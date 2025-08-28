"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Mapping
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfigWithPast
from ...utils import logging
logger = logging.get_logger(__name__)
class PLBartConfig(PretrainedConfig):
    model_type = "plbart"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=50005, max_position_embeddings=1024, encoder_layers=6, encoder_ffn_dim=3072, encoder_attention_heads=12, decoder_layers=6,
    decoder_ffn_dim=3072, decoder_attention_heads=12, encoder_layerdrop=0.0, decoder_layerdrop=0.0, use_cache=True, is_encoder_decoder=True, activation_function="gelu",
    d_model=768, dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, init_std=0.02, classifier_dropout=0.0, scale_embedding=True, pad_token_id=1, bos_token_id=0,
    eos_token_id=2, forced_eos_token_id=2, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
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
        self.classifier_dropout = classifier_dropout
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, forced_eos_token_id=forced_eos_token_id, **kwargs)
class PLBartOnnxConfig(OnnxConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]: return OrderedDict([("input_ids", {0: "batch", 1: "sequence"}), ("attention_mask", {0: "batch", 1: "sequence"})])
    @property
    def outputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.use_past: return OrderedDict([("last_hidden_state", {0: "batch", 1: "sequence"}), ("past_keys", {0: "batch", 2: "sequence"}), ("encoder_last_hidden_state", {0: "batch", 1: "sequence"})])
        else: return OrderedDict([("last_hidden_state", {0: "batch", 1: "sequence"}), ("encoder_last_hidden_state", {0: "batch", 1: "sequence"})])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
