"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
from typing import List, Tuple
import numpy as np
import tensorflow as tf
from ..tf_utils import stable_softmax
from ..utils import add_start_docstrings
from ..utils.logging import get_logger
logger = get_logger(__name__)
TF_LOGITS_PROCESSOR_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`tf.Tensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`PreTrainedTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        scores (`tf.Tensor` of shape `(batch_size, config.vocab_size)`):
            Prediction scores of a language modeling head. These can be logits for each vocabulary when not using beam
            search or log softmax for each vocabulary token when using beam search.
        cur_len (`int`):
            The current length of valid input sequence tokens. In the TF implementation, the input_ids' sequence length
            is the maximum length generate can produce, and we need to know which of its tokens are valid.
        kwargs (`Dict[str, Any]`, *optional*):
            Additional logits processor specific kwargs.
    Return:
        `tf.Tensor` of shape `(batch_size, config.vocab_size)`: The processed prediction scores.
"""
class TFLogitsProcessor:
    @add_start_docstrings(TF_LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor: raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can be called.")
class TFLogitsWarper:
    @add_start_docstrings(TF_LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor: raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can be called.")
class TFLogitsProcessorList(list):
    @add_start_docstrings(TF_LOGITS_PROCESSOR_INPUTS_DOCSTRING)
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int, **kwargs) -> tf.Tensor:
        for processor in self:
            function_args = inspect.signature(processor.__call__).parameters
            if len(function_args) > 3:
                if not all(arg in kwargs for arg in list(function_args.keys())[2:]): raise ValueError(f"Make sure that all the required parameters: {list(function_args.keys())} for {processor.__class__} are passed to the logits processor.")
                scores = processor(input_ids, scores, cur_len, **kwargs)
            else: scores = processor(input_ids, scores, cur_len)
        return scores
class TFTemperatureLogitsWarper(TFLogitsWarper):
    def __init__(self, temperature: float):
        if not isinstance(temperature, float) or not (temperature > 0): raise ValueError(f"`temperature` has to be a strictly positive float, but is {temperature}")
        self.temperature = temperature
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        scores = scores / self.temperature
        return scores
class TFTopKLogitsWarper(TFLogitsWarper):
    def __init__(self, top_k: int, filter_value: float = -float("Inf"), min_tokens_to_keep: int = 1):
        if not isinstance(top_k, int) or top_k <= 0: raise ValueError(f"`top_k` has to be a strictly positive integer, but is {top_k}")
        self.top_k = max(top_k, min_tokens_to_keep)
        self.filter_value = filter_value
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        top_k = min(self.top_k, scores.shape[-1])
        indices_to_remove = scores < tf.math.top_k(scores, k=top_k)[0][..., -1:]
        next_scores = tf.where(indices_to_remove, self.filter_value, scores)
        return next_scores
class TFTopPLogitsWarper(TFLogitsWarper):
    def __init__(self, top_p: float, filter_value: float = -float("Inf"), min_tokens_to_keep: int = 1):
        if not isinstance(top_p, float) or (top_p < 0 or top_p > 1.0): raise ValueError(f"`top_p` has to be a float > 0 and < 1, but is {top_p}")
        if not isinstance(min_tokens_to_keep, int) or (min_tokens_to_keep < 1): raise ValueError(f"`min_tokens_to_keep` has to be a positive integer, but is {min_tokens_to_keep}")
        self.top_p = top_p
        self.filter_value = filter_value
        self.min_tokens_to_keep = min_tokens_to_keep
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        topk_scores, topk_indices = tf.math.top_k(scores, scores.shape[-1])
        mask_scores = tf.fill(scores.shape, self.filter_value)
        cumulative_probs = tf.math.cumsum(stable_softmax(topk_scores, axis=-1), axis=-1)
        score_mask = cumulative_probs < self.top_p
        score_mask = tf.concat((tf.ones([score_mask.shape[0], 1], dtype=tf.bool), score_mask[:, :-1]), axis=-1)
        score_mask = tf.concat((tf.ones([score_mask.shape[0], self.min_tokens_to_keep], dtype=tf.bool), score_mask[:, self.min_tokens_to_keep :]), axis=-1)
        topk_next_scores = tf.where(score_mask, topk_scores, mask_scores)
        scatter_rows = tf.tile(tf.expand_dims(tf.range(topk_indices.shape[0]), axis=-1), [1, topk_indices.shape[-1]])
        scatter_indices = tf.stack((scatter_rows, topk_indices), axis=-1)
        next_scores = tf.scatter_nd(scatter_indices, topk_next_scores, shape=topk_next_scores.shape)
        return next_scores
class TFMinLengthLogitsProcessor(TFLogitsProcessor):
    def __init__(self, min_length: int, eos_token_id: int):
        if not isinstance(min_length, int) or min_length < 0: raise ValueError(f"`min_length` has to be a positive integer, but is {min_length}")
        if not isinstance(eos_token_id, int) or eos_token_id < 0: raise ValueError(f"`eos_token_id` has to be a positive integer, but is {eos_token_id}")
        self.min_length = min_length
        self.eos_token_id = eos_token_id
    def _apply_eos_token_mask(self, scores: tf.Tensor) -> tf.Tensor:
        eos_token_id_mask = tf.range(scores.shape[-1]) == self.eos_token_id
        scores = tf.where(eos_token_id_mask, float("-inf"), scores)
        return scores
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        scores = tf.cond(tf.less(cur_len, self.min_length), lambda: self._apply_eos_token_mask(scores), lambda: tf.identity(scores))
        return scores
class TFRepetitionPenaltyLogitsProcessor(TFLogitsProcessor):
    def __init__(self, penalty: float):
        if not isinstance(penalty, float) or not (penalty > 0): raise ValueError(f"`penalty` has to be a strictly positive float, but is {penalty}")
        self.penalty = penalty
    def _create_score_penalties(self, input_ids: tf.Tensor, logits: tf.Tensor) -> tf.Tensor:
        logit_penalties = tf.gather(logits, input_ids, axis=1, batch_dims=1)
        logit_penalties = tf.where(logit_penalties > 0, 1 / self.penalty, logit_penalties)
        logit_penalties = tf.where(logit_penalties < 0, self.penalty, logit_penalties)
        token_penalties = tf.ones(logits.shape)
        batch_size = input_ids.shape[0]
        seq_len = tf.shape(input_ids)[1]
        indexable_prev_input_ids = tf.concat((tf.expand_dims(tf.repeat(tf.range(batch_size), seq_len), axis=-1), tf.expand_dims(tf.reshape(input_ids, [-1]), axis=-1)), axis=1)
        token_penalties = tf.tensor_scatter_nd_update(token_penalties, indices=indexable_prev_input_ids, updates=tf.reshape(logit_penalties, [-1]))
        return token_penalties
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        score_penalties = self._create_score_penalties(input_ids[:, :cur_len], scores)
        scores = tf.math.multiply(scores, score_penalties)
        return scores
class TFNoBadWordsLogitsProcessor(TFLogitsProcessor):
    def __init__(self, bad_words_ids: List[List[int]], eos_token_id: int):
        if not isinstance(bad_words_ids, List) or len(bad_words_ids) == 0: raise ValueError(f"`bad_words_ids` has to be a non-empty list, but is {bad_words_ids}.")
        if any(not isinstance(bad_word_ids, list) for bad_word_ids in bad_words_ids): raise ValueError(f"`bad_words_ids` has to be a list of lists, but is {bad_words_ids}.")
        if any(any((not isinstance(token_id, (int, np.integer)) or token_id < 0) for token_id in bad_word_ids) for bad_word_ids in bad_words_ids): raise ValueError(f"Each list in `bad_words_ids` has to be a list of positive integers, but is {bad_words_ids}.")
        self.bad_word_seqs_ids = tf.ragged.constant(bad_words_ids).to_tensor(default_value=-1)
        bad_word_seqs_len = [len(bad_words) for bad_words in bad_words_ids]
        if any(word_len == 0 for word_len in bad_word_seqs_len): raise ValueError(f"Banned words token sequences {bad_words_ids} cannot have an empty list")
        self.bad_word_seqs_len = tf.convert_to_tensor(bad_word_seqs_len, dtype=tf.int32)
        self.seq_forbidden_tokens = tf.convert_to_tensor([bad_words[-1] for bad_words in bad_words_ids])
    def _calc_row_banned_bad_tokens(self, row_input_ids: tf.Tensor) -> tf.Tensor:
        def _tokens_match(bad_word_seq_number):
            def _len_one(): return tf.cond(tf.math.equal(self.bad_word_seqs_len[bad_word_seq_number], 1), lambda: tf.ones((), dtype=tf.bool), _len_greater_than_cur_len)
            def _len_greater_than_cur_len(): return tf.cond(tf.math.greater(self.bad_word_seqs_len[bad_word_seq_number], tf.shape(row_input_ids)[0]), lambda: tf.zeros((), dtype=tf.bool), _match_found)
            def _match_found():
                compare_len = self.bad_word_seqs_len[bad_word_seq_number] - 1
                return tf.cond(tf.math.reduce_all(tf.math.equal(row_input_ids[-compare_len:], self.bad_word_seqs_ids[bad_word_seq_number, :compare_len])), lambda: tf.ones((), dtype=tf.bool), lambda: tf.zeros((), dtype=tf.bool))
            match = _len_one()
            return match
        match_mask = tf.map_fn(_tokens_match, tf.range(self.bad_word_seqs_ids.shape[0]), fn_output_signature=tf.bool)
        row_banned_tokens = self.seq_forbidden_tokens[match_mask]
        return row_banned_tokens
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        def _get_row_updated_score(row_inputs: Tuple[tf.Tensor]) -> tf.Tensor:
            row_input_ids, row_score = row_inputs
            banned_tokens = self._calc_row_banned_bad_tokens(row_input_ids[:cur_len])
            banned_tokens_mask = tf.scatter_nd(indices=tf.expand_dims(banned_tokens, axis=-1), updates=tf.ones_like(banned_tokens, dtype=tf.bool), shape=row_score.shape)
            row_score = tf.where(banned_tokens_mask, -float("inf"), row_score)
            return row_score
        scores = tf.map_fn(_get_row_updated_score, (input_ids, scores), fn_output_signature=tf.float32)
        return scores
class TFNoRepeatNGramLogitsProcessor(TFLogitsProcessor):
    def __init__(self, ngram_size: int):
        if not isinstance(ngram_size, int) or ngram_size <= 0: raise ValueError(f"`ngram_size` has to be a strictly positive integer, but is {ngram_size}")
        self.ngram_size = ngram_size
    def calc_banned_ngram_tokens(self, input_ids, num_hypos, cur_len):
        if cur_len + 1 < self.ngram_size: return [[] for _ in range(num_hypos)]
        generated_ngrams = [{} for _ in range(num_hypos)]
        prev_input_ids = input_ids[:, :cur_len]
        for idx in range(num_hypos):
            gen_tokens = prev_input_ids[idx].numpy().tolist()
            generated_ngram = generated_ngrams[idx]
            for ngram in zip(*[gen_tokens[i:] for i in range(self.ngram_size)]):
                prev_ngram_tuple = tuple(ngram[:-1])
                generated_ngram[prev_ngram_tuple] = generated_ngram.get(prev_ngram_tuple, []) + [ngram[-1]]
        def _get_generated_ngrams(hypo_idx):
            start_idx = cur_len + 1 - self.ngram_size
            ngram_idx = tuple(prev_input_ids[hypo_idx, start_idx:cur_len].numpy().tolist())
            return generated_ngrams[hypo_idx].get(ngram_idx, [])
        banned_tokens = [_get_generated_ngrams(hypo_idx) for hypo_idx in range(num_hypos)]
        return banned_tokens
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        if not tf.executing_eagerly(): raise NotImplementedError("TFNoRepeatNGramLogitsProcessor is only implemented for eager execution.")
        batch_size, vocab_size = scores.shape
        banned_tokens = self.calc_banned_ngram_tokens(input_ids, batch_size, cur_len)
        banned_tokens_indices_mask = []
        for banned_tokens_slice in banned_tokens: banned_tokens_indices_mask.append([True if token in banned_tokens_slice else False for token in range(vocab_size)])
        scores = tf.where(tf.convert_to_tensor(banned_tokens_indices_mask, dtype=tf.bool), -float("inf"), scores)
        return scores
class TFForcedBOSTokenLogitsProcessor(TFLogitsProcessor):
    def __init__(self, bos_token_id: int):
        if bos_token_id < 0: raise ValueError(f"The forced bos token id  must be a non-negative integer, got {bos_token_id}")
        self.bos_token_id = bos_token_id
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        if cur_len == 1:
            batch_size, num_tokens = scores.shape
            scores = tf.zeros((batch_size, 1))
            if self.bos_token_id > 0: scores = tf.concat((tf.broadcast_to(-float("inf"), (batch_size, self.bos_token_id)), scores), axis=-1)
            if self.bos_token_id < (num_tokens - 1): scores = tf.concat((scores, tf.broadcast_to(-float("inf"), (batch_size, (num_tokens - 1) - self.bos_token_id))), axis=-1)
        return scores
class TFForcedEOSTokenLogitsProcessor(TFLogitsProcessor):
    def __init__(self, max_length: int, eos_token_id: int):
        self.max_length = max_length
        if eos_token_id < 0: raise ValueError(f"The forced eos token id must be a non-negative integer, got {eos_token_id}")
        self.eos_token_id = eos_token_id
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        if cur_len == self.max_length - 1:
            batch_size, num_tokens = scores.shape
            scores = tf.zeros((batch_size, 1))
            if self.eos_token_id > 0: scores = tf.concat((tf.broadcast_to(-float("inf"), (batch_size, self.eos_token_id)), scores), axis=-1)
            if self.eos_token_id < (num_tokens - 1): scores = tf.concat((scores, tf.broadcast_to(-float("inf"), (batch_size, (num_tokens - 1) - self.eos_token_id))), axis=-1)
        return scores
class TFSuppressTokensAtBeginLogitsProcessor(TFLogitsProcessor):
    def __init__(self, begin_suppress_tokens, begin_index):
        self.begin_suppress_tokens = list(begin_suppress_tokens)
        self.begin_index = begin_index
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        suppressed_indices = []
        for token in self.begin_suppress_tokens:
            if token < scores.shape[-1]: suppressed_indices.extend([[i, token] for i in range(scores.shape[0])])
        if len(suppressed_indices) > 0: scores = tf.cond(tf.equal(cur_len, self.begin_index), lambda: tf.tensor_scatter_nd_update(scores, indices=suppressed_indices, updates=[-float("inf") for _ in range(scores.shape[0] * len(self.begin_suppress_tokens))]), lambda: scores)
        return scores
class TFSuppressTokensLogitsProcessor(TFLogitsProcessor):
    def __init__(self, suppress_tokens): self.suppress_tokens = list(suppress_tokens)
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        suppressed_indices = []
        for token in self.suppress_tokens:
            if token < scores.shape[-1]: suppressed_indices.extend([[i, token] for i in range(scores.shape[0])])
        if len(suppressed_indices) > 0: scores = tf.tensor_scatter_nd_update(scores, indices=[[i, token] for i in range(scores.shape[0]) for token in self.suppress_tokens], updates=[-float("inf") for _ in range(scores.shape[0] * len(self.suppress_tokens))])
        return scores
class TFForceTokensLogitsProcessor(TFLogitsProcessor):
    def __init__(self, force_token_map: List[List[int]]):
        force_token_map = dict(force_token_map)
        force_token_array = np.ones((max(force_token_map.keys()) + 1), dtype=np.int32) * -1
        for index, token in force_token_map.items():
            if token is not None: force_token_array[index] = token
        self.force_token_array = tf.convert_to_tensor(force_token_array, dtype=tf.int32)
    def __call__(self, input_ids: tf.Tensor, scores: tf.Tensor, cur_len: int) -> tf.Tensor:
        def _force_token(generation_idx):
            batch_size = scores.shape[0]
            current_token = self.force_token_array[generation_idx]
            new_scores = tf.zeros_like(scores, dtype=scores.dtype) + tf.constant([scores.dtype.min])
            indices = tf.stack((tf.range(batch_size), tf.tile([current_token], [batch_size])), axis=1)
            updates = tf.zeros((batch_size,), dtype=scores.dtype)
            new_scores = tf.tensor_scatter_nd_update(new_scores, indices, updates)
            return new_scores
        scores = tf.cond(tf.greater_equal(cur_len, tf.shape(self.force_token_array)[0]), lambda: tf.identity(scores), lambda: tf.cond(tf.greater_equal(self.force_token_array[cur_len], 0), lambda: _force_token(cur_len), lambda: scores))
        return scores
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
