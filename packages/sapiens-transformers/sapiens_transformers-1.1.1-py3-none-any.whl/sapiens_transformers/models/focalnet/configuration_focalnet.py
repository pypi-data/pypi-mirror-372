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
class FocalNetConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "focalnet"
    def __init__(self, image_size=224, patch_size=4, num_channels=3, embed_dim=96, use_conv_embed=False, hidden_sizes=[192, 384, 768, 768], depths=[2, 2, 6, 2], focal_levels=[2, 2, 2, 2],
    focal_windows=[3, 3, 3, 3], hidden_act="gelu", mlp_ratio=4.0, hidden_dropout_prob=0.0, drop_path_rate=0.1, use_layerscale=False, layerscale_value=1e-4, use_post_layernorm=False,
    use_post_layernorm_in_modulation=False, normalize_modulator=False, initializer_range=0.02, layer_norm_eps=1e-5, encoder_stride=32, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.embed_dim = embed_dim
        self.use_conv_embed = use_conv_embed
        self.hidden_sizes = hidden_sizes
        self.depths = depths
        self.focal_levels = focal_levels
        self.focal_windows = focal_windows
        self.hidden_act = hidden_act
        self.mlp_ratio = mlp_ratio
        self.hidden_dropout_prob = hidden_dropout_prob
        self.drop_path_rate = drop_path_rate
        self.use_layerscale = use_layerscale
        self.layerscale_value = layerscale_value
        self.use_post_layernorm = use_post_layernorm
        self.use_post_layernorm_in_modulation = use_post_layernorm_in_modulation
        self.normalize_modulator = normalize_modulator
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.encoder_stride = encoder_stride
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(self.depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
