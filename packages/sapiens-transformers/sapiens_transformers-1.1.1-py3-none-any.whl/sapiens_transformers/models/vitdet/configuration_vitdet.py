"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import BackboneConfigMixin, get_aligned_output_features_output_indices
logger = logging.get_logger(__name__)
class VitDetConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "vitdet"
    def __init__(self, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, mlp_ratio=4, hidden_act="gelu", dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-6,
    image_size=224, pretrain_image_size=224, patch_size=16, num_channels=3, qkv_bias=True, drop_path_rate=0.0, window_block_indices=[], residual_block_indices=[],
    use_absolute_position_embeddings=True, use_relative_position_embeddings=False, window_size=0, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.mlp_ratio = mlp_ratio
        self.hidden_act = hidden_act
        self.dropout_prob = dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.pretrain_image_size = pretrain_image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
        self.drop_path_rate = drop_path_rate
        self.window_block_indices = window_block_indices
        self.residual_block_indices = residual_block_indices
        self.use_absolute_position_embeddings = use_absolute_position_embeddings
        self.use_relative_position_embeddings = use_relative_position_embeddings
        self.window_size = window_size
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, self.num_hidden_layers + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
