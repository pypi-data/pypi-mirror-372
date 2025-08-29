'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Dict, Optional, Union
from .sapiens_machine import Sapiens4BitDiffusersQuantizer, Sapiens8BitDiffusersQuantizer
from .gguf import GGUFQuantizer
from .quantization_config import SapiensMachineConfig, GGUFQuantizationConfig, QuantizationConfigMixin, QuantizationMethod, TorchAoConfig
from .torchao import TorchAoHfQuantizer
AUTO_QUANTIZER_MAPPING = {'sapiens_machine_4bit': Sapiens4BitDiffusersQuantizer, 'sapiens_machine_8bit': Sapiens8BitDiffusersQuantizer, 'gguf': GGUFQuantizer, 'torchao': TorchAoHfQuantizer}
AUTO_QUANTIZATION_CONFIG_MAPPING = {'sapiens_machine_4bit': SapiensMachineConfig, 'sapiens_machine_8bit': SapiensMachineConfig, 'gguf': GGUFQuantizationConfig, 'torchao': TorchAoConfig}
class DiffusersAutoQuantizer:
    @classmethod
    def from_dict(cls, quantization_config_dict: Dict):
        quant_method = quantization_config_dict.get('quant_method', None)
        if quantization_config_dict.get('load_in_8bit', False) or quantization_config_dict.get('load_in_4bit', False):
            suffix = '_4bit' if quantization_config_dict.get('load_in_4bit', False) else '_8bit'
            quant_method = QuantizationMethod.SAPIENS_MACHINE + suffix
        elif quant_method is None: raise ValueError("The model's quantization config from the arguments has no `quant_method` attribute. Make sure that the model has been correctly quantized")
        if quant_method not in AUTO_QUANTIZATION_CONFIG_MAPPING.keys(): raise ValueError(f'Unknown quantization type, got {quant_method} - supported types are: {list(AUTO_QUANTIZER_MAPPING.keys())}')
        target_cls = AUTO_QUANTIZATION_CONFIG_MAPPING[quant_method]
        return target_cls.from_dict(quantization_config_dict)
    @classmethod
    def from_config(cls, quantization_config: Union[QuantizationConfigMixin, Dict], **kwargs):
        if isinstance(quantization_config, dict): quantization_config = cls.from_dict(quantization_config)
        quant_method = quantization_config.quant_method
        if quant_method == QuantizationMethod.SAPIENS_MACHINE:
            if quantization_config.load_in_8bit: quant_method += '_8bit'
            else: quant_method += '_4bit'
        if quant_method not in AUTO_QUANTIZER_MAPPING.keys(): raise ValueError(f'Unknown quantization type, got {quant_method} - supported types are: {list(AUTO_QUANTIZER_MAPPING.keys())}')
        target_cls = AUTO_QUANTIZER_MAPPING[quant_method]
        return target_cls(quantization_config, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        model_config = cls.load_config(pretrained_model_name_or_path, **kwargs)
        if getattr(model_config, 'quantization_config', None) is None: raise ValueError(f'Did not found a `quantization_config` in {pretrained_model_name_or_path}. Make sure that the model is correctly quantized.')
        quantization_config_dict = model_config.quantization_config
        quantization_config = cls.from_dict(quantization_config_dict)
        quantization_config.update(kwargs)
        return cls.from_config(quantization_config)
    @classmethod
    def merge_quantization_configs(cls, quantization_config: Union[dict, QuantizationConfigMixin], quantization_config_from_args: Optional[QuantizationConfigMixin]):
        if isinstance(quantization_config, dict): quantization_config = cls.from_dict(quantization_config)
        return quantization_config
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
