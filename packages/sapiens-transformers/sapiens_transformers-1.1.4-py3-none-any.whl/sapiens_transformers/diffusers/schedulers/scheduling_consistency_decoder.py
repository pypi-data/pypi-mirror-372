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
@dataclass
class ConsistencyDecoderSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
class ConsistencyDecoderScheduler(SchedulerMixin, ConfigMixin):
    order = 1
    @register_to_config
    def __init__(self, num_train_timesteps: int=1024, sigma_data: float=0.5):
        betas = betas_for_alpha_bar(num_train_timesteps)
        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        self.sqrt_alphas_cumprod = torch.sqrt(alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - alphas_cumprod)
        sigmas = torch.sqrt(1.0 / alphas_cumprod - 1)
        sqrt_recip_alphas_cumprod = torch.sqrt(1.0 / alphas_cumprod)
        self.c_skip = sqrt_recip_alphas_cumprod * sigma_data ** 2 / (sigmas ** 2 + sigma_data ** 2)
        self.c_out = sigmas * sigma_data / (sigmas ** 2 + sigma_data ** 2) ** 0.5
        self.c_in = sqrt_recip_alphas_cumprod / (sigmas ** 2 + sigma_data ** 2) ** 0.5
    def set_timesteps(self, num_inference_steps: Optional[int]=None, device: Union[str, torch.device]=None):
        if num_inference_steps != 2: raise ValueError('Currently more than 2 inference steps are not supported.')
        self.timesteps = torch.tensor([1008, 512], dtype=torch.long, device=device)
        self.sqrt_alphas_cumprod = self.sqrt_alphas_cumprod.to(device)
        self.sqrt_one_minus_alphas_cumprod = self.sqrt_one_minus_alphas_cumprod.to(device)
        self.c_skip = self.c_skip.to(device)
        self.c_out = self.c_out.to(device)
        self.c_in = self.c_in.to(device)
    @property
    def init_noise_sigma(self): return self.sqrt_one_minus_alphas_cumprod[self.timesteps[0]]
    def scale_model_input(self, sample: torch.Tensor, timestep: Optional[int]=None) -> torch.Tensor:
        """Returns:"""
        return sample * self.c_in[timestep]
    def step(self, model_output: torch.Tensor, timestep: Union[float, torch.Tensor], sample: torch.Tensor, generator: Optional[torch.Generator]=None,
    return_dict: bool=True) -> Union[ConsistencyDecoderSchedulerOutput, Tuple]:
        """Returns:"""
        x_0 = self.c_out[timestep] * model_output + self.c_skip[timestep] * sample
        timestep_idx = torch.where(self.timesteps == timestep)[0]
        if timestep_idx == len(self.timesteps) - 1: prev_sample = x_0
        else:
            noise = randn_tensor(x_0.shape, generator=generator, dtype=x_0.dtype, device=x_0.device)
            prev_sample = self.sqrt_alphas_cumprod[self.timesteps[timestep_idx + 1]].to(x_0.dtype) * x_0 + self.sqrt_one_minus_alphas_cumprod[self.timesteps[timestep_idx + 1]].to(x_0.dtype) * noise
        if not return_dict: return (prev_sample,)
        return ConsistencyDecoderSchedulerOutput(prev_sample=prev_sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
