'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .single_file_utils import (SingleFileComponentError, _is_legacy_scheduler_kwargs, _is_model_weights_in_cached_folder, _legacy_load_clip_tokenizer, _legacy_load_safety_checker,
_legacy_load_scheduler, create_diffusers_clip_model_from_ldm, create_diffusers_t5_model_from_checkpoint, fetch_diffusers_config, fetch_original_config,
is_clip_model_in_single_file, is_t5_in_single_file, load_single_file_checkpoint)
from huggingface_hub.utils import LocalEntryNotFoundError, validate_hf_hub_args
from ..utils import deprecate, is_transformers_available
from huggingface_hub import snapshot_download
from packaging import version
import importlib
import inspect
import torch
import os
SINGLE_FILE_OPTIONAL_COMPONENTS = ['safety_checker']
if is_transformers_available():
    import sapiens_transformers
    from sapiens_transformers import PreTrainedModel, PreTrainedTokenizer
def load_single_file_sub_model(library_name, class_name, name, checkpoint, pipelines, is_pipeline_module, cached_model_config_path, original_config=None, local_files_only=False, torch_dtype=None, is_legacy_loading=False, **kwargs):
    if is_pipeline_module:
        pipeline_module = getattr(pipelines, library_name)
        class_obj = getattr(pipeline_module, class_name)
    else:
        library = importlib.import_module(library_name)
        class_obj = getattr(library, class_name)
    if is_transformers_available(): sapiens_transformers_version = version.parse(version.parse(sapiens_transformers.__version__).base_version)
    else: sapiens_transformers_version = 'N/A'
    is_transformers_model = is_transformers_available() and issubclass(class_obj, PreTrainedModel) and (sapiens_transformers_version >= version.parse('4.20.0'))
    is_tokenizer = is_transformers_available() and issubclass(class_obj, PreTrainedTokenizer) and (sapiens_transformers_version >= version.parse('4.20.0'))
    diffusers_module = importlib.import_module(__name__.split('.')[0])
    is_diffusers_single_file_model = issubclass(class_obj, diffusers_module.FromOriginalModelMixin)
    is_diffusers_model = issubclass(class_obj, diffusers_module.ModelMixin)
    is_diffusers_scheduler = issubclass(class_obj, diffusers_module.SchedulerMixin)
    if is_diffusers_single_file_model:
        load_method = getattr(class_obj, 'from_single_file')
        if original_config: cached_model_config_path = None
        loaded_sub_model = load_method(pretrained_model_link_or_path_or_dict=checkpoint, original_config=original_config, config=cached_model_config_path, subfolder=name, torch_dtype=torch_dtype, local_files_only=local_files_only, **kwargs)
    elif is_transformers_model and is_clip_model_in_single_file(class_obj, checkpoint): loaded_sub_model = create_diffusers_clip_model_from_ldm(class_obj, checkpoint=checkpoint, config=cached_model_config_path,
    subfolder=name, torch_dtype=torch_dtype, local_files_only=local_files_only, is_legacy_loading=is_legacy_loading)
    elif is_transformers_model and is_t5_in_single_file(checkpoint): loaded_sub_model = create_diffusers_t5_model_from_checkpoint(class_obj, checkpoint=checkpoint, config=cached_model_config_path, subfolder=name, torch_dtype=torch_dtype, local_files_only=local_files_only)
    elif is_tokenizer and is_legacy_loading: loaded_sub_model = _legacy_load_clip_tokenizer(class_obj, checkpoint=checkpoint, config=cached_model_config_path, local_files_only=local_files_only)
    elif is_diffusers_scheduler and (is_legacy_loading or _is_legacy_scheduler_kwargs(kwargs)): loaded_sub_model = _legacy_load_scheduler(class_obj, checkpoint=checkpoint, component_name=name, original_config=original_config, **kwargs)
    else:
        if not hasattr(class_obj, 'from_pretrained'): raise ValueError(f'The component {class_obj.__name__} cannot be loaded as it does not seem to have a supported loading method.')
        loading_kwargs = {}
        loading_kwargs.update({'pretrained_model_name_or_path': cached_model_config_path, 'subfolder': name, 'local_files_only': local_files_only})
        if issubclass(class_obj, torch.nn.Module): loading_kwargs.update({'torch_dtype': torch_dtype})
        if is_diffusers_model or is_transformers_model:
            if not _is_model_weights_in_cached_folder(cached_model_config_path, name): raise SingleFileComponentError(f'Failed to load {class_name}. Weights for this component appear to be missing in the checkpoint.')
        load_method = getattr(class_obj, 'from_pretrained')
        loaded_sub_model = load_method(**loading_kwargs)
    return loaded_sub_model
