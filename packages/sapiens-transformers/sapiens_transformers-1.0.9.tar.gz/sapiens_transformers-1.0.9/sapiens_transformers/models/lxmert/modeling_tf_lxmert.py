from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union
import numpy as np
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_utils import (TFModelInputType, TFPreTrainedModel, get_initializer, keras, keras_serializable, shape_list, unpack_inputs)
from ...tf_utils import check_embeddings_within_bounds, stable_softmax
from ...utils import (ModelOutput, add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_lxmert import LxmertConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "unc-nlp/lxmert-base-uncased"
_CONFIG_FOR_DOC = "LxmertConfig"
@dataclass
class TFLxmertModelOutput(ModelOutput):
    """Args:"""
    language_output: tf.Tensor | None = None
    vision_output: tf.Tensor | None = None
    pooled_output: tf.Tensor | None = None
    language_hidden_states: Tuple[tf.Tensor] | None = None
    vision_hidden_states: Tuple[tf.Tensor] | None = None
    language_attentions: Tuple[tf.Tensor] | None = None
    vision_attentions: Tuple[tf.Tensor] | None = None
    cross_encoder_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFLxmertForPreTrainingOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    prediction_logits: tf.Tensor | None = None
    cross_relationship_score: tf.Tensor | None = None
    question_answering_score: tf.Tensor | None = None
    language_hidden_states: Tuple[tf.Tensor] | None = None
    vision_hidden_states: Tuple[tf.Tensor] | None = None
    language_attentions: Tuple[tf.Tensor] | None = None
    vision_attentions: Tuple[tf.Tensor] | None = None
    cross_encoder_attentions: Tuple[tf.Tensor] | None = None
class TFLxmertVisualFeatureEncoder(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.visn_fc = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="visn_fc")
        self.visn_layer_norm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="visn_layer_norm")
        self.box_fc = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="box_fc")
        self.box_layer_norm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="box_layer_norm")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.feat_dim = config.visual_feat_dim
        self.pos_dim = config.visual_pos_dim
        self.config = config
    def call(self, visn_input, training=False):
        feats, boxes = visn_input
        x = self.visn_fc(feats)
        x = self.visn_layer_norm(x)
        y = self.box_fc(boxes)
        y = self.box_layer_norm(y)
        output = (x + y) / 2
        output = self.dropout(output, training=training)
        return output
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "visn_fc", None) is not None:
            with tf.name_scope(self.visn_fc.name): self.visn_fc.build([None, None, self.feat_dim])
        if getattr(self, "visn_layer_norm", None) is not None:
            with tf.name_scope(self.visn_layer_norm.name): self.visn_layer_norm.build([None, None, self.config.hidden_size])
        if getattr(self, "box_fc", None) is not None:
            with tf.name_scope(self.box_fc.name): self.box_fc.build([None, None, self.pos_dim])
        if getattr(self, "box_layer_norm", None) is not None:
            with tf.name_scope(self.box_layer_norm.name): self.box_layer_norm.build([None, None, self.config.hidden_size])
