from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import sapiens_transformers.sapiens_optimizer.sapiens_optimizer as sapiens_optimizer
from typing import (Dict, List, Tuple, Optional, Sequence)
from .sapiens_grammar import SapiensGrammar
from ._utils import suppress_stdout_stderr
from dataclasses import dataclass, field
from contextlib import ExitStack
from .sapiens_types import *
import numpy.typing as npt
import numpy as np
import ctypes
import os
class SapiensModel:
    def __init__(self, *, path_model: str, params: sapiens_optimizer.llama_model_params, verbose: bool = True):
        self.path_model = path_model
        self.params = params
        self.verbose = verbose
        self._exit_stack = ExitStack()
        model = None
        if not os.path.exists(path_model): raise ValueError(f"Model path does not exist: {path_model}")
        with suppress_stdout_stderr(disable=verbose): model = sapiens_optimizer.llama_load_model_from_file(self.path_model.encode("utf-8"), self.params)
        if model is None: raise ValueError(f"Failed to load model from file: {path_model}")
        self.model = model
        def free_model():
            if self.model is None: return
            sapiens_optimizer.llama_free_model(self.model)
            self.model = None
        self._exit_stack.callback(free_model)
    def close(self): self._exit_stack.close()
    def __del__(self): self.close()
    def vocab_type(self) -> int: return sapiens_optimizer.llama_vocab_type(self.model)
    def n_vocab(self) -> int: return sapiens_optimizer.llama_n_vocab(self.model)
    def n_ctx_train(self) -> int: return sapiens_optimizer.llama_n_ctx_train(self.model)
    def n_embd(self) -> int: return sapiens_optimizer.llama_n_embd(self.model)
    def rope_freq_scale_train(self) -> float: return sapiens_optimizer.llama_rope_freq_scale_train(self.model)
    def desc(self) -> str:
        buf = ctypes.create_string_buffer(1024)
        sapiens_optimizer.llama_model_desc(self.model, buf, 1024)
        return buf.value.decode("utf-8")
    def size(self) -> int: return sapiens_optimizer.llama_model_size(self.model)
    def n_params(self) -> int: return sapiens_optimizer.llama_model_n_params(self.model)
    def get_tensor(self, name: str) -> ctypes.c_void_p: return sapiens_optimizer.llama_get_model_tensor(self.model, name.encode("utf-8"))
    def token_get_text(self, token: int) -> str: return sapiens_optimizer.llama_token_get_text(self.model, token).decode("utf-8")
    def token_get_score(self, token: int) -> float: return sapiens_optimizer.llama_token_get_score(self.model, token)
    def token_get_attr(self, token: int) -> int: return sapiens_optimizer.llama_token_get_attr(self.model, token)
    def token_bos(self) -> int: return sapiens_optimizer.llama_token_bos(self.model)
    def token_eos(self) -> int: return sapiens_optimizer.llama_token_eos(self.model)
    def token_cls(self) -> int: return sapiens_optimizer.llama_token_cls(self.model)
    def token_sep(self) -> int: return sapiens_optimizer.llama_token_sep(self.model)
    def token_nl(self) -> int: return sapiens_optimizer.llama_token_nl(self.model)
    def token_prefix(self) -> int: return sapiens_optimizer.llama_token_prefix(self.model)
    def token_middle(self) -> int: return sapiens_optimizer.llama_token_middle(self.model)
    def token_suffix(self) -> int: return sapiens_optimizer.llama_token_suffix(self.model)
    def token_eot(self) -> int: return sapiens_optimizer.llama_token_eot(self.model)
    def add_bos_token(self) -> bool: return sapiens_optimizer.llama_add_bos_token(self.model)
    def add_eos_token(self) -> bool: return sapiens_optimizer.llama_add_eos_token(self.model)
    def tokenize(self, text: bytes, add_bos: bool, special: bool):
        n_ctx = self.n_ctx_train()
        tokens = (sapiens_optimizer.llama_token * n_ctx)()
        n_tokens = sapiens_optimizer.llama_tokenize(self.model, text, len(text), tokens, n_ctx, add_bos, special)
        if n_tokens < 0:
            n_tokens = abs(n_tokens)
            tokens = (sapiens_optimizer.llama_token * n_tokens)()
            n_tokens = sapiens_optimizer.llama_tokenize(self.model, text, len(text), tokens, n_tokens, add_bos, special)
            if n_tokens < 0: raise RuntimeError(f'Failed to tokenize: text="{text}" n_tokens={n_tokens}')
        return list(tokens[:n_tokens])
    def token_to_piece(self, token: int, special: bool = False) -> bytes:
        buf = ctypes.create_string_buffer(32)
        sapiens_optimizer.llama_token_to_piece(self.model, token, buf, 32, 0, special)
        return bytes(buf)
    def detokenize(self, tokens: List[int], special: bool = False) -> bytes:
        output = b""
        size = 32
        buffer = (ctypes.c_char * size)()
        for token in tokens:
            n = sapiens_optimizer.llama_token_to_piece(self.model, sapiens_optimizer.llama_token(token), buffer, size, 0, special)
            assert n <= size
            output += bytes(buffer[:n])
        return (output[1:] if len(tokens) > 0 and tokens[0] == self.token_bos() and output[0:1] == b" " else output)
    def metadata(self) -> Dict[str, str]:
        metadata: Dict[str, str] = {}
        buffer_size = 1024
        buffer = ctypes.create_string_buffer(buffer_size)
        buffer.value = b"\0" * buffer_size
        for i in range(sapiens_optimizer.llama_model_meta_count(self.model)):
            nbytes = sapiens_optimizer.llama_model_meta_key_by_index(self.model, i, buffer, buffer_size)
            if nbytes > buffer_size:
                buffer_size = nbytes + 1
                buffer = ctypes.create_string_buffer(buffer_size)
                nbytes = sapiens_optimizer.llama_model_meta_key_by_index(self.model, i, buffer, buffer_size)
            key = buffer.value.decode("utf-8")
            nbytes = sapiens_optimizer.llama_model_meta_val_str_by_index(self.model, i, buffer, buffer_size)
            if nbytes > buffer_size:
                buffer_size = nbytes + 1
                buffer = ctypes.create_string_buffer(buffer_size)
                nbytes = sapiens_optimizer.llama_model_meta_val_str_by_index(self.model, i, buffer, buffer_size)
            value = buffer.value.decode("utf-8")
            metadata[key] = value
        return metadata
    @staticmethod
    def default_params(): return sapiens_optimizer.llama_model_default_params()
