"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available, is_vision_available)
_import_structure = {'configuration_layoutlmv2': ['LayoutLMv2Config'], 'processing_layoutlmv2': ['LayoutLMv2Processor'], 'tokenization_layoutlmv2': ['LayoutLMv2Tokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_layoutlmv2_fast"] = ["LayoutLMv2TokenizerFast"]
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_layoutlmv2"] = ["LayoutLMv2FeatureExtractor"]
    _import_structure["image_processing_layoutlmv2"] = ["LayoutLMv2ImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_layoutlmv2"] = ["LayoutLMv2ForQuestionAnswering", "LayoutLMv2ForSequenceClassification", "LayoutLMv2ForTokenClassification",
    "LayoutLMv2Layer", "LayoutLMv2Model", "LayoutLMv2PreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_layoutlmv2 import LayoutLMv2Config
    from .processing_layoutlmv2 import LayoutLMv2Processor
    from .tokenization_layoutlmv2 import LayoutLMv2Tokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_layoutlmv2_fast import LayoutLMv2TokenizerFast
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .feature_extraction_layoutlmv2 import LayoutLMv2FeatureExtractor, LayoutLMv2ImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_layoutlmv2 import (LayoutLMv2ForQuestionAnswering, LayoutLMv2ForSequenceClassification, LayoutLMv2ForTokenClassification, LayoutLMv2Layer,
        LayoutLMv2Model, LayoutLMv2PreTrainedModel)
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
