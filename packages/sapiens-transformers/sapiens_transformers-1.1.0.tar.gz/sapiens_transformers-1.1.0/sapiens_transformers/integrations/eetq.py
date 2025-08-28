"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import is_sapiens_accelerator_available, is_eetq_available, logging
if is_eetq_available():
    import eetq
    import torch.nn as nn
if is_sapiens_accelerator_available(): from sapiens_accelerator import init_empty_weights
logger = logging.get_logger(__name__)
def _replace_with_eetq_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False, pre_quantized=False):
    if current_key_name is None: current_key_name = []
    for name, module in model.named_children():
        current_key_name.append(name)
        if (isinstance(module, nn.Linear)) and name not in modules_to_not_convert:
            current_key_name_str = ".".join(current_key_name)
            if not any((key + "." in current_key_name_str) or (key == current_key_name_str) for key in modules_to_not_convert):
                with init_empty_weights():
                    in_features = module.in_features
                    out_features = module.out_features
                    model._modules[name] = eetq.EetqLinear(in_features, out_features, module.bias is not None, module.weight.device)
                    if pre_quantized: model._modules[name].register_scale(module.weight.device)
                    has_been_replaced = True
                    model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0: _, has_been_replaced = _replace_with_eetq_linear(module, modules_to_not_convert, current_key_name, quantization_config, has_been_replaced=has_been_replaced, pre_quantized=pre_quantized)
        current_key_name.pop(-1)
    return model, has_been_replaced
def replace_with_eetq_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, pre_quantized=False):
    modules_to_not_convert = ["lm_head"] if modules_to_not_convert is None else modules_to_not_convert
    if quantization_config.modules_to_not_convert is not None: modules_to_not_convert.extend(quantization_config.modules_to_not_convert)
    modules_to_not_convert = list(set(modules_to_not_convert))
    model, has_been_replaced = _replace_with_eetq_linear(model, modules_to_not_convert, current_key_name, quantization_config, pre_quantized=pre_quantized)
    if not has_been_replaced: logger.warning("You are loading your model using eetq but no linear modules were found in your model. Please double check your model architecture, or submit an issue on github if you think this is a bug.")
    return model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
