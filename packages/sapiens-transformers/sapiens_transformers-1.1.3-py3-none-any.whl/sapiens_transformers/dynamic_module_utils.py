"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (HF_MODULES_CACHE, TRANSFORMERS_DYNAMIC_MODULE_NAME, cached_file, extract_commit_hash, is_offline_mode, logging)
from typing import Any, Dict, List, Optional, Union
from huggingface_hub import try_to_load_from_cache
from types import ModuleType
from pathlib import Path
import importlib.util
import importlib
import threading
import warnings
import filecmp
import hashlib
import shutil
import signal
import typing
import sys
import os
import re
logger = logging.get_logger(__name__)
_HF_REMOTE_CODE_LOCK = threading.Lock()
def init_hf_modules():
    if HF_MODULES_CACHE in sys.path: return
    sys.path.append(HF_MODULES_CACHE)
    os.makedirs(HF_MODULES_CACHE, exist_ok=True)
    init_path = Path(HF_MODULES_CACHE) / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        importlib.invalidate_caches()
def create_dynamic_module(name: Union[str, os.PathLike]) -> None:
    init_hf_modules()
    dynamic_module_path = (Path(HF_MODULES_CACHE) / name).resolve()
    if not dynamic_module_path.parent.exists(): create_dynamic_module(dynamic_module_path.parent)
    os.makedirs(dynamic_module_path, exist_ok=True)
    init_path = dynamic_module_path / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        importlib.invalidate_caches()
def get_relative_imports(module_file: Union[str, os.PathLike]) -> List[str]:
    with open(module_file, "r", encoding="utf-8") as f: content = f.read()
    relative_imports = re.findall(r"^\s*import\s+\.(\S+)\s*$", content, flags=re.MULTILINE)
    relative_imports += re.findall(r"^\s*from\s+\.(\S+)\s+import", content, flags=re.MULTILINE)
    return list(set(relative_imports))
def get_relative_import_files(module_file: Union[str, os.PathLike]) -> List[str]:
    no_change = False
    files_to_check = [module_file]
    all_relative_imports = []
    while not no_change:
        new_imports = []
        for f in files_to_check: new_imports.extend(get_relative_imports(f))
        module_path = Path(module_file).parent
        new_import_files = [str(module_path / m) for m in new_imports]
        new_import_files = [f for f in new_import_files if f not in all_relative_imports]
        files_to_check = [f"{f}.py" for f in new_import_files]
        no_change = len(new_import_files) == 0
        all_relative_imports.extend(files_to_check)
    return all_relative_imports
def get_imports(filename: Union[str, os.PathLike]) -> List[str]:
    with open(filename, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r"\s*try\s*:\s*.*?\s*except\s*.*?:", "", content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r"if is_flash_attn[a-zA-Z0-9_]+available\(\):\s*(from flash_attn\s*.*\s*)+", "", content, flags=re.MULTILINE)
    imports = re.findall(r"^\s*import\s+(\S+)\s*$", content, flags=re.MULTILINE)
    imports += re.findall(r"^\s*from\s+(\S+)\s+import", content, flags=re.MULTILINE)
    imports = [imp.split(".")[0] for imp in imports if not imp.startswith(".")]
    return list(set(imports))
def check_imports(filename: Union[str, os.PathLike]) -> List[str]:
    imports = get_imports(filename)
    missing_packages = []
    for imp in imports:
        try: importlib.import_module(imp)
        except ImportError as exception:
            logger.warning(f"Encountered exception while importing {imp}: {exception}")
            if "No module named" in str(exception): missing_packages.append(imp)
            else: raise
    if len(missing_packages) > 0: raise ImportError(f"This modeling file requires the following packages that were not found in your environment: {', '.join(missing_packages)}. Run `pip install {' '.join(missing_packages)}`")
    return get_relative_imports(filename)
def get_class_in_module(class_name: str, module_path: Union[str, os.PathLike], *, force_reload: bool = False) -> typing.Type:
    name = os.path.normpath(module_path)
    if name.endswith(".py"): name = name[:-3]
    name = name.replace(os.path.sep, ".")
    module_file: Path = Path(HF_MODULES_CACHE) / module_path
    with _HF_REMOTE_CODE_LOCK:
        if force_reload:
            sys.modules.pop(name, None)
            importlib.invalidate_caches()
        cached_module: Optional[ModuleType] = sys.modules.get(name)
        module_spec = importlib.util.spec_from_file_location(name, location=module_file)
        module_files: List[Path] = [module_file] + sorted(map(Path, get_relative_import_files(module_file)))
        module_hash: str = hashlib.sha256(b"".join(bytes(f) + f.read_bytes() for f in module_files)).hexdigest()
        module: ModuleType
        if cached_module is None:
            module = importlib.util.module_from_spec(module_spec)
            sys.modules[name] = module
        else: module = cached_module
        if getattr(module, "__transformers_module_hash__", "") != module_hash:
            module_spec.loader.exec_module(module)
            module.__transformers_module_hash__ = module_hash
        return getattr(module, class_name)
