'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import (USE_PEFT_BACKEND, _get_model_file, convert_state_dict_to_diffusers, convert_state_dict_to_peft, delete_adapter_layers, deprecate, get_adapter_name, get_peft_kwargs,
is_sapiens_accelerator_available, is_peft_available, is_peft_version, is_transformers_available, is_sapiens_transformers_version, recurse_remove_peft_layers, scale_lora_layers, set_adapter_layers, set_weights_and_activate_adapters)
from ..models.modeling_utils import ModelMixin, load_state_dict
from typing import Callable, Dict, List, Optional, Union
from huggingface_hub.constants import HF_HUB_OFFLINE
from huggingface_hub import model_info
from pathlib import Path
import torch.nn as nn
import safetensors
import inspect
import torch
import copy
import os
if is_transformers_available():
    from ..models.lora import text_encoder_attn_modules, text_encoder_mlp_modules
    from sapiens_transformers import PreTrainedModel
if is_peft_available(): from peft.tuners.tuners_utils import BaseTunerLayer
if is_sapiens_accelerator_available(): from sapiens_accelerator.hooks import AlignDevicesHook, CpuOffload, remove_hook_from_module
LORA_WEIGHT_NAME = 'pytorch_lora_weights.bin'
LORA_WEIGHT_NAME_SAFE = 'pytorch_lora_weights.safetensors'
def fuse_text_encoder_lora(text_encoder, lora_scale=1.0, safe_fusing=False, adapter_names=None):
    """Args:"""
    merge_kwargs = {'safe_merge': safe_fusing}
    for module in text_encoder.modules():
        if isinstance(module, BaseTunerLayer):
            if lora_scale != 1.0: module.scale_layer(lora_scale)
            supported_merge_kwargs = list(inspect.signature(module.merge).parameters)
            if 'adapter_names' in supported_merge_kwargs: merge_kwargs['adapter_names'] = adapter_names
            elif 'adapter_names' not in supported_merge_kwargs and adapter_names is not None: raise ValueError('The `adapter_names` argument is not supported with your PEFT version. Please upgrade to the latest version of PEFT. `pip install -U peft`')
            module.merge(**merge_kwargs)
def unfuse_text_encoder_lora(text_encoder):
    """Args:"""
    for module in text_encoder.modules():
        if isinstance(module, BaseTunerLayer): module.unmerge()
def set_adapters_for_text_encoder(adapter_names: Union[List[str], str], text_encoder: Optional['PreTrainedModel']=None, text_encoder_weights: Optional[Union[float, List[float], List[None]]]=None):
    """Args:"""
    if text_encoder is None: raise ValueError('The pipeline does not have a default `pipe.text_encoder` class. Please make sure to pass a `text_encoder` instead.')
    def process_weights(adapter_names, weights):
        if not isinstance(weights, list): weights = [weights] * len(adapter_names)
        if len(adapter_names) != len(weights): raise ValueError(f'Length of adapter names {len(adapter_names)} is not equal to the length of the weights {len(weights)}')
        weights = [w if w is not None else 1.0 for w in weights]
        return weights
    adapter_names = [adapter_names] if isinstance(adapter_names, str) else adapter_names
    text_encoder_weights = process_weights(adapter_names, text_encoder_weights)
    set_weights_and_activate_adapters(text_encoder, adapter_names, text_encoder_weights)
def disable_lora_for_text_encoder(text_encoder: Optional['PreTrainedModel']=None):
    """Args:"""
    if text_encoder is None: raise ValueError('Text Encoder not found.')
    set_adapter_layers(text_encoder, enabled=False)
def enable_lora_for_text_encoder(text_encoder: Optional['PreTrainedModel']=None):
    """Args:"""
    if text_encoder is None: raise ValueError('Text Encoder not found.')
    set_adapter_layers(text_encoder, enabled=True)
def _remove_text_encoder_monkey_patch(text_encoder):
    recurse_remove_peft_layers(text_encoder)
    if getattr(text_encoder, 'peft_config', None) is not None:
        del text_encoder.peft_config
        text_encoder._hf_peft_config_loaded = None
