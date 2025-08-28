"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..utils import is_sapiens_accelerator_available, is_fbgemm_gpu_available, is_torch_available, logging
if is_torch_available():
    import torch
    from torch import nn
if is_sapiens_accelerator_available(): from sapiens_accelerator import init_empty_weights
if is_fbgemm_gpu_available(): import fbgemm_gpu.experimental.gen_ai
logger = logging.get_logger(__name__)
class FbgemmFp8Linear(torch.nn.Module):
    def __init__(self, in_features, out_features, bias, weight_dtype=torch.float32):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.register_buffer("weight", torch.zeros((out_features, in_features), dtype=torch.float8_e4m3fn))
        self.register_buffer("weight_scale", torch.zeros((out_features, 1), dtype=weight_dtype))
        self.register_buffer("input_scale_ub", torch.zeros([1], dtype=torch.float), persistent=False)
        if bias: self.register_buffer("bias", torch.zeros((self.out_features), dtype=weight_dtype))
        else: self.bias = None
    def forward(self, x):
        num_tokens = None
        output_shape = (*x.shape[:-1], -1)
        x_quantized, x_scale = torch.ops.fbgemm.quantize_fp8_per_row(x.view(-1, x.shape[-1]), num_tokens, self.input_scale_ub)
        output = torch.ops.fbgemm.f8f8bf16_rowwise(x_quantized, self.weight, x_scale, self.weight_scale, use_fast_accum=True)
        output = output + self.bias if self.bias is not None else output
        output = output.to(x.device)
        output = output.reshape(output_shape)
        del x_quantized, x_scale
        return output
def _replace_with_fbgemm_fp8_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, has_been_replaced=False, pre_quantized=False):
    if current_key_name is None: current_key_name = []
    for name, module in model.named_children():
        current_key_name.append(name)
        if (isinstance(module, nn.Linear)) and name not in modules_to_not_convert:
            current_key_name_str = ".".join(current_key_name)
            if not any((key + "." in current_key_name_str) or (key == current_key_name_str) for key in modules_to_not_convert):
                with init_empty_weights(include_buffers=True):
                    in_features = module.in_features
                    out_features = module.out_features
                    model._modules[name] = FbgemmFp8Linear(in_features, out_features, module.bias is not None)
                    has_been_replaced = True
                    model._modules[name].requires_grad_(False)
                model._modules[name].input_scale_ub = torch.tensor([quantization_config.activation_scale_ub], dtype=torch.float)
        if len(list(module.children())) > 0: _, has_been_replaced = _replace_with_fbgemm_fp8_linear(module, modules_to_not_convert, current_key_name, quantization_config, has_been_replaced=has_been_replaced, pre_quantized=pre_quantized)
        current_key_name.pop(-1)
    return model, has_been_replaced
def replace_with_fbgemm_fp8_linear(model, modules_to_not_convert=None, current_key_name=None, quantization_config=None, pre_quantized=False):
    modules_to_not_convert = ["lm_head"] if modules_to_not_convert is None else modules_to_not_convert
    if quantization_config.modules_to_not_convert is not None: modules_to_not_convert.extend(quantization_config.modules_to_not_convert)
    modules_to_not_convert = list(set(modules_to_not_convert))
    model, has_been_replaced = _replace_with_fbgemm_fp8_linear(model, modules_to_not_convert, current_key_name, quantization_config, pre_quantized=pre_quantized)
    if not has_been_replaced: logger.warning("You are loading your model using FP8 quantization but no linear modules were found in your model. Please double check your model architecture, or submit an issue on github if you think this is a bug.")
    return model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
