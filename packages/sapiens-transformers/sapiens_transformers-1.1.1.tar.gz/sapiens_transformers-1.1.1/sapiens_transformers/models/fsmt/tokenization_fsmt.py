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
from typing import Dict, List, Optional, Tuple
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'src_vocab_file': 'vocab-src.json', 'tgt_vocab_file': 'vocab-tgt.json', 'merges_file': 'merges.txt'}
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
class FSMTTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, langs=None, src_vocab_file=None, tgt_vocab_file=None, merges_file=None, do_lower_case=False, unk_token="<unk>", bos_token="<s>", sep_token="</s>", pad_token="<pad>", **kwargs):
        try: import sacremoses
        except ImportError: raise ImportError("You need to install sacremoses to use XLMTokenizer. See https://pypi.org/project/sacremoses/ for installation.")
        self.sm = sacremoses
        self.src_vocab_file = src_vocab_file
        self.tgt_vocab_file = tgt_vocab_file
        self.merges_file = merges_file
        self.do_lower_case = do_lower_case
        self.cache_moses_punct_normalizer = {}
        self.cache_moses_tokenizer = {}
        self.cache_moses_detokenizer = {}
        if langs and len(langs) == 2: self.src_lang, self.tgt_lang = langs
        else: raise ValueError(f"arg `langs` needs to be a list of 2 langs, e.g. ['en', 'ru'], but got {langs}. Usually that means that tokenizer can't find a mapping for the given model path in  and other maps of this tokenizer.")
        with open(src_vocab_file, encoding="utf-8") as src_vocab_handle: self.encoder = json.load(src_vocab_handle)
        with open(tgt_vocab_file, encoding="utf-8") as tgt_vocab_handle:
            tgt_vocab = json.load(tgt_vocab_handle)
            self.decoder = {v: k for k, v in tgt_vocab.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: merges = merges_handle.read().split("\n")[:-1]
        merges = [tuple(merge.split()[:2]) for merge in merges]
        self.bpe_ranks = dict(zip(merges, range(len(merges))))
        self.cache = {}
        super().__init__(langs=langs, src_vocab_file=src_vocab_file, tgt_vocab_file=tgt_vocab_file, merges_file=merges_file, do_lower_case=do_lower_case, unk_token=unk_token,
        bos_token=bos_token, sep_token=sep_token, pad_token=pad_token, **kwargs)
    def get_vocab(self) -> Dict[str, int]: return self.get_src_vocab()
    @property
    def vocab_size(self) -> int: return self.src_vocab_size
    def moses_punct_norm(self, text, lang):
        if lang not in self.cache_moses_punct_normalizer:
            punct_normalizer = self.sm.MosesPunctNormalizer(lang=lang)
            self.cache_moses_punct_normalizer[lang] = punct_normalizer
        return self.cache_moses_punct_normalizer[lang].normalize(text)
    def moses_tokenize(self, text, lang):
        if lang not in self.cache_moses_tokenizer:
            moses_tokenizer = self.sm.MosesTokenizer(lang=lang)
            self.cache_moses_tokenizer[lang] = moses_tokenizer
        return self.cache_moses_tokenizer[lang].tokenize(text, aggressive_dash_splits=True, return_str=False, escape=True)
    def moses_detokenize(self, tokens, lang):
        if lang not in self.cache_moses_detokenizer:
            moses_detokenizer = self.sm.MosesDetokenizer(lang=lang)
            self.cache_moses_detokenizer[lang] = moses_detokenizer
        return self.cache_moses_detokenizer[lang].detokenize(tokens)
    def moses_pipeline(self, text, lang):
        text = replace_unicode_punct(text)
        text = self.moses_punct_norm(text, lang)
        text = remove_non_printing_char(text)
        return text
    @property
    def src_vocab_size(self): return len(self.encoder)
    @property
    def tgt_vocab_size(self): return len(self.decoder)
    def get_src_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def get_tgt_vocab(self): return dict(self.decoder, **self.added_tokens_decoder)
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
    def _tokenize(self, text, lang="en", bypass_tokenizer=False):
        lang = self.src_lang
        if self.do_lower_case: text = text.lower()
        if bypass_tokenizer: text = text.split()
        else:
            text = self.moses_pipeline(text, lang=lang)
            text = self.moses_tokenize(text, lang=lang)
        split_tokens = []
        for token in text:
            if token: split_tokens.extend(list(self.bpe(token).split(" ")))
        return split_tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index, self.unk_token)
    def convert_tokens_to_string(self, tokens):
        tokens = [t.replace(" ", "").replace("</w>", " ") for t in tokens]
        tokens = "".join(tokens).split()
        text = self.moses_detokenize(tokens, self.tgt_lang)
        return text
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        if token_ids_1 is None: return token_ids_0 + sep
        return token_ids_0 + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is not None: return ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return ([0] * len(token_ids_0)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        if token_ids_1 is None: return len(token_ids_0 + sep) * [0]
        return len(token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        src_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["src_vocab_file"])
        tgt_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["tgt_vocab_file"])
        merges_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"])
        with open(src_vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.encoder, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        with open(tgt_vocab_file, "w", encoding="utf-8") as f:
            tgt_vocab = {v: k for k, v in self.decoder.items()}
            f.write(json.dumps(tgt_vocab, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        index = 0
        with open(merges_file, "w", encoding="utf-8") as writer:
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {merges_file}: BPE merge indices are not consecutive. Please check that the tokenizer is not corrupted!")
                    index = token_index
                writer.write(" ".join(bpe_tokens) + "\n")
                index += 1
        return src_vocab_file, tgt_vocab_file, merges_file
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
