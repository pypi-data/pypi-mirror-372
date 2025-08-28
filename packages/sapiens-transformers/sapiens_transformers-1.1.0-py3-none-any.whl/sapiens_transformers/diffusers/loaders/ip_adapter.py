'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..models.attention_processor import (AttnProcessor, AttnProcessor2_0, FluxAttnProcessor2_0, FluxIPAdapterJointAttnProcessor2_0, IPAdapterAttnProcessor, IPAdapterAttnProcessor2_0,
IPAdapterXFormersAttnProcessor, JointAttnProcessor2_0, SAPIPhotoGenAttnProcessor2_0, SAPIPhotoGenIPAdapterJointAttnProcessor2_0, SAPIIPAdapterJointAttnProcessor2_0, SD3IPAdapterJointAttnProcessor2_0)
from ..utils import USE_PEFT_BACKEND, _get_model_file, is_sapiens_accelerator_available, is_torch_version, is_transformers_available
from ..models.modeling_utils import _LOW_CPU_MEM_USAGE_DEFAULT, load_state_dict
from .unet_loader_utils import _maybe_expand_lora_scales
from huggingface_hub.utils import validate_hf_hub_args
from typing import Dict, List, Optional, Union
from safetensors import safe_open
import torch.nn.functional as F
from pathlib import Path
import torch
if is_transformers_available(): from sapiens_transformers import CLIPImageProcessor, CLIPVisionModelWithProjection, SiglipImageProcessor, SiglipVisionModel
class IPAdapterMixin:
    @validate_hf_hub_args
    def load_ip_adapter(self, pretrained_model_name_or_path_or_dict: Union[str, List[str], Dict[str, torch.Tensor]], subfolder: Union[str, List[str]], weight_name: Union[str, List[str]], image_encoder_folder: Optional[str]='image_encoder', **kwargs):
        if not isinstance(weight_name, list): weight_name = [weight_name]
        if not isinstance(pretrained_model_name_or_path_or_dict, list): pretrained_model_name_or_path_or_dict = [pretrained_model_name_or_path_or_dict]
        if len(pretrained_model_name_or_path_or_dict) == 1: pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict * len(weight_name)
        if not isinstance(subfolder, list): subfolder = [subfolder]
        if len(subfolder) == 1: subfolder = subfolder * len(weight_name)
        if len(weight_name) != len(pretrained_model_name_or_path_or_dict): raise ValueError('`weight_name` and `pretrained_model_name_or_path_or_dict` must have the same length.')
        if len(weight_name) != len(subfolder): raise ValueError('`weight_name` and `subfolder` must have the same length.')
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dicts = []
        for pretrained_model_name_or_path_or_dict, weight_name, subfolder in zip(pretrained_model_name_or_path_or_dict, weight_name, subfolder):
            if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                if weight_name.endswith('.safetensors'):
                    state_dict = {'image_proj': {}, 'ip_adapter': {}}
                    with safe_open(model_file, framework='pt', device='cpu') as f:
                        for key in f.keys():
                            if key.startswith('image_proj.'): state_dict['image_proj'][key.replace('image_proj.', '')] = f.get_tensor(key)
                            elif key.startswith('ip_adapter.'): state_dict['ip_adapter'][key.replace('ip_adapter.', '')] = f.get_tensor(key)
                else: state_dict = load_state_dict(model_file)
            else: state_dict = pretrained_model_name_or_path_or_dict
            keys = list(state_dict.keys())
            if 'image_proj' not in keys and 'ip_adapter' not in keys: raise ValueError('Required keys are (`image_proj` and `ip_adapter`) missing from the state dict.')
            state_dicts.append(state_dict)
            if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is None:
                if image_encoder_folder is not None:
                    if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                        if image_encoder_folder.count('/') == 0: image_encoder_subfolder = Path(subfolder, image_encoder_folder).as_posix()
                        else: image_encoder_subfolder = Path(image_encoder_folder).as_posix()
                        image_encoder = CLIPVisionModelWithProjection.from_pretrained(pretrained_model_name_or_path_or_dict, subfolder=image_encoder_subfolder, low_cpu_mem_usage=low_cpu_mem_usage, cache_dir=cache_dir, local_files_only=local_files_only).to(self.device, dtype=self.dtype)
                        self.register_modules(image_encoder=image_encoder)
                    else: raise ValueError('`image_encoder` cannot be loaded because `pretrained_model_name_or_path_or_dict` is a state dict.')
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is None:
                default_clip_size = 224
                clip_image_size = self.image_encoder.config.image_size if self.image_encoder is not None else default_clip_size
                feature_extractor = CLIPImageProcessor(size=clip_image_size, crop_size=clip_image_size)
                self.register_modules(feature_extractor=feature_extractor)
        unet = getattr(self, self.unet_name) if not hasattr(self, 'unet') else self.unet
        unet._load_ip_adapter_weights(state_dicts, low_cpu_mem_usage=low_cpu_mem_usage)
        extra_loras = unet._load_ip_adapter_loras(state_dicts)
        if extra_loras != {}:
            peft_config = getattr(unet, 'peft_config', {})
            for k, lora in extra_loras.items():
                if f'faceid_{k}' not in peft_config:
                    self.load_lora_weights(lora, adapter_name=f'faceid_{k}')
                    self.set_adapters([f'faceid_{k}'], adapter_weights=[1.0])
    def set_ip_adapter_scale(self, scale):
        unet = getattr(self, self.unet_name) if not hasattr(self, 'unet') else self.unet
        if not isinstance(scale, list): scale = [scale]
        scale_configs = _maybe_expand_lora_scales(unet, scale, default_scale=0.0)
        for attn_name, attn_processor in unet.attn_processors.items():
            if isinstance(attn_processor, (IPAdapterAttnProcessor, IPAdapterAttnProcessor2_0, IPAdapterXFormersAttnProcessor)):
                if len(scale_configs) != len(attn_processor.scale): raise ValueError(f'Cannot assign {len(scale_configs)} scale_configs to {len(attn_processor.scale)} IP-Adapter.')
                elif len(scale_configs) == 1: scale_configs = scale_configs * len(attn_processor.scale)
                for i, scale_config in enumerate(scale_configs):
                    if isinstance(scale_config, dict):
                        for k, s in scale_config.items():
                            if attn_name.startswith(k): attn_processor.scale[i] = s
                    else: attn_processor.scale[i] = scale_config
    def unload_ip_adapter(self):
        """Examples:"""
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is not None:
            self.image_encoder = None
            self.register_to_config(image_encoder=[None, None])
        if not hasattr(self, 'safety_checker'):
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is not None:
                self.feature_extractor = None
                self.register_to_config(feature_extractor=[None, None])
        self.unet.encoder_hid_proj = None
        self.unet.config.encoder_hid_dim_type = None
        if hasattr(self.unet, 'text_encoder_hid_proj') and self.unet.text_encoder_hid_proj is not None:
            self.unet.encoder_hid_proj = self.unet.text_encoder_hid_proj
            self.unet.text_encoder_hid_proj = None
            self.unet.config.encoder_hid_dim_type = 'text_proj'
        attn_procs = {}
        for name, value in self.unet.attn_processors.items():
            attn_processor_class = AttnProcessor2_0() if hasattr(F, 'scaled_dot_product_attention') else AttnProcessor()
            attn_procs[name] = attn_processor_class if isinstance(value, (IPAdapterAttnProcessor, IPAdapterAttnProcessor2_0, IPAdapterXFormersAttnProcessor)) else value.__class__()
        self.unet.set_attn_processor(attn_procs)
