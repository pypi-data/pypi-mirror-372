"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available, is_vision_available)
_import_structure = {'configuration_mobilevit': ['MobileViTConfig', 'MobileViTOnnxConfig']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_mobilevit"] = ["MobileViTFeatureExtractor"]
    _import_structure["image_processing_mobilevit"] = ["MobileViTImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_mobilevit"] = ["MobileViTForImageClassification", "MobileViTForSemanticSegmentation", "MobileViTModel", "MobileViTPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_mobilevit"] = ["TFMobileViTForImageClassification", "TFMobileViTForSemanticSegmentation", "TFMobileViTModel", "TFMobileViTPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_mobilevit import MobileViTConfig, MobileViTOnnxConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_mobilevit import MobileViTFeatureExtractor
        from .image_processing_mobilevit import MobileViTImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_mobilevit import (MobileViTForImageClassification, MobileViTForSemanticSegmentation, MobileViTModel, MobileViTPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_mobilevit import (TFMobileViTForImageClassification, TFMobileViTForSemanticSegmentation, TFMobileViTModel, TFMobileViTPreTrainedModel)
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
