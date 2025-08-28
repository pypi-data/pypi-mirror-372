"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .image_processing_base import BatchFeature, ImageProcessingMixin
from .image_transforms import center_crop, normalize, rescale
from typing import Dict, Iterable, Optional, Union
from .image_utils import ChannelDimension
from .utils import logging
import numpy as np
logger = logging.get_logger(__name__)
INIT_SERVICE_KWARGS = ["processor_class", "image_processor_type"]
class BaseImageProcessor(ImageProcessingMixin):
    def __init__(self, **kwargs): super().__init__(**kwargs)
    def __call__(self, images, **kwargs) -> BatchFeature: return self.preprocess(images, **kwargs)
    def preprocess(self, images, **kwargs) -> BatchFeature: raise NotImplementedError("Each image processor must implement its own preprocess method")
    def rescale(self, image: np.ndarray, scale: float, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray: return rescale(image, scale=scale, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def normalize(self, image: np.ndarray, mean: Union[float, Iterable[float]], std: Union[float, Iterable[float]], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray: return normalize(image, mean=mean, std=std, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def center_crop(self, image: np.ndarray, size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The size dictionary must have keys 'height' and 'width'. Got {size.keys()}")
        return center_crop(image, size=(size["height"], size["width"]), data_format=data_format, input_data_format=input_data_format, **kwargs)
    def to_dict(self):
        encoder_dict = super().to_dict()
        encoder_dict.pop("_valid_processor_keys", None)
        return encoder_dict
VALID_SIZE_DICT_KEYS = ({"height", "width"}, {"shortest_edge"}, {"shortest_edge", "longest_edge"}, {"longest_edge"}, {"max_height", "max_width"})
def is_valid_size_dict(size_dict):
    if not isinstance(size_dict, dict): return False
    size_dict_keys = set(size_dict.keys())
    for allowed_keys in VALID_SIZE_DICT_KEYS:
        if size_dict_keys == allowed_keys: return True
    return False
def convert_to_size_dict(size, max_size: Optional[int] = None, default_to_square: bool = True, height_width_order: bool = True):
    if isinstance(size, int) and default_to_square:
        if max_size is not None: raise ValueError("Cannot specify both size as an int, with default_to_square=True and max_size")
        return {"height": size, "width": size}
    elif isinstance(size, int) and not default_to_square:
        size_dict = {"shortest_edge": size}
        if max_size is not None: size_dict["longest_edge"] = max_size
        return size_dict
    elif isinstance(size, (tuple, list)) and height_width_order: return {"height": size[0], "width": size[1]}
    elif isinstance(size, (tuple, list)) and not height_width_order: return {"height": size[1], "width": size[0]}
    elif size is None and max_size is not None:
        if default_to_square: raise ValueError("Cannot specify both default_to_square=True and max_size")
        return {"longest_edge": max_size}
    raise ValueError(f"Could not convert size input to size dict: {size}")
def get_size_dict(size: Union[int, Iterable[int], Dict[str, int]] = None, max_size: Optional[int] = None, height_width_order: bool = True, default_to_square: bool = True, param_name="size") -> dict:
    if not isinstance(size, dict):
        size_dict = convert_to_size_dict(size, max_size, default_to_square, height_width_order)
        logger.info(f"{param_name} should be a dictionary on of the following set of keys: {VALID_SIZE_DICT_KEYS}, got {size}. Converted to {size_dict}.")
    else: size_dict = size
    if not is_valid_size_dict(size_dict): raise ValueError(f"{param_name} must have one of the following set of keys: {VALID_SIZE_DICT_KEYS}, got {size_dict.keys()}")
    return size_dict
def select_best_resolution(original_size: tuple, possible_resolutions: list) -> tuple:
    original_height, original_width = original_size
    best_fit = None
    max_effective_resolution = 0
    min_wasted_resolution = float("inf")
    for height, width in possible_resolutions:
        scale = min(width / original_width, height / original_height)
        downscaled_width, downscaled_height = int(original_width * scale), int(original_height * scale)
        effective_resolution = min(downscaled_width * downscaled_height, original_width * original_height)
        wasted_resolution = (width * height) - effective_resolution
        if effective_resolution > max_effective_resolution or (effective_resolution == max_effective_resolution and wasted_resolution < min_wasted_resolution):
            max_effective_resolution = effective_resolution
            min_wasted_resolution = wasted_resolution
            best_fit = (height, width)
    return best_fit
class SapiensImageProcessor(BaseImageProcessor): pass
from .image_processing_base import BatchFeature as SapiensBatchFeature
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