def get_cached_module_file(pretrained_model_name_or_path: Union[str, os.PathLike], module_file: str, cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False,
resume_download: Optional[bool] = None, proxies: Optional[Dict[str, str]] = None, token: Optional[Union[bool, str]] = None, revision: Optional[str] = None, local_files_only: bool = False,
repo_type: Optional[str] = None, _commit_hash: Optional[str] = None, **deprecated_kwargs) -> str:
    use_auth_token = deprecated_kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
        if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    if is_offline_mode() and not local_files_only:
        logger.info("Offline mode: forcing local_files_only=True")
        local_files_only = True
    pretrained_model_name_or_path = str(pretrained_model_name_or_path)
    is_local = os.path.isdir(pretrained_model_name_or_path)
    if is_local: submodule = os.path.basename(pretrained_model_name_or_path)
    else:
        submodule = pretrained_model_name_or_path.replace("/", os.path.sep)
        cached_module = try_to_load_from_cache(pretrained_model_name_or_path, module_file, cache_dir=cache_dir, revision=_commit_hash, repo_type=repo_type)
    new_files = []
    try:
        resolved_module_file = cached_file(pretrained_model_name_or_path, module_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies, resume_download=resume_download,
        local_files_only=local_files_only, token=token, revision=revision, repo_type=repo_type, _commit_hash=_commit_hash)
        if not is_local and cached_module != resolved_module_file: new_files.append(module_file)
    except EnvironmentError:
        logger.error(f"Could not locate the {module_file} inside {pretrained_model_name_or_path}.")
        raise
    modules_needed = check_imports(resolved_module_file)
    full_submodule = TRANSFORMERS_DYNAMIC_MODULE_NAME + os.path.sep + submodule
    create_dynamic_module(full_submodule)
    submodule_path = Path(HF_MODULES_CACHE) / full_submodule
    if submodule == os.path.basename(pretrained_model_name_or_path):
        if not (submodule_path / module_file).exists() or not filecmp.cmp(resolved_module_file, str(submodule_path / module_file)):
            shutil.copy(resolved_module_file, submodule_path / module_file)
            importlib.invalidate_caches()
        for module_needed in modules_needed:
            module_needed = f"{module_needed}.py"
            module_needed_file = os.path.join(pretrained_model_name_or_path, module_needed)
            if not (submodule_path / module_needed).exists() or not filecmp.cmp(module_needed_file, str(submodule_path / module_needed)):
                shutil.copy(module_needed_file, submodule_path / module_needed)
                importlib.invalidate_caches()
    else:
        commit_hash = extract_commit_hash(resolved_module_file, _commit_hash)
        submodule_path = submodule_path / commit_hash
        full_submodule = full_submodule + os.path.sep + commit_hash
        create_dynamic_module(full_submodule)
        if not (submodule_path / module_file).exists():
            shutil.copy(resolved_module_file, submodule_path / module_file)
            importlib.invalidate_caches()
        for module_needed in modules_needed:
            if not (submodule_path / f"{module_needed}.py").exists():
                get_cached_module_file(pretrained_model_name_or_path, f"{module_needed}.py", cache_dir=cache_dir, force_download=force_download, resume_download=resume_download,
                proxies=proxies, token=token, revision=revision, local_files_only=local_files_only, _commit_hash=commit_hash)
                new_files.append(f"{module_needed}.py")
    if len(new_files) > 0 and revision is None:
        new_files = "\n".join([f"- {f}" for f in new_files])
        repo_type_str = "" if repo_type is None else f"{repo_type}s/"
    return os.path.join(full_submodule, module_file)
def get_class_from_dynamic_module(class_reference: str, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False,
resume_download: Optional[bool] = None, proxies: Optional[Dict[str, str]] = None, token: Optional[Union[bool, str]] = None, revision: Optional[str] = None, local_files_only: bool = False, repo_type: Optional[str] = None, code_revision: Optional[str] = None, **kwargs) -> typing.Type:
    use_auth_token = kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
        if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    if "--" in class_reference: repo_id, class_reference = class_reference.split("--")
    else: repo_id = pretrained_model_name_or_path
    module_file, class_name = class_reference.split(".")
    if code_revision is None and pretrained_model_name_or_path == repo_id: code_revision = revision
    final_module = get_cached_module_file(repo_id, module_file + ".py", cache_dir=cache_dir, force_download=force_download, resume_download=resume_download, proxies=proxies, token=token, revision=code_revision, local_files_only=local_files_only, repo_type=repo_type)
    return get_class_in_module(class_name, final_module, force_reload=force_download)
