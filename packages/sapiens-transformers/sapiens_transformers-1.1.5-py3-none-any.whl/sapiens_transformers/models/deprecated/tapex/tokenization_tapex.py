"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import random
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union
import regex as re
from ....file_utils import ExplicitEnum, PaddingStrategy, TensorType, add_end_docstrings, is_pandas_available
from ....tokenization_utils import AddedToken, PreTrainedTokenizer
from ....tokenization_utils_base import ENCODE_KWARGS_DOCSTRING, BatchEncoding, TextInput, TruncationStrategy
from ....utils import logging
if is_pandas_available(): import pandas as pd
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json", "merges_file": "merges.txt"}
class TapexTruncationStrategy(ExplicitEnum): DROP_ROWS_TO_FIT = "drop_rows_to_fit"
TAPEX_ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING = r"""
            add_special_tokens (`bool`, *optional*, defaults to `True`):
                Whether or not to encode the sequences with the special tokens relative to their model.
            padding (`bool`, `str` or [`~file_utils.PaddingStrategy`], *optional*, defaults to `False`):
                Activates and controls padding. Accepts the following values:
                - `True` or `'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
                  sequence if provided).
                - `'max_length'`: Pad to a maximum length specified with the argument `max_length` or to the maximum
                  acceptable input length for the model if that argument is not provided.
                - `False` or `'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of different
                  lengths).
            truncation (`bool`, `str`, [`TapexTruncationStrategy`] or [`~tokenization_utils_base.TruncationStrategy`],
                   *optional*, defaults to `False`):
                Activates and controls truncation. Accepts the following values:
                - `'drop_rows_to_fit'`: Truncate to a maximum length specified with the argument `max_length` or to the
                  maximum acceptable input length for the model if that argument is not provided. This will truncate
                  row by row, removing rows from the table.
                - `True` or `'longest_first'`: Truncate to a maximum length specified with the argument `max_length` or
                  to the maximum acceptable input length for the model if that argument is not provided. This will
                  truncate token by token, removing a token from the longest sequence in the pair if a pair of
                  sequences (or a batch of pairs) is provided.
                - `'only_first'`: Truncate to a maximum length specified with the argument `max_length` or to the
                  maximum acceptable input length for the model if that argument is not provided. This will only
                  truncate the first sequence of a pair if a pair of sequences (or a batch of pairs) is provided.
                - `'only_second'`: Truncate to a maximum length specified with the argument `max_length` or to the
                  maximum acceptable input length for the model if that argument is not provided. This will only
                  truncate the second sequence of a pair if a pair of sequences (or a batch of pairs) is provided.
                - `False` or `'do_not_truncate'` (default): No truncation (i.e., can output batch with sequence lengths
                  greater than the model maximum admissible input size).
            max_length (`int`, *optional*):
                Controls the maximum length to use by one of the truncation/padding parameters. If left unset or set to
                `None`, this will use the predefined model maximum length if a maximum length is required by one of the
                truncation/padding parameters. If the model has no specific maximum input length (like XLNet)
                truncation/padding to a maximum length will be deactivated.
            stride (`int`, *optional*, defaults to 0):
                If set to a number along with `max_length`, the overflowing tokens returned when
                `return_overflowing_tokens=True` will contain some tokens from the end of the truncated sequence
                returned to provide some overlap between truncated and overflowing sequences. The value of this
                argument defines the number of overlapping tokens.
            pad_to_multiple_of (`int`, *optional*):
                If set will pad the sequence to a multiple of the provided value. This is especially useful to enable
                the use of Tensor Cores on NVIDIA hardware with compute capability `>= 7.5` (Volta).
            return_tensors (`str` or [`~file_utils.TensorType`], *optional*):
                If set, will return tensors instead of list of python integers. Acceptable values are:
                - `'tf'`: Return TensorFlow `tf.constant` objects.
                - `'pt'`: Return PyTorch `torch.Tensor` objects.
                - `'np'`: Return Numpy `np.ndarray` objects.
"""
@lru_cache()
def bytes_to_unicode():
    bs = (list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1)))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))
