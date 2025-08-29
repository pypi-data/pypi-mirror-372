'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import Union
import torch
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.torch_utils import randn_tensor
from ..scheduling_utils import SchedulerMixin
class ScoreSdeVpScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps=2000, beta_min=0.1, beta_max=20, sampling_eps=0.001):
        self.sigmas = None
        self.discrete_sigmas = None
        self.timesteps = None
    def set_timesteps(self, num_inference_steps, device: Union[str, torch.device]=None):
        """Args:"""
        self.timesteps = torch.linspace(1, self.config.sampling_eps, num_inference_steps, device=device)
    def step_pred(self, score, x, t, generator=None):
        """Args:"""
        if self.timesteps is None: raise ValueError("`self.timesteps` is not set, you need to run 'set_timesteps' after creating the scheduler")
        log_mean_coeff = -0.25 * t ** 2 * (self.config.beta_max - self.config.beta_min) - 0.5 * t * self.config.beta_min
        std = torch.sqrt(1.0 - torch.exp(2.0 * log_mean_coeff))
        std = std.flatten()
        while len(std.shape) < len(score.shape): std = std.unsqueeze(-1)
        score = -score / std
        dt = -1.0 / len(self.timesteps)
        beta_t = self.config.beta_min + t * (self.config.beta_max - self.config.beta_min)
        beta_t = beta_t.flatten()
        while len(beta_t.shape) < len(x.shape): beta_t = beta_t.unsqueeze(-1)
        drift = -0.5 * beta_t * x
        diffusion = torch.sqrt(beta_t)
        drift = drift - diffusion ** 2 * score
        x_mean = x + drift * dt
        noise = randn_tensor(x.shape, layout=x.layout, generator=generator, device=x.device, dtype=x.dtype)
        x = x_mean + diffusion * math.sqrt(-dt) * noise
        return (x, x_mean)
    def __len__(self): return self.config.num_train_timesteps
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
