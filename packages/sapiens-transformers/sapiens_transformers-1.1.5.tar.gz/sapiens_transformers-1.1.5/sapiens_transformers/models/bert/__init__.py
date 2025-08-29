"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import TYPE_CHECKING
from ...utils import (OptionalDependencyNotAvailable, _LazyModule, is_flax_available, is_tensorflow_text_available, is_tf_available, is_tokenizers_available, is_torch_available)
_import_structure = {'configuration_bert': ['BertConfig', 'BertOnnxConfig'], 'tokenization_bert': ['BasicTokenizer', 'BertTokenizer', 'WordpieceTokenizer']}
try:
    if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_bert_fast"] = ["BertTokenizerFast"]
try:
    if not is_torch_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_bert"] = ["BertForMaskedLM", "BertForMultipleChoice", "BertForNextSentencePrediction", "BertForPreTraining", "BertForQuestionAnswering",
    "BertForSequenceClassification", "BertForTokenClassification", "BertLayer", "BertLMHeadModel", "BertModel", "BertPreTrainedModel", "load_tf_weights_in_bert"]
try:
    if not is_tf_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_tf_bert"] = ["TFBertEmbeddings", "TFBertForMaskedLM", "TFBertForMultipleChoice", "TFBertForNextSentencePrediction", "TFBertForPreTraining",
    "TFBertForQuestionAnswering", "TFBertForSequenceClassification", "TFBertForTokenClassification", "TFBertLMHeadModel", "TFBertMainLayer", "TFBertModel", "TFBertPreTrainedModel"]
try:
    if not is_tensorflow_text_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else: _import_structure["tokenization_bert_tf"] = ["TFBertTokenizer"]
try:
    if not is_flax_available(): raise OptionalDependencyNotAvailable()
except OptionalDependencyNotAvailable: pass
else:
    _import_structure["modeling_flax_bert"] = ["FlaxBertForCausalLM", "FlaxBertForMaskedLM", "FlaxBertForMultipleChoice", "FlaxBertForNextSentencePrediction", "FlaxBertForPreTraining",
    "FlaxBertForQuestionAnswering", "FlaxBertForSequenceClassification", "FlaxBertForTokenClassification", "FlaxBertModel", "FlaxBertPreTrainedModel"]
if TYPE_CHECKING:
    from .configuration_bert import BertConfig, BertOnnxConfig
    from .tokenization_bert import BasicTokenizer, BertTokenizer, WordpieceTokenizer
    try:
        if not is_tokenizers_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_bert_fast import BertTokenizerFast
    try:
        if not is_torch_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_bert import (BertForMaskedLM, BertForMultipleChoice, BertForNextSentencePrediction, BertForPreTraining, BertForQuestionAnswering, BertForSequenceClassification,
        BertForTokenClassification, BertLayer, BertLMHeadModel, BertModel, BertPreTrainedModel, load_tf_weights_in_bert)
    try:
        if not is_tf_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_tf_bert import (TFBertEmbeddings, TFBertForMaskedLM, TFBertForMultipleChoice, TFBertForNextSentencePrediction, TFBertForPreTraining, TFBertForQuestionAnswering,
        TFBertForSequenceClassification, TFBertForTokenClassification, TFBertLMHeadModel, TFBertMainLayer, TFBertModel, TFBertPreTrainedModel)
    try:
        if not is_tensorflow_text_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else: from .tokenization_bert_tf import TFBertTokenizer
    try:
        if not is_flax_available(): raise OptionalDependencyNotAvailable()
    except OptionalDependencyNotAvailable: pass
    else:
        from .modeling_flax_bert import (FlaxBertForCausalLM, FlaxBertForMaskedLM, FlaxBertForMultipleChoice, FlaxBertForNextSentencePrediction, FlaxBertForPreTraining,
        FlaxBertForQuestionAnswering, FlaxBertForSequenceClassification, FlaxBertForTokenClassification, FlaxBertModel, FlaxBertPreTrainedModel)
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
