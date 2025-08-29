"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Any, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...cache_utils import Cache, DynamicCache, StaticCache
from ...generation import GenerationMixin
from ...modeling_attn_mask_utils import AttentionMaskConverter
from ...modeling_outputs import MoeCausalLMOutputWithPast, MoeModelOutputWithPast
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, logging, replace_return_docstrings)
from .configuration_dbrx import DbrxConfig
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "DbrxConfig"
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: torch.Tensor, sequence_length: int, target_length: int, dtype: torch.dtype, device: torch.device, min_dtype: float, cache_position: torch.Tensor, batch_size: int):
    if attention_mask is not None and attention_mask.dim() == 4: causal_mask = attention_mask
    else:
        causal_mask = torch.full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != 1: causal_mask = torch.triu(causal_mask, diagonal=1)
        causal_mask *= torch.arange(target_length, device=device) > cache_position.reshape(-1, 1)
        causal_mask = causal_mask[None, None, :, :].expand(batch_size, 1, -1, -1)
        if attention_mask is not None:
            causal_mask = causal_mask.clone()
            mask_length = attention_mask.shape[-1]
            padding_mask = causal_mask[:, :, :, :mask_length] + attention_mask[:, None, None, :]
            padding_mask = padding_mask == 0
            causal_mask[:, :, :, :mask_length] = causal_mask[:, :, :, :mask_length].masked_fill(padding_mask, min_dtype)
    return causal_mask
class DbrxRotaryEmbedding(nn.Module):
    def __init__(self, dim, max_position_embeddings=2048, base=10000, device=None):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2, dtype=torch.int64).float() / self.dim))
        self.register_buffer("inv_freq", tensor=inv_freq, persistent=False)
    @torch.no_grad()
    def forward(self, x, position_ids, seq_len=None):
        self.inv_freq.to(x.device)
        inv_freq_expanded = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1)
        position_ids_expanded = position_ids[:, None, :].float()
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos()
            sin = emb.sin()
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)
def rotate_half(x):
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
def load_balancing_loss_func(gate_logits: torch.Tensor, num_experts: int, top_k: int, attention_mask: Optional[torch.Tensor]) -> torch.Tensor:
    if gate_logits is None or not isinstance(gate_logits, tuple): return torch.tensor(0.0)
    if isinstance(gate_logits, tuple):
        compute_device = gate_logits[0].device
        concatenated_gate_logits = torch.cat([layer_gate.to(compute_device) for layer_gate in gate_logits], dim=0)
    routing_weights = torch.nn.functional.softmax(concatenated_gate_logits, dim=-1)
    _, selected_experts = torch.topk(routing_weights, top_k, dim=-1)
    expert_mask = torch.nn.functional.one_hot(selected_experts, num_experts)
    if attention_mask is None:
        tokens_per_expert = torch.mean(expert_mask.float(), dim=0)
        router_prob_per_expert = torch.mean(routing_weights, dim=0)
    else:
        batch_size, sequence_length = attention_mask.shape
        num_hidden_layers = concatenated_gate_logits.shape[0] // (batch_size * sequence_length)
        expert_attention_mask = (attention_mask[None, :, :, None, None].expand((num_hidden_layers, batch_size, sequence_length, top_k, num_experts)).reshape(-1, top_k, num_experts).to(compute_device))
        tokens_per_expert = torch.sum(expert_mask.float() * expert_attention_mask, dim=0) / torch.sum(expert_attention_mask, dim=0)
        router_per_expert_attention_mask = (attention_mask[None, :, :, None].expand((num_hidden_layers, batch_size, sequence_length, num_experts)).reshape(-1, num_experts).to(compute_device))
        router_prob_per_expert = torch.sum(routing_weights * router_per_expert_attention_mask, dim=0) / torch.sum(router_per_expert_attention_mask, dim=0)
    overall_loss = torch.sum(tokens_per_expert * router_prob_per_expert.unsqueeze(0))
    return overall_loss * num_experts
