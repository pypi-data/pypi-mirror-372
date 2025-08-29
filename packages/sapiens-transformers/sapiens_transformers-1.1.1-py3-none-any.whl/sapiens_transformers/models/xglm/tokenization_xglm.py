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
logger = logging.get_logger(__name__)
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "sentencepiece.bpe.model"}
class XGLMTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, bos_token="<s>", eos_token="</s>", sep_token="</s>", cls_token="<s>", unk_token="<unk>", pad_token="<pad>", sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.num_madeup_words = 7
        madeup_words = [f"<madeupword{i}>" for i in range(self.num_madeup_words)]
        kwargs["additional_special_tokens"] = kwargs.get("additional_special_tokens", []) or []
        kwargs["additional_special_tokens"] += [word for word in madeup_words if word not in kwargs["additional_special_tokens"]]
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(str(vocab_file))
        self.vocab_file = vocab_file
        self.fairseq_offset = 1
        self.fairseq_tokens_to_ids = {"<s>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3}
        sp_size = len(self.sp_model)
        madeup_words = {f"<madeupword{i}>": sp_size + i + self.fairseq_offset for i in range(self.num_madeup_words)}
        self.fairseq_tokens_to_ids.update(madeup_words)
        self.fairseq_ids_to_tokens = {v: k for k, v in self.fairseq_tokens_to_ids.items()}
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, sep_token=sep_token, cls_token=cls_token, pad_token=pad_token, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
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
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.sep_token_id] + token_ids_0
        sep = [self.sep_token_id]
        return sep + token_ids_0 + sep + sep + token_ids_1
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + ([0] * len(token_ids_0))
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1))
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        if token_ids_1 is None: return len(sep + token_ids_0) * [0]
        return len(sep + token_ids_0 + sep + sep + token_ids_1) * [0]
    @property
    def vocab_size(self): return len(self.sp_model) + self.fairseq_offset + self.num_madeup_words
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text: str) -> List[str]: return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token):
        if token in self.fairseq_tokens_to_ids: return self.fairseq_tokens_to_ids[token]
        spm_id = self.sp_model.PieceToId(token)
        return spm_id + self.fairseq_offset if spm_id else self.unk_token_id
    def _convert_id_to_token(self, index):
        if index in self.fairseq_ids_to_tokens: return self.fairseq_ids_to_tokens[index]
        return self.sp_model.IdToPiece(index - self.fairseq_offset)
    def convert_tokens_to_string(self, tokens):
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
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
