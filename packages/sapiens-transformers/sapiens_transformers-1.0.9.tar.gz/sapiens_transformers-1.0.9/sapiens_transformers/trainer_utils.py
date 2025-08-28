"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (ExplicitEnum, is_psutil_available, is_tf_available, is_torch_available, is_torch_cuda_available, is_torch_mlu_available,
is_torch_mps_available, is_torch_musa_available, is_torch_npu_available, is_torch_xla_available, is_torch_xpu_available, requires_backends)
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union
import numpy as np
import functools
import threading
import inspect
import random
import time
import copy
import gc
import os
import re
if is_torch_available(): import torch
def seed_worker(_):
    worker_seed = torch.initial_seed() % 2**32
    set_seed(worker_seed)
def enable_full_determinism(seed: int, warn_only: bool = False):
    set_seed(seed)
    if is_torch_available():
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
        os.environ["ASCEND_LAUNCH_BLOCKING"] = "1"
        os.environ["HCCL_DETERMINISTIC"] = "1"
        os.environ["FLASH_ATTENTION_DETERMINISTIC"] = "1"
        torch.use_deterministic_algorithms(True, warn_only=warn_only)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    if is_tf_available():
        import tensorflow as tf
        tf.config.experimental.enable_op_determinism()
def set_seed(seed: int, deterministic: bool = False):
    random.seed(seed)
    np.random.seed(seed)
    if is_torch_available():
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic: torch.use_deterministic_algorithms(True)
    if is_torch_mlu_available(): torch.mlu.manual_seed_all(seed)
    if is_torch_musa_available(): torch.musa.manual_seed_all(seed)
    if is_torch_npu_available(): torch.npu.manual_seed_all(seed)
    if is_torch_xpu_available(): torch.xpu.manual_seed_all(seed)
    if is_tf_available():
        import tensorflow as tf
        tf.random.set_seed(seed)
        if deterministic: tf.config.experimental.enable_op_determinism()
def neftune_post_forward_hook(module, input, output):
    if module.training:
        dims = torch.tensor(output.size(1) * output.size(2))
        mag_norm = module.neftune_noise_alpha / torch.sqrt(dims)
        output = output + torch.zeros_like(output).uniform_(-mag_norm, mag_norm)
    return output
class EvalPrediction:
    def __init__(self, predictions: Union[np.ndarray, Tuple[np.ndarray]], label_ids: Union[np.ndarray, Tuple[np.ndarray]], inputs: Optional[Union[np.ndarray, Tuple[np.ndarray]]] = None):
        self.predictions = predictions
        self.label_ids = label_ids
        self.inputs = inputs
    def __iter__(self):
        if self.inputs is not None: return iter((self.predictions, self.label_ids, self.inputs))
        else: return iter((self.predictions, self.label_ids))
    def __getitem__(self, idx):
        if idx < 0 or idx > 2: raise IndexError("tuple index out of range")
        if idx == 2 and self.inputs is None: raise IndexError("tuple index out of range")
        if idx == 0: return self.predictions
        elif idx == 1: return self.label_ids
        elif idx == 2: return self.inputs
class EvalLoopOutput(NamedTuple):
    predictions: Union[np.ndarray, Tuple[np.ndarray]]
    label_ids: Optional[Union[np.ndarray, Tuple[np.ndarray]]]
    metrics: Optional[Dict[str, float]]
    num_samples: Optional[int]
class PredictionOutput(NamedTuple):
    predictions: Union[np.ndarray, Tuple[np.ndarray]]
    label_ids: Optional[Union[np.ndarray, Tuple[np.ndarray]]]
    metrics: Optional[Dict[str, float]]
class TrainOutput(NamedTuple):
    global_step: int
    training_loss: float
    metrics: Dict[str, float]
PREFIX_CHECKPOINT_DIR = "checkpoint"
_re_checkpoint = re.compile(r"^" + PREFIX_CHECKPOINT_DIR + r"\-(\d+)$")
def get_last_checkpoint(folder):
    content = os.listdir(folder)
    checkpoints = [path for path in content if _re_checkpoint.search(path) is not None and os.path.isdir(os.path.join(folder, path))]
    if len(checkpoints) == 0: return
    return os.path.join(folder, max(checkpoints, key=lambda x: int(_re_checkpoint.search(x).groups()[0])))
