"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
from ..detr import DetrConfig
from ..swin import SwinConfig
logger = logging.get_logger(__name__)
class MaskFormerConfig(PretrainedConfig):
    model_type = "maskformer"
    attribute_map = {"hidden_size": "mask_feature_size"}
    backbones_supported = ["resnet", "swin"]
    decoders_supported = ["detr"]
    def __init__(self, fpn_feature_size: int = 256, mask_feature_size: int = 256, no_object_weight: float = 0.1, use_auxiliary_loss: bool = False, backbone_config: Optional[Dict] = None,
    decoder_config: Optional[Dict] = None, init_std: float = 0.02, init_xavier_std: float = 1.0, dice_weight: float = 1.0, cross_entropy_weight: float = 1.0, mask_weight: float = 20.0,
    output_auxiliary_logits: Optional[bool] = None, backbone: Optional[str] = None, use_pretrained_backbone: bool = False, use_timm_backbone: bool = False, backbone_kwargs: Optional[Dict] = None, **kwargs):
        if backbone_config is None and backbone is None:
            backbone_config = SwinConfig(image_size=384, in_channels=3, patch_size=4, embed_dim=128, depths=[2, 2, 18, 2], num_heads=[4, 8, 16, 32], window_size=12,
            drop_path_rate=0.3, out_features=["stage1", "stage2", "stage3", "stage4"])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.pop("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        if backbone_config is not None and backbone_config.model_type not in self.backbones_supported: logger.warning_once(f"Backbone {backbone_config.model_type} is not a supported model and may not be compatible with MaskFormer. Supported model types: {','.join(self.backbones_supported)}")
        if decoder_config is None: decoder_config = DetrConfig()
        else:
            decoder_type = (decoder_config.pop("model_type") if isinstance(decoder_config, dict) else decoder_config.model_type)
            if decoder_type not in self.decoders_supported: raise ValueError(f"Transformer Decoder {decoder_type} not supported, please use one of {','.join(self.decoders_supported)}")
            if isinstance(decoder_config, dict):
                config_class = CONFIG_MAPPING[decoder_type]
                decoder_config = config_class.from_dict(decoder_config)
        self.backbone_config = backbone_config
        self.decoder_config = decoder_config
        self.fpn_feature_size = fpn_feature_size
        self.mask_feature_size = mask_feature_size
        self.init_std = init_std
        self.init_xavier_std = init_xavier_std
        self.cross_entropy_weight = cross_entropy_weight
        self.dice_weight = dice_weight
        self.mask_weight = mask_weight
        self.use_auxiliary_loss = use_auxiliary_loss
        self.no_object_weight = no_object_weight
        self.output_auxiliary_logits = output_auxiliary_logits
        self.num_attention_heads = self.decoder_config.encoder_attention_heads
        self.num_hidden_layers = self.decoder_config.num_hidden_layers
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        super().__init__(**kwargs)
    @classmethod
    def from_backbone_and_decoder_configs(cls, backbone_config: PretrainedConfig, decoder_config: PretrainedConfig, **kwargs): return cls(backbone_config=backbone_config, decoder_config=decoder_config, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
