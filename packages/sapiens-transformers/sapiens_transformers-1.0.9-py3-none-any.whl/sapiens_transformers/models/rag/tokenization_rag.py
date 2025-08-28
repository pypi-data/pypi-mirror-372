"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Optional
from ...tokenization_utils_base import BatchEncoding
from .configuration_rag import RagConfig
class RagTokenizer:
    def __init__(self, question_encoder, generator):
        self.question_encoder = question_encoder
        self.generator = generator
        self.current_tokenizer = self.question_encoder
    def save_pretrained(self, save_directory):
        if os.path.isfile(save_directory): raise ValueError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        question_encoder_path = os.path.join(save_directory, "question_encoder_tokenizer")
        generator_path = os.path.join(save_directory, "generator_tokenizer")
        self.question_encoder.save_pretrained(question_encoder_path)
        self.generator.save_pretrained(generator_path)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        from ..auto.tokenization_auto import AutoTokenizer
        config = kwargs.pop("config", None)
        if config is None: config = RagConfig.from_pretrained(pretrained_model_name_or_path)
        question_encoder = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, config=config.question_encoder, subfolder="question_encoder_tokenizer")
        generator = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, config=config.generator, subfolder="generator_tokenizer")
        return cls(question_encoder=question_encoder, generator=generator)
    def __call__(self, *args, **kwargs): return self.current_tokenizer(*args, **kwargs)
    def batch_decode(self, *args, **kwargs): return self.generator.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs): return self.generator.decode(*args, **kwargs)
    def _switch_to_input_mode(self): self.current_tokenizer = self.question_encoder
    def _switch_to_target_mode(self): self.current_tokenizer = self.generator
    def prepare_seq2seq_batch(self, src_texts: List[str], tgt_texts: Optional[List[str]] = None, max_length: Optional[int] = None, max_target_length: Optional[int] = None,
    padding: str = "longest", return_tensors: str = None, truncation: bool = True, **kwargs) -> BatchEncoding:
        if max_length is None: max_length = self.current_tokenizer.model_max_length
        model_inputs = self(src_texts, add_special_tokens=True, return_tensors=return_tensors, max_length=max_length, padding=padding, truncation=truncation, **kwargs)
        if tgt_texts is None: return model_inputs
        if max_target_length is None: max_target_length = self.current_tokenizer.model_max_length
        labels = self(text_target=tgt_texts, add_special_tokens=True, return_tensors=return_tensors, padding=padding, max_length=max_target_length, truncation=truncation,  **kwargs)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
