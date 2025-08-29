"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from sapiens_transformers.sapiens_optimizer import llama_log_callback, llama_log_set
import logging
import ctypes
import sys
GGML_LOG_LEVEL_TO_LOGGING_LEVEL = {0: logging.CRITICAL, 1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR, 4: logging.DEBUG, 5: logging.DEBUG}
_last_log_level = GGML_LOG_LEVEL_TO_LOGGING_LEVEL[0]
logger = logging.getLogger("llama-cpp-python")
@llama_log_callback
def llama_log_callback(level: int, text: bytes, user_data: ctypes.c_void_p):
    global _last_log_level
    log_level = GGML_LOG_LEVEL_TO_LOGGING_LEVEL[level] if level != 5 else _last_log_level
    _last_log_level = log_level
llama_log_set(llama_log_callback, ctypes.c_void_p(0))
def set_verbose(verbose: bool): logger.setLevel(logging.DEBUG if verbose else logging.ERROR)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
