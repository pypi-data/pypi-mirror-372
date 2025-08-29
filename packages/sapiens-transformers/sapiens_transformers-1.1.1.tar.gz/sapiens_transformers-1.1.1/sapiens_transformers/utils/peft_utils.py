"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
import os
from typing import Dict, Optional, Union
from packaging import version
from .hub import cached_file
from .import_utils import is_peft_available
ADAPTER_CONFIG_NAME = "adapter_config.json"
ADAPTER_WEIGHTS_NAME = "adapter_model.bin"
ADAPTER_SAFE_WEIGHTS_NAME = "adapter_model.safetensors"
def find_adapter_config_file(model_id: str, cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False, resume_download: Optional[bool] = None,
proxies: Optional[Dict[str, str]] = None, token: Optional[Union[bool, str]] = None, revision: Optional[str] = None, local_files_only: bool = False, subfolder: str = "", _commit_hash: Optional[str] = None) -> Optional[str]:
    adapter_cached_filename = None
    if model_id is None: return None
    elif os.path.isdir(model_id):
        list_remote_files = os.listdir(model_id)
        if ADAPTER_CONFIG_NAME in list_remote_files: adapter_cached_filename = os.path.join(model_id, ADAPTER_CONFIG_NAME)
    else: adapter_cached_filename = cached_file(model_id, ADAPTER_CONFIG_NAME, cache_dir=cache_dir, force_download=force_download, resume_download=resume_download, proxies=proxies, token=token, revision=revision,
    local_files_only=local_files_only, subfolder=subfolder, _commit_hash=_commit_hash, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False, _raise_exceptions_for_connection_errors=False)
    return adapter_cached_filename
def check_peft_version(min_version: str) -> None:
    if not is_peft_available(): raise ValueError("PEFT is not installed. Please install it with `pip install peft`")
    is_peft_version_compatible = version.parse(importlib.metadata.version("peft")) >= version.parse(min_version)
    if not is_peft_version_compatible: raise ValueError(f"The version of PEFT you are using is not compatible, please use a version that is greater than {min_version}")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
