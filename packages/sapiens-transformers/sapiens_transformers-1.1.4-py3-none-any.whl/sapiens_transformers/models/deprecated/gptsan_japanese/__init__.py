"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ....utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_torch_available)
_import_structure = {'configuration_gptsan_japanese': ['GPTSanJapaneseConfig'], 'tokenization_gptsan_japanese': ['GPTSanJapaneseTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_gptsan_japanese"] = ["GPTSanJapaneseForConditionalGeneration", "GPTSanJapaneseModel", "GPTSanJapanesePreTrainedModel"]
    _import_structure["tokenization_gptsan_japanese"] = ["GPTSanJapaneseTokenizer"]
if TYPE_CHECKING:
    from .configuration_gptsan_japanese import GPTSanJapaneseConfig
    from .tokenization_gptsan_japanese import GPTSanJapaneseTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_gptsan_japanese import (GPTSanJapaneseForConditionalGeneration, GPTSanJapaneseModel, GPTSanJapanesePreTrainedModel)
        from .tokenization_gptsan_japanese import GPTSanJapaneseTokenizer
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
