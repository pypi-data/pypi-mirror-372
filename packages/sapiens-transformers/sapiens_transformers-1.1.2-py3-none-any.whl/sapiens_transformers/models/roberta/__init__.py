"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_roberta': ['RobertaConfig', 'RobertaOnnxConfig'], 'tokenization_roberta': ['RobertaTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_roberta_fast"] = ["RobertaTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_roberta"] = ["RobertaForCausalLM", "RobertaForMaskedLM", "RobertaForMultipleChoice", "RobertaForQuestionAnswering", "RobertaForSequenceClassification",
"RobertaForTokenClassification", "RobertaModel", "RobertaPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_roberta"] = ["TFRobertaForCausalLM", "TFRobertaForMaskedLM", "TFRobertaForMultipleChoice", "TFRobertaForQuestionAnswering",
"TFRobertaForSequenceClassification", "TFRobertaForTokenClassification", "TFRobertaMainLayer", "TFRobertaModel", "TFRobertaPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_roberta"] = ["FlaxRobertaForCausalLM", "FlaxRobertaForMaskedLM", "FlaxRobertaForMultipleChoice", "FlaxRobertaForQuestionAnswering",
"FlaxRobertaForSequenceClassification", "FlaxRobertaForTokenClassification", "FlaxRobertaModel", "FlaxRobertaPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_roberta import RobertaConfig, RobertaOnnxConfig
    from .tokenization_roberta import RobertaTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_roberta_fast import RobertaTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_roberta import (RobertaForCausalLM, RobertaForMaskedLM, RobertaForMultipleChoice, RobertaForQuestionAnswering, RobertaForSequenceClassification,
    RobertaForTokenClassification, RobertaModel, RobertaPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_roberta import (TFRobertaForCausalLM, TFRobertaForMaskedLM, TFRobertaForMultipleChoice, TFRobertaForQuestionAnswering, TFRobertaForSequenceClassification,
    TFRobertaForTokenClassification, TFRobertaMainLayer, TFRobertaModel, TFRobertaPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_roberta import (FlaxRobertaForCausalLM, FlaxRobertaForMaskedLM, FlaxRobertaForMultipleChoice, FlaxRobertaForQuestionAnswering,
    FlaxRobertaForSequenceClassification, FlaxRobertaForTokenClassification, FlaxRobertaModel, FlaxRobertaPreTrainedModel)
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
