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
class HieraConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "hiera"
    attribute_map = {"num_hidden_layers": "num_layers"}
    def __init__(self, embed_dim=96, image_size=[224, 224], patch_size=[7, 7], patch_stride=[4, 4], patch_padding=[3, 3], mlp_ratio=4.0, depths=[2, 3, 16, 3],
    num_heads=[1, 2, 4, 8], embed_dim_multiplier=2.0, num_query_pool=3, query_stride=[2, 2], masked_unit_size=[8, 8], masked_unit_attention=[True, True, False, False],
    drop_path_rate=0.0, num_channels=3, hidden_act="gelu", initializer_range=0.02, layer_norm_init=1.0, layer_norm_eps=1e-6, decoder_hidden_size=None, decoder_depth=None,
    decoder_num_heads=None, normalize_pixel_loss=True, mask_ratio=0.6, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        if masked_unit_size[0] % query_stride[0] ** (len(depths) - 1) != 0: raise ValueError(f"masked_unit_size[0] ({masked_unit_size[0]}) must be divisible by query_stride[0] ({query_stride[0]}) raised to the power of the number of layers ({len(depths) - 1})")
        if num_query_pool >= len(depths): raise ValueError(f"num_query_pool ({num_query_pool}) must be less than the number of layers ({len(depths)})")
        self.embed_dim = embed_dim
        self.image_size = image_size
        self.patch_size = patch_size
        self.patch_stride = patch_stride
        self.patch_padding = patch_padding
        self.mlp_ratio = mlp_ratio
        self.depths = depths
        self.num_heads = num_heads
        self.num_layers = len(depths)
        self.embed_dim_multiplier = embed_dim_multiplier
        self.num_query_pool = num_query_pool
        self.query_stride = query_stride
        self.masked_unit_size = masked_unit_size
        self.masked_unit_attention = masked_unit_attention
        self.drop_path_rate = drop_path_rate
        self.num_channels = num_channels
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_init = layer_norm_init
        self.layer_norm_eps = layer_norm_eps
        self.decoder_hidden_size = decoder_hidden_size
        self.decoder_depth = decoder_depth
        self.decoder_num_heads = decoder_num_heads
        self.normalize_pixel_loss = normalize_pixel_loss
        self.mask_ratio = mask_ratio
        self.hidden_size = int(embed_dim * embed_dim_multiplier ** (len(depths) - 1))
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
