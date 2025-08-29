"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_deberta_v2': ['DebertaV2Config', 'DebertaV2OnnxConfig'], 'tokenization_deberta_v2': ['DebertaV2Tokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_deberta_v2_fast"] = ["DebertaV2TokenizerFast"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_deberta_v2"] = ["TFDebertaV2ForMaskedLM", "TFDebertaV2ForQuestionAnswering", "TFDebertaV2ForMultipleChoice", "TFDebertaV2ForSequenceClassification",
    "TFDebertaV2ForTokenClassification", "TFDebertaV2Model", "TFDebertaV2PreTrainedModel"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_deberta_v2"] = ["DebertaV2ForMaskedLM", "DebertaV2ForMultipleChoice", "DebertaV2ForQuestionAnswering", "DebertaV2ForSequenceClassification", "DebertaV2ForTokenClassification", "DebertaV2Model", "DebertaV2PreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_deberta_v2 import (DebertaV2Config, DebertaV2OnnxConfig)
    from .tokenization_deberta_v2 import DebertaV2Tokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_deberta_v2_fast import DebertaV2TokenizerFast
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_deberta_v2 import (TFDebertaV2ForMaskedLM, TFDebertaV2ForMultipleChoice, TFDebertaV2ForQuestionAnswering, TFDebertaV2ForSequenceClassification, TFDebertaV2ForTokenClassification, TFDebertaV2Model, TFDebertaV2PreTrainedModel)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_deberta_v2 import (DebertaV2ForMaskedLM, DebertaV2ForMultipleChoice, DebertaV2ForQuestionAnswering, DebertaV2ForSequenceClassification, DebertaV2ForTokenClassification, DebertaV2Model, DebertaV2PreTrainedModel)
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
