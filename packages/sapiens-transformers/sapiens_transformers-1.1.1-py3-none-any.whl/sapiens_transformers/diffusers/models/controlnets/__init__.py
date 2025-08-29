'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import is_flax_available, is_torch_available
if is_torch_available():
    from .controlnet_sapi_photogen import SAPIPhotoGenControlNetModel, SAPIPhotoGenControlNetOutput, SAPIPhotoGenMultiControlNetModel
    from .controlnet_sparsectrl import SparseControlNetConditioningEmbedding, SparseControlNetModel, SparseControlNetOutput
    from .controlnet_hunyuan import HunyuanControlNetOutput, HunyuanDiT2DControlNetModel, HunyuanDiT2DMultiControlNetModel
    from .controlnet_sapi_imagegen import SAPIControlNetModel, SAPIControlNetOutput, SAPIMultiControlNetModel
    from .controlnet_flux import FluxControlNetModel, FluxControlNetOutput, FluxMultiControlNetModel
    from .controlnet_sd3 import SD3ControlNetModel, SD3ControlNetOutput, SD3MultiControlNetModel
    from .controlnet_xs import ControlNetXSAdapter, ControlNetXSOutput, UNetControlNetXSModel
    from .controlnet import ControlNetModel, ControlNetOutput
    from .controlnet_union import ControlNetUnionModel
    from .multicontrolnet import MultiControlNetModel
if is_flax_available(): from .controlnet_flax import FlaxControlNetModel
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