class TFLxmertEmbeddings(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.hidden_size = config.hidden_size
        self.max_position_embeddings = config.max_position_embeddings
        self.initializer_range = config.initializer_range
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
    def build(self, input_shape=None):
        with tf.name_scope("word_embeddings"): self.weight = self.add_weight(name="weight", shape=[self.config.vocab_size, self.hidden_size], initializer=get_initializer(initializer_range=self.initializer_range))
        with tf.name_scope("token_type_embeddings"): self.token_type_embeddings = self.add_weight(name="embeddings", shape=[self.config.type_vocab_size, self.hidden_size], initializer=get_initializer(initializer_range=self.initializer_range))
        with tf.name_scope("position_embeddings"): self.position_embeddings = self.add_weight(name="embeddings", shape=[self.max_position_embeddings, self.hidden_size], initializer=get_initializer(initializer_range=self.initializer_range))
        if self.built: return
        self.built = True
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
    def call(self, input_ids=None, token_type_ids=None, inputs_embeds=None, training=False):
        assert not (input_ids is None and inputs_embeds is None)
        if input_ids is not None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = tf.gather(params=self.weight, indices=input_ids)
        input_shape = shape_list(inputs_embeds)[:-1]
        if token_type_ids is None: token_type_ids = tf.fill(dims=input_shape, value=0)
        position_ids = tf.expand_dims(tf.range(start=0, limit=input_shape[-1]), axis=0)
        position_embeds = tf.gather(params=self.position_embeddings, indices=position_ids)
        token_type_embeds = tf.gather(params=self.token_type_embeddings, indices=token_type_ids)
        final_embeddings = inputs_embeds + position_embeds + token_type_embeds
        final_embeddings = self.LayerNorm(inputs=final_embeddings)
        final_embeddings = self.dropout(inputs=final_embeddings, training=training)
        return final_embeddings
class TFLxmertAttention(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        if config.hidden_size % config.num_attention_heads != 0: raise ValueError(f"The hidden size ({config.hidden_size}) is not a multiple of the number of attention heads ({config.num_attention_heads}")
        self.num_attention_heads = config.num_attention_heads
        assert config.hidden_size % config.num_attention_heads == 0
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="query")
        self.key = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="key")
        self.value = keras.layers.Dense(self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="value")
        self.dropout = keras.layers.Dropout(config.attention_probs_dropout_prob)
        self.ctx_dim = config.hidden_size
        self.config = config
    def transpose_for_scores(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_attention_heads, self.attention_head_size))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    def call(self, hidden_states, context, attention_mask, output_attentions, training=False):
        batch_size = shape_list(hidden_states)[0]
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(context)
        mixed_value_layer = self.value(context)
        query_layer = self.transpose_for_scores(mixed_query_layer, batch_size)
        key_layer = self.transpose_for_scores(mixed_key_layer, batch_size)
        value_layer = self.transpose_for_scores(mixed_value_layer, batch_size)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        dk = tf.cast(shape_list(key_layer)[-1], dtype=attention_scores.dtype)
        attention_scores = attention_scores / tf.math.sqrt(dk)
        if attention_mask is not None:
            attention_mask = tf.cast(attention_mask, dtype=attention_scores.dtype)
            attention_scores = attention_scores + attention_mask
        attention_probs = stable_softmax(attention_scores, axis=-1)
        attention_probs = self.dropout(attention_probs, training=training)
        context_layer = tf.matmul(attention_probs, value_layer)
        context_layer = tf.transpose(context_layer, perm=[0, 2, 1, 3])
        context_layer = tf.reshape(context_layer, (batch_size, -1, self.all_head_size))
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "query", None) is not None:
            with tf.name_scope(self.query.name): self.query.build([None, None, self.config.hidden_size])
        if getattr(self, "key", None) is not None:
            with tf.name_scope(self.key.name): self.key.build([None, None, self.ctx_dim])
        if getattr(self, "value", None) is not None:
            with tf.name_scope(self.value.name): self.value.build([None, None, self.ctx_dim])
class TFLxmertIntermediate(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(config.intermediate_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = get_tf_activation(config.hidden_act)
        else: self.intermediate_act_fn = config.hidden_act
        self.config = config
    def call(self, hidden_states):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFLxmertOutput(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states, input_tensor, training=False):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states, training)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.intermediate_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFLxmertAttentionOutput(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states, input_tensor, training=False):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states, training=training)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name): self.LayerNorm.build([None, None, self.config.hidden_size])
class TFLxmertSelfAttentionLayer(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.self = TFLxmertAttention(config, name="self")
        self.attention_output = TFLxmertAttentionOutput(config, name="output")
    def call(self, input_tensor, attention_mask, output_attentions, training=False):
        self_output = self.self(input_tensor, input_tensor, attention_mask, output_attentions)
        if output_attentions: attention_probs = self_output[1]
        attention_output = self.attention_output(self_output[0], input_tensor)
        return (attention_output, attention_probs) if output_attentions else (attention_output,)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "self", None) is not None:
            with tf.name_scope(self.self.name): self.self.build(None)
        if getattr(self, "attention_output", None) is not None:
            with tf.name_scope(self.attention_output.name): self.attention_output.build(None)
class TFLxmertCrossAttentionLayer(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.att = TFLxmertAttention(config, name="att")
        self.attention_output = TFLxmertAttentionOutput(config, name="output")
    def call(self, input_tensor, ctx_tensor, ctx_att_mask, output_attentions=False, training=False):
        output = self.att(input_tensor, ctx_tensor, ctx_att_mask, output_attentions, training=training)
        if output_attentions: attention_probs = output[1]
        attention_output = self.attention_output(output[0], input_tensor, training=training)
        outputs = (attention_output, attention_probs) if output_attentions else (attention_output,)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "att", None) is not None:
            with tf.name_scope(self.att.name): self.att.build(None)
        if getattr(self, "attention_output", None) is not None:
            with tf.name_scope(self.attention_output.name): self.attention_output.build(None)