class DbrxAttention(nn.Module):
    def __init__(self, config: DbrxConfig, block_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.hidden_size = config.d_model
        self.num_heads = config.n_heads
        self.head_dim = self.hidden_size // self.num_heads
        self.max_position_embeddings = config.max_seq_len
        self.block_idx = block_idx
        if block_idx is None: logger.warning_once(f"Instantiating {self.__class__.__name__} without passing a `block_idx` is not recommended and will lead to errors during the forward call if caching is used. Please make sure to provide a `block_idx` when creating this class.")
        attn_config = config.attn_config
        self.attn_pdrop = attn_config.attn_pdrop
        self.clip_qkv = attn_config.clip_qkv
        self.num_key_value_heads = attn_config.kv_n_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.rope_theta = attn_config.rope_theta
        self.is_causal = True
        self.Wqkv = nn.Linear(self.hidden_size, self.hidden_size + 2 * self.num_key_value_heads * self.head_dim, bias=False)
        self.out_proj = nn.Linear(self.hidden_size, self.hidden_size, bias=False)
        self.rotary_emb = DbrxRotaryEmbedding(self.head_dim, max_position_embeddings=self.max_position_embeddings, base=self.rope_theta)
    def forward(self, hidden_states: torch.Tensor, position_ids: torch.LongTensor, attention_mask: Optional[torch.Tensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None, **kwargs: Any) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Cache]]:
        bsz, q_len, _ = hidden_states.size()
        qkv_states = self.Wqkv(hidden_states)
        min_val = -self.clip_qkv if self.clip_qkv is not None else None
        max_val = self.clip_qkv
        qkv_states = qkv_states.clamp(min=min_val, max=max_val)
        query_states, key_states, value_states = qkv_states.split([self.hidden_size, self.num_key_value_heads * self.head_dim, self.num_key_value_heads * self.head_dim], dim=2)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.block_idx, cache_kwargs)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.attn_pdrop, training=self.training)
        attn_output = torch.matmul(attn_weights, value_states)
        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is" + f" {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(bsz, q_len, self.hidden_size)
        attn_output = self.out_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class DbrxFlashAttention2(DbrxAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None, **kwargs: Any) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if isinstance(past_key_value, StaticCache): raise ValueError("`static` cache implementation is not compatible with `attn_implementation==flash_attention_2` make sure to use `sdpa` in the mean time.")
        logger.info("Implicitly setting `output_attentions` to False as it is not supported in Flash Attention.")
        output_attentions = False
        bsz, q_len, _ = hidden_states.size()
        qkv_states = self.Wqkv(hidden_states)
        if self.clip_qkv is not None: qkv_states = qkv_states.clamp(min=-self.clip_qkv, max=self.clip_qkv)
        query_states, key_states, value_states = qkv_states.split([self.hidden_size, self.num_key_value_heads * self.head_dim, self.num_key_value_heads * self.head_dim], dim=2)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.block_idx, cache_kwargs)
        query_states = query_states.transpose(1, 2)
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)
        dropout_rate = self.attn_pdrop if self.training else 0.0
        input_dtype = query_states.dtype
        if input_dtype == torch.float32:
            if torch.is_autocast_enabled(): target_dtype = torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = query_states.dtype
            logger.warning_once(f"The input hidden states seems to be silently casted in float32, this might be related to the fact you have upcasted embedding or layer norm layers in float32. We will cast back the input in {target_dtype}.")
            query_states = query_states.to(target_dtype)
            key_states = key_states.to(target_dtype)
            value_states = value_states.to(target_dtype)
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, position_ids=position_ids, dropout=dropout_rate,
        is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        attn_output = attn_output.reshape(bsz, q_len, self.hidden_size).contiguous()
        attn_output = self.out_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class DbrxSdpaAttention(DbrxAttention):
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if output_attentions:
            logger.warning_once("DbrxModel is using DbrxSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True`. Falling back to the manual attention implementation, "+'but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position)
        bsz, q_len, _ = hidden_states.size()
        qkv_states = self.Wqkv(hidden_states)
        if self.clip_qkv is not None: qkv_states = qkv_states.clamp(min=-self.clip_qkv, max=self.clip_qkv)
        query_states, key_states, value_states = qkv_states.split([self.hidden_size, self.num_key_value_heads * self.head_dim, self.num_key_value_heads * self.head_dim], dim=2)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rotary_emb(value_states, position_ids, seq_len=None)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, None)
        if past_key_value is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_value.update(key_states, value_states, self.block_idx, cache_kwargs)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        causal_mask = attention_mask
        if attention_mask is not None: causal_mask = causal_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and causal_mask is not None:
            query_states = query_states.contiguous()
            key_states = key_states.contiguous()
            value_states = value_states.contiguous()
        is_causal = True if causal_mask is None and q_len > 1 else False
        attn_output = torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.attn_pdrop if self.training else 0.0, is_causal=is_causal)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(bsz, q_len, -1)
        attn_output = self.out_proj(attn_output)
        return attn_output, None, past_key_value
