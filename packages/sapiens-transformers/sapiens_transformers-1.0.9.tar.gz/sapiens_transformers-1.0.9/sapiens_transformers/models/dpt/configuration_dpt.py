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
from ..auto.configuration_auto import CONFIG_MAPPING
from ..bit import BitConfig
logger = logging.get_logger(__name__)
class DPTConfig(PretrainedConfig):
    model_type = "dpt"
    def __init__(self, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0,
    initializer_range=0.02, layer_norm_eps=1e-12, image_size=384, patch_size=16, num_channels=3, is_hybrid=False, qkv_bias=True, backbone_out_indices=[2, 5, 8, 11], readout_type="project",
    reassemble_factors=[4, 2, 1, 0.5], neck_hidden_sizes=[96, 192, 384, 768], fusion_hidden_size=256, head_in_index=-1, use_batch_norm_in_fusion_residual=False, use_bias_in_fusion_residual=None,
    add_projection=False, use_auxiliary_head=True, auxiliary_loss_weight=0.4, semantic_loss_ignore_index=255, semantic_classifier_dropout=0.1, backbone_featmap_shape=[1, 1024, 24, 24],
    neck_ignore_stages=[0, 1], backbone_config=None, backbone=None, use_pretrained_backbone=False, use_timm_backbone=False, backbone_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.is_hybrid = is_hybrid
        use_autobackbone = False
        if self.is_hybrid:
            if backbone_config is None: backbone_config = {'global_padding': 'same', 'layer_type': 'bottleneck', 'depths': [3, 4, 9], 'out_features': ['stage1', 'stage2', 'stage3'], 'embedding_dynamic_padding': True}
            if isinstance(backbone_config, dict):
                logger.info("Initializing the config with a `BiT` backbone.")
                backbone_config = BitConfig(**backbone_config)
            elif isinstance(backbone_config, PretrainedConfig): backbone_config = backbone_config
            else: raise ValueError(f"backbone_config must be a dictionary or a `PretrainedConfig`, got {backbone_config.__class__}.")
            self.backbone_config = backbone_config
            self.backbone_featmap_shape = backbone_featmap_shape
            self.neck_ignore_stages = neck_ignore_stages
            if readout_type != "project": raise ValueError("Readout type must be 'project' when using `DPT-hybrid` mode.")
        elif backbone is not None or backbone_config is not None:
            use_autobackbone = True
            if isinstance(backbone_config, dict):
                backbone_model_type = backbone_config.get("model_type")
                config_class = CONFIG_MAPPING[backbone_model_type]
                backbone_config = config_class.from_dict(backbone_config)
            self.backbone_config = backbone_config
            self.backbone_featmap_shape = None
            self.neck_ignore_stages = []
            verify_backbone_config_arguments(use_timm_backbone=use_timm_backbone, use_pretrained_backbone=use_pretrained_backbone, backbone=backbone, backbone_config=backbone_config, backbone_kwargs=backbone_kwargs)
        else:
            self.backbone_config = None
            self.backbone_featmap_shape = None
            self.neck_ignore_stages = []
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.backbone_kwargs = backbone_kwargs
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
        self.use_autobackbone = use_autobackbone
        self.backbone_out_indices = None if use_autobackbone else backbone_out_indices
        if readout_type not in ["ignore", "add", "project"]: raise ValueError("Readout_type must be one of ['ignore', 'add', 'project']")
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.readout_type = readout_type
        self.reassemble_factors = reassemble_factors
        self.neck_hidden_sizes = neck_hidden_sizes
        self.fusion_hidden_size = fusion_hidden_size
        self.head_in_index = head_in_index
        self.use_batch_norm_in_fusion_residual = use_batch_norm_in_fusion_residual
        self.use_bias_in_fusion_residual = use_bias_in_fusion_residual
        self.add_projection = add_projection
        self.use_auxiliary_head = use_auxiliary_head
        self.auxiliary_loss_weight = auxiliary_loss_weight
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
        self.semantic_classifier_dropout = semantic_classifier_dropout
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
