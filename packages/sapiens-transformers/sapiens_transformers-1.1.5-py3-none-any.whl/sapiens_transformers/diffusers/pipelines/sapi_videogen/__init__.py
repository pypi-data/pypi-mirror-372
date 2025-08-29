'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import SAPIENS_TECHNOLOGY_CHECKING, SAPIENS_TECHNOLOGY_IMPORT, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_module, sapiens_technology_torch, sapiens_technology_transformers
_import_structure, _dummy_objects = {'pipeline_output': ['SAPIVideoGenPipelineOutput']}, {}
try:
    if not (sapiens_technology_transformers() and sapiens_technology_torch()): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable:
    from ...utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(sapiens_technology_module(dummy_torch_and_transformers_objects))
else:
    _import_structure['pipeline_sapi_videogen'] = ['SAPIVideoGenPipeline']
    _import_structure['pipeline_sapi_videogen_controlnet'] = ['SAPIVideoGenControlNetPipeline']
    _import_structure['pipeline_sapi_videogen_sdxl'] = ['SAPIVideoGenSDXLPipeline']
    _import_structure['pipeline_sapi_videogen_sparsectrl'] = ['SAPIVideoGenSparseControlNetPipeline']
    _import_structure['pipeline_sapi_videogen_video2video'] = ['SAPIVideoGenVideoToVideoPipeline']
    _import_structure['pipeline_sapi_videogen_video2video_controlnet'] = ['SAPIVideoGenVideoToVideoControlNetPipeline']
if SAPIENS_TECHNOLOGY_CHECKING or SAPIENS_TECHNOLOGY_IMPORT:
    try:
        if not (sapiens_technology_transformers() and sapiens_technology_torch()): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import *
    else:
        from .pipeline_sapi_videogen import SAPIVideoGenPipeline
        from .pipeline_sapi_videogen_controlnet import SAPIVideoGenControlNetPipeline
        from .pipeline_sapi_videogen_sdxl import SAPIVideoGenSDXLPipeline
        from .pipeline_sapi_videogen_sparsectrl import SAPIVideoGenSparseControlNetPipeline
        from .pipeline_sapi_videogen_video2video import SAPIVideoGenVideoToVideoPipeline
        from .pipeline_sapi_videogen_video2video_controlnet import SAPIVideoGenVideoToVideoControlNetPipeline
        from .pipeline_output import SAPIVideoGenPipelineOutput
else:
    import sys
    sys.modules[__name__] = SapiensTechnologyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
