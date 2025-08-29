"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ....utils import OptionalDependencyNotAvailable, _LazyModule, is_tokenizers_available, is_torch_available
_import_structure = {'configuration_realm': ['RealmConfig'], 'tokenization_realm': ['RealmTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_realm_fast"] = ["RealmTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_realm"] = ["RealmEmbedder", "RealmForOpenQA", "RealmKnowledgeAugEncoder", "RealmPreTrainedModel", "RealmReader", "RealmScorer", "load_tf_weights_in_realm"]
    _import_structure["retrieval_realm"] = ["RealmRetriever"]
if TYPE_CHECKING:
    from .configuration_realm import RealmConfig
    from .tokenization_realm import RealmTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_realm import RealmTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_realm import (RealmEmbedder, RealmForOpenQA, RealmKnowledgeAugEncoder, RealmPreTrainedModel, RealmReader, RealmScorer, load_tf_weights_in_realm)
        from .retrieval_realm import RealmRetriever
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
