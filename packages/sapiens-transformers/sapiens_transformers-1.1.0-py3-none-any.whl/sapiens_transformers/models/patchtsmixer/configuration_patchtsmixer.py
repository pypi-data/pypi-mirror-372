"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class PatchTSMixerConfig(PretrainedConfig):
    model_type = "patchtsmixer"
    attribute_map = {'hidden_size': 'd_model', 'num_hidden_layers': 'num_layers'}
    def __init__(self, context_length: int = 32, patch_length: int = 8, num_input_channels: int = 1, patch_stride: int = 8, num_parallel_samples: int = 100, d_model: int = 8,
    expansion_factor: int = 2, num_layers: int = 3, dropout: float = 0.2, mode: str = "common_channel", gated_attn: bool = True, norm_mlp: str = "LayerNorm", self_attn: bool = False,
    self_attn_heads: int = 1, use_positional_encoding: bool = False, positional_encoding_type: str = "sincos", scaling: Optional[Union[str, bool]] = "std", loss: str = "mse",
    init_std: float = 0.02, post_init: bool = False, norm_eps: float = 1e-5, mask_type: str = "random", random_mask_ratio: float = 0.5, num_forecast_mask_patches: Optional[Union[List[int], int]] = [2],
    mask_value: int = 0, masked_loss: bool = True, channel_consistent_masking: bool = True, unmasked_channel_indices: Optional[List[int]] = None, head_dropout: float = 0.2,
    distribution_output: str = "student_t", prediction_length: int = 16, prediction_channel_indices: list = None, num_targets: int = 3, output_range: list = None,
    head_aggregation: str = "max_pool", **kwargs):
        self.num_input_channels = num_input_channels
        self.context_length = context_length
        self.patch_length = patch_length
        self.patch_stride = patch_stride
        self.d_model = d_model
        self.expansion_factor = expansion_factor
        self.num_layers = num_layers
        self.dropout = dropout
        self.mode = mode
        self.gated_attn = gated_attn
        self.norm_mlp = norm_mlp
        self.scaling = scaling
        self.head_dropout = head_dropout
        self.num_patches = (max(context_length, patch_length) - patch_length) // patch_stride + 1
        self.mask_type = mask_type
        self.random_mask_ratio = random_mask_ratio
        self.num_forecast_mask_patches = num_forecast_mask_patches
        self.mask_value = mask_value
        self.channel_consistent_masking = channel_consistent_masking
        self.masked_loss = masked_loss
        self.patch_last = True
        self.use_positional_encoding = use_positional_encoding
        self.positional_encoding_type = positional_encoding_type
        self.prediction_length = prediction_length
        self.prediction_channel_indices = prediction_channel_indices
        self.num_targets = num_targets
        self.output_range = output_range
        self.head_aggregation = head_aggregation
        self.self_attn = self_attn
        self.self_attn_heads = self_attn_heads
        self.init_std = init_std
        self.post_init = post_init
        self.distribution_output = distribution_output
        self.loss = loss
        self.num_parallel_samples = num_parallel_samples
        self.unmasked_channel_indices = unmasked_channel_indices
        self.norm_eps = norm_eps
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
