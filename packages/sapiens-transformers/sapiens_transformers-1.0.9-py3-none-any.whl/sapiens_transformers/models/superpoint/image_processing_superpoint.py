"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, Optional, Union
import numpy as np
from ... import is_vision_available
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (ChannelDimension, ImageInput, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array, valid_images)
from ...utils import TensorType, logging, requires_backends
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def is_grayscale(image: ImageInput, input_data_format: Optional[Union[str, ChannelDimension]] = None):
    if input_data_format == ChannelDimension.FIRST: return np.all(image[0, ...] == image[1, ...]) and np.all(image[1, ...] == image[2, ...])
    elif input_data_format == ChannelDimension.LAST: return np.all(image[..., 0] == image[..., 1]) and np.all(image[..., 1] == image[..., 2])
def convert_to_grayscale(image: ImageInput, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> ImageInput:
    requires_backends(convert_to_grayscale, ["vision"])
    if isinstance(image, np.ndarray):
        if input_data_format == ChannelDimension.FIRST:
            gray_image = image[0, ...] * 0.2989 + image[1, ...] * 0.5870 + image[2, ...] * 0.1140
            gray_image = np.stack([gray_image] * 3, axis=0)
        elif input_data_format == ChannelDimension.LAST:
            gray_image = image[..., 0] * 0.2989 + image[..., 1] * 0.5870 + image[..., 2] * 0.1140
            gray_image = np.stack([gray_image] * 3, axis=-1)
        return gray_image
    if not isinstance(image, PIL.Image.Image): return image
    image = image.convert("L")
    return image
class SuperPointImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: float = 1 / 255, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 480, "width": 640}
        size = get_size_dict(size, default_to_square=False)
        self.do_resize = do_resize
        self.size = size
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
    def resize(self, image: np.ndarray, size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs):
        size = get_size_dict(size, default_to_square=False)
        return resize(image, size=(size["height"], size["width"]), data_format=data_format, input_data_format=input_data_format, **kwargs)
    def preprocess(self, images, do_resize: bool = None, size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: ChannelDimension = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> BatchFeature:
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if do_resize and size is None: raise ValueError("Size must be specified if do_resize is True.")
        if do_rescale and rescale_factor is None: raise ValueError("Rescale factor must be specified if do_rescale is True.")
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image=image, size=size, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        for i in range(len(images)):
            if not is_grayscale(images[i], input_data_format): images[i] = convert_to_grayscale(images[i], input_data_format=input_data_format)
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        data = {"pixel_values": images}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
