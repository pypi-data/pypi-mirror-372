"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Optional, Union
import numpy as np
from ...feature_extraction_utils import BatchFeature
from ...processing_utils import ProcessorMixin
from ...tokenization_utils import BatchEncoding, PaddingStrategy, TruncationStrategy
from ...utils import TensorType
class Pop2PianoProcessor(ProcessorMixin):
    attributes = ["feature_extractor", "tokenizer"]
    feature_extractor_class = "Pop2PianoFeatureExtractor"
    tokenizer_class = "Pop2PianoTokenizer"
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    def __call__(self, audio: Union[np.ndarray, List[float], List[np.ndarray]] = None, sampling_rate: Union[int, List[int]] = None, steps_per_beat: int = 2,
    resample: Optional[bool] = True, notes: Union[List, TensorType] = None, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, verbose: bool = True, **kwargs) -> Union[BatchFeature, BatchEncoding]:
        if (audio is None and sampling_rate is None) and (notes is None): raise ValueError("You have to specify at least audios and sampling_rate in order to use feature extractor or notes to use the tokenizer part.")
        if audio is not None and sampling_rate is not None: inputs = self.feature_extractor(audio=audio, sampling_rate=sampling_rate, steps_per_beat=steps_per_beat, resample=resample, **kwargs)
        if notes is not None: encoded_token_ids = self.tokenizer(notes=notes, padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        if notes is None: return inputs
        elif audio is None or sampling_rate is None: return encoded_token_ids
        else:
            inputs["token_ids"] = encoded_token_ids["token_ids"]
            return inputs
    def batch_decode(self, token_ids, feature_extractor_output: BatchFeature, return_midi: bool = True) -> BatchEncoding: return self.tokenizer.batch_decode(token_ids=token_ids, feature_extractor_output=feature_extractor_output, return_midi=return_midi)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        feature_extractor_input_names = self.feature_extractor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + feature_extractor_input_names))
    def save_pretrained(self, save_directory, **kwargs):
        if os.path.isfile(save_directory): raise ValueError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        return super().save_pretrained(save_directory, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        args = cls._get_arguments_from_pretrained(pretrained_model_name_or_path, **kwargs)
        return cls(*args)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
