'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import Callable, List, Optional, Tuple, Union
import numpy as np
import torch
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import deprecate, is_scipy_available
from ..utils.torch_utils import randn_tensor
from .scheduling_utils import KarrasDiffusionSchedulers, SchedulerMixin, SchedulerOutput
if is_scipy_available():
    import scipy.stats
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
class SASolverScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    predictor_order: int=2, corrector_order: int=2, prediction_type: str='epsilon', tau_func: Optional[Callable]=None, thresholding: bool=False, dynamic_thresholding_ratio: float=0.995,
    sample_max_value: float=1.0, algorithm_type: str='data_prediction', lower_order_final: bool=True, use_karras_sigmas: Optional[bool]=False, use_exponential_sigmas: Optional[bool]=False,
    use_beta_sigmas: Optional[bool]=False, use_flow_sigmas: Optional[bool]=False, flow_shift: Optional[float]=1.0, lambda_min_clipped: float=-float('inf'), variance_type: Optional[str]=None,
    timestep_spacing: str='linspace', steps_offset: int=0):
        if self.config.use_beta_sigmas and (not is_scipy_available()): raise ImportError('Make sure to install scipy if you want to use beta sigmas.')
        if sum([self.config.use_beta_sigmas, self.config.use_exponential_sigmas, self.config.use_karras_sigmas]) > 1: raise ValueError('Only one of `config.use_beta_sigmas`, `config.use_exponential_sigmas`, `config.use_karras_sigmas` can be used.')
        if trained_betas is not None: self.betas = torch.tensor(trained_betas, dtype=torch.float32)
        elif beta_schedule == 'linear': self.betas = torch.linspace(beta_start, beta_end, num_train_timesteps, dtype=torch.float32)
        elif beta_schedule == 'scaled_linear': self.betas = torch.linspace(beta_start ** 0.5, beta_end ** 0.5, num_train_timesteps, dtype=torch.float32) ** 2
        elif beta_schedule == 'squaredcos_cap_v2': self.betas = betas_for_alpha_bar(num_train_timesteps)
        else: raise NotImplementedError(f'{beta_schedule} is not implemented for {self.__class__}')
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alpha_t = torch.sqrt(self.alphas_cumprod)
        self.sigma_t = torch.sqrt(1 - self.alphas_cumprod)
        self.lambda_t = torch.log(self.alpha_t) - torch.log(self.sigma_t)
        self.sigmas = ((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5
        self.init_noise_sigma = 1.0
        if algorithm_type not in ['data_prediction', 'noise_prediction']: raise NotImplementedError(f'{algorithm_type} is not implemented for {self.__class__}')
        self.num_inference_steps = None
        timesteps = np.linspace(0, num_train_timesteps - 1, num_train_timesteps, dtype=np.float32)[::-1].copy()
        self.timesteps = torch.from_numpy(timesteps)
        self.timestep_list = [None] * max(predictor_order, corrector_order - 1)
        self.model_outputs = [None] * max(predictor_order, corrector_order - 1)
        if tau_func is None: self.tau_func = lambda t: 1 if t >= 200 and t <= 800 else 0
        else: self.tau_func = tau_func
        self.predict_x0 = algorithm_type == 'data_prediction'
        self.lower_order_nums = 0
        self.last_sample = None
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
    def set_timesteps(self, num_inference_steps: int=None, device: Union[str, torch.device]=None):
        """Args:"""
        clipped_idx = torch.searchsorted(torch.flip(self.lambda_t, [0]), self.config.lambda_min_clipped)
        last_timestep = (self.config.num_train_timesteps - clipped_idx).numpy().item()
        if self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, last_timestep - 1, num_inference_steps + 1).round()[::-1][:-1].copy().astype(np.int64)
        elif self.config.timestep_spacing == 'leading':
            step_ratio = last_timestep // (num_inference_steps + 1)
            timesteps = (np.arange(0, num_inference_steps + 1) * step_ratio).round()[::-1][:-1].copy().astype(np.int64)
            timesteps += self.config.steps_offset
        elif self.config.timestep_spacing == 'trailing':
            step_ratio = self.config.num_train_timesteps / num_inference_steps
            timesteps = np.arange(last_timestep, 0, -step_ratio).round().copy().astype(np.int64)
            timesteps -= 1
        else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
        sigmas = np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5)
        log_sigmas = np.log(sigmas)
        if self.config.use_karras_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_karras(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas]).round()
            sigmas = np.concatenate([sigmas, sigmas[-1:]]).astype(np.float32)
        elif self.config.use_exponential_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_exponential(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            sigmas = np.concatenate([sigmas, sigmas[-1:]]).astype(np.float32)
        elif self.config.use_beta_sigmas:
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_beta(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            sigmas = np.concatenate([sigmas, sigmas[-1:]]).astype(np.float32)
        elif self.config.use_flow_sigmas:
            alphas = np.linspace(1, 1 / self.config.num_train_timesteps, num_inference_steps + 1)
            sigmas = 1.0 - alphas
            sigmas = np.flip(self.config.flow_shift * sigmas / (1 + (self.config.flow_shift - 1) * sigmas))[:-1].copy()
            timesteps = (sigmas * self.config.num_train_timesteps).copy()
            sigmas = np.concatenate([sigmas, sigmas[-1:]]).astype(np.float32)
        else:
            sigmas = np.interp(timesteps, np.arange(0, len(sigmas)), sigmas)
            sigma_last = ((1 - self.alphas_cumprod[0]) / self.alphas_cumprod[0]) ** 0.5
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        self.sigmas = torch.from_numpy(sigmas)
        self.timesteps = torch.from_numpy(timesteps).to(device=device, dtype=torch.int64)
        self.num_inference_steps = len(timesteps)
        self.model_outputs = [None] * max(self.config.predictor_order, self.config.corrector_order - 1)
        self.lower_order_nums = 0
        self.last_sample = None
        self._step_index = None
        self._begin_index = None
        self.sigmas = self.sigmas.to('cpu')
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
        if self.config.use_flow_sigmas:
            alpha_t = 1 - sigma
            sigma_t = sigma
        else:
            alpha_t = 1 / (sigma ** 2 + 1) ** 0.5
            sigma_t = sigma * alpha_t
        return (alpha_t, sigma_t)
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
    def convert_model_output(self, model_output: torch.Tensor, *args, sample: torch.Tensor=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        timestep = args[0] if len(args) > 0 else kwargs.pop('timestep', None)
        if sample is None:
            if len(args) > 1: sample = args[1]
            else: raise ValueError('missing `sample` as a required keyward argument')
        if timestep is not None: deprecate('timesteps', '1.0.0', 'Passing `timesteps` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        sigma = self.sigmas[self.step_index]
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
        if self.config.algorithm_type in ['data_prediction']:
            if self.config.prediction_type == 'epsilon':
                if self.config.variance_type in ['learned', 'learned_range']: model_output = model_output[:, :3]
                x0_pred = (sample - sigma_t * model_output) / alpha_t
            elif self.config.prediction_type == 'sample': x0_pred = model_output
            elif self.config.prediction_type == 'v_prediction': x0_pred = alpha_t * sample - sigma_t * model_output
            elif self.config.prediction_type == 'flow_prediction':
                sigma_t = self.sigmas[self.step_index]
                x0_pred = sample - sigma_t * model_output
            else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, `v_prediction`, or `flow_prediction` for the SASolverScheduler.')
            if self.config.thresholding: x0_pred = self._threshold_sample(x0_pred)
            return x0_pred
        elif self.config.algorithm_type in ['noise_prediction']:
            if self.config.prediction_type == 'epsilon':
                if self.config.variance_type in ['learned', 'learned_range']: epsilon = model_output[:, :3]
                else: epsilon = model_output
            elif self.config.prediction_type == 'sample': epsilon = (sample - alpha_t * model_output) / sigma_t
            elif self.config.prediction_type == 'v_prediction': epsilon = alpha_t * model_output + sigma_t * sample
            else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, or `v_prediction` for the SASolverScheduler.')
            if self.config.thresholding:
                alpha_t, sigma_t = (self.alpha_t[timestep], self.sigma_t[timestep])
                x0_pred = (sample - sigma_t * epsilon) / alpha_t
                x0_pred = self._threshold_sample(x0_pred)
                epsilon = (sample - alpha_t * x0_pred) / sigma_t
            return epsilon
    def get_coefficients_exponential_negative(self, order, interval_start, interval_end):
        assert order in [0, 1, 2, 3], 'order is only supported for 0, 1, 2 and 3'
        if order == 0: return torch.exp(-interval_end) * (torch.exp(interval_end - interval_start) - 1)
        elif order == 1: return torch.exp(-interval_end) * ((interval_start + 1) * torch.exp(interval_end - interval_start) - (interval_end + 1))
        elif order == 2: return torch.exp(-interval_end) * ((interval_start ** 2 + 2 * interval_start + 2) * torch.exp(interval_end - interval_start) - (interval_end ** 2 + 2 * interval_end + 2))
        elif order == 3: return torch.exp(-interval_end) * ((interval_start ** 3 + 3 * interval_start ** 2 + 6 * interval_start + 6) * torch.exp(interval_end - interval_start) - (interval_end ** 3 + 3 * interval_end ** 2 + 6 * interval_end + 6))
    def get_coefficients_exponential_positive(self, order, interval_start, interval_end, tau):
        assert order in [0, 1, 2, 3], 'order is only supported for 0, 1, 2 and 3'
        interval_end_cov = (1 + tau ** 2) * interval_end
        interval_start_cov = (1 + tau ** 2) * interval_start
        if order == 0: return torch.exp(interval_end_cov) * (1 - torch.exp(-(interval_end_cov - interval_start_cov))) / (1 + tau ** 2)
        elif order == 1: return torch.exp(interval_end_cov) * (interval_end_cov - 1 - (interval_start_cov - 1) * torch.exp(-(interval_end_cov - interval_start_cov))) / (1 + tau ** 2) ** 2
        elif order == 2: return torch.exp(interval_end_cov) * (interval_end_cov ** 2 - 2 * interval_end_cov + 2 - (interval_start_cov ** 2 - 2 * interval_start_cov + 2) * torch.exp(-(interval_end_cov - interval_start_cov))) / (1 + tau ** 2) ** 3
        elif order == 3: return torch.exp(interval_end_cov) * (interval_end_cov ** 3 - 3 * interval_end_cov ** 2 + 6 * interval_end_cov - 6 - (interval_start_cov ** 3 - 3 * interval_start_cov ** 2 + 6 * interval_start_cov - 6) * torch.exp(-(interval_end_cov - interval_start_cov))) / (1 + tau ** 2) ** 4
    def lagrange_polynomial_coefficient(self, order, lambda_list):
        assert order in [0, 1, 2, 3]
        assert order == len(lambda_list) - 1
        if order == 0: return [[1]]
        elif order == 1: return [[1 / (lambda_list[0] - lambda_list[1]), -lambda_list[1] / (lambda_list[0] - lambda_list[1])], [1 / (lambda_list[1] - lambda_list[0]), -lambda_list[0] / (lambda_list[1] - lambda_list[0])]]
        elif order == 2:
            denominator1 = (lambda_list[0] - lambda_list[1]) * (lambda_list[0] - lambda_list[2])
            denominator2 = (lambda_list[1] - lambda_list[0]) * (lambda_list[1] - lambda_list[2])
            denominator3 = (lambda_list[2] - lambda_list[0]) * (lambda_list[2] - lambda_list[1])
            return [[1 / denominator1, (-lambda_list[1] - lambda_list[2]) / denominator1, lambda_list[1] * lambda_list[2] / denominator1], [1 / denominator2, (-lambda_list[0] - lambda_list[2]) / denominator2, lambda_list[0] * lambda_list[2] / denominator2], [1 / denominator3, (-lambda_list[0] - lambda_list[1]) / denominator3, lambda_list[0] * lambda_list[1] / denominator3]]
        elif order == 3:
            denominator1 = (lambda_list[0] - lambda_list[1]) * (lambda_list[0] - lambda_list[2]) * (lambda_list[0] - lambda_list[3])
            denominator2 = (lambda_list[1] - lambda_list[0]) * (lambda_list[1] - lambda_list[2]) * (lambda_list[1] - lambda_list[3])
            denominator3 = (lambda_list[2] - lambda_list[0]) * (lambda_list[2] - lambda_list[1]) * (lambda_list[2] - lambda_list[3])
            denominator4 = (lambda_list[3] - lambda_list[0]) * (lambda_list[3] - lambda_list[1]) * (lambda_list[3] - lambda_list[2])
            return [[1 / denominator1, (-lambda_list[1] - lambda_list[2] - lambda_list[3]) / denominator1, (lambda_list[1] * lambda_list[2] + lambda_list[1] * lambda_list[3] + lambda_list[2] * lambda_list[3]) / denominator1, -lambda_list[1] * lambda_list[2] * lambda_list[3] / denominator1], [1 / denominator2, (-lambda_list[0] - lambda_list[2] - lambda_list[3]) / denominator2, (lambda_list[0] * lambda_list[2] + lambda_list[0] * lambda_list[3] + lambda_list[2] * lambda_list[3]) / denominator2, -lambda_list[0] * lambda_list[2] * lambda_list[3] / denominator2], [1 / denominator3, (-lambda_list[0] - lambda_list[1] - lambda_list[3]) / denominator3, (lambda_list[0] * lambda_list[1] + lambda_list[0] * lambda_list[3] + lambda_list[1] * lambda_list[3]) / denominator3, -lambda_list[0] * lambda_list[1] * lambda_list[3] / denominator3], [1 / denominator4, (-lambda_list[0] - lambda_list[1] - lambda_list[2]) / denominator4, (lambda_list[0] * lambda_list[1] + lambda_list[0] * lambda_list[2] + lambda_list[1] * lambda_list[2]) / denominator4, -lambda_list[0] * lambda_list[1] * lambda_list[2] / denominator4]]
    def get_coefficients_fn(self, order, interval_start, interval_end, lambda_list, tau):
        assert order in [1, 2, 3, 4]
        assert order == len(lambda_list), 'the length of lambda list must be equal to the order'
        coefficients = []
        lagrange_coefficient = self.lagrange_polynomial_coefficient(order - 1, lambda_list)
        for i in range(order):
            coefficient = 0
            for j in range(order):
                if self.predict_x0: coefficient += lagrange_coefficient[i][j] * self.get_coefficients_exponential_positive(order - 1 - j, interval_start, interval_end, tau)
                else: coefficient += lagrange_coefficient[i][j] * self.get_coefficients_exponential_negative(order - 1 - j, interval_start, interval_end)
            coefficients.append(coefficient)
        assert len(coefficients) == order, 'the length of coefficients does not match the order'
        return coefficients
    def stochastic_adams_bashforth_update(self, model_output: torch.Tensor, *args, sample: torch.Tensor, noise: torch.Tensor, order: int, tau: torch.Tensor, **kwargs) -> torch.Tensor:
        """Returns:"""
        prev_timestep = args[0] if len(args) > 0 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 1: sample = args[1]
            else: raise ValueError(' missing `sample` as a required keyward argument')
        if noise is None:
            if len(args) > 2: noise = args[2]
            else: raise ValueError(' missing `noise` as a required keyward argument')
        if order is None:
            if len(args) > 3: order = args[3]
            else: raise ValueError(' missing `order` as a required keyward argument')
        if tau is None:
            if len(args) > 4: tau = args[4]
            else: raise ValueError(' missing `tau` as a required keyward argument')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        model_output_list = self.model_outputs
        sigma_t, sigma_s0 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        gradient_part = torch.zeros_like(sample)
        h = lambda_t - lambda_s0
        lambda_list = []
        for i in range(order):
            si = self.step_index - i
            alpha_si, sigma_si = self._sigma_to_alpha_sigma_t(self.sigmas[si])
            lambda_si = torch.log(alpha_si) - torch.log(sigma_si)
            lambda_list.append(lambda_si)
        gradient_coefficients = self.get_coefficients_fn(order, lambda_s0, lambda_t, lambda_list, tau)
        x = sample
        if self.predict_x0:
            if order == 2:
                temp_sigma = self.sigmas[self.step_index - 1]
                temp_alpha_s, temp_sigma_s = self._sigma_to_alpha_sigma_t(temp_sigma)
                temp_lambda_s = torch.log(temp_alpha_s) - torch.log(temp_sigma_s)
                gradient_coefficients[0] += 1.0 * torch.exp((1 + tau ** 2) * lambda_t) * (h ** 2 / 2 - (h * (1 + tau ** 2) - 1 + torch.exp((1 + tau ** 2) * -h)) / (1 + tau ** 2) ** 2) / (lambda_s0 - temp_lambda_s)
                gradient_coefficients[1] -= 1.0 * torch.exp((1 + tau ** 2) * lambda_t) * (h ** 2 / 2 - (h * (1 + tau ** 2) - 1 + torch.exp((1 + tau ** 2) * -h)) / (1 + tau ** 2) ** 2) / (lambda_s0 - temp_lambda_s)
        for i in range(order):
            if self.predict_x0: gradient_part += (1 + tau ** 2) * sigma_t * torch.exp(-tau ** 2 * lambda_t) * gradient_coefficients[i] * model_output_list[-(i + 1)]
            else: gradient_part += -(1 + tau ** 2) * alpha_t * gradient_coefficients[i] * model_output_list[-(i + 1)]
        if self.predict_x0: noise_part = sigma_t * torch.sqrt(1 - torch.exp(-2 * tau ** 2 * h)) * noise
        else: noise_part = tau * sigma_t * torch.sqrt(torch.exp(2 * h) - 1) * noise
        if self.predict_x0: x_t = torch.exp(-tau ** 2 * h) * (sigma_t / sigma_s0) * x + gradient_part + noise_part
        else: x_t = alpha_t / alpha_s0 * x + gradient_part + noise_part
        x_t = x_t.to(x.dtype)
        return x_t
    def stochastic_adams_moulton_update(self, this_model_output: torch.Tensor, *args, last_sample: torch.Tensor, last_noise: torch.Tensor, this_sample: torch.Tensor,
    order: int, tau: torch.Tensor, **kwargs) -> torch.Tensor:
        """Returns:"""
        this_timestep = args[0] if len(args) > 0 else kwargs.pop('this_timestep', None)
        if last_sample is None:
            if len(args) > 1: last_sample = args[1]
            else: raise ValueError(' missing`last_sample` as a required keyward argument')
        if last_noise is None:
            if len(args) > 2: last_noise = args[2]
            else: raise ValueError(' missing`last_noise` as a required keyward argument')
        if this_sample is None:
            if len(args) > 3: this_sample = args[3]
            else: raise ValueError(' missing`this_sample` as a required keyward argument')
        if order is None:
            if len(args) > 4: order = args[4]
            else: raise ValueError(' missing`order` as a required keyward argument')
        if tau is None:
            if len(args) > 5: tau = args[5]
            else: raise ValueError(' missing`tau` as a required keyward argument')
        if this_timestep is not None: deprecate('this_timestep', '1.0.0', 'Passing `this_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        model_output_list = self.model_outputs
        sigma_t, sigma_s0 = (self.sigmas[self.step_index], self.sigmas[self.step_index - 1])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        gradient_part = torch.zeros_like(this_sample)
        h = lambda_t - lambda_s0
        lambda_list = []
        for i in range(order):
            si = self.step_index - i
            alpha_si, sigma_si = self._sigma_to_alpha_sigma_t(self.sigmas[si])
            lambda_si = torch.log(alpha_si) - torch.log(sigma_si)
            lambda_list.append(lambda_si)
        model_prev_list = model_output_list + [this_model_output]
        gradient_coefficients = self.get_coefficients_fn(order, lambda_s0, lambda_t, lambda_list, tau)
        x = last_sample
        if self.predict_x0:
            if order == 2:
                gradient_coefficients[0] += 1.0 * torch.exp((1 + tau ** 2) * lambda_t) * (h / 2 - (h * (1 + tau ** 2) - 1 + torch.exp((1 + tau ** 2) * -h)) / ((1 + tau ** 2) ** 2 * h))
                gradient_coefficients[1] -= 1.0 * torch.exp((1 + tau ** 2) * lambda_t) * (h / 2 - (h * (1 + tau ** 2) - 1 + torch.exp((1 + tau ** 2) * -h)) / ((1 + tau ** 2) ** 2 * h))
        for i in range(order):
            if self.predict_x0: gradient_part += (1 + tau ** 2) * sigma_t * torch.exp(-tau ** 2 * lambda_t) * gradient_coefficients[i] * model_prev_list[-(i + 1)]
            else: gradient_part += -(1 + tau ** 2) * alpha_t * gradient_coefficients[i] * model_prev_list[-(i + 1)]
        if self.predict_x0: noise_part = sigma_t * torch.sqrt(1 - torch.exp(-2 * tau ** 2 * h)) * last_noise
        else: noise_part = tau * sigma_t * torch.sqrt(torch.exp(2 * h) - 1) * last_noise
        if self.predict_x0: x_t = torch.exp(-tau ** 2 * h) * (sigma_t / sigma_s0) * x + gradient_part + noise_part
        else: x_t = alpha_t / alpha_s0 * x + gradient_part + noise_part
        x_t = x_t.to(x.dtype)
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
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor, generator=None, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.step_index is None: self._init_step_index(timestep)
        use_corrector = self.step_index > 0 and self.last_sample is not None
        model_output_convert = self.convert_model_output(model_output, sample=sample)
        if use_corrector:
            current_tau = self.tau_func(self.timestep_list[-1])
            sample = self.stochastic_adams_moulton_update(this_model_output=model_output_convert, last_sample=self.last_sample, last_noise=self.last_noise, this_sample=sample,
            order=self.this_corrector_order, tau=current_tau)
        for i in range(max(self.config.predictor_order, self.config.corrector_order - 1) - 1):
            self.model_outputs[i] = self.model_outputs[i + 1]
            self.timestep_list[i] = self.timestep_list[i + 1]
        self.model_outputs[-1] = model_output_convert
        self.timestep_list[-1] = timestep
        noise = randn_tensor(model_output.shape, generator=generator, device=model_output.device, dtype=model_output.dtype)
        if self.config.lower_order_final:
            this_predictor_order = min(self.config.predictor_order, len(self.timesteps) - self.step_index)
            this_corrector_order = min(self.config.corrector_order, len(self.timesteps) - self.step_index + 1)
        else:
            this_predictor_order = self.config.predictor_order
            this_corrector_order = self.config.corrector_order
        self.this_predictor_order = min(this_predictor_order, self.lower_order_nums + 1)
        self.this_corrector_order = min(this_corrector_order, self.lower_order_nums + 2)
        assert self.this_predictor_order > 0
        assert self.this_corrector_order > 0
        self.last_sample = sample
        self.last_noise = noise
        current_tau = self.tau_func(self.timestep_list[-1])
        prev_sample = self.stochastic_adams_bashforth_update(model_output=model_output_convert, sample=sample, noise=noise, order=self.this_predictor_order, tau=current_tau)
        if self.lower_order_nums < max(self.config.predictor_order, self.config.corrector_order - 1): self.lower_order_nums += 1
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
    def scale_model_input(self, sample: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """Returns:"""
        return sample
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
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
