"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (FEATURE_EXTRACTOR_NAME, PushToHubMixin, TensorType, add_model_info_to_auto_map, add_model_info_to_custom_pipelines, cached_file, copy_func, download_url,
is_flax_available, is_jax_tensor, is_numpy_array, is_offline_mode, is_remote_url, is_tf_available, is_torch_available, is_torch_device, is_torch_dtype, logging, requires_backends)
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union
from .dynamic_module_utils import custom_object_save
from collections import UserDict
import numpy as np
import warnings
import copy
import json
import os
if TYPE_CHECKING:
    if is_torch_available(): import torch
logger = logging.get_logger(__name__)
PreTrainedFeatureExtractor = Union["SequenceFeatureExtractor"]
class BatchFeature(UserDict):
    def __init__(self, data: Optional[Dict[str, Any]] = None, tensor_type: Union[None, str, TensorType] = None):
        super().__init__(data)
        self.convert_to_tensors(tensor_type=tensor_type)
    def __getitem__(self, item: str) -> Union[Any]:
        if isinstance(item, str): return self.data[item]
        else: raise KeyError("Indexing with integers is not available when using Python based feature extractors")
    def __getattr__(self, item: str):
        try: return self.data[item]
        except KeyError: raise AttributeError
    def __getstate__(self): return {"data": self.data}
    def __setstate__(self, state):
        if "data" in state: self.data = state["data"]
    def keys(self): return self.data.keys()
    def values(self): return self.data.values()
    def items(self): return self.data.items()
    def _get_is_as_tensor_fns(self, tensor_type: Optional[Union[str, TensorType]] = None):
        if tensor_type is None: return None, None
        if not isinstance(tensor_type, TensorType): tensor_type = TensorType(tensor_type)
        if tensor_type == TensorType.TENSORFLOW:
            if not is_tf_available(): raise ImportError("Unable to convert output to TensorFlow tensors format, TensorFlow is not installed.")
            import tensorflow as tf
            as_tensor = tf.constant
            is_tensor = tf.is_tensor
        elif tensor_type == TensorType.PYTORCH:
            if not is_torch_available(): raise ImportError("Unable to convert output to PyTorch tensors format, PyTorch is not installed.")
            import torch
            def as_tensor(value):
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    if isinstance(value[0], np.ndarray): value = np.array(value)
                    elif (isinstance(value[0], (list, tuple)) and len(value[0]) > 0 and isinstance(value[0][0], np.ndarray)): value = np.array(value)
                if isinstance(value, np.ndarray): return torch.from_numpy(value)
                else: return torch.tensor(value)
            is_tensor = torch.is_tensor
        elif tensor_type == TensorType.JAX:
            if not is_flax_available(): raise ImportError("Unable to convert output to JAX tensors format, JAX is not installed.")
            import jax.numpy as jnp
            as_tensor = jnp.array
            is_tensor = is_jax_tensor
        else:
            def as_tensor(value, dtype=None):
                if isinstance(value, (list, tuple)) and isinstance(value[0], (list, tuple, np.ndarray)):
                    value_lens = [len(val) for val in value]
                    if len(set(value_lens)) > 1 and dtype is None: value = as_tensor([np.asarray(val) for val in value], dtype=object)
                return np.asarray(value, dtype=dtype)
            is_tensor = is_numpy_array
        return is_tensor, as_tensor
    def convert_to_tensors(self, tensor_type: Optional[Union[str, TensorType]] = None):
        if tensor_type is None: return self
        is_tensor, as_tensor = self._get_is_as_tensor_fns(tensor_type)
        for key, value in self.items():
            try:
                if not is_tensor(value):
                    tensor = as_tensor(value)
                    self[key] = tensor
            except:
                if key == "overflowing_values": raise ValueError("Unable to create tensor returning overflowing values of different lengths. ")
                raise ValueError("Unable to create tensor, you should probably activate padding with 'padding=True' to have batched tensors with the same length.")
        return self
    def to(self, *args, **kwargs) -> "BatchFeature":
        requires_backends(self, ["torch"])
        import torch
        new_data = {}
        device = kwargs.get("device")
        if device is None and len(args) > 0:
            arg = args[0]
            if is_torch_dtype(arg): pass
            elif isinstance(arg, str) or is_torch_device(arg) or isinstance(arg, int): device = arg
            else: raise ValueError(f"Attempting to cast a BatchFeature to type {str(arg)}. This is not supported.")
        for k, v in self.items():
            if torch.is_floating_point(v): new_data[k] = v.to(*args, **kwargs)
            elif device is not None: new_data[k] = v.to(device=device)
            else: new_data[k] = v
        self.data = new_data
        return self