class TFLxmertLayer(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.attention = TFLxmertSelfAttentionLayer(config, name="attention")
        self.intermediate = TFLxmertIntermediate(config, name="intermediate")
        self.transformer_output = TFLxmertOutput(config, name="output")
    def call(self, hidden_states, attention_mask, output_attentions, training=False):
        attention_outputs = self.attention(hidden_states, attention_mask, output_attentions, training=training)
        attention_output = attention_outputs[0]
        intermediate_output = self.intermediate(attention_output)
        layer_output = self.transformer_output(intermediate_output, attention_output, training=training)
        outputs = (layer_output,) + attention_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "attention", None) is not None:
            with tf.name_scope(self.attention.name): self.attention.build(None)
        if getattr(self, "intermediate", None) is not None:
            with tf.name_scope(self.intermediate.name): self.intermediate.build(None)
        if getattr(self, "transformer_output", None) is not None:
            with tf.name_scope(self.transformer_output.name): self.transformer_output.build(None)
class TFLxmertXLayer(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.visual_attention = TFLxmertCrossAttentionLayer(config, name="visual_attention")
        self.lang_self_att = TFLxmertSelfAttentionLayer(config, name="lang_self_att")
        self.visn_self_att = TFLxmertSelfAttentionLayer(config, name="visn_self_att")
        self.lang_inter = TFLxmertIntermediate(config, name="lang_inter")
        self.lang_output = TFLxmertOutput(config, name="lang_output")
        self.visn_inter = TFLxmertIntermediate(config, name="visn_inter")
        self.visn_output = TFLxmertOutput(config, name="visn_output")
    def cross_att(self, lang_input, lang_attention_mask, visn_input, visn_attention_mask, output_attentions, training=False):
        lang_attention_lang_input = tf.identity(lang_input)
        visn_attention_lang_input = tf.identity(lang_input)
        lang_attention_visn_input = tf.identity(visn_input)
        visn_attention_visn_input = tf.identity(visn_input)
        lang_att_output = self.visual_attention(lang_attention_lang_input, lang_attention_visn_input, visn_attention_mask, output_attentions=output_attentions, training=training)
        visn_att_output = self.visual_attention(visn_attention_visn_input, visn_attention_lang_input, lang_attention_mask, output_attentions=output_attentions, training=training)
        return lang_att_output, visn_att_output
    def self_att(self, lang_input, lang_attention_mask, visn_input, visn_attention_mask, training=False):
        output_attentions = False
        lang_att_output = self.lang_self_att(lang_input, lang_attention_mask, output_attentions, training=training)
        visn_att_output = self.visn_self_att(visn_input, visn_attention_mask, output_attentions, training=training)
        return lang_att_output[0], visn_att_output[0]
    def output_fc(self, lang_input, visn_input, training=False):
        lang_inter_output = self.lang_inter(lang_input)
        visn_inter_output = self.visn_inter(visn_input)
        lang_output = self.lang_output(lang_inter_output, lang_input, training)
        visn_output = self.visn_output(visn_inter_output, visn_input, training)
        return lang_output, visn_output
    def call(self, lang_feats, lang_attention_mask, visn_feats, visn_attention_mask, output_attentions, training=False):
        lang_att_output = lang_feats
        visn_att_output = visn_feats
        lang_att_output, visn_att_output = self.cross_att(lang_att_output, lang_attention_mask, visn_att_output, visn_attention_mask, output_attentions, training=training)
        attention_probs = lang_att_output[1:]
        lang_att_output, visn_att_output = self.self_att(lang_att_output[0], lang_attention_mask, visn_att_output[0], visn_attention_mask, training=training)
        lang_output, visn_output = self.output_fc(lang_att_output, visn_att_output, training=training)
        return (lang_output, visn_output, attention_probs[0]) if output_attentions else (lang_output, visn_output)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "visual_attention", None) is not None:
            with tf.name_scope(self.visual_attention.name): self.visual_attention.build(None)
        if getattr(self, "lang_self_att", None) is not None:
            with tf.name_scope(self.lang_self_att.name): self.lang_self_att.build(None)
        if getattr(self, "visn_self_att", None) is not None:
            with tf.name_scope(self.visn_self_att.name): self.visn_self_att.build(None)
        if getattr(self, "lang_inter", None) is not None:
            with tf.name_scope(self.lang_inter.name): self.lang_inter.build(None)
        if getattr(self, "lang_output", None) is not None:
            with tf.name_scope(self.lang_output.name): self.lang_output.build(None)
        if getattr(self, "visn_inter", None) is not None:
            with tf.name_scope(self.visn_inter.name): self.visn_inter.build(None)
        if getattr(self, "visn_output", None) is not None:
            with tf.name_scope(self.visn_output.name): self.visn_output.build(None)
