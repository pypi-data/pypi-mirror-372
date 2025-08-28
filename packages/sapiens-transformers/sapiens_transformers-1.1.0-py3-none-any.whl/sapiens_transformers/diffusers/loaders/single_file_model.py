'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .single_file_utils import (SingleFileComponentError, convert_animatediff_checkpoint_to_diffusers, convert_autoencoder_dc_checkpoint_to_diffusers, convert_controlnet_checkpoint,
convert_flux_transformer_checkpoint_to_diffusers, convert_hunyuan_video_transformer_to_diffusers, convert_ldm_unet_checkpoint, convert_ldm_vae_checkpoint, convert_ltx_transformer_checkpoint_to_diffusers,
convert_ltx_vae_checkpoint_to_diffusers, convert_mochi_transformer_checkpoint_to_diffusers, convert_sapi_photogen_transformer_checkpoint_to_diffusers, convert_sapi_videogen_checkpoint_to_diffusers, convert_sapi_imagegen_transformer_checkpoint_to_diffusers,
convert_sapiens_videogen_transformer_checkpoint_to_diffusers, convert_sapiens_videogen_vae_checkpoint_to_diffusers, convert_sd3_transformer_checkpoint_to_diffusers, convert_stable_cascade_unet_single_file_to_diffusers,
create_controlnet_diffusers_config_from_ldm, create_unet_diffusers_config_from_ldm, create_vae_diffusers_config_from_ldm, fetch_diffusers_config, fetch_original_config, load_single_file_checkpoint)
from ..utils import deprecate, is_sapiens_accelerator_available
from huggingface_hub.utils import validate_hf_hub_args
from ..quantizers import DiffusersAutoQuantizer
from contextlib import nullcontext
from typing import Optional
import importlib
import inspect
import torch
import re
if is_sapiens_accelerator_available():
    from sapiens_accelerator import init_empty_weights
    from ..models.modeling_utils import load_model_dict_into_meta
