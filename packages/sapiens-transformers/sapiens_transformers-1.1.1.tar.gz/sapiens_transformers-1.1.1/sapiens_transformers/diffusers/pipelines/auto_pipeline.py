'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from collections import OrderedDict
from huggingface_hub.utils import validate_hf_hub_args
from ..configuration_utils import ConfigMixin
from ..models.controlnets import ControlNetUnionModel
from ..utils import is_sentencepiece_available
from .aura_flow import AuraFlowPipeline
from .cogview3 import CogView3PlusPipeline
from .controlnet import (StableDiffusionControlNetImg2ImgPipeline, StableDiffusionControlNetInpaintPipeline, StableDiffusionControlNetPipeline, StableDiffusionXLControlNetImg2ImgPipeline,
StableDiffusionXLControlNetInpaintPipeline, StableDiffusionXLControlNetPipeline, StableDiffusionXLControlNetUnionImg2ImgPipeline,
StableDiffusionXLControlNetUnionInpaintPipeline, StableDiffusionXLControlNetUnionPipeline)
from .deepfloyd_if import IFImg2ImgPipeline, IFInpaintingPipeline, IFPipeline
from .flux import (FluxControlImg2ImgPipeline, FluxControlInpaintPipeline, FluxControlNetImg2ImgPipeline, FluxControlNetInpaintPipeline, FluxControlNetPipeline,
FluxControlPipeline, FluxImg2ImgPipeline, FluxInpaintPipeline, FluxPipeline)
from .hunyuandit import HunyuanDiTPipeline
from .kandinsky import KandinskyCombinedPipeline, KandinskyImg2ImgCombinedPipeline, KandinskyImg2ImgPipeline, KandinskyInpaintCombinedPipeline, KandinskyInpaintPipeline, KandinskyPipeline
from .kandinsky2_2 import (KandinskyV22CombinedPipeline, KandinskyV22Img2ImgCombinedPipeline, KandinskyV22Img2ImgPipeline, KandinskyV22InpaintCombinedPipeline,
KandinskyV22InpaintPipeline, KandinskyV22Pipeline)
from .kandinsky3 import Kandinsky3Img2ImgPipeline, Kandinsky3Pipeline
from .latent_consistency_models import LatentConsistencyModelImg2ImgPipeline, LatentConsistencyModelPipeline
from .lumina import LuminaText2ImgPipeline
from .pag import (HunyuanDiTPAGPipeline, PixArtSigmaPAGPipeline, SAPIImageGenPAGImg2ImgPipeline, SAPIImageGenPAGPipeline, StableDiffusion3PAGImg2ImgPipeline, StableDiffusion3PAGPipeline,
StableDiffusionControlNetPAGInpaintPipeline, StableDiffusionControlNetPAGPipeline, StableDiffusionPAGImg2ImgPipeline, StableDiffusionPAGInpaintPipeline, StableDiffusionPAGPipeline,
StableDiffusionXLControlNetPAGImg2ImgPipeline, StableDiffusionXLControlNetPAGPipeline, StableDiffusionXLPAGImg2ImgPipeline, StableDiffusionXLPAGInpaintPipeline, StableDiffusionXLPAGPipeline)
from .pixart_alpha import PixArtAlphaPipeline, PixArtSigmaPipeline
from .sapi_imagegen import SAPIImageGenImg2ImgPipeline, SAPIImageGenInpaintPipeline, SAPIImageGenPipeline
from .sapi_photogen import (SAPIPhotoGenControlImg2ImgPipeline, SAPIPhotoGenControlInpaintPipeline, SAPIPhotoGenControlNetImg2ImgPipeline, SAPIPhotoGenControlNetInpaintPipeline, SAPIPhotoGenControlNetPipeline,
SAPIPhotoGenControlPipeline, SAPIPhotoGenImg2ImgPipeline, SAPIPhotoGenInpaintPipeline, SAPIPhotoGenPipeline)
from .stable_cascade import StableCascadeCombinedPipeline, StableCascadeDecoderPipeline
from .stable_diffusion import StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline, StableDiffusionPipeline
from .stable_diffusion_3 import StableDiffusion3Img2ImgPipeline, StableDiffusion3InpaintPipeline, StableDiffusion3Pipeline
from .stable_diffusion_xl import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLInpaintPipeline, StableDiffusionXLPipeline
from .wuerstchen import WuerstchenCombinedPipeline, WuerstchenDecoderPipeline
AUTO_TEXT2IMAGE_PIPELINES_MAPPING = OrderedDict([('stable-diffusion', StableDiffusionPipeline), ('stable-diffusion-xl', StableDiffusionXLPipeline), ('stable-diffusion-3', StableDiffusion3Pipeline),
('sapi-imagegen', SAPIImageGenPipeline), ('sapi-imagegen-pag', SAPIImageGenPAGPipeline), ('stable-diffusion-3-pag', StableDiffusion3PAGPipeline), ('if', IFPipeline), ('hunyuan', HunyuanDiTPipeline),
('hunyuan-pag', HunyuanDiTPAGPipeline), ('kandinsky', KandinskyCombinedPipeline), ('kandinsky22', KandinskyV22CombinedPipeline), ('kandinsky3', Kandinsky3Pipeline), ('stable-diffusion-controlnet', StableDiffusionControlNetPipeline),
('stable-diffusion-xl-controlnet', StableDiffusionXLControlNetPipeline), ('stable-diffusion-xl-controlnet-union', StableDiffusionXLControlNetUnionPipeline), ('wuerstchen', WuerstchenCombinedPipeline),
('cascade', StableCascadeCombinedPipeline), ('lcm', LatentConsistencyModelPipeline), ('pixart-alpha', PixArtAlphaPipeline), ('pixart-sigma', PixArtSigmaPipeline),
('stable-diffusion-pag', StableDiffusionPAGPipeline), ('stable-diffusion-controlnet-pag', StableDiffusionControlNetPAGPipeline),
('sapi_photogen', SAPIPhotoGenPipeline), ('sapi_photogen-control', SAPIPhotoGenControlPipeline), ('sapi_photogen-controlnet', SAPIPhotoGenControlNetPipeline), ('stable-diffusion-xl-pag', StableDiffusionXLPAGPipeline),
('stable-diffusion-xl-controlnet-pag', StableDiffusionXLControlNetPAGPipeline), ('pixart-sigma-pag', PixArtSigmaPAGPipeline), ('auraflow', AuraFlowPipeline), ('flux', FluxPipeline),
('flux-control', FluxControlPipeline), ('flux-controlnet', FluxControlNetPipeline), ('lumina', LuminaText2ImgPipeline), ('cogview3', CogView3PlusPipeline)])
AUTO_IMAGE2IMAGE_PIPELINES_MAPPING = OrderedDict([('sapi-imagegen', SAPIImageGenImg2ImgPipeline), ('sapi-imagegen-pag', SAPIImageGenPAGImg2ImgPipeline), ('stable-diffusion', StableDiffusionImg2ImgPipeline),
('stable-diffusion-xl', StableDiffusionXLImg2ImgPipeline), ('stable-diffusion-3', StableDiffusion3Img2ImgPipeline), ('stable-diffusion-3-pag', StableDiffusion3PAGImg2ImgPipeline), ('if', IFImg2ImgPipeline),
('kandinsky', KandinskyImg2ImgCombinedPipeline), ('kandinsky22', KandinskyV22Img2ImgCombinedPipeline), ('kandinsky3', Kandinsky3Img2ImgPipeline), ('stable-diffusion-controlnet', StableDiffusionControlNetImg2ImgPipeline),
('sapi_photogen', SAPIPhotoGenImg2ImgPipeline), ('sapi_photogen-controlnet', SAPIPhotoGenControlNetImg2ImgPipeline), ('sapi_photogen-control', SAPIPhotoGenControlImg2ImgPipeline),
('stable-diffusion-pag', StableDiffusionPAGImg2ImgPipeline), ('stable-diffusion-xl-controlnet', StableDiffusionXLControlNetImg2ImgPipeline),
('stable-diffusion-xl-controlnet-union', StableDiffusionXLControlNetUnionImg2ImgPipeline), ('stable-diffusion-xl-pag', StableDiffusionXLPAGImg2ImgPipeline),
('stable-diffusion-xl-controlnet-pag', StableDiffusionXLControlNetPAGImg2ImgPipeline), ('lcm', LatentConsistencyModelImg2ImgPipeline), ('flux', FluxImg2ImgPipeline),
('flux-controlnet', FluxControlNetImg2ImgPipeline), ('flux-control', FluxControlImg2ImgPipeline)])
AUTO_INPAINT_PIPELINES_MAPPING = OrderedDict([('sapi-imagegen', SAPIImageGenInpaintPipeline), ('sapi_photogen', SAPIPhotoGenInpaintPipeline), ('sapi_photogen-controlnet', SAPIPhotoGenControlNetInpaintPipeline),
('sapi_photogen-control', SAPIPhotoGenControlInpaintPipeline), ('stable-diffusion', StableDiffusionInpaintPipeline), ('stable-diffusion-xl', StableDiffusionXLInpaintPipeline),
('stable-diffusion-3', StableDiffusion3InpaintPipeline), ('if', IFInpaintingPipeline), ('kandinsky', KandinskyInpaintCombinedPipeline), ('kandinsky22', KandinskyV22InpaintCombinedPipeline),
('stable-diffusion-controlnet', StableDiffusionControlNetInpaintPipeline), ('stable-diffusion-controlnet-pag', StableDiffusionControlNetPAGInpaintPipeline),
('stable-diffusion-xl-controlnet', StableDiffusionXLControlNetInpaintPipeline), ('stable-diffusion-xl-controlnet-union', StableDiffusionXLControlNetUnionInpaintPipeline),
('stable-diffusion-xl-pag', StableDiffusionXLPAGInpaintPipeline), ('flux', FluxInpaintPipeline), ('flux-controlnet', FluxControlNetInpaintPipeline), ('flux-control', FluxControlInpaintPipeline),
('stable-diffusion-pag', StableDiffusionPAGInpaintPipeline)])
_AUTO_TEXT2IMAGE_DECODER_PIPELINES_MAPPING = OrderedDict([('kandinsky', KandinskyPipeline), ('kandinsky22', KandinskyV22Pipeline),
('wuerstchen', WuerstchenDecoderPipeline), ('cascade', StableCascadeDecoderPipeline)])
_AUTO_IMAGE2IMAGE_DECODER_PIPELINES_MAPPING = OrderedDict([('kandinsky', KandinskyImg2ImgPipeline), ('kandinsky22', KandinskyV22Img2ImgPipeline)])
_AUTO_INPAINT_DECODER_PIPELINES_MAPPING = OrderedDict([('kandinsky', KandinskyInpaintPipeline), ('kandinsky22', KandinskyV22InpaintPipeline)])
if is_sentencepiece_available():
    from .kolors import KolorsImg2ImgPipeline, KolorsPipeline
    from .pag import KolorsPAGPipeline
    AUTO_TEXT2IMAGE_PIPELINES_MAPPING['kolors'] = KolorsPipeline
    AUTO_TEXT2IMAGE_PIPELINES_MAPPING['kolors-pag'] = KolorsPAGPipeline
    AUTO_IMAGE2IMAGE_PIPELINES_MAPPING['kolors'] = KolorsImg2ImgPipeline
