"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import time
import warnings
from abc import ABC
from collections import OrderedDict
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from torch.nn import functional as F
from ..pytorch_utils import isin_mps_friendly
from ..tokenization_utils_base import PreTrainedTokenizerBase
from ..utils import add_start_docstrings, logging
logger = logging.get_logger(__name__)
STOP_STRING_EMBEDDING_CACHE = OrderedDict()
STOPPING_CRITERIA_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        scores (`torch.FloatTensor` of shape `(batch_size, config.vocab_size)`):
            Prediction scores of a language modeling head. These can be scores for each vocabulary token before SoftMax
            or scores for each vocabulary token after SoftMax. If this stopping criteria depends on the `scores` input,
            make sure you pass `return_dict_in_generate=True, output_scores=True` to `generate`.
        kwargs (`Dict[str, Any]`, *optional*):
            Additional stopping criteria specific kwargs.
    Return:
        `torch.BoolTensor`. (`torch.BoolTensor` of shape `(batch_size, 1)`), where `True` indicates we stop generation
            for a particular row, `True` indicates we should continue.
"""
class StoppingCriteria(ABC):
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor: raise NotImplementedError("StoppingCriteria needs to be subclassed")
class MaxLengthCriteria(StoppingCriteria):
    def __init__(self, max_length: int, max_position_embeddings: Optional[int] = None):
        self.max_length = max_length
        self.max_position_embeddings = max_position_embeddings
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        cur_len = input_ids.shape[-1]
        is_done = cur_len >= self.max_length
        if self.max_position_embeddings is not None and not is_done and cur_len >= self.max_position_embeddings: logger.warning_once(f"This is a friendly reminder - the current text generation call will exceed the model's predefined maximum length ({self.max_position_embeddings}). Depending on the model, you may observe exceptions, performance degradation, or nothing at all.")
        return torch.full((input_ids.shape[0],), is_done, device=input_ids.device, dtype=torch.bool)
class MaxTimeCriteria(StoppingCriteria):
    def __init__(self, max_time: float, initial_timestamp: Optional[float] = None):
        self.max_time = max_time
        self.initial_timestamp = time.time() if initial_timestamp is None else initial_timestamp
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        is_done = time.time() - self.initial_timestamp > self.max_time
        return torch.full((input_ids.shape[0],), is_done, device=input_ids.device, dtype=torch.bool)
class StopStringCriteria(StoppingCriteria):
    def __init__(self, tokenizer: PreTrainedTokenizerBase, stop_strings: Union[str, List[str]]):
        if isinstance(stop_strings, str): stop_strings = [stop_strings]
        self.stop_strings: Tuple[str, ...] = tuple(stop_strings)
        vocab = tokenizer.get_vocab()
        token_list, token_indices = tuple(vocab.keys()), tuple(vocab.values())
        self.embedding_vec, self.max_valid_positions, self.max_valid_end_lens = self.clean_and_embed_tokens_with_cache(token_list, token_indices, self.stop_strings, tokenizer)
        self.maximum_token_len = max([len(stop_string) for stop_string in self.stop_strings])
        self.num_stop_strings = len(self.stop_strings)
        self.target_lens = torch.tensor([len(stop_string) for stop_string in stop_strings], dtype=torch.int32)
    def clean_and_embed_tokens_with_cache(self, token_list, token_indices, stop_strings, tokenizer):
        if (token_list, token_indices, stop_strings) in STOP_STRING_EMBEDDING_CACHE:
            embedding_vec, max_valid_positions, max_valid_end_lens = STOP_STRING_EMBEDDING_CACHE[(token_list, token_indices, self.stop_strings)]
            STOP_STRING_EMBEDDING_CACHE.move_to_end((token_list, token_indices, stop_strings))
        else:
            clean_token_list, clean_token_indices = self.clean_tokenizer_vocab(tokenizer)
            embedding_vec, max_valid_positions, max_valid_end_lens = self._stop_string_create_embedding_vec(clean_token_list, clean_token_indices, stop_strings)
            STOP_STRING_EMBEDDING_CACHE[(token_list, token_indices, stop_strings)] = (embedding_vec, max_valid_positions, max_valid_end_lens)
            if len(STOP_STRING_EMBEDDING_CACHE) > 8: STOP_STRING_EMBEDDING_CACHE.popitem(last=False)
        return embedding_vec, max_valid_positions, max_valid_end_lens
    @staticmethod
    def clean_tokenizer_vocab(tokenizer, static_prefix="abcdef"):
        vocab = tokenizer.get_vocab()
        clean_token_list = []
        clean_token_indices = []
        sentence_base = tokenizer(static_prefix, add_special_tokens=False)["input_ids"]
        tokens_base = [tokenizer._convert_id_to_token(tok) for tok in sentence_base]
        for token, token_idx in vocab.items():
            token_string = tokenizer.convert_tokens_to_string(tokens_base + [token])
            token_string = token_string[token_string.index(static_prefix) + len(static_prefix) :]
            clean_token_list.append(token_string)
            clean_token_indices.append(token_idx)
        return tuple(clean_token_list), tuple(clean_token_indices)
    @staticmethod
    def _stop_string_get_matching_positions(token_list, token_indices, stop_strings) -> Tuple[Dict[str, Dict[str, List[int]]], Dict[str, Dict[str, List[int]]]]:
        token_valid_positions = {}
        token_end_overlaps = {}
        for stop_string in stop_strings:
            reversed_stop_string = stop_string[::-1]
            token_valid_positions[stop_string] = {}
            token_end_overlaps[stop_string] = {}
            for token, tok_idx in zip(token_list, token_indices):
                reversed_token = token[::-1]
                matching_positions = []
                possible_end_lengths = []
                for i in range(1 - len(token), len(stop_string)):
                    if i < 0:
                        tok = reversed_token[-i:]
                        i = 0
                    else: tok = reversed_token
                    stop = reversed_stop_string[i : i + len(tok)]
                    if tok.startswith(stop):
                        if i == 0: possible_end_lengths.append(min(len(tok), len(stop)))
                        else: matching_positions.append(i)
                if matching_positions: token_valid_positions[stop_string][tok_idx] = matching_positions
                if possible_end_lengths: token_end_overlaps[stop_string][tok_idx] = possible_end_lengths
        return token_valid_positions, token_end_overlaps
    @staticmethod
    def _stop_string_create_embedding_vec(token_list, token_indices, stop_strings) -> Dict[str, torch.tensor]:
        token_valid_positions, token_end_overlaps = StopStringCriteria._stop_string_get_matching_positions(token_list, token_indices, stop_strings)
        all_valid_positions = [len(val) for positions in token_valid_positions.values() for val in positions.values()]
        max_valid_positions = max(all_valid_positions) if all_valid_positions else 1
        valid_end_lens = [len(val) for positions in token_end_overlaps.values() for val in positions.values()]
        if not valid_end_lens: raise ValueError("Stop string preprocessing was unable to identify tokens matching one or more of the supplied stop string(s). This is most often caused by the stop strings containing unusual characters that are not in the tokenizer vocabulary.")
        max_valid_end_lens = max(valid_end_lens)
        vec_size = len(stop_strings) * (max_valid_positions + max_valid_end_lens) + 1
        gather_vec = np.full((len(token_list), vec_size), dtype=np.int32, fill_value=-1)
        for i, stop_string in enumerate(stop_strings):
            positions = token_valid_positions[stop_string]
            end_lens = token_end_overlaps[stop_string]
            for token_idx, valid_positions in positions.items(): gather_vec[token_idx, max_valid_positions * i : max_valid_positions * i + len(valid_positions)] = (valid_positions)
            for token_idx, possible_end_lens in end_lens.items(): gather_vec[token_idx, max_valid_positions * len(stop_strings) + max_valid_end_lens * i : max_valid_positions * len(stop_strings) + max_valid_end_lens * i + len(possible_end_lens)] = possible_end_lens
            for token, token_idx in zip(token_list, token_indices): gather_vec[token_idx, -1] = len(token)
        gather_vec = torch.tensor(gather_vec, dtype=torch.int32)
        return gather_vec, max_valid_positions, max_valid_end_lens
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.Tensor:
        self.embedding_vec = self.embedding_vec.to(input_ids.device)
        self.target_lens = self.target_lens.to(input_ids.device)
        input_ids = input_ids[:, -self.maximum_token_len :]
        flipped_ids = torch.flip(input_ids, (1,))
        max_valid_positions = self.max_valid_positions
        embedded = F.embedding(flipped_ids, self.embedding_vec)
        valid_positions = embedded[:, 1:, : max_valid_positions * self.num_stop_strings].unflatten(-1, (self.num_stop_strings, -1))
        end_lengths = embedded[:, :1, max_valid_positions * self.num_stop_strings : -1].unflatten(-1, (self.num_stop_strings, -1))
        lengths = embedded[:, 1:, None, -1:]
        lengths = lengths.expand((-1, -1, end_lengths.shape[-2], end_lengths.shape[-1]))
        lengths_with_ends = torch.cat([end_lengths, lengths], dim=1)
        cumsum = lengths_with_ends.cumsum(dim=1)
        initial_match = end_lengths > 0
        later_match = torch.any(cumsum[:, :-1, :, None] == valid_positions[:, :, :, :, None], axis=-2)
        match = torch.cat([initial_match, later_match], dim=1)
        mask = (~match).cumsum(dim=1, dtype=torch.int32)
        mask = mask == 0
        string_matches = torch.amax(cumsum * mask, dim=(1, -1)) >= self.target_lens[None, :]
        return torch.any(string_matches, dim=-1)
class EosTokenCriteria(StoppingCriteria):
    def __init__(self, eos_token_id: Union[int, List[int], torch.Tensor]):
        if not isinstance(eos_token_id, torch.Tensor):
            if isinstance(eos_token_id, int): eos_token_id = [eos_token_id]
            eos_token_id = torch.tensor(eos_token_id)
        self.eos_token_id = eos_token_id
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        self.eos_token_id = self.eos_token_id.to(input_ids.device)
        is_done = isin_mps_friendly(input_ids[:, -1], self.eos_token_id)
        return is_done
class ConfidenceCriteria(StoppingCriteria):
    def __init__(self, assistant_confidence_threshold): self.assistant_confidence_threshold = assistant_confidence_threshold
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        probs = scores[-1].softmax(-1)
        p = probs[0, input_ids[0, -1]].item()
        if p < self.assistant_confidence_threshold: return True
        return False
class StoppingCriteriaList(list):
    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        is_done = torch.full((input_ids.shape[0],), False, device=input_ids.device, dtype=torch.bool)
        for criteria in self: is_done = is_done | criteria(input_ids, scores, **kwargs)
        return is_done
    @property
    def max_length(self) -> Optional[int]:
        for stopping_criterium in self:
            if isinstance(stopping_criterium, MaxLengthCriteria): return stopping_criterium.max_length
        return None
def validate_stopping_criteria(stopping_criteria: StoppingCriteriaList, max_length: int) -> StoppingCriteriaList:
    stopping_max_length = stopping_criteria.max_length
    new_stopping_criteria = deepcopy(stopping_criteria)
    if stopping_max_length is not None and stopping_max_length != max_length: warnings.warn("You set different `max_length` for stopping criteria and `max_length` parameter", UserWarning)
    elif stopping_max_length is None: new_stopping_criteria.append(MaxLengthCriteria(max_length=max_length))
    return new_stopping_criteria
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
