'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .utils import convert_state_dict_to_diffusers, convert_state_dict_to_peft, deprecate, is_peft_available, is_torch_npu_available, is_torchvision_available, is_transformers_available
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from .models import UNet2DConditionModel
from .schedulers import SchedulerMixin
import numpy as np
import contextlib
import random
import torch
import math
import copy
import gc
if is_transformers_available():
    import sapiens_transformers
    if sapiens_transformers.integrations.deepspeed.is_deepspeed_zero3_enabled(): import deepspeed
if is_peft_available(): from peft import set_peft_model_state_dict
if is_torchvision_available(): from torchvision import transforms
if is_torch_npu_available(): import torch_npu
def set_seed(seed: int):
    """Returns:"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if is_torch_npu_available(): torch.npu.manual_seed_all(seed)
    else: torch.cuda.manual_seed_all(seed)
def compute_snr(noise_scheduler, timesteps):
    """Returns:"""
    alphas_cumprod = noise_scheduler.alphas_cumprod
    sqrt_alphas_cumprod = alphas_cumprod ** 0.5
    sqrt_one_minus_alphas_cumprod = (1.0 - alphas_cumprod) ** 0.5
    sqrt_alphas_cumprod = sqrt_alphas_cumprod.to(device=timesteps.device)[timesteps].float()
    while len(sqrt_alphas_cumprod.shape) < len(timesteps.shape): sqrt_alphas_cumprod = sqrt_alphas_cumprod[..., None]
    alpha = sqrt_alphas_cumprod.expand(timesteps.shape)
    sqrt_one_minus_alphas_cumprod = sqrt_one_minus_alphas_cumprod.to(device=timesteps.device)[timesteps].float()
    while len(sqrt_one_minus_alphas_cumprod.shape) < len(timesteps.shape): sqrt_one_minus_alphas_cumprod = sqrt_one_minus_alphas_cumprod[..., None]
    sigma = sqrt_one_minus_alphas_cumprod.expand(timesteps.shape)
    snr = (alpha / sigma) ** 2
    return snr
def resolve_interpolation_mode(interpolation_type: str):
    """Returns:"""
    if not is_torchvision_available(): raise ImportError('Please make sure to install `torchvision` to be able to use the `resolve_interpolation_mode()` function.')
    if interpolation_type == 'bilinear': interpolation_mode = transforms.InterpolationMode.BILINEAR
    elif interpolation_type == 'bicubic': interpolation_mode = transforms.InterpolationMode.BICUBIC
    elif interpolation_type == 'box': interpolation_mode = transforms.InterpolationMode.BOX
    elif interpolation_type == 'nearest': interpolation_mode = transforms.InterpolationMode.NEAREST
    elif interpolation_type == 'nearest_exact': interpolation_mode = transforms.InterpolationMode.NEAREST_EXACT
    elif interpolation_type == 'hamming': interpolation_mode = transforms.InterpolationMode.HAMMING
    elif interpolation_type == 'lanczos': interpolation_mode = transforms.InterpolationMode.LANCZOS
    else: raise ValueError(f'The given interpolation mode {interpolation_type} is not supported. Currently supported interpolation modes are `bilinear`, `bicubic`, `box`, `nearest`, `nearest_exact`, `hamming`, and `lanczos`.')
    return interpolation_mode
def compute_dream_and_update_latents(unet: UNet2DConditionModel, noise_scheduler: SchedulerMixin, timesteps: torch.Tensor, noise: torch.Tensor, noisy_latents: torch.Tensor, target: torch.Tensor,
encoder_hidden_states: torch.Tensor, dream_detail_preservation: float=1.0) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor]]:
    """Returns:"""
    alphas_cumprod = noise_scheduler.alphas_cumprod.to(timesteps.device)[timesteps, None, None, None]
    sqrt_one_minus_alphas_cumprod = (1.0 - alphas_cumprod) ** 0.5
    dream_lambda = sqrt_one_minus_alphas_cumprod ** dream_detail_preservation
    pred = None
    with torch.no_grad(): pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample
    _noisy_latents, _target = (None, None)
    if noise_scheduler.config.prediction_type == 'epsilon':
        predicted_noise = pred
        delta_noise = (noise - predicted_noise).detach()
        delta_noise.mul_(dream_lambda)
        _noisy_latents = noisy_latents.add(sqrt_one_minus_alphas_cumprod * delta_noise)
        _target = target.add(delta_noise)
    elif noise_scheduler.config.prediction_type == 'v_prediction': raise NotImplementedError('DREAM has not been implemented for v-prediction')
    else: raise ValueError(f'Unknown prediction type {noise_scheduler.config.prediction_type}')
    return (_noisy_latents, _target)
def unet_lora_state_dict(unet: UNet2DConditionModel) -> Dict[str, torch.Tensor]:
    """Returns:"""
    lora_state_dict = {}
    for name, module in unet.named_modules():
        if hasattr(module, 'set_lora_layer'):
            lora_layer = getattr(module, 'lora_layer')
            if lora_layer is not None:
                current_lora_layer_sd = lora_layer.state_dict()
                for lora_layer_matrix_name, lora_param in current_lora_layer_sd.items(): lora_state_dict[f'{name}.lora.{lora_layer_matrix_name}'] = lora_param
    return lora_state_dict
def cast_training_params(model: Union[torch.nn.Module, List[torch.nn.Module]], dtype=torch.float32):
    """Args:"""
    if not isinstance(model, list): model = [model]
    for m in model:
        for param in m.parameters():
            if param.requires_grad: param.data = param.to(dtype)
def _set_state_dict_into_text_encoder(lora_state_dict: Dict[str, torch.Tensor], prefix: str, text_encoder: torch.nn.Module):
    """Args:"""
    text_encoder_state_dict = {f"{k.replace(prefix, '')}": v for k, v in lora_state_dict.items() if k.startswith(prefix)}
    text_encoder_state_dict = convert_state_dict_to_peft(convert_state_dict_to_diffusers(text_encoder_state_dict))
    set_peft_model_state_dict(text_encoder, text_encoder_state_dict, adapter_name='default')
def compute_density_for_timestep_sampling(weighting_scheme: str, batch_size: int, logit_mean: float=None, logit_std: float=None, mode_scale: float=None):
    if weighting_scheme == 'logit_normal':
        u = torch.normal(mean=logit_mean, std=logit_std, size=(batch_size,), device='cpu')
        u = torch.nn.functional.sigmoid(u)
    elif weighting_scheme == 'mode':
        u = torch.rand(size=(batch_size,), device='cpu')
        u = 1 - u - mode_scale * (torch.cos(math.pi * u / 2) ** 2 - 1 + u)
    else: u = torch.rand(size=(batch_size,), device='cpu')
    return u
def compute_loss_weighting_for_sapi_imagegen(weighting_scheme: str, sigmas=None):
    if weighting_scheme == 'sigma_sqrt': weighting = (sigmas ** (-2.0)).float()
    elif weighting_scheme == 'cosmap':
        bot = 1 - 2 * sigmas + 2 * sigmas ** 2
        weighting = 2 / (math.pi * bot)
    else: weighting = torch.ones_like(sigmas)
    return weighting
def compute_loss_weighting_for_sd3(weighting_scheme: str, sigmas=None):
    if weighting_scheme == 'sigma_sqrt': weighting = (sigmas ** (-2.0)).float()
    elif weighting_scheme == 'cosmap':
        bot = 1 - 2 * sigmas + 2 * sigmas ** 2
        weighting = 2 / (math.pi * bot)
    else: weighting = torch.ones_like(sigmas)
    return weighting
def free_memory():
    gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    elif torch.backends.mps.is_available(): torch.mps.empty_cache()
    elif is_torch_npu_available(): torch_npu.npu.empty_cache()
class EMAModel:
    def __init__(self, parameters: Iterable[torch.nn.Parameter], decay: float=0.9999, min_decay: float=0.0, update_after_step: int=0, use_ema_warmup: bool=False,
    inv_gamma: Union[float, int]=1.0, power: Union[float, int]=2 / 3, foreach: bool=False, model_cls: Optional[Any]=None, model_config: Dict[str, Any]=None, **kwargs):
        """Args:"""
        if isinstance(parameters, torch.nn.Module):
            deprecation_message = 'Passing a `torch.nn.Module` to `ExponentialMovingAverage` is deprecated. Please pass the parameters of the module instead.'
            deprecate('passing a `torch.nn.Module` to `ExponentialMovingAverage`', '1.0.0', deprecation_message, standard_warn=False)
            parameters = parameters.parameters()
            use_ema_warmup = True
        if kwargs.get('max_value', None) is not None:
            deprecation_message = 'The `max_value` argument is deprecated. Please use `decay` instead.'
            deprecate('max_value', '1.0.0', deprecation_message, standard_warn=False)
            decay = kwargs['max_value']
        if kwargs.get('min_value', None) is not None:
            deprecation_message = 'The `min_value` argument is deprecated. Please use `min_decay` instead.'
            deprecate('min_value', '1.0.0', deprecation_message, standard_warn=False)
            min_decay = kwargs['min_value']
        parameters = list(parameters)
        self.shadow_params = [p.clone().detach() for p in parameters]
        if kwargs.get('device', None) is not None:
            deprecation_message = 'The `device` argument is deprecated. Please use `to` instead.'
            deprecate('device', '1.0.0', deprecation_message, standard_warn=False)
            self.to(device=kwargs['device'])
        self.temp_stored_params = None
        self.decay = decay
        self.min_decay = min_decay
        self.update_after_step = update_after_step
        self.use_ema_warmup = use_ema_warmup
        self.inv_gamma = inv_gamma
        self.power = power
        self.optimization_step = 0
        self.cur_decay_value = None
        self.foreach = foreach
        self.model_cls = model_cls
        self.model_config = model_config
    @classmethod
    def from_pretrained(cls, path, model_cls, foreach=False) -> 'EMAModel':
        _, ema_kwargs = model_cls.from_config(path, return_unused_kwargs=True)
        model = model_cls.from_pretrained(path)
        ema_model = cls(model.parameters(), model_cls=model_cls, model_config=model.config, foreach=foreach)
        ema_model.load_state_dict(ema_kwargs)
        return ema_model
    def save_pretrained(self, path):
        if self.model_cls is None: raise ValueError('`save_pretrained` can only be used if `model_cls` was defined at __init__.')
        if self.model_config is None: raise ValueError('`save_pretrained` can only be used if `model_config` was defined at __init__.')
        model = self.model_cls.from_config(self.model_config)
        state_dict = self.state_dict()
        state_dict.pop('shadow_params', None)
        model.register_to_config(**state_dict)
        self.copy_to(model.parameters())
        model.save_pretrained(path)
    def get_decay(self, optimization_step: int) -> float:
        step = max(0, optimization_step - self.update_after_step - 1)
        if step <= 0: return 0.0
        if self.use_ema_warmup: cur_decay_value = 1 - (1 + step / self.inv_gamma) ** (-self.power)
        else: cur_decay_value = (1 + step) / (10 + step)
        cur_decay_value = min(cur_decay_value, self.decay)
        cur_decay_value = max(cur_decay_value, self.min_decay)
        return cur_decay_value
    @torch.no_grad()
    def step(self, parameters: Iterable[torch.nn.Parameter]):
        if isinstance(parameters, torch.nn.Module):
            deprecation_message = 'Passing a `torch.nn.Module` to `ExponentialMovingAverage.step` is deprecated. Please pass the parameters of the module instead.'
            deprecate('passing a `torch.nn.Module` to `ExponentialMovingAverage.step`', '1.0.0', deprecation_message, standard_warn=False)
            parameters = parameters.parameters()
        parameters = list(parameters)
        self.optimization_step += 1
        decay = self.get_decay(self.optimization_step)
        self.cur_decay_value = decay
        one_minus_decay = 1 - decay
        context_manager = contextlib.nullcontext()
        if self.foreach:
            if is_transformers_available() and sapiens_transformers.integrations.deepspeed.is_deepspeed_zero3_enabled(): context_manager = deepspeed.zero.GatheredParameters(parameters, modifier_rank=None)
            with context_manager:
                params_grad = [param for param in parameters if param.requires_grad]
                s_params_grad = [s_param for s_param, param in zip(self.shadow_params, parameters) if param.requires_grad]
                if len(params_grad) < len(parameters): torch._foreach_copy_([s_param for s_param, param in zip(self.shadow_params, parameters) if not param.requires_grad], [param for param in parameters if not param.requires_grad], non_blocking=True)
                torch._foreach_sub_(s_params_grad, torch._foreach_sub(s_params_grad, params_grad), alpha=one_minus_decay)
        else:
            for s_param, param in zip(self.shadow_params, parameters):
                if is_transformers_available() and sapiens_transformers.integrations.deepspeed.is_deepspeed_zero3_enabled(): context_manager = deepspeed.zero.GatheredParameters(param, modifier_rank=None)
                with context_manager:
                    if param.requires_grad: s_param.sub_(one_minus_decay * (s_param - param))
                    else: s_param.copy_(param)
    def copy_to(self, parameters: Iterable[torch.nn.Parameter]) -> None:
        """Args:"""
        parameters = list(parameters)
        if self.foreach: torch._foreach_copy_([param.data for param in parameters], [s_param.to(param.device).data for s_param, param in zip(self.shadow_params, parameters)])
        else:
            for s_param, param in zip(self.shadow_params, parameters): param.data.copy_(s_param.to(param.device).data)
    def pin_memory(self) -> None: self.shadow_params = [p.pin_memory() for p in self.shadow_params]
    def to(self, device=None, dtype=None, non_blocking=False) -> None:
        """Args:"""
        self.shadow_params = [p.to(device=device, dtype=dtype, non_blocking=non_blocking) if p.is_floating_point() else p.to(device=device, non_blocking=non_blocking) for p in self.shadow_params]
    def state_dict(self) -> dict: return {'decay': self.decay, 'min_decay': self.min_decay, 'optimization_step': self.optimization_step, 'update_after_step': self.update_after_step,
    'use_ema_warmup': self.use_ema_warmup, 'inv_gamma': self.inv_gamma, 'power': self.power, 'shadow_params': self.shadow_params}
    def store(self, parameters: Iterable[torch.nn.Parameter]) -> None:
        """Args:"""
        self.temp_stored_params = [param.detach().cpu().clone() for param in parameters]
    def restore(self, parameters: Iterable[torch.nn.Parameter]) -> None:
        """Args:"""
        if self.temp_stored_params is None: raise RuntimeError('This ExponentialMovingAverage has no `store()`ed weights to `restore()`')
        if self.foreach: torch._foreach_copy_([param.data for param in parameters], [c_param.data for c_param in self.temp_stored_params])
        else:
            for c_param, param in zip(self.temp_stored_params, parameters): param.data.copy_(c_param.data)
        self.temp_stored_params = None
    def load_state_dict(self, state_dict: dict) -> None:
        """Args:"""
        state_dict = copy.deepcopy(state_dict)
        self.decay = state_dict.get('decay', self.decay)
        if self.decay < 0.0 or self.decay > 1.0: raise ValueError('Decay must be between 0 and 1')
        self.min_decay = state_dict.get('min_decay', self.min_decay)
        if not isinstance(self.min_decay, float): raise ValueError('Invalid min_decay')
        self.optimization_step = state_dict.get('optimization_step', self.optimization_step)
        if not isinstance(self.optimization_step, int): raise ValueError('Invalid optimization_step')
        self.update_after_step = state_dict.get('update_after_step', self.update_after_step)
        if not isinstance(self.update_after_step, int): raise ValueError('Invalid update_after_step')
        self.use_ema_warmup = state_dict.get('use_ema_warmup', self.use_ema_warmup)
        if not isinstance(self.use_ema_warmup, bool): raise ValueError('Invalid use_ema_warmup')
        self.inv_gamma = state_dict.get('inv_gamma', self.inv_gamma)
        if not isinstance(self.inv_gamma, (float, int)): raise ValueError('Invalid inv_gamma')
        self.power = state_dict.get('power', self.power)
        if not isinstance(self.power, (float, int)): raise ValueError('Invalid power')
        shadow_params = state_dict.get('shadow_params', None)
        if shadow_params is not None:
            self.shadow_params = shadow_params
            if not isinstance(self.shadow_params, list): raise ValueError('shadow_params must be a list')
            if not all((isinstance(p, torch.Tensor) for p in self.shadow_params)): raise ValueError('shadow_params must all be Tensors')
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
