"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.nn as nn
from sapiens_transformers.modeling_utils import PreTrainedModel
from sapiens_transformers.utils import ModelOutput
from ...time_series_utils import NegativeBinomialOutput, NormalOutput, StudentTOutput
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_patchtsmixer import PatchTSMixerConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "PatchTSMixerConfig"
PATCHTSMIXER_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`PatchTSMixerConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
        mask_input (`bool`, *optional*, defaults to `False`):
            If True, Masking will be enabled. False otherwise.
"""
PATCHTSMIXER_INPUTS_DOCSTRING = r"""
    Args:
        past_values (`torch.FloatTensor` of shape `(batch_size, seq_length, num_input_channels)`):
            Context values of the time series. For a pretraining task, this denotes the input time series to predict
            the masked portion. For a forecasting task, this denotes the history/past time series values. Similarly,
            for classification or regression tasks, it denotes the appropriate context values of the time series.
            For univariate time series, `num_input_channels` dimension should be 1. For multivariate time series, it is
            greater than 1.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
class PatchTSMixerGatedAttention(nn.Module):
    def __init__(self, in_size: int, out_size: int):
        super().__init__()
        self.attn_layer = nn.Linear(in_size, out_size)
        self.attn_softmax = nn.Softmax(dim=-1)
    def forward(self, inputs):
        attn_weight = self.attn_softmax(self.attn_layer(inputs))
        inputs = inputs * attn_weight
        return inputs
class PatchTSMixerBatchNorm(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.batchnorm = nn.BatchNorm1d(config.d_model, eps=config.norm_eps)
    def forward(self, inputs: torch.Tensor):
        output = inputs.transpose(1, 2)
        output = self.batchnorm(output)
        return output.transpose(1, 2)
class PatchTSMixerPositionalEncoding(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        if config.use_positional_encoding: self.position_enc = self._init_pe(config)
        else: self.position_enc = nn.Parameter(torch.zeros(config.num_patches, config.d_model))
    @staticmethod
    def _init_pe(config: PatchTSMixerConfig) -> nn.Parameter:
        if config.positional_encoding_type == "random": position_enc = nn.Parameter(torch.randn(config.num_patches, config.d_model), requires_grad=True)
        elif config.positional_encoding_type == "sincos":
            position_enc = torch.zeros(config.num_patches, config.d_model)
            position = torch.arange(0, config.num_patches).unsqueeze(1)
            div_term = torch.exp(torch.arange(0, config.d_model, 2) * -(math.log(10000.0) / config.d_model))
            position_enc[:, 0::2] = torch.sin(position * div_term)
            position_enc[:, 1::2] = torch.cos(position * div_term)
            position_enc = position_enc - position_enc.mean()
            position_enc = position_enc / (position_enc.std() * 10)
            position_enc = nn.Parameter(position_enc, requires_grad=False)
        else: raise ValueError(f"{config.positional_encoding_type} is not a valid positional encoder. Available types are 'random' and 'sincos'.")
        return position_enc
    def forward(self, patch_input: torch.Tensor):
        hidden_state = patch_input + self.position_enc
        return hidden_state
class PatchTSMixerNormLayer(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.norm_mlp = config.norm_mlp
        if "batch" in config.norm_mlp.lower(): self.norm = PatchTSMixerBatchNorm(config)
        else: self.norm = nn.LayerNorm(config.d_model, eps=config.norm_eps)
    def forward(self, inputs: torch.Tensor):
        if "batch" in self.norm_mlp.lower():
            inputs_reshaped = torch.reshape(inputs, (inputs.shape[0] * inputs.shape[1], inputs.shape[2], inputs.shape[3]))
            inputs_reshaped = self.norm(inputs_reshaped)
            inputs = torch.reshape(inputs_reshaped, inputs.shape)
        else: inputs = self.norm(inputs)
        return inputs
class PatchTSMixerMLP(nn.Module):
    def __init__(self, in_features, out_features, config):
        super().__init__()
        num_hidden = in_features * config.expansion_factor
        self.fc1 = nn.Linear(in_features, num_hidden)
        self.dropout1 = nn.Dropout(config.dropout)
        self.fc2 = nn.Linear(num_hidden, out_features)
        self.dropout2 = nn.Dropout(config.dropout)
    def forward(self, inputs: torch.Tensor):
        inputs = self.dropout1(nn.functional.gelu(self.fc1(inputs)))
        inputs = self.fc2(inputs)
        inputs = self.dropout2(inputs)
        return inputs
class PatchTSMixerChannelFeatureMixerBlock(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.norm = PatchTSMixerNormLayer(config)
        self.gated_attn = config.gated_attn
        self.mlp = PatchTSMixerMLP(in_features=config.num_input_channels, out_features=config.num_input_channels, config=config)
        if config.gated_attn: self.gating_block = PatchTSMixerGatedAttention(in_size=config.num_input_channels, out_size=config.num_input_channels)
    def forward(self, inputs: torch.Tensor):
        residual = inputs
        inputs = self.norm(inputs)
        inputs = inputs.permute(0, 3, 2, 1)
        if self.gated_attn: inputs = self.gating_block(inputs)
        inputs = self.mlp(inputs)
        inputs = inputs.permute(0, 3, 2, 1)
        out = inputs + residual
        return out
class PatchTSMixerAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True, is_causal: bool = False, config: Optional[PatchTSMixerConfig] = None):
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
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor] = None, past_key_value: Optional[Tuple[torch.Tensor]] = None,
    attention_mask: Optional[torch.Tensor] = None, layer_head_mask: Optional[torch.Tensor] = None,
    output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
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
class PatchMixerBlock(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.norm = PatchTSMixerNormLayer(config)
        self.self_attn = config.self_attn
        self.gated_attn = config.gated_attn
        self.mlp = PatchTSMixerMLP(in_features=config.num_patches, out_features=config.num_patches, config=config)
        if config.gated_attn: self.gating_block = PatchTSMixerGatedAttention(in_size=config.num_patches, out_size=config.num_patches)
        if config.self_attn:
            self.self_attn_layer = PatchTSMixerAttention(embed_dim=config.d_model, num_heads=config.self_attn_heads, dropout=config.dropout)
            self.norm_attn = PatchTSMixerNormLayer(config)
    def forward(self, hidden_state):
        residual = hidden_state
        hidden_state = self.norm(hidden_state)
        if self.self_attn:
            batch_size, n_vars, num_patches, d_model = hidden_state.shape
            hidden_state_reshaped = hidden_state.reshape(batch_size * n_vars, num_patches, d_model)
            x_attn, _, _ = self.self_attn_layer(hidden_state_reshaped, output_attentions=False)
            x_attn = x_attn.reshape(batch_size, n_vars, num_patches, d_model)
        hidden_state = hidden_state.transpose(2, 3)
        hidden_state = self.mlp(hidden_state)
        if self.gated_attn: hidden_state = self.gating_block(hidden_state)
        hidden_state = hidden_state.transpose(2, 3)
        if self.self_attn: hidden_state = self.norm_attn(hidden_state + x_attn)
        out = hidden_state + residual
        return out
class FeatureMixerBlock(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.norm = PatchTSMixerNormLayer(config)
        self.gated_attn = config.gated_attn
        self.mlp = PatchTSMixerMLP(in_features=config.d_model, out_features=config.d_model, config=config)
        if config.gated_attn: self.gating_block = PatchTSMixerGatedAttention(in_size=config.d_model, out_size=config.d_model)
    def forward(self, hidden: torch.Tensor):
        residual = hidden
        hidden = self.norm(hidden)
        hidden = self.mlp(hidden)
        if self.gated_attn: hidden = self.gating_block(hidden)
        out = hidden + residual
        return out
class PatchTSMixerLayer(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.patch_mixer = PatchMixerBlock(config=config)
        self.feature_mixer = FeatureMixerBlock(config=config)
        self.mode = config.mode
        if config.mode == "mix_channel": self.channel_feature_mixer = PatchTSMixerChannelFeatureMixerBlock(config=config)
    def forward(self, hidden: torch.Tensor):
        if self.mode == "mix_channel": hidden = self.channel_feature_mixer(hidden)
        hidden = self.patch_mixer(hidden)
        hidden = self.feature_mixer(hidden)
        return hidden
class PatchTSMixerBlock(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        num_layers = config.num_layers
        self.mixers = nn.ModuleList([PatchTSMixerLayer(config=config) for _ in range(num_layers)])
    def forward(self, hidden_state, output_hidden_states: bool = False):
        all_hidden_states = []
        embedding = hidden_state
        for mod in self.mixers:
            embedding = mod(embedding)
            if output_hidden_states: all_hidden_states.append(embedding)
        if output_hidden_states: return embedding, all_hidden_states
        else: return embedding, None
class PatchTSMixerForPredictionHead(nn.Module):
    def __init__(self, config: PatchTSMixerConfig, distribution_output=None):
        super().__init__()
        self.prediction_channel_indices = config.prediction_channel_indices
        if self.prediction_channel_indices is not None: self.prediction_channel_indices.sort()
        self.dropout_layer = nn.Dropout(config.head_dropout)
        if distribution_output is None: self.base_forecast_block = nn.Linear((config.num_patches * config.d_model), config.prediction_length)
        else: self.base_forecast_block = distribution_output.get_parameter_projection(config.num_patches * config.d_model)
        self.flatten = nn.Flatten(start_dim=-2)
    def forward(self, hidden_features):
        hidden_features = self.flatten(hidden_features)
        hidden_features = self.dropout_layer(hidden_features)
        forecast = self.base_forecast_block(hidden_features)
        if isinstance(forecast, tuple): forecast = tuple(z.transpose(-1, -2) for z in forecast)
        else: forecast = forecast.transpose(-1, -2)
        if self.prediction_channel_indices is not None:
            if isinstance(forecast, tuple): forecast = tuple(z[..., self.prediction_channel_indices] for z in forecast)
            else: forecast = forecast[..., self.prediction_channel_indices]
        return forecast
class PatchTSMixerLinearHead(nn.Module):
    def __init__(self, config: PatchTSMixerConfig, distribution_output=None):
        super().__init__()
        self.head_aggregation = config.head_aggregation
        self.output_range = config.output_range
        if config.head_aggregation is None: mul_factor = config.num_patches
        else: mul_factor = 1
        self.distribution_output = distribution_output
        if distribution_output is None: self.projection = nn.Linear(config.d_model * config.num_input_channels * mul_factor, config.num_targets)
        else: self.projection = distribution_output.get_parameter_projection(config.d_model * config.num_input_channels * mul_factor)
        if config.head_aggregation is None: self.flatten = nn.Flatten(start_dim=-3)
        else: self.flatten = nn.Flatten(start_dim=-2)
        self.dropout = nn.Dropout(config.head_dropout)
    def forward(self, hidden_features):
        hidden_features = hidden_features.transpose(-1, -2)
        if self.head_aggregation == "use_last": hidden_features = hidden_features[..., -1]
        elif self.head_aggregation == "max_pool": hidden_features = hidden_features.max(dim=-1).values
        elif self.head_aggregation == "avg_pool": hidden_features = hidden_features.mean(dim=-1)
        if self.flatten: hidden_features = self.flatten(hidden_features)
        hidden_features = self.dropout(hidden_features)
        hidden_features = self.projection(hidden_features)
        if (self.distribution_output is None) and (self.output_range is not None): hidden_features = (torch.sigmoid(hidden_features) * (self.output_range[1] - self.output_range[0]) + self.output_range[0])
        return hidden_features
class PatchTSMixerPreTrainedModel(PreTrainedModel):
    config_class = PatchTSMixerConfig
    base_model_prefix = "model"
    main_input_name = "past_values"
    supports_gradient_checkpointing = False
    def _init_weights(self, module):
        if isinstance(module, PatchTSMixerPositionalEncoding):
            if self.config.positional_encoding_type == "random": nn.init.normal_(module.position_enc, mean=0.0, std=0.1)
        elif isinstance(module, (nn.LayerNorm, nn.BatchNorm1d)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, PatchTSMixerBatchNorm):
            module.batchnorm.bias.data.zero_()
            module.batchnorm.weight.data.fill_(1.0)
        elif isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.init_std)
            if module.bias is not None: module.bias.data.zero_()
class PatchTSMixerPretrainHead(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.dropout_layer = nn.Dropout(config.head_dropout)
        self.base_pt_block = nn.Linear(config.d_model, config.patch_length)
    def forward(self, hidden_features):
        hidden_features = self.dropout_layer(hidden_features)
        forecast = self.base_pt_block(hidden_features)
        return forecast
def random_masking(inputs: torch.Tensor, mask_ratio: float, unmasked_channel_indices: list = None, channel_consistent_masking: bool = False, mask_value: int = 0):
    if mask_ratio < 0 or mask_ratio >= 1: raise ValueError(f"Mask ratio {mask_ratio} has to be between 0 and 1.")
    batch_size, num_channels, sequence_length, num_features = inputs.shape
    device = inputs.device
    len_keep = int(sequence_length * (1 - mask_ratio))
    if channel_consistent_masking:
        noise = torch.rand(batch_size, 1, sequence_length, device=device)
        noise = noise.repeat(1, num_channels, 1)
    else: noise = torch.rand(batch_size, num_channels, sequence_length, device=device)
    mask = torch.ones(batch_size, num_channels, sequence_length, device=device)
    mask[:, :, :len_keep] = 0
    ids_shuffle = torch.argsort(noise, dim=-1)
    ids_restore = torch.argsort(ids_shuffle, dim=-1)
    mask = torch.gather(mask, dim=-1, index=ids_restore)
    mask = mask.unsqueeze(-1).repeat(1, 1, 1, num_features)
    if unmasked_channel_indices is not None: mask[:, unmasked_channel_indices, :, :] = 0
    inputs_mask = inputs.masked_fill(mask.bool(), mask_value)
    return inputs_mask, mask[..., 0]
def forecast_masking(inputs: torch.Tensor, num_forecast_mask_patches: Union[list, int], unmasked_channel_indices: list = None, mask_value: int = 0):
    if isinstance(num_forecast_mask_patches, int): num_forecast_mask_patches = [num_forecast_mask_patches]
    forecast_mask_ratios = [1 for _ in num_forecast_mask_patches]
    batch_size, num_channels, sequence_length, num_features = inputs.shape
    mask = torch.zeros(batch_size, num_channels, sequence_length, device=inputs.device)
    t_list = []
    total_length = 0
    total_ratio = sum(forecast_mask_ratios)
    for patch_length, ratio in zip(num_forecast_mask_patches, forecast_mask_ratios):
        if patch_length <= 0 or patch_length >= sequence_length: raise ValueError(f"num_forecast_mask_patches {patch_length} should be greater than 0 and less than total patches.")
        temp_len = int(batch_size * ratio / total_ratio)
        t_list.append([patch_length, ratio, temp_len])
        total_length += temp_len
    t_list = sorted(t_list, key=lambda x: x[2])
    if total_length < batch_size: t_list[0][2] = t_list[0][2] + (batch_size - total_length)
    elif total_length > batch_size: t_list[-1][2] = t_list[-1][2] + (total_length - batch_size)
    batch1 = 0
    for patch_len, _, temp_len in t_list:
        batch2 = batch1 + temp_len
        mask[batch1:batch2, :, -patch_len:] = 1
        batch1 = batch2
    perm = torch.randperm(mask.shape[0])
    mask = mask[perm]
    mask = mask.unsqueeze(-1).repeat(1, 1, 1, num_features)
    if unmasked_channel_indices is not None: mask[:, unmasked_channel_indices, :, :] = 0
    inputs_mask = inputs.masked_fill(mask.bool(), mask_value)
    return inputs_mask, mask[..., 0]
class PatchTSMixerPatchify(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.sequence_length = config.context_length
        self.patch_length = config.patch_length
        self.patch_stride = config.patch_stride
        if self.sequence_length <= self.patch_length: raise ValueError(f"Sequence length ({self.sequence_length}) has to be greater than the patch length ({self.patch_length})")
        self.num_patches = (max(self.sequence_length, self.patch_length) - self.patch_length) // self.patch_stride + 1
        new_sequence_length = self.patch_length + self.patch_stride * (self.num_patches - 1)
        self.sequence_start = self.sequence_length - new_sequence_length
    def forward(self, past_values: torch.Tensor):
        sequence_length = past_values.shape[-2]
        if sequence_length != self.sequence_length: raise ValueError(f"Input sequence length ({sequence_length}) doesn't match model configuration ({self.sequence_length}).")
        output = past_values[:, self.sequence_start :, :]
        output = output.unfold(dimension=-2, size=self.patch_length, step=self.patch_stride)
        output = output.transpose(-2, -3).contiguous()
        return output
class PatchTSMixerMasking(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.random_mask_ratio = config.random_mask_ratio
        self.channel_consistent_masking = config.channel_consistent_masking
        self.mask_type = config.mask_type
        self.num_forecast_mask_patches = config.num_forecast_mask_patches
        self.unmasked_channel_indices = config.unmasked_channel_indices
        self.mask_value = config.mask_value
        if self.unmasked_channel_indices is not None: self.unmasked_channel_indices = sorted(self.unmasked_channel_indices)
    def forward(self, patch_input: torch.Tensor):
        if self.mask_type == "random": masked_input, mask = random_masking(inputs=patch_input, mask_ratio=self.random_mask_ratio,
        unmasked_channel_indices=self.unmasked_channel_indices, channel_consistent_masking=self.channel_consistent_masking, mask_value=self.mask_value)
        elif self.mask_type == "forecast": masked_input, mask = forecast_masking(inputs=patch_input, num_forecast_mask_patches=self.num_forecast_mask_patches,
        unmasked_channel_indices=self.unmasked_channel_indices, mask_value=self.mask_value)
        else: raise ValueError(f"Invalid mask type {self.mask_type}.")
        mask = mask.bool()
        return masked_input, mask
class PatchTSMixerStdScaler(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.dim = config.scaling_dim if hasattr(config, "scaling_dim") else 1
        self.keepdim = config.keepdim if hasattr(config, "keepdim") else True
        self.minimum_scale = config.minimum_scale if hasattr(config, "minimum_scale") else 1e-5
    def forward(self, data: torch.Tensor, observed_indicator: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        denominator = observed_indicator.sum(self.dim, keepdim=self.keepdim)
        denominator = denominator.clamp_min(1.0)
        loc = (data * observed_indicator).sum(self.dim, keepdim=self.keepdim) / denominator
        variance = (((data - loc) * observed_indicator) ** 2).sum(self.dim, keepdim=self.keepdim) / denominator
        scale = torch.sqrt(variance + self.minimum_scale)
        return (data - loc) / scale, loc, scale
class PatchTSMixerMeanScaler(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.dim = config.scaling_dim if hasattr(config, "scaling_dim") else 1
        self.keepdim = config.keepdim if hasattr(config, "keepdim") else True
        self.minimum_scale = config.minimum_scale if hasattr(config, "minimum_scale") else 1e-10
        self.default_scale = config.default_scale if hasattr(config, "default_scale") else None
    def forward(self, data: torch.Tensor, observed_indicator: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        ts_sum = (data * observed_indicator).abs().sum(self.dim, keepdim=True)
        num_observed = observed_indicator.sum(self.dim, keepdim=True)
        scale = ts_sum / torch.clamp(num_observed, min=1)
        if self.default_scale is None:
            batch_sum = ts_sum.sum(dim=0)
            batch_observations = torch.clamp(num_observed.sum(0), min=1)
            default_scale = torch.squeeze(batch_sum / batch_observations)
        else: default_scale = self.default_scale * torch.ones_like(scale)
        scale = torch.where(num_observed > 0, scale, default_scale)
        scale = torch.clamp(scale, min=self.minimum_scale)
        scaled_data = data / scale
        if not self.keepdim: scale = scale.squeeze(dim=self.dim)
        return scaled_data, torch.zeros_like(scale), scale
class PatchTSMixerNOPScaler(nn.Module):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__()
        self.dim = config.scaling_dim if hasattr(config, "scaling_dim") else 1
        self.keepdim = config.keepdim if hasattr(config, "keepdim") else True
    def forward(self, data: torch.Tensor, observed_indicator: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scale = torch.ones_like(data, requires_grad=False).mean(dim=self.dim, keepdim=self.keepdim)
        loc = torch.zeros_like(data, requires_grad=False).mean(dim=self.dim, keepdim=self.keepdim)
        return data, loc, scale
@dataclass
class PatchTSMixerEncoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class PatchTSMixerEncoder(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__(config)
        self.use_return_dict = config.use_return_dict
        self.patcher = nn.Linear(config.patch_length, config.d_model)
        if config.use_positional_encoding: self.positional_encoder = PatchTSMixerPositionalEncoding(config=config)
        else: self.positional_encoder = None
        self.mlp_mixer_encoder = PatchTSMixerBlock(config=config)
        if config.post_init: self.post_init()
    def forward(self, past_values: torch.Tensor, output_hidden_states: Optional[bool] = False, return_dict: Optional[bool] = None) -> Union[Tuple, PatchTSMixerEncoderOutput]:
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        patches = self.patcher(past_values)
        if self.positional_encoder is not None: patches = self.positional_encoder(patches)
        last_hidden_state, hidden_states = self.mlp_mixer_encoder(patches, output_hidden_states=output_hidden_states)
        if not return_dict: return tuple(v for v in [last_hidden_state, hidden_states])
        return PatchTSMixerEncoderOutput(last_hidden_state=last_hidden_state, hidden_states=hidden_states)
@dataclass
class PatchTSMixerModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    patch_input: torch.FloatTensor = None
    mask: Optional[torch.FloatTensor] = None
    loc: Optional[torch.FloatTensor] = None
    scale: Optional[torch.FloatTensor] = None
@add_start_docstrings("The PatchTSMixer Model for time-series forecasting.", PATCHTSMIXER_START_DOCSTRING)
class PatchTSMixerModel(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig, mask_input: bool = False):
        super().__init__(config)
        self.use_return_dict = config.use_return_dict
        self.encoder = PatchTSMixerEncoder(config)
        self.patching = PatchTSMixerPatchify(config)
        if mask_input is True: self.masking = PatchTSMixerMasking(config)
        else: self.masking = None
        if config.scaling == "mean": self.scaler = PatchTSMixerMeanScaler(config)
        elif config.scaling == "std" or config.scaling is True: self.scaler = PatchTSMixerStdScaler(config)
        else: self.scaler = PatchTSMixerNOPScaler(config)
        if config.post_init: self.post_init()
    @add_start_docstrings_to_model_forward(PATCHTSMIXER_INPUTS_DOCSTRING)
    def forward(self, past_values: torch.Tensor, observed_mask: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = False,
    return_dict: Optional[bool] = None) -> PatchTSMixerModelOutput:
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        mask = None
        if observed_mask is None: observed_mask = torch.ones_like(past_values)
        scaled_past_values, loc, scale = self.scaler(past_values, observed_mask)
        patched_x = self.patching(scaled_past_values)
        enc_input = patched_x
        if self.masking is not None: enc_input, mask = self.masking(patched_x)
        encoder_output = self.encoder(enc_input, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if isinstance(encoder_output, tuple): encoder_output = PatchTSMixerEncoderOutput(*encoder_output)
        if not return_dict: return tuple(v for v in [encoder_output.last_hidden_state, encoder_output.hidden_states, patched_x, mask, loc, scale])
        return PatchTSMixerModelOutput(last_hidden_state=encoder_output.last_hidden_state, hidden_states=encoder_output.hidden_states,
        patch_input=patched_x, mask=mask, loc=loc, scale=scale)
@dataclass
class PatchTSMixerForPreTrainingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_outputs: torch.FloatTensor = None
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class PatchTSMixerForPretraining(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__(config)
        self.model = PatchTSMixerModel(config, mask_input=True)
        self.head = PatchTSMixerPretrainHead(config=config)
        self.masked_loss = config.masked_loss
        self.use_return_dict = config.use_return_dict
        if config.post_init: self.post_init()
    @add_start_docstrings_to_model_forward(PATCHTSMIXER_INPUTS_DOCSTRING)
    def forward(self, past_values: torch.Tensor, observed_mask: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = False,
    return_loss: bool = True, return_dict: Optional[bool] = None) -> PatchTSMixerForPreTrainingOutput:
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        if self.masked_loss is True: loss = torch.nn.MSELoss(reduction="none")
        else: loss = torch.nn.MSELoss(reduction="mean")
        model_output = self.model(past_values, observed_mask=observed_mask, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if isinstance(model_output, tuple): model_output = PatchTSMixerModelOutput(*model_output)
        x_hat = self.head(model_output.last_hidden_state)
        if return_loss is True: loss_val = loss(x_hat, model_output.patch_input)
        else: loss_val = None
        if self.masked_loss is True and loss_val is not None: loss_val = (loss_val.mean(dim=-1) * model_output.mask).sum() / (model_output.mask.sum() + 1e-10)
        if not return_dict: return tuple(v for v in [loss_val, x_hat, model_output.last_hidden_state, model_output.hidden_states])
        return PatchTSMixerForPreTrainingOutput(loss=loss_val, prediction_outputs=x_hat, last_hidden_state=model_output.last_hidden_state, hidden_states=model_output.hidden_states)
@dataclass
class PatchTSMixerForPredictionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_outputs: torch.FloatTensor = None
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    loc: torch.FloatTensor = None
    scale: torch.FloatTensor = None
@dataclass
class SamplePatchTSMixerPredictionOutput(ModelOutput):
    """Args:"""
    sequences: torch.FloatTensor = None
@dataclass
class SamplePatchTSMixerRegressionOutput(ModelOutput):
    """Args:"""
    sequences: torch.FloatTensor = None
def nll(input: torch.distributions.Distribution, target: torch.Tensor) -> torch.Tensor: return -input.log_prob(target)
def weighted_average(input_tensor: torch.Tensor, weights: Optional[torch.Tensor] = None, dim=None) -> torch.Tensor:
    if weights is not None:
        weighted_tensor = torch.where(weights != 0, input_tensor * weights, torch.zeros_like(input_tensor))
        sum_weights = torch.clamp(weights.sum(dim=dim) if dim else weights.sum(), min=1.0)
        return (weighted_tensor.sum(dim=dim) if dim else weighted_tensor.sum()) / sum_weights
    else: return input_tensor.mean(dim=dim)
class PatchTSMixerForPrediction(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__(config)
        self.loss = config.loss
        self.use_return_dict = config.use_return_dict
        self.prediction_channel_indices = config.prediction_channel_indices
        self.num_parallel_samples = config.num_parallel_samples
        if config.loss == "mse": self.distribution_output = None
        else:
            dim = config.prediction_length
            distribution_output_map = {"student_t": StudentTOutput, "normal": NormalOutput, "negative_binomial": NegativeBinomialOutput}
            output_class = distribution_output_map.get(config.distribution_output, None)
            if output_class is not None: self.distribution_output = output_class(dim=dim)
            else: raise ValueError(f"Unknown distribution output {config.distribution_output}")
        self.model = PatchTSMixerModel(config)
        self.head = PatchTSMixerForPredictionHead(config=config, distribution_output=self.distribution_output)
        if config.post_init: self.post_init()
    @add_start_docstrings_to_model_forward(PATCHTSMIXER_INPUTS_DOCSTRING)
    def forward(self, past_values: torch.Tensor, observed_mask: Optional[torch.Tensor] = None, future_values: Optional[torch.Tensor] = None,
    output_hidden_states: Optional[bool] = False, return_loss: bool = True, return_dict: Optional[bool] = None) -> PatchTSMixerForPredictionOutput:
        if self.loss == "mse": loss = nn.MSELoss(reduction="mean")
        elif self.loss == "nll": loss = nll
        else: raise ValueError("Invalid loss function: Allowed values: mse and nll")
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        model_output = self.model(past_values, observed_mask=observed_mask, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if isinstance(model_output, tuple): model_output = PatchTSMixerModelOutput(*model_output)
        y_hat = self.head(model_output.last_hidden_state)
        loss_val = None
        if self.prediction_channel_indices is not None:
            if self.distribution_output:
                distribution = self.distribution_output.distribution(y_hat, loc=model_output.loc[..., self.prediction_channel_indices],
                scale=model_output.scale[..., self.prediction_channel_indices])
                if future_values is not None and return_loss is True:
                    loss_val = loss(distribution, future_values[..., self.prediction_channel_indices])
                    loss_val = weighted_average(loss_val)
            else:
                y_hat = (y_hat * model_output.scale[..., self.prediction_channel_indices] + model_output.loc[..., self.prediction_channel_indices])
                if future_values is not None and return_loss is True: loss_val = loss(y_hat, future_values[..., self.prediction_channel_indices])
        else:
            if self.distribution_output:
                distribution = self.distribution_output.distribution(y_hat, loc=model_output.loc, scale=model_output.scale)
                if future_values is not None and return_loss is True:
                    loss_val = loss(distribution, future_values)
                    loss_val = weighted_average(loss_val)
            else:
                y_hat = y_hat * model_output.scale + model_output.loc
                if future_values is not None and return_loss is True: loss_val = loss(y_hat, future_values)
        if self.prediction_channel_indices is not None:
            loc = model_output.loc[..., self.prediction_channel_indices]
            scale = model_output.scale[..., self.prediction_channel_indices]
        else:
            loc = model_output.loc
            scale = model_output.scale
        if not return_dict: return tuple(v for v in [loss_val, y_hat, model_output.last_hidden_state, model_output.hidden_states, loc, scale])
        return PatchTSMixerForPredictionOutput(loss=loss_val, prediction_outputs=y_hat, last_hidden_state=model_output.last_hidden_state,
        hidden_states=model_output.hidden_states, loc=loc, scale=scale)
    def generate(self, past_values: torch.Tensor, observed_mask: Optional[torch.Tensor] = None) -> SamplePatchTSMixerPredictionOutput:
        num_parallel_samples = self.num_parallel_samples
        outputs = self(past_values=past_values, future_values=None, observed_mask=observed_mask, output_hidden_states=False)
        distribution = self.distribution_output.distribution(outputs.prediction_outputs, loc=outputs.loc, scale=outputs.scale)
        samples = [distribution.sample() for _ in range(num_parallel_samples)]
        samples = torch.stack(samples, dim=1)
        return SamplePatchTSMixerPredictionOutput(sequences=samples)
@dataclass
class PatchTSMixerForTimeSeriesClassificationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_outputs: torch.FloatTensor = None
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class PatchTSMixerForTimeSeriesClassification(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__(config)
        self.model = PatchTSMixerModel(config)
        self.head = PatchTSMixerLinearHead(config=config)
        self.use_return_dict = config.use_return_dict
        if config.scaling in ["std", "mean", True]: self.inject_scale = InjectScalerStatistics4D(d_model=config.d_model, num_patches=config.num_patches)
        else: self.inject_scale = None
        if config.post_init: self.post_init()
    @add_start_docstrings_to_model_forward(PATCHTSMIXER_INPUTS_DOCSTRING)
    def forward(self, past_values: torch.Tensor, target_values: torch.Tensor = None, output_hidden_states: Optional[bool] = False, return_loss: bool = True,
    return_dict: Optional[bool] = None) -> PatchTSMixerForTimeSeriesClassificationOutput:
        loss = torch.nn.CrossEntropyLoss()
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        model_output = self.model(past_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if isinstance(model_output, tuple): model_output = PatchTSMixerModelOutput(*model_output)
        if self.inject_scale is not None: model_output.last_hidden_state = self.inject_scale(model_output.last_hidden_state,
        loc=model_output.loc, scale=model_output.scale)
        y_hat = self.head(model_output.last_hidden_state)
        if target_values is not None and return_loss is True: loss_val = loss(y_hat, target_values)
        else: loss_val = None
        if not return_dict: return tuple(v for v in [loss_val, y_hat, model_output.last_hidden_state, model_output.hidden_states])
        return PatchTSMixerForTimeSeriesClassificationOutput(loss=loss_val, prediction_outputs=y_hat, last_hidden_state=model_output.last_hidden_state, hidden_states=model_output.hidden_states)
@dataclass
class PatchTSMixerForRegressionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    regression_outputs: torch.FloatTensor = None
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class InjectScalerStatistics4D(nn.Module):
    def __init__(self, d_model: int, num_patches: int, expansion: int = 2):
        super().__init__()
        self.inverse_trans_expansion = nn.Linear(d_model + 2, expansion * d_model)
        self.inverse_trans_compression = nn.Linear(expansion * d_model, d_model)
        self.map_scale_expansion = nn.Linear(2, 2 * expansion)
        self.map_scale_compression = nn.Linear(2 * expansion, 2)
        self.num_patches = num_patches
    def forward(self, inputs: torch.Tensor, loc: torch.Tensor, scale: torch.Tensor):
        mean = loc.transpose(-1, -2)
        mean = mean.unsqueeze(-2)
        mean = mean.repeat(1, 1, self.num_patches, 1)
        stdev = scale.transpose(-1, -2)
        stdev = stdev.unsqueeze(-2)
        stdev = stdev.repeat(1, 1, self.num_patches, 1)
        concat_stats = torch.cat([mean, stdev], dim=-1)
        concat_stats = self.map_scale_expansion(concat_stats)
        concat_stats = self.map_scale_compression(concat_stats)
        inputs = torch.cat([inputs, concat_stats], dim=-1)
        inputs = self.inverse_trans_expansion(inputs)
        inputs = self.inverse_trans_compression(inputs)
        return inputs
class PatchTSMixerForRegression(PatchTSMixerPreTrainedModel):
    def __init__(self, config: PatchTSMixerConfig):
        super().__init__(config)
        self.model = PatchTSMixerModel(config)
        self.loss = config.loss
        self.distribution_output = config.distribution_output
        self.use_return_dict = config.use_return_dict
        self.num_parallel_samples = config.num_parallel_samples
        if config.loss == "mse": self.distribution_output = None
        else:
            distribution_output_map = {"student_t": StudentTOutput, "normal": NormalOutput, "negative_binomial": NegativeBinomialOutput}
            output_class = distribution_output_map.get(config.distribution_output)
            if output_class is not None: self.distribution_output = output_class(dim=config.num_targets)
            else: raise ValueError(f"Unknown distribution output {config.distribution_output}")
        if config.scaling in ["std", "mean", True]: self.inject_scale = InjectScalerStatistics4D(d_model=config.d_model, num_patches=config.num_patches)
        else: self.inject_scale = None
        self.head = PatchTSMixerLinearHead(config=config, distribution_output=self.distribution_output)
        if config.post_init: self.post_init()
    @add_start_docstrings_to_model_forward(PATCHTSMIXER_INPUTS_DOCSTRING)
    def forward(self, past_values: torch.Tensor, target_values: torch.Tensor = None, output_hidden_states: Optional[bool] = False, return_loss: bool = True,
    return_dict: Optional[bool] = None) -> PatchTSMixerForRegressionOutput:
        if self.loss == "mse": loss = nn.MSELoss(reduction="mean")
        elif self.loss == "nll": loss = nll
        else: raise ValueError("Invalid loss function: Allowed values: mse and nll")
        return_dict = return_dict if return_dict is not None else self.use_return_dict
        model_output = self.model(past_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if isinstance(model_output, tuple): model_output = PatchTSMixerModelOutput(*model_output)
        if self.inject_scale is not None: model_output.last_hidden_state = self.inject_scale(model_output.last_hidden_state,
        loc=model_output.loc, scale=model_output.scale)
        y_hat = self.head(model_output.last_hidden_state)
        if target_values is not None and return_loss is True:
            if self.distribution_output:
                if self.distribution_output == "negative_binomial" and torch.any(target_values < 0): raise Exception("target_values cannot be negative for negative_binomial distribution.")
                distribution = self.distribution_output.distribution(y_hat)
                y_hat = tuple([item.view(-1, self.config.num_targets) for item in y_hat])
                loss_val = loss(distribution, target_values)
                loss_val = weighted_average(loss_val)
            else: loss_val = loss(y_hat, target_values)
        else: loss_val = None
        if not return_dict: return tuple(v for v in [loss_val, y_hat, model_output.last_hidden_state, model_output.hidden_states])
        return PatchTSMixerForRegressionOutput(loss=loss_val, regression_outputs=y_hat, last_hidden_state=model_output.last_hidden_state,
        hidden_states=model_output.hidden_states)
    def generate(self, past_values: torch.Tensor) -> SamplePatchTSMixerRegressionOutput:
        num_parallel_samples = self.num_parallel_samples
        outputs = self(past_values=past_values, target_values=None, output_hidden_states=False)
        distribution = self.distribution_output.distribution(outputs.regression_outputs)
        samples = [distribution.sample() for _ in range(num_parallel_samples)]
        samples = torch.stack(samples, dim=1).view(-1, num_parallel_samples, self.config.num_targets)
        return SamplePatchTSMixerRegressionOutput(sequences=samples)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
