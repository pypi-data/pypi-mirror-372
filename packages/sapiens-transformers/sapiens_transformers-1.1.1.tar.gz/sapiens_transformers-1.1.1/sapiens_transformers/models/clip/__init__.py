"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_tokenizers_available, is_torch_available, is_vision_available)
_import_structure = {'configuration_clip': ['CLIPConfig', 'CLIPOnnxConfig', 'CLIPTextConfig', 'CLIPVisionConfig'], 'processing_clip': ['CLIPProcessor'], 'tokenization_clip': ['CLIPTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_clip_fast"] = ["CLIPTokenizerFast"]
try:
    if not is_vision_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["feature_extraction_clip"] = ["CLIPFeatureExtractor"]
    _import_structure["image_processing_clip"] = ["CLIPImageProcessor"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_clip"] = ["CLIPModel", "CLIPPreTrainedModel", "CLIPTextModel", "CLIPTextModelWithProjection", "CLIPVisionModel", "CLIPVisionModelWithProjection", "CLIPForImageClassification"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_clip"] = ["TFCLIPModel", "TFCLIPPreTrainedModel", "TFCLIPTextModel", "TFCLIPVisionModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_clip"] = ["FlaxCLIPModel", "FlaxCLIPPreTrainedModel", "FlaxCLIPTextModel", "FlaxCLIPTextPreTrainedModel", "FlaxCLIPTextModelWithProjection", "FlaxCLIPVisionModel", "FlaxCLIPVisionPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_clip import (CLIPConfig, CLIPOnnxConfig, CLIPTextConfig, CLIPVisionConfig)
    from .processing_clip import CLIPProcessor
    from .tokenization_clip import CLIPTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_clip_fast import CLIPTokenizerFast
    try:
        if not is_vision_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_clip import CLIPFeatureExtractor
        from .image_processing_clip import CLIPImageProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_clip import (CLIPForImageClassification, CLIPModel, CLIPPreTrainedModel, CLIPTextModel, CLIPTextModelWithProjection, CLIPVisionModel, CLIPVisionModelWithProjection)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_clip import (TFCLIPModel, TFCLIPPreTrainedModel, TFCLIPTextModel, TFCLIPVisionModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_clip import (FlaxCLIPModel, FlaxCLIPPreTrainedModel, FlaxCLIPTextModel, FlaxCLIPTextModelWithProjection, FlaxCLIPTextPreTrainedModel, FlaxCLIPVisionModel, FlaxCLIPVisionPreTrainedModel)
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
