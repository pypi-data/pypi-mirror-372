"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import SAPIENS_ACCELERATOR_MIN_VERSION, is_sapiens_accelerator_available, is_aqlm_available, is_torch_available
if is_torch_available(): import torch.nn as nn
def replace_with_aqlm_linear(model, quantization_config=None, linear_weights_not_to_quantize=None, current_key_name=None, has_been_replaced=False):
    if not is_aqlm_available(): raise ValueError("AQLM is not available. Please install it with `pip install aqlm[cpu,gpu]`")
    if not is_sapiens_accelerator_available(): raise ValueError(f"AQLM requires SapiensAccelerator to be installed: `pip install 'sapiens_accelerator>={SAPIENS_ACCELERATOR_MIN_VERSION}'`")
    if linear_weights_not_to_quantize is None: linear_weights_not_to_quantize = []
    from sapiens_accelerator import init_empty_weights
    from aqlm import QuantizedLinear
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, nn.Linear):
            if ".".join(current_key_name) + ".weight" not in linear_weights_not_to_quantize:
                with init_empty_weights():
                    in_features = module.in_features
                    out_features = module.out_features
                    model._modules[name] = QuantizedLinear(in_features, out_features, bias=module.bias is not None, in_group_size=quantization_config.in_group_size,
                    out_group_size=quantization_config.out_group_size, num_codebooks=quantization_config.num_codebooks, nbits_per_codebook=quantization_config.nbits_per_codebook)
                    has_been_replaced = True
                    model._modules[name].source_cls = type(module)
                    model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0: _, has_been_replaced = replace_with_aqlm_linear(module, quantization_config=quantization_config,
        linear_weights_not_to_quantize=linear_weights_not_to_quantize, current_key_name=current_key_name, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
