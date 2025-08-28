'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..utils import CONFIG_NAME, FLAX_WEIGHTS_NAME, HUGGINGFACE_CO_RESOLVE_ENDPOINT, WEIGHTS_NAME, PushToHubMixin
from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError, validate_hf_hub_args
from .modeling_flax_pytorch_utils import convert_pytorch_state_dict_to_flax
from flax.traverse_util import flatten_dict, unflatten_dict
from huggingface_hub import create_repo, hf_hub_download
from flax.core.frozen_dict import FrozenDict, unfreeze
from flax.serialization import from_bytes, to_bytes
from .. import __version__, is_torch_available
from typing import Any, Dict, Union
from pickle import UnpicklingError
from requests import HTTPError
import msgpack.exceptions
import jax.numpy as jnp
import jax
import os
class FlaxModelMixin(PushToHubMixin):
    config_name = CONFIG_NAME
    _automatically_saved_args = ['_diffusers_version', '_class_name', '_name_or_path']
    _flax_internal_args = ['name', 'parent', 'dtype']
    @classmethod
    def _from_config(cls, config, **kwargs): return cls(config, **kwargs)
    def _cast_floating_to(self, params: Union[Dict, FrozenDict], dtype: jnp.dtype, mask: Any=None) -> Any:
        def conditional_cast(param):
            if isinstance(param, jnp.ndarray) and jnp.issubdtype(param.dtype, jnp.floating): param = param.astype(dtype)
            return param
        if mask is None: return jax.tree_map(conditional_cast, params)
        flat_params = flatten_dict(params)
        flat_mask, _ = jax.tree_flatten(mask)
        for masked, key in zip(flat_mask, flat_params.keys()):
            if masked:
                param = flat_params[key]
                flat_params[key] = conditional_cast(param)
        return unflatten_dict(flat_params)
    def to_bf16(self, params: Union[Dict, FrozenDict], mask: Any=None):
        """Examples:"""
        return self._cast_floating_to(params, jnp.bfloat16, mask)
    def to_fp32(self, params: Union[Dict, FrozenDict], mask: Any=None):
        """Examples:"""
        return self._cast_floating_to(params, jnp.float32, mask)
    def to_fp16(self, params: Union[Dict, FrozenDict], mask: Any=None):
        """Examples:"""
        return self._cast_floating_to(params, jnp.float16, mask)
    def init_weights(self, rng: jax.Array) -> Dict: raise NotImplementedError(f'init_weights method has to be implemented for {self}')
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], dtype: jnp.dtype=jnp.float32, *model_args, **kwargs):
        """Examples:"""
        config = kwargs.pop('config', None)
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        from_pt = kwargs.pop('from_pt', False)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', False)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        subfolder = kwargs.pop('subfolder', None)
        user_agent = {'sapiens_transformers.diffusers': __version__, 'file_type': 'model', 'framework': 'flax'}
        if config is None: config, unused_kwargs = cls.load_config(pretrained_model_name_or_path, cache_dir=cache_dir, return_unused_kwargs=True, force_download=force_download, proxies=proxies,
        local_files_only=local_files_only, token=token, revision=revision, subfolder=subfolder, **kwargs)
        model, model_kwargs = cls.from_config(config, dtype=dtype, return_unused_kwargs=True, **unused_kwargs)
        pretrained_path_with_subfolder = pretrained_model_name_or_path if subfolder is None else os.path.join(pretrained_model_name_or_path, subfolder)
        if os.path.isdir(pretrained_path_with_subfolder):
            if from_pt:
                if not os.path.isfile(os.path.join(pretrained_path_with_subfolder, WEIGHTS_NAME)): raise EnvironmentError(f'Error no file named {WEIGHTS_NAME} found in directory {pretrained_path_with_subfolder} ')
                model_file = os.path.join(pretrained_path_with_subfolder, WEIGHTS_NAME)
            elif os.path.isfile(os.path.join(pretrained_path_with_subfolder, FLAX_WEIGHTS_NAME)): model_file = os.path.join(pretrained_path_with_subfolder, FLAX_WEIGHTS_NAME)
            elif os.path.isfile(os.path.join(pretrained_path_with_subfolder, WEIGHTS_NAME)): raise EnvironmentError(f'{WEIGHTS_NAME} file found in directory {pretrained_path_with_subfolder}. Please load the model using `from_pt=True`.')
            else: raise EnvironmentError(f'Error no file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME} found in directory {pretrained_path_with_subfolder}.')
        else:
            try: model_file = hf_hub_download(pretrained_model_name_or_path, filename=FLAX_WEIGHTS_NAME if not from_pt else WEIGHTS_NAME, cache_dir=cache_dir,
            force_download=force_download, proxies=proxies, local_files_only=local_files_only, token=token, user_agent=user_agent, subfolder=subfolder, revision=revision)
            except RepositoryNotFoundError: raise EnvironmentError(f"{pretrained_model_name_or_path} is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'\nIf this is a private repository, make sure to pass a token having permission to this repo with `token` or log in with `huggingface-cli login`.")
            except RevisionNotFoundError: raise EnvironmentError(f"{revision} is not a valid git identifier (branch name, tag name or commit id) that exists for this model name. Check the model page at 'https://huggingface.co/{pretrained_model_name_or_path}' for available revisions.")
            except EntryNotFoundError: raise EnvironmentError(f'{pretrained_model_name_or_path} does not appear to have a file named {FLAX_WEIGHTS_NAME}.')
            except HTTPError as err: raise EnvironmentError(f'There was a specific connection error when trying to load {pretrained_model_name_or_path}:\n{err}')
            except ValueError: raise EnvironmentError(f"We couldn't connect to '{HUGGINGFACE_CO_RESOLVE_ENDPOINT}' to load this model, couldn't find it in the cached files and it looks like {pretrained_model_name_or_path} is not the path to a directory containing a file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME}.\nCheckout your internet connection or see how to run the library in offline mode at 'https://huggingface.co/docs/transformers/installation#offline-mode'.")
            except EnvironmentError: raise EnvironmentError(f"Can't load the model for '{pretrained_model_name_or_path}'. If you were trying to load it from 'https://huggingface.co/models', make sure you don't have a local directory with the same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a file named {FLAX_WEIGHTS_NAME} or {WEIGHTS_NAME}.")
        if from_pt:
            if is_torch_available(): from .modeling_utils import load_state_dict
            else: raise EnvironmentError("Can't load the model in PyTorch format because PyTorch is not installed. Please, install PyTorch or use native Flax weights.")
            pytorch_model_file = load_state_dict(model_file)
            state = convert_pytorch_state_dict_to_flax(pytorch_model_file, model)
        else:
            try:
                with open(model_file, 'rb') as state_f: state = from_bytes(cls, state_f.read())
            except (UnpicklingError, msgpack.exceptions.ExtraData) as e:
                try:
                    with open(model_file) as f:
                        if f.read().startswith('version'): raise OSError('You seem to have cloned a repository without having git-lfs installed. Please install git-lfs and run `git lfs install` followed by `git lfs pull` in the folder you cloned.')
                        else: raise ValueError from e
                except (UnicodeDecodeError, ValueError): raise EnvironmentError(f'Unable to convert {model_file} to Flax deserializable object. ')
        state = jax.tree_util.tree_map(lambda x: jax.device_put(x, jax.local_devices(backend='cpu')[0]), state)
        state = flatten_dict(state)
        params_shape_tree = jax.eval_shape(model.init_weights, rng=jax.random.PRNGKey(0))
        required_params = set(flatten_dict(unfreeze(params_shape_tree)).keys())
        shape_state = flatten_dict(unfreeze(params_shape_tree))
        missing_keys = required_params - set(state.keys())
        unexpected_keys = set(state.keys()) - required_params
        if missing_keys: cls._missing_keys = missing_keys
        for key in state.keys():
            if key in shape_state and state[key].shape != shape_state[key].shape: raise ValueError(f'Trying to load the pretrained weight for {key} failed: checkpoint has shape {state[key].shape} which is incompatible with the model shape {shape_state[key].shape}. ')
        for unexpected_key in unexpected_keys: del state[unexpected_key]
        return (model, unflatten_dict(state))
    def save_pretrained(self, save_directory: Union[str, os.PathLike], params: Union[Dict, FrozenDict], is_main_process: bool=True, push_to_hub: bool=False, **kwargs):
        if os.path.isfile(save_directory): return
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop('commit_message', None)
            private = kwargs.pop('private', None)
            create_pr = kwargs.pop('create_pr', False)
            token = kwargs.pop('token', None)
            repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
            repo_id = create_repo(repo_id, exist_ok=True, private=private, token=token).repo_id
        model_to_save = self
        if is_main_process: model_to_save.save_config(save_directory)
        output_model_file = os.path.join(save_directory, FLAX_WEIGHTS_NAME)
        with open(output_model_file, 'wb') as f:
            model_bytes = to_bytes(params)
            f.write(model_bytes)
        if push_to_hub: self._upload_folder(save_directory, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
