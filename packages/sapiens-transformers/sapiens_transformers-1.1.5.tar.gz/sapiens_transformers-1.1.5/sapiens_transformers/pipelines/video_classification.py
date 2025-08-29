"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from io import BytesIO
from typing import List, Union
import requests
from ..utils import (add_end_docstrings, is_av_available, is_torch_available, logging, requires_backends)
from .base import Pipeline, build_pipeline_init_args
if is_av_available():
    import av
    import numpy as np
if is_torch_available(): from ..models.auto.modeling_auto import MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class VideoClassificationPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "av")
        self.check_model_type(MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING_NAMES)
    def _sanitize_parameters(self, top_k=None, num_frames=None, frame_sampling_rate=None):
        preprocess_params = {}
        if frame_sampling_rate is not None: preprocess_params["frame_sampling_rate"] = frame_sampling_rate
        if num_frames is not None: preprocess_params["num_frames"] = num_frames
        postprocess_params = {}
        if top_k is not None: postprocess_params["top_k"] = top_k
        return preprocess_params, {}, postprocess_params
    def __call__(self, videos: Union[str, List[str]], **kwargs): return super().__call__(videos, **kwargs)
    def preprocess(self, video, num_frames=None, frame_sampling_rate=1):
        if num_frames is None: num_frames = self.model.config.num_frames
        if video.startswith("http://") or video.startswith("https://"): video = BytesIO(requests.get(video).content)
        container = av.open(video)
        start_idx = 0
        end_idx = num_frames * frame_sampling_rate - 1
        indices = np.linspace(start_idx, end_idx, num=num_frames, dtype=np.int64)
        video = read_video_pyav(container, indices)
        video = list(video)
        model_inputs = self.image_processor(video, return_tensors=self.framework)
        if self.framework == "pt": model_inputs = model_inputs.to(self.torch_dtype)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, top_k=5):
        if top_k > self.model.config.num_labels: top_k = self.model.config.num_labels
        if self.framework == "pt":
            probs = model_outputs.logits.softmax(-1)[0]
            scores, ids = probs.topk(top_k)
        else: raise ValueError(f"Unsupported framework: {self.framework}")
        scores = scores.tolist()
        ids = ids.tolist()
        return [{"score": score, "label": self.model.config.id2label[_id]} for score, _id in zip(scores, ids)]
def read_video_pyav(container, indices):
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index: break
        if i >= start_index and i in indices: frames.append(frame)
    return np.stack([x.to_ndarray(format="rgb24") for x in frames])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
