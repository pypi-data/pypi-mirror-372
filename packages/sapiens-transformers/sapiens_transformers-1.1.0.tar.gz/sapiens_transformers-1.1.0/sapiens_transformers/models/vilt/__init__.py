"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_vision_available
_import_structure = {"configuration_vilt": ["ViltConfig"]}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_vilt"] = ["ViltFeatureExtractor"]
    _import_structure["image_processing_vilt"] = ["ViltImageProcessor"]
    _import_structure["processing_vilt"] = ["ViltProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_vilt"] = ["ViltForImageAndTextRetrieval", "ViltForImagesAndTextClassification", "ViltForTokenClassification", "ViltForMaskedLM",
"ViltForQuestionAnswering", "ViltLayer", "ViltModel", "ViltPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_vilt import ViltConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_vilt import ViltFeatureExtractor
        from .image_processing_vilt import ViltImageProcessor
        from .processing_vilt import ViltProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_vilt import (ViltForImageAndTextRetrieval, ViltForImagesAndTextClassification, ViltForMaskedLM, ViltForQuestionAnswering, ViltForTokenClassification,
    ViltLayer, ViltModel, ViltPreTrainedModel)
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