class TFLxmertEncoder(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.visn_fc = TFLxmertVisualFeatureEncoder(config, name="visn_fc")
        self.num_l_layers = config.l_layers
        self.num_x_layers = config.x_layers
        self.num_r_layers = config.r_layers
        self.layer = [TFLxmertLayer(config, name=f"layer_._{i}") for i in range(self.num_l_layers)]
        self.x_layers = [TFLxmertXLayer(config, name=f"x_layers_._{i}") for i in range(self.num_x_layers)]
        self.r_layers = [TFLxmertLayer(config, name=f"r_layers_._{i}") for i in range(self.num_r_layers)]
        self.config = config
    def call(self, lang_feats=None, lang_attention_mask=None, visual_feats=None, visual_pos=None, visual_attention_mask=None, output_attentions=None, training=False):
        vision_hidden_states = ()
        language_hidden_states = ()
        vision_attentions = () if output_attentions or self.config.output_attentions else None
        language_attentions = () if output_attentions or self.config.output_attentions else None
        cross_encoder_attentions = () if output_attentions or self.config.output_attentions else None
        visual_feats = self.visn_fc([visual_feats, visual_pos], training=training)
        for layer_module in self.layer:
            l_outputs = layer_module(lang_feats, lang_attention_mask, output_attentions, training=training)
            lang_feats = l_outputs[0]
            language_hidden_states = language_hidden_states + (lang_feats,)
            if language_attentions is not None: language_attentions = language_attentions + (l_outputs[1],)
        for layer_module in self.r_layers:
            v_outputs = layer_module(visual_feats, visual_attention_mask, output_attentions, training=training)
            visual_feats = v_outputs[0]
            vision_hidden_states = vision_hidden_states + (visual_feats,)
            if vision_attentions is not None: vision_attentions = vision_attentions + (v_outputs[1],)
        for layer_module in self.x_layers:
            x_outputs = layer_module(lang_feats, lang_attention_mask, visual_feats, visual_attention_mask, output_attentions, training=training)
            lang_feats, visual_feats = x_outputs[:2]
            vision_hidden_states = vision_hidden_states + (visual_feats,)
            language_hidden_states = language_hidden_states + (lang_feats,)
            if cross_encoder_attentions is not None: cross_encoder_attentions = cross_encoder_attentions + (x_outputs[2],)
        visual_encoder_outputs = (vision_hidden_states, vision_attentions if output_attentions else None)
        lang_encoder_outputs = (language_hidden_states, language_attentions if output_attentions else None)
        return (visual_encoder_outputs, lang_encoder_outputs, cross_encoder_attentions if output_attentions else None)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "visn_fc", None) is not None:
            with tf.name_scope(self.visn_fc.name): self.visn_fc.build(None)
        if getattr(self, "layer", None) is not None:
            for layer in self.layer:
                with tf.name_scope(layer.name): layer.build(None)
        if getattr(self, "x_layers", None) is not None:
            for layer in self.x_layers:
                with tf.name_scope(layer.name): layer.build(None)
        if getattr(self, "r_layers", None) is not None:
            for layer in self.r_layers:
                with tf.name_scope(layer.name): layer.build(None)
