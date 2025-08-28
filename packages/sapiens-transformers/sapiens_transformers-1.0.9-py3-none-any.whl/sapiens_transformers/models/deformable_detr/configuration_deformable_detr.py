"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class DeformableDetrConfig(PretrainedConfig):
    model_type = "deformable_detr"
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'encoder_attention_heads'}
    def __init__(self, use_timm_backbone=True, backbone_config=None, num_channels=3, num_queries=300, max_position_embeddings=1024, encoder_layers=6, encoder_ffn_dim=1024,
    encoder_attention_heads=8, decoder_layers=6, decoder_ffn_dim=1024, decoder_attention_heads=8, encoder_layerdrop=0.0, is_encoder_decoder=True, activation_function="relu",
    d_model=256, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, init_xavier_std=1.0, return_intermediate=True, auxiliary_loss=False,
    position_embedding_type="sine", backbone="resnet50", use_pretrained_backbone=True, backbone_kwargs=None, dilation=False, num_feature_levels=4, encoder_n_points=4,
    decoder_n_points=4, two_stage=False, two_stage_num_proposals=300, with_box_refine=False, class_cost=1, bbox_cost=5, giou_cost=2, mask_loss_coefficient=1,
    dice_loss_coefficient=1, bbox_loss_coefficient=5, giou_loss_coefficient=2, eos_coefficient=0.1, focal_alpha=0.25, disable_custom_kernels=False, **kwargs):
        if use_timm_backbone and backbone_kwargs is None:
            backbone_kwargs = {}
            if dilation: backbone_kwargs["output_stride"] = 16
            backbone_kwargs["out_indices"] = [2, 3, 4] if num_feature_levels > 1 else [4]
            backbone_kwargs["in_chans"] = num_channels
        elif not use_timm_backbone and backbone in (None, "resnet50"):
            if backbone_config is None:
                logger.info("`backbone_config` is `None`. Initializing the config with the default `ResNet` backbone.")
                backbone_config = CONFIG_MAPPING["resnet"](out_features=["stage4"])
            elif isinstance(backbone_config, dict):
                backbone_model_type = backbone_config.get("model_type")
                config_class = CONFIG_MAPPING[backbone_model_type]
                backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        self.use_timm_backbone = use_timm_backbone
        self.backbone_config = backbone_config
        self.num_channels = num_channels
        self.num_queries = num_queries
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.init_xavier_std = init_xavier_std
        self.encoder_layerdrop = encoder_layerdrop
        self.auxiliary_loss = auxiliary_loss
        self.position_embedding_type = position_embedding_type
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.backbone_kwargs = backbone_kwargs
        self.dilation = dilation
        self.num_feature_levels = num_feature_levels
        self.encoder_n_points = encoder_n_points
        self.decoder_n_points = decoder_n_points
        self.two_stage = two_stage
        self.two_stage_num_proposals = two_stage_num_proposals
        self.with_box_refine = with_box_refine
        if two_stage is True and with_box_refine is False: raise ValueError("If two_stage is True, with_box_refine must be True.")
        self.class_cost = class_cost
        self.bbox_cost = bbox_cost
        self.giou_cost = giou_cost
        self.mask_loss_coefficient = mask_loss_coefficient
        self.dice_loss_coefficient = dice_loss_coefficient
        self.bbox_loss_coefficient = bbox_loss_coefficient
        self.giou_loss_coefficient = giou_loss_coefficient
        self.eos_coefficient = eos_coefficient
        self.focal_alpha = focal_alpha
        self.disable_custom_kernels = disable_custom_kernels
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
    @property
    def num_attention_heads(self) -> int: return self.encoder_attention_heads
    @property
    def hidden_size(self) -> int: return self.d_model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
