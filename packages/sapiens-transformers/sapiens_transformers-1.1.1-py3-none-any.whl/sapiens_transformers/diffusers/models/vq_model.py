'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .autoencoders.vq_model import VQEncoderOutput, VQModel
from ..utils import deprecate
class VQEncoderOutput(VQEncoderOutput):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `VQEncoderOutput` from `diffusers.models.vq_model` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.autoencoders.vq_model import VQEncoderOutput`, instead.'
        deprecate('VQEncoderOutput', '0.31', deprecation_message)
        super().__init__(*args, **kwargs)
class VQModel(VQModel):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `VQModel` from `diffusers.models.vq_model` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.autoencoders.vq_model import VQModel`, instead.'
        deprecate('VQModel', '0.31', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
