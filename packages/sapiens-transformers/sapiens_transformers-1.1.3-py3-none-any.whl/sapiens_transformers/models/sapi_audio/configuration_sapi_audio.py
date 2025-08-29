"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PRETRAINED_SAPIENS_TECHNOLOGY as SapiensTechnologyForPretraining
from .sapi_audio_import_variables import ATTRIBUTE_MAP, NON_SPEECH_TOKENS, NON_SPEECH_TOKENS_MULTI
from ...utils import SAPIENS_TECHNOLOGY_CHECKING
if SAPIENS_TECHNOLOGY_CHECKING:
    from ...feature_extraction_utils import FeatureExtractionMixin
    from ...tokenization_utils_base import PreTrainedTokenizerBase
    from ...utils import TensorType
from ...onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast
from typing import Mapping, Union, Optional, Any
from collections import OrderedDict
class SAPIAudioOnnxConfig(OnnxSeq2SeqConfigWithPast):
    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        common_inputs = OrderedDict([("input_features", {0: "batch", 1: "feature_size", 2: "encoder_sequence"})])
        common_inputs["decoder_input_ids"] = {0: "batch"} if self.use_past else {0: "batch", 1: "decoder_sequence"}
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
        dummy_inputs["input_features"], dummy_inputs["decoder_input_ids"] = encoder_inputs.pop("input_features"), decoder_inputs.pop("decoder_input_ids")
        if "past_key_values" in decoder_inputs: dummy_inputs["past_key_values"] = decoder_inputs.pop("past_key_values")
        return dummy_inputs
    @property
    def atol_for_validation(self) -> float: return 1e-3
class SAPIAudioConfig(SapiensTechnologyForPretraining):
    model_type, keys_to_ignore_at_inference, attribute_map = "sapi_audio", ["past_key_values"], ATTRIBUTE_MAP
    def __init__(self, vocab_size=103730, num_mel_bins=160, encoder_layers=8, encoder_attention_heads=12, decoder_layers=8, decoder_attention_heads=12, decoder_ffn_dim=3072,
    encoder_ffn_dim=3072, encoder_layerdrop=0.01, decoder_layerdrop=0.01, decoder_start_token_id=100514, use_cache=True, is_encoder_decoder=True, activation_function="gelu",
    d_model=768, dropout=0.01, attention_dropout=0.01, activation_dropout=0.01, init_std=0.04, scale_embedding=False, max_source_positions=3000, max_target_positions=896,
    pad_token_id=100512, bos_token_id=100512, eos_token_id=100512, suppress_tokens=None, begin_suppress_tokens=[440, 100512], use_weighted_layer_sum=False, classifier_proj_size=512,
    apply_spec_augment=False, mask_time_prob=0.07, mask_time_length=20, mask_time_min_masks=4, mask_feature_prob=0.01, mask_feature_length=20, mask_feature_min_masks=0,
    median_filter_width=8, **kwargs):
        self.vocab_size = vocab_size if type(vocab_size) in (int, float) else 103730
        self.num_mel_bins = num_mel_bins if type(num_mel_bins) in (int, float) else 160
        self.encoder_layers = self.num_hidden_layers = encoder_layers if type(encoder_layers) in (int, float) else 8
        self.encoder_attention_heads = encoder_attention_heads if type(encoder_attention_heads) in (int, float) else 12
        self.decoder_layers = decoder_layers if type(decoder_layers) in (int, float) else 8
        self.decoder_attention_heads = decoder_attention_heads if type(decoder_attention_heads) in (int, float) else 12
        self.decoder_ffn_dim = decoder_ffn_dim if type(decoder_ffn_dim) in (int, float) else 3072
        self.encoder_ffn_dim = encoder_ffn_dim if type(encoder_ffn_dim) in (int, float) else 3072
        self.encoder_layerdrop = encoder_layerdrop if type(encoder_layerdrop) in (int, float) else 0.01
        self.decoder_layerdrop = decoder_layerdrop if type(decoder_layerdrop) in (int, float) else 0.01
        self.decoder_start_token_id = decoder_start_token_id if type(decoder_start_token_id) in (int, float) else 100514
        self.use_cache = use_cache if type(use_cache) in (bool, int, float) else True
        self.is_encoder_decoder = is_encoder_decoder if type(is_encoder_decoder) in (bool, int, float) else True
        self.activation_function = activation_function if type(activation_function) == str else "gelu"
        self.d_model = d_model if type(d_model) in (int, float) else 768
        self.dropout = dropout if type(dropout) in (int, float) else 0.01
        self.attention_dropout = attention_dropout if type(attention_dropout) in (int, float) else 0.01
        self.activation_dropout = activation_dropout if type(activation_dropout) in (int, float) else 0.01
        self.init_std = init_std if type(init_std) in (int, float) else 0.04
        self.scale_embedding = scale_embedding if type(scale_embedding) in (bool, int, float) else False
        self.max_source_positions = max_source_positions if type(max_source_positions) in (int, float) else 3000
        self.max_target_positions = max_target_positions if type(max_target_positions) in (int, float) else 896
        self.pad_token_id = pad_token_id if type(pad_token_id) in (int, float) else 100512
        self.bos_token_id = bos_token_id if type(bos_token_id) in (int, float) else 100512
        self.eos_token_id = eos_token_id if type(eos_token_id) in (int, float) else 100512
        self.suppress_tokens = suppress_tokens
        self.begin_suppress_tokens = begin_suppress_tokens if type(begin_suppress_tokens) in (tuple, list) else [440, 100512]
        self.use_weighted_layer_sum = use_weighted_layer_sum if type(use_weighted_layer_sum) in (bool, int, float) else False
        self.classifier_proj_size = classifier_proj_size if type(classifier_proj_size) in (int, float) else 512
        self.apply_spec_augment = apply_spec_augment if type(apply_spec_augment) in (bool, int, float) else False
        self.mask_time_prob = mask_time_prob if type(mask_time_prob) in (int, float) else 0.07
        self.mask_time_length = mask_time_length if type(mask_time_length) in (int, float) else 20
        self.mask_time_min_masks = mask_time_min_masks if type(mask_time_min_masks) in (int, float) else 4
        self.mask_feature_prob = mask_feature_prob if type(mask_feature_prob) in (int, float) else 0.01
        self.mask_feature_length = mask_feature_length if type(mask_feature_length) in (int, float) else 20
        self.mask_feature_min_masks = mask_feature_min_masks if type(mask_feature_min_masks) in (int, float) else 0
        self.median_filter_width = median_filter_width if type(median_filter_width) in (int, float) else 8
        super().__init__(pad_token_id=self.pad_token_id, bos_token_id=self.bos_token_id, eos_token_id=self.eos_token_id, is_encoder_decoder=self.is_encoder_decoder, decoder_start_token_id=self.decoder_start_token_id,
        suppress_tokens=self.suppress_tokens, begin_suppress_tokens=self.begin_suppress_tokens, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
