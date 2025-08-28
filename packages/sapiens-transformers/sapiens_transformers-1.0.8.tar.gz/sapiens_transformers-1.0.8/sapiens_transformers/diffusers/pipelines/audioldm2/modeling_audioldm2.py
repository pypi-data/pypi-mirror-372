'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.utils.checkpoint
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders import UNet2DConditionLoadersMixin
from ...models.activations import get_activation
from ...models.attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from ...models.embeddings import TimestepEmbedding, Timesteps
from ...models.modeling_utils import ModelMixin
from ...models.resnet import Downsample2D, ResnetBlock2D, Upsample2D
from ...models.sapiens_transformers.transformer_2d import Transformer2DModel
from ...models.unets.unet_2d_blocks import DownBlock2D, UpBlock2D
from ...models.unets.unet_2d_condition import UNet2DConditionOutput
from ...utils import BaseOutput, is_torch_version
def add_special_tokens(hidden_states, attention_mask, sos_token, eos_token):
    batch_size = hidden_states.shape[0]
    if attention_mask is not None:
        new_attn_mask_step = attention_mask.new_ones((batch_size, 1))
        attention_mask = torch.concat([new_attn_mask_step, attention_mask, new_attn_mask_step], dim=-1)
    sos_token = sos_token.expand(batch_size, 1, -1)
    eos_token = eos_token.expand(batch_size, 1, -1)
    hidden_states = torch.concat([sos_token, hidden_states, eos_token], dim=1)
    return (hidden_states, attention_mask)
@dataclass
class AudioLDM2ProjectionModelOutput(BaseOutput):
    """Args:"""
    hidden_states: torch.Tensor
    attention_mask: Optional[torch.LongTensor] = None
class AudioLDM2ProjectionModel(ModelMixin, ConfigMixin):
    """Args:"""
    @register_to_config
    def __init__(self, text_encoder_dim, text_encoder_1_dim, langauge_model_dim, use_learned_position_embedding=None, max_seq_length=None):
        super().__init__()
        self.projection = nn.Linear(text_encoder_dim, langauge_model_dim)
        self.projection_1 = nn.Linear(text_encoder_1_dim, langauge_model_dim)
        self.sos_embed = nn.Parameter(torch.ones(langauge_model_dim))
        self.eos_embed = nn.Parameter(torch.ones(langauge_model_dim))
        self.sos_embed_1 = nn.Parameter(torch.ones(langauge_model_dim))
        self.eos_embed_1 = nn.Parameter(torch.ones(langauge_model_dim))
        self.use_learned_position_embedding = use_learned_position_embedding
        if self.use_learned_position_embedding is not None: self.learnable_positional_embedding = torch.nn.Parameter(torch.zeros((1, text_encoder_1_dim, max_seq_length)))
    def forward(self, hidden_states: Optional[torch.Tensor]=None, hidden_states_1: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.LongTensor]=None, attention_mask_1: Optional[torch.LongTensor]=None):
        hidden_states = self.projection(hidden_states)
        hidden_states, attention_mask = add_special_tokens(hidden_states, attention_mask, sos_token=self.sos_embed, eos_token=self.eos_embed)
        if self.use_learned_position_embedding is not None: hidden_states_1 = (hidden_states_1.permute(0, 2, 1) + self.learnable_positional_embedding).permute(0, 2, 1)
        hidden_states_1 = self.projection_1(hidden_states_1)
        hidden_states_1, attention_mask_1 = add_special_tokens(hidden_states_1, attention_mask_1, sos_token=self.sos_embed_1, eos_token=self.eos_embed_1)
        hidden_states = torch.cat([hidden_states, hidden_states_1], dim=1)
        if attention_mask is None and attention_mask_1 is not None: attention_mask = attention_mask_1.new_ones(hidden_states[:2])
        elif attention_mask is not None and attention_mask_1 is None: attention_mask_1 = attention_mask.new_ones(hidden_states_1[:2])
        if attention_mask is not None and attention_mask_1 is not None: attention_mask = torch.cat([attention_mask, attention_mask_1], dim=-1)
        else: attention_mask = None
        return AudioLDM2ProjectionModelOutput(hidden_states=hidden_states, attention_mask=attention_mask)