class IntervalStrategy(ExplicitEnum):
    NO = "no"
    STEPS = "steps"
    EPOCH = "epoch"
class EvaluationStrategy(ExplicitEnum):
    NO = "no"
    STEPS = "steps"
    EPOCH = "epoch"
class HubStrategy(ExplicitEnum):
    END = "end"
    EVERY_SAVE = "every_save"
    CHECKPOINT = "checkpoint"
    ALL_CHECKPOINTS = "all_checkpoints"
class BestRun(NamedTuple):
    run_id: str
    objective: Union[float, List[float]]
    hyperparameters: Dict[str, Any]
    run_summary: Optional[Any] = None
def default_compute_objective(metrics: Dict[str, float]) -> float:
    metrics = copy.deepcopy(metrics)
    loss = metrics.pop("eval_loss", None)
    _ = metrics.pop("epoch", None)
    speed_metrics = [m for m in metrics.keys() if m.endswith("_runtime") or m.endswith("_per_second") or m.endswith("_compilation_time")]
    for sm in speed_metrics: _ = metrics.pop(sm, None)
    return loss if len(metrics) == 0 else sum(metrics.values())
def default_hp_space_optuna(trial) -> Dict[str, float]:
    from .integrations import is_optuna_available
    assert is_optuna_available(), "This function needs Optuna installed: `pip install optuna`"
    return {"learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True), "num_train_epochs": trial.suggest_int("num_train_epochs", 1, 5), "seed": trial.suggest_int("seed", 1, 40), "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [4, 8, 16, 32, 64])}
def default_hp_space_ray(trial) -> Dict[str, float]:
    from .integrations import is_ray_tune_available
    assert is_ray_tune_available(), "This function needs ray installed: `pip install ray[tune]`"
    from ray import tune
    return {"learning_rate": tune.loguniform(1e-6, 1e-4), "num_train_epochs": tune.choice(list(range(1, 6))), "seed": tune.uniform(1, 40), "per_device_train_batch_size": tune.choice([4, 8, 16, 32, 64])}
def default_hp_space_sigopt(trial):
    return [{"bounds": {"min": 1e-6, "max": 1e-4}, "name": "learning_rate", "type": "double", "transformamtion": "log"}, {"bounds": {"min": 1, "max": 6}, "name": "num_train_epochs", "type": "int"},
    {"bounds": {"min": 1, "max": 40}, "name": "seed", "type": "int"}, {'categorical_values': ['4', '8', '16', '32', '64'], 'name': 'per_device_train_batch_size', 'type': 'categorical'}]
def default_hp_space_wandb(trial) -> Dict[str, float]:
    from .integrations import is_wandb_available
    if not is_wandb_available(): raise ImportError("This function needs wandb installed: `pip install wandb`")
    return {"method": "random", "metric": {"name": "objective", "goal": "minimize"}, "parameters": {"learning_rate": {"distribution": "uniform", "min": 1e-6, "max": 1e-4}, "num_train_epochs": {"distribution": "int_uniform", "min": 1, "max": 6}, "seed": {"distribution": "int_uniform", "min": 1, "max": 40}, "per_device_train_batch_size": {"values": [4, 8, 16, 32, 64]}}}
class HPSearchBackend(ExplicitEnum):
    OPTUNA = "optuna"
    RAY = "ray"
    SIGOPT = "sigopt"
    WANDB = "wandb"
def is_main_process(local_rank):
    if is_torch_xla_available():
        import torch_xla.core.xla_model as xm
        return xm.get_ordinal() == 0
    return local_rank in [-1, 0]
def total_processes_number(local_rank):
    if is_torch_xla_available():
        import torch_xla.core.xla_model as xm
        return xm.xrt_world_size()
    elif local_rank != -1 and is_torch_available():
        import torch
        return torch.distributed.get_world_size()
    return 1
