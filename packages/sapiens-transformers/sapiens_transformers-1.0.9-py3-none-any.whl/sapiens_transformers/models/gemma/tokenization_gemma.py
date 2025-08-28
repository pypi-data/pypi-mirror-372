"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
if TYPE_CHECKING: pass
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "tokenizer.model"}
SPIECE_UNDERLINE = "▁"
class GemmaTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, unk_token="<unk>", bos_token="<bos>", eos_token="<eos>", pad_token="<pad>", sp_model_kwargs: Optional[Dict[str, Any]] = None,
    add_bos_token=True, add_eos_token=False, clean_up_tokenization_spaces=False, use_default_system_prompt=False, spaces_between_special_tokens=False, **kwargs):
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        bos_token = AddedToken(bos_token, normalized=False, special=True) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, normalized=False, special=True) if isinstance(eos_token, str) else eos_token
        unk_token = AddedToken(unk_token, normalized=False, special=True) if isinstance(unk_token, str) else unk_token
        pad_token = AddedToken(pad_token, normalized=False, special=True) if isinstance(pad_token, str) else pad_token
        self.vocab_file = vocab_file
        self.add_bos_token = add_bos_token
        self.add_eos_token = add_eos_token
        self.use_default_system_prompt = use_default_system_prompt
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(vocab_file)
        super().__init__(bos_token=bos_token, eos_token=eos_token, unk_token=unk_token, pad_token=pad_token, add_bos_token=add_bos_token, add_eos_token=add_eos_token,
        sp_model_kwargs=self.sp_model_kwargs, clean_up_tokenization_spaces=clean_up_tokenization_spaces, use_default_system_prompt=use_default_system_prompt,
        spaces_between_special_tokens=spaces_between_special_tokens, **kwargs)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        state["sp_model_proto"] = self.sp_model.serialized_model_proto()
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.LoadFromSerializedProto(self.sp_model_proto)
    @property
    def vocab_size(self): return self.sp_model.get_piece_size()
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text, **kwargs): return self.sp_model.encode(text, out_type=str)
    def _convert_token_to_id(self, token): return self.sp_model.piece_to_id(token)
    def _convert_id_to_token(self, index):
        token = self.sp_model.IdToPiece(index)
        return token
    def _decode(self, token_ids: List[int], skip_special_tokens: bool = False, spaces_between_special_tokens: bool = False, **kwargs) -> str:
        sub_texts = []
        current_sub_text = []
        for ids in token_ids:
            if skip_special_tokens and ids in self.all_special_ids: continue
            if ids in self._added_tokens_decoder:
                if current_sub_text: sub_texts.append(self.sp_model.decode(current_sub_text))
                sub_texts.append(self._added_tokens_decoder[ids].content)
                current_sub_text = []
            else: current_sub_text.append(ids)
        if current_sub_text: sub_texts.append(self.sp_model.decode(current_sub_text))
        if spaces_between_special_tokens: sub_texts = " ".join(sub_texts)
        else: sub_texts = "".join(sub_texts)
        return sub_texts.replace(SPIECE_UNDERLINE, " ")
    def convert_tokens_to_string(self, tokens):
        current_sub_tokens = []
        out_string = ""
        for token in tokens:
            if token in self._added_tokens_encoder:
                out_string += self.sp_model.decode(current_sub_tokens) + token
                current_sub_tokens = []
            else: current_sub_tokens.append(token)
        out_string += self.sp_model.decode(current_sub_tokens)
        return out_string
    def save_vocabulary(self, save_directory, filename_prefix: Optional[str] = None) -> Tuple[str]:
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
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        bos_token_id = [self.bos_token_id] if self.add_bos_token else []
        eos_token_id = [self.eos_token_id] if self.add_eos_token else []
        output = bos_token_id + token_ids_0 + eos_token_id
        if token_ids_1 is not None: output = output + bos_token_id + token_ids_1 + eos_token_id
        return output
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        bos_token_id = [1] if self.add_bos_token else []
        eos_token_id = [1] if self.add_eos_token else []
        if token_ids_1 is None: return bos_token_id + ([0] * len(token_ids_0)) + eos_token_id
        return (bos_token_id + ([0] * len(token_ids_0)) + eos_token_id + bos_token_id + ([0] * len(token_ids_1)) + eos_token_id)
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        bos_token_id = [self.bos_token_id] if self.add_bos_token else []
        eos_token_id = [self.eos_token_id] if self.add_eos_token else []
        output = [0] * len(bos_token_id + token_ids_0 + eos_token_id)
        if token_ids_1 is not None: output += [1] * len(bos_token_id + token_ids_1 + eos_token_id)
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
