'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import flax.linen as nn
import jax.numpy as jnp
import math
def get_sinusoidal_embeddings(timesteps: jnp.ndarray, embedding_dim: int, freq_shift: float=1, min_timescale: float=1, max_timescale: float=10000.0, flip_sin_to_cos: bool=False, scale: float=1.0) -> jnp.ndarray:
    """Returns:"""
    assert timesteps.ndim == 1, 'Timesteps should be a 1d-array'
    assert embedding_dim % 2 == 0, f'Embedding dimension {embedding_dim} should be even'
    num_timescales = float(embedding_dim // 2)
    log_timescale_increment = math.log(max_timescale / min_timescale) / (num_timescales - freq_shift)
    inv_timescales = min_timescale * jnp.exp(jnp.arange(num_timescales, dtype=jnp.float32) * -log_timescale_increment)
    emb = jnp.expand_dims(timesteps, 1) * jnp.expand_dims(inv_timescales, 0)
    scaled_time = scale * emb
    if flip_sin_to_cos: signal = jnp.concatenate([jnp.cos(scaled_time), jnp.sin(scaled_time)], axis=1)
    else: signal = jnp.concatenate([jnp.sin(scaled_time), jnp.cos(scaled_time)], axis=1)
    signal = jnp.reshape(signal, [jnp.shape(timesteps)[0], embedding_dim])
    return signal
class FlaxTimestepEmbedding(nn.Module):
    """Args:"""
    time_embed_dim: int = 32
    dtype: jnp.dtype = jnp.float32
    @nn.compact
    def __call__(self, temb):
        temb = nn.Dense(self.time_embed_dim, dtype=self.dtype, name='linear_1')(temb)
        temb = nn.silu(temb)
        temb = nn.Dense(self.time_embed_dim, dtype=self.dtype, name='linear_2')(temb)
        return temb
class FlaxTimesteps(nn.Module):
    """Args:"""
    dim: int = 32
    flip_sin_to_cos: bool = False
    freq_shift: float = 1
    @nn.compact
    def __call__(self, timesteps): return get_sinusoidal_embeddings(timesteps, embedding_dim=self.dim, flip_sin_to_cos=self.flip_sin_to_cos, freq_shift=self.freq_shift)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
