"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import sys
from typing import List, Optional, Tuple, Union
from ...feature_extraction_utils import BatchFeature
from ...image_transforms import center_to_corners_format
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, TextKwargs
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import (TensorType, is_torch_available, is_torchvision_available)
if sys.version_info >= (3, 11): from typing import Unpack
else: from typing_extensions import Unpack
class OmDetTurboTextKwargs(TextKwargs, total=False):
    task: Optional[Union[str, List[str], TextInput, PreTokenizedInput]]
class OmDetTurboProcessorKwargs(ProcessingKwargs, total=False):
    text_kwargs: OmDetTurboTextKwargs
    _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': 'max_length', 'truncation': True, 'max_length': 77, 'stride': 0, 'return_overflowing_tokens': False,
    'return_special_tokens_mask': False, 'return_offsets_mapping': False, 'return_token_type_ids': False, 'return_length': False, 'verbose': True, 'task': None}, "images_kwargs": {}}
if is_torch_available(): import torch
if is_torchvision_available(): from torchvision.ops.boxes import batched_nms
def clip_boxes(box, box_size: Tuple[int, int]):
    assert torch.isfinite(box).all(), "Box tensor contains infinite or NaN!"
    height, width = box_size
    x1 = box[:, 0].clamp(min=0, max=width)
    y1 = box[:, 1].clamp(min=0, max=height)
    x2 = box[:, 2].clamp(min=0, max=width)
    y2 = box[:, 3].clamp(min=0, max=height)
    box = torch.stack((x1, y1, x2, y2), dim=-1)
    return box
def compute_score(boxes):
    num_classes = boxes.shape[2]
    proposal_num = boxes.shape[1]
    scores = torch.sigmoid(boxes)
    classes = torch.arange(num_classes, device=boxes.device).unsqueeze(0).repeat(proposal_num, 1).flatten(0, 1)
    return scores, classes
def _post_process_boxes_for_image(boxes: TensorType, scores: TensorType, predicted_classes: TensorType, classes: List[str], image_size: Tuple[int, int], num_classes: int,
score_threshold: float, nms_threshold: float, max_num_det: int = None) -> dict:
    proposal_num = len(boxes) if max_num_det is None else max_num_det
    scores_per_image, topk_indices = scores.flatten(0, 1).topk(proposal_num, sorted=False)
    classes_per_image = predicted_classes[topk_indices]
    box_pred_per_image = boxes.view(-1, 1, 4).repeat(1, num_classes, 1).view(-1, 4)
    box_pred_per_image = box_pred_per_image[topk_indices]
    box_pred_per_image = center_to_corners_format(box_pred_per_image)
    box_pred_per_image = box_pred_per_image * torch.tensor(image_size[::-1]).repeat(2).to(box_pred_per_image.device)
    filter_mask = scores_per_image > score_threshold
    score_keep = filter_mask.nonzero(as_tuple=False).view(-1)
    box_pred_per_image = box_pred_per_image[score_keep]
    scores_per_image = scores_per_image[score_keep]
    classes_per_image = classes_per_image[score_keep]
    filter_classes_mask = classes_per_image < len(classes)
    classes_keep = filter_classes_mask.nonzero(as_tuple=False).view(-1)
    box_pred_per_image = box_pred_per_image[classes_keep]
    scores_per_image = scores_per_image[classes_keep]
    classes_per_image = classes_per_image[classes_keep]
    keep = batched_nms(box_pred_per_image, scores_per_image, classes_per_image, nms_threshold)
    box_pred_per_image = box_pred_per_image[keep]
    scores_per_image = scores_per_image[keep]
    classes_per_image = classes_per_image[keep]
    classes_per_image = [classes[i] for i in classes_per_image]
    result = {}
    result["boxes"] = clip_boxes(box_pred_per_image, image_size)
    result["scores"] = scores_per_image
    result["classes"] = classes_per_image
    return result
class OmDetTurboProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "DetrImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer): super().__init__(image_processor, tokenizer)
    def __call__(self, images: ImageInput = None, text: Union[List[str], List[List[str]]] = None, audio=None, videos=None, **kwargs: Unpack[OmDetTurboProcessorKwargs]) -> BatchFeature:
        if images is None or text is None: raise ValueError("You have to specify both `images` and `text`")
        output_kwargs = self._merge_kwargs(OmDetTurboProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if isinstance(text, str): text = text.strip(" ").split(",")
        if not (len(text) and isinstance(text[0], (list, tuple))): text = [text]
        task = output_kwargs["text_kwargs"].pop("task", None)
        if task is None: task = ["Detect {}.".format(", ".join(text_single)) for text_single in text]
        elif not isinstance(task, (list, tuple)): task = [task]
        encoding_image_processor = self.image_processor(images, **output_kwargs["images_kwargs"])
        tasks_encoding = self.tokenizer(text=task, **output_kwargs["text_kwargs"])
        classes = text
        classes_structure = torch.tensor([len(class_single) for class_single in classes], dtype=torch.long)
        classes_flattened = [class_single for class_batch in classes for class_single in class_batch]
        classes_encoding = self.tokenizer(text=classes_flattened, **output_kwargs["text_kwargs"])
        encoding = BatchFeature()
        encoding.update({f"tasks_{key}": value for key, value in tasks_encoding.items()})
        encoding.update({f"classes_{key}": value for key, value in classes_encoding.items()})
        encoding.update({"classes_structure": classes_structure})
        encoding.update(encoding_image_processor)
        return encoding
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def post_process_grounded_object_detection(self, outputs, classes: Union[List[str], List[List[str]]], score_threshold: float = 0.3, nms_threshold: float = 0.5,
    target_sizes: Optional[Union[TensorType, List[Tuple]]] = None, max_num_det: Optional[int] = None):
        if isinstance(classes[0], str): classes = [classes]
        boxes_logits = outputs.decoder_coord_logits
        scores_logits = outputs.decoder_class_logits
        if target_sizes is None:
            height = (self.image_processor.size["height"] if "height" in self.image_processor.size else self.image_processor.size["shortest_edge"])
            width = (self.image_processor.size["width"] if "width" in self.image_processor.size else self.image_processor.size["longest_edge"])
            target_sizes = ((height, width),) * len(boxes_logits)
        elif len(target_sizes[0]) != 2: raise ValueError("Each element of target_sizes must contain the size (height, width) of each image of the batch")
        if len(target_sizes) != len(boxes_logits): raise ValueError("Make sure that you pass in as many target sizes as output sequences")
        if len(classes) != len(boxes_logits): raise ValueError("Make sure that you pass in as many classes group as output sequences")
        if isinstance(target_sizes, torch.Tensor): target_sizes = target_sizes.tolist()
        scores, predicted_classes = compute_score(scores_logits)
        num_classes = scores_logits.shape[2]
        results = []
        for scores_img, box_per_img, image_size, class_names in zip(scores, boxes_logits, target_sizes, classes):
            results.append(_post_process_boxes_for_image(box_per_img, scores_img, predicted_classes, class_names, image_size, num_classes, score_threshold=score_threshold,
            nms_threshold=nms_threshold, max_num_det=max_num_det))
        return results
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
