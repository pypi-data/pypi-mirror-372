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
class OmDetTurboConfig(PretrainedConfig):
    model_type = "omdet-turbo"
    attribute_map = {'encoder_hidden_dim': 'd_model', 'num_attention_heads': 'encoder_attention_heads'}
    def __init__(self, text_config=None, backbone_config=None, use_timm_backbone=True, backbone="swin_tiny_patch4_window7_224", backbone_kwargs=None, use_pretrained_backbone=False,
    apply_layernorm_after_vision_backbone=True, image_size=640, disable_custom_kernels=False, layer_norm_eps=1e-5, batch_norm_eps=1e-5, init_std=0.02, text_projection_in_dim=512,
    text_projection_out_dim=512, task_encoder_hidden_dim=1024, class_embed_dim=512, class_distance_type="cosine", num_queries=900, csp_activation="silu", conv_norm_activation="gelu",
    encoder_feedforward_activation="relu", encoder_feedforward_dropout=0.0, encoder_dropout=0.0, hidden_expansion=1, vision_features_channels=[256, 256, 256], encoder_hidden_dim=256,
    encoder_in_channels=[192, 384, 768], encoder_projection_indices=[2], encoder_attention_heads=8, encoder_dim_feedforward=2048, encoder_layers=1, positional_encoding_temperature=10000,
    num_feature_levels=3, decoder_hidden_dim=256, decoder_num_heads=8, decoder_num_layers=6, decoder_activation="relu", decoder_dim_feedforward=2048, decoder_num_points=4,
    decoder_dropout=0.0, eval_size=None, learn_initial_query=False, cache_size=100, is_encoder_decoder=True, **kwargs):
        if use_timm_backbone:
            if backbone_config is None: backbone_kwargs = {"out_indices": [1, 2, 3], "img_size": image_size, "always_partition": True}
        elif backbone_config is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `swin` vision config.")
            backbone_config = CONFIG_MAPPING["swin"](window_size=7, image_size=image_size, embed_dim=96, depths=[2, 2, 6, 2], num_heads=[3, 6, 12, 24], out_indices=[2, 3, 4])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.get("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        if text_config is None:
            logger.info("`text_config` is `None`. Initializing the config with the default `clip_text_model` text config.")
            text_config = CONFIG_MAPPING["clip_text_model"]()
        elif isinstance(text_config, dict):
            text_model_type = text_config.get("model_type")
            text_config = CONFIG_MAPPING[text_model_type](**text_config)
        if class_distance_type not in ["cosine", "dot"]: raise ValueError(f"Invalid `class_distance_type`. It should be either `cosine` or `dot`, but got {class_distance_type}.")
        self.text_config = text_config
        self.backbone_config = backbone_config
        self.use_timm_backbone = use_timm_backbone
        self.backbone = backbone
        self.backbone_kwargs = backbone_kwargs
        self.use_pretrained_backbone = use_pretrained_backbone
        self.apply_layernorm_after_vision_backbone = apply_layernorm_after_vision_backbone
        self.image_size = image_size
        self.disable_custom_kernels = disable_custom_kernels
        self.layer_norm_eps = layer_norm_eps
        self.batch_norm_eps = batch_norm_eps
        self.init_std = init_std
        self.text_projection_in_dim = text_projection_in_dim
        self.text_projection_out_dim = text_projection_out_dim
        self.task_encoder_hidden_dim = task_encoder_hidden_dim
        self.class_embed_dim = class_embed_dim
        self.class_distance_type = class_distance_type
        self.num_queries = num_queries
        self.csp_activation = csp_activation
        self.conv_norm_activation = conv_norm_activation
        self.encoder_feedforward_activation = encoder_feedforward_activation
        self.encoder_feedforward_dropout = encoder_feedforward_dropout
        self.encoder_dropout = encoder_dropout
        self.hidden_expansion = hidden_expansion
        self.vision_features_channels = vision_features_channels
        self.encoder_hidden_dim = encoder_hidden_dim
        self.encoder_in_channels = encoder_in_channels
        self.encoder_projection_indices = encoder_projection_indices
        self.encoder_attention_heads = encoder_attention_heads
        self.encoder_dim_feedforward = encoder_dim_feedforward
        self.encoder_layers = encoder_layers
        self.positional_encoding_temperature = positional_encoding_temperature
        self.num_feature_levels = num_feature_levels
        self.decoder_hidden_dim = decoder_hidden_dim
        self.decoder_num_heads = decoder_num_heads
        self.decoder_num_layers = decoder_num_layers
        self.decoder_activation = decoder_activation
        self.decoder_dim_feedforward = decoder_dim_feedforward
        self.decoder_num_points = decoder_num_points
        self.decoder_dropout = decoder_dropout
        self.eval_size = eval_size
        self.learn_initial_query = learn_initial_query
        self.cache_size = cache_size
        self.is_encoder_decoder = is_encoder_decoder
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
