"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import warnings
from dataclasses import dataclass
from itertools import groupby
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union
import numpy as np
from ...tokenization_utils import PreTrainedTokenizer
from ...tokenization_utils_base import AddedToken, BatchEncoding
from ...utils import (ModelOutput, PaddingStrategy, TensorType, add_end_docstrings, is_flax_available, is_tf_available, is_torch_available, logging, to_py_obj)
logger = logging.get_logger(__name__)
if TYPE_CHECKING:
    if is_torch_available(): import torch
    if is_tf_available(): import tensorflow as tf
    if is_flax_available(): import jax.numpy as jnp
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'tokenizer_config_file': 'tokenizer_config.json'}
WAV2VEC2_KWARGS_DOCSTRING = r"""
            padding (`bool`, `str` or [`~utils.PaddingStrategy`], *optional*, defaults to `False`):
                Activates and controls padding. Accepts the following values:
                - `True` or `'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
                  sequence if provided).
                - `'max_length'`: Pad to a maximum length specified with the argument `max_length` or to the maximum
                  acceptable input length for the model if that argument is not provided.
                - `False` or `'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of different
                  lengths).
            max_length (`int`, *optional*):
                Controls the maximum length to use by one of the truncation/padding parameters.
                If left unset or set to `None`, this will use the predefined model maximum length if a maximum length
                is required by one of the truncation/padding parameters. If the model has no specific maximum input
                length (like XLNet) truncation/padding to a maximum length will be deactivated.
            pad_to_multiple_of (`int`, *optional*):
                If set will pad the sequence to a multiple of the provided value. This is especially useful to enable
                the use of Tensor Cores on NVIDIA hardware with compute capability `>= 7.5` (Volta).
            return_tensors (`str` or [`~utils.TensorType`], *optional*):
                If set, will return tensors instead of list of python integers. Acceptable values are:
                - `'tf'`: Return TensorFlow `tf.constant` objects.
                - `'pt'`: Return PyTorch `torch.Tensor` objects.
                - `'np'`: Return Numpy `np.ndarray` objects.
            verbose (`bool`, *optional*, defaults to `True`):
                Whether or not to print more information and warnings.
"""
ListOfDict = List[Dict[str, Union[int, str]]]
@dataclass
class Wav2Vec2CTCTokenizerOutput(ModelOutput):
    """Args:"""
    text: Union[List[str], str]
    char_offsets: Union[List[ListOfDict], ListOfDict] = None
    word_offsets: Union[List[ListOfDict], ListOfDict] = None
