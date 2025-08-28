'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .controlnets.controlnet_sapi_imagegen import SAPIControlNetModel, SAPIControlNetOutput, SAPIMultiControlNetModel
from ..utils import deprecate
class SAPIControlNetOutput(SAPIControlNetOutput):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `SAPIControlNetOutput` from `diffusers.models.controlnet_sapi_imagegen` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sapi_imagegen import SAPIControlNetOutput`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sapi_imagegen.SAPIControlNetOutput', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
class SAPIControlNetModel(SAPIControlNetModel):
    def __init__(self, sample_size: int=128, patch_size: int=2, in_channels: int=16, num_layers: int=18, attention_head_dim: int=64, num_attention_heads: int=18, joint_attention_dim: int=4096,
    caption_projection_dim: int=1152, pooled_projection_dim: int=2048, out_channels: int=16, pos_embed_max_size: int=96, extra_conditioning_channels: int=0):
        deprecation_message = 'Importing `SAPIControlNetModel` from `diffusers.models.controlnet_sapi_imagegen` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sapi_imagegen import SAPIControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sapi_imagegen.SAPIControlNetModel', '0.34', deprecation_message)
        super().__init__(sample_size=sample_size, patch_size=patch_size, in_channels=in_channels, num_layers=num_layers, attention_head_dim=attention_head_dim, num_attention_heads=num_attention_heads,
        joint_attention_dim=joint_attention_dim, caption_projection_dim=caption_projection_dim, pooled_projection_dim=pooled_projection_dim, out_channels=out_channels,
        pos_embed_max_size=pos_embed_max_size, extra_conditioning_channels=extra_conditioning_channels)
class SAPIMultiControlNetModel(SAPIMultiControlNetModel):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `SAPIMultiControlNetModel` from `diffusers.models.controlnet_sapi_imagegen` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_sapi_imagegen import SAPIMultiControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_sapi_imagegen.SAPIMultiControlNetModel', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
