"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_roformer': ['RoFormerConfig', 'RoFormerOnnxConfig'], 'tokenization_roformer': ['RoFormerTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_roformer_fast"] = ["RoFormerTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_roformer"] = ["RoFormerForCausalLM", "RoFormerForMaskedLM", "RoFormerForMultipleChoice", "RoFormerForQuestionAnswering",
"RoFormerForSequenceClassification", "RoFormerForTokenClassification", "RoFormerLayer", "RoFormerModel", "RoFormerPreTrainedModel", "load_tf_weights_in_roformer"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_roformer"] = ["TFRoFormerForCausalLM", "TFRoFormerForMaskedLM", "TFRoFormerForMultipleChoice", "TFRoFormerForQuestionAnswering",
"TFRoFormerForSequenceClassification", "TFRoFormerForTokenClassification", "TFRoFormerLayer", "TFRoFormerModel", "TFRoFormerPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_roformer"] = ["FlaxRoFormerForMaskedLM", "FlaxRoFormerForMultipleChoice", "FlaxRoFormerForQuestionAnswering", "FlaxRoFormerForSequenceClassification",
"FlaxRoFormerForTokenClassification", "FlaxRoFormerModel", "FlaxRoFormerPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_roformer import RoFormerConfig, RoFormerOnnxConfig
    from .tokenization_roformer import RoFormerTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_roformer_fast import RoFormerTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_roformer import (RoFormerForCausalLM, RoFormerForMaskedLM, RoFormerForMultipleChoice, RoFormerForQuestionAnswering, RoFormerForSequenceClassification,
    RoFormerForTokenClassification, RoFormerLayer, RoFormerModel, RoFormerPreTrainedModel, load_tf_weights_in_roformer)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_roformer import (TFRoFormerForCausalLM, TFRoFormerForMaskedLM, TFRoFormerForMultipleChoice, TFRoFormerForQuestionAnswering, TFRoFormerForSequenceClassification,
    TFRoFormerForTokenClassification, TFRoFormerLayer, TFRoFormerModel, TFRoFormerPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_roformer import (FlaxRoFormerForMaskedLM, FlaxRoFormerForMultipleChoice, FlaxRoFormerForQuestionAnswering, FlaxRoFormerForSequenceClassification,
    FlaxRoFormerForTokenClassification, FlaxRoFormerModel, FlaxRoFormerPreTrainedModel)
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
