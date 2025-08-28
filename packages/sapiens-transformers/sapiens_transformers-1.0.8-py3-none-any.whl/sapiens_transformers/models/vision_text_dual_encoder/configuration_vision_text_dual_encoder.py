"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto.configuration_auto import AutoConfig
from ..chinese_clip.configuration_chinese_clip import ChineseCLIPVisionConfig
from ..clip.configuration_clip import CLIPVisionConfig
from ..siglip.configuration_siglip import SiglipVisionConfig
logger = logging.get_logger(__name__)
VISION_MODEL_CONFIGS = {"clip_vision_model": CLIPVisionConfig, "chinese_clip_vision_model": ChineseCLIPVisionConfig, "siglip_vision_model": SiglipVisionConfig}
class VisionTextDualEncoderConfig(PretrainedConfig):
    model_type = "vision-text-dual-encoder"
    is_composition = True
    def __init__(self, projection_dim=512, logit_scale_init_value=2.6592, **kwargs):
        super().__init__(**kwargs)
        if "vision_config" not in kwargs: raise ValueError("`vision_config` can not be `None`.")
        if "text_config" not in kwargs: raise ValueError("`text_config` can not be `None`.")
        vision_config = kwargs.pop("vision_config")
        text_config = kwargs.pop("text_config")
        vision_model_type = vision_config.pop("model_type")
        text_model_type = text_config.pop("model_type")
        vision_config_class = VISION_MODEL_CONFIGS.get(vision_model_type)
        if vision_config_class is not None: self.vision_config = vision_config_class(**vision_config)
        else:
            self.vision_config = AutoConfig.for_model(vision_model_type, **vision_config)
            if hasattr(self.vision_config, "vision_config"): self.vision_config = self.vision_config.vision_config
        self.text_config = AutoConfig.for_model(text_model_type, **text_config)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
    @classmethod
    def from_vision_text_configs(cls, vision_config: PretrainedConfig, text_config: PretrainedConfig, **kwargs): return cls(vision_config=vision_config.to_dict(), text_config=text_config.to_dict(), **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
