"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import pad, resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, is_torch_available, is_torch_tensor, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_torch_available(): import torch
if is_vision_available(): import PIL
logger = logging.get_logger(__name__)
def get_resize_output_image_size(input_image: np.ndarray, output_size: Union[int, Iterable[int]], keep_aspect_ratio: bool, multiple: int, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    def constrain_to_multiple_of(val, multiple, min_val=0, max_val=None):
        x = round(val / multiple) * multiple
        if max_val is not None and x > max_val: x = math.floor(val / multiple) * multiple
        if x < min_val: x = math.ceil(val / multiple) * multiple
        return x
    output_size = (output_size, output_size) if isinstance(output_size, int) else output_size
    input_height, input_width = get_image_size(input_image, input_data_format)
    output_height, output_width = output_size
    scale_height = output_height / input_height
    scale_width = output_width / input_width
    if keep_aspect_ratio:
        if abs(1 - scale_width) < abs(1 - scale_height): scale_height = scale_width
        else: scale_width = scale_height
    new_height = constrain_to_multiple_of(scale_height * input_height, multiple=multiple)
    new_width = constrain_to_multiple_of(scale_width * input_width, multiple=multiple)
    return (new_height, new_width)
class DPTImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BICUBIC, keep_aspect_ratio: bool = False,
    ensure_multiple_of: int = 1, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = False, size_divisor: int = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 384, "width": 384}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.size = size
        self.keep_aspect_ratio = keep_aspect_ratio
        self.ensure_multiple_of = ensure_multiple_of
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
        self.size_divisor = size_divisor
    def resize(self, image: np.ndarray, size: Dict[str, int], keep_aspect_ratio: bool = False, ensure_multiple_of: int = 1, resample: PILImageResampling = PILImageResampling.BICUBIC,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The size dictionary must contain the keys 'height' and 'width'. Got {size.keys()}")
        output_size = get_resize_output_image_size(image, output_size=(size["height"], size["width"]), keep_aspect_ratio=keep_aspect_ratio, multiple=ensure_multiple_of, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def pad_image(self, image: np.array, size_divisor: int, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        def _get_pad(size, size_divisor):
            new_size = math.ceil(size / size_divisor) * size_divisor
            pad_size = new_size - size
            pad_size_left = pad_size // 2
            pad_size_right = pad_size - pad_size_left
            return pad_size_left, pad_size_right
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        height, width = get_image_size(image, input_data_format)
        pad_size_left, pad_size_right = _get_pad(height, size_divisor)
        pad_size_top, pad_size_bottom = _get_pad(width, size_divisor)
        return pad(image, ((pad_size_left, pad_size_right), (pad_size_top, pad_size_bottom)), data_format=data_format)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: bool = None, size: int = None, keep_aspect_ratio: bool = None, ensure_multiple_of: int = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_pad: bool = None, size_divisor: int = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        keep_aspect_ratio = keep_aspect_ratio if keep_aspect_ratio is not None else self.keep_aspect_ratio
        ensure_multiple_of = ensure_multiple_of if ensure_multiple_of is not None else self.ensure_multiple_of
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        size_divisor = size_divisor if size_divisor is not None else self.size_divisor
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_pad=do_pad, size_divisibility=size_divisor, do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image=image, size=size, resample=resample, keep_aspect_ratio=keep_aspect_ratio, ensure_multiple_of=ensure_multiple_of, input_data_format=input_data_format) for image in images]
        if do_rescale:images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize:images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        if do_pad:images = [self.pad_image(image=image, size_divisor=size_divisor, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        data = {"pixel_values": images}
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_semantic_segmentation(self, outputs, target_sizes: List[Tuple] = None):
        logits = outputs.logits
        if target_sizes is not None:
            if len(logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
            if is_torch_tensor(target_sizes): target_sizes = target_sizes.numpy()
            semantic_segmentation = []
            for idx in range(len(logits)):
                resized_logits = torch.nn.functional.interpolate(logits[idx].unsqueeze(dim=0), size=target_sizes[idx], mode="bilinear", align_corners=False)
                semantic_map = resized_logits[0].argmax(dim=0)
                semantic_segmentation.append(semantic_map)
        else:
            semantic_segmentation = logits.argmax(dim=1)
            semantic_segmentation = [semantic_segmentation[i] for i in range(semantic_segmentation.shape[0])]
        return semantic_segmentation
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
