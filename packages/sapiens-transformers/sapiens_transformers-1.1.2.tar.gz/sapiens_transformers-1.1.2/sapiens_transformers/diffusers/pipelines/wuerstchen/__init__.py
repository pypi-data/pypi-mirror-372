'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import TYPE_CHECKING
from ...utils import DIFFUSERS_SLOW_IMPORT, OptionalDependencyNotAvailable, _LazyModule, get_objects_from_module, is_torch_available, is_transformers_available
_dummy_objects = {}
_import_structure = {}
try:
    if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ...utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(get_objects_from_module(dummy_torch_and_transformers_objects))
else:
    _import_structure['modeling_paella_vq_model'] = ['PaellaVQModel']
    _import_structure['modeling_wuerstchen_diffnext'] = ['WuerstchenDiffNeXt']
    _import_structure['modeling_wuerstchen_prior'] = ['WuerstchenPrior']
    _import_structure['pipeline_wuerstchen'] = ['WuerstchenDecoderPipeline']
    _import_structure['pipeline_wuerstchen_combined'] = ['WuerstchenCombinedPipeline']
    _import_structure['pipeline_wuerstchen_prior'] = ['DEFAULT_STAGE_C_TIMESTEPS', 'WuerstchenPriorPipeline']
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import *
    else:
        from .modeling_paella_vq_model import PaellaVQModel
        from .modeling_wuerstchen_diffnext import WuerstchenDiffNeXt
        from .modeling_wuerstchen_prior import WuerstchenPrior
        from .pipeline_wuerstchen import WuerstchenDecoderPipeline
        from .pipeline_wuerstchen_combined import WuerstchenCombinedPipeline
        from .pipeline_wuerstchen_prior import DEFAULT_STAGE_C_TIMESTEPS, WuerstchenPriorPipeline
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
