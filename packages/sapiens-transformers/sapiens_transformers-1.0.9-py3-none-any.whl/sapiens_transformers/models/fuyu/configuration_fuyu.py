"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class FuyuConfig(PretrainedConfig):
    model_type = "fuyu"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=262144, hidden_size=4096, intermediate_size=16384, num_hidden_layers=36, num_attention_heads=64, hidden_act="relu2", max_position_embeddings=16384,
    image_size=300, patch_size=30, num_channels=3, initializer_range=0.02, layer_norm_eps=1e-5, use_cache=True, tie_word_embeddings=False, rope_theta=25000.0, rope_scaling=None,
    qk_layernorm=True, hidden_dropout=0.0, attention_dropout=0.0, partial_rotary_factor=0.5, pad_token_id=None, bos_token_id=1, eos_token_id=2, text_config=None, **kwargs):
        if text_config is None:
            text_config = {"vocab_size": vocab_size, "max_position_embeddings": max_position_embeddings, "hidden_size": hidden_size, "intermediate_size": intermediate_size,
            "num_hidden_layers": num_hidden_layers, "num_attention_heads": num_attention_heads, "hidden_act": hidden_act, "initializer_range": initializer_range,
            "layer_norm_eps": layer_norm_eps, "use_cache": use_cache, "rope_theta": rope_theta, "rope_scaling": rope_scaling, "qk_layernorm": qk_layernorm,
            "hidden_dropout": hidden_dropout, "attention_dropout": attention_dropout, "partial_rotary_factor": partial_rotary_factor, "pad_token_id": pad_token_id,
            "bos_token_id": bos_token_id, "eos_token_id": eos_token_id, "tie_word_embeddings": tie_word_embeddings}
            logger.info("text_config is None. initializing the text model with default values.")
        text_model_type = text_config["model_type"] if "model_type" in text_config else "persimmon"
        self.text_config = CONFIG_MAPPING[text_model_type](**text_config)
        self._vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.qk_layernorm = qk_layernorm
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.partial_rotary_factor = partial_rotary_factor
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
