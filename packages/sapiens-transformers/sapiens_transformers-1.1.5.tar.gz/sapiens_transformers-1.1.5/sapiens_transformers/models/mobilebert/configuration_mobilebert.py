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
from ...onnx import OnnxConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class MobileBertConfig(PretrainedConfig):
    model_type = "mobilebert"
    def __init__(self, vocab_size=30522, hidden_size=512, num_hidden_layers=24, num_attention_heads=4, intermediate_size=512, hidden_act="relu", hidden_dropout_prob=0.0,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02, layer_norm_eps=1e-12, pad_token_id=0, embedding_size=128,
    trigram_input=True, use_bottleneck=True, intra_bottleneck_size=128, use_bottleneck_attention=False, key_query_shared_bottleneck=True, num_feedforward_networks=4,
    normalization_type="no_norm", classifier_activation=True, classifier_dropout=None, **kwargs):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.embedding_size = embedding_size
        self.trigram_input = trigram_input
        self.use_bottleneck = use_bottleneck
        self.intra_bottleneck_size = intra_bottleneck_size
        self.use_bottleneck_attention = use_bottleneck_attention
        self.key_query_shared_bottleneck = key_query_shared_bottleneck
        self.num_feedforward_networks = num_feedforward_networks
        self.normalization_type = normalization_type
        self.classifier_activation = classifier_activation
        if self.use_bottleneck: self.true_hidden_size = intra_bottleneck_size
        else: self.true_hidden_size = hidden_size
        self.classifier_dropout = classifier_dropout
class MobileBertOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis), ("token_type_ids", dynamic_axis)])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
