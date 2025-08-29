"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import is_hqq_available, is_quanto_available, is_torchdynamo_compiling, logging
from typing import Any, Dict, List, Optional, Tuple, Union
from .configuration_utils import PretrainedConfig
from .utils.deprecation import deprecate_kwarg
from dataclasses import dataclass
from packaging import version
import importlib.metadata
import torch
import json
import copy
import os
if is_quanto_available():
    quanto_version = version.parse(importlib.metadata.version("quanto"))
    if quanto_version >= version.parse("0.2.0"): from quanto import AffineQuantizer, MaxOptimizer, qint2, qint4
if is_hqq_available(): from hqq.core.quantize import Quantizer as HQQQuantizer
logger = logging.get_logger(__name__)
class Cache(torch.nn.Module):
    def __init__(self): super().__init__()
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]: raise NotImplementedError("Make sure to implement `update` in a subclass.")
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int: raise NotImplementedError("Make sure to implement `get_seq_length` in a subclass.")
    def get_max_length(self) -> Optional[int]: raise NotImplementedError("Make sure to implement `get_max_length` in a subclass.")
    def get_usable_length(self, new_seq_length: int, layer_idx: Optional[int] = 0) -> int:
        max_length = self.get_max_length()
        previous_seq_length = self.get_seq_length(layer_idx)
        if max_length is not None and previous_seq_length + new_seq_length > max_length: return max_length - new_seq_length
        return previous_seq_length
    def reorder_cache(self, beam_idx: torch.LongTensor):
        for layer_idx in range(len(self.key_cache)):
            if self.key_cache[layer_idx] != []:
                device = self.key_cache[layer_idx].device
                self.key_cache[layer_idx] = self.key_cache[layer_idx].index_select(0, beam_idx.to(device))
            if self.value_cache[layer_idx] != []:
                device = self.value_cache[layer_idx].device
                self.value_cache[layer_idx] = self.value_cache[layer_idx].index_select(0, beam_idx.to(device))
    @property
    def seen_tokens(self):
        logger.warning_once("The `seen_tokens` attribute is deprecated and will be removed in v4.41. Use the `cache_position` model input instead.")
        if hasattr(self, "_seen_tokens"): return self._seen_tokens
        else: return None
@dataclass
class CacheConfig:
    cache_implementation: None
    @classmethod
    def from_dict(cls, config_dict, **kwargs):
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
            writer.write(json_string)
    def to_dict(self) -> Dict[str, Any]: return copy.deepcopy(self.__dict__)
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items(): yield attr, value
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_json_string(self): return json.dumps(self.__dict__, indent=2) + "\n"
    def update(self, **kwargs):
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs
@dataclass
class QuantizedCacheConfig(CacheConfig):
    def __init__(self, backend: str = "quanto", nbits: Optional[int] = 4, axis_key: Optional[int] = 0, axis_value: Optional[int] = 0, q_group_size: Optional[int] = 64,
    residual_length: Optional[int] = 128, compute_dtype: Optional[torch.dtype] = torch.float16, device: Optional[str] = "cpu"):
        self.backend = backend
        self.nbits = nbits
        self.axis_key = axis_key
        self.axis_value = axis_value
        self.q_group_size = q_group_size
        self.residual_length = residual_length
        self.compute_dtype = compute_dtype
        self.device = device
    def validate(self):
        incorrect_arg_msg = ("Some of the keys in `cache_config` are defined incorrectly. `{key}` should be {correct_value}` but found {found_value}")
        if self.nbits not in [1, 2, 3, 4, 8]: raise ValueError(incorrect_arg_msg.format(key="nbits", correct_value="2 or 4 or 8", found_value=self.nbits))
        if self.q_group_size <= 0: raise ValueError(incorrect_arg_msg.format(key="q_group_size", correct_value="a positive integer", found_value=self.q_group_size))
        if self.residual_length < 0: raise ValueError(incorrect_arg_msg.format(key="residual_length", correct_value="a positive integer", found_value=self.residual_length))
        if self.axis_key not in [0, 1, -1]: raise ValueError(incorrect_arg_msg.format(key="axis_key", correct_value="`1` or `0`, `-1`", found_value=self.axis_key))
        if self.axis_value not in [0, 1, -1]: raise ValueError(incorrect_arg_msg.format(key="axis_value", correct_value="`1` or `0` or `-1`", found_value=self.axis_value))
@dataclass
class StaticCacheConfig(CacheConfig):
    cache_implementation = "static"
    def __init__(self, batch_size: int, max_cache_len: int, device="cpu"):
        self.batch_size = batch_size
        self.max_cache_len = max_cache_len
        self.device = device
    def validate(self):
        incorrect_arg_msg = ("Some of the keys in `cache_config` are defined incorrectly. `{key}` should be {correct_value}` but found {found_value}")
        if self.batch_size <= 0: raise ValueError(incorrect_arg_msg.format(key="batch_size", correct_value="> 0", found_value=self.batch_size))
        if self.max_cache_len <= 0: raise ValueError(incorrect_arg_msg.format(key="max_cache_len", correct_value="> 0", found_value=self.max_cache_len))
