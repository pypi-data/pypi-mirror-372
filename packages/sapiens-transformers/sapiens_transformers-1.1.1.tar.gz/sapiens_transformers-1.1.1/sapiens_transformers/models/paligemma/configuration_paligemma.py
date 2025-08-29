"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class PaliGemmaConfig(PretrainedConfig):
    model_type = "paligemma"
    is_composition = False
    def __init__(self, vision_config=None, text_config=None, ignore_index=-100, image_token_index=256000, vocab_size=257152, projection_dim=2048, hidden_size=2048, **kwargs):
        self._ignore_index = ignore_index
        self.image_token_index = image_token_index
        self._vocab_size = vocab_size
        self.projection_dim = projection_dim
        self.hidden_size = hidden_size
        self.vision_config = vision_config
        self.is_encoder_decoder = False
        if isinstance(self.vision_config, dict):
            vision_config["model_type"] = (vision_config["model_type"] if "model_type" in vision_config else "siglip_vision_model")
            self.vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            self.vision_config = CONFIG_MAPPING["siglip_vision_model"](intermediate_size=4096, hidden_size=1152, patch_size=14, image_size=224, num_hidden_layers=27,
            num_attention_heads=16, vocab_size=257152, vision_use_head=False)
        self.text_config = text_config
        if isinstance(self.text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "gemma"
            self.text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None:
            self.text_config = CONFIG_MAPPING["gemma"](hidden_size=2048, num_hidden_layers=18, intermediate_size=16384, num_attention_heads=8, num_key_value_heads=1,
            is_encoder_decoder=False, vocab_size=vocab_size)
        self.text_config.num_image_tokens = (self.vision_config.image_size // self.vision_config.patch_size) ** 2
        self.vision_config.projection_dim = projection_dim
        super().__init__(**kwargs)
    @property
    def ignore_index(self):
        warnings.warn("The `ignore_index` attribute is deprecated and will be removed in v1.0.", FutureWarning)
        return self._ignore_index
    @ignore_index.setter
    def ignore_index(self, value): self._ignore_index = value
    def to_dict(self):
        output = super().to_dict()
        output.pop("_ignore_index", None)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
