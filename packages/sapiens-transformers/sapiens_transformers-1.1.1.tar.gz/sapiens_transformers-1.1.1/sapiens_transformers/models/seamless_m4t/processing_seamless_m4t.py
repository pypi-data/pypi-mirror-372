"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessorMixin
class SeamlessM4TProcessor(ProcessorMixin):
    feature_extractor_class = "SeamlessM4TFeatureExtractor"
    tokenizer_class = ("SeamlessM4TTokenizer", "SeamlessM4TTokenizerFast")
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    def __call__(self, text=None, audios=None, src_lang=None, tgt_lang=None, **kwargs):
        sampling_rate = kwargs.pop("sampling_rate", None)
        if text is None and audios is None: raise ValueError("You have to specify either text or audios. Both cannot be none.")
        elif text is not None and audios is not None: raise ValueError("Text and audios are mututally exclusive when passed to `SeamlessM4T`. Specify one or another.")
        elif text is not None:
            if tgt_lang is not None: self.tokenizer.tgt_lang = tgt_lang
            if src_lang is not None: self.tokenizer.src_lang = src_lang
            encoding = self.tokenizer(text, **kwargs)
            return encoding
        else:
            encoding = self.feature_extractor(audios, sampling_rate=sampling_rate, **kwargs)
            return encoding
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
