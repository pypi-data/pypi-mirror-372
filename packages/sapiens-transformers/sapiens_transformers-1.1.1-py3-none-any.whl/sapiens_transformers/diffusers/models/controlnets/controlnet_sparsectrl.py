'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from ..unets.unet_motion_model import CrossAttnDownBlockMotion, DownBlockMotion
from ...configuration_utils import ConfigMixin, register_to_config
from ..unets.unet_2d_blocks import UNetMidBlock2DCrossAttn
from ..unets.unet_2d_condition import UNet2DConditionModel
from typing import Any, Dict, List, Optional, Tuple, Union
from ..embeddings import TimestepEmbedding, Timesteps
from ...loaders import FromOriginalModelMixin
from ...utils import BaseOutput
from ..modeling_utils import ModelMixin
from torch.nn import functional as F
from dataclasses import dataclass
from torch import nn
import torch
@dataclass
class SparseControlNetOutput(BaseOutput):
    """Args:"""
    down_block_res_samples: Tuple[torch.Tensor]
    mid_block_res_sample: torch.Tensor
class SparseControlNetConditioningEmbedding(nn.Module):
    def __init__(self, conditioning_embedding_channels: int, conditioning_channels: int=3, block_out_channels: Tuple[int, ...]=(16, 32, 96, 256)):
        super().__init__()
        self.conv_in = nn.Conv2d(conditioning_channels, block_out_channels[0], kernel_size=3, padding=1)
        self.blocks = nn.ModuleList([])
        for i in range(len(block_out_channels) - 1):
            channel_in = block_out_channels[i]
            channel_out = block_out_channels[i + 1]
            self.blocks.append(nn.Conv2d(channel_in, channel_in, kernel_size=3, padding=1))
            self.blocks.append(nn.Conv2d(channel_in, channel_out, kernel_size=3, padding=1, stride=2))
        self.conv_out = zero_module(nn.Conv2d(block_out_channels[-1], conditioning_embedding_channels, kernel_size=3, padding=1))
    def forward(self, conditioning: torch.Tensor) -> torch.Tensor:
        embedding = self.conv_in(conditioning)
        embedding = F.silu(embedding)
        for block in self.blocks:
            embedding = block(embedding)
            embedding = F.silu(embedding)
        embedding = self.conv_out(embedding)
        return embedding