SUPPORTED_TASKS_MAPPINGS = [AUTO_TEXT2IMAGE_PIPELINES_MAPPING, AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, AUTO_INPAINT_PIPELINES_MAPPING, _AUTO_TEXT2IMAGE_DECODER_PIPELINES_MAPPING,
_AUTO_IMAGE2IMAGE_DECODER_PIPELINES_MAPPING, _AUTO_INPAINT_DECODER_PIPELINES_MAPPING]
def _get_connected_pipeline(pipeline_cls):
    if pipeline_cls in _AUTO_TEXT2IMAGE_DECODER_PIPELINES_MAPPING.values(): return _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, pipeline_cls.__name__, throw_error_if_not_exist=False)
    if pipeline_cls in _AUTO_IMAGE2IMAGE_DECODER_PIPELINES_MAPPING.values(): return _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, pipeline_cls.__name__, throw_error_if_not_exist=False)
    if pipeline_cls in _AUTO_INPAINT_DECODER_PIPELINES_MAPPING.values(): return _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, pipeline_cls.__name__, throw_error_if_not_exist=False)
def _get_task_class(mapping, pipeline_class_name, throw_error_if_not_exist: bool=True):
    def get_model(pipeline_class_name):
        for task_mapping in SUPPORTED_TASKS_MAPPINGS:
            for model_name, pipeline in task_mapping.items():
                if pipeline.__name__ == pipeline_class_name: return model_name
    model_name = get_model(pipeline_class_name)
    if model_name is not None:
        task_class = mapping.get(model_name, None)
        if task_class is not None: return task_class
    if throw_error_if_not_exist: raise ValueError(f"AutoPipeline can't find a pipeline linked to {pipeline_class_name} for {model_name}")
