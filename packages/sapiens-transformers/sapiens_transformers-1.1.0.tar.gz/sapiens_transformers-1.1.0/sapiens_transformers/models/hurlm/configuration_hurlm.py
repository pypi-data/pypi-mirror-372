"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from ..auto import CONFIG_MAPPING, AutoConfig
class HurLMVisionConfig(SapiensTechnologyForPretraining):
    model_type, base_config_key = "hurlm_vision", "vision_config"
    def __init__(self, hidden_size=2415, intermediate_size=2253, num_hidden_layers=24, num_attention_heads=32, num_channels=4, image_size=228,
    patch_size=41, hidden_act="gelu_pytorch_tanh", layer_norm_eps=1e-7, attention_dropout=0.01, initializer_range=0.03, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 2415
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 2253
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 24
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 32
        self.num_channels = num_channels if type(num_channels) in (int, float) else 4
        self.image_size = image_size if type(image_size) in (int, float) else 228
        self.patch_size = patch_size if type(patch_size) in (int, float) else 41
        self.hidden_act = hidden_act if type(hidden_act) == str else "gelu_pytorch_tanh"
        self.layer_norm_eps = layer_norm_eps if type(layer_norm_eps) in (int, float) else 1e-7
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.03
class HurLMConfig(SapiensTechnologyForPretraining):
    model_type, sub_configs = "hurlm", {"text_config": AutoConfig, "vision_config": HurLMVisionConfig}
    def __init__(self, use_cache=True, image_token_id=235189, tie_word_embeddings=False, vision_config=None, text_config=None, scale_factor=4, pad_token_id=256004, **kwargs):
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.image_token_id = image_token_id if type(image_token_id) in (int, float) else 235189
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        if vision_config is None: self.vision_config = HurLMVisionConfig()
        elif isinstance(vision_config, dict): self.vision_config = HurLMVisionConfig(**vision_config)
        elif isinstance(vision_config, HurLMVisionConfig): self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "llama"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["llama"](rms_norm_eps=1e-5, pad_token_id=pad_token_id, tie_word_embeddings=False)
        self.text_config = text_config
        self.scale_factor = scale_factor if type(scale_factor) in (int, float) else 4
        self.pad_token_id = pad_token_id if type(pad_token_id) in (int, float) else 256004
        super().__init__(**kwargs, pad_token_id=self.pad_token_id, tie_word_embeddings=tie_word_embeddings)
__all__ = ["HurLMConfig", "HurLMVisionConfig"]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
