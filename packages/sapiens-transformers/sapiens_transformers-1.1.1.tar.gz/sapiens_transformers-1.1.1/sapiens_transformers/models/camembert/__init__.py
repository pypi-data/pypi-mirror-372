"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_sentencepiece_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_camembert': ['CamembertConfig', 'CamembertOnnxConfig']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_camembert"] = ["CamembertTokenizer"]
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_camembert_fast"] = ["CamembertTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_camembert"] = ["CamembertForCausalLM", "CamembertForMaskedLM", "CamembertForMultipleChoice", "CamembertForQuestionAnswering", "CamembertForSequenceClassification", "CamembertForTokenClassification", "CamembertModel", "CamembertPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_camembert"] = ["TFCamembertForCausalLM", "TFCamembertForMaskedLM", "TFCamembertForMultipleChoice", "TFCamembertForQuestionAnswering", "TFCamembertForSequenceClassification", "TFCamembertForTokenClassification", "TFCamembertModel", "TFCamembertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_camembert import CamembertConfig, CamembertOnnxConfig
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_camembert import CamembertTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_camembert_fast import CamembertTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_camembert import (CamembertForCausalLM, CamembertForMaskedLM, CamembertForMultipleChoice, CamembertForQuestionAnswering, CamembertForSequenceClassification, CamembertForTokenClassification, CamembertModel, CamembertPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_camembert import (TFCamembertForCausalLM, TFCamembertForMaskedLM, TFCamembertForMultipleChoice, TFCamembertForQuestionAnswering, TFCamembertForSequenceClassification, TFCamembertForTokenClassification, TFCamembertModel, TFCamembertPreTrainedModel)
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
