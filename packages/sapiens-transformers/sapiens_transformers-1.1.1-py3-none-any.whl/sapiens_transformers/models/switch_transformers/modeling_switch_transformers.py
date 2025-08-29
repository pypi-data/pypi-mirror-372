"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import math
import warnings
from typing import Optional, Tuple, Union
import torch
import torch.nn as nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...generation import GenerationMixin
from ...modeling_outputs import (MoEModelOutput, MoEModelOutputWithPastAndCrossAttentions, Seq2SeqMoEModelOutput, Seq2SeqMoEOutput)
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import ALL_LAYERNORM_LAYERS, find_pruneable_heads_and_indices, prune_linear_layer
from ...utils import (DUMMY_INPUTS, DUMMY_MASK, add_start_docstrings, add_start_docstrings_to_model_forward, is_torch_fx_proxy, logging, replace_return_docstrings)
from .configuration_switch_transformers import SwitchTransformersConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "SwitchTransformersConfig"
_CHECKPOINT_FOR_DOC = "google/switch-base-8"
def router_z_loss_func(router_logits: torch.Tensor) -> float:
    num_groups, tokens_per_group, _ = router_logits.shape
    log_z = torch.logsumexp(router_logits, dim=-1)
    z_loss = log_z**2
    return torch.sum(z_loss) / (num_groups * tokens_per_group)
def load_balancing_loss_func(router_probs: torch.Tensor, expert_indices: torch.Tensor) -> float:
    num_experts = router_probs.shape[-1]
    if expert_indices.dtype != torch.int64: expert_indices = expert_indices.to(torch.int64)
    if len(expert_indices.shape) == 2: expert_indices = expert_indices.unsqueeze(2)
    expert_mask = torch.nn.functional.one_hot(expert_indices, num_experts)
    expert_mask = torch.max(expert_mask, axis=-2).values
    expert_mask = expert_mask.to(torch.float32)
    tokens_per_group_and_expert = torch.mean(expert_mask, axis=-2)
    router_prob_per_group_and_expert = torch.mean(router_probs, axis=-2)
    return torch.mean(tokens_per_group_and_expert * router_prob_per_group_and_expert) * (num_experts**2)
class SwitchTransformersTop1Router(nn.Module):
    def __init__(self, config: SwitchTransformersConfig):
        super().__init__()
        self.num_experts = config.num_experts
        self.expert_capacity = config.expert_capacity
        self.classifier = nn.Linear(config.hidden_size, self.num_experts, bias=config.router_bias)
        self.jitter_noise = config.router_jitter_noise
        self.ignore_padding_tokens = config.router_ignore_padding_tokens
        self.dtype = getattr(torch, config.router_dtype)
    def _compute_router_probabilities(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        self.input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(self.dtype)
        if self.training and self.jitter_noise > 0: hidden_states *= torch.empty_like(hidden_states).uniform_(1.0 - self.jitter_noise, 1.0 + self.jitter_noise)
        self._cast_classifier()
        router_logits = self.classifier(hidden_states)
        router_probabilities = nn.functional.softmax(router_logits, dim=-1, dtype=self.dtype).to(self.input_dtype)
        return router_probabilities, router_logits
    def _cast_classifier(self):
        if not (hasattr(self.classifier, "SCB") or hasattr(self.classifier, "CB")): self.classifier = self.classifier.to(self.dtype)
    def forward(self, hidden_states: torch.Tensor) -> Tuple:
        router_probs, router_logits = self._compute_router_probabilities(hidden_states)
        expert_index = torch.argmax(router_probs, dim=-1)
        expert_index = torch.nn.functional.one_hot(expert_index, num_classes=self.num_experts)
        token_priority = torch.cumsum(expert_index, dim=-2)
        expert_capacity_mask = token_priority <= self.expert_capacity
        expert_index = expert_index * expert_capacity_mask
        router_probs = torch.max(router_probs, dim=-1).values.unsqueeze(-1)
        return expert_index, router_probs, router_logits
class SwitchTransformersLayerNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states):
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        if self.weight.dtype in [torch.float16, torch.bfloat16]: hidden_states = hidden_states.to(self.weight.dtype)
        return self.weight * hidden_states
