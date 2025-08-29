"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available
_import_structure = {'configuration_xlm': ['XLMConfig', 'XLMOnnxConfig'], 'tokenization_xlm': ['XLMTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_xlm"] = ["XLMForMultipleChoice", "XLMForQuestionAnswering", "XLMForQuestionAnsweringSimple", "XLMForSequenceClassification",
"XLMForTokenClassification", "XLMModel", "XLMPreTrainedModel", "XLMWithLMHeadModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_xlm"] = ["TFXLMForMultipleChoice", "TFXLMForQuestionAnsweringSimple", "TFXLMForSequenceClassification", "TFXLMForTokenClassification",
"TFXLMMainLayer", "TFXLMModel", "TFXLMPreTrainedModel", "TFXLMWithLMHeadModel"]
if TYPE_CHECKING:
    from .configuration_xlm import XLMConfig, XLMOnnxConfig
    from .tokenization_xlm import XLMTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_xlm import (XLMForMultipleChoice, XLMForQuestionAnswering, XLMForQuestionAnsweringSimple, XLMForSequenceClassification, XLMForTokenClassification,
    XLMModel, XLMPreTrainedModel, XLMWithLMHeadModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_xlm import (TFXLMForMultipleChoice, TFXLMForQuestionAnsweringSimple, TFXLMForSequenceClassification, TFXLMForTokenClassification,
    TFXLMMainLayer, TFXLMModel, TFXLMPreTrainedModel, TFXLMWithLMHeadModel)
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
