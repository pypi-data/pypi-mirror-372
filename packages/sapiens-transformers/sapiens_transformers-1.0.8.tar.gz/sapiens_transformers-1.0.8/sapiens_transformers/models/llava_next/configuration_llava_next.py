"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class LlavaNextConfig(PretrainedConfig):
    model_type = "llava_next"
    is_composition = False
    def __init__(self, vision_config=None, text_config=None, ignore_index=-100, image_token_index=32000, projector_hidden_act="gelu", vision_feature_select_strategy="default",
    vision_feature_layer=-2, image_grid_pinpoints=None, tie_word_embeddings=False, image_seq_length=576, **kwargs):
        self.ignore_index = ignore_index
        self.image_token_index = image_token_index
        self.projector_hidden_act = projector_hidden_act
        self.image_seq_length = image_seq_length
        if vision_feature_select_strategy not in ["default", "full"]: raise ValueError(f"vision_feature_select_strategy should be one of 'default', 'full'. Got: {vision_feature_select_strategy}")
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.vision_feature_layer = vision_feature_layer
        image_grid_pinpoints = (image_grid_pinpoints if image_grid_pinpoints is not None else [[336, 672], [672, 336], [672, 672], [1008, 336], [336, 1008]])
        self.image_grid_pinpoints = image_grid_pinpoints
        if isinstance(vision_config, dict):
            vision_config["model_type"] = (vision_config["model_type"] if "model_type" in vision_config else "clip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["clip_vision_model"](intermediate_size=4096, hidden_size=1024, patch_size=14, image_size=336, num_hidden_layers=24,
            num_attention_heads=16, vocab_size=32000, projection_dim=768)
        self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "llama"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["llama"]()
        self.text_config = text_config
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
