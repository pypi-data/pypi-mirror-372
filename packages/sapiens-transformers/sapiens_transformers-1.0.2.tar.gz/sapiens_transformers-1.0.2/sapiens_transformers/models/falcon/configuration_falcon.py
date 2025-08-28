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
class FalconConfig(PretrainedConfig):
    model_type = "falcon"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=65024, hidden_size=4544, num_hidden_layers=32, num_attention_heads=71, num_ln_in_parallel_attn=None, layer_norm_epsilon=1e-5, initializer_range=0.02,
    use_cache=True, hidden_dropout=0.0, attention_dropout=0.0, num_kv_heads=None, alibi=False, new_decoder_architecture=False, multi_query=True, parallel_attn=True,
    bias=False, max_position_embeddings=2048, rope_theta=10000.0, rope_scaling=None, bos_token_id=11, eos_token_id=11, ffn_hidden_size=None, activation="gelu", **kwargs):
        self.vocab_size = vocab_size
        n_embed = kwargs.pop("n_embed", None)
        self.hidden_size = hidden_size if n_embed is None else n_embed
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.use_cache = use_cache
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        self.num_kv_heads = num_attention_heads if num_kv_heads is None else num_kv_heads
        self.alibi = alibi
        self.new_decoder_architecture = new_decoder_architecture
        self.multi_query = multi_query
        self.parallel_attn = parallel_attn
        self.bias = bias
        self.num_ln_in_parallel_attn = num_ln_in_parallel_attn
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.activation = activation
        if ffn_hidden_size is None: self.ffn_hidden_size = hidden_size * 4
        else: self.ffn_hidden_size = ffn_hidden_size
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
    @property
    def head_dim(self): return self.hidden_size // self.num_attention_heads
    @property
    def rotary(self): return not self.alibi
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
