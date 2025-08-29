"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib.metadata
import inspect
import warnings
from copy import deepcopy
from inspect import signature
from packaging import version
from ..utils import (get_available_devices, is_sapiens_accelerator_available, is_sapiens_machine_available, is_sapiens_machine_multi_backend_available, is_ipex_available, is_torch_available, logging)
if is_sapiens_machine_available():
    import sapiens_machine as sapiens
    import torch
    import torch.nn as nn
    from ..pytorch_utils import Conv1D
if is_sapiens_accelerator_available():
    import sapiens_accelerator
    from sapiens_accelerator import init_empty_weights
    from sapiens_accelerator.hooks import add_hook_to_module, remove_hook_from_module
    from sapiens_accelerator.utils import find_tied_parameters
logger = logging.get_logger(__name__)
def set_module_quantized_tensor_to_device(module, tensor_name, device, value=None, quantized_stats=None):
    if "." in tensor_name:
        splits = tensor_name.split(".")
        for split in splits[:-1]:
            new_module = getattr(module, split)
            if new_module is None: raise ValueError(f"{module} has no attribute {split}.")
            module = new_module
        tensor_name = splits[-1]
    if tensor_name not in module._parameters and tensor_name not in module._buffers: raise ValueError(f"{module} does not have a parameter or a buffer named {tensor_name}.")
    is_buffer = tensor_name in module._buffers
    old_value = getattr(module, tensor_name)
    if old_value.device == torch.device("meta") and device not in ["meta", torch.device("meta")] and value is None: raise ValueError(f"{tensor_name} is on the meta device, we need a `value` to put in on {device}.")
    prequantized_loading = quantized_stats is not None
    if is_buffer or not is_sapiens_machine_available():
        is_8bit = False
        is_4bit = False
    else:
        is_4bit = hasattr(sapiens.nn, "Params4bit") and isinstance(module._parameters[tensor_name], sapiens.nn.Params4bit)
        is_8bit = isinstance(module._parameters[tensor_name], sapiens.nn.Int8Params)
    if is_8bit or is_4bit:
        param = module._parameters[tensor_name]
        if param.device.type != "cuda":
            if value is None: new_value = old_value.to(device)
            elif isinstance(value, torch.Tensor): new_value = value.to("cpu")
            else: new_value = torch.tensor(value, device="cpu")
            if issubclass(module.source_cls, Conv1D) and not prequantized_loading: new_value = new_value.T
            kwargs = old_value.__dict__
            if prequantized_loading != (new_value.dtype in (torch.int8, torch.uint8)): raise ValueError(f"Value dtype `{new_value.dtype}` is not compatible with parameter quantization status.")
            if is_8bit:
                is_8bit_serializable = version.parse(importlib.metadata.version("sapiens_machine")) > version.parse("0.0.0")
                if new_value.dtype in (torch.int8, torch.uint8) and not is_8bit_serializable: raise ValueError("Detected int8 weights but the version of sapiens_machine is not compatible with int8 serialization. Make sure to download the latest `sapiens_machine` version. `pip install --upgrade sapiens_machine`.")
                new_value = sapiens.nn.Int8Params(new_value, requires_grad=False, **kwargs).to(device)
                if prequantized_loading: setattr(new_value, "SCB", quantized_stats["SCB"].to(device))
            elif is_4bit:
                if prequantized_loading:
                    is_4bit_serializable = version.parse(importlib.metadata.version("sapiens_machine")) >= version.parse("1.0.0")
                    if new_value.dtype in (torch.int8, torch.uint8) and not is_4bit_serializable: raise ValueError("Detected 4-bit weights but the version of sapiens_machine is not compatible with 4-bit serialization. Make sure to download the latest `sapiens_machine` version. `pip install --upgrade sapiens_machine`.")
                    new_value = sapiens.nn.Params4bit.from_prequantized(data=new_value, quantized_stats=quantized_stats, requires_grad=False, device=device, **kwargs)
                else: new_value = sapiens.nn.Params4bit(new_value, requires_grad=False, **kwargs).to(device)
            module._parameters[tensor_name] = new_value
    else:
        if value is None: new_value = old_value.to(device)
        elif isinstance(value, torch.Tensor): new_value = value.to(device)
        else: new_value = torch.tensor(value, device=device)
        if is_buffer: module._buffers[tensor_name] = new_value
        else:
            new_value = nn.Parameter(new_value, requires_grad=old_value.requires_grad)
            module._parameters[tensor_name] = new_value
