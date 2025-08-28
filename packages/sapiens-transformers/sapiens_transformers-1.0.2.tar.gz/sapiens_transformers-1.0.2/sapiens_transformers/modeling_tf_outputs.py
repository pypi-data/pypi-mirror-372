from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .utils import ModelOutput
import tensorflow as tf
import warnings
@dataclass
class TFBaseModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithNoAttention(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    hidden_states: Optional[Tuple[tf.Tensor, ...]] = None
@dataclass
class TFBaseModelOutputWithPooling(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    pooler_output: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPoolingAndNoAttention(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    pooler_output: tf.Tensor = None
    hidden_states: Optional[Tuple[tf.Tensor, ...]] = None
@dataclass
class TFBaseModelOutputWithPoolingAndCrossAttentions(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    pooler_output: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPast(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithCrossAttentions(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPastAndCrossAttentions(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    decoder_hidden_states: Tuple[tf.Tensor] | None = None
    decoder_attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: Tuple[tf.Tensor] | None = None
    encoder_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutputWithCrossAttentions(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFMaskedLMOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqLMOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    decoder_hidden_states: Tuple[tf.Tensor] | None = None
    decoder_attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: Tuple[tf.Tensor] | None = None
    encoder_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFNextSentencePredictorOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSequenceClassifierOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqSequenceClassifierOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    decoder_hidden_states: Tuple[tf.Tensor] | None = None
    decoder_attentions: Tuple[tf.Tensor] | None = None
    cross_attentions: Tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: Tuple[tf.Tensor] | None = None
    encoder_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSemanticSegmenterOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSemanticSegmenterOutputWithNoAttention(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
@dataclass
class TFImageClassifierOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFMultipleChoiceModelOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFTokenClassifierOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFQuestionAnsweringModelOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    start_logits: tf.Tensor = None
    end_logits: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqQuestionAnsweringModelOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    start_logits: tf.Tensor = None
    end_logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    decoder_hidden_states: Tuple[tf.Tensor] | None = None
    decoder_attentions: Tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: Tuple[tf.Tensor] | None = None
    encoder_attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFSequenceClassifierOutputWithPast(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
@dataclass
class TFImageClassifierOutputWithNoAttention(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    hidden_states: Optional[Tuple[tf.Tensor, ...]] = None
@dataclass
class TFMaskedImageModelingOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    reconstruction: tf.Tensor = None
    hidden_states: Tuple[tf.Tensor] | None = None
    attentions: Tuple[tf.Tensor] | None = None
    @property
    def logits(self):
        warnings.warn("logits attribute is deprecated and will be removed in version 1 of Sapiens Transformers. Please use the reconstruction attribute to retrieve the final output instead.", FutureWarning)
        return self.reconstruction
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