@keras_serializable
class TFLxmertMainLayer(keras.layers.Layer):
    config_class = LxmertConfig
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.num_l_layers = config.l_layers
        self.num_x_layers = config.x_layers
        self.num_r_layers = config.r_layers
        self.initializer_range = config.initializer_range
        self.output_attentions = config.output_attentions
        self.output_hidden_states = config.output_hidden_states
        self.return_dict = config.use_return_dict
        self.embeddings = TFLxmertEmbeddings(config, name="embeddings")
        self.encoder = TFLxmertEncoder(config, name="encoder")
        self.pooler = TFLxmertPooler(config, name="pooler")
        self.config = config
    def get_input_embeddings(self): return self.embeddings
    def set_input_embeddings(self, value):
        self.embeddings.weight = value
        self.embeddings.vocab_size = shape_list(value)[0]
    def _prune_heads(self, heads_to_prune): raise NotImplementedError
    @unpack_inputs
    def call(self, input_ids=None, visual_feats=None, visual_pos=None, attention_mask=None, visual_attention_mask=None, token_type_ids=None, inputs_embeds=None,
    output_attentions=None, output_hidden_states=None, return_dict=None, training=False):
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None: input_shape = shape_list(input_ids)
        elif inputs_embeds is not None: input_shape = shape_list(inputs_embeds)[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if visual_pos is None or visual_feats is None: raise ValueError("visual_feats and visual_pos cannot be `None` in LXMERT's `call` method.")
        if attention_mask is None: attention_mask = tf.fill(input_shape, 1)
        if token_type_ids is None: token_type_ids = tf.fill(input_shape, 0)
        embedding_output = self.embeddings(input_ids, token_type_ids, inputs_embeds, training)
        extended_attention_mask = tf.reshape(attention_mask, (input_shape[0], 1, 1, input_shape[1]))
        extended_attention_mask = tf.cast(extended_attention_mask, dtype=embedding_output.dtype)
        one_cst = tf.constant(1.0, dtype=embedding_output.dtype)
        ten_thousand_cst = tf.constant(-10000.0, dtype=embedding_output.dtype)
        extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)
        if visual_attention_mask is not None:
            extended_visual_attention_mask = tf.reshape(visual_attention_mask, (input_shape[0], 1, 1, input_shape[1]))
            extended_visual_attention_mask = tf.expand_dims(tf.expand_dims(visual_attention_mask, axis=1), axis=1)
            extended_visual_attention_mask = tf.cast(extended_visual_attention_mask, dtype=embedding_output.dtype)
            extended_visual_attention_mask = tf.multiply(tf.subtract(one_cst, extended_visual_attention_mask), ten_thousand_cst)
        else: extended_visual_attention_mask = None
        encoder_outputs = self.encoder(embedding_output, extended_attention_mask, visual_feats, visual_pos, extended_visual_attention_mask, output_attentions, training)
        visual_encoder_outputs, lang_encoder_outputs = encoder_outputs[:2]
        vision_hidden_states = visual_encoder_outputs[0]
        language_hidden_states = lang_encoder_outputs[0]
        all_attentions = ()
        if output_attentions:
            language_attentions = lang_encoder_outputs[1]
            vision_attentions = visual_encoder_outputs[1]
            cross_encoder_attentions = encoder_outputs[2]
            all_attentions = (language_attentions, vision_attentions, cross_encoder_attentions)
        hidden_states = (language_hidden_states, vision_hidden_states) if output_hidden_states else ()
        visual_output = vision_hidden_states[-1]
        lang_output = language_hidden_states[-1]
        pooled_output = self.pooler(lang_output)
        if not return_dict: return (lang_output, visual_output, pooled_output) + hidden_states + all_attentions
        return TFLxmertModelOutput(pooled_output=pooled_output, language_output=lang_output, vision_output=visual_output, language_hidden_states=language_hidden_states if output_hidden_states else None,
        vision_hidden_states=vision_hidden_states if output_hidden_states else None, language_attentions=language_attentions if output_attentions else None,
        vision_attentions=vision_attentions if output_attentions else None, cross_encoder_attentions=cross_encoder_attentions if output_attentions else None)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name): self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name): self.encoder.build(None)
        if getattr(self, "pooler", None) is not None:
            with tf.name_scope(self.pooler.name): self.pooler.build(None)
class TFLxmertPreTrainedModel(TFPreTrainedModel):
    config_class = LxmertConfig
    base_model_prefix = "lxmert"
    @property
    def dummy_inputs(self):
        batch_size = 2
        num_visual_features = 10
        input_ids = tf.constant([[3, 5, 6], [2, 3, 4]], dtype=tf.int32)
        visual_feats = tf.random.uniform((batch_size, num_visual_features, self.config.visual_feat_dim))
        visual_pos = tf.random.uniform((batch_size, num_visual_features, 4))
        return {"input_ids": input_ids, "visual_feats": visual_feats, "visual_pos": visual_pos}
    @property
    def input_signature(self):
        return {
            "input_ids": tf.TensorSpec((None, None), tf.int32, name="input_ids"),
            "attention_mask": tf.TensorSpec((None, None), tf.int32, name="attention_mask"),
            "visual_feats": tf.TensorSpec((None, None, self.config.visual_feat_dim), tf.float32, name="visual_feats"),
            "visual_pos": tf.TensorSpec((None, None, 4), tf.float32, name="visual_pos"),
            "visual_attention_mask": tf.TensorSpec((None, None), tf.int32, name="visual_attention_mask"),
            "token_type_ids": tf.TensorSpec((None, None), tf.int32, name="token_type_ids"),
        }
