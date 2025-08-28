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
class JetMoeConfig(PretrainedConfig):
    model_type = "jetmoe"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=32000, hidden_size=2048, num_hidden_layers=12, num_key_value_heads=16, kv_channels=128, intermediate_size=5632, max_position_embeddings=4096,
    activation_function="silu", num_local_experts=8, num_experts_per_tok=2, output_router_logits=False, aux_loss_coef=0.01, use_cache=True, bos_token_id=1, eos_token_id=2,
    tie_word_embeddings=True, rope_theta=10000.0, rms_norm_eps=1e-6, initializer_range=0.01, attention_dropout=0.0, **kwargs):
        if num_experts_per_tok > num_local_experts: raise ValueError("`num_experts_per_tok` must be less than or equal to `num_local_experts`")
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_key_value_heads * num_experts_per_tok
        self.num_key_value_heads = num_key_value_heads
        self.kv_channels = kv_channels
        self.intermediate_size = intermediate_size
        self.max_position_embeddings = max_position_embeddings
        self.activation_function = activation_function
        self.num_local_experts = num_local_experts
        self.num_experts_per_tok = num_experts_per_tok
        self.output_router_logits = output_router_logits
        self.aux_loss_coef = aux_loss_coef
        self.use_cache = use_cache
        self.initializer_range = initializer_range
        self.attention_dropout = attention_dropout
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        self.rope_theta = rope_theta
        self.rms_norm_eps = rms_norm_eps
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
