"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_mobilebert': ['MobileBertConfig', 'MobileBertOnnxConfig'], 'tokenization_mobilebert': ['MobileBertTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_mobilebert_fast"] = ["MobileBertTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_mobilebert"] = ["MobileBertForMaskedLM", "MobileBertForMultipleChoice", "MobileBertForNextSentencePrediction", "MobileBertForPreTraining",
    "MobileBertForQuestionAnswering", "MobileBertForSequenceClassification", "MobileBertForTokenClassification", "MobileBertLayer", "MobileBertModel", "MobileBertPreTrainedModel",
    "load_tf_weights_in_mobilebert"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_mobilebert"] = ["TFMobileBertForMaskedLM", "TFMobileBertForMultipleChoice", "TFMobileBertForNextSentencePrediction", "TFMobileBertForPreTraining",
    "TFMobileBertForQuestionAnswering", "TFMobileBertForSequenceClassification", "TFMobileBertForTokenClassification", "TFMobileBertMainLayer", "TFMobileBertModel", "TFMobileBertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_mobilebert import (MobileBertConfig, MobileBertOnnxConfig)
    from .tokenization_mobilebert import MobileBertTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_mobilebert_fast import MobileBertTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_mobilebert import (MobileBertForMaskedLM, MobileBertForMultipleChoice, MobileBertForNextSentencePrediction, MobileBertForPreTraining,
        MobileBertForQuestionAnswering, MobileBertForSequenceClassification, MobileBertForTokenClassification, MobileBertLayer, MobileBertModel,
        MobileBertPreTrainedModel, load_tf_weights_in_mobilebert)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_mobilebert import (TFMobileBertForMaskedLM, TFMobileBertForMultipleChoice, TFMobileBertForNextSentencePrediction, TFMobileBertForPreTraining,
        TFMobileBertForQuestionAnswering, TFMobileBertForSequenceClassification, TFMobileBertForTokenClassification, TFMobileBertMainLayer, TFMobileBertModel, TFMobileBertPreTrainedModel)
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
