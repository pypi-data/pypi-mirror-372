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
import unicodedata
from typing import List, Optional, Tuple
from ...tokenization_utils import PreTrainedTokenizer, _is_control, _is_punctuation, _is_whitespace
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'merges_file': 'merges.txt'}
def get_pairs(word):
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs
def replace_unicode_punct(text):
    text = text.replace("，", ",")
    text = re.sub(r"。\s*", ". ", text)
    text = text.replace("、", ",")
    text = text.replace("”", '"')
    text = text.replace("“", '"')
    text = text.replace("∶", ":")
    text = text.replace("：", ":")
    text = text.replace("？", "?")
    text = text.replace("《", '"')
    text = text.replace("》", '"')
    text = text.replace("）", ")")
    text = text.replace("！", "!")
    text = text.replace("（", "(")
    text = text.replace("；", ";")
    text = text.replace("１", "1")
    text = text.replace("」", '"')
    text = text.replace("「", '"')
    text = text.replace("０", "0")
    text = text.replace("３", "3")
    text = text.replace("２", "2")
    text = text.replace("５", "5")
    text = text.replace("６", "6")
    text = text.replace("９", "9")
    text = text.replace("７", "7")
    text = text.replace("８", "8")
    text = text.replace("４", "4")
    text = re.sub(r"．\s*", ". ", text)
    text = text.replace("～", "~")
    text = text.replace("’", "'")
    text = text.replace("…", "...")
    text = text.replace("━", "-")
    text = text.replace("〈", "<")
    text = text.replace("〉", ">")
    text = text.replace("【", "[")
    text = text.replace("】", "]")
    text = text.replace("％", "%")
    return text
def remove_non_printing_char(text):
    output = []
    for char in text:
        cat = unicodedata.category(char)
        if cat.startswith("C"): continue
        output.append(char)
    return "".join(output)
def whitespace_tokenize(text):
    text = text.strip()
    if not text: return []
    tokens = text.split()
    return tokens
