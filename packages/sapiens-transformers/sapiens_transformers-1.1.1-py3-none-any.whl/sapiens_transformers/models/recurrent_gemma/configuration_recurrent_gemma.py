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
class RecurrentGemmaConfig(PretrainedConfig):
    model_type = "recurrent_gemma"
    def __init__(self, num_hidden_layers=26, vocab_size=256000, hidden_size=2560, intermediate_size=3 * 2560, num_attention_heads=10, lru_width=None, attention_window_size=2048,
    conv1d_width=4, logits_soft_cap=30.0, rms_norm_eps=1e-6, use_cache=True, pad_token_id=0, eos_token_id=1, bos_token_id=2, hidden_activation="gelu_pytorch_tanh",
    partial_rotary_factor=0.5, rope_theta=10000.0, block_types=("recurrent", "recurrent", "attention"), attention_dropout=0.0, num_key_value_heads=None,
    attention_bias=False, w_init_variance_scale=0.01, **kwargs):
        self.num_hidden_layers = num_hidden_layers
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_attention_heads = num_attention_heads
        self.lru_width = lru_width if lru_width is not None else hidden_size
        self.attention_window_size = attention_window_size
        self.conv1d_width = conv1d_width
        self.logits_soft_cap = logits_soft_cap
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.partial_rotary_factor = partial_rotary_factor
        self.block_types = list(block_types)
        self.hidden_activation = hidden_activation
        self.head_dim = self.hidden_size // self.num_attention_heads
        self.num_key_value_heads = num_key_value_heads if num_key_value_heads is not None else num_attention_heads
        if self.num_key_value_heads > self.num_attention_heads: raise ValueError("The number of `num_key_value_heads` must be smaller than `num_attention_heads`")
        self.attention_dropout = attention_dropout
        self.attention_bias = attention_bias
        self.w_init_variance_scale = w_init_variance_scale
        self.final_w_init_variance_scale = 2.0 / self.num_hidden_layers
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
    @property
    def layers_block_type(self): return (self.block_types * 100)[: self.num_hidden_layers]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
