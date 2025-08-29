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
class Pop2PianoConfig(PretrainedConfig):
    model_type = "pop2piano"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(self, vocab_size=2400, composer_vocab_size=21, d_model=512, d_kv=64, d_ff=2048, num_layers=6, num_decoder_layers=None, num_heads=8, relative_attention_num_buckets=32,
    relative_attention_max_distance=128, dropout_rate=0.1, layer_norm_epsilon=1e-6, initializer_factor=1.0, feed_forward_proj="gated-gelu", is_encoder_decoder=True,
    use_cache=True, pad_token_id=0, eos_token_id=1, dense_act_fn="relu", **kwargs):
        self.vocab_size = vocab_size
        self.composer_vocab_size = composer_vocab_size
        self.d_model = d_model
        self.d_kv = d_kv
        self.d_ff = d_ff
        self.num_layers = num_layers
        self.num_decoder_layers = num_decoder_layers if num_decoder_layers is not None else self.num_layers
        self.num_heads = num_heads
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.dropout_rate = dropout_rate
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_factor = initializer_factor
        self.feed_forward_proj = feed_forward_proj
        self.use_cache = use_cache
        self.dense_act_fn = dense_act_fn
        self.is_gated_act = self.feed_forward_proj.split("-")[0] == "gated"
        self.hidden_size = self.d_model
        self.num_attention_heads = num_heads
        self.num_hidden_layers = num_layers
        super().__init__(pad_token_id=pad_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
