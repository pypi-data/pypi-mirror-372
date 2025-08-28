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
class Pix2StructTextConfig(PretrainedConfig):
    model_type = "pix2struct_text_model"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'hidden_size', 'num_attention_heads': 'num_heads', 'num_hidden_layers': 'num_layers'}
    def __init__(self, vocab_size=50244, hidden_size=768, d_kv=64, d_ff=2048, num_layers=12, num_heads=12, relative_attention_num_buckets=32, relative_attention_max_distance=128,
    dropout_rate=0.1, layer_norm_epsilon=1e-6, initializer_factor=1.0, dense_act_fn="gelu_new", decoder_start_token_id=0, use_cache=False, pad_token_id=0, eos_token_id=1,
    tie_word_embeddings=False, is_decoder=True, **kwargs):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.d_kv = d_kv
        self.d_ff = d_ff
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.dropout_rate = dropout_rate
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_factor = initializer_factor
        self.use_cache = use_cache
        self.eos_token_id = eos_token_id
        self.decoder_start_token_id = decoder_start_token_id
        self.dense_act_fn = dense_act_fn
        super().__init__(pad_token_id=pad_token_id, eos_token_id=eos_token_id, decoder_start_token_id=decoder_start_token_id, tie_word_embeddings=tie_word_embeddings,
        is_decoder=is_decoder, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrainehidden_size_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrainehidden_size_name_or_path, **kwargs)
        if config_dict.get("model_type") == "pix2struct": config_dict = config_dict["text_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Pix2StructVisionConfig(PretrainedConfig):
    model_type = "pix2struct_vision_model"
    def __init__(self, hidden_size=768, patch_embed_hidden_size=768, d_ff=2048, d_kv=64, num_hidden_layers=12, num_attention_heads=12, dense_act_fn="gelu_new",
    layer_norm_eps=1e-6, dropout_rate=0.0, attention_dropout=0.0, initializer_range=1e-10, initializer_factor=1.0, seq_len=4096, relative_attention_num_buckets=32, relative_attention_max_distance=128, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.patch_embed_hidden_size = patch_embed_hidden_size
        self.d_ff = d_ff
        self.dropout_rate = dropout_rate
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.dense_act_fn = dense_act_fn
        self.seq_len = seq_len
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.d_kv = d_kv
    @classmethod
    def from_pretrained(cls, pretrainehidden_size_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrainehidden_size_name_or_path, **kwargs)
        if config_dict.get("model_type") == "pix2struct": config_dict = config_dict["vision_config"]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type: logger.warning(f"You are using a model of type {config_dict['model_type']} to instantiate a model of type {cls.model_type}. This is not supported for all configurations of models and can yield errors.")
        return cls.from_dict(config_dict, **kwargs)
class Pix2StructConfig(PretrainedConfig):
    model_type = "pix2struct"
    def __init__(self, text_config=None, vision_config=None, initializer_factor=1.0, initializer_range=0.02, is_vqa=False, tie_word_embeddings=False, is_encoder_decoder=True, **kwargs):
        super().__init__(tie_word_embeddings=tie_word_embeddings, is_encoder_decoder=is_encoder_decoder, **kwargs)
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the Pix2StructTextConfig with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("vision_config is None. Initializing the Pix2StructVisionConfig with default values.")
        self.text_config = Pix2StructTextConfig(**text_config)
        self.vision_config = Pix2StructVisionConfig(**vision_config)
        self.decoder_start_token_id = self.text_config.decoder_start_token_id
        self.pad_token_id = self.text_config.pad_token_id
        self.eos_token_id = self.text_config.eos_token_id
        self.initializer_factor = initializer_factor
        self.initializer_range = initializer_range
        self.text_config.initializer_range = self.initializer_range
        self.vision_config.initializer_range = self.initializer_range
        self.is_vqa = is_vqa
    @classmethod
    def from_text_vision_configs(cls, text_config: Pix2StructTextConfig, vision_config: Pix2StructVisionConfig, **kwargs): return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
