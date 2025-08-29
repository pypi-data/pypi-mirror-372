"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tf_available, is_torch_available)
_import_structure = {"configuration_resnet": ["ResNetConfig", "ResNetOnnxConfig"]}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_resnet"] = ["ResNetForImageClassification", "ResNetModel", "ResNetPreTrainedModel", "ResNetBackbone"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_resnet"] = ["TFResNetForImageClassification", "TFResNetModel", "TFResNetPreTrainedModel"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_resnet"] = ["FlaxResNetForImageClassification", "FlaxResNetModel", "FlaxResNetPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_resnet import ResNetConfig, ResNetOnnxConfig
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_resnet import (ResNetBackbone, ResNetForImageClassification, ResNetModel, ResNetPreTrainedModel)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_resnet import (TFResNetForImageClassification, TFResNetModel, TFResNetPreTrainedModel)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_resnet import FlaxResNetForImageClassification, FlaxResNetModel, FlaxResNetPreTrainedModel
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
