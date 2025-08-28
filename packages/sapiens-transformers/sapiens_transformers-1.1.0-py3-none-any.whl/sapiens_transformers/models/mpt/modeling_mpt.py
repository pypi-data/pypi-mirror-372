"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, LayerNorm, MSELoss
from torch.nn import functional as F
from ...file_utils import add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward
from ...generation import GenerationMixin
from ...modeling_attn_mask_utils import _prepare_4d_causal_attention_mask
from ...modeling_outputs import (BaseModelOutputWithPastAndCrossAttentions, CausalLMOutputWithCrossAttentions, QuestionAnsweringModelOutput, SequenceClassifierOutputWithPast, TokenClassifierOutput)
from ...modeling_utils import PreTrainedModel
from ...utils import logging
from .configuration_mpt import MptConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "mosaicml/mpt-7b"
_CONFIG_FOR_DOC = "MptConfig"
def build_mpt_alibi_tensor(num_heads, sequence_length, alibi_bias_max=8, device=None):
    alibi = torch.arange(1 - sequence_length, 1, dtype=torch.int32, device=device).view(1, 1, 1, sequence_length)
    num_heads_power_of_2 = 2 ** math.ceil(math.log2(num_heads))
    base = torch.arange(1, num_heads_power_of_2 + 1, dtype=torch.int64, device=device).float()
    base = base * (alibi_bias_max / num_heads_power_of_2)
    slopes = 1.0 / torch.pow(2, base)
    slopes = slopes.view(1, num_heads_power_of_2, 1, 1)
    if num_heads_power_of_2 != num_heads: slopes = torch.concat([slopes[:, 1::2, ...], slopes[:, ::2, ...]], dim=1)[:, :num_heads, ...]
    alibi = alibi * slopes
    return alibi.squeeze(0)
