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
class MobileViTConfig(PretrainedConfig):
    model_type = "mobilevit"
    def __init__(self, num_channels=3, image_size=256, patch_size=2, hidden_sizes=[144, 192, 240], neck_hidden_sizes=[16, 32, 64, 96, 128, 160, 640], num_attention_heads=4,
    mlp_ratio=2.0, expand_ratio=4.0, hidden_act="silu", conv_kernel_size=3, output_stride=32, hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.0, classifier_dropout_prob=0.1,
    initializer_range=0.02, layer_norm_eps=1e-5, qkv_bias=True, aspp_out_channels=256, atrous_rates=[6, 12, 18], aspp_dropout_prob=0.1, semantic_loss_ignore_index=255, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.image_size = image_size
        self.patch_size = patch_size
        self.hidden_sizes = hidden_sizes
        self.neck_hidden_sizes = neck_hidden_sizes
        self.num_attention_heads = num_attention_heads
        self.mlp_ratio = mlp_ratio
        self.expand_ratio = expand_ratio
        self.hidden_act = hidden_act
        self.conv_kernel_size = conv_kernel_size
        self.output_stride = output_stride
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.classifier_dropout_prob = classifier_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.aspp_out_channels = aspp_out_channels
        self.atrous_rates = atrous_rates
        self.aspp_dropout_prob = aspp_dropout_prob
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
class MobileViTOnnxConfig(OnnxConfig):
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
