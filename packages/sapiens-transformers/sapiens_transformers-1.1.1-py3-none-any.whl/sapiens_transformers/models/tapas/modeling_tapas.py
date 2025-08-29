"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import enum
import math
import os
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ...activations import ACT2FN
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPooling, MaskedLMOutput, SequenceClassifierOutput
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import (apply_chunking_to_forward, find_pruneable_heads_and_indices, is_torch_greater_or_equal_than_1_12, prune_linear_layer)
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_tapas import TapasConfig
logger = logging.get_logger(__name__)
if not is_torch_greater_or_equal_than_1_12: logger.warning(f"You are using torch=={torch.__version__}, but torch>=1.12.0 is required to use TapasModel. Please upgrade torch.")
_CONFIG_FOR_DOC = "TapasConfig"
_CHECKPOINT_FOR_DOC = "google/tapas-base"
EPSILON_ZERO_DIVISION = 1e-10
CLOSE_ENOUGH_TO_LOG_ZERO = -10000.0
@dataclass
class TableQuestionAnsweringOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    logits_aggregation: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
def load_tf_weights_in_tapas(model, config, tf_checkpoint_path):
    try:
        import re
        import numpy as np
        import tensorflow as tf
    except ImportError:
        logger.error("Loading a TensorFlow model in PyTorch, requires TensorFlow to be installed. Please see https://www.tensorflow.org/install/ for installation instructions.")
        raise
    tf_path = os.path.abspath(tf_checkpoint_path)
    logger.info(f"Converting TensorFlow checkpoint from {tf_path}")
    init_vars = tf.train.list_variables(tf_path)
    names = []
    arrays = []
    for name, shape in init_vars:
        logger.info(f"Loading TF weight {name} with shape {shape}")
        array = tf.train.load_variable(tf_path, name)
        names.append(name)
        arrays.append(array)
    for name, array in zip(names, arrays):
        name = name.split("/")
        if any(n in ["adam_v", "adam_m", "AdamWeightDecayOptimizer", "AdamWeightDecayOptimizer_1", "global_step", "seq_relationship"] for n in name):
            logger.info(f"Skipping {'/'.join(name)}")
            continue
        if isinstance(model, TapasForSequenceClassification):
            if any(n in ["output_bias", "output_weights"] for n in name):
                logger.info(f"Skipping {'/'.join(name)}")
                continue
        if isinstance(model, TapasModel):
            if any(n in ["output_bias", "output_weights", "output_bias_cls", "output_weights_cls"] for n in name):
                logger.info(f"Skipping {'/'.join(name)}")
                continue
        if isinstance(model, TapasForMaskedLM):
            if any(n in ["pooler"] for n in name):
                logger.info(f"Skipping {'/'.join(name)}")
                continue
        if name[0] == "bert": name[0] = "tapas"
        pointer = model
        for m_name in name:
            if re.fullmatch(r"[A-Za-z]+_\d+", m_name): scope_names = re.split(r"_(\d+)", m_name)
            else: scope_names = [m_name]
            if scope_names[0] == "kernel" or scope_names[0] == "gamma": pointer = getattr(pointer, "weight")
            elif scope_names[0] == "beta": pointer = getattr(pointer, "bias")
            elif scope_names[0] == "output_bias":
                if not isinstance(model, TapasForMaskedLM): pointer = getattr(pointer, "output_bias")
                else: pointer = getattr(pointer, "bias")
            elif scope_names[0] == "output_weights": pointer = getattr(pointer, "output_weights")
            elif scope_names[0] == "column_output_bias": pointer = getattr(pointer, "column_output_bias")
            elif scope_names[0] == "column_output_weights": pointer = getattr(pointer, "column_output_weights")
            elif scope_names[0] == "output_bias_agg":
                pointer = getattr(pointer, "aggregation_classifier")
                pointer = getattr(pointer, "bias")
            elif scope_names[0] == "output_weights_agg":
                pointer = getattr(pointer, "aggregation_classifier")
                pointer = getattr(pointer, "weight")
            elif scope_names[0] == "output_bias_cls":
                pointer = getattr(pointer, "classifier")
                pointer = getattr(pointer, "bias")
            elif scope_names[0] == "output_weights_cls":
                pointer = getattr(pointer, "classifier")
                pointer = getattr(pointer, "weight")
            else:
                try: pointer = getattr(pointer, scope_names[0])
                except AttributeError:
                    logger.info(f"Skipping {'/'.join(name)}")
                    continue
            if len(scope_names) >= 2:
                num = int(scope_names[1])
                pointer = pointer[num]
        if m_name[-11:] == "_embeddings": pointer = getattr(pointer, "weight")
        elif m_name[-13:] in [f"_embeddings_{i}" for i in range(7)]: pointer = getattr(pointer, "weight")
        elif m_name == "kernel": array = np.transpose(array)
        try:
            if pointer.shape != array.shape: raise ValueError(f"Pointer shape {pointer.shape} and array shape {array.shape} mismatched")
        except AssertionError as e:
            e.args += (pointer.shape, array.shape)
            raise
        logger.info(f"Initialize PyTorch weight {name}")
        if np.isscalar(array): array = np.array(array)
        pointer.data = torch.from_numpy(array)
    return model
class TapasEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        for i, type_vocab_sizes in enumerate(config.type_vocab_sizes):
            name = f"token_type_embeddings_{i}"
            setattr(self, name, nn.Embedding(type_vocab_sizes, config.hidden_size))
        self.number_of_token_type_embeddings = len(config.type_vocab_sizes)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.config = config
    def forward(self, input_ids=None, token_type_ids=None, position_ids=None, inputs_embeds=None):
        if input_ids is not None: input_shape = input_ids.size()
        else: input_shape = inputs_embeds.size()[:-1]
        seq_length = input_shape[1]
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if position_ids is None:
            position_ids = torch.arange(seq_length, dtype=torch.long, device=device)
            position_ids = position_ids.unsqueeze(0).expand(input_shape)
            if self.config.reset_position_index_per_cell:
                col_index = IndexMap(token_type_ids[:, :, 1], self.config.type_vocab_sizes[1], batch_dims=1)
                row_index = IndexMap(token_type_ids[:, :, 2], self.config.type_vocab_sizes[2], batch_dims=1)
                full_index = ProductIndexMap(col_index, row_index)
                first_position_per_segment = reduce_min(position_ids, full_index)[0]
                first_position = gather(first_position_per_segment, full_index)
                position = torch.arange(seq_length, dtype=torch.long, device=device).unsqueeze(0)
                position_ids = torch.min(torch.as_tensor(self.config.max_position_embeddings - 1, device=device), position - first_position)
        if token_type_ids is None: token_type_ids = torch.zeros((input_shape + self.number_of_token_type_embeddings), dtype=torch.long, device=device)
        if inputs_embeds is None: inputs_embeds = self.word_embeddings(input_ids)
        position_embeddings = self.position_embeddings(position_ids)
        embeddings = inputs_embeds + position_embeddings
        for i in range(self.number_of_token_type_embeddings):
            name = f"token_type_embeddings_{i}"
            embeddings += getattr(self, name)(token_type_ids[:, :, i])
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
class TapasSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size {config.hidden_size} is not a multiple of the number of attention heads {config.num_attention_heads}")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)
        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)
        self.is_decoder = config.is_decoder
    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    def forward(self, hidden_states, attention_mask=None, head_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, past_key_value=None, output_attentions=False):
        mixed_query_layer = self.query(hidden_states)
        is_cross_attention = encoder_hidden_states is not None
        if is_cross_attention and past_key_value is not None:
            key_layer = past_key_value[0]
            value_layer = past_key_value[1]
            attention_mask = encoder_attention_mask
        elif is_cross_attention:
            key_layer = self.transpose_for_scores(self.key(encoder_hidden_states))
            value_layer = self.transpose_for_scores(self.value(encoder_hidden_states))
            attention_mask = encoder_attention_mask
        elif past_key_value is not None:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))
            key_layer = torch.cat([past_key_value[0], key_layer], dim=2)
            value_layer = torch.cat([past_key_value[1], value_layer], dim=2)
        else:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)
        if self.is_decoder: past_key_value = (key_layer, value_layer)
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        if self.is_decoder: outputs = outputs + (past_key_value,)
        return outputs
class TapasSelfOutput(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states
class TapasAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.self = TapasSelfAttention(config)
        self.output = TapasSelfOutput(config)
        self.pruned_heads = set()
    def prune_heads(self, heads):
        if len(heads) == 0: return
        heads, index = find_pruneable_heads_and_indices(heads, self.self.num_attention_heads, self.self.attention_head_size, self.pruned_heads)
        self.self.query = prune_linear_layer(self.self.query, index)
        self.self.key = prune_linear_layer(self.self.key, index)
        self.self.value = prune_linear_layer(self.self.value, index)
        self.output.dense = prune_linear_layer(self.output.dense, index, dim=1)
        self.self.num_attention_heads = self.self.num_attention_heads - len(heads)
        self.self.all_head_size = self.self.attention_head_size * self.self.num_attention_heads
        self.pruned_heads = self.pruned_heads.union(heads)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.FloatTensor] = None, head_mask: Optional[torch.FloatTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.FloatTensor] = None, past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor]:
        self_outputs = self.self(hidden_states, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, past_key_value, output_attentions)
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
class TapasIntermediate(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class TapasOutput(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states
class TapasLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.attention = TapasAttention(config)
        self.is_decoder = config.is_decoder
        self.add_cross_attention = config.add_cross_attention
        if self.add_cross_attention:
            if not self.is_decoder: raise ValueError(f"{self} should be used as a decoder model if cross attention is added")
            self.crossattention = TapasAttention(config)
        self.intermediate = TapasIntermediate(config)
        self.output = TapasOutput(config)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.FloatTensor] = None, head_mask: Optional[torch.FloatTensor] = None,
    encoder_hidden_states: Optional[torch.FloatTensor] = None, encoder_attention_mask: Optional[torch.FloatTensor] = None, past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor]:
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        self_attention_outputs = self.attention(hidden_states, attention_mask, head_mask, output_attentions=output_attentions, past_key_value=self_attn_past_key_value)
        attention_output = self_attention_outputs[0]
        if self.is_decoder:
            outputs = self_attention_outputs[1:-1]
            present_key_value = self_attention_outputs[-1]
        else: outputs = self_attention_outputs[1:]
        cross_attn_present_key_value = None
        if self.is_decoder and encoder_hidden_states is not None:
            if not hasattr(self, "crossattention"): raise ValueError(f"If `encoder_hidden_states` are passed, {self} has to be instantiated with cross-attention layers by setting `config.add_cross_attention=True`")
            cross_attn_past_key_value = past_key_value[-2:] if past_key_value is not None else None
            cross_attention_outputs = self.crossattention(attention_output, attention_mask, head_mask, encoder_hidden_states, encoder_attention_mask, cross_attn_past_key_value, output_attentions)
            attention_output = cross_attention_outputs[0]
            outputs = outputs + cross_attention_outputs[1:-1]
            cross_attn_present_key_value = cross_attention_outputs[-1]
            present_key_value = present_key_value + cross_attn_present_key_value
        layer_output = apply_chunking_to_forward(self.feed_forward_chunk, self.chunk_size_feed_forward, self.seq_len_dim, attention_output)
        outputs = (layer_output,) + outputs
        if self.is_decoder: outputs = outputs + (present_key_value,)
        return outputs
    def feed_forward_chunk(self, attention_output):
        intermediate_output = self.intermediate(attention_output)
        layer_output = self.output(intermediate_output, attention_output)
        return layer_output
class TapasEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([TapasLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states, attention_mask=None, head_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, past_key_values=None, use_cache=None,
    output_attentions=False, output_hidden_states=False, return_dict=True):
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_head_mask = head_mask[i] if head_mask is not None else None
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states, attention_mask,
            layer_head_mask, encoder_hidden_states, encoder_attention_mask, past_key_values, output_attentions)
            else: layer_outputs = layer_module(hidden_states, attention_mask, layer_head_mask, encoder_hidden_states, encoder_attention_mask, past_key_values, output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_attentions)
class TapasPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output
class TapasPredictionHeadTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        if isinstance(config.hidden_act, str): self.transform_act_fn = ACT2FN[config.hidden_act]
        else: self.transform_act_fn = config.hidden_act
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        return hidden_states
class TapasLMPredictionHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.transform = TapasPredictionHeadTransform(config)
        self.decoder = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.bias = nn.Parameter(torch.zeros(config.vocab_size))
        self.decoder.bias = self.bias
    def _tie_weights(self): self.decoder.bias = self.bias
    def forward(self, hidden_states):
        hidden_states = self.transform(hidden_states)
        hidden_states = self.decoder(hidden_states)
        return hidden_states
class TapasOnlyMLMHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.predictions = TapasLMPredictionHead(config)
    def forward(self, sequence_output: torch.Tensor) -> torch.Tensor:
        prediction_scores = self.predictions(sequence_output)
        return prediction_scores
