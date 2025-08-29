"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .integrations import (GGUF_CONFIG_MAPPING, GGUF_TENSOR_MAPPING, GGUF_TOKENIZER_MAPPING, _gguf_parse_value)
from .utils.import_utils import is_gguf_available
from .utils import is_torch_available
from .utils.logging import get_logger
from typing import Optional
from tqdm import tqdm
import numpy as np
if is_torch_available(): import torch
logger = get_logger(__name__)
GGUF_TO_TRANSFORMERS_MAPPING = {"ignore": {"GGUF": {'version': 'version', 'tensor_count': 'tensor_count', 'kv_count': 'kv_count'},
"general": {"file_type": "file_type", "quantization_version": "quantization_version"}}, "config": GGUF_CONFIG_MAPPING, "tensors": GGUF_TENSOR_MAPPING,
"tokenizer": {"tokenizer": GGUF_TOKENIZER_MAPPING["tokenizer"]}, "tokenizer_config": {"tokenizer": GGUF_TOKENIZER_MAPPING["tokenizer_config"]}}
GGUF_SUPPORTED_ARCHITECTURES = list(GGUF_TO_TRANSFORMERS_MAPPING["tensors"].keys())
def read_field(reader, field):
    value = reader.fields[field]
    return [_gguf_parse_value(value.parts[_data_index], value.types) for _data_index in value.data]
def load_gguf_checkpoint(gguf_checkpoint_path, return_tensors=False):
    if is_gguf_available() and is_torch_available(): from gguf import GGUFReader, dequantize
    else:
        logger.error("Loading a GGUF checkpoint in PyTorch, requires both PyTorch and GGUF>=0.10.0 to be installed. Please see https://pytorch.org/ and https://github.com/ggerganov/llama.cpp/tree/master/gguf-py for installation instructions.")
        raise ImportError("Please install torch and gguf>=0.10.0 to load a GGUF checkpoint in PyTorch.")
    reader = GGUFReader(gguf_checkpoint_path)
    fields = reader.fields
    reader_keys = list(fields.keys())
    parsed_parameters = {k: {} for k in GGUF_TO_TRANSFORMERS_MAPPING}
    architecture = read_field(reader, "general.architecture")[0]
    model_name = read_field(reader, "general.name")
    if ("entity" in architecture or "llama" in architecture or "sapama" in architecture) and ("mistral" in model_name or "sastral" in model_name): updated_architecture = "mistral"
    else: updated_architecture = architecture
    if "qwen2moe" in architecture: updated_architecture = "qwen2_moe"
    if architecture not in GGUF_SUPPORTED_ARCHITECTURES: raise ValueError(f"Architecture {architecture} not supported")
    for gguf_key, field in reader.fields.items():
        gguf_key = gguf_key.replace(architecture, updated_architecture)
        split = gguf_key.split(".")
        prefix = split[0]
        config_key = ".".join(split[1:])
        value = [_gguf_parse_value(field.parts[_data_index], field.types) for _data_index in field.data]
        if len(value) == 1: value = value[0]
        if isinstance(value, str) and architecture in value: value = value.replace(architecture, updated_architecture)
        for parameter in GGUF_TO_TRANSFORMERS_MAPPING:
            parameter_renames = GGUF_TO_TRANSFORMERS_MAPPING[parameter]
            if prefix in parameter_renames and config_key in parameter_renames[prefix]:
                renamed_config_key = parameter_renames[prefix][config_key]
                if renamed_config_key == -1: continue
                if renamed_config_key is not None: parsed_parameters[parameter][renamed_config_key] = value
                if gguf_key in reader_keys: reader_keys.remove(gguf_key)
        if gguf_key in reader_keys: logger.info(f"Some keys were not parsed and added into account {gguf_key} | {value}")
    if "vocab_size" not in parsed_parameters["config"]:
        tokenizer_parameters = parsed_parameters["tokenizer"]
        if "tokens" in tokenizer_parameters: parsed_parameters["config"]["vocab_size"] = len(tokenizer_parameters["tokens"])
        else: logger.warning("Can't find a way to retrieve missing config vocab_size from tokenizer parameters. This will use default value from model config class and cause unexpected behavior.")
    if return_tensors:
        tensor_key_mapping = GGUF_TO_TRANSFORMERS_MAPPING["tensors"][architecture]
        for tensor in tqdm(reader.tensors, desc="Converting and de-quantizing GGUF tensors..."):
            renamed_tensor_name = tensor.name
            for tensor_name_mapping in GGUF_TO_TRANSFORMERS_MAPPING["tensors"]:
                if tensor_name_mapping in renamed_tensor_name: renamed_tensor_name = renamed_tensor_name.replace(tensor_name_mapping, GGUF_TO_TRANSFORMERS_MAPPING["tensors"][tensor_name_mapping])
            name = tensor.name
            weights = dequantize(tensor.data, tensor.tensor_type)
            if (architecture == "entity" or architecture == "llama" or architecture == "sapama") and (".attn_k." in name or ".attn_q." in name):
                num_heads = parsed_parameters["config"]["num_attention_heads"]
                num_kv_heads = parsed_parameters["config"]["num_key_value_heads"]
                if ".attn_q." in name: weights = reverse_permute_weights(weights, num_heads, num_heads)
                elif ".attn_k." in name: weights = reverse_permute_weights(weights, num_heads, num_kv_heads)
            for tensor_name in tensor_key_mapping:
                if tensor_name in name: name = name.replace(tensor_name, tensor_key_mapping[tensor_name])
            parsed_parameters["tensors"][name] = torch.from_numpy(np.copy(weights))
    if len(reader_keys) > 0: logger.info(f"Some keys of the GGUF file were not considered: {reader_keys}")
    return parsed_parameters
def reverse_permute_weights(weights: np.ndarray, n_head: int, num_kv_heads: Optional[int] = None) -> np.ndarray:
    if num_kv_heads is not None and n_head != num_kv_heads: n_head = num_kv_heads
    dim = weights.shape[0] // n_head // 2
    w = weights.reshape(n_head, dim, 2, *weights.shape[1:])
    return w.swapaxes(2, 1).reshape(weights.shape)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
