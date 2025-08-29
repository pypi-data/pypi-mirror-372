from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import (Any, Callable, List, Union, Optional, TYPE_CHECKING, TypeVar, Generic)
from typing_extensions import TypeAlias
import functools
import pathlib
import ctypes
import sys
import os
def load_shared_library(lib_base_name: str, base_path: pathlib.Path):
    lib_paths: List[pathlib.Path] = []
    if sys.platform.startswith("linux") or sys.platform.startswith("freebsd"): lib_paths += [base_path / f"lib{lib_base_name}.so"]
    elif sys.platform == "darwin": lib_paths += [base_path / f"lib{lib_base_name}.so", base_path / f"lib{lib_base_name}.dylib"]
    elif sys.platform == "win32": lib_paths += [base_path / f"{lib_base_name}.dll", base_path / f"lib{lib_base_name}.dll"]
    else: raise RuntimeError("Unsupported platform")
    cdll_args = dict()
    if sys.platform == "win32":
        os.add_dll_directory(str(base_path))
        os.environ["PATH"] = str(base_path) + os.pathsep + os.environ["PATH"]
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        os.add_dll_directory(str(base_path))
        if "CUDA_PATH" in os.environ:
            os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "bin"))
            os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "lib"))
        if "HIP_PATH" in os.environ:
            os.add_dll_directory(os.path.join(os.environ["HIP_PATH"], "bin"))
            os.add_dll_directory(os.path.join(os.environ["HIP_PATH"], "lib"))
        cdll_args["winmode"] = ctypes.RTLD_GLOBAL
    for lib_path in lib_paths:
        if lib_path.exists():
            try: return ctypes.CDLL(str(lib_path), **cdll_args)
            except Exception as e: raise RuntimeError(f"Failed to load shared library '{lib_path}': {e}")
    raise FileNotFoundError(f"Shared library with base name '{lib_base_name}' not found")
if TYPE_CHECKING:
    CtypesCData = TypeVar("CtypesCData", bound=ctypes._CData)
    CtypesArray: TypeAlias = ctypes.Array[CtypesCData]
    CtypesPointer: TypeAlias = ctypes._Pointer[CtypesCData]
    CtypesVoidPointer: TypeAlias = ctypes.c_void_p
    class CtypesRef(Generic[CtypesCData]): pass
    CtypesPointerOrRef: TypeAlias = Union[CtypesPointer[CtypesCData], CtypesRef[CtypesCData]]
    CtypesFuncPointer: TypeAlias = ctypes._FuncPointer
F = TypeVar("F", bound=Callable[..., Any])
def ctypes_function_for_shared_library(lib: ctypes.CDLL):
    def ctypes_function(name: str, argtypes: List[Any], restype: Any, enabled: bool = True):
        def decorator(f: F) -> F:
            if enabled:
                func = getattr(lib, name)
                func.argtypes = argtypes
                func.restype = restype
                functools.wraps(f)(func)
                return func
            else: return f
        return decorator
    return ctypes_function
def _byref(obj: CtypesCData, offset: Optional[int] = None) -> CtypesRef[CtypesCData]: ...
byref = _byref if TYPE_CHECKING else ctypes.byref
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
