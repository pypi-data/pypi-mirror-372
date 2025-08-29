"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
_CONFIG_FOR_DOC, _CHECKPOINT_FOR_DOC, _REAL_CHECKPOINT_FOR_DOC = "EntityConfig", "afmck/testing-entity-tiny", "openlm-research/open_entity_3b_v2"
ENTITY_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`numpy.ndarray` of shape `(batch_size, input_ids_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`numpy.ndarray` of shape `(batch_size, sequence_length)`, *optional*):
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
        position_ids (`numpy.ndarray` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`.
            [What are position IDs?](../glossary#position-ids)
        past_key_values (`Dict[str, np.ndarray]`, *optional*, returned by `init_cache` or when passing previous `past_key_values`):
            Dictionary of pre-computed hidden-states (key and values in the attention blocks) that can be used for fast
            auto-regressive decoding. Pre-computed key and value hidden-states are of shape *[batch_size, max_length]*.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
ENTITY_START_DOCSTRING = r"""
    This model inherits from [`FlaxPreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a Flax Linen
    [flax.nn.Module](https://flax.readthedocs.io/en/latest/_autosummary/flax.nn.module.html) subclass. Use it as a
    regular Flax Module and refer to the Flax documentation for all matter related to general usage and behavior.
    Finally, this model supports inherent JAX features such as:
    - [Just-In-Time (JIT) compilation](https://jax.readthedocs.io/en/latest/jax.html#just-in-time-compilation-jit)
    - [Automatic Differentiation](https://jax.readthedocs.io/en/latest/jax.html#automatic-differentiation)
    - [Vectorization](https://jax.readthedocs.io/en/latest/jax.html#vectorization-vmap)
    - [Parallelization](https://jax.readthedocs.io/en/latest/jax.html#parallelization-pmap)
    Parameters:
        config ([`EntityConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~FlaxPreTrainedModel.from_pretrained`] method to load the model weights.
        dtype (`jax.numpy.dtype`, *optional*, defaults to `jax.numpy.float32`):
            The data type of the computation. Can be one of `jax.numpy.float32`, `jax.numpy.float16`, or
            `jax.numpy.bfloat16`.
            This can be used to enable mixed-precision training or half-precision inference on GPUs or TPUs. If
            specified all the computation will be performed with the given `dtype`.
            *Note that this only specifies the dtype of the computation and does not influence the dtype of model
            parameters.*
            If you wish to change the dtype of the model parameters, see [`~FlaxPreTrainedModel.to_fp16`] and
            [`~FlaxPreTrainedModel.to_bf16`].
"""
from flax.linen import Module as f_Module, Dense as f_Dense, compact as f_compact, Embed as f_Embed
from .configuration_entity import EntityConfig
from jax.numpy import (dtype as j_dtype, float32 as j_float32, ones as j_ones, asarray as j_asarray, power as j_power, sqrt as j_sqrt, concatenate as j_concatenate, array as j_array,
split as j_split, zeros as j_zeros, int32 as j_int32, broadcast_to as j_broadcast_to, arange as j_arange, expand_dims as j_expand_dims, repeat as j_repeat, full as j_full,
finfo as j_finfo, einsum as j_einsum, ones_like as j_ones_like, atleast_2d as j_atleast_2d)
from jax.nn import initializers as jn_initializers
from jax.lax import dynamic_update_slice as l_dynamic_update_slice, select as l_select
class FlaxEntityRMSNorm(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self): self.epsilon, self.weight = self.config.rms_norm_eps, self.param("weight", lambda _, shape: j_ones(shape), self.config.hidden_size)
    def __call__(self, hidden_states): return self.weight * j_asarray(hidden_states / j_sqrt(j_power(j_asarray(hidden_states, dtype=j_float32), 2).mean(-1, keepdims=True) + self.epsilon), dtype=self.dtype)
def rotate_half(tensor=None): return j_concatenate((-tensor[..., tensor.shape[-1] // 2 :], tensor[..., : tensor.shape[-1] // 2]), axis=-1)
import numpy as np
def create_sinusoidal_positions(num_pos=None, dim=None):
    freqs = np.einsum("i , j -> i j", np.arange(num_pos), 1.0 / (10000 ** (np.arange(0, dim, 2) / dim))).astype("float32")
    emb = np.concatenate((freqs, freqs), axis=-1)
    return j_array(np.concatenate((np.sin(emb)[:, None, :], np.cos(emb)[:, None, :]), axis=-1)[:, :, :num_pos])
def apply_rotary_pos_emb(tensor=None, sin_pos=None, cos_pos=None): return (tensor * cos_pos) + (rotate_half(tensor) * sin_pos)
class FlaxEntityRotaryEmbedding(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self): self.sincos = create_sinusoidal_positions(self.config.max_position_embeddings, self.config.hidden_size // self.config.num_attention_heads)
    def __call__(self, key, query, position_ids):
        sincos = self.sincos[position_ids]
        sin_pos, cos_pos = j_split(sincos, 2, axis=-1)
        key, query = apply_rotary_pos_emb(key, sin_pos, cos_pos), apply_rotary_pos_emb(query, sin_pos, cos_pos)
        return j_asarray(key, dtype=self.dtype), j_asarray(query, dtype=self.dtype)
from flax.linen import combine_masks
class FlaxEntityAttention(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    causal: bool = True
    is_cross_attention: bool = False
    def setup(self):
        config = self.config
        self.embed_dim, self.num_heads = config.hidden_size, config.num_attention_heads
        self.head_dim, self.num_key_value_heads = self.embed_dim // self.num_heads, config.num_key_value_heads
        self.num_key_value_groups, self.attention_softmax_in_fp32 = self.num_heads // self.num_key_value_heads, self.dtype is not j_float32
        from functools import partial
        dense = partial(f_Dense, use_bias=config.attention_bias, dtype=self.dtype, kernel_init=jn_initializers.normal(self.config.initializer_range))
        self.q_proj, self.k_proj = dense(self.num_heads * self.head_dim), dense(self.num_key_value_heads * self.head_dim)
        self.v_proj, self.o_proj = dense(self.num_key_value_heads * self.head_dim), dense(self.embed_dim)
        from flax.linen import make_causal_mask
        self.causal_mask, self.rotary_emb = make_causal_mask(j_ones((1, config.max_position_embeddings), dtype="bool"), dtype="bool"), FlaxEntityRotaryEmbedding(config, dtype=self.dtype)
    def _split_heads(self, hidden_states=None, num_heads=None): return hidden_states.reshape(hidden_states.shape[:2] + (num_heads, self.head_dim))
    def _merge_heads(self, hidden_states=None): return hidden_states.reshape(hidden_states.shape[:2] + (self.embed_dim,))
    @f_compact
    def _concatenate_to_cache(self, key=None, value=None, query=None, attention_mask=None):
        is_initialized, cached_key = self.has_variable("cache", "cached_key"), self.variable("cache", "cached_key", j_zeros, key.shape, key.dtype)
        cached_value, cache_index = self.variable("cache", "cached_value", j_zeros, value.shape, value.dtype), self.variable("cache", "cache_index", lambda: j_array(0, dtype=j_int32))
        if is_initialized:
            *batch_dims, max_length, num_heads, depth_per_head = cached_key.value.shape
            cur_index = cache_index.value
            indices = (0,) * len(batch_dims) + (cur_index, 0, 0)
            key, value = l_dynamic_update_slice(cached_key.value, key, indices), l_dynamic_update_slice(cached_value.value, value, indices)
            cached_key.value, cached_value.value = key, value
            num_updated_cache_vectors = query.shape[1]
            cache_index.value = cache_index.value + num_updated_cache_vectors
            attention_mask = combine_masks(j_broadcast_to(j_arange(max_length) < cur_index + num_updated_cache_vectors, tuple(batch_dims) + (1, num_updated_cache_vectors, max_length)), attention_mask)
        return key, value, attention_mask
    def __call__(self, hidden_states=None, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False):
        query, key, value = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query, key, value = self._split_heads(query, self.num_heads), self._split_heads(key, self.num_key_value_heads), self._split_heads(value, self.num_key_value_heads)
        key, query = self.rotary_emb(key, query, position_ids)
        query_length, key_length = query.shape[1], key.shape[1]
        if self.has_variable("cache", "cached_key"):
            mask_shift, max_decoder_length = self.variables["cache"]["cache_index"], self.variables["cache"]["cached_key"].shape[1]
            causal_mask = l_dynamic_slice(self.causal_mask, (0, 0, mask_shift, 0), (1, 1, query_length, max_decoder_length))
        else: causal_mask = self.causal_mask[:, :, :query_length, :key_length]
        causal_mask, attention_mask = j_broadcast_to(causal_mask, (hidden_states.shape[0],) + causal_mask.shape[1:]), j_broadcast_to(j_expand_dims(attention_mask, axis=(-3, -2)), causal_mask.shape)
        attention_mask, dropout_rng = combine_masks(attention_mask, causal_mask), None
        if not deterministic and self.config.attention_dropout > 0.0: dropout_rng = self.make_rng("dropout")
        if self.has_variable("cache", "cached_key") or init_cache: key, value, attention_mask = self._concatenate_to_cache(key, value, query, attention_mask)
        key, value = j_repeat(key, self.num_key_value_groups, axis=2), j_repeat(value, self.num_key_value_groups, axis=2)
        attention_bias = l_select(attention_mask > 0, j_full(attention_mask.shape, 0.0).astype(self.dtype), j_full(attention_mask.shape, j_finfo(self.dtype).min).astype(self.dtype))
        from flax.linen.attention import dot_product_attention_weights
        attn_weights = dot_product_attention_weights(query, key, bias=attention_bias, dropout_rng=dropout_rng, dropout_rate=self.config.attention_dropout, deterministic=deterministic, dtype=j_float32 if self.attention_softmax_in_fp32 else self.dtype)
        if self.attention_softmax_in_fp32: attn_weights = attn_weights.astype(self.dtype)
        attn_output = self.o_proj(self._merge_heads(j_einsum("...hqk,...khd->...qhd", attn_weights, value)))
        return (attn_output, attn_weights) if output_attentions else (attn_output,)
class FlaxEntityMLP(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self):
        embed_dim = self.config.hidden_size
        inner_dim, kernel_init = self.config.intermediate_size if self.config.intermediate_size is not None else 4 * embed_dim, jn_initializers.normal(self.config.initializer_range)
        from ...modeling_flax_utils import ACT2FN
        self.act, self.gate_proj = ACT2FN[self.config.hidden_act], f_Dense(inner_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init)
        self.down_proj, self.up_proj = f_Dense(embed_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init), f_Dense(inner_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init)
    def __call__(self, hidden_states=None):
        up_proj_states, gate_states = self.up_proj(hidden_states), self.act(self.gate_proj(hidden_states))
        return self.down_proj(up_proj_states * gate_states)
class FlaxEntityDecoderLayer(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self):
        self.input_layernorm, self.self_attn = FlaxEntityRMSNorm(self.config, dtype=self.dtype), FlaxEntityAttention(self.config, dtype=self.dtype)
        self.post_attention_layernorm, self.mlp = FlaxEntityRMSNorm(self.config, dtype=self.dtype), FlaxEntityMLP(self.config, dtype=self.dtype)
    def __call__(self, hidden_states=None, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False):
        residual, hidden_states = hidden_states, self.input_layernorm(hidden_states)
        outputs = self.self_attn(hidden_states, attention_mask=attention_mask, position_ids=position_ids, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions)
        hidden_states = residual + outputs[0]
        return (hidden_states + self.mlp(self.post_attention_layernorm(hidden_states)),) + outputs[1:]
from ...modeling_flax_utils import FlaxPreTrainedModel, append_call_sample_docstring
from typing import Tuple, Optional
from flax.core.frozen_dict import FrozenDict, unfreeze, freeze
from ...utils import add_start_docstrings_to_model_forward, add_start_docstrings
class FlaxEntityPreTrainedModel(FlaxPreTrainedModel):
    config_class, base_model_prefix = EntityConfig, "model"
    module_class: f_Module = None
    def __init__(self, config: EntityConfig, input_shape: Tuple = (1, 1), seed: int = 0, dtype: j_dtype = j_float32, _do_init: bool = True, **kwargs):
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: jax.random.PRNGKey, input_shape: Tuple, params: FrozenDict = None) -> FrozenDict:
        input_ids = j_zeros(input_shape, dtype="i4")
        attention_mask, position_ids = j_ones_like(input_ids), j_broadcast_to(j_arange(j_atleast_2d(input_ids).shape[-1]), input_shape)
        params_rng, dropout_rng = jax.random.split(rng)
        random_params = self.module.init({"params": params_rng, "dropout": dropout_rng}, input_ids, attention_mask, position_ids, return_dict=False)["params"]
        if params is not None:
            from flax.traverse_util import flatten_dict, unflatten_dict
            random_params, params = flatten_dict(unfreeze(random_params)), flatten_dict(unfreeze(params))
            for missing_key in self._missing_keys: params[missing_key] = random_params[missing_key]
            self._missing_keys = set()
            return freeze(unflatten_dict(params))
        else: return random_params
    def init_cache(self, batch_size=None, max_length=None):
        input_ids = j_ones((batch_size, max_length))
        attention_mask, position_ids = j_ones_like(input_ids), j_broadcast_to(j_arange(j_atleast_2d(input_ids).shape[-1]), input_ids.shape)
        return unfreeze(self.module.init(jax.random.PRNGKey(0), input_ids, attention_mask, position_ids, return_dict=False, init_cache=True)["cache"])
    @add_start_docstrings_to_model_forward(ENTITY_INPUTS_DOCSTRING)
    def __call__(self, input_ids=None, attention_mask=None, position_ids=None, params: dict = None, past_key_values: dict = None, dropout_rng: jax.random.PRNGKey = None,
    train: bool = False, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None):
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        batch_size, sequence_length, rngs, inputs = input_ids.shape, {}, {"params": params or self.params}
        if position_ids is None:
            if past_key_values is not None: raise ValueError("Make sure to provide `position_ids` when passing `past_key_values`.")
            position_ids = j_broadcast_to(j_arange(sequence_length)[None, :], (batch_size, sequence_length))
        if attention_mask is None: attention_mask = j_ones((batch_size, sequence_length))
        if dropout_rng is not None: rngs["dropout"] = dropout_rng
        if past_key_values: inputs["cache"], mutable = past_key_values, ["cache"]
        else: mutable = False
        outputs = self.module.apply(inputs, j_array(input_ids, dtype="i4"), j_array(attention_mask, dtype="i4"), j_array(position_ids, dtype="i4"), not train,
        False, output_attentions, output_hidden_states, return_dict, rngs=rngs, mutable=mutable)
        if past_key_values is not None and return_dict:
            outputs, past_key_values = outputs
            outputs["past_key_values"] = unfreeze(past_key_values["cache"])
            return outputs
        elif past_key_values is not None and not return_dict:
            outputs, past_key_values = outputs
            outputs = outputs[:1] + (unfreeze(past_key_values["cache"]),) + outputs[1:]
        return outputs
class FlaxEntityLayerCollection(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self): self.blocks = [FlaxEntityDecoderLayer(self.config, dtype=self.dtype, name=str(i)) for i in range(self.config.num_hidden_layers)]
    def __call__(self, hidden_states=None, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False,
    output_hidden_states: bool = False, return_dict: bool = False):
        all_attentions, all_hidden_states = () if output_attentions else None, () if output_hidden_states else None
        for block in self.blocks:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            layer_outputs = block(hidden_states, attention_mask=attention_mask, position_ids=position_ids, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions)
            if output_attentions: all_attentions += (layer_outputs[1],)
        return (layer_outputs[0], all_hidden_states, all_attentions)
from ...modeling_flax_outputs import FlaxBaseModelOutput, FlaxCausalLMOutput
class FlaxEntityModule(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self):
        self.hidden_size, embedding_init = self.config.hidden_size, jn_initializers.normal(stddev=self.config.initializer_range)
        self.embed_tokens, self.layers, self.norm = f_Embed(self.config.vocab_size, self.hidden_size, embedding_init=embedding_init, dtype=self.dtype), FlaxEntityLayerCollection(self.config, dtype=self.dtype), FlaxEntityRMSNorm(self.config, dtype=self.dtype)
    def __call__(self, input_ids=None, attention_mask=None, position_ids=None, deterministic=True, init_cache: bool = False, output_attentions: bool = False, output_hidden_states: bool = False, return_dict: bool = True):
        outputs = self.layers(self.embed_tokens(input_ids.astype("i4")), position_ids=position_ids, attention_mask=attention_mask, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = self.norm(outputs[0])
        if output_hidden_states: outputs = (hidden_states, outputs[1] + (hidden_states,)) + outputs[2:]
        else: outputs = (hidden_states,) + outputs[1:]
        if not return_dict: return tuple(v for v in outputs if v is not None)
        return FlaxBaseModelOutput(last_hidden_state=hidden_states, hidden_states=outputs[1], attentions=outputs[-1])
@add_start_docstrings("The bare Entity Model transformer outputting raw hidden-states without any specific head on top.", ENTITY_START_DOCSTRING)
class FlaxEntityModel(FlaxEntityPreTrainedModel): module_class = FlaxEntityModule
append_call_sample_docstring(FlaxEntityModel, _CHECKPOINT_FOR_DOC, FlaxBaseModelOutput, _CONFIG_FOR_DOC, real_checkpoint=_REAL_CHECKPOINT_FOR_DOC)
class FlaxEntityForCausalLMModule(f_Module):
    config: EntityConfig
    dtype: j_dtype = j_float32
    def setup(self): self.model, self.lm_head = FlaxEntityModule(self.config, dtype=self.dtype), f_Dense(self.config.vocab_size, use_bias=False, dtype=self.dtype, kernel_init=jn_initializers.normal(stddev=self.config.initializer_range))
    def __call__(self, input_ids, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False,
    output_hidden_states: bool = False, return_dict: bool = True):
        outputs = self.model(input_ids, position_ids=position_ids, attention_mask=attention_mask, deterministic=deterministic, init_cache=init_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        lm_logits = self.lm_head(outputs[0])
        if not return_dict: return (lm_logits,) + outputs[1:]
        return FlaxCausalLMOutput(logits=lm_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("The Entity Model transformer with a language modeling head (linear layer) on top.", ENTITY_START_DOCSTRING)
class FlaxEntityForCausalLM(FlaxEntityPreTrainedModel):
    module_class = FlaxEntityForCausalLMModule
    def prepare_inputs_for_generation(self, input_ids=None, max_length=None, attention_mask: Optional[jax.Array] = None):
        batch_size, seq_length = input_ids.shape
        past_key_values, extended_attention_mask = self.init_cache(batch_size, max_length), j_ones((batch_size, max_length), dtype="i4")
        if attention_mask is not None: position_ids, extended_attention_mask = attention_mask.cumsum(axis=-1) - 1, l_dynamic_update_slice(extended_attention_mask, attention_mask, (0, 0))
        else: position_ids = j_broadcast_to(j_arange(seq_length, dtype="i4")[None, :], (batch_size, seq_length))
        return {"past_key_values": past_key_values, "attention_mask": extended_attention_mask, "position_ids": position_ids}
    def update_inputs_for_generation(self, model_outputs, model_kwargs):
        model_kwargs["past_key_values"], model_kwargs["position_ids"] = model_outputs.past_key_values, model_kwargs["position_ids"][:, -1:] + 1
        return model_kwargs
append_call_sample_docstring(FlaxEntityForCausalLM, _CHECKPOINT_FOR_DOC, FlaxCausalLMOutput, _CONFIG_FOR_DOC, real_checkpoint=_REAL_CHECKPOINT_FOR_DOC)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
