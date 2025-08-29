'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import USE_PEFT_BACKEND, is_torch_version, scale_lora_layers, unscale_lora_layers
from ..attention_processor import Attention, AttentionProcessor, FusedJointAttnProcessor2_0
from ..embeddings import CombinedTimestepTextProjEmbeddings, PatchEmbed
from ..sapiens_transformers.transformer_sapiens_imagegen import SAPISingleTransformerBlock
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders import FromOriginalModelMixin, PeftAdapterMixin
from typing import Any, Dict, List, Optional, Tuple, Union
from ..modeling_outputs import Transformer2DModelOutput
from .controlnet import BaseOutput, zero_module
from ..attention import JointTransformerBlock
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
import torch.nn as nn
import torch
@dataclass
class SAPIControlNetOutput(BaseOutput): controlnet_block_samples: Tuple[torch.Tensor]
class SAPIControlNetModel(ModelMixin, ConfigMixin, PeftAdapterMixin, FromOriginalModelMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: int=128, patch_size: int=2, in_channels: int=16, num_layers: int=18, attention_head_dim: int=64, num_attention_heads: int=18, joint_attention_dim: int=4096,
    caption_projection_dim: int=1152, pooled_projection_dim: int=2048, out_channels: int=16, pos_embed_max_size: int=96, extra_conditioning_channels: int=0, dual_attention_layers: Tuple[int, ...]=(),
    qk_norm: Optional[str]=None, pos_embed_type: Optional[str]='sincos', use_pos_embed: bool=True, force_zeros_for_pooled_projection: bool=True):
        super().__init__()
        default_out_channels = in_channels
        self.out_channels = out_channels if out_channels is not None else default_out_channels
        self.inner_dim = num_attention_heads * attention_head_dim
        if use_pos_embed: self.pos_embed = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels,
        embed_dim=self.inner_dim, pos_embed_max_size=pos_embed_max_size, pos_embed_type=pos_embed_type)
        else: self.pos_embed = None
        self.time_text_embed = CombinedTimestepTextProjEmbeddings(embedding_dim=self.inner_dim, pooled_projection_dim=pooled_projection_dim)
        if joint_attention_dim is not None:
            self.context_embedder = nn.Linear(joint_attention_dim, caption_projection_dim)
            self.transformer_blocks = nn.ModuleList([JointTransformerBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads, attention_head_dim=self.config.attention_head_dim,
            context_pre_only=False, qk_norm=qk_norm, use_dual_attention=True if i in dual_attention_layers else False) for i in range(num_layers)])
        else:
            self.context_embedder = None
            self.transformer_blocks = nn.ModuleList([SAPISingleTransformerBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads, attention_head_dim=self.config.attention_head_dim) for _ in range(num_layers)])
        self.controlnet_blocks = nn.ModuleList([])
        for _ in range(len(self.transformer_blocks)):
            controlnet_block = nn.Linear(self.inner_dim, self.inner_dim)
            controlnet_block = zero_module(controlnet_block)
            self.controlnet_blocks.append(controlnet_block)
        pos_embed_input = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels + extra_conditioning_channels, embed_dim=self.inner_dim, pos_embed_type=None)
        self.pos_embed_input = zero_module(pos_embed_input)
        self.gradient_checkpointing = False
    def enable_forward_chunking(self, chunk_size: Optional[int]=None, dim: int=0) -> None:
        if dim not in [0, 1]: raise ValueError(f'Make sure to set `dim` to either 0 or 1, not {dim}')
        chunk_size = chunk_size or 1
        def fn_recursive_feed_forward(module: torch.nn.Module, chunk_size: int, dim: int):
            if hasattr(module, 'set_chunk_feed_forward'): module.set_chunk_feed_forward(chunk_size=chunk_size, dim=dim)
            for child in module.children(): fn_recursive_feed_forward(child, chunk_size, dim)
        for module in self.children(): fn_recursive_feed_forward(module, chunk_size, dim)
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
        if isinstance(processor, dict) and len(processor) != count:
            raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def fuse_qkv_projections(self):
        self.original_attn_processors = None
        for _, attn_processor in self.attn_processors.items():
            if 'Added' in str(attn_processor.__class__.__name__): raise ValueError('`fuse_qkv_projections()` is not supported for models having added KV projections.')
        self.original_attn_processors = self.attn_processors
        for module in self.modules():
            if isinstance(module, Attention): module.fuse_projections(fuse=True)
        self.set_attn_processor(FusedJointAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def _get_pos_embed_from_transformer(self, transformer):
        pos_embed = PatchEmbed(height=transformer.config.sample_size, width=transformer.config.sample_size, patch_size=transformer.config.patch_size, in_channels=transformer.config.in_channels,
        embed_dim=transformer.inner_dim, pos_embed_max_size=transformer.config.pos_embed_max_size)
        pos_embed.load_state_dict(transformer.pos_embed.state_dict(), strict=True)
        return pos_embed
    @classmethod
    def from_transformer(cls, transformer, num_layers=12, num_extra_conditioning_channels=1, load_weights_from_transformer=True):
        config = transformer.config
        config['num_layers'] = num_layers or config.num_layers
        config['extra_conditioning_channels'] = num_extra_conditioning_channels
        controlnet = cls.from_config(config)
        if load_weights_from_transformer:
            controlnet.pos_embed.load_state_dict(transformer.pos_embed.state_dict())
            controlnet.time_text_embed.load_state_dict(transformer.time_text_embed.state_dict())
            controlnet.context_embedder.load_state_dict(transformer.context_embedder.state_dict())
            controlnet.transformer_blocks.load_state_dict(transformer.transformer_blocks.state_dict(), strict=False)
            controlnet.pos_embed_input = zero_module(controlnet.pos_embed_input)
        return controlnet
    def forward(self, hidden_states: torch.FloatTensor, controlnet_cond: torch.Tensor, conditioning_scale: float=1.0, encoder_hidden_states: torch.FloatTensor=None,
    pooled_projections: torch.FloatTensor=None, timestep: torch.LongTensor=None, joint_attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        """Returns:"""
        if joint_attention_kwargs is not None:
            joint_attention_kwargs = joint_attention_kwargs.copy()
            lora_scale = joint_attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        if self.pos_embed is not None and hidden_states.ndim != 4: raise ValueError('hidden_states must be 4D when pos_embed is used')
        elif self.pos_embed is None and hidden_states.ndim != 3: raise ValueError('hidden_states must be 3D when pos_embed is not used')
        if self.context_embedder is not None and encoder_hidden_states is None: raise ValueError('encoder_hidden_states must be provided when context_embedder is used')
        elif self.context_embedder is None and encoder_hidden_states is not None: raise ValueError('encoder_hidden_states should not be provided when context_embedder is not used')
        if self.pos_embed is not None: hidden_states = self.pos_embed(hidden_states)
        temb = self.time_text_embed(timestep, pooled_projections)
        if self.context_embedder is not None: encoder_hidden_states = self.context_embedder(encoder_hidden_states)
        hidden_states = hidden_states + self.pos_embed_input(controlnet_cond)
        block_res_samples = ()
        for block in self.transformer_blocks:
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                if self.context_embedder is not None: encoder_hidden_states, hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, temb, **ckpt_kwargs)
                else: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, temb, **ckpt_kwargs)
            elif self.context_embedder is not None: encoder_hidden_states, hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=temb)
            else: hidden_states = block(hidden_states, temb)
            block_res_samples = block_res_samples + (hidden_states,)
        controlnet_block_res_samples = ()
        for block_res_sample, controlnet_block in zip(block_res_samples, self.controlnet_blocks):
            block_res_sample = controlnet_block(block_res_sample)
            controlnet_block_res_samples = controlnet_block_res_samples + (block_res_sample,)
        controlnet_block_res_samples = [sample * conditioning_scale for sample in controlnet_block_res_samples]
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (controlnet_block_res_samples,)
        return SAPIControlNetOutput(controlnet_block_samples=controlnet_block_res_samples)
class SAPIMultiControlNetModel(ModelMixin):
    """Args:"""
    def __init__(self, controlnets):
        super().__init__()
        self.nets = nn.ModuleList(controlnets)
    def forward(self, hidden_states: torch.FloatTensor, controlnet_cond: List[torch.tensor], conditioning_scale: List[float], pooled_projections: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor=None,
    timestep: torch.LongTensor=None, joint_attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True) -> Union[SAPIControlNetOutput, Tuple]:
        for i, (image, scale, controlnet) in enumerate(zip(controlnet_cond, conditioning_scale, self.nets)):
            block_samples = controlnet(hidden_states=hidden_states, timestep=timestep, encoder_hidden_states=encoder_hidden_states, pooled_projections=pooled_projections, controlnet_cond=image, conditioning_scale=scale,
            joint_attention_kwargs=joint_attention_kwargs, return_dict=return_dict)
            if i == 0: control_block_samples = block_samples
            else:
                control_block_samples = [control_block_sample + block_sample for control_block_sample, block_sample in zip(control_block_samples[0], block_samples[0])]
                control_block_samples = (tuple(control_block_samples),)
        return control_block_samples
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
