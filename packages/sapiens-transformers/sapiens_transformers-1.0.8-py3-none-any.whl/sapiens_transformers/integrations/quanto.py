"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import is_torch_available
if is_torch_available(): import torch
def replace_with_quanto_layers(model, quantization_config=None, modules_to_not_convert=None, current_key_name=None, has_been_replaced=False):
    from sapiens_accelerator import init_empty_weights
    from quanto import QLayerNorm, QLinear, qfloat8, qint2, qint4, qint8
    w_mapping = {"float8": qfloat8, "int8": qint8, "int4": qint4, "int2": qint2}
    a_mapping = {None: None, "float8": qfloat8, "int8": qint8}
    if modules_to_not_convert is None: modules_to_not_convert = []
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if not any(key in ".".join(current_key_name) for key in modules_to_not_convert):
            with init_empty_weights():
                if isinstance(module, torch.nn.Linear):
                    model._modules[name] = QLinear(in_features=module.in_features, out_features=module.out_features, bias=module.bias is not None, dtype=module.weight.dtype, weights=w_mapping[quantization_config.weights], activations=a_mapping[quantization_config.activations])
                    model._modules[name].requires_grad_(False)
                    has_been_replaced = True
                elif isinstance(module, torch.nn.LayerNorm):
                    if quantization_config.activations is not None:
                        model._modules[name] = QLayerNorm(module.normalized_shape, module.eps, module.elementwise_affine, module.bias is not None, activations=a_mapping[quantization_config.activations])
                        has_been_replaced = True
        if len(list(module.children())) > 0: _, has_been_replaced = replace_with_quanto_layers(module, quantization_config=quantization_config, modules_to_not_convert=modules_to_not_convert, current_key_name=current_key_name, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
