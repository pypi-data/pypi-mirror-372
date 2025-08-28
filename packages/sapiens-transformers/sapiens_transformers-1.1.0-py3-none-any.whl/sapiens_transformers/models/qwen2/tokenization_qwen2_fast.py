"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Tuple
from ...tokenization_utils import AddedToken
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from .tokenization_qwen2 import Qwen2Tokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'merges_file': 'merges.txt', 'tokenizer_file': 'tokenizer.json'}
MAX_MODEL_INPUT_SIZES = {"qwen/qwen-tokenizer": 32768}
class Qwen2TokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = Qwen2Tokenizer
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, unk_token="<|endoftext|>", bos_token=None, eos_token="<|endoftext|>", pad_token="<|endoftext|>", **kwargs):
        bos_token = (AddedToken(bos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(bos_token, str) else bos_token)
        eos_token = (AddedToken(eos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(eos_token, str) else eos_token)
        unk_token = (AddedToken(unk_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(unk_token, str) else unk_token)
        pad_token = (AddedToken(pad_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(pad_token, str) else pad_token)
        super().__init__(vocab_file=vocab_file, merges_file=merges_file, tokenizer_file=tokenizer_file, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token,
        pad_token=pad_token, **kwargs)
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
