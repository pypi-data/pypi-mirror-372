"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_sentencepiece_available, is_tf_available, is_torch_available)
_import_structure = {'configuration_speech_to_text': ['Speech2TextConfig'], 'feature_extraction_speech_to_text': ['Speech2TextFeatureExtractor'],
'processing_speech_to_text': ['Speech2TextProcessor']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_speech_to_text"] = ["Speech2TextTokenizer"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_speech_to_text"] = ["TFSpeech2TextForConditionalGeneration", "TFSpeech2TextModel", "TFSpeech2TextPreTrainedModel"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_speech_to_text"] = ["Speech2TextForConditionalGeneration", "Speech2TextModel", "Speech2TextPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_speech_to_text import Speech2TextConfig
    from .feature_extraction_speech_to_text import Speech2TextFeatureExtractor
    from .processing_speech_to_text import Speech2TextProcessor
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_speech_to_text import Speech2TextTokenizer
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_speech_to_text import (TFSpeech2TextForConditionalGeneration, TFSpeech2TextModel, TFSpeech2TextPreTrainedModel)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_speech_to_text import (Speech2TextForConditionalGeneration, Speech2TextModel, Speech2TextPreTrainedModel)
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
