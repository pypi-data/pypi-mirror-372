"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import functools
from typing import Dict, List, Optional, Union
from ...image_processing_base import BatchFeature
from ...image_processing_utils import get_size_dict
from ...image_processing_utils_fast import BaseImageProcessorFast, SizeDict
from ...image_transforms import FusedRescaleNormalize, NumpyToTensor, Rescale
from ...image_utils import (IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ChannelDimension, ImageInput, ImageType, PILImageResampling, get_image_type,
make_list_of_images, pil_torch_interpolation_mapping)
from ...utils import TensorType, logging
from ...utils.import_utils import is_torch_available, is_torchvision_available
logger = logging.get_logger(__name__)
if is_torch_available(): import torch
if is_torchvision_available(): from torchvision.transforms import Compose, Normalize, PILToTensor, Resize
class ViTImageProcessorFast(BaseImageProcessorFast):
    model_input_names = ["pixel_values"]
    _transform_params = ["do_resize", "do_rescale", "do_normalize", "size", "resample", "rescale_factor", "image_mean", "image_std", "image_type"]
    def __init__(self, do_resize: bool = True, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_rescale: bool = True,
    rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 224, "width": 224}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.do_rescale = do_rescale
        self.do_normalize = do_normalize
        self.size = size
        self.resample = resample
        self.rescale_factor = rescale_factor
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
    def _build_transforms(self, do_resize: bool, size: Dict[str, int], resample: PILImageResampling, do_rescale: bool, rescale_factor: float, do_normalize: bool, image_mean: Union[float, List[float]],
    image_std: Union[float, List[float]], image_type: ImageType) -> "Compose":
        transforms = []
        if image_type == ImageType.PIL: transforms.append(PILToTensor())
        elif image_type == ImageType.NUMPY: transforms.append(NumpyToTensor())
        if do_resize: transforms.append(Resize((size["height"], size["width"]), interpolation=pil_torch_interpolation_mapping[resample]))
        if do_rescale and do_normalize: transforms.append(FusedRescaleNormalize(image_mean, image_std, rescale_factor=rescale_factor))
        elif do_rescale: transforms.append(Rescale(rescale_factor=rescale_factor))
        elif do_normalize: transforms.append(Normalize(image_mean, image_std))
        return Compose(transforms)
    @functools.lru_cache(maxsize=1)
    def _validate_input_arguments(self, return_tensors: Union[str, TensorType], do_resize: bool, size: Dict[str, int], resample: PILImageResampling, do_rescale: bool,
    rescale_factor: float, do_normalize: bool, image_mean: Union[float, List[float]], image_std: Union[float, List[float]], data_format: Union[str, ChannelDimension], image_type: ImageType):
        if return_tensors != "pt": raise ValueError("Only returning PyTorch tensors is currently supported.")
        if data_format != ChannelDimension.FIRST: raise ValueError("Only channel first data format is currently supported.")
        if do_resize and None in (size, resample): raise ValueError("Size and resample must be specified if do_resize is True.")
        if do_rescale and rescale_factor is None: raise ValueError("Rescale factor must be specified if do_rescale is True.")
        if do_normalize and None in (image_mean, image_std): raise ValueError("Image mean and standard deviation must be specified if do_normalize is True.")
    def preprocess(self, images: ImageInput, do_resize: Optional[bool] = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_rescale: Optional[bool] = None,
    rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    return_tensors: Optional[Union[str, TensorType]] = "pt", data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs):
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        resample = resample if resample is not None else self.resample
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        size = SizeDict(**size)
        image_mean = tuple(image_mean) if isinstance(image_mean, list) else image_mean
        image_std = tuple(image_std) if isinstance(image_std, list) else image_std
        images = make_list_of_images(images)
        image_type = get_image_type(images[0])
        if image_type not in [ImageType.PIL, ImageType.TORCH, ImageType.NUMPY]: raise ValueError(f"Unsupported input image type {image_type}")
        self._validate_input_arguments(do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize,
        image_mean=image_mean, image_std=image_std, return_tensors=return_tensors, data_format=data_format, image_type=image_type)
        transforms = self.get_transforms(do_resize=do_resize, do_rescale=do_rescale, do_normalize=do_normalize, size=size, resample=resample, rescale_factor=rescale_factor,
        image_mean=image_mean, image_std=image_std, image_type=image_type)
        transformed_images = [transforms(image) for image in images]
        data = {"pixel_values": torch.stack(transformed_images, dim=0)}
        return BatchFeature(data, tensor_type=return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
