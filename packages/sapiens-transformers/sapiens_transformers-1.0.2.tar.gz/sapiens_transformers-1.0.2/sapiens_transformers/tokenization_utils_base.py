"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (ExplicitEnum, PaddingStrategy, PushToHubMixin, TensorType, add_end_docstrings, add_model_info_to_auto_map, add_model_info_to_custom_pipelines,
cached_file, copy_func, download_url, extract_commit_hash, get_json_schema, is_flax_available, is_jax_tensor, is_mlx_available, is_numpy_array, is_offline_mode,
is_protobuf_available, is_remote_url, is_tf_available, is_tf_tensor, is_tokenizers_available, is_torch_available, is_torch_device, is_torch_tensor, logging,
requires_backends, to_py_obj)
from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Union
from .utils.chat_template_utils import _compile_jinja_template, _render_with_assistant_indices
from .utils.import_utils import PROTOBUF_IMPORT_ERROR
from .dynamic_module_utils import custom_object_save
from collections.abc import Mapping, Sized
from contextlib import contextmanager
from dataclasses import dataclass
from collections import UserDict
from inspect import isfunction
from packaging import version
from . import __version__
import numpy as np
import warnings
import copy
import json
import os
import re
if TYPE_CHECKING:
    if is_torch_available(): import torch
    if is_tf_available(): import tensorflow as tf
    if is_flax_available(): import jax.numpy as jnp
def import_protobuf_decode_error(error_message=""):
    if is_protobuf_available():
        from google.protobuf.message import DecodeError
        return DecodeError
    else: raise ImportError(PROTOBUF_IMPORT_ERROR.format(error_message))
if is_tokenizers_available():
    from tokenizers import AddedToken
    from tokenizers import Encoding as EncodingFast
else:
    @dataclass(frozen=False, eq=True)
    class AddedToken:
        def __init__(self, content: str, single_word=False, lstrip=False, rstrip=False, special=False, normalized=None):
            self.content = content
            self.single_word = single_word
            self.lstrip = lstrip
            self.rstrip = rstrip
            self.special = special
            self.normalized = normalized if normalized is not None else not special
        def __getstate__(self): return self.__dict__
        def __str__(self): return self.content
    @dataclass
    class EncodingFast: pass
logger = logging.get_logger(__name__)
VERY_LARGE_INTEGER = int(1e30)
LARGE_INTEGER = int(1e20)
TextInput = SapiensTextInput = str
PreTokenizedInput = SapiensPreTokenizedInput = List[str]
EncodedInput = List[int]
TextInputPair = Tuple[str, str]
PreTokenizedInputPair = Tuple[List[str], List[str]]
EncodedInputPair = Tuple[List[int], List[int]]
AudioInput = Union["np.ndarray", "torch.Tensor", List["np.ndarray"], List["torch.Tensor"]]
SPECIAL_TOKENS_MAP_FILE = "special_tokens_map.json"
ADDED_TOKENS_FILE = "added_tokens.json"
TOKENIZER_CONFIG_FILE = "tokenizer_config.json"
FULL_TOKENIZER_FILE = "tokenizer.json"
_re_tokenizer_file = re.compile(r"tokenizer\.(.*)\.json")
class TruncationStrategy(ExplicitEnum):
    ONLY_FIRST = "only_first"
    ONLY_SECOND = "only_second"
    LONGEST_FIRST = "longest_first"
    DO_NOT_TRUNCATE = "do_not_truncate"
class CharSpan(NamedTuple):
    start: int
    end: int
class TokenSpan(NamedTuple):
    start: int
    end: int
class BatchEncoding(UserDict):
    def __init__(self, data: Optional[Dict[str, Any]] = None, encoding: Optional[Union[EncodingFast, Sequence[EncodingFast]]] = None, tensor_type: Union[None, str, TensorType] = None, prepend_batch_axis: bool = False, n_sequences: Optional[int] = None):
        super().__init__(data)
        if isinstance(encoding, EncodingFast): encoding = [encoding]
        self._encodings = encoding
        if n_sequences is None and encoding is not None and len(encoding): n_sequences = encoding[0].n_sequences
        self._n_sequences = n_sequences
        self.convert_to_tensors(tensor_type=tensor_type, prepend_batch_axis=prepend_batch_axis)
    @property
    def n_sequences(self) -> Optional[int]: return self._n_sequences
    @property
    def is_fast(self) -> bool: return self._encodings is not None
    def __getitem__(self, item: Union[int, str]) -> Union[Any, EncodingFast]:
        if isinstance(item, str): return self.data[item]
        elif self._encodings is not None: return self._encodings[item]
        elif isinstance(item, slice): return {key: self.data[key][item] for key in self.data.keys()}
        else: raise KeyError("Invalid key. Only three types of key are available: (1) string, (2) integers for backend Encoding, and (3) slices for data subsetting.")
    def __getattr__(self, item: str):
        try: return self.data[item]
        except KeyError: raise AttributeError
    def __getstate__(self): return {"data": self.data, "encodings": self._encodings}
    def __setstate__(self, state):
        if "data" in state: self.data = state["data"]
        if "encodings" in state: self._encodings = state["encodings"]
    def keys(self): return self.data.keys()
    def values(self): return self.data.values()
    def items(self): return self.data.items()
    @property
    def encodings(self) -> Optional[List[EncodingFast]]: return self._encodings
    def tokens(self, batch_index: int = 0) -> List[str]:
        if not self._encodings: raise ValueError("tokens() is not available when using non-fast tokenizers (e.g. instance of a `XxxTokenizerFast` class).")
        return self._encodings[batch_index].tokens
    def sequence_ids(self, batch_index: int = 0) -> List[Optional[int]]:
        if not self._encodings: raise ValueError("sequence_ids() is not available when using non-fast tokenizers (e.g. instance of a `XxxTokenizerFast` class).")
        return self._encodings[batch_index].sequence_ids
    def words(self, batch_index: int = 0) -> List[Optional[int]]:
        if not self._encodings: raise ValueError("words() is not available when using non-fast tokenizers (e.g. instance of a `XxxTokenizerFast` class).")
        warnings.warn("`BatchEncoding.words()` property is deprecated and should be replaced with the identical, but more self-explanatory `BatchEncoding.word_ids()` property.", FutureWarning)
        return self.word_ids(batch_index)
    def word_ids(self, batch_index: int = 0) -> List[Optional[int]]:
        if not self._encodings: raise ValueError("word_ids() is not available when using non-fast tokenizers (e.g. instance of a `XxxTokenizerFast` class).")
        return self._encodings[batch_index].word_ids
    def token_to_sequence(self, batch_or_token_index: int, token_index: Optional[int] = None) -> int:
        if not self._encodings: raise ValueError("token_to_sequence() is not available when using Python based tokenizers")
        if token_index is not None: batch_index = batch_or_token_index
        else:
            batch_index = 0
            token_index = batch_or_token_index
        if batch_index < 0: batch_index = self._batch_size + batch_index
        if token_index < 0: token_index = self._seq_len + token_index
        return self._encodings[batch_index].token_to_sequence(token_index)
    def token_to_word(self, batch_or_token_index: int, token_index: Optional[int] = None) -> int:
        if not self._encodings: raise ValueError("token_to_word() is not available when using Python based tokenizers")
        if token_index is not None: batch_index = batch_or_token_index
        else:
            batch_index = 0
            token_index = batch_or_token_index
        if batch_index < 0: batch_index = self._batch_size + batch_index
        if token_index < 0: token_index = self._seq_len + token_index
        return self._encodings[batch_index].token_to_word(token_index)
    def word_to_tokens(self, batch_or_word_index: int, word_index: Optional[int] = None, sequence_index: int = 0) -> Optional[TokenSpan]:
        if not self._encodings: raise ValueError("word_to_tokens() is not available when using Python based tokenizers")
        if word_index is not None: batch_index = batch_or_word_index
        else:
            batch_index = 0
            word_index = batch_or_word_index
        if batch_index < 0: batch_index = self._batch_size + batch_index
        if word_index < 0: word_index = self._seq_len + word_index
        span = self._encodings[batch_index].word_to_tokens(word_index, sequence_index)
        return TokenSpan(*span) if span is not None else None
    def token_to_chars(self, batch_or_token_index: int, token_index: Optional[int] = None) -> CharSpan:
        if not self._encodings: raise ValueError("token_to_chars() is not available when using Python based tokenizers")
        if token_index is not None: batch_index = batch_or_token_index
        else:
            batch_index = 0
            token_index = batch_or_token_index
        span_indices = self._encodings[batch_index].token_to_chars(token_index)
        return CharSpan(*span_indices) if span_indices is not None else None
    def char_to_token(self, batch_or_char_index: int, char_index: Optional[int] = None, sequence_index: int = 0) -> int:
        if not self._encodings: raise ValueError("char_to_token() is not available when using Python based tokenizers")
        if char_index is not None: batch_index = batch_or_char_index
        else:
            batch_index = 0
            char_index = batch_or_char_index
        return self._encodings[batch_index].char_to_token(char_index, sequence_index)
    def word_to_chars(self, batch_or_word_index: int, word_index: Optional[int] = None, sequence_index: int = 0) -> CharSpan:
        if not self._encodings: raise ValueError("word_to_chars() is not available when using Python based tokenizers")
        if word_index is not None: batch_index = batch_or_word_index
        else:
            batch_index = 0
            word_index = batch_or_word_index
        return CharSpan(*(self._encodings[batch_index].word_to_chars(word_index, sequence_index)))
    def char_to_word(self, batch_or_char_index: int, char_index: Optional[int] = None, sequence_index: int = 0) -> int:
        if not self._encodings: raise ValueError("char_to_word() is not available when using Python based tokenizers")
        if char_index is not None: batch_index = batch_or_char_index
        else:
            batch_index = 0
            char_index = batch_or_char_index
        return self._encodings[batch_index].char_to_word(char_index, sequence_index)
    def convert_to_tensors(self, tensor_type: Optional[Union[str, TensorType]] = None, prepend_batch_axis: bool = False):
        if tensor_type is None: return self
        if not isinstance(tensor_type, TensorType): tensor_type = TensorType(tensor_type)
        if tensor_type == TensorType.TENSORFLOW:
            if not is_tf_available(): raise ImportError("Unable to convert output to TensorFlow tensors format, TensorFlow is not installed.")
            import tensorflow as tf
            as_tensor = tf.constant
            is_tensor = tf.is_tensor
        elif tensor_type == TensorType.PYTORCH:
            if not is_torch_available(): raise ImportError("Unable to convert output to PyTorch tensors format, PyTorch is not installed.")
            import torch
            is_tensor = torch.is_tensor
            def as_tensor(value, dtype=None):
                if isinstance(value, list) and isinstance(value[0], np.ndarray): return torch.from_numpy(np.array(value))
                return torch.tensor(value)
        elif tensor_type == TensorType.JAX:
            if not is_flax_available(): raise ImportError("Unable to convert output to JAX tensors format, JAX is not installed.")
            import jax.numpy as jnp
            as_tensor = jnp.array
            is_tensor = is_jax_tensor
        elif tensor_type == TensorType.MLX:
            if not is_mlx_available(): raise ImportError("Unable to convert output to MLX tensors format, MLX is not installed.")
            import mlx.core as mx
            as_tensor = mx.array
            def is_tensor(obj): return isinstance(obj, mx.array)
        else:
            def as_tensor(value, dtype=None):
                if isinstance(value, (list, tuple)) and isinstance(value[0], (list, tuple, np.ndarray)):
                    value_lens = [len(val) for val in value]
                    if len(set(value_lens)) > 1 and dtype is None: value = as_tensor([np.asarray(val) for val in value], dtype=object)
                return np.asarray(value, dtype=dtype)
            is_tensor = is_numpy_array
        for key, value in self.items():
            try:
                if prepend_batch_axis: value = [value]
                if not is_tensor(value):
                    tensor = as_tensor(value)
                    self[key] = tensor
            except Exception as e:
                if key == "overflowing_tokens": raise ValueError("Unable to create tensor returning overflowing tokens of different lengths. Please see if a fast version of this tokenizer is available to have this feature available.") from e
                raise ValueError(f"Unable to create tensor, you should probably activate truncation and/or padding with 'padding=True' 'truncation=True' to have batched tensors with the same length. Perhaps your features (`{key}` in this case) have excessive nesting (inputs type `list` where type `int` is expected).") from e
        return self
    def to(self, device: Union[str, "torch.device"]) -> "BatchEncoding":
        requires_backends(self, ["torch"])
        if isinstance(device, str) or is_torch_device(device) or isinstance(device, int): self.data = {k: v.to(device=device) for k, v in self.data.items() if v is not None}
        else: logger.warning(f"Attempting to cast a BatchEncoding to type {str(device)}. This is not supported.")
        return self
