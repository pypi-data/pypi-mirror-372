"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import Any, Dict, List, Optional, Union
import numpy as np
from ...audio_utils import mel_filter_bank, optimal_fft_length, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import PaddingStrategy, TensorType, logging
logger = logging.get_logger(__name__)
class SpeechT5FeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_values", "attention_mask"]
    def __init__(self,  feature_size: int = 1, sampling_rate: int = 16000, padding_value: float = 0.0, do_normalize: bool = False, num_mel_bins: int = 80, hop_length: int = 16,
    win_length: int = 64, win_function: str = "hann_window", frame_signal_scale: float = 1.0, fmin: float = 80, fmax: float = 7600, mel_floor: float = 1e-10,
    reduction_factor: int = 2, return_attention_mask: bool = True, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
        self.do_normalize = do_normalize
        self.return_attention_mask = return_attention_mask
        self.num_mel_bins = num_mel_bins
        self.hop_length = hop_length
        self.win_length = win_length
        self.win_function = win_function
        self.frame_signal_scale = frame_signal_scale
        self.fmin = fmin
        self.fmax = fmax
        self.mel_floor = mel_floor
        self.reduction_factor = reduction_factor
        self.sample_size = win_length * sampling_rate // 1000
        self.sample_stride = hop_length * sampling_rate // 1000
        self.n_fft = optimal_fft_length(self.sample_size)
        self.n_freqs = (self.n_fft // 2) + 1
        self.window = window_function(window_length=self.sample_size, name=self.win_function, periodic=True)
        self.mel_filters = mel_filter_bank(num_frequency_bins=self.n_freqs, num_mel_filters=self.num_mel_bins, min_frequency=self.fmin, max_frequency=self.fmax,
        sampling_rate=self.sampling_rate, norm="slaney", mel_scale="slaney")
        if frame_signal_scale != 1.0: warnings.warn("The argument `frame_signal_scale` is deprecated and will be removed in version 4.30.0 of Transformers", FutureWarning)
        if reduction_factor != 2.0: warnings.warn("The argument `reduction_factor` is deprecated and will be removed in version 4.30.0 of Transformers", FutureWarning)
    @staticmethod
    def zero_mean_unit_var_norm(input_values: List[np.ndarray], attention_mask: List[np.ndarray], padding_value: float = 0.0) -> List[np.ndarray]:
        if attention_mask is not None:
            attention_mask = np.array(attention_mask, np.int32)
            normed_input_values = []
            for vector, length in zip(input_values, attention_mask.sum(-1)):
                normed_slice = (vector - vector[:length].mean()) / np.sqrt(vector[:length].var() + 1e-7)
                if length < normed_slice.shape[0]: normed_slice[length:] = padding_value
                normed_input_values.append(normed_slice)
        else: normed_input_values = [(x - x.mean()) / np.sqrt(x.var() + 1e-7) for x in input_values]
        return normed_input_values
    def _extract_mel_features(self, one_waveform: np.ndarray) -> np.ndarray:
        log_mel_spec = spectrogram(one_waveform, window=self.window, frame_length=self.sample_size, hop_length=self.sample_stride, fft_length=self.n_fft,
        mel_filters=self.mel_filters, mel_floor=self.mel_floor, log_mel="log10")
        return log_mel_spec.T
    def __call__(self, audio: Optional[Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]]] = None, audio_target: Optional[Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]]] = None,
    padding: Union[bool, str, PaddingStrategy] = False, max_length: Optional[int] = None, truncation: bool = False, pad_to_multiple_of: Optional[int] = None,
    return_attention_mask: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, sampling_rate: Optional[int] = None, **kwargs) -> BatchFeature:
        if audio is None and audio_target is None: raise ValueError("You must provide either `audio` or `audio_target` values.")
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided audio input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the ``sampling_rate`` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        if audio is not None: inputs = self._process_audio(audio, False, padding, max_length, truncation, pad_to_multiple_of, return_attention_mask, return_tensors, **kwargs)
        else: inputs = None
        if audio_target is not None:
            inputs_target = self._process_audio(audio_target, True, padding, max_length, truncation, pad_to_multiple_of, return_attention_mask, return_tensors, **kwargs)
            if inputs is None: return inputs_target
            else:
                inputs["labels"] = inputs_target["input_values"]
                decoder_attention_mask = inputs_target.get("attention_mask")
                if decoder_attention_mask is not None: inputs["decoder_attention_mask"] = decoder_attention_mask
        return inputs
    def _process_audio(self, speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], is_target: bool = False, padding: Union[bool, str, PaddingStrategy] = False,
    max_length: Optional[int] = None, truncation: bool = False, pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchFeature:
        is_batched_numpy = isinstance(speech, np.ndarray) and len(speech.shape) > 1
        if is_batched_numpy and len(speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(speech, (list, tuple)) and (isinstance(speech[0], (np.ndarray, tuple, list))))
        if is_batched: speech = [np.asarray(speech, dtype=np.float32) for speech in speech]
        elif not is_batched and not isinstance(speech, np.ndarray): speech = np.asarray(speech, dtype=np.float32)
        elif isinstance(speech, np.ndarray) and speech.dtype is np.dtype(np.float64): speech = speech.astype(np.float32)
        if not is_batched: speech = [speech]
        feature_size_hack = self.feature_size
        if is_target:
            features = [self._extract_mel_features(waveform) for waveform in speech]
            encoded_inputs = BatchFeature({"input_values": features})
            self.feature_size = self.num_mel_bins
        else: encoded_inputs = BatchFeature({"input_values": speech})
        padded_inputs = self.pad(encoded_inputs, padding=padding, max_length=max_length, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of,
        return_attention_mask=return_attention_mask, **kwargs)
        self.feature_size = feature_size_hack
        input_values = padded_inputs["input_values"]
        if not isinstance(input_values[0], np.ndarray): padded_inputs["input_values"] = [np.asarray(array, dtype=np.float32) for array in input_values]
        elif (not isinstance(input_values, np.ndarray) and isinstance(input_values[0], np.ndarray) and input_values[0].dtype is np.dtype(np.float64)): padded_inputs["input_values"] = [array.astype(np.float32) for array in input_values]
        elif isinstance(input_values, np.ndarray) and input_values.dtype is np.dtype(np.float64): padded_inputs["input_values"] = input_values.astype(np.float32)
        attention_mask = padded_inputs.get("attention_mask")
        if attention_mask is not None: padded_inputs["attention_mask"] = [np.asarray(array, dtype=np.int32) for array in attention_mask]
        if not is_target and self.do_normalize:
            attention_mask = (attention_mask if self._get_padding_strategies(padding, max_length=max_length) is not PaddingStrategy.DO_NOT_PAD else None)
            padded_inputs["input_values"] = self.zero_mean_unit_var_norm(padded_inputs["input_values"], attention_mask=attention_mask, padding_value=self.padding_value)
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
    def to_dict(self) -> Dict[str, Any]:
        output = super().to_dict()
        names = ["window", "mel_filters", "sample_size", "sample_stride", "n_fft", "n_freqs"]
        for name in names:
            if name in output: del output[name]
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
