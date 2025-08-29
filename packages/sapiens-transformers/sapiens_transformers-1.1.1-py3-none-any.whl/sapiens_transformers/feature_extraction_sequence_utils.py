"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import PaddingStrategy, TensorType, is_tf_tensor, is_torch_tensor, logging, to_numpy
from .feature_extraction_utils import BatchFeature, FeatureExtractionMixin
from typing import Dict, List, Optional, Union
import numpy as np
logger = logging.get_logger(__name__)
class SequenceFeatureExtractor(FeatureExtractionMixin):
    def __init__(self, feature_size: int, sampling_rate: int, padding_value: float, **kwargs):
        self.feature_size = feature_size
        self.sampling_rate = sampling_rate
        self.padding_value = padding_value
        self.padding_side = kwargs.pop("padding_side", "right")
        self.return_attention_mask = kwargs.pop("return_attention_mask", True)
        super().__init__(**kwargs)
    def pad(self, processed_features: Union[BatchFeature, List[BatchFeature], Dict[str, BatchFeature], Dict[str, List[BatchFeature]], List[Dict[str, BatchFeature]]], padding: Union[bool, str, PaddingStrategy] = True,
    max_length: Optional[int] = None, truncation: bool = False, pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None) -> BatchFeature:
        if isinstance(processed_features, (list, tuple)) and isinstance(processed_features[0], (dict, BatchFeature)): processed_features = {key: [example[key] for example in processed_features] for key in processed_features[0].keys()}
        if self.model_input_names[0] not in processed_features: raise ValueError(f"You should supply an instance of `sapiens_transformers.BatchFeature` or list of `sapiens_transformers.BatchFeature` to this method that includes {self.model_input_names[0]}, but you provided {list(processed_features.keys())}")
        required_input = processed_features[self.model_input_names[0]]
        return_attention_mask = (return_attention_mask if return_attention_mask is not None else self.return_attention_mask)
        if len(required_input) == 0:
            if return_attention_mask: processed_features["attention_mask"] = []
            return processed_features
        first_element = required_input[0]
        if isinstance(first_element, (list, tuple)):
            index = 0
            while len(required_input[index]) == 0: index += 1
            if index < len(required_input): first_element = required_input[index][0]
        if return_tensors is None:
            if is_tf_tensor(first_element): return_tensors = "tf"
            elif is_torch_tensor(first_element): return_tensors = "pt"
            elif isinstance(first_element, (int, float, list, tuple, np.ndarray)): return_tensors = "np"
            else: raise ValueError(f"type of {first_element} unknown: {type(first_element)}. Should be one of a python, numpy, pytorch or tensorflow object.")
        for key, value in processed_features.items():
            if isinstance(value[0], (int, float)): processed_features[key] = to_numpy(value)
            else: processed_features[key] = [to_numpy(v) for v in value]
        padding_strategy = self._get_padding_strategies(padding=padding, max_length=max_length)
        required_input = processed_features[self.model_input_names[0]]
        batch_size = len(required_input)
        if not all(len(v) == batch_size for v in processed_features.values()): raise ValueError("Some items in the output dictionary have a different batch size than others.")
        truncated_inputs = []
        for i in range(batch_size):
            inputs = {k: v[i] for k, v in processed_features.items()}
            inputs_slice = self._truncate(inputs, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, truncation=truncation)
            truncated_inputs.append(inputs_slice)
        if padding_strategy == PaddingStrategy.LONGEST:
            max_length = max(len(input_slice[self.model_input_names[0]]) for input_slice in truncated_inputs)
            padding_strategy = PaddingStrategy.MAX_LENGTH
        batch_outputs = {}
        for i in range(batch_size):
            outputs = self._pad(truncated_inputs[i], max_length=max_length, padding_strategy=padding_strategy, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                if value.dtype is np.dtype(np.float64): value = value.astype(np.float32)
                batch_outputs[key].append(value)
        return BatchFeature(batch_outputs, tensor_type=return_tensors)
    def _pad(self, processed_features: Union[Dict[str, np.ndarray], BatchFeature], max_length: Optional[int] = None, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, pad_to_multiple_of: Optional[int] = None, return_attention_mask: Optional[bool] = None) -> dict:
        required_input = processed_features[self.model_input_names[0]]
        if padding_strategy == PaddingStrategy.LONGEST: max_length = len(required_input)
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_padded = padding_strategy != PaddingStrategy.DO_NOT_PAD and len(required_input) < max_length
        if return_attention_mask and "attention_mask" not in processed_features: processed_features["attention_mask"] = np.ones(len(required_input), dtype=np.int32)
        if needs_to_be_padded:
            difference = max_length - len(required_input)
            if self.padding_side == "right":
                if return_attention_mask: processed_features["attention_mask"] = np.pad(processed_features["attention_mask"], (0, difference))
                padding_shape = ((0, difference), (0, 0)) if self.feature_size > 1 else (0, difference)
                processed_features[self.model_input_names[0]] = np.pad(required_input, padding_shape, "constant", constant_values=self.padding_value)
            elif self.padding_side == "left":
                if return_attention_mask: processed_features["attention_mask"] = np.pad(processed_features["attention_mask"], (difference, 0))
                padding_shape = ((difference, 0), (0, 0)) if self.feature_size > 1 else (difference, 0)
                processed_features[self.model_input_names[0]] = np.pad(required_input, padding_shape, "constant", constant_values=self.padding_value)
            else: raise ValueError("Invalid padding strategy:" + str(self.padding_side))
        return processed_features
    def _truncate(self, processed_features: Union[Dict[str, np.ndarray], BatchFeature], max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, truncation: Optional[bool] = None):
        if not truncation: return processed_features
        elif truncation and max_length is None: raise ValueError("When setting ``truncation=True``, make sure that ``max_length`` is defined.")
        required_input = processed_features[self.model_input_names[0]]
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_truncated = len(required_input) > max_length
        if needs_to_be_truncated:
            processed_features[self.model_input_names[0]] = processed_features[self.model_input_names[0]][:max_length]
            if "attention_mask" in processed_features: processed_features["attention_mask"] = processed_features["attention_mask"][:max_length]
        return processed_features
    def _get_padding_strategies(self, padding=False, max_length=None):
        if padding is not False:
            if padding is True: padding_strategy = PaddingStrategy.LONGEST
            elif not isinstance(padding, PaddingStrategy): padding_strategy = PaddingStrategy(padding)
            elif isinstance(padding, PaddingStrategy): padding_strategy = padding
        else: padding_strategy = PaddingStrategy.DO_NOT_PAD
        if max_length is None:
            if padding_strategy == PaddingStrategy.MAX_LENGTH: raise ValueError(f"When setting ``padding={PaddingStrategy.MAX_LENGTH}``, make sure that max_length is defined")
        if padding_strategy != PaddingStrategy.DO_NOT_PAD and (self.padding_value is None): raise ValueError("Asking to pad but the feature_extractor does not have a padding value. Please select a value to use as `padding_value`. For example: `feature_extractor.padding_value = 0.0`.")
        return padding_strategy
class SapiensTechnologySequenceFeatureExtractor(SequenceFeatureExtractor): pass
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