class DynamicCache(Cache):
    @deprecate_kwarg("num_hidden_layers", version="1.0.0")
    def __init__(self, num_hidden_layers: Optional[int] = None) -> None:
        super().__init__()
        self._seen_tokens = 0
        self.key_cache: List[torch.Tensor] = []
        self.value_cache: List[torch.Tensor] = []
    def __getitem__(self, layer_idx: int) -> List[Tuple[torch.Tensor]]:
        if layer_idx < len(self): return (self.key_cache[layer_idx], self.value_cache[layer_idx])
        else: raise KeyError(f"Cache only has {len(self)} layers, attempted to access layer with index {layer_idx}")
    def __iter__(self):
        for layer_idx in range(len(self)): yield (self.key_cache[layer_idx], self.value_cache[layer_idx])
    def __len__(self): return len(self.key_cache)
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        if layer_idx == 0: self._seen_tokens += key_states.shape[-2]
        if len(self.key_cache) <= layer_idx:
            for _ in range(len(self.key_cache), layer_idx):
                self.key_cache.append([])
                self.value_cache.append([])
            self.key_cache.append(key_states)
            self.value_cache.append(value_states)
        elif len(self.key_cache[layer_idx]) == 0:
            self.key_cache[layer_idx] = key_states
            self.value_cache[layer_idx] = value_states
        else:
            self.key_cache[layer_idx] = torch.cat([self.key_cache[layer_idx], key_states], dim=-2)
            self.value_cache[layer_idx] = torch.cat([self.value_cache[layer_idx], value_states], dim=-2)
        return self.key_cache[layer_idx], self.value_cache[layer_idx]
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        is_empty_layer = (len(self.key_cache) == 0 or len(self.key_cache) <= layer_idx or len(self.key_cache[layer_idx]) == 0)
        layer_seq_length = self.key_cache[layer_idx].shape[-2] if not is_empty_layer else 0
        return layer_seq_length
    def get_max_length(self) -> Optional[int]: return None
    def to_legacy_cache(self) -> Tuple[Tuple[torch.Tensor], Tuple[torch.Tensor]]:
        legacy_cache = ()
        for layer_idx in range(len(self)): legacy_cache += ((self.key_cache[layer_idx], self.value_cache[layer_idx]),)
        return legacy_cache
    @classmethod
    @deprecate_kwarg("num_hidden_layers", version="1.0.0")
    def from_legacy_cache(cls, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, num_hidden_layers: int = None) -> "DynamicCache":
        cache = cls()
        if past_key_values is not None:
            for layer_idx in range(len(past_key_values)):
                key_states, value_states = past_key_values[layer_idx]
                cache.update(key_states, value_states, layer_idx)
        return cache
    def crop(self, max_length: int):
        if max_length < 0: max_length = self.get_seq_length() - abs(max_length)
        if self.get_seq_length() <= max_length: return
        self._seen_tokens = max_length
        for idx in range(len(self.key_cache)):
            if self.key_cache[idx] != []:
                self.key_cache[idx] = self.key_cache[idx][..., :max_length, :]
                self.value_cache[idx] = self.value_cache[idx][..., :max_length, :]
    @deprecate_kwarg("num_hidden_layers", version="1.0.0")
    def batch_split(self, full_batch_size: int, split_size: int, num_hidden_layers: int = None) -> List["DynamicCache"]:
        out = []
        for i in range(0, full_batch_size, split_size):
            current_split = DynamicCache()
            current_split._seen_tokens = self._seen_tokens
            current_split.key_cache = [tensor[i : i + split_size] for tensor in self.key_cache]
            current_split.value_cache = [tensor[i : i + split_size] for tensor in self.value_cache]
            out.append(current_split)
        return out
    @classmethod
    @deprecate_kwarg("num_hidden_layers", version="1.0.0")
    def from_batch_splits(cls, splits: List["DynamicCache"], num_hidden_layers: int = None) -> "DynamicCache":
        cache = cls()
        for idx in range(len(splits[0])):
            key_cache = [current.key_cache[idx] for current in splits if current.key_cache[idx] != []]
            value_cache = [current.key_cache[idx] for current in splits if current.key_cache[idx] != []]
            if key_cache != []:
                layer_keys = torch.cat(key_cache, dim=0)
                layer_values = torch.cat(value_cache, dim=0)
                cache.update(layer_keys, layer_values, idx)
        return cache
    def batch_repeat_interleave(self, repeats: int):
        for layer_idx in range(len(self)):
            self.key_cache[layer_idx] = self.key_cache[layer_idx].repeat_interleave(repeats, dim=0)
            self.value_cache[layer_idx] = self.value_cache[layer_idx].repeat_interleave(repeats, dim=0)
    def batch_select_indices(self, indices: torch.Tensor):
        for layer_idx in range(len(self)):
            self.key_cache[layer_idx] = self.key_cache[layer_idx][indices, ...]
            self.value_cache[layer_idx] = self.value_cache[layer_idx][indices, ...]
class OffloadedCache(DynamicCache):
    def __init__(self) -> None:
        if not torch.cuda.is_available(): raise RuntimeError("OffloadedCache can only be used with a GPU")
        super().__init__()
        self.original_device = []
        self.prefetch_stream = torch.cuda.Stream()
        self.beam_idx = None
    def prefetch_layer(self, layer_idx: int):
        if layer_idx < len(self):
            with torch.cuda.stream(self.prefetch_stream):
                device = self.original_device[layer_idx]
                self.key_cache[layer_idx] = self.key_cache[layer_idx].to(device, non_blocking=True)
                self.value_cache[layer_idx] = self.value_cache[layer_idx].to(device, non_blocking=True)
    def evict_previous_layer(self, layer_idx: int):
        if len(self) > 2:
            prev_layer_idx = (layer_idx - 1) % len(self)
            self.key_cache[prev_layer_idx] = self.key_cache[prev_layer_idx].to("cpu", non_blocking=True)
            self.value_cache[prev_layer_idx] = self.value_cache[prev_layer_idx].to("cpu", non_blocking=True)
    def __getitem__(self, layer_idx: int) -> List[Tuple[torch.Tensor]]:
        if layer_idx < len(self):
            torch.cuda.current_stream().synchronize()
            self.evict_previous_layer(layer_idx)
            original_device = self.original_device[layer_idx]
            self.prefetch_stream.synchronize()
            key_tensor = self.key_cache[layer_idx]
            value_tensor = self.value_cache[layer_idx]
            if self.beam_idx is not None:
                self.beam_idx = self.beam_idx.to(original_device)
                key_tensor = key_tensor.index_select(0, self.beam_idx)
                value_tensor = value_tensor.index_select(0, self.beam_idx)
            self.prefetch_layer((layer_idx + 1) % len(self))
            return (key_tensor, value_tensor)
        else: raise KeyError(f"Cache only has {len(self)} layers, attempted to access layer with index {layer_idx}")
    def reorder_cache(self, beam_idx: torch.LongTensor):
        del self.beam_idx
        self.beam_idx = beam_idx.clone()
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        if layer_idx == 0: self._seen_tokens += key_states.shape[-2]
        if len(self.key_cache) < layer_idx: raise ValueError("OffloadedCache does not support model usage where layers are skipped. Use DynamicCache.")
        elif len(self.key_cache) == layer_idx:
            self.key_cache.append(key_states)
            self.value_cache.append(value_states)
            self.original_device.append(key_states.device)
            self.evict_previous_layer(layer_idx)
        else:
            key_tensor, value_tensor = self[layer_idx]
            self.key_cache[layer_idx] = torch.cat([key_tensor, key_states], dim=-2)
            self.value_cache[layer_idx] = torch.cat([value_tensor, value_states], dim=-2)
        return self.key_cache[layer_idx], self.value_cache[layer_idx]
    from_legacy_cache = None
    to_legacy_cache = None
