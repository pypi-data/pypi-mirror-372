"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Any, List, Mapping, Optional
from ... import PreTrainedTokenizer, TensorType, is_torch_available
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfigWithPast, PatchingSpec
from ...utils import logging
logger = logging.get_logger(__name__)
class GPTJConfig(PretrainedConfig):
    model_type = "gptj"
    attribute_map = {'max_position_embeddings': 'n_positions', 'hidden_size': 'n_embd', 'num_attention_heads': 'n_head', 'num_hidden_layers': 'n_layer'}
    def __init__(self, vocab_size=50400, n_positions=2048, n_embd=4096, n_layer=28, n_head=16, rotary_dim=64, n_inner=None, activation_function="gelu_new",
    resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0, layer_norm_epsilon=1e-5, initializer_range=0.02, use_cache=True, bos_token_id=50256, eos_token_id=50256,
    tie_word_embeddings=False, **kwargs):
        self.vocab_size = vocab_size
        self.n_positions = n_positions
        self.n_embd = n_embd
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_inner = n_inner
        self.rotary_dim = rotary_dim
        self.activation_function = activation_function
        self.resid_pdrop = resid_pdrop
        self.embd_pdrop = embd_pdrop
        self.attn_pdrop = attn_pdrop
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.use_cache = use_cache
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, tie_word_embeddings=tie_word_embeddings, **kwargs)
class GPTJOnnxConfig(OnnxConfigWithPast):
    def __init__(self, config: PretrainedConfig, task: str = "default", patching_specs: List[PatchingSpec] = None, use_past: bool = False):
        super().__init__(config, task=task, patching_specs=patching_specs, use_past=use_past)
        if not getattr(self._config, "pad_token_id", None): self._config.pad_token_id = 0
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict({"input_ids": {0: "batch", 1: "sequence"}})
        if self.use_past:
            self.fill_with_past_key_values_(common_inputs, direction="inputs")
            common_inputs["attention_mask"] = {0: "batch", 1: "past_sequence + sequence"}
        else: common_inputs["attention_mask"] = {0: "batch", 1: "sequence"}
        return common_inputs
    @property
    def num_layers(self) -> int: return self._config.n_layer
    @property
    def num_attention_heads(self) -> int: return self._config.n_head
    def generate_dummy_inputs(self, tokenizer: PreTrainedTokenizer, batch_size: int = -1, seq_length: int = -1, is_pair: bool = False, framework: Optional[TensorType] = None) -> Mapping[str, Any]:
        common_inputs = super(OnnxConfigWithPast, self).generate_dummy_inputs(tokenizer, batch_size=batch_size, seq_length=seq_length, is_pair=is_pair, framework=framework)
        ordered_inputs = OrderedDict({"input_ids": common_inputs["input_ids"]})
        if self.use_past:
            if not is_torch_available(): raise ValueError("Cannot generate dummy past_keys inputs without PyTorch installed.")
            else:
                import torch
                batch, seqlen = common_inputs["input_ids"].shape
                past_key_values_length = seqlen + 2
                past_shape = (batch, self.num_attention_heads, past_key_values_length, self._config.hidden_size // self.num_attention_heads)
                ordered_inputs["past_key_values"] = [(torch.zeros(past_shape), torch.zeros(past_shape)) for _ in range(self.num_layers)]
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
