"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import Dict, List, Union
import tensorflow as tf
from keras_nlp.tokenizers import BytePairTokenizer
from tensorflow_text import pad_model_inputs
from ...modeling_tf_utils import keras
from .tokenization_gpt2 import GPT2Tokenizer
class TFGPT2Tokenizer(keras.layers.Layer):
    def __init__(self, vocab: Dict[str, int], merges: List[str], max_length: int = None, pad_token_id: int = None):
        super().__init__()
        self.pad_token_id = pad_token_id
        self.max_length = max_length
        self.vocab = vocab
        self.merges = merges
        self.tf_tokenizer = BytePairTokenizer(vocab, merges, sequence_length=max_length)
    @classmethod
    def from_tokenizer(cls, tokenizer: GPT2Tokenizer, *args, **kwargs):
        merges = [" ".join(m) for m in tokenizer.bpe_ranks.keys()]
        vocab = tokenizer.get_vocab()
        return cls(vocab, merges, *args, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], *init_inputs, **kwargs):
        tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model_name_or_path, *init_inputs, **kwargs)
        return cls.from_tokenizer(tokenizer, *init_inputs, **kwargs)
    @classmethod
    def from_config(cls, config): return cls(**config)
    def get_config(self): return {"vocab": self.vocab, "merges": self.merges, "max_length": self.max_length, "pad_token_id": self.pad_token_id}
    def call(self, x, max_length: int = None):
        input_ids = self.tf_tokenizer(x)
        attention_mask = tf.ones_like(input_ids)
        if self.pad_token_id is not None:
            max_length = max_length if max_length is not None else self.max_length
            if max_length is not None: input_ids, attention_mask = pad_model_inputs(input_ids, max_seq_length=max_length, pad_value=self.pad_token_id)
        return {"attention_mask": attention_mask, "input_ids": input_ids}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
