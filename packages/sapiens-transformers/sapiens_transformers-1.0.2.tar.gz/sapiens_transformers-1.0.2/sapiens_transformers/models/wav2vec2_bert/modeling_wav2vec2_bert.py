"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
import warnings
from typing import Optional, Tuple, Union
import numpy as np
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...integrations.deepspeed import is_deepspeed_zero3_enabled
from ...modeling_attn_mask_utils import _prepare_4d_attention_mask
from ...modeling_outputs import (BaseModelOutput, CausalLMOutput, SequenceClassifierOutput, TokenClassifierOutput, Wav2Vec2BaseModelOutput, XVectorOutput)
from ...modeling_utils import PreTrainedModel
from ...utils import (add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, is_peft_available, logging)
from .configuration_wav2vec2_bert import Wav2Vec2BertConfig
logger = logging.get_logger(__name__)
_HIDDEN_STATES_START_POSITION = 2
_CONFIG_FOR_DOC = "Wav2Vec2BertConfig"
_BASE_CHECKPOINT_FOR_DOC = "facebook/w2v-bert-2.0"
_PRETRAINED_CHECKPOINT_FOR_DOC = "hf-audio/wav2vec2-bert-CV16-en"
_EXPECTED_OUTPUT_SHAPE = [1, 146, 1024]
_CTC_EXPECTED_OUTPUT = "'mr quilter is the apostle of the middle classes and we are glad to welcome his gospel'"
_CTC_EXPECTED_LOSS = 17.04
def _compute_new_attention_mask(hidden_states: torch.Tensor, seq_lens: torch.Tensor):
    batch_size, mask_seq_len = hidden_states.shape[:2]
    indices = torch.arange(mask_seq_len, device=seq_lens.device).expand(batch_size, -1)
    bool_mask = indices >= seq_lens.unsqueeze(1).expand(-1, mask_seq_len)
    mask = hidden_states.new_ones((batch_size, mask_seq_len))
    mask = mask.masked_fill(bool_mask, 0)
    return mask
def _compute_mask_indices(shape: Tuple[int, int], mask_prob: float, mask_length: int, attention_mask: Optional[torch.LongTensor] = None, min_masks: int = 0) -> np.ndarray:
    batch_size, sequence_length = shape
    if mask_length < 1: raise ValueError("`mask_length` has to be bigger than 0.")
    if mask_length > sequence_length: raise ValueError(f"`mask_length` has to be smaller than `sequence_length`, but got `mask_length`: {mask_length} and `sequence_length`: {sequence_length}`")
    epsilon = np.random.rand(1).item()
    def compute_num_masked_span(input_length):
        num_masked_span = int(mask_prob * input_length / mask_length + epsilon)
        num_masked_span = max(num_masked_span, min_masks)
        if num_masked_span * mask_length > sequence_length: num_masked_span = sequence_length // mask_length
        if input_length - (mask_length - 1) < num_masked_span: num_masked_span = max(input_length - (mask_length - 1), 0)
        return num_masked_span
    input_lengths = (attention_mask.sum(-1).detach().tolist() if attention_mask is not None else [sequence_length for _ in range(batch_size)])
    spec_aug_mask = np.zeros((batch_size, sequence_length), dtype=bool)
    spec_aug_mask_idxs = []
    max_num_masked_span = compute_num_masked_span(sequence_length)
    if max_num_masked_span == 0: return spec_aug_mask
    for input_length in input_lengths:
        num_masked_span = compute_num_masked_span(input_length)
        spec_aug_mask_idx = np.random.choice(np.arange(input_length - (mask_length - 1)), num_masked_span, replace=False)
        if len(spec_aug_mask_idx) == 0: dummy_mask_idx = sequence_length - 1
        else: dummy_mask_idx = spec_aug_mask_idx[0]
        spec_aug_mask_idx = np.concatenate([spec_aug_mask_idx, np.ones(max_num_masked_span - num_masked_span, dtype=np.int32) * dummy_mask_idx])
        spec_aug_mask_idxs.append(spec_aug_mask_idx)
    spec_aug_mask_idxs = np.array(spec_aug_mask_idxs)
    spec_aug_mask_idxs = np.broadcast_to(spec_aug_mask_idxs[:, :, None], (batch_size, max_num_masked_span, mask_length))
    spec_aug_mask_idxs = spec_aug_mask_idxs.reshape(batch_size, max_num_masked_span * mask_length)
    offsets = np.arange(mask_length)[None, None, :]
    offsets = np.broadcast_to(offsets, (batch_size, max_num_masked_span, mask_length)).reshape(batch_size, max_num_masked_span * mask_length)
    spec_aug_mask_idxs = spec_aug_mask_idxs + offsets
    if spec_aug_mask_idxs.max() > sequence_length - 1: spec_aug_mask_idxs[spec_aug_mask_idxs > sequence_length - 1] = sequence_length - 1
    np.put_along_axis(spec_aug_mask, spec_aug_mask_idxs, 1, -1)
    return spec_aug_mask
def _sample_negative_indices(features_shape: Tuple, num_negatives: int, mask_time_indices: Optional[np.ndarray] = None):
    batch_size, sequence_length = features_shape
    sequence_length_range = np.arange(sequence_length)
    sampled_negative_indices = np.zeros(shape=(batch_size, sequence_length, num_negatives), dtype=np.int32)
    mask_time_indices = (mask_time_indices.astype(bool) if mask_time_indices is not None else np.ones(features_shape, dtype=bool))
    for batch_idx in range(batch_size):
        high = mask_time_indices[batch_idx].sum() - 1
        mapped_masked_indices = sequence_length_range[mask_time_indices[batch_idx]]
        feature_indices = np.broadcast_to(np.arange(high + 1)[:, None], (high + 1, num_negatives))
        sampled_indices = np.random.randint(0, high, size=(high + 1, num_negatives))
        sampled_indices[sampled_indices >= feature_indices] += 1
        sampled_negative_indices[batch_idx][mask_time_indices[batch_idx]] = mapped_masked_indices[sampled_indices]
        sampled_negative_indices[batch_idx] += batch_idx * sequence_length
    return sampled_negative_indices
