"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import re
import warnings
from shutil import copyfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...convert_slow_tokenizer import import_protobuf
from ...tokenization_utils import PreTrainedTokenizer
from ...tokenization_utils_base import AddedToken
if TYPE_CHECKING: from ...tokenization_utils_base import TextInput
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model"}
SPIECE_UNDERLINE = "▁"
class T5Tokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, eos_token="</s>", unk_token="<unk>", pad_token="<pad>", extra_ids=100, additional_special_tokens=None, sp_model_kwargs: Optional[Dict[str, Any]] = None,
    legacy=None, add_prefix_space=True, **kwargs) -> None:
        pad_token = AddedToken(pad_token, special=True) if isinstance(pad_token, str) else pad_token
        unk_token = AddedToken(unk_token, special=True) if isinstance(unk_token, str) else unk_token
        eos_token = AddedToken(eos_token, special=True) if isinstance(eos_token, str) else eos_token
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.vocab_file = vocab_file
        self._extra_ids = extra_ids
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(vocab_file)
        if additional_special_tokens is not None:
            extra_tokens = [x for x in additional_special_tokens if "<extra_id_" in str(x)]
            if len(extra_tokens) < 1: additional_special_tokens += [f"<extra_id_{i}>" for i in range(extra_ids)]
            elif extra_ids > 0 and extra_ids != len(extra_tokens): raise ValueError(f"Both extra_ids ({extra_ids}) and additional_special_tokens ({additional_special_tokens}) are provided to T5Tokenizer. In this case the additional_special_tokens must include the extra_ids tokens")
        else:
            extra_tokens = [f"<extra_id_{i}>" for i in range(extra_ids)]
            additional_special_tokens = extra_tokens
        self._added_tokens_decoder = {}
        for i in range(len(extra_tokens)): self._added_tokens_decoder[len(self.sp_model) - 1 + extra_ids - i] = AddedToken(f"<extra_id_{i}>", single_word=False, lstrip=True, rstrip=True, special=True, normalized=False)
        if legacy is None:
            logger.warning_once(f"You are using the default legacy behaviour of the {self.__class__}. This is expected, and simply means that the `legacy` (previous) behavior will be used so nothing changes for you. If you want to use the new behaviour, set `legacy=False`. This should only be set if you understand what it means.")
            legacy = True
        self.legacy = legacy
        self.sp_model = self.get_spm_processor(kwargs.pop("from_slow", False))
        self.vocab_file = vocab_file
        self._extra_ids = extra_ids
        self.add_prefix_space = add_prefix_space
        super().__init__(eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, extra_ids=extra_ids, additional_special_tokens=additional_special_tokens,
        sp_model_kwargs=self.sp_model_kwargs, legacy=legacy, add_prefix_space=add_prefix_space, **kwargs)
    def get_spm_processor(self, from_slow=False):
        tokenizer = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        if self.legacy or from_slow:
            tokenizer.Load(self.vocab_file)
            return tokenizer
        with open(self.vocab_file, "rb") as f:
            sp_model = f.read()
            model_pb2 = import_protobuf(f"The new behaviour of {self.__class__.__name__} (with `self.legacy = False`)")
            model = model_pb2.ModelProto.FromString(sp_model)
            normalizer_spec = model_pb2.NormalizerSpec()
            normalizer_spec.add_dummy_prefix = False
            model.normalizer_spec.MergeFrom(normalizer_spec)
            sp_model = model.SerializeToString()
            tokenizer.LoadFromSerializedProto(sp_model)
        return tokenizer
    @staticmethod
    def _eventually_correct_t5_max_length(pretrained_model_name_or_path, max_model_length, init_max_model_length):
        if pretrained_model_name_or_path in T5Tokenizer.max_model_input_sizes:
            deprecated_max_model_length = T5Tokenizer.max_model_input_sizes[pretrained_model_name_or_path]
            if init_max_model_length is not None and init_max_model_length != max_model_length: return init_max_model_length
            elif init_max_model_length is None: warnings.warn(f"This tokenizer was incorrectly instantiated with a model max length of {deprecated_max_model_length} which will be corrected in Transformers v5.\nFor now, this behavior is kept to avoid breaking backwards compatibility when padding/encoding with `truncation is True`.\n- Be aware that you SHOULD NOT rely on {pretrained_model_name_or_path} automatically truncating your input to {deprecated_max_model_length} when padding/encoding.\n- If you want to encode/pad to sequences longer than {deprecated_max_model_length} you can either instantiate this tokenizer with `model_max_length` or pass `max_length` when encoding/padding.\n- To avoid this warning, please instantiate this tokenizer with `model_max_length` set to your preferred value.", FutureWarning)
        return max_model_length
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
    def get_sentinel_tokens(self): return list(set(filter(lambda x: bool(re.search(r"<extra_id_\d+>", x)) is not None, self.additional_special_tokens)))
    def get_sentinel_token_ids(self): return [self.convert_tokens_to_ids(token) for token in self.get_sentinel_tokens()]
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
    def tokenize(self, text: "TextInput", **kwargs) -> List[str]:
        if self.legacy or len(text) == 0: return super().tokenize(text, **kwargs)
        text = text.replace(SPIECE_UNDERLINE, " ")
        if self.add_prefix_space: text = SPIECE_UNDERLINE + text
        tokens = super().tokenize(text, **kwargs)
        if len(tokens) > 1 and tokens[0] == SPIECE_UNDERLINE and tokens[1] in self.all_special_tokens: tokens = tokens[1:]
        return tokens
    @property
    def unk_token_length(self): return len(self.sp_model.encode(str(self.unk_token)))
    def _tokenize(self, text, **kwargs):
        if self.legacy or not text.startswith((SPIECE_UNDERLINE, " ")): return self.sp_model.encode(text, out_type=str)
        tokens = self.sp_model.encode(self.unk_token + text, out_type=str)
        return tokens[self.unk_token_length :] if len(tokens) >= self.unk_token_length else tokens
    def _convert_token_to_id(self, token): return self.sp_model.piece_to_id(token)
    def _convert_id_to_token(self, index):
        token = self.sp_model.IdToPiece(index)
        return token
    def convert_tokens_to_string(self, tokens):
        if tokens[0].startswith(SPIECE_UNDERLINE) and self.add_prefix_space: tokens[0] = tokens[0][1:]
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
