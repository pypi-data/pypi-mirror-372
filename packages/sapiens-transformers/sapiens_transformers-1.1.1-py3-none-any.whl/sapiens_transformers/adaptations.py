"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from sapiens_transformers import (MllamaForConditionalGeneration as ModularEntityForConditionalGeneration, AutoProcessor as ModularEntityAutoProcessor, AutoProcessor as HurLMAutoProcessor,
AutoModelForVision2Seq as AutoModelForHurLM, MusicgenForConditionalGeneration as SAPIMusicForConditionalGeneration, AutoProcessor as SAPIMusicAutoProcessor)
from sapiens_transformers import LlavaNextVideoProcessor as SAPIVideoProcessor, LlavaNextVideoForConditionalGeneration as SAPIVideoForConditionalGeneration
from sapiens_transformers import LlavaNextImageProcessor as SAPIImageProcessor, LlavaNextForConditionalGeneration as SAPIImageForConditionalGeneration
from .diffusers import MotionAdapter as SapiensMotionAdapter, EulerDiscreteScheduler as SapiensEulerDiscreteScheduler
from torch import bfloat16 as SAPIENS_PRECISION1, float16 as SAPIENS_PRECISION2, float32 as SAPIENS_PRECISION3
try: from nemo.collections.common.tokenizers.huggingface.auto_tokenizer import AutoTokenizer as SAPITokenizer
except: from sapiens_transformers import AutoTokenizer as SAPITokenizer
try: from nemo.collections.nlp.parts.nlp_overrides import NLPDDPStrategy as SAPIStrategy
except: from sapiens_transformers import TrainingArguments as SAPIStrategy
from .sapiens_utils import process_vision_info as sapiens_vision_processor
from .diffusers import FluxPipeline as SapiensImageGenerator
try: from audiocraft.models import MusicGen as SAPIMusicGen
except: SAPIMusicGen = SAPIMusicForConditionalGeneration
from .utils.sapi_audiogen import SAPIAudioGen
SAPIENS_PRECISIONX, STATE1X, STATE1Y, STATE2X, STATE2Y, ALLEGRO_COMPATIBILITY = 'auto', 'safetensors', 'ben', 'bin', 'hur', 'allegro'
(HURLM_COMPATIBILITY, SAPI_ZERO_COMPATIBILITY, SAPIENS_COMPATIBILITY, SASTRAL_COMPATIBILITY, MODULAR_ENTITY_COMPATIBILITY, SAPIENS_VISION_COMPATIBILITY, SAPI_IMAGE_COMPATIBILITY,
SAPIENS_IMAGEGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPI_PHOTOGEN_COMPATIBILITY, SAPI_AUDIO_COMPATIBILITY, SAPI_AUDIOGEN_COMPATIBILITY, SAPI_MUSICGEN_COMPATIBILITY,
SAPI_VIDEO_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_POSSIBILITIES) = (('hurlm', 'idefics3'), ('sapi_zero', 'granite'), ('sapiens', 'qwen2'),
('sastral', 'mistral'), ('modular_entity', 'modularentity', 'mllama'), ('sapiens_vision', 'sapiensvision', 'qwen2vl', 'qwen2_vl'), ('sapi_image', 'sapiimage', 'llavanext', 'llava_next'),
('sapiens_imagegen', 'sapiensimagegen', 'sana'), ('sapi_imagegen', 'sapiimagegen', 'stablediffusion3', 'stable_diffusion_3'), ('sapi_photogen', 'sapiphotogen', 'flux'), ('sapi_audio', 'sapiaudio',
'whisper'), ('sapi_audiogen', 'sapiaudiogen', 'xtts'), ('sapi_musicgen', 'sapimusicgen', 'sapi_music', 'sapimusic', 'encodec', 'musicgen'), ('sapi_video', 'sapivideo', 'llavanextvideo',
'llava_next_video'), ('sapiens_videogen', 'sapiensvideogen', 'ltx'), ('sapi_videogen', 'sapivideogen', 'animatediff'), ('sapi_videogen', 'sapi-videogen', 'sapivideogen', 'animatediff'))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
