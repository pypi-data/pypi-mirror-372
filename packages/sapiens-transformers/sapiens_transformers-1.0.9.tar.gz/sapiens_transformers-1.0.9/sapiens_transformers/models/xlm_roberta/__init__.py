"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_sentencepiece_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_xlm_roberta': ['XLMRobertaConfig', 'XLMRobertaOnnxConfig']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_xlm_roberta"] = ["XLMRobertaTokenizer"]
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_xlm_roberta_fast"] = ["XLMRobertaTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_xlm_roberta"] = ["XLMRobertaForCausalLM", "XLMRobertaForMaskedLM", "XLMRobertaForMultipleChoice", "XLMRobertaForQuestionAnswering",
"XLMRobertaForSequenceClassification", "XLMRobertaForTokenClassification", "XLMRobertaModel", "XLMRobertaPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_xlm_roberta"] = ["TFXLMRobertaForCausalLM", "TFXLMRobertaForMaskedLM", "TFXLMRobertaForMultipleChoice", "TFXLMRobertaForQuestionAnswering",
"TFXLMRobertaForSequenceClassification", "TFXLMRobertaForTokenClassification", "TFXLMRobertaModel", "TFXLMRobertaPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_xlm_roberta"] = ["FlaxXLMRobertaForMaskedLM", "FlaxXLMRobertaForCausalLM", "FlaxXLMRobertaForMultipleChoice", "FlaxXLMRobertaForQuestionAnswering",
"FlaxXLMRobertaForSequenceClassification", "FlaxXLMRobertaForTokenClassification", "FlaxXLMRobertaModel", "FlaxXLMRobertaPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_xlm_roberta import (XLMRobertaConfig, XLMRobertaOnnxConfig)
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_xlm_roberta import XLMRobertaTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_xlm_roberta_fast import XLMRobertaTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_xlm_roberta import (XLMRobertaForCausalLM, XLMRobertaForMaskedLM, XLMRobertaForMultipleChoice, XLMRobertaForQuestionAnswering,
    XLMRobertaForSequenceClassification, XLMRobertaForTokenClassification, XLMRobertaModel, XLMRobertaPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_xlm_roberta import (TFXLMRobertaForCausalLM, TFXLMRobertaForMaskedLM, TFXLMRobertaForMultipleChoice, TFXLMRobertaForQuestionAnswering,
    TFXLMRobertaForSequenceClassification, TFXLMRobertaForTokenClassification, TFXLMRobertaModel, TFXLMRobertaPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_xlm_roberta import (FlaxXLMRobertaForCausalLM, FlaxXLMRobertaForMaskedLM, FlaxXLMRobertaForMultipleChoice, FlaxXLMRobertaForQuestionAnswering,
    FlaxXLMRobertaForSequenceClassification, FlaxXLMRobertaForTokenClassification, FlaxXLMRobertaModel, FlaxXLMRobertaPreTrainedModel)
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
