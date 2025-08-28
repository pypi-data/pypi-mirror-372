"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .utils import (CONFIG_NAME, PushToHubMixin, add_model_info_to_auto_map, add_model_info_to_custom_pipelines, cached_file, copy_func, download_url, extract_commit_hash, is_remote_url, is_torch_available, logging)
from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
from typing import Any, Dict, List, Optional, Tuple, Union
from .dynamic_module_utils import custom_object_save
from packaging import version
from . import __version__
import warnings
import copy
import json
import os
import re
logger = logging.get_logger(__name__)
_re_configuration_file = re.compile(r"config\.(.*)\.json")
class PretrainedConfig(PushToHubMixin):
    model_type: str = ""
    is_composition: bool = False
    attribute_map: Dict[str, str] = {}
    _auto_class: Optional[str] = None
    def __setattr__(self, key, value):
        if key in super().__getattribute__("attribute_map"): key = super().__getattribute__("attribute_map")[key]
        super().__setattr__(key, value)
    def __getattribute__(self, key):
        if key != "attribute_map" and key in super().__getattribute__("attribute_map"): key = super().__getattribute__("attribute_map")[key]
        return super().__getattribute__(key)
    def __init__(self, **kwargs):
        self.return_dict = kwargs.pop("return_dict", True)
        self.output_hidden_states = kwargs.pop("output_hidden_states", False)
        self.output_attentions = kwargs.pop("output_attentions", False)
        self.torchscript = kwargs.pop("torchscript", False)
        self.torch_dtype = kwargs.pop("torch_dtype", None)
        self.use_bfloat16 = kwargs.pop("use_bfloat16", False)
        self.tf_legacy_loss = kwargs.pop("tf_legacy_loss", False)
        self.pruned_heads = kwargs.pop("pruned_heads", {})
        self.tie_word_embeddings = kwargs.pop("tie_word_embeddings", True)
        self.chunk_size_feed_forward = kwargs.pop("chunk_size_feed_forward", 0)
        self.is_encoder_decoder = kwargs.pop("is_encoder_decoder", False)
        self.is_decoder = kwargs.pop("is_decoder", False)
        self.cross_attention_hidden_size = kwargs.pop("cross_attention_hidden_size", None)
        self.add_cross_attention = kwargs.pop("add_cross_attention", False)
        self.tie_encoder_decoder = kwargs.pop("tie_encoder_decoder", False)
        for parameter_name, default_value in self._get_global_generation_defaults().items(): setattr(self, parameter_name, kwargs.pop(parameter_name, default_value))
        self.architectures = kwargs.pop("architectures", None)
        self.finetuning_task = kwargs.pop("finetuning_task", None)
        self.id2label = kwargs.pop("id2label", None)
        self.label2id = kwargs.pop("label2id", None)
        if self.label2id is not None and not isinstance(self.label2id, dict): raise ValueError("Argument label2id should be a dictionary.")
        if self.id2label is not None:
            if not isinstance(self.id2label, dict): raise ValueError("Argument id2label should be a dictionary.")
            num_labels = kwargs.pop("num_labels", None)
            if num_labels is not None and len(self.id2label) != num_labels: logger.warning(f"You passed along `num_labels={num_labels}` with an incompatible id to label map: {self.id2label}. The number of labels wil be overwritten to {self.num_labels}.")
            self.id2label = {int(key): value for key, value in self.id2label.items()}
        else: self.num_labels = kwargs.pop("num_labels", 2)
        if self.torch_dtype is not None and isinstance(self.torch_dtype, str):
            if is_torch_available():
                import torch
                self.torch_dtype = getattr(torch, self.torch_dtype)
        self.tokenizer_class = kwargs.pop("tokenizer_class", None)
        self.prefix = kwargs.pop("prefix", None)
        self.bos_token_id = kwargs.pop("bos_token_id", None)
        self.pad_token_id = kwargs.pop("pad_token_id", None)
        self.eos_token_id = kwargs.pop("eos_token_id", None)
        self.sep_token_id = kwargs.pop("sep_token_id", None)
        self.decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)
        self.task_specific_params = kwargs.pop("task_specific_params", None)
        self.problem_type = kwargs.pop("problem_type", None)
        allowed_problem_types = ("regression", "single_label_classification", "multi_label_classification")
        if self.problem_type is not None and self.problem_type not in allowed_problem_types: raise ValueError(f"The config parameter `problem_type` was not understood: received {self.problem_type} but only 'regression', 'single_label_classification' and 'multi_label_classification' are valid.")
        if kwargs.pop("xla_device", None) is not None: logger.warning("The `xla_device` argument has been deprecated in v1.0.0 of Sapiens Transformers. It is ignored and you can safely remove it from your `config.json` file.")
        self._name_or_path = str(kwargs.pop("name_or_path", ""))
        self._commit_hash = kwargs.pop("_commit_hash", None)
        self._attn_implementation_internal = kwargs.pop("attn_implementation", None)
        self.sapiens_transformers_version = kwargs.pop("sapiens_transformers_version", None)
        if kwargs.get("gradient_checkpointing", False): warnings.warn("Passing `gradient_checkpointing` to a config initialization is deprecated and will be removed in v1 Sapiens Transformers. Using `model.gradient_checkpointing_enable()` instead, or if you are using the `Trainer` API, pass `gradient_checkpointing=True` in your `TrainingArguments`.")
        for key, value in kwargs.items():
            try: setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err
    @property
    def name_or_path(self) -> str: return getattr(self, "_name_or_path", None)
    @name_or_path.setter
    def name_or_path(self, value): self._name_or_path = str(value)
    @property
    def use_return_dict(self) -> bool: return self.return_dict and not self.torchscript
    @property
    def num_labels(self) -> int: return len(self.id2label)
    @num_labels.setter
    def num_labels(self, num_labels: int):
        if not hasattr(self, "id2label") or self.id2label is None or len(self.id2label) != num_labels:
            self.id2label = {i: f"LABEL_{i}" for i in range(num_labels)}
            self.label2id = dict(zip(self.id2label.values(), self.id2label.keys()))
    @property
    def _attn_implementation(self):
        if hasattr(self, "_attn_implementation_internal"):
            if self._attn_implementation_internal is None: return "eager"
            else: return self._attn_implementation_internal
        else: return "eager"
    @_attn_implementation.setter
    def _attn_implementation(self, value): self._attn_implementation_internal = value
    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool = False, **kwargs):
        self._set_token_in_kwargs(kwargs)
        if os.path.isfile(save_directory): raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        non_default_generation_parameters = self._get_non_default_generation_parameters()
        if len(non_default_generation_parameters) > 0: warnings.warn(f"Some non-default generation parameters are set in the model config. These should go into either a) `model.generation_config` (as opposed to `model.config`); OR b) a GenerationConfig file. This warning will become an exception in the future.\nNon-default generation parameters: {str(non_default_generation_parameters)}", UserWarning)
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if self._auto_class is not None: custom_object_save(self, save_directory, config=self)
        output_config_file = os.path.join(save_directory, CONFIG_NAME)
        self.to_json_file(output_config_file, use_diff=True)
        logger.info(f"Configuration saved in {output_config_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
    @staticmethod
    def _set_token_in_kwargs(kwargs, token=None):
        if token is None: token = kwargs.pop("token", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        if token is not None: kwargs["token"] = token
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False, local_files_only: bool = False,
    token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs) -> "PretrainedConfig":
        kwargs["cache_dir"] = cache_dir
        kwargs["force_download"] = force_download
        kwargs["local_files_only"] = local_files_only
        kwargs["revision"] = revision
        cls._set_token_in_kwargs(kwargs, token)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict['model_type'] == "modular_entity": cls.model_type = config_dict['model_type']
        return cls.from_dict(config_dict, **kwargs)
    @classmethod
    def get_config_dict(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cls._set_token_in_kwargs(kwargs)
        original_kwargs = copy.deepcopy(kwargs)
        config_dict, kwargs = cls._get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict is None: return {}, kwargs
        if "_commit_hash" in config_dict: original_kwargs["_commit_hash"] = config_dict["_commit_hash"]
        if "configuration_files" in config_dict:
            configuration_file = get_configuration_file(config_dict["configuration_files"])
            config_dict, kwargs = cls._get_config_dict(pretrained_model_name_or_path, _configuration_file=configuration_file, **original_kwargs)
        return config_dict, kwargs
    @classmethod
    def _get_config_dict(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        commit_hash = kwargs.pop("_commit_hash", None)
        gguf_file = kwargs.get("gguf_file", None)
        if trust_remote_code is True: logger.warning("The argument `trust_remote_code` is to be used with Auto classes. It has no effect here and is ignored.")
        user_agent = {"file_type": "config", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path)):
            resolved_config_file = pretrained_model_name_or_path
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            configuration_file = pretrained_model_name_or_path if gguf_file is None else gguf_file
            resolved_config_file = download_url(pretrained_model_name_or_path)
        else:
            configuration_file = kwargs.pop("_configuration_file", CONFIG_NAME) if gguf_file is None else gguf_file
            try:
                resolved_config_file = cached_file(pretrained_model_name_or_path, configuration_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies, resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder, _commit_hash=commit_hash)
                if resolved_config_file is None: return None, kwargs
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            except EnvironmentError: raise
            except Exception: raise EnvironmentError(f"Can't load the configuration of '{pretrained_model_name_or_path}'. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory containing a {configuration_file} file")
        try:
            if gguf_file: config_dict = load_gguf_checkpoint(resolved_config_file, return_tensors=False)["config"]
            else: config_dict = cls._dict_from_json_file(resolved_config_file)
            config_dict["_commit_hash"] = commit_hash
        except (json.JSONDecodeError, UnicodeDecodeError): raise EnvironmentError(f"It looks like the config file at '{resolved_config_file}' is not a valid JSON file.")
        if is_local: logger.info(f"loading configuration file {resolved_config_file}")
        else: logger.info(f"loading configuration file {configuration_file} from cache at {resolved_config_file}")
        if "auto_map" in config_dict and not is_local: config_dict["auto_map"] = add_model_info_to_auto_map(config_dict["auto_map"], pretrained_model_name_or_path)
        if "custom_pipelines" in config_dict and not is_local: config_dict["custom_pipelines"] = add_model_info_to_custom_pipelines(config_dict["custom_pipelines"], pretrained_model_name_or_path)
        return config_dict, kwargs
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], **kwargs) -> "PretrainedConfig":
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        kwargs.pop("_from_auto", None)
        kwargs.pop("_from_pipeline", None)
        if "_commit_hash" in kwargs and "_commit_hash" in config_dict: kwargs["_commit_hash"] = config_dict["_commit_hash"]
        config_dict["attn_implementation"] = kwargs.pop("attn_implementation", None)
        config = cls(**config_dict)
        if hasattr(config, "pruned_heads"): config.pruned_heads = {int(key): value for key, value in config.pruned_heads.items()}
        if "num_labels" in kwargs and "id2label" in kwargs:
            num_labels = kwargs["num_labels"]
            id2label = kwargs["id2label"] if kwargs["id2label"] is not None else []
            if len(id2label) != num_labels: raise ValueError(f"You passed along `num_labels={num_labels }` with an incompatible id to label map: {kwargs['id2label']}. Since those arguments are inconsistent with each other, you should remove one of them.")
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                current_attr = getattr(config, key)
                if isinstance(current_attr, PretrainedConfig) and isinstance(value, dict): value = current_attr.__class__(**value)
                setattr(config, key, value)
                if key != "torch_dtype": to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        logger.info(f"Model config {config}")
        if return_unused_kwargs: return config, kwargs
        else: return config
    @classmethod
    def from_json_file(cls, json_file: Union[str, os.PathLike]) -> "PretrainedConfig":
        config_dict = cls._dict_from_json_file(json_file)
        return cls(**config_dict)
    @classmethod
    def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, "r", encoding="utf-8") as reader: text = reader.read()
        return json.loads(text)
    def __eq__(self, other): return isinstance(other, PretrainedConfig) and (self.__dict__ == other.__dict__)
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_diff_dict(self) -> Dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = PretrainedConfig().to_dict()
        class_config_dict = self.__class__().to_dict() if not self.is_composition else {}
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if (isinstance(getattr(self, key, None), PretrainedConfig) and key in class_config_dict and isinstance(class_config_dict[key], dict)):
                diff = recursive_diff_dict(value, class_config_dict[key], config_obj=getattr(self, key, None))
                if "model_type" in value: diff["model_type"] = value["model_type"]
                if len(diff) > 0: serializable_config_dict[key] = diff
            elif (key not in default_config_dict or key == "sapiens_transformers_version" or value != default_config_dict[key] or (key in class_config_dict and value != class_config_dict[key])):
                serializable_config_dict[key] = value
        if hasattr(self, "quantization_config"):
            serializable_config_dict["quantization_config"] = (self.quantization_config.to_dict() if not isinstance(self.quantization_config, dict) else self.quantization_config)
            _ = serializable_config_dict.pop("_pre_quantization_dtype", None)
        self.dict_torch_dtype_to_str(serializable_config_dict)
        if "_attn_implementation_internal" in serializable_config_dict: del serializable_config_dict["_attn_implementation_internal"]
        return serializable_config_dict
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        if hasattr(self.__class__, "model_type"): output["model_type"] = self.__class__.model_type
        if "_auto_class" in output: del output["_auto_class"]
        if "_commit_hash" in output: del output["_commit_hash"]
        if "_attn_implementation_internal" in output: del output["_attn_implementation_internal"]
        output["sapiens_transformers_version"] = __version__
        for key, value in output.items():
            if isinstance(value, PretrainedConfig):
                value = value.to_dict()
                del value["sapiens_transformers_version"]
            output[key] = value
        if hasattr(self, "quantization_config"):
            output["quantization_config"] = (self.quantization_config.to_dict() if not isinstance(self.quantization_config, dict) else self.quantization_config)
            _ = output.pop("_pre_quantization_dtype", None)
        self.dict_torch_dtype_to_str(output)
        return output
    def to_json_string(self, use_diff: bool = True) -> str:
        if use_diff is True: config_dict = self.to_diff_dict()
        else: config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike], use_diff: bool = True):
        with open(json_file_path, "w", encoding="utf-8") as writer: writer.write(self.to_json_string(use_diff=use_diff))
    def update(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items(): setattr(self, key, value)
    def update_from_string(self, update_str: str):
        d = dict(x.split("=") for x in update_str.split(","))
        for k, v in d.items():
            if not hasattr(self, k): raise ValueError(f"key {k} isn't in the original config dict")
            old_v = getattr(self, k)
            if isinstance(old_v, bool):
                if v.lower() in ["true", "1", "y", "yes"]: v = True
                elif v.lower() in ["false", "0", "n", "no"]: v = False
                else: raise ValueError(f"can't derive true or false from {v} (key {k})")
            elif isinstance(old_v, int): v = int(v)
            elif isinstance(old_v, float): v = float(v)
            elif not isinstance(old_v, str): raise TypeError(f"You can only update int, float, bool or string values in the config, got {v} for key {k}")
            setattr(self, k, v)
    def dict_torch_dtype_to_str(self, d: Dict[str, Any]) -> None:
        if d.get("torch_dtype", None) is not None and not isinstance(d["torch_dtype"], str): d["torch_dtype"] = str(d["torch_dtype"]).split(".")[1]
        for value in d.values():
            if isinstance(value, dict): self.dict_torch_dtype_to_str(value)
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoConfig"):
        if not isinstance(auto_class, str): auto_class = auto_class.__name__
        import sapiens_transformers.models.auto as auto_module
        if not hasattr(auto_module, auto_class): raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    @staticmethod
    def _get_global_generation_defaults() -> Dict[str, Any]: return {'max_length': 20, 'min_length': 0, 'do_sample': False, 'early_stopping': False, 'num_beams': 1, 'num_beam_groups': 1, 'diversity_penalty': 0.0, 'temperature': 1.0, 'top_k': 50,
    'top_p': 1.0, 'typical_p': 1.0, 'repetition_penalty': 1.0, 'length_penalty': 1.0, 'no_repeat_ngram_size': 0, 'encoder_no_repeat_ngram_size': 0, 'bad_words_ids': None, 'num_return_sequences': 1, 'output_scores': False, 'return_dict_in_generate': False,
    'forced_bos_token_id': None, 'forced_eos_token_id': None, 'remove_invalid_values': False, 'exponential_decay_length_penalty': None, 'suppress_tokens': None, 'begin_suppress_tokens': None}
    def _get_non_default_generation_parameters(self) -> Dict[str, Any]:
        non_default_generation_parameters = {}
        decoder_attribute_name = None
        try: default_config = self.__class__()
        except ValueError:
            decoder_config = self.get_text_config(decoder=True)
            if decoder_config is not self: default_config = decoder_config.__class__()
            else: decoder_config = None
        self_decoder_config = self if decoder_attribute_name is None else getattr(self, decoder_attribute_name)
        for parameter_name, default_global_value in self._get_global_generation_defaults().items():
            if hasattr(self_decoder_config, parameter_name):
                is_default_in_config = is_default_generation_value = None
                parameter_value = getattr(self_decoder_config, parameter_name)
                if parameter_value is None: continue
                if default_config is not None: is_default_in_config = parameter_value == getattr(default_config, parameter_name)
                else: is_default_generation_value = parameter_value == default_global_value
                is_non_default = (is_default_in_config is False) or (is_default_in_config is None and is_default_generation_value is False)
                if is_non_default: non_default_generation_parameters[parameter_name] = getattr(self_decoder_config, parameter_name)
        return non_default_generation_parameters
    def get_text_config(self, decoder=False) -> "PretrainedConfig":
        decoder_possible_text_config_names = ("decoder", "generator", "text_config")
        encoder_possible_text_config_names = ("text_encoder",)
        if decoder: possible_text_config_names = decoder_possible_text_config_names
        else: possible_text_config_names = encoder_possible_text_config_names + decoder_possible_text_config_names
        valid_text_config_names = []
        for text_config_name in possible_text_config_names:
            if hasattr(self, text_config_name):
                text_config = getattr(self, text_config_name, None)
                if text_config is not None: valid_text_config_names += [text_config_name]
        if len(valid_text_config_names) > 1: raise ValueError(f"Multiple valid text configs were found in the model config: {valid_text_config_names}. In this case, using `get_text_config()` would be ambiguous. Please specify the desied text config directly.")
        elif len(valid_text_config_names) == 1: return getattr(self, valid_text_config_names[0])
        return self
class PRETRAINED_SAPIENS_TECHNOLOGY(PretrainedConfig): pass
def get_configuration_file(configuration_files: List[str]) -> str:
    configuration_files_map = {}
    for file_name in configuration_files:
        search = _re_configuration_file.search(file_name)
        if search is not None:
            v = search.groups()[0]
            configuration_files_map[v] = file_name
    available_versions = sorted(configuration_files_map.keys())
    configuration_file = CONFIG_NAME
    sapiens_transformers_version = version.parse(__version__)
    for v in available_versions:
        if version.parse(v) <= sapiens_transformers_version: configuration_file = configuration_files_map[v]
        else: break
    return configuration_file
def recursive_diff_dict(dict_a, dict_b, config_obj=None):
    diff = {}
    default = config_obj.__class__().to_dict() if config_obj is not None else {}
    for key, value in dict_a.items():
        obj_value = getattr(config_obj, str(key), None)
        if isinstance(obj_value, PretrainedConfig) and key in dict_b and isinstance(dict_b[key], dict):
            diff_value = recursive_diff_dict(value, dict_b[key], config_obj=obj_value)
            if len(diff_value) > 0: diff[key] = diff_value
        elif key not in dict_b or value != dict_b[key] or key not in default or value != default[key]: diff[key] = value
    return diff
PretrainedConfig.push_to_hub = copy_func(PretrainedConfig.push_to_hub)
if PretrainedConfig.push_to_hub.__doc__ is not None: PretrainedConfig.push_to_hub.__doc__ = PretrainedConfig.push_to_hub.__doc__.format(object="config", object_class="AutoConfig", object_files="configuration file")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
