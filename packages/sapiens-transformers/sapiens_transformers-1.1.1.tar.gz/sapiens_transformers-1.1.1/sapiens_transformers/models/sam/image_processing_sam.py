"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from copy import deepcopy
from itertools import product
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import convert_to_rgb, pad, resize, to_channel_dimension_format
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_tf_available, is_torch_available, is_torchvision_available, logging, requires_backends)
if is_torch_available():
    import torch
    import torch.nn.functional as F
if is_torchvision_available(): from torchvision.ops.boxes import batched_nms
if is_tf_available():
    import tensorflow as tf
    from tensorflow.experimental import numpy as tnp
    from ...tf_utils import flatten, shape_list
logger = logging.get_logger(__name__)
class SamImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize: bool = True, size: Dict[str, int] = None, mask_size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: bool = True, pad_size: int = None, mask_pad_size: int = None, do_convert_rgb: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"longest_edge": 1024}
        size = get_size_dict(max_size=size, default_to_square=False) if not isinstance(size, dict) else size
        pad_size = pad_size if pad_size is not None else {"height": 1024, "width": 1024}
        pad_size = get_size_dict(pad_size, default_to_square=True)
        mask_size = mask_size if mask_size is not None else {"longest_edge": 256}
        mask_size = (get_size_dict(max_size=mask_size, default_to_square=False) if not isinstance(mask_size, dict) else mask_size)
        mask_pad_size = mask_pad_size if mask_pad_size is not None else {"height": 256, "width": 256}
        mask_pad_size = get_size_dict(mask_pad_size, default_to_square=True)
        self.do_resize = do_resize
        self.size = size
        self.mask_size = mask_size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.do_pad = do_pad
        self.pad_size = pad_size
        self.mask_pad_size = mask_pad_size
        self.do_convert_rgb = do_convert_rgb
    def pad_image(self, image: np.ndarray, pad_size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        output_height, output_width = pad_size["height"], pad_size["width"]
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        pad_width = output_width - input_width
        pad_height = output_height - input_height
        padded_image = pad(image, ((0, pad_height), (0, pad_width)), data_format=data_format, input_data_format=input_data_format, **kwargs)
        return padded_image
    def _get_preprocess_shape(self, old_shape: Tuple[int, int], longest_edge: int):
        oldh, oldw = old_shape
        scale = longest_edge * 1.0 / max(oldh, oldw)
        newh, neww = oldh * scale, oldw * scale
        newh = int(newh + 0.5)
        neww = int(neww + 0.5)
        return (newh, neww)
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size)
        if "longest_edge" not in size: raise ValueError(f"The `size` dictionary must contain the key `longest_edge`. Got {size.keys()}")
        input_size = get_image_size(image, channel_dim=input_data_format)
        output_height, output_width = self._get_preprocess_shape(input_size, size["longest_edge"])
        return resize(image, size=(output_height, output_width), resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def _preprocess(self, image: ImageInput, do_resize: bool, do_rescale: bool, do_normalize: bool, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = None,
    rescale_factor: Optional[float] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_pad: Optional[bool] = None, pad_size: Optional[Dict[str, int]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        if do_resize: image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
        reshaped_input_size = get_image_size(image, channel_dim=input_data_format)
        if do_rescale: image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_normalize: image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        if do_pad: image = self.pad_image(image=image, pad_size=pad_size, input_data_format=input_data_format)
        return image, reshaped_input_size
    def _preprocess_image(self, image: ImageInput, do_resize: Optional[bool] = None, size: Dict[str, int] = None, resample: PILImageResampling = None, do_rescale: bool = None,
    rescale_factor: Optional[float] = None, do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    do_pad: Optional[bool] = None, pad_size: Optional[Dict[str, int]] = None, do_convert_rgb: Optional[bool] = None, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
        image = to_numpy_array(image)
        if do_convert_rgb: image = convert_to_rgb(image)
        image = to_numpy_array(image)
        if is_scaled_image(image) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(image)
        original_size = get_image_size(image, channel_dim=input_data_format)
        image, reshaped_input_size = self._preprocess(image=image, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale, rescale_factor=rescale_factor,
        do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_pad=do_pad, pad_size=pad_size, input_data_format=input_data_format)
        if data_format is not None: image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image, original_size, reshaped_input_size
    def _preprocess_mask(self, segmentation_map: ImageInput, do_resize: Optional[bool] = None, mask_size: Dict[str, int] = None, do_pad: Optional[bool] = None,
    mask_pad_size: Optional[Dict[str, int]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray:
        segmentation_map = to_numpy_array(segmentation_map)
        if segmentation_map.ndim == 2:
            added_channel_dim = True
            segmentation_map = segmentation_map[None, ...]
            input_data_format = ChannelDimension.FIRST
        else:
            added_channel_dim = False
            if input_data_format is None: input_data_format = infer_channel_dimension_format(segmentation_map, num_channels=1)
        original_size = get_image_size(segmentation_map, channel_dim=input_data_format)
        segmentation_map, _ = self._preprocess(image=segmentation_map, do_resize=do_resize, size=mask_size, resample=PILImageResampling.NEAREST, do_rescale=False,
        do_normalize=False, do_pad=do_pad, pad_size=mask_pad_size, input_data_format=input_data_format)
        if added_channel_dim: segmentation_map = segmentation_map.squeeze(0)
        segmentation_map = segmentation_map.astype(np.int64)
        return segmentation_map, original_size
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, segmentation_maps: Optional[ImageInput] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None,
    mask_size: Optional[Dict[str, int]] = None, resample: Optional["PILImageResampling"] = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[Union[int, float]] = None,
    do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None,
    pad_size: Optional[Dict[str, int]] = None, mask_pad_size: Optional[Dict[str, int]] = None, do_convert_rgb: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: ChannelDimension = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(max_size=size, default_to_square=False) if not isinstance(size, dict) else size
        mask_size = mask_size if mask_size is not None else self.mask_size
        mask_size = (get_size_dict(max_size=mask_size, default_to_square=False) if not isinstance(mask_size, dict) else mask_size)
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        pad_size = pad_size if pad_size is not None else self.pad_size
        pad_size = get_size_dict(pad_size, default_to_square=True)
        mask_pad_size = mask_pad_size if mask_pad_size is not None else self.mask_pad_size
        mask_pad_size = get_size_dict(mask_pad_size, default_to_square=True)
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        if segmentation_maps is not None:
            segmentation_maps = make_list_of_images(segmentation_maps, expected_ndims=2)
            if not valid_images(segmentation_maps): raise ValueError("Invalid segmentation map type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_pad=do_pad, size_divisibility=pad_size, do_resize=do_resize, size=size, resample=resample)
        images, original_sizes, reshaped_input_sizes = zip(*(self._preprocess_image(image=img, do_resize=do_resize, size=size, resample=resample, do_rescale=do_rescale,
        rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, do_pad=do_pad, pad_size=pad_size, do_convert_rgb=do_convert_rgb,
        data_format=data_format, input_data_format=input_data_format) for img in images))
        data = {"pixel_values": images, "original_sizes": original_sizes, "reshaped_input_sizes": reshaped_input_sizes}
        if segmentation_maps is not None:
            segmentation_maps, original_mask_sizes = zip(*(self._preprocess_mask(segmentation_map=mask, do_resize=do_resize, mask_size=mask_size, do_pad=do_pad,
            mask_pad_size=mask_pad_size, input_data_format=input_data_format) for mask in segmentation_maps))
            assert all(original_im_size == original_mask_size for original_im_size, original_mask_size in zip(original_sizes, original_mask_sizes)), "Segmentation maps should be the same size as input images."
            data["labels"] = segmentation_maps
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_masks(self, masks, original_sizes, reshaped_input_sizes, mask_threshold=0.0, binarize=True, pad_size=None, return_tensors="pt"):
        if return_tensors == "pt": return self._post_process_masks_pt(masks=masks, original_sizes=original_sizes, reshaped_input_sizes=reshaped_input_sizes,
        mask_threshold=mask_threshold, binarize=binarize, pad_size=pad_size)
        elif return_tensors == "tf": return self._post_process_masks_tf(masks=masks, original_sizes=original_sizes, reshaped_input_sizes=reshaped_input_sizes,
        mask_threshold=mask_threshold, binarize=binarize, pad_size=pad_size)
        else: raise ValueError("return_tensors must be either 'pt' or 'tf'")
    def _post_process_masks_pt(self, masks, original_sizes, reshaped_input_sizes, mask_threshold=0.0, binarize=True, pad_size=None):
        requires_backends(self, ["torch"])
        pad_size = self.pad_size if pad_size is None else pad_size
        target_image_size = (pad_size["height"], pad_size["width"])
        if isinstance(original_sizes, (torch.Tensor, np.ndarray)): original_sizes = original_sizes.tolist()
        if isinstance(reshaped_input_sizes, (torch.Tensor, np.ndarray)): reshaped_input_sizes = reshaped_input_sizes.tolist()
        output_masks = []
        for i, original_size in enumerate(original_sizes):
            if isinstance(masks[i], np.ndarray): masks[i] = torch.from_numpy(masks[i])
            elif not isinstance(masks[i], torch.Tensor): raise ValueError("Input masks should be a list of `torch.tensors` or a list of `np.ndarray`")
            interpolated_mask = F.interpolate(masks[i], target_image_size, mode="bilinear", align_corners=False)
            interpolated_mask = interpolated_mask[..., : reshaped_input_sizes[i][0], : reshaped_input_sizes[i][1]]
            interpolated_mask = F.interpolate(interpolated_mask, original_size, mode="bilinear", align_corners=False)
            if binarize: interpolated_mask = interpolated_mask > mask_threshold
            output_masks.append(interpolated_mask)
        return output_masks
    def _post_process_masks_tf(self, masks, original_sizes, reshaped_input_sizes, mask_threshold=0.0, binarize=True, pad_size=None):
        requires_backends(self, ["tf"])
        pad_size = self.pad_size if pad_size is None else pad_size
        target_image_size = (pad_size["height"], pad_size["width"])
        output_masks = []
        for i, original_size in enumerate(original_sizes):
            mask = tf.transpose(masks[i], perm=[0, 2, 3, 1])
            interpolated_mask = tf.image.resize(mask, target_image_size, method="bilinear")
            interpolated_mask = interpolated_mask[:, : reshaped_input_sizes[i][0], : reshaped_input_sizes[i][1], :]
            interpolated_mask = tf.image.resize(interpolated_mask, original_size, method="bilinear")
            if binarize: interpolated_mask = interpolated_mask > mask_threshold
            output_masks.append(tf.transpose(interpolated_mask, perm=[0, 3, 1, 2]))
        return output_masks
    def post_process_for_mask_generation(self, all_masks, all_scores, all_boxes, crops_nms_thresh, return_tensors="pt"):
        if return_tensors == "pt": return _postprocess_for_mg(all_masks, all_scores, all_boxes, crops_nms_thresh)
        elif return_tensors == "tf": return _postprocess_for_mg_tf(all_masks, all_scores, all_boxes, crops_nms_thresh)
    def generate_crop_boxes(self, image, target_size, crop_n_layers: int = 0, overlap_ratio: float = 512 / 1500, points_per_crop: Optional[int] = 32, crop_n_points_downscale_factor: Optional[List[int]] = 1,
    device: Optional["torch.device"] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, return_tensors: str = "pt"):
        crop_boxes, points_per_crop, cropped_images, input_labels = _generate_crop_boxes(image, target_size, crop_n_layers, overlap_ratio, points_per_crop, crop_n_points_downscale_factor, input_data_format)
        if return_tensors == "pt":
            if device is None: device = torch.device("cpu")
            crop_boxes = torch.tensor(crop_boxes, device=device)
            points_per_crop = torch.tensor(points_per_crop, device=device)
            input_labels = torch.tensor(input_labels, device=device)
        elif return_tensors == "tf":
            if device is not None: raise ValueError("device is not a supported argument when return_tensors is tf!")
            crop_boxes = tf.convert_to_tensor(crop_boxes)
            points_per_crop = tf.convert_to_tensor(points_per_crop)
            input_labels = tf.convert_to_tensor(input_labels)
        else: raise ValueError("return_tensors must be either 'pt' or 'tf'.")
        return crop_boxes, points_per_crop, cropped_images, input_labels
    def filter_masks(self, masks, iou_scores, original_size, cropped_box_image, pred_iou_thresh=0.88, stability_score_thresh=0.95, mask_threshold=0, stability_score_offset=1, return_tensors="pt"):
        if return_tensors == "pt": return self._filter_masks_pt(masks=masks, iou_scores=iou_scores, original_size=original_size, cropped_box_image=cropped_box_image,
        pred_iou_thresh=pred_iou_thresh, stability_score_thresh=stability_score_thresh, mask_threshold=mask_threshold, stability_score_offset=stability_score_offset)
        elif return_tensors == "tf": return self._filter_masks_tf(masks=masks, iou_scores=iou_scores, original_size=original_size, cropped_box_image=cropped_box_image,
        pred_iou_thresh=pred_iou_thresh, stability_score_thresh=stability_score_thresh, mask_threshold=mask_threshold, stability_score_offset=stability_score_offset)
    def _filter_masks_pt(self, masks, iou_scores, original_size, cropped_box_image, pred_iou_thresh=0.88, stability_score_thresh=0.95, mask_threshold=0, stability_score_offset=1):
        requires_backends(self, ["torch"])
        original_height, original_width = original_size
        iou_scores = iou_scores.flatten(0, 1)
        masks = masks.flatten(0, 1)
        if masks.shape[0] != iou_scores.shape[0]: raise ValueError("masks and iou_scores must have the same batch size.")
        if masks.device != iou_scores.device: iou_scores = iou_scores.to(masks.device)
        batch_size = masks.shape[0]
        keep_mask = torch.ones(batch_size, dtype=torch.bool, device=masks.device)
        if pred_iou_thresh > 0.0: keep_mask = keep_mask & (iou_scores > pred_iou_thresh)
        if stability_score_thresh > 0.0:
            stability_scores = _compute_stability_score_pt(masks, mask_threshold, stability_score_offset)
            keep_mask = keep_mask & (stability_scores > stability_score_thresh)
        scores = iou_scores[keep_mask]
        masks = masks[keep_mask]
        masks = masks > mask_threshold
        converted_boxes = _batched_mask_to_box(masks)
        keep_mask = ~_is_box_near_crop_edge(converted_boxes, cropped_box_image, [0, 0, original_width, original_height])
        scores = scores[keep_mask]
        masks = masks[keep_mask]
        converted_boxes = converted_boxes[keep_mask]
        masks = _pad_masks(masks, cropped_box_image, original_height, original_width)
        masks = _mask_to_rle_pytorch(masks)
        return masks, scores, converted_boxes
    def _filter_masks_tf(self, masks, iou_scores, original_size, cropped_box_image, pred_iou_thresh=0.88, stability_score_thresh=0.95, mask_threshold=0, stability_score_offset=1):
        requires_backends(self, ["tf"])
        original_height, original_width = original_size
        iou_scores = tf.reshape(iou_scores, [iou_scores.shape[0] * iou_scores.shape[1], iou_scores.shape[2:]])
        masks = tf.reshape(masks, [masks.shape[0] * masks.shape[1], masks.shape[2:]])
        if masks.shape[0] != iou_scores.shape[0]: raise ValueError("masks and iou_scores must have the same batch size.")
        batch_size = masks.shape[0]
        keep_mask = tf.ones(batch_size, dtype=tf.bool)
        if pred_iou_thresh > 0.0: keep_mask = keep_mask & (iou_scores > pred_iou_thresh)
        if stability_score_thresh > 0.0:
            stability_scores = _compute_stability_score_tf(masks, mask_threshold, stability_score_offset)
            keep_mask = keep_mask & (stability_scores > stability_score_thresh)
        scores = iou_scores[keep_mask]
        masks = masks[keep_mask]
        masks = masks > mask_threshold
        converted_boxes = _batched_mask_to_box_tf(masks)
        keep_mask = ~_is_box_near_crop_edge_tf(converted_boxes, cropped_box_image, [0, 0, original_width, original_height])
        scores = scores[keep_mask]
        masks = masks[keep_mask]
        converted_boxes = converted_boxes[keep_mask]
        masks = _pad_masks_tf(masks, cropped_box_image, original_height, original_width)
        masks = _mask_to_rle_tf(masks)
        return masks, scores, converted_boxes
def _compute_stability_score_pt(masks: "torch.Tensor", mask_threshold: float, stability_score_offset: int):
    intersections = ((masks > (mask_threshold + stability_score_offset)).sum(-1, dtype=torch.int16).sum(-1, dtype=torch.int32))
    unions = (masks > (mask_threshold - stability_score_offset)).sum(-1, dtype=torch.int16).sum(-1, dtype=torch.int32)
    stability_scores = intersections / unions
    return stability_scores
def _compute_stability_score_tf(masks: "tf.Tensor", mask_threshold: float, stability_score_offset: int):
    intersections = tf.count_nonzero(masks > (mask_threshold + stability_score_offset), axis=[-1, -2], dtype=tf.float32)
    unions = tf.count_nonzero(masks > (mask_threshold - stability_score_offset), axis=[-1, -2], dtype=tf.float32)
    stability_scores = intersections / unions
    return stability_scores
def _build_point_grid(n_per_side: int) -> np.ndarray:
    offset = 1 / (2 * n_per_side)
    points_one_side = np.linspace(offset, 1 - offset, n_per_side)
    points_x = np.tile(points_one_side[None, :], (n_per_side, 1))
    points_y = np.tile(points_one_side[:, None], (1, n_per_side))
    points = np.stack([points_x, points_y], axis=-1).reshape(-1, 2)
    return points
def _normalize_coordinates(target_size: int, coords: np.ndarray, original_size: Tuple[int, int], is_bounding_box=False) -> np.ndarray:
    old_height, old_width = original_size
    scale = target_size * 1.0 / max(old_height, old_width)
    new_height, new_width = old_height * scale, old_width * scale
    new_width = int(new_width + 0.5)
    new_height = int(new_height + 0.5)
    coords = deepcopy(coords).astype(float)
    if is_bounding_box: coords = coords.reshape(-1, 2, 2)
    coords[..., 0] = coords[..., 0] * (new_width / old_width)
    coords[..., 1] = coords[..., 1] * (new_height / old_height)
    if is_bounding_box: coords = coords.reshape(-1, 4)
    return coords
def _generate_crop_boxes(image, target_size: int, crop_n_layers: int = 0, overlap_ratio: float = 512 / 1500, points_per_crop: Optional[int] = 32, crop_n_points_downscale_factor: Optional[List[int]] = 1,
input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[List[List[int]], List[int]]:
    if isinstance(image, list): raise ValueError("Only one image is allowed for crop generation.")
    image = to_numpy_array(image)
    original_size = get_image_size(image, input_data_format)
    points_grid = []
    for i in range(crop_n_layers + 1):
        n_points = int(points_per_crop / (crop_n_points_downscale_factor**i))
        points_grid.append(_build_point_grid(n_points))
    crop_boxes, layer_idxs = _generate_per_layer_crops(crop_n_layers, overlap_ratio, original_size)
    cropped_images, point_grid_per_crop = _generate_crop_images(crop_boxes, image, points_grid, layer_idxs, target_size, original_size, input_data_format)
    crop_boxes = np.array(crop_boxes)
    crop_boxes = crop_boxes.astype(np.float32)
    points_per_crop = np.array([point_grid_per_crop])
    points_per_crop = np.transpose(points_per_crop, axes=(0, 2, 1, 3))
    input_labels = np.ones_like(points_per_crop[:, :, :, 0], dtype=np.int64)
    return crop_boxes, points_per_crop, cropped_images, input_labels
def _generate_per_layer_crops(crop_n_layers, overlap_ratio, original_size):
    crop_boxes, layer_idxs = [], []
    im_height, im_width = original_size
    short_side = min(im_height, im_width)
    crop_boxes.append([0, 0, im_width, im_height])
    layer_idxs.append(0)
    for i_layer in range(crop_n_layers):
        n_crops_per_side = 2 ** (i_layer + 1)
        overlap = int(overlap_ratio * short_side * (2 / n_crops_per_side))
        crop_width = int(math.ceil((overlap * (n_crops_per_side - 1) + im_width) / n_crops_per_side))
        crop_height = int(math.ceil((overlap * (n_crops_per_side - 1) + im_height) / n_crops_per_side))
        crop_box_x0 = [int((crop_width - overlap) * i) for i in range(n_crops_per_side)]
        crop_box_y0 = [int((crop_height - overlap) * i) for i in range(n_crops_per_side)]
        for left, top in product(crop_box_x0, crop_box_y0):
            box = [left, top, min(left + crop_width, im_width), min(top + crop_height, im_height)]
            crop_boxes.append(box)
            layer_idxs.append(i_layer + 1)
    return crop_boxes, layer_idxs
def _generate_crop_images(crop_boxes, image, points_grid, layer_idxs, target_size, original_size, input_data_format=None):
    cropped_images = []
    total_points_per_crop = []
    for i, crop_box in enumerate(crop_boxes):
        left, top, right, bottom = crop_box
        channel_dim = infer_channel_dimension_format(image, input_data_format)
        if channel_dim == ChannelDimension.LAST: cropped_im = image[top:bottom, left:right, :]
        else: cropped_im = image[:, top:bottom, left:right]
        cropped_images.append(cropped_im)
        cropped_im_size = get_image_size(cropped_im, channel_dim)
        points_scale = np.array(cropped_im_size)[None, ::-1]
        points = points_grid[layer_idxs[i]] * points_scale
        normalized_points = _normalize_coordinates(target_size, points, original_size)
        total_points_per_crop.append(normalized_points)
    return cropped_images, total_points_per_crop
def _pad_masks(masks, crop_box: List[int], orig_height: int, orig_width: int):
    left, top, right, bottom = crop_box
    if left == 0 and top == 0 and right == orig_width and bottom == orig_height: return masks
    pad_x, pad_y = orig_width - (right - left), orig_height - (bottom - top)
    pad = (left, pad_x - left, top, pad_y - top)
    return torch.nn.functional.pad(masks, pad, value=0)
def _pad_masks_tf(masks, crop_box: List[int], orig_height: int, orig_width: int):
    left, top, right, bottom = crop_box
    if left == 0 and top == 0 and right == orig_width and bottom == orig_height: return masks
    pad_x, pad_y = orig_width - (right - left), orig_height - (bottom - top)
    pad = (left, pad_x - left, top, pad_y - top)
    return tf.pad(masks, pad, constant_values=0)
def _is_box_near_crop_edge(boxes, crop_box, orig_box, atol=20.0):
    crop_box_torch = torch.as_tensor(crop_box, dtype=torch.float, device=boxes.device)
    orig_box_torch = torch.as_tensor(orig_box, dtype=torch.float, device=boxes.device)
    left, top, _, _ = crop_box
    offset = torch.tensor([[left, top, left, top]], device=boxes.device)
    if len(boxes.shape) == 3: offset = offset.unsqueeze(1)
    boxes = (boxes + offset).float()
    near_crop_edge = torch.isclose(boxes, crop_box_torch[None, :], atol=atol, rtol=0)
    near_image_edge = torch.isclose(boxes, orig_box_torch[None, :], atol=atol, rtol=0)
    near_crop_edge = torch.logical_and(near_crop_edge, ~near_image_edge)
    return torch.any(near_crop_edge, dim=1)
def _is_box_near_crop_edge_tf(boxes, crop_box, orig_box, atol=20.0):
    crop_box_tf = tf.convert_to_tensor(crop_box, dtype=tf.float32)
    orig_box_tf = tf.convert_to_tensor(orig_box, dtype=tf.float32)
    left, top, _, _ = crop_box
    offset = tf.convert_to_tensor([[left, top, left, top]])
    if len(boxes.shape) == 3: offset = tf.expand_dims(offset, 1)
    boxes = tf.cast(boxes + offset, tf.float32)
    near_crop_edge = tnp.isclose(boxes, crop_box_tf[None, :], atol=atol, rtol=0)
    near_image_edge = tnp.isclose(boxes, orig_box_tf[None, :], atol=atol, rtol=0)
    near_crop_edge = tf.math.logical_and(near_crop_edge, ~near_image_edge)
    return tf.reduce_any(near_crop_edge, axis=1)
def _batched_mask_to_box(masks: "torch.Tensor"):
    if torch.numel(masks) == 0: return torch.zeros(*masks.shape[:-2], 4, device=masks.device)
    shape = masks.shape
    height, width = shape[-2:]
    in_height, _ = torch.max(masks, dim=-1)
    in_height_coords = in_height * torch.arange(height, device=in_height.device)[None, :]
    bottom_edges, _ = torch.max(in_height_coords, dim=-1)
    in_height_coords = in_height_coords + height * (~in_height)
    top_edges, _ = torch.min(in_height_coords, dim=-1)
    in_width, _ = torch.max(masks, dim=-2)
    in_width_coords = in_width * torch.arange(width, device=in_width.device)[None, :]
    right_edges, _ = torch.max(in_width_coords, dim=-1)
    in_width_coords = in_width_coords + width * (~in_width)
    left_edges, _ = torch.min(in_width_coords, dim=-1)
    empty_filter = (right_edges < left_edges) | (bottom_edges < top_edges)
    out = torch.stack([left_edges, top_edges, right_edges, bottom_edges], dim=-1)
    out = out * (~empty_filter).unsqueeze(-1)
    out = out.reshape(*shape[:-2], 4)
    return out
def _batched_mask_to_box_tf(masks: "tf.Tensor"):
    if tf.size(masks) == 0: return tf.zeros([*masks.shape[:-2], 4])
    shape = shape_list(masks)
    height, width = shape[-2:]
    in_height = tf.reduce_max(masks, axis=-1)
    in_height_coords = in_height * tf.range(height)[None, :]
    bottom_edges = tf.reduce_max(in_height_coords, axis=-1)
    in_height_coords = in_height_coords + height * (~in_height)
    top_edges = tf.reduce_min(in_height_coords, axis=-1)
    in_width, _ = tf.reduce_max(masks, axis=-2)
    in_width_coords = in_width * tf.range(width)[None, :]
    right_edges, _ = tf.reduce_max(in_width_coords, axis=-1)
    in_width_coords = in_width_coords + width * (~in_width)
    left_edges, _ = tf.reduce_min(in_width_coords, axis=-1)
    empty_filter = (right_edges < left_edges) | (bottom_edges < top_edges)
    out = tf.stack([left_edges, top_edges, right_edges, bottom_edges], axis=-1)
    out = out * tf.expand_dims(~empty_filter, -1)
    out = tf.reshape(out, *shape[:-2], 4)
    return out
def _mask_to_rle_pytorch(input_mask: "torch.Tensor"):
    batch_size, height, width = input_mask.shape
    input_mask = input_mask.permute(0, 2, 1).flatten(1)
    diff = input_mask[:, 1:] ^ input_mask[:, :-1]
    change_indices = diff.nonzero()
    out = []
    for i in range(batch_size):
        cur_idxs = change_indices[change_indices[:, 0] == i, 1] + 1
        btw_idxs = cur_idxs[1:] - cur_idxs[:-1]
        counts = [] if input_mask[i, 0] == 0 else [0]
        counts += [cur_idxs[0].item()] + btw_idxs.tolist() + [height * width - cur_idxs[-1]]
        out.append({"size": [height, width], "counts": counts})
    return out
def _mask_to_rle_tf(input_mask: "tf.Tensor"):
    batch_size, height, width = input_mask.shape
    input_mask = flatten(tf.transpose(input_mask, perm=(0, 2, 1)), 1)
    diff = input_mask[:, 1:] ^ input_mask[:, :-1]
    change_indices = tf.where(diff)
    out = []
    for i in range(batch_size):
        cur_idxs = change_indices[change_indices[:, 0] == i, 1] + 1
        btw_idxs = cur_idxs[1:] - cur_idxs[:-1]
        counts = [] if input_mask[i, 0] == 0 else [0]
        counts += [cur_idxs[0].item()] + btw_idxs.tolist() + [height * width - cur_idxs[-1]]
        out.append({"size": [height, width], "counts": counts})
    return out
def _rle_to_mask(rle: Dict[str, Any]) -> np.ndarray:
    height, width = rle["size"]
    mask = np.empty(height * width, dtype=bool)
    idx = 0
    parity = False
    for count in rle["counts"]:
        mask[idx : idx + count] = parity
        idx += count
        parity = not parity
    mask = mask.reshape(width, height)
    return mask.transpose()
def _postprocess_for_mg(rle_masks, iou_scores, mask_boxes, amg_crops_nms_thresh=0.7):
    keep_by_nms = batched_nms(boxes=mask_boxes.float(), scores=iou_scores, idxs=torch.zeros(mask_boxes.shape[0]), iou_threshold=amg_crops_nms_thresh)
    iou_scores = iou_scores[keep_by_nms]
    rle_masks = [rle_masks[i] for i in keep_by_nms]
    mask_boxes = mask_boxes[keep_by_nms]
    masks = [_rle_to_mask(rle) for rle in rle_masks]
    return masks, iou_scores, rle_masks, mask_boxes
def _postprocess_for_mg_tf(rle_masks, iou_scores, mask_boxes, amg_crops_nms_thresh=0.7):
    keep_by_nms = tf.image.combined_non_max_suppression(boxes=mask_boxes.float(), scores=iou_scores, idxs=torch.zeros(mask_boxes.shape[0]), iou_threshold=amg_crops_nms_thresh)
    iou_scores = iou_scores[keep_by_nms]
    rle_masks = [rle_masks[i] for i in keep_by_nms]
    mask_boxes = mask_boxes[keep_by_nms]
    masks = [_rle_to_mask(rle) for rle in rle_masks]
    return masks, iou_scores, rle_masks, mask_boxes
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
