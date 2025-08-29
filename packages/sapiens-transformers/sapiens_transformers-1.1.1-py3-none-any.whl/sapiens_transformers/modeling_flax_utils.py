"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (FLAX_WEIGHTS_INDEX_NAME, FLAX_WEIGHTS_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_NAME, WEIGHTS_INDEX_NAME, WEIGHTS_NAME, PushToHubMixin, add_code_sample_docstrings,
add_start_docstrings_to_model_forward, cached_file, copy_func, download_url, has_file, is_offline_mode, is_remote_url, logging, replace_return_docstrings)
from .modeling_flax_pytorch_utils import load_pytorch_checkpoint_in_flax_state_dict
from .utils.hub import convert_file_size_to_int, get_checkpoint_shard_files
from .generation import FlaxGenerationMixin, GenerationConfig
from flax.traverse_util import flatten_dict, unflatten_dict
from typing import Any, Dict, Optional, Set, Tuple, Union
from .utils.import_utils import is_safetensors_available
from flax.core.frozen_dict import FrozenDict, unfreeze
from .dynamic_module_utils import custom_object_save
from flax.serialization import from_bytes, to_bytes
from .configuration_utils import PretrainedConfig
from pickle import UnpicklingError
from jax.random import PRNGKey
from functools import partial
import msgpack.exceptions
import jax.numpy as jnp
import flax.linen as nn
import warnings
import json
import jax
import re
import gc
import os
if is_safetensors_available():
    from safetensors import safe_open
    from safetensors.flax import load_file as safe_load_file
    from safetensors.flax import save_file as safe_save_file
logger = logging.get_logger(__name__)
def quick_gelu(x): return x * jax.nn.sigmoid(1.702 * x)
ACT2FN = {"gelu": partial(nn.gelu, approximate=False), "relu": nn.relu, "silu": nn.swish, "swish": nn.swish, "gelu_new": partial(nn.gelu, approximate=True), "quick_gelu": quick_gelu, "gelu_pytorch_tanh": partial(nn.gelu, approximate=True)}
def dtype_byte_size(dtype):
    if dtype is bool: return 1 / 8
    bit_search = re.search(r"[^\d](\d+)$", dtype.name)
    if bit_search is None: raise ValueError(f"`dtype` is not a valid dtype: {dtype}.")
    bit_size = int(bit_search.groups()[0])
    return bit_size // 8
def flax_shard_checkpoint(params, max_shard_size="10GB"):
    max_shard_size = convert_file_size_to_int(max_shard_size)
    sharded_state_dicts = []
    current_block = {}
    current_block_size = 0
    total_size = 0
    weights = flatten_dict(params, sep="/")
    for item in weights:
        weight_size = weights[item].size * dtype_byte_size(weights[item].dtype)
        if current_block_size + weight_size > max_shard_size:
            sharded_state_dicts.append(current_block)
            current_block = {}
            current_block_size = 0
        current_block[item] = weights[item]
        current_block_size += weight_size
        total_size += weight_size
    sharded_state_dicts.append(current_block)
    if len(sharded_state_dicts) == 1: return {FLAX_WEIGHTS_NAME: sharded_state_dicts[0]}, None
    weight_map = {}
    shards = {}
    for idx, shard in enumerate(sharded_state_dicts):
        shard_file = FLAX_WEIGHTS_NAME.replace(".msgpack", f"-{idx+1:05d}-of-{len(sharded_state_dicts):05d}.msgpack")
        shards[shard_file] = shard
        for weight_name in shard.keys(): weight_map[weight_name] = shard_file
    metadata = {"total_size": total_size}
    index = {"metadata": metadata, "weight_map": weight_map}
    return shards, index
