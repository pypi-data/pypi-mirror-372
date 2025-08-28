"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class DbrxAttentionConfig(PretrainedConfig):
    def __init__(self, attn_pdrop: float = 0.0, clip_qkv: Optional[float] = None, kv_n_heads: int = 1, rope_theta: float = 10000.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.attn_pdrop = attn_pdrop
        self.clip_qkv = clip_qkv
        self.kv_n_heads = kv_n_heads
        self.rope_theta = rope_theta
        for k in ["model_type"]:
            if k in kwargs: kwargs.pop(k)
        if len(kwargs) != 0: raise ValueError(f"Found unknown {kwargs=}")
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str, **kwargs: Any) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "dbrx": config_dict = config_dict["attn_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type " + f"{cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class DbrxFFNConfig(PretrainedConfig):
    def __init__(self, ffn_act_fn: dict = None, ffn_hidden_size: int = 3584, moe_num_experts: int = 4, moe_top_k: int = 1, moe_jitter_eps: Optional[float] = None,
    moe_loss_weight: float = 0.01, moe_normalize_expert_weights: Optional[float] = 1.0, **kwargs: Any):
        super().__init__()
        if ffn_act_fn is None: ffn_act_fn = {"name": "silu"}
        self.ffn_act_fn = ffn_act_fn
        self.ffn_hidden_size = ffn_hidden_size
        self.moe_num_experts = moe_num_experts
        self.moe_top_k = moe_top_k
        self.moe_jitter_eps = moe_jitter_eps
        self.moe_loss_weight = moe_loss_weight
        self.moe_normalize_expert_weights = moe_normalize_expert_weights
        for k in ["model_type"]:
            if k in kwargs: kwargs.pop(k)
        if len(kwargs) != 0: raise ValueError(f"Found unknown {kwargs=}")
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str, **kwargs: Any) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "dbrx": config_dict = config_dict["ffn_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type " + f"{cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class DbrxConfig(PretrainedConfig):
    model_type = "dbrx"
    attribute_map = {'num_attention_heads': 'n_heads', 'hidden_size': 'd_model', 'num_hidden_layers': 'n_layers', 'max_position_embeddings': 'max_seq_len'}
    def __init__(self, d_model: int = 2048, n_heads: int = 16, n_layers: int = 24, max_seq_len: int = 2048, vocab_size: int = 32000, resid_pdrop: float = 0.0, emb_pdrop: float = 0.0,
    attn_config: Optional[DbrxAttentionConfig] = None, ffn_config: Optional[DbrxFFNConfig] = None, use_cache: bool = True, initializer_range: float = 0.02,
    output_router_logits: bool = False, **kwargs: Any):
        if attn_config is None: self.attn_config = DbrxAttentionConfig()
        elif isinstance(attn_config, dict): self.attn_config = DbrxAttentionConfig(**attn_config)
        else: self.attn_config = attn_config
        if ffn_config is None: self.ffn_config = DbrxFFNConfig()
        elif isinstance(ffn_config, dict): self.ffn_config = DbrxFFNConfig(**ffn_config)
        else: self.ffn_config = ffn_config
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.max_seq_len = max_seq_len
        self.vocab_size = vocab_size
        self.resid_pdrop = resid_pdrop
        self.emb_pdrop = emb_pdrop
        self.use_cache = use_cache
        self.initializer_range = initializer_range
        self.output_router_logits = output_router_logits
        self.num_key_value_heads = self.attn_config.kv_n_heads
        tie_word_embeddings = kwargs.pop("tie_word_embeddings", False)
        if tie_word_embeddings: raise ValueError("tie_word_embeddings is not supported for DBRX models.")
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
