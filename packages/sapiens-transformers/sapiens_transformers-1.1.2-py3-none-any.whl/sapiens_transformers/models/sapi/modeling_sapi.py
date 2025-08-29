"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch.nn import LayerNorm, functional as Functional, Module, Linear, Embedding, ModuleList, Dropout
from typing import Union, List, Optional, Tuple
from torch import Size, Tensor
from torch import (is_autocast_enabled as t_is_autocast_enabled, cuda as t_cuda, get_autocast_gpu_dtype as t_get_autocast_gpu_dtype, amp as t_amp, Tensor as t_Tensor,
cat as t_cat, LongTensor as t_LongTensor, matmul as t_matmul, float32 as t_float32, FloatTensor as t_FloatTensor, dtype as t_dtype, device as t_device, full as t_full, triu as t_triu,
arange as t_arange, max as t_max, no_grad as t_no_grad, autocast as t_autocast, finfo as t_finfo, contiguous_format as t_contiguous_format, eq as t_eq, long as t_long, int as t_int)
from ...cache_utils import Cache, StaticCache
from .configuration_sapi import SAPIConfig
from ...utils import (is_flash_attn_greater_or_equal_2_10, add_start_docstrings, add_start_docstrings_to_model_forward)
from ...modeling_outputs import (BaseModelOutputWithPast, CausalLMOutputWithPast, SequenceClassifierOutputWithPast, TokenClassifierOutput, QuestionAnsweringModelOutput)
_CONFIG_FOR_DOC = "SAPIConfig"
class SAPILayerNorm1P(LayerNorm):
    def __init__(self, normalized_shape: Union[int, List[int], Size], eps: float = 1e-5, elementwise_affine: bool = True, bias: bool = True, device=None, dtype=None): super().__init__(normalized_shape, eps, elementwise_affine, bias, device, dtype)
    def forward(self, input: Tensor) -> Tensor:
        def _cast_if_autocast_enabled(*args):
            if not t_is_autocast_enabled(): return args
            else: return t_cuda.amp.autocast_mode._cast(args, t_get_autocast_gpu_dtype())
        args = _cast_if_autocast_enabled(input, self.normalized_shape, self.weight + 1, self.bias, self.eps)
        with t_amp.autocast('cuda', enabled=False): return Functional.layer_norm(*args)
from ...pytorch_utils import ALL_LAYERNORM_LAYERS
ALL_LAYERNORM_LAYERS.append(SAPILayerNorm1P)
class SAPIMLP(Module):
    def __init__(self, config):
        super().__init__()
        self.config, self.hidden_size = config, config.hidden_size
        from ...activations import ACT2FN
        self.intermediate_size, self.act_fn = config.intermediate_size, ACT2FN[config.hidden_act]
        self.up_proj, self.down_proj = Linear(self.hidden_size, self.intermediate_size, bias=config.mlp_bias), Linear(self.intermediate_size, self.hidden_size, bias=config.mlp_bias)
    def forward(self, x): return self.down_proj(self.act_fn(self.up_proj(x)))
