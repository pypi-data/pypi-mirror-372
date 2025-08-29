'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import is_flax_available, is_torch_available
if is_torch_available():
    from .unet_spatio_temporal_condition import UNetSpatioTemporalConditionModel
    from .unet_motion_model import MotionAdapter, UNetMotionModel
    from .unet_2d_condition import UNet2DConditionModel
    from .unet_3d_condition import UNet3DConditionModel
    from .unet_stable_cascade import StableCascadeUNet
    from .unet_kandinsky3 import Kandinsky3UNet
    from .unet_i2vgen_xl import I2VGenXLUNet
    from .unet_1d import UNet1DModel
    from .unet_2d import UNet2DModel
    from .uvit_2d import UVit2DModel
if is_flax_available(): from .unet_2d_condition_flax import FlaxUNet2DConditionModel
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
