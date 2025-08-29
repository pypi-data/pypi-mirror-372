"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, add_start_docstrings, add_start_docstrings_to_model_forward)
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
from torch import (ones as sapiens_ones, float32 as sapiens_float32, rsqrt as sapiens_rsqrt, max as sapiens_max, no_grad as sapiens_no_grad, autocast as sapiens_autocast,
cat as sapiens_cat, Tensor as sapiens_Tensor, LongTensor as sapiens_LongTensor, matmul as sapiens_matmul, ones_like as sapiens_ones_like, is_autocast_enabled as sapiens_is_autocast_enabled,
get_autocast_gpu_dtype as sapiens_get_autocast_gpu_dtype, FloatTensor as sapiens_FloatTensor, dtype as sapiens_dtype, device as sapiens_device, full as sapiens_full, triu as sapiens_triu,
arange as sapiens_arange, finfo as sapiens_finfo, contiguous_format as sapiens_contiguous_format, eq as sapiens_eq, long as sapiens_long, int as sapiens_int)
from torch.nn import (Module as SAPIENSModule, Parameter as SAPIENSParameter, Linear as SAPIENSLinear, functional as SAPIENSFunctional,
Embedding as SAPIENSEmbedding, ModuleList as SAPIENSModuleList, Dropout as SAPIENSDropout)
_CHECKPOINT_FOR_DOC, _CONFIG_FOR_DOC = "Sapiens/Semantic_AI_with_Pretrained_Integration/SAPI", "SapiensConfig"
class SapiensRMSNorm(SAPIENSModule):
    def __init__(self, hidden_size=5128, eps=1e-6):
        super().__init__()
        self.variance_epsilon, self.weight = eps, SAPIENSParameter(sapiens_ones(hidden_size))
    def forward(self, hidden_states=None):
        input_dtype = hidden_states.dtype
        _x, _y, _z = 2, -1, True
        hidden_states = hidden_states.to(sapiens_float32)
        hidden_states = hidden_states * sapiens_rsqrt(hidden_states.pow(_x).mean(_y, keepdim=_z) + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)
    def extra_repr(self): return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"
from typing import Optional, Tuple, List, Union
from .configuration_sapiens import SapiensConfig
class SapiensRotaryEmbedding(SAPIENSModule):
    def __init__(self, dim=None, max_position_embeddings=43512, base=20000, device=None, scaling_factor=1.01, rope_type="default", config: Optional[SapiensConfig] = None):
        super().__init__()
        self.rope_kwargs = dict()
        if config is None:
            self.rope_type, self.max_seq_len_cached = rope_type, max_position_embeddings
            self.original_max_seq_len, self.rope_kwargs = max_position_embeddings, {"rope_type": rope_type, "factor": scaling_factor, "dim": dim, "base": base, "max_position_embeddings": max_position_embeddings}
        else:
            if config.rope_scaling is not None: self.rope_type = config.rope_scaling.get("rope_type", config.rope_scaling.get("type"))
            else: self.rope_type = "default"
            self.max_seq_len_cached, self.original_max_seq_len = config.max_position_embeddings, config.max_position_embeddings
        from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
        self.config, self.rope_init_fn = config, ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, **self.rope_kwargs)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.original_inv_freq = self.inv_freq
    def _dynamic_frequency_update(self, position_ids=None, device=None):
        seq_len = sapiens_max(position_ids) + 1
        if self.max_seq_len_cached < seq_len:
            inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device, seq_len=seq_len, **self.rope_kwargs)
            self.register_buffer("inv_freq", inv_freq, persistent=False)
            self.max_seq_len_cached = seq_len
        if seq_len < self.original_max_seq_len and self.max_seq_len_cached > self.original_max_seq_len:
            self.register_buffer("inv_freq", self.original_inv_freq, persistent=False)
            self.max_seq_len_cached = self.original_max_seq_len
    @sapiens_no_grad()
    def forward(self, x=None, position_ids={}):
        if "dynamic" in self.rope_type: self._dynamic_frequency_update(position_ids, device=x.device)
        inv_freq_expanded, position_ids_expanded = self.inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1), position_ids[:, None, :].float()
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with sapiens_autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = sapiens_cat((freqs, freqs), dim=-1)
            cos, sin = emb.cos(), emb.sin()
        cos, sin = cos * self.attention_scaling, sin * self.attention_scaling
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)
class SapiensMLP(SAPIENSModule):
    def __init__(self, config=None):
        super().__init__()
        from ...activations import ACT2FN
        self.hidden_size, self.intermediate_size = config.hidden_size, config.intermediate_size
        self.down_proj, self.act_fn = SAPIENSLinear(self.intermediate_size, self.hidden_size, bias=False), ACT2FN[config.hidden_act]
        self.gate_proj, self.up_proj = SAPIENSLinear(self.hidden_size, self.intermediate_size, bias=False), SAPIENSLinear(self.hidden_size, self.intermediate_size, bias=False)
    def forward(self, hidden_state=None): return self.down_proj(self.act_fn(self.gate_proj(hidden_state)) * self.up_proj(hidden_state))
