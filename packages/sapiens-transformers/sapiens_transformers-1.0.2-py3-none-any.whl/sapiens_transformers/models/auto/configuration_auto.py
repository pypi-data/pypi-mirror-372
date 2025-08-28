"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
import os
import re
import warnings
from collections import OrderedDict
from typing import List, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...utils import CONFIG_NAME, logging
logger = logging.get_logger(__name__)
CONFIG_MAPPING_NAMES = OrderedDict([("albert", "AlbertConfig"), ("align", "AlignConfig"), ("altclip", "AltCLIPConfig"), ("audio-spectrogram-transformer", "ASTConfig"), ("autoformer", "AutoformerConfig"), ("bark", "BarkConfig"),
("bart", "BartConfig"), ("beit", "BeitConfig"), ("bert", "BertConfig"), ("bert-generation", "BertGenerationConfig"), ("big_bird", "BigBirdConfig"), ("bigbird_pegasus", "BigBirdPegasusConfig"),
("biogpt", "BioGptConfig"), ("bit", "BitConfig"), ("blenderbot", "BlenderbotConfig"), ("blenderbot-small", "BlenderbotSmallConfig"), ("blip", "BlipConfig"), ("blip-2", "Blip2Config"),
("bloom", "BloomConfig"), ("bridgetower", "BridgeTowerConfig"), ("bros", "BrosConfig"), ("camembert", "CamembertConfig"), ("canine", "CanineConfig"), ("chameleon", "ChameleonConfig"),
("chinese_clip", "ChineseCLIPConfig"), ("chinese_clip_vision_model", "ChineseCLIPVisionConfig"), ("clap", "ClapConfig"), ("clip", "CLIPConfig"), ("clip_text_model", "CLIPTextConfig"),
("clip_vision_model", "CLIPVisionConfig"), ("clipseg", "CLIPSegConfig"), ("clvp", "ClvpConfig"), ("code_llama", "LlamaConfig"), ("codegen", "CodeGenConfig"), ("cohere", "CohereConfig"),
("conditional_detr", "ConditionalDetrConfig"), ("convbert", "ConvBertConfig"), ("convnext", "ConvNextConfig"), ("convnextv2", "ConvNextV2Config"), ("cpmant", "CpmAntConfig"), ("ctrl", "CTRLConfig"),
("cvt", "CvtConfig"), ("dac", "DacConfig"), ("data2vec-audio", "Data2VecAudioConfig"), ("data2vec-text", "Data2VecTextConfig"), ("data2vec-vision", "Data2VecVisionConfig"), ("dbrx", "DbrxConfig"),
("deberta", "DebertaConfig"), ("deberta-v2", "DebertaV2Config"), ("decision_transformer", "DecisionTransformerConfig"), ("deformable_detr", "DeformableDetrConfig"), ("deit", "DeiTConfig"),
("depth_anything", "DepthAnythingConfig"), ("deta", "DetaConfig"), ("detr", "DetrConfig"), ("dinat", "DinatConfig"), ("dinov2", "Dinov2Config"), ("distilbert", "DistilBertConfig"),
("donut-swin", "DonutSwinConfig"), ("dpr", "DPRConfig"), ("dpt", "DPTConfig"), ("efficientformer", "EfficientFormerConfig"), ("efficientnet", "EfficientNetConfig"), ("electra", "ElectraConfig"),
("encodec", "EncodecConfig"), ("encoder-decoder", "EncoderDecoderConfig"), ("entity", "EntityConfig"), ("ernie", "ErnieConfig"), ("ernie_m", "ErnieMConfig"), ("esm", "EsmConfig"), ("falcon", "FalconConfig"),
("falcon_mamba", "FalconMambaConfig"), ("fastspeech2_conformer", "FastSpeech2ConformerConfig"), ("flaubert", "FlaubertConfig"), ("flava", "FlavaConfig"), ("fnet", "FNetConfig"),
("focalnet", "FocalNetConfig"), ("fsmt", "FSMTConfig"), ("funnel", "FunnelConfig"), ("fuyu", "FuyuConfig"), ("gemma", "GemmaConfig"), ("gemma2", "Gemma2Config"), ("git", "GitConfig"),
("glpn", "GLPNConfig"), ("gpt-sw3", "GPT2Config"), ("gpt2", "GPT2Config"), ("gpt_bigcode", "GPTBigCodeConfig"), ("gpt_neo", "GPTNeoConfig"), ("gpt_neox", "GPTNeoXConfig"),
("gpt_neox_japanese", "GPTNeoXJapaneseConfig"), ("gptj", "GPTJConfig"), ("gptsan-japanese", "GPTSanJapaneseConfig"), ("granite", "GraniteConfig"), ("granitemoe", "GraniteMoeConfig"),
("graphormer", "GraphormerConfig"), ("grounding-dino", "GroundingDinoConfig"), ("groupvit", "GroupViTConfig"), ("hiera", "HieraConfig"), ("hubert", "HubertConfig"), ("hurlm", "HurLMConfig"),
("ibert", "IBertConfig"), ("idefics", "IdeficsConfig"), ("idefics2", "Idefics2Config"), ("imagegpt", "ImageGPTConfig"), ("informer", "InformerConfig"), ("instructblip", "InstructBlipConfig"),
("instructblipvideo", "InstructBlipVideoConfig"), ("jamba", "JambaConfig"), ("jetmoe", "JetMoeConfig"), ("jukebox", "JukeboxConfig"), ("kosmos-2", "Kosmos2Config"), ("layoutlm", "LayoutLMConfig"),
("layoutlmv2", "LayoutLMv2Config"), ("layoutlmv3", "LayoutLMv3Config"), ("led", "LEDConfig"), ("levit", "LevitConfig"), ("lilt", "LiltConfig"), ("llama", "LlamaConfig"), ("llava", "LlavaConfig"),
("llava_next", "LlavaNextConfig"), ("llava_next_video", "LlavaNextVideoConfig"), ("llava_onevision", "LlavaOnevisionConfig"), ("longformer", "LongformerConfig"), ("longt5", "LongT5Config"),
("luke", "LukeConfig"), ("lxmert", "LxmertConfig"), ("m2m_100", "M2M100Config"), ("mamba", "MambaConfig"), ("mamba2", "Mamba2Config"), ("marian", "MarianConfig"), ("markuplm", "MarkupLMConfig"),
("mask2former", "Mask2FormerConfig"), ("maskformer", "MaskFormerConfig"), ("maskformer-swin", "MaskFormerSwinConfig"), ("mbart", "MBartConfig"), ("mctct", "MCTCTConfig"), ("mega", "MegaConfig"),
("megatron-bert", "MegatronBertConfig"), ("mgp-str", "MgpstrConfig"), ("mimi", "MimiConfig"), ("mistral", "MistralConfig"), ("mixtral", "MixtralConfig"), ("mllama", "MllamaConfig"),
("mobilebert", "MobileBertConfig"), ("mobilenet_v1", "MobileNetV1Config"), ("mobilenet_v2", "MobileNetV2Config"), ("mobilevit", "MobileViTConfig"), ("mobilevitv2", "MobileViTV2Config"), ("modular_entity", "ModularEntityConfig"),
("mpnet", "MPNetConfig"), ("mpt", "MptConfig"), ("mra", "MraConfig"), ("mt5", "MT5Config"), ("musicgen", "MusicgenConfig"), ("musicgen_melody", "MusicgenMelodyConfig"), ("mvp", "MvpConfig"),
("nat", "NatConfig"), ("nemotron", "NemotronConfig"), ("nezha", "NezhaConfig"), ("nllb-moe", "NllbMoeConfig"), ("nougat", "VisionEncoderDecoderConfig"), ("nystromformer", "NystromformerConfig"),
("olmo", "OlmoConfig"), ("olmoe", "OlmoeConfig"), ("omdet-turbo", "OmDetTurboConfig"), ("oneformer", "OneFormerConfig"), ("open-llama", "OpenLlamaConfig"), ("openai-gpt", "OpenAIGPTConfig"),
("opt", "OPTConfig"), ("owlv2", "Owlv2Config"), ("owlvit", "OwlViTConfig"), ("paligemma", "PaliGemmaConfig"), ("patchtsmixer", "PatchTSMixerConfig"), ("patchtst", "PatchTSTConfig"),
("pegasus", "PegasusConfig"), ("pegasus_x", "PegasusXConfig"), ("perceiver", "PerceiverConfig"), ("persimmon", "PersimmonConfig"), ("phi", "PhiConfig"), ("phi3", "Phi3Config"),
("pix2struct", "Pix2StructConfig"), ("pixtral", "PixtralVisionConfig"), ("plbart", "PLBartConfig"), ("poolformer", "PoolFormerConfig"), ("pop2piano", "Pop2PianoConfig"), ("prophetnet", "ProphetNetConfig"),
("pvt", "PvtConfig"), ("pvt_v2", "PvtV2Config"), ("qdqbert", "QDQBertConfig"), ("qwen2", "Qwen2Config"), ("qwen2_audio", "Qwen2AudioConfig"),
("qwen2_audio_encoder", "Qwen2AudioEncoderConfig"), ("qwen2_moe", "Qwen2MoeConfig"), ("qwen2_vl", "Qwen2VLConfig"), ("rag", "RagConfig"), ("realm", "RealmConfig"), ("recurrent_gemma", "RecurrentGemmaConfig"),
("reformer", "ReformerConfig"), ("regnet", "RegNetConfig"), ("rembert", "RemBertConfig"), ("resnet", "ResNetConfig"), ("retribert", "RetriBertConfig"), ("roberta", "RobertaConfig"),
("roberta-prelayernorm", "RobertaPreLayerNormConfig"), ("roc_bert", "RoCBertConfig"), ("roformer", "RoFormerConfig"), ("rt_detr", "RTDetrConfig"), ("rt_detr_resnet", "RTDetrResNetConfig"),
("rwkv", "RwkvConfig"), ("sam", "SamConfig"), ("sapama", "SapamaConfig"), ("sapi", "SAPIConfig"), ("sapi_audio", "SAPIAudioConfig"),
("sapi_image", "SAPIImageConfig"), ("sapi_music", "SAPIMusicConfig"), ("sapi_musicgen", "SAPIMusicGenConfig"), ("sapi_video", "SAPIVideoConfig"), ("sapi_zero", "SAPIZeroConfig"),
("sapiens", "SapiensConfig"), ("sapiens_code", "SapiensCodeConfig"), ("sapiens_vision", "SapiensVisionConfig"), ("sastral", "SastralConfig"),
("seamless_m4t", "SeamlessM4TConfig"), ("seamless_m4t_v2", "SeamlessM4Tv2Config"), ("segformer", "SegformerConfig"),
("seggpt", "SegGptConfig"), ("sew", "SEWConfig"), ("sew-d", "SEWDConfig"), ("siglip", "SiglipConfig"), ("siglip_vision_model", "SiglipVisionConfig"),
("speech-encoder-decoder", "SpeechEncoderDecoderConfig"), ("speech_to_text", "Speech2TextConfig"),
("speech_to_text_2", "Speech2Text2Config"), ("speecht5", "SpeechT5Config"), ("splinter", "SplinterConfig"), ("squeezebert", "SqueezeBertConfig"),
("stablelm", "StableLmConfig"), ("starcoder2", "Starcoder2Config"), ("superpoint", "SuperPointConfig"),
("swiftformer", "SwiftFormerConfig"), ("swin", "SwinConfig"), ("swin2sr", "Swin2SRConfig"), ("swinv2", "Swinv2Config"), ("switch_transformers", "SwitchTransformersConfig"),
("t5", "T5Config"), ("table-transformer", "TableTransformerConfig"), ("tapas", "TapasConfig"),
("time_series_transformer", "TimeSeriesTransformerConfig"), ("timesformer", "TimesformerConfig"), ("timm_backbone", "TimmBackboneConfig"), ("trajectory_transformer", "TrajectoryTransformerConfig"),
("transfo-xl", "TransfoXLConfig"), ("trocr", "TrOCRConfig"), ("tvlt", "TvltConfig"), ("tvp", "TvpConfig"), ("udop", "UdopConfig"), ("umt5", "UMT5Config"), ("unispeech", "UniSpeechConfig"),
("unispeech-sat", "UniSpeechSatConfig"), ("univnet", "UnivNetConfig"), ("upernet", "UperNetConfig"), ("van", "VanConfig"), ("video_llava", "VideoLlavaConfig"), ("videomae", "VideoMAEConfig"),
("vilt", "ViltConfig"), ("vipllava", "VipLlavaConfig"), ("vision-encoder-decoder", "VisionEncoderDecoderConfig"), ("vision-text-dual-encoder", "VisionTextDualEncoderConfig"),
("visual_bert", "VisualBertConfig"), ("vit", "ViTConfig"), ("vit_hybrid", "ViTHybridConfig"), ("vit_mae", "ViTMAEConfig"), ("vit_msn", "ViTMSNConfig"), ("vitdet", "VitDetConfig"),
("vitmatte", "VitMatteConfig"), ("vits", "VitsConfig"), ("vivit", "VivitConfig"), ("wav2vec2", "Wav2Vec2Config"), ("wav2vec2-bert", "Wav2Vec2BertConfig"), ("wav2vec2-conformer", "Wav2Vec2ConformerConfig"),
("wavlm", "WavLMConfig"), ("whisper", "WhisperConfig"), ("xclip", "XCLIPConfig"), ("xglm", "XGLMConfig"), ("xlm", "XLMConfig"), ("xlm-prophetnet", "XLMProphetNetConfig"), ("xlm-roberta", "XLMRobertaConfig"),
("xlm-roberta-xl", "XLMRobertaXLConfig"), ("xlnet", "XLNetConfig"), ("xmod", "XmodConfig"), ("yolos", "YolosConfig"), ("yoso", "YosoConfig"), ("zoedepth", "ZoeDepthConfig")])
MODEL_NAMES_MAPPING = OrderedDict([("albert", "ALBERT"), ("align", "ALIGN"), ("altclip", "AltCLIP"),
("audio-spectrogram-transformer", "Audio Spectrogram Transformer"), ("autoformer", "Autoformer"), ("bark", "Bark"), ("bart", "BART"),
("barthez", "BARThez"), ("bartpho", "BARTpho"), ("beit", "BEiT"), ("bert", "BERT"), ("bert-generation", "Bert Generation"), ("bert-japanese", "BertJapanese"), ("bertweet", "BERTweet"), ("big_bird", "BigBird"),
("bigbird_pegasus", "BigBird-Pegasus"), ("biogpt", "BioGpt"), ("bit", "BiT"), ("blenderbot", "Blenderbot"), ("blenderbot-small", "BlenderbotSmall"), ("blip", "BLIP"), ("blip-2", "BLIP-2"), ("bloom", "BLOOM"),
("bort", "BORT"), ("bridgetower", "BridgeTower"), ("bros", "BROS"), ("byt5", "ByT5"), ("camembert", "CamemBERT"), ("canine", "CANINE"), ("chameleon", "Chameleon"), ("chinese_clip", "Chinese-CLIP"),
("chinese_clip_vision_model", "ChineseCLIPVisionModel"), ("clap", "CLAP"), ("clip", "CLIP"), ("clip_text_model", "CLIPTextModel"), ("clip_vision_model", "CLIPVisionModel"), ("clipseg", "CLIPSeg"),
("clvp", "CLVP"), ("code_llama", "CodeLlama"), ("codegen", "CodeGen"), ("cohere", "Cohere"), ("conditional_detr", "Conditional DETR"), ("convbert", "ConvBERT"), ("convnext", "ConvNeXT"),
("convnextv2", "ConvNeXTV2"), ("cpm", "CPM"), ("cpmant", "CPM-Ant"), ("ctrl", "CTRL"), ("cvt", "CvT"), ("dac", "DAC"), ("data2vec-audio", "Data2VecAudio"), ("data2vec-text", "Data2VecText"),
("data2vec-vision", "Data2VecVision"), ("dbrx", "DBRX"), ("deberta", "DeBERTa"), ("deberta-v2", "DeBERTa-v2"), ("decision_transformer", "Decision Transformer"), ("deformable_detr", "Deformable DETR"),
("deit", "DeiT"), ("deplot", "DePlot"), ("depth_anything", "Depth Anything"), ("depth_anything_v2", "Depth Anything V2"), ("deta", "DETA"), ("detr", "DETR"), ("dialogpt", "DialoGPT"), ("dinat", "DiNAT"),
("dinov2", "DINOv2"), ("distilbert", "DistilBERT"), ("dit", "DiT"), ("donut-swin", "DonutSwin"), ("dpr", "DPR"), ("dpt", "DPT"), ("efficientformer", "EfficientFormer"), ("efficientnet", "EfficientNet"),
("electra", "ELECTRA"), ("encodec", "EnCodec"), ("encoder-decoder", "Encoder decoder"), ("entity", "Entity"), ("ernie", "ERNIE"), ("ernie_m", "ErnieM"), ("esm", "ESM"), ("falcon", "Falcon"), ("falcon_mamba", "FalconMamba"),
("fastspeech2_conformer", "FastSpeech2Conformer"), ("flan-t5", "FLAN-T5"), ("flan-ul2", "FLAN-UL2"), ("flaubert", "FlauBERT"), ("flava", "FLAVA"), ("fnet", "FNet"), ("focalnet", "FocalNet"),
("fsmt", "FairSeq Machine-Translation"), ("funnel", "Funnel Transformer"), ("fuyu", "Fuyu"), ("gemma", "Gemma"), ("gemma2", "Gemma2"), ("git", "GIT"), ("glpn", "GLPN"), ("gpt-sw3", "GPT-Sw3"),
("gpt2", "OpenAI GPT-2"), ("gpt_bigcode", "GPTBigCode"), ("gpt_neo", "GPT Neo"), ("gpt_neox", "GPT NeoX"), ("gpt_neox_japanese", "GPT NeoX Japanese"), ("gptj", "GPT-J"), ("gptsan-japanese", "GPTSAN-japanese"),
("granite", "Granite"), ("granitemoe", "GraniteMoeMoe"), ("graphormer", "Graphormer"), ("grounding-dino", "Grounding DINO"), ("groupvit", "GroupViT"), ("herbert", "HerBERT"), ("hiera", "Hiera"),
("hubert", "Hubert"), ("hurlm", "HurLM"), ("ibert", "I-BERT"), ("idefics", "IDEFICS"), ("idefics2", "Idefics2"),
("imagegpt", "ImageGPT"), ("informer", "Informer"), ("instructblip", "InstructBLIP"), ("instructblipvideo", "InstructBlipVideo"),
("jamba", "Jamba"), ("jetmoe", "JetMoe"), ("jukebox", "Jukebox"), ("kosmos-2", "KOSMOS-2"), ("layoutlm", "LayoutLM"), ("layoutlmv2", "LayoutLMv2"), ("layoutlmv3", "LayoutLMv3"), ("layoutxlm", "LayoutXLM"),
("led", "LED"), ("levit", "LeViT"), ("lilt", "LiLT"), ("llama", "LLaMA"), ("llama2", "Llama2"), ("llama3", "Llama3"), ("llava", "LLaVa"), ("llava_next", "LLaVA-NeXT"), ("llava_next_video", "LLaVa-NeXT-Video"),
("llava_onevision", "LLaVA-Onevision"), ("longformer", "Longformer"), ("longt5", "LongT5"), ("luke", "LUKE"), ("lxmert", "LXMERT"), ("m2m_100", "M2M100"), ("madlad-400", "MADLAD-400"), ("mamba", "Mamba"),
("mamba2", "mamba2"), ("marian", "Marian"), ("markuplm", "MarkupLM"), ("mask2former", "Mask2Former"), ("maskformer", "MaskFormer"), ("maskformer-swin", "MaskFormerSwin"), ("matcha", "MatCha"),
("mbart", "mBART"), ("mbart50", "mBART-50"), ("mctct", "M-CTC-T"), ("mega", "MEGA"), ("megatron-bert", "Megatron-BERT"), ("megatron_gpt2", "Megatron-GPT2"), ("mgp-str", "MGP-STR"), ("mimi", "Mimi"),
("mistral", "Mistral"), ("mixtral", "Mixtral"), ("mllama", "Mllama"), ("mluke", "mLUKE"), ("mms", "MMS"), ("mobilebert", "MobileBERT"), ("mobilenet_v1", "MobileNetV1"), ("mobilenet_v2", "MobileNetV2"),
("mobilevit", "MobileViT"), ("mobilevitv2", "MobileViTV2"), ("modular_entity", "ModularEntity"), ("mpnet", "MPNet"), ("mpt", "MPT"), ("mra", "MRA"), ("mt5", "MT5"), ("musicgen", "MusicGen"), ("musicgen_melody", "MusicGen Melody"),
("mvp", "MVP"), ("nat", "NAT"), ("nemotron", "Nemotron"), ("nezha", "Nezha"), ("nllb", "NLLB"), ("nllb-moe", "NLLB-MOE"), ("nougat", "Nougat"), ("nystromformer", "Nyströmformer"), ("olmo", "OLMo"),
("olmoe", "OLMoE"), ("omdet-turbo", "OmDet-Turbo"), ("oneformer", "OneFormer"), ("open-llama", "OpenLlama"), ("openai-gpt", "OpenAI GPT"), ("opt", "OPT"), ("owlv2", "OWLv2"), ("owlvit", "OWL-ViT"),
("paligemma", "PaliGemma"), ("patchtsmixer", "PatchTSMixer"), ("patchtst", "PatchTST"), ("pegasus", "Pegasus"), ("pegasus_x", "PEGASUS-X"), ("perceiver", "Perceiver"), ("persimmon", "Persimmon"),
("phi", "Phi"), ("phi3", "Phi3"), ("phobert", "PhoBERT"), ("pix2struct", "Pix2Struct"), ("pixtral", "Pixtral"), ("plbart", "PLBart"), ("poolformer", "PoolFormer"), ("pop2piano", "Pop2Piano"),
("prophetnet", "ProphetNet"), ("pvt", "PVT"), ("pvt_v2", "PVTv2"), ("qdqbert", "QDQBert"), ("qwen2", "Qwen2"), ("qwen2_audio", "Qwen2Audio"), ("qwen2_audio_encoder", "Qwen2AudioEncoder"),
("qwen2_moe", "Qwen2MoE"), ("qwen2_vl", "Qwen2VL"), ("rag", "RAG"), ("realm", "REALM"), ("recurrent_gemma", "RecurrentGemma"), ("reformer", "Reformer"), ("regnet", "RegNet"), ("rembert", "RemBERT"),
("resnet", "ResNet"), ("retribert", "RetriBERT"), ("roberta", "RoBERTa"), ("roberta-prelayernorm", "RoBERTa-PreLayerNorm"), ("roc_bert", "RoCBert"), ("roformer", "RoFormer"), ("rt_detr", "RT-DETR"),
("rt_detr_resnet", "RT-DETR-ResNet"), ("rwkv", "RWKV"), ("sam", "SAM"), ("sapama", "Sapama"), ("sapi", "SAPI"), ("sapi_audio", "SAPIAudio"), ("sapi_image", "SAPIImage"),
("sapi_music", "SAPIMusic"), ("sapi_musicgen", "SAPIMusicGen"), ("sapi_video", "SAPIVideo"), ("sapi_zero", "SAPIZero"), ("sapiens", "Sapiens"),
("sapiens_code", "SapiensCode"), ("sapiens_vision", "SapiensVision"), ("sastral", "Sastral"), ("seamless_m4t", "SeamlessM4T"), ("seamless_m4t_v2", "SeamlessM4Tv2"),
("segformer", "SegFormer"), ("seggpt", "SegGPT"), ("sew", "SEW"), ("sew-d", "SEW-D"), ("siglip", "SigLIP"),
("siglip_vision_model", "SiglipVisionModel"), ("speech-encoder-decoder", "Speech Encoder decoder"), ("speech_to_text", "Speech2Text"), ("speech_to_text_2", "Speech2Text2"),
("speecht5", "SpeechT5"), ("splinter", "Splinter"), ("squeezebert", "SqueezeBERT"), ("stablelm", "StableLm"),
("starcoder2", "Starcoder2"), ("superpoint", "SuperPoint"), ("swiftformer", "SwiftFormer"), ("swin", "Swin Transformer"), ("swin2sr", "Swin2SR"),
("swinv2", "Swin Transformer V2"), ("switch_transformers", "SwitchTransformers"), ("t5", "T5"), ("t5v1.1", "T5v1.1"),
("table-transformer", "Table Transformer"), ("tapas", "TAPAS"), ("tapex", "TAPEX"), ("time_series_transformer", "Time Series Transformer"), ("timesformer", "TimeSformer"), ("timm_backbone", "TimmBackbone"),
("trajectory_transformer", "Trajectory Transformer"), ("transfo-xl", "Transformer-XL"), ("trocr", "TrOCR"), ("tvlt", "TVLT"), ("tvp", "TVP"), ("udop", "UDOP"), ("ul2", "UL2"), ("umt5", "UMT5"),
("unispeech", "UniSpeech"), ("unispeech-sat", "UniSpeechSat"), ("univnet", "UnivNet"), ("upernet", "UPerNet"), ("van", "VAN"), ("video_llava", "VideoLlava"), ("videomae", "VideoMAE"), ("vilt", "ViLT"),
("vipllava", "VipLlava"), ("vision-encoder-decoder", "Vision Encoder decoder"), ("vision-text-dual-encoder", "VisionTextDualEncoder"), ("visual_bert", "VisualBERT"), ("vit", "ViT"), ("vit_hybrid", "ViT Hybrid"),
("vit_mae", "ViTMAE"), ("vit_msn", "ViTMSN"), ("vitdet", "VitDet"), ("vitmatte", "ViTMatte"), ("vits", "VITS"), ("vivit", "ViViT"), ("wav2vec2", "Wav2Vec2"), ("wav2vec2-bert", "Wav2Vec2-BERT"),
("wav2vec2-conformer", "Wav2Vec2-Conformer"), ("wav2vec2_phoneme", "Wav2Vec2Phoneme"), ("wavlm", "WavLM"), ("whisper", "Whisper"), ("xclip", "X-CLIP"), ("xglm", "XGLM"), ("xlm", "XLM"),
("xlm-prophetnet", "XLM-ProphetNet"), ("xlm-roberta", "XLM-RoBERTa"), ("xlm-roberta-xl", "XLM-RoBERTa-XL"), ("xlm-v", "XLM-V"), ("xlnet", "XLNet"), ("xls_r", "XLS-R"), ("xlsr_wav2vec2", "XLSR-Wav2Vec2"),
("xmod", "X-MOD"), ("yolos", "YOLOS"), ("yoso", "YOSO"), ("zoedepth", "ZoeDepth")])
DEPRECATED_MODELS = ["bort", "deta", "efficientformer", "ernie_m", "gptsan_japanese", "graphormer", "jukebox", "mctct", "mega", "mmbt", "nat", "nezha", "open_llama",
"qdqbert", "realm", "retribert", "speech_to_text_2", "tapex", "trajectory_transformer", "transfo_xl", "tvlt", "van", "vit_hybrid", "xlm_prophetnet"]
SPECIAL_MODEL_TYPE_TO_MODULE_NAME = OrderedDict([("openai-gpt", "openai"), ("data2vec-audio", "data2vec"), ("data2vec-text", "data2vec"), ("data2vec-vision", "data2vec"), ("donut-swin", "donut"), ("kosmos-2", "kosmos2"),
("maskformer-swin", "maskformer"), ("xclip", "x_clip"), ("clip_vision_model", "clip"), ("qwen2_audio_encoder", "qwen2_audio"), ("clip_text_model", "clip"), ("siglip_vision_model", "siglip"),
("chinese_clip_vision_model", "chinese_clip"), ("rt_detr_resnet", "rt_detr")])
def model_type_to_module_name(key):
    if key in SPECIAL_MODEL_TYPE_TO_MODULE_NAME:
        key = SPECIAL_MODEL_TYPE_TO_MODULE_NAME[key]
        if key in DEPRECATED_MODELS: key = f"deprecated.{key}"
        return key
    key = key.replace("-", "_")
    if key in DEPRECATED_MODELS: key = f"deprecated.{key}"
    return key
