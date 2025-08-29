"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_sentencepiece_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {"configuration_rembert": ["RemBertConfig", "RemBertOnnxConfig"]}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_rembert"] = ["RemBertTokenizer"]
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_rembert_fast"] = ["RemBertTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_rembert"] = ["RemBertForCausalLM", "RemBertForMaskedLM", "RemBertForMultipleChoice", "RemBertForQuestionAnswering", "RemBertForSequenceClassification",
"RemBertForTokenClassification", "RemBertLayer", "RemBertModel", "RemBertPreTrainedModel", "load_tf_weights_in_rembert"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_rembert"] = ["TFRemBertForCausalLM", "TFRemBertForMaskedLM", "TFRemBertForMultipleChoice", "TFRemBertForQuestionAnswering",
"TFRemBertForSequenceClassification", "TFRemBertForTokenClassification", "TFRemBertLayer", "TFRemBertModel", "TFRemBertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_rembert import RemBertConfig, RemBertOnnxConfig
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_rembert import RemBertTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_rembert_fast import RemBertTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_rembert import (RemBertForCausalLM, RemBertForMaskedLM, RemBertForMultipleChoice, RemBertForQuestionAnswering, RemBertForSequenceClassification,
    RemBertForTokenClassification, RemBertLayer, RemBertModel, RemBertPreTrainedModel, load_tf_weights_in_rembert)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_rembert import (TFRemBertForCausalLM, TFRemBertForMaskedLM, TFRemBertForMultipleChoice, TFRemBertForQuestionAnswering, TFRemBertForSequenceClassification,
    TFRemBertForTokenClassification, TFRemBertLayer, TFRemBertModel, TFRemBertPreTrainedModel)
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
