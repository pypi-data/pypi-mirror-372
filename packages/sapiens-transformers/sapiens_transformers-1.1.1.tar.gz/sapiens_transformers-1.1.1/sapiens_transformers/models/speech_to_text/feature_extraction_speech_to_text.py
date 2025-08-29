"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
from ...audio_utils import mel_filter_bank, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import PaddingStrategy, TensorType, is_speech_available, logging
if is_speech_available():
    import torch
    import torchaudio.compliance.kaldi as ta_kaldi
logger = logging.get_logger(__name__)
class Speech2TextFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "attention_mask"]
    def __init__(self, feature_size=80, sampling_rate=16000, num_mel_bins=80, padding_value=0.0, do_ceptral_normalize=True, normalize_means=True, normalize_vars=True, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
        self.num_mel_bins = num_mel_bins
        self.do_ceptral_normalize = do_ceptral_normalize
        self.normalize_means = normalize_means
        self.normalize_vars = normalize_vars
        self.return_attention_mask = True
        if not is_speech_available():
            mel_filters = mel_filter_bank(num_frequency_bins=256, num_mel_filters=self.num_mel_bins, min_frequency=20, max_frequency=sampling_rate // 2,
            sampling_rate=sampling_rate, norm=None, mel_scale="kaldi", triangularize_in_mel_space=True)
            self.mel_filters = np.pad(mel_filters, ((0, 1), (0, 0)))
            self.window = window_function(400, "povey", periodic=False)
    def _extract_fbank_features(self, waveform: np.ndarray) -> np.ndarray:
        waveform = waveform * (2**15)
        if is_speech_available():
            waveform = torch.from_numpy(waveform).unsqueeze(0)
            features = ta_kaldi.fbank(waveform, num_mel_bins=self.num_mel_bins, sample_frequency=self.sampling_rate)
            features = features.numpy()
        else:
            waveform = np.squeeze(waveform)
            features = spectrogram(waveform, self.window, frame_length=400, hop_length=160, fft_length=512, power=2.0, center=False, preemphasis=0.97, mel_filters=self.mel_filters,
            log_mel="log", mel_floor=1.192092955078125e-07, remove_dc_offset=True).T
        return features
    @staticmethod
    def utterance_cmvn(x: np.ndarray, input_length: int, normalize_means: Optional[bool] = True, normalize_vars: Optional[bool] = True, padding_value: float = 0.0) -> np.ndarray:
        if normalize_means:
            mean = x[:input_length].mean(axis=0)
            x = np.subtract(x, mean)
        if normalize_vars:
            std = x[:input_length].std(axis=0)
            x = np.divide(x, std)
        if input_length < x.shape[0]: x[input_length:] = padding_value
        x = x.astype(np.float32)
        return x
    def normalize(self, input_features: List[np.ndarray], attention_mask: Optional[np.ndarray] = None) -> List[np.ndarray]:
        lengths = attention_mask.sum(-1) if attention_mask is not None else [x.shape[0] for x in input_features]
        return [self.utterance_cmvn(x, n, self.normalize_means, self.normalize_vars, self.padding_value) for x, n in zip(input_features, lengths)]
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], padding: Union[bool, str, PaddingStrategy] = False,
    max_length: Optional[int] = None, truncation: bool = False, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    sampling_rate: Optional[int] = None, return_attention_mask: Optional[bool] = None, **kwargs) -> BatchFeature:
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if is_batched: raw_speech = [np.asarray(speech, dtype=np.float32) for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech, dtype=np.float32)
        elif isinstance(raw_speech, np.ndarray) and raw_speech.dtype is np.dtype(np.float64): raw_speech = raw_speech.astype(np.float32)
        if not is_batched: raw_speech = [raw_speech]
        features = [self._extract_fbank_features(waveform) for waveform in raw_speech]
        encoded_inputs = BatchFeature({"input_features": features})
        padded_inputs = self.pad(encoded_inputs, padding=padding, max_length=max_length, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of,
        return_attention_mask=return_attention_mask, **kwargs)
        input_features = padded_inputs.get("input_features")
        if isinstance(input_features[0], list): padded_inputs["input_features"] = [np.asarray(feature, dtype=np.float32) for feature in input_features]
        attention_mask = padded_inputs.get("attention_mask")
        if attention_mask is not None: padded_inputs["attention_mask"] = [np.asarray(array, dtype=np.int32) for array in attention_mask]
        if self.do_ceptral_normalize:
            attention_mask = (np.array(attention_mask, dtype=np.int32) if self._get_padding_strategies(padding, max_length=max_length) is not PaddingStrategy.DO_NOT_PAD else None)
            padded_inputs["input_features"] = self.normalize(padded_inputs["input_features"], attention_mask=attention_mask)
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
