"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
from ...utils import is_torch_available
if is_torch_available(): import torch
from ...audio_utils import mel_filter_bank, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import PaddingStrategy, TensorType, logging
logger = logging.get_logger(__name__)
class SeamlessM4TFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "attention_mask"]
    def __init__(self, feature_size=80, sampling_rate=16000, num_mel_bins=80, padding_value=0.0, stride=2, **kwargs):
        self.num_mel_bins = num_mel_bins
        self.return_attention_mask = True
        self.stride = stride
        mel_filters = mel_filter_bank(num_frequency_bins=256, num_mel_filters=self.num_mel_bins, min_frequency=20, max_frequency=sampling_rate // 2, sampling_rate=sampling_rate,
        norm=None, mel_scale="kaldi", triangularize_in_mel_space=True)
        self.mel_filters = np.pad(mel_filters, ((0, 1), (0, 0)))
        self.window = window_function(400, "povey", periodic=False)
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
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
    def _extract_fbank_features(self, waveform: np.ndarray) -> np.ndarray:
        if len(waveform.shape) == 2: waveform = waveform[0]
        waveform = np.squeeze(waveform) * (2**15)
        features = spectrogram(waveform, self.window, frame_length=400, hop_length=160, fft_length=512, power=2.0, center=False, preemphasis=0.97, mel_filters=self.mel_filters,
        log_mel="log", mel_floor=1.192092955078125e-07, remove_dc_offset=True).T
        return features
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], padding: Union[bool, str, PaddingStrategy] = True,
    pad_to_multiple_of: Optional[int] = 2, max_length: Optional[int] = None, truncation: bool = False, return_tensors: Optional[Union[str, TensorType]] = None,
    sampling_rate: Optional[int] = None, return_attention_mask: Optional[bool] = None, do_normalize_per_mel_bins: Optional[bool] = True, **kwargs) -> BatchFeature:
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        return_attention_mask = (return_attention_mask if return_attention_mask is not None else self.return_attention_mask)
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 3: raise ValueError(f"Only mono-channel or stereo-channel audio is supported for input to {self}")
        acceptable_types = ((torch.Tensor, np.ndarray, tuple, list) if is_torch_available() else (np.ndarray, tuple, list))
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], acceptable_types)))
        if is_batched: raw_speech = [np.asarray(speech, dtype=np.float32) for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech, dtype=np.float32)
        elif isinstance(raw_speech, np.ndarray) and raw_speech.dtype is np.dtype(np.float64): raw_speech = raw_speech.astype(np.float32)
        if not is_batched: raw_speech = [raw_speech]
        features = [self._extract_fbank_features(waveform) for waveform in raw_speech]
        if do_normalize_per_mel_bins: features = [(x - np.expand_dims(x.mean(0), 0)) / np.sqrt(np.expand_dims(x.var(0, ddof=1), 0) + 1e-7) for x in features]
        encoded_inputs = BatchFeature({"input_features": features})
        padded_inputs = self.pad(encoded_inputs, padding=padding, max_length=max_length, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of,
        return_attention_mask=True, return_tensors="np")
        input_features = padded_inputs.get("input_features")
        attention_mask = padded_inputs.pop("attention_mask")
        batch_size, num_frames, num_channels = input_features.shape
        remainder = num_frames % self.stride
        if remainder != 0:
            input_features = input_features[:, : num_frames - remainder, :]
            attention_mask = attention_mask[:, : num_frames - remainder]
        input_features = np.reshape(input_features, (batch_size, num_frames // self.stride, num_channels * self.stride))
        indices = np.arange(0, num_frames - remainder)
        attention_mask = attention_mask[:, indices % self.stride == 1]
        padded_inputs["input_features"] = input_features
        if return_attention_mask: padded_inputs["attention_mask"] = attention_mask
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
