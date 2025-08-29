'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput, is_scipy_available
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin
if is_scipy_available(): import scipy.stats
@dataclass
class HeunDiscreteSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
    pred_original_sample: Optional[torch.Tensor] = None
def betas_for_alpha_bar(num_diffusion_timesteps, max_beta=0.999, alpha_transform_type='cosine'):
    """Returns:"""
    if alpha_transform_type == 'cosine':
        def alpha_bar_fn(t): return math.cos((t + 0.008) / 1.008 * math.pi / 2) ** 2
    elif alpha_transform_type == 'exp':
        def alpha_bar_fn(t): return math.exp(t * -12.0)
    else: raise ValueError(f'Unsupported alpha_transform_type: {alpha_transform_type}')
    betas = []
    for i in range(num_diffusion_timesteps):
        t1 = i / num_diffusion_timesteps
        t2 = (i + 1) / num_diffusion_timesteps
        betas.append(min(1 - alpha_bar_fn(t2) / alpha_bar_fn(t1), max_beta))
    return torch.tensor(betas, dtype=torch.float32)
class HeunDiscreteScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 2
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.00085, beta_end: float=0.012, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    prediction_type: str='epsilon', use_karras_sigmas: Optional[bool]=False, use_exponential_sigmas: Optional[bool]=False, use_beta_sigmas: Optional[bool]=False, clip_sample: Optional[bool]=False,
    clip_sample_range: float=1.0, timestep_spacing: str='linspace', steps_offset: int=0):
        if self.config.use_beta_sigmas and (not is_scipy_available()): raise ImportError('Make sure to install scipy if you want to use beta sigmas.')
        if sum([self.config.use_beta_sigmas, self.config.use_exponential_sigmas, self.config.use_karras_sigmas]) > 1: raise ValueError('Only one of `config.use_beta_sigmas`, `config.use_exponential_sigmas`, `config.use_karras_sigmas` can be used.')
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps, alpha_transform_type='cosine')
        elif beta_schedule == 'exp': self.betas = betas_for_alpha_bar(num_train_timesteps, alpha_transform_type='exp')
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.set_timesteps(num_train_timesteps, None, num_train_timesteps)
        self.use_karras_sigmas = use_karras_sigmas
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    def index_for_timestep(self, timestep, schedule_timesteps=None):
        if schedule_timesteps is None: schedule_timesteps = self.timesteps
        indices = (schedule_timesteps == timestep).nonzero()
        pos = 1 if len(indices) > 1 else 0
        return indices[pos].item()
    @property
    def init_noise_sigma(self):
        if self.config.timestep_spacing in ['linspace', 'trailing']: return self.sigmas.max()
        return (self.sigmas.max() ** 2 + 1) ** 0.5
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
        sample = sample / (sigma ** 2 + 1) ** 0.5
        return sample
    def set_timesteps(self, num_inference_steps: Optional[int]=None, device: Union[str, torch.device]=None, num_train_timesteps: Optional[int]=None, timesteps: Optional[List[int]]=None):
        """Args:"""
        if num_inference_steps is None and timesteps is None: raise ValueError('Must pass exactly one of `num_inference_steps` or `custom_timesteps`.')
        if num_inference_steps is not None and timesteps is not None: raise ValueError('Can only pass one of `num_inference_steps` or `custom_timesteps`.')
        if timesteps is not None and self.config.use_karras_sigmas: raise ValueError('Cannot use `timesteps` with `config.use_karras_sigmas = True`')
        if timesteps is not None and self.config.use_exponential_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_exponential_sigmas = True`.')
        if timesteps is not None and self.config.use_beta_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_beta_sigmas = True`.')
        num_inference_steps = num_inference_steps or len(timesteps)
        self.num_inference_steps = num_inference_steps
        num_train_timesteps = num_train_timesteps or self.config.num_train_timesteps
        if timesteps is not None: timesteps = np.array(timesteps, dtype=np.float32)
        elif self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, num_train_timesteps - 1, num_inference_steps, dtype=np.float32)[::-1].copy()
        elif self.config.timestep_spacing == 'leading':
            step_ratio = num_train_timesteps // self.num_inference_steps
            timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.float32)
            timesteps += self.config.steps_offset
        elif self.config.timestep_spacing == 'trailing':
            step_ratio = num_train_timesteps / self.num_inference_steps
            timesteps = np.arange(num_train_timesteps, 0, -step_ratio).round().copy().astype(np.float32)
            timesteps -= 1
        else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
        sigmas = np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5)
        log_sigmas = np.log(sigmas)
        sigmas = np.interp(timesteps, np.arange(0, len(sigmas)), sigmas)
        if self.config.use_karras_sigmas:
            sigmas = self._convert_to_karras(in_sigmas=sigmas, num_inference_steps=self.num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
        elif self.config.use_exponential_sigmas:
            sigmas = self._convert_to_exponential(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
        elif self.config.use_beta_sigmas:
            sigmas = self._convert_to_beta(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
        sigmas = np.concatenate([sigmas, [0.0]]).astype(np.float32)
        sigmas = torch.from_numpy(sigmas).to(device=device)
        self.sigmas = torch.cat([sigmas[:1], sigmas[1:-1].repeat_interleave(2), sigmas[-1:]])
        timesteps = torch.from_numpy(timesteps)
        timesteps = torch.cat([timesteps[:1], timesteps[1:].repeat_interleave(2)])
        self.timesteps = timesteps.to(device=device)
        self.prev_derivative = None
        self.dt = None
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    def _sigma_to_t(self, sigma, log_sigmas):
        log_sigma = np.log(np.maximum(sigma, 1e-10))
        dists = log_sigma - log_sigmas[:, np.newaxis]
        low_idx = np.cumsum(dists >= 0, axis=0).argmax(axis=0).clip(max=log_sigmas.shape[0] - 2)
        high_idx = low_idx + 1
        low = log_sigmas[low_idx]
        high = log_sigmas[high_idx]
        w = (low - log_sigma) / (low - high)
        w = np.clip(w, 0, 1)
        t = (1 - w) * low_idx + w * high_idx
        t = t.reshape(sigma.shape)
        return t
    def _convert_to_karras(self, in_sigmas: torch.Tensor, num_inference_steps) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        rho = 7.0
        ramp = np.linspace(0, 1, num_inference_steps)
        min_inv_rho = sigma_min ** (1 / rho)
        max_inv_rho = sigma_max ** (1 / rho)
        sigmas = (max_inv_rho + ramp * (min_inv_rho - max_inv_rho)) ** rho
        return sigmas
    def _convert_to_exponential(self, in_sigmas: torch.Tensor, num_inference_steps: int) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        sigmas = np.exp(np.linspace(math.log(sigma_max), math.log(sigma_min), num_inference_steps))
        return sigmas
    def _convert_to_beta(self, in_sigmas: torch.Tensor, num_inference_steps: int, alpha: float=0.6, beta: float=0.6) -> torch.Tensor:
        if hasattr(self.config, 'sigma_min'): sigma_min = self.config.sigma_min
        else: sigma_min = None
        if hasattr(self.config, 'sigma_max'): sigma_max = self.config.sigma_max
        else: sigma_max = None
        sigma_min = sigma_min if sigma_min is not None else in_sigmas[-1].item()
        sigma_max = sigma_max if sigma_max is not None else in_sigmas[0].item()
        sigmas = np.array([sigma_min + ppf * (sigma_max - sigma_min) for ppf in [scipy.stats.beta.ppf(timestep, alpha, beta) for timestep in 1 - np.linspace(0, 1, num_inference_steps)]])
        return sigmas
    @property
    def state_in_first_order(self): return self.dt is None
    def _init_step_index(self, timestep):
        if self.begin_index is None:
            if isinstance(timestep, torch.Tensor): timestep = timestep.to(self.timesteps.device)
            self._step_index = self.index_for_timestep(timestep)
        else: self._step_index = self._begin_index
    def step(self, model_output: Union[torch.Tensor, np.ndarray], timestep: Union[float, torch.Tensor], sample: Union[torch.Tensor, np.ndarray],
    return_dict: bool=True) -> Union[HeunDiscreteSchedulerOutput, Tuple]:
        """Returns:"""
        if self.step_index is None: self._init_step_index(timestep)
        if self.state_in_first_order:
            sigma = self.sigmas[self.step_index]
            sigma_next = self.sigmas[self.step_index + 1]
        else:
            sigma = self.sigmas[self.step_index - 1]
            sigma_next = self.sigmas[self.step_index]
        gamma = 0
        sigma_hat = sigma * (gamma + 1)
        if self.config.prediction_type == 'epsilon':
            sigma_input = sigma_hat if self.state_in_first_order else sigma_next
            pred_original_sample = sample - sigma_input * model_output
        elif self.config.prediction_type == 'v_prediction':
            sigma_input = sigma_hat if self.state_in_first_order else sigma_next
            pred_original_sample = model_output * (-sigma_input / (sigma_input ** 2 + 1) ** 0.5) + sample / (sigma_input ** 2 + 1)
        elif self.config.prediction_type == 'sample': pred_original_sample = model_output
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, or `v_prediction`')
        if self.config.clip_sample: pred_original_sample = pred_original_sample.clamp(-self.config.clip_sample_range, self.config.clip_sample_range)
        if self.state_in_first_order:
            derivative = (sample - pred_original_sample) / sigma_hat
            dt = sigma_next - sigma_hat
            self.prev_derivative = derivative
            self.dt = dt
            self.sample = sample
        else:
            derivative = (sample - pred_original_sample) / sigma_next
            derivative = (self.prev_derivative + derivative) / 2
            dt = self.dt
            sample = self.sample
            self.prev_derivative = None
            self.dt = None
            self.sample = None
        prev_sample = sample + derivative * dt
        self._step_index += 1
        if not return_dict: return (prev_sample, pred_original_sample)
        return HeunDiscreteSchedulerOutput(prev_sample=prev_sample, pred_original_sample=pred_original_sample)
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
