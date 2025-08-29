"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig
from ...utils import TensorType, logging
if TYPE_CHECKING:
    from ...onnx.config import PatchingSpec
    from ...tokenization_utils_base import PreTrainedTokenizerBase
logger = logging.get_logger(__name__)
class LongformerConfig(PretrainedConfig):
    model_type = "longformer"
    def __init__(self, attention_window: Union[List[int], int] = 512, sep_token_id: int = 2, pad_token_id: int = 1, bos_token_id: int = 0, eos_token_id: int = 2,
    vocab_size: int = 30522, hidden_size: int = 768, num_hidden_layers: int = 12, num_attention_heads: int = 12, intermediate_size: int = 3072, hidden_act: str = "gelu",
    hidden_dropout_prob: float = 0.1, attention_probs_dropout_prob: float = 0.1, max_position_embeddings: int = 512, type_vocab_size: int = 2, initializer_range: float = 0.02,
    layer_norm_eps: float = 1e-12, onnx_export: bool = False, **kwargs):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        self.attention_window = attention_window
        self.sep_token_id = sep_token_id
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
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
        self.onnx_export = onnx_export
class LongformerOnnxConfig(OnnxConfig):
    def __init__(self, config: "PretrainedConfig", task: str = "default", patching_specs: "List[PatchingSpec]" = None):
        super().__init__(config, task, patching_specs)
        config.onnx_export = True
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        if self.task == "multiple-choice": dynamic_axis = {0: "batch", 1: "choice", 2: "sequence"}
        else: dynamic_axis = {0: "batch", 1: "sequence"}
        return OrderedDict([("input_ids", dynamic_axis), ("attention_mask", dynamic_axis), ("global_attention_mask", dynamic_axis)])
    @property
    def outputs(self) -> Mapping[str, Mapping[int, str]]:
        outputs = super().outputs
        if self.task == "default": outputs["pooler_output"] = {0: "batch"}
        return outputs
    @property
    def atol_for_validation(self) -> float: return 1e-4
    @property
    def default_onnx_opset(self) -> int: return max(super().default_onnx_opset, 14)
    def generate_dummy_inputs(self, tokenizer: "PreTrainedTokenizerBase", batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional[TensorType] = None) -> Mapping[str, Any]:
        inputs = super().generate_dummy_inputs(preprocessor=tokenizer, batch_size=batch_size, seq_length=seq_length, is_pair=is_pair, framework=framework)
        import torch
        inputs["global_attention_mask"] = torch.zeros_like(inputs["input_ids"])
        inputs["global_attention_mask"][:, ::2] = 1
        return inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
