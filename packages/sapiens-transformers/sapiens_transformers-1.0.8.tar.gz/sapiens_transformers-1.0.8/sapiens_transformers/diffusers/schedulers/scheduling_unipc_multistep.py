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
from ..utils import deprecate, is_scipy_available
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
class UniPCMultistepScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    _compatibles = [e.name for e in KarrasDiffusionSchedulers]
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1000, beta_start: float=0.0001, beta_end: float=0.02, beta_schedule: str='linear', trained_betas: Optional[Union[np.ndarray, List[float]]]=None,
    solver_order: int=2, prediction_type: str='epsilon', thresholding: bool=False, dynamic_thresholding_ratio: float=0.995, sample_max_value: float=1.0, predict_x0: bool=True,
    solver_type: str='bh2', lower_order_final: bool=True, disable_corrector: List[int]=[], solver_p: SchedulerMixin=None, use_karras_sigmas: Optional[bool]=False,
    use_exponential_sigmas: Optional[bool]=False, use_beta_sigmas: Optional[bool]=False, use_flow_sigmas: Optional[bool]=False, flow_shift: Optional[float]=1.0,
    timestep_spacing: str='linspace', steps_offset: int=0, final_sigmas_type: Optional[str]='zero', rescale_betas_zero_snr: bool=False):
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
        self.alpha_t = torch.sqrt(self.alphas_cumprod)
        self.sigma_t = torch.sqrt(1 - self.alphas_cumprod)
        self.lambda_t = torch.log(self.alpha_t) - torch.log(self.sigma_t)
        self.sigmas = ((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5
        self.init_noise_sigma = 1.0
        if solver_type not in ['bh1', 'bh2']:
            if solver_type in ['midpoint', 'heun', 'logrho']: self.register_to_config(solver_type='bh2')
            else: raise NotImplementedError(f'{solver_type} is not implemented for {self.__class__}')
        self.predict_x0 = predict_x0
        self.num_inference_steps = None
        timesteps = np.linspace(0, num_train_timesteps - 1, num_train_timesteps, dtype=np.float32)[::-1].copy()
        self.timesteps = torch.from_numpy(timesteps)
        self.model_outputs = [None] * solver_order
        self.timestep_list = [None] * solver_order
        self.lower_order_nums = 0
        self.disable_corrector = disable_corrector
        self.solver_p = solver_p
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
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        if self.config.timestep_spacing == 'linspace': timesteps = np.linspace(0, self.config.num_train_timesteps - 1, num_inference_steps + 1).round()[::-1][:-1].copy().astype(np.int64)
        elif self.config.timestep_spacing == 'leading':
            step_ratio = self.config.num_train_timesteps // (num_inference_steps + 1)
            timesteps = (np.arange(0, num_inference_steps + 1) * step_ratio).round()[::-1][:-1].copy().astype(np.int64)
            timesteps += self.config.steps_offset
        elif self.config.timestep_spacing == 'trailing':
            step_ratio = self.config.num_train_timesteps / num_inference_steps
            timesteps = np.arange(self.config.num_train_timesteps, 0, -step_ratio).round().copy().astype(np.int64)
            timesteps -= 1
        else: raise ValueError(f"{self.config.timestep_spacing} is not supported. Please make sure to choose one of 'linspace', 'leading' or 'trailing'.")
        sigmas = np.array(((1 - self.alphas_cumprod) / self.alphas_cumprod) ** 0.5)
        if self.config.use_karras_sigmas:
            log_sigmas = np.log(sigmas)
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_karras(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas]).round()
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = sigmas[-1]
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        elif self.config.use_exponential_sigmas:
            log_sigmas = np.log(sigmas)
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_exponential(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = sigmas[-1]
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        elif self.config.use_beta_sigmas:
            log_sigmas = np.log(sigmas)
            sigmas = np.flip(sigmas).copy()
            sigmas = self._convert_to_beta(in_sigmas=sigmas, num_inference_steps=num_inference_steps)
            timesteps = np.array([self._sigma_to_t(sigma, log_sigmas) for sigma in sigmas])
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = sigmas[-1]
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        elif self.config.use_flow_sigmas:
            alphas = np.linspace(1, 1 / self.config.num_train_timesteps, num_inference_steps + 1)
            sigmas = 1.0 - alphas
            sigmas = np.flip(self.config.flow_shift * sigmas / (1 + (self.config.flow_shift - 1) * sigmas))[:-1].copy()
            timesteps = (sigmas * self.config.num_train_timesteps).copy()
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = sigmas[-1]
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        else:
            sigmas = np.interp(timesteps, np.arange(0, len(sigmas)), sigmas)
            if self.config.final_sigmas_type == 'sigma_min': sigma_last = ((1 - self.alphas_cumprod[0]) / self.alphas_cumprod[0]) ** 0.5
            elif self.config.final_sigmas_type == 'zero': sigma_last = 0
            else: raise ValueError(f"`final_sigmas_type` must be one of 'zero', or 'sigma_min', but got {self.config.final_sigmas_type}")
            sigmas = np.concatenate([sigmas, [sigma_last]]).astype(np.float32)
        self.sigmas = torch.from_numpy(sigmas)
        self.timesteps = torch.from_numpy(timesteps).to(device=device, dtype=torch.int64)
        self.num_inference_steps = len(timesteps)
        self.model_outputs = [None] * self.config.solver_order
        self.lower_order_nums = 0
        self.last_sample = None
        if self.solver_p: self.solver_p.set_timesteps(self.num_inference_steps, device=device)
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
        if self.predict_x0:
            if self.config.prediction_type == 'epsilon': x0_pred = (sample - sigma_t * model_output) / alpha_t
            elif self.config.prediction_type == 'sample': x0_pred = model_output
            elif self.config.prediction_type == 'v_prediction': x0_pred = alpha_t * sample - sigma_t * model_output
            elif self.config.prediction_type == 'flow_prediction':
                sigma_t = self.sigmas[self.step_index]
                x0_pred = sample - sigma_t * model_output
            else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, `v_prediction`, or `flow_prediction` for the UniPCMultistepScheduler.')
            if self.config.thresholding: x0_pred = self._threshold_sample(x0_pred)
            return x0_pred
        elif self.config.prediction_type == 'epsilon': return model_output
        elif self.config.prediction_type == 'sample':
            epsilon = (sample - alpha_t * model_output) / sigma_t
            return epsilon
        elif self.config.prediction_type == 'v_prediction':
            epsilon = alpha_t * model_output + sigma_t * sample
            return epsilon
        else: raise ValueError(f'prediction_type given as {self.config.prediction_type} must be one of `epsilon`, `sample`, or `v_prediction` for the UniPCMultistepScheduler.')
    def multistep_uni_p_bh_update(self, model_output: torch.Tensor, *args, sample: torch.Tensor=None, order: int=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        prev_timestep = args[0] if len(args) > 0 else kwargs.pop('prev_timestep', None)
        if sample is None:
            if len(args) > 1: sample = args[1]
            else: raise ValueError(' missing `sample` as a required keyward argument')
        if order is None:
            if len(args) > 2: order = args[2]
            else: raise ValueError(' missing `order` as a required keyward argument')
        if prev_timestep is not None: deprecate('prev_timestep', '1.0.0', 'Passing `prev_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        model_output_list = self.model_outputs
        s0 = self.timestep_list[-1]
        m0 = model_output_list[-1]
        x = sample
        if self.solver_p:
            x_t = self.solver_p.step(model_output, s0, x).prev_sample
            return x_t
        sigma_t, sigma_s0 = (self.sigmas[self.step_index + 1], self.sigmas[self.step_index])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        h = lambda_t - lambda_s0
        device = sample.device
        rks = []
        D1s = []
        for i in range(1, order):
            si = self.step_index - i
            mi = model_output_list[-(i + 1)]
            alpha_si, sigma_si = self._sigma_to_alpha_sigma_t(self.sigmas[si])
            lambda_si = torch.log(alpha_si) - torch.log(sigma_si)
            rk = (lambda_si - lambda_s0) / h
            rks.append(rk)
            D1s.append((mi - m0) / rk)
        rks.append(1.0)
        rks = torch.tensor(rks, device=device)
        R = []
        b = []
        hh = -h if self.predict_x0 else h
        h_phi_1 = torch.expm1(hh)
        h_phi_k = h_phi_1 / hh - 1
        factorial_i = 1
        if self.config.solver_type == 'bh1': B_h = hh
        elif self.config.solver_type == 'bh2': B_h = torch.expm1(hh)
        else: raise NotImplementedError()
        for i in range(1, order + 1):
            R.append(torch.pow(rks, i - 1))
            b.append(h_phi_k * factorial_i / B_h)
            factorial_i *= i + 1
            h_phi_k = h_phi_k / hh - 1 / factorial_i
        R = torch.stack(R)
        b = torch.tensor(b, device=device)
        if len(D1s) > 0:
            D1s = torch.stack(D1s, dim=1)
            if order == 2: rhos_p = torch.tensor([0.5], dtype=x.dtype, device=device)
            else: rhos_p = torch.linalg.solve(R[:-1, :-1], b[:-1]).to(device).to(x.dtype)
        else: D1s = None
        if self.predict_x0:
            x_t_ = sigma_t / sigma_s0 * x - alpha_t * h_phi_1 * m0
            if D1s is not None: pred_res = torch.einsum('k,bkc...->bc...', rhos_p, D1s)
            else: pred_res = 0
            x_t = x_t_ - alpha_t * B_h * pred_res
        else:
            x_t_ = alpha_t / alpha_s0 * x - sigma_t * h_phi_1 * m0
            if D1s is not None: pred_res = torch.einsum('k,bkc...->bc...', rhos_p, D1s)
            else: pred_res = 0
            x_t = x_t_ - sigma_t * B_h * pred_res
        x_t = x_t.to(x.dtype)
        return x_t
    def multistep_uni_c_bh_update(self, this_model_output: torch.Tensor, *args, last_sample: torch.Tensor=None, this_sample: torch.Tensor=None, order: int=None, **kwargs) -> torch.Tensor:
        """Returns:"""
        this_timestep = args[0] if len(args) > 0 else kwargs.pop('this_timestep', None)
        if last_sample is None:
            if len(args) > 1: last_sample = args[1]
            else: raise ValueError(' missing`last_sample` as a required keyward argument')
        if this_sample is None:
            if len(args) > 2: this_sample = args[2]
            else: raise ValueError(' missing`this_sample` as a required keyward argument')
        if order is None:
            if len(args) > 3: order = args[3]
            else: raise ValueError(' missing`order` as a required keyward argument')
        if this_timestep is not None: deprecate('this_timestep', '1.0.0', 'Passing `this_timestep` is deprecated and has no effect as model output conversion is now handled via an internal counter `self.step_index`')
        model_output_list = self.model_outputs
        m0 = model_output_list[-1]
        x = last_sample
        x_t = this_sample
        model_t = this_model_output
        sigma_t, sigma_s0 = (self.sigmas[self.step_index], self.sigmas[self.step_index - 1])
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = self._sigma_to_alpha_sigma_t(sigma_s0)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        h = lambda_t - lambda_s0
        device = this_sample.device
        rks = []
        D1s = []
        for i in range(1, order):
            si = self.step_index - (i + 1)
            mi = model_output_list[-(i + 1)]
            alpha_si, sigma_si = self._sigma_to_alpha_sigma_t(self.sigmas[si])
            lambda_si = torch.log(alpha_si) - torch.log(sigma_si)
            rk = (lambda_si - lambda_s0) / h
            rks.append(rk)
            D1s.append((mi - m0) / rk)
        rks.append(1.0)
        rks = torch.tensor(rks, device=device)
        R = []
        b = []
        hh = -h if self.predict_x0 else h
        h_phi_1 = torch.expm1(hh)
        h_phi_k = h_phi_1 / hh - 1
        factorial_i = 1
        if self.config.solver_type == 'bh1': B_h = hh
        elif self.config.solver_type == 'bh2': B_h = torch.expm1(hh)
        else: raise NotImplementedError()
        for i in range(1, order + 1):
            R.append(torch.pow(rks, i - 1))
            b.append(h_phi_k * factorial_i / B_h)
            factorial_i *= i + 1
            h_phi_k = h_phi_k / hh - 1 / factorial_i
        R = torch.stack(R)
        b = torch.tensor(b, device=device)
        if len(D1s) > 0: D1s = torch.stack(D1s, dim=1)
        else: D1s = None
        if order == 1: rhos_c = torch.tensor([0.5], dtype=x.dtype, device=device)
        else: rhos_c = torch.linalg.solve(R, b).to(device).to(x.dtype)
        if self.predict_x0:
            x_t_ = sigma_t / sigma_s0 * x - alpha_t * h_phi_1 * m0
            if D1s is not None: corr_res = torch.einsum('k,bkc...->bc...', rhos_c[:-1], D1s)
            else: corr_res = 0
            D1_t = model_t - m0
            x_t = x_t_ - alpha_t * B_h * (corr_res + rhos_c[-1] * D1_t)
        else:
            x_t_ = alpha_t / alpha_s0 * x - sigma_t * h_phi_1 * m0
            if D1s is not None: corr_res = torch.einsum('k,bkc...->bc...', rhos_c[:-1], D1s)
            else: corr_res = 0
            D1_t = model_t - m0
            x_t = x_t_ - sigma_t * B_h * (corr_res + rhos_c[-1] * D1_t)
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
    def step(self, model_output: torch.Tensor, timestep: Union[int, torch.Tensor], sample: torch.Tensor, return_dict: bool=True) -> Union[SchedulerOutput, Tuple]:
        """Returns:"""
        if self.num_inference_steps is None: raise ValueError("Number of inference steps is 'None', you need to run 'set_timesteps' after creating the scheduler")
        if self.step_index is None: self._init_step_index(timestep)
        use_corrector = self.step_index > 0 and self.step_index - 1 not in self.disable_corrector and (self.last_sample is not None)
        model_output_convert = self.convert_model_output(model_output, sample=sample)
        if use_corrector: sample = self.multistep_uni_c_bh_update(this_model_output=model_output_convert, last_sample=self.last_sample, this_sample=sample, order=self.this_order)
        for i in range(self.config.solver_order - 1):
            self.model_outputs[i] = self.model_outputs[i + 1]
            self.timestep_list[i] = self.timestep_list[i + 1]
        self.model_outputs[-1] = model_output_convert
        self.timestep_list[-1] = timestep
        if self.config.lower_order_final: this_order = min(self.config.solver_order, len(self.timesteps) - self.step_index)
        else: this_order = self.config.solver_order
        self.this_order = min(this_order, self.lower_order_nums + 1)
        assert self.this_order > 0
        self.last_sample = sample
        prev_sample = self.multistep_uni_p_bh_update(model_output=model_output, sample=sample, order=self.this_order)
        if self.lower_order_nums < self.config.solver_order: self.lower_order_nums += 1
        self._step_index += 1
        if not return_dict: return (prev_sample,)
        return SchedulerOutput(prev_sample=prev_sample)
    def scale_model_input(self, sample: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """Returns:"""
        return sample
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
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
        alpha_t, sigma_t = self._sigma_to_alpha_sigma_t(sigma)
        noisy_samples = alpha_t * original_samples + sigma_t * noise
        return noisy_samples
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
