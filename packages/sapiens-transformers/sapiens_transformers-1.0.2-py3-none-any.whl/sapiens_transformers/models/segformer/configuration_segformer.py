"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from collections import OrderedDict
from typing import Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class SegformerConfig(PretrainedConfig):
    model_type = "segformer"
    def __init__(self, num_channels=3, num_encoder_blocks=4, depths=[2, 2, 2, 2], sr_ratios=[8, 4, 2, 1], hidden_sizes=[32, 64, 160, 256], patch_sizes=[7, 3, 3, 3],
    strides=[4, 2, 2, 2], num_attention_heads=[1, 2, 5, 8], mlp_ratios=[4, 4, 4, 4], hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0,
    classifier_dropout_prob=0.1, initializer_range=0.02, drop_path_rate=0.1, layer_norm_eps=1e-6, decoder_hidden_size=256, semantic_loss_ignore_index=255, **kwargs):
        super().__init__(**kwargs)
        if "reshape_last_stage" in kwargs and kwargs["reshape_last_stage"] is False: warnings.warn("Reshape_last_stage is set to False in this config. This argument is deprecated and will soon be removed, as the behaviour will default to that of reshape_last_stage = True.", FutureWarning)
        self.num_channels = num_channels
        self.num_encoder_blocks = num_encoder_blocks
        self.depths = depths
        self.sr_ratios = sr_ratios
        self.hidden_sizes = hidden_sizes
        self.patch_sizes = patch_sizes
        self.strides = strides
        self.mlp_ratios = mlp_ratios
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.classifier_dropout_prob = classifier_dropout_prob
        self.initializer_range = initializer_range
        self.drop_path_rate = drop_path_rate
        self.layer_norm_eps = layer_norm_eps
        self.decoder_hidden_size = decoder_hidden_size
        self.reshape_last_stage = kwargs.get("reshape_last_stage", True)
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
class SegformerOnnxConfig(OnnxConfig):
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
