"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import (SAPIENS_TECHNOLOGY_CHECKING, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_flax,
sapiens_technology_is_available, sapiens_technology_tokenizers, sapiens_technology_torch)
_import_structure = {'configuration_sapama': ['SapamaConfig']}
try:
    if not sapiens_technology_is_available(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_sapama"] = ["SapamaTokenizer"]
try:
    if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["tokenization_sapama_fast"] = ["SapamaTokenizerFast"]
try:
    if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_sapama"] = ["SapamaForCausalLM", "SapamaModel", "SapamaPreTrainedModel", "SapamaForSequenceClassification", "SapamaForQuestionAnswering", "SapamaForTokenClassification"]
try:
    if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable: pass
else: _import_structure["modeling_flax_sapama"] = ["FlaxSapamaForCausalLM", "FlaxSapamaModel", "FlaxSapamaPreTrainedModel"]
if SAPIENS_TECHNOLOGY_CHECKING:
    from .configuration_sapama import SapamaConfig
    try:
        if not sapiens_technology_is_available(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_sapama import SapamaTokenizer
    try:
        if not sapiens_technology_tokenizers(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .tokenization_sapama_fast import SapamaTokenizerFast
    try:
        if not sapiens_technology_torch(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_sapama import (SapamaForCausalLM, SapamaForQuestionAnswering, SapamaForSequenceClassification, SapamaForTokenClassification, SapamaModel, SapamaPreTrainedModel)
    try:
        if not sapiens_technology_flax(): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: pass
    else: from .modeling_flax_sapama import FlaxSapamaForCausalLM, FlaxSapamaModel, FlaxSapamaPreTrainedModel
else:
    import sys
    sys.modules[__name__] = SapiensTechnologyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
