"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
from ...auto.configuration_auto import CONFIG_MAPPING
from ...bit import BitConfig
logger = logging.get_logger(__name__)
class ViTHybridConfig(PretrainedConfig):
    model_type = "vit-hybrid"
    def __init__(self, backbone_config=None, backbone=None, use_pretrained_backbone=False, use_timm_backbone=False, backbone_kwargs=None, hidden_size=768, num_hidden_layers=12,
    num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-12,
    image_size=224, patch_size=1, num_channels=3, backbone_featmap_shape=[1, 1024, 24, 24], qkv_bias=True, **kwargs):
        super().__init__(**kwargs)
        if use_pretrained_backbone: raise ValueError("Pretrained backbones are not supported yet.")
        if backbone_config is not None and backbone is not None: raise ValueError("You can't specify both `backbone` and `backbone_config`.")
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with a `BiT` backbone.")
            backbone_config = {'global_padding': 'same', 'layer_type': 'bottleneck', 'depths': [3, 4, 9], 'out_features': ['stage3'], 'embedding_dynamic_padding': True}
        if backbone_kwargs is not None and backbone_kwargs and backbone_config is not None: raise ValueError("You can't specify both `backbone_kwargs` and `backbone_config`.")
        if isinstance(backbone_config, dict):
            if "model_type" in backbone_config: backbone_config_class = CONFIG_MAPPING[backbone_config["model_type"]]
            else:
                logger.info("`model_type` is not found in `backbone_config`. Use `Bit` as the backbone configuration class.")
                backbone_config_class = BitConfig
            backbone_config = backbone_config_class(**backbone_config)
        self.backbone_featmap_shape = backbone_featmap_shape
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
