"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
import inspect
import json
import os
import warnings
from collections import OrderedDict
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...feature_extraction_utils import FeatureExtractionMixin
from ...image_processing_utils import ImageProcessingMixin
from ...processing_utils import ProcessorMixin
from ...tokenization_utils import TOKENIZER_CONFIG_FILE
from ...utils import FEATURE_EXTRACTOR_NAME, PROCESSOR_NAME, get_file_from_repo, logging
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (CONFIG_MAPPING_NAMES, AutoConfig, model_type_to_module_name, replace_list_option_in_docstrings)
from .feature_extraction_auto import AutoFeatureExtractor
from .image_processing_auto import AutoImageProcessor
from .tokenization_auto import AutoTokenizer
logger = logging.get_logger(__name__)
PROCESSOR_MAPPING_NAMES = OrderedDict([("align", "AlignProcessor"), ("altclip", "AltCLIPProcessor"), ("bark", "BarkProcessor"), ("blip", "BlipProcessor"), ("blip-2", "Blip2Processor"),
("bridgetower", "BridgeTowerProcessor"), ("chameleon", "ChameleonProcessor"), ("chinese_clip", "ChineseCLIPProcessor"), ("clap", "ClapProcessor"), ("clip", "CLIPProcessor"),
("clipseg", "CLIPSegProcessor"), ("clvp", "ClvpProcessor"), ("flava", "FlavaProcessor"), ("fuyu", "FuyuProcessor"), ("git", "GitProcessor"), ("grounding-dino", "GroundingDinoProcessor"),
("groupvit", "CLIPProcessor"), ("hubert", "Wav2Vec2Processor"), ("hurlm", "HurLMProcessor"), ("idefics", "IdeficsProcessor"), ("idefics2", "Idefics2Processor"), ("instructblip", "InstructBlipProcessor"),
("instructblipvideo", "InstructBlipVideoProcessor"), ("kosmos-2", "Kosmos2Processor"), ("layoutlmv2", "LayoutLMv2Processor"), ("layoutlmv3", "LayoutLMv3Processor"),
("llava", "LlavaProcessor"), ("llava_next", "LlavaNextProcessor"), ("llava_next_video", "LlavaNextVideoProcessor"), ("llava_onevision", "LlavaOnevisionProcessor"),
("markuplm", "MarkupLMProcessor"), ("mctct", "MCTCTProcessor"), ("mgp-str", "MgpstrProcessor"), ("mllama", "MllamaProcessor"), ("modular_entity", "ModularEntityProcessor"),
("oneformer", "OneFormerProcessor"), ("owlv2", "Owlv2Processor"), ("owlvit", "OwlViTProcessor"), ("paligemma", "PaliGemmaProcessor"), ("pix2struct", "Pix2StructProcessor"), ("pixtral", "PixtralProcessor"),
("pop2piano", "Pop2PianoProcessor"), ("qwen2_audio", "Qwen2AudioProcessor"), ("qwen2_vl", "Qwen2VLProcessor"), ("sam", "SamProcessor"), ("sapi_audio", "SAPIAudioProcessor"), ("sapi_image", "SAPIImageProcessor"), ("sapi_video", "SAPIVideoProcessor"),
("sapiens_vision", "SapiensVisionProcessor"), ("seamless_m4t", "SeamlessM4TProcessor"), ("sew", "Wav2Vec2Processor"), ("sew-d", "Wav2Vec2Processor"), ("siglip", "SiglipProcessor"), ("speech_to_text", "Speech2TextProcessor"),
("speech_to_text_2", "Speech2Text2Processor"), ("speecht5", "SpeechT5Processor"), ("trocr", "TrOCRProcessor"), ("tvlt", "TvltProcessor"), ("tvp", "TvpProcessor"), ("unispeech", "Wav2Vec2Processor"), ("unispeech-sat", "Wav2Vec2Processor"),
("video_llava", "VideoLlavaProcessor"), ("vilt", "ViltProcessor"), ("vipllava", "LlavaProcessor"), ("vision-text-dual-encoder", "VisionTextDualEncoderProcessor"), ("wav2vec2", "Wav2Vec2Processor"),
("wav2vec2-bert", "Wav2Vec2Processor"), ("wav2vec2-conformer", "Wav2Vec2Processor"), ("wavlm", "Wav2Vec2Processor"), ("whisper", "WhisperProcessor"), ("xclip", "XCLIPProcessor")])
PROCESSOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, PROCESSOR_MAPPING_NAMES)
def processor_class_from_name(class_name: str):
    for module_name, processors in PROCESSOR_MAPPING_NAMES.items():
        if class_name in processors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "sapiens_transformers.models")
            try: return getattr(module, class_name)
            except AttributeError: continue
    for processor in PROCESSOR_MAPPING._extra_content.values():
        if getattr(processor, "__name__", None) == class_name: return processor
    main_module = importlib.import_module("sapiens_transformers")
    if hasattr(main_module, class_name): return getattr(main_module, class_name)
    return None