class Wav2Vec2CTCTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", unk_token="<unk>", pad_token="<pad>", word_delimiter_token="|", replace_word_delimiter_char=" ",
    do_lower_case=False, target_lang=None, **kwargs):
        self._word_delimiter_token = word_delimiter_token
        self.do_lower_case = do_lower_case
        self.replace_word_delimiter_char = replace_word_delimiter_char
        self.target_lang = target_lang
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.vocab = json.load(vocab_handle)
        if target_lang is not None: self.encoder = self.vocab[target_lang]
        else: self.encoder = self.vocab
        self.decoder = {v: k for k, v in self.encoder.items()}
        super().__init__(unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, do_lower_case=do_lower_case, word_delimiter_token=word_delimiter_token,
        replace_word_delimiter_char=replace_word_delimiter_char, target_lang=target_lang, **kwargs)
        for token in self.encoder.keys():
            if len(token) > 1: self.add_tokens(AddedToken(token, rstrip=True, lstrip=True, normalized=False))
    def set_target_lang(self, target_lang: str):
        if self.vocab == self.encoder: raise ValueError(f"{self.vocab} is not a multi-lingual, nested tokenizer. Cannot set target language.")
        if target_lang not in self.vocab: raise ValueError(f"{target_lang} does not exist. Choose one of {', '.join(self.vocab.keys())}.")
        self.target_lang = target_lang
        self.init_kwargs["target_lang"] = target_lang
        self.encoder = self.vocab[target_lang]
        self.decoder = {v: k for k, v in self.encoder.items()}
        for token in self.encoder.keys():
            if len(token) > 1: self.add_tokens(AddedToken(token, rstrip=True, lstrip=True, normalized=False))
    @property
    def word_delimiter_token(self) -> str:
        if self._word_delimiter_token is None and self.verbose:
            logger.error("Using word_delimiter_token, but it is not set yet.")
            return None
        return str(self._word_delimiter_token)
    @property
    def word_delimiter_token_id(self) -> Optional[int]:
        if self._word_delimiter_token is None: return None
        return self.convert_tokens_to_ids(self.word_delimiter_token)
    @word_delimiter_token.setter
    def word_delimiter_token(self, value): self._word_delimiter_token = value
    @word_delimiter_token_id.setter
    def word_delimiter_token_id(self, value): self._word_delimiter_token = self.convert_tokens_to_ids(value)
    @property
    def vocab_size(self) -> int: return len(self.decoder)
    def get_vocab(self) -> Dict:
        vocab = dict(self.encoder)
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _add_tokens(self, new_tokens: Union[List[str], List[AddedToken]], special_tokens: bool = False) -> int:
        to_add = []
        for token in new_tokens:
            if isinstance(token, str): to_add.append(AddedToken(token, rstrip=False, lstrip=False, normalized=False))
            else: to_add.append(token)
        return super()._add_tokens(to_add, special_tokens)
    def _tokenize(self, text, **kwargs):
        if self.do_lower_case: text = text.upper()
        return list(text.replace(" ", self.word_delimiter_token))
    def _convert_token_to_id(self, token: str) -> int: return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index: int) -> str:
        result = self.decoder.get(index, self.unk_token)
        return result
    def convert_tokens_to_string(self, tokens: List[str], group_tokens: bool = True, spaces_between_special_tokens: bool = False, output_char_offsets: bool = False,
    output_word_offsets: bool = False) -> Dict[str, Union[str, float]]:
        if len(tokens) == 0: return {"text": "", "char_offsets": [], "word_offsets": []}
        if group_tokens: chars, char_repetitions = zip(*((token, len(list(group_iter))) for token, group_iter in groupby(tokens)))
        else:
            chars = tokens
            char_repetitions = len(tokens) * [1]
        processed_chars = list(filter(lambda char: char != self.pad_token, chars))
        processed_chars = [self.replace_word_delimiter_char if char == self.word_delimiter_token else char for char in processed_chars]
        char_offsets = word_offsets = None
        if output_char_offsets or output_word_offsets:
            char_offsets = self._compute_offsets(char_repetitions, chars, self.pad_token)
            if len(char_offsets) != len(processed_chars): raise ValueError(f"`char_offsets`: {char_offsets} and `processed_tokens`: {processed_chars} have to be of the same length, but are: `len(offsets)`: {len(char_offsets)} and `len(processed_tokens)`: {len(processed_chars)}")
            for i, char in enumerate(processed_chars): char_offsets[i]["char"] = char
            word_offsets = None
            if output_word_offsets: word_offsets = self._get_word_offsets(char_offsets, self.replace_word_delimiter_char)
            if not output_char_offsets: char_offsets = None
        join_char = " " if spaces_between_special_tokens else ""
        string = join_char.join(processed_chars).strip()
        if self.do_lower_case: string = string.lower()
        return {"text": string, "char_offsets": char_offsets, "word_offsets": word_offsets}
    @staticmethod
    def _compute_offsets(char_repetitions: List[int], chars: List[str], ctc_token: int) -> List[Dict[str, Union[str, int]]]:
        end_indices = np.asarray(char_repetitions).cumsum()
        start_indices = np.concatenate(([0], end_indices[:-1]))
        offsets = [{"char": t, "start_offset": s, "end_offset": e} for t, s, e in zip(chars, start_indices, end_indices)]
        offsets = list(filter(lambda offsets: offsets["char"] != ctc_token, offsets))
        return offsets
    @staticmethod
    def _get_word_offsets(offsets: Dict[str, Union[str, float]], word_delimiter_char: str = " ") -> Dict[str, Union[str, float]]:
        word_offsets = []
        last_state = "SPACE"
        word = ""
        start_offset = 0
        end_offset = 0
        for i, offset in enumerate(offsets):
            char = offset["char"]
            state = "SPACE" if char == word_delimiter_char else "WORD"
            if state == last_state:
                end_offset = offset["end_offset"]
                word += char
            else:
                if state == "SPACE": word_offsets.append({"word": word, "start_offset": start_offset, "end_offset": end_offset})
                else:
                    start_offset = offset["start_offset"]
                    end_offset = offset["end_offset"]
                    word = char
            last_state = state
        if last_state == "WORD": word_offsets.append({"word": word, "start_offset": start_offset, "end_offset": end_offset})
        return word_offsets
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        if is_split_into_words: text = " " + text
        return (text, kwargs)
    def _decode(self, token_ids: List[int], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, group_tokens: bool = True, spaces_between_special_tokens: bool = False,
    output_word_offsets: Optional[bool] = False, output_char_offsets: Optional[bool] = False) -> str:
        filtered_tokens = self.convert_ids_to_tokens(token_ids, skip_special_tokens=skip_special_tokens)
        result = []
        for token in filtered_tokens:
            if skip_special_tokens and (token in self.all_special_ids or (token != self.pad_token and token in self.all_special_tokens)): continue
            result.append(token)
        string_output = self.convert_tokens_to_string(result, group_tokens=group_tokens, spaces_between_special_tokens=spaces_between_special_tokens,
        output_word_offsets=output_word_offsets, output_char_offsets=output_char_offsets)
        text = string_output["text"]
        clean_up_tokenization_spaces = (clean_up_tokenization_spaces if clean_up_tokenization_spaces is not None else self.clean_up_tokenization_spaces)
        if clean_up_tokenization_spaces: text = self.clean_up_tokenization(text)
        if output_word_offsets or output_char_offsets: return Wav2Vec2CTCTokenizerOutput(text=text, char_offsets=string_output["char_offsets"], word_offsets=string_output["word_offsets"])
        else: return text
    def batch_decode(self, sequences: Union[List[int], List[List[int]], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None,
    output_char_offsets: bool = False, output_word_offsets: bool = False, **kwargs) -> List[str]:
        batch_decoded = [self.decode(seq, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, output_char_offsets=output_char_offsets,
        output_word_offsets=output_word_offsets, **kwargs) for seq in sequences]
        if output_char_offsets or output_word_offsets: return Wav2Vec2CTCTokenizerOutput({k: [d[k] for d in batch_decoded] for k in batch_decoded[0]})
        return batch_decoded
    def decode(self, token_ids: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None,
    output_char_offsets: bool = False, output_word_offsets: bool = False, **kwargs) -> str:
        token_ids = to_py_obj(token_ids)
        return self._decode(token_ids=token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, output_char_offsets=output_char_offsets,
        output_word_offsets=output_word_offsets, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.vocab, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        return (vocab_file,)
class Wav2Vec2Tokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = {"vocab_file": {'facebook/wav2vec2-base-960h': 'https://huggingface.co/facebook/wav2vec2-base-960h/resolve/main/vocab.json'},
    "tokenizer_config_file": {'facebook/wav2vec2-base-960h': 'https://huggingface.co/facebook/wav2vec2-base-960h/resolve/main/tokenizer.json'}}
    model_input_names = ["input_values", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", unk_token="<unk>", pad_token="<pad>", word_delimiter_token="|", do_lower_case=False,
    do_normalize=False, return_attention_mask=False, **kwargs):
        warnings.warn("The class `Wav2Vec2Tokenizer` is deprecated and will be removed in version 1 of Sapiens Transformers. Please use `Wav2Vec2Processor` or `Wav2Vec2CTCTokenizer` instead.", FutureWarning)
        self._word_delimiter_token = word_delimiter_token
        self.do_lower_case = do_lower_case
        self.return_attention_mask = return_attention_mask
        self.do_normalize = do_normalize
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        super().__init__(unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, do_lower_case=do_lower_case, do_normalize=do_normalize,
        return_attention_mask=return_attention_mask, word_delimiter_token=word_delimiter_token, **kwargs)
    @property
    def word_delimiter_token(self) -> str:
        if self._word_delimiter_token is None and self.verbose:
            logger.error("Using word_delimiter_token, but it is not set yet.")
            return None
        return str(self._word_delimiter_token)
    @property
    def word_delimiter_token_id(self) -> Optional[int]:
        if self._word_delimiter_token is None: return None
        return self.convert_tokens_to_ids(self.word_delimiter_token)
    @word_delimiter_token.setter
    def word_delimiter_token(self, value): self._word_delimiter_token = value
    @word_delimiter_token_id.setter
    def word_delimiter_token_id(self, value): self._word_delimiter_token = self.convert_tokens_to_ids(value)
    @add_end_docstrings(WAV2VEC2_KWARGS_DOCSTRING)
    def __call__(self, raw_speech: Union[np.ndarray, List[float], List[np.ndarray], List[List[float]]], padding: Union[bool, str, PaddingStrategy] = False,
    max_length: Optional[int] = None, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    verbose: bool = True, **kwargs) -> BatchEncoding:
        is_batched_numpy = isinstance(raw_speech, np.ndarray) and len(raw_speech.shape) > 1
        if is_batched_numpy and len(raw_speech.shape) > 2: raise ValueError(f"Only mono-channel audio is supported for input to {self}")
        is_batched = is_batched_numpy or (isinstance(raw_speech, (list, tuple)) and (isinstance(raw_speech[0], (np.ndarray, tuple, list))))
        if is_batched and not isinstance(raw_speech[0], np.ndarray): raw_speech = [np.asarray(speech) for speech in raw_speech]
        elif not is_batched and not isinstance(raw_speech, np.ndarray): raw_speech = np.asarray(raw_speech)
        if not is_batched: raw_speech = [raw_speech]
        if self.do_normalize: raw_speech = [(x - np.mean(x)) / np.sqrt(np.var(x) + 1e-5) for x in raw_speech]
        encoded_inputs = BatchEncoding({"input_values": raw_speech})
        padded_inputs = self.pad(encoded_inputs, padding=padding, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side,
        return_attention_mask=self.return_attention_mask, return_tensors=return_tensors, verbose=verbose)
        return padded_inputs
    @property
    def vocab_size(self) -> int: return len(self.decoder)
    def get_vocab(self) -> Dict: return dict(self.encoder, **self.added_tokens_encoder)
    def _convert_token_to_id(self, token: str) -> int: return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index: int) -> str:
        result = self.decoder.get(index, self.unk_token)
        return result
    def convert_tokens_to_string(self, tokens: List[str]) -> str:
        grouped_tokens = [token_group[0] for token_group in groupby(tokens)]
        filtered_tokens = list(filter(lambda token: token != self.pad_token, grouped_tokens))
        string = "".join([" " if token == self.word_delimiter_token else token for token in filtered_tokens]).strip()
        if self.do_lower_case: string = string.lower()
        return string
    def _decode(self, token_ids: List[int], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, **kwargs) -> str:
        filtered_tokens = self.convert_ids_to_tokens(token_ids, skip_special_tokens=skip_special_tokens)
        result = []
        for token in filtered_tokens:
            if skip_special_tokens and (token in self.all_special_ids or (token != self.pad_token and token in self.all_special_tokens)): continue
            result.append(token)
        text = self.convert_tokens_to_string(result)
        clean_up_tokenization_spaces = (clean_up_tokenization_spaces if clean_up_tokenization_spaces is not None else self.clean_up_tokenization_spaces)
        if clean_up_tokenization_spaces:
            clean_text = self.clean_up_tokenization(text)
            return clean_text
        else: return text
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.encoder, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        return (vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
