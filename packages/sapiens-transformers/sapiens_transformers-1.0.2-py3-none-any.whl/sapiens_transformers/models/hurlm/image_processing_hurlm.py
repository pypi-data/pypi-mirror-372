"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size,
infer_channel_dimension_format, is_scaled_image, is_valid_image, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...image_transforms import PaddingMode, pad, to_channel_dimension_format, to_pil_image
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from ...utils import TensorType, is_vision_available
import numpy as np
import math
MAX_IMAGE_SIZE = 4096
if is_vision_available():
    import PIL
    from PIL import Image
def _resize_output_size_rescale_to_max_len(height: int, width: int, min_len: Optional[int] = 1, max_len: Optional[int] = None) -> Tuple[int, int]:
    max_len = max(height, width) if max_len is None else max_len
    aspect_ratio = width / height
    if width >= height:
        width = max_len
        height = int(width / aspect_ratio)
        if height % 2 != 0: height += 1
    elif height > width:
        height = max_len
        width = int(height * aspect_ratio)
        if width % 2 != 0: width += 1
    height = max(height, min_len)
    width = max(width, min_len)
    return height, width
def _resize_output_size_scale_below_upper_bound(height: int, width: int, max_len: Optional[Dict[str, int]] = None) -> Tuple[int, int]:
    max_len = max(height, width) if max_len is None else max_len
    aspect_ratio = width / height
    if width >= height and width > max_len:
        width = max_len
        height = int(width / aspect_ratio)
    elif height > width and height > max_len:
        height = max_len
        width = int(height * aspect_ratio)
    height = max(height, 1)
    width = max(width, 1)
    return height, width
