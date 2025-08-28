"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import pathlib
from typing import Dict, List, Optional, Tuple, Union
from ...image_processing_utils import BatchFeature
from ...image_transforms import center_to_corners_format
from ...image_utils import AnnotationFormat, ImageInput
from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import BatchEncoding, PreTokenizedInput, TextInput
from ...utils import TensorType, is_torch_available
if is_torch_available(): import torch
AnnotationType = Dict[str, Union[int, str, List[Dict]]]
def get_phrases_from_posmap(posmaps, input_ids):
    left_idx = 0
    right_idx = posmaps.shape[-1] - 1
    posmaps = posmaps.clone()
    posmaps[:, 0 : left_idx + 1] = False
    posmaps[:, right_idx:] = False
    token_ids = []
    for posmap in posmaps:
        non_zero_idx = posmap.nonzero(as_tuple=True)[0].tolist()
        token_ids.append([input_ids[i] for i in non_zero_idx])
    return token_ids
class GroundingDinoImagesKwargs(ImagesKwargs, total=False):
    annotations: Optional[Union[AnnotationType, List[AnnotationType]]]
    return_segmentation_masks: Optional[bool]
    masks_path: Optional[Union[str, pathlib.Path]]
    do_convert_annotations: Optional[bool]
    format: Optional[Union[str, AnnotationFormat]]
class GroundingDinoProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: GroundingDinoImagesKwargs
    _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': False, 'stride': 0, 'return_overflowing_tokens': False, 'return_special_tokens_mask': False,
    'return_offsets_mapping': False, 'return_token_type_ids': True, 'return_length': False, 'verbose': True}}
class GroundingDinoProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "GroundingDinoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer): super().__init__(image_processor, tokenizer)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None,
    videos=None, **kwargs: Unpack[GroundingDinoProcessorKwargs]) -> BatchEncoding:
        if images is None and text is None: raise ValueError("You must specify either text or images.")
        output_kwargs = self._merge_kwargs(GroundingDinoProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        if images is not None: encoding_image_processor = self.image_processor(images, **output_kwargs["images_kwargs"])
        else: encoding_image_processor = BatchFeature()
        if text is not None: text_encoding = self.tokenizer(text=text, **output_kwargs["text_kwargs"])
        else: text_encoding = BatchEncoding()
        text_encoding.update(encoding_image_processor)
        return text_encoding
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    def post_process_grounded_object_detection(self, outputs, input_ids, box_threshold: float = 0.25, text_threshold: float = 0.25, target_sizes: Union[TensorType, List[Tuple]] = None):
        logits, boxes = outputs.logits, outputs.pred_boxes
        if target_sizes is not None:
            if len(logits) != len(target_sizes): raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        probs = torch.sigmoid(logits)
        scores = torch.max(probs, dim=-1)[0]
        boxes = center_to_corners_format(boxes)
        if target_sizes is not None:
            if isinstance(target_sizes, List):
                img_h = torch.Tensor([i[0] for i in target_sizes])
                img_w = torch.Tensor([i[1] for i in target_sizes])
            else: img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(boxes.device)
            boxes = boxes * scale_fct[:, None, :]
        results = []
        for idx, (s, b, p) in enumerate(zip(scores, boxes, probs)):
            score = s[s > box_threshold]
            box = b[s > box_threshold]
            prob = p[s > box_threshold]
            label_ids = get_phrases_from_posmap(prob > text_threshold, input_ids[idx])
            label = self.batch_decode(label_ids)
            results.append({"scores": score, "labels": label, "boxes": box})
        return results
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