class FlaxPreTrainedModel(PushToHubMixin, FlaxGenerationMixin):
    config_class = None
    base_model_prefix = ""
    main_input_name = "input_ids"
    _auto_class = None
    _missing_keys = set()
    def __init__(self, config: PretrainedConfig, module: nn.Module, input_shape: Tuple = (1, 1), seed: int = 0, dtype: jnp.dtype = jnp.float32, _do_init: bool = True):
        if config is None: raise ValueError("config cannot be None")
        if module is None: raise ValueError("module cannot be None")
        self._config = config
        self._module = module
        self.key = PRNGKey(seed)
        self.dtype = dtype
        self.input_shape = input_shape
        self.generation_config = GenerationConfig.from_model_config(config) if self.can_generate() else None
        self._is_initialized = _do_init
        if _do_init:
            random_params = self.init_weights(self.key, input_shape)
            params_shape_tree = jax.eval_shape(lambda params: params, random_params)
        else:
            init_fn = partial(self.init_weights, input_shape=input_shape)
            params_shape_tree = jax.eval_shape(init_fn, self.key)
            logger.info(f"Model weights are not initialized as `_do_init` is set to `False`. Make sure to call `{self.__class__.__name__}.init_weights` manually to initialize the weights.")
        self._params_shape_tree = params_shape_tree
        self._required_params = set(flatten_dict(unfreeze(params_shape_tree)).keys())
        if _do_init: self.params = random_params
    def init_weights(self, rng: jax.random.PRNGKey, input_shape: Tuple, params: FrozenDict = None) -> Dict: raise NotImplementedError(f"init method has to be implemented for {self}")
    def enable_gradient_checkpointing(self): raise NotImplementedError(f"gradient checkpointing method has to be implemented for {self}")
    @classmethod
    def _from_config(cls, config, **kwargs): return cls(config, **kwargs)
    @property
    def framework(self) -> str: return "flax"
    @property
    def config(self) -> PretrainedConfig: return self._config
    @property
    def module(self) -> nn.Module: return self._module
    @property
    def params(self) -> Union[Dict, FrozenDict]:
        if not self._is_initialized: raise ValueError("`params` cannot be accessed from model when the model is created with `_do_init=False`. You must call `init_weights` manually and store the params outside of the model and pass it explicitly where needed.")
        return self._params
    @property
    def required_params(self) -> Set: return self._required_params
    @property
    def params_shape_tree(self) -> Dict: return self._params_shape_tree
    @params.setter
    def params(self, params: Union[Dict, FrozenDict]):
        if not self._is_initialized: raise ValueError("`params` cannot be set from model when the model is created with `_do_init=False`. You store the params outside of the model.")
        if isinstance(params, FrozenDict): params = unfreeze(params)
        param_keys = set(flatten_dict(params).keys())
        if len(self.required_params - param_keys) > 0: raise ValueError(f"Some parameters are missing. Make sure that `params` include the following parameters {self.required_params - param_keys}")
        self._params = params
    def _cast_floating_to(self, params: Union[Dict, FrozenDict], dtype: jnp.dtype, mask: Any = None) -> Any:
        def conditional_cast(param):
            if isinstance(param, jnp.ndarray) and jnp.issubdtype(param.dtype, jnp.floating): param = param.astype(dtype)
            return param
        if mask is None: return jax.tree_util.tree_map(conditional_cast, params)
        flat_params = flatten_dict(params)
        flat_mask, _ = jax.tree_util.tree_flatten(mask)
        for masked, key in zip(flat_mask, sorted(flat_params.keys())):
            if masked: flat_params[key] = conditional_cast(flat_params[key])
        return unflatten_dict(flat_params)
    def to_bf16(self, params: Union[Dict, FrozenDict], mask: Any = None): return self._cast_floating_to(params, jnp.bfloat16, mask)
    def to_fp32(self, params: Union[Dict, FrozenDict], mask: Any = None): return self._cast_floating_to(params, jnp.float32, mask)
    def to_fp16(self, params: Union[Dict, FrozenDict], mask: Any = None): return self._cast_floating_to(params, jnp.float16, mask)
    @classmethod
    def load_flax_weights(cls, resolved_archive_file):
        try:
            if resolved_archive_file.endswith(".safetensors"):
                state = safe_load_file(resolved_archive_file)
                state = unflatten_dict(state, sep=".")
            else:
                with open(resolved_archive_file, "rb") as state_f: state = from_bytes(cls, state_f.read())
        except (UnpicklingError, msgpack.exceptions.ExtraData) as e:
            try:
                with open(resolved_archive_file) as f:
                    if f.read().startswith("version"): raise OSError("You seem to have cloned a repository without having git-lfs installed. Please install git-lfs and run `git lfs install` followed by `git lfs pull` in the folder you cloned.")
                    else: raise ValueError from e
            except (UnicodeDecodeError, ValueError): raise EnvironmentError(f"Unable to convert {resolved_archive_file} to Flax deserializable object. ")
        return state
    @classmethod
    def load_flax_sharded_weights(cls, shard_files):
        state_sharded_dict = {}
        for shard_file in shard_files:
            try:
                with open(shard_file, "rb") as state_f: state = from_bytes(cls, state_f.read())
            except (UnpicklingError, msgpack.exceptions.ExtraData) as e:
                with open(shard_file) as f:
                    if f.read().startswith("version"): raise OSError("You seem to have cloned a repository without having git-lfs installed. Please install git-lfs and run `git lfs install` followed by `git lfs pull` in the folder you cloned.")
                    else: raise ValueError from e
            except (UnicodeDecodeError, ValueError): raise EnvironmentError(f"Unable to convert {shard_file} to Flax deserializable object. ")
            state = flatten_dict(state, sep="/")
            state_sharded_dict.update(state)
            del state
            gc.collect()
        return unflatten_dict(state_sharded_dict, sep="/")
    @classmethod
    def can_generate(cls) -> bool:
        if "GenerationMixin" in str(cls.prepare_inputs_for_generation) and "GenerationMixin" in str(cls.generate): return False
        return True
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], dtype: jnp.dtype = jnp.float32, *model_args, config: Optional[Union[PretrainedConfig, str, os.PathLike]] = None, cache_dir: Optional[Union[str, os.PathLike]] = None,
    ignore_mismatched_sizes: bool = False, force_download: bool = False, local_files_only: bool = False, token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs):
        from_pt = kwargs.pop("from_pt", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        _do_init = kwargs.pop("_do_init", True)
        subfolder = kwargs.pop("subfolder", "")
        commit_hash = kwargs.pop("_commit_hash", None)
        _ = kwargs.pop("adapter_kwargs", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if trust_remote_code is True: logger.warning("The argument `trust_remote_code` is to be used with Auto classes. It has no effect here and is ignored.")
        user_agent = {"file_type": "model", "framework": "flax", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        if not isinstance(config, PretrainedConfig):
            config_path = config if config is not None else pretrained_model_name_or_path
            config, model_kwargs = cls.config_class.from_pretrained(config_path, cache_dir=cache_dir, return_unused_kwargs=True, force_download=force_download, resume_download=resume_download,
            proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, _from_auto=from_auto_class, _from_pipeline=from_pipeline, _commit_hash=commit_hash, **kwargs)
        else: model_kwargs = kwargs.copy()
        if commit_hash is None: commit_hash = getattr(config, "_commit_hash", None)
        model_kwargs["dtype"] = dtype
        is_sharded = False
        if pretrained_model_name_or_path is not None:
            pretrained_model_name_or_path = str(pretrained_model_name_or_path)
            is_local = os.path.isdir(pretrained_model_name_or_path)
            if os.path.isdir(pretrained_model_name_or_path):
                if os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)
                elif os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_INDEX_NAME)):
                    archive_file = os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_INDEX_NAME)
                    is_sharded = True
                elif is_safetensors_available() and os.path.isfile(os.path.join(pretrained_model_name_or_path, SAFE_WEIGHTS_NAME)): archive_file = os.path.join(pretrained_model_name_or_path, SAFE_WEIGHTS_NAME)
                elif from_pt and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, WEIGHTS_NAME)): archive_file = os.path.join(pretrained_model_name_or_path, subfolder, WEIGHTS_NAME)
                elif from_pt and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, WEIGHTS_INDEX_NAME)):
                    archive_file = os.path.join(pretrained_model_name_or_path, subfolder, WEIGHTS_INDEX_NAME)
                    is_sharded = True
                elif is_safetensors_available() and os.path.isfile(os.path.join(pretrained_model_name_or_path, SAFE_WEIGHTS_INDEX_NAME)):
                    archive_file = os.path.join(pretrained_model_name_or_path, SAFE_WEIGHTS_INDEX_NAME)
                    is_sharded = True
                    raise NotImplementedError("Support for sharded checkpoints using safetensors is coming soon!")
                elif os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, WEIGHTS_NAME)): raise EnvironmentError(f"Error no file named {FLAX_WEIGHTS_NAME} found in directory {pretrained_model_name_or_path} but there is a file for PyTorch weights. Use `from_pt=True` to load this model from those weights.")
                else: raise EnvironmentError(f"Error no file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME} found in directory {pretrained_model_name_or_path}.")
            elif os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path)):
                archive_file = pretrained_model_name_or_path
                is_local = True
            elif is_remote_url(pretrained_model_name_or_path):
                filename = pretrained_model_name_or_path
                resolved_archive_file = download_url(pretrained_model_name_or_path)
            else:
                if from_pt: filename = WEIGHTS_NAME
                else: filename = FLAX_WEIGHTS_NAME
                try:
                    cached_file_kwargs = {"cache_dir": cache_dir, "force_download": force_download, "proxies": proxies, "resume_download": resume_download, "local_files_only": local_files_only, "token": token, "user_agent": user_agent, "revision": revision, "subfolder": subfolder, "_raise_exceptions_for_gated_repo": False, "_raise_exceptions_for_missing_entries": False, "_commit_hash": commit_hash}
                    resolved_archive_file = cached_file(pretrained_model_name_or_path, filename, **cached_file_kwargs)
                    if resolved_archive_file is None and filename == FLAX_WEIGHTS_NAME:
                        resolved_archive_file = cached_file(pretrained_model_name_or_path, FLAX_WEIGHTS_INDEX_NAME, **cached_file_kwargs)
                        if resolved_archive_file is not None: is_sharded = True
                    if resolved_archive_file is None and from_pt:
                        resolved_archive_file = cached_file(pretrained_model_name_or_path, WEIGHTS_INDEX_NAME, **cached_file_kwargs)
                        if resolved_archive_file is not None: is_sharded = True
                    if resolved_archive_file is None:
                        filename = SAFE_WEIGHTS_NAME
                        resolved_archive_file = cached_file(pretrained_model_name_or_path, SAFE_WEIGHTS_NAME, **cached_file_kwargs)
                    if resolved_archive_file is None:
                        has_file_kwargs = {"revision": revision, "proxies": proxies, "token": token, "cache_dir": cache_dir, "local_files_only": local_files_only}
                        if has_file(pretrained_model_name_or_path, SAFE_WEIGHTS_INDEX_NAME, **has_file_kwargs):
                            is_sharded = True
                            raise NotImplementedError("Support for sharded checkpoints using safetensors is coming soon!")
                        elif has_file(pretrained_model_name_or_path, WEIGHTS_NAME, **has_file_kwargs): raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {FLAX_WEIGHTS_NAME} but there is a file for PyTorch weights. Use `from_pt=True` to load this model from those weights.")
                        elif has_file(pretrained_model_name_or_path, WEIGHTS_INDEX_NAME, **has_file_kwargs): raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {FLAX_WEIGHTS_INDEX_NAME} but there is a sharded file for PyTorch weights. Use `from_pt=True` to load this model from those weights.")
                        else: raise EnvironmentError(f"{pretrained_model_name_or_path} does not appear to have a file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME}.")
                except EnvironmentError: raise
                except Exception: raise EnvironmentError(f"Can't load the model for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME}.")
            if is_local:
                logger.info(f"loading weights file {archive_file}")
                resolved_archive_file = archive_file
                filename = resolved_archive_file.split(os.path.sep)[-1]
            else: logger.info(f"loading weights file {filename} from cache at {resolved_archive_file}")
        else: resolved_archive_file = None
        if is_sharded: resolved_archive_file, _ = get_checkpoint_shard_files(pretrained_model_name_or_path, resolved_archive_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies, resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder, _commit_hash=commit_hash)
        safetensors_from_pt = False
        if filename == SAFE_WEIGHTS_NAME:
            with safe_open(resolved_archive_file, framework="flax") as f: safetensors_metadata = f.metadata()
            if safetensors_metadata is None or safetensors_metadata.get("format") not in ["pt", "tf", "flax"]: raise OSError(f"The safetensors archive passed at {resolved_archive_file} does not contain the valid metadata. Make sure you save your model with the `save_pretrained` method.")
            safetensors_from_pt = safetensors_metadata.get("format") == "pt"
        model = cls(config, *model_args, _do_init=_do_init, **model_kwargs)
        if from_pt or safetensors_from_pt: state = load_pytorch_checkpoint_in_flax_state_dict(model, resolved_archive_file, is_sharded)
        else:
            if is_sharded: state = cls.load_flax_sharded_weights(resolved_archive_file)
            else: state = cls.load_flax_weights(resolved_archive_file)
            if _do_init: state = jax.tree_util.tree_map(jnp.array, state)
            else: state = jax.tree_util.tree_map(lambda x: jax.device_put(x, jax.local_devices(backend="cpu")[0]), state)
        if "batch_stats" in state:
            if (cls.base_model_prefix not in dict(model.params_shape_tree["params"]) and cls.base_model_prefix in state["params"]):
                state["params"] = state["params"][cls.base_model_prefix]
                state["batch_stats"] = state["batch_stats"][cls.base_model_prefix]
            if (cls.base_model_prefix in dict(model.params_shape_tree["params"]) and cls.base_model_prefix not in state["params"]): state = {"params": {cls.base_model_prefix: state["params"]}, "batch_stats": {cls.base_model_prefix: state["batch_stats"]}}
        else:
            if cls.base_model_prefix not in dict(model.params_shape_tree) and cls.base_model_prefix in state: state = state[cls.base_model_prefix]
            if cls.base_model_prefix in dict(model.params_shape_tree) and cls.base_model_prefix not in state: state = {cls.base_model_prefix: state}
        state = flatten_dict(state)
        random_state = flatten_dict(unfreeze(model.params if _do_init else model.params_shape_tree))
        missing_keys = model.required_params - set(state.keys())
        unexpected_keys = set(state.keys()) - model.required_params
        for unexpected_key in unexpected_keys.copy():
            if "num_batches_tracked" in unexpected_key[-1]: unexpected_keys.remove(unexpected_key)
        if missing_keys and not _do_init:
            logger.warning(f"The checkpoint {pretrained_model_name_or_path} is missing required keys: {missing_keys}. Make sure to call model.init_weights to initialize the missing weights.")
            cls._missing_keys = missing_keys
        mismatched_keys = []
        for key in state.keys():
            if key in random_state and state[key].shape != random_state[key].shape:
                if ignore_mismatched_sizes:
                    mismatched_keys.append((key, state[key].shape, random_state[key].shape))
                    state[key] = random_state[key]
                else: raise ValueError(f"Trying to load the pretrained weight for {key} failed: checkpoint has shape {state[key].shape} which is incompatible with the model shape {random_state[key].shape}. Using `ignore_mismatched_sizes=True` if you really want to load this checkpoint inside this model.")
        if missing_keys and _do_init:
            for missing_key in missing_keys: state[missing_key] = random_state[missing_key]
        for unexpected_key in unexpected_keys: del state[unexpected_key]
        if len(unexpected_keys) > 0: logger.warning(f"Some weights of the model checkpoint at {pretrained_model_name_or_path} were not used when initializing {model.__class__.__name__}: {unexpected_keys}\n- This IS expected if you are initializing {model.__class__.__name__} from the checkpoint of a model trained on another task or with another architecture (e.g. initializing a BertForSequenceClassification model from a BertForPreTraining model).\n- This IS NOT expected if you are initializing {model.__class__.__name__} from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).")
        if len(missing_keys) > 0: logger.warning(f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at {pretrained_model_name_or_path} and are newly initialized: {missing_keys}\nYou should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.")
        elif len(mismatched_keys) == 0: logger.info(f"All the weights of {model.__class__.__name__} were initialized from the model checkpoint at {pretrained_model_name_or_path}.\nIf your task is similar to the task the model of the checkpoint was trained on, you can already use {model.__class__.__name__} for predictions without further training.")
        if len(mismatched_keys) > 0:
            mismatched_warning = "\n".join([f"- {key}: found shape {shape1} in the checkpoint and {shape2} in the model instantiated" for key, shape1, shape2 in mismatched_keys])
            logger.warning(f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at {pretrained_model_name_or_path} and are newly initialized because the shapes did not match:\n{mismatched_warning}\nYou should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.")
        param_dtypes = jax.tree_util.tree_map(lambda x: x.dtype, state)
        fp16_params = [k for k in param_dtypes if param_dtypes[k] == jnp.float16]
        bf16_params = [k for k in param_dtypes if param_dtypes[k] == jnp.bfloat16]
        if len(fp16_params) > 0: logger.warning(f"Some of the weights of {model.__class__.__name__} were initialized in float16 precision from the model checkpoint at {pretrained_model_name_or_path}:\n{fp16_params}\nYou should probably UPCAST the model weights to float32 if this was not intended. See [`~FlaxPreTrainedModel.to_fp32`] for further information on how to do this.")
        if len(bf16_params) > 0: logger.warning(f"Some of the weights of {model.__class__.__name__} were initialized in bfloat16 precision from the model checkpoint at {pretrained_model_name_or_path}:\n{bf16_params}\nYou should probably UPCAST the model weights to float32 if this was not intended. See [`~FlaxPreTrainedModel.to_fp32`] for further information on how to do this.")
        if model.can_generate():
            try: model.generation_config = GenerationConfig.from_pretrained(pretrained_model_name_or_path, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, _from_auto=from_auto_class, _from_pipeline=from_pipeline, **kwargs)
            except OSError:
                logger.info("Generation config file not found, using a generation config created from the model config.")
                pass
        if _do_init:
            model.params = unflatten_dict(state)
            return model
        else: return model, unflatten_dict(state)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], params=None, push_to_hub=False, max_shard_size="10GB", token: Optional[Union[str, bool]] = None, safe_serialization: bool = False, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None: kwargs["token"] = token
        if os.path.isfile(save_directory):
            logger.error(f"Provided path ({save_directory}) should be a directory, not a file")
            return
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        save_directory = os.path.abspath(save_directory)
        self.config.architectures = [self.__class__.__name__[4:]]
        if self._auto_class is not None: custom_object_save(self, save_directory, config=self.config)
        self.config.save_pretrained(save_directory)
        if self.can_generate(): self.generation_config.save_pretrained(save_directory)
        weights_name = SAFE_WEIGHTS_NAME if safe_serialization else FLAX_WEIGHTS_NAME
        output_model_file = os.path.join(save_directory, weights_name)
        shards, index = flax_shard_checkpoint(params if params is not None else self.params, max_shard_size)
        for filename in os.listdir(save_directory):
            full_filename = os.path.join(save_directory, filename)
            weights_no_suffix = weights_name.replace(".bin", "").replace(".safetensors", "")
            if (filename.startswith(weights_no_suffix) and os.path.isfile(full_filename) and filename not in shards.keys()): os.remove(full_filename)
        if index is None:
            if safe_serialization:
                params = params if params is not None else self.params
                flat_dict = flatten_dict(params, sep=".")
                safe_save_file(flat_dict, output_model_file, metadata={"format": "flax"})
            else:
                with open(output_model_file, "wb") as f:
                    params = params if params is not None else self.params
                    model_bytes = to_bytes(params)
                    f.write(model_bytes)
        else:
            save_index_file = os.path.join(save_directory, FLAX_WEIGHTS_INDEX_NAME)
            with open(save_index_file, "w", encoding="utf-8") as f:
                content = json.dumps(index, indent=2, sort_keys=True) + "\n"
                f.write(content)
            logger.info(f"The model is bigger than the maximum size per checkpoint ({max_shard_size}) and is going to be split in {len(shards)} checkpoint shards. You can find where each parameters has been saved in the index located at {save_index_file}.")
            for shard_file, shard in shards.items():
                with open(os.path.join(save_directory, shard_file), mode="wb") as f:
                    params = unflatten_dict(shard, sep="/")
                    shard_bytes = to_bytes(params)
                    f.write(shard_bytes)
        logger.info(f"Model weights saved in {output_model_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=token)
    @classmethod
    def register_for_auto_class(cls, auto_class="FlaxAutoModel"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
FlaxPreTrainedModel.push_to_hub = copy_func(FlaxPreTrainedModel.push_to_hub)
if FlaxPreTrainedModel.push_to_hub.__doc__ is not None: FlaxPreTrainedModel.push_to_hub.__doc__ = FlaxPreTrainedModel.push_to_hub.__doc__.format(object="model", object_class="FlaxAutoModel", object_files="model checkpoint")
def overwrite_call_docstring(model_class, docstring):
    model_class.__call__ = copy_func(model_class.__call__)
    model_class.__call__.__doc__ = None
    model_class.__call__ = add_start_docstrings_to_model_forward(docstring)(model_class.__call__)
def append_call_sample_docstring(model_class, checkpoint, output_type, config_class, mask=None, revision=None, real_checkpoint=None):
    model_class.__call__ = copy_func(model_class.__call__)
    model_class.__call__ = add_code_sample_docstrings(checkpoint=checkpoint, output_type=output_type, config_class=config_class, model_cls=model_class.__name__, revision=revision, real_checkpoint=real_checkpoint)(model_class.__call__)
def append_replace_return_docstrings(model_class, output_type, config_class):
    model_class.__call__ = copy_func(model_class.__call__)
    model_class.__call__ = replace_return_docstrings(output_type=output_type, config_class=config_class)(model_class.__call__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
