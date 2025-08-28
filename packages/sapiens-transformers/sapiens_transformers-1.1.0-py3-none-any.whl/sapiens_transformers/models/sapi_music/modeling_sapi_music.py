"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward
from torch import nn as sapiens_technology_neural_networks
from .configuration_sapi_music import SAPIMusicConfig
from ...modeling_utils import SapiensPreTrainedModel
from typing import Tuple, List, Optional, Union
import torch as sapiens_technology_torch
import math as sapiens_technology_math
from dataclasses import dataclass
_CONFIG_FOR_DOC = "SAPIMusicConfig"
class SAPIMusicConv1d(sapiens_technology_neural_networks.Module):
    def __init__(self, config, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1, dilation: int = 1):
        super().__init__()
        self.causal = config.use_causal_conv
        self.pad_mode = config.pad_mode
        self.norm_type = config.norm_type
        if self.norm_type not in ["weight_norm", "time_group_norm"]: raise ValueError(f'self.norm_type must be one of `"weight_norm"`, `"time_group_norm"`), got {self.norm_type}')
        self.conv = sapiens_technology_neural_networks.Conv1d(in_channels, out_channels, kernel_size, stride, dilation=dilation)
        weight_norm = sapiens_technology_neural_networks.utils.weight_norm
        if hasattr(sapiens_technology_neural_networks.utils.parametrizations, "weight_norm"): weight_norm = sapiens_technology_neural_networks.utils.parametrizations.weight_norm
        if self.norm_type == "weight_norm": self.conv = weight_norm(self.conv)
        elif self.norm_type == "time_group_norm": self.norm = sapiens_technology_neural_networks.GroupNorm(1, out_channels)
        kernel_size = self.conv.kernel_size[0]
        stride = sapiens_technology_torch.tensor(self.conv.stride[0], dtype=sapiens_technology_torch.int64)
        dilation = self.conv.dilation[0]
        kernel_size = sapiens_technology_torch.tensor((kernel_size - 1) * dilation + 1, dtype=sapiens_technology_torch.int64)
        self.register_buffer("stride", stride, persistent=False)
        self.register_buffer("kernel_size", kernel_size, persistent=False)
        self.register_buffer("padding_total", (kernel_size - stride).clone().detach().to(dtype=sapiens_technology_torch.int64), persistent=False)
    def _get_extra_padding_for_conv1d(self, hidden_states: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        length = hidden_states.shape[-1]
        n_frames = (length - self.kernel_size + self.padding_total) / self.stride + 1
        n_frames = sapiens_technology_torch.ceil(n_frames).to(sapiens_technology_torch.int64) - 1
        ideal_length = n_frames * self.stride + self.kernel_size - self.padding_total
        return ideal_length - length
    @staticmethod
    def _pad1d(hidden_states: sapiens_technology_torch.Tensor, paddings: Tuple[int, int], mode: str = "zero", value: float = 0.0):
        length = hidden_states.shape[-1]
        padding_left, padding_right = paddings
        if not mode == "reflect": return sapiens_technology_neural_networks.functional.pad(hidden_states, paddings, mode, value)
        max_pad = max(padding_left, padding_right)
        extra_pad = 0
        if length <= max_pad:
            extra_pad = max_pad - length + 1
            hidden_states = sapiens_technology_neural_networks.functional.pad(hidden_states, (0, extra_pad))
        padded = sapiens_technology_neural_networks.functional.pad(hidden_states, paddings, mode, value)
        end = padded.shape[-1] - extra_pad
        return padded[..., :end]
    def forward(self, hidden_states):
        extra_padding = self._get_extra_padding_for_conv1d(hidden_states)
        if self.causal: hidden_states = self._pad1d(hidden_states, (self.padding_total, extra_padding), mode=self.pad_mode)
        else:
            padding_right = self.padding_total // 2
            padding_left = self.padding_total - padding_right
            hidden_states = self._pad1d(hidden_states, (padding_left, padding_right + extra_padding), mode=self.pad_mode)
        hidden_states = self.conv(hidden_states)
        if self.norm_type == "time_group_norm": hidden_states = self.norm(hidden_states)
        return hidden_states
class SAPIMusicConvTranspose1d(sapiens_technology_neural_networks.Module):
    def __init__(self, config, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1):
        super().__init__()
        self.causal = config.use_causal_conv
        self.trim_right_ratio = config.trim_right_ratio
        self.norm_type = config.norm_type
        if self.norm_type not in ["weight_norm", "time_group_norm"]: raise ValueError(f'self.norm_type must be one of `"weight_norm"`, `"time_group_norm"`), got {self.norm_type}')
        self.conv = sapiens_technology_neural_networks.ConvTranspose1d(in_channels, out_channels, kernel_size, stride)
        weight_norm = sapiens_technology_neural_networks.utils.weight_norm
        if hasattr(sapiens_technology_neural_networks.utils.parametrizations, "weight_norm"): weight_norm = sapiens_technology_neural_networks.utils.parametrizations.weight_norm
        if config.norm_type == "weight_norm": self.conv = weight_norm(self.conv)
        elif config.norm_type == "time_group_norm": self.norm = sapiens_technology_neural_networks.GroupNorm(1, out_channels)
        if not (self.causal or self.trim_right_ratio == 1.0): raise ValueError("`trim_right_ratio` != 1.0 only makes sense for causal convolutions")
    def forward(self, hidden_states):
        kernel_size = self.conv.kernel_size[0]
        stride = self.conv.stride[0]
        padding_total = kernel_size - stride
        hidden_states = self.conv(hidden_states)
        if self.norm_type == "time_group_norm": hidden_states = self.norm(hidden_states)
        if self.causal: padding_right = sapiens_technology_math.ceil(padding_total * self.trim_right_ratio)
        else: padding_right = padding_total // 2
        padding_left = padding_total - padding_right
        end = hidden_states.shape[-1] - padding_right
        hidden_states = hidden_states[..., padding_left:end]
        return hidden_states
class SAPIMusicLSTM(sapiens_technology_neural_networks.Module):
    def __init__(self, config, dimension):
        super().__init__()
        self.lstm = sapiens_technology_neural_networks.LSTM(dimension, dimension, config.num_lstm_layers)
    def forward(self, hidden_states):
        hidden_states = hidden_states.permute(2, 0, 1)
        hidden_states = self.lstm(hidden_states)[0] + hidden_states
        hidden_states = hidden_states.permute(1, 2, 0)
        return hidden_states
class SAPIMusicResnetBlock(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig, dim: int, dilations: List[int]):
        super().__init__()
        kernel_sizes = (config.residual_kernel_size, 1)
        if len(kernel_sizes) != len(dilations): raise ValueError("Number of kernel sizes should match number of dilations")
        hidden = dim // config.compress
        block = []
        for i, (kernel_size, dilation) in enumerate(zip(kernel_sizes, dilations)):
            in_chs = dim if i == 0 else hidden
            out_chs = dim if i == len(kernel_sizes) - 1 else hidden
            block += [sapiens_technology_neural_networks.ELU()]
            block += [SAPIMusicConv1d(config, in_chs, out_chs, kernel_size, dilation=dilation)]
        self.block = sapiens_technology_neural_networks.ModuleList(block)
        if config.use_conv_shortcut: self.shortcut = SAPIMusicConv1d(config, dim, dim, kernel_size=1)
        else: self.shortcut = sapiens_technology_neural_networks.Identity()
    def forward(self, hidden_states):
        residual = hidden_states
        for layer in self.block: hidden_states = layer(hidden_states)
        return self.shortcut(residual) + hidden_states
SAPI_MUSIC_INPUTS_DOCSTRING = r"""
    Args:
        input_values (`torch.FloatTensor` of shape `(batch_size, channels, sequence_length)`, *optional*):
            Raw audio input converted to Float and padded to the approriate length in order to be encoded using chunks
            of length self.chunk_length and a stride of `config.chunk_stride`.
        padding_mask (`torch.BoolTensor` of shape `(batch_size, channels, sequence_length)`, *optional*):
            Mask to avoid computing scaling factors on padding token indices (can we avoid computing conv on these+).
            Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            <Tip warning={true}>
             `padding_mask` should always be passed, unless the input was truncated or not padded. This is because in
             order to process tensors effectively, the input audio should be padded so that `input_length % stride =
             step` with `step = chunk_length-stride`. This ensures that all chunks are of the same shape
            </Tip>
        bandwidth (`float`, *optional*):
            The target bandwidth. Must be one of `config.target_bandwidths`. If `None`, uses the smallest possible
            bandwidth. bandwidth is represented as a thousandth of what it is, e.g. 6kbps bandwidth is represented as
            `bandwidth == 6.0`
        audio_codes (`torch.LongTensor`  of shape `(batch_size, nb_chunks, chunk_length)`, *optional*):
            Discret code embeddings computed using `model.encode`.
        audio_scales (`torch.Tensor` of shape `(batch_size, nb_chunks)`, *optional*):
            Scaling factor for each `audio_codes` input.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
SAPI_MUSIC_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SAPIMusicConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
class SAPIMusicEncoder(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__()
        model = [SAPIMusicConv1d(config, config.audio_channels, config.num_filters, config.kernel_size)]
        scaling = 1
        for ratio in reversed(config.upsampling_ratios):
            current_scale = scaling * config.num_filters
            for j in range(config.num_residual_layers): model += [SAPIMusicResnetBlock(config, current_scale, [config.dilation_growth_rate**j, 1])]
            model += [sapiens_technology_neural_networks.ELU()]
            model += [SAPIMusicConv1d(config, current_scale, current_scale * 2, kernel_size=ratio * 2, stride=ratio)]
            scaling *= 2
        model += [SAPIMusicLSTM(config, scaling * config.num_filters)]
        model += [sapiens_technology_neural_networks.ELU()]
        model += [SAPIMusicConv1d(config, scaling * config.num_filters, config.hidden_size, config.last_kernel_size)]
        self.layers = sapiens_technology_neural_networks.ModuleList(model)
    def forward(self, hidden_states):
        for layer in self.layers: hidden_states = layer(hidden_states)
        return hidden_states
class SAPIMusicDecoder(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__()
        scaling = int(2 ** len(config.upsampling_ratios))
        model = [SAPIMusicConv1d(config, config.hidden_size, scaling * config.num_filters, config.kernel_size)]
        model += [SAPIMusicLSTM(config, scaling * config.num_filters)]
        for ratio in config.upsampling_ratios:
            current_scale = scaling * config.num_filters
            model += [sapiens_technology_neural_networks.ELU()]
            model += [SAPIMusicConvTranspose1d(config, current_scale, current_scale // 2, kernel_size=ratio * 2, stride=ratio)]
            for j in range(config.num_residual_layers): model += [SAPIMusicResnetBlock(config, current_scale // 2, (config.dilation_growth_rate**j, 1))]
            scaling //= 2
        model += [sapiens_technology_neural_networks.ELU()]
        model += [SAPIMusicConv1d(config, config.num_filters, config.audio_channels, config.last_kernel_size)]
        self.layers = sapiens_technology_neural_networks.ModuleList(model)
    def forward(self, hidden_states):
        for layer in self.layers: hidden_states = layer(hidden_states)
        return hidden_states
class SAPIMusicEuclideanCodebook(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__()
        embed = sapiens_technology_torch.zeros(config.codebook_size, config.codebook_dim)
        self.codebook_size = config.codebook_size
        self.register_buffer("inited", sapiens_technology_torch.Tensor([True]))
        self.register_buffer("cluster_size", sapiens_technology_torch.zeros(config.codebook_size))
        self.register_buffer("embed", embed)
        self.register_buffer("embed_avg", embed.clone())
    def quantize(self, hidden_states):
        embed = self.embed.t()
        scaled_states = hidden_states.pow(2).sum(1, keepdim=True)
        dist = -(scaled_states - 2 * hidden_states @ embed + embed.pow(2).sum(0, keepdim=True))
        embed_ind = dist.max(dim=-1).indices
        return embed_ind
    def encode(self, hidden_states):
        shape = hidden_states.shape
        hidden_states = hidden_states.reshape((-1, shape[-1]))
        embed_ind = self.quantize(hidden_states)
        embed_ind = embed_ind.view(*shape[:-1])
        return embed_ind
    def decode(self, embed_ind):
        quantize = sapiens_technology_neural_networks.functional.embedding(embed_ind, self.embed)
        return quantize
class SAPIMusicVectorQuantization(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__()
        self.codebook = SAPIMusicEuclideanCodebook(config)
    def encode(self, hidden_states):
        hidden_states = hidden_states.permute(0, 2, 1)
        embed_in = self.codebook.encode(hidden_states)
        return embed_in
    def decode(self, embed_ind):
        quantize = self.codebook.decode(embed_ind)
        quantize = quantize.permute(0, 2, 1)
        return quantize
class SAPIMusicResidualVectorQuantizer(sapiens_technology_neural_networks.Module):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__()
        self.codebook_size = config.codebook_size
        self.frame_rate = config.frame_rate
        self.num_quantizers = config.num_quantizers
        self.layers = sapiens_technology_neural_networks.ModuleList([SAPIMusicVectorQuantization(config) for _ in range(config.num_quantizers)])
    def get_num_quantizers_for_bandwidth(self, bandwidth: Optional[float] = None) -> int:
        bw_per_q = sapiens_technology_math.log2(self.codebook_size) * self.frame_rate
        num_quantizers = self.num_quantizers
        if bandwidth is not None and bandwidth > 0.0: num_quantizers = int(max(1, sapiens_technology_math.floor(bandwidth * 1000 / bw_per_q)))
        return num_quantizers
    def encode(self, embeddings: sapiens_technology_torch.Tensor, bandwidth: Optional[float] = None) -> sapiens_technology_torch.Tensor:
        num_quantizers = self.get_num_quantizers_for_bandwidth(bandwidth)
        residual = embeddings
        all_indices = []
        for layer in self.layers[:num_quantizers]:
            indices = layer.encode(residual)
            quantized = layer.decode(indices)
            residual = residual - quantized
            all_indices.append(indices)
        out_indices = sapiens_technology_torch.stack(all_indices)
        return out_indices
    def decode(self, codes: sapiens_technology_torch.Tensor) -> sapiens_technology_torch.Tensor:
        quantized_out = sapiens_technology_torch.tensor(0.0, device=codes.device)
        for i, indices in enumerate(codes):
            layer = self.layers[i]
            quantized = layer.decode(indices)
            quantized_out = quantized_out + quantized
        return quantized_out
class SAPIMusicPreTrainedModel(SapiensPreTrainedModel):
    config_class = SAPIMusicConfig
    base_model_prefix = "sapi_music"
    main_input_name = "input_values"
    def _init_weights(self, module):
        if isinstance(module, sapiens_technology_neural_networks.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, (sapiens_technology_neural_networks.LayerNorm, sapiens_technology_neural_networks.GroupNorm)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, sapiens_technology_neural_networks.Conv1d):
            sapiens_technology_neural_networks.init.kaiming_normal_(module.weight)
            if module.bias is not None:
                k = sapiens_technology_math.sqrt(module.groups / (module.in_channels * module.kernel_size[0]))
                sapiens_technology_neural_networks.init.uniform_(module.bias, a=-k, b=k)
        elif isinstance(module, sapiens_technology_neural_networks.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, sapiens_technology_neural_networks.LSTM):
            for name, param in module.named_parameters():
                if "weight" in name: sapiens_technology_neural_networks.init.xavier_uniform_(param)
                elif "bias" in name: sapiens_technology_neural_networks.init.constant_(param, 0.0)
@dataclass
class SAPIMusicOutput(ModelOutput):
    """Args:"""
    audio_codes: sapiens_technology_torch.LongTensor = None
    audio_values: sapiens_technology_torch.FloatTensor = None
@dataclass
class SAPIMusicEncoderOutput(ModelOutput):
    """Args:"""
    audio_codes: sapiens_technology_torch.LongTensor = None
    audio_scales: sapiens_technology_torch.FloatTensor = None
@dataclass
class SAPIMusicDecoderOutput(ModelOutput):
    """Args:"""
    audio_values: sapiens_technology_torch.FloatTensor = None
@add_start_docstrings("The SAPI-Music neural audio codec model.", SAPI_MUSIC_START_DOCSTRING)
class SAPIMusicModel(SAPIMusicPreTrainedModel):
    def __init__(self, config: SAPIMusicConfig):
        super().__init__(config)
        self.config = config
        self.encoder = SAPIMusicEncoder(config)
        self.decoder = SAPIMusicDecoder(config)
        self.quantizer = SAPIMusicResidualVectorQuantizer(config)
        self.bits_per_codebook = int(sapiens_technology_math.log2(self.config.codebook_size))
        if 2**self.bits_per_codebook != self.config.codebook_size: raise ValueError("The codebook_size must be a power of 2.")
        self.post_init()
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def _encode_frame(self, input_values: sapiens_technology_torch.Tensor, bandwidth: float, padding_mask: int) -> Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor]]:
        length = input_values.shape[-1]
        duration = length / self.config.sampling_rate
        if self.config.chunk_length_s is not None and duration > 1e-5 + self.config.chunk_length_s: raise RuntimeError(f"Duration of frame ({duration}) is longer than chunk {self.config.chunk_length_s}")
        scale = None
        if self.config.normalize:
            input_values = input_values * padding_mask
            mono = sapiens_technology_torch.sum(input_values, 1, keepdim=True) / input_values.shape[1]
            scale = mono.pow(2).mean(dim=-1, keepdim=True).sqrt() + 1e-8
            input_values = input_values / scale
        embeddings = self.encoder(input_values)
        codes = self.quantizer.encode(embeddings, bandwidth)
        codes = codes.transpose(0, 1)
        return codes, scale
    def encode(self, input_values: sapiens_technology_torch.Tensor, padding_mask: sapiens_technology_torch.Tensor = None, bandwidth: Optional[float] = None, return_dict: Optional[bool] = None) -> Union[Tuple[sapiens_technology_torch.Tensor, Optional[sapiens_technology_torch.Tensor]], SAPIMusicEncoderOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if bandwidth is None: bandwidth = self.config.target_bandwidths[0]
        if bandwidth not in self.config.target_bandwidths: raise ValueError(f"This model doesn't support the bandwidth {bandwidth}. Select one of {self.config.target_bandwidths}.")
        _, channels, input_length = input_values.shape
        if channels < 1 or channels > 2: raise ValueError(f"Number of audio channels must be 1 or 2, but got {channels}")
        chunk_length = self.config.chunk_length
        if chunk_length is None:
            chunk_length = input_length
            stride = input_length
        else: stride = self.config.chunk_stride
        if padding_mask is None: padding_mask = sapiens_technology_torch.ones_like(input_values).bool()
        encoded_frames = []
        scales = []
        step = chunk_length - stride
        if (input_length % stride) - step != 0: raise ValueError("The input length is not properly padded for batched chunked decoding. Make sure to pad the input correctly.")
        for offset in range(0, input_length - step, stride):
            mask = padding_mask[..., offset : offset + chunk_length].bool()
            frame = input_values[:, :, offset : offset + chunk_length]
            encoded_frame, scale = self._encode_frame(frame, bandwidth, mask)
            encoded_frames.append(encoded_frame)
            scales.append(scale)
        encoded_frames = sapiens_technology_torch.stack(encoded_frames)
        if not return_dict: return (encoded_frames, scales)
        return SAPIMusicEncoderOutput(encoded_frames, scales)
    @staticmethod
    def _linear_overlap_add(frames: List[sapiens_technology_torch.Tensor], stride: int):
        if len(frames) == 0: raise ValueError("`frames` cannot be an empty list.")
        device = frames[0].device
        dtype = frames[0].dtype
        shape = frames[0].shape[:-1]
        total_size = stride * (len(frames) - 1) + frames[-1].shape[-1]
        frame_length = frames[0].shape[-1]
        time_vec = sapiens_technology_torch.linspace(0, 1, frame_length + 2, device=device, dtype=dtype)[1:-1]
        weight = 0.5 - (time_vec - 0.5).abs()
        sum_weight = sapiens_technology_torch.zeros(total_size, device=device, dtype=dtype)
        out = sapiens_technology_torch.zeros(*shape, total_size, device=device, dtype=dtype)
        offset: int = 0
        for frame in frames:
            frame_length = frame.shape[-1]
            out[..., offset : offset + frame_length] += weight[:frame_length] * frame
            sum_weight[offset : offset + frame_length] += weight[:frame_length]
            offset += stride
        if sum_weight.min() == 0: raise ValueError(f"`sum_weight` minimum element must be bigger than zero: {sum_weight}`")
        return out / sum_weight
    def _decode_frame(self, codes: sapiens_technology_torch.Tensor, scale: Optional[sapiens_technology_torch.Tensor] = None) -> sapiens_technology_torch.Tensor:
        codes = codes.transpose(0, 1)
        embeddings = self.quantizer.decode(codes)
        outputs = self.decoder(embeddings)
        if scale is not None: outputs = outputs * scale.view(-1, 1, 1)
        return outputs
    def decode(self, audio_codes: sapiens_technology_torch.Tensor, audio_scales: sapiens_technology_torch.Tensor, padding_mask: Optional[sapiens_technology_torch.Tensor] = None, return_dict: Optional[bool] = None) -> Union[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor], SAPIMusicDecoderOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        chunk_length = self.config.chunk_length
        if chunk_length is None:
            if len(audio_codes) != 1: raise ValueError(f"Expected one frame, got {len(audio_codes)}")
            audio_values = self._decode_frame(audio_codes[0], audio_scales[0])
        else:
            decoded_frames = []
            for frame, scale in zip(audio_codes, audio_scales):
                frames = self._decode_frame(frame, scale)
                decoded_frames.append(frames)
            audio_values = self._linear_overlap_add(decoded_frames, self.config.chunk_stride or 1)
        if padding_mask is not None and padding_mask.shape[-1] < audio_values.shape[-1]: audio_values = audio_values[..., : padding_mask.shape[-1]]
        if not return_dict: return (audio_values,)
        return SAPIMusicDecoderOutput(audio_values)
    @add_start_docstrings_to_model_forward(SAPI_MUSIC_INPUTS_DOCSTRING)
    def forward(self, input_values: sapiens_technology_torch.Tensor, padding_mask: Optional[sapiens_technology_torch.Tensor] = None, bandwidth: Optional[float] = None, audio_codes: Optional[sapiens_technology_torch.Tensor] = None,
    audio_scales: Optional[sapiens_technology_torch.Tensor] = None, return_dict: Optional[bool] = None) -> Union[Tuple[sapiens_technology_torch.Tensor, sapiens_technology_torch.Tensor], SAPIMusicOutput]:
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if padding_mask is None: padding_mask = sapiens_technology_torch.ones_like(input_values).bool()
        if audio_codes is not None and audio_scales is None: raise ValueError("You specified `audio_codes` but did not specify the `audio_scales`")
        if audio_scales is not None and audio_codes is None: raise ValueError("You specified `audio_scales` but did not specify the `audio_codes`")
        if audio_scales is None and audio_codes is None: audio_codes, audio_scales = self.encode(input_values, padding_mask, bandwidth, False)
        audio_values = self.decode(audio_codes, audio_scales, padding_mask, return_dict=return_dict)[0]
        if not return_dict: return (audio_codes, audio_values)
        return SAPIMusicOutput(audio_codes=audio_codes, audio_values=audio_values)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
