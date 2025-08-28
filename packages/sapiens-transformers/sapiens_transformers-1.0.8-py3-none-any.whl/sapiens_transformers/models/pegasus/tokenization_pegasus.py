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
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "spiece.model"}
logger = logging.get_logger(__name__)
class PegasusTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, pad_token="<pad>", eos_token="</s>", unk_token="<unk>", mask_token="<mask_2>", mask_token_sent="<mask_1>", additional_special_tokens=None,
    offset=103, sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self.offset = offset
        if additional_special_tokens is not None:
            if not isinstance(additional_special_tokens, list): raise TypeError(f"additional_special_tokens should be of type {type(list)}, but is {type(additional_special_tokens)}")
            additional_special_tokens_extended = (([mask_token_sent] + additional_special_tokens) if mask_token_sent not in additional_special_tokens and mask_token_sent is not None else additional_special_tokens)
            additional_special_tokens_extended += [f"<unk_{i}>" for i in range(len(additional_special_tokens_extended), self.offset - 1)]
            if len(set(additional_special_tokens_extended)) != len(additional_special_tokens_extended): raise ValueError(f"Please make sure that the provided additional_special_tokens do not contain an incorrectly shifted list of <unk_x> tokens. Found {additional_special_tokens_extended}.")
            additional_special_tokens = additional_special_tokens_extended
        else:
            additional_special_tokens_extended = []
            additional_special_tokens = [mask_token_sent] if mask_token_sent is not None else []
            additional_special_tokens += [f"<unk_{i}>" for i in range(2, self.offset)]
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.mask_token_sent = mask_token_sent
        self.vocab_file = vocab_file
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(vocab_file)
        _added_tokens_decoder = {0: AddedToken(str(pad_token), special=True), 1: AddedToken(str(eos_token), special=True)}
        if self.mask_token_sent is not None:
            _added_tokens_decoder[2] = AddedToken(mask_token_sent, special=True)
            _added_tokens_decoder[3] = AddedToken(str(mask_token), special=True)
        for i in range(2, self.offset): _added_tokens_decoder[len(_added_tokens_decoder)] = AddedToken(f"<unk_{i}>", special=True)
        self._added_tokens_decoder = kwargs.pop("added_tokens_decoder", {})
        self._added_tokens_decoder.update(_added_tokens_decoder)
        super().__init__(eos_token=eos_token, unk_token=unk_token, mask_token=mask_token, pad_token=pad_token, mask_token_sent=mask_token_sent, offset=offset,
        additional_special_tokens=additional_special_tokens, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
    @property
    def vocab_size(self) -> int: return len(self.sp_model) + self.offset
    def get_vocab(self) -> Dict[str, int]:
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
    def _convert_token_to_id(self, token: str) -> int:
        sp_id = self.sp_model.piece_to_id(token)
        return sp_id + self.offset
    def _convert_id_to_token(self, index: int) -> str:
        if index < self.offset: return self.sp_model.IdToPiece(index)
        token = self.sp_model.IdToPiece(index - self.offset)
        return token
    def convert_tokens_to_string(self, tokens):
        current_sub_tokens = []
        out_string = ""
        for token in tokens:
            if token in self.all_special_tokens:
                out_string += self.sp_model.decode(current_sub_tokens) + token
                current_sub_tokens = []
            else: current_sub_tokens.append(token)
        out_string += self.sp_model.decode(current_sub_tokens)
        return out_string.strip()
    def num_special_tokens_to_add(self, pair=False): return 1
    def _special_token_mask(self, seq):
        all_special_ids = set(self.all_special_ids)
        all_special_ids.remove(self.unk_token_id)
        return [1 if x in all_special_ids else 0 for x in seq]
    def get_special_tokens_mask(self, token_ids_0: List, token_ids_1: Optional[List] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return self._special_token_mask(token_ids_0)
        elif token_ids_1 is None: return self._special_token_mask(token_ids_0) + [1]
        else: return self._special_token_mask(token_ids_0 + token_ids_1) + [1]
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None) -> List[int]:
        if token_ids_1 is None: return token_ids_0 + [self.eos_token_id]
        return token_ids_0 + token_ids_1 + [self.eos_token_id]
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