def _map_component_types_to_config_dict(component_types):
    diffusers_module = importlib.import_module(__name__.split('.')[0])
    config_dict = {}
    component_types.pop('self', None)
    if is_transformers_available(): sapiens_transformers_version = version.parse(version.parse(sapiens_transformers.__version__).base_version)
    else: sapiens_transformers_version = 'N/A'
    for component_name, component_value in component_types.items():
        is_diffusers_model = issubclass(component_value[0], diffusers_module.ModelMixin)
        is_scheduler_enum = component_value[0].__name__ == 'KarrasDiffusionSchedulers'
        is_scheduler = issubclass(component_value[0], diffusers_module.SchedulerMixin)
        is_transformers_model = is_transformers_available() and issubclass(component_value[0], PreTrainedModel) and (sapiens_transformers_version >= version.parse('4.20.0'))
        is_transformers_tokenizer = is_transformers_available() and issubclass(component_value[0], PreTrainedTokenizer) and (sapiens_transformers_version >= version.parse('4.20.0'))
        if is_diffusers_model and component_name not in SINGLE_FILE_OPTIONAL_COMPONENTS: config_dict[component_name] = ['sapiens_transformers.diffusers', component_value[0].__name__]
        elif is_scheduler_enum or is_scheduler:
            if is_scheduler_enum: config_dict[component_name] = ['sapiens_transformers.diffusers', 'DDIMScheduler']
            elif is_scheduler: config_dict[component_name] = ['sapiens_transformers.diffusers', component_value[0].__name__]
        elif (is_transformers_model or is_transformers_tokenizer) and component_name not in SINGLE_FILE_OPTIONAL_COMPONENTS: config_dict[component_name] = ['sapiens_transformers', component_value[0].__name__]
        else: config_dict[component_name] = [None, None]
    return config_dict
def _infer_pipeline_config_dict(pipeline_class):
    parameters = inspect.signature(pipeline_class.__init__).parameters
    required_parameters = {k: v for k, v in parameters.items() if v.default == inspect._empty}
    component_types = pipeline_class._get_signature_types()
    component_types = {k: v for k, v in component_types.items() if k in required_parameters}
    config_dict = _map_component_types_to_config_dict(component_types)
    return config_dict
def _download_diffusers_model_config_from_hub(pretrained_model_name_or_path, cache_dir, revision, proxies, force_download=None, local_files_only=None, token=None):
    allow_patterns = ['**/*.json', '*.json', '*.txt', '**/*.txt', '**/*.model']
    cached_model_path = snapshot_download(pretrained_model_name_or_path, cache_dir=cache_dir, revision=revision, proxies=proxies, force_download=force_download, local_files_only=local_files_only, token=token, allow_patterns=allow_patterns)
    return cached_model_path
