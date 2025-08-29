"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import List, Optional, Tuple, Union
from tokenizers import processors
from ...tokenization_utils import (BatchEncoding, PreTokenizedInput, TextInput)
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import PaddingStrategy, is_sentencepiece_available, logging
if is_sentencepiece_available(): from .tokenization_seamless_m4t import SeamlessM4TTokenizer
else: SeamlessM4TTokenizer = None
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "sentencepiece.bpe.model", "tokenizer_file": "tokenizer.json"}
class SeamlessM4TTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = SeamlessM4TTokenizer
    model_input_names = ["input_ids", "attention_mask"]
    prefix_tokens: List[int] = []
    suffix_tokens: List[int] = []
    def __init__(self, vocab_file=None, tokenizer_file=None, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>", unk_token="<unk>", pad_token="<pad>",
    src_lang="eng", tgt_lang="fra", additional_special_tokens=None, **kwargs):
        super().__init__(vocab_file=vocab_file, tokenizer_file=tokenizer_file, bos_token=bos_token, eos_token=eos_token, sep_token=sep_token, cls_token=cls_token,
        unk_token=unk_token, pad_token=pad_token, src_lang=src_lang, tgt_lang=tgt_lang, additional_special_tokens=additional_special_tokens, **kwargs)
        self.vocab_file = vocab_file
        self._src_lang = f"__{src_lang}__" if "__" not in src_lang else src_lang
        self._tgt_lang = f"__{tgt_lang}__" if "__" not in tgt_lang else tgt_lang
        self.set_src_lang_special_tokens(self._src_lang)
        self.set_tgt_lang_special_tokens(self._tgt_lang)
    @property
    def can_save_slow_tokenizer(self) -> bool: return os.path.isfile(self.vocab_file) if self.vocab_file else False
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
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return self.prefix_tokens + token_ids_0 + self.suffix_tokens
        return self.prefix_tokens + token_ids_0 + token_ids_1 + self.suffix_tokens
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    def _build_translation_inputs(self, raw_inputs, return_tensors: str, src_lang: Optional[str], tgt_lang: Optional[str], **extra_kwargs):
        if src_lang is None or tgt_lang is None: raise ValueError("Translation requires a `src_lang` and a `tgt_lang` for this model")
        self.src_lang = src_lang
        inputs = self(raw_inputs, add_special_tokens=True, return_tensors=return_tensors, **extra_kwargs)
        if "__" not in tgt_lang: tgt_lang = f"__{tgt_lang}__"
        tgt_lang_id = self.convert_tokens_to_ids(tgt_lang)
        inputs["forced_bos_token_id"] = tgt_lang_id
        return inputs
    def prepare_seq2seq_batch(self, src_texts: List[str], src_lang: str = "eng", tgt_texts: Optional[List[str]] = None, tgt_lang: str = "fra", **kwargs) -> BatchEncoding:
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        return super().prepare_seq2seq_batch(src_texts, tgt_texts, **kwargs)
    def _switch_to_input_mode(self): return self.set_src_lang_special_tokens(self.src_lang)
    def _switch_to_target_mode(self): return self.set_tgt_lang_special_tokens(self.tgt_lang)
    def set_src_lang_special_tokens(self, src_lang) -> None:
        self.cur_lang_code = self.convert_tokens_to_ids(src_lang)
        if self.cur_lang_code == self.unk_token_id: logger.warning_once(f"`tgt_lang={src_lang}` has not be found in the `vocabulary`. Behaviour will probably be unexpected because the language token id will be replaced by the unknown token id.")
        self.init_kwargs["src_lang"] = src_lang
        self.prefix_tokens = [self.cur_lang_code]
        self.suffix_tokens = [self.eos_token_id]
        prefix_tokens_str = self.convert_ids_to_tokens(self.prefix_tokens)
        suffix_tokens_str = self.convert_ids_to_tokens(self.suffix_tokens)
        self._tokenizer.post_processor = processors.TemplateProcessing(single=prefix_tokens_str + ["$A"] + suffix_tokens_str, pair=prefix_tokens_str + ["$A", "$B"] + suffix_tokens_str,
        special_tokens=list(zip(prefix_tokens_str + suffix_tokens_str, self.prefix_tokens + self.suffix_tokens)))
    def set_tgt_lang_special_tokens(self, lang: str) -> None:
        self.cur_lang_code = self.convert_tokens_to_ids(lang)
        if self.cur_lang_code == self.unk_token_id: logger.warning_once(f"`tgt_lang={lang}` has not be found in the `vocabulary`. Behaviour will probably be unexpected because the language token id will be replaced by the unknown token id.")
        self.init_kwargs["tgt_lang"] = lang
        self.prefix_tokens = [self.eos_token_id, self.cur_lang_code]
        self.suffix_tokens = [self.eos_token_id]
        prefix_tokens_str = self.convert_ids_to_tokens(self.prefix_tokens)
        suffix_tokens_str = self.convert_ids_to_tokens(self.suffix_tokens)
        self._tokenizer.post_processor = processors.TemplateProcessing(single=prefix_tokens_str + ["$A"] + suffix_tokens_str, pair=prefix_tokens_str + ["$A", "$B"] + suffix_tokens_str,
        special_tokens=list(zip(prefix_tokens_str + suffix_tokens_str, self.prefix_tokens + self.suffix_tokens)))
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not self.can_save_slow_tokenizer: raise ValueError("Your fast tokenizer does not have the necessary information to save the vocabulary for a slow tokenizer.")
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory.")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file): copyfile(self.vocab_file, out_vocab_file)
        return (out_vocab_file,)
    @classmethod
    def _from_pretrained(cls, resolved_vocab_files, pretrained_model_name_or_path, init_configuration, *init_inputs, token=None, cache_dir=None, local_files_only=False,
    _commit_hash=None, _is_local=False, **kwargs):
        tokenizer = super()._from_pretrained(resolved_vocab_files, pretrained_model_name_or_path, init_configuration, *init_inputs, token=token, cache_dir=cache_dir,
        local_files_only=local_files_only, _commit_hash=_commit_hash, _is_local=_is_local, **kwargs)
        tokenizer.set_src_lang_special_tokens(tokenizer._src_lang)
        tokenizer.set_tgt_lang_special_tokens(tokenizer._tgt_lang)
        return tokenizer
    def __call__(self, text: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    text_target: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]] = None, text_pair_target: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]] = None,
    padding: Union[bool, str, PaddingStrategy] = True, pad_to_multiple_of: Optional[int] = 2, src_lang: Optional[str] = None, tgt_lang: Optional[str] = None, **kwargs):
        if src_lang is not None: self.src_lang = src_lang
        if tgt_lang is not None: self.tgt_lang = tgt_lang
        output = super().__call__(text=text, text_pair=text_pair, text_target=text_target, text_pair_target=text_pair_target, padding=padding, pad_to_multiple_of=pad_to_multiple_of, **kwargs)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
