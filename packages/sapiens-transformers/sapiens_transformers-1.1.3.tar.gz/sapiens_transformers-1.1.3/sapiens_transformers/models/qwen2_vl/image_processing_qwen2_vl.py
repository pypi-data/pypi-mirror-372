"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Dict, List, Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import (convert_to_rgb, resize, to_channel_dimension_format)
from ...image_utils import (OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, PILImageResampling, VideoInput, get_image_size, infer_channel_dimension_format,
is_scaled_image, is_valid_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, is_vision_available, logging
logger = logging.get_logger(__name__)
if is_vision_available(): from PIL import Image
def make_batched_images(images) -> List[List[ImageInput]]:
    if isinstance(images, (list, tuple)) and isinstance(images[0], (list, tuple)) and is_valid_image(images[0][0]): return [img for img_list in images for img in img_list]
    elif isinstance(images, (list, tuple)) and is_valid_image(images[0]): return images
    elif is_valid_image(images): return [images]
    raise ValueError(f"Could not make batched images from {images}")
def make_batched_videos(videos) -> List[VideoInput]:
    if isinstance(videos, (list, tuple)) and isinstance(videos[0], (list, tuple)) and is_valid_image(videos[0][0]): return videos
    elif isinstance(videos, (list, tuple)) and is_valid_image(videos[0]):
        if isinstance(videos[0], Image.Image): return [videos]
        elif len(videos[0].shape) == 4: return [list(video) for video in videos]
    elif is_valid_image(videos) and len(videos.shape) == 4: return [list(videos)]
    raise ValueError(f"Could not make batched video from {videos}")
def smart_resize(height: int, width: int, factor: int = 28, min_pixels: int = 56 * 56, max_pixels: int = 14 * 14 * 4 * 1280):
    if height < factor or width < factor: raise ValueError(f"height:{height} or width:{width} must be larger than factor:{factor}")
    elif max(height, width) / min(height, width) > 200: raise ValueError(f"absolute aspect ratio must be smaller than 200, got {max(height, width) / min(height, width)}")
    h_bar = round(height / factor) * factor
    w_bar = round(width / factor) * factor
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar = math.floor(height / beta / factor) * factor
        w_bar = math.floor(width / beta / factor) * factor
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar = math.ceil(height * beta / factor) * factor
        w_bar = math.ceil(width * beta / factor) * factor
    return h_bar, w_bar
class Qwen2VLImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "image_grid_thw", "pixel_values_videos", "video_grid_thw"]
    def __init__(self, do_resize: bool = True, resample: PILImageResampling = PILImageResampling.BICUBIC, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255,
    do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = True,
    min_pixels: int = 56 * 56, max_pixels: int = 28 * 28 * 1280, patch_size: int = 14, temporal_patch_size: int = 2, merge_size: int = 2, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_resize = do_resize
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else OPENAI_CLIP_MEAN
        self.image_std = image_std if image_std is not None else OPENAI_CLIP_STD
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels
        self.patch_size = patch_size
        self.temporal_patch_size = temporal_patch_size
        self.merge_size = merge_size
        self.size = {"min_pixels": min_pixels, "max_pixels": max_pixels}
        self.do_convert_rgb = do_convert_rgb
    def _preprocess(self, images: Union[ImageInput, VideoInput], do_resize: bool = None, resample: PILImageResampling = None, do_rescale: bool = None, rescale_factor: float = None,
    do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = None,
    data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        images = make_list_of_images(images)
        if do_convert_rgb: images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        height, width = get_image_size(images[0], channel_dim=input_data_format)
        resized_height, resized_width = height, width
        processed_images = []
        for image in images:
            if do_resize:
                resized_height, resized_width = smart_resize(height, width, factor=self.patch_size * self.merge_size, min_pixels=self.min_pixels, max_pixels=self.max_pixels)
                image = resize(image, size=(resized_height, resized_width), resample=resample, input_data_format=input_data_format)
            if do_rescale: image = self.rescale(image, scale=rescale_factor, input_data_format=input_data_format)
            if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
            image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
            processed_images.append(image)
        patches = np.array(processed_images)
        if data_format == ChannelDimension.LAST: patches = patches.transpose(0, 3, 1, 2)
        if patches.shape[0] == 1: patches = np.tile(patches, (self.temporal_patch_size, 1, 1, 1))
        channel = patches.shape[1]
        grid_t = patches.shape[0] // self.temporal_patch_size
        grid_h, grid_w = resized_height // self.patch_size, resized_width // self.patch_size
        patches = patches.reshape(grid_t, self.temporal_patch_size, channel, grid_h // self.merge_size, self.merge_size, self.patch_size, grid_w // self.merge_size, self.merge_size, self.patch_size)
        patches = patches.transpose(0, 3, 6, 4, 7, 2, 1, 5, 8)
        flatten_patches = patches.reshape(grid_t * grid_h * grid_w, channel * self.temporal_patch_size * self.patch_size * self.patch_size)
        return flatten_patches, (grid_t, grid_h, grid_w)
    def preprocess(self, images: ImageInput, videos: VideoInput = None, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: Optional[ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        if images is not None: images = make_batched_images(images)
        if videos is not None: videos = make_batched_videos(videos)
        if images is not None and not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_resize=do_resize, size=size, resample=resample)
        if images is not None:
            pixel_values, vision_grid_thws = [], []
            for image in images:
                patches, image_grid_thw = self._preprocess(image, do_resize=do_resize, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
                do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format)
                pixel_values.extend(patches)
                vision_grid_thws.append(image_grid_thw)
            pixel_values = np.array(pixel_values)
            vision_grid_thws = np.array(vision_grid_thws)
            data = {"pixel_values": pixel_values, "image_grid_thw": vision_grid_thws}
        if videos is not None:
            pixel_values, vision_grid_thws = [], []
            for images in videos:
                patches, video_grid_thw = self._preprocess(images, do_resize=do_resize, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
                do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format)
                pixel_values.extend(patches)
                vision_grid_thws.append(video_grid_thw)
            pixel_values = np.array(pixel_values)
            vision_grid_thws = np.array(vision_grid_thws)
            data = {"pixel_values_videos": pixel_values, "video_grid_thw": vision_grid_thws}
        return BatchFeature(data=data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
