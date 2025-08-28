"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (SAPIENS_ACCELERATOR_MIN_VERSION, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_WEIGHTS_NAME, CONFIG_NAME, DUMMY_INPUTS, FLAX_WEIGHTS_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_NAME, TF2_WEIGHTS_NAME, TF_WEIGHTS_NAME, WEIGHTS_INDEX_NAME,
WEIGHTS_NAME, ContextManagers, ModelOutput, PushToHubMixin, cached_file, copy_func, download_url, extract_commit_hash, has_file, is_sapiens_accelerator_available, is_sapiens_machine_available, is_flash_attn_2_available, is_offline_mode,
is_optimum_available, is_peft_available, is_remote_url, is_safetensors_available, is_torch_sdpa_available, is_torch_xla_available, logging, replace_return_docstrings, strtobool)
from .pytorch_utils import (Conv1D, apply_chunking_to_forward, find_pruneable_heads_and_indices, id_tensor_storage, is_torch_greater_or_equal_than_1_13, prune_conv1d_layer, prune_layer, prune_linear_layer)
from .utils.import_utils import (ENV_VARS_TRUE_VALUES, is_sagemaker_mp_enabled, is_torch_fx_proxy, is_torchdynamo_compiling)
from .utils.hub import convert_file_size_to_int, create_and_tag_model_card, get_checkpoint_shard_files
from .integrations import PeftAdapterMixin, deepspeed_config, is_deepspeed_zero3_enabled
from .utils.quantization_config import SapiensMachineConfig, QuantizationMethod
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from .integrations.flash_attention import flash_attention_forward
from .integrations.flex_attention import flex_attention_forward
from .integrations.sdpa_attention import sdpa_attention_forward
from huggingface_hub import split_torch_state_dict_into_shards
from .quantizers.quantizers_utils import get_module_from_name
from .generation import GenerationConfig, GenerationMixin
from .dynamic_module_utils import custom_object_save
from .quantizers import AutoHfQuantizer, HfQuantizer
from .safetensors_conversion import auto_conversion
from .configuration_utils import PretrainedConfig
from torch.nn import CrossEntropyLoss, Identity
from torch.utils.checkpoint import checkpoint
from .activations import get_activation
from contextlib import contextmanager
from functools import partial, wraps
from dataclasses import dataclass
from zipfile import is_zipfile
from packaging import version
from threading import Thread
from torch import Tensor, nn
import importlib.metadata
import collections
import itertools
import functools
import tempfile
import warnings
import inspect
import shutil
import torch
import copy
import json
import gc
import os
import re
XLA_USE_BF16, ALL_ATTENTION_FUNCTIONS = os.environ.get("XLA_USE_BF16", "0").upper(), None
XLA_DOWNCAST_BF16 = os.environ.get("XLA_DOWNCAST_BF16", "0").upper()
if is_sapiens_accelerator_available():
    from sapiens_accelerator import dispatch_model, infer_auto_device_map, init_empty_weights
    from sapiens_accelerator.hooks import add_hook_to_module
    from sapiens_accelerator.utils import (check_tied_parameters_on_same_device, extract_model_from_parallel, find_tied_parameters, get_balanced_memory, get_max_memory, load_offloaded_weights, offload_weight, save_offload_index, set_module_tensor_to_device)
    sapiens_accelerator_version = version.parse(importlib.metadata.version("sapiens_accelerator"))
    if sapiens_accelerator_version >= version.parse("0.0"): from sapiens_accelerator.utils.modeling import get_state_dict_from_offload
if is_safetensors_available():
    from safetensors import safe_open
    from safetensors.torch import load_file as safe_load_file
    from safetensors.torch import save_file as safe_save_file
logger = logging.get_logger(__name__)
_init_weights = True
def is_fsdp_enabled(): return (torch.distributed.is_available() and torch.distributed.is_initialized() and strtobool(os.environ.get("SAPIENS_ACCELERATOR_USE_FSDP", "False")) == 1 and strtobool(os.environ.get("FSDP_CPU_RAM_EFFICIENT_LOADING", "False")) == 1)
def is_local_dist_rank_0(): return (torch.distributed.is_available() and torch.distributed.is_initialized() and int(os.environ.get("LOCAL_RANK", -1)) == 0)
if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp
    from smdistributed.modelparallel import __version__ as SMP_VERSION
    IS_SAGEMAKER_MP_POST_1_10 = version.parse(SMP_VERSION) >= version.parse("1.10")
else: IS_SAGEMAKER_MP_POST_1_10 = False
if is_peft_available(): from .utils import find_adapter_config_file
TORCH_INIT_FUNCTIONS = {"uniform_": nn.init.uniform_, "normal_": nn.init.normal_, "trunc_normal_": nn.init.trunc_normal_, "constant_": nn.init.constant_, "xavier_uniform_": nn.init.xavier_uniform_, "xavier_normal_": nn.init.xavier_normal_,
"kaiming_uniform_": nn.init.kaiming_uniform_, "kaiming_normal_": nn.init.kaiming_normal_, "uniform": nn.init.uniform, "normal": nn.init.normal, "xavier_uniform": nn.init.xavier_uniform, "xavier_normal": nn.init.xavier_normal, "kaiming_uniform": nn.init.kaiming_uniform, "kaiming_normal": nn.init.kaiming_normal}
@contextmanager
def no_init_weights(_enable=True):
    global _init_weights
    old_init_weights = _init_weights
    if _enable:
        _init_weights = False
        def _skip_init(*args, **kwargs): pass
        for name, init_func in TORCH_INIT_FUNCTIONS.items(): setattr(torch.nn.init, name, _skip_init)
    try: yield
    finally:
        _init_weights = old_init_weights
        if _enable:
            for name, init_func in TORCH_INIT_FUNCTIONS.items(): setattr(torch.nn.init, name, init_func)
def get_parameter_device(parameter: Union[nn.Module, "ModuleUtilsMixin"]):
    try: return next(parameter.parameters()).device
    except StopIteration:
        def find_tensor_attributes(module: nn.Module) -> List[Tuple[str, Tensor]]:
            tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
            return tuples
        gen = parameter._named_members(get_members_fn=find_tensor_attributes)
        first_tuple = next(gen)
        return first_tuple[1].device
def get_first_parameter_dtype(parameter: Union[nn.Module, "ModuleUtilsMixin"]):
    try: return next(parameter.parameters()).dtype
    except StopIteration:
        def find_tensor_attributes(module: nn.Module) -> List[Tuple[str, Tensor]]:
            tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
            return tuples
        gen = parameter._named_members(get_members_fn=find_tensor_attributes)
        first_tuple = next(gen)
        return first_tuple[1].dtype
def get_parameter_dtype(parameter: Union[nn.Module, "ModuleUtilsMixin"]):
    last_dtype = None
    for t in parameter.parameters():
        last_dtype = t.dtype
        if t.is_floating_point():
            if XLA_USE_BF16 in ENV_VARS_TRUE_VALUES and is_torch_xla_available(): return torch.bfloat16
            if XLA_DOWNCAST_BF16 in ENV_VARS_TRUE_VALUES and is_torch_xla_available():
                if t.dtype == torch.float: return torch.bfloat16
                if t.dtype == torch.double: return torch.float32
            return t.dtype
    if last_dtype is not None: return last_dtype
    def find_tensor_attributes(module: nn.Module) -> List[Tuple[str, Tensor]]:
        tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
        return tuples
    gen = parameter._named_members(get_members_fn=find_tensor_attributes)
    last_tuple = None
    for tuple in gen:
        last_tuple = tuple
        if tuple[1].is_floating_point(): return tuple[1].dtype
    if last_tuple is not None: return last_tuple[1].dtype
    for t in parameter.buffers():
        last_dtype = t.dtype
        if t.is_floating_point(): return t.dtype
    return last_dtype
def get_state_dict_float_dtype(state_dict):
    for t in state_dict.values():
        if t.is_floating_point(): return t.dtype
    raise ValueError("couldn't find any floating point dtypes in state_dict")
def get_state_dict_dtype(state_dict):
    for t in state_dict.values():
        if t.is_floating_point(): return t.dtype
    else: return next(state_dict.values()).dtype
def dtype_byte_size(dtype):
    if dtype == torch.bool: return 1 / 8
    bit_search = re.search(r"[^\d](\d+)_?", str(dtype))
    if bit_search is None: raise ValueError(f"`dtype` is not a valid dtype: {dtype}.")
    bit_size = int(bit_search.groups()[0])
    return bit_size // 8
def check_support_param_buffer_assignment(model_to_load, state_dict, start_prefix=""):
    if len([key for key in state_dict if key.startswith(start_prefix)]) == 0: return False
    if is_deepspeed_zero3_enabled(): return False
    if not getattr(model_to_load, "_supports_param_buffer_assignment", True):
        logger.debug(f"{model_to_load.__class__.__name__} does not support param buffer assignment, loading will be slower")
        return False
    first_key = list(model_to_load.state_dict().keys())[0]
    if start_prefix + first_key in state_dict: return state_dict[start_prefix + first_key].dtype == model_to_load.state_dict()[first_key].dtype
    return False
def shard_checkpoint(state_dict: Dict[str, torch.Tensor], max_shard_size: Union[int, str] = "10GB", weights_name: str = WEIGHTS_NAME):
    logger.warning("Note that `shard_checkpoint` is deprecated and will be removed in v4.44. We recommend you using split_torch_state_dict_into_shards from huggingface_hub library")
    max_shard_size = convert_file_size_to_int(max_shard_size)
    sharded_state_dicts = [{}]
    last_block_size = 0
    total_size = 0
    storage_id_to_block = {}
    for key, weight in state_dict.items():
        if isinstance(weight, str): continue
        else: storage_id = id_tensor_storage(weight)
        if storage_id in storage_id_to_block and weight.device != torch.device("meta"):
            block_id = storage_id_to_block[storage_id]
            sharded_state_dicts[block_id][key] = weight
            continue
        weight_size = weight.numel() * dtype_byte_size(weight.dtype)
        if last_block_size + weight_size > max_shard_size and len(sharded_state_dicts[-1]) > 0:
            sharded_state_dicts.append({})
            last_block_size = 0
        sharded_state_dicts[-1][key] = weight
        last_block_size += weight_size
        total_size += weight_size
        storage_id_to_block[storage_id] = len(sharded_state_dicts) - 1
    if len(sharded_state_dicts) == 1: return {weights_name: sharded_state_dicts[0]}, None
    weight_map = {}
    shards = {}
    for idx, shard in enumerate(sharded_state_dicts):
        shard_file = weights_name.replace(".bin", f"-{idx+1:05d}-of-{len(sharded_state_dicts):05d}.bin")
        shard_file = shard_file.replace(".safetensors", f"-{idx + 1:05d}-of-{len(sharded_state_dicts):05d}.safetensors")
        shards[shard_file] = shard
        for key in shard.keys(): weight_map[key] = shard_file
    metadata = {"total_size": total_size}
    index = {"metadata": metadata, "weight_map": weight_map}
    return shards, index
def load_sharded_checkpoint(model, folder, strict=True, prefer_safe=True):
    index_file = os.path.join(folder, WEIGHTS_INDEX_NAME)
    safe_index_file = os.path.join(folder, SAFE_WEIGHTS_INDEX_NAME)
    index_present = os.path.isfile(index_file)
    safe_index_present = os.path.isfile(safe_index_file)
    if not index_present and not (safe_index_present and is_safetensors_available()):
        filenames = ((WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_INDEX_NAME) if is_safetensors_available() else (WEIGHTS_INDEX_NAME,))
        raise ValueError(f"Can't find a checkpoint index ({' or '.join(filenames)}) in {folder}.")
    load_safe = False
    if safe_index_present:
        if prefer_safe:
            if is_safetensors_available(): load_safe = True
            else: logger.warning(f"Cannot load sharded checkpoint at {folder} safely since safetensors is not installed!")
        elif not index_present: load_safe = True
    load_index = safe_index_file if load_safe else index_file
    with open(load_index, "r", encoding="utf-8") as f: index = json.load(f)
    shard_files = list(set(index["weight_map"].values()))
    loaded_keys = index["weight_map"].keys()
    model_keys = model.state_dict().keys()
    missing_keys = [key for key in model_keys if key not in loaded_keys]
    unexpected_keys = [key for key in loaded_keys if key not in model_keys]
    if strict and (len(missing_keys) > 0 or len(unexpected_keys) > 0):
        error_message = f"Error(s) in loading state_dict for {model.__class__.__name__}"
        if len(missing_keys) > 0:
            str_missing_keys = ",".join([f'"{k}"' for k in missing_keys])
            error_message += f"\nMissing key(s): {str_missing_keys}."
        if len(unexpected_keys) > 0:
            str_unexpected_keys = ",".join([f'"{k}"' for k in unexpected_keys])
            error_message += f"\nMissing key(s): {str_unexpected_keys}."
        raise RuntimeError(error_message)
    weights_only_kwarg = {"weights_only": True} if is_torch_greater_or_equal_than_1_13 else {}
    loader = safe_load_file if load_safe else partial(torch.load, map_location="cpu", **weights_only_kwarg)
    for shard_file in shard_files:
        state_dict = loader(os.path.join(folder, shard_file))
        model.load_state_dict(state_dict, strict=False)
        del state_dict
        gc.collect()
    return torch.nn.modules.module._IncompatibleKeys(missing_keys, unexpected_keys)
def load_state_dict(checkpoint_file: Union[str, os.PathLike], is_quantized: bool = False):
    if checkpoint_file.endswith(".safetensors") and is_safetensors_available():
        with safe_open(checkpoint_file, framework="pt") as f: metadata = f.metadata()
        if metadata.get("format") not in ["pt", "tf", "flax", "mlx"]: raise OSError(f"The safetensors archive passed at {checkpoint_file} does not contain the valid metadata. Make sure you save your model with the `save_pretrained` method.")
        return safe_load_file(checkpoint_file)
    try:
        if ((is_deepspeed_zero3_enabled() and torch.distributed.is_initialized() and torch.distributed.get_rank() > 0) or (is_fsdp_enabled() and not is_local_dist_rank_0())) and not is_quantized: map_location = "meta"
        else: map_location = "cpu"
        extra_args = {}
        if (isinstance(checkpoint_file, str) and map_location != "meta" and version.parse(torch.__version__) >= version.parse("2.1.0") and is_zipfile(checkpoint_file)): extra_args = {"mmap": True}
        weights_only_kwarg = {"weights_only": True} if is_torch_greater_or_equal_than_1_13 else {}
        return torch.load(checkpoint_file, map_location=map_location, **weights_only_kwarg, **extra_args)
    except Exception as e:
        try:
            with open(checkpoint_file) as f:
                if f.read(7) == "version": raise OSError("You seem to have cloned a repository without having git-lfs installed. Please install git-lfs and run `git lfs install` followed by `git lfs pull` in the folder you cloned.")
                else: raise ValueError(f"Unable to locate the file {checkpoint_file} which is necessary to load this pretrained model. Make sure you have saved the model properly.") from e
        except (UnicodeDecodeError, ValueError): raise OSError(f"Unable to load weights from pytorch checkpoint file for '{checkpoint_file}' at '{checkpoint_file}'. If you tried to load a PyTorch model from a TF 2.0 checkpoint, please set from_tf=True.")
def set_initialized_submodules(model, state_dict_keys):
    not_initialized_submodules = {}
    for module_name, module in model.named_modules():
        loaded_keys = {k.replace(f"{module_name}.", "") for k in state_dict_keys if k.startswith(f"{module_name}.")}
        if loaded_keys.issuperset(module.state_dict()): module._is_hf_initialized = True
        else: not_initialized_submodules[module_name] = module
    return not_initialized_submodules
def _end_ptr(tensor: torch.Tensor) -> int:
    if tensor.nelement(): stop = tensor.view(-1)[-1].data_ptr() + tensor.element_size()
    else: stop = tensor.data_ptr()
    return stop
def _get_tied_weight_keys(module: nn.Module, prefix=""):
    tied_weight_keys = []
    if getattr(module, "_tied_weights_keys", None) is not None:
        names = [f"{prefix}.{k}" if prefix else k for k in module._tied_weights_keys]
        tied_weight_keys.extend(names)
    if getattr(module, "_dynamic_tied_weights_keys", None) is not None:
        names = [f"{prefix}.{k}" if prefix else k for k in module._dynamic_tied_weights_keys]
        tied_weight_keys.extend(names)
    for name, submodule in module.named_children():
        local_prefix = f"{prefix}.{name}" if prefix else name
        tied_weight_keys.extend(_get_tied_weight_keys(submodule, prefix=local_prefix))
    return tied_weight_keys