def get_pairs(word):
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs
class IndexedRowTableLinearize:
    def process_table(self, table_content: Dict):
        assert "header" in table_content and "rows" in table_content, self.PROMPT_MESSAGE
        table_str = self.process_header(table_content["header"]) + " "
        for i, row_example in enumerate(table_content["rows"]): table_str += self.process_row(row_example, row_index=i + 1) + " "
        return table_str.strip()
    def process_header(self, headers: List): return "col : " + " | ".join(headers)
    def process_row(self, row: List, row_index: int):
        row_str = ""
        row_cell_values = []
        for cell_value in row:
            if isinstance(cell_value, int): row_cell_values.append(str(cell_value))
            else: row_cell_values.append(cell_value)
        row_str += " | ".join(row_cell_values)
        return "row " + str(row_index) + " : " + row_str
class TapexTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, merges_file, do_lower_case=True, errors="replace", bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>",
    unk_token="<unk>", pad_token="<pad>", mask_token="<mask>", add_prefix_space=False, max_cell_length=15, **kwargs):
        bos_token = AddedToken(bos_token, lstrip=False, rstrip=False) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, lstrip=False, rstrip=False) if isinstance(eos_token, str) else eos_token
        sep_token = AddedToken(sep_token, lstrip=False, rstrip=False) if isinstance(sep_token, str) else sep_token
        cls_token = AddedToken(cls_token, lstrip=False, rstrip=False) if isinstance(cls_token, str) else cls_token
        unk_token = AddedToken(unk_token, lstrip=False, rstrip=False) if isinstance(unk_token, str) else unk_token
        pad_token = AddedToken(pad_token, lstrip=False, rstrip=False) if isinstance(pad_token, str) else pad_token
        mask_token = AddedToken(mask_token, lstrip=True, rstrip=False) if isinstance(mask_token, str) else mask_token
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.errors = errors
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: bpe_merges = merges_handle.read().split("\n")[1:-1]
        bpe_merges = [tuple(merge.split()) for merge in bpe_merges]
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}
        self.add_prefix_space = add_prefix_space
        self.do_lower_case = do_lower_case
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
        super().__init__(vocab_file=vocab_file, merges_file=merges_file, do_lower_case=do_lower_case, errors=errors, bos_token=bos_token, eos_token=eos_token, unk_token=unk_token,
        sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, mask_token=mask_token, add_prefix_space=add_prefix_space, max_cell_length=max_cell_length, **kwargs)
        self.max_cell_length = max_cell_length
        self.table_linearize = IndexedRowTableLinearize()
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + ([0] * len(token_ids_0)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        add_prefix_space = kwargs.pop("add_prefix_space", self.add_prefix_space)
        if (is_split_into_words or add_prefix_space) and (len(text) > 0 and not text[0].isspace()): text = " " + text
        return (text, kwargs)
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def bpe(self, token):
        if token in self.cache: return self.cache[token]
        word = tuple(token)
        pairs = get_pairs(word)
        if not pairs: return token
        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float("inf")))
            if bigram not in self.bpe_ranks: break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try: j = word.index(first, i)
                except ValueError:
                    new_word.extend(word[i:])
                    break
                else:
                    new_word.extend(word[i:j])
                    i = j
                if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1: break
            else: pairs = get_pairs(word)
        word = " ".join(word)
        self.cache[token] = word
        return word
    def _tokenize(self, text):
        bpe_tokens = []
        for token in re.findall(self.pat, text):
            token = "".join(self.byte_encoder[b] for b in token.encode("utf-8"))
            bpe_tokens.extend(bpe_token for bpe_token in self.bpe(token).split(" "))
        return bpe_tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index)
    def convert_tokens_to_string(self, tokens):
        text = "".join(tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode("utf-8", errors=self.errors)
        return text
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        merge_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.encoder, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        index = 0
        with open(merge_file, "w", encoding="utf-8") as writer:
            writer.write("#version: 0.2\n")
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {merge_file}: BPE merge indices are not consecutive. Please check that the tokenizer is not corrupted!")
                    index = token_index
                writer.write(" ".join(bpe_tokens) + "\n")
                index += 1
        return vocab_file, merge_file
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, TAPEX_ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def __call__(self, table: Union["pd.DataFrame", List["pd.DataFrame"]] = None, query: Optional[Union[TextInput, List[TextInput]]] = None, answer: Union[str, List[str]] = None,
    add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None,
    stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if table is not None:
            return self.source_call_func(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length,
            stride=stride, pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
            return_length=return_length, verbose=verbose, **kwargs)
        elif answer is not None:
            return self.target_call_func(answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride,
            pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
            return_length=return_length, verbose=verbose, **kwargs)
        else: raise ValueError("You need to provide either a `table` or an `answer`.")
    def source_call_func(self, table: Union["pd.DataFrame", List["pd.DataFrame"]], query: Optional[Union[TextInput, List[TextInput]]] = None, answer: Union[str, List[str]] = None,
    add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None,
    stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, **kwargs) -> BatchEncoding:
        valid_table = False
        valid_query = False
        if isinstance(table, pd.DataFrame): valid_table = True
        elif isinstance(table, (list, tuple)) and isinstance(table[0], pd.DataFrame): valid_table = True
        if query is None or isinstance(query, str): valid_query = True
        elif isinstance(query, (list, tuple)):
            if len(query) == 0 or isinstance(query[0], str): valid_query = True
        if not valid_table: raise ValueError("table input must of type `pd.DataFrame` (single example), `List[pd.DataFrame]` (batch of examples). ")
        if not valid_query: raise ValueError("query input must of type `str` (single example), `List[str]` (batch of examples). ")
        is_batched = isinstance(table, (list, tuple)) or isinstance(query, (list, tuple))
        if is_batched:
            return self.batch_encode_plus(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
            return_length=return_length, verbose=verbose, **kwargs)
        else:
            return self.encode_plus(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
            return_length=return_length, verbose=verbose, **kwargs)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, TAPEX_ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def batch_encode_plus(self, table: Union["pd.DataFrame", List["pd.DataFrame"]], query: Optional[List[TextInput]] = None, answer: List[str] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str] = None, max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        return self._batch_encode_plus(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
    def _batch_encode_plus(self, table: Union["pd.DataFrame", List["pd.DataFrame"]], query: Optional[List[TextInput]] = None, answer: Optional[List[str]] = None, add_special_tokens: bool = True,
    padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None,
    stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        if isinstance(table, pd.DataFrame) and isinstance(query, (list, tuple)): table = [table] * len(query)
        if isinstance(table, (list, tuple)) and isinstance(query, str): query = [query] * len(table)
        batch_outputs = self._batch_prepare_for_model(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy,
        max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens,
        return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, return_tensors=return_tensors, verbose=verbose)
        return BatchEncoding(batch_outputs)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, TAPEX_ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def _batch_prepare_for_model(self, table: Union["pd.DataFrame", List["pd.DataFrame"]], query: Optional[Union[TextInput, List[TextInput]]] = None, answer: Optional[Union[str, List[str]]] = None,
    add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[str] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_length: bool = False, verbose: bool = True) -> BatchEncoding:
        batch_outputs = {}
        if answer is None: answer = [None] * len(table)
        for _table, _query, _answer in zip(table, query, answer):
            text = self.prepare_table_query(_table, _query, _answer, truncation_strategy=truncation_strategy, max_length=max_length)
            if self.do_lower_case: text = text.lower()
            tokens = self.tokenize(text)
            outputs = self.prepare_for_model(ids=self.convert_tokens_to_ids(tokens), add_special_tokens=add_special_tokens, padding=PaddingStrategy.DO_NOT_PAD.value,
            truncation=truncation_strategy.value, max_length=max_length, stride=stride, pad_to_multiple_of=None, return_attention_mask=False, return_token_type_ids=return_token_type_ids,
            return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, return_tensors=None,
            prepend_batch_axis=False, verbose=verbose)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(batch_outputs, padding=padding_strategy.value, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return batch_outputs
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING)
    def encode(self, table: "pd.DataFrame", query: Optional[TextInput] = None, answer: Optional[str] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy, TapexTruncationStrategy] = None, max_length: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> List[int]:
        encoded_inputs = self.encode_plus(table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, return_tensors=return_tensors, **kwargs)
        return encoded_inputs["input_ids"]
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, TAPEX_ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def encode_plus(self, table: "pd.DataFrame", query: Optional[TextInput] = None, answer: Optional[str] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str] = None, max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of,
        verbose=verbose, **kwargs)
        return self._encode_plus(table=table, query=query, answer=answer, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy,
        max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
    def _encode_plus(self, table: "pd.DataFrame", query: Optional[TextInput] = None, answer: Optional[str] = None, add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
    truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        text = self.prepare_table_query(table, query, answer, truncation_strategy=truncation_strategy, max_length=max_length)
        if self.do_lower_case: text = text.lower()
        tokens = self.tokenize(text)
        return self.prepare_for_model(ids=self.convert_tokens_to_ids(tokens), add_special_tokens=add_special_tokens, padding=padding_strategy.value, truncation=truncation_strategy.value,
        max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, prepend_batch_axis=True, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, verbose=verbose)
    def target_call_func(self, answer: Union[str, List[str]], add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        is_batched = isinstance(answer, (list, tuple))
        if is_batched:
            return self.target_batch_encode_plus(answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of,
            return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
        else:
            return self.target_encode_plus(answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of,
            return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
    def target_batch_encode_plus(self, answer: List[str], add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str] = None,
    max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        return self._target_batch_encode_plus(answer=answer, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy,
        max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
        return_length=return_length, verbose=verbose, **kwargs)
    def _target_batch_encode_plus(self, answer: List[str], add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        batch_outputs = {}
        for text in answer:
            if self.do_lower_case: text = text.lower()
            tokens = self.tokenize(text)
            outputs = self.prepare_for_model(ids=self.convert_tokens_to_ids(tokens), add_special_tokens=add_special_tokens, padding=PaddingStrategy.DO_NOT_PAD.value, truncation=truncation_strategy.value,
            max_length=max_length, stride=stride, pad_to_multiple_of=None, return_attention_mask=False, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, return_tensors=None, prepend_batch_axis=False, verbose=verbose)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(batch_outputs, padding=padding_strategy.value, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, return_attention_mask=return_attention_mask)
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return BatchEncoding(batch_outputs)
    def target_encode(self, answer: str, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy, TapexTruncationStrategy] = None,
    max_length: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> List[int]:
        encoded_outputs = self.target_encode_plus(answer=answer, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, return_tensors=return_tensors, **kwargs)
        return encoded_outputs["input_ids"]
    def target_encode_plus(self, answer: str, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str] = None, max_length: Optional[int] = None,
    pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        return self._target_encode_plus(answer=answer, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length,
        pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
        return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, **kwargs)
    def _target_encode_plus(self, answer: str, add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        text = answer
        if self.do_lower_case: text = text.lower()
        tokens = self.tokenize(text)
        return self.prepare_for_model(ids=self.convert_tokens_to_ids(tokens), add_special_tokens=add_special_tokens, padding=padding_strategy.value, truncation=truncation_strategy.value,
        max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of, return_tensors=return_tensors, prepend_batch_axis=True, return_attention_mask=return_attention_mask,
        return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, verbose=verbose)
    def prepare_table_query(self, table, query, answer=None, truncation_strategy=Union[str, TruncationStrategy, TapexTruncationStrategy], max_length=None):
        if not table.empty:
            table_content = {"header": list(table.columns), "rows": [list(row.values) for i, row in table.iterrows()]}
            self.truncate_table_cells(table_content, query, answer)
            if truncation_strategy == TapexTruncationStrategy.DROP_ROWS_TO_FIT: self.truncate_table_rows(table_content, query, answer, max_length=max_length)
            linear_table = self.table_linearize.process_table(table_content)
        else: linear_table = ""
        if linear_table == "": logger.warning(f"You provide an empty table, or all cells contain much tokens (e.g., >= 1024 tokens). Please carefully check the corresponding table with the query : {query}.")
        if query == "": logger.warning("You provide nothing to query with respect to the table.")
        separator = " " if query and linear_table else ""
        joint_input = (query + separator + linear_table) if query else linear_table
        return joint_input
    def truncate_table_cells(self, table_content: Dict, question: str, answer: List):
        cell_mapping = {}
        for row in table_content["rows"]:
            for i, cell in enumerate(row):
                truncate_cell = self.truncate_cell(cell)
                if truncate_cell is not None:
                    cell_mapping[cell] = truncate_cell
                    row[i] = truncate_cell
        if answer is not None:
            for i, case in enumerate(answer):
                if case in cell_mapping.keys(): answer[i] = cell_mapping[case]
    def truncate_cell(self, cell_value):
        if isinstance(cell_value, int) or isinstance(cell_value, float): return cell_value
        if cell_value.strip() != "":
            try_tokens = self.tokenize(cell_value)
            if len(try_tokens) >= self.max_cell_length:
                retain_tokens = try_tokens[: self.max_cell_length]
                retain_cell_value = self.convert_tokens_to_string(retain_tokens)
                return retain_cell_value
            else: return None
        else: return cell_value
    def truncate_table_rows(self, table_content: Dict, question: str, answer: Optional[Union[str, List[str]]] = None, max_length=None):
        delete_ratio, remain_token_len = self.estimate_delete_ratio(table_content, question, max_length)
        self.delete_unrelated_rows(table_content, question, answer, delete_ratio)
        maximum_keep_rows = 0
        for ind, row_example in enumerate(table_content["rows"]):
            value_string = self.table_linearize.process_row(row_example, ind + 1)
            value_token_len = len(self.tokenize(value_string))
            if value_token_len > remain_token_len: break
            remain_token_len -= value_token_len
            maximum_keep_rows += 1
        del table_content["rows"][maximum_keep_rows:]
    def estimate_delete_ratio(self, table_content: Dict, question: str, max_length=None):
        if "header" not in table_content or "rows" not in table_content: raise ValueError("The table content should contain both 'header' and 'rows' keys.")
        question_tokens = self.tokenize(question, add_special_tokens=True)
        header_string = self.table_linearize.process_header(table_content["header"])
        header_tokens = self.tokenize(header_string, add_special_tokens=False)
        used_token_len = len(question_tokens) + len(header_tokens)
        remain_token_len = max_length - used_token_len
        value_string = ""
        for _, row_example in enumerate(table_content["rows"]): value_string += self.table_linearize.process_row(row_example, 100) + " "
        value_token_len = len(self.tokenize(value_string))
        if value_token_len < remain_token_len: return 0.0, remain_token_len
        else: return 1.0 - remain_token_len / value_token_len, remain_token_len
    def delete_unrelated_rows(self, table_content: Dict, question: str, answer: List, delete_ratio: float):
        truncated_unrelated_indices = []
        related_indices = []
        if answer is None or len(answer) == 0: answer_set = set()
        else: answer_set = {ans_ex.lower() for ans_ex in answer}
        if question is not None: answer_set.update(question.split())
        question_set = set(question.strip("?!.,").split(" "))
        row_max_len = len(table_content["rows"])
        for _row_idx, row in enumerate(table_content["rows"]):
            lower_row = {str(cell).lower() for cell in row}
            if len(lower_row & answer_set) == 0 and len(lower_row & question_set) == 0: truncated_unrelated_indices.append(_row_idx)
            else: related_indices.extend([_row_idx - 2, _row_idx - 1, _row_idx, _row_idx + 1, _row_idx + 2])
        truncated_unrelated_indices = [_row_idx for _row_idx in truncated_unrelated_indices if _row_idx not in related_indices]
        drop_items = min(len(truncated_unrelated_indices), int(len(table_content["rows"]) * delete_ratio))
        drop_row_indices = random.choices(truncated_unrelated_indices, k=drop_items)
        for _row_idx in reversed(range(row_max_len)):
            if _row_idx in drop_row_indices: del table_content["rows"][_row_idx]
        if "id" in table_content and len(drop_row_indices) > 0: logger.warning("Delete {:.2f} rows in table {}".format(len(drop_row_indices), table_content["id"]))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
