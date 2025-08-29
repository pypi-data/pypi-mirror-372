"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class VanConfig(PretrainedConfig):
    model_type = "van"
    def __init__(self, image_size=224, num_channels=3, patch_sizes=[7, 3, 3, 3], strides=[4, 2, 2, 2], hidden_sizes=[64, 128, 320, 512], depths=[3, 3, 12, 3], mlp_ratios=[8, 8, 4, 4],
    hidden_act="gelu", initializer_range=0.02, layer_norm_eps=1e-6, layer_scale_init_value=1e-2, drop_path_rate=0.0, dropout_rate=0.0, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.num_channels = num_channels
        self.patch_sizes = patch_sizes
        self.strides = strides
        self.hidden_sizes = hidden_sizes
        self.depths = depths
        self.mlp_ratios = mlp_ratios
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.layer_scale_init_value = layer_scale_init_value
        self.drop_path_rate = drop_path_rate
        self.dropout_rate = dropout_rate
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
