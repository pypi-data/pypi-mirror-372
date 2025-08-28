"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class TvpConfig(PretrainedConfig):
    model_type = "tvp"
    def __init__(self, backbone_config=None, backbone=None, use_pretrained_backbone=False, use_timm_backbone=False, backbone_kwargs=None, distance_loss_weight=1.0,
    duration_loss_weight=0.1, visual_prompter_type="framepad", visual_prompter_apply="replace", visual_prompt_size=96, max_img_size=448, num_frames=48, vocab_size=30522,
    hidden_size=768, intermediate_size=3072, num_hidden_layers=12, num_attention_heads=12, max_position_embeddings=512, max_grid_col_position_embeddings=100, max_grid_row_position_embeddings=100,
    hidden_dropout_prob=0.1, hidden_act="gelu", layer_norm_eps=1e-12, initializer_range=0.02, attention_probs_dropout_prob=0.1, **kwargs):
        super().__init__(**kwargs)
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `ResNet` backbone.")
            backbone_config = CONFIG_MAPPING["resnet"](out_features=["stage4"])
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
        self.distance_loss_weight = distance_loss_weight
        self.duration_loss_weight = duration_loss_weight
        self.visual_prompter_type = visual_prompter_type
        self.visual_prompter_apply = visual_prompter_apply
        self.visual_prompt_size = visual_prompt_size
        self.max_img_size = max_img_size
        self.num_frames = num_frames
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.max_grid_col_position_embeddings = max_grid_col_position_embeddings
        self.max_grid_row_position_embeddings = max_grid_row_position_embeddings
        self.layer_norm_eps = layer_norm_eps
        self.hidden_dropout_prob = hidden_dropout_prob
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
    @classmethod
    def from_backbone_config(cls, backbone_config: PretrainedConfig, **kwargs): return cls(backbone_config=backbone_config, **kwargs)
    def to_dict(self):
        output = copy.deepcopy(self.__dict__)
        if output["backbone_config"] is not None: output["backbone_config"] = self.backbone_config.to_dict()
        output["model_type"] = self.__class__.model_type
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
