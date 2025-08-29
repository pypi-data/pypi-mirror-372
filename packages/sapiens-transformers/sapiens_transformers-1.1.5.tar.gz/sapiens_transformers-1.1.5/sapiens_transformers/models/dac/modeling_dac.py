"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings)
from .configuration_dac import DacConfig
_CONFIG_FOR_DOC = "DacConfig"
@dataclass
class DacOutput(ModelOutput):
    """Args:"""
    loss: torch.FloatTensor = None
    audio_values: torch.FloatTensor = None
    quantized_representation: torch.FloatTensor = None
    audio_codes: torch.LongTensor = None
    projected_latents: torch.FloatTensor = None
@dataclass
class DacEncoderOutput(ModelOutput):
    """Args:"""
    loss: torch.FloatTensor = None
    quantized_representation: torch.FloatTensor = None
    audio_codes: torch.FloatTensor = None
    projected_latents: torch.FloatTensor = None
@dataclass
class DacDecoderOutput(ModelOutput):
    """Args:"""
    audio_values: torch.FloatTensor = None
class Snake1d(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.alpha = nn.Parameter(torch.ones(1, hidden_dim, 1))
    def forward(self, hidden_states):
        shape = hidden_states.shape
        hidden_states = hidden_states.reshape(shape[0], shape[1], -1)
        hidden_states = hidden_states + (self.alpha + 1e-9).reciprocal() * torch.sin(self.alpha * hidden_states).pow(2)
        hidden_states = hidden_states.reshape(shape)
        return hidden_states
class DacVectorQuantize(nn.Module):
    def __init__(self, config: DacConfig):
        super().__init__()
        self.in_proj = nn.Conv1d(config.hidden_size, config.codebook_dim, kernel_size=1)
        self.out_proj = nn.Conv1d(config.codebook_dim, config.hidden_size, kernel_size=1)
        self.codebook = nn.Embedding(config.codebook_size, config.codebook_dim)
    def forward(self, hidden_state):
        projected_latents = self.in_proj(hidden_state)
        quantized_representation, audio_codes = self.decode_latents(projected_latents)
        commitment_loss = F.mse_loss(projected_latents, quantized_representation.detach(), reduction="mean")
        codebook_loss = F.mse_loss(quantized_representation, projected_latents.detach(), reduction="mean")
        quantized_representation = projected_latents + (quantized_representation - projected_latents).detach()
        quantized_representation = self.out_proj(quantized_representation)
        return quantized_representation, commitment_loss, codebook_loss, audio_codes, projected_latents
    def decode_latents(self, hidden_states):
        batch_size, hidden_dim, sequence_length = hidden_states.shape
        encodings = hidden_states.permute(0, 2, 1).reshape(batch_size * sequence_length, hidden_dim)
        codebook = self.codebook.weight
        encodings = F.normalize(encodings)
        codebook = F.normalize(codebook)
        l2_norm = encodings.pow(2).sum(1, keepdim=True)
        dist = -(l2_norm - 2 * encodings @ codebook.t()) + codebook.pow(2).sum(1, keepdim=True).t()
        indices = dist.max(1)[1]
        indices = indices.reshape(hidden_states.size(0), -1)
        quantized_representation = self.codebook(indices).transpose(1, 2)
        return quantized_representation, indices
class DacResidualUnit(nn.Module):
    def __init__(self, dimension: int = 16, dilation: int = 1):
        super().__init__()
        pad = ((7 - 1) * dilation) // 2
        self.snake1 = Snake1d(dimension)
        self.conv1 = nn.Conv1d(dimension, dimension, kernel_size=7, dilation=dilation, padding=pad)
        self.snake2 = Snake1d(dimension)
        self.conv2 = nn.Conv1d(dimension, dimension, kernel_size=1)
    def forward(self, hidden_state):
        output_tensor = hidden_state
        output_tensor = self.conv1(self.snake1(output_tensor))
        output_tensor = self.conv2(self.snake2(output_tensor))
        padding = (hidden_state.shape[-1] - output_tensor.shape[-1]) // 2
        if padding > 0: hidden_state = hidden_state[..., padding:-padding]
        output_tensor = hidden_state + output_tensor
        return output_tensor
class DacEncoderBlock(nn.Module):
    def __init__(self, config: DacConfig, stride: int = 1, stride_index: int = 1):
        super().__init__()
        dimension = config.encoder_hidden_size * 2**stride_index
        self.res_unit1 = DacResidualUnit(dimension // 2, dilation=1)
        self.res_unit2 = DacResidualUnit(dimension // 2, dilation=3)
        self.res_unit3 = DacResidualUnit(dimension // 2, dilation=9)
        self.snake1 = Snake1d(dimension // 2)
        self.conv1 = nn.Conv1d(dimension // 2, dimension, kernel_size=2 * stride, stride=stride, padding=math.ceil(stride / 2))
    def forward(self, hidden_state):
        hidden_state = self.res_unit1(hidden_state)
        hidden_state = self.res_unit2(hidden_state)
        hidden_state = self.snake1(self.res_unit3(hidden_state))
        hidden_state = self.conv1(hidden_state)
        return hidden_state
class DacDecoderBlock(nn.Module):
    def __init__(self, config: DacConfig, stride: int = 1, stride_index: int = 1):
        super().__init__()
        input_dim = config.decoder_hidden_size // 2**stride_index
        output_dim = config.decoder_hidden_size // 2 ** (stride_index + 1)
        self.snake1 = Snake1d(input_dim)
        self.conv_t1 = nn.ConvTranspose1d(input_dim, output_dim, kernel_size=2 * stride, stride=stride, padding=math.ceil(stride / 2))
        self.res_unit1 = DacResidualUnit(output_dim, dilation=1)
        self.res_unit2 = DacResidualUnit(output_dim, dilation=3)
        self.res_unit3 = DacResidualUnit(output_dim, dilation=9)
    def forward(self, hidden_state):
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv_t1(hidden_state)
        hidden_state = self.res_unit1(hidden_state)
        hidden_state = self.res_unit2(hidden_state)
        hidden_state = self.res_unit3(hidden_state)
        return hidden_state
class DacResidualVectorQuantize(nn.Module):
    def __init__(self, config: DacConfig):
        super().__init__()
        n_codebooks = config.n_codebooks
        quantizer_dropout = config.quantizer_dropout
        self.n_codebooks = n_codebooks
        self.quantizers = nn.ModuleList([DacVectorQuantize(config) for i in range(config.n_codebooks)])
        self.quantizer_dropout = quantizer_dropout
    def forward(self, hidden_state, n_quantizers: int = None):
        quantized_representation = 0
        residual = hidden_state
        commitment_loss = 0
        codebook_loss = 0
        audio_codes = []
        projected_latents = []
        n_quantizers = n_quantizers if n_quantizers is not None else self.n_codebooks
        if self.training:
            n_quantizers = torch.ones((hidden_state.shape[0],)) * self.n_codebooks + 1
            dropout = torch.randint(1, self.n_codebooks + 1, (hidden_state.shape[0],))
            n_dropout = int(hidden_state.shape[0] * self.quantizer_dropout)
            n_quantizers[:n_dropout] = dropout[:n_dropout]
            n_quantizers = n_quantizers.to(hidden_state.device)
        for i, quantizer in enumerate(self.quantizers):
            if self.training is False and i >= n_quantizers: break
            quantized_representation_i, commitment_loss_i, codebook_loss_i, indices_i, projected_latents_i = quantizer(residual)
            mask = torch.full((hidden_state.shape[0],), fill_value=i, device=hidden_state.device) < n_quantizers
            quantized_representation = quantized_representation + quantized_representation_i * mask[:, None, None]
            residual = residual - quantized_representation_i
            commitment_loss += commitment_loss_i * mask
            codebook_loss += codebook_loss_i * mask
            audio_codes.append(indices_i)
            projected_latents.append(projected_latents_i)
        audio_codes = torch.stack(audio_codes, dim=1)
        projected_latents = torch.cat(projected_latents, dim=1)
        return quantized_representation, audio_codes, projected_latents, commitment_loss, codebook_loss
    def from_codes(self, audio_codes: torch.Tensor):
        quantized_representation = 0.0
        projected_latents = []
        n_codebooks = audio_codes.shape[1]
        for i in range(n_codebooks):
            projected_latents_i = self.quantizers[i].codebook(audio_codes[:, i, :]).transpose(1, 2)
            projected_latents.append(projected_latents_i)
            quantized_representation += self.quantizers[i].out_proj(projected_latents_i)
        return quantized_representation, torch.cat(projected_latents, dim=1), audio_codes
    def from_latents(self, latents: torch.Tensor):
        quantized_representation = 0
        quantized_latents = []
        codes = []
        codebook_dims_tensor = torch.tensor([0] + [q.codebook_dim for q in self.quantizers])
        dims = torch.cumsum(codebook_dims_tensor, dim=0)
        n_codebooks = np.where(dims <= latents.shape[1])[0].max(axis=0, keepdims=True)[0]
        for i in range(n_codebooks):
            hidden_dim_j, hidden_dim_k = dims[i], dims[i + 1]
            quantized_latents_i, codes_i = self.quantizers[i].decode_latents(latents[:, hidden_dim_j:hidden_dim_k, :])
            quantized_latents.append(quantized_latents_i)
            codes.append(codes_i)
            quantized_representation_i = self.quantizers[i].out_proj(quantized_latents_i)
            quantized_representation = quantized_representation + quantized_representation_i
        return quantized_representation, torch.cat(quantized_latents, dim=1)
class DacDecoder(nn.Module):
    def __init__(self, config: DacConfig):
        super().__init__()
        input_channel = config.hidden_size
        channels = config.decoder_hidden_size
        strides = config.upsampling_ratios
        self.conv1 = nn.Conv1d(input_channel, channels, kernel_size=7, padding=3)
        block = []
        for stride_index, stride in enumerate(strides): block += [DacDecoderBlock(config, stride, stride_index)]
        self.block = nn.ModuleList(block)
        output_dim = config.decoder_hidden_size // 2 ** (stride_index + 1)
        self.snake1 = Snake1d(output_dim)
        self.conv2 = nn.Conv1d(output_dim, 1, kernel_size=7, padding=3)
        self.tanh = nn.Tanh()
    def forward(self, hidden_state):
        hidden_state = self.conv1(hidden_state)
        for layer in self.block: hidden_state = layer(hidden_state)
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv2(hidden_state)
        hidden_state = self.tanh(hidden_state)
        return hidden_state
class DacEncoder(nn.Module):
    def __init__(self, config: DacConfig):
        super().__init__()
        strides = config.downsampling_ratios
        self.conv1 = nn.Conv1d(1, config.encoder_hidden_size, kernel_size=7, padding=3)
        self.block = []
        for stride_index, stride in enumerate(strides):
            stride_index = stride_index + 1
            self.block += [DacEncoderBlock(config, stride=stride, stride_index=stride_index)]
        self.block = nn.ModuleList(self.block)
        d_model = config.encoder_hidden_size * 2**stride_index
        self.snake1 = Snake1d(d_model)
        self.conv2 = nn.Conv1d(d_model, config.hidden_size, kernel_size=3, padding=1)
    def forward(self, hidden_state):
        hidden_state = self.conv1(hidden_state)
        for module in self.block: hidden_state = module(hidden_state)
        hidden_state = self.snake1(hidden_state)
        hidden_state = self.conv2(hidden_state)
        return hidden_state
class DacPreTrainedModel(PreTrainedModel):
    config_class = DacConfig
    base_model_prefix = "dac"
    main_input_name = "input_values"
    def _init_weights(self, module):
        if isinstance(module, nn.Conv1d):
            nn.init.trunc_normal_(module.weight, std=0.02)
            nn.init.constant_(module.bias, 0)
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        for layer in self.quantizer.quantizers:
            weight_norm(layer.in_proj)
            weight_norm(layer.out_proj)
        weight_norm(self.encoder.conv1)
        weight_norm(self.encoder.conv2)
        for layer in self.encoder.block:
            weight_norm(layer.conv1)
            weight_norm(layer.res_unit1.conv1)
            weight_norm(layer.res_unit1.conv2)
            weight_norm(layer.res_unit2.conv1)
            weight_norm(layer.res_unit2.conv2)
            weight_norm(layer.res_unit3.conv1)
            weight_norm(layer.res_unit3.conv2)
        weight_norm(self.decoder.conv1)
        weight_norm(self.decoder.conv2)
        for layer in self.decoder.block:
            weight_norm(layer.conv_t1)
            weight_norm(layer.res_unit1.conv1)
            weight_norm(layer.res_unit1.conv2)
            weight_norm(layer.res_unit2.conv1)
            weight_norm(layer.res_unit2.conv2)
            weight_norm(layer.res_unit3.conv1)
            weight_norm(layer.res_unit3.conv2)
    def remove_weight_norm(self):
        for layer in self.quantizer.quantizers:
            nn.utils.remove_weight_norm(layer.in_proj)
            nn.utils.remove_weight_norm(layer.out_proj)
        nn.utils.remove_weight_norm(self.encoder.conv1)
        nn.utils.remove_weight_norm(self.encoder.conv2)
        for layer in self.encoder.block:
            nn.utils.remove_weight_norm(layer.conv1)
            nn.utils.remove_weight_norm(layer.res_unit1.conv1)
            nn.utils.remove_weight_norm(layer.res_unit1.conv2)
            nn.utils.remove_weight_norm(layer.res_unit2.conv1)
            nn.utils.remove_weight_norm(layer.res_unit2.conv2)
            nn.utils.remove_weight_norm(layer.res_unit3.conv1)
            nn.utils.remove_weight_norm(layer.res_unit3.conv2)
        nn.utils.remove_weight_norm(self.decoder.conv1)
        nn.utils.remove_weight_norm(self.decoder.conv2)
        for layer in self.decoder.block:
            nn.utils.remove_weight_norm(layer.conv_t1)
            nn.utils.remove_weight_norm(layer.res_unit1.conv1)
            nn.utils.remove_weight_norm(layer.res_unit1.conv2)
            nn.utils.remove_weight_norm(layer.res_unit2.conv1)
            nn.utils.remove_weight_norm(layer.res_unit2.conv2)
            nn.utils.remove_weight_norm(layer.res_unit3.conv1)
            nn.utils.remove_weight_norm(layer.res_unit3.conv2)
DAC_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`DacConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
DAC_INPUTS_DOCSTRING = r"""
    Args:
        input_values (`torch.Tensor` of shape `(batch_size, 1, time_steps)`).
            Audio data to encode,
        n_quantizers (`int`, *optional*):
            Number of quantizers to use. If `None`, all quantizers are used. Default is `None`.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The DAC (Descript Audio Codec) model.", DAC_START_DOCSTRING)
class DacModel(DacPreTrainedModel):
    def __init__(self, config: DacConfig):
        super().__init__(config)
        self.config = config
        self.encoder = DacEncoder(config)
        self.decoder = DacDecoder(config)
        self.quantizer = DacResidualVectorQuantize(config)
        self.bits_per_codebook = int(math.log2(self.config.codebook_size))
        if 2**self.bits_per_codebook != self.config.codebook_size: raise ValueError("The codebook_size must be a power of 2.")
        self.post_init()
    def encode(self, input_values: torch.Tensor, n_quantizers: int = None, return_dict: Optional[bool] = None):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        quantized_representation = self.encoder(input_values)
        quantized_representation, audio_codes, projected_latents, commitment_loss, codebook_loss = self.quantizer(quantized_representation, n_quantizers)
        loss = self.config.commitment_loss_weight * commitment_loss + self.config.codebook_loss_weight * codebook_loss
        if not return_dict: return (loss, quantized_representation, audio_codes, projected_latents)
        return DacEncoderOutput(loss, quantized_representation, audio_codes, projected_latents)
    def decode(self, quantized_representation: Optional[torch.Tensor], audio_codes: Optional[torch.Tensor] = None, return_dict: Optional[bool] = None):
        if quantized_representation is None and audio_codes is None: raise ValueError("Either `quantized_representation` or `audio_codes` must be provided.")
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if audio_codes is not None: quantized_representation = self.quantizer.from_codes(audio_codes)[0]
        audio_values = self.decoder(quantized_representation).squeeze(1)
        if not return_dict: return (audio_values,)
        return DacDecoderOutput(audio_values)
    @add_start_docstrings_to_model_forward(DAC_INPUTS_DOCSTRING)
    def forward(self, input_values: torch.Tensor, n_quantizers: int = None, return_dict: Optional[bool] = None):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        length = input_values.shape[-1]
        loss, quantized_representation, audio_codes, projected_latents = self.encode(input_values, n_quantizers, return_dict=False)
        audio_values = self.decode(quantized_representation, return_dict=False)[0][..., :length]
        if not return_dict: return (loss, audio_values, quantized_representation, audio_codes, projected_latents)
        return DacOutput(loss, audio_values, quantized_representation, audio_codes, projected_latents)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
