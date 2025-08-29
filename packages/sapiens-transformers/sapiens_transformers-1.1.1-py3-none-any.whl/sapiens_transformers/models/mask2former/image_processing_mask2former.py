"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
import numpy as np
from ...image_processing_utils import INIT_SERVICE_KWARGS, BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import (PaddingMode, get_resize_output_image_size, pad, rescale, resize, to_channel_dimension_format)
from ...image_utils import (ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format, is_batched, is_scaled_image,
to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, TensorType, filter_out_non_signature_kwargs, is_torch_available, is_torch_tensor, logging)
from ...utils.deprecation import deprecate_kwarg
logger = logging.get_logger(__name__)
if is_torch_available():
    import torch
    from torch import nn
def max_across_indices(values: Iterable[Any]) -> List[Any]: return [max(values_i) for values_i in zip(*values)]
def get_max_height_width(images: List[np.ndarray], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> List[int]:
    if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
    if input_data_format == ChannelDimension.FIRST: _, max_height, max_width = max_across_indices([img.shape for img in images])
    elif input_data_format == ChannelDimension.LAST: max_height, max_width, _ = max_across_indices([img.shape for img in images])
    else: raise ValueError(f"Invalid channel dimension format: {input_data_format}")
    return (max_height, max_width)
def make_pixel_mask(image: np.ndarray, output_size: Tuple[int, int], input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
    input_height, input_width = get_image_size(image, channel_dim=input_data_format)
    mask = np.zeros(output_size, dtype=np.int64)
    mask[:input_height, :input_width] = 1
    return mask
def binary_mask_to_rle(mask):
    if is_torch_tensor(mask): mask = mask.numpy()
    pixels = mask.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    runs = np.where(pixels[1:] != pixels[:-1])[0] + 1
    runs[1::2] -= runs[::2]
    return list(runs)
def convert_segmentation_to_rle(segmentation):
    segment_ids = torch.unique(segmentation)
    run_length_encodings = []
    for idx in segment_ids:
        mask = torch.where(segmentation == idx, 1, 0)
        rle = binary_mask_to_rle(mask)
        run_length_encodings.append(rle)
    return run_length_encodings
def remove_low_and_no_objects(masks, scores, labels, object_mask_threshold, num_labels):
    if not (masks.shape[0] == scores.shape[0] == labels.shape[0]): raise ValueError("mask, scores and labels must have the same shape!")
    to_keep = labels.ne(num_labels) & (scores > object_mask_threshold)
    return masks[to_keep], scores[to_keep], labels[to_keep]
def check_segment_validity(mask_labels, mask_probs, k, mask_threshold=0.5, overlap_mask_area_threshold=0.8):
    mask_k = mask_labels == k
    mask_k_area = mask_k.sum()
    original_area = (mask_probs[k] >= mask_threshold).sum()
    mask_exists = mask_k_area > 0 and original_area > 0
    if mask_exists:
        area_ratio = mask_k_area / original_area
        if not area_ratio.item() > overlap_mask_area_threshold: mask_exists = False
    return mask_exists, mask_k
def compute_segments(mask_probs, pred_scores, pred_labels, mask_threshold: float = 0.5, overlap_mask_area_threshold: float = 0.8, label_ids_to_fuse: Optional[Set[int]] = None, target_size: Tuple[int, int] = None):
    height = mask_probs.shape[1] if target_size is None else target_size[0]
    width = mask_probs.shape[2] if target_size is None else target_size[1]
    segmentation = torch.zeros((height, width), dtype=torch.int32, device=mask_probs.device)
    segments: List[Dict] = []
    if target_size is not None: mask_probs = nn.functional.interpolate(mask_probs.unsqueeze(0), size=target_size, mode="bilinear", align_corners=False)[0]
    current_segment_id = 0
    mask_probs *= pred_scores.view(-1, 1, 1)
    mask_labels = mask_probs.argmax(0)
    stuff_memory_list: Dict[str, int] = {}
    for k in range(pred_labels.shape[0]):
        pred_class = pred_labels[k].item()
        should_fuse = pred_class in label_ids_to_fuse
        mask_exists, mask_k = check_segment_validity(mask_labels, mask_probs, k, mask_threshold, overlap_mask_area_threshold)
        if mask_exists:
            if pred_class in stuff_memory_list: current_segment_id = stuff_memory_list[pred_class]
            else: current_segment_id += 1
            segmentation[mask_k] = current_segment_id
            segment_score = round(pred_scores[k].item(), 6)
            segments.append({"id": current_segment_id, "label_id": pred_class, "was_fused": should_fuse, "score": segment_score})
            if should_fuse: stuff_memory_list[pred_class] = current_segment_id
    return segmentation, segments
def convert_segmentation_map_to_binary_masks(segmentation_map: "np.ndarray", instance_id_to_semantic_id: Optional[Dict[int, int]] = None, ignore_index: Optional[int] = None, do_reduce_labels: bool = False):
    if do_reduce_labels and ignore_index is None: raise ValueError("If `do_reduce_labels` is True, `ignore_index` must be provided.")
    if do_reduce_labels: segmentation_map = np.where(segmentation_map == 0, ignore_index, segmentation_map - 1)
    all_labels = np.unique(segmentation_map)
    if ignore_index is not None: all_labels = all_labels[all_labels != ignore_index]
    binary_masks = [(segmentation_map == i) for i in all_labels]
    if binary_masks: binary_masks = np.stack(binary_masks, axis=0)
    else: binary_masks = np.zeros((0, *segmentation_map.shape))
    if instance_id_to_semantic_id is not None:
        labels = np.zeros(all_labels.shape[0])
        for label in all_labels:
            class_id = instance_id_to_semantic_id[label + 1 if do_reduce_labels else label]
            labels[all_labels == label] = class_id - 1 if do_reduce_labels else class_id
    else: labels = all_labels
    return binary_masks.astype(np.float32), labels.astype(np.int64)
def get_mask2former_resize_output_image_size(image: np.ndarray, size: Union[int, Tuple[int, int], List[int], Tuple[int]], max_size: Optional[int] = None, size_divisor: int = 0,
default_to_square: bool = True, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    output_size = get_resize_output_image_size(input_image=image, size=size, default_to_square=default_to_square, max_size=max_size, input_data_format=input_data_format)
    if size_divisor > 0:
        height, width = output_size
        height = int(math.ceil(height / size_divisor) * size_divisor)
        width = int(math.ceil(width / size_divisor) * size_divisor)
        output_size = (height, width)
    return output_size
class Mask2FormerImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "pixel_mask"]
    @deprecate_kwarg("reduce_labels", new_name="do_reduce_labels", version="4.44.0")
    @deprecate_kwarg("size_divisibility", new_name="size_divisor", version="4.41.0")
    @deprecate_kwarg("max_size", version="4.27.0", warn_if_greater_or_equal_version=True)
    @filter_out_non_signature_kwargs(extra=["max_size", *INIT_SERVICE_KWARGS])
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, size_divisor: int = 32, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_rescale: bool = True, rescale_factor: float = 1 / 255, do_normalize: bool = True, image_mean: Union[float, List[float]] = None, image_std: Union[float, List[float]] = None,
    ignore_index: Optional[int] = None, do_reduce_labels: bool = False, num_labels: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self._max_size = kwargs.pop("max_size", 1333)
        size = size if size is not None else {"shortest_edge": 800, "longest_edge": self._max_size}
        size = get_size_dict(size, max_size=self._max_size, default_to_square=False)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.size_divisor = size_divisor
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.ignore_index = ignore_index
        self.do_reduce_labels = do_reduce_labels
        self.num_labels = num_labels
    @classmethod
    def from_dict(cls, image_processor_dict: Dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        if "max_size" in kwargs: image_processor_dict["max_size"] = kwargs.pop("max_size")
        if "size_divisibility" in kwargs: image_processor_dict["size_divisor"] = kwargs.pop("size_divisibility")
        if "reduce_labels" in image_processor_dict: image_processor_dict["do_reduce_labels"] = image_processor_dict.pop("reduce_labels")
        return super().from_dict(image_processor_dict, **kwargs)
    def to_dict(self) -> Dict[str, Any]:
        image_processor_dict = super().to_dict()
        image_processor_dict.pop("_max_size", None)
        return image_processor_dict
    @deprecate_kwarg("max_size", version="4.27.0", warn_if_greater_or_equal_version=True)
    def resize(self, image: np.ndarray, size: Dict[str, int], size_divisor: int = 0, resample: PILImageResampling = PILImageResampling.BILINEAR, data_format=None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        max_size = kwargs.pop("max_size", None)
        size = get_size_dict(size, max_size=max_size, default_to_square=False)
        if "shortest_edge" in size and "longest_edge" in size: size, max_size = size["shortest_edge"], size["longest_edge"]
        elif "height" in size and "width" in size:
            size = (size["height"], size["width"])
            max_size = None
        else: raise ValueError(f"Size must contain 'height' and 'width' keys or 'shortest_edge' and 'longest_edge' keys. Got {size.keys()}.")
        size = get_mask2former_resize_output_image_size(image=image, size=size, max_size=max_size, size_divisor=size_divisor, default_to_square=False, input_data_format=input_data_format)
        image = resize(image, size=size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
        return image
    def rescale(self, image: np.ndarray, rescale_factor: float, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray: return rescale(image, rescale_factor, data_format=data_format, input_data_format=input_data_format)
    def convert_segmentation_map_to_binary_masks(self, segmentation_map: "np.ndarray", instance_id_to_semantic_id: Optional[Dict[int, int]] = None, ignore_index: Optional[int] = None, do_reduce_labels: bool = False):
        do_reduce_labels = do_reduce_labels if do_reduce_labels is not None else self.do_reduce_labels
        ignore_index = ignore_index if ignore_index is not None else self.ignore_index
        return convert_segmentation_map_to_binary_masks(segmentation_map=segmentation_map, instance_id_to_semantic_id=instance_id_to_semantic_id, ignore_index=ignore_index, do_reduce_labels=do_reduce_labels)
    def __call__(self, images, segmentation_maps=None, **kwargs) -> BatchFeature: return self.preprocess(images, segmentation_maps=segmentation_maps, **kwargs)
    def _preprocess(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, size_divisor: int = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        if do_resize: image = self.resize(image, size=size, size_divisor=size_divisor, resample=resample, input_data_format=input_data_format)
        if do_rescale: image = self.rescale(image, rescale_factor=rescale_factor, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        return image
    def _preprocess_image(self, image: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, size_divisor: int = None, resample: PILImageResampling = None,
    do_rescale: bool = None, rescale_factor: float = None, do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        image = self._preprocess(image=image, do_resize=do_resize, size=size, size_divisor=size_divisor, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
        do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, input_data_format=input_data_format)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    def _preprocess_mask(self, segmentation_map: ImageInput, do_resize: bool = None, size: Dict[str, int] = None, size_divisor: int = 0, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        segmentation_map = to_numpy_array(segmentation_map)
        if segmentation_map.ndim == 2:
            added_channel_dim = True
            segmentation_map = segmentation_map[None, ...]
            input_data_format = ChannelDimension.FIRST
        else:
            added_channel_dim = False
            if input_data_format is None: input_data_format = infer_channel_dimension_format(segmentation_map)
        segmentation_map = self._preprocess(image=segmentation_map, do_resize=do_resize, resample=PILImageResampling.NEAREST, size=size, size_divisor=size_divisor,
        do_rescale=False, do_normalize=False, input_data_format=input_data_format)
        if added_channel_dim: segmentation_map = segmentation_map.squeeze(0)
        return segmentation_map
    @deprecate_kwarg("reduce_labels", new_name="do_reduce_labels", version="4.44.0")
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, segmentation_maps: Optional[ImageInput] = None, instance_id_to_semantic_id: Optional[Dict[int, int]] = None, do_resize: Optional[bool] = None,
    size: Optional[Dict[str, int]] = None, size_divisor: Optional[int] = None, resample: PILImageResampling = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None,
    do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, ignore_index: Optional[int] = None,
    do_reduce_labels: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> BatchFeature:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False, max_size=self._max_size)
        size_divisor = size_divisor if size_divisor is not None else self.size_divisor
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        ignore_index = ignore_index if ignore_index is not None else self.ignore_index
        do_reduce_labels = do_reduce_labels if do_reduce_labels is not None else self.do_reduce_labels
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        if segmentation_maps is not None and not valid_images(segmentation_maps): raise ValueError("Invalid segmentation map type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if not is_batched(images):
            images = [images]
            segmentation_maps = [segmentation_maps] if segmentation_maps is not None else None
        if segmentation_maps is not None and len(images) != len(segmentation_maps): raise ValueError("Images and segmentation maps must have the same length.")
        images = [self._preprocess_image(image, do_resize=do_resize, size=size, size_divisor=size_divisor, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
        do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, data_format=data_format, input_data_format=input_data_format) for image in images]
        if segmentation_maps is not None: segmentation_maps = [self._preprocess_mask(segmentation_map, do_resize, size, size_divisor, input_data_format=input_data_format) for segmentation_map in segmentation_maps]
        encoded_inputs = self.encode_inputs(images, segmentation_maps, instance_id_to_semantic_id, ignore_index, do_reduce_labels, return_tensors, input_data_format=data_format)
        return encoded_inputs
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
        padded_images = [self._pad_image(image, pad_size, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format) for image in images]
        data = {"pixel_values": padded_images}
        if return_pixel_mask:
            masks = [make_pixel_mask(image=image, output_size=pad_size, input_data_format=input_data_format) for image in images]
            data["pixel_mask"] = masks
        return BatchFeature(data=data, tensor_type=return_tensors)
    def encode_inputs(self, pixel_values_list: List[ImageInput], segmentation_maps: ImageInput = None, instance_id_to_semantic_id: Optional[Union[List[Dict[int, int]], Dict[int, int]]] = None,
    ignore_index: Optional[int] = None, do_reduce_labels: bool = False, return_tensors: Optional[Union[str, TensorType]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        ignore_index = self.ignore_index if ignore_index is None else ignore_index
        do_reduce_labels = self.do_reduce_labels if do_reduce_labels is None else do_reduce_labels
        pixel_values_list = [to_numpy_array(pixel_values) for pixel_values in pixel_values_list]
        if input_data_format is None: input_data_format = infer_channel_dimension_format(pixel_values_list[0])
        encoded_inputs = self.pad(pixel_values_list, return_tensors=return_tensors, input_data_format=input_data_format)
        if segmentation_maps is not None:
            mask_labels = []
            class_labels = []
            pad_size = get_max_height_width(pixel_values_list, input_data_format=input_data_format)
            for idx, segmentation_map in enumerate(segmentation_maps):
                segmentation_map = to_numpy_array(segmentation_map)
                if isinstance(instance_id_to_semantic_id, list): instance_id = instance_id_to_semantic_id[idx]
                else: instance_id = instance_id_to_semantic_id
                masks, classes = self.convert_segmentation_map_to_binary_masks(segmentation_map, instance_id, ignore_index=ignore_index, do_reduce_labels=do_reduce_labels)
                if masks.shape[0] > 0:
                    masks = [mask[None, ...] for mask in masks]
                    masks = [self._pad_image(image=mask, output_size=pad_size, constant_values=ignore_index) for mask in masks]
                    masks = np.concatenate(masks, axis=0)
                else: masks = np.zeros((0, *pad_size), dtype=np.float32)
                mask_labels.append(torch.from_numpy(masks))
                class_labels.append(torch.from_numpy(classes))
            encoded_inputs["mask_labels"] = mask_labels
            encoded_inputs["class_labels"] = class_labels
        return encoded_inputs
    def post_process_semantic_segmentation(self, outputs, target_sizes: Optional[List[Tuple[int, int]]] = None) -> "torch.Tensor":
        class_queries_logits = outputs.class_queries_logits
        masks_queries_logits = outputs.masks_queries_logits
        masks_queries_logits = torch.nn.functional.interpolate(masks_queries_logits, size=(384, 384), mode="bilinear", align_corners=False)
        masks_classes = class_queries_logits.softmax(dim=-1)[..., :-1]
        masks_probs = masks_queries_logits.sigmoid()
        segmentation = torch.einsum("bqc, bqhw -> bchw", masks_classes, masks_probs)
        batch_size = class_queries_logits.shape[0]
        if target_sizes is not None:
            if batch_size != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
            semantic_segmentation = []
            for idx in range(batch_size):
                resized_logits = torch.nn.functional.interpolate(segmentation[idx].unsqueeze(dim=0), size=target_sizes[idx], mode="bilinear", align_corners=False)
                semantic_map = resized_logits[0].argmax(dim=0)
                semantic_segmentation.append(semantic_map)
        else:
            semantic_segmentation = segmentation.argmax(dim=1)
            semantic_segmentation = [semantic_segmentation[i] for i in range(semantic_segmentation.shape[0])]
        return semantic_segmentation
    def post_process_instance_segmentation(self, outputs, threshold: float = 0.5, mask_threshold: float = 0.5, overlap_mask_area_threshold: float = 0.8,
    target_sizes: Optional[List[Tuple[int, int]]] = None, return_coco_annotation: Optional[bool] = False, return_binary_maps: Optional[bool] = False) -> List[Dict]:
        if return_coco_annotation and return_binary_maps: raise ValueError("return_coco_annotation and return_binary_maps can not be both set to True.")
        class_queries_logits = outputs.class_queries_logits
        masks_queries_logits = outputs.masks_queries_logits
        masks_queries_logits = torch.nn.functional.interpolate(masks_queries_logits, size=(384, 384), mode="bilinear", align_corners=False)
        device = masks_queries_logits.device
        num_classes = class_queries_logits.shape[-1] - 1
        num_queries = class_queries_logits.shape[-2]
        results: List[Dict[str, TensorType]] = []
        for i in range(class_queries_logits.shape[0]):
            mask_pred = masks_queries_logits[i]
            mask_cls = class_queries_logits[i]
            scores = torch.nn.functional.softmax(mask_cls, dim=-1)[:, :-1]
            labels = torch.arange(num_classes, device=device).unsqueeze(0).repeat(num_queries, 1).flatten(0, 1)
            scores_per_image, topk_indices = scores.flatten(0, 1).topk(num_queries, sorted=False)
            labels_per_image = labels[topk_indices]
            topk_indices = torch.div(topk_indices, num_classes, rounding_mode="floor")
            mask_pred = mask_pred[topk_indices]
            pred_masks = (mask_pred > 0).float()
            mask_scores_per_image = (mask_pred.sigmoid().flatten(1) * pred_masks.flatten(1)).sum(1) / (pred_masks.flatten(1).sum(1) + 1e-6)
            pred_scores = scores_per_image * mask_scores_per_image
            pred_classes = labels_per_image
            segmentation = torch.zeros((384, 384)) - 1
            if target_sizes is not None:
                segmentation = torch.zeros(target_sizes[i]) - 1
                pred_masks = torch.nn.functional.interpolate(pred_masks.unsqueeze(0), size=target_sizes[i], mode="nearest")[0]
            instance_maps, segments = [], []
            current_segment_id = 0
            for j in range(num_queries):
                score = pred_scores[j].item()
                if not torch.all(pred_masks[j] == 0) and score >= threshold:
                    segmentation[pred_masks[j] == 1] = current_segment_id
                    segments.append({"id": current_segment_id, "label_id": pred_classes[j].item(), "was_fused": False, "score": round(score, 6)})
                    current_segment_id += 1
                    instance_maps.append(pred_masks[j])
            if return_coco_annotation: segmentation = convert_segmentation_to_rle(segmentation)
            if return_binary_maps and len(instance_maps) != 0: segmentation = torch.stack(instance_maps, dim=0)
            results.append({"segmentation": segmentation, "segments_info": segments})
        return results
    def post_process_panoptic_segmentation(self, outputs, threshold: float = 0.5, mask_threshold: float = 0.5, overlap_mask_area_threshold: float = 0.8,
    label_ids_to_fuse: Optional[Set[int]] = None, target_sizes: Optional[List[Tuple[int, int]]] = None) -> List[Dict]:
        if label_ids_to_fuse is None:
            logger.warning("`label_ids_to_fuse` unset. No instance will be fused.")
            label_ids_to_fuse = set()
        class_queries_logits = outputs.class_queries_logits
        masks_queries_logits = outputs.masks_queries_logits
        masks_queries_logits = torch.nn.functional.interpolate(masks_queries_logits, size=(384, 384), mode="bilinear", align_corners=False)
        batch_size = class_queries_logits.shape[0]
        num_labels = class_queries_logits.shape[-1] - 1
        mask_probs = masks_queries_logits.sigmoid()
        pred_scores, pred_labels = nn.functional.softmax(class_queries_logits, dim=-1).max(-1)
        results: List[Dict[str, TensorType]] = []
        for i in range(batch_size):
            mask_probs_item, pred_scores_item, pred_labels_item = remove_low_and_no_objects(mask_probs[i], pred_scores[i], pred_labels[i], threshold, num_labels)
            if mask_probs_item.shape[0] <= 0:
                height, width = target_sizes[i] if target_sizes is not None else mask_probs_item.shape[1:]
                segmentation = torch.zeros((height, width)) - 1
                results.append({"segmentation": segmentation, "segments_info": []})
                continue
            target_size = target_sizes[i] if target_sizes is not None else None
            segmentation, segments = compute_segments(mask_probs=mask_probs_item, pred_scores=pred_scores_item, pred_labels=pred_labels_item, mask_threshold=mask_threshold,
            overlap_mask_area_threshold=overlap_mask_area_threshold, label_ids_to_fuse=label_ids_to_fuse, target_size=target_size)
            results.append({"segmentation": segmentation, "segments_info": segments})
        return results
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
