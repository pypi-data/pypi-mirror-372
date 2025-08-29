'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.controlnets.multicontrolnet import MultiControlNetModel
from ...utils import deprecate
class MultiControlNetModel(MultiControlNetModel):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `MultiControlNetModel` from `diffusers.pipelines.controlnet.multicontrolnet` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.multicontrolnet import MultiControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.pipelines.controlnet.multicontrolnet.MultiControlNetModel', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