class Wav2Vec2BertRotaryPositionalEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        dim = config.hidden_size // config.num_attention_heads
        base = config.rotary_embedding_base
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, dtype=torch.int64).float() / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.cached_sequence_length = None
        self.cached_rotary_positional_embedding = None
    def forward(self, hidden_states):
        sequence_length = hidden_states.shape[1]
        if sequence_length == self.cached_sequence_length and self.cached_rotary_positional_embedding is not None: return self.cached_rotary_positional_embedding
        self.cached_sequence_length = sequence_length
        time_stamps = torch.arange(sequence_length).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", time_stamps, self.inv_freq)
        embeddings = torch.cat((freqs, freqs), dim=-1)
        cos_embeddings = embeddings.cos()[:, None, None, :]
        sin_embeddings = embeddings.sin()[:, None, None, :]
        self.cached_rotary_positional_embedding = torch.stack([cos_embeddings, sin_embeddings]).type_as(hidden_states)
        return self.cached_rotary_positional_embedding
class Wav2Vec2BertRelPositionalEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.max_len = config.max_source_positions
        self.d_model = config.hidden_size
        self.pe = None
        self.extend_pe(torch.tensor(0.0).expand(1, self.max_len))
    def extend_pe(self, x):
        if self.pe is not None:
            if self.pe.size(1) >= x.size(1) * 2 - 1:
                if self.pe.dtype != x.dtype or self.pe.device != x.device: self.pe = self.pe.to(dtype=x.dtype, device=x.device)
                return
        pe_positive = torch.zeros(x.size(1), self.d_model)
        pe_negative = torch.zeros(x.size(1), self.d_model)
        position = torch.arange(0, x.size(1), dtype=torch.int64).float().unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.d_model, 2, dtype=torch.int64).float() * -(math.log(10000.0) / self.d_model))
        pe_positive[:, 0::2] = torch.sin(position * div_term)
        pe_positive[:, 1::2] = torch.cos(position * div_term)
        pe_negative[:, 0::2] = torch.sin(-1 * position * div_term)
        pe_negative[:, 1::2] = torch.cos(-1 * position * div_term)
        pe_positive = torch.flip(pe_positive, [0]).unsqueeze(0)
        pe_negative = pe_negative[1:].unsqueeze(0)
        pe = torch.cat([pe_positive, pe_negative], dim=1)
        self.pe = pe.to(device=x.device, dtype=x.dtype)
    def forward(self, hidden_states: torch.Tensor):
        self.extend_pe(hidden_states)
        start_idx = self.pe.size(1) // 2 - hidden_states.size(1) + 1
        end_idx = self.pe.size(1) // 2 + hidden_states.size(1)
        relative_position_embeddings = self.pe[:, start_idx:end_idx]
        return relative_position_embeddings
