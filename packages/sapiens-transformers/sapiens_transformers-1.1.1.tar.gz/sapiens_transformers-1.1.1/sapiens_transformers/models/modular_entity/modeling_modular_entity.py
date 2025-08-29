"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch import nn as entity_neural_network
import torch as sapiens_technology_torch
from .configuration_modular_entity import ModularEntityVisionConfig, ModularEntityTextConfig, ModularEntityConfig
from typing import Optional, Union, Tuple, List
from math import sqrt, pi
import torch.nn.functional as Functional
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPast, CausalLMOutputWithPast
from ...cache_utils import Cache
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward)
class ModularEntityVisionMLP(entity_neural_network.Module):
    def __init__(self, config):
        super().__init__()
        from ...activations import ACT2FN
        self.config, self.activation_fn = config, ACT2FN[config.hidden_act]
        self.fc1, self.fc2 = entity_neural_network.Linear(config.hidden_size, config.intermediate_size), entity_neural_network.Linear(config.intermediate_size, config.hidden_size)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor: return self.fc2(self.activation_fn(self.fc1(hidden_states)))
class ModularEntityVisionAttention(entity_neural_network.Module):
    def __init__(self, config: ModularEntityVisionConfig):
        super().__init__()
        self.embed_dim, self.num_heads, self.head_dim = config.hidden_size, config.attention_heads, config.hidden_size // config.attention_heads
        self.q_proj, self.k_proj = entity_neural_network.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False)
        self.v_proj, self.o_proj = entity_neural_network.Linear(self.embed_dim, self.num_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.num_heads * self.head_dim, self.embed_dim, bias=False)
    def forward(self, hidden_state: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, output_attentions: bool = None) -> sapiens_technology_torch.Tensor:
        query, key, value = self.q_proj(hidden_state), self.k_proj(hidden_state), self.v_proj(hidden_state)
        batch_size, q_seq_len, _ = query.shape
        _, kv_seq_len, _ = key.shape
        query, key = query.view(batch_size, q_seq_len, self.num_heads, self.head_dim).transpose(1, 2), key.view(batch_size, kv_seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value, attn_weights = value.view(batch_size, kv_seq_len, self.num_heads, self.head_dim).transpose(1, 2), sapiens_technology_torch.matmul(query, key.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key.shape[-2]]
        attn_weights = entity_neural_network.functional.softmax(attn_weights, dim=-1, dtype=sapiens_technology_torch.float32).to(query.dtype)
        output = self.o_proj(sapiens_technology_torch.matmul(attn_weights, value).transpose(1, 2).contiguous().reshape(batch_size, q_seq_len, -1))
        if not output_attentions: attn_weights = None
        return output, attn_weights
class ModularEntityVisionSdpaAttention(ModularEntityVisionAttention):
    def forward(self, hidden_state: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, output_attentions: bool = None) -> sapiens_technology_torch.Tensor:
        if output_attentions: return super().forward(hidden_state=hidden_state, attention_mask=attention_mask, output_attentions=output_attentions)
        query, key, value = self.q_proj(hidden_state), self.k_proj(hidden_state), self.v_proj(hidden_state)
        batch_size, q_seq_len, _ = query.shape
        _, kv_seq_len, _ = key.shape
        query, key = query.view(batch_size, q_seq_len, self.num_heads, self.head_dim), key.view(batch_size, kv_seq_len, self.num_heads, self.head_dim)
        value, query = value.view(batch_size, kv_seq_len, self.num_heads, self.head_dim), query.transpose(1, 2)
        key, value = key.transpose(1, 2), value.transpose(1, 2)
        return self.o_proj(Functional.scaled_dot_product_attention(query, key, value, attn_mask=attention_mask).transpose(1, 2).contiguous().reshape(batch_size, q_seq_len, -1)), None
MODULAR_ENTITY_VISION_ATTENTION_CLASSES = {"eager": ModularEntityVisionAttention, "sdpa": ModularEntityVisionSdpaAttention}
class ModularEntityVisionEncoderLayer(entity_neural_network.Module):
    def __init__(self, config: ModularEntityVisionConfig, is_gated: bool = False):
        super().__init__()
        self.hidden_size, self.num_attention_heads, self.is_gated = config.hidden_size, config.attention_heads, is_gated
        self.intermediate_size, self.self_attn = config.intermediate_size, MODULAR_ENTITY_VISION_ATTENTION_CLASSES[config._attn_implementation](config)
        self.mlp, self.input_layernorm, self.post_attention_layernorm = ModularEntityVisionMLP(config), entity_neural_network.LayerNorm(self.hidden_size, eps=config.norm_eps), entity_neural_network.LayerNorm(self.hidden_size, eps=config.norm_eps)
        if is_gated: self.gate_attn, self.gate_ffn = entity_neural_network.Parameter(sapiens_technology_torch.ones(1) * pi / 4), entity_neural_network.Parameter(sapiens_technology_torch.ones(1) * pi / 4)
    def forward(self, hidden_state: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, output_attentions: bool = None):
        residual = hidden_state
        hidden_state = self.input_layernorm(hidden_state)
        hidden_state, attn_weights = self.self_attn(hidden_state, attention_mask=attention_mask)
        if self.is_gated: hidden_state = self.gate_attn.tanh() * hidden_state
        hidden_state = residual + hidden_state
        residual = hidden_state
        hidden_state = self.mlp(self.post_attention_layernorm(hidden_state))
        if self.is_gated: hidden_state = self.gate_ffn.tanh() * hidden_state
        outputs = (residual + hidden_state,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class ModularEntityVisionEncoder(entity_neural_network.Module):
    def __init__(self, config: ModularEntityVisionConfig, num_layers=32, is_gated=False):
        super().__init__()
        self.config, self.layers = config, entity_neural_network.ModuleList([ModularEntityVisionEncoderLayer(config, is_gated) for _ in range(num_layers)])
        self.gradient_checkpointing, self.config = False, config
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states, all_attentions = () if output_hidden_states else None, () if output_attentions else None
        for encoder_layer in self.layers:
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask, output_attentions)
            else: layer_outputs = encoder_layer(hidden_state=hidden_states, attention_mask=attention_mask, output_attentions=output_attentions)
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
            hidden_states = layer_outputs[0]
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class ModularEntityTextRMSNorm(entity_neural_network.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight, self.variance_epsilon = entity_neural_network.Parameter(sapiens_technology_torch.ones(hidden_size)), eps
    def forward(self, hidden_states):
        hidden_states = hidden_states.to(sapiens_technology_torch.float32)
        hidden_states = hidden_states * sapiens_technology_torch.rsqrt(hidden_states.pow(2).mean(-1, keepdim=True) + self.variance_epsilon)
        return self.weight * hidden_states.to(hidden_states.dtype)
    def extra_repr(self): return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"
class ModularEntityTextCrossAttention(entity_neural_network.Module):
    def __init__(self, config: Optional[ModularEntityTextConfig] = None, layer_idx: Optional[int] = None):
        super().__init__()
        self.config, self.num_heads = config, self.config.num_attention_heads
        self.num_key_value_heads = self.config.num_key_value_heads
        self.dropout, self.hidden_size, self.head_dim = config.dropout, config.hidden_size, config.hidden_size // self.num_heads
        self.layer_idx, self.num_key_value_groups = layer_idx, self.num_heads // self.num_key_value_heads
        self.q_proj, self.k_proj = entity_neural_network.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj, self.o_proj = entity_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        self.q_norm, self.k_norm = ModularEntityTextRMSNorm(self.head_dim, eps=config.rms_norm_eps), ModularEntityTextRMSNorm(self.head_dim, eps=config.rms_norm_eps)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cross_attention_states: Optional[sapiens_technology_torch.Tensor] = None, past_key_value: Optional[Cache] = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None,
    output_attentions: bool = False, use_cache: bool = None, cache_position: Optional[sapiens_technology_torch.LongTensor] = None) -> Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor], Optional[Tuple[sapiens_technology_torch.Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_norm(self.q_proj(hidden_states).view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2))
        if cross_attention_states is not None:
            key_states, value_states, key_states = self.k_proj(cross_attention_states), self.v_proj(cross_attention_states), key_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            value_states, key_states = value_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2), repeat_kv(key_states, self.num_key_value_groups)
            value_states, key_states = repeat_kv(value_states, self.num_key_value_groups), self.k_norm(key_states)
            if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        elif cache_position[0] != 0: key_states, value_states = (past_key_value.key_cache[self.layer_idx], past_key_value.value_cache[self.layer_idx])
        else: raise ValueError("Cross attention layer can't find neither `cross_attn_states` nor cached values for key/values!")
        attn_weights = sapiens_technology_torch.matmul(query_states, key_states.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights = entity_neural_network.functional.dropout(entity_neural_network.functional.softmax(attn_weights, dim=-1, dtype=sapiens_technology_torch.float32).to(query_states.dtype), p=self.dropout, training=self.training)
        if not output_attentions: attn_weights = None
        return self.o_proj(sapiens_technology_torch.matmul(attn_weights, value_states).transpose(1, 2).contiguous().reshape(bsz, q_len, -1)), attn_weights, past_key_value
class ModularEntityTextCrossSdpaAttention(ModularEntityTextCrossAttention):
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cross_attention_states: Optional[sapiens_technology_torch.Tensor] = None, past_key_value: Optional[Cache] = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None,
    output_attentions: bool = False, use_cache: bool = None, cache_position: Optional[sapiens_technology_torch.LongTensor] = None) -> Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor], Optional[Tuple[sapiens_technology_torch.Tensor]]]:
        if output_attentions:
            return super().forward(hidden_states=hidden_states, cross_attention_states=cross_attention_states, attention_mask=attention_mask, past_key_value=past_key_value,
            output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position)
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_norm(self.q_proj(hidden_states).view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2))
        if cross_attention_states is not None:
            key_states, value_states = self.k_proj(cross_attention_states), self.v_proj(cross_attention_states)
            key_states, value_states = key_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, -1, self.num_key_value_heads, self.head_dim).transpose(1, 2)
            if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        elif cache_position[0] != 0: key_states, value_states = (past_key_value.key_cache[self.layer_idx], past_key_value.value_cache[self.layer_idx])
        else: raise ValueError("Cross attention layer can't find neither `cross_attn_states` nor cached values for key/values!")
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        key_states = self.k_norm(key_states)
        if query_states.device.type == "cuda" and attention_mask is not None: query_states, key_states, value_states = query_states.contiguous(), key_states.contiguous(), value_states.contiguous()
        is_causal = True if attention_mask is None and q_len > 1 else False
        return self.o_proj(sapiens_technology_torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=attention_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal).transpose(1, 2).contiguous().reshape(bsz, q_len, -1)), None, past_key_value
