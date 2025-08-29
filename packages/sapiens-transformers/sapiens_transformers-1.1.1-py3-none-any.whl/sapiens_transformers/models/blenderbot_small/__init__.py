"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_blenderbot_small': ['BlenderbotSmallConfig', 'BlenderbotSmallOnnxConfig'], 'tokenization_blenderbot_small': ['BlenderbotSmallTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_blenderbot_small_fast"] = ["BlenderbotSmallTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_blenderbot_small"] = ["BlenderbotSmallForCausalLM", "BlenderbotSmallForConditionalGeneration", "BlenderbotSmallModel", "BlenderbotSmallPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_blenderbot_small"] = ["TFBlenderbotSmallForConditionalGeneration", "TFBlenderbotSmallModel", "TFBlenderbotSmallPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_blenderbot_small"] = ["FlaxBlenderbotSmallForConditionalGeneration", "FlaxBlenderbotSmallModel", "FlaxBlenderbotSmallPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_blenderbot_small import (BlenderbotSmallConfig, BlenderbotSmallOnnxConfig)
    from .tokenization_blenderbot_small import BlenderbotSmallTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_blenderbot_small_fast import BlenderbotSmallTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_blenderbot_small import (BlenderbotSmallForCausalLM, BlenderbotSmallForConditionalGeneration, BlenderbotSmallModel, BlenderbotSmallPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_blenderbot_small import (TFBlenderbotSmallForConditionalGeneration, TFBlenderbotSmallModel, TFBlenderbotSmallPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_blenderbot_small import (FlaxBlenderbotSmallForConditionalGeneration, FlaxBlenderbotSmallModel, FlaxBlenderbotSmallPreTrainedModel)
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
