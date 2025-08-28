"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import html
import os
import re
from shutil import copyfile
from typing import List, Optional, Tuple
import regex
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.txt', 'merges_file': 'bpe.codes'}
def get_pairs(word):
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    pairs = set(pairs)
    return pairs
class BertweetTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    def __init__(self, vocab_file, merges_file, normalization=False, bos_token="<s>", eos_token="</s>", sep_token="</s>",
    cls_token="<s>", unk_token="<unk>", pad_token="<pad>", mask_token="<mask>", **kwargs):
        try:
            from emoji import demojize
            self.demojizer = demojize
        except ImportError:
            logger.warning("emoji is not installed, thus not converting emoticons or emojis into text. Install emoji: pip3 install emoji==0.6.0")
            self.demojizer = None
        self.vocab_file = vocab_file
        self.merges_file = merges_file
        self.encoder = {}
        self.encoder[str(bos_token)] = 0
        self.encoder[str(pad_token)] = 1
        self.encoder[str(eos_token)] = 2
        self.encoder[str(unk_token)] = 3
        self.add_from_file(vocab_file)
        self.decoder = {v: k for k, v in self.encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: merges = merges_handle.read().split("\n")[:-1]
        merges = [tuple(merge.split()[:-1]) for merge in merges]
        self.bpe_ranks = dict(zip(merges, range(len(merges))))
        self.cache = {}
        self.normalization = normalization
        self.tweetPreprocessor = TweetTokenizer()
        self.special_puncts = {"’": "'", "…": "..."}
        super().__init__(normalization=normalization, bos_token=bos_token, eos_token=eos_token, sep_token=sep_token, cls_token=cls_token, unk_token=unk_token, pad_token=pad_token, mask_token=mask_token, **kwargs)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + sep + token_ids_1 + sep
    def get_special_tokens_mask(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens: return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        if token_ids_1 is None: return [1] + ([0] * len(token_ids_0)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)) + [1]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def bpe(self, token):
        if token in self.cache: return self.cache[token]
        word = tuple(token)
        word = tuple(list(word[:-1]) + [word[-1] + "</w>"])
        pairs = get_pairs(word)
        if not pairs: return token
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
        word = "@@ ".join(word)
        word = word[:-4]
        self.cache[token] = word
        return word
    def _tokenize(self, text):
        if self.normalization: text = self.normalizeTweet(text)
        split_tokens = []
        words = re.findall(r"\S+\n?", text)
        for token in words: split_tokens.extend(list(self.bpe(token).split(" ")))
        return split_tokens
    def normalizeTweet(self, tweet):
        for punct in self.special_puncts: tweet = tweet.replace(punct, self.special_puncts[punct])
        tokens = self.tweetPreprocessor.tokenize(tweet)
        normTweet = " ".join([self.normalizeToken(token) for token in tokens])
        normTweet = (normTweet.replace("cannot ", "can not ").replace("n't ", " n't ").replace("n 't ", " n't ").replace("ca n't", "can't").replace("ai n't", "ain't"))
        normTweet = (normTweet.replace("'m ", " 'm ").replace("'re ", " 're ").replace("'s ", " 's ").replace("'ll ", " 'll ").replace("'d ", " 'd ").replace("'ve ", " 've "))
        normTweet = (normTweet.replace(" p . m .", "  p.m.").replace(" p . m ", " p.m ").replace(" a . m .", " a.m.").replace(" a . m ", " a.m "))
        return " ".join(normTweet.split())
    def normalizeToken(self, token):
        lowercased_token = token.lower()
        if token.startswith("@"): return "@USER"
        elif lowercased_token.startswith("http") or lowercased_token.startswith("www"): return "HTTPURL"
        elif len(token) == 1:
            if token in self.special_puncts: return self.special_puncts[token]
            if self.demojizer is not None: return self.demojizer(token)
            else: return token
        else: return token
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index, self.unk_token)
    def convert_tokens_to_string(self, tokens):
        out_string = " ".join(tokens).replace("@@ ", "").strip()
        return out_string
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        out_merge_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file) and os.path.isfile(self.vocab_file): copyfile(self.vocab_file, out_vocab_file)
        elif not os.path.isfile(self.vocab_file):
            with open(out_vocab_file, "wb") as fi:
                content_spiece_model = self.sp_model.serialized_model_proto()
                fi.write(content_spiece_model)
        if os.path.abspath(self.merges_file) != os.path.abspath(out_merge_file): copyfile(self.merges_file, out_merge_file)
        return out_vocab_file, out_merge_file
    def add_from_file(self, f):
        if isinstance(f, str):
            try:
                with open(f, "r", encoding="utf-8") as fd: self.add_from_file(fd)
            except FileNotFoundError as fnfe: raise fnfe
            except UnicodeError: raise Exception(f"Incorrect encoding detected in {f}, please rebuild the dataset")
            return
        lines = f.readlines()
        for lineTmp in lines:
            line = lineTmp.strip()
            idx = line.rfind(" ")
            if idx == -1: raise ValueError("Incorrect dictionary format, expected '<token> <cnt>'")
            word = line[:idx]
            self.encoder[word] = len(self.encoder)