def config_class_to_model_type(config):
    for key, cls in CONFIG_MAPPING_NAMES.items():
        if cls == config: return key
    for key, cls in CONFIG_MAPPING._extra_content.items():
        if cls.__name__ == config: return key
    return None
class _LazyConfigMapping(OrderedDict):
    def __init__(self, mapping):
        self._mapping = mapping
        self._extra_content = {}
        self._modules = {}
    def __getitem__(self, key):
        if key in self._extra_content: return self._extra_content[key]
        if key not in self._mapping: raise KeyError(key)
        value = self._mapping[key]
        module_name = model_type_to_module_name(key)
        if module_name not in self._modules: self._modules[module_name] = importlib.import_module(f".{module_name}", "sapiens_transformers.models")
        if hasattr(self._modules[module_name], value): return getattr(self._modules[module_name], value)
        transformers_module = importlib.import_module("sapiens_transformers")
        return getattr(transformers_module, value)
    def keys(self): return list(self._mapping.keys()) + list(self._extra_content.keys())
    def values(self): return [self[k] for k in self._mapping.keys()] + list(self._extra_content.values())
    def items(self): return [(k, self[k]) for k in self._mapping.keys()] + list(self._extra_content.items())
    def __iter__(self): return iter(list(self._mapping.keys()) + list(self._extra_content.keys()))
    def __contains__(self, item): return item in self._mapping or item in self._extra_content
    def register(self, key, value, exist_ok=False):
        if key in self._mapping.keys() and not exist_ok: raise ValueError(f"'{key}' is already used by a Transformers config, pick another name.")
        self._extra_content[key] = value
