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
class SiglipProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "SiglipImageProcessor"
    tokenizer_class = "SiglipTokenizer"
    def __init__(self, image_processor, tokenizer): super().__init__(image_processor, tokenizer)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, images: ImageInput = None, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: int = None, return_tensors: Optional[Union[str, TensorType]] = TensorType.PYTORCH) -> BatchFeature:
        if text is None and images is None: raise ValueError("You have to specify either text or images. Both cannot be none.")
        if text is not None: encoding = self.tokenizer(text, return_tensors=return_tensors, padding=padding, truncation=truncation, max_length=max_length)
        if images is not None: image_features = self.image_processor(images, return_tensors=return_tensors)
        if text is not None and images is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif text is not None: return encoding
        else: return BatchFeature(data=dict(**image_features), tensor_type=return_tensors)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
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
