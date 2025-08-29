"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class TableTransformerConfig(PretrainedConfig):
    model_type = "table-transformer"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'encoder_attention_heads'}
    def __init__(self, use_timm_backbone=True, backbone_config=None, num_channels=3, num_queries=100, encoder_layers=6, encoder_ffn_dim=2048, encoder_attention_heads=8,
    decoder_layers=6, decoder_ffn_dim=2048, decoder_attention_heads=8, encoder_layerdrop=0.0, decoder_layerdrop=0.0, is_encoder_decoder=True, activation_function="relu",
    d_model=256, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, init_xavier_std=1.0, auxiliary_loss=False, position_embedding_type="sine",
    backbone="resnet50", use_pretrained_backbone=True, backbone_kwargs=None, dilation=False, class_cost=1, bbox_cost=5, giou_cost=2, mask_loss_coefficient=1, dice_loss_coefficient=1,
    bbox_loss_coefficient=5, giou_loss_coefficient=2, eos_coefficient=0.1, **kwargs):
        if use_timm_backbone and backbone_kwargs is None:
            backbone_kwargs = {}
            if dilation: backbone_kwargs["output_stride"] = 16
            backbone_kwargs["out_indices"] = [1, 2, 3, 4]
            backbone_kwargs["in_chans"] = num_channels
        elif not use_timm_backbone and backbone in (None, "resnet50"):
            if backbone_config is None:
                logger.info("`backbone_config` is `None`. Initializing the config with the default `ResNet` backbone.")
                backbone_config = CONFIG_MAPPING["resnet"](out_features=["stage4"])
            elif isinstance(backbone_config, dict):
                backbone_model_type = backbone_config.get("model_type")
                config_class = CONFIG_MAPPING[backbone_model_type]
                backbone_config = config_class.from_dict(backbone_config)
            backbone = None
            dilation = None
        verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        self.use_timm_backbone = use_timm_backbone
        self.backbone_config = backbone_config
        self.num_channels = num_channels
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
        self.init_std = init_std
        self.init_xavier_std = init_xavier_std
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.num_hidden_layers = encoder_layers
        self.auxiliary_loss = auxiliary_loss
        self.position_embedding_type = position_embedding_type
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.backbone_kwargs = backbone_kwargs
        self.dilation = dilation
        self.class_cost = class_cost
        self.bbox_cost = bbox_cost
        self.giou_cost = giou_cost
        self.mask_loss_coefficient = mask_loss_coefficient
        self.dice_loss_coefficient = dice_loss_coefficient
        self.bbox_loss_coefficient = bbox_loss_coefficient
        self.giou_loss_coefficient = giou_loss_coefficient
        self.eos_coefficient = eos_coefficient
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
    @property
    def num_attention_heads(self) -> int: return self.encoder_attention_heads
    @property
    def hidden_size(self) -> int: return self.d_model
class TableTransformerOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"}), ("pixel_mask", {0: "batch"})])
    @property
    def atol_for_validation(self) -> float: return 1e-5
    @property
    def default_onnx_opset(self) -> int: return 12
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
