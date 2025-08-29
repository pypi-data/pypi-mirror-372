"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available, is_vision_available)
_import_structure = {"configuration_segformer": ["SegformerConfig", "SegformerOnnxConfig"]}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_segformer"] = ["SegformerFeatureExtractor"]
    _import_structure["image_processing_segformer"] = ["SegformerImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_segformer"] = ["SegformerDecodeHead", "SegformerForImageClassification", "SegformerForSemanticSegmentation",
"SegformerLayer", "SegformerModel", "SegformerPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_segformer"] = ["TFSegformerDecodeHead", "TFSegformerForImageClassification", "TFSegformerForSemanticSegmentation",
"TFSegformerModel", "TFSegformerPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_segformer import SegformerConfig, SegformerOnnxConfig
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_segformer import SegformerFeatureExtractor
        from .image_processing_segformer import SegformerImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_segformer import (SegformerDecodeHead, SegformerForImageClassification, SegformerForSemanticSegmentation, SegformerLayer, SegformerModel, SegformerPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_segformer import (TFSegformerDecodeHead, TFSegformerForImageClassification, TFSegformerForSemanticSegmentation, TFSegformerModel, TFSegformerPreTrainedModel)
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
