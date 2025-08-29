"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections
import json
import os
import re
from typing import List, Optional, Tuple, Union
import numpy as np
from ....tokenization_utils import PreTrainedTokenizer
from ....tokenization_utils_base import (BatchEncoding, PreTokenizedInput, PreTokenizedInputPair, TextInput, TextInputPair, TruncationStrategy)
from ....utils import PaddingStrategy, logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt", "emoji_file": "emoji.json"}
def load_vocab_and_emoji(vocab_file, emoji_file):
    with open(emoji_file, "r", encoding="utf-8") as f: emoji = json.loads(f.read())
    vocab = collections.OrderedDict()
    raw_vocab = collections.OrderedDict()
    ids_to_tokens = collections.OrderedDict()
    with open(vocab_file, "r", encoding="utf-8") as f: token = f.readlines()
    token = [[t.rstrip("\n")] if (t == ",\n" or "," not in t) else t.rstrip("\n").split(",") for t in token]
    for idx, b in enumerate(token):
        ids_to_tokens[idx] = b
        raw_vocab[",".join(b)] = idx
        for wd in b: vocab[wd] = idx
    return vocab, raw_vocab, ids_to_tokens, emoji
class GPTSanJapaneseTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask", "token_type_ids"]
    def __init__(self, vocab_file, emoji_file, unk_token="<|nottoken|>", pad_token="<|separator|>", bos_token="<|startoftext|>", eos_token="<|endoftext|>",
    sep_token="<|segmenter|>", do_clean_text=False, **kwargs):
        if not os.path.isfile(vocab_file): raise ValueError(f"Can't find a vocabulary file at path '{vocab_file}'. To load the vocabulary from a Google pretrained model use `tokenizer = GPTSanJapaneseTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`")
        if not os.path.isfile(emoji_file): raise ValueError(f"Can't find a emoji file at path '{emoji_file}'. To load the emoji information from a Google pretrained model use `tokenizer = GPTSanJapaneseTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`")
        self.do_clean_text = do_clean_text
        self.vocab, self.raw_vocab, self.ids_to_tokens, self.emoji = load_vocab_and_emoji(vocab_file, emoji_file)
        self.subword_tokenizer = SubWordJapaneseTokenizer(vocab=self.vocab, ids_to_tokens=self.ids_to_tokens, emoji=self.emoji)
        super().__init__(unk_token=unk_token, pad_token=pad_token, bos_token=bos_token, eos_token=eos_token, sep_token=sep_token, do_clean_text=do_clean_text, **kwargs)
    @property
    def vocab_size(self): return len(self.raw_vocab)
    def get_vocab(self): return dict(self.raw_vocab, **self.added_tokens_encoder)
    def _tokenize(self, text): return self.subword_tokenizer.tokenize(text, clean=self.do_clean_text)
    def _convert_token_to_id(self, token): return self.vocab.get(token, self.vocab.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.subword_tokenizer.convert_id_to_token(index)
    def convert_tokens_to_string(self, tokens):
        words = []
        byte_tokens = []
        for word in tokens:
            if word[:6] == "<|byte" and word[-2:] == "|>": byte_tokens.append(int(word[6:-2]))
            else:
                if len(byte_tokens) > 0:
                    words.append(bytearray(byte_tokens).decode("utf-8", errors="replace"))
                    byte_tokens = []
                if word[:7] == "<|emoji" and word[-2:] == "|>": words.append(self.emoji["emoji_inv"][word])
                elif word == "<SP>": words.append(" ")
                elif word == "<BR>": words.append("\n")
                elif word == "<TAB>": words.append("\t")
                elif word == "<BLOCK>": words.append("▀")
                elif word == "<KIGOU>": words.append("ǀ")
                elif word == "<U2000U2BFF>": words.append("‖")
                elif word == "<|bagoftoken|>":
                    if len(words) > 0:
                        words.append(words[-1])
                        words.append(words[-1])
                        words.append(words[-1])
                elif word.startswith("<|") and word.endswith("|>"): words.append("")
                else: words.append(word)
        if len(byte_tokens) > 0: words.append(bytearray(byte_tokens).decode("utf-8", errors="replace"))
        text = "".join(words)
        return text
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        index = 0
        if os.path.isdir(save_directory):
            vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
            emoji_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["emoji_file"])
        else:
            vocab_file = ((filename_prefix + "-" if filename_prefix else "") + save_directory + VOCAB_FILES_NAMES["vocab_file"])
            emoji_file = ((filename_prefix + "-" if filename_prefix else "") + save_directory + VOCAB_FILES_NAMES["emoji_file"])
        with open(vocab_file, "w", encoding="utf-8") as writer:
            for token_index, token in self.ids_to_tokens.items():
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {vocab_file}: vocabulary indices are not consecutive. Please check that the vocabulary is not corrupted!")
                    index = token_index
                writer.write(",".join(token) + "\n")
                index += 1
        with open(emoji_file, "w", encoding="utf-8") as writer: json.dump(self.emoji, writer)
        return vocab_file, emoji_file
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        prefix_len = 0
        if self.sep_token in self.vocab:
            segid = self.vocab[self.sep_token]
            if segid in token_ids_0: prefix_len = token_ids_0.index(segid)
        if token_ids_1 is None: total_len = len(token_ids_0)
        else: total_len = len(token_ids_0 + token_ids_1)
        return prefix_len * [1] + (total_len - prefix_len) * [0]
    def prepare_for_tokenization(self, text, prefix_text=None, add_sep_token=None, **kwargs):
        if add_sep_token is None: add_sep_token = self.sep_token not in text
        prepared = self.bos_token if self.bos_token in self.vocab else ""
        prepared += prefix_text if prefix_text is not None else ""
        if add_sep_token: prepared += self.sep_token if self.sep_token in self.vocab else ""
        prepared += text
        return (prepared, kwargs)
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair]], add_special_tokens: bool = True,
    padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None,
    stride: int = 0, is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, return_tensors: Optional[str] = None, return_token_type_ids: Optional[bool] = None,
    return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False,
    return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        if isinstance(batch_text_or_text_pairs[0], tuple) or isinstance(tuple(batch_text_or_text_pairs[0]), list):
            batch_prefix_texts = []
            for pref, txt in batch_text_or_text_pairs: batch_prefix_texts.append(pref + self.sep_token + txt)
            batch_text_or_text_pairs = batch_prefix_texts
        return super()._batch_encode_plus(batch_text_or_text_pairs, add_special_tokens, padding_strategy, truncation_strategy, max_length, stride, is_split_into_words,
        pad_to_multiple_of, return_tensors, return_token_type_ids, return_attention_mask, return_overflowing_tokens, return_special_tokens_mask, return_offsets_mapping,
        return_length, verbose, **kwargs)