class AudioLDM2UNet2DConditionModel(ModelMixin, ConfigMixin, UNet2DConditionLoadersMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: Optional[int]=None, in_channels: int=4, out_channels: int=4, flip_sin_to_cos: bool=True, freq_shift: int=0,
    down_block_types: Tuple[str]=('CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'CrossAttnDownBlock2D', 'DownBlock2D'), mid_block_type: Optional[str]='UNetMidBlock2DCrossAttn',
    up_block_types: Tuple[str]=('UpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D', 'CrossAttnUpBlock2D'), only_cross_attention: Union[bool,
    Tuple[bool]]=False, block_out_channels: Tuple[int]=(320, 640, 1280, 1280),
    layers_per_block: Union[int, Tuple[int]]=2, downsample_padding: int=1, mid_block_scale_factor: float=1, act_fn: str='silu',
    norm_num_groups: Optional[int]=32, norm_eps: float=1e-05, cross_attention_dim: Union[int,
    Tuple[int]]=1280, transformer_layers_per_block: Union[int, Tuple[int]]=1, attention_head_dim: Union[int, Tuple[int]]=8,
    num_attention_heads: Optional[Union[int, Tuple[int]]]=None, use_linear_projection: bool=False,
    class_embed_type: Optional[str]=None, num_class_embeds: Optional[int]=None, upcast_attention: bool=False, resnet_time_scale_shift: str='default',
    time_embedding_type: str='positional', time_embedding_dim: Optional[int]=None,
    time_embedding_act_fn: Optional[str]=None, timestep_post_act: Optional[str]=None, time_cond_proj_dim: Optional[int]=None, conv_in_kernel: int=3, conv_out_kernel: int=3,
    projection_class_embeddings_input_dim: Optional[int]=None, class_embeddings_concat: bool=False):
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
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        if time_embedding_type == 'positional':
            time_embed_dim = time_embedding_dim or block_out_channels[0] * 4
            self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
            timestep_input_dim = block_out_channels[0]
        else: raise ValueError(f'{time_embedding_type} does not exist. Please make sure to use `positional`.')
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn, post_act_fn=timestep_post_act, cond_proj_dim=time_cond_proj_dim)
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
        if time_embedding_act_fn is None: self.time_embed_act = None
        else: self.time_embed_act = get_activation(time_embedding_act_fn)
        self.down_blocks = nn.ModuleList([])
        self.up_blocks = nn.ModuleList([])
        if isinstance(only_cross_attention, bool): only_cross_attention = [only_cross_attention] * len(down_block_types)
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
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
            down_block = get_down_block(down_block_type, num_layers=layers_per_block[i],
            transformer_layers_per_block=transformer_layers_per_block[i], in_channels=input_channel,
            out_channels=output_channel, temb_channels=blocks_time_embed_dim, add_downsample=not is_final_block, resnet_eps=norm_eps, resnet_act_fn=act_fn,
            resnet_groups=norm_num_groups, cross_attention_dim=cross_attention_dim[i],
            num_attention_heads=num_attention_heads[i], downsample_padding=downsample_padding, use_linear_projection=use_linear_projection,
            only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention,
            resnet_time_scale_shift=resnet_time_scale_shift)
            self.down_blocks.append(down_block)
        if mid_block_type == 'UNetMidBlock2DCrossAttn': self.mid_block = UNetMidBlock2DCrossAttn(transformer_layers_per_block=transformer_layers_per_block[-1],
        in_channels=block_out_channels[-1], temb_channels=blocks_time_embed_dim, resnet_eps=norm_eps,
        resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor, resnet_time_scale_shift=resnet_time_scale_shift,
        cross_attention_dim=cross_attention_dim[-1], num_attention_heads=num_attention_heads[-1], resnet_groups=norm_num_groups,
        use_linear_projection=use_linear_projection, upcast_attention=upcast_attention)
        else: raise ValueError(f'unknown mid_block_type : {mid_block_type}. Should be `UNetMidBlock2DCrossAttn` for AudioLDM2.')
        self.num_upsamplers = 0
        reversed_block_out_channels = list(reversed(block_out_channels))
        reversed_num_attention_heads = list(reversed(num_attention_heads))
        reversed_layers_per_block = list(reversed(layers_per_block))
        reversed_cross_attention_dim = list(reversed(cross_attention_dim))
        reversed_transformer_layers_per_block = list(reversed(transformer_layers_per_block))
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
            up_block = get_up_block(up_block_type, num_layers=reversed_layers_per_block[i] + 1, transformer_layers_per_block=reversed_transformer_layers_per_block[i],
            in_channels=input_channel, out_channels=output_channel, prev_output_channel=prev_output_channel, temb_channels=blocks_time_embed_dim,
            add_upsample=add_upsample, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, cross_attention_dim=reversed_cross_attention_dim[i],
            num_attention_heads=reversed_num_attention_heads[i], use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i],
            upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift)
            self.up_blocks.append(up_block)
            prev_output_channel = output_channel
        if norm_num_groups is not None:
            self.conv_norm_out = nn.GroupNorm(num_channels=block_out_channels[0], num_groups=norm_num_groups, eps=norm_eps)
            self.conv_act = get_activation(act_fn)
        else:
            self.conv_norm_out = None
            self.conv_act = None
        conv_out_padding = (conv_out_kernel - 1) // 2
        self.conv_out = nn.Conv2d(block_out_channels[0], out_channels, kernel_size=conv_out_kernel, padding=conv_out_padding)
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
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor,
    class_labels: Optional[torch.Tensor]=None, timestep_cond: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, return_dict: bool=True, encoder_hidden_states_1: Optional[torch.Tensor]=None,
    encoder_attention_mask_1: Optional[torch.Tensor]=None) -> Union[UNet2DConditionOutput, Tuple]:
        """Returns:"""
        default_overall_up_factor = 2 ** self.num_upsamplers
        forward_upsample_size = False
        upsample_size = None
        if any((s % default_overall_up_factor != 0 for s in sample.shape[-2:])): forward_upsample_size = True
        if attention_mask is not None:
            attention_mask = (1 - attention_mask.to(sample.dtype)) * -10000.0
            attention_mask = attention_mask.unsqueeze(1)
        if encoder_attention_mask is not None:
            encoder_attention_mask = (1 - encoder_attention_mask.to(sample.dtype)) * -10000.0
            encoder_attention_mask = encoder_attention_mask.unsqueeze(1)
        if encoder_attention_mask_1 is not None:
            encoder_attention_mask_1 = (1 - encoder_attention_mask_1.to(sample.dtype)) * -10000.0
            encoder_attention_mask_1 = encoder_attention_mask_1.unsqueeze(1)
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
        emb = emb + aug_emb if aug_emb is not None else emb
        if self.time_embed_act is not None: emb = self.time_embed_act(emb)
        sample = self.conv_in(sample)
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention: sample, res_samples = downsample_block(hidden_states=sample,
            temb=emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs,
            encoder_attention_mask=encoder_attention_mask, encoder_hidden_states_1=encoder_hidden_states_1, encoder_attention_mask_1=encoder_attention_mask_1)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb)
            down_block_res_samples += res_samples
        if self.mid_block is not None: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask,
        cross_attention_kwargs=cross_attention_kwargs, encoder_attention_mask=encoder_attention_mask, encoder_hidden_states_1=encoder_hidden_states_1,
        encoder_attention_mask_1=encoder_attention_mask_1)
        for i, upsample_block in enumerate(self.up_blocks):
            is_final_block = i == len(self.up_blocks) - 1
            res_samples = down_block_res_samples[-len(upsample_block.resnets):]
            down_block_res_samples = down_block_res_samples[:-len(upsample_block.resnets)]
            if not is_final_block and forward_upsample_size: upsample_size = down_block_res_samples[-1].shape[2:]
            if hasattr(upsample_block, 'has_cross_attention') and upsample_block.has_cross_attention: sample = upsample_block(hidden_states=sample, temb=emb,
            res_hidden_states_tuple=res_samples, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs, upsample_size=upsample_size,
            attention_mask=attention_mask, encoder_attention_mask=encoder_attention_mask, encoder_hidden_states_1=encoder_hidden_states_1, encoder_attention_mask_1=encoder_attention_mask_1)
            else: sample = upsample_block(hidden_states=sample, temb=emb, res_hidden_states_tuple=res_samples, upsample_size=upsample_size)
        if self.conv_norm_out:
            sample = self.conv_norm_out(sample)
            sample = self.conv_act(sample)
        sample = self.conv_out(sample)
        if not return_dict: return (sample,)
        return UNet2DConditionOutput(sample=sample)
