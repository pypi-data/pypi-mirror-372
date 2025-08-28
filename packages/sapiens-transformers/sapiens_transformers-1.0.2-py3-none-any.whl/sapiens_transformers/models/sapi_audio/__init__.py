"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_flax,
sapiens_technology_tf, sapiens_technology_tokenizers, sapiens_technology_torch)
_import_structure = {'configuration_sapi_audio': ['SAPIAudioConfig', 'SAPIAudioOnnxConfig'], 'feature_extraction_sapi_audio': ['SAPIAudioFeatureExtractor'],
'processing_sapi_audio': ['SAPIAudioProcessor'], 'tokenization_sapi_audio': ['SAPIAudioTokenizer']}
list_of_sapi_attributes1 = ["SAPIAudioTokenizerFast"]
list_of_sapi_attributes2 = ["SAPIAudioForCausalLM", "SAPIAudioForConditionalGeneration", "SAPIAudioModel", "SAPIAudioPreTrainedModel", "SAPIAudioForAudioClassification"]
list_of_sapi_attributes3 = ["TFSAPIAudioForConditionalGeneration", "TFSAPIAudioModel", "TFSAPIAudioPreTrainedModel"]
list_of_sapi_attributes4 = ["FlaxSAPIAudioForConditionalGeneration", "FlaxSAPIAudioModel", "FlaxSAPIAudioPreTrainedModel", "FlaxSAPIAudioForAudioClassification"]
try:
    if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_sapi_audio_fast"] = list_of_sapi_attributes1
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_sapi_audio"] = list_of_sapi_attributes2
try:
    if not sapiens_technology_tf(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_tf_sapi_audio"] = list_of_sapi_attributes3
try:
    if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_flax_sapi_audio"] = list_of_sapi_attributes4
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapi_audio import SAPIAudioConfig, SAPIAudioOnnxConfig
    from .feature_extraction_sapi_audio import SAPIAudioFeatureExtractor
    from .processing_sapi_audio import SAPIAudioProcessor
    from .tokenization_sapi_audio import SAPIAudioTokenizer
    try:
        if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_sapi_audio_fast import SAPIAudioTokenizerFast
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapi_audio import (SAPIAudioForAudioClassification, SAPIAudioForCausalLM, SAPIAudioForConditionalGeneration, SAPIAudioModel, SAPIAudioPreTrainedModel)
    try:
        if not sapiens_technology_tf(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_tf_sapi_audio import (TFSAPIAudioForConditionalGeneration, TFSAPIAudioModel, TFSAPIAudioPreTrainedModel)
    try:
        if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_flax_sapi_audio import (FlaxSAPIAudioForAudioClassification, FlaxSAPIAudioForConditionalGeneration, FlaxSAPIAudioModel, FlaxSAPIAudioPreTrainedModel)
else:
    import sys
    name, module_file, import_structure, module_spec = __name__, globals()["__file__"], _import_structure, __spec__
    sys.modules[__name__] = SapiensTechnologyModule(name, module_file, import_structure, module_spec)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
