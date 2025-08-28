"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from typing import List
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto.configuration_auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class VitMatteConfig(PretrainedConfig):
    model_type = "vitmatte"
    def __init__(self, backbone_config: PretrainedConfig = None, backbone=None, use_pretrained_backbone=False, use_timm_backbone=False, backbone_kwargs=None, hidden_size: int = 384,
    batch_norm_eps: float = 1e-5, initializer_range: float = 0.02, convstream_hidden_sizes: List[int] = [48, 96, 192], fusion_hidden_sizes: List[int] = [256, 128, 64, 32], **kwargs):
        super().__init__(**kwargs)
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `VitDet` backbone.")
            backbone_config = CONFIG_MAPPING["vitdet"](out_features=["stage4"])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.get("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        self.batch_norm_eps = batch_norm_eps
        self.hidden_size = hidden_size
        self.initializer_range = initializer_range
        self.convstream_hidden_sizes = convstream_hidden_sizes
        self.fusion_hidden_sizes = fusion_hidden_sizes
    def to_dict(self):
        output = copy.deepcopy(self.__dict__)
        output["backbone_config"] = self.backbone_config.to_dict()
        output["model_type"] = self.__class__.model_type
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
