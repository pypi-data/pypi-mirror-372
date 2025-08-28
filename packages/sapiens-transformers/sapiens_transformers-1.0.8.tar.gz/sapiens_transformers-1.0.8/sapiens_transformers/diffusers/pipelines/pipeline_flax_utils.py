'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import importlib
import inspect
import os
from typing import Any, Dict, List, Optional, Union
import flax
import numpy as np
import PIL.Image
from flax.core.frozen_dict import FrozenDict
from huggingface_hub import create_repo, snapshot_download
from huggingface_hub.utils import validate_hf_hub_args
from PIL import Image
from tqdm.auto import tqdm
from ..configuration_utils import ConfigMixin
from ..models.modeling_flax_utils import FLAX_WEIGHTS_NAME, FlaxModelMixin
from ..schedulers.scheduling_utils_flax import SCHEDULER_CONFIG_NAME, FlaxSchedulerMixin
from ..utils import CONFIG_NAME, BaseOutput, PushToHubMixin, http_user_agent, is_transformers_available
if is_transformers_available(): from sapiens_transformers import FlaxPreTrainedModel
INDEX_FILE = 'diffusion_flax_model.bin'
LOADABLE_CLASSES = {'sapiens_transformers.diffusers': {'FlaxModelMixin': ['save_pretrained', 'from_pretrained'], 'FlaxSchedulerMixin': ['save_pretrained', 'from_pretrained'],
'FlaxDiffusionPipeline': ['save_pretrained', 'from_pretrained']}, 'sapiens_transformers': {'PreTrainedTokenizer': ['save_pretrained', 'from_pretrained'],
'PreTrainedTokenizerFast': ['save_pretrained', 'from_pretrained'], 'FlaxPreTrainedModel': ['save_pretrained', 'from_pretrained'],
'FeatureExtractionMixin': ['save_pretrained', 'from_pretrained'], 'ProcessorMixin': ['save_pretrained', 'from_pretrained'],
'ImageProcessingMixin': ['save_pretrained', 'from_pretrained']}}
ALL_IMPORTABLE_CLASSES = {}
for library in LOADABLE_CLASSES: ALL_IMPORTABLE_CLASSES.update(LOADABLE_CLASSES[library])
def import_flax_or_no_model(module, class_name):
    try: class_obj = getattr(module, 'Flax' + class_name)
    except AttributeError: class_obj = getattr(module, class_name)
    except AttributeError: raise ValueError(f'Neither Flax{class_name} nor {class_name} exist in {module}')
    return class_obj
@flax.struct.dataclass
class FlaxImagePipelineOutput(BaseOutput):
    """Args:"""
    images: Union[List[PIL.Image.Image], np.ndarray]
