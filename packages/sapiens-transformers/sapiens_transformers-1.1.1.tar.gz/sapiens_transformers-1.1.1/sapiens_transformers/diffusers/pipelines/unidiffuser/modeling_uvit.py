'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import Optional, Union
import torch
from torch import nn
from ...configuration_utils import ConfigMixin, register_to_config
from ...models import ModelMixin
from ...models.attention import FeedForward
from ...models.attention_processor import Attention
from ...models.embeddings import TimestepEmbedding, Timesteps, get_2d_sincos_pos_embed
from ...models.modeling_outputs import Transformer2DModelOutput
from ...models.normalization import AdaLayerNorm
def _no_grad_trunc_normal_(tensor, mean, std, a, b):
    def norm_cdf(x): return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    with torch.no_grad():
        l = norm_cdf((a - mean) / std)
        u = norm_cdf((b - mean) / std)
        tensor.uniform_(2 * l - 1, 2 * u - 1)
        tensor.erfinv_()
        tensor.mul_(std * math.sqrt(2.0))
        tensor.add_(mean)
        tensor.clamp_(min=a, max=b)
        return tensor
def trunc_normal_(tensor, mean=0.0, std=1.0, a=-2.0, b=2.0):
    """Examples:"""
    return _no_grad_trunc_normal_(tensor, mean, std, a, b)
class PatchEmbed(nn.Module):
    def __init__(self, height=224, width=224, patch_size=16, in_channels=3, embed_dim=768, layer_norm=False, flatten=True, bias=True, use_pos_embed=True):
        super().__init__()
        num_patches = height // patch_size * (width // patch_size)
        self.flatten = flatten
        self.layer_norm = layer_norm
        self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=(patch_size, patch_size), stride=patch_size, bias=bias)
        if layer_norm: self.norm = nn.LayerNorm(embed_dim, elementwise_affine=False, eps=1e-06)
        else: self.norm = None
        self.use_pos_embed = use_pos_embed
        if self.use_pos_embed:
            pos_embed = get_2d_sincos_pos_embed(embed_dim, int(num_patches ** 0.5), output_type='pt')
            self.register_buffer('pos_embed', pos_embed.float().unsqueeze(0), persistent=False)
    def forward(self, latent):
        latent = self.proj(latent)
        if self.flatten: latent = latent.flatten(2).transpose(1, 2)
        if self.layer_norm: latent = self.norm(latent)
        if self.use_pos_embed: return latent + self.pos_embed
        else: return latent
class SkipBlock(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.skip_linear = nn.Linear(2 * dim, dim)
        self.norm = nn.LayerNorm(dim)
    def forward(self, x, skip):
        x = self.skip_linear(torch.cat([x, skip], dim=-1))
        x = self.norm(x)
        return x
class UTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, dropout=0.0, cross_attention_dim: Optional[int]=None, activation_fn: str='geglu',
    num_embeds_ada_norm: Optional[int]=None, attention_bias: bool=False, only_cross_attention: bool=False, double_self_attention: bool=False, upcast_attention: bool=False,
    norm_elementwise_affine: bool=True, norm_type: str='layer_norm', pre_layer_norm: bool=True, final_dropout: bool=False):
        super().__init__()
        self.only_cross_attention = only_cross_attention
        self.use_ada_layer_norm = num_embeds_ada_norm is not None and norm_type == 'ada_norm'
        self.pre_layer_norm = pre_layer_norm
        if norm_type in ('ada_norm', 'ada_norm_zero') and num_embeds_ada_norm is None: raise ValueError(f'`norm_type` is set to {norm_type}, but `num_embeds_ada_norm` is not defined. Please make sure to define `num_embeds_ada_norm` if setting `norm_type` to {norm_type}.')
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias,
        cross_attention_dim=cross_attention_dim if only_cross_attention else None, upcast_attention=upcast_attention)
        if cross_attention_dim is not None or double_self_attention: self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim if not double_self_attention else None,
        heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, upcast_attention=upcast_attention)
        else: self.attn2 = None
        if self.use_ada_layer_norm: self.norm1 = AdaLayerNorm(dim, num_embeds_ada_norm)
        else: self.norm1 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine)
        if cross_attention_dim is not None or double_self_attention: self.norm2 = AdaLayerNorm(dim, num_embeds_ada_norm) if self.use_ada_layer_norm else nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine)
        else: self.norm2 = None
        self.norm3 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=final_dropout)
    def forward(self, hidden_states, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, timestep=None, cross_attention_kwargs=None, class_labels=None):
        if self.pre_layer_norm:
            if self.use_ada_layer_norm: norm_hidden_states = self.norm1(hidden_states, timestep)
            else: norm_hidden_states = self.norm1(hidden_states)
        else: norm_hidden_states = hidden_states
        cross_attention_kwargs = cross_attention_kwargs if cross_attention_kwargs is not None else {}
        attn_output = self.attn1(norm_hidden_states, encoder_hidden_states=encoder_hidden_states if self.only_cross_attention else None, attention_mask=attention_mask, **cross_attention_kwargs)
        if not self.pre_layer_norm:
            if self.use_ada_layer_norm: attn_output = self.norm1(attn_output, timestep)
            else: attn_output = self.norm1(attn_output)
        hidden_states = attn_output + hidden_states
        if self.attn2 is not None:
            if self.pre_layer_norm: norm_hidden_states = self.norm2(hidden_states, timestep) if self.use_ada_layer_norm else self.norm2(hidden_states)
            else: norm_hidden_states = hidden_states
            attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask, **cross_attention_kwargs)
            if not self.pre_layer_norm: attn_output = self.norm2(attn_output, timestep) if self.use_ada_layer_norm else self.norm2(attn_output)
            hidden_states = attn_output + hidden_states
        if self.pre_layer_norm: norm_hidden_states = self.norm3(hidden_states)
        else: norm_hidden_states = hidden_states
        ff_output = self.ff(norm_hidden_states)
        if not self.pre_layer_norm: ff_output = self.norm3(ff_output)
        hidden_states = ff_output + hidden_states
        return hidden_states
class UniDiffuserBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int, dropout=0.0, cross_attention_dim: Optional[int]=None,
    activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None, attention_bias: bool=False, only_cross_attention: bool=False,
    double_self_attention: bool=False, upcast_attention: bool=False, norm_elementwise_affine: bool=True, norm_type: str='layer_norm',
    pre_layer_norm: bool=False, final_dropout: bool=True):
        super().__init__()
        self.only_cross_attention = only_cross_attention
        self.use_ada_layer_norm = num_embeds_ada_norm is not None and norm_type == 'ada_norm'
        self.pre_layer_norm = pre_layer_norm
        if norm_type in ('ada_norm', 'ada_norm_zero') and num_embeds_ada_norm is None: raise ValueError(f'`norm_type` is set to {norm_type}, but `num_embeds_ada_norm` is not defined. Please make sure to define `num_embeds_ada_norm` if setting `norm_type` to {norm_type}.')
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias,
        cross_attention_dim=cross_attention_dim if only_cross_attention else None, upcast_attention=upcast_attention)
        if cross_attention_dim is not None or double_self_attention: self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim if not double_self_attention else None,
        heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, upcast_attention=upcast_attention)
        else: self.attn2 = None
        if self.use_ada_layer_norm: self.norm1 = AdaLayerNorm(dim, num_embeds_ada_norm)
        else: self.norm1 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine)
        if cross_attention_dim is not None or double_self_attention: self.norm2 = AdaLayerNorm(dim, num_embeds_ada_norm) if self.use_ada_layer_norm else nn.LayerNorm(dim,
        elementwise_affine=norm_elementwise_affine)
        else: self.norm2 = None
        self.norm3 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=final_dropout)
    def forward(self, hidden_states, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, timestep=None,
    cross_attention_kwargs=None, class_labels=None):
        if self.pre_layer_norm:
            if self.use_ada_layer_norm: hidden_states = self.norm1(hidden_states, timestep)
            else: hidden_states = self.norm1(hidden_states)
        cross_attention_kwargs = cross_attention_kwargs if cross_attention_kwargs is not None else {}
        attn_output = self.attn1(hidden_states, encoder_hidden_states=encoder_hidden_states if self.only_cross_attention else None, attention_mask=attention_mask, **cross_attention_kwargs)
        hidden_states = attn_output + hidden_states
        if not self.pre_layer_norm:
            if self.use_ada_layer_norm: hidden_states = self.norm1(hidden_states, timestep)
            else: hidden_states = self.norm1(hidden_states)
        if self.attn2 is not None:
            if self.pre_layer_norm: hidden_states = self.norm2(hidden_states, timestep) if self.use_ada_layer_norm else self.norm2(hidden_states)
            attn_output = self.attn2(hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask, **cross_attention_kwargs)
            hidden_states = attn_output + hidden_states
            if not self.pre_layer_norm: hidden_states = self.norm2(hidden_states, timestep) if self.use_ada_layer_norm else self.norm2(hidden_states)
        if self.pre_layer_norm: hidden_states = self.norm3(hidden_states)
        ff_output = self.ff(hidden_states)
        hidden_states = ff_output + hidden_states
        if not self.pre_layer_norm: hidden_states = self.norm3(hidden_states)
        return hidden_states
