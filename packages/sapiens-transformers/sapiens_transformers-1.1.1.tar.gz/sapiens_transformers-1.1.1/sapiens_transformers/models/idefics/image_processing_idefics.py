"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Callable, Dict, List, Optional, Union
from PIL import Image
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, make_list_of_images, to_numpy_array, valid_images)
from ...utils import TensorType, is_torch_available
IDEFICS_STANDARD_MEAN = [0.48145466, 0.4578275, 0.40821073]
IDEFICS_STANDARD_STD = [0.26862954, 0.26130258, 0.27577711]
def convert_to_rgb(image):
    if image.mode == "RGB": return image
    image_rgba = image.convert("RGBA")
    background = Image.new("RGBA", image_rgba.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, image_rgba)
    alpha_composite = alpha_composite.convert("RGB")
    return alpha_composite
class IdeficsImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, image_size: int = 224, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    image_num_channels: Optional[int] = 3, **kwargs) -> None:
        super().__init__(**kwargs)
        self.image_size = image_size
        self.image_num_channels = image_num_channels
        self.image_mean = image_mean
        self.image_std = image_std
    def preprocess(self, images: ImageInput, image_num_channels: Optional[int] = 3, image_size: Optional[Dict[str, int]] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, transform: Callable = None, return_tensors: Optional[Union[str, TensorType]] = TensorType.PYTORCH, **kwargs) -> TensorType:
        image_size = image_size if image_size is not None else self.image_size
        image_num_channels = image_num_channels if image_num_channels is not None else self.image_num_channels
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = (image_size, image_size)
        if isinstance(images, list) and len(images) == 0: return []
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if transform is not None:
            if not is_torch_available(): raise ImportError("To pass in `transform` torch must be installed")
            import torch
            images = [transform(x) for x in images]
            return torch.stack(images)
        images = [convert_to_rgb(x) for x in images]
        images = [to_numpy_array(x) for x in images]
        images = [resize(x, size, resample=PILImageResampling.BICUBIC) for x in images]
        images = [self.rescale(image=image, scale=1 / 255) for image in images]
        images = [self.normalize(x, mean=image_mean, std=image_std) for x in images]
        images = [to_channel_dimension_format(x, ChannelDimension.FIRST) for x in images]
        images = BatchFeature(data={"pixel_values": images}, tensor_type=return_tensors)["pixel_values"]
        return images
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
