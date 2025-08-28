"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from dataclasses import dataclass
from itertools import groupby
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
import numpy as np
from ...tokenization_utils import PreTrainedTokenizer
from ...tokenization_utils_base import AddedToken
from ...utils import (ModelOutput, is_flax_available, is_tf_available, is_torch_available, logging, requires_backends, to_py_obj)
logger = logging.get_logger(__name__)
if TYPE_CHECKING:
    if is_torch_available(): import torch
    if is_tf_available(): import tensorflow as tf
    if is_flax_available(): import jax.numpy as jnp
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'tokenizer_config_file': 'tokenizer_config.json'}
ListOfDict = List[Dict[str, Union[int, str]]]
@dataclass
class Wav2Vec2PhonemeCTCTokenizerOutput(ModelOutput):
    """Args:"""
    text: Union[List[str], str]
    char_offsets: Union[List[ListOfDict], ListOfDict] = None
class Wav2Vec2PhonemeCTCTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", unk_token="<unk>", pad_token="<pad>", phone_delimiter_token=" ", word_delimiter_token=None,
    do_phonemize=True, phonemizer_lang="en-us", phonemizer_backend="espeak", **kwargs):
        self._word_delimiter_token = word_delimiter_token
        self._phone_delimiter_token = phone_delimiter_token
        self.do_phonemize = do_phonemize
        self.phonemizer_lang = phonemizer_lang
        self.phonemizer_backend = phonemizer_backend
        if do_phonemize: self.init_backend(self.phonemizer_lang)
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        super().__init__(unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, word_delimiter_token=word_delimiter_token,
        phone_delimiter_token=phone_delimiter_token, do_phonemize=do_phonemize, phonemizer_lang=phonemizer_lang, phonemizer_backend=phonemizer_backend, **kwargs)
    @property
    def vocab_size(self) -> int: return len(self.decoder)
    def get_vocab(self) -> Dict:
        vocab = dict(self.encoder.copy())
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _add_tokens(self, new_tokens: Union[List[str], List[AddedToken]], special_tokens: bool = False) -> int:
        to_add = []
        for token in new_tokens:
            if isinstance(token, str): to_add.append(AddedToken(token, rstrip=False, lstrip=False, normalized=True, special=special_tokens))
            else: to_add.append(token)
        return super()._add_tokens(to_add, special_tokens)
    def init_backend(self, phonemizer_lang: str):
        requires_backends(self, "phonemizer")
        from phonemizer.backend import BACKENDS
        self.backend = BACKENDS[self.phonemizer_backend](phonemizer_lang, language_switch="remove-flags")
    def prepare_for_tokenization(self, text: str, is_split_into_words: bool = False, phonemizer_lang: Optional[str] = None, do_phonemize: Optional[bool] = None) -> Tuple[str, Dict[str, Any]]:
        if is_split_into_words: text = " " + text
        if do_phonemize is not None: self.do_phonemize = do_phonemize
        if phonemizer_lang is not None:
            self.phonemizer_lang = phonemizer_lang
            self.init_backend(phonemizer_lang)
        return (text, {})
    def _tokenize(self, text, **kwargs):
        text = text.strip()
        if self.do_phonemize:
            text = text.lower()
            text = self.phonemize(text, self.phonemizer_lang)
        tokens = text.split(" ")
        tokens = list(filter(lambda p: p.strip() != "", tokens))
        return tokens
    def phonemize(self, text: str, phonemizer_lang: Optional[str] = None) -> str:
        from phonemizer.separator import Separator
        word_delimiter = self.word_delimiter_token + " " if self.word_delimiter_token is not None else ""
        if phonemizer_lang is not None and phonemizer_lang != self.phonemizer_lang: self.init_backend(phonemizer_lang)
        else: phonemizer_lang = self.phonemizer_lang
        separator = Separator(phone=self.phone_delimiter_token, word=word_delimiter, syllable="")
        phonemes = self.backend.phonemize([text], separator=separator)
        phonemes = phonemes[0].strip()
        return phonemes
    @property
    def word_delimiter_token(self) -> str:
        if self._word_delimiter_token is None:
            if self.verbose: logger.error("Using word_delimiter_token, but it is not set yet.")
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
    def phone_delimiter_token(self) -> str:
        if self._phone_delimiter_token is None:
            if self.verbose: logger.error("Using phone_delimiter_token, but it is not set yet.")
            return None
        return str(self._phone_delimiter_token)
    @property
    def phone_delimiter_token_id(self) -> Optional[int]:
        if self._phone_delimiter_token is None: return None
        return self.convert_tokens_to_ids(self.phone_delimiter_token)
    @phone_delimiter_token.setter
    def phone_delimiter_token(self, value): self._phone_delimiter_token = value
    @phone_delimiter_token_id.setter
    def phone_delimiter_token_id(self, value): self._phone_delimiter_token = self.convert_tokens_to_ids(value)
    def _convert_token_to_id(self, token: str) -> int: return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index: int) -> str:
        result = self.decoder.get(index, self.unk_token)
        return result
    def convert_tokens_to_string(self, tokens: List[str], group_tokens: bool = True, spaces_between_special_tokens: bool = False, filter_word_delimiter_token: bool = True, output_char_offsets: bool = False) -> str:
        if group_tokens: chars, char_repetitions = zip(*((token, len(list(group_iter))) for token, group_iter in groupby(tokens)))
        else:
            chars = tokens
            char_repetitions = len(tokens) * [1]
        processed_chars = list(filter(lambda char: char != self.pad_token, chars))
        if filter_word_delimiter_token and self.word_delimiter_token is not None: processed_chars = list(filter(lambda token: token != self.word_delimiter_token, processed_chars))
        char_offsets = None
        if output_char_offsets:
            word_delimiter_token_for_offsets = (self.word_delimiter_token if filter_word_delimiter_token is True else None)
            char_offsets = self._compute_offsets(char_repetitions, chars, self.pad_token, word_delimiter_token=word_delimiter_token_for_offsets)
            if len(char_offsets) != len(processed_chars): raise ValueError(f"`char_offsets`: {char_offsets} and `processed_tokens`: {processed_chars} have to be of the same length, but are: `len(offsets)`: {len(char_offsets)} and `len(processed_tokens)`: {len(processed_chars)}")
            for i, char in enumerate(processed_chars): char_offsets[i]["char"] = char
        string = " ".join(processed_chars).strip()
        return {"text": string, "char_offsets": char_offsets}
    @staticmethod
    def _compute_offsets(char_repetitions: List[int], chars: List[str], ctc_token: int, word_delimiter_token: Optional[int] = None) -> List[Dict[str, Union[str, int]]]:
        end_indices = np.asarray(char_repetitions).cumsum()
        start_indices = np.concatenate(([0], end_indices[:-1]))
        offsets = [{"char": t, "start_offset": s, "end_offset": e} for t, s, e in zip(chars, start_indices, end_indices)]
        offsets = list(filter(lambda offsets: offsets["char"] != ctc_token, offsets))
        if word_delimiter_token is not None: offsets = list(filter(lambda offsets: offsets["char"] != word_delimiter_token, offsets))
        return offsets
    def _decode(self, token_ids: List[int], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, group_tokens: bool = True, filter_word_delimiter_token: bool = True,
    spaces_between_special_tokens: bool = False, output_char_offsets: bool = False) -> str:
        filtered_tokens = self.convert_ids_to_tokens(token_ids, skip_special_tokens=skip_special_tokens)
        result = []
        for token in filtered_tokens:
            if skip_special_tokens and token in self.all_special_ids: continue
            result.append(token)
        string_output = self.convert_tokens_to_string(result, group_tokens=group_tokens, spaces_between_special_tokens=spaces_between_special_tokens,
        filter_word_delimiter_token=filter_word_delimiter_token, output_char_offsets=output_char_offsets)
        text = string_output["text"]
        clean_up_tokenization_spaces = (clean_up_tokenization_spaces if clean_up_tokenization_spaces is not None else self.clean_up_tokenization_spaces)
        if clean_up_tokenization_spaces: text = self.clean_up_tokenization(text)
        if output_char_offsets: return Wav2Vec2PhonemeCTCTokenizerOutput(text=text, char_offsets=string_output["char_offsets"])
        else: return text
    def decode(self, token_ids: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, output_char_offsets: bool = False, **kwargs) -> str:
        token_ids = to_py_obj(token_ids)
        return self._decode(token_ids=token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, output_char_offsets=output_char_offsets, **kwargs)
    def batch_decode(self, sequences: Union[List[int], List[List[int]], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, output_char_offsets: bool = False, **kwargs) -> List[str]:
        batch_decoded = [self.decode(seq, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, output_char_offsets=output_char_offsets, **kwargs) for seq in sequences]
        if output_char_offsets: return Wav2Vec2PhonemeCTCTokenizerOutput({k: [d[k] for d in batch_decoded] for k in batch_decoded[0]})
        return batch_decoded
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
