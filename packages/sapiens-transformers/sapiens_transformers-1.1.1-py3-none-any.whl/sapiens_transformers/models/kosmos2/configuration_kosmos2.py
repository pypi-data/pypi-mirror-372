"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Union
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class Kosmos2TextConfig(PretrainedConfig):
    model_type = "kosmos_2_text_model"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'num_attention_heads': 'attention_heads', 'hidden_size': 'embed_dim', 'num_hidden_layers': 'layers'}
    def __init__(self, vocab_size=65037, max_position_embeddings=2048, embed_dim=2048, layers=24, ffn_dim=8192, attention_heads=32, activation_function="gelu",
    dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, layerdrop=0.0, layer_norm_eps=1e-5, init_std=0.02, scale_embedding=True, use_cache=True,
    pad_token_id=1, bos_token_id=0, eos_token_id=2, **kwargs):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.embed_dim = embed_dim
        self.layers = layers
        self.ffn_dim = ffn_dim
        self.attention_heads = attention_heads
        self.activation_function = activation_function
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.layerdrop = layerdrop
        self.layer_norm_eps = layer_norm_eps
        self.init_std = init_std
        self.scale_embedding = scale_embedding
        self.use_cache = use_cache
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "kosmos-2": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Kosmos2VisionConfig(PretrainedConfig):
    model_type = "kosmos_2_vision_model"
    def __init__(self, hidden_size=1024, intermediate_size=4096, num_hidden_layers=24, num_attention_heads=16, num_channels=3, image_size=224, patch_size=14,
    hidden_act="quick_gelu", layer_norm_eps=1e-5, attention_dropout=0.0, initializer_range=0.02, initializer_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.image_size = image_size
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "kosmos-2": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Kosmos2Config(PretrainedConfig):
    model_type = "kosmos-2"
    is_composition = True
    def __init__(self, text_config=None, vision_config=None, latent_query_num=64, **kwargs):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `Kosmos2TextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. Initializing the `Kosmos2VisionConfig` with default values.")
        self.text_config = Kosmos2TextConfig(**text_config)
        self.vision_config = Kosmos2VisionConfig(**vision_config)
        self.latent_query_num = latent_query_num
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
