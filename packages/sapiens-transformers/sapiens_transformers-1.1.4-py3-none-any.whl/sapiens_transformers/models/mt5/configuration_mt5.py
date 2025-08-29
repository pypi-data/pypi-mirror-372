"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Mapping
from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxSeq2SeqConfigWithPast
from ...utils import logging
logger = logging.get_logger(__name__)
class MT5Config(PretrainedConfig):
    model_type = "mt5"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"hidden_size": "d_model", "num_attention_heads": "num_heads", "num_hidden_layers": "num_layers"}
    def __init__(self, vocab_size=250112, d_model=512, d_kv=64, d_ff=1024, num_layers=8, num_decoder_layers=None, num_heads=6, relative_attention_num_buckets=32,
    relative_attention_max_distance=128, dropout_rate=0.1, layer_norm_epsilon=1e-6, initializer_factor=1.0, feed_forward_proj="gated-gelu", is_encoder_decoder=True,
    use_cache=True, tokenizer_class="T5Tokenizer", tie_word_embeddings=False, pad_token_id=0, eos_token_id=1, decoder_start_token_id=0, classifier_dropout=0.0, **kwargs):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_kv = d_kv
        self.d_ff = d_ff
        self.num_layers = num_layers
        self.num_decoder_layers = (num_decoder_layers if num_decoder_layers is not None else self.num_layers)
        self.num_heads = num_heads
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.dropout_rate = dropout_rate
        self.classifier_dropout = classifier_dropout
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_factor = initializer_factor
        self.feed_forward_proj = feed_forward_proj
        self.use_cache = use_cache
        act_info = self.feed_forward_proj.split("-")
        self.dense_act_fn = act_info[-1]
        self.is_gated_act = act_info[0] == "gated"
        if len(act_info) > 1 and act_info[0] != "gated" or len(act_info) > 2: raise ValueError(f"`feed_forward_proj`: {feed_forward_proj} is not a valid activation function of the dense layer. Please make sure `feed_forward_proj` is of the format `gated-{ACT_FN}` or `{ACT_FN}`, e.g. 'gated-gelu' or 'relu'")
        if feed_forward_proj == "gated-gelu": self.dense_act_fn = "gelu_new"
        super().__init__(is_encoder_decoder=is_encoder_decoder, tokenizer_class=tokenizer_class, tie_word_embeddings=tie_word_embeddings, pad_token_id=pad_token_id,
        eos_token_id=eos_token_id, decoder_start_token_id=decoder_start_token_id, **kwargs)
class MT5OnnxConfig(OnnxSeq2SeqConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = {"input_ids": {0: "batch", 1: "encoder_sequence"}, "attention_mask": {0: "batch", 1: "encoder_sequence"}}
        if self.use_past:
            common_inputs["attention_mask"][1] = "past_encoder_sequence + sequence"
            common_inputs["decoder_input_ids"] = {0: "batch"}
            common_inputs["decoder_attention_mask"] = {0: "batch", 1: "past_decoder_sequence + sequence"}
        else:
            common_inputs["decoder_input_ids"] = {0: "batch", 1: "decoder_sequence"}
            common_inputs["decoder_attention_mask"] = {0: "batch", 1: "decoder_sequence"}
        if self.use_past: self.fill_with_past_key_values_(common_inputs, direction="inputs")
        return common_inputs
    @property
    def default_onnx_opset(self) -> int: return 13
    @property
    def atol_for_validation(self) -> float: return 5e-4
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
