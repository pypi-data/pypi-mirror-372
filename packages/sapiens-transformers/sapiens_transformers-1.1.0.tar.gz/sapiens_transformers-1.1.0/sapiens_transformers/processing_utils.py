"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (CHAT_TEMPLATE_NAME, PROCESSOR_NAME, PushToHubMixin, TensorType, add_model_info_to_auto_map, add_model_info_to_custom_pipelines,
cached_file, copy_func, direct_transformers_import, download_url, is_offline_mode, is_remote_url, logging)
from .tokenization_utils_base import (PaddingStrategy, PreTokenizedInput, PreTrainedTokenizerBase, TextInput, TruncationStrategy)
from .image_utils import ChannelDimension, is_valid_image, is_vision_available
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union
from .dynamic_module_utils import custom_object_save
from pathlib import Path
import typing_extensions
import numpy as np
import warnings
import inspect
import typing
import copy
import json
import sys
import os
if is_vision_available(): from .image_utils import PILImageResampling
logger = logging.get_logger(__name__)
transformers_module = direct_transformers_import(Path(__file__).parent)
AUTO_TO_BASE_CLASS_MAPPING = {'AutoTokenizer': 'PreTrainedTokenizerBase', 'AutoFeatureExtractor': 'FeatureExtractionMixin', 'AutoImageProcessor': 'ImageProcessingMixin'}
if sys.version_info >= (3, 11): Unpack = typing.Unpack
else: Unpack = typing_extensions.Unpack
class TextKwargs(TypedDict, total=False):
    text_pair: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]]
    text_target: Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]
    text_pair_target: Optional[Union[TextInput, PreTokenizedInput, List[TextInput], List[PreTokenizedInput]]]
    add_special_tokens: Optional[bool]
    padding: Union[bool, str, PaddingStrategy]
    truncation: Union[bool, str, TruncationStrategy]
    max_length: Optional[int]
    stride: Optional[int]
    is_split_into_words: Optional[bool]
    pad_to_multiple_of: Optional[int]
    return_token_type_ids: Optional[bool]
    return_attention_mask: Optional[bool]
    return_overflowing_tokens: Optional[bool]
    return_special_tokens_mask: Optional[bool]
    return_offsets_mapping: Optional[bool]
    return_length: Optional[bool]
    verbose: Optional[bool]
    padding_side: Optional[str]
class ImagesKwargs(TypedDict, total=False):
    do_resize: Optional[bool]
    size: Optional[Dict[str, int]]
    size_divisor: Optional[int]
    crop_size: Optional[Dict[str, int]]
    resample: Optional[Union["PILImageResampling", int]]
    do_rescale: Optional[bool]
    rescale_factor: Optional[float]
    do_normalize: Optional[bool]
    image_mean: Optional[Union[float, List[float]]]
    image_std: Optional[Union[float, List[float]]]
    do_pad: Optional[bool]
    pad_size: Optional[Dict[str, int]]
    do_center_crop: Optional[bool]
    data_format: Optional[ChannelDimension]
    input_data_format: Optional[Union[str, ChannelDimension]]
class VideosKwargs(TypedDict, total=False):
    do_resize: Optional[bool]
    size: Optional[Dict[str, int]]
    size_divisor: Optional[int]
    resample: Optional["PILImageResampling"]
    do_rescale: Optional[bool]
    rescale_factor: Optional[float]
    do_normalize: Optional[bool]
    image_mean: Optional[Union[float, List[float]]]
    image_std: Optional[Union[float, List[float]]]
    do_pad: Optional[bool]
    do_center_crop: Optional[bool]
    data_format: Optional[ChannelDimension]
    input_data_format: Optional[Union[str, ChannelDimension]]
class AudioKwargs(TypedDict, total=False):
    sampling_rate: Optional[int]
    raw_speech: Optional[Union["np.ndarray", List[float], List["np.ndarray"], List[List[float]]]]
    padding: Optional[Union[bool, str, PaddingStrategy]]
    max_length: Optional[int]
    truncation: Optional[bool]
    pad_to_multiple_of: Optional[int]
    return_attention_mask: Optional[bool]
