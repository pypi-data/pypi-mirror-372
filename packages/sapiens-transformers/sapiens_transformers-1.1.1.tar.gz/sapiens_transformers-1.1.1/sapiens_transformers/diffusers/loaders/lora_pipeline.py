'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .lora_conversion_utils import (_convert_bfl_flux_control_lora_to_diffusers, _convert_bfl_sapi_photogen_control_lora_to_diffusers, _convert_hunyuan_video_lora_to_diffusers, _convert_kohya_flux_lora_to_diffusers,
_convert_kohya_sapi_photogen_lora_to_diffusers, _convert_non_diffusers_lora_to_diffusers, _convert_xlabs_flux_lora_to_diffusers, _convert_xlabs_sapi_photogen_lora_to_diffusers, _maybe_map_sgm_blocks_to_diffusers)
from ..utils import USE_PEFT_BACKEND, deprecate, get_submodule_by_name, is_peft_available, is_peft_version, is_torch_version, is_transformers_available, is_sapiens_transformers_version
from .lora_base import LORA_WEIGHT_NAME, LORA_WEIGHT_NAME_SAFE, LoraBaseMixin, _fetch_state_dict, _load_lora_into_text_encoder
from typing import Callable, Dict, List, Optional, Union
from huggingface_hub.utils import validate_hf_hub_args
import torch
import os
_LOW_CPU_MEM_USAGE_DEFAULT_LORA = False
if is_torch_version('>=', '1.9.0'):
    if is_peft_available() and is_peft_version('>=', '0.13.1') and is_transformers_available() and is_sapiens_transformers_version('>', '1.0.0'): _LOW_CPU_MEM_USAGE_DEFAULT_LORA = True
