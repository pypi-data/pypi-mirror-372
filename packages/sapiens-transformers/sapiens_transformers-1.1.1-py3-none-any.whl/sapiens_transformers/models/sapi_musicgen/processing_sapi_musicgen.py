"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...processing_utils import ProcessorMixin
from typing import List, Optional
from ...utils import to_numpy
import numpy as np
class SAPIMusicGenProcessor(ProcessorMixin):
    feature_extractor_class, tokenizer_class = "EncodecFeatureExtractor", ("T5Tokenizer", "T5TokenizerFast")
    def __init__(self, feature_extractor, tokenizer):
        super().__init__(feature_extractor, tokenizer)
        self.current_processor, self._in_target_context_manager = self.feature_extractor, False
    def get_decoder_prompt_ids(self, task=None, language=None, no_timestamps=True): return self.tokenizer.get_decoder_prompt_ids(task=task, language=language, no_timestamps=no_timestamps)
    def __call__(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor(*args, **kwargs)
        audio = kwargs.pop("audio", None)
        sampling_rate = kwargs.pop("sampling_rate", None)
        text = kwargs.pop("text", None)
        if len(args) > 0: audio, args = args[0], args[1:]
        if audio is None and text is None: raise ValueError("You need to specify either an `audio` or `text` input to process.")
        if text is not None: inputs = self.tokenizer(text, **kwargs)
        if audio is not None: audio_inputs = self.feature_extractor(audio, *args, sampling_rate=sampling_rate, **kwargs)
        if audio is None: return inputs
        elif text is None: return audio_inputs
        else:
            inputs["input_values"] = audio_inputs["input_values"]
            if "padding_mask" in audio_inputs: inputs["padding_mask"] = audio_inputs["padding_mask"]
            return inputs
    def batch_decode(self, *args, **kwargs):
        audio_values = kwargs.pop("audio", None)
        padding_mask = kwargs.pop("padding_mask", None)
        if len(args) > 0: audio_values, args = args[0], args[1:]
        if audio_values is not None: return self._decode_audio(audio_values, padding_mask=padding_mask)
        else: return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    def _decode_audio(self, audio_values, padding_mask: Optional = None) -> List[np.ndarray]:
        audio_values = to_numpy(audio_values)
        bsz, channels, seq_len = audio_values.shape
        if padding_mask is None: return list(audio_values)
        padding_mask = to_numpy(padding_mask)
        difference = seq_len - padding_mask.shape[-1]
        padding_value = 1 - self.feature_extractor.padding_value
        padding_mask = np.pad(padding_mask, ((0, 0), (0, difference)), "constant", constant_values=padding_value)
        audio_values = audio_values.tolist()
        for i in range(bsz): audio_values[i] = np.asarray(audio_values[i])[padding_mask[i][None, :] != self.feature_extractor.padding_value].reshape(channels, -1)
        return audio_values
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
