"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from typing import Any, Dict, List, Optional, Union
import numpy as np
import torch
from ...audio_utils import mel_filter_bank, spectrogram, window_function
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import TensorType, logging
logger = logging.get_logger(__name__)
class ClapFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "is_longer"]
    def __init__(self, feature_size=64, sampling_rate=48_000, hop_length=480, max_length_s=10, fft_window_size=1024, padding_value=0.0, return_attention_mask=False,
    frequency_min: float = 0, frequency_max: float = 14_000, top_db: int = None, truncation: str = "fusion", padding: str = "repeatpad", **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, return_attention_mask=return_attention_mask, **kwargs)
        self.top_db = top_db
        self.truncation = truncation
        self.padding = padding
        self.fft_window_size = fft_window_size
        self.nb_frequency_bins = (fft_window_size >> 1) + 1
        self.hop_length = hop_length
        self.max_length_s = max_length_s
        self.nb_max_samples = max_length_s * sampling_rate
        self.sampling_rate = sampling_rate
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max
        self.mel_filters = mel_filter_bank(num_frequency_bins=self.nb_frequency_bins, num_mel_filters=feature_size, min_frequency=frequency_min, max_frequency=frequency_max, sampling_rate=sampling_rate, norm=None, mel_scale="htk")
        self.mel_filters_slaney = mel_filter_bank(num_frequency_bins=self.nb_frequency_bins, num_mel_filters=feature_size, min_frequency=frequency_min, max_frequency=frequency_max, sampling_rate=sampling_rate, norm="slaney", mel_scale="slaney")
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["feature_extractor_type"] = self.__class__.__name__
        if "mel_filters" in output: del output["mel_filters"]
        if "mel_filters_slaney" in output: del output["mel_filters_slaney"]
        return output
    def _np_extract_fbank_features(self, waveform: np.array, mel_filters: Optional[np.array] = None) -> np.ndarray:
        log_mel_spectrogram = spectrogram(waveform, window_function(self.fft_window_size, "hann"), frame_length=self.fft_window_size, hop_length=self.hop_length, power=2.0, mel_filters=mel_filters, log_mel="dB")
        return log_mel_spectrogram.T
    def _random_mel_fusion(self, mel, total_frames, chunk_frames):
        ranges = np.array_split(list(range(0, total_frames - chunk_frames + 1)), 3)
        if len(ranges[1]) == 0: ranges[1] = [0]
        if len(ranges[2]) == 0: ranges[2] = [0]
        idx_front = np.random.choice(ranges[0])
        idx_middle = np.random.choice(ranges[1])
        idx_back = np.random.choice(ranges[2])
        mel_chunk_front = mel[idx_front : idx_front + chunk_frames, :]
        mel_chunk_middle = mel[idx_middle : idx_middle + chunk_frames, :]
        mel_chunk_back = mel[idx_back : idx_back + chunk_frames, :]
        mel = torch.tensor(mel[None, None, :])
        mel_shrink = torch.nn.functional.interpolate(mel, size=[chunk_frames, 64], mode="bilinear", align_corners=False)
        mel_shrink = mel_shrink[0][0].numpy()
        mel_fusion = np.stack([mel_shrink, mel_chunk_front, mel_chunk_middle, mel_chunk_back], axis=0)
        return mel_fusion
    def _get_input_mel(self, waveform: np.array, max_length, truncation, padding) -> np.array:
        if waveform.shape[0] > max_length:
            if truncation == "rand_trunc":
                longer = True
                overflow = len(waveform) - max_length
                idx = np.random.randint(0, overflow + 1)
                waveform = waveform[idx : idx + max_length]
                input_mel = self._np_extract_fbank_features(waveform, self.mel_filters_slaney)[None, :]
            elif truncation == "fusion":
                mel = self._np_extract_fbank_features(waveform, self.mel_filters)
                chunk_frames = max_length // self.hop_length + 1
                total_frames = mel.shape[0]
                if chunk_frames == total_frames:
                    input_mel = np.stack([mel, mel, mel, mel], axis=0)
                    longer = False
                else:
                    input_mel = self._random_mel_fusion(mel, total_frames, chunk_frames)
                    longer = True
            else: raise NotImplementedError(f"data_truncating {truncation} not implemented")
        else:
            longer = False
            if waveform.shape[0] < max_length:
                if padding == "repeat":
                    n_repeat = int(max_length / len(waveform))
                    waveform = np.tile(waveform, n_repeat + 1)[:max_length]
                if padding == "repeatpad":
                    n_repeat = int(max_length / len(waveform))
                    waveform = np.tile(waveform, n_repeat)
                waveform = np.pad(waveform, (0, max_length - waveform.shape[0]), mode="constant", constant_values=0)
            if truncation == "fusion":
                input_mel = self._np_extract_fbank_features(waveform, self.mel_filters)
                input_mel = np.stack([input_mel, input_mel, input_mel, input_mel], axis=0)
            else: input_mel = self._np_extract_fbank_features(waveform, self.mel_filters_slaney)[None, :]
        return input_mel, longer
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], truncation: str = None, padding: Optional[str] = None,
    max_length: Optional[int] = None, sampling_rate: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchFeature:
        truncation = truncation if truncation is not None else self.truncation
        padding = padding if padding else self.padding
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self.__class__.__name__} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if is_batched: raw_speech = [np.asarray(speech, dtype=np.float64) for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech, dtype=np.float64)
        elif isinstance(raw_speech, np.ndarray) and raw_speech.dtype is np.dtype(np.float64): raw_speech = raw_speech.astype(np.float64)
        if not is_batched: raw_speech = [np.asarray(raw_speech)]
        padded_inputs = [self._get_input_mel(waveform, max_length if max_length else self.nb_max_samples, truncation, padding) for waveform in raw_speech]
        input_mel = []
        is_longer = []
        for mel, longer in padded_inputs:
            input_mel.append(mel)
            is_longer.append(longer)
        if truncation == "fusion" and sum(is_longer) == 0:
            rand_idx = np.random.randint(0, len(input_mel))
            is_longer[rand_idx] = True
        if isinstance(input_mel[0], List): input_mel = [np.asarray(feature, dtype=np.float64) for feature in input_mel]
        is_longer = [[longer] for longer in is_longer]
        input_features = {"input_features": input_mel, "is_longer": is_longer}
        input_features = BatchFeature(input_features)
        if return_tensors is not None: input_features = input_features.convert_to_tensors(return_tensors)
        return input_features
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
