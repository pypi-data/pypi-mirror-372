'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import SchedulerMixin, SchedulerOutput
class EDMDPMSolverMultistepScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = []
    order = 1
    @register_to_config
    def __init__(self, sigma_min: float=0.002, sigma_max: float=80.0, sigma_data: float=0.5, sigma_schedule: str='karras', num_train_timesteps: int=1000, prediction_type: str='epsilon',
    rho: float=7.0, solver_order: int=2, thresholding: bool=False, dynamic_thresholding_ratio: float=0.995, sample_max_value: float=1.0, algorithm_type: str='dpmsolver++',
    solver_type: str='midpoint', lower_order_final: bool=True, euler_at_final: bool=False, final_sigmas_type: Optional[str]='zero'):
        if algorithm_type not in ['dpmsolver++', 'sde-dpmsolver++']:
            if algorithm_type == 'deis': self.register_to_config(algorithm_type='dpmsolver++')
            else: raise NotImplementedError(f'{algorithm_type} is not implemented for {self.__class__}')
        if solver_type not in ['midpoint', 'heun']:
            if solver_type in ['logrho', 'bh1', 'bh2']: self.register_to_config(solver_type='midpoint')
            else: raise NotImplementedError(f'{solver_type} is not implemented for {self.__class__}')
        if algorithm_type not in ['dpmsolver++', 'sde-dpmsolver++'] and final_sigmas_type == 'zero': raise ValueError(f'`final_sigmas_type` {final_sigmas_type} is not supported for `algorithm_type` {algorithm_type}. Please choose `sigma_min` instead.')
        ramp = torch.linspace(0, 1, num_train_timesteps)
        if sigma_schedule == 'karras': sigmas = self._compute_karras_sigmas(ramp)
        elif sigma_schedule == 'exponential': sigmas = self._compute_exponential_sigmas(ramp)
        self.timesteps = self.precondition_noise(sigmas)
        self.sigmas = torch.cat([sigmas, torch.zeros(1, device=sigmas.device)])
        self.num_inference_steps = None
        self.model_outputs = [None] * solver_order
        self.lower_order_nums = 0
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
    def set_timesteps(self, num_inference_steps: int=None, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        ramp = torch.linspace(0, 1, self.num_inference_steps)
        if self.config.sigma_schedule == 'karras': sigmas = self._compute_karras_sigmas(ramp)
        elif self.config.sigma_schedule == 'exponential': sigmas = self._compute_exponential_sigmas(ramp)
        sigmas = sigmas.to(dtype=torch.float32, device=device)
        self.timesteps = self.precondition_noise(sigmas)
        if self.config.final_sigmas_type == 'sigma_min': sigma_last = self.config.sigma_min
        elif self.config.final_sigmas_type == 'zero': sigma_last = 0
        else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
        self.sigmas = torch.cat([sigmas, torch.tensor([sigma_last], dtype=torch.float32, device=device)])
        self.model_outputs = [None] * self.config.solver_order
        self.lower_order_nums = 0
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
    def _sigma_to_alpha_sigma_t(self, sigma):
        alpha_t = torch.tensor(1)
        sigma_t = sigma
        return (alpha_t, sigma_t)
    def convert_model_output(self, model_output: torch.Tensor, sample: torch.Tensor=None) -> torch.Tensor:
        """Returns:"""
        sigma = self.sigmas[self.step_index]
        x0_pred = self.precondition_outputs(sample, model_output, sigma)
        if self.config.thresholding: x0_pred = self._threshold_sample(x0_pred)
        return x0_pred
    def dpm_solver_first_order_update(self, model_output: torch.Tensor, sample: torch.Tensor=None, noise: Optional[torch.Tensor]=None) -> torch.Tensor:
        """Returns:"""
        sigma_t, sigma_s = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s, sigma_s = self._sigma_to_alpha_sigma_t(sigma_s)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s = torch.log(alpha_s) - torch.log(sigma_s)
        h = lambda_t - lambda_s
        if self.config.algorithm_type == 'dpmsolver++': x_t = sigma_t / sigma_s * sample - alpha_t * (torch.exp(-h) - 1.0) * model_output
        elif self.config.algorithm_type == 'sde-dpmsolver++':
            assert noise is not None
            x_t = sigma_t / sigma_s * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * model_output + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
        return x_t
    def multistep_dpm_solver_second_order_update(self, model_output_list: List[torch.Tensor], sample: torch.Tensor=None, noise: Optional[torch.Tensor]=None) -> torch.Tensor:
        """Returns:"""
        sigma_t, sigma_s0, sigma_s1 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index], self.sigmas[self.step_index - 1])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        alpha_s1, sigma_s1 = self._sigma_to_alpha_sigma_t(sigma_s1)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        lambda_s1 = torch.log(alpha_s1) - torch.log(sigma_s1)
        m0, m1 = (model_output_list[-1], model_output_list[-2])
        h, h_0 = (lambda_t - lambda_s0, lambda_s0 - lambda_s1)
        r0 = h_0 / h
        D0, D1 = (m0, 1.0 / r0 * (m0 - m1))
        if self.config.algorithm_type == 'dpmsolver++':
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s0 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 - 0.5 * (alpha_t * (torch.exp(-h) - 1.0)) * D1
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s0 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 + alpha_t * ((torch.exp(-h) - 1.0) / h + 1.0) * D1
        elif self.config.algorithm_type == 'sde-dpmsolver++':
            assert noise is not None
            if self.config.solver_type == 'midpoint': x_t = sigma_t / sigma_s0 * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * D0 + 0.5 * (alpha_t * (1 - torch.exp(-2.0 * h))) * D1 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
            elif self.config.solver_type == 'heun': x_t = sigma_t / sigma_s0 * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * D0 + alpha_t * ((1.0 - torch.exp(-2.0 * h)) / (-2.0 * h) + 1.0) * D1 + sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h)) * noise
        return x_t
    def multistep_dpm_solver_third_order_update(self, model_output_list: List[torch.Tensor], sample: torch.Tensor=None) -> torch.Tensor:
        """Returns:"""
        sigma_t, sigma_s0, sigma_s1, sigma_s2 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index], self.sigmas[self.step_index - 1], self.sigmas[self.step_index - 2])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        alpha_s1, sigma_s1 = self._sigma_to_alpha_sigma_t(sigma_s1)
        alpha_s2, sigma_s2 = self._sigma_to_alpha_sigma_t(sigma_s2)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        lambda_s1 = torch.log(alpha_s1) - torch.log(sigma_s1)
        lambda_s2 = torch.log(alpha_s2) - torch.log(sigma_s2)
        m0, m1, m2 = (model_output_list[-1], model_output_list[-2], model_output_list[-3])
        h, h_0, h_1 = (lambda_t - lambda_s0, lambda_s0 - lambda_s1, lambda_s1 - lambda_s2)
        r0, r1 = (h_0 / h, h_1 / h)
        D0 = m0
        D1_0, D1_1 = (1.0 / r0 * (m0 - m1), 1.0 / r1 * (m1 - m2))
        D1 = D1_0 + r0 / (r0 + r1) * (D1_0 - D1_1)
        D2 = 1.0 / (r0 + r1) * (D1_0 - D1_1)
        if self.config.algorithm_type == 'dpmsolver++': x_t = sigma_t / sigma_s0 * sample - alpha_t * (torch.exp(-h) - 1.0) * D0 + alpha_t * ((torch.exp(-h) - 1.0) / h + 1.0) * D1 - alpha_t * ((torch.exp(-h) - 1.0 + h) / h ** 2 - 0.5) * D2
        return x_t
    def index_for_timestep(self, timestep, schedule_timesteps=None):
        if schedule_timesteps is None: schedule_timesteps = self.timesteps
        index_candidates = (schedule_timesteps == timestep).nonzero()
        if len(index_candidates) == 0: step_index = len(self.timesteps) - 1
        elif len(index_candidates) > 1: step_index = index_candidates[1].item()
        else: step_index = index_candidates[0].item()
        return step_index
    def _init_step_index(self, timestep):
        if self.begin_index is None:
            if isinstance(timestep, torch.Tensor): timestep = timestep.to(self.timesteps.device)
            self._step_index = self.index_for_timestep(timestep)
        else: self._step_index = self._begin_index
    def step(self, model_output: torch.Tensor, timestep: Union[int, torch.Tensor], sample: torch.Tensor, generator=None, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.step_index is None: self._init_step_index(timestep)
        lower_order_final = self.step_index == len(self.timesteps) - 1 and (self.config.euler_at_final or (self.config.lower_order_final and len(self.timesteps) < 15) or self.config.final_sigmas_type == 'zero')
        lower_order_second = self.step_index == len(self.timesteps) - 2 and self.config.lower_order_final and (len(self.timesteps) < 15)
        model_output = self.convert_model_output(model_output, sample=sample)
        for i in range(self.config.solver_order - 1): self.model_outputs[i] = self.model_outputs[i + 1]
        self.model_outputs[-1] = model_output
        if self.config.algorithm_type == 'sde-dpmsolver++': noise = randn_tensor(model_output.shape, generator=generator, device=model_output.device, dtype=model_output.dtype)
        else: noise = None
        if self.config.solver_order == 1 or self.lower_order_nums < 1 or lower_order_final: prev_sample = self.dpm_solver_first_order_update(model_output, sample=sample, noise=noise)
        elif self.config.solver_order == 2 or self.lower_order_nums < 2 or lower_order_second: prev_sample = self.multistep_dpm_solver_second_order_update(self.model_outputs, sample=sample, noise=noise)
        else: prev_sample = self.multistep_dpm_solver_third_order_update(self.model_outputs, sample=sample)
        if self.lower_order_nums < self.config.solver_order: self.lower_order_nums += 1
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
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
