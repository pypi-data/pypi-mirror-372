"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple, Union
import sentencepiece as spm
from ...convert_slow_tokenizer import import_protobuf
from ...tokenization_utils import (BatchEncoding, PreTokenizedInput, PreTrainedTokenizer, TextInput)
from ...tokenization_utils_base import AddedToken
from ...utils import PaddingStrategy, logging
logger = logging.get_logger(__name__)
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "sentencepiece.bpe.model"}
class SeamlessM4TTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    prefix_tokens: List[int] = []
    suffix_tokens: List[int] = []
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>", unk_token="<unk>", pad_token="<pad>", tokenizer_file=None,
    src_lang="eng", tgt_lang="fra", sp_model_kwargs: Optional[Dict[str, Any]] = None, additional_special_tokens=None, add_prefix_space=True, **kwargs):
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.legacy = False
        self.vocab_file = vocab_file
        self.sp_model = self.get_spm_processor(kwargs.pop("from_slow", False))
        self._added_tokens_decoder = {0: AddedToken(pad_token, special=True) if isinstance(pad_token, str) else pad_token, 1: AddedToken(unk_token, special=True) if isinstance(unk_token, str) else unk_token,
        2: AddedToken(bos_token, special=True) if isinstance(bos_token, str) else bos_token, 3: AddedToken(eos_token, special=True) if isinstance(eos_token, str) else eos_token}
        self.fairseq_offset = 1
        self.sp_model_size = len(self.sp_model)
        self._src_lang = f"__{src_lang}__" if "__" not in src_lang else src_lang
        self._tgt_lang = f"__{tgt_lang}__" if "__" not in tgt_lang else tgt_lang
        self.add_prefix_space = add_prefix_space
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, tokenizer_file=tokenizer_file,
        src_lang=src_lang, tgt_lang=tgt_lang, additional_special_tokens=additional_special_tokens, sp_model_kwargs=self.sp_model_kwargs, add_prefix_space=add_prefix_space, **kwargs)
        self.set_src_lang_special_tokens(self._src_lang)
        self.set_tgt_lang_special_tokens(self._tgt_lang)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        state["sp_model_proto"] = self.sp_model.serialized_model_proto()
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.LoadFromSerializedProto(self.sp_model_proto)
    @property
    def vocab_size(self): return len(self.sp_model)
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    text_target: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, text_pair_target: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    padding: Union[bool, str, PaddingStrategy] = True, pad_to_multiple_of: Optional[int] = 2, src_lang: Optional[str] = None, tgt_lang: Optional[str] = None, **kwargs):
        if src_lang is not None: self.src_lang = src_lang
        if tgt_lang is not None: self.tgt_lang = tgt_lang
        output = super().__call__(text=text, text_pair=text_pair, text_target=text_target, text_pair_target=text_pair_target, padding=padding, pad_to_multiple_of=pad_to_multiple_of, **kwargs)
        return BatchEncoding(output, tensor_type=kwargs.get("return_tensors"))
    @property
    def src_lang(self) -> str: return self._src_lang
    @src_lang.setter
    def src_lang(self, new_src_lang: str) -> None:
        if "__" not in new_src_lang: self._src_lang = f"__{new_src_lang}__"
        else: self._src_lang = new_src_lang
        self.set_src_lang_special_tokens(self._src_lang)
    @property
    def tgt_lang(self) -> str: return self._tgt_lang
    @tgt_lang.setter
    def tgt_lang(self, new_tgt_lang: str) -> None:
        if "__" not in new_tgt_lang: self._tgt_lang = f"__{new_tgt_lang}__"
        else: self._tgt_lang = new_tgt_lang
        self.set_tgt_lang_special_tokens(self._tgt_lang)
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        prefix_ones = [1] * len(self.prefix_tokens)
        suffix_ones = [1] * len(self.suffix_tokens)
        if token_ids_1 is None: return prefix_ones + ([0] * len(token_ids_0)) + suffix_ones
        return prefix_ones + ([0] * len(token_ids_0)) + ([0] * len(token_ids_1)) + suffix_ones
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return self.prefix_tokens + token_ids_0 + self.suffix_tokens
        return self.prefix_tokens + token_ids_0 + token_ids_1 + self.suffix_tokens
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def _build_translation_inputs(self, raw_inputs, return_tensors: str, src_lang: Optional[str], tgt_lang: Optional[str], **extra_kwargs):
        if src_lang is None or tgt_lang is None: raise ValueError("Translation requires a `src_lang` and a `tgt_lang` for this model.")
        self.src_lang = src_lang
        inputs = self(raw_inputs, add_special_tokens=True, return_tensors=return_tensors, **extra_kwargs)
        if "__" not in tgt_lang: tgt_lang = f"__{tgt_lang}__"
        tgt_lang_id = self.convert_tokens_to_ids(tgt_lang)
        inputs["forced_bos_token_id"] = tgt_lang_id
        return inputs
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.fairseq_offset, self.vocab_size + self.fairseq_offset)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    @property
    def unk_token_length(self): return len(self.sp_model.encode(str(self.unk_token)))
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
    def tokenize(self, text: "TextInput", **kwargs) -> List[str]:
        if self.legacy or len(text) == 0: return super().tokenize(text, **kwargs)
        text = text.replace(SPIECE_UNDERLINE, " ")
        if self.add_prefix_space: text = SPIECE_UNDERLINE + text
        tokens = super().tokenize(text, **kwargs)
        if len(tokens) > 1 and tokens[0] == SPIECE_UNDERLINE and tokens[1] in self.all_special_tokens: tokens = tokens[1:]
        return tokens
    def _tokenize(self, text, **kwargs):
        if self.legacy or not text.startswith((SPIECE_UNDERLINE, " ")): return self.sp_model.encode(text, out_type=str)
        tokens = self.sp_model.encode(self.unk_token + text, out_type=str)
        return tokens[self.unk_token_length :] if len(tokens) >= self.unk_token_length else tokens
    def _convert_token_to_id(self, token):
        spm_id = self.sp_model.PieceToId(token)
        return spm_id + self.fairseq_offset if spm_id else self.unk_token_id
    def _convert_id_to_token(self, index): return self.sp_model.IdToPiece(index - self.fairseq_offset)
    def convert_tokens_to_string(self, tokens):
        if tokens[0].startswith(SPIECE_UNDERLINE) and self.add_prefix_space: tokens[0] = tokens[0][1:]
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string
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
    def prepare_seq2seq_batch(self, src_texts: List[str], src_lang: str = "eng", tgt_texts: Optional[List[str]] = None, tgt_lang: str = "fra", **kwargs) -> BatchEncoding:
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        return super().prepare_seq2seq_batch(src_texts, tgt_texts, **kwargs)
    def _switch_to_input_mode(self): return self.set_src_lang_special_tokens(self.src_lang)
    def _switch_to_target_mode(self): return self.set_tgt_lang_special_tokens(self.tgt_lang)
    def set_src_lang_special_tokens(self, src_lang) -> None:
        self.cur_lang_code = self.convert_tokens_to_ids(src_lang)
        self.init_kwargs["src_lang"] = src_lang
        if self.cur_lang_code == self.unk_token_id: logger.warning_once(f"`src_lang={src_lang}` has not be found in the vocabulary. Behaviour will probably be unexpected because the language token id will be replaced by the unknown token id.")
        self.prefix_tokens = [self.cur_lang_code]
        self.suffix_tokens = [self.eos_token_id]
    def set_tgt_lang_special_tokens(self, lang: str) -> None:
        self.cur_lang_code = self.convert_tokens_to_ids(lang)
        self.init_kwargs["tgt_lang"] = lang
        if self.cur_lang_code == self.unk_token_id: logger.warning_once(f"`tgt_lang={lang}` has not be found in the vocabulary. Behaviour will probably be unexpected because the language token id will be replaced by the unknown token id.")
        self.prefix_tokens = [self.eos_token_id, self.cur_lang_code]
        self.suffix_tokens = [self.eos_token_id]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