EMOTICONS = r"""
    (?:
      [<>]?
      [:;=8]
      [\-o\*\']?
      [\)\]\(\[dDpP/\:\}\{@\|\\]
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\]
      [\-o\*\']?
      [:;=8]
      [<>]?
      |
      <3
    )"""
URLS = r"""
  (?:
  https?:
    (?:
      /{1,3}
      |
      [a-z0-9%]
    )
    |
    [a-z0-9.\-]+[.]
    (?:[a-z]{2,13})
    /
  )
  (?:
    [^\s()<>{}\[\]]+
    |
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\)
    |
    \([^\s]+?\)
  )+
  (?:
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\)
    |
    \([^\s]+?\)
    |
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]
  )
  |
  (?:
    (?<!@)
    [a-z0-9]+
    (?:[.\-][a-z0-9]+)*
    [.]
    (?:[a-z]{2,13})
    \b
    /?
    (?!@)
  )
"""
REGEXPS = (URLS,
    r"""
    (?:
      (?:
        \+?[01]
        [ *\-.\)]*
      )?
      (?:
        [\(]?
        \d{3}
        [ *\-.\)]*
      )?
      \d{3}
      [ *\-.\)]*
      \d{4}
    )""", EMOTICONS,
    r"""<[^>\s]+>""",
    r"""[\-]+>|<[\-]+""",
    r"""(?:@[\w_]+)""",
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)""",
    r"""[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]""",
    r"""
    (?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_])
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)
    |
    (?:[\w_]+)
    |
    (?:\.(?:\s*\.){1,})
    |
    (?:\S)
    """)
WORD_RE = regex.compile(r"""(%s)""" % "|".join(REGEXPS), regex.VERBOSE | regex.I | regex.UNICODE)
HANG_RE = regex.compile(r"([^a-zA-Z0-9])\1{3,}")
EMOTICON_RE = regex.compile(EMOTICONS, regex.VERBOSE | regex.I | regex.UNICODE)
ENT_RE = regex.compile(r"&(#?(x?))([^&;\s]+);")
def _str_to_unicode(text, encoding=None, errors="strict"):
    if encoding is None: encoding = "utf-8"
    if isinstance(text, bytes): return text.decode(encoding, errors)
    return text
def _replace_html_entities(text, keep=(), remove_illegal=True, encoding="utf-8"):
    def _convert_entity(match):
        entity_body = match.group(3)
        if match.group(1):
            try:
                if match.group(2): number = int(entity_body, 16)
                else: number = int(entity_body, 10)
                if 0x80 <= number <= 0x9F: return bytes((number,)).decode("cp1252")
            except ValueError: number = None
        else:
            if entity_body in keep: return match.group(0)
            else: number = html.entities.name2codepoint.get(entity_body)
        if number is not None:
            try: return chr(number)
            except (ValueError, OverflowError): pass
        return "" if remove_illegal else match.group(0)
    return ENT_RE.sub(_convert_entity, _str_to_unicode(text, encoding))
class TweetTokenizer:
    def __init__(self, preserve_case=True, reduce_len=False, strip_handles=False):
        self.preserve_case = preserve_case
        self.reduce_len = reduce_len
        self.strip_handles = strip_handles
    def tokenize(self, text):
        text = _replace_html_entities(text)
        if self.strip_handles: text = remove_handles(text)
        if self.reduce_len: text = reduce_lengthening(text)
        safe_text = HANG_RE.sub(r"\1\1\1", text)
        words = WORD_RE.findall(safe_text)
        if not self.preserve_case: words = [x if EMOTICON_RE.search(x) else x.lower() for x in words]
        return words
def reduce_lengthening(text):
    pattern = regex.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1\1", text)
def remove_handles(text):
    pattern = regex.compile(r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)")
    return pattern.sub(" ", text)
def casual_tokenize(text, preserve_case=True, reduce_len=False, strip_handles=False): return TweetTokenizer(preserve_case=preserve_case, reduce_len=reduce_len, strip_handles=strip_handles).tokenize(text)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
