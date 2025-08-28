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
class TimmBackboneConfig(PretrainedConfig):
    model_type = "timm_backbone"
    def __init__(self, backbone=None, num_channels=3, features_only=True, use_pretrained_backbone=True, out_indices=None, freeze_batch_norm_2d=False, **kwargs):
        super().__init__(**kwargs)
        self.backbone = backbone
        self.num_channels = num_channels
        self.features_only = features_only
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = True
        self.out_indices = out_indices if out_indices is not None else [-1]
        self.freeze_batch_norm_2d = freeze_batch_norm_2d
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
