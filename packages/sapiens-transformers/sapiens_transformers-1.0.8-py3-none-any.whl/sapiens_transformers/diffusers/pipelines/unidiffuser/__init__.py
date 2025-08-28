'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import TYPE_CHECKING
from ...utils import DIFFUSERS_SLOW_IMPORT, OptionalDependencyNotAvailable, _LazyModule, is_torch_available, is_transformers_available
_dummy_objects = {}
_import_structure = {}
try:
    if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable:
    from ...utils.dummy_torch_and_transformers_objects import ImageTextPipelineOutput, UniDiffuserPipeline
    _dummy_objects.update({'ImageTextPipelineOutput': ImageTextPipelineOutput, 'UniDiffuserPipeline': UniDiffuserPipeline})
else:
    _import_structure['modeling_text_decoder'] = ['UniDiffuserTextDecoder']
    _import_structure['modeling_uvit'] = ['UniDiffuserModel', 'UTransformer2DModel']
    _import_structure['pipeline_unidiffuser'] = ['ImageTextPipelineOutput', 'UniDiffuserPipeline']
if TYPE_CHECKING or DIFFUSERS_SLOW_IMPORT:
    try:
        if not (is_transformers_available() and is_torch_available()): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import ImageTextPipelineOutput, UniDiffuserPipeline
    else:
        from .modeling_text_decoder import UniDiffuserTextDecoder
        from .modeling_uvit import UniDiffuserModel, UTransformer2DModel
        from .pipeline_unidiffuser import ImageTextPipelineOutput, UniDiffuserPipeline
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
