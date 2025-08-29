from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections.abc
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_outputs import (TFBaseModelOutput, TFBaseModelOutputWithPooling, TFImageClassifierOutput, TFMaskedImageModelingOutput)
from ...modeling_tf_utils import (TFPreTrainedModel, TFSequenceClassificationLoss, get_initializer, keras, keras_serializable, unpack_inputs)
from ...tf_utils import shape_list, stable_softmax
from ...utils import (ModelOutput, add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_deit import DeiTConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "DeiTConfig"
_CHECKPOINT_FOR_DOC = "facebook/deit-base-distilled-patch16-224"
_EXPECTED_OUTPUT_SHAPE = [1, 198, 768]
_IMAGE_CLASS_CHECKPOINT = "facebook/deit-base-distilled-patch16-224"
_IMAGE_CLASS_EXPECTED_OUTPUT = "tabby, tabby cat"
@dataclass
class TFDeiTForImageClassificationWithTeacherOutput(ModelOutput):
    """Args:"""
    logits: tf.Tensor = None
    cls_logits: tf.Tensor = None
    distillation_logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
class TFDeiTEmbeddings(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, use_mask_token: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.use_mask_token = use_mask_token
        self.patch_embeddings = TFDeiTPatchEmbeddings(config=config, name="patch_embeddings")
        self.dropout = keras.layers.Dropout(config.hidden_dropout_prob, name="dropout")
    def build(self, input_shape=None):
        self.cls_token = self.add_weight(shape=(1, 1, self.config.hidden_size), initializer=keras.initializers.zeros(), trainable=True, name="cls_token")
        self.distillation_token = self.add_weight(shape=(1, 1, self.config.hidden_size), initializer=keras.initializers.zeros(), trainable=True, name="distillation_token")
        self.mask_token = None
        if self.use_mask_token: self.mask_token = self.add_weight(shape=(1, 1, self.config.hidden_size), initializer=keras.initializers.zeros(), trainable=True, name="mask_token")
        num_patches = self.patch_embeddings.num_patches
        self.position_embeddings = self.add_weight(shape=(1, num_patches + 2, self.config.hidden_size), initializer=keras.initializers.zeros(), trainable=True, name="position_embeddings")
        if self.built: return
        self.built = True
        if getattr(self, "patch_embeddings", None) is not None:
            with tf.name_scope(self.patch_embeddings.name): self.patch_embeddings.build(None)
        if getattr(self, "dropout", None) is not None:
            with tf.name_scope(self.dropout.name): self.dropout.build(None)
    def interpolate_pos_encoding(self, embeddings: tf.Tensor, height: int, width: int) -> tf.Tensor:
        num_patches = embeddings.shape[1] - 2
        num_positions = self.position_embeddings.shape[1] - 2
        if num_patches == num_positions and height == width: return self.position_embeddings
        class_pos_embed = self.position_embeddings[:, 0, :]
        dist_pos_embed = self.position_embeddings[:, 1, :]
        patch_pos_embed = self.position_embeddings[:, 2:, :]
        dim = embeddings.shape[-1]
        h0 = height // self.config.patch_size
        w0 = width // self.config.patch_size
        h0, w0 = h0 + 0.1, w0 + 0.1
        patch_pos_embed = tf.reshape(patch_pos_embed, (1, int(math.sqrt(num_positions)), int(math.sqrt(num_positions)), dim))
        patch_pos_embed = tf.image.resize(patch_pos_embed, size=(int(h0), int(w0)), method="bicubic")
        patch_pos_embed = tf.transpose(patch_pos_embed, perm=[0, 2, 3, 1])
        patch_pos_embed = tf.reshape(patch_pos_embed, (1, -1, dim))
        return tf.concat([tf.expand_dims(class_pos_embed, axis=0), tf.expand_dims(dist_pos_embed, axis=0), patch_pos_embed], axis=1)
    def call(self, pixel_values: tf.Tensor, bool_masked_pos: tf.Tensor | None = None, training: bool = False, interpolate_pos_encoding: bool = False) -> tf.Tensor:
        _, height, width, _ = pixel_values.shape
        embeddings = self.patch_embeddings(pixel_values)
        batch_size, seq_length, _ = shape_list(embeddings)
        if bool_masked_pos is not None:
            mask_tokens = tf.tile(self.mask_token, [batch_size, seq_length, 1])
            mask = tf.expand_dims(bool_masked_pos, axis=-1)
            mask = tf.cast(mask, dtype=mask_tokens.dtype)
            embeddings = embeddings * (1.0 - mask) + mask_tokens * mask
        cls_tokens = tf.repeat(self.cls_token, repeats=batch_size, axis=0)
        distillation_tokens = tf.repeat(self.distillation_token, repeats=batch_size, axis=0)
        embeddings = tf.concat((cls_tokens, distillation_tokens, embeddings), axis=1)
        position_embedding = self.position_embeddings
        if interpolate_pos_encoding: position_embedding = self.interpolate_pos_encoding(embeddings, height, width)
        embeddings = embeddings + position_embedding
        embeddings = self.dropout(embeddings, training=training)
        return embeddings
class TFDeiTPatchEmbeddings(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.projection = keras.layers.Conv2D(hidden_size, kernel_size=patch_size, strides=patch_size, name="projection")
    def call(self, pixel_values: tf.Tensor) -> tf.Tensor:
        batch_size, height, width, num_channels = shape_list(pixel_values)
        if tf.executing_eagerly() and num_channels != self.num_channels: raise ValueError("Make sure that the channel dimension of the pixel values match with the one set in the configuration.")
        x = self.projection(pixel_values)
        batch_size, height, width, num_channels = shape_list(x)
        x = tf.reshape(x, (batch_size, height * width, num_channels))
        return x
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "projection", None) is not None:
            with tf.name_scope(self.projection.name): self.projection.build([None, None, None, self.num_channels])
class TFDeiTSelfAttention(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
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
        self.config = config
    def transpose_for_scores(self, tensor: tf.Tensor, batch_size: int) -> tf.Tensor:
        tensor = tf.reshape(tensor=tensor, shape=(batch_size, -1, self.num_attention_heads, self.attention_head_size))
        return tf.transpose(tensor, perm=[0, 2, 1, 3])
    def call(self, hidden_states: tf.Tensor, head_mask: tf.Tensor, output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        batch_size = shape_list(hidden_states)[0]
        mixed_query_layer = self.query(inputs=hidden_states)
        mixed_key_layer = self.key(inputs=hidden_states)
        mixed_value_layer = self.value(inputs=hidden_states)
        query_layer = self.transpose_for_scores(mixed_query_layer, batch_size)
        key_layer = self.transpose_for_scores(mixed_key_layer, batch_size)
        value_layer = self.transpose_for_scores(mixed_value_layer, batch_size)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        dk = tf.cast(self.sqrt_att_head_size, dtype=attention_scores.dtype)
        attention_scores = tf.divide(attention_scores, dk)
        attention_probs = stable_softmax(logits=attention_scores, axis=-1)
        attention_probs = self.dropout(inputs=attention_probs, training=training)
        if head_mask is not None: attention_probs = tf.multiply(attention_probs, head_mask)
        attention_output = tf.matmul(attention_probs, value_layer)
        attention_output = tf.transpose(attention_output, perm=[0, 2, 1, 3])
        attention_output = tf.reshape(tensor=attention_output, shape=(batch_size, -1, self.all_head_size))
        outputs = (attention_output, attention_probs) if output_attentions else (attention_output,)
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
class TFDeiTSelfOutput(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states: tf.Tensor, input_tensor: tf.Tensor, training: bool = False) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.dropout(inputs=hidden_states, training=training)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.hidden_size])
class TFDeiTAttention(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
        super().__init__(**kwargs)
        self.self_attention = TFDeiTSelfAttention(config, name="attention")
        self.dense_output = TFDeiTSelfOutput(config, name="output")
    def prune_heads(self, heads): raise NotImplementedError
    def call(self, input_tensor: tf.Tensor, head_mask: tf.Tensor, output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        self_outputs = self.self_attention(hidden_states=input_tensor, head_mask=head_mask, output_attentions=output_attentions, training=training)
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
class TFDeiTIntermediate(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
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
class TFDeiTOutput(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
        super().__init__(**kwargs)
        self.dense = keras.layers.Dense(units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def call(self, hidden_states: tf.Tensor, input_tensor: tf.Tensor, training: bool = False) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.dropout(inputs=hidden_states, training=training)
        hidden_states = hidden_states + input_tensor
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name): self.dense.build([None, None, self.config.intermediate_size])
class TFDeiTLayer(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
        super().__init__(**kwargs)
        self.attention = TFDeiTAttention(config, name="attention")
        self.intermediate = TFDeiTIntermediate(config, name="intermediate")
        self.deit_output = TFDeiTOutput(config, name="output")
        self.layernorm_before = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layernorm_before")
        self.layernorm_after = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layernorm_after")
        self.config = config
    def call(self, hidden_states: tf.Tensor, head_mask: tf.Tensor, output_attentions: bool, training: bool = False) -> Tuple[tf.Tensor]:
        attention_outputs = self.attention(input_tensor=self.layernorm_before(inputs=hidden_states, training=training), head_mask=head_mask, output_attentions=output_attentions, training=training)
        attention_output = attention_outputs[0]
        hidden_states = attention_output + hidden_states
        layer_output = self.layernorm_after(inputs=hidden_states, training=training)
        intermediate_output = self.intermediate(hidden_states=layer_output, training=training)
        layer_output = self.deit_output(hidden_states=intermediate_output, input_tensor=hidden_states, training=training)
        outputs = (layer_output,) + attention_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "attention", None) is not None:
            with tf.name_scope(self.attention.name): self.attention.build(None)
        if getattr(self, "intermediate", None) is not None:
            with tf.name_scope(self.intermediate.name): self.intermediate.build(None)
        if getattr(self, "deit_output", None) is not None:
            with tf.name_scope(self.deit_output.name): self.deit_output.build(None)
        if getattr(self, "layernorm_before", None) is not None:
            with tf.name_scope(self.layernorm_before.name): self.layernorm_before.build([None, None, self.config.hidden_size])
        if getattr(self, "layernorm_after", None) is not None:
            with tf.name_scope(self.layernorm_after.name): self.layernorm_after.build([None, None, self.config.hidden_size])
class TFDeiTEncoder(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
        super().__init__(**kwargs)
        self.layer = [TFDeiTLayer(config, name=f"layer_._{i}") for i in range(config.num_hidden_layers)]
    def call(self, hidden_states: tf.Tensor, head_mask: tf.Tensor, output_attentions: bool, output_hidden_states: bool, return_dict: bool, training: bool = False) -> Union[TFBaseModelOutput, Tuple[tf.Tensor]]:
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_outputs = layer_module(hidden_states=hidden_states, head_mask=head_mask[i], output_attentions=output_attentions, training=training)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_attentions] if v is not None)
        return TFBaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "layer", None) is not None:
            for layer in self.layer:
                with tf.name_scope(layer.name): layer.build(None)
@keras_serializable
class TFDeiTMainLayer(keras.layers.Layer):
    config_class = DeiTConfig
    def __init__(self, config: DeiTConfig, add_pooling_layer: bool = True, use_mask_token: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.embeddings = TFDeiTEmbeddings(config, use_mask_token=use_mask_token, name="embeddings")
        self.encoder = TFDeiTEncoder(config, name="encoder")
        self.layernorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layernorm")
        self.pooler = TFDeiTPooler(config, name="pooler") if add_pooling_layer else None
    def get_input_embeddings(self) -> TFDeiTPatchEmbeddings: return self.embeddings.patch_embeddings
    def _prune_heads(self, heads_to_prune): raise NotImplementedError
    def get_head_mask(self, head_mask):
        if head_mask is not None: raise NotImplementedError
        else: head_mask = [None] * self.config.num_hidden_layers
        return head_mask
    @unpack_inputs
    def call(self, pixel_values: tf.Tensor | None = None, bool_masked_pos: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False, training: bool = False) -> Union[TFBaseModelOutputWithPooling, Tuple[tf.Tensor, ...]]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        pixel_values = tf.transpose(pixel_values, (0, 2, 3, 1))
        head_mask = self.get_head_mask(head_mask)
        embedding_output = self.embeddings(pixel_values, bool_masked_pos=bool_masked_pos, training=training, interpolate_pos_encoding=interpolate_pos_encoding)
        encoder_outputs = self.encoder(embedding_output, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        sequence_output = encoder_outputs[0]
        sequence_output = self.layernorm(sequence_output, training=training)
        pooled_output = self.pooler(sequence_output, training=training) if self.pooler is not None else None
        if not return_dict:
            head_outputs = (sequence_output, pooled_output) if pooled_output is not None else (sequence_output,)
            return head_outputs + encoder_outputs[1:]
        return TFBaseModelOutputWithPooling(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name): self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name): self.encoder.build(None)
        if getattr(self, "layernorm", None) is not None:
            with tf.name_scope(self.layernorm.name): self.layernorm.build([None, None, self.config.hidden_size])
        if getattr(self, "pooler", None) is not None:
            with tf.name_scope(self.pooler.name): self.pooler.build(None)
class TFDeiTPreTrainedModel(TFPreTrainedModel):
    config_class = DeiTConfig
    base_model_prefix = "deit"
    main_input_name = "pixel_values"
DEIT_START_DOCSTRING = r"""
    This model is a TensorFlow
    [keras.layers.Layer](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Layer). Use it as a regular
    TensorFlow Module and refer to the TensorFlow documentation for all matter related to general usage and behavior.
    Parameters:
        config ([`DeiTConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
DEIT_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`tf.Tensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`DeiTImageProcessor.__call__`] for details.
        head_mask (`tf.Tensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        interpolate_pos_encoding (`bool`, *optional*, defaults to `False`):
            Whether to interpolate the pre-trained position encodings.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare DeiT Model transformer outputting raw hidden-states without any specific head on top.", DEIT_START_DOCSTRING)
class TFDeiTModel(TFDeiTPreTrainedModel):
    def __init__(self, config: DeiTConfig, add_pooling_layer: bool = True, use_mask_token: bool = False, **kwargs) -> None:
        super().__init__(config, **kwargs)
        self.deit = TFDeiTMainLayer(config, add_pooling_layer=add_pooling_layer, use_mask_token=use_mask_token, name="deit")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(DEIT_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor | None = None, bool_masked_pos: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False, training: bool = False) -> Union[Tuple, TFBaseModelOutputWithPooling]:
        outputs = self.deit(pixel_values=pixel_values, bool_masked_pos=bool_masked_pos, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states,
        return_dict=return_dict, interpolate_pos_encoding=interpolate_pos_encoding, training=training)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "deit", None) is not None:
            with tf.name_scope(self.deit.name): self.deit.build(None)
class TFDeiTPooler(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs):
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
class TFDeitPixelShuffle(keras.layers.Layer):
    def __init__(self, upscale_factor: int, **kwargs) -> None:
        super().__init__(**kwargs)
        if not isinstance(upscale_factor, int) or upscale_factor < 2: raise ValueError(f"upscale_factor must be an integer value >= 2 got {upscale_factor}")
        self.upscale_factor = upscale_factor
    def call(self, x: tf.Tensor) -> tf.Tensor:
        hidden_states = x
        batch_size, _, _, num_input_channels = shape_list(hidden_states)
        block_size_squared = self.upscale_factor**2
        output_depth = int(num_input_channels / block_size_squared)
        permutation = tf.constant([[i + j * block_size_squared for i in range(block_size_squared) for j in range(output_depth)]])
        hidden_states = tf.gather(params=hidden_states, indices=tf.tile(permutation, [batch_size, 1]), batch_dims=-1)
        hidden_states = tf.nn.depth_to_space(hidden_states, block_size=self.upscale_factor, data_format="NHWC")
        return hidden_states
class TFDeitDecoder(keras.layers.Layer):
    def __init__(self, config: DeiTConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.conv2d = keras.layers.Conv2D(filters=config.encoder_stride**2 * config.num_channels, kernel_size=1, name="0")
        self.pixel_shuffle = TFDeitPixelShuffle(config.encoder_stride, name="1")
        self.config = config
    def call(self, inputs: tf.Tensor, training: bool = False) -> tf.Tensor:
        hidden_states = inputs
        hidden_states = self.conv2d(hidden_states)
        hidden_states = self.pixel_shuffle(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "conv2d", None) is not None:
            with tf.name_scope(self.conv2d.name): self.conv2d.build([None, None, None, self.config.hidden_size])
        if getattr(self, "pixel_shuffle", None) is not None:
            with tf.name_scope(self.pixel_shuffle.name): self.pixel_shuffle.build(None)
@add_start_docstrings("DeiT Model with a decoder on top for masked image modeling, as proposed in [SimMIM](https://arxiv.org/abs/2111.09886).", DEIT_START_DOCSTRING)
class TFDeiTForMaskedImageModeling(TFDeiTPreTrainedModel):
    def __init__(self, config: DeiTConfig) -> None:
        super().__init__(config)
        self.deit = TFDeiTMainLayer(config, add_pooling_layer=False, use_mask_token=True, name="deit")
        self.decoder = TFDeitDecoder(config, name="decoder")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(DEIT_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor | None = None, bool_masked_pos: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False, training: bool = False) -> Union[tuple, TFMaskedImageModelingOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.deit(pixel_values, bool_masked_pos=bool_masked_pos, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict,
        interpolate_pos_encoding=interpolate_pos_encoding, training=training)
        sequence_output = outputs[0]
        sequence_output = sequence_output[:, 1:-1]
        batch_size, sequence_length, num_channels = shape_list(sequence_output)
        height = width = int(sequence_length**0.5)
        sequence_output = tf.reshape(sequence_output, (batch_size, height, width, num_channels))
        reconstructed_pixel_values = self.decoder(sequence_output, training=training)
        reconstructed_pixel_values = tf.transpose(reconstructed_pixel_values, (0, 3, 1, 2))
        masked_im_loss = None
        if bool_masked_pos is not None:
            size = self.config.image_size // self.config.patch_size
            bool_masked_pos = tf.reshape(bool_masked_pos, (-1, size, size))
            mask = tf.repeat(bool_masked_pos, self.config.patch_size, 1)
            mask = tf.repeat(mask, self.config.patch_size, 2)
            mask = tf.expand_dims(mask, 1)
            mask = tf.cast(mask, tf.float32)
            reconstruction_loss = keras.losses.mean_absolute_error(tf.transpose(pixel_values, (1, 2, 3, 0)), tf.transpose(reconstructed_pixel_values, (1, 2, 3, 0)))
            reconstruction_loss = tf.expand_dims(reconstruction_loss, 0)
            total_loss = tf.reduce_sum(reconstruction_loss * mask)
            num_masked_pixels = (tf.reduce_sum(mask) + 1e-5) * self.config.num_channels
            masked_im_loss = total_loss / num_masked_pixels
            masked_im_loss = tf.reshape(masked_im_loss, (1,))
        if not return_dict:
            output = (reconstructed_pixel_values,) + outputs[1:]
            return ((masked_im_loss,) + output) if masked_im_loss is not None else output
        return TFMaskedImageModelingOutput(loss=masked_im_loss, reconstruction=reconstructed_pixel_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "deit", None) is not None:
            with tf.name_scope(self.deit.name): self.deit.build(None)
        if getattr(self, "decoder", None) is not None:
            with tf.name_scope(self.decoder.name): self.decoder.build(None)
@add_start_docstrings("DeiT Model transformer with an image classification head on top (a linear layer on top of the final hidden state of the [CLS] token) e.g. for ImageNet.", DEIT_START_DOCSTRING)
class TFDeiTForImageClassification(TFDeiTPreTrainedModel, TFSequenceClassificationLoss):
    def __init__(self, config: DeiTConfig):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.deit = TFDeiTMainLayer(config, add_pooling_layer=False, name="deit")
        self.classifier = (keras.layers.Dense(config.num_labels, name="classifier") if config.num_labels > 0 else keras.layers.Activation("linear", name="classifier"))
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(DEIT_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, labels: tf.Tensor | None = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False,
    training: bool = False) -> Union[tf.Tensor, TFImageClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.deit(pixel_values, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict,
        interpolate_pos_encoding=interpolate_pos_encoding, training=training)
        sequence_output = outputs[0]
        logits = self.classifier(sequence_output[:, 0, :])
        loss = None if labels is None else self.hf_compute_loss(labels, logits)
        if not return_dict:
            output = (logits,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return TFImageClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "deit", None) is not None:
            with tf.name_scope(self.deit.name): self.deit.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name): self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings("""
    DeiT Model transformer with image classification heads on top (a linear layer on top of the final hidden state of
    the [CLS] token and a linear layer on top of the final hidden state of the distillation token) e.g. for ImageNet.
    .. warning::
            This model supports inference-only. Fine-tuning with distillation (i.e. with a teacher) is not yet
            supported.
    """, DEIT_START_DOCSTRING)
class TFDeiTForImageClassificationWithTeacher(TFDeiTPreTrainedModel):
    def __init__(self, config: DeiTConfig) -> None:
        super().__init__(config)
        self.num_labels = config.num_labels
        self.deit = TFDeiTMainLayer(config, add_pooling_layer=False, name="deit")
        self.cls_classifier = (keras.layers.Dense(config.num_labels, name="cls_classifier") if config.num_labels > 0 else keras.layers.Activation("linear", name="cls_classifier"))
        self.distillation_classifier = (keras.layers.Dense(config.num_labels, name="distillation_classifier") if config.num_labels > 0 else keras.layers.Activation("linear", name="distillation_classifier"))
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(DEIT_INPUTS_DOCSTRING)
    def call(self, pixel_values: tf.Tensor | None = None, head_mask: tf.Tensor | None = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False, training: bool = False) -> Union[tuple, TFDeiTForImageClassificationWithTeacherOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.deit(pixel_values, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict,
        interpolate_pos_encoding=interpolate_pos_encoding, training=training)
        sequence_output = outputs[0]
        cls_logits = self.cls_classifier(sequence_output[:, 0, :])
        distillation_logits = self.distillation_classifier(sequence_output[:, 1, :])
        logits = (cls_logits + distillation_logits) / 2
        if not return_dict:
            output = (logits, cls_logits, distillation_logits) + outputs[1:]
            return output
        return TFDeiTForImageClassificationWithTeacherOutput(logits=logits, cls_logits=cls_logits, distillation_logits=distillation_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "deit", None) is not None:
            with tf.name_scope(self.deit.name): self.deit.build(None)
        if getattr(self, "cls_classifier", None) is not None:
            with tf.name_scope(self.cls_classifier.name): self.cls_classifier.build([None, None, self.config.hidden_size])
        if getattr(self, "distillation_classifier", None) is not None:
            with tf.name_scope(self.distillation_classifier.name): self.distillation_classifier.build([None, None, self.config.hidden_size])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
