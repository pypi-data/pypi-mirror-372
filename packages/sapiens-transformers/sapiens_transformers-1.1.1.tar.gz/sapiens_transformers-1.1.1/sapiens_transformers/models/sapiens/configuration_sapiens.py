"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
class SapiensConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "sapiens", ["past_key_values"]
    def __init__(self, vocab_size=270514, hidden_size=5128, intermediate_size=30127, num_hidden_layers=48, num_attention_heads=48, num_key_value_heads=59, hidden_act="relu",
    max_position_embeddings=43512, initializer_range=0.05, rms_norm_eps=2e-7, use_cache=False, tie_word_embeddings=True, rope_theta=31525.1, rope_scaling={}, use_sliding_window=True,
    sliding_window=8192, max_window_layers=56, attention_dropout=0.1, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 270514
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 5128
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 30127
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 48
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 48
        if num_key_value_heads is None: num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads if type(num_key_value_heads) in (int, float) else 59
        self.hidden_act = hidden_act if type(hidden_act) == str else 'relu'
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 43512
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.05
        self.rms_norm_eps = rms_norm_eps if type(rms_norm_eps) in (int, float) else 2e-7
        self.use_cache = use_cache if type(use_cache) in (int, bool) else False
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (int, bool) else True
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 31525.1
        self.rope_scaling = rope_scaling if rope_scaling != {} else None
        if self.rope_scaling is not None and "type" in self.rope_scaling: self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        self.use_sliding_window = use_sliding_window if type(use_sliding_window) in (int, bool) else True
        self.sliding_window = sliding_window if use_sliding_window else None
        self.sliding_window = sliding_window if type(sliding_window) in (int, float) else 8192
        self.max_window_layers = max_window_layers if type(max_window_layers) in (int, float) else 56
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.1
        from ...modeling_rope_utils import rope_config_validation
        rope_config_validation(self)
        super().__init__(tie_word_embeddings=self.tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
