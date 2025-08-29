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
class OpenLlamaConfig(PretrainedConfig):
    model_type = "open-llama"
    def __init__(self, vocab_size=100000, hidden_size=4096, intermediate_size=11008, num_hidden_layers=32, num_attention_heads=32, hidden_act="silu", max_position_embeddings=2048,
    initializer_range=0.02, rms_norm_eps=1e-6, use_cache=True, pad_token_id=0, bos_token_id=1, eos_token_id=2, tie_word_embeddings=False, use_memory_efficient_attention=True,
    hidden_dropout_prob=0.1, attention_dropout_prob=0.1, use_stable_embedding=True, shared_input_output_embedding=True, rope_theta=10000.0, rope_scaling=None, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.use_memory_efficient_attention = kwargs.pop("use_memorry_efficient_attention", use_memory_efficient_attention)
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_dropout_prob = attention_dropout_prob
        self.use_stable_embedding = use_stable_embedding
        self.shared_input_output_embedding = shared_input_output_embedding
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self._rope_scaling_validation()
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
    def _rope_scaling_validation(self):
        if self.rope_scaling is None: return
        if not isinstance(self.rope_scaling, dict) or len(self.rope_scaling) != 2: raise ValueError("`rope_scaling` must be a dictionary with two fields, `type` and `factor`, " f"got {self.rope_scaling}")
        rope_scaling_type = self.rope_scaling.get("type", None)
        rope_scaling_factor = self.rope_scaling.get("factor", None)
        if rope_scaling_type is None or rope_scaling_type not in ["linear", "dynamic"]: raise ValueError(f"`rope_scaling`'s type field must be one of ['linear', 'dynamic'], got {rope_scaling_type}")
        if rope_scaling_factor is None or not isinstance(rope_scaling_factor, float) or rope_scaling_factor <= 1.0: raise ValueError(f"`rope_scaling`'s factor field must be a float > 1, got {rope_scaling_factor}")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