def apply_rotary_pos_emb(q=None, k=None, cos=None, sin=None, position_ids=None, unsqueeze_dim=1):
    def rotate_half(x): return sapiens_cat((-x[..., x.shape[-1] // 2 :], x[..., : x.shape[-1] // 2]), dim=-1)
    cos, sin = cos.unsqueeze(unsqueeze_dim), sin.unsqueeze(unsqueeze_dim)
    return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)
def repeat_kv(hidden_states: sapiens_Tensor, n_rep: int) -> sapiens_Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
from ...cache_utils import Cache, DynamicCache, StaticCache
class SapiensAttention(SAPIENSModule):
    def __init__(self, config: SapiensConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config, self.layer_idx = config, layer_idx
        self.hidden_size, self.num_heads = config.hidden_size, config.num_attention_heads
        self.head_dim, self.num_key_value_heads = self.hidden_size // self.num_heads, config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings, self.rope_theta = config.max_position_embeddings, config.rope_theta
        self.is_causal, self.attention_dropout = True, config.attention_dropout
        if (self.head_dim * self.num_heads) != self.hidden_size: raise ValueError(f"hidden_size must be divisible by num_heads (got `hidden_size`: {self.hidden_size} and `num_heads`: {self.num_heads}).")
        self.q_proj, self.k_proj = SAPIENSLinear(self.hidden_size, self.num_heads * self.head_dim, bias=True), SAPIENSLinear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=True)
        self.v_proj, self.o_proj = SAPIENSLinear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=True), SAPIENSLinear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        self.rotary_emb = SapiensRotaryEmbedding(config=self.config)
    def forward(self, hidden_states: sapiens_Tensor, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_LongTensor] = None, position_embeddings: Optional[Tuple[sapiens_Tensor, sapiens_Tensor]] = None) -> Tuple[sapiens_Tensor,
    Optional[sapiens_Tensor], Optional[Tuple[sapiens_Tensor]]]:
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states = self.q_proj(hidden_states), self.k_proj(hidden_states)
        value_states, query_states = self.v_proj(hidden_states), query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states, value_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        from math import sqrt
        attn_weights = sapiens_matmul(query_states, key_states.transpose(2, 3)) / sqrt(self.head_dim)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights, attn_weights = SAPIENSFunctional.softmax(attn_weights, dim=-1, dtype=sapiens_float32).to(query_states.dtype), SAPIENSFunctional.dropout(attn_weights, p=self.attention_dropout, training=self.training)
        attn_output = sapiens_matmul(attn_weights, value_states)
        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is {attn_output.size()}")
        if not output_attentions: attn_weights = None
        return self.o_proj(attn_output.transpose(1, 2).contiguous().reshape(bsz, q_len, self.hidden_size)), attn_weights, past_key_value
