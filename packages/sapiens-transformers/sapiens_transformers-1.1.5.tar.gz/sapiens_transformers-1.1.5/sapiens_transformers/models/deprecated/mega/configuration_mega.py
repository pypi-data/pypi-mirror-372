"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Mapping
from ....configuration_utils import PretrainedConfig
from ....onnx import OnnxConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class MegaConfig(PretrainedConfig):
    model_type = "mega"
    def __init__(self, vocab_size=30522, hidden_size=128, num_hidden_layers=4, intermediate_size=256, ema_projection_size=16, bidirectional=True, shared_representation_size=64,
    use_chunking=False, chunk_size=-1, truncation=None, normalize_before_mega=True, normalization_type="scalenorm", norm_affine=True, activation="silu", attention_activation="softmax",
    dropout_prob=0.1, hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.1, use_feature_dropout=False, use_normalized_ffn=True, nffn_hidden_size=256, normalize_before_ffn=True,
    nffn_activation_dropout_prob=0.1, max_positions=2048, add_token_type_embeddings=False, type_vocab_size=2, initializer_range=0.02, ema_delta_alpha_range=0.2, ema_beta_range=0.02,
    ema_gamma_omega_range=1.0, pad_token_id=1, bos_token_id=0, eos_token_id=2, relative_positional_bias="rotary", classifier_dropout=None, use_cache=True, add_lm_hidden_dense_layer=True, **kwargs):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.activation = activation
        self.attention_activation = attention_activation
        self.intermediate_size = intermediate_size
        self.ema_projection_size = ema_projection_size
        self.bidirectional = bidirectional
        self.shared_representation_size = shared_representation_size
        self.use_chunking = use_chunking
        self.chunk_size = chunk_size
        self.truncation = truncation
        self.normalize_before_mega = normalize_before_mega
        self.normalization_type = normalization_type
        self.norm_affine = norm_affine
        self.dropout_prob = dropout_prob
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.use_feature_dropout = use_feature_dropout
        self.use_normalized_ffn = use_normalized_ffn
        self.nffn_hidden_size = nffn_hidden_size
        self.normalize_before_ffn = normalize_before_ffn
        self.nffn_activation_dropout_prob = nffn_activation_dropout_prob
        self.max_positions = max_positions
        self.add_token_type_embeddings = add_token_type_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.ema_delta_alpha_range = ema_delta_alpha_range
        self.ema_beta_range = ema_beta_range
        self.ema_gamma_omega_range = ema_gamma_omega_range
        self.relative_positional_bias = relative_positional_bias
        self.use_cache = use_cache
        self.classifier_dropout = classifier_dropout
        self.add_lm_hidden_dense_layer = add_lm_hidden_dense_layer
        self.num_attention_heads = 1
class MegaOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis)])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
