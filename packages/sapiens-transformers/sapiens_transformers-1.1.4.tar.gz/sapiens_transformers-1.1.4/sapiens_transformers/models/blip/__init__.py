"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available, is_vision_available)
_import_structure = {'configuration_blip': ['BlipConfig', 'BlipTextConfig', 'BlipVisionConfig'], 'processing_blip': ['BlipProcessor']}
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["image_processing_blip"] = ["BlipImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_blip"] = ["BlipModel", "BlipPreTrainedModel", "BlipForConditionalGeneration", "BlipForQuestionAnswering", "BlipVisionModel", "BlipTextModel", "BlipForImageTextRetrieval"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_blip"] = ["TFBlipModel", "TFBlipPreTrainedModel", "TFBlipForConditionalGeneration", "TFBlipForQuestionAnswering", "TFBlipVisionModel", "TFBlipTextModel", "TFBlipForImageTextRetrieval"]
if TYPE_CHECKING:
    from .configuration_blip import BlipConfig, BlipTextConfig, BlipVisionConfig
    from .processing_blip import BlipProcessor
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .image_processing_blip import BlipImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_blip import (BlipForConditionalGeneration, BlipForImageTextRetrieval, BlipForQuestionAnswering, BlipModel, BlipPreTrainedModel, BlipTextModel, BlipVisionModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_blip import (TFBlipForConditionalGeneration, TFBlipForImageTextRetrieval, TFBlipForQuestionAnswering, TFBlipModel, TFBlipPreTrainedModel, TFBlipTextModel, TFBlipVisionModel)
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
