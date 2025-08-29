"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from collections import OrderedDict
from typing import Mapping
from packaging import version
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils.backbone_utils import BackboneConfigMixin, get_aligned_output_features_output_indices
class BeitConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "beit"
    def __init__(self, vocab_size=8192, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.0,
    attention_probs_dropout_prob=0.0, initializer_range=0.02, layer_norm_eps=1e-12, image_size=224, patch_size=16, num_channels=3, use_mask_token=False, use_absolute_position_embeddings=False,
    use_relative_position_bias=False, use_shared_relative_position_bias=False, layer_scale_init_value=0.1, drop_path_rate=0.1, use_mean_pooling=True, pool_scales=[1, 2, 3, 6],
    use_auxiliary_head=True, auxiliary_loss_weight=0.4, auxiliary_channels=256, auxiliary_num_convs=1, auxiliary_concat_input=False, semantic_loss_ignore_index=255, out_features=None,
    out_indices=None, add_fpn=False, reshape_hidden_states=True, **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
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
        self.use_mask_token = use_mask_token
        self.use_absolute_position_embeddings = use_absolute_position_embeddings
        self.use_relative_position_bias = use_relative_position_bias
        self.use_shared_relative_position_bias = use_shared_relative_position_bias
        self.layer_scale_init_value = layer_scale_init_value
        self.drop_path_rate = drop_path_rate
        self.use_mean_pooling = use_mean_pooling
        self.pool_scales = pool_scales
        self.use_auxiliary_head = use_auxiliary_head
        self.auxiliary_loss_weight = auxiliary_loss_weight
        self.auxiliary_channels = auxiliary_channels
        self.auxiliary_num_convs = auxiliary_num_convs
        self.auxiliary_concat_input = auxiliary_concat_input
        self.semantic_loss_ignore_index = semantic_loss_ignore_index
        if "segmentation_indices" in kwargs:
            warnings.warn("The `segmentation_indices` argument is deprecated and will be removed in a future version, use `out_indices` instead.", FutureWarning)
            out_indices = kwargs.pop("segmentation_indices")
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, self.num_hidden_layers + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(out_features=out_features, out_indices=out_indices, stage_names=self.stage_names)
        self.add_fpn = add_fpn
        self.reshape_hidden_states = reshape_hidden_states
class BeitOnnxConfig(OnnxConfig):
    torch_onnx_minimum_version = version.parse("1.11")
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"})])
    @property
    def atol_for_validation(self) -> float: return 1e-4
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
