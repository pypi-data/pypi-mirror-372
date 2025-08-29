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
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import is_sentencepiece_available, logging
if is_sentencepiece_available(): from .tokenization_pegasus import PegasusTokenizer
else: PegasusTokenizer = None
logger = logging.get_logger(__name__)
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model", "tokenizer_file": "tokenizer.json"}
class PegasusTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = PegasusTokenizer
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file=None, tokenizer_file=None, pad_token="<pad>", eos_token="</s>", unk_token="<unk>", mask_token="<mask_2>", mask_token_sent="<mask_1>",
    additional_special_tokens=None, offset=103, **kwargs):
        self.offset = offset
        if additional_special_tokens is not None:
            if not isinstance(additional_special_tokens, list): raise TypeError(f"additional_special_tokens should be of type {type(list)}, but is {type(additional_special_tokens)}")
            additional_special_tokens_extended = (([mask_token_sent] + additional_special_tokens) if mask_token_sent not in additional_special_tokens and mask_token_sent is not None else additional_special_tokens)
            additional_special_tokens_extended += [f"<unk_{i}>" for i in range(len(additional_special_tokens_extended), self.offset - 1)]
            if len(set(additional_special_tokens_extended)) != len(additional_special_tokens_extended): raise ValueError(f"Please make sure that the provided additional_special_tokens do not contain an incorrectly shifted list of <unk_x> tokens. Found {additional_special_tokens_extended}.")
            additional_special_tokens = additional_special_tokens_extended
        else:
            additional_special_tokens = [mask_token_sent] if mask_token_sent is not None else []
            additional_special_tokens += [f"<unk_{i}>" for i in range(2, self.offset)]
        from_slow = kwargs.pop("from_slow", None)
        from_slow = from_slow or str(pad_token) != "<pad>" or str(eos_token) != "</s>" or str(unk_token) != "<unk>"
        kwargs.pop("added_tokens_decoder", {})
        super().__init__(vocab_file, tokenizer_file=tokenizer_file, pad_token=pad_token, eos_token=eos_token, unk_token=unk_token, mask_token=mask_token,
        mask_token_sent=mask_token_sent, offset=offset, additional_special_tokens=additional_special_tokens, from_slow=from_slow, **kwargs)
        self.vocab_file = vocab_file
    @property
    def can_save_slow_tokenizer(self) -> bool: return os.path.isfile(self.vocab_file) if self.vocab_file else False
    def _special_token_mask(self, seq):
        all_special_ids = set(self.all_special_ids)
        all_special_ids.remove(self.unk_token_id)
        if all_special_ids != set(range(len(self.additional_special_tokens) + 3)): raise ValueError(f"There should be 3 special tokens: mask_token, pad_token, and eos_token + {len(self.additional_special_tokens)} additional_special_tokens, but got {all_special_ids}")
        return [1 if x in all_special_ids else 0 for x in seq]
    def get_special_tokens_mask(self, token_ids_0: List, token_ids_1: Optional[List] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return self._special_token_mask(token_ids_0)
        elif token_ids_1 is None: return self._special_token_mask(token_ids_0) + [1]
        else: return self._special_token_mask(token_ids_0 + token_ids_1) + [1]
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None) -> List[int]:
        if token_ids_1 is None: return token_ids_0 + [self.eos_token_id]
        return token_ids_0 + token_ids_1 + [self.eos_token_id]
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
