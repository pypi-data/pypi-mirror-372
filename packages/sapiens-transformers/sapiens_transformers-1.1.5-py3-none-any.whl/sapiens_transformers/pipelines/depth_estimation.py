"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
import numpy as np
from ..utils import add_end_docstrings, is_torch_available, is_vision_available, logging, requires_backends
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_DEPTH_ESTIMATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class DepthEstimationPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(MODEL_FOR_DEPTH_ESTIMATION_MAPPING_NAMES)
    def __call__(self, images: Union[str, List[str], "Image.Image", List["Image.Image"]], **kwargs): return super().__call__(images, **kwargs)
    def _sanitize_parameters(self, timeout=None, **kwargs):
        preprocess_params = {}
        if timeout is not None: preprocess_params["timeout"] = timeout
        return preprocess_params, {}, {}
    def preprocess(self, image, timeout=None):
        image = load_image(image, timeout)
        self.image_size = image.size
        model_inputs = self.image_processor(images=image, return_tensors=self.framework)
        if self.framework == "pt": model_inputs = model_inputs.to(self.torch_dtype)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs):
        predicted_depth = model_outputs.predicted_depth
        prediction = torch.nn.functional.interpolate(predicted_depth.unsqueeze(1), size=self.image_size[::-1], mode="bicubic", align_corners=False)
        output = prediction.squeeze().cpu().numpy()
        formatted = (output * 255 / np.max(output)).astype("uint8")
        depth = Image.fromarray(formatted)
        output_dict = {}
        output_dict["predicted_depth"] = predicted_depth
        output_dict["depth"] = depth
        return output_dict
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
