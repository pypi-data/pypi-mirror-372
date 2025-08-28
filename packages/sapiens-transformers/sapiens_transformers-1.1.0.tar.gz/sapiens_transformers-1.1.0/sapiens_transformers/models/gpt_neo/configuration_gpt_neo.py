"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Any, Mapping, Optional
from ... import PreTrainedTokenizer, TensorType, is_torch_available
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfigWithPast
from ...utils import logging
logger = logging.get_logger(__name__)
class GPTNeoConfig(PretrainedConfig):
    model_type = "gpt_neo"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "num_heads", "num_hidden_layers": "num_layers"}
    def __init__(self, vocab_size=50257, max_position_embeddings=2048, hidden_size=2048, num_layers=24, attention_types=[[["global", "local"], 12]], num_heads=16, intermediate_size=None,
    window_size=256, activation_function="gelu_new", resid_dropout=0.0, embed_dropout=0.0, attention_dropout=0.0, classifier_dropout=0.1, layer_norm_epsilon=1e-5, initializer_range=0.02,
    use_cache=True, bos_token_id=50256, eos_token_id=50256, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.intermediate_size = intermediate_size
        self.window_size = window_size
        self.activation_function = activation_function
        self.resid_dropout = resid_dropout
        self.embed_dropout = embed_dropout
        self.attention_dropout = attention_dropout
        self.classifier_dropout = classifier_dropout
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.use_cache = use_cache
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        self.attention_types = attention_types
        self.attention_layers = self.expand_attention_types_params(attention_types)
        if len(self.attention_layers) != self.num_layers: raise ValueError(f"Configuration for convolutional module is incorrect. It is required that `len(config.attention_layers)` == `config.num_layers` but is `len(config.attention_layers) = {len(self.attention_layers)}`, `config.num_layers = {self.num_layers}`. `config.attention_layers` is prepared using `config.attention_types`. Please verify the value of `config.attention_types` argument.")
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
    @staticmethod
    def expand_attention_types_params(attention_types):
        attentions = []
        for item in attention_types:
            for _ in range(item[1]): attentions.extend(item[0])
        return attentions
def custom_unfold(input, dimension, size, step):
    import torch
    shape = input.size()
    rank = len(shape)
    sizedim = shape[dimension]
    low_indices = torch.arange(0, sizedim, step)
    min_length = torch.div(sizedim - size, step, rounding_mode="floor") + 1
    indices = torch.arange(size) + low_indices[:min_length][:, None]
    s = [slice(None)] * rank
    s[dimension] = indices
    sliced = input[s]
    perm = list(range(0, rank + 1))
    perm.append(perm.pop(dimension + 1))
    return sliced.permute(perm)
def custom_get_block_length_and_num_blocks(seq_length, window_size):
    import torch
    candidates = torch.arange(1, window_size)
    remainders = torch.remainder(seq_length, candidates)
    divisor_indices = remainders == 0
    divisors = candidates[divisor_indices]
    largest_divisor = torch.max(divisors)
    return largest_divisor, torch.div(seq_length, largest_divisor, rounding_mode="floor")
class GPTNeoOnnxConfig(OnnxConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict({"input_ids": {0: "batch", 1: "sequence"}})
        if self.use_past:
            self.fill_with_past_key_values_(common_inputs, direction="inputs")
            common_inputs["attention_mask"] = {0: "batch", 1: "past_sequence + sequence"}
        else: common_inputs["attention_mask"] = {0: "batch", 1: "sequence"}
        return common_inputs
    @property
    def num_attention_heads(self) -> int: return self._config.num_heads
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
