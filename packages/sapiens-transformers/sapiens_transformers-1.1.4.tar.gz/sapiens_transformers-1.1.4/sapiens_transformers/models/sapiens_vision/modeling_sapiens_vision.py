"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import torch as sapiens_technology_torch
from ...utils import (is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, add_start_docstrings, add_start_docstrings_to_model_forward)
if is_flash_attn_2_available():
    from flash_attn import flash_attn_varlen_func
    from ...modeling_flash_attention_utils import _flash_attention_forward
else: flash_attn_varlen_func = None
from .configuration_sapiens_vision import SapiensVisionConfig, SapiensVisionVisionConfig
_CONFIG_FOR_DOC = "SapiensVisionConfig"
def rotate_half(x): return sapiens_technology_torch.cat((-x[..., x.shape[-1] // 2 :], x[..., : x.shape[-1] // 2]), dim=-1)
def apply_multimodal_rotary_pos_emb(q, k, cos, sin, mrope_section, unsqueeze_dim=1):
    mrope_section = mrope_section * 2
    cos = sapiens_technology_torch.cat([m[i % 3] for i, m in enumerate(cos.split(mrope_section, dim=-1))], dim=-1).unsqueeze(unsqueeze_dim)
    sin = sapiens_technology_torch.cat([m[i % 3] for i, m in enumerate(sin.split(mrope_section, dim=-1))], dim=-1).unsqueeze(unsqueeze_dim)
    return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)
def apply_rotary_pos_emb_vision(tensor: sapiens_technology_torch.Tensor, freqs: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
    orig_dtype = tensor.dtype
    tensor = tensor.float()
    cos, sin = freqs.cos(), freqs.sin()
    cos, sin = cos.unsqueeze(1).repeat(1, 1, 2).unsqueeze(0).float(), sin.unsqueeze(1).repeat(1, 1, 2).unsqueeze(0).float()
    return ((tensor * cos) + (rotate_half(tensor) * sin)).to(orig_dtype)
import torch.nn as sapiens_technology_neural_network
class VisionRotaryEmbedding(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, theta: float = 10000.0) -> None:
        super().__init__()
        inv_freq = 1.0 / (theta ** (sapiens_technology_torch.arange(0, dim, 2, dtype=sapiens_technology_torch.float) / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
    def forward(self, seqlen: int) -> sapiens_technology_torch.Tensor: return sapiens_technology_torch.outer(sapiens_technology_torch.arange(seqlen, device=self.inv_freq.device, dtype=self.inv_freq.dtype), self.inv_freq)
class PatchEmbed(sapiens_technology_neural_network.Module):
    def __init__(self, patch_size: int = 14, temporal_patch_size: int = 2, in_channels: int = 3, embed_dim: int = 1152) -> None:
        super().__init__()
        self.patch_size, self.temporal_patch_size, self.in_channels, self.embed_dim = patch_size, temporal_patch_size, in_channels, embed_dim
        kernel_size = [temporal_patch_size, patch_size, patch_size]
        self.proj = sapiens_technology_neural_network.Conv3d(in_channels, embed_dim, kernel_size=kernel_size, stride=kernel_size, bias=False)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor: return self.proj(hidden_states.view(-1, self.in_channels, self.temporal_patch_size, self.patch_size, self.patch_size).to(dtype=self.proj.weight.dtype)).view(-1, self.embed_dim)
from torch.nn import LayerNorm, CrossEntropyLoss
class PatchMerger(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, context_dim: int, spatial_merge_size: int = 2) -> None:
        super().__init__()
        self.hidden_size, self.ln_q = context_dim * (spatial_merge_size**2), LayerNorm(context_dim, eps=1e-6)
        self.mlp = sapiens_technology_neural_network.Sequential(sapiens_technology_neural_network.Linear(self.hidden_size, self.hidden_size), sapiens_technology_neural_network.GELU(), sapiens_technology_neural_network.Linear(self.hidden_size, dim))
    def forward(self, x: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor: return self.mlp(self.ln_q(x).view(-1, self.hidden_size))
from ...activations import ACT2FN
class VisionMlp(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, hidden_dim: int, hidden_act: str) -> None:
        super().__init__()
        self.fc1, self.act, self.fc2 = sapiens_technology_neural_network.Linear(dim, hidden_dim), ACT2FN[hidden_act], sapiens_technology_neural_network.Linear(hidden_dim, dim)
    def forward(self, x) -> sapiens_technology_torch.Tensor: return self.fc2(self.act(self.fc1(x)))
class VisionAttention(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, num_heads: int = 16) -> None:
        super().__init__()
        self.num_heads, self.head_dim, self.qkv, self.proj = num_heads, dim // num_heads, sapiens_technology_neural_network.Linear(dim, dim * 3, bias=True), sapiens_technology_neural_network.Linear(dim, dim)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cu_seqlens: sapiens_technology_torch.Tensor, rotary_pos_emb: sapiens_technology_torch.Tensor = None) -> sapiens_technology_torch.Tensor:
        seq_length = hidden_states.shape[0]
        q, k, v = self.qkv(hidden_states).reshape(seq_length, 3, self.num_heads, -1).permute(1, 0, 2, 3).unbind(0)
        q, k = apply_rotary_pos_emb_vision(q.unsqueeze(0), rotary_pos_emb).squeeze(0), apply_rotary_pos_emb_vision(k.unsqueeze(0), rotary_pos_emb).squeeze(0)
        attention_mask = sapiens_technology_torch.full([1, seq_length, seq_length], sapiens_technology_torch.finfo(q.dtype).min, device=q.device, dtype=q.dtype)
        for i in range(1, len(cu_seqlens)): attention_mask[..., cu_seqlens[i - 1] : cu_seqlens[i], cu_seqlens[i - 1] : cu_seqlens[i]] = 0
        q, k, v = q.transpose(0, 1), k.transpose(0, 1), v.transpose(0, 1)
        from math import sqrt
        attn_weights = sapiens_technology_neural_network.functional.softmax(sapiens_technology_torch.matmul(q, k.transpose(1, 2)) / sqrt(self.head_dim) + attention_mask, dim=-1, dtype=sapiens_technology_torch.float32).to(q.dtype)
        return self.proj(sapiens_technology_torch.matmul(attn_weights, v).transpose(0, 1).reshape(seq_length, -1))
class VisionFlashAttention2(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, num_heads: int = 16) -> None:
        super().__init__()
        self.num_heads, self.qkv, self.proj = num_heads, sapiens_technology_neural_network.Linear(dim, dim * 3, bias=True), sapiens_technology_neural_network.Linear(dim, dim)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cu_seqlens: sapiens_technology_torch.Tensor, rotary_pos_emb: sapiens_technology_torch.Tensor = None) -> sapiens_technology_torch.Tensor:
        seq_length = hidden_states.shape[0]
        q, k, v = self.qkv(hidden_states).reshape(seq_length, 3, self.num_heads, -1).permute(1, 0, 2, 3).unbind(0)
        q, k = apply_rotary_pos_emb_vision(q.unsqueeze(0), rotary_pos_emb).squeeze(0), apply_rotary_pos_emb_vision(k.unsqueeze(0), rotary_pos_emb).squeeze(0)
        max_seqlen = (cu_seqlens[1:] - cu_seqlens[:-1]).max().item()
        return self.proj(flash_attn_varlen_func(q, k, v, cu_seqlens, cu_seqlens, max_seqlen, max_seqlen).reshape(seq_length, -1))
import torch.nn.functional as Functional
class VisionSdpaAttention(sapiens_technology_neural_network.Module):
    def __init__(self, dim: int, num_heads: int = 16) -> None:
        super().__init__()
        self.num_heads, self.qkv, self.proj = num_heads, sapiens_technology_neural_network.Linear(dim, dim * 3, bias=True), sapiens_technology_neural_network.Linear(dim, dim)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cu_seqlens: sapiens_technology_torch.Tensor, rotary_pos_emb: sapiens_technology_torch.Tensor = None) -> sapiens_technology_torch.Tensor:
        seq_length = hidden_states.shape[0]
        q, k, v = self.qkv(hidden_states).reshape(seq_length, 3, self.num_heads, -1).permute(1, 0, 2, 3).unbind(0)
        q, k = apply_rotary_pos_emb_vision(q.unsqueeze(0), rotary_pos_emb).squeeze(0), apply_rotary_pos_emb_vision(k.unsqueeze(0), rotary_pos_emb).squeeze(0)
        attention_mask = sapiens_technology_torch.zeros([1, seq_length, seq_length], device=q.device, dtype=sapiens_technology_torch.bool)
        for i in range(1, len(cu_seqlens)): attention_mask[..., cu_seqlens[i - 1] : cu_seqlens[i], cu_seqlens[i - 1] : cu_seqlens[i]] = True
        q, k, v = q.transpose(0, 1), k.transpose(0, 1), v.transpose(0, 1)
        return self.proj(Functional.scaled_dot_product_attention(q, k, v, attention_mask, dropout_p=0.0).transpose(0, 1).reshape(seq_length, -1))
SAPIENS_VISION_ATTENTION_CLASSES = {"eager": VisionAttention, "flash_attention_2": VisionFlashAttention2, "sdpa": VisionSdpaAttention}
class SapiensVisionVisionBlock(sapiens_technology_neural_network.Module):
    def __init__(self, config, attn_implementation: str = "sdpa") -> None:
        super().__init__()
        self.norm1, self.norm2 = LayerNorm(config.embed_dim, eps=1e-6), LayerNorm(config.embed_dim, eps=1e-6)
        self.attn, self.mlp = SAPIENS_VISION_ATTENTION_CLASSES[attn_implementation](config.embed_dim, num_heads=config.num_heads), VisionMlp(dim=config.embed_dim, hidden_dim=int(config.embed_dim * config.mlp_ratio), hidden_act=config.hidden_act)
    def forward(self, hidden_states, cu_seqlens, rotary_pos_emb) -> sapiens_technology_torch.Tensor:
        hidden_states = hidden_states + self.attn(self.norm1(hidden_states), cu_seqlens=cu_seqlens, rotary_pos_emb=rotary_pos_emb)
        return hidden_states + self.mlp(self.norm2(hidden_states))
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: sapiens_technology_torch.Tensor, sequence_length: int, target_length: int, dtype: sapiens_technology_torch.dtype, device: sapiens_technology_torch.device,
min_dtype: float, cache_position: sapiens_technology_torch.Tensor, batch_size: int):
    if attention_mask is not None and attention_mask.dim() == 4: causal_mask = attention_mask
    else:
        causal_mask = sapiens_technology_torch.full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != 1: causal_mask = sapiens_technology_torch.triu(causal_mask, diagonal=1)
        causal_mask *= sapiens_technology_torch.arange(target_length, device=device) > cache_position.reshape(-1, 1)
        causal_mask = causal_mask[None, None, :, :].expand(batch_size, 1, -1, -1)
        if attention_mask is not None:
            causal_mask, mask_length = causal_mask.clone(), attention_mask.shape[-1]
            padding_mask = causal_mask[:, :, :, :mask_length] + attention_mask[:, None, None, :] == 0
            causal_mask[:, :, :, :mask_length] = causal_mask[:, :, :, :mask_length].masked_fill(padding_mask, min_dtype)
    return causal_mask
from typing import Optional, Tuple, List, Union, Dict, Any
class SapiensRMSNorm(sapiens_technology_neural_network.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight, self.variance_epsilon = sapiens_technology_neural_network.Parameter(sapiens_technology_torch.ones(hidden_size)), eps
    def forward(self, hidden_states):
        input_dtype, hidden_states = hidden_states.dtype, hidden_states.to(sapiens_technology_torch.float32)
        return self.weight * (hidden_states * sapiens_technology_torch.rsqrt(hidden_states.pow(2).mean(-1, keepdim=True) + self.variance_epsilon)).to(input_dtype)
    def extra_repr(self): return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"
class SapiensVisionRotaryEmbedding(sapiens_technology_neural_network.Module):
    def __init__(self, dim=None, max_position_embeddings=2048, base=10000, device=None, scaling_factor=1.0, rope_type="default", config: Optional[SapiensVisionConfig] = None):
        super().__init__()
        self.rope_kwargs = {}
        if config is None:
            self.rope_kwargs = {"rope_type": rope_type, "factor": scaling_factor, "dim": dim, "base": base, "max_position_embeddings": max_position_embeddings}
            self.rope_type, self.max_seq_len_cached, self.original_max_seq_len = rope_type, max_position_embeddings, max_position_embeddings
        else:
            if config.rope_scaling is not None: self.rope_type = config.rope_scaling.get("rope_type", config.rope_scaling.get("type"))
            else: self.rope_type = "default"
            self.max_seq_len_cached, self.original_max_seq_len = config.max_position_embeddings, config.max_position_embeddings
        from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
        self.config, self.rope_init_fn = config, ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, **self.rope_kwargs)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.original_inv_freq = self.inv_freq
    def _dynamic_frequency_update(self, position_ids, device):
        seq_len = sapiens_technology_torch.max(position_ids) + 1
        if seq_len > self.max_seq_len_cached:
            inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, seq_len=seq_len, **self.rope_kwargs)
            self.register_buffer("inv_freq", inv_freq, persistent=False)
            self.max_seq_len_cached = seq_len
        if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:
            self.register_buffer("inv_freq", self.original_inv_freq, persistent=False)
            self.max_seq_len_cached = self.original_max_seq_len
    @sapiens_technology_torch.no_grad()
    def forward(self, x, position_ids):
        if "dynamic" in self.rope_type: self._dynamic_frequency_update(position_ids, device=x.device)
        inv_freq_expanded, position_ids_expanded, device_type = self.inv_freq[None, None, :, None].float().expand(3, position_ids.shape[1], -1, 1), position_ids[:, :, None, :].float(), x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with sapiens_technology_torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(2, 3)
            emb = sapiens_technology_torch.cat((freqs, freqs), dim=-1)
            cos, sin = emb.cos(), emb.sin()
        return (cos * self.attention_scaling).to(dtype=x.dtype), (sin * self.attention_scaling).to(dtype=x.dtype)
class SapiensMLP(sapiens_technology_neural_network.Module):
    def __init__(self, config):
        super().__init__()
        self.hidden_size, self.intermediate_size, self.act_fn = config.hidden_size, config.intermediate_size, ACT2FN[config.hidden_act]
        self.gate_proj = sapiens_technology_neural_network.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.up_proj = sapiens_technology_neural_network.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj = sapiens_technology_neural_network.Linear(self.intermediate_size, self.hidden_size, bias=False)
    def forward(self, hidden_state): return self.down_proj(self.act_fn(self.gate_proj(hidden_state)) * self.up_proj(hidden_state))
def repeat_kv(hidden_states: sapiens_technology_torch.Tensor, n_rep: int) -> sapiens_technology_torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    return hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim).reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
from ...cache_utils import Cache, StaticCache
class SapiensVisionAttention(sapiens_technology_neural_network.Module):
    def __init__(self, config: SapiensVisionConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config, self.layer_idx, self.hidden_size = config, layer_idx, config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.hidden_size // self.num_heads
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings, self.rope_theta, self.is_causal = config.max_position_embeddings, config.rope_theta, True
        self.attention_dropout, self.rope_scaling = config.attention_dropout, config.rope_scaling
        if (self.head_dim * self.num_heads) != self.hidden_size: raise ValueError(f"hidden_size must be divisible by num_heads (got `hidden_size`: {self.hidden_size} and `num_heads`: {self.num_heads}).")
        self.q_proj, self.k_proj = sapiens_technology_neural_network.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=True), sapiens_technology_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=True)
        self.v_proj, self.o_proj = sapiens_technology_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=True), sapiens_technology_neural_network.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        self.rotary_emb = SapiensVisionRotaryEmbedding(self.head_dim, max_position_embeddings=self.max_position_embeddings, base=self.rope_theta)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_technology_torch.LongTensor] = None,
    position_embeddings: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None) -> Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor], Optional[Tuple[sapiens_technology_torch.Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states, kv_seq_len = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), key_states.shape[-2]
        if past_key_value is not None: kv_seq_len += cache_position[0] + 1
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_multimodal_rotary_pos_emb(query_states, key_states, cos, sin, self.rope_scaling["mrope_section"])
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        from math import sqrt
        attn_weights = sapiens_technology_torch.matmul(query_states, key_states.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
        if query_states.dtype == sapiens_technology_torch.float16: attn_weights = sapiens_technology_torch.where(sapiens_technology_torch.isinf(attn_weights), sapiens_technology_torch.zeros_like(attn_weights), attn_weights)
        attn_weights = sapiens_technology_neural_network.functional.dropout(sapiens_technology_neural_network.functional.softmax(attn_weights, dim=-1, dtype=sapiens_technology_torch.float32).to(query_states.dtype), p=self.attention_dropout, training=self.training)
        attn_output = sapiens_technology_torch.matmul(attn_weights, value_states)
        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = self.o_proj(attn_output.transpose(1, 2).contiguous().reshape(bsz, q_len, -1))
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class SapiensVisionFlashAttention2(SapiensVisionAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_technology_torch.LongTensor] = None, position_embeddings: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None):
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states, kv_seq_len = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), key_states.shape[-2]
        if past_key_value is not None:
            if self.layer_idx is None: raise ValueError(f"The cache structure has changed since version v4.36. If you are using {self.__class__.__name__} for auto-regressive decoding with k/v caching, please make sure to initialize the attention class with a layer index.")
            kv_seq_len += past_key_value.get_usable_length(kv_seq_len, self.layer_idx)
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_multimodal_rotary_pos_emb(query_states, key_states, cos, sin, self.rope_scaling["mrope_section"])
        if past_key_value is not None:
            cache_has_contents = past_key_value.get_seq_length(self.layer_idx) > 0
            if (getattr(self.config, "sliding_window", None) is not None and kv_seq_len > self.config.sliding_window and cache_has_contents):
                slicing_tokens = 1 - self.config.sliding_window
                past_key, past_value = past_key_value[self.layer_idx][0], past_key_value[self.layer_idx][1]
                past_key, past_value = past_key[:, :, slicing_tokens:, :].contiguous(), past_value[:, :, slicing_tokens:, :].contiguous()
                if past_key.shape[-2] != self.config.sliding_window - 1: raise ValueError(f"past key must have a shape of (`batch_size, num_heads, self.config.sliding_window-1, head_dim`), got {past_key.shape}")
                if attention_mask is not None:
                    attention_mask = attention_mask[:, slicing_tokens:]
                    attention_mask = sapiens_technology_torch.cat([attention_mask, sapiens_technology_torch.ones_like(attention_mask[:, -1:])], dim=-1)
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        dropout_rate, input_dtype = 0.0 if not self.training else self.attention_dropout, query_states.dtype
        if input_dtype == sapiens_technology_torch.float32:
            if sapiens_technology_torch.is_autocast_enabled(): target_dtype = sapiens_technology_torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            query_states, key_states, value_states = query_states.to(target_dtype), key_states.to(target_dtype), value_states.to(target_dtype)
        query_states, key_states, value_states = query_states.transpose(1, 2), key_states.transpose(1, 2), value_states.transpose(1, 2)
        if (self.config.use_sliding_window and getattr(self.config, "sliding_window", None) is not None and self.layer_idx >= self.config.max_window_layers): sliding_window = self.config.sliding_window
        else: sliding_window = None
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, dropout=dropout_rate, sliding_window=sliding_window,
        is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        if not output_attentions: attn_weights = None
        return self.o_proj(attn_output.reshape(bsz, q_len, self.hidden_size).contiguous()), attn_weights, past_key_value
