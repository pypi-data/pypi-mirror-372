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
from ...image_processing_utils import BaseImageProcessor, BatchFeature
from ...image_transforms import (center_to_corners_format, pad, to_channel_dimension_format)
from ...image_utils import (OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ChannelDimension, ImageInput, PILImageResampling, get_image_size, infer_channel_dimension_format,
is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_preprocess_arguments)
from ...utils import (TensorType, filter_out_non_signature_kwargs, is_scipy_available, is_torch_available, is_vision_available, logging, requires_backends)
if is_torch_available(): import torch
if is_vision_available(): import PIL
if is_scipy_available(): from scipy import ndimage as ndi
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
def _preprocess_resize_output_shape(image, output_shape):
    output_shape = tuple(output_shape)
    output_ndim = len(output_shape)
    input_shape = image.shape
    if output_ndim > image.ndim:
        input_shape += (1,) * (output_ndim - image.ndim)
        image = np.reshape(image, input_shape)
    elif output_ndim == image.ndim - 1: output_shape = output_shape + (image.shape[-1],)
    elif output_ndim < image.ndim: raise ValueError("output_shape length cannot be smaller than the " "image number of dimensions")
    return image, output_shape
def _clip_warp_output(input_image, output_image):
    min_val = np.min(input_image)
    if np.isnan(min_val):
        min_func = np.nanmin
        max_func = np.nanmax
        min_val = min_func(input_image)
    else:
        min_func = np.min
        max_func = np.max
    max_val = max_func(input_image)
    output_image = np.clip(output_image, min_val, max_val)
    return output_image
class Owlv2ImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(self, do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_pad: bool = True, do_resize: bool = True, size: Dict[str, int] = None,
    resample: PILImageResampling = PILImageResampling.BILINEAR, do_normalize: bool = True, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_pad = do_pad
        self.do_resize = do_resize
        self.size = size if size is not None else {"height": 960, "width": 960}
        self.resample = resample
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else OPENAI_CLIP_MEAN
        self.image_std = image_std if image_std is not None else OPENAI_CLIP_STD
    def pad(self, image: np.array, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None):
        height, width = get_image_size(image)
        size = max(height, width)
        image = pad(image=image, padding=((0, size - height), (0, size - width)), constant_values=0.5, data_format=data_format, input_data_format=input_data_format)
        return image
    def resize(self, image: np.ndarray, size: Dict[str, int], anti_aliasing: bool = True, anti_aliasing_sigma=None, data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        requires_backends(self, "scipy")
        output_shape = (size["height"], size["width"])
        image = to_channel_dimension_format(image, ChannelDimension.LAST)
        image, output_shape = _preprocess_resize_output_shape(image, output_shape)
        input_shape = image.shape
        factors = np.divide(input_shape, output_shape)
        ndi_mode = "mirror"
        cval = 0
        order = 1
        if anti_aliasing:
            if anti_aliasing_sigma is None: anti_aliasing_sigma = np.maximum(0, (factors - 1) / 2)
            else:
                anti_aliasing_sigma = np.atleast_1d(anti_aliasing_sigma) * np.ones_like(factors)
                if np.any(anti_aliasing_sigma < 0): raise ValueError("Anti-aliasing standard deviation must be " "greater than or equal to zero")
                elif np.any((anti_aliasing_sigma > 0) & (factors <= 1)): warnings.warn("Anti-aliasing standard deviation greater than zero but " "not down-sampling along all axes")
            filtered = ndi.gaussian_filter(image, anti_aliasing_sigma, cval=cval, mode=ndi_mode)
        else: filtered = image
        zoom_factors = [1 / f for f in factors]
        out = ndi.zoom(filtered, zoom_factors, order=order, mode=ndi_mode, cval=cval, grid_mode=True)
        image = _clip_warp_output(image, out)
        image = to_channel_dimension_format(image, input_data_format, ChannelDimension.LAST)
        image = (to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image)
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, do_pad: bool = None, do_resize: bool = None, size: Dict[str, int] = None, do_rescale: bool = None, rescale_factor: float = None,
    do_normalize: bool = None, image_mean: Optional[Union[float, List[float]]] = None, image_std: Optional[Union[float, List[float]]] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: ChannelDimension = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> PIL.Image.Image:
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_pad = do_pad if do_pad is not None else self.do_pad
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std, size=size)
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if do_rescale: images = [self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format) for image in images]
        if do_pad: images = [self.pad(image=image, input_data_format=input_data_format) for image in images]
        if do_resize: images = [self.resize(image=image, size=size, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format) for image in images]
        images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
        data = {"pixel_values": images}
        return BatchFeature(data=data, tensor_type=return_tensors)
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
            size = torch.max(img_h, img_w)
            scale_fct = torch.stack([size, size, size, size], dim=1).to(boxes.device)
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
