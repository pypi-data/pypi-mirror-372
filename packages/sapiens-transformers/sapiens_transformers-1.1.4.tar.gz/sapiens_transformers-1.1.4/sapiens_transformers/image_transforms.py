"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils.import_utils import (is_flax_available, is_tf_available, is_torch_available, is_torchvision_available, is_vision_available, requires_backends)
from .image_utils import (ChannelDimension, ImageInput, get_channel_dimension_axis, get_image_size, infer_channel_dimension_format)
from .utils import ExplicitEnum, TensorType, is_jax_tensor, is_tf_tensor, is_torch_tensor
from typing import Iterable, List, Optional, Tuple, Union
from math import ceil
import numpy as np
import warnings
if is_vision_available():
    import PIL
    from .image_utils import PILImageResampling
if is_torch_available(): import torch
if is_tf_available(): import tensorflow as tf
if is_flax_available(): import jax.numpy as jnp
if is_torchvision_available(): from torchvision.transforms import functional as F
def to_channel_dimension_format(image: np.ndarray, channel_dim: Union[ChannelDimension, str], input_channel_dim: Optional[Union[ChannelDimension, str]] = None) -> np.ndarray:
    if not isinstance(image, np.ndarray): raise TypeError(f"Input image must be of type np.ndarray, got {type(image)}")
    if input_channel_dim is None: input_channel_dim = infer_channel_dimension_format(image)
    target_channel_dim = ChannelDimension(channel_dim)
    if input_channel_dim == target_channel_dim: return image
    if target_channel_dim == ChannelDimension.FIRST: image = image.transpose((2, 0, 1))
    elif target_channel_dim == ChannelDimension.LAST: image = image.transpose((1, 2, 0))
    else: raise ValueError("Unsupported channel dimension format: {}".format(channel_dim))
    return image
