'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, Attention, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor, AttnProcessor2_0, FusedAttnProcessor2_0, IPAdapterAttnProcessor, IPAdapterAttnProcessor2_0
from ...loaders import FromOriginalModelMixin, PeftAdapterMixin, UNet2DConditionLoadersMixin
from ...configuration_utils import ConfigMixin, FrozenDict, register_to_config
from ...utils import BaseOutput, deprecate, is_torch_version
from ..sapiens_transformers.dual_transformer_2d import DualTransformer2DModel
from ..resnet import Downsample2D, ResnetBlock2D, Upsample2D
from ..sapiens_transformers.transformer_2d import Transformer2DModel
from ..embeddings import TimestepEmbedding, Timesteps
from typing import Any, Dict, Optional, Tuple, Union
from .unet_2d_blocks import UNetMidBlock2DCrossAttn
from .unet_2d_condition import UNet2DConditionModel
from ..attention import BasicTransformerBlock
from ...utils.torch_utils import apply_freeu
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
import torch.nn.functional as F
import torch.utils.checkpoint
import torch.nn as nn
import torch
@dataclass
class UNetMotionOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor
class AnimateDiffTransformer3D(nn.Module):
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, out_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0,
    norm_num_groups: int=32, cross_attention_dim: Optional[int]=None, attention_bias: bool=False, sample_size: Optional[int]=None, activation_fn: str='geglu', norm_elementwise_affine: bool=True,
    double_self_attention: bool=True, positional_embeddings: Optional[str]=None, num_positional_embeddings: Optional[int]=None):
        super().__init__()
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        inner_dim = num_attention_heads * attention_head_dim
        self.in_channels = in_channels
        self.norm = nn.GroupNorm(num_groups=norm_num_groups, num_channels=in_channels, eps=1e-06, affine=True)
        self.proj_in = nn.Linear(in_channels, inner_dim)
        self.transformer_blocks = nn.ModuleList([BasicTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, attention_bias=attention_bias, double_self_attention=double_self_attention, norm_elementwise_affine=norm_elementwise_affine, positional_embeddings=positional_embeddings,
        num_positional_embeddings=num_positional_embeddings) for _ in range(num_layers)])
        self.proj_out = nn.Linear(inner_dim, in_channels)
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: Optional[torch.LongTensor]=None, timestep: Optional[torch.LongTensor]=None, class_labels: Optional[torch.LongTensor]=None,
    num_frames: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None) -> torch.Tensor:
        """Returns:"""
        batch_frames, channel, height, width = hidden_states.shape
        batch_size = batch_frames // num_frames
        residual = hidden_states
        hidden_states = hidden_states[None, :].reshape(batch_size, num_frames, channel, height, width)
        hidden_states = hidden_states.permute(0, 2, 1, 3, 4)
        hidden_states = self.norm(hidden_states)
        hidden_states = hidden_states.permute(0, 3, 4, 2, 1).reshape(batch_size * height * width, num_frames, channel)
        hidden_states = self.proj_in(input=hidden_states)
        for block in self.transformer_blocks: hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states,
        timestep=timestep, cross_attention_kwargs=cross_attention_kwargs, class_labels=class_labels)
        hidden_states = self.proj_out(input=hidden_states)
        hidden_states = hidden_states[None, None, :].reshape(batch_size, height, width, num_frames, channel).permute(0, 3, 4, 1, 2).contiguous()
        hidden_states = hidden_states.reshape(batch_frames, channel, height, width)
        output = hidden_states + residual
        return output
class DownBlockMotion(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default',
    resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, output_scale_factor: float=1.0, add_downsample: bool=True, downsample_padding: int=1,
    temporal_num_attention_heads: Union[int, Tuple[int]]=1, temporal_cross_attention_dim: Optional[int]=None, temporal_max_seq_length: int=32,
    temporal_transformer_layers_per_block: Union[int, Tuple[int]]=1, temporal_double_self_attention: bool=True):
        super().__init__()
        resnets = []
        motion_modules = []
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = (temporal_transformer_layers_per_block,) * num_layers
        elif len(temporal_transformer_layers_per_block) != num_layers: raise ValueError(f'`temporal_transformer_layers_per_block` must be an integer or a tuple of integers of length {num_layers}')
        if isinstance(temporal_num_attention_heads, int): temporal_num_attention_heads = (temporal_num_attention_heads,) * num_layers
        elif len(temporal_num_attention_heads) != num_layers: raise ValueError(f'`temporal_num_attention_heads` must be an integer or a tuple of integers of length {num_layers}')
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            motion_modules.append(AnimateDiffTransformer3D(num_attention_heads=temporal_num_attention_heads[i], in_channels=out_channels, num_layers=temporal_transformer_layers_per_block[i],
            norm_num_groups=resnet_groups, cross_attention_dim=temporal_cross_attention_dim, attention_bias=False, activation_fn='geglu', positional_embeddings='sinusoidal',
            num_positional_embeddings=temporal_max_seq_length, attention_head_dim=out_channels // temporal_num_attention_heads[i], double_self_attention=temporal_double_self_attention))
        self.resnets = nn.ModuleList(resnets)
        self.motion_modules = nn.ModuleList(motion_modules)
        if add_downsample: self.downsamplers = nn.ModuleList([Downsample2D(out_channels, use_conv=True, out_channels=out_channels, padding=downsample_padding, name='op')])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, num_frames: int=1, *args, **kwargs) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        if len(args) > 0 or kwargs.get('scale', None) is not None:
            deprecation_message = 'The `scale` argument is deprecated and will be ignored. Please remove it, as passing it will raise an error in the future. `scale` should directly be passed while calling the underlying pipeline component i.e., via `cross_attention_kwargs`.'
            deprecate('scale', '1.0.0', deprecation_message)
        output_states = ()
        blocks = zip(self.resnets, self.motion_modules)
        for resnet, motion_module in blocks:
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                if is_torch_version('>=', '1.11.0'): hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, use_reentrant=False)
                else: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb)
            else: hidden_states = resnet(input_tensor=hidden_states, temb=temb)
            hidden_states = motion_module(hidden_states, num_frames=num_frames)
            output_states = output_states + (hidden_states,)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states=hidden_states)
            output_states = output_states + (hidden_states,)
        return (hidden_states, output_states)