class MptAttention(nn.Module):
    def __init__(self, config: MptConfig):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.n_heads = config.n_heads
        self.max_seq_length = config.max_seq_len
        self.head_dim = self.hidden_size // self.n_heads
        self.softmax_scale = config.attn_config.softmax_scale
        if self.softmax_scale is None: self.softmax_scale = 1 / math.sqrt(self.hidden_size / self.n_heads)
        self.attn_dropout_p = config.attn_config.attn_pdrop
        self.clip_qkv = config.attn_config.clip_qkv
        self.Wqkv = nn.Linear(self.hidden_size, 3 * self.hidden_size, bias=False)
        self.out_proj = nn.Linear(self.hidden_size, self.hidden_size, bias=False)
    def forward(self, hidden_states: torch.Tensor, position_bias: torch.Tensor, past_key_value: Optional[Tuple[torch.Tensor]] = None, attention_mask: Optional[torch.Tensor] = None):
        batch_size, seq_length = hidden_states.shape[:2]
        mixed_qkv = self.Wqkv(hidden_states)
        if self.clip_qkv: mixed_qkv = mixed_qkv.clamp(min=-self.clip_qkv, max=self.clip_qkv)
        query_states, key_states, value_states = mixed_qkv.chunk(3, dim=2)
        query_states = query_states.reshape(batch_size, seq_length, self.n_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.reshape(batch_size, seq_length, self.n_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.reshape(batch_size, seq_length, self.n_heads, self.head_dim).transpose(1, 2)
        if past_key_value is not None:
            if len(past_key_value) != 0:
                key_states = torch.cat([past_key_value[0], key_states], dim=2)
                value_states = torch.cat([past_key_value[1], value_states], dim=2)
            past_key_value = (key_states, value_states)
        else: past_key_value = (key_states, value_states)
        attention_scores = torch.matmul(query_states, key_states.transpose(-1, -2)) * self.softmax_scale
        query_length = seq_length if past_key_value is None else seq_length + past_key_value[0].shape[2]
        if position_bias is not None:
            if len(position_bias.shape) != 3: raise ValueError(f"Expecting position_bias shape to be 3 dimensions, got {len(position_bias.shape)}")
            key_length = key_states.shape[-2]
            position_bias_query_index = max(0, position_bias.size(1) - query_length)
            position_bias_key_index = max(0, position_bias.size(2) - key_length)
            position_bias = position_bias[:, position_bias_query_index:, position_bias_key_index:]
            attention_scores = attention_scores + position_bias
        if attention_mask is not None: attention_scores = attention_scores.masked_fill(attention_mask, torch.finfo(query_states.dtype).min)
        attn_weights = nn.functional.softmax(attention_scores.float(), dim=-1).to(value_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.attn_dropout_p, training=self.training)
        context_states = torch.matmul(attn_weights, value_states)
        context_states = context_states.permute(0, 2, 1, 3).contiguous().view(batch_size, seq_length, -1)
        attn_output = self.out_proj(context_states)
        return attn_output, attn_weights, past_key_value
class MptMLP(nn.Module):
    def __init__(self, config: MptConfig):
        super().__init__()
        hidden_size = config.hidden_size
        self.up_proj = nn.Linear(hidden_size, 4 * hidden_size, bias=False)
        self.act = nn.GELU(approximate="none")
        self.down_proj = nn.Linear(4 * hidden_size, hidden_size, bias=False)
        self.hidden_dropout = config.attn_config.attn_pdrop
    def forward(self, hidden_states: torch.Tensor, residual: torch.Tensor) -> torch.Tensor:
        hidden_states = self.act(self.up_proj(hidden_states))
        intermediate_output = self.down_proj(hidden_states)
        output = F.dropout(intermediate_output, p=self.hidden_dropout, training=self.training)
        output = output + residual
        return output
class MptBlock(nn.Module):
    def __init__(self, config: MptConfig):
        super().__init__()
        hidden_size = config.hidden_size
        self.norm_1 = LayerNorm(hidden_size, eps=config.layer_norm_epsilon)
        self.norm_1.bias = None
        self.num_heads = config.n_heads
        self.attn = MptAttention(config)
        self.norm_2 = LayerNorm(hidden_size, eps=config.layer_norm_epsilon)
        self.norm_2.bias = None
        self.ffn = MptMLP(config)
        self.dropout_rate = config.attn_config.attn_pdrop
        self.resid_attn_dropout = nn.Dropout(self.dropout_rate)
    def forward(self, hidden_states: torch.Tensor, position_bias: torch.Tensor, attention_mask: torch.Tensor, layer_past: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
    use_cache: bool = False, output_attentions: bool = False):
        layernorm_output = self.norm_1(hidden_states)
        residual = hidden_states
        attn_outputs, attn_weights, past_key_value = self.attn(layernorm_output, position_bias=position_bias, attention_mask=attention_mask, past_key_value=layer_past)
        hidden_states = self.resid_attn_dropout(attn_outputs) + residual
        layernorm_output = self.norm_2(hidden_states)
        residual = hidden_states
        output = self.ffn(layernorm_output, residual)
        outputs = (output,)
        if use_cache: outputs += (past_key_value,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class MptPreTrainedModel(PreTrainedModel):
    config_class = MptConfig
    base_model_prefix = "transformer"
    supports_gradient_checkpointing = True
    _no_split_modules = ["MptBlock"]
    _keys_to_ignore_on_load_missing = [r"lm_head.*."]
    def __init__(self, *inputs, **kwargs): super().__init__(*inputs, **kwargs)
    def _init_weights(self, module: nn.Module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, LayerNorm):
            if module.bias is not None: module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    @staticmethod
    def _convert_to_mpt_cache(past_key_value: Tuple[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[Tuple[torch.Tensor, torch.Tensor]]:
        batch_size, num_heads, head_dim, seq_length = past_key_value[0][0].shape
        batch_size_times_num_heads = batch_size * num_heads
        return tuple((layer_past[0].reshape(batch_size_times_num_heads, head_dim, seq_length), layer_past[1].reshape(batch_size_times_num_heads, seq_length, head_dim),) for layer_past in past_key_value)
MPT_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`MptConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MPT_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, input_ids_length)`):
            `input_ids_length` = `sequence_length` if `past_key_values` is `None` else `past_key_values[0][0].shape[2]`
            (`sequence_length` of input past key value states). Indices of input sequence tokens in the vocabulary.
            If `past_key_values` is used, only `input_ids` that do not have their past calculated should be passed as
            `input_ids`.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        past_key_values (`Tuple[Tuple[torch.Tensor]]` of length `config.n_layers`):
            Contains precomputed hidden-states (key and values in the attention blocks) as computed by the model (see
            `past_key_values` output below). Can be used to speed up sequential decoding. The `input_ids` which have
            their past given to this model should not be passed as `input_ids` as they have already been computed.
            Each element of `past_key_values` is a tuple (past_key, past_value):
            - past_key: [batch_size * num_heads, head_dim, kv_length]
            - past_value: [batch_size * num_heads, kv_length, head_dim]
        attention_mask (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
            If `past_key_values` is used, optionally only the last `inputs_embeds` have to be input (see
            `past_key_values`).
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare Mpt Model transformer outputting raw hidden-states without any specific head on top.", MPT_START_DOCSTRING)
class MptModel(MptPreTrainedModel):
    def __init__(self, config: MptConfig):
        super().__init__(config)
        self.hidden_size = config.hidden_size
        self.num_heads = config.n_heads
        self.wte = nn.Embedding(config.vocab_size, self.hidden_size)
        self.blocks = nn.ModuleList([MptBlock(config) for _ in range(config.n_layers)])
        self.norm_f = LayerNorm(self.hidden_size, eps=config.layer_norm_epsilon)
        self.norm_f.bias = None
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self): return self.wte
    def build_mpt_alibi_tensor(self, num_heads, sequence_length, alibi_bias_max=8, device=None): return build_mpt_alibi_tensor(num_heads, sequence_length, alibi_bias_max, device)
    def set_input_embeddings(self, new_embeddings: torch.Tensor): self.wte = new_embeddings
    @add_start_docstrings_to_model_forward(MPT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]] = None,
    attention_mask: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor, ...], BaseModelOutputWithPastAndCrossAttentions]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None: batch_size, seq_length = input_ids.shape
        elif inputs_embeds is not None: batch_size, seq_length, _ = inputs_embeds.shape
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if past_key_values is None: past_key_values = tuple([None] * len(self.blocks))
        if inputs_embeds is None: inputs_embeds = self.wte(input_ids)
        hidden_states = inputs_embeds
        presents = () if use_cache else None
        all_self_attentions = () if output_attentions else None
        all_hidden_states = () if output_hidden_states else None
        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...")
                use_cache = False
        seq_length_with_past = seq_length
        past_key_values_length = 0
        if past_key_values[0] is not None:
            past_key_values_length = past_key_values[0][0].shape[2]
            seq_length_with_past = seq_length_with_past + past_key_values_length
        if attention_mask is None: attention_mask = torch.ones((batch_size, seq_length_with_past), device=hidden_states.device)
        else: attention_mask = attention_mask.to(hidden_states.device)
        alibi = self.build_mpt_alibi_tensor(self.num_heads, self.config.max_seq_len, device=hidden_states.device)
        causal_mask = _prepare_4d_causal_attention_mask(attention_mask, (batch_size, seq_length), inputs_embeds, past_key_values_length)
        causal_mask = causal_mask.bool()
        for block, layer_past in zip(self.blocks, past_key_values):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: outputs = self._gradient_checkpointing_func(block.__call__, hidden_states, alibi, causal_mask, layer_past, use_cache, output_attentions)
            else: outputs = block(hidden_states, layer_past=layer_past, attention_mask=causal_mask, use_cache=use_cache, output_attentions=output_attentions, position_bias=alibi)
            hidden_states = outputs[0]
            if use_cache is True: presents = presents + (outputs[1],)
            if output_attentions: all_self_attentions = all_self_attentions + (outputs[2 if use_cache else 1],)
        hidden_states = self.norm_f(hidden_states)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, presents, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=presents, hidden_states=all_hidden_states, attentions=all_self_attentions)