class SapiensContext:
    def __init__(self, *, model: SapiensModel, params: sapiens_optimizer.llama_context_params, verbose: bool = True):
        self.model = model
        self.params = params
        self.verbose = verbose
        self._exit_stack = ExitStack()
        ctx = sapiens_optimizer.llama_new_context_with_model(self.model.model, self.params)
        if ctx is None: raise ValueError("Failed to create llama_context")
        self.ctx = ctx
        def free_ctx():
            if self.ctx is None: return
            sapiens_optimizer.llama_free(self.ctx)
            self.ctx = None
        self._exit_stack.callback(free_ctx)
    def close(self): self._exit_stack.close()
    def __del__(self): self.close()
    def n_ctx(self) -> int: return sapiens_optimizer.llama_n_ctx(self.ctx)
    def pooling_type(self) -> int: return sapiens_optimizer.llama_pooling_type(self.ctx)
    def kv_cache_clear(self): sapiens_optimizer.llama_kv_cache_clear(self.ctx)
    def kv_cache_seq_rm(self, seq_id: int, p0: int, p1: int): sapiens_optimizer.llama_kv_cache_seq_rm(self.ctx, seq_id, p0, p1)
    def kv_cache_seq_cp(self, seq_id_src: int, seq_id_dst: int, p0: int, p1: int): sapiens_optimizer.llama_kv_cache_seq_cp(self.ctx, seq_id_src, seq_id_dst, p0, p1)
    def kv_cache_seq_keep(self, seq_id: int): sapiens_optimizer.llama_kv_cache_seq_keep(self.ctx, seq_id)
    def kv_cache_seq_shift(self, seq_id: int, p0: int, p1: int, shift: int): sapiens_optimizer.llama_kv_cache_seq_add(self.ctx, seq_id, p0, p1, shift)
    def get_state_size(self) -> int: return sapiens_optimizer.llama_get_state_size(self.ctx)
    def decode(self, batch: SapiensBatch):
        return_code = sapiens_optimizer.llama_decode(self.ctx, batch.batch)
        if return_code != 0: raise RuntimeError(f"llama_decode returned {return_code}")
    def set_n_threads(self, n_threads: int, n_threads_batch: int): sapiens_optimizer.llama_set_n_threads(self.ctx, n_threads, n_threads_batch)
    def get_logits(self): return sapiens_optimizer.llama_get_logits(self.ctx)
    def get_logits_ith(self, i: int): return sapiens_optimizer.llama_get_logits_ith(self.ctx, i)
    def get_embeddings(self): return sapiens_optimizer.llama_get_embeddings(self.ctx)
    def set_rng_seed(self, seed: int): sapiens_optimizer.llama_set_rng_seed(self.ctx, seed)
    def sample_repetition_penalties(self, candidates: "_SapiensTokenDataArray", last_tokens_data: "sapiens_optimizer.Array[sapiens_optimizer.llama_token]",
    penalty_last_n: int, penalty_repeat: float, penalty_freq: float, penalty_present: float):
        sapiens_optimizer.llama_sample_repetition_penalties(self.ctx, sapiens_optimizer.byref(candidates.candidates), last_tokens_data, penalty_last_n,
        penalty_repeat, penalty_freq, penalty_present)
    def sample_softmax(self, candidates: "_SapiensTokenDataArray"): sapiens_optimizer.llama_sample_softmax(self.ctx, sapiens_optimizer.byref(candidates.candidates))
    def sample_top_k(self, candidates: "_SapiensTokenDataArray", k: int, min_keep: int): sapiens_optimizer.llama_sample_top_k(self.ctx, sapiens_optimizer.byref(candidates.candidates), k, min_keep)
    def sample_top_p(self, candidates: "_SapiensTokenDataArray", p: float, min_keep: int): sapiens_optimizer.llama_sample_top_p(self.ctx, sapiens_optimizer.byref(candidates.candidates), p, min_keep)
    def sample_min_p(self, candidates: "_SapiensTokenDataArray", p: float, min_keep: int): sapiens_optimizer.llama_sample_min_p(self.ctx, sapiens_optimizer.byref(candidates.candidates), p, min_keep)
    def sample_typical(self, candidates: "_SapiensTokenDataArray", p: float, min_keep: int): sapiens_optimizer.llama_sample_typical(self.ctx, sapiens_optimizer.byref(candidates.candidates), p, min_keep)
    def sample_temp(self, candidates: "_SapiensTokenDataArray", temp: float): sapiens_optimizer.llama_sample_temp(self.ctx, sapiens_optimizer.byref(candidates.candidates), temp)
    def sample_grammar(self, candidates: "_SapiensTokenDataArray", grammar: SapiensGrammar): sapiens_optimizer.llama_sample_grammar(self.ctx, sapiens_optimizer.byref(candidates.candidates), grammar.grammar)
    def sample_token_mirostat(self, candidates: "_SapiensTokenDataArray", tau: float, eta: float, m: int, mu: sapiens_optimizer.CtypesPointerOrRef[ctypes.c_float]) -> int: return sapiens_optimizer.llama_sample_token_mirostat(self.ctx,
    sapiens_optimizer.byref(candidates.candidates), tau, eta, m, mu)
    def sample_token_mirostat_v2(self, candidates: "_SapiensTokenDataArray", tau: float, eta: float, mu: sapiens_optimizer.CtypesPointerOrRef[ctypes.c_float]) -> int: return sapiens_optimizer.llama_sample_token_mirostat_v2(self.ctx,
    sapiens_optimizer.byref(candidates.candidates), tau, eta, mu)
    def sample_token_greedy(self, candidates: "_SapiensTokenDataArray") -> int: return sapiens_optimizer.llama_sample_token_greedy(self.ctx, sapiens_optimizer.byref(candidates.candidates))
    def sample_token(self, candidates: "_SapiensTokenDataArray") -> int: return sapiens_optimizer.llama_sample_token(self.ctx, sapiens_optimizer.byref(candidates.candidates))
    def grammar_accept_token(self, grammar: SapiensGrammar, token: int): sapiens_optimizer.sapiens_grammar_accept_token(grammar.grammar, self.ctx, token)
    def reset_timings(self): sapiens_optimizer.llama_perf_context_reset(self.ctx)
    def print_timings(self): sapiens_optimizer.llama_perf_context_print(self.ctx)
    @staticmethod
    def default_params(): return sapiens_optimizer.llama_context_default_params()