class Wav2Vec2BertFeatureProjection(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layer_norm = nn.LayerNorm(config.feature_projection_input_dim, eps=config.layer_norm_eps)
        self.projection = nn.Linear(config.feature_projection_input_dim, config.hidden_size)
        self.dropout = nn.Dropout(config.feat_proj_dropout)
    def forward(self, hidden_states):
        norm_hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.projection(norm_hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states, norm_hidden_states
class Wav2Vec2BertFeedForward(nn.Module):
    def __init__(self, config, act_fn=None, hidden_size=None):
        super().__init__()
        act_fn = act_fn if act_fn is not None else config.hidden_act
        hidden_size = hidden_size if hidden_size is not None else config.hidden_size
        self.intermediate_dropout = nn.Dropout(config.activation_dropout)
        self.intermediate_dense = nn.Linear(hidden_size, config.intermediate_size)
        self.intermediate_act_fn = ACT2FN[act_fn] if isinstance(act_fn, str) else act_fn
        self.output_dense = nn.Linear(config.intermediate_size, hidden_size)
        self.output_dropout = nn.Dropout(config.hidden_dropout)
    def forward(self, hidden_states):
        hidden_states = self.intermediate_dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        hidden_states = self.intermediate_dropout(hidden_states)
        hidden_states = self.output_dense(hidden_states)
        hidden_states = self.output_dropout(hidden_states)
        return hidden_states
class Wav2Vec2BertConvolutionModule(nn.Module):
    def __init__(self, config):
        super().__init__()
        if (config.conv_depthwise_kernel_size - 1) % 2 == 1: raise ValueError("`config.conv_depthwise_kernel_size` should be a odd number for 'SAME' padding")
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.pointwise_conv1 = nn.Conv1d(config.hidden_size, 2 * config.hidden_size, kernel_size=1, stride=1, padding=0, bias=False)
        self.glu = nn.GLU(dim=1)
        self.depthwise_conv = nn.Conv1d(config.hidden_size, config.hidden_size, config.conv_depthwise_kernel_size, stride=1, padding=0, groups=config.hidden_size, bias=False)
        self.depthwise_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.activation = ACT2FN[config.hidden_act]
        self.pointwise_conv2 = nn.Conv1d(config.hidden_size, config.hidden_size, kernel_size=1, stride=1, padding=0, bias=False)
        self.dropout = nn.Dropout(config.conformer_conv_dropout)
    def forward(self, hidden_states, attention_mask=None):
        hidden_states = self.layer_norm(hidden_states)
        if attention_mask is not None: hidden_states = hidden_states.masked_fill(~attention_mask.bool().unsqueeze(-1), 0.0)
        hidden_states = hidden_states.transpose(1, 2)
        hidden_states = self.pointwise_conv1(hidden_states)
        hidden_states = self.glu(hidden_states)
        hidden_states = torch.nn.functional.pad(hidden_states, (self.depthwise_conv.kernel_size[0] - 1, 0))
        hidden_states = self.depthwise_conv(hidden_states)
        hidden_states = self.depthwise_layer_norm(hidden_states.transpose(1, 2)).transpose(1, 2)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.pointwise_conv2(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = hidden_states.transpose(1, 2)
        return hidden_states
class Wav2Vec2BertSelfAttention(nn.Module):
    def __init__(self, config, is_adapter_attention=False):
        super().__init__()
        hidden_size = config.hidden_size if not is_adapter_attention else config.output_hidden_size
        self.head_size = hidden_size // config.num_attention_heads
        self.num_heads = config.num_attention_heads
        self.position_embeddings_type = config.position_embeddings_type if not is_adapter_attention else None
        self.linear_q = nn.Linear(hidden_size, hidden_size)
        self.linear_k = nn.Linear(hidden_size, hidden_size)
        self.linear_v = nn.Linear(hidden_size, hidden_size)
        self.linear_out = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(p=config.attention_dropout)
        if self.position_embeddings_type == "relative":
            self.linear_pos = nn.Linear(hidden_size, hidden_size, bias=False)
            self.pos_bias_u = nn.Parameter(torch.zeros(self.num_heads, self.head_size))
            self.pos_bias_v = nn.Parameter(torch.zeros(self.num_heads, self.head_size))
        if self.position_embeddings_type == "relative_key":
            self.left_max_position_embeddings = config.left_max_position_embeddings
            self.right_max_position_embeddings = config.right_max_position_embeddings
            num_positions = self.left_max_position_embeddings + self.right_max_position_embeddings + 1
            self.distance_embedding = nn.Embedding(num_positions, self.head_size)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, relative_position_embeddings: Optional[torch.Tensor] = None,
    output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        batch_size, sequence_length, hidden_size = hidden_states.size()
        query_key_states = hidden_states
        value_states = hidden_states
        if self.position_embeddings_type == "rotary":
            if relative_position_embeddings is None: raise ValueError("`relative_position_embeddings` has to be defined when `self.position_embeddings_type == 'rotary'")
            query_key_states = self._apply_rotary_embedding(query_key_states, relative_position_embeddings)
        query = self.linear_q(query_key_states).view(batch_size, -1, self.num_heads, self.head_size)
        key = self.linear_k(query_key_states).view(batch_size, -1, self.num_heads, self.head_size)
        value = self.linear_v(value_states).view(batch_size, -1, self.num_heads, self.head_size)
        query = query.transpose(1, 2)
        key = key.transpose(1, 2)
        value = value.transpose(1, 2)
        if self.position_embeddings_type == "relative":
            if relative_position_embeddings is None: raise ValueError("`relative_position_embeddings` has to be defined when `self.position_embeddings_type == 'relative'")
            scores = self._apply_relative_embeddings(query=query, key=key, relative_position_embeddings=relative_position_embeddings)
        else: scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.head_size)
        if self.position_embeddings_type == "relative_key":
            query_length, key_length = query.shape[2], key.shape[2]
            position_ids_l = torch.arange(query_length, dtype=torch.long, device=hidden_states.device).view(-1, 1)
            position_ids_r = torch.arange(key_length, dtype=torch.long, device=hidden_states.device).view(1, -1)
            distance = position_ids_r - position_ids_l
            distance = torch.clamp(distance, -self.left_max_position_embeddings, self.right_max_position_embeddings)
            positional_embedding = self.distance_embedding(distance + self.left_max_position_embeddings)
            positional_embedding = positional_embedding.to(dtype=query.dtype)
            relative_position_attn_weights = torch.einsum("bhld,lrd->bhlr", query, positional_embedding)
            scores = scores + (relative_position_attn_weights / math.sqrt(self.head_size))
        if attention_mask is not None: scores = scores + attention_mask
        probs = torch.softmax(scores, dim=-1)
        probs = self.dropout(probs)
        hidden_states = torch.matmul(probs, value)
        hidden_states = hidden_states.transpose(1, 2).reshape(batch_size, -1, self.num_heads * self.head_size)
        hidden_states = self.linear_out(hidden_states)
        return hidden_states, probs
    def _apply_rotary_embedding(self, hidden_states, relative_position_embeddings):
        batch_size, sequence_length, hidden_size = hidden_states.size()
        hidden_states = hidden_states.view(batch_size, sequence_length, self.num_heads, self.head_size)
        cos = relative_position_embeddings[0, :sequence_length, ...]
        sin = relative_position_embeddings[1, :sequence_length, ...]
        hidden_states = hidden_states.transpose(0, 1)
        rotated_states_begin = hidden_states[..., : self.head_size // 2]
        rotated_states_end = hidden_states[..., self.head_size // 2 :]
        rotated_states = torch.cat((-rotated_states_end, rotated_states_begin), dim=rotated_states_begin.ndim - 1)
        hidden_states = (hidden_states * cos) + (rotated_states * sin)
        hidden_states = hidden_states.transpose(0, 1)
        hidden_states = hidden_states.view(batch_size, sequence_length, self.num_heads * self.head_size)
        return hidden_states
    def _apply_relative_embeddings(self, query, key, relative_position_embeddings):
        proj_relative_position_embeddings = self.linear_pos(relative_position_embeddings)
        proj_relative_position_embeddings = proj_relative_position_embeddings.view(relative_position_embeddings.size(0), -1, self.num_heads, self.head_size)
        proj_relative_position_embeddings = proj_relative_position_embeddings.transpose(1, 2)
        proj_relative_position_embeddings = proj_relative_position_embeddings.transpose(2, 3)
        query = query.transpose(1, 2)
        q_with_bias_u = (query + self.pos_bias_u).transpose(1, 2)
        q_with_bias_v = (query + self.pos_bias_v).transpose(1, 2)
        scores_ac = torch.matmul(q_with_bias_u, key.transpose(-2, -1))
        scores_bd = torch.matmul(q_with_bias_v, proj_relative_position_embeddings)
        zero_pad = torch.zeros((*scores_bd.size()[:3], 1), device=scores_bd.device, dtype=scores_bd.dtype)
        scores_bd_padded = torch.cat([zero_pad, scores_bd], dim=-1)
        scores_bd_padded_shape = scores_bd.size()[:2] + (scores_bd.shape[3] + 1, scores_bd.shape[2])
        scores_bd_padded = scores_bd_padded.view(*scores_bd_padded_shape)
        scores_bd = scores_bd_padded[:, :, 1:].view_as(scores_bd)
        scores_bd = scores_bd[:, :, :, : scores_bd.size(-1) // 2 + 1]
        scores = (scores_ac + scores_bd) / math.sqrt(self.head_size)
        return scores
class Wav2Vec2BertEncoderLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        embed_dim = config.hidden_size
        dropout = config.attention_dropout
        self.ffn1_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.ffn1 = Wav2Vec2BertFeedForward(config)
        self.self_attn_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.self_attn_dropout = nn.Dropout(dropout)
        self.self_attn = Wav2Vec2BertSelfAttention(config)
        self.conv_module = Wav2Vec2BertConvolutionModule(config)
        self.ffn2_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.ffn2 = Wav2Vec2BertFeedForward(config)
        self.final_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states, attention_mask: Optional[torch.Tensor] = None, relative_position_embeddings: Optional[torch.Tensor] = None,
    output_attentions: bool = False, conv_attention_mask: Optional[torch.Tensor] = None):
        hidden_states = hidden_states
        residual = hidden_states
        hidden_states = self.ffn1_layer_norm(hidden_states)
        hidden_states = self.ffn1(hidden_states)
        hidden_states = hidden_states * 0.5 + residual
        residual = hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states, attn_weigts = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, relative_position_embeddings=relative_position_embeddings, output_attentions=output_attentions)
        hidden_states = self.self_attn_dropout(hidden_states)
        hidden_states = hidden_states + residual
        residual = hidden_states
        hidden_states = self.conv_module(hidden_states, attention_mask=conv_attention_mask)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.ffn2_layer_norm(hidden_states)
        hidden_states = self.ffn2(hidden_states)
        hidden_states = hidden_states * 0.5 + residual
        hidden_states = self.final_layer_norm(hidden_states)
        return hidden_states, attn_weigts
class Wav2Vec2BertEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config.position_embeddings_type == "relative": self.embed_positions = Wav2Vec2BertRelPositionalEmbedding(config)
        elif config.position_embeddings_type == "rotary": self.embed_positions = Wav2Vec2BertRotaryPositionalEmbedding(config)
        else: self.embed_positions = None
        self.dropout = nn.Dropout(config.hidden_dropout)
        self.layers = nn.ModuleList([Wav2Vec2BertEncoderLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states, attention_mask=None, output_attentions=False, output_hidden_states=False, return_dict=True):
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        conv_attention_mask = attention_mask
        if attention_mask is not None:
            hidden_states = hidden_states.masked_fill(~attention_mask.bool().unsqueeze(-1), 0.0)
            attention_mask = 1.0 - attention_mask[:, None, None, :].to(dtype=hidden_states.dtype)
            attention_mask = attention_mask * torch.finfo(hidden_states.dtype).min
            attention_mask = attention_mask.expand(attention_mask.shape[0], 1, attention_mask.shape[-1], attention_mask.shape[-1])
        hidden_states = self.dropout(hidden_states)
        if self.embed_positions is not None: relative_position_embeddings = self.embed_positions(hidden_states)
        else: relative_position_embeddings = None
        deepspeed_zero3_is_enabled = is_deepspeed_zero3_enabled()
        for i, layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            dropout_probability = torch.rand([])
            skip_the_layer = True if self.training and (dropout_probability < self.config.layerdrop) else False
            if not skip_the_layer or deepspeed_zero3_is_enabled:
                if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer.__call__, hidden_states, attention_mask, relative_position_embeddings, output_attentions, conv_attention_mask)
                else: layer_outputs = layer(hidden_states, attention_mask=attention_mask, relative_position_embeddings=relative_position_embeddings, output_attentions=output_attentions, conv_attention_mask=conv_attention_mask)
                hidden_states = layer_outputs[0]
            if skip_the_layer: layer_outputs = (None, None)
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions)
class Wav2Vec2BertAdapter(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.output_hidden_size != config.hidden_size:
            self.proj = nn.Linear(config.hidden_size, config.output_hidden_size)
            self.proj_layer_norm = nn.LayerNorm(config.output_hidden_size, eps=config.layer_norm_eps)
        else: self.proj = self.proj_layer_norm = None
        self.layers = nn.ModuleList(Wav2Vec2BertAdapterLayer(config) for _ in range(config.num_adapter_layers))
        self.layerdrop = config.layerdrop
        self.kernel_size = config.adapter_kernel_size
        self.stride = config.adapter_stride
    def _compute_sub_sample_lengths_from_attention_mask(self, seq_lens):
        if seq_lens is None: return seq_lens
        pad = self.kernel_size // 2
        seq_lens = ((seq_lens + 2 * pad - self.kernel_size) / self.stride) + 1
        return seq_lens.floor()
    def forward(self, hidden_states, attention_mask=None):
        if self.proj is not None and self.proj_layer_norm is not None:
            hidden_states = self.proj(hidden_states)
            hidden_states = self.proj_layer_norm(hidden_states)
        sub_sampled_lengths = None
        if attention_mask is not None: sub_sampled_lengths = (attention_mask.size(1) - (1 - attention_mask.int()).sum(1)).to(hidden_states.device)
        for layer in self.layers:
            layerdrop_prob = torch.rand([])
            sub_sampled_lengths = self._compute_sub_sample_lengths_from_attention_mask(sub_sampled_lengths)
            if not self.training or (layerdrop_prob > self.layerdrop): hidden_states = layer(hidden_states, attention_mask=attention_mask, sub_sampled_lengths=sub_sampled_lengths)
        return hidden_states
class Wav2Vec2BertAdapterLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        embed_dim = config.output_hidden_size
        dropout = config.conformer_conv_dropout
        self.kernel_size = config.adapter_kernel_size
        self.stride = config.adapter_stride
        self.residual_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.residual_conv = nn.Conv1d(embed_dim, 2 * embed_dim, self.kernel_size, stride=self.stride, padding=self.stride // 2)
        self.activation = nn.GLU(dim=1)
        self.self_attn_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.self_attn_conv = nn.Conv1d(embed_dim, 2 * embed_dim, self.kernel_size, stride=self.stride, padding=self.stride // 2)
        self.self_attn = Wav2Vec2BertSelfAttention(config, is_adapter_attention=True)
        self.self_attn_dropout = nn.Dropout(dropout)
        self.ffn_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.ffn = Wav2Vec2BertFeedForward(config, act_fn=config.adapter_act, hidden_size=embed_dim)
    def forward(self, hidden_states, attention_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, sub_sampled_lengths: Optional[torch.Tensor] = None):
        residual = self.residual_layer_norm(hidden_states)
        residual = residual.transpose(1, 2)
        residual = self.residual_conv(residual)
        residual = self.activation(residual)
        residual = residual.transpose(1, 2)
        hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states = hidden_states.transpose(1, 2)
        hidden_states = self.self_attn_conv(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = hidden_states.transpose(1, 2)
        if attention_mask is not None:
            attention_mask = _compute_new_attention_mask(hidden_states=hidden_states, seq_lens=sub_sampled_lengths)
            attention_mask = _prepare_4d_attention_mask(attention_mask, hidden_states.dtype)
        hidden_states, attn_weigths = self.self_attn(hidden_states, attention_mask=attention_mask, output_attentions=output_attentions)
        hidden_states = self.self_attn_dropout(hidden_states)
        hidden_states = hidden_states + residual
        residual = hidden_states
        hidden_states = self.ffn_layer_norm(hidden_states)
        hidden_states = self.ffn(hidden_states) + residual
        return hidden_states
class Wav2Vec2BertPreTrainedModel(PreTrainedModel):
    config_class = Wav2Vec2BertConfig
    base_model_prefix = "wav2vec2_bert"
    main_input_name = "input_features"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, Wav2Vec2BertSelfAttention):
            if hasattr(module, "pos_bias_u"): nn.init.xavier_uniform_(module.pos_bias_u)
            if hasattr(module, "pos_bias_v"): nn.init.xavier_uniform_(module.pos_bias_v)
        elif isinstance(module, Wav2Vec2BertFeatureProjection):
            k = math.sqrt(1 / module.projection.in_features)
            nn.init.uniform_(module.projection.weight, a=-k, b=k)
            nn.init.uniform_(module.projection.bias, a=-k, b=k)
        elif isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, (nn.LayerNorm, nn.GroupNorm)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, nn.Conv1d):
            nn.init.kaiming_normal_(module.weight)
            if module.bias is not None:
                k = math.sqrt(module.groups / (module.in_channels * module.kernel_size[0]))
                nn.init.uniform_(module.bias, a=-k, b=k)
    def _get_feat_extract_output_lengths(self, input_lengths: Union[torch.LongTensor, int], add_adapter: Optional[bool] = None):
        add_adapter = self.config.add_adapter if add_adapter is None else add_adapter
        def _conv_out_length(input_length, kernel_size, stride, padding): return torch.div(input_length + 2 * padding - kernel_size, stride, rounding_mode="floor") + 1
        if add_adapter:
            padding = self.config.adapter_kernel_size // 2
            for _ in range(self.config.num_adapter_layers): input_lengths = _conv_out_length(input_lengths, self.config.adapter_kernel_size, self.config.adapter_stride, padding)
        return input_lengths
    def _get_feature_vector_attention_mask(self, feature_vector_length: int, attention_mask: torch.LongTensor, add_adapter=None):
        non_padded_lengths = attention_mask.cumsum(dim=-1)[:, -1]
        output_lengths = self._get_feat_extract_output_lengths(non_padded_lengths, add_adapter=add_adapter)
        output_lengths = output_lengths.to(torch.long)
        batch_size = attention_mask.shape[0]
        attention_mask = torch.zeros((batch_size, feature_vector_length), dtype=attention_mask.dtype, device=attention_mask.device)
        attention_mask[(torch.arange(attention_mask.shape[0], device=attention_mask.device), output_lengths - 1)] = 1
        attention_mask = attention_mask.flip([-1]).cumsum(-1).flip([-1]).bool()
        return attention_mask
WAV2VEC2_BERT_START_DOCSTRING = r"""
    Wav2Vec2Bert was proposed in [wav2vec 2.0: A Framework for Self-Supervised Learning of Speech
    Representations](https://arxiv.org/abs/2006.11477) by Alexei Baevski, Henry Zhou, Abdelrahman Mohamed, Michael
    Auli.
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving etc.).
    This model is a PyTorch [nn.Module](https://pytorch.org/docs/stable/nn.html#nn.Module) sub-class. Use it as a
    regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and behavior.
    Parameters:
        config ([`Wav2Vec2BertConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
WAV2VEC2_BERT_INPUTS_DOCSTRING = r"""
    Args:
        input_features (`torch.FloatTensor` of shape `(batch_size, sequence_length)`):
            Float values of input raw speech waveform. Values can be obtained by loading a `.flac` or `.wav` audio file
            into an array of type `List[float]` or a `numpy.ndarray`, *e.g.* via the soundfile library (`pip install
            soundfile`). To prepare the array into `input_features`, the [`AutoProcessor`] should be used for padding and
            conversion into a tensor of type `torch.FloatTensor`. See [`Wav2Vec2BertProcessor.__call__`] for details.
        attention_mask (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing convolution and attention on padding token indices. Mask values selected in `[0,
            1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare Wav2Vec2Bert Model transformer outputting raw hidden-states without any specific head on top.", WAV2VEC2_BERT_START_DOCSTRING)
class Wav2Vec2BertModel(Wav2Vec2BertPreTrainedModel):
    def __init__(self, config: Wav2Vec2BertConfig):
        super().__init__(config)
        self.config = config
        self.feature_projection = Wav2Vec2BertFeatureProjection(config)
        if config.mask_time_prob > 0.0 or config.mask_feature_prob > 0.0: self.masked_spec_embed = nn.Parameter(torch.Tensor(config.hidden_size).uniform_())
        self.encoder = Wav2Vec2BertEncoder(config)
        self.adapter = Wav2Vec2BertAdapter(config) if config.add_adapter else None
        self.intermediate_ffn = None
        if config.use_intermediate_ffn_before_adapter: self.intermediate_ffn = Wav2Vec2BertFeedForward(config, act_fn="relu")
        self.post_init()
    def _mask_hidden_states(self, hidden_states: torch.FloatTensor, mask_time_indices: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None):
        if not getattr(self.config, "apply_spec_augment", True): return hidden_states
        batch_size, sequence_length, hidden_size = hidden_states.size()
        if mask_time_indices is not None: hidden_states[mask_time_indices] = self.masked_spec_embed.to(hidden_states.dtype)
        elif self.config.mask_time_prob > 0 and self.training:
            mask_time_indices = _compute_mask_indices((batch_size, sequence_length), mask_prob=self.config.mask_time_prob, mask_length=self.config.mask_time_length,
            attention_mask=attention_mask, min_masks=self.config.mask_time_min_masks)
            mask_time_indices = torch.tensor(mask_time_indices, device=hidden_states.device, dtype=torch.bool)
            hidden_states[mask_time_indices] = self.masked_spec_embed.to(hidden_states.dtype)
        if self.config.mask_feature_prob > 0 and self.training:
            mask_feature_indices = _compute_mask_indices((batch_size, hidden_size), mask_prob=self.config.mask_feature_prob, mask_length=self.config.mask_feature_length, min_masks=self.config.mask_feature_min_masks)
            mask_feature_indices = torch.tensor(mask_feature_indices, device=hidden_states.device, dtype=torch.bool)
            mask_feature_indices = mask_feature_indices[:, None].expand(-1, sequence_length, -1)
            hidden_states[mask_feature_indices] = 0
        return hidden_states
    @add_start_docstrings_to_model_forward(WAV2VEC2_BERT_INPUTS_DOCSTRING)
    def forward(self, input_features: Optional[torch.Tensor], attention_mask: Optional[torch.Tensor] = None, mask_time_indices: Optional[torch.FloatTensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, Wav2Vec2BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states, extract_features = self.feature_projection(input_features)
        hidden_states = self._mask_hidden_states(hidden_states, mask_time_indices=mask_time_indices, attention_mask=attention_mask)
        encoder_outputs = self.encoder(hidden_states, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = encoder_outputs[0]
        if self.intermediate_ffn:
            expanded_hidden_states = self.intermediate_ffn(hidden_states)
            hidden_states = hidden_states + 0.5 * expanded_hidden_states
        if self.adapter is not None: hidden_states = self.adapter(hidden_states, attention_mask=attention_mask)
        if not return_dict: return (hidden_states, extract_features) + encoder_outputs[1:]
        return Wav2Vec2BaseModelOutput(last_hidden_state=hidden_states, extract_features=extract_features, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
@add_start_docstrings("Wav2Vec2Bert Model with a `language modeling` head on top for Connectionist Temporal Classification (CTC).", WAV2VEC2_BERT_START_DOCSTRING)
class Wav2Vec2BertForCTC(Wav2Vec2BertPreTrainedModel):
    def __init__(self, config, target_lang: Optional[str] = None):
        super().__init__(config)
        self.wav2vec2_bert = Wav2Vec2BertModel(config)
        self.dropout = nn.Dropout(config.final_dropout)
        self.target_lang = target_lang
        if config.vocab_size is None: raise ValueError(f"You are trying to instantiate {self.__class__} with a configuration that does not define the vocabulary size of the language model head. Please instantiate the model as follows: `Wav2Vec2BertForCTC.from_pretrained(..., vocab_size=vocab_size)`. or define `vocab_size` of your model's configuration.")
        output_hidden_size = (config.output_hidden_size if hasattr(config, "add_adapter") and config.add_adapter else config.hidden_size)
        self.lm_head = nn.Linear(output_hidden_size, config.vocab_size)
        self.post_init()
    @add_start_docstrings_to_model_forward(WAV2VEC2_BERT_INPUTS_DOCSTRING)
    def forward(self, input_features: Optional[torch.Tensor], attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, labels: Optional[torch.Tensor] = None) -> Union[Tuple, CausalLMOutput]:
        if labels is not None and labels.max() >= self.config.vocab_size: raise ValueError(f"Label values must be <= vocab_size: {self.config.vocab_size}")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.wav2vec2_bert(input_features, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = outputs[0]
        hidden_states = self.dropout(hidden_states)
        logits = self.lm_head(hidden_states)
        loss = None
        if labels is not None:
            attention_mask = (attention_mask if attention_mask is not None else torch.ones(input_features.shape[:2], device=input_features.device, dtype=torch.long))
            input_lengths = self._get_feat_extract_output_lengths(attention_mask.sum([-1])).to(torch.long)
            labels_mask = labels >= 0
            target_lengths = labels_mask.sum(-1)
            flattened_targets = labels.masked_select(labels_mask)
            log_probs = nn.functional.log_softmax(logits, dim=-1, dtype=torch.float32).transpose(0, 1)
            with torch.backends.cudnn.flags(enabled=False): loss = nn.functional.ctc_loss(log_probs, flattened_targets, input_lengths, target_lengths,
            blank=self.config.pad_token_id, reduction=self.config.ctc_loss_reduction, zero_infinity=self.config.ctc_zero_infinity)
        if not return_dict:
            output = (logits,) + outputs[_HIDDEN_STATES_START_POSITION:]
            return ((loss,) + output) if loss is not None else output
        return CausalLMOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Wav2Vec2Bert Model with a sequence classification head on top (a linear layer over the pooled output) for tasks like SUPERB Keyword Spotting.", WAV2VEC2_BERT_START_DOCSTRING)
class Wav2Vec2BertForSequenceClassification(Wav2Vec2BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        if hasattr(config, "add_adapter") and config.add_adapter: raise ValueError("Sequence classification does not support the use of Wav2Vec2Bert adapters (config.add_adapter=True)")
        self.wav2vec2_bert = Wav2Vec2BertModel(config)
        num_layers = config.num_hidden_layers + 1
        if config.use_weighted_layer_sum: self.layer_weights = nn.Parameter(torch.ones(num_layers) / num_layers)
        self.projector = nn.Linear(config.hidden_size, config.classifier_proj_size)
        self.classifier = nn.Linear(config.classifier_proj_size, config.num_labels)
        self.post_init()
    def freeze_base_model(self):
        for param in self.wav2vec2_bert.parameters(): param.requires_grad = False
    @add_start_docstrings_to_model_forward(WAV2VEC2_BERT_INPUTS_DOCSTRING)
    def forward(self, input_features: Optional[torch.Tensor], attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: Optional[torch.Tensor] = None) -> Union[Tuple, SequenceClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = True if self.config.use_weighted_layer_sum else output_hidden_states
        outputs = self.wav2vec2_bert(input_features, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if self.config.use_weighted_layer_sum:
            hidden_states = outputs[_HIDDEN_STATES_START_POSITION]
            hidden_states = torch.stack(hidden_states, dim=1)
            norm_weights = nn.functional.softmax(self.layer_weights, dim=-1)
            hidden_states = (hidden_states * norm_weights.view(-1, 1, 1)).sum(dim=1)
        else: hidden_states = outputs[0]
        hidden_states = self.projector(hidden_states)
        if attention_mask is None: pooled_output = hidden_states.mean(dim=1)
        else:
            padding_mask = self._get_feature_vector_attention_mask(hidden_states.shape[1], attention_mask)
            hidden_states[~padding_mask] = 0.0
            pooled_output = hidden_states.sum(dim=1) / padding_mask.sum(dim=1).view(-1, 1)
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.config.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[_HIDDEN_STATES_START_POSITION:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Wav2Vec2Bert Model with a frame classification head on top for tasks like Speaker Diarization.", WAV2VEC2_BERT_START_DOCSTRING)
class Wav2Vec2BertForAudioFrameClassification(Wav2Vec2BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        if hasattr(config, "add_adapter") and config.add_adapter: raise ValueError("Audio frame classification does not support the use of Wav2Vec2Bert adapters (config.add_adapter=True)")
        self.wav2vec2_bert = Wav2Vec2BertModel(config)
        num_layers = config.num_hidden_layers + 1
        if config.use_weighted_layer_sum: self.layer_weights = nn.Parameter(torch.ones(num_layers) / num_layers)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.num_labels = config.num_labels
        self.init_weights()
    def freeze_base_model(self):
        for param in self.wav2vec2_bert.parameters(): param.requires_grad = False
    @add_start_docstrings_to_model_forward(WAV2VEC2_BERT_INPUTS_DOCSTRING)
    def forward(self, input_features: Optional[torch.Tensor], attention_mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, TokenClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = True if self.config.use_weighted_layer_sum else output_hidden_states
        outputs = self.wav2vec2_bert(input_features, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if self.config.use_weighted_layer_sum:
            hidden_states = outputs[_HIDDEN_STATES_START_POSITION]
            hidden_states = torch.stack(hidden_states, dim=1)
            norm_weights = nn.functional.softmax(self.layer_weights, dim=-1)
            hidden_states = (hidden_states * norm_weights.view(-1, 1, 1)).sum(dim=1)
        else: hidden_states = outputs[0]
        logits = self.classifier(hidden_states)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), torch.argmax(labels.view(-1, self.num_labels), axis=1))
        if not return_dict:
            output = (logits,) + outputs[_HIDDEN_STATES_START_POSITION:]
            return output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
class AMSoftmaxLoss(nn.Module):
    def __init__(self, input_dim, num_labels, scale=30.0, margin=0.4):
        super(AMSoftmaxLoss, self).__init__()
        self.scale = scale
        self.margin = margin
        self.num_labels = num_labels
        self.weight = nn.Parameter(torch.randn(input_dim, num_labels), requires_grad=True)
        self.loss = nn.CrossEntropyLoss()
    def forward(self, hidden_states, labels):
        labels = labels.flatten()
        weight = nn.functional.normalize(self.weight, dim=0)
        hidden_states = nn.functional.normalize(hidden_states, dim=1)
        cos_theta = torch.mm(hidden_states, weight)
        psi = cos_theta - self.margin
        onehot = nn.functional.one_hot(labels, self.num_labels)
        logits = self.scale * torch.where(onehot.bool(), psi, cos_theta)
        loss = self.loss(logits, labels)
        return loss
class TDNNLayer(nn.Module):
    def __init__(self, config, layer_id=0):
        super().__init__()
        self.in_conv_dim = config.tdnn_dim[layer_id - 1] if layer_id > 0 else config.tdnn_dim[layer_id]
        self.out_conv_dim = config.tdnn_dim[layer_id]
        self.kernel_size = config.tdnn_kernel[layer_id]
        self.dilation = config.tdnn_dilation[layer_id]
        self.kernel = nn.Linear(self.in_conv_dim * self.kernel_size, self.out_conv_dim)
        self.activation = nn.ReLU()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if is_peft_available():
            from peft.tuners.lora import LoraLayer
            if isinstance(self.kernel, LoraLayer): warnings.warn("Detected LoRA on TDNNLayer. LoRA weights won't be applied due to optimization. You should exclude TDNNLayer from LoRA's target modules.")
        hidden_states = hidden_states.transpose(1, 2)
        weight = self.kernel.weight.view(self.out_conv_dim, self.kernel_size, self.in_conv_dim).transpose(1, 2)
        hidden_states = nn.functional.conv1d(hidden_states, weight, self.kernel.bias, dilation=self.dilation)
        hidden_states = hidden_states.transpose(1, 2)
        hidden_states = self.activation(hidden_states)
        return hidden_states
@add_start_docstrings("Wav2Vec2Bert Model with an XVector feature extraction head on top for tasks like Speaker Verification.", WAV2VEC2_BERT_START_DOCSTRING)
class Wav2Vec2BertForXVector(Wav2Vec2BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.wav2vec2_bert = Wav2Vec2BertModel(config)
        num_layers = config.num_hidden_layers + 1
        if config.use_weighted_layer_sum: self.layer_weights = nn.Parameter(torch.ones(num_layers) / num_layers)
        self.projector = nn.Linear(config.hidden_size, config.tdnn_dim[0])
        tdnn_layers = [TDNNLayer(config, i) for i in range(len(config.tdnn_dim))]
        self.tdnn = nn.ModuleList(tdnn_layers)
        self.feature_extractor = nn.Linear(config.tdnn_dim[-1] * 2, config.xvector_output_dim)
        self.classifier = nn.Linear(config.xvector_output_dim, config.xvector_output_dim)
        self.objective = AMSoftmaxLoss(config.xvector_output_dim, config.num_labels)
        self.init_weights()
    def freeze_base_model(self):
        for param in self.wav2vec2_bert.parameters(): param.requires_grad = False
    def _get_tdnn_output_lengths(self, input_lengths: Union[torch.LongTensor, int]):
        def _conv_out_length(input_length, kernel_size, stride): return (input_length - kernel_size) // stride + 1
        for kernel_size in self.config.tdnn_kernel: input_lengths = _conv_out_length(input_lengths, kernel_size, 1)
        return input_lengths
    @add_start_docstrings_to_model_forward(WAV2VEC2_BERT_INPUTS_DOCSTRING)
    def forward(self, input_features: Optional[torch.Tensor], attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: Optional[torch.Tensor] = None) -> Union[Tuple, XVectorOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = True if self.config.use_weighted_layer_sum else output_hidden_states
        outputs = self.wav2vec2_bert(input_features, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if self.config.use_weighted_layer_sum:
            hidden_states = outputs[_HIDDEN_STATES_START_POSITION]
            hidden_states = torch.stack(hidden_states, dim=1)
            norm_weights = nn.functional.softmax(self.layer_weights, dim=-1)
            hidden_states = (hidden_states * norm_weights.view(-1, 1, 1)).sum(dim=1)
        else: hidden_states = outputs[0]
        hidden_states = self.projector(hidden_states)
        for tdnn_layer in self.tdnn: hidden_states = tdnn_layer(hidden_states)
        if attention_mask is None:
            mean_features = hidden_states.mean(dim=1)
            std_features = hidden_states.std(dim=1)
        else:
            feat_extract_output_lengths = self._get_feat_extract_output_lengths(attention_mask.sum(dim=1))
            tdnn_output_lengths = self._get_tdnn_output_lengths(feat_extract_output_lengths)
            mean_features = []
            std_features = []
            for i, length in enumerate(tdnn_output_lengths):
                mean_features.append(hidden_states[i, :length].mean(dim=0))
                std_features.append(hidden_states[i, :length].std(dim=0))
            mean_features = torch.stack(mean_features)
            std_features = torch.stack(std_features)
        statistic_pooling = torch.cat([mean_features, std_features], dim=-1)
        output_embeddings = self.feature_extractor(statistic_pooling)
        logits = self.classifier(output_embeddings)
        loss = None
        if labels is not None: loss = self.objective(logits, labels)
        if not return_dict:
            output = (logits, output_embeddings) + outputs[_HIDDEN_STATES_START_POSITION:]
            return ((loss,) + output) if loss is not None else output
        return XVectorOutput(loss=loss, logits=logits, embeddings=output_embeddings, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
