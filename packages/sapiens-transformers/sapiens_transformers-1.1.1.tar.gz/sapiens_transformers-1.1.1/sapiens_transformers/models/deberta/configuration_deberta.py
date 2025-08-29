"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import logging
if TYPE_CHECKING: from ... import FeatureExtractionMixin, PreTrainedTokenizerBase, TensorType
logger = logging.get_logger(__name__)
class DebertaConfig(PretrainedConfig):
    model_type = "deberta"
    def __init__(self, vocab_size=50265, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=0, initializer_range=0.02, layer_norm_eps=1e-7, relative_attention=False, max_relative_positions=-1,
    pad_token_id=0, position_biased_input=True, pos_att_type=None, pooler_dropout=0, pooler_hidden_act="gelu", **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.relative_attention = relative_attention
        self.max_relative_positions = max_relative_positions
        self.pad_token_id = pad_token_id
        self.position_biased_input = position_biased_input
        if isinstance(pos_att_type, str): pos_att_type = [x.strip() for x in pos_att_type.lower().split("|")]
        self.pos_att_type = pos_att_type
        self.vocab_size = vocab_size
        self.layer_norm_eps = layer_norm_eps
        self.pooler_hidden_size = kwargs.get("pooler_hidden_size", hidden_size)
        self.pooler_dropout = pooler_dropout
        self.pooler_hidden_act = pooler_hidden_act
class DebertaOnnxConfig(OnnxConfig):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        if self._config.type_vocab_size > 0: return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis), ("token_type_ids", dynamic_axis)])
        else: return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis)])
    @property
    def default_onnx_opset(self) -> int: return 12
    def generate_dummy_inputs(self, preprocessor: Union["PreTrainedTokenizerBase", "FeatureExtractionMixin"], batch_size: int = -1, seq_length: int = -1, num_choices: int = -1,
    is_pair: bool = False, framework: Optional["TensorType"] = None, num_channels: int = 3, image_width: int = 40, image_height: int = 40, tokenizer: "PreTrainedTokenizerBase" = None) -> Mapping[str, Any]:
        dummy_inputs = super().generate_dummy_inputs(preprocessor=preprocessor, framework=framework)
        if self._config.type_vocab_size == 0 and "token_type_ids" in dummy_inputs: del dummy_inputs["token_type_ids"]
        return dummy_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
