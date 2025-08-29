"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import List, Optional, Tuple, Union
import numpy as np
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, L1Loss
from ...activations import ACT2FN
from ...integrations.deepspeed import is_deepspeed_zero3_enabled
from ...modeling_attn_mask_utils import _prepare_4d_attention_mask, _prepare_4d_causal_attention_mask
from ...modeling_outputs import (BaseModelOutput, BaseModelOutputWithPastAndCrossAttentions, Seq2SeqLMOutput, Seq2SeqModelOutput, Seq2SeqSpectrogramOutput)
from ...modeling_utils import PreTrainedModel
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_speecht5 import SpeechT5Config, SpeechT5HifiGanConfig
logger = logging.get_logger(__name__)
_HIDDEN_STATES_START_POSITION = 1
_CONFIG_FOR_DOC = "SpeechT5Config"
def shift_tokens_right(input_ids: torch.Tensor, pad_token_id: int, decoder_start_token_id: int):
    shifted_input_ids = input_ids.new_zeros(input_ids.shape)
    shifted_input_ids[:, 1:] = input_ids[:, :-1].clone()
    shifted_input_ids[:, 0] = decoder_start_token_id
    if pad_token_id is None: raise ValueError("self.model.config.pad_token_id has to be defined.")
    shifted_input_ids.masked_fill_(shifted_input_ids == -100, pad_token_id)
    return shifted_input_ids
def shift_spectrograms_right(input_values: torch.Tensor, reduction_factor: int = 1, attention_mask: Optional[torch.Tensor] = None):
    if reduction_factor > 1:
        input_values = input_values[:, reduction_factor - 1 :: reduction_factor]
        if attention_mask is not None: attention_mask = attention_mask[:, reduction_factor - 1 :: reduction_factor]
    shifted_input_values = input_values.new_zeros(input_values.shape)
    shifted_input_values[:, 1:] = input_values[:, :-1].clone()
    shifted_input_values.masked_fill_(shifted_input_values == -100.0, 0.0)
    return shifted_input_values, attention_mask
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
class SpeechT5NoLayerNormConvLayer(nn.Module):
    def __init__(self, config, layer_id=0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]
        self.conv = nn.Conv1d(self.in_conv_dim, self.out_conv_dim, kernel_size=config.conv_kernel[layer_id], stride=config.conv_stride[layer_id], bias=config.conv_bias)
        self.activation = ACT2FN[config.feat_extract_activation]
    def forward(self, hidden_states):
        hidden_states = self.conv(hidden_states)
        hidden_states = self.activation(hidden_states)
        return hidden_states
class SpeechT5LayerNormConvLayer(nn.Module):
    def __init__(self, config, layer_id=0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]
        self.conv = nn.Conv1d(self.in_conv_dim, self.out_conv_dim, kernel_size=config.conv_kernel[layer_id], stride=config.conv_stride[layer_id], bias=config.conv_bias)
        self.layer_norm = nn.LayerNorm(self.out_conv_dim, elementwise_affine=True)
        self.activation = ACT2FN[config.feat_extract_activation]
    def forward(self, hidden_states):
        hidden_states = self.conv(hidden_states)
        hidden_states = hidden_states.transpose(-2, -1)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = hidden_states.transpose(-2, -1)
        hidden_states = self.activation(hidden_states)
        return hidden_states
