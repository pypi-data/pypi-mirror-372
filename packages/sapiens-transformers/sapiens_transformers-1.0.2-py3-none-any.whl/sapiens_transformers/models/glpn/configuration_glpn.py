"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class GLPNConfig(PretrainedConfig):
    model_type = "glpn"
    def __init__(self, num_channels=3, num_encoder_blocks=4, depths=[2, 2, 2, 2], sr_ratios=[8, 4, 2, 1], hidden_sizes=[32, 64, 160, 256], patch_sizes=[7, 3, 3, 3],
    strides=[4, 2, 2, 2], num_attention_heads=[1, 2, 5, 8], mlp_ratios=[4, 4, 4, 4], hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0,
    initializer_range=0.02, drop_path_rate=0.1, layer_norm_eps=1e-6, decoder_hidden_size=64, max_depth=10, head_in_index=-1, **kwargs):
        super().__init__(**kwargs)
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
        self.decoder_hidden_size = decoder_hidden_size
        self.max_depth = max_depth
        self.head_in_index = head_in_index
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