class AutoProcessor:
    def __init__(self): raise EnvironmentError("AutoProcessor is designed to be instantiated using the `AutoProcessor.from_pretrained(pretrained_model_name_or_path)` method.")
    @classmethod
    @replace_list_option_in_docstrings(PROCESSOR_MAPPING_NAMES)
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        config = kwargs.pop("config", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        processor_class = None
        processor_auto_map = None
        get_file_from_repo_kwargs = {key: kwargs[key] for key in inspect.signature(get_file_from_repo).parameters.keys() if key in kwargs}
        processor_config_file = get_file_from_repo(pretrained_model_name_or_path, PROCESSOR_NAME, **get_file_from_repo_kwargs)
        if processor_config_file is not None:
            config_dict, _ = ProcessorMixin.get_processor_dict(pretrained_model_name_or_path, **kwargs)
            processor_class = config_dict.get("processor_class", None)
            if "AutoProcessor" in config_dict.get("auto_map", {}): processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            preprocessor_config_file = get_file_from_repo(pretrained_model_name_or_path, FEATURE_EXTRACTOR_NAME, **get_file_from_repo_kwargs)
            if preprocessor_config_file is not None:
                config_dict, _ = ImageProcessingMixin.get_image_processor_dict(pretrained_model_name_or_path, **kwargs)
                processor_class = config_dict.get("processor_class", None)
                if "AutoProcessor" in config_dict.get("auto_map", {}): processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
            if preprocessor_config_file is not None and processor_class is None:
                config_dict, _ = FeatureExtractionMixin.get_feature_extractor_dict(pretrained_model_name_or_path, **kwargs)
                processor_class = config_dict.get("processor_class", None)
                if "AutoProcessor" in config_dict.get("auto_map", {}): processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            tokenizer_config_file = get_file_from_repo(pretrained_model_name_or_path, TOKENIZER_CONFIG_FILE, **get_file_from_repo_kwargs)
            if tokenizer_config_file is not None:
                with open(tokenizer_config_file, encoding="utf-8") as reader: config_dict = json.load(reader)
                processor_class = config_dict.get("processor_class", None)
                if "AutoProcessor" in config_dict.get("auto_map", {}): processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            if not isinstance(config, PretrainedConfig): config = AutoConfig.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
            processor_class = getattr(config, "processor_class", None)
            if hasattr(config, "auto_map") and "AutoProcessor" in config.auto_map: processor_auto_map = config.auto_map["AutoProcessor"]
        if processor_class is not None: processor_class = processor_class_from_name(processor_class)
        has_remote_code = processor_auto_map is not None
        has_local_code = processor_class is not None or type(config) in PROCESSOR_MAPPING
        trust_remote_code = resolve_trust_remote_code(trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code)
        if has_remote_code and trust_remote_code:
            processor_class = get_class_from_dynamic_module(processor_auto_map, pretrained_model_name_or_path, **kwargs)
            _ = kwargs.pop("code_revision", None)
            if os.path.isdir(pretrained_model_name_or_path): processor_class.register_for_auto_class()
            return processor_class.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
        elif processor_class is not None: return processor_class.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
        elif type(config) in PROCESSOR_MAPPING: return PROCESSOR_MAPPING[type(config)].from_pretrained(pretrained_model_name_or_path, **kwargs)
        try: return AutoTokenizer.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
        except Exception:
            try: return AutoImageProcessor.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
            except Exception: pass
            try: return AutoFeatureExtractor.from_pretrained(pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs)
            except Exception: pass
        raise ValueError(f"Unrecognized processing class in {pretrained_model_name_or_path}. Can't instantiate a processor, a tokenizer, an image processor or a feature extractor for this model. Make sure the repository contains the files of at least one of those processing classes.")
    @staticmethod
    def register(config_class, processor_class, exist_ok=False): PROCESSOR_MAPPING.register(config_class, processor_class, exist_ok=exist_ok)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
