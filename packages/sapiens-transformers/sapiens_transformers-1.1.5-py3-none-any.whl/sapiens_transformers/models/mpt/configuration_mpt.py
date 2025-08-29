"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING: pass
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class MptAttentionConfig(PretrainedConfig):
    def __init__(self, attn_type="multihead_attention", attn_pdrop=0, attn_impl="torch", clip_qkv=None, softmax_scale=None, prefix_lm=False, qk_ln=False,
    attn_uses_sequence_id=False, alibi=True, alibi_bias_max=8, **kwargs):
        super().__init__()
        self.attn_type = attn_type
        self.attn_pdrop = attn_pdrop
        self.attn_impl = attn_impl
        self.clip_qkv = clip_qkv
        self.softmax_scale = softmax_scale
        self.prefix_lm = prefix_lm
        self.attn_uses_sequence_id = attn_uses_sequence_id
        self.alibi = alibi
        self.qk_ln = qk_ln
        self.alibi_bias_max = alibi_bias_max
        if attn_type not in ["multihead_attention", "multiquery_attention"]: raise ValueError(f"`attn_type` has to be either `multihead_attention` or `multiquery_attention`. Received: {attn_type}")
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "mpt": config_dict = config_dict["attn_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class MptConfig(PretrainedConfig):
    model_type = "mpt"
    attribute_map = {'num_attention_heads': 'n_heads', 'hidden_size': 'd_model', 'num_hidden_layers': 'n_layers'}
    def __init__(self, d_model: int = 2048, n_heads: int = 16, n_layers: int = 24, expansion_ratio: int = 4, max_seq_len: int = 2048, vocab_size: int = 50368,
    resid_pdrop: float = 0.0, layer_norm_epsilon: float = 1e-5, emb_pdrop: float = 0.0, learned_pos_emb: bool = True, attn_config: MptAttentionConfig = None,
    init_device: str = "cpu", logit_scale: Optional[Union[float, str]] = None, no_bias: bool = True, verbose: int = 0, embedding_fraction: float = 1.0,
    norm_type: str = "low_precision_layernorm", use_cache: bool = False, initializer_range=0.02, **kwargs):
        if attn_config is None: self.attn_config = MptAttentionConfig()
        elif isinstance(attn_config, dict): self.attn_config = MptAttentionConfig(**attn_config)
        else: self.attn_config = attn_config
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.expansion_ratio = expansion_ratio
        self.max_seq_len = max_seq_len
        self.vocab_size = vocab_size
        self.resid_pdrop = resid_pdrop
        self.emb_pdrop = emb_pdrop
        self.learned_pos_emb = learned_pos_emb
        self.init_device = init_device
        self.logit_scale = logit_scale
        self.no_bias = no_bias
        self.verbose = verbose
        self.embedding_fraction = embedding_fraction
        self.norm_type = norm_type
        self.layer_norm_epsilon = layer_norm_epsilon
        self.use_cache = use_cache
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
