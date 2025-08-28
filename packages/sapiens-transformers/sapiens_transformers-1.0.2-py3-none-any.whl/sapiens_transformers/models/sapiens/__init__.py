"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_tokenizers, sapiens_technology_torch)
_import_structure = {'configuration_sapiens': ['SapiensConfig'], 'tokenization_sapiens': ['SapiensTokenizer']}
try:
    if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_sapiens_fast"] = ["SapiensTokenizerFast"]
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else:
    list_of_sapiens_attributes = ["SapiensForCausalLM", "SapiensModel", "SapiensPreTrainedModel", "SapiensForSequenceClassification", "SapiensForTokenClassification"]
    _import_structure["modeling_sapiens"] = list_of_sapiens_attributes
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapiens import SapiensConfig
    from .tokenization_sapiens import SapiensTokenizer
    try:
        if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_sapiens_fast import SapiensTokenizerFast
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapiens import (SapiensForCausalLM, SapiensForSequenceClassification, SapiensForTokenClassification, SapiensModel, SapiensPreTrainedModel)
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
