from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Optional, Tuple, Union
import numpy as np
import tensorflow as tf
from ...file_utils import add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward
from ...modeling_tf_outputs import (TFBaseModelOutputWithPastAndCrossAttentions, TFBaseModelOutputWithPoolingAndCrossAttentions, TFMaskedLMOutput,
TFSequenceClassifierOutput, TFTokenClassifierOutput)
from ...modeling_tf_utils import (TFMaskedLanguageModelingLoss, TFModelInputType, TFPreTrainedModel, TFSequenceClassificationLoss, TFTokenClassificationLoss,
get_initializer, keras, shape_list, unpack_inputs)
from ...tf_utils import check_embeddings_within_bounds, stable_softmax
from ...utils import logging
from .configuration_esm import EsmConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "facebook/esm2_t6_8M_UR50D"
_CONFIG_FOR_DOC = "EsmConfig"
def rotate_half(x):
    x1, x2 = tf.split(x, 2, axis=-1)
    return tf.concat((-x2, x1), axis=-1)
def apply_rotary_pos_emb(x, cos, sin):
    cos = cos[:, :, : tf.shape(x)[-2], :]
    sin = sin[:, :, : tf.shape(x)[-2], :]
    return (x * cos) + (rotate_half(x) * sin)
def symmetrize(x): return x + tf.linalg.matrix_transpose(x)
def average_product_correct(x):
    a1 = tf.reduce_sum(x, -1, keepdims=True)
    a2 = tf.reduce_sum(x, -2, keepdims=True)
    a12 = tf.reduce_sum(x, (-1, -2), keepdims=True)
    avg = a1 * a2
    avg = avg / a12
    normalized = x - avg
    return normalized
