"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import OrderedDict
from typing import Any, Mapping, Optional
from ... import PreTrainedTokenizer
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast
from ...onnx.utils import compute_effective_axis_dimension
from ...utils import TensorType, is_torch_available, logging
logger = logging.get_logger(__name__)
class M2M100Config(PretrainedConfig):
    model_type = "m2m_100"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=128112, max_position_embeddings=1024, encoder_layers=12, encoder_ffn_dim=4096, encoder_attention_heads=16, decoder_layers=12,
    decoder_ffn_dim=4096, decoder_attention_heads=16, encoder_layerdrop=0.05, decoder_layerdrop=0.05, use_cache=True, is_encoder_decoder=True, activation_function="relu",
    d_model=1024, dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, init_std=0.02, decoder_start_token_id=2, scale_embedding=True, pad_token_id=1,
    bos_token_id=0, eos_token_id=2, **kwargs):
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
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder,
        decoder_start_token_id=decoder_start_token_id, **kwargs)
class M2M100OnnxConfig(OnnxSeq2SeqConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict([("input_ids", {0: "batch", 1: "encoder_sequence"}), ("attention_mask", {0: "batch", 1: "encoder_sequence"})])
        if self.use_past:
            common_inputs["decoder_input_ids"] = {0: "batch"}
            common_inputs["decoder_attention_mask"] = {0: "batch", 1: "past_decoder_sequence + sequence"}
        else:
            common_inputs["decoder_input_ids"] = {0: "batch", 1: "decoder_sequence"}
            common_inputs["decoder_attention_mask"] = {0: "batch", 1: "decoder_sequence"}
        if self.use_past: self.fill_with_past_key_values_(common_inputs, direction="inputs")
        return common_inputs
    def _generate_dummy_inputs_for_sequence_classification_and_question_answering(self, tokenizer: PreTrainedTokenizer, batch_size: int = -1, seq_length: int = -1,
    is_pair: bool = False, framework: Optional[TensorType] = None) -> Mapping[str, Any]:
        batch_size = compute_effective_axis_dimension(batch_size, fixed_dimension=OnnxConfig.default_fixed_batch, num_token_to_add=0)
        token_to_add = tokenizer.num_special_tokens_to_add(is_pair)
        seq_length = compute_effective_axis_dimension(seq_length, fixed_dimension=OnnxConfig.default_fixed_sequence, num_token_to_add=token_to_add)
        dummy_input = [" ".join([tokenizer.unk_token]) * seq_length] * batch_size
        common_inputs = dict(tokenizer(dummy_input, return_tensors=framework))
        return common_inputs
    def _generate_dummy_inputs_for_default_and_seq2seq_lm(self, tokenizer: PreTrainedTokenizer, batch_size: int = -1, seq_length: int = -1, is_pair: bool = False,
    framework: Optional[TensorType] = None) -> Mapping[str, Any]:
        encoder_inputs = self._generate_dummy_inputs_for_sequence_classification_and_question_answering(tokenizer, batch_size, seq_length, is_pair, framework)
        decoder_seq_length = seq_length if not self.use_past else 1
        decoder_inputs = self._generate_dummy_inputs_for_sequence_classification_and_question_answering(tokenizer, batch_size, decoder_seq_length, is_pair, framework)
        decoder_inputs = {f"decoder_{name}": tensor for name, tensor in decoder_inputs.items()}
        common_inputs = dict(**encoder_inputs, **decoder_inputs)
        if self.use_past:
            if not is_torch_available(): raise ValueError("Cannot generate dummy past_keys inputs without PyTorch installed.")
            else: import torch
            batch, encoder_seq_length = common_inputs["input_ids"].shape
            decoder_seq_length = common_inputs["decoder_input_ids"].shape[1]
            num_encoder_attention_heads, num_decoder_attention_heads = self.num_attention_heads
            encoder_shape = (batch, num_encoder_attention_heads, encoder_seq_length, self._config.hidden_size // num_encoder_attention_heads)
            decoder_past_length = decoder_seq_length + 3
            decoder_shape = (batch, num_decoder_attention_heads, decoder_past_length, self._config.hidden_size // num_decoder_attention_heads)
            common_inputs["decoder_attention_mask"] = torch.cat([common_inputs["decoder_attention_mask"], torch.ones(batch, decoder_past_length)], dim=1)
            common_inputs["past_key_values"] = []
            num_encoder_layers, num_decoder_layers = self.num_layers
            min_num_layers = min(num_encoder_layers, num_decoder_layers)
            max_num_layers = max(num_encoder_layers, num_decoder_layers) - min_num_layers
            remaining_side_name = "encoder" if num_encoder_layers > num_decoder_layers else "decoder"
            for _ in range(min_num_layers): common_inputs["past_key_values"].append((torch.zeros(decoder_shape), torch.zeros(decoder_shape), torch.zeros(encoder_shape), torch.zeros(encoder_shape)))
            shape = encoder_shape if remaining_side_name == "encoder" else decoder_shape
            for _ in range(min_num_layers, max_num_layers): common_inputs["past_key_values"].append((torch.zeros(shape), torch.zeros(shape)))
        return common_inputs
    generate_dummy_inputs = _generate_dummy_inputs_for_default_and_seq2seq_lm
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
