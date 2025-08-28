"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import PaddingMode, pad, resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, is_valid_image, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, is_vision_available, logging
logger = logging.get_logger(__name__)
if is_vision_available():
    import PIL
    from PIL import Image
def get_resize_output_image_size(image, size, input_data_format) -> Tuple[int, int]:
    height, width = get_image_size(image, channel_dim=input_data_format)
    min_len = size["shortest_edge"]
    max_len = size["longest_edge"]
    aspect_ratio = width / height
    if width >= height and width > max_len:
        width = max_len
        height = int(width / aspect_ratio)
    elif height > width and height > max_len:
        height = max_len
        width = int(height * aspect_ratio)
    height = max(height, min_len)
    width = max(width, min_len)
    return height, width
def make_list_of_images(images: ImageInput) -> List[List[np.ndarray]]:
    if is_valid_image(images): images = [[images]]
    elif isinstance(images, (list, tuple)) and len(images) > 0 and is_valid_image(images[0]): images = [images]
    elif (isinstance(images, (list, tuple)) and len(images) > 0 and isinstance(images[0], (list, tuple)) and is_valid_image(images[0][0])): pass
    else: raise ValueError("Invalid input type. Must be a single image, a list of images, or a list of batches of images.")
    return images
def max_across_indices(values: Iterable[Any]) -> List[Any]: return [max(values_i) for values_i in zip(*values)]
def get_max_height_width(images_list: List[List[np.ndarray]], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> List[int]:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(images_list[0][0])
    image_sizes = []
    for images in images_list:
        for image in images: image_sizes.append(get_image_size(image, channel_dim=input_data_format))
    max_height, max_width = max_across_indices(image_sizes)
    return (max_height, max_width)
def make_pixel_mask(image: np.ndarray, output_size: Tuple[int, int], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    input_height, input_width = get_image_size(image, channel_dim=input_data_format)
    mask = np.zeros(output_size, dtype=np.int64)
    mask[:input_height, :input_width] = 1
    return mask
def convert_to_rgb(image: ImageInput) -> ImageInput:
    if not isinstance(image, PIL.Image.Image): return image
    if image.mode == "RGB": return image
    image_rgba = image.convert("RGBA")
    background = Image.new("RGBA", image_rgba.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, image_rgba)
    alpha_composite = alpha_composite.convert("RGB")
    return alpha_composite
class Idefics2ImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_convert_rgb: bool = True, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_rescale: bool = True, rescale_factor: float = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = True, do_image_splitting: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_convert_rgb = do_convert_rgb
        self.do_resize = do_resize
        self.size = size if size is not None else {"shortest_edge": 378, "longest_edge": 980}
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
        self.do_image_splitting = do_image_splitting
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        if "shortest_edge" in size and "longest_edge" in size: size = get_resize_output_image_size(image, size, input_data_format)
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("size must be a dictionary with keys 'shortest_edge' and 'longest_edge' or 'height' and 'width'.")
        return resize(image, size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def _pad_image(self, image: np.ndarray, output_size: Tuple[int, int], constant_values: Union[float, Iterable[float]] = 0, data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
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
        batch_size = len(images)
        max_num_images = max(len(images_) for images_ in images)
        input_data_format = (infer_channel_dimension_format(images[0][0]) if input_data_format is None else input_data_format)
        data_format = input_data_format if data_format is None else data_format
        def empty_image(size, input_data_format):
            if input_data_format == ChannelDimension.FIRST: return np.zeros((3, *size), dtype=np.uint8)
            elif input_data_format == ChannelDimension.LAST: return np.zeros((*size, 3), dtype=np.uint8)
            raise ValueError("Invalid channel dimension format.")
        padded_images_list = [[empty_image(pad_size, data_format) for _ in range(max_num_images)] for _ in range(batch_size)]
        padded_masks = [[np.zeros(pad_size) for _ in range(max_num_images)] for _ in range(batch_size)]
        for batch_idx in range(batch_size):
            for sample_idx, image in enumerate(images[batch_idx]):
                padded_images_list[batch_idx][sample_idx] = self._pad_image(image, pad_size, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
                padded_masks[batch_idx][sample_idx] = make_pixel_mask(image, output_size=pad_size, input_data_format=input_data_format)
        padded_masks = padded_masks if return_pixel_mask else None
        return padded_images_list, padded_masks
    def _crop(self, im: np.ndarray, w1: int, h1: int, w2: int, h2: int, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        if input_data_format == ChannelDimension.FIRST: return im[:, h1:h2, w1:w2]
        elif input_data_format == ChannelDimension.LAST: return im[h1:h2, w1:w2, :]
    def split_image(self, image: np.ndarray, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        height, width = get_image_size(image, input_data_format)
        mid_width = width // 2
        mid_height = height // 2
        return [self._crop(image, 0, 0, mid_width, mid_height, input_data_format), self._crop(image, mid_width, 0, width, mid_height, input_data_format),
        self._crop(image, 0, mid_height, mid_width, height, input_data_format), self._crop(image, mid_width, mid_height, width, height, input_data_format), image]
    def preprocess(self, images: ImageInput, do_convert_rgb: Optional[bool] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = None,
    do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, do_image_splitting: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    input_data_format: Optional[ChannelDimension] = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_pad = do_pad if do_pad is not None else self.do_pad
        do_image_splitting = do_image_splitting if do_image_splitting is not None else self.do_image_splitting
        images_list = make_list_of_images(images)
        if not valid_images(images_list[0]): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        if do_convert_rgb: images_list = [[convert_to_rgb(image) for image in images] for images in images_list]
        images_list = [[to_numpy_array(image) for image in images] for images in images_list]
        if is_scaled_image(images_list[0][0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images_list[0][0])
        if do_image_splitting:
            new_images_list = []
            for images in images_list:
                new_images = []
                for image in images: new_images.extend(self.split_image(image, input_data_format))
                new_images_list.append(new_images)
            images_list = new_images_list
        if do_resize: images_list = [[self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images] for images in images_list]
        if do_rescale: images_list = [[self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images] for images in images_list]
        if do_normalize: images_list = [[self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images] for images in images_list]
        pixel_attention_mask = None
        if do_pad: images_list, pixel_attention_mask = self.pad(images_list, return_pixel_mask=True, return_tensors=return_tensors, input_data_format=input_data_format)
        if data_format is not None: images_list = [[to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images] for images in images_list]
        data = {"pixel_values": np.array(images_list) if do_pad else images_list}
        if pixel_attention_mask is not None: data["pixel_attention_mask"] = np.array(pixel_attention_mask) if do_pad else pixel_attention_mask
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