class AutoPipelineForText2Image(ConfigMixin):
    config_name = 'model_index.json'
    def __init__(self, *args, **kwargs): raise EnvironmentError(f'{self.__class__.__name__} is designed to be instantiated using the `{self.__class__.__name__}.from_pretrained(pretrained_model_name_or_path)` or `{self.__class__.__name__}.from_pipe(pipeline)` methods.')
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_or_path, **kwargs):
        """Examples:"""
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        local_files_only = kwargs.pop('local_files_only', False)
        revision = kwargs.pop('revision', None)
        load_config_kwargs = {'cache_dir': cache_dir, 'force_download': force_download, 'proxies': proxies, 'token': token, 'local_files_only': local_files_only, 'revision': revision}
        config = cls.load_config(pretrained_model_or_path, **load_config_kwargs)
        orig_class_name = config['_class_name']
        if 'ControlPipeline' in orig_class_name: to_replace = 'ControlPipeline'
        else: to_replace = 'Pipeline'
        if 'controlnet' in kwargs:
            if isinstance(kwargs['controlnet'], ControlNetUnionModel): orig_class_name = config['_class_name'].replace(to_replace, 'ControlNetUnionPipeline')
            else: orig_class_name = config['_class_name'].replace(to_replace, 'ControlNetPipeline')
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: orig_class_name = orig_class_name.replace(to_replace, 'PAGPipeline')
        text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, orig_class_name)
        kwargs = {**load_config_kwargs, **kwargs}
        return text_2_image_cls.from_pretrained(pretrained_model_or_path, **kwargs)
    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        original_config = dict(pipeline.config)
        original_cls_name = pipeline.__class__.__name__
        text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, original_cls_name)
        if 'controlnet' in kwargs:
            if kwargs['controlnet'] is not None:
                to_replace = 'PAGPipeline' if 'PAG' in text_2_image_cls.__name__ else 'Pipeline'
                text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, text_2_image_cls.__name__.replace('ControlNet', '').replace(to_replace, 'ControlNet' + to_replace))
            else: text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, text_2_image_cls.__name__.replace('ControlNet', ''))
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, text_2_image_cls.__name__.replace('PAG', '').replace('Pipeline', 'PAGPipeline'))
            else: text_2_image_cls = _get_task_class(AUTO_TEXT2IMAGE_PIPELINES_MAPPING, text_2_image_cls.__name__.replace('PAG', ''))
        expected_modules, optional_kwargs = text_2_image_cls._get_signature_keys(text_2_image_cls)
        pretrained_model_name_or_path = original_config.pop('_name_or_path', None)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        original_class_obj = {k: pipeline.components[k] for k, v in pipeline.components.items() if k in expected_modules and k not in passed_class_obj}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        original_pipe_kwargs = {k: original_config[k] for k, v in original_config.items() if k in optional_kwargs and k not in passed_pipe_kwargs}
        additional_pipe_kwargs = [k[1:] for k in original_config.keys() if k.startswith('_') and k[1:] in optional_kwargs and (k[1:] not in passed_pipe_kwargs)]
        for k in additional_pipe_kwargs: original_pipe_kwargs[k] = original_config.pop(f'_{k}')
        text_2_image_kwargs = {**passed_class_obj, **original_class_obj, **passed_pipe_kwargs, **original_pipe_kwargs}
        unused_original_config = {f"{('' if k.startswith('_') else '_')}{k}": original_config[k] for k, v in original_config.items() if k not in text_2_image_kwargs}
        missing_modules = set(expected_modules) - set(pipeline._optional_components) - set(text_2_image_kwargs.keys())
        if len(missing_modules) > 0: raise ValueError(f'Pipeline {text_2_image_cls} expected {expected_modules}, but only {set(list(passed_class_obj.keys()) + list(original_class_obj.keys()))} were passed')
        model = text_2_image_cls(**text_2_image_kwargs)
        model.register_to_config(_name_or_path=pretrained_model_name_or_path)
        model.register_to_config(**unused_original_config)
        return model
