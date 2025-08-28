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
class MobileViTV2Config(PretrainedConfig):
    model_type = "mobilevitv2"
    def __init__(self, num_channels=3, image_size=256, patch_size=2, expand_ratio=2.0, hidden_act="swish", conv_kernel_size=3, output_stride=32, classifier_dropout_prob=0.1,
    initializer_range=0.02, layer_norm_eps=1e-5, aspp_out_channels=512, atrous_rates=[6, 12, 18], aspp_dropout_prob=0.1, semantic_loss_ignore_index=255, n_attn_blocks=[2, 4, 3],
    base_attn_unit_dims=[128, 192, 256], width_multiplier=1.0, ffn_multiplier=2, attn_dropout=0.0, ffn_dropout=0.0, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.image_size = image_size
        self.patch_size = patch_size
        self.expand_ratio = expand_ratio
        self.hidden_act = hidden_act
        self.conv_kernel_size = conv_kernel_size
        self.output_stride = output_stride
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.n_attn_blocks = n_attn_blocks
        self.base_attn_unit_dims = base_attn_unit_dims
        self.width_multiplier = width_multiplier
        self.ffn_multiplier = ffn_multiplier
        self.ffn_dropout = ffn_dropout
        self.attn_dropout = attn_dropout
        self.classifier_dropout_prob = classifier_dropout_prob
        self.aspp_out_channels = aspp_out_channels
        self.atrous_rates = atrous_rates
        self.aspp_dropout_prob = aspp_dropout_prob
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
class MobileViTV2OnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def outputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "image-classification": return OrderedDict([("logits", {0: "batch"})])
        else: return OrderedDict([("last_hidden_state", {0: "batch"}), ("pooler_output", {0: "batch"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
