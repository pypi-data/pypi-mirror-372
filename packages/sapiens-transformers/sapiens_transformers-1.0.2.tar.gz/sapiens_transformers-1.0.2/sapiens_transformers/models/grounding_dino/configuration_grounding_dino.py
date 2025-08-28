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
class GroundingDinoConfig(PretrainedConfig):
    model_type = "grounding-dino"
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'encoder_attention_heads'}
    def __init__(self, backbone_config=None, backbone=None, use_pretrained_backbone=False, use_timm_backbone=False, backbone_kwargs=None, text_config=None, num_queries=900,
    encoder_layers=6, encoder_ffn_dim=2048, encoder_attention_heads=8, decoder_layers=6, decoder_ffn_dim=2048, decoder_attention_heads=8, is_encoder_decoder=True,
    activation_function="relu", d_model=256, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, auxiliary_loss=False, position_embedding_type="sine",
    num_feature_levels=4, encoder_n_points=4, decoder_n_points=4, two_stage=True, class_cost=1.0, bbox_cost=5.0, giou_cost=2.0, bbox_loss_coefficient=5.0,
    giou_loss_coefficient=2.0, focal_alpha=0.25, disable_custom_kernels=False, max_text_len=256, text_enhancer_dropout=0.0, fusion_droppath=0.1, fusion_dropout=0.0,
    embedding_init_target=True, query_dim=4, decoder_bbox_embed_share=True, two_stage_bbox_embed_share=False, positional_embedding_temperature=20, init_std=0.02,
    layer_norm_eps=1e-5, **kwargs):
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `Swin` backbone.")
            backbone_config = CONFIG_MAPPING["swin"](window_size=7, image_size=224, embed_dim=96, depths=[2, 2, 6, 2], num_heads=[3, 6, 12, 24], out_indices=[2, 3, 4])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.pop("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the text config with default values (`BertConfig`).")
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        self.num_queries = num_queries
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
        self.auxiliary_loss = auxiliary_loss
        self.position_embedding_type = position_embedding_type
        self.num_feature_levels = num_feature_levels
        self.encoder_n_points = encoder_n_points
        self.decoder_n_points = decoder_n_points
        self.two_stage = two_stage
        self.class_cost = class_cost
        self.bbox_cost = bbox_cost
        self.giou_cost = giou_cost
        self.bbox_loss_coefficient = bbox_loss_coefficient
        self.giou_loss_coefficient = giou_loss_coefficient
        self.focal_alpha = focal_alpha
        self.disable_custom_kernels = disable_custom_kernels
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "bert"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["bert"]()
        self.text_config = text_config
        self.max_text_len = max_text_len
        self.text_enhancer_dropout = text_enhancer_dropout
        self.fusion_droppath = fusion_droppath
        self.fusion_dropout = fusion_dropout
        self.embedding_init_target = embedding_init_target
        self.query_dim = query_dim
        self.decoder_bbox_embed_share = decoder_bbox_embed_share
        self.two_stage_bbox_embed_share = two_stage_bbox_embed_share
        if two_stage_bbox_embed_share and not decoder_bbox_embed_share: raise ValueError("If two_stage_bbox_embed_share is True, decoder_bbox_embed_share must be True.")
        self.positional_embedding_temperature = positional_embedding_temperature
        self.init_std = init_std
        self.layer_norm_eps = layer_norm_eps
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