def speed_metrics(split, start_time, num_samples=None, num_steps=None, num_tokens=None):
    runtime = time.time() - start_time
    result = {f"{split}_runtime": round(runtime, 4)}
    if runtime == 0: return result
    if num_samples is not None:
        samples_per_second = num_samples / runtime
        result[f"{split}_samples_per_second"] = round(samples_per_second, 3)
    if num_steps is not None:
        steps_per_second = num_steps / runtime
        result[f"{split}_steps_per_second"] = round(steps_per_second, 3)
    if num_tokens is not None:
        tokens_per_second = num_tokens / runtime
        result[f"{split}_tokens_per_second"] = round(tokens_per_second, 3)
    return result
class SchedulerType(ExplicitEnum):
    LINEAR = "linear"
    COSINE = "cosine"
    COSINE_WITH_RESTARTS = "cosine_with_restarts"
    POLYNOMIAL = "polynomial"
    CONSTANT = "constant"
    CONSTANT_WITH_WARMUP = "constant_with_warmup"
    INVERSE_SQRT = "inverse_sqrt"
    REDUCE_ON_PLATEAU = "reduce_lr_on_plateau"
    COSINE_WITH_MIN_LR = "cosine_with_min_lr"
    WARMUP_STABLE_DECAY = "warmup_stable_decay"
