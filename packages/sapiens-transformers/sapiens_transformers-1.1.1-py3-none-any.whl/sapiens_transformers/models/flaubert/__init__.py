"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available
_import_structure = {'configuration_flaubert': ['FlaubertConfig', 'FlaubertOnnxConfig'], 'tokenization_flaubert': ['FlaubertTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_flaubert"] = ["FlaubertForMultipleChoice", "FlaubertForQuestionAnswering", "FlaubertForQuestionAnsweringSimple", "FlaubertForSequenceClassification",
    "FlaubertForTokenClassification", "FlaubertModel", "FlaubertWithLMHeadModel", "FlaubertPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_flaubert"] = ["TFFlaubertForMultipleChoice", "TFFlaubertForQuestionAnsweringSimple", "TFFlaubertForSequenceClassification", "TFFlaubertForTokenClassification",
    "TFFlaubertModel", "TFFlaubertPreTrainedModel", "TFFlaubertWithLMHeadModel"]
if TYPE_CHECKING:
    from .configuration_flaubert import FlaubertConfig, FlaubertOnnxConfig
    from .tokenization_flaubert import FlaubertTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_flaubert import (FlaubertForMultipleChoice, FlaubertForQuestionAnswering, FlaubertForQuestionAnsweringSimple, FlaubertForSequenceClassification,
        FlaubertForTokenClassification, FlaubertModel, FlaubertPreTrainedModel, FlaubertWithLMHeadModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_flaubert import (TFFlaubertForMultipleChoice, TFFlaubertForQuestionAnsweringSimple, TFFlaubertForSequenceClassification, TFFlaubertForTokenClassification,
        TFFlaubertModel, TFFlaubertPreTrainedModel, TFFlaubertWithLMHeadModel)
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
