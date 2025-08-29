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
class VideoMAEConfig(PretrainedConfig):
    model_type = "videomae"
    def __init__(self, image_size=224, patch_size=16, num_channels=3, num_frames=16, tubelet_size=2, hidden_size=768, num_hidden_layers=12, num_attention_heads=12,
    intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-12, qkv_bias=True,
    use_mean_pooling=True, decoder_num_attention_heads=6, decoder_hidden_size=384, decoder_num_hidden_layers=4, decoder_intermediate_size=1536, norm_pix_loss=True, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_frames = num_frames
        self.tubelet_size = tubelet_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.use_mean_pooling = use_mean_pooling
        self.decoder_num_attention_heads = decoder_num_attention_heads
        self.decoder_hidden_size = decoder_hidden_size
        self.decoder_num_hidden_layers = decoder_num_hidden_layers
        self.decoder_intermediate_size = decoder_intermediate_size
        self.norm_pix_loss = norm_pix_loss
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