def get_resize_output_image_size(image, resolution_max_side: int, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    height, width = get_image_size(image, channel_dim=input_data_format)
    height, width = _resize_output_size_rescale_to_max_len(height, width, max_len=resolution_max_side)
    height, width = _resize_output_size_scale_below_upper_bound(height, width, max_len=MAX_IMAGE_SIZE)
    return height, width
def make_list_of_images(images: ImageInput) -> List[List[np.ndarray]]:
    if is_valid_image(images): images = [[images]]
    elif isinstance(images, (list, tuple)) and len(images) > 0 and is_valid_image(images[0]): images = [images]
    elif (isinstance(images, (list, tuple)) and len(images) > 0 and isinstance(images[0], (list, tuple)) and len(images[0]) > 0 and is_valid_image(images[0][0])): pass
    else: raise ValueError("Invalid input type. Must be a single image, a list of images, or a list of batches of images.")
    return images
def max_across_indices(values: Iterable[Any]) -> List[Any]: return [max(values_i) for values_i in zip(*values)]
def get_max_height_width(images_list: List[List[np.ndarray]], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> List[int]:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(images_list[0][0], num_channels=(1, 3, 4))
    max_height = max_width = float("-inf")
    for images in images_list:
        for image in images:
            height, width = get_image_size(image, channel_dim=input_data_format)
            max_height = max(height, max_height)
            max_width = max(width, max_width)
    return (max_height, max_width)
def make_pixel_mask(image: np.ndarray, output_size: Tuple[int, int], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    input_height, input_width = get_image_size(image, channel_dim=input_data_format)
    mask = np.zeros(output_size, dtype=np.int64)
    mask[:input_height, :input_width] = 1
    return mask
def convert_to_rgb(image: np.ndarray, palette: Optional[PIL.ImagePalette.ImagePalette] = None, data_format: Optional[Union[str, ChannelDimension]] = None,
input_data_format: Optional[Union[str, ChannelDimension]] = None) -> ImageInput:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(image, num_channels=(1, 3, 4))
    data_format = input_data_format if data_format is None else data_format
    mode = "P" if palette is not None else None
    image = to_pil_image(image, image_mode=mode, input_data_format=input_data_format)
    if image.mode == "P" and palette is not None: image.putpalette(palette)
    image_rgba = image.convert("RGBA")
    background = Image.new("RGBA", image_rgba.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, image_rgba)
    alpha_composite = alpha_composite.convert("RGB")
    output_array = np.array(alpha_composite)
    output_array = to_channel_dimension_format(output_array, data_format, input_channel_dim=ChannelDimension.LAST)
    return output_array
def _crop(image: np.ndarray, w1: int, h1: int, w2: int, h2: int, data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    if data_format is None: data_format = infer_channel_dimension_format(image, num_channels=(1, 3, 4))
    if data_format == ChannelDimension.FIRST: image = image[:, h1:h2, w1:w2]
    elif data_format == ChannelDimension.LAST: image = image[h1:h2, w1:w2, :]
    else: raise ValueError("Invalid channel dimension format.")
    return image
class HurLMImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_convert_rgb: bool = True, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.LANCZOS,
    do_image_splitting: bool = True, max_image_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: float = 1 / 255, do_normalize: bool = True,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_convert_rgb = do_convert_rgb
        self.do_resize = do_resize
        self.size = size if size is not None else {"longest_edge": 4 * 364}
        self.resample = resample
        self.do_image_splitting = do_image_splitting
        self.max_image_size = max_image_size if max_image_size is not None else {"longest_edge": 364}
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.LANCZOS, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image, num_channels=(1, 3, 4))
        data_format = input_data_format if data_format is None else data_format
        if "longest_edge" in size: size = get_resize_output_image_size(image, resolution_max_side=size["longest_edge"], input_data_format=input_data_format)
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("size must be a dictionary with key 'longest_edge' or 'height' and 'width'.")
        image_mode = None
        if image.ndim == 2 or image.shape[-1] == 1: image_mode = "P"
        image = to_pil_image(image, image_mode=image_mode, input_data_format=input_data_format)
        resized_image = image.resize((size[1], size[0]), resample=resample)
        resized_image = np.array(resized_image)
        resized_image = np.expand_dims(resized_image, axis=-1) if resized_image.ndim == 2 else resized_image
        resized_image = to_channel_dimension_format(resized_image, data_format, input_channel_dim=ChannelDimension.LAST)
        return resized_image
    def split_image(self, image, max_image_size: Dict[str, int], resample: PILImageResampling = PILImageResampling.LANCZOS, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None):
        height, width = get_image_size(image, channel_dim=input_data_format)
        max_height = max_width = max_image_size["longest_edge"]
        frames = []
        if height > max_height or width > max_width:
            num_splits_h = math.ceil(height / max_height)
            num_splits_w = math.ceil(width / max_width)
            optimal_height = math.ceil(height / num_splits_h)
            optimal_width = math.ceil(width / num_splits_w)
            for r in range(num_splits_h):
                for c in range(num_splits_w):
                    start_x = c * optimal_width
                    start_y = r * optimal_height
                    end_x = min(start_x + optimal_width, width)
                    end_y = min(start_y + optimal_height, height)
                    cropped_image = _crop(image, start_x, start_y, end_x, end_y, data_format=data_format)
                    frames.append(cropped_image)
            global_image_height, global_image_width = max_height, max_width
            if height != global_image_height or width != global_image_width: image = self.resize(image, {"height": global_image_height, "width": global_image_width},
            resample=resample, input_data_format=data_format)
        else: num_splits_h, num_splits_w = 0, 0
        frames.append(image)
        return frames, num_splits_h, num_splits_w
    def resize_for_vision_encoder(self, image: np.ndarray, vision_encoder_max_size: int, resample: PILImageResampling = PILImageResampling.LANCZOS,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        height, width = get_image_size(image, channel_dim=input_data_format)
        aspect_ratio = width / height
        if width >= height:
            width = math.ceil(width / vision_encoder_max_size) * vision_encoder_max_size
            height = int(width / aspect_ratio)
            height = math.ceil(height / vision_encoder_max_size) * vision_encoder_max_size
        elif height > width:
            height = math.ceil(height / vision_encoder_max_size) * vision_encoder_max_size
            width = int(height * aspect_ratio)
            width = math.ceil(width / vision_encoder_max_size) * vision_encoder_max_size
        new_size = {"height": height, "width": width}
        return self.resize(image, size=new_size, resample=resample, input_data_format=input_data_format, data_format=data_format)
    def _pad_image(self, image: np.ndarray, output_size: Tuple[int, int], constant_values: Union[float, Iterable[float]] = 0, data_format: Optional[ChannelDimension] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
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
        input_data_format = (infer_channel_dimension_format(images[0][0], num_channels=(1, 3, 4)) if input_data_format is None else input_data_format)
        data_format = input_data_format if data_format is None else data_format
        if input_data_format == ChannelDimension.FIRST: n_channels = images[0][0].shape[0]
        elif input_data_format == ChannelDimension.LAST: n_channels = images[0][0].shape[-1]
        else: raise ValueError("Invalid channel dimension format.")
        def empty_image(size, input_data_format):
            if input_data_format == ChannelDimension.FIRST: return np.zeros((n_channels, *size), dtype=np.uint8)
            elif input_data_format == ChannelDimension.LAST: return np.zeros((*size, n_channels), dtype=np.uint8)
        padded_images_list = [[empty_image(pad_size, data_format) for _ in range(max_num_images)] for _ in range(batch_size)]
        padded_masks = [[np.zeros(pad_size) for _ in range(max_num_images)] for _ in range(batch_size)]
        for batch_idx in range(batch_size):
            for sample_idx, image in enumerate(images[batch_idx]):
                padded_images_list[batch_idx][sample_idx] = self._pad_image(image, pad_size, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
                padded_masks[batch_idx][sample_idx] = make_pixel_mask(image, output_size=pad_size, input_data_format=input_data_format)
        padded_masks = padded_masks if return_pixel_mask else None
        return padded_images_list, padded_masks
    def preprocess(self, images: ImageInput, do_convert_rgb: Optional[bool] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None,
    resample: PILImageResampling = None, do_image_splitting: Optional[bool] = None, do_rescale: Optional[bool] = None, max_image_size: Optional[Dict[str, int]] = None,
    rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_row_col_info: bool = False, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_image_splitting = do_image_splitting if do_image_splitting is not None else self.do_image_splitting
        max_image_size = max_image_size if max_image_size is not None else self.max_image_size
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_pad = do_pad if do_pad is not None else self.do_pad
        images_list = make_list_of_images(images)
        if not valid_images(images_list[0]): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean,
        image_std=image_std, do_resize=do_resize, size=size, resample=resample)
        palettes_list = [[im.getpalette() if isinstance(im, Image.Image) and im.mode == "P" else None for im in images] for images in images_list]
        images_list = [[to_numpy_array(image) for image in images] for images in images_list]
        if input_data_format in [ChannelDimension.LAST, None]: images_list = [[np.expand_dims(img, axis=-1) if img.ndim == 2 else img for img in images] for images in images_list]
        elif input_data_format == ChannelDimension.FIRST: images_list = [[np.expand_dims(img, axis=0) if img.ndim == 2 else img for img in images] for images in images_list]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images_list[0][0], num_channels=(1, 3, 4))
        if do_resize: images_list = [[self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format) for image in images] for images in images_list]
        if do_image_splitting:
            images_list = [[self.resize_for_vision_encoder(image, max_image_size["longest_edge"], resample=resample, input_data_format=input_data_format) for image in images] for images in images_list]
            images_list_split_arrays = []
            palettes_list_split_arrays = []
            images_list_rows = []
            images_list_cols = []
            for images, palettes in zip(images_list, palettes_list):
                split_image_arrays = []
                split_palettes_arrays = []
                image_rows = []
                image_cols = []
                for image, palette in zip(images, palettes):
                    split_image_array, rows, cols = self.split_image(image, max_image_size=max_image_size, input_data_format=input_data_format)
                    split_image_arrays.extend(split_image_array)
                    split_palettes_arrays.extend([palette] * len(split_image_array))
                    image_rows.append(rows)
                    image_cols.append(cols)
                images_list_split_arrays.append(split_image_arrays)
                palettes_list_split_arrays.append(split_palettes_arrays)
                images_list_rows.append(image_rows)
                images_list_cols.append(image_cols)
            images_list = images_list_split_arrays
            palettes_list = palettes_list_split_arrays
        else:
            images_list = [[self.resize(image=image, size={"height": max_image_size["longest_edge"], "width": max_image_size["longest_edge"]}, resample=resample,
            input_data_format=input_data_format) for image in images] for images in images_list]
            images_list_rows = [[0] * len(images) for images in images_list]
            images_list_cols = [[0] * len(images) for images in images_list]
        if do_convert_rgb: images_list = [[convert_to_rgb(img, palette) for img, palette in zip(images, palettes)] for images, palettes in zip(images_list, palettes_list)]
        if do_rescale: images_list = [[self.rescale(image, rescale_factor, input_data_format=input_data_format) for image in images] for images in images_list]
        if do_normalize: images_list = [[self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images] for images in images_list]
        pixel_attention_mask = None
        if do_pad: images_list, pixel_attention_mask = self.pad(images_list, return_pixel_mask=True, return_tensors=return_tensors, input_data_format=input_data_format)
        if data_format is not None: images_list = [[to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images] for images in images_list]
        data = {"pixel_values": np.array(images_list) if do_pad and return_tensors is not None else images_list}
        if pixel_attention_mask is not None: data["pixel_attention_mask"] = (np.array(pixel_attention_mask) if do_pad and return_tensors is not None else pixel_attention_mask)
        encoding = BatchFeature(data=data, tensor_type=return_tensors)
        if return_row_col_info: encoding["rows"], encoding["cols"] = images_list_rows, images_list_cols
        return encoding
__all__ = ["HurLMImageProcessor"]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
