from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_outputs import (TFBaseModelOutputWithPastAndCrossAttentions, TFCausalLMOutputWithCrossAttentions, TFSequenceClassifierOutputWithPast)
from ...modeling_tf_utils import (TFCausalLanguageModelingLoss, TFConv1D, TFModelInputType, TFPreTrainedModel, TFSequenceClassificationLoss, TFSequenceSummary, get_initializer,
keras, keras_serializable, unpack_inputs)
from ...tf_utils import check_embeddings_within_bounds, shape_list, stable_softmax
from ...utils import (ModelOutput, add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_gpt2 import GPT2Config
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "openai-community/gpt2"
_CONFIG_FOR_DOC = "GPT2Config"
class TFAttention(keras.layers.Layer):
    def __init__(self, nx, config, scale=False, is_cross_attention=False, **kwargs):
        super().__init__(**kwargs)
        n_state = nx
        assert n_state % config.n_head == 0
        self.n_head = config.n_head
        self.split_size = n_state
        self.scale = scale
        self.output_attentions = config.output_attentions
        self.is_cross_attention = is_cross_attention
        if self.is_cross_attention:
            self.c_attn = TFConv1D(n_state * 2, nx, initializer_range=config.initializer_range, name="c_attn")
            self.q_attn = TFConv1D(n_state, nx, initializer_range=config.initializer_range, name="q_attn")
        else: self.c_attn = TFConv1D(n_state * 3, nx, initializer_range=config.initializer_range, name="c_attn")
        self.c_proj = TFConv1D(n_state, nx, initializer_range=config.initializer_range, name="c_proj")
        self.attn_dropout = keras.layers.Dropout(config.attn_pdrop)
        self.resid_dropout = keras.layers.Dropout(config.resid_pdrop)
        self.pruned_heads = set()
        self.embed_dim = n_state
    def prune_heads(self, heads): pass
    @staticmethod
    def causal_attention_mask(nd, ns, dtype):
        i = tf.range(nd)[:, None]
        j = tf.range(ns)
        m = i >= j - ns + nd
        return tf.cast(m, dtype)
    def _attn(self, q, k, v, attention_mask, head_mask, output_attentions, training=False):
        w = tf.matmul(q, k, transpose_b=True)
        if self.scale:
            dk = tf.cast(shape_list(k)[-1], dtype=w.dtype)
            w = w / tf.math.sqrt(dk)
        if not self.is_cross_attention:
            _, _, nd, ns = shape_list(w)
            b = self.causal_attention_mask(nd, ns, dtype=w.dtype)
            b = tf.reshape(b, [1, 1, nd, ns])
            w = w * b - 1e4 * (1 - b)
        if attention_mask is not None:
            attention_mask = tf.cast(attention_mask, dtype=w.dtype)
            w = w + attention_mask
        w = stable_softmax(w, axis=-1)
        w = self.attn_dropout(w, training=training)
        if head_mask is not None: w = w * head_mask
        outputs = [tf.matmul(w, v)]
        if output_attentions: outputs.append(w)
        return outputs
    def merge_heads(self, x):
        x = tf.transpose(x, [0, 2, 1, 3])
        x_shape = shape_list(x)
        new_x_shape = x_shape[:-2] + [x_shape[-2] * x_shape[-1]]
        return tf.reshape(x, new_x_shape)
    def split_heads(self, x):
        x_shape = shape_list(x)
        new_x_shape = x_shape[:-1] + [self.n_head, x_shape[-1] // self.n_head]
        x = tf.reshape(x, new_x_shape)
        return tf.transpose(x, (0, 2, 1, 3))
    def call(self, x, layer_past, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, use_cache, output_attentions, training=False):
        if encoder_hidden_states is not None:
            if not hasattr(self, "q_attn"): raise ValueError("If class is used as cross attention, the weights `q_attn` have to be defined. Please make sure to instantiate class with `GPT2Attention(..., is_cross_attention=True)`.")
            query = self.q_attn(x)
            kv_out = self.c_attn(encoder_hidden_states)
            key, value = tf.split(kv_out, 2, axis=2)
            attention_mask = encoder_attention_mask
        else:
            x = self.c_attn(x)
            query, key, value = tf.split(x, 3, axis=2)
        query = self.split_heads(query)
        key = self.split_heads(key)
        value = self.split_heads(value)
        if layer_past is not None:
            past_key, past_value = tf.unstack(layer_past, axis=0, num=2)
            key = tf.concat([past_key, key], axis=-2)
            value = tf.concat([past_value, value], axis=-2)
        if use_cache: present = tf.stack([key, value], axis=0)
        else: present = (None,)
        attn_outputs = self._attn(query, key, value, attention_mask, head_mask, output_attentions, training=training)
        a = attn_outputs[0]
        a = self.merge_heads(a)
        a = self.c_proj(a)
        a = self.resid_dropout(a, training=training)
        outputs = [a, present] + attn_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if self.is_cross_attention: c_attn_shape = 2 * self.embed_dim
        else: c_attn_shape = 3 * self.embed_dim
        if getattr(self, "c_proj", None) is not None:
            with tf.name_scope(self.c_proj.name): self.c_proj.build([None, None, self.embed_dim])
        if getattr(self, "c_attn", None) is not None:
            with tf.name_scope(self.c_attn.name): self.c_attn.build([None, None, c_attn_shape])
        if getattr(self, "q_attn", None) is not None:
            with tf.name_scope(self.q_attn.name): self.q_attn.build([None, None, self.embed_dim])
class TFMLP(keras.layers.Layer):
    def __init__(self, n_state, config, **kwargs):
        super().__init__(**kwargs)
        nx = config.n_embd
        self.c_fc = TFConv1D(n_state, nx, initializer_range=config.initializer_range, name="c_fc")
        self.c_proj = TFConv1D(nx, n_state, initializer_range=config.initializer_range, name="c_proj")
        self.act = get_tf_activation(config.activation_function)
        self.dropout = keras.layers.Dropout(config.resid_pdrop)
        self.intermediate_size = n_state
        self.embed_dim = nx
    def call(self, x, training=False):
        h = self.act(self.c_fc(x))
        h2 = self.c_proj(h)
        h2 = self.dropout(h2, training=training)
        return h2
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "c_fc", None) is not None:
            with tf.name_scope(self.c_fc.name): self.c_fc.build([None, None, self.intermediate_size])
        if getattr(self, "c_proj", None) is not None:
            with tf.name_scope(self.c_proj.name): self.c_proj.build([None, None, self.embed_dim])
class TFBlock(keras.layers.Layer):
    def __init__(self, config, scale=False, **kwargs):
        super().__init__(**kwargs)
        nx = config.n_embd
        inner_dim = config.n_inner if config.n_inner is not None else 4 * nx
        self.ln_1 = keras.layers.LayerNormalization(epsilon=config.layer_norm_epsilon, name="ln_1")
        self.attn = TFAttention(nx, config, scale, name="attn")
        self.ln_2 = keras.layers.LayerNormalization(epsilon=config.layer_norm_epsilon, name="ln_2")
        if config.add_cross_attention:
            self.crossattention = TFAttention(nx, config, scale, name="crossattention", is_cross_attention=True)
            self.ln_cross_attn = keras.layers.LayerNormalization(epsilon=config.layer_norm_epsilon, name="ln_cross_attn")
        self.mlp = TFMLP(inner_dim, config, name="mlp")
        self.hidden_size = config.hidden_size
    def call(self, x, layer_past, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, use_cache, output_attentions, training=False):
        a = self.ln_1(x)
        output_attn = self.attn(a, layer_past=layer_past, attention_mask=attention_mask, head_mask=head_mask, encoder_hidden_states=None, encoder_attention_mask=None,
        use_cache=use_cache, output_attentions=output_attentions, training=training)
        a = output_attn[0]
        outputs = output_attn[1:]
        x = x + a
        if encoder_hidden_states is not None:
            if not hasattr(self, "crossattention"): raise ValueError(f"If `encoder_hidden_states` are passed, {self} has to be instantiated with cross-attention layers by setting `config.add_cross_attention=True`")
            ca = self.ln_cross_attn(x)
            output_cross_attn = self.crossattention(ca, layer_past=None, attention_mask=attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask, use_cache=False, output_attentions=output_attentions, training=training)
            ca = output_cross_attn[0]
            x = x + ca
            outputs = outputs + output_cross_attn[2:]
        m = self.ln_2(x)
        m = self.mlp(m, training=training)
        x = x + m
        outputs = [x] + outputs
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "ln_1", None) is not None:
            with tf.name_scope(self.ln_1.name): self.ln_1.build([None, None, self.hidden_size])
        if getattr(self, "attn", None) is not None:
            with tf.name_scope(self.attn.name): self.attn.build(None)
        if getattr(self, "ln_2", None) is not None:
            with tf.name_scope(self.ln_2.name): self.ln_2.build([None, None, self.hidden_size])
        if getattr(self, "mlp", None) is not None:
            with tf.name_scope(self.mlp.name): self.mlp.build(None)
        if getattr(self, "crossattention", None) is not None:
            with tf.name_scope(self.crossattention.name): self.crossattention.build(None)
        if getattr(self, "ln_cross_attn", None) is not None:
            with tf.name_scope(self.ln_cross_attn.name): self.ln_cross_attn.build([None, None, self.hidden_size])