class QuantizedCache(DynamicCache):
    def __init__(self, cache_config: QuantizedCacheConfig) -> None:
        super().__init__()
        self._quantized_key_cache: List[torch.Tensor] = []
        self._quantized_value_cache: List[torch.Tensor] = []
        self.nbits = cache_config.nbits
        self.residual_length = cache_config.residual_length
        self.q_group_size = cache_config.q_group_size
        self.axis_key = cache_config.axis_key
        self.axis_value = cache_config.axis_value
        self.compute_dtype = cache_config.compute_dtype
        self.device = cache_config.device
        super().__init__()
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        if layer_idx == 0: self._seen_tokens += key_states.shape[-2]
        if len(self.key_cache) < layer_idx: raise ValueError("QuantizedCache does not support model usage where layers are skipped. Use DynamicCache.")
        elif len(self.key_cache) == layer_idx:
            self._quantized_key_cache.append(self._quantize(key_states.contiguous(), axis=self.axis_key))
            self._quantized_value_cache.append(self._quantize(value_states.contiguous(), axis=self.axis_value))
            self.key_cache.append(torch.zeros(0, dtype=key_states.dtype, device=key_states.device))
            self.value_cache.append(torch.zeros(0, dtype=key_states.dtype, device=key_states.device))
            keys_to_return, values_to_return = key_states, value_states
        else:
            dequant_key = self._dequantize(self._quantized_key_cache[layer_idx])
            dequant_value = self._dequantize(self._quantized_value_cache[layer_idx])
            keys_to_return = [dequant_key, self.key_cache[layer_idx], key_states]
            values_to_return = [dequant_value, self.value_cache[layer_idx], value_states]
            keys_to_return = torch.cat(keys_to_return, dim=-2)
            values_to_return = torch.cat(values_to_return, dim=-2)
            if (self.key_cache[layer_idx].dim() == 4 and self.key_cache[layer_idx].shape[-2] + 1 >= self.residual_length):
                self._quantized_key_cache[layer_idx] = self._quantize(keys_to_return.contiguous(), axis=self.axis_key)
                self._quantized_value_cache[layer_idx] = self._quantize(values_to_return.contiguous(), axis=self.axis_value)
                self.key_cache[layer_idx] = torch.zeros(0, dtype=key_states.dtype, device=key_states.device)
                self.value_cache[layer_idx] = torch.zeros(0, dtype=key_states.dtype, device=key_states.device)
            else:
                self.key_cache[layer_idx] = torch.cat([self.key_cache[layer_idx], key_states], dim=-2)
                self.value_cache[layer_idx] = torch.cat([self.value_cache[layer_idx], value_states], dim=-2)
        return keys_to_return, values_to_return
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        if len(self.key_cache) <= layer_idx: return 0
        return self._seen_tokens if layer_idx == 0 else self._seen_tokens - 1
    def _quantize(self, tensor, axis): raise NotImplementedError("Make sure to implement `_quantize` in a subclass.")
    def _dequantize(self, q_tensor): raise NotImplementedError("Make sure to implement `_dequantize` in a subclass.")
class QuantoQuantizedCache(QuantizedCache):
    def __init__(self, cache_config: CacheConfig) -> None:
        super().__init__(cache_config)
        quanto_version = version.parse(importlib.metadata.version("quanto"))
        if quanto_version < version.parse("0.2.0"): raise ImportError(f"You need quanto package version to be greater or equal than 0.2.0 to use `QuantoQuantizedCache`. Detected version {quanto_version}. Please upgrade quanto with `pip install -U quanto`")
        if self.nbits not in [2, 4]: raise ValueError(f"`nbits` for `quanto` backend has to be one of [`2`, `4`] but got {self.nbits}")
        if self.axis_key not in [0, -1]: raise ValueError(f"`axis_key` for `quanto` backend has to be one of [`0`, `-1`] but got {self.axis_key}")
        if self.axis_value not in [0, -1]: raise ValueError(f"`axis_value` for `quanto` backend has to be one of [`0`, `-1`] but got {self.axis_value}")
        self.qtype = qint4 if self.nbits == 4 else qint2
        self.optimizer = MaxOptimizer()
    def _quantize(self, tensor, axis):
        scale, zeropoint = self.optimizer(tensor, self.qtype.bits, axis, self.q_group_size)
        qtensor = AffineQuantizer.apply(tensor, self.qtype, axis, self.q_group_size, scale, zeropoint)
        return qtensor
    def _dequantize(self, qtensor): return qtensor.dequantize()
