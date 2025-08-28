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
from ...audio_utils import chroma_filter_bank
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import TensorType, is_torch_available, is_torchaudio_available, logging
if is_torch_available(): import torch
if is_torchaudio_available(): import torchaudio
logger = logging.get_logger(__name__)
class MusicgenMelodyFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_features"]
    def __init__(self, feature_size=12, sampling_rate=32000, hop_length=4096, chunk_length=30, n_fft=16384, num_chroma=12, padding_value=0.0, return_attention_mask=False,
    stem_indices=[3, 2], **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, return_attention_mask=return_attention_mask, **kwargs)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.chunk_length = chunk_length
        self.n_samples = chunk_length * sampling_rate
        self.sampling_rate = sampling_rate
        self.chroma_filters = torch.from_numpy(chroma_filter_bank(sampling_rate=sampling_rate, num_frequency_bins=n_fft, tuning=0, num_chroma=num_chroma)).float()
        self.spectrogram = torchaudio.transforms.Spectrogram(n_fft=n_fft, win_length=n_fft, hop_length=hop_length, power=2, center=True, pad=0, normalized=True)
        self.stem_indices = stem_indices
    def _torch_extract_fbank_features(self, waveform: torch.Tensor) -> torch.Tensor:
        wav_length = waveform.shape[-1]
        if wav_length < self.n_fft:
            pad = self.n_fft - wav_length
            rest = 0 if pad % 2 == 0 else 1
            waveform = torch.nn.functional.pad(waveform, (pad // 2, pad // 2 + rest), "constant", 0)
        spec = self.spectrogram(waveform).squeeze(1)
        raw_chroma = torch.einsum("cf, ...ft->...ct", self.chroma_filters, spec)
        norm_chroma = torch.nn.functional.normalize(raw_chroma, p=float("inf"), dim=-2, eps=1e-6)
        norm_chroma = norm_chroma.transpose(1, 2)
        idx = norm_chroma.argmax(-1, keepdim=True)
        norm_chroma[:] = 0
        norm_chroma.scatter_(dim=-1, index=idx, value=1)
        return norm_chroma
    def _extract_stem_indices(self, audio, sampling_rate=None):
        sampling_rate = 44000 if sampling_rate is None else sampling_rate
        wav = audio[:, torch.tensor(self.stem_indices)]
        wav = wav.sum(1)
        wav = wav.mean(dim=1, keepdim=True)
        if sampling_rate != self.sampling_rate: wav = torchaudio.functional.resample(wav, sampling_rate, self.sampling_rate, rolloff=0.945, lowpass_filter_width=24)
        wav = wav.squeeze(1)
        return wav
    def __call__(self, audio: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], truncation: bool = True, pad_to_multiple_of: Optional[int] = None,
    return_tensors: Optional[Union[str, TensorType]] = None, return_attention_mask: Optional[bool] = None, padding: Optional[str] = True, max_length: Optional[int] = None,
    sampling_rate: Optional[int] = None, **kwargs) -> BatchFeature:
        if sampling_rate is None: logger.warning_once("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        if isinstance(audio, torch.Tensor) and len(audio.shape) == 4:
            logger.warning_once("`audio` is a 4-dimensional torch tensor and has thus been recognized as the output of `Demucs`. If this is not the case, make sure to read Musicgen Melody docstrings and to correct `audio` to get the right behaviour.")
            audio = self._extract_stem_indices(audio, sampling_rate=sampling_rate)
        elif sampling_rate is not None and sampling_rate != self.sampling_rate: audio = torchaudio.functional.resample(audio, sampling_rate, self.sampling_rate, rolloff=0.945, lowpass_filter_width=24)
        is_batched = isinstance(audio, (np.ndarray, torch.Tensor)) and len(audio.shape) > 1
        is_batched = is_batched or (isinstance(audio, (list, tuple)) and (isinstance(audio[0], (torch.Tensor, np.ndarray, tuple, list))))
        if is_batched and not isinstance(audio[0], torch.Tensor): audio = [torch.tensor(speech, dtype=torch.float32).unsqueeze(-1) for speech in audio]
        elif is_batched: audio = [speech.unsqueeze(-1) for speech in audio]
        elif not is_batched and not isinstance(audio, torch.Tensor): audio = torch.tensor(audio, dtype=torch.float32).unsqueeze(-1)
        if isinstance(audio[0], torch.Tensor) and audio[0].dtype is torch.float64: audio = [speech.to(torch.float32) for speech in audio]
        if not is_batched: audio = [audio]
        if len(audio[0].shape) == 3:
            logger.warning_once("`audio` has been detected as a batch of stereo signals. Will be convert to mono signals. If this is an undesired behaviour, make sure to read Musicgen Melody docstrings and to correct `audio` to get the right behaviour.")
            audio = [stereo.mean(dim=0) for stereo in audio]
        batched_speech = BatchFeature({"input_features": audio})
        padded_inputs = self.pad(batched_speech, padding=padding, max_length=max_length if max_length else self.n_samples, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of,
        return_attention_mask=return_attention_mask, return_tensors="pt")
        input_features = self._torch_extract_fbank_features(padded_inputs["input_features"].squeeze(-1))
        padded_inputs["input_features"] = input_features
        if return_attention_mask: padded_inputs["attention_mask"] = padded_inputs["attention_mask"][:, :: self.hop_length]
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["feature_extractor_type"] = self.__class__.__name__
        if "mel_filters" in output: del output["mel_filters"]
        if "window" in output: del output["window"]
        if "chroma_filters" in output: del output["chroma_filters"]
        if "spectrogram" in output: del output["spectrogram"]
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
