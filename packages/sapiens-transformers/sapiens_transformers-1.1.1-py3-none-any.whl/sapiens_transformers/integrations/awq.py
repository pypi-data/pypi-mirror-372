"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ..activations import ACT2FN
from ..modeling_utils import PreTrainedModel
from ..utils import is_auto_awq_available, is_torch_available, logging
from ..utils.quantization_config import (AwqBackendPackingMethod, AwqConfig, AWQLinearVersion, ExllamaVersion)
if is_torch_available():
    import torch
    import torch.nn as nn
logger = logging.get_logger(__name__)
AWQ_FUSED_MAPPINGS = {"entity": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False},
"mistral": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False},
"mixtral": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['w1', 'w3', 'w2'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False, 'rope_theta': 1000000.0},
"llama": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False},
"llava": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False},
"sapama": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False},
"sastral": {'attention': ['q_proj', 'k_proj', 'v_proj', 'o_proj'], 'mlp': ['gate_proj', 'up_proj', 'down_proj'], 'layernorm': ['input_layernorm', 'post_attention_layernorm', 'norm'], 'use_alibi': False}}
AWQ_SCALES_MAPPINGS = {"sapiens_code": {"act": "act", "layer_before_act": "c_fc"}, "starcoder2": {"act": "act", "layer_before_act": "c_fc"}, "RefinedWebModel": {"act": "act", "layer_before_act": "dense_h_to_4h"},
"falcon": {"act": "act", "layer_before_act": "dense_h_to_4h"}, "mpt": {"act": "act", "layer_before_act": "up_proj"}, "gptj": {"act": "act", "layer_before_act": "fc_in"},
"gpt_neox": {"act": "act", "layer_before_act": "dense_h_to_4h"}, "gpt_bigcode": {"act": "act", "layer_before_act": "c_fc"}, "bloom": {"act": "gelu_impl", "layer_before_act": "dense_h_to_4h"}}
def replace_quantization_scales(model, model_type):
    from awq.modules.act import ScaledActivation
    if model_type not in AWQ_SCALES_MAPPINGS: return model
    for name, module in model.named_children():
        act_name = AWQ_SCALES_MAPPINGS[model_type]["act"]
        layer_before_act_name = AWQ_SCALES_MAPPINGS[model_type]["layer_before_act"]
        if name == act_name and hasattr(model, layer_before_act_name):
            layer_before_act = getattr(model, AWQ_SCALES_MAPPINGS[model_type]["layer_before_act"])
            size = layer_before_act.out_features
            scale_like = torch.ones(size)
            model._modules[name] = ScaledActivation(module, scale_like)
        _ = replace_quantization_scales(module, model_type)
    return model
def replace_with_awq_linear(model, modules_to_not_convert=None, quantization_config=None, current_key_name=None, has_been_replaced=False) -> bool:
    if modules_to_not_convert is None: modules_to_not_convert = []
    backend = quantization_config.backend
    if not is_auto_awq_available(): raise ValueError("AWQ (either `autoawq` or `llmawq`) is not available. Please install it with `pip install autoawq` or check out the installation guide in https://github.com/mit-han-lab/llm-awq")
    if backend == AwqBackendPackingMethod.AUTOAWQ:
        if quantization_config.version == AWQLinearVersion.GEMM:
            from awq.modules.linear.gemm import WQLinear_GEMM
            target_cls = WQLinear_GEMM
        elif quantization_config.version == AWQLinearVersion.GEMV:
            from awq.modules.linear.gemv import WQLinear_GEMV
            target_cls = WQLinear_GEMV
        elif quantization_config.version == AWQLinearVersion.EXLLAMA:
            if quantization_config.exllama_config["version"] == ExllamaVersion.ONE:
                from awq.modules.linear.exllama import WQLinear_Exllama
                target_cls = WQLinear_Exllama
            elif quantization_config.exllama_config["version"] == ExllamaVersion.TWO:
                from awq.modules.linear.exllamav2 import WQLinear_ExllamaV2
                target_cls = WQLinear_ExllamaV2
            else: raise ValueError(f"Unrecognized Exllama version: {quantization_config.exllama_config['version']}")
        else: raise ValueError(f"Unrecognized AWQ version: {quantization_config.version}")
    else:
        from awq.quantize.qmodule import WQLinear
        target_cls = WQLinear
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, nn.Linear) and name not in modules_to_not_convert:
            if not any(key in ".".join(current_key_name) for key in modules_to_not_convert):
                in_features = module.in_features
                out_features = module.out_features
                model._modules[name] = target_cls(w_bit=quantization_config.bits, group_size=quantization_config.group_size, in_features=in_features, out_features=out_features, bias=module.bias is not None, dev=module.weight.device)
                has_been_replaced = True
                model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0: _, has_been_replaced = replace_with_awq_linear(module, modules_to_not_convert=modules_to_not_convert, current_key_name=current_key_name, quantization_config=quantization_config, has_been_replaced=has_been_replaced)
        current_key_name.pop(-1)
    return model, has_been_replaced
