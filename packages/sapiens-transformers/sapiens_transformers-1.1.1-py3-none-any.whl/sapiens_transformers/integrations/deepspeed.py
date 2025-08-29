"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import importlib.metadata as importlib_metadata
import importlib.util
import weakref
from functools import partialmethod
from ..dependency_versions_check import dep_version_check
from ..utils import is_sapiens_accelerator_available, is_torch_available, is_torch_mlu_available, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
def is_deepspeed_available():
    package_exists = importlib.util.find_spec("deepspeed") is not None
    if package_exists:
        try:
            if is_torch_mlu_available():
                _ = importlib_metadata.metadata("deepspeed-mlu")
                return True
            _ = importlib_metadata.metadata("deepspeed")
            return True
        except importlib_metadata.PackageNotFoundError: return False
if is_sapiens_accelerator_available() and is_deepspeed_available(): from sapiens_accelerator.utils.deepspeed import HfDeepSpeedConfig as DeepSpeedConfig
else: from builtins import object as DeepSpeedConfig
class HfDeepSpeedConfig(DeepSpeedConfig):
    def __init__(self, config_file_or_dict):
        set_hf_deepspeed_config(self)
        dep_version_check("sapiens_accelerator")
        dep_version_check("deepspeed")
        super().__init__(config_file_or_dict)
class HfTrainerDeepSpeedConfig(HfDeepSpeedConfig):
    def __init__(self, config_file_or_dict):
        super().__init__(config_file_or_dict)
        self._dtype = None
        self.mismatches = []
    def dtype(self):
        if self._dtype is None: raise ValueError("trainer_config_process() wasn't called yet to tell dtype")
        return self._dtype
    def is_auto(self, ds_key_long):
        val = self.get_value(ds_key_long)
        if val is None: return False
        else: return val == "auto"
    def fill_match(self, ds_key_long, hf_val, hf_key=None, must_match=True):
        config, ds_key = self.find_config_node(ds_key_long)
        if config is None: return
        if config.get(ds_key) == "auto":
            config[ds_key] = hf_val
            return
        if not must_match: return
        ds_val = config.get(ds_key)
        if ds_val is not None and ds_val != hf_val: self.mismatches.append(f"- ds {ds_key_long}={ds_val} vs hf {hf_key}={hf_val}")
    fill_only = partialmethod(fill_match, must_match=False)
    def trainer_config_process(self, args, auto_find_batch_size=False):
        train_batch_size = args.world_size * args.per_device_train_batch_size * args.gradient_accumulation_steps
        self.fill_match("train_micro_batch_size_per_gpu", args.per_device_train_batch_size, "per_device_train_batch_size", not auto_find_batch_size)
        self.fill_match("gradient_accumulation_steps", args.gradient_accumulation_steps, "gradient_accumulation_steps")
        self.fill_match("train_batch_size", train_batch_size, "train_batch_size (calculated)", not auto_find_batch_size)
        self.fill_match("gradient_clipping", args.max_grad_norm, "max_grad_norm")
        self.fill_match("optimizer.params.lr", args.learning_rate, "learning_rate")
        self.fill_match("optimizer.params.betas", [args.adam_beta1, args.adam_beta2], "adam_beta1+adam_beta2")
        self.fill_match("optimizer.params.eps", args.adam_epsilon, "adam_epsilon")
        self.fill_match("optimizer.params.weight_decay", args.weight_decay, "weight_decay")
        self.fill_only("scheduler.params.warmup_min_lr", 0)
        self.fill_match("scheduler.params.warmup_max_lr", args.learning_rate, "learning_rate")
        if args.fp16 or args.fp16_full_eval: fp16_backend = "apex" if args.fp16_backend == "apex" else "amp"
        else: fp16_backend = None
        if args.save_on_each_node:
            self.config["checkpoint"] = self.config.get("checkpoint", {})
            self.config["checkpoint"]["use_node_local_storage"] = args.save_on_each_node
        self.fill_match("fp16.enabled", ((args.fp16 or args.fp16_full_eval) and fp16_backend == "amp"), "fp16|fp16_full_eval+fp16_backend(amp)")
        self.fill_match("amp.enabled", fp16_backend == "apex", "fp16+fp16_backend(apex)")
        self.fill_match("amp.opt_level", args.fp16_opt_level, "fp16_opt_level")
        self.fill_match("bf16.enabled", (args.bf16 or args.bf16_full_eval), "bf16|bf16_full_eval")
        if self.is_true("bf16.enabled"): self._dtype = torch.bfloat16
        elif self.is_false("fp16.enabled"): self._dtype = torch.float32
        else: self._dtype = torch.float16
    def trainer_config_finalize(self, args, model, num_training_steps):
        hidden_size_based_keys = ["zero_optimization.reduce_bucket_size", "zero_optimization.stage3_prefetch_bucket_size", "zero_optimization.stage3_param_persistence_threshold"]
        hidden_size_auto_keys = [x for x in hidden_size_based_keys if self.is_auto(x)]
        if len(hidden_size_auto_keys) > 0:
            if hasattr(model.config, "hidden_size"): hidden_size = model.config.hidden_size
            elif hasattr(model.config, "hidden_sizes"): hidden_size = max(model.config.hidden_sizes)
            else: raise ValueError(f"The model's config file has neither `hidden_size` nor `hidden_sizes` entry, therefore it's not possible to automatically fill out the following `auto` entries in the DeepSpeed config file: {hidden_size_auto_keys}. You can fix that by replacing `auto` values for these keys with an integer value of your choice.")
            self.fill_only("zero_optimization.reduce_bucket_size", hidden_size * hidden_size)
            if self.is_zero3():
                self.fill_only("zero_optimization.stage3_prefetch_bucket_size", int(0.9 * hidden_size * hidden_size))
                self.fill_only("zero_optimization.stage3_param_persistence_threshold", 10 * hidden_size)
        self.fill_match("scheduler.params.total_num_steps", num_training_steps, "num_training_steps (calculated)")
        self.fill_match("scheduler.params.warmup_num_steps", args.get_warmup_steps(num_training_steps), "warmup_steps")
        if len(self.mismatches) > 0:
            mismatches = "\n".join(self.mismatches)
            raise ValueError(f"Please correct the following DeepSpeed config values that mismatch TrainingArguments values:\n{mismatches}\nThe easiest method is to set these DeepSpeed config values to 'auto'.")
