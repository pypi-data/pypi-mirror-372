"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import importlib.metadata
import json
import os
from dataclasses import dataclass
from enum import Enum
from inspect import Parameter, signature
from typing import Any, Dict, List, Optional, Union
from packaging import version
from ..utils import is_auto_awq_available, is_hqq_available, is_torch_available, is_torchao_available, logging
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class QuantizationMethod(str, Enum):
    SAPIENS_MACHINE = "sapiens_machine"
    GPTQ = "gptq"
    AWQ = "awq"
    AQLM = "aqlm"
    QUANTO = "quanto"
    EETQ = "eetq"
    HQQ = "hqq"
    COMPRESSED_TENSORS = "compressed-tensors"
    FBGEMM_FP8 = "fbgemm_fp8"
    TORCHAO = "torchao"
class AWQLinearVersion(str, Enum):
    GEMM = "gemm"
    GEMV = "gemv"
    EXLLAMA = "exllama"
    @staticmethod
    def from_str(version: str):
        version = version.lower()
        if version == "gemm": return AWQLinearVersion.GEMM
        elif version == "gemv": return AWQLinearVersion.GEMV
        elif version == "exllama": return AWQLinearVersion.EXLLAMA
        else: raise ValueError(f"Unknown AWQLinearVersion {version}")
class AwqBackendPackingMethod(str, Enum):
    AUTOAWQ = "autoawq"
    LLMAWQ = "llm-awq"
@dataclass
class QuantizationConfigMixin:
    quant_method: QuantizationMethod
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove: kwargs.pop(key, None)
        if return_unused_kwargs: return config, kwargs
        else: return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
            writer.write(json_string)
    def to_dict(self) -> Dict[str, Any]: return copy.deepcopy(self.__dict__)
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items(): yield attr, value
    def __repr__(self): return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_json_string(self, use_diff: bool = True) -> str:
        if use_diff is True: config_dict = self.to_diff_dict()
        else: config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
    def update(self, **kwargs):
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs
@dataclass
class HqqConfig(QuantizationConfigMixin):
    def __init__(self, nbits: int = 4, group_size: int = 64, quant_zero: bool = True, quant_scale: bool = False, offload_meta: bool = False,
    view_as_float: bool = False, axis: int = 0, dynamic_config: Optional[dict] = None, skip_modules: List[str] = ["lm_head"], **kwargs):
        if is_hqq_available(): from hqq.core.quantize import BaseQuantizeConfig as HQQBaseQuantizeConfig
        if axis not in [0, 1]: raise ValueError("Invalid axis value. Only 0 and 1 are allowed.")
        if dynamic_config is not None:
            self.quant_config = {}
            for key in dynamic_config: self.quant_config[key] = HQQBaseQuantizeConfig(**dynamic_config[key])
        else: self.quant_config = HQQBaseQuantizeConfig(**{"nbits": nbits, "group_size": group_size, "quant_zero": quant_zero, "quant_scale": quant_scale, "offload_meta": offload_meta, "view_as_float": view_as_float, "axis": axis})
        self.quant_method = QuantizationMethod.HQQ
        self.skip_modules = skip_modules
        self.post_init()
    def post_init(self): pass
    def to_dict(self) -> Dict[str, Any]: return self.quant_config
    def __repr__(self):
        config_dict = self.to_dict()
        return f"{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n"
    def to_diff_dict(self) -> Dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = HqqConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]: serializable_config_dict[key] = value
        return serializable_config_dict
