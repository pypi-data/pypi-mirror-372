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
class BridgeTowerVisionConfig(PretrainedConfig):
    model_type = "bridgetower_vision_model"
    def __init__(self, hidden_size=768, num_hidden_layers=12, num_channels=3, patch_size=16, image_size=288, initializer_factor=1, layer_norm_eps=1e-05, stop_gradient=False,
    share_layernorm=True, remove_last_layer=False, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.image_size = image_size
        self.initializer_factor = initializer_factor
        self.layer_norm_eps = layer_norm_eps
        self.stop_gradient = stop_gradient
        self.share_layernorm = share_layernorm
        self.remove_last_layer = remove_last_layer
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "bridgetower": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class BridgeTowerTextConfig(PretrainedConfig):
    model_type = "bridgetower_text_model"
    def __init__(self, vocab_size=50265, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, initializer_factor=1, intermediate_size=3072, hidden_act="gelu",
    hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.1, max_position_embeddings=514, type_vocab_size=1, layer_norm_eps=1e-05, pad_token_id=1, bos_token_id=0,
    eos_token_id=2, position_embedding_type="absolute", use_cache=True, **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.initializer_factor = initializer_factor
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
        self.pad_token_id = pad_token_id
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "bridgetower": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class BridgeTowerConfig(PretrainedConfig):
    model_type = "bridgetower"
    def __init__(self, share_cross_modal_transformer_layers=True, hidden_act="gelu", hidden_size=768, initializer_factor=1, layer_norm_eps=1e-05, share_link_tower_layers=False,
    link_tower_type="add", num_attention_heads=12, num_hidden_layers=6, tie_word_embeddings=False, init_layernorm_from_vision_encoder=False, text_config=None, vision_config=None, **kwargs):
        _ = kwargs.pop("text_config_dict", None)
        _ = kwargs.pop("vision_config_dict", None)
        super().__init__(**kwargs)
        self.share_cross_modal_transformer_layers = share_cross_modal_transformer_layers
        self.hidden_act = hidden_act
        self.hidden_size = hidden_size
        self.initializer_factor = initializer_factor
        self.layer_norm_eps = layer_norm_eps
        self.share_link_tower_layers = share_link_tower_layers
        self.link_tower_type = link_tower_type
        self.num_attention_heads = num_attention_heads
        self.num_hidden_layers = num_hidden_layers
        self.tie_word_embeddings = tie_word_embeddings
        self.init_layernorm_from_vision_encoder = init_layernorm_from_vision_encoder
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `BridgeTowerTextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. Initializing the `BridgeTowerVisionConfig` with default values.")
        self.text_config = BridgeTowerTextConfig(**text_config)
        self.vision_config = BridgeTowerVisionConfig(**vision_config)
    @classmethod
    def from_text_vision_configs(cls, text_config: BridgeTowerTextConfig, vision_config: BridgeTowerVisionConfig, **kwargs): return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
