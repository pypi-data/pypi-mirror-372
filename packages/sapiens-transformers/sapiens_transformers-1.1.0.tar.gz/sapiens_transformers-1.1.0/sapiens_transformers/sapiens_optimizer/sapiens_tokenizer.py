from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import (List, Optional, Any)
import sapiens_transformers.sapiens_optimizer
from .sapiens_types import List
import abc
class BaseSapiensTokenizer(abc.ABC):
    @abc.abstractmethod
    def tokenize(self, text: bytes, add_bos: bool = True, special: bool = True) -> List[int]: raise NotImplementedError
    @abc.abstractmethod
    def detokenize(self, tokens: List[int], prev_tokens: Optional[List[int]] = None, special: bool = False) -> bytes: raise NotImplementedError
class SapiensTokenizer(BaseSapiensTokenizer):
    def __init__(self, llama: sapiens_optimizer.Sapiens): self._model = llama._model
    def tokenize(self, text: bytes, add_bos: bool = True, special: bool = True) -> List[int]: return self._model.tokenize(text, add_bos=add_bos, special=special)
    def detokenize(self, tokens: List[int], prev_tokens: Optional[List[int]] = None, special: bool = False) -> bytes: return self._model.detokenize(tokens, special=special)
    def encode(self, text: str, add_bos: bool = True, special: bool = True) -> List[int]: return self.tokenize(text.encode("utf-8", errors="ignore"), add_bos=add_bos, special=special)
    def decode(self, tokens: List[int]) -> str: return self.detokenize(tokens).decode("utf-8", errors="ignore")
    @classmethod
    def from_ggml_file(cls, path: str) -> "SapiensTokenizer": return cls(sapiens_optimizer.Sapiens(model_path=path, vocab_only=True))
class SapiensHFTokenizer(BaseSapiensTokenizer):
    def __init__(self, hf_tokenizer: Any): self.hf_tokenizer = hf_tokenizer
    def tokenize(self, text: bytes, add_bos: bool = True, special: bool = True) -> List[int]: return self.hf_tokenizer.encode(text.decode("utf-8", errors="ignore"), add_special_tokens=special)
    def detokenize(self, tokens: List[int], prev_tokens: Optional[List[int]] = None, special: bool = False) -> bytes:
        skip_special_tokens = not special
        if prev_tokens is not None:
            text = self.hf_tokenizer.decode(prev_tokens + tokens, skip_special_tokens=skip_special_tokens).encode("utf-8", errors="ignore")
            prev_text = self.hf_tokenizer.decode(prev_tokens, skip_special_tokens=skip_special_tokens).encode("utf-8", errors="ignore")
            return text[len(prev_text) :]
        else: return self.hf_tokenizer.decode(tokens, skip_special_tokens=skip_special_tokens).encode("utf-8", errors="ignore")
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str) -> "SapiensHFTokenizer":
        try: from sapiens_transformers import AutoTokenizer
        except ImportError: raise ImportError("The `transformers` library is required to use the `HFTokenizer`. You can install it with `pip install transformers`.")
        hf_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=pretrained_model_name_or_path)
        return cls(hf_tokenizer)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
