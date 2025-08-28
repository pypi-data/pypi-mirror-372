"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_keras_nlp_available, is_tensorflow_text_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_gpt2': ['GPT2Config', 'GPT2OnnxConfig'], 'tokenization_gpt2': ['GPT2Tokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_gpt2_fast"] = ["GPT2TokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_gpt2"] = ["GPT2DoubleHeadsModel", "GPT2ForQuestionAnswering", "GPT2ForSequenceClassification", "GPT2ForTokenClassification", "GPT2LMHeadModel", "GPT2Model", "GPT2PreTrainedModel", "load_tf_weights_in_gpt2"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_tf_gpt2"] = ["TFGPT2DoubleHeadsModel", "TFGPT2ForSequenceClassification", "TFGPT2LMHeadModel", "TFGPT2MainLayer", "TFGPT2Model", "TFGPT2PreTrainedModel"]
try:
    if not is_keras_nlp_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_gpt2_tf"] = ["TFGPT2Tokenizer"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["modeling_flax_gpt2"] = ["FlaxGPT2LMHeadModel", "FlaxGPT2Model", "FlaxGPT2PreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_gpt2 import GPT2Config, GPT2OnnxConfig
    from .tokenization_gpt2 import GPT2Tokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_gpt2_fast import GPT2TokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_gpt2 import (GPT2DoubleHeadsModel, GPT2ForQuestionAnswering, GPT2ForSequenceClassification, GPT2ForTokenClassification, GPT2LMHeadModel, GPT2Model, GPT2PreTrainedModel, load_tf_weights_in_gpt2)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_tf_gpt2 import (TFGPT2DoubleHeadsModel, TFGPT2ForSequenceClassification, TFGPT2LMHeadModel, TFGPT2MainLayer, TFGPT2Model, TFGPT2PreTrainedModel)
    try:
        if not is_keras_nlp_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_gpt2_tf import TFGPT2Tokenizer
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .modeling_flax_gpt2 import FlaxGPT2LMHeadModel, FlaxGPT2Model, FlaxGPT2PreTrainedModel
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