class SapiensBatch:
    def __init__(self, *, n_tokens: int, embd: int, n_seq_max: int, verbose: bool = True):
        self._n_tokens = n_tokens
        self.embd = embd
        self.n_seq_max = n_seq_max
        self.verbose = verbose
        self._exit_stack = ExitStack()
        batch = sapiens_optimizer.llama_batch_init(self._n_tokens, self.embd, self.n_seq_max)
        if batch is None: raise ValueError("Failed to create llama_batch")
        self.batch = batch
        def free_batch():
            if self.batch is None: return
            sapiens_optimizer.llama_batch_free(self.batch)
            self.batch = None
        self._exit_stack.callback(free_batch)
    def close(self): self._exit_stack.close()
    def __del__(self): self.close()
    def n_tokens(self) -> int: return self.batch.n_tokens
    def reset(self): self.batch.n_tokens = 0
    def set_batch(self, batch: Sequence[int], n_past: int, logits_all: bool):
        n_tokens = len(batch)
        self.batch.n_tokens = n_tokens
        for i in range(n_tokens):
            self.batch.token[i] = batch[i]
            self.batch.pos[i] = n_past + i
            self.batch.seq_id[i][0] = 0
            self.batch.n_seq_id[i] = 1
            self.batch.logits[i] = logits_all
        self.batch.logits[n_tokens - 1] = True
    def add_sequence(self, batch: Sequence[int], seq_id: int, logits_all: bool):
        n_tokens = len(batch)
        n_tokens0 = self.batch.n_tokens
        self.batch.n_tokens += n_tokens
        for i in range(n_tokens):
            j = n_tokens0 + i
            self.batch.token[j] = batch[i]
            self.batch.pos[j] = i
            self.batch.seq_id[j][0] = seq_id
            self.batch.n_seq_id[j] = 1
            self.batch.logits[j] = logits_all
        self.batch.logits[n_tokens - 1] = True
