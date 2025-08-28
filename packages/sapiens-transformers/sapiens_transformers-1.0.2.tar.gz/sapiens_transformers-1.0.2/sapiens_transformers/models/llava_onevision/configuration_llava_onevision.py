"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import (logging)
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class LlavaOnevisionConfig(PretrainedConfig):
    model_type = "llava_onevision"
    is_composition = False
    def __init__(self, vision_config=None, text_config=None, image_token_index=151646, video_token_index=151647, projector_hidden_act="gelu", vision_feature_select_strategy="full",
    vision_feature_layer=-1, vision_aspect_ratio="anyres_max_9", image_grid_pinpoints=None, tie_word_embeddings=False, **kwargs):
        self.image_token_index = image_token_index
        self.video_token_index = video_token_index
        self.projector_hidden_act = projector_hidden_act
        if vision_feature_select_strategy not in ["default", "full"]: raise ValueError(f"vision_feature_select_strategy should be one of 'default', 'full'. Got: {vision_feature_select_strategy}")
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.vision_feature_layer = vision_feature_layer
        self.vision_aspect_ratio = vision_aspect_ratio
        image_grid_pinpoints = (image_grid_pinpoints if image_grid_pinpoints is not None else [[384, 384], [384, 768], [384, 1152], [384, 1536], [384, 1920], [384, 2304], [768, 384], [768, 768],
        [768, 1152], [768, 1536], [768, 1920], [768, 2304], [1152, 384], [1152, 768], [1152, 1152], [1152, 1536], [1152, 1920], [1152, 2304], [1536, 384], [1536, 768], [1536, 1152], [1536, 1536],
        [1536, 1920], [1536, 2304], [1920, 384], [1920, 768], [1920, 1152], [1920, 1536], [1920, 1920], [1920, 2304], [2304, 384], [2304, 768], [2304, 1152], [2304, 1536], [2304, 1920], [2304, 2304]])
        self.image_grid_pinpoints = image_grid_pinpoints
        if isinstance(vision_config, dict):
            vision_config["model_type"] = (vision_config["model_type"] if "model_type" in vision_config else "siglip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None: vision_config = CONFIG_MAPPING["siglip_vision_model"](hidden_size=1152, intermediate_size=4304, patch_size=14, image_size=384, num_hidden_layers=26, num_attention_heads=14, vision_use_head=False)
        self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "qwen2"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["qwen2"]()
        self.text_config = text_config
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
