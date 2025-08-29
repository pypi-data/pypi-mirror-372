"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_torch_available, is_torchvision_available, is_vision_available)
_import_structure = {"configuration_vit": ["ViTConfig", "ViTOnnxConfig"]}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_vit"] = ["ViTFeatureExtractor"]
    _import_structure["image_processing_vit"] = ["ViTImageProcessor"]
try:
    if not is_torchvision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["image_processing_vit_fast"] = ["ViTImageProcessorFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_vit"] = ["ViTForImageClassification", "ViTForMaskedImageModeling", "ViTModel", "ViTPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_vit"] = ["TFViTForImageClassification", "TFViTModel", "TFViTPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_vit"] = ["FlaxViTForImageClassification", "FlaxViTModel", "FlaxViTPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_vit import ViTConfig, ViTOnnxConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_vit import ViTFeatureExtractor
        from .image_processing_vit import ViTImageProcessor
    try:
        if not is_torchvision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .image_processing_vit_fast import ViTImageProcessorFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_vit import (ViTForImageClassification, ViTForMaskedImageModeling, ViTModel, ViTPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_vit import TFViTForImageClassification, TFViTModel, TFViTPreTrainedModel
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_vit import FlaxViTForImageClassification, FlaxViTModel, FlaxViTPreTrainedModel
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
