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
class ConvNextV2Config(BackboneConfigMixin, PretrainedConfig):
    model_type = "convnextv2"
    def __init__(self, num_channels=3, patch_size=4, num_stages=4, hidden_sizes=None, depths=None, hidden_act="gelu", initializer_range=0.02, layer_norm_eps=1e-12,
    drop_path_rate=0.0, image_size=224, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.num_stages = num_stages
        self.hidden_sizes = [96, 192, 384, 768] if hidden_sizes is None else hidden_sizes
        self.depths = [3, 3, 9, 3] if depths is None else depths
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.drop_path_rate = drop_path_rate
        self.image_size = image_size
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(self.depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