class CrossAttnDownBlockMotion(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: Union[int, Tuple[int]]=1, resnet_eps: float=1e-06,
    resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads: int=1, cross_attention_dim: int=1280,
    output_scale_factor: float=1.0, downsample_padding: int=1, add_downsample: bool=True, dual_cross_attention: bool=False, use_linear_projection: bool=False,
    only_cross_attention: bool=False, upcast_attention: bool=False, attention_type: str='default', temporal_cross_attention_dim: Optional[int]=None, temporal_num_attention_heads: int=8,
    temporal_max_seq_length: int=32, temporal_transformer_layers_per_block: Union[int, Tuple[int]]=1, temporal_double_self_attention: bool=True):
        super().__init__()
        resnets = []
        attentions = []
        motion_modules = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = (transformer_layers_per_block,) * num_layers
        elif len(transformer_layers_per_block) != num_layers: raise ValueError(f'transformer_layers_per_block must be an integer or a list of integers of length {num_layers}')
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = (temporal_transformer_layers_per_block,) * num_layers
        elif len(temporal_transformer_layers_per_block) != num_layers: raise ValueError(f'temporal_transformer_layers_per_block must be an integer or a list of integers of length {num_layers}')
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, time_embedding_norm=resnet_time_scale_shift,
            non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=transformer_layers_per_block[i],
            cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=1, cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
            motion_modules.append(AnimateDiffTransformer3D(num_attention_heads=temporal_num_attention_heads, in_channels=out_channels, num_layers=temporal_transformer_layers_per_block[i], norm_num_groups=resnet_groups,
            cross_attention_dim=temporal_cross_attention_dim, attention_bias=False, activation_fn='geglu', positional_embeddings='sinusoidal', num_positional_embeddings=temporal_max_seq_length,
            attention_head_dim=out_channels // temporal_num_attention_heads, double_self_attention=temporal_double_self_attention))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.motion_modules = nn.ModuleList(motion_modules)
        if add_downsample: self.downsamplers = nn.ModuleList([Downsample2D(out_channels, use_conv=True, out_channels=out_channels, padding=downsample_padding, name='op')])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    num_frames: int=1, encoder_attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, additional_residuals: Optional[torch.Tensor]=None):
        output_states = ()
        blocks = list(zip(self.resnets, self.attentions, self.motion_modules))
        for i, (resnet, attn, motion_module) in enumerate(blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
            else: hidden_states = resnet(input_tensor=hidden_states, temb=temb)
            hidden_states = attn(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, attention_mask=attention_mask,
            encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            hidden_states = motion_module(hidden_states, num_frames=num_frames)
            if i == len(blocks) - 1 and additional_residuals is not None: hidden_states = hidden_states + additional_residuals
            output_states = output_states + (hidden_states,)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states=hidden_states)
            output_states = output_states + (hidden_states,)
        return (hidden_states, output_states)
class CrossAttnUpBlockMotion(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, prev_output_channel: int, temb_channels: int, resolution_idx: Optional[int]=None, dropout: float=0.0, num_layers: int=1,
    transformer_layers_per_block: Union[int, Tuple[int]]=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True,
    num_attention_heads: int=1, cross_attention_dim: int=1280, output_scale_factor: float=1.0, add_upsample: bool=True, dual_cross_attention: bool=False, use_linear_projection: bool=False,
    only_cross_attention: bool=False, upcast_attention: bool=False, attention_type: str='default', temporal_cross_attention_dim: Optional[int]=None, temporal_num_attention_heads: int=8,
    temporal_max_seq_length: int=32, temporal_transformer_layers_per_block: Union[int, Tuple[int]]=1):
        super().__init__()
        resnets = []
        attentions = []
        motion_modules = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = (transformer_layers_per_block,) * num_layers
        elif len(transformer_layers_per_block) != num_layers: raise ValueError(f'transformer_layers_per_block must be an integer or a list of integers of length {num_layers}, got {len(transformer_layers_per_block)}')
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = (temporal_transformer_layers_per_block,) * num_layers
        elif len(temporal_transformer_layers_per_block) != num_layers: raise ValueError(f'temporal_transformer_layers_per_block must be an integer or a list of integers of length {num_layers}, got {len(temporal_transformer_layers_per_block)}')
        for i in range(num_layers):
            res_skip_channels = in_channels if i == num_layers - 1 else out_channels
            resnet_in_channels = prev_output_channel if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=resnet_in_channels + res_skip_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups,
            dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=transformer_layers_per_block[i],
            cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=1, cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
            motion_modules.append(AnimateDiffTransformer3D(num_attention_heads=temporal_num_attention_heads, in_channels=out_channels, num_layers=temporal_transformer_layers_per_block[i],
            norm_num_groups=resnet_groups, cross_attention_dim=temporal_cross_attention_dim, attention_bias=False, activation_fn='geglu', positional_embeddings='sinusoidal',
            num_positional_embeddings=temporal_max_seq_length, attention_head_dim=out_channels // temporal_num_attention_heads))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.motion_modules = nn.ModuleList(motion_modules)
        if add_upsample: self.upsamplers = nn.ModuleList([Upsample2D(out_channels, use_conv=True, out_channels=out_channels)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
        self.resolution_idx = resolution_idx
    def forward(self, hidden_states: torch.Tensor, res_hidden_states_tuple: Tuple[torch.Tensor, ...], temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, upsample_size: Optional[int]=None, attention_mask: Optional[torch.Tensor]=None, encoder_attention_mask: Optional[torch.Tensor]=None, num_frames: int=1) -> torch.Tensor:
        is_freeu_enabled = getattr(self, 's1', None) and getattr(self, 's2', None) and getattr(self, 'b1', None) and getattr(self, 'b2', None)
        blocks = zip(self.resnets, self.attentions, self.motion_modules)
        for resnet, attn, motion_module in blocks:
            res_hidden_states = res_hidden_states_tuple[-1]
            res_hidden_states_tuple = res_hidden_states_tuple[:-1]
            if is_freeu_enabled: hidden_states, res_hidden_states = apply_freeu(self.resolution_idx, hidden_states, res_hidden_states, s1=self.s1, s2=self.s2, b1=self.b1, b2=self.b2)
            hidden_states = torch.cat([hidden_states, res_hidden_states], dim=1)
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
            else: hidden_states = resnet(input_tensor=hidden_states, temb=temb)
            hidden_states = attn(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs,
            attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            hidden_states = motion_module(hidden_states, num_frames=num_frames)
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states=hidden_states, output_size=upsample_size)
        return hidden_states
class UpBlockMotion(nn.Module):
    def __init__(self, in_channels: int, prev_output_channel: int, out_channels: int, temb_channels: int, resolution_idx: Optional[int]=None, dropout: float=0.0, num_layers: int=1,
    resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, output_scale_factor: float=1.0,
    add_upsample: bool=True, temporal_cross_attention_dim: Optional[int]=None, temporal_num_attention_heads: int=8, temporal_max_seq_length: int=32, temporal_transformer_layers_per_block: Union[int, Tuple[int]]=1):
        super().__init__()
        resnets = []
        motion_modules = []
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = (temporal_transformer_layers_per_block,) * num_layers
        elif len(temporal_transformer_layers_per_block) != num_layers: raise ValueError(f'temporal_transformer_layers_per_block must be an integer or a list of integers of length {num_layers}')
        for i in range(num_layers):
            res_skip_channels = in_channels if i == num_layers - 1 else out_channels
            resnet_in_channels = prev_output_channel if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=resnet_in_channels + res_skip_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups,
            dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            motion_modules.append(AnimateDiffTransformer3D(num_attention_heads=temporal_num_attention_heads, in_channels=out_channels, num_layers=temporal_transformer_layers_per_block[i],
            norm_num_groups=resnet_groups, cross_attention_dim=temporal_cross_attention_dim, attention_bias=False, activation_fn='geglu', positional_embeddings='sinusoidal',
            num_positional_embeddings=temporal_max_seq_length, attention_head_dim=out_channels // temporal_num_attention_heads))
        self.resnets = nn.ModuleList(resnets)
        self.motion_modules = nn.ModuleList(motion_modules)
        if add_upsample: self.upsamplers = nn.ModuleList([Upsample2D(out_channels, use_conv=True, out_channels=out_channels)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
        self.resolution_idx = resolution_idx
    def forward(self, hidden_states: torch.Tensor, res_hidden_states_tuple: Tuple[torch.Tensor, ...], temb: Optional[torch.Tensor]=None, upsample_size=None, num_frames: int=1, *args, **kwargs) -> torch.Tensor:
        if len(args) > 0 or kwargs.get('scale', None) is not None:
            deprecation_message = 'The `scale` argument is deprecated and will be ignored. Please remove it, as passing it will raise an error in the future. `scale` should directly be passed while calling the underlying pipeline component i.e., via `cross_attention_kwargs`.'
            deprecate('scale', '1.0.0', deprecation_message)
        is_freeu_enabled = getattr(self, 's1', None) and getattr(self, 's2', None) and getattr(self, 'b1', None) and getattr(self, 'b2', None)
        blocks = zip(self.resnets, self.motion_modules)
        for resnet, motion_module in blocks:
            res_hidden_states = res_hidden_states_tuple[-1]
            res_hidden_states_tuple = res_hidden_states_tuple[:-1]
            if is_freeu_enabled: hidden_states, res_hidden_states = apply_freeu(self.resolution_idx, hidden_states, res_hidden_states, s1=self.s1, s2=self.s2, b1=self.b1, b2=self.b2)
            hidden_states = torch.cat([hidden_states, res_hidden_states], dim=1)
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                if is_torch_version('>=', '1.11.0'): hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, use_reentrant=False)
                else: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb)
            else: hidden_states = resnet(input_tensor=hidden_states, temb=temb)
            hidden_states = motion_module(hidden_states, num_frames=num_frames)
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states=hidden_states, output_size=upsample_size)
        return hidden_states
class UNetMidBlockCrossAttnMotion(nn.Module):
    def __init__(self, in_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: Union[int, Tuple[int]]=1, resnet_eps: float=1e-06,
    resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads: int=1, output_scale_factor: float=1.0,
    cross_attention_dim: int=1280, dual_cross_attention: bool=False, use_linear_projection: bool=False, upcast_attention: bool=False, attention_type: str='default',
    temporal_num_attention_heads: int=1, temporal_cross_attention_dim: Optional[int]=None, temporal_max_seq_length: int=32, temporal_transformer_layers_per_block: Union[int, Tuple[int]]=1):
        super().__init__()
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = (transformer_layers_per_block,) * num_layers
        elif len(transformer_layers_per_block) != num_layers: raise ValueError(f'`transformer_layers_per_block` should be an integer or a list of integers of length {num_layers}.')
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = (temporal_transformer_layers_per_block,) * num_layers
        elif len(temporal_transformer_layers_per_block) != num_layers: raise ValueError(f'`temporal_transformer_layers_per_block` should be an integer or a list of integers of length {num_layers}.')
        resnets = [ResnetBlock2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, time_embedding_norm=resnet_time_scale_shift,
        non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm)]
        attentions = []
        motion_modules = []
        for i in range(num_layers):
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, in_channels // num_attention_heads, in_channels=in_channels, num_layers=transformer_layers_per_block[i],
            cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection, upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, in_channels // num_attention_heads, in_channels=in_channels, num_layers=1, cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
            resnets.append(ResnetBlock2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            motion_modules.append(AnimateDiffTransformer3D(num_attention_heads=temporal_num_attention_heads, attention_head_dim=in_channels // temporal_num_attention_heads, in_channels=in_channels,
            num_layers=temporal_transformer_layers_per_block[i], norm_num_groups=resnet_groups, cross_attention_dim=temporal_cross_attention_dim, attention_bias=False,
            positional_embeddings='sinusoidal', num_positional_embeddings=temporal_max_seq_length, activation_fn='geglu'))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.motion_modules = nn.ModuleList(motion_modules)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None, num_frames: int=1) -> torch.Tensor:
        hidden_states = self.resnets[0](input_tensor=hidden_states, temb=temb)
        blocks = zip(self.attentions, self.resnets[1:], self.motion_modules)
        for attn, resnet, motion_module in blocks:
            hidden_states = attn(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs,
            attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(motion_module), hidden_states, temb, **ckpt_kwargs)
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
            else:
                hidden_states = motion_module(hidden_states, num_frames=num_frames)
                hidden_states = resnet(input_tensor=hidden_states, temb=temb)
        return hidden_states
class MotionModules(nn.Module):
    def __init__(self, in_channels: int, layers_per_block: int=2, transformer_layers_per_block: Union[int, Tuple[int]]=8, num_attention_heads: Union[int, Tuple[int]]=8,
    attention_bias: bool=False, cross_attention_dim: Optional[int]=None, activation_fn: str='geglu', norm_num_groups: int=32, max_seq_length: int=32):
        super().__init__()
        self.motion_modules = nn.ModuleList([])
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = (transformer_layers_per_block,) * layers_per_block
        elif len(transformer_layers_per_block) != layers_per_block: raise ValueError(f'The number of transformer layers per block must match the number of layers per block, got {layers_per_block} and {len(transformer_layers_per_block)}')
        for i in range(layers_per_block): self.motion_modules.append(AnimateDiffTransformer3D(in_channels=in_channels, num_layers=transformer_layers_per_block[i], norm_num_groups=norm_num_groups,
        cross_attention_dim=cross_attention_dim, activation_fn=activation_fn, attention_bias=attention_bias, num_attention_heads=num_attention_heads,
        attention_head_dim=in_channels // num_attention_heads, positional_embeddings='sinusoidal', num_positional_embeddings=max_seq_length))
class MotionAdapter(ModelMixin, ConfigMixin, FromOriginalModelMixin):
    @register_to_config
    def __init__(self, block_out_channels: Tuple[int, ...]=(320, 640, 1280, 1280), motion_layers_per_block: Union[int, Tuple[int]]=2,
    motion_transformer_layers_per_block: Union[int, Tuple[int], Tuple[Tuple[int]]]=1, motion_mid_block_layers_per_block: int=1,
    motion_transformer_layers_per_mid_block: Union[int, Tuple[int]]=1, motion_num_attention_heads: Union[int, Tuple[int]]=8, motion_norm_num_groups: int=32,
    motion_max_seq_length: int=32, use_motion_mid_block: bool=True, conv_in_channels: Optional[int]=None):
        """Args:"""
        super().__init__()
        down_blocks = []
        up_blocks = []
        if isinstance(motion_layers_per_block, int): motion_layers_per_block = (motion_layers_per_block,) * len(block_out_channels)
        elif len(motion_layers_per_block) != len(block_out_channels): raise ValueError(f'The number of motion layers per block must match the number of blocks, got {len(block_out_channels)} and {len(motion_layers_per_block)}')
        if isinstance(motion_transformer_layers_per_block, int): motion_transformer_layers_per_block = (motion_transformer_layers_per_block,) * len(block_out_channels)
        if isinstance(motion_transformer_layers_per_mid_block, int): motion_transformer_layers_per_mid_block = (motion_transformer_layers_per_mid_block,) * motion_mid_block_layers_per_block
        elif len(motion_transformer_layers_per_mid_block) != motion_mid_block_layers_per_block: raise ValueError(f'The number of layers per mid block ({motion_mid_block_layers_per_block}) must match the length of motion_transformer_layers_per_mid_block ({len(motion_transformer_layers_per_mid_block)})')
        if isinstance(motion_num_attention_heads, int): motion_num_attention_heads = (motion_num_attention_heads,) * len(block_out_channels)
        elif len(motion_num_attention_heads) != len(block_out_channels): raise ValueError(f'The length of the attention head number tuple in the motion module must match the number of block, got {len(motion_num_attention_heads)} and {len(block_out_channels)}')
        if conv_in_channels: self.conv_in = nn.Conv2d(conv_in_channels, block_out_channels[0], kernel_size=3, padding=1)
        else: self.conv_in = None
        for i, channel in enumerate(block_out_channels):
            output_channel = block_out_channels[i]
            down_blocks.append(MotionModules(in_channels=output_channel, norm_num_groups=motion_norm_num_groups, cross_attention_dim=None, activation_fn='geglu', attention_bias=False,
            num_attention_heads=motion_num_attention_heads[i], max_seq_length=motion_max_seq_length, layers_per_block=motion_layers_per_block[i], transformer_layers_per_block=motion_transformer_layers_per_block[i]))
        if use_motion_mid_block: self.mid_block = MotionModules(in_channels=block_out_channels[-1], norm_num_groups=motion_norm_num_groups, cross_attention_dim=None, activation_fn='geglu', attention_bias=False,
        num_attention_heads=motion_num_attention_heads[-1], max_seq_length=motion_max_seq_length, layers_per_block=motion_mid_block_layers_per_block, transformer_layers_per_block=motion_transformer_layers_per_mid_block)
        else: self.mid_block = None
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        reversed_motion_layers_per_block = list(reversed(motion_layers_per_block))
        reversed_motion_transformer_layers_per_block = list(reversed(motion_transformer_layers_per_block))
        reversed_motion_num_attention_heads = list(reversed(motion_num_attention_heads))
        for i, channel in enumerate(reversed_block_out_channels):
            output_channel = reversed_block_out_channels[i]
            up_blocks.append(MotionModules(in_channels=output_channel, norm_num_groups=motion_norm_num_groups, cross_attention_dim=None, activation_fn='geglu', attention_bias=False, num_attention_heads=reversed_motion_num_attention_heads[i],
            max_seq_length=motion_max_seq_length, layers_per_block=reversed_motion_layers_per_block[i] + 1, transformer_layers_per_block=reversed_motion_transformer_layers_per_block[i]))
        self.down_blocks = nn.ModuleList(down_blocks)
        self.up_blocks = nn.ModuleList(up_blocks)
    def forward(self, sample): pass
class SAPIVideoGenTransformer3D(nn.Module):
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, out_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0,
    norm_num_groups: int=32, cross_attention_dim: Optional[int]=None, attention_bias: bool=False, sample_size: Optional[int]=None, activation_fn: str='geglu', norm_elementwise_affine: bool=True,
    double_self_attention: bool=True, positional_embeddings: Optional[str]=None, num_positional_embeddings: Optional[int]=None):
        super().__init__()
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        inner_dim = num_attention_heads * attention_head_dim
        self.in_channels = in_channels
        self.norm = nn.GroupNorm(num_groups=norm_num_groups, num_channels=in_channels, eps=1e-06, affine=True)
        self.proj_in = nn.Linear(in_channels, inner_dim)
        self.transformer_blocks = nn.ModuleList([BasicTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, attention_bias=attention_bias, double_self_attention=double_self_attention, norm_elementwise_affine=norm_elementwise_affine, positional_embeddings=positional_embeddings,
        num_positional_embeddings=num_positional_embeddings) for _ in range(num_layers)])
        self.proj_out = nn.Linear(inner_dim, in_channels)
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: Optional[torch.LongTensor]=None, timestep: Optional[torch.LongTensor]=None, class_labels: Optional[torch.LongTensor]=None,
    num_frames: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None) -> torch.Tensor:
        """Returns:"""
        batch_frames, channel, height, width = hidden_states.shape
        batch_size = batch_frames // num_frames
        residual = hidden_states
        hidden_states = hidden_states[None, :].reshape(batch_size, num_frames, channel, height, width)
        hidden_states = hidden_states.permute(0, 2, 1, 3, 4)
        hidden_states = self.norm(hidden_states)
        hidden_states = hidden_states.permute(0, 3, 4, 2, 1).reshape(batch_size * height * width, num_frames, channel)
        hidden_states = self.proj_in(input=hidden_states)
        for block in self.transformer_blocks: hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states,
        timestep=timestep, cross_attention_kwargs=cross_attention_kwargs, class_labels=class_labels)
        hidden_states = self.proj_out(input=hidden_states)
        hidden_states = hidden_states[None, None, :].reshape(batch_size, height, width, num_frames, channel).permute(0, 3, 4, 1, 2).contiguous()
        hidden_states = hidden_states.reshape(batch_frames, channel, height, width)
        output = hidden_states + residual
        return output
class UNetMotionModel(ModelMixin, ConfigMixin, UNet2DConditionLoadersMixin, PeftAdapterMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: Optional[int]=None, in_channels: int=4, out_channels: int=4, down_block_types: Tuple[str, ...]=('CrossAttnDownBlockMotion', 'CrossAttnDownBlockMotion', 'CrossAttnDownBlockMotion', 'DownBlockMotion'),
    up_block_types: Tuple[str, ...]=('UpBlockMotion', 'CrossAttnUpBlockMotion', 'CrossAttnUpBlockMotion', 'CrossAttnUpBlockMotion'), block_out_channels: Tuple[int, ...]=(320, 640, 1280, 1280), layers_per_block: Union[int, Tuple[int]]=2,
    downsample_padding: int=1, mid_block_scale_factor: float=1, act_fn: str='silu', norm_num_groups: int=32, norm_eps: float=1e-05, cross_attention_dim: int=1280, transformer_layers_per_block: Union[int, Tuple[int], Tuple[Tuple]]=1,
    reverse_transformer_layers_per_block: Optional[Union[int, Tuple[int], Tuple[Tuple]]]=None, temporal_transformer_layers_per_block: Union[int, Tuple[int], Tuple[Tuple]]=1,
    reverse_temporal_transformer_layers_per_block: Optional[Union[int, Tuple[int], Tuple[Tuple]]]=None, transformer_layers_per_mid_block: Optional[Union[int, Tuple[int]]]=None,
    temporal_transformer_layers_per_mid_block: Optional[Union[int, Tuple[int]]]=1, use_linear_projection: bool=False, num_attention_heads: Union[int, Tuple[int, ...]]=8, motion_max_seq_length: int=32,
    motion_num_attention_heads: Union[int, Tuple[int, ...]]=8, reverse_motion_num_attention_heads: Optional[Union[int, Tuple[int, ...], Tuple[Tuple[int, ...], ...]]]=None, use_motion_mid_block: bool=True,
    mid_block_layers: int=1, encoder_hid_dim: Optional[int]=None, encoder_hid_dim_type: Optional[str]=None, addition_embed_type: Optional[str]=None, addition_time_embed_dim: Optional[int]=None,
    projection_class_embeddings_input_dim: Optional[int]=None, time_cond_proj_dim: Optional[int]=None):
        super().__init__()
        self.sample_size = sample_size
        if len(down_block_types) != len(up_block_types): raise ValueError(f'Must provide the same number of `down_block_types` as `up_block_types`. `down_block_types`: {down_block_types}. `up_block_types`: {up_block_types}.')
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        if isinstance(cross_attention_dim, list) and len(cross_attention_dim) != len(down_block_types): raise ValueError(f'Must provide the same number of `cross_attention_dim` as `down_block_types`. `cross_attention_dim`: {cross_attention_dim}. `down_block_types`: {down_block_types}.')
        if not isinstance(layers_per_block, int) and len(layers_per_block) != len(down_block_types): raise ValueError(f'Must provide the same number of `layers_per_block` as `down_block_types`. `layers_per_block`: {layers_per_block}. `down_block_types`: {down_block_types}.')
        if isinstance(transformer_layers_per_block, list) and reverse_transformer_layers_per_block is None:
            for layer_number_per_block in transformer_layers_per_block:
                if isinstance(layer_number_per_block, list): raise ValueError("Must provide 'reverse_transformer_layers_per_block` if using asymmetrical UNet.")
        if isinstance(temporal_transformer_layers_per_block, list) and reverse_temporal_transformer_layers_per_block is None:
            for layer_number_per_block in temporal_transformer_layers_per_block:
                if isinstance(layer_number_per_block, list): raise ValueError("Must provide 'reverse_temporal_transformer_layers_per_block` if using asymmetrical motion module in UNet.")
        conv_in_kernel = 3
        conv_out_kernel = 3
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        time_embed_dim = block_out_channels[0] * 4
        self.time_proj = Timesteps(block_out_channels[0], True, 0)
        timestep_input_dim = block_out_channels[0]
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn, cond_proj_dim=time_cond_proj_dim)
        if encoder_hid_dim_type is None: self.encoder_hid_proj = None
        if addition_embed_type == 'text_time':
            self.add_time_proj = Timesteps(addition_time_embed_dim, True, 0)
            self.add_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        self.down_blocks = nn.ModuleList([])
        self.up_blocks = nn.ModuleList([])
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,) * len(down_block_types)
        if isinstance(layers_per_block, int): layers_per_block = [layers_per_block] * len(down_block_types)
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(down_block_types)
        if isinstance(reverse_transformer_layers_per_block, int): reverse_transformer_layers_per_block = [reverse_transformer_layers_per_block] * len(down_block_types)
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = [temporal_transformer_layers_per_block] * len(down_block_types)
        if isinstance(reverse_temporal_transformer_layers_per_block, int): reverse_temporal_transformer_layers_per_block = [reverse_temporal_transformer_layers_per_block] * len(down_block_types)
        if isinstance(motion_num_attention_heads, int): motion_num_attention_heads = (motion_num_attention_heads,) * len(down_block_types)
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            if down_block_type == 'CrossAttnDownBlockMotion': down_block = CrossAttnDownBlockMotion(in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, num_layers=layers_per_block[i],
            transformer_layers_per_block=transformer_layers_per_block[i], resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, num_attention_heads=num_attention_heads[i],
            cross_attention_dim=cross_attention_dim[i], downsample_padding=downsample_padding, add_downsample=not is_final_block, use_linear_projection=use_linear_projection, temporal_num_attention_heads=motion_num_attention_heads[i],
            temporal_max_seq_length=motion_max_seq_length, temporal_transformer_layers_per_block=temporal_transformer_layers_per_block[i])
            elif down_block_type == 'DownBlockMotion': down_block = DownBlockMotion(in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, num_layers=layers_per_block[i],
            resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, add_downsample=not is_final_block, downsample_padding=downsample_padding, temporal_num_attention_heads=motion_num_attention_heads[i],
            temporal_max_seq_length=motion_max_seq_length, temporal_transformer_layers_per_block=temporal_transformer_layers_per_block[i])
            else: raise ValueError('Invalid `down_block_type` encountered. Must be one of `CrossAttnDownBlockMotion` or `DownBlockMotion`')
            self.down_blocks.append(down_block)
        if transformer_layers_per_mid_block is None: transformer_layers_per_mid_block = transformer_layers_per_block[-1] if isinstance(transformer_layers_per_block[-1], int) else 1
        if use_motion_mid_block: self.mid_block = UNetMidBlockCrossAttnMotion(in_channels=block_out_channels[-1], temb_channels=time_embed_dim, resnet_eps=norm_eps, resnet_act_fn=act_fn,
        output_scale_factor=mid_block_scale_factor, cross_attention_dim=cross_attention_dim[-1], num_attention_heads=num_attention_heads[-1], resnet_groups=norm_num_groups, dual_cross_attention=False,
        use_linear_projection=use_linear_projection, num_layers=mid_block_layers, temporal_num_attention_heads=motion_num_attention_heads[-1], temporal_max_seq_length=motion_max_seq_length,
        transformer_layers_per_block=transformer_layers_per_mid_block, temporal_transformer_layers_per_block=temporal_transformer_layers_per_mid_block)
        else: self.mid_block = UNetMidBlock2DCrossAttn(in_channels=block_out_channels[-1], temb_channels=time_embed_dim, resnet_eps=norm_eps, resnet_act_fn=act_fn,
        output_scale_factor=mid_block_scale_factor, cross_attention_dim=cross_attention_dim[-1], num_attention_heads=num_attention_heads[-1], resnet_groups=norm_num_groups,
        dual_cross_attention=False, use_linear_projection=use_linear_projection, num_layers=mid_block_layers, transformer_layers_per_block=transformer_layers_per_mid_block)
        self.num_upsamplers = 0
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
        reversed_layers_per_block = list(reversed(layers_per_block))
        reversed_cross_attention_dim = list(reversed(cross_attention_dim))
        reversed_motion_num_attention_heads = list(reversed(motion_num_attention_heads))
        if reverse_transformer_layers_per_block is None: reverse_transformer_layers_per_block = list(reversed(transformer_layers_per_block))
        if reverse_temporal_transformer_layers_per_block is None: reverse_temporal_transformer_layers_per_block = list(reversed(temporal_transformer_layers_per_block))
        output_channel = reversed_block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            is_final_block = i == len(block_out_channels) - 1
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i]
            input_channel = reversed_block_out_channels[min(i + 1, len(block_out_channels) - 1)]
            if not is_final_block:
                add_upsample = True
                self.num_upsamplers += 1
            else: add_upsample = False
            if up_block_type == 'CrossAttnUpBlockMotion': up_block = CrossAttnUpBlockMotion(in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel,
            temb_channels=time_embed_dim, resolution_idx=i, num_layers=reversed_layers_per_block[i] + 1, transformer_layers_per_block=reverse_transformer_layers_per_block[i], resnet_eps=norm_eps,
            resnet_act_fn=act_fn, resnet_groups=norm_num_groups, num_attention_heads=reversed_num_attention_heads[i], cross_attention_dim=reversed_cross_attention_dim[i], add_upsample=add_upsample,
            use_linear_projection=use_linear_projection, temporal_num_attention_heads=reversed_motion_num_attention_heads[i], temporal_max_seq_length=motion_max_seq_length,
            temporal_transformer_layers_per_block=reverse_temporal_transformer_layers_per_block[i])
            elif up_block_type == 'UpBlockMotion': up_block = UpBlockMotion(in_channels=input_channel, prev_output_channel=prev_output_channel, out_channels=output_channel,
            temb_channels=time_embed_dim, resolution_idx=i, num_layers=reversed_layers_per_block[i] + 1, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups,
            add_upsample=add_upsample, temporal_num_attention_heads=reversed_motion_num_attention_heads[i], temporal_max_seq_length=motion_max_seq_length,
            temporal_transformer_layers_per_block=reverse_temporal_transformer_layers_per_block[i])
            else: raise ValueError('Invalid `up_block_type` encountered. Must be one of `CrossAttnUpBlockMotion` or `UpBlockMotion`')
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        if norm_num_groups is not None:
            self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=norm_eps)
            self.conv_act = nn.SiLU()
        else:
            self.conv_norm_out = None
            self.conv_act = None
        conv_out_padding = (conv_out_kernel - 1) // 2
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, kernel_size=conv_out_kernel, padding=conv_out_padding)
    @classmethod
    def from_unet2d(cls, unet: UNet2DConditionModel, motion_adapter: Optional[MotionAdapter]=None, load_weights: bool=True):
        has_motion_adapter = motion_adapter is not None
        if has_motion_adapter:
            motion_adapter.to(device=unet.device)
            if len(unet.config['down_block_types']) != len(motion_adapter.config['block_out_channels']): raise ValueError('Incompatible Motion Adapter, got different number of blocks')
            if isinstance(unet.config['layers_per_block'], int): expanded_layers_per_block = [unet.config['layers_per_block']] * len(unet.config['down_block_types'])
            else: expanded_layers_per_block = list(unet.config['layers_per_block'])
            if isinstance(motion_adapter.config['motion_layers_per_block'], int): expanded_adapter_layers_per_block = [motion_adapter.config['motion_layers_per_block']] * len(motion_adapter.config['block_out_channels'])
            else: expanded_adapter_layers_per_block = list(motion_adapter.config['motion_layers_per_block'])
            if expanded_layers_per_block != expanded_adapter_layers_per_block: raise ValueError('Incompatible Motion Adapter, got different number of layers per block')
        config = dict(unet.config)
        config['_class_name'] = cls.__name__
        down_blocks = []
        for down_blocks_type in config['down_block_types']:
            if 'CrossAttn' in down_blocks_type: down_blocks.append('CrossAttnDownBlockMotion')
            else: down_blocks.append('DownBlockMotion')
        config['down_block_types'] = down_blocks
        up_blocks = []
        for down_blocks_type in config['up_block_types']:
            if 'CrossAttn' in down_blocks_type: up_blocks.append('CrossAttnUpBlockMotion')
            else: up_blocks.append('UpBlockMotion')
        config['up_block_types'] = up_blocks
        if has_motion_adapter:
            config['motion_num_attention_heads'] = motion_adapter.config['motion_num_attention_heads']
            config['motion_max_seq_length'] = motion_adapter.config['motion_max_seq_length']
            config['use_motion_mid_block'] = motion_adapter.config['use_motion_mid_block']
            config['layers_per_block'] = motion_adapter.config['motion_layers_per_block']
            config['temporal_transformer_layers_per_mid_block'] = motion_adapter.config['motion_transformer_layers_per_mid_block']
            config['temporal_transformer_layers_per_block'] = motion_adapter.config['motion_transformer_layers_per_block']
            config['motion_num_attention_heads'] = motion_adapter.config['motion_num_attention_heads']
            if motion_adapter.config['conv_in_channels']: config['in_channels'] = motion_adapter.config['conv_in_channels']
        if not config.get('num_attention_heads'): config['num_attention_heads'] = config['attention_head_dim']
        expected_kwargs, optional_kwargs = cls._get_signature_keys(cls)
        config = FrozenDict({k: config.get(k) for k in config if k in expected_kwargs or k in optional_kwargs})
        config['_class_name'] = cls.__name__
        model = cls.from_config(config)
        if not load_weights: return model
        if has_motion_adapter and motion_adapter.config['conv_in_channels']:
            model.conv_in = motion_adapter.conv_in
            updated_conv_in_weight = torch.cat([unet.conv_in.weight, motion_adapter.conv_in.weight[:, 4:, :, :]], dim=1)
            model.conv_in.load_state_dict({'weight': updated_conv_in_weight, 'bias': unet.conv_in.bias})
        else: model.conv_in.load_state_dict(unet.conv_in.state_dict())
        model.time_proj.load_state_dict(unet.time_proj.state_dict())
        model.time_embedding.load_state_dict(unet.time_embedding.state_dict())
        if any((isinstance(proc, (IPAdapterAttnProcessor, IPAdapterAttnProcessor2_0)) for proc in unet.attn_processors.values())):
            attn_procs = {}
            for name, processor in unet.attn_processors.items():
                if name.endswith('attn1.processor'):
                    attn_processor_class = AttnProcessor2_0 if hasattr(F, 'scaled_dot_product_attention') else AttnProcessor
                    attn_procs[name] = attn_processor_class()
                else:
                    attn_processor_class = IPAdapterAttnProcessor2_0 if hasattr(F, 'scaled_dot_product_attention') else IPAdapterAttnProcessor
                    attn_procs[name] = attn_processor_class(hidden_size=processor.hidden_size, cross_attention_dim=processor.cross_attention_dim, scale=processor.scale, num_tokens=processor.num_tokens)
            for name, processor in model.attn_processors.items():
                if name not in attn_procs: attn_procs[name] = processor.__class__()
            model.set_attn_processor(attn_procs)
            model.config.encoder_hid_dim_type = 'ip_image_proj'
            model.encoder_hid_proj = unet.encoder_hid_proj
        for i, down_block in enumerate(unet.down_blocks):
            model.down_blocks[i].resnets.load_state_dict(down_block.resnets.state_dict())
            if hasattr(model.down_blocks[i], 'attentions'): model.down_blocks[i].attentions.load_state_dict(down_block.attentions.state_dict())
            if model.down_blocks[i].downsamplers: model.down_blocks[i].downsamplers.load_state_dict(down_block.downsamplers.state_dict())
        for i, up_block in enumerate(unet.up_blocks):
            model.up_blocks[i].resnets.load_state_dict(up_block.resnets.state_dict())
            if hasattr(model.up_blocks[i], 'attentions'): model.up_blocks[i].attentions.load_state_dict(up_block.attentions.state_dict())
            if model.up_blocks[i].upsamplers: model.up_blocks[i].upsamplers.load_state_dict(up_block.upsamplers.state_dict())
        model.mid_block.resnets.load_state_dict(unet.mid_block.resnets.state_dict())
        model.mid_block.attentions.load_state_dict(unet.mid_block.attentions.state_dict())
        if unet.conv_norm_out is not None: model.conv_norm_out.load_state_dict(unet.conv_norm_out.state_dict())
        if unet.conv_act is not None: model.conv_act.load_state_dict(unet.conv_act.state_dict())
        model.conv_out.load_state_dict(unet.conv_out.state_dict())
        if has_motion_adapter: model.load_motion_modules(motion_adapter)
        model.to(unet.dtype)
        return model
    def freeze_unet2d_params(self) -> None:
        for param in self.parameters(): param.requires_grad = False
        for down_block in self.down_blocks:
            motion_modules = down_block.motion_modules
            for param in motion_modules.parameters(): param.requires_grad = True
        for up_block in self.up_blocks:
            motion_modules = up_block.motion_modules
            for param in motion_modules.parameters(): param.requires_grad = True
        if hasattr(self.mid_block, 'motion_modules'):
            motion_modules = self.mid_block.motion_modules
            for param in motion_modules.parameters(): param.requires_grad = True
    def load_motion_modules(self, motion_adapter: Optional[MotionAdapter]) -> None:
        for i, down_block in enumerate(motion_adapter.down_blocks): self.down_blocks[i].motion_modules.load_state_dict(down_block.motion_modules.state_dict())
        for i, up_block in enumerate(motion_adapter.up_blocks): self.up_blocks[i].motion_modules.load_state_dict(up_block.motion_modules.state_dict())
        if hasattr(self.mid_block, 'motion_modules'): self.mid_block.motion_modules.load_state_dict(motion_adapter.mid_block.motion_modules.state_dict())
    def save_motion_modules(self, save_directory: str, is_main_process: bool=True, safe_serialization: bool=True, variant: Optional[str]=None, push_to_hub: bool=False, **kwargs) -> None:
        state_dict = self.state_dict()
        motion_state_dict = {}
        for k, v in state_dict.items():
            if 'motion_modules' in k: motion_state_dict[k] = v
        adapter = MotionAdapter(block_out_channels=self.config['block_out_channels'], motion_layers_per_block=self.config['layers_per_block'], motion_norm_num_groups=self.config['norm_num_groups'],
        motion_num_attention_heads=self.config['motion_num_attention_heads'], motion_max_seq_length=self.config['motion_max_seq_length'], use_motion_mid_block=self.config['use_motion_mid_block'])
        adapter.load_state_dict(motion_state_dict)
        adapter.save_pretrained(save_directory=save_directory, is_main_process=is_main_process, safe_serialization=safe_serialization, variant=variant, push_to_hub=push_to_hub, **kwargs)
    @property
    def attn_processors(self) -> Dict[str, AttentionProcessor]:
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor()
            for sub_name, child in module.named_children(): fn_recursive_add_processors(f'{name}.{sub_name}', child, processors)
            return processors
        for name, module in self.named_children(): fn_recursive_add_processors(name, module, processors)
        return processors
    def set_attn_processor(self, processor: Union[AttentionProcessor, Dict[str, AttentionProcessor]]):
        count = len(self.attn_processors.keys())
        if isinstance(processor, dict) and len(processor) != count: raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def enable_forward_chunking(self, chunk_size: Optional[int]=None, dim: int=0) -> None:
        if dim not in [0, 1]: raise ValueError(f'Make sure to set `dim` to either 0 or 1, not {dim}')
        chunk_size = chunk_size or 1
        def fn_recursive_feed_forward(module: torch.nn.Module, chunk_size: int, dim: int):
            if hasattr(module, 'set_chunk_feed_forward'): module.set_chunk_feed_forward(chunk_size=chunk_size, dim=dim)
            for child in module.children(): fn_recursive_feed_forward(child, chunk_size, dim)
        for module in self.children(): fn_recursive_feed_forward(module, chunk_size, dim)
    def disable_forward_chunking(self) -> None:
        def fn_recursive_feed_forward(module: torch.nn.Module, chunk_size: int, dim: int):
            if hasattr(module, 'set_chunk_feed_forward'): module.set_chunk_feed_forward(chunk_size=chunk_size, dim=dim)
            for child in module.children(): fn_recursive_feed_forward(child, chunk_size, dim)
        for module in self.children(): fn_recursive_feed_forward(module, None, 0)
    def set_default_attn_processor(self) -> None:
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    def _set_gradient_checkpointing(self, module, value: bool=False) -> None:
        if isinstance(module, (CrossAttnDownBlockMotion, DownBlockMotion, CrossAttnUpBlockMotion, UpBlockMotion)): module.gradient_checkpointing = value
    def enable_freeu(self, s1: float, s2: float, b1: float, b2: float) -> None:
        """Args:"""
        for i, upsample_block in enumerate(self.up_blocks):
            setattr(upsample_block, 's1', s1)
            setattr(upsample_block, 's2', s2)
            setattr(upsample_block, 'b1', b1)
            setattr(upsample_block, 'b2', b2)
    def disable_freeu(self) -> None:
        freeu_keys = {'s1', 's2', 'b1', 'b2'}
        for i, upsample_block in enumerate(self.up_blocks):
            for k in freeu_keys:
                if hasattr(upsample_block, k) or getattr(upsample_block, k, None) is not None: setattr(upsample_block, k, None)
    def fuse_qkv_projections(self):
        self.original_attn_processors = None
        for _, attn_processor in self.attn_processors.items():
            if 'Added' in str(attn_processor.__class__.__name__): raise ValueError('`fuse_qkv_projections()` is not supported for models having added KV projections.')
        self.original_attn_processors = self.attn_processors
        for module in self.modules():
            if isinstance(module, Attention): module.fuse_projections(fuse=True)
        self.set_attn_processor(FusedAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, timestep_cond: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None,
    down_block_additional_residuals: Optional[Tuple[torch.Tensor]]=None, mid_block_additional_residual: Optional[torch.Tensor]=None, return_dict: bool=True) -> Union[UNetMotionOutput, Tuple[torch.Tensor]]:
        """Returns:"""
        default_overall_up_factor = 2 ** self.num_upsamplers
        forward_upsample_size = False
        upsample_size = None
        if any((s % default_overall_up_factor != 0 for s in sample.shape[-2:])): forward_upsample_size = True
        if attention_mask is not None:
            attention_mask = (1 - attention_mask.to(sample.dtype)) * -10000.0
            attention_mask = attention_mask.unsqueeze(1)
        timesteps = timestep
        if not torch.is_tensor(timesteps):
            is_mps = sample.device.type == 'mps'
            if isinstance(timestep, float): dtype = torch.float32 if is_mps else torch.float64
            else: dtype = torch.int32 if is_mps else torch.int64
            timesteps = torch.tensor([timesteps], dtype=dtype, device=sample.device)
        elif len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        num_frames = sample.shape[2]
        timesteps = timesteps.expand(sample.shape[0])
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=self.dtype)
        emb = self.time_embedding(t_emb, timestep_cond)
        aug_emb = None
        if self.config.addition_embed_type == 'text_time':
            if 'text_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `text_embeds` to be passed in `added_cond_kwargs`")
            text_embeds = added_cond_kwargs.get('text_embeds')
            if 'time_ids' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `time_ids` to be passed in `added_cond_kwargs`")
            time_ids = added_cond_kwargs.get('time_ids')
            time_embeds = self.add_time_proj(time_ids.flatten())
            time_embeds = time_embeds.reshape((text_embeds.shape[0], -1))
            add_embeds = torch.concat([text_embeds, time_embeds], dim=-1)
            add_embeds = add_embeds.to(emb.dtype)
            aug_emb = self.add_embedding(add_embeds)
        emb = emb if aug_emb is None else emb + aug_emb
        emb = emb.repeat_interleave(repeats=num_frames, dim=0)
        if self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'ip_image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'ip_image_proj' which requires the keyword argument `image_embeds` to be passed in  `added_conditions`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            image_embeds = self.encoder_hid_proj(image_embeds)
            image_embeds = [image_embed.repeat_interleave(repeats=num_frames, dim=0) for image_embed in image_embeds]
            encoder_hidden_states = (encoder_hidden_states, image_embeds)
        sample = sample.permute(0, 2, 1, 3, 4).reshape((sample.shape[0] * num_frames, -1) + sample.shape[3:])
        sample = self.conv_in(sample)
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention: sample, res_samples = downsample_block(hidden_states=sample,
            temb=emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, num_frames=num_frames)
            down_block_res_samples += res_samples
        if down_block_additional_residuals is not None:
            new_down_block_res_samples = ()
            for down_block_res_sample, down_block_additional_residual in zip(down_block_res_samples, down_block_additional_residuals):
                down_block_res_sample = down_block_res_sample + down_block_additional_residual
                new_down_block_res_samples += (down_block_res_sample,)
            down_block_res_samples = new_down_block_res_samples
        if self.mid_block is not None:
            if hasattr(self.mid_block, 'motion_modules'): sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask,
            num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs)
        if mid_block_additional_residual is not None: sample = sample + mid_block_additional_residual
        for i, upsample_block in enumerate(self.up_blocks):
            is_final_block = i == len(self.up_blocks) - 1
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if not is_final_block and forward_upsample_size: upsample_size = down_block_res_samples[-1].shape[2:]
            if hasattr(upsample_block, 'has_cross_attention') and upsample_block.has_cross_attention: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples,
            encoder_hidden_states=encoder_hidden_states, upsample_size=upsample_size, attention_mask=attention_mask, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples, upsample_size=upsample_size, num_frames=num_frames)
        if self.conv_norm_out:
            sample = self.conv_norm_out(sample)
            sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        sample = sample[None, :].reshape((-1, num_frames) + sample.shape[1:]).permute(0, 2, 1, 3, 4)
        if not return_dict: return (sample,)
        return UNetMotionOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
