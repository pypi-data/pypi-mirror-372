"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Any, Dict, Union
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class FlavaImageConfig(PretrainedConfig):
    model_type = "flava_image_model"
    def __init__(self, hidden_size: int = 768, num_hidden_layers: int = 12, num_attention_heads: int = 12, intermediate_size: int = 3072, hidden_act: int = "gelu",
    hidden_dropout_prob: float = 0.0, attention_probs_dropout_prob: float = 0.0, initializer_range: float = 0.02, layer_norm_eps: float = 1e-12, image_size: int = 224,
    patch_size: int = 16, num_channels: int = 3, qkv_bias: bool = True, mask_token: bool = True, vocab_size: int = 8192, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
        self.mask_token = mask_token
        self.vocab_size = vocab_size
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "flava": config_dict = config_dict["image_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class FlavaTextConfig(PretrainedConfig):
    model_type = "flava_text_model"
    def __init__(self, vocab_size: int = 30522, type_vocab_size: int = 2, max_position_embeddings: int = 512, position_embedding_type: str = "absolute", hidden_size: int = 768,
    num_hidden_layers: int = 12, num_attention_heads: int = 12, intermediate_size: int = 3072, hidden_act: str = "gelu", hidden_dropout_prob: float = 0.0, attention_probs_dropout_prob: float = 0.0,
    initializer_range: float = 0.02, layer_norm_eps: float = 1e-12, pad_token_id: int = 0, qkv_bias: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.type_vocab_size = type_vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.position_embedding_type = position_embedding_type
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.pad_token_id = pad_token_id
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "flava": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class FlavaMultimodalConfig(PretrainedConfig):
    model_type = "flava_multimodal_model"
    def __init__(self, hidden_size: int = 768, num_hidden_layers: int = 6, num_attention_heads: int = 12, intermediate_size: int = 3072, hidden_act: int = "gelu",
    hidden_dropout_prob: int = 0.0, attention_probs_dropout_prob: int = 0.0, initializer_range: float = 0.02, layer_norm_eps: float = 1e-12, qkv_bias: bool = True,
    use_cls_token: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.qkv_bias = qkv_bias
        self.use_cls_token = use_cls_token
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "flava": config_dict = config_dict["multimodal_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class FlavaImageCodebookConfig(PretrainedConfig):
    model_type = "flava_image_codebook"
    def __init__(self, num_groups: int = 4, input_channels: int = 3, num_blocks_per_group: int = 2, hidden_size: int = 256, vocab_size: int = 8192, freeze: int = True, initializer_range: float = 0.02, **kwargs):
        super().__init__(**kwargs)
        self.num_groups = num_groups
        self.input_channels = input_channels
        self.num_blocks_per_group = num_blocks_per_group
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.freeze = freeze
        self.initializer_range = initializer_range
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "flava": config_dict = config_dict["image_codebook_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class FlavaConfig(PretrainedConfig):
    model_type = "flava"
    def __init__(self, image_config: Dict[str, Any] = None, text_config: Dict[str, Any] = None, multimodal_config: Dict[str, Any] = None, image_codebook_config: Dict[str, Any] = None,
    hidden_size: int = 768, layer_norm_eps: float = 1e-12, projection_dim: int = 768, init_codebook: bool = True, logit_scale_init_value: float = 2.6592, initializer_range: float = 0.02,
    ce_ignore_index: int = -100, mim_weight: float = 1.0, mlm_weight: float = 1.0, global_contrastive_weight: float = 1.0, itm_weight: float = 1.0, mmm_image_weight: float = 1.0,
    mmm_text_weight: float = 1.0, global_backprop_contrastive: bool = True, skip_unmasked_multimodal_encoder: bool = True, return_loss: bool = True, **kwargs):
        text_config_dict = kwargs.pop("text_config_dict", None)
        image_config_dict = kwargs.pop("image_config_dict", None)
        multimodal_config_dict = kwargs.pop("multimodal_config_dict", None)
        image_codebook_config_dict = kwargs.pop("image_codebook_config_dict", None)
        super().__init__(**kwargs)
        if text_config_dict is not None:
            if text_config is None: text_config = {}
            _text_config_dict = FlavaTextConfig(**text_config_dict).to_dict()
            for key, value in _text_config_dict.items():
                if key in text_config and value != text_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in text_config_dict: message = (f"`{key}` is found in both `text_config_dict` and `text_config` but with different values. "+f'The value `text_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`text_config_dict` is provided which will be used to initialize `FlavaTextConfig`. The "+f'value `text_config["{key}"]` will be overridden.')
                    logger.info(message)
            text_config.update(_text_config_dict)
        if image_config_dict is not None:
            if image_config is None: image_config = {}
            _image_config_dict = FlavaImageConfig(**image_config_dict).to_dict()
            if "id2label" in _image_config_dict: _image_config_dict["id2label"] = {str(key): value for key, value in _image_config_dict["id2label"].items()}
            for key, value in _image_config_dict.items():
                if key in image_config and value != image_config[key] and key not in ["sapiens_transformers_version"]:
                    if key in image_config_dict: message = (f"`{key}` is found in both `image_config_dict` and `image_config` but with different "+f'values. The value `image_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`image_config_dict` is provided which will be used to initialize `FlavaImageConfig`. "+f'The value `image_config["{key}"]` will be overridden.')
                    logger.info(message)
            image_config.update(_image_config_dict)
        if multimodal_config_dict is not None:
            if multimodal_config is None: multimodal_config = {}
            _multimodal_config_dict = FlavaMultimodalConfig(**multimodal_config_dict).to_dict()
            for key, value in _multimodal_config_dict.items():
                if (key in multimodal_config and value != multimodal_config[key] and key not in ["sapiens_transformers_version"]):
                    if key in multimodal_config_dict: message = (f"`{key}` is found in both `multimodal_config_dict` and `multimodal_config` but with "+f'different values. The value `multimodal_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`multimodal_config_dict` is provided which will be used to initialize "+f'`FlavaMultimodalConfig`. The value `multimodal_config["{key}"]` will be overridden.')
                    logger.info(message)
            multimodal_config.update(_multimodal_config_dict)
        if image_codebook_config_dict is not None:
            if image_codebook_config is None: image_codebook_config = {}
            _image_codebook_config_dict = FlavaImageCodebookConfig(**image_codebook_config_dict).to_dict()
            for key, value in _image_codebook_config_dict.items():
                if (key in image_codebook_config and value != image_codebook_config[key] and key not in ["sapiens_transformers_version"]):
                    if key in image_codebook_config_dict: message = (f"`{key}` is found in both `image_codebook_config_dict` and `image_codebook_config` but "+f'with different values. The value `image_codebook_config_dict["{key}"]` will be used instead.')
                    else: message = (f"`image_codebook_config_dict` is provided which will be used to initialize "+f'`FlavaImageCodebookConfig`. The value `image_codebook_config["{key}"]` will be overridden.')
                    logger.info(message)
            image_codebook_config.update(_image_codebook_config_dict)
        if image_config is None:
            image_config = {}
            logger.info("`image_config` is `None`. initializing the `FlavaImageConfig` with default values.")
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `FlavaTextConfig` with default values.")
        if multimodal_config is None:
            multimodal_config = {}
            logger.info("`multimodal_config` is `None`. initializing the `FlavaMultimodalConfig` with default values.")
        if image_codebook_config is None:
            image_codebook_config = {}
            logger.info("`image_codebook_config` is `None`. initializing the `FlavaImageCodebookConfig` with default values.")
        self.image_config = FlavaImageConfig(**image_config)
        self.text_config = FlavaTextConfig(**text_config)
        self.multimodal_config = FlavaMultimodalConfig(**multimodal_config)
        self.image_codebook_config = FlavaImageCodebookConfig(**image_codebook_config)
        self.projection_dim = projection_dim
        self.init_codebook = init_codebook
        self.hidden_size = hidden_size
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range
        self.logit_scale_init_value = logit_scale_init_value
        self.initializer_factor = 1.0
        self.ce_ignore_index = ce_ignore_index
        self.mim_weight = mim_weight
        self.mlm_weight = mlm_weight
        self.global_contrastive_weight = global_contrastive_weight
        self.itm_weight = itm_weight
        self.mmm_image_weight = mmm_image_weight
        self.mmm_text_weight = mmm_text_weight
        self.global_backprop_contrastive = global_backprop_contrastive
        self.skip_unmasked_multimodal_encoder = skip_unmasked_multimodal_encoder
        self.return_loss = return_loss
    @classmethod
    def from_configs(cls, image_config: FlavaImageConfig, text_config: FlavaTextConfig, multimodal_config: FlavaMultimodalConfig, image_codebook_config: FlavaImageCodebookConfig, **kwargs): return cls(image_config=image_config.to_dict(), text_config=text_config.to_dict(), multimodal_config=multimodal_config.to_dict(), image_codebook_config=image_codebook_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
