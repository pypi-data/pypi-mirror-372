'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError, validate_hf_hub_args
from .utils import HUGGINGFACE_CO_RESOLVE_ENDPOINT, DummyObject, deprecate, extract_commit_hash, http_user_agent
from huggingface_hub import create_repo, hf_hub_download
from typing import Any, Dict, Tuple, Union
from collections import OrderedDict
from requests import HTTPError
from . import __version__
from pathlib import Path
import dataclasses
import numpy as np
import functools
import importlib
import inspect
import json
import os
import re
_re_configuration_file = re.compile('config\\.(.*)\\.json')
class FrozenDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items(): setattr(self, key, value)
        self.__frozen = True
    def __delitem__(self, *args, **kwargs): raise Exception(f'You cannot use ``__delitem__`` on a {self.__class__.__name__} instance.')
    def setdefault(self, *args, **kwargs): raise Exception(f'You cannot use ``setdefault`` on a {self.__class__.__name__} instance.')
    def pop(self, *args, **kwargs): raise Exception(f'You cannot use ``pop`` on a {self.__class__.__name__} instance.')
    def update(self, *args, **kwargs): raise Exception(f'You cannot use ``update`` on a {self.__class__.__name__} instance.')
    def __setattr__(self, name, value):
        if hasattr(self, '__frozen') and self.__frozen: raise Exception(f'You cannot use ``__setattr__`` on a {self.__class__.__name__} instance.')
        super().__setattr__(name, value)
    def __setitem__(self, name, value):
        if hasattr(self, '__frozen') and self.__frozen: raise Exception(f'You cannot use ``__setattr__`` on a {self.__class__.__name__} instance.')
        super().__setitem__(name, value)
