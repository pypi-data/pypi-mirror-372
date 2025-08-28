"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_electra': ['ElectraConfig', 'ElectraOnnxConfig'], 'tokenization_electra': ['ElectraTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_electra_fast"] = ["ElectraTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_electra"] = ["ElectraForCausalLM", "ElectraForMaskedLM", "ElectraForMultipleChoice", "ElectraForPreTraining", "ElectraForQuestionAnswering",
    "ElectraForSequenceClassification", "ElectraForTokenClassification", "ElectraModel", "ElectraPreTrainedModel", "load_tf_weights_in_electra"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_electra"] = ["TFElectraForMaskedLM", "TFElectraForMultipleChoice", "TFElectraForPreTraining", "TFElectraForQuestionAnswering",
    "TFElectraForSequenceClassification", "TFElectraForTokenClassification", "TFElectraModel", "TFElectraPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_flax_electra"] = ["FlaxElectraForCausalLM", "FlaxElectraForMaskedLM", "FlaxElectraForMultipleChoice", "FlaxElectraForPreTraining", "FlaxElectraForQuestionAnswering",
    "FlaxElectraForSequenceClassification", "FlaxElectraForTokenClassification", "FlaxElectraModel", "FlaxElectraPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_electra import ElectraConfig, ElectraOnnxConfig
    from .tokenization_electra import ElectraTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_electra_fast import ElectraTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_electra import (ElectraForCausalLM, ElectraForMaskedLM, ElectraForMultipleChoice, ElectraForPreTraining, ElectraForQuestionAnswering, ElectraForSequenceClassification,
        ElectraForTokenClassification, ElectraModel, ElectraPreTrainedModel, load_tf_weights_in_electra)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_electra import (TFElectraForMaskedLM, TFElectraForMultipleChoice, TFElectraForPreTraining, TFElectraForQuestionAnswering, TFElectraForSequenceClassification,
        TFElectraForTokenClassification, TFElectraModel, TFElectraPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_flax_electra import (FlaxElectraForCausalLM, FlaxElectraForMaskedLM, FlaxElectraForMultipleChoice, FlaxElectraForPreTraining, FlaxElectraForQuestionAnswering,
        FlaxElectraForSequenceClassification, FlaxElectraForTokenClassification, FlaxElectraModel, FlaxElectraPreTrainedModel)
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