class SpecialTokensMixin:
    SPECIAL_TOKENS_ATTRIBUTES = ["bos_token", "eos_token", "unk_token", "sep_token", "pad_token", "cls_token", "mask_token", "additional_special_tokens"]
    def __init__(self, verbose=False, **kwargs):
        self._bos_token = None
        self._eos_token = None
        self._unk_token = None
        self._sep_token = None
        self._pad_token = None
        self._cls_token = None
        self._mask_token = None
        self._pad_token_type_id = 0
        self._additional_special_tokens = []
        self.verbose = verbose
        for key, value in kwargs.items():
            if value is None: continue
            if key in self.SPECIAL_TOKENS_ATTRIBUTES:
                if key == "additional_special_tokens":
                    assert isinstance(value, (list, tuple)), f"Value {value} is not a list or tuple"
                    assert all(isinstance(t, (str, AddedToken)) for t in value), "One of the tokens is not a string or an AddedToken"
                    setattr(self, key, value)
                elif isinstance(value, (str, AddedToken)): setattr(self, key, value)
                else: raise TypeError(f"Special token {key} has to be either str or AddedToken but got: {type(value)}")
    def sanitize_special_tokens(self) -> int:
        logger.warning_once("The `sanitize_special_tokens` will be removed in transformers v5.")
        return self.add_tokens(self.all_special_tokens_extended, special_tokens=True)
    def add_special_tokens(self, special_tokens_dict: Dict[str, Union[str, AddedToken]], replace_additional_special_tokens=True) -> int:
        if not special_tokens_dict: return 0
        added_tokens = []
        for key, value in special_tokens_dict.items():
            assert key in self.SPECIAL_TOKENS_ATTRIBUTES, f"Key {key} is not a special token"
            if self.verbose: logger.info(f"Assigning {value} to the {key} key of the tokenizer")
            if key == "additional_special_tokens":
                assert isinstance(value, (list, tuple)) and all(isinstance(t, (str, AddedToken)) for t in value), f"Tokens {value} for key {key} should all be str or AddedToken instances"
                to_add = []
                for token in value:
                    if isinstance(token, str): token = AddedToken(token, rstrip=False, lstrip=False, normalized=False, special=True)
                    if not replace_additional_special_tokens and str(token) in self.additional_special_tokens: continue
                    to_add.append(token)
                if replace_additional_special_tokens and len(to_add) > 0: setattr(self, key, list(to_add))
                else: self._additional_special_tokens.extend(to_add)
                added_tokens += to_add
            else:
                if not isinstance(value, (str, AddedToken)): raise ValueError(f"Token {value} for key {key} should be a str or an AddedToken instance")
                if isinstance(value, (str)): value = AddedToken(value, rstrip=False, lstrip=False, normalized=False, special=True)
                if isinstance(value, AddedToken): setattr(self, key, value)
                if value not in added_tokens: added_tokens.append(value)
        added_tokens = self.add_tokens(added_tokens, special_tokens=True)
        return added_tokens
    def add_tokens(self, new_tokens: Union[str, AddedToken, List[Union[str, AddedToken]]], special_tokens: bool = False) -> int:
        if not new_tokens: return 0
        if not isinstance(new_tokens, (list, tuple)): new_tokens = [new_tokens]
        return self._add_tokens(new_tokens, special_tokens=special_tokens)
    def _add_tokens(self, new_tokens: Union[List[str], List[AddedToken]], special_tokens: bool = False) -> int: raise NotImplementedError
    @property
    def bos_token(self) -> str:
        if self._bos_token is None:
            if self.verbose: logger.error("Using bos_token, but it is not set yet.")
            return None
        return str(self._bos_token)
    @property
    def eos_token(self) -> str:
        if self._eos_token is None:
            if self.verbose: logger.error("Using eos_token, but it is not set yet.")
            return None
        return str(self._eos_token)
    @property
    def unk_token(self) -> str:
        if self._unk_token is None:
            if self.verbose: logger.error("Using unk_token, but it is not set yet.")
            return None
        return str(self._unk_token)
    @property
    def sep_token(self) -> str:
        if self._sep_token is None:
            if self.verbose: logger.error("Using sep_token, but it is not set yet.")
            return None
        return str(self._sep_token)
    @property
    def pad_token(self) -> str:
        if self._pad_token is None:
            if self.verbose: logger.error("Using pad_token, but it is not set yet.")
            return None
        return str(self._pad_token)
    @property
    def cls_token(self) -> str:
        if self._cls_token is None:
            if self.verbose: logger.error("Using cls_token, but it is not set yet.")
            return None
        return str(self._cls_token)
    @property
    def mask_token(self) -> str:
        if self._mask_token is None:
            if self.verbose: logger.error("Using mask_token, but it is not set yet.")
            return None
        return str(self._mask_token)
    @property
    def additional_special_tokens(self) -> List[str]:
        if self._additional_special_tokens is None:
            if self.verbose: logger.error("Using additional_special_tokens, but it is not set yet.")
            return None
        return [str(tok) for tok in self._additional_special_tokens]
    @bos_token.setter
    def bos_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the BOS token")
        self._bos_token = value
    @eos_token.setter
    def eos_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the EOS token")
        self._eos_token = value
    @unk_token.setter
    def unk_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the UNK token")
        self._unk_token = value
    @sep_token.setter
    def sep_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the SEP token")
        self._sep_token = value
    @pad_token.setter
    def pad_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the PAD token")
        self._pad_token = value
    @cls_token.setter
    def cls_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the CLS token")
        self._cls_token = value
    @mask_token.setter
    def mask_token(self, value):
        if not isinstance(value, (str, AddedToken)) and value is not None: raise ValueError("Cannot set a non-string value as the MASK token")
        self._mask_token = value
    @additional_special_tokens.setter
    def additional_special_tokens(self, value): self._additional_special_tokens = value if value is not None else None
    @property
    def bos_token_id(self) -> Optional[int]:
        if self._bos_token is None: return None
        return self.convert_tokens_to_ids(self.bos_token)
    @property
    def eos_token_id(self) -> Optional[int]:
        if self._eos_token is None: return None
        return self.convert_tokens_to_ids(self.eos_token)
    @property
    def unk_token_id(self) -> Optional[int]:
        if self._unk_token is None: return None
        return self.convert_tokens_to_ids(self.unk_token)
    @property
    def sep_token_id(self) -> Optional[int]:
        if self._sep_token is None: return None
        return self.convert_tokens_to_ids(self.sep_token)
    @property
    def pad_token_id(self) -> Optional[int]:
        if self._pad_token is None: return None
        return self.convert_tokens_to_ids(self.pad_token)
    @property
    def pad_token_type_id(self) -> int: return self._pad_token_type_id
    @property
    def cls_token_id(self) -> Optional[int]:
        if self._cls_token is None: return None
        return self.convert_tokens_to_ids(self.cls_token)
    @property
    def mask_token_id(self) -> Optional[int]:
        if self._mask_token is None: return None
        return self.convert_tokens_to_ids(self.mask_token)
    @property
    def additional_special_tokens_ids(self) -> List[int]: return self.convert_tokens_to_ids(self.additional_special_tokens)
    @bos_token_id.setter
    def bos_token_id(self, value): self._bos_token = self.convert_ids_to_tokens(value) if value is not None else None
    @eos_token_id.setter
    def eos_token_id(self, value): self._eos_token = self.convert_ids_to_tokens(value) if value is not None else None
    @unk_token_id.setter
    def unk_token_id(self, value): self._unk_token = self.convert_ids_to_tokens(value) if value is not None else None
    @sep_token_id.setter
    def sep_token_id(self, value): self._sep_token = self.convert_ids_to_tokens(value) if value is not None else None
    @pad_token_id.setter
    def pad_token_id(self, value): self._pad_token = self.convert_ids_to_tokens(value) if value is not None else None
    @cls_token_id.setter
    def cls_token_id(self, value): self._cls_token = self.convert_ids_to_tokens(value) if value is not None else None
    @mask_token_id.setter
    def mask_token_id(self, value): self._mask_token = self.convert_ids_to_tokens(value) if value is not None else None
    @additional_special_tokens_ids.setter
    def additional_special_tokens_ids(self, values): self._additional_special_tokens = [self.convert_ids_to_tokens(value) for value in values]
    @property
    def special_tokens_map(self) -> Dict[str, Union[str, List[str]]]:
        set_attr = {}
        for attr in self.SPECIAL_TOKENS_ATTRIBUTES:
            attr_value = getattr(self, attr)
            if attr_value: set_attr[attr] = attr_value
        return set_attr
    @property
    def special_tokens_map_extended(self) -> Dict[str, Union[str, AddedToken, List[Union[str, AddedToken]]]]:
        set_attr = {}
        for attr in self.SPECIAL_TOKENS_ATTRIBUTES:
            attr_value = getattr(self, "_" + attr)
            if attr_value: set_attr[attr] = attr_value
        return set_attr
    @property
    def all_special_tokens_extended(self) -> List[Union[str, AddedToken]]:
        all_tokens = []
        seen = set()
        for value in self.special_tokens_map_extended.values():
            if isinstance(value, (list, tuple)): tokens_to_add = [token for token in value if str(token) not in seen]
            else: tokens_to_add = [value] if str(value) not in seen else []
            seen.update(map(str, tokens_to_add))
            all_tokens.extend(tokens_to_add)
        return all_tokens
    @property
    def all_special_tokens(self) -> List[str]:
        all_toks = [str(s) for s in self.all_special_tokens_extended]
        return all_toks
    @property
    def all_special_ids(self) -> List[int]:
        all_toks = self.all_special_tokens
        all_ids = self.convert_tokens_to_ids(all_toks)
        return all_ids