_hf_deepspeed_config_weak_ref = None
def set_hf_deepspeed_config(hf_deepspeed_config_obj):
    global _hf_deepspeed_config_weak_ref
    _hf_deepspeed_config_weak_ref = weakref.ref(hf_deepspeed_config_obj)
def unset_hf_deepspeed_config():
    global _hf_deepspeed_config_weak_ref
    _hf_deepspeed_config_weak_ref = None
def is_deepspeed_zero3_enabled():
    if _hf_deepspeed_config_weak_ref is not None and _hf_deepspeed_config_weak_ref() is not None: return _hf_deepspeed_config_weak_ref().is_zero3()
    else: return False
def deepspeed_config():
    if _hf_deepspeed_config_weak_ref is not None and _hf_deepspeed_config_weak_ref() is not None: return _hf_deepspeed_config_weak_ref().config
    else: return None
def deepspeed_optim_sched(trainer, hf_deepspeed_config, args, num_training_steps, model_parameters):
    from sapiens_accelerator.utils import DummyOptim, DummyScheduler
    config = hf_deepspeed_config.config
    optimizer = None
    if "optimizer" in config:
        if args.adafactor: raise ValueError("--adafactor was passed, but also found `optimizer` configured in the DeepSpeed config. Only one optimizer can be configured.")
        optimizer = DummyOptim(params=model_parameters)
    else:
        if hf_deepspeed_config.is_offload(): logger.info("Detected ZeRO Offload and non-DeepSpeed optimizers: This combination should work as long as the custom optimizer has both CPU and GPU implementation (except LAMB)")
        optimizer = trainer.create_optimizer()
        config["zero_allow_untested_optimizer"] = True
    lr_scheduler = None
    if "scheduler" in config: lr_scheduler = DummyScheduler(optimizer)
    else:
        if isinstance(optimizer, DummyOptim):
            def _lr_scheduler_callable(optimizer):
                trainer_copy = copy.copy(trainer)
                trainer_copy.lr_scheduler = None
                lr_scheduler = trainer_copy.create_scheduler(num_training_steps=num_training_steps, optimizer=optimizer)
                return lr_scheduler
            lr_scheduler = DummyScheduler(optimizer, lr_scheduler_callable=_lr_scheduler_callable)
        else: lr_scheduler = trainer.create_scheduler(num_training_steps=num_training_steps, optimizer=optimizer)
    return optimizer, lr_scheduler
def deepspeed_init(trainer, num_training_steps, inference=False):
    from deepspeed.utils import logger as ds_logger
    model = trainer.model
    args = trainer.args
    hf_deepspeed_config = trainer.accelerator.state.deepspeed_plugin.hf_ds_config
    hf_deepspeed_config.trainer_config_finalize(args, model, num_training_steps)
    ds_logger.setLevel(args.get_process_log_level())
    if inference:
        if not hf_deepspeed_config.is_zero3(): raise ValueError("ZeRO inference only makes sense with ZeRO Stage 3 - please adjust your config")
        hf_deepspeed_config.del_config_sub_tree("optimizer")
        hf_deepspeed_config.del_config_sub_tree("lr_scheduler")
        optimizer, lr_scheduler = None, None
        model_parameters = None
    else:
        trainer.optimizer = None
        model_parameters = list(filter(lambda p: p.requires_grad, model.parameters()))
        optimizer, lr_scheduler = deepspeed_optim_sched(trainer, hf_deepspeed_config, args, num_training_steps, model_parameters)
    return optimizer, lr_scheduler
def deepspeed_load_checkpoint(deepspeed_engine, checkpoint_path, load_module_strict=True):
    import glob
    deepspeed_checkpoint_dirs = sorted(glob.glob(f"{checkpoint_path}/global_step*"))
    if len(deepspeed_checkpoint_dirs) > 0:
        logger.info(f"Attempting to resume from {checkpoint_path}")
        load_path, _ = deepspeed_engine.load_checkpoint(checkpoint_path, load_module_strict=load_module_strict, load_optimizer_states=True, load_lr_scheduler_states=True)
        if load_path is None: raise ValueError(f"[deepspeed] failed to resume from checkpoint {checkpoint_path}")
    else: raise ValueError(f"Can't find a valid checkpoint at {checkpoint_path}")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