def get_modules_to_fuse(model, quantization_config):
    if not isinstance(model, PreTrainedModel): raise TypeError(f"The model should be an instance of `PreTrainedModel`, got {model.__class__.__name__}")
    if quantization_config.modules_to_fuse is not None:
        current_fused_mapping = quantization_config.modules_to_fuse
        current_fused_mapping["max_seq_len"] = quantization_config.fuse_max_seq_len
    elif model.config.model_type in AWQ_FUSED_MAPPINGS:
        current_fused_mapping = AWQ_FUSED_MAPPINGS[model.config.model_type]
        config = model.config.get_text_config(decoder=True)
        hidden_size = config.hidden_size
        num_attention_heads = config.num_attention_heads
        num_key_value_heads = getattr(config, "num_key_value_heads", num_attention_heads)
        current_fused_mapping["hidden_size"] = hidden_size
        current_fused_mapping["num_attention_heads"] = num_attention_heads
        current_fused_mapping["num_key_value_heads"] = num_key_value_heads
        current_fused_mapping["max_seq_len"] = quantization_config.fuse_max_seq_len
    else: raise ValueError("Fusing mapping not found either on the quantization config or the supported `AWQ_FUSED_MAPPINGS`.")
    return current_fused_mapping
def fuse_awq_modules(model, quantization_config):
    if isinstance(quantization_config, dict): quantization_config = AwqConfig.from_dict(quantization_config)
    backend = quantization_config.backend
    modules_to_fuse = get_modules_to_fuse(model, quantization_config)
    modules_to_not_convert = getattr(quantization_config, "modules_to_not_convert", None)
    if backend == AwqBackendPackingMethod.AUTOAWQ:
        from awq.modules.fused.attn import QuantAttentionFused
        from awq.modules.fused.mlp import QuantFusedMLP
        from awq.modules.fused.norm import FasterTransformerRMSNorm
    else: raise ValueError("Fusing is only supported for the AutoAWQ backend")
    fused_attention_modules = []
    for name, module in model.named_modules():
        if modules_to_not_convert is not None:
            if any(module_name_to_not_convert in name for module_name_to_not_convert in modules_to_not_convert): continue
        _fuse_awq_layernorm(modules_to_fuse["layernorm"], module, FasterTransformerRMSNorm)
        _fuse_awq_mlp(model, name, modules_to_fuse["mlp"], module, QuantFusedMLP)
        attention_has_been_fused = _fuse_awq_attention_layers(model, module, modules_to_fuse, name, QuantAttentionFused)
        if attention_has_been_fused: fused_attention_modules.append(name.split(".")[0])
    if len(fused_attention_modules) > 0:
        for module_name, module in model.named_modules():
            if any(module_name in fused_attention_modules for fused_attention_parent_module in fused_attention_modules):
                if hasattr(module, "config") and hasattr(module.config, "_attn_implementation"): module.config._attn_implementation = "custom"
    return model
def _fuse_awq_layernorm(fuse_module_names, module, target_cls):
    for module_name in fuse_module_names:
        if hasattr(module, module_name):
            old_module = getattr(module, module_name)
            module._modules[module_name] = target_cls(old_module.weight, old_module.variance_epsilon).to(old_module.weight.device)
            del old_module
