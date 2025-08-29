'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import (MIN_PEFT_VERSION, USE_PEFT_BACKEND, check_peft_version, convert_unet_state_dict_to_peft, delete_adapter_layers, get_adapter_name, get_peft_kwargs,
is_peft_available, is_peft_version, set_adapter_layers, set_weights_and_activate_adapters)
from .lora_base import _fetch_state_dict, _func_optionally_disable_offloading
from .unet_loader_utils import _maybe_expand_lora_scales
from typing import Dict, List, Optional, Union
from functools import partial
from pathlib import Path
import safetensors
import inspect
import torch
import os
_SET_ADAPTER_SCALE_FN_MAPPING = {'UNet2DConditionModel': _maybe_expand_lora_scales, 'UNetMotionModel': _maybe_expand_lora_scales, 'SD3Transformer2DModel': lambda model_cls, weights: weights,
'FluxTransformer2DModel': lambda model_cls, weights: weights, 'CogVideoXTransformer3DModel': lambda model_cls, weights: weights, 'MochiTransformer3DModel': lambda model_cls, weights: weights,
'HunyuanVideoTransformer3DModel': lambda model_cls, weights: weights, 'LTXVideoTransformer3DModel': lambda model_cls, weights: weights, 'SanaTransformer2DModel': lambda model_cls, weights: weights,
'SAPIPhotoGenTransformer2DModel': lambda model_cls, weights: weights, 'SAPITransformer2DModel': lambda model_cls, weights: weights, 'SapienImageGenTransformer2DModel': lambda model_cls, weights: weights,
'SapiensVideoGenVideoTransformer3DModel': lambda model_cls, weights: weights}
def _maybe_adjust_config(config):
    rank_pattern = config['rank_pattern'].copy()
    target_modules = config['target_modules']
    original_r = config['r']
    for key in list(rank_pattern.keys()):
        key_rank = rank_pattern[key]
        exact_matches = [mod for mod in target_modules if mod == key]
        substring_matches = [mod for mod in target_modules if key in mod and mod != key]
        ambiguous_key = key
        if exact_matches and substring_matches:
            config['r'] = key_rank
            del config['rank_pattern'][key]
            for mod in substring_matches:
                if mod not in config['rank_pattern']: config['rank_pattern'][mod] = original_r
            for mod in target_modules:
                if mod != ambiguous_key and mod not in config['rank_pattern']: config['rank_pattern'][mod] = original_r
    has_different_ranks = len(config['rank_pattern']) > 1 and list(config['rank_pattern'])[0] != config['r']
    if has_different_ranks:
        config['lora_alpha'] = config['r']
        alpha_pattern = {}
        for module_name, rank in config['rank_pattern'].items(): alpha_pattern[module_name] = rank
        config['alpha_pattern'] = alpha_pattern
    return config
