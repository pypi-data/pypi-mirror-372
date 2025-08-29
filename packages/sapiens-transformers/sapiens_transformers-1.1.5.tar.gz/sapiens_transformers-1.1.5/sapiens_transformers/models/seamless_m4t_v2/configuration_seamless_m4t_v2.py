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
class SeamlessM4Tv2Config(PretrainedConfig):
    model_type = "seamless_m4t_v2"
    def __init__(self, vocab_size=256102, t2u_vocab_size=10082, char_vocab_size=10943, hidden_size=1024, initializer_range=0.02, layer_norm_eps=1e-5, use_cache=True,
    max_position_embeddings=4096, is_encoder_decoder=True, encoder_layerdrop=0.05, decoder_layerdrop=0.05, activation_function="relu", dropout=0.1, attention_dropout=0.1,
    activation_dropout=0.0, scale_embedding=True, encoder_layers=24, encoder_ffn_dim=8192, encoder_attention_heads=16, decoder_layers=24, decoder_ffn_dim=8192,
    decoder_attention_heads=16, decoder_start_token_id=3, max_new_tokens=256, pad_token_id=0, bos_token_id=2, eos_token_id=3, speech_encoder_layers=24, speech_encoder_attention_heads=16,
    speech_encoder_intermediate_size=4096, speech_encoder_hidden_act="swish", speech_encoder_dropout=0.0, add_adapter=True, speech_encoder_layerdrop=0.1,
    feature_projection_input_dim=160, adaptor_kernel_size=8, adaptor_stride=8, adaptor_dropout=0.1, num_adapter_layers=1, position_embeddings_type="relative_key",
    conv_depthwise_kernel_size=31, left_max_position_embeddings=64, right_max_position_embeddings=8, speech_encoder_chunk_size=20000, speech_encoder_left_chunk_num=128,
    t2u_bos_token_id=0, t2u_pad_token_id=1, t2u_eos_token_id=2, t2u_encoder_layers=6, t2u_encoder_ffn_dim=8192, t2u_encoder_attention_heads=16, t2u_decoder_layers=6,
    t2u_decoder_ffn_dim=8192, t2u_decoder_attention_heads=16, t2u_max_position_embeddings=4096, t2u_variance_predictor_embed_dim=1024, t2u_variance_predictor_hidden_dim=256,
    t2u_variance_predictor_kernel_size=3, t2u_variance_pred_dropout=0.5, sampling_rate=16000, upsample_initial_channel=512, upsample_rates=[5, 4, 4, 2, 2],
    upsample_kernel_sizes=[11, 8, 8, 4, 4], resblock_kernel_sizes=[3, 7, 11], resblock_dilation_sizes=[[1, 3, 5], [1, 3, 5], [1, 3, 5]], leaky_relu_slope=0.1,
    unit_hifi_gan_vocab_size=10000, unit_embed_dim=1280, lang_embed_dim=256, spkr_embed_dim=256, vocoder_num_langs=36, vocoder_num_spkrs=200, variance_predictor_kernel_size=3,
    var_pred_dropout=0.5, vocoder_offset=4, **kwargs):
        self.vocab_size = vocab_size
        self.t2u_vocab_size = t2u_vocab_size
        self.char_vocab_size = char_vocab_size
        self.hidden_size = hidden_size
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.max_position_embeddings = max_position_embeddings
        self.use_cache = use_cache
        self.max_new_tokens = max_new_tokens
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.activation_function = activation_function
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.scale_embedding = scale_embedding
        self.num_attention_heads = decoder_attention_heads
        self.num_hidden_layers = decoder_layers
        self.encoder_layers = encoder_layers
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_layers = decoder_layers
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_attention_heads = decoder_attention_heads
        self.speech_encoder_layers = speech_encoder_layers
        self.speech_encoder_hidden_act = speech_encoder_hidden_act
        self.speech_encoder_dropout = speech_encoder_dropout
        self.speech_encoder_attention_heads = speech_encoder_attention_heads
        self.speech_encoder_layerdrop = speech_encoder_layerdrop
        self.speech_encoder_intermediate_size = speech_encoder_intermediate_size
        self.feature_projection_input_dim = feature_projection_input_dim
        self.adaptor_kernel_size = adaptor_kernel_size
        self.adaptor_stride = adaptor_stride
        self.adaptor_dropout = adaptor_dropout
        self.num_adapter_layers = num_adapter_layers
        self.position_embeddings_type = position_embeddings_type
        self.conv_depthwise_kernel_size = conv_depthwise_kernel_size
        self.add_adapter = add_adapter
        self.left_max_position_embeddings = left_max_position_embeddings
        self.right_max_position_embeddings = right_max_position_embeddings
        self.speech_encoder_chunk_size = speech_encoder_chunk_size
        self.speech_encoder_left_chunk_num = speech_encoder_left_chunk_num
        self.t2u_bos_token_id = t2u_bos_token_id
        self.t2u_pad_token_id = t2u_pad_token_id
        self.t2u_eos_token_id = t2u_eos_token_id
        self.t2u_encoder_layers = t2u_encoder_layers
        self.t2u_encoder_ffn_dim = t2u_encoder_ffn_dim
        self.t2u_encoder_attention_heads = t2u_encoder_attention_heads
        self.t2u_decoder_layers = t2u_decoder_layers
        self.t2u_decoder_ffn_dim = t2u_decoder_ffn_dim
        self.t2u_decoder_attention_heads = t2u_decoder_attention_heads
        self.t2u_max_position_embeddings = t2u_max_position_embeddings
        self.t2u_variance_predictor_embed_dim = t2u_variance_predictor_embed_dim
        self.t2u_variance_predictor_hidden_dim = t2u_variance_predictor_hidden_dim
        self.t2u_variance_predictor_kernel_size = t2u_variance_predictor_kernel_size
        self.t2u_variance_pred_dropout = t2u_variance_pred_dropout
        self.sampling_rate = sampling_rate
        self.upsample_initial_channel = upsample_initial_channel
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.leaky_relu_slope = leaky_relu_slope
        self.unit_hifi_gan_vocab_size = unit_hifi_gan_vocab_size
        self.unit_embed_dim = unit_embed_dim
        self.lang_embed_dim = lang_embed_dim
        self.spkr_embed_dim = spkr_embed_dim
        self.vocoder_num_langs = vocoder_num_langs
        self.vocoder_num_spkrs = vocoder_num_spkrs
        self.variance_predictor_kernel_size = variance_predictor_kernel_size
        self.var_pred_dropout = var_pred_dropout
        self.vocoder_offset = vocoder_offset
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, decoder_start_token_id=decoder_start_token_id,
        is_encoder_decoder=is_encoder_decoder, max_position_embeddings=max_position_embeddings, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