class FluxIPAdapterMixin:
    @validate_hf_hub_args
    def load_ip_adapter(self, pretrained_model_name_or_path_or_dict: Union[str, List[str], Dict[str, torch.Tensor]], weight_name: Union[str, List[str]], subfolder: Optional[Union[str, List[str]]]='', image_encoder_pretrained_model_name_or_path: Optional[str]='image_encoder', image_encoder_subfolder: Optional[str]='', image_encoder_dtype: torch.dtype=torch.float16, **kwargs):
        if not isinstance(weight_name, list): weight_name = [weight_name]
        if not isinstance(pretrained_model_name_or_path_or_dict, list): pretrained_model_name_or_path_or_dict = [pretrained_model_name_or_path_or_dict]
        if len(pretrained_model_name_or_path_or_dict) == 1: pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict * len(weight_name)
        if not isinstance(subfolder, list): subfolder = [subfolder]
        if len(subfolder) == 1: subfolder = subfolder * len(weight_name)
        if len(weight_name) != len(pretrained_model_name_or_path_or_dict): raise ValueError('`weight_name` and `pretrained_model_name_or_path_or_dict` must have the same length.')
        if len(weight_name) != len(subfolder): raise ValueError('`weight_name` and `subfolder` must have the same length.')
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dicts = []
        for pretrained_model_name_or_path_or_dict, weight_name, subfolder in zip(pretrained_model_name_or_path_or_dict, weight_name, subfolder):
            if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                if weight_name.endswith('.safetensors'):
                    state_dict = {'image_proj': {}, 'ip_adapter': {}}
                    with safe_open(model_file, framework='pt', device='cpu') as f:
                        image_proj_keys = ['ip_adapter_proj_model.', 'image_proj.']
                        ip_adapter_keys = ['double_blocks.', 'ip_adapter.']
                        for key in f.keys():
                            if any((key.startswith(prefix) for prefix in image_proj_keys)):
                                diffusers_name = '.'.join(key.split('.')[1:])
                                state_dict['image_proj'][diffusers_name] = f.get_tensor(key)
                            elif any((key.startswith(prefix) for prefix in ip_adapter_keys)):
                                diffusers_name = '.'.join(key.split('.')[1:]).replace('ip_adapter_double_stream_k_proj', 'to_k_ip').replace('ip_adapter_double_stream_v_proj', 'to_v_ip').replace('processor.', '')
                                state_dict['ip_adapter'][diffusers_name] = f.get_tensor(key)
                else: state_dict = load_state_dict(model_file)
            else: state_dict = pretrained_model_name_or_path_or_dict
            keys = list(state_dict.keys())
            if keys != ['image_proj', 'ip_adapter']: raise ValueError('Required keys are (`image_proj` and `ip_adapter`) missing from the state dict.')
            state_dicts.append(state_dict)
            if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is None:
                if image_encoder_pretrained_model_name_or_path is not None:
                    if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                        image_encoder = CLIPVisionModelWithProjection.from_pretrained(image_encoder_pretrained_model_name_or_path, subfolder=image_encoder_subfolder, low_cpu_mem_usage=low_cpu_mem_usage, cache_dir=cache_dir, local_files_only=local_files_only).to(self.device, dtype=image_encoder_dtype).eval()
                        self.register_modules(image_encoder=image_encoder)
                    else: raise ValueError('`image_encoder` cannot be loaded because `pretrained_model_name_or_path_or_dict` is a state dict.')
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is None:
                default_clip_size = 224
                clip_image_size = self.image_encoder.config.image_size if self.image_encoder is not None else default_clip_size
                feature_extractor = CLIPImageProcessor(size=clip_image_size, crop_size=clip_image_size)
                self.register_modules(feature_extractor=feature_extractor)
        self.transformer._load_ip_adapter_weights(state_dicts, low_cpu_mem_usage=low_cpu_mem_usage)
    def set_ip_adapter_scale(self, scale: Union[float, List[float], List[List[float]]]):
        transformer = self.transformer
        if not isinstance(scale, list): scale = [[scale] * transformer.config.num_layers]
        elif isinstance(scale, list) and isinstance(scale[0], int) or isinstance(scale[0], float):
            if len(scale) != transformer.config.num_layers: raise ValueError(f'Expected list of {transformer.config.num_layers} scales, got {len(scale)}.')
            scale = [scale]
        scale_configs = scale
        key_id = 0
        for attn_name, attn_processor in transformer.attn_processors.items():
            if isinstance(attn_processor, FluxIPAdapterJointAttnProcessor2_0):
                if len(scale_configs) != len(attn_processor.scale): raise ValueError(f'Cannot assign {len(scale_configs)} scale_configs to {len(attn_processor.scale)} IP-Adapter.')
                elif len(scale_configs) == 1: scale_configs = scale_configs * len(attn_processor.scale)
                for i, scale_config in enumerate(scale_configs): attn_processor.scale[i] = scale_config[key_id]
                key_id += 1
    def unload_ip_adapter(self):
        """Examples:"""
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is not None:
            self.image_encoder = None
            self.register_to_config(image_encoder=[None, None])
        if not hasattr(self, 'safety_checker'):
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is not None:
                self.feature_extractor = None
                self.register_to_config(feature_extractor=[None, None])
        self.transformer.encoder_hid_proj = None
        self.transformer.config.encoder_hid_dim_type = None
        attn_procs = {}
        for name, value in self.transformer.attn_processors.items():
            attn_processor_class = FluxAttnProcessor2_0()
            attn_procs[name] = attn_processor_class if isinstance(value, FluxIPAdapterJointAttnProcessor2_0) else value.__class__()
        self.transformer.set_attn_processor(attn_procs)
