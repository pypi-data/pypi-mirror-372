"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .trainer_pt_utils import LayerWiseDummyOptimizer, LayerWiseDummyScheduler
from torch.optim.lr_scheduler import LambdaLR, ReduceLROnPlateau
from typing import Callable, Iterable, Optional, Tuple, Union
from .utils.versions import require_version
from .trainer_utils import SchedulerType
from torch.optim import Optimizer
from functools import partial
from .utils import logging
from torch import nn
import warnings
import torch
import math
logger = logging.get_logger(__name__)
def _get_constant_lambda(_=None): return 1
def get_constant_schedule(optimizer: Optimizer, last_epoch: int = -1): return LambdaLR(optimizer, _get_constant_lambda, last_epoch=last_epoch)
def get_reduce_on_plateau_schedule(optimizer: Optimizer, **kwargs): return ReduceLROnPlateau(optimizer, **kwargs)
def _get_constant_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1.0, num_warmup_steps))
    return 1.0
def get_constant_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, last_epoch: int = -1):
    lr_lambda = partial(_get_constant_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps)
    return LambdaLR(optimizer, lr_lambda, last_epoch=last_epoch)
def _get_linear_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int, num_training_steps: int):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    return max(0.0, float(num_training_steps - current_step) / float(max(1, num_training_steps - num_warmup_steps)))
def get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps, last_epoch=-1):
    lr_lambda = partial(_get_linear_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
def _get_cosine_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int, num_training_steps: int, num_cycles: float):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
    return max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))
def get_cosine_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_cycles: float = 0.5, last_epoch: int = -1):
    lr_lambda = partial(_get_cosine_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps, num_cycles=num_cycles)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
def _get_cosine_with_hard_restarts_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int, num_training_steps: int, num_cycles: int):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
    if progress >= 1.0: return 0.0
    return max(0.0, 0.5 * (1.0 + math.cos(math.pi * ((float(num_cycles) * progress) % 1.0))))
def get_cosine_with_hard_restarts_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_cycles: int = 1, last_epoch: int = -1):
    lr_lambda = partial(_get_cosine_with_hard_restarts_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps, num_cycles=num_cycles)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
def _get_polynomial_decay_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int, num_training_steps: int, lr_end: float, power: float, lr_init: int):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    elif current_step > num_training_steps: return lr_end / lr_init
    else:
        lr_range = lr_init - lr_end
        decay_steps = num_training_steps - num_warmup_steps
        pct_remaining = 1 - (current_step - num_warmup_steps) / decay_steps
        decay = lr_range * pct_remaining**power + lr_end
        return decay / lr_init
def get_polynomial_decay_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps, lr_end=1e-7, power=1.0, last_epoch=-1):
    lr_init = optimizer.defaults["lr"]
    if not (lr_init > lr_end): raise ValueError(f"lr_end ({lr_end}) must be smaller than initial lr ({lr_init})")
    lr_lambda = partial(_get_polynomial_decay_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps, lr_end=lr_end, power=power, lr_init=lr_init)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
def _get_inverse_sqrt_schedule_lr_lambda(current_step: int, *, num_warmup_steps: int, timescale: int = None):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    shift = timescale - num_warmup_steps
    decay = 1.0 / math.sqrt((current_step + shift) / timescale)
    return decay
def get_inverse_sqrt_schedule(optimizer: Optimizer, num_warmup_steps: int, timescale: int = None, last_epoch: int = -1):
    if timescale is None: timescale = num_warmup_steps or 10_000
    lr_lambda = partial(_get_inverse_sqrt_schedule_lr_lambda, num_warmup_steps=num_warmup_steps, timescale=timescale)
    return LambdaLR(optimizer, lr_lambda, last_epoch=last_epoch)
def _get_cosine_schedule_with_warmup_lr_lambda(current_step: int, *, num_warmup_steps: int, num_training_steps: int, num_cycles: float, min_lr_rate: float = 0.0):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
    factor = 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress))
    factor = factor * (1 - min_lr_rate) + min_lr_rate
    return max(0, factor)
