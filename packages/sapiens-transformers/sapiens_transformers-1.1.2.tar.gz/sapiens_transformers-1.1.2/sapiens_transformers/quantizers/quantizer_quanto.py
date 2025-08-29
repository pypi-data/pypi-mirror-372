"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import importlib
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from packaging import version
from .base import HfQuantizer
from .quantizers_utils import get_module_from_name
if TYPE_CHECKING: from ..modeling_utils import PreTrainedModel
from ..utils import is_sapiens_accelerator_available, is_quanto_available, is_torch_available, logging
from ..utils.quantization_config import QuantoConfig
if is_torch_available(): import torch
logger = logging.get_logger(__name__)
class QuantoHfQuantizer(HfQuantizer):
    required_packages = ["quanto", "sapiens_accelerator"]
    requires_parameters_quantization = True
    requires_calibration = False
    def __init__(self, quantization_config: QuantoConfig, **kwargs):
        super().__init__(quantization_config, **kwargs)
        self.post_init()
    def post_init(self):
        if self.quantization_config.activations is not None and not self.pre_quantized: raise ValueError("We don't support quantizing the activations with transformers library. Use quanto library for more complex use cases such as activations quantization, calibration and quantization aware training.")
    def validate_environment(self, *args, **kwargs):
        if not is_quanto_available(): raise ImportError("Loading a quanto quantized model requires quanto library (`pip install quanto`)")
        if not is_sapiens_accelerator_available(): raise ImportError("Loading a quanto quantized model requires sapiens_accelerator library (`pip install sapiens_accelerator`)")
    def update_device_map(self, device_map):
        if device_map is None:
            device_map = {"": "cpu"}
            logger.info("The device_map was not initialized. Setting device_map to {'':'cpu'}. If you want to use the model for inference, please set device_map ='auto'")
        return device_map
    def update_torch_dtype(self, torch_dtype: "torch.dtype") -> "torch.dtype":
        if torch_dtype is None:
            logger.info("You did not specify `torch_dtype` in `from_pretrained`. Setting it to `torch.float32`.")
            torch_dtype = torch.float32
        return torch_dtype
    def update_missing_keys(self, model, missing_keys: List[str], prefix: str) -> List[str]:
        import quanto
        not_missing_keys = []
        for name, module in model.named_modules():
            if isinstance(module, quanto.QModuleMixin):
                for missing in missing_keys:
                    if ((name in missing or name in f"{prefix}.{missing}") and not missing.endswith(".weight") and not missing.endswith(".bias")): not_missing_keys.append(missing)
        return [k for k in missing_keys if k not in not_missing_keys]
    def check_quantized_param(self, model: "PreTrainedModel", param_value: "torch.Tensor", param_name: str, state_dict: Dict[str, Any], **kwargs) -> bool:
        import quanto
        device_map = kwargs.get("device_map", None)
        param_device = kwargs.get("param_device", None)
        if device_map is not None and param_device is not None:
            device_map_values = set(device_map.values())
            if param_device == "cpu" and len(device_map_values) > 1:
                if not (device_map_values == {"cpu"} or device_map_values == {"cpu", "disk"}): return False
        module, tensor_name = get_module_from_name(model, param_name)
        if isinstance(module, quanto.QModuleMixin) and "weight" in tensor_name: return not module.frozen
        else: return False
    def adjust_max_memory(self, max_memory: Dict[str, Union[int, str]]) -> Dict[str, Union[int, str]]:
        max_memory = {key: val * 0.90 for key, val in max_memory.items()}
        return max_memory
    def create_quantized_param(self, model: "PreTrainedModel", param_value: "torch.Tensor", param_name: str, target_device: "torch.device", *args, **kwargs):
        from sapiens_accelerator.utils import set_module_tensor_to_device
        set_module_tensor_to_device(model, param_name, target_device, param_value)
        module, _ = get_module_from_name(model, param_name)
        module.freeze()
        module.weight.requires_grad = False
    def adjust_target_dtype(self, target_dtype: "torch.dtype") -> "torch.dtype":
        if version.parse(importlib.metadata.version("sapiens_accelerator")) > version.parse("0.0.0"):
            from sapiens_accelerator.utils import CustomDtype
            mapping = {"int8": torch.int8, "float8": CustomDtype.FP8, "int4": CustomDtype.INT4, "int2": CustomDtype.INT2}
            target_dtype = mapping[self.quantization_config.weights]
            return target_dtype
        else: raise ValueError("You are using `device_map='auto'` on a quanto quantized model. To automatically compute the appropriate device map, you should upgrade your `sapiens_accelerator` library, `pip install --upgrade sapiens_accelerator` or install it from source.")
    def _process_model_before_weight_loading(self, model: "PreTrainedModel", keep_in_fp32_modules: List[str] = [], **kwargs):
        from ..integrations import get_keys_to_not_convert, replace_with_quanto_layers
        if self.quantization_config.modules_to_not_convert is None: self.modules_to_not_convert = get_keys_to_not_convert(model)
        else: self.modules_to_not_convert = self.quantization_config.modules_to_not_convert
        if not isinstance(self.modules_to_not_convert, list): self.modules_to_not_convert = [self.modules_to_not_convert]
        self.modules_to_not_convert.extend(keep_in_fp32_modules)
        model, _ = replace_with_quanto_layers(model, modules_to_not_convert=self.modules_to_not_convert, quantization_config=self.quantization_config)
        model.config.quantization_config = self.quantization_config
    def _process_model_after_weight_loading(self, model): return model
    @property
    def is_trainable(self, model: Optional["PreTrainedModel"] = None): return False
    @property
    def is_serializable(self): return False
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
