"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Callable, List, Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class PvtConfig(PretrainedConfig):
    model_type = "pvt"
    def __init__(self, image_size: int = 224, num_channels: int = 3, num_encoder_blocks: int = 4, depths: List[int] = [2, 2, 2, 2], sequence_reduction_ratios: List[int] = [8, 4, 2, 1],
    hidden_sizes: List[int] = [64, 128, 320, 512], patch_sizes: List[int] = [4, 2, 2, 2], strides: List[int] = [4, 2, 2, 2], num_attention_heads: List[int] = [1, 2, 5, 8],
    mlp_ratios: List[int] = [8, 8, 4, 4], hidden_act: Mapping[str, Callable] = "gelu", hidden_dropout_prob: float = 0.0, attention_probs_dropout_prob: float = 0.0,
    initializer_range: float = 0.02, drop_path_rate: float = 0.0, layer_norm_eps: float = 1e-6, qkv_bias: bool = True, num_labels: int = 1000, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.num_channels = num_channels
        self.num_encoder_blocks = num_encoder_blocks
        self.depths = depths
        self.sequence_reduction_ratios = sequence_reduction_ratios
        self.hidden_sizes = hidden_sizes
        self.patch_sizes = patch_sizes
        self.strides = strides
        self.mlp_ratios = mlp_ratios
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.drop_path_rate = drop_path_rate
        self.layer_norm_eps = layer_norm_eps
        self.num_labels = num_labels
        self.qkv_bias = qkv_bias
class PvtOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
    @property
    def default_onnx_opset(self) -> int: return 12
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
