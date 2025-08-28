'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import enum
import fnmatch
import importlib
import inspect
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin
import numpy as np
import PIL.Image
import requests
import torch
from huggingface_hub import ModelCard, create_repo, hf_hub_download, model_info, snapshot_download
from huggingface_hub.utils import OfflineModeIsEnabled, validate_hf_hub_args
from packaging import version
from requests.exceptions import HTTPError
from tqdm.auto import tqdm
from .. import __version__
from ..configuration_utils import ConfigMixin
from ..models import AutoencoderKL
from ..models.attention_processor import FusedAttnProcessor2_0
from ..models.modeling_utils import _LOW_CPU_MEM_USAGE_DEFAULT, ModelMixin
from ..quantizers.sapiens_machine.utils import _check_sapiens_status
from ..schedulers.scheduling_utils import SCHEDULER_CONFIG_NAME
from ..utils import (CONFIG_NAME, DEPRECATED_REVISION_ARGS, BaseOutput, PushToHubMixin, is_sapiens_accelerator_available, is_sapiens_accelerator_version,
is_torch_npu_available, is_torch_version, is_sapiens_transformers_version, logging, numpy_to_pil)
from ..utils.hub_utils import _check_legacy_sharding_variant_format, load_or_create_model_card, populate_model_card
from ..utils.torch_utils import is_compiled_module
if is_torch_npu_available(): import torch_npu
from .pipeline_loading_utils import (ALL_IMPORTABLE_CLASSES, CONNECTED_PIPES_KEYS, CUSTOM_PIPELINE_FILE_NAME, LOADABLE_CLASSES, _fetch_class_library_tuple, _get_custom_components_and_folders,
_get_custom_pipeline_class, _get_final_device_map, _get_ignore_patterns, _get_pipeline_class, _identify_model_variants, _maybe_raise_warning_for_inpainting, _resolve_custom_pipeline_and_cls,
_unwrap_model, _update_init_kwargs_with_connected_pipeline, load_sub_model, maybe_raise_or_warn, variant_compatible_siblings, warn_deprecated_model_variant)
if is_sapiens_accelerator_available(): import sapiens_accelerator
LIBRARIES = []
for library in LOADABLE_CLASSES: LIBRARIES.append(library)
SUPPORTED_DEVICE_MAP = ['balanced']
@dataclass
class ImagePipelineOutput(BaseOutput):
    """Args:"""
    images: Union[List[PIL.Image.Image], np.ndarray]
@dataclass
class AudioPipelineOutput(BaseOutput):
    """Args:"""
    audios: np.ndarray
