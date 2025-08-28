"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import json
import os
import warnings
from dataclasses import dataclass, is_dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Union
from .. import __version__
from ..configuration_utils import PretrainedConfig
from ..utils import (GENERATION_CONFIG_NAME, ExplicitEnum, PushToHubMixin, cached_file, download_url, extract_commit_hash, is_remote_url, is_torch_available, logging)
if TYPE_CHECKING: from ..modeling_utils import PreTrainedModel
logger = logging.get_logger(__name__)
METADATA_FIELDS = ("_from_model_config", "_commit_hash", "_original_object_hash", "sapiens_transformers_version")
NEEDS_CACHE_CONFIG = {}
NEED_SETUP_CACHE_CLASSES_MAPPING = {}
QUANT_BACKEND_CLASSES_MAPPING = {}
ALL_CACHE_IMPLEMENTATIONS = []
if is_torch_available():
    from ..cache_utils import (HQQQuantizedCache, HybridCache, MambaCache, OffloadedStaticCache, QuantizedCacheConfig, QuantoQuantizedCache, SlidingWindowCache, StaticCache, StaticCacheConfig)
    NEEDS_CACHE_CONFIG["quantized"] = QuantizedCacheConfig
    NEEDS_CACHE_CONFIG["static"] = StaticCacheConfig
    NEED_SETUP_CACHE_CLASSES_MAPPING = {"static": StaticCache, "offloaded_static": OffloadedStaticCache, "sliding_window": SlidingWindowCache, "hybrid": HybridCache, "mamba": MambaCache}
    QUANT_BACKEND_CLASSES_MAPPING = {"quanto": QuantoQuantizedCache, "HQQ": HQQQuantizedCache}
    ALL_CACHE_IMPLEMENTATIONS = list(NEED_SETUP_CACHE_CLASSES_MAPPING.keys()) + list(NEEDS_CACHE_CONFIG.keys())
class GenerationMode(ExplicitEnum):
    CONTRASTIVE_SEARCH = "contrastive_search"
    GREEDY_SEARCH = "greedy_search"
    SAMPLE = "sample"
    ASSISTED_GENERATION = "assisted_generation"
    DOLA_GENERATION = "dola_generation"
    BEAM_SEARCH = "beam_search"
    BEAM_SAMPLE = "beam_sample"
    CONSTRAINED_BEAM_SEARCH = "constrained_beam_search"
    GROUP_BEAM_SEARCH = "group_beam_search"
