"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
UNICODE_VOCAB_SIZE = 1114112
PAD = 0
CLS = 0xE000
SEP = 0xE001
BOS = 0xE002
MASK = 0xE003
RESERVED = 0xE004
SPECIAL_CODEPOINTS: Dict[int, str] = {CLS: "[CLS]", SEP: "[SEP]", BOS: "[BOS]", MASK: "[MASK]", PAD: "[PAD]", RESERVED: "[RESERVED]"}
SPECIAL_CODEPOINTS_BY_NAME: Dict[str, int] = {name: codepoint for codepoint, name in SPECIAL_CODEPOINTS.items()}
class CanineTokenizer(PreTrainedTokenizer):
    def __init__(self, bos_token=chr(CLS), eos_token=chr(SEP), sep_token=chr(SEP), cls_token=chr(CLS), pad_token=chr(PAD), mask_token=chr(MASK),
    add_prefix_space=False, model_max_length=2048, **kwargs):
        bos_token = AddedToken(bos_token, lstrip=False, rstrip=False) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, lstrip=False, rstrip=False) if isinstance(eos_token, str) else eos_token
        sep_token = AddedToken(sep_token, lstrip=False, rstrip=False) if isinstance(sep_token, str) else sep_token
        cls_token = AddedToken(cls_token, lstrip=False, rstrip=False) if isinstance(cls_token, str) else cls_token
        pad_token = AddedToken(pad_token, lstrip=False, rstrip=False) if isinstance(pad_token, str) else pad_token
        mask_token = AddedToken(mask_token, lstrip=True, rstrip=False) if isinstance(mask_token, str) else mask_token
        self._special_codepoints: Dict[str, int] = {}
        for codepoint, name in SPECIAL_CODEPOINTS.items(): self._special_codepoints[name] = codepoint
        self._special_codepoint_strings: Dict[int, str] = {codepoint: name for name, codepoint in self._special_codepoints.items()}
        self._unicode_vocab_size = UNICODE_VOCAB_SIZE
        self._num_special_tokens = len(self._special_codepoints)
        super().__init__(bos_token=bos_token, eos_token=eos_token, sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, mask_token=mask_token,
        add_prefix_space=add_prefix_space, model_max_length=model_max_length, **kwargs)
    @property
    def vocab_size(self) -> int: return self._unicode_vocab_size
    def get_vocab(self):
        vocab = {chr(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text: str) -> List[str]: return list(text)
    def _convert_token_to_id(self, token: str) -> int:
        try: return ord(token)
        except TypeError: raise ValueError(f"invalid token: '{token}'")
    def _convert_id_to_token(self, index: int) -> str:
        try:
            if index in SPECIAL_CODEPOINTS: return SPECIAL_CODEPOINTS[index]
            return chr(index)
        except TypeError: raise ValueError(f"invalid id: {index}")
    def convert_tokens_to_string(self, tokens): return "".join(tokens)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        result = cls + token_ids_0 + sep
        if token_ids_1 is not None: result += token_ids_1 + sep
        return result
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        result = [1] + ([0] * len(token_ids_0)) + [1]
        if token_ids_1 is not None: result += ([0] * len(token_ids_1)) + [1]
        return result
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        result = len(cls + token_ids_0 + sep) * [0]
        if token_ids_1 is not None: result += len(token_ids_1 + sep) * [1]
        return result
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None): return ()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
