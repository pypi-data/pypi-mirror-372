"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import PaddingStrategy, PreTokenizedInput, TextInput, TruncationStrategy
from ...utils import TensorType
class ChameleonProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    tokenizer_class = ("LlamaTokenizer", "LlamaTokenizerFast")
    image_processor_class = "ChameleonImageProcessor"
    def __init__(self, image_processor, tokenizer, image_seq_length: int = 1024, image_token: str = "<image>"):
        self.image_seq_length = image_seq_length
        self.image_token = image_token
        self.image_start_token = "<racm3:break>"
        self.image_end_token = "<eoss>"
        super().__init__(image_processor, tokenizer)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, images: ImageInput = None, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: int = None, return_tensors: Optional[Union[str, TensorType]] = TensorType.PYTORCH, return_for_text_completion: bool = False) -> BatchFeature:
        if isinstance(text, str): text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str): raise TypeError("Invalid input text. Please provide a string, or a list of strings")
        prompt_strings = []
        one_img_tokens = self.image_start_token + (self.image_token * self.image_seq_length) + self.image_end_token
        for sample in text:
            sample = sample.replace(self.image_token, one_img_tokens)
            if not return_for_text_completion: sample += self.tokenizer.sep_token
            prompt_strings.append(sample)
        data = self.tokenizer(prompt_strings, return_tensors=return_tensors, padding=padding, truncation=truncation, max_length=max_length)
        if images is not None:
            pixel_values = self.image_processor(images, return_tensors=return_tensors)["pixel_values"]
            data["pixel_values"] = pixel_values
        return BatchFeature(data=data, tensor_type=return_tensors)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
