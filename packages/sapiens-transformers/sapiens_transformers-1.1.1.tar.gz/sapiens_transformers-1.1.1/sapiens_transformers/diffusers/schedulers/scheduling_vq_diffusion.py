'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np
import torch
import torch.nn.functional as F
from ..configuration_utils import ConfigMixin, register_to_config
from ..utils import BaseOutput
from .scheduling_utils import SchedulerMixin
@dataclass
class VQDiffusionSchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.LongTensor
def index_to_log_onehot(x: torch.LongTensor, num_classes: int) -> torch.Tensor:
    """Returns:"""
    x_onehot = F.one_hot(x, num_classes)
    x_onehot = x_onehot.permute(0, 2, 1)
    log_x = torch.log(x_onehot.float().clamp(min=1e-30))
    return log_x
def gumbel_noised(logits: torch.Tensor, generator: Optional[torch.Generator]) -> torch.Tensor:
    uniform = torch.rand(logits.shape, device=logits.device, generator=generator)
    gumbel_noise = -torch.log(-torch.log(uniform + 1e-30) + 1e-30)
    noised = gumbel_noise + logits
    return noised
def alpha_schedules(num_diffusion_timesteps: int, alpha_cum_start=0.99999, alpha_cum_end=9e-06):
    att = np.arange(0, num_diffusion_timesteps) / (num_diffusion_timesteps - 1) * (alpha_cum_end - alpha_cum_start) + alpha_cum_start
    att = np.concatenate(([1], att))
    at = att[1:] / att[:-1]
    att = np.concatenate((att[1:], [1]))
    return (at, att)
def gamma_schedules(num_diffusion_timesteps: int, gamma_cum_start=9e-06, gamma_cum_end=0.99999):
    ctt = np.arange(0, num_diffusion_timesteps) / (num_diffusion_timesteps - 1) * (gamma_cum_end - gamma_cum_start) + gamma_cum_start
    ctt = np.concatenate(([0], ctt))
    one_minus_ctt = 1 - ctt
    one_minus_ct = one_minus_ctt[1:] / one_minus_ctt[:-1]
    ct = 1 - one_minus_ct
    ctt = np.concatenate((ctt[1:], [0]))
    return (ct, ctt)
