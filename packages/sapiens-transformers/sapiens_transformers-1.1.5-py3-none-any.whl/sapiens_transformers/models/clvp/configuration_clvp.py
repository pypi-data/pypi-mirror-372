"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING: pass
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class ClvpEncoderConfig(PretrainedConfig):
    model_type = "clvp_encoder"
    def __init__(self, vocab_size=256, hidden_size=768, intermediate_size=1536, projection_dim=768, num_hidden_layers=20, num_attention_heads=12, hidden_act="gelu", layer_norm_eps=1e-5,
    attention_dropout=0.1, dropout=0.1, use_rotary_embedding=True, use_attention_bias=False, summary_type="mean", initializer_factor=1.0, bos_token_id=255, eos_token_id=0, **kwargs):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.projection_dim = projection_dim
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
        self.initializer_factor = initializer_factor
        self.attention_dropout = attention_dropout
        self.dropout = dropout
        self.use_rotary_embedding = use_rotary_embedding
        self.use_attention_bias = use_attention_bias
        self.summary_type = summary_type
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], config_type: str = "text_config", **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_type not in ["text_config", "speech_config"]: raise ValueError(f"We can only load either 'text_config' or 'speech_config' but you are trying to load" f"{config_type}")
        if config_dict.get("model_type") == "clvp": config_dict = config_dict[config_type]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class ClvpDecoderConfig(PretrainedConfig):
    model_type = "clvp_decoder"
    def __init__(self, vocab_size=8194, max_position_embeddings=608, max_text_tokens=404, hidden_size=1024, num_hidden_layers=30, num_attention_heads=16, n_inner=None,
    num_mel_attn_blocks=6, activation_function="gelu_new", resid_pdrop=0.1, embd_pdrop=0.1, attention_dropout=0.1, layer_norm_epsilon=1e-5, initializer_range=0.02, summary_type="cls_index",
    summary_use_proj=True, summary_activation=None, summary_proj_to_labels=True, summary_first_dropout=0.1, use_cache=True, bos_token_id=8192, eos_token_id=8193, feature_size=80,
    use_attention_bias=True, initializer_factor=1.0, decoder_fixing_codes=[83, 45, 45, 248], **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.max_text_tokens = max_text_tokens
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.n_inner = n_inner
        self.num_mel_attn_blocks = num_mel_attn_blocks
        self.activation_function = activation_function
        self.resid_pdrop = resid_pdrop
        self.embd_pdrop = embd_pdrop
        self.attention_dropout = attention_dropout
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.summary_type = summary_type
        self.summary_use_proj = summary_use_proj
        self.summary_activation = summary_activation
        self.summary_first_dropout = summary_first_dropout
        self.summary_proj_to_labels = summary_proj_to_labels
        self.use_cache = use_cache
        self.feature_size = feature_size
        self.use_attention_bias = use_attention_bias
        self.initializer_factor = initializer_factor
        self.decoder_fixing_codes = decoder_fixing_codes
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "clvp": config_dict = config_dict["decoder_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class ClvpConfig(PretrainedConfig):
    model_type = "clvp"
    is_composition = True
    def __init__(self, text_config=None, speech_config=None, decoder_config=None, projection_dim=768, logit_scale_init_value=2.6592, initializer_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `ClvpEncoderConfig` with default values.")
        if speech_config is None:
            speech_config = {}
            logger.info("`speech_config` is `None`. initializing the `ClvpEncoderConfig` with default values.")
        if decoder_config is None:
            decoder_config = {}
            logger.info("`decoder_config` is `None`. initializing the `ClvpDecoderConfig` with default values.")
        self.text_config = ClvpEncoderConfig(**text_config)
        self.speech_config = ClvpEncoderConfig(**speech_config)
        self.decoder_config = ClvpDecoderConfig(**decoder_config)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.initializer_factor = initializer_factor
    @classmethod
    def from_sub_model_configs(cls, text_config: ClvpEncoderConfig, speech_config: ClvpEncoderConfig, decoder_config: ClvpDecoderConfig, **kwargs): return cls(text_config=text_config.to_dict(), speech_config=speech_config.to_dict(), decoder_config=decoder_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
