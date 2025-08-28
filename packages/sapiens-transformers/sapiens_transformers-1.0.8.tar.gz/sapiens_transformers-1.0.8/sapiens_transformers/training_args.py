"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (SAPIENS_ACCELERATOR_MIN_VERSION, ExplicitEnum, cached_property, is_sapiens_accelerator_available, is_ipex_available, is_safetensors_available,
is_sagemaker_dp_enabled, is_sagemaker_mp_enabled, is_torch_available, is_torch_bf16_cpu_available, is_torch_bf16_gpu_available, is_torch_mlu_available,
is_torch_mps_available, is_torch_musa_available, is_torch_neuroncore_available, is_torch_npu_available, is_torch_tf32_available, is_torch_xla_available,
is_torch_xpu_available, logging, requires_backends)
from .trainer_utils import (EvaluationStrategy, FSDPOption, HubStrategy, IntervalStrategy, SchedulerType)
from .utils.import_utils import is_optimum_neuron_available
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, List, Optional, Union
from huggingface_hub import get_full_repo_name
from .utils.generic import strtobool
from .debug_utils import DebugOption
from datetime import timedelta
from packaging import version
from pathlib import Path
from enum import Enum
import contextlib
import warnings
import json
import math
import io
import os
logger = logging.get_logger(__name__)
log_levels = logging.get_log_levels_dict().copy()
trainer_log_levels = dict(**log_levels, passive=-1)
if is_torch_available():
    import torch
    import torch.distributed as dist
    from .pytorch_utils import is_torch_greater_or_equal_than_2_0
if is_sapiens_accelerator_available():
    from sapiens_accelerator.state import AcceleratorState, PartialState
    from sapiens_accelerator.utils import DistributedType
    from .trainer_pt_utils import AcceleratorConfig
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
if is_torch_neuroncore_available(check_device=False):
    if os.environ.get("TORCHELASTIC_RUN_ID"):
        if is_optimum_neuron_available(): logger.info("Make sure that you are performing the training with the NeuronTrainer from optimum[neuron], this will fail otherwise.")
        else:
            logger.warning("Please use the NeuronTrainer from optimum[neuron] instead of the Transformers library to perform training on AWS Trainium instances.")
            import torch_xla.distributed.xla_backend as xbn
            if not isinstance(dist.group.WORLD, xbn.ProcessGroupXla):
                dist.init_process_group(backend="xla")
                if not isinstance(dist.group.WORLD, xbn.ProcessGroupXla): raise AssertionError("Failed to initialize torch.distributed process group using XLA backend.")
if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp
    smp.init()
def default_logdir() -> str:
    import socket
    from datetime import datetime
    current_time = datetime.now().strftime("%b%d_%H-%M-%S")
    return os.path.join("runs", current_time + "_" + socket.gethostname())
def get_int_from_env(env_keys, default):
    for e in env_keys:
        val = int(os.environ.get(e, -1))
        if val >= 0: return val
    return default
def get_xla_device_type(device: "torch.device") -> Optional[str]:
    if is_torch_xla_available():
        if device.type == "cpu": return "CPU"
        return xm.xla_real_devices([device])[0].split(":")[0]
    return None
class OptimizerNames(ExplicitEnum):
    ADAMW_HF = "adamw_hf"
    ADAMW_TORCH = "adamw_torch"
    ADAMW_TORCH_FUSED = "adamw_torch_fused"
    ADAMW_TORCH_XLA = "adamw_torch_xla"
    ADAMW_TORCH_NPU_FUSED = "adamw_torch_npu_fused"
    ADAMW_APEX_FUSED = "adamw_apex_fused"
    ADAFACTOR = "adafactor"
    ADAMW_ANYPRECISION = "adamw_anyprecision"
    ADAMW_TORCH_4BIT = "adamw_torch_4bit"
    ADEMAMIX = "ademamix"
    SGD = "sgd"
    ADAGRAD = "adagrad"
    ADAMW_SAPIENS = "adamw_sapiens_8bit"
    ADAMW_8BIT = "adamw_8bit"
    ADEMAMIX_8BIT = "ademamix_8bit"
    LION_8BIT = "lion_8bit"
    LION = "lion_32bit"
    PAGED_ADAMW = "paged_adamw_32bit"
    PAGED_ADAMW_8BIT = "paged_adamw_8bit"
    PAGED_ADEMAMIX = "paged_ademamix_32bit"
    PAGED_ADEMAMIX_8BIT = "paged_ademamix_8bit"
    PAGED_LION = "paged_lion_32bit"
    PAGED_LION_8BIT = "paged_lion_8bit"
    RMSPROP = "rmsprop"
    RMSPROP_SAPIENS = "rmsprop_sapiens"
    RMSPROP_8BIT = "rmsprop_sapiens_8bit"
    RMSPROP_32BIT = "rmsprop_sapiens_32bit"
    GALORE_ADAMW = "galore_adamw"
    GALORE_ADAMW_8BIT = "galore_adamw_8bit"
    GALORE_ADAFACTOR = "galore_adafactor"
    GALORE_ADAMW_LAYERWISE = "galore_adamw_layerwise"
    GALORE_ADAMW_8BIT_LAYERWISE = "galore_adamw_8bit_layerwise"
    GALORE_ADAFACTOR_LAYERWISE = "galore_adafactor_layerwise"
    LOMO = "lomo"
    ADALOMO = "adalomo"
    GROKADAMW = "grokadamw"
    SCHEDULE_FREE_ADAMW = "schedule_free_adamw"
    SCHEDULE_FREE_SGD = "schedule_free_sgd"
_VALID_DICT_FIELDS = ["accelerator_config", "fsdp_config", "deepspeed", "gradient_checkpointing_kwargs", "lr_scheduler_kwargs"]
def _convert_str_dict(passed_value: dict):
    for key, value in passed_value.items():
        if isinstance(value, dict): passed_value[key] = _convert_str_dict(value)
        elif isinstance(value, str):
            if value.lower() in ("true", "false"): passed_value[key] = value.lower() == "true"
            elif value.isdigit(): passed_value[key] = int(value)
            elif value.replace(".", "", 1).isdigit(): passed_value[key] = float(value)
    return passed_value
