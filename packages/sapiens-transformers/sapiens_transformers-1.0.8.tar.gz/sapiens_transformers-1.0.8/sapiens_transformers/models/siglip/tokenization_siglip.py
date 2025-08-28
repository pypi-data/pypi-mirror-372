"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import re
import string
import warnings
from shutil import copyfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...convert_slow_tokenizer import import_protobuf
from ...tokenization_utils import PreTrainedTokenizer
from ...tokenization_utils_base import AddedToken
if TYPE_CHECKING: from ...tokenization_utils_base import TextInput
from ...utils import logging, requires_backends
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model"}
SPIECE_UNDERLINE = "▁"
class SiglipTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, eos_token="</s>", unk_token="<unk>", pad_token="</s>", additional_special_tokens=None, sp_model_kwargs: Optional[Dict[str, Any]] = None,
    model_max_length=64, do_lower_case=True, **kwargs) -> None:
        requires_backends(self, "protobuf")
        pad_token = (AddedToken(pad_token, rstrip=True, lstrip=True, normalized=False, special=True) if isinstance(pad_token, str) else pad_token)
        unk_token = (AddedToken(unk_token, rstrip=True, lstrip=True, normalized=False, special=True) if isinstance(unk_token, str) else unk_token)
        eos_token = (AddedToken(eos_token, rstrip=True, lstrip=True, normalized=False, special=True) if isinstance(eos_token, str) else eos_token)
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.do_lower_case = do_lower_case
        self.vocab_file = vocab_file
        self.sp_model = self.get_spm_processor()
        self.vocab_file = vocab_file
        super().__init__(eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, additional_special_tokens=additional_special_tokens, sp_model_kwargs=self.sp_model_kwargs,
        model_max_length=model_max_length, do_lower_case=do_lower_case, **kwargs)
    def get_spm_processor(self):
        tokenizer = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        with open(self.vocab_file, "rb") as f:
            sp_model = f.read()
            model_pb2 = import_protobuf()
            model = model_pb2.ModelProto.FromString(sp_model)
            normalizer_spec = model_pb2.NormalizerSpec()
            normalizer_spec.add_dummy_prefix = False
            model.normalizer_spec.MergeFrom(normalizer_spec)
            sp_model = model.SerializeToString()
            tokenizer.LoadFromSerializedProto(sp_model)
        return tokenizer
    @property
    def vocab_size(self): return self.sp_model.get_piece_size()
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return ([0] * len(token_ids_0)) + [1]
        return ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
    def _add_eos_if_not_present(self, token_ids: List[int]) -> List[int]:
        if len(token_ids) > 0 and token_ids[-1] == self.eos_token_id:
            warnings.warn(f"This sequence already has {self.eos_token}. In future versions this behavior may lead to duplicated eos tokens being added.")
            return token_ids
        else: return token_ids + [self.eos_token_id]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        eos = [self.eos_token_id]
        if token_ids_1 is None: return len(token_ids_0 + eos) * [0]
        return len(token_ids_0 + eos + token_ids_1 + eos) * [0]
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        token_ids_0 = self._add_eos_if_not_present(token_ids_0)
        if token_ids_1 is None: return token_ids_0
        else:
            token_ids_1 = self._add_eos_if_not_present(token_ids_1)
            return token_ids_0 + token_ids_1
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(self.vocab_file)
    def remove_punctuation(self, text: str) -> str: return text.translate(str.maketrans("", "", string.punctuation))
    def canonicalize_text(self, text, *, keep_punctuation_exact_string=None):
        if keep_punctuation_exact_string: text = keep_punctuation_exact_string.join(self.remove_punctuation(part) for part in text.split(keep_punctuation_exact_string))
        else: text = self.remove_punctuation(text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text
    def tokenize(self, text: "TextInput", add_special_tokens=False, **kwargs) -> List[str]:
        tokens = super().tokenize(SPIECE_UNDERLINE + text.replace(SPIECE_UNDERLINE, " "), **kwargs)
        if len(tokens) > 1 and tokens[0] == SPIECE_UNDERLINE and tokens[1] in self.all_special_tokens: tokens = tokens[1:]
        return tokens
    @property
    def unk_token_length(self): return len(self.sp_model.encode(str(self.unk_token)))
    def _tokenize(self, text, **kwargs):
        text = self.canonicalize_text(text, keep_punctuation_exact_string=None)
        tokens = self.sp_model.encode(text, out_type=str)
        tokens = self.sp_model.encode(self.unk_token + text, out_type=str)
        return tokens[self.unk_token_length :] if len(tokens) >= self.unk_token_length else tokens
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