class TFRotaryEmbedding(keras.layers.Layer):
    def __init__(self, dim: int, name=None):
        super().__init__(name=name)
        self.dim = dim
    def build(self, input_shape):
        super().build(input_shape)
        self.inv_freq = self.add_weight("inv_freq", shape=(self.dim // 2,), dtype=tf.float32, initializer=get_initializer(1.0), trainable=False)
        self.inv_freq.assign(1.0 / (10000 ** (tf.range(start=0, limit=self.dim, delta=2, dtype=tf.float32) / self.dim)))
    def _compute_cos_sin(self, x, seq_dimension=2):
        seq_len = tf.shape(x)[seq_dimension]
        t = tf.range(seq_len, dtype=self.inv_freq.dtype)
        freqs = tf.einsum("i, j -> ij", t, self.inv_freq)
        emb = tf.concat((freqs, freqs), axis=-1)[None, None, :, :]
        return tf.cos(emb), tf.sin(emb)
    def call(self, q: tf.Tensor, k: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
        cos_emb, sin_emb = self._compute_cos_sin(k, seq_dimension=-2)
        return (apply_rotary_pos_emb(q, cos_emb, sin_emb), apply_rotary_pos_emb(k, cos_emb, sin_emb),)
class TFEsmContactPredictionHead(keras.layers.Layer):
    def __init__(self, in_features: int, bias=True, eos_idx: int = 2, name=None):
        super().__init__(name=name)
        self.eos_idx = eos_idx
        self.in_features = in_features
        self.regression = keras.layers.Dense(1, use_bias=bias, activation="sigmoid", name="regression")
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "regression", None) is not None:
            with tf.name_scope(self.regression.name): self.regression.build((None, self.in_features))
    def call(self, tokens, attentions):
        eos_mask = tf.cast(tokens != self.eos_idx, attentions.dtype)
        eos_mask = tf.expand_dims(eos_mask, 1) * tf.expand_dims(eos_mask, 2)
        attentions = attentions * eos_mask[:, None, None, :, :]
        attentions = attentions[..., :-1, :-1]
        attentions = attentions[..., 1:, 1:]
        batch_size, layers, heads, seqlen, _ = shape_list(attentions)
        attentions = tf.reshape(attentions, (batch_size, layers * heads, seqlen, seqlen))
        attentions = average_product_correct(symmetrize(attentions))
        attentions = tf.transpose(attentions, perm=(0, 2, 3, 1))
        return tf.squeeze(self.regression(attentions), 3)
class TFEsmEmbeddings(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.word_embeddings = keras.layers.Embedding(config.vocab_size, config.hidden_size, embeddings_initializer=get_initializer(config.initializer_range), name="word_embeddings")
        self.position_embeddings = keras.layers.Embedding(config.max_position_embeddings, config.hidden_size, embeddings_initializer=get_initializer(config.initializer_range), name="position_embeddings")
        if config.emb_layer_norm_before: self.layer_norm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layer_norm")
        else: self.layer_norm = None
        self.position_embedding_type = getattr(config, "position_embedding_type", "absolute")
        self.position_ids = tf.range(config.max_position_embeddings)[None, :]
        self.padding_idx = config.pad_token_id
        self.token_dropout = config.token_dropout
        self.mask_token_id = config.mask_token_id
        self.config = config
    def call(self, input_ids=None, attention_mask=None, position_ids=None, inputs_embeds=None, past_key_values_length=0):
        if position_ids is None:
            if input_ids is not None: position_ids = create_position_ids_from_input_ids(input_ids, self.padding_idx, past_key_values_length)
            else: position_ids = self.create_position_ids_from_inputs_embeds(inputs_embeds)
        if inputs_embeds is None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = self.word_embeddings(input_ids)
        embeddings = inputs_embeds
        if self.token_dropout:
            embeddings = tf.where((input_ids == self.mask_token_id)[:, :, None], 0.0, embeddings)
            mask_ratio_train = 0.15 * 0.8
            src_lengths = tf.cast(tf.reduce_sum(attention_mask, axis=-1), tf.float32)
            masked_tokens = input_ids == self.mask_token_id
            mask_ratio_observed = tf.math.count_nonzero(masked_tokens, dtype=tf.float32, axis=-1) / src_lengths
            embeddings = embeddings * (1 - mask_ratio_train) / (1 - mask_ratio_observed)[:, None, None]
        if self.position_embedding_type == "absolute":
            position_embeddings = self.position_embeddings(position_ids)
            embeddings += position_embeddings
        if self.layer_norm is not None: embeddings = self.layer_norm(embeddings)
        if attention_mask is not None: embeddings = embeddings * tf.cast(tf.expand_dims(attention_mask, -1), embeddings.dtype)
        return embeddings
    def create_position_ids_from_inputs_embeds(self, inputs_embeds):
        input_shape = shape_list(inputs_embeds)[:-1]
        sequence_length = input_shape[1]
        position_ids = tf.range(start=self.padding_idx + 1, limit=sequence_length + self.padding_idx + 1, dtype=tf.int64)
        return tf.broadcast_to(tf.expand_dims(position_ids, 0), input_shape)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "word_embeddings", None) is not None:
            with tf.name_scope(self.word_embeddings.name): self.word_embeddings.build(None)
        if getattr(self, "position_embeddings", None) is not None:
            with tf.name_scope(self.position_embeddings.name): self.position_embeddings.build(None)
        if getattr(self, "layer_norm", None) is not None:
            with tf.name_scope(self.layer_norm.name): self.layer_norm.build([None, None, self.config.hidden_size])
class TFEsmSelfAttention(keras.layers.Layer):
    def __init__(self, config, position_embedding_type=None, name=None):
        super().__init__(name=name)
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size ({config.hidden_size}) is not a multiple of the number of attention heads ({config.num_attention_heads})")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="query")
        self.key = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="key")
        self.value = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="value")
        self.dropout = keras.layers.Dropout(config.attention_probs_dropout_prob)
        self.position_embedding_type = position_embedding_type or getattr(config, "position_embedding_type", "absolute")
        self.rotary_embeddings = None
        if self.position_embedding_type == "relative_key" or self.position_embedding_type == "relative_key_query":
            self.max_position_embeddings = config.max_position_embeddings
            self.distance_embedding = keras.layers.Embedding(2 * config.max_position_embeddings - 1, self.attention_head_size, embeddings_initializer=get_initializer(config.initializer_range))
        elif self.position_embedding_type == "rotary": self.rotary_embeddings = TFRotaryEmbedding(dim=self.attention_head_size, name="rotary_embeddings")
        self.is_decoder = config.is_decoder
        self.config = config
    def transpose_for_scores(self, x: tf.Tensor) -> tf.Tensor:
        new_x_shape = shape_list(x)[:-1] + [self.num_attention_heads, self.attention_head_size]
        x = tf.reshape(x, new_x_shape)
        return tf.transpose(x, perm=(0, 2, 1, 3))
    def call(self, hidden_states: tf.Tensor, attention_mask: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, encoder_hidden_states: tf.Tensor | None = None,
    encoder_attention_mask: tf.Tensor | None = None, past_key_value: Tuple[Tuple[tf.Tensor]] | None = None, output_attentions: Optional[bool] = False,
    training: bool = False) -> Tuple[tf.Tensor]:
        mixed_query_layer = self.query(hidden_states)
        is_cross_attention = encoder_hidden_states is not None
        if is_cross_attention and past_key_value is not None:
            key_layer = past_key_value[0]
            value_layer = past_key_value[1]
            attention_mask = encoder_attention_mask
        elif is_cross_attention:
            key_layer = self.transpose_for_scores(self.key(encoder_hidden_states))
            value_layer = self.transpose_for_scores(self.value(encoder_hidden_states))
            attention_mask = encoder_attention_mask
        elif past_key_value is not None:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))
            key_layer = tf.concat([past_key_value[0], key_layer], axis=2)
            value_layer = tf.concat([past_key_value[1], value_layer], axis=2)
        else:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)
        query_layer = query_layer * self.attention_head_size**-0.5
        if self.is_decoder: past_key_value = (key_layer, value_layer)
        if self.position_embedding_type == "rotary": query_layer, key_layer = self.rotary_embeddings(query_layer, key_layer)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        if self.position_embedding_type == "relative_key" or self.position_embedding_type == "relative_key_query":
            seq_length = shape_list(hidden_states)[1]
            position_ids_l = tf.expand_dims(tf.range(seq_length, dtype=tf.int64), -1)
            position_ids_r = tf.expand_dims(tf.range(seq_length, dtype=tf.int64), 0)
            distance = position_ids_l - position_ids_r
            positional_embedding = self.distance_embedding(distance + self.max_position_embeddings - 1)
            positional_embedding = tf.cast(positional_embedding, query_layer.dtype)  # fp16 compatibility
            if self.position_embedding_type == "relative_key":
                relative_position_scores = tf.einsum("bhld,lrd->bhlr", query_layer, positional_embedding)
                attention_scores = attention_scores + relative_position_scores
            elif self.position_embedding_type == "relative_key_query":
                relative_position_scores_query = tf.einsum("bhld,lrd->bhlr", query_layer, positional_embedding)
                relative_position_scores_key = tf.einsum("bhrd,lrd->bhlr", key_layer, positional_embedding)
                attention_scores = attention_scores + relative_position_scores_query + relative_position_scores_key
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = stable_softmax(attention_scores, axis=-1)
        attention_probs = self.dropout(attention_probs, training=training)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        context_layer = attention_probs @ value_layer
        context_layer = tf.transpose(context_layer, perm=(0, 2, 1, 3))
        new_context_layer_shape = shape_list(context_layer)[:-2] + [self.all_head_size]
        context_layer = tf.reshape(context_layer, new_context_layer_shape)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        if self.is_decoder: outputs = outputs + (past_key_value,)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "query", None) is not None:
            with tf.name_scope(self.query.name): self.query.build([None, None, self.config.hidden_size])
        if getattr(self, "key", None) is not None:
            with tf.name_scope(self.key.name): self.key.build([None, None, self.config.hidden_size])
        if getattr(self, "value", None) is not None:
            with tf.name_scope(self.value.name): self.value.build([None, None, self.config.hidden_size])
        if getattr(self, "rotary_embeddings", None) is not None:
            with tf.name_scope(self.rotary_embeddings.name): self.rotary_embeddings.build(None)