ENCODE_KWARGS_DOCSTRING = r"""
            add_special_tokens (`bool`, *optional*, defaults to `True`):
                Whether or not to add special tokens when encoding the sequences. This will use the underlying
                `PretrainedTokenizerBase.build_inputs_with_special_tokens` function, which defines which tokens are
                automatically added to the input ids. This is usefull if you want to add `bos` or `eos` tokens
                automatically.
            padding (`bool`, `str` or [`~utils.PaddingStrategy`], *optional*, defaults to `False`):
                Activates and controls padding. Accepts the following values:
                - `True` or `'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
                  sequence if provided).
                - `'max_length'`: Pad to a maximum length specified with the argument `max_length` or to the maximum
                  acceptable input length for the model if that argument is not provided.
                - `False` or `'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of different
                  lengths).
            truncation (`bool`, `str` or [`~tokenization_utils_base.TruncationStrategy`], *optional*, defaults to `False`):
                Activates and controls truncation. Accepts the following values:
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
                Controls the maximum length to use by one of the truncation/padding parameters.
                If left unset or set to `None`, this will use the predefined model maximum length if a maximum length
                is required by one of the truncation/padding parameters. If the model has no specific maximum input
                length (like XLNet) truncation/padding to a maximum length will be deactivated.
            stride (`int`, *optional*, defaults to 0):
                If set to a number along with `max_length`, the overflowing tokens returned when
                `return_overflowing_tokens=True` will contain some tokens from the end of the truncated sequence
                returned to provide some overlap between truncated and overflowing sequences. The value of this
                argument defines the number of overlapping tokens.
            is_split_into_words (`bool`, *optional*, defaults to `False`):
                Whether or not the input is already pre-tokenized (e.g., split into words). If set to `True`, the
                tokenizer assumes the input is already split into words (for instance, by splitting it on whitespace)
                which it will tokenize. This is useful for NER or token classification.
            pad_to_multiple_of (`int`, *optional*):
                If set will pad the sequence to a multiple of the provided value. Requires `padding` to be activated.
                This is especially useful to enable the use of Tensor Cores on NVIDIA hardware with compute capability
                `>= 7.5` (Volta).
            padding_side (`str`, *optional*):
                The side on which the model should have padding applied. Should be selected between ['right', 'left'].
                Default value is picked from the class attribute of the same name.
            return_tensors (`str` or [`~utils.TensorType`], *optional*):
                If set, will return tensors instead of list of python integers. Acceptable values are:
                - `'tf'`: Return TensorFlow `tf.constant` objects.
                - `'pt'`: Return PyTorch `torch.Tensor` objects.
                - `'np'`: Return Numpy `np.ndarray` objects.
"""
ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING = r"""
            return_token_type_ids (`bool`, *optional*):
                Whether to return token type IDs. If left to the default, will return the token type IDs according to
                the specific tokenizer's default, defined by the `return_outputs` attribute.
                [What are token type IDs?](../glossary#token-type-ids)
            return_attention_mask (`bool`, *optional*):
                Whether to return the attention mask. If left to the default, will return the attention mask according
                to the specific tokenizer's default, defined by the `return_outputs` attribute.
                [What are attention masks?](../glossary#attention-mask)
            return_overflowing_tokens (`bool`, *optional*, defaults to `False`):
                Whether or not to return overflowing token sequences. If a pair of sequences of input ids (or a batch
                of pairs) is provided with `truncation_strategy = longest_first` or `True`, an error is raised instead
                of returning overflowing tokens.
            return_special_tokens_mask (`bool`, *optional*, defaults to `False`):
                Whether or not to return special tokens mask information.
            return_offsets_mapping (`bool`, *optional*, defaults to `False`):
                Whether or not to return `(char_start, char_end)` for each token.
                This is only available on fast tokenizers inheriting from [`PreTrainedTokenizerFast`], if using
                Python's tokenizer, this method will raise `NotImplementedError`.
            return_length  (`bool`, *optional*, defaults to `False`):
                Whether or not to return the lengths of the encoded inputs.
            verbose (`bool`, *optional*, defaults to `True`):
                Whether or not to print more information and warnings.
            *kwargs: passed to the `self.tokenize()` method
        Return:
            [`BatchEncoding`]: A [`BatchEncoding`] with the following fields:
            - *input_ids* -- List of token ids to be fed to a model.
              [What are input IDs?](../glossary#input-ids)
            - *token_type_ids* -- List of token type ids to be fed to a model (when `return_token_type_ids=True` or
              if *"token_type_ids"* is in `self.model_input_names`).
              [What are token type IDs?](../glossary#token-type-ids)
            - *attention_mask* -- List of indices specifying which tokens should be attended to by the model (when
              `return_attention_mask=True` or if *"attention_mask"* is in `self.model_input_names`).
              [What are attention masks?](../glossary#attention-mask)
            - *overflowing_tokens* -- List of overflowing tokens sequences (when a `max_length` is specified and
              `return_overflowing_tokens=True`).
            - *num_truncated_tokens* -- Number of tokens truncated (when a `max_length` is specified and
              `return_overflowing_tokens=True`).
            - *special_tokens_mask* -- List of 0s and 1s, with 1 specifying added special tokens and 0 specifying
              regular sequence tokens (when `add_special_tokens=True` and `return_special_tokens_mask=True`).
            - *length* -- The length of the inputs (when `return_length=True`)
"""
INIT_TOKENIZER_DOCSTRING = r"""
    Class attributes (overridden by derived classes)
        - *vocab_files_names* (`Dict[str, str]`) -- A dictionary with, as keys, the `__init__` keyword name of each
          vocabulary file required by the model, and as associated values, the filename for saving the associated file
          (string).
        - *pretrained_vocab_files_map* (`Dict[str, Dict[str, str]]`) -- A dictionary of dictionaries, with the
          high-level keys being the `__init__` keyword name of each vocabulary file required by the model, the
          low-level being the `short-cut-names` of the pretrained models with, as associated values, the `url` to the
          associated pretrained vocabulary file.
        - *model_input_names* (`List[str]`) -- A list of inputs expected in the forward pass of the model.
        - *padding_side* (`str`) -- The default value for the side on which the model should have padding applied.
          Should be `'right'` or `'left'`.
        - *truncation_side* (`str`) -- The default value for the side on which the model should have truncation
          applied. Should be `'right'` or `'left'`.
    Args:
        model_max_length (`int`, *optional*):
            The maximum length (in number of tokens) for the inputs to the transformer model. When the tokenizer is
            loaded with [`~tokenization_utils_base.PreTrainedTokenizerBase.from_pretrained`], this will be set to the
            value stored for the associated model in `max_model_input_sizes` (see above). If no value is provided, will
            default to VERY_LARGE_INTEGER (`int(1e30)`).
        padding_side (`str`, *optional*):
            The side on which the model should have padding applied. Should be selected between ['right', 'left'].
            Default value is picked from the class attribute of the same name.
        truncation_side (`str`, *optional*):
            The side on which the model should have truncation applied. Should be selected between ['right', 'left'].
            Default value is picked from the class attribute of the same name.
        chat_template (`str`, *optional*):
            A Jinja template string that will be used to format lists of chat messages.
        model_input_names (`List[string]`, *optional*):
            The list of inputs accepted by the forward pass of the model (like `"token_type_ids"` or
            `"attention_mask"`). Default value is picked from the class attribute of the same name.
        bos_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token representing the beginning of a sentence. Will be associated to `self.bos_token` and
            `self.bos_token_id`.
        eos_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token representing the end of a sentence. Will be associated to `self.eos_token` and
            `self.eos_token_id`.
        unk_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token representing an out-of-vocabulary token. Will be associated to `self.unk_token` and
            `self.unk_token_id`.
        sep_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token separating two different sentences in the same input (used by BERT for instance). Will be
            associated to `self.sep_token` and `self.sep_token_id`.
        pad_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token used to make arrays of tokens the same size for batching purpose. Will then be ignored by
            attention mechanisms or loss computation. Will be associated to `self.pad_token` and `self.pad_token_id`.
        cls_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token representing the class of the input (used by BERT for instance). Will be associated to
            `self.cls_token` and `self.cls_token_id`.
        mask_token (`str` or `tokenizers.AddedToken`, *optional*):
            A special token representing a masked token (used by masked-language modeling pretraining objectives, like
            BERT). Will be associated to `self.mask_token` and `self.mask_token_id`.
        additional_special_tokens (tuple or list of `str` or `tokenizers.AddedToken`, *optional*):
            A tuple or a list of additional special tokens. Add them here to ensure they are skipped when decoding with
            `skip_special_tokens` is set to True. If they are not part of the vocabulary, they will be added at the end
            of the vocabulary.
        clean_up_tokenization_spaces (`bool`, *optional*, defaults to `True`):
            Whether or not the model should cleanup the spaces that were added when splitting the input text during the
            tokenization process.
        split_special_tokens (`bool`, *optional*, defaults to `False`):
            Whether or not the special tokens should be split during the tokenization process. Passing will affect the
            internal state of the tokenizer. The default behavior is to not split special tokens. This means that if
            `<s>` is the `bos_token`, then `tokenizer.tokenize("<s>") = ['<s>`]. Otherwise, if
            `split_special_tokens=True`, then `tokenizer.tokenize("<s>")` will be give `['<','s', '>']`.
"""
@add_end_docstrings(INIT_TOKENIZER_DOCSTRING)
class PreTrainedTokenizerBase(SpecialTokensMixin, PushToHubMixin):
    vocab_files_names: Dict[str, str] = {}
    pretrained_vocab_files_map: Dict[str, Dict[str, str]] = {}
    _auto_class: Optional[str] = None
    model_input_names: List[str] = ["input_ids", "token_type_ids", "attention_mask"]
    padding_side: str = "right"
    truncation_side: str = "right"
    slow_tokenizer_class = None
    def __init__(self, **kwargs):
        self.init_inputs = ()
        for key in kwargs:
            if hasattr(self, key) and callable(getattr(self, key)): raise AttributeError(f"{key} conflicts with the method {key} in {self.__class__.__name__}")
        self.init_kwargs = copy.deepcopy(kwargs)
        self.name_or_path = kwargs.pop("name_or_path", "")
        self._processor_class = kwargs.pop("processor_class", None)
        model_max_length = kwargs.pop("model_max_length", kwargs.pop("max_len", None))
        self.model_max_length = model_max_length if model_max_length is not None else VERY_LARGE_INTEGER
        self.padding_side = kwargs.pop("padding_side", self.padding_side)
        if self.padding_side not in ["right", "left"]: raise ValueError(f"Padding side should be selected between 'right' and 'left', current value: {self.padding_side}")
        self.truncation_side = kwargs.pop("truncation_side", self.truncation_side)
        if self.truncation_side not in ["right", "left"]: raise ValueError(f"Truncation side should be selected between 'right' and 'left', current value: {self.truncation_side}")
        self.model_input_names = kwargs.pop("model_input_names", self.model_input_names)
        self.clean_up_tokenization_spaces = kwargs.pop("clean_up_tokenization_spaces", False)
        self.split_special_tokens = kwargs.pop("split_special_tokens", False)
        self.deprecation_warnings = {}
        self._in_target_context_manager = False
        self.chat_template = kwargs.pop("chat_template", None)
        if isinstance(self.chat_template, (list, tuple)): self.chat_template = {template["name"]: template["template"] for template in self.chat_template}
        super().__init__(**kwargs)
    @property
    def max_len_single_sentence(self) -> int: return self.model_max_length - self.num_special_tokens_to_add(pair=False)
    @property
    def max_len_sentences_pair(self) -> int: return self.model_max_length - self.num_special_tokens_to_add(pair=True)
    @max_len_single_sentence.setter
    def max_len_single_sentence(self, value) -> int:
        if value == self.model_max_length - self.num_special_tokens_to_add(pair=False) and self.verbose:
            if not self.deprecation_warnings.get("max_len_single_sentence", False): logger.warning("Setting 'max_len_single_sentence' is now deprecated. This value is automatically set up.")
            self.deprecation_warnings["max_len_single_sentence"] = True
        else: raise ValueError("Setting 'max_len_single_sentence' is now deprecated. This value is automatically set up.")
    @max_len_sentences_pair.setter
    def max_len_sentences_pair(self, value) -> int:
        if value == self.model_max_length - self.num_special_tokens_to_add(pair=True) and self.verbose:
            if not self.deprecation_warnings.get("max_len_sentences_pair", False): logger.warning("Setting 'max_len_sentences_pair' is now deprecated. This value is automatically set up.")
            self.deprecation_warnings["max_len_sentences_pair"] = True
        else: raise ValueError("Setting 'max_len_sentences_pair' is now deprecated. This value is automatically set up.")
    def _set_processor_class(self, processor_class: str): self._processor_class = processor_class
    @property
    def added_tokens_decoder(self) -> Dict[int, AddedToken]: raise NotImplementedError()
    def __repr__(self) -> str:
        added_tokens_decoder_rep = "\n\t".join([f"{k}: {v.__repr__()}," for k, v in self.added_tokens_decoder.items()])
        return (f"{self.__class__.__name__}(name_or_path='{self.name_or_path}', vocab_size={self.vocab_size}, model_max_length={self.model_max_length}, is_fast={self.is_fast}, padding_side='{self.padding_side}', truncation_side='{self.truncation_side}', special_tokens={self.special_tokens_map}, clean_up_tokenization_spaces={self.clean_up_tokenization_spaces}), " + "added_tokens_decoder={\n\t" + added_tokens_decoder_rep + "\n}")
    def __len__(self) -> int: raise NotImplementedError()
    def get_vocab(self) -> Dict[str, int]: raise NotImplementedError()
    def apply_chat_template(self, conversation: Union[List[Dict[str, str]], List[List[Dict[str, str]]]], tools: Optional[List[Dict]] = None, documents: Optional[List[Dict[str, str]]] = None, chat_template: Optional[str] = None,
    add_generation_prompt: bool = False, continue_final_message: bool = False, tokenize: bool = True, padding: bool = False, truncation: bool = False, max_length: Optional[int] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_dict: bool = False, return_assistant_tokens_mask: bool = False, tokenizer_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> Union[str, List[int], List[str], List[List[int]], BatchEncoding]:
        if return_dict and not tokenize: raise ValueError("`return_dict=True` is incompatible with `tokenize=False`, because there is no dict of tokenizer outputs to return.")
        if return_assistant_tokens_mask and not return_dict: raise ValueError("`return_assistant_tokens_mask=True` is incompatible with `return_dict=False`")
        if tokenizer_kwargs is None: tokenizer_kwargs = {}
        chat_template = self.get_chat_template(chat_template, tools)
        if return_assistant_tokens_mask and not re.search(r"\{\%-?\s*generation\s*-?\%\}", chat_template): logger.warning_once("return_assistant_tokens_mask==True but chat template does not contain `{% generation %}` keyword.")
        compiled_template = _compile_jinja_template(chat_template)
        if isinstance(conversation, (list, tuple)) and (isinstance(conversation[0], (list, tuple)) or hasattr(conversation[0], "messages")):
            conversations = conversation
            is_batched = True
        else:
            conversations = [conversation]
            is_batched = False
        if continue_final_message:
            if add_generation_prompt: raise ValueError("continue_final_message and add_generation_prompt are not compatible. Use continue_final_message when you want the model to continue the final message, and add_generation_prompt when you want to add a header that will prompt it to start a new assistant message instead.")
            if return_assistant_tokens_mask: raise ValueError("continue_final_message is not compatible with return_assistant_tokens_mask.")
        if tools is not None:
            tool_schemas = []
            for tool in tools:
                if isinstance(tool, dict): tool_schemas.append(tool)
                elif isfunction(tool): tool_schemas.append(get_json_schema(tool))
                else: raise ValueError("Tools should either be a JSON schema, or a callable function with type hints and a docstring suitable for auto-conversion to a schema.")
        else: tool_schemas = None
        if documents is not None:
            for document in documents:
                if not isinstance(document, dict): raise TypeError("Documents should be a list of dicts with 'title' and 'text' keys!")
        rendered = []
        all_generation_indices = []
        template_kwargs = {**self.special_tokens_map, **kwargs}
        for chat in conversations:
            if hasattr(chat, "messages"): chat = chat.messages
            if return_assistant_tokens_mask:
                rendered_chat, generation_indices = _render_with_assistant_indices(compiled_template=compiled_template, messages=chat, tools=tool_schemas, documents=documents, add_generation_prompt=add_generation_prompt, **template_kwargs)
                all_generation_indices.append(generation_indices)
            else: rendered_chat = compiled_template.render(messages=chat, tools=tool_schemas, documents=documents, add_generation_prompt=add_generation_prompt, **template_kwargs)
            if continue_final_message:
                final_message = chat[-1]["content"]
                rendered_chat = rendered_chat[: rendered_chat.rindex(final_message) + len(final_message)].rstrip()
            rendered.append(rendered_chat)
        if not is_batched: rendered = rendered[0]
        if tokenize:
            out = self(rendered, padding=padding, truncation=truncation, max_length=max_length, add_special_tokens=False, return_tensors=return_tensors, **tokenizer_kwargs)
            if return_dict:
                if return_assistant_tokens_mask:
                    assistant_masks = []
                    if is_batched or return_tensors: input_ids = out["input_ids"]
                    else: input_ids = [out["input_ids"]]
                    for i in range(len(input_ids)):
                        current_mask = [0] * len(input_ids[i])
                        for assistant_start_char, assistant_end_char in all_generation_indices[i]:
                            start_token = out.char_to_token(i, assistant_start_char)
                            end_token = out.char_to_token(i, assistant_end_char - 1)
                            if start_token is None: break
                            for token_id in range(start_token, end_token + 1 if end_token else len(input_ids)): current_mask[token_id] = 1
                        assistant_masks.append(current_mask)
                    out["assistant_masks"] = assistant_masks if is_batched else assistant_masks[0]
                return out
            else: return out["input_ids"]
        else: return rendered
    def get_chat_template(self, chat_template: Optional[str] = None, tools: Optional[List[Dict]] = None) -> str:
        if isinstance(self.chat_template, dict):
            template_dict = self.chat_template
            if chat_template is not None and chat_template in template_dict: chat_template = template_dict[chat_template]
            elif chat_template is None:
                if tools is not None and "tool_use" in template_dict: chat_template = template_dict["tool_use"]
                elif "default" in template_dict: chat_template = template_dict["default"]
                else: raise ValueError(f"This model has multiple chat templates with no default specified! Please either pass a chat template or the name of the template you wish to use to the `chat_template` argument. Available template names are {sorted(template_dict.keys())}.")
        elif chat_template is None:
            if self.chat_template is not None: chat_template = self.chat_template
            else: raise ValueError("Cannot use chat template functions because tokenizer.chat_template is not set and no template argument was passed! For information about writing templates and setting the tokenizer.chat_template attribute.")
        return chat_template
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], *init_inputs, cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False, local_files_only: bool = False, token: Optional[Union[str, bool]] = None, revision: str = "main", trust_remote_code=False, **kwargs):
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        subfolder = kwargs.pop("subfolder", None)
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        commit_hash = kwargs.pop("_commit_hash", None)
        gguf_file = kwargs.get("gguf_file", None)
        if use_auth_token is not None:
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        user_agent = {"file_type": "tokenizer", "from_auto_class": from_auto_class, "is_fast": "Fast" in cls.__name__}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        vocab_files = {}
        init_configuration = {}
        is_local = os.path.isdir(pretrained_model_name_or_path)
        single_file_id = None
        if os.path.isfile(pretrained_model_name_or_path) or is_remote_url(pretrained_model_name_or_path):
            if len(cls.vocab_files_names) > 1 and not gguf_file: raise ValueError(f"Calling {cls.__name__}.from_pretrained() with the path to a single file or url is not supported for this tokenizer. Use a model identifier or the path to a directory instead.")
            warnings.warn(f"Calling {cls.__name__}.from_pretrained() with the path to a single file or url is deprecated and won't be possible anymore in v5. Use a model identifier or the path to a directory instead.", FutureWarning)
            file_id = list(cls.vocab_files_names.keys())[0]
            vocab_files[file_id] = pretrained_model_name_or_path
            single_file_id = file_id
        else:
            if gguf_file: vocab_files["vocab_file"] = gguf_file
            else:
                additional_files_names = {"added_tokens_file": ADDED_TOKENS_FILE, "special_tokens_map_file": SPECIAL_TOKENS_MAP_FILE, "tokenizer_config_file": TOKENIZER_CONFIG_FILE, "tokenizer_file": FULL_TOKENIZER_FILE}
                vocab_files = {**cls.vocab_files_names, **additional_files_names}
                if "tokenizer_file" in vocab_files:
                    fast_tokenizer_file = FULL_TOKENIZER_FILE
                    resolved_config_file = cached_file(pretrained_model_name_or_path, TOKENIZER_CONFIG_FILE, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download, proxies=proxies,
                    token=token, revision=revision, local_files_only=local_files_only, subfolder=subfolder, user_agent=user_agent, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False, _raise_exceptions_for_connection_errors=False, _commit_hash=commit_hash)
                    commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
                    if resolved_config_file is not None:
                        with open(resolved_config_file, encoding="utf-8") as reader:
                            tokenizer_config = json.load(reader)
                            if "fast_tokenizer_files" in tokenizer_config: fast_tokenizer_file = get_fast_tokenizer_file(tokenizer_config["fast_tokenizer_files"])
                    vocab_files["tokenizer_file"] = fast_tokenizer_file
        resolved_vocab_files = {}
        unresolved_files = []
        for file_id, file_path in vocab_files.items():
            if file_path is None: resolved_vocab_files[file_id] = None
            elif single_file_id == file_id:
                if os.path.isfile(file_path): resolved_vocab_files[file_id] = file_path
                elif is_remote_url(file_path): resolved_vocab_files[file_id] = download_url(file_path, proxies=proxies)
            else:
                resolved_vocab_files[file_id] = cached_file(pretrained_model_name_or_path, file_path, cache_dir=cache_dir, force_download=force_download, proxies=proxies, resume_download=resume_download,
                local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False,
                _raise_exceptions_for_connection_errors=False, _commit_hash=commit_hash)
                commit_hash = extract_commit_hash(resolved_vocab_files[file_id], commit_hash)
        if len(unresolved_files) > 0: logger.info(f"Can't load following files from cache: {unresolved_files} and cannot check if these files are necessary for the tokenizer to operate.")
        if all(full_file_name is None for full_file_name in resolved_vocab_files.values()) and not gguf_file: raise EnvironmentError(f"Can't load tokenizer for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing all relevant files for a {cls.__name__} tokenizer.")
        for file_id, file_path in vocab_files.items():
            if file_id not in resolved_vocab_files: continue
            if is_local: logger.info(f"loading file {file_path}")
            else: logger.info(f"loading file {file_path} from cache at {resolved_vocab_files[file_id]}")
        return cls._from_pretrained(resolved_vocab_files, pretrained_model_name_or_path, init_configuration, *init_inputs, token=token, cache_dir=cache_dir, local_files_only=local_files_only, _commit_hash=commit_hash, _is_local=is_local, trust_remote_code=trust_remote_code, **kwargs)
    @classmethod
    def _from_pretrained(cls, resolved_vocab_files, pretrained_model_name_or_path, init_configuration, *init_inputs, token=None, cache_dir=None, local_files_only=False, _commit_hash=None, _is_local=False, trust_remote_code=False, **kwargs):
        from_slow = kwargs.get("from_slow", False)
        gguf_file = kwargs.get("gguf_file", None)
        has_tokenizer_file = resolved_vocab_files.get("tokenizer_file", None) is not None
        if (from_slow or not has_tokenizer_file) and cls.slow_tokenizer_class is not None and not gguf_file: slow_tokenizer = (cls.slow_tokenizer_class)._from_pretrained(copy.deepcopy(resolved_vocab_files), pretrained_model_name_or_path,
        copy.deepcopy(init_configuration), *init_inputs, token=token, cache_dir=cache_dir, local_files_only=local_files_only, _commit_hash=_commit_hash, **(copy.deepcopy(kwargs)))
        else: slow_tokenizer = None
        tokenizer_config_file = resolved_vocab_files.pop("tokenizer_config_file", None)
        if tokenizer_config_file is not None:
            with open(tokenizer_config_file, encoding="utf-8") as tokenizer_config_handle: init_kwargs = json.load(tokenizer_config_handle)
            config_tokenizer_class = init_kwargs.get("tokenizer_class")
            init_kwargs.pop("tokenizer_class", None)
            if not has_tokenizer_file: init_kwargs.pop("tokenizer_file", None)
            saved_init_inputs = init_kwargs.pop("init_inputs", ())
            if not init_inputs: init_inputs = saved_init_inputs
        else:
            config_tokenizer_class = None
            init_kwargs = init_configuration
        if not _is_local:
            if "auto_map" in init_kwargs:
                if isinstance(init_kwargs["auto_map"], (tuple, list)): init_kwargs["auto_map"] = {"AutoTokenizer": init_kwargs["auto_map"]}
                init_kwargs["auto_map"] = add_model_info_to_auto_map(init_kwargs["auto_map"], pretrained_model_name_or_path)
            if "custom_pipelines" in init_kwargs: init_kwargs["custom_pipelines"] = add_model_info_to_custom_pipelines(init_kwargs["custom_pipelines"], pretrained_model_name_or_path)
        if config_tokenizer_class is None:
            from .models.auto.configuration_auto import AutoConfig
            try:
                config = AutoConfig.from_pretrained(pretrained_model_name_or_path, token=token, cache_dir=cache_dir, local_files_only=local_files_only, trust_remote_code=trust_remote_code, _commit_hash=_commit_hash)
                config_tokenizer_class = config.tokenizer_class
            except (OSError, ValueError, KeyError): config = None
            if config_tokenizer_class is None:
                from .models.auto.tokenization_auto import TOKENIZER_MAPPING_NAMES
                if hasattr(config, "model_type"): model_type = config.model_type
                else:
                    model_type = None
                    for pattern in TOKENIZER_MAPPING_NAMES.keys():
                        if pattern in str(pretrained_model_name_or_path):
                            model_type = pattern
                            break
                if model_type is not None:
                    config_tokenizer_class, config_tokenizer_class_fast = TOKENIZER_MAPPING_NAMES.get(model_type, (None, None))
                    if config_tokenizer_class is None: config_tokenizer_class = config_tokenizer_class_fast
        if config_tokenizer_class is not None:
            tokenizer1, tokenizer2 = cls.__name__.replace("Fast", ""), config_tokenizer_class.replace("Fast", "")
            if tokenizer1 != "SAPIAudioTokenizer" and tokenizer2 != "WhisperTokenizer":
                if cls.__name__.replace("Fast", "") != config_tokenizer_class.replace("Fast", ""): logger.warning(f"The tokenizer class you load from this checkpoint is not the same type as the class this function is called from. It may result in unexpected tokenization. \nThe tokenizer class you load from this checkpoint is '{config_tokenizer_class}'. \nThe class this function is called from is '{cls.__name__}'.")
        init_kwargs.update(kwargs)
        added_tokens_file = resolved_vocab_files.pop("added_tokens_file", None)
        special_tokens_map_file = resolved_vocab_files.pop("special_tokens_map_file", None)
        for args_name, file_path in resolved_vocab_files.items():
            if args_name not in init_kwargs: init_kwargs[args_name] = file_path
        tokenizer_file = resolved_vocab_files.pop("tokenizer_file", None)
        if slow_tokenizer is not None: init_kwargs["__slow_tokenizer"] = slow_tokenizer
        init_kwargs["name_or_path"] = pretrained_model_name_or_path
        added_tokens_decoder: Dict[int, AddedToken] = {}
        added_tokens_map: Dict[str, AddedToken] = {}
        if "added_tokens_decoder" in init_kwargs:
            for idx, token in init_kwargs["added_tokens_decoder"].items():
                if isinstance(token, dict): token = AddedToken(**token)
                if isinstance(token, AddedToken):
                    added_tokens_decoder[int(idx)] = token
                    added_tokens_map[str(token)] = token
                else: raise ValueError(f"Found a {token.__class__} in the saved `added_tokens_decoder`, should be a dictionary or an AddedToken instance")
        else:
            if special_tokens_map_file is not None:
                with open(special_tokens_map_file, encoding="utf-8") as special_tokens_map_handle:
                    special_tokens_map = json.load(special_tokens_map_handle)
                    for key, value in special_tokens_map.items():
                        if key in kwargs and kwargs[key]: continue
                        if isinstance(value, dict):
                            value["special"] = True
                            value = AddedToken(**value)
                        elif key == "additional_special_tokens" and isinstance(value, list):
                            additional_special_tokens = init_kwargs.pop("additional_special_tokens", []) or []
                            for token in value:
                                if isinstance(token, dict):
                                    token["special"] = True
                                    token = AddedToken(**token)
                                if token not in additional_special_tokens: additional_special_tokens.append(token)
                            value = additional_special_tokens
                        init_kwargs[key] = value
            if added_tokens_file is not None:
                special_tokens = []
                for key in cls.SPECIAL_TOKENS_ATTRIBUTES & init_kwargs.keys():
                    if init_kwargs[key] is not None:
                        if key == "additional_special_tokens": special_tokens += [str(token) for token in init_kwargs[key]]
                        else: special_tokens.append(str(init_kwargs[key]))
                with open(added_tokens_file, encoding="utf-8") as added_tokens_handle: added_tok_encoder = json.load(added_tokens_handle)
                for str_token, index in added_tok_encoder.items():
                    special = str_token in special_tokens
                    added_tokens_decoder[index] = AddedToken(str_token, rstrip=False, lstrip=False, normalized=not special, special=special)
                    added_tokens_map[str(token)] = added_tokens_decoder[index]
            if tokenizer_file is not None:
                with open(tokenizer_file, encoding="utf-8") as tokenizer_file_handle:
                    tokenizer_file_handle = json.load(tokenizer_file_handle)
                    added_tokens = tokenizer_file_handle.pop("added_tokens")
                for serialized_tokens in added_tokens:
                    idx = serialized_tokens.pop("id")
                    added_tokens_decoder[idx] = AddedToken(**serialized_tokens)
                    added_tokens_map[str(added_tokens_decoder[idx])] = added_tokens_decoder[idx]
        init_kwargs["added_tokens_decoder"] = added_tokens_decoder
        init_kwargs = cls.convert_added_tokens(init_kwargs, save=False)
        for key in cls.SPECIAL_TOKENS_ATTRIBUTES & init_kwargs.keys():
            if added_tokens_map != {} and init_kwargs[key] is not None:
                if key != "additional_special_tokens": init_kwargs[key] = added_tokens_map.get(str(init_kwargs[key]), init_kwargs[key])
        try: tokenizer = cls(*init_inputs, **init_kwargs)
        except import_protobuf_decode_error():
            logger.info("Unable to load tokenizer model from SPM, loading from TikToken will be attempted instead. (Google protobuf error: Tried to load SPM model with non-SPM vocab file).")
            return False
        except RuntimeError as e:
            if "sentencepiece_processor.cc" in str(e): logger.info("Unable to load tokenizer model from SPM, loading from TikToken will be attempted instead. (SentencePiece RuntimeError: Tried to load SPM model with non-SPM vocab file).")
            return False
        except OSError: raise OSError("Unable to load vocabulary from file. Please check that the provided vocabulary is accessible and not corrupted.")
        except RuntimeError as e:
            if "sentencepiece_processor.cc" in str(e):
                logger.info("Unable to load tokenizer model from SPM, loading from TikToken will be attempted instead. (SentencePiece RuntimeError: Tried to load SPM model with non-SPM vocab file).")
                return False
        if added_tokens_decoder != {} and max(list(added_tokens_decoder.keys())[-1], 0) > tokenizer.vocab_size: logger.info("Special tokens have been added in the vocabulary, make sure the associated word embeddings are fine-tuned or trained.")
        return tokenizer
    @staticmethod
    def _eventually_correct_t5_max_length(pretrained_model_name_or_path, max_model_length, init_max_model_length): return max_model_length
    @classmethod
    def convert_added_tokens(cls, obj: Union[AddedToken, Any], save=False, add_type_field=True):
        if isinstance(obj, dict) and "__type" in obj and obj["__type"] == "AddedToken":
            obj.pop("__type")
            return AddedToken(**obj)
        if isinstance(obj, AddedToken) and save:
            obj = obj.__getstate__()
            if add_type_field: obj["__type"] = "AddedToken"
            else: obj.pop("special")
            return obj
        elif isinstance(obj, (list, tuple)): return [cls.convert_added_tokens(o, save=save, add_type_field=add_type_field) for o in obj]
        elif isinstance(obj, dict): return {k: cls.convert_added_tokens(v, save=save, add_type_field=add_type_field) for k, v in obj.items()}
        return obj
    def save_pretrained(self, save_directory: Union[str, os.PathLike], legacy_format: Optional[bool] = None, filename_prefix: Optional[str] = None, push_to_hub: bool = False, **kwargs) -> Tuple[str]:
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        if os.path.isfile(save_directory):
            logger.error(f"Provided path ({save_directory}) should be a directory, not a file")
            return
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        special_tokens_map_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + SPECIAL_TOKENS_MAP_FILE)
        tokenizer_config_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + TOKENIZER_CONFIG_FILE)
        tokenizer_config = copy.deepcopy(self.init_kwargs)
        target_keys = set(self.init_kwargs.keys())
        target_keys.update(["model_max_length", "clean_up_tokenization_spaces"])
        for k in target_keys:
            if hasattr(self, k): tokenizer_config[k] = getattr(self, k)
        tokenizer_config.update(self.special_tokens_map)
        if self.chat_template is not None:
            if isinstance(self.chat_template, dict): tokenizer_config["chat_template"] = [{"name": k, "template": v} for k, v in self.chat_template.items()]
            else: tokenizer_config["chat_template"] = self.chat_template
        if len(self.init_inputs) > 0: tokenizer_config["init_inputs"] = copy.deepcopy(self.init_inputs)
        for file_id in self.vocab_files_names.keys(): tokenizer_config.pop(file_id, None)
        tokenizer_config = self.convert_added_tokens(tokenizer_config, add_type_field=True, save=True)
        added_tokens = {}
        for key, value in self.added_tokens_decoder.items(): added_tokens[key] = value.__getstate__()
        tokenizer_config["added_tokens_decoder"] = added_tokens
        tokenizer_class = self.__class__.__name__
        if tokenizer_class.endswith("Fast") and tokenizer_class != "PreTrainedTokenizerFast": tokenizer_class = tokenizer_class[:-4]
        tokenizer_config["tokenizer_class"] = tokenizer_class
        if getattr(self, "_auto_map", None) is not None: tokenizer_config["auto_map"] = self._auto_map
        if getattr(self, "_processor_class", None) is not None: tokenizer_config["processor_class"] = self._processor_class
        if self._auto_class is not None: custom_object_save(self, save_directory, config=tokenizer_config)
        if "name_or_path" in tokenizer_config:
            tokenizer_config.pop("name_or_path")
            tokenizer_config.pop("special_tokens_map_file", None)
            tokenizer_config.pop("tokenizer_file", None)
        if "device_map" in tokenizer_config: tokenizer_config.pop("device_map")
        with open(tokenizer_config_file, "w", encoding="utf-8") as f:
            out_str = json.dumps(tokenizer_config, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            f.write(out_str)
        logger.info(f"tokenizer config file saved in {tokenizer_config_file}")
        write_dict = self.convert_added_tokens(self.special_tokens_map_extended, save=True, add_type_field=False)
        with open(special_tokens_map_file, "w", encoding="utf-8") as f:
            out_str = json.dumps(write_dict, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            f.write(out_str)
        logger.info(f"Special tokens file saved in {special_tokens_map_file}")
        file_names = (tokenizer_config_file, special_tokens_map_file)
        save_files = self._save_pretrained(save_directory=save_directory, file_names=file_names, legacy_format=legacy_format, filename_prefix=filename_prefix)
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
        return save_files
    def _save_pretrained(self, save_directory: Union[str, os.PathLike], file_names: Tuple[str], legacy_format: Optional[bool] = None, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if legacy_format is False: raise ValueError("Only fast tokenizers (instances of PreTrainedTokenizerFast) can be saved in non legacy format.")
        save_directory = str(save_directory)
        added_tokens_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + ADDED_TOKENS_FILE)
        added_vocab = {tok: index for tok, index in self.added_tokens_encoder.items() if index >= self.vocab_size}
        if added_vocab:
            with open(added_tokens_file, "w", encoding="utf-8") as f:
                out_str = json.dumps(added_vocab, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
                f.write(out_str)
                logger.info(f"added tokens file saved in {added_tokens_file}")
        vocab_files = self.save_vocabulary(save_directory, filename_prefix=filename_prefix)
        return file_names + vocab_files + (added_tokens_file,)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]: raise NotImplementedError
    def tokenize(self, text: str, pair: Optional[str] = None, add_special_tokens: bool = False, **kwargs) -> List[str]: raise NotImplementedError
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING,
        """
            **kwargs: Passed along to the `.tokenize()` method.
        """,
        """
        Returns:
            `List[int]`, `torch.Tensor`, `tf.Tensor` or `np.ndarray`: The tokenized ids of the text.
        """)
    def encode(self, text: Union[TextInput, PreTokenizedInput, EncodedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput, EncodedInput]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False,
    truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, **kwargs) -> List[int]:
        encoded_inputs = self.encode_plus(text, text_pair=text_pair, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length, stride=stride, padding_side=padding_side, return_tensors=return_tensors, **kwargs)
        return encoded_inputs["input_ids"]
    def num_special_tokens_to_add(self, pair: bool = False) -> int: raise NotImplementedError
    def _get_padding_truncation_strategies(self, padding=False, truncation=None, max_length=None, pad_to_multiple_of=None, verbose=True, **kwargs):
        old_truncation_strategy = kwargs.pop("truncation_strategy", "do_not_truncate")
        old_pad_to_max_length = kwargs.pop("pad_to_max_length", False)
        if max_length is not None and padding is False and truncation is None:
            if verbose:
                if not self.deprecation_warnings.get("Truncation-not-explicitly-activated", False): logger.warning("Truncation was not explicitly activated but `max_length` is provided a specific value, please use `truncation=True` to explicitly truncate examples to max length. Defaulting to 'longest_first' truncation strategy. If you encode pairs of sequences (GLUE-style) with the tokenizer you can select this strategy more precisely by providing a specific strategy to `truncation`.")
                self.deprecation_warnings["Truncation-not-explicitly-activated"] = True
            truncation = "longest_first"
        if padding is False and old_pad_to_max_length:
            if verbose: warnings.warn("The `pad_to_max_length` argument is deprecated and will be removed in a future version, use `padding=True` or `padding='longest'` to pad to the longest sequence in the batch, or use `padding='max_length'` to pad to a max length. In this case, you can give a specific length with `max_length` (e.g. `max_length=45`) or leave max_length to None to pad to the maximal input size of the model (e.g. 512 for Bert).", FutureWarning)
            if max_length is None: padding_strategy = PaddingStrategy.LONGEST
            else: padding_strategy = PaddingStrategy.MAX_LENGTH
        elif padding is not False:
            if padding is True:
                if verbose:
                    if max_length is not None and (truncation is None or truncation is False or truncation == "do_not_truncate"): warnings.warn("`max_length` is ignored when `padding`=`True` and there is no truncation strategy. To pad to max length, use `padding='max_length'`.")
                    if old_pad_to_max_length is not False: warnings.warn("Though `pad_to_max_length` = `True`, it is ignored because `padding`=`True`.")
                padding_strategy = PaddingStrategy.LONGEST
            elif not isinstance(padding, PaddingStrategy): padding_strategy = PaddingStrategy(padding)
            elif isinstance(padding, PaddingStrategy): padding_strategy = padding
        else: padding_strategy = PaddingStrategy.DO_NOT_PAD
        if truncation is None and old_truncation_strategy != "do_not_truncate":
            if verbose: warnings.warn("The `truncation_strategy` argument is deprecated and will be removed in a future version, use `truncation=True` to truncate examples to a max length. You can give a specific length with `max_length` (e.g. `max_length=45`) or leave max_length to None to truncate to the maximal input size of the model (e.g. 512 for Bert).  If you have pairs of inputs, you can give a specific truncation strategy selected among `truncation='only_first'` (will only truncate the first sentence in the pairs) `truncation='only_second'` (will only truncate the second sentence in the pairs) or `truncation='longest_first'` (will iteratively remove tokens from the longest sentence in the pairs).", FutureWarning)
            truncation_strategy = TruncationStrategy(old_truncation_strategy)
        elif truncation is not False and truncation is not None:
            if truncation is True: truncation_strategy = (TruncationStrategy.LONGEST_FIRST)
            elif not isinstance(truncation, TruncationStrategy): truncation_strategy = TruncationStrategy(truncation)
            elif isinstance(truncation, TruncationStrategy): truncation_strategy = truncation
        else: truncation_strategy = TruncationStrategy.DO_NOT_TRUNCATE
        if max_length is None:
            if padding_strategy == PaddingStrategy.MAX_LENGTH:
                if self.model_max_length > LARGE_INTEGER:
                    if verbose:
                        if not self.deprecation_warnings.get("Asking-to-pad-to-max_length", False): logger.warning("Asking to pad to max_length but no maximum length is provided and the model has no predefined maximum length. Default to no padding.")
                        self.deprecation_warnings["Asking-to-pad-to-max_length"] = True
                    padding_strategy = PaddingStrategy.DO_NOT_PAD
                else: max_length = self.model_max_length
            if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE:
                if self.model_max_length > LARGE_INTEGER:
                    if verbose:
                        if not self.deprecation_warnings.get("Asking-to-truncate-to-max_length", False): logger.warning("Asking to truncate to max_length but no maximum length is provided and the model has no predefined maximum length. Default to no truncation.")
                        self.deprecation_warnings["Asking-to-truncate-to-max_length"] = True
                    truncation_strategy = TruncationStrategy.DO_NOT_TRUNCATE
                else: max_length = self.model_max_length
        if padding_strategy != PaddingStrategy.DO_NOT_PAD and (self.pad_token is None or self.pad_token_id < 0): raise ValueError("Asking to pad but the tokenizer does not have a padding token. Please select a token to use as `pad_token` `(tokenizer.pad_token = tokenizer.eos_token e.g.)` or add a new pad token via `tokenizer.add_special_tokens({'pad_token': '[PAD]'})`.")
        if (truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and padding_strategy != PaddingStrategy.DO_NOT_PAD and pad_to_multiple_of is not None and max_length is not None and (max_length % pad_to_multiple_of != 0)): raise ValueError(f"Truncation and padding are both activated but truncation length ({max_length}) is not a multiple of pad_to_multiple_of ({pad_to_multiple_of}).")
        return padding_strategy, truncation_strategy, max_length, kwargs
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None, text_target: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None,
    text_pair_target: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0,
    is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        all_kwargs = {"add_special_tokens": add_special_tokens, "padding": padding, "truncation": truncation, "max_length": max_length, "stride": stride, "is_split_into_words": is_split_into_words, "pad_to_multiple_of": pad_to_multiple_of, "padding_side": padding_side, "return_tensors": return_tensors,
        "return_token_type_ids": return_token_type_ids, "return_attention_mask": return_attention_mask, "return_overflowing_tokens": return_overflowing_tokens, "return_special_tokens_mask": return_special_tokens_mask, "return_offsets_mapping": return_offsets_mapping, "return_length": return_length,
        "split_special_tokens": kwargs.pop("split_special_tokens", self.split_special_tokens), "verbose": verbose}
        all_kwargs.update(kwargs)
        if text is None and text_target is None: raise ValueError("You need to specify either `text` or `text_target`.")
        if text is not None:
            if not self._in_target_context_manager: self._switch_to_input_mode()
            encodings = self._call_one(text=text, text_pair=text_pair, **all_kwargs)
        if text_target is not None:
            self._switch_to_target_mode()
            target_encodings = self._call_one(text=text_target, text_pair=text_pair_target, **all_kwargs)
        self._switch_to_input_mode()
        if text_target is None: return encodings
        elif text is None: return target_encodings
        else:
            encodings["labels"] = target_encodings["input_ids"]
            return encodings
    def _call_one(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]], text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None, add_special_tokens: bool = True,
    padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None,
    padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding:
        def _is_valid_text_input(t):
            if isinstance(t, str): return True
            elif isinstance(t, (list, tuple)):
                if len(t) == 0: return True
                elif isinstance(t[0], str): return True
                elif isinstance(t[0], (list, tuple)): return len(t[0]) == 0 or isinstance(t[0][0], str)
                else: return False
            else: return False
        if not _is_valid_text_input(text): raise ValueError("text input must be of type `str` (single example), `List[str]` (batch or single pretokenized example) or `List[List[str]]` (batch of pretokenized examples).")
        if text_pair is not None and not _is_valid_text_input(text_pair): raise ValueError("text input must be of type `str` (single example), `List[str]` (batch or single pretokenized example) or `List[List[str]]` (batch of pretokenized examples).")
        if is_split_into_words: is_batched = isinstance(text, (list, tuple)) and text and isinstance(text[0], (list, tuple))
        else: is_batched = isinstance(text, (list, tuple))
        if is_batched:
            if isinstance(text_pair, str): raise TypeError("when tokenizing batches of text, `text_pair` must be a list or tuple with the same length as `text`.")
            if text_pair is not None and len(text) != len(text_pair): raise ValueError(f"batch length of `text`: {len(text)} does not match batch length of `text_pair`: {len(text_pair)}.")
            batch_text_or_text_pairs = list(zip(text, text_pair)) if text_pair is not None else text
            return self.batch_encode_plus(batch_text_or_text_pairs=batch_text_or_text_pairs, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation,
            max_length=max_length, stride=stride, is_split_into_words=is_split_into_words, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors,
            return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask,
            return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose, split_special_tokens=split_special_tokens, **kwargs)
        else:
            return self.encode_plus(text=text, text_pair=text_pair, add_special_tokens=add_special_tokens, padding=padding, truncation=truncation, max_length=max_length,
            stride=stride, is_split_into_words=is_split_into_words, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors,
            return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose,
            split_special_tokens=split_special_tokens, **kwargs)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def encode_plus(self, text: Union[TextInput, PreTokenizedInput, EncodedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput, EncodedInput]] = None, add_special_tokens: bool = True,
    padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False,
    pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        return self._encode_plus(text=text, text_pair=text_pair, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length, stride=stride,
        is_split_into_words=is_split_into_words, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids, return_attention_mask=return_attention_mask,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping, return_length=return_length, verbose=verbose,
        split_special_tokens=kwargs.pop("split_special_tokens", self.split_special_tokens), **kwargs)
    def _encode_plus(self, text: Union[TextInput, PreTokenizedInput, EncodedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput, EncodedInput]] = None, add_special_tokens: bool = True,
    padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0,
    is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding: raise NotImplementedError
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair], List[EncodedInput], List[EncodedInputPair]],
    add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None, max_length: Optional[int] = None, stride: int = 0,
    is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False,
    verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        return self._batch_encode_plus(batch_text_or_text_pairs=batch_text_or_text_pairs, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy,
        max_length=max_length, stride=stride, is_split_into_words=is_split_into_words, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors, return_token_type_ids=return_token_type_ids,
        return_attention_mask=return_attention_mask, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_offsets_mapping=return_offsets_mapping,
        return_length=return_length, verbose=verbose, split_special_tokens=split_special_tokens, **kwargs)
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair], List[EncodedInput], List[EncodedInputPair]],
    add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None,
    stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding: raise NotImplementedError
    def pad(self, encoded_inputs: Union[BatchEncoding, List[BatchEncoding], Dict[str, EncodedInput], Dict[str, List[EncodedInput]], List[Dict[str, EncodedInput]]], padding: Union[bool, str, PaddingStrategy] = True,
    max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, verbose: bool = True) -> BatchEncoding:
        if self.__class__.__name__.endswith("Fast"):
            if not self.deprecation_warnings.get("Asking-to-pad-a-fast-tokenizer", False):
                logger.warning_advice(f"You're using a {self.__class__.__name__} tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.")
                self.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = True
        if isinstance(encoded_inputs, (list, tuple)) and isinstance(encoded_inputs[0], Mapping): encoded_inputs = {key: [example[key] for example in encoded_inputs] for key in encoded_inputs[0].keys()}
        if self.model_input_names[0] not in encoded_inputs: raise ValueError(f"You should supply an encoding or a list of encodings to this method that includes {self.model_input_names[0]}, but you provided {list(encoded_inputs.keys())}")
        required_input = encoded_inputs[self.model_input_names[0]]
        if required_input is None or (isinstance(required_input, Sized) and len(required_input) == 0):
            if return_attention_mask: encoded_inputs["attention_mask"] = []
            return encoded_inputs
        first_element = required_input[0]
        if isinstance(first_element, (list, tuple)):
            for item in required_input:
                if len(item) != 0:
                    first_element = item[0]
                    break
        if not isinstance(first_element, (int, list, tuple)):
            if is_tf_tensor(first_element): return_tensors = "tf" if return_tensors is None else return_tensors
            elif is_torch_tensor(first_element): return_tensors = "pt" if return_tensors is None else return_tensors
            elif isinstance(first_element, np.ndarray): return_tensors = "np" if return_tensors is None else return_tensors
            else: raise ValueError(f"type of {first_element} unknown: {type(first_element)}. Should be one of a python, numpy, pytorch or tensorflow object.")
            for key, value in encoded_inputs.items(): encoded_inputs[key] = to_py_obj(value)
        padding_strategy, _, max_length, _ = self._get_padding_truncation_strategies(padding=padding, max_length=max_length, verbose=verbose)
        required_input = encoded_inputs[self.model_input_names[0]]
        if required_input and not isinstance(required_input[0], (list, tuple)):
            encoded_inputs = self._pad(encoded_inputs, max_length=max_length, padding_strategy=padding_strategy, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
            return BatchEncoding(encoded_inputs, tensor_type=return_tensors)
        batch_size = len(required_input)
        assert all(len(v) == batch_size for v in encoded_inputs.values()), "Some items in the output dictionary have a different batch size than others."
        if padding_strategy == PaddingStrategy.LONGEST:
            max_length = max(len(inputs) for inputs in required_input)
            padding_strategy = PaddingStrategy.MAX_LENGTH
        batch_outputs = {}
        for i in range(batch_size):
            inputs = {k: v[i] for k, v in encoded_inputs.items()}
            outputs = self._pad(inputs, max_length=max_length, padding_strategy=padding_strategy, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        return BatchEncoding(batch_outputs, tensor_type=return_tensors)
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return len(token_ids_0) * [0]
        return [0] * len(token_ids_0) + [1] * len(token_ids_1)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return token_ids_0
        return token_ids_0 + token_ids_1
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def prepare_for_model(self, ids: List[int], pair_ids: Optional[List[int]] = None, add_special_tokens: bool = True, padding: Union[bool, str, PaddingStrategy] = False, truncation: Union[bool, str, TruncationStrategy] = None,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True,
    prepend_batch_axis: bool = False, **kwargs) -> BatchEncoding:
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(padding=padding, truncation=truncation, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, verbose=verbose, **kwargs)
        pair = bool(pair_ids is not None)
        len_ids = len(ids)
        len_pair_ids = len(pair_ids) if pair else 0
        if return_token_type_ids and not add_special_tokens: raise ValueError("Asking to return token_type_ids while setting add_special_tokens to False results in an undefined behavior. Please set add_special_tokens to True or set return_token_type_ids to None.")
        if (return_overflowing_tokens and truncation_strategy == TruncationStrategy.LONGEST_FIRST and pair_ids is not None): raise ValueError("Not possible to return overflowing tokens for pair of sequences with the `longest_first`. Please select another truncation strategy than `longest_first`, for instance `only_second` or `only_first`.")
        if return_token_type_ids is None: return_token_type_ids = "token_type_ids" in self.model_input_names
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        encoded_inputs = {}
        total_len = len_ids + len_pair_ids + (self.num_special_tokens_to_add(pair=pair) if add_special_tokens else 0)
        overflowing_tokens = []
        if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and max_length and total_len > max_length: ids, pair_ids, overflowing_tokens = self.truncate_sequences(ids, pair_ids=pair_ids, num_tokens_to_remove=total_len - max_length, truncation_strategy=truncation_strategy, stride=stride)
        if return_overflowing_tokens:
            encoded_inputs["overflowing_tokens"] = overflowing_tokens
            encoded_inputs["num_truncated_tokens"] = total_len - max_length
        if add_special_tokens:
            sequence = self.build_inputs_with_special_tokens(ids, pair_ids)
            token_type_ids = self.create_token_type_ids_from_sequences(ids, pair_ids)
        else:
            sequence = ids + pair_ids if pair else ids
            token_type_ids = [0] * len(ids) + ([0] * len(pair_ids) if pair else [])
        encoded_inputs["input_ids"] = sequence
        if return_token_type_ids: encoded_inputs["token_type_ids"] = token_type_ids
        if return_special_tokens_mask:
            if add_special_tokens: encoded_inputs["special_tokens_mask"] = self.get_special_tokens_mask(ids, pair_ids)
            else: encoded_inputs["special_tokens_mask"] = [0] * len(sequence)
        self._eventual_warn_about_too_long_sequence(encoded_inputs["input_ids"], max_length, verbose)
        if padding_strategy != PaddingStrategy.DO_NOT_PAD or return_attention_mask: encoded_inputs = self.pad(encoded_inputs, max_length=max_length, padding=padding_strategy.value, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        if return_length: encoded_inputs["length"] = len(encoded_inputs["input_ids"])
        batch_outputs = BatchEncoding(encoded_inputs, tensor_type=return_tensors, prepend_batch_axis=prepend_batch_axis)
        return batch_outputs
    def truncate_sequences(self, ids: List[int], pair_ids: Optional[List[int]] = None, num_tokens_to_remove: int = 0, truncation_strategy: Union[str, TruncationStrategy] = "longest_first", stride: int = 0) -> Tuple[List[int], List[int], List[int]]:
        if num_tokens_to_remove <= 0: return ids, pair_ids, []
        if not isinstance(truncation_strategy, TruncationStrategy): truncation_strategy = TruncationStrategy(truncation_strategy)
        overflowing_tokens = []
        if truncation_strategy == TruncationStrategy.ONLY_FIRST or (truncation_strategy == TruncationStrategy.LONGEST_FIRST and pair_ids is None):
            if len(ids) > num_tokens_to_remove:
                window_len = min(len(ids), stride + num_tokens_to_remove)
                if self.truncation_side == "left":
                    overflowing_tokens = ids[:window_len]
                    ids = ids[num_tokens_to_remove:]
                elif self.truncation_side == "right":
                    overflowing_tokens = ids[-window_len:]
                    ids = ids[:-num_tokens_to_remove]
                else: raise ValueError(f"invalid truncation strategy: {self.truncation_side}, use 'left' or 'right'.")
            else:
                error_msg = (f"We need to remove {num_tokens_to_remove} to truncate the input but the first sequence has a length {len(ids)}. ")
                if truncation_strategy == TruncationStrategy.ONLY_FIRST: error_msg = (error_msg + f"Please select another truncation strategy than {truncation_strategy}, for instance 'longest_first' or 'only_second'.")
                logger.error(error_msg)
        elif truncation_strategy == TruncationStrategy.LONGEST_FIRST:
            logger.warning(f"Be aware, overflowing tokens are not returned for the setting you have chosen, i.e. sequence pairs with the '{TruncationStrategy.LONGEST_FIRST.value}' truncation strategy. So the returned list will always be empty even if some tokens have been removed.")
            len_pair_ids = len(pair_ids) if pair_ids is not None else 0
            len_ids = len(ids)
            first_remove = min(abs(len_pair_ids - len_ids), num_tokens_to_remove)
            second_remove = num_tokens_to_remove - first_remove
            if len_ids > len_pair_ids:
                ids_to_move = first_remove + second_remove // 2
                pair_ids_to_move = second_remove - second_remove // 2
            else:
                ids_to_move = second_remove // 2
                pair_ids_to_move = first_remove + second_remove - (second_remove // 2)
            if self.truncation_side == "right":
                ids = ids[:-ids_to_move] if ids_to_move > 0 else ids
                pair_ids = pair_ids[:-pair_ids_to_move] if pair_ids is not None and pair_ids_to_move > 0 else pair_ids
            elif self.truncation_side == "left":
                ids = ids[ids_to_move:]
                pair_ids = pair_ids[pair_ids_to_move:] if pair_ids is not None else None
            else: raise ValueError(f"invalid truncation strategy:{self.truncation_side}")
        elif truncation_strategy == TruncationStrategy.ONLY_SECOND and pair_ids is not None:
            if len(pair_ids) > num_tokens_to_remove:
                window_len = min(len(pair_ids), stride + num_tokens_to_remove)
                if self.truncation_side == "right":
                    overflowing_tokens = pair_ids[-window_len:]
                    pair_ids = pair_ids[:-num_tokens_to_remove]
                elif self.truncation_side == "left":
                    overflowing_tokens = pair_ids[:window_len]
                    pair_ids = pair_ids[num_tokens_to_remove:]
                else: raise ValueError(f"invalid truncation strategy:{self.truncation_side}")
            else: logger.error(f"We need to remove {num_tokens_to_remove} to truncate the input but the second sequence has a length {len(pair_ids)}. Please select another truncation strategy than {truncation_strategy}, for instance 'longest_first' or 'only_first'.")
        return (ids, pair_ids, overflowing_tokens)
    def _pad(self, encoded_inputs: Union[Dict[str, EncodedInput], BatchEncoding], max_length: Optional[int] = None, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_attention_mask: Optional[bool] = None) -> dict:
        if return_attention_mask is None: return_attention_mask = "attention_mask" in self.model_input_names
        required_input = encoded_inputs[self.model_input_names[0]]
        if padding_strategy == PaddingStrategy.LONGEST: max_length = len(required_input)
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0): max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_padded = padding_strategy != PaddingStrategy.DO_NOT_PAD and len(required_input) != max_length
        if return_attention_mask and "attention_mask" not in encoded_inputs: encoded_inputs["attention_mask"] = [1] * len(required_input)
        if needs_to_be_padded:
            difference = max_length - len(required_input)
            padding_side = padding_side if padding_side is not None else self.padding_side
            if padding_side == "right":
                if return_attention_mask: encoded_inputs["attention_mask"] = encoded_inputs["attention_mask"] + [0] * difference
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = (encoded_inputs["token_type_ids"] + [self.pad_token_type_id] * difference)
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = encoded_inputs["special_tokens_mask"] + [1] * difference
                encoded_inputs[self.model_input_names[0]] = required_input + [self.pad_token_id] * difference
            elif padding_side == "left":
                if return_attention_mask: encoded_inputs["attention_mask"] = [0] * difference + encoded_inputs["attention_mask"]
                if "token_type_ids" in encoded_inputs: encoded_inputs["token_type_ids"] = [self.pad_token_type_id] * difference + encoded_inputs["token_type_ids"]
                if "special_tokens_mask" in encoded_inputs: encoded_inputs["special_tokens_mask"] = [1] * difference + encoded_inputs["special_tokens_mask"]
                encoded_inputs[self.model_input_names[0]] = [self.pad_token_id] * difference + required_input
            else: raise ValueError(f"Invalid padding strategy:{padding_side}")
        return encoded_inputs
    def convert_tokens_to_string(self, tokens: List[str]) -> str: raise NotImplementedError
    def batch_decode(self, sequences: Union[List[int], List[List[int]], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, **kwargs) -> List[str]: return [self.decode(seq, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, **kwargs) for seq in sequences]
    def decode(self, token_ids: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, **kwargs) -> str:
        token_ids = to_py_obj(token_ids)
        return self._decode(token_ids=token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, **kwargs)
    def _decode(self, token_ids: Union[int, List[int]], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, **kwargs) -> str: raise NotImplementedError
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        assert already_has_special_tokens and token_ids_1 is None, ("You cannot use ``already_has_special_tokens=False`` with this tokenizer. Please use a slow (full python) tokenizer to activate this argument. Or set `return_special_tokens_mask=True` when calling the encoding method to get the special tokens mask in any tokenizer. ")
        all_special_ids = self.all_special_ids
        special_tokens_mask = [1 if token in all_special_ids else 0 for token in token_ids_0]
        return special_tokens_mask
    @staticmethod
    def clean_up_tokenization(out_string: str) -> str:
        out_string = (out_string.replace(" .", ".").replace(" ?", "?").replace(" !", "!").replace(" ,", ",").replace(" ' ", "'").replace(" n't", "n't").replace(" 'm", "'m").replace(" 's", "'s").replace(" 've", "'ve").replace(" 're", "'re"))
        return out_string
    def _eventual_warn_about_too_long_sequence(self, ids: List[int], max_length: Optional[int], verbose: bool):
        if max_length is None and len(ids) > self.model_max_length and verbose: self.deprecation_warnings["sequence-length-is-longer-than-the-specified-maximum"] = True
    def _switch_to_input_mode(self): pass
    def _switch_to_target_mode(self): pass
    @contextmanager
    def as_target_tokenizer(self):
        self._switch_to_target_mode()
        self._in_target_context_manager = True
        yield
        self._in_target_context_manager = False
        self._switch_to_input_mode()
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoTokenizer"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    def prepare_seq2seq_batch(self, src_texts: List[str], tgt_texts: Optional[List[str]] = None, max_length: Optional[int] = None, max_target_length: Optional[int] = None, padding: str = "longest", return_tensors: str = None, truncation: bool = True, **kwargs) -> BatchEncoding:
        formatted_warning = """
`prepare_seq2seq_batch` is deprecated and will be removed in version 1 of Sapiens Transformers. Use the regular
`__call__` method to prepare your inputs and targets.
Here is a short example:
model_inputs = tokenizer(src_texts, text_target=tgt_texts, ...)
If you either need to use different keyword arguments for the source and target texts, you should do two calls like
this:
model_inputs = tokenizer(src_texts, ...)
labels = tokenizer(text_target=tgt_texts, ...)
model_inputs["labels"] = labels["input_ids"]
See the documentation of your specific tokenizer for more details on the specific arguments to the tokenizer of choice.
For a more complete example, see the implementation of `prepare_seq2seq_batch`.
"""
        warnings.warn(formatted_warning, FutureWarning)
        kwargs.pop("src_lang", None)
        kwargs.pop("tgt_lang", None)
        if max_length is None: max_length = self.model_max_length
        model_inputs = self(src_texts, add_special_tokens=True, return_tensors=return_tensors, max_length=max_length, padding=padding, truncation=truncation, **kwargs)
        if tgt_texts is None: return model_inputs
        if max_target_length is None: max_target_length = max_length
        with self.as_target_tokenizer(): labels = self(tgt_texts, add_special_tokens=True, return_tensors=return_tensors, padding=padding, max_length=max_target_length, truncation=truncation, **kwargs)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
def get_fast_tokenizer_file(tokenization_files: List[str]) -> str:
    tokenizer_files_map = {}
    for file_name in tokenization_files:
        search = _re_tokenizer_file.search(file_name)
        if search is not None:
            v = search.groups()[0]
            tokenizer_files_map[v] = file_name
    available_versions = sorted(tokenizer_files_map.keys())
    tokenizer_file = FULL_TOKENIZER_FILE
    sapiens_transformers_version = version.parse(__version__)
    for v in available_versions:
        if version.parse(v) <= sapiens_transformers_version: tokenizer_file = tokenizer_files_map[v]
        else: break
    return tokenizer_file
PreTrainedTokenizerBase.push_to_hub = copy_func(PreTrainedTokenizerBase.push_to_hub)
if PreTrainedTokenizerBase.push_to_hub.__doc__ is not None: PreTrainedTokenizerBase.push_to_hub.__doc__ = PreTrainedTokenizerBase.push_to_hub.__doc__.format(object="tokenizer", object_class="AutoTokenizer", object_files="tokenizer files")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
