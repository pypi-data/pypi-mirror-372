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
class RTDetrResNetConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "rt_detr_resnet"
    layer_types = ["basic", "bottleneck"]
    def __init__(self, num_channels=3, embedding_size=64, hidden_sizes=[256, 512, 1024, 2048], depths=[3, 4, 6, 3], layer_type="bottleneck", hidden_act="relu", downsample_in_first_stage=False,
    downsample_in_bottleneck=False, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        if layer_type not in self.layer_types: raise ValueError(f"layer_type={layer_type} is not one of {','.join(self.layer_types)}")
        self.num_channels = num_channels
        self.embedding_size = embedding_size
        self.hidden_sizes = hidden_sizes
        self.depths = depths
        self.layer_type = layer_type
        self.hidden_act = hidden_act
        self.downsample_in_first_stage = downsample_in_first_stage
        self.downsample_in_bottleneck = downsample_in_bottleneck
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
