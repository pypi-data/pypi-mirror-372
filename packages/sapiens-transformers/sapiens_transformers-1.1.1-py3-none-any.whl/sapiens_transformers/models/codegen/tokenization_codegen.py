"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from functools import lru_cache
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
import numpy as np
import regex as re
from ...utils import is_tf_available, is_torch_available, logging, to_py_obj
if TYPE_CHECKING:
    if is_torch_available(): import torch
    if is_tf_available(): import tensorflow as tf
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'merges_file': 'merges.txt'}
@lru_cache()
def bytes_to_unicode():
    bs = (list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1)))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))
def get_pairs(word):
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs
class CodeGenTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file, merges_file, errors="replace", unk_token="<|endoftext|>", bos_token="<|endoftext|>", eos_token="<|endoftext|>", pad_token=None, add_prefix_space=False,
    add_bos_token=False, return_token_type_ids=False, **kwargs):
        bos_token = AddedToken(bos_token, special=True) if isinstance(bos_token, str) else bos_token
        eos_token = AddedToken(eos_token, special=True) if isinstance(eos_token, str) else eos_token
        unk_token = AddedToken(unk_token, special=True) if isinstance(unk_token, str) else unk_token
        pad_token = AddedToken(pad_token, special=True) if isinstance(pad_token, str) else pad_token
        self.add_bos_token = add_bos_token
        self.return_token_type_ids = return_token_type_ids
        if self.return_token_type_ids: self.model_input_names.append("token_type_ids")
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.errors = errors
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle: bpe_merges = merges_handle.read().split("\n")[1:-1]
        bpe_merges = [tuple(merge.split()) for merge in bpe_merges]
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}
        self.add_prefix_space = add_prefix_space
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
        super().__init__(errors=errors, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token,
        add_prefix_space=add_prefix_space, add_bos_token=add_bos_token, return_token_type_ids=return_token_type_ids, **kwargs)
    @property
    def vocab_size(self): return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def bpe(self, token):
        if token in self.cache: return self.cache[token]
        word = tuple(token)
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
        word = " ".join(word)
        self.cache[token] = word
        return word
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        if self.add_bos_token: bos_token_ids = [self.bos_token_id]
        else: bos_token_ids = []
        output = bos_token_ids + token_ids_0
        if token_ids_1 is None: return output
        return output + bos_token_ids + token_ids_1
    def _tokenize(self, text):
        bpe_tokens = []
        for token in re.findall(self.pat, text):
            token = "".join(self.byte_encoder[b] for b in token.encode("utf-8"))
            bpe_tokens.extend(bpe_token for bpe_token in self.bpe(token).split(" "))
        return bpe_tokens
    def _convert_token_to_id(self, token): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index)
    def convert_tokens_to_string(self, tokens):
        text = "".join(tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode("utf-8", errors=self.errors)
        return text
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id] if self.sep_token_id is not None else []
        cls = [self.cls_token_id] if self.sep_token_id is not None else []
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
            writer.write("#version: 0.2\n")
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(f"Saving vocabulary to {merge_file}: BPE merge indices are not consecutive. Please check that the tokenizer is not corrupted!")
                    index = token_index
                writer.write(" ".join(bpe_tokens) + "\n")
                index += 1
        return vocab_file, merge_file
    def prepare_for_tokenization(self, text, is_split_into_words=False, **kwargs):
        add_prefix_space = kwargs.pop("add_prefix_space", self.add_prefix_space)
        if is_split_into_words or add_prefix_space: text = " " + text
        return (text, kwargs)
    def decode(self, token_ids: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None,
    truncate_before_pattern: Optional[List[str]] = None, **kwargs) -> str:
        token_ids = to_py_obj(token_ids)
        decoded_text = super()._decode(token_ids=token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces, **kwargs)
        if truncate_before_pattern is not None and len(truncate_before_pattern) > 0: decoded_text = self.truncate(decoded_text, truncate_before_pattern)
        return decoded_text
    def truncate(self, completion, truncate_before_pattern):
        def find_re(string, pattern, start_pos):
            m = pattern.search(string, start_pos)
            return m.start() if m else -1
        terminals = [re.compile(pattern, re.MULTILINE) for pattern in truncate_before_pattern]
        prints = list(re.finditer("^print", completion, re.MULTILINE))
        if len(prints) > 1: completion = completion[: prints[1].start()]
        defs = list(re.finditer("^def", completion, re.MULTILINE))
        if len(defs) > 1: completion = completion[: defs[1].start()]
        start_pos = 0
        terminals_pos = [pos for pos in [find_re(completion, terminal, start_pos) for terminal in terminals] if pos != -1]
        if len(terminals_pos) > 0: return completion[: min(terminals_pos)]
        else: return completion
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
