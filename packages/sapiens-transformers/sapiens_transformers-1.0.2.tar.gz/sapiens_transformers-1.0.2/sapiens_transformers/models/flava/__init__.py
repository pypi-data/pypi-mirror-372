"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_vision_available
_import_structure = {'configuration_flava': ['FlavaConfig', 'FlavaImageCodebookConfig', 'FlavaImageConfig', 'FlavaMultimodalConfig', 'FlavaTextConfig']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_flava"] = ["FlavaFeatureExtractor"]
    _import_structure["image_processing_flava"] = ["FlavaImageProcessor"]
    _import_structure["processing_flava"] = ["FlavaProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flava"] = ["FlavaForPreTraining", "FlavaImageCodebook", "FlavaImageModel", "FlavaModel", "FlavaMultimodalModel", "FlavaPreTrainedModel", "FlavaTextModel"]
if TYPE_CHECKING:
    from .configuration_flava import (FlavaConfig, FlavaImageCodebookConfig, FlavaImageConfig, FlavaMultimodalConfig, FlavaTextConfig)
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_flava import FlavaFeatureExtractor
        from .image_processing_flava import FlavaImageProcessor
        from .processing_flava import FlavaProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flava import (FlavaForPreTraining, FlavaImageCodebook, FlavaImageModel, FlavaModel, FlavaMultimodalModel, FlavaPreTrainedModel, FlavaTextModel)
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