class AutoPipelineForImage2Image(ConfigMixin):
    config_name = 'model_index.json'
    def __init__(self, *args, **kwargs): raise EnvironmentError(f'{self.__class__.__name__} is designed to be instantiated using the `{self.__class__.__name__}.from_pretrained(pretrained_model_name_or_path)` or `{self.__class__.__name__}.from_pipe(pipeline)` methods.')
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_or_path, **kwargs):
        """Examples:"""
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        local_files_only = kwargs.pop('local_files_only', False)
        revision = kwargs.pop('revision', None)
        load_config_kwargs = {'cache_dir': cache_dir, 'force_download': force_download, 'proxies': proxies, 'token': token, 'local_files_only': local_files_only, 'revision': revision}
        config = cls.load_config(pretrained_model_or_path, **load_config_kwargs)
        orig_class_name = config['_class_name']
        if 'Img2Img' in orig_class_name: to_replace = 'Img2ImgPipeline'
        elif 'ControlPipeline' in orig_class_name: to_replace = 'ControlPipeline'
        else: to_replace = 'Pipeline'
        if 'controlnet' in kwargs:
            if isinstance(kwargs['controlnet'], ControlNetUnionModel): orig_class_name = orig_class_name.replace(to_replace, 'ControlNetUnion' + to_replace)
            else: orig_class_name = orig_class_name.replace(to_replace, 'ControlNet' + to_replace)
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: orig_class_name = orig_class_name.replace(to_replace, 'PAG' + to_replace)
        if to_replace == 'ControlPipeline': orig_class_name = orig_class_name.replace(to_replace, 'ControlImg2ImgPipeline')
        image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, orig_class_name)
        kwargs = {**load_config_kwargs, **kwargs}
        return image_2_image_cls.from_pretrained(pretrained_model_or_path, **kwargs)
    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        """Examples:"""
        original_config = dict(pipeline.config)
        original_cls_name = pipeline.__class__.__name__
        image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, original_cls_name)
        if 'controlnet' in kwargs:
            if kwargs['controlnet'] is not None:
                to_replace = 'Img2ImgPipeline'
                if 'PAG' in image_2_image_cls.__name__: to_replace = 'PAG' + to_replace
                image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, image_2_image_cls.__name__.replace('ControlNet', '').replace(to_replace, 'ControlNet' + to_replace))
            else: image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, image_2_image_cls.__name__.replace('ControlNet', ''))
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, image_2_image_cls.__name__.replace('PAG', '').replace('Img2ImgPipeline', 'PAGImg2ImgPipeline'))
            else: image_2_image_cls = _get_task_class(AUTO_IMAGE2IMAGE_PIPELINES_MAPPING, image_2_image_cls.__name__.replace('PAG', ''))
        expected_modules, optional_kwargs = image_2_image_cls._get_signature_keys(image_2_image_cls)
        pretrained_model_name_or_path = original_config.pop('_name_or_path', None)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        original_class_obj = {k: pipeline.components[k] for k, v in pipeline.components.items() if k in expected_modules and k not in passed_class_obj}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        original_pipe_kwargs = {k: original_config[k] for k, v in original_config.items() if k in optional_kwargs and k not in passed_pipe_kwargs}
        additional_pipe_kwargs = [k[1:] for k in original_config.keys() if k.startswith('_') and k[1:] in optional_kwargs and (k[1:] not in passed_pipe_kwargs)]
        for k in additional_pipe_kwargs: original_pipe_kwargs[k] = original_config.pop(f'_{k}')
        image_2_image_kwargs = {**passed_class_obj, **original_class_obj, **passed_pipe_kwargs, **original_pipe_kwargs}
        unused_original_config = {f"{('' if k.startswith('_') else '_')}{k}": original_config[k] for k, v in original_config.items() if k not in image_2_image_kwargs}
        missing_modules = set(expected_modules) - set(pipeline._optional_components) - set(image_2_image_kwargs.keys())
        if len(missing_modules) > 0: raise ValueError(f'Pipeline {image_2_image_cls} expected {expected_modules}, but only {set(list(passed_class_obj.keys()) + list(original_class_obj.keys()))} were passed')
        model = image_2_image_cls(**image_2_image_kwargs)
        model.register_to_config(_name_or_path=pretrained_model_name_or_path)
        model.register_to_config(**unused_original_config)
        return model