CONFIG_MAPPING = _LazyConfigMapping(CONFIG_MAPPING_NAMES)
class _LazyLoadAllMappings(OrderedDict):
    def __init__(self, mapping):
        self._mapping = mapping
        self._initialized = False
        self._data = {}
    def _initialize(self):
        if self._initialized: return
        for model_type, map_name in self._mapping.items():
            module_name = model_type_to_module_name(model_type)
            module = importlib.import_module(f".{module_name}", "sapiens_transformers.models")
            mapping = getattr(module, map_name)
            self._data.update(mapping)
        self._initialized = True
    def __getitem__(self, key):
        self._initialize()
        return self._data[key]
    def keys(self):
        self._initialize()
        return self._data.keys()
    def values(self):
        self._initialize()
        return self._data.values()
    def items(self):
        self._initialize()
        return self._data.keys()
    def __iter__(self):
        self._initialize()
        return iter(self._data)
    def __contains__(self, item):
        self._initialize()
        return item in self._data
def _get_class_name(model_class: Union[str, List[str]]):
    if isinstance(model_class, (list, tuple)): return " or ".join([f"[`{c}`]" for c in model_class if c is not None])
    return f"[`{model_class}`]"
def _list_model_options(indent, config_to_class=None, use_model_types=True):
    if config_to_class is None and not use_model_types: raise ValueError("Using `use_model_types=False` requires a `config_to_class` dictionary.")
    if use_model_types:
        if config_to_class is None: model_type_to_name = {model_type: f"[`{config}`]" for model_type, config in CONFIG_MAPPING_NAMES.items()}
        else: model_type_to_name = {model_type: _get_class_name(model_class) for model_type, model_class in config_to_class.items() if model_type in MODEL_NAMES_MAPPING}
        lines = [f"{indent}- **{model_type}** -- {model_type_to_name[model_type]} ({MODEL_NAMES_MAPPING[model_type]} model)" for model_type in sorted(model_type_to_name.keys())]
    else:
        config_to_name = {CONFIG_MAPPING_NAMES[config]: _get_class_name(clas) for config, clas in config_to_class.items() if config in CONFIG_MAPPING_NAMES}
        config_to_model_name = {config: MODEL_NAMES_MAPPING[model_type] for model_type, config in CONFIG_MAPPING_NAMES.items()}
        lines = [f"{indent}- [`{config_name}`] configuration class: {config_to_name[config_name]} ({config_to_model_name[config_name]} model)" for config_name in sorted(config_to_name.keys())]
    return "\n".join(lines)
