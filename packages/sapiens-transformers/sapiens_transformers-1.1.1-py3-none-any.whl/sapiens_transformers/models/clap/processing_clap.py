"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
class ClapProcessor(ProcessorMixin):
    feature_extractor_class = "ClapFeatureExtractor"
    tokenizer_class = ("RobertaTokenizer", "RobertaTokenizerFast")
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    def __call__(self, text=None, audios=None, return_tensors=None, **kwargs):
        sampling_rate = kwargs.pop("sampling_rate", None)
        if text is None and audios is None: raise ValueError("You have to specify either text or audios. Both cannot be none.")
        if text is not None: encoding = self.tokenizer(text, return_tensors=return_tensors, **kwargs)
        if audios is not None: audio_features = self.feature_extractor(audios, sampling_rate=sampling_rate, return_tensors=return_tensors, **kwargs)
        if text is not None and audios is not None:
            encoding.update(audio_features)
            return encoding
        elif text is not None: return encoding
        else: return BatchEncoding(data=dict(**audio_features), tensor_type=return_tensors)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        feature_extractor_input_names = self.feature_extractor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + feature_extractor_input_names))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
