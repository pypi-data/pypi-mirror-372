"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, List, Mapping, Optional
from packaging import version
if TYPE_CHECKING: from ... import PreTrainedTokenizer, TensorType
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfigWithPast, PatchingSpec
from ...utils import is_torch_available, logging
logger = logging.get_logger(__name__)
class BloomConfig(PretrainedConfig):
    model_type = "bloom"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'num_hidden_layers': 'n_layer', 'num_attention_heads': 'n_head'}
    def __init__(self, vocab_size=250880, hidden_size=64, n_layer=2, n_head=8, layer_norm_epsilon=1e-5, initializer_range=0.02, use_cache=True, bos_token_id=1,
    eos_token_id=2, apply_residual_connection_post_layernorm=False, hidden_dropout=0.0, attention_dropout=0.0, pretraining_tp=1, slow_but_exact=False, **kwargs):
        self.vocab_size = vocab_size
        n_embed = kwargs.pop("n_embed", None)
        self.hidden_size = hidden_size if n_embed is None else n_embed
        self.n_layer = n_layer
        self.n_head = n_head
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.use_cache = use_cache
        self.pretraining_tp = pretraining_tp
        self.apply_residual_connection_post_layernorm = apply_residual_connection_post_layernorm
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        self.slow_but_exact = slow_but_exact
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
class BloomOnnxConfig(OnnxConfigWithPast):
    torch_onnx_minimum_version = version.parse("1.12")
    def __init__(self, config: PretrainedConfig, task: str = "default", patching_specs: List[PatchingSpec] = None, use_past: bool = False):
        super().__init__(config, task=task, patching_specs=patching_specs, use_past=use_past)
        if not getattr(self._config, "pad_token_id", None): self._config.pad_token_id = 0
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict({"input_ids": {0: "batch", 1: "sequence"}})
        if self.use_past:
            self.fill_with_past_key_values_(common_inputs, direction="inputs", inverted_values_shape=True)
            common_inputs["attention_mask"] = {0: "batch", 1: "past_sequence + sequence"}
        else: common_inputs["attention_mask"] = {0: "batch", 1: "sequence"}
        return common_inputs
    @property
    def num_layers(self) -> int: return self._config.n_layer
    @property
    def num_attention_heads(self) -> int: return self._config.n_head
    @property
    def atol_for_validation(self) -> float: return 1e-3
    def generate_dummy_inputs(self, tokenizer: "PreTrainedTokenizer", batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional["TensorType"] = None) -> Mapping[str, Any]:
        common_inputs = super(OnnxConfigWithPast, self).generate_dummy_inputs(tokenizer, batch_size=batch_size, seq_length=seq_length, is_pair=is_pair, framework=framework)
        ordered_inputs = OrderedDict({"input_ids": common_inputs["input_ids"]})
        if self.use_past:
            if not is_torch_available(): raise ValueError("Cannot generate dummy past_keys inputs without PyTorch installed.")
            else:
                import torch
                batch, seqlen = common_inputs["input_ids"].shape
                past_key_values_length = seqlen + 2
                head_dim = self._config.hidden_size // self.num_attention_heads
                past_key_shape = (batch * self.num_attention_heads, head_dim, past_key_values_length)
                past_value_shape = (batch * self.num_attention_heads, past_key_values_length, head_dim)
                ordered_inputs["past_key_values"] = [(torch.zeros(past_key_shape), torch.zeros(past_value_shape)) for _ in range(self.num_layers)]
        ordered_inputs["attention_mask"] = common_inputs["attention_mask"]
        if self.use_past:
            mask_dtype = ordered_inputs["attention_mask"].dtype
            ordered_inputs["attention_mask"] = torch.cat([ordered_inputs["attention_mask"], torch.ones(batch, past_key_values_length, dtype=mask_dtype)], dim=1)
        return ordered_inputs
    @property
    def default_onnx_opset(self) -> int: return 13
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