class SpeechT5GroupNormConvLayer(nn.Module):
    def __init__(self, config, layer_id=0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]
        self.conv = nn.Conv1d(self.in_conv_dim, self.out_conv_dim, kernel_size=config.conv_kernel[layer_id], stride=config.conv_stride[layer_id], bias=config.conv_bias)
        self.activation = ACT2FN[config.feat_extract_activation]
        self.layer_norm = nn.GroupNorm(num_groups=self.out_conv_dim, num_channels=self.out_conv_dim, affine=True)
    def forward(self, hidden_states):
        hidden_states = self.conv(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.activation(hidden_states)
        return hidden_states
class SpeechT5SinusoidalPositionalEmbedding(nn.Module):
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
class SpeechT5PositionalConvEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.conv = nn.Conv1d(config.hidden_size, config.hidden_size, kernel_size=config.num_conv_pos_embeddings, padding=config.num_conv_pos_embeddings // 2, groups=config.num_conv_pos_embedding_groups)
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        if is_deepspeed_zero3_enabled():
            import deepspeed
            with deepspeed.zero.GatheredParameters(self.conv.weight, modifier_rank=0): self.conv = weight_norm(self.conv, name="weight", dim=2)
            if hasattr(self.conv, "parametrizations"):
                weight_g = self.conv.parametrizations.weight.original0
                weight_v = self.conv.parametrizations.weight.original1
            else:
                weight_g = self.conv.weight_g
                weight_v = self.conv.weight_v
            deepspeed.zero.register_external_parameter(self, weight_v)
            deepspeed.zero.register_external_parameter(self, weight_g)
        else: self.conv = weight_norm(self.conv, name="weight", dim=2)
        self.padding = SpeechT5SamePadLayer(config.num_conv_pos_embeddings)
        self.activation = ACT2FN[config.feat_extract_activation]
    def forward(self, hidden_states):
        hidden_states = hidden_states.transpose(1, 2)
        hidden_states = self.conv(hidden_states)
        hidden_states = self.padding(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = hidden_states.transpose(1, 2)
        return hidden_states
class SpeechT5ScaledPositionalEncoding(nn.Module):
    def __init__(self, dropout, dim, max_len=5000):
        pe = torch.zeros(max_len, dim)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp((torch.arange(0, dim, 2, dtype=torch.int64).float() * -(math.log(10000.0) / dim)))
        pe[:, 0::2] = torch.sin(position.float() * div_term)
        pe[:, 1::2] = torch.cos(position.float() * div_term)
        pe = pe.unsqueeze(0)
        super().__init__()
        self.register_buffer("pe", pe, persistent=False)
        self.dropout = nn.Dropout(p=dropout)
        self.dim = dim
        self.alpha = torch.nn.Parameter(torch.tensor(1.0))
    def forward(self, emb):
        emb = emb + self.alpha * self.pe[:, : emb.size(1)]
        emb = self.dropout(emb)
        return emb
class SpeechT5RelativePositionalEncoding(torch.nn.Module):
    def __init__(self, dim, max_length=1000):
        super().__init__()
        self.dim = dim
        self.max_length = max_length
        self.pe_k = torch.nn.Embedding(2 * max_length, dim)
    def forward(self, hidden_states):
        seq_len = hidden_states.shape[1]
        pos_seq = torch.arange(0, seq_len).long().to(hidden_states.device)
        pos_seq = pos_seq[:, None] - pos_seq[None, :]
        pos_seq[pos_seq < -self.max_length] = -self.max_length
        pos_seq[pos_seq >= self.max_length] = self.max_length - 1
        pos_seq = pos_seq + self.max_length
        return self.pe_k(pos_seq)
class SpeechT5SamePadLayer(nn.Module):
    def __init__(self, num_conv_pos_embeddings):
        super().__init__()
        self.num_pad_remove = 1 if num_conv_pos_embeddings % 2 == 0 else 0
    def forward(self, hidden_states):
        if self.num_pad_remove > 0: hidden_states = hidden_states[:, :, : -self.num_pad_remove]
        return hidden_states
class SpeechT5FeatureEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.feat_extract_norm == "group": conv_layers = [SpeechT5GroupNormConvLayer(config, layer_id=0)] + [SpeechT5NoLayerNormConvLayer(config, layer_id=i + 1) for i in range(config.num_feat_extract_layers - 1)]
        elif config.feat_extract_norm == "layer": conv_layers = [SpeechT5LayerNormConvLayer(config, layer_id=i) for i in range(config.num_feat_extract_layers)]
        else: raise ValueError(f"`config.feat_extract_norm` is {config.feat_extract_norm}, but has to be one of ['group', 'layer']")
        self.conv_layers = nn.ModuleList(conv_layers)
        self.gradient_checkpointing = False
        self._requires_grad = True
    def _freeze_parameters(self):
        for param in self.parameters(): param.requires_grad = False
        self._requires_grad = False
    def forward(self, input_values):
        hidden_states = input_values[:, None]
        if self._requires_grad and self.training: hidden_states.requires_grad = True
        for conv_layer in self.conv_layers:
            if self._requires_grad and self.gradient_checkpointing and self.training: hidden_states = self._gradient_checkpointing_func(conv_layer.__call__, hidden_states)
            else: hidden_states = conv_layer(hidden_states)
        return hidden_states
class SpeechT5FeatureProjection(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layer_norm = nn.LayerNorm(config.conv_dim[-1], eps=config.layer_norm_eps)
        self.projection = nn.Linear(config.conv_dim[-1], config.hidden_size)
        self.dropout = nn.Dropout(config.feat_proj_dropout)
    def forward(self, hidden_states):
        norm_hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.projection(norm_hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states, norm_hidden_states
class SpeechT5SpeechEncoderPrenet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.feature_encoder = SpeechT5FeatureEncoder(config)
        self.feature_projection = SpeechT5FeatureProjection(config)
        if config.mask_time_prob > 0.0 or config.mask_feature_prob > 0.0: self.masked_spec_embed = nn.Parameter(torch.Tensor(config.hidden_size).uniform_())
        self.pos_conv_embed = SpeechT5PositionalConvEmbedding(config)
        self.pos_sinusoidal_embed = SpeechT5SinusoidalPositionalEmbedding(config.max_speech_positions + config.pad_token_id + 1, config.hidden_size, config.pad_token_id)
    def freeze_feature_encoder(self): self.feature_encoder._freeze_parameters()
    def forward(self, input_values: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, mask_time_indices: Optional[torch.FloatTensor] = None):
        extract_features = self.feature_encoder(input_values)
        extract_features = extract_features.transpose(1, 2)
        if attention_mask is not None: attention_mask = self._get_feature_vector_attention_mask(extract_features.shape[1], attention_mask)
        hidden_states, extract_features = self.feature_projection(extract_features)
        hidden_states = self._mask_hidden_states(hidden_states, mask_time_indices=mask_time_indices, attention_mask=attention_mask)
        positional_conv_embedding = self.pos_conv_embed(hidden_states)
        hidden_states = hidden_states + positional_conv_embedding
        if attention_mask is not None: padding_mask = attention_mask.ne(1).long()
        else: padding_mask = torch.zeros(hidden_states.shape[:2], dtype=torch.long, device=hidden_states.device)
        positional_sinusoidal_embeddings = self.pos_sinusoidal_embed(padding_mask)
        hidden_states = hidden_states + positional_sinusoidal_embeddings
        return hidden_states, attention_mask
    def _get_feature_vector_attention_mask(self, feature_vector_length: int, attention_mask: torch.LongTensor):
        non_padded_lengths = attention_mask.cumsum(dim=-1)[:, -1]
        output_lengths = self._get_feat_extract_output_lengths(non_padded_lengths).to(torch.long)
        batch_size = attention_mask.shape[0]
        attention_mask = torch.zeros((batch_size, feature_vector_length), dtype=attention_mask.dtype, device=attention_mask.device)
        attention_mask[(torch.arange(attention_mask.shape[0], device=attention_mask.device), output_lengths - 1)] = 1
        attention_mask = attention_mask.flip([-1]).cumsum(-1).flip([-1]).bool()
        return attention_mask
    def _get_feat_extract_output_lengths(self, input_lengths: Union[torch.LongTensor, int]):
        def _conv_out_length(input_length, kernel_size, stride): return torch.div(input_length - kernel_size, stride, rounding_mode="floor") + 1
        for kernel_size, stride in zip(self.config.conv_kernel, self.config.conv_stride): input_lengths = _conv_out_length(input_lengths, kernel_size, stride)
        return input_lengths
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
            mask_feature_indices = _compute_mask_indices((batch_size, hidden_size), mask_prob=self.config.mask_feature_prob,
            mask_length=self.config.mask_feature_length, min_masks=self.config.mask_feature_min_masks)
            mask_feature_indices = torch.tensor(mask_feature_indices, device=hidden_states.device, dtype=torch.bool)
            mask_feature_indices = mask_feature_indices[:, None].expand(-1, sequence_length, -1)
            hidden_states[mask_feature_indices] = 0
        return hidden_states
class SpeechT5SpeechDecoderPrenet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([nn.Linear(config.num_mel_bins if i == 0 else config.speech_decoder_prenet_units, config.speech_decoder_prenet_units) for i in range(config.speech_decoder_prenet_layers)])
        self.final_layer = nn.Linear(config.speech_decoder_prenet_units, config.hidden_size)
        self.encode_positions = SpeechT5ScaledPositionalEncoding(config.positional_dropout, config.hidden_size, config.max_speech_positions)
        self.speaker_embeds_layer = nn.Linear(config.speaker_embedding_dim + config.hidden_size, config.hidden_size)
    def _consistent_dropout(self, inputs_embeds, p):
        mask = torch.bernoulli(inputs_embeds[0], p=p)
        all_masks = mask.unsqueeze(0).repeat(inputs_embeds.size(0), 1, 1)
        return torch.where(all_masks == 1, inputs_embeds, 0) * 1 / (1 - p)
    def forward(self, input_values: torch.Tensor, speaker_embeddings: Optional[torch.Tensor] = None):
        inputs_embeds = input_values
        for layer in self.layers:
            inputs_embeds = nn.functional.relu(layer(inputs_embeds))
            inputs_embeds = self._consistent_dropout(inputs_embeds, self.config.speech_decoder_prenet_dropout)
        inputs_embeds = self.final_layer(inputs_embeds)
        inputs_embeds = self.encode_positions(inputs_embeds)
        if speaker_embeddings is not None:
            speaker_embeddings = nn.functional.normalize(speaker_embeddings)
            speaker_embeddings = speaker_embeddings.unsqueeze(1).expand(-1, inputs_embeds.size(1), -1)
            inputs_embeds = torch.cat([inputs_embeds, speaker_embeddings], dim=-1)
            inputs_embeds = nn.functional.relu(self.speaker_embeds_layer(inputs_embeds))
        return inputs_embeds
class SpeechT5BatchNormConvLayer(nn.Module):
    def __init__(self, config, layer_id=0):
        super().__init__()
        if layer_id == 0: in_conv_dim = config.num_mel_bins
        else: in_conv_dim = config.speech_decoder_postnet_units
        if layer_id == config.speech_decoder_postnet_layers - 1: out_conv_dim = config.num_mel_bins
        else: out_conv_dim = config.speech_decoder_postnet_units
        self.conv = nn.Conv1d(in_conv_dim, out_conv_dim, kernel_size=config.speech_decoder_postnet_kernel, stride=1, padding=(config.speech_decoder_postnet_kernel - 1) // 2, bias=False)
        self.batch_norm = nn.BatchNorm1d(out_conv_dim)
        if layer_id < config.speech_decoder_postnet_layers - 1: self.activation = nn.Tanh()
        else: self.activation = None
        self.dropout = nn.Dropout(config.speech_decoder_postnet_dropout)
    def forward(self, hidden_states):
        hidden_states = self.conv(hidden_states)
        hidden_states = self.batch_norm(hidden_states)
        if self.activation is not None: hidden_states = self.activation(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class SpeechT5SpeechDecoderPostnet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.feat_out = nn.Linear(config.hidden_size, config.num_mel_bins * config.reduction_factor)
        self.prob_out = nn.Linear(config.hidden_size, config.reduction_factor)
        self.layers = nn.ModuleList([SpeechT5BatchNormConvLayer(config, i) for i in range(config.speech_decoder_postnet_layers)])
    def forward(self, hidden_states: torch.Tensor):
        outputs_before_postnet = self.feat_out(hidden_states).view(hidden_states.size(0), -1, self.config.num_mel_bins)
        outputs_after_postnet = self.postnet(outputs_before_postnet)
        logits = self.prob_out(hidden_states).view(hidden_states.size(0), -1)
        return outputs_before_postnet, outputs_after_postnet, logits
    def postnet(self, hidden_states: torch.Tensor):
        layer_output = hidden_states.transpose(1, 2)
        for layer in self.layers: layer_output = layer(layer_output)
        return hidden_states + layer_output.transpose(1, 2)
class SpeechT5TextEncoderPrenet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, config.pad_token_id)
        self.encode_positions = SpeechT5ScaledPositionalEncoding(config.positional_dropout, config.hidden_size, config.max_text_positions)
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    def forward(self, input_ids: torch.Tensor):
        inputs_embeds = self.embed_tokens(input_ids)
        inputs_embeds = self.encode_positions(inputs_embeds)
        return inputs_embeds
class SpeechT5TextDecoderPrenet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.dropout = nn.Dropout(config.positional_dropout)
        self.embed_scale = math.sqrt(config.hidden_size) if config.scale_embedding else 1.0
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, config.pad_token_id)
        self.embed_positions = SpeechT5SinusoidalPositionalEmbedding(config.max_text_positions + config.pad_token_id + 1, config.hidden_size, config.pad_token_id)
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None):
        if input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
        else: raise ValueError("You have to specify `decoder_input_ids`")
        past_key_values_length = past_key_values[0][0].shape[2] if past_key_values is not None else 0
        positions = self.embed_positions(input_ids, past_key_values_length)
        inputs_embeds = self.embed_tokens(input_ids) * self.embed_scale
        inputs_embeds += positions
        inputs_embeds = self.dropout(inputs_embeds)
        return inputs_embeds, attention_mask
class SpeechT5TextDecoderPostnet(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
    def forward(self, hidden_states: torch.Tensor): return self.lm_head(hidden_states)
    def get_output_embeddings(self): return self.lm_head
    def set_output_embeddings(self, new_embeddings): self.lm_head = new_embeddings
class SpeechT5Attention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        if (self.head_dim * num_heads) != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {num_heads}).")
        self.scaling = self.head_dim**-0.5
        self.is_decoder = is_decoder
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None,
    attention_mask: Optional[torch.Tensor] = None, layer_head_mask: Optional[torch.Tensor] = None, position_bias: Optional[torch.Tensor] = None,
    output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scaling
        if is_cross_attention and past_key_value is not None:
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
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        if position_bias is not None:
            reshape_q = query_states.contiguous().view(bsz * self.num_heads, -1, self.head_dim).transpose(0, 1)
            rel_pos_bias = torch.matmul(reshape_q, position_bias.transpose(-2, -1))
            rel_pos_bias = rel_pos_bias.transpose(0, 1).view(bsz * self.num_heads, position_bias.size(0), position_bias.size(1))
            attn_weights += rel_pos_bias
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
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped, past_key_value
class SpeechT5FeedForward(nn.Module):
    def __init__(self, config, intermediate_size):
        super().__init__()
        self.intermediate_dropout = nn.Dropout(config.activation_dropout)
        self.intermediate_dense = nn.Linear(config.hidden_size, intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
        self.output_dense = nn.Linear(intermediate_size, config.hidden_size)
        self.output_dropout = nn.Dropout(config.hidden_dropout)
    def forward(self, hidden_states):
        hidden_states = self.intermediate_dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        hidden_states = self.intermediate_dropout(hidden_states)
        hidden_states = self.output_dense(hidden_states)
        hidden_states = self.output_dropout(hidden_states)
        return hidden_states
class SpeechT5EncoderLayer(nn.Module):
    def __init__(self, config: SpeechT5Config):
        super().__init__()
        self.attention = SpeechT5Attention(embed_dim=config.hidden_size, num_heads=config.encoder_attention_heads, dropout=config.attention_dropout, is_decoder=False)
        self.dropout = nn.Dropout(config.hidden_dropout)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.feed_forward = SpeechT5FeedForward(config, config.encoder_ffn_dim)
        self.final_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, layer_head_mask: Optional[torch.Tensor] = None, position_bias: Optional[torch.Tensor] = None, output_attentions: bool = False):
        residual = hidden_states
        hidden_states, attn_weights, _ = self.attention(hidden_states=hidden_states, attention_mask=attention_mask, layer_head_mask=layer_head_mask, position_bias=position_bias, output_attentions=output_attentions)
        hidden_states = self.dropout(hidden_states)
        hidden_states = residual + hidden_states
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = hidden_states + self.feed_forward(hidden_states)
        hidden_states = self.final_layer_norm(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class SpeechT5DecoderLayer(nn.Module):
    def __init__(self, config: SpeechT5Config):
        super().__init__()
        self.self_attn = SpeechT5Attention(embed_dim=config.hidden_size, num_heads=config.decoder_attention_heads, dropout=config.attention_dropout, is_decoder=True)
        self.dropout = nn.Dropout(config.hidden_dropout)
        self.self_attn_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.encoder_attn = SpeechT5Attention(config.hidden_size, config.decoder_attention_heads, dropout=config.attention_dropout, is_decoder=True)
        self.encoder_attn_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.feed_forward = SpeechT5FeedForward(config, config.decoder_ffn_dim)
        self.final_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, encoder_hidden_states: Optional[torch.Tensor] = None,
    encoder_attention_mask: Optional[torch.Tensor] = None, layer_head_mask: Optional[torch.Tensor] = None, cross_attn_layer_head_mask: Optional[torch.Tensor] = None,
    past_key_value: Optional[Tuple[torch.Tensor]] = None, output_attentions: Optional[bool] = False, use_cache: Optional[bool] = True):
        residual = hidden_states
        self_attn_past_key_value = past_key_value[:2] if past_key_value is not None else None
        hidden_states, self_attn_weights, present_key_value = self.self_attn(hidden_states=hidden_states, past_key_value=self_attn_past_key_value, attention_mask=attention_mask,
        layer_head_mask=layer_head_mask, output_attentions=output_attentions)
        hidden_states = self.dropout(hidden_states)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        cross_attn_present_key_value = None
        cross_attn_weights = None
        if encoder_hidden_states is not None:
            residual = hidden_states
            cross_attn_past_key_value = past_key_value[-2:] if past_key_value is not None else None
            hidden_states, cross_attn_weights, cross_attn_present_key_value = self.encoder_attn(hidden_states=hidden_states, key_value_states=encoder_hidden_states,
            attention_mask=encoder_attention_mask, layer_head_mask=cross_attn_layer_head_mask, past_key_value=cross_attn_past_key_value, output_attentions=output_attentions)
            hidden_states = self.dropout(hidden_states)
            hidden_states = residual + hidden_states
            hidden_states = self.encoder_attn_layer_norm(hidden_states)
            present_key_value = present_key_value + cross_attn_present_key_value
        hidden_states = hidden_states + self.feed_forward(hidden_states)
        hidden_states = self.final_layer_norm(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights, cross_attn_weights)
        if use_cache: outputs += (present_key_value,)
        return outputs
class SpeechT5PreTrainedModel(PreTrainedModel):
    config_class = SpeechT5Config
    base_model_prefix = "speecht5"
    main_input_name = "input_values"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, SpeechT5PositionalConvEmbedding):
            nn.init.normal_(module.conv.weight, mean=0, std=2 * math.sqrt(1 / (module.conv.kernel_size[0] * module.conv.in_channels)))
            nn.init.constant_(module.conv.bias, 0)
        elif isinstance(module, SpeechT5FeatureProjection):
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
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
class SpeechT5Encoder(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout)
        self.layerdrop = config.encoder_layerdrop
        self.layers = nn.ModuleList([SpeechT5EncoderLayer(config) for _ in range(config.encoder_layers)])
        self.embed_positions = SpeechT5RelativePositionalEncoding(config.hidden_size // config.encoder_attention_heads, config.encoder_max_relative_position)
        self.gradient_checkpointing = False
        self.post_init()
    def forward(self, hidden_states: torch.FloatTensor, attention_mask: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if attention_mask is not None: attention_mask = _prepare_4d_attention_mask(attention_mask, hidden_states.dtype)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.dropout(hidden_states)
        position_bias = self.embed_positions(hidden_states)
        deepspeed_zero3_is_enabled = is_deepspeed_zero3_enabled()
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        if head_mask is not None:
            if head_mask.size()[0] != len(self.layers): raise ValueError(f"The head_mask should be specified for {len(self.layers)} layers, but it is for {head_mask.size()[0]}.")
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            skip_the_layer = False
            if self.training:
                dropout_probability = torch.rand([])
                skip_the_layer = dropout_probability < self.layerdrop
            if not skip_the_layer or deepspeed_zero3_is_enabled:
                if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states,
                attention_mask, (head_mask[idx] if head_mask is not None else None), position_bias, output_attentions)
                else: layer_outputs = encoder_layer(hidden_states, attention_mask=attention_mask, position_bias=position_bias,
                layer_head_mask=(head_mask[idx] if head_mask is not None else None), output_attentions=output_attentions)
                hidden_states = layer_outputs[0]
            if skip_the_layer: layer_outputs = (None, None)
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions)
class SpeechT5EncoderWithSpeechPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.prenet = SpeechT5SpeechEncoderPrenet(config)
        self.wrapped_encoder = SpeechT5Encoder(config)
        self.post_init()
    def forward(self, input_values: torch.FloatTensor, attention_mask: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        hidden_states, attention_mask = self.prenet(input_values, attention_mask)
        outputs = self.wrapped_encoder(hidden_states=hidden_states, attention_mask=attention_mask, head_mask=head_mask, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
class SpeechT5EncoderWithTextPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.prenet = SpeechT5TextEncoderPrenet(config)
        self.wrapped_encoder = SpeechT5Encoder(config)
        self.post_init()
    def get_input_embeddings(self): return self.prenet.get_input_embeddings()
    def set_input_embeddings(self, value): self.prenet.set_input_embeddings(value)
    def forward(self, input_values: torch.FloatTensor, attention_mask: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        hidden_states = self.prenet(input_values)
        outputs = self.wrapped_encoder(hidden_states=hidden_states, attention_mask=attention_mask, head_mask=head_mask, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
class SpeechT5EncoderWithoutPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.wrapped_encoder = SpeechT5Encoder(config)
        self.post_init()
    def forward(self, input_values: torch.FloatTensor, attention_mask: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        return self.wrapped_encoder(hidden_states=input_values, attention_mask=attention_mask, head_mask=head_mask, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
class SpeechT5Decoder(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.layerdrop = config.decoder_layerdrop
        self.layers = nn.ModuleList([SpeechT5DecoderLayer(config) for _ in range(config.decoder_layers)])
        self.gradient_checkpointing = False
        self.post_init()
    def forward(self, hidden_states: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.Tensor] = None, cross_attn_head_mask: Optional[torch.Tensor] = None,
    past_key_values: Optional[List[torch.FloatTensor]] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPastAndCrossAttentions]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        input_shape = hidden_states.size()[:-1]
        past_key_values_length = past_key_values[0][0].shape[2] if past_key_values is not None else 0
        attention_mask = _prepare_4d_causal_attention_mask(attention_mask, input_shape, hidden_states, past_key_values_length)
        if encoder_hidden_states is not None and encoder_attention_mask is not None: encoder_attention_mask = _prepare_4d_attention_mask(encoder_attention_mask, hidden_states.dtype, tgt_len=input_shape[-1])
        deepspeed_zero3_is_enabled = is_deepspeed_zero3_enabled()
        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once("`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...")
                use_cache = False
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        next_decoder_cache = () if use_cache else None
        for attn_mask, mask_name in zip([head_mask, cross_attn_head_mask], ["head_mask", "cross_attn_head_mask"]):
            if attn_mask is not None:
                if attn_mask.size()[0] != (len(self.layers)): raise ValueError(f"The `{mask_name}` should be specified for {len(self.layers)} layers, but it is for {head_mask.size()[0]}.")
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            skip_the_layer = False
            if self.training:
                dropout_probability = torch.rand([])
                skip_the_layer = dropout_probability < self.layerdrop
            if skip_the_layer and not deepspeed_zero3_is_enabled: continue
            past_key_value = past_key_values[idx] if past_key_values is not None else None
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, attention_mask,
            encoder_hidden_states, encoder_attention_mask, head_mask[idx] if head_mask is not None else None, cross_attn_head_mask[idx] if cross_attn_head_mask is not None else None,
            None, output_attentions, use_cache)
            else: layer_outputs = decoder_layer(hidden_states, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
            layer_head_mask=(head_mask[idx] if head_mask is not None else None), cross_attn_layer_head_mask=(cross_attn_head_mask[idx] if cross_attn_head_mask is not None else None),
            past_key_value=past_key_value, output_attentions=output_attentions, use_cache=use_cache)
            hidden_states = layer_outputs[0]
            if use_cache: next_decoder_cache += (layer_outputs[3 if output_attentions else 1],)
            if output_attentions:
                all_self_attentions = all_self_attentions + (layer_outputs[1],)
                if encoder_hidden_states is not None: all_cross_attentions = all_cross_attentions + (layer_outputs[2],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        next_cache = next_decoder_cache if use_cache else None
        if not return_dict: return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attentions, all_cross_attentions] if v is not None)
        return BaseModelOutputWithPastAndCrossAttentions(last_hidden_state=hidden_states, past_key_values=next_cache, hidden_states=all_hidden_states,
        attentions=all_self_attentions, cross_attentions=all_cross_attentions)
class SpeechT5DecoderWithSpeechPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.prenet = SpeechT5SpeechDecoderPrenet(config)
        self.wrapped_decoder = SpeechT5Decoder(config)
        self.post_init()
    def forward(self, input_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.LongTensor] = None, speaker_embeddings: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPastAndCrossAttentions]:
        decoder_hidden_states = self.prenet(input_values, speaker_embeddings)
        outputs = self.wrapped_decoder(hidden_states=decoder_hidden_states, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
        head_mask=head_mask, cross_attn_head_mask=cross_attn_head_mask, past_key_values=past_key_values, use_cache=use_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
class SpeechT5DecoderWithTextPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.prenet = SpeechT5TextDecoderPrenet(config)
        self.wrapped_decoder = SpeechT5Decoder(config)
        self.post_init()
    def get_input_embeddings(self): return self.prenet.get_input_embeddings()
    def set_input_embeddings(self, value): self.prenet.set_input_embeddings(value)
    def forward(self, input_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.Tensor] = None, cross_attn_head_mask: Optional[torch.Tensor] = None,
    past_key_values: Optional[List[torch.FloatTensor]] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPastAndCrossAttentions]:
        decoder_hidden_states, attention_mask = self.prenet(input_values, attention_mask, past_key_values)
        outputs = self.wrapped_decoder(hidden_states=decoder_hidden_states, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states,
        encoder_attention_mask=encoder_attention_mask, head_mask=head_mask, cross_attn_head_mask=cross_attn_head_mask, past_key_values=past_key_values,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
class SpeechT5DecoderWithoutPrenet(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        self.wrapped_decoder = SpeechT5Decoder(config)
        self.post_init()
    def forward(self, input_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, encoder_hidden_states: Optional[torch.FloatTensor] = None,
    encoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.Tensor] = None, cross_attn_head_mask: Optional[torch.Tensor] = None,
    past_key_values: Optional[List[torch.FloatTensor]] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPastAndCrossAttentions]:
        outputs = self.wrapped_decoder(hidden_states=input_values, attention_mask=attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
        head_mask=head_mask, cross_attn_head_mask=cross_attn_head_mask, past_key_values=past_key_values, use_cache=use_cache, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
class SpeechT5GuidedMultiheadAttentionLoss(nn.Module):
    def __init__(self, config: SpeechT5Config):
        super().__init__()
        self.sigma = config.guided_attention_loss_sigma
        self.scale = config.guided_attention_loss_scale
    def forward(self, attentions: torch.FloatTensor, input_masks: torch.BoolTensor, output_masks: torch.BoolTensor) -> torch.Tensor:
        guided_attn_masks = self._make_guided_attention_masks(input_masks, output_masks, attentions.device)
        masks = output_masks.unsqueeze(-1) & input_masks.unsqueeze(-2)
        masks = masks.to(attentions.device).unsqueeze(1)
        losses = guided_attn_masks * attentions
        loss = torch.mean(losses.masked_select(masks))
        return self.scale * loss
    def _make_guided_attention_masks(self, input_masks, output_masks, device):
        input_lengths = input_masks.sum(-1)
        output_lengths = output_masks.sum(-1)
        guided_attn_masks = torch.zeros((len(input_masks), output_masks.shape[1], input_masks.shape[1]), device=device)
        for idx, (ilen, olen) in enumerate(zip(input_lengths, output_lengths)): guided_attn_masks[idx, :olen, :ilen] = self._make_guided_attention_mask(ilen, olen, self.sigma, device)
        return guided_attn_masks.unsqueeze(1)
    @staticmethod
    def _make_guided_attention_mask(input_length, output_length, sigma, device):
        grid_y, grid_x = torch.meshgrid(torch.arange(input_length, device=device), torch.arange(output_length, device=device), indexing="xy")
        grid_x = grid_x.float() / output_length
        grid_y = grid_y.float() / input_length
        return 1.0 - torch.exp(-((grid_y - grid_x) ** 2) / (2 * (sigma**2)))
class SpeechT5SpectrogramLoss(nn.Module):
    def __init__(self, config: SpeechT5Config):
        super().__init__()
        self.use_guided_attention_loss = config.use_guided_attention_loss
        self.guided_attention_loss_num_heads = config.guided_attention_loss_num_heads
        self.reduction_factor = config.reduction_factor
        self.l1_criterion = L1Loss()
        self.bce_criterion = BCEWithLogitsLoss(pos_weight=torch.tensor(5.0))
        if self.use_guided_attention_loss: self.attn_criterion = SpeechT5GuidedMultiheadAttentionLoss(config)
    def forward(self, attention_mask: torch.LongTensor, outputs_before_postnet: torch.FloatTensor, outputs_after_postnet: torch.FloatTensor, logits: torch.FloatTensor,
    labels: torch.FloatTensor, cross_attentions: Optional[torch.FloatTensor] = None) -> torch.Tensor:
        padding_mask = labels != -100.0
        labels = labels.masked_select(padding_mask)
        outputs_before_postnet = outputs_before_postnet.masked_select(padding_mask)
        outputs_after_postnet = outputs_after_postnet.masked_select(padding_mask)
        l1_loss = self.l1_criterion(outputs_after_postnet, labels) + self.l1_criterion(outputs_before_postnet, labels)
        masks = padding_mask[:, :, 0]
        stop_labels = torch.cat([~masks * 1.0, torch.ones(masks.size(0), 1).to(masks.device)], dim=1)
        stop_labels = stop_labels[:, 1:].masked_select(masks)
        logits = logits.masked_select(masks)
        bce_loss = self.bce_criterion(logits, stop_labels)
        loss = l1_loss + bce_loss
        if self.use_guided_attention_loss:
            attn = torch.cat([x[:, : self.guided_attention_loss_num_heads] for x in cross_attentions], dim=1)
            input_masks = attention_mask == 1
            output_masks = padding_mask[:, :, 0]
            if self.reduction_factor > 1: output_masks = output_masks[:, self.reduction_factor - 1 :: self.reduction_factor]
            attn_loss = self.attn_criterion(attn, input_masks, output_masks)
            loss += attn_loss
        return loss
SPEECHT5_BASE_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SpeechT5Config`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
        encoder ([`SpeechT5EncoderWithSpeechPrenet`] or [`SpeechT5EncoderWithTextPrenet`] or `None`):
            The Transformer encoder module that applies the appropiate speech or text encoder prenet. If `None`,
            [`SpeechT5EncoderWithoutPrenet`] will be used and the `input_values` are assumed to be hidden states.
        decoder ([`SpeechT5DecoderWithSpeechPrenet`] or [`SpeechT5DecoderWithTextPrenet`] or `None`):
            The Transformer decoder module that applies the appropiate speech or text decoder prenet. If `None`,
            [`SpeechT5DecoderWithoutPrenet`] will be used and the `decoder_input_values` are assumed to be hidden
            states.
"""
SPEECHT5_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SpeechT5Config`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
SPEECHT5_INPUTS_DOCSTRING = r"""
    Args:
        attention_mask (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing convolution and attention on padding token indices. Mask values selected in `[0,
            1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            <Tip warning={true}>
            `attention_mask` should only be passed if the corresponding processor has `config.return_attention_mask ==
            True`. For all models whose processor has `config.return_attention_mask == False`, `attention_mask` should
            *not* be passed to avoid degraded performance when doing batched inference. For such models
            `input_values` should simply be padded with 0 and passed without `attention_mask`. Be aware that these
            models also yield slightly different results depending on whether `input_values` is padded or not.
            </Tip>
        decoder_attention_mask (`torch.LongTensor` of shape `(batch_size, target_sequence_length)`, *optional*):
            Default behavior: generate a tensor that ignores pad tokens in `decoder_input_values`. Causal mask will
            also be used by default.
            If you want to change padding behavior, you should read [`SpeechT5Decoder._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
        head_mask (`torch.FloatTensor` of shape `(encoder_layers, encoder_attention_heads)`, *optional*):
            Mask to nullify selected heads of the attention modules in the encoder. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        decoder_head_mask (`torch.FloatTensor` of shape `(decoder_layers, decoder_attention_heads)`, *optional*):
            Mask to nullify selected heads of the attention modules in the decoder. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        cross_attn_head_mask (`torch.Tensor` of shape `(decoder_layers, decoder_attention_heads)`, *optional*):
            Mask to nullify selected heads of the cross-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        encoder_outputs (`tuple(tuple(torch.FloatTensor)`, *optional*):
            Tuple consists of (`last_hidden_state`, *optional*: `hidden_states`, *optional*: `attentions`)
            `last_hidden_state` of shape `(batch_size, sequence_length, hidden_size)`, *optional*) is a sequence of
            hidden-states at the output of the last layer of the encoder. Used in the cross-attention of the decoder.
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)` and 2 additional tensors of shape
            `(batch_size, num_heads, encoder_sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used (see `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_values` (those
            that don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_values` of shape `(batch_size, sequence_length)`. decoder_inputs_embeds (`torch.FloatTensor`
            of shape `(batch_size, target_sequence_length, hidden_size)`, *optional*): Optionally, instead of passing
            `decoder_input_values` you can choose to directly pass an embedded representation. If `past_key_values` is
            used, optionally only the last `decoder_inputs_embeds` have to be input (see `past_key_values`). This is
            useful if you want more control over how to convert `decoder_input_values` indices into associated vectors
            than the model's internal embedding lookup matrix.
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
@add_start_docstrings("The bare SpeechT5 Encoder-Decoder Model outputting raw hidden-states without any specific pre- or post-nets.", SPEECHT5_BASE_START_DOCSTRING)
class SpeechT5Model(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config, encoder: Optional[nn.Module] = None, decoder: Optional[nn.Module] = None):
        super().__init__(config)
        self.config = config
        self.encoder = SpeechT5EncoderWithoutPrenet(config) if encoder is None else encoder
        self.decoder = SpeechT5DecoderWithoutPrenet(config) if decoder is None else decoder
        self.post_init()
    def get_input_embeddings(self):
        if isinstance(self.encoder, SpeechT5EncoderWithTextPrenet): return self.encoder.get_input_embeddings()
        if isinstance(self.decoder, SpeechT5DecoderWithTextPrenet): return self.decoder.get_input_embeddings()
        return None
    def set_input_embeddings(self, value):
        if isinstance(self.encoder, SpeechT5EncoderWithTextPrenet): self.encoder.set_input_embeddings(value)
        if isinstance(self.decoder, SpeechT5DecoderWithTextPrenet): self.decoder.set_input_embeddings(value)
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def freeze_feature_encoder(self):
        if isinstance(self.encoder, SpeechT5EncoderWithSpeechPrenet): self.encoder.prenet.freeze_feature_encoder()
    @add_start_docstrings_to_model_forward(SPEECHT5_INPUTS_DOCSTRING)
    def forward(self, input_values: Optional[torch.Tensor] = None, attention_mask: Optional[torch.LongTensor] = None, decoder_input_values: Optional[torch.Tensor] = None,
    decoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    use_cache: Optional[bool] = None, speaker_embeddings: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], Seq2SeqModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if encoder_outputs is None: encoder_outputs = self.encoder(input_values=input_values, attention_mask=attention_mask, head_mask=head_mask, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, BaseModelOutput): encoder_outputs = BaseModelOutput(last_hidden_state=encoder_outputs[0], hidden_states=encoder_outputs[1] if len(encoder_outputs) > 1 else None,
        attentions=encoder_outputs[2] if len(encoder_outputs) > 2 else None)
        if attention_mask is not None and isinstance(self.encoder, SpeechT5EncoderWithSpeechPrenet): encoder_attention_mask = self.encoder.prenet._get_feature_vector_attention_mask(encoder_outputs[0].shape[1], attention_mask)
        else: encoder_attention_mask = attention_mask
        if isinstance(self.decoder, SpeechT5DecoderWithSpeechPrenet): decoder_args = {"speaker_embeddings": speaker_embeddings}
        else: decoder_args = {}
        decoder_outputs = self.decoder(input_values=decoder_input_values, attention_mask=decoder_attention_mask, encoder_hidden_states=encoder_outputs[0],
        encoder_attention_mask=encoder_attention_mask, head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, past_key_values=past_key_values,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, **decoder_args)
        if not return_dict: return decoder_outputs + encoder_outputs
        return Seq2SeqModelOutput(last_hidden_state=decoder_outputs.last_hidden_state, past_key_values=decoder_outputs.past_key_values, decoder_hidden_states=decoder_outputs.hidden_states,
        decoder_attentions=decoder_outputs.attentions, cross_attentions=decoder_outputs.cross_attentions, encoder_last_hidden_state=encoder_outputs.last_hidden_state,
        encoder_hidden_states=encoder_outputs.hidden_states, encoder_attentions=encoder_outputs.attentions)
@add_start_docstrings("SpeechT5 Model with a speech encoder and a text decoder.", SPEECHT5_START_DOCSTRING)
class SpeechT5ForSpeechToText(SpeechT5PreTrainedModel):
    _tied_weights_keys = ["text_decoder_postnet.lm_head.weight"]
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        if config.vocab_size is None: raise ValueError(f"You are trying to instantiate {self.__class__} with a configuration that does not define the vocabulary size of the language model head. Please instantiate the model as follows: `SpeechT5ForSpeechToText.from_pretrained(..., vocab_size=vocab_size)`. or define `vocab_size` of your model's configuration.")
        speech_encoder = SpeechT5EncoderWithSpeechPrenet(config)
        text_decoder = SpeechT5DecoderWithTextPrenet(config)
        self.speecht5 = SpeechT5Model(config, speech_encoder, text_decoder)
        self.text_decoder_postnet = SpeechT5TextDecoderPostnet(config)
        self.post_init()
    def get_encoder(self): return self.speecht5.get_encoder()
    def get_decoder(self): return self.speecht5.get_decoder()
    def freeze_feature_encoder(self): self.get_encoder().prenet.freeze_feature_encoder()
    def get_output_embeddings(self): return self.text_decoder_postnet.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.text_decoder_postnet.set_output_embeddings(new_embeddings)
    @add_start_docstrings_to_model_forward(SPEECHT5_INPUTS_DOCSTRING)
    def forward(self, input_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, decoder_input_ids: Optional[torch.LongTensor] = None,
    decoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    labels: Optional[torch.LongTensor] = None) -> Union[Tuple, Seq2SeqLMOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if labels is not None:
            if decoder_input_ids is None: decoder_input_ids = shift_tokens_right(labels, self.config.pad_token_id, self.config.decoder_start_token_id)
        outputs = self.speecht5(input_values=input_values, attention_mask=attention_mask, decoder_input_values=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
        head_mask=head_mask, decoder_head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, encoder_outputs=encoder_outputs, past_key_values=past_key_values,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=True)
        logits = self.text_decoder_postnet(outputs[0])
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.config.vocab_size), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return Seq2SeqLMOutput(loss=loss, logits=logits, past_key_values=outputs.past_key_values, decoder_hidden_states=outputs.decoder_hidden_states,
        decoder_attentions=outputs.decoder_attentions, cross_attentions=outputs.cross_attentions, encoder_last_hidden_state=outputs.encoder_last_hidden_state,
        encoder_hidden_states=outputs.encoder_hidden_states, encoder_attentions=outputs.encoder_attentions)
    def prepare_inputs_for_generation(self, decoder_input_ids, past_key_values=None, attention_mask=None, head_mask=None, decoder_head_mask=None, cross_attn_head_mask=None,
    use_cache=None, encoder_outputs=None, **kwargs):
        if past_key_values is not None:
            past_length = past_key_values[0][0].shape[2]
            if decoder_input_ids.shape[1] > past_length: remove_prefix_length = past_length
            else: remove_prefix_length = decoder_input_ids.shape[1] - 1
            decoder_input_ids = decoder_input_ids[:, remove_prefix_length:]
        return {"encoder_outputs": encoder_outputs, "past_key_values": past_key_values, "decoder_input_ids": decoder_input_ids, "attention_mask": attention_mask,
        "head_mask": head_mask, "decoder_head_mask": decoder_head_mask, "cross_attn_head_mask": cross_attn_head_mask, "use_cache": use_cache}
    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values: reordered_past += (tuple(past_state.index_select(0, beam_idx.to(past_state.device)) for past_state in layer_past),)
        return reordered_past
def _generate_speech(model: SpeechT5PreTrainedModel, input_values: torch.FloatTensor, speaker_embeddings: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None,
threshold: float = 0.5, minlenratio: float = 0.0, maxlenratio: float = 20.0, vocoder: Optional[nn.Module] = None, output_cross_attentions: bool = False,
return_output_lengths: bool = False) -> Union[torch.FloatTensor, Tuple[torch.FloatTensor, torch.FloatTensor]]:
    if speaker_embeddings is None: raise ValueError("`speaker_embeddings` must be specified.")
    if attention_mask is None: encoder_attention_mask = 1 - (input_values == model.config.pad_token_id).int()
    else: encoder_attention_mask = attention_mask
    bsz = input_values.size(0)
    encoder_out = model.speecht5.encoder(input_values=input_values, attention_mask=encoder_attention_mask, return_dict=True)
    encoder_last_hidden_state = encoder_out.last_hidden_state
    if isinstance(model.speecht5.encoder, SpeechT5EncoderWithSpeechPrenet): encoder_attention_mask = model.speecht5.encoder.prenet._get_feature_vector_attention_mask(encoder_out[0].shape[1], encoder_attention_mask)
    maxlen = int(encoder_last_hidden_state.size(1) * maxlenratio / model.config.reduction_factor)
    minlen = int(encoder_last_hidden_state.size(1) * minlenratio / model.config.reduction_factor)
    output_sequence = encoder_last_hidden_state.new_zeros(bsz, 1, model.config.num_mel_bins)
    spectrogram = []
    cross_attentions = []
    past_key_values = None
    idx = 0
    result_spectrogram = {}
    while True:
        idx += 1
        decoder_hidden_states = model.speecht5.decoder.prenet(output_sequence, speaker_embeddings)
        decoder_out = model.speecht5.decoder.wrapped_decoder(hidden_states=decoder_hidden_states[:, -1:], attention_mask=None, encoder_hidden_states=encoder_last_hidden_state,
        encoder_attention_mask=encoder_attention_mask, past_key_values=past_key_values, use_cache=True, output_attentions=output_cross_attentions, return_dict=True)
        if output_cross_attentions: cross_attentions.append(torch.cat(decoder_out.cross_attentions, dim=0))
        last_decoder_output = decoder_out.last_hidden_state.squeeze(1)
        past_key_values = decoder_out.past_key_values
        spectrum = model.speech_decoder_postnet.feat_out(last_decoder_output)
        spectrum = spectrum.view(bsz, model.config.reduction_factor, model.config.num_mel_bins)
        spectrogram.append(spectrum)
        new_spectrogram = spectrum[:, -1, :].view(bsz, 1, model.config.num_mel_bins)
        output_sequence = torch.cat((output_sequence, new_spectrogram), dim=1)
        prob = torch.sigmoid(model.speech_decoder_postnet.prob_out(last_decoder_output))
        if idx < minlen: continue
        else:
            if idx < maxlen:
                meet_thresholds = torch.sum(prob, dim=-1) >= threshold
                meet_indexes = torch.where(meet_thresholds)[0].tolist()
            else: meet_indexes = range(len(prob))
            meet_indexes = [i for i in meet_indexes if i not in result_spectrogram]
            if len(meet_indexes) > 0:
                spectrograms = torch.stack(spectrogram)
                spectrograms = spectrograms.transpose(0, 1).flatten(1, 2)
                spectrograms = model.speech_decoder_postnet.postnet(spectrograms)
                for meet_index in meet_indexes: result_spectrogram[meet_index] = spectrograms[meet_index]
            if len(result_spectrogram) >= bsz: break
    spectrograms = [result_spectrogram[i] for i in range(len(result_spectrogram))]
    if not return_output_lengths:
        spectrogram = spectrograms[0] if bsz == 1 else torch.nn.utils.rnn.pad_sequence(spectrograms, batch_first=True)
        if vocoder is not None: outputs = vocoder(spectrogram)
        else: outputs = spectrogram
        if output_cross_attentions:
            cross_attentions = torch.cat(cross_attentions, dim=2)
            if bsz > 1: cross_attentions = cross_attentions.view(bsz, int(cross_attentions.size(0) / bsz), *cross_attentions.size()[-3:])
            outputs = (outputs, cross_attentions)
    else:
        spectrogram_lengths = []
        for i in range(bsz): spectrogram_lengths.append(spectrograms[i].size(0))
        if vocoder is None:
            spectrograms = torch.nn.utils.rnn.pad_sequence(spectrograms, batch_first=True)
            outputs = (spectrograms, spectrogram_lengths)
        else:
            waveforms = []
            spectrograms = torch.nn.utils.rnn.pad_sequence(spectrograms, batch_first=True)
            waveforms = vocoder(spectrograms)
            waveform_lengths = [int(waveforms.size(1) / max(spectrogram_lengths)) * i for i in spectrogram_lengths]
            outputs = (waveforms, waveform_lengths)
        if output_cross_attentions:
            cross_attentions = torch.cat(cross_attentions, dim=2)
            cross_attentions = cross_attentions.view(bsz, int(cross_attentions.size(0) / bsz), *cross_attentions.size()[-3:])
            outputs = (*outputs, cross_attentions)
    return outputs
@add_start_docstrings("SpeechT5 Model with a text encoder and a speech decoder.", SPEECHT5_START_DOCSTRING)
class SpeechT5ForTextToSpeech(SpeechT5PreTrainedModel):
    main_input_name = "input_ids"
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        if config.vocab_size is None: raise ValueError(f"You are trying to instantiate {self.__class__} with a configuration that does not define the vocabulary size of the language model head. Please instantiate the model as follows: `SpeechT5ForTextToSpeech.from_pretrained(..., vocab_size=vocab_size)`. or define `vocab_size` of your model's configuration.")
        text_encoder = SpeechT5EncoderWithTextPrenet(config)
        speech_decoder = SpeechT5DecoderWithSpeechPrenet(config)
        self.speecht5 = SpeechT5Model(config, text_encoder, speech_decoder)
        self.speech_decoder_postnet = SpeechT5SpeechDecoderPostnet(config)
        self.post_init()
    def get_encoder(self): return self.speecht5.get_encoder()
    def get_decoder(self): return self.speecht5.get_decoder()
    @add_start_docstrings_to_model_forward(SPEECHT5_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.LongTensor] = None, decoder_input_values: Optional[torch.FloatTensor] = None,
    decoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    speaker_embeddings: Optional[torch.FloatTensor] = None, labels: Optional[torch.FloatTensor] = None, stop_labels: Optional[torch.Tensor] = None) -> Union[Tuple, Seq2SeqSpectrogramOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if labels is not None:
            if decoder_input_values is None: decoder_input_values, decoder_attention_mask = shift_spectrograms_right(labels, self.config.reduction_factor, decoder_attention_mask)
            if self.config.use_guided_attention_loss: output_attentions = True
        outputs = self.speecht5(input_values=input_ids, attention_mask=attention_mask, decoder_input_values=decoder_input_values, decoder_attention_mask=decoder_attention_mask,
        head_mask=head_mask, decoder_head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, encoder_outputs=encoder_outputs, past_key_values=past_key_values,
        use_cache=use_cache, speaker_embeddings=speaker_embeddings, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=True)
        outputs_before_postnet, outputs_after_postnet, logits = self.speech_decoder_postnet(outputs[0])
        loss = None
        if labels is not None:
            criterion = SpeechT5SpectrogramLoss(self.config)
            loss = criterion(attention_mask, outputs_before_postnet, outputs_after_postnet, logits, labels, outputs.cross_attentions)
        if not return_dict:
            output = (outputs_after_postnet,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return Seq2SeqSpectrogramOutput(loss=loss, spectrogram=outputs_after_postnet, past_key_values=outputs.past_key_values, decoder_hidden_states=outputs.decoder_hidden_states,
        decoder_attentions=outputs.decoder_attentions, cross_attentions=outputs.cross_attentions, encoder_last_hidden_state=outputs.encoder_last_hidden_state,
        encoder_hidden_states=outputs.encoder_hidden_states, encoder_attentions=outputs.encoder_attentions)
    @torch.no_grad()
    def generate(self, input_ids: torch.LongTensor, attention_mask: Optional[torch.LongTensor] = None, speaker_embeddings: Optional[torch.FloatTensor] = None,
    threshold: float = 0.5, minlenratio: float = 0.0, maxlenratio: float = 20.0, vocoder: Optional[nn.Module] = None, output_cross_attentions: bool = False,
    return_output_lengths: bool = False, **kwargs) -> Union[torch.FloatTensor, Tuple[torch.FloatTensor, torch.FloatTensor]]:
        if speaker_embeddings is not None:
            batch_size = input_ids.size(0)
            if speaker_embeddings.size(0) != batch_size:
                if speaker_embeddings.size(0) == 1: speaker_embeddings = speaker_embeddings.repeat(batch_size, 1)
                else: raise ValueError("The first dimension of speaker_embeddings must be either 1 or the same as batch_size.")
        return _generate_speech(self, input_ids, speaker_embeddings, attention_mask, threshold, minlenratio, maxlenratio, vocoder, output_cross_attentions, return_output_lengths)
    @torch.no_grad()
    def generate_speech(self, input_ids: torch.LongTensor, speaker_embeddings: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None,
    threshold: float = 0.5, minlenratio: float = 0.0, maxlenratio: float = 20.0, vocoder: Optional[nn.Module] = None, output_cross_attentions: bool = False,
    return_output_lengths: bool = False) -> Union[torch.FloatTensor, Tuple[torch.FloatTensor, torch.FloatTensor]]:
        if speaker_embeddings is not None:
            batch_size = input_ids.size(0)
            if speaker_embeddings.size(0) != batch_size:
                if speaker_embeddings.size(0) == 1: speaker_embeddings = speaker_embeddings.repeat(batch_size, 1)
                else: raise ValueError("The first dimension of speaker_embeddings must be either 1 or the same as batch size.")
        return _generate_speech(self, input_ids, speaker_embeddings, attention_mask, threshold, minlenratio, maxlenratio, vocoder, output_cross_attentions, return_output_lengths)
@add_start_docstrings("SpeechT5 Model with a speech encoder and a speech decoder.", SPEECHT5_START_DOCSTRING)
class SpeechT5ForSpeechToSpeech(SpeechT5PreTrainedModel):
    def __init__(self, config: SpeechT5Config):
        super().__init__(config)
        speech_encoder = SpeechT5EncoderWithSpeechPrenet(config)
        speech_decoder = SpeechT5DecoderWithSpeechPrenet(config)
        self.speecht5 = SpeechT5Model(config, speech_encoder, speech_decoder)
        self.speech_decoder_postnet = SpeechT5SpeechDecoderPostnet(config)
        self.post_init()
    def get_encoder(self): return self.speecht5.get_encoder()
    def get_decoder(self): return self.speecht5.get_decoder()
    def freeze_feature_encoder(self): self.get_encoder().prenet.freeze_feature_encoder()
    @add_start_docstrings_to_model_forward(SPEECHT5_INPUTS_DOCSTRING)
    def forward(self, input_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None, decoder_input_values: Optional[torch.FloatTensor] = None,
    decoder_attention_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, decoder_head_mask: Optional[torch.FloatTensor] = None,
    cross_attn_head_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    speaker_embeddings: Optional[torch.FloatTensor] = None, labels: Optional[torch.FloatTensor] = None,
    stop_labels: Optional[torch.Tensor] = None) -> Union[Tuple, Seq2SeqSpectrogramOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if labels is not None:
            if decoder_input_values is None: decoder_input_values, decoder_attention_mask = shift_spectrograms_right(labels, self.config.reduction_factor, decoder_attention_mask)
        outputs = self.speecht5(input_values=input_values, attention_mask=attention_mask, decoder_input_values=decoder_input_values, decoder_attention_mask=decoder_attention_mask,
        head_mask=head_mask, decoder_head_mask=decoder_head_mask, cross_attn_head_mask=cross_attn_head_mask, encoder_outputs=encoder_outputs, past_key_values=past_key_values,
        use_cache=use_cache, speaker_embeddings=speaker_embeddings, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=True)
        _, spectrogram, logits = self.speech_decoder_postnet(outputs[0])
        loss = None
        if not return_dict:
            output = (spectrogram,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return Seq2SeqSpectrogramOutput(loss=loss, spectrogram=spectrogram, past_key_values=outputs.past_key_values, decoder_hidden_states=outputs.decoder_hidden_states,
        decoder_attentions=outputs.decoder_attentions, cross_attentions=outputs.cross_attentions, encoder_last_hidden_state=outputs.encoder_last_hidden_state,
        encoder_hidden_states=outputs.encoder_hidden_states, encoder_attentions=outputs.encoder_attentions)
    @torch.no_grad()
    def generate_speech(self, input_values: torch.FloatTensor, speaker_embeddings: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None,
    threshold: float = 0.5, minlenratio: float = 0.0, maxlenratio: float = 20.0, vocoder: Optional[nn.Module] = None, output_cross_attentions: bool = False,
    return_output_lengths: bool = False) -> torch.FloatTensor:
        if speaker_embeddings is None: speaker_embeddings = torch.zeros((1, 512), device=input_values.device)
        return _generate_speech(self, input_values, speaker_embeddings, attention_mask, threshold, minlenratio, maxlenratio, vocoder, output_cross_attentions, return_output_lengths)
HIFIGAN_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SpeechT5HifiGanConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
class HifiGanResidualBlock(nn.Module):
    def __init__(self, channels, kernel_size=3, dilation=(1, 3, 5), leaky_relu_slope=0.1):
        super().__init__()
        self.leaky_relu_slope = leaky_relu_slope
        self.convs1 = nn.ModuleList([nn.Conv1d(channels, channels, kernel_size, stride=1, dilation=dilation[i], padding=self.get_padding(kernel_size, dilation[i])) for i in range(len(dilation))])
        self.convs2 = nn.ModuleList([nn.Conv1d(channels, channels, kernel_size, stride=1, dilation=1, padding=self.get_padding(kernel_size, 1)) for _ in range(len(dilation))])
    def get_padding(self, kernel_size, dilation=1): return (kernel_size * dilation - dilation) // 2
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        for layer in self.convs1: weight_norm(layer)
        for layer in self.convs2: weight_norm(layer)
    def remove_weight_norm(self):
        for layer in self.convs1: nn.utils.remove_weight_norm(layer)
        for layer in self.convs2: nn.utils.remove_weight_norm(layer)
    def forward(self, hidden_states):
        for conv1, conv2 in zip(self.convs1, self.convs2):
            residual = hidden_states
            hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
            hidden_states = conv1(hidden_states)
            hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
            hidden_states = conv2(hidden_states)
            hidden_states = hidden_states + residual
        return hidden_states
@add_start_docstrings("HiFi-GAN vocoder.", HIFIGAN_START_DOCSTRING)
class SpeechT5HifiGan(PreTrainedModel):
    config_class = SpeechT5HifiGanConfig
    main_input_name = "spectrogram"
    def __init__(self, config: SpeechT5HifiGanConfig):
        super().__init__(config)
        self.num_kernels = len(config.resblock_kernel_sizes)
        self.num_upsamples = len(config.upsample_rates)
        self.conv_pre = nn.Conv1d(config.model_in_dim, config.upsample_initial_channel, kernel_size=7, stride=1, padding=3)
        self.upsampler = nn.ModuleList()
        for i, (upsample_rate, kernel_size) in enumerate(zip(config.upsample_rates, config.upsample_kernel_sizes)): self.upsampler.append(nn.ConvTranspose1d(config.upsample_initial_channel // (2**i),
        config.upsample_initial_channel // (2 ** (i + 1)), kernel_size=kernel_size, stride=upsample_rate, padding=(kernel_size - upsample_rate) // 2))
        self.resblocks = nn.ModuleList()
        for i in range(len(self.upsampler)):
            channels = config.upsample_initial_channel // (2 ** (i + 1))
            for kernel_size, dilation in zip(config.resblock_kernel_sizes, config.resblock_dilation_sizes): self.resblocks.append(HifiGanResidualBlock(channels, kernel_size, dilation, config.leaky_relu_slope))
        self.conv_post = nn.Conv1d(channels, 1, kernel_size=7, stride=1, padding=3)
        self.register_buffer("mean", torch.zeros(config.model_in_dim))
        self.register_buffer("scale", torch.ones(config.model_in_dim))
        self.post_init()
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv1d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv_pre)
        for layer in self.upsampler: weight_norm(layer)
        for layer in self.resblocks: layer.apply_weight_norm()
        weight_norm(self.conv_post)
    def remove_weight_norm(self):
        nn.utils.remove_weight_norm(self.conv_pre)
        for layer in self.upsampler: nn.utils.remove_weight_norm(layer)
        for layer in self.resblocks: layer.remove_weight_norm()
        nn.utils.remove_weight_norm(self.conv_post)
    def forward(self, spectrogram: torch.FloatTensor) -> torch.FloatTensor:
        if self.config.normalize_before: spectrogram = (spectrogram - self.mean) / self.scale
        is_batched = spectrogram.dim() == 3
        if not is_batched: spectrogram = spectrogram.unsqueeze(0)
        hidden_states = spectrogram.transpose(2, 1)
        hidden_states = self.conv_pre(hidden_states)
        for i in range(self.num_upsamples):
            hidden_states = nn.functional.leaky_relu(hidden_states, self.config.leaky_relu_slope)
            hidden_states = self.upsampler[i](hidden_states)
            res_state = self.resblocks[i * self.num_kernels](hidden_states)
            for j in range(1, self.num_kernels): res_state += self.resblocks[i * self.num_kernels + j](hidden_states)
            hidden_states = res_state / self.num_kernels
        hidden_states = nn.functional.leaky_relu(hidden_states)
        hidden_states = self.conv_post(hidden_states)
        hidden_states = torch.tanh(hidden_states)
        if not is_batched: waveform = hidden_states.squeeze(0).transpose(1, 0).view(-1)
        else: waveform = hidden_states.squeeze(1)
        return waveform
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