class SD3IPAdapterMixin:
    @property
    def is_ip_adapter_active(self) -> bool:
        """Returns:"""
        scales = [attn_proc.scale for attn_proc in self.transformer.attn_processors.values() if isinstance(attn_proc, SD3IPAdapterJointAttnProcessor2_0)]
        return len(scales) > 0 and any((scale > 0 for scale in scales))
    @validate_hf_hub_args
    def load_ip_adapter(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], weight_name: str='ip-adapter.safetensors', subfolder: Optional[str]=None, image_encoder_folder: Optional[str]='image_encoder', **kwargs) -> None:
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        if not isinstance(pretrained_model_name_or_path_or_dict, dict):
            model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
            if weight_name.endswith('.safetensors'):
                state_dict = {'image_proj': {}, 'ip_adapter': {}}
                with safe_open(model_file, framework='pt', device='cpu') as f:
                    for key in f.keys():
                        if key.startswith('image_proj.'): state_dict['image_proj'][key.replace('image_proj.', '')] = f.get_tensor(key)
                        elif key.startswith('ip_adapter.'): state_dict['ip_adapter'][key.replace('ip_adapter.', '')] = f.get_tensor(key)
            else: state_dict = load_state_dict(model_file)
        else: state_dict = pretrained_model_name_or_path_or_dict
        keys = list(state_dict.keys())
        if 'image_proj' not in keys and 'ip_adapter' not in keys: raise ValueError('Required keys are (`image_proj` and `ip_adapter`) missing from the state dict.')
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is None:
            if image_encoder_folder is not None:
                if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                    if image_encoder_folder.count('/') == 0: image_encoder_subfolder = Path(subfolder, image_encoder_folder).as_posix()
                    else: image_encoder_subfolder = Path(image_encoder_folder).as_posix()
                    kwargs = {'low_cpu_mem_usage': low_cpu_mem_usage, 'cache_dir': cache_dir, 'local_files_only': local_files_only}
                    self.register_modules(feature_extractor=SiglipImageProcessor.from_pretrained(image_encoder_subfolder, **kwargs).to(self.device, dtype=self.dtype), image_encoder=SiglipVisionModel.from_pretrained(image_encoder_subfolder, **kwargs).to(self.device, dtype=self.dtype))
                else: raise ValueError('`image_encoder` cannot be loaded because `pretrained_model_name_or_path_or_dict` is a state dict.')
        self.transformer._load_ip_adapter_weights(state_dict, low_cpu_mem_usage=low_cpu_mem_usage)
    def set_ip_adapter_scale(self, scale: float) -> None:
        """Args:"""
        for attn_processor in self.transformer.attn_processors.values():
            if isinstance(attn_processor, SD3IPAdapterJointAttnProcessor2_0): attn_processor.scale = scale
    def unload_ip_adapter(self) -> None:
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is not None:
            self.image_encoder = None
            self.register_to_config(image_encoder=None)
        if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is not None:
            self.feature_extractor = None
            self.register_to_config(feature_extractor=None)
        self.transformer.image_proj = None
        attn_procs = {name: JointAttnProcessor2_0() if isinstance(value, SD3IPAdapterJointAttnProcessor2_0) else value.__class__() for name, value in self.transformer.attn_processors.items()}
        self.transformer.set_attn_processor(attn_procs)
