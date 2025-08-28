"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import (resize, to_channel_dimension_format)
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format, is_scaled_image, is_valid_image,
to_numpy_array, valid_images, validate_kwargs, validate_preprocess_arguments)
from ...utils import TensorType, is_torch_device, is_torch_dtype, is_torch_tensor, is_vision_available, logging
from ...utils.import_utils import requires_backends
logger = logging.get_logger(__name__)
if is_vision_available(): import PIL
class BatchMixFeature(BatchFeature):
    def to(self, *args, **kwargs) -> "BatchMixFeature":
        requires_backends(self, ["torch"])
        import torch
        new_data = {}
        device = kwargs.get("device")
        if device is None and len(args) > 0:
            arg = args[0]
            if is_torch_dtype(arg): pass
            elif isinstance(arg, str) or is_torch_device(arg) or isinstance(arg, int): device = arg
            else: raise ValueError(f"Attempting to cast a BatchFeature to type {str(arg)}. This is not supported.")
        for k, v in self.items():
            if isinstance(v, list): new_data[k] = [element.to(*args, **kwargs) for sample in v for element in sample if is_torch_tensor(element)]
            elif torch.is_floating_point(v): new_data[k] = v.to(*args, **kwargs)
            elif device is not None: new_data[k] = v.to(device=device)
            else: new_data[k] = v
        self.data = new_data
        return self
def make_list_of_images(images: ImageInput) -> List[List[np.ndarray]]:
    if is_valid_image(images): images = [[images]]
    elif isinstance(images, (list, tuple)) and len(images) > 0 and is_valid_image(images[0]): images = [images]
    elif (isinstance(images, (list, tuple)) and len(images) > 0 and isinstance(images[0], (list, tuple)) and is_valid_image(images[0][0])): pass
    else: raise ValueError("Invalid input type. Must be a single image, a list of images, or a list of batches of images.")
    return images
def convert_to_rgb(image: ImageInput) -> ImageInput:
    requires_backends(convert_to_rgb, ["vision"])
    if not isinstance(image, PIL.Image.Image): return image
    if image.mode == "RGB": return image
    image = image.convert("RGBA")
    new_image = PIL.Image.new("RGBA", image.size, "WHITE")
    new_image.paste(image, (0, 0), image)
    new_image = new_image.convert("RGB")
    return new_image
def _num_image_tokens(image_size: Tuple[int, int], patch_size: Tuple[int, int]) -> int:
    height, width = image_size
    patch_height, patch_width = patch_size if isinstance(patch_size, (tuple, list)) else (patch_size, patch_size)
    num_width_tokens = (width - 1) // patch_width + 1
    num_height_tokens = (height - 1) // patch_height + 1
    return num_height_tokens, num_width_tokens
def get_resize_output_image_size(input_image: np.ndarray, size: Union[int, Tuple[int, int], List[int], Tuple[int]], patch_size: Union[int, Tuple[int, int], List[int], Tuple[int]],
input_data_format: Optional[Union[str, ChannelDimension]] = None) -> tuple:
    max_height, max_width = size if isinstance(size, (tuple, list)) else (size, size)
    patch_height, patch_width = patch_size if isinstance(patch_size, (tuple, list)) else (patch_size, patch_size)
    height, width = get_image_size(input_image, input_data_format)
    ratio = max(height / max_height, width / max_width)
    if ratio > 1:
        height = int(np.ceil(height / ratio))
        width = int(np.ceil(width / ratio))
    num_height_tokens, num_width_tokens = _num_image_tokens((height, width), (patch_height, patch_width))
    return num_height_tokens * patch_height, num_width_tokens * patch_width
def _get_is_as_tensor_fns(tensor_type: Union[str, TensorType]) -> Tuple[Callable, Callable]: return BatchFeature()._get_is_as_tensor_fns(tensor_type)
def convert_to_tensor(array, tensor_type: Union[str, TensorType]) -> Any:
    is_tensor, as_tensor = _get_is_as_tensor_fns(tensor_type)
    if is_tensor(array): return array
    return as_tensor(array)
class PixtralImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, patch_size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BICUBIC,
    do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_convert_rgb: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"longest_edge": 1024}
        patch_size = patch_size if patch_size is not None else {"height": 16, "width": 16}
        patch_size = get_size_dict(patch_size, default_to_square=True)
        self.do_resize = do_resize
        self.size = size
        self.patch_size = patch_size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else [0.48145466, 0.4578275, 0.40821073]
        self.image_std = image_std if image_std is not None else [0.26862954, 0.26130258, 0.27577711]
        self.do_convert_rgb = do_convert_rgb
        self._valid_processor_keys = ["images", "do_resize", "size", "patch_size", "resample", "do_rescale", "rescale_factor", "do_normalize", "image_mean",
        "image_std", "do_convert_rgb", "return_tensors", "data_format", "input_data_format"]
    def resize(self, image: np.ndarray, size: Dict[str, int], patch_size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        if "longest_edge" in size: size = (size["longest_edge"], size["longest_edge"])
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("size must contain either 'longest_edge' or 'height' and 'width'.")
        if "height" in patch_size and "width" in patch_size: patch_size = (patch_size["height"], patch_size["width"])
        else: raise ValueError("patch_size must contain either 'shortest_edge' or 'height' and 'width'.")
        output_size = get_resize_output_image_size(image, size=size, patch_size=patch_size, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def preprocess(self, images: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, patch_size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_convert_rgb: bool = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> PIL.Image.Image:
        patch_size = patch_size if patch_size is not None else self.patch_size
        patch_size = get_size_dict(patch_size, default_to_square=True)
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        validate_kwargs(captured_kwargs=kwargs.keys(), valid_processor_keys=self._valid_processor_keys)
        images_list = make_list_of_images(images)
        if not valid_images(images_list[0]): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        if do_convert_rgb: images_list = [[convert_to_rgb(image) for image in images] for images in images_list]
        images_list = [[to_numpy_array(image) for image in images] for images in images_list]
        if is_scaled_image(images_list[0][0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images_list[0][0])
        batch_images = []
        batch_image_sizes = []
        for sample_images in images_list:
            images = []
            image_sizes = []
            for image in sample_images:
                if do_resize: image = self.resize(image=image, size=size, patch_size=patch_size, resample=resample, input_data_format=input_data_format)
                if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
                if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
                images.append(image)
                image_sizes.append(get_image_size(image, input_data_format))
            batch_images.append(images)
            batch_image_sizes.append(image_sizes)
        images_list = [[to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images] for images in batch_images]
        images_list = [[convert_to_tensor(image, return_tensors) for image in images] for images in images_list]
        return BatchMixFeature(data={"pixel_values": images_list, "image_sizes": batch_image_sizes}, tensor_type=None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
