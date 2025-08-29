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
class Wav2Vec2FeatureExtractor(SequenceFeatureExtractor):
    model_input_names = ["input_values", "attention_mask"]
    def __init__(self, feature_size=1, sampling_rate=16000, padding_value=0.0, return_attention_mask=False, do_normalize=True, **kwargs):
        super().__init__(feature_size=feature_size, sampling_rate=sampling_rate, padding_value=padding_value, **kwargs)
        self.return_attention_mask = return_attention_mask
        self.do_normalize = do_normalize
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
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], padding: Union[bool, str, PaddingStrategy] = False, max_length: Optional[int] = None,
    truncation: bool = False, pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    sampling_rate: Optional[int] = None, **kwargs) -> BatchFeature:
        if sampling_rate is not None:
            if sampling_rate != self.sampling_rate: raise ValueError(f"The model corresponding to this feature extractor: {self} was trained using a sampling rate of {self.sampling_rate}. Please make sure that the provided `raw_speech` input was sampled with {self.sampling_rate} and not {sampling_rate}.")
        else: logger.warning("It is strongly recommended to pass the ``sampling_rate`` argument to this function. Failing to do so can result in silent errors that might be hard to debug.")
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if not is_batched: raw_speech = [raw_speech]
        encoded_inputs = BatchFeature({"input_values": raw_speech})
        padded_inputs = self.pad(encoded_inputs, padding=padding, max_length=max_length, truncation=truncation, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
        input_values = padded_inputs["input_values"]
        if not isinstance(input_values[0], np.ndarray): padded_inputs["input_values"] = [np.asarray(array, dtype=np.float32) for array in input_values]
        elif (not isinstance(input_values, np.ndarray) and isinstance(input_values[0], np.ndarray) and input_values[0].dtype is np.dtype(np.float64)): padded_inputs["input_values"] = [array.astype(np.float32) for array in input_values]
        elif isinstance(input_values, np.ndarray) and input_values.dtype is np.dtype(np.float64): padded_inputs["input_values"] = input_values.astype(np.float32)
        attention_mask = padded_inputs.get("attention_mask")
        if attention_mask is not None: padded_inputs["attention_mask"] = [np.asarray(array, dtype=np.int32) for array in attention_mask]
        if self.do_normalize:
            attention_mask = (attention_mask if self._get_padding_strategies(padding, max_length=max_length) is not PaddingStrategy.DO_NOT_PAD else None)
            padded_inputs["input_values"] = self.zero_mean_unit_var_norm(padded_inputs["input_values"], attention_mask=attention_mask, padding_value=self.padding_value)
        if return_tensors is not None: padded_inputs = padded_inputs.convert_to_tensors(return_tensors)
        return padded_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
