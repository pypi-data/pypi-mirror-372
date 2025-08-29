"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils.import_utils import is_torchdynamo_compiling
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
import torch
@dataclass
class AttentionMaskConverter:
    is_causal: bool
    sliding_window: int
    def __init__(self, is_causal: bool, sliding_window: Optional[int] = None):
        self.is_causal = is_causal
        self.sliding_window = sliding_window
        if self.sliding_window is not None and self.sliding_window <= 0: raise ValueError(f"Make sure that when passing `sliding_window` that its value is a strictly positive integer, not `{self.sliding_window}`")
    def to_causal_4d(self, batch_size: int, query_length: int, key_value_length: int, dtype: torch.dtype, device: Union[torch.device, "str"] = "cpu") -> Optional[torch.Tensor]:
        if not self.is_causal: raise ValueError(f"Please use `to_causal_4d` only if {self.__class__} has `is_causal` set to True.")
        input_shape = (batch_size, query_length)
        past_key_values_length = key_value_length - query_length
        causal_4d_mask = None
        if input_shape[-1] > 1 or self.sliding_window is not None: causal_4d_mask = self._make_causal_mask(input_shape, dtype, device=device, past_key_values_length=past_key_values_length, sliding_window=self.sliding_window)
        return causal_4d_mask
    def to_4d(self, attention_mask_2d: torch.Tensor, query_length: int, dtype: torch.dtype, key_value_length: Optional[int] = None) -> torch.Tensor:
        input_shape = (attention_mask_2d.shape[0], query_length)
        causal_4d_mask = None
        if (input_shape[-1] > 1 or self.sliding_window is not None) and self.is_causal:
            if key_value_length is None: raise ValueError("This attention mask converter is causal. Make sure to pass `key_value_length` to correctly create a causal mask.")
            past_key_values_length = key_value_length - query_length
            causal_4d_mask = self._make_causal_mask(input_shape, dtype, device=attention_mask_2d.device, past_key_values_length=past_key_values_length, sliding_window=self.sliding_window)
        elif self.sliding_window is not None: raise NotImplementedError("Sliding window is currently only implemented for causal masking")
        expanded_attn_mask = self._expand_mask(attention_mask_2d, dtype, tgt_len=input_shape[-1]).to(attention_mask_2d.device)
        if causal_4d_mask is not None: expanded_attn_mask = causal_4d_mask.masked_fill(expanded_attn_mask.bool(), torch.finfo(dtype).min)
        expanded_4d_mask = expanded_attn_mask
        return expanded_4d_mask
    @staticmethod
    def _make_causal_mask(input_ids_shape: torch.Size, dtype: torch.dtype, device: torch.device, past_key_values_length: int = 0, sliding_window: Optional[int] = None):
        bsz, tgt_len = input_ids_shape
        mask = torch.full((tgt_len, tgt_len), torch.finfo(dtype).min, device=device)
        mask_cond = torch.arange(mask.size(-1), device=device)
        mask.masked_fill_(mask_cond < (mask_cond + 1).view(mask.size(-1), 1), 0)
        mask = mask.to(dtype)
        if past_key_values_length > 0: mask = torch.cat([torch.zeros(tgt_len, past_key_values_length, dtype=dtype, device=device), mask], dim=-1)
        if sliding_window is not None:
            diagonal = past_key_values_length - sliding_window - 1
            context_mask = torch.tril(torch.ones_like(mask, dtype=torch.bool), diagonal=diagonal)
            mask.masked_fill_(context_mask, torch.finfo(dtype).min)
        return mask[None, None, :, :].expand(bsz, 1, tgt_len, tgt_len + past_key_values_length)
    @staticmethod
    def _expand_mask(mask: torch.Tensor, dtype: torch.dtype, tgt_len: Optional[int] = None):
        bsz, src_len = mask.size()
        tgt_len = tgt_len if tgt_len is not None else src_len
        expanded_mask = mask[:, None, None, :].expand(bsz, 1, tgt_len, src_len).to(dtype)
        inverted_mask = 1.0 - expanded_mask
        return inverted_mask.masked_fill(inverted_mask.to(torch.bool), torch.finfo(dtype).min)
    @staticmethod
    def _unmask_unattended(expanded_mask: torch.FloatTensor, min_dtype: float):
        if expanded_mask.dtype == torch.bool: raise ValueError("AttentionMaskConverter._unmask_unattended expects a float `expanded_mask`, got a BoolTensor.")
        return expanded_mask.mul(~torch.all(expanded_mask == min_dtype, dim=-1, keepdim=True))
    @staticmethod
    def _ignore_causal_mask_sdpa(attention_mask: Optional[torch.Tensor], inputs_embeds: torch.Tensor, past_key_values_length: int, sliding_window: Optional[int] = None, is_training: bool = False) -> bool:
        _, query_length = inputs_embeds.shape[0], inputs_embeds.shape[1]
        key_value_length = query_length + past_key_values_length
        is_tracing = torch.jit.is_tracing() or isinstance(inputs_embeds, torch.fx.Proxy) or is_torchdynamo_compiling()
        ignore_causal_mask = False
        if attention_mask is None:
            if ((is_training or not is_tracing) and (query_length == 1 or key_value_length == query_length) and (sliding_window is None or key_value_length < sliding_window)): ignore_causal_mask = True
        elif sliding_window is None or key_value_length < sliding_window:
            if len(attention_mask.shape) == 4: return False
            elif (is_training or not is_tracing) and torch.all(attention_mask == 1):
                if query_length == 1 or key_value_length == query_length: ignore_causal_mask = True
        return ignore_causal_mask