DBRX_ATTENTION_CLASSES = {"eager": DbrxAttention, "flash_attention_2": DbrxFlashAttention2, "sdpa": DbrxSdpaAttention}
class DbrxNormAttentionNorm(nn.Module):
    def __init__(self, config: DbrxConfig, block_idx: Optional[int] = None):
        super().__init__()
        self.block_idx = block_idx
        self.resid_pdrop = config.resid_pdrop
        self.norm_1 = nn.LayerNorm(config.d_model, bias=False)
        self.attn = DBRX_ATTENTION_CLASSES[config._attn_implementation](config=config, block_idx=block_idx)
        self.norm_2 = nn.LayerNorm(config.d_model, bias=False)
    def forward(self, hidden_states: torch.Tensor, position_ids: torch.LongTensor, attention_mask: Optional[torch.Tensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[torch.LongTensor] = None, **kwargs: Any) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor], Optional[Cache]]:
        residual_states = hidden_states
        hidden_states = self.norm_1(hidden_states).to(hidden_states.dtype)
        hidden_states, attn_weights, past_key_value = self.attn(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value,
        output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, **kwargs)
        hidden_states = nn.functional.dropout(hidden_states, p=self.resid_pdrop, training=self.training)
        hidden_states = hidden_states + residual_states
        residual_states = hidden_states
        hidden_states = self.norm_2(hidden_states).to(hidden_states.dtype)
        return residual_states, hidden_states, attn_weights, past_key_value
class DbrxRouter(nn.Module):
    def __init__(self, hidden_size: int, moe_num_experts: int, moe_top_k: int, moe_jitter_eps: Optional[float], moe_normalize_expert_weights: Optional[float]):
        super().__init__()
        self.hidden_size = hidden_size
        self.moe_num_experts = moe_num_experts
        self.moe_top_k = moe_top_k
        self.moe_jitter_eps = moe_jitter_eps
        self.moe_normalize_expert_weights = moe_normalize_expert_weights
        self.layer = nn.Linear(self.hidden_size, self.moe_num_experts, bias=False)
    def forward(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.LongTensor]:
        if self.training and self.moe_jitter_eps is not None: hidden_states *= torch.empty_like(hidden_states).uniform_(1.0 - self.moe_jitter_eps, 1.0 + self.moe_jitter_eps)
        hidden_states = hidden_states.view(-1, hidden_states.shape[-1])
        weights = self.layer(hidden_states).softmax(dim=-1, dtype=torch.float32)
        top_weights, top_experts = torch.topk(weights, self.moe_top_k, dim=-1)
        top_weights_scale = (torch.norm(top_weights, p=self.moe_normalize_expert_weights, dim=-1, keepdim=True) if self.moe_normalize_expert_weights is not None else 1.0)
        top_weights = top_weights / top_weights_scale
        weights = weights.to(hidden_states.dtype)
        top_weights = top_weights.to(hidden_states.dtype)
        return weights, top_weights, top_experts
class DbrxExpertGLU(nn.Module):
    def __init__(self, hidden_size: int, ffn_hidden_size: int, moe_num_experts: int, ffn_act_fn: dict):
        super().__init__()
        self.hidden_size = hidden_size
        self.ffn_hidden_size = ffn_hidden_size
        self.moe_num_experts = moe_num_experts
        self.w1 = nn.Parameter(torch.empty(moe_num_experts * ffn_hidden_size, hidden_size))
        self.v1 = nn.Parameter(torch.empty(moe_num_experts * ffn_hidden_size, hidden_size))
        self.w2 = nn.Parameter(torch.empty(moe_num_experts * ffn_hidden_size, hidden_size))
        act_fn_name = ffn_act_fn.get("name", "silu")
        self.activation_fn = ACT2FN[act_fn_name]
    def forward(self, x: torch.Tensor, expert_w1: torch.Tensor, expert_v1: torch.Tensor, expert_w2: torch.Tensor) -> torch.Tensor:
        gate_proj = x.matmul(expert_w1.t())
        up_proj = x.matmul(expert_v1.t())
        gate_proj = self.activation_fn(gate_proj)
        intermediate_states = gate_proj * up_proj
        down_proj = intermediate_states.matmul(expert_w2)
        return down_proj
