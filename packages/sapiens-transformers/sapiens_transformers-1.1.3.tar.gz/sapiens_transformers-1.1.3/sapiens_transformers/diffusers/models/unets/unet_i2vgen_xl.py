'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor, FusedAttnProcessor2_0
from .unet_3d_blocks import CrossAttnDownBlock3D, CrossAttnUpBlock3D, DownBlock3D, UNetMidBlock3DCrossAttn, UpBlock3D, get_down_block, get_up_block
from ..sapiens_transformers.transformer_temporal import TransformerTemporalModel
from ...configuration_utils import ConfigMixin, register_to_config
from ..embeddings import TimestepEmbedding, Timesteps
from typing import Any, Dict, Optional, Tuple, Union
from .unet_3d_condition import UNet3DConditionOutput
from ...loaders import UNet2DConditionLoadersMixin
from ..attention import Attention, FeedForward
from ..activations import get_activation
from ..modeling_utils import ModelMixin
import torch.utils.checkpoint
import torch.nn as nn
import torch
class I2VGenXLTransformerTemporalEncoder(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, activation_fn: str='geglu', upcast_attention: bool=False, ff_inner_dim: Optional[int]=None, dropout: int=0.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=True, eps=1e-05)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=False, upcast_attention=upcast_attention, out_bias=True)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=False, inner_dim=ff_inner_dim, bias=True)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        norm_hidden_states = self.norm1(hidden_states)
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=None)
        hidden_states = attn_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        ff_output = self.ff(hidden_states)
        hidden_states = ff_output + hidden_states
        if hidden_states.ndim == 4: hidden_states = hidden_states.squeeze(1)
        return hidden_states
