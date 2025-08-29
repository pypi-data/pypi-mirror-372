"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...modeling_flax_utils import ACT2FN, FlaxPreTrainedModel, append_call_sample_docstring
from ...utils import add_start_docstrings_to_model_forward, add_start_docstrings
from ...modeling_flax_outputs import FlaxBaseModelOutput, FlaxCausalLMOutput
from flax.linen.attention import dot_product_attention_weights
from flax.core.frozen_dict import FrozenDict, unfreeze, freeze
from flax.traverse_util import flatten_dict, unflatten_dict
from flax.linen import make_causal_mask, combine_masks
from .configuration_sapama import SapamaConfig
from typing import Tuple, Optional
import jax.numpy as jnp
from jax import lax
import numpy as np
_CONFIG_FOR_DOC, _CHECKPOINT_FOR_DOC, _REAL_CHECKPOINT_FOR_DOC = "SapamaConfig", "sapiens/testing-sapama-tiny", "sapiens/sapama"
import flax.linen as nn
class FlaxSapamaRMSNorm(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self): self.epsilon, self.weight = self.config.rms_norm_eps, self.param("weight", lambda _, shape: jnp.ones(shape), self.config.hidden_size)
    def __call__(self, hidden_states): return self.weight * jnp.asarray(hidden_states / jnp.sqrt(jnp.power(jnp.asarray(hidden_states, dtype=jnp.float32), 2).mean(-1, keepdims=True) + self.epsilon), dtype=self.dtype)
def create_sinusoidal_positions(num_pos, dim):
    freqs = np.einsum("i , j -> i j", np.arange(num_pos), 1.0 / (10000 ** (np.arange(0, dim, 2) / dim))).astype("float32")
    emb = np.concatenate((freqs, freqs), axis=-1)
    return jnp.array(np.concatenate((np.sin(emb)[:, None, :], np.cos(emb)[:, None, :]), axis=-1)[:, :, :num_pos])