def _replace_with_sapiens_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False):
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if (isinstance(module, nn.Linear) or isinstance(module, Conv1D)) and name not in modules_to_not_convert:
            current_key_name_str = ".".join(current_key_name)
            if not any((key + "." in current_key_name_str) or (key == current_key_name_str) for key in modules_to_not_convert):
                with init_empty_weights():
                    if isinstance(module, Conv1D): in_features, out_features = module.weight.shape
                    else:
                        in_features = module.in_features
                        out_features = module.out_features
                    if quantization_config.quantization_method() == "llm_int8":
                        model._modules[name] = sapiens.nn.Linear8bitLt(in_features, out_features, module.bias is not None, has_fp16_weights=quantization_config.llm_int8_has_fp16_weight, threshold=quantization_config.llm_int8_threshold)
                        has_been_replaced = True
                    else:
                        if (quantization_config.llm_int8_skip_modules is not None and name in quantization_config.llm_int8_skip_modules): pass
                        else:
                            extra_kwargs = ({"quant_storage": quantization_config.sapiens_4bit_quant_storage} if "quant_storage" in list(signature(sapiens.nn.Linear4bit).parameters) else {})
                            model._modules[name] = sapiens.nn.Linear4bit(in_features, out_features, module.bias is not None, quantization_config.sapiens_4bit_compute_dtype, compress_statistics=quantization_config.sapiens_4bit_use_double_quant, quant_type=quantization_config.sapiens_4bit_quant_type, **extra_kwargs)
                            has_been_replaced = True
                    model._modules[name].source_cls = type(module)
                    model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0: _, has_been_replaced = _replace_with_sapiens_linear(module, modules_to_not_convert, current_key_name, quantization_config, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
def replace_with_sapiens_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None):
    modules_to_not_convert = ["lm_head"] if modules_to_not_convert is None else modules_to_not_convert
    model, has_been_replaced = _replace_with_sapiens_linear(model, modules_to_not_convert, current_key_name, quantization_config)
    if not has_been_replaced: logger.warning("You are loading your model in 8bit or 4bit but no linear modules were found in your model. Please double check your model architecture, or submit an issue on github if you think this is a bug.")
    return model
def replace_8bit_linear(*args, **kwargs):
    warnings.warn("`replace_8bit_linear` will be deprecated in a future version, please use `replace_with_sapiens_linear` instead", FutureWarning)
    return replace_with_sapiens_linear(*args, **kwargs)
def set_module_8bit_tensor_to_device(*args, **kwargs):
    warnings.warn("`set_module_8bit_tensor_to_device` will be deprecated in a future version, please use `set_module_quantized_tensor_to_device` instead", FutureWarning)
    return set_module_quantized_tensor_to_device(*args, **kwargs)
def get_keys_to_not_convert(model):
    tied_model = deepcopy(model)
    tied_model.tie_weights()
    tied_params = find_tied_parameters(tied_model)
    if isinstance(tied_params, dict): tied_keys = sum(list(tied_params.values()), []) + list(tied_params.keys())
    else: tied_keys = sum(tied_params, [])
    has_tied_params = len(tied_keys) > 0
    if not has_tied_params:
        output_emb = model.get_output_embeddings()
        if output_emb is not None:
            list_last_module = [name for name, module in model.named_modules() if id(module) == id(output_emb)]
            return list_last_module
    list_modules = list(model.named_parameters())
    list_last_module = [list_modules[-1][0]]
    intersection = set(list_last_module) - set(tied_keys)
    list_untouched = list(set(tied_keys)) + list(intersection)
    names_to_remove = [".weight", ".bias"]
    filtered_module_names = []
    for name in list_untouched:
        for name_to_remove in names_to_remove:
            if name_to_remove in name: name = name.replace(name_to_remove, "")
        filtered_module_names.append(name)
    return filtered_module_names
def dequantize_sapiens_weight(weight: "torch.nn.Parameter", dtype: "torch.dtype", state=None):
    if not isinstance(weight, torch.nn.Parameter): raise TypeError(f"Input weight should be of type nn.Parameter, got {type(weight)} instead")
    cls_name = weight.__class__.__name__
    if cls_name not in ("Params4bit", "Int8Params"): return weight
    if cls_name == "Params4bit":
        output_tensor = sapiens.functional.dequantize_4bit(weight.data, weight.quant_state)
        logger.warning_once(f"The model is going to be dequantized in {output_tensor.dtype} - if you want to upcast it to another dtype, make sure to pass the desired dtype when quantizing the model through `sapiens_4bit_quant_type` argument of `SapiensMachineConfig`")
        return output_tensor.to(dtype)
    if state.SCB is None: state.SCB = weight.SCB
    im = torch.eye(weight.data.shape[-1]).contiguous().half().to(weight.device)
    im, imt, SCim, SCimt, coo_tensorim = sapiens.functional.double_quant(im)
    im, Sim = sapiens.functional.transform(im, "col32")
    if state.CxB is None: state.CxB, state.SB = sapiens.functional.transform(weight.data, to_order=state.formatB)
    out32, Sout32 = sapiens.functional.igemmlt(im, state.CxB, Sim, state.SB)
    return sapiens.functional.mm_dequant(out32, Sout32, SCim, state.SCB, bias=None).t().to(dtype)
