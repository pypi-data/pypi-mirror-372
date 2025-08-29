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
class BitConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "bit"
    layer_types = ["preactivation", "bottleneck"]
    supported_padding = ["SAME", "VALID"]
    def __init__(self, num_channels=3, embedding_size=64, hidden_sizes=[256, 512, 1024, 2048], depths=[3, 4, 6, 3], layer_type="preactivation", hidden_act="relu",
    global_padding=None, num_groups=32, drop_path_rate=0.0, embedding_dynamic_padding=False, output_stride=32, width_factor=1, out_features=None, out_indices=None, **kwargs):
        super().__init__(**kwargs)
        if layer_type not in self.layer_types: raise ValueError(f"layer_type={layer_type} is not one of {','.join(self.layer_types)}")
        if global_padding is not None:
            if global_padding.upper() in self.supported_padding: global_padding = global_padding.upper()
            else: raise ValueError(f"Padding strategy {global_padding} not supported")
        self.num_channels = num_channels
        self.embedding_size = embedding_size
        self.hidden_sizes = hidden_sizes
        self.depths = depths
        self.layer_type = layer_type
        self.hidden_act = hidden_act
        self.global_padding = global_padding
        self.num_groups = num_groups
        self.drop_path_rate = drop_path_rate
        self.embedding_dynamic_padding = embedding_dynamic_padding
        self.output_stride = output_stride
        self.width_factor = width_factor
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(depths) + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
