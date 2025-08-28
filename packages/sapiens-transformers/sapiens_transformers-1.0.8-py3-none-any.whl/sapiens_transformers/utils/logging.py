"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import functools
import logging
import os
import sys
import threading
from logging import (CRITICAL, DEBUG, ERROR, FATAL, INFO, NOTSET, WARN, WARNING)
from logging import captureWarnings as _captureWarnings
from typing import Optional
import huggingface_hub.utils as hf_hub_utils
from tqdm import auto as tqdm_lib
_lock = threading.Lock()
_default_handler: Optional[logging.Handler] = None
log_levels = {"detail": logging.DEBUG, "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR, "critical": logging.CRITICAL}
_default_log_level = logging.WARNING
_tqdm_active = not hf_hub_utils.are_progress_bars_disabled()
def _get_default_logging_level():
    env_level_str = os.getenv("TRANSFORMERS_VERBOSITY", None)
    if env_level_str:
        if env_level_str in log_levels: return log_levels[env_level_str]
        else: logging.getLogger().warning(f"Unknown option TRANSFORMERS_VERBOSITY={env_level_str}, has to be one of: { ', '.join(log_levels.keys()) }")
    return _default_log_level
def _get_library_name() -> str: return __name__.split(".")[0]
def _get_library_root_logger() -> logging.Logger: return logging.getLogger(_get_library_name())
def _configure_library_root_logger() -> None:
    global _default_handler
    with _lock:
        if _default_handler: return
        _default_handler = logging.StreamHandler()
        if sys.stderr is None: sys.stderr = open(os.devnull, "w")
        _default_handler.flush = sys.stderr.flush
        library_root_logger = _get_library_root_logger()
        library_root_logger.addHandler(_default_handler)
        library_root_logger.setLevel(_get_default_logging_level())
        if os.getenv("TRANSFORMERS_VERBOSITY", None) == "detail":
            formatter = logging.Formatter("[%(levelname)s|%(pathname)s:%(lineno)s] %(asctime)s >> %(message)s")
            _default_handler.setFormatter(formatter)
        library_root_logger.propagate = False
def _reset_library_root_logger() -> None:
    global _default_handler
    with _lock:
        if not _default_handler: return
        library_root_logger = _get_library_root_logger()
        library_root_logger.removeHandler(_default_handler)
        library_root_logger.setLevel(logging.NOTSET)
        _default_handler = None
def get_log_levels_dict(): return log_levels
def captureWarnings(capture):
    logger = get_logger("py.warnings")
    if not logger.handlers: logger.addHandler(_default_handler)
    logger.setLevel(_get_library_root_logger().level)
    _captureWarnings(capture)
def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name is None: name = _get_library_name()
    _configure_library_root_logger()
    return logging.getLogger(name)
def get_verbosity() -> int:
    _configure_library_root_logger()
    return _get_library_root_logger().getEffectiveLevel()
def set_verbosity(verbosity: int) -> None:
    _configure_library_root_logger()
    _get_library_root_logger().setLevel(verbosity)
def set_verbosity_info(): return set_verbosity(INFO)
def set_verbosity_warning(): return set_verbosity(WARNING)
def set_verbosity_debug(): return set_verbosity(DEBUG)
def set_verbosity_error(): return set_verbosity(ERROR)
def disable_default_handler() -> None:
    _configure_library_root_logger()
    assert _default_handler is not None
    _get_library_root_logger().removeHandler(_default_handler)
def enable_default_handler() -> None:
    _configure_library_root_logger()
    assert _default_handler is not None
    _get_library_root_logger().addHandler(_default_handler)
def add_handler(handler: logging.Handler) -> None:
    _configure_library_root_logger()
    assert handler is not None
    _get_library_root_logger().addHandler(handler)
def remove_handler(handler: logging.Handler) -> None:
    _configure_library_root_logger()
    assert handler is not None and handler not in _get_library_root_logger().handlers
    _get_library_root_logger().removeHandler(handler)
def disable_propagation() -> None:
    _configure_library_root_logger()
    _get_library_root_logger().propagate = False
def enable_propagation() -> None:
    _configure_library_root_logger()
    _get_library_root_logger().propagate = True
def enable_explicit_format() -> None:
    handlers = _get_library_root_logger().handlers
    for handler in handlers:
        formatter = logging.Formatter("[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s >> %(message)s")
        handler.setFormatter(formatter)
def reset_format() -> None:
    handlers = _get_library_root_logger().handlers
    for handler in handlers: handler.setFormatter(None)
def warning_advice(self, *args, **kwargs):
    no_advisory_warnings = os.getenv("TRANSFORMERS_NO_ADVISORY_WARNINGS", False)
    if no_advisory_warnings: return
    self.warning(*args, **kwargs)
logging.Logger.warning_advice = warning_advice
@functools.lru_cache(None)
def warning_once(self, *args, **kwargs): self.warning(*args, **kwargs)
logging.Logger.warning_once = warning_once
@functools.lru_cache(None)
def info_once(self, *args, **kwargs): self.info(*args, **kwargs)
logging.Logger.info_once = info_once
class EmptyTqdm:
    def __init__(self, *args, **kwargs): self._iterator = args[0] if args else None
    def __iter__(self): return iter(self._iterator)
    def __getattr__(self, _):
        def empty_fn(*args, **kwargs): return
        return empty_fn
    def __enter__(self): return self
    def __exit__(self, type_, value, traceback): return
class _tqdm_cls:
    def __call__(self, *args, **kwargs):
        if _tqdm_active: return tqdm_lib.tqdm(*args, **kwargs)
        else: return EmptyTqdm(*args, **kwargs)
    def set_lock(self, *args, **kwargs):
        self._lock = None
        if _tqdm_active: return tqdm_lib.tqdm.set_lock(*args, **kwargs)
    def get_lock(self):
        if _tqdm_active: return tqdm_lib.tqdm.get_lock()
tqdm = _tqdm_cls()
def is_progress_bar_enabled() -> bool:
    global _tqdm_active
    return bool(_tqdm_active)
def enable_progress_bar():
    global _tqdm_active
    _tqdm_active = True
    hf_hub_utils.enable_progress_bars()
def disable_progress_bar():
    global _tqdm_active
    _tqdm_active = False
    hf_hub_utils.disable_progress_bars()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