class SapiensTokenDataArray:
    def __init__(self, *, n_vocab: int):
        self.n_vocab = n_vocab
        self.candidates_data = np.recarray((self.n_vocab,), dtype=np.dtype([("id", np.intc), ("logit", np.single), ("p", np.single)], align=True))
        self.candidates = sapiens_optimizer.llama_token_data_array(data=self.candidates_data.ctypes.data_as(sapiens_optimizer.llama_token_data_p), size=self.n_vocab, sorted=False)
        self.default_candidates_data_id = np.arange(self.n_vocab, dtype=np.intc)
        self.default_candidates_data_p = np.zeros(self.n_vocab, dtype=np.single)
    def copy_logits(self, logits: npt.NDArray[np.single]):
        self.candidates_data.id[:] = self.default_candidates_data_id
        self.candidates_data.logit[:] = logits
        self.candidates_data.p[:] = self.default_candidates_data_p
        self.candidates.sorted = False
        self.candidates.size = self.n_vocab
def normalize_embedding(embedding):
    norm = float(np.linalg.norm(embedding))
    if norm == 0.0: return embedding
    return [v / norm for v in embedding]
@dataclass
class SapiensSamplingParams:
    n_prev: int = 64
    n_probs: int = 0
    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    tfs_z: float = 1.00
    typical_p: float = 1.00
    temp: float = 0.80
    penalty_last_n: int = 64
    penalty_repeat: float = 1.0
    penalty_freq: float = 0.00
    penalty_present: float = 0.00
    mirostat: int = 0
    mirostat_tau: float = 5.00
    mirostat_eta: float = 0.10
    penalize_nl: bool = True
    grammar: str = ""
    cfg_negative_prompt: str = ""
    cfg_scale: float = 1.00
    logit_bias: dict[int, float] = field(default_factory=dict)