class SubWordJapaneseTokenizer:
    def __init__(self, vocab, ids_to_tokens, emoji):
        self.vocab = vocab
        self.ids_to_tokens = ids_to_tokens
        self.emoji = emoji
        self.maxlen = np.max([len(w) for w in self.vocab.keys()])
        self.content_repatter1 = re.compile(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+$,%#]+)")
        self.content_repatter2 = re.compile(r"[A-Za-z0-9\._+]*@[\-_0-9A-Za-z]+(\.[A-Za-z]+)*")
        self.content_repatter3 = re.compile(r"[\(]{0,1}[0-9]{2,4}[\)\-\(]{0,1}[0-9]{2,4}[\)\-]{0,1}[0-9]{3,4}")
        self.content_repatter4 = re.compile(r"([12]\d{3}[/\-年])*(0?[1-9]|1[0-2])[/\-月]((0?[1-9]|[12][0-9]|3[01])日?)*(\d{1,2}|:|\d{1,2}時|\d{1,2}分|\(日\)|\(月\)|\(火\)|\(水\)|\(木\)|\(金\)|\(土\)|㈰|㈪|㈫|㈬|㈭|㈮|㈯)*")
        self.content_repatter5 = re.compile(r"(明治|大正|昭和|平成|令和|㍾|㍽|㍼|㍻|\u32ff)\d{1,2}年(0?[1-9]|1[0-2])月(0?[1-9]|[12][0-9]|3[01])日(\d{1,2}|:|\d{1,2}時|\d{1,2}分|\(日\)|\(月\)|\(火\)|\(水\)|\(木\)|\(金\)|\(土\)|㈰|㈪|㈫|㈬|㈭|㈮|㈯)*")
        self.content_repatter6 = re.compile(r"((0|[1-9]\d*|[1-9]\d{0,2}(,\d{3})+)*億)*((0|[1-9]\d*|[1-9]\d{0,2}(,\d{3})+)*万)*((0|[1-9]\d*|[1-9]\d{0,2}(,\d{3})+)*千)*(0|[1-9]\d*|[1-9]\d{0,2}(,\d{3})+)*(千円|万円|千万円|円|千ドル|万ドル|千万ドル|ドル|千ユーロ|万ユーロ|千万ユーロ|ユーロ)+(\(税込\)|\(税抜\)|\+tax)*")
        keisen = "─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿"
        blocks = "▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▏▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟"
        self.content_trans1 = str.maketrans({k: "<BLOCK>" for k in keisen + blocks})
    def __len__(self): return len(self.ids_to_tokens)
    def clean_text(self, content):
        content = self.content_repatter1.sub("<URL>", content)
        content = self.content_repatter2.sub("<EMAIL>", content)
        content = self.content_repatter3.sub("<TEL>", content)
        content = self.content_repatter4.sub("<DATE>", content)
        content = self.content_repatter5.sub("<DATE>", content)
        content = self.content_repatter6.sub("<PRICE>", content)
        content = content.translate(self.content_trans1)
        while "<BLOCK><BLOCK>" in content: content = content.replace("<BLOCK><BLOCK>", "<BLOCK>")
        return content
    def tokenize(self, text, clean=False):
        text = text.replace(" ", "<SP>")
        text = text.replace("　", "<SP>")
        text = text.replace("\r\n", "<BR>")
        text = text.replace("\n", "<BR>")
        text = text.replace("\r", "<BR>")
        text = text.replace("\t", "<TAB>")
        text = text.replace("—", "ー")
        text = text.replace("−", "ー")
        for k, v in self.emoji["emoji"].items():
            if k in text: text = text.replace(k, v)
        if clean: text = self.clean_text(text)
        def check_simbol(x):
            e = x.encode()
            if len(x) == 1 and len(e) == 2:
                c = (int(e[0]) << 8) + int(e[1])
                if ((c >= 0xC2A1 and c <= 0xC2BF) or (c >= 0xC780 and c <= 0xC783) or (c >= 0xCAB9 and c <= 0xCBBF) or (c >= 0xCC80 and c <= 0xCDA2)): return True
            return False
        def checku2e(x):
            e = x.encode()
            if len(x) == 1 and len(e) == 3:
                c = (int(e[0]) << 16) + (int(e[1]) << 8) + int(e[2])
                if c >= 0xE28080 and c <= 0xE2B07F: return True
            return False
        pos = 0
        result = []
        while pos < len(text):
            end = min(len(text), pos + self.maxlen + 1) if text[pos] == "<" else pos + 3
            candidates = []
            for e in range(end, pos, -1):
                wd = text[pos:e]
                if wd in self.vocab:
                    if wd[0] == "<" and len(wd) > 2:
                        candidates = [(self.vocab[wd], wd, e)]
                        break
                    else: candidates.append((self.vocab[wd], wd, e))
            if len(candidates) > 0:
                _, wd, e = sorted(candidates, key=lambda x: x[0])[0]
                result.append(wd)
                pos = e
            else:
                end = pos + 1
                wd = text[pos:end]
                if check_simbol(wd): result.append("<KIGOU>")
                elif checku2e(wd): result.append("<U2000U2BFF>")
                else:
                    for i in wd.encode("utf-8"): result.append("<|byte%d|>" % i)
                pos = end
        return result
    def convert_id_to_token(self, index): return self.ids_to_tokens[index][0]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
