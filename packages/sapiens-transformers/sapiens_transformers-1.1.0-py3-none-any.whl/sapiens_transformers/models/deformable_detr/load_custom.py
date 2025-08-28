"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from pathlib import Path
def load_cuda_kernels():
    from torch.utils.cpp_extension import load
    root = Path(__file__).resolve().parent.parent.parent / "kernels" / "deformable_detr"
    src_files = [root / filename for filename in ["vision.cpp", os.path.join("cpu", "ms_deform_attn_cpu.cpp"), os.path.join("cuda", "ms_deform_attn_cuda.cu")]]
    load("MultiScaleDeformableAttention", src_files, with_cuda=True, extra_include_paths=[str(root)], extra_cflags=["-DWITH_CUDA=1"],
    extra_cuda_cflags=["-DCUDA_HAS_FP16=1", "-D__CUDA_NO_HALF_OPERATORS__", "-D__CUDA_NO_HALF_CONVERSIONS__", "-D__CUDA_NO_HALF2_OPERATORS__"])
    import MultiScaleDeformableAttention as MSDA
    return MSDA
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
