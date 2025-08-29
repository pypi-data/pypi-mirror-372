'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Union
import numpy as np
import PIL
from PIL import Image
from ...utils import DIFFUSERS_SLOW_IMPORT, BaseOutput, OptionalDependencyNotAvailable, _LazyModule, get_objects_from_module, is_torch_available, is_transformers_available
@dataclass
class SafetyConfig(object):
    WEAK = {'sld_warmup_steps': 15, 'sld_guidance_scale': 20, 'sld_threshold': 0.0, 'sld_momentum_scale': 0.0, 'sld_mom_beta': 0.0}
    MEDIUM = {'sld_warmup_steps': 10, 'sld_guidance_scale': 1000, 'sld_threshold': 0.01, 'sld_momentum_scale': 0.3, 'sld_mom_beta': 0.4}
    STRONG = {'sld_warmup_steps': 7, 'sld_guidance_scale': 2000, 'sld_threshold': 0.025, 'sld_momentum_scale': 0.5, 'sld_mom_beta': 0.7}
    MAX = {'sld_warmup_steps': 0, 'sld_guidance_scale': 5000, 'sld_threshold': 1.0, 'sld_momentum_scale': 0.5, 'sld_mom_beta': 0.7}
_dummy_objects = {}
_additional_imports = {}
_import_structure = {}
_additional_imports.update({'SafetyConfig': SafetyConfig})
try:
    if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ...utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(get_objects_from_module(dummy_torch_and_transformers_objects))
else: _import_structure.update({'pipeline_output': ['StableDiffusionSafePipelineOutput'], 'pipeline_stable_diffusion_safe': ['StableDiffusionPipelineSafe'], 'safety_checker': ['StableDiffusionSafetyChecker']})
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import *
    else:
        from .pipeline_output import StableDiffusionSafePipelineOutput
        from .pipeline_stable_diffusion_safe import StableDiffusionPipelineSafe
        from .safety_checker import SafeStableDiffusionSafetyChecker
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
    for name, value in _additional_imports.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
