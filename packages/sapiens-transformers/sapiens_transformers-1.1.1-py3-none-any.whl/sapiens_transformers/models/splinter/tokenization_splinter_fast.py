"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
from typing import List, Optional, Tuple
from tokenizers import normalizers
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from .tokenization_splinter import SplinterTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt"}
class SplinterTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = SplinterTokenizer
    def __init__(self, vocab_file=None, tokenizer_file=None, do_lower_case=True, unk_token="[UNK]", sep_token="[SEP]", pad_token="[PAD]", cls_token="[CLS]",
    mask_token="[MASK]", question_token="[QUESTION]", tokenize_chinese_chars=True, strip_accents=None, **kwargs):
        super().__init__(vocab_file, tokenizer_file=tokenizer_file, do_lower_case=do_lower_case, unk_token=unk_token, sep_token=sep_token, pad_token=pad_token,
        cls_token=cls_token, mask_token=mask_token, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents, additional_special_tokens=(question_token,), **kwargs)
        pre_tok_state = json.loads(self.backend_tokenizer.normalizer.__getstate__())
        if (pre_tok_state.get("lowercase", do_lower_case) != do_lower_case or pre_tok_state.get("strip_accents", strip_accents) != strip_accents):
            pre_tok_class = getattr(normalizers, pre_tok_state.pop("type"))
            pre_tok_state["lowercase"] = do_lower_case
            pre_tok_state["strip_accents"] = strip_accents
            self.backend_tokenizer.normalizer = pre_tok_class(**pre_tok_state)
        self.do_lower_case = do_lower_case
    @property
    def question_token_id(self): return self.convert_tokens_to_ids(self.question_token)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        question_suffix = [self.question_token_id] + [self.convert_tokens_to_ids(".")]
        if self.padding_side == "right": return cls + token_ids_0 + question_suffix + sep + token_ids_1 + sep
        else: return cls + token_ids_0 + sep + token_ids_1 + question_suffix + sep
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        question_suffix = [self.question_token_id] + [self.convert_tokens_to_ids(".")]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        if self.padding_side == "right": return len(cls + token_ids_0 + question_suffix + sep) * [0] + len(token_ids_1 + sep) * [1]
        else: return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + question_suffix + sep) * [1]
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
