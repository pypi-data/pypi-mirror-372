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
class SegGptConfig(PretrainedConfig):
    model_type = "seggpt"
    def __init__(self, hidden_size=1024, num_hidden_layers=24, num_attention_heads=16, hidden_act="gelu", hidden_dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-6,
    image_size=[896, 448], patch_size=16, num_channels=3, qkv_bias=True, mlp_dim=None, drop_path_rate=0.1, pretrain_image_size=224, decoder_hidden_size=64, use_relative_position_embeddings=True,
    merge_index=2, intermediate_hidden_state_indices=[5, 11, 17, 23], beta=0.01, **kwargs):
        super().__init__(**kwargs)
        if merge_index > min(intermediate_hidden_state_indices): raise ValueError(f"Merge index must be less than the minimum encoder output index, but got {merge_index=} and {intermediate_hidden_state_indices=}")
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
        self.drop_path_rate = drop_path_rate
        self.pretrain_image_size = pretrain_image_size
        self.decoder_hidden_size = decoder_hidden_size
        self.use_relative_position_embeddings = use_relative_position_embeddings
        self.merge_index = merge_index
        self.intermediate_hidden_state_indices = intermediate_hidden_state_indices
        self.beta = beta
        self.mlp_dim = int(hidden_size * 4) if mlp_dim is None else mlp_dim
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
