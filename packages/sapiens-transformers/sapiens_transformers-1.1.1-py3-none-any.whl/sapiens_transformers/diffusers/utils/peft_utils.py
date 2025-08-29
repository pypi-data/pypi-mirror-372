'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import collections
import importlib
from typing import Optional
from packaging import version
from .import_utils import is_peft_available, is_torch_available
if is_torch_available(): import torch
def recurse_remove_peft_layers(model):
    from peft.tuners.tuners_utils import BaseTunerLayer
    has_base_layer_pattern = False
    for module in model.modules():
        if isinstance(module, BaseTunerLayer):
            has_base_layer_pattern = hasattr(module, 'base_layer')
            break
    if has_base_layer_pattern:
        from peft.utils import _get_submodules
        key_list = [key for key, _ in model.named_modules() if 'lora' not in key]
        for key in key_list:
            try: parent, target, target_name = _get_submodules(model, key)
            except AttributeError: continue
            if hasattr(target, 'base_layer'): setattr(parent, target_name, target.get_base_layer())
    else:
        from peft.tuners.lora import LoraLayer
        for name, module in model.named_children():
            if len(list(module.children())) > 0: recurse_remove_peft_layers(module)
            module_replaced = False
            if isinstance(module, LoraLayer) and isinstance(module, torch.nn.Linear):
                new_module = torch.nn.Linear(module.in_features, module.out_features, bias=module.bias is not None).to(module.weight.device)
                new_module.weight = module.weight
                if module.bias is not None: new_module.bias = module.bias
                module_replaced = True
            elif isinstance(module, LoraLayer) and isinstance(module, torch.nn.Conv2d):
                new_module = torch.nn.Conv2d(module.in_channels, module.out_channels, module.kernel_size, module.stride, module.padding, module.dilation, module.groups).to(module.weight.device)
                new_module.weight = module.weight
                if module.bias is not None: new_module.bias = module.bias
                module_replaced = True
            if module_replaced:
                setattr(model, name, new_module)
                del module
                if torch.cuda.is_available(): torch.cuda.empty_cache()
    return model
def scale_lora_layers(model, weight):
    """Args:"""
    from peft.tuners.tuners_utils import BaseTunerLayer
    if weight == 1.0: return
    for module in model.modules():
        if isinstance(module, BaseTunerLayer): module.scale_layer(weight)
def unscale_lora_layers(model, weight: Optional[float]=None):
    """Args:"""
    from peft.tuners.tuners_utils import BaseTunerLayer
    if weight is None or weight == 1.0: return
    for module in model.modules():
        if isinstance(module, BaseTunerLayer):
            if weight != 0: module.unscale_layer(weight)
            else:
                for adapter_name in module.active_adapters: module.set_scale(adapter_name, 1.0)
def get_peft_kwargs(rank_dict, network_alpha_dict, peft_state_dict, is_unet=True):
    rank_pattern = {}
    alpha_pattern = {}
    r = lora_alpha = list(rank_dict.values())[0]
    if len(set(rank_dict.values())) > 1:
        r = collections.Counter(rank_dict.values()).most_common()[0][0]
        rank_pattern = dict(filter(lambda x: x[1] != r, rank_dict.items()))
        rank_pattern = {k.split('.lora_B.')[0]: v for k, v in rank_pattern.items()}
    if network_alpha_dict is not None and len(network_alpha_dict) > 0:
        if len(set(network_alpha_dict.values())) > 1:
            lora_alpha = collections.Counter(network_alpha_dict.values()).most_common()[0][0]
            alpha_pattern = dict(filter(lambda x: x[1] != lora_alpha, network_alpha_dict.items()))
            if is_unet: alpha_pattern = {'.'.join(k.split('.lora_A.')[0].split('.')).replace('.alpha', ''): v for k, v in alpha_pattern.items()}
            else: alpha_pattern = {'.'.join(k.split('.down.')[0].split('.')[:-1]): v for k, v in alpha_pattern.items()}
        else: lora_alpha = set(network_alpha_dict.values()).pop()
    target_modules = list({name.split('.lora')[0] for name in peft_state_dict.keys()})
    use_dora = any(('lora_magnitude_vector' in k for k in peft_state_dict))
    lora_bias = any(('lora_B' in k and k.endswith('.bias') for k in peft_state_dict))
    lora_config_kwargs = {'r': r, 'lora_alpha': lora_alpha, 'rank_pattern': rank_pattern, 'alpha_pattern': alpha_pattern, 'target_modules': target_modules, 'use_dora': use_dora, 'lora_bias': lora_bias}
    return lora_config_kwargs
def get_adapter_name(model):
    from peft.tuners.tuners_utils import BaseTunerLayer
    for module in model.modules():
        if isinstance(module, BaseTunerLayer): return f'default_{len(module.r)}'
    return 'default_0'
def set_adapter_layers(model, enabled=True):
    from peft.tuners.tuners_utils import BaseTunerLayer
    for module in model.modules():
        if isinstance(module, BaseTunerLayer):
            if hasattr(module, 'enable_adapters'): module.enable_adapters(enabled=enabled)
            else: module.disable_adapters = not enabled
def delete_adapter_layers(model, adapter_name):
    from peft.tuners.tuners_utils import BaseTunerLayer
    for module in model.modules():
        if isinstance(module, BaseTunerLayer):
            if hasattr(module, 'delete_adapter'): module.delete_adapter(adapter_name)
            else: raise ValueError('The version of PEFT you are using is not compatible, please use a version that is greater than 0.6.1')
    if getattr(model, '_hf_peft_config_loaded', False) and hasattr(model, 'peft_config'):
        model.peft_config.pop(adapter_name, None)
        if len(model.peft_config) == 0:
            del model.peft_config
            model._hf_peft_config_loaded = None
def set_weights_and_activate_adapters(model, adapter_names, weights):
    from peft.tuners.tuners_utils import BaseTunerLayer
    def get_module_weight(weight_for_adapter, module_name):
        if not isinstance(weight_for_adapter, dict): return weight_for_adapter
        for layer_name, weight_ in weight_for_adapter.items():
            if layer_name in module_name: return weight_
        parts = module_name.split('.')
        key = f'{parts[0]}.{parts[1]}.attentions.{parts[3]}'
        block_weight = weight_for_adapter.get(key, 1.0)
        return block_weight
    for adapter_name, weight in zip(adapter_names, weights):
        for module_name, module in model.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, 'set_adapter'): module.set_adapter(adapter_name)
                else: module.active_adapter = adapter_name
                module.set_scale(adapter_name, get_module_weight(weight, module_name))
    for module in model.modules():
        if isinstance(module, BaseTunerLayer):
            if hasattr(module, 'set_adapter'): module.set_adapter(adapter_names)
            else: module.active_adapter = adapter_names
def check_peft_version(min_version: str) -> None:
    """Args:"""
    if not is_peft_available(): raise ValueError('PEFT is not installed. Please install it with `pip install peft`')
    is_peft_version_compatible = version.parse(importlib.metadata.version('peft')) > version.parse(min_version)
    if not is_peft_version_compatible: raise ValueError(f'The version of PEFT you are using is not compatible, please use a version that is greater than {min_version}')
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
