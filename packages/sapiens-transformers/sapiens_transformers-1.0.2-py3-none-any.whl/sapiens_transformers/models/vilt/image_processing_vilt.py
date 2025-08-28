"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import PaddingMode, pad, resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def max_across_indices(values: Iterable[Any]) -> List[Any]: return [max(values_i) for values_i in zip(*values)]
def make_pixel_mask(image: np.ndarray, output_size: Tuple[int, int], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    input_height, input_width = get_image_size(image, channel_dim=input_data_format)
    mask = np.zeros(output_size, dtype=np.int64)
    mask[:input_height, :input_width] = 1
    return mask
def get_max_height_width(images: List[np.ndarray], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> List[int]:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
    if input_data_format == ChannelDimension.FIRST: _, max_height, max_width = max_across_indices([img.shape for img in images])
    elif input_data_format == ChannelDimension.LAST: max_height, max_width, _ = max_across_indices([img.shape for img in images])
    else: raise ValueError(f"Invalid channel dimension format: {input_data_format}")
    return (max_height, max_width)
def get_resize_output_image_size(input_image: np.ndarray, shorter: int = 800, longer: int = 1333, size_divisor: int = 32, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    input_height, input_width = get_image_size(input_image, input_data_format)
    min_size, max_size = shorter, longer
    scale = min_size / min(input_height, input_width)
    if input_height < input_width:
        new_height = min_size
        new_width = scale * input_width
    else:
        new_height = scale * input_height
        new_width = min_size
    if max(new_height, new_width) > max_size:
        scale = max_size / max(new_height, new_width)
        new_height = scale * new_height
        new_width = scale * new_width
    new_height, new_width = int(new_height + 0.5), int(new_width + 0.5)
    new_height = new_height // size_divisor * size_divisor
    new_width = new_width // size_divisor * size_divisor
    return new_height, new_width
class ViltImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, size_divisor: int = 32, resample: PILImageResampling = PILImageResampling.BICUBIC, do_rescale: bool = True,
    rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = True, **kwargs) -> None:
        if "pad_and_return_pixel_mask" in kwargs: do_pad = kwargs.pop("pad_and_return_pixel_mask")
        super().__init__(**kwargs)
        size = size if size is not None else {"shortest_edge": 384}
        size = get_size_dict(size, default_to_square=False)
        self.do_resize = do_resize
        self.size = size
        self.size_divisor = size_divisor
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
    @classmethod
    def from_dict(cls, image_processor_dict: Dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        if "pad_and_return_pixel_mask" in kwargs: image_processor_dict["pad_and_return_pixel_mask"] = kwargs.pop("pad_and_return_pixel_mask")
        return super().from_dict(image_processor_dict, **kwargs)
    def resize(self, image: np.ndarray, size: Dict[str, int], size_divisor: int = 32, resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size, default_to_square=False)
        if "shortest_edge" not in size: raise ValueError(f"The `size` dictionary must contain the key `shortest_edge`. Got {size.keys()}")
        shorter = size["shortest_edge"]
        longer = int(1333 / 800 * shorter)
        output_size = get_resize_output_image_size(image, shorter=shorter, longer=longer, size_divisor=size_divisor, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def _pad_image(self, image: np.ndarray, output_size: Tuple[int, int], constant_values: Union[float, Iterable[float]] = 0, data_format: Optional[ChannelDimension] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        output_height, output_width = output_size
        pad_bottom = output_height - input_height
        pad_right = output_width - input_width
        padding = ((0, pad_bottom), (0, pad_right))
        padded_image = pad(image, padding, mode=PaddingMode.CONSTANT, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
        return padded_image
    def pad(self, images: List[np.ndarray], constant_values: Union[float, Iterable[float]] = 0, return_pixel_mask: bool = True, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> BatchFeature:
        pad_size = get_max_height_width(images, input_data_format=input_data_format)
        padded_images = [self._pad_image(image, pad_size, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format) for image in images]
        data = {"pixel_values": padded_images}
        if return_pixel_mask:
            masks = [make_pixel_mask(image=image, output_size=pad_size, input_data_format=input_data_format) for image in images]
            data["pixel_mask"] = masks
        return BatchFeature(data=data, tensor_type=return_tensors)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, size_divisor: Optional[int] = None, resample: PILImageResampling = None,
    do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: ChannelDimension = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size_divisor = size_divisor if size_divisor is not None else self.size_divisor
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image=image, size=size, size_divisor=size_divisor, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        if do_pad: encoded_outputs = self.pad(images, return_pixel_mask=True, return_tensors=return_tensors, input_data_format=data_format)
        else: encoded_outputs = BatchFeature(data={"pixel_values": images}, tensor_type=return_tensors)
        return encoded_outputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