@dataclass
class SapiensSamplingContext:
    params: SapiensSamplingParams = field(default_factory=SapiensSamplingParams)
    mirostat_mu: ctypes.c_float = field(default_factory=ctypes.c_float)
    grammar: Optional[SapiensGrammar] = None
    prev: list[int] = field(default_factory=list)
    cur: list[sapiens_optimizer.llama_token_data] = field(default_factory=list)
    def reset(self):
        self.prev = []
        self.cur = []
        if self.grammar is not None: self.grammar.reset()
    def cp(self): return SapiensSamplingContext(params=self.params, mirostat_mu=self.mirostat_mu, grammar=self.grammar, prev=self.prev.copy(), cur=self.cur.copy())
    def last(self) -> Optional[int]:
        if len(self.prev) > 0: return self.prev[-1]
        else: return None
    def prev_str(self, ctx_main: SapiensContext, n: int) -> str: return ctx_main.model.detokenize(self.prev[-n:]).decode("utf-8")
    def sample(self, ctx_main: SapiensContext, idx: int = 0, logits_array: Optional[npt.NDArray[np.single]] = None):
        n_vocab = ctx_main.model.n_vocab()
        id: int = 0
        if logits_array is None:
            logits = ctx_main.get_logits_ith(idx)
            logits_array = np.array(ctypes.cast(logits, ctypes.POINTER(ctypes.c_float * n_vocab)).contents, dtype=np.single)
        for token, logit_bias in self.params.logit_bias.items(): logits_array[token] += logit_bias
        token_data_array = SapiensTokenDataArray(n_vocab=n_vocab)
        token_data_array.copy_logits(logits_array)
        if len(self.prev) > 0:
            nl_token = ctx_main.model.token_nl()
            nl_logit = logits_array[nl_token]
            last_tokens = self.prev[-self.params.penalty_last_n :]
            last_tokens_size = min(len(last_tokens), self.params.penalty_last_n)
            if last_tokens_size > 0:
                last_tokens_p = (sapiens_optimizer.llama_token * len(last_tokens))(*last_tokens)
                ctx_main.sample_repetition_penalties(token_data_array, last_tokens_p, last_tokens_size, self.params.penalty_repeat, self.params.penalty_freq, self.params.penalty_present)
            if not self.params.penalize_nl: token_data_array.candidates_data.logit[nl_token] = nl_logit
        if self.grammar is not None: ctx_main.sample_grammar(token_data_array, self.grammar)
        if self.params.temp < 0:
            ctx_main.sample_softmax(token_data_array)
            id = token_data_array.candidates_data.id[0]
        elif self.params.temp == 0: id = ctx_main.sample_token_greedy(token_data_array)
        else:
            if self.params.mirostat == 1:
                mirostat_m = 100
                ctx_main.sample_temp(token_data_array, self.params.temp)
                id = ctx_main.sample_token_mirostat(token_data_array, self.params.mirostat_tau, self.params.mirostat_eta, mirostat_m, ctypes.pointer(self.mirostat_mu))
            elif self.params.mirostat == 2:
                ctx_main.sample_temp(token_data_array, self.params.temp)
                id = ctx_main.sample_token_mirostat_v2(token_data_array, self.params.mirostat_tau, self.params.mirostat_eta, ctypes.pointer(self.mirostat_mu))
            else:
                min_keep = max(1, self.params.n_probs)
                ctx_main.sample_top_k(token_data_array, self.params.top_k, min_keep=min_keep)
                ctx_main.sample_typical(token_data_array, self.params.typical_p, min_keep=min_keep)
                ctx_main.sample_top_p(token_data_array, self.params.top_p, min_keep=min_keep)
                ctx_main.sample_min_p(token_data_array, self.params.min_p, min_keep=min_keep)
                ctx_main.sample_temp(token_data_array, self.params.temp)
                id = ctx_main.sample_token(token_data_array)
        return id
    def accept(self, ctx_main: SapiensContext, id: int, apply_grammar: bool):
        if apply_grammar and self.grammar is not None: ctx_main.grammar_accept_token(self.grammar, id)
        self.prev.append(id)
from typing import List, Callable, Optional, Union
import ctypes
import sapiens_transformers.sapiens_optimizer
class CustomSampler:
    def __init__(self, apply_func: typing.Callable[[sapiens_optimizer.llama_token_data_array], None]):
        self.apply_func = apply_func
        def apply_wrapper(sampler: sapiens_optimizer.llama_sampler_p, cur_p: sapiens_optimizer.llama_token_data_array_p): self.apply_func(cur_p)
        def free_wrapper(sampler: sapiens_optimizer.llama_sampler_p): pass
        sampler_i = sapiens_optimizer.llama_sampler_i()
        sampler_i.apply = sapiens_optimizer.llama_sampler_i_apply(apply_wrapper)
        self._apply_wrapper_ref = apply_wrapper
        sampler_i.name = sapiens_optimizer.llama_sampler_i_name(0)
        sampler_i.accept = sapiens_optimizer.llama_sampler_i_accept(0)
        sampler_i.reset = sapiens_optimizer.llama_sampler_i_reset(0)
        sampler_i.clone = sapiens_optimizer.llama_sampler_i_clone(0)
        sampler_i.free = sapiens_optimizer.llama_sampler_i_free(0)
        self.sampler = sapiens_optimizer.llama_sampler()
        self.sampler.iface = ctypes.pointer(sampler_i)
        self.sampler.ctx = None
    def get_sampler(self) -> sapiens_optimizer.llama_sampler_p: return ctypes.pointer(self.sampler)
