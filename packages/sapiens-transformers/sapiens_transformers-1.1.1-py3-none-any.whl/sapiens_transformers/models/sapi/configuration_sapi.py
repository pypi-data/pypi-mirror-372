"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
class SAPIConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "sapi", ["past_key_values"]
    def __init__(self, vocab_size=315000, hidden_size=7201, intermediate_size=35210, num_hidden_layers=64, num_attention_heads=52, head_dim=None, num_key_value_heads=None,
    hidden_act="silu", max_position_embeddings=2000000, initializer_range=0.0057, norm_eps=2e-7, use_cache=True, pad_token_id=None, bos_token_id=2, eos_token_id=3,
    tie_word_embeddings=False, rope_theta=20000.0, partial_rotary_factor=0.49, attention_bias=False, attention_dropout=0.01, mlp_bias=False, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 315000
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 7201
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 35210
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 64
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 52
        self.head_dim = head_dim if head_dim is not None else hidden_size // num_attention_heads
        self.num_key_value_heads = num_key_value_heads if type(num_key_value_heads) in (int, float) else None
        self.hidden_act = hidden_act if type(hidden_act) == str else 'silu'
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 2000000
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.0057
        self.norm_eps = norm_eps if type(norm_eps) in (int, float) else 2e-7
        self.use_cache = use_cache if type(use_cache) == bool else True
        self.pad_token_id = pad_token_id if type(pad_token_id) in (int, float) else None
        self.bos_token_id = bos_token_id if type(bos_token_id) in (int, float) else 2
        self.eos_token_id = eos_token_id if type(eos_token_id) in (int, float) else 3
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) == bool else False
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 20000.0
        self.partial_rotary_factor = partial_rotary_factor if type(partial_rotary_factor) in (int, float) else 0.49
        self.attention_bias = attention_bias if type(attention_bias) == bool else False
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        self.mlp_bias = mlp_bias if type(mlp_bias) == bool else False
        from ...modeling_rope_utils import rope_config_validation
        rope_config_validation(self)
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