def get_down_block(down_block_type, num_layers, in_channels, out_channels, temb_channels, add_downsample, resnet_eps, resnet_act_fn, transformer_layers_per_block=1,
num_attention_heads=None, resnet_groups=None, cross_attention_dim=None, downsample_padding=None, use_linear_projection=False,
only_cross_attention=False, upcast_attention=False, resnet_time_scale_shift='default'):
    down_block_type = down_block_type[7:] if down_block_type.startswith('UNetRes') else down_block_type
    if down_block_type == 'DownBlock2D': return DownBlock2D(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels,
    add_downsample=add_downsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups,
    downsample_padding=downsample_padding, resnet_time_scale_shift=resnet_time_scale_shift)
    elif down_block_type == 'CrossAttnDownBlock2D':
        if cross_attention_dim is None: raise ValueError('cross_attention_dim must be specified for CrossAttnDownBlock2D')
        return CrossAttnDownBlock2D(num_layers=num_layers, transformer_layers_per_block=transformer_layers_per_block, in_channels=in_channels, out_channels=out_channels,
        temb_channels=temb_channels, add_downsample=add_downsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups, downsample_padding=downsample_padding,
        cross_attention_dim=cross_attention_dim, num_attention_heads=num_attention_heads, use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention,
        upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift)
    raise ValueError(f'{down_block_type} does not exist.')