class PeftAdapterMixin:
    _hf_peft_config_loaded = False
    @classmethod
    def _optionally_disable_offloading(cls, _pipeline):
        """Returns:"""
        return _func_optionally_disable_offloading(_pipeline=_pipeline)
    def load_lora_adapter(self, pretrained_model_name_or_path_or_dict, prefix='transformer', **kwargs):
        from peft import LoraConfig, inject_adapter_in_model, set_peft_model_state_dict
        from peft.tuners.tuners_utils import BaseTunerLayer
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        adapter_name = kwargs.pop('adapter_name', None)
        network_alphas = kwargs.pop('network_alphas', None)
        _pipeline = kwargs.pop('_pipeline', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', False)
        allow_pickle = False
        if low_cpu_mem_usage and is_peft_version('<=', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        if network_alphas is not None and prefix is None: raise ValueError('`network_alphas` cannot be None when `prefix` is None.')
        if prefix is not None:
            keys = list(state_dict.keys())
            model_keys = [k for k in keys if k.startswith(f'{prefix}.')]
            if len(model_keys) > 0: state_dict = {k.replace(f'{prefix}.', ''): v for k, v in state_dict.items() if k in model_keys}
        if len(state_dict) > 0:
            if adapter_name in getattr(self, 'peft_config', {}): raise ValueError(f'Adapter name {adapter_name} already in use in the model - please select a new adapter name.')
            first_key = next(iter(state_dict.keys()))
            if 'lora_A' not in first_key: state_dict = convert_unet_state_dict_to_peft(state_dict)
            rank = {}
            for key, val in state_dict.items():
                if 'lora_B' in key and val.ndim > 1: rank[key] = val.shape[1]
            if network_alphas is not None and len(network_alphas) >= 1:
                alpha_keys = [k for k in network_alphas.keys() if k.startswith(f'{prefix}.')]
                network_alphas = {k.replace(f'{prefix}.', ''): v for k, v in network_alphas.items() if k in alpha_keys}
            lora_config_kwargs = get_peft_kwargs(rank, network_alpha_dict=network_alphas, peft_state_dict=state_dict)
            lora_config_kwargs = _maybe_adjust_config(lora_config_kwargs)
            if 'use_dora' in lora_config_kwargs:
                if lora_config_kwargs['use_dora']:
                    if is_peft_version('<', '0.9.0'): raise ValueError('You need `peft` 0.9.0 at least to use DoRA-enabled LoRAs. Please upgrade your installation of `peft`.')
                elif is_peft_version('<', '0.9.0'): lora_config_kwargs.pop('use_dora')
            if 'lora_bias' in lora_config_kwargs:
                if lora_config_kwargs['lora_bias']:
                    if is_peft_version('<=', '0.13.2'): raise ValueError('You need `peft` 0.14.0 at least to use `lora_bias` in LoRAs. Please upgrade your installation of `peft`.')
                elif is_peft_version('<=', '0.13.2'): lora_config_kwargs.pop('lora_bias')
            lora_config = LoraConfig(**lora_config_kwargs)
            if adapter_name is None: adapter_name = get_adapter_name(self)
            is_model_cpu_offload, is_sequential_cpu_offload = self._optionally_disable_offloading(_pipeline)
            peft_kwargs = {}
            if is_peft_version('>=', '0.13.1'): peft_kwargs['low_cpu_mem_usage'] = low_cpu_mem_usage
            try:
                inject_adapter_in_model(lora_config, self, adapter_name=adapter_name, **peft_kwargs)
                incompatible_keys = set_peft_model_state_dict(self, state_dict, adapter_name, **peft_kwargs)
            except RuntimeError as e:
                for module in self.modules():
                    if isinstance(module, BaseTunerLayer):
                        active_adapters = module.active_adapters
                        for active_adapter in active_adapters:
                            if adapter_name in active_adapter: module.delete_adapter(adapter_name)
                self.peft_config.pop(adapter_name)
                raise
            warn_msg = ''
            if incompatible_keys is not None:
                unexpected_keys = getattr(incompatible_keys, 'unexpected_keys', None)
                if unexpected_keys:
                    lora_unexpected_keys = [k for k in unexpected_keys if 'lora_' in k and adapter_name in k]
                    if lora_unexpected_keys: warn_msg = f"Loading adapter weights from state_dict led to unexpected keys found in the model: {', '.join(lora_unexpected_keys)}. "
                missing_keys = getattr(incompatible_keys, 'missing_keys', None)
                if missing_keys:
                    lora_missing_keys = [k for k in missing_keys if 'lora_' in k and adapter_name in k]
                    if lora_missing_keys: warn_msg += f"Loading adapter weights from state_dict led to missing keys in the model: {', '.join(lora_missing_keys)}."
            if is_model_cpu_offload: _pipeline.enable_model_cpu_offload()
            elif is_sequential_cpu_offload: _pipeline.enable_sequential_cpu_offload()
    def save_lora_adapter(self, save_directory, adapter_name: str='default', upcast_before_saving: bool=False, safe_serialization: bool=True, weight_name: Optional[str]=None):
        from peft.utils import get_peft_model_state_dict
        from .lora_base import LORA_WEIGHT_NAME, LORA_WEIGHT_NAME_SAFE
        if adapter_name is None: adapter_name = get_adapter_name(self)
        if adapter_name not in getattr(self, 'peft_config', {}): raise ValueError(f'Adapter name {adapter_name} not found in the model.')
        lora_layers_to_save = get_peft_model_state_dict(self.to(dtype=torch.float32 if upcast_before_saving else None), adapter_name=adapter_name)
        if os.path.isfile(save_directory): raise ValueError(f'Provided path ({save_directory}) should be a directory, not a file')
        if safe_serialization:
            def save_function(weights, filename): return safetensors.torch.save_file(weights, filename, metadata={'format': 'pt'})
        else: save_function = torch.save
        os.makedirs(save_directory, exist_ok=True)
        if weight_name is None:
            if safe_serialization: weight_name = LORA_WEIGHT_NAME_SAFE
            else: weight_name = LORA_WEIGHT_NAME
        save_path = Path(save_directory, weight_name).as_posix()
        save_function(lora_layers_to_save, save_path)
    def set_adapters(self, adapter_names: Union[List[str], str], weights: Optional[Union[float, Dict, List[float], List[Dict], List[None]]]=None):
        """Args:"""
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for `set_adapters()`.')
        adapter_names = [adapter_names] if isinstance(adapter_names, str) else adapter_names
        if not isinstance(weights, list): weights = [weights] * len(adapter_names)
        if len(adapter_names) != len(weights): raise ValueError(f'Length of adapter names {len(adapter_names)} is not equal to the length of their weights {len(weights)}.')
        weights = [w if w is not None else 1.0 for w in weights]
        scale_expansion_fn = _SET_ADAPTER_SCALE_FN_MAPPING[self.__class__.__name__]
        weights = scale_expansion_fn(self, weights)
        set_weights_and_activate_adapters(self, adapter_names, weights)
    def add_adapter(self, adapter_config, adapter_name: str='default') -> None:
        """Args:"""
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not is_peft_available(): raise ImportError('PEFT is not available. Please install PEFT to use this function: `pip install peft`.')
        from peft import PeftConfig, inject_adapter_in_model
        if not self._hf_peft_config_loaded: self._hf_peft_config_loaded = True
        elif adapter_name in self.peft_config: raise ValueError(f'Adapter with name {adapter_name} already exists. Please use a different name.')
        if not isinstance(adapter_config, PeftConfig): raise ValueError(f'adapter_config should be an instance of PeftConfig. Got {type(adapter_config)} instead.')
        adapter_config.base_model_name_or_path = None
        inject_adapter_in_model(adapter_config, self, adapter_name)
        self.set_adapter(adapter_name)
    def set_adapter(self, adapter_name: Union[str, List[str]]) -> None:
        """Args:"""
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError('No adapter loaded. Please load an adapter first.')
        if isinstance(adapter_name, str): adapter_name = [adapter_name]
        missing = set(adapter_name) - set(self.peft_config)
        if len(missing) > 0: raise ValueError(f"Following adapter(s) could not be found: {', '.join(missing)}. Make sure you are passing the correct adapter name(s). current loaded adapters are: {list(self.peft_config.keys())}")
        from peft.tuners.tuners_utils import BaseTunerLayer
        _adapters_has_been_set = False
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, 'set_adapter'): module.set_adapter(adapter_name)
                elif not hasattr(module, 'set_adapter') and len(adapter_name) != 1: raise ValueError('You are trying to set multiple adapters and you have a PEFT version that does not support multi-adapter inference. Please upgrade to the latest version of PEFT. `pip install -U peft` or `pip install -U git+https://github.com/huggingface/peft.git`')
                else: module.active_adapter = adapter_name
                _adapters_has_been_set = True
        if not _adapters_has_been_set: raise ValueError('Did not succeeded in setting the adapter. Please make sure you are using a model that supports adapters.')
    def disable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError('No adapter loaded. Please load an adapter first.')
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, 'enable_adapters'): module.enable_adapters(enabled=False)
                else: module.disable_adapters = True
    def enable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError('No adapter loaded. Please load an adapter first.')
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, 'enable_adapters'): module.enable_adapters(enabled=True)
                else: module.disable_adapters = False
    def active_adapters(self) -> List[str]:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not is_peft_available(): raise ImportError('PEFT is not available. Please install PEFT to use this function: `pip install peft`.')
        if not self._hf_peft_config_loaded: raise ValueError('No adapter loaded. Please load an adapter first.')
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer): return module.active_adapter
    def fuse_lora(self, lora_scale=1.0, safe_fusing=False, adapter_names=None):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for `fuse_lora()`.')
        self.lora_scale = lora_scale
        self._safe_fusing = safe_fusing
        self.apply(partial(self._fuse_lora_apply, adapter_names=adapter_names))
    def _fuse_lora_apply(self, module, adapter_names=None):
        from peft.tuners.tuners_utils import BaseTunerLayer
        merge_kwargs = {'safe_merge': self._safe_fusing}
        if isinstance(module, BaseTunerLayer):
            if self.lora_scale != 1.0: module.scale_layer(self.lora_scale)
            supported_merge_kwargs = list(inspect.signature(module.merge).parameters)
            if 'adapter_names' in supported_merge_kwargs: merge_kwargs['adapter_names'] = adapter_names
            elif 'adapter_names' not in supported_merge_kwargs and adapter_names is not None: raise ValueError('The `adapter_names` argument is not supported with your PEFT version. Please upgrade to the latest version of PEFT. `pip install -U peft`')
            module.merge(**merge_kwargs)
    def unfuse_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for `unfuse_lora()`.')
        self.apply(self._unfuse_lora_apply)
    def _unfuse_lora_apply(self, module):
        from peft.tuners.tuners_utils import BaseTunerLayer
        if isinstance(module, BaseTunerLayer): module.unmerge()
    def unload_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for `unload_lora()`.')
        from ..utils import recurse_remove_peft_layers
        recurse_remove_peft_layers(self)
        if hasattr(self, 'peft_config'): del self.peft_config
    def disable_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        set_adapter_layers(self, enabled=False)
    def enable_lora(self):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        set_adapter_layers(self, enabled=True)
    def delete_adapters(self, adapter_names: Union[List[str], str]):
        """Args:"""
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        if isinstance(adapter_names, str): adapter_names = [adapter_names]
        for adapter_name in adapter_names:
            delete_adapter_layers(self, adapter_name)
            if hasattr(self, 'peft_config'): self.peft_config.pop(adapter_name, None)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
