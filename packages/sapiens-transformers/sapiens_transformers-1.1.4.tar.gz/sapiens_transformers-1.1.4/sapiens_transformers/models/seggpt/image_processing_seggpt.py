"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images)
from ...utils import TensorType, is_torch_available, is_vision_available, logging, requires_backends
if is_torch_available(): import torch
if is_vision_available(): pass
logger = logging.get_logger(__name__)
def build_palette(num_labels: int) -> List[Tuple[int, int]]:
    base = int(num_labels ** (1 / 3)) + 1
    margin = 256 // base
    color_list = [(0, 0, 0)]
    for location in range(num_labels):
        num_seq_r = location // base**2
        num_seq_g = (location % base**2) // base
        num_seq_b = location % base
        R = 255 - num_seq_r * margin
        G = 255 - num_seq_g * margin
        B = 255 - num_seq_b * margin
        color_list.append((R, G, B))
    return color_list
def mask_to_rgb(mask: np.ndarray, palette: Optional[List[Tuple[int, int]]] = None, data_format: Optional[ChannelDimension] = None) -> np.ndarray:
    data_format = data_format if data_format is not None else ChannelDimension.FIRST
    if palette is not None:
        height, width = mask.shape
        rgb_mask = np.zeros((3, height, width), dtype=np.uint8)
        classes_in_mask = np.unique(mask)
        for class_idx in classes_in_mask:
            rgb_value = palette[class_idx]
            class_mask = (mask == class_idx).astype(np.uint8)
            class_mask = np.expand_dims(class_mask, axis=-1)
            class_rgb_mask = class_mask * np.array(rgb_value)
            class_rgb_mask = np.moveaxis(class_rgb_mask, -1, 0)
            rgb_mask += class_rgb_mask.astype(np.uint8)
        rgb_mask = np.clip(rgb_mask, 0, 255).astype(np.uint8)
    else: rgb_mask = np.repeat(mask[None, ...], 3, axis=0)
    return to_channel_dimension_format(rgb_mask, data_format)
class SegGptImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = PILImageResampling.BICUBIC, do_rescale: bool = True,
    rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_convert_rgb: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 448, "width": 448}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.do_rescale = do_rescale
        self.do_normalize = do_normalize
        self.size = size
        self.resample = resample
        self.rescale_factor = rescale_factor
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.do_convert_rgb = do_convert_rgb
    def get_palette(self, num_labels: int) -> List[Tuple[int, int]]: return build_palette(num_labels)
    def mask_to_rgb(self, image: np.ndarray, palette: Optional[List[Tuple[int, int]]] = None, data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray: return mask_to_rgb(image, palette=palette, data_format=data_format)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def _preprocess_step(self, images: ImageInput, do_resize: Optional[bool] = None, size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None,
    do_convert_rgb: Optional[bool] = None, num_labels: Optional[int] = None, **kwargs):
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        resample = resample if resample is not None else self.resample
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        size_dict = get_size_dict(size)
        images = make_list_of_images(images, expected_ndims=2 if do_convert_rgb else 3)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if do_resize and size is None: raise ValueError("Size must be specified if do_resize is True.")
        if do_rescale and rescale_factor is None: raise ValueError("Rescale factor must be specified if do_rescale is True.")
        if do_normalize and (image_mean is None or image_std is None): raise ValueError("Image mean and std must be specified if do_normalize is True.")
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None and not do_convert_rgb: input_data_format = infer_channel_dimension_format(images[0])
        if do_convert_rgb:
            palette = self.get_palette(num_labels) if num_labels is not None else None
            images = [self.mask_to_rgb(image=image, palette=palette, data_format=ChannelDimension.FIRST) for image in images]
            input_data_format = ChannelDimension.FIRST
        if do_resize: images = [self.resize(image=image, size=size_dict, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        return images
    def preprocess(self, images: Optional[ImageInput] = None, prompt_images: Optional[ImageInput] = None, prompt_masks: Optional[ImageInput] = None, do_resize: Optional[bool] = None,
    size: Dict[str, int] = None, resample: PILImageResampling = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: Optional[bool] = None, num_labels: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs):
        if all(v is None for v in [images, prompt_images, prompt_masks]): raise ValueError("At least one of images, prompt_images, prompt_masks must be specified.")
        data = {}
        if images is not None:
            images = self._preprocess_step(images, is_mask=False, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
            do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_convert_rgb=False, data_format=data_format, input_data_format=input_data_format, **kwargs)
            data["pixel_values"] = images
        if prompt_images is not None:
            prompt_images = self._preprocess_step(prompt_images, is_mask=False, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
            do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_convert_rgb=False, data_format=data_format, input_data_format=input_data_format, **kwargs)
            data["prompt_pixel_values"] = prompt_images
        if prompt_masks is not None:
            prompt_masks = self._preprocess_step(prompt_masks, do_resize=do_resize, size=size, resample=PILImageResampling.NEAREST, do_rescale=do_rescale, rescale_factor=rescale_factor,
            do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_convert_rgb=do_convert_rgb, num_labels=num_labels, data_format=data_format,
            input_data_format=input_data_format, **kwargs)
            data["prompt_masks"] = prompt_masks
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_semantic_segmentation(self, outputs, target_sizes: Optional[List[Tuple[int, int]]] = None, num_labels: Optional[int] = None):
        requires_backends(self, ["torch"])
        masks = outputs.pred_masks
        masks = masks[:, :, masks.shape[2] // 2 :, :]
        std = torch.tensor(self.image_std).to(masks.device)
        mean = torch.tensor(self.image_mean).to(masks.device)
        masks = masks.permute(0, 2, 3, 1) * std + mean
        masks = masks.permute(0, 3, 1, 2)
        masks = torch.clip(masks * 255, 0, 255)
        semantic_segmentation = []
        palette_tensor = None
        palette = self.get_palette(num_labels) if num_labels is not None else None
        if palette is not None:
            palette_tensor = torch.tensor(palette).float().to(masks.device)
            _, num_channels, _, _ = masks.shape
            palette_tensor = palette_tensor.view(1, 1, num_labels + 1, num_channels)
        for idx, mask in enumerate(masks):
            if target_sizes is not None: mask = torch.nn.functional.interpolate(mask.unsqueeze(0), size=target_sizes[idx], mode="nearest")[0]
            if num_labels is not None:
                channels, height, width = mask.shape
                dist = mask.permute(1, 2, 0).view(height, width, 1, channels)
                dist = dist - palette_tensor
                dist = torch.pow(dist, 2)
                dist = torch.sum(dist, dim=-1)
                pred = dist.argmin(dim=-1)
            else: pred = mask.mean(dim=0).int()
            semantic_segmentation.append(pred)
        return semantic_segmentation
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