class SAPIPhotoGenIPAdapterMixin:
    @validate_hf_hub_args
    def load_ip_adapter(self, pretrained_model_name_or_path_or_dict: Union[str, List[str], Dict[str, torch.Tensor]], weight_name: Union[str, List[str]], subfolder: Optional[Union[str, List[str]]]='', image_encoder_pretrained_model_name_or_path: Optional[str]='image_encoder', image_encoder_subfolder: Optional[str]='', image_encoder_dtype: torch.dtype=torch.float16, **kwargs):
        if not isinstance(weight_name, list): weight_name = [weight_name]
        if not isinstance(pretrained_model_name_or_path_or_dict, list): pretrained_model_name_or_path_or_dict = [pretrained_model_name_or_path_or_dict]
        if len(pretrained_model_name_or_path_or_dict) == 1: pretrained_model_name_or_path_or_dict = pretrained_model_name_or_path_or_dict * len(weight_name)
        if not isinstance(subfolder, list): subfolder = [subfolder]
        if len(subfolder) == 1: subfolder = subfolder * len(weight_name)
        if len(weight_name) != len(pretrained_model_name_or_path_or_dict): raise ValueError('`weight_name` and `pretrained_model_name_or_path_or_dict` must have the same length.')
        if len(weight_name) != len(subfolder): raise ValueError('`weight_name` and `subfolder` must have the same length.')
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        state_dicts = []
        for pretrained_model_name_or_path_or_dict, weight_name, subfolder in zip(pretrained_model_name_or_path_or_dict, weight_name, subfolder):
            if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
                if weight_name.endswith('.safetensors'):
                    state_dict = {'image_proj': {}, 'ip_adapter': {}}
                    with safe_open(model_file, framework='pt', device='cpu') as f:
                        image_proj_keys = ['ip_adapter_proj_model.', 'image_proj.']
                        ip_adapter_keys = ['double_blocks.', 'ip_adapter.']
                        for key in f.keys():
                            if any((key.startswith(prefix) for prefix in image_proj_keys)):
                                diffusers_name = '.'.join(key.split('.')[1:])
                                state_dict['image_proj'][diffusers_name] = f.get_tensor(key)
                            elif any((key.startswith(prefix) for prefix in ip_adapter_keys)):
                                diffusers_name = '.'.join(key.split('.')[1:]).replace('ip_adapter_double_stream_k_proj', 'to_k_ip').replace('ip_adapter_double_stream_v_proj', 'to_v_ip').replace('processor.', '')
                                state_dict['ip_adapter'][diffusers_name] = f.get_tensor(key)
                else: state_dict = load_state_dict(model_file)
            else: state_dict = pretrained_model_name_or_path_or_dict
            keys = list(state_dict.keys())
            if keys != ['image_proj', 'ip_adapter']: raise ValueError('Required keys are (`image_proj` and `ip_adapter`) missing from the state dict.')
            state_dicts.append(state_dict)
            if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is None:
                if image_encoder_pretrained_model_name_or_path is not None:
                    if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                        image_encoder = CLIPVisionModelWithProjection.from_pretrained(image_encoder_pretrained_model_name_or_path, subfolder=image_encoder_subfolder, low_cpu_mem_usage=low_cpu_mem_usage, cache_dir=cache_dir, local_files_only=local_files_only).to(self.device, dtype=image_encoder_dtype).eval()
                        self.register_modules(image_encoder=image_encoder)
                    else: raise ValueError('`image_encoder` cannot be loaded because `pretrained_model_name_or_path_or_dict` is a state dict.')
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is None:
                default_clip_size = 224
                clip_image_size = self.image_encoder.config.image_size if self.image_encoder is not None else default_clip_size
                feature_extractor = CLIPImageProcessor(size=clip_image_size, crop_size=clip_image_size)
                self.register_modules(feature_extractor=feature_extractor)
        self.transformer._load_ip_adapter_weights(state_dicts, low_cpu_mem_usage=low_cpu_mem_usage)
    def set_ip_adapter_scale(self, scale: Union[float, List[float], List[List[float]]]):
        transformer = self.transformer
        if not isinstance(scale, list): scale = [[scale] * transformer.config.num_layers]
        elif isinstance(scale, list) and isinstance(scale[0], int) or isinstance(scale[0], float):
            if len(scale) != transformer.config.num_layers: raise ValueError(f'Expected list of {transformer.config.num_layers} scales, got {len(scale)}.')
            scale = [scale]
        scale_configs = scale
        key_id = 0
        for attn_name, attn_processor in transformer.attn_processors.items():
            if isinstance(attn_processor, SAPIPhotoGenIPAdapterJointAttnProcessor2_0):
                if len(scale_configs) != len(attn_processor.scale): raise ValueError(f'Cannot assign {len(scale_configs)} scale_configs to {len(attn_processor.scale)} IP-Adapter.')
                elif len(scale_configs) == 1: scale_configs = scale_configs * len(attn_processor.scale)
                for i, scale_config in enumerate(scale_configs): attn_processor.scale[i] = scale_config[key_id]
                key_id += 1
    def unload_ip_adapter(self):
        """Examples:"""
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is not None:
            self.image_encoder = None
            self.register_to_config(image_encoder=[None, None])
        if not hasattr(self, 'safety_checker'):
            if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is not None:
                self.feature_extractor = None
                self.register_to_config(feature_extractor=[None, None])
        self.transformer.encoder_hid_proj = None
        self.transformer.config.encoder_hid_dim_type = None
        attn_procs = {}
        for name, value in self.transformer.attn_processors.items():
            attn_processor_class = SAPIPhotoGenAttnProcessor2_0()
            attn_procs[name] = attn_processor_class if isinstance(value, SAPIPhotoGenIPAdapterJointAttnProcessor2_0) else value.__class__()
        self.transformer.set_attn_processor(attn_procs)        
