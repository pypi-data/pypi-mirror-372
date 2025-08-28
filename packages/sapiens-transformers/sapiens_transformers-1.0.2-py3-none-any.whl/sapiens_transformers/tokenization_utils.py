"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .tokenization_utils_base import (ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING, INIT_TOKENIZER_DOCSTRING, AddedToken,
BatchEncoding, EncodedInput, EncodedInputPair, PreTokenizedInput, PreTokenizedInputPair, PreTrainedTokenizerBase, TextInput, TextInputPair, TruncationStrategy)
from .utils import PaddingStrategy, TensorType, add_end_docstrings, logging
from typing import Any, Dict, List, Optional, Tuple, Union, overload
from .tokenization_utils_base import AddedToken as SapiensAddedToken
from collections import OrderedDict
import unicodedata
import itertools
import bisect
import re
logger = logging.get_logger(__name__)
SPECIAL_TOKENS_MAP_FILE = "special_tokens_map.json"
ADDED_TOKENS_FILE = "added_tokens.json"
TOKENIZER_CONFIG_FILE = "tokenizer_config.json"
class Trie:
    def __init__(self, *args):
        self.data = {}
        self._tokens = set()
        self._termination_char = ""
        self.update(*args)
    def update(self, *args):
        for token in tuple(*args): self.add(token)
    def add(self, word: str):
        if not word: return
        self._tokens.add(word)
        ref = self.data
        for char in word:
            ref[char] = ref.setdefault(char, {})
            ref = ref[char]
        ref[self._termination_char] = 1
    def split(self, text: str) -> List[str]:
        states = OrderedDict()
        offsets = [0]
        skip = 0
        for current, current_char in enumerate(text):
            if skip and current < skip: continue
            to_remove = set()
            reset = False
            for start, trie_pointer in states.items():
                if "" in trie_pointer:
                    for lookstart, looktrie_pointer in states.items():
                        if lookstart > start: break
                        elif lookstart < start:
                            lookahead_index = current + 1
                            end = current + 1
                        else:
                            lookahead_index = current
                            end = current
                        next_char = text[lookahead_index] if lookahead_index < len(text) else None
                        if "" in looktrie_pointer:
                            start = lookstart
                            end = lookahead_index
                            skip = lookahead_index
                        while next_char in looktrie_pointer:
                            looktrie_pointer = looktrie_pointer[next_char]
                            lookahead_index += 1
                            if "" in looktrie_pointer:
                                start = lookstart
                                end = lookahead_index
                                skip = lookahead_index
                            if lookahead_index == len(text): break
                            next_char = text[lookahead_index]
                    offsets.append(start)
                    offsets.append(end)
                    reset = True
                    break
                elif current_char in trie_pointer:
                    trie_pointer = trie_pointer[current_char]
                    states[start] = trie_pointer
                else: to_remove.add(start)
            if reset: states = {}
            else:
                for start in to_remove: del states[start]
            if current >= skip and current_char in self.data: states[current] = self.data[current_char]
        for start, trie_pointer in states.items():
            if "" in trie_pointer:
                end = len(text)
                offsets.append(start)
                offsets.append(end)
                break
        return self.cut_text(text, offsets)
    def cut_text(self, text, offsets):
        offsets.append(len(text))
        tokens = []
        start = 0
        for end in offsets:
            if start > end:
                logger.error("There was a bug in Trie algorithm in tokenization. Attempting to recover. Please report it anyway.")
                continue
            elif start == end: continue
            tokens.append(text[start:end])
            start = end
        return tokens
class ExtensionsTrie(Trie):
    def __init__(self, *args): super().__init__(*args)
    def extensions(self, prefix: str):
        prefix_node = self._get_node(prefix)
        ret = self._collect_tokens(prefix_node)
        return [prefix + token for token in ret]
    def _get_node(self, token: str) -> dict:
        node = self.data
        for char in token: node = node[char]
        return node
    def _collect_tokens(self, node: dict) -> list:
        tokens = [self._termination_char] if self._termination_char in node else []
        for token, subtrie_head in node.items():
            if token != self._termination_char:
                subtokens = self._collect_tokens(subtrie_head)
                tokens.extend([token + subtoken for subtoken in subtokens])
        return tokens