class VQDiffusionScheduler(SchedulerMixin, ConfigMixin):
    """Args:"""
    order = 1
    @register_to_config
    def __init__(self, num_vec_classes: int, num_train_timesteps: int=100, alpha_cum_start: float=0.99999, alpha_cum_end: float=9e-06,
    gamma_cum_start: float=9e-06, gamma_cum_end: float=0.99999):
        self.num_embed = num_vec_classes
        self.mask_class = self.num_embed - 1
        at, att = alpha_schedules(num_train_timesteps, alpha_cum_start=alpha_cum_start, alpha_cum_end=alpha_cum_end)
        ct, ctt = gamma_schedules(num_train_timesteps, gamma_cum_start=gamma_cum_start, gamma_cum_end=gamma_cum_end)
        num_non_mask_classes = self.num_embed - 1
        bt = (1 - at - ct) / num_non_mask_classes
        btt = (1 - att - ctt) / num_non_mask_classes
        at = torch.tensor(at.astype('float64'))
        bt = torch.tensor(bt.astype('float64'))
        ct = torch.tensor(ct.astype('float64'))
        log_at = torch.log(at)
        log_bt = torch.log(bt)
        log_ct = torch.log(ct)
        att = torch.tensor(att.astype('float64'))
        btt = torch.tensor(btt.astype('float64'))
        ctt = torch.tensor(ctt.astype('float64'))
        log_cumprod_at = torch.log(att)
        log_cumprod_bt = torch.log(btt)
        log_cumprod_ct = torch.log(ctt)
        self.log_at = log_at.float()
        self.log_bt = log_bt.float()
        self.log_ct = log_ct.float()
        self.log_cumprod_at = log_cumprod_at.float()
        self.log_cumprod_bt = log_cumprod_bt.float()
        self.log_cumprod_ct = log_cumprod_ct.float()
        self.num_inference_steps = None
        self.timesteps = torch.from_numpy(np.arange(0, num_train_timesteps)[::-1].copy())
    def set_timesteps(self, num_inference_steps: int, device: Union[str, torch.device]=None):
        """Args:"""
        self.num_inference_steps = num_inference_steps
        timesteps = np.arange(0, self.num_inference_steps)[::-1].copy()
        self.timesteps = torch.from_numpy(timesteps).to(device)
        self.log_at = self.log_at.to(device)
        self.log_bt = self.log_bt.to(device)
        self.log_ct = self.log_ct.to(device)
        self.log_cumprod_at = self.log_cumprod_at.to(device)
        self.log_cumprod_bt = self.log_cumprod_bt.to(device)
        self.log_cumprod_ct = self.log_cumprod_ct.to(device)
    def step(self, model_output: torch.Tensor, timestep: torch.long, sample: torch.LongTensor, generator: Optional[torch.Generator]=None,
    return_dict: bool=True) -> Union[VQDiffusionSchedulerOutput, Tuple]:
        """Returns:"""
        if timestep == 0: log_p_x_t_min_1 = model_output
        else: log_p_x_t_min_1 = self.q_posterior(model_output, sample, timestep)
        log_p_x_t_min_1 = gumbel_noised(log_p_x_t_min_1, generator)
        x_t_min_1 = log_p_x_t_min_1.argmax(dim=1)
        if not return_dict: return (x_t_min_1,)
        return VQDiffusionSchedulerOutput(prev_sample=x_t_min_1)
    def q_posterior(self, log_p_x_0, x_t, t):
        """Returns:"""
        log_onehot_x_t = index_to_log_onehot(x_t, self.num_embed)
        log_q_x_t_given_x_0 = self.log_Q_t_transitioning_to_known_class(t=t, x_t=x_t, log_onehot_x_t=log_onehot_x_t, cumulative=True)
        log_q_t_given_x_t_min_1 = self.log_Q_t_transitioning_to_known_class(t=t, x_t=x_t, log_onehot_x_t=log_onehot_x_t, cumulative=False)
        q = log_p_x_0 - log_q_x_t_given_x_0
        q_log_sum_exp = torch.logsumexp(q, dim=1, keepdim=True)
        q = q - q_log_sum_exp
        q = self.apply_cumulative_transitions(q, t - 1)
        log_p_x_t_min_1 = q + log_q_t_given_x_t_min_1 + q_log_sum_exp
        return log_p_x_t_min_1
    def log_Q_t_transitioning_to_known_class(self, *, t: torch.int, x_t: torch.LongTensor, log_onehot_x_t: torch.Tensor, cumulative: bool):
        """Returns:"""
        if cumulative:
            a = self.log_cumprod_at[t]
            b = self.log_cumprod_bt[t]
            c = self.log_cumprod_ct[t]
        else:
            a = self.log_at[t]
            b = self.log_bt[t]
            c = self.log_ct[t]
        if not cumulative: log_onehot_x_t_transitioning_from_masked = log_onehot_x_t[:, -1, :].unsqueeze(1)
        log_onehot_x_t = log_onehot_x_t[:, :-1, :]
        log_Q_t = (log_onehot_x_t + a).logaddexp(b)
        mask_class_mask = x_t == self.mask_class
        mask_class_mask = mask_class_mask.unsqueeze(1).expand(-1, self.num_embed - 1, -1)
        log_Q_t[mask_class_mask] = c
        if not cumulative: log_Q_t = torch.cat((log_Q_t, log_onehot_x_t_transitioning_from_masked), dim=1)
        return log_Q_t
    def apply_cumulative_transitions(self, q, t):
        bsz = q.shape[0]
        a = self.log_cumprod_at[t]
        b = self.log_cumprod_bt[t]
        c = self.log_cumprod_ct[t]
        num_latent_pixels = q.shape[2]
        c = c.expand(bsz, 1, num_latent_pixels)
        q = (q + a).logaddexp(b)
        q = torch.cat((q, c), dim=1)
        return q
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
