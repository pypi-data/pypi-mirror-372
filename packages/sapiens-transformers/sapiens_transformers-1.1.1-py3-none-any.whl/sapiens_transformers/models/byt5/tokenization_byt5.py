"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import List, Optional, Tuple
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
class ByT5Tokenizer(PreTrainedTokenizer):
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, eos_token="</s>", unk_token="<unk>", pad_token="<pad>", extra_ids=125, additional_special_tokens=None, **kwargs) -> None:
        if extra_ids > 0 and additional_special_tokens is None: additional_special_tokens = [f"<extra_id_{i}>" for i in range(extra_ids)]
        elif extra_ids > 0 and additional_special_tokens is not None and len(additional_special_tokens) > 0:
            extra_tokens = len(set(filter(lambda x: bool("extra_id" in str(x)), additional_special_tokens)))
            if extra_tokens != extra_ids: raise ValueError(f"Both extra_ids ({extra_ids}) and additional_special_tokens ({additional_special_tokens}) are provided to ByT5Tokenizer. In this case the additional_special_tokens must include the extra_ids tokens")
        pad_token = AddedToken(pad_token, lstrip=True, rstrip=True) if isinstance(pad_token, str) else pad_token
        eos_token = AddedToken(eos_token, lstrip=True, rstrip=True) if isinstance(eos_token, str) else eos_token
        unk_token = AddedToken(unk_token, lstrip=True, rstrip=True) if isinstance(unk_token, str) else unk_token
        self._added_tokens_decoder = {0: pad_token, 1: eos_token, 2: unk_token}
        self.offset = len(self._added_tokens_decoder)
        self._utf_vocab_size = 2**8
        super().__init__(eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, extra_ids=0, additional_special_tokens=additional_special_tokens, **kwargs)
    @property
    def vocab_size(self): return self._utf_vocab_size
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size + self.offset)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return ([0] * len(token_ids_0)) + [1]
        return ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
    def _add_eos_if_not_present(self, token_ids: List[int]) -> List[int]:
        if len(token_ids) > 0 and token_ids[-1] == self.eos_token_id:
            warnings.warn(f"This sequence already has {self.eos_token}. In future versions this behavior may lead to duplicated eos tokens being added.")
            return token_ids
        else: return token_ids + [self.eos_token_id]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        eos = [self.eos_token_id]
        if token_ids_1 is None: return len(token_ids_0 + eos) * [0]
        return len(token_ids_0 + eos + token_ids_1 + eos) * [0]
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        token_ids_0 = self._add_eos_if_not_present(token_ids_0)
        if token_ids_1 is None: return token_ids_0
        else:
            token_ids_1 = self._add_eos_if_not_present(token_ids_1)
            return token_ids_0 + token_ids_1
    def _tokenize(self, text: str) -> List[str]:
        tokens = [chr(i) for i in text.encode("utf-8")]
        return tokens
    def _convert_token_to_id(self, token):
        if len(token) != 1: token_id = None
        else: token_id = ord(token) + self.offset
        return token_id
    def _convert_id_to_token(self, index):
        token = chr(index - self.offset)
        return token
    def convert_tokens_to_string(self, tokens):
        bstring = b""
        for token in tokens:
            if token in self.added_tokens_decoder: tok_string = self.added_tokens_decoder[token].encode("utf-8")
            elif token in self.added_tokens_encoder: tok_string = token.encode("utf-8")
            else: tok_string = bytes([ord(token)])
            bstring += tok_string
        string = bstring.decode("utf-8", errors="ignore")
        return string
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]: return ()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
