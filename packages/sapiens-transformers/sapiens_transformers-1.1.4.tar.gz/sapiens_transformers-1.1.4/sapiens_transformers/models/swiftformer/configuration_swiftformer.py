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
class SwiftFormerConfig(PretrainedConfig):
    model_type = "swiftformer"
    def __init__(self, image_size=224, num_channels=3, depths=[3, 3, 6, 4], embed_dims=[48, 56, 112, 220], mlp_ratio=4, downsamples=[True, True, True, True], hidden_act="gelu",
    down_patch_size=3, down_stride=2, down_pad=1, drop_path_rate=0.0, drop_mlp_rate=0.0, drop_conv_encoder_rate=0.0, use_layer_scale=True, layer_scale_init_value=1e-5,
    batch_norm_eps=1e-5, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.num_channels = num_channels
        self.depths = depths
        self.embed_dims = embed_dims
        self.mlp_ratio = mlp_ratio
        self.downsamples = downsamples
        self.hidden_act = hidden_act
        self.down_patch_size = down_patch_size
        self.down_stride = down_stride
        self.down_pad = down_pad
        self.drop_path_rate = drop_path_rate
        self.drop_mlp_rate = drop_mlp_rate
        self.drop_conv_encoder_rate = drop_conv_encoder_rate
        self.use_layer_scale = use_layer_scale
        self.layer_scale_init_value = layer_scale_init_value
        self.batch_norm_eps = batch_norm_eps
class SwiftFormerOnnxConfig(OnnxConfig):
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
