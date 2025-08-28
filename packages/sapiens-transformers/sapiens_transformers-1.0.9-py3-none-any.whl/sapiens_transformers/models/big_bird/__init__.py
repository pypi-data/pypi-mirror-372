"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_sentencepiece_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_big_bird': ['BigBirdConfig', 'BigBirdOnnxConfig']}
try:
    if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_big_bird"] = ["BigBirdTokenizer"]
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_big_bird_fast"] = ["BigBirdTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_big_bird"] = ["BigBirdForCausalLM", "BigBirdForMaskedLM", "BigBirdForMultipleChoice", "BigBirdForPreTraining", "BigBirdForQuestionAnswering",
    "BigBirdForSequenceClassification", "BigBirdForTokenClassification", "BigBirdLayer", "BigBirdModel", "BigBirdPreTrainedModel", "load_tf_weights_in_big_bird"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_flax_big_bird"] = ["FlaxBigBirdForCausalLM", "FlaxBigBirdForMaskedLM", "FlaxBigBirdForMultipleChoice", "FlaxBigBirdForPreTraining",
    "FlaxBigBirdForQuestionAnswering", "FlaxBigBirdForSequenceClassification", "FlaxBigBirdForTokenClassification", "FlaxBigBirdModel", "FlaxBigBirdPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_big_bird import BigBirdConfig, BigBirdOnnxConfig
    try:
        if not is_sentencepiece_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_big_bird import BigBirdTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_big_bird_fast import BigBirdTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_big_bird import (BigBirdForCausalLM, BigBirdForMaskedLM, BigBirdForMultipleChoice, BigBirdForPreTraining, BigBirdForQuestionAnswering,
        BigBirdForSequenceClassification, BigBirdForTokenClassification, BigBirdLayer, BigBirdModel, BigBirdPreTrainedModel, load_tf_weights_in_big_bird)
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_flax_big_bird import (FlaxBigBirdForCausalLM, FlaxBigBirdForMaskedLM, FlaxBigBirdForMultipleChoice, FlaxBigBirdForPreTraining, FlaxBigBirdForQuestionAnswering,
        FlaxBigBirdForSequenceClassification, FlaxBigBirdForTokenClassification, FlaxBigBirdModel, FlaxBigBirdPreTrainedModel)
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
