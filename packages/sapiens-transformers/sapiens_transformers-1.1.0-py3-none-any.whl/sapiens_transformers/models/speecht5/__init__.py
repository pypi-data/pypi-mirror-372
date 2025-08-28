"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_sentencepiece_available, is_torch_available)
_import_structure = {'configuration_speecht5': ['SpeechT5Config', 'SpeechT5HifiGanConfig'], 'feature_extraction_speecht5': ['SpeechT5FeatureExtractor'], 'processing_speecht5': ['SpeechT5Processor']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_speecht5"] = ["SpeechT5Tokenizer"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_speecht5"] = ["SpeechT5ForSpeechToText", "SpeechT5ForSpeechToSpeech", "SpeechT5ForTextToSpeech", "SpeechT5Model", "SpeechT5PreTrainedModel", "SpeechT5HifiGan"]
if TYPE_CHECKING:
    from .configuration_speecht5 import (SpeechT5Config, SpeechT5HifiGanConfig)
    from .feature_extraction_speecht5 import SpeechT5FeatureExtractor
    from .processing_speecht5 import SpeechT5Processor
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_speecht5 import SpeechT5Tokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_speecht5 import (SpeechT5ForSpeechToSpeech, SpeechT5ForSpeechToText, SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Model, SpeechT5PreTrainedModel)
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
