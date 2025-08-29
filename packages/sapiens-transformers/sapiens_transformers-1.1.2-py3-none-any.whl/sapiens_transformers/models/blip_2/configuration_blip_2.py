"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Optional, Union
from ...configuration_utils import PretrainedConfig
from ...models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class Blip2VisionConfig(PretrainedConfig):
    model_type = "blip_2_vision_model"
    def __init__(self, hidden_size=1408, intermediate_size=6144, num_hidden_layers=39, num_attention_heads=16, image_size=224, patch_size=14, hidden_act="gelu",
    layer_norm_eps=1e-6, attention_dropout=0.0, initializer_range=1e-10, qkv_bias=True, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.patch_size = patch_size
        self.image_size = image_size
        self.initializer_range = initializer_range
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
        self.qkv_bias = qkv_bias
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "blip-2": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Blip2QFormerConfig(PretrainedConfig):
    model_type = "blip_2_qformer"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, initializer_range=0.02, layer_norm_eps=1e-12, pad_token_id=0, position_embedding_type="absolute",
    cross_attention_frequency=2, encoder_hidden_size=1408, use_qformer_text_input=False, **kwargs):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.cross_attention_frequency = cross_attention_frequency
        self.encoder_hidden_size = encoder_hidden_size
        self.use_qformer_text_input = use_qformer_text_input
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "blip-2": config_dict = config_dict["qformer_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Blip2Config(PretrainedConfig):
    model_type = "blip-2"
    def __init__(self, vision_config=None, qformer_config=None, text_config=None, num_query_tokens=32, image_text_hidden_size=256, image_token_index=None, **kwargs):
        super().__init__(**kwargs)
        if vision_config is None:
            vision_config = {}
            logger.info("vision_config is None. initializing the Blip2VisionConfig with default values.")
        if qformer_config is None:
            qformer_config = {}
            logger.info("qformer_config is None. Initializing the Blip2QFormerConfig with default values.")
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the text config with default values (`OPTConfig`).")
        self.vision_config = Blip2VisionConfig(**vision_config)
        self.qformer_config = Blip2QFormerConfig(**qformer_config)
        text_model_type = text_config["model_type"] if "model_type" in text_config else "opt"
        self.text_config = CONFIG_MAPPING[text_model_type](**text_config)
        self.tie_word_embeddings = self.text_config.tie_word_embeddings
        self.is_encoder_decoder = self.text_config.is_encoder_decoder
        self.num_query_tokens = num_query_tokens
        self.image_text_hidden_size = image_text_hidden_size
        self.image_token_index = image_token_index
        self.qformer_config.encoder_hidden_size = self.vision_config.hidden_size
        self.use_decoder_only_language_model = self.text_config.model_type in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
        self.initializer_factor = 1.0
        self.initializer_range = 0.02
    @classmethod
    def from_vision_qformer_text_configs(cls, vision_config: Blip2VisionConfig, qformer_config: Blip2QFormerConfig, text_config: Optional[PretrainedConfig] = None, **kwargs): return cls(vision_config=vision_config.to_dict(), qformer_config=qformer_config.to_dict(), text_config=text_config.to_dict() if text_config is not None else None, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
