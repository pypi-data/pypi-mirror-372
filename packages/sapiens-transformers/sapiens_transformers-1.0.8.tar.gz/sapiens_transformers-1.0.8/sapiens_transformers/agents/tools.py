"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import base64
import importlib
import inspect
import io
import json
import os
import tempfile
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional, Union
from huggingface_hub import create_repo, get_collection, hf_hub_download, metadata_update, upload_folder
from huggingface_hub.utils import RepositoryNotFoundError, build_hf_headers, get_session
from packaging import version
from ..dynamic_module_utils import (custom_object_save, get_class_from_dynamic_module, get_imports)
from ..models.auto import AutoProcessor
from ..utils import (CONFIG_NAME, TypeHintParsingException, cached_file, get_json_schema, is_sapiens_accelerator_available, is_torch_available, is_vision_available, logging)
from .agent_types import handle_agent_inputs, handle_agent_outputs
logger = logging.get_logger(__name__)
if is_torch_available(): import torch
if is_sapiens_accelerator_available():
    from sapiens_accelerator import PartialState
    from sapiens_accelerator.utils import send_to_device
TOOL_CONFIG_FILE = "tool_config.json"
def get_repo_type(repo_id, repo_type=None, **hub_kwargs):
    if repo_type is not None: return repo_type
    try:
        hf_hub_download(repo_id, TOOL_CONFIG_FILE, repo_type="space", **hub_kwargs)
        return "space"
    except RepositoryNotFoundError:
        try:
            hf_hub_download(repo_id, TOOL_CONFIG_FILE, repo_type="model", **hub_kwargs)
            return "model"
        except RepositoryNotFoundError: raise EnvironmentError(f"`{repo_id}` does not seem to be a valid repo identifier on the Hub.")
        except Exception: return "model"
    except Exception: return "space"
APP_FILE_TEMPLATE = """from sapiens_transformers import launch_gradio_demo
from {module_name} import {class_name}
launch_gradio_demo({class_name})
"""
def validate_after_init(cls):
    original_init = cls.__init__
    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if not isinstance(self, PipelineTool): self.validate_arguments()
    cls.__init__ = new_init
    return cls
