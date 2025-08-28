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
from typing import Any, Optional, Tuple, Union
import tensorflow as tf
from ...modeling_tf_outputs import TFBaseModelOutput, TFBaseModelOutputWithPooling
from ...modeling_tf_utils import (TFPreTrainedModel, get_initializer, get_tf_activation, keras, keras_serializable, shape_list, unpack_inputs)
from ...tf_utils import check_embeddings_within_bounds, stable_softmax
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_blip import BlipConfig, BlipTextConfig, BlipVisionConfig
from .modeling_tf_blip_text import BLIP_TEXT_INPUTS_DOCSTRING, TFBlipTextLMHeadModel, TFBlipTextModel
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "Salesforce/blip-vqa-base"
def contrastive_loss(logits: tf.Tensor) -> tf.Tensor: return tf.math.reduce_mean(keras.metrics.sparse_categorical_crossentropy(y_true=tf.range(shape_list(logits)[0]), y_pred=logits, from_logits=True))
def blip_loss(similarity: tf.Tensor) -> tf.Tensor:
    caption_loss = contrastive_loss(similarity)
    image_loss = contrastive_loss(tf.transpose(similarity))
    return (caption_loss + image_loss) / 2.0
@dataclass
class TFBlipForConditionalGenerationModelOutput(ModelOutput):
    """Args:"""
    loss: Tuple[tf.Tensor] | None = None
    logits: Tuple[tf.Tensor] | None = None
    image_embeds: tf.Tensor | None = None
    last_hidden_state: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor, ...] | None = None
    attentions: Tuple[tf.Tensor, ...] | None = None
    @property
    def decoder_logits(self):
        warnings.warn("`decoder_logits` attribute is deprecated and will be removed in version 1 of Sapiens Transformers. Please use the `logits` attribute to retrieve the final output instead.", FutureWarning)
        return self.logits
@dataclass
class TFBlipTextVisionModelOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    image_embeds: tf.Tensor | None = None
    last_hidden_state: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor, ...] | None = None
    attentions: Tuple[tf.Tensor, ...] | None = None
@dataclass
class TFBlipImageTextMatchingModelOutput(ModelOutput):
    """Args:"""
    itm_score: tf.Tensor | None = None
    loss: tf.Tensor | None = None
    image_embeds: tf.Tensor | None = None
    last_hidden_state: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor, ...] | None = None
    vision_pooler_output: tf.Tensor | None = None
    attentions: Tuple[tf.Tensor, ...] | None = None
    question_embeds: Tuple[tf.Tensor] | None = None
@dataclass
class TFBlipOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits_per_image: tf.Tensor = None
    logits_per_text: tf.Tensor = None
    text_embeds: tf.Tensor = None
    image_embeds: tf.Tensor = None
    text_model_output: TFBaseModelOutputWithPooling = None
    vision_model_output: TFBaseModelOutputWithPooling = None
    def to_tuple(self) -> Tuple[Any]: return tuple(self[k] if k not in ["text_model_output", "vision_model_output"] else getattr(self, k).to_tuple() for k in self.keys())
