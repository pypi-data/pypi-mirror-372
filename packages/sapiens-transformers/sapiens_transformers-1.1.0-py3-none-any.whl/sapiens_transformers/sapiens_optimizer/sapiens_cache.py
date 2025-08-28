"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import (Optional, Sequence, Tuple)
import sapiens_transformers.sapiens_optimizer.llama
from collections import OrderedDict
from abc import ABC, abstractmethod
from .sapiens_types import *
import diskcache
import sys
class BaseSapiensCache(ABC):
    def __init__(self, capacity_bytes: int = (2 << 30)): self.capacity_bytes = capacity_bytes
    @property
    @abstractmethod
    def cache_size(self) -> int: raise NotImplementedError
    def _find_longest_prefix_key(self, key: Tuple[int, ...]) -> Optional[Tuple[int, ...]]: pass
    @abstractmethod
    def __getitem__(self, key: Sequence[int]) -> "sapiens_optimizer.llama.SapiensState": raise NotImplementedError
    @abstractmethod
    def __contains__(self, key: Sequence[int]) -> bool: raise NotImplementedError
    @abstractmethod
    def __setitem__(self, key: Sequence[int], value: "sapiens_optimizer.llama.SapiensState") -> None: raise NotImplementedError
class SapiensRAMCache(BaseSapiensCache):
    def __init__(self, capacity_bytes: int = (2 << 30)):
        super().__init__(capacity_bytes)
        self.capacity_bytes = capacity_bytes
        self.cache_state: OrderedDict[Tuple[int, ...], "sapiens_optimizer.llama.SapiensState"] = OrderedDict()
    @property
    def cache_size(self): return sum([state.llama_state_size for state in self.cache_state.values()])
    def _find_longest_prefix_key(self, key: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
        min_len = 0
        min_key = None
        keys = ((k, sapiens_optimizer.llama.Sapiens.longest_token_prefix(k, key)) for k in self.cache_state.keys())
        for k, prefix_len in keys:
            if prefix_len > min_len:
                min_len = prefix_len
                min_key = k
        return min_key
    def __getitem__(self, key: Sequence[int]) -> "sapiens_optimizer.llama.SapiensState":
        key = tuple(key)
        _key = self._find_longest_prefix_key(key)
        if _key is None: raise KeyError("Key not found")
        value = self.cache_state[_key]
        self.cache_state.move_to_end(_key)
        return value
    def __contains__(self, key: Sequence[int]) -> bool: return self._find_longest_prefix_key(tuple(key)) is not None
    def __setitem__(self, key: Sequence[int], value: "sapiens_optimizer.llama.SapiensState"):
        key = tuple(key)
        if key in self.cache_state: del self.cache_state[key]
        self.cache_state[key] = value
        while self.cache_size > self.capacity_bytes and len(self.cache_state) > 0: self.cache_state.popitem(last=False)
SapiensCache = SapiensRAMCache
class SapiensDiskCache(BaseSapiensCache):
    def __init__(self, cache_dir: str = ".cache/sapiens_cache", capacity_bytes: int = (2 << 30)):
        super().__init__(capacity_bytes)
        self.cache = diskcache.Cache(cache_dir)
    @property
    def cache_size(self): return int(self.cache.volume())
    def _find_longest_prefix_key(self, key: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
        min_len = 0
        min_key: Optional[Tuple[int, ...]] = None
        for k in self.cache.iterkeys():
            prefix_len = sapiens_optimizer.llama.Sapiens.longest_token_prefix(k, key)
            if prefix_len > min_len:
                min_len = prefix_len
                min_key = k
        return min_key
    def __getitem__(self, key: Sequence[int]) -> "sapiens_optimizer.llama.SapiensState":
        key = tuple(key)
        _key = self._find_longest_prefix_key(key)
        if _key is None: raise KeyError("Key not found")
        value: "sapiens_optimizer.llama.SapiensState" = self.cache.pop(_key)
        return value
    def __contains__(self, key: Sequence[int]) -> bool: return self._find_longest_prefix_key(tuple(key)) is not None
    def __setitem__(self, key: Sequence[int], value: "sapiens_optimizer.llama.SapiensState"):
        key = tuple(key)
        if key in self.cache: del self.cache[key]
        self.cache[key] = value
        while self.cache_size > self.capacity_bytes and len(self.cache) > 0:
            key_to_remove = next(iter(self.cache))
            del self.cache[key_to_remove]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
