"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Union
import numpy as np
from ...feature_extraction_sequence_utils import SequenceFeatureExtractor
from ...feature_extraction_utils import BatchFeature
from ...utils import PaddingStrategy, TensorType, logging
logger = logging.get_logger(__name__)
class EncodecFeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_values", "padding_mask"]
    def __init__(self, feature_size: int = 1, sampling_rate: int = 24000, padding_value: float = 0.0, chunk_length_s: float = None, overlap: float = None, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
        self.chunk_length_s = chunk_length_s
        self.overlap = overlap
    @property
    def chunk_length(self) -> Optional[int]:
        if self.chunk_length_s is None: return None
        else: return int(self.chunk_length_s * self.sampling_rate)
    @property
    def chunk_stride(self) -> Optional[int]:
        if self.chunk_length_s is None or self.overlap is None: return None
        else: return max(1, int((1.0 - self.overlap) * self.chunk_length))
    def __call__(self, raw_audio: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], padding: Optional[Union[bool, str, PaddingStrategy]] = None,
    truncation: Optional[bool] = False, max_length: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, sampling_rate: Optional[int] = None) -> BatchFeature:
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided audio input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the `sampling_rate` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        if padding and truncation: raise ValueError("Both padding and truncation were set. Make sure you only set one.")
        elif padding is None: padding = True
        is_batched = bool(isinstance(raw_audio, (list, tuple)) and (isinstance(raw_audio[0], (np.ndarray, tuple, list))))
        if is_batched: raw_audio = [np.asarray(audio, dtype=np.float32).T for audio in raw_audio]
        elif not is_batched and not isinstance(raw_audio, np.ndarray): raw_audio = np.asarray(raw_audio, dtype=np.float32)
        elif isinstance(raw_audio, np.ndarray) and raw_audio.dtype is np.dtype(np.float64): raw_audio = raw_audio.astype(np.float32)
        if not is_batched: raw_audio = [np.asarray(raw_audio).T]
        for idx, example in enumerate(raw_audio):
            if example.ndim > 2: raise ValueError(f"Expected input shape (channels, length) but got shape {example.shape}")
            if self.feature_size == 1 and example.ndim != 1: raise ValueError(f"Expected mono audio but example has {example.shape[-1]} channels")
            if self.feature_size == 2 and example.shape[-1] != 2: raise ValueError(f"Expected stereo audio but example has {example.shape[-1]} channels")
        padded_inputs = None
        input_values = BatchFeature({"input_values": raw_audio})
        if self.chunk_stride is not None and self.chunk_length is not None and max_length is None:
            if truncation:
                max_length = min(array.shape[0] for array in raw_audio)
                nb_step = int(np.floor(max_length / self.chunk_stride))
                max_length = (nb_step - 1) * self.chunk_stride + self.chunk_length
            elif padding:
                max_length = max(array.shape[0] for array in raw_audio)
                nb_step = int(np.ceil(max_length / self.chunk_stride))
                max_length = (nb_step - 1) * self.chunk_stride + self.chunk_length
                padding = "max_length"
            else: padded_inputs = input_values
        if padded_inputs is None:
            padded_inputs = self.pad(input_values, max_length=max_length, truncation=truncation, padding=padding, return_attention_mask=padding)
            if padding: padded_inputs["padding_mask"] = padded_inputs.pop("attention_mask")
        input_values = []
        for example in padded_inputs.pop("input_values"):
            if self.feature_size == 1: example = example[..., None]
            input_values.append(example.T)
        padded_inputs["input_values"] = input_values
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
