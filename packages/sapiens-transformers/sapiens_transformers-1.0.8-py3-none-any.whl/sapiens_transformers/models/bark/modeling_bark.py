"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Dict, Optional, Tuple, Union
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from ...generation import GenerationMixin
from ...generation.logits_process import (AlternatingCodebooksLogitsProcessor, BarkEosPrioritizerLogitsProcessor, SuppressTokensLogitsProcessor)
from ...modeling_attn_mask_utils import _prepare_4d_attention_mask
from ...modeling_outputs import CausalLMOutputWithPast, MaskedLMOutput
from ...modeling_utils import PreTrainedModel, get_parameter_device
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, is_sapiens_accelerator_available, is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, logging)
from ..auto import AutoModel
from .configuration_bark import (BarkCoarseConfig, BarkConfig, BarkFineConfig, BarkSemanticConfig, BarkSubModelConfig)
from .generation_configuration_bark import (BarkCoarseGenerationConfig, BarkFineGenerationConfig, BarkSemanticGenerationConfig)
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "suno/bark-small"
_CONFIG_FOR_DOC = "BarkConfig"
class BarkSelfAttention(nn.Module):
    def __init__(self, config, is_causal=False):
        super().__init__()
        self.dropout = config.dropout
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_heads
        self.head_dim = self.embed_dim // self.num_heads
        if config.hidden_size % config.num_heads != 0: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.att_proj = nn.Linear(config.hidden_size, 3 * config.hidden_size, bias=config.bias)
        self.out_proj = nn.Linear(config.hidden_size, config.hidden_size, bias=config.bias)
        self.is_causal = is_causal
        if is_causal:
            block_size = config.block_size
            bias = torch.tril(torch.ones((block_size, block_size), dtype=bool)).view(1, 1, block_size, block_size)
            self.register_buffer("bias", bias)
    def _split_heads(self, tensor, num_heads, attn_head_size):
        new_shape = tensor.size()[:-1] + (num_heads, attn_head_size)
        tensor = tensor.view(new_shape)
        return tensor.permute(0, 2, 1, 3)
    def _merge_heads(self, tensor, num_heads, attn_head_size):
        tensor = tensor.transpose(1, 2).contiguous()
        tensor = tensor.view(tensor.size()[:-2] + (num_heads * attn_head_size,))
        return tensor
    def _attn(self, query, key, value, attention_mask=None, head_mask=None):
        attn_weights = torch.matmul(query, key.transpose(-1, -2)) * (1.0 / math.sqrt(self.head_dim))
        if self.is_causal:
            query_length, key_length = query.size(-2), key.size(-2)
            attn_weights = attn_weights.masked_fill(self.bias[:, :, key_length - query_length : key_length, :key_length] == 0, torch.finfo(attn_weights.dtype).min)
        if attention_mask is not None: attn_weights = attn_weights + attention_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        attn_weights = attn_weights.to(value.dtype)
        attn_weights = self.attn_dropout(attn_weights)
        if head_mask is not None: attn_weights = attn_weights * head_mask
        attn_output = torch.matmul(attn_weights, value)
        return attn_output, attn_weights
    def forward(self, hidden_states, attention_mask=None, past_key_values=None, head_mask=None, use_cache=False, output_attentions=False):
        query, key, value = self.att_proj(hidden_states).split(self.embed_dim, dim=2)
        query = self._split_heads(query, self.num_heads, self.head_dim)
        key = self._split_heads(key, self.num_heads, self.head_dim)
        value = self._split_heads(value, self.num_heads, self.head_dim)
        if past_key_values is not None:
            past_key = past_key_values[0]
            past_value = past_key_values[1]
            key = torch.cat((past_key, key), dim=-2)
            value = torch.cat((past_value, value), dim=-2)
        if use_cache is True: present = (key, value)
        else: present = None
        attn_output, attn_weights = self._attn(query, key, value, attention_mask, head_mask)
        attn_output = self._merge_heads(attn_output, self.num_heads, self.head_dim)
        attn_output = self.out_proj(attn_output)
        attn_output = self.resid_dropout(attn_output)
        outputs = (attn_output, present)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class BarkSelfFlashAttention2(BarkSelfAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def _split_heads(self, tensor, num_heads, attn_head_size):
        new_shape = tensor.size()[:-1] + (num_heads, attn_head_size)
        tensor = tensor.view(new_shape)
        return tensor
    def _merge_heads(self, tensor, num_heads, attn_head_size):
        tensor = tensor.view(tensor.size()[:-2] + (num_heads * attn_head_size,))
        return tensor
    def forward(self, hidden_states, attention_mask=None, past_key_values=None, head_mask=None, use_cache=False, output_attentions=False):
        batch_size, query_len, _ = hidden_states.size()
        query, key, value = self.att_proj(hidden_states).split(self.embed_dim, dim=2)
        query = self._split_heads(query, self.num_heads, self.head_dim)
        key = self._split_heads(key, self.num_heads, self.head_dim)
        value = self._split_heads(value, self.num_heads, self.head_dim)
        if past_key_values is not None:
            past_key = past_key_values[0].transpose(1, 2)
            past_value = past_key_values[1].transpose(1, 2)
            key = torch.cat((past_key, key), dim=1)
            value = torch.cat((past_value, value), dim=1)
        if use_cache is True: present = (key.transpose(1, 2), value.transpose(1, 2))
        else: present = None
        attn_output = _flash_attention_forward(query, key, value, attention_mask, query_len, dropout=self.dropout, use_top_left_mask=self._flash_attn_uses_top_left_mask, is_causal=self.is_causal)
        attn_output = self._merge_heads(attn_output, self.num_heads, self.head_dim)
        attn_output = self.out_proj(attn_output)
        attn_output = self.resid_dropout(attn_output)
        outputs = (attn_output, present)
        if output_attentions:
            attn_weights = None
            outputs += (attn_weights,)
        return outputs
BARK_ATTENTION_CLASSES = {"eager": BarkSelfAttention, "flash_attention_2": BarkSelfFlashAttention2}
class BarkLayerNorm(nn.Module):
    def __init__(self, hidden_size, bias=True):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.bias = nn.Parameter(torch.zeros(hidden_size)) if bias else None
    def forward(self, input): return F.layer_norm(input, self.weight.shape, self.weight, self.bias, eps=1e-5)
class BarkMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.in_proj = nn.Linear(config.hidden_size, 4 * config.hidden_size, bias=config.bias)
        self.out_proj = nn.Linear(4 * config.hidden_size, config.hidden_size, bias=config.bias)
        self.dropout = nn.Dropout(config.dropout)
        self.gelu = nn.GELU()
    def forward(self, hidden_states):
        hidden_states = self.in_proj(hidden_states)
        hidden_states = self.gelu(hidden_states)
        hidden_states = self.out_proj(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class BarkBlock(nn.Module):
    def __init__(self, config, is_causal=False):
        super().__init__()
        if is_causal:
            self.layernorm_1 = BarkLayerNorm(config.hidden_size, bias=config.bias)
            self.layernorm_2 = BarkLayerNorm(config.hidden_size, bias=config.bias)
        else:
            self.layernorm_1 = nn.LayerNorm(config.hidden_size)
            self.layernorm_2 = nn.LayerNorm(config.hidden_size)
        self.attn = BARK_ATTENTION_CLASSES[config._attn_implementation](config, is_causal=is_causal)
        self.mlp = BarkMLP(config)
    def forward(self, hidden_states, past_key_values=None, attention_mask=None, head_mask=None, use_cache=False, output_attentions=False):
        intermediary_hidden_states = self.layernorm_1(hidden_states)
        attn_outputs = self.attn(intermediary_hidden_states, past_key_values=past_key_values, attention_mask=attention_mask, head_mask=head_mask, use_cache=use_cache, output_attentions=output_attentions)
        attn_output = attn_outputs[0]
        outputs = attn_outputs[1:]
        intermediary_hidden_states = hidden_states + attn_output
        intermediary_hidden_states = intermediary_hidden_states + self.mlp(self.layernorm_2(intermediary_hidden_states))
        if use_cache: outputs = (intermediary_hidden_states,) + outputs
        else: outputs = (intermediary_hidden_states,) + outputs[1:]
        return outputs
class BarkPreTrainedModel(PreTrainedModel):
    config_class = BarkConfig
    supports_gradient_checkpointing = False
    _supports_flash_attn_2 = True
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear,)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    def __init__(self, *inputs, **kwargs): super().__init__(*inputs, **kwargs)
    @property
    def device(self) -> torch.device:
        if not hasattr(self, "_hf_hook"): return get_parameter_device(self)
        for module in self.modules():
            if (hasattr(module, "_hf_hook") and hasattr(module._hf_hook, "execution_device") and module._hf_hook.execution_device is not None): return torch.device(module._hf_hook.execution_device)
        return get_parameter_device(self)
BARK_MODEL_START_DOCSTRING = """
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`{config}`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
BARK_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`BarkConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
BARK_FINE_INPUTS_DOCSTRING = r"""
    Args:
        codebook_idx (`int`):
            Index of the codebook that will be predicted.
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length, number_of_codebooks)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it. Initially, indices of the first two codebooks are obtained from the `coarse` sub-model. The rest is
            predicted recursively by attending the previously predicted channels. The model predicts on windows of
            length 1024.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`torch.Tensor` of shape `(encoder_layers, encoder_attention_heads)`, *optional*):
            Mask to nullify selected heads of the attention modules in the encoder. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*): NOT IMPLEMENTED YET.
        input_embeds (`torch.FloatTensor` of shape `(batch_size, input_sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. If
            `past_key_values` is used, optionally only the last `input_embeds` have to be input (see
            `past_key_values`). This is useful if you want more control over how to convert `input_ids` indices into
            associated vectors than the model's internal embedding lookup matrix.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
BARK_CAUSAL_MODEL_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it. Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details. [What are input IDs?](../glossary#input-ids)
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks) that can be used (see
            `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `input_ids` of shape `(batch_size, sequence_length)`.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        head_mask (`torch.Tensor` of shape `(encoder_layers, encoder_attention_heads)`, *optional*):
            Mask to nullify selected heads of the attention modules in the encoder. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        input_embeds (`torch.FloatTensor` of shape `(batch_size, input_sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation.
            Here, due to `Bark` particularities, if `past_key_values` is used, `input_embeds` will be ignored and you
            have to use `input_ids`. If `past_key_values` is not used and `use_cache` is set to `True`, `input_embeds`
            is used in priority instead of `input_ids`.
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
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
class BarkCausalModel(BarkPreTrainedModel, GenerationMixin):
    config_class = BarkSubModelConfig
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.input_embeds_layer = nn.Embedding(config.input_vocab_size, config.hidden_size)
        self.position_embeds_layer = nn.Embedding(config.block_size, config.hidden_size)
        self.drop = nn.Dropout(config.dropout)
        self.layers = nn.ModuleList([BarkBlock(config, is_causal=True) for _ in range(config.num_layers)])
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
        self.layernorm_final = BarkLayerNorm(config.hidden_size, bias=config.bias)
        self.lm_head = nn.Linear(config.hidden_size, config.output_vocab_size, bias=False)
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self): return self.input_embeds_layer
    def set_input_embeddings(self, new_embeddings): self.input_embeds_layer = new_embeddings
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, **kwargs):
        input_embeds = kwargs.get("input_embeds", None)
        attention_mask = kwargs.get("attention_mask", None)
        position_ids = kwargs.get("position_ids", None)
        if past_key_values is not None:
            seq_len = input_ids.shape[1]
            past_length = past_key_values[0][0].shape[2]
            if input_ids.shape[1] > past_length: remove_prefix_length = past_length
            else: remove_prefix_length = input_ids.shape[1] - 1
            input_ids = input_ids[:, remove_prefix_length:]
            input_embeds = None
        else:
            if input_embeds is not None and kwargs.get("use_cache"): seq_len = input_embeds.shape[1]
            else: seq_len = input_ids.shape[1]
        if attention_mask is not None: attention_mask = attention_mask[:, :seq_len]
        if position_ids is not None: position_ids = position_ids[:, :seq_len]
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :]
        else: position_ids = None
        if input_embeds is not None and kwargs.get("use_cache"): return {"input_ids": None, "input_embeds": input_embeds, "past_key_values": past_key_values, "use_cache": kwargs.get("use_cache"), "position_ids": position_ids, "attention_mask": attention_mask}
        return {"input_ids": input_ids, "past_key_values": past_key_values, "use_cache": kwargs.get("use_cache"), "position_ids": position_ids, "attention_mask": attention_mask}
    @add_start_docstrings_to_model_forward(BARK_CAUSAL_MODEL_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.Tensor] = None, past_key_values: Optional[Tuple[torch.FloatTensor]] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None,
    head_mask: Optional[torch.Tensor] = None, labels: Optional[torch.LongTensor] = None, input_embeds: Optional[torch.Tensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], CausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        loss = None
        if labels is not None: raise NotImplementedError("Training is not implemented yet for Bark - ensure you do not pass `labels` to the model.")
        if input_ids is not None and input_embeds is not None: raise ValueError("You cannot specify both input_ids and input_embeds at the same time")
        elif input_embeds is not None and past_key_values is None: pass
        elif input_ids is not None: input_embeds = self.input_embeds_layer(input_ids)
        elif input_embeds is not None: pass
        else: raise ValueError("You have to specify either input_ids or input_embeds")
        input_shape = input_embeds.size()[:-1]
        batch_size = input_embeds.shape[0]
        seq_length = input_shape[-1]
        device = input_ids.device if input_ids is not None else input_embeds.device
        if past_key_values is None:
            past_length = 0
            past_key_values = tuple([None] * len(self.layers))
        else: past_length = past_key_values[0][0].size(-2)
        if position_ids is None:
            position_ids = torch.arange(past_length, seq_length + past_length, dtype=torch.long, device=device)
            position_ids = position_ids.unsqueeze(0)
        position_embeds = self.position_embeds_layer(position_ids)
        if attention_mask is not None:
            if batch_size <= 0: raise ValueError("batch_size has to be defined and > 0")
            if self._use_flash_attention_2: attention_mask = attention_mask if 0 in attention_mask else None
            else:
                attention_mask = attention_mask.view(batch_size, -1)
                attention_mask = _prepare_4d_attention_mask(attention_mask, input_embeds.dtype, tgt_len=1)
        head_mask = self.get_head_mask(head_mask, self.config.num_layers)
        hidden_states = self.drop(input_embeds + position_embeds)
        output_shape = input_shape + (hidden_states.size(-1),)
        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...")
                use_cache = False
        present_key_values = () if use_cache else None
        all_self_attentions = () if output_attentions else None
        all_hidden_states = () if output_hidden_states else None
        for i, (block, past_layer_key_values) in enumerate(zip(self.layers, past_key_values)):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: outputs = self._gradient_checkpointing_func(block.__call__, hidden_states, None, attention_mask, head_mask[i], use_cache, output_attentions)
            else: outputs = block(hidden_states, past_key_values=past_layer_key_values, attention_mask=attention_mask, head_mask=head_mask[i], use_cache=use_cache, output_attentions=output_attentions)
            hidden_states = outputs[0]
            if use_cache: present_key_values = present_key_values + (outputs[1],)
            if output_attentions: all_self_attentions = all_self_attentions + (outputs[2 if use_cache else 1],)
        hidden_states = self.layernorm_final(hidden_states)
        hidden_states = hidden_states.view(output_shape)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        logits = self.lm_head(hidden_states)
        if not return_dict: return tuple(v for v in [None, logits, present_key_values, all_hidden_states, all_self_attentions] if v is not None)
        return CausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=present_key_values, hidden_states=all_hidden_states, attentions=all_self_attentions)
    @staticmethod
    def _reorder_cache(past_key_values: Tuple[Tuple[torch.Tensor]], beam_idx: torch.Tensor) -> Tuple[Tuple[torch.Tensor]]: return tuple(tuple(past_state.index_select(0, beam_idx.to(past_state.device)) for past_state in layer_past) for layer_past in past_key_values)
@add_start_docstrings("""Bark semantic (or text) model. It shares the same architecture as the coarse model.
    It is a GPT-2 like autoregressive model with a language modeling head on top.""", BARK_MODEL_START_DOCSTRING.format(config="BarkSemanticConfig"))
class BarkSemanticModel(BarkCausalModel):
    base_model_prefix = "semantic"
    config_class = BarkSemanticConfig
    def generate(self, input_ids: torch.Tensor, semantic_generation_config: BarkSemanticGenerationConfig = None, history_prompt: Optional[Dict[str, torch.Tensor]] = None, attention_mask: Optional[torch.Tensor] = None, **kwargs) -> torch.LongTensor:
        if semantic_generation_config is None: raise ValueError("`semantic_generation_config` has to be provided")
        batch_size = input_ids.shape[0]
        max_input_semantic_length = semantic_generation_config.max_input_semantic_length
        input_ids = input_ids + semantic_generation_config.text_encoding_offset
        if attention_mask is not None: input_ids = input_ids.masked_fill((1 - attention_mask).bool(), semantic_generation_config.text_pad_token)
        if history_prompt is not None:
            semantic_history = history_prompt["semantic_prompt"][-max_input_semantic_length:]
            semantic_history = nn.functional.pad(semantic_history, (0, max_input_semantic_length - len(semantic_history)), value=semantic_generation_config.semantic_pad_token, mode="constant")
        else: semantic_history = torch.tensor([semantic_generation_config.semantic_pad_token] * max_input_semantic_length, dtype=torch.int).to(self.device)
        semantic_history = torch.repeat_interleave(semantic_history[None], batch_size, dim=0)
        infer_array = torch.tensor([[semantic_generation_config.semantic_infer_token]] * batch_size, dtype=torch.int).to(self.device)
        input_embeds = torch.cat([self.input_embeds_layer(input_ids[:, :max_input_semantic_length]) + self.input_embeds_layer(semantic_history[:, : max_input_semantic_length + 1]), self.input_embeds_layer(infer_array)], dim=1)
        tokens_to_suppress = list(range(semantic_generation_config.semantic_vocab_size, semantic_generation_config.semantic_pad_token))
        tokens_to_suppress.extend(list(range(semantic_generation_config.semantic_pad_token + 1, self.config.output_vocab_size)))
        suppress_tokens_logits_processor = SuppressTokensLogitsProcessor(tokens_to_suppress, device=input_ids.device)
        min_eos_p = kwargs.get("min_eos_p", semantic_generation_config.min_eos_p)
        early_stopping_logits_processor = BarkEosPrioritizerLogitsProcessor(eos_token_id=semantic_generation_config.eos_token_id, min_eos_p=min_eos_p, device=input_ids.device)
        semantic_output = super().generate(torch.ones((batch_size, max_input_semantic_length + 1), dtype=torch.int).to(self.device), input_embeds=input_embeds, logits_processor=[suppress_tokens_logits_processor, early_stopping_logits_processor], generation_config=semantic_generation_config, **kwargs)
        semantic_output = semantic_output[:, max_input_semantic_length + 1 :]
        return semantic_output
@add_start_docstrings("""Bark coarse acoustics model.
    It shares the same architecture as the semantic (or text) model. It is a GPT-2 like autoregressive model with a
    language modeling head on top.""", BARK_MODEL_START_DOCSTRING.format(config="BarkCoarseConfig"))
class BarkCoarseModel(BarkCausalModel):
    base_model_prefix = "coarse_acoustics"
    config_class = BarkCoarseConfig
    def preprocess_histories(self, max_coarse_history: int, semantic_to_coarse_ratio: int, batch_size: int, semantic_generation_config: int, codebook_size: int, history_prompt: Optional[Dict[str, torch.Tensor]] = None):
        if history_prompt is not None:
            x_semantic_history = torch.repeat_interleave(history_prompt["semantic_prompt"][None], batch_size, dim=0)
            x_coarse_history = history_prompt["coarse_prompt"].clone()
            if codebook_size is not None:
                for n in range(1, x_coarse_history.shape[0]): x_coarse_history[n, :] += codebook_size * n
            x_coarse_history = torch.transpose(x_coarse_history, 0, 1).reshape(-1)
            x_coarse_history = x_coarse_history + semantic_generation_config.semantic_vocab_size
            x_coarse_history = torch.repeat_interleave(x_coarse_history[None], batch_size, dim=0)
            max_semantic_history = int(np.floor(max_coarse_history / semantic_to_coarse_ratio))
            n_semantic_hist_provided = min([max_semantic_history, x_semantic_history.shape[1] - x_semantic_history.shape[1] % 2, int(np.floor(x_coarse_history.shape[1] / semantic_to_coarse_ratio))])
            n_coarse_hist_provided = int(round(n_semantic_hist_provided * semantic_to_coarse_ratio))
            x_semantic_history = x_semantic_history[:, -n_semantic_hist_provided:].int()
            x_coarse_history = x_coarse_history[:, -n_coarse_hist_provided:].int()
            x_coarse_history = x_coarse_history[:, :-2]
        else:
            x_semantic_history = torch.tensor([[]] * batch_size, dtype=torch.int).to(self.device)
            x_coarse_history = torch.tensor([[]] * batch_size, dtype=torch.int).to(self.device)
        return x_semantic_history, x_coarse_history
    def generate(self, semantic_output: torch.Tensor, semantic_generation_config: BarkSemanticGenerationConfig = None, coarse_generation_config: BarkCoarseGenerationConfig = None,
    codebook_size: int = 1024, history_prompt: Optional[Dict[str, torch.Tensor]] = None, return_output_lengths: Optional[bool] = None, **kwargs) -> Union[torch.LongTensor, Tuple[torch.LongTensor, torch.LongTensor]]:
        if semantic_generation_config is None: raise ValueError("`semantic_generation_config` has to be provided")
        if coarse_generation_config is None: raise ValueError("`coarse_generation_config` has to be provided")
        max_coarse_input_length = coarse_generation_config.max_coarse_input_length
        max_coarse_history = coarse_generation_config.max_coarse_history
        sliding_window_len = coarse_generation_config.sliding_window_len
        semantic_output.masked_fill_(semantic_output == semantic_generation_config.semantic_pad_token, coarse_generation_config.coarse_semantic_pad_token)
        semantic_to_coarse_ratio = (coarse_generation_config.coarse_rate_hz / semantic_generation_config.semantic_rate_hz * coarse_generation_config.n_coarse_codebooks)
        max_semantic_history = int(np.floor(max_coarse_history / semantic_to_coarse_ratio))
        output_lengths = (semantic_output != coarse_generation_config.coarse_semantic_pad_token).sum(1)
        output_lengths = torch.floor(output_lengths * semantic_to_coarse_ratio / coarse_generation_config.n_coarse_codebooks)
        output_lengths = torch.round(output_lengths * coarse_generation_config.n_coarse_codebooks).int()
        max_generated_len = torch.max(output_lengths).item()
        batch_size = semantic_output.shape[0]
        x_semantic_history, x_coarse = self.preprocess_histories(history_prompt=history_prompt, max_coarse_history=max_coarse_history, semantic_to_coarse_ratio=semantic_to_coarse_ratio, batch_size=batch_size,
        semantic_generation_config=semantic_generation_config, codebook_size=codebook_size)
        base_semantic_idx = x_semantic_history.shape[1]
        semantic_output = torch.hstack([x_semantic_history, semantic_output])
        n_window_steps = int(np.ceil(max_generated_len / sliding_window_len))
        total_generated_len = 0
        len_coarse_history = x_coarse.shape[1]
        for _ in range(n_window_steps):
            semantic_idx = base_semantic_idx + int(round(total_generated_len / semantic_to_coarse_ratio))
            input_coarse = semantic_output[:, np.max([0, semantic_idx - max_semantic_history]) :]
            input_coarse = input_coarse[:, :max_coarse_input_length]
            input_coarse = F.pad(input_coarse, (0, max_coarse_input_length - input_coarse.shape[-1]), "constant", coarse_generation_config.coarse_semantic_pad_token)
            input_coarse = torch.hstack([input_coarse, torch.tensor([[coarse_generation_config.coarse_infer_token]] * batch_size).to(self.device), x_coarse[:, -max_coarse_history:]])
            alternatingLogitsProcessor = AlternatingCodebooksLogitsProcessor(input_coarse.shape[1], semantic_generation_config.semantic_vocab_size, codebook_size)
            output_coarse = super().generate(input_coarse, logits_processor=[alternatingLogitsProcessor], max_new_tokens=min(sliding_window_len, max_generated_len - total_generated_len),
            generation_config=coarse_generation_config, **kwargs)
            input_coarse_len = input_coarse.shape[1]
            x_coarse = torch.hstack([x_coarse, output_coarse[:, input_coarse_len:]])
            total_generated_len = x_coarse.shape[1] - len_coarse_history
            del output_coarse
        coarse_output = x_coarse[:, len_coarse_history:]
        if return_output_lengths: return coarse_output, output_lengths
        return coarse_output
@add_start_docstrings("""Bark fine acoustics model. It is a non-causal GPT-like model with `config.n_codes_total` embedding layers and
    language modeling heads, one for each codebook.""",
    BARK_MODEL_START_DOCSTRING.format(config="BarkFineConfig"))
class BarkFineModel(BarkPreTrainedModel):
    base_model_prefix = "fine_acoustics"
    config_class = BarkFineConfig
    main_input_name = "codebook_idx"
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.input_embeds_layers = nn.ModuleList([nn.Embedding(config.input_vocab_size, config.hidden_size) for _ in range(config.n_codes_total)])
        self.position_embeds_layer = nn.Embedding(config.block_size, config.hidden_size)
        self.drop = nn.Dropout(config.dropout)
        self.layers = nn.ModuleList([BarkBlock(config, is_causal=False) for _ in range(config.num_layers)])
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
        self.layernorm_final = nn.LayerNorm(config.hidden_size)
        self.lm_heads = nn.ModuleList([nn.Linear(config.hidden_size, config.output_vocab_size, bias=False) for _ in range(config.n_codes_given, config.n_codes_total)])
        self.gradient_checkpointing = False
        self.n_codes_total = config.n_codes_total
        self.post_init()
    def get_input_embeddings(self): return self.input_embeds_layers
    def set_input_embeddings(self, new_embeddings): self.input_embeds_layers = new_embeddings
    def get_output_embeddings(self): return self.lm_heads
    def set_output_embeddings(self, new_output_embeddings): self.lm_heads = new_output_embeddings
    def _resize_token_embeddings(self, new_num_tokens, pad_to_multiple_of=None):
        old_embeddings_list = self.get_input_embeddings()
        new_embeddings_list = nn.ModuleList([self._get_resized_embeddings(old_embeddings, new_num_tokens, pad_to_multiple_of) for old_embeddings in old_embeddings_list])
        self.set_input_embeddings(new_embeddings_list)
        new_num_tokens = new_embeddings_list[0].weight.shape[0]
        if self.get_output_embeddings() is not None and not self.config.tie_word_embeddings:
            old_lm_head_list = self.get_output_embeddings()
            new_lm_head_list = nn.ModuleList([self._get_resized_lm_head(old_lm_head, new_num_tokens) for old_lm_head in old_lm_head_list])
            self.set_output_embeddings(new_lm_head_list)
        return self.get_input_embeddings()
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of: Optional[int] = None) -> nn.Embedding:
        model_embeds = self._resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        if new_num_tokens is None and pad_to_multiple_of is None: return model_embeds
        self.config.output_vocab_size = model_embeds[0].weight.shape[0]
        self.config.vocab_size = model_embeds[0].weight.shape[0]
        self.output_vocab_size = model_embeds[0].weight.shape[0]
        self.vocab_size = model_embeds[0].weight.shape[0]
        self.tie_weights()
        return model_embeds
    def _tie_weights(self):
        if getattr(self.config, "tie_word_embeddings", True):
            self._tied_weights_keys = []
            output_embeddings = self.get_output_embeddings()
            input_embeddings = self.get_input_embeddings()
            for i in range(self.config.n_codes_total - self.config.n_codes_given):
                self._tie_or_clone_weights(output_embeddings[i], input_embeddings[i + 1])
                self._tied_weights_keys.append(f"lm_heads.{i}.weight")
    def tie_weights(self):
        if getattr(self.config, "tie_word_embeddings", True):
            self._tied_weights_keys = []
            output_embeddings = self.get_output_embeddings()
            input_embeddings = self.get_input_embeddings()
            for i in range(self.config.n_codes_total - self.config.n_codes_given):
                self._tie_or_clone_weights(output_embeddings[i], input_embeddings[i + 1])
                self._tied_weights_keys.append(f"lm_heads.{i}.weight")
        for module in self.modules():
            if hasattr(module, "_tie_weights"): module._tie_weights()
    @add_start_docstrings_to_model_forward(BARK_FINE_INPUTS_DOCSTRING)
    def forward(self, codebook_idx: int, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None,
    labels: Optional[torch.LongTensor] = None, input_embeds: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], MaskedLMOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        loss = None
        if labels is not None: raise NotImplementedError("Training is not implemented yet")
        if codebook_idx == 0: raise ValueError("Cannot predict 0th codebook - 0th codebook should be predicted by the coarse model")
        if input_ids is not None and input_embeds is not None: raise ValueError("You cannot specify both input_ids and input_embeds at the same time")
        if input_ids is None and input_embeds is None: raise ValueError("You have to specify either input_ids or input_embeds")
        if input_ids is not None:
            input_embeds = [input_embeds_layer(input_ids[:, :, i]).unsqueeze(-1) for i, input_embeds_layer in enumerate(self.input_embeds_layers)]
            input_embeds = torch.cat(input_embeds, dim=-1)
            input_embeds = input_embeds[:, :, :, : codebook_idx + 1].sum(dim=-1)
        input_shape = input_embeds.size()[:-1]
        batch_size = input_embeds.shape[0]
        seq_length = input_shape[1]
        device = input_ids.device if input_ids is not None else input_embeds.device
        if position_ids is None:
            position_ids = torch.arange(0, seq_length, dtype=torch.long, device=device)
            position_ids = position_ids.unsqueeze(0)
        position_embeds = self.position_embeds_layer(position_ids)
        if attention_mask is not None:
            if batch_size <= 0: raise ValueError("batch_size has to be defined and > 0")
            if self._use_flash_attention_2: attention_mask = attention_mask if 0 in attention_mask else None
            else: attention_mask = _prepare_4d_attention_mask(attention_mask, input_embeds.dtype, tgt_len=1)
        head_mask = self.get_head_mask(head_mask, self.config.num_layers)
        hidden_states = self.drop(input_embeds + position_embeds)
        output_shape = input_shape + (hidden_states.size(-1),)
        all_self_attentions = () if output_attentions else None
        all_hidden_states = () if output_hidden_states else None
        for i, block in enumerate(self.layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            outputs = block(hidden_states, attention_mask=attention_mask, head_mask=head_mask[i], output_attentions=output_attentions)
            hidden_states = outputs[0]
            if output_attentions: all_self_attentions = all_self_attentions + (outputs[1],)
        hidden_states = self.layernorm_final(hidden_states)
        hidden_states = hidden_states.view(output_shape)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        logits = self.lm_heads[codebook_idx - self.config.n_codes_given](hidden_states)
        if not return_dict: return tuple(v for v in [None, logits, all_hidden_states, all_self_attentions] if v is not None)
        return MaskedLMOutput(loss=loss, logits=logits, hidden_states=all_hidden_states, attentions=all_self_attentions)
    def generate(self, coarse_output: torch.Tensor, semantic_generation_config: BarkSemanticGenerationConfig = None, coarse_generation_config: BarkCoarseGenerationConfig = None,
    fine_generation_config: BarkFineGenerationConfig = None, codebook_size: int = 1024, history_prompt: Optional[Dict[str, torch.Tensor]] = None, **kwargs) -> torch.LongTensor:
        if semantic_generation_config is None: raise ValueError("`semantic_generation_config` has to be provided")
        if coarse_generation_config is None: raise ValueError("`coarse_generation_config` has to be provided")
        if fine_generation_config is None: raise ValueError("`fine_generation_config` has to be provided")
        temperature = kwargs.get("temperature", fine_generation_config.temperature)
        max_fine_history_length = fine_generation_config.max_fine_history_length
        max_fine_input_length = fine_generation_config.max_fine_input_length
        coarse_output = coarse_output.view(coarse_output.shape[0], -1, coarse_generation_config.n_coarse_codebooks)
        coarse_output = torch.remainder(coarse_output - semantic_generation_config.semantic_vocab_size, codebook_size)
        batch_size = coarse_output.shape[0]
        if history_prompt is not None: x_fine_history = torch.repeat_interleave(history_prompt["fine_prompt"].T[None], batch_size, dim=0)
        else: x_fine_history = None
        n_coarse = coarse_generation_config.n_coarse_codebooks
        fine_input = F.pad(coarse_output, (0, fine_generation_config.n_fine_codebooks - n_coarse), "constant", codebook_size)
        if x_fine_history is not None:
            fine_input = torch.cat([x_fine_history[:, -max_fine_history_length:, :], fine_input], dim=1)
            n_history = x_fine_history[:, -max_fine_history_length:, :].shape[1]
        else: n_history = 0
        n_remove_from_end = 0
        if fine_input.shape[1] < max_fine_input_length:
            n_remove_from_end = max_fine_input_length - fine_input.shape[1]
            fine_input = F.pad(fine_input, (0, 0, 0, n_remove_from_end), mode="constant", value=codebook_size)
        n_loops = (coarse_output.shape[1] - (max_fine_input_length - n_history)) / max_fine_history_length
        n_loops = int(np.ceil(n_loops))
        n_loops = max(0, n_loops) + 1
        for n_outer in range(n_loops):
            start_idx = min([n_outer * max_fine_history_length, fine_input.shape[1] - max_fine_input_length])
            start_fill_idx = min([n_history + n_outer * max_fine_history_length, fine_input.shape[1] - max_fine_history_length])
            rel_start_fill_idx = start_fill_idx - start_idx
            input_buffer = fine_input[:, start_idx : start_idx + max_fine_input_length, :]
            for n_inner in range(n_coarse, fine_generation_config.n_fine_codebooks):
                logits = self.forward(n_inner, input_buffer).logits
                if temperature is None or temperature == 1.0:
                    relevant_logits = logits[:, rel_start_fill_idx:, :codebook_size]
                    codebook_preds = torch.argmax(relevant_logits, -1)
                else:
                    relevant_logits = logits[:, :, :codebook_size] / temperature
                    probs = F.softmax(relevant_logits, dim=-1)[:, rel_start_fill_idx:max_fine_input_length]
                    probs = probs.reshape((-1, codebook_size))
                    codebook_preds = torch.multinomial(probs, num_samples=1).view(batch_size, -1)
                codebook_preds = codebook_preds.to(torch.int32)
                input_buffer[:, rel_start_fill_idx:, n_inner] = codebook_preds
                del logits, codebook_preds
            for n_inner in range(n_coarse, fine_generation_config.n_fine_codebooks): fine_input[:, start_fill_idx : start_fill_idx + (max_fine_input_length - rel_start_fill_idx), n_inner] = input_buffer[:, rel_start_fill_idx:, n_inner]
            del input_buffer
        fine_input = fine_input.transpose(1, 2)[:, :, n_history:]
        if n_remove_from_end > 0: fine_input = fine_input[:, :, :-n_remove_from_end]
        if fine_input.shape[-1] != coarse_output.shape[-2]: raise ValueError("input and output should have the same seq_len")
        return fine_input
@add_start_docstrings("""
    The full Bark model, a text-to-speech model composed of 4 sub-models:
    - [`BarkSemanticModel`] (also referred to as the 'text' model): a causal auto-regressive transformer model that
      takes
    as input tokenized text, and predicts semantic text tokens that capture the meaning of the text.
    - [`BarkCoarseModel`] (also refered to as the 'coarse acoustics' model), also a causal autoregressive transformer,
    that takes into input the results of the last model. It aims at regressing the first two audio codebooks necessary
    to `encodec`.
    - [`BarkFineModel`] (the 'fine acoustics' model), this time a non-causal autoencoder transformer, which iteratively
    predicts the last codebooks based on the sum of the previous codebooks embeddings.
    - having predicted all the codebook channels from the [`EncodecModel`], Bark uses it to decode the output audio
      array.
    It should be noted that each of the first three modules can support conditional speaker embeddings to condition the
    output sound according to specific predefined voice.
    """, BARK_START_DOCSTRING)
class BarkModel(BarkPreTrainedModel):
    config_class = BarkConfig
    def __init__(self, config):
        super().__init__(config)
        self.semantic = BarkSemanticModel(config.semantic_config)
        self.coarse_acoustics = BarkCoarseModel(config.coarse_acoustics_config)
        self.fine_acoustics = BarkFineModel(config.fine_acoustics_config)
        self.codec_model = AutoModel.from_config(config.codec_config)
        self.config = config
    @property
    def device(self) -> torch.device:
        if not hasattr(self.semantic, "_hf_hook"): return get_parameter_device(self)
        for module in self.semantic.modules():
            if (hasattr(module, "_hf_hook") and hasattr(module._hf_hook, "execution_device") and module._hf_hook.execution_device is not None): return torch.device(module._hf_hook.execution_device)
    def enable_cpu_offload(self, gpu_id: Optional[int] = 0):
        if is_sapiens_accelerator_available(): from sapiens_accelerator import cpu_offload_with_hook
        else: raise ImportError("`enable_model_cpu_offload` requires `sapiens_accelerator`.")
        device = torch.device(f"cuda:{gpu_id}")
        if self.device.type != "cpu":
            self.to("cpu")
            torch.cuda.empty_cache()
        self.semantic.input_embeds_layer, _ = cpu_offload_with_hook(self.semantic.input_embeds_layer, device)
        hook = None
        for cpu_offloaded_model in [self.semantic, self.coarse_acoustics, self.fine_acoustics]: _, hook = cpu_offload_with_hook(cpu_offloaded_model, device, prev_module_hook=hook)
        self.fine_acoustics_hook = hook
        _, hook = cpu_offload_with_hook(self.codec_model, device, prev_module_hook=hook)
        self.codec_model_hook = hook
    def codec_decode(self, fine_output, output_lengths=None):
        fine_output = fine_output.transpose(0, 1)
        emb = self.codec_model.quantizer.decode(fine_output)
        if output_lengths is not None:
            out = [sample[:, :l].unsqueeze(0) for (sample, l) in zip(emb, output_lengths)]
            audio_arr = [self.codec_model.decoder(sample).squeeze() for sample in out]
        else:
            out = self.codec_model.decoder(emb)
            audio_arr = out.squeeze(1)
        return audio_arr
    @torch.no_grad()
    def generate(self, input_ids: Optional[torch.Tensor] = None, history_prompt: Optional[Dict[str, torch.Tensor]] = None, return_output_lengths: Optional[bool] = None, **kwargs) -> torch.LongTensor:
        semantic_generation_config = BarkSemanticGenerationConfig(**self.generation_config.semantic_config)
        coarse_generation_config = BarkCoarseGenerationConfig(**self.generation_config.coarse_acoustics_config)
        fine_generation_config = BarkFineGenerationConfig(**self.generation_config.fine_acoustics_config)
        kwargs_semantic = {"attention_mask": kwargs.pop("attention_mask", None), "min_eos_p": kwargs.pop("min_eos_p", None)}
        kwargs_coarse = {}
        kwargs_fine = {}
        for key, value in kwargs.items():
            if key.startswith("semantic_"):
                key = key[len("semantic_") :]
                kwargs_semantic[key] = value
            elif key.startswith("coarse_"):
                key = key[len("coarse_") :]
                kwargs_coarse[key] = value
            elif key.startswith("fine_"):
                key = key[len("fine_") :]
                kwargs_fine[key] = value
            else:
                if key not in kwargs_semantic: kwargs_semantic[key] = value
                if key not in kwargs_coarse: kwargs_coarse[key] = value
                if key not in kwargs_fine: kwargs_fine[key] = value
        semantic_output = self.semantic.generate(input_ids, history_prompt=history_prompt, semantic_generation_config=semantic_generation_config, **kwargs_semantic)
        coarse_output = self.coarse_acoustics.generate(semantic_output, history_prompt=history_prompt, semantic_generation_config=semantic_generation_config, coarse_generation_config=coarse_generation_config,
        codebook_size=self.generation_config.codebook_size, return_output_lengths=return_output_lengths, **kwargs_coarse)
        output_lengths = None
        if return_output_lengths:
            coarse_output, output_lengths = coarse_output
            output_lengths = output_lengths // coarse_generation_config.n_coarse_codebooks
        output = self.fine_acoustics.generate(coarse_output, history_prompt=history_prompt, semantic_generation_config=semantic_generation_config, coarse_generation_config=coarse_generation_config,
        fine_generation_config=fine_generation_config, codebook_size=self.generation_config.codebook_size, **kwargs_fine)
        if getattr(self, "fine_acoustics_hook", None) is not None:
            self.fine_acoustics_hook.offload()
            self.codec_model = self.codec_model.to(self.device)
        audio = self.codec_decode(output, output_lengths)
        if getattr(self, "codec_model_hook", None) is not None: self.codec_model_hook.offload()
        if return_output_lengths:
            output_lengths = [len(sample) for sample in audio]
            audio = nn.utils.rnn.pad_sequence(audio, batch_first=True, padding_value=0)
            return audio, output_lengths
        return audio
    @classmethod
    def _check_and_enable_flash_attn_2(cls, config, torch_dtype: Optional[torch.dtype] = None, device_map: Optional[Union[str, Dict[str, int]]] = None, hard_check_only: bool = False, check_device_map: bool = False):
        config = super()._check_and_enable_flash_attn_2(config, torch_dtype, device_map, hard_check_only=hard_check_only, check_device_map=check_device_map)
        config.semantic_config._attn_implementation = config._attn_implementation
        config.coarse_acoustics_config._attn_implementation = config._attn_implementation
        config.fine_acoustics_config._attn_implementation = config._attn_implementation
        return config
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
