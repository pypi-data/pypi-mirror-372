"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
import re
import unicodedata
from json.encoder import INFINITY
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import regex
from ....tokenization_utils import AddedToken, PreTrainedTokenizer
from ....tokenization_utils_base import BatchEncoding
from ....utils import TensorType, is_flax_available, is_tf_available, is_torch_available, logging
from ....utils.generic import _is_jax, _is_numpy
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'artists_file': 'artists.json', 'lyrics_file': 'lyrics.json', 'genres_file': 'genres.json'}
class JukeboxTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, artists_file, genres_file, lyrics_file, version=["v3", "v2", "v2"], max_n_lyric_tokens=512, n_genres=5, unk_token="<|endoftext|>", **kwargs):
        unk_token = AddedToken(unk_token, lstrip=False, rstrip=False) if isinstance(unk_token, str) else unk_token
        self.version = version
        self.max_n_lyric_tokens = max_n_lyric_tokens
        self.n_genres = n_genres
        self._added_tokens_decoder = {0: unk_token}
        with open(artists_file, encoding="utf-8") as vocab_handle: self.artists_encoder = json.load(vocab_handle)
        with open(genres_file, encoding="utf-8") as vocab_handle: self.genres_encoder = json.load(vocab_handle)
        with open(lyrics_file, encoding="utf-8") as vocab_handle: self.lyrics_encoder = json.load(vocab_handle)
        oov = r"[^A-Za-z0-9.,:;!?\-'\"()\[\] \t\n]+"
        if len(self.lyrics_encoder) == 79: oov = oov.replace(r"\-'", r"\-+'")
        self.out_of_vocab = regex.compile(oov)
        self.artists_decoder = {v: k for k, v in self.artists_encoder.items()}
        self.genres_decoder = {v: k for k, v in self.genres_encoder.items()}
        self.lyrics_decoder = {v: k for k, v in self.lyrics_encoder.items()}
        super().__init__(unk_token=unk_token, n_genres=n_genres, version=version, max_n_lyric_tokens=max_n_lyric_tokens, **kwargs)
    @property
    def vocab_size(self): return len(self.artists_encoder) + len(self.genres_encoder) + len(self.lyrics_encoder)
    def get_vocab(self): return {"artists_encoder": self.artists_encoder, "genres_encoder": self.genres_encoder, "lyrics_encoder": self.lyrics_encoder}
    def _convert_token_to_id(self, list_artists, list_genres, list_lyrics):
        artists_id = [self.artists_encoder.get(artist, 0) for artist in list_artists]
        for genres in range(len(list_genres)):
            list_genres[genres] = [self.genres_encoder.get(genre, 0) for genre in list_genres[genres]]
            list_genres[genres] = list_genres[genres] + [-1] * (self.n_genres - len(list_genres[genres]))
        lyric_ids = [[self.lyrics_encoder.get(character, 0) for character in list_lyrics[0]], [], []]
        return artists_id, list_genres, lyric_ids
    def _tokenize(self, lyrics): return list(lyrics)
    def tokenize(self, artist, genre, lyrics, **kwargs):
        artist, genre, lyrics = self.prepare_for_tokenization(artist, genre, lyrics)
        lyrics = self._tokenize(lyrics)
        return artist, genre, lyrics
    def prepare_for_tokenization(self, artists: str, genres: str, lyrics: str, is_split_into_words: bool = False) -> Tuple[str, str, str, Dict[str, Any]]:
        for idx in range(len(self.version)):
            if self.version[idx] == "v3":
                artists[idx] = artists[idx].lower()
                genres[idx] = [genres[idx].lower()]
            else:
                artists[idx] = self._normalize(artists[idx]) + ".v2"
                genres[idx] = [self._normalize(genre) + ".v2" for genre in genres[idx].split("_")]
        if self.version[0] == "v2":
            self.out_of_vocab = regex.compile(r"[^A-Za-z0-9.,:;!?\-'\"()\[\] \t\n]+")
            vocab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?-+'\"()[] \t\n"
            self.vocab = {vocab[index]: index + 1 for index in range(len(vocab))}
            self.vocab["<unk>"] = 0
            self.n_vocab = len(vocab) + 1
            self.lyrics_encoder = self.vocab
            self.lyrics_decoder = {v: k for k, v in self.vocab.items()}
            self.lyrics_decoder[0] = ""
        else: self.out_of_vocab = regex.compile(r"[^A-Za-z0-9.,:;!?\-+'\"()\[\] \t\n]+")
        lyrics = self._run_strip_accents(lyrics)
        lyrics = lyrics.replace("\\", "\n")
        lyrics = self.out_of_vocab.sub("", lyrics), [], []
        return artists, genres, lyrics
    def _run_strip_accents(self, text):
        text = unicodedata.normalize("NFD", text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == "Mn": continue
            output.append(char)
        return "".join(output)
    def _normalize(self, text: str) -> str:
        accepted = ([chr(i) for i in range(ord("a"), ord("z") + 1)] + [chr(i) for i in range(ord("A"), ord("Z") + 1)] + [chr(i) for i in range(ord("0"), ord("9") + 1)] + ["."])
        accepted = frozenset(accepted)
        pattern = re.compile(r"_+")
        text = "".join([c if c in accepted else "_" for c in text.lower()])
        text = pattern.sub("_", text).strip("_")
        return text
    def convert_lyric_tokens_to_string(self, lyrics: List[str]) -> str: return " ".join(lyrics)
    def convert_to_tensors(self, inputs, tensor_type: Optional[Union[str, TensorType]] = None, prepend_batch_axis: bool = False):
        if not isinstance(tensor_type, TensorType): tensor_type = TensorType(tensor_type)
        if tensor_type == TensorType.TENSORFLOW:
            if not is_tf_available(): raise ImportError("Unable to convert output to TensorFlow tensors format, TensorFlow is not installed.")
            import tensorflow as tf
            as_tensor = tf.constant
            is_tensor = tf.is_tensor
        elif tensor_type == TensorType.PYTORCH:
            if not is_torch_available(): raise ImportError("Unable to convert output to PyTorch tensors format, PyTorch is not installed.")
            import torch
            as_tensor = torch.tensor
            is_tensor = torch.is_tensor
        elif tensor_type == TensorType.JAX:
            if not is_flax_available(): raise ImportError("Unable to convert output to JAX tensors format, JAX is not installed.")
            import jax.numpy as jnp
            as_tensor = jnp.array
            is_tensor = _is_jax
        else:
            as_tensor = np.asarray
            is_tensor = _is_numpy
        try:
            if prepend_batch_axis: inputs = [inputs]
            if not is_tensor(inputs): inputs = as_tensor(inputs)
        except: raise ValueError("Unable to create tensor, you should probably activate truncation and/or padding with 'padding=True' 'truncation=True' to have batched tensors with the same length.")
        return inputs
    def __call__(self, artist, genres, lyrics="", return_tensors="pt") -> BatchEncoding:
        input_ids = [0, 0, 0]
        artist = [artist] * len(self.version)
        genres = [genres] * len(self.version)
        artists_tokens, genres_tokens, lyrics_tokens = self.tokenize(artist, genres, lyrics)
        artists_id, genres_ids, full_tokens = self._convert_token_to_id(artists_tokens, genres_tokens, lyrics_tokens)
        attention_masks = [-INFINITY] * len(full_tokens[-1])
        input_ids = [self.convert_to_tensors([input_ids + [artists_id[i]] + genres_ids[i] + full_tokens[i]], tensor_type=return_tensors) for i in range(len(self.version))]
        return BatchEncoding({"input_ids": input_ids, "attention_masks": attention_masks})
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        artists_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["artists_file"])
        with open(artists_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.artists_encoder, ensure_ascii=False))
        genres_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["genres_file"])
        with open(genres_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.genres_encoder, ensure_ascii=False))
        lyrics_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["lyrics_file"])
        with open(lyrics_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.lyrics_encoder, ensure_ascii=False))
        return (artists_file, genres_file, lyrics_file)
    def _convert_id_to_token(self, artists_index, genres_index, lyric_index):
        artist = self.artists_decoder.get(artists_index)
        genres = [self.genres_decoder.get(genre) for genre in genres_index]
        lyrics = [self.lyrics_decoder.get(character) for character in lyric_index]
        return artist, genres, lyrics
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
