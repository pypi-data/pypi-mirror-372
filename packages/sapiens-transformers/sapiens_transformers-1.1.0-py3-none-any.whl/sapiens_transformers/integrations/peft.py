"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import inspect
import warnings
from typing import Any, Dict, List, Optional, Union
from ..utils import (check_peft_version, find_adapter_config_file, is_sapiens_accelerator_available, is_peft_available, is_torch_available, logging)
if is_torch_available(): import torch
if is_sapiens_accelerator_available():
    from sapiens_accelerator import dispatch_model
    from sapiens_accelerator.utils import get_balanced_memory, infer_auto_device_map
MIN_PEFT_VERSION = "0.5.0"
logger = logging.get_logger(__name__)
class PeftAdapterMixin:
    _hf_peft_config_loaded = False
    def load_adapter(self, peft_model_id: Optional[str] = None, adapter_name: Optional[str] = None, revision: Optional[str] = None, token: Optional[str] = None,
    device_map: Optional[str] = "auto", max_memory: Optional[str] = None, offload_folder: Optional[str] = None, offload_index: Optional[int] = None,
    peft_config: Dict[str, Any] = None, adapter_state_dict: Optional[Dict[str, "torch.Tensor"]] = None, adapter_kwargs: Optional[Dict[str, Any]] = None) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        adapter_name = adapter_name if adapter_name is not None else "default"
        if adapter_kwargs is None: adapter_kwargs = {}
        from peft import PeftConfig, inject_adapter_in_model, load_peft_weights
        from peft.utils import set_peft_model_state_dict
        if self._hf_peft_config_loaded and adapter_name in self.peft_config: raise ValueError(f"Adapter with name {adapter_name} already exists. Please use a different name.")
        if peft_model_id is None and (adapter_state_dict is None and peft_config is None): raise ValueError("You should either pass a `peft_model_id` or a `peft_config` and `adapter_state_dict` to load an adapter.")
        if "device" not in adapter_kwargs: device = self.device if not hasattr(self, "hf_device_map") else list(self.hf_device_map.values())[0]
        else: device = adapter_kwargs.pop("device")
        if isinstance(device, torch.device): device = str(device)
        if revision is not None and "revision" not in adapter_kwargs: adapter_kwargs["revision"] = revision
        elif revision is not None and "revision" in adapter_kwargs and revision != adapter_kwargs["revision"]: logger.error("You passed a `revision` argument both in `adapter_kwargs` and as a standalone argument. The one in `adapter_kwargs` will be used.")
        if "token" in adapter_kwargs: token = adapter_kwargs.pop("token")
        if peft_config is None:
            adapter_config_file = find_adapter_config_file(peft_model_id, token=token, **adapter_kwargs)
            if adapter_config_file is None: raise ValueError(f"adapter model file not found in {peft_model_id}. Make sure you are passing the correct path to the adapter model.")
            peft_config = PeftConfig.from_pretrained(peft_model_id, token=token, **adapter_kwargs)
        inject_adapter_in_model(peft_config, self, adapter_name)
        if not self._hf_peft_config_loaded: self._hf_peft_config_loaded = True
        if peft_model_id is not None: adapter_state_dict = load_peft_weights(peft_model_id, token=token, device=device, **adapter_kwargs)
        processed_adapter_state_dict = {}
        prefix = "base_model.model."
        for key, value in adapter_state_dict.items():
            if key.startswith(prefix): new_key = key[len(prefix) :]
            else: new_key = key
            processed_adapter_state_dict[new_key] = value
        incompatible_keys = set_peft_model_state_dict(self, processed_adapter_state_dict, adapter_name)
        if incompatible_keys is not None:
            if hasattr(incompatible_keys, "unexpected_keys") and len(incompatible_keys.unexpected_keys) > 0: logger.warning(f"Loading adapter weights from {peft_model_id} led to unexpected keys not found in the model:  {incompatible_keys.unexpected_keys}. ")
        if ((getattr(self, "hf_device_map", None) is not None) and (len(set(self.hf_device_map.values()).intersection({"cpu", "disk"})) > 0) and len(self.peft_config) == 1): self._dispatch_sapiens_accelerator_model(device_map=device_map, max_memory=max_memory, offload_folder=offload_folder, offload_index=offload_index)
    def add_adapter(self, adapter_config, adapter_name: Optional[str] = None) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        from peft import PeftConfig, inject_adapter_in_model
        adapter_name = adapter_name or "default"
        if not self._hf_peft_config_loaded: self._hf_peft_config_loaded = True
        elif adapter_name in self.peft_config: raise ValueError(f"Adapter with name {adapter_name} already exists. Please use a different name.")
        if not isinstance(adapter_config, PeftConfig): raise TypeError(f"adapter_config should be an instance of PeftConfig. Got {type(adapter_config)} instead.")
        adapter_config.base_model_name_or_path = self.__dict__.get("name_or_path", None)
        inject_adapter_in_model(adapter_config, self, adapter_name)
        self.set_adapter(adapter_name)
    def set_adapter(self, adapter_name: Union[List[str], str]) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError("No adapter loaded. Please load an adapter first.")
        elif isinstance(adapter_name, list):
            missing = set(adapter_name) - set(self.peft_config)
            if len(missing) > 0: raise ValueError(f"Following adapter(s) could not be found: {', '.join(missing)}. Make sure you are passing the correct adapter name(s). current loaded adapters are: {list(self.peft_config.keys())}")
        elif adapter_name not in self.peft_config: raise ValueError(f"Adapter with name {adapter_name} not found. Please pass the correct adapter name among {list(self.peft_config.keys())}")
        from peft.tuners.tuners_utils import BaseTunerLayer
        from peft.utils import ModulesToSaveWrapper
        _adapters_has_been_set = False
        for _, module in self.named_modules():
            if isinstance(module, (BaseTunerLayer, ModulesToSaveWrapper)):
                if hasattr(module, "set_adapter"): module.set_adapter(adapter_name)
                else: module.active_adapter = adapter_name
                _adapters_has_been_set = True
        if not _adapters_has_been_set: raise ValueError("Did not succeeded in setting the adapter. Please make sure you are using a model that supports adapters.")
    def disable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        from peft.utils import ModulesToSaveWrapper
        for _, module in self.named_modules():
            if isinstance(module, (BaseTunerLayer, ModulesToSaveWrapper)):
                if hasattr(module, "enable_adapters"): module.enable_adapters(enabled=False)
                else: module.disable_adapters = True
    def enable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, "enable_adapters"): module.enable_adapters(enabled=True)
                else: module.disable_adapters = False
    def active_adapters(self) -> List[str]:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not is_peft_available(): raise ImportError("PEFT is not available. Please install PEFT to use this function: `pip install peft`.")
        if not self._hf_peft_config_loaded: raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                active_adapters = module.active_adapter
                break
        if isinstance(active_adapters, str): active_adapters = [active_adapters]
        return active_adapters
    def active_adapter(self) -> str:
        warnings.warn("The `active_adapter` method is deprecated and will be removed in a future version.", FutureWarning)
        return self.active_adapters()[0]
    def get_adapter_state_dict(self, adapter_name: Optional[str] = None) -> dict:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded: raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft import get_peft_model_state_dict
        if adapter_name is None: adapter_name = self.active_adapter()
        adapter_state_dict = get_peft_model_state_dict(self, adapter_name=adapter_name)
        return adapter_state_dict
    def _dispatch_sapiens_accelerator_model(self, device_map: str, max_memory: Optional[int] = None, offload_folder: Optional[str] = None, offload_index: Optional[int] = None) -> None:
        dispatch_model_kwargs = {}
        if "offload_index" in inspect.signature(dispatch_model).parameters: dispatch_model_kwargs["offload_index"] = offload_index
        no_split_module_classes = self._no_split_modules
        if device_map != "sequential": max_memory = get_balanced_memory(self, max_memory=max_memory, no_split_module_classes=no_split_module_classes, low_zero=(device_map == "balanced_low_0"))
        if isinstance(device_map, str): device_map = infer_auto_device_map(self, max_memory=max_memory, no_split_module_classes=no_split_module_classes)
        dispatch_model(self, device_map=device_map, offload_dir=offload_folder, **dispatch_model_kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
