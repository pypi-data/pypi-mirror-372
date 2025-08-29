"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import pathlib
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import numpy as np
from ...feature_extraction_utils import BatchFeature
from ...image_processing_utils import BaseImageProcessor, get_size_dict
from ...image_transforms import (PaddingMode, center_to_corners_format, corners_to_center_format, pad, rescale, resize, to_channel_dimension_format)
from ...image_utils import (IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, AnnotationFormat, AnnotationType, ChannelDimension, ImageInput, PILImageResampling,
get_image_size, infer_channel_dimension_format, is_scaled_image, make_list_of_images, to_numpy_array, valid_images, validate_annotations, validate_preprocess_arguments)
from ...utils import (filter_out_non_signature_kwargs, is_flax_available, is_jax_tensor, is_tf_available, is_tf_tensor, is_torch_available, is_torch_tensor, logging, requires_backends)
from ...utils.generic import TensorType
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
SUPPORTED_ANNOTATION_FORMATS = (AnnotationFormat.COCO_DETECTION,)
def get_size_with_aspect_ratio(image_size, size, max_size=None) -> Tuple[int, int]:
    height, width = image_size
    raw_size = None
    if max_size is not None:
        min_original_size = float(min((height, width)))
        max_original_size = float(max((height, width)))
        if max_original_size / min_original_size * size > max_size:
            raw_size = max_size * min_original_size / max_original_size
            size = int(round(raw_size))
    if (height <= width and height == size) or (width <= height and width == size): oh, ow = height, width
    elif width < height:
        ow = size
        if max_size is not None and raw_size is not None: oh = int(raw_size * height / width)
        else: oh = int(size * height / width)
    else:
        oh = size
        if max_size is not None and raw_size is not None: ow = int(raw_size * width / height)
        else: ow = int(size * width / height)
    return (oh, ow)
