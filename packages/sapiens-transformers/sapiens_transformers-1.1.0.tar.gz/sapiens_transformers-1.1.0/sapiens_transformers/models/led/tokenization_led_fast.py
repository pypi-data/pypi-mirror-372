"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
from typing import Dict, List, Optional, Tuple, Union
from tokenizers import pre_tokenizers, processors
from ...tokenization_utils_base import AddedToken, BatchEncoding, EncodedInput
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import PaddingStrategy, logging
from .tokenization_led import LEDTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json", "merges_file": "merges.txt", "tokenizer_file": "tokenizer.json"}
class LEDTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = LEDTokenizer
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, errors="replace", bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>",
    unk_token="<unk>", pad_token="<pad>", mask_token="<mask>", add_prefix_space=False, trim_offsets=True, **kwargs):
        mask_token = (AddedToken(mask_token, lstrip=True, normalized=True, special=True) if isinstance(mask_token, str) else mask_token)
        super().__init__(vocab_file, merges_file, tokenizer_file=tokenizer_file, errors=errors, bos_token=bos_token, eos_token=eos_token, sep_token=sep_token,
        cls_token=cls_token, unk_token=unk_token, pad_token=pad_token, mask_token=mask_token, add_prefix_space=add_prefix_space, trim_offsets=trim_offsets, **kwargs)
        pre_tok_state = json.loads(self.backend_tokenizer.pre_tokenizer.__getstate__())
        if pre_tok_state.get("add_prefix_space", add_prefix_space) != add_prefix_space:
            pre_tok_class = getattr(pre_tokenizers, pre_tok_state.pop("type"))
            pre_tok_state["add_prefix_space"] = add_prefix_space
            self.backend_tokenizer.pre_tokenizer = pre_tok_class(**pre_tok_state)
        self.add_prefix_space = add_prefix_space
        tokenizer_component = "post_processor"
        tokenizer_component_instance = getattr(self.backend_tokenizer, tokenizer_component, None)
        if tokenizer_component_instance:
            state = json.loads(tokenizer_component_instance.__getstate__())
            if "sep" in state: state["sep"] = tuple(state["sep"])
            if "cls" in state: state["cls"] = tuple(state["cls"])
            changes_to_apply = False
            if state.get("add_prefix_space", add_prefix_space) != add_prefix_space:
                state["add_prefix_space"] = add_prefix_space
                changes_to_apply = True
            if state.get("trim_offsets", trim_offsets) != trim_offsets:
                state["trim_offsets"] = trim_offsets
                changes_to_apply = True
            if changes_to_apply:
                component_class = getattr(processors, state.pop("type"))
                new_value = component_class(**state)
                setattr(self.backend_tokenizer, tokenizer_component, new_value)
    @property
    def mask_token(self) -> str:
        if self._mask_token is None:
            if self.verbose: logger.error("Using mask_token, but it is not set yet.")
            return None
        return str(self._mask_token)
    @mask_token.setter
    def mask_token(self, value):
        value = AddedToken(value, lstrip=True, rstrip=False) if isinstance(value, str) else value
        self._mask_token = value
    def _batch_encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        if is_split_into_words and not self.add_prefix_space: raise ValueError(f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._batch_encode_plus(*args, **kwargs)
    def _encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        if is_split_into_words and not self.add_prefix_space: raise ValueError(f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._encode_plus(*args, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        files = self._tokenizer.model.save(save_directory, name=filename_prefix)
        return tuple(files)
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        output = [self.bos_token_id] + token_ids_0 + [self.eos_token_id]
        if token_ids_1 is None: return output
        return output + [self.eos_token_id] + token_ids_1 + [self.eos_token_id]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def _pad(self, encoded_inputs: Union[Dict[str, EncodedInput], BatchEncoding], max_length: Optional[int] = None, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_attention_mask: Optional[bool] = None) -> dict:
        encoded_inputs = super()._pad(encoded_inputs=encoded_inputs, max_length=max_length, padding_strategy=padding_strategy, pad_to_multiple_of=pad_to_multiple_of,
        padding_side=padding_side, return_attention_mask=return_attention_mask)
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        if return_attention_mask and "global_attention_mask" in encoded_inputs:
            required_input = encoded_inputs[self.model_input_names[0]]
            needs_to_be_padded = len(encoded_inputs["global_attention_mask"]) != len(required_input)
            if needs_to_be_padded:
                difference = len(required_input) - len(encoded_inputs["global_attention_mask"])
                if self.padding_side == "right": encoded_inputs["global_attention_mask"] = (encoded_inputs["global_attention_mask"] + [-1] * difference)
                elif self.padding_side == "left": encoded_inputs["global_attention_mask"] = [-1] * difference + encoded_inputs["global_attention_mask"]
                else: raise ValueError("Invalid padding strategy:" + str(self.padding_side))
        return encoded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