@dataclass
class SapiensMachineConfig(QuantizationConfigMixin):
    def __init__(self, load_in_8bit=False, load_in_4bit=False, llm_int8_threshold=6.0, llm_int8_skip_modules=None, llm_int8_enable_fp32_cpu_offload=False, llm_int8_has_fp16_weight=False,
    bnb_4bit_compute_dtype=None, bnb_4bit_quant_type="fp4", bnb_4bit_use_double_quant=False, bnb_4bit_quant_storage=None,
    sapiens_4bit_compute_dtype=None, sapiens_4bit_quant_type="fp4", sapiens_4bit_use_double_quant=False, sapiens_4bit_quant_storage=None, **kwargs):
        self.quant_method = QuantizationMethod.SAPIENS_MACHINE
        if load_in_4bit and load_in_8bit: raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
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
        else: raise ValueError("sapiens_4bit_compute_dtype must be a string or a torch.dtype")
        if bnb_4bit_compute_dtype is None and not sapiens_4bit_compute_dtype is None: bnb_4bit_compute_dtype = sapiens_4bit_compute_dtype
        if bnb_4bit_compute_dtype is None: self.bnb_4bit_compute_dtype = torch.float32
        elif isinstance(bnb_4bit_compute_dtype, str): self.bnb_4bit_compute_dtype = getattr(torch, bnb_4bit_compute_dtype)
        elif isinstance(bnb_4bit_compute_dtype, torch.dtype): self.bnb_4bit_compute_dtype = bnb_4bit_compute_dtype
        else: raise ValueError("bnb_4bit_compute_dtype must be a string or a torch.dtype")
        if sapiens_4bit_quant_storage is None and not bnb_4bit_quant_storage is None: sapiens_4bit_quant_storage = bnb_4bit_quant_storage
        if sapiens_4bit_quant_storage is None: self.sapiens_4bit_quant_storage = torch.uint8
        elif isinstance(sapiens_4bit_quant_storage, str):
            if sapiens_4bit_quant_storage not in ["float16", "float32", "int8", "uint8", "float64", "bfloat16"]: raise ValueError("`sapiens_4bit_quant_storage` must be a valid string (one of 'float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16') ")
            self.sapiens_4bit_quant_storage = getattr(torch, sapiens_4bit_quant_storage)
        elif isinstance(sapiens_4bit_quant_storage, torch.dtype): self.sapiens_4bit_quant_storage = sapiens_4bit_quant_storage
        else: raise ValueError("sapiens_4bit_quant_storage must be a string or a torch.dtype")
        if bnb_4bit_quant_storage is None and not sapiens_4bit_quant_storage is None: bnb_4bit_quant_storage = sapiens_4bit_quant_storage
        if bnb_4bit_quant_storage is None: self.bnb_4bit_quant_storage = torch.uint8
        elif isinstance(bnb_4bit_quant_storage, str):
            if bnb_4bit_quant_storage not in ["float16", "float32", "int8", "uint8", "float64", "bfloat16"]: raise ValueError("`bnb_4bit_quant_storage` must be a valid string (one of 'float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16') ")
            self.bnb_4bit_quant_storage = getattr(torch, bnb_4bit_quant_storage)
        elif isinstance(bnb_4bit_quant_storage, torch.dtype): self.bnb_4bit_quant_storage = bnb_4bit_quant_storage
        else: raise ValueError("bnb_4bit_quant_storage must be a string or a torch.dtype")
        if kwargs: logger.warning(f"Unused kwargs: {list(kwargs.keys())}. These kwargs are not used in {self.__class__}.")
        self.post_init()
    @property
    def load_in_4bit(self): return self._load_in_4bit
    @load_in_4bit.setter
    def load_in_4bit(self, value: bool):
        if not isinstance(value, bool): raise TypeError("load_in_4bit must be a boolean")
        if self.load_in_8bit and value: raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
        self._load_in_4bit = value
    @property
    def load_in_8bit(self): return self._load_in_8bit
    @load_in_8bit.setter
    def load_in_8bit(self, value: bool):
        if not isinstance(value, bool): raise TypeError("load_in_8bit must be a boolean")
        if self.load_in_4bit and value: raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
        self._load_in_8bit = value
    def post_init(self):
        if not isinstance(self.load_in_4bit, bool): raise TypeError("load_in_4bit must be a boolean")
        if not isinstance(self.load_in_8bit, bool): raise TypeError("load_in_8bit must be a boolean")
        if not isinstance(self.llm_int8_threshold, float): raise TypeError("llm_int8_threshold must be a float")
        if self.llm_int8_skip_modules is not None and not isinstance(self.llm_int8_skip_modules, list): raise TypeError("llm_int8_skip_modules must be a list of strings")
        if not isinstance(self.llm_int8_enable_fp32_cpu_offload, bool): raise TypeError("llm_int8_enable_fp32_cpu_offload must be a boolean")
        if not isinstance(self.llm_int8_has_fp16_weight, bool): raise TypeError("llm_int8_has_fp16_weight must be a boolean")
        if self.sapiens_4bit_compute_dtype is not None and not isinstance(self.sapiens_4bit_compute_dtype, torch.dtype): raise TypeError("sapiens_4bit_compute_dtype must be torch.dtype")
        if self.bnb_4bit_compute_dtype is not None and not isinstance(self.bnb_4bit_compute_dtype, torch.dtype): raise TypeError("bnb_4bit_compute_dtype must be torch.dtype")
        if not isinstance(self.sapiens_4bit_quant_type, str): raise TypeError("sapiens_4bit_quant_type must be a string")
        if not isinstance(self.bnb_4bit_quant_type, str): raise TypeError("bnb_4bit_quant_type must be a string")
        if not isinstance(self.sapiens_4bit_use_double_quant, bool): raise TypeError("sapiens_4bit_use_double_quant must be a boolean")
        if not isinstance(self.bnb_4bit_use_double_quant, bool): raise TypeError("bnb_4bit_use_double_quant must be a boolean")
        if self.load_in_4bit and not version.parse(importlib.metadata.version("sapiens_machine")) >= version.parse("1.0.0"): raise ValueError("4 bit quantization requires sapiens_machine>=1.0.0 - please upgrade your sapiens_machine version")
    def is_quantizable(self): return self.load_in_8bit or self.load_in_4bit
    def quantization_method(self):
        if self.load_in_8bit: return "llm_int8"
        elif self.load_in_4bit and self.sapiens_4bit_quant_type == "fp4" and self.bnb_4bit_quant_type == "fp4": return "fp4"
        elif self.load_in_4bit and self.sapiens_4bit_quant_type == "nf4" and self.bnb_4bit_quant_type == "nf4": return "nf4"
        else: return None
    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["sapiens_4bit_compute_dtype"] = str(output["sapiens_4bit_compute_dtype"]).split(".")[1]
        output["bnb_4bit_compute_dtype"] = str(output["bnb_4bit_compute_dtype"]).split(".")[1]
        output["sapiens_4bit_quant_storage"] = str(output["sapiens_4bit_quant_storage"]).split(".")[1]
        output["bnb_4bit_quant_storage"] = str(output["bnb_4bit_quant_storage"]).split(".")[1]
        output["load_in_4bit"] = self.load_in_4bit
        output["load_in_8bit"] = self.load_in_8bit
        return output
    def __repr__(self):
        config_dict = self.to_dict()
        return f"{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n"
    def to_diff_dict(self) -> Dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = SapiensMachineConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]: serializable_config_dict[key] = value
        return serializable_config_dict
