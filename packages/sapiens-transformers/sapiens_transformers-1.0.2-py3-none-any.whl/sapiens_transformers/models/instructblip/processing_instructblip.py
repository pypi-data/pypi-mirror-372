"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Union
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import (AddedToken, BatchEncoding, PreTokenizedInput, TextInput)
from ...utils import logging
from ..auto import AutoTokenizer
logger = logging.get_logger(__name__)
class InstructBlipProcessorKwargs(ProcessingKwargs, total=False): _defaults = {"text_kwargs": {'add_special_tokens': True, 'padding': False, 'stride': 0, 'return_overflowing_tokens': False,
'return_special_tokens_mask': False, 'return_offsets_mapping': False, 'return_token_type_ids': False, 'return_length': False, 'verbose': True}, "images_kwargs": {}}
class InstructBlipProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer", "qformer_tokenizer"]
    valid_kwargs = ["num_query_tokens"]
    image_processor_class = "BlipImageProcessor"
    tokenizer_class = "AutoTokenizer"
    qformer_tokenizer_class = "AutoTokenizer"
    def __init__(self, image_processor, tokenizer, qformer_tokenizer, num_query_tokens=None, **kwargs):
        self.image_token = AddedToken("<image>", normalized=False, special=True)
        tokenizer.add_tokens([self.image_token], special_tokens=True)
        self.num_query_tokens = num_query_tokens
        super().__init__(image_processor, tokenizer, qformer_tokenizer)
    def __call__(self, images: ImageInput = None, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, audio=None, videos=None,
    **kwargs: Unpack[InstructBlipProcessorKwargs]) -> BatchFeature:
        if images is None and text is None: raise ValueError("You have to specify at least images or text.")
        output_kwargs = self._merge_kwargs(InstructBlipProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs)
        encoding = BatchFeature()
        if text is not None:
            if isinstance(text, str): text = [text]
            elif not isinstance(text, list) and not isinstance(text[0], str): raise ValueError("Invalid input text. Please provide a string, or a list of strings")
            _text_encoding = self.tokenizer(text, **output_kwargs["text_kwargs"])
            if self.num_query_tokens is not None and images is not None:
                text_encoding = {}
                image_tokens = self.image_token.content * self.num_query_tokens
                image_token_encoding = self.tokenizer([image_tokens], add_special_tokens=False, return_tensors=None)
                for k in _text_encoding: text_encoding[k] = [img_encoding + txt_encoding for img_encoding, txt_encoding in zip(image_token_encoding[k], _text_encoding[k])]
            else:
                text_encoding = _text_encoding
                if images is not None: logger.warning_once("Expanding inputs for image tokens in InstructBLIP should be done in processing. Please follow instruction here (https://gist.github.com/zucchini-nlp/e9f20b054fa322f84ac9311d9ab67042) to update your InstructBLIP model. Using processors without these attributes in the config is deprecated and will throw an error in v1.0.")
            text_encoding = BatchEncoding(text_encoding, tensor_type=output_kwargs["common_kwargs"].get("return_tensors"))
            encoding.update(text_encoding)
            qformer_text_encoding = self.qformer_tokenizer(text, **output_kwargs["text_kwargs"])
            encoding["qformer_input_ids"] = qformer_text_encoding.pop("input_ids")
            encoding["qformer_attention_mask"] = qformer_text_encoding.pop("attention_mask")
        if images is not None:
            image_encoding = self.image_processor(images, **output_kwargs["images_kwargs"])
            encoding.update(image_encoding)
        return encoding
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    def save_pretrained(self, save_directory, **kwargs):
        if os.path.isfile(save_directory): raise ValueError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        qformer_tokenizer_path = os.path.join(save_directory, "qformer_tokenizer")
        self.qformer_tokenizer.save_pretrained(qformer_tokenizer_path)
        qformer_present = "qformer_tokenizer" in self.attributes
        if qformer_present: self.attributes.remove("qformer_tokenizer")
        outputs = super().save_pretrained(save_directory, **kwargs)
        if qformer_present: self.attributes += ["qformer_tokenizer"]
        return outputs
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        processor = super().from_pretrained(pretrained_model_name_or_path, **kwargs)
        if isinstance(processor, tuple): processor = processor[0]
        qformer_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, subfolder="qformer_tokenizer")
        processor.qformer_tokenizer = qformer_tokenizer
        return processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
