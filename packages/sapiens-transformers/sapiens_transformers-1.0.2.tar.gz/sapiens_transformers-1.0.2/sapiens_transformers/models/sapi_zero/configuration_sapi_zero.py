"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from ...modeling_rope_utils import rope_config_validation
class SAPIZeroConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "sapi_zero", ["past_key_values"]
    def __init__(self, vocab_size=64000, hidden_size=8192, intermediate_size=22016, num_hidden_layers=64, num_attention_heads=64, num_key_value_heads=None,
    hidden_act="tanh", max_position_embeddings=4096, initializer_range=0.04, rms_norm_eps=1e-7, use_cache=True, pad_token_id=None, bos_token_id=1,
    eos_token_id=2, tie_word_embeddings=False, rope_theta=20000.0, rope_scaling=None, attention_bias=False, attention_dropout=0.01, mlp_bias=False,
    embedding_multiplier=1.01, logits_scaling=1.01, residual_multiplier=1.01, attention_multiplier=1.01, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 64000
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 8192
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 22016
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 64
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 64
        if num_key_value_heads is None: num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act if type(hidden_act) == str else "tanh"
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 4096
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.04
        self.rms_norm_eps = rms_norm_eps if type(rms_norm_eps) in (int, float) else 1e-7
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.pad_token_id = pad_token_id
        self.bos_token_id = bos_token_id if type(bos_token_id) in (int, float) else 1
        self.eos_token_id = eos_token_id if type(eos_token_id) in (int, float) else 2
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 20000.0
        self.rope_scaling = rope_scaling
        self.attention_bias = attention_bias if type(attention_bias) in (bool, int, float) else False
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        self.mlp_bias = mlp_bias if type(mlp_bias) in (bool, int, float) else False
        self.embedding_multiplier = embedding_multiplier if type(embedding_multiplier) in (int, float) else 1.01
        self.logits_scaling = logits_scaling if type(logits_scaling) in (int, float) else 1.01
        self.residual_multiplier = residual_multiplier if type(residual_multiplier) in (int, float) else 1.01
        self.attention_multiplier = attention_multiplier if type(attention_multiplier) in (int, float) else 1.01
        super().__init__(pad_token_id=self.pad_token_id, bos_token_id=self.bos_token_id, eos_token_id=self.eos_token_id, tie_word_embeddings=self.tie_word_embeddings, **kwargs)
        rope_config_validation(self)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