class ExllamaVersion(int, Enum):
    ONE = 1
    TWO = 2
@dataclass
class GPTQConfig(QuantizationConfigMixin):
    def __init__(self, bits: int, tokenizer: Any = None, dataset: Optional[Union[List[str], str]] = None, group_size: int = 128, damp_percent: float = 0.1, desc_act: bool = False, sym: bool = True,
    true_sequential: bool = True, use_cuda_fp16: bool = False, model_seqlen: Optional[int] = None, block_name_to_quantize: Optional[str] = None, module_name_preceding_first_block: Optional[List[str]] = None,
    batch_size: int = 1, pad_token_id: Optional[int] = None, use_exllama: Optional[bool] = None, max_input_length: Optional[int] = None, exllama_config: Optional[Dict[str, Any]] = None, cache_block_outputs: bool = True,
    modules_in_block_to_quantize: Optional[List[List[str]]] = None, **kwargs):
        self.quant_method = QuantizationMethod.GPTQ
        self.bits = bits
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.group_size = group_size
        self.damp_percent = damp_percent
        self.desc_act = desc_act
        self.sym = sym
        self.true_sequential = true_sequential
        self.use_cuda_fp16 = use_cuda_fp16
        self.model_seqlen = model_seqlen
        self.block_name_to_quantize = block_name_to_quantize
        self.module_name_preceding_first_block = module_name_preceding_first_block
        self.batch_size = batch_size
        self.pad_token_id = pad_token_id
        self.use_exllama = use_exllama
        self.max_input_length = max_input_length
        self.exllama_config = exllama_config
        self.disable_exllama = kwargs.pop("disable_exllama", None)
        self.cache_block_outputs = cache_block_outputs
        self.modules_in_block_to_quantize = modules_in_block_to_quantize
        self.post_init()
    def get_loading_attributes(self):
        attibutes_dict = copy.deepcopy(self.__dict__)
        loading_attibutes = ["disable_exllama", "use_exllama", "exllama_config", "use_cuda_fp16", "max_input_length"]
        loading_attibutes_dict = {i: j for i, j in attibutes_dict.items() if i in loading_attibutes}
        return loading_attibutes_dict
    def post_init(self):
        if self.bits not in [2, 3, 4, 8]: raise ValueError(f"Only support quantization to [2,3,4,8] bits but found {self.bits}")
        if self.group_size != -1 and self.group_size <= 0: raise ValueError("group_size must be greater than 0 or equal to -1")
        if not (0 < self.damp_percent < 1): raise ValueError("damp_percent must between 0 and 1.")
        if self.dataset is not None:
            if isinstance(self.dataset, str):
                if self.dataset in ["ptb", "ptb-new"]: raise ValueError(f"{self.dataset} dataset was deprecated. You can only choose between ['wikitext2','c4','c4-new']")
                if self.dataset not in ["wikitext2", "c4", "c4-new"]: raise ValueError(f"You have entered a string value for dataset. You can only choose between ['wikitext2','c4','c4-new'], but we found {self.dataset}")
            elif not isinstance(self.dataset, list): raise ValueError(f"dataset needs to be either a list of string or a value in ['wikitext2','c4','c4-new'], but we found {self.dataset}")
        if self.disable_exllama is None and self.use_exllama is None: self.use_exllama = True
        elif self.disable_exllama is not None and self.use_exllama is None:
            logger.warning("Using `disable_exllama` is deprecated and will be removed in version 4.37. Use `use_exllama` instead and specify the version with `exllama_config`. The value of `use_exllama` will be overwritten by `disable_exllama` passed in `GPTQConfig` or stored in your config file.")
            self.use_exllama = not self.disable_exllama
            self.disable_exllama = None
        elif self.disable_exllama is not None and self.use_exllama is not None: raise ValueError("Cannot specify both `disable_exllama` and `use_exllama`. Please use just `use_exllama`")
        if self.exllama_config is None: self.exllama_config = {"version": ExllamaVersion.ONE}
        else:
            if "version" not in self.exllama_config: raise ValueError("`exllama_config` needs to have a `version` key.")
            elif self.exllama_config["version"] not in [ExllamaVersion.ONE, ExllamaVersion.TWO]:
                exllama_version = self.exllama_config["version"]
                raise ValueError(f"Only supported versions are in [ExllamaVersion.ONE, ExllamaVersion.TWO] - not recognized version {exllama_version}")
        if self.bits == 4 and self.use_exllama:
            if self.exllama_config["version"] == ExllamaVersion.ONE: logger.info("You have activated exllama backend. Note that you can get better inference speed using exllamav2 kernel by setting `exllama_config`.")
            elif self.exllama_config["version"] == ExllamaVersion.TWO:
                optimum_version = version.parse(importlib.metadata.version("optimum"))
                autogptq_version = version.parse(importlib.metadata.version("auto_gptq"))
                if optimum_version <= version.parse("1.13.2") or autogptq_version <= version.parse("0.4.2"): raise ValueError(f"You need optimum > 1.13.2 and auto-gptq > 0.4.2 . Make sure to have that version installed - detected version : optimum {optimum_version} and autogptq {autogptq_version}")
        if self.modules_in_block_to_quantize is not None:
            optimum_version = version.parse(importlib.metadata.version("optimum"))
            if optimum_version < version.parse("1.15.0"): raise ValueError("You current version of `optimum` does not support `modules_in_block_to_quantize` quantization argument, please upgrade `optimum` package to a version superior than 1.15.0 .")
    def to_dict(self):
        config_dict = super().to_dict()
        config_dict.pop("disable_exllama", None)
        return config_dict
    def to_dict_optimum(self):
        quant_dict = self.to_dict()
        quant_dict["disable_exllama"] = not self.use_exllama
        return quant_dict
    @classmethod
    def from_dict_optimum(cls, config_dict):
        if "disable_exllama" in config_dict:
            config_dict["use_exllama"] = not config_dict["disable_exllama"]
            config_dict["disable_exllama"] = None
        config = cls(**config_dict)
        return config
