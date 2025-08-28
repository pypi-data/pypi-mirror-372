'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from ....utils import deprecate
from ....configuration_utils import ConfigMixin, register_to_config
from ....models import ModelMixin
from ....models.activations import get_activation
from ....models.attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, Attention, AttentionProcessor, AttnAddedKVProcessor, AttnAddedKVProcessor2_0, AttnProcessor
from ....models.embeddings import (GaussianFourierProjection, ImageHintTimeEmbedding, ImageProjection, ImageTimeEmbedding, TextImageProjection,
TextImageTimeEmbedding, TextTimeEmbedding, TimestepEmbedding, Timesteps)
from ....models.resnet import ResnetBlockCondNorm2D
from ....models.sapiens_transformers.dual_transformer_2d import DualTransformer2DModel
from ....models.sapiens_transformers.transformer_2d import Transformer2DModel
from ....models.unets.unet_2d_condition import UNet2DConditionOutput
from ....utils import USE_PEFT_BACKEND, is_torch_version, scale_lora_layers, unscale_lora_layers
from ....utils.torch_utils import apply_freeu
def get_down_block(down_block_type, num_layers, in_channels, out_channels, temb_channels, add_downsample, resnet_eps, resnet_act_fn, num_attention_heads, transformer_layers_per_block,
attention_type, attention_head_dim, resnet_groups=None, cross_attention_dim=None, downsample_padding=None, dual_cross_attention=False, use_linear_projection=False, only_cross_attention=False,
upcast_attention=False, resnet_time_scale_shift='default', resnet_skip_time_act=False, resnet_out_scale_factor=1.0, cross_attention_norm=None, dropout=0.0):
    down_block_type = down_block_type[7:] if down_block_type.startswith('UNetRes') else down_block_type
    if down_block_type == 'DownBlockFlat': return DownBlockFlat(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, dropout=dropout,
    add_downsample=add_downsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups, downsample_padding=downsample_padding, resnet_time_scale_shift=resnet_time_scale_shift)
    elif down_block_type == 'CrossAttnDownBlockFlat':
        if cross_attention_dim is None: raise ValueError('cross_attention_dim must be specified for CrossAttnDownBlockFlat')
        return CrossAttnDownBlockFlat(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, dropout=dropout, add_downsample=add_downsample,
        resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups, downsample_padding=downsample_padding, cross_attention_dim=cross_attention_dim,
        num_attention_heads=num_attention_heads, dual_cross_attention=dual_cross_attention, use_linear_projection=use_linear_projection,
        only_cross_attention=only_cross_attention, resnet_time_scale_shift=resnet_time_scale_shift)
    raise ValueError(f'{down_block_type} is not supported.')
def get_up_block(up_block_type, num_layers, in_channels, out_channels, prev_output_channel, temb_channels, add_upsample, resnet_eps, resnet_act_fn, num_attention_heads,
transformer_layers_per_block, resolution_idx, attention_type, attention_head_dim, resnet_groups=None, cross_attention_dim=None, dual_cross_attention=False, use_linear_projection=False,
only_cross_attention=False, upcast_attention=False, resnet_time_scale_shift='default', resnet_skip_time_act=False, resnet_out_scale_factor=1.0, cross_attention_norm=None, dropout=0.0):
    up_block_type = up_block_type[7:] if up_block_type.startswith('UNetRes') else up_block_type
    if up_block_type == 'UpBlockFlat': return UpBlockFlat(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, prev_output_channel=prev_output_channel,
    temb_channels=temb_channels, dropout=dropout, add_upsample=add_upsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn,
    resnet_groups=resnet_groups, resnet_time_scale_shift=resnet_time_scale_shift)
    elif up_block_type == 'CrossAttnUpBlockFlat':
        if cross_attention_dim is None: raise ValueError('cross_attention_dim must be specified for CrossAttnUpBlockFlat')
        return CrossAttnUpBlockFlat(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, prev_output_channel=prev_output_channel, temb_channels=temb_channels,
        dropout=dropout, add_upsample=add_upsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups, cross_attention_dim=cross_attention_dim,
        num_attention_heads=num_attention_heads, dual_cross_attention=dual_cross_attention, use_linear_projection=use_linear_projection,
        only_cross_attention=only_cross_attention, resnet_time_scale_shift=resnet_time_scale_shift)
    raise ValueError(f'{up_block_type} is not supported.')
class FourierEmbedder(nn.Module):
    def __init__(self, num_freqs=64, temperature=100):
        super().__init__()
        self.num_freqs = num_freqs
        self.temperature = temperature
        freq_bands = temperature ** (torch.arange(num_freqs) / num_freqs)
        freq_bands = freq_bands[None, None, None]
        self.register_buffer('freq_bands', freq_bands, persistent=False)
    def __call__(self, x):
        x = self.freq_bands * x.unsqueeze(-1)
        return torch.stack((x.sin(), x.cos()), dim=-1).permute(0, 1, 3, 4, 2).reshape(*x.shape[:2], -1)