@validate_after_init
class Tool:
    name: str
    description: str
    inputs: Dict[str, Dict[str, Union[str, type]]]
    output_type: type
    def __init__(self, *args, **kwargs): self.is_initialized = False
    def validate_arguments(self):
        required_attributes = {"description": str, "name": str, "inputs": Dict, "output_type": str}
        authorized_types = ["string", "integer", "number", "image", "audio", "any"]
        for attr, expected_type in required_attributes.items():
            attr_value = getattr(self, attr, None)
            if not isinstance(attr_value, expected_type): raise TypeError(f"You must set an attribute {attr} of type {expected_type.__name__}.")
        for input_name, input_content in self.inputs.items():
            assert "type" in input_content, f"Input '{input_name}' should specify a type."
            if input_content["type"] not in authorized_types: raise Exception(f"Input '{input_name}': type '{input_content['type']}' is not an authorized value, should be one of {authorized_types}.")
            assert "description" in input_content, f"Input '{input_name}' should have a description."
        assert getattr(self, "output_type", None) in authorized_types
        if not isinstance(self, PipelineTool):
            signature = inspect.signature(self.forward)
            if not set(signature.parameters.keys()) == set(self.inputs.keys()): raise Exception("Tool's 'forward' method should take 'self' as its first argument, then its next arguments should match the keys of tool attribute 'inputs'.")
    def forward(self, *args, **kwargs): return NotImplemented("Write this method in your subclass of `Tool`.")
    def __call__(self, *args, **kwargs):
        args, kwargs = handle_agent_inputs(*args, **kwargs)
        outputs = self.forward(*args, **kwargs)
        return handle_agent_outputs(outputs, self.output_type)
    def setup(self): self.is_initialized = True
    def save(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        if self.__module__ == "__main__": raise ValueError(f"We can't save the code defining {self} in {output_dir} as it's been defined in __main__. You have to put this code in a separate module so we can include it in the saved folder.")
        module_files = custom_object_save(self, output_dir)
        module_name = self.__class__.__module__
        last_module = module_name.split(".")[-1]
        full_name = f"{last_module}.{self.__class__.__name__}"
        config_file = os.path.join(output_dir, "tool_config.json")
        if os.path.isfile(config_file):
            with open(config_file, "r", encoding="utf-8") as f: tool_config = json.load(f)
        else: tool_config = {}
        tool_config = {"tool_class": full_name, "description": self.description, "name": self.name, "inputs": self.inputs, "output_type": str(self.output_type)}
        with open(config_file, "w", encoding="utf-8") as f: f.write(json.dumps(tool_config, indent=2, sort_keys=True) + "\n")
        app_file = os.path.join(output_dir, "app.py")
        with open(app_file, "w", encoding="utf-8") as f: f.write(APP_FILE_TEMPLATE.format(module_name=last_module, class_name=self.__class__.__name__))
        requirements_file = os.path.join(output_dir, "requirements.txt")
        imports = []
        for module in module_files: imports.extend(get_imports(module))
        imports = list(set(imports))
        with open(requirements_file, "w", encoding="utf-8") as f: f.write("\n".join(imports) + "\n")
    @classmethod
    def from_hub(cls, repo_id: str, model_repo_id: Optional[str] = None, token: Optional[str] = None, **kwargs):
        hub_kwargs_names = ["cache_dir", "force_download", "resume_download", "proxies", "revision", "repo_type", "subfolder", "local_files_only"]
        hub_kwargs = {k: v for k, v in kwargs.items() if k in hub_kwargs_names}
        hub_kwargs["repo_type"] = get_repo_type(repo_id, **hub_kwargs)
        resolved_config_file = cached_file(repo_id, TOOL_CONFIG_FILE, token=token, **hub_kwargs, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False, _raise_exceptions_for_connection_errors=False)
        is_tool_config = resolved_config_file is not None
        if resolved_config_file is None: resolved_config_file = cached_file(repo_id, CONFIG_NAME, token=token, **hub_kwargs, _raise_exceptions_for_gated_repo=False, _raise_exceptions_for_missing_entries=False, _raise_exceptions_for_connection_errors=False)
        if resolved_config_file is None: raise EnvironmentError(f"{repo_id} does not appear to provide a valid configuration in `tool_config.json` or `config.json`.")
        with open(resolved_config_file, encoding="utf-8") as reader: config = json.load(reader)
        if not is_tool_config:
            if "custom_tool" not in config: raise EnvironmentError(f"{repo_id} does not provide a mapping to custom tools in its configuration `config.json`.")
            custom_tool = config["custom_tool"]
        else: custom_tool = config
        tool_class = custom_tool["tool_class"]
        tool_class = get_class_from_dynamic_module(tool_class, repo_id, token=token, **hub_kwargs)
        if len(tool_class.name) == 0: tool_class.name = custom_tool["name"]
        if tool_class.name != custom_tool["name"]:
            logger.warning(f"{tool_class.__name__} implements a different name in its configuration and class. Using the tool configuration name.")
            tool_class.name = custom_tool["name"]
        if len(tool_class.description) == 0: tool_class.description = custom_tool["description"]
        if tool_class.description != custom_tool["description"]:
            logger.warning(f"{tool_class.__name__} implements a different description in its configuration and class. Using the tool configuration description.")
            tool_class.description = custom_tool["description"]
        if tool_class.inputs != custom_tool["inputs"]: tool_class.inputs = custom_tool["inputs"]
        if tool_class.output_type != custom_tool["output_type"]: tool_class.output_type = custom_tool["output_type"]
        return tool_class(**kwargs)
    def push_to_hub(self, repo_id: str, commit_message: str = "Upload tool", private: Optional[bool] = None, token: Optional[Union[bool, str]] = None, create_pr: bool = False) -> str:
        repo_url = create_repo(repo_id=repo_id, token=token, private=private, exist_ok=True, repo_type="space", space_sdk="gradio")
        repo_id = repo_url.repo_id
        metadata_update(repo_id, {"tags": ["tool"]}, repo_type="space")
        with tempfile.TemporaryDirectory() as work_dir:
            self.save(work_dir)
            logger.info(f"Uploading the following files to {repo_id}: {','.join(os.listdir(work_dir))}")
            return upload_folder(repo_id=repo_id, commit_message=commit_message, folder_path=work_dir, token=token, create_pr=create_pr, repo_type="space")
    @staticmethod
    def from_gradio(gradio_tool):
        import inspect
        class GradioToolWrapper(Tool):
            def __init__(self, _gradio_tool):
                super().__init__()
                self.name = _gradio_tool.name
                self.description = _gradio_tool.description
                self.output_type = "string"
                self._gradio_tool = _gradio_tool
                func_args = list(inspect.signature(_gradio_tool.run).parameters.keys())
                self.inputs = {key: "" for key in func_args}
            def forward(self, *args, **kwargs): return self._gradio_tool.run(*args, **kwargs)
        return GradioToolWrapper(gradio_tool)
    @staticmethod
    def from_langchain(langchain_tool):
        class LangChainToolWrapper(Tool):
            def __init__(self, _langchain_tool):
                super().__init__()
                self.name = _langchain_tool.name.lower()
                self.description = _langchain_tool.description
                self.inputs = parse_langchain_args(_langchain_tool.args)
                self.output_type = "string"
                self.langchain_tool = _langchain_tool
            def forward(self, *args, **kwargs):
                tool_input = kwargs.copy()
                for index, argument in enumerate(args):
                    if index < len(self.inputs):
                        input_key = next(iter(self.inputs))
                        tool_input[input_key] = argument
                return self.langchain_tool.run(tool_input)
        return LangChainToolWrapper(langchain_tool)
DEFAULT_TOOL_DESCRIPTION_TEMPLATE = """
- {{ tool.name }}: {{ tool.description }}
    Takes inputs: {{tool.inputs}}
    Returns an output of type: {{tool.output_type}}
"""
def get_tool_description_with_args(tool: Tool, description_template: str = DEFAULT_TOOL_DESCRIPTION_TEMPLATE) -> str:
    compiled_template = compile_jinja_template(description_template)
    rendered = compiled_template.render(tool=tool)
    return rendered
@lru_cache
def compile_jinja_template(template):
    try:
        import jinja2
        from jinja2.exceptions import TemplateError
        from jinja2.sandbox import ImmutableSandboxedEnvironment
    except ImportError: raise ImportError("template requires jinja2 to be installed.")
    if version.parse(jinja2.__version__) < version.parse("3.1.0"): raise ImportError("template requires jinja2>=3.1.0 to be installed. Your version is " f"{jinja2.__version__}.")
    def raise_exception(message): raise TemplateError(message)
    jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)
    jinja_env.globals["raise_exception"] = raise_exception
    return jinja_env.from_string(template)
