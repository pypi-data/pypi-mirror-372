"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from ...processing_utils import ProcessorMixin
from ..seamless_m4t.feature_extraction_seamless_m4t import SeamlessM4TFeatureExtractor
from ..wav2vec2.tokenization_wav2vec2 import Wav2Vec2CTCTokenizer
class Wav2Vec2BertProcessor(ProcessorMixin):
    feature_extractor_class = "SeamlessM4TFeatureExtractor"
    tokenizer_class = "AutoTokenizer"
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        try: return super().from_pretrained(pretrained_model_name_or_path, **kwargs)
        except OSError:
            warnings.warn(f"Loading a tokenizer inside {cls.__name__} from a config that does not include a `tokenizer_class` attribute is deprecated and will be removed in v5. Please add `'tokenizer_class': 'Wav2Vec2CTCTokenizer'` attribute to either your `config.json` or `tokenizer_config.json` file to suppress this warning: ", FutureWarning)
            feature_extractor = SeamlessM4TFeatureExtractor.from_pretrained(pretrained_model_name_or_path, **kwargs)
            tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(pretrained_model_name_or_path, **kwargs)
            return cls(feature_extractor=feature_extractor, tokenizer=tokenizer)
    def __call__(self, audio=None, text=None, **kwargs):
        sampling_rate = kwargs.pop("sampling_rate", None)
        if audio is None and text is None: raise ValueError("You need to specify either an `audio` or `text` input to process.")
        if audio is not None: inputs = self.feature_extractor(audio, sampling_rate=sampling_rate, **kwargs)
        if text is not None: encodings = self.tokenizer(text, **kwargs)
        if text is None: return inputs
        elif audio is None: return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            return inputs
    def pad(self, input_features=None, labels=None, **kwargs):
        if input_features is None and labels is None: raise ValueError("You need to specify either an `input_features` or `labels` input to pad.")
        if input_features is not None: input_features = self.feature_extractor.pad(input_features, **kwargs)
        if labels is not None: labels = self.tokenizer.pad(labels, **kwargs)
        if labels is None: return input_features
        elif input_features is None: return labels
        else:
            input_features["labels"] = labels["input_ids"]
            return input_features
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
