"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class FastSpeech2ConformerConfig(PretrainedConfig):
    model_type = "fastspeech2_conformer"
    attribute_map = {"num_hidden_layers": "encoder_layers", "num_attention_heads": "encoder_num_attention_heads"}
    def __init__(self, hidden_size=384, vocab_size=78, num_mel_bins=80, encoder_num_attention_heads=2, encoder_layers=4, encoder_linear_units=1536, decoder_layers=4,
    decoder_num_attention_heads=2, decoder_linear_units=1536, speech_decoder_postnet_layers=5, speech_decoder_postnet_units=256, speech_decoder_postnet_kernel=5,
    positionwise_conv_kernel_size=3, encoder_normalize_before=False, decoder_normalize_before=False, encoder_concat_after=False, decoder_concat_after=False,
    reduction_factor=1, speaking_speed=1.0, use_macaron_style_in_conformer=True, use_cnn_in_conformer=True, encoder_kernel_size=7, decoder_kernel_size=31,
    duration_predictor_layers=2, duration_predictor_channels=256, duration_predictor_kernel_size=3, energy_predictor_layers=2, energy_predictor_channels=256,
    energy_predictor_kernel_size=3, energy_predictor_dropout=0.5, energy_embed_kernel_size=1, energy_embed_dropout=0.0, stop_gradient_from_energy_predictor=False,
    pitch_predictor_layers=5, pitch_predictor_channels=256, pitch_predictor_kernel_size=5, pitch_predictor_dropout=0.5, pitch_embed_kernel_size=1, pitch_embed_dropout=0.0,
    stop_gradient_from_pitch_predictor=True, encoder_dropout_rate=0.2, encoder_positional_dropout_rate=0.2, encoder_attention_dropout_rate=0.2, decoder_dropout_rate=0.2,
    decoder_positional_dropout_rate=0.2, decoder_attention_dropout_rate=0.2, duration_predictor_dropout_rate=0.2, speech_decoder_postnet_dropout=0.5, max_source_positions=5000,
    use_masking=True, use_weighted_masking=False, num_speakers=None, num_languages=None, speaker_embed_dim=None, is_encoder_decoder=True, **kwargs):
        if positionwise_conv_kernel_size % 2 == 0: raise ValueError(f"positionwise_conv_kernel_size must be odd, but got {positionwise_conv_kernel_size} instead.")
        if encoder_kernel_size % 2 == 0: raise ValueError(f"encoder_kernel_size must be odd, but got {encoder_kernel_size} instead.")
        if decoder_kernel_size % 2 == 0: raise ValueError(f"decoder_kernel_size must be odd, but got {decoder_kernel_size} instead.")
        if duration_predictor_kernel_size % 2 == 0: raise ValueError(f"duration_predictor_kernel_size must be odd, but got {duration_predictor_kernel_size} instead.")
        if energy_predictor_kernel_size % 2 == 0: raise ValueError(f"energy_predictor_kernel_size must be odd, but got {energy_predictor_kernel_size} instead.")
        if energy_embed_kernel_size % 2 == 0: raise ValueError(f"energy_embed_kernel_size must be odd, but got {energy_embed_kernel_size} instead.")
        if pitch_predictor_kernel_size % 2 == 0: raise ValueError(f"pitch_predictor_kernel_size must be odd, but got {pitch_predictor_kernel_size} instead.")
        if pitch_embed_kernel_size % 2 == 0: raise ValueError(f"pitch_embed_kernel_size must be odd, but got {pitch_embed_kernel_size} instead.")
        if hidden_size % encoder_num_attention_heads != 0: raise ValueError("The hidden_size must be evenly divisible by encoder_num_attention_heads.")
        if hidden_size % decoder_num_attention_heads != 0: raise ValueError("The hidden_size must be evenly divisible by decoder_num_attention_heads.")
        if use_masking and use_weighted_masking: raise ValueError("Either use_masking or use_weighted_masking can be True, but not both.")
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.num_mel_bins = num_mel_bins
        self.encoder_config = {"num_attention_heads": encoder_num_attention_heads, "layers": encoder_layers, "kernel_size": encoder_kernel_size, "attention_dropout_rate": encoder_attention_dropout_rate,
        "dropout_rate": encoder_dropout_rate, "positional_dropout_rate": encoder_positional_dropout_rate, "linear_units": encoder_linear_units, "normalize_before": encoder_normalize_before, "concat_after": encoder_concat_after}
        self.decoder_config = {"num_attention_heads": decoder_num_attention_heads, "layers": decoder_layers, "kernel_size": decoder_kernel_size, "attention_dropout_rate": decoder_attention_dropout_rate,
        "dropout_rate": decoder_dropout_rate, "positional_dropout_rate": decoder_positional_dropout_rate, "linear_units": decoder_linear_units, "normalize_before": decoder_normalize_before, "concat_after": decoder_concat_after}
        self.encoder_num_attention_heads = encoder_num_attention_heads
        self.encoder_layers = encoder_layers
        self.duration_predictor_channels = duration_predictor_channels
        self.duration_predictor_kernel_size = duration_predictor_kernel_size
        self.duration_predictor_layers = duration_predictor_layers
        self.energy_embed_dropout = energy_embed_dropout
        self.energy_embed_kernel_size = energy_embed_kernel_size
        self.energy_predictor_channels = energy_predictor_channels
        self.energy_predictor_dropout = energy_predictor_dropout
        self.energy_predictor_kernel_size = energy_predictor_kernel_size
        self.energy_predictor_layers = energy_predictor_layers
        self.pitch_embed_dropout = pitch_embed_dropout
        self.pitch_embed_kernel_size = pitch_embed_kernel_size
        self.pitch_predictor_channels = pitch_predictor_channels
        self.pitch_predictor_dropout = pitch_predictor_dropout
        self.pitch_predictor_kernel_size = pitch_predictor_kernel_size
        self.pitch_predictor_layers = pitch_predictor_layers
        self.positionwise_conv_kernel_size = positionwise_conv_kernel_size
        self.speech_decoder_postnet_units = speech_decoder_postnet_units
        self.speech_decoder_postnet_dropout = speech_decoder_postnet_dropout
        self.speech_decoder_postnet_kernel = speech_decoder_postnet_kernel
        self.speech_decoder_postnet_layers = speech_decoder_postnet_layers
        self.reduction_factor = reduction_factor
        self.speaking_speed = speaking_speed
        self.stop_gradient_from_energy_predictor = stop_gradient_from_energy_predictor
        self.stop_gradient_from_pitch_predictor = stop_gradient_from_pitch_predictor
        self.max_source_positions = max_source_positions
        self.use_cnn_in_conformer = use_cnn_in_conformer
        self.use_macaron_style_in_conformer = use_macaron_style_in_conformer
        self.use_masking = use_masking
        self.use_weighted_masking = use_weighted_masking
        self.num_speakers = num_speakers
        self.num_languages = num_languages
        self.speaker_embed_dim = speaker_embed_dim
        self.duration_predictor_dropout_rate = duration_predictor_dropout_rate
        self.is_encoder_decoder = is_encoder_decoder
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
class FastSpeech2ConformerHifiGanConfig(PretrainedConfig):
    model_type = "hifigan"
    def __init__(self, model_in_dim=80, upsample_initial_channel=512, upsample_rates=[8, 8, 2, 2], upsample_kernel_sizes=[16, 16, 4, 4], resblock_kernel_sizes=[3, 7, 11],
    resblock_dilation_sizes=[[1, 3, 5], [1, 3, 5], [1, 3, 5]], initializer_range=0.01, leaky_relu_slope=0.1, normalize_before=True, **kwargs):
        self.model_in_dim = model_in_dim
        self.upsample_initial_channel = upsample_initial_channel
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.initializer_range = initializer_range
        self.leaky_relu_slope = leaky_relu_slope
        self.normalize_before = normalize_before
        super().__init__(**kwargs)
class FastSpeech2ConformerWithHifiGanConfig(PretrainedConfig):
    model_type = "fastspeech2_conformer_with_hifigan"
    is_composition = True
    def __init__(self, model_config: Dict = None, vocoder_config: Dict = None, **kwargs):
        if model_config is None:
            model_config = {}
            logger.info("model_config is None. initializing the model with default values.")
        if vocoder_config is None:
            vocoder_config = {}
            logger.info("vocoder_config is None. initializing the coarse model with default values.")
        self.model_config = FastSpeech2ConformerConfig(**model_config)
        self.vocoder_config = FastSpeech2ConformerHifiGanConfig(**vocoder_config)
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
