"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_vision_available
_import_structure = {'configuration_maskformer': ['MaskFormerConfig'], 'configuration_maskformer_swin': ['MaskFormerSwinConfig']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_maskformer"] = ["MaskFormerFeatureExtractor"]
    _import_structure["image_processing_maskformer"] = ["MaskFormerImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_maskformer"] = ["MaskFormerForInstanceSegmentation", "MaskFormerModel", "MaskFormerPreTrainedModel"]
    _import_structure["modeling_maskformer_swin"] = ["MaskFormerSwinBackbone", "MaskFormerSwinModel", "MaskFormerSwinPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_maskformer import MaskFormerConfig
    from .configuration_maskformer_swin import MaskFormerSwinConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_maskformer import MaskFormerFeatureExtractor
        from .image_processing_maskformer import MaskFormerImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_maskformer import (MaskFormerForInstanceSegmentation, MaskFormerModel, MaskFormerPreTrainedModel)
        from .modeling_maskformer_swin import (MaskFormerSwinBackbone, MaskFormerSwinModel, MaskFormerSwinPreTrainedModel)
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
