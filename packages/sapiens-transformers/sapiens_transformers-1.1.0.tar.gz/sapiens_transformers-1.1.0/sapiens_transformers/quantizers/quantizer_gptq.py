"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
from typing import TYPE_CHECKING, Optional
from packaging import version
from .base import HfQuantizer
if TYPE_CHECKING: from ..modeling_utils import PreTrainedModel
from ..utils import is_auto_gptq_available, is_optimum_available, is_torch_available, logging
from ..utils.quantization_config import GPTQConfig, QuantizationConfigMixin
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class GptqHfQuantizer(HfQuantizer):
    requires_calibration = False
    required_packages = ["optimum", "auto_gptq"]
    optimum_quantizer = None
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
        from optimum.gptq import GPTQQuantizer
        self.optimum_quantizer = GPTQQuantizer.from_dict(self.quantization_config.to_dict_optimum())
    def validate_environment(self, *args, **kwargs):
        gptq_supports_cpu = version.parse(importlib.metadata.version("auto-gptq")) > version.parse("0.4.2")
        if not gptq_supports_cpu and not torch.cuda.is_available(): raise RuntimeError("GPU is required to quantize or run quantize model.")
        elif not (is_optimum_available() and is_auto_gptq_available()): raise ImportError("Loading a GPTQ quantized model requires optimum (`pip install optimum`) and auto-gptq library (`pip install auto-gptq`)")
        elif version.parse(importlib.metadata.version("auto_gptq")) < version.parse("0.4.2"): raise ImportError("You need a version of auto_gptq >= 0.4.2 to use GPTQ: `pip install --upgrade auto-gptq`")
    def update_torch_dtype(self, torch_dtype: "torch.dtype") -> "torch.dtype":
        if torch_dtype is None: torch_dtype = torch.float16
        elif torch_dtype != torch.float16: logger.info("We suggest you to set `torch_dtype=torch.float16` for better efficiency with GPTQ.")
        return torch_dtype
    def _process_model_before_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if model.__class__.main_input_name != "input_ids": raise RuntimeError("We can only quantize pure text model.")
        if self.pre_quantized: model = self.optimum_quantizer.convert_model(model)
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if self.pre_quantized: model = self.optimum_quantizer.post_init_model(model)
        else:
            if self.quantization_config.tokenizer is None: self.quantization_config.tokenizer = model.name_or_path
            self.optimum_quantizer.quantize_model(model, self.quantization_config.tokenizer)
            model.config.quantization_config = GPTQConfig.from_dict(self.optimum_quantizer.to_dict())
    @property
    def is_trainable(self, model: Optional["PreTrainedModel"] = None): return True
    @property
    def is_serializable(self): return True
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
