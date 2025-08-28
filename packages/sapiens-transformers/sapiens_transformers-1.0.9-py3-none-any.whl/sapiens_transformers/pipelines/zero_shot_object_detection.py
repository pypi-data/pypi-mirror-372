"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, List, Union
from ..utils import add_end_docstrings, is_torch_available, is_vision_available, logging, requires_backends
from .base import ChunkPipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available():
    import torch
    from sapiens_transformers.modeling_outputs import BaseModelOutput
    from ..models.auto.modeling_auto import MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class ZeroShotObjectDetectionPipeline(ChunkPipeline):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.framework == "tf": raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        requires_backends(self, "vision")
        self.check_model_type(MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING_NAMES)
    def __call__(self, image: Union[str, "Image.Image", List[Dict[str, Any]]], candidate_labels: Union[str, List[str]] = None, **kwargs):
        if "text_queries" in kwargs: candidate_labels = kwargs.pop("text_queries")
        if isinstance(image, (str, Image.Image)): inputs = {"image": image, "candidate_labels": candidate_labels}
        else: inputs = image
        results = super().__call__(inputs, **kwargs)
        return results
    def _sanitize_parameters(self, **kwargs):
        preprocess_params = {}
        if "timeout" in kwargs: preprocess_params["timeout"] = kwargs["timeout"]
        postprocess_params = {}
        if "threshold" in kwargs: postprocess_params["threshold"] = kwargs["threshold"]
        if "top_k" in kwargs: postprocess_params["top_k"] = kwargs["top_k"]
        return preprocess_params, {}, postprocess_params
    def preprocess(self, inputs, timeout=None):
        image = load_image(inputs["image"], timeout=timeout)
        candidate_labels = inputs["candidate_labels"]
        if isinstance(candidate_labels, str): candidate_labels = candidate_labels.split(",")
        target_size = torch.tensor([[image.height, image.width]], dtype=torch.int32)
        for i, candidate_label in enumerate(candidate_labels):
            text_inputs = self.tokenizer(candidate_label, return_tensors=self.framework)
            image_features = self.image_processor(image, return_tensors=self.framework)
            if self.framework == "pt": image_features = image_features.to(self.torch_dtype)
            yield {"is_last": i == len(candidate_labels) - 1, "target_size": target_size, "candidate_label": candidate_label, **text_inputs, **image_features}
    def _forward(self, model_inputs):
        target_size = model_inputs.pop("target_size")
        candidate_label = model_inputs.pop("candidate_label")
        is_last = model_inputs.pop("is_last")
        outputs = self.model(**model_inputs)
        model_outputs = {"target_size": target_size, "candidate_label": candidate_label, "is_last": is_last, **outputs}
        return model_outputs
    def postprocess(self, model_outputs, threshold=0.1, top_k=None):
        results = []
        for model_output in model_outputs:
            label = model_output["candidate_label"]
            model_output = BaseModelOutput(model_output)
            outputs = self.image_processor.post_process_object_detection(outputs=model_output, threshold=threshold, target_sizes=model_output["target_size"])[0]
            for index in outputs["scores"].nonzero():
                score = outputs["scores"][index].item()
                box = self._get_bounding_box(outputs["boxes"][index][0])
                result = {"score": score, "label": label, "box": box}
                results.append(result)
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        if top_k: results = results[:top_k]
        return results
    def _get_bounding_box(self, box: "torch.Tensor") -> Dict[str, int]:
        if self.framework != "pt": raise ValueError("The ZeroShotObjectDetectionPipeline is only available in PyTorch.")
        xmin, ymin, xmax, ymax = box.int().tolist()
        bbox = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
        return bbox
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
