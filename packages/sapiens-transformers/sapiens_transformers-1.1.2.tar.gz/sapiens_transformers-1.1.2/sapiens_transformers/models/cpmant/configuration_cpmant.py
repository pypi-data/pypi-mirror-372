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
class CpmAntConfig(PretrainedConfig):
    model_type = "cpmant"
    def __init__(self, vocab_size: int = 30720, hidden_size: int = 4096, num_attention_heads: int = 32, dim_head: int = 128, dim_ff: int = 10240, num_hidden_layers: int = 48,
    dropout_p: int = 0.0, position_bias_num_buckets: int = 512, position_bias_max_distance: int = 2048, eps: int = 1e-6, init_std: float = 1.0, prompt_types: int = 32,
    prompt_length: int = 32, segment_types: int = 32, use_cache: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.prompt_types = prompt_types
        self.prompt_length = prompt_length
        self.segment_types = segment_types
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.dim_head = dim_head
        self.dim_ff = dim_ff
        self.num_hidden_layers = num_hidden_layers
        self.position_bias_num_buckets = position_bias_num_buckets
        self.position_bias_max_distance = position_bias_max_distance
        self.dropout_p = dropout_p
        self.eps = eps
        self.use_cache = use_cache
        self.vocab_size = vocab_size
        self.init_std = init_std
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
