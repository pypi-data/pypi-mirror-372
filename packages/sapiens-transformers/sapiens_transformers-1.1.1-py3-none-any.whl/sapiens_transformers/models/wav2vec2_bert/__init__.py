"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available
_import_structure = {'configuration_wav2vec2_bert': ['Wav2Vec2BertConfig'], 'processing_wav2vec2_bert': ['Wav2Vec2BertProcessor']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_wav2vec2_bert"] = ["Wav2Vec2BertForAudioFrameClassification", "Wav2Vec2BertForCTC", "Wav2Vec2BertForSequenceClassification",
"Wav2Vec2BertForXVector", "Wav2Vec2BertModel", "Wav2Vec2BertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_wav2vec2_bert import (Wav2Vec2BertConfig)
    from .processing_wav2vec2_bert import Wav2Vec2BertProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_wav2vec2_bert import (Wav2Vec2BertForAudioFrameClassification, Wav2Vec2BertForCTC, Wav2Vec2BertForSequenceClassification, Wav2Vec2BertForXVector, Wav2Vec2BertModel, Wav2Vec2BertPreTrainedModel)
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