def replace_list_option_in_docstrings(config_to_class=None, use_model_types=True):
    def docstring_decorator(fn):
        docstrings = fn.__doc__
        if docstrings is None: return fn
        lines = docstrings.split("\n")
        i = 0
        while i < len(lines) and re.search(r"^(\s*)List options\s*$", lines[i]) is None: i += 1
        if i < len(lines):
            indent = re.search(r"^(\s*)List options\s*$", lines[i]).groups()[0]
            if use_model_types: indent = f"{indent}    "
            lines[i] = _list_model_options(indent, config_to_class=config_to_class, use_model_types=use_model_types)
            docstrings = "\n".join(lines)
        else: raise ValueError(f"The function {fn} should have an empty 'List options' in its docstring as placeholder, current docstring is:\n{docstrings}")
        fn.__doc__ = docstrings
        return fn
    return docstring_decorator
class AutoConfig:
    def __init__(self): raise EnvironmentError("AutoConfig is designed to be instantiated using the `AutoConfig.from_pretrained(pretrained_model_name_or_path)` method.")
    @classmethod
    def for_model(cls, model_type: str, *args, **kwargs):
        if model_type in CONFIG_MAPPING:
            config_class = CONFIG_MAPPING[model_type]
            return config_class(*args, **kwargs)
        raise ValueError(f"Unrecognized model identifier: {model_type}. Should contain one of {', '.join(CONFIG_MAPPING.keys())}")
    @classmethod
    @replace_list_option_in_docstrings()
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn("The `use_auth_token` argument is deprecated and will be removed in v1 of Sapiens Transformers. Please use `token` instead.", FutureWarning)
            if kwargs.get("token", None) is not None: raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
            kwargs["token"] = use_auth_token
        kwargs["_from_auto"] = True
        kwargs["name_or_path"] = pretrained_model_name_or_path
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        code_revision = kwargs.pop("code_revision", None)
        config_dict, unused_kwargs = PretrainedConfig.get_config_dict(pretrained_model_name_or_path, **kwargs)
        has_remote_code = "auto_map" in config_dict and "AutoConfig" in config_dict["auto_map"]
        has_local_code = "model_type" in config_dict and config_dict["model_type"] in CONFIG_MAPPING
        trust_remote_code = resolve_trust_remote_code(trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code)
        if has_remote_code and trust_remote_code:
            class_ref = config_dict["auto_map"]["AutoConfig"]
            config_class = get_class_from_dynamic_module(class_ref, pretrained_model_name_or_path, code_revision=code_revision, **kwargs)
            if os.path.isdir(pretrained_model_name_or_path): config_class.register_for_auto_class()
            return config_class.from_pretrained(pretrained_model_name_or_path, **kwargs)
        elif "model_type" in config_dict:
            try: config_class = CONFIG_MAPPING[config_dict["model_type"]]
            except KeyError: raise ValueError(f"The checkpoint you are trying to load has model type `{config_dict['model_type']}` but Transformers does not recognize this architecture. This could be because of an issue with the checkpoint, or because your version of Transformers is out of date.")
            return config_class.from_dict(config_dict, **unused_kwargs)
        else:
            for pattern in sorted(CONFIG_MAPPING.keys(), key=len, reverse=True):
                if pattern in str(pretrained_model_name_or_path): return CONFIG_MAPPING[pattern].from_dict(config_dict, **unused_kwargs)
        raise ValueError(f"Unrecognized model in {pretrained_model_name_or_path}. Should have a `model_type` key in its {CONFIG_NAME}, or contain one of the following strings in its name: {', '.join(CONFIG_MAPPING.keys())}")
    @staticmethod
    def register(model_type, config, exist_ok=False):
        if issubclass(config, PretrainedConfig) and config.model_type != model_type: raise ValueError(f"The config you are passing has a `model_type` attribute that is not consistent with the model type you passed (config has {config.model_type} and you passed {model_type}. Fix one of those so they match!")
        CONFIG_MAPPING.register(model_type, config, exist_ok=exist_ok)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
