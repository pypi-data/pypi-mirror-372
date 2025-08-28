"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
import random
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, is_scaled_image,
make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
FLAVA_IMAGE_MEAN = OPENAI_CLIP_MEAN
FLAVA_IMAGE_STD = OPENAI_CLIP_STD
FLAVA_CODEBOOK_MEAN = [0.0, 0.0, 0.0]
FLAVA_CODEBOOK_STD = [1.0, 1.0, 1.0]
LOGIT_LAPLACE_EPS: float = 0.1
class FlavaMaskingGenerator:
    def __init__(self, input_size: Union[int, Tuple[int, int]] = 14, total_mask_patches: int = 75, mask_group_max_patches: Optional[int] = None, mask_group_min_patches: int = 16,
    mask_group_min_aspect_ratio: Optional[float] = 0.3, mask_group_max_aspect_ratio: float = None):
        if not isinstance(input_size, tuple): input_size = (input_size,) * 2
        self.height, self.width = input_size
        self.num_patches = self.height * self.width
        self.total_mask_patches = total_mask_patches
        self.mask_group_min_patches = mask_group_min_patches
        self.mask_group_max_patches = total_mask_patches if mask_group_max_patches is None else mask_group_max_patches
        mask_group_max_aspect_ratio = mask_group_max_aspect_ratio or 1 / mask_group_min_aspect_ratio
        self.log_aspect_ratio = (math.log(mask_group_min_aspect_ratio), math.log(mask_group_max_aspect_ratio))
    def __repr__(self):
        repr_str = "MaskingGenerator(%d, %d -> [%d ~ %d], max = %d, %.3f ~ %.3f)" % (self.height, self.width, self.mask_group_min_patches, self.mask_group_max_patches,
        self.total_mask_patches, self.log_aspect_ratio[0], self.log_aspect_ratio[1])
        return repr_str
    def get_shape(self): return self.height, self.width
    def _mask(self, mask, max_mask_patches):
        delta = 0
        for _attempt in range(10):
            target_area = random.uniform(self.mask_group_min_patches, max_mask_patches)
            aspect_ratio = math.exp(random.uniform(*self.log_aspect_ratio))
            height = int(round(math.sqrt(target_area * aspect_ratio)))
            width = int(round(math.sqrt(target_area / aspect_ratio)))
            if width < self.width and height < self.height:
                top = random.randint(0, self.height - height)
                left = random.randint(0, self.width - width)
                num_masked = mask[top : top + height, left : left + width].sum()
                if 0 < height * width - num_masked <= max_mask_patches:
                    for i in range(top, top + height):
                        for j in range(left, left + width):
                            if mask[i, j] == 0:
                                mask[i, j] = 1
                                delta += 1
                if delta > 0: break
        return delta
    def __call__(self):
        mask = np.zeros(shape=self.get_shape(), dtype=int)
        mask_count = 0
        while mask_count < self.total_mask_patches:
            max_mask_patches = self.total_mask_patches - mask_count
            max_mask_patches = min(max_mask_patches, self.mask_group_max_patches)
            delta = self._mask(mask, max_mask_patches)
            if delta == 0: break
            else: mask_count += delta
        return mask
class FlavaImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BICUBIC, do_center_crop: bool = True,
    crop_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, Iterable[float]]] = None,
    image_std: Optional[Union[float, Iterable[float]]] = None, return_image_mask: bool = False, input_size_patches: int = 14, total_mask_patches: int = 75, mask_group_min_patches: int = 16,
    mask_group_max_patches: Optional[int] = None, mask_group_min_aspect_ratio: float = 0.3, mask_group_max_aspect_ratio: Optional[float] = None, return_codebook_pixels: bool = False,
    codebook_do_resize: bool = True, codebook_size: bool = None, codebook_resample: int = PILImageResampling.LANCZOS, codebook_do_center_crop: bool = True, codebook_crop_size: int = None,
    codebook_do_rescale: bool = True, codebook_rescale_factor: Union[int, float] = 1 / 255, codebook_do_map_pixels: bool = True, codebook_do_normalize: bool = True,
    codebook_image_mean: Optional[Union[float, Iterable[float]]] = None, codebook_image_std: Optional[Union[float, Iterable[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 224, "width": 224}
        size = get_size_dict(size)
        crop_size = crop_size if crop_size is not None else {"height": 224, "width": 224}
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        codebook_size = codebook_size if codebook_size is not None else {"height": 112, "width": 112}
        codebook_size = get_size_dict(codebook_size, param_name="codebook_size")
        codebook_crop_size = codebook_crop_size if codebook_crop_size is not None else {"height": 112, "width": 112}
        codebook_crop_size = get_size_dict(codebook_crop_size, param_name="codebook_crop_size")
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else FLAVA_IMAGE_MEAN
        self.image_std = image_std if image_std is not None else FLAVA_IMAGE_STD
        self.return_image_mask = return_image_mask
        self.input_size_patches = input_size_patches
        self.total_mask_patches = total_mask_patches
        self.mask_group_min_patches = mask_group_min_patches
        self.mask_group_max_patches = mask_group_max_patches
        self.mask_group_min_aspect_ratio = mask_group_min_aspect_ratio
        self.mask_group_max_aspect_ratio = mask_group_max_aspect_ratio
        self.return_codebook_pixels = return_codebook_pixels
        self.codebook_do_resize = codebook_do_resize
        self.codebook_size = codebook_size
        self.codebook_resample = codebook_resample
        self.codebook_do_center_crop = codebook_do_center_crop
        self.codebook_crop_size = codebook_crop_size
        self.codebook_do_rescale = codebook_do_rescale
        self.codebook_rescale_factor = codebook_rescale_factor
        self.codebook_do_map_pixels = codebook_do_map_pixels
        self.codebook_do_normalize = codebook_do_normalize
        self.codebook_image_mean = codebook_image_mean
        self.codebook_image_mean = codebook_image_mean if codebook_image_mean is not None else FLAVA_CODEBOOK_MEAN
        self.codebook_image_std = codebook_image_std if codebook_image_std is not None else FLAVA_CODEBOOK_STD
    @classmethod
    def from_dict(cls, image_processor_dict: Dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        if "codebook_size" in kwargs: image_processor_dict["codebook_size"] = kwargs.pop("codebook_size")
        if "codebook_crop_size" in kwargs: image_processor_dict["codebook_crop_size"] = kwargs.pop("codebook_crop_size")
        return super().from_dict(image_processor_dict, **kwargs)
    @lru_cache()
    def masking_generator(self, input_size_patches, total_mask_patches, mask_group_min_patches, mask_group_max_patches, mask_group_min_aspect_ratio, mask_group_max_aspect_ratio) -> FlavaMaskingGenerator:
        return FlavaMaskingGenerator(input_size=input_size_patches, total_mask_patches=total_mask_patches, mask_group_min_patches=mask_group_min_patches, mask_group_max_patches=mask_group_max_patches,
        mask_group_min_aspect_ratio=mask_group_min_aspect_ratio, mask_group_max_aspect_ratio=mask_group_max_aspect_ratio)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def map_pixels(self, image: np.ndarray) -> np.ndarray: return (1 - 2 * LOGIT_LAPLACE_EPS) * image + LOGIT_LAPLACE_EPS
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_map_pixels: bool = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[ChannelDimension] = None) -> np.ndarray:
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        if do_center_crop: image = self.center_crop(image=image, size=crop_size, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        if do_map_pixels: image = self.map_pixels(image)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: Optional[bool] = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: Optional[bool] = None,
    crop_size: Optional[Dict[str, int]] = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, return_image_mask: Optional[bool] = None,
    input_size_patches: Optional[int] = None, total_mask_patches: Optional[int] = None, mask_group_min_patches: Optional[int] = None, mask_group_max_patches: Optional[int] = None,
    mask_group_min_aspect_ratio: Optional[float] = None, mask_group_max_aspect_ratio: Optional[float] = None, return_codebook_pixels: Optional[bool] = None,
    codebook_do_resize: Optional[bool] = None, codebook_size: Optional[Dict[str, int]] = None, codebook_resample: Optional[int] = None, codebook_do_center_crop: Optional[bool] = None,
    codebook_crop_size: Optional[Dict[str, int]] = None, codebook_do_rescale: Optional[bool] = None, codebook_rescale_factor: Optional[float] = None,
    codebook_do_map_pixels: Optional[bool] = None, codebook_do_normalize: Optional[bool] = None, codebook_image_mean: Optional[Iterable[float]] = None,
    codebook_image_std: Optional[Iterable[float]] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        resample = resample if resample is not None else self.resample
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        crop_size = crop_size if crop_size is not None else self.crop_size
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        return_image_mask = return_image_mask if return_image_mask is not None else self.return_image_mask
        input_size_patches = input_size_patches if input_size_patches is not None else self.input_size_patches
        total_mask_patches = total_mask_patches if total_mask_patches is not None else self.total_mask_patches
        mask_group_min_patches = (mask_group_min_patches if mask_group_min_patches is not None else self.mask_group_min_patches)
        mask_group_max_patches = (mask_group_max_patches if mask_group_max_patches is not None else self.mask_group_max_patches)
        mask_group_min_aspect_ratio = (mask_group_min_aspect_ratio if mask_group_min_aspect_ratio is not None else self.mask_group_min_aspect_ratio)
        mask_group_max_aspect_ratio = (mask_group_max_aspect_ratio if mask_group_max_aspect_ratio is not None else self.mask_group_max_aspect_ratio)
        return_codebook_pixels = (return_codebook_pixels if return_codebook_pixels is not None else self.return_codebook_pixels)
        codebook_do_resize = codebook_do_resize if codebook_do_resize is not None else self.codebook_do_resize
        codebook_size = codebook_size if codebook_size is not None else self.codebook_size
        codebook_size = get_size_dict(codebook_size, param_name="codebook_size")
        codebook_resample = codebook_resample if codebook_resample is not None else self.codebook_resample
        codebook_do_rescale = codebook_do_rescale if codebook_do_rescale is not None else self.codebook_do_rescale
        codebook_rescale_factor = (codebook_rescale_factor if codebook_rescale_factor is not None else self.codebook_rescale_factor)
        codebook_do_center_crop = (codebook_do_center_crop if codebook_do_center_crop is not None else self.codebook_do_center_crop)
        codebook_crop_size = codebook_crop_size if codebook_crop_size is not None else self.codebook_crop_size
        codebook_crop_size = get_size_dict(codebook_crop_size, param_name="codebook_crop_size")
        codebook_do_map_pixels = (codebook_do_map_pixels if codebook_do_map_pixels is not None else self.codebook_do_map_pixels)
        codebook_do_normalize = (codebook_do_normalize if codebook_do_normalize is not None else self.codebook_do_normalize)
        codebook_image_mean = codebook_image_mean if codebook_image_mean is not None else self.codebook_image_mean
        codebook_image_std = codebook_image_std if codebook_image_std is not None else self.codebook_image_std
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        processed_images = [self._preprocess_image(image=img, do_resize=do_resize, size=size, resample=resample, do_center_crop=do_center_crop, crop_size=crop_size,
        do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_map_pixels=False,
        data_format=data_format, input_data_format=input_data_format) for img in images]
        data = {"pixel_values": processed_images}
        if return_codebook_pixels:
            codebook_images = [self._preprocess_image(image=img, do_resize=codebook_do_resize, size=codebook_size, resample=codebook_resample, do_center_crop=codebook_do_center_crop,
            crop_size=codebook_crop_size, do_rescale=codebook_do_rescale, rescale_factor=codebook_rescale_factor, do_normalize=codebook_do_normalize, image_mean=codebook_image_mean,
            image_std=codebook_image_std, do_map_pixels=codebook_do_map_pixels, data_format=data_format, input_data_format=input_data_format) for img in images]
            data["codebook_pixel_values"] = codebook_images
        if return_image_mask:
            mask_generator = self.masking_generator(input_size_patches=input_size_patches, total_mask_patches=total_mask_patches, mask_group_min_patches=mask_group_min_patches,
            mask_group_max_patches=mask_group_max_patches, mask_group_min_aspect_ratio=mask_group_min_aspect_ratio, mask_group_max_aspect_ratio=mask_group_max_aspect_ratio)
            masks = [mask_generator() for _ in images]
            data["bool_masked_pos"] = masks
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
