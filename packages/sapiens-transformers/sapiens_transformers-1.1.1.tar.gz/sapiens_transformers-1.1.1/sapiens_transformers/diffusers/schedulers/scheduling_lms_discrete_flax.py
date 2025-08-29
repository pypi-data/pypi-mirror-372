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
from scipy import integrate
from ..configuration_utils import ConfigMixin, register_to_config
from .scheduling_utils_flax import CommonSchedulerState, FlaxKarrasDiffusionSchedulers, FlaxSchedulerMixin, FlaxSchedulerOutput, broadcast_to_shape_from_left
@flax.struct.dataclass
class LMSDiscreteSchedulerState:
    common: CommonSchedulerState
    init_noise_sigma: jnp.ndarray
    timesteps: jnp.ndarray
    sigmas: jnp.ndarray
    num_inference_steps: Optional[int] = None
    derivatives: Optional[jnp.ndarray] = None
    @classmethod
    def create(cls, common: CommonSchedulerState, init_noise_sigma: jnp.ndarray, timesteps: jnp.ndarray, sigmas: jnp.ndarray): return cls(common=common,
    init_noise_sigma=init_noise_sigma, timesteps=timesteps, sigmas=sigmas)
@dataclass
class FlaxLMSSchedulerOutput(FlaxSchedulerOutput):
    state: LMSDiscreteSchedulerState
class FlaxLMSDiscreteScheduler(FlaxSchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in FlaxKarrasDiffusionSchedulers]
    dtype: jnp.dtype
    @property
    def has_state(self): return True
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[jnp.ndarray]=None,
    prediction_type: str='epsilon', dtype: jnp.dtype=jnp.float32): self.dtype = dtype
    def create_state(self, common: Optional[CommonSchedulerState]=None) -> LMSDiscreteSchedulerState:
        if common is None: common = CommonSchedulerState.create(self)
        timesteps = jnp.arange(0, self.config.num_train_timesteps).round()[::-1]
        sigmas = ((1 - common.alphas_cumprod) / common.alphas_cumprod) ** 0.5
        init_noise_sigma = sigmas.max()
        return LMSDiscreteSchedulerState.create(common=common, init_noise_sigma=init_noise_sigma, timesteps=timesteps, sigmas=sigmas)
    def scale_model_input(self, state: LMSDiscreteSchedulerState, sample: jnp.ndarray, timestep: int) -> jnp.ndarray:
        """Returns:"""
        step_index, = jnp.where(state.timesteps == timestep, size=1)
        step_index = step_index[0]
        sigma = state.sigmas[step_index]
        sample = sample / (sigma ** 2 + 1) ** 0.5
        return sample
    def get_lms_coefficient(self, state: LMSDiscreteSchedulerState, order, t, current_order):
        """Args:"""
        def lms_derivative(tau):
            prod = 1.0
            for k in range(order):
                if current_order == k: continue
                prod *= (tau - state.sigmas[t - k]) / (state.sigmas[t - current_order] - state.sigmas[t - k])
            return prod
        integrated_coeff = integrate.quad(lms_derivative, state.sigmas[t], state.sigmas[t + 1], epsrel=0.0001)[0]
        return integrated_coeff
    def set_timesteps(self, state: LMSDiscreteSchedulerState, num_inference_steps: int, shape: Tuple=()) -> LMSDiscreteSchedulerState:
        """Args:"""
        timesteps = jnp.linspace(self.config.num_train_timesteps - 1, 0, num_inference_steps, dtype=self.dtype)
        low_idx = jnp.floor(timesteps).astype(jnp.int32)
        high_idx = jnp.ceil(timesteps).astype(jnp.int32)
        frac = jnp.mod(timesteps, 1.0)
        sigmas = ((1 - state.common.alphas_cumprod) / state.common.alphas_cumprod) ** 0.5
        sigmas = (1 - frac) * sigmas[low_idx] + frac * sigmas[high_idx]
        sigmas = jnp.concatenate([sigmas, jnp.array([0.0], dtype=self.dtype)])
        timesteps = timesteps.astype(jnp.int32)
        derivatives = jnp.zeros((0,) + shape, dtype=self.dtype)
        return state.replace(timesteps=timesteps, sigmas=sigmas, num_inference_steps=num_inference_steps, derivatives=derivatives)
    def step(self, state: LMSDiscreteSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray, order: int=4, return_dict: bool=True) -> Union[FlaxLMSSchedulerOutput, Tuple]:
        """Returns:"""
        if state.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        sigma = state.sigmas[timestep]
        if self.config.prediction_type == 'epsilon': pred_original_sample = sample - sigma * model_output
        elif self.config.prediction_type == 'v_prediction': pred_original_sample = model_output * (-sigma / (sigma ** 2 + 1) ** 0.5) + sample / (sigma ** 2 + 1)
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, or `v_prediction`')
        derivative = (sample - pred_original_sample) / sigma
        state = state.replace(derivatives=jnp.append(state.derivatives, derivative))
        if len(state.derivatives) > order: state = state.replace(derivatives=jnp.delete(state.derivatives, 0))
        order = min(timestep + 1, order)
        lms_coeffs = [self.get_lms_coefficient(state, order, timestep, curr_order) for curr_order in range(order)]
        prev_sample = sample + sum((coeff * derivative for coeff, derivative in zip(lms_coeffs, reversed(state.derivatives))))
        if not return_dict: return (prev_sample, state)
        return FlaxLMSSchedulerOutput(prev_sample=prev_sample, state=state)
    def add_noise(self, state: LMSDiscreteSchedulerState, original_samples: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray:
        sigma = state.sigmas[timesteps].flatten()
        sigma = broadcast_to_shape_from_left(sigma, noise.shape)
        noisy_samples = original_samples + noise * sigma
        return noisy_samples
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
