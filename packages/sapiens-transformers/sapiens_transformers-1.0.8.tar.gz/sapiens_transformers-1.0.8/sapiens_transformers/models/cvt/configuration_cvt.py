"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class CvtConfig(PretrainedConfig):
    model_type = "cvt"
    def __init__(self, num_channels=3, patch_sizes=[7, 3, 3], patch_stride=[4, 2, 2], patch_padding=[2, 1, 1], embed_dim=[64, 192, 384], num_heads=[1, 3, 6],
    depth=[1, 2, 10], mlp_ratio=[4.0, 4.0, 4.0], attention_drop_rate=[0.0, 0.0, 0.0], drop_rate=[0.0, 0.0, 0.0], drop_path_rate=[0.0, 0.0, 0.1], qkv_bias=[True, True, True],
    cls_token=[False, False, True], qkv_projection_method=["dw_bn", "dw_bn", "dw_bn"], kernel_qkv=[3, 3, 3], padding_kv=[1, 1, 1], stride_kv=[2, 2, 2], padding_q=[1, 1, 1],
    stride_q=[1, 1, 1], initializer_range=0.02, layer_norm_eps=1e-12, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.patch_sizes = patch_sizes
        self.patch_stride = patch_stride
        self.patch_padding = patch_padding
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.depth = depth
        self.mlp_ratio = mlp_ratio
        self.attention_drop_rate = attention_drop_rate
        self.drop_rate = drop_rate
        self.drop_path_rate = drop_path_rate
        self.qkv_bias = qkv_bias
        self.cls_token = cls_token
        self.qkv_projection_method = qkv_projection_method
        self.kernel_qkv = kernel_qkv
        self.padding_kv = padding_kv
        self.stride_kv = stride_kv
        self.padding_q = padding_q
        self.stride_q = stride_q
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
