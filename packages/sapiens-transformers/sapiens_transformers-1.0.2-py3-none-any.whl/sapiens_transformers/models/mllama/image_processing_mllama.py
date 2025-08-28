"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import (PaddingMode, get_image_size, pad, resize)
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format,
is_valid_image, is_vision_available, to_numpy_array, validate_preprocess_arguments)
from ...utils import TensorType, logging
if is_vision_available():
    import PIL
    from PIL import Image
logger = logging.get_logger(__name__)
@lru_cache(maxsize=10)
def get_all_supported_aspect_ratios(max_image_tiles: int) -> List[Tuple[int, int]]:
    aspect_ratios = []
    for width in range(1, max_image_tiles + 1):
        for height in range(1, max_image_tiles + 1):
            if width * height <= max_image_tiles: aspect_ratios.append((width, height))
    return aspect_ratios
def get_image_size_fit_to_canvas(image_height: int, image_width: int, canvas_height: int, canvas_width: int, tile_size: int) -> Tuple[int, int]:
    target_width = np.clip(image_width, tile_size, canvas_width)
    target_height = np.clip(image_height, tile_size, canvas_height)
    scale_h = target_height / image_height
    scale_w = target_width / image_width
    if scale_w < scale_h:
        new_width = target_width
        new_height = min(math.floor(image_height * scale_w), target_height)
    else:
        new_height = target_height
        new_width = min(math.floor(image_width * scale_h), target_width)
    return new_height, new_width
@lru_cache(maxsize=100)
def get_optimal_tiled_canvas(image_height: int, image_width: int, max_image_tiles: int, tile_size: int) -> Tuple[int, int]:
    possible_tile_arrangements = get_all_supported_aspect_ratios(max_image_tiles)
    possible_canvas_sizes = np.array(possible_tile_arrangements) * tile_size
    target_heights, target_widths = np.array(possible_canvas_sizes).T
    scale_h = target_heights / image_height
    scale_w = target_widths / image_width
    scales = np.where(scale_w > scale_h, scale_h, scale_w)
    upscaling_options = scales[scales >= 1]
    if len(upscaling_options) > 0: selected_scale = np.min(upscaling_options)
    else:
        downscaling_options = scales[scales < 1]
        selected_scale = np.max(downscaling_options)
    chosen_canvas = possible_canvas_sizes[scales == selected_scale]
    if len(chosen_canvas) > 1:
        areas = chosen_canvas[:, 0] * chosen_canvas[:, 1]
        optimal_idx = np.argmin(areas)
        optimal_canvas = chosen_canvas[optimal_idx]
    else: optimal_canvas = chosen_canvas[0]
    return optimal_canvas
def split_to_tiles(image: np.ndarray, num_tiles_height: int, num_tiles_width: int) -> np.ndarray:
    num_channels, height, width = image.shape
    tile_height = height // num_tiles_height
    tile_width = width // num_tiles_width
    image = image.reshape(num_channels, num_tiles_height, tile_height, num_tiles_width, tile_width)
    image = image.transpose(1, 3, 0, 2, 4)
    image = image.reshape(num_tiles_width * num_tiles_height, num_channels, tile_height, tile_width)
    return np.ascontiguousarray(image)
def build_aspect_ratio_mask(aspect_ratios: List[List[Tuple[int, int]]], max_image_tiles: int) -> np.ndarray:
    batch_size = len(aspect_ratios)
    max_num_images = max([len(row) for row in aspect_ratios])
    aspect_ratio_mask = np.zeros((batch_size, max_num_images, max_image_tiles), dtype=np.int64)
    aspect_ratio_mask[:, :, 0] = 1
    for i, sample_aspect_ratios in enumerate(aspect_ratios):
        for j, (num_tiles_w, num_tiles_h) in enumerate(sample_aspect_ratios): aspect_ratio_mask[i, j, : num_tiles_w * num_tiles_h] = 1
    return aspect_ratio_mask
def pack_images(batch_images: List[List[np.ndarray]], max_image_tiles: int) -> Tuple[np.ndarray, List[List[int]]]:
    batch_size = len(batch_images)
    max_num_images = max([len(images) for images in batch_images])
    shapes = [image.shape for images in batch_images for image in images]
    _, channels, tile_height, tile_width = shapes[0]
    stacked_images = np.zeros((batch_size, max_num_images, max_image_tiles, channels, tile_height, tile_width), dtype=np.float32)
    all_num_tiles = []
    for i, images in enumerate(batch_images):
        num_sample_tiles = []
        for j, image in enumerate(images):
            num_tiles = image.shape[0]
            stacked_images[i, j, :num_tiles] = image
            num_sample_tiles.append(num_tiles)
        all_num_tiles.append(num_sample_tiles)
    return stacked_images, all_num_tiles
