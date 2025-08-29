"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import pad, to_channel_dimension_format
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, get_image_size, infer_channel_dimension_format, is_scaled_image,
make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, logging
logger = logging.get_logger(__name__)
class VitMatteImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = True, size_divisibility: int = 32, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_rescale = do_rescale
        self.do_normalize = do_normalize
        self.do_pad = do_pad
        self.rescale_factor = rescale_factor
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.size_divisibility = size_divisibility
    def pad_image(self, image: np.ndarray, size_divisibility: int = 32, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        height, width = get_image_size(image, input_data_format)
        pad_height = 0 if height % size_divisibility == 0 else size_divisibility - height % size_divisibility
        pad_width = 0 if width % size_divisibility == 0 else size_divisibility - width % size_divisibility
        if pad_width + pad_height > 0:
            padding = ((0, pad_height), (0, pad_width))
            image = pad(image, padding=padding, data_format=data_format, input_data_format=input_data_format)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_data_format)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, trimaps: ImageInput, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, size_divisibility: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_pad = do_pad if do_pad is not None else self.do_pad
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size_divisibility = size_divisibility if size_divisibility is not None else self.size_divisibility
        images = make_list_of_images(images)
        trimaps = make_list_of_images(trimaps, expected_ndims=2)
        if not valid_images(trimaps): raise ValueError("Invalid trimap type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_pad=do_pad, size_divisibility=size_divisibility)
        images = [to_numpy_array(image) for image in images]
        trimaps = [to_numpy_array(trimap) for trimap in trimaps]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_rescale:
            images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
            trimaps = [self.rescale(image=trimap, scale=rescale_factor, input_data_format=input_data_format) for trimap in trimaps]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        images = [np.concatenate([image, np.expand_dims(trimap, axis=-1)], axis=-1) for image, trimap in zip(images, trimaps)]
        if do_pad: images = [self.pad_image(image, size_divisibility=size_divisibility, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image=image, channel_dim=data_format, input_channel_dim=input_data_format) for image in images]
        data = {"pixel_values": images}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
