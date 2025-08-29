'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import flax
import jax.numpy as jnp
from ..configuration_utils import ConfigMixin, register_to_config
from .scheduling_utils_flax import CommonSchedulerState, FlaxKarrasDiffusionSchedulers, FlaxSchedulerMixin, FlaxSchedulerOutput, add_noise_common, get_velocity_common
@flax.struct.dataclass
class DDIMSchedulerState:
    common: CommonSchedulerState
    final_alpha_cumprod: jnp.ndarray
    init_noise_sigma: jnp.ndarray
    timesteps: jnp.ndarray
    num_inference_steps: Optional[int] = None
    @classmethod
    def create(cls, common: CommonSchedulerState, final_alpha_cumprod: jnp.ndarray, init_noise_sigma: jnp.ndarray, timesteps: jnp.ndarray): return cls(common=common,
    final_alpha_cumprod=final_alpha_cumprod, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
@dataclass
class FlaxDDIMSchedulerOutput(FlaxSchedulerOutput):
    state: DDIMSchedulerState
class FlaxDDIMScheduler(FlaxSchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in FlaxKarrasDiffusionSchedulers]
    dtype: jnp.dtype
    @property
    def has_state(self): return True
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[jnp.ndarray]=None,
    clip_sample: bool=True, clip_sample_range: float=1.0, set_alpha_to_one: bool=True, steps_offset: int=0, prediction_type: str='epsilon', dtype: jnp.dtype=jnp.float32): self.dtype = dtype
    def create_state(self, common: Optional[CommonSchedulerState]=None) -> DDIMSchedulerState:
        if common is None: common = CommonSchedulerState.create(self)
        final_alpha_cumprod = jnp.array(1.0, dtype=self.dtype) if self.config.set_alpha_to_one else common.alphas_cumprod[0]
        init_noise_sigma = jnp.array(1.0, dtype=self.dtype)
        timesteps = jnp.arange(0, self.config.num_train_timesteps).round()[::-1]
        return DDIMSchedulerState.create(common=common, final_alpha_cumprod=final_alpha_cumprod, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
    def scale_model_input(self, state: DDIMSchedulerState, sample: jnp.ndarray, timestep: Optional[int]=None) -> jnp.ndarray:
        """Returns:"""
        return sample
    def set_timesteps(self, state: DDIMSchedulerState, num_inference_steps: int, shape: Tuple=()) -> DDIMSchedulerState:
        """Args:"""
        step_ratio = self.config.num_train_timesteps // num_inference_steps
        timesteps = (jnp.arange(0, num_inference_steps) * step_ratio).round()[::-1] + self.config.steps_offset
        return state.replace(num_inference_steps=num_inference_steps, timesteps=timesteps)
    def _get_variance(self, state: DDIMSchedulerState, timestep, prev_timestep):
        alpha_prod_t = state.common.alphas_cumprod[timestep]
        alpha_prod_t_prev = jnp.where(prev_timestep >= 0, state.common.alphas_cumprod[prev_timestep], state.final_alpha_cumprod)
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        variance = beta_prod_t_prev / beta_prod_t * (1 - alpha_prod_t / alpha_prod_t_prev)
        return variance
    def step(self, state: DDIMSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray, eta: float=0.0, return_dict: bool=True) -> Union[FlaxDDIMSchedulerOutput, Tuple]:
        """Returns:"""
        if state.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        prev_timestep = timestep - self.config.num_train_timesteps // state.num_inference_steps
        alphas_cumprod = state.common.alphas_cumprod
        final_alpha_cumprod = state.final_alpha_cumprod
        alpha_prod_t = alphas_cumprod[timestep]
        alpha_prod_t_prev = jnp.where(prev_timestep >= 0, alphas_cumprod[prev_timestep], final_alpha_cumprod)
        beta_prod_t = 1 - alpha_prod_t
        if self.config.prediction_type == 'epsilon':
            pred_original_sample = (sample - beta_prod_t ** 0.5 * model_output) / alpha_prod_t ** 0.5
            pred_epsilon = model_output
        elif self.config.prediction_type == 'sample':
            pred_original_sample = model_output
            pred_epsilon = (sample - alpha_prod_t ** 0.5 * pred_original_sample) / beta_prod_t ** 0.5
        elif self.config.prediction_type == 'v_prediction':
            pred_original_sample = alpha_prod_t ** 0.5 * sample - beta_prod_t ** 0.5 * model_output
            pred_epsilon = alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, or `v_prediction`')
        if self.config.clip_sample: pred_original_sample = pred_original_sample.clip(-self.config.clip_sample_range, self.config.clip_sample_range)
        variance = self._get_variance(state, timestep, prev_timestep)
        std_dev_t = eta * variance ** 0.5
        pred_sample_direction = (1 - alpha_prod_t_prev - std_dev_t ** 2) ** 0.5 * pred_epsilon
        prev_sample = alpha_prod_t_prev ** 0.5 * pred_original_sample + pred_sample_direction
        if not return_dict: return (prev_sample, state)
        return FlaxDDIMSchedulerOutput(prev_sample=prev_sample, state=state)
    def add_noise(self, state: DDIMSchedulerState, original_samples: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray: return add_noise_common(state.common, original_samples, noise, timesteps)
    def get_velocity(self, state: DDIMSchedulerState, sample: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray: return get_velocity_common(state.common, sample, noise, timesteps)
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
