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
class CLIPSegTextConfig(PretrainedConfig):
    model_type = "clipseg_text_model"
    def __init__(self, vocab_size=49408, hidden_size=512, intermediate_size=2048, num_hidden_layers=12, num_attention_heads=8, max_position_embeddings=77, hidden_act="quick_gelu",
    layer_norm_eps=1e-5, attention_dropout=0.0, initializer_range=0.02, initializer_factor=1.0, pad_token_id=1, bos_token_id=49406, eos_token_id=49407, **kwargs):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.attention_dropout = attention_dropout
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "clipseg": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class CLIPSegVisionConfig(PretrainedConfig):
    model_type = "clipseg_vision_model"
    def __init__(self, hidden_size=768, intermediate_size=3072, num_hidden_layers=12, num_attention_heads=12, num_channels=3, image_size=224, patch_size=32, hidden_act="quick_gelu",
    layer_norm_eps=1e-5, attention_dropout=0.0, initializer_range=0.02, initializer_factor=1.0, **kwargs):
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
        if config_dict.get("model_type") == "clipseg": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class CLIPSegConfig(PretrainedConfig):
    model_type = "clipseg"
    def __init__(self, text_config=None, vision_config=None, projection_dim=512, logit_scale_init_value=2.6592, extract_layers=[3, 6, 9], reduce_dim=64, decoder_num_attention_heads=4,
    decoder_attention_dropout=0.0, decoder_hidden_act="quick_gelu", decoder_intermediate_size=2048, conditional_layer=0, use_complex_transposed_convolution=False, **kwargs):
        text_config_dict = kwargs.pop("text_config_dict", None)
        vision_config_dict = kwargs.pop("vision_config_dict", None)
        super().__init__(**kwargs)
        if text_config_dict is not None:
            if text_config is None: text_config = {}
            _text_config_dict = CLIPSegTextConfig(**text_config_dict).to_dict()
            for key, value in _text_config_dict.items():
                if key in text_config and value != text_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in text_config_dict: message = (f"`{key}` is found in both `text_config_dict` and `text_config` but with different values. "+f'The value `text_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`text_config_dict` is provided which will be used to initialize `CLIPSegTextConfig`. The "+f'value `text_config["{key}"]` will be overridden.')
                    logger.info(message)
            text_config.update(_text_config_dict)
        if vision_config_dict is not None:
            if vision_config is None: vision_config = {}
            _vision_config_dict = CLIPSegVisionConfig(**vision_config_dict).to_dict()
            if "id2label" in _vision_config_dict: _vision_config_dict["id2label"] = {str(key): value for key, value in _vision_config_dict["id2label"].items()}
            for key, value in _vision_config_dict.items():
                if key in vision_config and value != vision_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in vision_config_dict: message = (f"`{key}` is found in both `vision_config_dict` and `vision_config` but with different "+f'values. The value `vision_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`vision_config_dict` is provided which will be used to initialize `CLIPSegVisionConfig`. "+f'The value `vision_config["{key}"]` will be overridden.')
                    logger.info(message)
            vision_config.update(_vision_config_dict)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `CLIPSegTextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. initializing the `CLIPSegVisionConfig` with default values.")
        self.text_config = CLIPSegTextConfig(**text_config)
        self.vision_config = CLIPSegVisionConfig(**vision_config)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.extract_layers = extract_layers
        self.reduce_dim = reduce_dim
        self.decoder_num_attention_heads = decoder_num_attention_heads
        self.decoder_attention_dropout = decoder_attention_dropout
        self.decoder_hidden_act = decoder_hidden_act
        self.decoder_intermediate_size = decoder_intermediate_size
        self.conditional_layer = conditional_layer
        self.initializer_factor = 1.0
        self.use_complex_transposed_convolution = use_complex_transposed_convolution
    @classmethod
    def from_text_vision_configs(cls, text_config: CLIPSegTextConfig, vision_config: CLIPSegVisionConfig, **kwargs): return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