class TFBlipVisionEmbeddings(keras.layers.Layer):
    def __init__(self, config: BlipVisionConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embed_dim = config.hidden_size
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.patch_embedding = keras.layers.Conv2D(filters=self.embed_dim, kernel_size=self.patch_size, strides=self.patch_size, kernel_initializer=get_initializer(self.config.initializer_range), data_format="channels_last", name="patch_embedding")
        self.num_patches = (self.image_size // self.patch_size) ** 2
        self.num_positions = self.num_patches + 1
    def build(self, input_shape=None):
        self.class_embedding = self.add_weight(shape=(1, 1, self.embed_dim), initializer=get_initializer(self.config.initializer_range), trainable=True, name="class_embedding")
        self.position_embedding = self.add_weight(shape=(1, self.num_positions, self.embed_dim), initializer=get_initializer(self.config.initializer_range), trainable=True, name="position_embedding")
        if self.built: return
        self.built = True
        if getattr(self, "patch_embedding", None) is not None:
            with tf.name_scope(self.patch_embedding.name): self.patch_embedding.build([None, None, None, 3])
    def call(self, pixel_values: tf.Tensor) -> tf.Tensor:
        batch_size = tf.shape(pixel_values)[0]
        pixel_values = tf.transpose(pixel_values, perm=(0, 2, 3, 1))
        patch_embeds = self.patch_embedding(pixel_values)
        patch_embeds = tf.reshape(patch_embeds, (batch_size, self.num_patches, -1))
        class_embeds = tf.broadcast_to(self.class_embedding, (batch_size, 1, self.embed_dim))
        embeddings = tf.concat([class_embeds, patch_embeds], axis=1)
        embeddings = embeddings + self.position_embedding[:, : tf.shape(embeddings)[1], :]
        return embeddings
class TFBlipTextEmbeddings(keras.layers.Layer):
    def __init__(self, config: BlipTextConfig, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = config.hidden_size
        self.config = config
    def build(self, input_shape: tf.TensorShape = None):
        with tf.name_scope("token_embedding"): self.weight = self.add_weight(shape=(self.config.vocab_size, self.embed_dim), initializer=get_initializer(self.config.initializer_factor * self.config.initializer_range), trainable=True, name="weight")
        with tf.name_scope("position_embedding"): self.position_embedding = self.add_weight(shape=(self.config.max_position_embeddings, self.embed_dim), initializer=get_initializer(self.config.initializer_factor * self.config.initializer_range), trainable=True, name="embeddings")
        super().build(input_shape)
    def call(self, input_ids: tf.Tensor = None, position_ids: tf.Tensor = None, inputs_embeds: tf.Tensor = None) -> tf.Tensor:
        if input_ids is None and inputs_embeds is None: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if inputs_embeds is None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = tf.gather(params=self.weight, indices=input_ids)
        input_shape = shape_list(inputs_embeds)[:-1]
        if position_ids is None: position_ids = tf.expand_dims(tf.range(start=0, limit=input_shape[-1]), axis=0)
        position_embeds = tf.gather(params=self.position_embedding, indices=position_ids)
        position_embeds = tf.tile(input=position_embeds, multiples=(input_shape[0], 1, 1))
        final_embeddings = inputs_embeds + position_embeds
        return final_embeddings
class TFBlipAttention(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        if self.head_dim * self.num_heads != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.scale = self.head_dim**-0.5
        self.dropout = keras.layers.Dropout(config.attention_dropout, name="dropout")
        self.qkv = keras.layers.Dense(3 * self.embed_dim, kernel_initializer=get_initializer(config.initializer_range), name="qkv")
        self.projection = keras.layers.Dense(self.embed_dim, kernel_initializer=get_initializer(config.initializer_range), name="projection")
    def call(self, hidden_states: tf.Tensor, head_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = False, training: Optional[bool] = None) -> Tuple[tf.Tensor, tf.Tensor | None, Tuple[tf.Tensor] | None]:
        bsz, tgt_len, embed_dim = shape_list(hidden_states)
        mixed_qkv = self.qkv(hidden_states)
        mixed_qkv = tf.reshape(mixed_qkv, (bsz, tgt_len, 3, self.num_heads, self.head_dim))
        mixed_qkv = tf.transpose(mixed_qkv, perm=(2, 0, 3, 1, 4))
        query_states, key_states, value_states = mixed_qkv[0], mixed_qkv[1], mixed_qkv[2]
        attention_scores = query_states @ tf.transpose(key_states, (0, 1, 3, 2))
        attention_scores = attention_scores * self.scale
        attention_probs = stable_softmax(attention_scores, axis=-1)
        attention_probs = self.dropout(attention_probs, training=training)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        context_layer = tf.transpose(attention_probs @ value_states, perm=(0, 2, 1, 3))
        new_context_layer_shape = shape_list(context_layer)[:-2] + [self.embed_dim]
        context_layer = tf.reshape(context_layer, new_context_layer_shape)
        output = self.projection(context_layer)
        outputs = (output, attention_probs) if output_attentions else (output, None)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dropout", None) is not None:
            with tf.name_scope(self.dropout.name): self.dropout.build(None)
        if getattr(self, "qkv", None) is not None:
            with tf.name_scope(self.qkv.name): self.qkv.build([None, None, self.embed_dim])
        if getattr(self, "projection", None) is not None:
            with tf.name_scope(self.projection.name): self.projection.build([None, None, self.embed_dim])
class TFBlipMLP(keras.layers.Layer):
    def __init__(self, config: BlipConfig, **kwargs):
        super().__init__(**kwargs)
        self.activation_fn = get_tf_activation(config.hidden_act)
        in_proj_std = (config.hidden_size**-0.5) * ((2 * config.num_hidden_layers) ** -0.5)
        fc_std = (2 * config.hidden_size) ** -0.5
        self.fc1 = keras.layers.Dense(units=config.intermediate_size, kernel_initializer=get_initializer(fc_std), name="fc1")
        self.fc2 = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(in_proj_std), name="fc2")
        self.config = config
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.fc1(inputs=hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(inputs=hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "fc1", None) is not None:
            with tf.name_scope(self.fc1.name): self.fc1.build([None, None, self.config.hidden_size])
        if getattr(self, "fc2", None) is not None:
            with tf.name_scope(self.fc2.name): self.fc2.build([None, None, self.config.intermediate_size])
class TFBlipEncoderLayer(keras.layers.Layer):
    def __init__(self, config: BlipConfig, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = config.hidden_size
        self.self_attn = TFBlipAttention(config, name="self_attn")
        self.layer_norm1 = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layer_norm1")
        self.mlp = TFBlipMLP(config, name="mlp")
        self.layer_norm2 = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layer_norm2")
    def call(self, hidden_states: tf.Tensor, attention_mask: tf.Tensor, output_attentions: Optional[bool] = False, training: Optional[bool] = None) -> Tuple[tf.Tensor]:
        residual = hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, head_mask=attention_mask, output_attentions=output_attentions, training=training)
        hidden_states = hidden_states + residual
        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = hidden_states + residual
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "self_attn", None) is not None:
            with tf.name_scope(self.self_attn.name): self.self_attn.build(None)
        if getattr(self, "layer_norm1", None) is not None:
            with tf.name_scope(self.layer_norm1.name): self.layer_norm1.build([None, None, self.embed_dim])
        if getattr(self, "mlp", None) is not None:
            with tf.name_scope(self.mlp.name): self.mlp.build(None)
        if getattr(self, "layer_norm2", None) is not None:
            with tf.name_scope(self.layer_norm2.name): self.layer_norm2.build([None, None, self.embed_dim])
class TFBlipPreTrainedModel(TFPreTrainedModel):
    config_class = BlipConfig
    base_model_prefix = "blip"
    _keys_to_ignore_on_load_missing = [r"position_ids"]
BLIP_START_DOCSTRING = r"""
    This model inherits from [`TFPreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a [keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model) subclass. Use it
    as a regular TF 2.0 Keras Model and refer to the TF 2.0 documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`BlipConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~TFPreTrainedModel.from_pretrained`] method to load the model weights.
"""
BLIP_VISION_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`tf.Tensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`BlipImageProcessor`]. See [`BlipImageProcessor.__call__`] for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
BLIP_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`tf.Tensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoProcessor`]. See [`BlipProcessor.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        pixel_values (`tf.Tensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`BlipImageProcessor`]. See [`BlipImageProcessor.__call__`] for details.
        return_loss (`bool`, *optional*):
            Whether or not to return the contrastive loss.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@keras_serializable
class TFBlipEncoder(keras.layers.Layer):
    config_class = BlipConfig
    def __init__(self, config: BlipConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.layers = [TFBlipEncoderLayer(config, name=f"layers_._{i}") for i in range(config.num_hidden_layers)]
    @unpack_inputs
    def call(self, inputs_embeds, attention_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        hidden_states = inputs_embeds
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            layer_outputs = encoder_layer(hidden_states, attention_mask, output_attentions=output_attentions, training=training)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return TFBaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layers", None) is not None:
            for layer in self.layers:
                with tf.name_scope(layer.name): layer.build(None)
class TFBlipVisionModel(TFBlipPreTrainedModel):
    main_input_name = "pixel_values"
    config_class = BlipVisionConfig
    def __init__(self, config: BlipVisionConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.config = config
        self.embeddings = TFBlipVisionEmbeddings(config, name="embeddings")
        self.encoder = TFBlipEncoder(config, name="encoder")
        self.post_layernorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="post_layernorm")
        self.embed_dim = config.hidden_size
    def serving_output(self, output: TFBaseModelOutputWithPooling) -> TFBaseModelOutputWithPooling:
        hs = tf.convert_to_tensor(output.hidden_states) if self.config.output_hidden_states else None
        attns = tf.convert_to_tensor(output.attentions) if self.config.output_attentions else None
        return TFBaseModelOutputWithPooling(last_hidden_state=output.last_hidden_state, pooler_output=output.pooler_output, hidden_states=hs, attentions=attns)
    @unpack_inputs
    @add_start_docstrings_to_model_forward(BLIP_VISION_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: Optional[bool] = None) -> Union[Tuple, TFBaseModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        hidden_states = self.embeddings(pixel_values)
        encoder_outputs = self.encoder(inputs_embeds=hidden_states, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        last_hidden_state = encoder_outputs[0]
        last_hidden_state = self.post_layernorm(last_hidden_state)
        pooled_output = last_hidden_state[:, 0, :]
        pooled_output = self.post_layernorm(tf.expand_dims(pooled_output, 1))
        pooled_output = tf.squeeze(pooled_output, 1)
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return TFBaseModelOutputWithPooling(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
    def get_input_embeddings(self): return self.embeddings
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name): self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name): self.encoder.build(None)
        if getattr(self, "post_layernorm", None) is not None:
            with tf.name_scope(self.post_layernorm.name): self.post_layernorm.build([None, None, self.embed_dim])
class TFBlipMainLayer(keras.layers.Layer):
    config_class = BlipConfig
    def __init__(self, config: BlipConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(config.text_config, BlipTextConfig): raise TypeError(f"config.text_config is expected to be of type BlipTextConfig but is of type {type(config.text_config)}.")
        if not isinstance(config.vision_config, BlipVisionConfig): raise TypeError(f"config.vision_config is expected to be of type BlipVisionConfig but is of type {type(config.vision_config)}.")
        text_config = config.text_config
        vision_config = config.vision_config
        self.projection_dim = config.projection_dim
        self.text_embed_dim = text_config.hidden_size
        self.vision_embed_dim = vision_config.hidden_size
        self.text_model = TFBlipTextModel(text_config, name="text_model")
        self.vision_model = TFBlipVisionModel(vision_config, name="vision_model")
        self.visual_projection = keras.layers.Dense(self.projection_dim, use_bias=False, kernel_initializer=get_initializer(config.initializer_range), name="visual_projection")
        self.text_projection = keras.layers.Dense(self.projection_dim, use_bias=False, kernel_initializer=get_initializer(config.initializer_range), name="text_projection")
        self.config = config
    def build(self, input_shape=None):
        self.logit_scale = self.add_weight(name="logit_scale", shape=[], initializer=keras.initializers.Constant(self.config.logit_scale_init_value), trainable=True)
        if self.built: return
        self.built = True
        if getattr(self, "text_model", None) is not None:
            with tf.name_scope(self.text_model.name): self.text_model.build(None)
        if getattr(self, "vision_model", None) is not None:
            with tf.name_scope(self.vision_model.name): self.vision_model.build(None)
        if getattr(self, "visual_projection", None) is not None:
            with tf.name_scope(self.visual_projection.name): self.visual_projection.build([None, None, self.vision_embed_dim])
        if getattr(self, "text_projection", None) is not None:
            with tf.name_scope(self.text_projection.name): self.text_projection.build([None, None, self.text_embed_dim])
    @unpack_inputs
    def call(self, input_ids: tf.Tensor | None = None, pixel_values: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None, position_ids: tf.Tensor | None = None,
    return_loss: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBlipOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        text_outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        image_embeds = vision_outputs[1]
        image_embeds = self.visual_projection(image_embeds)
        text_embeds = text_outputs[1]
        text_embeds = self.text_projection(text_embeds)
        image_embeds = image_embeds / tf.norm(image_embeds, ord=2, axis=-1, keepdims=True)
        text_embeds = text_embeds / tf.norm(text_embeds, ord=2, axis=-1, keepdims=True)
        logit_scale = tf.exp(self.logit_scale)
        logits_per_text = tf.matmul(text_embeds, image_embeds, transpose_b=True) * logit_scale
        logits_per_image = tf.transpose(logits_per_text)
        loss = None
        if return_loss:
            loss = blip_loss(logits_per_text)
            loss = tf.reshape(loss, (1,))
        if not return_dict:
            output = (logits_per_image, logits_per_text, text_embeds, image_embeds, text_outputs, vision_outputs)
            return ((loss,) + output) if loss is not None else output
        return TFBlipOutput(loss=loss, logits_per_image=logits_per_image, logits_per_text=logits_per_text, text_embeds=text_embeds, image_embeds=image_embeds, text_model_output=text_outputs, vision_model_output=vision_outputs)
class TFBlipModel(TFBlipPreTrainedModel):
    config_class = BlipConfig
    _keys_to_ignore_on_load_missing = [r"text_decoder.cls.predictions.decoder.bias"]
    main_input_name = "input_ids"
    def __init__(self, config: BlipConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.blip = TFBlipMainLayer(config, name="blip")
    def serving_output(self, output: TFBlipOutput) -> TFBlipOutput: return TFBlipOutput(logits_per_image=output.logits_per_image, logits_per_text=output.logits_per_text, text_embeds=output.text_embeds, image_embeds=output.image_embeds)
    @unpack_inputs
    @add_start_docstrings_to_model_forward(BLIP_INPUTS_DOCSTRING)
    def call(self, input_ids: tf.Tensor | None = None, pixel_values: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None, position_ids: tf.Tensor | None = None,
    return_loss: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBlipOutput]:
        outputs = self.blip(input_ids=input_ids, pixel_values=pixel_values, attention_mask=attention_mask, position_ids=position_ids, return_loss=return_loss, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        return outputs
    @add_start_docstrings_to_model_forward(BLIP_TEXT_INPUTS_DOCSTRING)
    def get_text_features(self, input_ids: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None, position_ids: tf.Tensor | None = None, return_dict: Optional[bool] = None) -> tf.Tensor:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        text_outputs = self.blip.text_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, return_dict=return_dict)
        pooled_output = text_outputs[1]
        text_features = self.blip.text_projection(pooled_output)
        return text_features
    @add_start_docstrings_to_model_forward(BLIP_VISION_INPUTS_DOCSTRING)
    def get_image_features(self, pixel_values: tf.Tensor | None = None, return_dict: Optional[bool] = None) -> tf.Tensor:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.blip.vision_model(pixel_values=pixel_values, return_dict=return_dict)
        pooled_output = vision_outputs[1]
        image_features = self.blip.visual_projection(pooled_output)
        return image_features
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "blip", None) is not None:
            with tf.name_scope(self.blip.name): self.blip.build(None)
@add_start_docstrings("""
    BLIP Model for image captioning. The model consists of a vision encoder and a text decoder. One can optionally pass
    `input_ids` to the model, which serve as a text prompt, to make the text decoder continue the prompt. Otherwise,
    the decoder starts generating text from the [BOS] (beginning-of-sequence) token. will start generating the caption
    from the text input. If no text input is provided, the decoder will start with the [BOS] token only.
    """, BLIP_START_DOCSTRING)
class TFBlipForConditionalGeneration(TFBlipPreTrainedModel):
    config_class = BlipConfig
    _keys_to_ignore_on_load_missing = [r"text_decoder.cls.predictions.decoder.bias"]
    main_input_name = "pixel_values"
    def __init__(self, config: BlipConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.vision_model = TFBlipVisionModel(config.vision_config, name="vision_model")
        self.text_decoder = TFBlipTextLMHeadModel(config.text_config, name="text_decoder")
        self.decoder_input_ids = config.text_config.bos_token_id
        self.decoder_pad_token_id = config.text_config.pad_token_id
    def get_input_embeddings(self) -> keras.layers.Layer: return self.vision_model.embeddings.patch_embedding
    @unpack_inputs
    @add_start_docstrings_to_model_forward(BLIP_VISION_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor, input_ids: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, labels: tf.Tensor | None = None, return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBlipForConditionalGenerationModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        image_embeds = vision_outputs[0]
        outputs = self.text_decoder(input_ids=input_ids, attention_mask=attention_mask, encoder_hidden_states=image_embeds, labels=labels, return_dict=False, training=training)
        if not return_dict:
            outputs = (outputs[0], outputs[1], image_embeds, vision_outputs[0]) + vision_outputs[2:]
            return tuple(output for output in outputs if output is not None)
        if labels is not None:
            loss = outputs[0]
            logits = outputs[1]
        else:
            loss = None
            logits = outputs[0]
        if loss is not None and loss.shape.rank == 0: loss = tf.reshape(loss, (1,))
        return TFBlipForConditionalGenerationModelOutput(loss=loss, logits=logits, image_embeds=image_embeds, last_hidden_state=vision_outputs.last_hidden_state, hidden_states=vision_outputs.hidden_states, attentions=vision_outputs.attentions)
    def generate(self, pixel_values: tf.Tensor, input_ids: tf.Tensor | None = None, attention_mask: tf.Tensor | None = None, **generate_kwargs) -> tf.Tensor:
        batch_size = pixel_values.shape[0]
        vision_outputs = self.vision_model(pixel_values=pixel_values)
        image_embeds = vision_outputs[0]
        image_attention_mask = tf.ones(shape_list(image_embeds)[:-1], dtype=tf.int32)
        if isinstance(input_ids, list): input_ids = tf.convert_to_tensor(input_ids, dtype=tf.int32)
        elif input_ids is None:
            input_ids = tf.convert_to_tensor([[self.decoder_input_ids, self.config.text_config.eos_token_id]], dtype=tf.int32)
            input_ids = tf.tile(input_ids, (batch_size, 1))
        input_ids = tf.concat([tf.ones((batch_size, 1), dtype=tf.int32) * self.config.text_config.bos_token_id, input_ids[:, 1:]], axis=1)
        attention_mask = attention_mask[:, :-1] if attention_mask is not None else None
        outputs = self.text_decoder.generate(input_ids=input_ids[:, :-1], eos_token_id=self.config.text_config.sep_token_id, pad_token_id=self.config.text_config.pad_token_id,
        attention_mask=attention_mask, encoder_hidden_states=image_embeds, encoder_attention_mask=image_attention_mask, **generate_kwargs)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "vision_model", None) is not None:
            with tf.name_scope(self.vision_model.name): self.vision_model.build(None)
        if getattr(self, "text_decoder", None) is not None:
            with tf.name_scope(self.text_decoder.name): self.text_decoder.build(None)
@add_start_docstrings("""
    BLIP Model for visual question answering. The model consists of a vision encoder, a text encoder as well as a text
    decoder. The vision encoder will encode the input image, the text encoder will encode the input question together
    with the encoding of the image, and the text decoder will output the answer to the question.
    """, BLIP_START_DOCSTRING)
class TFBlipForQuestionAnswering(TFBlipPreTrainedModel):
    config_class = BlipConfig
    _keys_to_ignore_on_load_missing = [r"text_decoder.cls.predictions.decoder.bias"]
    def __init__(self, config: BlipConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.vision_model = TFBlipVisionModel(config.vision_config, name="vision_model")
        self.text_encoder = TFBlipTextModel(config.text_config, name="text_encoder", add_pooling_layer=False)
        self.text_decoder = TFBlipTextLMHeadModel(config.text_config, name="text_decoder")
        self.decoder_pad_token_id = config.text_config.pad_token_id
        self.decoder_start_token_id = config.text_config.bos_token_id
    def get_input_embeddings(self) -> keras.layers.Layer: return self.vision_model.embeddings.patch_embedding
    def _shift_right(self, input_ids):
        decoder_start_token_id = self.decoder_start_token_id
        pad_token_id = self.decoder_pad_token_id
        if decoder_start_token_id is None or pad_token_id is None: raise ValueError("decoder_start_token_id and pad_token_id must be defined!")
        start_tokens = tf.fill((shape_list(input_ids)[0], 1), decoder_start_token_id)
        start_tokens = tf.cast(start_tokens, input_ids.dtype)
        shifted_input_ids = tf.concat([start_tokens, input_ids[:, :-1]], -1)
        shifted_input_ids = tf.where(shifted_input_ids == -100, tf.cast(tf.fill(shape_list(shifted_input_ids), pad_token_id), shifted_input_ids.dtype), shifted_input_ids)
        tf.debugging.assert_greater_equal(shifted_input_ids, tf.constant(0, dtype=shifted_input_ids.dtype))
        return shifted_input_ids
    @unpack_inputs
    @add_start_docstrings_to_model_forward(BLIP_VISION_INPUTS_DOCSTRING)
    def call(self, input_ids: tf.Tensor, pixel_values: tf.Tensor | None = None, decoder_input_ids: tf.Tensor | None = None, decoder_attention_mask: tf.Tensor | None = None,
    attention_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, labels: tf.Tensor | None = None,
    return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBlipTextVisionModelOutput]:
        if labels is None and decoder_input_ids is None: raise ValueError("Either `decoder_input_ids` or `labels` should be passed when calling `TFBlipForQuestionAnswering`. if you are training the model make sure that `labels` is passed, if you are using the model for inference make sure that `decoder_input_ids` is passed or call `generate`")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        image_embeds = vision_outputs[0]
        image_attention_mask = tf.ones(shape_list(image_embeds)[:-1], dtype=tf.int64)
        question_embeds = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask, encoder_hidden_states=image_embeds, encoder_attention_mask=image_attention_mask, return_dict=return_dict, training=training)
        question_embeds = question_embeds[0] if not return_dict else question_embeds.last_hidden_state
        if labels is not None and decoder_input_ids is None: decoder_input_ids = labels
        answer_output = self.text_decoder(input_ids=decoder_input_ids, attention_mask=decoder_attention_mask, encoder_hidden_states=question_embeds, encoder_attention_mask=attention_mask,
        labels=labels, return_dict=return_dict, training=training)
        if labels is not None: decoder_loss = tf.reduce_mean(answer_output.loss) if return_dict else tf.reduce_mean(answer_output[0])
        else: decoder_loss = None
        if not return_dict:
            outputs = (decoder_loss, image_embeds, vision_outputs[0]) + vision_outputs[2:]
            return tuple(output for output in outputs if output is not None)
        return TFBlipTextVisionModelOutput(loss=decoder_loss, image_embeds=image_embeds, last_hidden_state=vision_outputs.last_hidden_state, hidden_states=vision_outputs.hidden_states, attentions=vision_outputs.attentions)
    def generate(self, input_ids: tf.Tensor, pixel_values: tf.Tensor, attention_mask: tf.Tensor | None = None, **generate_kwargs) -> tf.Tensor:
        vision_outputs = self.vision_model(pixel_values=pixel_values)
        image_embeds = vision_outputs[0]
        image_attention_mask = tf.ones(shape_list(image_embeds)[:-1], dtype=tf.int32)
        if isinstance(input_ids, list): input_ids = tf.Tensor(input_ids)
        question_outputs = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask, encoder_hidden_states=image_embeds, encoder_attention_mask=image_attention_mask, return_dict=False)
        question_embeds = question_outputs[0]
        question_attention_mask = tf.ones(shape_list(question_embeds)[:-1], dtype=tf.int32)
        bos_ids = tf.fill((tf.shape(question_embeds)[0], 1), value=tf.cast(self.decoder_start_token_id, input_ids.dtype))
        outputs = self.text_decoder.generate(input_ids=bos_ids, eos_token_id=self.config.text_config.sep_token_id, pad_token_id=self.config.text_config.pad_token_id,
        encoder_hidden_states=question_embeds, encoder_attention_mask=question_attention_mask, **generate_kwargs)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "vision_model", None) is not None:
            with tf.name_scope(self.vision_model.name): self.vision_model.build(None)
        if getattr(self, "text_encoder", None) is not None:
            with tf.name_scope(self.text_encoder.name): self.text_encoder.build(None)
        if getattr(self, "text_decoder", None) is not None:
            with tf.name_scope(self.text_decoder.name): self.text_decoder.build(None)
@add_start_docstrings("""
    BLIP Model with a vision and text projector, and a classification head on top. The model is used in the context of
    image-text retrieval. Given an image and a text, the model returns the probability of the text being relevant to
    the image.
    """, BLIP_START_DOCSTRING)
class TFBlipForImageTextRetrieval(TFBlipPreTrainedModel):
    config_class = BlipConfig
    def __init__(self, config: BlipConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.vision_model = TFBlipVisionModel(config.vision_config, name="vision_model")
        self.text_encoder = TFBlipTextModel(config.text_config, name="text_encoder", add_pooling_layer=False)
        self.vision_proj = keras.layers.Dense(config.image_text_hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="vision_proj")
        self.text_proj = keras.layers.Dense(config.image_text_hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="text_proj")
        self.itm_head = keras.layers.Dense(2, kernel_initializer=get_initializer(config.initializer_range), name="itm_head")
        self.decoder_pad_token_id = (config.text_config.pad_token_id if not hasattr(config, "decoder_pad_token_id") else config.decoder_pad_token_id)
        self.decoder_start_token_id = (config.text_config.bos_token_id if not hasattr(config, "decoder_start_token_id") else config.decoder_start_token_id)
        self.config = config
    def get_input_embeddings(self) -> keras.layers.Layer: return self.vision_model.embeddings.patch_embedding
    @unpack_inputs
    @add_start_docstrings_to_model_forward(BLIP_VISION_INPUTS_DOCSTRING)
    def call(self, input_ids: tf.Tensor, pixel_values: tf.Tensor | None = None, use_itm_head: Optional[bool] = True, attention_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: Optional[bool] = None) -> Union[Tuple, TFBlipImageTextMatchingModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        image_embeds = vision_outputs[0]
        image_atts = tf.ones(shape_list(image_embeds)[:-1], dtype=tf.int64)
        itm_question_embeds = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask, encoder_hidden_states=image_embeds, encoder_attention_mask=image_atts, return_dict=return_dict, training=training)
        itm_question_embeds = itm_question_embeds[0] if not return_dict else itm_question_embeds.last_hidden_state
        itm_output = self.itm_head(itm_question_embeds[:, 0, :])
        no_itm_question_embeds = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask, return_dict=return_dict, training=training)
        no_itm_question_embeds = (no_itm_question_embeds[0] if not return_dict else no_itm_question_embeds.last_hidden_state)
        image_feat, _ = tf.linalg.normalize(self.vision_proj(image_embeds[:, 0, :]), ord=2, axis=-1)
        text_feat, _ = tf.linalg.normalize(self.text_proj(no_itm_question_embeds[:, 0, :]), ord=2, axis=-1)
        no_itm_output = tf.matmul(image_feat, text_feat, transpose_b=True)
        if use_itm_head:
            output = itm_output
            question_embeds = itm_question_embeds
        else:
            output = no_itm_output
            question_embeds = no_itm_question_embeds
        if not return_dict:
            outputs = (output, vision_outputs[0]) + vision_outputs[2:] + (question_embeds,)
            return tuple(output for output in outputs if output is not None)
        return TFBlipImageTextMatchingModelOutput(itm_score=output, last_hidden_state=vision_outputs.last_hidden_state, hidden_states=vision_outputs.hidden_states, attentions=vision_outputs.attentions, question_embeds=question_embeds)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "vision_model", None) is not None:
            with tf.name_scope(self.vision_model.name): self.vision_model.build(None)
        if getattr(self, "text_encoder", None) is not None:
            with tf.name_scope(self.text_encoder.name): self.text_encoder.build(None)
        if getattr(self, "vision_proj", None) is not None:
            with tf.name_scope(self.vision_proj.name): self.vision_proj.build([None, None, self.config.vision_config.hidden_size])
        if getattr(self, "text_proj", None) is not None:
            with tf.name_scope(self.text_proj.name): self.text_proj.build([None, None, self.config.text_config.hidden_size])
        if getattr(self, "itm_head", None) is not None:
            with tf.name_scope(self.itm_head.name): self.itm_head.build([None, None, self.config.text_config.hidden_size])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
