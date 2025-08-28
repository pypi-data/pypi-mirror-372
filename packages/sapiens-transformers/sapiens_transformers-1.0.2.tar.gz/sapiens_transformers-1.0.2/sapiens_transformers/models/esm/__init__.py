"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_torch_available
_import_structure = {'configuration_esm': ['EsmConfig'], 'tokenization_esm': ['EsmTokenizer']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_esm"] = ["EsmForMaskedLM", "EsmForSequenceClassification", "EsmForTokenClassification", "EsmModel", "EsmPreTrainedModel"]
    _import_structure["modeling_esmfold"] = ["EsmForProteinFolding", "EsmFoldPreTrainedModel"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_esm"] = ["TFEsmForMaskedLM", "TFEsmForSequenceClassification", "TFEsmForTokenClassification", "TFEsmModel", "TFEsmPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_esm import EsmConfig
    from .tokenization_esm import EsmTokenizer
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_esm import (EsmForMaskedLM, EsmForSequenceClassification, EsmForTokenClassification, EsmModel, EsmPreTrainedModel)
        from .modeling_esmfold import EsmFoldPreTrainedModel, EsmForProteinFolding
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_esm import (TFEsmForMaskedLM, TFEsmForSequenceClassification, TFEsmForTokenClassification, TFEsmModel, TFEsmPreTrainedModel)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
