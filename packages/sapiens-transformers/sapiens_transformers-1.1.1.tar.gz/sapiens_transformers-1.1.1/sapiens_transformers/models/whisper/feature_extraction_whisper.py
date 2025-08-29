"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
from ... import is_torch_available
from ...audio_utils import mel_filter_bank, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import TensorType, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class WhisperFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features"]
    def __init__(self, feature_size=80, sampling_rate=16000, hop_length=160, chunk_length=30, n_fft=400, padding_value=0.0, return_attention_mask=False, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, return_attention_mask=return_attention_mask, **kwargs)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.chunk_length = chunk_length
        self.n_samples = chunk_length * sampling_rate
        self.nb_max_frames = self.n_samples // hop_length
        self.sampling_rate = sampling_rate
        self.mel_filters = mel_filter_bank(num_frequency_bins=1 + n_fft // 2, num_mel_filters=feature_size, min_frequency=0.0, max_frequency=8000.0, sampling_rate=sampling_rate, norm="slaney", mel_scale="slaney")
    def _np_extract_fbank_features(self, waveform_batch: np.array, device: str) -> np.ndarray:
        if device != "cpu": raise ValueError(f"Got device `{device}` for feature extraction, but feature extraction on CUDA accelerator devices requires torch, which is not installed. Either set `device='cpu'`, or install torch according to the official instructions: https://pytorch.org/get-started/locally/")
        log_spec_batch = []
        for waveform in waveform_batch:
            log_spec = spectrogram(waveform, window_function(self.n_fft, "hann"), frame_length=self.n_fft, hop_length=self.hop_length, power=2.0, mel_filters=self.mel_filters, log_mel="log10")
            log_spec = log_spec[:, :-1]
            log_spec = np.maximum(log_spec, log_spec.max() - 8.0)
            log_spec = (log_spec + 4.0) / 4.0
            log_spec_batch.append(log_spec)
        log_spec_batch = np.array(log_spec_batch)
        return log_spec_batch
    def _torch_extract_fbank_features(self, waveform: np.array, device: str = "cpu") -> np.ndarray:
        waveform = torch.from_numpy(waveform).type(torch.float32)
        window = torch.hann_window(self.n_fft)
        if device != "cpu":
            waveform = waveform.to(device)
            window = window.to(device)
        stft = torch.stft(waveform, self.n_fft, self.hop_length, window=window, return_complex=True)
        magnitudes = stft[..., :-1].abs() ** 2
        mel_filters = torch.from_numpy(self.mel_filters).type(torch.float32)
        if device != "cpu": mel_filters = mel_filters.to(device)
        mel_spec = mel_filters.T @ magnitudes
        log_spec = torch.clamp(mel_spec, min=1e-10).log10()
        if waveform.dim() == 2:
            max_val = log_spec.max(dim=2, keepdim=True)[0].max(dim=1, keepdim=True)[0]
            log_spec = torch.maximum(log_spec, max_val - 8.0)
        else: log_spec = torch.maximum(log_spec, log_spec.max() - 8.0)
        log_spec = (log_spec + 4.0) / 4.0
        if device != "cpu": log_spec = log_spec.detach().cpu()
        return log_spec.numpy()
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
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], truncation: bool = True, pad_to_multiple_of: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, return_attention_mask: Optional[bool] = None, padding: Optional[str] = "max_length", max_length: Optional[int] = None,
    sampling_rate: Optional[int] = None, do_normalize: Optional[bool] = None, device: Optional[str] = "cpu", return_token_timestamps: Optional[bool] = None, **kwargs) -> BatchFeature:
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
        padded_inputs = self.pad(batched_speech, padding=padding, max_length=max_length if max_length else self.n_samples, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask or do_normalize)
        if do_normalize:
            padded_inputs["input_features"] = self.zero_mean_unit_var_norm(padded_inputs["input_features"], attention_mask=padded_inputs["attention_mask"], padding_value=self.padding_value)
            padded_inputs["input_features"] = np.stack(padded_inputs["input_features"], axis=0)
        input_features = padded_inputs.get("input_features").transpose(2, 0, 1)
        extract_fbank_features = (self._torch_extract_fbank_features if is_torch_available() else self._np_extract_fbank_features)
        input_features = extract_fbank_features(input_features[0], device)
        if isinstance(input_features[0], List): padded_inputs["input_features"] = [np.asarray(feature, dtype=np.float32) for feature in input_features]
        else: padded_inputs["input_features"] = input_features
        if return_attention_mask: padded_inputs["attention_mask"] = padded_inputs["attention_mask"][:, :: self.hop_length]
        if return_token_timestamps is not None: padded_inputs["num_frames"] = [len(raw_speech_i) // self.hop_length for raw_speech_i in raw_speech]
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
