'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import copy
import importlib.metadata
import inspect
import json
import os
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any, Dict, List, Optional, Union
from packaging import version
from ..utils import is_torch_available, is_torchao_available
if is_torch_available(): import torch
class QuantizationMethod(str, Enum): SAPIENS_MACHINE, GGUF, TORCHAO = 'sapiens_machine', 'gguf', 'torchao'
@dataclass
class QuantizationConfigMixin:
    quant_method: QuantizationMethod
    _exclude_attributes_at_init = []
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        """Returns:"""
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        if return_unused_kwargs: return (config, kwargs)
        else: return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        """Args:"""
        with open(json_file_path, 'w', encoding='utf-8') as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + '\n'
            writer.write(json_string)
    def to_dict(self) -> Dict[str, Any]:
        """Returns:"""
        return copy.deepcopy(self.__dict__)
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items(): yield (attr, value)
    def __repr__(self): return f'{self.__class__.__name__} {self.to_json_string()}'
    def to_json_string(self, use_diff: bool=True) -> str:
        """Returns:"""
        if use_diff is True: config_dict = self.to_diff_dict()
        else: config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + '\n'
    def update(self, **kwargs):
        """Returns:"""
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs
@dataclass
class SapiensMachineConfig(QuantizationConfigMixin):
    """Args:"""
    _exclude_attributes_at_init = ['_load_in_4bit', '_load_in_8bit', 'quant_method']
    def __init__(self, load_in_8bit=False, load_in_4bit=False, llm_int8_threshold=6.0, llm_int8_skip_modules=None, llm_int8_enable_fp32_cpu_offload=False, llm_int8_has_fp16_weight=False,
    bnb_4bit_compute_dtype=None, bnb_4bit_quant_type='fp4', bnb_4bit_use_double_quant=False, bnb_4bit_quant_storage=None,
    sapiens_4bit_compute_dtype=None, sapiens_4bit_quant_type='fp4', sapiens_4bit_use_double_quant=False, sapiens_4bit_quant_storage=None, **kwargs):
        self.quant_method = QuantizationMethod.SAPIENS_MACHINE
        if load_in_4bit and load_in_8bit: raise ValueError('load_in_4bit and load_in_8bit are both True, but only one can be used at the same time')
        self._load_in_8bit = load_in_8bit
        self._load_in_4bit = load_in_4bit
        self.llm_int8_threshold = llm_int8_threshold
        self.llm_int8_skip_modules = llm_int8_skip_modules
        self.llm_int8_enable_fp32_cpu_offload = llm_int8_enable_fp32_cpu_offload
        self.llm_int8_has_fp16_weight = llm_int8_has_fp16_weight
        self.sapiens_4bit_quant_type = sapiens_4bit_quant_type
        self.bnb_4bit_quant_type = bnb_4bit_quant_type
        self.sapiens_4bit_use_double_quant = sapiens_4bit_use_double_quant
        self.bnb_4bit_use_double_quant = bnb_4bit_use_double_quant
        if sapiens_4bit_compute_dtype is None and not bnb_4bit_compute_dtype is None: sapiens_4bit_compute_dtype = bnb_4bit_compute_dtype
        if sapiens_4bit_compute_dtype is None: self.sapiens_4bit_compute_dtype = torch.float32
        elif isinstance(sapiens_4bit_compute_dtype, str): self.sapiens_4bit_compute_dtype = getattr(torch, sapiens_4bit_compute_dtype)
        elif isinstance(sapiens_4bit_compute_dtype, torch.dtype): self.sapiens_4bit_compute_dtype = sapiens_4bit_compute_dtype
        else: raise ValueError('sapiens_4bit_compute_dtype must be a string or a torch.dtype')
        if bnb_4bit_compute_dtype is None and not sapiens_4bit_compute_dtype is None: bnb_4bit_compute_dtype = sapiens_4bit_compute_dtype
        if bnb_4bit_compute_dtype is None: self.bnb_4bit_compute_dtype = torch.float32
        elif isinstance(bnb_4bit_compute_dtype, str): self.bnb_4bit_compute_dtype = getattr(torch, bnb_4bit_compute_dtype)
        elif isinstance(bnb_4bit_compute_dtype, torch.dtype): self.bnb_4bit_compute_dtype = bnb_4bit_compute_dtype
        else: raise ValueError('bnb_4bit_compute_dtype must be a string or a torch.dtype')
        if sapiens_4bit_quant_storage is None and not bnb_4bit_quant_storage is None: sapiens_4bit_quant_storage = bnb_4bit_quant_storage
        if sapiens_4bit_quant_storage is None: self.sapiens_4bit_quant_storage = torch.uint8
        elif isinstance(sapiens_4bit_quant_storage, str):
            if sapiens_4bit_quant_storage not in ['float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16']: raise ValueError("`sapiens_4bit_quant_storage` must be a valid string (one of 'float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16') ")
            self.sapiens_4bit_quant_storage = getattr(torch, sapiens_4bit_quant_storage)
        elif isinstance(sapiens_4bit_quant_storage, torch.dtype): self.sapiens_4bit_quant_storage = sapiens_4bit_quant_storage
        else: raise ValueError('sapiens_4bit_quant_storage must be a string or a torch.dtype')
        if bnb_4bit_quant_storage is None and not sapiens_4bit_quant_storage is None: bnb_4bit_quant_storage = sapiens_4bit_quant_storage
        if bnb_4bit_quant_storage is None: self.bnb_4bit_quant_storage = torch.uint8
        elif isinstance(bnb_4bit_quant_storage, str):
            if bnb_4bit_quant_storage not in ['float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16']: raise ValueError("`bnb_4bit_quant_storage` must be a valid string (one of 'float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16') ")
            self.bnb_4bit_quant_storage = getattr(torch, bnb_4bit_quant_storage)
        elif isinstance(bnb_4bit_quant_storage, torch.dtype): self.bnb_4bit_quant_storage = bnb_4bit_quant_storage
        else: raise ValueError('bnb_4bit_quant_storage must be a string or a torch.dtype')
        self.post_init()
    @property
    def load_in_4bit(self): return self._load_in_4bit
    @load_in_4bit.setter
    def load_in_4bit(self, value: bool):
        if not isinstance(value, bool): raise TypeError('load_in_4bit must be a boolean')
        if self.load_in_8bit and value: raise ValueError('load_in_4bit and load_in_8bit are both True, but only one can be used at the same time')
        self._load_in_4bit = value
    @property
    def load_in_8bit(self): return self._load_in_8bit
    @load_in_8bit.setter
    def load_in_8bit(self, value: bool):
        if not isinstance(value, bool): raise TypeError('load_in_8bit must be a boolean')
        if self.load_in_4bit and value: raise ValueError('load_in_4bit and load_in_8bit are both True, but only one can be used at the same time')
        self._load_in_8bit = value
    def post_init(self):
        if not isinstance(self.load_in_4bit, bool): raise TypeError('load_in_4bit must be a boolean')
        if not isinstance(self.load_in_8bit, bool): raise TypeError('load_in_8bit must be a boolean')
        if not isinstance(self.llm_int8_threshold, float): raise TypeError('llm_int8_threshold must be a float')
        if self.llm_int8_skip_modules is not None and (not isinstance(self.llm_int8_skip_modules, list)): raise TypeError('llm_int8_skip_modules must be a list of strings')
        if not isinstance(self.llm_int8_enable_fp32_cpu_offload, bool): raise TypeError('llm_int8_enable_fp32_cpu_offload must be a boolean')
        if not isinstance(self.llm_int8_has_fp16_weight, bool): raise TypeError('llm_int8_has_fp16_weight must be a boolean')
        if self.sapiens_4bit_compute_dtype is not None and (not isinstance(self.sapiens_4bit_compute_dtype, torch.dtype)): raise TypeError('sapiens_4bit_compute_dtype must be torch.dtype')
        if self.bnb_4bit_compute_dtype is not None and (not isinstance(self.bnb_4bit_compute_dtype, torch.dtype)): raise TypeError('bnb_4bit_compute_dtype must be torch.dtype')
        if not isinstance(self.sapiens_4bit_quant_type, str): raise TypeError('sapiens_4bit_quant_type must be a string')
        if not isinstance(self.bnb_4bit_quant_type, str): raise TypeError('bnb_4bit_quant_type must be a string')
        if not isinstance(self.sapiens_4bit_use_double_quant, bool): raise TypeError('sapiens_4bit_use_double_quant must be a boolean')
        if not isinstance(self.bnb_4bit_use_double_quant, bool): raise TypeError('bnb_4bit_use_double_quant must be a boolean')
        if self.load_in_4bit and (not version.parse(importlib.metadata.version('sapiens_machine')) >= version.parse('1.0.0')): raise ValueError('4 bit quantization requires sapiens_machine>=1.0.0 - please upgrade your sapiens_machine version')
    def is_quantizable(self): return self.load_in_8bit or self.load_in_4bit
    def quantization_method(self):
        if self.load_in_8bit: return 'llm_int8'
        elif self.load_in_4bit and self.sapiens_4bit_quant_type == 'fp4' and self.bnb_4bit_quant_type == 'fp4': return 'fp4'
        elif self.load_in_4bit and self.sapiens_4bit_quant_type == 'nf4' and self.bnb_4bit_quant_type == 'nf4': return 'nf4'
        else: return None
    def to_dict(self) -> Dict[str, Any]:
        """Returns:"""
        output = copy.deepcopy(self.__dict__)
        output['sapiens_4bit_compute_dtype'] = str(output['sapiens_4bit_compute_dtype']).split('.')[1]
        output['bnb_4bit_compute_dtype'] = str(output['bnb_4bit_compute_dtype']).split('.')[1]
        output['sapiens_4bit_quant_storage'] = str(output['sapiens_4bit_quant_storage']).split('.')[1]
        output['bnb_4bit_quant_storage'] = str(output['bnb_4bit_quant_storage']).split('.')[1]
        output['load_in_4bit'] = self.load_in_4bit
        output['load_in_8bit'] = self.load_in_8bit
        return output
    def __repr__(self):
        config_dict = self.to_dict()
        return f'{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n'
    def to_diff_dict(self) -> Dict[str, Any]:
        """Returns:"""
        config_dict = self.to_dict()
        default_config_dict = SapiensMachineConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]: serializable_config_dict[key] = value
        return serializable_config_dict