class DbrxExperts(nn.Module):
    def __init__(self, hidden_size: int, ffn_hidden_size: int, moe_num_experts: int, ffn_act_fn: dict):
        super().__init__()
        self.moe_num_experts = moe_num_experts
        self.mlp = DbrxExpertGLU(hidden_size=hidden_size, ffn_hidden_size=ffn_hidden_size, moe_num_experts=moe_num_experts, ffn_act_fn=ffn_act_fn)
    def forward(self, x: torch.Tensor, weights: torch.Tensor, top_weights: torch.Tensor, top_experts: torch.LongTensor) -> torch.Tensor:
        bsz, q_len, hidden_size = x.shape
        x = x.view(-1, hidden_size)
        out = torch.zeros_like(x)
        expert_mask = nn.functional.one_hot(top_experts, num_classes=self.moe_num_experts).permute(2, 1, 0)
        w1_chunked = self.mlp.w1.view(self.mlp.moe_num_experts, self.mlp.ffn_hidden_size, self.mlp.hidden_size).chunk(self.moe_num_experts, dim=0)
        v1_chunked = self.mlp.v1.view(self.mlp.moe_num_experts, self.mlp.ffn_hidden_size, self.mlp.hidden_size).chunk(self.moe_num_experts, dim=0)
        w2_chunked = self.mlp.w2.view(self.mlp.moe_num_experts, self.mlp.ffn_hidden_size, self.mlp.hidden_size).chunk(self.moe_num_experts, dim=0)
        w1_chunked = [w1.squeeze(dim=0) for w1 in w1_chunked]
        v1_chunked = [v1.squeeze(dim=0) for v1 in v1_chunked]
        w2_chunked = [w2.squeeze(dim=0) for w2 in w2_chunked]
        for expert_idx in range(0, self.moe_num_experts):
            topk_idx, token_idx = torch.where(expert_mask[expert_idx])
            if token_idx.shape[0] == 0: continue
            token_list = token_idx
            topk_list = topk_idx
            expert_tokens = x[None, token_list].reshape(-1, hidden_size)
            expert_out = (self.mlp(expert_tokens, w1_chunked[expert_idx], v1_chunked[expert_idx], w2_chunked[expert_idx]) * top_weights[token_list, topk_list, None])
            out.index_add_(0, token_idx, expert_out)
        out = out.reshape(bsz, q_len, hidden_size)
        return out
class DbrxFFN(nn.Module):
    def __init__(self, config: DbrxConfig):
        super().__init__()
        ffn_config = config.ffn_config
        self.router = DbrxRouter(hidden_size=config.d_model, moe_num_experts=ffn_config.moe_num_experts, moe_top_k=ffn_config.moe_top_k, moe_jitter_eps=ffn_config.moe_jitter_eps, moe_normalize_expert_weights=ffn_config.moe_normalize_expert_weights)
        self.experts = DbrxExperts(hidden_size=config.d_model, ffn_hidden_size=ffn_config.ffn_hidden_size, moe_num_experts=ffn_config.moe_num_experts, ffn_act_fn=ffn_config.ffn_act_fn)
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        weights, top_weights, top_experts = self.router(x)
        out = self.experts(x, weights, top_weights, top_experts)
        return out, weights
class DbrxBlock(nn.Module):
    def __init__(self, config: DbrxConfig, block_idx: int):
        super().__init__()
        self.hidden_size = config.d_model
        self.resid_pdrop = config.resid_pdrop
        self.block_idx = block_idx
        self.norm_attn_norm = DbrxNormAttentionNorm(config=config, block_idx=block_idx)
        self.ffn = DbrxFFN(config=config)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: torch.LongTensor = None, past_key_value: Optional[Cache] = None,
    output_attentions: Optional[bool] = False, output_router_logits: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[torch.LongTensor] = None,
    **kwargs: Any) -> Union[Tuple[torch.Tensor], Tuple[torch.Tensor, Optional[torch.Tensor]], Tuple[torch.Tensor, Optional[Cache]], Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Cache]],
    Tuple[torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]], Tuple[torch.Tensor, Optional[Cache], Optional[torch.Tensor]], Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Cache], Optional[torch.Tensor]]]:
        resid_states, hidden_states, self_attn_weights, present_key_value = self.norm_attn_norm(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions,
        use_cache=use_cache, cache_position=cache_position, **kwargs)
        hidden_states, router_logits = self.ffn(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.resid_pdrop, training=self.training)
        hidden_states = resid_states + hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        if output_router_logits: outputs += (router_logits,)
        return outputs