def get_up_block(up_block_type, num_layers, in_channels, out_channels, prev_output_channel, temb_channels, add_upsample, resnet_eps, resnet_act_fn,
transformer_layers_per_block=1, num_attention_heads=None, resnet_groups=None, cross_attention_dim=None, use_linear_projection=False,
only_cross_attention=False, upcast_attention=False, resnet_time_scale_shift='default'):
    up_block_type = up_block_type[7:] if up_block_type.startswith('UNetRes') else up_block_type
    if up_block_type == 'UpBlock2D': return UpBlock2D(num_layers=num_layers, in_channels=in_channels, out_channels=out_channels, prev_output_channel=prev_output_channel,
    temb_channels=temb_channels, add_upsample=add_upsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn, resnet_groups=resnet_groups, resnet_time_scale_shift=resnet_time_scale_shift)
    elif up_block_type == 'CrossAttnUpBlock2D':
        if cross_attention_dim is None: raise ValueError('cross_attention_dim must be specified for CrossAttnUpBlock2D')
        return CrossAttnUpBlock2D(num_layers=num_layers, transformer_layers_per_block=transformer_layers_per_block, in_channels=in_channels, out_channels=out_channels,
        prev_output_channel=prev_output_channel, temb_channels=temb_channels, add_upsample=add_upsample, resnet_eps=resnet_eps, resnet_act_fn=resnet_act_fn,
        resnet_groups=resnet_groups, cross_attention_dim=cross_attention_dim, num_attention_heads=num_attention_heads, use_linear_projection=use_linear_projection,
        only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift)
    raise ValueError(f'{up_block_type} does not exist.')
class CrossAttnDownBlock2D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: int=1, resnet_eps: float=1e-06,
    resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads=1, cross_attention_dim=1280,
    output_scale_factor=1.0, downsample_padding=1, add_downsample=True, use_linear_projection=False, only_cross_attention=False, upcast_attention=False):
        super().__init__()
        resnets = []
        attentions = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,)
        if isinstance(cross_attention_dim, (list, tuple)) and len(cross_attention_dim) > 4: raise ValueError(f'Only up to 4 cross-attention layers are supported. Ensure that the length of cross-attention dims is less than or equal to 4. Got cross-attention dims {cross_attention_dim} of length {len(cross_attention_dim)}')
        self.cross_attention_dim = cross_attention_dim
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=in_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            for j in range(len(cross_attention_dim)): attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels,
            num_layers=transformer_layers_per_block, cross_attention_dim=cross_attention_dim[j], norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection,
            only_cross_attention=only_cross_attention, upcast_attention=upcast_attention, double_self_attention=True if cross_attention_dim[j] is None else False))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        if add_downsample: self.downsamplers = nn.ModuleList([Downsample2D(out_channels, use_conv=True, out_channels=out_channels, padding=downsample_padding, name='op')])
        else: self.downsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states_1: Optional[torch.Tensor]=None,
    encoder_attention_mask_1: Optional[torch.Tensor]=None):
        output_states = ()
        num_layers = len(self.resnets)
        num_attention_per_layer = len(self.attentions) // num_layers
        encoder_hidden_states_1 = encoder_hidden_states_1 if encoder_hidden_states_1 is not None else encoder_hidden_states
        encoder_attention_mask_1 = encoder_attention_mask_1 if encoder_hidden_states_1 is not None else encoder_attention_mask
        for i in range(num_layers):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.resnets[i]), hidden_states, temb, **ckpt_kwargs)
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.attentions[i * num_attention_per_layer + idx], return_dict=False), hidden_states,
                    forward_encoder_hidden_states, None, None, cross_attention_kwargs, attention_mask, forward_encoder_attention_mask, **ckpt_kwargs)[0]
            else:
                hidden_states = self.resnets[i](hidden_states, temb)
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = self.attentions[i * num_attention_per_layer + idx](hidden_states, attention_mask=attention_mask, encoder_hidden_states=forward_encoder_hidden_states,
                    encoder_attention_mask=forward_encoder_attention_mask, return_dict=False)[0]
            output_states = output_states + (hidden_states,)
        if self.downsamplers is not None:
            for downsampler in self.downsamplers: hidden_states = downsampler(hidden_states)
            output_states = output_states + (hidden_states,)
        return (hidden_states, output_states)