@add_start_docstrings("The MPT Model transformer with a language modeling head on top (linear layer with weights tied to the input embeddings).", MPT_START_DOCSTRING)
class MptForCausalLM(MptPreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config: MptConfig):
        super().__init__(config)
        self.transformer = MptModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings: torch.Tensor): self.lm_head = new_embeddings
    def prepare_inputs_for_generation(self, input_ids: torch.LongTensor, past_key_values: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None,
    inputs_embeds: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, **kwargs) -> dict:
        if past_key_values is not None:
            past_length = past_key_values[0][0].shape[2]
            if input_ids.shape[1] > past_length: remove_prefix_length = past_length
            else: remove_prefix_length = input_ids.shape[1] - 1
            input_ids = input_ids[:, remove_prefix_length:]
        if inputs_embeds is not None and past_key_values is None: model_inputs = {"inputs_embeds": inputs_embeds}
        else: model_inputs = {"input_ids": input_ids}
        model_inputs.update({"past_key_values": past_key_values, "use_cache": use_cache, "attention_mask": attention_mask})
        return model_inputs
    @add_start_docstrings_to_model_forward(MPT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]] = None, attention_mask: Optional[torch.Tensor] = None,
    inputs_embeds: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], CausalLMOutputWithCrossAttentions]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        transformer_outputs = self.transformer(input_ids, past_key_values=past_key_values, attention_mask=attention_mask, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = transformer_outputs[0]
        lm_logits = self.lm_head(hidden_states)
        loss = None
        if labels is not None:
            labels = labels.to(lm_logits.device)
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            batch_size, seq_length, vocab_size = shift_logits.shape
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(batch_size * seq_length, vocab_size), shift_labels.view(batch_size * seq_length))
        if not return_dict:
            output = (lm_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return CausalLMOutputWithCrossAttentions(loss=loss, logits=lm_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states,
        attentions=transformer_outputs.attentions)
    def _reorder_cache(self, past: Tuple[Tuple[torch.Tensor, torch.Tensor], ...], beam_idx: torch.LongTensor) -> Tuple[Tuple[torch.Tensor, torch.Tensor], ...]:
        device_to_beam_idx = {past_state.device: beam_idx.to(past_state.device) for layer_past in past for past_state in layer_past}
        reordered_past = tuple((layer_past[0].index_select(0, device_to_beam_idx[layer_past[0].device]), layer_past[1].index_select(0, device_to_beam_idx[layer_past[0].device]),) for layer_past in past)
        return reordered_past
@add_start_docstrings("""
    The MPT Model transformer with a sequence classification head on top (linear layer).
    [`MptForSequenceClassification`] uses the last token in order to do the classification, as other causal models
    (e.g. GPT-1) do.
    Since it does classification on the last token, it requires to know the position of the last token. If a
    `pad_token_id` is defined in the configuration, it finds the last token that is not a padding token in each row. If
    no `pad_token_id` is defined, it simply takes the last value in each row of the batch. Since it cannot guess the
    padding tokens when `inputs_embeds` are passed instead of `input_ids`, it does the same (take the last value in
    each row of the batch).
""", MPT_START_DOCSTRING)
class MptForSequenceClassification(MptPreTrainedModel):
    def __init__(self, config: MptConfig):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.transformer = MptModel(config)
        self.score = nn.Linear(config.hidden_size, config.num_labels, bias=False)
        self.post_init()
    @add_start_docstrings_to_model_forward(MPT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]] = None,
    attention_mask: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], SequenceClassifierOutputWithPast]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        transformer_outputs = self.transformer(input_ids, past_key_values=past_key_values, attention_mask=attention_mask, inputs_embeds=inputs_embeds, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = transformer_outputs[0]
        logits = self.score(hidden_states)
        if input_ids is not None: batch_size = input_ids.shape[0]
        else: batch_size = inputs_embeds.shape[0]
        if self.config.pad_token_id is None and batch_size != 1: raise ValueError("Cannot handle batch sizes > 1 if no padding token is defined.")
        if self.config.pad_token_id is None: sequence_lengths = -1
        else:
            if input_ids is not None:
                sequence_lengths = torch.eq(input_ids, self.config.pad_token_id).int().argmax(-1) - 1
                sequence_lengths = sequence_lengths % input_ids.shape[-1]
                sequence_lengths = sequence_lengths.to(logits.device)
            else:
                sequence_lengths = -1
                logger.warning_once(f"{self.__class__.__name__} will not detect padding tokens in `inputs_embeds`. Results may be unexpected if using padding tokens in conjunction with `inputs_embeds.`")
        pooled_logits = logits[torch.arange(batch_size, device=logits.device), sequence_lengths]
        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(pooled_logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(pooled_logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(pooled_logits, labels)
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(pooled_logits, labels)
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutputWithPast(loss=loss, logits=pooled_logits, past_key_values=transformer_outputs.past_key_values, hidden_states=transformer_outputs.hidden_states,
        attentions=transformer_outputs.attentions)
@add_start_docstrings("MPT Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", MPT_START_DOCSTRING)
class MptForTokenClassification(MptPreTrainedModel):
    def __init__(self, config: MptConfig):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.transformer = MptModel(config)
        if hasattr(config, "classifier_dropout") and config.classifier_dropout is not None: classifier_dropout = config.classifier_dropout
        elif hasattr(config, "hidden_dropout") and config.hidden_dropout is not None: classifier_dropout = config.hidden_dropout
        else: classifier_dropout = 0.1
        self.dropout = nn.Dropout(classifier_dropout)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(MPT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]] = None, attention_mask: Optional[torch.Tensor] = None,
    inputs_embeds: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, **deprecated_arguments) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        transformer_outputs = self.transformer(input_ids, past_key_values=past_key_values, attention_mask=attention_mask, inputs_embeds=inputs_embeds, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = transformer_outputs[0]
        hidden_states = self.dropout(hidden_states)
        logits = self.classifier(hidden_states)
        loss = None
        if labels is not None:
            labels = labels.to(logits.device)
            batch_size, seq_length = labels.shape
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(batch_size * seq_length, self.num_labels), labels.view(batch_size * seq_length))
        if not return_dict:
            output = (logits,) + transformer_outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=transformer_outputs.hidden_states, attentions=transformer_outputs.attentions)
