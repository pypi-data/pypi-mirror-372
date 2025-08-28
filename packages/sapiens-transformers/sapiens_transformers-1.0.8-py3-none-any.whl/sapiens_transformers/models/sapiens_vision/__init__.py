"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_torch, sapiens_technology_for_vision)
_import_structure = {'configuration_sapiens_vision': ['SapiensVisionConfig'], 'processing_sapiens_vision': ['SapiensVisionProcessor']}
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else:
    list_of_sapiens_attributes = ["SapiensVisionForConditionalGeneration", "SapiensVisionModel", "SapiensVisionPreTrainedModel"]
    _import_structure["modeling_sapiens_vision"] = list_of_sapiens_attributes
try:
    if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["image_processing_sapiens_vision"] = ["SapiensVisionImageProcessor"]
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapiens_vision import SapiensVisionConfig
    from .processing_sapiens_vision import SapiensVisionProcessor
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapiens_vision import (SapiensVisionForConditionalGeneration, SapiensVisionModel, SapiensVisionPreTrainedModel)
    try:
        if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .image_processing_sapiens_vision import SapiensVisionImageProcessor
else:
    import sys
    name, module_file, import_structure = __name__, globals()["__file__"], _import_structure
    sys.modules[__name__] = SapiensTechnologyModule(name, module_file, import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
