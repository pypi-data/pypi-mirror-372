'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import importlib
import inspect
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional, Union
from urllib import request
from huggingface_hub import hf_hub_download, model_info
from huggingface_hub.utils import RevisionNotFoundError, validate_hf_hub_args
from packaging import version
from .. import __version__
from . import DIFFUSERS_DYNAMIC_MODULE_NAME, HF_MODULES_CACHE
COMMUNITY_PIPELINES_MIRROR_ID = 'sapiens_transformers.diffusers/community-pipelines-mirror'
def get_diffusers_versions():
    url = 'https://pypi.org/pypi/diffusers/json'
    releases = json.loads(request.urlopen(url).read())['releases'].keys()
    return sorted(releases, key=lambda x: version.Version(x))
def init_hf_modules():
    if HF_MODULES_CACHE in sys.path: return
    sys.path.append(HF_MODULES_CACHE)
    os.makedirs(HF_MODULES_CACHE, exist_ok=True)
    init_path = Path(HF_MODULES_CACHE) / '__init__.py'
    if not init_path.exists(): init_path.touch()
def create_dynamic_module(name: Union[str, os.PathLike]):
    init_hf_modules()
    dynamic_module_path = Path(HF_MODULES_CACHE) / name
    if not dynamic_module_path.parent.exists(): create_dynamic_module(dynamic_module_path.parent)
    os.makedirs(dynamic_module_path, exist_ok=True)
    init_path = dynamic_module_path / '__init__.py'
    if not init_path.exists(): init_path.touch()
def get_relative_imports(module_file):
    """Args:"""
    with open(module_file, 'r', encoding='utf-8') as f: content = f.read()
    relative_imports = re.findall('^\\s*import\\s+\\.(\\S+)\\s*$', content, flags=re.MULTILINE)
    relative_imports += re.findall('^\\s*from\\s+\\.(\\S+)\\s+import', content, flags=re.MULTILINE)
    return list(set(relative_imports))
def get_relative_import_files(module_file):
    """Args:"""
    no_change = False
    files_to_check = [module_file]
    all_relative_imports = []
    while not no_change:
        new_imports = []
        for f in files_to_check: new_imports.extend(get_relative_imports(f))
        module_path = Path(module_file).parent
        new_import_files = [str(module_path / m) for m in new_imports]
        new_import_files = [f for f in new_import_files if f not in all_relative_imports]
        files_to_check = [f'{f}.py' for f in new_import_files]
        no_change = len(new_import_files) == 0
        all_relative_imports.extend(files_to_check)
    return all_relative_imports
def check_imports(filename):
    with open(filename, 'r', encoding='utf-8') as f: content = f.read()
    imports = re.findall('^\\s*import\\s+(\\S+)\\s*$', content, flags=re.MULTILINE)
    imports += re.findall('^\\s*from\\s+(\\S+)\\s+import', content, flags=re.MULTILINE)
    imports = [imp.split('.')[0] for imp in imports if not imp.startswith('.')]
    imports = list(set(imports))
    missing_packages = []
    for imp in imports:
        try: importlib.import_module(imp)
        except ImportError: missing_packages.append(imp)
    if len(missing_packages) > 0: raise ImportError(f"This modeling file requires the following packages that were not found in your environment: {', '.join(missing_packages)}. Run `pip install {' '.join(missing_packages)}`")
    return get_relative_imports(filename)
def get_class_in_module(class_name, module_path):
    module_path = module_path.replace(os.path.sep, '.')
    module = importlib.import_module(module_path)
    if class_name is None: return find_pipeline_class(module)
    return getattr(module, class_name)
def find_pipeline_class(loaded_module):
    from ..pipelines import DiffusionPipeline
    cls_members = dict(inspect.getmembers(loaded_module, inspect.isclass))
    pipeline_class = None
    for cls_name, cls in cls_members.items():
        if cls_name != DiffusionPipeline.__name__ and issubclass(cls, DiffusionPipeline) and (cls.__module__.split('.')[0] != 'sapiens_transformers.diffusers'):
            if pipeline_class is not None: raise ValueError(f'Multiple classes that inherit from {DiffusionPipeline.__name__} have been found: {pipeline_class.__name__}, and {cls_name}. Please make sure to define only one in {loaded_module}.')
            pipeline_class = cls
    return pipeline_class
