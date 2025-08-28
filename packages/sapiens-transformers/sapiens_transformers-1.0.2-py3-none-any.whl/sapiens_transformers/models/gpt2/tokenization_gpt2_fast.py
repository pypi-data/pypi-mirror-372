"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
from typing import Optional, Tuple
from tokenizers import pre_tokenizers
from ...tokenization_utils_base import BatchEncoding
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from .tokenization_gpt2 import GPT2Tokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json", "merges_file": "merges.txt", "tokenizer_file": "tokenizer.json"}
class GPT2TokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = GPT2Tokenizer
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, unk_token="<|endoftext|>", bos_token="<|endoftext|>", eos_token="<|endoftext|>", add_prefix_space=False, **kwargs):
        super().__init__(vocab_file, merges_file, tokenizer_file=tokenizer_file, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, add_prefix_space=add_prefix_space, **kwargs)
        self.add_bos_token = kwargs.pop("add_bos_token", False)
        pre_tok_state = json.loads(self.backend_tokenizer.pre_tokenizer.__getstate__())
        if pre_tok_state.get("add_prefix_space", add_prefix_space) != add_prefix_space:
            pre_tok_class = getattr(pre_tokenizers, pre_tok_state.pop("type"))
            pre_tok_state["add_prefix_space"] = add_prefix_space
            self.backend_tokenizer.pre_tokenizer = pre_tok_class(**pre_tok_state)
        self.add_prefix_space = add_prefix_space
    def _batch_encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        assert self.add_prefix_space or not is_split_into_words, (f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._batch_encode_plus(*args, **kwargs)
    def _encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        assert self.add_prefix_space or not is_split_into_words, (f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._encode_plus(*args, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        files = self._tokenizer.model.save(save_directory, name=filename_prefix)
        return tuple(files)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
