"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Union
from ..utils import add_end_docstrings, is_torch_available, is_vision_available, logging
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available():
    from ..models.auto.modeling_auto import MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING_NAMES
    from .pt_utils import KeyDataset
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True, has_image_processor=True))
class VisualQuestionAnsweringPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_model_type(MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING_NAMES)
    def _sanitize_parameters(self, top_k=None, padding=None, truncation=None, timeout=None, **kwargs):
        preprocess_params, postprocess_params = {}, {}
        if padding is not None: preprocess_params["padding"] = padding
        if truncation is not None: preprocess_params["truncation"] = truncation
        if timeout is not None: preprocess_params["timeout"] = timeout
        if top_k is not None: postprocess_params["top_k"] = top_k
        return preprocess_params, {}, postprocess_params
    def __call__(self, image: Union["Image.Image", str, List["Image.Image"], List[str], "KeyDataset"], question: Union[str, List[str]] = None, **kwargs):
        is_dataset = isinstance(image, KeyDataset)
        is_image_batch = isinstance(image, list) and all(isinstance(item, (Image.Image, str)) for item in image)
        is_question_batch = isinstance(question, list) and all(isinstance(item, str) for item in question)
        if isinstance(image, (Image.Image, str)) and isinstance(question, str): inputs = {"image": image, "question": question}
        elif (is_image_batch or is_dataset) and isinstance(question, str): inputs = [{"image": im, "question": question} for im in image]
        elif isinstance(image, (Image.Image, str)) and is_question_batch: inputs = [{"image": image, "question": q} for q in question]
        elif (is_image_batch or is_dataset) and is_question_batch:
            question_image_pairs = []
            for q in question:
                for im in image: question_image_pairs.append({"image": im, "question": q})
            inputs = question_image_pairs
        else: inputs = image
        results = super().__call__(inputs, **kwargs)
        return results
    def preprocess(self, inputs, padding=False, truncation=False, timeout=None):
        image = load_image(inputs["image"], timeout=timeout)
        model_inputs = self.tokenizer(inputs["question"], return_tensors=self.framework, padding=padding, truncation=truncation)
        image_features = self.image_processor(images=image, return_tensors=self.framework)
        if self.framework == "pt": image_features = image_features.to(self.torch_dtype)
        model_inputs.update(image_features)
        return model_inputs
    def _forward(self, model_inputs, **generate_kwargs):
        if self.model.can_generate():
            if "generation_config" not in generate_kwargs: generate_kwargs["generation_config"] = self.generation_config
            model_outputs = self.model.generate(**model_inputs, **generate_kwargs)
        else: model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, top_k=5):
        if self.model.can_generate(): return [{"answer": self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()} for output_ids in model_outputs]
        else:
            if top_k > self.model.config.num_labels: top_k = self.model.config.num_labels
            if self.framework == "pt":
                probs = model_outputs.logits.sigmoid()[0]
                scores, ids = probs.topk(top_k)
            else: raise ValueError(f"Unsupported framework: {self.framework}")
            scores = scores.tolist()
            ids = ids.tolist()
            return [{"score": score, "answer": self.model.config.id2label[_id]} for score, _id in zip(scores, ids)]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