class FromSingleFileMixin:
    @classmethod
    @validate_hf_hub_args
    def from_single_file(cls, pretrained_model_link_or_path, **kwargs):
        """Examples:"""
        original_config_file = kwargs.pop('original_config_file', None)
        config = kwargs.pop('config', None)
        original_config = kwargs.pop('original_config', None)
        if original_config_file is not None:
            deprecation_message = '`original_config_file` argument is deprecated and will be removed in future versions.please use the `original_config` argument instead.'
            deprecate('original_config_file', '1.0.0', deprecation_message)
            original_config = original_config_file
        force_download = kwargs.pop('force_download', False)
        proxies = kwargs.pop('proxies', None)
        token = kwargs.pop('token', None)
        cache_dir = kwargs.pop('cache_dir', None)
        local_files_only = kwargs.pop('local_files_only', False)
        revision = kwargs.pop('revision', None)
        torch_dtype = kwargs.pop('torch_dtype', None)
        is_legacy_loading = False
        scaling_factor = kwargs.get('scaling_factor', None)
        if scaling_factor is not None:
            deprecation_message = 'Passing the `scaling_factor` argument to `from_single_file is deprecated and will be ignored in future versions.'
            deprecate('scaling_factor', '1.0.0', deprecation_message)
        if original_config is not None: original_config = fetch_original_config(original_config, local_files_only=local_files_only)
        from ..pipelines.pipeline_utils import _get_pipeline_class
        pipeline_class = _get_pipeline_class(cls, config=None)
        checkpoint = load_single_file_checkpoint(pretrained_model_link_or_path, force_download=force_download, proxies=proxies, token=token, cache_dir=cache_dir, local_files_only=local_files_only, revision=revision)
        if config is None:
            config = fetch_diffusers_config(checkpoint)
            default_pretrained_model_config_name = config['pretrained_model_name_or_path']
        else: default_pretrained_model_config_name = config
        if not os.path.isdir(default_pretrained_model_config_name):
            if default_pretrained_model_config_name.count('/') > 1: raise ValueError(f'The provided config "{config}" is neither a valid local path nor a valid repo id. Please check the parameter.')
            try:
                cached_model_config_path = _download_diffusers_model_config_from_hub(default_pretrained_model_config_name, cache_dir=cache_dir, revision=revision, proxies=proxies, force_download=force_download, local_files_only=local_files_only, token=token)
                config_dict = pipeline_class.load_config(cached_model_config_path)
            except LocalEntryNotFoundError:
                if original_config is None:
                    cached_model_config_path = _download_diffusers_model_config_from_hub(default_pretrained_model_config_name, cache_dir=cache_dir, revision=revision, proxies=proxies, force_download=force_download, local_files_only=False, token=token)
                    config_dict = pipeline_class.load_config(cached_model_config_path)
                else:
                    is_legacy_loading = True
                    cached_model_config_path = None
                    config_dict = _infer_pipeline_config_dict(pipeline_class)
                    config_dict['_class_name'] = pipeline_class.__name__
        else:
            cached_model_config_path = default_pretrained_model_config_name
            config_dict = pipeline_class.load_config(cached_model_config_path)
        config_dict.pop('_ignore_files', None)
        expected_modules, optional_kwargs = pipeline_class._get_signature_keys(cls)
        passed_class_obj = {k: kwargs.pop(k) for k in expected_modules if k in kwargs}
        passed_pipe_kwargs = {k: kwargs.pop(k) for k in optional_kwargs if k in kwargs}
        init_dict, unused_kwargs, _ = pipeline_class.extract_init_dict(config_dict, **kwargs)
        init_kwargs = {k: init_dict.pop(k) for k in optional_kwargs if k in init_dict}
        init_kwargs = {**init_kwargs, **passed_pipe_kwargs}
        from .. import pipelines
        def load_module(name, value):
            if value[0] is None: return False
            if name in passed_class_obj and passed_class_obj[name] is None: return False
            if name in SINGLE_FILE_OPTIONAL_COMPONENTS: return False
            return True
        init_dict = {k: v for k, v in init_dict.items() if load_module(k, v)}
        for name, (library_name, class_name) in sorted(init_dict.items()):
            loaded_sub_model = None
            is_pipeline_module = hasattr(pipelines, library_name)
            if name in passed_class_obj: loaded_sub_model = passed_class_obj[name]
            else:
                try: loaded_sub_model = load_single_file_sub_model(library_name=library_name, class_name=class_name, name=name, checkpoint=checkpoint, is_pipeline_module=is_pipeline_module, cached_model_config_path=cached_model_config_path,
                pipelines=pipelines, torch_dtype=torch_dtype, original_config=original_config, local_files_only=local_files_only, is_legacy_loading=is_legacy_loading, **kwargs)
                except SingleFileComponentError as e: raise SingleFileComponentError(f"{e.message}\nPlease load the component before passing it in as an argument to `from_single_file`.\n\n{name} = {class_name}.from_pretrained('...')\npipe = {pipeline_class.__name__}.from_single_file(<checkpoint path>, {name}={name})\n\n")
            init_kwargs[name] = loaded_sub_model
        missing_modules = set(expected_modules) - set(init_kwargs.keys())
        passed_modules = list(passed_class_obj.keys())
        optional_modules = pipeline_class._optional_components
        if len(missing_modules) > 0 and missing_modules <= set(passed_modules + optional_modules):
            for module in missing_modules: init_kwargs[module] = passed_class_obj.get(module, None)
        elif len(missing_modules) > 0:
            passed_modules = set(list(init_kwargs.keys()) + list(passed_class_obj.keys())) - optional_kwargs
            raise ValueError(f'Pipeline {pipeline_class} expected {expected_modules}, but only {passed_modules} were passed.')
        load_safety_checker = kwargs.pop('load_safety_checker', None)
        if load_safety_checker is not None:
            deprecation_message = 'Please pass instances of `StableDiffusionSafetyChecker` and `AutoImageProcessor`using the `safety_checker` and `feature_extractor` arguments in `from_single_file`'
            deprecate('load_safety_checker', '1.0.0', deprecation_message)
            safety_checker_components = _legacy_load_safety_checker(local_files_only, torch_dtype)
            init_kwargs.update(safety_checker_components)
        pipe = pipeline_class(**init_kwargs)
        return pipe
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
