'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import importlib
import os
from huggingface_hub.constants import HF_HOME
from packaging import version
from ..dependency_versions_check import dep_version_check
from .import_utils import ENV_VARS_TRUE_VALUES, is_peft_available, is_transformers_available
MIN_PEFT_VERSION = '0.6.0'
MIN_TRANSFORMERS_VERSION = '4.34.0'
_CHECK_PEFT = os.environ.get('_CHECK_PEFT', '1') in ENV_VARS_TRUE_VALUES
CONFIG_NAME = 'config.json'
WEIGHTS_NAME = 'diffusion_pytorch_model.bin'
WEIGHTS_INDEX_NAME = 'diffusion_pytorch_model.bin.index.json'
FLAX_WEIGHTS_NAME = 'diffusion_flax_model.msgpack'
ONNX_WEIGHTS_NAME = 'model.onnx'
SAFETENSORS_WEIGHTS_NAME = 'diffusion_pytorch_model.safetensors'
SAFE_WEIGHTS_INDEX_NAME = 'diffusion_pytorch_model.safetensors.index.json'
SAFETENSORS_FILE_EXTENSION = 'safetensors'
GGUF_FILE_EXTENSION = 'gguf'
ONNX_EXTERNAL_WEIGHTS_NAME = 'weights.pb'
HUGGINGFACE_CO_RESOLVE_ENDPOINT = os.environ.get('HF_ENDPOINT', 'https://huggingface.co')
DIFFUSERS_DYNAMIC_MODULE_NAME = 'sapiens_transformers.diffusers_modules'
HF_MODULES_CACHE = os.getenv('HF_MODULES_CACHE', os.path.join(HF_HOME, 'modules'))
DEPRECATED_REVISION_ARGS = ['fp16', 'non-ema']
_required_peft_version = is_peft_available() and version.parse(version.parse(importlib.metadata.version('peft')).base_version) >= version.parse(MIN_PEFT_VERSION)
_required_sapiens_transformers_version = is_transformers_available()
USE_PEFT_BACKEND = _required_peft_version and _required_sapiens_transformers_version
if USE_PEFT_BACKEND and _CHECK_PEFT: dep_version_check('peft')
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