def get_cosine_with_min_lr_schedule_with_warmup(optimizer: Optimizer, num_warmup_steps: int, num_training_steps: int, num_cycles: float = 0.5, last_epoch: int = -1, min_lr: float = None, min_lr_rate: float = None):
    if min_lr is not None and min_lr_rate is not None: raise ValueError("Only one of min_lr or min_lr_rate should be set")
    elif min_lr is not None: min_lr_rate = min_lr / optimizer.defaults["lr"]
    elif min_lr_rate is None: raise ValueError("One of min_lr or min_lr_rate should be set through the `lr_scheduler_kwargs`")
    lr_lambda = partial(_get_cosine_schedule_with_warmup_lr_lambda, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps, num_cycles=num_cycles, min_lr_rate=min_lr_rate)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
def _get_wsd_scheduler_lambda(current_step: int, *, num_warmup_steps: int, num_stable_steps: int, num_decay_steps: int, num_cycles: float, min_lr_ratio: float):
    if current_step < num_warmup_steps: return float(current_step) / float(max(1, num_warmup_steps))
    if current_step < num_warmup_steps + num_stable_steps: return 1.0
    if current_step < num_warmup_steps + num_stable_steps + num_decay_steps:
        progress = float(current_step - num_warmup_steps - num_stable_steps) / float(max(1, num_decay_steps))
        value = max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))
        return (1.0 - min_lr_ratio) * value + min_lr_ratio
    return min_lr_ratio
def get_wsd_schedule(optimizer: Optimizer, num_warmup_steps: int, num_stable_steps: int, num_decay_steps: int, min_lr_ratio: float = 0, num_cycles: float = 0.5, last_epoch: int = -1):
    lr_lambda = partial(_get_wsd_scheduler_lambda, num_warmup_steps=num_warmup_steps, num_stable_steps=num_stable_steps, num_decay_steps=num_decay_steps, min_lr_ratio=min_lr_ratio, num_cycles=num_cycles)
    return LambdaLR(optimizer, lr_lambda, last_epoch)
TYPE_TO_SCHEDULER_FUNCTION = {SchedulerType.LINEAR: get_linear_schedule_with_warmup, SchedulerType.COSINE: get_cosine_schedule_with_warmup, SchedulerType.COSINE_WITH_RESTARTS: get_cosine_with_hard_restarts_schedule_with_warmup,
SchedulerType.POLYNOMIAL: get_polynomial_decay_schedule_with_warmup, SchedulerType.CONSTANT: get_constant_schedule, SchedulerType.CONSTANT_WITH_WARMUP: get_constant_schedule_with_warmup, SchedulerType.INVERSE_SQRT: get_inverse_sqrt_schedule,
SchedulerType.REDUCE_ON_PLATEAU: get_reduce_on_plateau_schedule, SchedulerType.COSINE_WITH_MIN_LR: get_cosine_with_min_lr_schedule_with_warmup, SchedulerType.WARMUP_STABLE_DECAY: get_wsd_schedule}
def get_scheduler(name: Union[str, SchedulerType], optimizer: Optimizer, num_warmup_steps: Optional[int] = None, num_training_steps: Optional[int] = None, scheduler_specific_kwargs: Optional[dict] = None):
    name = SchedulerType(name)
    schedule_func = TYPE_TO_SCHEDULER_FUNCTION[name]
    if optimizer is not None and isinstance(optimizer, LayerWiseDummyOptimizer):
        optimizer_dict = optimizer.optimizer_dict
        scheduler_dict = {}
        for param in optimizer_dict.keys(): scheduler_dict[param] = get_scheduler(name, optimizer=optimizer_dict[param], num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps)
        def scheduler_hook(param): scheduler_dict[param].step()
        for param in optimizer_dict.keys():
            if param.requires_grad: param.register_post_accumulate_grad_hook(scheduler_hook)
        return LayerWiseDummyScheduler(optimizer_dict=optimizer_dict, lr=optimizer.defaults["lr"])
    if name == SchedulerType.CONSTANT: return schedule_func(optimizer)
    if scheduler_specific_kwargs is None: scheduler_specific_kwargs = {}
    if name == SchedulerType.REDUCE_ON_PLATEAU: return schedule_func(optimizer, **scheduler_specific_kwargs)
    if num_warmup_steps is None: raise ValueError(f"{name} requires `num_warmup_steps`, please provide that argument.")
    if name == SchedulerType.CONSTANT_WITH_WARMUP: return schedule_func(optimizer, num_warmup_steps=num_warmup_steps)
    if name == SchedulerType.INVERSE_SQRT: return schedule_func(optimizer, num_warmup_steps=num_warmup_steps)
    if name == SchedulerType.WARMUP_STABLE_DECAY: return schedule_func(optimizer, num_warmup_steps=num_warmup_steps, **scheduler_specific_kwargs)
    if num_training_steps is None: raise ValueError(f"{name} requires `num_training_steps`, please provide that argument.")
    return schedule_func(optimizer, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps, **scheduler_specific_kwargs)
