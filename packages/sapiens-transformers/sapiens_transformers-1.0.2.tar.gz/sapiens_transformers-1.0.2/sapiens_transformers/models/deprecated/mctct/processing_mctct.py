"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from contextlib import contextmanager
from ....processing_utils import ProcessorMixin
class MCTCTProcessor(ProcessorMixin):
    feature_extractor_class = "MCTCTFeatureExtractor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, feature_extractor, tokenizer):
        super().__init__(feature_extractor, tokenizer)
        self.current_processor = self.feature_extractor
        self._in_target_context_manager = False
    def __call__(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor(*args, **kwargs)
        if "raw_speech" in kwargs:
            warnings.warn("Using `raw_speech` as a keyword argument is deprecated. Use `audio` instead.")
            audio = kwargs.pop("raw_speech")
        else: audio = kwargs.pop("audio", None)
        sampling_rate = kwargs.pop("sampling_rate", None)
        text = kwargs.pop("text", None)
        if len(args) > 0:
            audio = args[0]
            args = args[1:]
        if audio is None and text is None: raise ValueError("You need to specify either an `audio` or `text` input to process.")
        if audio is not None: inputs = self.feature_extractor(audio, *args, sampling_rate=sampling_rate, **kwargs)
        if text is not None: encodings = self.tokenizer(text, **kwargs)
        if text is None: return inputs
        elif audio is None: return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            return inputs
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def pad(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor.pad(*args, **kwargs)
        input_features = kwargs.pop("input_features", None)
        labels = kwargs.pop("labels", None)
        if len(args) > 0:
            input_features = args[0]
            args = args[1:]
        if input_features is not None: input_features = self.feature_extractor.pad(input_features, *args, **kwargs)
        if labels is not None: labels = self.tokenizer.pad(labels, **kwargs)
        if labels is None: return input_features
        elif input_features is None: return labels
        else:
            input_features["labels"] = labels["input_ids"]
            return input_features
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @contextmanager
    def as_target_processor(self):
        warnings.warn("`as_target_processor` is deprecated and will be removed in v1 of Sapiens Transformers. You can process your labels by using the argument `text` of the regular `__call__` method (either in the same call as your audio inputs, or in a separate call.")
        self._in_target_context_manager = True
        self.current_processor = self.tokenizer
        yield
        self.current_processor = self.feature_extractor
        self._in_target_context_manager = False
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
