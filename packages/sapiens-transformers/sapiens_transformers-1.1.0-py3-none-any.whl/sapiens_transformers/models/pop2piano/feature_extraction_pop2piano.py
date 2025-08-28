"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import List, Optional, Union
import numpy
import numpy as np
from ...audio_utils import mel_filter_bank, spectrogram
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import (TensorType, is_essentia_available, is_librosa_available, is_scipy_available, logging, requires_backends)
if is_essentia_available():
    import essentia
    import essentia.standard
if is_librosa_available(): import librosa
if is_scipy_available(): import scipy
logger = logging.get_logger(__name__)
class Pop2PianoFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features", "beatsteps", "extrapolated_beatstep"]
    def __init__(self, sampling_rate: int = 22050, padding_value: int = 0, window_size: int = 4096, hop_length: int = 1024, min_frequency: float = 10.0, feature_size: int = 512, num_bars: int = 2, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
        self.sampling_rate = sampling_rate
        self.padding_value = padding_value
        self.window_size = window_size
        self.hop_length = hop_length
        self.min_frequency = min_frequency
        self.feature_size = feature_size
        self.num_bars = num_bars
        self.mel_filters = mel_filter_bank(num_frequency_bins=(self.window_size // 2) + 1, num_mel_filters=self.feature_size, min_frequency=self.min_frequency,
        max_frequency=float(self.sampling_rate // 2), sampling_rate=self.sampling_rate, norm=None, mel_scale="htk")
    def mel_spectrogram(self, sequence: np.ndarray):
        mel_specs = []
        for seq in sequence:
            window = np.hanning(self.window_size + 1)[:-1]
            mel_specs.append(spectrogram(waveform=seq, window=window, frame_length=self.window_size, hop_length=self.hop_length, power=2.0, mel_filters=self.mel_filters))
        mel_specs = np.array(mel_specs)
        return mel_specs
    def extract_rhythm(self, audio: np.ndarray):
        requires_backends(self, ["essentia"])
        essentia_tracker = essentia.standard.RhythmExtractor2013(method="multifeature")
        bpm, beat_times, confidence, estimates, essentia_beat_intervals = essentia_tracker(audio)
        return bpm, beat_times, confidence, estimates, essentia_beat_intervals
    def interpolate_beat_times(self, beat_times: numpy.ndarray, steps_per_beat: numpy.ndarray, n_extend: numpy.ndarray):
        requires_backends(self, ["scipy"])
        beat_times_function = scipy.interpolate.interp1d(np.arange(beat_times.size), beat_times, bounds_error=False, fill_value="extrapolate")
        ext_beats = beat_times_function(np.linspace(0, beat_times.size + n_extend - 1, beat_times.size * steps_per_beat + n_extend))
        return ext_beats
    def preprocess_mel(self, audio: np.ndarray, beatstep: np.ndarray):
        if audio is not None and len(audio.shape) != 1: raise ValueError(f"Expected `audio` to be a single channel audio input of shape `(n, )` but found shape {audio.shape}.")
        if beatstep[0] > 0.0: beatstep = beatstep - beatstep[0]
        num_steps = self.num_bars * 4
        num_target_steps = len(beatstep)
        extrapolated_beatstep = self.interpolate_beat_times(beat_times=beatstep, steps_per_beat=1, n_extend=(self.num_bars + 1) * 4 + 1)
        sample_indices = []
        max_feature_length = 0
        for i in range(0, num_target_steps, num_steps):
            start_idx = i
            end_idx = min(i + num_steps, num_target_steps)
            start_sample = int(extrapolated_beatstep[start_idx] * self.sampling_rate)
            end_sample = int(extrapolated_beatstep[end_idx] * self.sampling_rate)
            sample_indices.append((start_sample, end_sample))
            max_feature_length = max(max_feature_length, end_sample - start_sample)
        padded_batch = []
        for start_sample, end_sample in sample_indices:
            feature = audio[start_sample:end_sample]
            padded_feature = np.pad(feature, ((0, max_feature_length - feature.shape[0]),), "constant", constant_values=0)
            padded_batch.append(padded_feature)
        padded_batch = np.asarray(padded_batch)
        return padded_batch, extrapolated_beatstep
    def _pad(self, features: np.ndarray, add_zero_line=True):
        features_shapes = [each_feature.shape for each_feature in features]
        attention_masks, padded_features = [], []
        for i, each_feature in enumerate(features):
            if len(each_feature.shape) == 3:
                features_pad_value = max([*zip(*features_shapes)][1]) - features_shapes[i][1]
                attention_mask = np.ones(features_shapes[i][:2], dtype=np.int64)
                feature_padding = ((0, 0), (0, features_pad_value), (0, 0))
                attention_mask_padding = (feature_padding[0], feature_padding[1])
            else:
                each_feature = each_feature.reshape(1, -1)
                features_pad_value = max([*zip(*features_shapes)][0]) - features_shapes[i][0]
                attention_mask = np.ones(features_shapes[i], dtype=np.int64).reshape(1, -1)
                feature_padding = attention_mask_padding = ((0, 0), (0, features_pad_value))
            each_padded_feature = np.pad(each_feature, feature_padding, "constant", constant_values=self.padding_value)
            attention_mask = np.pad(attention_mask, attention_mask_padding, "constant", constant_values=self.padding_value)
            if add_zero_line:
                zero_array_len = max([*zip(*features_shapes)][1])
                each_padded_feature = np.concatenate([each_padded_feature, np.zeros([1, zero_array_len, self.feature_size])], axis=0)
                attention_mask = np.concatenate([attention_mask, np.zeros([1, zero_array_len], dtype=attention_mask.dtype)], axis=0)
            padded_features.append(each_padded_feature)
            attention_masks.append(attention_mask)
        padded_features = np.concatenate(padded_features, axis=0).astype(np.float32)
        attention_masks = np.concatenate(attention_masks, axis=0).astype(np.int64)
        return padded_features, attention_masks
    def pad(self, inputs: BatchFeature, is_batched: bool, return_attention_mask: bool, return_tensors: Optional[Union[str, TensorType]] = None):
        processed_features_dict = {}
        for feature_name, feature_value in inputs.items():
            if feature_name == "input_features":
                padded_feature_values, attention_mask = self._pad(feature_value, add_zero_line=True)
                processed_features_dict[feature_name] = padded_feature_values
                if return_attention_mask: processed_features_dict["attention_mask"] = attention_mask
            else:
                padded_feature_values, attention_mask = self._pad(feature_value, add_zero_line=False)
                processed_features_dict[feature_name] = padded_feature_values
                if return_attention_mask: processed_features_dict[f"attention_mask_{feature_name}"] = attention_mask
        if not is_batched and not return_attention_mask: processed_features_dict["input_features"] = processed_features_dict["input_features"][:-1, ...]
        outputs = BatchFeature(processed_features_dict, tensor_type=return_tensors)
        return outputs
    def __call__(self, audio: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], sampling_rate: Union[int, List[int]], steps_per_beat: int = 2,
    resample: Optional[bool] = True, return_attention_mask: Optional[bool] = False, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> BatchFeature:
        requires_backends(self, ["librosa"])
        is_batched = bool(isinstance(audio, (list, tuple)) and isinstance(audio[0], (np.ndarray, tuple, list)))
        if is_batched:
            if not isinstance(sampling_rate, list): raise ValueError(f"Please give sampling_rate of each audio separately when you are passing multiple raw_audios at the same time. Received {sampling_rate}, expected [audio_1_sr, ..., audio_n_sr].")
            return_attention_mask = True if return_attention_mask is None else return_attention_mask
        else:
            audio = [audio]
            sampling_rate = [sampling_rate]
            return_attention_mask = False if return_attention_mask is None else return_attention_mask
        batch_input_features, batch_beatsteps, batch_ext_beatstep = [], [], []
        for single_raw_audio, single_sampling_rate in zip(audio, sampling_rate):
            bpm, beat_times, confidence, estimates, essentia_beat_intervals = self.extract_rhythm(audio=single_raw_audio)
            beatsteps = self.interpolate_beat_times(beat_times=beat_times, steps_per_beat=steps_per_beat, n_extend=1)
            if self.sampling_rate != single_sampling_rate and self.sampling_rate is not None:
                if resample: single_raw_audio = librosa.core.resample(single_raw_audio, orig_sr=single_sampling_rate, target_sr=self.sampling_rate, res_type="kaiser_best")
                else: warnings.warn(f"The sampling_rate of the provided audio is different from the target sampling_rate of the Feature Extractor, {self.sampling_rate} vs {single_sampling_rate}. In these cases it is recommended to use `resample=True` in the `__call__` method to get the optimal behaviour.")
            single_sampling_rate = self.sampling_rate
            start_sample = int(beatsteps[0] * single_sampling_rate)
            end_sample = int(beatsteps[-1] * single_sampling_rate)
            input_features, extrapolated_beatstep = self.preprocess_mel(single_raw_audio[start_sample:end_sample], beatsteps - beatsteps[0])
            mel_specs = self.mel_spectrogram(input_features.astype(np.float32))
            log_mel_specs = np.log(np.clip(mel_specs, a_min=1e-6, a_max=None))
            input_features = np.transpose(log_mel_specs, (0, -1, -2))
            batch_input_features.append(input_features)
            batch_beatsteps.append(beatsteps)
            batch_ext_beatstep.append(extrapolated_beatstep)
        output = BatchFeature({"input_features": batch_input_features, "beatsteps": batch_beatsteps, "extrapolated_beatstep": batch_ext_beatstep})
        output = self.pad(output, is_batched=is_batched, return_attention_mask=return_attention_mask, return_tensors=return_tensors)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
