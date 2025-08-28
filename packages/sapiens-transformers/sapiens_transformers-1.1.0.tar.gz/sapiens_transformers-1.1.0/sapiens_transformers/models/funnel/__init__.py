"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_funnel': ['FunnelConfig'], 'convert_funnel_original_tf_checkpoint_to_pytorch': [], 'tokenization_funnel': ['FunnelTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_funnel_fast"] = ["FunnelTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_funnel"] = ["FunnelBaseModel", "FunnelForMaskedLM", "FunnelForMultipleChoice", "FunnelForPreTraining", "FunnelForQuestionAnswering",
    "FunnelForSequenceClassification", "FunnelForTokenClassification", "FunnelModel", "FunnelPreTrainedModel", "load_tf_weights_in_funnel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_funnel"] = ["TFFunnelBaseModel", "TFFunnelForMaskedLM", "TFFunnelForMultipleChoice", "TFFunnelForPreTraining", "TFFunnelForQuestionAnswering",
    "TFFunnelForSequenceClassification", "TFFunnelForTokenClassification", "TFFunnelModel", "TFFunnelPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_funnel import FunnelConfig
    from .tokenization_funnel import FunnelTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_funnel_fast import FunnelTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_funnel import (FunnelBaseModel, FunnelForMaskedLM, FunnelForMultipleChoice, FunnelForPreTraining, FunnelForQuestionAnswering, FunnelForSequenceClassification,
        FunnelForTokenClassification, FunnelModel, FunnelPreTrainedModel, load_tf_weights_in_funnel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_funnel import (TFFunnelBaseModel, TFFunnelForMaskedLM, TFFunnelForMultipleChoice, TFFunnelForPreTraining, TFFunnelForQuestionAnswering, TFFunnelForSequenceClassification,
        TFFunnelForTokenClassification, TFFunnelModel, TFFunnelPreTrainedModel)
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
