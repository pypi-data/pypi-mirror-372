"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import (center_crop, center_to_corners_format, rescale, resize, to_channel_dimension_format)
from ...image_utils import (OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, PILImageResampling, infer_channel_dimension_format, is_scaled_image,
make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_torch_available, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
def _upcast(t):
    if t.is_floating_point(): return t if t.dtype in (torch.float32, torch.float64) else t.float()
    else: return t if t.dtype in (torch.int32, torch.int64) else t.int()
def box_area(boxes):
    boxes = _upcast(boxes)
    return (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
def box_iou(boxes1, boxes2):
    area1 = box_area(boxes1)
    area2 = box_area(boxes2)
    left_top = torch.max(boxes1[:, None, :2], boxes2[:, :2])
    right_bottom = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])
    width_height = (right_bottom - left_top).clamp(min=0)
    inter = width_height[:, :, 0] * width_height[:, :, 1]
    union = area1[:, None] + area2 - inter
    iou = inter / union
    return iou, union
class OwlViTImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_resize=True, size=None, resample=PILImageResampling.BICUBIC, do_center_crop=False, crop_size=None, do_rescale=True, rescale_factor=1 / 255,
    do_normalize=True, image_mean=None, image_std=None, **kwargs):
        size = size if size is not None else {"height": 768, "width": 768}
        size = get_size_dict(size, default_to_square=True)
        crop_size = crop_size if crop_size is not None else {"height": 768, "width": 768}
        crop_size = get_size_dict(crop_size, default_to_square=True)
        if "rescale" in kwargs:
            rescale_val = kwargs.pop("rescale")
            kwargs["do_rescale"] = rescale_val
        super().__init__(**kwargs)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_center_crop = do_center_crop
        self.crop_size = crop_size
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else OPENAI_CLIP_MEAN
        self.image_std = image_std if image_std is not None else OPENAI_CLIP_STD
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling.BICUBIC, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        size = get_size_dict(size, default_to_square=True)
        if "height" not in size or "width" not in size: raise ValueError("size dictionary must contain height and width keys")
        return resize(image, (size["height"], size["width"]), resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
    def center_crop(self, image: np.ndarray, crop_size: Dict[str, int], data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        crop_size = get_size_dict(crop_size, default_to_square=True)
        if "height" not in crop_size or "width" not in crop_size: raise ValueError("crop_size dictionary must contain height and width keys")
        return center_crop(image, (crop_size["height"], crop_size["width"]), data_format=data_format, input_data_format=input_data_format, **kwargs)
    def rescale(self, image: np.ndarray, rescale_factor: float, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray: return rescale(image, rescale_factor, data_format=data_format, input_data_format=input_data_format)
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, resample: PILImageResampling = None,
    do_center_crop: Optional[bool] = None, crop_size: Optional[Dict[str, int]] = None, do_rescale: Optional[bool] = None, rescale_factor: Optional[float] = None,
    do_normalize: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None,
    return_tensors: Optional[Union[TensorType, str]] = None, data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> BatchFeature:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        resample = resample if resample is not None else self.resample
        do_center_crop = do_center_crop if do_center_crop is not None else self.do_center_crop
        crop_size = crop_size if crop_size is not None else self.crop_size
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_center_crop=do_center_crop, crop_size=crop_size, do_resize=do_resize, size=size, resample=resample)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_resize: images = [self.resize(image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_center_crop: images = [self.center_crop(image, crop_size=crop_size, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image, rescale_factor=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        encoded_inputs = BatchFeature(data={"pixel_values": images}, tensor_type=return_tensors)
        return encoded_inputs
    def post_process(self, outputs, target_sizes):
        warnings.warn("`post_process` is deprecated and will be removed in v5 of Transformers, please use `post_process_object_detection` instead, with `threshold=0.` for equivalent results.", FutureWarning)
        logits, boxes = outputs.logits, outputs.pred_boxes
        if len(logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        if target_sizes.shape[1] != 2: raise ValueError("Each element of target_sizes must contain the size (h, w) of each image of the batch")
        probs = torch.max(logits, dim=-1)
        scores = torch.sigmoid(probs.values)
        labels = probs.indices
        boxes = center_to_corners_format(boxes)
        img_h, img_w = target_sizes.unbind(1)
        scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(boxes.device)
        boxes = boxes * scale_fct[:, None, :]
        results = [{"scores": s, "labels": l, "boxes": b} for s, l, b in zip(scores, labels, boxes)]
        return results
    def post_process_object_detection(self, outputs, threshold: float = 0.1, target_sizes: Union[TensorType, List[Tuple]] = None):
        logits, boxes = outputs.logits, outputs.pred_boxes
        if target_sizes is not None:
            if len(logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        probs = torch.max(logits, dim=-1)
        scores = torch.sigmoid(probs.values)
        labels = probs.indices
        boxes = center_to_corners_format(boxes)
        if target_sizes is not None:
            if isinstance(target_sizes, List):
                img_h = torch.Tensor([i[0] for i in target_sizes])
                img_w = torch.Tensor([i[1] for i in target_sizes])
            else: img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(boxes.device)
            boxes = boxes * scale_fct[:, None, :]
        results = []
        for s, l, b in zip(scores, labels, boxes):
            score = s[s > threshold]
            label = l[s > threshold]
            box = b[s > threshold]
            results.append({"scores": score, "labels": label, "boxes": box})
        return results
    def post_process_image_guided_detection(self, outputs, threshold=0.0, nms_threshold=0.3, target_sizes=None):
        logits, target_boxes = outputs.logits, outputs.target_pred_boxes
        if target_sizes is not None and len(logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        if target_sizes is not None and target_sizes.shape[1] != 2: raise ValueError("Each element of target_sizes must contain the size (h, w) of each image of the batch")
        probs = torch.max(logits, dim=-1)
        scores = torch.sigmoid(probs.values)
        target_boxes = center_to_corners_format(target_boxes)
        if nms_threshold < 1.0:
            for idx in range(target_boxes.shape[0]):
                for i in torch.argsort(-scores[idx]):
                    if not scores[idx][i]: continue
                    ious = box_iou(target_boxes[idx][i, :].unsqueeze(0), target_boxes[idx])[0][0]
                    ious[i] = -1.0
                    scores[idx][ious > nms_threshold] = 0.0
        if target_sizes is not None:
            if isinstance(target_sizes, List):
                img_h = torch.tensor([i[0] for i in target_sizes])
                img_w = torch.tensor([i[1] for i in target_sizes])
            else: img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(target_boxes.device)
            target_boxes = target_boxes * scale_fct[:, None, :]
        results = []
        alphas = torch.zeros_like(scores)
        for idx in range(target_boxes.shape[0]):
            query_scores = scores[idx]
            if not query_scores.nonzero().numel(): continue
            query_scores[query_scores < threshold] = 0.0
            max_score = torch.max(query_scores) + 1e-6
            query_alphas = (query_scores - (max_score * 0.1)) / (max_score * 0.9)
            query_alphas = torch.clip(query_alphas, 0.0, 1.0)
            alphas[idx] = query_alphas
            mask = alphas[idx] > 0
            box_scores = alphas[idx][mask]
            boxes = target_boxes[idx][mask]
            results.append({"scores": box_scores, "labels": None, "boxes": boxes})
        return results
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
