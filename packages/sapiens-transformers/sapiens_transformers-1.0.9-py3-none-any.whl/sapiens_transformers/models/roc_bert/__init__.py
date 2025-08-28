"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available
_import_structure = {'configuration_roc_bert': ['RoCBertConfig'], 'tokenization_roc_bert': ['RoCBertTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: pass
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_roc_bert"] = ["RoCBertForCausalLM", "RoCBertForMaskedLM", "RoCBertForMultipleChoice", "RoCBertForPreTraining", "RoCBertForQuestionAnswering",
"RoCBertForSequenceClassification", "RoCBertForTokenClassification", "RoCBertLayer", "RoCBertModel", "RoCBertPreTrainedModel", "load_tf_weights_in_roc_bert"]
if TYPE_CHECKING:
    from .configuration_roc_bert import RoCBertConfig
    from .tokenization_roc_bert import RoCBertTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: raise OptionalDependencyNotAvailable()
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_roc_bert import (RoCBertForCausalLM, RoCBertForMaskedLM, RoCBertForMultipleChoice, RoCBertForPreTraining, RoCBertForQuestionAnswering,
    RoCBertForSequenceClassification, RoCBertForTokenClassification, RoCBertLayer, RoCBertModel, RoCBertPreTrainedModel, load_tf_weights_in_roc_bert)
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
