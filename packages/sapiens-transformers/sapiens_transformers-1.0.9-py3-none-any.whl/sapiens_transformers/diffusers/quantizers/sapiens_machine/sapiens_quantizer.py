'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from ...utils import get_module_from_name
from ..base import DiffusersQuantizer
if TYPE_CHECKING: from ...models.modeling_utils import ModelMixin
from ...utils import is_sapiens_accelerator_available, is_sapiens_accelerator_version, is_sapiens_machine_available, is_sapiens_machine_version, is_torch_available
if is_torch_available(): import torch
class Sapiens4BitDiffusersQuantizer(DiffusersQuantizer):
    use_keep_in_fp32_modules = True
    requires_calibration = False
    def __init__(self, quantization_config, **kwargs):
        super().__init__(quantization_config, **kwargs)
        if self.quantization_config.llm_int8_skip_modules is not None: self.modules_to_not_convert = self.quantization_config.llm_int8_skip_modules
    def validate_environment(self, *args, **kwargs):
        if not torch.cuda.is_available(): raise RuntimeError('No GPU found. A GPU is needed for quantization.')
        if not is_sapiens_accelerator_available() or is_sapiens_accelerator_version('<', '0.26.0'): raise ImportError("Using `sapiens_machine` 4-bit quantization requires SapiensAccelerator: `pip install 'sapiens_accelerator>=0.26.0'`")
        if not is_sapiens_machine_available() or is_sapiens_machine_version('<', '0.43.3'): raise ImportError('Using `sapiens_machine` 4-bit quantization requires the latest version of sapiens_machine: `pip install -U sapiens_machine`')
        if kwargs.get('from_flax', False): raise ValueError('Converting into 4-bit weights from flax weights is currently not supported, please make sure the weights are in PyTorch format.')
        device_map = kwargs.get('device_map', None)
        if device_map is not None and isinstance(device_map, dict) and (not self.quantization_config.llm_int8_enable_fp32_cpu_offload):
            device_map_without_no_convert = {key: device_map[key] for key in device_map.keys() if key not in self.modules_to_not_convert}
            if 'cpu' in device_map_without_no_convert.values() or 'disk' in device_map_without_no_convert.values(): raise ValueError('Some modules are dispatched on the CPU or the disk. Make sure you have enough GPU RAM to fit the quantized model. If you want to dispatch the model on the CPU or the disk while keeping these modules in 32-bit, you need to set `load_in_8bit_fp32_cpu_offload=True` and pass a custom `device_map` to `from_pretrained`. Check https://huggingface.co/docs/transformers/main/en/main_classes/quantization#offload-between-cpu-and-gpu for more details. ')
    def adjust_target_dtype(self, target_dtype: 'torch.dtype') -> 'torch.dtype':
        if target_dtype != torch.int8:
            from sapiens_accelerator.utils import CustomDtype
            return CustomDtype.INT4
        else: raise ValueError(f'Wrong `target_dtype` ({target_dtype}) provided.')
    def check_if_quantized_param(self, model: 'ModelMixin', param_value: 'torch.Tensor', param_name: str, state_dict: Dict[str, Any], **kwargs) -> bool:
        import sapiens_machine as sapiens
        module, tensor_name = get_module_from_name(model, param_name)
        if isinstance(module._parameters.get(tensor_name, None), sapiens.nn.Params4bit): return True
        elif isinstance(module, sapiens.nn.Linear4bit) and tensor_name == 'bias': return True
        else: return False
    def create_quantized_param(self, model: 'ModelMixin', param_value: 'torch.Tensor', param_name: str, target_device: 'torch.device',
    state_dict: Dict[str, Any], unexpected_keys: Optional[List[str]]=None):
        import sapiens_machine as sapiens
        module, tensor_name = get_module_from_name(model, param_name)
        if tensor_name not in module._parameters: raise ValueError(f'{module} does not have a parameter or a buffer named {tensor_name}.')
        old_value = getattr(module, tensor_name)
        if tensor_name == 'bias':
            if param_value is None: new_value = old_value.to(target_device)
            else: new_value = param_value.to(target_device)
            new_value = torch.nn.Parameter(new_value, requires_grad=old_value.requires_grad)
            module._parameters[tensor_name] = new_value
            return
        if not isinstance(module._parameters[tensor_name], sapiens.nn.Params4bit): raise ValueError('this function only loads `Linear4bit components`')
        if old_value.device == torch.device('meta') and target_device not in ['meta', torch.device('meta')] and (param_value is None): raise ValueError(f'{tensor_name} is on the meta device, we need a `value` to put in on {target_device}.')
        if self.pre_quantized:
            if not self.is_serializable: raise ValueError('Detected int4 weights but the version of sapiens_machine is not compatible with int4 serialization. Make sure to download the latest `sapiens_machine` version. `pip install --upgrade sapiens_machine`.')
            if param_name + '.quant_state.sapiens_machine__fp4' not in state_dict and param_name + '.quant_state.sapiens_machine__nf4' not in state_dict: raise ValueError(f'Supplied state dict for {param_name} does not contain `sapiens_machine__*` and possibly other `quantized_stats` components.')
            quantized_stats = {}
            for k, v in state_dict.items():
                if param_name + '.' in k and k.startswith(param_name):
                    quantized_stats[k] = v
                    if unexpected_keys is not None and k in unexpected_keys: unexpected_keys.remove(k)
            new_value = sapiens.nn.Params4bit.from_prequantized(data=param_value, quantized_stats=quantized_stats, requires_grad=False, device=target_device)
        else:
            new_value = param_value.to('cpu')
            kwargs = old_value.__dict__
            new_value = sapiens.nn.Params4bit(new_value, requires_grad=False, **kwargs).to(target_device)
        module._parameters[tensor_name] = new_value
    def check_quantized_param_shape(self, param_name, current_param, loaded_param):
        current_param_shape = current_param.shape
        loaded_param_shape = loaded_param.shape
        n = current_param_shape.numel()
        inferred_shape = (n,) if 'bias' in param_name else ((n + 1) // 2, 1)
        if loaded_param_shape != inferred_shape: raise ValueError(f'Expected the flattened shape of the current param ({param_name}) to be {loaded_param_shape} but is {inferred_shape}.')
        else: return True
    def adjust_max_memory(self, max_memory: Dict[str, Union[int, str]]) -> Dict[str, Union[int, str]]:
        max_memory = {key: val * 0.9 for key, val in max_memory.items()}
        return max_memory
    def update_torch_dtype(self, torch_dtype: 'torch.dtype') -> 'torch.dtype':
        if torch_dtype is None: torch_dtype = torch.float16
        return torch_dtype
    def _process_model_before_weight_loading(self, model: 'ModelMixin', device_map, keep_in_fp32_modules: List[str]=[], **kwargs):
        from .utils import replace_with_sapiens_linear
        load_in_8bit_fp32_cpu_offload = self.quantization_config.llm_int8_enable_fp32_cpu_offload
        self.modules_to_not_convert = self.quantization_config.llm_int8_skip_modules
        if not isinstance(self.modules_to_not_convert, list): self.modules_to_not_convert = [self.modules_to_not_convert]
        self.modules_to_not_convert.extend(keep_in_fp32_modules)
        if isinstance(device_map, dict) and len(device_map.keys()) > 1:
            keys_on_cpu = [key for key, value in device_map.items() if value in ['disk', 'cpu']]
            if len(keys_on_cpu) > 0 and (not load_in_8bit_fp32_cpu_offload): raise ValueError('If you want to offload some keys to `cpu` or `disk`, you need to set `llm_int8_enable_fp32_cpu_offload=True`. Note that these modules will not be  converted to 8-bit but kept in 32-bit.')
            self.modules_to_not_convert.extend(keys_on_cpu)
        self.modules_to_not_convert = [module for module in self.modules_to_not_convert if module is not None]
        model = replace_with_sapiens_linear(model, modules_to_not_convert=self.modules_to_not_convert, quantization_config=self.quantization_config)
        model.config.quantization_config = self.quantization_config
    def _process_model_after_weight_loading(self, model: 'ModelMixin', **kwargs):
        model.is_loaded_in_4bit = True
        model.is_4bit_serializable = self.is_serializable
        return model
    @property
    def is_serializable(self): return True
    @property
    def is_trainable(self) -> bool: return True
    def _dequantize(self, model):
        from .utils import dequantize_and_replace
        is_model_on_cpu = model.device.type == 'cpu'
        if is_model_on_cpu: model.to(torch.cuda.current_device())
        model = dequantize_and_replace(model, self.modules_to_not_convert, quantization_config=self.quantization_config)
        if is_model_on_cpu: model.to('cpu')
        return model
class Sapiens8BitDiffusersQuantizer(DiffusersQuantizer):
    use_keep_in_fp32_modules = True
    requires_calibration = False
    def __init__(self, quantization_config, **kwargs):
        super().__init__(quantization_config, **kwargs)
        if self.quantization_config.llm_int8_skip_modules is not None: self.modules_to_not_convert = self.quantization_config.llm_int8_skip_modules
    def validate_environment(self, *args, **kwargs):
        if not torch.cuda.is_available(): raise RuntimeError('No GPU found. A GPU is needed for quantization.')
        if not is_sapiens_accelerator_available() or is_sapiens_accelerator_version('<', '0.26.0'): raise ImportError("Using `sapiens_machine` 8-bit quantization requires SapiensAccelerator: `pip install 'sapiens_accelerator>=0.26.0'`")
        if not is_sapiens_machine_available() or is_sapiens_machine_version('<', '0.43.3'): raise ImportError('Using `sapiens_machine` 8-bit quantization requires the latest version of sapiens_machine: `pip install -U sapiens_machine`')
        if kwargs.get('from_flax', False): raise ValueError('Converting into 8-bit weights from flax weights is currently not supported, please make sure the weights are in PyTorch format.')
        device_map = kwargs.get('device_map', None)
        if device_map is not None and isinstance(device_map, dict) and (not self.quantization_config.llm_int8_enable_fp32_cpu_offload):
            device_map_without_no_convert = {key: device_map[key] for key in device_map.keys() if key not in self.modules_to_not_convert}
            if 'cpu' in device_map_without_no_convert.values() or 'disk' in device_map_without_no_convert.values(): raise ValueError('Some modules are dispatched on the CPU or the disk. Make sure you have enough GPU RAM to fit the quantized model. If you want to dispatch the model on the CPU or the disk while keeping these modules in 32-bit, you need to set `load_in_8bit_fp32_cpu_offload=True` and pass a custom `device_map` to `from_pretrained`. Check https://huggingface.co/docs/transformers/main/en/main_classes/quantization#offload-between-cpu-and-gpu for more details. ')
    def adjust_max_memory(self, max_memory: Dict[str, Union[int, str]]) -> Dict[str, Union[int, str]]:
        max_memory = {key: val * 0.9 for key, val in max_memory.items()}
        return max_memory
    def update_torch_dtype(self, torch_dtype: 'torch.dtype') -> 'torch.dtype':
        if torch_dtype is None: torch_dtype = torch.float16
        return torch_dtype
    def adjust_target_dtype(self, target_dtype: 'torch.dtype') -> 'torch.dtype': return torch.int8
    def check_if_quantized_param(self, model: 'ModelMixin', param_value: 'torch.Tensor', param_name: str, state_dict: Dict[str, Any], **kwargs):
        import sapiens_machine as sapiens
        module, tensor_name = get_module_from_name(model, param_name)
        if isinstance(module._parameters.get(tensor_name, None), sapiens.nn.Int8Params):
            if self.pre_quantized:
                if param_name.replace('weight', 'SCB') not in state_dict.keys(): raise ValueError('Missing quantization component `SCB`')
                if param_value.dtype != torch.int8: raise ValueError(f'Incompatible dtype `{param_value.dtype}` when loading 8-bit prequantized weight. Expected `torch.int8`.')
            return True
        return False
    def create_quantized_param(self, model: 'ModelMixin', param_value: 'torch.Tensor', param_name: str, target_device: 'torch.device', state_dict: Dict[str, Any], unexpected_keys: Optional[List[str]]=None):
        import sapiens_machine as sapiens
        fp16_statistics_key = param_name.replace('weight', 'SCB')
        fp16_weights_format_key = param_name.replace('weight', 'weight_format')
        fp16_statistics = state_dict.get(fp16_statistics_key, None)
        fp16_weights_format = state_dict.get(fp16_weights_format_key, None)
        module, tensor_name = get_module_from_name(model, param_name)
        if tensor_name not in module._parameters: raise ValueError(f'{module} does not have a parameter or a buffer named {tensor_name}.')
        old_value = getattr(module, tensor_name)
        if not isinstance(module._parameters[tensor_name], sapiens.nn.Int8Params): raise ValueError(f'Parameter `{tensor_name}` should only be a `sapiens.nn.Int8Params` instance.')
        if old_value.device == torch.device('meta') and target_device not in ['meta', torch.device('meta')] and (param_value is None): raise ValueError(f'{tensor_name} is on the meta device, we need a `value` to put in on {target_device}.')
        new_value = param_value.to('cpu')
        if self.pre_quantized and (not self.is_serializable): raise ValueError('Detected int8 weights but the version of sapiens_machine is not compatible with int8 serialization. Make sure to download the latest `sapiens_machine` version. `pip install --upgrade sapiens_machine`.')
        kwargs = old_value.__dict__
        new_value = sapiens.nn.Int8Params(new_value, requires_grad=False, **kwargs).to(target_device)
        module._parameters[tensor_name] = new_value
        if fp16_statistics is not None:
            setattr(module.weight, 'SCB', fp16_statistics.to(target_device))
            if unexpected_keys is not None: unexpected_keys.remove(fp16_statistics_key)
        if fp16_weights_format is not None and unexpected_keys is not None: unexpected_keys.remove(fp16_weights_format_key)
    def _process_model_after_weight_loading(self, model: 'ModelMixin', **kwargs):
        model.is_loaded_in_8bit = True
        model.is_8bit_serializable = self.is_serializable
        return model
    def _process_model_before_weight_loading(self, model: 'ModelMixin', device_map, keep_in_fp32_modules: List[str]=[], **kwargs):
        from .utils import replace_with_sapiens_linear
        load_in_8bit_fp32_cpu_offload = self.quantization_config.llm_int8_enable_fp32_cpu_offload
        self.modules_to_not_convert = self.quantization_config.llm_int8_skip_modules
        if not isinstance(self.modules_to_not_convert, list): self.modules_to_not_convert = [self.modules_to_not_convert]
        self.modules_to_not_convert.extend(keep_in_fp32_modules)
        if isinstance(device_map, dict) and len(device_map.keys()) > 1:
            keys_on_cpu = [key for key, value in device_map.items() if value in ['disk', 'cpu']]
            if len(keys_on_cpu) > 0 and (not load_in_8bit_fp32_cpu_offload): raise ValueError('If you want to offload some keys to `cpu` or `disk`, you need to set `llm_int8_enable_fp32_cpu_offload=True`. Note that these modules will not be  converted to 8-bit but kept in 32-bit.')
            self.modules_to_not_convert.extend(keys_on_cpu)
        self.modules_to_not_convert = [module for module in self.modules_to_not_convert if module is not None]
        model = replace_with_sapiens_linear(model, modules_to_not_convert=self.modules_to_not_convert, quantization_config=self.quantization_config)
        model.config.quantization_config = self.quantization_config
    @property
    def is_serializable(self): return True
    @property
    def is_trainable(self) -> bool: return True
    def _dequantize(self, model):
        from .utils import dequantize_and_replace
        model = dequantize_and_replace(model, self.modules_to_not_convert, quantization_config=self.quantization_config)
        return model
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
