"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import math
from typing import Optional, Tuple, Union
import torch
from torch import nn
from torch.nn import CrossEntropyLoss
from ....activations import ACT2FN
from ....modeling_attn_mask_utils import _prepare_4d_attention_mask, _prepare_4d_causal_attention_mask
from ....modeling_outputs import BaseModelOutputWithPastAndCrossAttentions, CausalLMOutputWithCrossAttentions
from ....modeling_utils import PreTrainedModel
from ....utils import add_start_docstrings, logging, replace_return_docstrings
from .configuration_speech_to_text_2 import Speech2Text2Config
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "Speech2Text2Config"
_CHECKPOINT_FOR_DOC = "facebook/s2t-wav2vec2-large-en-de"
class Speech2Text2SinusoidalPositionalEmbedding(nn.Module):
    def __init__(self, num_positions: int, embedding_dim: int, padding_idx: Optional[int] = None):
        super().__init__()
        self.offset = 2
        self.embedding_dim = embedding_dim
        self.padding_idx = padding_idx
        self.make_weights(num_positions + self.offset, embedding_dim, padding_idx)
    def make_weights(self, num_embeddings: int, embedding_dim: int, padding_idx: Optional[int] = None):
        emb_weights = self.get_embedding(num_embeddings, embedding_dim, padding_idx)
        if hasattr(self, "weights"): emb_weights = emb_weights.to(dtype=self.weights.dtype, device=self.weights.device)
        self.weights = nn.Parameter(emb_weights)
        self.weights.requires_grad = False
        self.weights.detach_()
    @staticmethod
    def get_embedding(num_embeddings: int, embedding_dim: int, padding_idx: Optional[int] = None):
        half_dim = embedding_dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, dtype=torch.int64).float() * -emb)
        emb = torch.arange(num_embeddings, dtype=torch.int64).float().unsqueeze(1) * emb.unsqueeze(0)
        emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=1).view(num_embeddings, -1)
        if embedding_dim % 2 == 1: emb = torch.cat([emb, torch.zeros(num_embeddings, 1)], dim=1)
        if padding_idx is not None: emb[padding_idx, :] = 0
        return emb.to(torch.get_default_dtype())
    @torch.no_grad()
    def forward(self, input_ids: torch.Tensor, past_key_values_length: int = 0):
        bsz, seq_len = input_ids.size()
        position_ids = self.create_position_ids_from_input_ids(input_ids, self.padding_idx, past_key_values_length).to(input_ids.device)
        max_pos = self.padding_idx + 1 + seq_len
        if max_pos > self.weights.size(0): self.make_weights(max_pos + self.offset, self.embedding_dim, self.padding_idx)
        return self.weights.index_select(0, position_ids.view(-1)).view(bsz, seq_len, -1).detach()
    def create_position_ids_from_input_ids(self, input_ids: torch.Tensor, padding_idx: int, past_key_values_length: Optional[int] = 0):
        mask = input_ids.ne(padding_idx).int()
        incremental_indices = (torch.cumsum(mask, dim=1).type_as(mask) + past_key_values_length) * mask
        return incremental_indices.long() + padding_idx