class UNetMidBlock2DCrossAttn(nn.Module):
    def __init__(self, in_channels: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: int=1, resnet_eps: float=1e-06,
    resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads=1, output_scale_factor=1.0,
    cross_attention_dim=1280, use_linear_projection=False, upcast_attention=False):
        super().__init__()
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        resnet_groups = resnet_groups if resnet_groups is not None else min(in_channels // 4, 32)
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,)
        if isinstance(cross_attention_dim, (list, tuple)) and len(cross_attention_dim) > 4: raise ValueError(f'Only up to 4 cross-attention layers are supported. Ensure that the length of cross-attention dims is less than or equal to 4. Got cross-attention dims {cross_attention_dim} of length {len(cross_attention_dim)}')
        self.cross_attention_dim = cross_attention_dim
        resnets = [ResnetBlock2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout, time_embedding_norm=resnet_time_scale_shift,
        non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm)]
        attentions = []
        for i in range(num_layers):
            for j in range(len(cross_attention_dim)): attentions.append(Transformer2DModel(num_attention_heads, in_channels // num_attention_heads, in_channels=in_channels,
            num_layers=transformer_layers_per_block, cross_attention_dim=cross_attention_dim[j], norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection, upcast_attention=upcast_attention,
            double_self_attention=True if cross_attention_dim[j] is None else False))
            resnets.append(ResnetBlock2D(in_channels=in_channels, out_channels=in_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, encoder_attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states_1: Optional[torch.Tensor]=None,
    encoder_attention_mask_1: Optional[torch.Tensor]=None) -> torch.Tensor:
        hidden_states = self.resnets[0](hidden_states, temb)
        num_attention_per_layer = len(self.attentions) // (len(self.resnets) - 1)
        encoder_hidden_states_1 = encoder_hidden_states_1 if encoder_hidden_states_1 is not None else encoder_hidden_states
        encoder_attention_mask_1 = encoder_attention_mask_1 if encoder_hidden_states_1 is not None else encoder_attention_mask
        for i in range(len(self.resnets[1:])):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.attentions[i * num_attention_per_layer + idx], return_dict=False), hidden_states, forward_encoder_hidden_states,
                    None, None, cross_attention_kwargs, attention_mask, forward_encoder_attention_mask, **ckpt_kwargs)[0]
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.resnets[i + 1]), hidden_states, temb, **ckpt_kwargs)
            else:
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = self.attentions[i * num_attention_per_layer + idx](hidden_states, attention_mask=attention_mask, encoder_hidden_states=forward_encoder_hidden_states,
                    encoder_attention_mask=forward_encoder_attention_mask, return_dict=False)[0]
                hidden_states = self.resnets[i + 1](hidden_states, temb)
        return hidden_states
