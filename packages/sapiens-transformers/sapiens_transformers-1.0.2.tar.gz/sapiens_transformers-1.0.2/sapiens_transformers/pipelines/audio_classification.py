"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import subprocess
from typing import Union
import numpy as np
import requests
from ..utils import add_end_docstrings, is_torch_available, is_torchaudio_available, logging
from .base import Pipeline, build_pipeline_init_args
if is_torch_available(): from ..models.auto.modeling_auto import MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
def ffmpeg_read(bpayload: bytes, sampling_rate: int) -> np.array:
    ar = f"{sampling_rate}"
    ac = "1"
    format_for_conversion = "f32le"
    ffmpeg_command = ["ffmpeg", "-i", "pipe:0", "-ac", ac, "-ar", ar, "-f", format_for_conversion, "-hide_banner", "-loglevel", "quiet", "pipe:1"]
    try: ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    except FileNotFoundError: raise ValueError("ffmpeg was not found but is required to load audio files from filename")
    output_stream = ffmpeg_process.communicate(bpayload)
    out_bytes = output_stream[0]
    audio = np.frombuffer(out_bytes, np.float32)
    if audio.shape[0] == 0: raise ValueError("Malformed soundfile")
    return audio
@add_end_docstrings(build_pipeline_init_args(has_feature_extractor=True))
class AudioClassificationPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        kwargs["top_k"] = 5
        super().__init__(*args, **kwargs)
        if self.framework != "pt": raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        self.check_model_type(MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING_NAMES)
    def __call__(self, inputs: Union[np.ndarray, bytes, str], **kwargs): return super().__call__(inputs, **kwargs)
    def _sanitize_parameters(self, top_k=None, **kwargs):
        postprocess_params = {}
        if top_k is not None:
            if top_k > self.model.config.num_labels: top_k = self.model.config.num_labels
            postprocess_params["top_k"] = top_k
        return {}, {}, postprocess_params
    def preprocess(self, inputs):
        if isinstance(inputs, str):
            if inputs.startswith("http://") or inputs.startswith("https://"): inputs = requests.get(inputs).content
            else:
                with open(inputs, "rb") as f: inputs = f.read()
        if isinstance(inputs, bytes): inputs = ffmpeg_read(inputs, self.feature_extractor.sampling_rate)
        if isinstance(inputs, dict):
            if not ("sampling_rate" in inputs and ("raw" in inputs or "array" in inputs)): raise ValueError("When passing a dictionary to AudioClassificationPipeline, the dict needs to contain a "+'"raw" key containing the numpy array representing the audio and a "sampling_rate" key, '+"containing the sampling_rate associated with that array")
            _inputs = inputs.pop("raw", None)
            if _inputs is None:
                inputs.pop("path", None)
                _inputs = inputs.pop("array", None)
            in_sampling_rate = inputs.pop("sampling_rate")
            inputs = _inputs
            if in_sampling_rate != self.feature_extractor.sampling_rate:
                import torch
                if is_torchaudio_available(): from torchaudio import functional as F
                else: raise ImportError("torchaudio is required to resample audio samples in AudioClassificationPipeline. The torchaudio package can be installed through: `pip install torchaudio`.")
                inputs = F.resample(torch.from_numpy(inputs), in_sampling_rate, self.feature_extractor.sampling_rate).numpy()
        if not isinstance(inputs, np.ndarray): raise TypeError("We expect a numpy ndarray as input")
        if len(inputs.shape) != 1: raise ValueError("We expect a single channel audio input for AudioClassificationPipeline")
        processed = self.feature_extractor(inputs, sampling_rate=self.feature_extractor.sampling_rate, return_tensors="pt")
        return processed
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, top_k=5):
        probs = model_outputs.logits[0].softmax(-1)
        scores, ids = probs.topk(top_k)
        scores = scores.tolist()
        ids = ids.tolist()
        labels = [{"score": score, "label": self.model.config.id2label[_id]} for score, _id in zip(scores, ids)]
        return labels
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
