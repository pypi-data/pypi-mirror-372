"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import List, Optional, Tuple
from ...tokenization_utils import AddedToken
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import is_sentencepiece_available, logging
if is_sentencepiece_available(): from .tokenization_xlnet import XLNetTokenizer
else: XLNetTokenizer = None
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model", "tokenizer_file": "tokenizer.json"}
SPIECE_UNDERLINE = "▁"
SEG_ID_A = 0
SEG_ID_B = 1
SEG_ID_CLS = 2
SEG_ID_SEP = 3
SEG_ID_PAD = 4
class XLNetTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    padding_side = "left"
    slow_tokenizer_class = XLNetTokenizer
    def __init__(self, vocab_file=None, tokenizer_file=None, do_lower_case=False, remove_space=True, keep_accents=False, bos_token="<s>", eos_token="</s>", unk_token="<unk>",
    sep_token="<sep>", pad_token="<pad>", cls_token="<cls>", mask_token="<mask>", additional_special_tokens=["<eop>", "<eod>"], **kwargs):
        mask_token = AddedToken(mask_token, lstrip=True, rstrip=False) if isinstance(mask_token, str) else mask_token
        super().__init__(vocab_file=vocab_file, tokenizer_file=tokenizer_file, do_lower_case=do_lower_case, remove_space=remove_space, keep_accents=keep_accents,
        bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, sep_token=sep_token, pad_token=pad_token, cls_token=cls_token, mask_token=mask_token,
        additional_special_tokens=additional_special_tokens, **kwargs)
        self._pad_token_type_id = 3
        self.do_lower_case = do_lower_case
        self.remove_space = remove_space
        self.keep_accents = keep_accents
        self.vocab_file = vocab_file
    @property
    def can_save_slow_tokenizer(self) -> bool: return os.path.isfile(self.vocab_file) if self.vocab_file else False
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return token_ids_0 + sep + cls
        return token_ids_0 + sep + token_ids_1 + sep + cls
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls_segment_id = [2]
        if token_ids_1 is None: return len(token_ids_0 + sep) * [0] + cls_segment_id
        return len(token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1] + cls_segment_id
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not self.can_save_slow_tokenizer: raise ValueError("Your fast tokenizer does not have the necessary information to save the vocabulary for a slow tokenizer.")
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file): copyfile(self.vocab_file, out_vocab_file)
        return (out_vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