class CrossAttnUpBlock2D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, prev_output_channel: int, temb_channels: int, dropout: float=0.0, num_layers: int=1, transformer_layers_per_block: int=1, resnet_eps: float=1e-06,
    resnet_time_scale_shift: str='default', resnet_act_fn: str='swish', resnet_groups: int=32, resnet_pre_norm: bool=True, num_attention_heads=1, cross_attention_dim=1280, output_scale_factor=1.0,
    add_upsample=True, use_linear_projection=False, only_cross_attention=False, upcast_attention=False):
        super().__init__()
        resnets = []
        attentions = []
        self.has_cross_attention = True
        self.num_attention_heads = num_attention_heads
        if isinstance(cross_attention_dim, int): cross_attention_dim = (cross_attention_dim,)
        if isinstance(cross_attention_dim, (list, tuple)) and len(cross_attention_dim) > 4: raise ValueError(f'Only up to 4 cross-attention layers are supported. Ensure that the length of cross-attention dims is less than or equal to 4. Got cross-attention dims {cross_attention_dim} of length {len(cross_attention_dim)}')
        self.cross_attention_dim = cross_attention_dim
        for i in range(num_layers):
            res_skip_channels = in_channels if i == num_layers - 1 else out_channels
            resnet_in_channels = prev_output_channel if i == 0 else out_channels
            resnets.append(ResnetBlock2D(in_channels=resnet_in_channels + res_skip_channels, out_channels=out_channels, temb_channels=temb_channels, eps=resnet_eps, groups=resnet_groups, dropout=dropout,
            time_embedding_norm=resnet_time_scale_shift, non_linearity=resnet_act_fn, output_scale_factor=output_scale_factor, pre_norm=resnet_pre_norm))
            for j in range(len(cross_attention_dim)): attentions.append(Transformer2DModel(num_attention_heads, out_channels // num_attention_heads, in_channels=out_channels, num_layers=transformer_layers_per_block,
            cross_attention_dim=cross_attention_dim[j], norm_num_groups=resnet_groups, use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention, upcast_attention=upcast_attention,
            double_self_attention=True if cross_attention_dim[j] is None else False))
        self.attentions = nn.ModuleList(attentions)
        self.resnets = nn.ModuleList(resnets)
        if add_upsample: self.upsamplers = nn.ModuleList([Upsample2D(out_channels, use_conv=True, out_channels=out_channels)])
        else: self.upsamplers = None
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, res_hidden_states_tuple: Tuple[torch.Tensor, ...], temb: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, upsample_size: Optional[int]=None, attention_mask: Optional[torch.Tensor]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    encoder_hidden_states_1: Optional[torch.Tensor]=None, encoder_attention_mask_1: Optional[torch.Tensor]=None):
        num_layers = len(self.resnets)
        num_attention_per_layer = len(self.attentions) // num_layers
        encoder_hidden_states_1 = encoder_hidden_states_1 if encoder_hidden_states_1 is not None else encoder_hidden_states
        encoder_attention_mask_1 = encoder_attention_mask_1 if encoder_hidden_states_1 is not None else encoder_attention_mask
        for i in range(num_layers):
            res_hidden_states = res_hidden_states_tuple[-1]
            res_hidden_states_tuple = res_hidden_states_tuple[:-1]
            hidden_states = torch.cat([hidden_states, res_hidden_states], dim=1)
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.resnets[i]), hidden_states, temb, **ckpt_kwargs)
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(self.attentions[i * num_attention_per_layer + idx], return_dict=False), hidden_states, forward_encoder_hidden_states,
                    None, None, cross_attention_kwargs, attention_mask, forward_encoder_attention_mask, **ckpt_kwargs)[0]
            else:
                hidden_states = self.resnets[i](hidden_states, temb)
                for idx, cross_attention_dim in enumerate(self.cross_attention_dim):
                    if cross_attention_dim is not None and idx <= 1:
                        forward_encoder_hidden_states = encoder_hidden_states
                        forward_encoder_attention_mask = encoder_attention_mask
                    elif cross_attention_dim is not None and idx > 1:
                        forward_encoder_hidden_states = encoder_hidden_states_1
                        forward_encoder_attention_mask = encoder_attention_mask_1
                    else:
                        forward_encoder_hidden_states = None
                        forward_encoder_attention_mask = None
                    hidden_states = self.attentions[i * num_attention_per_layer + idx](hidden_states, attention_mask=attention_mask, encoder_hidden_states=forward_encoder_hidden_states,
                    encoder_attention_mask=forward_encoder_attention_mask, return_dict=False)[0]
        if self.upsamplers is not None:
            for upsampler in self.upsamplers: hidden_states = upsampler(hidden_states, upsample_size)
        return hidden_states
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