@dataclass
class GGUFQuantizationConfig(QuantizationConfigMixin):
    """Args:"""
    def __init__(self, compute_dtype: Optional['torch.dtype']=None):
        self.quant_method = QuantizationMethod.GGUF
        self.compute_dtype = compute_dtype
        self.pre_quantized = True
        self.modules_to_not_convert = None
        if self.compute_dtype is None: self.compute_dtype = torch.float32
@dataclass
class TorchAoConfig(QuantizationConfigMixin):
    """Args:"""
    def __init__(self, quant_type: str, modules_to_not_convert: Optional[List[str]]=None, **kwargs) -> None:
        self.quant_method = QuantizationMethod.TORCHAO
        self.quant_type = quant_type
        self.modules_to_not_convert = modules_to_not_convert
        if 'quant_type_kwargs' in kwargs: self.quant_type_kwargs = kwargs['quant_type_kwargs']
        else: self.quant_type_kwargs = kwargs
        TORCHAO_QUANT_TYPE_METHODS = self._get_torchao_quant_type_to_method()
        if self.quant_type not in TORCHAO_QUANT_TYPE_METHODS.keys(): raise ValueError(f'Requested quantization type: {self.quant_type} is not supported yet or is incorrect. If you think the provided quantization type should be supported, please open an issue at https://github.com/huggingface/diffusers/issues.')
        method = TORCHAO_QUANT_TYPE_METHODS[self.quant_type]
        signature = inspect.signature(method)
        all_kwargs = {param.name for param in signature.parameters.values() if param.kind in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]}
        unsupported_kwargs = list(self.quant_type_kwargs.keys() - all_kwargs)
        if len(unsupported_kwargs) > 0: raise ValueError(f'The quantization method "{quant_type}" does not support the following keyword arguments: {unsupported_kwargs}. The following keywords arguments are supported: {all_kwargs}.')
    @classmethod
    def _get_torchao_quant_type_to_method(cls):
        if is_torchao_available():
            from torchao.quantization import (float8_dynamic_activation_float8_weight, float8_static_activation_float8_weight, float8_weight_only, fpx_weight_only, int4_weight_only,
            int8_dynamic_activation_int4_weight, int8_dynamic_activation_int8_weight, int8_weight_only, uintx_weight_only)
            from torchao.quantization.observer import PerRow, PerTensor
            def generate_float8dq_types(dtype: torch.dtype):
                name = 'e5m2' if dtype == torch.float8_e5m2 else 'e4m3'
                types = {}
                for granularity_cls in [PerTensor, PerRow]:
                    granularity_name = 'tensor' if granularity_cls is PerTensor else 'row'
                    types[f'float8dq_{name}_{granularity_name}'] = partial(float8_dynamic_activation_float8_weight, activation_dtype=dtype,
                    weight_dtype=dtype, granularity=(granularity_cls(), granularity_cls()))
                return types
            def generate_fpx_quantization_types(bits: int):
                types = {}
                for ebits in range(1, bits):
                    mbits = bits - ebits - 1
                    types[f'fp{bits}_e{ebits}m{mbits}'] = partial(fpx_weight_only, ebits=ebits, mbits=mbits)
                non_sign_bits = bits - 1
                default_ebits = (non_sign_bits + 1) // 2
                default_mbits = non_sign_bits - default_ebits
                types[f'fp{bits}'] = partial(fpx_weight_only, ebits=default_ebits, mbits=default_mbits)
                return types
            INT4_QUANTIZATION_TYPES = {'int4wo': int4_weight_only, 'int4_weight_only': int4_weight_only,
            'int4dq': int8_dynamic_activation_int4_weight, 'int8_dynamic_activation_int4_weight': int8_dynamic_activation_int4_weight}
            INT8_QUANTIZATION_TYPES = {'int8wo': int8_weight_only, 'int8_weight_only': int8_weight_only,
            'int8dq': int8_dynamic_activation_int8_weight, 'int8_dynamic_activation_int8_weight': int8_dynamic_activation_int8_weight}
            FLOATX_QUANTIZATION_TYPES = {'float8wo': partial(float8_weight_only, weight_dtype=torch.float8_e5m2),
            'float8_weight_only': float8_weight_only, 'float8wo_e5m2': partial(float8_weight_only, weight_dtype=torch.float8_e5m2),
            'float8wo_e4m3': partial(float8_weight_only, weight_dtype=torch.float8_e4m3fn), 'float8dq': float8_dynamic_activation_float8_weight,
            'float8_dynamic_activation_float8_weight': float8_dynamic_activation_float8_weight, 'float8dq_e4m3': partial(float8_dynamic_activation_float8_weight,
                activation_dtype=torch.float8_e4m3fn, weight_dtype=torch.float8_e4m3fn), **generate_float8dq_types(torch.float8_e4m3fn),
            'float8_static_activation_float8_weight': float8_static_activation_float8_weight, **generate_fpx_quantization_types(3),
            **generate_fpx_quantization_types(4), **generate_fpx_quantization_types(5), **generate_fpx_quantization_types(6), **generate_fpx_quantization_types(7)}
            UINTX_QUANTIZATION_DTYPES = {'uintx_weight_only': uintx_weight_only, 'uint1wo': partial(uintx_weight_only, dtype=torch.uint1),
            'uint2wo': partial(uintx_weight_only, dtype=torch.uint2), 'uint3wo': partial(uintx_weight_only, dtype=torch.uint3),
            'uint4wo': partial(uintx_weight_only, dtype=torch.uint4), 'uint5wo': partial(uintx_weight_only, dtype=torch.uint5),
            'uint6wo': partial(uintx_weight_only, dtype=torch.uint6), 'uint7wo': partial(uintx_weight_only, dtype=torch.uint7)}
            QUANTIZATION_TYPES = {}
            QUANTIZATION_TYPES.update(INT4_QUANTIZATION_TYPES)
            QUANTIZATION_TYPES.update(INT8_QUANTIZATION_TYPES)
            QUANTIZATION_TYPES.update(UINTX_QUANTIZATION_DTYPES)
            if cls._is_cuda_capability_atleast_8_9(): QUANTIZATION_TYPES.update(FLOATX_QUANTIZATION_TYPES)
            return QUANTIZATION_TYPES
        else: raise ValueError('TorchAoConfig requires torchao to be installed, please install with `pip install torchao`')
    @staticmethod
    def _is_cuda_capability_atleast_8_9() -> bool:
        if not torch.cuda.is_available(): raise RuntimeError('TorchAO requires a CUDA compatible GPU and installation of PyTorch.')
        major, minor = torch.cuda.get_device_capability()
        if major == 8: return minor >= 9
        return major >= 9
    def get_apply_tensor_subclass(self):
        TORCHAO_QUANT_TYPE_METHODS = self._get_torchao_quant_type_to_method()
        return TORCHAO_QUANT_TYPE_METHODS[self.quant_type](**self.quant_type_kwargs)
    def __repr__(self):
        config_dict = self.to_dict()
        return f'{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n'
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