class AdamW(Optimizer):
    def __init__(self, params: Iterable[nn.parameter.Parameter], lr: float = 1e-3, betas: Tuple[float, float] = (0.9, 0.999), eps: float = 1e-6, weight_decay: float = 0.0, correct_bias: bool = True, no_deprecation_warning: bool = False):
        if not no_deprecation_warning: warnings.warn("This implementation of AdamW is deprecated and will be removed in a future version. Use the PyTorch implementation torch.optim.AdamW instead, or set `no_deprecation_warning=True` to disable this warning", FutureWarning)
        require_version("torch>=1.5.0")
        if lr < 0.0: raise ValueError(f"Invalid learning rate: {lr} - should be >= 0.0")
        if not 0.0 <= betas[0] < 1.0: raise ValueError(f"Invalid beta parameter: {betas[0]} - should be in [0.0, 1.0)")
        if not 0.0 <= betas[1] < 1.0: raise ValueError(f"Invalid beta parameter: {betas[1]} - should be in [0.0, 1.0)")
        if not 0.0 <= eps: raise ValueError(f"Invalid epsilon value: {eps} - should be >= 0.0")
        defaults = {"lr": lr, "betas": betas, "eps": eps, "weight_decay": weight_decay, "correct_bias": correct_bias}
        super().__init__(params, defaults)
    @torch.no_grad()
    def step(self, closure: Callable = None):
        loss = None
        if closure is not None: loss = closure()
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None: continue
                grad = p.grad
                if grad.is_sparse: raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(p)
                    state["exp_avg_sq"] = torch.zeros_like(p)
                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                beta1, beta2 = group["betas"]
                state["step"] += 1
                exp_avg.mul_(beta1).add_(grad, alpha=(1.0 - beta1))
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1.0 - beta2)
                denom = exp_avg_sq.sqrt().add_(group["eps"])
                step_size = group["lr"]
                if group["correct_bias"]:
                    bias_correction1 = 1.0 - beta1 ** state["step"]
                    bias_correction2 = 1.0 - beta2 ** state["step"]
                    step_size = step_size * math.sqrt(bias_correction2) / bias_correction1
                p.addcdiv_(exp_avg, denom, value=-step_size)
                if group["weight_decay"] > 0.0: p.add_(p, alpha=(-group["lr"] * group["weight_decay"]))
        return loss
