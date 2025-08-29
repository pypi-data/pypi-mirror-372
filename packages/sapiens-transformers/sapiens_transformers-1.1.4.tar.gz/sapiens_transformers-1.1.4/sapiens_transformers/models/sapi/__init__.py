"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_torch)
_import_structure = {'configuration_sapi': ['SAPIConfig']}
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else:
    list_of_sapi_attributes = ["SAPIForQuestionAnswering", "SAPIForCausalLM", "SAPIModel", "SAPIPreTrainedModel", "SAPIForSequenceClassification", "SAPIForTokenClassification"]
    _import_structure["modeling_sapi"] = list_of_sapi_attributes
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapi import SAPIConfig
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapi import (SAPIForCausalLM, SAPIForQuestionAnswering, SAPIForSequenceClassification, SAPIForTokenClassification, SAPIModel, SAPIPreTrainedModel)
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