SINGLE_FILE_LOADABLE_CLASSES = {'SAPIPhotoGenTransformer2DModel': {'checkpoint_mapping_fn': convert_sapi_imagegen_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'SAPIMotionAdapter': {'checkpoint_mapping_fn': convert_sapi_videogen_checkpoint_to_diffusers}, 'SparseControlNetModel': {'checkpoint_mapping_fn': convert_sapi_videogen_checkpoint_to_diffusers},
'SAPITransformer2DModel': {'checkpoint_mapping_fn': convert_sapi_imagegen_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'StableCascadeUNet': {'checkpoint_mapping_fn': convert_stable_cascade_unet_single_file_to_diffusers}, 'UNet2DConditionModel': {'checkpoint_mapping_fn': convert_ldm_unet_checkpoint,
'config_mapping_fn': create_unet_diffusers_config_from_ldm, 'default_subfolder': 'unet', 'legacy_kwargs': {'num_in_channels': 'in_channels'}},
'AutoencoderKL': {'checkpoint_mapping_fn': convert_ldm_vae_checkpoint, 'config_mapping_fn': create_vae_diffusers_config_from_ldm, 'default_subfolder': 'vae'},
'ControlNetModel': {'checkpoint_mapping_fn': convert_controlnet_checkpoint, 'config_mapping_fn': create_controlnet_diffusers_config_from_ldm},
'SD3Transformer2DModel': {'checkpoint_mapping_fn': convert_sd3_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'MotionAdapter': {'checkpoint_mapping_fn': convert_animatediff_checkpoint_to_diffusers}, 'SparseControlNetModel': {'checkpoint_mapping_fn': convert_animatediff_checkpoint_to_diffusers},
'FluxTransformer2DModel': {'checkpoint_mapping_fn': convert_flux_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'LTXVideoTransformer3DModel': {'checkpoint_mapping_fn': convert_ltx_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'AutoencoderKLLTXVideo': {'checkpoint_mapping_fn': convert_ltx_vae_checkpoint_to_diffusers, 'default_subfolder': 'vae'},
'AutoencoderKLSapiensVideoGenVideo': {'checkpoint_mapping_fn': convert_sapiens_videogen_vae_checkpoint_to_diffusers, 'default_subfolder': 'vae'},
'AutoencoderDC': {'checkpoint_mapping_fn': convert_autoencoder_dc_checkpoint_to_diffusers},
'MochiTransformer3DModel': {'checkpoint_mapping_fn': convert_mochi_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'},
'HunyuanVideoTransformer3DModel': {'checkpoint_mapping_fn': convert_hunyuan_video_transformer_to_diffusers, 'default_subfolder': 'transformer'},
'SapiensVideoGenVideoTransformer3DModel': {'checkpoint_mapping_fn': convert_sapiens_videogen_transformer_checkpoint_to_diffusers, 'default_subfolder': 'transformer'}}
def _get_single_file_loadable_mapping_class(cls):
    diffusers_module = importlib.import_module(__name__.split('.')[0])
    for loadable_class_str in SINGLE_FILE_LOADABLE_CLASSES:
        loadable_class = getattr(diffusers_module, loadable_class_str)
        if issubclass(cls, loadable_class): return loadable_class_str
    return None
def _get_mapping_function_kwargs(mapping_fn, **kwargs):
    parameters = inspect.signature(mapping_fn).parameters
    mapping_kwargs = {}
    for parameter in parameters:
        if parameter in kwargs: mapping_kwargs[parameter] = kwargs[parameter]
    return mapping_kwargs
class FromOriginalModelMixin:
    @classmethod
    @validate_hf_hub_args
    def from_single_file(cls, pretrained_model_link_or_path_or_dict: Optional[str]=None, **kwargs):
        mapping_class_name = _get_single_file_loadable_mapping_class(cls)
        if mapping_class_name is None: raise ValueError(f"FromOriginalModelMixin is currently only compatible with {', '.join(SINGLE_FILE_LOADABLE_CLASSES.keys())}")
        pretrained_model_link_or_path = kwargs.get('pretrained_model_link_or_path', None)
        if pretrained_model_link_or_path is not None:
            deprecation_message = 'Please use `pretrained_model_link_or_path_or_dict` argument instead for model classes'
            deprecate('pretrained_model_link_or_path', '1.0.0', deprecation_message)
            pretrained_model_link_or_path_or_dict = pretrained_model_link_or_path
        config = kwargs.pop('config', None)
        original_config = kwargs.pop('original_config', None)
        if config is not None and original_config is not None: raise ValueError('`from_single_file` cannot accept both `config` and `original_config` arguments. Please provide only one of these arguments')
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        cache_dir = kwargs.pop('cache_dir', None)
        local_files_only = kwargs.pop('local_files_only', None)
        subfolder = kwargs.pop('subfolder', None)
        revision = kwargs.pop('revision', None)
        config_revision = kwargs.pop('config_revision', None)
        torch_dtype = kwargs.pop('torch_dtype', None)
        quantization_config = kwargs.pop('quantization_config', None)
        device = kwargs.pop('device', None)
        if isinstance(pretrained_model_link_or_path_or_dict, dict): checkpoint = pretrained_model_link_or_path_or_dict
        else: checkpoint = load_single_file_checkpoint(pretrained_model_link_or_path_or_dict, force_download=force_download, proxies=proxies, token=token, cache_dir=cache_dir, local_files_only=local_files_only, revision=revision)
        if quantization_config is not None:
            hf_quantizer = DiffusersAutoQuantizer.from_config(quantization_config)
            hf_quantizer.validate_environment()
        else: hf_quantizer = None
        mapping_functions = SINGLE_FILE_LOADABLE_CLASSES[mapping_class_name]
        checkpoint_mapping_fn = mapping_functions['checkpoint_mapping_fn']
        if original_config is not None:
            if 'config_mapping_fn' in mapping_functions: config_mapping_fn = mapping_functions['config_mapping_fn']
            else: config_mapping_fn = None
            if config_mapping_fn is None: raise ValueError(f'`original_config` has been provided for {mapping_class_name} but no mapping functionwas found to convert the original config to a Diffusers config in`diffusers.loaders.single_file_utils`')
            if isinstance(original_config, str): original_config = fetch_original_config(original_config, local_files_only=local_files_only)
            config_mapping_kwargs = _get_mapping_function_kwargs(config_mapping_fn, **kwargs)
            diffusers_model_config = config_mapping_fn(original_config=original_config, checkpoint=checkpoint, **config_mapping_kwargs)
        else:
            if config is not None:
                if isinstance(config, str): default_pretrained_model_config_name = config
                else: raise ValueError('Invalid `config` argument. Please provide a string representing a repo idor path to a local Diffusers model repo.')
            else:
                config = fetch_diffusers_config(checkpoint)
                default_pretrained_model_config_name = config['pretrained_model_name_or_path']
                if 'default_subfolder' in mapping_functions: subfolder = mapping_functions['default_subfolder']
                subfolder = subfolder or config.pop('subfolder', None)
            diffusers_model_config = cls.load_config(pretrained_model_name_or_path=default_pretrained_model_config_name, subfolder=subfolder, local_files_only=local_files_only, token=token, revision=config_revision)
            expected_kwargs, optional_kwargs = cls._get_signature_keys(cls)
            if 'legacy_kwargs' in mapping_functions:
                legacy_kwargs = mapping_functions['legacy_kwargs']
                for legacy_key, new_key in legacy_kwargs.items():
                    if legacy_key in kwargs: kwargs[new_key] = kwargs.pop(legacy_key)
            model_kwargs = {k: kwargs.get(k) for k in kwargs if k in expected_kwargs or k in optional_kwargs}
            diffusers_model_config.update(model_kwargs)
        checkpoint_mapping_kwargs = _get_mapping_function_kwargs(checkpoint_mapping_fn, **kwargs)
        diffusers_format_checkpoint = checkpoint_mapping_fn(config=diffusers_model_config, checkpoint=checkpoint, **checkpoint_mapping_kwargs)
        if not diffusers_format_checkpoint: raise SingleFileComponentError(f'Failed to load {mapping_class_name}. Weights for this component appear to be missing in the checkpoint.')
        ctx = init_empty_weights if is_sapiens_accelerator_available() else nullcontext
        with ctx(): model = cls.from_config(diffusers_model_config)
        use_keep_in_fp32_modules = cls._keep_in_fp32_modules is not None and (torch_dtype == torch.float16 or hasattr(hf_quantizer, 'use_keep_in_fp32_modules'))
        if use_keep_in_fp32_modules:
            keep_in_fp32_modules = cls._keep_in_fp32_modules
            if not isinstance(keep_in_fp32_modules, list): keep_in_fp32_modules = [keep_in_fp32_modules]
        else: keep_in_fp32_modules = []
        if hf_quantizer is not None: hf_quantizer.preprocess_model(model=model, device_map=None, state_dict=diffusers_format_checkpoint, keep_in_fp32_modules=keep_in_fp32_modules)
        if is_sapiens_accelerator_available():
            param_device = torch.device(device) if device else torch.device('cpu')
            unexpected_keys = load_model_dict_into_meta(model, diffusers_format_checkpoint, dtype=torch_dtype, device=param_device, hf_quantizer=hf_quantizer, keep_in_fp32_modules=keep_in_fp32_modules)
        else: _, unexpected_keys = model.load_state_dict(diffusers_format_checkpoint, strict=False)
        if model._keys_to_ignore_on_load_unexpected is not None:
            for pat in model._keys_to_ignore_on_load_unexpected: unexpected_keys = [k for k in unexpected_keys if re.search(pat, k) is None]
        if hf_quantizer is not None:
            hf_quantizer.postprocess_model(model)
            model.hf_quantizer = hf_quantizer
        if torch_dtype is not None and hf_quantizer is None: model.to(torch_dtype)
        model.eval()
        return model
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