class SAPIIPAdapterMixin:
    @property
    def is_ip_adapter_active(self) -> bool:
        """Returns:"""
        scales = [attn_proc.scale for attn_proc in self.transformer.attn_processors.values() if isinstance(attn_proc, SAPIIPAdapterJointAttnProcessor2_0)]
        return len(scales) > 0 and any((scale > 0 for scale in scales))
    @validate_hf_hub_args
    def load_ip_adapter(self, pretrained_model_name_or_path_or_dict: Union[str, Dict[str, torch.Tensor]], weight_name: str='ip-adapter.safetensors', subfolder: Optional[str]=None, image_encoder_folder: Optional[str]='image_encoder', **kwargs) -> None:
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', None)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        low_cpu_mem_usage = kwargs.pop('low_cpu_mem_usage', _LOW_CPU_MEM_USAGE_DEFAULT)
        if low_cpu_mem_usage and (not is_sapiens_accelerator_available()): low_cpu_mem_usage = False
        if low_cpu_mem_usage is True and (not is_torch_version('>=', '1.9.0')): raise NotImplementedError('Low memory initialization requires torch >= 1.9.0. Please either update your PyTorch version or set `low_cpu_mem_usage=False`.')
        user_agent = {'file_type': 'attn_procs_weights', 'framework': 'pytorch'}
        if not isinstance(pretrained_model_name_or_path_or_dict, dict):
            model_file = _get_model_file(pretrained_model_name_or_path_or_dict, weights_name=weight_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, user_agent=user_agent)
            if weight_name.endswith('.safetensors'):
                state_dict = {'image_proj': {}, 'ip_adapter': {}}
                with safe_open(model_file, framework='pt', device='cpu') as f:
                    for key in f.keys():
                        if key.startswith('image_proj.'): state_dict['image_proj'][key.replace('image_proj.', '')] = f.get_tensor(key)
                        elif key.startswith('ip_adapter.'): state_dict['ip_adapter'][key.replace('ip_adapter.', '')] = f.get_tensor(key)
            else: state_dict = load_state_dict(model_file)
        else: state_dict = pretrained_model_name_or_path_or_dict
        keys = list(state_dict.keys())
        if 'image_proj' not in keys and 'ip_adapter' not in keys: raise ValueError('Required keys are (`image_proj` and `ip_adapter`) missing from the state dict.')
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is None:
            if image_encoder_folder is not None:
                if not isinstance(pretrained_model_name_or_path_or_dict, dict):
                    if image_encoder_folder.count('/') == 0: image_encoder_subfolder = Path(subfolder, image_encoder_folder).as_posix()
                    else: image_encoder_subfolder = Path(image_encoder_folder).as_posix()
                    kwargs = {'low_cpu_mem_usage': low_cpu_mem_usage, 'cache_dir': cache_dir, 'local_files_only': local_files_only}
                    self.register_modules(feature_extractor=SiglipImageProcessor.from_pretrained(image_encoder_subfolder, **kwargs).to(self.device, dtype=self.dtype), image_encoder=SiglipVisionModel.from_pretrained(image_encoder_subfolder, **kwargs).to(self.device, dtype=self.dtype))
                else: raise ValueError('`image_encoder` cannot be loaded because `pretrained_model_name_or_path_or_dict` is a state dict.')
        self.transformer._load_ip_adapter_weights(state_dict, low_cpu_mem_usage=low_cpu_mem_usage)
    def set_ip_adapter_scale(self, scale: float) -> None:
        """Args:"""
        for attn_processor in self.transformer.attn_processors.values():
            if isinstance(attn_processor, SAPIIPAdapterJointAttnProcessor2_0): attn_processor.scale = scale
    def unload_ip_adapter(self) -> None:
        if hasattr(self, 'image_encoder') and getattr(self, 'image_encoder', None) is not None:
            self.image_encoder = None
            self.register_to_config(image_encoder=None)
        if hasattr(self, 'feature_extractor') and getattr(self, 'feature_extractor', None) is not None:
            self.feature_extractor = None
            self.register_to_config(feature_extractor=None)
        self.transformer.image_proj = None
        attn_procs = {name: JointAttnProcessor2_0() if isinstance(value, SAPIIPAdapterJointAttnProcessor2_0) else value.__class__() for name, value in self.transformer.attn_processors.items()}
        self.transformer.set_attn_processor(attn_procs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
