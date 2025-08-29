"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Dict, Optional, Tuple
from .utils import ModelOutput
import jax.numpy as jnp
import flax
@flax.struct.dataclass
class FlaxBaseModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithNoAttention(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPoolingAndNoAttention(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    pooler_output: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxImageClassifierOutputWithNoAttention(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPast(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    past_key_values: Optional[Dict[str, jnp.ndarray]] = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPooling(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    pooler_output: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPoolingAndCrossAttentions(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    pooler_output: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPastAndCrossAttentions(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxCausalLMOutputWithCrossAttentions(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxMaskedLMOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
FlaxCausalLMOutput = FlaxMaskedLMOutput
@flax.struct.dataclass
class FlaxSeq2SeqLMOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxNextSentencePredictorOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSequenceClassifierOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqSequenceClassifierOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxMultipleChoiceModelOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxTokenClassifierOutput(ModelOutput):
    """Args:"""
    logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxQuestionAnsweringModelOutput(ModelOutput):
    """Args:"""
    start_logits: jnp.ndarray = None
    end_logits: jnp.ndarray = None
    hidden_states: Optional[Tuple[jnp.ndarray]] = None
    attentions: Optional[Tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqQuestionAnsweringModelOutput(ModelOutput):
    """Args:"""
    start_logits: jnp.ndarray = None
    end_logits: jnp.ndarray = None
    past_key_values: Optional[Tuple[Tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[Tuple[jnp.ndarray]] = None
    cross_attentions: Optional[Tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[Tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[Tuple[jnp.ndarray]] = None
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