class AutoPipelineForInpainting(ConfigMixin):
    config_name = 'model_index.json'
    def __init__(self, *args, **kwargs): raise EnvironmentError(f'{self.__class__.__name__} is designed to be instantiated using the `{self.__class__.__name__}.from_pretrained(pretrained_model_name_or_path)` or `{self.__class__.__name__}.from_pipe(pipeline)` methods.')
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_or_path, **kwargs):
        """Examples:"""
        cache_dir = kwargs.pop('cache_dir', None)
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        local_files_only = kwargs.pop('local_files_only', False)
        revision = kwargs.pop('revision', None)
        load_config_kwargs = {'cache_dir': cache_dir, 'force_download': force_download, 'proxies': proxies, 'token': token, 'local_files_only': local_files_only, 'revision': revision}
        config = cls.load_config(pretrained_model_or_path, **load_config_kwargs)
        orig_class_name = config['_class_name']
        if 'Inpaint' in orig_class_name: to_replace = 'InpaintPipeline'
        elif 'ControlPipeline' in orig_class_name: to_replace = 'ControlPipeline'
        else: to_replace = 'Pipeline'
        if 'controlnet' in kwargs:
            if isinstance(kwargs['controlnet'], ControlNetUnionModel): orig_class_name = orig_class_name.replace(to_replace, 'ControlNetUnion' + to_replace)
            else: orig_class_name = orig_class_name.replace(to_replace, 'ControlNet' + to_replace)
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: orig_class_name = orig_class_name.replace(to_replace, 'PAG' + to_replace)
        if to_replace == 'ControlPipeline': orig_class_name = orig_class_name.replace(to_replace, 'ControlInpaintPipeline')
        inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, orig_class_name)
        kwargs = {**load_config_kwargs, **kwargs}
        return inpainting_cls.from_pretrained(pretrained_model_or_path, **kwargs)
    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        """Examples:"""
        original_config = dict(pipeline.config)
        original_cls_name = pipeline.__class__.__name__
        inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, original_cls_name)
        if 'controlnet' in kwargs:
            if kwargs['controlnet'] is not None: inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, inpainting_cls.__name__.replace('ControlNet', '').replace('InpaintPipeline', 'ControlNetInpaintPipeline'))
            else: inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, inpainting_cls.__name__.replace('ControlNetInpaintPipeline', 'InpaintPipeline'))
        if 'enable_pag' in kwargs:
            enable_pag = kwargs.pop('enable_pag')
            if enable_pag: inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, inpainting_cls.__name__.replace('PAG', '').replace('InpaintPipeline', 'PAGInpaintPipeline'))
            else: inpainting_cls = _get_task_class(AUTO_INPAINT_PIPELINES_MAPPING, inpainting_cls.__name__.replace('PAGInpaintPipeline', 'InpaintPipeline'))
        expected_modules, optional_kwargs = inpainting_cls._get_signature_keys(inpainting_cls)
        pretrained_model_name_or_path = original_config.pop('_name_or_path', None)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        original_class_obj = {k: pipeline.components[k] for k, v in pipeline.components.items() if k in expected_modules and k not in passed_class_obj}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        original_pipe_kwargs = {k: original_config[k] for k, v in original_config.items() if k in optional_kwargs and k not in passed_pipe_kwargs}
        additional_pipe_kwargs = [k[1:] for k in original_config.keys() if k.startswith('_') and k[1:] in optional_kwargs and (k[1:] not in passed_pipe_kwargs)]
        for k in additional_pipe_kwargs: original_pipe_kwargs[k] = original_config.pop(f'_{k}')
        inpainting_kwargs = {**passed_class_obj, **original_class_obj, **passed_pipe_kwargs, **original_pipe_kwargs}
        unused_original_config = {f"{('' if k.startswith('_') else '_')}{k}": original_config[k] for k, v in original_config.items() if k not in inpainting_kwargs}
        missing_modules = set(expected_modules) - set(pipeline._optional_components) - set(inpainting_kwargs.keys())
        if len(missing_modules) > 0: raise ValueError(f'Pipeline {inpainting_cls} expected {expected_modules}, but only {set(list(passed_class_obj.keys()) + list(original_class_obj.keys()))} were passed')
        model = inpainting_cls(**inpainting_kwargs)
        model.register_to_config(_name_or_path=pretrained_model_name_or_path)
        model.register_to_config(**unused_original_config)
        return model
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
