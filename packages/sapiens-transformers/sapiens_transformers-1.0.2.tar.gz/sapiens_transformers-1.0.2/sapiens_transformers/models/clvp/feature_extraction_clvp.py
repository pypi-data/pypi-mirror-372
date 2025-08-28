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
from ...utils import TensorType, logging
logger = logging.get_logger(__name__)
class ClvpFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "attention_mask"]
    def __init__(self, feature_size=80, sampling_rate=22050, default_audio_length=6, hop_length=256, chunk_length=30, n_fft=1024, padding_value=0.0, mel_norms=None, return_attention_mask=False, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, return_attention_mask=return_attention_mask, **kwargs)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.chunk_length = chunk_length
        self.n_samples = chunk_length * sampling_rate
        self.nb_max_frames = self.n_samples // hop_length
        self.sampling_rate = sampling_rate
        self.default_audio_length = default_audio_length
        self.mel_norms = mel_norms
        self.mel_filters = mel_filter_bank(num_frequency_bins=1 + (n_fft // 2), num_mel_filters=feature_size, min_frequency=0.0, max_frequency=8000.0, sampling_rate=sampling_rate, norm="slaney", mel_scale="htk")
    def _np_extract_fbank_features(self, waveform: np.array) -> np.ndarray:
        log_spec = spectrogram(waveform, window_function(self.n_fft, "hann"), frame_length=self.n_fft, hop_length=self.hop_length, power=2.0, mel_filters=self.mel_filters, log_mel=None)
        log_spec = np.log(np.clip(log_spec, a_min=1e-5, a_max=None))
        if self.mel_norms is not None: log_spec = log_spec / np.array(self.mel_norms)[:, None]
        return log_spec
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], sampling_rate: Optional[int] = None, truncation: bool = True,
    pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_attention_mask: Optional[bool] = True, padding: Optional[str] = "max_length",
    max_length: Optional[int] = None, **kwargs) -> BatchFeature:
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self.__class__.__name__} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if is_batched: raw_speech = [np.asarray([speech], dtype=np.float32).T for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech, dtype=np.float32)
        elif isinstance(raw_speech, np.ndarray) and raw_speech.dtype is np.dtype(np.float64): raw_speech = raw_speech.astype(np.float32)
        if not is_batched: raw_speech = [np.asarray([raw_speech]).T]
        batched_speech = BatchFeature({"input_features": raw_speech})
        max_length = self.default_audio_length * self.sampling_rate if max_length is None else max_length
        padded_inputs = self.pad(batched_speech, padding=padding, max_length=max_length, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
        input_features = padded_inputs.get("input_features").transpose(2, 0, 1)
        input_features = [self._np_extract_fbank_features(waveform).astype(np.float32) for waveform in input_features[0]]
        if isinstance(input_features[0], List): padded_inputs["input_features"] = [np.asarray(feature) for feature in input_features]
        else: padded_inputs["input_features"] = input_features
        return padded_inputs.convert_to_tensors(return_tensors)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
