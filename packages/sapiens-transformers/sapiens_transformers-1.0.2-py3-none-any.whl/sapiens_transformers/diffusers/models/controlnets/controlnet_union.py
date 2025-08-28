'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from ..unets.unet_2d_blocks import CrossAttnDownBlock2D, DownBlock2D, UNetMidBlock2DCrossAttn, get_down_block
from ..embeddings import TextImageTimeEmbedding, TextTimeEmbedding, TimestepEmbedding, Timesteps
from .controlnet import ControlNetConditioningEmbedding, ControlNetOutput, zero_module
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders.single_file_model import FromOriginalModelMixin
from typing import Any, Dict, List, Optional, Tuple, Union
from ..unets.unet_2d_condition import UNet2DConditionModel
from ..modeling_utils import ModelMixin
from torch import nn
import torch
class QuickGELU(nn.Module):
    def forward(self, input: torch.Tensor) -> torch.Tensor: return input * torch.sigmoid(1.702 * input)
class ResidualAttentionMlp(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.c_fc = nn.Linear(d_model, d_model * 4)
        self.gelu = QuickGELU()
        self.c_proj = nn.Linear(d_model * 4, d_model)
    def forward(self, x: torch.Tensor):
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        return x
class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int, attn_mask: torch.Tensor=None):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_head)
        self.ln_1 = nn.LayerNorm(d_model)
        self.mlp = ResidualAttentionMlp(d_model)
        self.ln_2 = nn.LayerNorm(d_model)
        self.attn_mask = attn_mask
    def attention(self, x: torch.Tensor):
        self.attn_mask = self.attn_mask.to(dtype=x.dtype, device=x.device) if self.attn_mask is not None else None
        return self.attn(x, x, x, need_weights=False, attn_mask=self.attn_mask)[0]
    def forward(self, x: torch.Tensor):
        x = x + self.attention(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x
class ControlNetUnionModel(ModelMixin, ConfigMixin, FromOriginalModelMixin):
    """Args:"""
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, in_channels: int=4, conditioning_channels: int=3, flip_sin_to_cos: bool=True, freq_shift: int=0, down_block_types: Tuple[str, ...]=('CrossAttnDownBlock2D', 'CrossAttnDownBlock2D',
    'CrossAttnDownBlock2D', 'DownBlock2D'), only_cross_attention: Union[bool, Tuple[bool]]=False, block_out_channels: Tuple[int, ...]=(320, 640, 1280, 1280), layers_per_block: int=2, downsample_padding: int=1,
    mid_block_scale_factor: float=1, act_fn: str='silu', norm_num_groups: Optional[int]=32, norm_eps: float=1e-05, cross_attention_dim: int=1280, transformer_layers_per_block: Union[int, Tuple[int, ...]]=1,
    encoder_hid_dim: Optional[int]=None, encoder_hid_dim_type: Optional[str]=None, attention_head_dim: Union[int, Tuple[int, ...]]=8, num_attention_heads: Optional[Union[int, Tuple[int, ...]]]=None,
    use_linear_projection: bool=False, class_embed_type: Optional[str]=None, addition_embed_type: Optional[str]=None, addition_time_embed_dim: Optional[int]=None, num_class_embeds: Optional[int]=None,
    upcast_attention: bool=False, resnet_time_scale_shift: str='default', projection_class_embeddings_input_dim: Optional[int]=None, controlnet_conditioning_channel_order: str='rgb',
    conditioning_embedding_out_channels: Optional[Tuple[int, ...]]=(48, 96, 192, 384), global_pool_conditions: bool=False, addition_embed_type_num_heads: int=64, num_control_type: int=6,
    num_trans_channel: int=320, num_trans_head: int=8, num_trans_layer: int=1, num_proj_channel: int=320):
        super().__init__()
        num_attention_heads = num_attention_heads or attention_head_dim
        if len(block_out_channels) != len(down_block_types): raise ValueError(f'Must provide the same number of `block_out_channels` as `down_block_types`. `block_out_channels`: {block_out_channels}. `down_block_types`: {down_block_types}.')
        if not isinstance(only_cross_attention, bool) and len(only_cross_attention) != len(down_block_types): raise ValueError(f'Must provide the same number of `only_cross_attention` as `down_block_types`. `only_cross_attention`: {only_cross_attention}. `down_block_types`: {down_block_types}.')
        if not isinstance(num_attention_heads, int) and len(num_attention_heads) != len(down_block_types): raise ValueError(f'Must provide the same number of `num_attention_heads` as `down_block_types`. `num_attention_heads`: {num_attention_heads}. `down_block_types`: {down_block_types}.')
        if isinstance(transformer_layers_per_block, int): transformer_layers_per_block = [transformer_layers_per_block] * len(down_block_types)
        conv_in_kernel = 3
        conv_in_padding = (conv_in_kernel - 1) // 2
        self.conv_in = nn.Conv2d(in_channels, block_out_channels[0], kernel_size=conv_in_kernel, padding=conv_in_padding)
        time_embed_dim = block_out_channels[0] * 4
        self.time_proj = Timesteps(block_out_channels[0], flip_sin_to_cos, freq_shift)
        timestep_input_dim = block_out_channels[0]
        self.time_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim, act_fn=act_fn)
        if encoder_hid_dim_type is not None: raise ValueError(f'encoder_hid_dim_type: {encoder_hid_dim_type} must be None.')
        else: self.encoder_hid_proj = None
        if class_embed_type is None and num_class_embeds is not None: self.class_embedding = nn.Embedding(num_class_embeds, time_embed_dim)
        elif class_embed_type == 'timestep': self.class_embedding = TimestepEmbedding(timestep_input_dim, time_embed_dim)
        elif class_embed_type == 'identity': self.class_embedding = nn.Identity(time_embed_dim, time_embed_dim)
        elif class_embed_type == 'projection':
            if projection_class_embeddings_input_dim is None: raise ValueError("`class_embed_type`: 'projection' requires `projection_class_embeddings_input_dim` be set")
            self.class_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        else: self.class_embedding = None
        if addition_embed_type == 'text':
            if encoder_hid_dim is not None: text_time_embedding_from_dim = encoder_hid_dim
            else: text_time_embedding_from_dim = cross_attention_dim
            self.add_embedding = TextTimeEmbedding(text_time_embedding_from_dim, time_embed_dim, num_heads=addition_embed_type_num_heads)
        elif addition_embed_type == 'text_image': self.add_embedding = TextImageTimeEmbedding(text_embed_dim=cross_attention_dim, image_embed_dim=cross_attention_dim, time_embed_dim=time_embed_dim)
        elif addition_embed_type == 'text_time':
            self.add_time_proj = Timesteps(addition_time_embed_dim, flip_sin_to_cos, freq_shift)
            self.add_embedding = TimestepEmbedding(projection_class_embeddings_input_dim, time_embed_dim)
        elif addition_embed_type is not None: raise ValueError(f"addition_embed_type: {addition_embed_type} must be None, 'text' or 'text_image'.")
        self.controlnet_cond_embedding = ControlNetConditioningEmbedding(conditioning_embedding_channels=block_out_channels[0],
        block_out_channels=conditioning_embedding_out_channels, conditioning_channels=conditioning_channels)
        task_scale_factor = num_trans_channel ** 0.5
        self.task_embedding = nn.Parameter(task_scale_factor * torch.randn(num_control_type, num_trans_channel))
        self.transformer_layes = nn.ModuleList([ResidualAttentionBlock(num_trans_channel, num_trans_head) for _ in range(num_trans_layer)])
        self.spatial_ch_projs = zero_module(nn.Linear(num_trans_channel, num_proj_channel))
        self.control_type_proj = Timesteps(addition_time_embed_dim, flip_sin_to_cos, freq_shift)
        self.control_add_embedding = TimestepEmbedding(addition_time_embed_dim * num_control_type, time_embed_dim)
        self.down_blocks = nn.ModuleList([])
        self.controlnet_down_blocks = nn.ModuleList([])
        if isinstance(only_cross_attention, bool): only_cross_attention = [only_cross_attention] * len(down_block_types)
        if isinstance(attention_head_dim, int): attention_head_dim = (attention_head_dim,) * len(down_block_types)
        if isinstance(num_attention_heads, int): num_attention_heads = (num_attention_heads,) * len(down_block_types)
        output_channel = block_out_channels[0]
        controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
        controlnet_block = zero_module(controlnet_block)
        self.controlnet_down_blocks.append(controlnet_block)
        for i, down_block_type in enumerate(down_block_types):
            input_channel = output_channel
            output_channel = block_out_channels[i]
            is_final_block = i == len(block_out_channels) - 1
            down_block = get_down_block(down_block_type, num_layers=layers_per_block, transformer_layers_per_block=transformer_layers_per_block[i], in_channels=input_channel, out_channels=output_channel,
            temb_channels=time_embed_dim, add_downsample=not is_final_block, resnet_eps=norm_eps, resnet_act_fn=act_fn, resnet_groups=norm_num_groups, cross_attention_dim=cross_attention_dim,
            num_attention_heads=num_attention_heads[i], attention_head_dim=attention_head_dim[i] if attention_head_dim[i] is not None else output_channel, downsample_padding=downsample_padding,
            use_linear_projection=use_linear_projection, only_cross_attention=only_cross_attention[i], upcast_attention=upcast_attention, resnet_time_scale_shift=resnet_time_scale_shift)
            self.down_blocks.append(down_block)
            for _ in range(layers_per_block):
                controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
                controlnet_block = zero_module(controlnet_block)
                self.controlnet_down_blocks.append(controlnet_block)
            if not is_final_block:
                controlnet_block = nn.Conv2d(output_channel, output_channel, kernel_size=1)
                controlnet_block = zero_module(controlnet_block)
                self.controlnet_down_blocks.append(controlnet_block)
        mid_block_channel = block_out_channels[-1]
        controlnet_block = nn.Conv2d(mid_block_channel, mid_block_channel, kernel_size=1)
        controlnet_block = zero_module(controlnet_block)
        self.controlnet_mid_block = controlnet_block
        self.mid_block = UNetMidBlock2DCrossAttn(transformer_layers_per_block=transformer_layers_per_block[-1], in_channels=mid_block_channel, temb_channels=time_embed_dim, resnet_eps=norm_eps,
        resnet_act_fn=act_fn, output_scale_factor=mid_block_scale_factor, resnet_time_scale_shift=resnet_time_scale_shift, cross_attention_dim=cross_attention_dim, num_attention_heads=num_attention_heads[-1],
        resnet_groups=norm_num_groups, use_linear_projection=use_linear_projection, upcast_attention=upcast_attention)
    @classmethod
    def from_unet(cls, unet: UNet2DConditionModel, controlnet_conditioning_channel_order: str='rgb', conditioning_embedding_out_channels: Optional[Tuple[int, ...]]=(16, 32, 96, 256), load_weights_from_unet: bool=True):
        transformer_layers_per_block = unet.config.transformer_layers_per_block if 'transformer_layers_per_block' in unet.config else 1
        encoder_hid_dim = unet.config.encoder_hid_dim if 'encoder_hid_dim' in unet.config else None
        encoder_hid_dim_type = unet.config.encoder_hid_dim_type if 'encoder_hid_dim_type' in unet.config else None
        addition_embed_type = unet.config.addition_embed_type if 'addition_embed_type' in unet.config else None
        addition_time_embed_dim = unet.config.addition_time_embed_dim if 'addition_time_embed_dim' in unet.config else None
        controlnet = cls(encoder_hid_dim=encoder_hid_dim, encoder_hid_dim_type=encoder_hid_dim_type, addition_embed_type=addition_embed_type, addition_time_embed_dim=addition_time_embed_dim,
        transformer_layers_per_block=transformer_layers_per_block, in_channels=unet.config.in_channels, flip_sin_to_cos=unet.config.flip_sin_to_cos, freq_shift=unet.config.freq_shift,
        down_block_types=unet.config.down_block_types, only_cross_attention=unet.config.only_cross_attention, block_out_channels=unet.config.block_out_channels, layers_per_block=unet.config.layers_per_block,
        downsample_padding=unet.config.downsample_padding, mid_block_scale_factor=unet.config.mid_block_scale_factor, act_fn=unet.config.act_fn, norm_num_groups=unet.config.norm_num_groups,
        norm_eps=unet.config.norm_eps, cross_attention_dim=unet.config.cross_attention_dim, attention_head_dim=unet.config.attention_head_dim, num_attention_heads=unet.config.num_attention_heads,
        use_linear_projection=unet.config.use_linear_projection, class_embed_type=unet.config.class_embed_type, num_class_embeds=unet.config.num_class_embeds, upcast_attention=unet.config.upcast_attention,
        resnet_time_scale_shift=unet.config.resnet_time_scale_shift, projection_class_embeddings_input_dim=unet.config.projection_class_embeddings_input_dim,
        controlnet_conditioning_channel_order=controlnet_conditioning_channel_order, conditioning_embedding_out_channels=conditioning_embedding_out_channels)
        if load_weights_from_unet:
            controlnet.conv_in.load_state_dict(unet.conv_in.state_dict())
            controlnet.time_proj.load_state_dict(unet.time_proj.state_dict())
            controlnet.time_embedding.load_state_dict(unet.time_embedding.state_dict())
            if controlnet.class_embedding: controlnet.class_embedding.load_state_dict(unet.class_embedding.state_dict())
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
        if isinstance(module, (CrossAttnDownBlock2D, DownBlock2D)): module.gradient_checkpointing = value
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, controlnet_cond: List[torch.Tensor], control_type: torch.Tensor, control_type_idx: List[int],
    conditioning_scale: float=1.0, class_labels: Optional[torch.Tensor]=None, timestep_cond: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, guess_mode: bool=False, return_dict: bool=True) -> Union[ControlNetOutput, Tuple[Tuple[torch.Tensor, ...], torch.Tensor]]:
        """Returns:"""
        channel_order = self.config.controlnet_conditioning_channel_order
        if channel_order != 'rgb': raise ValueError(f'unknown `controlnet_conditioning_channel_order`: {channel_order}')
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
        aug_emb = None
        if self.class_embedding is not None:
            if class_labels is None: raise ValueError('class_labels should be provided when num_class_embeds > 0')
            if self.config.class_embed_type == 'timestep': class_labels = self.time_proj(class_labels)
            class_emb = self.class_embedding(class_labels).to(dtype=self.dtype)
            emb = emb + class_emb
        if self.config.addition_embed_type is not None:
            if self.config.addition_embed_type == 'text': aug_emb = self.add_embedding(encoder_hidden_states)
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
        control_embeds = self.control_type_proj(control_type.flatten())
        control_embeds = control_embeds.reshape((t_emb.shape[0], -1))
        control_embeds = control_embeds.to(emb.dtype)
        control_emb = self.control_add_embedding(control_embeds)
        emb = emb + control_emb
        emb = emb + aug_emb if aug_emb is not None else emb
        sample = self.conv_in(sample)
        inputs = []
        condition_list = []
        for cond, control_idx in zip(controlnet_cond, control_type_idx):
            condition = self.controlnet_cond_embedding(cond)
            feat_seq = torch.mean(condition, dim=(2, 3))
            feat_seq = feat_seq + self.task_embedding[control_idx]
            inputs.append(feat_seq.unsqueeze(1))
            condition_list.append(condition)
        condition = sample
        feat_seq = torch.mean(condition, dim=(2, 3))
        inputs.append(feat_seq.unsqueeze(1))
        condition_list.append(condition)
        x = torch.cat(inputs, dim=1)
        for layer in self.transformer_layes: x = layer(x)
        controlnet_cond_fuser = sample * 0.0
        for idx, condition in enumerate(condition_list[:-1]):
            alpha = self.spatial_ch_projs(x[:, idx])
            alpha = alpha.unsqueeze(-1).unsqueeze(-1)
            controlnet_cond_fuser += condition + alpha
        sample = sample + controlnet_cond_fuser
        down_block_res_samples = (sample,)
        for downsample_block in self.down_blocks:
            if hasattr(downsample_block, 'has_cross_attention') and downsample_block.has_cross_attention: sample, res_samples = downsample_block(hidden_states=sample, temb=emb, encoder_hidden_states=encoder_hidden_states,
            attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs)
            else: sample, res_samples = downsample_block(hidden_states=sample, temb=emb)
            down_block_res_samples += res_samples
        if self.mid_block is not None: sample = self.mid_block(sample, emb, encoder_hidden_states=encoder_hidden_states, attention_mask=attention_mask, cross_attention_kwargs=cross_attention_kwargs)
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
        return ControlNetOutput(down_block_res_samples=down_block_res_samples, mid_block_res_sample=mid_block_res_sample)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
