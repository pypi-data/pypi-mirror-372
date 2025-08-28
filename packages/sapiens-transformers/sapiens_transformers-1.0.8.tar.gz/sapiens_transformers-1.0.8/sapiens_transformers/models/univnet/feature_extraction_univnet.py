"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, List, Optional, Union
import numpy as np
from ...audio_utils import mel_filter_bank, optimal_fft_length, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import PaddingStrategy, TensorType, logging
logger = logging.get_logger(__name__)
class UnivNetFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "noise_sequence", "padding_mask"]
    def __init__(self, feature_size: int = 1, sampling_rate: int = 24000, padding_value: float = 0.0, do_normalize: bool = False, num_mel_bins: int = 100, hop_length: int = 256,
    win_length: int = 1024, win_function: str = "hann_window", filter_length: Optional[int] = 1024, max_length_s: int = 10, fmin: float = 0.0, fmax: Optional[float] = None,
    mel_floor: float = 1e-9, center: bool = False, compression_factor: float = 1.0, compression_clip_val: float = 1e-5, normalize_min: float = -11.512925148010254,
    normalize_max: float = 2.3143386840820312, model_in_channels: int = 64, pad_end_length: int = 10, return_attention_mask=True, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, return_attention_mask=return_attention_mask, **kwargs)
        self.do_normalize = do_normalize
        self.num_mel_bins = num_mel_bins
        self.hop_length = hop_length
        self.win_length = win_length
        self.win_function = win_function
        self.filter_length = filter_length
        self.fmin = fmin
        if fmax is None: fmax = float(sampling_rate) / 2
        self.fmax = fmax
        self.mel_floor = mel_floor
        self.max_length_s = max_length_s
        self.num_max_samples = max_length_s * sampling_rate
        if self.filter_length is None: self.n_fft = optimal_fft_length(self.win_length)
        else: self.n_fft = self.filter_length
        self.n_freqs = (self.n_fft // 2) + 1
        self.window = window_function(window_length=self.win_length, name=self.win_function, periodic=True)
        self.mel_filters = mel_filter_bank(num_frequency_bins=self.n_freqs, num_mel_filters=self.num_mel_bins, min_frequency=self.fmin, max_frequency=self.fmax,
        sampling_rate=self.sampling_rate, norm="slaney", mel_scale="slaney")
        self.center = center
        self.compression_factor = compression_factor
        self.compression_clip_val = compression_clip_val
        self.normalize_min = normalize_min
        self.normalize_max = normalize_max
        self.model_in_channels = model_in_channels
        self.pad_end_length = pad_end_length
    def normalize(self, spectrogram): return 2 * ((spectrogram - self.normalize_min) / (self.normalize_max - self.normalize_min)) - 1
    def denormalize(self, spectrogram): return self.normalize_min + (self.normalize_max - self.normalize_min) * ((spectrogram + 1) / 2)
    def mel_spectrogram(self, waveform: np.ndarray) -> np.ndarray:
        waveform = np.pad(waveform, (int((self.n_fft - self.hop_length) / 2), int((self.n_fft - self.hop_length) / 2)), mode="reflect")
        complex_spectrogram = spectrogram(waveform, window=self.window, frame_length=self.n_fft, hop_length=self.hop_length, fft_length=self.n_fft, power=None,
        center=self.center, mel_filters=None, mel_floor=None)
        amplitude_spectrogram = np.sqrt(np.real(complex_spectrogram) ** 2 + np.imag(complex_spectrogram) ** 2 + self.mel_floor)
        mel_spectrogram = np.matmul(self.mel_filters.T, amplitude_spectrogram)
        log_mel_spectrogram = np.log(np.clip(mel_spectrogram, a_min=self.compression_clip_val, a_max=None) * self.compression_factor)
        return log_mel_spectrogram.T
    def generate_noise(self, noise_length: int, generator: Optional[np.random.Generator] = None) -> np.ndarray:
        if generator is None: generator = np.random.default_rng()
        noise_shape = (noise_length, self.model_in_channels)
        noise = generator.standard_normal(noise_shape, dtype=np.float32)
        return noise
    def batch_decode(self, waveforms, waveform_lengths=None) -> List[np.ndarray]:
        waveforms = [waveform.detach().clone().cpu().numpy() for waveform in waveforms]
        if waveform_lengths is not None: waveforms = [waveform[: waveform_lengths[i]] for i, waveform in enumerate(waveforms)]
        return waveforms
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], sampling_rate: Optional[int] = None, padding: Union[bool, str, PaddingStrategy] = True,
    max_length: Optional[int] = None, truncation: bool = True, pad_to_multiple_of: Optional[int] = None, return_noise: bool = True, generator: Optional[np.random.Generator] = None,
    pad_end: bool = False, pad_length: Optional[int] = None, do_normalize: Optional[str] = None, return_attention_mask: Optional[bool] = None,
    return_tensors: Optional[Union[str, TensorType]] = None) -> BatchFeature:
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self.__class__.__name__} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if is_batched: raw_speech = [np.asarray(speech, dtype=np.float32) for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech, dtype=np.float32)
        elif isinstance(raw_speech, np.ndarray) and raw_speech.dtype is np.dtype(np.float64): raw_speech = raw_speech.astype(np.float32)
        if not is_batched: raw_speech = [np.asarray(raw_speech, dtype=np.float32)]
        if pad_end:
            pad_length = pad_length if pad_length is not None else self.pad_end_length
            raw_speech = [np.pad(waveform, (0, pad_length * self.hop_length), constant_values=self.padding_value) for waveform in raw_speech]
        batched_speech = BatchFeature({"input_features": raw_speech})
        padded_inputs = self.pad(batched_speech, padding=padding, max_length=max_length if max_length is not None else self.num_max_samples, truncation=truncation,
        pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
        input_features = padded_inputs.get("input_features")
        mel_spectrograms = [self.mel_spectrogram(waveform) for waveform in input_features]
        if isinstance(input_features[0], List): batched_speech["input_features"] = [np.asarray(mel, dtype=np.float32) for mel in mel_spectrograms]
        else: batched_speech["input_features"] = [mel.astype(np.float32) for mel in mel_spectrograms]
        attention_mask = padded_inputs.get("attention_mask")
        if attention_mask is not None: batched_speech["padding_mask"] = [np.asarray(array, dtype=np.int32) for array in attention_mask]
        if return_noise:
            noise = [self.generate_noise(spectrogram.shape[0], generator) for spectrogram in batched_speech["input_features"]]
            batched_speech["noise_sequence"] = noise
        if do_normalize: batched_speech["input_features"] = [self.normalize(spectrogram) for spectrogram in batched_speech["input_features"]]
        if return_tensors is not None: batched_speech = batched_speech.convert_to_tensors(return_tensors)
        return batched_speech
    def to_dict(self) -> Dict[str, Any]:
        output = super().to_dict()
        names = ["window", "mel_filters", "n_fft", "n_freqs", "num_max_samples"]
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