def _is_whitespace(char):
    if char == " " or char == "\t" or char == "\n" or char == "\r": return True
    cat = unicodedata.category(char)
    if cat == "Zs": return True
    return False
def _is_control(char):
    if char == "\t" or char == "\n" or char == "\r": return False
    cat = unicodedata.category(char)
    if cat.startswith("C"): return True
    return False
def _is_punctuation(char):
    cp = ord(char)
    if (cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126): return True
    cat = unicodedata.category(char)
    if cat.startswith("P"): return True
    return False
def _is_end_of_word(text):
    last_char = text[-1]
    return bool(_is_control(last_char) | _is_punctuation(last_char) | _is_whitespace(last_char))
def _is_start_of_word(text):
    first_char = text[0]
    return bool(_is_control(first_char) | _is_punctuation(first_char) | _is_whitespace(first_char))
def _insert_one_token_to_ordered_list(token_list: List[str], new_token: str):
    insertion_idx = bisect.bisect_left(token_list, new_token)
    if insertion_idx < len(token_list) and token_list[insertion_idx] == new_token: return
    else: token_list.insert(insertion_idx, new_token)
@add_end_docstrings(INIT_TOKENIZER_DOCSTRING)
class PreTrainedTokenizer(PreTrainedTokenizerBase):
    def __init__(self, **kwargs):
        self.tokens_trie = Trie()
        if not hasattr(self, "_added_tokens_decoder"): self._added_tokens_decoder: Dict[int, AddedToken] = {}
        self._added_tokens_decoder.update(kwargs.pop("added_tokens_decoder", {}))
        self._added_tokens_encoder: Dict[str, int] = {k.content: v for v, k in self._added_tokens_decoder.items()}
        super().__init__(**kwargs)
        self._add_tokens([token for token in self.all_special_tokens_extended if token not in self._added_tokens_encoder], special_tokens=True)
        self._decode_use_source_tokenizer = False
    @property
    def is_fast(self) -> bool: return False
    @property
    def vocab_size(self) -> int: raise NotImplementedError
    @property
    def added_tokens_encoder(self) -> Dict[str, int]: return {k.content: v for v, k in sorted(self._added_tokens_decoder.items(), key=lambda item: item[0])}
    @property
    def added_tokens_decoder(self) -> Dict[int, AddedToken]: return dict(sorted(self._added_tokens_decoder.items(), key=lambda item: item[0]))
    @added_tokens_decoder.setter
    def added_tokens_decoder(self, value: Dict[int, Union[AddedToken, str]]) -> Dict[int, AddedToken]:
        for index, token in value.items():
            if not isinstance(token, (str, AddedToken)) or not isinstance(index, int): raise TypeError(f"The provided `added_tokens_decoder` has an element of type {index.__class__, token.__class__}, should be a dict of {int, Union[AddedToken, str]}")
            self._added_tokens_decoder[index] = AddedToken(token) if isinstance(token, str) else token
            self._added_tokens_encoder[str(token)] = index
        self._update_total_vocab_size()
    def get_added_vocab(self) -> Dict[str, int]: return self._added_tokens_encoder
    def __len__(self): return self.total_vocab_size
    def _update_total_vocab_size(self): self.total_vocab_size = len(self.get_vocab())
    def _add_tokens(self, new_tokens: Union[List[str], List[AddedToken]], special_tokens: bool = False) -> int:
        added_tokens = 0
        if new_tokens is None: return added_tokens
        current_vocab = self.get_vocab().copy()
        new_idx = len(current_vocab)
        for token in new_tokens:
            if not isinstance(token, (str, AddedToken)): raise TypeError(f"Token {token} is not a string but a {type(token)}.")
            if str(token) == "": continue
            if isinstance(token, str):
                if token in self._added_tokens_encoder: continue
                else:
                    is_special = token in self.all_special_tokens or special_tokens
                    token = AddedToken(token, rstrip=False, lstrip=False, normalized=not is_special, special=is_special)
            elif special_tokens: token.__setstate__({"special": True, "normalized": token.normalized})
            if token in self._added_tokens_decoder: continue
            if not token.special and token.normalized and getattr(self, "do_lower_case", False): token.content = token.content.lower()
            if token.content not in current_vocab:
                token_index = new_idx + added_tokens
                current_vocab[token.content] = token_index
                added_tokens += 1
            else: token_index = current_vocab[token.content]
            if token.special and str(token) not in self.all_special_tokens: self._additional_special_tokens.append(token)
            self._added_tokens_decoder[token_index] = token
            self._added_tokens_encoder[token.content] = token_index
            if self.verbose: logger.info(f"Adding {token} to the vocabulary")
        self._update_trie()
        self._update_total_vocab_size()
        return added_tokens
    def _update_trie(self, unique_no_split_tokens: Optional[str] = []):
        for token in self._added_tokens_decoder.values():
            if token not in self.tokens_trie._tokens: self.tokens_trie.add(token.content)
        for token in unique_no_split_tokens:
            if token not in self.tokens_trie._tokens: self.tokens_trie.add(token)
    def num_special_tokens_to_add(self, pair: bool = False) -> int:
        token_ids_0 = []
        token_ids_1 = []
        return len(self.build_inputs_with_special_tokens(token_ids_0, token_ids_1 if pair else None))
    def tokenize(self, text: TextInput, **kwargs) -> List[str]:
        split_special_tokens = kwargs.pop("split_special_tokens", self.split_special_tokens)
        text, kwargs = self.prepare_for_tokenization(text, **kwargs)
        if kwargs: logger.warning(f"Keyword arguments {kwargs} not recognized.")
        if hasattr(self, "do_lower_case") and self.do_lower_case:
            escaped_special_toks = [re.escape(s_tok) for s_tok in (self.all_special_tokens)]
            escaped_special_toks += [re.escape(s_tok.content) for s_tok in (self._added_tokens_decoder.values()) if not s_tok.special and s_tok.normalized]
            open_parentheses, close_parentheses = r"(", rf"{chr(41)}|"
            pattern = open_parentheses + r"|".join(escaped_special_toks) + close_parentheses + r"(.+?)"
            text = re.sub(pattern, lambda m: m.groups()[0] or m.groups()[1].lower(), text)
        if split_special_tokens:
            no_split_token = []
            tokens = [text]
        else:
            no_split_token = self._added_tokens_encoder.keys()
            tokens = self.tokens_trie.split(text)
        for i, token in enumerate(tokens):
            if token in no_split_token:
                tok_extended = self._added_tokens_decoder.get(self._added_tokens_encoder[token], None)
                left = tokens[i - 1] if i > 0 else None
                right = tokens[i + 1] if i < len(tokens) - 1 else None
                if isinstance(tok_extended, AddedToken):
                    if tok_extended.rstrip and right: tokens[i + 1] = right.lstrip()
                    if tok_extended.lstrip and left: tokens[i - 1] = left.rstrip()
                    if tok_extended.single_word and left and left[-1] != " ":
                        tokens[i - 1] += token
                        tokens[i] = ""
                    elif tok_extended.single_word and right and right[0] != " ":
                        tokens[i + 1] = token + tokens[i + 1]
                        tokens[i] = ""
                else: raise ValueError(f"{tok_extended} cannot be tokenized because it was not properly added to the tokenizer. This means that it is not an `AddedToken` but a {type(tok_extended)}")
        tokenized_text = []
        for token in tokens:
            if not token: continue
            if token in no_split_token: tokenized_text.append(token)
            else: tokenized_text.extend(self._tokenize(token))
        return tokenized_text
    def _tokenize(self, text, **kwargs): raise NotImplementedError
    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        if tokens is None: return None
        if isinstance(tokens, str): return self._convert_token_to_id_with_added_voc(tokens)
        ids = []
        for token in tokens: ids.append(self._convert_token_to_id_with_added_voc(token))
        return ids
    def _convert_token_to_id_with_added_voc(self, token):
        if token is None: return None
        if token in self._added_tokens_encoder: return self._added_tokens_encoder[token]
        return self._convert_token_to_id(token)
    def _convert_token_to_id(self, token): raise NotImplementedError
    def _encode_plus(self, text: Union[TextInput, PreTokenizedInput, EncodedInput], text_pair: Optional[Union[TextInput, PreTokenizedInput, EncodedInput]] = None, add_special_tokens: bool = True,
    padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0,
    is_split_into_words: bool = False, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None,
    return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False,
    return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, **kwargs) -> BatchEncoding:
        def get_input_ids(text):
            if isinstance(text, str):
                tokens = self.tokenize(text, **kwargs)
                return self.convert_tokens_to_ids(tokens)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], str):
                if is_split_into_words:
                    tokens = list(itertools.chain(*(self.tokenize(t, is_split_into_words=True, **kwargs) for t in text)))
                    return self.convert_tokens_to_ids(tokens)
                else: return self.convert_tokens_to_ids(text)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int): return text
            else:
                if is_split_into_words: raise ValueError(f"Input {text} is not valid. Should be a string or a list/tuple of strings when `is_split_into_words=True`.")
                else: raise ValueError(f"Input {text} is not valid. Should be a string, a list/tuple of strings or a list/tuple of integers.")
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        first_ids = get_input_ids(text)
        second_ids = get_input_ids(text_pair) if text_pair is not None else None
        return self.prepare_for_model(first_ids, pair_ids=second_ids, add_special_tokens=add_special_tokens, padding=padding_strategy.value, truncation=truncation_strategy.value, max_length=max_length, stride=stride,
        pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_tensors=return_tensors, prepend_batch_axis=True, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids,
        return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, verbose=verbose)
    def _batch_encode_plus(self, batch_text_or_text_pairs: Union[List[TextInput], List[TextInputPair], List[PreTokenizedInput], List[PreTokenizedInputPair], List[EncodedInput], List[EncodedInputPair]], add_special_tokens: bool = True,
    padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE, max_length: Optional[int] = None, stride: int = 0, is_split_into_words: bool = False,
    pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[Union[str, TensorType]] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None,
    return_overflowing_tokens: bool = False, return_special_tokens_mask: bool = False, return_offsets_mapping: bool = False, return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False, **kwargs) -> BatchEncoding:
        def get_input_ids(text):
            if isinstance(text, str):
                tokens = self.tokenize(text, **kwargs)
                return self.convert_tokens_to_ids(tokens)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], str):
                if is_split_into_words:
                    tokens = list(itertools.chain(*(self.tokenize(t, is_split_into_words=True, **kwargs) for t in text)))
                    return self.convert_tokens_to_ids(tokens)
                else: return self.convert_tokens_to_ids(text)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int): return text
            else: raise ValueError("Input is not valid. Should be a string, a list/tuple of strings or a list/tuple of integers.")
        if return_offsets_mapping: raise NotImplementedError("return_offset_mapping is not available when using Python tokenizers. To use this feature, change your tokenizer to one deriving from sapiens_transformers.PreTrainedTokenizerFast.")
        input_ids = []
        for ids_or_pair_ids in batch_text_or_text_pairs:
            if not isinstance(ids_or_pair_ids, (list, tuple)): ids, pair_ids = ids_or_pair_ids, None
            elif is_split_into_words and not isinstance(ids_or_pair_ids[0], (list, tuple)): ids, pair_ids = ids_or_pair_ids, None
            else: ids, pair_ids = ids_or_pair_ids
            first_ids = get_input_ids(ids)
            second_ids = get_input_ids(pair_ids) if pair_ids is not None else None
            input_ids.append((first_ids, second_ids))
        batch_outputs = self._batch_prepare_for_model(input_ids, add_special_tokens=add_special_tokens, padding_strategy=padding_strategy, truncation_strategy=truncation_strategy, max_length=max_length, stride=stride, pad_to_multiple_of=pad_to_multiple_of,
        padding_side=padding_side, return_attention_mask=return_attention_mask, return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length,
        return_tensors=return_tensors, verbose=verbose, split_special_tokens=split_special_tokens)
        return BatchEncoding(batch_outputs)
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def _batch_prepare_for_model(self, batch_ids_pairs: List[Union[PreTokenizedInputPair, Tuple[List[int], None]]], add_special_tokens: bool = True, padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD, truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
    max_length: Optional[int] = None, stride: int = 0, pad_to_multiple_of: Optional[int] = None, padding_side: Optional[bool] = None, return_tensors: Optional[str] = None, return_token_type_ids: Optional[bool] = None, return_attention_mask: Optional[bool] = None, return_overflowing_tokens: bool = False,
    return_special_tokens_mask: bool = False, return_length: bool = False, verbose: bool = True, split_special_tokens: bool = False) -> BatchEncoding:
        batch_outputs = {}
        for first_ids, second_ids in batch_ids_pairs:
            outputs = self.prepare_for_model(first_ids, second_ids, add_special_tokens=add_special_tokens, padding=PaddingStrategy.DO_NOT_PAD.value, truncation=truncation_strategy.value, max_length=max_length, stride=stride, pad_to_multiple_of=None, padding_side=None, return_attention_mask=False,
            return_token_type_ids=return_token_type_ids, return_overflowing_tokens=return_overflowing_tokens, return_special_tokens_mask=return_special_tokens_mask, return_length=return_length, return_tensors=None, prepend_batch_axis=False, verbose=verbose, split_special_tokens=split_special_tokens)
            for key, value in outputs.items():
                if key not in batch_outputs: batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(batch_outputs, padding=padding_strategy.value, max_length=max_length, pad_to_multiple_of=pad_to_multiple_of, padding_side=padding_side, return_attention_mask=return_attention_mask)
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return batch_outputs
    def prepare_for_tokenization(self, text: str, is_split_into_words: bool = False, **kwargs) -> Tuple[str, Dict[str, Any]]: return (text, kwargs)
    def get_special_tokens_mask(self, token_ids_0: List, token_ids_1: Optional[List] = None, already_has_special_tokens: bool = False) -> List[int]:
        if already_has_special_tokens:
            if token_ids_1 is not None: raise ValueError("You should not supply a second sequence if the provided sequence of ids is already formatted with special tokens for the model.")
            return super().get_special_tokens_mask(token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True)
        return [0] * ((len(token_ids_1) if token_ids_1 else 0) + len(token_ids_0))
    @overload
    def convert_ids_to_tokens(self, ids: int, skip_special_tokens: bool = False) -> str: ...
    @overload
    def convert_ids_to_tokens(self, ids: List[int], skip_special_tokens: bool = False) -> List[str]: ...
    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False) -> Union[str, List[str]]:
        if isinstance(ids, int):
            if ids in self._added_tokens_decoder: return self._added_tokens_decoder[ids].content
            else: return self._convert_id_to_token(ids)
        tokens = []
        for index in ids:
            index = int(index)
            if skip_special_tokens and index in self.all_special_ids: continue
            if index in self._added_tokens_decoder: tokens.append(self._added_tokens_decoder[index].content)
            else: tokens.append(self._convert_id_to_token(index))
        return tokens
    def _convert_id_to_token(self, index: int) -> str: raise NotImplementedError
    def convert_tokens_to_string(self, tokens: List[str]) -> str: return " ".join(tokens)
    def _decode(self, token_ids: Union[int, List[int]], skip_special_tokens: bool = False, clean_up_tokenization_spaces: bool = None, spaces_between_special_tokens: bool = True, **kwargs) -> str:
        self._decode_use_source_tokenizer = kwargs.pop("use_source_tokenizer", False)
        filtered_tokens = self.convert_ids_to_tokens(token_ids, skip_special_tokens=skip_special_tokens)
        if isinstance(filtered_tokens, str): filtered_tokens = [filtered_tokens]
        legacy_added_tokens = set(self._added_tokens_encoder.keys()) - set(self.all_special_tokens) | {token for token in self.additional_special_tokens if self.convert_tokens_to_ids(token) >= self.vocab_size}
        sub_texts = []
        current_sub_text = []
        for token in filtered_tokens:
            if skip_special_tokens and token in self.all_special_tokens: continue
            if token in legacy_added_tokens:
                if current_sub_text:
                    string = self.convert_tokens_to_string(current_sub_text)
                    if len(string) > 0: sub_texts.append(string)
                    current_sub_text = []
                sub_texts.append(token)
            else: current_sub_text.append(token)
        if current_sub_text: sub_texts.append(self.convert_tokens_to_string(current_sub_text))
        if spaces_between_special_tokens: text = " ".join(sub_texts)
        else: text = "".join(sub_texts)
        clean_up_tokenization_spaces = (clean_up_tokenization_spaces if clean_up_tokenization_spaces is not None else self.clean_up_tokenization_spaces)
        if clean_up_tokenization_spaces:
            clean_text = self.clean_up_tokenization(text)
            return clean_text
        else: return text
class SapiensPreTrainedTokenizer(PreTrainedTokenizer): pass
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
