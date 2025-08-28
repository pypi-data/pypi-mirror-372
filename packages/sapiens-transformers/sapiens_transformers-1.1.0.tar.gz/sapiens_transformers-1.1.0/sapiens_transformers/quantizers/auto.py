"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from typing import Dict, Optional, Union
from ..models.auto.configuration_auto import AutoConfig
from ..utils.quantization_config import (AqlmConfig, AwqConfig, SapiensMachineConfig, CompressedTensorsConfig, EetqConfig, FbgemmFp8Config, GPTQConfig,
HqqConfig, QuantizationConfigMixin, QuantizationMethod, QuantoConfig, TorchAoConfig)
from .quantizer_aqlm import AqlmHfQuantizer
from .quantizer_awq import AwqQuantizer
from .quantizer_sapiens_4bit import Sapiens4BitHfQuantizer
from .quantizer_sapiens_8bit import Sapiens8BitHfQuantizer
from .quantizer_compressed_tensors import CompressedTensorsHfQuantizer
from .quantizer_eetq import EetqHfQuantizer
from .quantizer_fbgemm_fp8 import FbgemmFp8HfQuantizer
from .quantizer_gptq import GptqHfQuantizer
from .quantizer_hqq import HqqHfQuantizer
from .quantizer_quanto import QuantoHfQuantizer
from .quantizer_torchao import TorchAoHfQuantizer
AUTO_QUANTIZER_MAPPING = {"awq": AwqQuantizer, "sapiens_machine_4bit": Sapiens4BitHfQuantizer, "sapiens_machine_8bit": Sapiens8BitHfQuantizer, "gptq": GptqHfQuantizer,
"aqlm": AqlmHfQuantizer, "quanto": QuantoHfQuantizer, "eetq": EetqHfQuantizer, "hqq": HqqHfQuantizer, "compressed-tensors": CompressedTensorsHfQuantizer,
"fbgemm_fp8": FbgemmFp8HfQuantizer, "torchao": TorchAoHfQuantizer}
AUTO_QUANTIZATION_CONFIG_MAPPING = {"awq": AwqConfig, "sapiens_machine_4bit": SapiensMachineConfig, "sapiens_machine_8bit": SapiensMachineConfig, "eetq": EetqConfig,
"gptq": GPTQConfig, "aqlm": AqlmConfig, "quanto": QuantoConfig, "hqq": HqqConfig, "compressed-tensors": CompressedTensorsConfig, "fbgemm_fp8": FbgemmFp8Config,
"torchao": TorchAoConfig}
class AutoQuantizationConfig:
    @classmethod
    def from_dict(cls, quantization_config_dict: Dict):
        quant_method = quantization_config_dict.get("quant_method", None)
        if quantization_config_dict.get("load_in_8bit", False) or quantization_config_dict.get("load_in_4bit", False):
            suffix = "_4bit" if quantization_config_dict.get("load_in_4bit", False) else "_8bit"
            quant_method = QuantizationMethod.SAPIENS_MACHINE + suffix
        elif quant_method is None: raise ValueError("The model's quantization config from the arguments has no `quant_method` attribute. Make sure that the model has been correctly quantized")
        if quant_method not in AUTO_QUANTIZATION_CONFIG_MAPPING.keys(): raise ValueError(f"Unknown quantization type, got {quant_method} - supported types are: {list(AUTO_QUANTIZER_MAPPING.keys())}")
        target_cls = AUTO_QUANTIZATION_CONFIG_MAPPING[quant_method]
        return target_cls.from_dict(quantization_config_dict)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        model_config = AutoConfig.from_pretrained(pretrained_model_name_or_path, **kwargs)
        if getattr(model_config, "quantization_config", None) is None: raise ValueError(f"Did not found a `quantization_config` in {pretrained_model_name_or_path}. Make sure that the model is correctly quantized.")
        quantization_config_dict = model_config.quantization_config
        quantization_config = cls.from_dict(quantization_config_dict)
        quantization_config.update(kwargs)
        return quantization_config
class AutoHfQuantizer:
    @classmethod
    def from_config(cls, quantization_config: Union[QuantizationConfigMixin, Dict], **kwargs):
        if isinstance(quantization_config, dict): quantization_config = AutoQuantizationConfig.from_dict(quantization_config)
        quant_method = quantization_config.quant_method
        if quant_method == QuantizationMethod.SAPIENS_MACHINE:
            if quantization_config.load_in_8bit: quant_method += "_8bit"
            else: quant_method += "_4bit"
        if quant_method not in AUTO_QUANTIZER_MAPPING.keys(): raise ValueError(f"Unknown quantization type, got {quant_method} - supported types are: {list(AUTO_QUANTIZER_MAPPING.keys())}")
        target_cls = AUTO_QUANTIZER_MAPPING[quant_method]
        return target_cls(quantization_config, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        quantization_config = AutoQuantizationConfig.from_pretrained(pretrained_model_name_or_path, **kwargs)
        return cls.from_config(quantization_config)
    @classmethod
    def merge_quantization_configs(cls, quantization_config: Union[dict, QuantizationConfigMixin], quantization_config_from_args: Optional[QuantizationConfigMixin]):
        if quantization_config_from_args is not None: warning_msg = ("You passed `quantization_config` or equivalent parameters to `from_pretrained` but the model you're loading already has a `quantization_config` attribute. The `quantization_config` from the model will be used.")
        else: warning_msg = ""
        if isinstance(quantization_config, dict): quantization_config = AutoQuantizationConfig.from_dict(quantization_config)
        if (isinstance(quantization_config, (GPTQConfig, AwqConfig, FbgemmFp8Config)) and quantization_config_from_args is not None):
            loading_attr_dict = quantization_config_from_args.get_loading_attributes()
            for attr, val in loading_attr_dict.items(): setattr(quantization_config, attr, val)
            warning_msg += f"However, loading attributes (e.g. {list(loading_attr_dict.keys())}) will be overwritten with the one you passed to `from_pretrained`. The rest will be ignored."
        if warning_msg != "": warnings.warn(warning_msg)
        return quantization_config
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
