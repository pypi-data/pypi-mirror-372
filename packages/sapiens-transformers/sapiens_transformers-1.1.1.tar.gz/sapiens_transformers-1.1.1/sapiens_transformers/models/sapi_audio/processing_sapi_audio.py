"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import SapiensProcessorMixin
class SAPIAudioProcessor(SapiensProcessorMixin):
    feature_extractor_class, tokenizer_class = "SAPIAudioFeatureExtractor", "SAPIAudioTokenizer"
    def __init__(self, feature_extractor, tokenizer):
        super().__init__(feature_extractor, tokenizer)
        self.current_processor, self._in_target_context_manager = self.feature_extractor, False
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def get_prompt_ids(self, text: str, return_tensors="np"): return self.tokenizer.get_prompt_ids(text, return_tensors=return_tensors)
    def get_decoder_prompt_ids(self, task=None, language=None, no_timestamps=True): return self.tokenizer.get_decoder_prompt_ids(task=task, language=language, no_timestamps=no_timestamps)
    def __call__(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor(*args, **kwargs)
        audio, sampling_rate, text = kwargs.pop("audio", None), kwargs.pop("sampling_rate", None), kwargs.pop("text", None)
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
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