def _find_disjoint(tensors: List[Set[str]], state_dict: Dict[str, torch.Tensor]) -> Tuple[List[Set[str]], List[str]]:
    filtered_tensors = []
    for shared in tensors:
        if len(shared) < 2:
            filtered_tensors.append(shared)
            continue
        areas = []
        for name in shared:
            tensor = state_dict[name]
            areas.append((tensor.data_ptr(), _end_ptr(tensor), name))
        areas.sort()
        _, last_stop, last_name = areas[0]
        filtered_tensors.append({last_name})
        for start, stop, name in areas[1:]:
            if start >= last_stop: filtered_tensors.append({name})
            else: filtered_tensors[-1].add(name)
            last_stop = stop
    disjoint_tensors = []
    shared_tensors = []
    for tensors in filtered_tensors:
        if len(tensors) == 1: disjoint_tensors.append(tensors.pop())
        else: shared_tensors.append(tensors)
    return shared_tensors, disjoint_tensors
def _find_identical(tensors: List[Set[str]], state_dict: Dict[str, torch.Tensor]) -> Tuple[List[Set[str]], Set[str]]:
    shared_tensors = []
    identical = []
    for shared in tensors:
        if len(shared) < 2: continue
        areas = collections.defaultdict(set)
        for name in shared:
            tensor = state_dict[name]
            area = (tensor.device, tensor.data_ptr(), _end_ptr(tensor))
            areas[area].add(name)
        if len(areas) == 1: identical.append(shared)
        else: shared_tensors.append(shared)
    return shared_tensors, identical
def _load_state_dict_into_model(model_to_load, state_dict, start_prefix, assign_to_params_buffers=False):
    old_keys = []
    new_keys = []
    renamed_keys = {}
    renamed_gamma = {}
    renamed_beta = {}
    warning_msg = f"A pretrained model of type `{model_to_load.__class__.__name__}` "
    for key in state_dict.keys():
        new_key = None
        if "gamma" in key:
            new_key = key.replace("gamma", "weight")
            renamed_gamma[key] = new_key if not renamed_gamma else renamed_gamma
        if "beta" in key:
            new_key = key.replace("beta", "bias")
            renamed_beta[key] = new_key if not renamed_beta else renamed_beta
        if new_key:
            old_keys.append(key)
            new_keys.append(new_key)
    renamed_keys = {**renamed_gamma, **renamed_beta}
    if renamed_keys:
        warning_msg += "contains parameters that have been renamed internally (a few are listed below but more are present in the model):\n"
        for old_key, new_key in renamed_keys.items(): warning_msg += f"* `{old_key}` -> `{new_key}`\n"
        warning_msg += "If you are using a model from the Hub, consider submitting a PR to adjust these weights and help future users."
        logger.info_once(warning_msg)
    for old_key, new_key in zip(old_keys, new_keys): state_dict[new_key] = state_dict.pop(old_key)
    metadata = getattr(state_dict, "_metadata", None)
    state_dict = state_dict.copy()
    if metadata is not None: state_dict._metadata = metadata
    error_msgs = []
    def load(module: nn.Module, state_dict, prefix="", assign_to_params_buffers=False):
        local_metadata = {} if metadata is None else metadata.get(prefix[:-1], {})
        local_metadata["assign_to_params_buffers"] = assign_to_params_buffers
        args = (state_dict, prefix, local_metadata, True, [], [], error_msgs)
        if len([key for key in state_dict if key.startswith(prefix)]) > 0:
            if is_deepspeed_zero3_enabled():
                import deepspeed
                named_parameters = dict(module.named_parameters(prefix=prefix[:-1], recurse=False))
                params_to_gather = [named_parameters[k] for k in state_dict.keys() if k in named_parameters]
                if len(params_to_gather) > 0:
                    with deepspeed.zero.GatheredParameters(params_to_gather, modifier_rank=0):
                        if torch.distributed.get_rank() == 0: module._load_from_state_dict(*args)
            else: module._load_from_state_dict(*args)
        for name, child in module._modules.items():
            if child is not None: load(child, state_dict, prefix + name + ".", assign_to_params_buffers)
    load(model_to_load, state_dict, prefix=start_prefix, assign_to_params_buffers=assign_to_params_buffers)
    del state_dict
    return error_msgs
def find_submodule_and_param_name(model, long_key, start_prefix):
    if len(start_prefix) > 0 and long_key.startswith(start_prefix): long_key = ".".join(long_key.split(".")[1:])
    split_key = long_key.split(".")
    submodule = model
    while len(split_key) > 1:
        if hasattr(submodule, split_key[0]):
            submodule = getattr(submodule, split_key[0])
            del split_key[0]
        else:
            submodule = None
            break
    if submodule == model: submodule = None
    return submodule, split_key[0]
def _move_model_to_meta(model, loaded_state_dict_keys, start_prefix):
    for k in loaded_state_dict_keys:
        submodule, param_name = find_submodule_and_param_name(model, k, start_prefix)
        if submodule is not None:
            new_val = getattr(submodule, param_name)
            if isinstance(new_val, torch.nn.Parameter): new_val = torch.nn.Parameter(new_val.to("meta"))
            else: new_val = new_val.to("meta")
            setattr(submodule, param_name, new_val)
def _load_state_dict_into_meta_model(model, state_dict, start_prefix, expected_keys, device_map=None, offload_folder=None, offload_index=None,
state_dict_folder=None, state_dict_index=None, dtype=None, hf_quantizer=None, is_safetensors=False, keep_in_fp32_modules=None, unexpected_keys=None, pretrained_model_name_or_path=None):
    error_msgs = []
    old_keys = []
    new_keys = []
    renamed_gamma = {}
    renamed_beta = {}
    is_quantized = hf_quantizer is not None
    warning_msg = f"This model {type(model)}"
    for key in state_dict.keys():
        new_key = None
        if "gamma" in key:
            new_key = key.replace("gamma", "weight")
            renamed_gamma[key] = new_key if not renamed_gamma else renamed_gamma
        if "beta" in key:
            new_key = key.replace("beta", "bias")
            renamed_beta[key] = new_key if not renamed_beta else renamed_beta
        if hasattr(nn.utils.parametrizations, "weight_norm"):
            if "weight_g" in key: new_key = key.replace("weight_g", "parametrizations.weight.original0")
            if "weight_v" in key: new_key = key.replace("weight_v", "parametrizations.weight.original1")
        else:
            if "parametrizations.weight.original0" in key: new_key = key.replace("parametrizations.weight.original0", "weight_g")
            if "parametrizations.weight.original1" in key: new_key = key.replace("parametrizations.weight.original1", "weight_v")
        if new_key:
            old_keys.append(key)
            new_keys.append(new_key)
    renamed_keys = {**renamed_gamma, **renamed_beta}
    if renamed_keys:
        warning_msg += "contains parameters that have been renamed internally (a few are listed below but more are present in the model):\n"
        for old_key, new_key in renamed_keys.items(): warning_msg += f"* `{old_key}` -> `{new_key}`\n"
        warning_msg += "If you are using a model from the Hub, consider submitting a PR to adjust these weights and help future users."
        logger.info_once(warning_msg)
    for old_key, new_key in zip(old_keys, new_keys): state_dict[new_key] = state_dict.pop(old_key)
    is_torch_e4m3fn_available = hasattr(torch, "float8_e4m3fn")
    for param_name, param in state_dict.items():
        if param_name not in expected_keys: continue
        if param_name.startswith(start_prefix): param_name = param_name[len(start_prefix) :]
        module_name = param_name
        set_module_kwargs = {}
        is_param_float8_e4m3fn = is_torch_e4m3fn_available and param.dtype == torch.float8_e4m3fn
        if dtype is not None and torch.is_floating_point(param) and not is_param_float8_e4m3fn:
            if (keep_in_fp32_modules is not None and any(module_to_keep_in_fp32 in param_name.split(".") for module_to_keep_in_fp32 in keep_in_fp32_modules) and dtype == torch.float16):
                param = param.to(torch.float32)
                if "dtype" in list(inspect.signature(set_module_tensor_to_device).parameters): set_module_kwargs["dtype"] = torch.float32
            else: param = param.to(dtype)
        old_param = model
        splits = param_name.split(".")
        for split in splits:
            old_param = getattr(old_param, split)
            if old_param is None: break
        if old_param is not None:
            if dtype is None: param = param.to(old_param.dtype)
            if old_param.is_contiguous(): param = param.contiguous()
        set_module_kwargs["value"] = param
        if device_map is None: param_device = "cpu"
        else:
            while len(module_name) > 0 and module_name not in device_map: module_name = ".".join(module_name.split(".")[:-1])
            if module_name == "" and "" not in device_map: raise ValueError(f"{param_name} doesn't have any device set.")
            param_device = device_map[module_name]
        if param_device == "disk":
            if not is_safetensors: offload_index = offload_weight(param, param_name, offload_folder, offload_index)
        elif param_device == "cpu" and state_dict_index is not None: state_dict_index = offload_weight(param, param_name, state_dict_folder, state_dict_index)
        elif (not is_quantized or (not hf_quantizer.requires_parameters_quantization) or (not hf_quantizer.check_quantized_param(model, param, param_name, state_dict, param_device=param_device, device_map=device_map))):
            if is_fsdp_enabled(): param_device = "cpu" if is_local_dist_rank_0() else "meta"
            set_module_tensor_to_device(model, param_name, param_device, **set_module_kwargs)
        else:
            hf_quantizer.create_quantized_param(model, param, param_name, param_device, state_dict, unexpected_keys)
            if is_fsdp_enabled() or is_deepspeed_zero3_enabled():
                module, tensor_name = get_module_from_name(model, param_name)
                value = getattr(module, tensor_name)
                param_to = "cpu"
                if is_fsdp_enabled() and not is_local_dist_rank_0(): param_to = "meta"
                value = type(value)(value.data.to(param_to), **value.__dict__)
                setattr(module, tensor_name, value)
    return error_msgs, offload_index, state_dict_index
def _add_variant(weights_name: str, variant: Optional[str] = None) -> str:
    if variant is not None:
        splits = weights_name.split(".")
        splits = splits[:-1] + [variant] + splits[-1:]
        weights_name = ".".join(splits)
    return weights_name
class ModuleUtilsMixin:
    @staticmethod
    def _hook_rss_memory_pre_forward(module, *args, **kwargs):
        try: import psutil
        except ImportError: raise ImportError("You need to install psutil (pip install psutil) to use memory tracing.")
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        module.mem_rss_pre_forward = mem.rss
        return None
    @staticmethod
    def _hook_rss_memory_post_forward(module, *args, **kwargs):
        try: import psutil
        except ImportError: raise ImportError("You need to install psutil (pip install psutil) to use memory tracing.")
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        module.mem_rss_post_forward = mem.rss
        mem_rss_diff = module.mem_rss_post_forward - module.mem_rss_pre_forward
        module.mem_rss_diff = mem_rss_diff + (module.mem_rss_diff if hasattr(module, "mem_rss_diff") else 0)
        return None
    def add_memory_hooks(self):
        for module in self.modules():
            module.register_forward_pre_hook(self._hook_rss_memory_pre_forward)
            module.register_forward_hook(self._hook_rss_memory_post_forward)
        self.reset_memory_hooks_state()
    def reset_memory_hooks_state(self):
        for module in self.modules():
            module.mem_rss_diff = 0
            module.mem_rss_post_forward = 0
            module.mem_rss_pre_forward = 0
    @property
    def device(self) -> torch.device: return get_parameter_device(self)
    @property
    def dtype(self) -> torch.dtype: return get_parameter_dtype(self)
    def invert_attention_mask(self, encoder_attention_mask: Tensor) -> Tensor:
        if encoder_attention_mask.dim() == 3: encoder_extended_attention_mask = encoder_attention_mask[:, None, :, :]
        if encoder_attention_mask.dim() == 2: encoder_extended_attention_mask = encoder_attention_mask[:, None, None, :]
        encoder_extended_attention_mask = encoder_extended_attention_mask.to(dtype=self.dtype)  # fp16 compatibility
        encoder_extended_attention_mask = (1.0 - encoder_extended_attention_mask) * torch.finfo(self.dtype).min
        return encoder_extended_attention_mask
    @staticmethod
    def create_extended_attention_mask_for_decoder(input_shape, attention_mask, device=None):
        if device is not None: warnings.warn("The `device` argument is deprecated and will be removed in v1 of Sapiens Transformers.", FutureWarning)
        else: device = attention_mask.device
        batch_size, seq_length = input_shape
        seq_ids = torch.arange(seq_length, device=device)
        causal_mask = seq_ids[None, None, :].repeat(batch_size, seq_length, 1) <= seq_ids[None, :, None]
        causal_mask = causal_mask.to(attention_mask.dtype)
        if causal_mask.shape[1] < attention_mask.shape[1]:
            prefix_seq_len = attention_mask.shape[1] - causal_mask.shape[1]
            causal_mask = torch.cat([torch.ones((batch_size, seq_length, prefix_seq_len), device=device, dtype=causal_mask.dtype), causal_mask], axis=-1)
        extended_attention_mask = causal_mask[:, None, :, :] * attention_mask[:, None, None, :]
        return extended_attention_mask
    def get_extended_attention_mask(self, attention_mask: Tensor, input_shape: Tuple[int], device: torch.device = None, dtype: torch.float = None) -> Tensor:
        if dtype is None: dtype = self.dtype
        if not (attention_mask.dim() == 2 and self.config.is_decoder):
            if device is not None: warnings.warn("The `device` argument is deprecated and will be removed in v1 of Sapiens Transformers.", FutureWarning)
        if attention_mask.dim() == 3: extended_attention_mask = attention_mask[:, None, :, :]
        elif attention_mask.dim() == 2:
            if self.config.is_decoder: extended_attention_mask = ModuleUtilsMixin.create_extended_attention_mask_for_decoder(input_shape, attention_mask, device)
            else: extended_attention_mask = attention_mask[:, None, None, :]
        else: raise ValueError(f"Wrong shape for input_ids (shape {input_shape}) or attention_mask (shape {attention_mask.shape})")
        extended_attention_mask = extended_attention_mask.to(dtype=dtype)  # fp16 compatibility
        extended_attention_mask = (1.0 - extended_attention_mask) * torch.finfo(dtype).min
        return extended_attention_mask
    def get_head_mask(self, head_mask: Optional[Tensor], num_hidden_layers: int, is_attention_chunked: bool = False) -> Tensor:
        if head_mask is not None:
            head_mask = self._convert_head_mask_to_5d(head_mask, num_hidden_layers)
            if is_attention_chunked is True: head_mask = head_mask.unsqueeze(-1)
        else: head_mask = [None] * num_hidden_layers
        return head_mask
    def _convert_head_mask_to_5d(self, head_mask, num_hidden_layers):
        if head_mask.dim() == 1:
            head_mask = head_mask.unsqueeze(0).unsqueeze(0).unsqueeze(-1).unsqueeze(-1)
            head_mask = head_mask.expand(num_hidden_layers, -1, -1, -1, -1)
        elif head_mask.dim() == 2: head_mask = head_mask.unsqueeze(1).unsqueeze(-1).unsqueeze(-1)
        assert head_mask.dim() == 5, f"head_mask.dim != 5, instead {head_mask.dim()}"
        head_mask = head_mask.to(dtype=self.dtype)
        return head_mask
    def num_parameters(self, only_trainable: bool = False, exclude_embeddings: bool = False) -> int:
        if exclude_embeddings:
            embedding_param_names = [f"{name}.weight" for name, module_type in self.named_modules() if isinstance(module_type, nn.Embedding)]
            total_parameters = [parameter for name, parameter in self.named_parameters() if name not in embedding_param_names]
        else: total_parameters = list(self.parameters())
        total_numel = []
        is_loaded_in_4bit = getattr(self, "is_loaded_in_4bit", False)
        if is_loaded_in_4bit:
            if is_sapiens_machine_available(): import sapiens_machine as sapiens
            else: raise ValueError("sapiens_machine is not installed but it seems that the model has been loaded in 4bit precision, something went wrong make sure to install sapiens_machine with `pip install sapiens_machine`. You also need a GPU. ")
        for param in total_parameters:
            if param.requires_grad or not only_trainable:
                if is_loaded_in_4bit and isinstance(param, sapiens.nn.Params4bit):
                    if hasattr(param, "element_size"): num_bytes = param.element_size()
                    elif hasattr(param, "quant_storage"): num_bytes = param.quant_storage.itemsize
                    else: num_bytes = 1
                    total_numel.append(param.numel() * 2 * num_bytes)
                else: total_numel.append(param.numel())
        return sum(total_numel)
    def estimate_tokens(self, input_dict: Dict[str, Union[torch.Tensor, Any]]) -> int:
        if not hasattr(self, "warnings_issued"): self.warnings_issued = {}
        if self.main_input_name in input_dict: return input_dict[self.main_input_name].numel()
        elif "estimate_tokens" not in self.warnings_issued:
            logger.warning("Could not estimate the number of tokens of the input, floating-point operations will not be computed")
            self.warnings_issued["estimate_tokens"] = True
        return 0
    def floating_point_ops(self, input_dict: Dict[str, Union[torch.Tensor, Any]], exclude_embeddings: bool = True) -> int: return 6 * self.estimate_tokens(input_dict) * self.num_parameters(exclude_embeddings=exclude_embeddings)
