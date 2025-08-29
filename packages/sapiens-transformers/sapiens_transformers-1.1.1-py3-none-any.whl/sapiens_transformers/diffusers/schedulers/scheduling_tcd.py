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
from ..schedulers.scheduling_utils import SchedulerMixin
from ..utils import BaseOutput
from ..utils.torch_utils import randn_tensor
@dataclass
class TCDSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
    pred_noised_sample: Optional[torch.Tensor] = None
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
def rescale_zero_terminal_snr(betas: torch.Tensor) -> torch.Tensor:
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
class TCDScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.00085, beta_end: float=0.012, beta_schedule: str='scaled_linear', trained_betas: Optional[Union[np.ndarray,
    List[float]]]=None, original_inference_steps: int=50, clip_sample: bool=False, clip_sample_range: float=1.0, set_alpha_to_one: bool=True, steps_offset: int=0,
    prediction_type: str='epsilon', thresholding: bool=False, dynamic_thresholding_ratio: float=0.995, sample_max_value: float=1.0, timestep_spacing: str='leading',
    timestep_scaling: float=10.0, rescale_betas_zero_snr: bool=False):
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        if rescale_betas_zero_snr: self.betas = rescale_zero_terminal_snr(self.betas)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.final_alpha_cumprod = torch.tensor(1.0) if set_alpha_to_one else self.alphas_cumprod[0]
        self.init_noise_sigma = 1.0
        self.num_inference_steps = None
        self.timesteps = torch.from_numpy(np.arange(0, num_train_timesteps)[::-1].copy().astype(np.int64))
        self.custom_timesteps = False
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
    def step_index(self): return self._step_index
    @property
    def begin_index(self): return self._begin_index
    def set_begin_index(self, begin_index: int=0):
        """Args:"""
        self._begin_index = begin_index
    def scale_model_input(self, sample: torch.Tensor, timestep: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        return sample
    def _get_variance(self, timestep, prev_timestep):
        alpha_prod_t = self.alphas_cumprod[timestep]
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.final_alpha_cumprod
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev
        variance = beta_prod_t_prev / beta_prod_t * (1 - alpha_prod_t / alpha_prod_t_prev)
        return variance
    def _threshold_sample(self, sample: torch.Tensor) -> torch.Tensor:
        dtype = sample.dtype
        batch_size, channels, *remaining_dims = sample.shape
        if dtype not in (torch.float32, torch.float64): sample = sample.float()
        sample = sample.reshape(batch_size, channels * np.prod(remaining_dims))
        abs_sample = sample.abs()
        s = torch.quantile(abs_sample, self.config.dynamic_thresholding_ratio, dim=1)
        s = torch.clamp(s, min=1, max=self.config.sample_max_value)
        s = s.unsqueeze(1)
        sample = torch.clamp(sample, -s, s) / s
        sample = sample.reshape(batch_size, channels, *remaining_dims)
        sample = sample.to(dtype)
        return sample
    def set_timesteps(self, num_inference_steps: Optional[int]=None, device: Union[str, torch.device]=None, original_inference_steps: Optional[int]=None,
    timesteps: Optional[List[int]]=None, strength: float=1.0):
        """Args:"""
        if num_inference_steps is None and timesteps is None: raise ValueError('Must pass exactly one of `num_inference_steps` or `custom_timesteps`.')
        if num_inference_steps is not None and timesteps is not None: raise ValueError('Can only pass one of `num_inference_steps` or `custom_timesteps`.')
        original_steps = original_inference_steps if original_inference_steps is not None else self.config.original_inference_steps
        if original_inference_steps is None:
            if original_steps > self.config.num_train_timesteps: raise ValueError(f'`original_steps`: {original_steps} cannot be larger than `self.config.train_timesteps`: {self.config.num_train_timesteps} as the unet model trained with this scheduler can only handle maximal {self.config.num_train_timesteps} timesteps.')
            k = self.config.num_train_timesteps // original_steps
            tcd_origin_timesteps = np.asarray(list(range(1, int(original_steps * strength) + 1))) * k - 1
        else: tcd_origin_timesteps = np.asarray(list(range(0, int(self.config.num_train_timesteps * strength))))
        if timesteps is not None:
            train_timesteps = set(tcd_origin_timesteps)
            non_train_timesteps = []
            for i in range(1, len(timesteps)):
                if timesteps[i] >= timesteps[i - 1]: raise ValueError('`custom_timesteps` must be in descending order.')
                if timesteps[i] not in train_timesteps: non_train_timesteps.append(timesteps[i])
            if timesteps[0] >= self.config.num_train_timesteps: raise ValueError(f'`timesteps` must start before `self.config.train_timesteps`: {self.config.num_train_timesteps}.')
            timesteps = np.array(timesteps, dtype=np.int64)
            self.num_inference_steps = len(timesteps)
            self.custom_timesteps = True
            init_timestep = min(int(self.num_inference_steps * strength), self.num_inference_steps)
            t_start = max(self.num_inference_steps - init_timestep, 0)
            timesteps = timesteps[t_start * self.order:]
        else:
            if num_inference_steps > self.config.num_train_timesteps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `self.config.train_timesteps`: {self.config.num_train_timesteps} as the unet model trained with this scheduler can only handle maximal {self.config.num_train_timesteps} timesteps.')
            if original_steps is not None:
                skipping_step = len(tcd_origin_timesteps) // num_inference_steps
                if skipping_step < 1: raise ValueError(f'The combination of `original_steps x strength`: {original_steps} x {strength} is smaller than `num_inference_steps`: {num_inference_steps}. Make sure to either reduce `num_inference_steps` to a value smaller than {int(original_steps * strength)} or increase `strength` to a value higher than {float(num_inference_steps / original_steps)}.')
            self.num_inference_steps = num_inference_steps
            if original_steps is not None:
                if num_inference_steps > original_steps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `original_inference_steps`: {original_steps} because the final timestep schedule will be a subset of the `original_inference_steps`-sized initial timestep schedule.')
            elif num_inference_steps > self.config.num_train_timesteps: raise ValueError(f'`num_inference_steps`: {num_inference_steps} cannot be larger than `num_train_timesteps`: {self.config.num_train_timesteps} because the final timestep schedule will be a subset of the `num_train_timesteps`-sized initial timestep schedule.')
            tcd_origin_timesteps = tcd_origin_timesteps[::-1].copy()
            inference_indices = np.linspace(0, len(tcd_origin_timesteps), num=num_inference_steps, endpoint=False)
            inference_indices = np.floor(inference_indices).astype(np.int64)
            timesteps = tcd_origin_timesteps[inference_indices]
        self.timesteps = torch.from_numpy(timesteps).to(device=device, dtype=torch.long)
        self._step_index = None
        self._begin_index = None
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, eta: float=0.3, generator: Optional[torch.Generator]=None,
    return_dict: bool=True) -> Union[TCDSchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.step_index is None: self._init_step_index(timestep)
        assert 0 <= eta <= 1.0, 'gamma must be less than or equal to 1.0'
        prev_step_index = self.step_index + 1
        if prev_step_index < len(self.timesteps): prev_timestep = self.timesteps[prev_step_index]
        else: prev_timestep = torch.tensor(0)
        timestep_s = torch.floor((1 - eta) * prev_timestep).to(dtype=torch.long)
        alpha_prod_t = self.alphas_cumprod[timestep]
        beta_prod_t = 1 - alpha_prod_t
        alpha_prod_t_prev = self.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else self.final_alpha_cumprod
        alpha_prod_s = self.alphas_cumprod[timestep_s]
        beta_prod_s = 1 - alpha_prod_s
        if self.config.prediction_type == 'epsilon':
            pred_original_sample = (sample - beta_prod_t.sqrt() * model_output) / alpha_prod_t.sqrt()
            pred_epsilon = model_output
            pred_noised_sample = alpha_prod_s.sqrt() * pred_original_sample + beta_prod_s.sqrt() * pred_epsilon
        elif self.config.prediction_type == 'sample':
            pred_original_sample = model_output
            pred_epsilon = (sample - alpha_prod_t ** 0.5 * pred_original_sample) / beta_prod_t ** 0.5
            pred_noised_sample = alpha_prod_s.sqrt() * pred_original_sample + beta_prod_s.sqrt() * pred_epsilon
        elif self.config.prediction_type == 'v_prediction':
            pred_original_sample = alpha_prod_t ** 0.5 * sample - beta_prod_t ** 0.5 * model_output
            pred_epsilon = alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
            pred_noised_sample = alpha_prod_s.sqrt() * pred_original_sample + beta_prod_s.sqrt() * pred_epsilon
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample` or `v_prediction` for `TCDScheduler`.')
        if eta > 0:
            if self.step_index != self.num_inference_steps - 1:
                noise = randn_tensor(model_output.shape, generator=generator, device=model_output.device, dtype=pred_noised_sample.dtype)
                prev_sample = (alpha_prod_t_prev / alpha_prod_s).sqrt() * pred_noised_sample + (1 - alpha_prod_t_prev / alpha_prod_s).sqrt() * noise
            else: prev_sample = pred_noised_sample
        else: prev_sample = pred_noised_sample
        self._step_index += 1
        if not return_dict: return (prev_sample, pred_noised_sample)
        return TCDSchedulerOutput(prev_sample=prev_sample, pred_noised_sample=pred_noised_sample)
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        self.alphas_cumprod = self.alphas_cumprod.to(device=original_samples.device)
        alphas_cumprod = self.alphas_cumprod.to(dtype=original_samples.dtype)
        timesteps = timesteps.to(original_samples.device)
        sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(original_samples.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(original_samples.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        noisy_samples = sqrt_alpha_prod * original_samples + sqrt_one_minus_alpha_prod * noise
        return noisy_samples
    def get_velocity(self, sample: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        self.alphas_cumprod = self.alphas_cumprod.to(device=sample.device)
        alphas_cumprod = self.alphas_cumprod.to(dtype=sample.dtype)
        timesteps = timesteps.to(sample.device)
        sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(sample.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(sample.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        velocity = sqrt_alpha_prod * noise - sqrt_one_minus_alpha_prod * sample
        return velocity
    def __len__(self): return self.config.num_train_timesteps
    def previous_timestep(self, timestep):
        if self.custom_timesteps or self.num_inference_steps:
            index = (self.timesteps == timestep).nonzero(as_tuple=True)[0][0]
            if index == self.timesteps.shape[0] - 1: prev_t = torch.tensor(-1)
            else: prev_t = self.timesteps[index + 1]
        else: prev_t = timestep - 1
        return prev_t
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
