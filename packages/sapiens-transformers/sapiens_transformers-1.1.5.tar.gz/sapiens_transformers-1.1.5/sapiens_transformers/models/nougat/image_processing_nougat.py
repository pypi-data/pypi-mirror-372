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
from ...image_transforms import (get_resize_output_image_size, pad, resize, to_channel_dimension_format, to_pil_image)
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, logging
from ...utils.import_utils import is_cv2_available, is_vision_available
logger = logging.get_logger(__name__)
if is_cv2_available(): pass
if is_vision_available(): import PIL
class NougatImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_crop_margin: bool = True, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_thumbnail: bool = True, do_align_long_axis: bool = False, do_pad: bool = True, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255,
    do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 896, "width": 672}
        size = get_size_dict(size)
        self.do_crop_margin = do_crop_margin
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_thumbnail = do_thumbnail
        self.do_align_long_axis = do_align_long_axis
        self.do_pad = do_pad
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
    def python_find_non_zero(self, image: np.array):
        non_zero_indices = np.column_stack(np.nonzero(image))
        idxvec = non_zero_indices[:, [1, 0]]
        idxvec = idxvec.reshape(-1, 1, 2)
        return idxvec
    def python_bounding_rect(self, coordinates):
        min_values = np.min(coordinates, axis=(0, 1)).astype(int)
        max_values = np.max(coordinates, axis=(0, 1)).astype(int)
        x_min, y_min = min_values[0], min_values[1]
        width = max_values[0] - x_min + 1
        height = max_values[1] - y_min + 1
        return x_min, y_min, width, height
    def crop_margin(self, image: np.array, gray_threshold: int = 200, data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.array:
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        image = to_pil_image(image, input_data_format=input_data_format)
        data = np.array(image.convert("L")).astype(np.uint8)
        max_val = data.max()
        min_val = data.min()
        if max_val == min_val:
            image = np.array(image)
            image = (to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image)
            return image
        data = (data - min_val) / (max_val - min_val) * 255
        gray = data < gray_threshold
        coords = self.python_find_non_zero(gray)
        x_min, y_min, width, height = self.python_bounding_rect(coords)
        image = image.crop((x_min, y_min, x_min + width, y_min + height))
        image = np.array(image).astype(np.uint8)
        image = to_channel_dimension_format(image, input_data_format, ChannelDimension.LAST)
        image = (to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image)
        return image
    def align_long_axis(self, image: np.ndarray, size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        output_height, output_width = size["height"], size["width"]
        if (output_width < output_height and input_width > input_height) or (output_width > output_height and input_width < input_height): image = np.rot90(image, 3)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    def pad_image(self, image: np.ndarray, size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        output_height, output_width = size["height"], size["width"]
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        delta_width = output_width - input_width
        delta_height = output_height - input_height
        pad_top = delta_height // 2
        pad_left = delta_width // 2
        pad_bottom = delta_height - pad_top
        pad_right = delta_width - pad_left
        padding = ((pad_top, pad_bottom), (pad_left, pad_right))
        return pad(image, padding, data_format=data_format, input_data_format=input_data_format)
    def thumbnail(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        output_height, output_width = size["height"], size["width"]
        height = min(input_height, output_height)
        width = min(input_width, output_width)
        if height == input_height and width == input_width: return image
        if input_height > input_width: width = int(input_width * height / input_height)
        elif input_width > input_height: height = int(input_height * width / input_width)
        return resize(image, size=(height, width), resample=resample, reducing_gap=2.0, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        shortest_edge = min(size["height"], size["width"])
        output_size = get_resize_output_image_size(image, size=shortest_edge, default_to_square=False, input_data_format=input_data_format)
        resized_image = resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
        return resized_image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_crop_margin: bool = None, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_thumbnail: bool = None, do_align_long_axis: bool = None, do_pad: bool = None, do_rescale: bool = None, rescale_factor: Union[int, float] = None,
    do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_crop_margin = do_crop_margin if do_crop_margin is not None else self.do_crop_margin
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_thumbnail = do_thumbnail if do_thumbnail is not None else self.do_thumbnail
        do_align_long_axis = do_align_long_axis if do_align_long_axis is not None else self.do_align_long_axis
        do_pad = do_pad if do_pad is not None else self.do_pad
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_pad=do_pad, size_divisibility=size, do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_crop_margin: images = [self.crop_margin(image, input_data_format=input_data_format) for image in images]
        if do_align_long_axis: images = [self.align_long_axis(image, size=size, input_data_format=input_data_format) for image in images]
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_thumbnail: images = [self.thumbnail(image=image, size=size, input_data_format=input_data_format) for image in images]
        if do_pad: images = [self.pad_image(image=image, size=size, input_data_format=input_data_format) for image in images]
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