class SparseControlNetModel(ModelMixin, ConfigMixin, FromOriginalModelMixin):
    """Args:"""
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, in_channels: int=4, conditioning_channels: int=4, flip_sin_to_cos: bool=True, freq_shift: int=0, down_block_types: Tuple[str, ...]=('CrossAttnDownBlockMotion',
    'CrossAttnDownBlockMotion', 'CrossAttnDownBlockMotion', 'DownBlockMotion'), only_cross_attention: Union[bool, Tuple[bool]]=False, block_out_channels: Tuple[int, ...]=(320, 640, 1280, 1280),
    layers_per_block: int=2, downsample_padding: int=1, mid_block_scale_factor: float=1, act_fn: str='silu', norm_num_groups: Optional[int]=32, norm_eps: float=1e-05, cross_attention_dim: int=768,
    transformer_layers_per_block: Union[int, Tuple[int, ...]]=1, transformer_layers_per_mid_block: Optional[Union[int, Tuple[int]]]=None, temporal_transformer_layers_per_block: Union[int, Tuple[int, ...]]=1,
    attention_head_dim: Union[int, Tuple[int, ...]]=8, num_attention_heads: Optional[Union[int, Tuple[int, ...]]]=None, use_linear_projection: bool=False, upcast_attention: bool=False,
    resnet_time_scale_shift: str='default', conditioning_embedding_out_channels: Optional[Tuple[int, ...]]=(16, 32, 96, 256), global_pool_conditions: bool=False, controlnet_conditioning_channel_order: str='rgb',
    motion_max_seq_length: int=32, motion_num_attention_heads: int=8, concat_conditioning_mask: bool=True, use_simplified_condition_embedding: bool=True):
        super().__init__()
        self.use_simplified_condition_embedding = use_simplified_condition_embedding
        num_attention_heads = num_attention_heads or attention_head_dim
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(only_cross_attention, bool) and len(only_cross_attention) != len(down_block_types): raise ValueError(f'Must provide the same number of `only_cross_attention` as `down_block_types`. `only_cross_attention`: {only_cross_attention}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(down_block_types)
        if isinstance(temporal_transformer_layers_per_block, int): temporal_transformer_layers_per_block = [temporal_transformer_layers_per_block] * len(down_block_types)
        conv_in_kernel = 3
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        if concat_conditioning_mask: conditioning_channels = conditioning_channels + 1
        self.concat_conditioning_mask = concat_conditioning_mask
        if use_simplified_condition_embedding: self.controlnet_cond_embedding = zero_module(nn.Conv2d(conditioning_channels, block_out_channels[0], kernel_size=3, padding=1))
        else: self.controlnet_cond_embedding = SparseControlNetConditioningEmbedding(conditioning_embedding_channels=block_out_channels[0],
        block_out_channels=conditioning_embedding_out_channels, conditioning_channels=conditioning_channels)
        time_embed_dim = block_out_channels[0] * 4
        self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
        timestep_input_dim = block_out_channels[0]
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn)
        self.down_blocks = nn.ModuleList([])
        self.controlnet_down_blocks = nn.ModuleList([])
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,) * len(down_block_types)
        if isinstance(only_cross_attention, bool): only_cross_attention = [only_cross_attention] * len(down_block_types)
        if isinstance(attention_head_dim, int): attention_head_dim = (attention_head_dim,) * len(down_block_types)
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        if isinstance(motion_num_attention_heads, int): motion_num_attention_heads = (motion_num_attention_heads,) * len(down_block_types)
        output_channel = block_out_channels[0]
        controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
        controlnet_block = zero_module(controlnet_block)
        self.controlnet_down_blocks.append(controlnet_block)
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            if down_block_type == 'CrossAttnDownBlockMotion': down_block = CrossAttnDownBlockMotion(in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, dropout=0, num_layers=layers_per_block,
            transformer_layers_per_block=transformer_layers_per_block[i], resnet_eps=norm_eps, resnet_time_scale_shift=resnet_time_scale_shift, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, resnet_pre_norm=True,
            num_attention_heads=num_attention_heads[i], cross_attention_dim=cross_attention_dim[i], add_downsample=not is_final_block, dual_cross_attention=False, use_linear_projection=use_linear_projection,
            only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, temporal_num_attention_heads=motion_num_attention_heads[i], temporal_max_seq_length=motion_max_seq_length,
            temporal_transformer_layers_per_block=temporal_transformer_layers_per_block[i], temporal_double_self_attention=False)
            elif down_block_type == 'DownBlockMotion': down_block = DownBlockMotion(in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, dropout=0, num_layers=layers_per_block,
            resnet_eps=norm_eps, resnet_time_scale_shift=resnet_time_scale_shift, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, resnet_pre_norm=True, add_downsample=not is_final_block,
            temporal_num_attention_heads=motion_num_attention_heads[i], temporal_max_seq_length=motion_max_seq_length, temporal_transformer_layers_per_block=temporal_transformer_layers_per_block[i], temporal_double_self_attention=False)
            else: raise ValueError('Invalid `block_type` encountered. Must be one of `CrossAttnDownBlockMotion` or `DownBlockMotion`')
            self.down_blocks.append(down_block)
            for _ in range(layers_per_block):
                controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
                controlnet_block = zero_module(controlnet_block)
                self.controlnet_down_blocks.append(controlnet_block)
            if not is_final_block:
                controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
                controlnet_block = zero_module(controlnet_block)
                self.controlnet_down_blocks.append(controlnet_block)
        mid_block_channels = block_out_channels[-1]
        controlnet_block = nn.Conv2d(mid_block_channels, mid_block_channels, kernel_size=1)
        controlnet_block = zero_module(controlnet_block)
        self.controlnet_mid_block = controlnet_block
        if transformer_layers_per_mid_block is None: transformer_layers_per_mid_block = transformer_layers_per_block[-1] if isinstance(transformer_layers_per_block[-1], int) else 1
        self.mid_block = UNetMidBlock2DCrossAttn(in_channels=mid_block_channels, temb_channels=time_embed_dim, dropout=0, num_layers=1, transformer_layers_per_block=transformer_layers_per_mid_block, resnet_eps=norm_eps,
        resnet_time_scale_shift=resnet_time_scale_shift, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, resnet_pre_norm=True, num_attention_heads=num_attention_heads[-1], output_scale_factor=mid_block_scale_factor,
        cross_attention_dim=cross_attention_dim[-1], dual_cross_attention=False, use_linear_projection=use_linear_projection, upcast_attention=upcast_attention, attention_type='default')
    @classmethod
    def from_unet(cls, unet: UNet2DConditionModel, controlnet_conditioning_channel_order: str='rgb', conditioning_embedding_out_channels: Optional[Tuple[int, ...]]=(16, 32, 96, 256),
    load_weights_from_unet: bool=True, conditioning_channels: int=3) -> 'SparseControlNetModel':
        transformer_layers_per_block = unet.config.transformer_layers_per_block if 'transformer_layers_per_block' in unet.config else 1
        down_block_types = unet.config.down_block_types
        for i in range(len(down_block_types)):
            if 'CrossAttn' in down_block_types[i]: down_block_types[i] = 'CrossAttnDownBlockMotion'
            elif 'Down' in down_block_types[i]: down_block_types[i] = 'DownBlockMotion'
            else: raise ValueError('Invalid `block_type` encountered. Must be a cross-attention or down block')
        controlnet = cls(in_channels=unet.config.in_channels, conditioning_channels=conditioning_channels, flip_sin_to_cos=unet.config.flip_sin_to_cos, freq_shift=unet.config.freq_shift, down_block_types=unet.config.down_block_types,
        only_cross_attention=unet.config.only_cross_attention, block_out_channels=unet.config.block_out_channels, layers_per_block=unet.config.layers_per_block, downsample_padding=unet.config.downsample_padding,
        mid_block_scale_factor=unet.config.mid_block_scale_factor, act_fn=unet.config.act_fn, norm_num_groups=unet.config.norm_num_groups, norm_eps=unet.config.norm_eps, cross_attention_dim=unet.config.cross_attention_dim,
        transformer_layers_per_block=transformer_layers_per_block, attention_head_dim=unet.config.attention_head_dim, num_attention_heads=unet.config.num_attention_heads, use_linear_projection=unet.config.use_linear_projection,
        upcast_attention=unet.config.upcast_attention, resnet_time_scale_shift=unet.config.resnet_time_scale_shift, conditioning_embedding_out_channels=conditioning_embedding_out_channels, controlnet_conditioning_channel_order=controlnet_conditioning_channel_order)
        if load_weights_from_unet:
            controlnet.conv_in.load_state_dict(unet.conv_in.state_dict(), strict=False)
            controlnet.time_proj.load_state_dict(unet.time_proj.state_dict(), strict=False)
            controlnet.time_embedding.load_state_dict(unet.time_embedding.state_dict(), strict=False)
            controlnet.down_blocks.load_state_dict(unet.down_blocks.state_dict(), strict=False)
            controlnet.mid_block.load_state_dict(unet.mid_block.state_dict(), strict=False)
        return controlnet
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
    def set_attention_slice(self, slice_size: Union[str, int, List[int]]) -> None:
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
    def _set_gradient_checkpointing(self, module, value: bool=False) -> None:
        if isinstance(module, (CrossAttnDownBlockMotion, DownBlockMotion, UNetMidBlock2DCrossAttn)): module.gradient_checkpointing = value
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, controlnet_cond: torch.Tensor, conditioning_scale: float=1.0, timestep_cond: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, conditioning_mask: Optional[torch.Tensor]=None, guess_mode: bool=False,
    return_dict: bool=True) -> Union[SparseControlNetOutput, Tuple[Tuple[torch.Tensor, ...], torch.Tensor]]:
        """Returns:"""
        sample_batch_size, sample_channels, sample_num_frames, sample_height, sample_width = sample.shape
        sample = torch.zeros_like(sample)
        channel_order = self.config.controlnet_conditioning_channel_order
        if channel_order == 'rgb': ...
        elif channel_order == 'bgr': controlnet_cond = torch.flip(controlnet_cond, dims=[1])
        else: raise ValueError(f'unknown `controlnet_conditioning_channel_order`: {channel_order}')
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
        timesteps = timesteps.expand(sample.shape[0])
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=sample.dtype)
        emb = self.time_embedding(t_emb, timestep_cond)
        emb = emb.repeat_interleave(sample_num_frames, dim=0)
        batch_size, channels, num_frames, height, width = sample.shape
        sample = sample.permute(0, 2, 1, 3, 4).reshape(batch_size * num_frames, channels, height, width)
        sample = self.conv_in(sample)
        batch_frames, channels, height, width = sample.shape
        sample = sample[:, None].reshape(sample_batch_size, sample_num_frames, channels, height, width)
        if self.concat_conditioning_mask: controlnet_cond = torch.cat([controlnet_cond, conditioning_mask], dim=1)
        batch_size, channels, num_frames, height, width = controlnet_cond.shape
        controlnet_cond = controlnet_cond.permute(0, 2, 1, 3, 4).reshape(batch_size * num_frames, channels, height, width)
        controlnet_cond = self.controlnet_cond_embedding(controlnet_cond)
        batch_frames, channels, height, width = controlnet_cond.shape
        controlnet_cond = controlnet_cond[:, None].reshape(batch_size, num_frames, channels, height, width)
        sample = sample + controlnet_cond
        batch_size, num_frames, channels, height, width = sample.shape
        sample = sample.reshape(sample_batch_size * sample_num_frames, channels, height, width)
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, encoder_hidden_states=encoder_hidden_states,
            attention_mask=attention_mask, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, num_frames=num_frames)
            down_block_res_samples += res_samples
        if self.mid_block is not None:
            if hasattr(self.mid_block, 'has_cross_attention') and self.mid_block.has_cross_attention: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states,
            attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs)
            else: sample = self.mid_block(sample, emb)
        controlnet_down_block_res_samples = ()
        for down_block_res_sample, controlnet_block in zip(down_block_res_samples, self.controlnet_down_blocks):
            down_block_res_sample = controlnet_block(down_block_res_sample)
            controlnet_down_block_res_samples = controlnet_down_block_res_samples + (down_block_res_sample,)
        down_block_res_samples = controlnet_down_block_res_samples
        mid_block_res_sample = self.controlnet_mid_block(sample)
        if guess_mode and (not self.config.global_pool_conditions):
            scales = torch.logspace(-1, 0, len(down_block_res_samples) + 1, device=sample.device)
            scales = scales * conditioning_scale
            down_block_res_samples = [sample * scale for sample, scale in zip(down_block_res_samples, scales)]
            mid_block_res_sample = mid_block_res_sample * scales[-1]
        else:
            down_block_res_samples = [sample * conditioning_scale for sample in down_block_res_samples]
            mid_block_res_sample = mid_block_res_sample * conditioning_scale
        if self.config.global_pool_conditions:
            down_block_res_samples = [torch.mean(sample, dim=(2, 3), keepdim=True) for sample in down_block_res_samples]
            mid_block_res_sample = torch.mean(mid_block_res_sample, dim=(2, 3), keepdim=True)
        if not return_dict: return (down_block_res_samples, mid_block_res_sample)
        return SparseControlNetOutput(down_block_res_samples=down_block_res_samples, mid_block_res_sample=mid_block_res_sample)
def zero_module(module: nn.Module) -> nn.Module:
    for p in module.parameters(): nn.init.zeros_(p)
    return module
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
