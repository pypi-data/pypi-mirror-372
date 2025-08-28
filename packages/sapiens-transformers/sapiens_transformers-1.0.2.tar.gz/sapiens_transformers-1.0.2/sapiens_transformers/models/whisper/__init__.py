"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_whisper': ['WhisperConfig', 'WhisperOnnxConfig'], 'feature_extraction_whisper': ['WhisperFeatureExtractor'],
'processing_whisper': ['WhisperProcessor'], 'tokenization_whisper': ['WhisperTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_whisper_fast"] = ["WhisperTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_whisper"] = ["WhisperForCausalLM", "WhisperForConditionalGeneration", "WhisperModel", "WhisperPreTrainedModel", "WhisperForAudioClassification"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_whisper"] = ["TFWhisperForConditionalGeneration", "TFWhisperModel", "TFWhisperPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_whisper"] = ["FlaxWhisperForConditionalGeneration", "FlaxWhisperModel", "FlaxWhisperPreTrainedModel", "FlaxWhisperForAudioClassification"]
if TYPE_CHECKING:
    from .configuration_whisper import WhisperConfig, WhisperOnnxConfig
    from .feature_extraction_whisper import WhisperFeatureExtractor
    from .processing_whisper import WhisperProcessor
    from .tokenization_whisper import WhisperTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_whisper_fast import WhisperTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_whisper import (WhisperForAudioClassification, WhisperForCausalLM, WhisperForConditionalGeneration, WhisperModel, WhisperPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_whisper import (TFWhisperForConditionalGeneration, TFWhisperModel, TFWhisperPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_whisper import (FlaxWhisperForAudioClassification, FlaxWhisperForConditionalGeneration, FlaxWhisperModel, FlaxWhisperPreTrainedModel)
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