class GenerationConfig(PushToHubMixin):
    extra_output_flags = ("output_attentions", "output_hidden_states", "output_scores", "output_logits")
    def __init__(self, **kwargs):
        self.max_length = kwargs.pop("max_length", 20)
        self.max_new_tokens = kwargs.pop("max_new_tokens", None)
        self.min_length = kwargs.pop("min_length", 0)
        self.min_new_tokens = kwargs.pop("min_new_tokens", None)
        self.early_stopping = kwargs.pop("early_stopping", False)
        self.max_time = kwargs.pop("max_time", None)
        self.stop_strings = kwargs.pop("stop_strings", None)
        self.do_sample = kwargs.pop("do_sample", False)
        self.num_beams = kwargs.pop("num_beams", 1)
        self.num_beam_groups = kwargs.pop("num_beam_groups", 1)
        self.penalty_alpha = kwargs.pop("penalty_alpha", None)
        self.dola_layers = kwargs.pop("dola_layers", None)
        self.use_cache = kwargs.pop("use_cache", True)
        self.cache_implementation = kwargs.pop("cache_implementation", None)
        self.cache_config = kwargs.pop("cache_config", None)
        if self.cache_implementation is not None and self.cache_implementation in NEEDS_CACHE_CONFIG:
            cache_config_class = NEEDS_CACHE_CONFIG[self.cache_implementation]
            if self.cache_config is None: self.cache_config = cache_config_class()
            elif isinstance(self.cache_config, dict): self.cache_config = cache_config_class.from_dict(self.cache_config)
        self.return_legacy_cache = kwargs.pop("return_legacy_cache", None)
        self.temperature = kwargs.pop("temperature", 1.0)
        self.top_k = kwargs.pop("top_k", 50)
        self.top_p = kwargs.pop("top_p", 1.0)
        self.min_p = kwargs.pop("min_p", None)
        self.typical_p = kwargs.pop("typical_p", 1.0)
        self.epsilon_cutoff = kwargs.pop("epsilon_cutoff", 0.0)
        self.eta_cutoff = kwargs.pop("eta_cutoff", 0.0)
        self.diversity_penalty = kwargs.pop("diversity_penalty", 0.0)
        self.repetition_penalty = kwargs.pop("repetition_penalty", 1.0)
        self.encoder_repetition_penalty = kwargs.pop("encoder_repetition_penalty", 1.0)
        self.length_penalty = kwargs.pop("length_penalty", 1.0)
        self.no_repeat_ngram_size = kwargs.pop("no_repeat_ngram_size", 0)
        self.bad_words_ids = kwargs.pop("bad_words_ids", None)
        self.force_words_ids = kwargs.pop("force_words_ids", None)
        self.renormalize_logits = kwargs.pop("renormalize_logits", False)
        self.constraints = kwargs.pop("constraints", None)
        self.forced_bos_token_id = kwargs.pop("forced_bos_token_id", None)
        self.forced_eos_token_id = kwargs.pop("forced_eos_token_id", None)
        self.remove_invalid_values = kwargs.pop("remove_invalid_values", False)
        self.exponential_decay_length_penalty = kwargs.pop("exponential_decay_length_penalty", None)
        self.suppress_tokens = kwargs.pop("suppress_tokens", None)
        self.begin_suppress_tokens = kwargs.pop("begin_suppress_tokens", None)
        self.forced_decoder_ids = kwargs.pop("forced_decoder_ids", None)
        self.sequence_bias = kwargs.pop("sequence_bias", None)
        self.token_healing = kwargs.pop("token_healing", False)
        self.guidance_scale = kwargs.pop("guidance_scale", None)
        self.low_memory = kwargs.pop("low_memory", None)
        watermarking_config = kwargs.pop("watermarking_config", None)
        if watermarking_config is None: self.watermarking_config = None
        elif isinstance(watermarking_config, WatermarkingConfig): self.watermarking_config = watermarking_config
        else: self.watermarking_config = WatermarkingConfig.from_dict(watermarking_config)
        self.num_return_sequences = kwargs.pop("num_return_sequences", 1)
        self.output_attentions = kwargs.pop("output_attentions", False)
        self.output_hidden_states = kwargs.pop("output_hidden_states", False)
        self.output_scores = kwargs.pop("output_scores", False)
        self.output_logits = kwargs.pop("output_logits", None)
        self.return_dict_in_generate = kwargs.pop("return_dict_in_generate", False)
        self.pad_token_id = kwargs.pop("pad_token_id", None)
        self.bos_token_id = kwargs.pop("bos_token_id", None)
        self.eos_token_id = kwargs.pop("eos_token_id", None)
        self.encoder_no_repeat_ngram_size = kwargs.pop("encoder_no_repeat_ngram_size", 0)
        self.decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)
        self.is_assistant = False
        self.num_assistant_tokens = kwargs.pop("num_assistant_tokens", 20)
        self.num_assistant_tokens_schedule = kwargs.pop("num_assistant_tokens_schedule", "constant")
        self.assistant_confidence_threshold = kwargs.pop("assistant_confidence_threshold", 0.4)
        self.prompt_lookup_num_tokens = kwargs.pop("prompt_lookup_num_tokens", None)
        self.max_matching_ngram_size = kwargs.pop("max_matching_ngram_size", None)
        self.generation_kwargs = kwargs.pop("generation_kwargs", {})
        self._from_model_config = kwargs.pop("_from_model_config", False)
        self._commit_hash = kwargs.pop("_commit_hash", None)
        self.sapiens_transformers_version = kwargs.pop("sapiens_transformers_version", __version__)
        if not self._from_model_config:
            for key, value in kwargs.items():
                try: setattr(self, key, value)
                except AttributeError as err:
                    logger.error(f"Can't set {key} with value {value} for {self}")
                    raise err
        self.validate(is_init=True)
    def __hash__(self): return hash(self.to_json_string(ignore_metadata=True))
    def __eq__(self, other):
        if not isinstance(other, GenerationConfig): return False
        self_without_metadata = self.to_json_string(use_diff=False, ignore_metadata=True)
        other_without_metadata = other.to_json_string(use_diff=False, ignore_metadata=True)
        return self_without_metadata == other_without_metadata
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string(ignore_metadata=True)}"
    def get_generation_mode(self, assistant_model: Optional["PreTrainedModel"] = None) -> GenerationMode:
        if self.constraints is not None or self.force_words_ids is not None: generation_mode = GenerationMode.CONSTRAINED_BEAM_SEARCH
        elif self.num_beams == 1:
            if self.do_sample is False:
                if (self.top_k is not None and self.top_k > 1 and self.penalty_alpha is not None and self.penalty_alpha > 0): generation_mode = GenerationMode.CONTRASTIVE_SEARCH
                else: generation_mode = GenerationMode.GREEDY_SEARCH
            else: generation_mode = GenerationMode.SAMPLE
        else:
            if self.num_beam_groups > 1: generation_mode = GenerationMode.GROUP_BEAM_SEARCH
            elif self.do_sample is True: generation_mode = GenerationMode.BEAM_SAMPLE
            else: generation_mode = GenerationMode.BEAM_SEARCH
        if assistant_model is not None or self.prompt_lookup_num_tokens is not None:
            if generation_mode in ("greedy_search", "sample"): generation_mode = GenerationMode.ASSISTED_GENERATION
            else: raise ValueError("You've set `assistant_model`, which triggers assisted generate. Currently, assisted generate is only supported with Greedy Search and Sample.")
        if self.dola_layers is not None:
            if generation_mode in ("greedy_search", "sample"): generation_mode = GenerationMode.DOLA_GENERATION
            else: raise ValueError("You've set `dola_layers`, which triggers DoLa generate. Currently, DoLa generate is only supported with Greedy Search and Sample.")
        return generation_mode
    def validate(self, is_init=False):
        if self.early_stopping not in {True, False, "never"}: raise ValueError(f"`early_stopping` must be a boolean or 'never', but is {self.early_stopping}.")
        if self.max_new_tokens is not None and self.max_new_tokens <= 0: raise ValueError(f"`max_new_tokens` must be greater than 0, but is {self.max_new_tokens}.")
        if self.pad_token_id is not None and self.pad_token_id < 0: warnings.warn(f"`pad_token_id` should be positive but got {self.pad_token_id}. This will cause errors when batch generating, if there is padding. Please set `pad_token_id` explicitly as `model.generation_config.pad_token_id=PAD_TOKEN_ID` to avoid errors in generation")
        fix_location = ""
        if is_init: fix_location = (" This was detected when initializing the generation config instance, which means the corresponding file may hold incorrect parameterization and should be fixed.")
        if self.do_sample is False:
            greedy_wrong_parameter_msg = ("`do_sample` is set to `False`. However, `{flag_name}` is set to `{flag_value}` -- this flag is only used in sample-based generation modes. You should set `do_sample=True` or unset `{flag_name}`." + fix_location)
            if self.temperature is not None and self.temperature != 1.0: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="temperature", flag_value=self.temperature), UserWarning)
            if self.top_p is not None and self.top_p != 1.0: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="top_p", flag_value=self.top_p), UserWarning)
            if self.min_p is not None: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="min_p", flag_value=self.min_p), UserWarning)
            if self.typical_p is not None and self.typical_p != 1.0: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="typical_p", flag_value=self.typical_p), UserWarning)
            if (self.top_k is not None and self.top_k != 50 and self.penalty_alpha is None): warnings.warn(greedy_wrong_parameter_msg.format(flag_name="top_k", flag_value=self.top_k), UserWarning)
            if self.epsilon_cutoff is not None and self.epsilon_cutoff != 0.0: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="epsilon_cutoff", flag_value=self.epsilon_cutoff), UserWarning)
            if self.eta_cutoff is not None and self.eta_cutoff != 0.0: warnings.warn(greedy_wrong_parameter_msg.format(flag_name="eta_cutoff", flag_value=self.eta_cutoff), UserWarning)
        if self.num_beams is None:
            warnings.warn("`num_beams` is set to None - defaulting to 1.", UserWarning)
            self.num_beams = 1
        if self.num_beams == 1:
            single_beam_wrong_parameter_msg = ("`num_beams` is set to 1. However, `{flag_name}` is set to `{flag_value}` -- this flag is only used in beam-based generation modes. You should set `num_beams>1` or unset `{flag_name}`." + fix_location)
            if self.early_stopping is not False: warnings.warn(single_beam_wrong_parameter_msg.format(flag_name="early_stopping", flag_value=self.early_stopping), UserWarning)
            if self.num_beam_groups is not None and self.num_beam_groups != 1: warnings.warn(single_beam_wrong_parameter_msg.format(flag_name="num_beam_groups", flag_value=self.num_beam_groups), UserWarning)
            if self.diversity_penalty is not None and self.diversity_penalty != 0.0: warnings.warn(single_beam_wrong_parameter_msg.format(flag_name="diversity_penalty", flag_value=self.diversity_penalty), UserWarning)
            if self.length_penalty is not None and self.length_penalty != 1.0: warnings.warn(single_beam_wrong_parameter_msg.format(flag_name="length_penalty", flag_value=self.length_penalty), UserWarning)
            if self.constraints is not None: warnings.warn(single_beam_wrong_parameter_msg.format(flag_name="constraints", flag_value=self.constraints), UserWarning)
        else:
            if self.constraints is not None or self.force_words_ids is not None:
                constrained_wrong_parameter_msg = ("one of `constraints`, `force_words_ids` is not `None`, triggering constrained beam search. However, `{flag_name}` is set to `{flag_value}`, which is incompatible with this generation mode. Set `constraints` and `force_words_ids` to `None` or unset `{flag_name}` to continue." + fix_location)
                if self.do_sample is True: raise ValueError(constrained_wrong_parameter_msg.format(flag_name="do_sample", flag_value=self.do_sample))
                if self.num_beam_groups is not None and self.num_beam_groups != 1: raise ValueError(constrained_wrong_parameter_msg.format(flag_name="num_beam_groups", flag_value=self.num_beam_groups))
            if self.diversity_penalty != 0.0 or self.num_beam_groups != 1:
                group_error_prefix = ("`diversity_penalty` is not 0.0 or `num_beam_groups` is not 1, triggering group beam search. In this generation mode, ")
                if self.do_sample is True: raise ValueError(group_error_prefix + "`do_sample` must be set to `False`")
                if self.num_beams % self.num_beam_groups != 0: raise ValueError(group_error_prefix + "`num_beams` should be divisible by `num_beam_groups`")
                if self.diversity_penalty == 0.0: raise ValueError(group_error_prefix + "`diversity_penalty` should be greater than `0.0`, otherwise your groups will be identical.")
            if self.dola_layers is not None and (self.repetition_penalty is None or self.repetition_penalty < 1.2): warnings.warn(f"`dola_layers` is set to trigger DoLa decoding, but `repetition_penalty` is set to a value of {self.repetition_penalty}, which could induce unwanted repetition. The recommended value for DoLa decoding is `repetition_penalty>=1.2`.", UserWarning)
        if self.num_return_sequences != 1:
            if self.num_beams == 1:
                if self.do_sample is False: raise ValueError(f"Greedy methods without beam search do not support `num_return_sequences` different than 1 (got {self.num_return_sequences}).")
            elif self.num_return_sequences > self.num_beams: raise ValueError(f"`num_return_sequences` ({self.num_return_sequences}) has to be smaller or equal to `num_beams` ({self.num_beams}).")
        if self.cache_implementation is not None and self.cache_implementation not in ALL_CACHE_IMPLEMENTATIONS: raise ValueError(f"Invalid `cache_implementation` ({self.cache_implementation}). Choose one of: {ALL_CACHE_IMPLEMENTATIONS}")
        if self.cache_config is not None:
            cache_class = NEEDS_CACHE_CONFIG.get(self.cache_implementation)
            if cache_class is None: raise ValueError(f"You provided a `cache_config` but the cache implementation you are using ({self.cache_implementation}) does not require any config. Make sure to use the correct cache implementation matching your cache config.")
            if not isinstance(self.cache_config, cache_class): self.cache_config = cache_class.from_dict(self.cache_config)
            self.cache_config.validate()
        if self.use_cache is False:
            cache_arg = cache_arg_value = None
            no_cache_warning = (f"You have set `use_cache` to `False`, but {cache_arg} is set to {cache_arg_value}. {cache_arg} will have no effect.")
            for arg_name in ("cache_implementation", "cache_config", "return_legacy_cache"):
                if getattr(self, arg_name) is not None: logger.warning_once(no_cache_warning.format(cache_arg=arg_name, cache_arg_value=getattr(self, arg_name)), UserWarning)
        if self.watermarking_config is not None:
            if not isinstance(self.watermarking_config, WatermarkingConfig): self.watermarking_config = WatermarkingConfig.from_dict(self.watermarking_config)
            self.watermarking_config.validate()
        if self.return_dict_in_generate is not True:
            for extra_output_flag in self.extra_output_flags:
                if getattr(self, extra_output_flag) is True: warnings.warn(f"`return_dict_in_generate` is NOT set to `True`, but `{extra_output_flag}` is. When `return_dict_in_generate` is not `True`, `{extra_output_flag}` is ignored.", UserWarning)
        generate_arguments = ("logits_processor", "stopping_criteria", "prefix_allowed_tokens_fn", "synced_gpus", "assistant_model", "streamer", "negative_prompt_ids", "negative_prompt_attention_mask")
        for arg in generate_arguments:
            if hasattr(self, arg): raise ValueError(f"Argument `{arg}` is not a valid argument of `GenerationConfig`. It should be passed to `generate()` (or a pipeline) directly.")
    def save_pretrained(self, save_directory: Union[str, os.PathLike], config_file_name: Optional[Union[str, os.PathLike]] = None, push_to_hub: bool = False, **kwargs):
        try:
            with warnings.catch_warnings(record=True) as caught_warnings: self.validate()
            if len(caught_warnings) > 0: raise ValueError(str([w.message for w in caught_warnings]))
        except ValueError as exc: raise ValueError("The generation config instance is invalid -- `.validate()` throws warnings and/or exceptions. Fix these issues to save the configuration.\n\nThrown during validation:\n" + str(exc))
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        config_file_name = config_file_name if config_file_name is not None else GENERATION_CONFIG_NAME
        if os.path.isfile(save_directory): raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        output_config_file = os.path.join(save_directory, config_file_name)
        self.to_json_file(output_config_file, use_diff=True)
        logger.info(f"Configuration saved in {output_config_file}")
        if push_to_hub: self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=kwargs.get("token"))
    @classmethod
    def from_pretrained(cls, pretrained_model_name: Union[str, os.PathLike], config_file_name: Optional[Union[str, os.PathLike]] = None, cache_dir: Optional[Union[str, os.PathLike]] = None, force_download: bool = False,
    local_files_only: bool = False, token: Optional[Union[str, bool]] = None, revision: str = "main", **kwargs) -> "GenerationConfig":
        config_file_name = config_file_name if config_file_name is not None else GENERATION_CONFIG_NAME
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        commit_hash = kwargs.pop("_commit_hash", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if token is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            token = use_auth_token
        user_agent = {"file_type": "config", "from_auto_class": from_auto_class}
        if from_pipeline is not None: user_agent["using_pipeline"] = from_pipeline
        config_path = os.path.join(pretrained_model_name, config_file_name)
        config_path = str(config_path)
        is_local = os.path.exists(config_path)
        if os.path.isfile(os.path.join(subfolder, config_path)):
            resolved_config_file = config_path
            is_local = True
        elif is_remote_url(config_path):
            configuration_file = config_path
            resolved_config_file = download_url(config_path)
        else:
            configuration_file = config_file_name
            try:
                resolved_config_file = cached_file(pretrained_model_name, configuration_file, cache_dir=cache_dir, force_download=force_download, proxies=proxies,
                resume_download=resume_download, local_files_only=local_files_only, token=token, user_agent=user_agent, revision=revision, subfolder=subfolder, _commit_hash=commit_hash)
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            except EnvironmentError: raise
            except Exception: raise EnvironmentError(f"Can't load the configuration of '{pretrained_model_name}'. Otherwise, make sure '{pretrained_model_name}' is the correct path to a directory containing a {configuration_file} file")
        try:
            config_dict = cls._dict_from_json_file(resolved_config_file)
            config_dict["_commit_hash"] = commit_hash
        except (json.JSONDecodeError, UnicodeDecodeError): raise EnvironmentError(f"It looks like the config file at '{resolved_config_file}' is not a valid JSON file.")
        if is_local: logger.info(f"loading configuration file {resolved_config_file}")
        else: logger.info(f"loading configuration file {configuration_file} from cache at {resolved_config_file}")
        if kwargs.get("return_unused_kwargs") is True:
            config, unused_kwargs = cls.from_dict(config_dict, **kwargs)
            config._original_object_hash = hash(config)
            return config, unused_kwargs
        else:
            config = cls.from_dict(config_dict, **kwargs)
            config._original_object_hash = hash(config)
            return config
    @classmethod
    def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, "r", encoding="utf-8") as reader: text = reader.read()
        return json.loads(text)
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], **kwargs) -> "GenerationConfig":
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        kwargs.pop("_from_auto", None)
        kwargs.pop("_from_pipeline", None)
        if "_commit_hash" in kwargs and "_commit_hash" in config_dict: kwargs["_commit_hash"] = config_dict["_commit_hash"]
        config = cls(**{**config_dict, **kwargs})
        unused_kwargs = config.update(**kwargs)
        logger.info(f"Generate config {config}")
        if return_unused_kwargs: return config, unused_kwargs
        else: return config
    def dict_torch_dtype_to_str(self, d: Dict[str, Any]) -> None:
        if d.get("torch_dtype", None) is not None and not isinstance(d["torch_dtype"], str): d["torch_dtype"] = str(d["torch_dtype"]).split(".")[1]
        for value in d.values():
            if isinstance(value, dict): self.dict_torch_dtype_to_str(value)
    def to_diff_dict(self) -> Dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = GenerationConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if key not in default_config_dict or key == "sapiens_transformers_version" or value != default_config_dict[key]: serializable_config_dict[key] = value
        self.dict_torch_dtype_to_str(serializable_config_dict)
        return serializable_config_dict
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        if "_commit_hash" in output: del output["_commit_hash"]
        if "_original_object_hash" in output: del output["_original_object_hash"]
        output["sapiens_transformers_version"] = __version__
        self.dict_torch_dtype_to_str(output)
        return output
    def to_json_string(self, use_diff: bool = True, ignore_metadata: bool = False) -> str:
        if use_diff is True: config_dict = self.to_diff_dict()
        else: config_dict = self.to_dict()
        if ignore_metadata:
            for metadata_field in METADATA_FIELDS: config_dict.pop(metadata_field, None)
        def convert_keys_to_string(obj):
            if isinstance(obj, dict): return {str(key): convert_keys_to_string(value) for key, value in obj.items()}
            elif isinstance(obj, list): return [convert_keys_to_string(item) for item in obj]
            else: return obj
        def convert_dataclass_to_dict(obj):
            if isinstance(obj, dict): return {key: convert_dataclass_to_dict(value) for key, value in obj.items()}
            elif is_dataclass(obj): return obj.to_dict()
            else: return obj
        config_dict = convert_keys_to_string(config_dict)
        config_dict = convert_dataclass_to_dict(config_dict)
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike], use_diff: bool = True):
        with open(json_file_path, "w", encoding="utf-8") as writer: writer.write(self.to_json_string(use_diff=use_diff))
    @classmethod
    def from_model_config(cls, model_config: PretrainedConfig) -> "GenerationConfig":
        config_dict = model_config.to_dict()
        config_dict.pop("_from_model_config", None)
        config_dict = {key: value for key, value in config_dict.items() if value is not None}
        generation_config = cls.from_dict(config_dict, return_unused_kwargs=False, _from_model_config=True)
        decoder_config = model_config.get_text_config(decoder=True)
        if decoder_config is not model_config:
            default_generation_config = GenerationConfig()
            decoder_config_dict = decoder_config.to_dict()
            for attr in generation_config.to_dict().keys():
                is_unset = getattr(generation_config, attr) == getattr(default_generation_config, attr)
                if attr in decoder_config_dict and is_unset: setattr(generation_config, attr, decoder_config_dict[attr])
        if generation_config.return_dict_in_generate is False:
            if any(getattr(generation_config, extra_output_flag, False) for extra_output_flag in generation_config.extra_output_flags): generation_config.return_dict_in_generate = True
        generation_config._original_object_hash = hash(generation_config)
        return generation_config
    def update(self, **kwargs):
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        self.validate()
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs
@dataclass
class WatermarkingConfig:
    def __init__(self, greenlist_ratio: Optional[float] = 0.25, bias: Optional[float] = 2.0, hashing_key: Optional[int] = 15485863, seeding_scheme: Optional[str] = "lefthash", context_width: Optional[int] = 1):
        self.greenlist_ratio = greenlist_ratio
        self.bias = bias
        self.hashing_key = hashing_key
        self.seeding_scheme = seeding_scheme
        self.context_width = context_width
    @classmethod
    def from_dict(cls, config_dict, **kwargs):
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
            writer.write(json_string)
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        return output
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items(): yield attr, value
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_json_string(self): return json.dumps(self.__dict__, indent=2) + "\n"
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key): setattr(self, key, value)
    def validate(self):
        watermark_missing_arg_msg = (f"Some of the keys in `watermarking_config` are defined incorrectly. `{key}` should be {correct_value}` but found {found_value}")
        if self.seeding_scheme not in ["selfhash", "lefthash"]: raise ValueError(watermark_missing_arg_msg.format(key="seeding_scheme", correct_value="[`selfhash`, `lefthash`]", found_value=self.seeding_scheme))
        if not 0.0 <= self.greenlist_ratio <= 1.0: raise ValueError(watermark_missing_arg_msg.format(key="greenlist_ratio", correct_value="in range between 0.0 and 1.0", found_value=self.seeding_scheme))
        if not self.context_width >= 1: raise ValueError(watermark_missing_arg_msg.format(key="context_width", correct_value="a positive integer", found_value=self.context_width))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
