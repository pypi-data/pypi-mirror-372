"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import get_image_size, pad, to_channel_dimension_format
from ...image_utils import (ChannelDimension, ImageInput, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, logging
logger = logging.get_logger(__name__)
class Swin2SRImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_pad: bool = True, pad_size: int = 8, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_pad = do_pad
        self.pad_size = pad_size
    def pad(self, image: np.ndarray, size: int, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        old_height, old_width = get_image_size(image, input_data_format)
        pad_height = (old_height // size + 1) * size - old_height
        pad_width = (old_width // size + 1) * size - old_width
        return pad(image, ((0, pad_height), (0, pad_width)), mode="symmetric", data_format=data_format, input_data_format=input_data_format)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_pad: Optional[bool] = None, pad_size: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_pad = do_pad if do_pad is not None else self.do_pad
        pad_size = pad_size if pad_size is not None else self.pad_size
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_pad=do_pad, size_divisibility=pad_size)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_pad: images = [self.pad(image, size=pad_size, input_data_format=input_data_format) for image in images]
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
