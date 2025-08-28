from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ._ctypes_extensions import (load_shared_library, byref, ctypes_function_for_shared_library)
from typing import (Callable, Union, NewType, Optional, TYPE_CHECKING)
import pathlib
import ctypes
import os
if TYPE_CHECKING: from ._ctypes_extensions import (CtypesCData, CtypesArray, CtypesPointer, CtypesVoidPointer, CtypesRef, CtypesPointerOrRef, CtypesFuncPointer)
def get_package_installation_directory(package_name="llama_cpp"):
    try:
        import importlib.util
        import sys
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin: return os.path.dirname(spec.origin)
        else: return pathlib.Path(os.path.abspath(os.path.dirname(__file__))) / "lib"
    except: return pathlib.Path(os.path.abspath(os.path.dirname(__file__))) / "lib"
_lib_base_name = "llama"
_override_base_path = os.environ.get("SAPIENS_CPP_LIB_PATH")
_base_path = pathlib.Path(get_package_installation_directory()) / "lib" if _override_base_path is None else pathlib.Path(_override_base_path)
_lib = load_shared_library(_lib_base_name, _base_path)
ctypes_function = ctypes_function_for_shared_library(_lib)
GGML_TYPE_F32 = 0
GGML_TYPE_F16 = 1
GGML_TYPE_Q4_0 = 2
GGML_TYPE_Q4_1 = 3
GGML_TYPE_Q5_0 = 6
GGML_TYPE_Q5_1 = 7
GGML_TYPE_Q8_0 = 8
GGML_TYPE_Q8_1 = 9
GGML_TYPE_Q2_K = 10
GGML_TYPE_Q3_K = 11
GGML_TYPE_Q4_K = 12
GGML_TYPE_Q5_K = 13
GGML_TYPE_Q6_K = 14
GGML_TYPE_Q8_K = 15
GGML_TYPE_IQ2_XXS = 16
GGML_TYPE_IQ2_XS = 17
GGML_TYPE_IQ3_XXS = 18
GGML_TYPE_IQ1_S = 19
GGML_TYPE_IQ4_NL = 20
GGML_TYPE_IQ3_S = 21
GGML_TYPE_IQ2_S = 22
GGML_TYPE_IQ4_XS = 23
GGML_TYPE_I8 = 24
GGML_TYPE_I16 = 25
GGML_TYPE_I32 = 26
GGML_TYPE_I64 = 27
GGML_TYPE_F64 = 28
GGML_TYPE_IQ1_M = 29
GGML_TYPE_COUNT = 30
ggml_backend_sched_eval_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)
ggml_abort_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)
_lib.llama_max_devices.argtypes = []
_lib.llama_max_devices.restype = ctypes.c_size_t
SAPIENS_MAX_DEVICES = _lib.llama_max_devices()
SAPIENS_DEFAULT_SEED = 0xFFFFFFFF
SAPIENS_TOKEN_NULL = -1
SAPIENS_FILE_MAGIC_GGLA = 0x67676C61
SAPIENS_FILE_MAGIC_GGSN = 0x6767736E
SAPIENS_FILE_MAGIC_GGSQ = 0x67677371
SAPIENS_SESSION_MAGIC = SAPIENS_FILE_MAGIC_GGSN
SAPIENS_SESSION_VERSION = 9
SAPIENS_STATE_SEQ_MAGIC = SAPIENS_FILE_MAGIC_GGSQ
SAPIENS_STATE_SEQ_VERSION = 2
llama_model_p = NewType("llama_model_p", int)
llama_model_p_ctypes = ctypes.c_void_p
llama_context_p = NewType("llama_context_p", int)
llama_context_p_ctypes = ctypes.c_void_p
llama_pos = ctypes.c_int32
llama_token = ctypes.c_int32
llama_token_p = ctypes.POINTER(llama_token)
llama_seq_id = ctypes.c_int32
SAPIENS_VOCAB_TYPE_NONE = 0
SAPIENS_VOCAB_TYPE_SPM = 1
SAPIENS_VOCAB_TYPE_BPE = 2
SAPIENS_VOCAB_TYPE_WPM = 3
SAPIENS_VOCAB_TYPE_UGM = 4
SAPIENS_VOCAB_TYPE_RWKV = 5
SAPIENS_VOCAB_PRE_TYPE_DEFAULT = 0
SAPIENS_VOCAB_PRE_TYPE_SAPIENS = 1
SAPIENS_VOCAB_PRE_TYPE_DEEPSEEK_LLM = 2
SAPIENS_VOCAB_PRE_TYPE_DEEPSEEK_CODER = 3
SAPIENS_VOCAB_PRE_TYPE_FALCON = 4
SAPIENS_VOCAB_PRE_TYPE_MPT = 5
SAPIENS_VOCAB_PRE_TYPE_STARCODER = 6
SAPIENS_VOCAB_PRE_TYPE_GPT2 = 7
SAPIENS_VOCAB_PRE_TYPE_REFACT = 8
SAPIENS_VOCAB_PRE_TYPE_COMMAND_R = 9
SAPIENS_VOCAB_PRE_TYPE_STABLELM2 = 10
SAPIENS_VOCAB_PRE_TYPE_QWEN2 = 11
SAPIENS_VOCAB_PRE_TYPE_OLMO = 12
SAPIENS_VOCAB_PRE_TYPE_DBRX = 13
SAPIENS_VOCAB_PRE_TYPE_SMAUG = 14
SAPIENS_VOCAB_PRE_TYPE_PORO = 15
SAPIENS_VOCAV_PRE_TYPE_CHATGLM3 = 16
SAPIENS_VOCAB_PRE_TYPE_CHATGLM4 = 17
SAPIENS_VOCAB_PRE_TYPE_VIKING = 18
SAPIENS_VOCAB_PRE_TYPE_JAIS = 19
SAPIENS_VOCAB_PRE_TYPE_TEKKEN = 20
SAPIENS_VOCAB_PRE_TYPE_SMOLLM = 21
SAPIENS_VOCAB_PRE_TYPE_CODESHELL = 22
SAPIENS_VOCAB_PRE_TYPE_BLOOM = 23
SAPIENS_VOCAB_PRE_TYPE_GPT3_FINNISH = 24
SAPIENS_VOCAB_PRE_TYPE_EXAONE = 25
SAPIENS_VOCAB_PRE_TYPE_CHAMELEON = 26
SAPIENS_VOCAB_PRE_TYPE_MINERVA = 27
SAPIENS_VOCAB_PRE_TYPE_DEEPSEEK3_LLM = 28
SAPIENS_ROPE_TYPE_NONE = -1
SAPIENS_ROPE_TYPE_NORM = 0
SAPIENS_ROPE_TYPE_NEOX = GGML_ROPE_TYPE_NEOX = 2
SAPIENS_ROPE_TYPE_MROPE = GGML_ROPE_TYPE_MROPE = 8
SAPIENS_ROPE_TYPE_VISION = GGML_ROPE_TYPE_VISION = 24
SAPIENS_TOKEN_TYPE_UNDEFINED = 0
SAPIENS_TOKEN_TYPE_NORMAL = 1
SAPIENS_TOKEN_TYPE_UNKNOWN = 2
SAPIENS_TOKEN_TYPE_CONTROL = 3
SAPIENS_TOKEN_TYPE_USER_DEFINED = 4
SAPIENS_TOKEN_TYPE_UNUSED = 5
SAPIENS_TOKEN_TYPE_BYTE = 6
SAPIENS_TOKEN_ATTR_UNDEFINED = 0
SAPIENS_TOKEN_ATTR_UNKNOWN = 1 << 0
SAPIENS_TOKEN_ATTR_UNUSED = 1 << 1
SAPIENS_TOKEN_ATTR_NORMAL = 1 << 2
SAPIENS_TOKEN_ATTR_CONTROL = 1 << 3
SAPIENS_TOKEN_ATTR_USER_DEFINED = 1 << 4
SAPIENS_TOKEN_ATTR_BYTE = 1 << 5
SAPIENS_TOKEN_ATTR_NORMALIZED = 1 << 6
SAPIENS_TOKEN_ATTR_LSTRIP = 1 << 7
SAPIENS_TOKEN_ATTR_RSTRIP = 1 << 8
SAPIENS_TOKEN_ATTR_SINGLE_WORD = 1 << 9
SAPIENS_FTYPE_ALL_F32 = 0
SAPIENS_FTYPE_MOSTLY_F16 = 1
SAPIENS_FTYPE_MOSTLY_Q4_0 = 2
SAPIENS_FTYPE_MOSTLY_Q4_1 = 3
SAPIENS_FTYPE_MOSTLY_Q8_0 = 7
SAPIENS_FTYPE_MOSTLY_Q5_0 = 8
SAPIENS_FTYPE_MOSTLY_Q5_1 = 9
SAPIENS_FTYPE_MOSTLY_Q2_K = 10
SAPIENS_FTYPE_MOSTLY_Q3_K_S = 11
SAPIENS_FTYPE_MOSTLY_Q3_K_M = 12
SAPIENS_FTYPE_MOSTLY_Q3_K_L = 13
SAPIENS_FTYPE_MOSTLY_Q4_K_S = 14
SAPIENS_FTYPE_MOSTLY_Q4_K_M = 15
SAPIENS_FTYPE_MOSTLY_Q5_K_S = 16
SAPIENS_FTYPE_MOSTLY_Q5_K_M = 17
SAPIENS_FTYPE_MOSTLY_Q6_K = 18
SAPIENS_FTYPE_MOSTLY_IQ2_XXS = 19
SAPIENS_FTYPE_MOSTLY_IQ2_XS = 20
SAPIENS_FTYPE_MOSTLY_Q2_K_S = 21
SAPIENS_FTYPE_MOSTLY_IQ3_XS = 22
SAPIENS_FTYPE_MOSTLY_IQ3_XXS = 23
SAPIENS_FTYPE_MOSTLY_IQ1_S = 24
SAPIENS_FTYPE_MOSTLY_IQ4_NL = 25
SAPIENS_FTYPE_MOSTLY_IQ3_S = 26
SAPIENS_FTYPE_MOSTLY_IQ3_M = 27
SAPIENS_FTYPE_MOSTLY_IQ2_S = 28
SAPIENS_FTYPE_MOSTLY_IQ2_M = 29
SAPIENS_FTYPE_MOSTLY_IQ4_XS = 30
SAPIENS_FTYPE_MOSTLY_IQ1_M = 31
SAPIENS_FTYPE_MOSTLY_BF16 = 32
SAPIENS_FTYPE_MOSTLY_TQ1_0 = 36
SAPIENS_FTYPE_MOSTLY_TQ2_0 = 37
SAPIENS_FTYPE_GUESSED = 1024
SAPIENS_ROPE_SCALING_TYPE_UNSPECIFIED = -1
SAPIENS_ROPE_SCALING_TYPE_NONE = 0
SAPIENS_ROPE_SCALING_TYPE_LINEAR = 1
SAPIENS_ROPE_SCALING_TYPE_YARN = 2
SAPIENS_ROPE_SCALING_TYPE_LONGROPE = 3
SAPIENS_ROPE_SCALING_TYPE_MAX_VALUE = SAPIENS_ROPE_SCALING_TYPE_YARN
SAPIENS_POOLING_TYPE_UNSPECIFIED = -1
SAPIENS_POOLING_TYPE_NONE = 0
SAPIENS_POOLING_TYPE_MEAN = 1
SAPIENS_POOLING_TYPE_CLS = 2
SAPIENS_POOLING_TYPE_LAST = 3
SAPIENS_POOLING_TYPE_RANK = 4
SAPIENS_ATTENTION_TYPE_UNSPECIFIED = -1
SAPIENS_ATTENTION_TYPE_CAUSAL = 0
SAPIENS_ATTENTION_TYPE_NON_CAUSAL = 1
SAPIENS_SPLIT_MODE_NONE = 0
SAPIENS_SPLIT_MODE_LAYER = 1
SAPIENS_SPLIT_MODE_ROW = 2
class llama_token_data(ctypes.Structure):
    if TYPE_CHECKING:
        id: llama_token
        logit: float
        p: float
    _fields_ = [("id", llama_token), ("logit", ctypes.c_float), ("p", ctypes.c_float)]