class UTransformer2DModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, out_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0,
    norm_num_groups: int=32, cross_attention_dim: Optional[int]=None, attention_bias: bool=False, sample_size: Optional[int]=None, num_vector_embeds: Optional[int]=None,
    patch_size: Optional[int]=2, activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None, use_linear_projection: bool=False, only_cross_attention: bool=False,
    upcast_attention: bool=False, norm_type: str='layer_norm', block_type: str='unidiffuser', pre_layer_norm: bool=False, norm_elementwise_affine: bool=True,
    use_patch_pos_embed=False, ff_final_dropout: bool=False):
        super().__init__()
        self.use_linear_projection = use_linear_projection
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        inner_dim = num_attention_heads * attention_head_dim
        assert in_channels is not None and patch_size is not None, 'Patch input requires in_channels and patch_size.'
        assert sample_size is not None, 'UTransformer2DModel over patched input must provide sample_size'
        self.height = sample_size
        self.width = sample_size
        self.patch_size = patch_size
        self.pos_embed = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels, embed_dim=inner_dim, use_pos_embed=use_patch_pos_embed)
        if block_type == 'unidiffuser': block_cls = UniDiffuserBlock
        else: block_cls = UTransformerBlock
        self.transformer_in_blocks = nn.ModuleList([block_cls(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, attention_bias=attention_bias, only_cross_attention=only_cross_attention,
        upcast_attention=upcast_attention, norm_type=norm_type, pre_layer_norm=pre_layer_norm, norm_elementwise_affine=norm_elementwise_affine,
        final_dropout=ff_final_dropout) for d in range(num_layers // 2)])
        self.transformer_mid_block = block_cls(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, cross_attention_dim=cross_attention_dim,
        activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, attention_bias=attention_bias, only_cross_attention=only_cross_attention,
        upcast_attention=upcast_attention, norm_type=norm_type, pre_layer_norm=pre_layer_norm, norm_elementwise_affine=norm_elementwise_affine, final_dropout=ff_final_dropout)
        self.transformer_out_blocks = nn.ModuleList([nn.ModuleDict({'skip': SkipBlock(inner_dim), 'block': block_cls(inner_dim, num_attention_heads, attention_head_dim,
        dropout=dropout, cross_attention_dim=cross_attention_dim, activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, attention_bias=attention_bias,
        only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, norm_type=norm_type, pre_layer_norm=pre_layer_norm,
        norm_elementwise_affine=norm_elementwise_affine, final_dropout=ff_final_dropout)}) for d in range(num_layers // 2)])
        self.out_channels = in_channels if out_channels is None else out_channels
        self.norm_out = nn.LayerNorm(inner_dim)
    def forward(self, hidden_states, encoder_hidden_states=None, timestep=None, class_labels=None, cross_attention_kwargs=None, return_dict: bool=True,
    hidden_states_is_embedding: bool=False, unpatchify: bool=True):
        """Returns:"""
        if not unpatchify and return_dict: raise ValueError(f'Cannot both define `unpatchify`: {unpatchify} and `return_dict`: {return_dict} since when `unpatchify` is {unpatchify} the returned output is of shape (batch_size, seq_len, hidden_dim) rather than (batch_size, num_channels, height, width).')
        if not hidden_states_is_embedding: hidden_states = self.pos_embed(hidden_states)
        skips = []
        for in_block in self.transformer_in_blocks:
            hidden_states = in_block(hidden_states, encoder_hidden_states=encoder_hidden_states, timestep=timestep,
            cross_attention_kwargs=cross_attention_kwargs, class_labels=class_labels)
            skips.append(hidden_states)
        hidden_states = self.transformer_mid_block(hidden_states)
        for out_block in self.transformer_out_blocks:
            hidden_states = out_block['skip'](hidden_states, skips.pop())
            hidden_states = out_block['block'](hidden_states, encoder_hidden_states=encoder_hidden_states, timestep=timestep,
            cross_attention_kwargs=cross_attention_kwargs, class_labels=class_labels)
        hidden_states = self.norm_out(hidden_states)
        if unpatchify:
            height = width = int(hidden_states.shape[1] ** 0.5)
            hidden_states = hidden_states.reshape(shape=(-1, height, width, self.patch_size, self.patch_size, self.out_channels))
            hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
            output = hidden_states.reshape(shape=(-1, self.out_channels, height * self.patch_size, width * self.patch_size))
        else: output = hidden_states
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
class UniDiffuserModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, text_dim: int=768, clip_img_dim: int=512, num_text_tokens: int=77, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None,
    out_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0, norm_num_groups: int=32, cross_attention_dim: Optional[int]=None, attention_bias: bool=False,
    sample_size: Optional[int]=None, num_vector_embeds: Optional[int]=None, patch_size: Optional[int]=None, activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None,
    use_linear_projection: bool=False, only_cross_attention: bool=False, upcast_attention: bool=False, norm_type: str='layer_norm', block_type: str='unidiffuser',
    pre_layer_norm: bool=False, use_timestep_embedding=False, norm_elementwise_affine: bool=True, use_patch_pos_embed=False, ff_final_dropout: bool=True, use_data_type_embedding: bool=False):
        super().__init__()
        self.inner_dim = num_attention_heads * attention_head_dim
        assert sample_size is not None, 'UniDiffuserModel over patched input must provide sample_size'
        self.sample_size = sample_size
        self.in_channels = in_channels
        self.out_channels = in_channels if out_channels is None else out_channels
        self.patch_size = patch_size
        self.num_patches = self.sample_size // patch_size * (self.sample_size // patch_size)
        self.vae_img_in = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels, embed_dim=self.inner_dim, use_pos_embed=use_patch_pos_embed)
        self.clip_img_in = nn.Linear(clip_img_dim, self.inner_dim)
        self.text_in = nn.Linear(text_dim, self.inner_dim)
        self.timestep_img_proj = Timesteps(self.inner_dim, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_img_embed = TimestepEmbedding(self.inner_dim, 4 * self.inner_dim, out_dim=self.inner_dim) if use_timestep_embedding else nn.Identity()
        self.timestep_text_proj = Timesteps(self.inner_dim, flip_sin_to_cos=True, downscale_freq_shift=0)
        self.timestep_text_embed = TimestepEmbedding(self.inner_dim, 4 * self.inner_dim, out_dim=self.inner_dim) if use_timestep_embedding else nn.Identity()
        self.num_text_tokens = num_text_tokens
        self.num_tokens = 1 + 1 + num_text_tokens + 1 + self.num_patches
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_tokens, self.inner_dim))
        self.pos_embed_drop = nn.Dropout(p=dropout)
        trunc_normal_(self.pos_embed, std=0.02)
        self.use_data_type_embedding = use_data_type_embedding
        if self.use_data_type_embedding:
            self.data_type_token_embedding = nn.Embedding(2, self.inner_dim)
            self.data_type_pos_embed_token = nn.Parameter(torch.zeros(1, 1, self.inner_dim))
        self.transformer = UTransformer2DModel(num_attention_heads=num_attention_heads, attention_head_dim=attention_head_dim, in_channels=in_channels, out_channels=out_channels,
        num_layers=num_layers, dropout=dropout, norm_num_groups=norm_num_groups, cross_attention_dim=cross_attention_dim, attention_bias=attention_bias, sample_size=sample_size,
        num_vector_embeds=num_vector_embeds, patch_size=patch_size, activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm, use_linear_projection=use_linear_projection,
        only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, norm_type=norm_type, block_type=block_type, pre_layer_norm=pre_layer_norm,
        norm_elementwise_affine=norm_elementwise_affine, use_patch_pos_embed=use_patch_pos_embed, ff_final_dropout=ff_final_dropout)
        patch_dim = patch_size ** 2 * out_channels
        self.vae_img_out = nn.Linear(self.inner_dim, patch_dim)
        self.clip_img_out = nn.Linear(self.inner_dim, clip_img_dim)
        self.text_out = nn.Linear(self.inner_dim, text_dim)
    @torch.jit.ignore
    def no_weight_decay(self): return {'pos_embed'}
    def forward(self, latent_image_embeds: torch.Tensor, image_embeds: torch.Tensor, prompt_embeds: torch.Tensor, timestep_img: Union[torch.Tensor, float, int],
    timestep_text: Union[torch.Tensor, float, int], data_type: Optional[Union[torch.Tensor, float, int]]=1, encoder_hidden_states=None, cross_attention_kwargs=None):
        """Returns:"""
        batch_size = latent_image_embeds.shape[0]
        vae_hidden_states = self.vae_img_in(latent_image_embeds)
        clip_hidden_states = self.clip_img_in(image_embeds)
        text_hidden_states = self.text_in(prompt_embeds)
        num_text_tokens, num_img_tokens = (text_hidden_states.size(1), vae_hidden_states.size(1))
        if not torch.is_tensor(timestep_img): timestep_img = torch.tensor([timestep_img], dtype=torch.long, device=vae_hidden_states.device)
        timestep_img = timestep_img * torch.ones(batch_size, dtype=timestep_img.dtype, device=timestep_img.device)
        timestep_img_token = self.timestep_img_proj(timestep_img)
        timestep_img_token = timestep_img_token.to(dtype=self.dtype)
        timestep_img_token = self.timestep_img_embed(timestep_img_token)
        timestep_img_token = timestep_img_token.unsqueeze(dim=1)
        if not torch.is_tensor(timestep_text): timestep_text = torch.tensor([timestep_text], dtype=torch.long, device=vae_hidden_states.device)
        timestep_text = timestep_text * torch.ones(batch_size, dtype=timestep_text.dtype, device=timestep_text.device)
        timestep_text_token = self.timestep_text_proj(timestep_text)
        timestep_text_token = timestep_text_token.to(dtype=self.dtype)
        timestep_text_token = self.timestep_text_embed(timestep_text_token)
        timestep_text_token = timestep_text_token.unsqueeze(dim=1)
        if self.use_data_type_embedding:
            assert data_type is not None, 'data_type must be supplied if the model uses a data type embedding'
            if not torch.is_tensor(data_type): data_type = torch.tensor([data_type], dtype=torch.int, device=vae_hidden_states.device)
            data_type = data_type * torch.ones(batch_size, dtype=data_type.dtype, device=data_type.device)
            data_type_token = self.data_type_token_embedding(data_type).unsqueeze(dim=1)
            hidden_states = torch.cat([timestep_img_token, timestep_text_token, data_type_token, text_hidden_states, clip_hidden_states, vae_hidden_states], dim=1)
        else: hidden_states = torch.cat([timestep_img_token, timestep_text_token, text_hidden_states, clip_hidden_states, vae_hidden_states], dim=1)
        if self.use_data_type_embedding: pos_embed = torch.cat([self.pos_embed[:, :1 + 1, :], self.data_type_pos_embed_token, self.pos_embed[:, 1 + 1:, :]], dim=1)
        else: pos_embed = self.pos_embed
        hidden_states = hidden_states + pos_embed
        hidden_states = self.pos_embed_drop(hidden_states)
        hidden_states = self.transformer(hidden_states, encoder_hidden_states=encoder_hidden_states, timestep=None, class_labels=None, cross_attention_kwargs=cross_attention_kwargs,
        return_dict=False, hidden_states_is_embedding=True, unpatchify=False)[0]
        if self.use_data_type_embedding: t_img_token_out, t_text_token_out, data_type_token_out, text_out, img_clip_out, img_vae_out = hidden_states.split((1, 1, 1, num_text_tokens, 1, num_img_tokens), dim=1)
        else: t_img_token_out, t_text_token_out, text_out, img_clip_out, img_vae_out = hidden_states.split((1, 1, num_text_tokens, 1, num_img_tokens), dim=1)
        img_vae_out = self.vae_img_out(img_vae_out)
        height = width = int(img_vae_out.shape[1] ** 0.5)
        img_vae_out = img_vae_out.reshape(shape=(-1, height, width, self.patch_size, self.patch_size, self.out_channels))
        img_vae_out = torch.einsum('nhwpqc->nchpwq', img_vae_out)
        img_vae_out = img_vae_out.reshape(shape=(-1, self.out_channels, height * self.patch_size, width * self.patch_size))
        img_clip_out = self.clip_img_out(img_clip_out)
        text_out = self.text_out(text_out)
        return (img_vae_out, img_clip_out, text_out)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