class FlaxDiffusionPipeline(ConfigMixin, PushToHubMixin):
    config_name = 'model_index.json'
    def register_modules(self, **kwargs):
        from .. import pipelines
        for name, module in kwargs.items():
            if module is None: register_dict = {name: (None, None)}
            else:
                library = module.__module__.split('.')[0]
                pipeline_dir = module.__module__.split('.')[-2]
                path = module.__module__.split('.')
                is_pipeline_module = pipeline_dir in path and hasattr(pipelines, pipeline_dir)
                if library not in LOADABLE_CLASSES or is_pipeline_module: library = pipeline_dir
                class_name = module.__class__.__name__
                register_dict = {name: (library, class_name)}
            self.register_to_config(**register_dict)
            setattr(self, name, module)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], params: Union[Dict, FrozenDict], push_to_hub: bool=False, **kwargs):
        self.save_config(save_directory)
        model_index_dict = dict(self.config)
        model_index_dict.pop('_class_name')
        model_index_dict.pop('_diffusers_version')
        model_index_dict.pop('_module', None)
        if push_to_hub:
            commit_message = kwargs.pop('commit_message', None)
            private = kwargs.pop('private', None)
            create_pr = kwargs.pop('create_pr', False)
            token = kwargs.pop('token', None)
            repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
            repo_id = create_repo(repo_id, exist_ok=True, private=private, token=token).repo_id
        for pipeline_component_name in model_index_dict.keys():
            sub_model = getattr(self, pipeline_component_name)
            if sub_model is None: continue
            model_cls = sub_model.__class__
            save_method_name = None
            for library_name, library_classes in LOADABLE_CLASSES.items():
                library = importlib.import_module(library_name)
                for base_class, save_load_methods in library_classes.items():
                    class_candidate = getattr(library, base_class, None)
                    if class_candidate is not None and issubclass(model_cls, class_candidate):
                        save_method_name = save_load_methods[0]
                        break
                if save_method_name is not None: break
            save_method = getattr(sub_model, save_method_name)
            expects_params = 'params' in set(inspect.signature(save_method).parameters.keys())
            if expects_params: save_method(os.path.join(save_directory, pipeline_component_name), params=params[pipeline_component_name])
            else: save_method(os.path.join(save_directory, pipeline_component_name))
            if push_to_hub: self._upload_folder(save_directory, repo_id, token=token, commit_message=commit_message, create_pr=create_pr)
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], **kwargs):
        """Examples:"""
        cache_dir = kwargs.pop('cache_dir', None)
        proxies = kwargs.pop('proxies', None)
        local_files_only = kwargs.pop('local_files_only', False)
        token = kwargs.pop('token', None)
        revision = kwargs.pop('revision', None)
        from_pt = kwargs.pop('from_pt', False)
        use_memory_efficient_attention = kwargs.pop('use_memory_efficient_attention', False)
        split_head_dim = kwargs.pop('split_head_dim', False)
        dtype = kwargs.pop('dtype', None)
        if not os.path.isdir(pretrained_model_name_or_path):
            config_dict = cls.load_config(pretrained_model_name_or_path, cache_dir=cache_dir, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision)
            folder_names = [k for k in config_dict.keys() if not k.startswith('_')]
            allow_patterns = [os.path.join(k, '*') for k in folder_names]
            allow_patterns += [FLAX_WEIGHTS_NAME, SCHEDULER_CONFIG_NAME, CONFIG_NAME, cls.config_name]
            ignore_patterns = ['*.bin', '*.safetensors'] if not from_pt else []
            ignore_patterns += ['*.onnx', '*.onnx_data', '*.xml', '*.pb']
            if cls != FlaxDiffusionPipeline: requested_pipeline_class = cls.__name__
            else:
                requested_pipeline_class = config_dict.get('_class_name', cls.__name__)
                requested_pipeline_class = requested_pipeline_class if requested_pipeline_class.startswith('Flax') else 'Flax' + requested_pipeline_class
            user_agent = {'pipeline_class': requested_pipeline_class}
            user_agent = http_user_agent(user_agent)
            cached_folder = snapshot_download(pretrained_model_name_or_path, cache_dir=cache_dir, proxies=proxies, local_files_only=local_files_only, token=token, revision=revision,
            allow_patterns=allow_patterns, ignore_patterns=ignore_patterns, user_agent=user_agent)
        else: cached_folder = pretrained_model_name_or_path
        config_dict = cls.load_config(cached_folder)
        if cls != FlaxDiffusionPipeline: pipeline_class = cls
        else:
            diffusers_module = importlib.import_module(cls.__module__.split('.')[0])
            class_name = config_dict['_class_name'] if config_dict['_class_name'].startswith('Flax') else 'Flax' + config_dict['_class_name']
            pipeline_class = getattr(diffusers_module, class_name)
        expected_modules, optional_kwargs = cls._get_signature_keys(pipeline_class)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        init_dict, unused_kwargs, _ = pipeline_class.extract_init_dict(config_dict, **kwargs)
        init_kwargs = {k: init_dict.pop(k) for k in optional_kwargs if k in init_dict}
        init_kwargs = {**init_kwargs, **passed_pipe_kwargs}
        def load_module(name, value):
            if value[0] is None: return False
            if name in passed_class_obj and passed_class_obj[name] is None: return False
            return True
        init_dict = {k: v for k, v in init_dict.items() if load_module(k, v)}
        params = {}
        from .. import pipelines
        for name, (library_name, class_name) in init_dict.items():
            if class_name is None:
                init_kwargs[name] = None
                continue
            is_pipeline_module = hasattr(pipelines, library_name)
            loaded_sub_model = None
            sub_model_should_be_defined = True
            if name in passed_class_obj:
                if not is_pipeline_module:
                    library = importlib.import_module(library_name)
                    class_obj = getattr(library, class_name)
                    importable_classes = LOADABLE_CLASSES[library_name]
                    class_candidates = {c: getattr(library, c, None) for c in importable_classes.keys()}
                    expected_class_obj = None
                    for class_name, class_candidate in class_candidates.items():
                        if class_candidate is not None and issubclass(class_obj, class_candidate): expected_class_obj = class_candidate
                    if not issubclass(passed_class_obj[name].__class__, expected_class_obj): raise ValueError(f'{passed_class_obj[name]} is of type: {type(passed_class_obj[name])}, but should be {expected_class_obj}')
                elif passed_class_obj[name] is None: sub_model_should_be_defined = False
                loaded_sub_model = passed_class_obj[name]
            elif is_pipeline_module:
                pipeline_module = getattr(pipelines, library_name)
                class_obj = import_flax_or_no_model(pipeline_module, class_name)
                importable_classes = ALL_IMPORTABLE_CLASSES
                class_candidates = {c: class_obj for c in importable_classes.keys()}
            else:
                library = importlib.import_module(library_name)
                class_obj = import_flax_or_no_model(library, class_name)
                importable_classes = LOADABLE_CLASSES[library_name]
                class_candidates = {c: getattr(library, c, None) for c in importable_classes.keys()}
            if loaded_sub_model is None and sub_model_should_be_defined:
                load_method_name = None
                for class_name, class_candidate in class_candidates.items():
                    if class_candidate is not None and issubclass(class_obj, class_candidate): load_method_name = importable_classes[class_name][1]
                load_method = getattr(class_obj, load_method_name)
                if os.path.isdir(os.path.join(cached_folder, name)): loadable_folder = os.path.join(cached_folder, name)
                else: loaded_sub_model = cached_folder
                if issubclass(class_obj, FlaxModelMixin):
                    loaded_sub_model, loaded_params = load_method(loadable_folder, from_pt=from_pt,
                    use_memory_efficient_attention=use_memory_efficient_attention, split_head_dim=split_head_dim, dtype=dtype)
                    params[name] = loaded_params
                elif is_transformers_available() and issubclass(class_obj, FlaxPreTrainedModel):
                    if from_pt:
                        loaded_sub_model = load_method(loadable_folder, from_pt=from_pt)
                        loaded_params = loaded_sub_model.params
                        del loaded_sub_model._params
                    else: loaded_sub_model, loaded_params = load_method(loadable_folder, _do_init=False)
                    params[name] = loaded_params
                elif issubclass(class_obj, FlaxSchedulerMixin):
                    loaded_sub_model, scheduler_state = load_method(loadable_folder)
                    params[name] = scheduler_state
                else: loaded_sub_model = load_method(loadable_folder)
            init_kwargs[name] = loaded_sub_model
        missing_modules = set(expected_modules) - set(init_kwargs.keys())
        passed_modules = list(passed_class_obj.keys())
        if len(missing_modules) > 0 and missing_modules <= set(passed_modules):
            for module in missing_modules: init_kwargs[module] = passed_class_obj.get(module, None)
        elif len(missing_modules) > 0:
            passed_modules = set(list(init_kwargs.keys()) + list(passed_class_obj.keys())) - optional_kwargs
            raise ValueError(f'Pipeline {pipeline_class} expected {expected_modules}, but only {passed_modules} were passed.')
        model = pipeline_class(**init_kwargs, dtype=dtype)
        return (model, params)
    @classmethod
    def _get_signature_keys(cls, obj):
        parameters = inspect.signature(obj.__init__).parameters
        required_parameters = {k: v for k, v in parameters.items() if v.default == inspect._empty}
        optional_parameters = set({k for k, v in parameters.items() if v.default != inspect._empty})
        expected_modules = set(required_parameters.keys()) - {'self'}
        return (expected_modules, optional_parameters)
    @property
    def components(self) -> Dict[str, Any]:
        """Examples:"""
        expected_modules, optional_parameters = self._get_signature_keys(self)
        components = {k: getattr(self, k) for k in self.config.keys() if not k.startswith('_') and k not in optional_parameters}
        if set(components.keys()) != expected_modules: raise ValueError(f'{self} has been incorrectly initialized or {self.__class__} is incorrectly implemented. Expected {expected_modules} to be defined, but {components} are defined.')
        return components
    @staticmethod
    def numpy_to_pil(images):
        if images.ndim == 3: images = images[None, ...]
        images = (images * 255).round().astype('uint8')
        if images.shape[-1] == 1: pil_images = [Image.fromarray(image.squeeze(), mode='L') for image in images]
        else: pil_images = [Image.fromarray(image) for image in images]
        return pil_images
    def progress_bar(self, iterable):
        if not hasattr(self, '_progress_bar_config'): self._progress_bar_config = {}
        elif not isinstance(self._progress_bar_config, dict): raise ValueError(f'`self._progress_bar_config` should be of type `dict`, but is {type(self._progress_bar_config)}.')
        return tqdm(iterable, **self._progress_bar_config)
    def set_progress_bar_config(self, **kwargs): self._progress_bar_config = kwargs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
