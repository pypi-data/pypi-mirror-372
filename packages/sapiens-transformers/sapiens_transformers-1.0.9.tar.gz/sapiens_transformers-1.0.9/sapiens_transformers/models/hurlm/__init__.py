"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import SapiensTechnologyModule, SAPIENS_TECHNOLOGY_CHECKING
from ...utils.import_utils import define_import_structure
if SAPIENS_TECHNOLOGY_CHECKING:
    from .image_processing_hurlm import *
    from .configuration_hurlm import *
    from .processing_hurlm import *
    from .modeling_hurlm import *
else:
    import sys
    _file = globals()["__file__"]
    name, import_structure, module_spec = __name__, define_import_structure(_file), __spec__
    sys.modules[__name__] = SapiensTechnologyModule(name, _file, import_structure, module_spec)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