class SapiensFlashAttention2(SapiensAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: sapiens_Tensor, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_LongTensor] = None, position_embeddings: Optional[Tuple[sapiens_Tensor, sapiens_Tensor]] = None):
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states = self.q_proj(hidden_states), self.k_proj(hidden_states)
        value_states, query_states = self.v_proj(hidden_states), query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states, value_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2), value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None:
            cache_has_contents, kv_seq_len = past_key_value.get_seq_length(self.layer_idx) > 0, key_states.shape[-2] + cache_position[0]
            if (getattr(self.config, "sliding_window", None) is not None and kv_seq_len > self.config.sliding_window and cache_has_contents):
                slicing_tokens = 1 - self.config.sliding_window
                past_key, past_value = past_key_value[self.layer_idx][0], past_key_value[self.layer_idx][1]
                past_key, past_value = past_key[:, :, slicing_tokens:, :].contiguous(), past_value[:, :, slicing_tokens:, :].contiguous()
                if past_key.shape[-2] != self.config.sliding_window - 1: raise ValueError(f"past key must have a shape of (`batch_size, num_heads, self.config.sliding_window-1, head_dim`), got {past_key.shape}")
                if attention_mask is not None:
                    attention_mask = attention_mask[:, slicing_tokens:]
                    attention_mask = sapiens_cat([attention_mask, sapiens_ones_like(attention_mask[:, -1:])], dim=-1)
            key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups)
        dropout_rate, input_dtype = 0.001 if not self.training else self.attention_dropout, query_states.dtype
        if input_dtype == sapiens_float32:
            if sapiens_is_autocast_enabled(): target_dtype = sapiens_get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            query_states, key_states, value_states = query_states.to(target_dtype), key_states.to(target_dtype), value_states.to(target_dtype)
        query_states, key_states, value_states = query_states.transpose(1, 2), key_states.transpose(1, 2), value_states.transpose(1, 2)
        if (self.config.use_sliding_window and getattr(self.config, "sliding_window", None) is not None and self.layer_idx >= self.config.max_window_layers): sliding_window = self.config.sliding_window
        else: sliding_window = None
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, position_ids=position_ids, dropout=dropout_rate,
        sliding_window=sliding_window, is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        if not output_attentions: attn_weights = None
        return self.o_proj(attn_output.reshape(bsz, q_len, self.hidden_size).contiguous()), attn_weights, past_key_value
class SapiensSdpaAttention(SapiensAttention):
    def forward(self, hidden_states: sapiens_Tensor, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, cache_position: Optional[sapiens_LongTensor] = None, position_embeddings: Optional[Tuple[sapiens_Tensor, sapiens_Tensor]] = None) -> Tuple[sapiens_Tensor, Optional[sapiens_Tensor], Optional[Tuple[sapiens_Tensor]]]:
        if output_attentions: return super().forward(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache)
        bsz, q_len, _ = hidden_states.size()
        query_states, key_states, value_states = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query_states, key_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2), key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        if position_embeddings is None: cos, sin = self.rotary_emb(value_states, position_ids)
        else: cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"sin": sin, "cos": cos, "cache_position": cache_position})
        key_states, value_states, intentional_masking = repeat_kv(key_states, self.num_key_value_groups), repeat_kv(value_states, self.num_key_value_groups), attention_mask
        if attention_mask is not None: intentional_masking = attention_mask[:, :, :, : key_states.shape[-2]]
        if query_states.device.type == "cuda" and attention_mask is not None: query_states, key_states, value_states = query_states.contiguous(), key_states.contiguous(), value_states.contiguous()
        is_causal = True if intentional_masking is None and q_len > 1 else False
        return self.o_proj(SAPIENSFunctional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=intentional_masking, dropout_p=self.attention_dropout if self.training else 0.0, is_causal=is_causal).transpose(1, 2).contiguous().view(bsz, q_len, self.hidden_size)), None, past_key_value