class GLIGENTextBoundingboxProjection(nn.Module):
    def __init__(self, positive_len, out_dim, feature_type, fourier_freqs=8):
        super().__init__()
        self.positive_len = positive_len
        self.out_dim = out_dim
        self.fourier_embedder = FourierEmbedder(num_freqs=fourier_freqs)
        self.position_dim = fourier_freqs * 2 * 4
        if isinstance(out_dim, tuple): out_dim = out_dim[0]
        if feature_type == 'text-only':
            self.linears = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.null_positive_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
        elif feature_type == 'text-image':
            self.linears_text = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.linears_image = nn.Sequential(nn.Linear(self.positive_len + self.position_dim, 512), nn.SiLU(), nn.Linear(512, 512), nn.SiLU(), nn.Linear(512, out_dim))
            self.null_text_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
            self.null_image_feature = torch.nn.Parameter(torch.zeros([self.positive_len]))
        self.null_position_feature = torch.nn.Parameter(torch.zeros([self.position_dim]))
    def forward(self, boxes, masks, positive_embeddings=None, phrases_masks=None, image_masks=None, phrases_embeddings=None, image_embeddings=None):
        masks = masks.unsqueeze(-1)
        xyxy_embedding = self.fourier_embedder(boxes)
        xyxy_null = self.null_position_feature.view(1, 1, -1)
        xyxy_embedding = xyxy_embedding * masks + (1 - masks) * xyxy_null
        if positive_embeddings:
            positive_null = self.null_positive_feature.view(1, 1, -1)
            positive_embeddings = positive_embeddings * masks + (1 - masks) * positive_null
            objs = self.linears(torch.cat([positive_embeddings, xyxy_embedding], dim=-1))
        else:
            phrases_masks = phrases_masks.unsqueeze(-1)
            image_masks = image_masks.unsqueeze(-1)
            text_null = self.null_text_feature.view(1, 1, -1)
            image_null = self.null_image_feature.view(1, 1, -1)
            phrases_embeddings = phrases_embeddings * phrases_masks + (1 - phrases_masks) * text_null
            image_embeddings = image_embeddings * image_masks + (1 - image_masks) * image_null
            objs_text = self.linears_text(torch.cat([phrases_embeddings, xyxy_embedding], dim=-1))
            objs_image = self.linears_image(torch.cat([image_embeddings, xyxy_embedding], dim=-1))
            objs = torch.cat([objs_text, objs_image], dim=1)
        return objs
class UNetFlatConditionModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    _no_split_modules = ['BasicTransformerBlock', 'ResnetBlockFlat', 'CrossAttnUpBlockFlat']
    @register_to_config
    def __init__(self, sample_size: Optional[int]=None, in_channels: int=4, out_channels: int=4, center_input_sample: bool=False, flip_sin_to_cos: bool=True, freq_shift: int=0,
    down_block_types: Tuple[str]=('CrossAttnDownBlockFlat', 'CrossAttnDownBlockFlat', 'CrossAttnDownBlockFlat', 'DownBlockFlat'), mid_block_type: Optional[str]='UNetMidBlockFlatCrossAttn',
    up_block_types: Tuple[str]=('UpBlockFlat', 'CrossAttnUpBlockFlat', 'CrossAttnUpBlockFlat', 'CrossAttnUpBlockFlat'), only_cross_attention: Union[bool, Tuple[bool]]=False,
    block_out_channels: Tuple[int]=(320, 640, 1280, 1280), layers_per_block: Union[int, Tuple[int]]=2, downsample_padding: int=1, mid_block_scale_factor: float=1,
    dropout: float=0.0, act_fn: str='silu', norm_num_groups: Optional[int]=32, norm_eps: float=1e-05, cross_attention_dim: Union[int, Tuple[int]]=1280, transformer_layers_per_block: Union[int,
    Tuple[int], Tuple[Tuple]]=1, reverse_transformer_layers_per_block: Optional[Tuple[Tuple[int]]]=None, encoder_hid_dim: Optional[int]=None, encoder_hid_dim_type: Optional[str]=None,
    attention_head_dim: Union[int, Tuple[int]]=8, num_attention_heads: Optional[Union[int, Tuple[int]]]=None, dual_cross_attention: bool=False, use_linear_projection: bool=False,
    class_embed_type: Optional[str]=None, addition_embed_type: Optional[str]=None, addition_time_embed_dim: Optional[int]=None, num_class_embeds: Optional[int]=None, upcast_attention: bool=False,
    resnet_time_scale_shift: str='default', resnet_skip_time_act: bool=False, resnet_out_scale_factor: int=1.0, time_embedding_type: str='positional', time_embedding_dim: Optional[int]=None,
    time_embedding_act_fn: Optional[str]=None, timestep_post_act: Optional[str]=None, time_cond_proj_dim: Optional[int]=None, conv_in_kernel: int=3, conv_out_kernel: int=3,
    projection_class_embeddings_input_dim: Optional[int]=None, attention_type: str='default', class_embeddings_concat: bool=False, mid_block_only_cross_attention: Optional[bool]=None,
    cross_attention_norm: Optional[str]=None, addition_embed_type_num_heads=64):
        super().__init__()
        self.sample_size = sample_size
        if num_attention_heads is not None: raise ValueError('At the moment it is not possible to define the number of attention heads via `num_attention_heads` because of a naming issue as described in https://github.com/huggingface/diffusers/issues/2011#issuecomment-1547958131. Passing `num_attention_heads` will only be supported in diffusers v0.19.')
        num_attention_heads = num_attention_heads or attention_head_dim
        if len(down_block_types) != len(up_block_types): raise ValueError(f'Must provide the same number of `down_block_types` as `up_block_types`. `down_block_types`: {down_block_types}. `up_block_types`: {up_block_types}.')
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(only_cross_attention, bool) and len(only_cross_attention) != len(down_block_types): raise ValueError(f'Must provide the same number of `only_cross_attention` as `down_block_types`. `only_cross_attention`: {only_cross_attention}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        if not isinstance(attention_head_dim, int) and len(attention_head_dim) != len(down_block_types): raise ValueError(f'Must provide the same number of `attention_head_dim` as `down_block_types`. `attention_head_dim`: {attention_head_dim}. `down_block_types`: {down_block_types}.')
        if isinstance(cross_attention_dim, list) and len(cross_attention_dim) != len(down_block_types): raise ValueError(f'Must provide the same number of `cross_attention_dim` as `down_block_types`. `cross_attention_dim`: {cross_attention_dim}. `down_block_types`: {down_block_types}.')
        if not isinstance(layers_per_block, int) and len(layers_per_block) != len(down_block_types): raise ValueError(f'Must provide the same number of `layers_per_block` as `down_block_types`. `layers_per_block`: {layers_per_block}. `down_block_types`: {down_block_types}.')
        if isinstance(transformer_layers_per_block, list) and reverse_transformer_layers_per_block is None:
            for layer_number_per_block in transformer_layers_per_block:
                if isinstance(layer_number_per_block, list): raise ValueError("Must provide 'reverse_transformer_layers_per_block` if using asymmetrical UNet.")
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = LinearMultiDim(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        if time_embedding_type == 'fourier':
            time_embed_dim = time_embedding_dim or block_out_channels[0] * 2
            if time_embed_dim % 2 != 0: raise ValueError(f'`time_embed_dim` should be divisible by 2, but is {time_embed_dim}.')
            self.time_proj = GaussianFourierProjection(time_embed_dim // 2, set_W_to_weight=False, log=False, flip_sin_to_cos=flip_sin_to_cos)
            timestep_input_dim = time_embed_dim
        elif time_embedding_type == 'positional':
            time_embed_dim = time_embedding_dim or block_out_channels[0] * 4
            self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
            timestep_input_dim = block_out_channels[0]
        else: raise ValueError(f'{time_embedding_type} does not exist. Please make sure to use one of `fourier` or `positional`.')
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn, post_act_fn=timestep_post_act, cond_proj_dim=time_cond_proj_dim)
        if encoder_hid_dim_type is None and encoder_hid_dim is not None:
            encoder_hid_dim_type = 'text_proj'
            self.register_to_config(encoder_hid_dim_type=encoder_hid_dim_type)
        if encoder_hid_dim is None and encoder_hid_dim_type is not None: raise ValueError(f'`encoder_hid_dim` has to be defined when `encoder_hid_dim_type` is set to {encoder_hid_dim_type}.')
        if encoder_hid_dim_type == 'text_proj': self.encoder_hid_proj = nn.Linear(encoder_hid_dim, cross_attention_dim)
        elif encoder_hid_dim_type == 'text_image_proj': self.encoder_hid_proj = TextImageProjection(text_embed_dim=encoder_hid_dim, image_embed_dim=cross_attention_dim, cross_attention_dim=cross_attention_dim)
        elif encoder_hid_dim_type == 'image_proj': self.encoder_hid_proj = ImageProjection(image_embed_dim=encoder_hid_dim, cross_attention_dim=cross_attention_dim)
        elif encoder_hid_dim_type is not None: raise ValueError(f"`encoder_hid_dim_type`: {encoder_hid_dim_type} must be None, 'text_proj', 'text_image_proj' or 'image_proj'.")
        else: self.encoder_hid_proj = None
        if class_embed_type is None and num_class_embeds is not None: self.class_embedding = nn.Embedding(num_class_embeds, time_embed_dim)
        elif class_embed_type == 'timestep': self.class_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn)
        elif class_embed_type == 'identity': self.class_embedding = nn.Identity(time_embed_dim, time_embed_dim)
        elif class_embed_type == 'projection':
            if projection_class_embeddings_input_dim is None: raise ValueError("`class_embed_type`: 'projection' requires `projection_class_embeddings_input_dim` be set")
            self.class_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        elif class_embed_type == 'simple_projection':
            if projection_class_embeddings_input_dim is None: raise ValueError("`class_embed_type`: 'simple_projection' requires `projection_class_embeddings_input_dim` be set")
            self.class_embedding = nn.Linear(projection_class_embeddings_input_dim, time_embed_dim)
        else: self.class_embedding = None
        if addition_embed_type == 'text':
            if encoder_hid_dim is not None: text_time_embedding_from_dim = encoder_hid_dim
            else: text_time_embedding_from_dim = cross_attention_dim
            self.add_embedding = TextTimeEmbedding(text_time_embedding_from_dim, time_embed_dim, num_heads=addition_embed_type_num_heads)
        elif addition_embed_type == 'text_image': self.add_embedding = TextImageTimeEmbedding(text_embed_dim=cross_attention_dim, image_embed_dim=cross_attention_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type == 'text_time':
            self.add_time_proj = Timesteps(addition_time_embed_dim, flip_sin_to_cos, freq_shift)
            self.add_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        elif addition_embed_type == 'image': self.add_embedding = ImageTimeEmbedding(image_embed_dim=encoder_hid_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type == 'image_hint': self.add_embedding = ImageHintTimeEmbedding(image_embed_dim=encoder_hid_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type is not None: raise ValueError(f"addition_embed_type: {addition_embed_type} must be None, 'text' or 'text_image'.")
        if time_embedding_act_fn is None: self.time_embed_act = None
        else: self.time_embed_act = get_activation(time_embedding_act_fn)
        self.down_blocks = nn.ModuleList([])
        self.up_blocks = nn.ModuleList([])
        if isinstance(only_cross_attention, bool):
            if mid_block_only_cross_attention is None: mid_block_only_cross_attention = only_cross_attention
            only_cross_attention = [only_cross_attention] * len(down_block_types)
        if mid_block_only_cross_attention is None: mid_block_only_cross_attention = False
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        if isinstance(attention_head_dim, int): attention_head_dim = (attention_head_dim,) * len(down_block_types)
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,) * len(down_block_types)
        if isinstance(layers_per_block, int): layers_per_block = [layers_per_block] * len(down_block_types)
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(down_block_types)
        if class_embeddings_concat: blocks_time_embed_dim = time_embed_dim * 2
        else: blocks_time_embed_dim = time_embed_dim
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block[i], transformer_layers_per_block=transformer_layers_per_block[i], in_channels=input_channel,
            out_channels=output_channel, temb_channels=blocks_time_embed_dim, add_downsample=not is_final_block, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups,
            cross_attention_dim=cross_attention_dim[i], num_attention_heads=num_attention_heads[i], downsample_padding=downsample_padding, dual_cross_attention=dual_cross_attention,
            use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift,
            attention_type=attention_type, resnet_skip_time_act=resnet_skip_time_act, resnet_out_scale_factor=resnet_out_scale_factor, cross_attention_norm=cross_attention_norm,
            attention_head_dim=attention_head_dim[i] if attention_head_dim[i] is not None else output_channel, dropout=dropout)
            self.down_blocks.append(down_block)
        if mid_block_type == 'UNetMidBlockFlatCrossAttn': self.mid_block = UNetMidBlockFlatCrossAttn(transformer_layers_per_block=transformer_layers_per_block[-1], in_channels=block_out_channels[-1],
        temb_channels=blocks_time_embed_dim, dropout=dropout, resnet_eps=norm_eps, resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor, resnet_time_scale_shift=resnet_time_scale_shift,
        cross_attention_dim=cross_attention_dim[-1], num_attention_heads=num_attention_heads[-1], resnet_groups=norm_num_groups, dual_cross_attention=dual_cross_attention,
        use_linear_projection=use_linear_projection, upcast_attention=upcast_attention, attention_type=attention_type)
        elif mid_block_type == 'UNetMidBlockFlatSimpleCrossAttn': self.mid_block = UNetMidBlockFlatSimpleCrossAttn(in_channels=block_out_channels[-1], temb_channels=blocks_time_embed_dim,
        dropout=dropout, resnet_eps=norm_eps, resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor, cross_attention_dim=cross_attention_dim[-1], attention_head_dim=attention_head_dim[-1],
        resnet_groups=norm_num_groups, resnet_time_scale_shift=resnet_time_scale_shift, skip_time_act=resnet_skip_time_act, only_cross_attention=mid_block_only_cross_attention, cross_attention_norm=cross_attention_norm)
        elif mid_block_type == 'UNetMidBlockFlat': self.mid_block = UNetMidBlockFlat(in_channels=block_out_channels[-1], temb_channels=blocks_time_embed_dim, dropout=dropout, num_layers=0,
        resnet_eps=norm_eps, resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor, resnet_groups=norm_num_groups, resnet_time_scale_shift=resnet_time_scale_shift, add_attention=False)
        elif mid_block_type is None: self.mid_block = None
        else: raise ValueError(f'unknown mid_block_type : {mid_block_type}')
        self.num_upsamplers = 0
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
        reversed_layers_per_block = list(reversed(layers_per_block))
        reversed_cross_attention_dim = list(reversed(cross_attention_dim))
        reversed_transformer_layers_per_block = list(reversed(transformer_layers_per_block)) if reverse_transformer_layers_per_block is None else reverse_transformer_layers_per_block
        only_cross_attention = list(reversed(only_cross_attention))
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
            up_block = get_up_block(up_block_type, num_layers=reversed_layers_per_block[i] + 1, transformer_layers_per_block=reversed_transformer_layers_per_block[i], in_channels=input_channel,
            out_channels=output_channel, prev_output_channel=prev_output_channel, temb_channels=blocks_time_embed_dim, add_upsample=add_upsample, resnet_eps=norm_eps, resnet_act_fn=act_fn,
            resolution_idx=i, resnet_groups=norm_num_groups, cross_attention_dim=reversed_cross_attention_dim[i], num_attention_heads=reversed_num_attention_heads[i], dual_cross_attention=dual_cross_attention,
            use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift,
            attention_type=attention_type, resnet_skip_time_act=resnet_skip_time_act, resnet_out_scale_factor=resnet_out_scale_factor, cross_attention_norm=cross_attention_norm,
            attention_head_dim=attention_head_dim[i] if attention_head_dim[i] is not None else output_channel, dropout=dropout)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        if norm_num_groups is not None:
            self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=norm_eps)
            self.conv_act = get_activation(act_fn)
        else:
            self.conv_norm_out = None
            self.conv_act = None
        conv_out_padding = (conv_out_kernel - 1) // 2
        self.conv_out = LinearMultiDim(block_out_channels[0], out_channels, kernel_size=conv_out_kernel, padding=conv_out_padding)
        if attention_type in ['gated', 'gated-text-image']:
            positive_len = 768
            if isinstance(cross_attention_dim, int): positive_len = cross_attention_dim
            elif isinstance(cross_attention_dim, (list, tuple)): positive_len = cross_attention_dim[0]
            feature_type = 'text-only' if attention_type == 'gated' else 'text-image'
            self.position_net = GLIGENTextBoundingboxProjection(positive_len=positive_len, out_dim=cross_attention_dim, feature_type=feature_type)
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
    def set_default_attn_processor(self):
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    def set_attention_slice(self, slice_size):
        """Args:"""
        sliceable_head_dims = []
        def fn_recursive_retrieve_sliceable_dims(module: torch.nn.Module):
            if hasattr(module, 'set_attention_slice'): sliceable_head_dims.append(module.sliceable_head_dim)
            for child in module.children(): fn_recursive_retrieve_sliceable_dims(child)
        for module in self.children(): fn_recursive_retrieve_sliceable_dims(module)
        num_sliceable_layers = len(sliceable_head_dims)
        if slice_size == 'auto': slice_size = [dim // 2 for dim in sliceable_head_dims]
        elif slice_size == 'max': slice_size = num_sliceable_layers * [1]
        slice_size = num_sliceable_layers * [slice_size] if not isinstance(slice_size, list) else slice_size
        if len(slice_size) != len(sliceable_head_dims): raise ValueError(f'You have provided {len(slice_size)}, but {self.config} has {len(sliceable_head_dims)} different attention layers. Make sure to match `len(slice_size)` to be {len(sliceable_head_dims)}.')
        for i in range(len(slice_size)):
            size = slice_size[i]
            dim = sliceable_head_dims[i]
            if size is not None and size > dim: raise ValueError(f'size {size} has to be smaller or equal to {dim}.')
        def fn_recursive_set_attention_slice(module: torch.nn.Module, slice_size: List[int]):
            if hasattr(module, 'set_attention_slice'): module.set_attention_slice(slice_size.pop())
            for child in module.children(): fn_recursive_set_attention_slice(child, slice_size)
        reversed_slice_size = list(reversed(slice_size))
        for module in self.children(): fn_recursive_set_attention_slice(module, reversed_slice_size)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def enable_freeu(self, s1, s2, b1, b2):
        """Args:"""
        for i, upsample_block in enumerate(self.up_blocks):
            setattr(upsample_block, 's1', s1)
            setattr(upsample_block, 's2', s2)
            setattr(upsample_block, 'b1', b1)
            setattr(upsample_block, 'b2', b2)
    def disable_freeu(self):
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
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def unload_lora(self):
        deprecate('unload_lora', '0.28.0', 'Calling `unload_lora()` is deprecated and will be removed in a future version. Please install `peft` and then call `disable_adapters().')
        for module in self.modules():
            if hasattr(module, 'set_lora_layer'): module.set_lora_layer(None)
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, class_labels: Optional[torch.Tensor]=None,
    timestep_cond: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, added_cond_kwargs: Optional[Dict[str,
    torch.Tensor]]=None, down_block_additional_residuals: Optional[Tuple[torch.Tensor]]=None, mid_block_additional_residual: Optional[torch.Tensor]=None,
    down_intrablock_additional_residuals: Optional[Tuple[torch.Tensor]]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    return_dict: bool=True) -> Union[UNet2DConditionOutput, Tuple]:
        """Returns:"""
        default_overall_up_factor = 2 ** self.num_upsamplers
        forward_upsample_size = False
        upsample_size = None
        for dim in sample.shape[-2:]:
            if dim % default_overall_up_factor != 0:
                forward_upsample_size = True
                break
        if attention_mask is not None:
            attention_mask = (1 - attention_mask.to(sample.dtype)) * -10000.0
            attention_mask = attention_mask.unsqueeze(1)
        if encoder_attention_mask is not None:
            encoder_attention_mask = (1 - encoder_attention_mask.to(sample.dtype)) * -10000.0
            encoder_attention_mask = encoder_attention_mask.unsqueeze(1)
        if self.config.center_input_sample: sample = 2 * sample - 1.0
        timesteps = timestep
        if not torch.is_tensor(timesteps):
            is_mps = sample.device.type == 'mps'
            if isinstance(timestep, float): dtype = torch.float32 if is_mps else torch.float64
            else: dtype = torch.int32 if is_mps else torch.int64
            timesteps = torch.tensor([timesteps], dtype=dtype, device=sample.device)
        elif len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        timesteps = timesteps.expand(sample.shape[0])
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=sample.dtype)
        emb = self.time_embedding(t_emb, timestep_cond)
        aug_emb = None
        if self.class_embedding is not None:
            if class_labels is None: raise ValueError('class_labels should be provided when num_class_embeds > 0')
            if self.config.class_embed_type == 'timestep':
                class_labels = self.time_proj(class_labels)
                class_labels = class_labels.to(dtype=sample.dtype)
            class_emb = self.class_embedding(class_labels).to(dtype=sample.dtype)
            if self.config.class_embeddings_concat: emb = torch.cat([emb, class_emb], dim=-1)
            else: emb = emb + class_emb
        if self.config.addition_embed_type == 'text': aug_emb = self.add_embedding(encoder_hidden_states)
        elif self.config.addition_embed_type == 'text_image':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_image' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            text_embs = added_cond_kwargs.get('text_embeds', encoder_hidden_states)
            aug_emb = self.add_embedding(text_embs, image_embs)
        elif self.config.addition_embed_type == 'text_time':
            if 'text_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `text_embeds` to be passed in `added_cond_kwargs`")
            text_embeds = added_cond_kwargs.get('text_embeds')
            if 'time_ids' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'text_time' which requires the keyword argument `time_ids` to be passed in `added_cond_kwargs`")
            time_ids = added_cond_kwargs.get('time_ids')
            time_embeds = self.add_time_proj(time_ids.flatten())
            time_embeds = time_embeds.reshape((text_embeds.shape[0], -1))
            add_embeds = torch.concat([text_embeds, time_embeds], dim=-1)
            add_embeds = add_embeds.to(emb.dtype)
            aug_emb = self.add_embedding(add_embeds)
        elif self.config.addition_embed_type == 'image':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'image' which requires the keyword argument `image_embeds` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            aug_emb = self.add_embedding(image_embs)
        elif self.config.addition_embed_type == 'image_hint':
            if 'image_embeds' not in added_cond_kwargs or 'hint' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `addition_embed_type` set to 'image_hint' which requires the keyword arguments `image_embeds` and `hint` to be passed in `added_cond_kwargs`")
            image_embs = added_cond_kwargs.get('image_embeds')
            hint = added_cond_kwargs.get('hint')
            aug_emb, hint = self.add_embedding(image_embs, hint)
            sample = torch.cat([sample, hint], dim=1)
        emb = emb + aug_emb if aug_emb is not None else emb
        if self.time_embed_act is not None: emb = self.time_embed_act(emb)
        if self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'text_proj': encoder_hidden_states = self.encoder_hid_proj(encoder_hidden_states)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'text_image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'text_image_proj' which requires the keyword argument `image_embeds` to be passed in  `added_conditions`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            encoder_hidden_states = self.encoder_hid_proj(encoder_hidden_states, image_embeds)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'image_proj' which requires the keyword argument `image_embeds` to be passed in  `added_conditions`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            encoder_hidden_states = self.encoder_hid_proj(image_embeds)
        elif self.encoder_hid_proj is not None and self.config.encoder_hid_dim_type == 'ip_image_proj':
            if 'image_embeds' not in added_cond_kwargs: raise ValueError(f"{self.__class__} has the config param `encoder_hid_dim_type` set to 'ip_image_proj' which requires the keyword argument `image_embeds` to be passed in  `added_conditions`")
            image_embeds = added_cond_kwargs.get('image_embeds')
            image_embeds = self.encoder_hid_proj(image_embeds)
            encoder_hidden_states = (encoder_hidden_states, image_embeds)
        sample = self.conv_in(sample)
        if cross_attention_kwargs is not None and cross_attention_kwargs.get('gligen', None) is not None:
            cross_attention_kwargs = cross_attention_kwargs.copy()
            gligen_args = cross_attention_kwargs.pop('gligen')
            cross_attention_kwargs['gligen'] = {'objs': self.position_net(**gligen_args)}
        lora_scale = cross_attention_kwargs.get('scale', 1.0) if cross_attention_kwargs is not None else 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        is_controlnet = mid_block_additional_residual is not None and down_block_additional_residuals is not None
        is_adapter = down_intrablock_additional_residuals is not None
        if not is_adapter and mid_block_additional_residual is None and (down_block_additional_residuals is not None):
            deprecate('T2I should not use down_block_additional_residuals', '1.3.0', 'Passing intrablock residual connections with `down_block_additional_residuals` is deprecated and will be removed in diffusers 1.3.0. `down_block_additional_residuals` should only be used for ControlNet. Please make sure use `down_intrablock_additional_residuals` instead. ', standard_warn=False)
            down_intrablock_additional_residuals = down_block_additional_residuals
            is_adapter = True
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention:
                additional_residuals = {}
                if is_adapter and len(down_intrablock_additional_residuals) > 0: additional_residuals['additional_residuals'] = down_intrablock_additional_residuals.pop(0)
                sample, res_samples = downsample_block(hidden_states=sample, temb=emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs,
                encoder_attention_mask=encoder_attention_mask, **additional_residuals)
            else:
                sample, res_samples = downsample_block(hidden_states=sample, temb=emb)
                if is_adapter and len(down_intrablock_additional_residuals) > 0: sample += down_intrablock_additional_residuals.pop(0)
            down_block_res_samples += res_samples
        if is_controlnet:
            new_down_block_res_samples = ()
            for down_block_res_sample, down_block_additional_residual in zip(down_block_res_samples, down_block_additional_residuals):
                down_block_res_sample = down_block_res_sample + down_block_additional_residual
                new_down_block_res_samples = new_down_block_res_samples + (down_block_res_sample,)
            down_block_res_samples = new_down_block_res_samples
        if self.mid_block is not None:
            if hasattr(self.mid_block, 'has_cross_attention') and self.mid_block.has_cross_attention: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask,
            cross_attention_kwargs=cross_attention_kwargs, encoder_attention_mask=encoder_attention_mask)
            else: sample = self.mid_block(sample, emb)
            if is_adapter and len(down_intrablock_additional_residuals) > 0 and (sample.shape == down_intrablock_additional_residuals[0].shape): sample += down_intrablock_additional_residuals.pop(0)
        if is_controlnet: sample = sample + mid_block_additional_residual
        for i, upsample_block in enumerate(self.up_blocks):
            is_final_block = i == len(self.up_blocks) - 1
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if not is_final_block and forward_upsample_size: upsample_size = down_block_res_samples[-1].shape[2:]
            if hasattr(upsample_block, 'has_cross_attention') and upsample_block.has_cross_attention: sample = upsample_block(hidden_states=sample, temb=emb,
            res_hidden_states_tuple=res_samples, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, upsample_size=upsample_size,
            attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask)
            else: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples, upsample_size=upsample_size, scale=lora_scale)
        if self.conv_norm_out:
            sample = self.conv_norm_out(sample)
            sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (sample,)
        return UNet2DConditionOutput(sample=sample)
