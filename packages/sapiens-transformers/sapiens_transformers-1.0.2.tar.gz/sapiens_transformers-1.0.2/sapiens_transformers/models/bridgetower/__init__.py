"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_vision_available
_import_structure = {'configuration_bridgetower': ['BridgeTowerConfig', 'BridgeTowerTextConfig', 'BridgeTowerVisionConfig'], 'processing_bridgetower': ['BridgeTowerProcessor']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["image_processing_bridgetower"] = ["BridgeTowerImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_bridgetower"] = ["BridgeTowerForContrastiveLearning", "BridgeTowerForImageAndTextRetrieval", "BridgeTowerForMaskedLM", "BridgeTowerModel", "BridgeTowerPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_bridgetower import (BridgeTowerConfig, BridgeTowerTextConfig, BridgeTowerVisionConfig)
    from .processing_bridgetower import BridgeTowerProcessor
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .image_processing_bridgetower import BridgeTowerImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_bridgetower import (BridgeTowerForContrastiveLearning, BridgeTowerForImageAndTextRetrieval, BridgeTowerForMaskedLM, BridgeTowerModel, BridgeTowerPreTrainedModel)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
