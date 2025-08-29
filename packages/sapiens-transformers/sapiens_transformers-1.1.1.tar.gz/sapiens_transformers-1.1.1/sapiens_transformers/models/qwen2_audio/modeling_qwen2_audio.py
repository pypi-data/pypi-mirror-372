"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...cache_utils import Cache, EncoderDecoderCache, StaticCache
from ...generation import GenerationMixin
from ...modeling_outputs import BaseModelOutput, ModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10,
logging, replace_return_docstrings)
from ..auto import AutoModel, AutoModelForCausalLM
from .configuration_qwen2_audio import Qwen2AudioConfig, Qwen2AudioEncoderConfig
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "Qwen2AudioConfig"
@dataclass
class Qwen2AudioCausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    past_key_values: Optional[List[torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    attention_mask: Optional[torch.FloatTensor] = None
class Qwen2AudioAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True, is_causal: bool = False, layer_idx: Optional[int] = None, config: Optional[Qwen2AudioConfig] = None):
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
        if layer_idx is None and is_decoder: logger.warning_once(f"Instantiating a decoder {self.__class__.__name__} without passing `layer_idx` is not recommended and will to errors during the forward call, if caching is used. Please make sure to provide a `layer_idx` when creating this class.")
        self.layer_idx = layer_idx
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[EncoderDecoderCache] = None,
    attention_mask: Optional[torch.Tensor] = None, layer_head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False,
    cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self._shape(self.q_proj(hidden_states) * self.scaling, tgt_len, bsz)
        if past_key_value is not None:
            is_updated = past_key_value.is_updated.get(self.layer_idx)
            if is_cross_attention:
                past_key_value.is_updated[self.layer_idx] = True
                past_key_value = past_key_value.cross_attention_cache
            else: past_key_value = past_key_value.self_attention_cache
        current_states = key_value_states if key_value_states is not None else hidden_states
        if is_cross_attention and past_key_value and is_updated:
            key_states = past_key_value.key_cache[self.layer_idx]
            value_states = past_key_value.value_cache[self.layer_idx]
        else:
            key_states = self._shape(self.k_proj(current_states), -1, bsz)
            value_states = self._shape(self.v_proj(current_states), -1, bsz)
            if past_key_value is not None:
                cache_position = cache_position if not is_cross_attention else None
                key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3))
        if attention_mask is not None:
            causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
            attn_weights = attn_weights + causal_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if layer_head_mask is not None:
            if layer_head_mask.size() != (self.num_heads,): raise ValueError(f"Head mask for a single layer should be of size {(self.num_heads,)}, but is {layer_head_mask.size()}")
            attn_weights = layer_head_mask.view(1, -1, 1, 1) * attn_weights
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.matmul(attn_probs, value_states)
        if attn_output.size() != (bsz, self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights, past_key_value
class Qwen2AudioFlashAttention2(Qwen2AudioAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[EncoderDecoderCache] = None, attention_mask: Optional[torch.Tensor] = None,
    layer_head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if isinstance(past_key_value, StaticCache): raise ValueError("The `static` cache implementation is not compatible with `attn_implementation='flash_attention_2'`.")
        if output_attentions: raise ValueError("Qwen2AudioFlashAttention2 attention does not support output_attentions")
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = torch.reshape(self.q_proj(hidden_states), (bsz, tgt_len, self.num_heads, self.head_dim))
        if past_key_value is not None:
            is_updated = past_key_value.is_updated.get(self.layer_idx)
            if is_cross_attention:
                past_key_value.is_updated[self.layer_idx] = True
                past_key_value = past_key_value.cross_attention_cache
            else: past_key_value = past_key_value.self_attention_cache
        current_states = key_value_states if key_value_states is not None else hidden_states
        if is_cross_attention and past_key_value and is_updated:
            key_states = past_key_value.key_cache[self.layer_idx]
            value_states = past_key_value.value_cache[self.layer_idx]
        else:
            key_states = self._shape(self.k_proj(current_states), -1, bsz)
            value_states = self._shape(self.v_proj(current_states), -1, bsz)
            if past_key_value is not None:
                cache_position = cache_position if not is_cross_attention else None
                key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)
        causal_mask = attention_mask
        if attention_mask is not None: causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
        input_dtype = query_states.dtype
        if input_dtype == torch.float32:
            if torch.is_autocast_enabled(): target_dtype = torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            logger.warning_once(f"The input hidden states seems to be silently casted in float32, this might be related to the fact you have upcasted embedding or layer norm layers in float32. We will cast back the input in {target_dtype}.")
            query_states = query_states.to(target_dtype)
            key_states = key_states.to(target_dtype)
            value_states = value_states.to(target_dtype)
        attn_output = _flash_attention_forward(query_states, key_states, value_states, causal_mask, tgt_len, dropout=self.dropout, is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        attn_output = attn_output.reshape(bsz, tgt_len, -1)
        attn_output = self.out_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class Qwen2AudioSdpaAttention(Qwen2AudioAttention):
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[EncoderDecoderCache] = None, attention_mask: Optional[torch.Tensor] = None,
    layer_head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, cache_position: Optional[torch.LongTensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        if output_attentions or layer_head_mask is not None:
            logger.warning_once("Qwen2AudioModel is using Qwen2AudioSdpaAttention, but `torch.nn.functional.scaled_dot_product_attention` does not support `output_attentions=True` or `layer_head_mask` not None. Falling back to the manual attention"+' implementation, but specifying the manual implementation will be required from sapiens_transformers version v5.0.0 onwards. This warning can be removed using the argument `attn_implementation="eager"` when loading the model.')
            return super().forward(hidden_states, key_value_states=key_value_states, past_key_value=past_key_value, attention_mask=attention_mask, layer_head_mask=layer_head_mask,
            output_attentions=output_attentions, cache_position=cache_position)
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self._shape(self.q_proj(hidden_states), tgt_len, bsz)
        if past_key_value is not None:
            is_updated = past_key_value.is_updated.get(self.layer_idx)
            if is_cross_attention:
                past_key_value.is_updated[self.layer_idx] = True
                past_key_value = past_key_value.cross_attention_cache
            else: past_key_value = past_key_value.self_attention_cache
        current_states = key_value_states if key_value_states is not None else hidden_states
        if is_cross_attention and past_key_value and is_updated:
            key_states = past_key_value.key_cache[self.layer_idx]
            value_states = past_key_value.value_cache[self.layer_idx]
        else:
            key_states = self._shape(self.k_proj(current_states), -1, bsz)
            value_states = self._shape(self.v_proj(current_states), -1, bsz)
            if past_key_value is not None:
                cache_position = cache_position if not is_cross_attention else None
                key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx, {"cache_position": cache_position})
        causal_mask = attention_mask
        if attention_mask is not None: causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
        is_causal = True if self.is_causal and causal_mask is None and tgt_len > 1 else False
        attn_output = torch.nn.functional.scaled_dot_product_attention(query_states, key_states, value_states, attn_mask=causal_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal)
        if attn_output.size() != (bsz, self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, None, past_key_value
QWEN2AUDIO_ATTENTION_CLASSES = {"eager": Qwen2AudioAttention, "flash_attention_2": Qwen2AudioFlashAttention2, "sdpa": Qwen2AudioSdpaAttention}
class Qwen2AudioEncoderLayer(nn.Module):
    def __init__(self, config: Qwen2AudioConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = QWEN2AUDIO_ATTENTION_CLASSES[config._attn_implementation](embed_dim=self.embed_dim, num_heads=config.encoder_attention_heads, dropout=config.attention_dropout, config=config)
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(self.embed_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, layer_head_mask: torch.Tensor, output_attentions: bool = False) -> torch.Tensor:
        residual = hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states, attn_weights, _ = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, layer_head_mask=layer_head_mask, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if hidden_states.dtype == torch.float16 and (torch.isinf(hidden_states).any() or torch.isnan(hidden_states).any()):
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
QWEN2AUDIO_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`Qwen2AudioConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@add_start_docstrings("The bare Qwen2Audio Model outputting raw hidden-states without any specific head on top.", QWEN2AUDIO_START_DOCSTRING)
class Qwen2AudioPreTrainedModel(PreTrainedModel):
    config_class = Qwen2AudioConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["Qwen2AudioAttention"]
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn_2 = True
    def _init_weights(self, module):
        std = self.config.init_std if hasattr(self.config, "init_std") else self.config.audio_config.init_std
        if isinstance(module, (nn.Linear, nn.Conv1d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
    @property
    def _supports_sdpa(self): return self.language_model._supports_sdpa
QWEN2AUDIOENCODER_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`Qwen2AudioEncoderConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@add_start_docstrings("The audio model from Qwen2Audio without any head or projection on top.", QWEN2AUDIOENCODER_START_DOCSTRING)
class Qwen2AudioEncoder(Qwen2AudioPreTrainedModel):
    config_class = Qwen2AudioEncoderConfig
    main_input_name = "input_features"
    _no_split_modules = ["Qwen2AudioEncoderLayer"]
    def __init__(self, config: Qwen2AudioEncoderConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layerdrop = config.encoder_layerdrop
        embed_dim = config.d_model
        self.num_mel_bins = config.num_mel_bins
        self.padding_idx = config.pad_token_id
        self.max_source_positions = config.max_source_positions
        self.embed_scale = math.sqrt(embed_dim) if config.scale_embedding else 1.0
        self.conv1 = nn.Conv1d(self.num_mel_bins, embed_dim, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(embed_dim, embed_dim, kernel_size=3, stride=2, padding=1)
        self.embed_positions = nn.Embedding(self.max_source_positions, embed_dim)
        self.embed_positions.requires_grad_(False)
        self.layers = nn.ModuleList([Qwen2AudioEncoderLayer(config) for _ in range(config.encoder_layers)])
        self.layer_norm = nn.LayerNorm(config.d_model)
        self.avg_pooler = nn.AvgPool1d(2, stride=2)
        self.gradient_checkpointing = False
        self.post_init()
    def _freeze_parameters(self):
        for param in self.parameters(): param.requires_grad = False
        self._requires_grad = False
    def get_input_embeddings(self) -> nn.Module: return self.conv1
    def set_input_embeddings(self, value: nn.Module): self.conv1 = value
    def forward(self, input_features, attention_mask=None, head_mask=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        expected_seq_length = self.config.max_source_positions * self.conv1.stride[0] * self.conv2.stride[0]
        if input_features.shape[-1] != expected_seq_length: raise ValueError(f"Qwen2Audio expects the mel input features to be of length {expected_seq_length}, but found {input_features.shape[-1]}. Make sure to pad the input mel features to {expected_seq_length}.")
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        input_features = input_features.to(dtype=self.conv1.weight.dtype, device=self.conv1.weight.device)
        inputs_embeds = nn.functional.gelu(self.conv1(input_features))
        inputs_embeds = nn.functional.gelu(self.conv2(inputs_embeds))
        inputs_embeds = inputs_embeds.permute(0, 2, 1)
        embed_pos = self.embed_positions.weight
        hidden_states = inputs_embeds + embed_pos
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        if head_mask is not None: assert head_mask.size()[0] == (len(self.layers)), f"The head_mask should be specified for {len(self.layers)} layers, but it is for {head_mask.size()[0]}."
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            to_drop = False
            if self.training:
                dropout_probability = torch.rand([])
                if dropout_probability < self.layerdrop: to_drop = True
            if to_drop: layer_outputs = (None, None)
            else:
                if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask,
                (head_mask[idx] if head_mask is not None else None), output_attentions)
                else: layer_outputs = encoder_layer(hidden_states, attention_mask, layer_head_mask=(head_mask[idx] if head_mask is not None else None), output_attentions=output_attentions)
                hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        hidden_states = hidden_states.permute(0, 2, 1)
        hidden_states = self.avg_pooler(hidden_states)
        hidden_states = hidden_states.permute(0, 2, 1)
        hidden_states = self.layer_norm(hidden_states)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
    def _get_feat_extract_output_lengths(self, input_lengths: torch.LongTensor):
        input_lengths = (input_lengths - 1) // 2 + 1
        output_lengths = (input_lengths - 2) // 2 + 1
        return input_lengths, output_lengths
class Qwen2AudioMultiModalProjector(nn.Module):
    def __init__(self, config: Qwen2AudioConfig):
        super().__init__()
        self.linear = nn.Linear(config.audio_config.d_model, config.text_config.hidden_size, bias=True)
    def forward(self, audio_features):
        hidden_states = self.linear(audio_features)
        return hidden_states
QWEN2AUDIO_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        input_features (`torch.FloatTensor` of shape `(batch_size, feature_size, feature_sequence_length)`):
            Float values mel features extracted from the raw speech waveform. Raw speech waveform can be obtained by
            loading a `.flac` or `.wav` audio file into an array of type `List[float]` or a `numpy.ndarray`, *e.g.* via
            the soundfile library (`pip install soundfile`). To prepare the array into `input_features`, the
            [`AutoFeatureExtractor`] should be used for extracting the mel features, padding and conversion into a
            tensor of type `torch.FloatTensor`. See [`~WhisperFeatureExtractor.__call__`]
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `decoder_input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        feature_attention_mask (`torch.Tensor` of shape `(batch_size, feature_sequence_length)`):
            Mask to avoid performing attention on padding feature indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`. [What are position IDs?](../glossary#position-ids)
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)` and 2 additional tensors of shape
            `(batch_size, num_heads, encoder_sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used (see `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
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
@add_start_docstrings("The QWEN2AUDIO model which consists of a audio backbone and a language model.", QWEN2AUDIO_START_DOCSTRING)
class Qwen2AudioForConditionalGeneration(Qwen2AudioPreTrainedModel, GenerationMixin):
    def __init__(self, config: Qwen2AudioConfig):
        super().__init__(config)
        self.audio_tower = AutoModel.from_config(config.audio_config, attn_implementation=config._attn_implementation)
        self.multi_modal_projector = Qwen2AudioMultiModalProjector(config)
        self.vocab_size = config.text_config.vocab_size
        self.language_model = AutoModelForCausalLM.from_config(config.text_config, attn_implementation=config._attn_implementation)
        self.pad_token_id = self.config.pad_token_id if self.config.pad_token_id is not None else -1
        self._padding_side = "left"
        self.post_init()
    @property
    def padding_side(self): return self._padding_side
    @padding_side.setter
    def padding_side(self, padding_side: str):
        if padding_side not in ["left", "right"]: raise ValueError(f"{padding_side} is not `left` or `right`.")
        self._padding_side = padding_side
    def get_input_embeddings(self): return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.language_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.language_model.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.language_model.set_output_embeddings(new_embeddings)
    def set_decoder(self, decoder): self.language_model.set_decoder(decoder)
    def get_decoder(self): return self.language_model.get_decoder()
    def tie_weights(self): return self.language_model.tie_weights()
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of=None) -> nn.Embedding:
        model_embeds = self.language_model.resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        self.config.text_config.vocab_size = model_embeds.num_embeddings
        self.vocab_size = model_embeds.num_embeddings
        return model_embeds
    def _merge_input_ids_with_audio_features(self, audio_features, num_audio_tokens, inputs_embeds, input_ids, attention_mask, labels):
        num_audios, max_audio_tokens, embed_dim = audio_features.shape
        audio_features_mask = torch.arange(max_audio_tokens).expand(num_audios, max_audio_tokens).to(num_audio_tokens.device) < num_audio_tokens.unsqueeze(1)
        masked_audio_features = audio_features[audio_features_mask].view(-1, embed_dim)
        batch_size, sequence_length = input_ids.shape
        _left_padding = torch.any(attention_mask[:, 0] == 0)
        _right_padding = torch.any(attention_mask[:, -1] == 0)
        left_padding = True
        if batch_size > 1:
            if _left_padding and not _right_padding: left_padding = True
            elif not _left_padding and _right_padding: left_padding = False
            elif not _left_padding and not _right_padding: left_padding = self.padding_side == "left"
            else: raise ValueError(f"both side of attention_mask has zero, invalid. {attention_mask}")
        special_audio_token_mask = input_ids == self.config.audio_token_index
        num_special_audio_tokens = torch.sum(special_audio_token_mask, dim=-1)
        target_device = inputs_embeds.device
        attention_mask = attention_mask.to(target_device)
        input_ids = input_ids.to(target_device)
        num_audio_tokens = num_audio_tokens.to(target_device)
        batch_indices, non_audio_indices = torch.where((input_ids != self.config.audio_token_index) & (attention_mask == 1))
        token_placeholder_num = torch.zeros_like(input_ids)
        token_placeholder_num[special_audio_token_mask] = num_audio_tokens.long() - 1
        token_placeholder_num = token_placeholder_num + 1
        new_token_positions = torch.cumsum(token_placeholder_num, -1) - 1
        max_token_num = token_placeholder_num.sum(-1).max()
        nb_audio_pad = max_token_num - 1 - new_token_positions[:, -1]
        if left_padding: new_token_positions += nb_audio_pad[:, None]
        text_to_overwrite = new_token_positions[batch_indices, non_audio_indices]
        batch_indices, non_audio_indices, text_to_overwrite = (batch_indices.to(target_device), non_audio_indices.to(target_device), text_to_overwrite.to(target_device))
        final_embedding = torch.zeros(batch_size, max_token_num, embed_dim, dtype=inputs_embeds.dtype, device=inputs_embeds.device)
        final_attention_mask = torch.zeros(batch_size, max_token_num, dtype=attention_mask.dtype, device=inputs_embeds.device)
        final_input_ids = torch.full((batch_size, max_token_num), self.pad_token_id, dtype=input_ids.dtype, device=inputs_embeds.device)
        final_embedding[batch_indices, text_to_overwrite] = inputs_embeds[batch_indices, non_audio_indices]
        final_attention_mask[batch_indices, text_to_overwrite] = attention_mask[batch_indices, non_audio_indices]
        final_input_ids[batch_indices, text_to_overwrite] = input_ids[batch_indices, non_audio_indices]
        final_labels = None
        if labels is not None:
            labels = labels.to(target_device)
            final_labels = torch.full_like(final_attention_mask, self.config.ignore_index).to(torch.long)
            final_labels[batch_indices, text_to_overwrite] = labels[batch_indices, non_audio_indices]
        audio_to_overwrite = torch.full((batch_size, max_token_num), True, dtype=torch.bool, device=inputs_embeds.device)
        audio_to_overwrite[batch_indices, text_to_overwrite] = False
        seq_indices = torch.arange(max_token_num).unsqueeze(0).to(target_device)
        seq_indices = seq_indices.expand(batch_size, max_token_num)
        if left_padding:
            max_token_num = max_token_num.to(target_device)
            val = (max_token_num - seq_indices) <= (token_placeholder_num.sum(-1) - (attention_mask == 0).long().sum(-1))[:, None]
        else: val = seq_indices < (token_placeholder_num.sum(-1) - (attention_mask == 0).long().sum(-1))[:, None]
        audio_to_overwrite &= val
        if audio_to_overwrite.sum() != num_audio_tokens.sum(): raise ValueError(f"The input provided to the model are wrong. The number of audio tokens is {num_special_audio_tokens} while the number of audio given to the model is {num_audios}. This prevents correct indexing and breaks batch generation.")
        final_embedding[audio_to_overwrite] = (masked_audio_features.contiguous().reshape(-1, embed_dim).to(target_device))
        final_attention_mask |= audio_to_overwrite
        position_ids = (final_attention_mask.cumsum(-1) - 1).masked_fill_((final_attention_mask == 0), 1)
        return final_embedding, final_attention_mask, final_labels, position_ids, final_input_ids
    @add_start_docstrings_to_model_forward(QWEN2AUDIO_INPUTS_DOCSTRING)
    def forward(self, input_ids: torch.LongTensor = None, input_features: torch.FloatTensor = None, attention_mask: Optional[torch.Tensor] = None, feature_attention_mask: Optional[torch.Tensor] = None,
    position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, Qwen2AudioCausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        target_device = self.audio_tower.device
        if input_features is not None:
            input_features = input_features.to(target_device)
            feature_attention_mask = feature_attention_mask.to(target_device)
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
            if input_features is not None and input_ids.shape[1] != 1:
                audio_feat_lengths, audio_output_lengths = self.audio_tower._get_feat_extract_output_lengths(feature_attention_mask.sum(-1))
                batch_size, _, max_mel_seq_len = input_features.shape
                max_seq_len = (max_mel_seq_len - 2) // 2 + 1
                seq_range = (torch.arange(0, max_seq_len, dtype=audio_feat_lengths.dtype, device=audio_feat_lengths.device).unsqueeze(0).expand(batch_size, max_seq_len))
                lengths_expand = audio_feat_lengths.unsqueeze(1).expand(batch_size, max_seq_len)
                padding_mask = seq_range >= lengths_expand
                audio_attention_mask_ = padding_mask.view(batch_size, 1, 1, max_seq_len).expand(batch_size, 1, max_seq_len, max_seq_len)
                audio_attention_mask = audio_attention_mask_.to(dtype=self.audio_tower.conv1.weight.dtype, device=self.audio_tower.conv1.weight.device)
                audio_attention_mask[audio_attention_mask_] = float("-inf")
                audio_outputs = self.audio_tower(input_features, attention_mask=audio_attention_mask)
                selected_audio_feature = audio_outputs.last_hidden_state
                audio_features = self.multi_modal_projector(selected_audio_feature)
                inputs_embeds, attention_mask, labels, position_ids, _ = self._merge_input_ids_with_audio_features(audio_features, audio_output_lengths, inputs_embeds, input_ids, attention_mask, labels)
        outputs = self.language_model(attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits = outputs[0]
        loss = None
        if labels is not None:
            if attention_mask is not None:
                shift_attention_mask = attention_mask[..., 1:]
                shift_logits = logits[..., :-1, :][shift_attention_mask.to(logits.device) != 0].contiguous()
                shift_labels = labels[..., 1:][shift_attention_mask.to(labels.device) != 0].contiguous()
            else:
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return Qwen2AudioCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions, attention_mask=attention_mask)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, input_features=None, attention_mask=None, **kwargs):
        if past_key_values is not None:
            if isinstance(past_key_values, Cache):
                cache_length = past_key_values.get_seq_length()
                past_length = past_key_values.seen_tokens
            else: cache_length = past_length = past_key_values[0][0].shape[2]
            if input_features is not None and kwargs.get("attention_mask") is not None:
                attention_mask = kwargs["attention_mask"]
                attention_mask = torch.cat([attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1)
            if attention_mask is not None and attention_mask.shape[1] > input_ids.shape[1]: input_ids = input_ids[:, -(attention_mask.shape[1] - past_length) :]
            elif past_length < input_ids.shape[1]: input_ids = input_ids[:, past_length:]
            elif self.config.audio_token_index in input_ids: input_ids = input_ids[:, input_ids.shape[1] - 1 :]
            if cache_length < past_length and attention_mask is not None: attention_mask = attention_mask[:, -(cache_length + input_ids.shape[1]) :]
        position_ids = kwargs.get("position_ids", None)
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :]
        if inputs_embeds is not None and past_key_values is None: model_inputs = {"inputs_embeds": inputs_embeds}
        else: model_inputs = {"input_ids": input_ids}
        feature_attention_mask = kwargs.get("feature_attention_mask", None)
        model_inputs.update({"position_ids": position_ids, "past_key_values": past_key_values, "use_cache": kwargs.get("use_cache"), "attention_mask": attention_mask,
        "input_features": input_features, "feature_attention_mask": feature_attention_mask})
        return model_inputs
    def _update_model_kwargs_for_generation(self, outputs: ModelOutput, model_kwargs: Dict[str, Any], is_encoder_decoder: bool = False, num_new_tokens: int = 1) -> Dict[str, Any]:
        cache_name, cache = self._extract_past_from_model_output(outputs)
        model_kwargs[cache_name] = cache
        if getattr(outputs, "state", None) is not None: model_kwargs["state"] = outputs.state
        if getattr(outputs, "attention_mask", None) is not None: model_kwargs["attention_mask"] = outputs.attention_mask
        if "token_type_ids" in model_kwargs:
            token_type_ids = model_kwargs["token_type_ids"]
            model_kwargs["token_type_ids"] = torch.cat([token_type_ids, token_type_ids[:, -1].unsqueeze(-1)], dim=-1)
        if not is_encoder_decoder:
            if "attention_mask" in model_kwargs:
                attention_mask = model_kwargs["attention_mask"]
                model_kwargs["attention_mask"] = torch.cat([attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1)
        else:
            if "decoder_attention_mask" in model_kwargs:
                decoder_attention_mask = model_kwargs["decoder_attention_mask"]
                model_kwargs["decoder_attention_mask"] = torch.cat([decoder_attention_mask, decoder_attention_mask.new_ones((decoder_attention_mask.shape[0], 1))], dim=-1)
        if model_kwargs.get("use_cache", True): model_kwargs["cache_position"] = model_kwargs["cache_position"][-1:] + num_new_tokens
        else:
            past_positions = model_kwargs.pop("cache_position")
            new_positions = torch.arange(past_positions[-1] + 1, past_positions[-1] + num_new_tokens + 1, dtype=past_positions.dtype).to(past_positions.device)
            model_kwargs["cache_position"] = torch.cat((past_positions, new_positions))
        return model_kwargs
    def _reorder_cache(self, *args, **kwargs): return self.language_model._reorder_cache(*args, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
