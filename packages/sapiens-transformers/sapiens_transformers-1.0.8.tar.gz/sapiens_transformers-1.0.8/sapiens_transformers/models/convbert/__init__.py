"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_convbert': ['ConvBertConfig', 'ConvBertOnnxConfig'], 'tokenization_convbert': ['ConvBertTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_convbert_fast"] = ["ConvBertTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_convbert"] = ["ConvBertForMaskedLM", "ConvBertForMultipleChoice", "ConvBertForQuestionAnswering", "ConvBertForSequenceClassification", "ConvBertForTokenClassification", "ConvBertLayer", "ConvBertModel", "ConvBertPreTrainedModel", "load_tf_weights_in_convbert"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_convbert"] = ["TFConvBertForMaskedLM", "TFConvBertForMultipleChoice", "TFConvBertForQuestionAnswering", "TFConvBertForSequenceClassification", "TFConvBertForTokenClassification", "TFConvBertLayer", "TFConvBertModel", "TFConvBertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_convbert import ConvBertConfig, ConvBertOnnxConfig
    from .tokenization_convbert import ConvBertTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_convbert_fast import ConvBertTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_convbert import (ConvBertForMaskedLM, ConvBertForMultipleChoice, ConvBertForQuestionAnswering, ConvBertForSequenceClassification, ConvBertForTokenClassification,
        ConvBertLayer, ConvBertModel, ConvBertPreTrainedModel, load_tf_weights_in_convbert)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_convbert import (TFConvBertForMaskedLM, TFConvBertForMultipleChoice, TFConvBertForQuestionAnswering, TFConvBertForSequenceClassification, TFConvBertForTokenClassification, TFConvBertLayer, TFConvBertModel, TFConvBertPreTrainedModel)
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