def rescale(image: np.ndarray, scale: float, data_format: Optional[ChannelDimension] = None, dtype: np.dtype = np.float32, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    if not isinstance(image, np.ndarray): raise TypeError(f"Input image must be of type np.ndarray, got {type(image)}")
    rescaled_image = image * scale
    if data_format is not None: rescaled_image = to_channel_dimension_format(rescaled_image, data_format, input_data_format)
    rescaled_image = rescaled_image.astype(dtype)
    return rescaled_image
def _rescale_for_pil_conversion(image):
    if image.dtype == np.uint8: do_rescale = False
    elif np.allclose(image, image.astype(int)):
        if np.all(0 <= image) and np.all(image <= 255): do_rescale = False
        else: raise ValueError(f"The image to be converted to a PIL image contains values outside the range [0, 255], got [{image.min()}, {image.max()}] which cannot be converted to uint8.")
    elif np.all(0 <= image) and np.all(image <= 1): do_rescale = True
    else: raise ValueError(f"The image to be converted to a PIL image contains values outside the range [0, 1], got [{image.min()}, {image.max()}] which cannot be converted to uint8.")
    return do_rescale
def to_pil_image(image: Union[np.ndarray, "PIL.Image.Image", "torch.Tensor", "tf.Tensor", "jnp.ndarray"], do_rescale: Optional[bool] = None, image_mode: Optional[str] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> "PIL.Image.Image":
    requires_backends(to_pil_image, ["vision"])
    if isinstance(image, PIL.Image.Image): return image
    if is_torch_tensor(image) or is_tf_tensor(image): image = image.numpy()
    elif is_jax_tensor(image): image = np.array(image)
    elif not isinstance(image, np.ndarray): raise ValueError("Input image type not supported: {}".format(type(image)))
    image = to_channel_dimension_format(image, ChannelDimension.LAST, input_data_format)
    image = np.squeeze(image, axis=-1) if image.shape[-1] == 1 else image
    do_rescale = _rescale_for_pil_conversion(image) if do_rescale is None else do_rescale
    if do_rescale: image = rescale(image, 255)
    image = image.astype(np.uint8)
    return PIL.Image.fromarray(image, mode=image_mode)
def get_resize_output_image_size(input_image: np.ndarray, size: Union[int, Tuple[int, int], List[int], Tuple[int]], default_to_square: bool = True, max_size: Optional[int] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> tuple:
    if isinstance(size, (tuple, list)):
        if len(size) == 2: return tuple(size)
        elif len(size) == 1: size = size[0]
        else: raise ValueError("size must have 1 or 2 elements if it is a list or tuple")
    if default_to_square: return (size, size)
    height, width = get_image_size(input_image, input_data_format)
    short, long = (width, height) if width <= height else (height, width)
    requested_new_short = size
    new_short, new_long = requested_new_short, int(requested_new_short * long / short)
    if max_size is not None:
        if max_size <= requested_new_short: raise ValueError(f"max_size = {max_size} must be strictly greater than the requested size for the smaller edge size = {size}")
        if new_long > max_size: new_short, new_long = int(max_size * new_short / new_long), max_size
    return (new_long, new_short) if width <= height else (new_short, new_long)
def resize(image: np.ndarray, size: Tuple[int, int], resample: "PILImageResampling" = None, reducing_gap: Optional[int] = None, data_format: Optional[ChannelDimension] = None, return_numpy: bool = True, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    requires_backends(resize, ["vision"])
    resample = resample if resample is not None else PILImageResampling.BILINEAR
    if not len(size) == 2: raise ValueError("size must have 2 elements")
    if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
    data_format = input_data_format if data_format is None else data_format
    do_rescale = False
    if not isinstance(image, PIL.Image.Image):
        do_rescale = _rescale_for_pil_conversion(image)
        image = to_pil_image(image, do_rescale=do_rescale, input_data_format=input_data_format)
    height, width = size
    resized_image = image.resize((width, height), resample=resample, reducing_gap=reducing_gap)
    if return_numpy:
        resized_image = np.array(resized_image)
        resized_image = np.expand_dims(resized_image, axis=-1) if resized_image.ndim == 2 else resized_image
        resized_image = to_channel_dimension_format(resized_image, data_format, input_channel_dim=ChannelDimension.LAST)
        resized_image = rescale(resized_image, 1 / 255) if do_rescale else resized_image
    return resized_image
def normalize(image: np.ndarray, mean: Union[float, Iterable[float]], std: Union[float, Iterable[float]], data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    if not isinstance(image, np.ndarray): raise ValueError("image must be a numpy array")
    if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
    channel_axis = get_channel_dimension_axis(image, input_data_format=input_data_format)
    num_channels = image.shape[channel_axis]
    if not np.issubdtype(image.dtype, np.floating): image = image.astype(np.float32)
    if isinstance(mean, Iterable):
        if len(mean) != num_channels: raise ValueError(f"mean must have {num_channels} elements if it is an iterable, got {len(mean)}")
    else: mean = [mean] * num_channels
    mean = np.array(mean, dtype=image.dtype)
    if isinstance(std, Iterable):
        if len(std) != num_channels: raise ValueError(f"std must have {num_channels} elements if it is an iterable, got {len(std)}")
    else: std = [std] * num_channels
    std = np.array(std, dtype=image.dtype)
    if input_data_format == ChannelDimension.LAST: image = (image - mean) / std
    else: image = ((image.T - mean) / std).T
    image = to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image
    return image
def center_crop(image: np.ndarray, size: Tuple[int, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, return_numpy: Optional[bool] = None) -> np.ndarray:
    requires_backends(center_crop, ["vision"])
    if return_numpy is not None: warnings.warn("return_numpy is deprecated and will be removed in v.4.33", FutureWarning)
    return_numpy = True if return_numpy is None else return_numpy
    if not isinstance(image, np.ndarray): raise TypeError(f"Input image must be of type np.ndarray, got {type(image)}")
    if not isinstance(size, Iterable) or len(size) != 2: raise ValueError("size must have 2 elements representing the height and width of the output image")
    if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
    output_data_format = data_format if data_format is not None else input_data_format
    image = to_channel_dimension_format(image, ChannelDimension.FIRST, input_data_format)
    orig_height, orig_width = get_image_size(image, ChannelDimension.FIRST)
    crop_height, crop_width = size
    crop_height, crop_width = int(crop_height), int(crop_width)
    top = (orig_height - crop_height) // 2
    bottom = top + crop_height
    left = (orig_width - crop_width) // 2
    right = left + crop_width
    if top >= 0 and bottom <= orig_height and left >= 0 and right <= orig_width:
        image = image[..., top:bottom, left:right]
        image = to_channel_dimension_format(image, output_data_format, ChannelDimension.FIRST)
        return image
    new_height = max(crop_height, orig_height)
    new_width = max(crop_width, orig_width)
    new_shape = image.shape[:-2] + (new_height, new_width)
    new_image = np.zeros_like(image, shape=new_shape)
    top_pad = ceil((new_height - orig_height) / 2)
    bottom_pad = top_pad + orig_height
    left_pad = ceil((new_width - orig_width) / 2)
    right_pad = left_pad + orig_width
    new_image[..., top_pad:bottom_pad, left_pad:right_pad] = image
    top += top_pad
    bottom += top_pad
    left += left_pad
    right += left_pad
    new_image = new_image[..., max(0, top) : min(new_height, bottom), max(0, left) : min(new_width, right)]
    new_image = to_channel_dimension_format(new_image, output_data_format, ChannelDimension.FIRST)
    if not return_numpy: new_image = to_pil_image(new_image)
    return new_image
def _center_to_corners_format_torch(bboxes_center: "torch.Tensor") -> "torch.Tensor":
    center_x, center_y, width, height = bboxes_center.unbind(-1)
    bbox_corners = torch.stack([(center_x - 0.5 * width), (center_y - 0.5 * height), (center_x + 0.5 * width), (center_y + 0.5 * height)], dim=-1)
    return bbox_corners
def _center_to_corners_format_numpy(bboxes_center: np.ndarray) -> np.ndarray:
    center_x, center_y, width, height = bboxes_center.T
    bboxes_corners = np.stack([center_x - 0.5 * width, center_y - 0.5 * height, center_x + 0.5 * width, center_y + 0.5 * height], axis=-1)
    return bboxes_corners
def _center_to_corners_format_tf(bboxes_center: "tf.Tensor") -> "tf.Tensor":
    center_x, center_y, width, height = tf.unstack(bboxes_center, axis=-1)
    bboxes_corners = tf.stack([center_x - 0.5 * width, center_y - 0.5 * height, center_x + 0.5 * width, center_y + 0.5 * height], axis=-1)
    return bboxes_corners
def center_to_corners_format(bboxes_center: TensorType) -> TensorType:
    if is_torch_tensor(bboxes_center): return _center_to_corners_format_torch(bboxes_center)
    elif isinstance(bboxes_center, np.ndarray): return _center_to_corners_format_numpy(bboxes_center)
    elif is_tf_tensor(bboxes_center): return _center_to_corners_format_tf(bboxes_center)
    raise ValueError(f"Unsupported input type {type(bboxes_center)}")
def _corners_to_center_format_torch(bboxes_corners: "torch.Tensor") -> "torch.Tensor":
    top_left_x, top_left_y, bottom_right_x, bottom_right_y = bboxes_corners.unbind(-1)
    b = [(top_left_x + bottom_right_x) / 2, (top_left_y + bottom_right_y) / 2, (bottom_right_x - top_left_x), (bottom_right_y - top_left_y)]
    return torch.stack(b, dim=-1)
def _corners_to_center_format_numpy(bboxes_corners: np.ndarray) -> np.ndarray:
    top_left_x, top_left_y, bottom_right_x, bottom_right_y = bboxes_corners.T
    bboxes_center = np.stack([(top_left_x + bottom_right_x) / 2, (top_left_y + bottom_right_y) / 2, (bottom_right_x - top_left_x), (bottom_right_y - top_left_y)], axis=-1)
    return bboxes_center
def _corners_to_center_format_tf(bboxes_corners: "tf.Tensor") -> "tf.Tensor":
    top_left_x, top_left_y, bottom_right_x, bottom_right_y = tf.unstack(bboxes_corners, axis=-1)
    bboxes_center = tf.stack([(top_left_x + bottom_right_x) / 2, (top_left_y + bottom_right_y) / 2, (bottom_right_x - top_left_x), (bottom_right_y - top_left_y)], axis=-1)
    return bboxes_center
def corners_to_center_format(bboxes_corners: TensorType) -> TensorType:
    if is_torch_tensor(bboxes_corners): return _corners_to_center_format_torch(bboxes_corners)
    elif isinstance(bboxes_corners, np.ndarray): return _corners_to_center_format_numpy(bboxes_corners)
    elif is_tf_tensor(bboxes_corners): return _corners_to_center_format_tf(bboxes_corners)
    raise ValueError(f"Unsupported input type {type(bboxes_corners)}")
def rgb_to_id(color):
    if isinstance(color, np.ndarray) and len(color.shape) == 3:
        if color.dtype == np.uint8: color = color.astype(np.int32)
        return color[:, :, 0] + 256 * color[:, :, 1] + 256 * 256 * color[:, :, 2]
    return int(color[0] + 256 * color[1] + 256 * 256 * color[2])
def id_to_rgb(id_map):
    if isinstance(id_map, np.ndarray):
        id_map_copy = id_map.copy()
        rgb_shape = tuple(list(id_map.shape) + [3])
        rgb_map = np.zeros(rgb_shape, dtype=np.uint8)
        for i in range(3):
            rgb_map[..., i] = id_map_copy % 256
            id_map_copy //= 256
        return rgb_map
    color = []
    for _ in range(3):
        color.append(id_map % 256)
        id_map //= 256
    return color
class PaddingMode(ExplicitEnum):
    CONSTANT = "constant"
    REFLECT = "reflect"
    REPLICATE = "replicate"
    SYMMETRIC = "symmetric"
def pad(image: np.ndarray, padding: Union[int, Tuple[int, int], Iterable[Tuple[int, int]]], mode: PaddingMode = PaddingMode.CONSTANT, constant_values: Union[float, Iterable[float]] = 0.0,
data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
    def _expand_for_data_format(values):
        if isinstance(values, (int, float)): values = ((values, values), (values, values))
        elif isinstance(values, tuple) and len(values) == 1: values = ((values[0], values[0]), (values[0], values[0]))
        elif isinstance(values, tuple) and len(values) == 2 and isinstance(values[0], int): values = (values, values)
        elif isinstance(values, tuple) and len(values) == 2 and isinstance(values[0], tuple): values = values
        else: raise ValueError(f"Unsupported format: {values}")
        values = ((0, 0), *values) if input_data_format == ChannelDimension.FIRST else (*values, (0, 0))
        values = (0, *values) if image.ndim == 4 else values
        return values
    padding = _expand_for_data_format(padding)
    if mode == PaddingMode.CONSTANT:
        constant_values = _expand_for_data_format(constant_values)
        image = np.pad(image, padding, mode="constant", constant_values=constant_values)
    elif mode == PaddingMode.REFLECT: image = np.pad(image, padding, mode="reflect")
    elif mode == PaddingMode.REPLICATE: image = np.pad(image, padding, mode="edge")
    elif mode == PaddingMode.SYMMETRIC: image = np.pad(image, padding, mode="symmetric")
    else: raise ValueError(f"Invalid padding mode: {mode}")
    image = to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image
    return image
def convert_to_rgb(image: ImageInput) -> ImageInput:
    requires_backends(convert_to_rgb, ["vision"])
    if not isinstance(image, PIL.Image.Image): return image
    if image.mode == "RGB": return image
    image = image.convert("RGB")
    return image
def flip_channel_order(image: np.ndarray, data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    input_data_format = infer_channel_dimension_format(image) if input_data_format is None else input_data_format
    if input_data_format == ChannelDimension.LAST: image = image[..., ::-1]
    elif input_data_format == ChannelDimension.FIRST: image = image[::-1, ...]
    else: raise ValueError(f"Unsupported channel dimension: {input_data_format}")
    if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
    return image
def _cast_tensor_to_float(x):
    if x.is_floating_point(): return x
    return x.float()
class FusedRescaleNormalize:
    def __init__(self, mean, std, rescale_factor: float = 1.0, inplace: bool = False):
        self.mean = torch.tensor(mean) * (1.0 / rescale_factor)
        self.std = torch.tensor(std) * (1.0 / rescale_factor)
        self.inplace = inplace
    def __call__(self, image: "torch.Tensor"):
        image = _cast_tensor_to_float(image)
        return F.normalize(image, self.mean, self.std, inplace=self.inplace)
class Rescale:
    def __init__(self, rescale_factor: float = 1.0): self.rescale_factor = rescale_factor
    def __call__(self, image: "torch.Tensor"):
        image = image * self.rescale_factor
        return image
class NumpyToTensor:
    def __call__(self, image: np.ndarray): return torch.from_numpy(image.transpose(2, 0, 1)).contiguous()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
