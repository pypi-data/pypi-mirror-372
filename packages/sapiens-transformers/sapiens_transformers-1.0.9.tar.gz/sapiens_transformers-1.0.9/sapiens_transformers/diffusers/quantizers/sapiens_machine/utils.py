'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from inspect import signature
from typing import Union
from ...utils import is_sapiens_accelerator_available, is_sapiens_machine_available, is_torch_available
from ..quantization_config import QuantizationMethod
if is_torch_available():
    import torch
    import torch.nn as nn
if is_sapiens_machine_available(): import sapiens_machine as sapiens
if is_sapiens_accelerator_available():
    import sapiens_accelerator
    from sapiens_accelerator import init_empty_weights
    from sapiens_accelerator.hooks import add_hook_to_module, remove_hook_from_module
def _replace_with_sapiens_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False):
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, nn.Linear) and name not in modules_to_not_convert:
            current_key_name_str = '.'.join(current_key_name)
            if not any((key + '.' in current_key_name_str or key == current_key_name_str for key in modules_to_not_convert)):
                with init_empty_weights():
                    in_features = module.in_features
                    out_features = module.out_features
                    if quantization_config.quantization_method() == 'llm_int8':
                        model._modules[name] = sapiens.nn.Linear8bitLt(in_features, out_features, module.bias is not None,
                        has_fp16_weights=quantization_config.llm_int8_has_fp16_weight, threshold=quantization_config.llm_int8_threshold)
                        has_been_replaced = True
                    elif quantization_config.llm_int8_skip_modules is not None and name in quantization_config.llm_int8_skip_modules: pass
                    else:
                        extra_kwargs = {'quant_storage': quantization_config.sapiens_4bit_quant_storage} if 'quant_storage' in list(signature(sapiens.nn.Linear4bit).parameters) else {}
                        model._modules[name] = sapiens.nn.Linear4bit(in_features, out_features, module.bias is not None, quantization_config.sapiens_4bit_compute_dtype,
                        compress_statistics=quantization_config.sapiens_4bit_use_double_quant, quant_type=quantization_config.sapiens_4bit_quant_type, **extra_kwargs)
                        has_been_replaced = True
                    model._modules[name].source_cls = type(module)
                    model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0: _, has_been_replaced = _replace_with_sapiens_linear(module, modules_to_not_convert,
        current_key_name, quantization_config, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return (model, has_been_replaced)
def replace_with_sapiens_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None):
    model, has_been_replaced = _replace_with_sapiens_linear(model, modules_to_not_convert, current_key_name, quantization_config)
    return model
def dequantize_sapiens_weight(weight: 'torch.nn.Parameter', state=None):
    if not isinstance(weight, torch.nn.Parameter): raise TypeError(f'Input weight should be of type nn.Parameter, got {type(weight)} instead')
    cls_name = weight.__class__.__name__
    if cls_name not in ('Params4bit', 'Int8Params'): return weight
    if cls_name == 'Params4bit':
        output_tensor = sapiens.functional.dequantize_4bit(weight.data, weight.quant_state)
        return output_tensor
    if state.SCB is None: state.SCB = weight.SCB
    im = torch.eye(weight.data.shape[-1]).contiguous().half().to(weight.device)
    im, imt, SCim, SCimt, coo_tensorim = sapiens.functional.double_quant(im)
    im, Sim = sapiens.functional.transform(im, 'col32')
    if state.CxB is None: state.CxB, state.SB = sapiens.functional.transform(weight.data, to_order=state.formatB)
    out32, Sout32 = sapiens.functional.igemmlt(im, state.CxB, Sim, state.SB)
    return sapiens.functional.mm_dequant(out32, Sout32, SCim, state.SCB, bias=None).t()
def _create_sapiens_accelerator_new_hook(old_hook):
    old_hook_cls = getattr(sapiens_accelerator.hooks, old_hook.__class__.__name__)
    old_hook_attr = old_hook.__dict__
    filtered_old_hook_attr = {}
    old_hook_init_signature = inspect.signature(old_hook_cls.__init__)
    for k in old_hook_attr.keys():
        if k in old_hook_init_signature.parameters: filtered_old_hook_attr[k] = old_hook_attr[k]
    new_hook = old_hook_cls(**filtered_old_hook_attr)
    return new_hook
def _dequantize_and_replace(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False):
    quant_method = quantization_config.quantization_method()
    target_cls = sapiens.nn.Linear8bitLt if quant_method == 'llm_int8' else sapiens.nn.Linear4bit
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, target_cls) and name not in modules_to_not_convert:
            current_key_name_str = '.'.join(current_key_name)
            if not any((key + '.' in current_key_name_str or key == current_key_name_str for key in modules_to_not_convert)):
                bias = getattr(module, 'bias', None)
                device = module.weight.device
                with init_empty_weights(): new_module = torch.nn.Linear(module.in_features, module.out_features, bias=bias is not None)
                if quant_method == 'llm_int8': state = module.state
                else: state = None
                new_module.weight = torch.nn.Parameter(dequantize_sapiens_weight(module.weight, state))
                if bias is not None: new_module.bias = bias
                if hasattr(module, '_hf_hook'):
                    old_hook = module._hf_hook
                    new_hook = _create_sapiens_accelerator_new_hook(old_hook)
                    remove_hook_from_module(module)
                    add_hook_to_module(new_module, new_hook)
                new_module.to(device)
                model._modules[name] = new_module
                has_been_replaced = True
        if len(list(module.children())) > 0: _, has_been_replaced = _dequantize_and_replace(module, modules_to_not_convert,
        current_key_name, quantization_config, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return (model, has_been_replaced)
def dequantize_and_replace(model, modules_to_not_convert=None, quantization_config=None):
    model, has_been_replaced = _dequantize_and_replace(model, modules_to_not_convert=modules_to_not_convert, quantization_config=quantization_config)
    return model
def _check_sapiens_status(module) -> Union[bool, bool]:
    is_loaded_in_4bit_sapiens = hasattr(module, 'is_loaded_in_4bit') and module.is_loaded_in_4bit and (getattr(module, 'quantization_method', None) == QuantizationMethod.SAPIENS_MACHINE)
    is_loaded_in_8bit_sapiens = hasattr(module, 'is_loaded_in_8bit') and module.is_loaded_in_8bit and (getattr(module, 'quantization_method', None) == QuantizationMethod.SAPIENS_MACHINE)
    return (is_loaded_in_4bit_sapiens or is_loaded_in_8bit_sapiens, is_loaded_in_4bit_sapiens, is_loaded_in_8bit_sapiens)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
