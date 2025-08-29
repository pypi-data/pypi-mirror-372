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
import jax
import jax.numpy as jnp
from ..configuration_utils import ConfigMixin, register_to_config
from .scheduling_utils_flax import CommonSchedulerState, FlaxKarrasDiffusionSchedulers, FlaxSchedulerMixin, FlaxSchedulerOutput, add_noise_common
@flax.struct.dataclass
class PNDMSchedulerState:
    common: CommonSchedulerState
    final_alpha_cumprod: jnp.ndarray
    init_noise_sigma: jnp.ndarray
    timesteps: jnp.ndarray
    num_inference_steps: Optional[int] = None
    prk_timesteps: Optional[jnp.ndarray] = None
    plms_timesteps: Optional[jnp.ndarray] = None
    cur_model_output: Optional[jnp.ndarray] = None
    counter: Optional[jnp.int32] = None
    cur_sample: Optional[jnp.ndarray] = None
    ets: Optional[jnp.ndarray] = None
    @classmethod
    def create(cls, common: CommonSchedulerState, final_alpha_cumprod: jnp.ndarray, init_noise_sigma: jnp.ndarray, timesteps: jnp.ndarray): return cls(common=common,
    final_alpha_cumprod=final_alpha_cumprod, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
@dataclass
class FlaxPNDMSchedulerOutput(FlaxSchedulerOutput):
    state: PNDMSchedulerState
class FlaxPNDMScheduler(FlaxSchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in FlaxKarrasDiffusionSchedulers]
    dtype: jnp.dtype
    pndm_order: int
    @property
    def has_state(self): return True
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[jnp.ndarray]=None,
    skip_prk_steps: bool=False, set_alpha_to_one: bool=False, steps_offset: int=0, prediction_type: str='epsilon', dtype: jnp.dtype=jnp.float32):
        self.dtype = dtype
        self.pndm_order = 4
    def create_state(self, common: Optional[CommonSchedulerState]=None) -> PNDMSchedulerState:
        if common is None: common = CommonSchedulerState.create(self)
        final_alpha_cumprod = jnp.array(1.0, dtype=self.dtype) if self.config.set_alpha_to_one else common.alphas_cumprod[0]
        init_noise_sigma = jnp.array(1.0, dtype=self.dtype)
        timesteps = jnp.arange(0, self.config.num_train_timesteps).round()[::-1]
        return PNDMSchedulerState.create(common=common, final_alpha_cumprod=final_alpha_cumprod, init_noise_sigma=init_noise_sigma, timesteps=timesteps)
    def set_timesteps(self, state: PNDMSchedulerState, num_inference_steps: int, shape: Tuple) -> PNDMSchedulerState:
        """Args:"""
        step_ratio = self.config.num_train_timesteps // num_inference_steps
        _timesteps = (jnp.arange(0, num_inference_steps) * step_ratio).round() + self.config.steps_offset
        if self.config.skip_prk_steps:
            prk_timesteps = jnp.array([], dtype=jnp.int32)
            plms_timesteps = jnp.concatenate([_timesteps[:-1], _timesteps[-2:-1], _timesteps[-1:]])[::-1]
        else:
            prk_timesteps = _timesteps[-self.pndm_order:].repeat(2) + jnp.tile(jnp.array([0, self.config.num_train_timesteps // num_inference_steps // 2], dtype=jnp.int32), self.pndm_order)
            prk_timesteps = prk_timesteps[:-1].repeat(2)[1:-1][::-1]
            plms_timesteps = _timesteps[:-3][::-1]
        timesteps = jnp.concatenate([prk_timesteps, plms_timesteps])
        cur_model_output = jnp.zeros(shape, dtype=self.dtype)
        counter = jnp.int32(0)
        cur_sample = jnp.zeros(shape, dtype=self.dtype)
        ets = jnp.zeros((4,) + shape, dtype=self.dtype)
        return state.replace(timesteps=timesteps, num_inference_steps=num_inference_steps, prk_timesteps=prk_timesteps, plms_timesteps=plms_timesteps, cur_model_output=cur_model_output,
        counter=counter, cur_sample=cur_sample, ets=ets)
    def scale_model_input(self, state: PNDMSchedulerState, sample: jnp.ndarray, timestep: Optional[int]=None) -> jnp.ndarray:
        """Returns:"""
        return sample
    def step(self, state: PNDMSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray, return_dict: bool=True) -> Union[FlaxPNDMSchedulerOutput, Tuple]:
        """Returns:"""
        if state.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.config.skip_prk_steps: prev_sample, state = self.step_plms(state, model_output, timestep, sample)
        else:
            prk_prev_sample, prk_state = self.step_prk(state, model_output, timestep, sample)
            plms_prev_sample, plms_state = self.step_plms(state, model_output, timestep, sample)
            cond = state.counter < len(state.prk_timesteps)
            prev_sample = jax.lax.select(cond, prk_prev_sample, plms_prev_sample)
            state = state.replace(cur_model_output=jax.lax.select(cond, prk_state.cur_model_output, plms_state.cur_model_output), ets=jax.lax.select(cond, prk_state.ets, plms_state.ets),
            cur_sample=jax.lax.select(cond, prk_state.cur_sample, plms_state.cur_sample), counter=jax.lax.select(cond, prk_state.counter, plms_state.counter))
        if not return_dict: return (prev_sample, state)
        return FlaxPNDMSchedulerOutput(prev_sample=prev_sample, state=state)
    def step_prk(self, state: PNDMSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray) -> Union[FlaxPNDMSchedulerOutput, Tuple]:
        """Returns:"""
        if state.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        diff_to_prev = jnp.where(state.counter % 2, 0, self.config.num_train_timesteps // state.num_inference_steps // 2)
        prev_timestep = timestep - diff_to_prev
        timestep = state.prk_timesteps[state.counter // 4 * 4]
        model_output = jax.lax.select(state.counter % 4 != 3, model_output, state.cur_model_output + 1 / 6 * model_output)
        state = state.replace(cur_model_output=jax.lax.select_n(state.counter % 4, state.cur_model_output + 1 / 6 * model_output, state.cur_model_output + 1 / 3 * model_output, state.cur_model_output + 1 / 3 * model_output, jnp.zeros_like(state.cur_model_output)), ets=jax.lax.select(state.counter % 4 == 0, state.ets.at[0:3].set(state.ets[1:4]).at[3].set(model_output), state.ets), cur_sample=jax.lax.select(state.counter % 4 == 0, sample, state.cur_sample))
        cur_sample = state.cur_sample
        prev_sample = self._get_prev_sample(state, cur_sample, timestep, prev_timestep, model_output)
        state = state.replace(counter=state.counter + 1)
        return (prev_sample, state)
    def step_plms(self, state: PNDMSchedulerState, model_output: jnp.ndarray, timestep: int, sample: jnp.ndarray) -> Union[FlaxPNDMSchedulerOutput, Tuple]:
        """Returns:"""
        if state.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        prev_timestep = timestep - self.config.num_train_timesteps // state.num_inference_steps
        prev_timestep = jnp.where(prev_timestep > 0, prev_timestep, 0)
        prev_timestep = jnp.where(state.counter == 1, timestep, prev_timestep)
        timestep = jnp.where(state.counter == 1, timestep + self.config.num_train_timesteps // state.num_inference_steps, timestep)
        state = state.replace(ets=jax.lax.select(state.counter != 1, state.ets.at[0:3].set(state.ets[1:4]).at[3].set(model_output), state.ets), cur_sample=jax.lax.select(state.counter != 1, sample, state.cur_sample))
        state = state.replace(cur_model_output=jax.lax.select_n(jnp.clip(state.counter, 0, 4), model_output, (model_output + state.ets[-1]) / 2, (3 * state.ets[-1] - state.ets[-2]) / 2, (23 * state.ets[-1] - 16 * state.ets[-2] + 5 * state.ets[-3]) / 12, 1 / 24 * (55 * state.ets[-1] - 59 * state.ets[-2] + 37 * state.ets[-3] - 9 * state.ets[-4])))
        sample = state.cur_sample
        model_output = state.cur_model_output
        prev_sample = self._get_prev_sample(state, sample, timestep, prev_timestep, model_output)
        state = state.replace(counter=state.counter + 1)
        return (prev_sample, state)
    def _get_prev_sample(self, state: PNDMSchedulerState, sample, timestep, prev_timestep, model_output):
        alpha_prod_t = state.common.alphas_cumprod[timestep]
        alpha_prod_t_prev = jnp.where(prev_timestep >= 0, state.common.alphas_cumprod[prev_timestep], state.final_alpha_cumprod)
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        if self.config.prediction_type == 'v_prediction': model_output = alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
        elif self.config.prediction_type != 'epsilon': raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon` or `v_prediction`')
        sample_coeff = (alpha_prod_t_prev / alpha_prod_t) ** 0.5
        model_output_denom_coeff = alpha_prod_t * beta_prod_t_prev ** 0.5 + (alpha_prod_t * beta_prod_t * alpha_prod_t_prev) ** 0.5
        prev_sample = sample_coeff * sample - (alpha_prod_t_prev - alpha_prod_t) * model_output / model_output_denom_coeff
        return prev_sample
    def add_noise(self, state: PNDMSchedulerState, original_samples: jnp.ndarray, noise: jnp.ndarray, timesteps: jnp.ndarray) -> jnp.ndarray: return add_noise_common(state.common, original_samples, noise, timesteps)
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
