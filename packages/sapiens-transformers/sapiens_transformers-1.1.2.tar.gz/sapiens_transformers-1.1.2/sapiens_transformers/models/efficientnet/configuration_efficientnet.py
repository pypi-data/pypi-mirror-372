"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import List, Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class EfficientNetConfig(PretrainedConfig):
    model_type = "efficientnet"
    def __init__(self, num_channels: int = 3, image_size: int = 600, width_coefficient: float = 2.0, depth_coefficient: float = 3.1, depth_divisor: int = 8, kernel_sizes: List[int] = [3, 3, 5, 3, 5, 5, 3],
    in_channels: List[int] = [32, 16, 24, 40, 80, 112, 192], out_channels: List[int] = [16, 24, 40, 80, 112, 192, 320], depthwise_padding: List[int] = [], strides: List[int] = [1, 2, 2, 2, 1, 2, 1],
    num_block_repeats: List[int] = [1, 2, 2, 3, 3, 4, 1], expand_ratios: List[int] = [1, 6, 6, 6, 6, 6, 6], squeeze_expansion_ratio: float = 0.25, hidden_act: str = "swish", hidden_dim: int = 2560,
    pooling_type: str = "mean", initializer_range: float = 0.02, batch_norm_eps: float = 0.001, batch_norm_momentum: float = 0.99, dropout_rate: float = 0.5, drop_connect_rate: float = 0.2, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.image_size = image_size
        self.width_coefficient = width_coefficient
        self.depth_coefficient = depth_coefficient
        self.depth_divisor = depth_divisor
        self.kernel_sizes = kernel_sizes
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.depthwise_padding = depthwise_padding
        self.strides = strides
        self.num_block_repeats = num_block_repeats
        self.expand_ratios = expand_ratios
        self.squeeze_expansion_ratio = squeeze_expansion_ratio
        self.hidden_act = hidden_act
        self.hidden_dim = hidden_dim
        self.pooling_type = pooling_type
        self.initializer_range = initializer_range
        self.batch_norm_eps = batch_norm_eps
        self.batch_norm_momentum = batch_norm_momentum
        self.dropout_rate = dropout_rate
        self.drop_connect_rate = drop_connect_rate
        self.num_hidden_layers = sum(num_block_repeats) * 4
class EfficientNetOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def atol_for_validation(self) -> float: return 1e-5
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
