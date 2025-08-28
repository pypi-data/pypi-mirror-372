"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_bart': ['BartConfig', 'BartOnnxConfig'], 'tokenization_bart': ['BartTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_bart_fast"] = ["BartTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_bart"] = ["BartForCausalLM", "BartForConditionalGeneration", "BartForQuestionAnswering", "BartForSequenceClassification", "BartModel",
    "BartPreTrainedModel", "BartPretrainedModel", "PretrainedBartModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_bart"] = ["TFBartForConditionalGeneration", "TFBartForSequenceClassification", "TFBartModel", "TFBartPretrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_flax_bart"] = ["FlaxBartDecoderPreTrainedModel", "FlaxBartForCausalLM", "FlaxBartForConditionalGeneration", "FlaxBartForQuestionAnswering",
    "FlaxBartForSequenceClassification", "FlaxBartModel", "FlaxBartPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_bart import BartConfig, BartOnnxConfig
    from .tokenization_bart import BartTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_bart_fast import BartTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_bart import (BartForCausalLM, BartForConditionalGeneration, BartForQuestionAnswering, BartForSequenceClassification, BartModel, BartPreTrainedModel, BartPretrainedModel, PretrainedBartModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_bart import (TFBartForConditionalGeneration, TFBartForSequenceClassification, TFBartModel, TFBartPretrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_flax_bart import (FlaxBartDecoderPreTrainedModel, FlaxBartForCausalLM, FlaxBartForConditionalGeneration, FlaxBartForQuestionAnswering, FlaxBartForSequenceClassification,
        FlaxBartModel, FlaxBartPreTrainedModel)
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