@keras_serializable
class TFGPT2MainLayer(keras.layers.Layer):
    config_class = GPT2Config
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(*inputs, **kwargs)
        self.config = config
        self.output_attentions = config.output_attentions
        self.output_hidden_states = config.output_hidden_states
        self.use_cache = config.use_cache
        self.return_dict = config.use_return_dict
        self.num_hidden_layers = config.n_layer
        self.n_embd = config.n_embd
        self.n_positions = config.n_positions
        self.initializer_range = config.initializer_range
        self.wte = keras.layers.Embedding(input_dim=config.vocab_size, output_dim=config.hidden_size, embeddings_initializer=get_initializer(config.initializer_range), name="wte")
        self.wpe = keras.layers.Embedding(input_dim=config.n_positions, output_dim=config.n_embd, embeddings_initializer=get_initializer(config.initializer_range), name="wpe")
        self.drop = keras.layers.Dropout(config.embd_pdrop)
        self.h = [TFBlock(config, scale=True, name=f"h_._{i}") for i in range(config.n_layer)]
        self.ln_f = keras.layers.LayerNormalization(epsilon=config.layer_norm_epsilon, name="ln_f")
        self.embed_dim = config.hidden_size
    def get_input_embeddings(self): return self.wte
    def set_input_embeddings(self, new_embeddings): self.wte = new_embeddings
    def _prune_heads(self, heads_to_prune): raise NotImplementedError
    @unpack_inputs
    def call(self, input_ids: TFModelInputType | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    token_type_ids: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None,
    encoder_hidden_states: np.ndarray | tf.Tensor | None = None, encoder_attention_mask: np.ndarray | tf.Tensor | None = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, training: Optional[bool] = False) -> Union[TFBaseModelOutputWithPastAndCrossAttentions, Tuple[tf.Tensor]]:
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
            input_ids = tf.reshape(input_ids, [-1, input_shape[-1]])
        elif inputs_embeds is not None: input_shape = shape_list(inputs_embeds)[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if past_key_values is None:
            past_length = 0
            past_key_values = [None] * len(self.h)
        else: past_length = shape_list(past_key_values[0][0])[-2]
        if position_ids is None: position_ids = tf.expand_dims(tf.range(past_length, input_shape[-1] + past_length), axis=0)
        if attention_mask is not None:
            attention_mask_shape = shape_list(attention_mask)
            attention_mask = tf.reshape(attention_mask, (attention_mask_shape[0], 1, 1, attention_mask_shape[1]))
            one_cst = tf.constant(1.0)
            attention_mask = tf.cast(attention_mask, dtype=one_cst.dtype)
            attention_mask = tf.multiply(tf.subtract(one_cst, attention_mask), tf.constant(-10000.0))
        if self.config.add_cross_attention and encoder_attention_mask is not None:
            encoder_attention_mask = tf.cast(encoder_attention_mask, dtype=encoder_hidden_states.dtype)
            num_dims_encoder_attention_mask = len(shape_list(encoder_attention_mask))
            if num_dims_encoder_attention_mask == 3: encoder_extended_attention_mask = encoder_attention_mask[:, None, :, :]
            if num_dims_encoder_attention_mask == 2: encoder_extended_attention_mask = encoder_attention_mask[:, None, None, :]
            encoder_extended_attention_mask = (1.0 - encoder_extended_attention_mask) * -10000.0
        else: encoder_extended_attention_mask = None
        encoder_attention_mask = encoder_extended_attention_mask
        if head_mask is not None: raise NotImplementedError
        else: head_mask = [None] * self.num_hidden_layers
        position_ids = tf.reshape(position_ids, [-1, shape_list(position_ids)[-1]])
        if inputs_embeds is None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = self.wte(input_ids)
        position_embeds = self.wpe(position_ids)
        if token_type_ids is not None:
            token_type_ids = tf.reshape(token_type_ids, [-1, shape_list(token_type_ids)[-1]])
            token_type_embeds = self.wte(token_type_ids)
        else: token_type_embeds = tf.constant(0.0)
        position_embeds = tf.cast(position_embeds, dtype=inputs_embeds.dtype)
        token_type_embeds = tf.cast(token_type_embeds, dtype=inputs_embeds.dtype)
        hidden_states = inputs_embeds + position_embeds + token_type_embeds
        hidden_states = self.drop(hidden_states, training=training)
        output_shape = input_shape + [shape_list(hidden_states)[-1]]
        presents = () if use_cache else None
        all_attentions = () if output_attentions else None
        all_cross_attentions = () if output_attentions and self.config.add_cross_attention else None
        all_hidden_states = () if output_hidden_states else None
        for i, (block, layer_past) in enumerate(zip(self.h, past_key_values)):
            if output_hidden_states: all_hidden_states = all_hidden_states + (tf.reshape(hidden_states, output_shape),)
            outputs = block(hidden_states, layer_past, attention_mask, head_mask[i], encoder_hidden_states, encoder_attention_mask, use_cache, output_attentions, training=training)
            hidden_states, present = outputs[:2]
            if use_cache: presents = presents + (present,)
            if output_attentions:
                all_attentions = all_attentions + (outputs[2],)
                if self.config.add_cross_attention and encoder_hidden_states is not None: all_cross_attentions = all_cross_attentions + (outputs[3],)
        hidden_states = self.ln_f(hidden_states)
        hidden_states = tf.reshape(hidden_states, output_shape)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if output_attentions:
            attention_output_shape = input_shape[:-1] + [-1] + shape_list(all_attentions[0])[-2:]
            all_attentions = tuple(tf.reshape(t, attention_output_shape) for t in all_attentions)
        if not return_dict: return tuple(v for v in [hidden_states, presents, all_hidden_states, all_attentions, all_cross_attentions] if v is not None)
        return TFBaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=presents, hidden_states=all_hidden_states, attentions=all_attentions, cross_attentions=all_cross_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "wte", None) is not None:
            with tf.name_scope(self.wte.name): self.wte.build(None)
        if getattr(self, "wpe", None) is not None:
            with tf.name_scope(self.wpe.name): self.wpe.build(None)
        if getattr(self, "ln_f", None) is not None:
            with tf.name_scope(self.ln_f.name): self.ln_f.build([None, None, self.embed_dim])
        if getattr(self, "h", None) is not None:
            for layer in self.h:
                with tf.name_scope(layer.name): layer.build(None)
