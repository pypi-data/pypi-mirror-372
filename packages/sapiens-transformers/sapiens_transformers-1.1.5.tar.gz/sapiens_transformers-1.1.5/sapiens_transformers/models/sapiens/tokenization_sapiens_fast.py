"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...tokenization_utils_fast import SapiensPreTrainedTokenizerFast
from .tokenization_sapiens import SapiensTokenizer
from typing import Optional as SAPIENSOptional, Tuple as SAPIENSTuple
from .sapiens_import_variables import VOCAB_FILES_NAMES_X as VOCAB_FILES_NAMES, MAX_MODEL_INPUT_SIZES_X as MAX_MODEL_INPUT_SIZES
class SapiensTokenizerFast(SapiensPreTrainedTokenizerFast):
    vocab_files_names, model_input_names, slow_tokenizer_class = VOCAB_FILES_NAMES, ["input_ids", "attention_mask"], SapiensTokenizer
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, unk_token="<|endoftext|>", bos_token=None, eos_token="<|endoftext|>", pad_token="<|endoftext|>", **kwargs):
        from ...tokenization_utils import SapiensAddedToken
        insert_unk_token = unk_token if type(unk_token) == str else "<|endoftext|>"
        unk_token = (SapiensAddedToken(unk_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(unk_token, str) else unk_token)
        insert_bos_token = bos_token if type(bos_token) == str else None
        bos_token = (SapiensAddedToken(bos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(bos_token, str) else bos_token)
        insert_eos_token = eos_token if type(eos_token) == str else "<|endoftext|>"
        eos_token = (SapiensAddedToken(eos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(eos_token, str) else eos_token)
        insert_pad_token = pad_token if type(pad_token) == str else "<|endoftext|>"
        pad_token = (SapiensAddedToken(pad_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(pad_token, str) else pad_token)
        super().__init__(vocab_file=vocab_file, merges_file=merges_file, tokenizer_file=tokenizer_file, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: SAPIENSOptional[str] = None) -> SAPIENSTuple[str]: return tuple(self._tokenizer.model.save(save_directory, name=filename_prefix))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
