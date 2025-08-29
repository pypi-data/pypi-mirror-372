"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Union
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from ...modeling_rope_utils import sapiens_technology_configuration_validation
class SapiensVisionConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "sapiens_vision", ["past_key_values"]
    def __init__(self, vocab_size=304128, hidden_size=16384, intermediate_size=59136, num_hidden_layers=160, num_attention_heads=128, num_key_value_heads=16, hidden_act="silu",
    max_position_embeddings=65536, initializer_range=0.04, rms_norm_eps=1e-07, use_cache=True, tie_word_embeddings=False, rope_theta=2000000.0, use_sliding_window=False,
    sliding_window=8192, max_window_layers=160, attention_dropout=0.01, vision_config=None, rope_scaling=None, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 304128
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 16384
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 59136
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 160
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 128
        if num_key_value_heads is None: num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads if type(num_key_value_heads) in (int, float) else 16
        self.hidden_act = hidden_act if type(hidden_act) == str else "silu"
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 65536
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.04
        self.rms_norm_eps = rms_norm_eps if type(rms_norm_eps) in (int, float) else 1e-07
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 2000000.0
        self.use_sliding_window = use_sliding_window if type(use_sliding_window) in (bool, int, float) else False
        self.sliding_window = sliding_window if type(sliding_window) in (int, float) else 8192
        self.max_window_layers = max_window_layers if type(max_window_layers) in (int, float) else 160
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        if isinstance(vision_config, dict): self.vision_config = SapiensVisionVisionConfig(**vision_config)
        elif vision_config is None: self.vision_config = SapiensVisionVisionConfig()
        self.rope_scaling = rope_scaling
        if self.rope_scaling is not None and "type" in self.rope_scaling:
            if self.rope_scaling["type"] == "mrope": self.rope_scaling["type"] = "default"
            self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        sapiens_technology_configuration_validation(self, ignore_keys={"mrope_section"})
        super().__init__(tie_word_embeddings=self.tie_word_embeddings, **kwargs)
class SapiensVisionVisionConfig(SapiensTechnologyForPretraining):
    model_type = "sapiens_vision"
    def __init__(self, depth=64, embed_dim=2560, hidden_size=7168, hidden_act="quick_gelu", mlp_ratio=8, num_heads=32, in_channels=3, patch_size=28, spatial_merge_size=4, temporal_patch_size=4, **kwargs):
        super().__init__(**kwargs)
        self.depth = depth if type(depth) in (int, float) else 64
        self.embed_dim = embed_dim if type(embed_dim) in (int, float) else 2560
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 7168
        self.hidden_act = hidden_act if type(hidden_act) == str else "quick_gelu"
        self.mlp_ratio = mlp_ratio if type(mlp_ratio) in (int, float) else 8
        self.num_heads = num_heads if type(num_heads) in (int, float) else 32
        self.in_channels = in_channels if type(in_channels) in (int, float) else 3
        self.patch_size = patch_size if type(patch_size) in (int, float) else 28
        self.spatial_merge_size = spatial_merge_size if type(spatial_merge_size) in (int, float) else 4
        self.temporal_patch_size = temporal_patch_size if type(temporal_patch_size) in (int, float) else 4
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "SapiensTechnologyForPretraining":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "sapiens_vision": config_dict = config_dict["vision_config"]
        return cls.from_dict(config_dict, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
