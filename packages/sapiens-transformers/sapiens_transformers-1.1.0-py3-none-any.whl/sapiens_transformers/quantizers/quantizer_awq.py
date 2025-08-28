"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib.metadata
from typing import TYPE_CHECKING
from packaging import version
from .base import HfQuantizer
if TYPE_CHECKING: from ..modeling_utils import PreTrainedModel
from ..utils import is_sapiens_accelerator_available, is_auto_awq_available, is_torch_available, logging
from ..utils.quantization_config import AWQLinearVersion
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class AwqQuantizer(HfQuantizer):
    requires_calibration = True
    required_packages = ["awq", "sapiens_accelerator"]
    def __init__(self, quantization_config, **kwargs): super().__init__(quantization_config, **kwargs)
    def validate_environment(self, device_map, **kwargs):
        if not torch.cuda.is_available(): raise RuntimeError("GPU is required to run AWQ quantized model.")
        if not is_auto_awq_available(): raise ImportError("Loading an AWQ quantized model requires auto-awq library (`pip install autoawq`)")
        if not is_sapiens_accelerator_available(): raise ImportError("Loading an AWQ quantized model requires sapiens_accelerator (`pip install sapiens_accelerator`)")
        if device_map is None: logger.warning_once("You have loaded an AWQ model on CPU and have a CUDA device available, make sure to set your model on a GPU device in order to run your model.")
        elif device_map is not None:
            if isinstance(device_map, dict) and ("cpu" in device_map.values() or "disk" in device_map.values()): raise ValueError("You are attempting to load an AWQ model with a device_map that contains a CPU or disk device. This is not supported. Please remove the CPU or disk device from the device_map.")
    def update_torch_dtype(self, torch_dtype):
        if torch_dtype is None: torch_dtype = torch.float16
        elif torch_dtype != torch.float16: logger.warning("We suggest you to set `torch_dtype=torch.float16` for better efficiency with AWQ.")
        return torch_dtype
    def _process_model_before_weight_loading(self, model: "PreTrainedModel", **kwargs):
        from ..integrations import get_keys_to_not_convert, replace_quantization_scales, replace_with_awq_linear
        self.modules_to_not_convert = get_keys_to_not_convert(model)
        if self.quantization_config.modules_to_not_convert is not None: self.modules_to_not_convert.extend(self.quantization_config.modules_to_not_convert)
        model, has_been_replaced = replace_with_awq_linear(model, quantization_config=self.quantization_config, modules_to_not_convert=self.modules_to_not_convert)
        model = replace_quantization_scales(model, model.config.model_type)
        if not has_been_replaced: logger.warning("You are loading an AWQ model but no linear modules were found in your model. Please double check your model architecture, or submit an issue on github if you think this is a bug.")
    def _process_model_after_weight_loading(self, model):
        if self.quantization_config.do_fuse:
            from ..integrations import fuse_awq_modules
            model = fuse_awq_modules(model, self.quantization_config)
            model._awq_is_fused = True
        if self.quantization_config.version == AWQLinearVersion.EXLLAMA:
            from ..integrations import post_init_awq_exllama_modules
            model = post_init_awq_exllama_modules(model, self.quantization_config.exllama_config)
    @property
    def is_serializable(self):
        if self.quantization_config.do_fuse:
            logger.warning("You cannot save an AWQ model that uses fused modules!")
            return False
        if self.quantization_config.version == AWQLinearVersion.EXLLAMA:
            logger.warning("You cannot save an AWQ model that uses Exllama backend!")
            return False
        return True
    @property
    def is_trainable(self):
        MIN_AWQ_VERSION_FOR_PEFT = "0.2.0"
        return version.parse(importlib.metadata.version("autoawq")) >= version.parse(MIN_AWQ_VERSION_FOR_PEFT)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