class HQQQuantizedCache(QuantizedCache):
    def __init__(self, cache_config: CacheConfig) -> None:
        super().__init__(cache_config)
        if self.nbits not in [1, 2, 3, 4, 8]: raise ValueError(f"`nbits` for `HQQ` backend has to be one of [`1`, `2`, `3`, `4`, `8`] but got {self.nbits}")
        if self.axis_key not in [0, 1]: raise ValueError(f"`axis_key` for `HQQ` backend has to be one of [`0`, `1`] but got {self.axis_key}")
        if self.axis_value not in [0, 1]: raise ValueError(f"`axis_value` for `HQQ` backend has to be one of [`0`, `1`] but got {self.axis_value}")
        self.quantizer = HQQQuantizer
    def _quantize(self, tensor, axis):
        qtensor, meta = self.quantizer.quantize(tensor, axis=axis, device=self.device, compute_dtype=self.compute_dtype, nbits=self.nbits, group_size=self.q_group_size)
        meta["compute_dtype"] = self.compute_dtype
        self.quantizer.cuda(qtensor, meta=meta, device=self.device)
        return qtensor, meta
    def _dequantize(self, qtensor):
        quant_tensor, meta = qtensor
        tensor = self.quantizer.dequantize(quant_tensor, meta)
        return tensor
