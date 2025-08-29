"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Tuple
import tensorflow as tf
from ...modeling_tf_utils import shape_list
from .configuration_idefics import IdeficsConfig
class TFIdeficsPerceiverResampler(tf.keras.layers.Layer):
    def __init__(self, config: IdeficsConfig, embed_dim: int, depth: int, n_heads: int, head_dim: int, n_latents: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.embed_dim, self.n_heads, self.head_dim, self.n_latents = embed_dim, n_heads, head_dim, n_latents
        self.qk_layer_norms = config.perceiver_config.qk_layer_norms_perceiver
        self.intermediate_dim = (self.embed_dim * 4 if not hasattr(config.vision_config, "embed_dim") else config.vision_config.embed_dim * 4)
        self.blocks = []
        for i in range(depth): self.blocks.append([TFIdeficsPerceiverAttention(self.embed_dim, self.n_heads, self.head_dim, self.qk_layer_norms, name=f"blocks.{i}.0"), TFIdeficsMLP(self.intermediate_dim, config, name=f"blocks.{i}.1")])
        self.layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="layer_norm")
    def build(self, input_shape):
        self.latents = self.add_weight(shape=(self.n_latents, self.embed_dim), initializer="random_normal", trainable=True, name="latents")
        super().build(input_shape)
    def call(self, context: tf.Tensor) -> tf.Tensor:
        latents = tf.expand_dims(self.latents, axis=0)
        latents = tf.tile(latents, [tf.shape(context)[0], 1, 1])
        for attn, ff in self.blocks:
            latents = attn(context, latents) + latents
            latents = ff(latents) + latents
        return self.layer_norm(latents)
class TFIdeficsPerceiverAttention(tf.keras.layers.Layer):
    def __init__(self, embed_dim: int, n_heads: int, head_dim: int, qk_layer_norms: bool, **kwargs) -> None:
        super().__init__(**kwargs)
        self.embed_dim, self.n_heads, self.head_dim = embed_dim, n_heads, head_dim
        self.qk_layer_norms = qk_layer_norms
        self.context_layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="context_layer_norm")
        self.latents_layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="latents_layer_norm")
        if self.qk_layer_norms:
            self.q_layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="q_layer_norm")
            self.k_layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="k_layer_norm")
        self.qk_scale = self.head_dim**-0.5
        self.q_proj = tf.keras.layers.Dense(self.n_heads * self.head_dim, use_bias=False, name="q_proj")
        self.k_proj = tf.keras.layers.Dense(self.n_heads * self.head_dim, use_bias=False, name="k_proj")
        self.v_proj = tf.keras.layers.Dense(self.n_heads * self.head_dim, use_bias=False, name="v_proj")
        self.output_proj = tf.keras.layers.Dense(embed_dim, use_bias=False, name="output_proj")
    def call(self, context: tf.Tensor, latents: tf.Tensor) -> tf.Tensor:
        context = self.context_layer_norm(context)
        latents = self.latents_layer_norm(latents)
        batch_size, seq_length, embed_dim = shape_list(context)
        q = self.q_proj(latents)
        k = self.k_proj(tf.concat([context, latents], axis=-2))
        v = self.v_proj(tf.concat([context, latents], axis=-2))
        q, k, v = [tf.transpose(tf.reshape(x, (batch_size, x.shape[1], self.n_heads, self.head_dim)), perm=[0, 2, 1, 3]) for x in (q, k, v)]
        if self.qk_layer_norms:
            q = self.q_layer_norm(q)
            k = self.k_layer_norm(k)
        scores = tf.einsum("... i d, ... j d -> ... i j", q * self.qk_scale, k)
        stabilized_scores = scores - tf.reduce_max(scores, axis=-1, keepdims=True)
        attn = tf.nn.softmax(stabilized_scores, axis=-1)
        resampled = tf.einsum("... i j, ... j d -> ... i d", attn, v)
        return self.output_proj(tf.reshape(tf.transpose(resampled, perm=[0, 2, 1, 3]), (batch_size, -1, self.n_heads * self.head_dim)))
class TFIdeficsMLP(tf.keras.layers.Layer):
    def __init__(self, intermediate_size, config: IdeficsConfig, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = config.vision_config.embed_dim
        self.ln = tf.keras.layers.LayerNormalization(epsilon=1e-5, name="ln")
        self.fc = tf.keras.layers.Dense(intermediate_size, use_bias=False, name="fc")
        self.act = tf.keras.layers.ReLU(name="act")
        self.c_proj = tf.keras.layers.Dense(self.embed_dim, use_bias=False, name="c_proj")
    def call(self, hidden_states: Optional[Tuple[tf.Tensor]]) -> tf.Tensor:
        hidden_states = self.ln(hidden_states)
        hidden_states = self.fc(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.c_proj(hidden_states)
        return hidden_states
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