class DiffusionPipeline(ConfigMixin, PushToHubMixin):
    config_name = 'model_index.json'
    model_cpu_offload_seq = None
    hf_device_map = None
    _optional_components = []
    _exclude_from_cpu_offload = []
    _load_connected_pipes = False
    _is_onnx = False
    def register_modules(self, **kwargs):
        for name, module in kwargs.items():
            if module is None or (isinstance(module, (tuple, list)) and module[0] is None): register_dict = {name: (None, None)}
            else:
                library, class_name = _fetch_class_library_tuple(module)
                register_dict = {name: (library, class_name)}
            self.register_to_config(**register_dict)
            setattr(self, name, module)
    def __setattr__(self, name: str, value: Any):
        if name in self.__dict__ and hasattr(self.config, name):
            if isinstance(getattr(self.config, name), (tuple, list)):
                if value is not None and self.config[name][0] is not None: class_library_tuple = _fetch_class_library_tuple(value)
                else: class_library_tuple = (None, None)
                self.register_to_config(**{name: class_library_tuple})
            else: self.register_to_config(**{name: value})
        super().__setattr__(name, value)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], safe_serialization: bool=True, variant: Optional[str]=None,
    max_shard_size: Optional[Union[int, str]]=None, push_to_hub: bool=False, **kwargs):
        model_index_dict = dict(self.config)
        model_index_dict.pop('_class_name', None)
        model_index_dict.pop('_diffusers_version', None)
        model_index_dict.pop('_module', None)
        model_index_dict.pop('_name_or_path', None)
        if push_to_hub:
            commit_message = kwargs.pop('commit_message', None)
            private = kwargs.pop('private', None)
            create_pr = kwargs.pop('create_pr', False)
            token = kwargs.pop('token', None)
            repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
            repo_id = create_repo(repo_id, exist_ok=True, private=private, token=token).repo_id
        expected_modules, optional_kwargs = self._get_signature_keys(self)
        def is_saveable_module(name, value):
            if name not in expected_modules: return False
            if name in self._optional_components and value[0] is None: return False
            return True
        model_index_dict = {k: v for k, v in model_index_dict.items() if is_saveable_module(k, v)}
        for pipeline_component_name in model_index_dict.keys():
            sub_model = getattr(self, pipeline_component_name)
            model_cls = sub_model.__class__
            if is_compiled_module(sub_model):
                sub_model = _unwrap_model(sub_model)
                model_cls = sub_model.__class__
            save_method_name = None
            for library_name, library_classes in LOADABLE_CLASSES.items():
                if library_name in sys.modules: library = importlib.import_module(library_name)
                for base_class, save_load_methods in library_classes.items():
                    class_candidate = getattr(library, base_class, None)
                    if class_candidate is not None and issubclass(model_cls, class_candidate):
                        save_method_name = save_load_methods[0]
                        break
                if save_method_name is not None: break
            if save_method_name is None:
                self.register_to_config(**{pipeline_component_name: (None, None)})
                continue
            save_method = getattr(sub_model, save_method_name)
            save_method_signature = inspect.signature(save_method)
            save_method_accept_safe = 'safe_serialization' in save_method_signature.parameters
            save_method_accept_variant = 'variant' in save_method_signature.parameters
            save_method_accept_max_shard_size = 'max_shard_size' in save_method_signature.parameters
            save_kwargs = {}
            if save_method_accept_safe: save_kwargs['safe_serialization'] = safe_serialization
            if save_method_accept_variant: save_kwargs['variant'] = variant
            if save_method_accept_max_shard_size and max_shard_size is not None: save_kwargs['max_shard_size'] = max_shard_size
            save_method(os.path.join(save_directory, pipeline_component_name), **save_kwargs)
        self.save_config(save_directory)
        if push_to_hub:
            model_card = load_or_create_model_card(repo_id, token=token, is_pipeline=True)
            model_card = populate_model_card(model_card)
            model_card.save(os.path.join(save_directory, 'README.md'))
            self._upload_folder(save_directory, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
    def to(self, *args, **kwargs):
        """Returns:"""
        dtype = kwargs.pop('dtype', None)
        device = kwargs.pop('device', None)
        silence_dtype_warnings = kwargs.pop('silence_dtype_warnings', False)
        dtype_arg = None
        device_arg = None
        if len(args) == 1:
            if isinstance(args[0], torch.dtype): dtype_arg = args[0]
            else: device_arg = torch.device(args[0]) if args[0] is not None else None
        elif len(args) == 2:
            if isinstance(args[0], torch.dtype): raise ValueError('When passing two arguments, make sure the first corresponds to `device` and the second to `dtype`.')
            device_arg = torch.device(args[0]) if args[0] is not None else None
            dtype_arg = args[1]
        elif len(args) > 2: raise ValueError('Please make sure to pass at most two arguments (`device` and `dtype`) `.to(...)`')
        if dtype is not None and dtype_arg is not None: raise ValueError('You have passed `dtype` both as an argument and as a keyword argument. Please only pass one of the two.')
        dtype = dtype or dtype_arg
        if device is not None and device_arg is not None: raise ValueError('You have passed `device` both as an argument and as a keyword argument. Please only pass one of the two.')
        device = device or device_arg
        pipeline_has_sapiens = any((any(_check_sapiens_status(module)) for _, module in self.components.items()))
        def module_is_sequentially_offloaded(module):
            if not is_sapiens_accelerator_available() or is_sapiens_accelerator_version('<', '0.14.0'): return False
            return hasattr(module, '_hf_hook') and (isinstance(module._hf_hook, sapiens_accelerator.hooks.AlignDevicesHook) or (hasattr(module._hf_hook,
            'hooks') and isinstance(module._hf_hook.hooks[0], sapiens_accelerator.hooks.AlignDevicesHook)))
        def module_is_offloaded(module):
            if not is_sapiens_accelerator_available() or is_sapiens_accelerator_version('<', '0.17.0.dev0'): return False
            return hasattr(module, '_hf_hook') and isinstance(module._hf_hook, sapiens_accelerator.hooks.CpuOffload)
        pipeline_is_sequentially_offloaded = any((module_is_sequentially_offloaded(module) for _, module in self.components.items()))
        if device and torch.device(device).type == 'cuda':
            if pipeline_is_sequentially_offloaded and (not pipeline_has_sapiens): raise ValueError("It seems like you have activated sequential model offloading by calling `enable_sequential_cpu_offload`, but are now attempting to move the pipeline to GPU. This is not compatible with offloading. Please, move your pipeline `.to('cpu')` or consider removing the move altogether if you use sequential offloading.")
            elif pipeline_has_sapiens and is_sapiens_accelerator_version('<', '1.1.0.dev0'): raise ValueError("You are trying to call `.to('cuda')` on a pipeline that has models quantized with `sapiens_machine`. Your current `sapiens_accelerator` installation does not support it. Please upgrade the installation.")
        is_pipeline_device_mapped = self.hf_device_map is not None and len(self.hf_device_map) > 1
        if is_pipeline_device_mapped: raise ValueError("It seems like you have activated a device mapping strategy on the pipeline which doesn't allow explicit device placement using `to()`. You can call `reset_device_map()` first and then call `to()`.")
        pipeline_is_offloaded = any((module_is_offloaded(module) for _, module in self.components.items()))
        module_names, _ = self._get_signature_keys(self)
        modules = [getattr(self, n, None) for n in module_names]
        modules = [m for m in modules if isinstance(m, torch.nn.Module)]
        is_offloaded = pipeline_is_offloaded or pipeline_is_sequentially_offloaded
        for module in modules:
            _, is_loaded_in_4bit_sapiens, is_loaded_in_8bit_sapiens = _check_sapiens_status(module)
            if is_loaded_in_4bit_sapiens and device is not None and is_sapiens_transformers_version('>', '4.44.0'): module.to(device=device)
            elif not is_loaded_in_4bit_sapiens and (not is_loaded_in_8bit_sapiens): module.to(device, dtype)
        return self
    @property
    def device(self) -> torch.device:
        """Returns:"""
        module_names, _ = self._get_signature_keys(self)
        modules = [getattr(self, n, None) for n in module_names]
        modules = [m for m in modules if isinstance(m, torch.nn.Module)]
        for module in modules: return module.device
        return torch.device('cpu')
    @property
    def dtype(self) -> torch.dtype:
        """Returns:"""
        module_names, _ = self._get_signature_keys(self)
        modules = [getattr(self, n, None) for n in module_names]
        modules = [m for m in modules if isinstance(m, torch.nn.Module)]
        for module in modules: return module.dtype
        return torch.float32
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], **kwargs):
        """Examples:"""
        def getCurrentPath():
            from pathlib import Path
            from re import search
            return str(search(r"(.*?sapiens_transformers.*?diffusers)", str(Path(__file__).resolve())).group(1)).strip()
        def addSysPath():
            from sys import path
            from pathlib import Path
            path.insert(0, str(Path(getCurrentPath())))
        def removeSysPath():
            from sys import path
            transformers_diffusers_path = Path(getCurrentPath())
            if str(transformers_diffusers_path) in path: path.remove(str(transformers_diffusers_path))
        addSysPath()
        kwargs_copied = kwargs.copy()
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        from_flax = kwargs.pop('from_flax', False)
        torch_dtype = kwargs.pop('torch_dtype', None)
        custom_pipeline = kwargs.pop('custom_pipeline', None)
        custom_revision = kwargs.pop('custom_revision', None)
        provider = kwargs.pop('provider', None)
        sess_options = kwargs.pop('sess_options', None)
        device_map = kwargs.pop('device_map', None)
        max_memory = kwargs.pop('max_memory', None)
        offload_folder = kwargs.pop('offload_folder', None)
        offload_state_dict = kwargs.pop('offload_state_dict', False)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        variant = kwargs.pop('variant', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        use_onnx = kwargs.pop('use_onnx', None)
        load_connected_pipeline = kwargs.pop('load_connected_pipeline', False)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        if device_map is not None and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Loading and dispatching requires torch >= 1.9.0. Please either update your PyTorch version or set `device_map=None`.')
        if device_map is not None and (not is_sapiens_accelerator_available()): raise NotImplementedError('Using `device_map` requires the `sapiens_accelerator` library. Please install it using: `pip install sapiens_accelerator`.')
        if device_map is not None and (not isinstance(device_map, str)): raise ValueError('`device_map` must be a string.')
        if device_map is not None and device_map not in SUPPORTED_DEVICE_MAP: raise NotImplementedError(f"{device_map} not supported. Supported strategies are: {', '.join(SUPPORTED_DEVICE_MAP)}")
        if device_map is not None and device_map in SUPPORTED_DEVICE_MAP:
            if is_sapiens_accelerator_version('<', '0.28.0'): raise NotImplementedError('Device placement requires `sapiens_accelerator` version `0.28.0` or later.')
        if low_cpu_mem_usage is False and device_map is not None: raise ValueError(f'You cannot set `low_cpu_mem_usage` to False while using device_map={device_map} for loading and dispatching. Please make sure to set `low_cpu_mem_usage=True`.')
        if not os.path.isdir(pretrained_model_name_or_path):
            if pretrained_model_name_or_path.count('/') > 1: raise ValueError(f'The provided pretrained_model_name_or_path "{pretrained_model_name_or_path}" is neither a valid local path nor a valid repo id. Please check the parameter.')
            cached_folder = cls.download(pretrained_model_name_or_path, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token,
            revision=revision, from_flax=from_flax, use_safetensors=use_safetensors, use_onnx=use_onnx, custom_pipeline=custom_pipeline, custom_revision=custom_revision,
            variant=variant, load_connected_pipeline=load_connected_pipeline, **kwargs)
        else: cached_folder = pretrained_model_name_or_path
        config_dict = cls.load_config(cached_folder)
        config_dict.pop('_ignore_files', None)
        model_variants = _identify_model_variants(folder=cached_folder, variant=variant, config=config_dict)
        if len(model_variants) == 0 and variant is not None:
            error_message = f'You are trying to load the model files of the `variant={variant}`, but no such modeling files are available.'
            raise ValueError(error_message)
        custom_pipeline, custom_class_name = _resolve_custom_pipeline_and_cls(folder=cached_folder, config=config_dict, custom_pipeline=custom_pipeline)
        pipeline_class = _get_pipeline_class(cls, config=config_dict, load_connected_pipeline=load_connected_pipeline, custom_pipeline=custom_pipeline,
        class_name=custom_class_name, cache_dir=cache_dir, revision=custom_revision)
        if device_map is not None and pipeline_class._load_connected_pipes: raise NotImplementedError('`device_map` is not yet supported for connected pipelines.')
        _maybe_raise_warning_for_inpainting(pipeline_class=pipeline_class, pretrained_model_name_or_path=pretrained_model_name_or_path, config=config_dict)
        expected_modules, optional_kwargs = cls._get_signature_keys(pipeline_class)
        expected_types = pipeline_class._get_signature_types()
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        init_dict, unused_kwargs, _ = pipeline_class.extract_init_dict(config_dict, **kwargs)
        init_kwargs = {k: init_dict.pop(k) for k in optional_kwargs if k in init_dict and k not in pipeline_class._optional_components}
        init_kwargs = {**init_kwargs, **passed_pipe_kwargs}
        def load_module(name, value):
            if value[0] is None: return False
            if name in passed_class_obj and passed_class_obj[name] is None: return False
            return True
        init_dict = {k: v for k, v in init_dict.items() if load_module(k, v)}
        for key in init_dict.keys():
            if key not in passed_class_obj: continue
            if 'scheduler' in key: continue
            class_obj = passed_class_obj[key]
            _expected_class_types = []
            for expected_type in expected_types[key]:
                if isinstance(expected_type, enum.EnumMeta): _expected_class_types.extend(expected_type.__members__.keys())
                else: _expected_class_types.append(expected_type.__name__)
            _is_valid_type = class_obj.__class__.__name__ in _expected_class_types
        if from_flax and 'safety_checker' in init_dict and ('safety_checker' not in passed_class_obj): raise NotImplementedError('The safety checker cannot be automatically loaded when loading weights `from_flax`. Please, pass `safety_checker=None` to `from_pretrained`, and load the safety checker separately if you need it.')
        from .. import pipelines
        final_device_map = None
        if device_map is not None: final_device_map = _get_final_device_map(device_map=device_map, pipeline_class=pipeline_class, passed_class_obj=passed_class_obj, init_dict=init_dict,
        library=library, max_memory=max_memory, torch_dtype=torch_dtype, cached_folder=cached_folder, force_download=force_download, proxies=proxies,
        local_files_only=local_files_only, token=token, revision=revision)
        current_device_map = None
        for name, (library_name, class_name) in logging.tqdm(init_dict.items(), desc='Loading pipeline components...'):
            if 'transformers' in library_name and 'sapiens_transformers' not in library_name: library_name = library_name.replace('transformers', 'sapiens_transformers')
            if library_name == 'sapiens_transformers.diffusers': library_name = 'sapiens_transformers.diffusers'
            if final_device_map is not None and len(final_device_map) > 0:
                component_device = final_device_map.get(name, None)
                if component_device is not None: current_device_map = {'': component_device}
                else: current_device_map = None
            class_name = class_name[4:] if class_name.startswith('Flax') else class_name
            is_pipeline_module = hasattr(pipelines, library_name)
            importable_classes = ALL_IMPORTABLE_CLASSES
            loaded_sub_model = None
            if name in passed_class_obj:
                maybe_raise_or_warn(library_name, library, class_name, importable_classes, passed_class_obj, name, is_pipeline_module)
                loaded_sub_model = passed_class_obj[name]
            else:
                loaded_sub_model = load_sub_model(library_name=library_name, class_name=class_name, importable_classes=importable_classes, pipelines=pipelines,
                is_pipeline_module=is_pipeline_module, pipeline_class=pipeline_class, torch_dtype=torch_dtype, provider=provider, sess_options=sess_options,
                device_map=current_device_map, max_memory=max_memory, offload_folder=offload_folder, offload_state_dict=offload_state_dict, model_variants=model_variants,
                name=name, from_flax=from_flax, variant=variant, low_cpu_mem_usage=low_cpu_mem_usage, cached_folder=cached_folder, use_safetensors=use_safetensors)
            init_kwargs[name] = loaded_sub_model
        if pipeline_class._load_connected_pipes and os.path.isfile(os.path.join(cached_folder, 'README.md')): init_kwargs = _update_init_kwargs_with_connected_pipeline(init_kwargs=init_kwargs,
        passed_pipe_kwargs=passed_pipe_kwargs, passed_class_objs=passed_class_obj, folder=cached_folder, **kwargs_copied)
        missing_modules = set(expected_modules) - set(init_kwargs.keys())
        passed_modules = list(passed_class_obj.keys())
        optional_modules = pipeline_class._optional_components
        if len(missing_modules) > 0 and missing_modules <= set(passed_modules + optional_modules):
            for module in missing_modules: init_kwargs[module] = passed_class_obj.get(module, None)
        elif len(missing_modules) > 0:
            passed_modules = set(list(init_kwargs.keys()) + list(passed_class_obj.keys())) - optional_kwargs
            raise ValueError(f'Pipeline {pipeline_class} expected {expected_modules}, but only {passed_modules} were passed.')
        model = pipeline_class(**init_kwargs)
        model.register_to_config(_name_or_path=pretrained_model_name_or_path)
        if device_map is not None: setattr(model, 'hf_device_map', final_device_map)
        removeSysPath()
        return model
    @property
    def name_or_path(self) -> str: return getattr(self.config, '_name_or_path', None)
    @property
    def _execution_device(self):
        for name, model in self.components.items():
            if not isinstance(model, torch.nn.Module) or name in self._exclude_from_cpu_offload: continue
            if not hasattr(model, '_hf_hook'): return self.device
            for module in model.modules():
                if hasattr(module, '_hf_hook') and hasattr(module._hf_hook, 'execution_device') and (module._hf_hook.execution_device is not None): return torch.device(module._hf_hook.execution_device)
        return self.device
    def remove_all_hooks(self):
        for _, model in self.components.items():
            if isinstance(model, torch.nn.Module) and hasattr(model, '_hf_hook'): sapiens_accelerator.hooks.remove_hook_from_module(model, recurse=True)
        self._all_hooks = []
    def enable_model_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        is_pipeline_device_mapped = self.hf_device_map is not None and len(self.hf_device_map) > 1
        if is_pipeline_device_mapped: raise ValueError("It seems like you have activated a device mapping strategy on the pipeline so calling `enable_model_cpu_offload() isn't allowed. You can call `reset_device_map()` first and then call `enable_model_cpu_offload()`.")
        if self.model_cpu_offload_seq is None: raise ValueError('Model CPU offload cannot be enabled because no `model_cpu_offload_seq` class attribute is set.')
        if is_sapiens_accelerator_available() and is_sapiens_accelerator_version('>=', '0.17.0.dev0'): from sapiens_accelerator import cpu_offload_with_hook
        else: raise ImportError('`enable_model_cpu_offload` requires `sapiens_accelerator v0.17.0` or higher.')
        self.remove_all_hooks()
        torch_device = torch.device(device)
        device_index = torch_device.index
        if gpu_id is not None and device_index is not None: raise ValueError(f'You have passed both `gpu_id`={gpu_id} and an index as part of the passed device `device`={device}Cannot pass both. Please make sure to either not define `gpu_id` or not pass the index as part of the device: `device`={torch_device.type}')
        self._offload_gpu_id = gpu_id or torch_device.index or getattr(self, '_offload_gpu_id', 0)
        device_type = torch_device.type
        device = torch.device(f'{device_type}:{self._offload_gpu_id}')
        self._offload_device = device
        self.to('cpu', silence_dtype_warnings=True)
        device_mod = getattr(torch, device.type, None)
        if hasattr(device_mod, 'empty_cache') and device_mod.is_available(): device_mod.empty_cache()
        all_model_components = {k: v for k, v in self.components.items() if isinstance(v, torch.nn.Module)}
        self._all_hooks = []
        hook = None
        for model_str in self.model_cpu_offload_seq.split('->'):
            model = all_model_components.pop(model_str, None)
            if not isinstance(model, torch.nn.Module): continue
            _, _, is_loaded_in_8bit_sapiens = _check_sapiens_status(model)
            if is_loaded_in_8bit_sapiens: continue
            _, hook = cpu_offload_with_hook(model, device, prev_module_hook=hook)
            self._all_hooks.append(hook)
        for name, model in all_model_components.items():
            if not isinstance(model, torch.nn.Module): continue
            if name in self._exclude_from_cpu_offload: model.to(device)
            else:
                _, hook = cpu_offload_with_hook(model, device)
                self._all_hooks.append(hook)
    def maybe_free_model_hooks(self):
        if not hasattr(self, '_all_hooks') or len(self._all_hooks) == 0: return
        self.enable_model_cpu_offload(device=getattr(self, '_offload_device', 'cuda'))
    def enable_sequential_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        if is_sapiens_accelerator_available() and is_sapiens_accelerator_version('>=', '0.14.0'): from sapiens_accelerator import cpu_offload
        else: raise ImportError('`enable_sequential_cpu_offload` requires `sapiens_accelerator v0.14.0` or higher')
        self.remove_all_hooks()
        is_pipeline_device_mapped = self.hf_device_map is not None and len(self.hf_device_map) > 1
        if is_pipeline_device_mapped: raise ValueError("It seems like you have activated a device mapping strategy on the pipeline so calling `enable_sequential_cpu_offload() isn't allowed. You can call `reset_device_map()` first and then call `enable_sequential_cpu_offload()`.")
        torch_device = torch.device(device)
        device_index = torch_device.index
        if gpu_id is not None and device_index is not None: raise ValueError(f'You have passed both `gpu_id`={gpu_id} and an index as part of the passed device `device`={device}Cannot pass both. Please make sure to either not define `gpu_id` or not pass the index as part of the device: `device`={torch_device.type}')
        self._offload_gpu_id = gpu_id or torch_device.index or getattr(self, '_offload_gpu_id', 0)
        device_type = torch_device.type
        device = torch.device(f'{device_type}:{self._offload_gpu_id}')
        self._offload_device = device
        if self.device.type != 'cpu':
            self.to('cpu', silence_dtype_warnings=True)
            device_mod = getattr(torch, self.device.type, None)
            if hasattr(device_mod, 'empty_cache') and device_mod.is_available(): device_mod.empty_cache()
        for name, model in self.components.items():
            if not isinstance(model, torch.nn.Module): continue
            if name in self._exclude_from_cpu_offload: model.to(device)
            else:
                offload_buffers = len(model._parameters) > 0
                cpu_offload(model, device, offload_buffers=offload_buffers)
    def reset_device_map(self):
        if self.hf_device_map is None: return
        else:
            self.remove_all_hooks()
            for name, component in self.components.items():
                if isinstance(component, torch.nn.Module): component.to('cpu')
            self.hf_device_map = None
    @classmethod
    @validate_hf_hub_args
    def download(cls, pretrained_model_name, **kwargs) -> Union[str, os.PathLike]:
        """Returns:"""
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        from_flax = kwargs.pop('from_flax', False)
        custom_pipeline = kwargs.pop('custom_pipeline', None)
        custom_revision = kwargs.pop('custom_revision', None)
        variant = kwargs.pop('variant', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        use_onnx = kwargs.pop('use_onnx', None)
        load_connected_pipeline = kwargs.pop('load_connected_pipeline', False)
        trust_remote_code = kwargs.pop('trust_remote_code', False)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        allow_patterns = None
        ignore_patterns = None
        model_info_call_error: Optional[Exception] = None
        if not local_files_only:
            try: info = model_info(pretrained_model_name, token=token, revision=revision)
            except (HTTPError, OfflineModeIsEnabled, requests.ConnectionError) as e:
                local_files_only = True
                model_info_call_error = e
        if not local_files_only:
            filenames = {sibling.rfilename for sibling in info.siblings}
            model_filenames, variant_filenames = variant_compatible_siblings(filenames, variant=variant)
            config_file = hf_hub_download(pretrained_model_name, cls.config_name, cache_dir=cache_dir, revision=revision,
            proxies=proxies, force_download=force_download, token=token)
            config_dict = cls._dict_from_json_file(config_file)
            ignore_filenames = config_dict.pop('_ignore_files', [])
            model_filenames = set(model_filenames) - set(ignore_filenames)
            variant_filenames = set(variant_filenames) - set(ignore_filenames)
            if revision in DEPRECATED_REVISION_ARGS and version.parse(version.parse(__version__).base_version) >= version.parse('0.22.0'): warn_deprecated_model_variant(pretrained_model_name, token, variant, revision, model_filenames)
            custom_components, folder_names = _get_custom_components_and_folders(pretrained_model_name, config_dict, filenames, variant_filenames, variant)
            model_folder_names = {os.path.split(f)[0] for f in model_filenames if os.path.split(f)[0] in folder_names}
            custom_class_name = None
            if custom_pipeline is None and isinstance(config_dict['_class_name'], (list, tuple)):
                custom_pipeline = config_dict['_class_name'][0]
                custom_class_name = config_dict['_class_name'][1]
            allow_patterns = list(model_filenames)
            allow_patterns += [f'{k}/*' for k in folder_names if k not in model_folder_names]
            allow_patterns += [f'{k}/{f}.py' for k, f in custom_components.items()]
            allow_patterns += [f'{custom_pipeline}.py'] if f'{custom_pipeline}.py' in filenames else []
            allow_patterns += [os.path.join(k, 'config.json') for k in model_folder_names]
            allow_patterns += [SCHEDULER_CONFIG_NAME, CONFIG_NAME, cls.config_name, CUSTOM_PIPELINE_FILE_NAME]
            load_pipe_from_hub = custom_pipeline is not None and f'{custom_pipeline}.py' in filenames
            load_components_from_hub = len(custom_components) > 0
            if load_pipe_from_hub and (not trust_remote_code): raise ValueError(f'The repository for {pretrained_model_name} contains custom code in {custom_pipeline}.py which must be executed to correctly load the model. You can inspect the repository content at https://hf.co/{pretrained_model_name}/blob/main/{custom_pipeline}.py.\nPlease pass the argument `trust_remote_code=True` to allow custom code to be run.')
            if load_components_from_hub and (not trust_remote_code): raise ValueError(f"The repository for {pretrained_model_name} contains custom code in {'.py, '.join([os.path.join(k, v) for k, v in custom_components.items()])} which must be executed to correctly load the model. You can inspect the repository content at {', '.join([f'https://hf.co/{pretrained_model_name}/{k}/{v}.py' for k, v in custom_components.items()])}.\nPlease pass the argument `trust_remote_code=True` to allow custom code to be run.")
            pipeline_class = _get_pipeline_class(cls, config_dict, load_connected_pipeline=load_connected_pipeline, custom_pipeline=custom_pipeline, repo_id=pretrained_model_name if load_pipe_from_hub else None,
            hub_revision=revision, class_name=custom_class_name, cache_dir=cache_dir, revision=custom_revision)
            expected_components, _ = cls._get_signature_keys(pipeline_class)
            passed_components = [k for k in expected_components if k in kwargs]
            ignore_patterns = _get_ignore_patterns(passed_components, model_folder_names, model_filenames, variant_filenames, use_safetensors, from_flax, allow_pickle, use_onnx, pipeline_class._is_onnx, variant)
            allow_patterns = [p for p in allow_patterns if not (len(p.split('/')) == 2 and p.split('/')[0] in passed_components)]
            if pipeline_class._load_connected_pipes: allow_patterns.append('README.md')
            ignore_patterns = ignore_patterns + [f'{i}.index.*json' for i in ignore_patterns]
            re_ignore_pattern = [re.compile(fnmatch.translate(p)) for p in ignore_patterns]
            re_allow_pattern = [re.compile(fnmatch.translate(p)) for p in allow_patterns]
            expected_files = [f for f in filenames if not any((p.match(f) for p in re_ignore_pattern))]
            expected_files = [f for f in expected_files if any((p.match(f) for p in re_allow_pattern))]
            snapshot_folder = Path(config_file).parent
            pipeline_is_cached = all(((snapshot_folder / f).is_file() for f in expected_files))
            if pipeline_is_cached and (not force_download): return snapshot_folder
        user_agent = {'pipeline_class': cls.__name__}
        if custom_pipeline is not None and (not custom_pipeline.endswith('.py')): user_agent['custom_pipeline'] = custom_pipeline
        try:
            cached_folder = snapshot_download(pretrained_model_name, cache_dir=cache_dir, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns, user_agent=user_agent)
            cls_name = cls.load_config(os.path.join(cached_folder, 'model_index.json')).get('_class_name', None)
            cls_name = cls_name[4:] if isinstance(cls_name, str) and cls_name.startswith('Flax') else cls_name
            diffusers_module = importlib.import_module(__name__.split('.')[0])
            pipeline_class = getattr(diffusers_module, cls_name, None) if isinstance(cls_name, str) else None
            if pipeline_class is not None and pipeline_class._load_connected_pipes:
                modelcard = ModelCard.load(os.path.join(cached_folder, 'README.md'))
                connected_pipes = sum([getattr(modelcard.data, k, []) for k in CONNECTED_PIPES_KEYS], [])
                for connected_pipe_repo_id in connected_pipes:
                    download_kwargs = {'cache_dir': cache_dir, 'force_download': force_download, 'proxies': proxies, 'local_files_only': local_files_only, 'token': token, 'variant': variant, 'use_safetensors': use_safetensors}
                    DiffusionPipeline.download(connected_pipe_repo_id, **download_kwargs)
            return cached_folder
        except FileNotFoundError:
            if model_info_call_error is None: raise
            else: raise EnvironmentError(f'Cannot load model {pretrained_model_name}: model is not cached locally and an error occurred while trying to fetch metadata from the Hub. Please check out the root cause in the stacktrace above.') from model_info_call_error
    @classmethod
    def _get_signature_keys(cls, obj):
        parameters = inspect.signature(obj.__init__).parameters
        required_parameters = {k: v for k, v in parameters.items() if v.default == inspect._empty}
        optional_parameters = set({k for k, v in parameters.items() if v.default != inspect._empty})
        expected_modules = set(required_parameters.keys()) - {'self'}
        optional_names = list(optional_parameters)
        for name in optional_names:
            if name in cls._optional_components:
                expected_modules.add(name)
                optional_parameters.remove(name)
        return (expected_modules, optional_parameters)
    @classmethod
    def _get_signature_types(cls):
        signature_types = {}
        for k, v in inspect.signature(cls.__init__).parameters.items():
            if inspect.isclass(v.annotation): signature_types[k] = (v.annotation,)
            elif get_origin(v.annotation) == Union: signature_types[k] = get_args(v.annotation)
        return signature_types
    @property
    def components(self) -> Dict[str, Any]:
        """Examples:"""
        expected_modules, optional_parameters = self._get_signature_keys(self)
        components = {k: getattr(self, k) for k in self.config.keys() if not k.startswith('_') and k not in optional_parameters}
        if set(components.keys()) != expected_modules: raise ValueError(f'{self} has been incorrectly initialized or {self.__class__} is incorrectly implemented. Expected {expected_modules} to be defined, but {components.keys()} are defined.')
        return components
    @staticmethod
    def numpy_to_pil(images): return numpy_to_pil(images)
    @torch.compiler.disable
    def progress_bar(self, iterable=None, total=None):
        if not hasattr(self, '_progress_bar_config'): self._progress_bar_config = {}
        elif not isinstance(self._progress_bar_config, dict): raise ValueError(f'`self._progress_bar_config` should be of type `dict`, but is {type(self._progress_bar_config)}.')
        if iterable is not None: return tqdm(iterable, **self._progress_bar_config)
        elif total is not None: return tqdm(total=total, **self._progress_bar_config)
        else: raise ValueError('Either `total` or `iterable` has to be defined.')
    def set_progress_bar_config(self, **kwargs): self._progress_bar_config = kwargs
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None):
        """Examples:"""
        self.set_use_memory_efficient_attention_xformers(True, attention_op)
    def disable_xformers_memory_efficient_attention(self): self.set_use_memory_efficient_attention_xformers(False)
    def set_use_memory_efficient_attention_xformers(self, valid: bool, attention_op: Optional[Callable]=None) -> None:
        def fn_recursive_set_mem_eff(module: torch.nn.Module):
            if hasattr(module, 'set_use_memory_efficient_attention_xformers'): module.set_use_memory_efficient_attention_xformers(valid, attention_op)
            for child in module.children(): fn_recursive_set_mem_eff(child)
        module_names, _ = self._get_signature_keys(self)
        modules = [getattr(self, n, None) for n in module_names]
        modules = [m for m in modules if isinstance(m, torch.nn.Module)]
        for module in modules: fn_recursive_set_mem_eff(module)
    def enable_attention_slicing(self, slice_size: Optional[Union[str, int]]='auto'):
        """Examples:"""
        self.set_attention_slice(slice_size)
    def disable_attention_slicing(self): self.enable_attention_slicing(None)
    def set_attention_slice(self, slice_size: Optional[int]):
        module_names, _ = self._get_signature_keys(self)
        modules = [getattr(self, n, None) for n in module_names]
        modules = [m for m in modules if isinstance(m, torch.nn.Module) and hasattr(m, 'set_attention_slice')]
        for module in modules: module.set_attention_slice(slice_size)
    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        """Examples:"""
        original_config = dict(pipeline.config)
        torch_dtype = kwargs.pop('torch_dtype', None)
        custom_pipeline = kwargs.pop('custom_pipeline', None)
        custom_revision = kwargs.pop('custom_revision', None)
        if custom_pipeline is not None: pipeline_class = _get_custom_pipeline_class(custom_pipeline, revision=custom_revision)
        else: pipeline_class = cls
        expected_modules, optional_kwargs = cls._get_signature_keys(pipeline_class)
        parameters = inspect.signature(cls.__init__).parameters
        true_optional_modules = set({k for k, v in parameters.items() if v.default != inspect._empty and k in expected_modules})
        component_types = pipeline_class._get_signature_types()
        pretrained_model_name_or_path = original_config.pop('_name_or_path', None)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        original_class_obj = {}
        for name, component in pipeline.components.items():
            if name in expected_modules and name not in passed_class_obj:
                if not isinstance(component, ModelMixin) or type(component) in component_types[name] or (component is None and name in cls._optional_components): original_class_obj[name] = component
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        original_pipe_kwargs = {k: original_config[k] for k in original_config.keys() if k in optional_kwargs and k not in passed_pipe_kwargs}
        additional_pipe_kwargs = [k[1:] for k in original_config.keys() if k.startswith('_') and k[1:] in optional_kwargs and (k[1:] not in passed_pipe_kwargs)]
        for k in additional_pipe_kwargs: original_pipe_kwargs[k] = original_config.pop(f'_{k}')
        pipeline_kwargs = {**passed_class_obj, **original_class_obj, **passed_pipe_kwargs, **original_pipe_kwargs, **kwargs}
        unused_original_config = {f"{('' if k.startswith('_') else '_')}{k}": v for k, v in original_config.items() if k not in pipeline_kwargs}
        missing_modules = set(expected_modules) - set(pipeline._optional_components) - set(pipeline_kwargs.keys()) - set(true_optional_modules)
        if len(missing_modules) > 0: raise ValueError(f'Pipeline {pipeline_class} expected {expected_modules}, but only {set(list(passed_class_obj.keys()) + list(original_class_obj.keys()))} were passed')
        new_pipeline = pipeline_class(**pipeline_kwargs)
        if pretrained_model_name_or_path is not None: new_pipeline.register_to_config(_name_or_path=pretrained_model_name_or_path)
        new_pipeline.register_to_config(**unused_original_config)
        if torch_dtype is not None: new_pipeline.to(dtype=torch_dtype)
        return new_pipeline
class StableDiffusionMixin:
    def enable_vae_slicing(self): self.vae.enable_slicing()
    def disable_vae_slicing(self): self.vae.disable_slicing()
    def enable_vae_tiling(self): self.vae.enable_tiling()
    def disable_vae_tiling(self): self.vae.disable_tiling()
    def enable_freeu(self, s1: float, s2: float, b1: float, b2: float):
        """Args:"""
        if not hasattr(self, 'unet'): raise ValueError('The pipeline must have `unet` for using FreeU.')
        self.unet.enable_freeu(s1=s1, s2=s2, b1=b1, b2=b2)
    def disable_freeu(self): self.unet.disable_freeu()
    def fuse_qkv_projections(self, unet: bool=True, vae: bool=True):
        """Args:"""
        self.fusing_unet = False
        self.fusing_vae = False
        if unet:
            self.fusing_unet = True
            self.unet.fuse_qkv_projections()
            self.unet.set_attn_processor(FusedAttnProcessor2_0())
        if vae:
            if not isinstance(self.vae, AutoencoderKL): raise ValueError('`fuse_qkv_projections()` is only supported for the VAE of type `AutoencoderKL`.')
            self.fusing_vae = True
            self.vae.fuse_qkv_projections()
            self.vae.set_attn_processor(FusedAttnProcessor2_0())
    def unfuse_qkv_projections(self, unet: bool=True, vae: bool=True):
        """Args:"""
        if unet:
            if self.fusing_unet:
                self.unet.unfuse_qkv_projections()
                self.fusing_unet = False
        if vae:
            if self.fusing_vae:
                self.vae.unfuse_qkv_projections()
                self.fusing_vae = False
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
