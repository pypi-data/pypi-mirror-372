"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from ..auto import CONFIG_MAPPING
class SAPIVideoConfig(SapiensTechnologyForPretraining):
    model_type, is_composition = "sapi_video", True
    def __init__(self, vision_config=None, text_config=None, ignore_index=-325, image_token_index=128531, projector_hidden_act="relu", vision_feature_select_strategy="default",
    vision_feature_layer=-1, image_grid_pinpoints=None, tie_word_embeddings=False, video_token_index=128531, spatial_pool_mode="average", spatial_pool_stride=4,
    image_seq_length=421, video_seq_length=122, **kwargs):
        if isinstance(vision_config, dict):
            vision_config["model_type"] = (vision_config["model_type"] if "model_type" in vision_config else "clip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["clip_vision_model"](intermediate_size=4096, hidden_size=1024, patch_size=14, image_size=336, num_hidden_layers=24,
            num_attention_heads=16, vocab_size=32000, projection_dim=768)
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "entity"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["entity"]()
        self.vision_config = vision_config
        self.text_config = text_config
        self.ignore_index = ignore_index if type(ignore_index) == int else -325
        self.image_token_index = image_token_index if type(image_token_index) == int else 128531
        self.projector_hidden_act = projector_hidden_act if type(projector_hidden_act) == str else "relu"
        self.vision_feature_select_strategy = vision_feature_select_strategy if vision_feature_select_strategy in ("default", "full") else "default"
        self.vision_feature_layer = vision_feature_layer if type(vision_feature_layer) in (int, float) else -1
        image_grid_pinpoints = (image_grid_pinpoints if image_grid_pinpoints is not None else [[336, 672], [672, 336], [672, 672], [1008, 336], [336, 1008]])
        self.image_grid_pinpoints = image_grid_pinpoints
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        self.video_token_index = video_token_index if type(video_token_index) == int else 128531
        self.spatial_pool_mode = spatial_pool_mode if type(spatial_pool_mode) == str else "average"
        self.spatial_pool_stride = spatial_pool_stride if type(spatial_pool_stride) in (int, float) else 4
        self.image_seq_length = image_seq_length if type(image_seq_length) in (int, float) else 421
        self.video_seq_length = video_seq_length if type(video_seq_length) in (int, float) else 122
        super().__init__(tie_word_embeddings=self.tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