@add_start_docstrings("The MPT Model transformer with a span classification head on top for extractive question-answering tasks like SQuAD (a linear layers on top of the hidden-states output to compute `span start logits` and `span end logits`).", MPT_START_DOCSTRING)
class MptForQuestionAnswering(MptPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.transformer = MptModel(config)
        self.qa_outputs = nn.Linear(config.hidden_size, 2)
        self.post_init()
    @add_start_docstrings_to_model_forward(MPT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    start_positions: Optional[torch.LongTensor] = None, end_positions: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, QuestionAnsweringModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.transformer(input_ids, attention_mask=attention_mask, inputs_embeds=inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        logits = self.qa_outputs(sequence_output)
        start_logits, end_logits = logits.split(1, dim=-1)
        start_logits = start_logits.squeeze(-1).contiguous()
        end_logits = end_logits.squeeze(-1).contiguous()
        total_loss = None
        if start_positions is not None and end_positions is not None:
            if len(start_positions.size()) > 1: start_positions = start_positions.squeeze(-1)
            if len(end_positions.size()) > 1: end_positions = end_positions.squeeze(-1)
            ignored_index = start_logits.size(1)
            start_positions = start_positions.clamp(0, ignored_index)
            end_positions = end_positions.clamp(0, ignored_index)
            loss_fct = CrossEntropyLoss(ignore_index=ignored_index)
            start_loss = loss_fct(start_logits, start_positions)
            end_loss = loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2
        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output
        return QuestionAnsweringModelOutput(loss=total_loss, start_logits=start_logits, end_logits=end_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
