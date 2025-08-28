"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import OptionalDependencyNotAvailable, _LazyModule, is_torch_available
_import_structure = {'configuration_clap': ['ClapAudioConfig', 'ClapConfig', 'ClapTextConfig'], 'processing_clap': ['ClapProcessor']}
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_clap"] = ["ClapModel", "ClapPreTrainedModel", "ClapTextModel", "ClapTextModelWithProjection", "ClapAudioModel", "ClapAudioModelWithProjection"]
    _import_structure["feature_extraction_clap"] = ["ClapFeatureExtractor"]
if TYPE_CHECKING:
    from .configuration_clap import (ClapAudioConfig, ClapConfig, ClapTextConfig)
    from .processing_clap import ClapProcessor
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .feature_extraction_clap import ClapFeatureExtractor
        from .modeling_clap import (ClapAudioModel, ClapAudioModelWithProjection, ClapModel, ClapPreTrainedModel, ClapTextModel, ClapTextModelWithProjection)
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
