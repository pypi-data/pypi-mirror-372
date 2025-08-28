"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils.versions import require_version, require_version_core
from .dependency_versions_table import deps
pkgs_to_check_at_runtime = ["python", "tqdm", "regex", "requests", "packaging", "filelock", "numpy", "tokenizers", "huggingface-hub", "safetensors", "sapiens_accelerator", "pyyaml"]
for pkg in pkgs_to_check_at_runtime:
    if pkg in deps:
        if pkg == "tokenizers":
            from .utils import is_tokenizers_available
            if not is_tokenizers_available(): continue
        elif pkg == "sapiens_accelerator":
            from .utils import is_sapiens_accelerator_available
            if not is_sapiens_accelerator_available(): continue
        require_version_core(deps[pkg])
    else: raise ValueError(f"can't find {pkg} in {deps.keys()}, check dependency_versions_table.py")
def dep_version_check(pkg, hint=None): require_version(deps[pkg], hint)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
