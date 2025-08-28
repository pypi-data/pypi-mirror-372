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
from .configuration_rt_detr_resnet import RTDetrResNetConfig
logger = logging.get_logger(__name__)
class RTDetrConfig(PretrainedConfig):
    model_type = "rt_detr"
    layer_types = ["basic", "bottleneck"]
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'encoder_attention_heads'}
    def __init__(self, initializer_range=0.01, initializer_bias_prior_prob=None, layer_norm_eps=1e-5, batch_norm_eps=1e-5, backbone_config=None, backbone=None,
    use_pretrained_backbone=False, use_timm_backbone=False, freeze_backbone_batch_norms=True, backbone_kwargs=None, encoder_hidden_dim=256, encoder_in_channels=[512, 1024, 2048],
    feat_strides=[8, 16, 32], encoder_layers=1, encoder_ffn_dim=1024, encoder_attention_heads=8, dropout=0.0, activation_dropout=0.0, encode_proj_layers=[2],
    positional_encoding_temperature=10000, encoder_activation_function="gelu", activation_function="silu", eval_size=None, normalize_before=False, hidden_expansion=1.0,
    d_model=256, num_queries=300, decoder_in_channels=[256, 256, 256], decoder_ffn_dim=1024, num_feature_levels=3, decoder_n_points=4, decoder_layers=6, decoder_attention_heads=8,
    decoder_activation_function="relu", attention_dropout=0.0, num_denoising=100, label_noise_ratio=0.5, box_noise_scale=1.0, learn_initial_query=False, anchor_image_size=None,
    disable_custom_kernels=True, with_box_refine=True, is_encoder_decoder=True, matcher_alpha=0.25, matcher_gamma=2.0, matcher_class_cost=2.0, matcher_bbox_cost=5.0,
    matcher_giou_cost=2.0, use_focal_loss=True, auxiliary_loss=True, focal_loss_alpha=0.75, focal_loss_gamma=2.0, weight_loss_vfl=1.0, weight_loss_bbox=5.0,
    weight_loss_giou=2.0, eos_coefficient=1e-4, **kwargs):
        self.initializer_range = initializer_range
        self.initializer_bias_prior_prob = initializer_bias_prior_prob
        self.layer_norm_eps = layer_norm_eps
        self.batch_norm_eps = batch_norm_eps
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` and `backbone` are `None`. Initializing the config with the default `RTDetr-ResNet` backbone.")
            backbone_config = RTDetrResNetConfig(num_channels=3, embedding_size=64, hidden_sizes=[256, 512, 1024, 2048], depths=[3, 4, 6, 3], layer_type="bottleneck",
            hidden_act="relu", downsample_in_first_stage=False, downsample_in_bottleneck=False, out_features=None, out_indices=[2, 3, 4])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.pop("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.freeze_backbone_batch_norms = freeze_backbone_batch_norms
        self.backbone_kwargs = backbone_kwargs
        self.encoder_hidden_dim = encoder_hidden_dim
        self.encoder_in_channels = encoder_in_channels
        self.feat_strides = feat_strides
        self.encoder_attention_heads = encoder_attention_heads
        self.encoder_ffn_dim = encoder_ffn_dim
        self.dropout = dropout
        self.activation_dropout = activation_dropout
        self.encode_proj_layers = encode_proj_layers
        self.encoder_layers = encoder_layers
        self.positional_encoding_temperature = positional_encoding_temperature
        self.eval_size = eval_size
        self.normalize_before = normalize_before
        self.encoder_activation_function = encoder_activation_function
        self.activation_function = activation_function
        self.hidden_expansion = hidden_expansion
        self.d_model = d_model
        self.num_queries = num_queries
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_in_channels = decoder_in_channels
        self.num_feature_levels = num_feature_levels
        self.decoder_n_points = decoder_n_points
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.decoder_activation_function = decoder_activation_function
        self.attention_dropout = attention_dropout
        self.num_denoising = num_denoising
        self.label_noise_ratio = label_noise_ratio
        self.box_noise_scale = box_noise_scale
        self.learn_initial_query = learn_initial_query
        self.anchor_image_size = anchor_image_size
        self.auxiliary_loss = auxiliary_loss
        self.disable_custom_kernels = disable_custom_kernels
        self.with_box_refine = with_box_refine
        self.matcher_alpha = matcher_alpha
        self.matcher_gamma = matcher_gamma
        self.matcher_class_cost = matcher_class_cost
        self.matcher_bbox_cost = matcher_bbox_cost
        self.matcher_giou_cost = matcher_giou_cost
        self.use_focal_loss = use_focal_loss
        self.focal_loss_alpha = focal_loss_alpha
        self.focal_loss_gamma = focal_loss_gamma
        self.weight_loss_vfl = weight_loss_vfl
        self.weight_loss_bbox = weight_loss_bbox
        self.weight_loss_giou = weight_loss_giou
        self.eos_coefficient = eos_coefficient
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
    @property
    def num_attention_heads(self) -> int: return self.encoder_attention_heads
    @property
    def hidden_size(self) -> int: return self.d_model
    @classmethod
    def from_backbone_configs(cls, backbone_config: PretrainedConfig, **kwargs): return cls(backbone_config=backbone_config, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