def rotate_half(x): return sapiens_technology_torch.cat((-x[..., x.shape[-1] // 2 :], x[..., : x.shape[-1] // 2]), dim=-1)
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    cos, sin = cos.unsqueeze(unsqueeze_dim), sin.unsqueeze(unsqueeze_dim)
    return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)
def repeat_kv(hidden_states: sapiens_technology_torch.Tensor, n_rep: int) -> sapiens_technology_torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    return hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim).reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
class ModularEntityTextSelfAttention(entity_neural_network.Module):
    def __init__(self, config: ModularEntityTextConfig, layer_idx: int):
        super().__init__()
        self.config, self.num_heads, self.dropout = config, config.num_attention_heads, config.dropout
        self.hidden_size, self.num_key_value_heads = config.hidden_size, config.num_key_value_heads
        self.head_dim, self.num_key_value_groups = config.hidden_size // self.num_heads, self.num_heads // self.num_key_value_heads
        self.rope_theta, self.layer_idx = config.rope_theta, layer_idx
        self.q_proj, self.k_proj = entity_neural_network.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj, self.o_proj = entity_neural_network.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False), entity_neural_network.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: sapiens_technology_torch.Tensor, position_embeddings: sapiens_technology_torch.Tensor, output_attentions: bool = False, use_cache: bool = False,
    past_key_value=None, cache_position=None, **kwargs):
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states, value_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        attn_weights = sapiens_technology_torch.matmul(query_states, key_states.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
        if not output_attentions: attn_weights = None
        return self.o_proj(sapiens_technology_torch.matmul(attn_weights, value_states).transpose(1, 2).contiguous().view(bsz, q_len, -1)), entity_neural_network.functional.dropout(entity_neural_network.functional.softmax(attn_weights, dim=-1, dtype=sapiens_technology_torch.float32).to(query_states.dtype), p=self.dropout, training=self.training), past_key_value
class ModularEntityTextSelfSdpaAttention(ModularEntityTextSelfAttention):
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, attention_mask: sapiens_technology_torch.Tensor, position_embeddings: sapiens_technology_torch.Tensor, output_attentions: bool = False, use_cache: bool = False,
    past_key_value=None, cache_position=None, **kwargs):
        if output_attentions:
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_embeddings=position_embeddings, past_key_value=past_key_value,
            output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, **kwargs)
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states, causal_mask = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups), attention_mask
        if attention_mask is not None: causal_mask = causal_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and causal_mask is not None: query_states, key_states, value_states = query_states.contiguous(), key_states.contiguous(), value_states.contiguous()
        is_causal = True if causal_mask is None and q_len > 1 else False
        return self.o_proj(sapiens_technology_torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal).transpose(1, 2).contiguous().view(bsz, q_len, -1)), None, past_key_value
