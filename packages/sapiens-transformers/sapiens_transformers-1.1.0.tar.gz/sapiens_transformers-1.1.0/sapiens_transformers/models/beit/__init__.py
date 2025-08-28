"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_torch_available, is_vision_available)
_import_structure = {"configuration_beit": ["BeitConfig", "BeitOnnxConfig"]}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_beit"] = ["BeitFeatureExtractor"]
    _import_structure["image_processing_beit"] = ["BeitImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_beit"] = ["BeitForImageClassification", "BeitForMaskedImageModeling", "BeitForSemanticSegmentation", "BeitModel", "BeitPreTrainedModel", "BeitBackbone"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_beit"] = ["FlaxBeitForImageClassification", "FlaxBeitForMaskedImageModeling", "FlaxBeitModel", "FlaxBeitPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_beit import BeitConfig, BeitOnnxConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_beit import BeitFeatureExtractor
        from .image_processing_beit import BeitImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_beit import (BeitBackbone, BeitForImageClassification, BeitForMaskedImageModeling, BeitForSemanticSegmentation, BeitModel, BeitPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_beit import (FlaxBeitForImageClassification, FlaxBeitForMaskedImageModeling, FlaxBeitModel, FlaxBeitPreTrainedModel)
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
