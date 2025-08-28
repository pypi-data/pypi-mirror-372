'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from packaging import version
from .import_utils import is_sapiens_accelerator_available
if is_sapiens_accelerator_available(): import sapiens_accelerator
def apply_forward_hook(method):
    if not is_sapiens_accelerator_available(): return method
    sapiens_accelerator_version = version.parse(sapiens_accelerator.__version__).base_version
    if version.parse(sapiens_accelerator_version) < version.parse('0.17.0'): return method
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '_hf_hook') and hasattr(self._hf_hook, 'pre_forward'): self._hf_hook.pre_forward(self)
        return method(self, *args, **kwargs)
    return wrapper
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