def custom_object_save(obj: Any, folder: Union[str, os.PathLike], config: Optional[Dict] = None) -> List[str]:
    if obj.__module__ == "__main__":
        logger.warning(f"We can't save the code defining {obj} in {folder} as it's been defined in __main__. You should put this code in a separate module so we can include it in the saved folder and make it easier to share via the Hub.")
        return
    def _set_auto_map_in_config(_config):
        module_name = obj.__class__.__module__
        last_module = module_name.split(".")[-1]
        full_name = f"{last_module}.{obj.__class__.__name__}"
        if "Tokenizer" in full_name:
            slow_tokenizer_class = None
            fast_tokenizer_class = None
            if obj.__class__.__name__.endswith("Fast"):
                fast_tokenizer_class = f"{last_module}.{obj.__class__.__name__}"
                if getattr(obj, "slow_tokenizer_class", None) is not None:
                    slow_tokenizer = getattr(obj, "slow_tokenizer_class")
                    slow_tok_module_name = slow_tokenizer.__module__
                    last_slow_tok_module = slow_tok_module_name.split(".")[-1]
                    slow_tokenizer_class = f"{last_slow_tok_module}.{slow_tokenizer.__name__}"
            else: slow_tokenizer_class = f"{last_module}.{obj.__class__.__name__}"
            full_name = (slow_tokenizer_class, fast_tokenizer_class)
        if isinstance(_config, dict):
            auto_map = _config.get("auto_map", {})
            auto_map[obj._auto_class] = full_name
            _config["auto_map"] = auto_map
        elif getattr(_config, "auto_map", None) is not None: _config.auto_map[obj._auto_class] = full_name
        else: _config.auto_map = {obj._auto_class: full_name}
    if isinstance(config, (list, tuple)):
        for cfg in config: _set_auto_map_in_config(cfg)
    elif config is not None: _set_auto_map_in_config(config)
    result = []
    object_file = sys.modules[obj.__module__].__file__
    dest_file = Path(folder) / (Path(object_file).name)
    shutil.copy(object_file, dest_file)
    result.append(dest_file)
    for needed_file in get_relative_import_files(object_file):
        dest_file = Path(folder) / (Path(needed_file).name)
        shutil.copy(needed_file, dest_file)
        result.append(dest_file)
    return result
def _raise_timeout_error(signum, frame): raise ValueError("Loading this model requires you to execute custom code contained in the model repository on your local machine. Please set the option `trust_remote_code=True` to permit loading of this model.")
TIME_OUT_REMOTE_CODE = 15
def resolve_trust_remote_code(trust_remote_code, model_name, has_local_code, has_remote_code):
    if trust_remote_code is None:
        if has_local_code: trust_remote_code = False
        elif has_remote_code and TIME_OUT_REMOTE_CODE > 0:
            prev_sig_handler = None
            try:
                prev_sig_handler = signal.signal(signal.SIGALRM, _raise_timeout_error)
                signal.alarm(TIME_OUT_REMOTE_CODE)
                while trust_remote_code is None:
                    answer = input(f"The repository for {model_name} contains custom code which must be executed to correctly load the model. You can inspect the repository content at https://hf.co/{model_name}.\nYou can avoid this prompt in future by passing the argument `trust_remote_code=True`.\n\nDo you wish to run the custom code? [y/N] ")
                    if answer.lower() in ["yes", "y", "1"]: trust_remote_code = True
                    elif answer.lower() in ["no", "n", "0", ""]: trust_remote_code = False
                signal.alarm(0)
            except Exception: raise ValueError(f"The repository for {model_name} contains custom code which must be executed to correctly load the model. You can inspect the repository content at https://hf.co/{model_name}.\nPlease pass the argument `trust_remote_code=True` to allow custom code to be run.")
            finally:
                if prev_sig_handler is not None:
                    signal.signal(signal.SIGALRM, prev_sig_handler)
                    signal.alarm(0)
        elif has_remote_code: _raise_timeout_error(None, None)
    if has_remote_code and not has_local_code and not trust_remote_code: raise ValueError(f"Loading {model_name} requires you to execute the configuration file in that repo on your local machine. Make sure you have read the code there to avoid malicious use, then set the option `trust_remote_code=True` to remove this error.")
    return trust_remote_code
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
