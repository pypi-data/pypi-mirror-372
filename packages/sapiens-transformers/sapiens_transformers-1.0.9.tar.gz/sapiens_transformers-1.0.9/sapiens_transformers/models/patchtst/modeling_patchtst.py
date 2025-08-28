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
from torch import nn
from ...activations import ACT2CLS
from ...modeling_outputs import BaseModelOutput
from ...modeling_utils import PreTrainedModel
from ...time_series_utils import NegativeBinomialOutput, NormalOutput, StudentTOutput
from ...utils import ModelOutput, add_start_docstrings, logging
from .configuration_patchtst import PatchTSTConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "PatchTSTConfig"
class PatchTSTAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, is_decoder: bool = False, bias: bool = True, is_causal: bool = False, config: Optional[PatchTSTConfig] = None):
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
class PatchTSTBatchNorm(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.batchnorm = nn.BatchNorm1d(config.d_model, eps=config.norm_eps)
    def forward(self, inputs: torch.Tensor):
        output = inputs.transpose(1, 2)
        output = self.batchnorm(output)
        return output.transpose(1, 2)
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
class PatchTSTPatchify(nn.Module):
    def __init__(self, config: PatchTSTConfig):
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
class PatchTSTMasking(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.random_mask_ratio = config.random_mask_ratio
        self.channel_consistent_masking = config.channel_consistent_masking
        self.mask_type = config.mask_type
        self.num_forecast_mask_patches = config.num_forecast_mask_patches
        self.unmasked_channel_indices = config.unmasked_channel_indices
        self.mask_value = config.mask_value
        if self.unmasked_channel_indices is not None: self.unmasked_channel_indices = sorted(self.unmasked_channel_indices)
    def forward(self, patch_input: torch.Tensor):
        if self.mask_type == "random": masked_input, mask = random_masking(inputs=patch_input, mask_ratio=self.random_mask_ratio, unmasked_channel_indices=self.unmasked_channel_indices,
        channel_consistent_masking=self.channel_consistent_masking, mask_value=self.mask_value)
        elif self.mask_type == "forecast": masked_input, mask = forecast_masking(inputs=patch_input, num_forecast_mask_patches=self.num_forecast_mask_patches,
        unmasked_channel_indices=self.unmasked_channel_indices, mask_value=self.mask_value)
        else: raise ValueError(f"Invalid mask type {self.mask_type}.")
        mask = mask.bool()
        return masked_input, mask
class PatchTSTEncoderLayer(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.channel_attention = config.channel_attention
        self.self_attn = PatchTSTAttention(embed_dim=config.d_model, num_heads=config.num_attention_heads, dropout=config.attention_dropout)
        self.dropout_path1 = nn.Dropout(config.path_dropout) if config.path_dropout > 0 else nn.Identity()
        if config.norm_type == "batchnorm": self.norm_sublayer1 = PatchTSTBatchNorm(config)
        elif config.norm_type == "layernorm": self.norm_sublayer1 = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        else: raise ValueError(f"{config.norm_type} is not a supported norm layer type.")
        if self.channel_attention:
            self.dropout_path2 = nn.Dropout(config.path_dropout) if config.path_dropout > 0 else nn.Identity()
            if config.norm_type == "batchnorm": self.norm_sublayer2 = PatchTSTBatchNorm(config)
            elif config.norm_type == "layernorm": self.norm_sublayer2 = nn.LayerNorm(config.d_model, eps=config.norm_eps)
            else: raise ValueError(f"{config.norm_type} is not a supported norm layer type.")
        self.ff = nn.Sequential(nn.Linear(config.d_model, config.ffn_dim, bias=config.bias), ACT2CLS[config.activation_function](),
        nn.Dropout(config.ff_dropout) if config.ff_dropout > 0 else nn.Identity(), nn.Linear(config.ffn_dim, config.d_model, bias=config.bias))
        self.dropout_path3 = nn.Dropout(config.path_dropout) if config.path_dropout > 0 else nn.Identity()
        if config.norm_type == "batchnorm": self.norm_sublayer3 = PatchTSTBatchNorm(config)
        elif config.norm_type == "layernorm": self.norm_sublayer3 = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        else: raise ValueError(f"{config.norm_type} is not a supported norm layer type.")
        self.pre_norm = config.pre_norm
    def forward(self, hidden_state: torch.Tensor, output_attentions: Optional[bool] = None):
        batch_size, num_input_channels, sequence_length, d_model = hidden_state.shape
        hidden_state = hidden_state.view(batch_size * num_input_channels, sequence_length, d_model)
        if self.pre_norm:
            attn_output, attn_weights, _ = self.self_attn(hidden_states=self.norm_sublayer1(hidden_state), output_attentions=output_attentions)
            hidden_state = hidden_state + self.dropout_path1(attn_output)
        else:
            attn_output, attn_weights, _ = self.self_attn(hidden_states=hidden_state, output_attentions=output_attentions)
            hidden_state = self.norm_sublayer1(hidden_state + self.dropout_path1(attn_output))
        hidden_state = hidden_state.reshape(batch_size, num_input_channels, sequence_length, d_model)
        if self.channel_attention:
            hidden_state = hidden_state.transpose(2, 1).contiguous()
            hidden_state = hidden_state.view(batch_size * sequence_length, num_input_channels, d_model)
            if self.pre_norm:
                attn_output, channel_attn_weights, _ = self.self_attn(hidden_states=self.norm_sublayer2(hidden_state), output_attentions=output_attentions)
                hidden_state = hidden_state + self.dropout_path2(attn_output)
            else:
                attn_output, channel_attn_weights, _ = self.self_attn(hidden_states=hidden_state, output_attentions=output_attentions)
                hidden_state = self.norm_sublayer2(hidden_state + self.dropout_path2(attn_output))
            hidden_state = hidden_state.reshape(batch_size, sequence_length, num_input_channels, d_model)
            hidden_state = hidden_state.transpose(1, 2).contiguous()
        hidden_state = hidden_state.view(batch_size * num_input_channels, sequence_length, d_model)
        if self.pre_norm: hidden_state = hidden_state + self.dropout_path3(self.ff(self.norm_sublayer3(hidden_state)))
        else: hidden_state = self.norm_sublayer3(hidden_state + self.dropout_path3(self.ff(hidden_state)))
        hidden_state = hidden_state.reshape(batch_size, num_input_channels, sequence_length, d_model)
        outputs = (hidden_state,)
        if output_attentions: outputs += (attn_weights, channel_attn_weights) if self.channel_attention else (attn_weights,)
        return outputs
class PatchTSTPreTrainedModel(PreTrainedModel):
    config_class = PatchTSTConfig
    base_model_prefix = "model"
    main_input_name = "past_values"
    supports_gradient_checkpointing = False
    def _init_weights(self, module):
        if isinstance(module, PatchTSTPositionalEncoding):
            if self.config.use_cls_token: nn.init.normal_(module.cls_token, std=0.02)
            if self.config.positional_encoding_type == "random": nn.init.normal_(module.position_enc, mean=0.0, std=0.1)
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, PatchTSTBatchNorm):
            module.batchnorm.bias.data.zero_()
            module.batchnorm.weight.data.fill_(1.0)
        elif isinstance(module, (nn.Linear, nn.Conv1d)):
            module.weight.data.normal_(mean=0.0, std=self.config.init_std)
            if module.bias is not None: module.bias.data.zero_()
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (PatchTSTEncoder)): module.gradient_checkpointing = value
class PatchTSTEmbedding(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.num_input_channels = config.num_input_channels
        self.share_embedding = config.share_embedding
        if self.share_embedding: self.input_embedding = nn.Linear(config.patch_length, config.d_model)
        else:
            self.input_embedding = nn.ModuleList()
            for _ in range(config.num_input_channels): self.input_embedding.append(nn.Linear(config.patch_length, config.d_model))
    def forward(self, patch_input: torch.Tensor):
        num_input_channels = patch_input.shape[1]
        if num_input_channels != self.num_input_channels: raise ValueError(f"The defined number of input channels ({self.num_input_channels}) in the config has to be the same as the number of channels in the batch input ({num_input_channels})")
        if self.share_embedding: embeddings = self.input_embedding(patch_input)
        else:
            embeddings = [self.input_embedding[i](patch_input[:, i, :, :]) for i in range(num_input_channels)]
            embeddings = torch.stack(embeddings, dim=1)
        return embeddings
class PatchTSTPositionalEncoding(nn.Module):
    def __init__(self, config: PatchTSTConfig, num_patches: int):
        super().__init__()
        self.use_cls_token = config.use_cls_token
        self.num_input_channels = config.num_input_channels
        if config.use_cls_token:
            self.cls_token = nn.Parameter(torch.zeros(1, 1, 1, config.d_model))
            num_patches += 1
        self.position_enc = self._init_pe(config, num_patches)
        self.positional_dropout = (nn.Dropout(config.positional_dropout) if config.positional_dropout > 0 else nn.Identity())
    @staticmethod
    def _init_pe(config: PatchTSTConfig, num_patches: int) -> nn.Parameter:
        if config.positional_encoding_type == "random": position_enc = nn.Parameter(torch.randn(num_patches, config.d_model), requires_grad=True)
        elif config.positional_encoding_type == "sincos":
            position_enc = torch.zeros(num_patches, config.d_model)
            position = torch.arange(0, num_patches).unsqueeze(1)
            div_term = torch.exp(torch.arange(0, config.d_model, 2) * -(math.log(10000.0) / config.d_model))
            position_enc[:, 0::2] = torch.sin(position * div_term)
            position_enc[:, 1::2] = torch.cos(position * div_term)
            position_enc = position_enc - position_enc.mean()
            position_enc = position_enc / (position_enc.std() * 10)
            position_enc = nn.Parameter(position_enc, requires_grad=False)
        else: raise ValueError(f"{config.positional_encoding_type} is not a valid positional encoder. Available types are 'random' and 'sincos'.")
        return position_enc
    def forward(self, patch_input: torch.Tensor):
        if self.use_cls_token:
            patch_input = self.positional_dropout(patch_input + self.position_enc[1:, :])
            cls_token = self.cls_token + self.position_enc[:1, :]
            cls_tokens = cls_token.expand(patch_input.shape[0], self.num_input_channels, -1, -1)
            hidden_state = torch.cat((cls_tokens, patch_input), dim=2)
        else: hidden_state = self.positional_dropout(patch_input + self.position_enc)
        return hidden_state
class PatchTSTEncoder(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig, num_patches: int):
        super().__init__(config)
        self.gradient_checkpointing = False
        self.embedder = PatchTSTEmbedding(config)
        self.positional_encoder = PatchTSTPositionalEncoding(config, num_patches)
        self.layers = nn.ModuleList([PatchTSTEncoderLayer(config) for i in range(config.num_hidden_layers)])
        self.post_init()
    def forward(self, patch_input: torch.Tensor, output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None) -> BaseModelOutput:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        patch_input = self.embedder(patch_input)
        hidden_state = self.positional_encoder(patch_input)
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for encoder_layer in self.layers:
            if output_hidden_states: encoder_states = encoder_states + (hidden_state,)
            layer_outputs = encoder_layer(hidden_state=hidden_state, output_attentions=output_attentions)
            hidden_state = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        return BaseModelOutput(last_hidden_state=hidden_state, hidden_states=encoder_states, attentions=all_attentions)
PATCHTST_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`PatchTSTConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
@dataclass
class PatchTSTModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    mask: torch.FloatTensor = None
    loc: torch.FloatTensor = None
    scale: torch.FloatTensor = None
    patch_input: torch.FloatTensor = None
@dataclass
class PatchTSTForPretrainingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_output: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class PatchTSTForRegressionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    regression_outputs: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class PatchTSTForPredictionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_outputs: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    loc: torch.FloatTensor = None
    scale: torch.FloatTensor = None
@dataclass
class PatchTSTForClassificationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class SamplePatchTSTOutput(ModelOutput):
    """Args:"""
    sequences: torch.FloatTensor = None
def nll(input: torch.distributions.Distribution, target: torch.Tensor) -> torch.Tensor: return -input.log_prob(target)
def weighted_average(input_tensor: torch.Tensor, weights: Optional[torch.Tensor] = None, dim=None) -> torch.Tensor:
    if weights is not None:
        weighted_tensor = torch.where(weights != 0, input_tensor * weights, torch.zeros_like(input_tensor))
        sum_weights = torch.clamp(weights.sum(dim=dim) if dim else weights.sum(), min=1.0)
        return (weighted_tensor.sum(dim=dim) if dim else weighted_tensor.sum()) / sum_weights
    else: return input_tensor.mean(dim=dim)
class PatchTSTStdScaler(nn.Module):
    def __init__(self, config: PatchTSTConfig):
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
class PatchTSTMeanScaler(nn.Module):
    def __init__(self, config: PatchTSTConfig):
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
class PatchTSTNOPScaler(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.dim = config.scaling_dim if hasattr(config, "scaling_dim") else 1
        self.keepdim = config.keepdim if hasattr(config, "keepdim") else True
    def forward(self, data: torch.Tensor, observed_indicator: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scale = torch.ones_like(data, requires_grad=False).mean(dim=self.dim, keepdim=self.keepdim)
        loc = torch.zeros_like(data, requires_grad=False).mean(dim=self.dim, keepdim=self.keepdim)
        return data, loc, scale
class PatchTSTScaler(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        if config.scaling == "mean" or config.scaling is True: self.scaler = PatchTSTMeanScaler(config)
        elif config.scaling == "std": self.scaler = PatchTSTStdScaler(config)
        else: self.scaler = PatchTSTNOPScaler(config)
    def forward(self, data: torch.Tensor, observed_indicator: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        data, loc, scale = self.scaler(data, observed_indicator)
        return data, loc, scale
@add_start_docstrings("The bare PatchTST Model outputting raw hidden-states without any specific head.", PATCHTST_START_DOCSTRING)
class PatchTSTModel(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig):
        super().__init__(config)
        self.scaler = PatchTSTScaler(config)
        self.patchifier = PatchTSTPatchify(config)
        self.do_mask_input = config.do_mask_input
        num_patches = self.patchifier.num_patches
        if self.do_mask_input: self.masking = PatchTSTMasking(config)
        else: self.masking = nn.Identity()
        self.encoder = PatchTSTEncoder(config, num_patches=num_patches)
        self.post_init()
    def forward(self, past_values: torch.Tensor, past_observed_mask: Optional[torch.Tensor] = None, future_values: Optional[torch.Tensor] = None,
    output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, PatchTSTModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        if past_observed_mask is None: past_observed_mask = torch.ones_like(past_values)
        scaled_past_values, loc, scale = self.scaler(past_values, past_observed_mask)
        patched_values = self.patchifier(scaled_past_values)
        if self.do_mask_input: masked_values, mask = self.masking(patched_values)
        else: masked_values, mask = self.masking(patched_values), None
        encoder_output = self.encoder(patch_input=masked_values, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        if not return_dict:
            outputs = (encoder_output.last_hidden_state, encoder_output.hidden_states, encoder_output.attentions)
            outputs = outputs + (mask, loc, scale, patched_values)
            return tuple(v for v in outputs if v is not None)
        return PatchTSTModelOutput(last_hidden_state=encoder_output.last_hidden_state, hidden_states=encoder_output.hidden_states, attentions=encoder_output.attentions,
        mask=mask, loc=loc, scale=scale, patch_input=patched_values)
class PatchTSTMaskPretrainHead(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.dropout = nn.Dropout(config.head_dropout) if config.head_dropout > 0 else nn.Identity()
        self.linear = nn.Linear(config.d_model, config.patch_length)
        self.use_cls_token = config.use_cls_token
    def forward(self, embedding: torch.Tensor) -> torch.Tensor:
        embedding = self.linear(self.dropout(embedding))
        if self.use_cls_token: embedding = embedding[:, :, 1:, :]
        return embedding
@add_start_docstrings("The PatchTST for pretrain model.", PATCHTST_START_DOCSTRING)
class PatchTSTForPretraining(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig):
        super().__init__(config)
        config.do_mask_input = True
        self.model = PatchTSTModel(config=config)
        self.head = PatchTSTMaskPretrainHead(config)
        self.post_init()
    def forward(self, past_values: torch.Tensor, past_observed_mask: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, PatchTSTForPretrainingOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        model_output = self.model(past_values=past_values, past_observed_mask=past_observed_mask, output_hidden_states=output_hidden_states,
        output_attentions=output_attentions, return_dict=True)
        x_hat = self.head(model_output.last_hidden_state)
        loss = nn.MSELoss(reduction="none")
        loss_val = loss(x_hat, model_output.patch_input)
        masked_loss = (loss_val.mean(dim=-1) * model_output.mask).sum() / (model_output.mask.sum() + 1e-10)
        encoder_states = model_output.hidden_states
        if not return_dict:
            outputs = (x_hat,) + model_output[1:-4]
            outputs = (masked_loss,) + outputs if masked_loss is not None else outputs
            return outputs
        return PatchTSTForPretrainingOutput(loss=masked_loss, prediction_output=x_hat, hidden_states=encoder_states, attentions=model_output.attentions)
class PatchTSTClassificationHead(nn.Module):
    def __init__(self, config: PatchTSTConfig):
        super().__init__()
        self.use_cls_token = config.use_cls_token
        self.pooling_type = config.pooling_type
        self.flatten = nn.Flatten(start_dim=1)
        self.dropout = nn.Dropout(config.head_dropout) if config.head_dropout > 0 else nn.Identity()
        self.linear = nn.Linear(config.num_input_channels * config.d_model, config.num_targets)
    def forward(self, embedding: torch.Tensor):
        if self.use_cls_token: pooled_embedding = embedding[:, :, 0, :]
        elif self.pooling_type == "mean": pooled_embedding = embedding.mean(dim=2)
        elif self.pooling_type == "max": pooled_embedding = embedding.max(dim=2).values
        else: raise ValueError(f"pooling operator {self.pooling_type} is not implemented yet")
        pooled_embedding = self.flatten(pooled_embedding)
        output = self.linear(self.dropout(pooled_embedding))
        return output
@add_start_docstrings("The PatchTST for classification model.", PATCHTST_START_DOCSTRING)
class PatchTSTForClassification(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig):
        super().__init__(config)
        if config.do_mask_input:
            logger.warning("Setting `do_mask_input` parameter to False.")
            config.do_mask_input = False
        self.model = PatchTSTModel(config)
        self.head = PatchTSTClassificationHead(config)
        self.post_init()
    def forward(self, past_values: torch.Tensor, target_values: torch.Tensor = None, past_observed_mask: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    output_attentions: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[tuple, PatchTSTForClassificationOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        model_output = self.model(past_values=past_values, past_observed_mask=past_observed_mask, output_hidden_states=output_hidden_states,
        output_attentions=output_attentions, return_dict=True)
        y_hat = self.head(model_output.last_hidden_state)
        loss_val = None
        if target_values is not None:
            loss = nn.CrossEntropyLoss()
            loss_val = loss(y_hat, target_values)
        if not return_dict:
            outputs = (y_hat,) + model_output[1:-3]
            outputs = (loss_val,) + outputs if loss_val is not None else outputs
            return outputs
        return PatchTSTForClassificationOutput(loss=loss_val, prediction_logits=y_hat, hidden_states=model_output.hidden_states, attentions=model_output.attentions)
@add_start_docstrings("The PatchTST for regression Model.", PATCHTST_START_DOCSTRING)
class PatchTSTPredictionHead(nn.Module):
    def __init__(self, config: PatchTSTConfig, num_patches, distribution_output=None):
        super().__init__()
        self.share_projection = config.share_projection
        self.num_input_channels = config.num_input_channels
        self.use_cls_token = config.use_cls_token
        self.pooling_type = config.pooling_type
        if self.pooling_type or self.use_cls_token: head_dim = config.d_model
        else: head_dim = config.d_model * num_patches
        if not self.share_projection:
            self.projections = nn.ModuleList()
            self.dropouts = nn.ModuleList()
            self.flattens = nn.ModuleList()
            for i in range(self.num_input_channels):
                self.flattens.append(nn.Flatten(start_dim=2))
                if distribution_output is None: self.projections.append(nn.Linear(head_dim, config.prediction_length))
                else: self.projections.append(distribution_output.get_parameter_projection(head_dim))
                self.dropouts.append(nn.Dropout(config.head_dropout) if config.head_dropout > 0 else nn.Identity())
        else:
            self.flatten = nn.Flatten(start_dim=2)
            if distribution_output is None: self.projection = nn.Linear(head_dim, config.prediction_length)
            else: self.projection = distribution_output.get_parameter_projection(head_dim)
            self.dropout = nn.Dropout(config.head_dropout) if config.head_dropout > 0 else nn.Identity()
    def forward(self, embedding: torch.Tensor):
        if self.use_cls_token: pooled_embedding = embedding[:, :, 0, :]
        else:
            if self.pooling_type == "mean": pooled_embedding = embedding.mean(dim=2)
            elif self.pooling_type == "max": pooled_embedding = embedding.max(dim=2).values
            else: pooled_embedding = embedding
        if not self.share_projection:
            output = []
            for i in range(self.num_input_channels):
                pooled_embedding = self.flattens[i](pooled_embedding[:, i, :])
                pooled_embedding = self.dropouts[i](pooled_embedding)
                pooled_embedding = self.projections[i](pooled_embedding)
                output.append(pooled_embedding)
            output = torch.stack(output, dim=1)
        else:
            pooled_embedding = self.flatten(pooled_embedding)
            pooled_embedding = self.dropout(pooled_embedding)
            output = self.projection(pooled_embedding)
        if isinstance(output, tuple): output = tuple(z.transpose(2, 1) for z in output)
        else: output = output.transpose(2, 1)
        return output
@add_start_docstrings("The PatchTST for prediction model.", PATCHTST_START_DOCSTRING)
class PatchTSTForPrediction(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig):
        super().__init__(config)
        if config.do_mask_input:
            logger.warning("Setting `do_mask_input` parameter to False.")
            config.do_mask_input = False
        self.model = PatchTSTModel(config)
        if config.loss == "mse": self.distribution_output = None
        else:
            if config.distribution_output == "student_t": self.distribution_output = StudentTOutput(dim=config.prediction_length)
            elif config.distribution_output == "normal": self.distribution_output = NormalOutput(dim=config.prediction_length)
            elif config.distribution_output == "negative_binomial": self.distribution_output = NegativeBinomialOutput(dim=config.prediction_length)
            else: raise ValueError(f"Unknown distribution output {config.distribution_output}")
        self.head = PatchTSTPredictionHead(config, self.model.patchifier.num_patches, distribution_output=self.distribution_output)
        self.post_init()
    def forward(self, past_values: torch.Tensor, past_observed_mask: Optional[torch.Tensor] = None, future_values: Optional[torch.Tensor] = None,
    output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, PatchTSTForPredictionOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        model_output = self.model(past_values=past_values, past_observed_mask=past_observed_mask, output_hidden_states=output_hidden_states,
        output_attentions=output_attentions, return_dict=True)
        y_hat = self.head(model_output.last_hidden_state)
        loss_val = None
        if self.distribution_output: y_hat_out = y_hat
        else: y_hat_out = y_hat * model_output.scale + model_output.loc
        if future_values is not None:
            if self.distribution_output:
                distribution = self.distribution_output.distribution(y_hat, loc=model_output.loc, scale=model_output.scale)
                loss_val = nll(distribution, future_values)
                loss_val = weighted_average(loss_val)
            else:
                loss = nn.MSELoss(reduction="mean")
                loss_val = loss(y_hat_out, future_values)
        loc = model_output.loc
        scale = model_output.scale
        if not return_dict:
            outputs = (y_hat_out,) + model_output[1:-1]
            outputs = (loss_val,) + outputs if loss_val is not None else outputs
            return outputs
        return PatchTSTForPredictionOutput(loss=loss_val, prediction_outputs=y_hat_out, hidden_states=model_output.hidden_states, attentions=model_output.attentions, loc=loc, scale=scale)
    def generate(self, past_values: torch.Tensor, past_observed_mask: Optional[torch.Tensor] = None) -> SamplePatchTSTOutput:
        num_parallel_samples = self.config.num_parallel_samples
        outputs = self(past_values=past_values, future_values=None, past_observed_mask=past_observed_mask, output_hidden_states=False)
        if self.distribution_output:
            distribution = self.distribution_output.distribution(outputs.prediction_outputs, loc=outputs.loc, scale=outputs.scale)
            samples = [distribution.sample() for _ in range(num_parallel_samples)]
            samples = torch.stack(samples, dim=1)
        else: samples = outputs.prediction_outputs.unsqueeze(1)
        return SamplePatchTSTOutput(sequences=samples)
class PatchTSTRegressionHead(nn.Module):
    def __init__(self, config: PatchTSTConfig, distribution_output=None):
        super().__init__()
        self.y_range = config.output_range
        self.use_cls_token = config.use_cls_token
        self.pooling_type = config.pooling_type
        self.distribution_output = distribution_output
        head_dim = config.num_input_channels * config.d_model
        self.flatten = nn.Flatten(start_dim=1)
        self.dropout = nn.Dropout(config.head_dropout) if config.head_dropout > 0 else nn.Identity()
        if distribution_output is None: self.projection = nn.Linear(head_dim, config.num_targets)
        else: self.projection = distribution_output.get_parameter_projection(head_dim)
    def forward(self, embedding: torch.Tensor):
        if self.use_cls_token: pooled_embedding = embedding[:, :, 0, :]
        elif self.pooling_type == "mean": pooled_embedding = embedding.mean(dim=2)
        elif self.pooling_type == "max": pooled_embedding = embedding.max(dim=2).values
        else: raise ValueError(f"pooling operator {self.pooling_type} is not implemented yet")
        pooled_embedding = self.dropout(self.flatten(pooled_embedding))
        output = self.projection(pooled_embedding)
        if (self.distribution_output is None) & (self.y_range is not None): output = torch.sigmoid(output) * (self.y_range[1] - self.y_range[0]) + self.y_range[0]
        return output
@add_start_docstrings("The PatchTST for regression model.", PATCHTST_START_DOCSTRING)
class PatchTSTForRegression(PatchTSTPreTrainedModel):
    def __init__(self, config: PatchTSTConfig):
        super().__init__(config)
        if config.do_mask_input:
            logger.warning("Setting `do_mask_input` parameter to False.")
            config.do_mask_input = False
        self.model = PatchTSTModel(config)
        if config.loss == "mse": self.distribution_output = None
        else:
            if config.distribution_output == "student_t": self.distribution_output = StudentTOutput(dim=config.num_targets)
            elif config.distribution_output == "normal": self.distribution_output = NormalOutput(dim=config.num_targets)
            elif config.distribution_output == "negative_binomial": self.distribution_output = NegativeBinomialOutput(dim=config.num_targets)
            else: raise ValueError(f"Unknown distribution output {config.distribution_output}")
        self.head = PatchTSTRegressionHead(config, self.distribution_output)
        self.post_init()
    def forward(self, past_values: torch.Tensor, target_values: torch.Tensor = None, past_observed_mask: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None,
    output_attentions: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[tuple, PatchTSTForRegressionOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        model_output = self.model(past_values=past_values, past_observed_mask=past_observed_mask, output_hidden_states=output_hidden_states, output_attentions=output_attentions, return_dict=True)
        y_hat = self.head(model_output.last_hidden_state)
        loss = None
        if target_values is not None:
            if self.distribution_output:
                distribution = self.distribution_output.distribution(y_hat)
                y_hat = tuple([item.view(-1, self.config.num_targets) for item in y_hat])
                loss = nll(distribution, target_values)
                loss = weighted_average(loss)
            else:
                loss = nn.MSELoss(reduction="mean")
                loss = loss(y_hat, target_values)
        if not return_dict:
            outputs = (y_hat,) + model_output[1:-3]
            outputs = (loss,) + outputs if loss is not None else outputs
            return outputs
        return PatchTSTForRegressionOutput(loss=loss, regression_outputs=y_hat, hidden_states=model_output.hidden_states, attentions=model_output.attentions)
    def generate(self, past_values: torch.Tensor, past_observed_mask: Optional[torch.Tensor] = None) -> SamplePatchTSTOutput:
        num_parallel_samples = self.config.num_parallel_samples
        outputs = self(past_values=past_values, target_values=None, past_observed_mask=past_observed_mask, output_hidden_states=False)
        distribution = self.distribution_output.distribution(outputs.regression_outputs)
        samples = [distribution.sample() for _ in range(num_parallel_samples)]
        samples = torch.stack(samples, dim=1).view(-1, num_parallel_samples, self.config.num_targets)
        return SamplePatchTSTOutput(sequences=samples)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
