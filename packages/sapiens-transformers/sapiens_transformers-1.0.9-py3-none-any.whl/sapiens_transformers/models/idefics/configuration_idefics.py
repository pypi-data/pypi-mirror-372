"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class IdeficsVisionConfig(PretrainedConfig):
    model_type = "idefics"
    attribute_map = {'hidden_size': 'embed_dim'}
    def __init__(self, embed_dim=768, image_size=224, intermediate_size=5120, patch_size=14, num_hidden_layers=32, num_attention_heads=16, num_channels=3, hidden_act="gelu",
    layer_norm_eps=1e-5, attention_dropout=0.0, initializer_range=0.02, initializer_factor=1.0, **kwargs):
        self.embed_dim = embed_dim
        self.image_size = image_size
        self.intermediate_size = intermediate_size
        self.patch_size = patch_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.layer_norm_eps = layer_norm_eps
        self.attention_dropout = attention_dropout
        self.initializer_range = initializer_range
        self.initializer_factor = initializer_factor
        self.hidden_act = hidden_act
        super().__init__(**kwargs)
class IdeficsPerceiverConfig(PretrainedConfig):
    model_type = "idefics"
    def __init__(self, use_resampler=False, resampler_n_latents=64, resampler_depth=6, resampler_n_heads=16, resampler_head_dim=96, qk_layer_norms_perceiver=False, **kwargs):
        self.use_resampler = use_resampler
        self.resampler_n_latents = resampler_n_latents
        self.resampler_depth = resampler_depth
        self.resampler_n_heads = resampler_n_heads
        self.resampler_head_dim = resampler_head_dim
        self.qk_layer_norms_perceiver = qk_layer_norms_perceiver
        super().__init__(**kwargs)
class IdeficsConfig(PretrainedConfig):
    model_type = "idefics"
    is_composition = False
    def __init__(self, vocab_size=32000, additional_vocab_size=0, hidden_size=4096, intermediate_size=11008, num_hidden_layers=32, num_attention_heads=32, dropout=0.0,
    hidden_act="silu", initializer_range=0.02, alpha_initializer="zeros", alphas_initializer_range=0.0, alpha_type="float", rms_norm_eps=1e-6, use_cache=True,
    pad_token_id=0, bos_token_id=1, eos_token_id=2, tie_word_embeddings=False, cross_layer_interval=1, qk_layer_norms=False, freeze_text_layers=True, freeze_text_module_exceptions=[],
    freeze_lm_head=False, freeze_vision_layers=True, freeze_vision_module_exceptions=[], use_resampler=False, vision_config=None, perceiver_config=None, **kwargs):
        self.vocab_size = vocab_size
        self.additional_vocab_size = additional_vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.dropout = dropout
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.alpha_initializer = alpha_initializer
        self.alphas_initializer_range = alphas_initializer_range
        self.alpha_type = alpha_type
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.cross_layer_interval = cross_layer_interval
        self.qk_layer_norms = qk_layer_norms
        self.freeze_vision_layers = freeze_vision_layers
        self.freeze_text_layers = freeze_text_layers
        self.freeze_text_module_exceptions = freeze_text_module_exceptions
        self.freeze_vision_module_exceptions = freeze_vision_module_exceptions
        self.freeze_lm_head = freeze_lm_head
        self.use_resampler = use_resampler
        if perceiver_config is None: self.perceiver_config = IdeficsPerceiverConfig()
        elif isinstance(perceiver_config, dict): self.perceiver_config = IdeficsPerceiverConfig(**perceiver_config)
        elif isinstance(perceiver_config, IdeficsPerceiverConfig): self.perceiver_config = perceiver_config
        if vision_config is None: self.vision_config = IdeficsVisionConfig()
        elif isinstance(vision_config, dict): self.vision_config = IdeficsVisionConfig(**vision_config)
        elif isinstance(vision_config, IdeficsVisionConfig): self.vision_config = vision_config
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""

