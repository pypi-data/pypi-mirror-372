"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class LevitConfig(PretrainedConfig):
    model_type = "levit"
    def __init__(self, image_size=224, num_channels=3, kernel_size=3, stride=2, padding=1, patch_size=16, hidden_sizes=[128, 256, 384], num_attention_heads=[4, 8, 12],
    depths=[4, 4, 4], key_dim=[16, 16, 16], drop_path_rate=0, mlp_ratio=[2, 2, 2], attention_ratio=[2, 2, 2], initializer_range=0.02, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.num_channels = num_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.hidden_sizes = hidden_sizes
        self.num_attention_heads = num_attention_heads
        self.depths = depths
        self.key_dim = key_dim
        self.drop_path_rate = drop_path_rate
        self.patch_size = patch_size
        self.attention_ratio = attention_ratio
        self.mlp_ratio = mlp_ratio
        self.initializer_range = initializer_range
        self.down_ops = [["Subsample", key_dim[0], hidden_sizes[0] // key_dim[0], 4, 2, 2], ["Subsample", key_dim[0], hidden_sizes[1] // key_dim[0], 4, 2, 2]]
class LevitOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