llama_token_data_p = ctypes.POINTER(llama_token_data)
class llama_token_data_array(ctypes.Structure):
    if TYPE_CHECKING:
        data: CtypesArray[llama_token_data]
        size: int
        selected: int
        sorted: bool
    _fields_ = [("data", llama_token_data_p), ("size", ctypes.c_size_t), ("selected", ctypes.c_int64), ("sorted", ctypes.c_bool)]
llama_token_data_array_p = ctypes.POINTER(llama_token_data_array)
llama_progress_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_float, ctypes.c_void_p)
class llama_batch(ctypes.Structure):
    if TYPE_CHECKING:
        n_tokens: int
        token: CtypesArray[llama_token]
        embd: CtypesArray[ctypes.c_float]
        pos: CtypesArray[CtypesArray[llama_pos]]
        n_seq_id: CtypesArray[ctypes.c_int]
        seq_id: CtypesArray[CtypesArray[llama_seq_id]]
        logits: CtypesArray[ctypes.c_int8]
    _fields_ = [("n_tokens", ctypes.c_int32), ("token", ctypes.POINTER(llama_token)), ("embd", ctypes.POINTER(ctypes.c_float)), ("pos", ctypes.POINTER(llama_pos)),
    ("n_seq_id", ctypes.POINTER(ctypes.c_int32)), ("seq_id", ctypes.POINTER(ctypes.POINTER(llama_seq_id))), ("logits", ctypes.POINTER(ctypes.c_int8))]
SAPIENS_KV_OVERRIDE_TYPE_INT = 0
SAPIENS_KV_OVERRIDE_TYPE_FLOAT = 1
SAPIENS_KV_OVERRIDE_TYPE_BOOL = 2
SAPIENS_KV_OVERRIDE_TYPE_STR = 3
class llama_model_kv_override_value(ctypes.Union):
    _fields_ = [("val_i64", ctypes.c_int64), ("val_f64", ctypes.c_double), ("val_bool", ctypes.c_bool), ("val_str", ctypes.c_char * 128)]
    if TYPE_CHECKING:
        val_i64: int
        val_f64: float
        val_bool: bool
        val_str: bytes
