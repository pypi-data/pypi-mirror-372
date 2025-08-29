"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...modeling_rope_utils import rope_config_validation
from ...utils import logging
logger = logging.get_logger(__name__)
class StableLmConfig(PretrainedConfig):
    model_type = "stablelm"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=50304, intermediate_size=6912, hidden_size=2560, num_hidden_layers=32, num_attention_heads=32, num_key_value_heads=32,
    hidden_act="silu", max_position_embeddings=4096, initializer_range=0.02, layer_norm_eps=1.0e-5, use_cache=True, tie_word_embeddings=False,
    rope_theta=10_000, rope_scaling=None, use_qkv_bias=False, qk_layernorm=False, use_parallel_residual=False, hidden_dropout=0.0, attention_dropout=0.0,
    partial_rotary_factor=0.25, bos_token_id=0, eos_token_id=0, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.use_qkv_bias = use_qkv_bias
        self.qk_layernorm = qk_layernorm
        self.use_parallel_residual = use_parallel_residual
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.partial_rotary_factor = partial_rotary_factor
        if self.rope_scaling is not None and "type" in self.rope_scaling: self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        rope_config_validation(self)
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