LXMERT_START_DOCSTRING = r"""
    The LXMERT model was proposed in [LXMERT: Learning Cross-Modality Encoder Representations from
    Transformers](https://arxiv.org/abs/1908.07490) by Hao Tan and Mohit Bansal. It's a vision and language transformer
    model, pre-trained on a variety of multi-modal datasets comprising of GQA, VQAv2.0, MCSCOCO captions, and Visual
    genome, using a combination of masked language modeling, region of interest feature regression, cross entropy loss
    for question answering attribute prediction, and object tag prediction.
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
    Parameters:
        config ([`LxmertConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
LXMERT_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`np.ndarray` or `tf.Tensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.__call__`] and
            [`PreTrainedTokenizer.encode`] for details.
            [What are input IDs?](../glossary#input-ids)
        visual_feats (`tf.Tensor` of shape `(batch_size, num_visual_features, visual_feat_dim)`):
            This input represents visual features. They ROI pooled object features from bounding boxes using a
            faster-RCNN model
            These are currently not provided by the transformers library.
        visual_pos (`tf.Tensor` of shape `(batch_size, num_visual_features, visual_feat_dim)`):
            This input represents spacial features corresponding to their relative (via index) visual features. The
            pre-trained LXMERT model expects these spacial features to be normalized bounding boxes on a scale of 0 to
            1.
            These are currently not provided by the transformers library.
        attention_mask (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        visual_attention_mask (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            MMask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        inputs_embeds (`tf.Tensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail. This argument can be used only in eager mode, in graph mode the value in the
            config will be used instead.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail. This argument can be used only in eager mode, in graph mode the value in the config will be
            used instead.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple. This argument can be used in
            eager mode, in graph mode the value will always be set to True.
        training (`bool`, *optional*, defaults to `False`):
            Whether or not to use the model in training mode (some modules like dropout modules have different
            behaviors between training and evaluation).
"""
@add_start_docstrings("The bare Lxmert Model transformer outputting raw hidden-states without any specific head on top.", LXMERT_START_DOCSTRING)
class TFLxmertModel(TFLxmertPreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.lxmert = TFLxmertMainLayer(config, name="lxmert")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LXMERT_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, visual_feats: tf.Tensor | None = None, visual_pos: tf.Tensor | None = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    visual_attention_mask: np.ndarray | tf.Tensor | None = None, token_type_ids: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: bool = False) -> Union[Tuple, TFLxmertModelOutput]:
        outputs = self.lxmert(input_ids, visual_feats, visual_pos, attention_mask, visual_attention_mask, token_type_ids, inputs_embeds, output_attentions, output_hidden_states, return_dict, training)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "lxmert", None) is not None:
            with tf.name_scope(self.lxmert.name): self.lxmert.build(None)
class TFLxmertPooler(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), activation="tanh", name="dense")
        self.config = config
    def call(self, hidden_states):
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        return pooled_output
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFLxmertPredictionHeadTransform(keras.layers.Layer):
    def __init__(self, config: LxmertConfig, **kwargs):
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
class TFLxmertLMPredictionHead(keras.layers.Layer):
    def __init__(self, config: LxmertConfig, input_embeddings: keras.layers.Layer, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.hidden_size = config.hidden_size
        self.transform = TFLxmertPredictionHeadTransform(config, name="transform")
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
class TFLxmertMLMHead(keras.layers.Layer):
    def __init__(self, config: LxmertConfig, input_embeddings: keras.layers.Layer, **kwargs):
        super().__init__(**kwargs)
        self.predictions = TFLxmertLMPredictionHead(config, input_embeddings, name="predictions")
    def call(self, sequence_output: tf.Tensor) -> tf.Tensor:
        prediction_scores = self.predictions(hidden_states=sequence_output)
        return prediction_scores
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "predictions", None) is not None:
            with tf.name_scope(self.predictions.name): self.predictions.build(None)
class TFLxmertPreTrainingHeads(keras.layers.Layer):
    def __init__(self, config, input_embeddings, **kwargs):
        super().__init__(**kwargs)
        self.predictions = TFLxmertLMPredictionHead(config, input_embeddings, name="predictions")
        self.seq_relationship = keras.layers.Dense(2, kernel_initializer=get_initializer(config.initializer_range), name="seq_relationship")
        self.config = config
    def call(self, sequence_output, pooled_output):
        prediction_scores = self.predictions(sequence_output)
        seq_relationship_score = self.seq_relationship(pooled_output)
        return prediction_scores, seq_relationship_score
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "predictions", None) is not None:
            with tf.name_scope(self.predictions.name): self.predictions.build(None)
        if getattr(self, "seq_relationship", None) is not None:
            with tf.name_scope(self.seq_relationship.name): self.seq_relationship.build([None, None, self.config.hidden_size])
class TFLxmertVisualAnswerHead(keras.layers.Layer):
    def __init__(self, config, num_labels, **kwargs):
        super().__init__(**kwargs)
        hid_dim = config.hidden_size
        self.dense = keras.layers.Dense(hid_dim * 2, kernel_initializer=get_initializer(config.initializer_range), name="logit_fc_._0")
        self.activation = get_tf_activation("gelu")
        self.layer_norm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="logit_fc_._2")
        self.dense_1 = keras.layers.Dense(num_labels, kernel_initializer=get_initializer(config.initializer_range), name="logit_fc_._3")
        self.hid_dim = hid_dim
    def call(self, hidden_states):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.dense_1(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.hid_dim])
        if getattr(self, "layer_norm", None) is not None:
            with tf.name_scope(self.layer_norm.name): self.layer_norm.build([None, self.hid_dim * 2])
        if getattr(self, "dense_1", None) is not None:
            with tf.name_scope(self.dense_1.name): self.dense_1.build([None, None, self.hid_dim * 2])