MODULAR_ENTITY_TEXT_CROSS_ATTENTION_CLASSES = {"eager": ModularEntityTextCrossAttention, "sdpa": ModularEntityTextCrossSdpaAttention}
MODULAR_ENTITY_TEXT_ATTENTION_CLASSES = {"eager": ModularEntityTextSelfAttention, "sdpa": ModularEntityTextSelfSdpaAttention}
class ModularEntityTextMLP(entity_neural_network.Module):
    def __init__(self, config):
        super().__init__()
        from ...activations import ACT2FN
        self.config, self.hidden_size, self.intermediate_size = config, config.hidden_size, config.intermediate_size
        self.gate_proj, self.up_proj = entity_neural_network.Linear(self.hidden_size, self.intermediate_size, bias=False), entity_neural_network.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj, self.act_fn = entity_neural_network.Linear(self.intermediate_size, self.hidden_size, bias=False), ACT2FN[config.hidden_act]
    def forward(self, x): return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))
class ModularEntitySelfAttentionDecoderLayer(entity_neural_network.Module):
    def __init__(self, config: ModularEntityTextConfig, layer_idx: int):
        super().__init__()
        self.hidden_size, self.self_attn = config.hidden_size, MODULAR_ENTITY_TEXT_ATTENTION_CLASSES[config._attn_implementation](config=config, layer_idx=layer_idx)
        self.mlp, self.input_layernorm = ModularEntityTextMLP(config), ModularEntityTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm, self.layer_idx = ModularEntityTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps), layer_idx
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cross_attention_states: Optional[sapiens_technology_torch.Tensor] = None, cross_attention_mask: Optional[sapiens_technology_torch.Tensor] = None,
    attention_mask: Optional[sapiens_technology_torch.Tensor] = None, full_text_row_masked_out_mask: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None,
    past_key_value: Optional[Cache] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[sapiens_technology_torch.LongTensor] = None,
    position_embeddings: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None) -> Tuple[sapiens_technology_torch.FloatTensor, Optional[Tuple[sapiens_technology_torch.FloatTensor, sapiens_technology_torch.FloatTensor]]]:
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
class ModularEntityCrossAttentionDecoderLayer(sapiens_technology_torch.nn.Module):
    def __init__(self, config: ModularEntityTextConfig, layer_idx: int) -> None:
        super().__init__()
        self.layer_idx, self.cross_attn = layer_idx, MODULAR_ENTITY_TEXT_CROSS_ATTENTION_CLASSES[config._attn_implementation](config, layer_idx=layer_idx)
        self.input_layernorm, self.cross_attn_attn_gate = ModularEntityTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps), sapiens_technology_torch.nn.Parameter(sapiens_technology_torch.zeros(1))
        self.mlp, self.post_attention_layernorm = ModularEntityTextMLP(config), ModularEntityTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.cross_attn_mlp_gate = sapiens_technology_torch.nn.Parameter(sapiens_technology_torch.zeros(1))
    def forward(self, hidden_states: sapiens_technology_torch.Tensor, cross_attention_states: sapiens_technology_torch.Tensor, cross_attention_mask: sapiens_technology_torch.Tensor, attention_mask: sapiens_technology_torch.Tensor, full_text_row_masked_out_mask: Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor],
    position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_value: Optional[Cache] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False,
    cache_position: Optional[sapiens_technology_torch.LongTensor] = None, position_embeddings: Optional[sapiens_technology_torch.Tensor] = None) -> Tuple[sapiens_technology_torch.Tensor]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, attn_weights, past_key_value = self.cross_attn(hidden_states=hidden_states, attention_mask=cross_attention_mask, cross_attention_states=cross_attention_states,
        past_key_value=past_key_value, output_attentions=output_attentions, cache_position=cache_position)
        hidden_states = residual + self.cross_attn_attn_gate.tanh() * hidden_states
        residual = hidden_states
        hidden_states = self.mlp(self.post_attention_layernorm(hidden_states))
        if full_text_row_masked_out_mask is not None: hidden_states = full_text_row_masked_out_mask[:, 0] * hidden_states
        hidden_states = residual + self.cross_attn_mlp_gate.tanh() * hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        if use_cache: outputs += (past_key_value,)
        return outputs