class PipelineTool(Tool):
    pre_processor_class = AutoProcessor
    model_class = None
    post_processor_class = AutoProcessor
    default_checkpoint = None
    description = "This is a pipeline tool"
    name = "pipeline"
    inputs = {"prompt": str}
    output_type = str
    def __init__(self, model=None, pre_processor=None, post_processor=None, device=None, device_map=None, model_kwargs=None, token=None, **hub_kwargs):
        if not is_torch_available(): raise ImportError("Please install torch in order to use this tool.")
        if not is_sapiens_accelerator_available(): raise ImportError("Please install sapiens_accelerator in order to use this tool.")
        if model is None:
            if self.default_checkpoint is None: raise ValueError("This tool does not implement a default checkpoint, you need to pass one.")
            model = self.default_checkpoint
        if pre_processor is None: pre_processor = model
        self.model = model
        self.pre_processor = pre_processor
        self.post_processor = post_processor
        self.device = device
        self.device_map = device_map
        self.model_kwargs = {} if model_kwargs is None else model_kwargs
        if device_map is not None: self.model_kwargs["device_map"] = device_map
        self.hub_kwargs = hub_kwargs
        self.hub_kwargs["token"] = token
        super().__init__()
    def setup(self):
        if isinstance(self.pre_processor, str): self.pre_processor = self.pre_processor_class.from_pretrained(self.pre_processor, **self.hub_kwargs)
        if isinstance(self.model, str): self.model = self.model_class.from_pretrained(self.model, **self.model_kwargs, **self.hub_kwargs)
        if self.post_processor is None: self.post_processor = self.pre_processor
        elif isinstance(self.post_processor, str): self.post_processor = self.post_processor_class.from_pretrained(self.post_processor, **self.hub_kwargs)
        if self.device is None:
            if self.device_map is not None: self.device = list(self.model.hf_device_map.values())[0]
            else: self.device = PartialState().default_device
        if self.device_map is None: self.model.to(self.device)
        super().setup()
    def encode(self, raw_inputs): return self.pre_processor(raw_inputs)
    def forward(self, inputs):
        with torch.no_grad(): return self.model(**inputs)
    def decode(self, outputs): return self.post_processor(outputs)
    def __call__(self, *args, **kwargs):
        args, kwargs = handle_agent_inputs(*args, **kwargs)
        if not self.is_initialized: self.setup()
        encoded_inputs = self.encode(*args, **kwargs)
        tensor_inputs = {k: v for k, v in encoded_inputs.items() if isinstance(v, torch.Tensor)}
        non_tensor_inputs = {k: v for k, v in encoded_inputs.items() if not isinstance(v, torch.Tensor)}
        encoded_inputs = send_to_device(tensor_inputs, self.device)
        outputs = self.forward({**encoded_inputs, **non_tensor_inputs})
        outputs = send_to_device(outputs, "cpu")
        decoded_outputs = self.decode(outputs)
        return handle_agent_outputs(decoded_outputs, self.output_type)