ALL_LAYERNORM_LAYERS.append(SwitchTransformersLayerNorm)
class SwitchTransformersDenseActDense(nn.Module):
    def __init__(self, config: SwitchTransformersConfig):
        super().__init__()
        self.wi = nn.Linear(config.d_model, config.d_ff, bias=False)
        self.wo = nn.Linear(config.d_ff, config.d_model, bias=False)
        self.dropout = nn.Dropout(config.dropout_rate)
        self.act = ACT2FN[config.dense_act_fn]
    def forward(self, hidden_states):
        hidden_states = self.wi(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.dropout(hidden_states)
        if (isinstance(self.wo.weight, torch.Tensor) and hidden_states.dtype != self.wo.weight.dtype and self.wo.weight.dtype != torch.int8): hidden_states = hidden_states.to(self.wo.weight.dtype)
        hidden_states = self.wo(hidden_states)
        return hidden_states
class SwitchTransformersSparseMLP(nn.Module):
    def __init__(self, config: SwitchTransformersConfig, expert_class: nn.Module = SwitchTransformersDenseActDense):
        super().__init__()
        self.router = SwitchTransformersTop1Router(config)
        self.experts = nn.ModuleDict()
        for idx in range(config.num_experts): self.experts[f"expert_{idx}"] = expert_class(config)
    def forward(self, hidden_states):
        router_mask, router_probs, router_logits = self.router(hidden_states)
        expert_index = torch.argmax(router_mask, dim=-1)
        next_states = hidden_states.clone()
        router_mask = router_mask.bool()
        batch_size, seq_len, num_experts = router_mask.shape
        idx_mask = router_mask.transpose(1, 2).reshape(batch_size * seq_len, num_experts).sum(dim=0)
        idx_mask = torch.nonzero(idx_mask, as_tuple=True)[0].tolist()
        for idx in idx_mask: next_states[router_mask[:, :, idx]] = getattr(self.experts, "expert_{}".format(idx))(hidden_states[router_mask[:, :, idx]])
        hidden_states = router_probs * next_states
        return hidden_states, (router_logits, expert_index)
class SwitchTransformersLayerFF(nn.Module):
    def __init__(self, config: SwitchTransformersConfig, is_sparse=False):
        super().__init__()
        self.is_sparse = is_sparse
        if not self.is_sparse: self.mlp = SwitchTransformersDenseActDense(config)
        else: self.mlp = SwitchTransformersSparseMLP(config)
        self.layer_norm = SwitchTransformersLayerNorm(config.d_model, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.dropout_rate)
    def forward(self, hidden_states, output_router_logits):
        forwarded_states = self.layer_norm(hidden_states)
        forwarded_states = self.mlp(forwarded_states)
        if isinstance(forwarded_states, tuple): forwarded_states, router_tuple = forwarded_states
        else: router_tuple = None
        output = hidden_states + self.dropout(forwarded_states)
        if output_router_logits and router_tuple is not None: output = (output, router_tuple)
        return output
class SwitchTransformersAttention(nn.Module):
    def __init__(self, config: SwitchTransformersConfig, has_relative_attention_bias=False):
        super().__init__()
        self.is_decoder = config.is_decoder
        self.has_relative_attention_bias = has_relative_attention_bias
        self.relative_attention_num_buckets = config.relative_attention_num_buckets
        self.relative_attention_max_distance = config.relative_attention_max_distance
        self.d_model = config.d_model
        self.key_value_proj_dim = config.d_kv
        self.n_heads = config.num_heads
        self.dropout = config.dropout_rate
        self.inner_dim = self.n_heads * self.key_value_proj_dim
        self.q = nn.Linear(self.d_model, self.inner_dim, bias=False)
        self.k = nn.Linear(self.d_model, self.inner_dim, bias=False)
        self.v = nn.Linear(self.d_model, self.inner_dim, bias=False)
        self.o = nn.Linear(self.inner_dim, self.d_model, bias=False)
        if self.has_relative_attention_bias: self.relative_attention_bias = nn.Embedding(self.relative_attention_num_buckets, self.n_heads)
        self.pruned_heads = set()
        self.gradient_checkpointing = False
    def prune_heads(self, heads):
        if len(heads) == 0: return
        heads, index = find_pruneable_heads_and_indices(heads, self.n_heads, self.key_value_proj_dim, self.pruned_heads)
        self.q = prune_linear_layer(self.q, index)
        self.k = prune_linear_layer(self.k, index)
        self.v = prune_linear_layer(self.v, index)
        self.o = prune_linear_layer(self.o, index, dim=1)
        self.n_heads = self.n_heads - len(heads)
        self.inner_dim = self.key_value_proj_dim * self.n_heads
        self.pruned_heads = self.pruned_heads.union(heads)
    @staticmethod
    def _relative_position_bucket(relative_position, bidirectional=True, num_buckets=32, max_distance=128):
        relative_buckets = 0
        if bidirectional:
            num_buckets //= 2
            relative_buckets += (relative_position > 0).to(torch.long) * num_buckets
            relative_position = torch.abs(relative_position)
        else: relative_position = -torch.min(relative_position, torch.zeros_like(relative_position))
        max_exact = num_buckets // 2
        is_small = relative_position < max_exact
        relative_position_if_large = max_exact + (torch.log(relative_position.float() / max_exact) / math.log(max_distance / max_exact) * (num_buckets - max_exact)).to(torch.long)
        relative_position_if_large = torch.min(relative_position_if_large, torch.full_like(relative_position_if_large, num_buckets - 1))
        relative_buckets += torch.where(is_small, relative_position, relative_position_if_large)
        return relative_buckets
    def compute_bias(self, query_length, key_length, device=None):
        if device is None: device = self.relative_attention_bias.weight.device
        context_position = torch.arange(query_length, dtype=torch.long, device=device)[:, None]
        memory_position = torch.arange(key_length, dtype=torch.long, device=device)[None, :]
        relative_position = memory_position - context_position
        relative_position_bucket = self._relative_position_bucket(relative_position, bidirectional=(not self.is_decoder), num_buckets=self.relative_attention_num_buckets, max_distance=self.relative_attention_max_distance)
        values = self.relative_attention_bias(relative_position_bucket)
        values = values.permute([2, 0, 1]).unsqueeze(0)
        return values
    def forward(self, hidden_states, mask=None, key_value_states=None, position_bias=None, past_key_value=None, layer_head_mask=None, query_length=None, use_cache=False, output_attentions=False):
        batch_size, seq_length = hidden_states.shape[:2]
        real_seq_length = seq_length
        if past_key_value is not None:
            if len(past_key_value) != 2: raise ValueError(f"past_key_value should have 2 past states: keys and values. Got { len(past_key_value)} past states")
            real_seq_length += past_key_value[0].shape[2] if query_length is None else query_length
        key_length = real_seq_length if key_value_states is None else key_value_states.shape[1]
        def shape(states): return states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
        def unshape(states): return states.transpose(1, 2).contiguous().view(batch_size, -1, self.inner_dim)
        def project(hidden_states, proj_layer, key_value_states, past_key_value):
            if key_value_states is None: hidden_states = shape(proj_layer(hidden_states))
            elif past_key_value is None: hidden_states = shape(proj_layer(key_value_states))
            if past_key_value is not None:
                if key_value_states is None: hidden_states = torch.cat([past_key_value, hidden_states], dim=2)
                elif past_key_value.shape[2] != key_value_states.shape[1]: hidden_states = shape(proj_layer(key_value_states))
                else: hidden_states = past_key_value
            return hidden_states
        query_states = shape(self.q(hidden_states))
        key_states = project(hidden_states, self.k, key_value_states, past_key_value[0] if past_key_value is not None else None)
        value_states = project(hidden_states, self.v, key_value_states, past_key_value[1] if past_key_value is not None else None)
        scores = torch.matmul(query_states, key_states.transpose(3, 2))
        if position_bias is None:
            if not self.has_relative_attention_bias:
                position_bias = torch.zeros((1, self.n_heads, real_seq_length, key_length), device=scores.device, dtype=scores.dtype)
                if self.gradient_checkpointing and self.training: position_bias.requires_grad = True
            else: position_bias = self.compute_bias(real_seq_length, key_length, device=scores.device)
            if past_key_value is not None: position_bias = position_bias[:, :, -hidden_states.size(1) :, :]
            if mask is not None: position_bias = position_bias + mask
        if self.pruned_heads:
            mask = torch.ones(position_bias.shape[1])
            mask[list(self.pruned_heads)] = 0
            position_bias_masked = position_bias[:, mask.bool()]
        else: position_bias_masked = position_bias
        scores += position_bias_masked
        attn_weights = nn.functional.softmax(scores.float(), dim=-1).type_as(scores)
        attn_weights = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        if layer_head_mask is not None: attn_weights = attn_weights * layer_head_mask
        attn_output = unshape(torch.matmul(attn_weights, value_states))
        attn_output = self.o(attn_output)
        present_key_value_state = (key_states, value_states) if (self.is_decoder and use_cache) else None
        outputs = (attn_output,) + (present_key_value_state,) + (position_bias,)
        if output_attentions: outputs = outputs + (attn_weights,)
        return outputs
class SwitchTransformersLayerSelfAttention(nn.Module):
    def __init__(self, config, has_relative_attention_bias=False):
        super().__init__()
        self.SelfAttention = SwitchTransformersAttention(config, has_relative_attention_bias=has_relative_attention_bias)
        self.layer_norm = SwitchTransformersLayerNorm(config.d_model, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.dropout_rate)
    def forward(self, hidden_states, attention_mask=None, position_bias=None, layer_head_mask=None, past_key_value=None, use_cache=False, output_attentions=False):
        normed_hidden_states = self.layer_norm(hidden_states)
        attention_output = self.SelfAttention(normed_hidden_states, mask=attention_mask, position_bias=position_bias, layer_head_mask=layer_head_mask, past_key_value=past_key_value,
        use_cache=use_cache, output_attentions=output_attentions)
        hidden_states = hidden_states + self.dropout(attention_output[0])
        outputs = (hidden_states,) + attention_output[1:]
        return outputs
class SwitchTransformersLayerCrossAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.EncDecAttention = SwitchTransformersAttention(config, has_relative_attention_bias=False)
        self.layer_norm = SwitchTransformersLayerNorm(config.d_model, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.dropout_rate)
    def forward(self, hidden_states, key_value_states, attention_mask=None, position_bias=None, layer_head_mask=None, past_key_value=None, use_cache=False, query_length=None, output_attentions=False):
        normed_hidden_states = self.layer_norm(hidden_states)
        attention_output = self.EncDecAttention(normed_hidden_states, mask=attention_mask, key_value_states=key_value_states, position_bias=position_bias, layer_head_mask=layer_head_mask,
        past_key_value=past_key_value, use_cache=use_cache, query_length=query_length, output_attentions=output_attentions)
        layer_output = hidden_states + self.dropout(attention_output[0])
        outputs = (layer_output,) + attention_output[1:]
        return outputs
class SwitchTransformersBlock(nn.Module):
    def __init__(self, config, has_relative_attention_bias=False, is_sparse=False):
        super().__init__()
        self.is_decoder = config.is_decoder
        self.is_sparse = is_sparse
        self.layer = nn.ModuleList()
        self.layer.append(SwitchTransformersLayerSelfAttention(config, has_relative_attention_bias=has_relative_attention_bias))
        if self.is_decoder: self.layer.append(SwitchTransformersLayerCrossAttention(config))
        self.layer.append(SwitchTransformersLayerFF(config, is_sparse=self.is_sparse))
    def forward(self, hidden_states, attention_mask=None, position_bias=None, encoder_hidden_states=None, encoder_attention_mask=None, encoder_decoder_position_bias=None,
    layer_head_mask=None, cross_attn_layer_head_mask=None, past_key_value=None, use_cache=False, output_attentions=False, output_router_logits=True, return_dict=True):
        if past_key_value is not None:
            if not self.is_decoder: logger.warning("`past_key_values` is passed to the encoder. Please make sure this is intended.")
            expected_num_past_key_values = 2 if encoder_hidden_states is None else 4
            if len(past_key_value) != expected_num_past_key_values: raise ValueError(f"There should be {expected_num_past_key_values} past states. {'2 (past / key) for cross attention.' if expected_num_past_key_values == 4 else ''} Got {len(past_key_value)} past key / value states")
            self_attn_past_key_value = past_key_value[:2]
            cross_attn_past_key_value = past_key_value[2:]
        else: self_attn_past_key_value, cross_attn_past_key_value = None, None
        self_attention_outputs = self.layer[0](hidden_states, attention_mask=attention_mask, position_bias=position_bias, layer_head_mask=layer_head_mask, past_key_value=self_attn_past_key_value,
        use_cache=use_cache, output_attentions=output_attentions)
        hidden_states, present_key_value_state = self_attention_outputs[:2]
        attention_outputs = self_attention_outputs[2:]
        if hidden_states.dtype == torch.float16 and torch.isinf(hidden_states).any():
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        do_cross_attention = self.is_decoder and encoder_hidden_states is not None
        if do_cross_attention:
            if present_key_value_state is not None: query_length = present_key_value_state[0].shape[2]
            else: query_length = None
            cross_attention_outputs = self.layer[1](hidden_states, key_value_states=encoder_hidden_states, attention_mask=encoder_attention_mask, position_bias=encoder_decoder_position_bias,
            layer_head_mask=cross_attn_layer_head_mask, past_key_value=cross_attn_past_key_value, query_length=query_length, use_cache=use_cache, output_attentions=output_attentions)
            hidden_states = cross_attention_outputs[0]
            if hidden_states.dtype == torch.float16 and torch.isinf(hidden_states).any():
                clamp_value = torch.finfo(hidden_states.dtype).max - 1000
                hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
            if present_key_value_state is not None: present_key_value_state = present_key_value_state + cross_attention_outputs[1]
            attention_outputs = attention_outputs + cross_attention_outputs[2:]
        hidden_states = self.layer[-1](hidden_states, output_router_logits)
        if isinstance(hidden_states, tuple): hidden_states, router_tuple = hidden_states
        else: router_tuple = (torch.zeros((1,), device=hidden_states.device, dtype=torch.int64),)
        if hidden_states.dtype == torch.float16 and torch.isinf(hidden_states).any():
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        outputs = (hidden_states,)
        if use_cache: outputs = outputs + (present_key_value_state,) + attention_outputs + (router_tuple,)
        else: outputs = outputs + attention_outputs + (router_tuple,)
        return outputs
class SwitchTransformersPreTrainedModel(PreTrainedModel):
    config_class = SwitchTransformersConfig
    base_model_prefix = "switch_transformers"
    supports_gradient_checkpointing = True
    _no_split_modules = ["SwitchTransformersBlock"]
    @property
    def dummy_inputs(self):
        input_ids = torch.tensor(DUMMY_INPUTS)
        input_mask = torch.tensor(DUMMY_MASK)
        dummy_inputs = {"decoder_input_ids": input_ids, "input_ids": input_ids, "decoder_attention_mask": input_mask}
        return dummy_inputs
    def _init_weights(self, module):
        factor = self.config.initializer_factor
        if isinstance(module, SwitchTransformersLayerNorm): module.weight.data.fill_(factor * 1.0)
        elif isinstance(module, (SwitchTransformersModel, SwitchTransformersForConditionalGeneration, SwitchTransformersEncoderModel)):
            module.shared.weight.data.normal_(mean=0.0, std=factor * 1.0)
            if hasattr(module, "lm_head") and not self.config.tie_word_embeddings: module.lm_head.weight.data.normal_(mean=0.0, std=factor * 1.0)
        elif isinstance(module, SwitchTransformersDenseActDense):
            module.wi.weight.data.normal_(mean=0.0, std=factor * ((self.config.d_model) ** -0.5))
            if hasattr(module.wi, "bias") and module.wi.bias is not None: module.wi.bias.data.zero_()
            module.wo.weight.data.normal_(mean=0.0, std=factor * ((self.config.d_ff) ** -0.5))
            if hasattr(module.wo, "bias") and module.wo.bias is not None: module.wo.bias.data.zero_()
        elif isinstance(module, SwitchTransformersAttention):
            d_model = self.config.d_model
            key_value_proj_dim = self.config.d_kv
            n_heads = self.config.num_heads
            module.q.weight.data.normal_(mean=0.0, std=factor * ((d_model * key_value_proj_dim) ** -0.5))
            module.k.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
            module.v.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
            module.o.weight.data.normal_(mean=0.0, std=factor * ((n_heads * key_value_proj_dim) ** -0.5))
            if module.has_relative_attention_bias: module.relative_attention_bias.weight.data.normal_(mean=0.0, std=factor * ((d_model) ** -0.5))
        elif isinstance(module, SwitchTransformersSparseMLP):
            d_model = self.config.d_model
            key_value_proj_dim = self.config.d_kv
            n_heads = self.config.num_heads
            module.router.classifier.weight.data.normal_(mean=0.0, std=factor * 1)
            for idx in range(self.config.num_experts):
                module.experts[f"expert_{idx}"].wi.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
                module.experts[f"expert_{idx}"].wo.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
    def _shift_right(self, input_ids):
        decoder_start_token_id = self.config.decoder_start_token_id
        pad_token_id = self.config.pad_token_id
        if decoder_start_token_id is None: raise ValueError("self.model.config.decoder_start_token_id has to be defined. In SwitchTransformers it is usually set to the pad_token_id. See SwitchTransformers docs for more information")
        if is_torch_fx_proxy(input_ids):
            shifted_input_ids = torch.full(input_ids.shape[:-1] + (1,), decoder_start_token_id)
            shifted_input_ids = torch.cat([shifted_input_ids, input_ids[..., :-1]], dim=-1)
        else:
            shifted_input_ids = input_ids.new_zeros(input_ids.shape)
            shifted_input_ids[..., 1:] = input_ids[..., :-1].clone()
            shifted_input_ids[..., 0] = decoder_start_token_id
        if pad_token_id is None: raise ValueError("self.model.config.pad_token_id has to be defined.")
        shifted_input_ids.masked_fill_(shifted_input_ids == -100, pad_token_id)
        return shifted_input_ids
class SwitchTransformersStack(SwitchTransformersPreTrainedModel):
    def __init__(self, config, embed_tokens=None):
        super().__init__(config)
        self.embed_tokens = nn.Embedding(config.vocab_size, config.d_model)
        if embed_tokens is not None: self.embed_tokens.weight = embed_tokens.weight
        self.is_decoder = config.is_decoder
        sparse_step = config.decoder_sparse_step if self.is_decoder else config.encoder_sparse_step
        config.num_layers = config.num_decoder_layers if self.is_decoder else config.num_layers
        self.block = nn.ModuleList()
        for i in range(config.num_layers):
            is_sparse = (i % sparse_step == 1 or sparse_step == 1) if sparse_step > 0 else False
            self.block.append(SwitchTransformersBlock(config, has_relative_attention_bias=bool(i == 0), is_sparse=is_sparse))
        self.final_layer_norm = SwitchTransformersLayerNorm(config.d_model, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.dropout_rate)
        self.post_init()
        self.device_map = None
        self.gradient_checkpointing = False
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, new_embeddings): self.embed_tokens = new_embeddings
    def forward(self, input_ids=None, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, inputs_embeds=None, head_mask=None, cross_attn_head_mask=None,
    past_key_values=None, use_cache=None, output_attentions=None, output_hidden_states=None, output_router_logits=True, return_dict=None):
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None:
            err_msg_prefix = "decoder_" if self.is_decoder else ""
            raise ValueError(f"You cannot specify both {err_msg_prefix}input_ids and {err_msg_prefix}inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
        elif inputs_embeds is not None: input_shape = inputs_embeds.size()[:-1]
        else:
            err_msg_prefix = "decoder_" if self.is_decoder else ""
            raise ValueError(f"You have to specify either {err_msg_prefix}input_ids or {err_msg_prefix}inputs_embeds")
        if inputs_embeds is None:
            if self.embed_tokens is None: raise ValueError("You have to initialize the model with valid token embeddings")
            inputs_embeds = self.embed_tokens(input_ids)
        batch_size, seq_length = input_shape
        mask_seq_length = past_key_values[0][0].shape[2] + seq_length if past_key_values is not None else seq_length
        if use_cache is True:
            if not self.is_decoder: raise ValueError(f"`use_cache` can only be set to `True` if {self} is used as a decoder")
        if attention_mask is None: attention_mask = torch.ones(batch_size, mask_seq_length, device=inputs_embeds.device)
        if self.is_decoder and encoder_attention_mask is None and encoder_hidden_states is not None:
            encoder_seq_length = encoder_hidden_states.shape[1]
            encoder_attention_mask = torch.ones(batch_size, encoder_seq_length, device=inputs_embeds.device, dtype=torch.long)
        if past_key_values is None: past_key_values = [None] * len(self.block)
        extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape)
        if self.is_decoder and encoder_hidden_states is not None:
            encoder_batch_size, encoder_sequence_length, _ = encoder_hidden_states.size()
            encoder_hidden_shape = (encoder_batch_size, encoder_sequence_length)
            if encoder_attention_mask is None: encoder_attention_mask = torch.ones(encoder_hidden_shape, device=inputs_embeds.device)
            encoder_extended_attention_mask = self.invert_attention_mask(encoder_attention_mask)
        else: encoder_extended_attention_mask = None
        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...")
                use_cache = False
        head_mask = self.get_head_mask(head_mask, self.config.num_layers)
        cross_attn_head_mask = self.get_head_mask(cross_attn_head_mask, self.config.num_layers)
        present_key_value_states = () if use_cache else None
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        all_router_probs = () if output_router_logits else None
        all_cross_attentions = () if (output_attentions and self.is_decoder) else None
        position_bias = None
        encoder_decoder_position_bias = None
        hidden_states = self.dropout(inputs_embeds)
        for i, (layer_module, past_key_value) in enumerate(zip(self.block, past_key_values)):
            layer_head_mask = head_mask[i]
            cross_attn_layer_head_mask = cross_attn_head_mask[i]
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.forward, hidden_states, extended_attention_mask,
            position_bias, encoder_hidden_states, encoder_extended_attention_mask, encoder_decoder_position_bias, layer_head_mask, cross_attn_layer_head_mask, None, use_cache, output_attentions)
            else: layer_outputs = layer_module(hidden_states, attention_mask=extended_attention_mask, position_bias=position_bias, encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_extended_attention_mask, encoder_decoder_position_bias=encoder_decoder_position_bias, layer_head_mask=layer_head_mask, cross_attn_layer_head_mask=cross_attn_layer_head_mask,
            past_key_value=past_key_value, use_cache=use_cache, output_attentions=output_attentions, output_router_logits=output_router_logits)
            router_probs = layer_outputs[-1]
            layer_outputs = layer_outputs[:-1]
            if use_cache is False: layer_outputs = layer_outputs[:1] + (None,) + layer_outputs[1:]
            hidden_states, present_key_value_state = layer_outputs[:2]
            position_bias = layer_outputs[2]
            if self.is_decoder and encoder_hidden_states is not None: encoder_decoder_position_bias = layer_outputs[4 if output_attentions else 3]
            if use_cache: present_key_value_states = present_key_value_states + (present_key_value_state,)
            if output_attentions:
                all_attentions = all_attentions + (layer_outputs[3],)
                if self.is_decoder: all_cross_attentions = all_cross_attentions + (layer_outputs[5],)
            if output_router_logits: all_router_probs = all_router_probs + (router_probs,)
        hidden_states = self.final_layer_norm(hidden_states)
        hidden_states = self.dropout(hidden_states)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, present_key_value_states, all_hidden_states, all_attentions, all_cross_attentions, all_router_probs] if v is not None)
        return MoEModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=present_key_value_states, hidden_states=all_hidden_states,
        attentions=all_attentions, cross_attentions=all_cross_attentions, router_probs=all_router_probs)
