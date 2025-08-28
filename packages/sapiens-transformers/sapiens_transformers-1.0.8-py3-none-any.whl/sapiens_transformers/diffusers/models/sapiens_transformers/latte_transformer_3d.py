'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.embeddings import PixArtAlphaTextProjection, get_1d_sincos_pos_embed_from_grid
from ...configuration_utils import ConfigMixin, register_to_config
from ..modeling_outputs import Transformer2DModelOutput
from ..normalization import AdaLayerNormSingle
from ..attention import BasicTransformerBlock
from ..modeling_utils import ModelMixin
from ..embeddings import PatchEmbed
from typing import Optional
from torch import nn
import torch
class LatteTransformer3DModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, out_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0,
    cross_attention_dim: Optional[int]=None, attention_bias: bool=False, sample_size: int=64, patch_size: Optional[int]=None, activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None,
    norm_type: str='layer_norm', norm_elementwise_affine: bool=True, norm_eps: float=1e-05, caption_channels: int=None, video_length: int=16):
        super().__init__()
        inner_dim = num_attention_heads * attention_head_dim
        self.height = sample_size
        self.width = sample_size
        interpolation_scale = self.config.sample_size // 64
        interpolation_scale = max(interpolation_scale, 1)
        self.pos_embed = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels, embed_dim=inner_dim, interpolation_scale=interpolation_scale)
        self.transformer_blocks = nn.ModuleList([BasicTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, attention_bias=attention_bias, norm_type=norm_type,
        norm_elementwise_affine=norm_elementwise_affine, norm_eps=norm_eps) for d in range(num_layers)])
        self.temporal_transformer_blocks = nn.ModuleList([BasicTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=None,
        activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, attention_bias=attention_bias, norm_type=norm_type,
        norm_elementwise_affine=norm_elementwise_affine, norm_eps=norm_eps) for d in range(num_layers)])
        self.out_channels = in_channels if out_channels is None else out_channels
        self.norm_out = nn.LayerNorm(inner_dim, elementwise_affine=False, eps=1e-06)
        self.scale_shift_table = nn.Parameter(torch.randn(2, inner_dim) / inner_dim ** 0.5)
        self.proj_out = nn.Linear(inner_dim, patch_size * patch_size * self.out_channels)
        self.adaln_single = AdaLayerNormSingle(inner_dim, use_additional_conditions=False)
        self.caption_projection = PixArtAlphaTextProjection(in_features=caption_channels, hidden_size=inner_dim)
        temp_pos_embed = get_1d_sincos_pos_embed_from_grid(inner_dim, torch.arange(0, video_length).unsqueeze(1), output_type='pt')
        self.register_buffer('temp_pos_embed', temp_pos_embed.float().unsqueeze(0), persistent=False)
        self.gradient_checkpointing = False
    def _set_gradient_checkpointing(self, module, value=False): self.gradient_checkpointing = value
    def forward(self, hidden_states: torch.Tensor, timestep: Optional[torch.LongTensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, enable_temporal_attentions: bool=True, return_dict: bool=True):
        """Returns:"""
        batch_size, channels, num_frame, height, width = hidden_states.shape
        hidden_states = hidden_states.permute(0, 2, 1, 3, 4).reshape(-1, channels, height, width)
        height, width = (hidden_states.shape[-2] // self.config.patch_size, hidden_states.shape[-1] // self.config.patch_size)
        num_patches = height * width
        hidden_states = self.pos_embed(hidden_states)
        added_cond_kwargs = {'resolution': None, 'aspect_ratio': None}
        timestep, embedded_timestep = self.adaln_single(timestep, added_cond_kwargs=added_cond_kwargs, batch_size=batch_size, hidden_dtype=hidden_states.dtype)
        encoder_hidden_states = self.caption_projection(encoder_hidden_states)
        encoder_hidden_states_spatial = encoder_hidden_states.repeat_interleave(num_frame, dim=0).view(-1, encoder_hidden_states.shape[-2], encoder_hidden_states.shape[-1])
        timestep_spatial = timestep.repeat_interleave(num_frame, dim=0).view(-1, timestep.shape[-1])
        timestep_temp = timestep.repeat_interleave(num_patches, dim=0).view(-1, timestep.shape[-1])
        for i, (spatial_block, temp_block) in enumerate(zip(self.transformer_blocks, self.temporal_transformer_blocks)):
            if torch.is_grad_enabled() and self.gradient_checkpointing: hidden_states = torch.utils.checkpoint.checkpoint(spatial_block, hidden_states, None, encoder_hidden_states_spatial, encoder_attention_mask,
            timestep_spatial, None, None, use_reentrant=False)
            else: hidden_states = spatial_block(hidden_states, None, encoder_hidden_states_spatial, encoder_attention_mask, timestep_spatial, None, None)
            if enable_temporal_attentions:
                hidden_states = hidden_states.reshape(batch_size, -1, hidden_states.shape[-2], hidden_states.shape[-1]).permute(0, 2, 1, 3)
                hidden_states = hidden_states.reshape(-1, hidden_states.shape[-2], hidden_states.shape[-1])
                if i == 0 and num_frame > 1: hidden_states = hidden_states + self.temp_pos_embed
                if torch.is_grad_enabled() and self.gradient_checkpointing: hidden_states = torch.utils.checkpoint.checkpoint(temp_block, hidden_states,
                None, None, None, timestep_temp, None, None, use_reentrant=False)
                else: hidden_states = temp_block(hidden_states, None, None, None, timestep_temp, None, None)
                hidden_states = hidden_states.reshape(batch_size, -1, hidden_states.shape[-2], hidden_states.shape[-1]).permute(0, 2, 1, 3)
                hidden_states = hidden_states.reshape(-1, hidden_states.shape[-2], hidden_states.shape[-1])
        embedded_timestep = embedded_timestep.repeat_interleave(num_frame, dim=0).view(-1, embedded_timestep.shape[-1])
        shift, scale = (self.scale_shift_table[None] + embedded_timestep[:, None]).chunk(2, dim=1)
        hidden_states = self.norm_out(hidden_states)
        hidden_states = hidden_states * (1 + scale) + shift
        hidden_states = self.proj_out(hidden_states)
        if self.adaln_single is None: height = width = int(hidden_states.shape[1] ** 0.5)
        hidden_states = hidden_states.reshape(shape=(-1, height, width, self.config.patch_size, self.config.patch_size, self.out_channels))
        hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(-1, self.out_channels, height * self.config.patch_size, width * self.config.patch_size))
        output = output.reshape(batch_size, -1, output.shape[-3], output.shape[-2], output.shape[-1]).permute(0, 2, 1, 3, 4)
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