DBRX_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`DbrxConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@add_start_docstrings("The bare DBRX Model outputting raw hidden-states without any specific head on top.", DBRX_START_DOCSTRING)
class DbrxPreTrainedModel(PreTrainedModel):
    config_class = DbrxConfig
    base_model_prefix = "transformer"
    supports_gradient_checkpointing = True
    _no_split_modules = ["DbrxBlock"]
    _skip_keys_device_placement = ["past_key_values"]
    _supports_flash_attn_2 = True
    _supports_sdpa = True
    _supports_cache_class = True
    _supports_quantized_cache = True
    _supports_static_cache = True
    def _init_weights(self, module: nn.Module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, DbrxExpertGLU):
            module.w1.data.normal_(mean=0.0, std=std)
            module.v1.data.normal_(mean=0.0, std=std)
            module.w2.data.normal_(mean=0.0, std=std)
DBRX_INPUTS_DOCSTRING = r"""
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
            config.n_positions - 1]`.
            [What are position IDs?](../glossary#position-ids)
        past_key_values (`Cache` or `tuple(tuple(torch.FloatTensor))`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used to speed up sequential decoding. This typically consists in the `past_key_values`
            returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.
            Two formats are allowed:
            - a [`~cache_utils.Cache`] instance;
            - Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of
            shape `(batch_size, num_heads, sequence_length, embed_size_per_head)`. This is also known as the legacy
            cache format.
            The model will output the same cache format that is fed as input. If no `past_key_values` are passed, the
            legacy cache format will be returned.
            If `past_key_values` are used, the user can optionally input only the last `input_ids` (those that don't
            have their past key value states given to this model) of shape `(batch_size, 1)` instead of all `input_ids`
            of shape `(batch_size, sequence_length)`.
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
        output_router_logits (`bool`, *optional*):
            Whether or not to return the logits of all the routers. They are useful for computing the router loss, and
            should not be returned during inference.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
@add_start_docstrings("The bare DBRX Model outputting raw hidden-states without any specific head on top.", DBRX_START_DOCSTRING)
class DbrxModel(DbrxPreTrainedModel):
    def __init__(self, config: DbrxConfig):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        self.emb_pdrop = config.emb_pdrop
        self.wte = nn.Embedding(config.vocab_size, config.d_model, self.padding_idx)
        self.blocks = nn.ModuleList([DbrxBlock(config, block_idx) for block_idx in range(config.n_layers)])
        self.norm_f = nn.LayerNorm(config.d_model, bias=False)
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self) -> nn.Embedding: return self.wte
    def set_input_embeddings(self, value: nn.Embedding): self.wte = value
    @add_start_docstrings_to_model_forward(DBRX_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_values: Optional[Cache] = None, inputs_embeds: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, output_router_logits: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None) -> Union[Tuple, MoeModelOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_router_logits = (output_router_logits if output_router_logits is not None else self.config.output_router_logits)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training and use_cache:
            logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.")
            use_cache = False
        if inputs_embeds is None: inputs_embeds = self.wte(input_ids)
        inputs_embeds = nn.functional.dropout(inputs_embeds, p=self.emb_pdrop, training=self.training)
        return_legacy_cache = False
        if use_cache and not isinstance(past_key_values, Cache):
            return_legacy_cache = True
            if past_key_values is None: past_key_values = DynamicCache()
            else:
                past_key_values = DynamicCache.from_legacy_cache(past_key_values)
                logger.warning_once("We detected that you are passing `past_key_values` as a tuple of tuples. This is deprecated and will be removed in v1.0.")
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = torch.arange(past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        causal_mask = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions)
        hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_router_logits = () if output_router_logits else None
        next_decoder_cache = None
        for block in self.blocks:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training: block_outputs = self._gradient_checkpointing_func(block.__call__, hidden_states, causal_mask, position_ids, past_key_values, output_attentions, output_router_logits, use_cache, cache_position)
            else: block_outputs = block(hidden_states, attention_mask=causal_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions, output_router_logits=output_router_logits, use_cache=use_cache, cache_position=cache_position)
            hidden_states = block_outputs[0]
            if use_cache: next_decoder_cache = block_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (block_outputs[1],)
            if output_router_logits: all_router_logits += (block_outputs[-1],)
        hidden_states = self.norm_f(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if return_legacy_cache: next_cache = next_cache.to_legacy_cache()
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns, all_router_logits] if v is not None)
        return MoeModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns, router_logits=all_router_logits)
    def _update_causal_mask(self, attention_mask: torch.Tensor, input_tensor: torch.Tensor, cache_position: torch.Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
        using_static_cache = isinstance(past_key_values, StaticCache)
        if self.config._attn_implementation == "sdpa" and not using_static_cache and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype = torch.finfo(dtype).min
        sequence_length = input_tensor.shape[1]
        if using_static_cache: target_length = past_key_values.get_max_length()
        else: target_length = (attention_mask.shape[-1] if isinstance(attention_mask, torch.Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
@add_start_docstrings("The DBRX Model transformer for causal language modeling.", DBRX_START_DOCSTRING)
class DbrxForCausalLM(DbrxPreTrainedModel, GenerationMixin):
    def __init__(self, config: DbrxConfig):
        super().__init__(config)
        self.transformer = DbrxModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.moe_loss_weight = config.ffn_config.moe_loss_weight
        self.num_experts = config.ffn_config.moe_num_experts
        self.num_experts_per_tok = config.ffn_config.moe_top_k
        self.post_init()
    def get_input_embeddings(self) -> nn.Embedding: return self.transformer.get_input_embeddings()
    def set_input_embeddings(self, value: nn.Embedding): self.transformer.set_input_embeddings(value)
    def get_output_embeddings(self) -> nn.Linear: return self.lm_head
    def set_output_embeddings(self, new_embeddings: nn.Linear): self.lm_head = new_embeddings
    def set_decoder(self, decoder: DbrxModel): self.transformer = decoder
    def get_decoder(self) -> DbrxModel: return self.transformer
    @add_start_docstrings_to_model_forward(DBRX_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[Cache] = None,
    inputs_embeds: Optional[torch.Tensor] = None, labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    output_router_logits: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, MoeCausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_router_logits = (output_router_logits if output_router_logits is not None else self.config.output_router_logits)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict, cache_position=cache_position)
        hidden_states = outputs[0]
        logits = self.lm_head(hidden_states[:, -num_logits_to_keep:, :])
        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            shift_labels = shift_labels.view(-1)
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)
        aux_loss = None
        if output_router_logits:
            aux_loss = load_balancing_loss_func(outputs.router_logits if return_dict else outputs[-1], self.num_experts, self.num_experts_per_tok, attention_mask)
            if labels is not None and loss is not None: loss += self.moe_loss_weight * aux_loss.to(loss.device)
        if not return_dict:
            output = (logits,) + outputs[1:]
            if output_router_logits: output = (aux_loss,) + output
            return (loss,) + output if loss is not None else output
        return MoeCausalLMOutputWithPast(loss=loss, aux_loss=aux_loss, logits=logits, past_key_values=outputs.past_key_values,
        hidden_states=outputs.hidden_states, attentions=outputs.attentions, router_logits=outputs.router_logits)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, cache_position=None, position_ids=None,
    use_cache=True, num_logits_to_keep=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -input_ids.shape[1] :]
                position_ids = position_ids.clone(memory_format=torch.contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=torch.contiguous_format), "inputs_embeds": None}
        if isinstance(past_key_values, StaticCache) and attention_mask.ndim == 2:
            if model_inputs["inputs_embeds"] is not None:
                batch_size, sequence_length, _ = model_inputs["inputs_embeds"].shape
                device = model_inputs["inputs_embeds"].device
            else:
                batch_size, sequence_length = model_inputs["input_ids"].shape
                device = model_inputs["input_ids"].device
            dtype = self.lm_head.weight.dtype
            min_dtype = torch.finfo(dtype).min
            attention_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=past_key_values.get_max_length(),
            dtype=dtype, device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=batch_size)
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