@validate_hf_hub_args
def get_cached_module_file(pretrained_model_name_or_path: Union[str, os.PathLike], module_file: str, cache_dir: Optional[Union[str, os.PathLike]]=None, force_download: bool=False,
proxies: Optional[Dict[str, str]]=None, token: Optional[Union[bool, str]]=None, revision: Optional[str]=None, local_files_only: bool=False):
    """Returns:"""
    pretrained_model_name_or_path = str(pretrained_model_name_or_path)
    module_file_or_url = os.path.join(pretrained_model_name_or_path, module_file)
    if os.path.isfile(module_file_or_url):
        resolved_module_file = module_file_or_url
        submodule = 'local'
    elif pretrained_model_name_or_path.count('/') == 0:
        available_versions = get_diffusers_versions()
        latest_version = 'v' + '.'.join(__version__.split('.')[:3])
        if revision is None: revision = latest_version if latest_version[1:] in available_versions else 'main'
        elif revision in available_versions: revision = f'v{revision}'
        elif revision == 'main': revision = revision
        else: raise ValueError(f"`custom_revision`: {revision} does not exist. Please make sure to choose one of {', '.join(available_versions + ['main'])}.")
        try:
            resolved_module_file = hf_hub_download(repo_id=COMMUNITY_PIPELINES_MIRROR_ID, repo_type='dataset', filename=f'{revision}/{pretrained_model_name_or_path}.py',
            cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only)
            submodule = 'git'
            module_file = pretrained_model_name_or_path + '.py'
        except RevisionNotFoundError as e: raise EnvironmentError(f"Revision '{revision}' not found in the community pipelines mirror. Check available revisions on https://huggingface.co/datasets/diffusers/community-pipelines-mirror/tree/main. If you don't find the revision you are looking for, please open an issue on https://github.com/huggingface/diffusers/issues.") from e
        except EnvironmentError: raise
    else:
        try:
            resolved_module_file = hf_hub_download(pretrained_model_name_or_path, module_file, cache_dir=cache_dir, force_download=force_download,
            proxies=proxies, local_files_only=local_files_only, token=token)
            submodule = os.path.join('local', '--'.join(pretrained_model_name_or_path.split('/')))
        except EnvironmentError: raise
    modules_needed = check_imports(resolved_module_file)
    full_submodule = DIFFUSERS_DYNAMIC_MODULE_NAME + os.path.sep + submodule
    create_dynamic_module(full_submodule)
    submodule_path = Path(HF_MODULES_CACHE) / full_submodule
    if submodule == 'local' or submodule == 'git':
        shutil.copyfile(resolved_module_file, submodule_path / module_file)
        for module_needed in modules_needed:
            if len(module_needed.split('.')) == 2:
                module_needed = '/'.join(module_needed.split('.'))
                module_folder = module_needed.split('/')[0]
                if not os.path.exists(submodule_path / module_folder): os.makedirs(submodule_path / module_folder)
            module_needed = f'{module_needed}.py'
            shutil.copyfile(os.path.join(pretrained_model_name_or_path, module_needed), submodule_path / module_needed)
    else:
        commit_hash = model_info(pretrained_model_name_or_path, revision=revision, token=token).sha
        submodule_path = submodule_path / commit_hash
        full_submodule = full_submodule + os.path.sep + commit_hash
        create_dynamic_module(full_submodule)
        if not (submodule_path / module_file).exists():
            if len(module_file.split('/')) == 2:
                module_folder = module_file.split('/')[0]
                if not os.path.exists(submodule_path / module_folder): os.makedirs(submodule_path / module_folder)
            shutil.copyfile(resolved_module_file, submodule_path / module_file)
        for module_needed in modules_needed:
            if len(module_needed.split('.')) == 2: module_needed = '/'.join(module_needed.split('.'))
            if not (submodule_path / module_needed).exists(): get_cached_module_file(pretrained_model_name_or_path, f'{module_needed}.py', cache_dir=cache_dir, force_download=force_download,
            proxies=proxies, token=token, revision=revision, local_files_only=local_files_only)
    return os.path.join(full_submodule, module_file)
@validate_hf_hub_args
def get_class_from_dynamic_module(pretrained_model_name_or_path: Union[str, os.PathLike], module_file: str, class_name: Optional[str]=None, cache_dir: Optional[Union[str, os.PathLike]]=None,
force_download: bool=False, proxies: Optional[Dict[str, str]]=None, token: Optional[Union[bool, str]]=None, revision: Optional[str]=None, local_files_only: bool=False, **kwargs):
    """Examples:"""
    final_module = get_cached_module_file(pretrained_model_name_or_path, module_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies,
    token=token, revision=revision, local_files_only=local_files_only)
    return get_class_in_module(class_name, final_module.replace('.py', ''))
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