TEXT_ENCODER_NAME = 'text_encoder'
UNET_NAME = 'unet'
TRANSFORMER_NAME = 'transformer'
_MODULE_NAME_TO_ATTRIBUTE_MAP_FLUX = _MODULE_NAME_TO_ATTRIBUTE_MAP_SAPI_PHOTOGEN = {'x_embedder': 'in_channels'}
class StableDiffusionLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['unet', 'text_encoder']
    unet_name = UNET_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict, network_alphas = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_unet(state_dict, network_alphas=network_alphas, unet=getattr(self, self.unet_name) if not hasattr(self, 'unet') else self.unet, adapter_name=adapter_name,
        _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        self.load_lora_into_text_encoder(state_dict, network_alphas=network_alphas, text_encoder=getattr(self, self.text_encoder_name) if not hasattr(self, 'text_encoder') else self.text_encoder,
        lora_scale=self.lora_scale, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        unet_config = kwargs.pop('unet_config', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors,
        local_files_only=local_files_only, cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        network_alphas = None
        if all((k.startswith('lora_te_') or k.startswith('lora_unet_') or k.startswith('lora_te1_') or k.startswith('lora_te2_') for k in state_dict.keys())):
            if unet_config is not None: state_dict = _maybe_map_sgm_blocks_to_diffusers(state_dict, unet_config)
            state_dict, network_alphas = _convert_non_diffusers_lora_to_diffusers(state_dict)
        return (state_dict, network_alphas)
    @classmethod
    def load_lora_into_unet(cls, state_dict, network_alphas, unet, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        keys = list(state_dict.keys())
        only_text_encoder = all((key.startswith(cls.text_encoder_name) for key in keys))
        if not only_text_encoder: unet.load_lora_adapter(state_dict, prefix=cls.unet_name, network_alphas=network_alphas, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], unet_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, text_encoder_lora_layers: Dict[str, torch.nn.Module]=None,
    is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (unet_lora_layers or text_encoder_lora_layers): raise ValueError('You must pass at least one of `unet_lora_layers` and `text_encoder_lora_layers`.')
        if unet_lora_layers: state_dict.update(cls.pack_weights(unet_lora_layers, cls.unet_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, cls.text_encoder_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['unet', 'text_encoder'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['unet', 'text_encoder'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class StableDiffusionXLLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['unet', 'text_encoder', 'text_encoder_2']
    unet_name = UNET_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name: Optional[str]=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict, network_alphas = self.lora_state_dict(pretrained_model_name_or_path_or_dict, unet_config=self.unet.config, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_unet(state_dict, network_alphas=network_alphas, unet=self.unet, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder.' in k}
        if len(text_encoder_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_state_dict, network_alphas=network_alphas, text_encoder=self.text_encoder, prefix='text_encoder', lora_scale=self.lora_scale,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_2_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder_2.' in k}
        if len(text_encoder_2_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_2_state_dict, network_alphas=network_alphas, text_encoder=self.text_encoder_2, prefix='text_encoder_2',
        lora_scale=self.lora_scale, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        unet_config = kwargs.pop('unet_config', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only,
        cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        network_alphas = None
        if all((k.startswith('lora_te_') or k.startswith('lora_unet_') or k.startswith('lora_te1_') or k.startswith('lora_te2_') for k in state_dict.keys())):
            if unet_config is not None: state_dict = _maybe_map_sgm_blocks_to_diffusers(state_dict, unet_config)
            state_dict, network_alphas = _convert_non_diffusers_lora_to_diffusers(state_dict)
        return (state_dict, network_alphas)
    @classmethod
    def load_lora_into_unet(cls, state_dict, network_alphas, unet, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        keys = list(state_dict.keys())
        only_text_encoder = all((key.startswith(cls.text_encoder_name) for key in keys))
        if not only_text_encoder: unet.load_lora_adapter(state_dict, prefix=cls.unet_name, network_alphas=network_alphas, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], unet_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, text_encoder_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None,
    text_encoder_2_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (unet_lora_layers or text_encoder_lora_layers or text_encoder_2_lora_layers): raise ValueError('You must pass at least one of `unet_lora_layers`, `text_encoder_lora_layers` or `text_encoder_2_lora_layers`.')
        if unet_lora_layers: state_dict.update(cls.pack_weights(unet_lora_layers, 'unet'))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, 'text_encoder'))
        if text_encoder_2_lora_layers: state_dict.update(cls.pack_weights(text_encoder_2_lora_layers, 'text_encoder_2'))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['unet', 'text_encoder', 'text_encoder_2'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['unet', 'text_encoder', 'text_encoder_2'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class SD3LoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer', 'text_encoder', 'text_encoder_2']
    transformer_name = TRANSFORMER_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only,
        cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        transformer_state_dict = {k: v for k, v in state_dict.items() if 'transformer.' in k}
        if len(transformer_state_dict) > 0: self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder.' in k}
        if len(text_encoder_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_state_dict, network_alphas=None, text_encoder=self.text_encoder, prefix='text_encoder', lora_scale=self.lora_scale,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_2_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder_2.' in k}
        if len(text_encoder_2_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_2_state_dict, network_alphas=None, text_encoder=self.text_encoder_2, prefix='text_encoder_2',
        lora_scale=self.lora_scale, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, torch.nn.Module]=None, text_encoder_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None,
    text_encoder_2_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (transformer_lora_layers or text_encoder_lora_layers or text_encoder_2_lora_layers): raise ValueError('You must pass at least one of `transformer_lora_layers`, `text_encoder_lora_layers`, `text_encoder_2_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, 'text_encoder'))
        if text_encoder_2_lora_layers: state_dict.update(cls.pack_weights(text_encoder_2_lora_layers, 'text_encoder_2'))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer', 'text_encoder', 'text_encoder_2'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer', 'text_encoder', 'text_encoder_2'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class FluxLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer', 'text_encoder']
    transformer_name = TRANSFORMER_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    _control_lora_supported_norm_keys = ['norm_q', 'norm_k', 'norm_added_q', 'norm_added_k']
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], return_alphas: bool=False, **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only,
        cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        is_kohya = any(('.lora_down.weight' in k for k in state_dict))
        if is_kohya:
            state_dict = _convert_kohya_flux_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        is_xlabs = any(('processor' in k for k in state_dict))
        if is_xlabs:
            state_dict = _convert_xlabs_flux_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        is_bfl_control = any(('query_norm.scale' in k for k in state_dict))
        if is_bfl_control:
            state_dict = _convert_bfl_flux_control_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        keys = list(state_dict.keys())
        network_alphas = {}
        for k in keys:
            if 'alpha' in k:
                alpha_value = state_dict.get(k)
                if torch.is_tensor(alpha_value) and torch.is_floating_point(alpha_value) or isinstance(alpha_value, float): network_alphas[k] = state_dict.pop(k)
                else: raise ValueError(f'The alpha key ({k}) seems to be incorrect. If you think this error is unexpected, please open as issue.')
        if return_alphas: return (state_dict, network_alphas)
        else: return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict, network_alphas = self.lora_state_dict(pretrained_model_name_or_path_or_dict, return_alphas=True, **kwargs)
        has_lora_keys = any(('lora' in key for key in state_dict.keys()))
        has_norm_keys = any((norm_key in key for key in state_dict.keys() for norm_key in self._control_lora_supported_norm_keys))
        if not (has_lora_keys or has_norm_keys): raise ValueError('Invalid LoRA checkpoint.')
        transformer_lora_state_dict = {k: state_dict.pop(k) for k in list(state_dict.keys()) if 'transformer.' in k and 'lora' in k}
        transformer_norm_state_dict = {k: state_dict.pop(k) for k in list(state_dict.keys()) if 'transformer.' in k and any((norm_key in k for norm_key in self._control_lora_supported_norm_keys))}
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        has_param_with_expanded_shape = self._maybe_expand_transformer_param_shape_or_error_(transformer, transformer_lora_state_dict, transformer_norm_state_dict)
        transformer_lora_state_dict = self._maybe_expand_lora_state_dict(transformer=transformer, lora_state_dict=transformer_lora_state_dict)
        if len(transformer_lora_state_dict) > 0: self.load_lora_into_transformer(transformer_lora_state_dict, network_alphas=network_alphas, transformer=transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        if len(transformer_norm_state_dict) > 0: transformer._transformer_norm_layers = self._load_norm_into_transformer(transformer_norm_state_dict, transformer=transformer, discard_original_layers=False)
        text_encoder_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder.' in k}
        if len(text_encoder_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_state_dict, network_alphas=network_alphas, text_encoder=self.text_encoder, prefix='text_encoder', lora_scale=self.lora_scale,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, network_alphas, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        keys = list(state_dict.keys())
        transformer_present = any((key.startswith(cls.transformer_name) for key in keys))
        if transformer_present: transformer.load_lora_adapter(state_dict, network_alphas=network_alphas, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def _load_norm_into_transformer(cls, state_dict, transformer, prefix=None, discard_original_layers=False) -> Dict[str, torch.Tensor]:
        prefix = prefix or cls.transformer_name
        for key in list(state_dict.keys()):
            if key.split('.')[0] == prefix: state_dict[key[len(f'{prefix}.'):]] = state_dict.pop(key)
        transformer_state_dict = transformer.state_dict()
        transformer_keys = set(transformer_state_dict.keys())
        state_dict_keys = set(state_dict.keys())
        extra_keys = list(state_dict_keys - transformer_keys)
        for key in extra_keys: state_dict.pop(key)
        overwritten_layers_state_dict = {}
        if not discard_original_layers:
            for key in state_dict.keys(): overwritten_layers_state_dict[key] = transformer_state_dict[key].clone()
        incompatible_keys = transformer.load_state_dict(state_dict, strict=False)
        unexpected_keys = getattr(incompatible_keys, 'unexpected_keys', None)
        if unexpected_keys:
            if any((norm_key in k for k in unexpected_keys for norm_key in cls._control_lora_supported_norm_keys)): raise ValueError(f'Found {unexpected_keys} as unexpected keys while trying to load norm layers into the transformer.')
        return overwritten_layers_state_dict
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, text_encoder_lora_layers: Dict[str, torch.nn.Module]=None, is_main_process: bool=True,
    weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (transformer_lora_layers or text_encoder_lora_layers): raise ValueError('You must pass at least one of `transformer_lora_layers` and `text_encoder_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, cls.text_encoder_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer', 'text_encoder'], **kwargs):
        """Args:"""
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        if hasattr(transformer, '_transformer_norm_layers') and transformer._transformer_norm_layers: transformer.load_state_dict(transformer._transformer_norm_layers, strict=False)
        super().unfuse_lora(components=components)
    def unload_lora_weights(self, reset_to_overwritten_params=False):
        """Examples:"""
        super().unload_lora_weights()
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        if hasattr(transformer, '_transformer_norm_layers') and transformer._transformer_norm_layers:
            transformer.load_state_dict(transformer._transformer_norm_layers, strict=False)
            transformer._transformer_norm_layers = None
        if reset_to_overwritten_params and getattr(transformer, '_overwritten_params', None) is not None:
            overwritten_params = transformer._overwritten_params
            module_names = set()
            for param_name in overwritten_params:
                if param_name.endswith('.weight'): module_names.add(param_name.replace('.weight', ''))
            for name, module in transformer.named_modules():
                if isinstance(module, torch.nn.Linear) and name in module_names:
                    module_weight = module.weight.data
                    module_bias = module.bias.data if module.bias is not None else None
                    bias = module_bias is not None
                    parent_module_name, _, current_module_name = name.rpartition('.')
                    parent_module = transformer.get_submodule(parent_module_name)
                    current_param_weight = overwritten_params[f'{name}.weight']
                    in_features, out_features = (current_param_weight.shape[1], current_param_weight.shape[0])
                    with torch.device('meta'): original_module = torch.nn.Linear(in_features, out_features, bias=bias, dtype=module_weight.dtype)
                    tmp_state_dict = {'weight': current_param_weight}
                    if module_bias is not None: tmp_state_dict.update({'bias': overwritten_params[f'{name}.bias']})
                    original_module.load_state_dict(tmp_state_dict, assign=True, strict=True)
                    setattr(parent_module, current_module_name, original_module)
                    del tmp_state_dict
                    if current_module_name in _MODULE_NAME_TO_ATTRIBUTE_MAP_FLUX:
                        attribute_name = _MODULE_NAME_TO_ATTRIBUTE_MAP_FLUX[current_module_name]
                        new_value = int(current_param_weight.shape[1])
                        old_value = getattr(transformer.config, attribute_name)
                        setattr(transformer.config, attribute_name, new_value)
    @classmethod
    def _maybe_expand_transformer_param_shape_or_error_(cls, transformer: torch.nn.Module, lora_state_dict=None, norm_state_dict=None, prefix=None) -> bool:
        state_dict = {}
        if lora_state_dict is not None: state_dict.update(lora_state_dict)
        if norm_state_dict is not None: state_dict.update(norm_state_dict)
        prefix = prefix or cls.transformer_name
        for key in list(state_dict.keys()):
            if key.split('.')[0] == prefix: state_dict[key[len(f'{prefix}.'):]] = state_dict.pop(key)
        has_param_with_shape_update = False
        overwritten_params = {}
        is_peft_loaded = getattr(transformer, 'peft_config', None) is not None
        for name, module in transformer.named_modules():
            if isinstance(module, torch.nn.Linear):
                module_weight = module.weight.data
                module_bias = module.bias.data if module.bias is not None else None
                bias = module_bias is not None
                lora_base_name = name.replace('.base_layer', '') if is_peft_loaded else name
                lora_A_weight_name = f'{lora_base_name}.lora_A.weight'
                lora_B_weight_name = f'{lora_base_name}.lora_B.weight'
                if lora_A_weight_name not in state_dict: continue
                in_features = state_dict[lora_A_weight_name].shape[1]
                out_features = state_dict[lora_B_weight_name].shape[0]
                module_weight_shape = cls._calculate_module_shape(model=transformer, base_module=module)
                if tuple(module_weight_shape) == (out_features, in_features): continue
                module_out_features, module_in_features = module_weight.shape
                debug_message = ''
                if in_features > module_in_features: debug_message += f'Expanding the nn.Linear input/output features for module="{name}" because the provided LoRA checkpoint contains higher number of features than expected. The number of input_features will be expanded from {module_in_features} to {in_features}'
                if out_features > module_out_features: debug_message += f', and the number of output features will be expanded from {module_out_features} to {out_features}.'
                else: debug_message += '.'
                if out_features > module_out_features or in_features > module_in_features:
                    has_param_with_shape_update = True
                    parent_module_name, _, current_module_name = name.rpartition('.')
                    parent_module = transformer.get_submodule(parent_module_name)
                    with torch.device('meta'): expanded_module = torch.nn.Linear(in_features, out_features, bias=bias, dtype=module_weight.dtype)
                    new_weight = torch.zeros_like(expanded_module.weight.data, device=module_weight.device, dtype=module_weight.dtype)
                    slices = tuple((slice(0, dim) for dim in module_weight.shape))
                    new_weight[slices] = module_weight
                    tmp_state_dict = {'weight': new_weight}
                    if module_bias is not None: tmp_state_dict['bias'] = module_bias
                    expanded_module.load_state_dict(tmp_state_dict, strict=True, assign=True)
                    setattr(parent_module, current_module_name, expanded_module)
                    del tmp_state_dict
                    if current_module_name in _MODULE_NAME_TO_ATTRIBUTE_MAP_FLUX:
                        attribute_name = _MODULE_NAME_TO_ATTRIBUTE_MAP_FLUX[current_module_name]
                        new_value = int(expanded_module.weight.data.shape[1])
                        old_value = getattr(transformer.config, attribute_name)
                        setattr(transformer.config, attribute_name, new_value)
                    overwritten_params[f'{current_module_name}.weight'] = module_weight
                    if module_bias is not None: overwritten_params[f'{current_module_name}.bias'] = module_bias
        if len(overwritten_params) > 0: transformer._overwritten_params = overwritten_params
        return has_param_with_shape_update
    @classmethod
    def _maybe_expand_lora_state_dict(cls, transformer, lora_state_dict):
        expanded_module_names = set()
        transformer_state_dict = transformer.state_dict()
        prefix = f'{cls.transformer_name}.'
        lora_module_names = [key[:-len('.lora_A.weight')] for key in lora_state_dict if key.endswith('.lora_A.weight')]
        lora_module_names = [name[len(prefix):] for name in lora_module_names if name.startswith(prefix)]
        lora_module_names = sorted(set(lora_module_names))
        transformer_module_names = sorted({name for name, _ in transformer.named_modules()})
        unexpected_modules = set(lora_module_names) - set(transformer_module_names)
        is_peft_loaded = getattr(transformer, 'peft_config', None) is not None
        for k in lora_module_names:
            if k in unexpected_modules: continue
            base_param_name = f"{k.replace(prefix, '')}.base_layer.weight" if is_peft_loaded and f"{k.replace(prefix, '')}.base_layer.weight" in transformer_state_dict else f"{k.replace(prefix, '')}.weight"
            base_weight_param = transformer_state_dict[base_param_name]
            lora_A_param = lora_state_dict[f'{prefix}{k}.lora_A.weight']
            base_module_shape = cls._calculate_module_shape(model=transformer, base_weight_param_name=base_param_name)
            if base_module_shape[1] > lora_A_param.shape[1]:
                shape = (lora_A_param.shape[0], base_weight_param.shape[1])
                expanded_state_dict_weight = torch.zeros(shape, device=base_weight_param.device)
                expanded_state_dict_weight[:, :lora_A_param.shape[1]].copy_(lora_A_param)
                lora_state_dict[f'{prefix}{k}.lora_A.weight'] = expanded_state_dict_weight
                expanded_module_names.add(k)
            elif base_module_shape[1] < lora_A_param.shape[1]: raise NotImplementedError(f'This LoRA param ({k}.lora_A.weight) has an incompatible shape {lora_A_param.shape}. Please open an issue to file for a feature request - https://github.com/huggingface/diffusers/issues/new.')
        return lora_state_dict
    @staticmethod
    def _calculate_module_shape(model: 'torch.nn.Module', base_module: 'torch.nn.Linear'=None, base_weight_param_name: str=None) -> 'torch.Size':
        def _get_weight_shape(weight: torch.Tensor): return weight.quant_state.shape if weight.__class__.__name__ == 'Params4bit' else weight.shape
        if base_module is not None: return _get_weight_shape(base_module.weight)
        elif base_weight_param_name is not None:
            if not base_weight_param_name.endswith('.weight'): raise ValueError(f"Invalid `base_weight_param_name` passed as it does not end with '.weight' base_weight_param_name={base_weight_param_name!r}.")
            module_path = base_weight_param_name.rsplit('.weight', 1)[0]
            submodule = get_submodule_by_name(model, module_path)
            return _get_weight_shape(submodule.weight)
        raise ValueError('Either `base_module` or `base_weight_param_name` must be provided.')
class AmusedLoraLoaderMixin(StableDiffusionLoraLoaderMixin):
    _lora_loadable_modules = ['transformer', 'text_encoder']
    transformer_name = TRANSFORMER_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    @classmethod
    def load_lora_into_transformer(cls, state_dict, network_alphas, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        keys = list(state_dict.keys())
        transformer_present = any((key.startswith(cls.transformer_name) for key in keys))
        if transformer_present: transformer.load_lora_adapter(state_dict, network_alphas=network_alphas, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], text_encoder_lora_layers: Dict[str, torch.nn.Module]=None, transformer_lora_layers: Dict[str, torch.nn.Module]=None, is_main_process: bool=True,
    weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (transformer_lora_layers or text_encoder_lora_layers): raise ValueError('You must pass at least one of `transformer_lora_layers` or `text_encoder_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, cls.text_encoder_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
class CogVideoXLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class Mochi1LoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class LTXVideoLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class SanaLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class SAPIPhotoGenLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer', 'text_encoder']
    transformer_name = TRANSFORMER_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    _control_lora_supported_norm_keys = ['norm_q', 'norm_k', 'norm_added_q', 'norm_added_k']
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], return_alphas: bool=False, **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only,
        cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        is_kohya = any(('.lora_down.weight' in k for k in state_dict))
        if is_kohya:
            state_dict = _convert_kohya_sapi_photogen_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        is_xlabs = any(('processor' in k for k in state_dict))
        if is_xlabs:
            state_dict = _convert_xlabs_sapi_photogen_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        is_bfl_control = any(('query_norm.scale' in k for k in state_dict))
        if is_bfl_control:
            state_dict = _convert_bfl_sapi_photogen_control_lora_to_diffusers(state_dict)
            return (state_dict, None) if return_alphas else state_dict
        keys = list(state_dict.keys())
        network_alphas = {}
        for k in keys:
            if 'alpha' in k:
                alpha_value = state_dict.get(k)
                if torch.is_tensor(alpha_value) and torch.is_floating_point(alpha_value) or isinstance(alpha_value, float): network_alphas[k] = state_dict.pop(k)
                else: raise ValueError(f'The alpha key ({k}) seems to be incorrect. If you think this error is unexpected, please open as issue.')
        if return_alphas: return (state_dict, network_alphas)
        else: return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict, network_alphas = self.lora_state_dict(pretrained_model_name_or_path_or_dict, return_alphas=True, **kwargs)
        has_lora_keys = any(('lora' in key for key in state_dict.keys()))
        has_norm_keys = any((norm_key in key for key in state_dict.keys() for norm_key in self._control_lora_supported_norm_keys))
        if not (has_lora_keys or has_norm_keys): raise ValueError('Invalid LoRA checkpoint.')
        transformer_lora_state_dict = {k: state_dict.pop(k) for k in list(state_dict.keys()) if 'transformer.' in k and 'lora' in k}
        transformer_norm_state_dict = {k: state_dict.pop(k) for k in list(state_dict.keys()) if 'transformer.' in k and any((norm_key in k for norm_key in self._control_lora_supported_norm_keys))}
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        has_param_with_expanded_shape = self._maybe_expand_transformer_param_shape_or_error_(transformer, transformer_lora_state_dict, transformer_norm_state_dict)
        transformer_lora_state_dict = self._maybe_expand_lora_state_dict(transformer=transformer, lora_state_dict=transformer_lora_state_dict)
        if len(transformer_lora_state_dict) > 0: self.load_lora_into_transformer(transformer_lora_state_dict, network_alphas=network_alphas, transformer=transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        if len(transformer_norm_state_dict) > 0: transformer._transformer_norm_layers = self._load_norm_into_transformer(transformer_norm_state_dict, transformer=transformer, discard_original_layers=False)
        text_encoder_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder.' in k}
        if len(text_encoder_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_state_dict, network_alphas=network_alphas, text_encoder=self.text_encoder, prefix='text_encoder', lora_scale=self.lora_scale,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, network_alphas, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and (not is_peft_version('>=', '0.13.1')): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        keys = list(state_dict.keys())
        transformer_present = any((key.startswith(cls.transformer_name) for key in keys))
        if transformer_present: transformer.load_lora_adapter(state_dict, network_alphas=network_alphas, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def _load_norm_into_transformer(cls, state_dict, transformer, prefix=None, discard_original_layers=False) -> Dict[str, torch.Tensor]:
        prefix = prefix or cls.transformer_name
        for key in list(state_dict.keys()):
            if key.split('.')[0] == prefix: state_dict[key[len(f'{prefix}.'):]] = state_dict.pop(key)
        transformer_state_dict = transformer.state_dict()
        transformer_keys = set(transformer_state_dict.keys())
        state_dict_keys = set(state_dict.keys())
        extra_keys = list(state_dict_keys - transformer_keys)
        for key in extra_keys: state_dict.pop(key)
        overwritten_layers_state_dict = {}
        if not discard_original_layers:
            for key in state_dict.keys(): overwritten_layers_state_dict[key] = transformer_state_dict[key].clone()
        incompatible_keys = transformer.load_state_dict(state_dict, strict=False)
        unexpected_keys = getattr(incompatible_keys, 'unexpected_keys', None)
        if unexpected_keys:
            if any((norm_key in k for k in unexpected_keys for norm_key in cls._control_lora_supported_norm_keys)): raise ValueError(f'Found {unexpected_keys} as unexpected keys while trying to load norm layers into the transformer.')
        return overwritten_layers_state_dict
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, text_encoder_lora_layers: Dict[str, torch.nn.Module]=None, is_main_process: bool=True,
    weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (transformer_lora_layers or text_encoder_lora_layers): raise ValueError('You must pass at least one of `transformer_lora_layers` and `text_encoder_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, cls.text_encoder_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer', 'text_encoder'], **kwargs):
        """Args:"""
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        if hasattr(transformer, '_transformer_norm_layers') and transformer._transformer_norm_layers: transformer.load_state_dict(transformer._transformer_norm_layers, strict=False)
        super().unfuse_lora(components=components)
    def unload_lora_weights(self, reset_to_overwritten_params=False):
        """Examples:"""
        super().unload_lora_weights()
        transformer = getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer
        if hasattr(transformer, '_transformer_norm_layers') and transformer._transformer_norm_layers:
            transformer.load_state_dict(transformer._transformer_norm_layers, strict=False)
            transformer._transformer_norm_layers = None
        if reset_to_overwritten_params and getattr(transformer, '_overwritten_params', None) is not None:
            overwritten_params = transformer._overwritten_params
            module_names = set()
            for param_name in overwritten_params:
                if param_name.endswith('.weight'): module_names.add(param_name.replace('.weight', ''))
            for name, module in transformer.named_modules():
                if isinstance(module, torch.nn.Linear) and name in module_names:
                    module_weight = module.weight.data
                    module_bias = module.bias.data if module.bias is not None else None
                    bias = module_bias is not None
                    parent_module_name, _, current_module_name = name.rpartition('.')
                    parent_module = transformer.get_submodule(parent_module_name)
                    current_param_weight = overwritten_params[f'{name}.weight']
                    in_features, out_features = (current_param_weight.shape[1], current_param_weight.shape[0])
                    with torch.device('meta'): original_module = torch.nn.Linear(in_features, out_features, bias=bias, dtype=module_weight.dtype)
                    tmp_state_dict = {'weight': current_param_weight}
                    if module_bias is not None: tmp_state_dict.update({'bias': overwritten_params[f'{name}.bias']})
                    original_module.load_state_dict(tmp_state_dict, assign=True, strict=True)
                    setattr(parent_module, current_module_name, original_module)
                    del tmp_state_dict
                    if current_module_name in _MODULE_NAME_TO_ATTRIBUTE_MAP_SAPI_PHOTOGEN:
                        attribute_name = _MODULE_NAME_TO_ATTRIBUTE_MAP_SAPI_PHOTOGEN[current_module_name]
                        new_value = int(current_param_weight.shape[1])
                        old_value = getattr(transformer.config, attribute_name)
                        setattr(transformer.config, attribute_name, new_value)
    @classmethod
    def _maybe_expand_transformer_param_shape_or_error_(cls, transformer: torch.nn.Module, lora_state_dict=None, norm_state_dict=None, prefix=None) -> bool:
        state_dict = {}
        if lora_state_dict is not None: state_dict.update(lora_state_dict)
        if norm_state_dict is not None: state_dict.update(norm_state_dict)
        prefix = prefix or cls.transformer_name
        for key in list(state_dict.keys()):
            if key.split('.')[0] == prefix: state_dict[key[len(f'{prefix}.'):]] = state_dict.pop(key)
        has_param_with_shape_update = False
        overwritten_params = {}
        is_peft_loaded = getattr(transformer, 'peft_config', None) is not None
        for name, module in transformer.named_modules():
            if isinstance(module, torch.nn.Linear):
                module_weight = module.weight.data
                module_bias = module.bias.data if module.bias is not None else None
                bias = module_bias is not None
                lora_base_name = name.replace('.base_layer', '') if is_peft_loaded else name
                lora_A_weight_name = f'{lora_base_name}.lora_A.weight'
                lora_B_weight_name = f'{lora_base_name}.lora_B.weight'
                if lora_A_weight_name not in state_dict: continue
                in_features = state_dict[lora_A_weight_name].shape[1]
                out_features = state_dict[lora_B_weight_name].shape[0]
                module_weight_shape = cls._calculate_module_shape(model=transformer, base_module=module)
                if tuple(module_weight_shape) == (out_features, in_features): continue
                module_out_features, module_in_features = module_weight.shape
                debug_message = ''
                if in_features > module_in_features: debug_message += f'Expanding the nn.Linear input/output features for module="{name}" because the provided LoRA checkpoint contains higher number of features than expected. The number of input_features will be expanded from {module_in_features} to {in_features}'
                if out_features > module_out_features: debug_message += f', and the number of output features will be expanded from {module_out_features} to {out_features}.'
                else: debug_message += '.'
                if out_features > module_out_features or in_features > module_in_features:
                    has_param_with_shape_update = True
                    parent_module_name, _, current_module_name = name.rpartition('.')
                    parent_module = transformer.get_submodule(parent_module_name)
                    with torch.device('meta'): expanded_module = torch.nn.Linear(in_features, out_features, bias=bias, dtype=module_weight.dtype)
                    new_weight = torch.zeros_like(expanded_module.weight.data, device=module_weight.device, dtype=module_weight.dtype)
                    slices = tuple((slice(0, dim) for dim in module_weight.shape))
                    new_weight[slices] = module_weight
                    tmp_state_dict = {'weight': new_weight}
                    if module_bias is not None: tmp_state_dict['bias'] = module_bias
                    expanded_module.load_state_dict(tmp_state_dict, strict=True, assign=True)
                    setattr(parent_module, current_module_name, expanded_module)
                    del tmp_state_dict
                    if current_module_name in _MODULE_NAME_TO_ATTRIBUTE_MAP_SAPI_PHOTOGEN:
                        attribute_name = _MODULE_NAME_TO_ATTRIBUTE_MAP_SAPI_PHOTOGEN[current_module_name]
                        new_value = int(expanded_module.weight.data.shape[1])
                        old_value = getattr(transformer.config, attribute_name)
                        setattr(transformer.config, attribute_name, new_value)
                    overwritten_params[f'{current_module_name}.weight'] = module_weight
                    if module_bias is not None: overwritten_params[f'{current_module_name}.bias'] = module_bias
        if len(overwritten_params) > 0: transformer._overwritten_params = overwritten_params
        return has_param_with_shape_update
    @classmethod
    def _maybe_expand_lora_state_dict(cls, transformer, lora_state_dict):
        expanded_module_names = set()
        transformer_state_dict = transformer.state_dict()
        prefix = f'{cls.transformer_name}.'
        lora_module_names = [key[:-len('.lora_A.weight')] for key in lora_state_dict if key.endswith('.lora_A.weight')]
        lora_module_names = [name[len(prefix):] for name in lora_module_names if name.startswith(prefix)]
        lora_module_names = sorted(set(lora_module_names))
        transformer_module_names = sorted({name for name, _ in transformer.named_modules()})
        unexpected_modules = set(lora_module_names) - set(transformer_module_names)
        is_peft_loaded = getattr(transformer, 'peft_config', None) is not None
        for k in lora_module_names:
            if k in unexpected_modules: continue
            base_param_name = f"{k.replace(prefix, '')}.base_layer.weight" if is_peft_loaded and f"{k.replace(prefix, '')}.base_layer.weight" in transformer_state_dict else f"{k.replace(prefix, '')}.weight"
            base_weight_param = transformer_state_dict[base_param_name]
            lora_A_param = lora_state_dict[f'{prefix}{k}.lora_A.weight']
            base_module_shape = cls._calculate_module_shape(model=transformer, base_weight_param_name=base_param_name)
            if base_module_shape[1] > lora_A_param.shape[1]:
                shape = (lora_A_param.shape[0], base_weight_param.shape[1])
                expanded_state_dict_weight = torch.zeros(shape, device=base_weight_param.device)
                expanded_state_dict_weight[:, :lora_A_param.shape[1]].copy_(lora_A_param)
                lora_state_dict[f'{prefix}{k}.lora_A.weight'] = expanded_state_dict_weight
                expanded_module_names.add(k)
            elif base_module_shape[1] < lora_A_param.shape[1]: raise NotImplementedError(f'This LoRA param ({k}.lora_A.weight) has an incompatible shape {lora_A_param.shape}. Please open an issue to file for a feature request - https://github.com/huggingface/diffusers/issues/new.')
        return lora_state_dict
    @staticmethod
    def _calculate_module_shape(model: 'torch.nn.Module', base_module: 'torch.nn.Linear'=None, base_weight_param_name: str=None) -> 'torch.Size':
        def _get_weight_shape(weight: torch.Tensor): return weight.quant_state.shape if weight.__class__.__name__ == 'Params4bit' else weight.shape
        if base_module is not None: return _get_weight_shape(base_module.weight)
        elif base_weight_param_name is not None:
            if not base_weight_param_name.endswith('.weight'): raise ValueError(f"Invalid `base_weight_param_name` passed as it does not end with '.weight' base_weight_param_name={base_weight_param_name!r}.")
            module_path = base_weight_param_name.rsplit('.weight', 1)[0]
            submodule = get_submodule_by_name(model, module_path)
            return _get_weight_shape(submodule.weight)
        raise ValueError('Either `base_module` or `base_weight_param_name` must be provided.')
class SAPILoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer', 'text_encoder', 'text_encoder_2']
    transformer_name = TRANSFORMER_NAME
    text_encoder_name = TEXT_ENCODER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only,
        cache_dir=cache_dir, force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        transformer_state_dict = {k: v for k, v in state_dict.items() if 'transformer.' in k}
        if len(transformer_state_dict) > 0: self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder.' in k}
        if len(text_encoder_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_state_dict, network_alphas=None, text_encoder=self.text_encoder, prefix='text_encoder', lora_scale=self.lora_scale,
        adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
        text_encoder_2_state_dict = {k: v for k, v in state_dict.items() if 'text_encoder_2.' in k}
        if len(text_encoder_2_state_dict) > 0: self.load_lora_into_text_encoder(text_encoder_2_state_dict, network_alphas=None, text_encoder=self.text_encoder_2, prefix='text_encoder_2',
        lora_scale=self.lora_scale, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_text_encoder(cls, state_dict, network_alphas, text_encoder, prefix=None, lora_scale=1.0, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False): _load_lora_into_text_encoder(state_dict=state_dict,
    network_alphas=network_alphas, lora_scale=lora_scale, text_encoder=text_encoder, prefix=prefix, text_encoder_name=cls.text_encoder_name, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, torch.nn.Module]=None, text_encoder_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None,
    text_encoder_2_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not (transformer_lora_layers or text_encoder_lora_layers or text_encoder_2_lora_layers): raise ValueError('You must pass at least one of `transformer_lora_layers`, `text_encoder_lora_layers`, `text_encoder_2_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        if text_encoder_lora_layers: state_dict.update(cls.pack_weights(text_encoder_lora_layers, 'text_encoder'))
        if text_encoder_2_lora_layers: state_dict.update(cls.pack_weights(text_encoder_2_lora_layers, 'text_encoder_2'))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer', 'text_encoder', 'text_encoder_2'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer', 'text_encoder', 'text_encoder_2'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class SapiensImageGenLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class SapiensVideoGenVideoLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class HunyuanVideoLoraLoaderMixin(LoraBaseMixin):
    _lora_loadable_modules = ['transformer']
    transformer_name = TRANSFORMER_NAME
    @classmethod
    @validate_hf_hub_args
    def lora_state_dict(cls, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], **kwargs):
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        weight_name = kwargs.pop('weight_name', None)
        use_safetensors = kwargs.pop('use_safetensors', None)
        allow_pickle = False
        if use_safetensors is None:
            use_safetensors = True
            allow_pickle = True
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dict = _fetch_state_dict(pretrained_model_name_or_path_or_dict=pretrained_model_name_or_path_or_dict, weight_name=weight_name, use_safetensors=use_safetensors, local_files_only=local_files_only, cache_dir=cache_dir,
        force_download=force_download, proxies=proxies, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent, allow_pickle=allow_pickle)
        is_dora_scale_present = any(('dora_scale' in k for k in state_dict))
        if is_dora_scale_present:
            warn_msg = "It seems like you are using a DoRA checkpoint that is not compatible in Diffusers at the moment. So, we are going to filter out the keys associated to 'dora_scale` from the state dict. If you think this is a mistake please open an issue https://github.com/huggingface/diffusers/issues/new."
            state_dict = {k: v for k, v in state_dict.items() if 'dora_scale' not in k}
        is_original_hunyuan_video = any(('img_attn_qkv' in k for k in state_dict))
        if is_original_hunyuan_video: state_dict = _convert_hunyuan_video_lora_to_diffusers(state_dict)
        return state_dict
    def load_lora_weights(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], adapter_name=None, **kwargs):
        if not USE_PEFT_BACKEND: raise ValueError('PEFT backend is required for this method.')
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT_LORA)
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        if isinstance(pretrained_model_name_or_path_or_dict, dict): pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict.copy()
        state_dict = self.lora_state_dict(pretrained_model_name_or_path_or_dict, **kwargs)
        is_correct_format = all(('lora' in key for key in state_dict.keys()))
        if not is_correct_format: raise ValueError('Invalid LoRA checkpoint.')
        self.load_lora_into_transformer(state_dict, transformer=getattr(self, self.transformer_name) if not hasattr(self, 'transformer') else self.transformer, adapter_name=adapter_name, _pipeline=self, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def load_lora_into_transformer(cls, state_dict, transformer, adapter_name=None, _pipeline=None, low_cpu_mem_usage=False):
        if low_cpu_mem_usage and is_peft_version('<', '0.13.0'): raise ValueError('`low_cpu_mem_usage=True` is not compatible with this `peft` version. Please update it with `pip install -U peft`.')
        transformer.load_lora_adapter(state_dict, network_alphas=None, adapter_name=adapter_name, _pipeline=_pipeline, low_cpu_mem_usage=low_cpu_mem_usage)
    @classmethod
    def save_lora_weights(cls, save_directory: Union[str, os.PathLike], transformer_lora_layers: Dict[str, Union[torch.nn.Module, torch.Tensor]]=None, is_main_process: bool=True, weight_name: str=None, save_function: Callable=None, safe_serialization: bool=True):
        state_dict = {}
        if not transformer_lora_layers: raise ValueError('You must pass `transformer_lora_layers`.')
        if transformer_lora_layers: state_dict.update(cls.pack_weights(transformer_lora_layers, cls.transformer_name))
        cls.write_lora_layers(state_dict=state_dict, save_directory=save_directory, is_main_process=is_main_process, weight_name=weight_name, save_function=save_function, safe_serialization=safe_serialization)
    def fuse_lora(self, components: List[str]=['transformer'], lora_scale: float=1.0, safe_fusing: bool=False, adapter_names: Optional[List[str]]=None, **kwargs):
        """Args:"""
        super().fuse_lora(components=components, lora_scale=lora_scale, safe_fusing=safe_fusing, adapter_names=adapter_names)
    def unfuse_lora(self, components: List[str]=['transformer'], **kwargs):
        """Args:"""
        super().unfuse_lora(components=components)
class LoraLoaderMixin(StableDiffusionLoraLoaderMixin):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'LoraLoaderMixin is deprecated and this will be removed in a future version. Please use `StableDiffusionLoraLoaderMixin`, instead.'
        deprecate('LoraLoaderMixin', '1.0.0', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
