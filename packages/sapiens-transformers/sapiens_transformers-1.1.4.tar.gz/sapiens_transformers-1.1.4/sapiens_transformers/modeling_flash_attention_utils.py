"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import is_flash_attn_2_available, is_flash_attn_greater_or_equal
from typing import Optional, Tuple, TypedDict
import torch.nn.functional as F
import inspect
import torch
import os
if is_flash_attn_2_available():
    from flash_attn.bert_padding import index_first_axis, pad_input, unpad_input
    from flash_attn import flash_attn_func, flash_attn_varlen_func
    _flash_supports_window_size = "window_size" in list(inspect.signature(flash_attn_func).parameters)
def _get_unpad_data(attention_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, int]:
    seqlens_in_batch = attention_mask.sum(dim=-1, dtype=torch.int32)
    indices = torch.nonzero(attention_mask.flatten(), as_tuple=False).flatten()
    max_seqlen_in_batch = seqlens_in_batch.max().item()
    cu_seqlens = F.pad(torch.cumsum(seqlens_in_batch, dim=0, dtype=torch.int32), (1, 0))
    return (indices, cu_seqlens, max_seqlen_in_batch)
def _upad_input(query_layer: torch.Tensor, key_layer: torch.Tensor, value_layer: torch.Tensor, attention_mask: torch.Tensor, query_length: int):
    indices_k, cu_seqlens_k, max_seqlen_in_batch_k = _get_unpad_data(attention_mask)
    batch_size, kv_seq_len, num_key_value_heads, head_dim = key_layer.shape
    key_layer = index_first_axis(key_layer.reshape(batch_size * kv_seq_len, num_key_value_heads, head_dim), indices_k)
    value_layer = index_first_axis(value_layer.reshape(batch_size * kv_seq_len, num_key_value_heads, head_dim), indices_k)
    if query_length == kv_seq_len:
        query_layer = index_first_axis(query_layer.reshape(batch_size * kv_seq_len, -1, head_dim), indices_k)
        cu_seqlens_q = cu_seqlens_k
        max_seqlen_in_batch_q = max_seqlen_in_batch_k
        indices_q = indices_k
    elif query_length == 1:
        max_seqlen_in_batch_q = 1
        cu_seqlens_q = torch.arange(batch_size + 1, dtype=torch.int32, device=query_layer.device)
        indices_q = cu_seqlens_q[:-1]
        query_layer = query_layer.squeeze(1)
    else:
        attention_mask = attention_mask[:, -query_length:]
        query_layer, indices_q, cu_seqlens_q, max_seqlen_in_batch_q = unpad_input(query_layer, attention_mask)
    return (query_layer, key_layer, value_layer, indices_q, (cu_seqlens_q, cu_seqlens_k), (max_seqlen_in_batch_q, max_seqlen_in_batch_k),)
def prepare_fa2_from_position_ids(query, key, value, position_ids):
    query = query.view(-1, query.size(-2), query.size(-1))
    key = key.view(-1, key.size(-2), key.size(-1))
    value = value.view(-1, value.size(-2), value.size(-1))
    position_ids = position_ids.flatten()
    indices_q = torch.arange(position_ids.size(0), device=position_ids.device, dtype=torch.int32)
    cu_seq_lens = torch.cat((indices_q[position_ids == 0], torch.tensor(position_ids.size(), device=position_ids.device, dtype=torch.int32),))
    max_length = position_ids.max() + 1
    return (query, key, value, indices_q, (cu_seq_lens, cu_seq_lens), (max_length, max_length))
def _flash_attention_forward(query_states: torch.Tensor, key_states: torch.Tensor, value_states: torch.Tensor, attention_mask: torch.Tensor, query_length: int,
is_causal: bool, dropout: float = 0.0, position_ids: Optional[torch.Tensor] = None, softmax_scale: Optional[float] = None, sliding_window: Optional[int] = None, use_top_left_mask: bool = False, softcap: Optional[float] = None, deterministic: bool = None):
    if not use_top_left_mask: causal = is_causal
    else: causal = is_causal and query_length != 1
    use_sliding_windows = (_flash_supports_window_size and sliding_window is not None and key_states.shape[1] > sliding_window)
    flash_kwargs = {"window_size": (sliding_window, sliding_window)} if use_sliding_windows else {}
    if is_flash_attn_greater_or_equal("2.4.1"):
        if deterministic is None: deterministic = os.environ.get("FLASH_ATTENTION_DETERMINISTIC", "0") == "1"
        flash_kwargs["deterministic"] = deterministic
    if softcap is not None: flash_kwargs["softcap"] = softcap
    if attention_mask is not None:
        batch_size = query_states.shape[0]
        query_states, key_states, value_states, indices_q, cu_seq_lens, max_seq_lens = _upad_input(query_states, key_states, value_states, attention_mask, query_length)
        cu_seqlens_q, cu_seqlens_k = cu_seq_lens
        max_seqlen_in_batch_q, max_seqlen_in_batch_k = max_seq_lens
        attn_output_unpad = flash_attn_varlen_func(query_states, key_states, value_states, cu_seqlens_q=cu_seqlens_q, cu_seqlens_k=cu_seqlens_k, max_seqlen_q=max_seqlen_in_batch_q, max_seqlen_k=max_seqlen_in_batch_k, dropout_p=dropout, softmax_scale=softmax_scale, causal=causal, **flash_kwargs)
        attn_output = pad_input(attn_output_unpad, indices_q, batch_size, query_length)
    elif position_ids is not None and not (torch.diff(position_ids, dim=-1) >= 0).all() and query_length != 1:
        batch_size = query_states.size(0)
        query_states, key_states, value_states, indices_q, cu_seq_lens, max_seq_lens = prepare_fa2_from_position_ids(query_states, key_states, value_states, position_ids)
        cu_seqlens_q, cu_seqlens_k = cu_seq_lens
        max_seqlen_in_batch_q, max_seqlen_in_batch_k = max_seq_lens
        attn_output = flash_attn_varlen_func(query_states, key_states, value_states, cu_seqlens_q=cu_seqlens_q, cu_seqlens_k=cu_seqlens_k, max_seqlen_q=max_seqlen_in_batch_q, max_seqlen_k=max_seqlen_in_batch_k, dropout_p=dropout, softmax_scale=softmax_scale, causal=causal, **flash_kwargs)
        attn_output = attn_output.view(batch_size, -1, attn_output.size(-2), attn_output.size(-1))
    else: attn_output = flash_attn_func(query_states, key_states, value_states, dropout, softmax_scale=softmax_scale, causal=causal, **flash_kwargs)
    return attn_output
class FlashAttentionKwargs(TypedDict, total=False):
    cu_seq_lens_q: Optional[torch.LongTensor]
    cu_seq_lens_k: Optional[torch.LongTensor]
    max_length_q: Optional[int]
    max_length_k: Optional[int]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
