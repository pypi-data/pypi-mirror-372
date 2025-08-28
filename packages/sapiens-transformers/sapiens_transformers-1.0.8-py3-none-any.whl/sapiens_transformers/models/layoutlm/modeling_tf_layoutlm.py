from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
import warnings
from typing import Dict, Optional, Tuple, Union
import numpy as np
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_outputs import (TFBaseModelOutputWithPastAndCrossAttentions, TFBaseModelOutputWithPoolingAndCrossAttentions, TFMaskedLMOutput, TFQuestionAnsweringModelOutput,
TFSequenceClassifierOutput, TFTokenClassifierOutput)
from ...modeling_tf_utils import (TFMaskedLanguageModelingLoss, TFModelInputType, TFPreTrainedModel, TFQuestionAnsweringLoss, TFSequenceClassificationLoss, TFTokenClassificationLoss,
get_initializer, keras, keras_serializable, unpack_inputs)
from ...tf_utils import check_embeddings_within_bounds, shape_list, stable_softmax
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_layoutlm import LayoutLMConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "LayoutLMConfig"
class TFLayoutLMEmbeddings(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.hidden_size = config.hidden_size
        self.max_position_embeddings = config.max_position_embeddings
        self.max_2d_position_embeddings = config.max_2d_position_embeddings
        self.initializer_range = config.initializer_range
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
    def build(self, input_shape=None):
        with tf.name_scope("word_embeddings"): self.weight = self.add_weight(name="weight", shape=[self.config.vocab_size, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("token_type_embeddings"): self.token_type_embeddings = self.add_weight(name="embeddings", shape=[self.config.type_vocab_size, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("position_embeddings"): self.position_embeddings = self.add_weight(name="embeddings", shape=[self.max_position_embeddings, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("x_position_embeddings"): self.x_position_embeddings = self.add_weight(name="embeddings", shape=[self.max_2d_position_embeddings, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("y_position_embeddings"): self.y_position_embeddings = self.add_weight(name="embeddings", shape=[self.max_2d_position_embeddings, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("h_position_embeddings"): self.h_position_embeddings = self.add_weight(name="embeddings", shape=[self.max_2d_position_embeddings, self.hidden_size], initializer=get_initializer(self.initializer_range))
        with tf.name_scope("w_position_embeddings"): self.w_position_embeddings = self.add_weight(name="embeddings", shape=[self.max_2d_position_embeddings, self.hidden_size], initializer=get_initializer(self.initializer_range))
        if self.built: return
        self.built = True
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
    def call(self, input_ids: tf.Tensor = None, bbox: tf.Tensor = None, position_ids: tf.Tensor = None, token_type_ids: tf.Tensor = None, inputs_embeds: tf.Tensor = None, training: bool = False) -> tf.Tensor:
        assert not (input_ids is None and inputs_embeds is None)
        if input_ids is not None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = tf.gather(params=self.weight, indices=input_ids)
        input_shape = shape_list(inputs_embeds)[:-1]
        if token_type_ids is None: token_type_ids = tf.fill(dims=input_shape, value=0)
        if position_ids is None: position_ids = tf.expand_dims(tf.range(start=0, limit=input_shape[-1]), axis=0)
        if position_ids is None: position_ids = tf.expand_dims(tf.range(start=0, limit=input_shape[-1]), axis=0)
        if bbox is None: bbox = bbox = tf.fill(input_shape + [4], value=0)
        try:
            left_position_embeddings = tf.gather(self.x_position_embeddings, bbox[:, :, 0])
            upper_position_embeddings = tf.gather(self.y_position_embeddings, bbox[:, :, 1])
            right_position_embeddings = tf.gather(self.x_position_embeddings, bbox[:, :, 2])
            lower_position_embeddings = tf.gather(self.y_position_embeddings, bbox[:, :, 3])
        except IndexError as e: raise IndexError("The `bbox`coordinate values should be within 0-1000 range.") from e
        h_position_embeddings = tf.gather(self.h_position_embeddings, bbox[:, :, 3] - bbox[:, :, 1])
        w_position_embeddings = tf.gather(self.w_position_embeddings, bbox[:, :, 2] - bbox[:, :, 0])
        position_embeds = tf.gather(params=self.position_embeddings, indices=position_ids)
        token_type_embeds = tf.gather(params=self.token_type_embeddings, indices=token_type_ids)
        final_embeddings = (inputs_embeds + position_embeds + token_type_embeds + left_position_embeddings + upper_position_embeddings + right_position_embeddings + lower_position_embeddings + h_position_embeddings + w_position_embeddings)
        final_embeddings = self.LayerNorm(inputs=final_embeddings)
        final_embeddings = self.dropout(inputs=final_embeddings, training=training)
        return final_embeddings
class TFLayoutLMSelfAttention(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        if config.hidden_size % config.num_attention_heads != 0: raise ValueError(f"The hidden size ({config.hidden_size}) is not a multiple of the number of attention heads ({config.num_attention_heads})")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.sqrt_att_head_size = math.sqrt(self.attention_head_size)
        self.query = keras.layers.Dense(units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="query")
        self.key = keras.layers.Dense(units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="key")
        self.value = keras.layers.Dense(units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="value")
        self.dropout = keras.layers.Dropout(rate=config.attention_probs_dropout_prob)
        self.is_decoder = config.is_decoder
        self.config = config
    def transpose_for_scores(self, tensor: tf.Tensor, batch_size: int) -> tf.Tensor:
        tensor = tf.reshape(tensor=tensor, shape=(batch_size, -1, self.num_attention_heads, self.attention_head_size))
        return tf.transpose(tensor, perm=[0, 2, 1, 3])
    def call(self, hidden_states: tf.Tensor, attention_mask: tf.Tensor, head_mask: tf.Tensor, encoder_hidden_states: tf.Tensor, encoder_attention_mask: tf.Tensor,
    past_key_value: Tuple[tf.Tensor], output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        batch_size = shape_list(hidden_states)[0]
        mixed_query_layer = self.query(inputs=hidden_states)
        is_cross_attention = encoder_hidden_states is not None
        if is_cross_attention and past_key_value is not None:
            key_layer = past_key_value[0]
            value_layer = past_key_value[1]
            attention_mask = encoder_attention_mask
        elif is_cross_attention:
            key_layer = self.transpose_for_scores(self.key(inputs=encoder_hidden_states), batch_size)
            value_layer = self.transpose_for_scores(self.value(inputs=encoder_hidden_states), batch_size)
            attention_mask = encoder_attention_mask
        elif past_key_value is not None:
            key_layer = self.transpose_for_scores(self.key(inputs=hidden_states), batch_size)
            value_layer = self.transpose_for_scores(self.value(inputs=hidden_states), batch_size)
            key_layer = tf.concat([past_key_value[0], key_layer], axis=2)
            value_layer = tf.concat([past_key_value[1], value_layer], axis=2)
        else:
            key_layer = self.transpose_for_scores(self.key(inputs=hidden_states), batch_size)
            value_layer = self.transpose_for_scores(self.value(inputs=hidden_states), batch_size)
        query_layer = self.transpose_for_scores(mixed_query_layer, batch_size)
        if self.is_decoder: past_key_value = (key_layer, value_layer)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        dk = tf.cast(self.sqrt_att_head_size, dtype=attention_scores.dtype)
        attention_scores = tf.divide(attention_scores, dk)
        if attention_mask is not None: attention_scores = tf.add(attention_scores, attention_mask)
        attention_probs = stable_softmax(logits=attention_scores, axis=-1)
        attention_probs = self.dropout(inputs=attention_probs, training=training)
        if head_mask is not None: attention_probs = tf.multiply(attention_probs, head_mask)
        attention_output = tf.matmul(attention_probs, value_layer)
        attention_output = tf.transpose(attention_output, perm=[0, 2, 1, 3])
        attention_output = tf.reshape(tensor=attention_output, shape=(batch_size, -1, self.all_head_size))
        outputs = (attention_output, attention_probs) if output_attentions else (attention_output,)
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
class TFLayoutLMSelfOutput(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states: tf.Tensor, input_tensor: tf.Tensor, training: bool = False) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.dropout(inputs=hidden_states, training=training)
        hidden_states = self.LayerNorm(inputs=hidden_states + input_tensor)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFLayoutLMAttention(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.self_attention = TFLayoutLMSelfAttention(config, name="self")
        self.dense_output = TFLayoutLMSelfOutput(config, name="output")
    def prune_heads(self, heads): raise NotImplementedError
    def call(self, input_tensor: tf.Tensor, attention_mask: tf.Tensor, head_mask: tf.Tensor, encoder_hidden_states: tf.Tensor, encoder_attention_mask: tf.Tensor,
    past_key_value: Tuple[tf.Tensor], output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        self_outputs = self.self_attention(hidden_states=input_tensor, attention_mask=attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=encoder_attention_mask, past_key_value=past_key_value, output_attentions=output_attentions, training=training)
        attention_output = self.dense_output(hidden_states=self_outputs[0], input_tensor=input_tensor, training=training)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "self_attention", None) is not None:
            with tf.name_scope(self.self_attention.name): self.self_attention.build(None)
        if getattr(self, "dense_output", None) is not None:
            with tf.name_scope(self.dense_output.name): self.dense_output.build(None)
class TFLayoutLMIntermediate(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.intermediate_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = get_tf_activation(config.hidden_act)
        else: self.intermediate_act_fn = config.hidden_act
        self.config = config
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFLayoutLMOutput(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states: tf.Tensor, input_tensor: tf.Tensor, training: bool = False) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.dropout(inputs=hidden_states, training=training)
        hidden_states = self.LayerNorm(inputs=hidden_states + input_tensor)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.intermediate_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFLayoutLMLayer(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.attention = TFLayoutLMAttention(config, name="attention")
        self.is_decoder = config.is_decoder
        self.add_cross_attention = config.add_cross_attention
        if self.add_cross_attention:
            if not self.is_decoder: raise ValueError(f"{self} should be used as a decoder model if cross attention is added")
            self.crossattention = TFLayoutLMAttention(config, name="crossattention")
        self.intermediate = TFLayoutLMIntermediate(config, name="intermediate")
        self.bert_output = TFLayoutLMOutput(config, name="output")
    def call(self, hidden_states: tf.Tensor, attention_mask: tf.Tensor, head_mask: tf.Tensor, encoder_hidden_states: tf.Tensor | None, encoder_attention_mask: tf.Tensor | None,
    past_key_value: Tuple[tf.Tensor] | None, output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        self_attention_outputs = self.attention(input_tensor=hidden_states, attention_mask=attention_mask, head_mask=head_mask, encoder_hidden_states=None, encoder_attention_mask=None,
        past_key_value=self_attn_past_key_value, output_attentions=output_attentions, training=training)
        attention_output = self_attention_outputs[0]
        if self.is_decoder:
            outputs = self_attention_outputs[1:-1]
            present_key_value = self_attention_outputs[-1]
        else: outputs = self_attention_outputs[1:]
        cross_attn_present_key_value = None
        if self.is_decoder and encoder_hidden_states is not None:
            if not hasattr(self, "crossattention"): raise ValueError(f"If `encoder_hidden_states` are passed, {self} has to be instantiated with cross-attention layers by setting `config.add_cross_attention=True`")
            cross_attn_past_key_value = past_key_value[-2:] if past_key_value is not None else None
            cross_attention_outputs = self.crossattention(input_tensor=attention_output, attention_mask=attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask, past_key_value=cross_attn_past_key_value, output_attentions=output_attentions, training=training)
            attention_output = cross_attention_outputs[0]
            outputs = outputs + cross_attention_outputs[1:-1]
            cross_attn_present_key_value = cross_attention_outputs[-1]
            present_key_value = present_key_value + cross_attn_present_key_value
        intermediate_output = self.intermediate(hidden_states=attention_output)
        layer_output = self.bert_output(hidden_states=intermediate_output, input_tensor=attention_output, training=training)
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
        if getattr(self, "bert_output", None) is not None:
            with tf.name_scope(self.bert_output.name): self.bert_output.build(None)
        if getattr(self, "crossattention", None) is not None:
            with tf.name_scope(self.crossattention.name): self.crossattention.build(None)
class TFLayoutLMEncoder(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.layer = [TFLayoutLMLayer(config, name=f"layer_._{i}") for i in range(config.num_hidden_layers)]
    def call(self, hidden_states: tf.Tensor, attention_mask: tf.Tensor, head_mask: tf.Tensor, encoder_hidden_states: tf.Tensor | None, encoder_attention_mask: tf.Tensor | None,
    past_key_values: Tuple[Tuple[tf.Tensor]] | None, use_cache: Optional[bool], output_attentions: bool, output_hidden_states: bool, return_dict: bool,
    training: bool = False) -> Union[TFBaseModelOutputWithPastAndCrossAttentions, Tuple[tf.Tensor]]:
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        all_cross_attentions = () if output_attentions and self.config.add_cross_attention else None
        next_decoder_cache = () if use_cache else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            past_key_value = past_key_values[i] if past_key_values is not None else None
            layer_outputs = layer_module(hidden_states=hidden_states, attention_mask=attention_mask, head_mask=head_mask[i], encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask, past_key_value=past_key_value, output_attentions=output_attentions, training=training)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache += (layer_outputs[-1],)
            if output_attentions:
                all_attentions = all_attentions + (layer_outputs[1],)
                if self.config.add_cross_attention and encoder_hidden_states is not None: all_cross_attentions = all_cross_attentions + (layer_outputs[2],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_attentions, all_cross_attentions] if v is not None)
        return TFBaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=next_decoder_cache, hidden_states=all_hidden_states, attentions=all_attentions, cross_attentions=all_cross_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layer", None) is not None:
            for layer in self.layer:
                with tf.name_scope(layer.name): layer.build(None)
class TFLayoutLMPooler(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
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
class TFLayoutLMPredictionHeadTransform(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        if isinstance(config.hidden_act, str): self.transform_act_fn = get_tf_activation(config.hidden_act)
        else: self.transform_act_fn = config.hidden_act
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.config = config
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(inputs=hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFLayoutLMLMPredictionHead(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, input_embeddings: keras.layers.Layer, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.hidden_size = config.hidden_size
        self.transform = TFLayoutLMPredictionHeadTransform(config, name="transform")
        self.input_embeddings = input_embeddings
    def build(self, input_shape=None):
        self.bias = self.add_weight(shape=(self.config.vocab_size,), initializer="zeros", trainable=True, name="bias")
        if self.built: return
        self.built = True
        if getattr(self, "transform", None) is not None:
            with tf.name_scope(self.transform.name): self.transform.build(None)
    def get_output_embeddings(self) -> keras.layers.Layer: return self.input_embeddings
    def set_output_embeddings(self, value: tf.Variable):
        self.input_embeddings.weight = value
        self.input_embeddings.vocab_size = shape_list(value)[0]
    def get_bias(self) -> Dict[str, tf.Variable]: return {"bias": self.bias}
    def set_bias(self, value: tf.Variable):
        self.bias = value["bias"]
        self.config.vocab_size = shape_list(value["bias"])[0]
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.transform(hidden_states=hidden_states)
        seq_length = shape_list(hidden_states)[1]
        hidden_states = tf.reshape(tensor=hidden_states, shape=[-1, self.hidden_size])
        hidden_states = tf.matmul(a=hidden_states, b=self.input_embeddings.weight, transpose_b=True)
        hidden_states = tf.reshape(tensor=hidden_states, shape=[-1, seq_length, self.config.vocab_size])
        hidden_states = tf.nn.bias_add(value=hidden_states, bias=self.bias)
        return hidden_states
class TFLayoutLMMLMHead(keras.layers.Layer):
    def __init__(self, config: LayoutLMConfig, input_embeddings: keras.layers.Layer, **kwargs):
        super().__init__(**kwargs)
        self.predictions = TFLayoutLMLMPredictionHead(config, input_embeddings, name="predictions")
    def call(self, sequence_output: tf.Tensor) -> tf.Tensor:
        prediction_scores = self.predictions(hidden_states=sequence_output)
        return prediction_scores
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "predictions", None) is not None:
            with tf.name_scope(self.predictions.name): self.predictions.build(None)
@keras_serializable
class TFLayoutLMMainLayer(keras.layers.Layer):
    config_class = LayoutLMConfig
    def __init__(self, config: LayoutLMConfig, add_pooling_layer: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embeddings = TFLayoutLMEmbeddings(config, name="embeddings")
        self.encoder = TFLayoutLMEncoder(config, name="encoder")
        self.pooler = TFLayoutLMPooler(config, name="pooler") if add_pooling_layer else None
    def get_input_embeddings(self) -> keras.layers.Layer: return self.embeddings
    def set_input_embeddings(self, value: tf.Variable):
        self.embeddings.weight = value
        self.embeddings.vocab_size = shape_list(value)[0]
    def _prune_heads(self, heads_to_prune): raise NotImplementedError
    @unpack_inputs
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None,
    encoder_attention_mask: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: bool = False) -> Union[TFBaseModelOutputWithPoolingAndCrossAttentions, Tuple[tf.Tensor]]:
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None: input_shape = shape_list(input_ids)
        elif inputs_embeds is not None: input_shape = shape_list(inputs_embeds)[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if attention_mask is None: attention_mask = tf.fill(dims=input_shape, value=1)
        if token_type_ids is None: token_type_ids = tf.fill(dims=input_shape, value=0)
        if bbox is None: bbox = tf.fill(dims=input_shape + [4], value=0)
        embedding_output = self.embeddings(input_ids=input_ids, bbox=bbox, position_ids=position_ids, token_type_ids=token_type_ids, inputs_embeds=inputs_embeds, training=training)
        extended_attention_mask = tf.reshape(attention_mask, (input_shape[0], 1, 1, input_shape[1]))
        extended_attention_mask = tf.cast(extended_attention_mask, dtype=embedding_output.dtype)
        one_cst = tf.constant(1.0, dtype=embedding_output.dtype)
        ten_thousand_cst = tf.constant(-10000.0, dtype=embedding_output.dtype)
        extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)
        if head_mask is not None: raise NotImplementedError
        else: head_mask = [None] * self.config.num_hidden_layers
        encoder_outputs = self.encoder(hidden_states=embedding_output, attention_mask=extended_attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=None, past_key_values=None, use_cache=False, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(hidden_states=sequence_output) if self.pooler is not None else None
        if not return_dict: return (sequence_output, pooled_output) + encoder_outputs[1:]
        return TFBaseModelOutputWithPoolingAndCrossAttentions(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states,
        attentions=encoder_outputs.attentions, cross_attentions=encoder_outputs.cross_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name): self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name): self.encoder.build(None)
        if getattr(self, "pooler", None) is not None:
            with tf.name_scope(self.pooler.name): self.pooler.build(None)
class TFLayoutLMPreTrainedModel(TFPreTrainedModel):
    config_class = LayoutLMConfig
    base_model_prefix = "layoutlm"
    @property
    def input_signature(self):
        signature = super().input_signature
        signature["bbox"] = tf.TensorSpec(shape=(None, None, 4), dtype=tf.int32, name="bbox")
        return signature
LAYOUTLM_START_DOCSTRING = r"""
    This model inherits from [`TFPreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a [keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model) subclass. Use it
    as a regular TF 2.0 Keras Model and refer to the TF 2.0 documentation for all matter related to general usage and
    behavior.
    <Tip>
    TensorFlow models and layers in `transformers` accept two formats as input:
    - having all inputs as keyword arguments (like PyTorch models), or
    - having all inputs as a list, tuple or dict in the first positional argument.
    The reason the second format is supported is that Keras methods prefer this format when passing inputs to models
    and layers. Because of this support, when using methods like `model.fit()` things should "just work" for you - just
    pass your inputs and labels in any format that `model.fit()` supports! If, however, you want to use the second
    format outside of Keras methods like `fit()` and `predict()`, such as when creating your own layers or models with
    the Keras `Functional` API, there are three possibilities you can use to gather all the input Tensors in the first
    positional argument:
    - a single Tensor with `input_ids` only and nothing else: `model(input_ids)`
    - a list of varying length with one or several input Tensors IN THE ORDER given in the docstring:
    `model([input_ids, attention_mask])` or `model([input_ids, attention_mask, token_type_ids])`
    - a dictionary with one or several input Tensors associated to the input names given in the docstring:
    `model({"input_ids": input_ids, "token_type_ids": token_type_ids})`
    Note that when creating models and layers with
    [subclassing](https://keras.io/guides/making_new_layers_and_models_via_subclassing/) then you don't need to worry
    about any of this, as you can just pass inputs like you would to any other Python function!
    </Tip>
    Args:
        config ([`LayoutLMConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~TFPreTrainedModel.from_pretrained`] method to load the model weights.
"""
LAYOUTLM_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`Numpy array` or `tf.Tensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.__call__`] and
            [`PreTrainedTokenizer.encode`] for details.
            [What are input IDs?](../glossary#input-ids)
        bbox (`Numpy array` or `tf.Tensor` of shape `(0, 4)`, *optional*):
            Bounding Boxes of each input sequence tokens. Selected in the range `[0, config.max_2d_position_embeddings-
            1]`.
        attention_mask (`Numpy array` or `tf.Tensor` of shape `(0)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`Numpy array` or `tf.Tensor` of shape `(0)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        position_ids (`Numpy array` or `tf.Tensor` of shape `(0)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`Numpy array` or `tf.Tensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
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
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        training (`bool`, *optional*, defaults to `False`):
            Whether or not to use the model in training mode (some modules like dropout modules have different
            behaviors between training and evaluation).
"""
@add_start_docstrings("The bare LayoutLM Model transformer outputting raw hidden-states without any specific head on top.", LAYOUTLM_START_DOCSTRING)
class TFLayoutLMModel(TFLayoutLMPreTrainedModel):
    def __init__(self, config: LayoutLMConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.layoutlm = TFLayoutLMMainLayer(config, name="layoutlm")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LAYOUTLM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None,
    encoder_attention_mask: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: Optional[bool] = False) -> Union[TFBaseModelOutputWithPoolingAndCrossAttentions, Tuple[tf.Tensor]]:
        outputs = self.layoutlm(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask,
        inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layoutlm", None) is not None:
            with tf.name_scope(self.layoutlm.name): self.layoutlm.build(None)
@add_start_docstrings("LayoutLM Model with a `language modeling` head on top.", LAYOUTLM_START_DOCSTRING)
class TFLayoutLMForMaskedLM(TFLayoutLMPreTrainedModel, TFMaskedLanguageModelingLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"cls.seq_relationship", r"cls.predictions.decoder.weight", r"nsp___cls"]
    def __init__(self, config: LayoutLMConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        if config.is_decoder: logger.warning("If you want to use `TFLayoutLMForMaskedLM` make sure `config.is_decoder=False` for bi-directional self-attention.")
        self.layoutlm = TFLayoutLMMainLayer(config, add_pooling_layer=True, name="layoutlm")
        self.mlm = TFLayoutLMMLMHead(config, input_embeddings=self.layoutlm.embeddings, name="mlm___cls")
    def get_lm_head(self) -> keras.layers.Layer: return self.mlm.predictions
    def get_prefix_bias_name(self) -> str:
        warnings.warn("The method get_prefix_bias_name is deprecated. Please use `get_bias` instead.", FutureWarning)
        return self.name + "/" + self.mlm.name + "/" + self.mlm.predictions.name
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LAYOUTLM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: np.ndarray | tf.Tensor | None = None, training: Optional[bool] = False) -> Union[TFMaskedLMOutput, Tuple[tf.Tensor]]:
        outputs = self.layoutlm(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask,
        inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        prediction_scores = self.mlm(sequence_output=sequence_output, training=training)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=prediction_scores)
        if not return_dict:
            output = (prediction_scores,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFMaskedLMOutput(loss=loss, logits=prediction_scores, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layoutlm", None) is not None:
            with tf.name_scope(self.layoutlm.name): self.layoutlm.build(None)
        if getattr(self, "mlm", None) is not None:
            with tf.name_scope(self.mlm.name): self.mlm.build(None)
@add_start_docstrings("LayoutLM Model transformer with a sequence classification/regression head on top (a linear layer on top of the pooled output) e.g. for GLUE tasks.", LAYOUTLM_START_DOCSTRING)
class TFLayoutLMForSequenceClassification(TFLayoutLMPreTrainedModel, TFSequenceClassificationLoss):
    _keys_to_ignore_on_load_unexpected = [r"mlm___cls", r"nsp___cls", r"cls.predictions", r"cls.seq_relationship"]
    _keys_to_ignore_on_load_missing = [r"dropout"]
    def __init__(self, config: LayoutLMConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.layoutlm = TFLayoutLMMainLayer(config, name="layoutlm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.classifier = keras.layers.Dense(units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="classifier")
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LAYOUTLM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: np.ndarray | tf.Tensor | None = None, training: Optional[bool] = False) -> Union[TFSequenceClassifierOutput, Tuple[tf.Tensor]]:
        outputs = self.layoutlm(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask,
        inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        pooled_output = outputs[1]
        pooled_output = self.dropout(inputs=pooled_output, training=training)
        logits = self.classifier(inputs=pooled_output)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layoutlm", None) is not None:
            with tf.name_scope(self.layoutlm.name): self.layoutlm.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name): self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings("LayoutLM Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", LAYOUTLM_START_DOCSTRING)
class TFLayoutLMForTokenClassification(TFLayoutLMPreTrainedModel, TFTokenClassificationLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"mlm___cls", r"nsp___cls", r"cls.predictions", r"cls.seq_relationship"]
    _keys_to_ignore_on_load_missing = [r"dropout"]
    def __init__(self, config: LayoutLMConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.layoutlm = TFLayoutLMMainLayer(config, add_pooling_layer=True, name="layoutlm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.classifier = keras.layers.Dense(units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="classifier")
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LAYOUTLM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: np.ndarray | tf.Tensor | None = None, training: Optional[bool] = False) -> Union[TFTokenClassifierOutput, Tuple[tf.Tensor]]:
        outputs = self.layoutlm(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask,
        inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        sequence_output = self.dropout(inputs=sequence_output, training=training)
        logits = self.classifier(inputs=sequence_output)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFTokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layoutlm", None) is not None:
            with tf.name_scope(self.layoutlm.name): self.layoutlm.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name): self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings("""
    LayoutLM Model with a span classification head on top for extractive question-answering tasks such as
    [DocVQA](https://rrc.cvc.uab.es/?ch=17) (a linear layer on top of the final hidden-states output to compute `span
    start logits` and `span end logits`).
    """, LAYOUTLM_START_DOCSTRING)
class TFLayoutLMForQuestionAnswering(TFLayoutLMPreTrainedModel, TFQuestionAnsweringLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"mlm___cls", r"nsp___cls", r"cls.predictions", r"cls.seq_relationship"]
    def __init__(self, config: LayoutLMConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.layoutlm = TFLayoutLMMainLayer(config, add_pooling_layer=True, name="layoutlm")
        self.qa_outputs = keras.layers.Dense(units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="qa_outputs")
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LAYOUTLM_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def call(self, input_ids: TFModelInputType | None = None, bbox: np.ndarray | tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None,
    position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, start_positions: np.ndarray | tf.Tensor | None = None, end_positions: np.ndarray | tf.Tensor | None = None,
    training: Optional[bool] = False) -> Union[TFQuestionAnsweringModelOutput, Tuple[tf.Tensor]]:
        outputs = self.layoutlm(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask,
        inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = outputs[0]
        logits = self.qa_outputs(inputs=sequence_output)
        start_logits, end_logits = tf.split(value=logits, num_or_size_splits=2, axis=-1)
        start_logits = tf.squeeze(input=start_logits, axis=-1)
        end_logits = tf.squeeze(input=end_logits, axis=-1)
        loss = None
        if start_positions is not None and end_positions is not None:
            labels = {"start_position": start_positions}
            labels["end_position"] = end_positions
            loss = self.hf_compute_loss(labels=labels, logits=(start_logits, end_logits))
        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFQuestionAnsweringModelOutput(loss=loss, start_logits=start_logits, end_logits=end_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layoutlm", None) is not None:
            with tf.name_scope(self.layoutlm.name): self.layoutlm.build(None)
        if getattr(self, "qa_outputs", None) is not None:
            with tf.name_scope(self.qa_outputs.name): self.qa_outputs.build([None, None, self.config.hidden_size])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
