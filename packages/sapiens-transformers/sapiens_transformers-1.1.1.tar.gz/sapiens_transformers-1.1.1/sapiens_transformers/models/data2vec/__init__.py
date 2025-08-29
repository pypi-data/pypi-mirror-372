"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available
_import_structure = {'configuration_data2vec_audio': ['Data2VecAudioConfig'], 'configuration_data2vec_text': ['Data2VecTextConfig', 'Data2VecTextOnnxConfig'],
'configuration_data2vec_vision': ['Data2VecVisionConfig', 'Data2VecVisionOnnxConfig']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:pass
else:
    _import_structure["modeling_data2vec_audio"] = ["Data2VecAudioForAudioFrameClassification", "Data2VecAudioForCTC", "Data2VecAudioForSequenceClassification",
    "Data2VecAudioForXVector", "Data2VecAudioModel", "Data2VecAudioPreTrainedModel"]
    _import_structure["modeling_data2vec_text"] = ["Data2VecTextForCausalLM", "Data2VecTextForMaskedLM", "Data2VecTextForMultipleChoice", "Data2VecTextForQuestionAnswering",
    "Data2VecTextForSequenceClassification", "Data2VecTextForTokenClassification", "Data2VecTextModel", "Data2VecTextPreTrainedModel"]
    _import_structure["modeling_data2vec_vision"] = ["Data2VecVisionForImageClassification", "Data2VecVisionForMaskedImageModeling", "Data2VecVisionForSemanticSegmentation",
    "Data2VecVisionModel", "Data2VecVisionPreTrainedModel"]
if is_tf_available(): _import_structure["modeling_tf_data2vec_vision"] = ["TFData2VecVisionForImageClassification", "TFData2VecVisionForSemanticSegmentation", "TFData2VecVisionModel", "TFData2VecVisionPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_data2vec_audio import Data2VecAudioConfig
    from .configuration_data2vec_text import (Data2VecTextConfig, Data2VecTextOnnxConfig)
    from .configuration_data2vec_vision import (Data2VecVisionConfig, Data2VecVisionOnnxConfig)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_data2vec_audio import (Data2VecAudioForAudioFrameClassification, Data2VecAudioForCTC, Data2VecAudioForSequenceClassification, Data2VecAudioForXVector,
        Data2VecAudioModel, Data2VecAudioPreTrainedModel)
        from .modeling_data2vec_text import (Data2VecTextForCausalLM, Data2VecTextForMaskedLM, Data2VecTextForMultipleChoice, Data2VecTextForQuestionAnswering,
        Data2VecTextForSequenceClassification, Data2VecTextForTokenClassification, Data2VecTextModel, Data2VecTextPreTrainedModel)
        from .modeling_data2vec_vision import (Data2VecVisionForImageClassification, Data2VecVisionForMaskedImageModeling, Data2VecVisionForSemanticSegmentation,
        Data2VecVisionModel, Data2VecVisionPreTrainedModel)
    if is_tf_available(): from .modeling_tf_data2vec_vision import (TFData2VecVisionForImageClassification, TFData2VecVisionForSemanticSegmentation, TFData2VecVisionModel, TFData2VecVisionPreTrainedModel)
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
