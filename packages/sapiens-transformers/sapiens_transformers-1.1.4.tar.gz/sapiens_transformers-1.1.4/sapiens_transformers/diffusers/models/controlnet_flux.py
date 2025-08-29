'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .controlnets.controlnet_flux import FluxControlNetModel, FluxControlNetOutput, FluxMultiControlNetModel
from ..utils import deprecate
from typing import List
class FluxControlNetOutput(FluxControlNetOutput):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `FluxControlNetOutput` from `diffusers.models.controlnet_flux` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_flux import FluxControlNetOutput`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_flux.FluxControlNetOutput', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
class FluxControlNetModel(FluxControlNetModel):
    def __init__(self, patch_size: int=1, in_channels: int=64, num_layers: int=19, num_single_layers: int=38, attention_head_dim: int=128, num_attention_heads: int=24, joint_attention_dim: int=4096,
    pooled_projection_dim: int=768, guidance_embeds: bool=False, axes_dims_rope: List[int]=[16, 56, 56], num_mode: int=None, conditioning_embedding_channels: int=None):
        deprecation_message = 'Importing `FluxControlNetModel` from `diffusers.models.controlnet_flux` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_flux import FluxControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_flux.FluxControlNetModel', '0.34', deprecation_message)
        super().__init__(patch_size=patch_size, in_channels=in_channels, num_layers=num_layers, num_single_layers=num_single_layers, attention_head_dim=attention_head_dim,
        num_attention_heads=num_attention_heads, joint_attention_dim=joint_attention_dim, pooled_projection_dim=pooled_projection_dim, guidance_embeds=guidance_embeds, axes_dims_rope=axes_dims_rope,
        num_mode=num_mode, conditioning_embedding_channels=conditioning_embedding_channels)
class FluxMultiControlNetModel(FluxMultiControlNetModel):
    def __init__(self, *args, **kwargs):
        deprecation_message = 'Importing `FluxMultiControlNetModel` from `diffusers.models.controlnet_flux` is deprecated and this will be removed in a future version. Please use `from sapiens_transformers.diffusers.models.controlnets.controlnet_flux import FluxMultiControlNetModel`, instead.'
        deprecate('sapiens_transformers.diffusers.models.controlnet_flux.FluxMultiControlNetModel', '0.34', deprecation_message)
        super().__init__(*args, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