class ConfigMixin:
    config_name = None
    ignore_for_config = []
    has_compatibles = False
    _deprecated_kwargs = []
    def register_to_config(self, **kwargs):
        if self.config_name is None: raise NotImplementedError(f'Make sure that {self.__class__} has defined a class name `config_name`')
        kwargs.pop('kwargs', None)
        if not hasattr(self, '_internal_dict'): internal_dict = kwargs
        else:
            previous_dict = dict(self._internal_dict)
            internal_dict = {**self._internal_dict, **kwargs}
        self._internal_dict = FrozenDict(internal_dict)
    def __getattr__(self, name: str) -> Any:
        is_in_config = '_internal_dict' in self.__dict__ and hasattr(self.__dict__['_internal_dict'], name)
        is_attribute = name in self.__dict__
        if is_in_config and (not is_attribute):
            deprecation_message = f"Accessing config attribute `{name}` directly via '{type(self).__name__}' object attribute is deprecated. Please access '{name}' over '{type(self).__name__}'s config object instead, e.g. 'scheduler.config.{name}'."
            deprecate('direct config name access', '1.0.0', deprecation_message, standard_warn=False)
            return self._internal_dict[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    def save_config(self, save_directory: Union[str, os.PathLike], push_to_hub: bool=False, **kwargs):
        """Args:"""
        if os.path.isfile(save_directory): raise AssertionError(f'Provided path ({save_directory}) should be a directory, not a file')
        os.makedirs(save_directory, exist_ok=True)
        output_config_file = os.path.join(save_directory, self.config_name)
        self.to_json_file(output_config_file)
        if push_to_hub:
            commit_message = kwargs.pop('commit_message', None)
            private = kwargs.pop('private', None)
            create_pr = kwargs.pop('create_pr', False)
            token = kwargs.pop('token', None)
            repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
            repo_id = create_repo(repo_id, exist_ok=True, private=private, token=token).repo_id
            self._upload_folder(save_directory, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
    @classmethod
    def from_config(cls, config: Union[FrozenDict, Dict[str, Any]]=None, return_unused_kwargs=False, **kwargs):
        """Examples:"""
        if 'pretrained_model_name_or_path' in kwargs: config = kwargs.pop('pretrained_model_name_or_path')
        if config is None: raise ValueError('Please make sure to provide a config as the first positional argument.')
        if not isinstance(config, dict):
            deprecation_message = 'It is deprecated to pass a pretrained model name or path to `from_config`.'
            if 'Scheduler' in cls.__name__: deprecation_message += f'If you were trying to load a scheduler, please use {cls}.from_pretrained(...) instead. Otherwise, please make sure to pass a configuration dictionary instead. This functionality will be removed in v1.0.0.'
            elif 'Model' in cls.__name__: deprecation_message += f'If you were trying to load a model, please use {cls}.load_config(...) followed by {cls}.from_config(...) instead. Otherwise, please make sure to pass a configuration dictionary instead. This functionality will be removed in v1.0.0.'
            deprecate('config-passed-as-path', '1.0.0', deprecation_message, standard_warn=False)
            config, kwargs = cls.load_config(pretrained_model_name_or_path=config, return_unused_kwargs=True, **kwargs)
        init_dict, unused_kwargs, hidden_dict = cls.extract_init_dict(config, **kwargs)
        if 'dtype' in unused_kwargs: init_dict['dtype'] = unused_kwargs.pop('dtype')
        for deprecated_kwarg in cls._deprecated_kwargs:
            if deprecated_kwarg in unused_kwargs: init_dict[deprecated_kwarg] = unused_kwargs.pop(deprecated_kwarg)
        model = cls(**init_dict)
        if '_class_name' in hidden_dict: hidden_dict['_class_name'] = cls.__name__
        model.register_to_config(**hidden_dict)
        unused_kwargs = {**unused_kwargs, **hidden_dict}
        if return_unused_kwargs: return (model, unused_kwargs)
        else: return model
    @classmethod
    def get_config_dict(cls, *args, **kwargs):
        deprecation_message = f' The function get_config_dict is deprecated. Please use {cls}.load_config instead. This function will be removed in version v1.0.0'
        deprecate('get_config_dict', '1.0.0', deprecation_message, standard_warn=False)
        return cls.load_config(*args, **kwargs)
    @classmethod
    @validate_hf_hub_args
    def load_config(cls, pretrained_model_name_or_path: Union[str, os.PathLike], return_unused_kwargs=False, return_commit_hash=False, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Returns:"""
        cache_dir = kwargs.pop('cache_dir', None)
        local_dir = kwargs.pop('local_dir', None)
        local_dir_use_symlinks = kwargs.pop('local_dir_use_symlinks', 'auto')
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        local_files_only = kwargs.pop('local_files_only', False)
        revision = kwargs.pop('revision', None)
        _ = kwargs.pop('mirror', None)
        subfolder = kwargs.pop('subfolder', None)
        user_agent = kwargs.pop('user_agent', {})
        user_agent = {**user_agent, 'file_type': 'config'}
        user_agent = http_user_agent(user_agent)
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        if cls.config_name is None: raise ValueError('`self.config_name` is not defined. Note that one should not load a config from `ConfigMixin`. Please make sure to define `config_name` in a class inheriting from `ConfigMixin`')
        if os.path.isfile(pretrained_model_name_or_path): config_file = pretrained_model_name_or_path
        elif os.path.isdir(pretrained_model_name_or_path):
            if subfolder is not None and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, cls.config_name)): config_file = os.path.join(pretrained_model_name_or_path, subfolder, cls.config_name)
            elif os.path.isfile(os.path.join(pretrained_model_name_or_path, cls.config_name)): config_file = os.path.join(pretrained_model_name_or_path, cls.config_name)
            else: raise EnvironmentError(f'Error no file named {cls.config_name} found in directory {pretrained_model_name_or_path}.')
        else:
            try: config_file = hf_hub_download(pretrained_model_name_or_path, filename=cls.config_name, cache_dir=cache_dir, force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, user_agent=user_agent, subfolder=subfolder, revision=revision, local_dir=local_dir, local_dir_use_symlinks=local_dir_use_symlinks)
            except RepositoryNotFoundError: raise EnvironmentError(f"{pretrained_model_name_or_path} is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'\nIf this is a private repository, make sure to pass a token having permission to this repo with `token` or log in with `huggingface-cli login`.")
            except RevisionNotFoundError: raise EnvironmentError(f"{revision} is not a valid git identifier (branch name, tag name or commit id) that exists for this model name. Check the model page at 'https://huggingface.co/{pretrained_model_name_or_path}' for available revisions.")
            except EntryNotFoundError: raise EnvironmentError(f'{pretrained_model_name_or_path} does not appear to have a file named {cls.config_name}.')
            except HTTPError as err: raise EnvironmentError(f'There was a specific connection error when trying to load {pretrained_model_name_or_path}:\n{err}')
            except ValueError: raise EnvironmentError(f"We couldn't connect to '{HUGGINGFACE_CO_RESOLVE_ENDPOINT}' to load this model, couldn't find it in the cached files and it looks like {pretrained_model_name_or_path} is not the path to a directory containing a {cls.config_name} file.\nCheckout your internet connection or see how to run the library in offline mode at 'https://huggingface.co/docs/diffusers/installation#offline-mode'.")
            except EnvironmentError: raise EnvironmentError(f"Can't load config for '{pretrained_model_name_or_path}'. If you were trying to load it from 'https://huggingface.co/models', make sure you don't have a local directory with the same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a {cls.config_name} file")
        try:
            config_dict = cls._dict_from_json_file(config_file)
            commit_hash = extract_commit_hash(config_file)
        except (json.JSONDecodeError, UnicodeDecodeError): raise EnvironmentError(f"It looks like the config file at '{config_file}' is not a valid JSON file.")
        if not (return_unused_kwargs or return_commit_hash): return config_dict
        outputs = (config_dict,)
        if return_unused_kwargs: outputs += (kwargs,)
        if return_commit_hash: outputs += (commit_hash,)
        return outputs
    @staticmethod
    def _get_init_keys(input_class): return set(dict(inspect.signature(input_class.__init__).parameters).keys())
    @classmethod
    def extract_init_dict(cls, config_dict, **kwargs):
        used_defaults = config_dict.get('_use_default_values', [])
        config_dict = {k: v for k, v in config_dict.items() if k not in used_defaults and k != '_use_default_values'}
        original_dict = dict(config_dict.items())
        expected_keys = cls._get_init_keys(cls)
        expected_keys.remove('self')
        if 'kwargs' in expected_keys: expected_keys.remove('kwargs')
        if hasattr(cls, '_flax_internal_args'):
            for arg in cls._flax_internal_args: expected_keys.remove(arg)
        if len(cls.ignore_for_config) > 0: expected_keys = expected_keys - set(cls.ignore_for_config)
        diffusers_library = importlib.import_module(__name__.split('.')[0])
        if cls.has_compatibles: compatible_classes = [c for c in cls._get_compatibles() if not isinstance(c, DummyObject)]
        else: compatible_classes = []
        expected_keys_comp_cls = set()
        for c in compatible_classes:
            expected_keys_c = cls._get_init_keys(c)
            expected_keys_comp_cls = expected_keys_comp_cls.union(expected_keys_c)
        expected_keys_comp_cls = expected_keys_comp_cls - cls._get_init_keys(cls)
        config_dict = {k: v for k, v in config_dict.items() if k not in expected_keys_comp_cls}
        orig_cls_name = config_dict.pop('_class_name', cls.__name__)
        if isinstance(orig_cls_name, str) and orig_cls_name != cls.__name__ and hasattr(diffusers_library, orig_cls_name):
            orig_cls = getattr(diffusers_library, orig_cls_name)
            unexpected_keys_from_orig = cls._get_init_keys(orig_cls) - expected_keys
            config_dict = {k: v for k, v in config_dict.items() if k not in unexpected_keys_from_orig}
        elif not isinstance(orig_cls_name, str) and (not isinstance(orig_cls_name, (list, tuple))): raise ValueError('Make sure that the `_class_name` is of type string or list of string (for custom pipelines).')
        config_dict = {k: v for k, v in config_dict.items() if not k.startswith('_')}
        config_dict = {k: v for k, v in config_dict.items() if k != 'quantization_config'}
        init_dict = {}
        for key in expected_keys:
            if key in kwargs and key in config_dict: config_dict[key] = kwargs.pop(key)
            if key in kwargs: init_dict[key] = kwargs.pop(key)
            elif key in config_dict: init_dict[key] = config_dict.pop(key)
        passed_keys = set(init_dict.keys())
        unused_kwargs = {**config_dict, **kwargs}
        hidden_config_dict = {k: v for k, v in original_dict.items() if k not in init_dict}
        return (init_dict, unused_kwargs, hidden_config_dict)
    @classmethod
    def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, 'r', encoding='utf-8') as reader: text = reader.read()
        return json.loads(text)
    def __repr__(self): return f'{self.__class__.__name__} {self.to_json_string()}'
    @property
    def config(self) -> Dict[str, Any]:
        """Returns:"""
        return self._internal_dict
    def to_json_string(self) -> str:
        """Returns:"""
        config_dict = self._internal_dict if hasattr(self, '_internal_dict') else {}
        config_dict['_class_name'] = self.__class__.__name__
        config_dict['_diffusers_version'] = __version__
        def to_json_saveable(value):
            if isinstance(value, np.ndarray): value = value.tolist()
            elif isinstance(value, Path): value = value.as_posix()
            return value
        if 'quantization_config' in config_dict: config_dict['quantization_config'] = config_dict.quantization_config.to_dict() if not isinstance(config_dict.quantization_config, dict) else config_dict.quantization_config
        config_dict = {k: to_json_saveable(v) for k, v in config_dict.items()}
        config_dict.pop('_ignore_files', None)
        config_dict.pop('_use_default_values', None)
        _ = config_dict.pop('_pre_quantization_dtype', None)
        return json.dumps(config_dict, indent=2, sort_keys=True) + '\n'
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        """Args:"""
        with open(json_file_path, 'w', encoding='utf-8') as writer: writer.write(self.to_json_string())
def register_to_config(init):
    @functools.wraps(init)
    def inner_init(self, *args, **kwargs):
        init_kwargs = {k: v for k, v in kwargs.items() if not k.startswith('_')}
        config_init_kwargs = {k: v for k, v in kwargs.items() if k.startswith('_')}
        if not isinstance(self, ConfigMixin): raise RuntimeError(f'`@register_for_config` was applied to {self.__class__.__name__} init method, but this class does not inherit from `ConfigMixin`.')
        ignore = getattr(self, 'ignore_for_config', [])
        new_kwargs = {}
        signature = inspect.signature(init)
        parameters = {name: p.default for i, (name, p) in enumerate(signature.parameters.items()) if i > 0 and name not in ignore}
        for arg, name in zip(args, parameters.keys()): new_kwargs[name] = arg
        new_kwargs.update({k: init_kwargs.get(k, default) for k, default in parameters.items() if k not in ignore and k not in new_kwargs})
        if len(set(new_kwargs.keys()) - set(init_kwargs)) > 0: new_kwargs['_use_default_values'] = list(set(new_kwargs.keys()) - set(init_kwargs))
        new_kwargs = {**config_init_kwargs, **new_kwargs}
        getattr(self, 'register_to_config')(**new_kwargs)
        init(self, *args, **init_kwargs)
    return inner_init
def flax_register_to_config(cls):
    original_init = cls.__init__
    @functools.wraps(original_init)
    def init(self, *args, **kwargs):
        if not isinstance(self, ConfigMixin): raise RuntimeError(f'`@register_for_config` was applied to {self.__class__.__name__} init method, but this class does not inherit from `ConfigMixin`.')
        init_kwargs = dict(kwargs.items())
        fields = dataclasses.fields(self)
        default_kwargs = {}
        for field in fields:
            if field.name in self._flax_internal_args: continue
            if type(field.default) == dataclasses._MISSING_TYPE: default_kwargs[field.name] = None
            else: default_kwargs[field.name] = getattr(self, field.name)
        new_kwargs = {**default_kwargs, **init_kwargs}
        if 'dtype' in new_kwargs: new_kwargs.pop('dtype')
        for i, arg in enumerate(args):
            name = fields[i].name
            new_kwargs[name] = arg
        if len(set(new_kwargs.keys()) - set(init_kwargs)) > 0: new_kwargs['_use_default_values'] = list(set(new_kwargs.keys()) - set(init_kwargs))
        getattr(self, 'register_to_config')(**new_kwargs)
        original_init(self, *args, **kwargs)
    cls.__init__ = init
    return cls
class LegacyConfigMixin(ConfigMixin):
    @classmethod
    def from_config(cls, config: Union[FrozenDict, Dict[str, Any]]=None, return_unused_kwargs=False, **kwargs):
        from .models.model_loading_utils import _fetch_remapped_cls_from_config
        remapped_class = _fetch_remapped_cls_from_config(config, cls)
        return remapped_class.from_config(config, return_unused_kwargs, **kwargs)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
