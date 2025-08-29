"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_sentencepiece_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_gemma': ['GemmaConfig']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_gemma"] = ["GemmaTokenizer"]
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_gemma_fast"] = ["GemmaTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_gemma"] = ["GemmaForCausalLM", "GemmaModel", "GemmaPreTrainedModel", "GemmaForSequenceClassification", "GemmaForTokenClassification"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_gemma"] = ["FlaxGemmaForCausalLM", "FlaxGemmaModel", "FlaxGemmaPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_gemma import GemmaConfig
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_gemma import GemmaTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_gemma_fast import GemmaTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_gemma import (GemmaForCausalLM, GemmaForSequenceClassification, GemmaForTokenClassification, GemmaModel, GemmaPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_gemma import (FlaxGemmaForCausalLM, FlaxGemmaModel, FlaxGemmaPreTrainedModel)
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