class SapiensSampler:
    def __init__(self):
        params = sapiens_optimizer.llama_sampler_chain_params()
        self.sampler = sapiens_optimizer.llama_sampler_chain_init(params)
        self.samplers: List[sapiens_optimizer.llama_sampler_p] = []
        self.custom_samplers: List[Tuple[int, CustomSampler]] = []
    def add_greedy(self):
        sampler = sapiens_optimizer.llama_sampler_init_greedy()
        self._add_sampler(sampler)
    def add_dist(self, seed: int):
        sampler = sapiens_optimizer.llama_sampler_init_dist(seed)
        self._add_sampler(sampler)
    def add_softmax(self):
        sampler = sapiens_optimizer.llama_sampler_init_softmax()
        self._add_sampler(sampler)
    def add_top_k(self, k: int):
        sampler = sapiens_optimizer.llama_sampler_init_top_k(k)
        self._add_sampler(sampler)
    def add_top_p(self, p: float, min_keep: int):
        sampler = sapiens_optimizer.llama_sampler_init_top_p(p, min_keep)
        self._add_sampler(sampler)
    def add_min_p(self, p: float, min_keep: int):
        sampler = sapiens_optimizer.llama_sampler_init_min_p(p, min_keep)
        self._add_sampler(sampler)
    def add_typical(self, p: float, min_keep: int):
        sampler = sapiens_optimizer.llama_sampler_init_typical(p, min_keep)
        self._add_sampler(sampler)
    def add_temp(self, temp: float):
        sampler = sapiens_optimizer.llama_sampler_init_temp(temp)
        self._add_sampler(sampler)
    def add_temp_ext(self, t: float, delta: float, exponent: float):
        sampler = sapiens_optimizer.llama_sampler_init_temp_ext(t, delta, exponent)
        self._add_sampler(sampler)
    def add_mirostat(self, n_vocab: int, seed: int, tau: float, eta: float, m: int):
        sampler = sapiens_optimizer.llama_sampler_init_mirostat(n_vocab, seed, tau, eta, m)
        self._add_sampler(sampler)
    def add_mirostat_v2(self, seed: int, tau: float, eta: float):
        sampler = sapiens_optimizer.llama_sampler_init_mirostat_v2(seed, tau, eta)
        self._add_sampler(sampler)
    def add_grammar(self, model: SapiensModel, grammar: SapiensGrammar):
        sampler = sapiens_optimizer.llama_sampler_init_grammar(model.model, grammar._grammar.encode("utf-8"), grammar._root.encode("utf-8"))
        self._add_sampler(sampler)
    def add_penalties(self, n_vocab: int, special_eos_id: int, linefeed_id: int, penalty_last_n: int, penalty_repeat: float, penalty_freq: float,
    penalty_present: float, penalize_nl: bool, ignore_eos: bool):
        sampler = sapiens_optimizer.llama_sampler_init_penalties(penalty_last_n, penalty_repeat, penalty_freq, penalty_present)
        self._add_sampler(sampler)
    def init_logit_bias(self, n_vocab: int, n_logit_bias, logit_bias: sapiens_optimizer.llama_logit_bias_p):
        sampler = sapiens_optimizer.llama_sampler_init_logit_bias(n_vocab, n_logit_bias, logit_bias)
        self._add_sampler(sampler)
    def add_custom(self, apply_func: Callable[[sapiens_optimizer.llama_token_data_array], None]):
        custom_sampler = CustomSampler(apply_func)
        sampler = custom_sampler.get_sampler()
        self._add_sampler(sampler)
        self.custom_samplers.append((sapiens_optimizer.llama_sampler_chain_n(self.sampler) - 1, custom_sampler))
    def _add_sampler(self, sampler: sapiens_optimizer.llama_sampler_p):
        assert self.sampler is not None
        sapiens_optimizer.llama_sampler_chain_add(self.sampler, sampler)
        self.samplers.append(sampler)
    def get_seed(self) -> int:
        assert self.sampler is not None
        return sapiens_optimizer.llama_sampler_get_seed(self.sampler)
    def sample(self, ctx: SapiensContext, idx: int) -> int:
        assert self.sampler is not None
        return sapiens_optimizer.llama_sampler_sample(self.sampler, ctx.ctx, idx)
    def close(self):
        if self.sampler:
            for i, _ in reversed(self.custom_samplers): sapiens_optimizer.llama_sampler_chain_remove(self.sampler, i)
            sapiens_optimizer.llama_sampler_free(self.sampler)
            self.sampler = None
        self.samplers.clear()
        self.custom_samplers.clear()
    def __del__(self): self.close()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
