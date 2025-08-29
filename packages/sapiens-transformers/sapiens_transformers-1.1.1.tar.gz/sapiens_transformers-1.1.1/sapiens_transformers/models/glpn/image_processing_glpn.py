"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
import PIL.Image
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (ChannelDimension, PILImageResampling, get_image_size, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array,
valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, logging
logger = logging.get_logger(__name__)
class GLPNImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size_divisor: int = 32, resample=PILImageResampling.BILINEAR, do_rescale: bool = True, **kwargs) -> None:
        self.do_resize = do_resize
        self.do_rescale = do_rescale
        self.size_divisor = size_divisor
        self.resample = resample
        super().__init__(**kwargs)
    def resize(self, image: np.ndarray, size_divisor: int, resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[ChannelDimension] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        height, width = get_image_size(image, channel_dim=input_data_format)
        new_h = height // size_divisor * size_divisor
        new_w = width // size_divisor * size_divisor
        image = resize(image, (new_h, new_w), resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: Union["PIL.Image.Image", TensorType, List["PIL.Image.Image"], List[TensorType]], do_resize: Optional[bool] = None, size_divisor: Optional[int] = None,
    resample=None, do_rescale: Optional[bool] = None, return_tensors: Optional[Union[TensorType, str]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> BatchFeature:
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        size_divisor = size_divisor if size_divisor is not None else self.size_divisor
        resample = resample if resample is not None else self.resample
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_resize=do_resize, size=size_divisor, resample=resample)
        images = [to_numpy_array(img) for img in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image, size_divisor=size_divisor, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image, scale=1 / 255, input_data_format=input_data_format) for image in images]
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
