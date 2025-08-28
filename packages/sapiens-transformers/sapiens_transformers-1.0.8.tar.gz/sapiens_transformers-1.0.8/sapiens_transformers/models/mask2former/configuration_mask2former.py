"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, List, Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class Mask2FormerConfig(PretrainedConfig):
    model_type = "mask2former"
    backbones_supported = ["swin"]
    attribute_map = {"hidden_size": "hidden_dim"}
    def __init__(self, backbone_config: Optional[Dict] = None, feature_size: int = 256, mask_feature_size: int = 256, hidden_dim: int = 256, encoder_feedforward_dim: int = 1024,
    activation_function: str = "relu", encoder_layers: int = 6, decoder_layers: int = 10, num_attention_heads: int = 8, dropout: float = 0.0, dim_feedforward: int = 2048,
    pre_norm: bool = False, enforce_input_projection: bool = False, common_stride: int = 4, ignore_value: int = 255, num_queries: int = 100, no_object_weight: float = 0.1,
    class_weight: float = 2.0, mask_weight: float = 5.0, dice_weight: float = 5.0, train_num_points: int = 12544, oversample_ratio: float = 3.0, importance_sample_ratio: float = 0.75,
    init_std: float = 0.02, init_xavier_std: float = 1.0, use_auxiliary_loss: bool = True, feature_strides: List[int] = [4, 8, 16, 32], output_auxiliary_logits: bool = None,
    backbone: Optional[str] = None, use_pretrained_backbone: bool = False, use_timm_backbone: bool = False, backbone_kwargs: Optional[Dict] = None, **kwargs):
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `Swin` backbone.")
            backbone_config = CONFIG_MAPPING["swin"](image_size=224, in_channels=3, patch_size=4, embed_dim=96, depths=[2, 2, 18, 2], num_heads=[3, 6, 12, 24],
            window_size=7, drop_path_rate=0.3, use_absolute_embeddings=False, out_features=["stage1", "stage2", "stage3", "stage4"])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.pop("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        if backbone_config is not None and backbone_config.model_type not in self.backbones_supported: logger.warning_once(f"Backbone {backbone_config.model_type} is not a supported model and may not be compatible with Mask2Former. Supported model types: {','.join(self.backbones_supported)}")
        self.backbone_config = backbone_config
        self.feature_size = feature_size
        self.mask_feature_size = mask_feature_size
        self.hidden_dim = hidden_dim
        self.encoder_feedforward_dim = encoder_feedforward_dim
        self.activation_function = activation_function
        self.encoder_layers = encoder_layers
        self.decoder_layers = decoder_layers
        self.num_attention_heads = num_attention_heads
        self.dropout = dropout
        self.dim_feedforward = dim_feedforward
        self.pre_norm = pre_norm
        self.enforce_input_projection = enforce_input_projection
        self.common_stride = common_stride
        self.ignore_value = ignore_value
        self.num_queries = num_queries
        self.no_object_weight = no_object_weight
        self.class_weight = class_weight
        self.mask_weight = mask_weight
        self.dice_weight = dice_weight
        self.train_num_points = train_num_points
        self.oversample_ratio = oversample_ratio
        self.importance_sample_ratio = importance_sample_ratio
        self.init_std = init_std
        self.init_xavier_std = init_xavier_std
        self.use_auxiliary_loss = use_auxiliary_loss
        self.feature_strides = feature_strides
        self.output_auxiliary_logits = output_auxiliary_logits
        self.num_hidden_layers = decoder_layers
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        super().__init__(**kwargs)
    @classmethod
    def from_backbone_config(cls, backbone_config: PretrainedConfig, **kwargs): return cls(backbone_config=backbone_config, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
