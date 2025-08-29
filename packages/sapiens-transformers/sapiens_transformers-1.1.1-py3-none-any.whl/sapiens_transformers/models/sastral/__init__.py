"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_flax, sapiens_technology_tf, sapiens_technology_torch)
_import_structure = {'configuration_sastral': ['SastralConfig']}
list_of_sapiens_attributes1 = ["SastralForCausalLM", "SastralModel", "SastralPreTrainedModel", "SastralForSequenceClassification", "SastralForTokenClassification"]
list_of_sapiens_attributes2 = ["FlaxSastralForCausalLM", "FlaxSastralModel", "FlaxSastralPreTrainedModel"]
list_of_sapiens_attributes3 = ["TFSastralModel", "TFSastralForCausalLM", "TFSastralForSequenceClassification", "TFSastralPreTrainedModel"]
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_sastral"] = list_of_sapiens_attributes1
try:
    if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_flax_sastral"] = list_of_sapiens_attributes2
try:
    if not sapiens_technology_tf(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_tf_sastral"] = list_of_sapiens_attributes3
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sastral import SastralConfig
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sastral import (SastralForCausalLM, SastralForSequenceClassification, SastralForTokenClassification, SastralModel, SastralPreTrainedModel)
    try:
        if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_flax_sastral import (FlaxSastralForCausalLM, FlaxSastralModel, FlaxSastralPreTrainedModel)
    try:
        if not sapiens_technology_tf(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_tf_sastral import (TFSastralForCausalLM, TFSastralForSequenceClassification, TFSastralModel, TFSastralPreTrainedModel)
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
