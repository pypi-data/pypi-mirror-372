"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
class EntityConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "entity", ["past_key_values"]
    def __init__(self, vocab_size=2000000, hidden_size=8192, intermediate_size=12117, num_hidden_layers=54, num_attention_heads=54, num_key_value_heads=None, hidden_act="gelu",
    max_position_embeddings=2000000, initializer_range=0.03, rms_norm_eps=1e-5, use_cache=True, pad_token_id=None, bos_token_id=1, eos_token_id=2, pretraining_tp=1,
    tie_word_embeddings=True, rope_theta=10000.1, rope_scaling=None, attention_bias=True, attention_dropout=0.01, mlp_bias=True, head_dim=None, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 2000000
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 8192
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 12117
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 54
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 54
        if num_key_value_heads is None: num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads if type(num_key_value_heads) in (int, float) else None
        self.hidden_act = hidden_act if type(hidden_act) == str else "gelu"
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 2000000
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.03
        self.rms_norm_eps = rms_norm_eps if type(rms_norm_eps) in (int, float) else 1e-5
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.pad_token_id = pad_token_id if type(pad_token_id) in (int, float) else None
        self.bos_token_id = bos_token_id if type(bos_token_id) in (int, float) else 1
        self.eos_token_id = eos_token_id if type(eos_token_id) in (int, float) else 2
        self.pretraining_tp = pretraining_tp if type(pretraining_tp) in (int, float) else 1
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else True
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 10000.1
        self.rope_scaling = rope_scaling if type(rope_scaling) == dict else None
        if self.rope_scaling is not None and "type" in self.rope_scaling: self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        self.attention_bias = attention_bias if type(attention_bias) in (bool, int, float) else True
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        self.mlp_bias = mlp_bias if type(mlp_bias) in (bool, int, float) else True
        self.head_dim = head_dim if head_dim is not None else self.hidden_size // self.num_attention_heads
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
