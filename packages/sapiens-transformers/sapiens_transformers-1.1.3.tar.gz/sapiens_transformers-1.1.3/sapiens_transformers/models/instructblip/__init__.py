"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available
_import_structure = {'configuration_instructblip': ['InstructBlipConfig', 'InstructBlipQFormerConfig', 'InstructBlipVisionConfig'], 'processing_instructblip': ['InstructBlipProcessor']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_instructblip"] = ["InstructBlipQFormerModel", "InstructBlipPreTrainedModel", "InstructBlipForConditionalGeneration", "InstructBlipVisionModel"]
if TYPE_CHECKING:
    from .configuration_instructblip import (InstructBlipConfig, InstructBlipQFormerConfig, InstructBlipVisionConfig)
    from .processing_instructblip import InstructBlipProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_instructblip import (InstructBlipForConditionalGeneration, InstructBlipPreTrainedModel, InstructBlipQFormerModel, InstructBlipVisionModel)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
