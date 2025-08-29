"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_flax,
sapiens_technology_is_available, sapiens_technology_tokenizers, sapiens_technology_torch)
_import_structure = {'configuration_entity': ['EntityConfig']}
try:
    if not sapiens_technology_is_available(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_entity"] = ["EntityTokenizer"]
try:
    if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_entity_fast"] = ["EntityTokenizerFast"]
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else:
    list_of_entity_attributes1 = ["EntityForCausalLM", "EntityModel", "EntityPreTrainedModel", "EntityForSequenceClassification", "EntityForQuestionAnswering", "EntityForTokenClassification"]
    _import_structure["modeling_entity"] = list_of_entity_attributes1
try:
    if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else:
    list_of_entity_attributes2 = ["FlaxEntityForCausalLM", "FlaxEntityModel", "FlaxEntityPreTrainedModel"]
    _import_structure["modeling_flax_entity"] = list_of_entity_attributes2
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_entity import EntityConfig
    try:
        if not sapiens_technology_is_available(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_entity import EntityTokenizer
    try:
        if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_entity_fast import EntityTokenizerFast
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_entity import (EntityForCausalLM, EntityForQuestionAnswering, EntityForSequenceClassification, EntityForTokenClassification, EntityModel, EntityPreTrainedModel)
    try:
        if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_flax_entity import FlaxEntityForCausalLM, FlaxEntityModel, FlaxEntityPreTrainedModel
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
