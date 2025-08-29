"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Callable, List, Tuple, Union
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import BackboneConfigMixin, get_aligned_output_features_output_indices
logger = logging.get_logger(__name__)
class PvtV2Config(BackboneConfigMixin, PretrainedConfig):
    model_type = "pvt_v2"
    def __init__(self, image_size: Union[int, Tuple[int, int]] = 224, num_channels: int = 3, num_encoder_blocks: int = 4, depths: List[int] = [2, 2, 2, 2],
    sr_ratios: List[int] = [8, 4, 2, 1], hidden_sizes: List[int] = [32, 64, 160, 256], patch_sizes: List[int] = [7, 3, 3, 3], strides: List[int] = [4, 2, 2, 2],
    num_attention_heads: List[int] = [1, 2, 5, 8], mlp_ratios: List[int] = [8, 8, 4, 4], hidden_act: Union[str, Callable] = "gelu", hidden_dropout_prob: float = 0.0,
    attention_probs_dropout_prob: float = 0.0, initializer_range: float = 0.02, drop_path_rate: float = 0.0, layer_norm_eps: float = 1e-6, qkv_bias: bool = True,
    linear_attention: bool = False, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        image_size = (image_size, image_size) if isinstance(image_size, int) else image_size
        self.image_size = image_size
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
        self.initializer_range = initializer_range
        self.drop_path_rate = drop_path_rate
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.linear_attention = linear_attention
        self.stage_names = [f"stage{idx}" for idx in range(1, len(depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