SAPIENS_ATTENTION_CLASSES = {"eager": SapiensAttention, "flash_attention_2": SapiensFlashAttention2, "sdpa": SapiensSdpaAttention}
class SapiensDecoderLayer(SAPIENSModule):
    def __init__(self, config: SapiensConfig, layer_idx: int):
        super().__init__()
        self.hidden_size, self.self_attn = config.hidden_size, SAPIENS_ATTENTION_CLASSES[config._attn_implementation](config, layer_idx)
        self.mlp, self.input_layernorm = SapiensMLP(config), SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
    def forward(self, hidden_states: sapiens_Tensor, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_value: Optional[Tuple[sapiens_Tensor]] = None,
    output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, cache_position: Optional[sapiens_LongTensor] = None,
    position_embeddings: Optional[Tuple[sapiens_Tensor, sapiens_Tensor]] = None, **kwargs) -> Tuple[sapiens_FloatTensor, Optional[Tuple[sapiens_FloatTensor, sapiens_FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, position_ids=position_ids, past_key_value=past_key_value,
        output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
        hidden_states = residual + hidden_states
        residual = hidden_states
        outputs = (residual + self.mlp(self.post_attention_layernorm(hidden_states)),)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
from ...modeling_utils import PreTrainedModel
SAPIENS_START_DOCSTRING = r"\nThis model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the\nlibrary implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads etc.)\nThis model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.\nUse it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and behavior.\nParameters:\nconfig ([`SapiensConfig`]):\nModel configuration class with all the parameters of the model. Initializing with a config file does not\nload the weights associated with the model, only the configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights."
@add_start_docstrings("The bare Sapiens Model outputting raw hidden-states without any specific head on top.", SAPIENS_START_DOCSTRING)
class SapiensPreTrainedModel(PreTrainedModel):
    config_class, base_model_prefix = SapiensConfig, "model"
    supports_gradient_checkpointing, _no_split_modules, _skip_keys_device_placement = True, ["SapiensDecoderLayer"], "past_key_values"
    _supports_flash_attn_2, _supports_sdpa, _supports_cache_class, _supports_quantized_cache, _supports_static_cache = True, True, True, True, True
    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, SAPIENSLinear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, SAPIENSEmbedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
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
def _prepare_4d_causal_attention_mask_with_cache_position(attention_mask: sapiens_Tensor, sequence_length: int, target_length: int, dtype: sapiens_dtype,
device: sapiens_device, min_dtype: float, cache_position: sapiens_Tensor, batch_size: int):
    _n, _m, _x, _y, _z = None, 4, 1, -1, 0
    if attention_mask is not _n and attention_mask.dim() == _m: intentional_masking = attention_mask
    else:
        intentional_masking = sapiens_full((sequence_length, target_length), fill_value=min_dtype, dtype=dtype, device=device)
        if sequence_length != _x: intentional_masking = sapiens_triu(intentional_masking, diagonal=_x)
        intentional_masking *= sapiens_arange(target_length, device=device) > cache_position.reshape(_y, _x)
        intentional_masking = intentional_masking[_n, _n, :, :].expand(batch_size, _x, _y, _y)
        if attention_mask is not _n:
            intentional_masking, mask_length = intentional_masking.clone(), attention_mask.shape[_y]
            padding_mask = intentional_masking[:, :, :, :mask_length] + attention_mask[:, _n, _n, :] == _z
            intentional_masking[:, :, :, :mask_length] = intentional_masking[:, :, :, :mask_length].masked_fill(padding_mask, min_dtype)
    return intentional_masking
from ...modeling_outputs import (BaseModelOutputWithPast, CausalLMOutputWithPast, SequenceClassifierOutputWithPast, TokenClassifierOutput)
from ...modeling_attn_mask_utils import AttentionMaskConverter
@add_start_docstrings("The bare Sapiens Model outputting raw hidden-states without any specific head on top.", SAPIENS_START_DOCSTRING)
class SapiensModel(SapiensPreTrainedModel):
    def __init__(self, config: SapiensConfig):
        super().__init__(config)
        self.padding_idx, self.vocab_size = config.pad_token_id, config.vocab_size
        self.embed_tokens = SAPIENSEmbedding(config.vocab_size, config.hidden_size, self.padding_idx)
        self.layers, self._attn_implementation = SAPIENSModuleList([SapiensDecoderLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)]), config._attn_implementation
        self.norm, self.rotary_emb, self.gradient_checkpointing = SapiensRMSNorm(config.hidden_size, eps=config.rms_norm_eps), SapiensRotaryEmbedding(config=config), False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value=None): self.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPIENS_INPUTS_DOCSTRING)
    def forward(self, input_ids: sapiens_LongTensor = None, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_values: Optional[List[sapiens_FloatTensor]] = None,
    inputs_embeds: Optional[sapiens_FloatTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    cache_position: Optional[sapiens_LongTensor] = None) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache, return_dict, return_legacy_cache = use_cache if use_cache is not None else self.config.use_cache, return_dict if return_dict is not None else self.config.use_return_dict, False
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if self.gradient_checkpointing and self.training:
            if use_cache: use_cache = False
        if use_cache and not isinstance(past_key_values, Cache):
            return_legacy_cache = True
            if past_key_values is None: past_key_values = DynamicCache()
            else: past_key_values = DynamicCache.from_legacy_cache(past_key_values)
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        if cache_position is None:
            past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
            cache_position = sapiens_arange(past_seen_tokens, past_seen_tokens + inputs_embeds.shape[1], device=inputs_embeds.device)
        if position_ids is None: position_ids = cache_position.unsqueeze(0)
        intentional_masking, hidden_states = self._update_causal_mask(attention_mask, inputs_embeds, cache_position, past_key_values, output_attentions), inputs_embeds
        position_embeddings, all_hidden_states, all_self_attns, next_decoder_cache = self.rotary_emb(hidden_states, position_ids), () if output_hidden_states else None, () if output_attentions else None, None
        for decoder_layer in self.layers:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, intentional_masking, position_ids,
            past_key_values, output_attentions, use_cache, cache_position, position_embeddings)
            else: layer_outputs = decoder_layer( hidden_states, attention_mask=intentional_masking, position_ids=position_ids, past_key_value=past_key_values,
            output_attentions=output_attentions, use_cache=use_cache, cache_position=cache_position, position_embeddings=position_embeddings)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache = layer_outputs[2 if output_attentions else 1]
            if output_attentions: all_self_attns += (layer_outputs[1],)
        hidden_states = self.norm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if return_legacy_cache: next_cache = next_cache.to_legacy_cache()
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns] if v is not None)
        return BaseModelOutputWithPast(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns)
    def _update_causal_mask(self, attention_mask: sapiens_Tensor, input_tensor: sapiens_Tensor, cache_position: sapiens_Tensor, past_key_values: Cache, output_attentions: bool):
        if self.config._attn_implementation == "flash_attention_2":
            if attention_mask is not None and 0.0 in attention_mask: return attention_mask
            return None
        past_seen_tokens, using_static_cache = past_key_values.get_seq_length() if past_key_values is not None else 0, isinstance(past_key_values, StaticCache)
        if self.config._attn_implementation == "sdpa" and not using_static_cache and not output_attentions:
            if AttentionMaskConverter._ignore_causal_mask_sdpa(attention_mask, inputs_embeds=input_tensor, past_key_values_length=past_seen_tokens, is_training=self.training): return None
        dtype, device = input_tensor.dtype, input_tensor.device
        min_dtype, sequence_length = sapiens_finfo(dtype).min, input_tensor.shape[1]
        if using_static_cache: target_length = past_key_values.get_max_length()
        else: target_length = (attention_mask.shape[-1] if isinstance(attention_mask, sapiens_Tensor) else past_seen_tokens + sequence_length + 1)
        intentional_masking = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=target_length,
        dtype=dtype, device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=input_tensor.shape[0])
        if (self.config._attn_implementation == "sdpa" and attention_mask is not None and attention_mask.device.type == "cuda" and not output_attentions): intentional_masking = AttentionMaskConverter._unmask_unattended(intentional_masking, min_dtype)
        return intentional_masking
