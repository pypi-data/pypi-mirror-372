"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...image_utils import (get_image_size, ChannelDimension, ImageInput, is_valid_image, PILImageResampling, OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, infer_channel_dimension_format,
make_list_of_images, valid_images, validate_preprocess_arguments, to_numpy_array, is_scaled_image)
from ...utils import is_vision_available, TensorType
if is_vision_available(): from PIL import Image
def _get_patch_output_size(image, target_resolution, input_data_format):
    original_height, original_width = get_image_size(image, channel_dim=input_data_format)
    target_height, target_width = target_resolution
    scale_w, scale_h = target_width / original_width, target_height / original_height
    from math import ceil
    if scale_w < scale_h: new_width, new_height = target_width, min(ceil(original_height * scale_w), target_height)
    else: new_height, new_width = target_height, min(ceil(original_width * scale_h), target_width)
    return new_height, new_width
from numpy import array as n_array, ndarray as n_ndarray, pad as n_pad, ones as n_ones
from typing import List, Dict, Union, Optional, Tuple, Iterable
def divide_to_patches(image: n_array, patch_size: int, input_data_format) -> List[n_array]:
    patches = []
    height, width = get_image_size(image, channel_dim=input_data_format)
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size):
            if input_data_format == ChannelDimension.LAST: patch = image[i : i + patch_size, j : j + patch_size]
            else: patch = image[:, i : i + patch_size, j : j + patch_size]
            patches.append(patch)
    return patches
def make_batched_images(images) -> List[List[ImageInput]]:
    if isinstance(images, (list, tuple)) and isinstance(images[0], (list, tuple)) and is_valid_image(images[0][0]): return [img for img_list in images for img in img_list]
    elif isinstance(images, (list, tuple)) and is_valid_image(images[0]): return images
    elif is_valid_image(images): return [images]
    raise ValueError(f"Could not make batched video from {images}")