class LinearMultiDim(nn.Linear):
    def __init__(self, in_features, out_features=None, second_dim=4, *args, **kwargs):
        in_features = [in_features, second_dim, 1] if isinstance(in_features, int) else list(in_features)
        if out_features is None: out_features = in_features
        out_features = [out_features, second_dim, 1] if isinstance(out_features, int) else list(out_features)
        self.in_features_multidim = in_features
        self.out_features_multidim = out_features
        super().__init__(np.array(in_features).prod(), np.array(out_features).prod())
    def forward(self, input_tensor, *args, **kwargs):
        shape = input_tensor.shape
        n_dim = len(self.in_features_multidim)
        input_tensor = input_tensor.reshape(*shape[0:-n_dim], self.in_features)
        output_tensor = super().forward(input_tensor)
        output_tensor = output_tensor.view(*shape[0:-n_dim], *self.out_features_multidim)
        return output_tensor
class ResnetBlockFlat(nn.Module):
    def __init__(self, *, in_channels, out_channels=None, dropout=0.0, temb_channels=512, groups=32, groups_out=None, pre_norm=True, eps=1e-06, time_embedding_norm='default', use_in_shortcut=None, second_dim=4, **kwargs):
        super().__init__()
        self.pre_norm = pre_norm
        self.pre_norm = True
        in_channels = [in_channels, second_dim, 1] if isinstance(in_channels, int) else list(in_channels)
        self.in_channels_prod = np.array(in_channels).prod()
        self.channels_multidim = in_channels
        if out_channels is not None:
            out_channels = [out_channels, second_dim, 1] if isinstance(out_channels, int) else list(out_channels)
            out_channels_prod = np.array(out_channels).prod()
            self.out_channels_multidim = out_channels
        else:
            out_channels_prod = self.in_channels_prod
            self.out_channels_multidim = self.channels_multidim
        self.time_embedding_norm = time_embedding_norm
        if groups_out is None: groups_out = groups
        self.norm1 = torch.nn.GroupNorm(num_groups=groups, num_channels=self.in_channels_prod, eps=eps, affine=True)
        self.conv1 = torch.nn.Conv2d(self.in_channels_prod, out_channels_prod, kernel_size=1, padding=0)
        if temb_channels is not None: self.time_emb_proj = torch.nn.Linear(temb_channels, out_channels_prod)
        else: self.time_emb_proj = None
        self.norm2 = torch.nn.GroupNorm(num_groups=groups_out, num_channels=out_channels_prod, eps=eps, affine=True)
        self.dropout = torch.nn.Dropout(dropout)
        self.conv2 = torch.nn.Conv2d(out_channels_prod, out_channels_prod, kernel_size=1, padding=0)
        self.nonlinearity = nn.SiLU()
        self.use_in_shortcut = self.in_channels_prod != out_channels_prod if use_in_shortcut is None else use_in_shortcut
        self.conv_shortcut = None
        if self.use_in_shortcut: self.conv_shortcut = torch.nn.Conv2d(self.in_channels_prod, out_channels_prod, kernel_size=1, stride=1, padding=0)
    def forward(self, input_tensor, temb):
        shape = input_tensor.shape
        n_dim = len(self.channels_multidim)
        input_tensor = input_tensor.reshape(*shape[0:-n_dim], self.in_channels_prod, 1, 1)
        input_tensor = input_tensor.view(-1, self.in_channels_prod, 1, 1)
        hidden_states = input_tensor
        hidden_states = self.norm1(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.conv1(hidden_states)
        if temb is not None:
            temb = self.time_emb_proj(self.nonlinearity(temb))[:, :, None, None]
            hidden_states = hidden_states + temb
        hidden_states = self.norm2(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.conv2(hidden_states)
        if self.conv_shortcut is not None: input_tensor = self.conv_shortcut(input_tensor)
        output_tensor = input_tensor + hidden_states
        output_tensor = output_tensor.view(*shape[0:-n_dim], -1)
        output_tensor = output_tensor.view(*shape[0:-n_dim], *self.out_channels_multidim)
        return output_tensor
class DownBlockFlat(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default',
    resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, output_scale_factor: float=1.0, add_downsample: bool=True, downsample_padding: int=1):
        super().__init__()
        resnets = []
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(ResnetBlockFlat(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
        self.resnets = nn.ModuleList(resnets)
        if add_downsample: self.downsamplers = nn.ModuleList([LinearMultiDim(out_channels, use_conv=True, out_channels=out_channels, padding=downsample_padding, name='op')])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, ...]]:
        output_states = ()
        for resnet in self.resnets:
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                if is_torch_version('>=', '1.11.0'): hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, use_reentrant=False)
                else: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb)
            else: hidden_states = resnet(hidden_states, temb)
            output_states = output_states + (hidden_states,)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states)
            output_states = output_states + (hidden_states,)
        return (hidden_states, output_states)