def get_resize_output_image_size(input_image: np.ndarray, size: Union[int, Tuple[int, int], List[int]], max_size: Optional[int] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    image_size = get_image_size(input_image, input_data_format)
    if isinstance(size, (list, tuple)): return size
    return get_size_with_aspect_ratio(image_size, size, max_size)
def get_image_size_for_max_height_width(input_image: np.ndarray, max_height: int, max_width: int, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Tuple[int, int]:
    image_size = get_image_size(input_image, input_data_format)
    height, width = image_size
    height_scale = max_height / height
    width_scale = max_width / width
    min_scale = min(height_scale, width_scale)
    new_height = int(height * min_scale)
    new_width = int(width * min_scale)
    return new_height, new_width
def get_numpy_to_framework_fn(arr) -> Callable:
    if isinstance(arr, np.ndarray): return np.array
    if is_tf_available() and is_tf_tensor(arr):
        import tensorflow as tf
        return tf.convert_to_tensor
    if is_torch_available() and is_torch_tensor(arr):
        import torch
        return torch.tensor
    if is_flax_available() and is_jax_tensor(arr):
        import jax.numpy as jnp
        return jnp.array
    raise ValueError(f"Cannot convert arrays of type {type(arr)}")
def safe_squeeze(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    if axis is None: return arr.squeeze()
    try: return arr.squeeze(axis=axis)
    except ValueError: return arr
def normalize_annotation(annotation: Dict, image_size: Tuple[int, int]) -> Dict:
    image_height, image_width = image_size
    norm_annotation = {}
    for key, value in annotation.items():
        if key == "boxes":
            boxes = value
            boxes = corners_to_center_format(boxes)
            boxes /= np.asarray([image_width, image_height, image_width, image_height], dtype=np.float32)
            norm_annotation[key] = boxes
        else: norm_annotation[key] = value
    return norm_annotation
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
def prepare_coco_detection_annotation(image, target, return_segmentation_masks: bool = False, input_data_format: Optional[Union[ChannelDimension, str]] = None):
    image_height, image_width = get_image_size(image, channel_dim=input_data_format)
    image_id = target["image_id"]
    image_id = np.asarray([image_id], dtype=np.int64)
    annotations = target["annotations"]
    annotations = [obj for obj in annotations if "iscrowd" not in obj or obj["iscrowd"] == 0]
    classes = [obj["category_id"] for obj in annotations]
    classes = np.asarray(classes, dtype=np.int64)
    area = np.asarray([obj["area"] for obj in annotations], dtype=np.float32)
    iscrowd = np.asarray([obj["iscrowd"] if "iscrowd" in obj else 0 for obj in annotations], dtype=np.int64)
    boxes = [obj["bbox"] for obj in annotations]
    boxes = np.asarray(boxes, dtype=np.float32).reshape(-1, 4)
    boxes[:, 2:] += boxes[:, :2]
    boxes[:, 0::2] = boxes[:, 0::2].clip(min=0, max=image_width)
    boxes[:, 1::2] = boxes[:, 1::2].clip(min=0, max=image_height)
    keep = (boxes[:, 3] > boxes[:, 1]) & (boxes[:, 2] > boxes[:, 0])
    new_target = {}
    new_target["image_id"] = image_id
    new_target["class_labels"] = classes[keep]
    new_target["boxes"] = boxes[keep]
    new_target["area"] = area[keep]
    new_target["iscrowd"] = iscrowd[keep]
    new_target["orig_size"] = np.asarray([int(image_height), int(image_width)], dtype=np.int64)
    if annotations and "keypoints" in annotations[0]:
        keypoints = [obj["keypoints"] for obj in annotations]
        keypoints = np.asarray(keypoints, dtype=np.float32)
        keypoints = keypoints[keep]
        num_keypoints = keypoints.shape[0]
        keypoints = keypoints.reshape((-1, 3)) if num_keypoints else keypoints
        new_target["keypoints"] = keypoints
    return new_target
def resize_annotation(annotation: Dict[str, Any], orig_size: Tuple[int, int], target_size: Tuple[int, int], threshold: float = 0.5, resample: PILImageResampling = PILImageResampling.NEAREST):
    ratios = tuple(float(s) / float(s_orig) for s, s_orig in zip(target_size, orig_size))
    ratio_height, ratio_width = ratios
    new_annotation = {}
    new_annotation["size"] = target_size
    for key, value in annotation.items():
        if key == "boxes":
            boxes = value
            scaled_boxes = boxes * np.asarray([ratio_width, ratio_height, ratio_width, ratio_height], dtype=np.float32)
            new_annotation["boxes"] = scaled_boxes
        elif key == "area":
            area = value
            scaled_area = area * (ratio_width * ratio_height)
            new_annotation["area"] = scaled_area
        elif key == "masks":
            masks = value[:, None]
            masks = np.array([resize(mask, target_size, resample=resample) for mask in masks])
            masks = masks.astype(np.float32)
            masks = masks[:, 0] > threshold
            new_annotation["masks"] = masks
        elif key == "size": new_annotation["size"] = target_size
        else: new_annotation[key] = value
    return new_annotation
class RTDetrImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "pixel_mask"]
    def __init__(self, format: Union[str, AnnotationFormat] = AnnotationFormat.COCO_DETECTION, do_resize: bool = True, size: Dict[str, int] = None, resample: PILImageResampling = PILImageResampling.BILINEAR,
    do_rescale: bool = True, rescale_factor: Union[int, float] = 1 / 255, do_normalize: bool = False, image_mean: Union[float, List[float]] = None, image_std: Union[float, List[float]] = None,
    do_convert_annotations: bool = True, do_pad: bool = False, pad_size: Optional[Dict[str, int]] = None, **kwargs) -> None:
        size = size if size is not None else {"height": 640, "width": 640}
        size = get_size_dict(size, default_to_square=False)
        if do_convert_annotations is None: do_convert_annotations = do_normalize
        super().__init__(**kwargs)
        self.format = format
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.do_convert_annotations = do_convert_annotations
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.do_pad = do_pad
        self.pad_size = pad_size
    def prepare_annotation(self, image: np.ndarray, target: Dict, format: Optional[AnnotationFormat] = None, return_segmentation_masks: bool = None, masks_path: Optional[Union[str, pathlib.Path]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None) -> Dict:
        format = format if format is not None else self.format
        if format == AnnotationFormat.COCO_DETECTION:
            return_segmentation_masks = False if return_segmentation_masks is None else return_segmentation_masks
            target = prepare_coco_detection_annotation(image, target, return_segmentation_masks, input_data_format=input_data_format)
        else: raise ValueError(f"Format {format} is not supported.")
        return target
    def resize(self, image: np.ndarray, size: Dict[str, int], resample: PILImageResampling = PILImageResampling.BILINEAR, data_format: Optional[ChannelDimension] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None, **kwargs) -> np.ndarray:
        if "max_size" in kwargs:
            logger.warning_once("The `max_size` parameter is deprecated and will be removed in v4.26. Please specify in `size['longest_edge'] instead`.")
            max_size = kwargs.pop("max_size")
        else: max_size = None
        size = get_size_dict(size, max_size=max_size, default_to_square=False)
        if "shortest_edge" in size and "longest_edge" in size: new_size = get_resize_output_image_size(image, size["shortest_edge"], size["longest_edge"], input_data_format=input_data_format)
        elif "max_height" in size and "max_width" in size: new_size = get_image_size_for_max_height_width(image, size["max_height"], size["max_width"], input_data_format=input_data_format)
        elif "height" in size and "width" in size: new_size = (size["height"], size["width"])
        else: raise ValueError(f"Size must contain 'height' and 'width' keys or 'shortest_edge' and 'longest_edge' keys. Got {size.keys()}.")
        image = resize(image, size=new_size, resample=resample, data_format=data_format, input_data_format=input_data_format, **kwargs)
        return image
    def resize_annotation(self, annotation, orig_size, size, resample: PILImageResampling = PILImageResampling.NEAREST) -> Dict: return resize_annotation(annotation, orig_size=orig_size, target_size=size, resample=resample)
    def rescale(self, image: np.ndarray, rescale_factor: float, data_format: Optional[Union[str, ChannelDimension]] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None) -> np.ndarray: return rescale(image, rescale_factor, data_format=data_format, input_data_format=input_data_format)
    def normalize_annotation(self, annotation: Dict, image_size: Tuple[int, int]) -> Dict: return normalize_annotation(annotation, image_size=image_size)
    def _update_annotation_for_padded_image(self, annotation: Dict, input_image_size: Tuple[int, int], output_image_size: Tuple[int, int], padding, update_bboxes) -> Dict:
        new_annotation = {}
        new_annotation["size"] = output_image_size
        for key, value in annotation.items():
            if key == "masks":
                masks = value
                masks = pad(masks, padding, mode=PaddingMode.CONSTANT, constant_values=0, input_data_format=ChannelDimension.FIRST)
                masks = safe_squeeze(masks, 1)
                new_annotation["masks"] = masks
            elif key == "boxes" and update_bboxes:
                boxes = value
                boxes *= np.asarray([input_image_size[1] / output_image_size[1], input_image_size[0] / output_image_size[0], input_image_size[1] / output_image_size[1], input_image_size[0] / output_image_size[0]])
                new_annotation["boxes"] = boxes
            elif key == "size": new_annotation["size"] = output_image_size
            else: new_annotation[key] = value
        return new_annotation
    def _pad_image(self, image: np.ndarray, output_size: Tuple[int, int], annotation: Optional[Dict[str, Any]] = None, constant_values: Union[float, Iterable[float]] = 0,
    data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None, update_bboxes: bool = True) -> np.ndarray:
        input_height, input_width = get_image_size(image, channel_dim=input_data_format)
        output_height, output_width = output_size
        pad_bottom = output_height - input_height
        pad_right = output_width - input_width
        padding = ((0, pad_bottom), (0, pad_right))
        padded_image = pad(image, padding, mode=PaddingMode.CONSTANT, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format)
        if annotation is not None: annotation = self._update_annotation_for_padded_image(annotation, (input_height, input_width), (output_height, output_width), padding, update_bboxes)
        return padded_image, annotation
    def pad(self, images: List[np.ndarray], annotations: Optional[Union[AnnotationType, List[AnnotationType]]] = None, constant_values: Union[float, Iterable[float]] = 0,
    return_pixel_mask: bool = True, return_tensors: Optional[Union[str, TensorType]] = None, data_format: Optional[ChannelDimension] = None, input_data_format: Optional[Union[str, ChannelDimension]] = None,
    update_bboxes: bool = True, pad_size: Optional[Dict[str, int]] = None) -> BatchFeature:
        pad_size = pad_size if pad_size is not None else self.pad_size
        if pad_size is not None: padded_size = (pad_size["height"], pad_size["width"])
        else: padded_size = get_max_height_width(images, input_data_format=input_data_format)
        annotation_list = annotations if annotations is not None else [None] * len(images)
        padded_images = []
        padded_annotations = []
        for image, annotation in zip(images, annotation_list):
            padded_image, padded_annotation = self._pad_image(image, padded_size, annotation, constant_values=constant_values, data_format=data_format, input_data_format=input_data_format, update_bboxes=update_bboxes)
            padded_images.append(padded_image)
            padded_annotations.append(padded_annotation)
        data = {"pixel_values": padded_images}
        if return_pixel_mask:
            masks = [make_pixel_mask(image=image, output_size=padded_size, input_data_format=input_data_format) for image in images]
            data["pixel_mask"] = masks
        encoded_inputs = BatchFeature(data=data, tensor_type=return_tensors)
        if annotations is not None: encoded_inputs["labels"] = [BatchFeature(annotation, tensor_type=return_tensors) for annotation in padded_annotations]
        return encoded_inputs
    @filter_out_non_signature_kwargs()
    def preprocess(self, images: ImageInput, annotations: Optional[Union[AnnotationType, List[AnnotationType]]] = None, return_segmentation_masks: bool = None,
    masks_path: Optional[Union[str, pathlib.Path]] = None, do_resize: Optional[bool] = None, size: Optional[Dict[str, int]] = None, resample=None, do_rescale: Optional[bool] = None,
    rescale_factor: Optional[Union[int, float]] = None, do_normalize: Optional[bool] = None, do_convert_annotations: Optional[bool] = None, image_mean: Optional[Union[float, List[float]]] = None,
    image_std: Optional[Union[float, List[float]]] = None, do_pad: Optional[bool] = None, format: Optional[Union[str, AnnotationFormat]] = None, return_tensors: Optional[Union[TensorType, str]] = None,
    data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST, input_data_format: Optional[Union[str, ChannelDimension]] = None, pad_size: Optional[Dict[str, int]] = None) -> BatchFeature:
        do_resize = self.do_resize if do_resize is None else do_resize
        size = self.size if size is None else size
        size = get_size_dict(size=size, default_to_square=True)
        resample = self.resample if resample is None else resample
        do_rescale = self.do_rescale if do_rescale is None else do_rescale
        rescale_factor = self.rescale_factor if rescale_factor is None else rescale_factor
        do_normalize = self.do_normalize if do_normalize is None else do_normalize
        image_mean = self.image_mean if image_mean is None else image_mean
        image_std = self.image_std if image_std is None else image_std
        do_convert_annotations = (self.do_convert_annotations if do_convert_annotations is None else do_convert_annotations)
        do_pad = self.do_pad if do_pad is None else do_pad
        pad_size = self.pad_size if pad_size is None else pad_size
        format = self.format if format is None else format
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        validate_preprocess_arguments(do_rescale=do_rescale, rescale_factor=rescale_factor, do_normalize=do_normalize, image_mean=image_mean, image_std=image_std,
        do_resize=do_resize, size=size, resample=resample)
        if annotations is not None and isinstance(annotations, dict): annotations = [annotations]
        if annotations is not None and len(images) != len(annotations): raise ValueError(f"The number of images ({len(images)}) and annotations ({len(annotations)}) do not match.")
        format = AnnotationFormat(format)
        if annotations is not None: validate_annotations(format, SUPPORTED_ANNOTATION_FORMATS, annotations)
        images = make_list_of_images(images)
        if not valid_images(images): raise ValueError("Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, torch.Tensor, tf.Tensor or jax.ndarray.")
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale: logger.warning_once("It looks like you are trying to rescale already rescaled images. If the input images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again.")
        if input_data_format is None: input_data_format = infer_channel_dimension_format(images[0])
        if annotations is not None:
            prepared_images = []
            prepared_annotations = []
            for image, target in zip(images, annotations):
                target = self.prepare_annotation(image, target, format, return_segmentation_masks=return_segmentation_masks, masks_path=masks_path, input_data_format=input_data_format)
                prepared_images.append(image)
                prepared_annotations.append(target)
            images = prepared_images
            annotations = prepared_annotations
            del prepared_images, prepared_annotations
        if do_resize:
            if annotations is not None:
                resized_images, resized_annotations = [], []
                for image, target in zip(images, annotations):
                    orig_size = get_image_size(image, input_data_format)
                    resized_image = self.resize(image, size=size, resample=resample, input_data_format=input_data_format)
                    resized_annotation = self.resize_annotation(target, orig_size, get_image_size(resized_image, input_data_format))
                    resized_images.append(resized_image)
                    resized_annotations.append(resized_annotation)
                images = resized_images
                annotations = resized_annotations
                del resized_images, resized_annotations
            else: images = [self.resize(image, size=size, resample=resample, input_data_format=input_data_format) for image in images]
        if do_rescale: images = [self.rescale(image, rescale_factor, input_data_format=input_data_format) for image in images]
        if do_normalize: images = [self.normalize(image, image_mean, image_std, input_data_format=input_data_format) for image in images]
        if do_convert_annotations and annotations is not None: annotations = [self.normalize_annotation(annotation, get_image_size(image, input_data_format)) for annotation, image in zip(annotations, images)]
        if do_pad: encoded_inputs = self.pad(images, annotations=annotations, return_pixel_mask=True, data_format=data_format, input_data_format=input_data_format, update_bboxes=do_convert_annotations, return_tensors=return_tensors, pad_size=pad_size)
        else:
            images = [to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format) for image in images]
            encoded_inputs = BatchFeature(data={"pixel_values": images}, tensor_type=return_tensors)
            if annotations is not None: encoded_inputs["labels"] = [BatchFeature(annotation, tensor_type=return_tensors) for annotation in annotations]
        return encoded_inputs
    def post_process_object_detection(self, outputs, threshold: float = 0.5, target_sizes: Union[TensorType, List[Tuple]] = None, use_focal_loss: bool = True):
        requires_backends(self, ["torch"])
        out_logits, out_bbox = outputs.logits, outputs.pred_boxes
        boxes = center_to_corners_format(out_bbox)
        if target_sizes is not None:
            if len(out_logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
            if isinstance(target_sizes, List):
                img_h = torch.Tensor([i[0] for i in target_sizes])
                img_w = torch.Tensor([i[1] for i in target_sizes])
            else: img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(boxes.device)
            boxes = boxes * scale_fct[:, None, :]
        num_top_queries = out_logits.shape[1]
        num_classes = out_logits.shape[2]
        if use_focal_loss:
            scores = torch.nn.functional.sigmoid(out_logits)
            scores, index = torch.topk(scores.flatten(1), num_top_queries, axis=-1)
            labels = index % num_classes
            index = index // num_classes
            boxes = boxes.gather(dim=1, index=index.unsqueeze(-1).repeat(1, 1, boxes.shape[-1]))
        else:
            scores = torch.nn.functional.softmax(out_logits)[:, :, :-1]
            scores, labels = scores.max(dim=-1)
            if scores.shape[1] > num_top_queries:
                scores, index = torch.topk(scores, num_top_queries, dim=-1)
                labels = torch.gather(labels, dim=1, index=index)
                boxes = torch.gather(boxes, dim=1, index=index.unsqueeze(-1).tile(1, 1, boxes.shape[-1]))
        results = []
        for s, l, b in zip(scores, labels, boxes):
            score = s[s > threshold]
            label = l[s > threshold]
            box = b[s > threshold]
            results.append({"scores": score, "labels": label, "boxes": box})
        return results
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
