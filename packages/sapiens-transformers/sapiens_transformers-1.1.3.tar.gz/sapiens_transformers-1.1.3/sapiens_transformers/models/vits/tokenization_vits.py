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
from typing import Any, Dict, List, Optional, Tuple, Union
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import is_phonemizer_available, is_uroman_available, logging
if is_phonemizer_available(): import phonemizer
if is_uroman_available(): import uroman as ur
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json"}
def has_non_roman_characters(input_string):
    non_roman_pattern = re.compile(r"[^\x00-\x7F]")
    match = non_roman_pattern.search(input_string)
    has_non_roman = match is not None
    return has_non_roman
class VitsTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, pad_token="<pad>", unk_token="<unk>", language=None, add_blank=True, normalize=True, phonemize=True, is_uroman=False, **kwargs) -> None:
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.language = language
        self.add_blank = add_blank
        self.normalize = normalize
        self.phonemize = phonemize
        self.is_uroman = is_uroman
        super().__init__(pad_token=pad_token, unk_token=unk_token, language=language, add_blank=add_blank, normalize=normalize, phonemize=phonemize, is_uroman=is_uroman, **kwargs)
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def normalize_text(self, input_string):
        all_vocabulary = list(self.encoder.keys()) + list(self.added_tokens_encoder.keys())
        filtered_text = ""
        i = 0
        while i < len(input_string):
            found_match = False
            for word in all_vocabulary:
                if input_string[i : i + len(word)] == word:
                    filtered_text += word
                    i += len(word)
                    found_match = True
                    break
            if not found_match:
                filtered_text += input_string[i].lower()
                i += 1
        return filtered_text
    def _preprocess_char(self, text):
        if self.language == "ron": text = text.replace("ț", "ţ")
        return text
    def prepare_for_tokenization(self, text: str, is_split_into_words: bool = False, normalize: Optional[bool] = None, **kwargs) -> Tuple[str, Dict[str, Any]]:
        normalize = normalize if normalize is not None else self.normalize
        if normalize: text = self.normalize_text(text)
        filtered_text = self._preprocess_char(text)
        if has_non_roman_characters(filtered_text) and self.is_uroman:
            if not is_uroman_available(): logger.warning("Text to the tokenizer contains non-Roman characters. To apply the `uroman` pre-processing step automatically, ensure the `uroman` Romanizer is installed with: `pip install uroman` Note `uroman` requires python version >= 3.10 Otherwise, apply the Romanizer manually as per the instructions: https://github.com/isi-nlp/uroman")
            else:
                uroman = ur.Uroman()
                filtered_text = uroman.romanize_string(filtered_text)
        if self.phonemize:
            if not is_phonemizer_available(): raise ImportError("Please install the `phonemizer` Python package to use this tokenizer.")
            filtered_text = phonemizer.phonemize(filtered_text, language="en-us", backend="espeak", strip=True, preserve_punctuation=True, with_stress=True)
            filtered_text = re.sub(r"\s+", " ", filtered_text)
        elif normalize: filtered_text = "".join(list(filter(lambda char: char in self.encoder, filtered_text))).strip()
        return filtered_text, kwargs
    def _tokenize(self, text: str) -> List[str]:
        tokens = list(text)
        if self.add_blank:
            interspersed = [self._convert_id_to_token(0)] * (len(tokens) * 2 + 1)
            interspersed[1::2] = tokens
            tokens = interspersed
        return tokens
    def convert_tokens_to_string(self, tokens: List[str]) -> str:
        if self.add_blank and len(tokens) > 1: tokens = tokens[1::2]
        return "".join(tokens)
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Union[Tuple[str], None]:
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