def launch_gradio_demo(tool_class: Tool):
    try: import gradio as gr
    except ImportError: raise ImportError("Gradio should be installed in order to launch a gradio demo.")
    tool = tool_class()
    def fn(*args, **kwargs): return tool(*args, **kwargs)
    gradio_inputs = []
    for input_name, input_details in tool_class.inputs.items():
        input_type = input_details["type"]
        if input_type == "image": gradio_inputs.append(gr.Image(label=input_name))
        elif input_type == "audio": gradio_inputs.append(gr.Audio(label=input_name))
        elif input_type in ["string", "integer", "number"]: gradio_inputs.append(gr.Textbox(label=input_name))
        else:
            error_message = f"Input type '{input_type}' not supported."
            raise ValueError(error_message)
    gradio_output = tool_class.output_type
    assert gradio_output in ["string", "image", "audio"], f"Output type '{gradio_output}' not supported."
    gr.Interface(fn=fn, inputs=gradio_inputs, outputs=gradio_output, title=tool_class.__name__, article=tool.description).launch()
TOOL_MAPPING = {'document_question_answering': 'DocumentQuestionAnsweringTool', 'image_question_answering': 'ImageQuestionAnsweringTool', 'speech_to_text': 'SpeechToTextTool', 'text_to_speech': 'TextToSpeechTool', 'translation': 'TranslationTool', 'python_interpreter': 'PythonInterpreterTool', 'web_search': 'DuckDuckGoSearchTool'}
def load_tool(task_or_repo_id, model_repo_id=None, token=None, **kwargs):
    if task_or_repo_id in TOOL_MAPPING:
        tool_class_name = TOOL_MAPPING[task_or_repo_id]
        main_module = importlib.import_module("sapiens_transformers")
        tools_module = main_module.agents
        tool_class = getattr(tools_module, tool_class_name)
        return tool_class(model_repo_id, token=token, **kwargs)
    else:
        logger.warning_once(f"You're loading a tool from the Hub from {model_repo_id}. Please make sure this is a source that you trust as the code within that tool will be executed on your machine. Always verify the code of the tools that you load. We recommend specifying a `revision` to ensure you're loading the code that you have checked.")
        return Tool.from_hub(task_or_repo_id, model_repo_id=model_repo_id, token=token, **kwargs)
def add_description(description):
    def inner(func):
        func.description = description
        func.name = func.__name__
        return func
    return inner
class EndpointClient:
    def __init__(self, endpoint_url: str, token: Optional[str] = None):
        self.headers = {**build_hf_headers(token=token), "Content-Type": "application/json"}
        self.endpoint_url = endpoint_url
    @staticmethod
    def encode_image(image):
        _bytes = io.BytesIO()
        image.save(_bytes, format="PNG")
        b64 = base64.b64encode(_bytes.getvalue())
        return b64.decode("utf-8")
    @staticmethod
    def decode_image(raw_image):
        if not is_vision_available(): raise ImportError("This tool returned an image but Pillow is not installed. Please install it (`pip install Pillow`).")
        from PIL import Image
        b64 = base64.b64decode(raw_image)
        _bytes = io.BytesIO(b64)
        return Image.open(_bytes)
    def __call__(self, inputs: Optional[Union[str, Dict, List[str], List[List[str]]]] = None, params: Optional[Dict] = None, data: Optional[bytes] = None, output_image: bool = False) -> Any:
        payload = {}
        if inputs: payload["inputs"] = inputs
        if params: payload["parameters"] = params
        response = get_session().post(self.endpoint_url, headers=self.headers, json=payload, data=data)
        if output_image: return self.decode_image(response.content)
        else: return response.json()
def parse_langchain_args(args: Dict[str, str]) -> Dict[str, str]:
    inputs = args.copy()
    for arg_details in inputs.values():
        if "title" in arg_details: arg_details.pop("title")
    return inputs
class ToolCollection:
    def __init__(self, collection_slug: str, token: Optional[str] = None):
        self._collection = get_collection(collection_slug, token=token)
        self._hub_repo_ids = {item.item_id for item in self._collection.items if item.item_type == "space"}
        self.tools = {Tool.from_hub(repo_id) for repo_id in self._hub_repo_ids}
def tool(tool_function: Callable) -> Tool:
    parameters = get_json_schema(tool_function)["function"]
    if "return" not in parameters: raise TypeHintParsingException("Tool return type not found: make sure your function has a return type hint!")
    class_name = f"{parameters['name'].capitalize()}Tool"
    class SpecificTool(Tool):
        name = parameters["name"]
        description = parameters["description"]
        inputs = parameters["parameters"]["properties"]
        output_type = parameters["return"]["type"]
        @wraps(tool_function)
        def forward(self, *args, **kwargs): return tool_function(*args, **kwargs)
    original_signature = inspect.signature(tool_function)
    new_parameters = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)] + list(original_signature.parameters.values())
    new_signature = original_signature.replace(parameters=new_parameters)
    SpecificTool.forward.__signature__ = new_signature
    SpecificTool.__name__ = class_name
    return SpecificTool()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