def _fuse_awq_mlp(model, current_module_name, fuse_module_names, module, target_cls):
    if len(fuse_module_names) == 0: return
    if hasattr(module, fuse_module_names[0]):
        gate_proj = getattr(module, fuse_module_names[0])
        up_proj = getattr(module, fuse_module_names[1])
        down_proj = getattr(module, fuse_module_names[2])
        previous_device = gate_proj.qweight.device
        config = model.config.get_text_config(decoder=True)
        hidden_act = config.hidden_act
        activation_fn = ACT2FN[hidden_act]
        new_module = target_cls(gate_proj, down_proj, up_proj, activation_fn)
        parent_name, child_name = current_module_name.rsplit(".", 1)
        parent = model.get_submodule(parent_name)
        setattr(parent, child_name, new_module.to(previous_device))
        del gate_proj, up_proj, down_proj
def _fuse_awq_attention_layers(model, module, modules_to_fuse, current_module_name, target_cls):
    from awq.modules.linear import WQLinear_GEMM, WQLinear_GEMV
    module_has_been_fused = False
    if len(modules_to_fuse["attention"]) == 0: return module_has_been_fused
    if hasattr(module, modules_to_fuse["attention"][0]):
        q_proj = getattr(module, modules_to_fuse["attention"][0])
        if isinstance(q_proj, WQLinear_GEMV):
            linear_target_cls = WQLinear_GEMV
            cat_dim = 0
        elif isinstance(q_proj, WQLinear_GEMM):
            linear_target_cls = WQLinear_GEMM
            cat_dim = 1
        else: raise ValueError("Unsupported q_proj type: {type(q_proj)}")
        previous_device = q_proj.qweight.device
        k_proj = getattr(module, modules_to_fuse["attention"][1])
        v_proj = getattr(module, modules_to_fuse["attention"][2])
        o_proj = getattr(module, modules_to_fuse["attention"][3])
        bias = torch.cat([q_proj.bias, k_proj.bias, v_proj.bias], dim=0) if q_proj.bias is not None else None
        qkv_layer = linear_target_cls(q_proj.w_bit, q_proj.group_size, q_proj.in_features, q_proj.out_features + k_proj.out_features + v_proj.out_features, q_proj.bias is not None, next(iter(module.state_dict().values())).device)
        qkv_layer.qweight = torch.cat([q_proj.qweight, k_proj.qweight, v_proj.qweight], dim=cat_dim)
        qkv_layer.qzeros = torch.cat([q_proj.qzeros, k_proj.qzeros, v_proj.qzeros], dim=cat_dim)
        qkv_layer.scales = torch.cat([q_proj.scales, k_proj.scales, v_proj.scales], dim=cat_dim)
        if isinstance(qkv_layer, WQLinear_GEMV): qkv_layer.split_k_iters = q_proj.split_k_iters
        qkv_layer.bias = bias
        fused_attention_layer = target_cls(modules_to_fuse["hidden_size"], modules_to_fuse["num_attention_heads"], modules_to_fuse["num_key_value_heads"], qkv_layer, o_proj, previous_device, modules_to_fuse["max_seq_len"], use_alibi=modules_to_fuse["use_alibi"], rope_theta=modules_to_fuse.get("rope_theta", 10000.0))
        fused_attention_layer.is_hf_transformers = True
        parent_name, child_name = current_module_name.rsplit(".", 1)
        parent = model.get_submodule(parent_name)
        setattr(parent, child_name, fused_attention_layer.to(previous_device))
        del q_proj, k_proj, v_proj, o_proj
        module_has_been_fused = True
    return module_has_been_fused
def post_init_awq_exllama_modules(model, exllama_config):
    if exllama_config["version"] == ExllamaVersion.ONE:
        from awq.modules.linear.exllama import exllama_post_init
        model = exllama_post_init(model)
    elif exllama_config["version"] == ExllamaVersion.TWO:
        from awq.modules.linear.exllamav2 import exllamav2_post_init
        model = exllamav2_post_init(model, max_input_len=exllama_config["max_input_len"], max_batch_size=exllama_config["max_batch_size"])
    else: raise ValueError(f"Unrecognized Exllama version: {exllama_config['version']}")
    return model
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
