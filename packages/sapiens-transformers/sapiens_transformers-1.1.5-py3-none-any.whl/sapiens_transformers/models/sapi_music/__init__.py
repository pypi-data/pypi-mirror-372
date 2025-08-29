"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_torch)
_import_structure = {'configuration_sapi_music': ['SAPIMusicConfig'], 'feature_extraction_sapi_music': ['SAPIMusicFeatureExtractor']}
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_sapi_music"] = ["SAPIMusicModel", "SAPIMusicPreTrainedModel"]
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapi_music import (SAPIMusicConfig)
    from .feature_extraction_sapi_music import SAPIMusicFeatureExtractor
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapi_music import (SAPIMusicModel, SAPIMusicPreTrainedModel)
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
