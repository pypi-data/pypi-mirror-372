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
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin
if is_scipy_available(): import scipy.stats
@dataclass
class EulerDiscreteSchedulerOutput(BaseOutput):
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
def rescale_zero_terminal_snr(betas):
    """Returns:"""
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0)
    alphas_bar_sqrt = alphas_cumprod.sqrt()
    alphas_bar_sqrt_0 = alphas_bar_sqrt[0].clone()
    alphas_bar_sqrt_T = alphas_bar_sqrt[-1].clone()
    alphas_bar_sqrt -= alphas_bar_sqrt_T
    alphas_bar_sqrt *= alphas_bar_sqrt_0 / (alphas_bar_sqrt_0 - alphas_bar_sqrt_T)
    alphas_bar = alphas_bar_sqrt ** 2
    alphas = alphas_bar[1:] / alphas_bar[:-1]
    alphas = torch.cat([alphas_bar[0:1], alphas])
    betas = 1 - alphas
    return betas
class EulerDiscreteScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    prediction_type: str='epsilon', interpolation_type: str='linear', use_karras_sigmas: Optional[bool]=False, use_exponential_sigmas: Optional[bool]=False, use_beta_sigmas: Optional[bool]=False,
    sigma_min: Optional[float]=None, sigma_max: Optional[float]=None, timestep_spacing: str='linspace', timestep_type: str='discrete', steps_offset: int=0,
    rescale_betas_zero_snr: bool=False, final_sigmas_type: str='zero'):
        if self.config.use_beta_sigmas and (not is_scipy_available()): raise ImportError('Make sure to install scipy if you want to use beta sigmas.')
        if sum([self.config.use_beta_sigmas, self.config.use_exponential_sigmas, self.config.use_karras_sigmas]) > 1: raise ValueError('Only one of `config.use_beta_sigmas`, `config.use_exponential_sigmas`, `config.use_karras_sigmas` can be used.')
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        if rescale_betas_zero_snr: self.betas = rescale_zero_terminal_snr(self.betas)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        if rescale_betas_zero_snr: self.alphas_cumprod[-1] = 2 ** (-24)
        sigmas = (((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5).flip(0)
        timesteps = np.linspace(0, num_train_timesteps - 1, num_train_timesteps, dtype=float)[::-1].copy()
        timesteps = torch.from_numpy(timesteps).to(dtype=torch.float32)
        self.num_inference_steps = None
        if timestep_type == 'continuous' and prediction_type == 'v_prediction': self.timesteps = torch.Tensor([0.25 * sigma.log() for sigma in sigmas])
        else: self.timesteps = timesteps
        self.sigmas = torch.cat([sigmas, torch.zeros(1, device=sigmas.device)])
        self.is_scale_input_called = False
        self.use_karras_sigmas = use_karras_sigmas
        self.use_exponential_sigmas = use_exponential_sigmas
        self.use_beta_sigmas = use_beta_sigmas
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
    @property
    def init_noise_sigma(self):
        max_sigma = max(self.sigmas) if isinstance(self.sigmas, list) else self.sigmas.max()
        if self.config.timestep_spacing in ['linspace', 'trailing']: return max_sigma
        return (max_sigma ** 2 + 1) ** 0.5
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
        self.is_scale_input_called = True
        return sample
    def set_timesteps(self, num_inference_steps: int=None, device: Union[str, torch.device]=None, timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None):
        """Args:"""
        if timesteps is not None and sigmas is not None: raise ValueError('Only one of `timesteps` or `sigmas` should be set.')
        if num_inference_steps is None and timesteps is None and (sigmas is None): raise ValueError('Must pass exactly one of `num_inference_steps` or `timesteps` or `sigmas.')
        if num_inference_steps is not None and (timesteps is not None or sigmas is not None): raise ValueError('Can only pass one of `num_inference_steps` or `timesteps` or `sigmas`.')
        if timesteps is not None and self.config.use_karras_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_karras_sigmas = True`.')
        if timesteps is not None and self.config.use_exponential_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_exponential_sigmas = True`.')
        if timesteps is not None and self.config.use_beta_sigmas: raise ValueError('Cannot set `timesteps` with `config.use_beta_sigmas = True`.')
        if timesteps is not None and self.config.timestep_type == 'continuous' and (self.config.prediction_type == 'v_prediction'): raise ValueError("Cannot set `timesteps` with `config.timestep_type = 'continuous'` and `config.prediction_type = 'v_prediction'`.")
        if num_inference_steps is None: num_inference_steps = len(timesteps) if timesteps is not None else len(sigmas) - 1
        self.num_inference_steps = num_inference_steps
        if sigmas is not None:
            log_sigmas = np.log(np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5))
            sigmas = np.array(sigmas).astype(np.float32)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas[:-1]])
        else:
            if timesteps is not None: timesteps = np.array(timesteps).astype(np.float32)
            elif self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, self.config.num_train_timesteps - 1, num_inference_steps, dtype=np.float32)[::-1].copy()
            elif self.config.timestep_spacing == 'leading':
                step_ratio = self.config.num_train_timesteps // self.num_inference_steps
                timesteps = (np.arange(0, num_inference_steps) * step_ratio).round()[::-1].copy().astype(np.float32)
                timesteps += self.config.steps_offset
            elif self.config.timestep_spacing == 'trailing':
                step_ratio = self.config.num_train_timesteps / self.num_inference_steps
                timesteps = np.arange(self.config.num_train_timesteps, 0, -step_ratio).round().copy().astype(np.float32)
                timesteps -= 1
            else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
            sigmas = np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5)
            log_sigmas = np.log(sigmas)
            if self.config.interpolation_type == 'linear': sigmas = np.interp(timesteps, np.arange(0, len(sigmas)), sigmas)
            elif self.config.interpolation_type == 'log_linear': sigmas = torch.linspace(np.log(sigmas[-1]), np.log(sigmas[0]), num_inference_steps + 1).exp().numpy()
            else: raise ValueError(f"{self.config.interpolation_type} is not implemented. Please specify interpolation_type to either 'linear' or 'log_linear'")
            if self.config.use_karras_sigmas:
                sigmas = self._convert_to_karras(in_sigmas=sigmas, num_inference_steps=self.num_inference_steps)
                timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            elif self.config.use_exponential_sigmas:
                sigmas = self._convert_to_exponential(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
                timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            elif self.config.use_beta_sigmas:
                sigmas = self._convert_to_beta(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
                timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = ((1 - self.alphas_cumprod[0]) / self.alphas_cumprod[0]) ** 0.5
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        sigmas = torch.from_numpy(sigmas).to(dtype=torch.float32, device=device)
        if self.config.timestep_type == 'continuous' and self.config.prediction_type == 'v_prediction': self.timesteps = torch.Tensor([0.25 * sigma.log() for sigma in sigmas[:-1]]).to(device=device)
        else: self.timesteps = torch.from_numpy(timesteps.astype(np.float32)).to(device=device)
        self._step_index = None
        self._begin_index = None
        self.sigmas = sigmas.to('cpu')
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
    def step(self, model_output: torch.Tensor, timestep: Union[float, torch.Tensor], sample: torch.Tensor, s_churn: float=0.0, s_tmin: float=0.0, s_tmax: float=float('inf'),
    s_noise: float=1.0, generator: Optional[torch.Generator]=None, return_dict: bool=True) -> Union[EulerDiscreteSchedulerOutput, Tuple]:
        """Returns:"""
        if isinstance(timestep, (int, torch.IntTensor, torch.LongTensor)): raise ValueError('Passing integer indices (e.g. from `enumerate(timesteps)`) as timesteps to `EulerDiscreteScheduler.step()` is not supported. Make sure to pass one of the `scheduler.timesteps` as a timestep.')
        if self.step_index is None: self._init_step_index(timestep)
        sample = sample.to(torch.float32)
        sigma = self.sigmas[self.step_index]
        gamma = min(s_churn / (len(self.sigmas) - 1), 2 ** 0.5 - 1) if s_tmin <= sigma <= s_tmax else 0.0
        sigma_hat = sigma * (gamma + 1)
        if gamma > 0:
            noise = randn_tensor(model_output.shape, dtype=model_output.dtype, device=model_output.device, generator=generator)
            eps = noise * s_noise
            sample = sample + eps * (sigma_hat ** 2 - sigma ** 2) ** 0.5
        if self.config.prediction_type == 'original_sample' or self.config.prediction_type == 'sample': pred_original_sample = model_output
        elif self.config.prediction_type == 'epsilon': pred_original_sample = sample - sigma_hat * model_output
        elif self.config.prediction_type == 'v_prediction': pred_original_sample = model_output * (-sigma / (sigma ** 2 + 1) ** 0.5) + sample / (sigma ** 2 + 1)
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, or `v_prediction`')
        derivative = (sample - pred_original_sample) / sigma_hat
        dt = self.sigmas[self.step_index + 1] - sigma_hat
        prev_sample = sample + derivative * dt
        prev_sample = prev_sample.to(model_output.dtype)
        self._step_index += 1
        if not return_dict: return (prev_sample, pred_original_sample)
        return EulerDiscreteSchedulerOutput(prev_sample=prev_sample, pred_original_sample=pred_original_sample)
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
    def get_velocity(self, sample: torch.Tensor, noise: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        if isinstance(timesteps, int) or isinstance(timesteps, torch.IntTensor) or isinstance(timesteps, torch.LongTensor): raise ValueError('Passing integer indices (e.g. from `enumerate(timesteps)`) as timesteps to `EulerDiscreteScheduler.get_velocity()` is not supported. Make sure to pass one of the `scheduler.timesteps` as a timestep.')
        if sample.device.type == 'mps' and torch.is_floating_point(timesteps):
            schedule_timesteps = self.timesteps.to(sample.device, dtype=torch.float32)
            timesteps = timesteps.to(sample.device, dtype=torch.float32)
        else:
            schedule_timesteps = self.timesteps.to(sample.device)
            timesteps = timesteps.to(sample.device)
        step_indices = [self.index_for_timestep(t, schedule_timesteps) for t in timesteps]
        alphas_cumprod = self.alphas_cumprod.to(sample)
        sqrt_alpha_prod = alphas_cumprod[step_indices] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(sample.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[step_indices]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(sample.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        velocity = sqrt_alpha_prod * noise - sqrt_one_minus_alpha_prod * sample
        return velocity
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