class TrainerMemoryTracker:
    stages = {'__init__': 'init', 'train': 'train', '_inner_training_loop': 'train', 'evaluate': 'eval', 'predict': 'test'}
    def __init__(self, skip_memory_metrics=False):
        self.skip_memory_metrics = skip_memory_metrics
        if not is_psutil_available(): self.skip_memory_metrics = True
        if self.skip_memory_metrics: return
        import psutil
        if is_torch_cuda_available() or is_torch_mlu_available() or is_torch_musa_available():
            import torch
            self.torch = torch
            self.gpu = {}
        elif is_torch_mps_available():
            import torch
            self.torch = torch
            self.gpu = {}
        elif is_torch_xpu_available():
            import torch
            self.torch = torch
            self.gpu = {}
        elif is_torch_npu_available():
            import torch
            self.torch = torch
            self.gpu = {}
        else: self.torch = None
        self.process = psutil.Process()
        self.cur_stage = None
        self.cpu = {}
        self.init_reported = False
    def derive_stage(self):
        caller = inspect.currentframe().f_back.f_back.f_code.co_name
        if caller in self.stages: return self.stages[caller]
        else: raise ValueError(f"was called from {caller}, but only expect to be called from one of {self.stages.keys()}")
    def cpu_mem_used(self): return self.process.memory_info().rss
    def peak_monitor_func(self):
        self.cpu_mem_used_peak = -1
        while True:
            self.cpu_mem_used_peak = max(self.cpu_mem_used(), self.cpu_mem_used_peak)
            if not self.peak_monitoring: break
    def start(self):
        if self.skip_memory_metrics: return
        stage = self.derive_stage()
        if self.cur_stage is not None and self.cur_stage != stage: return
        self.cur_stage = stage
        gc.collect()
        if self.torch is not None:
            if torch.cuda.is_available():
                self.torch.cuda.reset_peak_memory_stats()
                self.torch.cuda.empty_cache()
            elif is_torch_mlu_available():
                self.torch.mlu.reset_peak_memory_stats()
                self.torch.mlu.empty_cache()
            elif is_torch_musa_available():
                self.torch.musa.reset_peak_memory_stats()
                self.torch.musa.empty_cache()
            elif is_torch_xpu_available():
                self.torch.xpu.reset_peak_memory_stats()
                self.torch.xpu.empty_cache()
            elif is_torch_npu_available():
                self.torch.npu.reset_peak_memory_stats()
                self.torch.npu.empty_cache()
            elif is_torch_mps_available(): self.torch.mps.empty_cache()
        if self.torch is not None:
            if torch.cuda.is_available(): self.gpu_mem_used_at_start = self.torch.cuda.memory_allocated()
            elif is_torch_mlu_available(): self.gpu_mem_used_at_start = self.torch.mlu.memory_allocated()
            elif is_torch_musa_available(): self.gpu_mem_used_at_start = self.torch.musa.memory_allocated()
            elif is_torch_xpu_available(): self.gpu_mem_used_at_start = self.torch.xpu.memory_allocated()
            elif is_torch_npu_available(): self.gpu_mem_used_at_start = self.torch.npu.memory_allocated()
            elif is_torch_mps_available(): self.gpu_mem_used_at_start = self.torch.mps.current_allocated_memory()
        self.cpu_mem_used_at_start = self.cpu_mem_used()
        self.peak_monitoring = True
        peak_monitor_thread = threading.Thread(target=self.peak_monitor_func)
        peak_monitor_thread.daemon = True
        peak_monitor_thread.start()
    def stop(self, stage):
        if self.cur_stage is not None and self.cur_stage != stage: return
        self.peak_monitoring = False
        gc.collect()
        if self.torch is not None:
            if torch.cuda.is_available(): self.torch.cuda.empty_cache()
            elif is_torch_mlu_available(): self.torch.mlu.empty_cache()
            elif is_torch_musa_available(): self.torch.musa.empty_cache()
            elif is_torch_xpu_available(): self.torch.xpu.empty_cache()
            elif is_torch_npu_available(): self.torch.npu.empty_cache()
            elif is_torch_mps_available(): self.torch.mps.empty_cache()
        if self.torch is not None:
            if torch.cuda.is_available():
                self.gpu_mem_used_now = self.torch.cuda.memory_allocated()
                self.gpu_mem_used_peak = self.torch.cuda.max_memory_allocated()
            elif is_torch_mlu_available():
                self.gpu_mem_used_now = self.torch.mlu.memory_allocated()
                self.gpu_mem_used_peak = self.torch.mlu.max_memory_allocated()
            elif is_torch_musa_available():
                self.gpu_mem_used_now = self.torch.musa.memory_allocated()
                self.gpu_mem_used_peak = self.torch.musa.max_memory_allocated()
            elif is_torch_xpu_available():
                self.gpu_mem_used_now = self.torch.xpu.memory_allocated()
                self.gpu_mem_used_peak = self.torch.xpu.max_memory_allocated()
            elif is_torch_npu_available():
                self.gpu_mem_used_now = self.torch.npu.memory_allocated()
                self.gpu_mem_used_peak = self.torch.npu.max_memory_allocated()
            elif is_torch_mps_available():
                self.gpu_mem_used_now = self.torch.mps.current_allocated_memory()
                self.gpu_mem_used_peak = None
            else: raise ValueError("No available GPU device found!")
            self.gpu[self.cur_stage] = {"begin": self.gpu_mem_used_at_start, "end": self.gpu_mem_used_now, "alloc": (self.gpu_mem_used_now - self.gpu_mem_used_at_start)}
            if self.gpu_mem_used_peak is not None: self.gpu[self.cur_stage]["peaked"] = max(0, self.gpu_mem_used_peak - self.gpu_mem_used_now)
            else: self.gpu[self.cur_stage]["peaked"] = "Not available"
        self.cpu_mem_used_now = self.cpu_mem_used()
        self.cpu[self.cur_stage] = {"begin": self.cpu_mem_used_at_start, "end": self.cpu_mem_used_now, "alloc": (self.cpu_mem_used_now - self.cpu_mem_used_at_start), "peaked": max(0, self.cpu_mem_used_peak - self.cpu_mem_used_now)}
        self.cur_stage = None
    def update_metrics(self, stage, metrics):
        if self.skip_memory_metrics: return
        if self.cur_stage is not None and self.cur_stage != stage: return
        stages = [stage]
        if not self.init_reported:
            stages.insert(0, "init")
            self.init_reported = True
        for stage in stages:
            for t in ["alloc", "peaked"]:
                if stage in self.cpu and t in self.cpu[stage]: metrics[f"{stage}_mem_cpu_{t}_delta"] = self.cpu[stage][t]
                if self.torch is not None and stage in self.gpu and t in self.gpu[stage]: metrics[f"{stage}_mem_gpu_{t}_delta"] = self.gpu[stage][t]
        if stages[0] == "init":
            metrics["before_init_mem_cpu"] = self.cpu["init"]["begin"]
            if self.torch is not None: metrics["before_init_mem_gpu"] = self.gpu["init"]["begin"]
    def stop_and_update_metrics(self, metrics=None):
        if self.skip_memory_metrics: return
        stage = self.derive_stage()
        self.stop(stage)
        if metrics is not None: self.update_metrics(stage, metrics)
