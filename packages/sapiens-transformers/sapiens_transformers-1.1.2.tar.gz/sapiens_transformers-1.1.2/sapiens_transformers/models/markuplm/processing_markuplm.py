"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Union
from ...file_utils import TensorType
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding, PaddingStrategy, TruncationStrategy
class MarkupLMProcessor(ProcessorMixin):
    feature_extractor_class = "MarkupLMFeatureExtractor"
    tokenizer_class = ("MarkupLMTokenizer", "MarkupLMTokenizerFast")
    parse_html = True
    def __call__(self, html_strings=None, nodes=None, xpaths=None, node_labels=None, questions=None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True,
    return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchEncoding:
        if self.parse_html:
            if html_strings is None: raise ValueError("Make sure to pass HTML strings in case `parse_html` is set to `True`")
            if nodes is not None or xpaths is not None or node_labels is not None: raise ValueError("Please don't pass nodes, xpaths nor node labels in case `parse_html` is set to `True`")
            features = self.feature_extractor(html_strings)
            nodes = features["nodes"]
            xpaths = features["xpaths"]
        else:
            if html_strings is not None: raise ValueError("You have passed HTML strings but `parse_html` is set to `False`.")
            if nodes is None or xpaths is None: raise ValueError("Make sure to pass nodes and xpaths in case `parse_html` is set to `False`")
        if questions is not None and self.parse_html:
            if isinstance(questions, str): questions = [questions]
        encoded_inputs = self.tokenizer(text=questions if questions is not None else nodes, text_pair=nodes if questions is not None else None, xpaths=xpaths,
        node_labels=node_labels, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride,
        pad_to_multiple_of=pad_to_multiple_of, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
        return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose,
        return_tensors=return_tensors, **kwargs)
        return encoded_inputs
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        return tokenizer_input_names
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