class TFLxmertVisualObjHead(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.transform = TFLxmertPredictionHeadTransform(config, name="transform")
        visual_losses = {}
        if config.visual_obj_loss: visual_losses["obj"] = {"shape": (-1,), "num": config.num_object_labels}
        if config.visual_attr_loss: visual_losses["attr"] = {"shape": (-1,), "num": config.num_attr_labels}
        if config.visual_feat_loss: visual_losses["feat"] = {"shape": (-1, 2048), "num": config.visual_feat_dim}
        self.visual_losses = visual_losses
        self.decoder_dict = {key: keras.layers.Dense(self.visual_losses[key]["num"], kernel_initializer=get_initializer(config.initializer_range), name=f"decoder_dict.{key}") for key in self.visual_losses}
        self.config = config
    def call(self, hidden_states):
        hidden_states = self.transform(hidden_states)
        output = {}
        for key in self.visual_losses: output[key] = self.decoder_dict[key](hidden_states)
        return output
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "transform", None) is not None:
            with tf.name_scope(self.transform.name): self.transform.build(None)
        if getattr(self, "decoder_dict", None) is not None:
            for layer in self.decoder_dict.values():
                with tf.name_scope(layer.name): layer.build([None, None, self.config.hidden_size])
@add_start_docstrings("Lxmert Model with a `language modeling` head on top.", LXMERT_START_DOCSTRING)
class TFLxmertForPreTraining(TFLxmertPreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.config = config
        self.num_qa_labels = config.num_qa_labels
        self.visual_loss_normalizer = config.visual_loss_normalizer
        self.task_mask_lm = config.task_mask_lm
        self.task_obj_predict = config.task_obj_predict
        self.task_matched = config.task_matched
        self.task_qa = config.task_qa
        self.lxmert = TFLxmertMainLayer(config, name="lxmert")
        self.cls = TFLxmertPreTrainingHeads(config, self.lxmert.embeddings, name="cls")
        if self.task_obj_predict: self.obj_predict_head = TFLxmertVisualObjHead(config, name="obj_predict_head")
        if self.task_qa: self.answer_head = TFLxmertVisualAnswerHead(config, self.num_qa_labels, name="answer_head")
        self.loss_fcts = {"l2": keras.losses.Huber(delta=1.0, name="huber_loss"), "visn_ce": keras.losses.SparseCategoricalCrossentropy(from_logits=True), "ce": keras.losses.SparseCategoricalCrossentropy(from_logits=True)}
        visual_losses = {}
        if config.visual_obj_loss: visual_losses["obj"] = {"shape": (-1,), "num": config.num_object_labels, "loss": "visn_ce"}
        if config.visual_attr_loss: visual_losses["attr"] = {"shape": (-1,), "num": config.num_attr_labels, "loss": "visn_ce"}
        if config.visual_feat_loss: visual_losses["feat"] = {"shape": (-1, config.visual_feat_dim), "num": config.visual_feat_dim, "loss": "l2"}
        self.visual_losses = visual_losses
    @property
    def dummy_inputs(self):
        batch_size = 2
        num_visual_features = 10
        input_ids = tf.constant([[3, 5, 6], [2, 3, 4]], dtype=tf.int32)
        visual_feats = tf.random.uniform((batch_size, num_visual_features, self.config.visual_feat_dim))
        visual_pos = tf.random.uniform((batch_size, num_visual_features, 4))
        if self.config.task_obj_predict: obj_labels = {}
        if self.config.visual_attr_loss and self.config.task_obj_predict: obj_labels["attr"] = (tf.ones([batch_size, num_visual_features]), tf.ones([batch_size, num_visual_features]),)
        if self.config.visual_feat_loss and self.config.task_obj_predict: obj_labels["feat"] = (tf.ones([batch_size, num_visual_features, self.config.visual_feat_dim]), tf.ones([batch_size, num_visual_features]),)
        if self.config.visual_obj_loss and self.config.task_obj_predict: obj_labels["obj"] = (tf.ones([batch_size, num_visual_features]), tf.ones([batch_size, num_visual_features]),)
        return {**{"input_ids": input_ids, "visual_feats": visual_feats, "visual_pos": visual_pos}, **({"obj_labels": obj_labels} if self.config.task_obj_predict else {})}
    def get_lm_head(self): return self.cls.predictions
    def get_prefix_bias_name(self):
        warnings.warn("The method get_prefix_bias_name is deprecated. Please use `get_bias` instead.", FutureWarning)
        return self.name + "/" + self.cls.name + "/" + self.cls.predictions.name
    @unpack_inputs
    @add_start_docstrings_to_model_forward(LXMERT_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, visual_feats: tf.Tensor | None = None, visual_pos: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None,
    visual_attention_mask: tf.Tensor | None = None, token_type_ids: tf.Tensor | None = None, inputs_embeds: tf.Tensor | None = None, masked_lm_labels: tf.Tensor | None = None,
    obj_labels: Dict[str, Tuple[tf.Tensor, tf.Tensor]] | None = None, matched_label: tf.Tensor | None = None, ans: tf.Tensor | None = None, output_attentions: bool | None = None,
    output_hidden_states: bool | None = None, return_dict: bool | None = None, training: bool = False) -> Tuple[tf.Tensor] | TFLxmertForPreTrainingOutput:
        lxmert_output = self.lxmert(input_ids, visual_feats, visual_pos, attention_mask, visual_attention_mask, token_type_ids, inputs_embeds, output_attentions,
        output_hidden_states, return_dict, training)
        lang_output, visual_output, pooled_output = (lxmert_output[0], lxmert_output[1], lxmert_output[2])
        lang_prediction_scores, cross_relationship_score = self.cls(lang_output, pooled_output)
        if self.task_qa: answer_score = self.answer_head(pooled_output)
        else: answer_score = pooled_output[0][0]
        total_loss = (None if (masked_lm_labels is None and matched_label is None and obj_labels is None and ans is None) else tf.constant(0.0))
        losses = ()
        if masked_lm_labels is not None and self.task_mask_lm:
            masked_lm_loss = self.loss_fcts["ce"](tf.reshape(masked_lm_labels, [-1]), tf.reshape(lang_prediction_scores, [-1, self.config.vocab_size]),)
            total_loss += masked_lm_loss
            losses += (masked_lm_loss,)
        if matched_label is not None and self.task_matched:
            matched_loss = self.loss_fcts["ce"](tf.reshape(matched_label, [-1]), tf.reshape(cross_relationship_score, [-1, 2]),)
            total_loss += matched_loss
            losses += (matched_loss,)
        if obj_labels is not None and self.task_obj_predict:
            total_visn_loss = 0.0
            visn_prediction_scores_dict = self.obj_predict_head(visual_output)
            for key, key_info in self.visual_losses.items():
                label, mask_conf = obj_labels[key]
                output_dim = key_info["num"]
                loss_fct_name = key_info["loss"]
                label_shape = key_info["shape"]
                weight = self.visual_loss_normalizer
                visn_loss_fct = self.loss_fcts[loss_fct_name]
                visn_prediction_scores = visn_prediction_scores_dict[key]
                visn_loss = visn_loss_fct(tf.reshape(label, label_shape), tf.reshape(visn_prediction_scores, [-1, output_dim]))
                if visn_loss.ndim > 1: visn_loss = tf.reduce_mean(visn_loss)
                visn_loss = tf.reduce_mean(visn_loss * tf.cast(tf.reshape(mask_conf, [-1]), visn_loss.dtype)) * weight
                total_visn_loss += visn_loss
                losses += (visn_loss,)
            total_loss += total_visn_loss
        if ans is not None and self.task_qa:
            answer_loss = self.loss_fcts["ce"](tf.reshape(ans, [-1]), tf.reshape(answer_score, [-1, self.num_qa_labels]))
            total_loss += answer_loss
            losses += (answer_loss,)
        if not return_dict:
            output = (lang_prediction_scores, cross_relationship_score, answer_score) + lxmert_output[3:]
            return ((total_loss,) + output) if total_loss is not None else output
        return TFLxmertForPreTrainingOutput(loss=total_loss, prediction_logits=lang_prediction_scores, cross_relationship_score=cross_relationship_score,
        question_answering_score=answer_score, language_hidden_states=lxmert_output.language_hidden_states, vision_hidden_states=lxmert_output.vision_hidden_states,
        language_attentions=lxmert_output.language_attentions, vision_attentions=lxmert_output.vision_attentions, cross_encoder_attentions=lxmert_output.cross_encoder_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "lxmert", None) is not None:
            with tf.name_scope(self.lxmert.name): self.lxmert.build(None)
        if getattr(self, "cls", None) is not None:
            with tf.name_scope(self.cls.name): self.cls.build(None)
        if getattr(self, "obj_predict_head", None) is not None:
            with tf.name_scope(self.obj_predict_head.name): self.obj_predict_head.build(None)
        if getattr(self, "answer_head", None) is not None:
            with tf.name_scope(self.answer_head.name): self.answer_head.build(None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
