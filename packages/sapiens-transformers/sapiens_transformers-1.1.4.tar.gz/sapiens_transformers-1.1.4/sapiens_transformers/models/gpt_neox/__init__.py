"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...file_utils import _LazyModule, is_tokenizers_available, is_torch_available
from ...utils import OptionalDependencyNotAvailable
_import_structure = {"configuration_gpt_neox": ["GPTNeoXConfig"]}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_gpt_neox_fast"] = ["GPTNeoXTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_gpt_neox"] = ["GPTNeoXForCausalLM", "GPTNeoXForQuestionAnswering", "GPTNeoXForSequenceClassification", "GPTNeoXForTokenClassification",
    "GPTNeoXLayer", "GPTNeoXModel", "GPTNeoXPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_gpt_neox import GPTNeoXConfig
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_gpt_neox_fast import GPTNeoXTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_gpt_neox import (GPTNeoXForCausalLM, GPTNeoXForQuestionAnswering, GPTNeoXForSequenceClassification, GPTNeoXForTokenClassification, GPTNeoXLayer, GPTNeoXModel, GPTNeoXPreTrainedModel)
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
