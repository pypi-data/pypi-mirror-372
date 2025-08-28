"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from collections import UserDict
from typing import Union
import numpy as np
import requests
from ..utils import (add_end_docstrings, logging)
from .audio_classification import ffmpeg_read
from .base import Pipeline, build_pipeline_init_args
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_feature_extractor=True, has_tokenizer=True))
class ZeroShotAudioClassificationPipeline(Pipeline):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.framework != "pt": raise ValueError(f"The {self.__class__} is only available in PyTorch.")
    def __call__(self, audios: Union[np.ndarray, bytes, str], **kwargs): return super().__call__(audios, **kwargs)
    def _sanitize_parameters(self, **kwargs):
        preprocess_params = {}
        if "candidate_labels" in kwargs: preprocess_params["candidate_labels"] = kwargs["candidate_labels"]
        if "hypothesis_template" in kwargs: preprocess_params["hypothesis_template"] = kwargs["hypothesis_template"]
        return preprocess_params, {}, {}
    def preprocess(self, audio, candidate_labels=None, hypothesis_template="This is a sound of {}."):
        if isinstance(audio, str):
            if audio.startswith("http://") or audio.startswith("https://"): audio = requests.get(audio).content
            else:
                with open(audio, "rb") as f: audio = f.read()
        if isinstance(audio, bytes): audio = ffmpeg_read(audio, self.feature_extractor.sampling_rate)
        if not isinstance(audio, np.ndarray): raise TypeError("We expect a numpy ndarray as input")
        if len(audio.shape) != 1: raise ValueError("We expect a single channel audio input for ZeroShotAudioClassificationPipeline")
        inputs = self.feature_extractor([audio], sampling_rate=self.feature_extractor.sampling_rate, return_tensors="pt")
        if self.framework == "pt": inputs = inputs.to(self.torch_dtype)
        inputs["candidate_labels"] = candidate_labels
        sequences = [hypothesis_template.format(x) for x in candidate_labels]
        text_inputs = self.tokenizer(sequences, return_tensors=self.framework, padding=True)
        inputs["text_inputs"] = [text_inputs]
        return inputs
    def _forward(self, model_inputs):
        candidate_labels = model_inputs.pop("candidate_labels")
        text_inputs = model_inputs.pop("text_inputs")
        if isinstance(text_inputs[0], UserDict): text_inputs = text_inputs[0]
        else: text_inputs = text_inputs[0][0]
        outputs = self.model(**text_inputs, **model_inputs)
        model_outputs = {"candidate_labels": candidate_labels, "logits": outputs.logits_per_audio}
        return model_outputs
    def postprocess(self, model_outputs):
        candidate_labels = model_outputs.pop("candidate_labels")
        logits = model_outputs["logits"][0]
        if self.framework == "pt":
            probs = logits.softmax(dim=0)
            scores = probs.tolist()
        else: raise ValueError("`tf` framework not supported.")
        result = [{"score": score, "label": candidate_label} for score, candidate_label in sorted(zip(scores, candidate_labels), key=lambda x: -x[0])]
        return result
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
