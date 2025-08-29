"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import torch
from PIL import Image
from ..models.auto import AutoModelForVisualQuestionAnswering, AutoProcessor
from ..utils import requires_backends
from .tools import PipelineTool
class ImageQuestionAnsweringTool(PipelineTool):
    default_checkpoint = "dandelin/vilt-b32-finetuned-vqa"
    description = ("This is a tool that answers a question about an image. It returns a text that is the answer to the question.")
    name = "image_qa"
    pre_processor_class = AutoProcessor
    model_class = AutoModelForVisualQuestionAnswering
    inputs = {"image": {'type': 'image', 'description': 'The image containing the information. Can be a PIL Image or a string path to the image.'}, "question": {"type": "string", "description": "The question in English"}}
    output_type = "string"
    def __init__(self, *args, **kwargs):
        requires_backends(self, ["vision"])
        super().__init__(*args, **kwargs)
    def encode(self, image: "Image", question: str): return self.pre_processor(image, question, return_tensors="pt")
    def forward(self, inputs):
        with torch.no_grad(): return self.model(**inputs).logits
    def decode(self, outputs):
        idx = outputs.argmax(-1).item()
        return self.model.config.id2label[idx]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
