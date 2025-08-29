"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_torchaudio_available)
_import_structure = {'configuration_musicgen_melody': ['MusicgenMelodyConfig', 'MusicgenMelodyDecoderConfig']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_musicgen_melody"] = ["MusicgenMelodyForConditionalGeneration", "MusicgenMelodyForCausalLM", "MusicgenMelodyModel", "MusicgenMelodyPreTrainedModel"]
try:
    if not is_torchaudio_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_musicgen_melody"] = ["MusicgenMelodyFeatureExtractor"]
    _import_structure["processing_musicgen_melody"] = ["MusicgenMelodyProcessor"]
if TYPE_CHECKING:
    from .configuration_musicgen_melody import (MusicgenMelodyConfig, MusicgenMelodyDecoderConfig)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_musicgen_melody import (MusicgenMelodyForCausalLM, MusicgenMelodyForConditionalGeneration, MusicgenMelodyModel, MusicgenMelodyPreTrainedModel)
    try:
        if not is_torchaudio_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_musicgen_melody import MusicgenMelodyFeatureExtractor
        from .processing_musicgen_melody import MusicgenMelodyProcessor
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
