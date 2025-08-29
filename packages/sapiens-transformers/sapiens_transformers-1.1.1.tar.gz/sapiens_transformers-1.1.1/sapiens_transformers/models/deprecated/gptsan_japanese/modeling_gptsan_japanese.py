"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from typing import List, Optional, Tuple, Union
import torch
import torch.nn as nn
from ....activations import ACT2FN
from ....modeling_outputs import MoECausalLMOutputWithPast, MoEModelOutputWithPastAndCrossAttentions
from ....modeling_utils import PreTrainedModel
from ....utils import (DUMMY_INPUTS, DUMMY_MASK, add_start_docstrings, add_start_docstrings_to_model_forward, is_torch_fx_proxy, logging)
from .configuration_gptsan_japanese import GPTSanJapaneseConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "GPTSanJapaneseConfig"
_CHECKPOINT_FOR_DOC = "Tanrei/GPTSAN-japanese"
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
class GPTSanJapaneseDenseActDense(nn.Module):
    def __init__(self, config: GPTSanJapaneseConfig, ext_layer=False):
        super().__init__()
        d_inter = config.d_ext if ext_layer else config.d_ff
        self.wi = nn.Linear(config.d_model, d_inter, bias=ext_layer)
        self.wo = nn.Linear(d_inter, config.d_model, bias=ext_layer)
        self.dropout = nn.Identity() if ext_layer else nn.Dropout(config.dropout_rate)
        self.act = ACT2FN["swish" if ext_layer else "relu"]
    def forward(self, hidden_states):
        hidden_states = self.wi(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.wo(hidden_states)
        return hidden_states
class GPTSanJapaneseTop1Router(nn.Module):
    def __init__(self, config: GPTSanJapaneseConfig):
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
class GPTSanJapaneseSparseMLP(nn.Module):
    def __init__(self, config: GPTSanJapaneseConfig, expert_class: nn.Module = GPTSanJapaneseDenseActDense):
        super().__init__()
        self.router = GPTSanJapaneseTop1Router(config)
        self.experts = nn.ModuleDict()
        for idx in range(config.num_experts): self.experts[f"expert_{idx}"] = expert_class(config)
    def forward(self, hidden_states):
        router_mask, router_probs, router_logits = self.router(hidden_states)
        expert_index = torch.argmax(router_mask, dim=-1)
        next_states = hidden_states.clone()
        for idx, expert in enumerate(self.experts.values()):
            token_indices = router_mask[:, :, idx].bool()
            next_states[token_indices] = expert(hidden_states[token_indices]).to(next_states.dtype)
        hidden_states = router_probs * next_states
        return hidden_states, (router_logits, expert_index)
class GPTSanJapaneseLayerSparseFF(nn.Module):
    def __init__(self, config: GPTSanJapaneseConfig):
        super().__init__()
        self.mlp = GPTSanJapaneseSparseMLP(config)
        self.soft_bypass_mlp = nn.Linear(config.d_model, config.d_model, bias=False)
        self.norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_epsilon)
    def forward(self, hidden_states, output_router_logits):
        forwarded_states, router_tuple = self.mlp(hidden_states)
        forwarded_states += torch.tanh(self.soft_bypass_mlp(hidden_states))
        output = hidden_states + self.norm(forwarded_states)
        if output_router_logits and router_tuple is not None: return output, router_tuple
        else: return output
class GPTSanJapaneseLayerDenseFF(nn.Module):
    def __init__(self, config: GPTSanJapaneseConfig):
        super().__init__()
        self.mlp = GPTSanJapaneseDenseActDense(config, ext_layer=True)
        self.norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_epsilon)
    def forward(self, hidden_states):
        forwarded_states = self.mlp(hidden_states)
        output = hidden_states + self.norm(forwarded_states)
        return output
class GPTSanJapaneseAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True, is_causal: bool = False, config: Optional[GPTSanJapaneseConfig] = None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        self.config = config
        if (self.head_dim * num_heads) != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {num_heads}).")
        self.scaling = self.head_dim**-0.5
        self.is_decoder = is_decoder
        self.is_causal = is_causal
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, attention_mask: Optional[torch.Tensor] = None,
    layer_head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scaling
        if (is_cross_attention and past_key_value is not None and past_key_value[0].shape[2] == key_value_states.shape[1]):
            key_states = past_key_value[0]
            value_states = past_key_value[1]
        elif is_cross_attention:
            key_states = self._shape(self.k_proj(key_value_states), -1, bsz)
            value_states = self._shape(self.v_proj(key_value_states), -1, bsz)
        elif past_key_value is not None:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
            key_states = torch.cat([past_key_value[0], key_states], dim=2)
            value_states = torch.cat([past_key_value[1], value_states], dim=2)
        else:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
        if self.is_decoder: past_key_value = (key_states, value_states)
        proj_shape = (bsz * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, tgt_len, bsz).view(*proj_shape)
        key_states = key_states.reshape(*proj_shape)
        value_states = value_states.reshape(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if layer_head_mask is not None:
            if layer_head_mask.size() != (self.num_heads,): raise ValueError(f"Head mask for a single layer should be of size {(self.num_heads,)}, but is {layer_head_mask.size()}")
            attn_weights = layer_head_mask.view(1, -1, 1, 1) * attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights_reshaped.view(bsz * self.num_heads, tgt_len, src_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz * self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped, past_key_value
class GPTSanJapaneseLayerSelfAttention(nn.Module):
    def __init__(self, config, has_relative_attention_bias=False):
        super().__init__()
        self.self_attn = GPTSanJapaneseAttention(embed_dim=config.d_model, num_heads=config.num_heads, is_decoder=True, bias=has_relative_attention_bias)
        self.norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_epsilon)
    def forward(self, hidden_states: Optional[Tuple[torch.FloatTensor]], past_key_value: Optional[Tuple[torch.Tensor]] = None, attention_mask: Optional[torch.FloatTensor] = None,
    head_mask: Optional[torch.FloatTensor] = None, use_cache: Optional[bool] = False, output_attentions: Optional[bool] = False) -> Tuple[Union[torch.Tensor, Tuple[torch.Tensor]], ...]:
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        atten_out = self.self_attn(hidden_states=hidden_states, past_key_value=self_attn_past_key_value, attention_mask=(1 - attention_mask) * torch.finfo(hidden_states.dtype).min,
        layer_head_mask=head_mask, output_attentions=output_attentions)
        if output_attentions: attn_weights = (atten_out[1],)
        else: attn_weights = ()
        attention_output = atten_out[0]
        hidden = hidden_states + self.norm(attention_output)
        if use_cache: outputs = (hidden, atten_out[2])
        else: outputs = (hidden,)
        return outputs + attn_weights
class GPTSanJapaneseBlock(nn.Module):
    def __init__(self, config, ext_layer=False):
        super().__init__()
        self.self_attn = GPTSanJapaneseLayerSelfAttention(config)
        self.feed_forward = GPTSanJapaneseLayerDenseFF(config) if ext_layer else GPTSanJapaneseLayerSparseFF(config)
    def forward(self, hidden_states: Optional[Tuple[torch.FloatTensor]], past_key_value: Optional[Tuple[torch.Tensor]] = None, attention_mask: Optional[torch.FloatTensor] = None,
    head_mask: Optional[torch.FloatTensor] = None, use_cache: Optional[bool] = False, output_attentions: Optional[bool] = False, output_router_tuple: Optional[bool] = False) -> Tuple[Union[torch.Tensor, Tuple[torch.Tensor]], ...]:
        atten_out = self.self_attn(hidden_states=hidden_states, past_key_value=past_key_value, attention_mask=attention_mask, head_mask=head_mask, use_cache=use_cache, output_attentions=output_attentions)
        attention_output = atten_out[0]
        if isinstance(self.feed_forward, GPTSanJapaneseLayerSparseFF):
            sparse_out = self.feed_forward(attention_output, output_router_tuple)
            if output_router_tuple: hidden, router_tuple = sparse_out
            else: hidden = sparse_out
        else: hidden = self.feed_forward(attention_output)
        outputs = (hidden,) + atten_out[1:]
        if isinstance(self.feed_forward, GPTSanJapaneseLayerSparseFF) and output_router_tuple: outputs += (router_tuple,)
        return outputs
class GPTSanJapanesePreTrainedModel(PreTrainedModel):
    config_class = GPTSanJapaneseConfig
    base_model_prefix = "gptsan_japanese"
    supports_gradient_checkpointing = False
    _no_split_modules = ["GPTSanJapaneseBlock"]
    _skip_keys_device_placement = "past_key_values"
    @property
    def dummy_inputs(self):
        input_ids = torch.tensor(DUMMY_INPUTS)
        input_mask = torch.tensor(DUMMY_MASK)
        dummy_inputs = {"input_ids": input_ids, "attention_mask": input_mask}
        return dummy_inputs
    def _init_weights(self, module):
        factor = self.config.initializer_factor
        if isinstance(module, nn.LayerNorm):
            module.weight.data.fill_(factor * 1.0)
            module.bias.data.zero_()
        elif isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=factor * ((self.config.d_model) ** -0.5))
            if hasattr(module, "bias") and module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding): module.weight.data.normal_(mean=0.0, std=factor * 1.0)
        elif isinstance(module, GPTSanJapaneseModel):
            module.embed_tokens.weight.data.normal_(mean=0.0, std=factor * 1.0)
            module.position_embeddings.weight.data.normal_(mean=0.0, std=factor * 1.0)
            if hasattr(module, "extra_position_embeddings") and module.extra_position_embeddings is not None: module.extra_position_embeddings.weight.data.normal_(mean=0.0, std=factor * 1.0)
        elif isinstance(module, (GPTSanJapaneseModel, GPTSanJapaneseForConditionalGeneration)):
            module.final_logits_bias.data.normal_(mean=0.0, std=factor * 1.0)
            if hasattr(module, "lm_head") and not self.config.tie_word_embeddings: module.lm_head.weight.data.normal_(mean=0.0, std=factor * 1.0)
        elif isinstance(module, GPTSanJapaneseDenseActDense):
            module.wi.weight.data.normal_(mean=0.0, std=factor * ((self.config.d_model) ** -0.5))
            if hasattr(module.wi, "bias") and module.wi.bias is not None: module.wi.bias.data.zero_()
            module.wo.weight.data.normal_(mean=0.0, std=factor * ((self.config.d_ff) ** -0.5))
            if hasattr(module.wo, "bias") and module.wo.bias is not None: module.wo.bias.data.zero_()
        elif isinstance(module, GPTSanJapaneseAttention):
            d_model = self.config.d_model
            key_value_proj_dim = self.config.d_model
            n_heads = self.config.num_heads
            module.k_proj.weight.data.normal_(mean=0.0, std=factor * ((d_model * key_value_proj_dim) ** -0.5))
            module.v_proj.weight.data.normal_(mean=0.0, std=factor * ((d_model * key_value_proj_dim) ** -0.5))
            module.q_proj.weight.data.normal_(mean=0.0, std=factor * ((d_model * key_value_proj_dim) ** -0.5))
            module.out_proj.weight.data.normal_(mean=0.0, std=factor * ((n_heads * key_value_proj_dim) ** -0.5))
        elif isinstance(module, GPTSanJapaneseSparseMLP):
            d_model = self.config.d_model
            key_value_proj_dim = self.config.d_model
            n_heads = self.config.num_heads
            module.router.classifier.weight.data.normal_(mean=0.0, std=factor * 1)
            for idx in range(self.config.num_experts):
                module.experts[f"expert_{idx}"].wi.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
                module.experts[f"expert_{idx}"].wo.weight.data.normal_(mean=0.0, std=factor * (d_model**-0.5))
    def _shift_right(self, input_ids):
        decoder_start_token_id = self.config.decoder_start_token_id
        pad_token_id = self.config.pad_token_id
        if decoder_start_token_id is None: raise ValueError("self.model.config.decoder_start_token_id has to be defined. In T5 it is usually set to the pad_token_id. See T5 docs for more information.")
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
GPTSAN_JAPANESE_START_DOCSTRING = r"""
    The [GPTSAN-japanese](https://github.com/tanreinama/GPTSAN) model was proposed in General-purpose Swich transformer
    based Japanese language model
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`GPTSanJapaneseConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
GPTSAN_JAPANESE_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. GPTSAN-japanese is a model that generates sentence
            continuations or predicts tokens at mask positions. Special tokens required for inputs to the model are
            automatically appended.
        attention_mask (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            An input that masks the Prefix part in the Prefix-LM input. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *prefix* input,
            - 0 for tokens that are *not-prefix* input.
        spout (`torch.Tensor` of shape `(batch_size, config.d_spout)`):
                This vector is transformed through an 8-layer FFN and can be used instead of `past_key_values`.
        past_key_values (`tuple(tuple(torch.FloatTensor))` of length `config.n_layers` with each tuple having 4 tensors of shape `(batch_size, num_heads, sequence_length - 1, embed_size_per_head)`):
            Contains precomputed key and value hidden states of the attention blocks. Can be used to speed up decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        decoder_inputs_embeds (`torch.FloatTensor` of shape `(batch_size, target_sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `decoder_input_ids` you can choose to directly pass an embedded
            representation. If `past_key_values` is used, optionally only the last `decoder_inputs_embeds` have to be
            input (see `past_key_values`). This is useful if you want more control over how to convert
            `decoder_input_ids` indices into associated vectors than the model's internal embedding lookup matrix.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        router_logits (`tuple(torch.FloatTensor)`, *optional*, returned when `output_router_logits=True` is passed or when `config.add_router_probs=True`):
            Tuple of `torch.FloatTensor` (one for each layer) of shape `(batch_size, sequence_length, num_experts)`.
            Router logits of the decoder model, useful to compute the auxiliary loss for Mixture of Experts models.
"""
@add_start_docstrings("The bare GPTSAN-japanese Model transformer outputting raw hidden-states without any specific head on top.", GPTSAN_JAPANESE_START_DOCSTRING)
class GPTSanJapaneseModel(GPTSanJapanesePreTrainedModel):
    def __init__(self, config: GPTSanJapaneseConfig):
        super().__init__(config)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.d_model)
        self.config = copy.deepcopy(config)
        self.embed_tokens = nn.Embedding(config.vocab_size, config.d_model)
        self.last_project = nn.Linear(config.d_model, config.d_model, bias=True)
        self.act = ACT2FN["swish"]
        self.blocks = torch.nn.ModuleList([])
        for _ in range(config.num_switch_layers): self.blocks.append(GPTSanJapaneseBlock(config))
        for _ in range(config.num_ext_layers): self.blocks.append(GPTSanJapaneseBlock(config, ext_layer=True))
        if config.num_ext_layers > 0: self.extra_position_embeddings = nn.Embedding(config.max_position_embeddings, config.d_model)
        if config.d_spout:
            spouts = []
            for _ in range(8):
                spouts.append(nn.Linear(config.d_spout, config.d_spout, bias=False))
                spouts.append(nn.Tanh())
            spouts.append(nn.Linear(config.d_spout, config.num_layers * 2 * config.d_model, bias=False))
            self.spout = nn.Sequential(*spouts)
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, new_embeddings): self.embed_tokens = new_embeddings
    @add_start_docstrings_to_model_forward(GPTSAN_JAPANESE_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.FloatTensor] = None,
    spout: Optional[torch.FloatTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, head_mask: Optional[torch.FloatTensor] = None,
    use_cache: Optional[bool] = False, inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, output_router_logits: Optional[bool] = None,
    num_precontext: Optional[torch.LongTensor] = None) -> Union[MoEModelOutputWithPastAndCrossAttentions, Tuple[torch.FloatTensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        device = self.position_embeddings.weight.device
        if input_ids is None: input_ids = torch.zeros([1, 1]).int().to(device)
        if inputs_embeds is not None: raise NotImplementedError("GPTSanJapaneseModel does not use `inputs_embeds`. Make sure to pass in `input_ids` instead.")
        num_pasts_contexts = 0
        num_batch = input_ids.shape[0]
        pasts_or_spout_value = None
        if past_key_values is not None: num_pasts_contexts = past_key_values[0][0].shape[2]
        elif self.config.d_spout and spout is not None: num_pasts_contexts += 1
        if self.config.d_spout and spout is not None and attention_mask is not None:
            attention_mask_with_spout = torch.ones(num_batch, attention_mask.shape[1] + 1, device=device)
            attention_mask_with_spout[:, 1:] -= 1 - attention_mask
            attention_mask = attention_mask_with_spout
        if num_precontext is not None:
            if not (len(num_precontext.shape) == 2 and num_precontext.shape[1] == 1): raise ValueError("num_precontext should be [batch, 1] size.")
            num_precontext = torch.reshape(num_precontext, [-1])
        else: num_precontext = torch.zeros([num_batch]).int().to(device)
        num_input_contexts = input_ids.shape[1]
        num_output_contexts = num_input_contexts + num_pasts_contexts
        hidden_states = self.embed_tokens(input_ids)
        if past_key_values is not None: pasts_or_spout_value = past_key_values
        elif self.config.d_spout and spout is not None:
            pasts_or_spout_value = self.spout(spout)
            pasts_or_spout_value = torch.reshape(pasts_or_spout_value, [num_batch, self.config.num_layers, 2, self.config.num_heads, num_pasts_contexts, self.config.d_model // self.config.num_heads])
            pasts_or_spout_value = torch.split(pasts_or_spout_value, [1] * self.config.num_layers, dim=1)
            pasts_or_spout_value = tuple(tuple([b.squeeze(1) for b in torch.split(a.squeeze(1), [1, 1], dim=1)]) for a in pasts_or_spout_value)
        else: pasts_or_spout_value = [None] * self.config.num_layers
        token_position = torch.arange(num_input_contexts).to(device) + num_pasts_contexts
        if attention_mask is None: attention_mask = torch.ones(num_batch, num_input_contexts, device=device)
        gather_position = ((torch.zeros((num_batch, self.config.d_model, num_input_contexts)).to(device) + token_position.unsqueeze(0)).transpose(1, 2).long())
        gather_position -= (1 - attention_mask).argmin(dim=-1).unsqueeze(1).unsqueeze(2)
        gather_position = torch.clip(gather_position, num_pasts_contexts, self.config.max_position_embeddings - 1)
        for i in range(num_batch): hidden_states[i] += torch.gather(self.position_embeddings.weight, dim=0, index=gather_position[i])
        causal_mask = (torch.tril(torch.ones((num_output_contexts, num_output_contexts), dtype=torch.uint8)).view(1, 1, num_output_contexts, num_output_contexts).to(device))
        prefix_lm_mask = causal_mask[:, :, -num_input_contexts:, :]
        if token_type_ids is not None:
            token_type_ids = token_type_ids.unsqueeze(1).unsqueeze(2)
            prefix_lm_mask = ((prefix_lm_mask + token_type_ids) > 0).float()
        extended_attention_mask = prefix_lm_mask * attention_mask.unsqueeze(1).unsqueeze(2)
        if head_mask is not None: head_mask = self.get_head_mask(head_mask, self.config.num_switch_layers + self.config.num_ext_layers)
        present_key_value_states = () if self.config.use_cache or use_cache else None
        all_hidden_states = () if self.config.output_hidden_states or output_hidden_states else None
        all_attentions = () if self.config.output_attentions or output_attentions else None
        all_router_probs = () if self.config.output_router_logits or output_router_logits else None
        for layer, past in enumerate(pasts_or_spout_value):
            if layer == self.config.num_switch_layers:
                if self.config.num_ext_layers > 0:
                    for i in range(num_batch): hidden_states[i] += torch.gather(self.extra_position_embeddings.weight, dim=0, index=gather_position[i])
            output_router_tuple = (self.config.output_router_logits or output_router_logits) and layer < self.config.num_switch_layers
            block_output = self.blocks[layer](hidden_states=hidden_states, past_key_value=past, attention_mask=extended_attention_mask, head_mask=head_mask,
            use_cache=self.config.use_cache or use_cache, output_attentions=self.config.output_attentions or output_attentions, output_router_tuple=output_router_tuple)
            outpos = 0
            hidden_states = block_output[outpos]
            if self.config.output_hidden_states or output_hidden_states: all_hidden_states += (hidden_states,)
            if self.config.use_cache or use_cache:
                outpos += 1
                present = block_output[outpos]
                present_key_value_states += (present,)
            if self.config.output_attentions or output_attentions:
                outpos += 1
                attention_probs = block_output[outpos]
                all_attentions += (attention_probs,)
            if output_router_tuple:
                outpos += 1
                router_tuple = block_output[outpos]
                all_router_probs.append(router_tuple[0])
        hidden_states = self.last_project(hidden_states)
        hidden_states = self.act(hidden_states)
        if self.config.output_hidden_states or output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, present_key_value_states, all_hidden_states, all_attentions, all_router_probs] if v is not None)
        return MoEModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=present_key_value_states, hidden_states=all_hidden_states, attentions=all_attentions, router_probs=all_router_probs)
@add_start_docstrings("The bare GPTSAN-japanese Model with a language modeling head.", GPTSAN_JAPANESE_START_DOCSTRING)
class GPTSanJapaneseForConditionalGeneration(GPTSanJapanesePreTrainedModel):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config: GPTSanJapaneseConfig):
        super().__init__(config)
        self.model = GPTSanJapaneseModel(config)
        self.register_buffer("final_logits_bias", torch.zeros([1, config.vocab_size]))
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        if not self.config.torchscript: self.lm_head.weight = self.model.embed_tokens.weight
    @add_start_docstrings_to_model_forward(GPTSAN_JAPANESE_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.FloatTensor] = None,
    spout: Optional[torch.FloatTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, head_mask: Optional[torch.FloatTensor] = None,
    use_cache: Optional[bool] = False, inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, output_router_logits: Optional[bool] = None, labels: Optional[torch.LongTensor] = None) -> Union[Tuple[torch.FloatTensor], MoECausalLMOutputWithPast]:
        SEG_TOKEN = self.config.separator_token_id
        use_cache = use_cache or self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        model_return_dict = True
        num_precontext = None
        if input_ids is not None:
            num_batch = input_ids.shape[0]
            num_precontext = torch.zeros([num_batch]).int().to(input_ids.device)
            where_separators = torch.where(input_ids == SEG_TOKEN)
            num_precontext[where_separators[0]] += where_separators[1]
            num_precontext = num_precontext.unsqueeze(1)
        outputs = self.model(input_ids, attention_mask, token_type_ids, spout, past_key_values, head_mask, use_cache, inputs_embeds, decoder_inputs_embeds,
        output_attentions, output_hidden_states, model_return_dict, output_router_logits, num_precontext)
        lm_logits = self.lm_head(outputs[0])
        if lm_logits.shape[-1] == self.final_logits_bias.shape[-1]: lm_logits = lm_logits + self.final_logits_bias
        loss = None
        z_loss = None
        router_probs = None
        aux_loss = None
        if labels is not None:
            labels = labels.to(lm_logits.device)
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            if output_router_logits:
                router_logits, expert_indexes = self._unpack_router_logits(outputs.router_probs)
                z_loss = router_z_loss_func(router_logits)
                router_probs = nn.Softmax(dim=-1)(router_logits)
                aux_loss = load_balancing_loss_func(router_probs, expert_indexes)
            loss = loss_fct(lm_logits.view(-1, lm_logits.size(-1)), labels.view(-1))
        if not return_dict: return tuple(v for v in [loss, lm_logits, outputs.past_key_values, outputs.hidden_states, outputs.router_probs, z_loss, aux_loss] if v is not None)
        return MoECausalLMOutputWithPast(loss=loss, logits=lm_logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions,
        router_logits=outputs.router_probs, z_loss=z_loss, aux_loss=aux_loss)
    def prepare_inputs_for_generation(self, input_ids: torch.LongTensor, attention_mask: torch.FloatTensor, token_type_ids: Optional[torch.FloatTensor] = None, spout: Optional[Union[List, torch.FloatTensor]] = None,
    past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, **kwargs):
        if isinstance(spout, list):
            spout = torch.tensor(spout).float()
            if input_ids is not None: spout = spout.to(input_ids.device)
        if past_key_values is not None: return {"input_ids": input_ids[:, -1:] if input_ids is not None else None, "attention_mask": attention_mask,
        "token_type_ids": token_type_ids[:, -1:] if token_type_ids is not None else None, "spout": spout, "past_key_values": past_key_values}
        return {"input_ids": input_ids, "attention_mask": attention_mask, "token_type_ids": token_type_ids, "spout": spout, "past_key_values": None}
    def prepare_decoder_input_ids_from_labels(self, labels: torch.Tensor): return self._shift_right(labels)
    def resize_token_embeddings(self, new_num_tokens: int, pad_to_multiple_of: Optional[int] = None) -> nn.Embedding:
        new_embeddings = super().resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        self._resize_final_logits_bias(new_embeddings.weight.shape[0])
        return new_embeddings
    def _resize_final_logits_bias(self, new_num_tokens: int) -> None:
        old_num_tokens = self.final_logits_bias.shape[-1]
        if new_num_tokens <= old_num_tokens: new_bias = self.final_logits_bias[:, :new_num_tokens]
        else:
            extra_bias = torch.zeros((1, new_num_tokens - old_num_tokens), device=self.final_logits_bias.device)
            new_bias = torch.cat([self.final_logits_bias, extra_bias], dim=1)
        self.register_buffer("final_logits_bias", new_bias)
    def get_input_embeddings(self): return self.model.get_input_embeddings()
    def set_input_embeddings(self, new_embeddings): self.model.set_input_embeddings(new_embeddings)
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def get_output_embeddings(self): return self.lm_head
    def _unpack_router_logits(self, router_outputs):
        total_router_logits = []
        total_expert_indexes = []
        for router_output in router_outputs:
            if len(router_output[0].shape) > 1:
                router_logits, expert_indexes = router_output
                total_router_logits.append(router_logits)
                total_expert_indexes.append(expert_indexes)
        return torch.cat(total_router_logits, dim=1), torch.cat(total_expert_indexes, dim=1)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