class TFEsmSelfOutput(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states, input_tensor, training=False):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states, training=training)
        hidden_states += input_tensor
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFEsmAttention(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.self = TFEsmSelfAttention(config, name="self")
        self.output_layer = TFEsmSelfOutput(config, name="output")
        self.pruned_heads = set()
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.config = config
    def prune_heads(self, heads): raise NotImplementedError
    def call(self, hidden_states, attention_mask=None, head_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, past_key_value=None, output_attentions=False, training=False):
        hidden_states_ln = self.LayerNorm(hidden_states)
        self_outputs = self.self(hidden_states_ln, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, past_key_value, output_attentions, training)
        attention_output = self.output_layer(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "self", None) is not None:
            with tf.name_scope(self.self.name): self.self.build(None)
        if getattr(self, "output_layer", None) is not None:
            with tf.name_scope(self.output_layer.name): self.output_layer.build(None)
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFEsmIntermediate(keras.layers.Layer):
    def __init__(self, config: EsmConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.intermediate_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.config = config
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = tf.nn.gelu(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFEsmOutput(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states, input_tensor, training=False):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states, training=training)
        hidden_states += input_tensor
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.intermediate_size])
class TFEsmLayer(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.attention = TFEsmAttention(config, name="attention")
        self.is_decoder = config.is_decoder
        self.add_cross_attention = config.add_cross_attention
        if self.add_cross_attention:
            if not self.is_decoder: raise RuntimeError(f"{self} should be used as a decoder model if cross attention is added")
            self.crossattention = TFEsmAttention(config)
        self.intermediate = TFEsmIntermediate(config, name="intermediate")
        self.output_layer = TFEsmOutput(config, name="output")
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.config = config
    def call(self, hidden_states, attention_mask=None, head_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, past_key_value=None, output_attentions=False, training=False):
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        self_attention_outputs = self.attention(hidden_states, attention_mask, head_mask, output_attentions=output_attentions, past_key_value=self_attn_past_key_value, training=training)
        attention_output = self_attention_outputs[0]
        if self.is_decoder:
            outputs = self_attention_outputs[1:-1]
            present_key_value = self_attention_outputs[-1]
        else: outputs = self_attention_outputs[1:]
        cross_attn_present_key_value = None
        if self.is_decoder and encoder_hidden_states is not None:
            if not hasattr(self, "crossattention"): raise AttributeError(f"If `encoder_hidden_states` are passed, {self} has to be instantiated with cross-attention layers by setting `config.add_cross_attention=True`")
            cross_attn_past_key_value = past_key_value[-2:] if past_key_value is not None else None
            cross_attention_outputs = self.crossattention(attention_output, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, cross_attn_past_key_value,
            output_attentions, training=training)
            attention_output = cross_attention_outputs[0]
            outputs = outputs + cross_attention_outputs[1:-1]
            cross_attn_present_key_value = cross_attention_outputs[-1]
            present_key_value = present_key_value + cross_attn_present_key_value
        layernorm_output = self.LayerNorm(attention_output)
        intermediate_output = self.intermediate(hidden_states=layernorm_output)
        layer_output = self.output_layer(hidden_states=intermediate_output, input_tensor=attention_output, training=training)
        outputs = (layer_output,) + outputs
        if self.is_decoder: outputs = outputs + (present_key_value,)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "attention", None) is not None:
            with tf.name_scope(self.attention.name): self.attention.build(None)
        if getattr(self, "intermediate", None) is not None:
            with tf.name_scope(self.intermediate.name): self.intermediate.build(None)
        if getattr(self, "output_layer", None) is not None:
            with tf.name_scope(self.output_layer.name): self.output_layer.build(None)
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFEsmEncoder(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.config = config
        self.layer = [TFEsmLayer(config, name=f"layer_._{i}") for i in range(config.num_hidden_layers)]
        self.emb_layer_norm_after = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="emb_layer_norm_after")
    def call(self, hidden_states, attention_mask=None, head_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, past_key_values=None, use_cache=None,
    output_attentions=False, output_hidden_states=False, return_dict=True, training=False):
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        all_cross_attentions = () if output_attentions and self.config.add_cross_attention else None
        next_decoder_cache = () if use_cache else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_head_mask = head_mask[i] if head_mask is not None else None
            past_key_value = past_key_values[i] if past_key_values is not None else None
            layer_outputs = layer_module(hidden_states, attention_mask, layer_head_mask, encoder_hidden_states, encoder_attention_mask, past_key_value, output_attentions, training)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache += (layer_outputs[-1],)
            if output_attentions:
                all_self_attentions = all_self_attentions + (layer_outputs[1],)
                if self.config.add_cross_attention: all_cross_attentions = all_cross_attentions + (layer_outputs[2],)
        if self.emb_layer_norm_after: hidden_states = self.emb_layer_norm_after(hidden_states)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, next_decoder_cache, all_hidden_states, all_self_attentions, all_cross_attentions] if v is not None)
        return TFBaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=next_decoder_cache, hidden_states=all_hidden_states,
        attentions=all_self_attentions, cross_attentions=all_cross_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "emb_layer_norm_after", None) is not None:
            with tf.name_scope(self.emb_layer_norm_after.name): self.emb_layer_norm_after.build([None, None, self.config.hidden_size])
        if getattr(self, "layer", None) is not None:
            for layer in self.layer:
                with tf.name_scope(layer.name): layer.build(None)
