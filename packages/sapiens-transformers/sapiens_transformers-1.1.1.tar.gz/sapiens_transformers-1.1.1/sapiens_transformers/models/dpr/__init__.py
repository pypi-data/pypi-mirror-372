"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_dpr': ['DPRConfig'], 'tokenization_dpr': ['DPRContextEncoderTokenizer', 'DPRQuestionEncoderTokenizer', 'DPRReaderOutput', 'DPRReaderTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_dpr_fast"] = ["DPRContextEncoderTokenizerFast", "DPRQuestionEncoderTokenizerFast", "DPRReaderTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_dpr"] = ["DPRContextEncoder", "DPRPretrainedContextEncoder", "DPRPreTrainedModel", "DPRPretrainedQuestionEncoder", "DPRPretrainedReader", "DPRQuestionEncoder", "DPRReader"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_dpr"] = ["TFDPRContextEncoder", "TFDPRPretrainedContextEncoder", "TFDPRPretrainedQuestionEncoder", "TFDPRPretrainedReader", "TFDPRQuestionEncoder", "TFDPRReader"]
if TYPE_CHECKING:
    from .configuration_dpr import DPRConfig
    from .tokenization_dpr import (DPRContextEncoderTokenizer, DPRQuestionEncoderTokenizer, DPRReaderOutput, DPRReaderTokenizer)
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_dpr_fast import (DPRContextEncoderTokenizerFast, DPRQuestionEncoderTokenizerFast, DPRReaderTokenizerFast)
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_dpr import (DPRContextEncoder, DPRPretrainedContextEncoder, DPRPreTrainedModel, DPRPretrainedQuestionEncoder, DPRPretrainedReader, DPRQuestionEncoder, DPRReader)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_dpr import (TFDPRContextEncoder, TFDPRPretrainedContextEncoder, TFDPRPretrainedQuestionEncoder, TFDPRPretrainedReader, TFDPRQuestionEncoder, TFDPRReader)
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