def repeat_kv(hidden_states: t_Tensor, n_rep: int) -> t_Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    return hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim).reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
def apply_rotary_pos_emb(q=None, k=None, cos=None, sin=None, position_ids=None, unsqueeze_dim=1):
    cos, sin, x, y = cos.unsqueeze(unsqueeze_dim), sin.unsqueeze(unsqueeze_dim), q, k
    rot_dim = cos.shape[-1]
    x, x_pass = x[..., :rot_dim], x[..., rot_dim:]
    y, y_pass = y[..., :rot_dim], y[..., rot_dim:]
    def rotate_half(x): return t_cat((-x[..., x.shape[-1] // 2 :], x[..., : x.shape[-1] // 2]), dim=-1)
    x_embed, y_embed = (x * cos) + (rotate_half(x) * sin), (y * cos) + (rotate_half(y) * sin)
    return t_cat((x_embed, x_pass), dim=-1), t_cat((y_embed, y_pass), dim=-1)
class SAPIAttention(Module):
    def __init__(self, config: SAPIConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config, self.layer_idx = config, layer_idx
        self.attention_dropout, self.hidden_size = config.attention_dropout, config.hidden_size
        self.num_heads, self.head_dim = config.num_attention_heads, config.head_dim
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings, self.rope_theta = config.max_position_embeddings, config.rope_theta
        self.partial_rotary_factor, self.is_causal = config.partial_rotary_factor, True
        self.q_proj, self.k_proj = Linear(self.hidden_size, self.num_heads * self.head_dim, bias=config.attention_bias), Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias)
        self.v_proj, self.o_proj = Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias), Linear(self.head_dim * self.num_heads, self.hidden_size, bias=config.attention_bias)
    def forward(self, hidden_states: t_Tensor, position_embeddings: Tuple[t_Tensor, t_Tensor], attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None,
    past_key_value: Optional[Cache] = None, output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[t_LongTensor] = None) -> Tuple[t_Tensor, Optional[t_Tensor], Optional[Tuple[t_Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states = self.q_proj(hidden_states), self.k_proj(hidden_states)
        value_states, query_states = self.v_proj(hidden_states), query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states, value_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is not None: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        from math import sqrt
        attn_weights = t_matmul(query_states, key_states.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights = Functional.dropout(Functional.softmax(attn_weights, dim=-1, dtype=t_float32).to(query_states.dtype), p=self.attention_dropout, training=self.training)
        attn_output = self.o_proj(t_matmul(attn_weights, value_states).transpose(1, 2).contiguous().reshape(bsz, q_len, -1))
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class SAPIFlashAttention2(SAPIAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: t_Tensor, position_embeddings: Tuple[t_Tensor, t_Tensor], attention_mask: Optional[t_LongTensor] = None,
    position_ids: Optional[t_LongTensor] = None, past_key_value: Optional[Cache] = None, output_attentions: bool = False, use_cache: bool = False,
    cache_position: Optional[t_LongTensor] = None) -> Tuple[t_Tensor, Optional[t_Tensor], Optional[Tuple[t_Tensor]]]:
        if isinstance(past_key_value, StaticCache): raise ValueError("`static` cache implementation is not compatible with `attn_implementation==flash_attention_2` make sure to use `sdpa` in the mean time")
        output_attentions = False
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states = self.q_proj(hidden_states), self.k_proj(hidden_states)
        value_states, query_states = self.v_proj(hidden_states), query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states, value_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is not None: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        query_states, key_states = query_states.transpose(1, 2), key_states.transpose(1, 2)
        value_states, dropout_rate, input_dtype = value_states.transpose(1, 2), self.attention_dropout if self.training else 0.0, query_states.dtype
        if input_dtype == t_float32:
            if t_is_autocast_enabled(): target_dtype = t_get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            query_states, key_states, value_states = query_states.to(target_dtype), key_states.to(target_dtype), value_states.to(target_dtype)
        from ...modeling_flash_attention_utils import _flash_attention_forward
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, position_ids=position_ids, dropout=dropout_rate,
        sliding_window=getattr(self, "sliding_window", None), use_top_left_mask=self._flash_attn_uses_top_left_mask, is_causal=self.is_causal)
        attn_output = self.o_proj(attn_output.reshape(bsz, q_len, -1).contiguous())
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class SAPISdpaAttention(SAPIAttention):
    def forward(self, hidden_states: t_Tensor, position_embeddings: Tuple[t_Tensor, t_Tensor], attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None,
    past_key_value: Optional[Cache] = None, output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[t_LongTensor] = None,
    **kwargs) -> Tuple[t_Tensor, Optional[t_Tensor], Optional[Tuple[t_Tensor]]]:
        if output_attentions:
            return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions,
            use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states = self.q_proj(hidden_states), self.k_proj(hidden_states)
        value_states, query_states = self.v_proj(hidden_states), query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states, value_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is not None: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states, causal_mask = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups), attention_mask
        if attention_mask is not None: causal_mask = causal_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and causal_mask is not None: query_states, key_states, value_states = query_states.contiguous(), key_states.contiguous(), value_states.contiguous()
        is_causal = True if causal_mask is None and q_len > 1 else False
        attn_output = self.o_proj(Functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.attention_dropout if self.training else 0.0, is_causal=is_causal).transpose(1, 2).contiguous().view(bsz, q_len, -1))
        return attn_output, None, past_key_value
SAPI_ATTENTION_CLASSES = {"eager": SAPIAttention, "flash_attention_2": SAPIFlashAttention2, "sdpa": SAPISdpaAttention}
class SAPIDecoderLayer(Module):
    def __init__(self, config: SAPIConfig, layer_idx: int):
        super().__init__()
        self.hidden_size, self.self_attn = config.hidden_size, SAPI_ATTENTION_CLASSES[config._attn_implementation](config=config, layer_idx=layer_idx)
        self.mlp, self.input_layernorm, self.post_attention_layernorm = SAPIMLP(config), SAPILayerNorm1P(config.hidden_size, eps=config.norm_eps), SAPILayerNorm1P(config.hidden_size, eps=config.norm_eps)
    def forward(self, hidden_states: t_Tensor, attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[t_LongTensor] = None, position_embeddings: Optional[Tuple[t_Tensor, t_Tensor]] = None,
    **kwargs) -> Tuple[t_FloatTensor, Optional[Tuple[t_FloatTensor, t_FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids,
        past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings, **kwargs)
        hidden_states = residual + hidden_states
        residual = hidden_states
        outputs = (residual + self.mlp(self.post_attention_layernorm(hidden_states)),)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
SAPI_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SAPIConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
SAPI_INPUTS_DOCSTRING = r"""
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
from ...modeling_utils import PreTrainedModel
@add_start_docstrings("The bare SAPI Model outputting raw hidden-states without any specific head on top.", SAPI_START_DOCSTRING)
class SAPIPreTrainedModel(PreTrainedModel):
    config_class, base_model_prefix, supports_gradient_checkpointing = SAPIConfig, "model", True
    _no_split_modules, _skip_keys_device_placement = ["SAPIDecoderLayer"], ["past_key_values"]
    _supports_flash_attn_2, _supports_sdpa, _supports_cache_class, _supports_quantized_cache, _supports_static_cache = True, True, True, True, True
    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: t_Tensor, sequence_length: int, target_length: int, dtype: t_dtype, device: t_device,
min_dtype: float, cache_position: t_Tensor, batch_size: int):
    if attention_mask is not None and attention_mask.dim() == 4: causal_mask = attention_mask
    else:
        causal_mask = t_full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != 1: causal_mask = t_triu(causal_mask, diagonal=1)
        causal_mask *= t_arange(target_length, device=device) > cache_position.reshape(-1, 1)
        causal_mask = causal_mask[None, None, :, :].expand(batch_size, 1, -1, -1)
        if attention_mask is not None:
            causal_mask, mask_length = causal_mask.clone(), attention_mask.shape[-1]
            causal_mask[:, :, :, :mask_length] = causal_mask[:, :, :, :mask_length].masked_fill(causal_mask[:, :, :, :mask_length] + attention_mask[:, None, None, :] == 0, min_dtype)
    return causal_mask
class SAPIRotaryEmbedding(Module):
    def __init__(self, config: SAPIConfig, device=None):
        super().__init__()
        self.rope_type, self.max_seq_len_cached = "default", config.max_position_embeddings
        self.original_max_seq_len, self.config, self.rope_kwargs = config.max_position_embeddings, config, None
        from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
        self.rope_init_fn = ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.original_inv_freq = self.inv_freq
    def _dynamic_frequency_update(self, position_ids=None, device=None):
        seq_len = t_max(position_ids) + 1
        if seq_len > self.max_seq_len_cached:
            inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, seq_len=seq_len, **self.rope_kwargs)
            self.register_buffer("inv_freq", inv_freq, persistent=False)
            self.max_seq_len_cached = seq_len
        if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:
            self.register_buffer("inv_freq", self.original_inv_freq, persistent=False)
            self.max_seq_len_cached = self.original_max_seq_len
    @t_no_grad()
    def forward(self, x=None, position_ids=None):
        if "dynamic" in self.rope_type: self._dynamic_frequency_update(position_ids, device=x.device)
        inv_freq_expanded, position_ids_expanded, device_type = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1), position_ids[:, None, :].float(), x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with t_autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = t_cat((freqs, freqs), dim=-1)
            cos, sin = emb.cos(), emb.sin()
        return (cos * self.attention_scaling).to(dtype=x.dtype), (sin * self.attention_scaling).to(dtype=x.dtype)
@add_start_docstrings("The bare SAPI Model outputting raw hidden-states without any specific head on top.", SAPI_START_DOCSTRING)
class SAPIModel(SAPIPreTrainedModel):
    def __init__(self, config: SAPIConfig):
        super().__init__(config)
        self.padding_idx, self.vocab_size = config.pad_token_id, config.vocab_size
        self.embed_tokens, self.layers = Embedding(config.vocab_size, config.hidden_size, self.padding_idx), ModuleList([SAPIDecoderLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)])
        self.norm, self.rotary_emb, self.gradient_checkpointing = SAPILayerNorm1P(config.hidden_size, eps=config.norm_eps), SAPIRotaryEmbedding(config=config), False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value=None): self.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPI_INPUTS_DOCSTRING)
    def forward(self, input_ids: t_LongTensor = None, attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None, past_key_values: Optional[Union[Cache, List[t_FloatTensor]]] = None,
    inputs_embeds: Optional[t_FloatTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[t_LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache, return_dict = use_cache if use_cache is not None else self.config.use_cache, return_dict if return_dict is not None else self.config.use_return_dict
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training and use_cache: use_cache = False
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        if cache_position is None: cache_position = t_arange(inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        causal_mask, hidden_states = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions), inputs_embeds
        position_embeddings = self.rotary_emb(hidden_states, position_ids)
        all_hidden_states, all_self_attns, next_decoder_cache = () if output_hidden_states else None, () if output_attentions else None, None
        for decoder_layer in self.layers:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, causal_mask, position_ids, past_key_values, output_attentions, use_cache, cache_position, position_embeddings)
            else: layer_outputs = decoder_layer(hidden_states, attention_mask=causal_mask, position_ids=position_ids, past_key_value=past_key_values, output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache = layer_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (layer_outputs[1],)
        hidden_states = self.norm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns)
    def _update_causal_mask(self, attention_mask: t_Tensor, input_tensor: t_Tensor, cache_position: t_Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens, using_static_cache = past_key_values.get_seq_length() if past_key_values is not None else 0, isinstance(past_key_values, StaticCache)
        from ...modeling_attn_mask_utils import AttentionMaskConverter
        if self.config._attn_implementation == "sdpa" and not using_static_cache and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype, sequence_length = t_finfo(dtype).min, input_tensor.shape[1]
        if using_static_cache: target_length = past_key_values.get_max_length()
        else: target_length = (attention_mask.shape[-1] if isinstance(attention_mask, t_Tensor) else past_seen_tokens + sequence_length + 1)
        causal_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length, dtype=dtype,
        device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): causal_mask = AttentionMaskConverter._unmask_unattended(causal_mask, min_dtype)
        return causal_mask
from ...generation import GenerationMixin
class SAPIForCausalLM(SAPIPreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        super().__init__(config)
        self.model, self.vocab_size = SAPIModel(config), config.vocab_size
        self.lm_head = Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings=None): self.lm_head = new_embeddings
    def set_decoder(self, decoder=None): self.model = decoder
    def get_decoder(self): return self.model
    @add_start_docstrings_to_model_forward(SAPI_INPUTS_DOCSTRING)
    def forward(self, input_ids: t_LongTensor = None, attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None, past_key_values: Optional[Union[Cache, List[t_FloatTensor]]] = None,
    inputs_embeds: Optional[t_FloatTensor] = None, labels: Optional[t_LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[t_LongTensor] = None,
    num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position)
        logits, loss = self.lm_head(outputs[0][:, -num_logits_to_keep:, :]).float(), None
        if labels is not None:
            logits = logits.float()
            shift_labels, loss_fct = labels[..., 1:].contiguous(), CrossEntropyLoss()
            shift_logits, shift_labels = logits[..., :-1, :].contiguous().view(-1, self.config.vocab_size), shift_labels.view(-1)
            loss = loss_fct(shift_logits, shift_labels.to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return CausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def prepare_inputs_for_generation(self, input_ids=None, past_key_values=None, attention_mask=None, inputs_embeds=None, cache_position=None, position_ids=None, use_cache=True, num_logits_to_keep=None, **kwargs):
        if past_key_values is not None:
            if inputs_embeds is not None: input_ids = input_ids[:, -cache_position.shape[0] :]
            elif input_ids.shape[1] != cache_position.shape[0]: input_ids = input_ids[:, cache_position]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :].clone(memory_format=t_contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=t_contiguous_format), "inputs_embeds": None}
        if isinstance(past_key_values, StaticCache) and attention_mask.ndim == 2:
            if model_inputs["inputs_embeds"] is not None:
                batch_size, sequence_length, _ = model_inputs["inputs_embeds"].shape
                device = model_inputs["inputs_embeds"].device
            else:
                batch_size, sequence_length = model_inputs["input_ids"].shape
                device = model_inputs["input_ids"].device
            min_dtype = t_finfo(self.lm_head.weight.dtype).min
            attention_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=past_key_values.get_max_length(),
            dtype=dtype, device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=batch_size)
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
        return model_inputs
from torch.nn import CrossEntropyLoss
@add_start_docstrings("""
    The SAPI Model transformer with a sequence classification head on top (linear layer).
    [`SAPIForSequenceClassification`] uses the last token in order to do the classification, as other causal models
    (e.g. GPT-2) do.
    Since it does classification on the last token, it requires to know the position of the last token. If a
    `pad_token_id` is defined in the configuration, it finds the last token that is not a padding token in each row. If
    no `pad_token_id` is defined, it simply takes the last value in each row of the batch. Since it cannot guess the
    padding tokens when `inputs_embeds` are passed instead of `input_ids`, it does the same (take the last value in
    each row of the batch).
""", SAPI_START_DOCSTRING)
class SAPIForSequenceClassification(SAPIPreTrainedModel):
    def __init__(self, config=None):
        super().__init__(config)
        self.num_labels, self.model = config.num_labels, SAPIModel(config)
        self.score = Linear(config.hidden_size, self.num_labels, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPI_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[t_LongTensor] = None, attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None,
    past_key_values: Optional[Union[Cache, List[t_FloatTensor]]] = None, inputs_embeds: Optional[t_FloatTensor] = None, labels: Optional[t_LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, SequenceClassifierOutputWithPast]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        transformer_outputs = self.model(input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits = self.score(transformer_outputs[0])
        if input_ids is not None: batch_size = input_ids.shape[0]
        else: batch_size = inputs_embeds.shape[0]
        if self.config.pad_token_id is None and batch_size != 1: raise ValueError("Cannot handle batch sizes > 1 if no padding token is defined.")
        if self.config.pad_token_id is None: sequence_lengths = -1
        else:
            if input_ids is not None: sequence_lengths = ((t_eq(input_ids, self.config.pad_token_id).int().argmax(-1) - 1) % input_ids.shape[-1]).to(logits.device)
            else: sequence_lengths = -1
        pooled_logits, loss = logits[t_arange(batch_size, device=logits.device), sequence_lengths], None
        if labels is not None:
            labels = labels.to(logits.device)
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == t_long or labels.dtype == t_int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            from torch.nn import MSELoss, BCEWithLogitsLoss
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(pooled_logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(pooled_logits, labels)
            elif self.config.problem_type == "single_label_classification": loss = CrossEntropyLoss()(pooled_logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification": loss = BCEWithLogitsLoss()(pooled_logits, labels)
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutputWithPast(loss=loss, logits=pooled_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states, attentions=transformer_outputs.attentions)
@add_start_docstrings("The SAPI Model transformer with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", SAPI_START_DOCSTRING)
class SAPIForTokenClassification(SAPIPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels, self.model = config.num_labels, SAPIModel(config)
        if getattr(config, "classifier_dropout", None) is not None: classifier_dropout = config.classifier_dropout
        elif getattr(config, "hidden_dropout", None) is not None: classifier_dropout = config.hidden_dropout
        else: classifier_dropout = 0.1
        self.dropout, self.score = Dropout(classifier_dropout), Linear(config.hidden_size, config.num_labels)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPI_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[t_LongTensor] = None, attention_mask: Optional[t_Tensor] = None, position_ids: Optional[t_LongTensor] = None,
    past_key_values: Optional[List[t_FloatTensor]] = None, inputs_embeds: Optional[t_FloatTensor] = None, labels: Optional[t_LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, TokenClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits, loss = self.score(self.dropout(outputs[0])), None
        if labels is not None: loss = CrossEntropyLoss()(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("The SAPI Model transformer with a span classification head on top for extractive question-answering tasks like SQuAD (a linear layer on top of the hidden-states output to compute `span start logits` and `span end logits`).", SAPI_START_DOCSTRING)
class SAPIForQuestionAnswering(SAPIPreTrainedModel):
    base_model_prefix = "transformer"
    def __init__(self, config=None):
        super().__init__(config)
        self.transformer, self.qa_outputs = SAPIModel(config), Linear(config.hidden_size, 2)
        self.post_init()
    def get_input_embeddings(self): return self.transformer.embed_tokens
    def set_input_embeddings(self, value=None): self.transformer.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPI_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[t_LongTensor] = None, attention_mask: Optional[t_FloatTensor] = None, position_ids: Optional[t_LongTensor] = None,
    past_key_values: Optional[Union[Cache, List[t_FloatTensor]]] = None, inputs_embeds: Optional[t_FloatTensor] = None, start_positions: Optional[t_LongTensor] = None,
    end_positions: Optional[t_LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, QuestionAnsweringModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.transformer(input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        start_logits, end_logits = self.qa_outputs(outputs[0]).split(1, dim=-1)
        start_logits, end_logits, total_loss = start_logits.squeeze(-1).contiguous(), end_logits.squeeze(-1).contiguous(), None
        if start_positions is not None and end_positions is not None:
            if len(start_positions.size()) > 1: start_positions = start_positions.squeeze(-1).to(start_logits.device)
            if len(end_positions.size()) > 1: end_positions = end_positions.squeeze(-1).to(end_logits.device)
            ignored_index = start_logits.size(1)
            start_positions, end_positions = start_positions.clamp(0, ignored_index), end_positions.clamp(0, ignored_index)
            loss_fct = CrossEntropyLoss(ignore_index=ignored_index)
            start_loss, end_loss = loss_fct(start_logits, start_positions), loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2
        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output
        return QuestionAnsweringModelOutput(loss=total_loss, start_logits=start_logits, end_logits=end_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