class TFEsmPooler(keras.layers.Layer):
    def __init__(self, config: EsmConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), activation="tanh", name="dense")
        self.config = config
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(inputs=first_token_tensor)
        return pooled_output
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFEsmPreTrainedModel(TFPreTrainedModel):
    config_class = EsmConfig
    base_model_prefix = "esm"
ESM_START_DOCSTRING = r"""
    This model inherits from [`TFPreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a Keras [Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model) subclass. Use it as a
    regular Keras model and refer to the TF/Keras documentation for all matters related to general usage and behavior.
    Parameters:
        config ([`EsmConfig`]): Model configuration class with all the parameters of the
            model. Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~TFPreTrainedModel.from_pretrained`] method to load the model weights.
"""
ESM_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`tf.Tensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`tf.Tensor` of shape `(0)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`tf.Tensor` of shape `(0)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`tf.Tensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        inputs_embeds (`tf.Tensor` of shape `(0, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare ESM Model transformer outputting raw hidden-states without any specific head on top.", ESM_START_DOCSTRING)
class TFEsmMainLayer(keras.layers.Layer):
    _keys_to_ignore_on_load_missing = [r"position_ids"]
    def __init__(self, config, add_pooling_layer=True, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.config = config
        self.is_decoder = config.is_decoder
        self.embeddings = TFEsmEmbeddings(config, name="embeddings")
        self.encoder = TFEsmEncoder(config, name="encoder")
        self.pooler = TFEsmPooler(config, name="pooler") if add_pooling_layer else None
        self.contact_head = TFEsmContactPredictionHead(in_features=self.config.num_hidden_layers * self.config.num_attention_heads, bias=True, name="contact_head")
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name): self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name): self.encoder.build(None)
        if getattr(self, "pooler", None) is not None:
            with tf.name_scope(self.pooler.name): self.pooler.build(None)
        if getattr(self, "contact_head", None) is not None:
            with tf.name_scope(self.contact_head.name): self.contact_head.build(None)
    def get_input_embeddings(self): return self.embeddings.word_embeddings
    def set_input_embeddings(self, value: tf.Variable):
        self.embeddings.word_embeddings.weight = value
        self.embeddings.vocab_size = shape_list(value)[0]
    def _prune_heads(self, heads_to_prune): raise NotImplementedError
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None,
    head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None,
    encoder_attention_mask: np.ndarray | tf.Tensor | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: bool = False) -> Union[TFBaseModelOutputWithPoolingAndCrossAttentions, Tuple[tf.Tensor]]:
        if not self.config.is_decoder: use_cache = False
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None: input_shape = shape_list(input_ids)
        elif inputs_embeds is not None: input_shape = shape_list(inputs_embeds)[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        batch_size, seq_length = input_shape
        if past_key_values is None:
            past_key_values_length = 0
            past_key_values = [None] * len(self.encoder.layer)
        else: past_key_values_length = shape_list(past_key_values[0][0])[-2]
        if attention_mask is None: attention_mask = tf.fill(dims=(batch_size, seq_length + past_key_values_length), value=1)
        embedding_output = self.embeddings(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, inputs_embeds=inputs_embeds,
        past_key_values_length=past_key_values_length, training=training)
        attention_mask_shape = shape_list(attention_mask)
        mask_seq_length = seq_length + past_key_values_length
        if self.is_decoder:
            seq_ids = tf.range(mask_seq_length)
            causal_mask = tf.less_equal(tf.tile(seq_ids[None, None, :], (batch_size, mask_seq_length, 1)), seq_ids[None, :, None])
            causal_mask = tf.cast(causal_mask, dtype=attention_mask.dtype)
            extended_attention_mask = causal_mask * attention_mask[:, None, :]
            attention_mask_shape = shape_list(extended_attention_mask)
            extended_attention_mask = tf.reshape(extended_attention_mask, (attention_mask_shape[0], 1, attention_mask_shape[1], attention_mask_shape[2]))
            if past_key_values[0] is not None: extended_attention_mask = extended_attention_mask[:, :, -seq_length:, :]
        else: extended_attention_mask = tf.reshape(attention_mask, (attention_mask_shape[0], 1, 1, attention_mask_shape[1]))
        extended_attention_mask = tf.cast(extended_attention_mask, dtype=embedding_output.dtype)
        one_cst = tf.constant(1.0, dtype=embedding_output.dtype)
        ten_thousand_cst = tf.constant(-10000.0, dtype=embedding_output.dtype)
        extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)
        if self.is_decoder and encoder_attention_mask is not None:
            encoder_attention_mask = tf.cast(encoder_attention_mask, dtype=extended_attention_mask.dtype)
            num_dims_encoder_attention_mask = len(shape_list(encoder_attention_mask))
            if num_dims_encoder_attention_mask == 3: encoder_extended_attention_mask = encoder_attention_mask[:, None, :, :]
            if num_dims_encoder_attention_mask == 2: encoder_extended_attention_mask = encoder_attention_mask[:, None, None, :]
            encoder_extended_attention_mask = (1.0 - encoder_extended_attention_mask) * -10000.0
        else: encoder_extended_attention_mask = None
        if head_mask is not None: raise NotImplementedError
        else: head_mask = [None] * self.config.num_hidden_layers
        encoder_outputs = self.encoder(hidden_states=embedding_output, attention_mask=extended_attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=encoder_extended_attention_mask, past_key_values=past_key_values, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states,
        return_dict=return_dict, training=training)
        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(hidden_states=sequence_output) if self.pooler is not None else None
        if not return_dict: return (sequence_output, pooled_output) + encoder_outputs[1:]
        return TFBaseModelOutputWithPoolingAndCrossAttentions(last_hidden_state=sequence_output, pooler_output=pooled_output, past_key_values=encoder_outputs.past_key_values,
        hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions, cross_attentions=encoder_outputs.cross_attentions)
    def predict_contacts(self, tokens, attention_mask):
        attns = self(tokens, attention_mask=attention_mask, return_dict=True, output_attentions=True).attentions
        attns = tf.stack(attns, axis=1)
        attention_mask = tf.cast(attention_mask, attns.dtype)
        attns *= attention_mask[:, None, None, None]
        attns *= attention_mask[:, None, None, :, None]
        return self.contact_head(tokens, attns)
@add_start_docstrings("The bare ESM Model transformer outputting raw hidden-states without any specific head on top.", ESM_START_DOCSTRING)
class TFEsmModel(TFEsmPreTrainedModel):
    def __init__(self, config: EsmConfig, add_pooling_layer=True, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.esm = TFEsmMainLayer(config, add_pooling_layer=add_pooling_layer, name="esm")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ESM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None,
    head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None,
    encoder_attention_mask: np.ndarray | tf.Tensor | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: Optional[bool] = False) -> Union[TFBaseModelOutputWithPoolingAndCrossAttentions, Tuple[tf.Tensor]]:
        outputs = self.esm(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds,
        encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask, past_key_values=past_key_values, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        return outputs
    def predict_contacts(self, tokens, attention_mask): return self.esm.predict_contacts(tokens, attention_mask)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "esm", None) is not None:
            with tf.name_scope(self.esm.name): self.esm.build(None)
@add_start_docstrings("""ESM Model with a `language modeling` head on top.""", ESM_START_DOCSTRING)
class TFEsmForMaskedLM(TFEsmPreTrainedModel, TFMaskedLanguageModelingLoss):
    _keys_to_ignore_on_load_missing = [r"position_ids"]
    _keys_to_ignore_on_load_unexpected = [r"pooler"]
    def __init__(self, config):
        super().__init__(config)
        if config.is_decoder: logger.warning("If you want to use `EsmForMaskedLM` make sure `config.is_decoder=False` for bi-directional self-attention.")
        self.esm = TFEsmMainLayer(config, add_pooling_layer=False, name="esm")
        self.lm_head = TFEsmLMHead(config, name="lm_head")
        if config.tie_word_embeddings:
            with tf.name_scope(os.path.join(self._name_scope(), "esm", "embeddings", "word_embeddings")): self.esm.embeddings.word_embeddings.build((None, None))
            self.lm_head.decoder = self.esm.embeddings.word_embeddings.weights[0]
    def get_output_embeddings(self): return self.lm_head.decoder
    def set_output_embeddings(self, new_embeddings): self.lm_head.decoder = new_embeddings
    def get_lm_head(self): return self.lm_head
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ESM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None,
    head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None,
    encoder_attention_mask: np.ndarray | tf.Tensor | None = None, labels: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: bool = False) -> Union[TFMaskedLMOutput, Tuple[tf.Tensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.esm(input_ids, attention_mask=attention_mask, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=encoder_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        prediction_scores = self.lm_head(sequence_output)
        masked_lm_loss = None
        if labels is not None: masked_lm_loss = self.hf_compute_loss(labels=labels, logits=prediction_scores)
        if not return_dict:
            output = (prediction_scores,) + outputs[2:]
            return ((masked_lm_loss,) + output) if masked_lm_loss is not None else output
        return TFMaskedLMOutput(loss=masked_lm_loss, logits=prediction_scores, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def predict_contacts(self, tokens, attention_mask): return self.esm.predict_contacts(tokens, attention_mask)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "esm", None) is not None:
            with tf.name_scope(self.esm.name): self.esm.build(None)
        if getattr(self, "lm_head", None) is not None:
            with tf.name_scope(self.lm_head.name): self.lm_head.build(None)
class TFEsmLMHead(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.layer_norm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layer_norm")
        if config.tie_word_embeddings: self.decoder = None
        else: self.decoder = keras.layers.Dense(config.vocab_size, kernel_initializer=get_initializer(config.initializer_range), name="decoder", use_bias=False)
        self.config = config
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        self.bias = self.add_weight("bias", shape=(self.config.vocab_size,), initializer="zeros", trainable=True)
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "layer_norm", None) is not None:
            with tf.name_scope(self.layer_norm.name): self.layer_norm.build([None, None, self.config.hidden_size])
        if getattr(self, "decoder", None) is not None and not self.config.tie_word_embeddings:
            with tf.name_scope(self.decoder.name): self.decoder.build([None, None, self.config.hidden_size])
    def get_bias(self): return {"bias": self.bias}
    def call(self, features):
        x = self.dense(features)
        x = tf.nn.gelu(x)
        x = self.layer_norm(x)
        if self.config.tie_word_embeddings: x = tf.matmul(x, self.decoder, transpose_b=True) + self.bias
        else: x = self.decoder(x) + self.bias
        return x
@add_start_docstrings("ESM Model transformer with a sequence classification/regression head on top (a linear layer on top of the pooled output) e.g. for GLUE tasks.", ESM_START_DOCSTRING)
class TFEsmForSequenceClassification(TFEsmPreTrainedModel, TFSequenceClassificationLoss):
    _keys_to_ignore_on_load_missing = [r"position_ids"]
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.config = config
        self.esm = TFEsmMainLayer(config, add_pooling_layer=False, name="esm")
        self.classifier = TFEsmClassificationHead(config, name="classifier")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ESM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None,
    head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, labels: np.ndarray | tf.Tensor | None = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: bool = False) -> Union[TFSequenceClassifierOutput, Tuple[tf.Tensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.esm(input_ids, attention_mask=attention_mask, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        logits = self.classifier(sequence_output)
        loss = None if labels is None else self.hf_compute_loss(labels, logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "esm", None) is not None:
            with tf.name_scope(self.esm.name): self.esm.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name): self.classifier.build(None)
@add_start_docstrings("ESM Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", ESM_START_DOCSTRING)
class TFEsmForTokenClassification(TFEsmPreTrainedModel, TFTokenClassificationLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler"]
    _keys_to_ignore_on_load_missing = [r"position_ids"]
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.esm = TFEsmMainLayer(config, add_pooling_layer=False, name="esm")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.classifier = keras.layers.Dense(config.num_labels, name="classifier")
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ESM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None,
    head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, labels: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: bool = False) -> Union[TFTokenClassifierOutput, Tuple[tf.Tensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.esm(input_ids, attention_mask=attention_mask, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        sequence_output = self.dropout(sequence_output, training=training)
        logits = self.classifier(sequence_output)
        loss = None if labels is None else self.hf_compute_loss(labels, logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFTokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "esm", None) is not None:
            with tf.name_scope(self.esm.name): self.esm.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name): self.classifier.build([None, None, self.config.hidden_size])
class TFEsmClassificationHead(keras.layers.Layer):
    def __init__(self, config, name=None):
        super().__init__(name=name)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), activation="tanh", name="dense")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.out_proj = keras.layers.Dense(config.num_labels, kernel_initializer=get_initializer(config.initializer_range), activation="linear", name="out_proj")
        self.config = config
    def call(self, features, training=False):
        x = features[:, 0, :]
        x = self.dropout(x, training=training)
        x = self.dense(x)
        x = self.dropout(x, training=training)
        x = self.out_proj(x)
        return x
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "out_proj", None) is not None:
            with tf.name_scope(self.out_proj.name): self.out_proj.build([None, None, self.config.hidden_size])
def create_position_ids_from_input_ids(input_ids, padding_idx, past_key_values_length=0):
    mask = tf.cast(input_ids != padding_idx, tf.int64)
    incremental_indices = (tf.cumsum(mask, axis=1) + past_key_values_length) * mask
    return incremental_indices + padding_idx
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
