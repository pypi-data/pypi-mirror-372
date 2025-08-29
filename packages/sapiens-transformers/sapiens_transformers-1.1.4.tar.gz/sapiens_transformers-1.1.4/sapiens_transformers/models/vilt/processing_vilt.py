"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import List, Optional, Union
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding, PaddingStrategy, PreTokenizedInput, TextInput, TruncationStrategy
from ...utils import TensorType
class ViltProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "ViltImageProcessor"
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn("The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor` instead.", FutureWarning)
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(self, images, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchEncoding:
        encoding = self.tokenizer(text=text, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride,
        pad_to_multiple_of=pad_to_multiple_of, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose,
        return_tensors=return_tensors, **kwargs)
        encoding_image_processor = self.image_processor(images, return_tensors=return_tensors)
        encoding.update(encoding_image_processor)
        return encoding
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
    @property
    def feature_extractor_class(self):
        warnings.warn("`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.", FutureWarning)
        return self.image_processor_class
    @property
    def feature_extractor(self):
        warnings.warn("`feature_extractor` is deprecated and will be removed in v5. Use `image_processor` instead.", FutureWarning)
        return self.image_processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
