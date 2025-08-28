'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import SAPIENS_TECHNOLOGY_CHECKING, SAPIENS_TECHNOLOGY_IMPORT, SapiensTechnologyNotAvailable, SapiensTechnologyModule, sapiens_technology_module, sapiens_technology_torch, sapiens_technology_transformers
_dummy_objects, _additional_imports, _import_structure = {}, {}, {'pipeline_output': ['SAPIPhotoGenPipelineOutput', 'SAPIPhotoGenPriorReduxPipelineOutput']}
try:
    if not (sapiens_technology_transformers() and sapiens_technology_torch()): raise SapiensTechnologyNotAvailable()
except SapiensTechnologyNotAvailable:
    from ...utils import dummy_torch_and_transformers_objects
    _dummy_objects.update(sapiens_technology_module(dummy_torch_and_transformers_objects))
else:
    _import_structure['modeling_sapi_photogen'] = ['ReduxImageEncoder']
    _import_structure['pipeline_sapi_photogen'] = ['SAPIPhotoGenPipeline']
    _import_structure['pipeline_sapi_photogen_control'] = ['SAPIPhotoGenControlPipeline']
    _import_structure['pipeline_sapi_photogen_control_img2img'] = ['SAPIPhotoGenControlImg2ImgPipeline']
    _import_structure['pipeline_sapi_photogen_control_inpaint'] = ['SAPIPhotoGenControlInpaintPipeline']
    _import_structure['pipeline_sapi_photogen_controlnet'] = ['SAPIPhotoGenControlNetPipeline']
    _import_structure['pipeline_sapi_photogen_controlnet_image_to_image'] = ['SAPIPhotoGenControlNetImg2ImgPipeline']
    _import_structure['pipeline_sapi_photogen_controlnet_inpainting'] = ['SAPIPhotoGenControlNetInpaintPipeline']
    _import_structure['pipeline_sapi_photogen_fill'] = ['SAPIPhotoGenFillPipeline']
    _import_structure['pipeline_sapi_photogen_img2img'] = ['SAPIPhotoGenImg2ImgPipeline']
    _import_structure['pipeline_sapi_photogen_inpaint'] = ['SAPIPhotoGenInpaintPipeline']
    _import_structure['pipeline_sapi_photogen_prior_redux'] = ['SAPIPhotoGenPriorReduxPipeline']
if SAPIENS_TECHNOLOGY_CHECKING or SAPIENS_TECHNOLOGY_IMPORT:
    try:
        if not (sapiens_technology_transformers() and sapiens_technology_torch()): raise SapiensTechnologyNotAvailable()
    except SapiensTechnologyNotAvailable: from ...utils.dummy_torch_and_transformers_objects import *
    else:
        from .modeling_sapi_photogen import ReduxImageEncoder
        from .pipeline_sapi_photogen import SAPIPhotoGenPipeline
        from .pipeline_sapi_photogen_control import SAPIPhotoGenControlPipeline
        from .pipeline_sapi_photogen_control_img2img import SAPIPhotoGenControlImg2ImgPipeline
        from .pipeline_sapi_photogen_control_inpaint import SAPIPhotoGenControlInpaintPipeline
        from .pipeline_sapi_photogen_controlnet import SAPIPhotoGenControlNetPipeline
        from .pipeline_sapi_photogen_controlnet_image_to_image import SAPIPhotoGenControlNetImg2ImgPipeline
        from .pipeline_sapi_photogen_controlnet_inpainting import SAPIPhotoGenControlNetInpaintPipeline
        from .pipeline_sapi_photogen_fill import SAPIPhotoGenFillPipeline
        from .pipeline_sapi_photogen_img2img import SAPIPhotoGenImg2ImgPipeline
        from .pipeline_sapi_photogen_inpaint import SAPIPhotoGenInpaintPipeline
        from .pipeline_sapi_photogen_prior_redux import SAPIPhotoGenPriorReduxPipeline
else:
    import sys
    sys.modules[__name__] = SapiensTechnologyModule(__name__, globals()['__file__'], _import_structure, module_spec=__spec__)
    for name, value in _dummy_objects.items(): setattr(sys.modules[__name__], name, value)
    for name, value in _additional_imports.items(): setattr(sys.modules[__name__], name, value)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