class Adafactor(Optimizer):
    def __init__(self, params, lr=None, eps=(1e-30, 1e-3), clip_threshold=1.0, decay_rate=-0.8, beta1=None, weight_decay=0.0, scale_parameter=True, relative_step=True, warmup_init=False):
        require_version("torch>=1.5.0")
        if lr is not None and relative_step: raise ValueError("Cannot combine manual `lr` and `relative_step=True` options")
        if warmup_init and not relative_step: raise ValueError("`warmup_init=True` requires `relative_step=True`")
        defaults = {"lr": lr, "eps": eps, "clip_threshold": clip_threshold, "decay_rate": decay_rate, "beta1": beta1, "weight_decay": weight_decay, "scale_parameter": scale_parameter, "relative_step": relative_step, "warmup_init": warmup_init}
        super().__init__(params, defaults)
    @staticmethod
    def _get_lr(param_group, param_state):
        rel_step_sz = param_group["lr"]
        if param_group["relative_step"]:
            min_step = 1e-6 * param_state["step"] if param_group["warmup_init"] else 1e-2
            rel_step_sz = min(min_step, 1.0 / math.sqrt(param_state["step"]))
        param_scale = 1.0
        if param_group["scale_parameter"]: param_scale = max(param_group["eps"][1], param_state["RMS"])
        return param_scale * rel_step_sz
    @staticmethod
    def _get_options(param_group, param_shape):
        factored = len(param_shape) >= 2
        use_first_moment = param_group["beta1"] is not None
        return factored, use_first_moment
    @staticmethod
    def _rms(tensor): return tensor.norm(2) / (tensor.numel() ** 0.5)
    @staticmethod
    def _approx_sq_grad(exp_avg_sq_row, exp_avg_sq_col):
        r_factor = (exp_avg_sq_row / exp_avg_sq_row.mean(dim=-1, keepdim=True)).rsqrt_().unsqueeze(-1)
        c_factor = exp_avg_sq_col.unsqueeze(-2).rsqrt()
        return torch.mul(r_factor, c_factor)
    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None: loss = closure()
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None: continue
                grad = p.grad
                if grad.dtype in {torch.float16, torch.bfloat16}: grad = grad.float()
                if grad.is_sparse: raise RuntimeError("Adafactor does not support sparse gradients.")
                state = self.state[p]
                grad_shape = grad.shape
                factored, use_first_moment = self._get_options(group, grad_shape)
                if len(state) == 0:
                    state["step"] = 0
                    if use_first_moment: state["exp_avg"] = torch.zeros_like(grad)
                    if factored:
                        state["exp_avg_sq_row"] = torch.zeros(grad_shape[:-1]).to(grad)
                        state["exp_avg_sq_col"] = torch.zeros(grad_shape[:-2] + grad_shape[-1:]).to(grad)
                    else: state["exp_avg_sq"] = torch.zeros_like(grad)
                    state["RMS"] = 0
                else:
                    if use_first_moment: state["exp_avg"] = state["exp_avg"].to(grad)
                    if factored:
                        state["exp_avg_sq_row"] = state["exp_avg_sq_row"].to(grad)
                        state["exp_avg_sq_col"] = state["exp_avg_sq_col"].to(grad)
                    else: state["exp_avg_sq"] = state["exp_avg_sq"].to(grad)
                p_data_fp32 = p
                if p.dtype in {torch.float16, torch.bfloat16}: p_data_fp32 = p_data_fp32.float()
                state["step"] += 1
                state["RMS"] = self._rms(p_data_fp32)
                lr = self._get_lr(group, state)
                beta2t = 1.0 - math.pow(state["step"], group["decay_rate"])
                update = (grad**2) + group["eps"][0]
                if factored:
                    exp_avg_sq_row = state["exp_avg_sq_row"]
                    exp_avg_sq_col = state["exp_avg_sq_col"]
                    exp_avg_sq_row.mul_(beta2t).add_(update.mean(dim=-1), alpha=(1.0 - beta2t))
                    exp_avg_sq_col.mul_(beta2t).add_(update.mean(dim=-2), alpha=(1.0 - beta2t))
                    update = self._approx_sq_grad(exp_avg_sq_row, exp_avg_sq_col)
                    update.mul_(grad)
                else:
                    exp_avg_sq = state["exp_avg_sq"]
                    exp_avg_sq.mul_(beta2t).add_(update, alpha=(1.0 - beta2t))
                    update = exp_avg_sq.rsqrt().mul_(grad)
                update.div_((self._rms(update) / group["clip_threshold"]).clamp_(min=1.0))
                update.mul_(lr)
                if use_first_moment:
                    exp_avg = state["exp_avg"]
                    exp_avg.mul_(group["beta1"]).add_(update, alpha=(1 - group["beta1"]))
                    update = exp_avg
                if group["weight_decay"] != 0: p_data_fp32.add_(p_data_fp32, alpha=(-group["weight_decay"] * lr))
                p_data_fp32.add_(-update)
                if p.dtype in {torch.float16, torch.bfloat16}: p.copy_(p_data_fp32)
        return loss
class AdafactorSchedule(LambdaLR):
    def __init__(self, optimizer, initial_lr=0.0):
        def lr_lambda(_): return initial_lr
        for group in optimizer.param_groups: group["initial_lr"] = initial_lr
        super().__init__(optimizer, lr_lambda)
        for group in optimizer.param_groups: del group["initial_lr"]
    def get_lr(self):
        opt = self.optimizer
        lrs = [opt._get_lr(group, opt.state[group["params"][0]]) for group in opt.param_groups if group["params"][0].grad is not None]
        if len(lrs) == 0: lrs = self.base_lrs
        return lrs
def get_adafactor_schedule(optimizer, initial_lr=0.0): return AdafactorSchedule(optimizer, initial_lr)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
