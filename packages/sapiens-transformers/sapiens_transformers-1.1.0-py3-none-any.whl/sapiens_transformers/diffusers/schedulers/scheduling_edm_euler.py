'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import SchedulerMixin
@dataclass
class EDMEulerSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
    pred_original_sample: Optional[torch.Tensor] = None
class EDMEulerScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = []
    order = 1
    @register_to_config
    def __init__(self, sigma_min: float=0.002, sigma_max: float=80.0, sigma_data: float=0.5, sigma_schedule: str='karras',
    num_train_timesteps: int=1000, prediction_type: str='epsilon', rho: float=7.0):
        if sigma_schedule not in ['karras', 'exponential']: raise ValueError(f'Wrong value for provided for `sigma_schedule={sigma_schedule!r}`.`')
        self.num_inference_steps = None
        ramp = torch.linspace(0, 1, num_train_timesteps)
        if sigma_schedule == 'karras': sigmas = self._compute_karras_sigmas(ramp)
        elif sigma_schedule == 'exponential': sigmas = self._compute_exponential_sigmas(ramp)
        self.timesteps = self.precondition_noise(sigmas)
        self.sigmas = torch.cat([sigmas, torch.zeros(1, device=sigmas.device)])
        self.is_scale_input_called = False
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    @property
    def init_noise_sigma(self): return (self.config.sigma_max ** 2 + 1) ** 0.5
    @property
    def step_index(self): return self._step_index
    @property
    def begin_index(self): return self._begin_index
    def set_begin_index(self, begin_index: int=0):
        """Args:"""
        self._begin_index = begin_index
    def precondition_inputs(self, sample, sigma):
        c_in = 1 / (sigma ** 2 + self.config.sigma_data ** 2) ** 0.5
        scaled_sample = sample * c_in
        return scaled_sample
    def precondition_noise(self, sigma):
        if not isinstance(sigma, torch.Tensor): sigma = torch.tensor([sigma])
        c_noise = 0.25 * torch.log(sigma)
        return c_noise
    def precondition_outputs(self, sample, model_output, sigma):
        sigma_data = self.config.sigma_data
        c_skip = sigma_data ** 2 / (sigma ** 2 + sigma_data ** 2)
        if self.config.prediction_type == 'epsilon': c_out = sigma * sigma_data / (sigma ** 2 + sigma_data ** 2) ** 0.5
        elif self.config.prediction_type == 'v_prediction': c_out = -sigma * sigma_data / (sigma ** 2 + sigma_data ** 2) ** 0.5
        else: raise ValueError(f'Prediction type {self.config.prediction_type} is not supported.')
        denoised = c_skip * sample + c_out * model_output
        return denoised
    def scale_model_input(self, sample: torch.Tensor, timestep: Union[float, torch.Tensor]) -> torch.Tensor:
        """Returns:"""
        if self.step_index is None: self._init_step_index(timestep)
        sigma = self.sigmas[self.step_index]
        sample = self.precondition_inputs(sample, sigma)
        self.is_scale_input_called = True
        return sample
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        ramp = torch.linspace(0, 1, self.num_inference_steps)
        if self.config.sigma_schedule == 'karras': sigmas = self._compute_karras_sigmas(ramp)
        elif self.config.sigma_schedule == 'exponential': sigmas = self._compute_exponential_sigmas(ramp)
        sigmas = sigmas.to(dtype=torch.float32, device=device)
        self.timesteps = self.precondition_noise(sigmas)
        self.sigmas = torch.cat([sigmas, torch.zeros(1, device=sigmas.device)])
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    def _compute_karras_sigmas(self, ramp, sigma_min=None, sigma_max=None) -> torch.Tensor:
        sigma_min = sigma_min or self.config.sigma_min
        sigma_max = sigma_max or self.config.sigma_max
        rho = self.config.rho
        min_inv_rho = sigma_min ** (1 / rho)
        max_inv_rho = sigma_max ** (1 / rho)
        sigmas = (max_inv_rho + ramp * (min_inv_rho - max_inv_rho)) ** rho
        return sigmas
    def _compute_exponential_sigmas(self, ramp, sigma_min=None, sigma_max=None) -> torch.Tensor:
        sigma_min = sigma_min or self.config.sigma_min
        sigma_max = sigma_max or self.config.sigma_max
        sigmas = torch.linspace(math.log(sigma_min), math.log(sigma_max), len(ramp)).exp().flip(0)
        return sigmas
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
    def step(self, model_output: torch.Tensor, timestep: Union[float, torch.Tensor], sample: torch.Tensor, s_churn: float=0.0, s_tmin: float=0.0, s_tmax: float=float('inf'), s_noise: float=1.0,
    generator: Optional[torch.Generator]=None, return_dict: bool=True) -> Union[EDMEulerSchedulerOutput, Tuple]:
        """Returns:"""
        if isinstance(timestep, (int, torch.IntTensor, torch.LongTensor)): raise ValueError('Passing integer indices (e.g. from `enumerate(timesteps)`) as timesteps to `EDMEulerScheduler.step()` is not supported. Make sure to pass one of the `scheduler.timesteps` as a timestep.')
        if self.step_index is None: self._init_step_index(timestep)
        sample = sample.to(torch.float32)
        sigma = self.sigmas[self.step_index]
        gamma = min(s_churn / (len(self.sigmas) - 1), 2 ** 0.5 - 1) if s_tmin <= sigma <= s_tmax else 0.0
        sigma_hat = sigma * (gamma + 1)
        if gamma > 0:
            noise = randn_tensor(model_output.shape, dtype=model_output.dtype, device=model_output.device, generator=generator)
            eps = noise * s_noise
            sample = sample + eps * (sigma_hat ** 2 - sigma ** 2) ** 0.5
        pred_original_sample = self.precondition_outputs(sample, model_output, sigma_hat)
        derivative = (sample - pred_original_sample) / sigma_hat
        dt = self.sigmas[self.step_index + 1] - sigma_hat
        prev_sample = sample + derivative * dt
        prev_sample = prev_sample.to(model_output.dtype)
        self._step_index += 1
        if not return_dict: return (prev_sample, pred_original_sample)
        return EDMEulerSchedulerOutput(prev_sample=prev_sample, pred_original_sample=pred_original_sample)
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
