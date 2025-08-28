"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class EfficientFormerConfig(PretrainedConfig):
    model_type = "efficientformer"
    def __init__(self, depths: List[int] = [3, 2, 6, 4], hidden_sizes: List[int] = [48, 96, 224, 448], downsamples: List[bool] = [True, True, True, True], dim: int = 448,
    key_dim: int = 32, attention_ratio: int = 4, resolution: int = 7, num_hidden_layers: int = 5, num_attention_heads: int = 8, mlp_expansion_ratio: int = 4, hidden_dropout_prob: float = 0.0,
    patch_size: int = 16, num_channels: int = 3, pool_size: int = 3, downsample_patch_size: int = 3, downsample_stride: int = 2, downsample_pad: int = 1, drop_path_rate: float = 0.0,
    num_meta3d_blocks: int = 1, distillation: bool = True, use_layer_scale: bool = True, layer_scale_init_value: float = 1e-5, hidden_act: str = "gelu", initializer_range: float = 0.02,
    layer_norm_eps: float = 1e-12, image_size: int = 224, batch_norm_eps: float = 1e-05, **kwargs) -> None:
        super().__init__(**kwargs)
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.hidden_sizes = hidden_sizes
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.depths = depths
        self.mlp_expansion_ratio = mlp_expansion_ratio
        self.downsamples = downsamples
        self.dim = dim
        self.key_dim = key_dim
        self.attention_ratio = attention_ratio
        self.resolution = resolution
        self.pool_size = pool_size
        self.downsample_patch_size = downsample_patch_size
        self.downsample_stride = downsample_stride
        self.downsample_pad = downsample_pad
        self.drop_path_rate = drop_path_rate
        self.num_meta3d_blocks = num_meta3d_blocks
        self.distillation = distillation
        self.use_layer_scale = use_layer_scale
        self.layer_scale_init_value = layer_scale_init_value
        self.image_size = image_size
        self.batch_norm_eps = batch_norm_eps
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