@dataclass
class AwqConfig(QuantizationConfigMixin):
    def __init__(self, bits: int = 4, group_size: int = 128, zero_point: bool = True, version: AWQLinearVersion = AWQLinearVersion.GEMM, backend: AwqBackendPackingMethod = AwqBackendPackingMethod.AUTOAWQ, do_fuse: Optional[bool] = None,
    fuse_max_seq_len: Optional[int] = None, modules_to_fuse: Optional[dict] = None, modules_to_not_convert: Optional[List] = None, exllama_config: Optional[Dict[str, int]] = None, **kwargs):
        self.quant_method = QuantizationMethod.AWQ
        self.bits = bits
        self.group_size = group_size
        self.zero_point = zero_point
        self.version = version
        self.backend = backend
        self.fuse_max_seq_len = fuse_max_seq_len
        self.modules_to_not_convert = modules_to_not_convert
        self.exllama_config = exllama_config
        self.modules_to_fuse = modules_to_fuse
        if do_fuse is None: self.do_fuse = modules_to_fuse is not None and len(modules_to_fuse) > 0
        else: self.do_fuse = do_fuse
        self.fuse_max_seq_len = fuse_max_seq_len
        self.post_init()
    def post_init(self):
        if not torch.cuda.is_available(): raise ValueError("AWQ is only available on GPU")
        if self.backend not in [AwqBackendPackingMethod.AUTOAWQ, AwqBackendPackingMethod.LLMAWQ]: raise ValueError(f"Only supported quantization backends in {AwqBackendPackingMethod.AUTOAWQ} and {AwqBackendPackingMethod.LLMAWQ} - not recognized backend {self.backend}")
        self.version = AWQLinearVersion.from_str(self.version)
        if self.version not in [AWQLinearVersion.GEMM, AWQLinearVersion.GEMV, AWQLinearVersion.EXLLAMA]: raise ValueError(f"Only supported versions are in [AWQLinearVersion.GEMM, AWQLinearVersion.GEMV, AWQLinearVersion.EXLLAMA] - not recognized version {self.version}")
        if self.backend == AwqBackendPackingMethod.LLMAWQ:
            compute_capability = torch.cuda.get_device_capability()
            major, minor = compute_capability
            if major < 8: raise ValueError("LLM-AWQ backend is only supported on GPUs with compute capability >= 8.0")
        if self.do_fuse and self.fuse_max_seq_len is None: raise ValueError("You cannot enable fused modules without specifying a `fuse_max_seq_len`, make sure to pass a valid `fuse_max_seq_len` for your usecase")
        if self.do_fuse:
            awq_version_supports_fusing = False
            MIN_AWQ_VERSION = "0.1.7"
            if is_auto_awq_available(): awq_version_supports_fusing = version.parse(importlib.metadata.version("autoawq")) >= version.parse(MIN_AWQ_VERSION)
            if not awq_version_supports_fusing: raise ValueError(f"You current version of `autoawq` does not support module fusing, please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}.")
        if self.modules_to_not_convert is not None:
            awq_version_supports_non_conversion = False
            MIN_AWQ_VERSION = "0.1.8"
            if is_auto_awq_available(): awq_version_supports_non_conversion = version.parse(importlib.metadata.version("autoawq")) >= version.parse(MIN_AWQ_VERSION)
            if not awq_version_supports_non_conversion: raise ValueError(f"You current version of `autoawq` does not support module quantization skipping, please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}.")
        if self.do_fuse and self.modules_to_fuse is not None:
            required_keys = ["hidden_size", "num_attention_heads", "num_key_value_heads", "mlp", "attention", "layernorm", "use_alibi"]
            if not all(key in self.modules_to_fuse for key in required_keys): raise ValueError(f"Required fields are missing in the fusing mapping, required fields are {required_keys}")
        if self.version == AWQLinearVersion.EXLLAMA:
            awq_version_supports_exllama = False
            MIN_AWQ_VERSION = "0.2.0"
            if is_auto_awq_available(): awq_version_supports_exllama = version.parse(importlib.metadata.version("autoawq")) >= version.parse(MIN_AWQ_VERSION)
            if not awq_version_supports_exllama: raise ValueError(f"You current version of `autoawq` does not support exllama backend, please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}.")
            if self.exllama_config is None: self.exllama_config = {"version": ExllamaVersion.TWO, "max_input_len": 2048, "max_batch_size": 8}
            else:
                if "version" not in self.exllama_config: raise ValueError("`exllama_config` needs to have a `version` key.")
                elif self.exllama_config["version"] not in [ExllamaVersion.ONE, ExllamaVersion.TWO]:
                    exllama_version = self.exllama_config["version"]
                    raise ValueError(f"Only supported versions are in [ExllamaVersion.ONE, ExllamaVersion.TWO] - not recognized version {exllama_version}")
    def get_loading_attributes(self):
        attibutes_dict = copy.deepcopy(self.__dict__)
        loading_attibutes = ["version", "do_fuse", "modules_to_fuse", "fuse_max_seq_len", "exllama_config"]
        loading_attibutes_dict = {i: j for i, j in attibutes_dict.items() if i in loading_attibutes}
        return loading_attibutes_dict
