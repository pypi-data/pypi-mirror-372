"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from sapiens_transformers import logging
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, TextKwargs, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
logger = logging.get_logger(__name__)
class UdopTextKwargs(TextKwargs, total=False):
    word_labels: Optional[Union[List[int], List[List[int]]]]
    boxes: Union[List[List[int]], List[List[List[int]]]]
class UdopProcessorKwargs(ProcessingKwargs, total=False):
    text_kwargs: UdopTextKwargs
    _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': False, 'truncation': False, 'stride': 0, 'return_overflowing_tokens': False, 'return_special_tokens_mask': False,
    'return_offsets_mapping': False, 'return_length': False, 'verbose': True}, "images_kwargs": {}}
class UdopProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "LayoutLMv3ImageProcessor"
    tokenizer_class = ("UdopTokenizer", "UdopTokenizerFast")
    optional_call_args = ["text_pair"]
    def __init__(self, image_processor, tokenizer): super().__init__(image_processor, tokenizer)
    def __call__(self, images: Optional[ImageInput] = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, *args,
    audio=None, videos=None, **kwargs: Unpack[UdopProcessorKwargs]) -> BatchFeature:
        output_kwargs = self._merge_kwargs(UdopProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs, **self.prepare_and_validate_optional_call_args(*args))
        boxes = output_kwargs["text_kwargs"].pop("boxes", None)
        word_labels = output_kwargs["text_kwargs"].pop("word_labels", None)
        text_pair = output_kwargs["text_kwargs"].pop("text_pair", None)
        return_overflowing_tokens = output_kwargs["text_kwargs"].get("return_overflowing_tokens", False)
        return_offsets_mapping = output_kwargs["text_kwargs"].get("return_offsets_mapping", False)
        text_target = output_kwargs["text_kwargs"].get("text_target", None)
        if self.image_processor.apply_ocr and (boxes is not None): raise ValueError("You cannot provide bounding boxes if you initialized the image processor with apply_ocr set to True.")
        if self.image_processor.apply_ocr and (word_labels is not None): raise ValueError("You cannot provide word labels if you initialized the image processor with apply_ocr set to True.")
        if return_overflowing_tokens and not return_offsets_mapping: raise ValueError("You cannot return overflowing tokens without returning the offsets mapping.")
        if text_target is not None: return self.tokenizer(**output_kwargs["text_kwargs"])
        else:
            features = self.image_processor(images=images, **output_kwargs["images_kwargs"])
            features_words = features.pop("words", None)
            features_boxes = features.pop("boxes", None)
            output_kwargs["text_kwargs"].pop("text_target", None)
            output_kwargs["text_kwargs"].pop("text_pair_target", None)
            output_kwargs["text_kwargs"]["text_pair"] = text_pair
            output_kwargs["text_kwargs"]["boxes"] = boxes if boxes is not None else features_boxes
            output_kwargs["text_kwargs"]["word_labels"] = word_labels
            if text is not None and self.image_processor.apply_ocr and text_pair is None:
                if isinstance(text, str): text = [text]
                output_kwargs["text_kwargs"]["text_pair"] = features_words
            encoded_inputs = self.tokenizer(text=text if text is not None else features_words, **output_kwargs["text_kwargs"])
            if return_overflowing_tokens is True: features["pixel_values"] = self.get_overflowing_images(features["pixel_values"], encoded_inputs["overflow_to_sample_mapping"])
            features.update(encoded_inputs)
            return features
    def get_overflowing_images(self, images, overflow_to_sample_mapping):
        images_with_overflow = []
        for sample_idx in overflow_to_sample_mapping: images_with_overflow.append(images[sample_idx])
        if len(images_with_overflow) != len(overflow_to_sample_mapping): raise ValueError(f"Expected length of images to be the same as the length of `overflow_to_sample_mapping`, but got {len(images_with_overflow)} and {len(overflow_to_sample_mapping)}")
        return images_with_overflow
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def post_process_image_text_to_text(self, generated_outputs): return self.tokenizer.batch_decode(generated_outputs, skip_special_tokens=True)
    @property
    def model_input_names(self): return ["pixel_values", "input_ids", "bbox", "attention_mask"]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
