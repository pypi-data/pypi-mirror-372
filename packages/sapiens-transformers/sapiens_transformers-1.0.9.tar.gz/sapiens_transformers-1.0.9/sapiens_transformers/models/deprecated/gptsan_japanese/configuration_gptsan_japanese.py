"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class GPTSanJapaneseConfig(PretrainedConfig):
    model_type = "gptsan-japanese"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'num_heads', 'num_hidden_layers': 'num_layers'}
    def __init__(self, vocab_size=36000, max_position_embeddings=1280, d_model=1024, d_ff=8192, d_ext=4096, d_spout=128, num_switch_layers=10, num_ext_layers=0,
    num_heads=16, num_experts=16, expert_capacity=128, dropout_rate=0.0, layer_norm_epsilon=1e-5, router_bias=False, router_jitter_noise=0.0, router_dtype="float32",
    router_ignore_padding_tokens=False, output_hidden_states=False, output_attentions=False, initializer_factor=0.002, output_router_logits=False, use_cache=True,
    separator_token_id=35998, pad_token_id=35995, eos_token_id=35999, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.d_ff = d_ff
        self.d_ext = d_ext
        self.d_spout = d_spout
        self.num_switch_layers = num_switch_layers
        self.num_ext_layers = num_ext_layers
        self.num_layers = num_switch_layers + num_ext_layers
        self.num_heads = num_heads
        self.num_experts = num_experts
        self.expert_capacity = expert_capacity
        self.dropout_rate = dropout_rate
        self.layer_norm_epsilon = layer_norm_epsilon
        self.router_bias = router_bias
        self.router_jitter_noise = router_jitter_noise
        self.router_dtype = router_dtype
        self.router_ignore_padding_tokens = router_ignore_padding_tokens
        self.output_hidden_states = output_hidden_states
        self.output_attentions = output_attentions
        self.initializer_factor = initializer_factor
        self.output_router_logits = output_router_logits
        self.use_cache = use_cache
        super().__init__(separator_token_id=separator_token_id, pad_token_id=pad_token_id, eos_token_id=eos_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
