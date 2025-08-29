"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
import numpy as np
from ..utils import (add_end_docstrings, is_torch_available, is_vision_available, logging, requires_backends)
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available(): from ..models.auto.modeling_auto import MODEL_FOR_IMAGE_TO_IMAGE_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class ImageToImagePipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(MODEL_FOR_IMAGE_TO_IMAGE_MAPPING_NAMES)
    def _sanitize_parameters(self, **kwargs):
        preprocess_params = {}
        postprocess_params = {}
        forward_params = {}
        if "timeout" in kwargs: preprocess_params["timeout"] = kwargs["timeout"]
        if "head_mask" in kwargs: forward_params["head_mask"] = kwargs["head_mask"]
        return preprocess_params, forward_params, postprocess_params
    def __call__(self, images: Union[str, List[str], "Image.Image", List["Image.Image"]], **kwargs) -> Union["Image.Image", List["Image.Image"]]: return super().__call__(images, **kwargs)
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def preprocess(self, image, timeout=None):
        image = load_image(image, timeout=timeout)
        inputs = self.image_processor(images=[image], return_tensors="pt")
        if self.framework == "pt": inputs = inputs.to(self.torch_dtype)
        return inputs
    def postprocess(self, model_outputs):
        images = []
        if "reconstruction" in model_outputs.keys(): outputs = model_outputs.reconstruction
        for output in outputs:
            output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
            output = np.moveaxis(output, source=0, destination=-1)
            output = (output * 255.0).round().astype(np.uint8)
            images.append(Image.fromarray(output))
        return images if len(images) > 1 else images[0]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