from ...image_processing_utils import BaseImageProcessor, get_size_dict, select_best_resolution, BatchFeature
from ...image_transforms import (get_resize_output_image_size, PaddingMode, pad, to_channel_dimension_format, resize, convert_to_rgb)
class SAPIImageImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, image_grid_pinpoints: List = None, resample: PILImageResampling = PILImageResampling.BICUBIC,
    do_center_crop: bool = True, crop_size: Dict[str, int] = None, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = True, do_convert_rgb: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"shortest_edge": 224}
        size, image_grid_pinpoints = get_size_dict(size, default_to_square=False), (image_grid_pinpoints if image_grid_pinpoints is not None else [[336, 672], [672, 336], [672, 672], [1008, 336], [336, 1008]])
        crop_size, crop_size = crop_size if crop_size is not None else {"height": 224, "width": 224}, get_size_dict(crop_size, default_to_square=True, param_name="crop_size")
        self.do_resize, self.size, self.image_grid_pinpoints = do_resize, size, image_grid_pinpoints
        self.resample, self.do_center_crop, self.crop_size = resample, do_center_crop, crop_size
        self.do_rescale, self.rescale_factor, self.do_normalize = do_rescale, rescale_factor, do_normalize
        self.image_mean, self.image_std = image_mean if image_mean is not None else OPENAI_CLIP_MEAN, image_std if image_std is not None else OPENAI_CLIP_STD
        self.do_pad, self.do_convert_rgb = do_pad, do_convert_rgb
    def resize(self, image: n_ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> n_ndarray:
        default_to_square = True
        if "shortest_edge" in size: size, default_to_square = size["shortest_edge"], False
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("Size must contain either 'shortest_edge' or 'height' and 'width'.")
        output_size = get_resize_output_image_size(image, size=size, default_to_square=default_to_square, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def pad(self, image: n_ndarray, padding: Union[int, Tuple[int, int], Iterable[Tuple[int, int]]], mode: PaddingMode = PaddingMode.CONSTANT,
    constant_values: Union[float, Iterable[float]] = 0.0, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> n_ndarray:
        if isinstance(padding, int) or len(padding) != 4: return pad(image, padding, mode, constant_values, data_format, input_data_format)
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        if mode == PaddingMode.CONSTANT: image = n_pad(image, padding, mode="constant", constant_values=constant_values)
        elif mode == PaddingMode.REFLECT: image = n_pad(image, padding, mode="reflect")
        elif mode == PaddingMode.REPLICATE: image = n_pad(image, padding, mode="edge")
        elif mode == PaddingMode.SYMMETRIC: image = n_pad(image, padding, mode="symmetric")
        else: raise ValueError(f"Invalid padding mode: {mode}")
        image = (to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image)
        return image
    def _preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_center_crop: bool = None,
    crop_size: int = None, do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Image.Image:
        images, all_images = make_list_of_images(images), []
        for image in images:
            if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
            if do_center_crop: image = self.center_crop(image=image, size=crop_size, input_data_format=input_data_format)
            if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
            if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
            all_images.append(image)
        return [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in all_images]
    def _resize_for_patching(self, image: n_array, target_resolution: tuple, resample, input_data_format: ChannelDimension) -> n_array:
        new_height, new_width = _get_patch_output_size(image, target_resolution, input_data_format)
        return resize(image, (new_height, new_width), resample=resample, input_data_format=input_data_format)
    def _pad_for_patching(self, image: n_array, target_resolution: tuple, input_data_format: ChannelDimension) -> n_array:
        target_height, target_width = target_resolution
        new_height, new_width = _get_patch_output_size(image, target_resolution, input_data_format)
        paste_x, paste_y = (target_width - new_width) // 2, (target_height - new_height) // 2
        return self.pad(image, padding=((paste_y, paste_y), (paste_x, paste_x)))
    def get_image_patches(self, image: n_array, grid_pinpoints, size: tuple, patch_size: int, resample: PILImageResampling, data_format: ChannelDimension,
    input_data_format: ChannelDimension) -> List[n_array]:
        if not isinstance(grid_pinpoints, list): raise TypeError("grid_pinpoints must be a list of possible resolutions.")
        best_resolution = select_best_resolution(get_image_size(image, channel_dim=input_data_format), grid_pinpoints)
        resized_image = self._resize_for_patching(image, best_resolution, resample=resample, input_data_format=input_data_format)
        padded_image = self._pad_for_patching(resized_image, best_resolution, input_data_format=input_data_format)
        return [resize(image, size=size, resample=resample, data_format=data_format, input_data_format=input_data_format)] + [to_channel_dimension_format(patch, channel_dim=data_format, input_channel_dim=input_data_format) for patch in divide_to_patches(padded_image, patch_size=patch_size, input_data_format=input_data_format)]
    def _pad_for_batching(self, pixel_values: List[n_ndarray], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None): return [self.pad(image, padding=((0, max(len(x) for x in pixel_values) - image.shape[0]), (0, 0), (0, 0), (0, 0)), data_format=data_format, input_data_format=input_data_format) for image in pixel_values]
    def preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, image_grid_pinpoints: List = None, resample: PILImageResampling = None,
    do_center_crop: bool = None, crop_size: int = None, do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, do_convert_rgb: bool = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_resize, size = do_resize if do_resize is not None else self.do_resize, size if size is not None else self.size
        size, image_grid_pinpoints = get_size_dict(size, param_name="size", default_to_square=False), image_grid_pinpoints if image_grid_pinpoints is not None else self.image_grid_pinpoints
        resample, do_center_crop = resample if resample is not None else self.resample, do_center_crop if do_center_crop is not None else self.do_center_crop
        crop_size = get_size_dict(crop_size if crop_size is not None else self.crop_size, param_name="crop_size", default_to_square=True)
        do_rescale, rescale_factor = do_rescale if do_rescale is not None else self.do_rescale, rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize, image_mean = do_normalize if do_normalize is not None else self.do_normalize, image_mean if image_mean is not None else self.image_mean
        image_std, do_pad, do_convert_rgb = image_std if image_std is not None else self.image_std, do_pad if do_pad is not None else self.do_pad, do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        images = make_batched_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        if do_convert_rgb: images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        new_images, image_sizes = [], [get_image_size(image, channel_dim=input_data_format) for image in images]
        for image in images:
            image_patches = self.get_image_patches(image, image_grid_pinpoints, size=(size["shortest_edge"], size["shortest_edge"]) if "shortest_edge" in size else (min(size["height"], size["width"]), min(size["height"], size["width"])),
            patch_size=crop_size["height"], resample=resample, data_format=input_data_format, input_data_format=input_data_format)
            pixel_values = self._preprocess(image_patches, do_resize=do_resize, size=size, resample=resample, do_center_crop=do_center_crop, crop_size=crop_size,
            do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format)
            pixel_values = n_array(pixel_values)
            new_images.append(pixel_values)
        if do_pad: processed_images = self._pad_for_batching(new_images)
        return BatchFeature(data={"pixel_values": processed_images, "image_sizes": image_sizes}, tensor_type=return_tensors)
def expand_to_square(image: n_array, background_color, input_data_format) -> n_array:
    height, width = get_image_size(image, channel_dim=input_data_format)
    if width == height: return image
    elif width > height:
        result = n_ones((width, width, image.shape[2]), dtype=image.dtype) * background_color
        result[(width - height) // 2 : (width - height) // 2 + height, :] = image
        return result
    else:
        result = n_ones((height, height, image.shape[2]), dtype=image.dtype) * background_color
        result[:, (height - width) // 2 : (height - width) // 2 + width] = image
        return result
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
