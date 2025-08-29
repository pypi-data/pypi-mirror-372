"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import center_crop, resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
class PerceiverImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_center_crop: bool = True, crop_size: Dict[str, int] = None, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BICUBIC,
    do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        crop_size = crop_size if crop_size is not None else {"height": 256, "width": 256}
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        size = size if size is not None else {"height": 224, "width": 224}
        size = get_size_dict(size)
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
    def center_crop(self, image: np.ndarray, crop_size: Dict[str, int], size: Optional[int] = None, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = self.size if size is None else size
        size = get_size_dict(size)
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        height, width = get_image_size(image, channel_dim=input_data_format)
        min_dim = min(height, width)
        cropped_height = (size["height"] / crop_size["height"]) * min_dim
        cropped_width = (size["width"] / crop_size["width"]) * min_dim
        return center_crop(image, size=(cropped_height, cropped_width), data_format=data_format, input_data_format=input_data_format, **kwargs)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_center_crop: Optional[bool] = None, crop_size: Optional[Dict[str, int]] = None, do_resize: Optional[bool] = None,
    size: Optional[Dict[str, int]] = None, resample: PILImageResampling = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None,
    do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        crop_size = crop_size if crop_size is not None else self.crop_size
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_center_crop: images = [self.center_crop(image, crop_size, size=size, input_data_format=input_data_format) for image in images]
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
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