class CrossAttnDownBlockFlat(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: Union[int, Tuple[int]]=1,
    resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads: int=1,
    cross_attention_dim: int=1280, output_scale_factor: float=1.0, downsample_padding: int=1, add_downsample: bool=True, dual_cross_attention: bool=False,
    use_linear_projection: bool=False, only_cross_attention: bool=False, upcast_attention: bool=False, attention_type: str='default'):
        super().__init__()
        resnets = []
        attentions = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * num_layers
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(ResnetBlockFlat(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups,
            dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=transformer_layers_per_block[i], cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection,
            only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=1, cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        if add_downsample: self.downsamplers = nn.ModuleList([LinearMultiDim(out_channels, use_conv=True, out_channels=out_channels, padding=downsample_padding, name='op')])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    additional_residuals: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, ...]]:
        output_states = ()
        blocks = list(zip(self.resnets, self.attentions))
        for i, (resnet, attn) in enumerate(blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs,
                attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            else:
                hidden_states = resnet(hidden_states, temb)
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs,
                attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            if i == len(blocks) - 1 and additional_residuals is not None: hidden_states = hidden_states + additional_residuals
            output_states = output_states + (hidden_states,)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states)
            output_states = output_states + (hidden_states,)
        return (hidden_states, output_states)
