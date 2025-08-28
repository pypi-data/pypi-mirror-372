"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import functools
import operator
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class SpeechT5Config(PretrainedConfig):
    model_type = "speecht5"
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "num_hidden_layers": "encoder_layers"}
    def __init__(self, vocab_size=81, hidden_size=768, encoder_layers=12, encoder_attention_heads=12, encoder_ffn_dim=3072, encoder_layerdrop=0.1, decoder_layers=6,
    decoder_ffn_dim=3072, decoder_attention_heads=12, decoder_layerdrop=0.1, hidden_act="gelu", positional_dropout=0.1, hidden_dropout=0.1, attention_dropout=0.1,
    activation_dropout=0.1, initializer_range=0.02, layer_norm_eps=1e-5, scale_embedding=False, feat_extract_norm="group", feat_proj_dropout=0.0, feat_extract_activation="gelu",
    conv_dim=(512, 512, 512, 512, 512, 512, 512), conv_stride=(5, 2, 2, 2, 2, 2, 2), conv_kernel=(10, 3, 3, 3, 3, 2, 2), conv_bias=False, num_conv_pos_embeddings=128,
    num_conv_pos_embedding_groups=16, apply_spec_augment=True, mask_time_prob=0.05, mask_time_length=10, mask_time_min_masks=2, mask_feature_prob=0.0, mask_feature_length=10,
    mask_feature_min_masks=0, pad_token_id=1, bos_token_id=0, eos_token_id=2, decoder_start_token_id=2, num_mel_bins=80, speech_decoder_prenet_layers=2, speech_decoder_prenet_units=256,
    speech_decoder_prenet_dropout=0.5, speaker_embedding_dim=512, speech_decoder_postnet_layers=5, speech_decoder_postnet_units=256, speech_decoder_postnet_kernel=5,
    speech_decoder_postnet_dropout=0.5, reduction_factor=2, max_speech_positions=4000, max_text_positions=450, encoder_max_relative_position=160, use_guided_attention_loss=True,
    guided_attention_loss_num_heads=2, guided_attention_loss_sigma=0.4, guided_attention_loss_scale=10.0, use_cache=True, is_encoder_decoder=True, **kwargs):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.encoder_layers = encoder_layers
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_attention_heads = encoder_attention_heads
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layers = decoder_layers
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_attention_heads = decoder_attention_heads
        self.decoder_layerdrop = decoder_layerdrop
        self.hidden_act = hidden_act
        self.positional_dropout = positional_dropout
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.scale_embedding = scale_embedding
        self.feat_extract_norm = feat_extract_norm
        self.feat_proj_dropout = feat_proj_dropout
        self.feat_extract_activation = feat_extract_activation
        self.conv_dim = list(conv_dim)
        self.conv_stride = list(conv_stride)
        self.conv_kernel = list(conv_kernel)
        self.conv_bias = conv_bias
        self.num_conv_pos_embeddings = num_conv_pos_embeddings
        self.num_conv_pos_embedding_groups = num_conv_pos_embedding_groups
        self.num_feat_extract_layers = len(self.conv_dim)
        if ((len(self.conv_stride) != self.num_feat_extract_layers) or (len(self.conv_kernel) != self.num_feat_extract_layers) or (len(self.conv_dim) != self.num_feat_extract_layers)): raise ValueError(f"Configuration for convolutional layers is incorrect. It is required that `len(config.conv_dim)` == `len(config.conv_stride)` == `len(config.conv_kernel)`, but is `len(config.conv_dim) = {len(self.conv_dim)}`, `len(config.conv_stride) = {len(self.conv_stride)}`, `len(config.conv_kernel) = {len(self.conv_kernel)}`.")
        self.apply_spec_augment = apply_spec_augment
        self.mask_time_prob = mask_time_prob
        self.mask_time_length = mask_time_length
        self.mask_time_min_masks = mask_time_min_masks
        self.mask_feature_prob = mask_feature_prob
        self.mask_feature_length = mask_feature_length
        self.mask_feature_min_masks = mask_feature_min_masks
        self.num_mel_bins = num_mel_bins
        self.speech_decoder_prenet_layers = speech_decoder_prenet_layers
        self.speech_decoder_prenet_units = speech_decoder_prenet_units
        self.speech_decoder_prenet_dropout = speech_decoder_prenet_dropout
        self.speaker_embedding_dim = speaker_embedding_dim
        self.speech_decoder_postnet_layers = speech_decoder_postnet_layers
        self.speech_decoder_postnet_units = speech_decoder_postnet_units
        self.speech_decoder_postnet_kernel = speech_decoder_postnet_kernel
        self.speech_decoder_postnet_dropout = speech_decoder_postnet_dropout
        self.reduction_factor = reduction_factor
        self.max_speech_positions = max_speech_positions
        self.max_text_positions = max_text_positions
        self.encoder_max_relative_position = encoder_max_relative_position
        self.use_guided_attention_loss = use_guided_attention_loss
        self.guided_attention_loss_num_heads = guided_attention_loss_num_heads
        self.guided_attention_loss_sigma = guided_attention_loss_sigma
        self.guided_attention_loss_scale = guided_attention_loss_scale
        self.use_cache = use_cache
        self.is_encoder_decoder = is_encoder_decoder
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, decoder_start_token_id=decoder_start_token_id, **kwargs)
    def inputs_to_logits_ratio(self): return functools.reduce(operator.mul, self.conv_stride, 1)
class SpeechT5HifiGanConfig(PretrainedConfig):
    model_type = "hifigan"
    def __init__(self, model_in_dim=80, sampling_rate=16000, upsample_initial_channel=512, upsample_rates=[4, 4, 4, 4], upsample_kernel_sizes=[8, 8, 8, 8],
    resblock_kernel_sizes=[3, 7, 11], resblock_dilation_sizes=[[1, 3, 5], [1, 3, 5], [1, 3, 5]], initializer_range=0.01, leaky_relu_slope=0.1,
    normalize_before=True, **kwargs):
        self.model_in_dim = model_in_dim
        self.sampling_rate = sampling_rate
        self.upsample_initial_channel = upsample_initial_channel
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.initializer_range = initializer_range
        self.leaky_relu_slope = leaky_relu_slope
        self.normalize_before = normalize_before
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
