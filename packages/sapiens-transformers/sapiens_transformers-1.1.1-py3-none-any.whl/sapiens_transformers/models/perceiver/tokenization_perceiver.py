"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional, Tuple
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
class PerceiverTokenizer(PreTrainedTokenizer):
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, pad_token="[PAD]", bos_token="[BOS]", eos_token="[EOS]", mask_token="[MASK]", cls_token="[CLS]", sep_token="[SEP]",
    model_max_length=2048, **kwargs) -> None:
        pad_token = AddedToken(pad_token, lstrip=False, rstrip=False) if isinstance(pad_token, str) else pad_token
        bos_token = AddedToken(bos_token, lstrip=False, rstrip=False) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, lstrip=False, rstrip=False) if isinstance(eos_token, str) else eos_token
        mask_token = AddedToken(mask_token, lstrip=False, rstrip=False) if isinstance(mask_token, str) else mask_token
        cls_token = AddedToken(cls_token, lstrip=False, rstrip=False) if isinstance(cls_token, str) else cls_token
        sep_token = AddedToken(sep_token, lstrip=False, rstrip=False) if isinstance(sep_token, str) else sep_token
        self._utf_vocab_size = 2**8
        self._added_tokens_decoder: Dict[str, int] = {0: pad_token, 1: bos_token, 2: eos_token, 3: mask_token, 4: cls_token, 5: sep_token}
        self._num_special_tokens = len(self._added_tokens_decoder)
        super().__init__(pad_token=pad_token, bos_token=bos_token, eos_token=eos_token, mask_token=mask_token, cls_token=cls_token,
        sep_token=sep_token, model_max_length=model_max_length, **kwargs)
    def get_vocab(self) -> Dict[str, int]:
        vocab = {}
        for i in range(self._utf_vocab_size):
            token = chr(i)
            vocab[token] = i + self._num_special_tokens
        vocab.update(self.added_tokens_encoder)
        return vocab
    @property
    def vocab_size(self): return self._utf_vocab_size
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + [0] * len(token_ids_0) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        else: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id] + token_ids_1 + [self.sep_token_id]
    def _tokenize(self, text: str) -> List[str]:
        tokens = [chr(i) for i in text.encode("utf-8")]
        return tokens
    def _convert_token_to_id(self, token):
        if len(token) != 1: token_id = self.unk_token_id
        else: token_id = ord(token) + self._num_special_tokens
        return token_id
    def _convert_id_to_token(self, index):
        token = chr(index - self._num_special_tokens)
        return token
    def convert_tokens_to_string(self, tokens):
        bstring = b""
        for token in tokens:
            if token in self.added_tokens_encoder: tok_string = str(token).encode("utf-8")
            else: tok_string = bytes([ord(token)])
            bstring += tok_string
        string = bstring.decode("utf-8", errors="replace")
        return string
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]: return ()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
