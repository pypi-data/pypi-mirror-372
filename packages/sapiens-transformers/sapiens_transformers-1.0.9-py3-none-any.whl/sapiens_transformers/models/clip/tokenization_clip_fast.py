"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Tuple
from tokenizers import pre_tokenizers
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from .tokenization_clip import CLIPTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json", "merges_file": "merges.txt", "tokenizer_file": "tokenizer.json"}
class CLIPTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = CLIPTokenizer
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, unk_token="<|endoftext|>", bos_token="<|startoftext|>", eos_token="<|endoftext|>", pad_token="<|endoftext|>", **kwargs):
        super().__init__(vocab_file, merges_file, tokenizer_file=tokenizer_file, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, **kwargs)
        if not isinstance(self.backend_tokenizer.pre_tokenizer, pre_tokenizers.Sequence): raise ValueError("The `backend_tokenizer` provided does not match the expected format. The CLIP tokenizer has been heavily modified from sapiens_transformers version 1.0.0. You need to convert the tokenizer you are using to be compatible with this version.The easiest way to do so is"+' `CLIPTokenizerFast.from_pretrained("path_to_local_folder_or_hub_repo, from_slow=True)`. If you want'+" to use your existing tokenizer, you will have to revert to a version prior to 1.0.0 of sapiens transformers.")
        self._wrap_decode_method_backend_tokenizer()
    def _wrap_decode_method_backend_tokenizer(self):
        orig_decode_method = self.backend_tokenizer.decode
        end_of_word_suffix = self.backend_tokenizer.model.end_of_word_suffix
        def new_decode_method(*args, **kwargs):
            text = orig_decode_method(*args, **kwargs)
            text = text.replace(end_of_word_suffix, " ").strip()
            return text
        self.backend_tokenizer.decode = new_decode_method
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        bos_token = [self.bos_token_id]
        eos_token = [self.eos_token_id]
        if token_ids_1 is None: return bos_token + token_ids_0 + eos_token
        return bos_token + token_ids_0 + eos_token + eos_token + token_ids_1 + eos_token
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        bos_token = [self.bos_token_id]
        eos_token = [self.eos_token_id]
        if token_ids_1 is None: return len(bos_token + token_ids_0 + eos_token) * [0]
        return len(bos_token + token_ids_0 + eos_token + eos_token + token_ids_1 + eos_token) * [0]
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
