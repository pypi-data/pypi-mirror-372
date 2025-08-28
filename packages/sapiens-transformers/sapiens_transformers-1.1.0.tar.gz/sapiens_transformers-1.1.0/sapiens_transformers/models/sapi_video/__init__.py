"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_torch, sapiens_technology_for_vision)
_import_structure = {'configuration_sapi_video': ['SAPIVideoConfig'], 'processing_sapi_video': ['SAPIVideoProcessor']}
try:
    if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["image_processing_sapi_video"] = ["SAPIVideoImageProcessor"]
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_sapi_video"] = ["SAPIVideoForConditionalGeneration", "SAPIVideoPreTrainedModel"]
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapi_video import SAPIVideoConfig
    from .processing_sapi_video import SAPIVideoProcessor
    try:
        if not sapiens_technology_for_vision(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .image_processing_sapi_video import SAPIVideoImageProcessor
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapi_video import (SAPIVideoForConditionalGeneration, SAPIVideoPreTrainedModel)
else:
    import sys
    sys.modules[__name__] = SapiensTechnologyModule(__name__, globals()["__file__"], _import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