@dataclass
class AqlmConfig(QuantizationConfigMixin):
    def __init__(self, in_group_size: int = 8, out_group_size: int = 1, num_codebooks: int = 1, nbits_per_codebook: int = 16, linear_weights_not_to_quantize: Optional[List[str]] = None, **kwargs):
        self.quant_method = QuantizationMethod.AQLM
        self.in_group_size = in_group_size
        self.out_group_size = out_group_size
        self.num_codebooks = num_codebooks
        self.nbits_per_codebook = nbits_per_codebook
        self.linear_weights_not_to_quantize = linear_weights_not_to_quantize
        self.post_init()
    def post_init(self):
        if not isinstance(self.in_group_size, int): raise TypeError("in_group_size must be a float")
        if not isinstance(self.out_group_size, int): raise TypeError("out_group_size must be a float")
        if not isinstance(self.num_codebooks, int): raise TypeError("num_codebooks must be a float")
        if not isinstance(self.nbits_per_codebook, int): raise TypeError("nbits_per_codebook must be a float")
        if self.linear_weights_not_to_quantize is not None and not isinstance(self.linear_weights_not_to_quantize, list): raise ValueError("linear_weights_not_to_quantize must be a list of strings")
        if self.linear_weights_not_to_quantize is None: self.linear_weights_not_to_quantize = []