def pack_aspect_ratios(aspect_ratios: List[List[Tuple[int, int]]], pad_value: int = 1) -> np.ndarray:
    batch_size = len(aspect_ratios)
    max_num_images = max([len(row) for row in aspect_ratios])
    aspect_ratios_stacked = np.full((batch_size, max_num_images, 2), pad_value, dtype=np.int64)
    for i, row in enumerate(aspect_ratios):
        if len(row) > 0: aspect_ratios_stacked[i, : len(row)] = np.array(row)
    return aspect_ratios_stacked
def convert_aspect_ratios_to_ids(aspect_ratios: List[List[Tuple[int, int]]], max_image_tiles: int) -> np.ndarray:
    batch_size = len(aspect_ratios)
    max_num_images = max([len(row) for row in aspect_ratios])
    supported_aspect_ratios = get_all_supported_aspect_ratios(max_image_tiles)
    aspect_ratios_ids = np.zeros((batch_size, max_num_images), dtype=np.int64)
    for i, sample_aspect_ratios in enumerate(aspect_ratios):
        for j, (num_tiles_h, num_tiles_w) in enumerate(sample_aspect_ratios): aspect_ratios_ids[i, j] = supported_aspect_ratios.index((num_tiles_h, num_tiles_w)) + 1
    return aspect_ratios_ids
def to_channel_dimension_format(image: np.ndarray, channel_dim: Union[ChannelDimension, str], input_channel_dim: Optional[Union[ChannelDimension, str]] = None) -> np.ndarray:
    if not isinstance(image, np.ndarray): raise ValueError(f"Input image must be of type np.ndarray, got {type(image)}")
    if input_channel_dim is None: input_channel_dim = infer_channel_dimension_format(image)
    target_channel_dim = ChannelDimension(channel_dim)
    if input_channel_dim == target_channel_dim: return image
    if target_channel_dim == ChannelDimension.FIRST: image = image.transpose((2, 0, 1))
    elif target_channel_dim == ChannelDimension.LAST: image = image.transpose((1, 2, 0))
    else: raise ValueError("Unsupported channel dimension format: {}".format(channel_dim))
    return image
def convert_to_rgb(image: ImageInput) -> ImageInput:
    if not isinstance(image, PIL.Image.Image): return image
    if image.mode == "RGB": return image
    image_rgba = image.convert("RGBA")
    background = Image.new("RGBA", image_rgba.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, image_rgba)
    alpha_composite = alpha_composite.convert("RGB")
    return alpha_composite
def make_list_of_images(images: ImageInput) -> List[List[Optional[np.ndarray]]]:
    if is_valid_image(images): output_images = [[images]]
    elif isinstance(images, (list, tuple)) and is_valid_list_of_images(images): output_images = [images]
    elif (isinstance(images, (list, tuple)) and all(isinstance(images_i, (list, tuple)) for images_i in images) and any(is_valid_list_of_images(images_i) for images_i in images)): output_images = images
    else: raise ValueError("Invalid input type. Must be a single image, a list of images, or a list of batches of images.")
    return output_images
def is_valid_list_of_images(images: List): return images and all(is_valid_image(image) for image in images)
def _validate_size(size: Dict[str, int]) -> None:
    if not ("height" in size and "width" in size): raise ValueError(f"Argument `size` must be a dictionary with keys 'height' and 'width'. Got: {size}")
    if size["height"] != size["width"]: raise ValueError(f"Argument `size` must have the same height and width, got {size}")
def _validate_mllama_preprocess_arguments(do_resize, size, do_pad, max_image_tiles):
    if not do_pad: raise ValueError("MllamaImageProcessor doesn't support `do_pad=False` mode.")
    if not do_resize: raise ValueError("MllamaImageProcessor doesn't support `do_resize=False` mode.")
    if max_image_tiles is None or max_image_tiles <= 0: raise ValueError(f"MllamaImageProcessor `max_image_tiles` must be a positive integer, got {max_image_tiles}.")
    _validate_size(size)
class MllamaImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "num_tiles", "aspect_ratio_ids", "aspect_ratio_mask"]
    def __init__(self, do_convert_rgb: bool = True, do_resize: bool = True, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_rescale: bool = True, rescale_factor: float = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_pad: bool = True, max_image_tiles: int = 4, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_convert_rgb = do_convert_rgb
        self.do_resize = do_resize
        self.size = size if size is not None else {"height": 224, "width": 224}
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
        self.max_image_tiles = max_image_tiles
        _validate_mllama_preprocess_arguments(self.do_resize, self.size, self.do_pad, self.max_image_tiles)
    def preprocess(self, images: ImageInput, do_convert_rgb: Optional[bool] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, resample: Optional[PILImageResampling] = None,
    do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, max_image_tiles: Optional[int] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None,
    return_tensors: Optional[Union[str, TensorType]] = None):
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        max_image_tiles = max_image_tiles if max_image_tiles is not None else self.max_image_tiles
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        _validate_mllama_preprocess_arguments(do_resize, size, do_pad, max_image_tiles)
        images_list = make_list_of_images(images)
        if self.do_convert_rgb: images_list = [[convert_to_rgb(image) for image in images] for images in images_list]
        images_list = [[to_numpy_array(image) for image in images] for images in images_list]
        batch_images = []
        batch_aspect_ratios = []
        for images in images_list:
            sample_images = []
            sample_aspect_ratios = []
            for image in images:
                data_format = ChannelDimension.FIRST
                image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
                image, aspect_ratio = self.resize(image=image, size=size, resample=resample, max_image_tiles=max_image_tiles, input_data_format=data_format, data_format=data_format)
                image = self.pad(image=image, size=size, aspect_ratio=aspect_ratio, input_data_format=data_format, data_format=data_format)
                if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format, data_format=data_format)
                if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format, data_format=data_format)
                num_tiles_height, num_tiles_width = aspect_ratio
                image = split_to_tiles(image, num_tiles_height, num_tiles_width)
                sample_images.append(image)
                sample_aspect_ratios.append((num_tiles_height, num_tiles_width))
            batch_images.append(sample_images)
            batch_aspect_ratios.append(sample_aspect_ratios)
        images, num_tiles = pack_images(batch_images, max_image_tiles)
        aspect_ratio_ids = convert_aspect_ratios_to_ids(batch_aspect_ratios, max_image_tiles=max_image_tiles)
        aspect_ratio_mask = build_aspect_ratio_mask(batch_aspect_ratios, max_image_tiles=max_image_tiles)
        encoded_inputs = BatchFeature(data={"pixel_values": images, "aspect_ratio_ids": aspect_ratio_ids, "aspect_ratio_mask": aspect_ratio_mask}, tensor_type=return_tensors)
        encoded_inputs["num_tiles"] = num_tiles
        return encoded_inputs
    def pad(self, image: np.ndarray, size: Dict[str, int], aspect_ratio: Tuple[int, int], data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        _validate_size(size)
        image_height, image_width = get_image_size(image, channel_dim=input_data_format)
        num_tiles_height, num_tiles_width = aspect_ratio
        padded_height = num_tiles_height * size["height"]
        padded_width = num_tiles_width * size["width"]
        pad_size = ((0, padded_height - image_height), (0, padded_width - image_width))
        image = pad(image, pad_size, mode=PaddingMode.CONSTANT, constant_values=0, data_format=data_format, input_data_format=input_data_format)
        return image
    def resize(self, image: np.ndarray, size: Dict[str, int], max_image_tiles: int, resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Union[np.ndarray, Tuple[int, int]]:
        _validate_size(size)
        image_height, image_width = get_image_size(image, channel_dim=input_data_format)
        tile_size = size["height"]
        canvas_height, canvas_width = get_optimal_tiled_canvas(image_height=image_height, image_width=image_width, max_image_tiles=max_image_tiles, tile_size=tile_size)
        num_tiles_height = canvas_height // tile_size
        num_tiles_width = canvas_width // tile_size
        new_height, new_width = get_image_size_fit_to_canvas(image_height=image_height, image_width=image_width, canvas_height=canvas_height, canvas_width=canvas_width, tile_size=tile_size)
        image = resize(image, (new_height, new_width), resample=resample, data_format=data_format, input_data_format=input_data_format)
        return image, (num_tiles_height, num_tiles_width)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