class SapiensVisionSdpaAttention(SapiensVisionAttention):
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_technology_torch.LongTensor] = None,
    position_embeddings: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None) -> Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor], Optional[Tuple[sapiens_technology_torch.Tensor]]]:
        if output_attentions:
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions,
            use_cache=use_cache, cache_position=cache_position)
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states, kv_seq_len = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), key_states.shape[-2]
        if past_key_value is not None: kv_seq_len += past_key_value.get_usable_length(kv_seq_len, self.layer_idx)
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_multimodal_rotary_pos_emb(query_states, key_states, cos, sin, self.rope_scaling["mrope_section"])
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states, causal_mask = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups), attention_mask
        if attention_mask is not None: causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and attention_mask is not None: query_states, key_states, value_states = query_states.contiguous(), key_states.contiguous(), value_states.contiguous()
        is_causal = True if causal_mask is None and q_len > 1 else False
        attn_output = sapiens_technology_torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.attention_dropout if self.training else 0.0, is_causal=is_causal)
        return self.o_proj(attn_output.transpose(1, 2).contiguous().view(bsz, q_len, self.hidden_size)), None, past_key_value
SAPIENS_ATTENTION_CLASSES = {"eager": SapiensVisionAttention, "flash_attention_2": SapiensVisionFlashAttention2, "sdpa": SapiensVisionSdpaAttention}
class SapiensVisionDecoderLayer(sapiens_technology_neural_network.Module):
    def __init__(self, config: SapiensVisionConfig, layer_idx: int):
        super().__init__()
        self.hidden_size, self.self_attn = config.hidden_size, SAPIENS_ATTENTION_CLASSES[config._attn_implementation](config, layer_idx)
        self.mlp, self.input_layernorm = SapiensMLP(config), SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_value: Optional[Tuple[sapiens_technology_torch.Tensor]] = None,
    output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[sapiens_technology_torch.LongTensor] = None, position_embeddings: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None,
    **kwargs) -> Tuple[sapiens_technology_torch.FloatTensor, Optional[Tuple[sapiens_technology_torch.FloatTensor, sapiens_technology_torch.FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids,
        past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
        hidden_states = residual + hidden_states
        residual = hidden_states
        outputs = (residual + self.mlp(self.post_attention_layernorm(hidden_states)),)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
SAPIENS_VISION_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SapiensVisionConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
SAPIENS_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `decoder_input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`. [What are position IDs?](../glossary#position-ids)
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)` and 2 additional tensors of shape
            `(batch_size, num_heads, encoder_sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used (see `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        pixel_values (`torch.FloatTensor` of shape `(seq_length, num_channels * image_size * image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`SapiensVisionImageProcessor.__call__`] for details. [`SapiensVisionProcessor`] uses
            [`SapiensVisionImageProcessor`] for processing images.
        pixel_values_videos (`torch.FloatTensor` of shape `(seq_length, num_channels * temporal_size * image_size * image_size)):
            The tensors corresponding to the input videos. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`SapiensVisionImageProcessor.__call__`] for details. [`SapiensVisionProcessor`] uses
            [`SapiensVisionImageProcessor`] for processing videos.
        image_grid_thw (`torch.LongTensor` of shape `(num_images, 3)`, *optional*):
            The temporal, height and width of feature shape of each image in LLM.
        video_grid_thw (`torch.LongTensor` of shape `(num_videos, 3)`, *optional*):
            The temporal, height and width of feature shape of each video in LLM.
        rope_deltas (`torch.LongTensor` of shape `(batch_size, )`, *optional*):
            The rope index difference between sequence length and multimodal rope.
"""
from ...modeling_utils import PreTrainedModel
@add_start_docstrings("The bare SapiensVision Model outputting raw hidden-states without any specific head on top.", SAPIENS_VISION_START_DOCSTRING)
class SapiensVisionPreTrainedModel(PreTrainedModel):
    config_class, base_model_prefix, supports_gradient_checkpointing = SapiensVisionConfig, "model", True
    _no_split_modules, _skip_keys_device_placement = ["SapiensVisionDecoderLayer", "SapiensVisionVisionBlock"], "past_key_values"
    _supports_flash_attn_2, _supports_sdpa, _supports_cache_class, _supports_static_cache = True, True, True, True
    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, (sapiens_technology_neural_network.Linear, sapiens_technology_neural_network.Conv3d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, sapiens_technology_neural_network.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
class SapiensVisionTransformerPretrainedModel(SapiensVisionPreTrainedModel):
    config_class = SapiensVisionVisionConfig
    _no_split_modules = ["SapiensVisionVisionBlock"]
    def __init__(self, config) -> None:
        super().__init__(config)
        self.spatial_merge_size, head_dim = config.spatial_merge_size, config.embed_dim // config.num_heads
        self.patch_embed = PatchEmbed(patch_size=config.patch_size, temporal_patch_size=config.temporal_patch_size, in_channels=config.in_channels, embed_dim=config.embed_dim)
        self.rotary_pos_emb = VisionRotaryEmbedding(head_dim // 2)
        self.blocks = sapiens_technology_neural_network.ModuleList([SapiensVisionVisionBlock(config, config._attn_implementation) for _ in range(config.depth)])
        self.merger = PatchMerger(dim=config.hidden_size, context_dim=config.embed_dim, spatial_merge_size=config.spatial_merge_size)
    def get_dtype(self) -> sapiens_technology_torch.dtype: return self.blocks[0].mlp.fc2.weight.dtype
    def get_device(self) -> sapiens_technology_torch.device: return self.blocks[0].mlp.fc2.weight.device
    def rot_pos_emb(self, grid_thw):
        pos_ids = []
        for t, h, w in grid_thw:
            hpos_ids = sapiens_technology_torch.arange(h).unsqueeze(1).expand(-1, w).reshape(h // self.spatial_merge_size, self.spatial_merge_size, w // self.spatial_merge_size, self.spatial_merge_size).permute(0, 2, 1, 3).flatten()
            wpos_ids = sapiens_technology_torch.arange(w).unsqueeze(0).expand(h, -1).reshape(h // self.spatial_merge_size, self.spatial_merge_size, w // self.spatial_merge_size, self.spatial_merge_size).permute(0, 2, 1, 3).flatten()
            pos_ids.append(sapiens_technology_torch.stack([hpos_ids, wpos_ids], dim=-1).repeat(t, 1))
        pos_ids = sapiens_technology_torch.cat(pos_ids, dim=0)
        return self.rotary_pos_emb(grid_thw[:, 1:].max())[pos_ids].flatten(1)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, grid_thw: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        hidden_states, rotary_pos_emb = self.patch_embed(hidden_states), self.rot_pos_emb(grid_thw)
        cu_seqlens = sapiens_technology_torch.repeat_interleave(grid_thw[:, 1] * grid_thw[:, 2], grid_thw[:, 0]).cumsum(dim=0, dtype=sapiens_technology_torch.int32)
        for blk in self.blocks: hidden_states = blk(hidden_states, cu_seqlens=Functional.pad(cu_seqlens, (1, 0), value=0), rotary_pos_emb=rotary_pos_emb)
        return self.merger(hidden_states)
from ...modeling_outputs import BaseModelOutputWithPast, ModelOutput
@add_start_docstrings("The bare SapiensVision Model outputting raw hidden-states without any specific head on top.", SAPIENS_VISION_START_DOCSTRING)
class SapiensVisionModel(SapiensVisionPreTrainedModel):
    def __init__(self, config: SapiensVisionConfig):
        super().__init__(config)
        self.padding_idx, self.vocab_size = config.pad_token_id, config.vocab_size
        self.embed_tokens = sapiens_technology_neural_network.Embedding(config.vocab_size, config.hidden_size, self.padding_idx)
        self.layers = sapiens_technology_neural_network.ModuleList([SapiensVisionDecoderLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)])
        self._attn_implementation, self.norm = config._attn_implementation, SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb, self.gradient_checkpointing = SapiensVisionRotaryEmbedding(config=config), False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    def forward(self, input_ids: sapiens_technology_torch.LongTensor = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None,
    past_key_values: Optional[List[sapiens_technology_torch.FloatTensor]] = None, inputs_embeds: Optional[sapiens_technology_torch.FloatTensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[sapiens_technology_torch.LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache, return_dict = use_cache if use_cache is not None else self.config.use_cache, return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training:
            if use_cache: use_cache = False
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = sapiens_technology_torch.arange(past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.view(1, 1, -1).expand(3, inputs_embeds.shape[0], -1)
        elif position_ids.dim() == 2: position_ids = position_ids[None, ...].expand(3, position_ids.shape[0], -1)
        causal_mask, hidden_states = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions), inputs_embeds
        position_embeddings, all_hidden_states, all_self_attns, next_decoder_cache = self.rotary_emb(hidden_states, position_ids), () if output_hidden_states else None, () if output_attentions else None, None
        for decoder_layer in self.layers:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, causal_mask,
            position_ids, past_key_values, output_attentions, use_cache, cache_position, position_embeddings)
            else: layer_outputs = decoder_layer(hidden_states, attention_mask=causal_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions,
            use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache = layer_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (layer_outputs[1],)
        hidden_states = self.norm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns)
    def _update_causal_mask(self, attention_mask: sapiens_technology_torch.Tensor, input_tensor: sapiens_technology_torch.Tensor, cache_position: sapiens_technology_torch.Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens, using_static_cache = past_key_values.get_seq_length() if past_key_values is not None else 0, isinstance(past_key_values, StaticCache)
        from ...modeling_attn_mask_utils import AttentionMaskConverter
        if self.config._attn_implementation == "sdpa" and not using_static_cache and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype, sequence_length = sapiens_technology_torch.finfo(dtype).min, input_tensor.shape[1]
        if using_static_cache: target_length = past_key_values.get_max_length()
        else: target_length = (attention_mask.shape[-1] if isinstance(attention_mask, sapiens_technology_torch.Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
from dataclasses import dataclass
@dataclass
class SapiensVisionCausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: Optional[sapiens_technology_torch.FloatTensor] = None
    logits: sapiens_technology_torch.FloatTensor = None
    past_key_values: Optional[List[sapiens_technology_torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[sapiens_technology_torch.FloatTensor]] = None
    attentions: Optional[Tuple[sapiens_technology_torch.FloatTensor]] = None
    rope_deltas: Optional[sapiens_technology_torch.LongTensor] = None
from ...generation import GenerationMixin
class SapiensVisionForConditionalGeneration(SapiensVisionPreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        super().__init__(config)
        self.visual = SapiensVisionTransformerPretrainedModel._from_config(config.vision_config, attn_implementation=config._attn_implementation)
        self.model, self.vocab_size = SapiensVisionModel(config), config.vocab_size
        self.lm_head, self.padding_side = sapiens_technology_neural_network.Linear(config.hidden_size, config.vocab_size, bias=False), "left"
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value): self.model.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def set_decoder(self, decoder): self.model = decoder
    def get_decoder(self): return self.model
    def get_rope_index(self, input_ids: sapiens_technology_torch.LongTensor, image_grid_thw: Optional[sapiens_technology_torch.LongTensor] = None, video_grid_thw: Optional[sapiens_technology_torch.LongTensor] = None,
    attention_mask: Optional[sapiens_technology_torch.Tensor] = None) -> Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]:
        spatial_merge_size, image_token_id, video_token_id = self.config.vision_config.spatial_merge_size, self.config.image_token_id, self.config.video_token_id
        vision_start_token_id, mrope_position_deltas = self.config.vision_start_token_id, []
        if image_grid_thw is not None or video_grid_thw is not None:
            total_input_ids, position_ids, image_index, video_index = input_ids, sapiens_technology_torch.ones(3, input_ids.shape[0], input_ids.shape[1], dtype=input_ids.dtype, device=input_ids.device), 0, 0
            for i, input_ids in enumerate(total_input_ids):
                if attention_mask is not None: input_ids = input_ids[attention_mask[i] == 1]
                image_nums, video_nums = 0, 0
                vision_tokens = input_ids[sapiens_technology_torch.argwhere(input_ids == vision_start_token_id).squeeze(1) + 1]
                image_nums, video_nums = (vision_tokens == image_token_id).sum(), (vision_tokens == video_token_id).sum()
                input_tokens, st = input_ids.tolist(), 0
                llm_pos_ids_list: list = []
                remain_images, remain_videos = image_nums, video_nums
                for _ in range(image_nums + video_nums):
                    if image_token_id in input_tokens and remain_images > 0: ed_image = input_tokens.index(image_token_id, st)
                    else: ed_image = len(input_tokens) + 1
                    if video_token_id in input_tokens and remain_videos > 0: ed_video = input_tokens.index(video_token_id, st)
                    else: ed_video = len(input_tokens) + 1
                    if ed_image < ed_video:
                        t, h, w = (image_grid_thw[image_index][0], image_grid_thw[image_index][1], image_grid_thw[image_index][2])
                        image_index += 1
                        remain_images -= 1
                        ed = ed_image
                    else:
                        t, h, w = (video_grid_thw[video_index][0], video_grid_thw[video_index][1], video_grid_thw[video_index][2])
                        video_index += 1
                        remain_videos -= 1
                        ed = ed_video
                    llm_grid_t, llm_grid_h, llm_grid_w = (t.item(), h.item() // spatial_merge_size, w.item() // spatial_merge_size)
                    text_len, st_idx = ed - st, llm_pos_ids_list[-1].max() + 1 if len(llm_pos_ids_list) > 0 else 0
                    llm_pos_ids_list.append(sapiens_technology_torch.arange(text_len).view(1, -1).expand(3, -1) + st_idx)
                    t_index = sapiens_technology_torch.arange(llm_grid_t).view(-1, 1).expand(-1, llm_grid_h * llm_grid_w).flatten()
                    h_index = sapiens_technology_torch.arange(llm_grid_h).view(1, -1, 1).expand(llm_grid_t, -1, llm_grid_w).flatten()
                    w_index = sapiens_technology_torch.arange(llm_grid_w).view(1, 1, -1).expand(llm_grid_t, llm_grid_h, -1).flatten()
                    llm_pos_ids_list.append(sapiens_technology_torch.stack([t_index, h_index, w_index]) + text_len + st_idx)
                    st = ed + llm_grid_t * llm_grid_h * llm_grid_w
                if st < len(input_tokens):
                    st_idx, text_len = llm_pos_ids_list[-1].max() + 1 if len(llm_pos_ids_list) > 0 else 0, len(input_tokens) - st
                    llm_pos_ids_list.append(sapiens_technology_torch.arange(text_len).view(1, -1).expand(3, -1) + st_idx)
                llm_positions = sapiens_technology_torch.cat(llm_pos_ids_list, dim=1).reshape(3, -1)
                position_ids[..., i, attention_mask[i] == 1] = llm_positions.to(position_ids.device)
                mrope_position_deltas.append(llm_positions.max() + 1 - len(total_input_ids[i]))
            mrope_position_deltas = sapiens_technology_torch.tensor(mrope_position_deltas, device=input_ids.device).unsqueeze(1)
            return position_ids, mrope_position_deltas
        else:
            if attention_mask is not None:
                position_ids = attention_mask.long().cumsum(-1) - 1
                position_ids.masked_fill_(attention_mask == 0, 1)
                position_ids = position_ids.unsqueeze(0).expand(3, -1, -1).to(input_ids.device)
                max_position_ids = position_ids.max(0, keepdim=False)[0].max(-1, keepdim=True)[0]
                mrope_position_deltas = max_position_ids + 1 - attention_mask.shape[-1]
            else:
                position_ids = (sapiens_technology_torch.arange(input_ids.shape[1], device=input_ids.device).view(1, 1, -1).expand(3, input_ids.shape[0], -1))
                mrope_position_deltas = sapiens_technology_torch.zeros([input_ids.shape[0], 1], device=input_ids.device, dtype=input_ids.dtype)
            return position_ids, mrope_position_deltas
    def _update_model_kwargs_for_generation(self, outputs: ModelOutput, model_kwargs: Dict[str, Any], is_encoder_decoder: bool = False,
    num_new_tokens: int = 1) -> Dict[str, Any]:
        model_kwargs = super()._update_model_kwargs_for_generation(outputs=outputs, model_kwargs=model_kwargs, is_encoder_decoder=is_encoder_decoder, num_new_tokens=num_new_tokens)
        if getattr(outputs, "rope_deltas", None) is not None: model_kwargs["rope_deltas"] = outputs.rope_deltas
        return model_kwargs
    @add_start_docstrings_to_model_forward(SAPIENS_INPUTS_DOCSTRING)
    def forward(self, input_ids: sapiens_technology_torch.LongTensor = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None,
    past_key_values: Optional[List[sapiens_technology_torch.FloatTensor]] = None, inputs_embeds: Optional[sapiens_technology_torch.FloatTensor] = None, labels: Optional[sapiens_technology_torch.LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    pixel_values: Optional[sapiens_technology_torch.Tensor] = None, pixel_values_videos: Optional[sapiens_technology_torch.FloatTensor] = None, image_grid_thw: Optional[sapiens_technology_torch.LongTensor] = None,
    video_grid_thw: Optional[sapiens_technology_torch.LongTensor] = None, rope_deltas: Optional[sapiens_technology_torch.LongTensor] = None) -> Union[Tuple, SapiensVisionCausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is None:
            inputs_embeds = self.model.embed_tokens(input_ids)
            if pixel_values is not None:
                image_embeds = self.visual(pixel_values.type(self.visual.get_dtype()), grid_thw=image_grid_thw)
                image_embeds = image_embeds.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter((input_ids == self.config.image_token_id).unsqueeze(-1).expand_as(inputs_embeds), image_embeds)
            if pixel_values_videos is not None:
                video_embeds = self.visual(pixel_values_videos.type(self.visual.get_dtype()), grid_thw=video_grid_thw).to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter((input_ids == self.config.video_token_id).unsqueeze(-1).expand_as(inputs_embeds), video_embeds)
            if attention_mask is not None: attention_mask = attention_mask.to(inputs_embeds.device)
        outputs = self.model(input_ids=None, position_ids=position_ids, attention_mask=attention_mask, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits, loss = self.lm_head(outputs[0]).float(), None
        if labels is not None:
            shift_logits, shift_labels = logits[..., :-1, :].contiguous(), labels[..., 1:].contiguous()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            loss = CrossEntropyLoss()(shift_logits, shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return SapiensVisionCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions, rope_deltas=rope_deltas)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, cache_position=None, position_ids=None, use_cache=True,
    pixel_values=None, pixel_values_videos=None, image_grid_thw=None, video_grid_thw=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        rope_deltas = kwargs.get("rope_deltas", None)
        if attention_mask is not None and position_ids is None:
            if cache_position is None or (cache_position is not None and cache_position[0] == 0): position_ids, rope_deltas = self.get_rope_index(input_ids, image_grid_thw, video_grid_thw, attention_mask)
            else:
                batch_size, seq_length = input_ids.shape
                position_ids = sapiens_technology_torch.arange(seq_length, device=input_ids.device).view(1, -1).expand(batch_size, -1).add((cache_position[0] + rope_deltas if cache_position is not None and rope_deltas is not None else 0))
                position_ids = position_ids.unsqueeze(0).expand(3, -1, -1)
        if cache_position[0] != 0: pixel_values, pixel_values_videos = None, None
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids, "inputs_embeds": None}
        if isinstance(past_key_values, StaticCache) and attention_mask.ndim == 2:
            if model_inputs["inputs_embeds"] is not None:
                batch_size, sequence_length, _ = inputs_embeds.shape
                device = inputs_embeds.device
            else:
                batch_size, sequence_length = input_ids.shape
                device = input_ids.device
            dtype = self.lm_head.weight.dtype
            attention_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=past_key_values.get_max_length(),
            dtype=dtype, device=device, min_dtype=sapiens_technology_torch.finfo(dtype).min, cache_position=cache_position, batch_size=batch_size)
        model_inputs.update({"position_ids": position_ids, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask, "pixel_values": pixel_values,
        "pixel_values_videos": pixel_values_videos, "image_grid_thw": image_grid_thw, "video_grid_thw": video_grid_thw, "rope_deltas": rope_deltas})
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
