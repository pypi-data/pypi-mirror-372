"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional
import numpy as np
from ...processing_utils import ProcessorMixin
from ...utils import to_numpy
class MusicgenMelodyProcessor(ProcessorMixin):
    feature_extractor_class = "MusicgenMelodyFeatureExtractor"
    tokenizer_class = ("T5Tokenizer", "T5TokenizerFast")
    def __init__(self, feature_extractor, tokenizer): super().__init__(feature_extractor, tokenizer)
    def get_decoder_prompt_ids(self, task=None, language=None, no_timestamps=True): return self.tokenizer.get_decoder_prompt_ids(task=task, language=language, no_timestamps=no_timestamps)
    def __call__(self, audio=None, text=None, **kwargs):
        sampling_rate = kwargs.pop("sampling_rate", None)
        if audio is None and text is None: raise ValueError("You need to specify either an `audio` or `text` input to process.")
        if text is not None: inputs = self.tokenizer(text, **kwargs)
        if audio is not None: audio_inputs = self.feature_extractor(audio, sampling_rate=sampling_rate, **kwargs)
        if text is None: return audio_inputs
        elif audio is None: return inputs
        else:
            inputs["input_features"] = audio_inputs["input_features"]
            return inputs
    def batch_decode(self, *args, **kwargs):
        audio_values = kwargs.pop("audio", None)
        attention_mask = kwargs.pop("attention_mask", None)
        if len(args) > 0:
            audio_values = args[0]
            args = args[1:]
        if audio_values is not None: return self._decode_audio(audio_values, attention_mask=attention_mask)
        else: return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def _decode_audio(self, audio_values, attention_mask: Optional = None) -> List[np.ndarray]:
        audio_values = to_numpy(audio_values)
        bsz, channels, seq_len = audio_values.shape
        if attention_mask is None: return list(audio_values)
        attention_mask = to_numpy(attention_mask)
        difference = seq_len - attention_mask.shape[-1]
        padding_value = 1 - self.feature_extractor.padding_value
        attention_mask = np.pad(attention_mask, ((0, 0), (0, difference)), "constant", constant_values=padding_value)
        audio_values = audio_values.tolist()
        for i in range(bsz):
            sliced_audio = np.asarray(audio_values[i])[attention_mask[i][None, :] != self.feature_extractor.padding_value]
            audio_values[i] = sliced_audio.reshape(channels, -1)
        return audio_values
    def get_unconditional_inputs(self, num_samples=1, return_tensors="pt"):
        inputs = self.tokenizer([""] * num_samples, return_tensors=return_tensors, return_attention_mask=True)
        inputs["attention_mask"][:] = 0
        return inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
