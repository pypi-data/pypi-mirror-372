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
from ...image_transforms import rescale, resize, to_channel_dimension_format
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array,
valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def squared_euclidean_distance(a, b):
    b = b.T
    a2 = np.sum(np.square(a), axis=1)
    b2 = np.sum(np.square(b), axis=0)
    ab = np.matmul(a, b)
    d = a2[:, None] - 2 * ab + b2[None, :]
    return d
def color_quantize(x, clusters):
    x = x.reshape(-1, 3)
    d = squared_euclidean_distance(x, clusters)
    return np.argmin(d, axis=1)
class ImageGPTImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, clusters: Optional[Union[List[List[int]], np.ndarray]] = None, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_normalize: bool = True, do_color_quantize: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 256, "width": 256}
        size = get_size_dict(size)
        self.clusters = np.array(clusters) if clusters is not None else None
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_normalize = do_normalize
        self.do_color_quantize = do_color_quantize
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def normalize(self, image: np.ndarray, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        image = rescale(image=image, scale=1 / 127.5, data_format=data_format, input_data_format=input_data_format)
        image = image - 1
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_normalize: bool = None,
    do_color_quantize: Optional[bool] = None, clusters: Optional[Union[List[List[int]], np.ndarray]] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: Optional[Union[str, ChannelDimension]] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        resample = resample if resample is not None else self.resample
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_color_quantize = do_color_quantize if do_color_quantize is not None else self.do_color_quantize
        clusters = clusters if clusters is not None else self.clusters
        clusters = np.array(clusters)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_resize=do_resize, size=size, resample=resample)
        if do_color_quantize and clusters is None: raise ValueError("Clusters must be specified if do_color_quantize is True.")
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_normalize: logger.warning_once("It looks like you are trying to rescale already rescaled images. If you wish to do this, make sure to set `do_normalize` to `False` and that pixel values are between [-1, 1].")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, input_data_format=input_data_format) for image in images]
        if do_color_quantize:
            images = [to_channel_dimension_format(image, ChannelDimension.LAST, input_data_format) for image in images]
            images = np.array(images)
            images = color_quantize(images, clusters).reshape(images.shape[:-1])
            batch_size = images.shape[0]
            images = images.reshape(batch_size, -1)
            images = list(images)
        else: images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        data = {"input_ids": images}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