@dataclass
class TrainingArguments:
    framework = "pt"
    output_dir: str = field(metadata={"help": "The output directory where the model predictions and checkpoints will be written."})
    overwrite_output_dir: bool = field(default=False, metadata={'help': 'Overwrite the content of the output directory. Use this to continue training if output_dir points to a checkpoint directory.'})
    do_train: bool = field(default=False, metadata={"help": "Whether to run training."})
    do_eval: bool = field(default=False, metadata={"help": "Whether to run eval on the dev set."})
    do_predict: bool = field(default=False, metadata={"help": "Whether to run predictions on the test set."})
    eval_strategy: Union[IntervalStrategy, str] = field(default="no", metadata={"help": "The evaluation strategy to use."})
    prediction_loss_only: bool = field(default=False, metadata={"help": "When performing evaluation and predictions, only returns the loss."})
    per_device_train_batch_size: int = field(default=8, metadata={"help": "Batch size per GPU/TPU/MPS/NPU core/CPU for training."})
    per_device_eval_batch_size: int = field(default=8, metadata={"help": "Batch size per GPU/TPU/MPS/NPU core/CPU for evaluation."})
    per_gpu_train_batch_size: Optional[int] = field(default=None, metadata={'help': 'Deprecated, the use of `--per_device_train_batch_size` is preferred. Batch size per GPU/TPU core/CPU for training.'})
    per_gpu_eval_batch_size: Optional[int] = field(default=None, metadata={'help': 'Deprecated, the use of `--per_device_eval_batch_size` is preferred. Batch size per GPU/TPU core/CPU for evaluation.'})
    gradient_accumulation_steps: int = field(default=1, metadata={"help": "Number of updates steps to accumulate before performing a backward/update pass."})
    eval_accumulation_steps: Optional[int] = field(default=None, metadata={"help": "Number of predictions steps to accumulate before moving the tensors to the CPU."})
    eval_delay: Optional[float] = field(default=0, metadata={'help': 'Number of epochs or steps to wait for before the first evaluation can be performed, depending on the eval_strategy.'})
    torch_empty_cache_steps: Optional[int] = field(default=None, metadata={'help': 'Number of steps to wait before calling `torch.<device>.empty_cache()`. If left unset or set to None, cache will not be emptied.'})
    learning_rate: float = field(default=5e-5, metadata={"help": "The initial learning rate for AdamW."})
    weight_decay: float = field(default=0.0, metadata={"help": "Weight decay for AdamW if we apply some."})
    adam_beta1: float = field(default=0.9, metadata={"help": "Beta1 for AdamW optimizer"})
    adam_beta2: float = field(default=0.999, metadata={"help": "Beta2 for AdamW optimizer"})
    adam_epsilon: float = field(default=1e-8, metadata={"help": "Epsilon for AdamW optimizer."})
    max_grad_norm: float = field(default=1.0, metadata={"help": "Max gradient norm."})
    num_train_epochs: float = field(default=3.0, metadata={"help": "Total number of training epochs to perform."})
    max_steps: int = field(default=-1, metadata={"help": "If > 0: set total number of training steps to perform. Override num_train_epochs."})
    lr_scheduler_type: Union[SchedulerType, str] = field(default="linear", metadata={"help": "The scheduler type to use."})
    lr_scheduler_kwargs: Optional[Union[dict, str]] = field(default_factory=dict, metadata={"help": ("Extra parameters for the lr_scheduler such as {'num_cycles': 1} for the cosine with hard restarts.")})
    warmup_ratio: float = field(default=0.0, metadata={"help": "Linear warmup over warmup_ratio fraction of total steps."})
    warmup_steps: int = field(default=0, metadata={"help": "Linear warmup over warmup_steps."})
    log_level: Optional[str] = field(default="passive", metadata={"help": ("Logger log level to use on the main node. Possible choices are the log levels as strings: 'debug', 'info', 'warning', 'error' and 'critical', plus a 'passive' level which doesn't set anything and lets the application set the level. Defaults to 'passive'."), "choices": trainer_log_levels.keys()})
    log_level_replica: Optional[str] = field(default="warning", metadata={"help": "Logger log level to use on replica nodes. Same choices and defaults as ``log_level``", "choices": trainer_log_levels.keys()})
    log_on_each_node: bool = field(default=True, metadata={'help': 'When doing a multinode distributed training, whether to log once per node or just once on the main node.'})
    logging_dir: Optional[str] = field(default=None, metadata={"help": "Tensorboard log dir."})
    logging_strategy: Union[IntervalStrategy, str] = field(default="steps", metadata={"help": "The logging strategy to use."})
    logging_first_step: bool = field(default=False, metadata={"help": "Log the first global_step"})
    logging_steps: float = field(default=500, metadata={'help': 'Log every X updates steps. Should be an integer or a float in range `[0,1)`. If smaller than 1, will be interpreted as ratio of total training steps.'})
    logging_nan_inf_filter: bool = field(default=True, metadata={"help": "Filter nan and inf losses for logging."})
    save_strategy: Union[IntervalStrategy, str] = field(default="steps", metadata={"help": "The checkpoint save strategy to use."})
    save_steps: float = field(default=500, metadata={'help': 'Save checkpoint every X updates steps. Should be an integer or a float in range `[0,1)`. If smaller than 1, will be interpreted as ratio of total training steps.'})
    save_total_limit: Optional[int] = field(default=None, metadata={'help': "If a value is passed, will limit the total amount of checkpoints. Deletes the older checkpoints in `output_dir`. When `load_best_model_at_end` is enabled, the 'best' checkpoint according to `metric_for_best_model` will always be retained in addition to the most recent ones. For example, for `save_total_limit=5` and `load_best_model_at_end=True`, the four last checkpoints will always be retained alongside the best model. When `save_total_limit=1` and `load_best_model_at_end=True`, it is possible that two checkpoints are saved: the last one and the best one (if they are different). Default is unlimited checkpoints"})
    save_safetensors: Optional[bool] = field(default=True, metadata={'help': 'Use safetensors saving and loading for state dicts instead of default torch.load and torch.save.'})
    save_on_each_node: bool = field(default=False, metadata={'help': 'When doing multi-node distributed training, whether to save models and checkpoints on each node, or only on the main one'})
    save_only_model: bool = field(default=False, metadata={'help': "When checkpointing, whether to only save the model, or also the optimizer, scheduler & rng state.Note that when this is true, you won't be able to resume training from checkpoint.This enables you to save storage by not storing the optimizer, scheduler & rng state.You can only load the model using from_pretrained with this option set to True."})
    restore_callback_states_from_checkpoint: bool = field(default=False, metadata={'help': 'Whether to restore the callback states from the checkpoint. If `True`, will override callbacks passed to the `Trainer` if they exist in the checkpoint.'})
    no_cuda: bool = field(default=False, metadata={"help": "This argument is deprecated."})
    use_cpu: bool = field(default=False, metadata={'help': ' Whether or not to use cpu. If set to False, we will use cuda/tpu/mps/npu device if available.'})
    use_mps_device: bool = field(default=False, metadata={'help': 'This argument is deprecated. `mps` device will be used if available similar to `cuda` device. It will be removed in version 5.0 of HF Transformers'})
    seed: int = field(default=42, metadata={"help": "Random seed that will be set at the beginning of training."})
    data_seed: Optional[int] = field(default=None, metadata={"help": "Random seed to be used with data samplers."})
    jit_mode_eval: bool = field(default=False, metadata={"help": "Whether or not to use PyTorch jit trace for inference"})
    use_ipex: bool = field(default=False, metadata={'help': "Use Intel extension for PyTorch when it is available, installation: 'https://github.com/intel/intel-extension-for-pytorch'"})
    bf16: bool = field(default=False, metadata={'help': 'Whether to use bf16 (mixed) precision instead of 32-bit. Requires Ampere or higher NVIDIA architecture or using CPU (use_cpu) or Ascend NPU. This is an experimental API and it may change.'})
    fp16: bool = field(default=False, metadata={"help": "Whether to use fp16 (mixed) precision instead of 32-bit"})
    fp16_opt_level: str = field(default="O1", metadata={'help': "For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']. See details at https://nvidia.github.io/apex/amp.html"})
    half_precision_backend: str = field(default="auto", metadata={'help': 'The backend to be used for half precision.', 'choices': ['auto', 'apex', 'cpu_amp']})
    bf16_full_eval: bool = field(default=False, metadata={'help': 'Whether to use full bfloat16 evaluation instead of 32-bit. This is an experimental API and it may change.'})
    fp16_full_eval: bool = field(default=False, metadata={"help": "Whether to use full float16 evaluation instead of 32-bit"})
    tf32: Optional[bool] = field(default=None, metadata={'help': 'Whether to enable tf32 mode, available in Ampere and newer GPU architectures. This is an experimental API and it may change.'})
    local_rank: int = field(default=-1, metadata={"help": "For distributed training: local_rank"})
    ddp_backend: Optional[str] = field(default=None, metadata={'help': 'The backend to be used for distributed training', 'choices': ['nccl', 'gloo', 'mpi', 'ccl', 'hccl', 'cncl', 'mccl']})
    tpu_num_cores: Optional[int] = field(default=None, metadata={"help": "TPU: Number of TPU cores (automatically passed by launcher script)"})
    tpu_metrics_debug: bool = field(default=False, metadata={'help': 'Deprecated, the use of `--debug tpu_metrics_debug` is preferred. TPU: Whether to print debug metrics'})
    debug: Union[str, List[DebugOption]] = field(default="", metadata={'help': 'Whether or not to enable debug mode. Current options: `underflow_overflow` (Detect underflow and overflow in activations and weights), `tpu_metrics_debug` (print debug metrics on TPU).'})
    dataloader_drop_last: bool = field(default=False, metadata={"help": "Drop the last incomplete batch if it is not divisible by the batch size."})
    eval_steps: Optional[float] = field(default=None, metadata={'help': 'Run an evaluation every X steps. Should be an integer or a float in range `[0,1)`. If smaller than 1, will be interpreted as ratio of total training steps.'})
    dataloader_num_workers: int = field(default=0, metadata={'help': 'Number of subprocesses to use for data loading (PyTorch only). 0 means that the data will be loaded in the main process.'})
    dataloader_prefetch_factor: Optional[int] = field(default=None if not is_torch_available() or is_torch_greater_or_equal_than_2_0 else 2, metadata={'help': 'Number of batches loaded in advance by each worker. 2 means there will be a total of 2 * num_workers batches prefetched across all workers. Default is 2 for PyTorch < 2.0.0 and otherwise None.'})
    past_index: int = field(default=-1, metadata={"help": "If >=0, uses the corresponding part of the output as the past state for next step."})
    run_name: Optional[str] = field(default=None, metadata={"help": "An optional descriptor for the run. Notably used for wandb, mlflow and comet logging."})
    disable_tqdm: Optional[bool] = field(default=None, metadata={"help": "Whether or not to disable the tqdm progress bars."})
    remove_unused_columns: Optional[bool] = field(default=True, metadata={"help": "Remove columns not required by the model when using an nlp.Dataset."})
    label_names: Optional[List[str]] = field(default=None, metadata={"help": "The list of keys in your dictionary of inputs that correspond to the labels."})
    load_best_model_at_end: Optional[bool] = field(default=False, metadata={'help': 'Whether or not to load the best model found during training at the end of training. When this option is enabled, the best checkpoint will always be saved. See `save_total_limit` for more.'})
    metric_for_best_model: Optional[str] = field(default=None, metadata={"help": "The metric to use to compare two different models."})
    greater_is_better: Optional[bool] = field(default=None, metadata={"help": "Whether the `metric_for_best_model` should be maximized or not."})
    ignore_data_skip: bool = field(default=False, metadata={'help': 'When resuming training, whether or not to skip the first epochs and batches to get to the same training data.'})
    fsdp: Optional[Union[List[FSDPOption], str]] = field(default="", metadata={'help': 'Whether or not to use PyTorch Fully Sharded Data Parallel (FSDP) training (in distributed training only). The base option should be `full_shard`, `shard_grad_op` or `no_shard` and you can add CPU-offload to `full_shard` or `shard_grad_op` like this: full_shard offload` or `shard_grad_op offload`. You can add auto-wrap to `full_shard` or `shard_grad_op` with the same syntax: full_shard auto_wrap` or `shard_grad_op auto_wrap`.'})
    fsdp_min_num_params: int = field(default=0, metadata={'help': "This parameter is deprecated. FSDP's minimum number of parameters for Default Auto Wrapping. (useful only when `fsdp` field is passed)."})
    fsdp_config: Optional[Union[dict, str]] = field(default=None, metadata={'help': 'Config to be used with FSDP (Pytorch Fully Sharded  Data Parallel). The value is either a fsdp json config file (e.g., `fsdp_config.json`) or an already loaded json file as `dict`.'})
    fsdp_transformer_layer_cls_to_wrap: Optional[str] = field(default=None, metadata={'help': 'This parameter is deprecated. Transformer layer class name (case-sensitive) to wrap, e.g, `BertLayer`, `GPTJBlock`, `T5Block` .... (useful only when `fsdp` flag is passed).'})
    accelerator_config: Optional[Union[dict, str]] = field(default=None, metadata={'help': 'Config to be used with the internal Accelerator object initializtion. The value is either a accelerator json config file (e.g., `accelerator_config.json`) or an already loaded json file as `dict`.'})
    deepspeed: Optional[Union[dict, str]] = field(default=None, metadata={'help': 'Enable deepspeed and pass the path to deepspeed json config file (e.g. `ds_config.json`) or an already loaded json file as a dict'})
    label_smoothing_factor: float = field(default=0.0, metadata={"help": "The label smoothing epsilon to apply (zero means no label smoothing)."})
    default_optim = "adamw_torch"
    optim: Union[OptimizerNames, str] = field(default=default_optim, metadata={"help": "The optimizer to use."})
    optim_args: Optional[str] = field(default=None, metadata={"help": "Optional arguments to supply to optimizer."})
    adafactor: bool = field(default=False, metadata={"help": "Whether or not to replace AdamW by Adafactor."})
    group_by_length: bool = field(default=False, metadata={"help": "Whether or not to group samples of roughly the same length together when batching."})
    length_column_name: Optional[str] = field(default="length", metadata={"help": "Column name with precomputed lengths to use when grouping by length."})
    report_to: Union[None, str, List[str]] = field(default=None, metadata={"help": "The list of integrations to report the results and logs to."})
    ddp_find_unused_parameters: Optional[bool] = field(default=None, metadata={'help': 'When using distributed training, the value of the flag `find_unused_parameters` passed to `DistributedDataParallel`.'})
    ddp_bucket_cap_mb: Optional[int] = field(default=None, metadata={'help': 'When using distributed training, the value of the flag `bucket_cap_mb` passed to `DistributedDataParallel`.'})
    ddp_broadcast_buffers: Optional[bool] = field(default=None, metadata={'help': 'When using distributed training, the value of the flag `broadcast_buffers` passed to `DistributedDataParallel`.'})
    dataloader_pin_memory: bool = field(default=True, metadata={"help": "Whether or not to pin memory for DataLoader."})
    dataloader_persistent_workers: bool = field(default=False, metadata={'help': 'If True, the data loader will not shut down the worker processes after a dataset has been consumed once. This allows to maintain the workers Dataset instances alive. Can potentially speed up training, but will increase RAM usage.'})
    skip_memory_metrics: bool = field(default=True, metadata={"help": "Whether or not to skip adding of memory profiler reports to metrics."})
    use_legacy_prediction_loop: bool = field(default=False, metadata={"help": "Whether or not to use the legacy prediction_loop in the Trainer."})
    push_to_hub: bool = field(default=False, metadata={"help": "Whether or not to upload the trained model to the model hub after training."})
    resume_from_checkpoint: Optional[str] = field(default=None, metadata={"help": "The path to a folder with a valid checkpoint for your model."})
    hub_model_id: Optional[str] = field(default=None, metadata={"help": "The name of the repository to keep in sync with the local `output_dir`."})
    hub_strategy: Union[HubStrategy, str] = field(default="every_save", metadata={"help": "The hub strategy to use when `--push_to_hub` is activated."})
    hub_token: Optional[str] = field(default=None, metadata={"help": "The token to use to push to the Model Hub."})
    hub_private_repo: bool = field(default=False, metadata={"help": "Whether the model repository is private or not."})
    hub_always_push: bool = field(default=False, metadata={"help": "Unless `True`, the Trainer will skip pushes if the previous one wasn't finished yet."})
    gradient_checkpointing: bool = field(default=False, metadata={'help': 'If True, use gradient checkpointing to save memory at the expense of slower backward pass.'})
    gradient_checkpointing_kwargs: Optional[Union[dict, str]] = field(default=None, metadata={'help': 'Gradient checkpointing key word arguments such as `use_reentrant`. Will be passed to `torch.utils.checkpoint.checkpoint` through `model.gradient_checkpointing_enable`.'})
    include_inputs_for_metrics: bool = field(default=False, metadata={"help": "Whether or not the inputs will be passed to the `compute_metrics` function."})
    eval_do_concat_batches: bool = field(default=True, metadata={'help': 'Whether to recursively concat inputs/losses/labels/predictions across batches. If `False`, will instead store them as lists, with each batch kept separate.'})
    fp16_backend: str = field(default="auto", metadata={'help': 'Deprecated. Use half_precision_backend instead', 'choices': ['auto', 'apex', 'cpu_amp']})
    evaluation_strategy: Union[IntervalStrategy, str] = field(default=None, metadata={"help": "Deprecated. Use `eval_strategy` instead"})
    push_to_hub_model_id: Optional[str] = field(default=None, metadata={"help": "The name of the repository to which push the `Trainer`."})
    push_to_hub_organization: Optional[str] = field(default=None, metadata={"help": "The name of the organization in with to which push the `Trainer`."})
    push_to_hub_token: Optional[str] = field(default=None, metadata={"help": "The token to use to push to the Model Hub."})
    _n_gpu: int = field(init=False, repr=False, default=-1)
    mp_parameters: str = field(default="", metadata={"help": "Used by the SageMaker launcher to send mp-specific args. Ignored in Trainer"})
    auto_find_batch_size: bool = field(default=False, metadata={'help': 'Whether to automatically decrease the batch size in half and rerun the training loop again each time a CUDA Out-of-Memory was reached'})
    full_determinism: bool = field(default=False, metadata={'help': 'Whether to call enable_full_determinism instead of set_seed for reproducibility in distributed training. Important: this will negatively impact the performance, so only use it for debugging.'})
    torchdynamo: Optional[str] = field(default=None, metadata={'help': 'This argument is deprecated, use `--torch_compile_backend` instead.'})
    ray_scope: Optional[str] = field(default="last", metadata={'help': 'The scope to use when doing hyperparameter search with Ray. By default, `"last"` will be used. Ray will then use the last checkpoint of all trials, compare those, and select the best one. However, other options are also available. See the Ray documentation (https://docs.ray.io/en/latest/tune/api_docs/analysis.html#ray.tune.ExperimentAnalysis.get_best_trial) for more options.'})
    ddp_timeout: Optional[int] = field(default=1800, metadata={'help': 'Overrides the default timeout for distributed training (value should be given in seconds).'})
    torch_compile: bool = field(default=False, metadata={"help": "If set to `True`, the model will be wrapped in `torch.compile`."})
    torch_compile_backend: Optional[str] = field(default=None, metadata={'help': 'Which backend to use with `torch.compile`, passing one will trigger a model compilation.'})
    torch_compile_mode: Optional[str] = field(default=None, metadata={'help': 'Which mode to use with `torch.compile`, passing one will trigger a model compilation.'})
    dispatch_batches: Optional[bool] = field(default=None, metadata={"help": "Deprecated. Pass {'dispatch_batches':VALUE} to `accelerator_config`."})
    split_batches: Optional[bool] = field(default=None, metadata={"help": "Deprecated. Pass {'split_batches':True} to `accelerator_config`."})
    include_tokens_per_second: Optional[bool] = field(default=False, metadata={"help": "If set to `True`, the speed metrics will include `tgs` (tokens per second per device)."})
    include_num_input_tokens_seen: Optional[bool] = field(default=False, metadata={'help': 'If set to `True`, will track the number of input tokens seen throughout training. (May be slower in distributed training)'})
    neftune_noise_alpha: Optional[float] = field(default=None, metadata={'help': 'Activates neftune noise embeddings into the model. NEFTune has been proven to drastically improve model performances for instrcution fine-tuning. Check out the original paper here: https://arxiv.org/abs/2310.05914 and the original code here: https://github.com/neelsjain/NEFTune. Only supported for `PreTrainedModel` and `PeftModel` classes.'})
    optim_target_modules: Union[None, str, List[str]] = field(default=None, metadata={'help': 'Target modules for the optimizer defined in the `optim` argument. Only used for the GaLore optimizer at the moment.'})
    batch_eval_metrics: bool = field(default=False, metadata={"help": "Break eval metrics calculation into batches to save memory."})
    eval_on_start: bool = field(default=False, metadata={'help': 'Whether to run through the entire `evaluation` step at the very beginning of training as a sanity check.'})
    use_liger_kernel: Optional[bool] = field(default=False, metadata={"help": "Whether or not to enable the Liger Kernel for model training."})
    eval_use_gather_object: Optional[bool] = field(default=False, metadata={'help': 'Whether to run recursively gather object in a nested list/tuple/dictionary of objects from all devices.'})
    def __post_init__(self):
        for field in _VALID_DICT_FIELDS:
            passed_value = getattr(self, field)
            if isinstance(passed_value, str) and passed_value.startswith("{"):
                loaded_dict = json.loads(passed_value)
                loaded_dict = _convert_str_dict(loaded_dict)
                setattr(self, field, loaded_dict)
        if self.output_dir is not None: self.output_dir = os.path.expanduser(self.output_dir)
        if self.logging_dir is None and self.output_dir is not None: self.logging_dir = os.path.join(self.output_dir, default_logdir())
        if self.logging_dir is not None: self.logging_dir = os.path.expanduser(self.logging_dir)
        if self.disable_tqdm is None: self.disable_tqdm = logger.getEffectiveLevel() > logging.WARN
        if self.evaluation_strategy is not None: self.eval_strategy = self.evaluation_strategy
        if isinstance(self.eval_strategy, EvaluationStrategy): self.eval_strategy = self.eval_strategy.value
        if self.no_cuda: self.use_cpu = self.no_cuda
        self.eval_strategy = IntervalStrategy(self.eval_strategy)
        self.logging_strategy = IntervalStrategy(self.logging_strategy)
        self.save_strategy = IntervalStrategy(self.save_strategy)
        self.hub_strategy = HubStrategy(self.hub_strategy)
        self.lr_scheduler_type = SchedulerType(self.lr_scheduler_type)
        if self.do_eval is False and self.eval_strategy != IntervalStrategy.NO: self.do_eval = True
        if self.torch_empty_cache_steps is not None:
            if not (isinstance(self.torch_empty_cache_steps, int) or self.torch_empty_cache_steps > 0): raise ValueError(f"`torch_empty_cache_steps` must be an integer bigger than 0, got {self.torch_empty_cache_steps}.")
        if self.eval_strategy == IntervalStrategy.STEPS and (self.eval_steps is None or self.eval_steps == 0):
            if self.logging_steps > 0:
                logger.info(f"using `logging_steps` to initialize `eval_steps` to {self.logging_steps}")
                self.eval_steps = self.logging_steps
            else: raise ValueError(f"evaluation strategy {self.eval_strategy} requires either non-zero --eval_steps or --logging_steps")
        if self.logging_strategy == IntervalStrategy.STEPS and self.logging_steps == 0: raise ValueError(f"logging strategy {self.logging_strategy} requires non-zero --logging_steps")
        if self.logging_strategy == IntervalStrategy.STEPS and self.logging_steps > 1:
            if self.logging_steps != int(self.logging_steps): raise ValueError(f"--logging_steps must be an integer if bigger than 1: {self.logging_steps}")
            self.logging_steps = int(self.logging_steps)
        if self.eval_strategy == IntervalStrategy.STEPS and self.eval_steps > 1:
            if self.eval_steps != int(self.eval_steps): raise ValueError(f"--eval_steps must be an integer if bigger than 1: {self.eval_steps}")
            self.eval_steps = int(self.eval_steps)
        if self.save_strategy == IntervalStrategy.STEPS and self.save_steps > 1:
            if self.save_steps != int(self.save_steps): raise ValueError(f"--save_steps must be an integer if bigger than 1: {self.save_steps}")
            self.save_steps = int(self.save_steps)
        if self.load_best_model_at_end:
            if self.eval_strategy != self.save_strategy: raise ValueError(f"--load_best_model_at_end requires the save and eval strategy to match, but found\n- Evaluation strategy: {self.eval_strategy}\n- Save strategy: {self.save_strategy}")
            if self.eval_strategy == IntervalStrategy.STEPS and self.save_steps % self.eval_steps != 0:
                if self.eval_steps < 1 or self.save_steps < 1:
                    if not (self.eval_steps < 1 and self.save_steps < 1): raise ValueError(f"--load_best_model_at_end requires the saving steps to be a multiple of the evaluation steps, which cannot get guaranteed when mixing ratio and absolute steps for save_steps {self.save_steps} and eval_steps {self.eval_steps}.")
                    LARGE_MULTIPLIER = 1_000_000
                    if (self.save_steps * LARGE_MULTIPLIER) % (self.eval_steps * LARGE_MULTIPLIER) != 0: raise ValueError(f"--load_best_model_at_end requires the saving steps to be a multiple of the evaluation steps, but found {self.save_steps}, which is not a multiple of {self.eval_steps}.")
                raise ValueError(f"--load_best_model_at_end requires the saving steps to be a round multiple of the evaluation steps, but found {self.save_steps}, which is not a round multiple of {self.eval_steps}.")
        safetensors_available = is_safetensors_available()
        if self.save_safetensors and not safetensors_available: raise ValueError(f"--save_safetensors={self.save_safetensors} requires safetensors to be installed!")
        if not self.save_safetensors and safetensors_available: logger.info(f"Found safetensors installation, but --save_safetensors={self.save_safetensors}. Safetensors should be a preferred weights saving format due to security and performance reasons.")
        if (self.load_best_model_at_end or self.lr_scheduler_type == SchedulerType.REDUCE_ON_PLATEAU) and self.metric_for_best_model is None: self.metric_for_best_model = "loss"
        if self.greater_is_better is None and self.metric_for_best_model is not None: self.greater_is_better = not (self.metric_for_best_model.endswith("loss"))
        if self.run_name is None: self.run_name = self.output_dir
        if self.framework == "pt" and is_torch_available():
            if self.fp16_backend and self.fp16_backend != "auto": self.half_precision_backend = self.fp16_backend
            if self.bf16 or self.bf16_full_eval:
                if self.use_cpu and not is_torch_bf16_cpu_available() and not is_torch_xla_available(): raise ValueError("Your setup doesn't support bf16/(cpu, tpu, neuroncore). You need torch>=1.10")
                elif not self.use_cpu:
                    if torch.cuda.is_available() and not is_torch_bf16_gpu_available(): raise ValueError("Your setup doesn't support bf16/gpu. You need torch>=1.10, using Ampere GPU with cuda>=11.0")
                    elif not is_torch_xpu_available():
                        from .pytorch_utils import is_torch_greater_or_equal_than_1_12
                        if not is_torch_greater_or_equal_than_1_12: raise ValueError("Your setup doesn't support bf16/xpu. You need torch>=1.12, using Intel XPU/GPU with IPEX installed")
        if self.fp16 and self.bf16: raise ValueError("At most one of fp16 and bf16 can be True, but not both")
        if self.fp16_full_eval and self.bf16_full_eval: raise ValueError("At most one of fp16 and bf16 can be True for full eval, but not both")
        if self.bf16:
            if self.half_precision_backend == "apex": raise ValueError(" `--half_precision_backend apex`: GPU bf16 is not supported by apex.")
        if self.lr_scheduler_type == SchedulerType.REDUCE_ON_PLATEAU:
            if self.eval_strategy == IntervalStrategy.NO: raise ValueError("lr_scheduler_type reduce_lr_on_plateau requires an eval strategy")
            if not is_torch_available(): raise ValueError("lr_scheduler_type reduce_lr_on_plateau requires torch>=0.2.0")
        self.optim = OptimizerNames(self.optim)
        if self.adafactor: self.optim = OptimizerNames.ADAFACTOR
        if self.optim == OptimizerNames.ADAMW_TORCH_FUSED and is_torch_available():
            if version.parse(version.parse(torch.__version__).base_version) < version.parse("2.0.0"): raise ValueError("--optim adamw_torch_fused requires PyTorch 2.0 or higher")
            if version.parse(version.parse(torch.__version__).base_version) == version.parse("2.0.0") and self.fp16: raise ValueError("--optim adamw_torch_fused with --fp16 requires PyTorch>2.0")
        if is_sapiens_accelerator_available():
            if not isinstance(self.accelerator_config, (AcceleratorConfig)):
                if self.accelerator_config is None: self.accelerator_config = AcceleratorConfig()
                elif isinstance(self.accelerator_config, dict): self.accelerator_config = AcceleratorConfig(**self.accelerator_config)
                elif isinstance(self.accelerator_config, type): raise NotImplementedError("Tried passing in a callable to `accelerator_config`, but this is not supported. Please pass in a fully constructed `AcceleratorConfig` object instead.")
                else: self.accelerator_config = AcceleratorConfig.from_json_file(self.accelerator_config)
            if self.dispatch_batches is not None: self.accelerator_config.dispatch_batches = self.dispatch_batches
            if self.split_batches is not None: self.accelerator_config.split_batches = self.split_batches
        if self.framework == "pt" and is_torch_available(): self.device
        if self.torchdynamo is not None: self.torch_compile_backend = self.torchdynamo
        if (self.torch_compile_mode is not None or self.torch_compile_backend is not None) and not self.torch_compile: self.torch_compile = True
        if self.torch_compile and self.torch_compile_backend is None: self.torch_compile_backend = "inductor"
        if self.torch_compile:
            prefix = "SAPIENS_ACCELERATOR_DYNAMO_"
            os.environ[prefix + "BACKEND"] = self.torch_compile_backend
            if self.torch_compile_mode is not None: os.environ[prefix + "MODE"] = self.torch_compile_mode
        if self.framework == "pt" and is_torch_available() and self.torch_compile:
            if is_torch_tf32_available():
                if self.tf32 is None and not self.fp16 or self.bf16:
                    logger.info("Setting TF32 in CUDA backends to speedup torch compile, you won't see any improvement otherwise.")
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True
            else: logger.warning("The speedups for torchdynamo mostly come wih GPU Ampere or higher and which is not detected here.")
        if self.framework == "pt" and is_torch_available() and self.tf32 is not None:
            if self.tf32:
                if is_torch_tf32_available():
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True
                else: raise ValueError("--tf32 requires Ampere or a newer GPU arch, cuda>=11 and torch>=1.7")
            else:
                if is_torch_tf32_available():
                    torch.backends.cuda.matmul.allow_tf32 = False
                    torch.backends.cudnn.allow_tf32 = False
        if self.half_precision_backend != "apex":
            mixed_precision_dtype = os.environ.get("SAPIENS_ACCELERATOR_MIXED_PRECISION", "no")
            if self.fp16: mixed_precision_dtype = "fp16"
            elif self.bf16: mixed_precision_dtype = "bf16"
            os.environ["SAPIENS_ACCELERATOR_MIXED_PRECISION"] = mixed_precision_dtype
        if self.report_to is None:
            logger.info("The default value for the training argument `--report_to` will change in v5 (from all installed integrations to none). In v5, you will need to use `--report_to all` to get the same behavior as now. You should start updating your code and make this info disappear :-).")
            self.report_to = "all"
        if self.report_to == "all" or self.report_to == ["all"]:
            from .integrations import get_available_reporting_integrations
            self.report_to = get_available_reporting_integrations()
            if "codecarbon" in self.report_to and torch.version.hip:
                logger.warning("When using the Trainer, CodeCarbonCallback requires the `codecarbon` package, which is not compatible with AMD ROCm (https://github.com/mlco2/codecarbon/pull/490). Automatically disabling the codecarbon callback.")
                self.report_to.remove("codecarbon")
        elif self.report_to == "none" or self.report_to == ["none"]: self.report_to = []
        elif not isinstance(self.report_to, list): self.report_to = [self.report_to]
        if self.warmup_ratio < 0 or self.warmup_ratio > 1: raise ValueError("warmup_ratio must lie in range [0,1]")
        elif self.warmup_ratio > 0 and self.warmup_steps > 0: logger.info("Both warmup_ratio and warmup_steps given, warmup_steps will override any effect of warmup_ratio during training")
        if not isinstance(self.warmup_steps, int) or self.warmup_steps < 0: raise ValueError("warmup_steps must be of type int and must be 0 or a positive integer.")
        if isinstance(self.fsdp, bool): self.fsdp = [FSDPOption.FULL_SHARD] if self.fsdp else ""
        if isinstance(self.fsdp, str): self.fsdp = [FSDPOption(s) for s in self.fsdp.split()]
        if self.fsdp == [FSDPOption.OFFLOAD]: raise ValueError("`--fsdp offload` can't work on its own. It needs to be added to `--fsdp full_shard` or "+'`--fsdp shard_grad_op`. For example, `--fsdp "full_shard offload"`.')
        elif FSDPOption.FULL_SHARD in self.fsdp and FSDPOption.SHARD_GRAD_OP in self.fsdp: raise ValueError("`--fsdp full_shard` is not compatible with `--fsdp shard_grad_op`.")
        if self.gradient_checkpointing and (FSDPOption.FULL_SHARD in self.fsdp or FSDPOption.HYBRID_SHARD in self.fsdp): logger.warning("When using FSDP full shard, instead of using `gradient_checkpointing` in TrainingArguments, please use `activation_checkpointing` in `fsdp_config`. The former introduces a redundant AllGather operation in backward pass.")
        if self.fsdp_config is None: self.fsdp_config = {}
        if isinstance(self.fsdp_config, str):
            if len(self.fsdp) == 0: warnings.warn("`--fsdp_config` is useful only when `--fsdp` is specified.")
            with io.open(self.fsdp_config, "r", encoding="utf-8") as f:
                self.fsdp_config = json.load(f)
                for k in list(self.fsdp_config.keys()):
                    if k.startswith("fsdp_"):
                        v = self.fsdp_config.pop(k)
                        self.fsdp_config[k[5:]] = v
        if self.fsdp_min_num_params > 0: warnings.warn("using `--fsdp_min_num_params` is deprecated. Use fsdp_config instead ", FutureWarning)
        self.fsdp_config["min_num_params"] = max(self.fsdp_config.get("min_num_params", 0), self.fsdp_min_num_params)
        if isinstance(self.fsdp_config.get("transformer_layer_cls_to_wrap", None), str): self.fsdp_config["transformer_layer_cls_to_wrap"] = [self.fsdp_config["transformer_layer_cls_to_wrap"]]
        if self.fsdp_transformer_layer_cls_to_wrap is not None:
            warnings.warn("using `--fsdp_transformer_layer_cls_to_wrap` is deprecated. Use fsdp_config instead ", FutureWarning)
            self.fsdp_config["transformer_layer_cls_to_wrap"] = self.fsdp_config.get("transformer_layer_cls_to_wrap", []) + [self.fsdp_transformer_layer_cls_to_wrap]
        if len(self.fsdp) == 0 and self.fsdp_config["min_num_params"] > 0: warnings.warn("`min_num_params` is useful only when `--fsdp` is specified.")
        if len(self.fsdp) == 0 and self.fsdp_config.get("transformer_layer_cls_to_wrap", None) is not None: warnings.warn("`transformer_layer_cls_to_wrap` is useful only when `--fsdp` is specified.")
        if (len(self.fsdp) > 0 and self.fsdp_config["min_num_params"] > 0 and self.fsdp_config.get("transformer_layer_cls_to_wrap", None) is not None): raise ValueError("`min_num_params` and `transformer_layer_cls_to_wrap` are mutually exclusive.")
        self.fsdp_config["xla"] = self.fsdp_config.get("xla", False)
        self.fsdp_config["xla_fsdp_v2"] = self.fsdp_config.get("xla_fsdp_v2", False)
        self.fsdp_config["xla_fsdp_grad_ckpt"] = self.fsdp_config.get("xla_fsdp_grad_ckpt", False)
        if self.fsdp_config["xla"]:
            if len(self.fsdp) > 0:
                self.xla_fsdp_config = self.fsdp_config.get("xla_fsdp_settings", {}).copy()
                if "compute_dtype" in self.xla_fsdp_config: self.xla_fsdp_config["compute_dtype"] = getattr(torch, self.xla_fsdp_config["compute_dtype"])
                if "buffer_dtype" in self.xla_fsdp_config: self.xla_fsdp_config["buffer_dtype"] = getattr(torch, self.xla_fsdp_config["buffer_dtype"])
            else: warnings.warn("XLA FSDP can be used only when `--fsdp` is specified.")
        else:
            if self.fsdp_config["xla_fsdp_grad_ckpt"]: warnings.warn("`--xla_fsdp_grad_ckpt` is useful only when `--xla` is set to true.")
        if len(self.fsdp) > 0 and is_sapiens_accelerator_available("0.28.0"):
            os.environ["SAPIENS_ACCELERATOR_USE_FSDP"] = "true"
            from sapiens_accelerator.utils.constants import (FSDP_AUTO_WRAP_POLICY, FSDP_SHARDING_STRATEGY)
            prefix = "FSDP_"
            for fsdp_option in self.fsdp:
                if fsdp_option.upper() in FSDP_SHARDING_STRATEGY: os.environ[f"{prefix}SHARDING_STRATEGY"] = str(FSDP_SHARDING_STRATEGY.index(fsdp_option.upper()) + 1)
                elif fsdp_option == FSDPOption.OFFLOAD: os.environ[f"{prefix}OFFLOAD_PARAMS"] = "true"
                elif fsdp_option == FSDPOption.AUTO_WRAP:
                    os.environ[f"{prefix}AUTO_WRAP_POLICY"] = FSDP_AUTO_WRAP_POLICY[0]
                    if self.fsdp_config["min_num_params"] > 0:
                        os.environ[f"{prefix}MIN_NUM_PARAMS"] = str(self.fsdp_config["min_num_params"])
                        os.environ[f"{prefix}AUTO_WRAP_POLICY"] = FSDP_AUTO_WRAP_POLICY[1]
                    elif self.fsdp_config.get("transformer_layer_cls_to_wrap", None) is not None: os.environ[f"{prefix}TRANSFORMER_CLS_TO_WRAP"] = ",".join(self.fsdp_config["transformer_layer_cls_to_wrap"])
            prefetch_policy = self.fsdp_config.get("backward_prefetch", "NO_PREFETCH")
            os.environ[f"{prefix}BACKWARD_PREFETCH"] = prefetch_policy.upper()
            os.environ[f"{prefix}FORWARD_PREFETCH"] = str(self.fsdp_config.get("forward_prefetch", "false")).lower()
            sync_module_states = str(self.fsdp_config.get("sync_module_states", "true")).lower()
            cpu_ram_efficient_loading = str(self.fsdp_config.get("cpu_ram_efficient_loading", "false")).lower()
            if sync_module_states == "false" and cpu_ram_efficient_loading == "true": raise ValueError('`sync_module_states` must be `"True"` if `cpu_ram_efficient_loading` is `"True"`')
            os.environ[f"{prefix}SYNC_MODULE_STATES"] = sync_module_states
            os.environ[f"{prefix}CPU_RAM_EFFICIENT_LOADING"] = cpu_ram_efficient_loading
            os.environ[f"{prefix}USE_ORIG_PARAMS"] = str(self.fsdp_config.get("use_orig_params", "true")).lower()
        if self.tpu_metrics_debug:
            if self.debug is None: self.debug = " tpu_metrics_debug"
            else: self.debug += " tpu_metrics_debug"
            self.tpu_metrics_debug = False
        if isinstance(self.debug, str): self.debug = [DebugOption(s) for s in self.debug.split()]
        elif self.debug is None: self.debug = []
        self.deepspeed_plugin = None
        if self.deepspeed:
            if not is_sapiens_accelerator_available(): raise ValueError(f"--deepspeed requires SapiensAccelerator to be installed: `pip install 'sapiens_accelerator>={SAPIENS_ACCELERATOR_MIN_VERSION}'`.")
            from sapiens_transformers.integrations.deepspeed import HfTrainerDeepSpeedConfig
            self.hf_deepspeed_config = HfTrainerDeepSpeedConfig(self.deepspeed)
            self.hf_deepspeed_config.trainer_config_process(self)
            from sapiens_accelerator.utils import DeepSpeedPlugin
            os.environ["SAPIENS_ACCELERATOR_USE_DEEPSPEED"] = "true"
            self.deepspeed_plugin = DeepSpeedPlugin(hf_ds_config=self.hf_deepspeed_config)
        elif strtobool(os.environ.get("SAPIENS_ACCELERATOR_USE_DEEPSPEED", "false")):
            from sapiens_accelerator.utils import DeepSpeedPlugin
            self.deepspeed_plugin = DeepSpeedPlugin()
            mixed_precision = os.environ.get("SAPIENS_ACCELERATOR_MIXED_PRECISION", "no")
            self.deepspeed_plugin.set_mixed_precision(mixed_precision)
            self.deepspeed_plugin.set_deepspeed_weakref()
        if self.use_cpu: self.dataloader_pin_memory = False
        if ((not is_torch_available() or is_torch_greater_or_equal_than_2_0) and self.dataloader_num_workers == 0 and self.dataloader_prefetch_factor is not None): raise ValueError("--dataloader_prefetch_factor can only be set when data is loaded in a different process, i.e. when --dataloader_num_workers > 1.")
        if self.push_to_hub_token is not None: self.hub_token = self.push_to_hub_token
        if self.push_to_hub_model_id is not None: self.hub_model_id = get_full_repo_name(self.push_to_hub_model_id, organization=self.push_to_hub_organization, token=self.hub_token)
        elif self.push_to_hub_organization is not None: self.hub_model_id = f"{self.push_to_hub_organization}/{Path(self.output_dir).name}"
        if self.eval_use_gather_object and not is_sapiens_accelerator_available("0.30.0"): raise ValueError("--eval_use_gather_object requires SapiensAccelerator to be version of `sapiens_accelerator` > 0.30.0. This is not supported and we recommend you to update your version.")
    def __str__(self):
        self_as_dict = asdict(self)
        del self_as_dict["per_gpu_train_batch_size"]
        del self_as_dict["per_gpu_eval_batch_size"]
        self_as_dict = {k: f"<{k.upper()}>" if k.endswith("_token") else v for k, v in self_as_dict.items()}
        attrs_as_str = [f"{k}={v},\n" for k, v in sorted(self_as_dict.items())]
        return f"{self.__class__.__name__}(\n{''.join(attrs_as_str)})"
    __repr__ = __str__
    @property
    def train_batch_size(self) -> int:
        if self.per_gpu_train_batch_size: logger.warning("Using deprecated `--per_gpu_train_batch_size` argument which will be removed in a future version. Using `--per_device_train_batch_size` is preferred.")
        per_device_batch_size = self.per_gpu_train_batch_size or self.per_device_train_batch_size
        train_batch_size = per_device_batch_size * max(1, self.n_gpu)
        return train_batch_size
    @property
    def eval_batch_size(self) -> int:
        if self.per_gpu_eval_batch_size: logger.warning("Using deprecated `--per_gpu_eval_batch_size` argument which will be removed in a future version. Using `--per_device_eval_batch_size` is preferred.")
        per_device_batch_size = self.per_gpu_eval_batch_size or self.per_device_eval_batch_size
        eval_batch_size = per_device_batch_size * max(1, self.n_gpu)
        return eval_batch_size
    @property
    def ddp_timeout_delta(self) -> timedelta: return timedelta(seconds=self.ddp_timeout)
    @cached_property
    def _setup_devices(self) -> "torch.device":
        requires_backends(self, ["torch"])
        logger.info("PyTorch: setting up devices")
        if not is_sagemaker_mp_enabled():
            if not is_sapiens_accelerator_available(): raise ImportError(f"Using the `Trainer` with `PyTorch` requires `sapiens_accelerator>={SAPIENS_ACCELERATOR_MIN_VERSION}`: Please run `pip install transformers[torch]` or `pip install 'sapiens_accelerator>={SAPIENS_ACCELERATOR_MIN_VERSION}'`")
        accelerator_state_kwargs = {"enabled": True, "use_configured_state": False}
        if isinstance(self.accelerator_config, AcceleratorConfig): accelerator_state_kwargs["use_configured_state"] = self.accelerator_config.pop("use_configured_state", False)
        if accelerator_state_kwargs["use_configured_state"]:
            if PartialState._shared_state == {}: raise ValueError("Passing `'use_configured_state':True` to the AcceleratorConfig requires a pre-configured `AcceleratorState` or `PartialState` to be defined before calling `TrainingArguments`. ")
            self.distributed_state = PartialState(cpu=self.use_cpu)
            if self.deepspeed and self.distributed_state.distributed_type != DistributedType.DEEPSPEED: raise RuntimeError("Tried to use an already configured `Accelerator` or `PartialState` that was not initialized for DeepSpeed, but also passed in a `deepspeed` configuration to the `TrainingArguments`. Please set `use_configured_state:False` instead or setup your `Accelerator` or `PartialState` properly.")
        else:
            AcceleratorState._reset_state(reset_partial_state=True)
            self.distributed_state = None
        if not self.use_ipex and "SAPIENS_ACCELERATOR_USE_IPEX" not in os.environ: os.environ["SAPIENS_ACCELERATOR_USE_IPEX"] = "false"
        self._n_gpu = 1
        if self.use_cpu or strtobool(os.environ.get("SAPIENS_ACCELERATOR_USE_CPU", "False")):
            accelerator_state_kwargs["cpu"] = True
            accelerator_state_kwargs["backend"] = self.ddp_backend
            self._n_gpu = 0
        elif is_sagemaker_mp_enabled():
            accelerator_state_kwargs["enabled"] = False
            local_rank = smp.local_rank()
            device = torch.device("cuda", local_rank)
            torch.cuda.set_device(device)
        elif is_sagemaker_dp_enabled(): accelerator_state_kwargs["_use_sagemaker_dp"] = True
        elif self.deepspeed:
            accelerator_state_kwargs["use_deepspeed"] = True
            accelerator_state_kwargs["timeout"] = timedelta(seconds=self.ddp_timeout)
        else:
            accelerator_state_kwargs["backend"] = self.ddp_backend
            accelerator_state_kwargs["timeout"] = timedelta(seconds=self.ddp_timeout)
        if accelerator_state_kwargs.pop("enabled", False) and not accelerator_state_kwargs.pop("use_configured_state", False):
            use_deepspeed = accelerator_state_kwargs.pop("use_deepspeed", False)
            if use_deepspeed: os.environ["SAPIENS_ACCELERATOR_USE_DEEPSPEED"] = "true"
            self.distributed_state = PartialState(**accelerator_state_kwargs)
            if use_deepspeed: del os.environ["SAPIENS_ACCELERATOR_USE_DEEPSPEED"]
        if not is_sagemaker_mp_enabled():
            device = self.distributed_state.device
            self.local_rank = self.distributed_state.local_process_index
        if dist.is_available() and dist.is_initialized() and self.parallel_mode != ParallelMode.DISTRIBUTED: logger.warning("torch.distributed process group is initialized, but parallel_mode != ParallelMode.DISTRIBUTED. In order to use Torch DDP, launch your script with `python -m torch.distributed.launch")
        if is_torch_xla_available():
            device = self.distributed_state.device
            self._n_gpu = 0
        elif is_sagemaker_dp_enabled() or is_sagemaker_mp_enabled(): pass
        elif self.distributed_state.distributed_type == DistributedType.NO:
            if self.use_mps_device:
                if device.type != "mps": raise ValueError("Either you do not have an MPS-enabled device on this machine or MacOS version is not 12.3+ or current PyTorch install was not built with MPS enabled.")
            if self.use_cpu: device = torch.device("cpu")
            elif is_torch_mps_available(): device = torch.device("mps")
            elif is_torch_xpu_available():
                if not is_ipex_available() and not is_sapiens_accelerator_available("0.32.0.dev"): raise ImportError("Using the XPU PyTorch backend requires `sapiens_accelerator>=0.32.0.dev`")
                device = torch.device("xpu:0")
                torch.xpu.set_device(device)
            elif is_torch_mlu_available():
                device = torch.device("mlu:0")
                torch.mlu.set_device(device)
            elif is_torch_musa_available():
                device = torch.device("musa:0")
                torch.musa.set_device(device)
            elif is_torch_npu_available():
                device = torch.device("npu:0")
                torch.npu.set_device(device)
            else:
                device = torch.device("cuda:0" if torch.cuda.is_available() else os.environ.get("SAPIENS_ACCELERATOR_TORCH_DEVICE", "cpu"))
                self._n_gpu = torch.cuda.device_count()
                if device.type == "cuda": torch.cuda.set_device(device)
        return device
    @property
    def device(self) -> "torch.device":
        requires_backends(self, ["torch"])
        return self._setup_devices
    @property
    def n_gpu(self):
        requires_backends(self, ["torch"])
        if not hasattr(self, "_n_gpu"): _ = self._setup_devices
        return self._n_gpu
    @property
    def parallel_mode(self):
        requires_backends(self, ["torch"])
        if is_torch_xla_available(): return ParallelMode.TPU
        elif is_sagemaker_mp_enabled(): return ParallelMode.SAGEMAKER_MODEL_PARALLEL
        elif is_sagemaker_dp_enabled(): return ParallelMode.SAGEMAKER_DATA_PARALLEL
        elif (self.distributed_state is not None and self.distributed_state.distributed_type != DistributedType.NO) or (self.distributed_state is None and self.local_rank != -1): return ParallelMode.DISTRIBUTED
        elif self.n_gpu > 1: return ParallelMode.NOT_DISTRIBUTED
        else: return ParallelMode.NOT_PARALLEL
    @property
    def world_size(self):
        requires_backends(self, ["torch"])
        if self.distributed_state is not None: return self.distributed_state.num_processes
        elif is_sagemaker_mp_enabled(): return smp.dp_size() if not smp.state.cfg.prescaled_batch else smp.rdp_size()
        return 1
    @property
    def process_index(self):
        requires_backends(self, ["torch"])
        if self.distributed_state is not None: return self.distributed_state.process_index
        elif is_sagemaker_mp_enabled(): return smp.dp_rank() if not smp.state.cfg.prescaled_batch else smp.rdp_rank()
        return 0
    @property
    def local_process_index(self):
        requires_backends(self, ["torch"])
        if self.distributed_state is not None: return self.distributed_state.local_process_index
        elif is_sagemaker_mp_enabled(): return smp.local_rank()
        return 0
    @property
    def should_log(self):
        if self.log_on_each_node: return self.local_process_index == 0
        else:
            if is_sagemaker_mp_enabled(): return smp.rank() == 0
            else: return self.process_index == 0
    @property
    def should_save(self):
        if self.save_on_each_node: return self.local_process_index == 0
        else:
            if is_sagemaker_mp_enabled(): return smp.rank() == 0
            else: return self.process_index == 0
    def get_process_log_level(self):
        log_level = trainer_log_levels[self.log_level]
        log_level_replica = trainer_log_levels[self.log_level_replica]
        log_level_main_node = logging.get_verbosity() if log_level == -1 else log_level
        log_level_replica_node = logging.get_verbosity() if log_level_replica == -1 else log_level_replica
        return log_level_main_node if self.should_log else log_level_replica_node
    @property
    def place_model_on_device(self): return not is_sagemaker_mp_enabled()
    @property
    def _no_sync_in_gradient_accumulation(self): return not (self.deepspeed or is_sagemaker_dp_enabled() or is_sagemaker_mp_enabled() or is_torch_neuroncore_available())
    @contextlib.contextmanager
    def main_process_first(self, local=True, desc="work"):
        if is_torch_available() and self.world_size > 1:
            main_process_desc = "main local process" if local else "main process"
            if self.distributed_state is not None: is_main_process = (self.distributed_state.is_local_main_process if local else self.distributed_state.is_main_process)
            elif is_sagemaker_mp_enabled(): is_main_process = smp.rank() == 0
            try:
                if not is_main_process:
                    logger.debug(f"{self.process_index}: waiting for the {main_process_desc} to perform {desc}")
                    if is_torch_xla_available(): xm.rendezvous(desc)
                    else: dist.barrier()
                yield
            finally:
                if is_main_process:
                    logger.debug(f"{self.process_index}: {main_process_desc} completed {desc}, releasing all replicas")
                    if is_torch_xla_available(): xm.rendezvous(desc)
                    else: dist.barrier()
        else: yield
    def get_warmup_steps(self, num_training_steps: int):
        warmup_steps = (self.warmup_steps if self.warmup_steps > 0 else math.ceil(num_training_steps * self.warmup_ratio))
        return warmup_steps
    def _dict_torch_dtype_to_str(self, d: Dict[str, Any]) -> None:
        if d.get("torch_dtype", None) is not None and not isinstance(d["torch_dtype"], str): d["torch_dtype"] = str(d["torch_dtype"]).split(".")[1]
        for value in d.values():
            if isinstance(value, dict): self._dict_torch_dtype_to_str(value)
    def to_dict(self):
        d = {field.name: getattr(self, field.name) for field in fields(self) if field.init}
        for k, v in d.items():
            if isinstance(v, Enum): d[k] = v.value
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], Enum): d[k] = [x.value for x in v]
            if k.endswith("_token"): d[k] = f"<{k.upper()}>"
            if is_sapiens_accelerator_available() and isinstance(v, AcceleratorConfig): d[k] = v.to_dict()
        self._dict_torch_dtype_to_str(d)
        return d
    def to_json_string(self): return json.dumps(self.to_dict(), indent=2)
    def to_sanitized_dict(self) -> Dict[str, Any]:
        d = self.to_dict()
        d = {**d, **{"train_batch_size": self.train_batch_size, "eval_batch_size": self.eval_batch_size}}
        valid_types = [bool, int, float, str]
        if is_torch_available(): valid_types.append(torch.Tensor)
        return {k: v if type(v) in valid_types else str(v) for k, v in d.items()}
    def set_training(self, learning_rate: float = 5e-5, batch_size: int = 8, weight_decay: float = 0, num_epochs: float = 3, max_steps: int = -1, gradient_accumulation_steps: int = 1, seed: int = 42, gradient_checkpointing: bool = False):
        self.do_train = True
        self.learning_rate = learning_rate
        self.per_device_train_batch_size = batch_size
        self.weight_decay = weight_decay
        self.num_train_epochs = num_epochs
        self.max_steps = max_steps
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.seed = seed
        self.gradient_checkpointing = gradient_checkpointing
        return self
    def set_evaluate(self, strategy: Union[str, IntervalStrategy] = "no", steps: int = 500, batch_size: int = 8, accumulation_steps: Optional[int] = None, delay: Optional[float] = None, loss_only: bool = False, jit_mode: bool = False):
        self.eval_strategy = IntervalStrategy(strategy)
        if self.eval_strategy == IntervalStrategy.STEPS and steps == 0: raise ValueError("Setting `strategy` as 'steps' requires a positive value for `steps`.")
        self.do_eval = self.eval_strategy != IntervalStrategy.NO
        self.eval_steps = steps
        self.per_device_eval_batch_size = batch_size
        self.eval_accumulation_steps = accumulation_steps
        self.eval_delay = delay
        self.prediction_loss_only = loss_only
        self.jit_mode_eval = jit_mode
        return self
    def set_testing(self, batch_size: int = 8, loss_only: bool = False, jit_mode: bool = False):
        self.do_predict = True
        self.per_device_eval_batch_size = batch_size
        self.prediction_loss_only = loss_only
        self.jit_mode_eval = jit_mode
        return self
    def set_save(self, strategy: Union[str, IntervalStrategy] = "steps", steps: int = 500, total_limit: Optional[int] = None, on_each_node: bool = False):
        self.save_strategy = IntervalStrategy(strategy)
        if self.save_strategy == IntervalStrategy.STEPS and steps == 0: raise ValueError("Setting `strategy` as 'steps' requires a positive value for `steps`.")
        self.save_steps = steps
        self.save_total_limit = total_limit
        self.save_on_each_node = on_each_node
        return self
    def set_logging(self, strategy: Union[str, IntervalStrategy] = "steps", steps: int = 500, report_to: Union[str, List[str]] = "none", level: str = "passive", first_step: bool = False, nan_inf_filter: bool = False, on_each_node: bool = False, replica_level: str = "passive"):
        self.logging_strategy = IntervalStrategy(strategy)
        if self.logging_strategy == IntervalStrategy.STEPS and steps == 0: raise ValueError("Setting `strategy` as 'steps' requires a positive value for `steps`.")
        self.logging_steps = steps
        self.report_to = report_to
        self.log_level = level
        self.logging_first_step = first_step
        self.logging_nan_inf_filter = nan_inf_filter
        self.log_on_each_node = on_each_node
        self.log_level_replica = replica_level
        return self
    def set_push_to_hub(self, model_id: str, strategy: Union[str, HubStrategy] = "every_save", token: Optional[str] = None, private_repo: bool = False, always_push: bool = False):
        self.push_to_hub = True
        self.hub_model_id = model_id
        self.hub_strategy = HubStrategy(strategy)
        self.hub_token = token
        self.hub_private_repo = private_repo
        self.hub_always_push = always_push
        return self
    def set_optimizer(self, name: Union[str, OptimizerNames] = "adamw_torch", learning_rate: float = 5e-5, weight_decay: float = 0, beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-8, args: Optional[str] = None):
        self.optim = OptimizerNames(name)
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.adam_beta1 = beta1
        self.adam_beta2 = beta2
        self.adam_epsilon = epsilon
        self.optim_args = args
        return self
    def set_lr_scheduler(self, name: Union[str, SchedulerType] = "linear", num_epochs: float = 3.0, max_steps: int = -1, warmup_ratio: float = 0, warmup_steps: int = 0):
        self.lr_scheduler_type = SchedulerType(name)
        self.num_train_epochs = num_epochs
        self.max_steps = max_steps
        self.warmup_ratio = warmup_ratio
        self.warmup_steps = warmup_steps
        return self
    def set_dataloader(self, train_batch_size: int = 8, eval_batch_size: int = 8, drop_last: bool = False, num_workers: int = 0, pin_memory: bool = True, persistent_workers: bool = False, prefetch_factor: Optional[int] = None, auto_find_batch_size: bool = False, ignore_data_skip: bool = False, sampler_seed: Optional[int] = None):
        self.per_device_train_batch_size = train_batch_size
        self.per_device_eval_batch_size = eval_batch_size
        self.dataloader_drop_last = drop_last
        self.dataloader_num_workers = num_workers
        self.dataloader_pin_memory = pin_memory
        self.dataloader_persistent_workers = persistent_workers
        self.dataloader_prefetch_factor = prefetch_factor
        self.auto_find_batch_size = auto_find_batch_size
        self.ignore_data_skip = ignore_data_skip
        self.data_seed = sampler_seed
        return self
class ParallelMode(Enum):
    NOT_PARALLEL = "not_parallel"
    NOT_DISTRIBUTED = "not_distributed"
    DISTRIBUTED = "distributed"
    SAGEMAKER_MODEL_PARALLEL = "sagemaker_model_parallel"
    SAGEMAKER_DATA_PARALLEL = "sagemaker_data_parallel"
    TPU = "tpu"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
