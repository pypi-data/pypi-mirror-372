"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from json import load as sapiens_load, dumps as sapiens_dumps
from typing import Optional as SAPIENSOptional, Tuple as SAPIENSTuple
from .sapiens_import_variables import VOCAB_FILES_NAMES, MAX_MODEL_INPUT_SIZES, PRETOKENIZE_REGEX
from ...tokenization_utils import SapiensPreTrainedTokenizer, SapiensAddedToken
class SapiensTokenizer(SapiensPreTrainedTokenizer):
    vocab_files_names, model_input_names, encoding, _version = VOCAB_FILES_NAMES, ["input_ids", "attention_mask"], "utf-8", "#version:"
    def __init__(self, vocab_file=None, merges_file=None, errors="replace", unk_token="<|endoftext|>", bos_token=None, eos_token="<|endoftext|>", pad_token="<|endoftext|>", clean_up_tokenization_spaces=False, split_special_tokens=False, **kwargs):
        insert_unk_token = unk_token if type(unk_token) == str else "<|endoftext|>"
        insert_unk_token = (SapiensAddedToken(insert_unk_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(insert_unk_token, str) else insert_unk_token)
        insert_bos_token = bos_token if type(bos_token) == str else None
        insert_bos_token = (SapiensAddedToken(insert_bos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(insert_bos_token, str) else insert_bos_token)
        insert_eos_token = eos_token if type(eos_token) == str else "<|endoftext|>"
        insert_eos_token = (SapiensAddedToken(insert_eos_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(insert_eos_token, str) else insert_eos_token)
        insert_pad_token = pad_token if type(pad_token) == str else "<|endoftext|>"
        insert_pad_token = (SapiensAddedToken(insert_pad_token, lstrip=False, rstrip=False, special=True, normalized=False) if isinstance(insert_pad_token, str) else insert_pad_token)
        with open(vocab_file, encoding=encoding) as vocab_handle: self.encoder = sapiens_load(vocab_handle)
        self.decoder, self.errors, exponential_power, zero, one = {v: k for k, v in self.encoder.items()}, errors, 256, 0, 1
        from functools import lru_cache
        @lru_cache()
        def bytes_to_unicode():
            union_of_listings = (list(range(33, 126 + one)) + list(range(161, 172 + one)) + list(range(174, 255 + one)))
            mathematical_list, number = union_of_listings[:], zero
            for x in range(exponential_power):
                if x not in union_of_listings:
                    union_of_listings.append(x), mathematical_list.append(exponential_power + number)
                    number += one
            return dict(zip(union_of_listings, [chr(number) for number in mathematical_list]))
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder, bpe_merges = {v: k for k, v in self.byte_encoder.items()}, []
        with open(merges_file, encoding=encoding) as merges_handle:
            for index, line in enumerate(merges_handle):
                line = line.strip()
                if (index == zero and line.startswith(_version)) or not line: continue
                bpe_merges.append(tuple(line.split()))
        self.bpe_ranks, self.cache = dict(zip(bpe_merges, range(len(bpe_merges)))), {}
        import regex as re
        self.__re = re
        self.pat = re.compile(PRETOKENIZE_REGEX)
        super().__init__(errors=errors, bos_token=insert_bos_token, eos_token=insert_eos_token, pad_token=insert_pad_token, unk_token=insert_unk_token, clean_up_tokenization_spaces=clean_up_tokenization_spaces, split_special_tokens=split_special_tokens, **kwargs)
    @property
    def vocab_size(self) -> int: return len(self.encoder)
    def get_vocab(self): return dict(self.encoder, **self.added_tokens_encoder)
    def bpe(self, token=None):
        if token in self.cache: return self.cache[token]
        def get_pairs(word):
            pairs, prev_char = set(), word[0]
            for char in word[1:]:
                pairs.add((prev_char, char))
                prev_char = char
            return pairs
        word, pairs = tuple(token), get_pairs(word)
        if not pairs: return token
        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float("inf")))
            if bigram not in self.bpe_ranks: break
            first, second = bigram
            new_word, start = [], 0
            while start < len(word):
                try: end = word.index(first, start)
                except ValueError:
                    new_word.extend(word[start:])
                    break
                else:
                    new_word.extend(word[start:end])
                    start = end
                two_more, one_more = 2, 1
                if word[start] == first and start < len(word) - one_more and word[start + one_more] == second:
                    new_word.append(first + second)
                    start += two_more
                else:
                    new_word.append(word[start])
                    start += one_more
            word = tuple(new_word)
            if len(word) == one_more: break
            else: pairs = get_pairs(word)
        word = chr(32).join(word)
        self.cache[token] = word
        return word
    def _tokenize(self, text=""):
        bpe_tokens = []
        for token in self.__re.findall(self.pat, text): bpe_tokens.extend(bpe_token for bpe_token in self.bpe("".join(self.byte_encoder[tok] for tok in token.encode("utf-8"))).split(chr(32)))
        return bpe_tokens
    def _convert_token_to_id(self, token=None): return self.encoder.get(token, self.encoder.get(self.unk_token))
    def _convert_id_to_token(self, index=0): return self.decoder.get(index)
    def convert_tokens_to_string(self, tokens=None): return bytearray([self.byte_decoder[element] for element in "".join(tokens)]).decode("utf-8", errors=self.errors)
    def decode(self, token_ids=None, skip_special_tokens: bool = False, clean_up_tokenization_spaces: SAPIENSOptional[bool] = False, spaces_between_special_tokens: bool = False,
    **kwargs) -> str: return super().decode(token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces,
    spaces_between_special_tokens=spaces_between_special_tokens, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: SAPIENSOptional[str] = None) -> SAPIENSTuple[str]:
        import os
        if not os.path.isdir(save_directory): return
        vocab_file, merge_file, index = os.path.join(save_directory, (filename_prefix + chr(45) if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"]), os.path.join(save_directory, (filename_prefix + chr(45) if filename_prefix else "") + VOCAB_FILES_NAMES["merges_file"]), 0
        w, encoding, indent, sort_keys, ensure_ascii, _version, one_more = "w", "utf-8", 2, True, False, "#version: 0.0\n", 1
        with open(vocab_file, w, encoding=encoding) as file: file.write(sapiens_dumps(self.encoder, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii) + "\n")
        with open(merge_file, w, encoding=encoding) as writer:
            writer.write(_version)
            for bpe_tokens, token_index in sorted(self.bpe_ranks.items(), key=lambda kv: kv[one_more]):
                if index != token_index: index = token_index
                writer.write(chr(32).join(bpe_tokens) + "\n")
                index += one_more
        return vocab_file, merge_file
    def prepare_for_tokenization(self, text="", **kwargs):
        from unicodedata import normalize
        return (normalize("NFC", text), kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