class SinkCache(Cache):
    def __init__(self, window_length: int, num_sink_tokens: int) -> None:
        super().__init__()
        self.key_cache: List[torch.Tensor] = []
        self.value_cache: List[torch.Tensor] = []
        self.window_length = window_length
        self.num_sink_tokens = num_sink_tokens
        self.cos_sin_rerotation_cache = {}
        self._cos_cache = None
        self._sin_cache = None
        self._seen_tokens = 0
    @staticmethod
    def _rotate_half(x):
        x1 = x[..., : x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)
    def _apply_key_rotary_pos_emb(self, key_states: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        rotated_key_states = (key_states * cos) + (self._rotate_half(key_states) * sin)
        return rotated_key_states
    def _get_rerotation_cos_sin(self, key_states: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        if key_states.shape[-2] not in self.cos_sin_rerotation_cache:
            cos = cos.to(torch.float32)
            sin = sin.to(torch.float32)
            original_cos = cos[self.num_sink_tokens + key_states.shape[-2] :]
            shifted_cos = cos[self.num_sink_tokens : -key_states.shape[-2]]
            original_sin = sin[self.num_sink_tokens + key_states.shape[-2] :]
            shifted_sin = sin[self.num_sink_tokens : -key_states.shape[-2]]
            rerotation_cos = original_cos * shifted_cos + original_sin * shifted_sin
            rerotation_sin = -original_sin * shifted_cos + original_cos * shifted_sin
            self.cos_sin_rerotation_cache[key_states.shape[-2]] = (rerotation_cos.to(key_states.dtype).unsqueeze(0), rerotation_sin.to(key_states.dtype).unsqueeze(0))
        return self.cos_sin_rerotation_cache[key_states.shape[-2]]
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        if len(self.key_cache) <= layer_idx: return 0
        return self.key_cache[layer_idx].shape[-2]
    def get_max_length(self) -> Optional[int]: return self.window_length
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        sin = cache_kwargs.get("sin")
        cos = cache_kwargs.get("cos")
        partial_rotation_size = cache_kwargs.get("partial_rotation_size")
        using_rope = cos is not None and sin is not None
        if layer_idx == 0: self._seen_tokens += key_states.shape[-2]
        if using_rope and layer_idx == 0:
            if cos.dim() == 2:
                self._cos_cache = cos
                self._sin_cache = sin
            else:
                if self._cos_cache is None:
                    self._cos_cache = cos[0, ...]
                    self._sin_cache = sin[0, ...]
                elif self._cos_cache.shape[0] < self.window_length:
                    self._cos_cache = torch.cat([self._cos_cache, cos[0, ...]], dim=0)
                    self._sin_cache = torch.cat([self._sin_cache, sin[0, ...]], dim=0)
        if len(self.key_cache) <= layer_idx:
            self.key_cache.append(key_states)
            self.value_cache.append(value_states)
        elif key_states.shape[-2] + self.get_seq_length(layer_idx) < self.window_length:
            self.key_cache[layer_idx] = torch.cat([self.key_cache[layer_idx], key_states], dim=-2)
            self.value_cache[layer_idx] = torch.cat([self.value_cache[layer_idx], value_states], dim=-2)
        else:
            keys_to_keep = self.key_cache[layer_idx][:, :, -self.window_length + self.num_sink_tokens + key_states.shape[-2] :]
            if using_rope:
                rerotation_cos, rerotation_sin = self._get_rerotation_cos_sin(key_states, self._cos_cache[: self.window_length], self._sin_cache[: self.window_length])
                if partial_rotation_size is not None: keys_to_keep, keys_pass = (keys_to_keep[..., :partial_rotation_size], keys_to_keep[..., partial_rotation_size:])
                keys_to_keep = self._apply_key_rotary_pos_emb(keys_to_keep, rerotation_cos, rerotation_sin)
                if partial_rotation_size is not None: keys_to_keep = torch.cat((keys_to_keep, keys_pass), dim=-1)
            sink_keys = self.key_cache[layer_idx][:, :, : self.num_sink_tokens]
            self.key_cache[layer_idx] = torch.cat([sink_keys, keys_to_keep, key_states], dim=-2)
            sink_values = self.value_cache[layer_idx][:, :, : self.num_sink_tokens]
            values_to_keep = self.value_cache[layer_idx][:, :, -self.window_length + self.num_sink_tokens + value_states.shape[-2] :]
            self.value_cache[layer_idx] = torch.cat([sink_values, values_to_keep, value_states], dim=-2)
        return self.key_cache[layer_idx], self.value_cache[layer_idx]
class StaticCache(Cache):
    def __init__(self, config: PretrainedConfig, batch_size: int = None, max_cache_len: int = None, device: torch.device = None, dtype: torch.dtype = torch.float32,
    max_batch_size: Optional[int] = None, layer_device_map: Optional[Dict[int, Union[str, torch.device, int]]] = None) -> None:
        super().__init__()
        if max_batch_size is not None: logger.warning_once(f"The 'max_batch_size' argument of {self.__class__.__name__} is deprecated and will be removed in v4.46. Use the more precisely named 'batch_size' argument instead.")
        self.batch_size = batch_size or max_batch_size
        self.max_cache_len = config.max_position_embeddings if max_cache_len is None else max_cache_len
        self.head_dim = (config.head_dim if hasattr(config, "head_dim") else config.hidden_size // config.num_attention_heads)
        self.dtype = dtype
        self.num_key_value_heads = (config.num_attention_heads if getattr(config, "num_key_value_heads", None) is None else config.num_key_value_heads)
        self.key_cache: List[torch.Tensor] = []
        self.value_cache: List[torch.Tensor] = []
        cache_shape = (self.batch_size, self.num_key_value_heads, self.max_cache_len, self.head_dim)
        for idx in range(config.num_hidden_layers):
            if layer_device_map is not None: layer_device = layer_device_map[idx]
            else: layer_device = device
            new_layer_key_cache = torch.zeros(cache_shape, dtype=self.dtype, device=layer_device)
            new_layer_value_cache = torch.zeros(cache_shape, dtype=self.dtype, device=layer_device)
            if not is_torchdynamo_compiling():
                self.register_buffer(f"key_cache_{idx}", torch.zeros(cache_shape, dtype=dtype, device=layer_device))
                self.register_buffer(f"value_cache_{idx}", torch.zeros(cache_shape, dtype=dtype, device=layer_device))
                new_layer_key_cache = getattr(self, f"key_cache_{idx}")
                new_layer_value_cache = getattr(self, f"value_cache_{idx}")
                torch._dynamo.mark_static_address(new_layer_key_cache)
                torch._dynamo.mark_static_address(new_layer_value_cache)
            self.key_cache.append(new_layer_key_cache)
            self.value_cache.append(new_layer_value_cache)
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        cache_position = cache_kwargs.get("cache_position")
        k_out = self.key_cache[layer_idx]
        v_out = self.value_cache[layer_idx]
        if cache_position is None:
            k_out.copy_(key_states)
            v_out.copy_(value_states)
        else:
            try:
                k_out.index_copy_(2, cache_position, key_states)
                v_out.index_copy_(2, cache_position, value_states)
            except NotImplementedError:
                k_out[:, :, cache_position] = key_states
                v_out[:, :, cache_position] = value_states
        return k_out, v_out
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int: return (self.key_cache[layer_idx][0, 0].any(dim=-1)).sum()
    def get_max_length(self) -> Optional[int]: return self.max_cache_len
    def reset(self):
        for layer_idx in range(len(self.key_cache)):
            self.key_cache[layer_idx].zero_()
            self.value_cache[layer_idx].zero_()
class SlidingWindowCache(StaticCache):
    def __init__(self, config: PretrainedConfig, batch_size: int = None, max_cache_len: int = None, device: torch.device = None, dtype: torch.dtype = torch.float32, max_batch_size: Optional[int] = None,
    layer_device_map: Optional[Dict[int, Union[str, torch.device, int]]] = None) -> None:
        super().__init__()
        if not hasattr(config, "sliding_window") or config.sliding_window is None: raise ValueError("Setting `cache_implementation` to 'sliding_window' requires the model config supporting sliding window attention, please check if there is a `sliding_window` field in the model config and it's not set to None.")
        max_cache_len = min(config.sliding_window, max_cache_len)
        super().__init__(config=config, batch_size=batch_size, max_cache_len=max_cache_len, device=device, dtype=dtype, max_batch_size=max_batch_size, layer_device_map=layer_device_map)
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor]:
        cache_position = cache_kwargs.get("cache_position")
        k_out = self.key_cache[layer_idx]
        v_out = self.value_cache[layer_idx]
        if cache_position.shape[0] > self.max_cache_len:
            k_out = key_states[:, :, -self.max_cache_len :, :]
            v_out = value_states[:, :, -self.max_cache_len :, :]
            self.key_cache[layer_idx] += k_out
            self.value_cache[layer_idx] += v_out
            return key_states, value_states
        slicing = torch.ones(self.max_cache_len, dtype=torch.long, device=value_states.device).cumsum(0)
        cache_position = cache_position.clamp(0, self.max_cache_len - 1)
        to_shift = cache_position >= self.max_cache_len - 1
        indices = (slicing + to_shift[-1].int() - 1) % self.max_cache_len
        k_out = k_out[:, :, indices]
        v_out = v_out[:, :, indices]
        try:
            k_out.index_copy_(2, cache_position, key_states)
            v_out.index_copy_(2, cache_position, value_states)
        except NotImplementedError:
            k_out[:, :, cache_position] = key_states
            v_out[:, :, cache_position] = value_states
        self.key_cache[layer_idx].zero_()
        self.value_cache[layer_idx].zero_()
        self.key_cache[layer_idx] += k_out
        self.value_cache[layer_idx] += v_out
        return k_out, v_out
    def get_max_length(self) -> Optional[int]:
        return None
    def reset(self):
        for layer_idx in range(len(self.key_cache)):
            self.key_cache[layer_idx].zero_()
            self.value_cache[layer_idx].zero_()
class EncoderDecoderCache(Cache):
    def __init__(self, self_attention_cache: Cache, cross_attention_cache: Cache):
        super().__init__()
        self.self_attention_cache = self_attention_cache
        self.cross_attention_cache = cross_attention_cache
        self.is_updated = {}
        for layer_idx in range(len(cross_attention_cache.key_cache)):
            self.is_updated[layer_idx] = bool(cross_attention_cache.get_seq_length(layer_idx) > 0)
    def __getitem__(self, layer_idx: int) -> List[Tuple[torch.Tensor]]:
        if layer_idx < len(self): return (self.self_attention_cache.key_cache[layer_idx], self.self_attention_cache.value_cache[layer_idx], self.cross_attention_cache.key_cache[layer_idx], self.cross_attention_cache.value_cache[layer_idx])
        else: raise KeyError(f"Cache only has {len(self)} layers, attempted to access layer with index {layer_idx}")
    def __len__(self): return len(self.self_attention_cache)
    def to_legacy_cache(self) -> Tuple[Tuple[torch.Tensor], Tuple[torch.Tensor]]:
        legacy_cache = ()
        if len(self.cross_attention_cache) > 0:
            for self_attn, cross_attn in zip(self.self_attention_cache.to_legacy_cache(), self.cross_attention_cache.to_legacy_cache()): legacy_cache += (self_attn + cross_attn,)
        else: legacy_cache = self.self_attention_cache.to_legacy_cache()
        return legacy_cache
    @classmethod
    def from_legacy_cache(cls, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None) -> "EncoderDecoderCache":
        cache = cls(self_attention_cache=DynamicCache(), cross_attention_cache=DynamicCache())
        if past_key_values is not None:
            for layer_idx in range(len(past_key_values)):
                key_states, value_states = past_key_values[layer_idx][:2]
                cache.self_attention_cache.update(key_states, value_states, layer_idx)
                if len(past_key_values[layer_idx]) > 2:
                    key_states, value_states = past_key_values[layer_idx][2:]
                    cache.cross_attention_cache.update(key_states, value_states, layer_idx)
                    cache.is_updated[layer_idx] = True
        return cache
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        if self.self_attention_cache.key_cache == []: return 0
        if len(self.self_attention_cache.key_cache) > 1 and self.self_attention_cache.key_cache[layer_idx] == []: return 0
        return (self.self_attention_cache.key_cache[layer_idx][0, 0].any(dim=-1)).sum()
    def reset(self):
        if hasattr(self.self_attention_cache, "reset"): self.self_attention_cache.reset()
        if hasattr(self.cross_attention_cache, "reset"): self.cross_attention_cache.reset()
        elif not hasattr(self.self_attention_cache, "reset") and not hasattr(self.cross_attention_cache, "reset"): raise ValueError(f"Neither self nor cross-attention cache have valid `.reset()` methods. `.reset()` should only be called on compatible cache classes, such as `StaticCache` or `SlidingWindowCache`. Got {self.self_attention_cache.__str__()} for the self attention cache and {self.cross_attention_cache.__str__()} for the cross attention cache.")
        for layer_idx in self.is_updated: self.is_updated[layer_idx] = False
    def reorder_cache(self, beam_idx: torch.LongTensor):
        self.self_attention_cache.reorder_cache(beam_idx)
        self.cross_attention_cache.reorder_cache(beam_idx)
    def check_dynamic_cache(self, method: str):
        if not (isinstance(self.self_attention_cache, DynamicCache) and isinstance(self.cross_attention_cache, DynamicCache)): raise ValueError(f"`{method}` is only defined for dynamic cache, got {self.self_attention_cache.__str__()} for the self attention cache and {self.cross_attention_cache.__str__()} for the cross attention cache.")
    def crop(self, maximum_length: int):
        self.check_dynamic_cache(self.crop.__name__)
        self.self_attention_cache.crop(maximum_length)
    def batch_split(self, full_batch_size: int, split_size: int) -> "List[EncoderDecoderCache]":
        self.check_dynamic_cache(self.batch_split.__name__)
        self_attention_cache = self.self_attention_cache.batch_split(full_batch_size, split_size)
        cross_attention_cache = self.cross_attention_cache.batch_split(full_batch_size, split_size)
        out = []
        for self_attn, cross_attn in zip(self_attention_cache, cross_attention_cache):
            out.append(EncoderDecoderCache(self_attn, cross_attn))
        return out
    @classmethod
    def from_batch_splits(cls, splits: List["EncoderDecoderCache"]) -> "EncoderDecoderCache":
        self_attention_cache = DynamicCache()
        cross_attention_cache = DynamicCache()
        for idx in range(len(splits[0])):
            layer_keys = torch.cat([current.self_attention_cache.key_cache[idx] for current in splits], dim=0)
            layer_values = torch.cat([current.self_attention_cache.value_cache[idx] for current in splits], dim=0)
            self_attention_cache.update(layer_keys, layer_values, idx)
            layer_keys = torch.cat([current.cross_attention_cache.key_cache[idx] for current in splits], dim=0)
            layer_values = torch.cat([current.cross_attention_cache.value_cache[idx] for current in splits], dim=0)
            cross_attention_cache.update(layer_keys, layer_values, idx)
        return cls(self_attention_cache, cross_attention_cache)
    def batch_repeat_interleave(self, repeats: int):
        self.check_dynamic_cache(self.batch_repeat_interleave.__name__)
        self.self_attention_cache.batch_repeat_interleave(repeats)
        self.cross_attention_cache.batch_repeat_interleave(repeats)
    def batch_select_indices(self, indices: torch.Tensor):
        self.check_dynamic_cache(self.batch_select_indices.__name__)
        self.self_attention_cache.batch_select_indices(indices)
        self.cross_attention_cache.batch_select_indices(indices)
class HybridCache(Cache):
    def __init__(self, config: PretrainedConfig, batch_size: int = None, max_cache_len: int = None, device: Union[torch.device, str] = "cpu", dtype: torch.dtype = torch.float32,
    max_batch_size: Optional[int] = None, layer_device_map: Optional[Dict[int, Union[str, torch.device, int]]] = None) -> None:
        super().__init__()
        if max_batch_size is not None: logger.warning_once(f"The 'max_batch_size' argument of {self.__class__.__name__} is deprecated and will be removed in v4.46. Use the more precisely named 'batch_size' argument instead.")
        if not hasattr(config, "sliding_window") or config.sliding_window is None: raise ValueError("Setting `cache_implementation` to 'sliding_window' requires the model config supporting sliding window attention, please check if there is a `sliding_window` field in the model config and it's not set to None.")
        self.max_cache_len = max_cache_len
        self.batch_size = batch_size or max_batch_size
        self.head_dim = (config.head_dim if hasattr(config, "head_dim") else config.hidden_size // config.num_attention_heads)
        self.dtype = dtype
        self.num_key_value_heads = (config.num_attention_heads if config.num_key_value_heads is None else config.num_key_value_heads)
        self.is_sliding = torch.tensor([not bool(i % 2) for i in range(config.num_hidden_layers)], dtype=torch.bool, device=device)
        self.key_cache: List[torch.Tensor] = []
        self.value_cache: List[torch.Tensor] = []
        global_cache_shape = (self.batch_size, self.num_key_value_heads, max_cache_len, self.head_dim)
        sliding_cache_shape = (self.batch_size, self.num_key_value_heads, min(config.sliding_window, max_cache_len), self.head_dim)
        for i in range(config.num_hidden_layers):
            if layer_device_map is not None: layer_device = layer_device_map[i]
            else: layer_device = device
            cache_shape = global_cache_shape if not self.is_sliding[i] else sliding_cache_shape
            new_layer_key_cache = torch.zeros(cache_shape, dtype=self.dtype, device=layer_device)
            new_layer_value_cache = torch.zeros(cache_shape, dtype=self.dtype, device=layer_device)
            torch._dynamo.mark_static_address(new_layer_key_cache)
            torch._dynamo.mark_static_address(new_layer_value_cache)
            self.key_cache.append(new_layer_key_cache)
            self.value_cache.append(new_layer_value_cache)
    def _sliding_update(self, cache_position, layer_idx, key_states, value_states, k_out, v_out, max_cache_len):
        if cache_position.shape[0] > max_cache_len:
            k_out = key_states[:, :, -max_cache_len:, :]
            v_out = value_states[:, :, -max_cache_len:, :]
            self.key_cache[layer_idx] += k_out
            self.value_cache[layer_idx] += v_out
            return key_states, value_states
        slicing = torch.ones(max_cache_len, dtype=torch.long, device=value_states.device).cumsum(0)
        cache_position = cache_position.clamp(0, max_cache_len - 1)
        to_shift = cache_position >= max_cache_len - 1
        indices = (slicing + to_shift[-1].int() - 1) % max_cache_len
        k_out = k_out[:, :, indices]
        v_out = v_out[:, :, indices]
        k_out[:, :, cache_position] = key_states
        v_out[:, :, cache_position] = value_states
        self.key_cache[layer_idx].zero_()
        self.value_cache[layer_idx].zero_()
        self.key_cache[layer_idx] += k_out
        self.value_cache[layer_idx] += v_out
        return k_out, v_out
    def _static_update(self, cache_position, layer_idx, key_states, value_states, k_out, v_out, max_cache_len):
        k_out[:, :, cache_position] = key_states
        v_out[:, :, cache_position] = value_states
        self.key_cache[layer_idx] = k_out
        self.value_cache[layer_idx] = v_out
        return k_out, v_out
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor]:
        cache_position = cache_kwargs.get("cache_position")
        sliding_window = cache_kwargs.get("sliding_window")
        k_out = self.key_cache[layer_idx]
        v_out = self.value_cache[layer_idx]
        if sliding_window: update_fn = self._sliding_update
        else: update_fn = self._static_update
        return update_fn(cache_position, layer_idx, key_states, value_states, k_out, v_out, k_out.shape[2])
    def get_max_length(self) -> Optional[int]:
        return self.max_cache_len
    def get_seq_length(self, layer_idx: Optional[int] = 0):
        if layer_idx != 0: raise ValueError("`get_seq_length` on `HybridCache` may get inconsistent results depending on the layer index. Using the `layer_idx` argument is not supported.")
        return (self.key_cache[layer_idx][0, 0].any(dim=-1)).sum()
    def reset(self):
        for layer_idx in range(len(self.key_cache)):
            self.key_cache[layer_idx].zero_()
            self.value_cache[layer_idx].zero_()
class MambaCache:
    def __init__(self, config: PretrainedConfig, batch_size: int = None, dtype: torch.dtype = torch.float16, device: Optional[Union[torch.device, str]] = None, max_batch_size: Optional[int] = None):
        if max_batch_size is not None: logger.warning_once(f"The 'max_batch_size' argument of {self.__class__.__name__} is deprecated and will be removed in v4.46. Use the more precisely named 'batch_size' argument instead.")
        self.dtype = dtype
        self.batch_size = batch_size or max_batch_size
        self.intermediate_size = config.intermediate_size
        self.ssm_state_size = config.state_size
        self.conv_kernel_size = config.conv_kernel
        self.conv_states: torch.Tensor = torch.zeros(config.num_hidden_layers, self.batch_size, self.intermediate_size, self.conv_kernel_size, device=device, dtype=dtype)
        self.ssm_states: torch.Tensor = torch.zeros(config.num_hidden_layers, self.batch_size, self.intermediate_size, self.ssm_state_size, device=device, dtype=dtype)
        torch._dynamo.mark_static_address(self.conv_states)
        torch._dynamo.mark_static_address(self.ssm_states)
    def update_conv_state(self, layer_idx: int, new_conv_state: torch.Tensor, cache_position: torch.LongTensor) -> torch.Tensor:
        conv_state = self.conv_states[layer_idx]
        cache_position = cache_position.clamp(0, self.conv_kernel_size - 1)
        conv_state = conv_state.roll(shifts=-1, dims=-1)
        conv_state[:, :, cache_position] = new_conv_state.to(conv_state.device)
        self.conv_states[layer_idx].zero_()
        self.conv_states[layer_idx] += conv_state
        return self.conv_states[layer_idx]
    def update_ssm_state(self, layer_idx: int, new_ssm_state: torch.Tensor):
        self.ssm_states[layer_idx] = new_ssm_state.to(self.ssm_states.device)
        return self.ssm_states[layer_idx]
    def reset(self):
        self.conv_states.zero_()
        self.ssm_states.zero_()
class OffloadedStaticCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_batch_size: int, max_cache_len: Optional[int], device: Union[str, torch.device], dtype: Optional[torch.dtype] = None, offload_device: Union[str, torch.device] = torch.device("cpu")) -> None:
        self.max_batch_size = max_batch_size
        self.max_cache_len = config.max_position_embeddings if max_cache_len is None else max_cache_len
        self.device = torch.device(device)
        self.offload_device = torch.device(offload_device)
        self.dtype = dtype if dtype is not None else torch.float32
        head_dim = config.head_dim if hasattr(config, "head_dim") else config.hidden_size // config.num_attention_heads
        num_key_value_heads = (config.num_attention_heads if config.num_key_value_heads is None else config.num_key_value_heads)
        cache_shape = (max_batch_size, num_key_value_heads, self.max_cache_len, head_dim)
        self.key_cache: List[torch.Tensor] = []
        self.value_cache: List[torch.Tensor] = []
        for i in range(config.num_hidden_layers):
            device = self.device if i == 0 else self.offload_device
            key_cache, value_cache = self._create_key_value_cache_tensors(cache_shape, device)
            self.key_cache.append(key_cache)
            self.value_cache.append(value_cache)
        self._device_key_cache: List[torch.Tensor] = []
        self._device_value_cache: List[torch.Tensor] = []
        for i in range(2):
            key_cache, value_cache = self._create_key_value_cache_tensors(cache_shape, self.device)
            self._device_key_cache.append(key_cache)
            self._device_value_cache.append(value_cache)
        self._seen_tokens = 0
        self._prefetch_stream = torch.cuda.Stream() if self.device.type == "cuda" else None
    def update(self, key_states: torch.Tensor, value_states: torch.Tensor, layer_idx: int, cache_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        if layer_idx == 0:
            self._seen_tokens += key_states.shape[-2]
            k_out = self.key_cache[0]
            v_out = self.value_cache[0]
        else:
            if self._prefetch_stream is not None: torch.cuda.default_stream(self.device).wait_stream(self._prefetch_stream)
            k_out = self._device_key_cache[layer_idx & 1]
            v_out = self._device_value_cache[layer_idx & 1]
        self._prefetch_layer(layer_idx + 1)
        cache_position = cache_kwargs.get("cache_position") if cache_kwargs is not None else None
        if cache_position is None:
            k_out.copy_(key_states)
            v_out.copy_(value_states)
            if layer_idx == 0:
                self.key_cache[layer_idx].copy_(key_states.to(self.offload_device))
                self.value_cache[layer_idx].copy_(value_states.to(self.offload_device))
        else:
            try:
                k_out.index_copy_(2, cache_position, key_states)
                v_out.index_copy_(2, cache_position, value_states)
            except NotImplementedError:
                k_out[:, :, cache_position] = key_states
                v_out[:, :, cache_position] = value_states
            if layer_idx != 0:
                cache_position = cache_position.to(self.offload_device)
                key_states = key_states.to(self.offload_device)
                value_states = value_states.to(self.offload_device)
                try:
                    self.key_cache[layer_idx].index_copy_(2, cache_position, key_states)
                    self.value_cache[layer_idx].index_copy_(2, cache_position, value_states)
                except NotImplementedError:
                    self.key_cache[layer_idx][:, :, cache_position] = key_states
                    self.value_cache[layer_idx][:, :, cache_position] = value_states
        return k_out, v_out
    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int: return self._seen_tokens
    def get_max_length(self) -> Optional[int]: return self.max_cache_len
    def reset(self) -> None:
        self._seen_tokens = 0
        for layer_idx in range(len(self.key_cache)):
            self.key_cache[layer_idx].zero_()
            self.value_cache[layer_idx].zero_()
    @property
    def seen_tokens(self) -> int: return self._seen_tokens
    def _create_key_value_cache_tensors(self, shape: Tuple[int, ...], device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        is_cpu_device = device == torch.device("cpu")
        key_cache = torch.zeros(shape, dtype=self.dtype, device=device, pin_memory=is_cpu_device)
        value_cache = torch.zeros(shape, dtype=self.dtype, device=device, pin_memory=is_cpu_device)
        torch._dynamo.mark_static_address(key_cache)
        torch._dynamo.mark_static_address(value_cache)
        return key_cache, value_cache
    def _prefetch_layer(self, layer_idx: int) -> None:
        if layer_idx >= len(self.key_cache): return
        if self._prefetch_stream is not None:
            with torch.cuda.stream(self._prefetch_stream): self._prefetch_layer_in_context(layer_idx)
        else: self._prefetch_layer_in_context(layer_idx)
    def _prefetch_layer_in_context(self, layer_idx: int) -> None:
        self._device_key_cache[layer_idx & 1].copy_(self.key_cache[layer_idx], non_blocking=True)
        self._device_value_cache[layer_idx & 1].copy_(self.value_cache[layer_idx], non_blocking=True)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
