"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_torch_available)
_import_structure = {'configuration_roberta_prelayernorm': ['RobertaPreLayerNormConfig', 'RobertaPreLayerNormOnnxConfig']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_roberta_prelayernorm"] = ["RobertaPreLayerNormForCausalLM", "RobertaPreLayerNormForMaskedLM", "RobertaPreLayerNormForMultipleChoice",
"RobertaPreLayerNormForQuestionAnswering", "RobertaPreLayerNormForSequenceClassification", "RobertaPreLayerNormForTokenClassification", "RobertaPreLayerNormModel", "RobertaPreLayerNormPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_roberta_prelayernorm"] = ["TFRobertaPreLayerNormForCausalLM", "TFRobertaPreLayerNormForMaskedLM", "TFRobertaPreLayerNormForMultipleChoice",
"TFRobertaPreLayerNormForQuestionAnswering", "TFRobertaPreLayerNormForSequenceClassification", "TFRobertaPreLayerNormForTokenClassification", "TFRobertaPreLayerNormMainLayer",
"TFRobertaPreLayerNormModel", "TFRobertaPreLayerNormPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_roberta_prelayernorm"] = ["FlaxRobertaPreLayerNormForCausalLM", "FlaxRobertaPreLayerNormForMaskedLM", "FlaxRobertaPreLayerNormForMultipleChoice",
"FlaxRobertaPreLayerNormForQuestionAnswering", "FlaxRobertaPreLayerNormForSequenceClassification", "FlaxRobertaPreLayerNormForTokenClassification",
"FlaxRobertaPreLayerNormModel", "FlaxRobertaPreLayerNormPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_roberta_prelayernorm import (RobertaPreLayerNormConfig, RobertaPreLayerNormOnnxConfig)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_roberta_prelayernorm import (RobertaPreLayerNormForCausalLM, RobertaPreLayerNormForMaskedLM, RobertaPreLayerNormForMultipleChoice,
    RobertaPreLayerNormForQuestionAnswering, RobertaPreLayerNormForSequenceClassification, RobertaPreLayerNormForTokenClassification, RobertaPreLayerNormModel,
    RobertaPreLayerNormPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_roberta_prelayernorm import (TFRobertaPreLayerNormForCausalLM, TFRobertaPreLayerNormForMaskedLM, TFRobertaPreLayerNormForMultipleChoice,
    TFRobertaPreLayerNormForQuestionAnswering, TFRobertaPreLayerNormForSequenceClassification, TFRobertaPreLayerNormForTokenClassification, TFRobertaPreLayerNormMainLayer,
    TFRobertaPreLayerNormModel, TFRobertaPreLayerNormPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_roberta_prelayernorm import (FlaxRobertaPreLayerNormForCausalLM, FlaxRobertaPreLayerNormForMaskedLM, FlaxRobertaPreLayerNormForMultipleChoice,
    FlaxRobertaPreLayerNormForQuestionAnswering, FlaxRobertaPreLayerNormForSequenceClassification, FlaxRobertaPreLayerNormForTokenClassification, FlaxRobertaPreLayerNormModel,
    FlaxRobertaPreLayerNormPreTrainedModel)
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
