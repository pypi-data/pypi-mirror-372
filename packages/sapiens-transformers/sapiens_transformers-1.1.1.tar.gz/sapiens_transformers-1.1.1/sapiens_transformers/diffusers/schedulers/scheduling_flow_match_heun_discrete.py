'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import SchedulerMixin
@dataclass
class FlowMatchHeunDiscreteSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.FloatTensor
class FlowMatchHeunDiscreteScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = []
    order = 2
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, shift: float=1.0):
        timesteps = np.linspace(1, num_train_timesteps, num_train_timesteps, dtype=np.float32)[::-1].copy()
        timesteps = torch.from_numpy(timesteps).to(dtype=torch.float32)
        sigmas = timesteps / num_train_timesteps
        sigmas = shift * sigmas / (1 + (shift - 1) * sigmas)
        self.timesteps = sigmas * num_train_timesteps
        self._step_index = None
        self._begin_index = None
        self.sigmas = sigmas.to('cpu')
        self.sigma_min = self.sigmas[-1].item()
        self.sigma_max = self.sigmas[0].item()
    @property
    def step_index(self): return self._step_index
    @property
    def begin_index(self): return self._begin_index
    def set_begin_index(self, begin_index: int=0):
        """Args:"""
        self._begin_index = begin_index
    def scale_noise(self, sample: torch.FloatTensor, timestep: Union[float, torch.FloatTensor], noise: Optional[torch.FloatTensor]=None) -> torch.FloatTensor:
        """Returns:"""
        if self.step_index is None: self._init_step_index(timestep)
        sigma = self.sigmas[self.step_index]
        sample = sigma * noise + (1.0 - sigma) * sample
        return sample
    def _sigma_to_t(self, sigma): return sigma * self.config.num_train_timesteps
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        timesteps = np.linspace(self._sigma_to_t(self.sigma_max), self._sigma_to_t(self.sigma_min), num_inference_steps)
        sigmas = timesteps / self.config.num_train_timesteps
        sigmas = self.config.shift * sigmas / (1 + (self.config.shift - 1) * sigmas)
        sigmas = torch.from_numpy(sigmas).to(dtype=torch.float32, device=device)
        timesteps = sigmas * self.config.num_train_timesteps
        timesteps = torch.cat([timesteps[:1], timesteps[1:].repeat_interleave(2)])
        self.timesteps = timesteps.to(device=device)
        sigmas = torch.cat([sigmas, torch.zeros(1, device=sigmas.device)])
        self.sigmas = torch.cat([sigmas[:1], sigmas[1:-1].repeat_interleave(2), sigmas[-1:]])
        self.prev_derivative = None
        self.dt = None
        self._step_index = None
        self._begin_index = None
    def index_for_timestep(self, timestep, schedule_timesteps=None):
        if schedule_timesteps is None: schedule_timesteps = self.timesteps
        indices = (schedule_timesteps == timestep).nonzero()
        pos = 1 if len(indices) > 1 else 0
        return indices[pos].item()
    def _init_step_index(self, timestep):
        if self.begin_index is None:
            if isinstance(timestep, torch.Tensor): timestep = timestep.to(self.timesteps.device)
            self._step_index = self.index_for_timestep(timestep)
        else: self._step_index = self._begin_index
    @property
    def state_in_first_order(self): return self.dt is None
    def step(self, model_output: torch.FloatTensor, timestep: Union[float, torch.FloatTensor], sample: torch.FloatTensor, s_churn: float=0.0, s_tmin: float=0.0, s_tmax: float=float('inf'),
    s_noise: float=1.0, generator: Optional[torch.Generator]=None, return_dict: bool=True) -> Union[FlowMatchHeunDiscreteSchedulerOutput, Tuple]:
        """Returns:"""
        if isinstance(timestep, int) or isinstance(timestep, torch.IntTensor) or isinstance(timestep, torch.LongTensor): raise ValueError('Passing integer indices (e.g. from `enumerate(timesteps)`) as timesteps to `HeunDiscreteScheduler.step()` is not supported. Make sure to pass one of the `scheduler.timesteps` as a timestep.')
        if self.step_index is None: self._init_step_index(timestep)
        sample = sample.to(torch.float32)
        if self.state_in_first_order:
            sigma = self.sigmas[self.step_index]
            sigma_next = self.sigmas[self.step_index + 1]
        else:
            sigma = self.sigmas[self.step_index - 1]
            sigma_next = self.sigmas[self.step_index]
        gamma = min(s_churn / (len(self.sigmas) - 1), 2 ** 0.5 - 1) if s_tmin <= sigma <= s_tmax else 0.0
        sigma_hat = sigma * (gamma + 1)
        if gamma > 0:
            noise = randn_tensor(model_output.shape, dtype=model_output.dtype, device=model_output.device, generator=generator)
            eps = noise * s_noise
            sample = sample + eps * (sigma_hat ** 2 - sigma ** 2) ** 0.5
        if self.state_in_first_order:
            denoised = sample - model_output * sigma
            derivative = (sample - denoised) / sigma_hat
            dt = sigma_next - sigma_hat
            self.prev_derivative = derivative
            self.dt = dt
            self.sample = sample
        else:
            denoised = sample - model_output * sigma_next
            derivative = (sample - denoised) / sigma_next
            derivative = 0.5 * (self.prev_derivative + derivative)
            dt = self.dt
            sample = self.sample
            self.prev_derivative = None
            self.dt = None
            self.sample = None
        prev_sample = sample + derivative * dt
        prev_sample = prev_sample.to(model_output.dtype)
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return FlowMatchHeunDiscreteSchedulerOutput(prev_sample=prev_sample)
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
