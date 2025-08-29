"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import List
import numpy as np
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
from ...utils import is_flax_available, is_tf_available, is_torch_available
class OwlViTProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "OwlViTImageProcessor"
    tokenizer_class = ("CLIPTokenizer", "CLIPTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn("The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor` instead.", FutureWarning)
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        if image_processor is None: raise ValueError("You need to specify an `image_processor`.")
        if tokenizer is None: raise ValueError("You need to specify a `tokenizer`.")
        super().__init__(image_processor, tokenizer)
    def __call__(self, text=None, images=None, query_images=None, padding="max_length", return_tensors="np", **kwargs):
        if text is None and query_images is None and images is None: raise ValueError("You have to specify at least one text or query image or image. All three cannot be none.")
        if text is not None:
            if isinstance(text, str) or (isinstance(text, List) and not isinstance(text[0], List)): encodings = [self.tokenizer(text, padding=padding, return_tensors=return_tensors, **kwargs)]
            elif isinstance(text, List) and isinstance(text[0], List):
                encodings = []
                max_num_queries = max([len(t) for t in text])
                for t in text:
                    if len(t) != max_num_queries: t = t + [" "] * (max_num_queries - len(t))
                    encoding = self.tokenizer(t, padding=padding, return_tensors=return_tensors, **kwargs)
                    encodings.append(encoding)
            else: raise TypeError("Input text should be a string, a list of strings or a nested list of strings")
            if return_tensors == "np":
                input_ids = np.concatenate([encoding["input_ids"] for encoding in encodings], axis=0)
                attention_mask = np.concatenate([encoding["attention_mask"] for encoding in encodings], axis=0)
            elif return_tensors == "jax" and is_flax_available():
                import jax.numpy as jnp
                input_ids = jnp.concatenate([encoding["input_ids"] for encoding in encodings], axis=0)
                attention_mask = jnp.concatenate([encoding["attention_mask"] for encoding in encodings], axis=0)
            elif return_tensors == "pt" and is_torch_available():
                import torch
                input_ids = torch.cat([encoding["input_ids"] for encoding in encodings], dim=0)
                attention_mask = torch.cat([encoding["attention_mask"] for encoding in encodings], dim=0)
            elif return_tensors == "tf" and is_tf_available():
                import tensorflow as tf
                input_ids = tf.stack([encoding["input_ids"] for encoding in encodings], axis=0)
                attention_mask = tf.stack([encoding["attention_mask"] for encoding in encodings], axis=0)
            else: raise ValueError("Target return tensor type could not be returned")
            encoding = BatchEncoding()
            encoding["input_ids"] = input_ids
            encoding["attention_mask"] = attention_mask
        if query_images is not None:
            encoding = BatchEncoding()
            query_pixel_values = self.image_processor(query_images, return_tensors=return_tensors, **kwargs).pixel_values
            encoding["query_pixel_values"] = query_pixel_values
        if images is not None: image_features = self.image_processor(images, return_tensors=return_tensors, **kwargs)
        if text is not None and images is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif query_images is not None and images is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif text is not None or query_images is not None: return encoding
        else: return BatchEncoding(data=dict(**image_features), tensor_type=return_tensors)
    def post_process(self, *args, **kwargs): return self.image_processor.post_process(*args, **kwargs)
    def post_process_object_detection(self, *args, **kwargs): return self.image_processor.post_process_object_detection(*args, **kwargs)
    def post_process_image_guided_detection(self, *args, **kwargs): return self.image_processor.post_process_image_guided_detection(*args, **kwargs)
    def batch_decode(self, *args, **kwargs): return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.tokenizer.decode(*args, **kwargs)
    @property
    def feature_extractor_class(self):
        warnings.warn("`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.", FutureWarning)
        return self.image_processor_class
    @property
    def feature_extractor(self):
        warnings.warn("`feature_extractor` is deprecated and will be removed in v5. Use `image_processor` instead.", FutureWarning)
        return self.image_processor
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