class ModularEntityRotaryEmbedding(entity_neural_network.Module):
    def __init__(self, config: ModularEntityTextConfig, device=None):
        super().__init__()
        from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
        self.rope_type, self.max_seq_len_cached = config.rope_scaling["rope_type"], config.max_position_embeddings
        self.original_max_seq_len, self.config, self.rope_init_fn = config.max_position_embeddings, config, ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device)
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
        inv_freq_expanded, position_ids_expanded, device_type = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1), position_ids[:, None, :].float(), x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with sapiens_technology_torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = sapiens_technology_torch.cat((freqs, freqs), dim=-1)
            cos, sin = emb.cos(), emb.sin()
        return (cos * self.attention_scaling).to(dtype=x.dtype), (sin * self.attention_scaling).to(dtype=x.dtype)
class ModularEntityPrecomputedPositionEmbedding(entity_neural_network.Module):
    def __init__(self, config: ModularEntityVisionConfig):
        super().__init__()
        self.max_num_tiles, self.max_aspect_ratio_id = config.max_num_tiles, config.max_aspect_ratio_id
        self.num_patches, self.hidden_size = (config.image_size // config.patch_size) ** 2 + 1, config.hidden_size
        self.scale, self.gate = config.hidden_size**-0.5, entity_neural_network.Parameter(sapiens_technology_torch.zeros(1))
        self.embedding, self.tile_embedding = entity_neural_network.Parameter(self.scale * sapiens_technology_torch.randn(self.num_patches, self.hidden_size)), entity_neural_network.Embedding(self.max_aspect_ratio_id + 1, self.max_num_tiles * self.num_patches * self.hidden_size)
    def forward(self, hidden_state: sapiens_technology_torch.Tensor, aspect_ratio_ids: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        hidden_state = hidden_state + ((1 - self.gate.tanh()) * self.embedding).view(1, 1, self.num_patches, self.hidden_size)
        return hidden_state + (self.gate.tanh() * self.tile_embedding(aspect_ratio_ids).reshape(hidden_state.shape[0], self.max_num_tiles, self.num_patches, self.hidden_size))
from ... import PreTrainedModel
class ModularEntityPreTrainedModel(PreTrainedModel):
    config_class, base_model_prefix, supports_gradient_checkpointing = ModularEntityConfig, "model", True
    _no_split_modules = ["ModularEntityVisionEncoderLayer", "ModularEntityCrossAttentionDecoderLayer", "ModularEntitySelfAttentionDecoderLayer"]
    _supports_cache_class, _supports_static_cache, _supports_sdpa, _supports_quantized_cache = True, False, True, True
    def _init_weights(self, module):
        std = self.config.get_text_config().initializer_range
        if isinstance(module, (entity_neural_network.Linear, entity_neural_network.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, entity_neural_network.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, entity_neural_network.Parameter): module.data.normal_(mean=0.0, std=std)
        elif isinstance(module, ModularEntityVisionModel): entity_neural_network.init.normal_(module.class_embedding.data, std=std)
        elif isinstance(module, ModularEntityPrecomputedPositionEmbedding): entity_neural_network.init.normal_(module.embedding.data, std=std)
        elif isinstance(module, ModularEntityVisionEncoderLayer) and module.is_gated:
            entity_neural_network.init.normal_(module.gate_attn.data, std=std)
            entity_neural_network.init.normal_(module.gate_ffn.data, std=std)
class ModularEntityPrecomputedAspectRatioEmbedding(entity_neural_network.Module):
    def __init__(self, config: ModularEntityVisionConfig, is_gated: bool = True):
        super().__init__()
        self.max_num_tiles, self.hidden_size, self.max_aspect_ratio_id = config.max_num_tiles, config.hidden_size, config.max_aspect_ratio_id
        self.is_gated, self.embedding = is_gated, entity_neural_network.Embedding(self.max_aspect_ratio_id + 1, self.max_num_tiles * self.hidden_size)
        if is_gated: self.gate = entity_neural_network.Parameter(sapiens_technology_torch.zeros(1))
    def forward(self, hidden_state: sapiens_technology_torch.Tensor, aspect_ratio_ids: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        embeddings = self.embedding(aspect_ratio_ids).reshape(-1, self.max_num_tiles, 1, self.hidden_size)
        if self.is_gated: embeddings = embeddings * self.gate.tanh()
        return hidden_state + embeddings
def _prepare_aspect_ratio_attention_mask(aspect_ratio_mask: sapiens_technology_torch.Tensor, num_patches: int, target_length: int, dtype: sapiens_technology_torch.dtype) -> sapiens_technology_torch.Tensor:
    batch_size, max_num_tiles = aspect_ratio_mask.shape
    attention_mask = aspect_ratio_mask.view(batch_size, max_num_tiles, 1, 1).to(dtype).repeat(1, 1, target_length, 1)
    attention_mask[:, :, -(target_length - num_patches):] = 0
    attention_mask = (1 - attention_mask).reshape(batch_size, max_num_tiles * target_length, 1)
    return (attention_mask @ attention_mask.transpose(-1, -2) * sapiens_technology_torch.finfo(dtype).min).unsqueeze(1)
MODULAR_ENTITY_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, max_num_images, max_num_tiles, channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`ModularEntityImageProcessor.__call__`] for details ([]`ModularEntityProcessor`] uses
            [`ModularEntityImageProcessor`] for processing images).
        aspect_ratio_mask (`torch.Tensor` of shape `(batch_size, max_num_images, max_num_tiles)`, *optional*):
            Mask to avoid performing attention on padding tiles. Mask values selected in `[0, 1]`:
            - 1 for tiles that are *not masked*,
            - 0 for tiles that are *masked*.
        aspect_ratio_ids (`torch.Tensor` of shape `(batch_size, max_num_images)`, *optional*):
            Aspect ratio ids used to select the appropriate precomputed tile embeddings based on the aspect ratio of each input image.
            These ids correspond to indices in the model's list of supported aspect ratios, offset by 1.
            For example, if the model supports aspect ratios [[1, 1], [1, 2], [2, 1]]:
            - An image with aspect ratio [1, 1] would have ID 1
            - An image with aspect ratio [1, 2] would have ID 2
            - An image with aspect ratio [2, 1] would have ID 3
            The id 0 is reserved for padding (i.e., no image).
            If an image has aspect ratio [1, 2], that means it was split into 2 tiles horizontally, and its `aspect_ratio_id` would be 2.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attention_mask (`torch.Tensor` of shape `(batch_size, seq_length, max_num_images, max_num_tiles)`, *optional*):
            Cross-attention mask to control the interaction between text tokens and image tiles.
            This 4D tensor defines which image tiles each text token should attend to.
            For each text token (in seq_length):
            - 1 indicates the token *should attend* to the corresponding image tile
            - 0 indicates the token *should not attend* to the corresponding image tile
        cross_attention_states (`torch.FloatTensor`, *optional*):
            Output of the vision model, used for cross-attention. This tensor contains the processed image features that
            the language model will attend to.
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
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
MODULAR_ENTITY_TEXT_INPUTS_DOCSTRING = r"""
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
            If `past_key_values` is used, optionally only the last `input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attention_mask (`torch.Tensor` of shape `(batch_size, seq_length, max_num_images, max_num_tiles)`, *optional*):
            Cross-attention mask to control the interaction between text tokens and image tiles.
            This 4D tensor defines which image tiles each text token should attend to.
            For each text token (in seq_length):
            - 1 indicates the token *should attend* to the corresponding image tile
            - 0 indicates the token *should not attend* to the corresponding image tile
        cross_attention_states (`torch.FloatTensor`, *optional*):
            Output of the vision model, used for cross-attention. This tensor contains the processed image features that
            the language model will attend to.
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
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
MODULAR_ENTITY_VISION_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, max_num_images, max_num_tiles, channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`ModularEntityImageProcessor.__call__`] for details ([]`ModularEntityProcessor`] uses
            [`ModularEntityImageProcessor`] for processing images).
        aspect_ratio_mask (`torch.Tensor` of shape `(batch_size, max_num_images, max_num_tiles)`, *optional*):
            Mask to avoid performing attention on padding tiles. Mask values selected in `[0, 1]`:
            - 1 for tiles that are *not masked*,
            - 0 for tiles that are *masked*.
        aspect_ratio_ids (`torch.Tensor` of shape `(batch_size, max_num_images)`, *optional*):
            Aspect ratio ids used to select the appropriate precomputed tile embeddings based on the aspect ratio of each input image.
            These ids correspond to indices in the model's list of supported aspect ratios, offset by 1.
            For example, if the model supports aspect ratios [[1, 1], [1, 2], [2, 1]]:
            - An image with aspect ratio [1, 1] would have ID 1
            - An image with aspect ratio [1, 2] would have ID 2
            - An image with aspect ratio [2, 1] would have ID 3
            The id 0 is reserved for padding (i.e., no image).
            If an image has aspect ratio [1, 2], that means it was split into 2 tiles horizontally, and its `aspect_ratio_id` would be 2.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
MODULAR_ENTITY_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`ModularEntityConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@add_start_docstrings("The ModularEntity Vision Model which consists of two vision encoders.", MODULAR_ENTITY_START_DOCSTRING)
class ModularEntityVisionModel(ModularEntityPreTrainedModel):
    config_class = ModularEntityVisionConfig
    base_model_prefix = "vision_model"
    def __init__(self, config: ModularEntityVisionConfig):
        super().__init__(config)
        self.image_size, self.patch_size, self.max_num_tiles = config.image_size, config.patch_size, config.max_num_tiles
        self.hidden_size, self.num_channels, self.intermediate_layers_indices = config.hidden_size, config.num_channels, config.intermediate_layers_indices
        self.num_patches, self.scale = (self.image_size // self.patch_size) ** 2 + 1, config.hidden_size**-0.5
        self.patch_embedding = entity_neural_network.Conv2d(in_channels=config.num_channels, out_channels=self.hidden_size, kernel_size=self.patch_size, stride=self.patch_size, padding="valid", bias=False)
        self.class_embedding, self.gated_positional_embedding = entity_neural_network.Parameter(self.scale * sapiens_technology_torch.randn(self.hidden_size)), ModularEntityPrecomputedPositionEmbedding(config)
        self.pre_tile_positional_embedding, self.post_tile_positional_embedding = ModularEntityPrecomputedAspectRatioEmbedding(config, is_gated=True), ModularEntityPrecomputedAspectRatioEmbedding(config, is_gated=True)
        self.layernorm_pre, self.layernorm_post = entity_neural_network.LayerNorm(self.hidden_size), entity_neural_network.LayerNorm(self.hidden_size)
        self.transformer, self.global_transformer = ModularEntityVisionEncoder(config, config.num_hidden_layers, is_gated=False), ModularEntityVisionEncoder(config, config.num_global_layers, is_gated=True)
        self.post_init()
    def get_input_embeddings(self): return self.patch_embedding
    def apply_class_embedding(self, hidden_state: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        batch_size, _, hidden_size = hidden_state.shape
        return sapiens_technology_torch.cat([self.class_embedding.expand(batch_size, 1, hidden_size), hidden_state], dim=1)
    @add_start_docstrings_to_model_forward(MODULAR_ENTITY_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: sapiens_technology_torch.Tensor, aspect_ratio_ids: sapiens_technology_torch.Tensor, aspect_ratio_mask: sapiens_technology_torch.Tensor, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[BaseModelOutput, Tuple[sapiens_technology_torch.Tensor, ...]]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, num_concurrent_media, num_tiles, num_channels, height, width = pixel_values.shape
        pixel_values, aspect_ratio_ids = pixel_values.reshape(batch_size * num_concurrent_media * num_tiles, num_channels, height, width), aspect_ratio_ids.reshape(batch_size * num_concurrent_media, -1)
        hidden_state = self.patch_embedding(pixel_values.to(self.dtype).to(self.device)).flatten(2).transpose(1, 2)
        _, num_patches, dim = hidden_state.shape
        hidden_state = self.apply_class_embedding(self.pre_tile_positional_embedding(hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, -1, dim), aspect_ratio_ids).reshape(batch_size * num_concurrent_media * num_tiles, num_patches, dim))
        num_patches += 1
        hidden_state = self.layernorm_pre(self.gated_positional_embedding(hidden_state.reshape(batch_size * num_concurrent_media, num_tiles, num_patches, dim), aspect_ratio_ids))
        num_padding_patches = (8 - (hidden_state.shape[-2] % 8)) % 8
        hidden_state = Functional.pad(hidden_state, (0, 0, 0, num_padding_patches), mode="constant", value=0)
        slice_index = -num_padding_patches if num_padding_patches > 0 else None
        attention_mask = _prepare_aspect_ratio_attention_mask(aspect_ratio_mask=aspect_ratio_mask.reshape(batch_size * num_concurrent_media, -1), num_patches=self.num_patches, target_length=hidden_state.shape[2], dtype=self.dtype)
        hidden_state = hidden_state.view(batch_size * num_concurrent_media, -1, dim)
        output = self.transformer(hidden_state, attention_mask=attention_mask, output_hidden_states=True, output_attentions=output_attentions)
        hidden_state = self.post_tile_positional_embedding(self.layernorm_post(output[0]).reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, dim), aspect_ratio_ids)
        global_output = self.global_transformer(hidden_state.reshape(batch_size * num_concurrent_media, num_tiles * (num_patches + num_padding_patches), dim), attention_mask=attention_mask, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        hidden_state = global_output[0].reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, dim)
        hidden_state = hidden_state[:, :, :slice_index].reshape(batch_size, num_concurrent_media, num_tiles, num_patches, dim)
        all_intermediate_hidden_states = output[1]
        intermediate_hidden_states = sapiens_technology_torch.stack(all_intermediate_hidden_states, dim=-1)[..., self.intermediate_layers_indices].reshape(batch_size * num_concurrent_media, num_tiles, num_patches + num_padding_patches, -1)
        hidden_state = sapiens_technology_torch.cat([hidden_state, intermediate_hidden_states[:, :, :slice_index].reshape(batch_size, num_concurrent_media, num_tiles, num_patches, -1)], dim=-1)
        if output_hidden_states: hidden_states = tuple(all_intermediate_hidden_states) + tuple(global_output[1])
        else: hidden_states = None
        if output_attentions: attentions = tuple(output[2]) + tuple(global_output[2]) if output_hidden_states else tuple(global_output[1])
        else: attentions = None
        if not return_dict: return tuple(v for v in [hidden_state, hidden_states, attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_state, hidden_states=hidden_states, attentions=attentions)
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: sapiens_technology_torch.Tensor, sequence_length: int, target_length: int, dtype: sapiens_technology_torch.dtype, device: sapiens_technology_torch.device,
min_dtype: float, cache_position: sapiens_technology_torch.Tensor, batch_size: int):
    if attention_mask is not None and attention_mask.dim() == 4: causal_mask = attention_mask
    else:
        causal_mask = sapiens_technology_torch.full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != 1: causal_mask = sapiens_technology_torch.triu(causal_mask, diagonal=1)
        causal_mask *= sapiens_technology_torch.arange(target_length, device=device) > cache_position.reshape(-1, 1)
        causal_mask = causal_mask[None, None, :, :].expand(batch_size, 1, -1, -1)
        if attention_mask is not None:
            causal_mask = causal_mask.clone()
            mask_length = attention_mask.shape[-1]
            padding_mask = causal_mask[:, :, :, :mask_length] + attention_mask[:, None, None, :] == 0
            causal_mask[:, :, :, :mask_length] = causal_mask[:, :, :, :mask_length].masked_fill(padding_mask, min_dtype)
    return causal_mask
@add_start_docstrings("The ModularEntity Text Model which consists of transformer with self and cross attention layers.", MODULAR_ENTITY_START_DOCSTRING)
class ModularEntityTextModel(ModularEntityPreTrainedModel):
    config_class, base_model_prefix = ModularEntityTextConfig, "language_model.model"
    def __init__(self, config: ModularEntityTextConfig):
        super().__init__(config)
        self.padding_idx, self.vocab_size, layers = config.pad_token_id, config.vocab_size, []
        self.embed_tokens, self.cross_attention_layers = entity_neural_network.Embedding(config.vocab_size + 8, config.hidden_size, self.padding_idx), config.cross_attention_layers
        for layer_idx in range(config.num_hidden_layers):
            if layer_idx in self.cross_attention_layers: layers.append(ModularEntityCrossAttentionDecoderLayer(config, layer_idx))
            else: layers.append(ModularEntitySelfAttentionDecoderLayer(config, layer_idx))
        self.layers, self.norm = entity_neural_network.ModuleList(layers), ModularEntityTextRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb, self.gradient_checkpointing = ModularEntityRotaryEmbedding(config=config), False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    @add_start_docstrings_to_model_forward(MODULAR_ENTITY_TEXT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[sapiens_technology_torch.LongTensor] = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None,
    cross_attention_states: Optional[sapiens_technology_torch.FloatTensor] = None, cross_attention_mask: Optional[sapiens_technology_torch.Tensor] = None, full_text_row_masked_out_mask: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None,
    past_key_values: Optional[Union[Cache, List[sapiens_technology_torch.FloatTensor]]] = None, inputs_embeds: Optional[sapiens_technology_torch.FloatTensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[sapiens_technology_torch.LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache, return_dict = use_cache if use_cache is not None else self.config.use_cache, return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training and use_cache: use_cache = False
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        hidden_states = inputs_embeds
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = sapiens_technology_torch.arange(past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        causal_mask, position_embeddings = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions), self.rotary_emb(hidden_states, position_ids)
        all_hidden_states, all_self_attns, next_decoder_cache = () if output_hidden_states else None, () if output_attentions else None, None
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if (idx in self.cross_attention_layers) and cross_attention_states is None and (past_key_values is None or (past_key_values is not None and past_key_values.get_seq_length(idx) == 0)): continue
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, cross_attention_states, cross_attention_mask, causal_mask,
            full_text_row_masked_out_mask, position_ids, past_key_values, output_attentions, use_cache, cache_position, position_embeddings)
            else: layer_outputs = decoder_layer(hidden_states, cross_attention_states=cross_attention_states, cross_attention_mask=cross_attention_mask, attention_mask=causal_mask,
            full_text_row_masked_out_mask=full_text_row_masked_out_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions,
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
        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
        from ...modeling_attn_mask_utils import AttentionMaskConverter
        if self.config._attn_implementation == "sdpa" and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype, sequence_length, target_length = sapiens_technology_torch.finfo(dtype).min, input_tensor.shape[1], (attention_mask.shape[-1] if isinstance(attention_mask, sapiens_technology_torch.Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
from ...generation import GenerationMixin
@add_start_docstrings("The ModularEntity Text Model with a language modeling head on top.", MODULAR_ENTITY_START_DOCSTRING)
class ModularEntityForCausalLM(ModularEntityPreTrainedModel, GenerationMixin):
    config_class = ModularEntityTextConfig
    base_model_prefix = "language_model"
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        super().__init__(config.get_text_config())
        self.text_config, self.vocab_size = config.get_text_config(), self.text_config.vocab_size
        self.model, self.lm_head = ModularEntityTextModel._from_config(self.text_config, attn_implementation=config._attn_implementation), entity_neural_network.Linear(self.text_config.hidden_size, self.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value): self.model.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def set_decoder(self, decoder): self.model = decoder
    def get_decoder(self): return self.model
    @add_start_docstrings_to_model_forward(MODULAR_ENTITY_INPUTS_DOCSTRING)
    def forward(self, input_ids: sapiens_technology_torch.LongTensor = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, position_ids: Optional[sapiens_technology_torch.LongTensor] = None,
    cross_attention_states: Optional[sapiens_technology_torch.LongTensor] = None, cross_attention_mask: Optional[sapiens_technology_torch.LongTensor] = None, full_text_row_masked_out_mask: Optional[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]] = None,
    past_key_values: Optional[Union[Cache, List[sapiens_technology_torch.FloatTensor]]] = None, inputs_embeds: Optional[sapiens_technology_torch.FloatTensor] = None, labels: Optional[sapiens_technology_torch.LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[sapiens_technology_torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids=input_ids, cross_attention_states=cross_attention_states, attention_mask=attention_mask, position_ids=position_ids,
        cross_attention_mask=cross_attention_mask, full_text_row_masked_out_mask=full_text_row_masked_out_mask, past_key_values=past_key_values,
        inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states,
        return_dict=return_dict, cache_position=cache_position)
        logits, loss = self.lm_head(outputs[0][:, -num_logits_to_keep:, :]).float(), None
        if labels is not None:
            logits = logits.float()
            shift_logits, shift_labels = logits[..., :-1, :].contiguous(), labels[..., 1:].contiguous()
            from sapiens_technology_torch.nn import CrossEntropyLoss
            loss = CrossEntropyLoss()(shift_logits.view(-1, self.config.vocab_size), shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return CausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
def _prepare_cross_attention_mask(cross_attention_mask: sapiens_technology_torch.Tensor, num_vision_tokens: int, dtype: str) -> Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor]:
    batch_size, text_total_length, *_ = cross_attention_mask.shape
    cross_attention_mask = cross_attention_mask.repeat_interleave(num_vision_tokens, dim=3).view(batch_size, text_total_length, -1).unsqueeze(1)
    inverted_cross_attn_mask = (1.0 - cross_attention_mask).to(dtype)
    cross_attention_mask = inverted_cross_attn_mask.masked_fill(inverted_cross_attn_mask.to(sapiens_technology_torch.bool), sapiens_technology_torch.finfo(dtype).min)
    full_text_row_masked_out_mask = ((cross_attention_mask != sapiens_technology_torch.finfo(dtype).min).any(dim=-1).type_as(cross_attention_mask)[..., None])
    cross_attention_mask *= full_text_row_masked_out_mask
    return cross_attention_mask, full_text_row_masked_out_mask
def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, cache_position=None, position_ids=None,
use_cache=True, num_logits_to_keep=None, **kwargs):
    if past_key_values is not None:
        if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
        elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
    if attention_mask is not None and position_ids is None:
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids.masked_fill_(attention_mask == 0, 1)
        if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :].clone(memory_format=sapiens_technology_torch.contiguous_format)
    if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
    else: model_inputs = {"input_ids": input_ids.clone(memory_format=sapiens_technology_torch.contiguous_format), "inputs_embeds": None}
    if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
    model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
    return model_inputs
@add_start_docstrings("The ModularEntity model which consists of a vision encoder and a language model.", MODULAR_ENTITY_START_DOCSTRING)
class ModularEntityForConditionalGeneration(ModularEntityPreTrainedModel, GenerationMixin):
    def __init__(self, config: ModularEntityConfig):
        super().__init__(config)
        self.vocab_size, self.hidden_size = config.text_config.vocab_size, config.text_config.hidden_size
        self.max_num_tiles, self.vision_output_dim = config.vision_config.max_num_tiles, config.vision_config.vision_output_dim
        self.pad_token_id, self.vision_model = self.config.pad_token_id if self.config.pad_token_id is not None else -1, ModularEntityVisionModel._from_config(config.vision_config, attn_implementation=config._attn_implementation)
        self.language_model, self.multi_modal_projector = ModularEntityForCausalLM._from_config(config.text_config, attn_implementation=config._attn_implementation), entity_neural_network.Linear(config.vision_config.vision_output_dim, config.text_config.hidden_size, bias=True)
        self.post_init()
    def get_input_embeddings(self): return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.language_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.language_model.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.language_model.set_output_embeddings(new_embeddings)
    def set_decoder(self, decoder): self.language_model.set_decoder(decoder)
    def get_decoder(self): return self.language_model.get_decoder()
    def tie_weights(self): return self.language_model.tie_weights()
    @add_start_docstrings_to_model_forward(MODULAR_ENTITY_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[sapiens_technology_torch.LongTensor] = None, pixel_values: Optional[sapiens_technology_torch.FloatTensor] = None, aspect_ratio_mask: Optional[sapiens_technology_torch.Tensor] = None,
    aspect_ratio_ids: Optional[sapiens_technology_torch.Tensor] = None, attention_mask: Optional[sapiens_technology_torch.Tensor] = None, cross_attention_mask: Optional[sapiens_technology_torch.Tensor] = None, cross_attention_states: Optional[sapiens_technology_torch.Tensor] = None,
    position_ids: Optional[sapiens_technology_torch.LongTensor] = None, past_key_values: Optional[List[sapiens_technology_torch.FloatTensor]] = None, inputs_embeds: Optional[sapiens_technology_torch.FloatTensor] = None,
    labels: Optional[sapiens_technology_torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[sapiens_technology_torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if pixel_values is not None and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values and inputs_embeds at the same time, and must specify either one")
        if pixel_values is not None and cross_attention_states is not None: raise ValueError("`pixel_values` and `cross_attention_states` cannot be provided simultaneously")
        if pixel_values is not None:
            if aspect_ratio_ids is None: raise ValueError("`aspect_ratio_ids` must be provided if `pixel_values` is provided")
            vision_outputs = self.vision_model(pixel_values=pixel_values, aspect_ratio_ids=aspect_ratio_ids, aspect_ratio_mask=aspect_ratio_mask, output_hidden_states=output_hidden_states,
            output_attentions=output_attentions, return_dict=return_dict)
            cross_attention_states = vision_outputs[0]
            cross_attention_states = self.multi_modal_projector(cross_attention_states).reshape(-1, cross_attention_states.shape[-2], self.hidden_size)
        if cross_attention_mask is not None: cross_attention_mask, full_text_row_masked_out_mask = _prepare_cross_attention_mask(cross_attention_mask, num_vision_tokens=self.vision_model.num_patches, dtype=self.dtype)
        else: full_text_row_masked_out_mask = None
        if cross_attention_mask is not None and cache_position is not None: cross_attention_mask, full_text_row_masked_out_mask = cross_attention_mask[:, :, cache_position], full_text_row_masked_out_mask[:, :, cache_position]
        outputs = self.language_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, cross_attention_states=cross_attention_states,
        cross_attention_mask=cross_attention_mask, full_text_row_masked_out_mask=full_text_row_masked_out_mask, past_key_values=past_key_values, use_cache=use_cache,
        inputs_embeds=inputs_embeds, labels=labels, output_hidden_states=output_hidden_states, output_attentions=output_attentions, return_dict=return_dict,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
        return outputs
    def prepare_inputs_for_generation(self, input_ids=None, inputs_embeds=None, attention_mask=None, position_ids=None, pixel_values=None, aspect_ratio_ids=None,
    aspect_ratio_mask=None, cross_attention_mask=None, past_key_values=None, use_cache=False, cache_position=None, num_logits_to_keep=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :].clone(memory_format=sapiens_technology_torch.contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=sapiens_technology_torch.contiguous_format), "inputs_embeds": None}
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask, "cross_attention_mask": cross_attention_mask})
        if (input_ids == self.config.image_token_index).any(): model_inputs["pixel_values"], model_inputs["aspect_ratio_ids"], model_inputs["aspect_ratio_mask"] = pixel_values, aspect_ratio_ids, aspect_ratio_mask
        return model_inputs
    def _update_model_kwargs_for_generation(self, outputs, model_kwargs, is_encoder_decoder, **kwargs):
        cross_attention_mask_prev = model_kwargs.get("cross_attention_mask", None)
        model_kwargs = super()._update_model_kwargs_for_generation(outputs=outputs, model_kwargs=model_kwargs, is_encoder_decoder=is_encoder_decoder, **kwargs)
        if cross_attention_mask_prev is not None: model_kwargs["cross_attention_mask"] = sapiens_technology_torch.cat([cross_attention_mask_prev, cross_attention_mask_prev[:, -1:, ...]], dim=1)
        return model_kwargs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