class llama_model_kv_override(ctypes.Structure):
    _fields_ = [("tag", ctypes.c_int), ("key", ctypes.c_char * 128), ("value", llama_model_kv_override_value)]
    if TYPE_CHECKING:
        tag: int
        key: bytes
        value: Union[int, float, bool, bytes]
class llama_model_params(ctypes.Structure):
    if TYPE_CHECKING:
        n_gpu_layers: int
        split_mode: int
        main_gpu: int
        tensor_split: CtypesArray[ctypes.c_float]
        rpc_servers: ctypes.c_char_p
        progress_callback: Callable[[float, ctypes.c_void_p], bool]
        progress_callback_user_data: ctypes.c_void_p
        kv_overrides: CtypesArray[llama_model_kv_override]
        vocab_only: bool
        use_mmap: bool
        use_mlock: bool
        check_tensors: bool
    _fields_ = [("devices", ctypes.c_void_p), ("n_gpu_layers", ctypes.c_int32), ("split_mode", ctypes.c_int), ("main_gpu", ctypes.c_int32), ("tensor_split", ctypes.POINTER(ctypes.c_float)),
    ("rpc_servers", ctypes.c_char_p), ("progress_callback", llama_progress_callback), ("progress_callback_user_data", ctypes.c_void_p), ("kv_overrides", ctypes.POINTER(llama_model_kv_override)),
    ("vocab_only", ctypes.c_bool), ("use_mmap", ctypes.c_bool), ("use_mlock", ctypes.c_bool), ("check_tensors", ctypes.c_bool)]
class llama_context_params(ctypes.Structure):
    if TYPE_CHECKING:
        n_ctx: int
        n_batch: int
        n_ubatch: int
        n_seq_max: int
        n_threads: int
        n_threads_batch: int
        rope_scaling_type: int
        pooling_type: int
        attention_type: int
        rope_freq_base: float
        rope_freq_scale: float
        yarn_ext_factor: float
        yarn_attn_factor: float
        yarn_beta_fast: float
        yarn_beta_slow: float
        yarn_orig_ctx: int
        defrag_thold: float
        cb_eval: Callable[[ctypes.c_void_p, bool], bool]
        cb_eval_user_data: ctypes.c_void_p
        type_k: int
        type_v: int
        logits_all: bool
        embeddings: bool
        offload_kqv: bool
        flash_attn: bool
        abort_callback: Callable[[ctypes.c_void_p], bool]
        abort_callback_data: ctypes.c_void_p
    _fields_ = [("n_ctx", ctypes.c_uint32), ("n_batch", ctypes.c_uint32), ("n_ubatch", ctypes.c_uint32), ("n_seq_max", ctypes.c_uint32), ("n_threads", ctypes.c_int32),
    ("n_threads_batch", ctypes.c_int32), ("rope_scaling_type", ctypes.c_int), ("pooling_type", ctypes.c_int), ("attention_type", ctypes.c_int), ("rope_freq_base", ctypes.c_float),
    ("rope_freq_scale", ctypes.c_float), ("yarn_ext_factor", ctypes.c_float), ("yarn_attn_factor", ctypes.c_float), ("yarn_beta_fast", ctypes.c_float), ("yarn_beta_slow", ctypes.c_float),
    ("yarn_orig_ctx", ctypes.c_uint32), ("defrag_thold", ctypes.c_float), ("cb_eval", ggml_backend_sched_eval_callback), ("cb_eval_user_data", ctypes.c_void_p), ("type_k", ctypes.c_int),
    ("type_v", ctypes.c_int), ("logits_all", ctypes.c_bool), ("embeddings", ctypes.c_bool), ("offload_kqv", ctypes.c_bool), ("flash_attn", ctypes.c_bool), ("abort_callback", ggml_abort_callback),
    ("abort_callback_data", ctypes.c_void_p)]
llama_log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)
class llama_model_quantize_params(ctypes.Structure):
    if TYPE_CHECKING:
        nthread: int
        ftype: int
        output_tensor_type: int
        token_embedding_type: int
        allow_requantize: bool
        quantize_output_tensor: bool
        only_copy: bool
        pure: bool
        keep_split: bool
        imatrix: ctypes.c_void_p
        kv_overrides: ctypes.c_void_p
    _fields_ = [("nthread", ctypes.c_int32), ("ftype", ctypes.c_int), ("output_tensor_type", ctypes.c_int), ("token_embedding_type", ctypes.c_int),
    ("allow_requantize", ctypes.c_bool), ("quantize_output_tensor", ctypes.c_bool), ("only_copy", ctypes.c_bool), ("pure", ctypes.c_bool),
    ("keep_split", ctypes.c_bool), ("imatrix", ctypes.c_void_p), ("kv_overrides", ctypes.c_void_p)]
class llama_logit_bias(ctypes.Structure):
    if TYPE_CHECKING:
        token: llama_token
        bias: float
    _fields_ = [("token", llama_token), ("bias", ctypes.c_float)]
llama_logit_bias_p = ctypes.POINTER(llama_logit_bias)
class llama_sampler_chain_params(ctypes.Structure):
    if TYPE_CHECKING: no_perf: bool
    _fields_ = [("no_perf", ctypes.c_bool)]
class llama_chat_message(ctypes.Structure):
    _fields_ = [("role", ctypes.c_char_p), ("content", ctypes.c_char_p)]
