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
    from ...utils import dummy_pt_objects
    _dummy_objects.update(get_objects_from_module(dummy_pt_objects))
else:
    _import_structure['scheduling_karras_ve'] = ['KarrasVeScheduler']
    _import_structure['scheduling_sde_vp'] = ['ScoreSdeVpScheduler']
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ...utils.dummy_pt_objects import *
    else:
        from .scheduling_karras_ve import KarrasVeScheduler
        from .scheduling_sde_vp import ScoreSdeVpScheduler
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