class BasicTokenizer:
    def __init__(self, do_lower_case=True, never_split=None, tokenize_chinese_chars=True, strip_accents=None, do_split_on_punc=True):
        if never_split is None: never_split = []
        self.do_lower_case = do_lower_case
        self.never_split = set(never_split)
        self.tokenize_chinese_chars = tokenize_chinese_chars
        self.strip_accents = strip_accents
        self.do_split_on_punc = do_split_on_punc
    def tokenize(self, text, never_split=None):
        never_split = self.never_split.union(set(never_split)) if never_split else self.never_split
        text = self._clean_text(text)
        if self.tokenize_chinese_chars: text = self._tokenize_chinese_chars(text)
        unicode_normalized_text = unicodedata.normalize("NFC", text)
        orig_tokens = whitespace_tokenize(unicode_normalized_text)
        split_tokens = []
        for token in orig_tokens:
            if token not in never_split:
                if self.do_lower_case:
                    token = token.lower()
                    if self.strip_accents is not False: token = self._run_strip_accents(token)
                elif self.strip_accents: token = self._run_strip_accents(token)
            split_tokens.extend(self._run_split_on_punc(token, never_split))
        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        return output_tokens
    def _run_strip_accents(self, text):
        text = unicodedata.normalize("NFD", text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == "Mn": continue
            output.append(char)
        return "".join(output)
    def _run_split_on_punc(self, text, never_split=None):
        if not self.do_split_on_punc or (never_split is not None and text in never_split): return [text]
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                output.append([char])
                start_new_word = True
            else:
                if start_new_word: output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1
        return ["".join(x) for x in output]
    def _tokenize_chinese_chars(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if self._is_chinese_char(cp):
                output.append(" ")
                output.append(char)
                output.append(" ")
            else: output.append(char)
        return "".join(output)
    def _is_chinese_char(self, cp):
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or (cp >= 0x3400 and cp <= 0x4DBF) or (cp >= 0x20000 and cp <= 0x2A6DF) or (cp >= 0x2A700 and cp <= 0x2B73F)
        or (cp >= 0x2B740 and cp <= 0x2B81F) or (cp >= 0x2B820 and cp <= 0x2CEAF) or (cp >= 0xF900 and cp <= 0xFAFF) or (cp >= 0x2F800 and cp <= 0x2FA1F)): return True
        return False
    def _clean_text(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xFFFD or _is_control(char): continue
            if _is_whitespace(char): output.append(" ")
            else: output.append(char)
        return "".join(output)
class HerbertTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    def __init__(self, vocab_file, merges_file, tokenizer_file=None, cls_token="<s>", unk_token="<unk>", pad_token="<pad>", mask_token="<mask>", sep_token="</s>",
    bos_token="<s>", do_lowercase_and_remove_accent=False, additional_special_tokens=["<special0>", "<special1>", "<special2>", "<special3>", "<special4>", "<special5>",
    "<special6>", "<special7>", "<special8>", "<special9>"], lang2id=None, id2lang=None, **kwargs):
        try: import sacremoses
        except ImportError: raise ImportError("You need to install sacremoses to use HerbertTokenizer. See https://pypi.org/project/sacremoses/ for installation.")
        self.sm = sacremoses
        self.cache_moses_punct_normalizer = {}
        self.cache_moses_tokenizer = {}
        self.lang_with_custom_tokenizer = {"zh", "th", "ja"}
        self.do_lowercase_and_remove_accent = do_lowercase_and_remove_accent
        self.lang2id = lang2id
        self.id2lang = id2lang
        if lang2id is not None and id2lang is not None: assert len(lang2id) == len(id2lang)
        self.ja_word_tokenizer = None
        self.zh_word_tokenizer = None
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: merges = merges_handle.read().split("\n")[:-1]
        merges = [tuple(merge.split()[:2]) for merge in merges]
        self.bpe_ranks = dict(zip(merges, range(len(merges))))
        self.cache = {}
        super().__init__(unk_token=unk_token, bos_token=bos_token, sep_token=sep_token, pad_token=pad_token, cls_token=cls_token, mask_token=mask_token, additional_special_tokens=additional_special_tokens,
        lang2id=lang2id, id2lang=id2lang, do_lowercase_and_remove_accent=do_lowercase_and_remove_accent, tokenizer_file=None, **kwargs)
        self.bert_pre_tokenizer = BasicTokenizer(do_lower_case=False, never_split=self.all_special_tokens, tokenize_chinese_chars=False, strip_accents=False)
    @property
    def do_lower_case(self): return self.do_lowercase_and_remove_accent
    def moses_punct_norm(self, text, lang):
        if lang not in self.cache_moses_punct_normalizer:
            punct_normalizer = self.sm.MosesPunctNormalizer(lang=lang)
            self.cache_moses_punct_normalizer[lang] = punct_normalizer
        else: punct_normalizer = self.cache_moses_punct_normalizer[lang]
        return punct_normalizer.normalize(text)
    def moses_tokenize(self, text, lang):
        if lang not in self.cache_moses_tokenizer:
            moses_tokenizer = self.sm.MosesTokenizer(lang=lang)
            self.cache_moses_tokenizer[lang] = moses_tokenizer
        else: moses_tokenizer = self.cache_moses_tokenizer[lang]
        return moses_tokenizer.tokenize(text, return_str=False, escape=False)
    def moses_pipeline(self, text, lang):
        text = replace_unicode_punct(text)
        text = self.moses_punct_norm(text, lang)
        text = remove_non_printing_char(text)
        return text
    def ja_tokenize(self, text):
        if self.ja_word_tokenizer is None:
            try:
                import Mykytea
                self.ja_word_tokenizer = Mykytea.Mykytea(f"-model {os.path.expanduser('~')}/local/share/kytea/model.bin")
            except (AttributeError, ImportError):
                logger.error("Make sure you install KyTea (https://github.com/neubig/kytea) and it's python wrapper (https://github.com/chezou/Mykytea-python) with the following steps")
                logger.error("1. git clone git@github.com:neubig/kytea.git && cd kytea")
                logger.error("2. autoreconf -i")
                logger.error("3. ./configure --prefix=$HOME/local")
                logger.error("4. make && make install")
                logger.error("5. pip install kytea")
                raise
        return list(self.ja_word_tokenizer.getWS(text))
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def bpe(self, token):
        word = tuple(token[:-1]) + (token[-1] + "</w>",)
        if token in self.cache: return self.cache[token]
        pairs = get_pairs(word)
        if not pairs: return token + "</w>"
        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float("inf")))
            if bigram not in self.bpe_ranks: break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try: j = word.index(first, i)
                except ValueError:
                    new_word.extend(word[i:])
                    break
                else:
                    new_word.extend(word[i:j])
                    i = j
                if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1: break
            else: pairs = get_pairs(word)
        word = " ".join(word)
        if word == "\n  </w>": word = "\n</w>"
        self.cache[token] = word
        return word
    def _tokenize(self, text):
        pre_tokens = self.bert_pre_tokenizer.tokenize(text)
        split_tokens = []
        for token in pre_tokens:
            if token: split_tokens.extend(list(self.bpe(token).split(" ")))
        return split_tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index, self.unk_token)
    def convert_tokens_to_string(self, tokens):
        out_string = "".join(tokens).replace("</w>", " ").strip()
        return out_string
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        bos = [self.bos_token_id]
        sep = [self.sep_token_id]
        if token_ids_1 is None: return bos + token_ids_0 + sep
        return bos + token_ids_0 + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is not None: return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        merge_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.encoder, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        index = 0
        with open(merge_file, "w", encoding="utf-8") as writer:
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {merge_file}: BPE merge indices are not consecutive. Please check that the tokenizer is not corrupted!")
                    index = token_index
                writer.write(" ".join(bpe_tokens) + "\n")
                index += 1
        return vocab_file, merge_file
    def __getstate__(self):
        state = self.__dict__.copy()
        state["sm"] = None
        return state
    def __setstate__(self, d):
        self.__dict__ = d
        try: import sacremoses
        except ImportError: raise ImportError("You need to install sacremoses to use XLMTokenizer. See https://pypi.org/project/sacremoses/ for installation.")
        self.sm = sacremoses
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