class FeatureExtractionMixin(PushToHubMixin):
    _auto_class = None
    def __init__(self, **kwargs):
        self._processor_class = kwargs.pop("processor_class", None)
        for key, value in kwargs.items():
            try: setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err
    def _set_processor_class(self, processor_class: str): self._processor_class = processor_class
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False, local_files_only: bool = False, token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs):
        kwargs["cache_dir"] = cache_dir
        kwargs["force_download"] = force_download
        kwargs["local_files_only"] = local_files_only
        kwargs["revision"] = revision
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None: kwargs["token"] = token
        feature_extractor_dict, kwargs = cls.get_feature_extractor_dict(pretrained_model_name_or_path, **kwargs)
        return cls.from_dict(feature_extractor_dict, **kwargs)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool = False, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        if os.path.isfile(save_directory): raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if self._auto_class is not None: custom_object_save(self, save_directory, config=self)
        output_feature_extractor_file = os.path.join(save_directory, FEATURE_EXTRACTOR_NAME)
        self.to_json_file(output_feature_extractor_file)
        logger.info(f"Feature extractor saved in {output_feature_extractor_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
        return [output_feature_extractor_file]
    @classmethod
    def get_feature_extractor_dict(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        subfolder = kwargs.pop("subfolder", None)
        token = kwargs.pop("token", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        user_agent = {"file_type": "feature extractor", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isdir(pretrained_model_name_or_path): feature_extractor_file = os.path.join(pretrained_model_name_or_path, FEATURE_EXTRACTOR_NAME)
        if os.path.isfile(pretrained_model_name_or_path):
            resolved_feature_extractor_file = pretrained_model_name_or_path
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            feature_extractor_file = pretrained_model_name_or_path
            resolved_feature_extractor_file = download_url(pretrained_model_name_or_path)
        else:
            feature_extractor_file = FEATURE_EXTRACTOR_NAME
            try: resolved_feature_extractor_file = cached_file(pretrained_model_name_or_path, feature_extractor_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies, resume_download=resume_download,
            local_files_only=local_files_only, subfolder=subfolder, token=token, user_agent=user_agent, revision=revision)
            except EnvironmentError: raise
            except Exception: raise EnvironmentError(f"Can't load feature extractor for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a {FEATURE_EXTRACTOR_NAME} file")
        try:
            with open(resolved_feature_extractor_file, "r", encoding="utf-8") as reader: text = reader.read()
            feature_extractor_dict = json.loads(text)
        except json.JSONDecodeError: raise EnvironmentError(f"It looks like the config file at '{resolved_feature_extractor_file}' is not a valid JSON file.")
        if is_local: logger.info(f"loading configuration file {resolved_feature_extractor_file}")
        else: logger.info(f"loading configuration file {feature_extractor_file} from cache at {resolved_feature_extractor_file}")
        if not is_local:
            if "auto_map" in feature_extractor_dict: feature_extractor_dict["auto_map"] = add_model_info_to_auto_map(feature_extractor_dict["auto_map"], pretrained_model_name_or_path)
            if "custom_pipelines" in feature_extractor_dict: feature_extractor_dict["custom_pipelines"] = add_model_info_to_custom_pipelines(feature_extractor_dict["custom_pipelines"], pretrained_model_name_or_path)
        return feature_extractor_dict, kwargs
    @classmethod
    def from_dict(cls, feature_extractor_dict: Dict[str, Any], **kwargs) -> PreTrainedFeatureExtractor:
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        to_remove = []
        for key, value in kwargs.items():
            if key in feature_extractor_dict:
                feature_extractor_dict[key] = value
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        feature_extractor = cls(**feature_extractor_dict)
        logger.info(f"Feature extractor {feature_extractor}")
        if return_unused_kwargs: return feature_extractor, kwargs
        else: return feature_extractor
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["feature_extractor_type"] = self.__class__.__name__
        if "mel_filters" in output: del output["mel_filters"]
        if "window" in output: del output["window"]
        return output
    @classmethod
    def from_json_file(cls, json_file: Union[str, os.PathLike]) -> PreTrainedFeatureExtractor:
        with open(json_file, "r", encoding="utf-8") as reader: text = reader.read()
        feature_extractor_dict = json.loads(text)
        return cls(**feature_extractor_dict)
    def to_json_string(self) -> str:
        dictionary = self.to_dict()
        for key, value in dictionary.items():
            if isinstance(value, np.ndarray): dictionary[key] = value.tolist()
        _processor_class = dictionary.pop("_processor_class", None)
        if _processor_class is not None: dictionary["processor_class"] = _processor_class
        return json.dumps(dictionary, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer: writer.write(self.to_json_string())
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string()}"
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoFeatureExtractor"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
class SapiensBatchFeature(BatchFeature): pass
FeatureExtractionMixin.push_to_hub = copy_func(FeatureExtractionMixin.push_to_hub)
if FeatureExtractionMixin.push_to_hub.__doc__ is not None: FeatureExtractionMixin.push_to_hub.__doc__ = FeatureExtractionMixin.push_to_hub.__doc__.format(object="feature extractor", object_class="AutoFeatureExtractor", object_files="feature extractor file")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
