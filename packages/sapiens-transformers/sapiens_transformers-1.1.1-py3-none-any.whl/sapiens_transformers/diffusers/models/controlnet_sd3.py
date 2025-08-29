'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .controlnets.controlnet_sd3 import SD3ControlNetModel, SD3ControlNetOutput, SD3MultiControlNetModel
from ..utils import deprecate
class SD3ControlNetOutput(SD3ControlNetOutput):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `SD3ControlNetOutput` from `diffusers.models.controlnet_sd3` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sd3 import SD3ControlNetOutput`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sd3.SD3ControlNetOutput', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
class SD3ControlNetModel(SD3ControlNetModel):
    def __init__(self, sample_size: int=128, patch_size: int=2, in_channels: int=16, num_layers: int=18, attention_head_dim: int=64, num_attention_heads: int=18, joint_attention_dim: int=4096,
    caption_projection_dim: int=1152, pooled_projection_dim: int=2048, out_channels: int=16, pos_embed_max_size: int=96, extra_conditioning_channels: int=0):
        deprecation_message = 'Importing `SD3ControlNetModel` from `diffusers.models.controlnet_sd3` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sd3 import SD3ControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sd3.SD3ControlNetModel', '0.34', deprecation_message)
        super().__init__(sample_size=sample_size, patch_size=patch_size, in_channels=in_channels, num_layers=num_layers, attention_head_dim=attention_head_dim, num_attention_heads=num_attention_heads,
        joint_attention_dim=joint_attention_dim, caption_projection_dim=caption_projection_dim, pooled_projection_dim=pooled_projection_dim, out_channels=out_channels,
        pos_embed_max_size=pos_embed_max_size, extra_conditioning_channels=extra_conditioning_channels)
class SD3MultiControlNetModel(SD3MultiControlNetModel):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `SD3MultiControlNetModel` from `diffusers.models.controlnet_sd3` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sd3 import SD3MultiControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sd3.SD3MultiControlNetModel', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
