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
class Speech2TextConfig(PretrainedConfig):
    model_type = "speech_to_text"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=10000, encoder_layers=12, encoder_ffn_dim=2048, encoder_attention_heads=4, decoder_layers=6, decoder_ffn_dim=2048, decoder_attention_heads=4,
    encoder_layerdrop=0.0, decoder_layerdrop=0.0, use_cache=True, is_encoder_decoder=True, activation_function="relu", d_model=256, dropout=0.1, attention_dropout=0.0,
    activation_dropout=0.0, init_std=0.02, decoder_start_token_id=2, scale_embedding=True, pad_token_id=1, bos_token_id=0, eos_token_id=2, max_source_positions=6000,
    max_target_positions=1024, num_conv_layers=2, conv_kernel_sizes=(5, 5), conv_channels=1024, input_feat_per_channel=80, input_channels=1, **kwargs):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        self.max_source_positions = max_source_positions
        self.max_target_positions = max_target_positions
        self.num_conv_layers = num_conv_layers
        self.conv_kernel_sizes = list(conv_kernel_sizes)
        self.conv_channels = conv_channels
        self.input_feat_per_channel = input_feat_per_channel
        self.input_channels = input_channels
        if len(self.conv_kernel_sizes) != self.num_conv_layers: raise ValueError(f"Configuration for convolutional module is incorrect. It is required that `len(config.conv_kernel_sizes)` == `config.num_conv_layers` but is `len(config.conv_kernel_sizes) = {len(self.conv_kernel_sizes)}`, `config.num_conv_layers = {self.num_conv_layers}`.")
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, decoder_start_token_id=decoder_start_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