def _create_sapiens_accelerator_new_hook(old_hook):
    old_hook_cls = getattr(sapiens_accelerator.hooks, old_hook.__class__.__name__)
    old_hook_attr = old_hook.__dict__
    filtered_old_hook_attr = {}
    old_hook_init_signature = inspect.signature(old_hook_cls.__init__)
    for k in old_hook_attr.keys():
        if k in old_hook_init_signature.parameters: filtered_old_hook_attr[k] = old_hook_attr[k]
    new_hook = old_hook_cls(**filtered_old_hook_attr)
    return new_hook
def _dequantize_and_replace(model, dtype, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False):
    quant_method = quantization_config.quantization_method()
    target_cls = sapiens.nn.Linear8bitLt if quant_method == "llm_int8" else sapiens.nn.Linear4bit
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, target_cls) and name not in modules_to_not_convert:
            current_key_name_str = ".".join(current_key_name)
            if not any((key + "." in current_key_name_str) or (key == current_key_name_str) for key in modules_to_not_convert):
                bias = getattr(module, "bias", None)
                device = module.weight.device
                with init_empty_weights(): new_module = torch.nn.Linear(module.in_features, module.out_features, bias=bias is not None)
                if quant_method == "llm_int8": state = module.state
                else: state = None
                new_module.weight = torch.nn.Parameter(dequantize_sapiens_weight(module.weight, dtype, state))
                if bias is not None: new_module.bias = bias
                if hasattr(module, "_hf_hook"):
                    old_hook = module._hf_hook
                    new_hook = _create_sapiens_accelerator_new_hook(old_hook)
                    remove_hook_from_module(module)
                    add_hook_to_module(new_module, new_hook)
                new_module.to(device)
                model._modules[name] = new_module
                has_been_replaced = True
        if len(list(module.children())) > 0: _, has_been_replaced = _dequantize_and_replace(module, dtype, modules_to_not_convert, current_key_name, quantization_config, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
def dequantize_and_replace(model, modules_to_not_convert=None, quantization_config=None):
    model, has_been_replaced = _dequantize_and_replace(model, model.dtype, modules_to_not_convert=modules_to_not_convert, quantization_config=quantization_config)
    if not has_been_replaced: logger.warning("For some reason the model has not been properly dequantized. You might see unexpected behavior.")
    return model
def _validate_sapiens_multi_backend_availability(raise_exception):
    import sapiens_machine as sapiens
    sapiens_supported_devices = getattr(sapiens, "supported_torch_devices", set())
    available_devices = get_available_devices()
    if available_devices == {"cpu"} and not is_ipex_available():
        from importlib.util import find_spec
        if find_spec("intel_extension_for_pytorch"): logger.warning("You have Intel IPEX installed but if you're intending to use it for CPU, it might not have the right version. Be sure to double check that your PyTorch and IPEX installs are compatible.")
        available_devices.discard("cpu")
    if not available_devices.intersection(sapiens_supported_devices):
        if raise_exception:
            sapiens_supported_devices_with_info = set('"cpu" (needs an Intel CPU and intel_extension_for_pytorch installed and compatible with the PyTorch version)' if device == "cpu" else device for device in sapiens_supported_devices)
            err_msg = (f"None of the available devices `available_devices = {available_devices or None}` are supported by the sapiens_machine version you have installed: `sapiens_supported_devices = {sapiens_supported_devices_with_info}`.")
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        logger.warning("No supported devices found for sapiens_machine multi-backend.")
        return False
    logger.debug("Multi-backend validation successful.")
    return True
def _validate_sapiens_cuda_backend_availability(raise_exception):
    if not is_torch_available(): return False
    import torch
    if not torch.cuda.is_available():
        log_msg = ("CUDA is required but not available for sapiens_machine. Please consider installing the multi-platform enabled version of sapiens_machine, which is currently a work in progress.")
        if raise_exception:
            logger.error(log_msg)
            raise RuntimeError(log_msg)
        logger.warning(log_msg)
        return False
    logger.debug("CUDA backend validation successful.")
    return True
def validate_sapiens_backend_availability(raise_exception=False):
    if not is_sapiens_machine_available():
        if importlib.util.find_spec("sapiens_machine") and version.parse(importlib.metadata.version("sapiens_machine")) < version.parse("0.0.1"): return _validate_sapiens_cuda_backend_availability(raise_exception)
        return False
    if is_sapiens_machine_multi_backend_available(): return _validate_sapiens_multi_backend_availability(raise_exception)
    return _validate_sapiens_cuda_backend_availability(raise_exception)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
