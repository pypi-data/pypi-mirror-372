"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from typing import List, Union
import tensorflow as tf
from tensorflow_text import BertTokenizer as BertTokenizerLayer
from tensorflow_text import FastBertTokenizer, ShrinkLongestTrimmer, case_fold_utf8, combine_segments, pad_model_inputs
from ...modeling_tf_utils import keras
from .tokenization_bert import BertTokenizer
class TFBertTokenizer(keras.layers.Layer):
    def __init__(self, vocab_list: List, do_lower_case: bool, cls_token_id: int = None, sep_token_id: int = None, pad_token_id: int = None, padding: str = "longest", truncation: bool = True,
    max_length: int = 512, pad_to_multiple_of: int = None, return_token_type_ids: bool = True, return_attention_mask: bool = True, use_fast_bert_tokenizer: bool = True, **tokenizer_kwargs):
        super().__init__()
        if use_fast_bert_tokenizer: self.tf_tokenizer = FastBertTokenizer(vocab_list, token_out_type=tf.int64, lower_case_nfd_strip_accents=do_lower_case, **tokenizer_kwargs)
        else:
            lookup_table = tf.lookup.StaticVocabularyTable(tf.lookup.KeyValueTensorInitializer(keys=vocab_list, key_dtype=tf.string, values=tf.range(tf.size(vocab_list, out_type=tf.int64), dtype=tf.int64), value_dtype=tf.int64), num_oov_buckets=1)
            self.tf_tokenizer = BertTokenizerLayer(lookup_table, token_out_type=tf.int64, lower_case=do_lower_case, **tokenizer_kwargs)
        self.vocab_list = vocab_list
        self.do_lower_case = do_lower_case
        self.cls_token_id = vocab_list.index("[CLS]") if cls_token_id is None else cls_token_id
        self.sep_token_id = vocab_list.index("[SEP]") if sep_token_id is None else sep_token_id
        self.pad_token_id = vocab_list.index("[PAD]") if pad_token_id is None else pad_token_id
        self.paired_trimmer = ShrinkLongestTrimmer(max_length - 3, axis=1)
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
        self.pad_to_multiple_of = pad_to_multiple_of
        self.return_token_type_ids = return_token_type_ids
        self.return_attention_mask = return_attention_mask
    @classmethod
    def from_tokenizer(cls, tokenizer: "PreTrainedTokenizerBase", **kwargs):
        do_lower_case = kwargs.pop("do_lower_case", None)
        do_lower_case = tokenizer.do_lower_case if do_lower_case is None else do_lower_case
        cls_token_id = kwargs.pop("cls_token_id", None)
        cls_token_id = tokenizer.cls_token_id if cls_token_id is None else cls_token_id
        sep_token_id = kwargs.pop("sep_token_id", None)
        sep_token_id = tokenizer.sep_token_id if sep_token_id is None else sep_token_id
        pad_token_id = kwargs.pop("pad_token_id", None)
        pad_token_id = tokenizer.pad_token_id if pad_token_id is None else pad_token_id
        vocab = tokenizer.get_vocab()
        vocab = sorted(vocab.items(), key=lambda x: x[1])
        vocab_list = [entry[0] for entry in vocab]
        return cls(vocab_list=vocab_list, do_lower_case=do_lower_case, cls_token_id=cls_token_id, sep_token_id=sep_token_id, pad_token_id=pad_token_id, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], *init_inputs, **kwargs):
        try: tokenizer = BertTokenizer.from_pretrained(pretrained_model_name_or_path, *init_inputs, **kwargs)
        except:
            from .tokenization_bert_fast import BertTokenizerFast
            tokenizer = BertTokenizerFast.from_pretrained(pretrained_model_name_or_path, *init_inputs, **kwargs)
        return cls.from_tokenizer(tokenizer, **kwargs)
    def unpaired_tokenize(self, texts):
        if self.do_lower_case: texts = case_fold_utf8(texts)
        tokens = self.tf_tokenizer.tokenize(texts)
        return tokens.merge_dims(1, -1)
    def call(self, text, text_pair=None, padding=None, truncation=None, max_length=None, pad_to_multiple_of=None, return_token_type_ids=None, return_attention_mask=None):
        if padding is None: padding = self.padding
        if padding not in ("longest", "max_length"): raise ValueError("Padding must be either 'longest' or 'max_length'!")
        if max_length is not None and text_pair is not None: raise ValueError("max_length cannot be overridden at call time when truncating paired texts!")
        if max_length is None: max_length = self.max_length
        if truncation is None: truncation = self.truncation
        if pad_to_multiple_of is None: pad_to_multiple_of = self.pad_to_multiple_of
        if return_token_type_ids is None: return_token_type_ids = self.return_token_type_ids
        if return_attention_mask is None: return_attention_mask = self.return_attention_mask
        if not isinstance(text, tf.Tensor): text = tf.convert_to_tensor(text)
        if text_pair is not None and not isinstance(text_pair, tf.Tensor): text_pair = tf.convert_to_tensor(text_pair)
        if text_pair is not None:
            if text.shape.rank > 1: raise ValueError("text argument should not be multidimensional when a text pair is supplied!")
            if text_pair.shape.rank > 1: raise ValueError("text_pair should not be multidimensional!")
        if text.shape.rank == 2: text, text_pair = text[:, 0], text[:, 1]
        text = self.unpaired_tokenize(text)
        if text_pair is None:
            if truncation: text = text[:, : max_length - 2]
            input_ids, token_type_ids = combine_segments((text,), start_of_sequence_id=self.cls_token_id, end_of_segment_id=self.sep_token_id)
        else:
            text_pair = self.unpaired_tokenize(text_pair)
            if truncation: text, text_pair = self.paired_trimmer.trim([text, text_pair])
            input_ids, token_type_ids = combine_segments((text, text_pair), start_of_sequence_id=self.cls_token_id, end_of_segment_id=self.sep_token_id)
        if padding == "longest":
            pad_length = input_ids.bounding_shape(axis=1)
            if pad_to_multiple_of is not None: pad_length = pad_to_multiple_of * (-tf.math.floordiv(-pad_length, pad_to_multiple_of))
        else: pad_length = max_length
        input_ids, attention_mask = pad_model_inputs(input_ids, max_seq_length=pad_length, pad_value=self.pad_token_id)
        output = {"input_ids": input_ids}
        if return_attention_mask: output["attention_mask"] = attention_mask
        if return_token_type_ids:
            token_type_ids, _ = pad_model_inputs(token_type_ids, max_seq_length=pad_length, pad_value=self.pad_token_id)
            output["token_type_ids"] = token_type_ids
        return output
    def get_config(self): return {"vocab_list": self.vocab_list, "do_lower_case": self.do_lower_case, "cls_token_id": self.cls_token_id, "sep_token_id": self.sep_token_id, "pad_token_id": self.pad_token_id}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
