"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import io
import os
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
import sentencepiece as spm
from ....tokenization_utils import PreTrainedTokenizer
from ....utils import logging
logger = logging.get_logger(__name__)
SPIECE_UNDERLINE = "▁"
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt", "sentencepiece_model_ckpt": "sentencepiece.bpe.model"}
RESOURCE_FILES_NAMES = {'sentencepiece_model_file': 'sentencepiece.bpe.model', 'vocab_file': 'vocab.txt'}
class ErnieMTokenizer(PreTrainedTokenizer):
    model_input_names: List[str] = ["input_ids"]
    vocab_files_names = VOCAB_FILES_NAMES
    resource_files_names = RESOURCE_FILES_NAMES
    def __init__(self, sentencepiece_model_ckpt, vocab_file=None, do_lower_case=False, encoding="utf8", unk_token="[UNK]", sep_token="[SEP]", pad_token="[PAD]",
    cls_token="[CLS]", mask_token="[MASK]", sp_model_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self.sp_model_kwargs = {} if sp_model_kwargs is None else sp_model_kwargs
        self.do_lower_case = do_lower_case
        self.sentencepiece_model_ckpt = sentencepiece_model_ckpt
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(sentencepiece_model_ckpt)
        if vocab_file is not None: self.vocab = self.load_vocab(filepath=vocab_file)
        else: self.vocab = {self.sp_model.id_to_piece(id): id for id in range(self.sp_model.get_piece_size())}
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        super().__init__(do_lower_case=do_lower_case, unk_token=unk_token, sep_token=sep_token, pad_token=pad_token, cls_token=cls_token, mask_token=mask_token, vocab_file=vocab_file,
        encoding=encoding, sp_model_kwargs=self.sp_model_kwargs, **kwargs)
    def get_offset_mapping(self, text):
        if text is None: return None
        split_tokens = self.tokenize(text)
        normalized_text, char_mapping = "", []
        for i, ch in enumerate(text):
            if ch in self.SP_CHAR_MAPPING: ch = self.SP_CHAR_MAPPING.get(ch)
            else: ch = unicodedata.normalize("NFKC", ch)
            if self.is_whitespace(ch): continue
            normalized_text += ch
            char_mapping.extend([i] * len(ch))
        text, token_mapping, offset = normalized_text, [], 0
        if self.do_lower_case: text = text.lower()
        for token in split_tokens:
            if token[:1] == "▁": token = token[1:]
            start = text[offset:].index(token) + offset
            end = start + len(token)
            token_mapping.append((char_mapping[start], char_mapping[end - 1] + 1))
            offset = end
        return token_mapping
    @property
    def vocab_size(self): return len(self.vocab)
    def get_vocab(self): return dict(self.vocab, **self.added_tokens_encoder)
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        if not hasattr(self, "sp_model_kwargs"): self.sp_model_kwargs = {}
        self.sp_model = spm.SentencePieceProcessor(**self.sp_model_kwargs)
        self.sp_model.Load(self.sentencepiece_model_ckpt)
    def clean_text(self, text): return "".join((self.SP_CHAR_MAPPING.get(c, c) for c in text))
    def _tokenize(self, text, enable_sampling=False, nbest_size=64, alpha=0.1):
        if self.sp_model_kwargs.get("enable_sampling") is True: enable_sampling = True
        if self.sp_model_kwargs.get("alpha") is not None: alpha = self.sp_model_kwargs.get("alpha")
        if self.sp_model_kwargs.get("nbest_size") is not None: nbest_size = self.sp_model_kwargs.get("nbest_size")
        if not enable_sampling: pieces = self.sp_model.EncodeAsPieces(text)
        else: pieces = self.sp_model.SampleEncodeAsPieces(text, nbest_size, alpha)
        new_pieces = []
        for pi, piece in enumerate(pieces):
            if piece == SPIECE_UNDERLINE:
                if not pieces[pi + 1].startswith(SPIECE_UNDERLINE) and pi != 0:
                    new_pieces.append(SPIECE_UNDERLINE)
                    continue
                else: continue
            lst_i = 0
            for i, chunk in enumerate(piece):
                if chunk == SPIECE_UNDERLINE: continue
                if self.is_ch_char(chunk) or self.is_punct(chunk):
                    if i > lst_i and piece[lst_i:i] != SPIECE_UNDERLINE: new_pieces.append(piece[lst_i:i])
                    new_pieces.append(chunk)
                    lst_i = i + 1
                elif chunk.isdigit() and i > 0 and not piece[i - 1].isdigit():
                    if i > lst_i and piece[lst_i:i] != SPIECE_UNDERLINE: new_pieces.append(piece[lst_i:i])
                    lst_i = i
                elif not chunk.isdigit() and i > 0 and piece[i - 1].isdigit():
                    if i > lst_i and piece[lst_i:i] != SPIECE_UNDERLINE: new_pieces.append(piece[lst_i:i])
                    lst_i = i
            if len(piece) > lst_i: new_pieces.append(piece[lst_i:])
        return new_pieces
    def convert_tokens_to_string(self, tokens):
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string
    def convert_ids_to_string(self, ids):
        tokens = self.convert_ids_to_tokens(ids)
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string
    def _convert_token_to_id(self, token): return self.vocab.get(token, self.vocab.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.reverse_vocab.get(index, self.unk_token)
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        _cls = [self.cls_token_id]
        _sep = [self.sep_token_id]
        return _cls + token_ids_0 + _sep + _sep + token_ids_1 + _sep
    def build_offset_mapping_with_special_tokens(self, offset_mapping_0, offset_mapping_1=None):
        if offset_mapping_1 is None: return [(0, 0)] + offset_mapping_0 + [(0, 0)]
        return [(0, 0)] + offset_mapping_0 + [(0, 0), (0, 0)] + offset_mapping_1 + [(0, 0)]
    def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
        if already_has_special_tokens:
            if token_ids_1 is not None: raise ValueError("You should not supply a second sequence if the provided sequence of ids is already formatted with special tokens for the model.")
            return [1 if x in [self.sep_token_id, self.cls_token_id] else 0 for x in token_ids_0]
        if token_ids_1 is not None: return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return (len(token_ids_0) + 2) * [0]
        return [0] * (len(token_ids_0) + 1) + [1] * (len(token_ids_1) + 3)
    def is_ch_char(self, char):
        if "\u4e00" <= char <= "\u9fff": return True
        return False
    def is_alpha(self, char):
        if ("a" <= char <= "z") or ("A" <= char <= "Z"): return True
        return False
    def is_punct(self, char):
        if char in ",;:.?!~，；：。？！《》【】": return True
        return False
    def is_whitespace(self, char):
        if char == " " or char == "\t" or char == "\n" or char == "\r": return True
        if len(char) == 1:
            cat = unicodedata.category(char)
            if cat == "Zs": return True
        return False
    def load_vocab(self, filepath):
        token_to_idx = {}
        with io.open(filepath, "r", encoding="utf-8") as f:
            for index, line in enumerate(f):
                token = line.rstrip("\n")
                token_to_idx[token] = int(index)
        return token_to_idx
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        index = 0
        if os.path.isdir(save_directory): vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        else: vocab_file = (filename_prefix + "-" if filename_prefix else "") + save_directory
        with open(vocab_file, "w", encoding="utf-8") as writer:
            for token, token_index in sorted(self.vocab.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {vocab_file}: vocabulary indices are not consecutive. Please check that the vocabulary is not corrupted!")
                    index = token_index
                writer.write(token + "\n")
                index += 1
        tokenizer_model_file = os.path.join(save_directory, "sentencepiece.bpe.model")
        with open(tokenizer_model_file, "wb") as fi:
            content_spiece_model = self.sp_model.serialized_model_proto()
            fi.write(content_spiece_model)
        return (vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