def apply_rotary_pos_emb(tensor, sin_pos, cos_pos):
    def rotate_half(tensor): return jnp.concatenate((-tensor[..., tensor.shape[-1] // 2 :], tensor[..., : tensor.shape[-1] // 2]), axis=-1)
    return (tensor * cos_pos) + (rotate_half(tensor) * sin_pos)
class FlaxSapamaRotaryEmbedding(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self): self.sincos = create_sinusoidal_positions(self.config.max_position_embeddings, self.config.hidden_size // self.config.num_attention_heads)
    def __call__(self, key, query, position_ids):
        sin_pos, cos_pos = jnp.split(self.sincos[position_ids], 2, axis=-1)
        key, query = apply_rotary_pos_emb(key, sin_pos, cos_pos), apply_rotary_pos_emb(query, sin_pos, cos_pos)
        return jnp.asarray(key, dtype=self.dtype), jnp.asarray(query, dtype=self.dtype)
from jax import nn as j_nn, random as j_random, Array as j_Array
class FlaxSapamaAttention(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    causal: bool = True
    is_cross_attention: bool = False
    def setup(self):
        config = self.config
        self.embed_dim, self.num_heads = config.hidden_size, config.num_attention_heads
        self.head_dim, self.num_key_value_heads = self.embed_dim // self.num_heads, config.num_key_value_heads
        self.num_key_value_groups, self.attention_softmax_in_fp32 = self.num_heads // self.num_key_value_heads, self.dtype is not jnp.float32
        from functools import partial
        dense = partial(nn.Dense, use_bias=config.attention_bias, dtype=self.dtype, kernel_init=j_nn.initializers.normal(self.config.initializer_range))
        self.q_proj, self.k_proj = dense(self.num_heads * self.head_dim), dense(self.num_key_value_heads * self.head_dim)
        self.v_proj, self.o_proj = dense(self.num_key_value_heads * self.head_dim), dense(self.embed_dim)
        self.causal_mask, self.rotary_emb = make_causal_mask(jnp.ones((1, config.max_position_embeddings), dtype="bool"), dtype="bool"), FlaxSapamaRotaryEmbedding(config, dtype=self.dtype)
    def _split_heads(self, hidden_states, num_heads): return hidden_states.reshape(hidden_states.shape[:2] + (num_heads, self.head_dim))
    def _merge_heads(self, hidden_states): return hidden_states.reshape(hidden_states.shape[:2] + (self.embed_dim,))
    @nn.compact
    def _concatenate_to_cache(self, key, value, query, attention_mask):
        is_initialized, cached_key = self.has_variable("cache", "cached_key"), self.variable("cache", "cached_key", jnp.zeros, key.shape, key.dtype)
        cached_value, cache_index = self.variable("cache", "cached_value", jnp.zeros, value.shape, value.dtype), self.variable("cache", "cache_index", lambda: jnp.array(0, dtype=jnp.int32))
        if is_initialized:
            *batch_dims, max_length, num_heads, depth_per_head = cached_key.value.shape
            cur_index = cache_index.value
            indices = (0,) * len(batch_dims) + (cur_index, 0, 0)
            key, value = lax.dynamic_update_slice(cached_key.value, key, indices), lax.dynamic_update_slice(cached_value.value, value, indices)
            cached_key.value, cached_value.value = key, value
            num_updated_cache_vectors, cache_index.value = query.shape[1], cache_index.value + num_updated_cache_vectors
        return key, value, combine_masks(jnp.broadcast_to(jnp.arange(max_length) < cur_index + num_updated_cache_vectors, tuple(batch_dims) + (1, num_updated_cache_vectors, max_length)), attention_mask)
    def __call__(self, hidden_states, attention_mask, position_ids, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False):
        query, key, value = self.q_proj(hidden_states), self.k_proj(hidden_states), self.v_proj(hidden_states)
        query, key, value = self._split_heads(query, self.num_heads), self._split_heads(key, self.num_key_value_heads), self._split_heads(value, self.num_key_value_heads)
        key, query = self.rotary_emb(key, query, position_ids)
        query_length, key_length = query.shape[1], key.shape[1]
        if self.has_variable("cache", "cached_key"): causal_mask = lax.dynamic_slice(self.causal_mask, (0, 0, self.variables["cache"]["cache_index"], 0), (1, 1, query_length, self.variables["cache"]["cached_key"].shape[1]))
        else: causal_mask = self.causal_mask[:, :, :query_length, :key_length]
        causal_mask = jnp.broadcast_to(causal_mask, (hidden_states.shape[0],) + causal_mask.shape[1:])
        attention_mask, dropout_rng = combine_masks(jnp.broadcast_to(jnp.expand_dims(attention_mask, axis=(-3, -2)), causal_mask.shape), causal_mask), None
        if not deterministic and self.config.attention_dropout > 0.0: dropout_rng = self.make_rng("dropout")
        if self.has_variable("cache", "cached_key") or init_cache: key, value, attention_mask = self._concatenate_to_cache(key, value, query, attention_mask)
        key, value = jnp.repeat(key, self.num_key_value_groups, axis=2), jnp.repeat(value, self.num_key_value_groups, axis=2)
        attention_bias = lax.select(attention_mask > 0, jnp.full(attention_mask.shape, 0.0).astype(self.dtype), jnp.full(attention_mask.shape, jnp.finfo(self.dtype).min).astype(self.dtype))
        attn_weights = dot_product_attention_weights(query, key, bias=attention_bias, dropout_rng=dropout_rng, dropout_rate=self.config.attention_dropout, deterministic=deterministic, dtype=jnp.float32 if self.attention_softmax_in_fp32 else self.dtype)
        if self.attention_softmax_in_fp32: attn_weights = attn_weights.astype(self.dtype)
        attn_output = self.o_proj(self._merge_heads(jnp.einsum("...hqk,...khd->...qhd", attn_weights, value)))
        return (attn_output, attn_weights) if output_attentions else (attn_output,)
class FlaxSapamaMLP(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        embed_dim, inner_dim = self.config.hidden_size, self.config.intermediate_size if self.config.intermediate_size is not None else 4 * embed_dim
        kernel_init, self.act = j_nn.initializers.normal(self.config.initializer_range), ACT2FN[self.config.hidden_act]
        self.gate_proj, self.down_proj = nn.Dense(inner_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init), nn.Dense(embed_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init)
        self.up_proj = nn.Dense(inner_dim, use_bias=False, dtype=self.dtype, kernel_init=kernel_init)
    def __call__(self, hidden_states): return self.down_proj(self.up_proj(hidden_states) * self.act(self.gate_proj(hidden_states)))
class FlaxSapamaDecoderLayer(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.input_layernorm, self.self_attn = FlaxSapamaRMSNorm(self.config, dtype=self.dtype), FlaxSapamaAttention(self.config, dtype=self.dtype)
        self.post_attention_layernorm, self.mlp = FlaxSapamaRMSNorm(self.config, dtype=self.dtype), FlaxSapamaMLP(self.config, dtype=self.dtype)
    def __call__(self, hidden_states, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False):
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        outputs = self.self_attn(hidden_states, attention_mask=attention_mask, position_ids=position_ids, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions)
        hidden_states = residual + outputs[0]
        residual = hidden_states
        return (residual + self.mlp(self.post_attention_layernorm(hidden_states)),) + outputs[1:]
class FlaxSapamaLayerCollection(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self): self.blocks = [FlaxSapamaDecoderLayer(self.config, dtype=self.dtype, name=str(i)) for i in range(self.config.num_hidden_layers)]
    def __call__(self, hidden_states, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False,
    output_hidden_states: bool = False, return_dict: bool = False):
        all_attentions, all_hidden_states = () if output_attentions else None, () if output_hidden_states else None
        for block in self.blocks:
            if output_hidden_states: all_hidden_states += (hidden_states,)
            layer_outputs = block(hidden_states, attention_mask=attention_mask, position_ids=position_ids, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions)
            if output_attentions: all_attentions += (layer_outputs[1],)
        return (layer_outputs[0], all_hidden_states, all_attentions)
class FlaxSapamaModule(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.hidden_size = self.config.hidden_size
        embedding_init = j_nn.initializers.normal(stddev=self.config.initializer_range)
        self.embed_tokens = nn.Embed(self.config.vocab_size, self.hidden_size, embedding_init=embedding_init, dtype=self.dtype)
        self.layers, self.norm = FlaxSapamaLayerCollection(self.config, dtype=self.dtype), FlaxSapamaRMSNorm(self.config, dtype=self.dtype)
    def __call__(self, input_ids, attention_mask=None, position_ids=None, deterministic=True, init_cache: bool = False, output_attentions: bool = False, output_hidden_states: bool = False, return_dict: bool = True):
        outputs = self.layers(self.embed_tokens(input_ids.astype("i4")), position_ids=position_ids, attention_mask=attention_mask, deterministic=deterministic, init_cache=init_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = self.norm(outputs[0])
        if output_hidden_states: outputs = (hidden_states, outputs[1] + (hidden_states,)) + outputs[2:]
        else: outputs = (hidden_states,) + outputs[1:]
        if not return_dict: return tuple(v for v in outputs if v is not None)
        return FlaxBaseModelOutput(last_hidden_state=hidden_states, hidden_states=outputs[1], attentions=outputs[-1])
class FlaxSapamaPreTrainedModel(FlaxPreTrainedModel):
    config_class, base_model_prefix = SapamaConfig, "model"
    module_class: nn.Module = None
    def __init__(self, config: SapamaConfig, input_shape: Tuple = (1, 1), seed: int = 0, dtype: jnp.dtype = jnp.float32, _do_init: bool = True, **kwargs):
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: j_random.PRNGKey, input_shape: Tuple, params: FrozenDict = None) -> FrozenDict:
        input_ids = jnp.zeros(input_shape, dtype="i4")
        attention_mask = jnp.ones_like(input_ids)
        position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_shape)
        params_rng, dropout_rng = j_random.split(rng)
        random_params = self.module.init({"params": params_rng, "dropout": dropout_rng}, input_ids, attention_mask, position_ids, return_dict=False)["params"]
        if params is not None:
            random_params = flatten_dict(unfreeze(random_params))
            params = flatten_dict(unfreeze(params))
            for missing_key in self._missing_keys: params[missing_key] = random_params[missing_key]
            self._missing_keys = set()
            return freeze(unflatten_dict(params))
        else: return random_params
    def init_cache(self, batch_size, max_length):
        input_ids, attention_mask = jnp.ones((batch_size, max_length)), jnp.ones_like(input_ids)
        return unfreeze(self.module.init(j_random.PRNGKey(0), input_ids, attention_mask, jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_ids.shape), return_dict=False, init_cache=True)["cache"])
    SAPAMA_INPUTS_DOCSTRING = r"""
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
    @add_start_docstrings_to_model_forward(SAPAMA_INPUTS_DOCSTRING)
    def __call__(self, input_ids, attention_mask=None, position_ids=None, params: dict = None, past_key_values: dict = None, dropout_rng: j_random.PRNGKey = None,
    train: bool = False, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None):
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict, rngs = return_dict if return_dict is not None else self.config.return_dict, {}
        batch_size, sequence_length = input_ids.shape
        if position_ids is None:
            if past_key_values is not None: raise ValueError("Make sure to provide `position_ids` when passing `past_key_values`.")
            position_ids = jnp.broadcast_to(jnp.arange(sequence_length)[None, :], (batch_size, sequence_length))
        if attention_mask is None: attention_mask = jnp.ones((batch_size, sequence_length))
        if dropout_rng is not None: rngs["dropout"] = dropout_rng
        inputs = {"params": params or self.params}
        if past_key_values: inputs["cache"], mutable = past_key_values, ["cache"]
        else: mutable = False
        outputs = self.module.apply(inputs, jnp.array(input_ids, dtype="i4"), jnp.array(attention_mask, dtype="i4"), jnp.array(position_ids, dtype="i4"), not train,
        False, output_attentions, output_hidden_states, return_dict, rngs=rngs, mutable=mutable)
        if past_key_values is not None and return_dict:
            outputs, past_key_values = outputs
            outputs["past_key_values"] = unfreeze(past_key_values["cache"])
            return outputs
        elif past_key_values is not None and not return_dict:
            outputs, past_key_values = outputs
            outputs = outputs[:1] + (unfreeze(past_key_values["cache"]),) + outputs[1:]
        return outputs
SAPAMA_START_DOCSTRING = r"""
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
        config ([`SapamaConfig`]): Model configuration class with all the parameters of the model.
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
@add_start_docstrings("The bare Sapama Model transformer outputting raw hidden-states without any specific head on top.", SAPAMA_START_DOCSTRING)
class FlaxSapamaModel(FlaxSapamaPreTrainedModel): module_class = FlaxSapamaModule
append_call_sample_docstring(FlaxSapamaModel, _CHECKPOINT_FOR_DOC, FlaxBaseModelOutput, _CONFIG_FOR_DOC, real_checkpoint=_REAL_CHECKPOINT_FOR_DOC)
class FlaxSapamaForCausalLMModule(nn.Module):
    config: SapamaConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self): self.model, self.lm_head = FlaxSapamaModule(self.config, dtype=self.dtype), nn.Dense(self.config.vocab_size, use_bias=False, dtype=self.dtype, kernel_init=j_nn.initializers.normal(stddev=self.config.initializer_range))
    def __call__(self, input_ids, attention_mask=None, position_ids=None, deterministic: bool = True, init_cache: bool = False, output_attentions: bool = False,
    output_hidden_states: bool = False, return_dict: bool = True):
        outputs = self.model(input_ids, position_ids=position_ids, attention_mask=attention_mask, deterministic=deterministic, init_cache=init_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        lm_logits = self.lm_head(outputs[0])
        if not return_dict: return (lm_logits,) + outputs[1:]
        return FlaxCausalLMOutput(logits=lm_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("The Sapama Model transformer with a language modeling head (linear layer) on top.", SAPAMA_START_DOCSTRING)
class FlaxSapamaForCausalLM(FlaxSapamaPreTrainedModel):
    module_class = FlaxSapamaForCausalLMModule
    def prepare_inputs_for_generation(self, input_ids, max_length, attention_mask: Optional[j_Array] = None):
        batch_size, seq_length = input_ids.shape
        past_key_values, extended_attention_mask = self.init_cache(batch_size, max_length), jnp.ones((batch_size, max_length), dtype="i4")
        if attention_mask is not None: position_ids, extended_attention_mask = attention_mask.cumsum(axis=-1) - 1, lax.dynamic_update_slice(extended_attention_mask, attention_mask, (0, 0))
        else: position_ids = jnp.broadcast_to(jnp.arange(seq_length, dtype="i4")[None, :], (batch_size, seq_length))
        return {"past_key_values": past_key_values, "attention_mask": extended_attention_mask, "position_ids": position_ids}
    def update_inputs_for_generation(self, model_outputs, model_kwargs):
        model_kwargs["past_key_values"], model_kwargs["position_ids"] = model_outputs.past_key_values, model_kwargs["position_ids"][:, -1:] + 1
        return model_kwargs
append_call_sample_docstring(FlaxSapamaForCausalLM, _CHECKPOINT_FOR_DOC, FlaxCausalLMOutput, _CONFIG_FOR_DOC, real_checkpoint=_REAL_CHECKPOINT_FOR_DOC)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
