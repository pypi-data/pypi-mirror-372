"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_longformer': ['LongformerConfig', 'LongformerOnnxConfig'], 'tokenization_longformer': ['LongformerTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_longformer_fast"] = ["LongformerTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_longformer"] = ["LongformerForMaskedLM", "LongformerForMultipleChoice", "LongformerForQuestionAnswering", "LongformerForSequenceClassification",
    "LongformerForTokenClassification", "LongformerModel", "LongformerPreTrainedModel", "LongformerSelfAttention"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_longformer"] = ["TFLongformerForMaskedLM", "TFLongformerForMultipleChoice", "TFLongformerForQuestionAnswering", "TFLongformerForSequenceClassification",
    "TFLongformerForTokenClassification", "TFLongformerModel", "TFLongformerPreTrainedModel", "TFLongformerSelfAttention"]
if TYPE_CHECKING:
    from .configuration_longformer import (LongformerConfig, LongformerOnnxConfig)
    from .tokenization_longformer import LongformerTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_longformer_fast import LongformerTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_longformer import (LongformerForMaskedLM, LongformerForMultipleChoice, LongformerForQuestionAnswering, LongformerForSequenceClassification,
        LongformerForTokenClassification, LongformerModel, LongformerPreTrainedModel, LongformerSelfAttention)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_longformer import (TFLongformerForMaskedLM, TFLongformerForMultipleChoice, TFLongformerForQuestionAnswering, TFLongformerForSequenceClassification,
        TFLongformerForTokenClassification, TFLongformerModel, TFLongformerPreTrainedModel, TFLongformerSelfAttention)
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