class PreTrainedModel(nn.Module, ModuleUtilsMixin, GenerationMixin, PushToHubMixin, PeftAdapterMixin):
    config_class = None
    base_model_prefix = ""
    main_input_name = "input_ids"
    model_tags = None
    _auto_class = None
    _no_split_modules = None
    _skip_keys_device_placement = None
    _keep_in_fp32_modules = None
    _keys_to_ignore_on_load_missing = None
    _keys_to_ignore_on_load_unexpected = None
    _keys_to_ignore_on_save = None
    _tied_weights_keys = None
    is_parallelizable = False
    supports_gradient_checkpointing = False
    _is_stateful = False
    _supports_flash_attn_2 = False
    _supports_sdpa = False
    _supports_cache_class = False
    _supports_static_cache = False
    _supports_quantized_cache = False
    @property
    def dummy_inputs(self) -> Dict[str, torch.Tensor]: return {"input_ids": torch.tensor(DUMMY_INPUTS)}
    @property
    def framework(self) -> str: return "pt"
    def __init__(self, config: PretrainedConfig, *inputs, **kwargs):
        super().__init__()
        if not isinstance(config, PretrainedConfig): raise ValueError(f"Parameter config in `{self.__class__.__name__}(config)` should be an instance of class `PretrainedConfig`. To create a model from a pretrained model use `model = {self.__class__.__name__}.from_pretrained(PRETRAINED_MODEL_NAME)`")
        config = self._autoset_attn_implementation(config, torch_dtype=torch.get_default_dtype(), check_device_map=False)
        self.config = config
        self.name_or_path = config.name_or_path
        self.warnings_issued = {}
        self.generation_config = GenerationConfig.from_model_config(config) if self.can_generate() else None
        self._keep_in_fp32_modules = copy.copy(self.__class__._keep_in_fp32_modules)
    def post_init(self):
        self.init_weights()
        self._backward_compatibility_gradient_checkpointing()
    def dequantize(self):
        hf_quantizer = getattr(self, "hf_quantizer", None)
        if hf_quantizer is None: raise ValueError("You need to first quantize your model in order to dequantize it")
        return hf_quantizer.dequantize(self)
    def _backward_compatibility_gradient_checkpointing(self):
        if self.supports_gradient_checkpointing and getattr(self.config, "gradient_checkpointing", False):
            self.gradient_checkpointing_enable()
            delattr(self.config, "gradient_checkpointing")
    def add_model_tags(self, tags: Union[List[str], str]) -> None:
        if isinstance(tags, str): tags = [tags]
        if self.model_tags is None: self.model_tags = []
        for tag in tags:
            if tag not in self.model_tags: self.model_tags.append(tag)
    @classmethod
    def _from_config(cls, config, **kwargs):
        torch_dtype = kwargs.pop("torch_dtype", None)
        use_flash_attention_2 = kwargs.pop("use_flash_attention_2", False)
        dtype_orig = None
        if torch_dtype is not None: dtype_orig = cls._set_default_torch_dtype(torch_dtype)
        config = copy.deepcopy(config)
        if config._attn_implementation_internal is not None: attn_implementation = config._attn_implementation_internal
        else: attn_implementation = None
        config._attn_implementation = kwargs.pop("attn_implementation", attn_implementation)
        config = cls._autoset_attn_implementation(config, use_flash_attention_2=use_flash_attention_2, check_device_map=False, torch_dtype=torch_dtype)
        if is_deepspeed_zero3_enabled():
            import deepspeed
            logger.info("Detected DeepSpeed ZeRO-3: activating zero.init() for this model")
            with deepspeed.zero.Init(config_dict_or_path=deepspeed_config()): model = cls(config, **kwargs)
        else: model = cls(config, **kwargs)
        if dtype_orig is not None: torch.set_default_dtype(dtype_orig)
        return model
    @classmethod
    def _autoset_attn_implementation(cls, config, use_flash_attention_2: bool = False, torch_dtype: Optional[torch.dtype] = None, device_map: Optional[Union[str, Dict[str, int]]] = None, check_device_map: bool = True):
        requested_attn_implementation = None
        if hasattr(config, "_attn_implementation_internal") and config._attn_implementation_internal is not None:
            if config._attn_implementation != "flash_attention_2" and use_flash_attention_2: raise ValueError(f'Both attn_implementation="{config._attn_implementation}" and `use_flash_attention_2=True` were used when loading the model, which are not compatible. We recommend to just use `attn_implementation="flash_attention_2"` when loading the model.')
            if not isinstance(config._attn_implementation, dict) and config._attn_implementation not in ["eager"] + list(ALL_ATTENTION_FUNCTIONS.keys()):
                message = f'Specified `attn_implementation="{config._attn_implementation}"` is not supported. The only possible arguments are `attn_implementation="eager"` (manual attention implementation)'
                if cls._supports_flash_attn_2: message += ', `"attn_implementation=flash_attention_2"` (implementation using flash attention 2)'
                if cls._supports_sdpa: message += ', `"attn_implementation=sdpa"` (implementation using torch.nn.functional.scaled_dot_product_attention)'
                if cls._supports_flex_attn: message += (', `"attn_implementation=flex_attention"` (implementation using torch\'s flex_attention)')
                raise ValueError(message + ".")
            requested_attn_implementation = config._attn_implementation_internal
        if use_flash_attention_2:
            logger.warning_once('The model was loaded with use_flash_attention_2=True, which is deprecated and may be removed in a future release. Please use `attn_implementation="flash_attention_2"` instead.')
            config._attn_implementation = "flash_attention_2"
        if config._attn_implementation == "flash_attention_2": cls._check_and_enable_flash_attn_2(config, torch_dtype=torch_dtype, device_map=device_map, hard_check_only=False, check_device_map=check_device_map)
        elif requested_attn_implementation in [None, "sdpa"] and not is_torch_xla_available():
            config = cls._check_and_enable_sdpa(config, hard_check_only=False if requested_attn_implementation is None else True)
            if (torch.version.hip is not None and config._attn_implementation == "sdpa" and torch.cuda.device_count() > 1):
                logger.warning_once("Using the `SDPA` attention implementation on multi-gpu setup with ROCM may lead to performance issues due to the FA backend. Disabling it to use alternative backends.")
                torch.backends.cuda.enable_flash_sdp(False)
        elif requested_attn_implementation in list(ALL_ATTENTION_FUNCTIONS.keys()): config._attn_implementation = requested_attn_implementation
        elif isinstance(requested_attn_implementation, dict): config._attn_implementation = None
        else: config._attn_implementation = "eager"
        config._attn_implementation_autoset = True
        return config
    @classmethod
    def _set_default_torch_dtype(cls, dtype: torch.dtype) -> torch.dtype:
        if not dtype.is_floating_point: raise ValueError(f"Can't instantiate {cls.__name__} model under dtype={dtype} since it is not a floating point dtype")
        logger.info(f"Instantiating {cls.__name__} model under default dtype {dtype}.")
        dtype_orig = torch.get_default_dtype()
        torch.set_default_dtype(dtype)
        return dtype_orig
    @property
    def base_model(self) -> nn.Module: return getattr(self, self.base_model_prefix, self)
    @classmethod
    def can_generate(cls) -> bool:
        if "GenerationMixin" in str(cls.__bases__): return True
        if str(cls.__name__) in str(cls.generate): return True
        for base in cls.__bases__:
            if not hasattr(base, "can_generate"): continue
            if "PreTrainedModel" not in str(base) and base.can_generate(): return True
        if "GenerationMixin" not in str(cls.prepare_inputs_for_generation): return True
        return False
    @classmethod
    def _check_and_enable_flash_attn_2(cls, config, torch_dtype: Optional[torch.dtype] = None, device_map: Optional[Union[str, Dict[str, int]]] = None, check_device_map: bool = True, hard_check_only: bool = False) -> PretrainedConfig:
        if not cls._supports_flash_attn_2: raise ValueError(f"{cls.__name__} does not support Flash Attention 2.0 yet.")
        if not is_flash_attn_2_available():
            preface = "FlashAttention2 has been toggled on, but it cannot be used due to the following error:"
            install_message = "Please refer to the documentation to install Flash Attention 2."
            if importlib.util.find_spec("flash_attn") is None: raise ImportError(f"{preface} the package flash_attn seems to be not installed. {install_message}")
            flash_attention_version = version.parse(importlib.metadata.version("flash_attn"))
            if torch.version.cuda:
                if flash_attention_version < version.parse("2.1.0"): raise ImportError(f"{preface} you need flash_attn package version to be greater or equal than 2.1.0. Detected version {flash_attention_version}. {install_message}")
                elif not torch.cuda.is_available(): raise ValueError(f"{preface} Flash Attention 2 is not available on CPU. Please make sure torch can access a CUDA device.")
                else: raise ImportError(f"{preface} Flash Attention 2 is not available. {install_message}")
            elif torch.version.hip:
                if flash_attention_version < version.parse("2.0.4"): raise ImportError(f"{preface} you need flash_attn package version to be greater or equal than 2.0.4. Make sure to have that version installed - detected version {flash_attention_version}. {install_message}")
                else: raise ImportError(f"{preface} Flash Attention 2 is not available. {install_message}")
        _is_bettertransformer = getattr(cls, "use_bettertransformer", False)
        if _is_bettertransformer: raise ValueError("Flash Attention 2 and BetterTransformer API are not compatible. Please make sure to disable BetterTransformers by doing model.reverse_bettertransformer()")
        if torch_dtype is None: logger.warning_once("You are attempting to use Flash Attention 2.0 without specifying a torch dtype. This might lead to unexpected behaviour")
        elif torch_dtype is not None and torch_dtype not in [torch.float16, torch.bfloat16]: logger.warning_once(f"Flash Attention 2.0 only supports torch.float16 and torch.bfloat16 dtypes, but the current dype in {cls.__name__} is {torch_dtype}. You should run training or inference using Automatic Mixed-Precision via the `with torch.autocast(device_type='torch_device'):` decorator,"+' or load the model with the `torch_dtype` argument. Example: `model = AutoModel.from_pretrained("openai/whisper-tiny", attn_implementation="flash_attention_2", torch_dtype=torch.float16)`')
        if check_device_map and device_map is None and torch.empty(0).device.type != "cuda":
            if torch.cuda.is_available(): logger.warning_once("You are attempting to use Flash Attention 2.0 with a model not initialized on GPU. Make sure to move the model to GPU after initializing it on CPU with `model.to('cuda')`.")
            else: raise ValueError("You are attempting to use Flash Attention 2.0 with a model not initialized on GPU and with no GPU available. This is not supported yet. Please make sure to have access to a GPU and either initialise the model on a GPU by passing a device_map or initialising the model on CPU and then moving it to GPU.")
        elif (check_device_map and device_map is not None and isinstance(device_map, dict) and ("cpu" in device_map.values() or "disk" in device_map.values())): raise ValueError("You are attempting to use Flash Attention 2.0 with a model dispatched on CPU or disk. This is not supported. Please make sure to initialise the model on a GPU by passing a device_map that contains only GPU devices as keys.")
        if not hard_check_only: config._attn_implementation = "flash_attention_2"
        return config
    @classmethod
    def _check_and_enable_sdpa(cls, config, hard_check_only: bool = False) -> PretrainedConfig:
        if hard_check_only:
            if not cls._supports_sdpa: raise ValueError(f"{cls.__name__} does not support an attention implementation through torch.nn.functional.scaled_dot_product_attention yet. If you believe"+' this error is a bug, please open an issue in Transformers GitHub repository and load your model with the argument `attn_implementation="eager"` meanwhile. Example: `model = AutoModel.from_pretrained("openai/whisper-tiny", attn_implementation="eager")`')
            if not is_torch_sdpa_available(): raise ImportError("PyTorch SDPA requirements in Transformers are not met. Please install torch>=2.1.1.")
        if not is_torch_sdpa_available() or not cls._supports_sdpa: return config
        _is_bettertransformer = getattr(cls, "use_bettertransformer", False)
        if _is_bettertransformer: return config
        if not hard_check_only: config._attn_implementation = "sdpa"
        return config
    def enable_input_require_grads(self):
        def make_inputs_require_grads(module, input, output): output.requires_grad_(True)
        self._require_grads_hook = self.get_input_embeddings().register_forward_hook(make_inputs_require_grads)
    def disable_input_require_grads(self): self._require_grads_hook.remove()
    def get_input_embeddings(self) -> nn.Module:
        base_model = getattr(self, self.base_model_prefix, self)
        if base_model is not self: return base_model.get_input_embeddings()
        else: raise NotImplementedError
    def set_input_embeddings(self, value: nn.Module):
        base_model = getattr(self, self.base_model_prefix, self)
        if base_model is not self: base_model.set_input_embeddings(value)
        else: raise NotImplementedError
    def get_output_embeddings(self) -> nn.Module: return None
    def _init_weights(self, module): pass
    def _initialize_weights(self, module):
        if getattr(module, "_is_hf_initialized", False): return
        self._init_weights(module)
        module._is_hf_initialized = True
    def tie_weights(self):
        if getattr(self.config, "tie_word_embeddings", True):
            output_embeddings = self.get_output_embeddings()
            if output_embeddings is not None: self._tie_or_clone_weights(output_embeddings, self.get_input_embeddings())
        if getattr(self.config, "is_encoder_decoder", False) and getattr(self.config, "tie_encoder_decoder", False):
            if hasattr(self, self.base_model_prefix): self = getattr(self, self.base_model_prefix)
            tied_weights = self._tie_encoder_decoder_weights(self.encoder, self.decoder, self.base_model_prefix, "encoder")
            self._dynamic_tied_weights_keys = tied_weights
        for module in self.modules():
            if hasattr(module, "_tie_weights"): module._tie_weights()
    @staticmethod
    def _tie_encoder_decoder_weights(encoder: nn.Module, decoder: nn.Module, base_model_prefix: str, base_encoder_name: str):
        uninitialized_encoder_weights: List[str] = []
        tied_weights: List[str] = []
        if decoder.__class__ != encoder.__class__: logger.info(f"{decoder.__class__} and {encoder.__class__} are not equal. In this case make sure that all encoder weights are correctly initialized.")
        def tie_encoder_to_decoder_recursively(decoder_pointer: nn.Module, encoder_pointer: nn.Module, module_name: str, base_encoder_name: str, uninitialized_encoder_weights: List[str], depth=0, total_decoder_name="", total_encoder_name=""):
            assert isinstance(decoder_pointer, nn.Module) and isinstance(encoder_pointer, nn.Module), f"{decoder_pointer} and {encoder_pointer} have to be of type nn.Module"
            if hasattr(decoder_pointer, "weight"):
                assert hasattr(encoder_pointer, "weight")
                encoder_pointer.weight = decoder_pointer.weight
                tied_weights.append(f"{base_encoder_name}{total_encoder_name}.weight")
                if hasattr(decoder_pointer, "bias"):
                    assert hasattr(encoder_pointer, "bias")
                    tied_weights.append(f"{base_encoder_name}{total_encoder_name}.bias")
                    encoder_pointer.bias = decoder_pointer.bias
                return
            encoder_modules = encoder_pointer._modules
            decoder_modules = decoder_pointer._modules
            if len(decoder_modules) > 0:
                assert (len(encoder_modules) > 0), f"Encoder module {encoder_pointer} does not match decoder module {decoder_pointer}"
                all_encoder_weights = {module_name + "/" + sub_name for sub_name in encoder_modules.keys()}
                encoder_layer_pos = 0
                for name, module in decoder_modules.items():
                    if name.isdigit():
                        encoder_name = str(int(name) + encoder_layer_pos)
                        decoder_name = name
                        if not isinstance(decoder_modules[decoder_name], type(encoder_modules[encoder_name])) and len(encoder_modules) != len(decoder_modules):
                            encoder_layer_pos -= 1
                            continue
                    elif name not in encoder_modules: continue
                    elif depth > 500: raise ValueError("Max depth of recursive function `tie_encoder_to_decoder` reached. It seems that there is a circular dependency between two or more `nn.Modules` of your model.")
                    else: decoder_name = encoder_name = name
                    tie_encoder_to_decoder_recursively(decoder_modules[decoder_name], encoder_modules[encoder_name], module_name + "/" + name, base_encoder_name, uninitialized_encoder_weights, depth=depth + 1, total_encoder_name=f"{total_encoder_name}.{encoder_name}", total_decoder_name=f"{total_decoder_name}.{decoder_name}")
                    all_encoder_weights.remove(module_name + "/" + encoder_name)
                uninitialized_encoder_weights += list(all_encoder_weights)
        tie_encoder_to_decoder_recursively(decoder, encoder, base_model_prefix, base_encoder_name, uninitialized_encoder_weights)
        if len(uninitialized_encoder_weights) > 0: logger.warning(f"The following encoder weights were not tied to the decoder {uninitialized_encoder_weights}")
        return tied_weights
    def _tie_or_clone_weights(self, output_embeddings, input_embeddings):
        if self.config.torchscript: output_embeddings.weight = nn.Parameter(input_embeddings.weight.clone())
        else: output_embeddings.weight = input_embeddings.weight
        if getattr(output_embeddings, "bias", None) is not None: output_embeddings.bias.data = nn.functional.pad(output_embeddings.bias.data, (0, output_embeddings.weight.shape[0] - output_embeddings.bias.shape[0]), "constant", 0)
        if hasattr(output_embeddings, "out_features") and hasattr(input_embeddings, "num_embeddings"): output_embeddings.out_features = input_embeddings.num_embeddings
    def _get_no_split_modules(self, device_map: str):
        _no_split_modules = set()
        modules_to_check = [self]
        while len(modules_to_check) > 0:
            module = modules_to_check.pop(-1)
            if module.__class__.__name__ not in _no_split_modules:
                if isinstance(module, PreTrainedModel):
                    if module._no_split_modules is None: raise ValueError(f"{module.__class__.__name__} does not support `device_map='{device_map}'`. To implement support, the model class needs to implement the `_no_split_modules` attribute.")
                    else: _no_split_modules = _no_split_modules | set(module._no_split_modules)
                modules_to_check += list(module.children())
        return list(_no_split_modules)
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of: Optional[int] = None) -> nn.Embedding:
        model_embeds = self._resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        if new_num_tokens is None and pad_to_multiple_of is None: return model_embeds
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(model_embeds.weight, modifier_rank=None): vocab_size = model_embeds.weight.shape[0]
        else: vocab_size = model_embeds.weight.shape[0]
        self.config.get_text_config().vocab_size = vocab_size
        self.vocab_size = vocab_size
        self.tie_weights()
        return model_embeds
    def _resize_token_embeddings(self, new_num_tokens, pad_to_multiple_of=None):
        old_embeddings = self.get_input_embeddings()
        new_embeddings = self._get_resized_embeddings(old_embeddings, new_num_tokens, pad_to_multiple_of)
        if hasattr(old_embeddings, "_hf_hook"):
            hook = old_embeddings._hf_hook
            add_hook_to_module(new_embeddings, hook)
        old_embeddings_requires_grad = old_embeddings.weight.requires_grad
        new_embeddings.requires_grad_(old_embeddings_requires_grad)
        self.set_input_embeddings(new_embeddings)
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if pad_to_multiple_of is not None:
            if is_deepspeed_zero3_enabled() and not is_quantized:
                import deepspeed
                with deepspeed.zero.GatheredParameters(new_embeddings.weight, modifier_rank=None): new_num_tokens = new_embeddings.weight.shape[0]
            else: new_num_tokens = new_embeddings.weight.shape[0]
        if self.get_output_embeddings() is not None and not self.config.tie_word_embeddings:
            old_lm_head = self.get_output_embeddings()
            if isinstance(old_lm_head, torch.nn.Embedding): new_lm_head = self._get_resized_embeddings(old_lm_head, new_num_tokens)
            else: new_lm_head = self._get_resized_lm_head(old_lm_head, new_num_tokens)
            if hasattr(old_lm_head, "_hf_hook"):
                hook = old_lm_head._hf_hook
                add_hook_to_module(new_lm_head, hook)
            old_lm_head_requires_grad = old_lm_head.weight.requires_grad
            new_lm_head.requires_grad_(old_lm_head_requires_grad)
            self.set_output_embeddings(new_lm_head)
        return self.get_input_embeddings()
    def _get_resized_embeddings(self, old_embeddings: nn.Embedding, new_num_tokens: Optional[int] = None, pad_to_multiple_of: Optional[int] = None) -> nn.Embedding:
        if pad_to_multiple_of is not None:
            if not isinstance(pad_to_multiple_of, int): raise ValueError(f"Asking to pad the embedding matrix to a multiple of `{pad_to_multiple_of}`, which is not and integer. Please make sure to pass an integer")
            if new_num_tokens is None: new_num_tokens = old_embeddings.weight.shape[0]
            new_num_tokens = ((new_num_tokens + pad_to_multiple_of - 1) // pad_to_multiple_of) * pad_to_multiple_of
        else: logger.info(f"You are resizing the embedding layer without providing a `pad_to_multiple_of` parameter. This means that the new embedding dimension will be {new_num_tokens}. This might induce some performance reduction as *Tensor Cores* will not be available. For more details about this, or help on choosing the correct value for resizing, refer to this guide: https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html#requirements-tc")
        if new_num_tokens is None: return old_embeddings
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(old_embeddings.weight, modifier_rank=None): old_num_tokens, old_embedding_dim = old_embeddings.weight.size()
        else: old_num_tokens, old_embedding_dim = old_embeddings.weight.size()
        if old_num_tokens == new_num_tokens and not is_deepspeed_zero3_enabled(): return old_embeddings
        if not isinstance(old_embeddings, nn.Embedding): raise TypeError(f"Old embeddings are of type {type(old_embeddings)}, which is not an instance of {nn.Embedding}. You should either use a different resize function or make sure that `old_embeddings` are an instance of {nn.Embedding}.")
        new_embeddings = nn.Embedding(new_num_tokens, old_embedding_dim, device=old_embeddings.weight.device, dtype=old_embeddings.weight.dtype)
        self._init_weights(new_embeddings)
        n = min(old_num_tokens, new_num_tokens)
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_embeddings.weight, new_embeddings.weight]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0): new_embeddings.weight.data[:n, :] = old_embeddings.weight.data[:n, :]
        else: new_embeddings.weight.data[:n, :] = old_embeddings.weight.data[:n, :]
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_embeddings.weight, new_embeddings.weight]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0):
                old_embeddings.weight = new_embeddings.weight
                old_embeddings.num_embeddings = new_embeddings.weight.data.shape[0]
                if old_embeddings.padding_idx is not None and (new_num_tokens - 1) < old_embeddings.padding_idx: old_embeddings.padding_idx = None
        else:
            old_embeddings.weight.data = new_embeddings.weight.data
            old_embeddings.num_embeddings = new_embeddings.weight.data.shape[0]
            if old_embeddings.padding_idx is not None and (new_num_tokens - 1) < old_embeddings.padding_idx: old_embeddings.padding_idx = None
        return old_embeddings
    def _get_resized_lm_head(self, old_lm_head: nn.Linear, new_num_tokens: Optional[int] = None, transposed: Optional[bool] = False) -> nn.Linear:
        if new_num_tokens is None: return old_lm_head
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(old_lm_head.weight, modifier_rank=None): old_num_tokens, old_lm_head_dim = (old_lm_head.weight.size() if not transposed else old_lm_head.weight.t().size())
        else: old_num_tokens, old_lm_head_dim = (old_lm_head.weight.size() if not transposed else old_lm_head.weight.t().size())
        if old_num_tokens == new_num_tokens and not is_deepspeed_zero3_enabled(): return old_lm_head
        if not isinstance(old_lm_head, nn.Linear): raise TypeError(f"Old language model head is of type {type(old_lm_head)}, which is not an instance of {nn.Linear}. You should either use a different resize function or make sure that `old_lm_head` are an instance of {nn.Linear}.")
        new_lm_head_shape = (old_lm_head_dim, new_num_tokens) if not transposed else (new_num_tokens, old_lm_head_dim)
        has_new_lm_head_bias = old_lm_head.bias is not None
        new_lm_head = nn.Linear(*new_lm_head_shape, bias=has_new_lm_head_bias, device=old_lm_head.weight.device, dtype=old_lm_head.weight.dtype)
        self._init_weights(new_lm_head)
        num_tokens_to_copy = min(old_num_tokens, new_num_tokens)
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_lm_head.weight, old_lm_head.bias, new_lm_head.weight, new_lm_head.bias]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0): self._copy_lm_head_original_to_resized(new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias)
        else: self._copy_lm_head_original_to_resized(new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias)
        return new_lm_head
    def _copy_lm_head_original_to_resized(self, new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias):
        if not transposed: new_lm_head.weight.data[:num_tokens_to_copy, :] = old_lm_head.weight.data[:num_tokens_to_copy, :]
        else: new_lm_head.weight.data[:, :num_tokens_to_copy] = old_lm_head.weight.data[:, :num_tokens_to_copy]
        if has_new_lm_head_bias: new_lm_head.bias.data[:num_tokens_to_copy] = old_lm_head.bias.data[:num_tokens_to_copy]
    def resize_position_embeddings(self, new_num_position_embeddings: int): raise NotImplementedError(f"`resize_position_embeddings` is not implemented for {self.__class__}`. To implement it, you should overwrite this method in the class {self.__class__} in `modeling_{self.__class__.__module__}.py`")
    def get_position_embeddings(self) -> Union[nn.Embedding, Tuple[nn.Embedding]]: raise NotImplementedError(f"`get_position_embeddings` is not implemented for {self.__class__}`. To implement it, you should overwrite this method in the class {self.__class__} in `modeling_{self.__class__.__module__}.py`")
    def init_weights(self):
        if self.config.pruned_heads: self.prune_heads(self.config.pruned_heads)
        if _init_weights:
            self.apply(self._initialize_weights)
            self.tie_weights()
    def prune_heads(self, heads_to_prune: Dict[int, List[int]]):
        for layer, heads in heads_to_prune.items():
            union_heads = set(self.config.pruned_heads.get(layer, [])) | set(heads)
            self.config.pruned_heads[layer] = list(union_heads)
        self.base_model._prune_heads(heads_to_prune)
    def gradient_checkpointing_enable(self, gradient_checkpointing_kwargs=None):
        if not self.supports_gradient_checkpointing: raise ValueError(f"{self.__class__.__name__} does not support gradient checkpointing.")
        if gradient_checkpointing_kwargs is None: gradient_checkpointing_kwargs = {"use_reentrant": True}
        gradient_checkpointing_func = functools.partial(checkpoint, **gradient_checkpointing_kwargs)
        _is_using_old_format = "value" in inspect.signature(self._set_gradient_checkpointing).parameters
        if not _is_using_old_format: self._set_gradient_checkpointing(enable=True, gradient_checkpointing_func=gradient_checkpointing_func)
        else:
            self.apply(partial(self._set_gradient_checkpointing, value=True))
            logger.warning("You are using an old version of the checkpointing format that is deprecated (We will also silently ignore `gradient_checkpointing_kwargs` in case you passed it). Please update to the new format on your modeling file. To use the new format, you need to completely remove the definition of the method `_set_gradient_checkpointing` in your model.")
        if getattr(self, "_hf_peft_config_loaded", False): self.enable_input_require_grads()
    def _set_gradient_checkpointing(self, enable: bool = True, gradient_checkpointing_func: Callable = checkpoint):
        is_gradient_checkpointing_set = False
        if hasattr(self, "gradient_checkpointing"):
            self._gradient_checkpointing_func = gradient_checkpointing_func
            self.gradient_checkpointing = enable
            is_gradient_checkpointing_set = True
        for module in self.modules():
            if hasattr(module, "gradient_checkpointing"):
                module._gradient_checkpointing_func = gradient_checkpointing_func
                module.gradient_checkpointing = enable
                is_gradient_checkpointing_set = True
        if not is_gradient_checkpointing_set: raise ValueError(f"{self.__class__.__name__} is not compatible with gradient checkpointing. Make sure all the architecture support it by setting a boolean attribute `gradient_checkpointing` to modules of the model that uses checkpointing.")
    def gradient_checkpointing_disable(self):
        if self.supports_gradient_checkpointing:
            _is_using_old_format = "value" in inspect.signature(self._set_gradient_checkpointing).parameters
            if not _is_using_old_format: self._set_gradient_checkpointing(enable=False)
            else:
                logger.warning("You are using an old version of the checkpointing format that is deprecated (We will also silently ignore `gradient_checkpointing_kwargs` in case you passed it). Please update to the new format on your modeling file. To use the new format, you need to completely remove the definition of the method `_set_gradient_checkpointing` in your model.")
                self.apply(partial(self._set_gradient_checkpointing, value=False))
        if getattr(self, "_hf_peft_config_loaded", False): self.disable_input_require_grads()
    @property
    def is_gradient_checkpointing(self) -> bool: return any(hasattr(m, "gradient_checkpointing") and m.gradient_checkpointing for m in self.modules())
    def save_pretrained(self, save_directory: Union[str, os.PathLike], is_main_process: bool = True, state_dict: Optional[dict] = None, save_function: Callable = torch.save, push_to_hub: bool = False,
    max_shard_size: Union[int, str] = "5GB", safe_serialization: bool = True, variant: Optional[str] = None, token: Optional[Union[str, bool]] = None, save_peft_format: bool = True, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        ignore_metadata_errors = kwargs.pop("ignore_metadata_errors", False)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None: kwargs["token"] = token
        _hf_peft_config_loaded = getattr(self, "_hf_peft_config_loaded", False)
        hf_quantizer = getattr(self, "hf_quantizer", None)
        quantization_serializable = (hf_quantizer is not None and isinstance(hf_quantizer, HfQuantizer) and hf_quantizer.is_serializable)
        if hf_quantizer is not None and not _hf_peft_config_loaded and not quantization_serializable: raise ValueError(f"The model is quantized with {hf_quantizer.quantization_config.quant_method} and is not serializable - check out the warnings from the logger on the traceback to understand the reason why the quantized model is not serializable.")
        if "save_config" in kwargs:
            warnings.warn("`save_config` is deprecated and will be removed in v1 of Sapiens Transformers. Use `is_main_process` instead.")
            is_main_process = kwargs.pop("save_config")
        if safe_serialization and not is_safetensors_available(): raise ImportError("`safe_serialization` requires the `safetensors library: `pip install safetensors`.")
        if os.path.isfile(save_directory):
            logger.error(f"Provided path ({save_directory}) should be a directory, not a file")
            return
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        model_to_save = unwrap_model(self)
        dtype = get_parameter_dtype(model_to_save)
        model_to_save.config.torch_dtype = str(dtype).split(".")[1]
        model_to_save.config.architectures = [model_to_save.__class__.__name__]
        if self._auto_class is not None: custom_object_save(self, save_directory, config=self.config)
        if is_main_process:
            if not _hf_peft_config_loaded:
                misplaced_generation_parameters = model_to_save.config._get_non_default_generation_parameters()
                if self.can_generate() and len(misplaced_generation_parameters) > 0:
                    warnings.warn(f"Moving the following attributes in the config to the generation config: {misplaced_generation_parameters}. You are seeing this warning because you've set generation parameters in the model config, as opposed to in the generation config.", UserWarning)
                    for param_name, param_value in misplaced_generation_parameters.items():
                        setattr(model_to_save.generation_config, param_name, param_value)
                        setattr(model_to_save.config, param_name, None)
                model_to_save.config.save_pretrained(save_directory)
            if self.can_generate(): model_to_save.generation_config.save_pretrained(save_directory)
            if _hf_peft_config_loaded:
                logger.info("Detected adapters on the model, saving the model in the PEFT format, only adapter weights will be saved.")
                state_dict = model_to_save.get_adapter_state_dict()
                if save_peft_format:
                    logger.info("To match the expected format of the PEFT library, all keys of the state dict of adapters will be pre-pended with `base_model.model`.")
                    peft_state_dict = {}
                    for key, value in state_dict.items(): peft_state_dict[f"base_model.model.{key}"] = value
                    state_dict = peft_state_dict
                active_adapter = self.active_adapters()
                if len(active_adapter) > 1: raise ValueError("Multiple active adapters detected, saving multiple active adapters is not supported yet. You can save adapters separately one by one by iteratively calling `model.set_adapter(adapter_name)` then `model.save_pretrained(...)`")
                active_adapter = active_adapter[0]
                current_peft_config = self.peft_config[active_adapter]
                current_peft_config.save_pretrained(save_directory)
        module_map = {}
        if state_dict is None:
            if (hasattr(self, "hf_device_map") and len(set(self.hf_device_map.values())) > 1 and ("cpu" in self.hf_device_map.values() or "disk" in self.hf_device_map.values())):
                warnings.warn("Attempting to save a model with offloaded modules. Ensure that unallocated cpu memory exceeds the `shard_size` (5GB default)")
                for name, module in model_to_save.named_modules():
                    if name == "": continue
                    module_state_dict = module.state_dict()
                    for key in module_state_dict: module_map[name + f".{key}"] = module
            state_dict = model_to_save.state_dict()
        if IS_SAGEMAKER_MP_POST_1_10:
            for smp_to_hf, _ in smp.state.module_manager.translate_functions: state_dict = smp_to_hf(state_dict)
        if self._keys_to_ignore_on_save is not None:
            for ignore_key in self._keys_to_ignore_on_save:
                if ignore_key in state_dict.keys(): del state_dict[ignore_key]
        if safe_serialization:
            ptrs = collections.defaultdict(list)
            for name, tensor in state_dict.items():
                if isinstance(tensor, torch.Tensor): ptrs[id_tensor_storage(tensor)].append(name)
                else: ptrs[id(tensor)].append(name)
            if hasattr(self, "hf_device_map"):
                tied_params = find_tied_parameters(self)
                if tied_params:
                    tied_names = tied_params[0]
                    shared_ptrs = {ptr: names for ptr, names in ptrs.items() if any(name in tied_names for name in names)}
                else: shared_ptrs = {}
            else: shared_ptrs = {ptr: names for ptr, names in ptrs.items() if len(names) > 1}
            _tied_weights_keys = _get_tied_weight_keys(self)
            error_names = []
            to_delete_names = set()
            for names in shared_ptrs.values():
                if _tied_weights_keys is not None:
                    found = 0
                    for name in sorted(names):
                        matches_pattern = any(re.search(pat, name) for pat in _tied_weights_keys)
                        if matches_pattern and name in state_dict:
                            found += 1
                            if found < len(names): to_delete_names.add(name)
            shared_names, disjoint_names = _find_disjoint(shared_ptrs.values(), state_dict)
            for name in disjoint_names: state_dict[name] = state_dict[name].clone()
            shared_names, identical_names = _find_identical(shared_names, state_dict)
            for inames in identical_names:
                known = inames.intersection(to_delete_names)
                for name in known: del state_dict[name]
                unknown = inames.difference(to_delete_names)
                if len(unknown) > 1: error_names.append(unknown)
            if shared_names: error_names.append(set(shared_names))
            if len(error_names) > 0: raise RuntimeError(f"The weights trying to be saved contained shared tensors {error_names} that are mismatching the transformers base configuration. Try saving using `safe_serialization=False` or remove this tensor sharing.")
        if not _hf_peft_config_loaded:
            weights_name = SAFE_WEIGHTS_NAME if safe_serialization else WEIGHTS_NAME
            weights_name = _add_variant(weights_name, variant)
        else: weights_name = ADAPTER_SAFE_WEIGHTS_NAME if safe_serialization else ADAPTER_WEIGHTS_NAME
        filename_pattern = weights_name.replace(".bin", "{suffix}.bin").replace(".safetensors", "{suffix}.safetensors")
        state_dict_split = split_torch_state_dict_into_shards(state_dict, filename_pattern=filename_pattern, max_shard_size=max_shard_size)
        index = None
        if state_dict_split.is_sharded: index = {"metadata": state_dict_split.metadata, "weight_map": state_dict_split.tensor_to_filename}
        for filename in os.listdir(save_directory):
            full_filename = os.path.join(save_directory, filename)
            weights_no_suffix = weights_name.replace(".bin", "").replace(".safetensors", "")
            filename_no_suffix = filename.replace(".bin", "").replace(".safetensors", "")
            reg = re.compile(r"(.*?)-\d{5}-of-\d{5}")
            if (filename.startswith(weights_no_suffix) and os.path.isfile(full_filename) and filename not in state_dict_split.filename_to_tensors.keys() and is_main_process and reg.fullmatch(filename_no_suffix) is not None): os.remove(full_filename)
        filename_to_tensors = state_dict_split.filename_to_tensors.items()
        if module_map: filename_to_tensors = logging.tqdm(filename_to_tensors, desc="Saving checkpoint shards")
        for shard_file, tensors in filename_to_tensors:
            shard = {tensor: state_dict[tensor].contiguous() for tensor in tensors}
            if module_map:
                if sapiens_accelerator_version < version.parse("0.31"): raise ImportError(f"You need sapiens_accelerator version to be greater or equal than 0.31 to save models with offloaded parameters. Detected version {sapiens_accelerator_version}. Please upgrade sapiens_accelerator with `pip install -U sapiens_accelerator`")
                shard_state_dict = {name: "" for name in shard}
                for module_name in shard:
                    module = module_map[module_name]
                    shard_state_dict = get_state_dict_from_offload(module, module_name, shard_state_dict)
                shard = shard_state_dict
                del shard_state_dict
                gc.collect()
            if safe_serialization: safe_save_file(shard, os.path.join(save_directory, shard_file), metadata={"format": "pt"})
            else: save_function(shard, os.path.join(save_directory, shard_file))
        if index is None:
            path_to_weights = os.path.join(save_directory, weights_name)
            logger.info(f"Model weights saved in {path_to_weights}")
        else:
            save_index_file = SAFE_WEIGHTS_INDEX_NAME if safe_serialization else WEIGHTS_INDEX_NAME
            save_index_file = os.path.join(save_directory, _add_variant(save_index_file, variant))
            with open(save_index_file, "w", encoding="utf-8") as f:
                content = json.dumps(index, indent=2, sort_keys=True) + "\n"
                f.write(content)
            logger.info(f"The model is bigger than the maximum size per checkpoint ({max_shard_size}) and is going to be split in {len(state_dict_split.filename_to_tensors)} checkpoint shards. You can find where each parameters has been saved in the index located at {save_index_file}.")
        if push_to_hub:
            model_card = create_and_tag_model_card(repo_id, self.model_tags, token=token, ignore_metadata_errors=ignore_metadata_errors)
            model_card.save(os.path.join(save_directory, "README.md"))
            self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=token)
    @wraps(PushToHubMixin.push_to_hub)
    def push_to_hub(self, *args, **kwargs):
        tags = self.model_tags if self.model_tags is not None else []
        tags_kwargs = kwargs.get("tags", [])
        if isinstance(tags_kwargs, str): tags_kwargs = [tags_kwargs]
        for tag in tags_kwargs:
            if tag not in tags: tags.append(tag)
        if tags: kwargs["tags"] = tags
        return super().push_to_hub(*args, **kwargs)
    def get_memory_footprint(self, return_buffers=True):
        mem = sum([param.nelement() * param.element_size() for param in self.parameters()])
        if return_buffers:
            mem_bufs = sum([buf.nelement() * buf.element_size() for buf in self.buffers()])
            mem = mem + mem_bufs
        return mem
    @wraps(torch.nn.Module.cuda)
    def cuda(self, *args, **kwargs):
        if getattr(self, "quantization_method", None) == QuantizationMethod.HQQ: raise ValueError("`.cuda` is not supported for HQQ-quantized models.")
        if getattr(self, "quantization_method", None) == QuantizationMethod.SAPIENS_MACHINE:
            if getattr(self, "is_loaded_in_8bit", False): raise ValueError("Calling `cuda()` is not supported for `8-bit` quantized models. Please use the model as it is, since the model has already been set to the correct devices.")
            elif version.parse(importlib.metadata.version("sapiens_machine")) < version.parse("1.0.0"): raise ValueError(f"Calling `cuda()` is not supported for `4-bit` quantized models with the installed version of sapiens_machine. The current device is `{self.device}`. If you intended to move the model, please install sapiens_machine >= 1.0.0.")
        else: return super().cuda(*args, **kwargs)
    @wraps(torch.nn.Module.to)
    def to(self, *args, **kwargs):
        dtype_present_in_args = "dtype" in kwargs
        if not dtype_present_in_args:
            for arg in args:
                if isinstance(arg, torch.dtype):
                    dtype_present_in_args = True
                    break
        if getattr(self, "quantization_method", None) == QuantizationMethod.HQQ: raise ValueError("`.to` is not supported for HQQ-quantized models.")
        if getattr(self, "quantization_method", None) == QuantizationMethod.SAPIENS_MACHINE:
            if dtype_present_in_args: raise ValueError("You cannot cast a sapiens_machine model in a new `dtype`. Make sure to load the model using `from_pretrained` using the desired `dtype` by passing the correct `torch_dtype` argument.")
            if getattr(self, "is_loaded_in_8bit", False): raise ValueError("`.to` is not supported for `8-bit` sapiens_machine models. Please use the model as it is, since the model has already been set to the correct devices and casted to the correct `dtype`.")
            elif version.parse(importlib.metadata.version("sapiens_machine")) < version.parse("1.0.0"): raise ValueError(f"Calling `to()` is not supported for `4-bit` quantized models with the installed version of sapiens_machine. The current device is `{self.device}`. If you intended to move the model, please install sapiens_machine >= 1.0.0.")
        elif getattr(self, "quantization_method", None) == QuantizationMethod.GPTQ:
            if dtype_present_in_args: raise ValueError("You cannot cast a GPTQ model in a new `dtype`. Make sure to load the model using `from_pretrained` using the desired `dtype` by passing the correct `torch_dtype` argument.")
        return super().to(*args, **kwargs)
    def half(self, *args):
        if getattr(self, "is_quantized", False): raise ValueError("`.half()` is not supported for quantized model. Please use the model as it is, since the model has already been casted to the correct `dtype`.")
        else: return super().half(*args)
    def float(self, *args):
        if getattr(self, "is_quantized", False): raise ValueError("`.float()` is not supported for quantized model. Please use the model as it is, since the model has already been casted to the correct `dtype`.")
        else: return super().float(*args)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], *model_args, config: Optional[Union[PretrainedConfig, str, os.PathLike]] = None,
    cache_dir: Optional[Union[str, os.PathLike]] = None, ignore_mismatched_sizes: bool = False, force_download: bool = False, local_files_only: bool = False,
    token: Optional[Union[str, bool]] = None, revision: str = "main", use_safetensors: bool = None, **kwargs) -> "PreTrainedModel":
        state_dict = kwargs.pop("state_dict", None)
        from_tf = kwargs.pop("from_tf", False)
        from_flax = kwargs.pop("from_flax", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        output_loading_info = kwargs.pop("output_loading_info", False)
        use_auth_token = kwargs.pop("use_auth_token", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        _ = kwargs.pop("mirror", None)
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        _fast_init = kwargs.pop("_fast_init", True)
        torch_dtype = kwargs.pop("torch_dtype", None)
        low_cpu_mem_usage = kwargs.pop("low_cpu_mem_usage", None)
        device_map = kwargs.pop("device_map", None)
        max_memory = kwargs.pop("max_memory", None)
        offload_folder = kwargs.pop("offload_folder", None)
        offload_state_dict = kwargs.pop("offload_state_dict", False)
        offload_buffers = kwargs.pop("offload_buffers", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        quantization_config = kwargs.pop("quantization_config", None)
        subfolder = kwargs.pop("subfolder", "")
        commit_hash = kwargs.pop("_commit_hash", None)
        variant = kwargs.pop("variant", None)
        adapter_kwargs = kwargs.pop("adapter_kwargs", {})
        adapter_name = kwargs.pop("adapter_name", "default")
        use_flash_attention_2 = kwargs.pop("use_flash_attention_2", False)
        generation_config = kwargs.pop("generation_config", None)
        gguf_file = kwargs.pop("gguf_file", None)
        gguf_path = None
        if is_fsdp_enabled(): low_cpu_mem_usage = True
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None and adapter_kwargs is not None and "token" not in adapter_kwargs: adapter_kwargs["token"] = token
        if use_safetensors is None and not is_safetensors_available(): use_safetensors = False
        if trust_remote_code is True: logger.warning("The argument `trust_remote_code` is to be used with Auto classes. It has no effect here and is ignored.")
        if gguf_file is not None and not is_sapiens_accelerator_available(): raise ValueError("sapiens_accelerator is required when loading a GGUF file `pip install sapiens_accelerator`.")
        if commit_hash is None:
            if not isinstance(config, PretrainedConfig):
                resolved_config_file = cached_file(pretrained_model_name_or_path, CONFIG_NAME, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download,
                proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False, _raise_exceptions_for_connection_errors=False)
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            else: commit_hash = getattr(config, "_commit_hash", None)
        if is_peft_available():
            _adapter_model_path = adapter_kwargs.pop("_adapter_model_path", None)
            if _adapter_model_path is None: _adapter_model_path = find_adapter_config_file(pretrained_model_name_or_path, cache_dir=cache_dir, force_download=force_download,
            resume_download=resume_download, proxies=proxies, local_files_only=local_files_only, _commit_hash=commit_hash, **adapter_kwargs)
            if _adapter_model_path is not None and os.path.isfile(_adapter_model_path):
                with open(_adapter_model_path, "r", encoding="utf-8") as f:
                    _adapter_model_path = pretrained_model_name_or_path
                    pretrained_model_name_or_path = json.load(f)["base_model_name_or_path"]
        else: _adapter_model_path = None
        if isinstance(device_map, torch.device): device_map = {"": device_map}
        elif isinstance(device_map, str) and device_map not in ["auto", "balanced", "balanced_low_0", "sequential"]:
            try: device_map = {"": torch.device(device_map)}
            except RuntimeError: raise ValueError(f"When passing device_map as a string, the value needs to be a device name (e.g. cpu, cuda:0) or 'auto', 'balanced', 'balanced_low_0', 'sequential' but found {device_map}.")
        elif isinstance(device_map, int):
            if device_map < 0: raise ValueError("You can't pass device_map as a negative int. If you want to put the model on the cpu, pass device_map = 'cpu' ")
            else: device_map = {"": device_map}
        if device_map is not None:
            if low_cpu_mem_usage is None: low_cpu_mem_usage = True
            elif not low_cpu_mem_usage: raise ValueError("Passing along a `device_map` requires `low_cpu_mem_usage=True`")
        if low_cpu_mem_usage:
            if is_deepspeed_zero3_enabled(): raise ValueError("DeepSpeed Zero-3 is not compatible with `low_cpu_mem_usage=True` or with passing a `device_map`.")
            elif not is_sapiens_accelerator_available(): raise ImportError(f"Using `low_cpu_mem_usage=True` or a `device_map` requires SapiensAccelerator: `pip install 'sapiens_accelerator>={SAPIENS_ACCELERATOR_MIN_VERSION}'`")
        if load_in_4bit or load_in_8bit:
            if quantization_config is not None: raise ValueError("You can't pass `load_in_4bit`or `load_in_8bit` as a kwarg when passing `quantization_config` argument at the same time.")
            config_dict = {k: v for k, v in kwargs.items() if k in inspect.signature(SapiensMachineConfig).parameters}
            config_dict = {**config_dict, "load_in_4bit": load_in_4bit, "load_in_8bit": load_in_8bit}
            quantization_config, kwargs = SapiensMachineConfig.from_dict(config_dict=config_dict, return_unused_kwargs=True, **kwargs)
            logger.warning("The `load_in_4bit` and `load_in_8bit` arguments are deprecated and will be removed in the future versions. Please, pass a `SapiensMachineConfig` object in `quantization_config` argument instead.")
        from_pt = not (from_tf | from_flax)
        user_agent = {"file_type": "model", "framework": "pytorch", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        if not isinstance(config, PretrainedConfig):
            config_path = config if config is not None else pretrained_model_name_or_path
            config, model_kwargs = cls.config_class.from_pretrained(config_path, cache_dir=cache_dir, return_unused_kwargs=True, force_download=force_download, resume_download=resume_download, proxies=proxies, local_files_only=local_files_only,
            token=token, revision=revision, subfolder=subfolder, _from_auto=from_auto_class, _from_pipeline=from_pipeline, **kwargs)
        else:
            config = copy.deepcopy(config)
            kwarg_attn_imp = kwargs.pop("attn_implementation", None)
            if kwarg_attn_imp is not None: config._attn_implementation = kwarg_attn_imp
            model_kwargs = kwargs
        pre_quantized = getattr(config, "quantization_config", None) is not None
        if pre_quantized or quantization_config is not None:
            if pre_quantized: config.quantization_config = AutoHfQuantizer.merge_quantization_configs(config.quantization_config, quantization_config)
            else: config.quantization_config = quantization_config
            hf_quantizer = AutoHfQuantizer.from_config(config.quantization_config, pre_quantized=pre_quantized)
        else: hf_quantizer = None
        if hf_quantizer is not None:
            hf_quantizer.validate_environment(torch_dtype=torch_dtype, from_tf=from_tf, from_flax=from_flax, device_map=device_map)
            torch_dtype = hf_quantizer.update_torch_dtype(torch_dtype)
            device_map = hf_quantizer.update_device_map(device_map)
            user_agent["quant"] = hf_quantizer.quantization_config.quant_method.value
            if low_cpu_mem_usage is None:
                low_cpu_mem_usage = True
                logger.warning("`low_cpu_mem_usage` was None, now set to True since model is quantized.")
        is_quantized = hf_quantizer is not None
        is_sharded = False
        sharded_metadata = None
        loading_info = None
        keep_in_fp32_modules = None
        use_keep_in_fp32_modules = False
        if gguf_file is not None and hf_quantizer is not None: raise ValueError("You cannot combine Quantization and loading a model from a GGUF file, try again by making sure you did not passed a `quantization_config` or that you did not load a quantized model from the Hub.")
        if pretrained_model_name_or_path is not None and gguf_file is None:
            pretrained_model_name_or_path = str(pretrained_model_name_or_path)
            is_local = os.path.isdir(pretrained_model_name_or_path)
            if is_local:
                if from_tf and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index")): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index")
                elif from_tf and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME)): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME)
                elif from_flax and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)
                elif use_safetensors is not False and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_NAME, variant))): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_NAME, variant))
                elif use_safetensors is not False and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant))):
                    archive_file = os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant))
                    is_sharded = True
                elif not use_safetensors and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_NAME, variant))): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_NAME, variant))
                elif not use_safetensors and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_INDEX_NAME, variant))):
                    archive_file = os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_INDEX_NAME, variant))
                    is_sharded = True
                elif not use_safetensors and (os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index")) or os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME))): raise EnvironmentError(f"Error no file named {_add_variant(WEIGHTS_NAME, variant)} found in directory {pretrained_model_name_or_path} but there is a file for TensorFlow weights. Use `from_tf=True` to load this model from those weights.")
                elif not use_safetensors and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)): raise EnvironmentError(f"Error no file named {_add_variant(WEIGHTS_NAME, variant)} found in directory {pretrained_model_name_or_path} but there is a file for Flax weights. Use `from_flax=True` to load this model from those weights.")
                elif use_safetensors: raise EnvironmentError(f"Error no file named {_add_variant(SAFE_WEIGHTS_NAME, variant)} found in directory {pretrained_model_name_or_path}.")
                else: raise EnvironmentError(f"Error no file named {_add_variant(WEIGHTS_NAME, variant)}, {_add_variant(SAFE_WEIGHTS_NAME, variant)}, {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME + '.index'} or {FLAX_WEIGHTS_NAME} found in directory {pretrained_model_name_or_path}.")
            elif os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path)):
                archive_file = pretrained_model_name_or_path
                is_local = True
            elif os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path + ".index")):
                if not from_tf: raise ValueError(f"We found a TensorFlow checkpoint at {pretrained_model_name_or_path + '.index'}, please set from_tf to True to load from this checkpoint.")
                archive_file = os.path.join(subfolder, pretrained_model_name_or_path + ".index")
                is_local = True
            elif is_remote_url(pretrained_model_name_or_path):
                filename = pretrained_model_name_or_path
                resolved_archive_file = download_url(pretrained_model_name_or_path)
            else:
                if from_tf: filename = TF2_WEIGHTS_NAME
                elif from_flax: filename = FLAX_WEIGHTS_NAME
                elif use_safetensors is not False: filename = _add_variant(SAFE_WEIGHTS_NAME, variant)
                else: filename = _add_variant(WEIGHTS_NAME, variant)
                try:
                    cached_file_kwargs = {"cache_dir": cache_dir, "force_download": force_download, "proxies": proxies, "resume_download": resume_download, "local_files_only": local_files_only,
                    "token": token, "user_agent": user_agent, "revision": revision, "subfolder": subfolder, "_raise_exceptions_for_gated_repo": False, "_raise_exceptions_for_missing_entries": False, "_commit_hash": commit_hash}
                    resolved_archive_file = cached_file(pretrained_model_name_or_path, filename, **cached_file_kwargs)
                    if resolved_archive_file is None and filename == _add_variant(SAFE_WEIGHTS_NAME, variant):
                        resolved_archive_file = cached_file(pretrained_model_name_or_path, _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant), **cached_file_kwargs)
                        if resolved_archive_file is not None: is_sharded = True
                        elif use_safetensors:
                            if revision == "main": resolved_archive_file, revision, is_sharded = auto_conversion(pretrained_model_name_or_path, **cached_file_kwargs)
                            cached_file_kwargs["revision"] = revision
                            if resolved_archive_file is None: raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {_add_variant(SAFE_WEIGHTS_NAME, variant)} or {_add_variant(SAFE_WEIGHTS_INDEX_NAME, variant)} and thus cannot be loaded with `safetensors`. Please make sure that the model has been saved with `safe_serialization=True` or do not set `use_safetensors=True`.")
                        else:
                            filename = _add_variant(WEIGHTS_NAME, variant)
                            resolved_archive_file = cached_file(pretrained_model_name_or_path, filename, **cached_file_kwargs)
                    if resolved_archive_file is None and filename == _add_variant(WEIGHTS_NAME, variant):
                        resolved_archive_file = cached_file(pretrained_model_name_or_path, _add_variant(WEIGHTS_INDEX_NAME, variant), **cached_file_kwargs)
                        if resolved_archive_file is not None: is_sharded = True
                    if not local_files_only and not is_offline_mode():
                        if resolved_archive_file is not None:
                            if filename in [WEIGHTS_NAME, WEIGHTS_INDEX_NAME]:
                                safe_weights_name = SAFE_WEIGHTS_INDEX_NAME if is_sharded else SAFE_WEIGHTS_NAME
                                has_file_kwargs = {"revision": revision, "proxies": proxies, "token": token, "cache_dir": cache_dir, "local_files_only": local_files_only}
                                cached_file_kwargs = {"cache_dir": cache_dir, "force_download": force_download, "resume_download": resume_download, "local_files_only": local_files_only,
                                "user_agent": user_agent, "subfolder": subfolder, "_raise_exceptions_for_gated_repo": False, "_raise_exceptions_for_missing_entries": False, "_commit_hash": commit_hash, **has_file_kwargs}
                                if not has_file(pretrained_model_name_or_path, safe_weights_name, **has_file_kwargs): Thread(target=auto_conversion, args=(pretrained_model_name_or_path,), kwargs={"ignore_errors_during_conversion": True, **cached_file_kwargs}, name="Thread-autoconversion").start()
                        else:
                            has_file_kwargs = {"revision": revision, "proxies": proxies, "token": token, "cache_dir": cache_dir, "local_files_only": local_files_only}
                            if has_file(pretrained_model_name_or_path, TF2_WEIGHTS_NAME, **has_file_kwargs): raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {_add_variant(WEIGHTS_NAME, variant)} but there is a file for TensorFlow weights. Use `from_tf=True` to load this model from those weights.")
                            elif has_file(pretrained_model_name_or_path, FLAX_WEIGHTS_NAME, **has_file_kwargs): raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {_add_variant(WEIGHTS_NAME, variant)} but there is a file for Flax weights. Use `from_flax=True` to load this model from those weights.")
                            elif variant is not None and has_file(pretrained_model_name_or_path, WEIGHTS_NAME, **has_file_kwargs): raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {_add_variant(WEIGHTS_NAME, variant)} but there is a file without the variant {variant}. Use `variant=None` to load this model from those weights.")
                            else: raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {_add_variant(WEIGHTS_NAME, variant)}, {_add_variant(SAFE_WEIGHTS_NAME, variant)}, {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME} or {FLAX_WEIGHTS_NAME}.")
                except EnvironmentError: raise
                except Exception as e: raise EnvironmentError(f"Can't load the model for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a file named {_add_variant(WEIGHTS_NAME, variant)}, {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME} or {FLAX_WEIGHTS_NAME}.") from e
            if is_local:
                logger.info(f"loading weights file {archive_file}")
                resolved_archive_file = archive_file
            else: logger.info(f"loading weights file {filename} from cache at {resolved_archive_file}")
        elif gguf_file:
            from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
            if os.path.isfile(gguf_file): gguf_path = gguf_file
            else:
                cached_file_kwargs = {"cache_dir": cache_dir, "force_download": force_download, "proxies": proxies, "resume_download": resume_download,
                "local_files_only": local_files_only, "token": token, "user_agent": user_agent, "revision": revision, "subfolder": subfolder,
                "_raise_exceptions_for_gated_repo": False, "_raise_exceptions_for_missing_entries": False, "_commit_hash": commit_hash}
                gguf_path = cached_file(pretrained_model_name_or_path, gguf_file, **cached_file_kwargs)
            state_dict = load_gguf_checkpoint(gguf_path, return_tensors=True)["tensors"]
            resolved_archive_file = None
            is_sharded = False
        else: resolved_archive_file = None
        if is_sharded: resolved_archive_file, sharded_metadata = get_checkpoint_shard_files(pretrained_model_name_or_path, resolved_archive_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies,
        resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder, _commit_hash=commit_hash)
        if (is_safetensors_available() and isinstance(resolved_archive_file, str) and resolved_archive_file.endswith(".safetensors")):
            with safe_open(resolved_archive_file, framework="pt") as f: metadata = f.metadata()
            if metadata.get("format") == "pt": pass
            elif metadata.get("format") == "tf":
                from_tf = True
                logger.info("A TensorFlow safetensors file is being loaded in a PyTorch model.")
            elif metadata.get("format") == "flax":
                from_flax = True
                logger.info("A Flax safetensors file is being loaded in a PyTorch model.")
            elif metadata.get("format") == "mlx": pass
            else: raise ValueError(f"Incompatible safetensors file. File metadata is not ['pt', 'tf', 'flax', 'mlx'] but {metadata.get('format')}")
        from_pt = not (from_tf | from_flax)
        if from_pt:
            if not is_sharded and state_dict is None: state_dict = load_state_dict(resolved_archive_file)
            dtype_orig = None
            if torch_dtype is not None:
                if isinstance(torch_dtype, str):
                    if torch_dtype == "auto":
                        if hasattr(config, "torch_dtype") and config.torch_dtype is not None:
                            torch_dtype = config.torch_dtype
                            logger.info(f"Will use torch_dtype={torch_dtype} as defined in model's config object")
                        else:
                            if is_sharded and "dtype" in sharded_metadata: torch_dtype = sharded_metadata["dtype"]
                            elif not is_sharded: torch_dtype = get_state_dict_dtype(state_dict)
                            else:
                                one_state_dict = load_state_dict(resolved_archive_file[0])
                                torch_dtype = get_state_dict_dtype(one_state_dict)
                                del one_state_dict
                            logger.info("Since the `torch_dtype` attribute can't be found in model's config object, will use torch_dtype={torch_dtype} as derived from model's weights")
                    elif hasattr(torch, torch_dtype): torch_dtype = getattr(torch, torch_dtype)
                    else: raise ValueError(f'`torch_dtype` can be one of: `torch.dtype`, `"auto"` or a string of a valid `torch.dtype`, but received {torch_dtype}')
                dtype_orig = cls._set_default_torch_dtype(torch_dtype)
            use_keep_in_fp32_modules = (cls._keep_in_fp32_modules is not None) and ((torch_dtype == torch.float16) or hasattr(hf_quantizer, "use_keep_in_fp32_modules"))
            if is_sharded: loaded_state_dict_keys = sharded_metadata["all_checkpoint_keys"]
            else: loaded_state_dict_keys = list(state_dict.keys())
            if gguf_path is None and (low_cpu_mem_usage or (use_keep_in_fp32_modules and is_sapiens_accelerator_available())): state_dict = None
        config.name_or_path = pretrained_model_name_or_path
        init_contexts = [no_init_weights(_enable=_fast_init)]
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            logger.info("Detected DeepSpeed ZeRO-3: activating zero.init() for this model")
            init_contexts = [deepspeed.zero.Init(config_dict_or_path=deepspeed_config())] + init_contexts
        elif low_cpu_mem_usage: init_contexts.append(init_empty_weights())
        config = copy.deepcopy(config)
        config = cls._autoset_attn_implementation(config, use_flash_attention_2=use_flash_attention_2, torch_dtype=torch_dtype, device_map=device_map)
        with ContextManagers(init_contexts): model = cls(config, *model_args, **model_kwargs)
        config = model.config
        if use_keep_in_fp32_modules:
            if is_sapiens_accelerator_available() and not is_deepspeed_zero3_enabled(): low_cpu_mem_usage = True
            keep_in_fp32_modules = model._keep_in_fp32_modules
        else: keep_in_fp32_modules = []
        if hf_quantizer is not None:
            hf_quantizer.preprocess_model(model=model, device_map=device_map, keep_in_fp32_modules=keep_in_fp32_modules)
            config._pre_quantization_dtype = torch_dtype
        if isinstance(device_map, str):
            special_dtypes = {}
            if hf_quantizer is not None: special_dtypes.update(hf_quantizer.get_special_dtypes_update(model, torch_dtype))
            special_dtypes.update({name: torch.float32 for name, _ in model.named_parameters() if any(m in name for m in keep_in_fp32_modules)})
            target_dtype = torch_dtype
            if hf_quantizer is not None: target_dtype = hf_quantizer.adjust_target_dtype(target_dtype)
            no_split_modules = model._get_no_split_modules(device_map)
            if device_map not in ["auto", "balanced", "balanced_low_0", "sequential"]: raise ValueError("If passing a string for `device_map`, please choose 'auto', 'balanced', 'balanced_low_0' or 'sequential'.")
            device_map_kwargs = {"no_split_module_classes": no_split_modules}
            if "special_dtypes" in inspect.signature(infer_auto_device_map).parameters: device_map_kwargs["special_dtypes"] = special_dtypes
            elif len(special_dtypes) > 0: logger.warning("This model has some weights that should be kept in higher precision, you need to upgrade `sapiens_accelerator` to properly deal with them (`pip install --upgrade sapiens_accelerator`).")
            if device_map != "sequential": max_memory = get_balanced_memory(model, dtype=target_dtype, low_zero=(device_map == "balanced_low_0"), max_memory=max_memory, **device_map_kwargs)
            else: max_memory = get_max_memory(max_memory)
            if hf_quantizer is not None: max_memory = hf_quantizer.adjust_max_memory(max_memory)
            device_map_kwargs["max_memory"] = max_memory
            model.tie_weights()
            device_map = infer_auto_device_map(model, dtype=target_dtype, **device_map_kwargs)
            if hf_quantizer is not None: hf_quantizer.validate_environment(device_map=device_map)
        elif device_map is not None:
            model.tie_weights()
            tied_params = find_tied_parameters(model)
            check_tied_parameters_on_same_device(tied_params, device_map)
        if from_tf:
            if resolved_archive_file.endswith(".index"): model = cls.load_tf_weights(model, config, resolved_archive_file[:-6])
            else:
                try:
                    from .modeling_tf_pytorch_utils import load_tf2_checkpoint_in_pytorch_model
                    model, loading_info = load_tf2_checkpoint_in_pytorch_model(model, resolved_archive_file, allow_missing_keys=True, output_loading_info=True)
                except ImportError:
                    logger.error("Loading a TensorFlow model in PyTorch, requires both PyTorch and TensorFlow to be installed. Please see https://pytorch.org/ and https://www.tensorflow.org/install/ for installation instructions.")
                    raise
        elif from_flax:
            try:
                from .modeling_flax_pytorch_utils import load_flax_checkpoint_in_pytorch_model
                model = load_flax_checkpoint_in_pytorch_model(model, resolved_archive_file)
            except ImportError:
                logger.error("Loading a Flax model in PyTorch, requires both PyTorch and Flax to be installed. Please see https://pytorch.org/ and https://flax.readthedocs.io/en/latest/installation.html for installation instructions.")
                raise
        elif from_pt:
            if dtype_orig is not None: torch.set_default_dtype(dtype_orig)
            (model, missing_keys, unexpected_keys, mismatched_keys, offload_index, error_msgs) = cls._load_pretrained_model(model, state_dict, loaded_state_dict_keys, resolved_archive_file, pretrained_model_name_or_path,
            ignore_mismatched_sizes=ignore_mismatched_sizes, sharded_metadata=sharded_metadata, _fast_init=_fast_init, low_cpu_mem_usage=low_cpu_mem_usage, device_map=device_map, offload_folder=offload_folder, offload_state_dict=offload_state_dict,
            dtype=torch_dtype, hf_quantizer=hf_quantizer, keep_in_fp32_modules=keep_in_fp32_modules, gguf_path=gguf_path)
        model.tie_weights()
        model.eval()
        if model.can_generate() and generation_config is not None:
            logger.info("The user-defined `generation_config` will be used to override the default generation config.")
            model.generation_config = model.generation_config.from_dict(generation_config.to_dict())
        elif model.can_generate() and pretrained_model_name_or_path is not None:
            try: model.generation_config = GenerationConfig.from_pretrained(pretrained_model_name_or_path, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download, proxies=proxies, local_files_only=local_files_only,
            token=token, revision=revision, subfolder=subfolder, _from_auto=from_auto_class, _from_pipeline=from_pipeline, **kwargs)
            except OSError:
                logger.info("Generation config file not found, using a generation config created from the model config.")
                pass
        if device_map is not None:
            device_map_kwargs = {"device_map": device_map, "offload_dir": offload_folder, "offload_index": offload_index, "offload_buffers": offload_buffers}
            if "skip_keys" in inspect.signature(dispatch_model).parameters: device_map_kwargs["skip_keys"] = model._skip_keys_device_placement
            if ("force_hooks" in inspect.signature(dispatch_model).parameters and hf_quantizer is not None and hf_quantizer.quantization_config.quant_method == QuantizationMethod.HQQ): device_map_kwargs["force_hooks"] = True
            if (hf_quantizer is not None and hf_quantizer.quantization_config.quant_method == QuantizationMethod.FBGEMM_FP8 and isinstance(device_map, dict) and ("cpu" in device_map.values() or "disk" in device_map.values())): device_map_kwargs["offload_buffers"] = True
            if not is_fsdp_enabled() and not is_deepspeed_zero3_enabled(): dispatch_model(model, **device_map_kwargs)
        if hf_quantizer is not None:
            hf_quantizer.postprocess_model(model)
            model.hf_quantizer = hf_quantizer
        if _adapter_model_path is not None: model.load_adapter(_adapter_model_path, adapter_name=adapter_name, token=token, adapter_kwargs=adapter_kwargs)
        if output_loading_info:
            if loading_info is None: loading_info = {"missing_keys": missing_keys, "unexpected_keys": unexpected_keys, "mismatched_keys": mismatched_keys, "error_msgs": error_msgs}
            return model, loading_info
        return model
    @classmethod
    def _load_pretrained_model(cls, model, state_dict, loaded_keys, resolved_archive_file, pretrained_model_name_or_path, ignore_mismatched_sizes=False, sharded_metadata=None, _fast_init=True, low_cpu_mem_usage=False, device_map=None, offload_folder=None,
    offload_state_dict=None, dtype=None, hf_quantizer=None, keep_in_fp32_modules=None, gguf_path=None):
        is_safetensors = False
        is_quantized = hf_quantizer is not None
        state_dict_folder = None
        state_dict_index = None
        if device_map is not None and "disk" in device_map.values():
            archive_file = (resolved_archive_file[0] if isinstance(resolved_archive_file, (list, tuple)) else resolved_archive_file)
            is_safetensors = archive_file.endswith(".safetensors")
            if offload_folder is None and not is_safetensors: raise ValueError("The current `device_map` had weights offloaded to the disk. Please provide an `offload_folder` for them. Alternatively, make sure you have `safetensors` installed if the model you are using offers the weights in this format.")
            if offload_folder is not None: os.makedirs(offload_folder, exist_ok=True)
            if offload_state_dict is None: offload_state_dict = True
        is_sharded_safetensors = is_safetensors and sharded_metadata is not None
        model.tie_weights()
        model_state_dict = model.state_dict()
        expected_keys = list(model_state_dict.keys())
        prefix = model.base_model_prefix
        def _fix_key(key):
            if "beta" in key: return key.replace("beta", "bias")
            if "gamma" in key: return key.replace("gamma", "weight")
            if hasattr(nn.utils.parametrizations, "weight_norm"):
                if "weight_g" in key: return key.replace("weight_g", "parametrizations.weight.original0")
                if "weight_v" in key: return key.replace("weight_v", "parametrizations.weight.original1")
            else:
                if "parametrizations.weight.original0" in key: return key.replace("parametrizations.weight.original0", "weight_g")
                if "parametrizations.weight.original1" in key: return key.replace("parametrizations.weight.original1", "weight_v")
            return key
        original_loaded_keys = loaded_keys
        loaded_keys = [_fix_key(key) for key in loaded_keys]
        if len(prefix) > 0:
            has_prefix_module = any(s.startswith(prefix) for s in loaded_keys)
            expects_prefix_module = any(s.startswith(prefix) for s in expected_keys)
        else:
            has_prefix_module = False
            expects_prefix_module = False
        remove_prefix_from_model = not has_prefix_module and expects_prefix_module
        add_prefix_to_model = has_prefix_module and not expects_prefix_module
        if remove_prefix_from_model:
            _prefix = f"{prefix}."
            expected_keys_not_prefixed = [s for s in expected_keys if not s.startswith(_prefix)]
            expected_keys = [s[len(_prefix) :] if s.startswith(_prefix) else s for s in expected_keys]
        elif add_prefix_to_model: expected_keys = [".".join([prefix, s]) for s in expected_keys]
        missing_keys = sorted(set(expected_keys) - set(loaded_keys))
        unexpected_keys = set(loaded_keys) - set(expected_keys)
        model_buffers = {n for n, _ in model.named_buffers()}
        if remove_prefix_from_model: model_buffers = {key[len(_prefix) :] if key.startswith(_prefix) else key for key in model_buffers}
        elif add_prefix_to_model: model_buffers = {".".join([prefix, key]) for key in model_buffers}
        unexpected_keys = sorted(unexpected_keys - model_buffers)
        model.tie_weights()
        if device_map is None and not is_fsdp_enabled() and not is_deepspeed_zero3_enabled():
            ptrs = collections.defaultdict(list)
            for name, tensor in model.state_dict().items():
                id_tensor = id_tensor_storage(tensor)
                ptrs[id_tensor].append(name)
            tied_params = [names for _, names in ptrs.items() if len(names) > 1]
        else: tied_params = find_tied_parameters(model)
        for group in tied_params:
            if remove_prefix_from_model: group = [key[len(_prefix) :] if key.startswith(_prefix) else key for key in group]
            elif add_prefix_to_model: group = [".".join([prefix, key]) for key in group]
            missing_in_group = [k for k in missing_keys if k in group]
            if len(missing_in_group) > 0 and len(missing_in_group) < len(group): missing_keys = [k for k in missing_keys if k not in missing_in_group]
        if cls._keys_to_ignore_on_load_missing is not None:
            for pat in cls._keys_to_ignore_on_load_missing:
                missing_keys = [k for k in missing_keys if re.search(pat, k) is None]
        if cls._keys_to_ignore_on_load_unexpected is not None:
            for pat in cls._keys_to_ignore_on_load_unexpected:
                unexpected_keys = [k for k in unexpected_keys if re.search(pat, k) is None]
        if hf_quantizer is not None: missing_keys = hf_quantizer.update_missing_keys(model, missing_keys, prefix)
        if low_cpu_mem_usage:
            for key in missing_keys:
                if key in list(model_state_dict.keys()): key = key
                elif f"{prefix}.{key}" in list(model_state_dict.keys()): key = f"{prefix}.{key}"
                elif key.startswith(prefix) and ".".join(key.split(".")[1:]) in list(model_state_dict.keys()): key = ".".join(key.split(".")[1:])
                param = model_state_dict[key]
                target_dtype = dtype
                if (keep_in_fp32_modules is not None and dtype == torch.float16 and any(module_to_keep_in_fp32 in key.split(".") for module_to_keep_in_fp32 in keep_in_fp32_modules)): target_dtype = torch.float32
                if param.device == torch.device("meta"):
                    value = torch.empty(*param.size(), dtype=target_dtype)
                    if (not is_quantized or getattr(hf_quantizer, "requires_parameters_quantization", False) or not hf_quantizer.check_quantized_param(model, param_value=value, param_name=key, state_dict={})): set_module_tensor_to_device(model, key, "cpu", value)
                    else: hf_quantizer.create_quantized_param(model, value, key, "cpu", state_dict, unexpected_keys)
        if _fast_init:
            if not ignore_mismatched_sizes:
                if remove_prefix_from_model: _loaded_keys = [f"{prefix}.{k}" for k in loaded_keys]
                elif add_prefix_to_model: _loaded_keys = [k[len(prefix) + 1 :] for k in loaded_keys]
                else: _loaded_keys = loaded_keys
                not_initialized_submodules = set_initialized_submodules(model, _loaded_keys)
                if hasattr(model.config, "tie_word_embeddings") and model.config.tie_word_embeddings:
                    output_embeddings = model.get_output_embeddings()
                    if output_embeddings is not None:
                        if not hasattr(output_embeddings, "bias") or output_embeddings.bias is None: output_embeddings._is_hf_initialized = True
            else: not_initialized_submodules = dict(model.named_modules())
            if is_deepspeed_zero3_enabled() and not is_quantized:
                import deepspeed
                not_initialized_parameters = list(set(itertools.chain.from_iterable(submodule.parameters(recurse=False) for submodule in not_initialized_submodules.values())))
                with deepspeed.zero.GatheredParameters(not_initialized_parameters, modifier_rank=0): model.apply(model._initialize_weights)
            else: model.apply(model._initialize_weights)
        if keep_in_fp32_modules is not None:
            for name, param in model.named_parameters():
                if any(module_to_keep_in_fp32 in name.split(".") for module_to_keep_in_fp32 in keep_in_fp32_modules): param.data = param.data.to(torch.float32)
        start_prefix = ""
        model_to_load = model
        if len(cls.base_model_prefix) > 0 and not hasattr(model, cls.base_model_prefix) and has_prefix_module: start_prefix = cls.base_model_prefix + "."
        if len(cls.base_model_prefix) > 0 and hasattr(model, cls.base_model_prefix) and not has_prefix_module:
            model_to_load = getattr(model, cls.base_model_prefix)
            base_model_expected_keys = list(model_to_load.state_dict().keys())
            if any(key in expected_keys_not_prefixed and key not in base_model_expected_keys for key in loaded_keys): raise ValueError("The state dictionary of the model you are trying to load is corrupted. Are you sure it was properly saved?")
            if device_map is not None: device_map = {k.replace(f"{cls.base_model_prefix}.", ""): v for k, v in device_map.items()}
        def _find_mismatched_keys(state_dict, model_state_dict, loaded_keys, add_prefix_to_model, remove_prefix_from_model, ignore_mismatched_sizes):
            mismatched_keys = []
            if ignore_mismatched_sizes:
                for checkpoint_key in loaded_keys:
                    if checkpoint_key not in state_dict: continue
                    model_key = checkpoint_key
                    if remove_prefix_from_model: model_key = f"{prefix}.{checkpoint_key}"
                    elif add_prefix_to_model: model_key = ".".join(checkpoint_key.split(".")[1:])
                    if (model_key in model_state_dict and state_dict[checkpoint_key].shape != model_state_dict[model_key].shape):
                        if (state_dict[checkpoint_key].shape[-1] == 1 and state_dict[checkpoint_key].numel() * 2 == model_state_dict[model_key].numel()): pass
                        else:
                            mismatched_keys.append((checkpoint_key, state_dict[checkpoint_key].shape, model_state_dict[model_key].shape))
                            del state_dict[checkpoint_key]
            return mismatched_keys
        if resolved_archive_file is not None: folder = os.path.sep.join(resolved_archive_file[0].split(os.path.sep)[:-1])
        else: folder = None
        if device_map is not None and is_safetensors:
            param_device_map = expand_device_map(device_map, original_loaded_keys, start_prefix)
            str_dtype = str(dtype).replace("torch.", "") if dtype is not None else "float32"
            if sharded_metadata is None:
                archive_file = (resolved_archive_file[0] if isinstance(resolved_archive_file, (list, tuple)) else resolved_archive_file)
                weight_map = {p: archive_file for p in original_loaded_keys}
            else: weight_map = {p: os.path.join(folder, f) for p, f in sharded_metadata["weight_map"].items()}
            offload_index = {p[len(start_prefix) :]: {"safetensors_file": f, "weight_name": p, "dtype": str_dtype} for p, f in weight_map.items() if p.startswith(start_prefix) and param_device_map[p[len(start_prefix) :]] == "disk"}
        else: offload_index = None
        if state_dict is not None:
            mismatched_keys = _find_mismatched_keys(state_dict, model_state_dict, original_loaded_keys, add_prefix_to_model, remove_prefix_from_model, ignore_mismatched_sizes)
            if gguf_path: error_msgs, offload_index, state_dict_index = _load_state_dict_into_meta_model(model_to_load, state_dict, start_prefix, expected_keys, device_map=device_map, offload_folder=offload_folder, offload_index=offload_index,
            state_dict_folder=state_dict_folder, state_dict_index=state_dict_index, dtype=dtype, hf_quantizer=hf_quantizer, is_safetensors=is_safetensors, keep_in_fp32_modules=keep_in_fp32_modules, unexpected_keys=unexpected_keys)
            else:
                assign_to_params_buffers = check_support_param_buffer_assignment(model_to_load, state_dict, start_prefix)
                error_msgs = _load_state_dict_into_model(model_to_load, state_dict, start_prefix, assign_to_params_buffers)
        else:
            if not isinstance(resolved_archive_file, list): resolved_archive_file = [resolved_archive_file]
            error_msgs = []
            mismatched_keys = []
            if not is_safetensors: offload_index = {} if device_map is not None and "disk" in device_map.values() else None
            if offload_state_dict:
                state_dict_folder = tempfile.mkdtemp()
                state_dict_index = {}
            else:
                state_dict_folder = None
                state_dict_index = None
            if is_sharded_safetensors:
                disk_only_shard_files = get_disk_only_shard_files(device_map, sharded_metadata=sharded_metadata, start_prefix=start_prefix)
                disk_only_shard_files = [os.path.join(folder, f) for f in disk_only_shard_files]
            else: disk_only_shard_files = []
            assign_to_params_buffers = None
            for shard_file in resolved_archive_file:
                if shard_file in disk_only_shard_files: continue
                state_dict = load_state_dict(shard_file, is_quantized=is_quantized)
                mismatched_keys += _find_mismatched_keys(state_dict, model_state_dict, original_loaded_keys, add_prefix_to_model, remove_prefix_from_model, ignore_mismatched_sizes)
                if low_cpu_mem_usage:
                    if is_fsdp_enabled() and not is_local_dist_rank_0() and not is_quantized:
                        for key, param in model_to_load.state_dict().items():
                            if param.device == torch.device("meta"): set_module_tensor_to_device(model_to_load, key, "cpu", torch.empty(*param.size(), dtype=dtype))
                    else:
                        new_error_msgs, offload_index, state_dict_index = _load_state_dict_into_meta_model(model_to_load, state_dict, start_prefix, expected_keys, device_map=device_map, offload_folder=offload_folder, offload_index=offload_index,
                        state_dict_folder=state_dict_folder, state_dict_index=state_dict_index, dtype=dtype, hf_quantizer=hf_quantizer, is_safetensors=is_safetensors, keep_in_fp32_modules=keep_in_fp32_modules, unexpected_keys=unexpected_keys)
                        error_msgs += new_error_msgs
                else:
                    if assign_to_params_buffers is None: assign_to_params_buffers = check_support_param_buffer_assignment(model_to_load, state_dict, start_prefix)
                    error_msgs += _load_state_dict_into_model(model_to_load, state_dict, start_prefix, assign_to_params_buffers)
                del state_dict
                gc.collect()
            if offload_index is not None and len(offload_index) > 0:
                if model != model_to_load:
                    prefix = cls.base_model_prefix
                    if not is_safetensors:
                        for weight_name in offload_index: shutil.move(os.path.join(offload_folder, f"{weight_name}.dat"), os.path.join(offload_folder, f"{prefix}.{weight_name}.dat"))
                    offload_index = {f"{prefix}.{key}": value for key, value in offload_index.items()}
                if not is_safetensors:
                    save_offload_index(offload_index, offload_folder)
                    offload_index = None
            if offload_state_dict:
                load_offloaded_weights(model_to_load, state_dict_index, state_dict_folder)
                shutil.rmtree(state_dict_folder)
        if len(error_msgs) > 0:
            error_msg = "\n\t".join(error_msgs)
            if "size mismatch" in error_msg: error_msg += ("\n\tYou may consider adding `ignore_mismatched_sizes=True` in the model `from_pretrained` method.")
            raise RuntimeError(f"Error(s) in loading state_dict for {model.__class__.__name__}:\n\t{error_msg}")
        if len(unexpected_keys) > 0:
            archs = [] if model.config.architectures is None else model.config.architectures
            warner = logger.warning if model.__class__.__name__ in archs else logger.info
        else: logger.info(f"All model checkpoint weights were used when initializing {model.__class__.__name__}.\n")
        if len(missing_keys) > 0: logger.warning(f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at {pretrained_model_name_or_path} and are newly initialized: {missing_keys}\nYou should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.")
        elif len(mismatched_keys) == 0: logger.info(f"All the weights of {model.__class__.__name__} were initialized from the model checkpoint at {pretrained_model_name_or_path}.\nIf your task is similar to the task the model of the checkpoint was trained on, you can already use {model.__class__.__name__} for predictions without further training.")
        if len(mismatched_keys) > 0:
            mismatched_warning = "\n".join([f"- {key}: found shape {shape1} in the checkpoint and {shape2} in the model instantiated" for key, shape1, shape2 in mismatched_keys])
            logger.warning(f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at {pretrained_model_name_or_path} and are newly initialized because the shapes did not match:\n{mismatched_warning}\nYou should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.")
        return model, missing_keys, unexpected_keys, mismatched_keys, offload_index, error_msgs
    def retrieve_modules_from_names(self, names, add_prefix=False, remove_prefix=False):
        module_keys = {".".join(key.split(".")[:-1]) for key in names}
        module_keys = module_keys.union({".".join(key.split(".")[:-2]) for key in names if len(key) > 0 and key[-1].isdigit()})
        retrieved_modules = []
        for name, module in self.named_modules():
            if remove_prefix:
                _prefix = f"{self.base_model_prefix}."
                name = name[len(_prefix) :] if name.startswith(_prefix) else name
            elif add_prefix: name = ".".join([self.base_model_prefix, name]) if len(name) > 0 else self.base_model_prefix
            if name in module_keys: retrieved_modules.append(module)
        return retrieved_modules
    @staticmethod
    def _load_pretrained_model_low_mem(model, loaded_state_dict_keys, resolved_archive_file, start_prefix="", hf_quantizer=None, pretrained_model_name_or_path=None):
        _move_model_to_meta(model, loaded_state_dict_keys, start_prefix)
        state_dict = load_state_dict(resolved_archive_file)
        expected_keys = loaded_state_dict_keys
        error_msgs = _load_state_dict_into_meta_model(model, state_dict, start_prefix, expected_keys=expected_keys, hf_quantizer=hf_quantizer)
        return error_msgs
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoModel"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    def to_bettertransformer(self) -> "PreTrainedModel":
        if not is_optimum_available(): raise ImportError("The package `optimum` is required to use Better Transformer.")
        from optimum.version import __version__ as optimum_version
        if version.parse(optimum_version) < version.parse("1.7.0"): raise ImportError(f"Please install optimum>=1.7.0 to use Better Transformer. The version {optimum_version} was found.")
        from optimum.bettertransformer import BetterTransformer
        return BetterTransformer.transform(self)
    def reverse_bettertransformer(self):
        if not is_optimum_available(): raise ImportError("The package `optimum` is required to use Better Transformer.")
        from optimum.version import __version__ as optimum_version
        if version.parse(optimum_version) < version.parse("1.7.0"): raise ImportError(f"Please install optimum>=1.7.0 to use Better Transformer. The version {optimum_version} was found.")
        from optimum.bettertransformer import BetterTransformer
        return BetterTransformer.reverse(self)
    def warn_if_padding_and_no_attention_mask(self, input_ids, attention_mask):
        if is_torch_fx_proxy(input_ids) or torch.jit.is_tracing() or is_torchdynamo_compiling(): return
        if (attention_mask is not None) or (self.config.pad_token_id is None): return
        if self.config.pad_token_id in input_ids[:, [-1, 0]]:
            warn_string = ("We strongly recommend passing in an `attention_mask` since your input_ids may be padded.")
            if ((self.config.bos_token_id is not None and self.config.bos_token_id == self.config.pad_token_id) or (self.config.eos_token_id is not None and self.config.eos_token_id == self.config.pad_token_id) or (self.config.sep_token_id is not None and self.config.sep_token_id == self.config.pad_token_id)): warn_string += (f"\nYou may ignore this warning if your `pad_token_id` ({self.config.pad_token_id}) is identical to the `bos_token_id` ({self.config.bos_token_id}), `eos_token_id` ({self.config.eos_token_id}), or the `sep_token_id` ({self.config.sep_token_id}), and your input is not padded.")
            logger.warning_once(warn_string)
    @property
    def _is_quantized_training_enabled(self):
        warnings.warn("`_is_quantized_training_enabled` is going to be deprecated in transformers 4.39.0. Please use `model.hf_quantizer.is_trainable` instead", FutureWarning)
        if not hasattr(self, "hf_quantizer"): return False
        return self.hf_quantizer.is_trainable
PreTrainedModel.push_to_hub = copy_func(PreTrainedModel.push_to_hub)
if PreTrainedModel.push_to_hub.__doc__ is not None: PreTrainedModel.push_to_hub.__doc__ = PreTrainedModel.push_to_hub.__doc__.format(object="model", object_class="AutoModel", object_files="model file")
class PoolerStartLogits(nn.Module):
    def __init__(self, config: PretrainedConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, 1)
    def forward(self, hidden_states: torch.FloatTensor, p_mask: Optional[torch.FloatTensor] = None) -> torch.FloatTensor:
        x = self.dense(hidden_states).squeeze(-1)
        if p_mask is not None:
            if get_parameter_dtype(self) == torch.float16: x = x * (1 - p_mask) - 65500 * p_mask
            else: x = x * (1 - p_mask) - 1e30 * p_mask
        return x
class PoolerEndLogits(nn.Module):
    def __init__(self, config: PretrainedConfig):
        super().__init__()
        self.dense_0 = nn.Linear(config.hidden_size * 2, config.hidden_size)
        self.activation = nn.Tanh()
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dense_1 = nn.Linear(config.hidden_size, 1)
    def forward(self, hidden_states: torch.FloatTensor, start_states: Optional[torch.FloatTensor] = None, start_positions: Optional[torch.LongTensor] = None, p_mask: Optional[torch.FloatTensor] = None) -> torch.FloatTensor:
        assert (start_states is not None or start_positions is not None), "One of start_states, start_positions should be not None"
        if start_positions is not None:
            slen, hsz = hidden_states.shape[-2:]
            start_positions = start_positions[:, None, None].expand(-1, -1, hsz)
            start_states = hidden_states.gather(-2, start_positions)
            start_states = start_states.expand(-1, slen, -1)
        x = self.dense_0(torch.cat([hidden_states, start_states], dim=-1))
        x = self.activation(x)
        x = self.LayerNorm(x)
        x = self.dense_1(x).squeeze(-1)
        if p_mask is not None:
            if get_parameter_dtype(self) == torch.float16: x = x * (1 - p_mask) - 65500 * p_mask
            else: x = x * (1 - p_mask) - 1e30 * p_mask
        return x
class PoolerAnswerClass(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense_0 = nn.Linear(config.hidden_size * 2, config.hidden_size)
        self.activation = nn.Tanh()
        self.dense_1 = nn.Linear(config.hidden_size, 1, bias=False)
    def forward(self, hidden_states: torch.FloatTensor, start_states: Optional[torch.FloatTensor] = None, start_positions: Optional[torch.LongTensor] = None, cls_index: Optional[torch.LongTensor] = None) -> torch.FloatTensor:
        hsz = hidden_states.shape[-1]
        assert (start_states is not None or start_positions is not None), "One of start_states, start_positions should be not None"
        if start_positions is not None:
            start_positions = start_positions[:, None, None].expand(-1, -1, hsz)
            start_states = hidden_states.gather(-2, start_positions).squeeze(-2)
        if cls_index is not None:
            cls_index = cls_index[:, None, None].expand(-1, -1, hsz)
            cls_token_state = hidden_states.gather(-2, cls_index).squeeze(-2)
        else: cls_token_state = hidden_states[:, -1, :]
        x = self.dense_0(torch.cat([start_states, cls_token_state], dim=-1))
        x = self.activation(x)
        x = self.dense_1(x).squeeze(-1)
        return x
@dataclass
class SquadHeadOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    start_top_log_probs: Optional[torch.FloatTensor] = None
    start_top_index: Optional[torch.LongTensor] = None
    end_top_log_probs: Optional[torch.FloatTensor] = None
    end_top_index: Optional[torch.LongTensor] = None
    cls_logits: Optional[torch.FloatTensor] = None
class SQuADHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.start_n_top = config.start_n_top
        self.end_n_top = config.end_n_top
        self.start_logits = PoolerStartLogits(config)
        self.end_logits = PoolerEndLogits(config)
        self.answer_class = PoolerAnswerClass(config)
    def forward(self, hidden_states: torch.FloatTensor, start_positions: Optional[torch.LongTensor] = None, end_positions: Optional[torch.LongTensor] = None, cls_index: Optional[torch.LongTensor] = None, is_impossible: Optional[torch.LongTensor] = None,
    p_mask: Optional[torch.FloatTensor] = None, return_dict: bool = False) -> Union[SquadHeadOutput, Tuple[torch.FloatTensor]]:
        start_logits = self.start_logits(hidden_states, p_mask=p_mask)
        if start_positions is not None and end_positions is not None:
            for x in (start_positions, end_positions, cls_index, is_impossible):
                if x is not None and x.dim() > 1: x.squeeze_(-1)
            end_logits = self.end_logits(hidden_states, start_positions=start_positions, p_mask=p_mask)
            loss_fct = CrossEntropyLoss()
            start_loss = loss_fct(start_logits, start_positions)
            end_loss = loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2
            if cls_index is not None and is_impossible is not None:
                cls_logits = self.answer_class(hidden_states, start_positions=start_positions, cls_index=cls_index)
                loss_fct_cls = nn.BCEWithLogitsLoss()
                cls_loss = loss_fct_cls(cls_logits, is_impossible)
                total_loss += cls_loss * 0.5
            return SquadHeadOutput(loss=total_loss) if return_dict else (total_loss,)
        else:
            bsz, slen, hsz = hidden_states.size()
            start_log_probs = nn.functional.softmax(start_logits, dim=-1)
            start_top_log_probs, start_top_index = torch.topk(start_log_probs, self.start_n_top, dim=-1)
            start_top_index_exp = start_top_index.unsqueeze(-1).expand(-1, -1, hsz)
            start_states = torch.gather(hidden_states, -2, start_top_index_exp)
            start_states = start_states.unsqueeze(1).expand(-1, slen, -1, -1)
            hidden_states_expanded = hidden_states.unsqueeze(2).expand_as(start_states)
            p_mask = p_mask.unsqueeze(-1) if p_mask is not None else None
            end_logits = self.end_logits(hidden_states_expanded, start_states=start_states, p_mask=p_mask)
            end_log_probs = nn.functional.softmax(end_logits, dim=1)
            end_top_log_probs, end_top_index = torch.topk(end_log_probs, self.end_n_top, dim=1)
            end_top_log_probs = end_top_log_probs.view(-1, self.start_n_top * self.end_n_top)
            end_top_index = end_top_index.view(-1, self.start_n_top * self.end_n_top)
            start_states = torch.einsum("blh,bl->bh", hidden_states, start_log_probs)
            cls_logits = self.answer_class(hidden_states, start_states=start_states, cls_index=cls_index)
            if not return_dict: return (start_top_log_probs, start_top_index, end_top_log_probs, end_top_index, cls_logits)
            else: return SquadHeadOutput(start_top_log_probs=start_top_log_probs, start_top_index=start_top_index, end_top_log_probs=end_top_log_probs, end_top_index=end_top_index, cls_logits=cls_logits)
class SequenceSummary(nn.Module):
    def __init__(self, config: PretrainedConfig):
        super().__init__()
        self.summary_type = getattr(config, "summary_type", "last")
        if self.summary_type == "attn": raise NotImplementedError
        self.summary = Identity()
        if hasattr(config, "summary_use_proj") and config.summary_use_proj:
            if hasattr(config, "summary_proj_to_labels") and config.summary_proj_to_labels and config.num_labels > 0: num_classes = config.num_labels
            else: num_classes = config.hidden_size
            self.summary = nn.Linear(config.hidden_size, num_classes)
        activation_string = getattr(config, "summary_activation", None)
        self.activation: Callable = get_activation(activation_string) if activation_string else Identity()
        self.first_dropout = Identity()
        if hasattr(config, "summary_first_dropout") and config.summary_first_dropout > 0: self.first_dropout = nn.Dropout(config.summary_first_dropout)
        self.last_dropout = Identity()
        if hasattr(config, "summary_last_dropout") and config.summary_last_dropout > 0: self.last_dropout = nn.Dropout(config.summary_last_dropout)
    def forward(self, hidden_states: torch.FloatTensor, cls_index: Optional[torch.LongTensor] = None) -> torch.FloatTensor:
        if self.summary_type == "last": output = hidden_states[:, -1]
        elif self.summary_type == "first": output = hidden_states[:, 0]
        elif self.summary_type == "mean": output = hidden_states.mean(dim=1)
        elif self.summary_type == "cls_index":
            if cls_index is None: cls_index = torch.full_like(hidden_states[..., :1, :], hidden_states.shape[-2] - 1, dtype=torch.long)
            else:
                cls_index = cls_index.unsqueeze(-1).unsqueeze(-1)
                cls_index = cls_index.expand((-1,) * (cls_index.dim() - 1) + (hidden_states.size(-1),))
            output = hidden_states.gather(-2, cls_index).squeeze(-2)
        elif self.summary_type == "attn": raise NotImplementedError
        output = self.first_dropout(output)
        output = self.summary(output)
        output = self.activation(output)
        output = self.last_dropout(output)
        return output
def unwrap_model(model: nn.Module, recursive: bool = False) -> nn.Module:
    if is_sapiens_accelerator_available():
        kwargs = {}
        if recursive:
            if not is_sapiens_accelerator_available("0.29.0"): raise RuntimeError("Setting `recursive=True` to `unwrap_model` requires `sapiens_accelerator` v0.29.0. Please upgrade your version of sapiens_accelerator")
            else: kwargs["recursive"] = recursive
        return extract_model_from_parallel(model, **kwargs)
    else:
        if hasattr(model, "module"): return unwrap_model(model.module)
        else: return model
def expand_device_map(device_map, param_names, start_prefix):
    new_device_map = {}
    param_names = [p[len(start_prefix) :] for p in param_names if p.startswith(start_prefix)]
    for module, device in device_map.items(): new_device_map.update({p: device for p in param_names if p == module or p.startswith(f"{module}.") or module == ""})
    return new_device_map
def get_disk_only_shard_files(device_map, sharded_metadata, start_prefix):
    weight_map = {p[len(start_prefix) :]: v for p, v in sharded_metadata["weight_map"].items() if p.startswith(start_prefix)}
    files_content = collections.defaultdict(list)
    for weight_name, filename in weight_map.items():
        while len(weight_name) > 0 and weight_name not in device_map: weight_name = ".".join(weight_name.split(".")[:-1])
        files_content[filename].append(device_map[weight_name])
    return [fname for fname, devices in files_content.items() if set(devices) == {"disk"}]
class SapiensPreTrainedModel(PreTrainedModel): pass
ALL_ATTENTION_FUNCTIONS: Dict[str, Dict[str, Callable]] = {}
ALL_ATTENTION_FUNCTIONS.update({"flash_attention_2": flash_attention_forward, "flex_attention": flex_attention_forward, "sdpa": sdpa_attention_forward})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
