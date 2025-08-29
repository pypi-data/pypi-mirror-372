"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto.configuration_auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
ZOEDEPTH_PRETRAINED_CONFIG_ARCHIVE_MAP = {'Intel/zoedepth-nyu': 'https://huggingface.co/Intel/zoedepth-nyu/resolve/main/config.json'}
class ZoeDepthConfig(PretrainedConfig):
    model_type = "zoedepth"
    def __init__(self, backbone_config=None, backbone=None, use_pretrained_backbone=False, backbone_kwargs=None, hidden_act="gelu", initializer_range=0.02, batch_norm_eps=1e-05,
    readout_type="project", reassemble_factors=[4, 2, 1, 0.5], neck_hidden_sizes=[96, 192, 384, 768], fusion_hidden_size=256, head_in_index=-1, use_batch_norm_in_fusion_residual=False,
    use_bias_in_fusion_residual=None, num_relative_features=32, add_projection=False, bottleneck_features=256, num_attractors=[16, 8, 4, 1], bin_embedding_dim=128,
    attractor_alpha=1000, attractor_gamma=2, attractor_kind="mean", min_temp=0.0212, max_temp=50.0, bin_centers_type="softplus", bin_configurations=[{"n_bins": 64, "min_depth": 0.001, "max_depth": 10.0}],
    num_patch_transformer_layers=None, patch_transformer_hidden_size=None, patch_transformer_intermediate_size=None, patch_transformer_num_attention_heads=None, **kwargs):
        super().__init__(**kwargs)
        if readout_type not in ["ignore", "add", "project"]: raise ValueError("Readout_type must be one of ['ignore', 'add', 'project']")
        if attractor_kind not in ["mean", "sum"]: raise ValueError("Attractor_kind must be one of ['mean', 'sum']")
        if use_pretrained_backbone: raise ValueError("Pretrained backbones are not supported yet.")
        if backbone_config is not None and backbone is not None: raise ValueError("You can't specify both `backbone` and `backbone_config`.")
        if backbone_config is None and backbone is None:
            logger.info("`backbone_config` is `None`. Initializing the config with the default `BEiT` backbone.")
            backbone_config = CONFIG_MAPPING["beit"](image_size=384, num_hidden_layers=24, hidden_size=1024, intermediate_size=4096, num_attention_heads=16, use_relative_position_bias=True,
            reshape_hidden_states=False, out_features=["stage6", "stage12", "stage18", "stage24"])
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.get("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        if backbone_kwargs is not None and backbone_kwargs and backbone_config is not None: raise ValueError("You can't specify both `backbone_kwargs` and `backbone_config`.")
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.hidden_act = hidden_act
        self.use_pretrained_backbone = use_pretrained_backbone
        self.initializer_range = initializer_range
        self.batch_norm_eps = batch_norm_eps
        self.readout_type = readout_type
        self.reassemble_factors = reassemble_factors
        self.neck_hidden_sizes = neck_hidden_sizes
        self.fusion_hidden_size = fusion_hidden_size
        self.head_in_index = head_in_index
        self.use_batch_norm_in_fusion_residual = use_batch_norm_in_fusion_residual
        self.use_bias_in_fusion_residual = use_bias_in_fusion_residual
        self.num_relative_features = num_relative_features
        self.add_projection = add_projection
        self.bottleneck_features = bottleneck_features
        self.num_attractors = num_attractors
        self.bin_embedding_dim = bin_embedding_dim
        self.attractor_alpha = attractor_alpha
        self.attractor_gamma = attractor_gamma
        self.attractor_kind = attractor_kind
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.bin_centers_type = bin_centers_type
        self.bin_configurations = bin_configurations
        self.num_patch_transformer_layers = num_patch_transformer_layers
        self.patch_transformer_hidden_size = patch_transformer_hidden_size
        self.patch_transformer_intermediate_size = patch_transformer_intermediate_size
        self.patch_transformer_num_attention_heads = patch_transformer_num_attention_heads
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