class I2VGenXLUNet(ModelMixin, ConfigMixin, UNet2DConditionLoadersMixin):
    _supports_gradient_checkpointing = False
    @register_to_config
    def __init__(self, sample_size: Optional[int]=None, in_channels: int=4, out_channels: int=4, down_block_types: Tuple[str, ...]=('CrossAttnDownBlock3D', 'CrossAttnDownBlock3D',
    'CrossAttnDownBlock3D', 'DownBlock3D'), up_block_types: Tuple[str, ...]=('UpBlock3D', 'CrossAttnUpBlock3D', 'CrossAttnUpBlock3D', 'CrossAttnUpBlock3D'),
    block_out_channels: Tuple[int, ...]=(320, 640, 1280, 1280), layers_per_block: int=2, norm_num_groups: Optional[int]=32, cross_attention_dim: int=1024,
    attention_head_dim: Union[int, Tuple[int]]=64, num_attention_heads: Optional[Union[int, Tuple[int]]]=None):
        super().__init__()
        num_attention_heads = attention_head_dim
        if len(down_block_types) != len(up_block_types): raise ValueError(f'Must provide the same number of `down_block_types` as `up_block_types`. `down_block_types`: {down_block_types}. `up_block_types`: {up_block_types}.')
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        self.conv_in = nn.Conv2d(in_channels + in_channels, block_out_channels[0], kernel_size=3, padding=1)
        self.transformer_in = TransformerTemporalModel(num_attention_heads=8, attention_head_dim=num_attention_heads, in_channels=block_out_channels[0], num_layers=1, norm_num_groups=norm_num_groups)
        self.image_latents_proj_in = nn.Sequential(nn.Conv2d(4, in_channels * 4, 3, padding=1), nn.SiLU(), nn.Conv2d(in_channels * 4, in_channels * 4, 3, stride=1, padding=1), nn.SiLU(), nn.Conv2d(in_channels * 4, in_channels, 3, stride=1, padding=1))
        self.image_latents_temporal_encoder = I2VGenXLTransformerTemporalEncoder(dim=in_channels, num_attention_heads=2, ff_inner_dim=in_channels * 4, attention_head_dim=in_channels, activation_fn='gelu')
        self.image_latents_context_embedding = nn.Sequential(nn.Conv2d(4, in_channels * 8, 3, padding=1), nn.SiLU(), nn.AdaptiveAvgPool2d((32, 32)), nn.Conv2d(in_channels * 8, in_channels * 16, 3, stride=2, padding=1), nn.SiLU(), nn.Conv2d(in_channels * 16, cross_attention_dim, 3, stride=2, padding=1))
        time_embed_dim = block_out_channels[0] * 4
        self.time_proj = Timesteps(block_out_channels[0], True, 0)
        timestep_input_dim = block_out_channels[0]
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn='silu')
        self.context_embedding = nn.Sequential(nn.Linear(cross_attention_dim, time_embed_dim), nn.SiLU(), nn.Linear(time_embed_dim, cross_attention_dim * in_channels))
        self.fps_embedding = nn.Sequential(nn.Linear(timestep_input_dim, time_embed_dim), nn.SiLU(), nn.Linear(time_embed_dim, time_embed_dim))
        self.down_blocks = nn.ModuleList([])
        self.up_blocks = nn.ModuleList([])
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        output_channel = block_out_channels[0]
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block, in_channels=input_channel, out_channels=output_channel, temb_channels=time_embed_dim, add_downsample=not is_final_block, resnet_eps=1e-05, resnet_act_fn='silu', resnet_groups=norm_num_groups,
            cross_attention_dim=cross_attention_dim, num_attention_heads=num_attention_heads[i], downsample_padding=1, dual_cross_attention=False)
            self.down_blocks.append(down_block)
        self.mid_block = UNetMidBlock3DCrossAttn(in_channels=block_out_channels[-1], temb_channels=time_embed_dim, resnet_eps=1e-05, resnet_act_fn='silu', output_scale_factor=1, cross_attention_dim=cross_attention_dim,
        num_attention_heads=num_attention_heads[-1], resnet_groups=norm_num_groups, dual_cross_attention=False)
        self.num_upsamplers = 0
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
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
            up_block = get_up_block(up_block_type, num_layers=layers_per_block + 1, in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel, temb_channels=time_embed_dim, add_upsample=add_upsample, resnet_eps=1e-05,
            resnet_act_fn='silu', resnet_groups=norm_num_groups, cross_attention_dim=cross_attention_dim, num_attention_heads=reversed_num_attention_heads[i], dual_cross_attention=False, resolution_idx=i)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=1e-05)
        self.conv_act = get_activation('silu')
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, kernel_size=3, padding=1)
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
    def disable_forward_chunking(self):
        def fn_recursive_feed_forward(module: torch.nn.Module, chunk_size: int, dim: int):
            if hasattr(module, 'set_chunk_feed_forward'): module.set_chunk_feed_forward(chunk_size=chunk_size, dim=dim)
            for child in module.children(): fn_recursive_feed_forward(child, chunk_size, dim)
        for module in self.children(): fn_recursive_feed_forward(module, None, 0)
    def set_default_attn_processor(self):
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    def _set_gradient_checkpointing(self, module, value: bool=False) -> None:
        if isinstance(module, (CrossAttnDownBlock3D, DownBlock3D, CrossAttnUpBlock3D, UpBlock3D)): module.gradient_checkpointing = value
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
        self.set_attn_processor(FusedAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], fps: torch.Tensor, image_latents: torch.Tensor, image_embeddings: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    timestep_cond: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True) -> Union[UNet3DConditionOutput, Tuple[torch.Tensor]]:
        """Returns:"""
        batch_size, channels, num_frames, height, width = sample.shape
        default_overall_up_factor = 2 ** self.num_upsamplers
        forward_upsample_size = False
        upsample_size = None
        if any((s % default_overall_up_factor != 0 for s in sample.shape[-2:])): forward_upsample_size = True
        timesteps = timestep
        if not torch.is_tensor(timesteps):
            is_mps = sample.device.type == 'mps'
            if isinstance(timesteps, float): dtype = torch.float32 if is_mps else torch.float64
            else: dtype = torch.int32 if is_mps else torch.int64
            timesteps = torch.tensor([timesteps], dtype=dtype, device=sample.device)
        elif len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        timesteps = timesteps.expand(sample.shape[0])
        t_emb = self.time_proj(timesteps)
        t_emb = t_emb.to(dtype=self.dtype)
        t_emb = self.time_embedding(t_emb, timestep_cond)
        fps = fps.expand(fps.shape[0])
        fps_emb = self.fps_embedding(self.time_proj(fps).to(dtype=self.dtype))
        emb = t_emb + fps_emb
        emb = emb.repeat_interleave(repeats=num_frames, dim=0)
        context_emb = sample.new_zeros(batch_size, 0, self.config.cross_attention_dim)
        context_emb = torch.cat([context_emb, encoder_hidden_states], dim=1)
        image_latents_for_context_embds = image_latents[:, :, :1, :]
        image_latents_context_embs = image_latents_for_context_embds.permute(0, 2, 1, 3, 4).reshape(image_latents_for_context_embds.shape[0] * image_latents_for_context_embds.shape[2], image_latents_for_context_embds.shape[1],
        image_latents_for_context_embds.shape[3], image_latents_for_context_embds.shape[4])
        image_latents_context_embs = self.image_latents_context_embedding(image_latents_context_embs)
        _batch_size, _channels, _height, _width = image_latents_context_embs.shape
        image_latents_context_embs = image_latents_context_embs.permute(0, 2, 3, 1).reshape(_batch_size, _height * _width, _channels)
        context_emb = torch.cat([context_emb, image_latents_context_embs], dim=1)
        image_emb = self.context_embedding(image_embeddings)
        image_emb = image_emb.view(-1, self.config.in_channels, self.config.cross_attention_dim)
        context_emb = torch.cat([context_emb, image_emb], dim=1)
        context_emb = context_emb.repeat_interleave(repeats=num_frames, dim=0)
        image_latents = image_latents.permute(0, 2, 1, 3, 4).reshape(image_latents.shape[0] * image_latents.shape[2], image_latents.shape[1], image_latents.shape[3], image_latents.shape[4])
        image_latents = self.image_latents_proj_in(image_latents)
        image_latents = image_latents[None, :].reshape(batch_size, num_frames, channels, height, width).permute(0, 3, 4, 1, 2).reshape(batch_size * height * width, num_frames, channels)
        image_latents = self.image_latents_temporal_encoder(image_latents)
        image_latents = image_latents.reshape(batch_size, height, width, num_frames, channels).permute(0, 4, 3, 1, 2)
        sample = torch.cat([sample, image_latents], dim=1)
        sample = sample.permute(0, 2, 1, 3, 4).reshape((sample.shape[0] * num_frames, -1) + sample.shape[3:])
        sample = self.conv_in(sample)
        sample = self.transformer_in(sample, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs, return_dict=False)[0]
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, encoder_hidden_states=context_emb,
            num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, num_frames=num_frames)
            down_block_res_samples += res_samples
        if self.mid_block is not None: sample = self.mid_block(sample, emb, encoder_hidden_states=context_emb, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
        for i, upsample_block in enumerate(self.up_blocks):
            is_final_block = i == len(self.up_blocks) - 1
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if not is_final_block and forward_upsample_size: upsample_size = down_block_res_samples[-1].shape[2:]
            if hasattr(upsample_block, 'has_cross_attention') and upsample_block.has_cross_attention: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples,
            encoder_hidden_states=context_emb, upsample_size=upsample_size, num_frames=num_frames, cross_attention_kwargs=cross_attention_kwargs)
            else: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples, upsample_size=upsample_size, num_frames=num_frames)
        sample = self.conv_norm_out(sample)
        sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        sample = sample[None, :].reshape((-1, num_frames) + sample.shape[1:]).permute(0, 2, 1, 3, 4)
        if not return_dict: return (sample,)
        return UNet3DConditionOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
