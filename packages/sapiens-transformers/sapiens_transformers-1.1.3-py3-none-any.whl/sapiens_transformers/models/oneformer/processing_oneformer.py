"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List
from ...processing_utils import ProcessorMixin
from ...utils import is_torch_available
if is_torch_available(): import torch
class OneFormerProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "OneFormerImageProcessor"
    tokenizer_class = ("CLIPTokenizer", "CLIPTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, max_seq_length: int = 77, task_seq_length: int = 77, **kwargs):
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        self.max_seq_length = max_seq_length
        self.task_seq_length = task_seq_length
        super().__init__(image_processor, tokenizer)
    def _preprocess_text(self, text_list=None, max_length=77):
        if text_list is None: raise ValueError("tokens cannot be None.")
        tokens = self.tokenizer(text_list, padding="max_length", max_length=max_length, truncation=True)
        attention_masks, input_ids = tokens["attention_mask"], tokens["input_ids"]
        token_inputs = []
        for attn_mask, input_id in zip(attention_masks, input_ids):
            token = torch.tensor(attn_mask) * torch.tensor(input_id)
            token_inputs.append(token.unsqueeze(0))
        token_inputs = torch.cat(token_inputs, dim=0)
        return token_inputs
    def __call__(self, images=None, task_inputs=None, segmentation_maps=None, **kwargs):
        if task_inputs is None: raise ValueError("You have to specify the task_input. Found None.")
        elif images is None: raise ValueError("You have to specify the image. Found None.")
        if not all(task in ["semantic", "instance", "panoptic"] for task in task_inputs): raise ValueError("task_inputs must be semantic, instance, or panoptic.")
        encoded_inputs = self.image_processor(images, task_inputs, segmentation_maps, **kwargs)
        if isinstance(task_inputs, str): task_inputs = [task_inputs]
        if isinstance(task_inputs, List) and all(isinstance(task_input, str) for task_input in task_inputs):
            task_token_inputs = []
            for task in task_inputs:
                task_input = f"the task is {task}"
                task_token_inputs.append(task_input)
            encoded_inputs["task_inputs"] = self._preprocess_text(task_token_inputs, max_length=self.task_seq_length)
        else: raise TypeError("Task Inputs should be a string or a list of strings.")
        if hasattr(encoded_inputs, "text_inputs"):
            texts_list = encoded_inputs.text_inputs
            text_inputs = []
            for texts in texts_list:
                text_input_list = self._preprocess_text(texts, max_length=self.max_seq_length)
                text_inputs.append(text_input_list.unsqueeze(0))
            encoded_inputs["text_inputs"] = torch.cat(text_inputs, dim=0)
        return encoded_inputs
    def encode_inputs(self, images=None, task_inputs=None, segmentation_maps=None, **kwargs):
        if task_inputs is None: raise ValueError("You have to specify the task_input. Found None.")
        elif images is None: raise ValueError("You have to specify the image. Found None.")
        if not all(task in ["semantic", "instance", "panoptic"] for task in task_inputs): raise ValueError("task_inputs must be semantic, instance, or panoptic.")
        encoded_inputs = self.image_processor.encode_inputs(images, task_inputs, segmentation_maps, **kwargs)
        if isinstance(task_inputs, str): task_inputs = [task_inputs]
        if isinstance(task_inputs, List) and all(isinstance(task_input, str) for task_input in task_inputs):
            task_token_inputs = []
            for task in task_inputs:
                task_input = f"the task is {task}"
                task_token_inputs.append(task_input)
            encoded_inputs["task_inputs"] = self._preprocess_text(task_token_inputs, max_length=self.task_seq_length)
        else: raise TypeError("Task Inputs should be a string or a list of strings.")
        if hasattr(encoded_inputs, "text_inputs"):
            texts_list = encoded_inputs.text_inputs
            text_inputs = []
            for texts in texts_list:
                text_input_list = self._preprocess_text(texts, max_length=self.max_seq_length)
                text_inputs.append(text_input_list.unsqueeze(0))
            encoded_inputs["text_inputs"] = torch.cat(text_inputs, dim=0)
        return encoded_inputs
    def post_process_semantic_segmentation(self, *args, **kwargs): return self.image_processor.post_process_semantic_segmentation(*args, **kwargs)
    def post_process_instance_segmentation(self, *args, **kwargs): return self.image_processor.post_process_instance_segmentation(*args, **kwargs)
    def post_process_panoptic_segmentation(self, *args, **kwargs): return self.image_processor.post_process_panoptic_segmentation(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
