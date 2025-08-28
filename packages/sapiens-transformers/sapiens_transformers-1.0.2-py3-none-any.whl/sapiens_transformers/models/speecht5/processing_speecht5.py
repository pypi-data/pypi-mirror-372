"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessorMixin
class SpeechT5Processor(ProcessorMixin):
    feature_extractor_class = "SpeechT5FeatureExtractor"
    tokenizer_class = "SpeechT5Tokenizer"
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    def __call__(self, *args, **kwargs):
        audio = kwargs.pop("audio", None)
        text = kwargs.pop("text", None)
        text_target = kwargs.pop("text_target", None)
        audio_target = kwargs.pop("audio_target", None)
        sampling_rate = kwargs.pop("sampling_rate", None)
        if audio is not None and text is not None: raise ValueError("Cannot process both `audio` and `text` inputs. Did you mean `audio_target` or `text_target`?")
        if audio_target is not None and text_target is not None: raise ValueError("Cannot process both `audio_target` and `text_target` inputs. Did you mean `audio` or `text`?")
        if audio is None and audio_target is None and text is None and text_target is None: raise ValueError("You need to specify either an `audio`, `audio_target`, `text`, or `text_target` input to process.")
        if audio is not None: inputs = self.feature_extractor(audio, *args, sampling_rate=sampling_rate, **kwargs)
        elif text is not None: inputs = self.tokenizer(text, **kwargs)
        else: inputs = None
        if audio_target is not None:
            targets = self.feature_extractor(audio_target=audio_target, *args, sampling_rate=sampling_rate, **kwargs)
            labels = targets["input_values"]
        elif text_target is not None:
            targets = self.tokenizer(text_target, **kwargs)
            labels = targets["input_ids"]
        else: targets = None
        if inputs is None: return targets
        if targets is not None:
            inputs["labels"] = labels
            decoder_attention_mask = targets.get("attention_mask")
            if decoder_attention_mask is not None: inputs["decoder_attention_mask"] = decoder_attention_mask
        return inputs
    def pad(self, *args, **kwargs):
        input_values = kwargs.pop("input_values", None)
        input_ids = kwargs.pop("input_ids", None)
        labels = kwargs.pop("labels", None)
        if input_values is not None and input_ids is not None: raise ValueError("Cannot process both `input_values` and `input_ids` inputs.")
        if input_values is None and input_ids is None and labels is None: raise ValueError("You need to specify either an `input_values`, `input_ids`, or `labels` input to be padded.")
        if input_values is not None: inputs = self.feature_extractor.pad(input_values, *args, **kwargs)
        elif input_ids is not None: inputs = self.tokenizer.pad(input_ids, **kwargs)
        else: inputs = None
        if labels is not None:
            if "input_ids" in labels or (isinstance(labels, list) and "input_ids" in labels[0]):
                targets = self.tokenizer.pad(labels, **kwargs)
                labels = targets["input_ids"]
            else:
                feature_size_hack = self.feature_extractor.feature_size
                self.feature_extractor.feature_size = self.feature_extractor.num_mel_bins
                targets = self.feature_extractor.pad(labels, *args, **kwargs)
                self.feature_extractor.feature_size = feature_size_hack
                labels = targets["input_values"]
        else: targets = None
        if inputs is None: return targets
        if targets is not None:
            inputs["labels"] = labels
            decoder_attention_mask = targets.get("attention_mask")
            if decoder_attention_mask is not None: inputs["decoder_attention_mask"] = decoder_attention_mask
        return inputs
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
