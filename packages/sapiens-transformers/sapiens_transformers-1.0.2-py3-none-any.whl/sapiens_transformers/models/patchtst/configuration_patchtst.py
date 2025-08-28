"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
from sapiens_transformers.configuration_utils import PretrainedConfig
from sapiens_transformers.utils import logging
logger = logging.get_logger(__name__)
class PatchTSTConfig(PretrainedConfig):
    model_type = "patchtst"
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'num_attention_heads', 'num_hidden_layers': 'num_hidden_layers'}
    def __init__(self, num_input_channels: int = 1, context_length: int = 32, distribution_output: str = "student_t", loss: str = "mse", patch_length: int = 1,
    patch_stride: int = 1, num_hidden_layers: int = 3, d_model: int = 128, num_attention_heads: int = 4, share_embedding: bool = True, channel_attention: bool = False,
    ffn_dim: int = 512, norm_type: str = "batchnorm", norm_eps: float = 1e-05, attention_dropout: float = 0.0, positional_dropout: float = 0.0, path_dropout: float = 0.0,
    ff_dropout: float = 0.0, bias: bool = True, activation_function: str = "gelu", pre_norm: bool = True, positional_encoding_type: str = "sincos", use_cls_token: bool = False,
    init_std: float = 0.02, share_projection: bool = True, scaling: Optional[Union[str, bool]] = "std", do_mask_input: Optional[bool] = None, mask_type: str = "random",
    random_mask_ratio: float = 0.5, num_forecast_mask_patches: Optional[Union[List[int], int]] = [2], channel_consistent_masking: Optional[bool] = False,
    unmasked_channel_indices: Optional[List[int]] = None, mask_value: int = 0, pooling_type: str = "mean", head_dropout: float = 0.0, prediction_length: int = 24,
    num_targets: int = 1, output_range: Optional[List] = None, num_parallel_samples: int = 100, **kwargs):
        self.context_length = context_length
        self.num_input_channels = num_input_channels
        self.loss = loss
        self.distribution_output = distribution_output
        self.num_parallel_samples = num_parallel_samples
        self.d_model = d_model
        self.num_attention_heads = num_attention_heads
        self.ffn_dim = ffn_dim
        self.num_hidden_layers = num_hidden_layers
        self.attention_dropout = attention_dropout
        self.share_embedding = share_embedding
        self.channel_attention = channel_attention
        self.norm_type = norm_type
        self.norm_eps = norm_eps
        self.positional_dropout = positional_dropout
        self.path_dropout = path_dropout
        self.ff_dropout = ff_dropout
        self.bias = bias
        self.activation_function = activation_function
        self.pre_norm = pre_norm
        self.positional_encoding_type = positional_encoding_type
        self.use_cls_token = use_cls_token
        self.init_std = init_std
        self.scaling = scaling
        self.patch_length = patch_length
        self.patch_stride = patch_stride
        self.do_mask_input = do_mask_input
        self.mask_type = mask_type
        self.random_mask_ratio = random_mask_ratio
        self.num_forecast_mask_patches = num_forecast_mask_patches
        self.channel_consistent_masking = channel_consistent_masking
        self.unmasked_channel_indices = unmasked_channel_indices
        self.mask_value = mask_value
        self.pooling_type = pooling_type
        self.head_dropout = head_dropout
        self.share_projection = share_projection
        self.prediction_length = prediction_length
        self.num_parallel_samples = num_parallel_samples
        self.num_targets = num_targets
        self.output_range = output_range
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
