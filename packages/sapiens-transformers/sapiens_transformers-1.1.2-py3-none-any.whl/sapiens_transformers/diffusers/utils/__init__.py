'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import os
from packaging import version
from .. import __version__
from .constants import (CONFIG_NAME, DEPRECATED_REVISION_ARGS, DIFFUSERS_DYNAMIC_MODULE_NAME, FLAX_WEIGHTS_NAME, GGUF_FILE_EXTENSION, HF_MODULES_CACHE, HUGGINGFACE_CO_RESOLVE_ENDPOINT,
MIN_PEFT_VERSION, ONNX_EXTERNAL_WEIGHTS_NAME, ONNX_WEIGHTS_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFETENSORS_FILE_EXTENSION, SAFETENSORS_WEIGHTS_NAME, USE_PEFT_BACKEND, WEIGHTS_INDEX_NAME, WEIGHTS_NAME)
from .deprecation_utils import deprecate
from .doc_utils import replace_example_docstring
from .dynamic_modules_utils import get_class_from_dynamic_module
from .export_utils import export_to_gif, export_to_obj, export_to_ply, export_to_video
from .hub_utils import PushToHubMixin, _add_variant, _get_checkpoint_shard_files, _get_model_file, extract_commit_hash, http_user_agent
from .import_utils import (BACKENDS_MAPPING, DIFFUSERS_SLOW_IMPORT, ENV_VARS_TRUE_AND_AUTO_VALUES, ENV_VARS_TRUE_VALUES, USE_JAX, USE_TF, USE_TORCH, DummyObject, OptionalDependencyNotAvailable,
_LazyModule, get_objects_from_module, is_sapiens_accelerator_available, is_sapiens_accelerator_version, is_sapiens_machine_available, is_sapiens_machine_version, is_bs4_available, is_flax_available, is_ftfy_available,
is_gguf_available, is_gguf_version, is_google_colab, is_inflect_available, is_invisible_watermark_available, is_k_diffusion_available, is_k_diffusion_version, is_librosa_available,
is_matplotlib_available, is_note_seq_available, is_onnx_available, is_peft_available, is_peft_version, is_safetensors_available, is_scipy_available, is_sentencepiece_available,
is_tensorboard_available, is_timm_available, is_torch_available, is_torch_npu_available, is_torch_version, is_torch_xla_available, is_torch_xla_version, is_torchao_available,
is_torchsde_available, is_torchvision_available, is_transformers_available, is_sapiens_transformers_version, is_unidecode_available, is_wandb_available, is_xformers_available, requires_backends)
from .loading_utils import get_module_from_name, get_submodule_by_name, load_image, load_video
from typing import TYPE_CHECKING as SAPIENS_TECHNOLOGY_CHECKING
from .outputs import BaseOutput
from .peft_utils import (check_peft_version, delete_adapter_layers, get_adapter_name, get_peft_kwargs, recurse_remove_peft_layers, scale_lora_layers, set_adapter_layers,
set_weights_and_activate_adapters, unscale_lora_layers)
from .pil_utils import PIL_INTERPOLATION, make_image_grid, numpy_to_pil, pt_to_pil
from .state_dict_utils import convert_all_state_dict_to_peft, convert_state_dict_to_diffusers, convert_state_dict_to_kohya, convert_state_dict_to_peft, convert_unet_state_dict_to_peft
from .outputs import BaseOutput as SapiensTechnologyOutput
from .import_utils import (OptionalDependencyNotAvailable as SapiensTechnologyNotAvailable, _LazyModule as SapiensTechnologyModule, is_torch_available as sapiens_technology_torch,
is_sentencepiece_available as sapiens_technology_is_available, is_flax_available as sapiens_technology_flax, DIFFUSERS_SLOW_IMPORT as SAPIENS_TECHNOLOGY_IMPORT,
get_objects_from_module as sapiens_technology_module, is_transformers_available as sapiens_technology_transformers)
def check_min_version(min_version):
    if version.parse(__version__) < version.parse(min_version):
        if 'dev' in min_version: error_message = 'This example requires a source install from Sapiens diffusers (see `https://huggingface.co/docs/diffusers/installation#install-from-source`),'
        else: error_message = f'This example requires a minimum version of {min_version},'
        error_message += f' but the version found is {__version__}.\n'
        raise ImportError(error_message)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
