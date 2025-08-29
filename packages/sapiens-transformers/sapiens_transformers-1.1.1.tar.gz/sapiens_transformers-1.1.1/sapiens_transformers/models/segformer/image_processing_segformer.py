"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import INIT_SERVICE_KWARGS, BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_torch_available, is_torch_tensor, is_vision_available, logging)
from ...utils.deprecation import deprecate_kwarg
if is_vision_available(): import PIL.Image
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class SegformerImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    @deprecate_kwarg("reduce_labels", new_name="do_reduce_labels", version="4.41.0")
    @filter_out_non_signature_kwargs(extra=INIT_SERVICE_KWARGS)
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_rescale: bool = True,
    rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_reduce_labels: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 512, "width": 512}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.do_reduce_labels = do_reduce_labels
    @classmethod
    def from_dict(cls, image_processor_dict: Dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        if "reduce_labels" in image_processor_dict: image_processor_dict["do_reduce_labels"] = image_processor_dict.pop("reduce_labels")
        return super().from_dict(image_processor_dict, **kwargs)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size: raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def reduce_label(self, label: ImageInput) -> np.ndarray:
        label = to_numpy_array(label)
        label[label == 0] = 255
        label = label - 1
        label[label == 254] = 255
        return label
    def _preprocess(self, image: ImageInput, do_reduce_labels: bool, do_resize: bool, do_rescale: bool, do_normalize: bool, size: Optional[Dict[str, int]] = None,
    resample: PILImageResampling = None, rescale_factor: Optional[float] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None):
        if do_reduce_labels: image = self.reduce_label(image)
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        return image
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_rescale: bool = None,
    rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        image = self._preprocess(image=image, do_reduce_labels=False, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
        do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, input_data_format=input_data_format)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    def _preprocess_mask(self, segmentation_map: ImageInput, do_reduce_labels: bool = None, do_resize: bool = None, size: Dict[str, int] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        segmentation_map = to_numpy_array(segmentation_map)
        if segmentation_map.ndim == 2:
            added_channel_dim = True
            segmentation_map = segmentation_map[None, ...]
            input_data_format = ChannelDimension.FIRST
        else:
            added_channel_dim = False
            if input_data_format is None: input_data_format = infer_channel_dimension_format(segmentation_map, num_channels=1)
        segmentation_map = self._preprocess(image=segmentation_map, do_reduce_labels=do_reduce_labels, do_resize=do_resize, resample=PILImageResampling.NEAREST,
        size=size, do_rescale=False, do_normalize=False, input_data_format=input_data_format)
        if added_channel_dim: segmentation_map = segmentation_map.squeeze(0)
        segmentation_map = segmentation_map.astype(np.int64)
        return segmentation_map
    def __call__(self, images, segmentation_maps=None, **kwargs): return super().__call__(images, segmentation_maps=segmentation_maps, **kwargs)
    @deprecate_kwarg("reduce_labels", new_name="do_reduce_labels", version="4.41.0")
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, segmentation_maps: Optional[ImageInput] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None,
    resample: PILImageResampling = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None,
    image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_reduce_labels: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        do_reduce_labels = do_reduce_labels if do_reduce_labels is not None else self.do_reduce_labels
        resample = resample if resample is not None else self.resample
        size = size if size is not None else self.size
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        images = make_list_of_images(images)
        if segmentation_maps is not None: segmentation_maps = make_list_of_images(segmentation_maps, expected_ndims=2)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        images = [self._preprocess_image(image=img, do_resize=do_resize, resample=resample, size=size, do_rescale=do_rescale, rescale_factor=rescale_factor,
        do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format) for img in images]
        data = {"pixel_values": images}
        if segmentation_maps is not None:
            segmentation_maps = [self._preprocess_mask(segmentation_map=segmentation_map, do_reduce_labels=do_reduce_labels, do_resize=do_resize,
            size=size, input_data_format=input_data_format) for segmentation_map in segmentation_maps]
            data["labels"] = segmentation_maps
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