def _fetch_state_dict(pretrained_model_name_or_path_or_dict, weight_name, use_safetensors, local_files_only, cache_dir, force_download, proxies, token, revision, subfolder, user_agent, allow_pickle):
    model_file = None
    if not isinstance(pretrained_model_name_or_path_or_dict, dict):
        if use_safetensors and weight_name is None or (weight_name is not None and weight_name.endswith('.safetensors')):
            try:
                if weight_name is None: weight_name = _best_guess_weight_name(pretrained_model_name_or_path_or_dict, file_extension='.safetensors', local_files_only=local_files_only)
                model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name or LORA_WEIGHT_NAME_SAFE, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                state_dict = safetensors.torch.load_file(model_file, device='cpu')
            except (IOError, safetensors.SafetensorError) as e:
                if not allow_pickle: raise e
                model_file = None
                pass
        if model_file is None:
            if weight_name is None: weight_name = _best_guess_weight_name(pretrained_model_name_or_path_or_dict, file_extension='.bin', local_files_only=local_files_only)
            model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name or LORA_WEIGHT_NAME, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
            state_dict = load_state_dict(model_file)
    else: state_dict = pretrained_model_name_or_path_or_dict
    return state_dict
def _best_guess_weight_name(pretrained_model_name_or_path_or_dict, file_extension='.safetensors', local_files_only=False):
    if local_files_only or HF_HUB_OFFLINE: raise ValueError('When using the offline mode, you must specify a `weight_name`.')
    targeted_files = []
    if os.path.isfile(pretrained_model_name_or_path_or_dict): return
    elif os.path.isdir(pretrained_model_name_or_path_or_dict): targeted_files = [f for f in os.listdir(pretrained_model_name_or_path_or_dict) if f.endswith(file_extension)]
    else:
        files_in_repo = model_info(pretrained_model_name_or_path_or_dict).siblings
        targeted_files = [f.rfilename for f in files_in_repo if f.rfilename.endswith(file_extension)]
    if len(targeted_files) == 0: return
    unallowed_substrings = {'scheduler', 'optimizer', 'checkpoint'}
    targeted_files = list(filter(lambda x: all((substring not in x for substring in unallowed_substrings)), targeted_files))
    if any((f.endswith(LORA_WEIGHT_NAME) for f in targeted_files)): targeted_files = list(filter(lambda x: x.endswith(LORA_WEIGHT_NAME), targeted_files))
    elif any((f.endswith(LORA_WEIGHT_NAME_SAFE) for f in targeted_files)): targeted_files = list(filter(lambda x: x.endswith(LORA_WEIGHT_NAME_SAFE), targeted_files))
    if len(targeted_files) > 1: raise ValueError(f"Provided path contains more than one weights file in the {file_extension} format. Either specify `weight_name` in `load_lora_weights` or make sure there's only one  `.safetensors` or `.bin` file in  {pretrained_model_name_or_path_or_dict}.")
    weight_name = targeted_files[0]
    return weight_name