class Speech2Text2Attention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True, is_causal: bool = False, config: Optional[Speech2Text2Config] = None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        self.config = config
        if (self.head_dim * num_heads) != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {num_heads}).")
        self.scaling = self.head_dim**-0.5
        self.is_decoder = is_decoder
        self.is_causal = is_causal
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, attention_mask: Optional[torch.Tensor] = None,
    layer_head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scaling
        if (is_cross_attention and past_key_value is not None and past_key_value[0].shape[2] == key_value_states.shape[1]):
            key_states = past_key_value[0]
            value_states = past_key_value[1]
        elif is_cross_attention:
            key_states = self._shape(self.k_proj(key_value_states), -1, bsz)
            value_states = self._shape(self.v_proj(key_value_states), -1, bsz)
        elif past_key_value is not None:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
            key_states = torch.cat([past_key_value[0], key_states], dim=2)
            value_states = torch.cat([past_key_value[1], value_states], dim=2)
        else:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
        if self.is_decoder: past_key_value = (key_states, value_states)
        proj_shape = (bsz * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, tgt_len, bsz).view(*proj_shape)
        key_states = key_states.reshape(*proj_shape)
        value_states = value_states.reshape(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if layer_head_mask is not None:
            if layer_head_mask.size() != (self.num_heads,): raise ValueError(f"Head mask for a single layer should be of size {(self.num_heads,)}, but is {layer_head_mask.size()}")
            attn_weights = layer_head_mask.view(1, -1, 1, 1) * attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights_reshaped.view(bsz * self.num_heads, tgt_len, src_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz * self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped, past_key_value
class Speech2Text2DecoderLayer(nn.Module):
    def __init__(self, config: Speech2Text2Config):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = Speech2Text2Attention(embed_dim=self.embed_dim, num_heads=config.decoder_attention_heads, dropout=config.attention_dropout, is_decoder=True)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        if config.is_decoder:
            self.encoder_attn = Speech2Text2Attention(self.embed_dim, config.decoder_attention_heads, dropout=config.attention_dropout, is_decoder=True)
            self.encoder_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.fc1 = nn.Linear(self.embed_dim, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, encoder_hidden_states: Optional[torch.Tensor] = None, encoder_attention_mask: Optional[torch.Tensor] = None,
    layer_head_mask: Optional[torch.Tensor] = None, cross_attn_layer_head_mask: Optional[torch.Tensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = True):
        residual = hidden_states
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, past_key_value=self_attn_past_key_value, attention_mask=attention_mask, layer_head_mask=layer_head_mask, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        cross_attn_present_key_value = None
        cross_attn_weights = None
        if encoder_hidden_states is not None:
            residual = hidden_states
            cross_attn_past_key_value = past_key_value[-2:] if past_key_value is not None else None
            hidden_states, cross_attn_weights, cross_attn_present_key_value = self.encoder_attn(hidden_states=hidden_states, key_value_states=encoder_hidden_states, attention_mask=encoder_attention_mask, layer_head_mask=cross_attn_layer_head_mask, past_key_value=cross_attn_past_key_value, output_attentions=output_attentions)
            hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
            hidden_states = residual + hidden_states
            hidden_states = self.encoder_attn_layer_norm(hidden_states)
            present_key_value = present_key_value + cross_attn_present_key_value
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights, cross_attn_weights)
        if use_cache: outputs += (present_key_value,)
        return outputs
class Speech2Text2PreTrainedModel(PreTrainedModel):
    config_class = Speech2Text2Config
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        std = self.config.init_std
        if isinstance(module, (nn.Linear, nn.Conv1d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
SPEECH_TO_TEXT_2_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`Speech2Text2Config`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
class Speech2Text2Decoder(Speech2Text2PreTrainedModel):
    def __init__(self, config: Speech2Text2Config):
        super().__init__(config)
        self.dropout = config.dropout
        self.layerdrop = config.decoder_layerdrop
        self.padding_idx = config.pad_token_id
        self.max_target_positions = config.max_target_positions
        self.embed_scale = math.sqrt(config.d_model) if config.scale_embedding else 1.0
        self.embed_tokens = nn.Embedding(config.vocab_size, config.d_model, self.padding_idx)
        self.embed_positions = Speech2Text2SinusoidalPositionalEmbedding(self.max_target_positions, config.d_model, self.padding_idx)
        self.layers = nn.ModuleList([Speech2Text2DecoderLayer(config) for _ in range(config.decoder_layers)])
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    def forward(self, input_ids=None, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, head_mask=None, cross_attn_head_mask=None, past_key_values=None,
    inputs_embeds=None, use_cache=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both decoder_input_ids and decoder_inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
        elif inputs_embeds is not None: input_shape = inputs_embeds.size()[:-1]
        else: raise ValueError("You have to specify either decoder_input_ids or decoder_inputs_embeds")
        past_key_values_length = past_key_values[0][0].shape[2] if past_key_values is not None else 0
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids) * self.embed_scale
        attention_mask = _prepare_4d_causal_attention_mask(attention_mask, input_shape, inputs_embeds, past_key_values_length)
        if encoder_hidden_states is not None and encoder_attention_mask is not None: encoder_attention_mask = _prepare_4d_attention_mask(encoder_attention_mask, inputs_embeds.dtype, tgt_len=input_shape[-1])
        positions = self.embed_positions(input_ids, past_key_values_length=past_key_values_length)
        hidden_states = inputs_embeds + positions
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once("`use_cache = True` is incompatible with gradient checkpointing. Setting `use_cache =" " False`...")
                use_cache = False
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        next_decoder_cache = () if use_cache else None
        for attn_mask, mask_name in zip([head_mask, cross_attn_head_mask], ["head_mask", "cross_attn_head_mask"]):
            if attn_mask is not None:
                if attn_mask.size()[0] != (len(self.layers)): raise ValueError(f"The `{mask_name}` should be specified for {len(self.layers)} layers, but it is for {head_mask.size()[0]}.")
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.training:
                dropout_probability = torch.rand([])
                if dropout_probability < self.layerdrop: continue
            past_key_value = past_key_values[idx] if past_key_values is not None else None
            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, attention_mask, encoder_hidden_states, encoder_attention_mask,
                head_mask[idx] if head_mask is not None else None, cross_attn_head_mask[idx] if cross_attn_head_mask is not None else None, None)
            else:
                layer_outputs = decoder_layer(hidden_states, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
                layer_head_mask=(head_mask[idx] if head_mask is not None else None), cross_attn_layer_head_mask=(cross_attn_head_mask[idx] if cross_attn_head_mask is not None else None),
                past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache += (layer_outputs[3 if output_attentions else 1],)
            if output_attentions:
                all_self_attns += (layer_outputs[1],)
                if encoder_hidden_states is not None: all_cross_attentions += (layer_outputs[2],)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attns, all_cross_attentions] if v is not None)
        return BaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states, attentions=all_self_attns, cross_attentions=all_cross_attentions)
@add_start_docstrings("The Speech2Text2 Model with a language modeling head. Can be used for summarization.", SPEECH_TO_TEXT_2_START_DOCSTRING)
class Speech2Text2DecoderWrapper(Speech2Text2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.decoder = Speech2Text2Decoder(config)
    def forward(self, *args, **kwargs): return self.decoder(*args, **kwargs)
@add_start_docstrings("The Speech2Text2 Decoder with a language modeling head. Can be used as the decoder part of [`EncoderDecoderModel`] and [`SpeechEncoderDecoder`].", SPEECH_TO_TEXT_2_START_DOCSTRING)
class Speech2Text2ForCausalLM(Speech2Text2PreTrainedModel):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        config = copy.deepcopy(config)
        config.is_decoder = True
        config.is_encoder_decoder = False
        super().__init__(config)
        self.model = Speech2Text2DecoderWrapper(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self): return self.model.decoder.embed_tokens
    def set_input_embeddings(self, value): self.model.decoder.embed_tokens = value
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def set_decoder(self, decoder): self.model.decoder = decoder
    def get_decoder(self): return self.model.decoder
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None, encoder_attention_mask: Optional[torch.FloatTensor] = None,
    head_mask: Optional[torch.Tensor] = None, cross_attn_head_mask: Optional[torch.Tensor] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], CausalLMOutputWithCrossAttentions]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model.decoder(input_ids=input_ids, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
        head_mask=head_mask, cross_attn_head_mask=cross_attn_head_mask, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits = self.lm_head(outputs[0])
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.config.vocab_size), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return CausalLMOutputWithCrossAttentions(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions, cross_attentions=outputs.cross_attentions)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
        if attention_mask is None: attention_mask = input_ids.new_ones(input_ids.shape)
        if past_key_values:
            past_length = past_key_values[0][0].shape[2]
            if input_ids.shape[1] > past_length: remove_prefix_length = past_length
            else: remove_prefix_length = input_ids.shape[1] - 1
            input_ids = input_ids[:, remove_prefix_length:]
        return {"input_ids": input_ids, "attention_mask": attention_mask, "past_key_values": past_key_values, "use_cache": use_cache}
    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values: reordered_past += (tuple(past_state.index_select(0, beam_idx.to(past_state.device)) for past_state in layer_past),)
        return reordered_past
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
