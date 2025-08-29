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
from ...onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast
from ...utils import logging
if TYPE_CHECKING:
    from ...feature_extraction_utils import FeatureExtractionMixin
    from ...tokenization_utils_base import PreTrainedTokenizerBase
    from ...utils import TensorType
logger = logging.get_logger(__name__)
NON_SPEECH_TOKENS = [1, 2, 7, 8, 9, 10, 14, 25, 26, 27, 28, 29, 31, 58, 59, 60, 61, 62, 63, 90, 91, 92, 93, 357, 366, 438, 532, 685, 705, 796, 930, 1058, 1220, 1267, 1279, 1303, 1343, 1377,
1391, 1635, 1782, 1875, 2162, 2361, 2488, 3467, 4008, 4211, 4600, 4808, 5299, 5855, 6329, 7203, 9609, 9959, 10563, 10786, 11420, 11709, 11907, 13163, 13697, 13700, 14808, 15306, 16410, 16791,
17992, 19203, 19510, 20724, 22305, 22935, 27007, 30109, 30420, 33409, 34949, 40283, 40493, 40549, 47282, 49146, 50257, 50359, 50360, 50361]
NON_SPEECH_TOKENS_MULTI = [1, 2, 7, 8, 9, 10, 14, 25, 26, 27, 28, 29, 31, 58, 59, 60, 61, 62, 63, 90, 91, 92, 93, 359, 503, 522, 542, 873, 893, 902, 918, 922, 931, 1350, 1853, 1982, 2460, 2627,
3246, 3253, 3268, 3536, 3846, 3961, 4183, 4667, 6585, 6647, 7273, 9061, 9383, 10428, 10929, 11938, 12033, 12331, 12562, 13793, 14157, 14635, 15265, 15618, 16553, 16604, 18362, 18956, 20075, 21675,
22520, 26130, 26161, 26435, 28279, 29464, 31650, 32302, 32470, 36865, 42863, 47425, 49870, 50254, 50258, 50360, 50361, 50362]
class WhisperConfig(PretrainedConfig):
    model_type = "whisper"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'num_key_value_heads': 'encoder_attention_heads', 'num_attention_heads': 'encoder_attention_heads', 'hidden_size': 'd_model'}
    def __init__(self, vocab_size=51865, num_mel_bins=80, encoder_layers=4, encoder_attention_heads=6, decoder_layers=4, decoder_attention_heads=6, decoder_ffn_dim=1536,
    encoder_ffn_dim=1536, encoder_layerdrop=0.0, decoder_layerdrop=0.0, decoder_start_token_id=50257, use_cache=True, is_encoder_decoder=True, activation_function="gelu",
    d_model=384, dropout=0.0, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, scale_embedding=False, max_source_positions=1500, max_target_positions=448,
    pad_token_id=50256, bos_token_id=50256, eos_token_id=50256, suppress_tokens=None, begin_suppress_tokens=[220, 50256], use_weighted_layer_sum=False, classifier_proj_size=256,
    apply_spec_augment=False, mask_time_prob=0.05, mask_time_length=10, mask_time_min_masks=2, mask_feature_prob=0.0, mask_feature_length=10, mask_feature_min_masks=0,
    median_filter_width=7, **kwargs):
        self.vocab_size = vocab_size
        self.num_mel_bins = num_mel_bins
        self.d_model = d_model
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.encoder_ffn_dim = encoder_ffn_dim
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
        self.max_source_positions = max_source_positions
        self.max_target_positions = max_target_positions
        self.classifier_proj_size = classifier_proj_size
        self.use_weighted_layer_sum = use_weighted_layer_sum
        self.apply_spec_augment = apply_spec_augment
        self.mask_time_prob = mask_time_prob
        self.mask_time_length = mask_time_length
        self.mask_time_min_masks = mask_time_min_masks
        self.mask_feature_prob = mask_feature_prob
        self.mask_feature_length = mask_feature_length
        self.mask_feature_min_masks = mask_feature_min_masks
        self.median_filter_width = median_filter_width
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, decoder_start_token_id=decoder_start_token_id,
        suppress_tokens=suppress_tokens, begin_suppress_tokens=begin_suppress_tokens, **kwargs)
class WhisperOnnxConfig(OnnxSeq2SeqConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict([("input_features", {0: "batch", 1: "feature_size", 2: "encoder_sequence"})])
        if self.use_past: common_inputs["decoder_input_ids"] = {0: "batch"}
        else: common_inputs["decoder_input_ids"] = {0: "batch", 1: "decoder_sequence"}
        if self.use_past: self.fill_with_past_key_values_(common_inputs, direction="inputs")
        return common_inputs
    def generate_dummy_inputs(self, preprocessor: Union["PreTrainedTokenizerBase", "FeatureExtractionMixin"], batch_size: int = -1, seq_length: int = -1, is_pair: bool = False,
    framework: Optional["TensorType"] = None, sampling_rate: int = 22050, time_duration: float = 5.0, frequency: int = 220) -> Mapping[str, Any]:
        dummy_inputs = OrderedDict()
        encoder_inputs = OnnxConfig.generate_dummy_inputs(self, preprocessor=preprocessor.feature_extractor, batch_size=batch_size, framework=framework, sampling_rate=sampling_rate,
        time_duration=time_duration, frequency=frequency)
        encoder_sequence_length = encoder_inputs["input_features"].shape[2]
        seq_length = encoder_sequence_length // 2 if self.use_past else seq_length
        decoder_inputs = super().generate_dummy_inputs(preprocessor.tokenizer, batch_size, seq_length, is_pair, framework)
        dummy_inputs["input_features"] = encoder_inputs.pop("input_features")
        dummy_inputs["decoder_input_ids"] = decoder_inputs.pop("decoder_input_ids")
        if "past_key_values" in decoder_inputs: dummy_inputs["past_key_values"] = decoder_inputs.pop("past_key_values")
        return dummy_inputs
    @property
    def atol_for_validation(self) -> float: return 1e-3
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