@dataclass
class QuantoConfig(QuantizationConfigMixin):
    def __init__(self, weights="int8", activations=None, modules_to_not_convert: Optional[List] = None, **kwargs):
        self.quant_method = QuantizationMethod.QUANTO
        self.weights = weights
        self.activations = activations
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        accepted_weights = ["float8", "int8", "int4", "int2"]
        accepted_activations = [None, "int8", "float8"]
        if self.weights not in accepted_weights: raise ValueError(f"Only support weights in {accepted_weights} but found {self.weights}")
        if self.activations not in accepted_activations: raise ValueError(f"Only support weights in {accepted_activations} but found {self.activations}")
@dataclass
class EetqConfig(QuantizationConfigMixin):
    def __init__(self, weights: str = "int8", modules_to_not_convert: Optional[List] = None, **kwargs):
        self.quant_method = QuantizationMethod.EETQ
        self.weights = weights
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        accepted_weights = ["int8"]
        if self.weights not in accepted_weights: raise ValueError(f"Only support weights in {accepted_weights} but found {self.weights}")
class CompressedTensorsConfig(QuantizationConfigMixin):
    def __init__(self, config_groups: Dict[str, Union["QuantizationScheme", List[str]]] = None, format: str = "dense", quantization_status: "QuantizationStatus" = "initialized",
    kv_cache_scheme: Optional["QuantizationArgs"] = None, global_compression_ratio: Optional[float] = None, ignore: Optional[List[str]] = None, sparsity_config: Dict[str, Any] = None, quant_method: str = "compressed-tensors", **kwargs):
        from compressed_tensors import QuantizationConfig
        from compressed_tensors.config import SparsityCompressionConfig
        self.quantization_config = None
        self.sparsity_config = None
        if config_groups: self.quantization_config = QuantizationConfig.parse_obj({"config_groups": config_groups, "quant_method": quant_method, "format": format, "quantization_status": quantization_status, "kv_cache_scheme": kv_cache_scheme,
        "global_compression_ratio": global_compression_ratio, "ignore": ignore, **kwargs})
        if sparsity_config: self.sparsity_config = SparsityCompressionConfig.load_from_registry(sparsity_config.get("format"), **sparsity_config)
        super().__init__(quant_method=QuantizationMethod.COMPRESSED_TENSORS)
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        if "quantization_config" in config_dict: config_dict = dict(sparsity_config=config_dict.get("sparsity_config"), **config_dict["quantization_config"])
        return super().from_dict(config_dict, return_unused_kwargs=return_unused_kwargs, **kwargs)
    def to_dict(self) -> Dict[str, Any]:
        quantization_config = self.quantization_config.dict() if self.quantization_config is not None else None
        sparsity_config = self.sparsity_config.dict() if self.sparsity_config is not None else None
        return {"quantization_config": quantization_config, "sparsity_config": sparsity_config}
    def to_diff_dict(self) -> Dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = CompressedTensorsConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]: serializable_config_dict[key] = value
        return serializable_config_dict