class TFGPT2PreTrainedModel(TFPreTrainedModel):
    config_class = GPT2Config
    base_model_prefix = "transformer"
    _keys_to_ignore_on_load_unexpected = [r"h.\d+.attn.bias", r"h.\d+.crossattention.bias"]
    @property
    def input_signature(self): return {"input_ids": tf.TensorSpec((None, None), tf.int32, name="input_ids"), "attention_mask": tf.TensorSpec((None, None), tf.int32, name="attention_mask")}
@dataclass
class TFGPT2DoubleHeadsModelOutput(ModelOutput):
    """Args:"""
    logits: tf.Tensor = None
    mc_logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
GPT2_START_DOCSTRING = r"""
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
    Parameters:
        config ([`GPT2Config`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
GPT2_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`Numpy array` or `tf.Tensor` of shape `(batch_size, input_ids_length)`):
            `input_ids_length` = `sequence_length` if `past_key_values` is `None` else `past_key_values[0].shape[-2]`
            (`sequence_length` of input past key value states). Indices of input sequence tokens in the vocabulary.
            If `past_key_values` is used, only input IDs that do not have their past calculated should be passed as
            `input_ids`.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.__call__`] and
            [`PreTrainedTokenizer.encode`] for details.
            [What are input IDs?](../glossary#input-ids)
        past_key_values (`List[tf.Tensor]` of length `config.n_layers`):
            Contains pre-computed hidden-states (key and values in the attention blocks) as computed by the model (see
            `past_key_values` output below). Can be used to speed up sequential decoding. The token ids which have
            their past given to this model should not be passed as input ids as they have already been computed.
        attention_mask (`tf.Tensor` or `Numpy array` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            If `past_key_values` is used, `attention_mask` needs to contain the masking strategy that was used for
            `past_key_values`. In other words, the `attention_mask` always has to have the length:
            `len(past_key_values) + len(input_ids)`
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`tf.Tensor` or `Numpy array` of shape `(batch_size, sequence_length)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        position_ids (`tf.Tensor` or `Numpy array` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`Numpy array` or `tf.Tensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
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
@add_start_docstrings("The bare GPT2 Model transformer outputting raw hidden-states without any specific head on top.", GPT2_START_DOCSTRING)
class TFGPT2Model(TFGPT2PreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.transformer = TFGPT2MainLayer(config, name="transformer")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(GPT2_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    token_type_ids: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None,
    inputs_embeds: np.ndarray | tf.Tensor | None = None, encoder_hidden_states: np.ndarray | tf.Tensor | None = None, encoder_attention_mask: np.ndarray | tf.Tensor | None = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    training: Optional[bool] = False) -> Union[TFBaseModelOutputWithPastAndCrossAttentions, Tuple[tf.Tensor]]:
        outputs = self.transformer(input_ids=input_ids, past_key_values=past_key_values, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids,
        head_mask=head_mask, inputs_embeds=inputs_embeds, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        return outputs
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name): self.transformer.build(None)
@add_start_docstrings("The GPT2 Model transformer with a language modeling head on top (linear layer with weights tied to the input embeddings).", GPT2_START_DOCSTRING)
class TFGPT2LMHeadModel(TFGPT2PreTrainedModel, TFCausalLanguageModelingLoss):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.transformer = TFGPT2MainLayer(config, name="transformer")
    def get_output_embeddings(self): return self.get_input_embeddings()
    def set_output_embeddings(self, value): self.set_input_embeddings(value)
    def prepare_inputs_for_generation(self, inputs, past_key_values=None, use_cache=None, **kwargs):
        token_type_ids = kwargs.get("token_type_ids", None)
        if past_key_values:
            inputs = tf.expand_dims(inputs[:, -1], -1)
            if token_type_ids is not None: token_type_ids = tf.expand_dims(token_type_ids[:, -1], -1)
        position_ids = kwargs.get("position_ids", None)
        attention_mask = kwargs.get("attention_mask", None)
        if attention_mask is not None and position_ids is None:
            position_ids = tf.math.cumsum(attention_mask, axis=-1, exclusive=True)
            if past_key_values: position_ids = tf.expand_dims(position_ids[:, -1], -1)
        return {"input_ids": inputs, "attention_mask": attention_mask, "position_ids": position_ids, "past_key_values": past_key_values, "use_cache": use_cache, "token_type_ids": token_type_ids}
    @unpack_inputs
    @add_start_docstrings_to_model_forward(GPT2_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    token_type_ids: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None,
    encoder_hidden_states: np.ndarray | tf.Tensor | None = None, encoder_attention_mask: np.ndarray | tf.Tensor | None = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: np.ndarray | tf.Tensor | None = None, training: Optional[bool] = False) -> Union[TFCausalLMOutputWithCrossAttentions, Tuple[tf.Tensor]]:
        transformer_outputs = self.transformer(input_ids=input_ids, past_key_values=past_key_values, attention_mask=attention_mask, token_type_ids=token_type_ids,
        position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        hidden_states = transformer_outputs[0]
        logits = tf.matmul(hidden_states, self.transformer.wte.weights, transpose_b=True)
        loss = None
        if labels is not None:
            shifted_logits = logits[:, :-1]
            labels = labels[:, 1:]
            loss = self.hf_compute_loss(labels, shifted_logits)
        if not return_dict:
            output = (logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return TFCausalLMOutputWithCrossAttentions(loss=loss, logits=logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states,
        attentions=transformer_outputs.attentions, cross_attentions=transformer_outputs.cross_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name): self.transformer.build(None)
@add_start_docstrings("""
    The GPT2 Model transformer with a language modeling and a multiple-choice classification head on top e.g. for
    RocStories/SWAG tasks. The two heads are two linear layers. The language modeling head has its weights tied to the
    input embeddings, the classification head takes as input the input of a specified classification token index in the
    input sequence).
    """, GPT2_START_DOCSTRING)
class TFGPT2DoubleHeadsModel(TFGPT2PreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        config.num_labels = 1
        self.transformer = TFGPT2MainLayer(config, name="transformer")
        self.multiple_choice_head = TFSequenceSummary(config, initializer_range=config.initializer_range, name="multiple_choice_head")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(GPT2_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    token_type_ids: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None,
    mc_token_ids: np.ndarray | tf.Tensor | None = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, training: Optional[bool] = False) -> Union[TFGPT2DoubleHeadsModelOutput, Tuple[tf.Tensor]]:
        if input_ids is not None: input_shapes = shape_list(input_ids)
        else: input_shapes = shape_list(inputs_embeds)[:-1]
        seq_length = input_shapes[-1]
        flat_input_ids = tf.reshape(input_ids, (-1, seq_length)) if input_ids is not None else None
        flat_attention_mask = tf.reshape(attention_mask, (-1, seq_length)) if attention_mask is not None else None
        flat_token_type_ids = tf.reshape(token_type_ids, (-1, seq_length)) if token_type_ids is not None else None
        flat_position_ids = tf.reshape(position_ids, (-1, seq_length)) if position_ids is not None else None
        transformer_outputs = self.transformer(input_ids=flat_input_ids, past_key_values=past_key_values, attention_mask=flat_attention_mask, token_type_ids=flat_token_type_ids,
        position_ids=flat_position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, encoder_hidden_states=None, encoder_attention_mask=None, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        hidden_states = transformer_outputs[0]
        hidden_states = tf.reshape(hidden_states, input_shapes + shape_list(hidden_states)[-1:])
        if return_dict and output_hidden_states: all_hidden_states = transformer_outputs.hidden_states[:-1] + (hidden_states,)
        else: all_hidden_states = None
        lm_logits = tf.matmul(hidden_states, self.transformer.wte.weights, transpose_b=True)
        mc_logits = self.multiple_choice_head(hidden_states, mc_token_ids, training=training)
        mc_logits = tf.squeeze(mc_logits, axis=-1)
        if not return_dict: return (lm_logits, mc_logits) + transformer_outputs[1:]
        return TFGPT2DoubleHeadsModelOutput(logits=lm_logits, mc_logits=mc_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=all_hidden_states, attentions=transformer_outputs.attentions)
    @property
    def input_signature(self): return {"input_ids": tf.TensorSpec((None, None, None), tf.int32, name="input_ids"), "attention_mask": tf.TensorSpec((None, None, None), tf.int32, name="attention_mask"), "mc_token_ids": tf.TensorSpec((None, None), tf.int32, name="mc_token_ids")}
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name): self.transformer.build(None)
        if getattr(self, "multiple_choice_head", None) is not None:
            with tf.name_scope(self.multiple_choice_head.name): self.multiple_choice_head.build(None)
@add_start_docstrings("""
    The GPT2 Model transformer with a sequence classification head on top (linear layer).
    [`TFGPT2ForSequenceClassification`] uses the last token in order to do the classification, as other causal models
    (e.g. GPT-1) do.
    Since it does classification on the last token, it requires to know the position of the last token. If a
    `pad_token_id` is defined in the configuration, it finds the last token that is not a padding token in each row. If
    no `pad_token_id` is defined, it simply takes the last value in each row of the batch. Since it cannot guess the
    padding tokens when `inputs_embeds` are passed instead of `input_ids`, it does the same (take the last value in
    each row of the batch).
    """, GPT2_START_DOCSTRING)
class TFGPT2ForSequenceClassification(TFGPT2PreTrainedModel, TFSequenceClassificationLoss):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.score = keras.layers.Dense(config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="score", use_bias=False)
        self.transformer = TFGPT2MainLayer(config, name="transformer")
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(GPT2_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None, attention_mask: np.ndarray | tf.Tensor | None = None,
    token_type_ids: np.ndarray | tf.Tensor | None = None, position_ids: np.ndarray | tf.Tensor | None = None, head_mask: np.ndarray | tf.Tensor | None = None, inputs_embeds: np.ndarray | tf.Tensor | None = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    labels: np.ndarray | tf.Tensor | None = None, training: Optional[bool] = False) -> Union[TFSequenceClassifierOutputWithPast, Tuple[tf.Tensor]]:
        transformer_outputs = self.transformer(input_ids=input_ids, past_key_values=past_key_values, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids,
        head_mask=head_mask, inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, training=training)
        hidden_states = transformer_outputs[0]
        logits = self.score(hidden_states)
        logits_shape = shape_list(logits)
        in_logits = None
        if self.config.pad_token_id is None: sequence_lengths = -1
        else:
            if input_ids is not None:
                sequence_lengths = (tf.argmax(tf.cast(tf.math.equal(input_ids, self.config.pad_token_id), input_ids.dtype), axis=-1) - 1)
                sequence_lengths = tf.where(sequence_lengths >= 0, sequence_lengths, input_ids.shape[-1] - 1)
                in_logits = tf.gather(logits, sequence_lengths, batch_dims=1, axis=1)
            else:
                sequence_lengths = -1
                logger.warning_once(f"{self.__class__.__name__} will not detect padding tokens in `inputs_embeds`. Results may be unexpected if using padding tokens in conjunction with `inputs_embeds.`")
        loss = None
        if labels is not None:
            assert (self.config.pad_token_id is not None or logits_shape[0] == 1), "Cannot handle batch sizes > 1 if no padding token is defined."
            if not tf.is_tensor(sequence_lengths): in_logits = logits[0 : logits_shape[0], sequence_lengths]
            loss = self.hf_compute_loss(tf.reshape(labels, [-1]), tf.reshape(in_logits, [-1, self.num_labels]))
        pooled_logits = in_logits if in_logits is not None else logits
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutputWithPast(loss=loss, logits=pooled_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states, attentions=transformer_outputs.attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "score", None) is not None:
            with tf.name_scope(self.score.name): self.score.build([None, None, self.config.n_embd])
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name): self.transformer.build(None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