def has_length(dataset):
    try: return len(dataset) is not None
    except TypeError: return False
def denumpify_detensorize(metrics):
    if isinstance(metrics, (list, tuple)): return type(metrics)(denumpify_detensorize(m) for m in metrics)
    elif isinstance(metrics, dict): return type(metrics)({k: denumpify_detensorize(v) for k, v in metrics.items()})
    elif isinstance(metrics, np.generic): return metrics.item()
    elif is_torch_available() and isinstance(metrics, torch.Tensor) and metrics.numel() == 1: return metrics.item()
    return metrics
def number_of_arguments(func):
    if isinstance(func, functools.partial):
        total_args = len(inspect.signature(func.func).parameters)
        return total_args - len(func.args) - len(func.keywords)
    return len(inspect.signature(func).parameters)
def find_executable_batch_size(function: callable = None, starting_batch_size: int = 128, auto_find_batch_size: bool = False):
    if function is None: return functools.partial(find_executable_batch_size, starting_batch_size=starting_batch_size, auto_find_batch_size=auto_find_batch_size)
    if auto_find_batch_size:
        requires_backends(find_executable_batch_size, "sapiens_accelerator")
        from sapiens_accelerator.utils import find_executable_batch_size as sapiens_accelerator_find_executable_batch_size
        return sapiens_accelerator_find_executable_batch_size(function=function, starting_batch_size=starting_batch_size)
    return functools.partial(function, batch_size=starting_batch_size)
class FSDPOption(ExplicitEnum):
    FULL_SHARD = "full_shard"
    SHARD_GRAD_OP = "shard_grad_op"
    NO_SHARD = "no_shard"
    HYBRID_SHARD = "hybrid_shard"
    HYBRID_SHARD_ZERO2 = "hybrid_shard_zero2"
    OFFLOAD = "offload"
    AUTO_WRAP = "auto_wrap"
class RemoveColumnsCollator:
    def __init__(self, data_collator, signature_columns, logger=None, model_name: Optional[str] = None, description: Optional[str] = None):
        self.data_collator = data_collator
        self.signature_columns = signature_columns
        self.logger = logger
        self.description = description
        self.model_name = model_name
        self.message_logged = False
    def _remove_columns(self, feature: dict) -> dict:
        if not isinstance(feature, dict): return feature
        if not self.message_logged and self.logger and self.model_name:
            ignored_columns = list(set(feature.keys()) - set(self.signature_columns))
            if len(ignored_columns) > 0:
                dset_description = "" if self.description is None else f"in the {self.description} set"
                self.logger.info(f"The following columns {dset_description} don't have a corresponding argument in `{self.model_name}.forward` and have been ignored: {', '.join(ignored_columns)}. If {', '.join(ignored_columns)} are not expected by `{self.model_name}.forward`, you can safely ignore this message.")
                self.message_logged = True
        return {k: v for k, v in feature.items() if k in self.signature_columns}
    def __call__(self, features: List[dict]):
        features = [self._remove_columns(feature) for feature in features]
        return self.data_collator(features)
def check_target_module_exists(optim_target_modules, key: str, return_is_regex: bool = False):
    target_module_found = False
    is_regex = False
    if isinstance(optim_target_modules, str):
        target_module_found = bool(re.fullmatch(optim_target_modules, key))
        is_regex = True if not optim_target_modules == key else False
    elif key in optim_target_modules: target_module_found = True
    elif any(target_key in key for target_key in optim_target_modules): target_module_found = True
    elif any(bool(re.fullmatch(optim_target_module, key)) for optim_target_module in optim_target_modules):
        target_module_found = True
        is_regex = True
    if return_is_regex: return target_module_found, is_regex
    return target_module_found
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