class UpBlockFlat(nn.Module):
    def __init__(self, in_channels: int, prev_output_channel: int, out_channels: int, temb_channels: int, resolution_idx: Optional[int]=None, dropout: float=0.0,
    num_layers: int=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True,
    output_scale_factor: float=1.0, add_upsample: bool=True):
        super().__init__()
        resnets = []
        for i in range(num_layers):
            res_skip_channels = in_channels if i == num_layers - 1 else out_channels
            resnet_in_channels = prev_output_channel if i == 0 else out_channels
            resnets.append(ResnetBlockFlat(in_channels=resnet_in_channels + res_skip_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps,
            groups=resnet_groups, dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn,
            output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
        self.resnets = nn.ModuleList(resnets)
        if add_upsample: self.upsamplers = nn.ModuleList([LinearMultiDim(out_channels, use_conv=True, out_channels=out_channels)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
        self.resolution_idx = resolution_idx
    def forward(self, hidden_states: torch.Tensor, res_hidden_states_tuple: Tuple[torch.Tensor, ...], temb: Optional[torch.Tensor]=None,
    upsample_size: Optional[int]=None, *args, **kwargs) -> torch.Tensor:
        if len(args) > 0 or kwargs.get('scale', None) is not None:
            deprecation_message = 'The `scale` argument is deprecated and will be ignored. Please remove it, as passing it will raise an error in the future. `scale` should directly be passed while calling the underlying pipeline component i.e., via `cross_attention_kwargs`.'
            deprecate('scale', '1.0.0', deprecation_message)
        is_freeu_enabled = getattr(self, 's1', None) and getattr(self, 's2', None) and getattr(self, 'b1', None) and getattr(self, 'b2', None)
        for resnet in self.resnets:
            res_hidden_states = res_hidden_states_tuple[-1]
            res_hidden_states_tuple = res_hidden_states_tuple[:-1]
            if is_freeu_enabled: hidden_states, res_hidden_states = apply_freeu(self.resolution_idx, hidden_states, res_hidden_states,
            s1=self.s1, s2=self.s2, b1=self.b1, b2=self.b2)
            hidden_states = torch.cat([hidden_states, res_hidden_states], dim=1)
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                if is_torch_version('>=', '1.11.0'): hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, use_reentrant=False)
                else: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb)
            else: hidden_states = resnet(hidden_states, temb)
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states, upsample_size)
        return hidden_states
class CrossAttnUpBlockFlat(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, prev_output_channel: int, temb_channels: int, resolution_idx: Optional[int]=None, dropout: float=0.0,
    num_layers: int=1, transformer_layers_per_block: Union[int, Tuple[int]]=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish',
    resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads: int=1, cross_attention_dim: int=1280, output_scale_factor: float=1.0, add_upsample: bool=True,
    dual_cross_attention: bool=False, use_linear_projection: bool=False, only_cross_attention: bool=False, upcast_attention: bool=False, attention_type: str='default'):
        super().__init__()
        resnets = []
        attentions = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * num_layers
        for i in range(num_layers):
            res_skip_channels = in_channels if i == num_layers - 1 else out_channels
            resnet_in_channels = prev_output_channel if i == 0 else out_channels
            resnets.append(ResnetBlockFlat(in_channels=resnet_in_channels + res_skip_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps,
            groups=resnet_groups, dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=transformer_layers_per_block[i], cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection,
            only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=1, cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        if add_upsample: self.upsamplers = nn.ModuleList([LinearMultiDim(out_channels, use_conv=True, out_channels=out_channels)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
        self.resolution_idx = resolution_idx
    def forward(self, hidden_states: torch.Tensor, res_hidden_states_tuple: Tuple[torch.Tensor, ...], temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, upsample_size: Optional[int]=None, attention_mask: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None) -> torch.Tensor:
        is_freeu_enabled = getattr(self, 's1', None) and getattr(self, 's2', None) and getattr(self, 'b1', None) and getattr(self, 'b2', None)
        for resnet, attn in zip(self.resnets, self.attentions):
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
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs,
                attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
            else:
                hidden_states = resnet(hidden_states, temb)
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, attention_mask=attention_mask,
                encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states, upsample_size)
        return hidden_states
class UNetMidBlockFlat(nn.Module):
    """Returns:"""
    def __init__(self, in_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish',
    resnet_groups: int=32, attn_groups: Optional[int]=None, resnet_pre_norm: bool=True, add_attention: bool=True, attention_head_dim: int=1, output_scale_factor: float=1.0):
        super().__init__()
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        self.add_attention = add_attention
        if attn_groups is None: attn_groups = resnet_groups if resnet_time_scale_shift == 'default' else None
        if resnet_time_scale_shift == 'spatial': resnets = [ResnetBlockCondNorm2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups,
        dropout=dropout, time_embedding_norm='spatial', non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor)]
        else: resnets = [ResnetBlockFlat(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
        time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm)]
        attentions = []
        if attention_head_dim is None: attention_head_dim = in_channels
        for _ in range(num_layers):
            if self.add_attention: attentions.append(Attention(in_channels, heads=in_channels // attention_head_dim, dim_head=attention_head_dim, rescale_output_factor=output_scale_factor,
            eps=resnet_eps, norm_num_groups=attn_groups, spatial_norm_dim=temb_channels if resnet_time_scale_shift == 'spatial' else None, residual_connection=True,
            bias=True, upcast_softmax=True, _from_deprecated_attn_block=True))
            else: attentions.append(None)
            if resnet_time_scale_shift == 'spatial': resnets.append(ResnetBlockCondNorm2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels,
            eps=resnet_eps, groups=resnet_groups, dropout=dropout, time_embedding_norm='spatial', non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor))
            else: resnets.append(ResnetBlockFlat(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups,
            dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None) -> torch.Tensor:
        hidden_states = self.resnets[0](hidden_states, temb)
        for attn, resnet in zip(self.attentions, self.resnets[1:]):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                if attn is not None: hidden_states = attn(hidden_states, temb=temb)
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
            else:
                if attn is not None: hidden_states = attn(hidden_states, temb=temb)
                hidden_states = resnet(hidden_states, temb)
        return hidden_states
class UNetMidBlockFlatCrossAttn(nn.Module):
    def __init__(self, in_channels: int, temb_channels: int, out_channels: Optional[int]=None, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: Union[int, Tuple[int]]=1,
    resnet_eps: float=1e-06, resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_groups_out: Optional[int]=None, resnet_pre_norm: bool=True,
    num_attention_heads: int=1, output_scale_factor: float=1.0, cross_attention_dim: int=1280, dual_cross_attention: bool=False,
    use_linear_projection: bool=False, upcast_attention: bool=False, attention_type: str='default'):
        super().__init__()
        out_channels = out_channels or in_channels
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * num_layers
        resnet_groups_out = resnet_groups_out or resnet_groups
        resnets = [ResnetBlockFlat(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, groups_out=resnet_groups_out,
        dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm)]
        attentions = []
        for i in range(num_layers):
            if not dual_cross_attention: attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=transformer_layers_per_block[i], cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups_out, use_linear_projection=use_linear_projection,
            upcast_attention=upcast_attention, attention_type=attention_type))
            else: attentions.append(DualTransformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=1,
            cross_attention_dim=cross_attention_dim, norm_num_groups=resnet_groups))
            resnets.append(ResnetBlockFlat(in_channels=out_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups_out,
            dropout=dropout, time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None) -> torch.Tensor:
        hidden_states = self.resnets[0](hidden_states, temb)
        for attn, resnet in zip(self.attentions, self.resnets[1:]):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, attention_mask=attention_mask,
                encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(resnet), hidden_states, temb, **ckpt_kwargs)
            else:
                hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, attention_mask=attention_mask,
                encoder_attention_mask=encoder_attention_mask, return_dict=False)[0]
                hidden_states = resnet(hidden_states, temb)
        return hidden_states
