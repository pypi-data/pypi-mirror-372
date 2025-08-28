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
logger = logging.get_logger(__name__)
class MusicgenMelodyDecoderConfig(PretrainedConfig):
    model_type = "musicgen_melody_decoder"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=2048, max_position_embeddings=2048, num_hidden_layers=24, ffn_dim=4096, num_attention_heads=16, layerdrop=0.0, use_cache=True,
    activation_function="gelu", hidden_size=1024, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, initializer_factor=0.02, scale_embedding=False,
    num_codebooks=4, audio_channels=1, pad_token_id=2048, bos_token_id=2048, eos_token_id=None, tie_word_embeddings=False, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.ffn_dim = ffn_dim
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.initializer_factor = initializer_factor
        self.layerdrop = layerdrop
        self.use_cache = use_cache
        self.scale_embedding = scale_embedding
        self.num_codebooks = num_codebooks
        if audio_channels not in [1, 2]: raise ValueError(f"Expected 1 (mono) or 2 (stereo) audio channels, got {audio_channels} channels.")
        self.audio_channels = audio_channels
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
class MusicgenMelodyConfig(PretrainedConfig):
    model_type = "musicgen_melody"
    is_composition = True
    def __init__(self, num_chroma=12, chroma_length=235, **kwargs):
        super().__init__(**kwargs)
        if "text_encoder" not in kwargs or "audio_encoder" not in kwargs or "decoder" not in kwargs: raise ValueError("Config has to be initialized with text_encoder, audio_encoder and decoder config")
        text_encoder_config = kwargs.pop("text_encoder")
        text_encoder_model_type = text_encoder_config.pop("model_type")
        audio_encoder_config = kwargs.pop("audio_encoder")
        audio_encoder_model_type = audio_encoder_config.pop("model_type")
        decoder_config = kwargs.pop("decoder")
        self.text_encoder = AutoConfig.for_model(text_encoder_model_type, **text_encoder_config)
        self.audio_encoder = AutoConfig.for_model(audio_encoder_model_type, **audio_encoder_config)
        self.decoder = MusicgenMelodyDecoderConfig(**decoder_config)
        self.is_encoder_decoder = False
        self.num_chroma = num_chroma
        self.chroma_length = chroma_length
    @classmethod
    def from_sub_models_config(cls, text_encoder_config: PretrainedConfig, audio_encoder_config: PretrainedConfig, decoder_config: MusicgenMelodyDecoderConfig, **kwargs): return cls(text_encoder=text_encoder_config.to_dict(), audio_encoder=audio_encoder_config.to_dict(), decoder=decoder_config.to_dict(), **kwargs)
    @property
    def sampling_rate(self): return self.audio_encoder.sampling_rate
    @property
    def _attn_implementation(self):
        if hasattr(self, "_attn_implementation_internal"):
            if self._attn_implementation_internal is None: return "eager"
            else: return self._attn_implementation_internal
        else: return "eager"
    @_attn_implementation.setter
    def _attn_implementation(self, value):
        self._attn_implementation_internal = value
        self.decoder._attn_implementation = value
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
