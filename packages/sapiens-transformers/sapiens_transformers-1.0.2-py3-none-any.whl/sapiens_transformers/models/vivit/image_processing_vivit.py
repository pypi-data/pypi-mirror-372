"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Union
import numpy as np
from sapiens_transformers.utils import is_vision_available
from sapiens_transformers.utils.generic import TensorType
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import (get_resize_output_image_size, rescale, resize, to_channel_dimension_format)
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format,
is_scaled_image, is_valid_image, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import filter_out_non_signature_kwargs, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def make_batched(videos) -> List[List[ImageInput]]:
    if isinstance(videos, (list, tuple)) and isinstance(videos[0], (list, tuple)) and is_valid_image(videos[0][0]): return videos
    elif isinstance(videos, (list, tuple)) and is_valid_image(videos[0]): return [videos]
    elif is_valid_image(videos): return [[videos]]
    raise ValueError(f"Could not make batched video from {videos}")
class VivitImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_center_crop: bool = True,
    crop_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 127.5, offset: bool = True, do_normalize: bool = True,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"shortest_edge": 256}
        size = get_size_dict(size, default_to_square=False)
        crop_size = crop_size if crop_size is not None else {"height": 224, "width": 224}
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        self.do_resize = do_resize
        self.size = size
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.offset = offset
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size, default_to_square=False)
        if "shortest_edge" in size: output_size = get_resize_output_image_size(image, size["shortest_edge"], default_to_square=False, input_data_format=input_data_format)
        elif "height" in size and "width" in size: output_size = (size["height"], size["width"])
        else: raise ValueError(f"Size must have 'height' and 'width' or 'shortest_edge' as keys. Got {size.keys()}")
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def rescale(self, image: np.ndarray, scale: Union[int, float], offset: bool = True, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs):
        rescaled_image = rescale(image, scale=scale, data_format=data_format, input_data_format=input_data_format, **kwargs)
        if offset: rescaled_image = rescaled_image - 1
        return rescaled_image
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, offset: bool = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        if offset and not do_rescale: raise ValueError("For offset, do_rescale must also be set to True.")
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        if do_center_crop: image = self.center_crop(image, size=crop_size, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, offset=offset, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, videos: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, offset: bool = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        resample = resample if resample is not None else self.resample
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        offset = offset if offset is not None else self.offset
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        crop_size = crop_size if crop_size is not None else self.crop_size
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        if not valid_images(videos): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        videos = make_batched(videos)
        videos = [[self._preprocess_image(image=img, do_resize=do_resize, size=size, resample=resample, do_center_crop=do_center_crop, crop_size=crop_size, do_rescale=do_rescale,
        rescale_factor=rescale_factor, offset=offset, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format)
        for img in video] for video in videos]
        data = {"pixel_values": videos}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