llama_lora_adapter_p = ctypes.c_void_p
llama_lora_adapter_p_ctypes = ctypes.POINTER(ctypes.c_void_p)
@ctypes_function("llama_model_default_params", [], llama_model_params)
def llama_model_default_params() -> llama_model_params: ...
@ctypes_function("llama_context_default_params", [], llama_context_params)
def llama_context_default_params() -> llama_context_params: ...
@ctypes_function("llama_sampler_chain_default_params", [], llama_sampler_chain_params)
def llama_sampler_chain_default_params() -> llama_sampler_chain_params: ...
@ctypes_function("llama_model_quantize_default_params", [], llama_model_quantize_params)
def llama_model_quantize_default_params() -> llama_model_quantize_params: ...
@ctypes_function("llama_backend_init", [], None)
def llama_backend_init(): ...
GGML_NUMA_STRATEGY_DISABLED = 0
GGML_NUMA_STRATEGY_DISTRIBUTE = 1
GGML_NUMA_STRATEGY_ISOLATE = 2
GGML_NUMA_STRATEGY_NUMACTL = 3
GGML_NUMA_STRATEGY_MIRROR = 4
GGML_NUMA_STRATEGY_COUNT = 5
@ctypes_function("llama_numa_init", [ctypes.c_int], None)
def llama_numa_init(numa: int): ...
@ctypes_function("llama_backend_free", [], None)
def llama_backend_free(): ...
@ctypes_function("llama_load_model_from_file", [ctypes.c_char_p, llama_model_params], llama_model_p_ctypes)
def llama_load_model_from_file(path_model: bytes, params: llama_model_params) -> Optional[llama_model_p]: ...
@ctypes_function("llama_model_load_from_file", [ctypes.c_char_p, llama_model_params], llama_model_p_ctypes)
def llama_model_load_from_file(path_model: bytes, params: llama_model_params) -> Optional[llama_model_p]: ...
@ctypes_function("llama_free_model", [llama_model_p_ctypes], None)
def llama_free_model(model: llama_model_p): ...
@ctypes_function("llama_model_free", [llama_model_p_ctypes], None)
def llama_model_free(model: llama_model_p): ...
@ctypes_function("llama_new_context_with_model", [llama_model_p_ctypes, llama_context_params], llama_context_p_ctypes)
def llama_new_context_with_model(model: llama_model_p, params: llama_context_params) -> Optional[llama_context_p]: ...
@ctypes_function("llama_free", [llama_context_p_ctypes], None)
def llama_free(ctx: llama_context_p): ...
@ctypes_function("llama_time_us", [], ctypes.c_int64)
def llama_time_us() -> int: ...
@ctypes_function("llama_max_devices", [], ctypes.c_size_t)
def llama_max_devices() -> int: ...
@ctypes_function("llama_supports_mmap", [], ctypes.c_bool)
def llama_supports_mmap() -> bool: ...
@ctypes_function("llama_supports_mlock", [], ctypes.c_bool)
def llama_supports_mlock() -> bool: ...
@ctypes_function("llama_supports_gpu_offload", [], ctypes.c_bool)
def llama_supports_gpu_offload() -> bool: ...
@ctypes_function("llama_supports_rpc", [], ctypes.c_bool)
def llama_supports_rpc() -> bool: ...
@ctypes_function("llama_n_ctx", [llama_context_p_ctypes], ctypes.c_uint32)
def llama_n_ctx(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_n_batch", [llama_context_p_ctypes], ctypes.c_uint32)
def llama_n_batch(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_n_ubatch", [llama_context_p_ctypes], ctypes.c_uint32)
def llama_n_ubatch(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_n_seq_max", [llama_context_p_ctypes], ctypes.c_uint32)
def llama_n_seq_max(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_n_vocab", [llama_model_p_ctypes], ctypes.c_int32)
def llama_n_vocab(model: llama_model_p) -> int: ...
@ctypes_function("llama_n_ctx_train", [llama_model_p_ctypes], ctypes.c_int32)
def llama_n_ctx_train(model: llama_model_p) -> int: ...
@ctypes_function("llama_n_embd", [llama_model_p_ctypes], ctypes.c_int32)
def llama_n_embd(model: llama_model_p) -> int: ...
@ctypes_function("llama_n_layer", [llama_model_p_ctypes], ctypes.c_int32)
def llama_n_layer(model: llama_model_p) -> int: ...
@ctypes_function("llama_n_head", [llama_model_p_ctypes], ctypes.c_int32)
def llama_n_head(model: llama_model_p) -> int: ...
@ctypes_function("llama_get_model", [llama_context_p_ctypes], llama_model_p_ctypes)
def llama_get_model(ctx: llama_context_p) -> Optional[llama_model_p]: ...
@ctypes_function("llama_pooling_type", [llama_context_p_ctypes], ctypes.c_int)
def llama_pooling_type(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_vocab_type", [llama_model_p_ctypes], ctypes.c_int)
def llama_vocab_type(model: llama_model_p) -> int: ...
@ctypes_function("llama_rope_type", [llama_model_p_ctypes], ctypes.c_int)
def llama_rope_type(model: llama_model_p) -> int: ...
@ctypes_function("llama_rope_freq_scale_train", [llama_model_p_ctypes], ctypes.c_float)
def llama_rope_freq_scale_train(model: llama_model_p) -> float: ...
@ctypes_function("llama_model_meta_val_str", [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t], ctypes.c_int32)
def llama_model_meta_val_str(model: llama_model_p, key: Union[ctypes.c_char_p, bytes], buf: bytes, buf_size: int) -> int: ...
@ctypes_function("llama_model_meta_count", [llama_model_p_ctypes], ctypes.c_int32)
def llama_model_meta_count(model: llama_model_p) -> int: ...
@ctypes_function("llama_model_meta_key_by_index", [llama_model_p_ctypes, ctypes.c_int32, ctypes.c_char_p, ctypes.c_size_t], ctypes.c_int32)
def llama_model_meta_key_by_index(model: llama_model_p, i: Union[ctypes.c_int, int], buf: Union[bytes, CtypesArray[ctypes.c_char]], buf_size: int) -> int: ...
@ctypes_function("llama_model_meta_val_str_by_index", [llama_model_p_ctypes, ctypes.c_int32, ctypes.c_char_p, ctypes.c_size_t], ctypes.c_int32)
def llama_model_meta_val_str_by_index(model: llama_model_p, i: Union[ctypes.c_int, int], buf: Union[bytes, CtypesArray[ctypes.c_char]], buf_size: int) -> int: ...
@ctypes_function("llama_model_desc", [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_size_t], ctypes.c_int32)
def llama_model_desc(model: llama_model_p, buf: Union[bytes, CtypesArray[ctypes.c_char]], buf_size: Union[ctypes.c_size_t, int]) -> int: ...
@ctypes_function("llama_model_size", [llama_model_p_ctypes], ctypes.c_uint64)
def llama_model_size(model: llama_model_p) -> int: ...
@ctypes_function("llama_model_n_params", [llama_model_p_ctypes], ctypes.c_uint64)
def llama_model_n_params(model: llama_model_p) -> int: ...
@ctypes_function("llama_model_has_encoder", [llama_model_p_ctypes], ctypes.c_bool)
def llama_model_has_encoder(model: llama_model_p) -> bool: ...
@ctypes_function("llama_model_has_decoder", [llama_model_p_ctypes], ctypes.c_bool)
def llama_model_has_decoder(model: llama_model_p) -> bool: ...
@ctypes_function("llama_model_decoder_start_token", [llama_model_p_ctypes], ctypes.c_int32)
def llama_model_decoder_start_token(model: llama_model_p) -> int: ...
@ctypes_function("llama_model_is_recurrent", [llama_model_p_ctypes], ctypes.c_bool)
def llama_model_is_recurrent(model: llama_model_p) -> bool: ...
@ctypes_function("llama_model_quantize", [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(llama_model_quantize_params)], ctypes.c_uint32)
def llama_model_quantize(fname_inp: bytes, fname_out: bytes, params: CtypesPointerOrRef[llama_model_quantize_params]) -> int: ...
@ctypes_function("llama_lora_adapter_init", [llama_model_p_ctypes, ctypes.c_char_p], llama_lora_adapter_p_ctypes)
def llama_lora_adapter_init(model: llama_model_p, path_lora: bytes) -> Optional[llama_lora_adapter_p]: ...
@ctypes_function("llama_lora_adapter_set", [llama_context_p_ctypes, llama_lora_adapter_p_ctypes, ctypes.c_float], ctypes.c_int32)
def llama_lora_adapter_set(ctx: llama_context_p, adapter: llama_lora_adapter_p, scale: float) -> int: ...
@ctypes_function("llama_lora_adapter_remove", [llama_context_p_ctypes, llama_lora_adapter_p_ctypes], ctypes.c_int32)
def llama_lora_adapter_remove(ctx: llama_context_p, adapter: llama_lora_adapter_p) -> int: ...
@ctypes_function("llama_lora_adapter_clear", [llama_context_p_ctypes], None)
def llama_lora_adapter_clear(ctx: llama_context_p): ...
@ctypes_function("llama_lora_adapter_free", [llama_lora_adapter_p_ctypes], None)
def llama_lora_adapter_free(adapter: llama_lora_adapter_p): ...
@ctypes_function("llama_control_vector_apply", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_float), ctypes.c_size_t, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32], ctypes.c_int32)
def llama_control_vector_apply(lctx: llama_context_p, data: CtypesPointerOrRef[ctypes.c_float], len: int, n_embd: int, il_start: int, il_end: int) -> int: ...
class llama_kv_cache_view_cell(ctypes.Structure):
    if TYPE_CHECKING: pos: llama_pos
    _fields_ = [("pos", llama_pos)]
class llama_kv_cache_view(ctypes.Structure):
    if TYPE_CHECKING:
        n_cells: int
        n_max_seq: int
        token_count: int
        used_cells: int
        max_contiguous: int
        max_contiguous_idx: int
        cells: CtypesArray[llama_kv_cache_view_cell]
        cells_sequences: CtypesArray[llama_seq_id]
    _fields_ = [("n_cells", ctypes.c_int32), ("n_max_seq", ctypes.c_int32), ("token_count", ctypes.c_int32), ("used_cells", ctypes.c_int32), ("max_contiguous", ctypes.c_int32),
    ("max_contiguous_idx", ctypes.c_int32), ("cells", ctypes.POINTER(llama_kv_cache_view_cell)), ("cells_sequences", ctypes.POINTER(llama_seq_id))]
llama_kv_cache_view_p = ctypes.POINTER(llama_kv_cache_view)
@ctypes_function("llama_kv_cache_view_init", [llama_context_p_ctypes, ctypes.c_int32], llama_kv_cache_view)
def llama_kv_cache_view_init(ctx: llama_context_p, n_seq_max: Union[ctypes.c_int32, int]) -> llama_kv_cache_view: ...
@ctypes_function("llama_kv_cache_view_free", [llama_kv_cache_view_p], None)
def llama_kv_cache_view_free(view: "ctypes.pointer[llama_kv_cache_view]"): ...
@ctypes_function("llama_kv_cache_view_update", [llama_context_p_ctypes, llama_kv_cache_view_p], None)
def llama_kv_cache_view_update(ctx: llama_context_p, view: CtypesPointerOrRef[llama_kv_cache_view]): ...
@ctypes_function("llama_get_kv_cache_token_count", [llama_context_p_ctypes], ctypes.c_int32)
def llama_get_kv_cache_token_count(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_get_kv_cache_used_cells", [llama_context_p_ctypes], ctypes.c_int32)
def llama_get_kv_cache_used_cells(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_kv_cache_clear", [llama_context_p_ctypes], None)
def llama_kv_cache_clear(ctx: llama_context_p): ...
@ctypes_function("llama_kv_cache_seq_rm", [llama_context_p_ctypes, llama_seq_id, llama_pos, llama_pos], ctypes.c_bool)
def llama_kv_cache_seq_rm(ctx: llama_context_p, seq_id: Union[llama_seq_id, int], p0: Union[llama_pos, int], p1: Union[llama_pos, int]) -> bool: ...
@ctypes_function("llama_kv_cache_seq_cp", [llama_context_p_ctypes, llama_seq_id, llama_seq_id, llama_pos, llama_pos], None)
def llama_kv_cache_seq_cp(ctx: llama_context_p, seq_id_src: Union[llama_seq_id, int], seq_id_dst: Union[llama_seq_id, int], p0: Union[llama_pos, int], p1: Union[llama_pos, int]): ...
@ctypes_function("llama_kv_cache_seq_keep", [llama_context_p_ctypes, llama_seq_id], None)
def llama_kv_cache_seq_keep(ctx: llama_context_p, seq_id: Union[llama_seq_id, int]): ...
@ctypes_function("llama_kv_cache_seq_add", [llama_context_p_ctypes, llama_seq_id, llama_pos, llama_pos, llama_pos], None)
def llama_kv_cache_seq_add(ctx: llama_context_p, seq_id: Union[llama_seq_id, int], p0: Union[llama_pos, int], p1: Union[llama_pos, int], delta: Union[llama_pos, int]): ...
@ctypes_function("llama_kv_cache_seq_div", [llama_context_p_ctypes, llama_seq_id, llama_pos, llama_pos, ctypes.c_int], None)
def llama_kv_cache_seq_div(ctx: llama_context_p, seq_id: Union[llama_seq_id, int], p0: Union[llama_pos, int], p1: Union[llama_pos, int], d: Union[ctypes.c_int, int]): ...
@ctypes_function("llama_kv_cache_defrag", [llama_context_p_ctypes], None)
def llama_kv_cache_defrag(ctx: llama_context_p): ...
@ctypes_function("llama_kv_cache_update", [llama_context_p_ctypes], None)
def llama_kv_cache_update(ctx: llama_context_p): ...
@ctypes_function("llama_kv_cache_can_shift", [llama_context_p_ctypes], ctypes.c_bool)
def llama_kv_cache_can_shift(ctx: llama_context_p) -> bool: ...
@ctypes_function("llama_state_get_size", [llama_context_p_ctypes], ctypes.c_size_t)
def llama_state_get_size(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_get_state_size", [llama_context_p_ctypes], ctypes.c_size_t)
def llama_get_state_size(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_state_get_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t], ctypes.c_size_t)
def llama_state_get_data(ctx: llama_context_p, dst: CtypesArray[ctypes.c_uint8], size: Union[ctypes.c_size_t, int]) -> int: ...
@ctypes_function("llama_copy_state_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8)], ctypes.c_size_t)
def llama_copy_state_data(ctx: llama_context_p, dst: CtypesArray[ctypes.c_uint8]) -> int: ...
@ctypes_function("llama_state_set_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t], ctypes.c_size_t)
def llama_state_set_data(ctx: llama_context_p, src: CtypesArray[ctypes.c_uint8], size: Union[ctypes.c_size_t, int]) -> int: ...
@ctypes_function("llama_set_state_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8)], ctypes.c_size_t)
def llama_set_state_data(ctx: llama_context_p, src: CtypesArray[ctypes.c_uint8]) -> int: ...
@ctypes_function("llama_state_load_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_token_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)], ctypes.c_bool)
def llama_state_load_file(ctx: llama_context_p, path_session: bytes, tokens_out: CtypesArray[llama_token], n_token_capacity: Union[ctypes.c_size_t, int],
n_token_count_out: CtypesPointerOrRef[ctypes.c_size_t]) -> bool: ...
@ctypes_function("llama_load_session_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_token_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)], ctypes.c_size_t)
def llama_load_session_file(ctx: llama_context_p, path_session: bytes, tokens_out: CtypesArray[llama_token], n_token_capacity: Union[ctypes.c_size_t, int],
n_token_count_out: CtypesPointerOrRef[ctypes.c_size_t]) -> int: ...
@ctypes_function("llama_state_save_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_token_p, ctypes.c_size_t], ctypes.c_bool)
def llama_state_save_file(ctx: llama_context_p, path_session: bytes, tokens: CtypesArray[llama_token], n_token_count: Union[ctypes.c_size_t, int]) -> bool: ...
@ctypes_function("llama_save_session_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_token_p, ctypes.c_size_t], ctypes.c_size_t)
def llama_save_session_file(ctx: llama_context_p, path_session: bytes, tokens: CtypesArray[llama_token], n_token_count: Union[ctypes.c_size_t, int]) -> int: ...
@ctypes_function("llama_state_seq_get_size", [llama_context_p_ctypes, llama_seq_id], ctypes.c_size_t)
def llama_state_seq_get_size(ctx: llama_context_p, seq_id: llama_seq_id) -> int: ...
@ctypes_function("llama_state_seq_get_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, llama_seq_id], ctypes.c_size_t)
def llama_state_seq_get_data(ctx: llama_context_p, dst: CtypesArray[ctypes.c_uint8], size: Union[ctypes.c_size_t, int], seq_id: llama_seq_id) -> int: ...
@ctypes_function("llama_state_seq_set_data", [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, llama_seq_id], ctypes.c_size_t)
def llama_state_seq_set_data(ctx: llama_context_p, src: CtypesArray[ctypes.c_uint8], size: Union[ctypes.c_size_t, int], dest_seq_id: llama_seq_id) -> int: ...
@ctypes_function("llama_state_seq_save_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_seq_id, llama_token_p, ctypes.c_size_t], ctypes.c_size_t)
def llama_state_seq_save_file(ctx: llama_context_p, filepath: bytes, seq_id: llama_seq_id, tokens: CtypesArray[llama_token], n_token_count: Union[ctypes.c_size_t, int]) -> int: ...
@ctypes_function("llama_state_seq_load_file", [llama_context_p_ctypes, ctypes.c_char_p, llama_seq_id, llama_token_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)], ctypes.c_size_t)
def llama_state_seq_load_file(ctx: llama_context_p, filepath: bytes, dest_seq_id: llama_seq_id, tokens_out: CtypesArray[llama_token], n_token_capacity: Union[ctypes.c_size_t, int], n_token_count_out: CtypesPointerOrRef[ctypes.c_size_t]) -> int: ...
@ctypes_function("llama_batch_get_one", [llama_token_p, ctypes.c_int32], llama_batch)
def llama_batch_get_one(tokens: CtypesArray[llama_token], n_tokens: Union[ctypes.c_int, int]) -> llama_batch: ...
@ctypes_function("llama_batch_init", [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32], llama_batch)
def llama_batch_init(n_tokens: Union[ctypes.c_int32, int], embd: Union[ctypes.c_int32, int], n_seq_max: Union[ctypes.c_int32, int]) -> llama_batch: ...
@ctypes_function("llama_batch_free", [llama_batch], None)
def llama_batch_free(batch: llama_batch): ...
@ctypes_function("llama_encode", [llama_context_p_ctypes, llama_batch], ctypes.c_int32)
def llama_encode(ctx: llama_context_p, batch: llama_batch) -> int: ...
@ctypes_function("llama_decode", [llama_context_p_ctypes, llama_batch], ctypes.c_int32)
def llama_decode(ctx: llama_context_p, batch: llama_batch) -> int: ...
@ctypes_function("llama_set_n_threads", [llama_context_p_ctypes, ctypes.c_int32, ctypes.c_int32], None)
def llama_set_n_threads(ctx: llama_context_p, n_threads: Union[ctypes.c_int32, int], n_threads_batch: Union[ctypes.c_int32, int]): ...
@ctypes_function("llama_n_threads", [llama_context_p_ctypes], ctypes.c_int32)
def llama_n_threads(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_n_threads_batch", [llama_context_p_ctypes], ctypes.c_int32)
def llama_n_threads_batch(ctx: llama_context_p) -> int: ...
@ctypes_function("llama_set_embeddings", [llama_context_p_ctypes, ctypes.c_bool], None)
def llama_set_embeddings(ctx: llama_context_p, embeddings: bool): ...
@ctypes_function("llama_set_causal_attn", [llama_context_p_ctypes, ctypes.c_bool], None)
def llama_set_causal_attn(ctx: llama_context_p, causal_attn: bool): ...
@ctypes_function("llama_set_abort_callback", [llama_context_p_ctypes, ggml_abort_callback, ctypes.c_void_p], None)
def llama_set_abort_callback(ctx: llama_context_p, abort_callback: Callable[[ctypes.c_void_p], None], abort_callback_data: ctypes.c_void_p): ...
@ctypes_function("llama_synchronize", [llama_context_p_ctypes], None)
def llama_synchronize(ctx: llama_context_p): ...
@ctypes_function("llama_get_logits", [llama_context_p_ctypes], ctypes.POINTER(ctypes.c_float))
def llama_get_logits(ctx: llama_context_p) -> CtypesArray[ctypes.c_float]: ...
@ctypes_function("llama_get_logits_ith", [llama_context_p_ctypes, ctypes.c_int32], ctypes.POINTER(ctypes.c_float))
def llama_get_logits_ith(ctx: llama_context_p, i: Union[ctypes.c_int32, int]) -> CtypesArray[ctypes.c_float]: ...
@ctypes_function("llama_get_embeddings", [llama_context_p_ctypes], ctypes.POINTER(ctypes.c_float))
def llama_get_embeddings(ctx: llama_context_p) -> CtypesArray[ctypes.c_float]: ...
@ctypes_function("llama_get_embeddings_ith", [llama_context_p_ctypes, ctypes.c_int32], ctypes.POINTER(ctypes.c_float))
def llama_get_embeddings_ith(ctx: llama_context_p, i: Union[ctypes.c_int32, int]) -> CtypesArray[ctypes.c_float]: ...
@ctypes_function("llama_get_embeddings_seq", [llama_context_p_ctypes, llama_seq_id], ctypes.POINTER(ctypes.c_float))
def llama_get_embeddings_seq(ctx: llama_context_p, seq_id: Union[llama_seq_id, int]) -> CtypesArray[ctypes.c_float]: ...
@ctypes_function("llama_token_get_text", [llama_model_p_ctypes, llama_token], ctypes.c_char_p)
def llama_token_get_text(model: llama_model_p, token: Union[llama_token, int]) -> bytes: ...
@ctypes_function("llama_token_get_score", [llama_model_p_ctypes, llama_token], ctypes.c_float)
def llama_token_get_score(model: llama_model_p, token: Union[llama_token, int]) -> float: ...
@ctypes_function("llama_token_get_attr", [llama_model_p_ctypes, llama_token], ctypes.c_int)
def llama_token_get_attr(model: llama_model_p, token: Union[llama_token, int]) -> int: ...
@ctypes_function("llama_token_is_eog", [llama_model_p_ctypes, llama_token], ctypes.c_bool)
def llama_token_is_eog(model: llama_model_p, token: Union[llama_token, int]) -> bool: ...
@ctypes_function("llama_token_is_control", [llama_model_p_ctypes, llama_token], ctypes.c_bool)
def llama_token_is_control(model: llama_model_p, token: Union[llama_token, int]) -> bool: ...
@ctypes_function("llama_token_bos", [llama_model_p_ctypes], llama_token)
def llama_token_bos(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_eos", [llama_model_p_ctypes], llama_token)
def llama_token_eos(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_eot", [llama_model_p_ctypes], llama_token)
def llama_token_eot(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_cls", [llama_model_p_ctypes], llama_token)
def llama_token_cls(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_sep", [llama_model_p_ctypes], llama_token)
def llama_token_sep(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_nl", [llama_model_p_ctypes], llama_token)
def llama_token_nl(model: llama_model_p) -> int: ...
@ctypes_function("llama_add_bos_token", [llama_model_p_ctypes], ctypes.c_bool)
def llama_add_bos_token(model: llama_model_p) -> bool: ...
@ctypes_function("llama_add_eos_token", [llama_model_p_ctypes], ctypes.c_bool)
def llama_add_eos_token(model: llama_model_p) -> bool: ...
@ctypes_function("llama_token_prefix", [llama_model_p_ctypes], llama_token)
def llama_token_prefix(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_middle", [llama_model_p_ctypes], llama_token)
def llama_token_middle(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_suffix", [llama_model_p_ctypes], llama_token)
def llama_token_suffix(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_pre", [llama_model_p_ctypes], llama_token)
def llama_token_fim_pre(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_suf", [llama_model_p_ctypes], llama_token)
def llama_token_fim_suf(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_mid", [llama_model_p_ctypes], llama_token)
def llama_token_fim_mid(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_pad", [llama_model_p_ctypes], llama_token)
def llama_token_fim_pad(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_rep", [llama_model_p_ctypes], llama_token)
def llama_token_fim_rep(model: llama_model_p) -> int: ...
@ctypes_function("llama_token_fim_sep", [llama_model_p_ctypes], llama_token)
def llama_token_fim_sep(model: llama_model_p) -> int: ...
@ctypes_function("llama_tokenize", [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_int32, llama_token_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool], ctypes.c_int32)
def llama_tokenize(model: llama_model_p, text: bytes, text_len: Union[ctypes.c_int, int], tokens: CtypesArray[llama_token], n_tokens_max: Union[ctypes.c_int, int],
add_special: Union[ctypes.c_bool, bool], parse_special: Union[ctypes.c_bool, bool]) -> int: ...
@ctypes_function("llama_token_to_piece", [llama_model_p_ctypes, llama_token, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_bool], ctypes.c_int32)
def llama_token_to_piece(model: llama_model_p, token: Union[llama_token, int], buf: Union[ctypes.c_char_p, bytes, CtypesArray[ctypes.c_char]], length: Union[ctypes.c_int, int],
lstrip: Union[ctypes.c_int, int], special: Union[ctypes.c_bool, bool]) -> int: ...
@ctypes_function("llama_detokenize", [llama_model_p_ctypes, ctypes.POINTER(llama_token), ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_bool], ctypes.c_int32)
def llama_detokenize(model: llama_model_p, tokens: CtypesArray[llama_token], n_tokens: Union[ctypes.c_int, int], text: bytes, text_len_max: Union[ctypes.c_int, int],
remove_special: Union[ctypes.c_bool, bool], unparse_special: Union[ctypes.c_bool, bool]) -> int: ...
@ctypes_function("llama_chat_apply_template", [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(llama_chat_message), ctypes.c_size_t], ctypes.c_int32)
def llama_chat_apply_template(model: llama_model_p, tmpl: bytes, chat: CtypesArray[llama_chat_message], n_msg: int) -> int: ...
@ctypes_function("llama_chat_builtin_templates", [ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t], ctypes.c_int32)
def llama_chat_builtin_templates(output: CtypesArray[bytes], len: Union[ctypes.c_size_t, int]) -> int: ...
llama_sampler_context_t = ctypes.c_void_p
class llama_sampler_i(ctypes.Structure): ...
class llama_sampler(ctypes.Structure): _fields_ = [("iface", ctypes.POINTER(llama_sampler_i)), ("ctx", llama_sampler_context_t)]
if TYPE_CHECKING: llama_sampler_p = CtypesPointer[llama_sampler]
llama_sampler_p_ctypes = ctypes.POINTER(llama_sampler)
llama_sampler_i_name = ctypes.CFUNCTYPE(ctypes.c_char_p, llama_sampler_p_ctypes)
llama_sampler_i_accept = ctypes.CFUNCTYPE(None, llama_sampler_p_ctypes, llama_token)
llama_sampler_i_apply = ctypes.CFUNCTYPE(None, llama_sampler_p_ctypes, llama_token_data_array_p)
llama_sampler_i_reset = ctypes.CFUNCTYPE(None, llama_sampler_p_ctypes)
llama_sampler_i_clone = ctypes.CFUNCTYPE(llama_sampler_p_ctypes, llama_sampler_p_ctypes)
llama_sampler_i_free = ctypes.CFUNCTYPE(None, llama_sampler_p_ctypes)
llama_sampler_i._fields_ = [("name", llama_sampler_i_name), ("accept", llama_sampler_i_accept), ("apply", llama_sampler_i_apply), ("reset", llama_sampler_i_reset), ("clone", llama_sampler_i_clone), ("free", llama_sampler_i_free)]
@ctypes_function("llama_sampler_name", [llama_sampler_p_ctypes], ctypes.c_char_p)
def llama_sampler_name(smpl: llama_sampler_p) -> bytes: ...
@ctypes_function("llama_sampler_accept", [llama_sampler_p_ctypes, llama_token], None)
def llama_sampler_accept(smpl: llama_sampler_p, token: Union[llama_token, int]): ...
@ctypes_function("llama_sampler_apply", [llama_sampler_p_ctypes, llama_token_data_array_p], None)
def llama_sampler_apply(smpl: llama_sampler_p, cur_p: CtypesArray[llama_token_data_array]): ...
@ctypes_function("llama_sampler_reset", [llama_sampler_p_ctypes], None)
def llama_sampler_reset(smpl: llama_sampler_p): ...
@ctypes_function("llama_sampler_clone", [llama_sampler_p_ctypes], llama_sampler_p_ctypes)
def llama_sampler_clone(smpl: llama_sampler_p) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_free", [llama_sampler_p_ctypes], None)
def llama_sampler_free(smpl: llama_sampler_p): ...
@ctypes_function("llama_sampler_chain_init", [llama_sampler_chain_params], llama_sampler_p_ctypes)
def llama_sampler_chain_init(params: llama_sampler_chain_params) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_chain_add", [llama_sampler_p_ctypes, llama_sampler_p_ctypes], None)
def llama_sampler_chain_add(chain: llama_sampler_p, smpl: llama_sampler_p): ...
@ctypes_function("llama_sampler_chain_get", [llama_sampler_p_ctypes, ctypes.c_int32], llama_sampler_p_ctypes)
def llama_sampler_chain_get(chain: llama_sampler_p, i: Union[ctypes.c_int32, int]) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_chain_n", [llama_sampler_p_ctypes], ctypes.c_int)
def llama_sampler_chain_n(chain: llama_sampler_p) -> int: ...
@ctypes_function("llama_sampler_chain_remove", [llama_sampler_p_ctypes, ctypes.c_int32], llama_sampler_p_ctypes)
def llama_sampler_chain_remove(chain: llama_sampler_p, i: Union[ctypes.c_int32, int]) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_greedy", [], llama_sampler_p_ctypes)
def llama_sampler_init_greedy() -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_dist", [ctypes.c_uint32], llama_sampler_p_ctypes)
def llama_sampler_init_dist(seed: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_softmax", [], llama_sampler_p_ctypes)
def llama_sampler_init_softmax() -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_top_k", [ctypes.c_int32], llama_sampler_p_ctypes)
def llama_sampler_init_top_k(k: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_top_p", [ctypes.c_float, ctypes.c_size_t], llama_sampler_p_ctypes)
def llama_sampler_init_top_p(p: float, min_keep: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_min_p", [ctypes.c_float, ctypes.c_size_t], llama_sampler_p_ctypes)
def llama_sampler_init_min_p(p: float, min_keep: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_typical", [ctypes.c_float, ctypes.c_size_t], llama_sampler_p_ctypes)
def llama_sampler_init_typical(p: float, min_keep: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_temp", [ctypes.c_float], llama_sampler_p_ctypes)
def llama_sampler_init_temp(t: float) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_temp_ext", [ctypes.c_float, ctypes.c_float, ctypes.c_float], llama_sampler_p_ctypes)
def llama_sampler_init_temp_ext(t: float, delta: float, exponent: float) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_xtc", [ctypes.c_float, ctypes.c_float, ctypes.c_size_t, ctypes.c_uint32], llama_sampler_p_ctypes)
def llama_sampler_init_xtc(p: float, t: float, min_keep: int, seed: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_mirostat", [ctypes.c_int32, ctypes.c_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_int32], llama_sampler_p_ctypes)
def llama_sampler_init_mirostat(n_vocab: int, seed: int, tau: float, eta: float, m: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_mirostat_v2", [ctypes.c_uint32, ctypes.c_float, ctypes.c_float], llama_sampler_p_ctypes)
def llama_sampler_init_mirostat_v2(seed: int, tau: float, eta: float) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_grammar", [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_char_p], llama_sampler_p_ctypes)
def llama_sampler_init_grammar(model: llama_model_p, grammar_str: bytes, grammar_root: bytes) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_penalties", [ctypes.c_int32, ctypes.c_float, ctypes.c_float, ctypes.c_float], llama_sampler_p_ctypes)
def llama_sampler_init_penalties(penalty_last_n: int, penalty_repeat: float, penalty_freq: float, penalty_present: float) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_dry", [llama_model_p_ctypes, ctypes.c_float, ctypes.c_float, ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t], llama_sampler_p_ctypes)
def llama_sampler_init_dry(model: llama_model_p, dry_multiplier: float, dry_base: float, dry_allowed_length: int, dry_penalty_last_n: int, seq_breakers: CtypesArray[bytes], num_breakers: int) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_logit_bias", [ctypes.c_int32, ctypes.c_int32, llama_logit_bias_p], llama_sampler_p_ctypes)
def llama_sampler_init_logit_bias(n_vocab: int, n_logit_bias: int, logit_bias: CtypesArray[llama_logit_bias]) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_init_infill", [llama_model_p_ctypes], llama_sampler_p_ctypes)
def llama_sampler_init_infill(model: llama_model_p) -> llama_sampler_p: ...
@ctypes_function("llama_sampler_get_seed", [llama_sampler_p_ctypes], ctypes.c_uint32)
def llama_sampler_get_seed(smpl: llama_sampler_p) -> int: ...
@ctypes_function("llama_sampler_sample", [llama_sampler_p_ctypes, llama_context_p_ctypes, ctypes.c_int32], llama_token)
def llama_sampler_sample(smpl: llama_sampler_p, ctx: llama_context_p, idx: int) -> int: ...
@ctypes_function("llama_split_path", [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_int, ctypes.c_int], ctypes.c_int)
def llama_split_path(split_path: bytes, maxlen: Union[ctypes.c_size_t, int], path_prefix: bytes, split_no: Union[ctypes.c_int, int], split_count: Union[ctypes.c_int, int]) -> int: ...
@ctypes_function("llama_split_prefix", [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_int, ctypes.c_int], ctypes.c_int)
def llama_split_prefix(split_prefix: bytes, maxlen: Union[ctypes.c_size_t, int], split_path: bytes, split_no: Union[ctypes.c_int, int], split_count: Union[ctypes.c_int, int]) -> int: ...
@ctypes_function("llama_print_system_info", [], ctypes.c_char_p)
def llama_print_system_info() -> bytes: ...
@ctypes_function("llama_log_set", [ctypes.c_void_p, ctypes.c_void_p], None)
def llama_log_set(log_callback: Optional[CtypesFuncPointer], user_data: ctypes.c_void_p): ...
class llama_perf_context_data(ctypes.Structure): _fields_ = [("t_start_ms", ctypes.c_double), ("t_load_ms", ctypes.c_double), ("t_p_eval_ms", ctypes.c_double), ("t_eval_ms", ctypes.c_double), ("n_p_eval", ctypes.c_int32), ("n_eval", ctypes.c_int32)]
class llama_perf_sampler_data(ctypes.Structure): _fields_ = [("t_sample_ms", ctypes.c_double), ("n_sample", ctypes.c_int32)]
@ctypes_function("llama_perf_context", [llama_context_p_ctypes], llama_perf_context_data)
def llama_perf_context(ctx: llama_context_p) -> llama_perf_context_data: ...
@ctypes_function("llama_perf_context_print", [llama_context_p_ctypes], None)
def llama_perf_context_print(ctx: llama_context_p): ...
@ctypes_function("llama_perf_context_reset", [llama_context_p_ctypes], None)
def llama_perf_context_reset(ctx: llama_context_p): ...
@ctypes_function("llama_perf_sampler", [llama_sampler_p_ctypes], llama_perf_sampler_data)
def llama_perf_sampler(chain: llama_sampler_p) -> llama_perf_sampler_data: ...
@ctypes_function("llama_perf_sampler_print", [llama_sampler_p_ctypes], None)
def llama_perf_sampler_print(chain: llama_sampler_p): ...
@ctypes_function("llama_perf_sampler_reset", [llama_sampler_p_ctypes], None)
def llama_perf_sampler_reset(chain: llama_sampler_p): ...
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