@dataclass
class FbgemmFp8Config(QuantizationConfigMixin):
    def __init__(self, activation_scale_ub: float = 1200.0, modules_to_not_convert: Optional[List] = None, **kwargs):
        self.quant_method = QuantizationMethod.FBGEMM_FP8
        self.activation_scale_ub = activation_scale_ub
        self.modules_to_not_convert = modules_to_not_convert
    def get_loading_attributes(self):
        attibutes_dict = copy.deepcopy(self.__dict__)
        loading_attibutes = ["activation_scale_ub"]
        loading_attibutes_dict = {i: j for i, j in attibutes_dict.items() if i in loading_attibutes}
        return loading_attibutes_dict
@dataclass
class TorchAoConfig(QuantizationConfigMixin):
    def __init__(self, quant_type: str, modules_to_not_convert: Optional[List] = None, **kwargs):
        self.quant_method = QuantizationMethod.TORCHAO
        self.quant_type = quant_type
        self.modules_to_not_convert = modules_to_not_convert
        self.kwargs = kwargs
        self._STR_TO_METHOD = {}
        if is_torchao_available():
            from torchao.quantization import (int4_weight_only, int8_dynamic_activation_int8_weight, int8_weight_only)
            self._STR_TO_METHOD = {"int4_weight_only": int4_weight_only, "int8_weight_only": int8_weight_only, "int8_dynamic_activation_int8_weight": int8_dynamic_activation_int8_weight}
        else: raise ValueError("TorchAoConfig requires torchao to be installed, please install with `pip install torchao`")
        self.post_init()
    def post_init(self):
        if not version.parse(importlib.metadata.version("torchao")) >= version.parse("0.4.0"): raise ValueError("Requires torchao 0.4.0 version and above")
        if self.quant_type not in self._STR_TO_METHOD.keys(): raise ValueError(f"Requested quantization type: {self.quant_type} is not supported yet, please add support in TorchAoConfig and TorchAoHfQuantizer.")
        method = self._STR_TO_METHOD[self.quant_type]
        sig = signature(method)
        all_kwargs = [param.name for param in sig.parameters.values() if param.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]]
        for k in self.kwargs:
            if k not in all_kwargs: raise ValueError(f"Unexpected keyword arg: {k} for API: {method}, accepted keyword args are: {all_kwargs}")
    def get_apply_tensor_subclass(self): return self._STR_TO_METHOD[self.quant_type](**self.kwargs)
    def __repr__(self): return f"{self.quant_type}({', '.join(str(k) + '=' + str(v) for k, v in self.kwargs.items())})"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
