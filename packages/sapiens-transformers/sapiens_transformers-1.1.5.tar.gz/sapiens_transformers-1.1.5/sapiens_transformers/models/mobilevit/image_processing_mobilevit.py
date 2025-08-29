"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import flip_channel_order, get_resize_output_image_size, resize, to_channel_dimension_format
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array,
valid_images, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_torch_available, is_torch_tensor, is_vision_available, logging)
if is_vision_available(): import PIL
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class MobileViTImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR, do_rescale: bool = True,
    rescale_factor: Union[int, float] = 1 / 255, do_center_crop: bool = True, crop_size: Dict[str, int] = None, do_flip_channel_order: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"shortest_edge": 224}
        size = get_size_dict(size, default_to_square=False)
        crop_size = crop_size if crop_size is not None else {"height": 256, "width": 256}
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.do_flip_channel_order = do_flip_channel_order
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        default_to_square = True
        if "shortest_edge" in size:
            size = size["shortest_edge"]
            default_to_square = False
        elif "height" in size and "width" in size: size = (size["height"], size["width"])
        else: raise ValueError("Size must contain either 'shortest_edge' or 'height' and 'width'.")
        output_size = get_resize_output_image_size(image, size=size, default_to_square=default_to_square, input_data_format=input_data_format)
        return resize(image, size=output_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def flip_channel_order(self, image: np.ndarray, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray: return flip_channel_order(image, data_format=data_format, input_data_format=input_data_format)
    def __call__(self, images, segmentation_maps=None, **kwargs): return super().__call__(images, segmentation_maps=segmentation_maps, **kwargs)
    def _preprocess(self, image: ImageInput, do_resize: bool, do_rescale: bool, do_center_crop: bool, do_flip_channel_order: bool, size: Optional[Dict[str, int]] = None,
    resample: PILImageResampling = None, rescale_factor: Optional[float] = None, crop_size: Optional[Dict[str, int]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_center_crop: image = self.center_crop(image=image, size=crop_size, input_data_format=input_data_format)
        if do_flip_channel_order: image = self.flip_channel_order(image, input_data_format=input_data_format)
        return image
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_rescale: bool = None,
    rescale_factor: float = None, do_center_crop: bool = None, crop_size: Dict[str, int] = None, do_flip_channel_order: bool = None, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        image = self._preprocess(image=image, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor, do_center_crop=do_center_crop,
        crop_size=crop_size, do_flip_channel_order=do_flip_channel_order, input_data_format=input_data_format)
        image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    def _preprocess_mask(self, segmentation_map: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, do_center_crop: bool = None, crop_size: Dict[str, int] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        segmentation_map = to_numpy_array(segmentation_map)
        if segmentation_map.ndim == 2:
            added_channel_dim = True
            segmentation_map = segmentation_map[None, ...]
            input_data_format = ChannelDimension.FIRST
        else:
            added_channel_dim = False
            if input_data_format is None: input_data_format = infer_channel_dimension_format(segmentation_map, num_channels=1)
        segmentation_map = self._preprocess(image=segmentation_map, do_resize=do_resize, size=size, resample=PILImageResampling.NEAREST, do_rescale=False,
        do_center_crop=do_center_crop, crop_size=crop_size, do_flip_channel_order=False, input_data_format=input_data_format)
        if added_channel_dim: segmentation_map = segmentation_map.squeeze(0)
        segmentation_map = segmentation_map.astype(np.int64)
        return segmentation_map
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, segmentation_maps: Optional[ImageInput] = None, do_resize: bool = None, size: Dict[str, int] = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_center_crop: bool = None, crop_size: Dict[str, int] = None, do_flip_channel_order: bool = None,
    return_tensors: Optional[Union[str, TensorType]] = None, data_format: ChannelDimension = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        do_flip_channel_order = (do_flip_channel_order if do_flip_channel_order is not None else self.do_flip_channel_order)
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        crop_size = crop_size if crop_size is not None else self.crop_size
        crop_size = get_size_dict(crop_size, param_name="crop_size")
        images = make_list_of_images(images)
        if segmentation_maps is not None: segmentation_maps = make_list_of_images(segmentation_maps, expected_ndims=2)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if segmentation_maps is not None and not valid_images(segmentation_maps): raise ValueError("Invalid segmentation map type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        images = [self._preprocess_image(image=img, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor, do_center_crop=do_center_crop,
        crop_size=crop_size, do_flip_channel_order=do_flip_channel_order, data_format=data_format, input_data_format=input_data_format) for img in images]
        data = {"pixel_values": images}
        if segmentation_maps is not None:
            segmentation_maps = [self._preprocess_mask(segmentation_map=segmentation_map, do_resize=do_resize, size=size, do_center_crop=do_center_crop,
            crop_size=crop_size, input_data_format=input_data_format) for segmentation_map in segmentation_maps]
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
