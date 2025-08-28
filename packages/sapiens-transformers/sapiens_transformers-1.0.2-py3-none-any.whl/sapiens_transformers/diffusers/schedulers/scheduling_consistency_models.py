'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import SchedulerMixin
@dataclass
class CMStochasticIterativeSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
class CMStochasticIterativeScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=40, sigma_min: float=0.002, sigma_max: float=80.0, sigma_data: float=0.5, s_noise: float=1.0, rho: float=7.0, clip_denoised: bool=True):
        self.init_noise_sigma = sigma_max
        ramp = np.linspace(0, 1, num_train_timesteps)
        sigmas = self._convert_to_karras(ramp)
        timesteps = self.sigma_to_t(sigmas)
        self.num_inference_steps = None
        self.sigmas = torch.from_numpy(sigmas)
        self.timesteps = torch.from_numpy(timesteps)
        self.custom_timesteps = False
        self.is_scale_input_called = False
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    @property
    def step_index(self): return self._step_index
    @property
    def begin_index(self): return self._begin_index
    def set_begin_index(self, begin_index: int=0):
        """Args:"""
        self._begin_index = begin_index
    def scale_model_input(self, sample: torch.Tensor, timestep: Union[float, torch.Tensor]) -> torch.Tensor:
        """Returns:"""
        if self.step_index is None: self._init_step_index(timestep)
        sigma = self.sigmas[self.step_index]
        sample = sample / (sigma ** 2 + self.config.sigma_data ** 2) ** 0.5
        self.is_scale_input_called = True
        return sample
    def sigma_to_t(self, sigmas: Union[float, np.ndarray]):
        """Returns:"""
        if not isinstance(sigmas, np.ndarray): sigmas = np.array(sigmas, dtype=np.float64)
        timesteps = 1000 * 0.25 * np.log(sigmas + 1e-44)
        return timesteps
    def set_timesteps(self, num_inference_steps: Optional[int]=None, device: Union[str, torch.device]=None, timesteps: Optional[List[int]]=None):
        """Args:"""
        if num_inference_steps is None and timesteps is None: raise ValueError('Exactly one of `num_inference_steps` or `timesteps` must be supplied.')
        if num_inference_steps is not None and timesteps is not None: raise ValueError('Can only pass one of `num_inference_steps` or `timesteps`.')
        if timesteps is not None:
            for i in range(1, len(timesteps)):
                if timesteps[i] >= timesteps[i - 1]: raise ValueError('`timesteps` must be in descending order.')
            if timesteps[0] >= self.config.num_train_timesteps: raise ValueError(f'`timesteps` must start before `self.config.train_timesteps`: {self.config.num_train_timesteps}.')
            timesteps = np.array(timesteps, dtype=np.int64)
            self.custom_timesteps = True
        else:
            if num_inference_steps > self.config.num_train_timesteps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `self.config.train_timesteps`: {self.config.num_train_timesteps} as the unet model trained with this scheduler can only handle maximal {self.config.num_train_timesteps} timesteps.')
            self.num_inference_steps = num_inference_steps
            step_ratio = self.config.num_train_timesteps // self.num_inference_steps
            timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.int64)
            self.custom_timesteps = False
        num_train_timesteps = self.config.num_train_timesteps
        ramp = timesteps[::-1].copy()
        ramp = ramp / (num_train_timesteps - 1)
        sigmas = self._convert_to_karras(ramp)
        timesteps = self.sigma_to_t(sigmas)
        sigmas = np.concatenate([sigmas, [self.config.sigma_min]]).astype(np.float32)
        self.sigmas = torch.from_numpy(sigmas).to(device=device)
        if str(device).startswith('mps'): self.timesteps = torch.from_numpy(timesteps).to(device, dtype=torch.float32)
        else: self.timesteps = torch.from_numpy(timesteps).to(device=device)
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    def _convert_to_karras(self, ramp):
        sigma_min: float = self.config.sigma_min
        sigma_max: float = self.config.sigma_max
        rho = self.config.rho
        min_inv_rho = sigma_min ** (1 / rho)
        max_inv_rho = sigma_max ** (1 / rho)
        sigmas = (max_inv_rho + ramp * (min_inv_rho - max_inv_rho)) ** rho
        return sigmas
    def get_scalings(self, sigma):
        sigma_data = self.config.sigma_data
        c_skip = sigma_data ** 2 / (sigma ** 2 + sigma_data ** 2)
        c_out = sigma * sigma_data / (sigma ** 2 + sigma_data ** 2) ** 0.5
        return (c_skip, c_out)
    def get_scalings_for_boundary_condition(self, sigma):
        """Returns:"""
        sigma_min = self.config.sigma_min
        sigma_data = self.config.sigma_data
        c_skip = sigma_data ** 2 / ((sigma - sigma_min) ** 2 + sigma_data ** 2)
        c_out = (sigma - sigma_min) * sigma_data / (sigma ** 2 + sigma_data ** 2) ** 0.5
        return (c_skip, c_out)
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
    def step(self, model_output: torch.Tensor, timestep: Union[float, torch.Tensor], sample: torch.Tensor, generator: Optional[torch.Generator]=None,
    return_dict: bool=True) -> Union[CMStochasticIterativeSchedulerOutput, Tuple]:
        """Returns:"""
        if isinstance(timestep, (int, torch.IntTensor, torch.LongTensor)): raise ValueError(f'Passing integer indices (e.g. from `enumerate(timesteps)`) as timesteps to `{self.__class__}.step()` is not supported. Make sure to pass one of the `scheduler.timesteps` as a timestep.')
        sigma_min = self.config.sigma_min
        sigma_max = self.config.sigma_max
        if self.step_index is None: self._init_step_index(timestep)
        sigma = self.sigmas[self.step_index]
        if self.step_index + 1 < self.config.num_train_timesteps: sigma_next = self.sigmas[self.step_index + 1]
        else: sigma_next = self.sigmas[-1]
        c_skip, c_out = self.get_scalings_for_boundary_condition(sigma)
        denoised = c_out * model_output + c_skip * sample
        if self.config.clip_denoised: denoised = denoised.clamp(-1, 1)
        if len(self.timesteps) > 1: noise = randn_tensor(model_output.shape, dtype=model_output.dtype, device=model_output.device, generator=generator)
        else: noise = torch.zeros_like(model_output)
        z = noise * self.config.s_noise
        sigma_hat = sigma_next.clamp(min=sigma_min, max=sigma_max)
        prev_sample = denoised + z * (sigma_hat ** 2 - sigma_min ** 2) ** 0.5
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return CMStochasticIterativeSchedulerOutput(prev_sample=prev_sample)
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        sigmas = self.sigmas.to(device=original_samples.device, dtype=original_samples.dtype)
        if original_samples.device.type == 'mps' and torch.is_floating_point(timesteps):
            schedule_timesteps = self.timesteps.to(original_samples.device, dtype=torch.float32)
            timesteps = timesteps.to(original_samples.device, dtype=torch.float32)
        else:
            schedule_timesteps = self.timesteps.to(original_samples.device)
            timesteps = timesteps.to(original_samples.device)
        if self.begin_index is None: step_indices = [self.index_for_timestep(t, schedule_timesteps) for t in timesteps]
        elif self.step_index is not None: step_indices = [self.step_index] * timesteps.shape[0]
        else: step_indices = [self.begin_index] * timesteps.shape[0]
        sigma = sigmas[step_indices].flatten()
        while len(sigma.shape) < len(original_samples.shape): sigma = sigma.unsqueeze(-1)
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