SWITCH_TRANSFORMERS_START_DOCSTRING = r"""
    The SWITCH_TRANSFORMERS model was proposed in [Switch Transformers: Scaling to Trillion Parameter Models with
    Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961) by [William
    Fedus](https://arxiv.org/search/cs?searchtype=author&query=Fedus%2C+W), [Barret
    Zoph](https://arxiv.org/search/cs?searchtype=author&query=Zoph%2C+B), and [Noam
    Shazeer](https://arxiv.org/search/cs?searchtype=author&query=Shazeer%2C+N). It's an encoder-decoder T5-like model
    with sparse Feed Forward that stands for Mixture of Experts (MoE) architecture.
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SwitchTransformersConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
SWITCH_TRANSFORMERS_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. SWITCH_TRANSFORMERS is a model with relative position
            embeddings so you should be able to pad the inputs on both the right and the left.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for detail.
            [What are input IDs?](../glossary#input-ids)
            To know more on how to prepare `input_ids` for pretraining take a look a [SWITCH_TRANSFORMERS
            Training](./switch_transformers#training).
        attention_mask (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        decoder_input_ids (`torch.LongTensor` of shape `(batch_size, target_sequence_length)`, *optional*):
            Indices of decoder input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are decoder input IDs?](../glossary#decoder-input-ids)
            SWITCH_TRANSFORMERS uses the `pad_token_id` as the starting token for `decoder_input_ids` generation. If
            `past_key_values` is used, optionally only the last `decoder_input_ids` have to be input (see
            `past_key_values`).
            To know more on how to prepare `decoder_input_ids` for pretraining take a look at [SWITCH_TRANSFORMERS
            Training](./switch_transformers#training).
        decoder_attention_mask (`torch.BoolTensor` of shape `(batch_size, target_sequence_length)`, *optional*):
            Default behavior: generate a tensor that ignores pad tokens in `decoder_input_ids`. Causal mask will also
            be used by default.
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules in the encoder. Mask values selected in `[0,
            1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        decoder_head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules in the decoder. Mask values selected in `[0,
            1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attn_head_mask (`torch.Tensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
                Mask to nullify selected heads of the cross-attention modules in the decoder. Mask values selected in
                `[0, 1]`:
                - 1 indicates the head is *not masked*,
                - 0 indicates the head is *masked*.
        encoder_outputs (`tuple(tuple(torch.FloatTensor)`, *optional*):
            Tuple consists of (`last_hidden_state`, `optional`: *hidden_states*, `optional`: *attentions*)
            `last_hidden_state` of shape `(batch_size, sequence_length, hidden_size)` is a sequence of hidden states at
            the output of the last layer of the encoder. Used in the cross-attention of the decoder.
        past_key_values (`tuple(tuple(torch.FloatTensor))` of length `config.n_layers` with each tuple having 4 tensors of shape `(batch_size, num_heads, sequence_length - 1, embed_size_per_head)`):
            Contains precomputed key and value hidden states of the attention blocks. Can be used to speed up decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        decoder_inputs_embeds (`torch.FloatTensor` of shape `(batch_size, target_sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `decoder_input_ids` you can choose to directly pass an embedded
            representation. If `past_key_values` is used, optionally only the last `decoder_inputs_embeds` have to be
            input (see `past_key_values`). This is useful if you want more control over how to convert
            `decoder_input_ids` indices into associated vectors than the model's internal embedding lookup matrix.
            If `decoder_input_ids` and `decoder_inputs_embeds` are both unset, `decoder_inputs_embeds` takes the value
            of `inputs_embeds`.
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
"""
SWITCH_TRANSFORMERS_ENCODER_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. SWITCH_TRANSFORMERS is a model with relative position
            embeddings so you should be able to pad the inputs on both the right and the left.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for detail.
            To know more on how to prepare `input_ids` for pretraining take a look a [SWITCH_TRANSFORMERS
            Training](./switch_transformers#training).
        attention_mask (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
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
"""
__HEAD_MASK_WARNING_MSG = """
The input argument `head_mask` was split into two arguments `head_mask` and `decoder_head_mask`. Currently,
`decoder_head_mask` is set to copy `head_mask`, but this feature is deprecated and will be removed in future versions.
If you do not want to use any `decoder_head_mask` now, please set `decoder_head_mask = torch.ones(num_layers,
num_heads)`.
"""
@add_start_docstrings("The bare SWITCH_TRANSFORMERS Model transformer outputting raw hidden-states without any specific head on top.", SWITCH_TRANSFORMERS_START_DOCSTRING)
class SwitchTransformersModel(SwitchTransformersPreTrainedModel):
    _tied_weights_keys = ["encoder.embed_tokens.weight", "decoder.embed_tokens.weight"]
    def __init__(self, config: SwitchTransformersConfig):
        super().__init__(config)
        self.shared = nn.Embedding(config.vocab_size, config.d_model)
        encoder_config = copy.deepcopy(config)
        encoder_config.is_decoder = False
        encoder_config.use_cache = False
        encoder_config.is_encoder_decoder = False
        self.encoder = SwitchTransformersStack(encoder_config, self.shared)
        decoder_config = copy.deepcopy(config)
        decoder_config.is_decoder = True
        decoder_config.is_encoder_decoder = False
        self.decoder = SwitchTransformersStack(decoder_config, self.shared)
        self.post_init()
        self.device_map = None
    def get_input_embeddings(self): return self.shared
    def set_input_embeddings(self, new_embeddings):
        self.shared = new_embeddings
        self.encoder.set_input_embeddings(new_embeddings)
        self.decoder.set_input_embeddings(new_embeddings)
    def _tie_weights(self):
        if self.config.tie_word_embeddings:
            self._tie_or_clone_weights(self.encoder.embed_tokens, self.shared)
            self._tie_or_clone_weights(self.decoder.embed_tokens, self.shared)
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(SWITCH_TRANSFORMERS_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, decoder_input_ids: Optional[torch.LongTensor] = None,
    decoder_attention_mask: Optional[torch.BoolTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    inputs_embeds: Optional[torch.Tensor] = None, decoder_inputs_embeds: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, output_router_logits: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], Seq2SeqMoEModelOutput]:
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if head_mask is not None and decoder_head_mask is None:
            if self.config.num_layers == self.config.num_decoder_layers:
                warnings.warn(__HEAD_MASK_WARNING_MSG, FutureWarning)
                decoder_head_mask = head_mask
        if (output_router_logits and self.config.num_sparse_encoder_layers == 0 and self.config.num_sparse_encoder_layers == 0): raise ValueError("You asked to return `output_router_logits` but the transformer in dense, and does not contain any sparse MLP Layers. Set `output_router_logits = False` and restart")
        if encoder_outputs is None: encoder_outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask, inputs_embeds=inputs_embeds, head_mask=head_mask,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, MoEModelOutput): encoder_outputs = MoEModelOutput(last_hidden_state=encoder_outputs[0], hidden_states=encoder_outputs[1] if len(encoder_outputs) > 1 else None,
        attentions=encoder_outputs[2] if len(encoder_outputs) > 2 else None, router_probs=encoder_outputs[3] if len(encoder_outputs) > 3 else None)
        hidden_states = encoder_outputs[0]
        decoder_outputs = self.decoder(input_ids=decoder_input_ids, attention_mask=decoder_attention_mask, inputs_embeds=decoder_inputs_embeds, past_key_values=past_key_values,
        encoder_hidden_states=hidden_states, encoder_attention_mask=attention_mask, head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict)
        if not return_dict: return decoder_outputs + encoder_outputs
        return Seq2SeqMoEModelOutput(last_hidden_state=decoder_outputs.last_hidden_state, past_key_values=decoder_outputs.past_key_values, decoder_hidden_states=decoder_outputs.hidden_states,
        decoder_attentions=decoder_outputs.attentions, cross_attentions=decoder_outputs.cross_attentions, decoder_router_logits=decoder_outputs.router_probs,
        encoder_last_hidden_state=encoder_outputs.last_hidden_state, encoder_hidden_states=encoder_outputs.hidden_states, encoder_attentions=encoder_outputs.attentions,
        encoder_router_logits=encoder_outputs.router_probs)
@add_start_docstrings("SWITCH_TRANSFORMERS Model with a `language modeling` head on top.", SWITCH_TRANSFORMERS_START_DOCSTRING)
class SwitchTransformersForConditionalGeneration(SwitchTransformersPreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["encoder.embed_tokens.weight", "decoder.embed_tokens.weight", "lm_head.weight"]
    def __init__(self, config: SwitchTransformersConfig):
        super().__init__(config)
        self.model_dim = config.d_model
        self.shared = nn.Embedding(config.vocab_size, config.d_model)
        encoder_config = copy.deepcopy(config)
        encoder_config.is_decoder = False
        encoder_config.use_cache = False
        encoder_config.is_encoder_decoder = False
        self.encoder = SwitchTransformersStack(encoder_config, self.shared)
        decoder_config = copy.deepcopy(config)
        decoder_config.is_decoder = True
        decoder_config.is_encoder_decoder = False
        decoder_config.num_layers = config.num_decoder_layers
        self.decoder = SwitchTransformersStack(decoder_config, self.shared)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.router_z_loss_coef = config.router_z_loss_coef
        self.router_aux_loss_coef = config.router_aux_loss_coef
        self.post_init()
        self.device_map = None
    def get_input_embeddings(self): return self.shared
    def set_input_embeddings(self, new_embeddings):
        self.shared = new_embeddings
        self.encoder.set_input_embeddings(new_embeddings)
        self.decoder.set_input_embeddings(new_embeddings)
    def _tie_weights(self):
        if self.config.tie_word_embeddings:
            self._tie_or_clone_weights(self.encoder.embed_tokens, self.shared)
            self._tie_or_clone_weights(self.decoder.embed_tokens, self.shared)
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def get_output_embeddings(self): return self.lm_head
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    @add_start_docstrings_to_model_forward(SWITCH_TRANSFORMERS_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, decoder_input_ids: Optional[torch.LongTensor] = None,
    decoder_attention_mask: Optional[torch.BoolTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.Tensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_router_logits: Optional[bool] = True, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], Seq2SeqMoEOutput]:
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if head_mask is not None and decoder_head_mask is None:
            if self.config.num_layers == self.config.num_decoder_layers:
                warnings.warn(__HEAD_MASK_WARNING_MSG, FutureWarning)
                decoder_head_mask = head_mask
        if encoder_outputs is None: encoder_outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask, inputs_embeds=inputs_embeds, head_mask=head_mask,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, MoEModelOutput): encoder_outputs = MoEModelOutput(last_hidden_state=encoder_outputs[0], hidden_states=encoder_outputs[1] if len(encoder_outputs) > 1 else None,
        attentions=encoder_outputs[2] if len(encoder_outputs) > 2 else None, router_probs=encoder_outputs[3] if len(encoder_outputs) > 3 else None)
        hidden_states = encoder_outputs[0]
        if labels is not None and decoder_input_ids is None and decoder_inputs_embeds is None: decoder_input_ids = self._shift_right(labels)
        decoder_outputs = self.decoder(input_ids=decoder_input_ids, attention_mask=decoder_attention_mask, inputs_embeds=decoder_inputs_embeds, past_key_values=past_key_values,
        encoder_hidden_states=hidden_states, encoder_attention_mask=attention_mask, head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict)
        sequence_output = decoder_outputs[0]
        if self.config.tie_word_embeddings: sequence_output = sequence_output * (self.model_dim**-0.5)
        lm_logits = self.lm_head(sequence_output)
        loss = None
        encoder_z_loss = None
        encoder_aux_loss = None
        decoder_z_loss = None
        decoder_aux_loss = None
        if output_router_logits:
            if self.encoder.config.encoder_sparse_step > 1:
                encoder_router_logits, encoder_expert_indexes = self._unpack_router_logits(encoder_outputs[-1])
                encoder_z_loss = router_z_loss_func(encoder_router_logits)
                encoder_router_probs = nn.Softmax(dim=-1)(encoder_router_logits)
                encoder_aux_loss = load_balancing_loss_func(encoder_router_probs, encoder_expert_indexes)
            else:
                encoder_z_loss = 0
                encoder_aux_loss = 0
            if self.decoder.config.decoder_sparse_step > 1:
                decoder_router_logits, decoder_expert_indexes = self._unpack_router_logits(decoder_outputs[-1])
                decoder_z_loss = router_z_loss_func(decoder_router_logits)
                decoder_router_probs = nn.Softmax(dim=-1)(decoder_router_logits)
                decoder_aux_loss = load_balancing_loss_func(decoder_router_probs, decoder_expert_indexes)
            else:
                decoder_z_loss = 0
                decoder_aux_loss = 0
        if labels is not None:
            loss_fct = CrossEntropyLoss(ignore_index=-100)
            labels = labels.to(lm_logits.device)
            loss = loss_fct(lm_logits.view(-1, lm_logits.size(-1)), labels.view(-1))
            if output_router_logits:
                z_loss = self.router_z_loss_coef * (encoder_z_loss + decoder_z_loss)
                aux_loss = self.router_aux_loss_coef * (encoder_aux_loss + decoder_aux_loss)
                loss = loss + z_loss + aux_loss
        if not return_dict:
            output = (lm_logits,)
            if output_router_logits: output += (encoder_z_loss, encoder_aux_loss, decoder_z_loss, decoder_aux_loss)
            output += (*decoder_outputs[1:], *encoder_outputs)
            return ((loss,) + output) if loss is not None else output
        return Seq2SeqMoEOutput(loss=loss, logits=lm_logits, encoder_z_loss=encoder_z_loss, encoder_aux_loss=encoder_aux_loss, decoder_z_loss=decoder_z_loss,
        decoder_aux_loss=decoder_aux_loss, past_key_values=decoder_outputs.past_key_values, decoder_hidden_states=decoder_outputs.hidden_states, decoder_attentions=decoder_outputs.attentions,
        cross_attentions=decoder_outputs.cross_attentions, decoder_router_logits=decoder_outputs.router_probs, encoder_last_hidden_state=encoder_outputs.last_hidden_state,
        encoder_hidden_states=encoder_outputs.hidden_states, encoder_attentions=encoder_outputs.attentions, encoder_router_logits=encoder_outputs.router_probs)
    def _unpack_router_logits(self, router_outputs):
        total_router_logits = []
        total_expert_indexes = []
        for router_output in router_outputs:
            if len(router_output[0].shape) > 1:
                router_logits, expert_indexes = router_output
                total_router_logits.append(router_logits)
                total_expert_indexes.append(expert_indexes)
        return torch.cat(total_router_logits, dim=1), torch.cat(total_expert_indexes, dim=1)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, head_mask=None, decoder_head_mask=None, cross_attn_head_mask=None, use_cache=None, encoder_outputs=None, **kwargs):
        if past_key_values is not None:
            past_length = past_key_values[0][0].shape[2]
            if input_ids.shape[1] > past_length: remove_prefix_length = past_length
            else: remove_prefix_length = input_ids.shape[1] - 1
            input_ids = input_ids[:, remove_prefix_length:]
        output_router_logits = kwargs.get("output_router_logits", True)
        return {"decoder_input_ids": input_ids, "past_key_values": past_key_values, "encoder_outputs": encoder_outputs, "attention_mask": attention_mask, "head_mask": head_mask,
        "decoder_head_mask": decoder_head_mask, "cross_attn_head_mask": cross_attn_head_mask, "use_cache": use_cache, "output_router_logits": output_router_logits}
    def prepare_decoder_input_ids_from_labels(self, labels: torch.Tensor): return self._shift_right(labels)
    def _reorder_cache(self, past_key_values, beam_idx):
        if past_key_values is None:
            logger.warning("You might want to consider setting `use_cache=True` to speed up decoding")
            return past_key_values
        reordered_decoder_past = ()
        for layer_past_states in past_key_values:
            reordered_layer_past_states = ()
            for layer_past_state in layer_past_states: reordered_layer_past_states = reordered_layer_past_states + (layer_past_state.index_select(0, beam_idx.to(layer_past_state.device)),)
            if reordered_layer_past_states[0].shape != layer_past_states[0].shape: raise ValueError(f"expected reordered_layer_past_states to have the same shape than layer_past_states, but got {reordered_layer_past_states[0].shape} and {layer_past_states[0].shape}")
            if len(reordered_layer_past_states) != len(layer_past_states): raise ValueError(f"expected layer_past_states to have the same length as reordered_layer_past_states, but got {len(layer_past_states)} and {len(reordered_layer_past_states)}")
            reordered_decoder_past = reordered_decoder_past + (reordered_layer_past_states,)
        return reordered_decoder_past
@add_start_docstrings("The bare SWITCH_TRANSFORMERS Model transformer outputting encoder's raw hidden-states without any specific head on top.", SWITCH_TRANSFORMERS_START_DOCSTRING)
class SwitchTransformersEncoderModel(SwitchTransformersPreTrainedModel):
    _tied_weights_keys = ["encoder.embed_tokens.weight"]
    def __init__(self, config: SwitchTransformersConfig):
        super().__init__(config)
        self.shared = nn.Embedding(config.vocab_size, config.d_model)
        encoder_config = copy.deepcopy(config)
        encoder_config.use_cache = False
        encoder_config.is_encoder_decoder = False
        self.encoder = SwitchTransformersStack(encoder_config, self.shared)
        self.post_init()
        self.device_map = None
    def get_input_embeddings(self): return self.shared
    def set_input_embeddings(self, new_embeddings):
        self.shared = new_embeddings
        self.encoder.set_input_embeddings(new_embeddings)
    def _tie_weights(self):
        if self.config.tie_word_embeddings: self._tie_or_clone_weights(self.encoder.embed_tokens, self.shared)
    def get_encoder(self): return self.encoder
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.block[layer].layer[0].SelfAttention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(SWITCH_TRANSFORMERS_ENCODER_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, head_mask: Optional[torch.FloatTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_router_logits: Optional[bool] = True,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], MoEModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask, inputs_embeds=inputs_embeds, head_mask=head_mask, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, output_router_logits=output_router_logits, return_dict=return_dict)
        return encoder_outputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