from ...generation import GenerationMixin
from torch.nn import CrossEntropyLoss, MSELoss, BCEWithLogitsLoss
class SapiensForCausalLM(SapiensPreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config=None):
        super().__init__(config)
        self.model, self.vocab_size = SapiensModel(config), config.vocab_size
        self.lm_head = SAPIENSLinear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings=None): self.lm_head = new_embeddings
    def set_decoder(self, decoder=None): self.model = decoder
    def get_decoder(self): return self.model
    @add_start_docstrings_to_model_forward(SAPIENS_INPUTS_DOCSTRING)
    def forward(self, input_ids: sapiens_LongTensor = None, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_values: Optional[List[sapiens_FloatTensor]] = None,
    inputs_embeds: Optional[sapiens_FloatTensor] = None, labels: Optional[sapiens_LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[sapiens_LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, CausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position)
        hidden_states = outputs[0]
        logits, loss = self.lm_head(hidden_states[:, -num_logits_to_keep:, :]).float(), None
        if labels is not None:
            logits = logits.float()
            shift_logits, shift_labels, loss_fct = logits[..., :-1, :].contiguous(), labels[..., 1:].contiguous(), CrossEntropyLoss()
            shift_logits, shift_labels, shift_labels, loss = shift_logits.view(-1, self.config.vocab_size), shift_labels.view(-1), shift_labels.to(shift_logits.device), loss_fct(shift_logits, shift_labels)
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
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :].clone(memory_format=sapiens_contiguous_format)
        if inputs_embeds is not None and cache_position[0] == 0: model_inputs = {"inputs_embeds": inputs_embeds, "input_ids": None}
        else: model_inputs = {"input_ids": input_ids.clone(memory_format=sapiens_contiguous_format), "inputs_embeds": None}
        if isinstance(past_key_values, StaticCache) and attention_mask.ndim == 2:
            if model_inputs["inputs_embeds"] is not None:
                batch_size, sequence_length, _ = model_inputs["inputs_embeds"].shape
                device = model_inputs["inputs_embeds"].device
            else:
                batch_size, sequence_length = model_inputs["input_ids"].shape
                device = model_inputs["input_ids"].device
            dtype, min_dtype = self.lm_head.weight.dtype, sapiens_finfo(dtype).min
            attention_mask = _prepare_4d_causal_attention_mask_with_cache_position(attention_mask, sequence_length=sequence_length, target_length=past_key_values.get_max_length(), dtype=dtype,
            device=device, min_dtype=min_dtype, cache_position=cache_position, batch_size=batch_size)
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        model_inputs.update({"position_ids": position_ids, "cache_position": cache_position, "past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
        return model_inputs
@add_start_docstrings("""
    The Sapiens Model transformer with a sequence classification head on top (linear layer).
    [`SapiensForSequenceClassification`] uses the last token in order to do the classification, as other causal models.
    Since it does classification on the last token, it requires to know the position of the last token. If a
    `pad_token_id` is defined in the configuration, it finds the last token that is not a padding token in each row. If
    no `pad_token_id` is defined, it simply takes the last value in each row of the batch. Since it cannot guess the
    padding tokens when `inputs_embeds` are passed instead of `input_ids`, it does the same (take the last value in
    each row of the batch).
""", SAPIENS_START_DOCSTRING)
class SapiensForSequenceClassification(SapiensPreTrainedModel):
    def __init__(self, config=None):
        super().__init__(config)
        self.num_labels, self.model = config.num_labels, SapiensModel(config)
        self.score = SAPIENSLinear(config.hidden_size, self.num_labels, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPIENS_INPUTS_DOCSTRING)
    def forward(self, input_ids: sapiens_LongTensor = None, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_values: Optional[List[sapiens_FloatTensor]] = None,
    inputs_embeds: Optional[sapiens_FloatTensor] = None, labels: Optional[sapiens_LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, SequenceClassifierOutputWithPast]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        transformer_outputs = self.model(input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states, logits = transformer_outputs[0], self.score(hidden_states)
        if input_ids is not None: batch_size = input_ids.shape[0]
        else: batch_size = inputs_embeds.shape[0]
        if self.config.pad_token_id is None and batch_size != 1: raise ValueError("Cannot handle batch sizes > 1 if no padding token is defined.")
        if self.config.pad_token_id is None: sequence_lengths = -1
        else:
            if input_ids is not None: sequence_lengths = ((sapiens_eq(input_ids, self.config.pad_token_id).int().argmax(-1) - 1) % input_ids.shape[-1]).to(logits.device)
            else: sequence_lengths = -1
        pooled_logits, loss = logits[sapiens_arange(batch_size, device=logits.device), sequence_lengths], None
        if labels is not None:
            labels = labels.to(logits.device)
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == sapiens_long or labels.dtype == sapiens_int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(pooled_logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(pooled_logits, labels)
            elif self.config.problem_type == "single_label_classification": loss_fct, loss = CrossEntropyLoss(), loss_fct(pooled_logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification": loss_fct, loss = BCEWithLogitsLoss(), loss_fct(pooled_logits, labels)
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutputWithPast(loss=loss, logits=pooled_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states, attentions=transformer_outputs.attentions)
@add_start_docstrings("The Sapiens Model transformer with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", SAPIENS_START_DOCSTRING)
class SapiensForTokenClassification(SapiensPreTrainedModel):
    def __init__(self, config=None):
        super().__init__(config)
        self.num_labels, self.model = config.num_labels, SapiensModel(config)
        if getattr(config, "classifier_dropout", None) is not None: classifier_dropout = config.classifier_dropout
        elif getattr(config, "hidden_dropout", None) is not None: classifier_dropout = config.hidden_dropout
        else: classifier_dropout = 0.1
        self.dropout, self.score = SAPIENSDropout(classifier_dropout), SAPIENSLinear(config.hidden_size, config.num_labels)
        self.post_init()
    def get_input_embeddings(self): return self.model.embed_tokens
    def set_input_embeddings(self, value=None): self.model.embed_tokens = value
    @add_start_docstrings_to_model_forward(SAPIENS_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[sapiens_LongTensor] = None, attention_mask: Optional[sapiens_Tensor] = None, position_ids: Optional[sapiens_LongTensor] = None, past_key_values: Optional[List[sapiens_FloatTensor]] = None,
    inputs_embeds: Optional[sapiens_FloatTensor] = None, labels: Optional[sapiens_LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, TokenClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output, logits, loss = self.dropout(outputs[0]), self.score(outputs[0]), None
        if labels is not None: loss = CrossEntropyLoss()(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
