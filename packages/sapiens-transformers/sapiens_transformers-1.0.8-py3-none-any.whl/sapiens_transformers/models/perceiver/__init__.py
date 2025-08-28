"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available, is_vision_available)
_import_structure = {'configuration_perceiver': ['PerceiverConfig', 'PerceiverOnnxConfig'], 'tokenization_perceiver': ['PerceiverTokenizer']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_perceiver"] = ["PerceiverFeatureExtractor"]
    _import_structure["image_processing_perceiver"] = ["PerceiverImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_perceiver"] = ["PerceiverForImageClassificationConvProcessing", "PerceiverForImageClassificationFourier", "PerceiverForImageClassificationLearned",
    "PerceiverForMaskedLM", "PerceiverForMultimodalAutoencoding", "PerceiverForOpticalFlow", "PerceiverForSequenceClassification", "PerceiverLayer", "PerceiverModel", "PerceiverPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_perceiver import PerceiverConfig, PerceiverOnnxConfig
    from .tokenization_perceiver import PerceiverTokenizer
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_perceiver import PerceiverFeatureExtractor
        from .image_processing_perceiver import PerceiverImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_perceiver import (PerceiverForImageClassificationConvProcessing, PerceiverForImageClassificationFourier, PerceiverForImageClassificationLearned,
        PerceiverForMaskedLM, PerceiverForMultimodalAutoencoding, PerceiverForOpticalFlow, PerceiverForSequenceClassification, PerceiverLayer, PerceiverModel, PerceiverPreTrainedModel)
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