class TapasPreTrainedModel(PreTrainedModel):
    config_class = TapasConfig
    base_model_prefix = "tapas"
    supports_gradient_checkpointing = True
    _supports_param_buffer_assignment = False
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
TAPAS_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its models (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`TapasConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
TAPAS_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary. Indices can be obtained using [`AutoTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.FloatTensor` of shape `(0)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`torch.LongTensor` of shape `(0, 7)`, *optional*):
            Token indices that encode tabular structure. Indices can be obtained using [`AutoTokenizer`]. See this
            class for more info.
            [What are token type IDs?](../glossary#token-type-ids)
        position_ids (`torch.LongTensor` of shape `(0)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. If
            `reset_position_index_per_cell` of [`TapasConfig`] is set to `True`, relative position embeddings will be
            used. Selected in the range `[0, config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`: - 1
            indicates the head is *not masked*, - 0 indicates the head is *masked*.
        inputs_embeds (`torch.FloatTensor` of shape `(0, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare Tapas Model transformer outputting raw hidden-states without any specific head on top.", TAPAS_START_DOCSTRING)
class TapasModel(TapasPreTrainedModel):
    def __init__(self, config, add_pooling_layer=True):
        super().__init__(config)
        self.config = config
        self.embeddings = TapasEmbeddings(config)
        self.encoder = TapasEncoder(config)
        self.pooler = TapasPooler(config) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.word_embeddings
    def set_input_embeddings(self, value): self.embeddings.word_embeddings = value
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(TAPAS_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    position_ids: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    encoder_hidden_states: Optional[torch.FloatTensor] = None, encoder_attention_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            self.warn_if_padding_and_no_attention_mask(input_ids, attention_mask)
            input_shape = input_ids.size()
        elif inputs_embeds is not None: input_shape = inputs_embeds.size()[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if attention_mask is None: attention_mask = torch.ones(input_shape, device=device)
        if token_type_ids is None: token_type_ids = torch.zeros((*input_shape, len(self.config.type_vocab_sizes)), dtype=torch.long, device=device)
        extended_attention_mask: torch.Tensor = self.get_extended_attention_mask(attention_mask, input_shape)
        if self.config.is_decoder and encoder_hidden_states is not None:
            encoder_batch_size, encoder_sequence_length, _ = encoder_hidden_states.size()
            encoder_hidden_shape = (encoder_batch_size, encoder_sequence_length)
            if encoder_attention_mask is None: encoder_attention_mask = torch.ones(encoder_hidden_shape, device=device)
            encoder_extended_attention_mask = self.invert_attention_mask(encoder_attention_mask)
        else: encoder_extended_attention_mask = None
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        embedding_output = self.embeddings(input_ids=input_ids, position_ids=position_ids, token_type_ids=token_type_ids, inputs_embeds=inputs_embeds)
        encoder_outputs = self.encoder(embedding_output, attention_mask=extended_attention_mask, head_mask=head_mask, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=encoder_extended_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None
        if not return_dict: return (sequence_output, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
@add_start_docstrings("Tapas Model with a `language modeling` head on top.", TAPAS_START_DOCSTRING)
class TapasForMaskedLM(TapasPreTrainedModel):
    _tied_weights_keys = ["cls.predictions.decoder.weight", "cls.predictions.decoder.bias"]
    config_class = TapasConfig
    base_model_prefix = "tapas"
    def __init__(self, config):
        super().__init__(config)
        self.tapas = TapasModel(config, add_pooling_layer=False)
        self.cls = TapasOnlyMLMHead(config)
        self.post_init()
    def get_output_embeddings(self): return self.cls.predictions.decoder
    def set_output_embeddings(self, new_embeddings):
        self.cls.predictions.decoder = new_embeddings
        self.cls.predictions.bias = new_embeddings.bias
    @add_start_docstrings_to_model_forward(TAPAS_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    position_ids: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, **kwargs) -> Union[Tuple, MaskedLMOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.tapas(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds,
        encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        prediction_scores = self.cls(sequence_output)
        masked_lm_loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            masked_lm_loss = loss_fct(prediction_scores.view(-1, self.config.vocab_size), labels.view(-1))
        if not return_dict:
            output = (prediction_scores,) + outputs[2:]
            return ((masked_lm_loss,) + output) if masked_lm_loss is not None else output
        return MaskedLMOutput(loss=masked_lm_loss, logits=prediction_scores, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Tapas Model with a cell selection head and optional aggregation head on top for question-answering tasks on tables (linear layers on top of the hidden-states output to compute `logits` and optional `logits_aggregation`), e.g. for SQA, WTQ or WikiSQL-supervised tasks.", TAPAS_START_DOCSTRING)
class TapasForQuestionAnswering(TapasPreTrainedModel):
    def __init__(self, config: TapasConfig):
        super().__init__(config)
        self.tapas = TapasModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        if config.init_cell_selection_weights_to_zero:
            self.output_weights = nn.Parameter(torch.zeros(config.hidden_size))
            self.column_output_weights = nn.Parameter(torch.zeros(config.hidden_size))
        else:
            self.output_weights = nn.Parameter(torch.empty(config.hidden_size))
            nn.init.normal_(self.output_weights, std=config.initializer_range)
            self.column_output_weights = nn.Parameter(torch.empty(config.hidden_size))
            nn.init.normal_(self.column_output_weights, std=config.initializer_range)
        self.output_bias = nn.Parameter(torch.zeros([]))
        self.column_output_bias = nn.Parameter(torch.zeros([]))
        if config.num_aggregation_labels > 0: self.aggregation_classifier = nn.Linear(config.hidden_size, config.num_aggregation_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(TAPAS_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    position_ids: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None, table_mask: Optional[torch.LongTensor] = None,
    labels: Optional[torch.LongTensor] = None, aggregation_labels: Optional[torch.LongTensor] = None, float_answer: Optional[torch.FloatTensor] = None,
    numeric_values: Optional[torch.FloatTensor] = None, numeric_values_scale: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, TableQuestionAnsweringOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.tapas(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        pooled_output = outputs[1]
        sequence_output = self.dropout(sequence_output)
        if input_ids is not None: input_shape = input_ids.size()
        else: input_shape = inputs_embeds.size()[:-1]
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if token_type_ids is None: token_type_ids = torch.zeros((*input_shape, len(self.config.type_vocab_sizes)), dtype=torch.long, device=device)
        token_types = ["segment_ids", "column_ids", "row_ids", "prev_labels", "column_ranks", "inv_column_ranks", "numeric_relations"]
        row_ids = token_type_ids[:, :, token_types.index("row_ids")]
        column_ids = token_type_ids[:, :, token_types.index("column_ids")]
        row_index = IndexMap(indices=torch.min(row_ids, torch.as_tensor(self.config.max_num_rows - 1, device=row_ids.device)), num_segments=self.config.max_num_rows, batch_dims=1)
        col_index = IndexMap(indices=torch.min(column_ids, torch.as_tensor(self.config.max_num_columns - 1, device=column_ids.device)), num_segments=self.config.max_num_columns, batch_dims=1)
        cell_index = ProductIndexMap(row_index, col_index)
        input_shape = input_ids.size() if input_ids is not None else inputs_embeds.size()[:-1]
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if attention_mask is None: attention_mask = torch.ones(input_shape, device=device)
        if table_mask is None: table_mask = torch.where(row_ids > 0, torch.ones_like(row_ids), torch.zeros_like(row_ids))
        input_mask_float = attention_mask.float().to(device)
        table_mask_float = table_mask.float().to(device)
        cell_mask, _ = reduce_mean(input_mask_float, cell_index)
        logits = compute_token_logits(sequence_output, self.config.temperature, self.output_weights, self.output_bias)
        column_logits = None
        if self.config.select_one_column: column_logits = compute_column_logits(sequence_output, self.column_output_weights, self.column_output_bias, cell_index,
        cell_mask, self.config.allow_empty_column_selection)
        logits_aggregation = None
        if self.config.num_aggregation_labels > 0: logits_aggregation = self.aggregation_classifier(pooled_output)
        total_loss = 0.0
        calculate_loss = False
        if labels is not None:
            calculate_loss = True
            is_supervised = not self.config.num_aggregation_labels > 0 or not self.config.use_answer_as_supervision
            if is_supervised: aggregate_mask = None
            else:
                if float_answer is not None:
                    assert (labels.shape[0] == float_answer.shape[0]), "Make sure the answers are a FloatTensor of shape (batch_size,)"
                    aggregate_mask = _calculate_aggregate_mask(float_answer, pooled_output, self.config.cell_selection_preference, labels, self.aggregation_classifier)
                else: raise ValueError("You have to specify float answers in order to calculate the aggregate mask")
            if self.config.average_logits_per_cell:
                logits_per_cell, _ = reduce_mean(logits, cell_index)
                logits = gather(logits_per_cell, cell_index)
            dist_per_token = torch.distributions.Bernoulli(logits=logits)
            selection_loss_per_example = None
            if not self.config.select_one_column:
                weight = torch.where(labels == 0, torch.ones_like(labels, dtype=torch.float32), self.config.positive_label_weight * torch.ones_like(labels, dtype=torch.float32))
                selection_loss_per_token = -dist_per_token.log_prob(labels) * weight
                selection_loss_per_example = torch.sum(selection_loss_per_token * input_mask_float, dim=1) / (torch.sum(input_mask_float, dim=1) + EPSILON_ZERO_DIVISION)
            else:
                selection_loss_per_example, logits = _single_column_cell_selection_loss(logits, column_logits, labels, cell_index, col_index, cell_mask)
                dist_per_token = torch.distributions.Bernoulli(logits=logits)
            if self.config.disable_per_token_loss: pass
            elif is_supervised: total_loss += torch.mean(selection_loss_per_example)
            else: total_loss += torch.mean(selection_loss_per_example * (1.0 - aggregate_mask))
            if self.config.num_aggregation_labels > 0:
                if is_supervised:
                    if aggregation_labels is not None:
                        assert (labels.shape[0] == aggregation_labels.shape[0]), "Make sure the aggregation labels are a LongTensor of shape (batch_size,)"
                        per_example_additional_loss = _calculate_aggregation_loss(logits_aggregation, aggregate_mask, aggregation_labels, self.config.use_answer_as_supervision,
                        self.config.num_aggregation_labels, self.config.aggregation_loss_weight)
                    else: raise ValueError("You have to specify aggregation labels in order to calculate the aggregation loss")
                else:
                    aggregation_labels = torch.zeros(labels.shape[0], dtype=torch.long, device=labels.device)
                    per_example_additional_loss = _calculate_aggregation_loss(logits_aggregation, aggregate_mask, aggregation_labels, self.config.use_answer_as_supervision,
                    self.config.num_aggregation_labels, self.config.aggregation_loss_weight)
                if self.config.use_answer_as_supervision:
                    if numeric_values is not None and numeric_values_scale is not None:
                        assert numeric_values.shape == numeric_values_scale.shape
                        answer_loss, large_answer_loss_mask = _calculate_regression_loss(float_answer, aggregate_mask, dist_per_token, numeric_values, numeric_values_scale,
                        table_mask_float, logits_aggregation, self.config)
                        per_example_additional_loss += answer_loss
                        per_example_additional_loss *= large_answer_loss_mask
                    else: raise ValueError("You have to specify numeric values and numeric values scale in order to calculate the regression loss")
                total_loss += torch.mean(per_example_additional_loss)
        else:
            labels = torch.zeros_like(logits)
            _, logits = _single_column_cell_selection_loss(logits, column_logits, labels, cell_index, col_index, cell_mask)
        if not return_dict:
            output = (logits, logits_aggregation) + outputs[2:]
            return ((total_loss,) + output) if calculate_loss else output
        return TableQuestionAnsweringOutput(loss=total_loss if calculate_loss else None, logits=logits, logits_aggregation=logits_aggregation, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Tapas Model with a sequence classification head on top (a linear layer on top of the pooled output), e.g. for table entailment tasks, such as TabFact (Chen et al., 2020).", TAPAS_START_DOCSTRING)
class TapasForSequenceClassification(TapasPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.tapas = TapasModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(TAPAS_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    position_ids: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], SequenceClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.tapas(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
class AverageApproximationFunction(str, enum.Enum):
    RATIO = "ratio"
    FIRST_ORDER = "first_order"
    SECOND_ORDER = "second_order"
class IndexMap:
    def __init__(self, indices, num_segments, batch_dims=0):
        self.indices = torch.as_tensor(indices)
        self.num_segments = torch.as_tensor(num_segments, device=indices.device)
        self.batch_dims = batch_dims
    def batch_shape(self): return self.indices.size()[: self.batch_dims]
class ProductIndexMap(IndexMap):
    def __init__(self, outer_index, inner_index):
        if outer_index.batch_dims != inner_index.batch_dims: raise ValueError("outer_index.batch_dims and inner_index.batch_dims must be the same.")
        super().__init__(indices=(inner_index.indices + outer_index.indices * inner_index.num_segments), num_segments=inner_index.num_segments * outer_index.num_segments, batch_dims=inner_index.batch_dims)
        self.outer_index = outer_index
        self.inner_index = inner_index
    def project_outer(self, index):
        indices = torch.div(index.indices, self.inner_index.num_segments, rounding_mode="floor").type(torch.long)
        return IndexMap(indices=indices, num_segments=self.outer_index.num_segments, batch_dims=index.batch_dims)
    def project_inner(self, index): return IndexMap(indices=torch.fmod(index.indices, self.inner_index.num_segments).type(torch.float).floor().type(torch.long), num_segments=self.inner_index.num_segments, batch_dims=index.batch_dims)
def gather(values, index, name="segmented_gather"):
    indices = index.indices
    if len(values.shape[index.batch_dims :]) < 2: return torch.gather(values, index.batch_dims, indices.view(values.size()[0], -1)).view(indices.size())
    else:
        indices = indices.unsqueeze(-1).expand(values.shape)
        return torch.gather(values, index.batch_dims, indices)
def flatten(index, name="segmented_flatten"):
    batch_size = torch.prod(torch.tensor(list(index.batch_shape())))
    offset = torch.arange(start=0, end=batch_size, device=index.num_segments.device) * index.num_segments
    offset = offset.view(index.batch_shape())
    for _ in range(index.batch_dims, len(index.indices.size())): offset = offset.unsqueeze(-1)
    indices = offset + index.indices
    return IndexMap(indices=indices.view(-1), num_segments=index.num_segments * batch_size, batch_dims=0)
def range_index_map(batch_shape, num_segments, name="range_index_map"):
    batch_shape = torch.as_tensor(batch_shape, dtype=torch.long)
    assert len(batch_shape.size()) == 1
    num_segments = torch.as_tensor(num_segments)
    assert len(num_segments.size()) == 0
    indices = torch.arange(start=0, end=num_segments, device=num_segments.device)
    new_tensor = torch.cat([torch.ones_like(batch_shape, dtype=torch.long, device=num_segments.device), num_segments.unsqueeze(dim=0)], dim=0)
    new_shape = [int(x) for x in new_tensor.tolist()]
    indices = indices.view(new_shape)
    multiples = torch.cat([batch_shape, torch.as_tensor([1])], dim=0)
    indices = indices.repeat(multiples.tolist())
    return IndexMap(indices=indices, num_segments=num_segments, batch_dims=list(batch_shape.size())[0])
def _segment_reduce(values, index, segment_reduce_fn, name):
    flat_index = flatten(index)
    vector_shape = values.size()[len(index.indices.size()) :]
    flattened_shape = torch.cat([torch.as_tensor([-1], dtype=torch.long), torch.as_tensor(vector_shape, dtype=torch.long)], dim=0)
    flat_values = values.reshape(flattened_shape.tolist())
    out = torch.zeros(int(flat_index.num_segments), dtype=torch.float, device=flat_values.device)
    segment_means = out.scatter_reduce(dim=0, index=flat_index.indices.long(), src=flat_values.float(), reduce=segment_reduce_fn, include_self=False)
    new_shape = torch.cat([torch.as_tensor(index.batch_shape(), dtype=torch.long), torch.as_tensor([index.num_segments], dtype=torch.long), torch.as_tensor(vector_shape, dtype=torch.long)], dim=0)
    output_values = segment_means.clone().view(new_shape.tolist()).to(values.dtype)
    output_index = range_index_map(index.batch_shape(), index.num_segments)
    return output_values, output_index
def reduce_sum(values, index, name="segmented_reduce_sum"): return _segment_reduce(values, index, "sum", name)
def reduce_mean(values, index, name="segmented_reduce_mean"): return _segment_reduce(values, index, "mean", name)
def reduce_max(values, index, name="segmented_reduce_max"): return _segment_reduce(values, index, "amax", name)
def reduce_min(values, index, name="segmented_reduce_min"): return _segment_reduce(values, index, "amin", name)
def compute_column_logits(sequence_output, column_output_weights, column_output_bias, cell_index, cell_mask, allow_empty_column_selection):
    token_logits = torch.einsum("bsj,j->bs", sequence_output, column_output_weights) + column_output_bias
    cell_logits, cell_logits_index = reduce_mean(token_logits, cell_index)
    column_index = cell_index.project_inner(cell_logits_index)
    column_logits, out_index = reduce_sum(cell_logits * cell_mask, column_index)
    cell_count, _ = reduce_sum(cell_mask, column_index)
    column_logits /= cell_count + EPSILON_ZERO_DIVISION
    is_padding = torch.logical_and(cell_count < 0.5, ~torch.eq(out_index.indices, 0))
    column_logits += CLOSE_ENOUGH_TO_LOG_ZERO * torch.as_tensor(is_padding, dtype=torch.float32, device=is_padding.device)
    if not allow_empty_column_selection: column_logits += CLOSE_ENOUGH_TO_LOG_ZERO * torch.as_tensor(torch.eq(out_index.indices, 0), dtype=torch.float32, device=out_index.indices.device)
    return column_logits
def _single_column_cell_selection_loss(token_logits, column_logits, labels, cell_index, col_index, cell_mask):
    labels_per_column, _ = reduce_sum(torch.as_tensor(labels, dtype=torch.float32, device=labels.device), col_index)
    column_label = torch.argmax(labels_per_column, dim=-1)
    no_cell_selected = torch.eq(torch.max(labels_per_column, dim=-1)[0], 0)
    column_label = torch.where(no_cell_selected.view(column_label.size()), torch.zeros_like(column_label), column_label)
    column_dist = torch.distributions.Categorical(logits=column_logits)
    column_loss_per_example = -column_dist.log_prob(column_label)
    logits_per_cell, _ = reduce_mean(token_logits, cell_index)
    labels_per_cell, labels_index = reduce_max(torch.as_tensor(labels, dtype=torch.long, device=labels.device), cell_index)
    column_id_for_cells = cell_index.project_inner(labels_index).indices
    column_mask = torch.as_tensor(torch.eq(column_id_for_cells, torch.unsqueeze(column_label, dim=-1)), dtype=torch.float32, device=cell_mask.device)
    cell_dist = torch.distributions.Bernoulli(logits=logits_per_cell)
    cell_log_prob = cell_dist.log_prob(labels_per_cell.type(torch.float32))
    cell_loss = -torch.sum(cell_log_prob * column_mask * cell_mask, dim=1)
    cell_loss /= torch.sum(column_mask * cell_mask, dim=1) + EPSILON_ZERO_DIVISION
    selection_loss_per_example = column_loss_per_example
    selection_loss_per_example += torch.where(no_cell_selected.view(selection_loss_per_example.size()), torch.zeros_like(selection_loss_per_example), cell_loss)
    selected_column_id = torch.as_tensor(torch.argmax(column_logits, dim=-1), dtype=torch.long, device=column_logits.device)
    selected_column_mask = torch.as_tensor(torch.eq(column_id_for_cells, torch.unsqueeze(selected_column_id, dim=-1)), dtype=torch.float32, device=selected_column_id.device)
    selected_column_mask = torch.where(torch.eq(column_id_for_cells, 0).view(selected_column_mask.size()), torch.zeros_like(selected_column_mask), selected_column_mask)
    new_logits_per_cell = logits_per_cell + CLOSE_ENOUGH_TO_LOG_ZERO * (1.0 - cell_mask * selected_column_mask)
    logits = gather(new_logits_per_cell, cell_index)
    return selection_loss_per_example, logits
def compute_token_logits(sequence_output, temperature, output_weights, output_bias):
    logits = (torch.einsum("bsj,j->bs", sequence_output, output_weights) + output_bias) / temperature
    return logits
def _calculate_aggregate_mask(answer, pooled_output, cell_selection_preference, labels, aggregation_classifier):
    aggregate_mask_init = torch.logical_not(torch.isnan(answer)).type(torch.FloatTensor).to(answer.device)
    logits_aggregation = aggregation_classifier(pooled_output)
    dist_aggregation = torch.distributions.categorical.Categorical(logits=logits_aggregation)
    aggregation_ops_total_mass = torch.sum(dist_aggregation.probs[:, 1:], dim=1)
    is_pred_cell_selection = aggregation_ops_total_mass <= cell_selection_preference
    is_cell_supervision_available = torch.sum(labels, dim=1) > 0
    aggregate_mask = torch.where(torch.logical_and(is_pred_cell_selection, is_cell_supervision_available).view(aggregate_mask_init.size()), torch.zeros_like(aggregate_mask_init, dtype=torch.float32), aggregate_mask_init)
    aggregate_mask = aggregate_mask.detach()
    return aggregate_mask
def _calculate_aggregation_loss_known(logits_aggregation, aggregate_mask, aggregation_labels, use_answer_as_supervision, num_aggregation_labels):
    if use_answer_as_supervision: target_aggregation = torch.zeros_like(aggregate_mask, dtype=torch.long)
    else: target_aggregation = aggregation_labels
    one_hot_labels = nn.functional.one_hot(target_aggregation, num_classes=num_aggregation_labels).type(torch.float32)
    log_probs = nn.functional.log_softmax(logits_aggregation, dim=-1)
    per_example_aggregation_intermediate = -torch.sum(one_hot_labels * log_probs, dim=-1)
    if use_answer_as_supervision: return per_example_aggregation_intermediate * (1 - aggregate_mask)
    else: return per_example_aggregation_intermediate
def _calculate_aggregation_loss_unknown(logits_aggregation, aggregate_mask):
    dist_aggregation = torch.distributions.categorical.Categorical(logits=logits_aggregation)
    aggregation_ops_total_mass = torch.sum(dist_aggregation.probs[:, 1:], dim=1)
    return -torch.log(aggregation_ops_total_mass) * aggregate_mask
def _calculate_aggregation_loss(logits_aggregation, aggregate_mask, aggregation_labels, use_answer_as_supervision, num_aggregation_labels, aggregation_loss_weight):
    per_example_aggregation_loss = _calculate_aggregation_loss_known(logits_aggregation, aggregate_mask, aggregation_labels, use_answer_as_supervision, num_aggregation_labels)
    if use_answer_as_supervision: per_example_aggregation_loss += _calculate_aggregation_loss_unknown(logits_aggregation, aggregate_mask)
    return aggregation_loss_weight * per_example_aggregation_loss
def _calculate_expected_result(dist_per_cell, numeric_values, numeric_values_scale, input_mask_float, logits_aggregation, config):
    if config.use_gumbel_for_cells:
        gumbel_dist = torch.distributions.RelaxedBernoulli(temperature=config.temperature, logits=dist_per_cell.logits * config.temperature)
        scaled_probability_per_cell = gumbel_dist.sample()
    else: scaled_probability_per_cell = dist_per_cell.probs
    scaled_probability_per_cell = (scaled_probability_per_cell / numeric_values_scale) * input_mask_float
    count_result = torch.sum(scaled_probability_per_cell, dim=1)
    numeric_values_masked = torch.where(torch.isnan(numeric_values), torch.zeros_like(numeric_values), numeric_values)
    sum_result = torch.sum(scaled_probability_per_cell * numeric_values_masked, dim=1)
    avg_approximation = config.average_approximation_function
    if avg_approximation == AverageApproximationFunction.RATIO: average_result = sum_result / (count_result + EPSILON_ZERO_DIVISION)
    elif avg_approximation == AverageApproximationFunction.FIRST_ORDER:
        ex = torch.sum(scaled_probability_per_cell, dim=1, keepdim=True) - scaled_probability_per_cell + 1
        average_result = torch.sum(numeric_values_masked * scaled_probability_per_cell / ex, dim=1)
    elif avg_approximation == AverageApproximationFunction.SECOND_ORDER:
        ex = torch.sum(scaled_probability_per_cell, dim=1, keepdim=True) - scaled_probability_per_cell + 1
        pointwise_var = scaled_probability_per_cell * (1 - scaled_probability_per_cell)
        var = torch.sum(pointwise_var, dim=1, keepdim=True) - pointwise_var
        multiplier = (var / torch.square(ex) + 1) / ex
        average_result = torch.sum(numeric_values_masked * scaled_probability_per_cell * multiplier, dim=1)
    else: raise ValueError(f"Invalid average_approximation_function: {config.average_approximation_function}")
    if config.use_gumbel_for_aggregation:
        gumbel_dist = torch.distributions.RelaxedOneHotCategorical(config.aggregation_temperature, logits=logits_aggregation[:, 1:])
        aggregation_op_only_probs = gumbel_dist.sample()
    else: aggregation_op_only_probs = nn.functional.softmax(logits_aggregation[:, 1:] / config.aggregation_temperature, dim=-1)
    all_results = torch.cat([torch.unsqueeze(sum_result, dim=1), torch.unsqueeze(average_result, dim=1), torch.unsqueeze(count_result, dim=1)], dim=1)
    expected_result = torch.sum(all_results * aggregation_op_only_probs, dim=1)
    return expected_result
def huber_loss(input, target, delta: float = 1.0):
    errors = torch.abs(input - target)
    return torch.where(errors < delta, 0.5 * errors**2, errors * delta - (0.5 * delta**2))
def _calculate_regression_loss(answer, aggregate_mask, dist_per_cell, numeric_values, numeric_values_scale, input_mask_float, logits_aggregation, config):
    expected_result = _calculate_expected_result(dist_per_cell, numeric_values, numeric_values_scale, input_mask_float, logits_aggregation, config)
    answer_masked = torch.where(torch.isnan(answer), torch.zeros_like(answer), answer)
    if config.use_normalized_answer_loss:
        normalizer = (torch.max(torch.abs(expected_result), torch.abs(answer_masked)) + EPSILON_ZERO_DIVISION).detach()
        normalized_answer_masked = answer_masked / normalizer
        normalized_expected_result = expected_result / normalizer
        per_example_answer_loss = huber_loss(normalized_expected_result * aggregate_mask, normalized_answer_masked * aggregate_mask)
    else: per_example_answer_loss = huber_loss(expected_result * aggregate_mask, answer_masked * aggregate_mask, delta=config.huber_loss_delta)
    if config.answer_loss_cutoff is None: large_answer_loss_mask = torch.ones_like(per_example_answer_loss, dtype=torch.float32)
    else: large_answer_loss_mask = torch.where(per_example_answer_loss > config.answer_loss_cutoff, torch.zeros_like(per_example_answer_loss, dtype=torch.float32), torch.ones_like(per_example_answer_loss, dtype=torch.float32))
    per_example_answer_loss_scaled = config.answer_loss_importance * (per_example_answer_loss * aggregate_mask)
    return per_example_answer_loss_scaled, large_answer_loss_mask
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
