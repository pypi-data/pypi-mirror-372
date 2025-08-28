"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (IMAGE_PROCESSOR_NAME, PushToHubMixin, add_model_info_to_auto_map, add_model_info_to_custom_pipelines, cached_file, copy_func, download_url, is_offline_mode, is_remote_url, is_vision_available, logging)
from .feature_extraction_utils import BatchFeature as BaseBatchFeature
from typing import Any, Dict, List, Optional, Tuple, Union
from .dynamic_module_utils import custom_object_save
from io import BytesIO
import numpy as np
import warnings
import requests
import copy
import json
import os
if is_vision_available(): from PIL import Image
logger = logging.get_logger(__name__)
class BatchFeature(BaseBatchFeature): pass
class ImageProcessingMixin(PushToHubMixin):
    _auto_class = None
    def __init__(self, **kwargs):
        kwargs.pop("feature_extractor_type", None)
        self._processor_class = kwargs.pop("processor_class", None)
        for key, value in kwargs.items():
            try: setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err
    def _set_processor_class(self, processor_class: str): self._processor_class = processor_class
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False,
    local_files_only: bool = False, token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs):
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
        image_processor_dict, kwargs = cls.get_image_processor_dict(pretrained_model_name_or_path, **kwargs)
        return cls.from_dict(image_processor_dict, **kwargs)
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
        output_image_processor_file = os.path.join(save_directory, IMAGE_PROCESSOR_NAME)
        self.to_json_file(output_image_processor_file)
        logger.info(f"Image processor saved in {output_image_processor_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
        return [output_image_processor_file]
    @classmethod
    def get_image_processor_dict(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        user_agent = {"file_type": "image processor", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isdir(pretrained_model_name_or_path): image_processor_file = os.path.join(pretrained_model_name_or_path, IMAGE_PROCESSOR_NAME)
        if os.path.isfile(pretrained_model_name_or_path):
            resolved_image_processor_file = pretrained_model_name_or_path
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            image_processor_file = pretrained_model_name_or_path
            resolved_image_processor_file = download_url(pretrained_model_name_or_path)
        else:
            image_processor_file = IMAGE_PROCESSOR_NAME
            try: resolved_image_processor_file = cached_file(pretrained_model_name_or_path, image_processor_file, cache_dir=cache_dir, force_download=force_download,
            proxies=proxies, resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder)
            except EnvironmentError: raise
            except Exception: raise EnvironmentError(f"Can't load image processor for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a {IMAGE_PROCESSOR_NAME} file")
        try:
            with open(resolved_image_processor_file, "r", encoding="utf-8") as reader: text = reader.read()
            image_processor_dict = json.loads(text)
        except json.JSONDecodeError: raise EnvironmentError(f"It looks like the config file at '{resolved_image_processor_file}' is not a valid JSON file.")
        if is_local: logger.info(f"loading configuration file {resolved_image_processor_file}")
        else: logger.info(f"loading configuration file {image_processor_file} from cache at {resolved_image_processor_file}")
        if not is_local:
            if "auto_map" in image_processor_dict: image_processor_dict["auto_map"] = add_model_info_to_auto_map(image_processor_dict["auto_map"], pretrained_model_name_or_path)
            if "custom_pipelines" in image_processor_dict: image_processor_dict["custom_pipelines"] = add_model_info_to_custom_pipelines(image_processor_dict["custom_pipelines"], pretrained_model_name_or_path)
        return image_processor_dict, kwargs
    @classmethod
    def from_dict(cls, image_processor_dict: Dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        if "size" in kwargs and "size" in image_processor_dict: image_processor_dict["size"] = kwargs.pop("size")
        if "crop_size" in kwargs and "crop_size" in image_processor_dict: image_processor_dict["crop_size"] = kwargs.pop("crop_size")
        image_processor = cls(**image_processor_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(image_processor, key):
                setattr(image_processor, key, value)
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        logger.info(f"Image processor {image_processor}")
        if return_unused_kwargs: return image_processor, kwargs
        else: return image_processor
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["image_processor_type"] = self.__class__.__name__
        return output
    @classmethod
    def from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, "r", encoding="utf-8") as reader: text = reader.read()
        image_processor_dict = json.loads(text)
        return cls(**image_processor_dict)
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
    def register_for_auto_class(cls, auto_class="AutoImageProcessor"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    def fetch_images(self, image_url_or_urls: Union[str, List[str]]):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
        if isinstance(image_url_or_urls, list): return [self.fetch_images(x) for x in image_url_or_urls]
        elif isinstance(image_url_or_urls, str):
            response = requests.get(image_url_or_urls, stream=True, headers=headers)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else: raise TypeError(f"only a single or a list of entries is supported but got type={type(image_url_or_urls)}")
ImageProcessingMixin.push_to_hub = copy_func(ImageProcessingMixin.push_to_hub)
if ImageProcessingMixin.push_to_hub.__doc__ is not None: ImageProcessingMixin.push_to_hub.__doc__ = ImageProcessingMixin.push_to_hub.__doc__.format(object="image processor", object_class="AutoImageProcessor", object_files="image processor file")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
