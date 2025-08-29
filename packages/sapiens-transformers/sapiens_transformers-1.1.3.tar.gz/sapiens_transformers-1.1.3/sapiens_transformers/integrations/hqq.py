"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import is_hqq_available, is_torch_available, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
def autoname_modules(model):
    for name, module in model.named_modules(): module.name = name
def name_to_linear_tag(name): return ".".join([n for n in name.split(".") if ((n not in ["model", "layers"]) and (not n.isnumeric()))])
def get_linear_tags(model):
    if is_hqq_available(): from hqq.core.quantize import HQQLinear
    linear_tags = set()
    for name, module in model.named_modules():
        if isinstance(module, (torch.nn.Linear, HQQLinear)): linear_tags.add(name_to_linear_tag(name))
    return list(linear_tags)
def _prepare_for_hqq_linear(model, patch_params, has_been_replaced, current_key_name=None):
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, torch.nn.Linear):
            linear_tag = name_to_linear_tag(module.name)
            if linear_tag in patch_params:
                if patch_params[linear_tag] is not None:
                    model._modules[name].quant_config = patch_params[linear_tag]
                    model._modules[name].source_cls = type(module)
                    model._modules[name].requires_grad_(False)
            has_been_replaced = True
        if len(list(module.children())) > 0: _, has_been_replaced = _prepare_for_hqq_linear(module, patch_params=patch_params, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
def prepare_for_hqq_linear(model, quantization_config=None, modules_to_not_convert=None, has_been_replaced=False):
    modules_to_not_convert = [] if modules_to_not_convert is None else modules_to_not_convert
    autoname_modules(model)
    linear_tags = get_linear_tags(model)
    skip_modules = quantization_config.skip_modules
    quant_config = quantization_config.to_dict()
    linear_tags = list(set(linear_tags) - set(skip_modules) - set(modules_to_not_convert))
    if any(key in linear_tags for key in quant_config.keys()):
        patch_params = {key: None for key in linear_tags}
        patch_params.update(quant_config)
    else: patch_params = {k: quant_config for k in linear_tags}
    model, has_been_replaced = _prepare_for_hqq_linear(model, patch_params=patch_params, has_been_replaced=has_been_replaced)
    model.config.quantization_config = patch_params
    if not has_been_replaced: logger.warning("No linear modules were found in your model for quantization.")
    return model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
