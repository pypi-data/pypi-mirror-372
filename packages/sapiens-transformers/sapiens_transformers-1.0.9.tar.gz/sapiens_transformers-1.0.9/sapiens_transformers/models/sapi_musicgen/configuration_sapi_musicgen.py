"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from ..auto.configuration_auto import AutoConfig
class SAPIMusicGenDecoderConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference = "sapi_musicgen_decoder", ["past_key_values"]
    def __init__(self, vocab_size=4096, max_position_embeddings=4096, num_hidden_layers=48, ffn_dim=4096, num_attention_heads=32, layerdrop=0.0, use_cache=True,
    activation_function="relu", hidden_size=1024, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, initializer_factor=0.02, scale_embedding=False,
    num_codebooks=4, audio_channels=2, pad_token_id=4096, bos_token_id=4096, eos_token_id=None, tie_word_embeddings=False, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 4096
        self.max_position_embeddings = max_position_embeddings if type(max_position_embeddings) in (int, float) else 4096
        self.num_hidden_layers = num_hidden_layers if type(num_hidden_layers) in (int, float) else 48
        self.ffn_dim = ffn_dim if type(ffn_dim) in (int, float) else 4096
        self.num_attention_heads = num_attention_heads if type(num_attention_heads) in (int, float) else 32
        self.layerdrop = layerdrop if type(layerdrop) in (int, float) else 0.0
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.activation_function = activation_function if type(activation_function) == str else "relu"
        self.hidden_size = hidden_size if type(hidden_size) in (int, float) else 1024
        self.dropout = dropout if type(dropout) in (int, float) else 0.1
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.0
        self.activation_dropout = activation_dropout if type(activation_dropout) in (int, float) else 0.0
        self.initializer_factor = initializer_factor if type(initializer_factor) in (int, float) else 0.02
        self.scale_embedding = scale_embedding if type(scale_embedding) in (bool, int, float) else False
        self.num_codebooks = num_codebooks if type(num_codebooks) in (int, float) else 4
        self.audio_channels = audio_channels if type(audio_channels) in (int, float) else 2
        if self.audio_channels not in [1, 2]: self.audio_channels = 2
        self.pad_token_id = pad_token_id if type(pad_token_id) in (int, float) else 4096
        self.bos_token_id = bos_token_id if type(bos_token_id) in (int, float) else 4096
        self.eos_token_id = eos_token_id
        self.tie_word_embeddings = tie_word_embeddings if type(tie_word_embeddings) in (bool, int, float) else False
        super().__init__(pad_token_id=self.pad_token_id, bos_token_id=self.bos_token_id, eos_token_id=self.eos_token_id, tie_word_embeddings=self.tie_word_embeddings, **kwargs)
class SAPIMusicGenConfig(SapiensTechnologyForPretraining):
    model_type, is_composition = "sapi_musicgen", True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "text_encoder" not in kwargs or "audio_encoder" not in kwargs or "decoder" not in kwargs: raise ValueError("Config has to be initialized with text_encoder, audio_encoder and decoder config")
        text_encoder_config = kwargs.pop("text_encoder")
        text_encoder_model_type = text_encoder_config.pop("model_type")
        audio_encoder_config = kwargs.pop("audio_encoder")
        audio_encoder_model_type = audio_encoder_config.pop("model_type")
        decoder_config = kwargs.pop("decoder")
        self.text_encoder = AutoConfig.for_model(text_encoder_model_type, **text_encoder_config)
        self.audio_encoder = AutoConfig.for_model(audio_encoder_model_type, **audio_encoder_config)
        self.decoder = SAPIMusicGenDecoderConfig(**decoder_config)
        self.is_encoder_decoder = True
    @classmethod
    def from_sub_models_config(cls, text_encoder_config: SapiensTechnologyForPretraining, audio_encoder_config: SapiensTechnologyForPretraining, decoder_config: SAPIMusicGenDecoderConfig, **kwargs): return cls(text_encoder=text_encoder_config.to_dict(),
    audio_encoder=audio_encoder_config.to_dict(), decoder=decoder_config.to_dict(), **kwargs)
    @property
    def sampling_rate(self): return self.audio_encoder.sampling_rate
    @property
    def _attn_implementation(self):
        if hasattr(self, "_attn_implementation_internal"):
            if self._attn_implementation_internal is None: return "eager"
            else: return self._attn_implementation_internal
        else: return "eager"
    @_attn_implementation.setter
    def _attn_implementation(self, value): self._attn_implementation_internal, self.decoder._attn_implementation = value, value
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
