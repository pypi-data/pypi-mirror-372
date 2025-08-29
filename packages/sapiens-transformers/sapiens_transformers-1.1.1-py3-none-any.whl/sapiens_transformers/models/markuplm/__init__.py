"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available
_import_structure = {'configuration_markuplm': ['MarkupLMConfig'], 'feature_extraction_markuplm': ['MarkupLMFeatureExtractor'], 'processing_markuplm': ['MarkupLMProcessor'], 'tokenization_markuplm': ['MarkupLMTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_markuplm_fast"] = ["MarkupLMTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_markuplm"] = ["MarkupLMForQuestionAnswering", "MarkupLMForSequenceClassification", "MarkupLMForTokenClassification", "MarkupLMModel", "MarkupLMPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_markuplm import MarkupLMConfig
    from .feature_extraction_markuplm import MarkupLMFeatureExtractor
    from .processing_markuplm import MarkupLMProcessor
    from .tokenization_markuplm import MarkupLMTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_markuplm_fast import MarkupLMTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_markuplm import (MarkupLMForQuestionAnswering, MarkupLMForSequenceClassification, MarkupLMForTokenClassification, MarkupLMModel, MarkupLMPreTrainedModel)
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
