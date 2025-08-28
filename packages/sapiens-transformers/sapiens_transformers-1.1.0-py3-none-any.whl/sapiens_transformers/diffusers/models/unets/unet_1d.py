'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .unet_1d_blocks import get_down_block, get_mid_block, get_out_block, get_up_block
from ..embeddings import GaussianFourierProjection, TimestepEmbedding, Timesteps
from ...configuration_utils import ConfigMixin, register_to_config
from typing import Optional, Tuple, Union
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
from ...utils import BaseOutput
import torch.nn as nn
import torch
@dataclass
class UNet1DOutput(BaseOutput):
    """Args:"""
    sample: torch.Tensor
class UNet1DModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, sample_size: int=65536, sample_rate: Optional[int]=None, in_channels: int=2, out_channels: int=2, extra_in_channels: int=0, time_embedding_type: str='fourier',
    flip_sin_to_cos: bool=True, use_timestep_embedding: bool=False, freq_shift: float=0.0, down_block_types: Tuple[str]=('DownBlock1DNoSkip', 'DownBlock1D', 'AttnDownBlock1D'),
    up_block_types: Tuple[str]=('AttnUpBlock1D', 'UpBlock1D', 'UpBlock1DNoSkip'), mid_block_type: Tuple[str]='UNetMidBlock1D', out_block_type: str=None,
    block_out_channels: Tuple[int]=(32, 32, 64), act_fn: str=None, norm_num_groups: int=8, layers_per_block: int=1, downsample_each_block: bool=False):
        super().__init__()
        self.sample_size = sample_size
        if time_embedding_type == 'fourier':
            self.time_proj = GaussianFourierProjection(embedding_size=8, set_W_to_weight=False, log=False, flip_sin_to_cos=flip_sin_to_cos)
            timestep_input_dim = 2 * block_out_channels[0]
        elif time_embedding_type == 'positional':
            self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos=flip_sin_to_cos, downscale_freq_shift=freq_shift)
            timestep_input_dim = block_out_channels[0]
        if use_timestep_embedding:
            time_embed_dim = block_out_channels[0] * 4
            self.time_mlp = TimestepEmbedding(in_channels=timestep_input_dim, time_embed_dim=time_embed_dim, act_fn=act_fn, out_dim=block_out_channels[0])
        self.down_blocks = nn.ModuleList([])
        self.mid_block = None
        self.up_blocks = nn.ModuleList([])
        self.out_block = None
        output_channel = in_channels
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            if i == 0: input_channel += extra_in_channels
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block, in_channels=input_channel, out_channels=output_channel, temb_channels=block_out_channels[0],
            add_downsample=not is_final_block or downsample_each_block)
            self.down_blocks.append(down_block)
        self.mid_block = get_mid_block(mid_block_type, in_channels=block_out_channels[-1], mid_channels=block_out_channels[-1], out_channels=block_out_channels[-1],
        embed_dim=block_out_channels[0], num_layers=layers_per_block, add_downsample=downsample_each_block)
        reversed_block_out_channels = list(reversed(block_out_channels))
        output_channel = reversed_block_out_channels[0]
        if out_block_type is None: final_upsample_channels = out_channels
        else: final_upsample_channels = block_out_channels[0]
        for i, up_block_type in enumerate(up_block_types):
            prev_output_channel = output_channel
            output_channel = reversed_block_out_channels[i + 1] if i < len(up_block_types) - 1 else final_upsample_channels
            is_final_block = i == len(block_out_channels) - 1
            up_block = get_up_block(up_block_type, num_layers=layers_per_block, in_channels=prev_output_channel, out_channels=output_channel,
            temb_channels=block_out_channels[0], add_upsample=not is_final_block)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        num_groups_out = norm_num_groups if norm_num_groups is not None else min(block_out_channels[0] // 4, 32)
        self.out_block = get_out_block(out_block_type=out_block_type, num_groups_out=num_groups_out, embed_dim=block_out_channels[0],
        out_channels=out_channels, act_fn=act_fn, fc_dim=block_out_channels[-1] // 4)
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], return_dict: bool=True) -> Union[UNet1DOutput, Tuple]:
        """Returns:"""
        timesteps = timestep
        if not torch.is_tensor(timesteps): timesteps = torch.tensor([timesteps], dtype=torch.long, device=sample.device)
        elif torch.is_tensor(timesteps) and len(timesteps.shape) == 0: timesteps = timesteps[None].to(sample.device)
        timestep_embed = self.time_proj(timesteps)
        if self.config.use_timestep_embedding: timestep_embed = self.time_mlp(timestep_embed)
        else:
            timestep_embed = timestep_embed[..., None]
            timestep_embed = timestep_embed.repeat([1, 1, sample.shape[2]]).to(sample.dtype)
            timestep_embed = timestep_embed.broadcast_to(sample.shape[:1] + timestep_embed.shape[1:])
        down_block_res_samples = ()
        for downsample_block in self.down_blocks:
            sample, res_samples = downsample_block(hidden_states=sample, temb=timestep_embed)
            down_block_res_samples += res_samples
        if self.mid_block: sample = self.mid_block(sample, timestep_embed)
        for i, upsample_block in enumerate(self.up_blocks):
            res_samples = down_block_res_samples[-1:]
            down_block_res_samples = down_block_res_samples[:-1]
            sample = upsample_block(sample, res_hidden_states_tuple=res_samples, temb=timestep_embed)
        if self.out_block: sample = self.out_block(sample, timestep_embed)
        if not return_dict: return (sample,)
        return UNet1DOutput(sample=sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
