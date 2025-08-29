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
class MgpstrConfig(PretrainedConfig):
    model_type = "mgp-str"
    def __init__(self, image_size=[32, 128], patch_size=4, num_channels=3, max_token_length=27, num_character_labels=38, num_bpe_labels=50257, num_wordpiece_labels=30522,
    hidden_size=768, num_hidden_layers=12, num_attention_heads=12, mlp_ratio=4.0, qkv_bias=True, distilled=False, layer_norm_eps=1e-5, drop_rate=0.0, attn_drop_rate=0.0,
    drop_path_rate=0.0, output_a3_attentions=False, initializer_range=0.02, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.max_token_length = max_token_length
        self.num_character_labels = num_character_labels
        self.num_bpe_labels = num_bpe_labels
        self.num_wordpiece_labels = num_wordpiece_labels
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.mlp_ratio = mlp_ratio
        self.distilled = distilled
        self.layer_norm_eps = layer_norm_eps
        self.drop_rate = drop_rate
        self.qkv_bias = qkv_bias
        self.attn_drop_rate = attn_drop_rate
        self.drop_path_rate = drop_path_rate
        self.output_a3_attentions = output_a3_attentions
        self.initializer_range = initializer_range
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
