"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import (PaddingMode, flip_channel_order, pad, resize, to_channel_dimension_format)
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, is_valid_image,
to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def make_batched(videos) -> List[List[ImageInput]]:
    if isinstance(videos, (list, tuple)) and isinstance(videos[0], (list, tuple)) and is_valid_image(videos[0][0]): return videos
    elif isinstance(videos, (list, tuple)) and is_valid_image(videos[0]): return [videos]
    elif is_valid_image(videos): return [[videos]]
    raise ValueError(f"Could not make batched video from {videos}")
def get_resize_output_image_size(input_image: np.ndarray, max_size: int = 448, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    height, width = get_image_size(input_image, input_data_format)
    if height >= width:
        ratio = width * 1.0 / height
        new_height = max_size
        new_width = new_height * ratio
    else:
        ratio = height * 1.0 / width
        new_width = max_size
        new_height = new_width * ratio
    size = (int(new_height), int(new_width))
    return size
class TvpImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_center_crop: bool = True,
    crop_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_pad: bool = True, pad_size: Dict[str, int] = None,
    constant_values: Union[float, Iterable[float]] = 0, pad_mode: PaddingMode = PaddingMode.CONSTANT, do_normalize: bool = True, do_flip_channel_order: bool = True,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"longest_edge": 448}
        crop_size = crop_size if crop_size is not None else {"height": 448, "width": 448}
        pad_size = pad_size if pad_size is not None else {"height": 448, "width": 448}
        self.do_resize = do_resize
        self.size = size
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_pad = do_pad
        self.pad_size = pad_size
        self.constant_values = constant_values
        self.pad_mode = pad_mode
        self.do_normalize = do_normalize
        self.do_flip_channel_order = do_flip_channel_order
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size, default_to_square=False)
        if "height" in size and "width" in size: output_size = (size["height"], size["width"])
        elif "longest_edge" in size: output_size = get_resize_output_image_size(image, size["longest_edge"], input_data_format)
        else: raise ValueError(f"Size must have 'height' and 'width' or 'longest_edge' as keys. Got {size.keys()}")
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def pad_image(self, image: np.ndarray, pad_size: Dict[str, int] = None, constant_values: Union[float, Iterable[float]] = 0, pad_mode: PaddingMode = PaddingMode.CONSTANT,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs):
        height, width = get_image_size(image, channel_dim=input_data_format)
        max_height = pad_size.get("height", height)
        max_width = pad_size.get("width", width)
        pad_right, pad_bottom = max_width - width, max_height - height
        if pad_right < 0 or pad_bottom < 0: raise ValueError("The padding size must be greater than image size")
        padding = ((0, pad_bottom), (0, pad_right))
        padded_image = pad(image, padding, mode=pad_mode, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
        return padded_image
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, do_pad: bool = True, pad_size: Dict[str, int] = None, constant_values: Union[float, Iterable[float]] = None,
    pad_mode: PaddingMode = None, do_normalize: bool = None, do_flip_channel_order: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_pad=do_pad, size_divisibility=pad_size, do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        image = to_numpy_array(image)
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        if do_center_crop: image = self.center_crop(image, size=crop_size, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image=image.astype(np.float32), mean=image_mean, std=image_std, input_data_format=input_data_format)
        if do_pad: image = self.pad_image(image=image, pad_size=pad_size, constant_values=constant_values, pad_mode=pad_mode, input_data_format=input_data_format)
        if do_flip_channel_order: image = flip_channel_order(image=image, input_data_format=input_data_format)
        image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, videos: Union[ImageInput, List[ImageInput], List[List[ImageInput]]], do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_center_crop: bool = None, crop_size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, do_pad: bool = None, pad_size: Dict[str, int] = None,
    constant_values: Union[float, Iterable[float]] = None, pad_mode: PaddingMode = None, do_normalize: bool = None, do_flip_channel_order: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        resample = resample if resample is not None else self.resample
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_pad = do_pad if do_pad is not None else self.do_pad
        pad_size = pad_size if pad_size is not None else self.pad_size
        constant_values = constant_values if constant_values is not None else self.constant_values
        pad_mode = pad_mode if pad_mode else self.pad_mode
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_flip_channel_order = (do_flip_channel_order if do_flip_channel_order is not None else self.do_flip_channel_order)
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        crop_size = crop_size if crop_size is not None else self.crop_size
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        if not valid_images(videos): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        videos = make_batched(videos)
        videos = [np.array([self._preprocess_image(image=img, do_resize=do_resize, size=size, resample=resample, do_center_crop=do_center_crop, crop_size=crop_size,
        do_rescale=do_rescale, rescale_factor=rescale_factor, do_pad=do_pad, pad_size=pad_size, constant_values=constant_values, pad_mode=pad_mode, do_normalize=do_normalize,
        do_flip_channel_order=do_flip_channel_order, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format)
        for img in video]) for video in videos]
        data = {"pixel_values": videos}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
