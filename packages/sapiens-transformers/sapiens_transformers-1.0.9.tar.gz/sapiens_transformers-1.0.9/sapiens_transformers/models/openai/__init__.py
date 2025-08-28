"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_openai': ['OpenAIGPTConfig'], 'tokenization_openai': ['OpenAIGPTTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_openai_fast"] = ["OpenAIGPTTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_openai"] = ["OpenAIGPTDoubleHeadsModel", "OpenAIGPTForSequenceClassification", "OpenAIGPTLMHeadModel", "OpenAIGPTModel",
    "OpenAIGPTPreTrainedModel", "load_tf_weights_in_openai_gpt"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_openai"] = ["TFOpenAIGPTDoubleHeadsModel", "TFOpenAIGPTForSequenceClassification", "TFOpenAIGPTLMHeadModel", "TFOpenAIGPTMainLayer",
    "TFOpenAIGPTModel", "TFOpenAIGPTPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_openai import OpenAIGPTConfig
    from .tokenization_openai import OpenAIGPTTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_openai_fast import OpenAIGPTTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_openai import (OpenAIGPTDoubleHeadsModel, OpenAIGPTForSequenceClassification, OpenAIGPTLMHeadModel, OpenAIGPTModel, OpenAIGPTPreTrainedModel,
        load_tf_weights_in_openai_gpt)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_openai import (TFOpenAIGPTDoubleHeadsModel, TFOpenAIGPTForSequenceClassification, TFOpenAIGPTLMHeadModel, TFOpenAIGPTMainLayer,
        TFOpenAIGPTModel, TFOpenAIGPTPreTrainedModel)
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
