"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...file_utils import _LazyModule, is_torch_available
from ...utils import OptionalDependencyNotAvailable
_import_structure = {'configuration_gpt_neox_japanese': ['GPTNeoXJapaneseConfig'], 'tokenization_gpt_neox_japanese': ['GPTNeoXJapaneseTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_gpt_neox_japanese"] = ["GPTNeoXJapaneseForCausalLM", "GPTNeoXJapaneseLayer", "GPTNeoXJapaneseModel", "GPTNeoXJapanesePreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_gpt_neox_japanese import GPTNeoXJapaneseConfig
    from .tokenization_gpt_neox_japanese import GPTNeoXJapaneseTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_gpt_neox_japanese import (GPTNeoXJapaneseForCausalLM, GPTNeoXJapaneseLayer, GPTNeoXJapaneseModel, GPTNeoXJapanesePreTrainedModel)
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
