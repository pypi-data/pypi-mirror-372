"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...cache_utils import Cache, DynamicCache
from ...generation import GenerationMixin
from ...modeling_attn_mask_utils import _prepare_4d_attention_mask
from ...modeling_outputs import BaseModelOutput, ModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, is_flash_attn_2_available, is_flash_attn_greater_or_equal_2_10, is_torchdynamo_compiling,
logging, replace_return_docstrings)
from ..auto import AutoModel
from .configuration_idefics2 import Idefics2Config, Idefics2VisionConfig
if is_flash_attn_2_available(): from ...modeling_flash_attention_utils import _flash_attention_forward
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "Idefics2Config"
@dataclass
class Idefics2BaseModelOutputWithPast(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    image_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class Idefics2CausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    past_key_values: Optional[List[torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    image_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class Idefics2VisionEmbeddings(nn.Module):
    def __init__(self, config: Idefics2VisionConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.patch_embedding = nn.Conv2d(in_channels=config.num_channels, out_channels=self.embed_dim, kernel_size=self.patch_size, stride=self.patch_size, padding="valid")
        self.num_patches_per_side = self.image_size // self.patch_size
        self.num_patches = self.num_patches_per_side**2
        self.num_positions = self.num_patches
        self.position_embedding = nn.Embedding(self.num_positions, self.embed_dim)
    def forward(self, pixel_values: torch.FloatTensor, patch_attention_mask: torch.BoolTensor) -> torch.Tensor:
        batch_size, _, max_im_h, max_im_w = pixel_values.shape
        patch_embeds = self.patch_embedding(pixel_values)
        embeddings = patch_embeds.flatten(2).transpose(1, 2)
        max_nb_patches_h, max_nb_patches_w = max_im_h // self.patch_size, max_im_w // self.patch_size
        boundaries = torch.arange(1 / self.num_patches_per_side, 1.0, 1 / self.num_patches_per_side)
        position_ids = torch.full(size=(batch_size, max_nb_patches_h * max_nb_patches_w), fill_value=0)
        for batch_idx, p_attn_mask in enumerate(patch_attention_mask):
            nb_patches_h = p_attn_mask[:, 0].sum()
            nb_patches_w = p_attn_mask[0].sum()
            fractional_coords_h = torch.arange(0, 1 - 1e-6, 1 / nb_patches_h)
            fractional_coords_w = torch.arange(0, 1 - 1e-6, 1 / nb_patches_w)
            bucket_coords_h = torch.bucketize(fractional_coords_h, boundaries, right=True)
            bucket_coords_w = torch.bucketize(fractional_coords_w, boundaries, right=True)
            pos_ids = (bucket_coords_h[:, None] * self.num_patches_per_side + bucket_coords_w).flatten()
            position_ids[batch_idx][p_attn_mask.view(-1).cpu()] = pos_ids
        position_ids = position_ids.to(self.position_embedding.weight.device)
        embeddings = embeddings + self.position_embedding(position_ids)
        return embeddings
class Idefics2VisionAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        if self.head_dim * self.num_heads != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.scale = self.head_dim**-0.5
        self.dropout = config.attention_dropout
        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.is_causal = False
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(batch_size, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(batch_size, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(batch_size, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        k_v_seq_len = key_states.shape[-2]
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) * self.scale
        if attn_weights.size() != (batch_size, self.num_heads, q_len, k_v_seq_len): raise ValueError(f"Attention weights should be of size {(batch_size, self.num_heads, q_len, k_v_seq_len)}, but is {attn_weights.size()}")
        if attention_mask is not None:
            if attention_mask.size() != (batch_size, 1, q_len, k_v_seq_len): raise ValueError(f"Attention mask should be of size {(batch_size, 1, q_len, k_v_seq_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights + attention_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_weights = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.matmul(attn_weights, value_states)
        if attn_output.size() != (batch_size, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(batch_size, self.num_heads, q_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(batch_size, q_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights
class Idefics2VisionFlashAttention2(Idefics2VisionAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Cache] = None,
    output_attentions: bool = False, use_cache: bool = False, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        output_attentions = False
        bsz, q_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim)
        key_states = key_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        kv_seq_len = key_states.shape[-2]
        if past_key_value is not None: kv_seq_len += past_key_value.get_usable_length(kv_seq_len, self.layer_idx)
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)
        dropout_rate = self.dropout if self.training else 0.0
        input_dtype = query_states.dtype
        if input_dtype == torch.float32:
            if torch.is_autocast_enabled(): target_dtype = torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            logger.warning_once(f"The input hidden states seems to be silently casted in float32, this might be related to the fact you have upcasted embedding or layer norm layers in float32. We will cast back the input in {target_dtype}.")
            query_states = query_states.to(target_dtype)
            key_states = key_states.to(target_dtype)
            value_states = value_states.to(target_dtype)
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, dropout=dropout_rate, is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        attn_output = attn_output.reshape(bsz, q_len, self.embed_dim).contiguous()
        attn_output = self.out_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights
IDEFICS_VISION_ATTENTION_CLASSES = {"eager": Idefics2VisionAttention, "flash_attention_2": Idefics2VisionFlashAttention2}
class Idefics2VisionMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.activation_fn = ACT2FN[config.hidden_act]
        self.fc1 = nn.Linear(config.hidden_size, config.intermediate_size)
        self.fc2 = nn.Linear(config.intermediate_size, config.hidden_size)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        return hidden_states
class Idefics2MLP(nn.Module):
    def __init__(self, hidden_size: int, intermediate_size: int, output_size: int, hidden_act: str):
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, output_size, bias=False)
        self.act_fn = ACT2FN[hidden_act]
    def forward(self, x): return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))
class Idefics2MultiheadAttentionPoolingHead(nn.Module):
    def __init__(self, config: Idefics2VisionConfig):
        super().__init__()
        self.probe = nn.Parameter(torch.randn(1, 1, config.hidden_size))
        self.attention = torch.nn.MultiheadAttention(config.hidden_size, config.num_attention_heads, batch_first=True)
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.mlp = Idefics2MLP(hidden_size=config.hidden_size, intermediate_size=config.intermediate_size, hidden_act=config.hidden_act, output_size=config.hidden_size)
    def forward(self, hidden_state):
        batch_size = hidden_state.shape[0]
        probe = self.probe.repeat(batch_size, 1, 1)
        hidden_state = self.attention(probe, hidden_state, hidden_state)[0]
        residual = hidden_state
        hidden_state = self.layernorm(hidden_state)
        hidden_state = residual + self.mlp(hidden_state)
        return hidden_state[:, 0]
class Idefics2EncoderLayer(nn.Module):
    def __init__(self, config: Idefics2VisionConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.self_attn = IDEFICS_VISION_ATTENTION_CLASSES[config._attn_implementation](config)
        self.layer_norm1 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
        self.mlp = Idefics2VisionMLP(config)
        self.layer_norm2 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, output_attentions: Optional[bool] = False) -> Tuple[torch.FloatTensor]:
        residual = hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, output_attentions=output_attentions)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class Idefics2Encoder(nn.Module):
    def __init__(self, config: Idefics2Config):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([Idefics2EncoderLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, inputs_embeds, attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        hidden_states = inputs_embeds
        for encoder_layer in self.layers:
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask, output_attentions)
            else: layer_outputs = encoder_layer(hidden_states, attention_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class Idefics2VisionTransformer(nn.Module):
    def __init__(self, config: Idefics2VisionConfig):
        super().__init__()
        embed_dim = config.hidden_size
        self.config = config
        self.embeddings = Idefics2VisionEmbeddings(config)
        self.encoder = Idefics2Encoder(config)
        self.post_layernorm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
    def get_input_embeddings(self): return self.embeddings
    def set_input_embeddings(self, value): self.embeddings = value
    def forward(self, pixel_values, patch_attention_mask: Optional[torch.BoolTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size = pixel_values.size(0)
        if patch_attention_mask is None:
            patch_size = self.config.patch_size
            patch_attention_mask = torch.ones((batch_size, pixel_values.size(2) // patch_size, pixel_values.size(3) // patch_size,))
            patch_attention_mask = patch_attention_mask.to(dtype=torch.bool, device=pixel_values.device)
        hidden_states = self.embeddings(pixel_values=pixel_values, patch_attention_mask=patch_attention_mask)
        patch_attention_mask = patch_attention_mask.view(batch_size, -1)
        if not torch.any(~patch_attention_mask): patch_attention_mask = None
        elif not self._use_flash_attention_2: patch_attention_mask = _prepare_4d_attention_mask(patch_attention_mask, hidden_states.dtype)
        encoder_outputs = self.encoder(inputs_embeds=hidden_states, attention_mask=patch_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        last_hidden_state = self.post_layernorm(last_hidden_state)
        if not return_dict: return (last_hidden_state,) + encoder_outputs[1:]
        return BaseModelOutput(last_hidden_state=last_hidden_state, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1: return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
class Idefics2RMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps
    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)
    def extra_repr(self): return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"
class Idefics2PerceiverAttention(nn.Module):
    def __init__(self, config, layer_idx: Optional[int] = None) -> None:
        super().__init__()
        self.layer_idx = None
        self.hidden_size = config.text_config.hidden_size
        self.num_heads = config.perceiver_config.resampler_n_heads
        self.head_dim = config.perceiver_config.resampler_head_dim
        self.num_key_value_heads = config.perceiver_config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.attention_dropout = config.perceiver_config.attention_dropout
        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)
        self.is_causal = False
    def forward(self, latents: torch.Tensor, context: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: bool = False, use_cache: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        bsz, q_len, _ = latents.size()
        kv_seq_len = q_len + context.size()[1]
        hidden_states = torch.concat([context, latents], dim=-2)
        query_states = self.q_proj(latents)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, kv_seq_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, kv_seq_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        past_key_value = getattr(self, "past_key_value", past_key_value)
        if past_key_value is not None: key_states, value_states = past_key_value.update(key_states, value_states, self.layer_idx)
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)
        if attn_weights.size() != (bsz, self.num_heads, q_len, kv_seq_len): raise ValueError(f"Attention weights should be of size {(bsz, self.num_heads, q_len, kv_seq_len)}, but is {attn_weights.size()}")
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, q_len, kv_seq_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, q_len, kv_seq_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights + attention_mask
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_output = torch.matmul(attn_weights, value_states)
        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(bsz, q_len, self.num_heads * self.head_dim)
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
class Idefics2PerceiverFlashAttention2(Idefics2PerceiverAttention):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flash_attn_uses_top_left_mask = not is_flash_attn_greater_or_equal_2_10()
    def forward(self, latents: torch.Tensor, context: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_value: Optional[Cache] = None, output_attentions: bool = False, use_cache: bool = False, **kwargs) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        bsz, q_len, _ = latents.size()
        kv_seq_len = q_len + context.size()[1]
        query_states = self.q_proj(latents)
        key_states = self.k_proj(torch.cat([context, latents], dim=-2))
        value_states = self.v_proj(torch.cat([context, latents], dim=-2))
        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim)
        key_states = key_states.view(bsz, kv_seq_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, kv_seq_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        kv_seq_len = key_states.shape[-2]
        if past_key_value is not None: kv_seq_len += past_key_value[0].shape[-2]
        if past_key_value is not None:
            if hasattr(self.config, "sliding_window") and kv_seq_len > self.config.sliding_window:
                slicing_tokens = kv_seq_len - self.config.sliding_window
                past_key = past_key_value[0]
                past_value = past_key_value[1]
                past_key = past_key[:, :, slicing_tokens:, :].contiguous()
                past_value = past_value[:, :, slicing_tokens:, :].contiguous()
                if past_key.shape[-2] != self.config.sliding_window - 1: raise ValueError(f"past key must have a shape of (`batch_size, num_heads, self.config.sliding_window-1, head_dim`), got {past_key.shape}")
                past_key_value = (past_key, past_value)
                if attention_mask is not None:
                    attention_mask = attention_mask[:, slicing_tokens:]
                    attention_mask = torch.cat([attention_mask, torch.ones_like(attention_mask[:, -1:])], dim=-1)
            key_states = torch.cat([past_key_value[0], key_states], dim=2)
            value_states = torch.cat([past_key_value[1], value_states], dim=2)
        past_key_value = (key_states, value_states) if use_cache else None
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)
        dropout_rate = 0.0 if not self.training else self.attention_dropout
        input_dtype = query_states.dtype
        if input_dtype == torch.float32:
            if torch.is_autocast_enabled(): target_dtype = torch.get_autocast_gpu_dtype()
            elif hasattr(self.config, "_pre_quantization_dtype"): target_dtype = self.config._pre_quantization_dtype
            else: target_dtype = self.q_proj.weight.dtype
            logger.warning_once(f"The input hidden states seems to be silently casted in float32, this might be related to the fact you have upcasted embedding or layer norm layers in float32. We will cast back the input in {target_dtype}.")
            query_states = query_states.to(target_dtype)
            key_states = key_states.to(target_dtype)
            value_states = value_states.to(target_dtype)
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)
        attn_output = _flash_attention_forward(query_states, key_states, value_states, attention_mask, q_len, dropout=dropout_rate, sliding_window=None, is_causal=self.is_causal, use_top_left_mask=self._flash_attn_uses_top_left_mask)
        attn_output = attn_output.reshape(bsz, q_len, self.num_heads * self.head_dim).contiguous()
        attn_output = self.o_proj(attn_output)
        if not output_attentions: attn_weights = None
        return attn_output, attn_weights, past_key_value
IDEFICS2_PERCEIVER_ATTENTION_CLASSES = {"eager": Idefics2PerceiverAttention, "flash_attention_2": Idefics2PerceiverFlashAttention2}
class Idefics2PerceiverLayer(nn.Module):
    def __init__(self, config, layer_idx: int):
        super().__init__()
        self.hidden_size = config.text_config.hidden_size
        self.n_latents = config.perceiver_config.resampler_n_latents
        self.depth = config.perceiver_config.resampler_depth
        self.rms_norm_eps = config.text_config.rms_norm_eps
        self.input_latents_norm = Idefics2RMSNorm(self.hidden_size, eps=self.rms_norm_eps)
        self.input_context_norm = Idefics2RMSNorm(self.hidden_size, eps=self.rms_norm_eps)
        self.self_attn = IDEFICS2_PERCEIVER_ATTENTION_CLASSES[config._attn_implementation](config, layer_idx=layer_idx)
        self.post_attention_layernorm = Idefics2RMSNorm(self.hidden_size, eps=self.rms_norm_eps)
        self.mlp = Idefics2MLP(hidden_size=config.text_config.hidden_size, intermediate_size=config.text_config.hidden_size * 4, output_size=config.text_config.hidden_size, hidden_act=config.perceiver_config.hidden_act)
    def forward(self, latents: torch.Tensor, context: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None,
    output_attentions: Optional[bool] = False, use_cache: Optional[bool] = False, **kwargs) -> Tuple[torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]]:
        residual = latents
        latents = self.input_latents_norm(latents)
        context = self.input_context_norm(context)
        latents, self_attn_weights, present_key_value = self.self_attn(latents=latents, context=context, attention_mask=attention_mask)
        latents = residual + latents
        residual = latents
        latents = self.post_attention_layernorm(latents)
        latents = self.mlp(latents)
        latents = residual + latents
        outputs = (latents,)
        if output_attentions: outputs += (self_attn_weights,)
        if use_cache: outputs += (present_key_value,)
        return outputs
class Idefics2PerceiverResampler(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.hidden_size = config.text_config.hidden_size
        self.hidden_act = config.perceiver_config.hidden_act
        self.n_latents = config.perceiver_config.resampler_n_latents
        self.depth = config.perceiver_config.resampler_depth
        self.rms_norm_eps = config.text_config.rms_norm_eps
        self.latents = nn.Parameter(torch.ones(self.n_latents, self.hidden_size))
        self.layers = nn.ModuleList([Idefics2PerceiverLayer(config, idx) for idx in range(self.depth)])
        self.norm = Idefics2RMSNorm(self.hidden_size, eps=self.rms_norm_eps)
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
    def forward(self, context: torch.Tensor, attention_mask) -> torch.Tensor:
        latents = self.latents.unsqueeze(0).expand((context.shape[0], *self.latents.size()))
        latent_attention_mask = torch.ones((attention_mask.size(0), latents.size(1)), dtype=attention_mask.dtype, device=attention_mask.device)
        attention_mask = torch.cat([attention_mask, latent_attention_mask], dim=-1)
        attention_mask = (_prepare_4d_attention_mask(attention_mask, latents.dtype, tgt_len=self.n_latents) if not self._use_flash_attention_2 else attention_mask)
        compressed_context = latents
        for perceiver_layer in self.layers:
            layer_outputs = perceiver_layer(compressed_context, context, attention_mask=attention_mask, position_ids=None, past_key_value=None, output_attentions=False, use_cache=False)
            compressed_context = layer_outputs[0]
        compressed_context = self.norm(compressed_context)
        return compressed_context
class Idefics2Connector(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.modality_projection = Idefics2MLP(hidden_size=config.vision_config.hidden_size, intermediate_size=config.text_config.intermediate_size, output_size=config.text_config.hidden_size, hidden_act=config.text_config.hidden_act)
        self.perceiver_resampler = Idefics2PerceiverResampler(config)
    def forward(self, image_hidden_states, attention_mask):
        image_hidden_states = self.modality_projection(image_hidden_states)
        image_hidden_states = self.perceiver_resampler(context=image_hidden_states, attention_mask=attention_mask)
        return image_hidden_states
IDEFICS2_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`Idefics2Config`] or [`Idefics2VisionConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights."""
@add_start_docstrings("The bare Idefics2 Model outputting raw hidden-states without any specific head on top.", IDEFICS2_START_DOCSTRING)
class Idefics2PreTrainedModel(PreTrainedModel):
    config_class = Idefics2Config
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["Idefics2VisionAttention", "Idefics2MLP", "Idefics2PerceiverLayer", "Idefics2DecoderLayer"]
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn_2 = True
    _supports_cache_class = True
    def _init_weights(self, module):
        std = (self.config.text_config.initializer_range if hasattr(self.config, "initializer_range") else self.config.text_config.initializer_range)
        if hasattr(module, "class_embedding"): module.class_embedding.data.normal_(mean=0.0, std=std)
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
    @classmethod
    def _autoset_attn_implementation(cls, config, use_flash_attention_2: bool = False, torch_dtype: Optional[torch.dtype] = None, device_map: Optional[Union[str, Dict[str, int]]] = None, check_device_map: bool = True, **kwargs):
        config = super()._autoset_attn_implementation(config=config, use_flash_attention_2=use_flash_attention_2, torch_dtype=torch_dtype, device_map=device_map, check_device_map=check_device_map, **kwargs)
        config.vision_config._attn_implementation = config._attn_implementation
        return config
IDEFICS2_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
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
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`CLIPImageProcessor.__call__`] for details ([]`LlavaProcessor`] uses
            [`CLIPImageProcessor`] for processing images).
        pixel_attention_mask (`torch.Tensor` of shape `(batch_size, image_size, image_size)`, *optional*):
            Mask to avoid performing attention on padding pixel indices.
        image_hidden_states (`torch.FloatTensor` of shape `(batch_size, num_channels, image_size, image_size)`):
            The hidden states of the image encoder after modality projection and perceiver resampling.
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
@add_start_docstrings("Idefics2 model consisting of a SIGLIP vision encoder and Mistral language decoder", IDEFICS2_START_DOCSTRING)
class Idefics2Model(Idefics2PreTrainedModel):
    def __init__(self, config: Idefics2Config):
        super().__init__(config)
        self.padding_idx = self.config.text_config.pad_token_id
        self.vocab_size = self.config.text_config.vocab_size
        self.vision_model = Idefics2VisionTransformer(config.vision_config)
        self.connector = Idefics2Connector(config)
        self.text_model = AutoModel.from_config(config.text_config, attn_implementation=config._attn_implementation)
        self.image_seq_len = config.perceiver_config.resampler_n_latents
        self.image_token_id = self.config.image_token_id
        self._use_flash_attention_2 = config._attn_implementation == "flash_attention_2"
        self.post_init()
    def enable_input_require_grads(self):
        def get_lowest_module(module):
            if len(list(module.children())) == 0: return module
            else: return get_lowest_module(list(module.children())[0])
        def make_inputs_require_grads(module, input, output): output.requires_grad_(True)
        self._text_require_grads_hook = self.get_input_embeddings().register_forward_hook(make_inputs_require_grads)
        self._vision_require_grads_hook = get_lowest_module(self.vision_model).register_forward_hook(make_inputs_require_grads)
    def disable_input_require_grads(self):
        self._text_require_grads_hook.remove()
        self._vision_require_grads_hook.remove()
    def get_input_embeddings(self): return self.text_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.text_model.set_input_embeddings(value)
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of=None) -> nn.Embedding:
        model_embeds = self.text_model.resize_token_embeddings(new_num_tokens=new_num_tokens, pad_to_multiple_of=pad_to_multiple_of)
        self.config.text_config.vocab_size = model_embeds.num_embeddings
        return model_embeds
    def inputs_merger(self, input_ids: torch.LongTensor, inputs_embeds: Optional[torch.Tensor], image_hidden_states: Optional[torch.Tensor]):
        num_images, _, vision_hidden_size = image_hidden_states.shape
        special_image_token_mask = input_ids == self.image_token_id
        new_inputs_embeds = inputs_embeds.clone()
        reshaped_image_hidden_states = image_hidden_states.view(-1, vision_hidden_size)
        new_inputs_embeds[special_image_token_mask] = reshaped_image_hidden_states
        return new_inputs_embeds
    @add_start_docstrings_to_model_forward("""
        Inputs fed to the model can have an arbitrary number of images. To account for this, pixel_values fed to
        the model have image padding -> (batch_size, max_num_images, 3, max_heights, max_widths) where
        max_num_images is the maximum number of images among the batch_size samples in the batch.
        Padding images are not needed beyond padding the pixel_values at the entrance of the model.
        For efficiency, we only pass through the vision_model's forward the real images by
        discarding the padding images i.e. pixel_values of size (image_batch_size, 3, height, width) where
        image_batch_size would be 7 when num_images_per_sample=[1, 3, 1, 2] and max_num_images would be 3.
        """, IDEFICS2_INPUTS_DOCSTRING)
    def forward(self, input_ids: torch.LongTensor = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, pixel_attention_mask: Optional[torch.BoolTensor] = None, image_hidden_states: Optional[torch.FloatTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, Idefics2BaseModelOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if self.training and self.text_model.gradient_checkpointing and use_cache:
            logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...")
            use_cache = False
        if input_ids is not None: batch_size, seq_length = input_ids.shape
        elif inputs_embeds is not None: batch_size, seq_length, _ = inputs_embeds.shape
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        past_seen_tokens = 0
        return_legacy_cache = False
        if use_cache:
            if not isinstance(past_key_values, Cache):
                return_legacy_cache = True
                if past_key_values is None: past_key_values = DynamicCache()
                else:
                    past_key_values = DynamicCache.from_legacy_cache(past_key_values)
                    logger.warning_once("We detected that you are passing `past_key_values` as a tuple of tuples. This is deprecated and will be removed in v1.0.")
            past_seen_tokens = past_key_values.get_seq_length()
        if inputs_embeds is not None and input_ids is None and past_seen_tokens == 0: raise ValueError("When first calling the model, if input_embeds are passed, input_ids should not be None.")
        if inputs_embeds is None: inputs_embeds = self.text_model.get_input_embeddings()(input_ids)
        if pixel_values is not None and image_hidden_states is not None: raise ValueError("You cannot specify both pixel_values and image_hidden_states at the same time")
        elif pixel_values is not None:
            batch_size, num_images, num_channels, height, width = pixel_values.shape
            pixel_values = pixel_values.to(dtype=self.dtype)
            pixel_values = pixel_values.view(batch_size * num_images, *pixel_values.shape[2:])
            nb_values_per_image = pixel_values.shape[1:].numel()
            real_images_inds = (pixel_values == 0.0).sum(dim=(-1, -2, -3)) != nb_values_per_image
            pixel_values = pixel_values[real_images_inds].contiguous()
            if pixel_attention_mask is None: pixel_attention_mask = torch.ones(size=(pixel_values.size(0), pixel_values.size(2), pixel_values.size(3)), dtype=torch.bool, device=pixel_values.device)
            else:
                pixel_attention_mask = pixel_attention_mask.view(batch_size * num_images, *pixel_attention_mask.shape[2:])
                pixel_attention_mask = pixel_attention_mask[real_images_inds].contiguous()
            patch_size = self.config.vision_config.patch_size
            patches_subgrid = pixel_attention_mask.unfold(dimension=1, size=patch_size, step=patch_size)
            patches_subgrid = patches_subgrid.unfold(dimension=2, size=patch_size, step=patch_size)
            patch_attention_mask = (patches_subgrid.sum(dim=(-1, -2)) == patch_size * patch_size).bool()
            image_hidden_states = self.vision_model(pixel_values=pixel_values, patch_attention_mask=patch_attention_mask).last_hidden_state
            image_hidden_states = self.connector(image_hidden_states, attention_mask=patch_attention_mask.view(pixel_values.size(0), -1))
        elif image_hidden_states is not None: image_hidden_states = image_hidden_states.to(dtype=self.dtype, device=input_ids.device)
        if past_seen_tokens == 0 and inputs_embeds is not None and image_hidden_states is not None: inputs_embeds = self.inputs_merger(input_ids=input_ids, inputs_embeds=inputs_embeds, image_hidden_states=image_hidden_states)
        outputs = self.text_model(inputs_embeds=inputs_embeds, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        if return_legacy_cache and use_cache: outputs.past_key_values = outputs.past_key_values.to_legacy_cache()
        if not return_dict: return tuple(v for v in [*outputs, image_hidden_states] if v is not None)
        return Idefics2BaseModelOutputWithPast(last_hidden_state=outputs.last_hidden_state, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states,
        attentions=outputs.attentions, image_hidden_states=image_hidden_states)
@add_start_docstrings("The Idefics2 Model with a language modeling head. It is made up a SigLIP vision encoder, with a language modeling head on top. ", IDEFICS2_START_DOCSTRING)
class Idefics2ForConditionalGeneration(Idefics2PreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config):
        super().__init__(config)
        self.model = Idefics2Model(config)
        self.image_token_id = self.config.image_token_id
        self.lm_head = nn.Linear(config.text_config.hidden_size, config.text_config.vocab_size, bias=False)
        self.vocab_size = config.text_config.vocab_size
        self.post_init()
    def enable_input_require_grads(self):
        def make_inputs_require_grads(module, input, output): output.requires_grad_(True)
        self._text_require_grads_hook = self.get_input_embeddings().register_forward_hook(make_inputs_require_grads)
        self._vision_require_grads_hook = self.model.vision_model.get_input_embeddings().register_forward_hook(make_inputs_require_grads)
    def disable_input_require_grads(self):
        self._text_require_grads_hook.remove()
        self._vision_require_grads_hook.remove()
    def get_input_embeddings(self): return self.model.text_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.model.text_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of=None) -> nn.Embedding:
        model_embeds = self._resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        if new_num_tokens is None and pad_to_multiple_of is None: return model_embeds
        self.config.text_config.vocab_size = model_embeds.weight.shape[0]
        self.vocab_size = self.config.text_config.vocab_size
        self.tie_weights()
        return model_embeds
    def tie_weights(self):
        output_embeddings = self.get_output_embeddings()
        input_embeddings = self.get_input_embeddings()
        if getattr(self.config, "tie_word_embeddings", True): output_embeddings.weight = input_embeddings.weight
    @add_start_docstrings_to_model_forward(IDEFICS2_INPUTS_DOCSTRING)
    def forward(self, input_ids: torch.LongTensor = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    past_key_values: Optional[List[torch.FloatTensor]] = None, inputs_embeds: Optional[torch.FloatTensor] = None, pixel_values: Optional[torch.FloatTensor] = None,
    pixel_attention_mask: Optional[torch.BoolTensor] = None, image_hidden_states: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    num_logits_to_keep: int = 0) -> Union[Tuple, Idefics2CausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        pixel_values=pixel_values, pixel_attention_mask=pixel_attention_mask, image_hidden_states=image_hidden_states, use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = outputs[0]
        logits = self.lm_head(hidden_states[:, -num_logits_to_keep:, :]).float()
        loss = None
        if labels is not None:
            logits = logits.float()
            labels = labels.to(logits.device)
            if attention_mask is not None:
                shift_attention_mask = attention_mask[..., 1:].to(logits.device)
                shift_logits = logits[..., :-1, :][shift_attention_mask != 0].contiguous()
                shift_labels = labels[..., 1:][shift_attention_mask != 0].contiguous()
            else:
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return Idefics2CausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions, image_hidden_states=outputs.image_hidden_states)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, num_logits_to_keep=None, **kwargs):
        past_length = 0
        if past_key_values is not None:
            past_length = past_key_values.get_seq_length()
            max_cache_length = past_key_values.get_max_length()
            if attention_mask is not None and attention_mask.shape[1] > input_ids.shape[1]: input_ids = input_ids[:, -(attention_mask.shape[1] - past_length) :]
            elif past_length < input_ids.shape[1]: input_ids = input_ids[:, past_length:]
            if (max_cache_length is not None and attention_mask is not None and past_length + input_ids.shape[1] > max_cache_length): attention_mask = attention_mask[:, -max_cache_length:]
        position_ids = kwargs.get("position_ids", None)
        if attention_mask is not None and position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values: position_ids = position_ids[:, -input_ids.shape[1] :]
        if inputs_embeds is not None and past_length == 0: model_inputs = {"inputs_embeds": inputs_embeds}
        else: model_inputs = {"input_ids": input_ids}
        if num_logits_to_keep is not None: model_inputs["num_logits_to_keep"] = num_logits_to_keep
        image_hidden_states = kwargs.get("image_hidden_states", None)
        if image_hidden_states is not None:
            pixel_values = None
            pixel_attention_mask = None
        else:
            pixel_values = kwargs.get("pixel_values", None)
            pixel_attention_mask = kwargs.get("pixel_attention_mask", None)
        model_inputs.update({"position_ids": position_ids, "past_key_values": past_key_values, "use_cache": kwargs.get("use_cache"), "attention_mask": attention_mask,
        "pixel_values": pixel_values, "pixel_attention_mask": pixel_attention_mask, "image_hidden_states": image_hidden_states})
        return model_inputs
    def _update_model_kwargs_for_generation(self, outputs, model_kwargs, is_encoder_decoder, **kwargs):
        model_kwargs = super()._update_model_kwargs_for_generation(outputs=outputs, model_kwargs=model_kwargs, is_encoder_decoder=is_encoder_decoder, **kwargs)
        model_kwargs["image_hidden_states"] = outputs.image_hidden_states
        return model_kwargs
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
