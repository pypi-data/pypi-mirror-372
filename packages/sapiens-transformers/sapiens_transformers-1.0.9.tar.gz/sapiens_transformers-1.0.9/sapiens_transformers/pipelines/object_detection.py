"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Any, Dict, List, Union
from ..utils import add_end_docstrings, is_torch_available, is_vision_available, logging, requires_backends
from .base import Pipeline, build_pipeline_init_args
if is_vision_available(): from ..image_utils import load_image
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import (MODEL_FOR_OBJECT_DETECTION_MAPPING_NAMES, MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES)
logger = logging.get_logger(__name__)
Prediction = Dict[str, Any]
Predictions = List[Prediction]
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class ObjectDetectionPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.framework == "tf": raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        requires_backends(self, "vision")
        mapping = MODEL_FOR_OBJECT_DETECTION_MAPPING_NAMES.copy()
        mapping.update(MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES)
        self.check_model_type(mapping)
    def _sanitize_parameters(self, **kwargs):
        preprocess_params = {}
        if "timeout" in kwargs: preprocess_params["timeout"] = kwargs["timeout"]
        postprocess_kwargs = {}
        if "threshold" in kwargs: postprocess_kwargs["threshold"] = kwargs["threshold"]
        return preprocess_params, {}, postprocess_kwargs
    def __call__(self, *args, **kwargs) -> Union[Predictions, List[Prediction]]: return super().__call__(*args, **kwargs)
    def preprocess(self, image, timeout=None):
        image = load_image(image, timeout=timeout)
        target_size = torch.IntTensor([[image.height, image.width]])
        inputs = self.image_processor(images=[image], return_tensors="pt")
        if self.framework == "pt": inputs = inputs.to(self.torch_dtype)
        if self.tokenizer is not None: inputs = self.tokenizer(text=inputs["words"], boxes=inputs["boxes"], return_tensors="pt")
        inputs["target_size"] = target_size
        return inputs
    def _forward(self, model_inputs):
        target_size = model_inputs.pop("target_size")
        outputs = self.model(**model_inputs)
        model_outputs = outputs.__class__({"target_size": target_size, **outputs})
        if self.tokenizer is not None: model_outputs["bbox"] = model_inputs["bbox"]
        return model_outputs
    def postprocess(self, model_outputs, threshold=0.5):
        target_size = model_outputs["target_size"]
        if self.tokenizer is not None:
            height, width = target_size[0].tolist()
            def unnormalize(bbox): return self._get_bounding_box(torch.Tensor([(width * bbox[0] / 1000), (height * bbox[1] / 1000), (width * bbox[2] / 1000), (height * bbox[3] / 1000)]))
            scores, classes = model_outputs["logits"].squeeze(0).softmax(dim=-1).max(dim=-1)
            labels = [self.model.config.id2label[prediction] for prediction in classes.tolist()]
            boxes = [unnormalize(bbox) for bbox in model_outputs["bbox"].squeeze(0)]
            keys = ["score", "label", "box"]
            annotation = [dict(zip(keys, vals)) for vals in zip(scores.tolist(), labels, boxes) if vals[0] > threshold]
        else:
            raw_annotations = self.image_processor.post_process_object_detection(model_outputs, threshold, target_size)
            raw_annotation = raw_annotations[0]
            scores = raw_annotation["scores"]
            labels = raw_annotation["labels"]
            boxes = raw_annotation["boxes"]
            raw_annotation["scores"] = scores.tolist()
            raw_annotation["labels"] = [self.model.config.id2label[label.item()] for label in labels]
            raw_annotation["boxes"] = [self._get_bounding_box(box) for box in boxes]
            keys = ["score", "label", "box"]
            annotation = [dict(zip(keys, vals)) for vals in zip(raw_annotation["scores"], raw_annotation["labels"], raw_annotation["boxes"])]
        return annotation
    def _get_bounding_box(self, box: "torch.Tensor") -> Dict[str, int]:
        if self.framework != "pt": raise ValueError("The ObjectDetectionPipeline is only available in PyTorch.")
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
