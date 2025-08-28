"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
from .number_normalizer import EnglishNumberNormalizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "spm_char.model"}
class SpeechT5Tokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", unk_token="<unk>", pad_token="<pad>", normalize=False, sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.vocab_file = vocab_file
        self.normalize = normalize
        self._normalizer = None
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(vocab_file)
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, normalize=normalize, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        normalize = kwargs.pop("normalize", self.normalize)
        if is_split_into_words: text = " " + text
        if normalize: text = self.normalizer(text)
        return (text, kwargs)
    @property
    def vocab_size(self): return self.sp_model.get_piece_size()
    @property
    def normalizer(self):
        if self._normalizer is None: self._normalizer = EnglishNumberNormalizer()
        return self._normalizer
    @normalizer.setter
    def normalizer(self, value): self._normalizer = value
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(self.vocab_file)
    def _tokenize(self, text: str) -> List[str]: return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token): return self.sp_model.piece_to_id(token)
    def _convert_id_to_token(self, index):
        token = self.sp_model.IdToPiece(index)
        return token
    def convert_tokens_to_string(self, tokens):
        current_sub_tokens = []
        out_string = ""
        prev_is_special = False
        for token in tokens:
            if token in self.all_special_tokens:
                if not prev_is_special: out_string += " "
                out_string += self.sp_model.decode(current_sub_tokens) + token
                prev_is_special = True
                current_sub_tokens = []
            else:
                current_sub_tokens.append(token)
                prev_is_special = False
        out_string += self.sp_model.decode(current_sub_tokens)
        return out_string.strip()
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None) -> List[int]:
        if token_ids_1 is None: return token_ids_0 + [self.eos_token_id]
        return token_ids_0 + token_ids_1 + [self.eos_token_id]
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        suffix_ones = [1]
        if token_ids_1 is None: return ([0] * len(token_ids_0)) + suffix_ones
        return ([0] * len(token_ids_0)) + ([0] * len(token_ids_1)) + suffix_ones
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file) and os.path.isfile(self.vocab_file): copyfile(self.vocab_file, out_vocab_file)
        elif not os.path.isfile(self.vocab_file):
            with open(out_vocab_file, "wb") as fi:
                content_spiece_model = self.sp_model.serialized_model_proto()
                fi.write(content_spiece_model)
        return (out_vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