class UNetMidBlockFlatSimpleCrossAttn(nn.Module):
    def __init__(self, in_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, resnet_eps: float=1e-06, resnet_time_scale_shift: str='default',
    resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, attention_head_dim: int=1, output_scale_factor: float=1.0, cross_attention_dim: int=1280,
    skip_time_act: bool=False, only_cross_attention: bool=False, cross_attention_norm: Optional[str]=None):
        super().__init__()
        self.has_cross_attention = True
        self.attention_head_dim = attention_head_dim
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        self.num_heads = in_channels // self.attention_head_dim
        resnets = [ResnetBlockFlat(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
        time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm, skip_time_act=skip_time_act)]
        attentions = []
        for _ in range(num_layers):
            processor = AttnAddedKVProcessor2_0() if hasattr(F, 'scaled_dot_product_attention') else AttnAddedKVProcessor()
            attentions.append(Attention(query_dim=in_channels, cross_attention_dim=in_channels, heads=self.num_heads, dim_head=self.attention_head_dim, added_kv_proj_dim=cross_attention_dim,
            norm_num_groups=resnet_groups, bias=True, upcast_softmax=True, only_cross_attention=only_cross_attention, cross_attention_norm=cross_attention_norm, processor=processor))
            resnets.append(ResnetBlockFlat(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm, skip_time_act=skip_time_act))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None) -> torch.Tensor:
        cross_attention_kwargs = cross_attention_kwargs if cross_attention_kwargs is not None else {}
        if attention_mask is None: mask = None if encoder_hidden_states is None else encoder_attention_mask
        else: mask = attention_mask
        hidden_states = self.resnets[0](hidden_states, temb)
        for attn, resnet in zip(self.attentions, self.resnets[1:]):
            hidden_states = attn(hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=mask, **cross_attention_kwargs)
            hidden_states = resnet(hidden_states, temb)
        return hidden_states
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