def _prepare_4d_causal_attention_mask(attention_mask: Optional[torch.Tensor], input_shape: Union[torch.Size, Tuple, List], inputs_embeds: torch.Tensor, past_key_values_length: int, sliding_window: Optional[int] = None):
    attn_mask_converter = AttentionMaskConverter(is_causal=True, sliding_window=sliding_window)
    key_value_length = input_shape[-1] + past_key_values_length
    if attention_mask is not None and len(attention_mask.shape) == 2: attention_mask = attn_mask_converter.to_4d(attention_mask, input_shape[-1], key_value_length=key_value_length, dtype=inputs_embeds.dtype)
    elif attention_mask is not None and len(attention_mask.shape) == 4:
        expected_shape = (input_shape[0], 1, input_shape[1], key_value_length)
        if tuple(attention_mask.shape) != expected_shape: raise ValueError(f"Incorrect 4D attention_mask shape: {tuple(attention_mask.shape)}; expected: {expected_shape}.")
        else:
            inverted_mask = 1.0 - attention_mask
            attention_mask = inverted_mask.masked_fill(inverted_mask.to(torch.bool), torch.finfo(inputs_embeds.dtype).min)
    else: attention_mask = attn_mask_converter.to_causal_4d(input_shape[0], input_shape[-1], key_value_length, dtype=inputs_embeds.dtype, device=inputs_embeds.device)
    return attention_mask
def _prepare_4d_causal_attention_mask_for_sdpa(attention_mask: Optional[torch.Tensor], input_shape: Union[torch.Size, Tuple, List], inputs_embeds: torch.Tensor, past_key_values_length: int, sliding_window: Optional[int] = None):
    attn_mask_converter = AttentionMaskConverter(is_causal=True, sliding_window=sliding_window)
    key_value_length = input_shape[-1] + past_key_values_length
    is_tracing = torch.jit.is_tracing() or isinstance(inputs_embeds, torch.fx.Proxy) or is_torchdynamo_compiling()
    ignore_causal_mask = AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask=attention_mask, inputs_embeds=inputs_embeds, past_key_values_length=past_key_values_length, sliding_window=sliding_window)
    if ignore_causal_mask: expanded_4d_mask = None
    elif attention_mask is None: expanded_4d_mask = attn_mask_converter.to_causal_4d(input_shape[0], input_shape[-1], key_value_length, dtype=inputs_embeds.dtype, device=inputs_embeds.device)
    else:
        if attention_mask.dim() == 4: expanded_4d_mask = attention_mask
        else: expanded_4d_mask = attn_mask_converter.to_4d(attention_mask, input_shape[-1], dtype=inputs_embeds.dtype, key_value_length=key_value_length)
        if not is_tracing and expanded_4d_mask.device.type == "cuda": expanded_4d_mask = AttentionMaskConverter._unmask_unattended(expanded_4d_mask, min_dtype=torch.finfo(inputs_embeds.dtype).min)
    return expanded_4d_mask
def _prepare_4d_attention_mask(mask: torch.Tensor, dtype: torch.dtype, tgt_len: Optional[int] = None): return AttentionMaskConverter._expand_mask(mask=mask, dtype=dtype, tgt_len=tgt_len)
def _prepare_4d_attention_mask_for_sdpa(mask: torch.Tensor, dtype: torch.dtype, tgt_len: Optional[int] = None):
    _, key_value_length = mask.shape
    tgt_len = tgt_len if tgt_len is not None else key_value_length
    is_tracing = torch.jit.is_tracing() or isinstance(mask, torch.fx.Proxy) or is_torchdynamo_compiling()
    if not is_tracing and torch.all(mask == 1): return None
    else: return AttentionMaskConverter._expand_mask(mask=mask, dtype=dtype, tgt_len=tgt_len)
def _create_4d_causal_attention_mask(input_shape: Union[torch.Size, Tuple, List], dtype: torch.dtype, device: torch.device, past_key_values_length: int = 0, sliding_window: Optional[int] = None) -> Optional[torch.Tensor]:
    attn_mask_converter = AttentionMaskConverter(is_causal=True, sliding_window=sliding_window)
    key_value_length = past_key_values_length + input_shape[-1]
    attention_mask = attn_mask_converter.to_causal_4d(input_shape[0], input_shape[-1], key_value_length, dtype=dtype, device=device)
    return attention_mask
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
