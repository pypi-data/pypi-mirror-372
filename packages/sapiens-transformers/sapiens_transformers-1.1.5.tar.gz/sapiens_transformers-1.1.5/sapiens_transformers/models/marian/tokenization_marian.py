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
import warnings
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple, Union
import sentencepiece
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'source_spm': 'source.spm', 'target_spm': 'target.spm', 'vocab': 'vocab.json', 'target_vocab_file': 'target_vocab.json', 'tokenizer_config_file': 'tokenizer_config.json'}
SPIECE_UNDERLINE = "▁"
class MarianTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    language_code_re = re.compile(">>.+<<")
    def __init__(self, source_spm, target_spm, vocab, target_vocab_file=None, source_lang=None, target_lang=None, unk_token="<unk>", eos_token="</s>", pad_token="<pad>",
    model_max_length=512, sp_model_kwargs: Optional[Dict[str, Any]] = None, separate_vocabs=False, **kwargs) -> None:
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        assert Path(source_spm).exists(), f"cannot find spm source {source_spm}"
        self.separate_vocabs = separate_vocabs
        self.encoder = load_json(vocab)
        if str(unk_token) not in self.encoder: raise KeyError("<unk> token must be in the vocab")
        assert str(pad_token) in self.encoder
        if separate_vocabs:
            self.target_encoder = load_json(target_vocab_file)
            self.decoder = {v: k for k, v in self.target_encoder.items()}
            self.supported_language_codes = []
        else:
            self.decoder = {v: k for k, v in self.encoder.items()}
            self.supported_language_codes: list = [k for k in self.encoder if k.startswith(">>") and k.endswith("<<")]
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.spm_files = [source_spm, target_spm]
        self.spm_source = load_spm(source_spm, self.sp_model_kwargs)
        self.spm_target = load_spm(target_spm, self.sp_model_kwargs)
        self.current_spm = self.spm_source
        self.current_encoder = self.encoder
        self._setup_normalizer()
        super().__init__(source_lang=source_lang, target_lang=target_lang, unk_token=unk_token, eos_token=eos_token, pad_token=pad_token, model_max_length=model_max_length,
        sp_model_kwargs=self.sp_model_kwargs, target_vocab_file=target_vocab_file, separate_vocabs=separate_vocabs, **kwargs)
    def _setup_normalizer(self):
        try:
            from sacremoses import MosesPunctNormalizer
            self.punc_normalizer = MosesPunctNormalizer(self.source_lang).normalize
        except (ImportError, FileNotFoundError):
            warnings.warn("Recommended: pip install sacremoses.")
            self.punc_normalizer = lambda x: x
    def normalize(self, x: str) -> str: return self.punc_normalizer(x) if x else ""
    def _convert_token_to_id(self, token): return self.current_encoder.get(token, self.current_encoder[self.unk_token])
    def remove_language_code(self, text: str):
        match = self.language_code_re.match(text)
        code: list = [match.group(0)] if match else []
        return code, self.language_code_re.sub("", text)
    def _tokenize(self, text: str) -> List[str]:
        code, text = self.remove_language_code(text)
        pieces = self.current_spm.encode(text, out_type=str)
        return code + pieces
    def _convert_id_to_token(self, index: int) -> str: return self.decoder.get(index, self.unk_token)
    def batch_decode(self, sequences, **kwargs): return super().batch_decode(sequences, **kwargs)
    def decode(self, token_ids, **kwargs): return super().decode(token_ids, **kwargs)
    def convert_tokens_to_string(self, tokens: List[str]) -> str:
        sp_model = self.spm_source if self._decode_use_source_tokenizer else self.spm_target
        current_sub_tokens = []
        out_string = ""
        for token in tokens:
            if token in self.all_special_tokens:
                out_string += sp_model.decode_pieces(current_sub_tokens) + token + " "
                current_sub_tokens = []
            else: current_sub_tokens.append(token)
        out_string += sp_model.decode_pieces(current_sub_tokens)
        out_string = out_string.replace(SPIECE_UNDERLINE, " ")
        return out_string.strip()
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None) -> List[int]:
        if token_ids_1 is None: return token_ids_0 + [self.eos_token_id]
        return token_ids_0 + token_ids_1 + [self.eos_token_id]
    def _switch_to_input_mode(self):
        self.current_spm = self.spm_source
        self.current_encoder = self.encoder
    def _switch_to_target_mode(self):
        self.current_spm = self.spm_target
        if self.separate_vocabs: self.current_encoder = self.target_encoder
    @property
    def vocab_size(self) -> int: return len(self.encoder)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        saved_files = []
        if self.separate_vocabs:
            out_src_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab"])
            out_tgt_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["target_vocab_file"])
            save_json(self.encoder, out_src_vocab_file)
            save_json(self.target_encoder, out_tgt_vocab_file)
            saved_files.append(out_src_vocab_file)
            saved_files.append(out_tgt_vocab_file)
        else:
            out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab"])
            save_json(self.encoder, out_vocab_file)
            saved_files.append(out_vocab_file)
        for spm_save_filename, spm_orig_path, spm_model in zip([VOCAB_FILES_NAMES["source_spm"], VOCAB_FILES_NAMES["target_spm"]], self.spm_files, [self.spm_source, self.spm_target]):
            spm_save_path = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + spm_save_filename)
            if os.path.abspath(spm_orig_path) != os.path.abspath(spm_save_path) and os.path.isfile(spm_orig_path):
                copyfile(spm_orig_path, spm_save_path)
                saved_files.append(spm_save_path)
            elif not os.path.isfile(spm_orig_path):
                with open(spm_save_path, "wb") as fi:
                    content_spiece_model = spm_model.serialized_model_proto()
                    fi.write(content_spiece_model)
                saved_files.append(spm_save_path)
        return tuple(saved_files)
    def get_vocab(self) -> Dict: return self.get_src_vocab()
    def get_src_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def get_tgt_vocab(self): return dict(self.target_encoder, **self.added_tokens_decoder)
    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        state.update({k: None for k in ["spm_source", "spm_target", "current_spm", "punc_normalizer", "target_vocab_file"]})
        return state
    def __setstate__(self, d: Dict) -> None:
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.spm_source, self.spm_target = (load_spm(f, self.sp_model_kwargs) for f in self.spm_files)
        self.current_spm = self.spm_source
        self._setup_normalizer()
    def num_special_tokens_to_add(self, *args, **kwargs): return 1
    def _special_token_mask(self, seq):
        all_special_ids = set(self.all_special_ids)
        all_special_ids.remove(self.unk_token_id)
        return [1 if x in all_special_ids else 0 for x in seq]
    def get_special_tokens_mask(self, token_ids_0: List, token_ids_1: Optional[List] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return self._special_token_mask(token_ids_0)
        elif token_ids_1 is None: return self._special_token_mask(token_ids_0) + [1]
        else: return self._special_token_mask(token_ids_0 + token_ids_1) + [1]
def load_spm(path: str, sp_model_kwargs: Dict[str, Any]) -> sentencepiece.SentencePieceProcessor:
    spm = sentencepiece.SentencePieceProcessor(**sp_model_kwargs)
    spm.Load(path)
    return spm
def save_json(data, path: str) -> None:
    with open(path, "w") as f: json.dump(data, f, indent=2)
def load_json(path: str) -> Union[Dict, List]:
    with open(path, "r") as f: return json.load(f)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
