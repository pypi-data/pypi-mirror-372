"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING: pass
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class AlignTextConfig(PretrainedConfig):
    model_type = "align_text_model"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02, layer_norm_eps=1e-12, pad_token_id=0, position_embedding_type="absolute", use_cache=True, **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
        self.pad_token_id = pad_token_id
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "align": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class AlignVisionConfig(PretrainedConfig):
    model_type = "align_vision_model"
    def __init__(self, num_channels: int = 3, image_size: int = 600, width_coefficient: float = 2.0, depth_coefficient: float = 3.1, depth_divisor: int = 8, kernel_sizes: List[int] = [3, 3, 5, 3, 5, 5, 3],
    in_channels: List[int] = [32, 16, 24, 40, 80, 112, 192], out_channels: List[int] = [16, 24, 40, 80, 112, 192, 320], depthwise_padding: List[int] = [], strides: List[int] = [1, 2, 2, 2, 1, 2, 1],
    num_block_repeats: List[int] = [1, 2, 2, 3, 3, 4, 1], expand_ratios: List[int] = [1, 6, 6, 6, 6, 6, 6], squeeze_expansion_ratio: float = 0.25, hidden_act: str = "swish", hidden_dim: int = 2560,
    pooling_type: str = "mean", initializer_range: float = 0.02, batch_norm_eps: float = 0.001, batch_norm_momentum: float = 0.99, drop_connect_rate: float = 0.2, **kwargs):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.image_size = image_size
        self.width_coefficient = width_coefficient
        self.depth_coefficient = depth_coefficient
        self.depth_divisor = depth_divisor
        self.kernel_sizes = kernel_sizes
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.depthwise_padding = depthwise_padding
        self.strides = strides
        self.num_block_repeats = num_block_repeats
        self.expand_ratios = expand_ratios
        self.squeeze_expansion_ratio = squeeze_expansion_ratio
        self.hidden_act = hidden_act
        self.hidden_dim = hidden_dim
        self.pooling_type = pooling_type
        self.initializer_range = initializer_range
        self.batch_norm_eps = batch_norm_eps
        self.batch_norm_momentum = batch_norm_momentum
        self.drop_connect_rate = drop_connect_rate
        self.num_hidden_layers = sum(num_block_repeats) * 4
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "align": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class AlignConfig(PretrainedConfig):
    model_type = "align"
    def __init__(self, text_config=None, vision_config=None, projection_dim=640, temperature_init_value=1.0, initializer_range=0.02, **kwargs):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the AlignTextConfig with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("vision_config is None. Initializing the AlignVisionConfig with default values.")
        self.text_config = AlignTextConfig(**text_config)
        self.vision_config = AlignVisionConfig(**vision_config)
        self.projection_dim = projection_dim
        self.temperature_init_value = temperature_init_value
        self.initializer_range = initializer_range
    @classmethod
    def from_text_vision_configs(cls, text_config: AlignTextConfig, vision_config: AlignVisionConfig, **kwargs): return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
__all__ = ["AlignTextConfig", "AlignVisionConfig", "AlignConfig"]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
