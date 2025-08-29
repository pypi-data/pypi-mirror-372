"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Any, List, Mapping, Optional
from ... import PretrainedConfig, PreTrainedTokenizer
from ...onnx import OnnxConfig, PatchingSpec
from ...utils import TensorType, is_torch_available, logging
logger = logging.get_logger(__name__)
class LayoutLMConfig(PretrainedConfig):
    model_type = "layoutlm"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu",
    hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02,
    layer_norm_eps=1e-12, pad_token_id=0, position_embedding_type="absolute", use_cache=True, max_2d_position_embeddings=1024, **kwargs):
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
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
        self.max_2d_position_embeddings = max_2d_position_embeddings
class LayoutLMOnnxConfig(OnnxConfig):
    def __init__(self, config: PretrainedConfig, task: str = "default", patching_specs: List[PatchingSpec] = None):
        super().__init__(config, task=task, patching_specs=patching_specs)
        self.max_2d_positions = config.max_2d_position_embeddings - 1
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        return OrderedDict([("input_ids", {0: "batch", 1: "sequence"}), ("bbox", {0: "batch", 1: "sequence"}), ("attention_mask", {0: "batch", 1: "sequence"}),
        ("token_type_ids", {0: "batch", 1: "sequence"})])
    def generate_dummy_inputs(self, tokenizer: PreTrainedTokenizer, batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional[TensorType] = None) -> Mapping[str, Any]:
        input_dict = super().generate_dummy_inputs(tokenizer, batch_size=batch_size, seq_length=seq_length, is_pair=is_pair, framework=framework)
        box = [48, 84, 73, 128]
        if not framework == TensorType.PYTORCH: raise NotImplementedError("Exporting LayoutLM to ONNX is currently only supported for PyTorch.")
        if not is_torch_available(): raise ValueError("Cannot generate dummy inputs without PyTorch installed.")
        import torch
        batch_size, seq_length = input_dict["input_ids"].shape
        input_dict["bbox"] = torch.tensor([*[box] * seq_length]).tile(batch_size, 1, 1)
        return input_dict
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
