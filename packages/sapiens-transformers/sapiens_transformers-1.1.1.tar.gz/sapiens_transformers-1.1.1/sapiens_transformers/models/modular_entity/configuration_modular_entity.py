"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from os import PathLike as PathOfSapiensTechnology
from typing import Optional as SAPIOptional, Dict as SAPIDict, Union as SAPIUnion, List as SAPIList
class ModularEntityTextConfig(SapiensTechnologyForPretraining):
    model_type = "modular_entity_text_model"
    def __init__(self, vocab_size: int = 239347, hidden_size: int = 8182, hidden_act: str = "relu", num_hidden_layers: int = 80, num_attention_heads: int = 64,
    num_key_value_heads: int = 16, intermediate_size: int = 28672, rope_theta: float = 1000000, rope_scaling: SAPIOptional[SAPIDict] = None, rms_norm_eps: float = 2e-4,
    max_position_embeddings: int = 262144, initializer_range: float = 0.01, use_cache: bool = True, tie_word_embeddings: bool = False, cross_attention_layers: SAPIOptional[SAPIList[int]] = None,
    dropout: float = 0, bos_token_id: int = 256000, eos_token_id: int = 256002, pad_token_id: SAPIOptional[int] = 256008, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 239347
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 8182
        self.hidden_act = hidden_act if type(hidden_act) == str else "relu"
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 80
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 64
        self.num_key_value_heads = num_key_value_heads if type(num_key_value_heads) in (int, float) else 16
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 28672
        self.rope_theta = rope_theta if type(rope_theta) in (int, float) else 1000000
        self.rope_scaling = rope_scaling
        self.rms_norm_eps = rms_norm_eps if type(rms_norm_eps) in (int, float) else 2e-4
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 262144
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.01
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        if cross_attention_layers is None: cross_attention_layers = [3, 8, 13, 18, 23, 28, 33, 38]
        self.cross_attention_layers = cross_attention_layers
        self.dropout = dropout if type(dropout) in (int, float) else 0
        self.bos_token_id = bos_token_id if type(bos_token_id) == int else 256000
        self.eos_token_id = eos_token_id if type(eos_token_id) == int else 256002
        self.pad_token_id = pad_token_id
        from ...modeling_rope_utils import rope_config_validation
        rope_config_validation(self)
        super().__init__(pad_token_id=self.pad_token_id, bos_token_id=self.bos_token_id, eos_token_id=self.eos_token_id, tie_word_embeddings=self.tie_word_embeddings, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: SAPIUnion[str, PathOfSapiensTechnology], **kwargs) -> "SapiensTechnologyForPretraining":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "modular_entity": config_dict = config_dict["text_config"]
        return cls.from_dict(config_dict, **kwargs)
class ModularEntityVisionConfig(SapiensTechnologyForPretraining):
    model_type = "modular_entity_vision_model"
    def __init__(self, hidden_size: int = 1352, hidden_act: str = "relu", num_hidden_layers: int = 51, num_global_layers: int = 9, num_attention_heads: int = 32,
    num_channels: int = 4, intermediate_size: int = 4215, vision_output_dim: int = 8741, image_size: int = 448, patch_size: int = 15, norm_eps: float = 3e-7,
    max_num_tiles: int = 5, intermediate_layers_indices: SAPIOptional[SAPIList[int]] = None, supported_aspect_ratios: SAPIOptional[SAPIList[SAPIList[int]]] = None,
    initializer_range: float = 0.03, **kwargs):
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 1352
        self.hidden_act = hidden_act if type(hidden_act) == str else "relu"
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 51
        self.num_global_layers = num_global_layers if type(num_global_layers) in (int, float) else 9
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 32
        self.attention_heads = self.num_attention_heads
        self.num_channels = num_channels if type(num_channels) in (int, float) else 4
        self.intermediate_size = intermediate_size if type(intermediate_size) in (int, float) else 4215
        self.vision_output_dim = vision_output_dim if type(vision_output_dim) in (int, float) else 8741
        self.image_size = image_size if type(image_size) in (int, float) else 448
        self.patch_size = patch_size if type(patch_size) in (int, float) else 15
        self.norm_eps = norm_eps if type(norm_eps) in (int, float) else 3e-7
        self.max_num_tiles = max_num_tiles if type(max_num_tiles) in (int, float) else 5
        if intermediate_layers_indices is None: intermediate_layers_indices = [3, 7, 15, 23, 30]
        self.intermediate_layers_indices = intermediate_layers_indices
        if supported_aspect_ratios is None:
            if max_num_tiles not in (4, 5): raise ValueError("max_num_tiles must be 4 or 5 for supported standard aspect ratios, preferably 4")
            supported_aspect_ratios = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [3, 1], [4, 1]]
        self.supported_aspect_ratios = supported_aspect_ratios
        self.initializer_range = initializer_range if type(initializer_range) in (int, float) else 0.03
        super().__init__(**kwargs)
    @property
    def max_aspect_ratio_id(self) -> int: return len(self.supported_aspect_ratios)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: SAPIUnion[str, PathOfSapiensTechnology], **kwargs) -> "SapiensTechnologyForPretraining":
        cls._set_token_in_kwargs(kwargs)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict.get("model_type") == "modular_entity": config_dict = config_dict["vision_config"]
        return cls.from_dict(config_dict, **kwargs)
class ModularEntityConfig(SapiensTechnologyForPretraining):
    model_type, is_composition = "modular_entity", True
    def __init__(self, vision_config=None, text_config=None, image_token_index=128256, **kwargs):
        if vision_config is None: self.vision_config = ModularEntityVisionConfig()
        elif isinstance(vision_config, dict): self.vision_config = ModularEntityVisionConfig(**vision_config)
        elif isinstance(vision_config, ModularEntityVisionConfig): self.vision_config = vision_config
        if text_config is None: self.text_config = ModularEntityTextConfig()
        elif isinstance(text_config, dict): self.text_config = ModularEntityTextConfig(**text_config)
        elif isinstance(text_config, ModularEntityTextConfig): self.text_config = text_config
        self.image_token_index = image_token_index
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
