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
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class Idefics2VisionConfig(PretrainedConfig):
    model_type = "idefics2"
    def __init__(self, hidden_size=768, intermediate_size=3072, num_hidden_layers=12, num_attention_heads=12, num_channels=3, image_size=224, patch_size=32,
    hidden_act="gelu_pytorch_tanh", layer_norm_eps=1e-6, attention_dropout=0.0, initializer_range=0.02, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.image_size = image_size
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "idefics2": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Idefics2PerceiverConfig(PretrainedConfig):
    model_type = "idefics2"
    def __init__(self, hidden_act="silu", resampler_n_latents=64, resampler_depth=3, resampler_n_heads=16, resampler_head_dim=96, num_key_value_heads=4, attention_dropout=0.0, **kwargs):
        self.hidden_act = hidden_act
        self.resampler_n_latents = resampler_n_latents
        self.resampler_depth = resampler_depth
        self.resampler_n_heads = resampler_n_heads
        self.num_key_value_heads = num_key_value_heads
        self.resampler_head_dim = resampler_head_dim
        self.attention_dropout = attention_dropout
        if self.num_key_value_heads > self.resampler_n_heads: raise ValueError(f"num_key_value_heads={self.num_key_value_heads} must be less than or equal to resampler_n_heads={self.resampler_n_heads}")
        super().__init__(**kwargs)
class Idefics2Config(PretrainedConfig):
    model_type = "idefics2"
    is_composition = True
    def __init__(self, use_cache=True, image_token_id=32_001, tie_word_embeddings=False, vision_config=None, perceiver_config=None, text_config=None, **kwargs):
        self.image_token_id = image_token_id
        self.use_cache = use_cache
        self.tie_word_embeddings = tie_word_embeddings
        if perceiver_config is None:
            self.perceiver_config = Idefics2PerceiverConfig()
            logger.info("perciver_config is None, using default perceiver config")
        elif isinstance(perceiver_config, dict): self.perceiver_config = Idefics2PerceiverConfig(**perceiver_config)
        elif isinstance(perceiver_config, Idefics2PerceiverConfig): self.perceiver_config = perceiver_config
        if vision_config is None:
            self.vision_config = Idefics2VisionConfig()
            logger.info("vision_config is None, using default vision config")
        elif isinstance(vision_config, dict): self.vision_config = Idefics2VisionConfig(**vision_config)
        elif isinstance(vision_config, Idefics2VisionConfig): self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "mistral"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None:
            logger.info("text_config is None, using default text config")
            text_config = CONFIG_MAPPING["mistral"](max_position_embeddings=4096 * 8, rms_norm_eps=1e-5, pad_token_id=0, tie_word_embeddings=False)
        self.text_config = text_config
        super().__init__(**kwargs, tie_word_embeddings=tie_word_embeddings)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
