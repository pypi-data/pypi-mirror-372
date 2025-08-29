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
class MobileNetV2Config(PretrainedConfig):
    model_type = "mobilenet_v2"
    def __init__(self, num_channels=3, image_size=224, depth_multiplier=1.0, depth_divisible_by=8, min_depth=8, expand_ratio=6.0, output_stride=32, first_layer_is_expansion=True,
    finegrained_output=True, hidden_act="relu6", tf_padding=True, classifier_dropout_prob=0.8, initializer_range=0.02, layer_norm_eps=0.001, semantic_loss_ignore_index=255, **kwargs):
        super().__init__(**kwargs)
        if depth_multiplier <= 0: raise ValueError("depth_multiplier must be greater than zero.")
        self.num_channels = num_channels
        self.image_size = image_size
        self.depth_multiplier = depth_multiplier
        self.depth_divisible_by = depth_divisible_by
        self.min_depth = min_depth
        self.expand_ratio = expand_ratio
        self.output_stride = output_stride
        self.first_layer_is_expansion = first_layer_is_expansion
        self.finegrained_output = finegrained_output
        self.hidden_act = hidden_act
        self.tf_padding = tf_padding
        self.classifier_dropout_prob = classifier_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
class MobileNetV2OnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch"})])
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
