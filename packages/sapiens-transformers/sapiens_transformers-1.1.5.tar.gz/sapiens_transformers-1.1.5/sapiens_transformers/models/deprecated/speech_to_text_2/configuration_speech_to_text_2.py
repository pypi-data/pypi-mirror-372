"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class Speech2Text2Config(PretrainedConfig):
    model_type = "speech_to_text_2"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "decoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=10000, decoder_layers=6, decoder_ffn_dim=2048, decoder_attention_heads=4, decoder_layerdrop=0.0, use_cache=True, activation_function="relu",
    d_model=256, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, decoder_start_token_id=2, scale_embedding=True, pad_token_id=1, bos_token_id=0,
    eos_token_id=2, max_target_positions=1024, **kwargs):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.decoder_layerdrop = decoder_layerdrop
        self.use_cache = use_cache
        self.num_hidden_layers = decoder_layers
        self.scale_embedding = scale_embedding
        self.max_target_positions = max_target_positions
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, decoder_start_token_id=decoder_start_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
