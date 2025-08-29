"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
import numpy as np
from ..utils import (ExplicitEnum, add_end_docstrings, is_tf_available, is_torch_available, is_vision_available, logging, requires_backends)
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_tf_available(): from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING_NAMES
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
def sigmoid(_outputs): return 1.0 / (1.0 + np.exp(-_outputs))
def softmax(_outputs):
    maxes = np.max(_outputs, axis=-1, keepdims=True)
    shifted_exp = np.exp(_outputs - maxes)
    return shifted_exp / shifted_exp.sum(axis=-1, keepdims=True)
class ClassificationFunction(ExplicitEnum):
    SIGMOID = "sigmoid"
    SOFTMAX = "softmax"
    NONE = "none"
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True),
    r"""
        function_to_apply (`str`, *optional*, defaults to `"default"`):
            The function to apply to the model outputs in order to retrieve the scores. Accepts four different values:
            - `"default"`: if the model has a single label, will apply the sigmoid function on the output. If the model
              has several labels, will apply the softmax function on the output.
            - `"sigmoid"`: Applies the sigmoid function on the output.
            - `"softmax"`: Applies the softmax function on the output.
            - `"none"`: Does not apply any function on the output.""")
class ImageClassificationPipeline(Pipeline):
    function_to_apply: ClassificationFunction = ClassificationFunction.NONE
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(TF_MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING_NAMES if self.framework == "tf" else MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING_NAMES)
    def _sanitize_parameters(self, top_k=None, function_to_apply=None, timeout=None):
        preprocess_params = {}
        if timeout is not None: preprocess_params["timeout"] = timeout
        postprocess_params = {}
        if top_k is not None: postprocess_params["top_k"] = top_k
        if isinstance(function_to_apply, str): function_to_apply = ClassificationFunction(function_to_apply.lower())
        if function_to_apply is not None: postprocess_params["function_to_apply"] = function_to_apply
        return preprocess_params, {}, postprocess_params
    def __call__(self, images: Union[str, List[str], "Image.Image", List["Image.Image"]], **kwargs): return super().__call__(images, **kwargs)
    def preprocess(self, image, timeout=None):
        image = load_image(image, timeout=timeout)
        model_inputs = self.image_processor(images=image, return_tensors=self.framework)
        if self.framework == "pt": model_inputs = model_inputs.to(self.torch_dtype)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, function_to_apply=None, top_k=5):
        if function_to_apply is None:
            if self.model.config.problem_type == "single_label_classification" or self.model.config.num_labels == 1: function_to_apply = ClassificationFunction.SIGMOID
            elif self.model.config.problem_type == "multi_label_classification" or self.model.config.num_labels > 1: function_to_apply = ClassificationFunction.SOFTMAX
            elif hasattr(self.model.config, "function_to_apply") and function_to_apply is None: function_to_apply = self.model.config.function_to_apply
            else: function_to_apply = ClassificationFunction.NONE
        if top_k > self.model.config.num_labels: top_k = self.model.config.num_labels
        outputs = model_outputs["logits"][0]
        if self.framework == "pt" and outputs.dtype in (torch.bfloat16, torch.float16): outputs = outputs.to(torch.float32).numpy()
        else: outputs = outputs.numpy()
        if function_to_apply == ClassificationFunction.SIGMOID: scores = sigmoid(outputs)
        elif function_to_apply == ClassificationFunction.SOFTMAX: scores = softmax(outputs)
        elif function_to_apply == ClassificationFunction.NONE: scores = outputs
        else: raise ValueError(f"Unrecognized `function_to_apply` argument: {function_to_apply}")
        dict_scores = [{"label": self.model.config.id2label[i], "score": score.item()} for i, score in enumerate(scores)]
        dict_scores.sort(key=lambda x: x["score"], reverse=True)
        if top_k is not None: dict_scores = dict_scores[:top_k]
        return dict_scores
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