def _load_lora_into_text_encoder(state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, text_encoder_name='text_encoder', adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
    if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
    peft_kwargs = {}
    if low_cpu_mem_usage:
        if not is_peft_version('>=', '0.13.1'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if not is_sapiens_transformers_version('>', '1.0.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `transformers` version. Please update it with `pip install -U transformers`.')
        peft_kwargs['low_cpu_mem_usage'] = low_cpu_mem_usage
    from peft import LoraConfig
    keys = list(state_dict.keys())
    prefix = text_encoder_name if prefix is None else prefix
    if any((text_encoder_name in key for key in keys)):
        text_encoder_keys = [k for k in keys if k.startswith(prefix) and k.split('.')[0] == prefix]
        text_encoder_lora_state_dict = {k.replace(f'{prefix}.', ''): v for k, v in state_dict.items() if k in text_encoder_keys}
        if len(text_encoder_lora_state_dict) > 0:
            rank = {}
            text_encoder_lora_state_dict = convert_state_dict_to_diffusers(text_encoder_lora_state_dict)
            text_encoder_lora_state_dict = convert_state_dict_to_peft(text_encoder_lora_state_dict)
            for name, _ in text_encoder_attn_modules(text_encoder):
                for module in ('out_proj', 'q_proj', 'k_proj', 'v_proj'):
                    rank_key = f'{name}.{module}.lora_B.weight'
                    if rank_key not in text_encoder_lora_state_dict: continue
                    rank[rank_key] = text_encoder_lora_state_dict[rank_key].shape[1]
            for name, _ in text_encoder_mlp_modules(text_encoder):
                for module in ('fc1', 'fc2'):
                    rank_key = f'{name}.{module}.lora_B.weight'
                    if rank_key not in text_encoder_lora_state_dict: continue
                    rank[rank_key] = text_encoder_lora_state_dict[rank_key].shape[1]
            if network_alphas is not None:
                alpha_keys = [k for k in network_alphas.keys() if k.startswith(prefix) and k.split('.')[0] == prefix]
                network_alphas = {k.replace(f'{prefix}.', ''): v for k, v in network_alphas.items() if k in alpha_keys}
            lora_config_kwargs = get_peft_kwargs(rank, network_alphas, text_encoder_lora_state_dict, is_unet=False)
            if 'use_dora' in lora_config_kwargs:
                if lora_config_kwargs['use_dora']:
                    if is_peft_version('<', '0.9.0'): raise ValueError('You need `peft` 0.9.0 at least to use DoRA-enabled LoRAs. Please upgrade your installation of `peft`.')
                elif is_peft_version('<', '0.9.0'): lora_config_kwargs.pop('use_dora')
            if 'lora_bias' in lora_config_kwargs:
                if lora_config_kwargs['lora_bias']:
                    if is_peft_version('<=', '0.13.2'): raise ValueError('You need `peft` 0.14.0 at least to use `bias` in LoRAs. Please upgrade your installation of `peft`.')
                elif is_peft_version('<=', '0.13.2'): lora_config_kwargs.pop('lora_bias')
            lora_config = LoraConfig(**lora_config_kwargs)
            if adapter_name is None: adapter_name = get_adapter_name(text_encoder)
            is_model_cpu_offload, is_sequential_cpu_offload = _func_optionally_disable_offloading(_pipeline)
            text_encoder.load_adapter(adapter_name=adapter_name, adapter_state_dict=text_encoder_lora_state_dict, peft_config=lora_config, **peft_kwargs)
            scale_lora_layers(text_encoder, weight=lora_scale)
            text_encoder.to(device=text_encoder.device, dtype=text_encoder.dtype)
            if is_model_cpu_offload: _pipeline.enable_model_cpu_offload()
            elif is_sequential_cpu_offload: _pipeline.enable_sequential_cpu_offload()
def _func_optionally_disable_offloading(_pipeline):
    is_model_cpu_offload = False
    is_sequential_cpu_offload = False
    if _pipeline is not None and _pipeline.hf_device_map is None:
        for _, component in _pipeline.components.items():
            if isinstance(component, nn.Module) and hasattr(component, '_hf_hook'):
                if not is_model_cpu_offload: is_model_cpu_offload = isinstance(component._hf_hook, CpuOffload)
                if not is_sequential_cpu_offload: is_sequential_cpu_offload = isinstance(component._hf_hook, AlignDevicesHook) or (hasattr(component._hf_hook, 'hooks') and isinstance(component._hf_hook.hooks[0], AlignDevicesHook))
                remove_hook_from_module(component, recurse=is_sequential_cpu_offload)
    return (is_model_cpu_offload, is_sequential_cpu_offload)
class LoraBaseMixin:
    _lora_loadable_modules = []
    num_fused_loras = 0
    def load_lora_weights(self, **kwargs): raise NotImplementedError('`load_lora_weights()` is not implemented.')
    @classmethod
    def save_lora_weights(cls, **kwargs): raise NotImplementedError('`save_lora_weights()` not implemented.')
    @classmethod
    def lora_state_dict(cls, **kwargs): raise NotImplementedError('`lora_state_dict()` is not implemented.')
    @classmethod
    def _optionally_disable_offloading(cls, _pipeline):
        """Returns:"""
        return _func_optionally_disable_offloading(_pipeline=_pipeline)
    @classmethod
    def _fetch_state_dict(cls, *args, **kwargs):
        deprecation_message = f'Using the `_fetch_state_dict()` method from {cls} has been deprecated and will be removed in a future version. Please use `from sapiens_transformers.diffusers.loaders.lora_base import _fetch_state_dict`.'
        deprecate('_fetch_state_dict', '0.35.0', deprecation_message)
        return _fetch_state_dict(*args, **kwargs)
    @classmethod
    def _best_guess_weight_name(cls, *args, **kwargs):
        deprecation_message = f'Using the `_best_guess_weight_name()` method from {cls} has been deprecated and will be removed in a future version. Please use `from sapiens_transformers.diffusers.loaders.lora_base import _best_guess_weight_name`.'
        deprecate('_best_guess_weight_name', '0.35.0', deprecation_message)
        return _best_guess_weight_name(*args, **kwargs)
    def unload_lora_weights(self):
        """Examples:"""
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None:
                if issubclass(model.__class__, ModelMixin): model.unload_lora()
                elif issubclass(model.__class__, PreTrainedModel): _remove_text_encoder_monkey_patch(model)
    def fuse_lora(self, components: List[str]=[], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        if 'fuse_unet' in kwargs:
            depr_message = 'Passing `fuse_unet` to `fuse_lora()` is deprecated and will be ignored. Please use the `components` argument and provide a list of the components whose LoRAs are to be fused. `fuse_unet` will be removed in a future version.'
            deprecate('fuse_unet', '1.0.0', depr_message)
        if 'fuse_transformer' in kwargs:
            depr_message = 'Passing `fuse_transformer` to `fuse_lora()` is deprecated and will be ignored. Please use the `components` argument and provide a list of the components whose LoRAs are to be fused. `fuse_transformer` will be removed in a future version.'
            deprecate('fuse_transformer', '1.0.0', depr_message)
        if 'fuse_text_encoder' in kwargs:
            depr_message = 'Passing `fuse_text_encoder` to `fuse_lora()` is deprecated and will be ignored. Please use the `components` argument and provide a list of the components whose LoRAs are to be fused. `fuse_text_encoder` will be removed in a future version.'
            deprecate('fuse_text_encoder', '1.0.0', depr_message)
        if len(components) == 0: raise ValueError('`components` cannot be an empty list.')
        for fuse_component in components:
            if fuse_component not in self._lora_loadable_modules: raise ValueError(f'{fuse_component} is not found in self._lora_loadable_modules={self._lora_loadable_modules!r}.')
            model = getattr(self, fuse_component, None)
            if model is not None:
                if issubclass(model.__class__, ModelMixin): model.fuse_lora(lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
                if issubclass(model.__class__, PreTrainedModel): fuse_text_encoder_lora(model, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
        self.num_fused_loras += 1
    def unfuse_lora(self, components: List[str]=[], **kwargs):
        """Args:"""
        if 'unfuse_unet' in kwargs:
            depr_message = 'Passing `unfuse_unet` to `unfuse_lora()` is deprecated and will be ignored. Please use the `components` argument. `unfuse_unet` will be removed in a future version.'
            deprecate('unfuse_unet', '1.0.0', depr_message)
        if 'unfuse_transformer' in kwargs:
            depr_message = 'Passing `unfuse_transformer` to `unfuse_lora()` is deprecated and will be ignored. Please use the `components` argument. `unfuse_transformer` will be removed in a future version.'
            deprecate('unfuse_transformer', '1.0.0', depr_message)
        if 'unfuse_text_encoder' in kwargs:
            depr_message = 'Passing `unfuse_text_encoder` to `unfuse_lora()` is deprecated and will be ignored. Please use the `components` argument. `unfuse_text_encoder` will be removed in a future version.'
            deprecate('unfuse_text_encoder', '1.0.0', depr_message)
        if len(components) == 0: raise ValueError('`components` cannot be an empty list.')
        for fuse_component in components:
            if fuse_component not in self._lora_loadable_modules: raise ValueError(f'{fuse_component} is not found in self._lora_loadable_modules={self._lora_loadable_modules!r}.')
            model = getattr(self, fuse_component, None)
            if model is not None:
                if issubclass(model.__class__, (ModelMixin, PreTrainedModel)):
                    for module in model.modules():
                        if isinstance(module, BaseTunerLayer): module.unmerge()
        self.num_fused_loras -= 1
    def set_adapters(self, adapter_names: Union[List[str], str], adapter_weights: Optional[Union[float, Dict, List[float], List[Dict]]]=None):
        adapter_names = [adapter_names] if isinstance(adapter_names, str) else adapter_names
        adapter_weights = copy.deepcopy(adapter_weights)
        if not isinstance(adapter_weights, list): adapter_weights = [adapter_weights] * len(adapter_names)
        if len(adapter_names) != len(adapter_weights): raise ValueError(f'Length of adapter names {len(adapter_names)} is not equal to the length of the weights {len(adapter_weights)}')
        list_adapters = self.get_list_adapters()
        all_adapters = {adapter for adapters in list_adapters.values() for adapter in adapters}
        missing_adapters = set(adapter_names) - all_adapters
        if len(missing_adapters) > 0: raise ValueError(f'Adapter name(s) {missing_adapters} not in the list of present adapters: {all_adapters}.')
        invert_list_adapters = {adapter: [part for part, adapters in list_adapters.items() if adapter in adapters] for adapter in all_adapters}
        _component_adapter_weights = {}
        for component in self._lora_loadable_modules:
            model = getattr(self, component)
            for adapter_name, weights in zip(adapter_names, adapter_weights):
                if isinstance(weights, dict): component_adapter_weights = weights.pop(component, None)
                else: component_adapter_weights = weights
                _component_adapter_weights.setdefault(component, [])
                _component_adapter_weights[component].append(component_adapter_weights)
            if issubclass(model.__class__, ModelMixin): model.set_adapters(adapter_names, _component_adapter_weights[component])
            elif issubclass(model.__class__, PreTrainedModel): set_adapters_for_text_encoder(adapter_names, model, _component_adapter_weights[component])
    def disable_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None:
                if issubclass(model.__class__, ModelMixin): model.disable_lora()
                elif issubclass(model.__class__, PreTrainedModel): disable_lora_for_text_encoder(model)
    def enable_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None:
                if issubclass(model.__class__, ModelMixin): model.enable_lora()
                elif issubclass(model.__class__, PreTrainedModel): enable_lora_for_text_encoder(model)
    def delete_adapters(self, adapter_names: Union[List[str], str]):
        """Args:"""
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        if isinstance(adapter_names, str): adapter_names = [adapter_names]
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None:
                if issubclass(model.__class__, ModelMixin): model.delete_adapters(adapter_names)
                elif issubclass(model.__class__, PreTrainedModel):
                    for adapter_name in adapter_names: delete_adapter_layers(model, adapter_name)
    def get_active_adapters(self) -> List[str]:
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method. Please install the latest version of PEFT `pip install -U peft`')
        active_adapters = []
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None and issubclass(model.__class__, ModelMixin):
                for module in model.modules():
                    if isinstance(module, BaseTunerLayer):
                        active_adapters = module.active_adapters
                        break
        return active_adapters
    def get_list_adapters(self) -> Dict[str, List[str]]:
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method. Please install the latest version of PEFT `pip install -U peft`')
        set_adapters = {}
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None and issubclass(model.__class__, (ModelMixin, PreTrainedModel)) and hasattr(model, 'peft_config'): set_adapters[component] = list(model.peft_config.keys())
        return set_adapters
    def set_lora_device(self, adapter_names: List[str], device: Union[torch.device, str, int]) -> None:
        """Args:"""
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        for component in self._lora_loadable_modules:
            model = getattr(self, component, None)
            if model is not None:
                for module in model.modules():
                    if isinstance(module, BaseTunerLayer):
                        for adapter_name in adapter_names:
                            module.lora_A[adapter_name].to(device)
                            module.lora_B[adapter_name].to(device)
                            if hasattr(module, 'lora_magnitude_vector') and module.lora_magnitude_vector is not None:
                                if adapter_name in module.lora_magnitude_vector: module.lora_magnitude_vector[adapter_name] = module.lora_magnitude_vector[adapter_name].to(device)
    @staticmethod
    def pack_weights(layers, prefix):
        layers_weights = layers.state_dict() if isinstance(layers, torch.nn.Module) else layers
        layers_state_dict = {f'{prefix}.{module_name}': param for module_name, param in layers_weights.items()}
        return layers_state_dict
    @staticmethod
    def write_lora_layers(state_dict: Dict[str, torch.Tensor], save_directory: str, is_main_process: bool, weight_name: str, save_function: Callable, safe_serialization: bool):
        if os.path.isfile(save_directory): return
        if save_function is None:
            if safe_serialization:
                def save_function(weights, filename): return safetensors.torch.save_file(weights, filename, metadata={'format': 'pt'})
            else: save_function = torch.save
        os.makedirs(save_directory, exist_ok=True)
        if weight_name is None:
            if safe_serialization: weight_name = LORA_WEIGHT_NAME_SAFE
            else: weight_name = LORA_WEIGHT_NAME
        save_path = Path(save_directory, weight_name).as_posix()
        save_function(state_dict, save_path)
    @property
    def lora_scale(self) -> float: return self._lora_scale if hasattr(self, '_lora_scale') else 1.0
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