class CommonKwargs(TypedDict, total=False):
    return_tensors: Optional[Union[str, TensorType]]
class ProcessingKwargs(TextKwargs, ImagesKwargs, VideosKwargs, AudioKwargs, CommonKwargs, total=False):
    common_kwargs: CommonKwargs = {**CommonKwargs.__annotations__}
    text_kwargs: TextKwargs = {**TextKwargs.__annotations__}
    images_kwargs: ImagesKwargs = {**ImagesKwargs.__annotations__}
    videos_kwargs: VideosKwargs = {**VideosKwargs.__annotations__}
    audio_kwargs: AudioKwargs = {**AudioKwargs.__annotations__}
class ProcessorMixin(PushToHubMixin):
    attributes = ["feature_extractor", "tokenizer"]
    optional_attributes = ["chat_template"]
    optional_call_args: List[str] = []
    feature_extractor_class = None
    tokenizer_class = None
    _auto_class = None
    valid_kwargs: List[str] = []
    def __init__(self, *args, **kwargs):
        for optional_attribute in self.optional_attributes: setattr(self, optional_attribute, kwargs.pop(optional_attribute, None))
        for key in kwargs:
            if key not in self.attributes: raise TypeError(f"Unexpected keyword argument {key}.")
        for arg, attribute_name in zip(args, self.attributes):
            if attribute_name in kwargs: raise TypeError(f"Got multiple values for argument {attribute_name}.")
            else: kwargs[attribute_name] = arg
        if len(kwargs) != len(self.attributes): raise ValueError(f"This processor requires {len(self.attributes)} arguments: {', '.join(self.attributes)}. Got {len(args)} arguments instead.")
        for attribute_name, arg in kwargs.items():
            class_name = getattr(self, f"{attribute_name}_class")
            class_name = AUTO_TO_BASE_CLASS_MAPPING.get(class_name, class_name)
            if isinstance(class_name, tuple): proper_class = tuple(getattr(transformers_module, n) for n in class_name if n is not None)
            else: proper_class = getattr(transformers_module, class_name)
            if not isinstance(arg, proper_class): raise TypeError(f"Received a {type(arg).__name__} for argument {attribute_name}, but a {class_name} was expected.")
            setattr(self, attribute_name, arg)
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        sig = inspect.signature(self.__init__)
        attrs_to_save = sig.parameters
        attrs_to_save = [x for x in attrs_to_save if x not in self.__class__.attributes]
        attrs_to_save += ["auto_map"]
        output = {k: v for k, v in output.items() if k in attrs_to_save}
        output["processor_class"] = self.__class__.__name__
        if "tokenizer" in output: del output["tokenizer"]
        if "image_processor" in output: del output["image_processor"]
        if "feature_extractor" in output: del output["feature_extractor"]
        if "chat_template" in output: del output["chat_template"]
        output = {k: v for k, v in output.items() if not (isinstance(v, PushToHubMixin) or v.__class__.__name__ == "BeamSearchDecoderCTC")}
        return output
    def to_json_string(self) -> str:
        dictionary = self.to_dict()
        return json.dumps(dictionary, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer: writer.write(self.to_json_string())
    def __repr__(self):
        attributes_repr = [f"- {name}: {repr(getattr(self, name))}" for name in self.attributes]
        attributes_repr = "\n".join(attributes_repr)
        return f"{self.__class__.__name__}:\n{attributes_repr}\n\n{self.to_json_string()}"
    def save_pretrained(self, save_directory, push_to_hub: bool = False, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if self._auto_class is not None:
            attrs = [getattr(self, attribute_name) for attribute_name in self.attributes]
            configs = [(a.init_kwargs if isinstance(a, PreTrainedTokenizerBase) else a) for a in attrs]
            configs.append(self)
            custom_object_save(self, save_directory, config=configs)
        for attribute_name in self.attributes:
            attribute = getattr(self, attribute_name)
            if hasattr(attribute, "_set_processor_class"): attribute._set_processor_class(self.__class__.__name__)
            attribute.save_pretrained(save_directory)
        if self._auto_class is not None:
            for attribute_name in self.attributes:
                attribute = getattr(self, attribute_name)
                if isinstance(attribute, PreTrainedTokenizerBase): del attribute.init_kwargs["auto_map"]
        output_processor_file = os.path.join(save_directory, PROCESSOR_NAME)
        output_chat_template_file = os.path.join(save_directory, CHAT_TEMPLATE_NAME)
        processor_dict = self.to_dict()
        if self.chat_template is not None:
            chat_template_json_string = (json.dumps({"chat_template": self.chat_template}, indent=2, sort_keys=True) + "\n")
            with open(output_chat_template_file, "w", encoding="utf-8") as writer: writer.write(chat_template_json_string)
            logger.info(f"chat template saved in {output_chat_template_file}")
        if set(processor_dict.keys()) != {"processor_class"}:
            self.to_json_file(output_processor_file)
            logger.info(f"processor saved in {output_processor_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
        if set(processor_dict.keys()) == {"processor_class"}: return []
        return [output_processor_file]
    @classmethod
    def get_processor_dict(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        user_agent = {"file_type": "processor", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isdir(pretrained_model_name_or_path):
            processor_file = os.path.join(pretrained_model_name_or_path, PROCESSOR_NAME)
            chat_template_file = os.path.join(pretrained_model_name_or_path, "chat_template.json")
        if os.path.isfile(pretrained_model_name_or_path):
            resolved_processor_file = pretrained_model_name_or_path
            resolved_chat_template_file = None
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            processor_file = pretrained_model_name_or_path
            resolved_processor_file = download_url(pretrained_model_name_or_path)
            resolved_chat_template_file = None
        else:
            processor_file = PROCESSOR_NAME
            chat_template_file = CHAT_TEMPLATE_NAME
            try:
                resolved_processor_file = cached_file(pretrained_model_name_or_path, processor_file, cache_dir=cache_dir, force_download=force_download,
                proxies=proxies, resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision,
                subfolder=subfolder, _raise_exceptions_for_missing_entries=False)
                resolved_chat_template_file = cached_file(pretrained_model_name_or_path, chat_template_file, cache_dir=cache_dir, force_download=force_download,
                proxies=proxies, resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision,
                subfolder=subfolder, _raise_exceptions_for_missing_entries=False)
            except EnvironmentError: raise
            except Exception: raise EnvironmentError(f"Can't load processor for '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a {PROCESSOR_NAME} file")
        chat_template = None
        if resolved_chat_template_file is not None:
            with open(resolved_chat_template_file, "r", encoding="utf-8") as reader: text = reader.read()
            chat_template = json.loads(text)["chat_template"]
            kwargs["chat_template"] = chat_template
        if resolved_processor_file is None: return {}, kwargs
        try:
            with open(resolved_processor_file, "r", encoding="utf-8") as reader: text = reader.read()
            processor_dict = json.loads(text)
        except json.JSONDecodeError: raise EnvironmentError(f"It looks like the config file at '{resolved_processor_file}' is not a valid JSON file.")
        if is_local: logger.info(f"loading configuration file {resolved_processor_file}")
        else: logger.info(f"loading configuration file {processor_file} from cache at {resolved_processor_file}")
        if "chat_template" in processor_dict and processor_dict["chat_template"] is not None: logger.warning_once("Chat templates should be in a 'chat_template.json' file but found key='chat_template' in the processor's config. Make sure to move your template to its own file.")
        if not is_local:
            if "auto_map" in processor_dict: processor_dict["auto_map"] = add_model_info_to_auto_map(processor_dict["auto_map"], pretrained_model_name_or_path)
            if "custom_pipelines" in processor_dict: processor_dict["custom_pipelines"] = add_model_info_to_custom_pipelines(processor_dict["custom_pipelines"], pretrained_model_name_or_path)
        return processor_dict, kwargs
    @classmethod
    def from_args_and_dict(cls, args, processor_dict: Dict[str, Any], **kwargs):
        processor_dict = processor_dict.copy()
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        chat_template = kwargs.pop("chat_template", None)
        if "processor_class" in processor_dict: del processor_dict["processor_class"]
        if "auto_map" in processor_dict: del processor_dict["auto_map"]
        unused_kwargs = cls.validate_init_kwargs(processor_config=processor_dict, valid_kwargs=cls.valid_kwargs)
        processor = cls(*args, **processor_dict)
        if chat_template is not None: setattr(processor, "chat_template", chat_template)
        for key in set(kwargs.keys()):
            if hasattr(processor, key): setattr(processor, key, kwargs.pop(key))
        kwargs.update(unused_kwargs)
        logger.info(f"Processor {processor}")
        if return_unused_kwargs: return processor, kwargs
        else: return processor
    def _merge_kwargs(self, ModelProcessorKwargs: ProcessingKwargs, tokenizer_init_kwargs: Optional[Dict] = None, **kwargs) -> Dict[str, Dict]:
        output_kwargs = {"text_kwargs": {}, "images_kwargs": {}, "audio_kwargs": {}, "videos_kwargs": {}, "common_kwargs": {}}
        default_kwargs = {"text_kwargs": {}, "images_kwargs": {}, "audio_kwargs": {}, "videos_kwargs": {}, "common_kwargs": {}}
        for modality in default_kwargs:
            default_kwargs[modality] = ModelProcessorKwargs._defaults.get(modality, {}).copy()
            for modality_key in ModelProcessorKwargs.__annotations__[modality].__annotations__.keys():
                if modality_key in tokenizer_init_kwargs: default_kwargs[modality][modality_key] = tokenizer_init_kwargs[modality_key]
        output_kwargs.update(default_kwargs)
        non_modality_kwargs = set(kwargs) - set(output_kwargs)
        for modality in output_kwargs:
            for modality_key in ModelProcessorKwargs.__annotations__[modality].__annotations__.keys():
                if modality in kwargs:
                    kwarg_value = kwargs[modality].pop(modality_key, "__empty__")
                    if kwarg_value != "__empty__" and modality_key in non_modality_kwargs: raise ValueError(f"Keyword argument {modality_key} was passed two times:\nin a dictionary for {modality} and as a **kwarg.")
                elif modality_key in kwargs: kwarg_value = kwargs.pop(modality_key, "__empty__")
                else: kwarg_value = "__empty__"
                if kwarg_value != "__empty__": output_kwargs[modality][modality_key] = kwarg_value
        if set(kwargs) & set(default_kwargs): [output_kwargs["common_kwargs"].update(subdict) for _, subdict in kwargs.items()]
        else: output_kwargs["common_kwargs"].update(kwargs)
        for modality in output_kwargs: output_kwargs[modality].update(output_kwargs["common_kwargs"])
        return output_kwargs
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False, local_files_only: bool = False,
    token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs):
        kwargs["cache_dir"] = cache_dir
        kwargs["force_download"] = force_download
        kwargs["local_files_only"] = local_files_only
        kwargs["revision"] = revision
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None: kwargs["token"] = token
        args = cls._get_arguments_from_pretrained(pretrained_model_name_or_path, **kwargs)
        processor_dict, kwargs = cls.get_processor_dict(pretrained_model_name_or_path, **kwargs)
        return cls.from_args_and_dict(args, processor_dict, **kwargs)
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoProcessor"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    @classmethod
    def _get_arguments_from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        args = []
        for attribute_name in cls.attributes:
            class_name = getattr(cls, f"{attribute_name}_class")
            if isinstance(class_name, tuple):
                classes = tuple(getattr(transformers_module, n) if n is not None else None for n in class_name)
                use_fast = kwargs.get("use_fast", True)
                if use_fast and classes[1] is not None: attribute_class = classes[1]
                else: attribute_class = classes[0]
            else: attribute_class = getattr(transformers_module, class_name)
            args.append(attribute_class.from_pretrained(pretrained_model_name_or_path, **kwargs))
        return args
    @property
    def model_input_names(self):
        first_attribute = getattr(self, self.attributes[0])
        return getattr(first_attribute, "model_input_names", None)
    @staticmethod
    def validate_init_kwargs(processor_config, valid_kwargs):
        kwargs_from_config = processor_config.keys()
        unused_kwargs = {}
        unused_keys = set(kwargs_from_config) - set(valid_kwargs)
        if unused_keys: unused_kwargs = {k: processor_config[k] for k in unused_keys}
        return unused_kwargs
    def prepare_and_validate_optional_call_args(self, *args):
        if len(args): warnings.warn("Passing positional arguments to the processor call is now deprecated and will be disallowed in v1.0. Please pass all arguments as keyword arguments.")
        if len(args) > len(self.optional_call_args): raise ValueError(f"Expected *at most* {len(self.optional_call_args)} optional positional arguments in processor call which will be matched with {' '.join(self.optional_call_args)} in the order they are passed. However, got {len(args)} positional arguments instead. Please pass all arguments as keyword arguments instead (e.g. `processor(arg_name_1=..., arg_name_2=...))`.")
        return {arg_name: arg_value for arg_value, arg_name in zip(args, self.optional_call_args)}
    def apply_chat_template(self, conversation: Union[List[Dict[str, str]]], chat_template: Optional[str] = None, tokenize: bool = False, **kwargs) -> str:
        if chat_template is None:
            if self.chat_template is not None: chat_template = self.chat_template
            else: raise ValueError("No chat template is set for this processor. Please either set the `chat_template` attribute, or provide a chat template as an argument.")
        return self.tokenizer.apply_chat_template(conversation, chat_template=chat_template, tokenize=tokenize, **kwargs)
def _validate_images_text_input_order(images, text):
    def is_url(val) -> bool: return isinstance(val, str) and val.startswith("http")
    def _is_valid_images_input_for_processor(imgs):
        if isinstance(imgs, (list, tuple)):
            for img in imgs:
                if not _is_valid_images_input_for_processor(img): return False
        elif not (is_valid_image(imgs) or is_url(imgs)): return False
        return True
    def _is_valid_text_input_for_processor(t):
        if isinstance(t, str): return True
        elif isinstance(t, (list, tuple)):
            if len(t) == 0: return False
            for t_s in t: return _is_valid_text_input_for_processor(t_s)
        return False
    def _is_valid(input, validator): return validator(input) or input is None
    images_is_valid = _is_valid(images, _is_valid_images_input_for_processor)
    images_is_text = _is_valid_text_input_for_processor(images)
    text_is_valid = _is_valid(text, _is_valid_text_input_for_processor)
    text_is_images = _is_valid_images_input_for_processor(text)
    if images_is_valid and text_is_valid: return images, text
    if (images is None and text_is_images) or (text is None and images_is_text) or (images_is_text and text_is_images):
        logger.warning_once("You may have used the wrong order for inputs. `images` should be passed before `text`. The `images` and `text` inputs will be swapped. This behavior will be deprecated in transformers v1.0.")
        return text, images
    raise ValueError("Invalid input type. Check that `images` and/or `text` are valid inputs.")
class SapiensProcessingKwargs(ProcessingKwargs): pass
class SapiensProcessorMixin(ProcessorMixin): pass
ProcessorMixin.push_to_hub = copy_func(ProcessorMixin.push_to_hub)
if ProcessorMixin.push_to_hub.__doc__ is not None: ProcessorMixin.push_to_hub.__doc__ = ProcessorMixin.push_to_hub.__doc__.format(object="processor", object_class="AutoProcessor", object_files="processor files")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
