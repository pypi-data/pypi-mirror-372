'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..embeddings import CombinedTimestepGuidanceTextProjEmbeddings, CombinedTimestepTextProjEmbeddings, FluxPosEmbed
from ...utils import USE_PEFT_BACKEND, BaseOutput, is_torch_version, scale_lora_layers, unscale_lora_layers
from ..sapiens_transformers.transformer_flux import FluxSingleTransformerBlock, FluxTransformerBlock
from ..controlnets.controlnet import ControlNetConditioningEmbedding, zero_module
from ...configuration_utils import ConfigMixin, register_to_config
from ...models.attention_processor import AttentionProcessor
from typing import Any, Dict, List, Optional, Tuple, Union
from ..modeling_outputs import Transformer2DModelOutput
from ...models.modeling_utils import ModelMixin
from ...loaders import PeftAdapterMixin
from dataclasses import dataclass
import torch.nn as nn
import torch
@dataclass
class FluxControlNetOutput(BaseOutput):
    controlnet_block_samples: Tuple[torch.Tensor]
    controlnet_single_block_samples: Tuple[torch.Tensor]
class FluxControlNetModel(ModelMixin, ConfigMixin, PeftAdapterMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, patch_size: int=1, in_channels: int=64, num_layers: int=19, num_single_layers: int=38, attention_head_dim: int=128, num_attention_heads: int=24, joint_attention_dim: int=4096,
    pooled_projection_dim: int=768, guidance_embeds: bool=False, axes_dims_rope: List[int]=[16, 56, 56], num_mode: int=None, conditioning_embedding_channels: int=None):
        super().__init__()
        self.out_channels = in_channels
        self.inner_dim = num_attention_heads * attention_head_dim
        self.pos_embed = FluxPosEmbed(theta=10000, axes_dim=axes_dims_rope)
        text_time_guidance_cls = CombinedTimestepGuidanceTextProjEmbeddings if guidance_embeds else CombinedTimestepTextProjEmbeddings
        self.time_text_embed = text_time_guidance_cls(embedding_dim=self.inner_dim, pooled_projection_dim=pooled_projection_dim)
        self.context_embedder = nn.Linear(joint_attention_dim, self.inner_dim)
        self.x_embedder = torch.nn.Linear(in_channels, self.inner_dim)
        self.transformer_blocks = nn.ModuleList([FluxTransformerBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads, attention_head_dim=attention_head_dim) for i in range(num_layers)])
        self.single_transformer_blocks = nn.ModuleList([FluxSingleTransformerBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads, attention_head_dim=attention_head_dim) for i in range(num_single_layers)])
        self.controlnet_blocks = nn.ModuleList([])
        for _ in range(len(self.transformer_blocks)): self.controlnet_blocks.append(zero_module(nn.Linear(self.inner_dim, self.inner_dim)))
        self.controlnet_single_blocks = nn.ModuleList([])
        for _ in range(len(self.single_transformer_blocks)): self.controlnet_single_blocks.append(zero_module(nn.Linear(self.inner_dim, self.inner_dim)))
        self.union = num_mode is not None
        if self.union: self.controlnet_mode_embedder = nn.Embedding(num_mode, self.inner_dim)
        if conditioning_embedding_channels is not None:
            self.input_hint_block = ControlNetConditioningEmbedding(conditioning_embedding_channels=conditioning_embedding_channels, block_out_channels=(16, 16, 16, 16))
            self.controlnet_x_embedder = torch.nn.Linear(in_channels, self.inner_dim)
        else:
            self.input_hint_block = None
            self.controlnet_x_embedder = zero_module(torch.nn.Linear(in_channels, self.inner_dim))
        self.gradient_checkpointing = False
    @property
    def attn_processors(self):
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor()
            for sub_name, child in module.named_children(): fn_recursive_add_processors(f'{name}.{sub_name}', child, processors)
            return processors
        for name, module in self.named_children(): fn_recursive_add_processors(name, module, processors)
        return processors
    def set_attn_processor(self, processor):
        count = len(self.attn_processors.keys())
        if isinstance(processor, dict) and len(processor) != count:
            raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict):
                    module.set_processor(processor)
                else:
                    module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    @classmethod
    def from_transformer(cls, transformer, num_layers: int=4, num_single_layers: int=10, attention_head_dim: int=128, num_attention_heads: int=24, load_weights_from_transformer=True):
        config = dict(transformer.config)
        config['num_layers'] = num_layers
        config['num_single_layers'] = num_single_layers
        config['attention_head_dim'] = attention_head_dim
        config['num_attention_heads'] = num_attention_heads
        controlnet = cls.from_config(config)
        if load_weights_from_transformer:
            controlnet.pos_embed.load_state_dict(transformer.pos_embed.state_dict())
            controlnet.time_text_embed.load_state_dict(transformer.time_text_embed.state_dict())
            controlnet.context_embedder.load_state_dict(transformer.context_embedder.state_dict())
            controlnet.x_embedder.load_state_dict(transformer.x_embedder.state_dict())
            controlnet.transformer_blocks.load_state_dict(transformer.transformer_blocks.state_dict(), strict=False)
            controlnet.single_transformer_blocks.load_state_dict(transformer.single_transformer_blocks.state_dict(), strict=False)
            controlnet.controlnet_x_embedder = zero_module(controlnet.controlnet_x_embedder)
        return controlnet
    def forward(self, hidden_states: torch.Tensor, controlnet_cond: torch.Tensor, controlnet_mode: torch.Tensor=None, conditioning_scale: float=1.0, encoder_hidden_states: torch.Tensor=None,
    pooled_projections: torch.Tensor=None, timestep: torch.LongTensor=None, img_ids: torch.Tensor=None, txt_ids: torch.Tensor=None, guidance: torch.Tensor=None, joint_attention_kwargs: Optional[Dict[str, Any]]=None,
    return_dict: bool=True) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        """Returns:"""
        if joint_attention_kwargs is not None:
            joint_attention_kwargs = joint_attention_kwargs.copy()
            lora_scale = joint_attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        hidden_states = self.x_embedder(hidden_states)
        if self.input_hint_block is not None:
            controlnet_cond = self.input_hint_block(controlnet_cond)
            batch_size, channels, height_pw, width_pw = controlnet_cond.shape
            height = height_pw // self.config.patch_size
            width = width_pw // self.config.patch_size
            controlnet_cond = controlnet_cond.reshape(batch_size, channels, height, self.config.patch_size, width, self.config.patch_size)
            controlnet_cond = controlnet_cond.permute(0, 2, 4, 1, 3, 5)
            controlnet_cond = controlnet_cond.reshape(batch_size, height * width, -1)
        hidden_states = hidden_states + self.controlnet_x_embedder(controlnet_cond)
        timestep = timestep.to(hidden_states.dtype) * 1000
        if guidance is not None: guidance = guidance.to(hidden_states.dtype) * 1000
        else: guidance = None
        temb = self.time_text_embed(timestep, pooled_projections) if guidance is None else self.time_text_embed(timestep, guidance, pooled_projections)
        encoder_hidden_states = self.context_embedder(encoder_hidden_states)
        if self.union:
            if controlnet_mode is None:
                raise ValueError('`controlnet_mode` cannot be `None` when applying ControlNet-Union')
            controlnet_mode_emb = self.controlnet_mode_embedder(controlnet_mode)
            encoder_hidden_states = torch.cat([controlnet_mode_emb, encoder_hidden_states], dim=1)
            txt_ids = torch.cat([txt_ids[:1], txt_ids], dim=0)
        if txt_ids.ndim == 3: txt_ids = txt_ids[0]
        if img_ids.ndim == 3: img_ids = img_ids[0]
        ids = torch.cat((txt_ids, img_ids), dim=0)
        image_rotary_emb = self.pos_embed(ids)
        block_samples = ()
        for index_block, block in enumerate(self.transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                encoder_hidden_states, hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, temb, image_rotary_emb, **ckpt_kwargs)
            else: encoder_hidden_states, hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=temb, image_rotary_emb=image_rotary_emb)
            block_samples = block_samples + (hidden_states,)
        hidden_states = torch.cat([encoder_hidden_states, hidden_states], dim=1)
        single_block_samples = ()
        for index_block, block in enumerate(self.single_transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, temb, image_rotary_emb, **ckpt_kwargs)
            else: hidden_states = block(hidden_states=hidden_states, temb=temb, image_rotary_emb=image_rotary_emb)
            single_block_samples = single_block_samples + (hidden_states[:, encoder_hidden_states.shape[1]:],)
        controlnet_block_samples = ()
        for block_sample, controlnet_block in zip(block_samples, self.controlnet_blocks):
            block_sample = controlnet_block(block_sample)
            controlnet_block_samples = controlnet_block_samples + (block_sample,)
        controlnet_single_block_samples = ()
        for single_block_sample, controlnet_block in zip(single_block_samples, self.controlnet_single_blocks):
            single_block_sample = controlnet_block(single_block_sample)
            controlnet_single_block_samples = controlnet_single_block_samples + (single_block_sample,)
        controlnet_block_samples = [sample * conditioning_scale for sample in controlnet_block_samples]
        controlnet_single_block_samples = [sample * conditioning_scale for sample in controlnet_single_block_samples]
        controlnet_block_samples = None if len(controlnet_block_samples) == 0 else controlnet_block_samples
        controlnet_single_block_samples = None if len(controlnet_single_block_samples) == 0 else controlnet_single_block_samples
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (controlnet_block_samples, controlnet_single_block_samples)
        return FluxControlNetOutput(controlnet_block_samples=controlnet_block_samples, controlnet_single_block_samples=controlnet_single_block_samples)
class FluxMultiControlNetModel(ModelMixin):
    """Args:"""
    def __init__(self, controlnets):
        super().__init__()
        self.nets = nn.ModuleList(controlnets)
    def forward(self, hidden_states: torch.FloatTensor, controlnet_cond: List[torch.tensor], controlnet_mode: List[torch.tensor], conditioning_scale: List[float], encoder_hidden_states: torch.Tensor=None,
    pooled_projections: torch.Tensor=None, timestep: torch.LongTensor=None, img_ids: torch.Tensor=None, txt_ids: torch.Tensor=None, guidance: torch.Tensor=None,
    joint_attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True) -> Union[FluxControlNetOutput, Tuple]:
        if len(self.nets) == 1 and self.nets[0].union:
            controlnet = self.nets[0]
            for i, (image, mode, scale) in enumerate(zip(controlnet_cond, controlnet_mode, conditioning_scale)):
                block_samples, single_block_samples = controlnet(hidden_states=hidden_states, controlnet_cond=image, controlnet_mode=mode[:, None], conditioning_scale=scale,
                timestep=timestep, guidance=guidance, pooled_projections=pooled_projections, encoder_hidden_states=encoder_hidden_states, txt_ids=txt_ids,
                img_ids=img_ids, joint_attention_kwargs=joint_attention_kwargs, return_dict=return_dict)
                if i == 0:
                    control_block_samples = block_samples
                    control_single_block_samples = single_block_samples
                else:
                    control_block_samples = [control_block_sample + block_sample for control_block_sample, block_sample in zip(control_block_samples, block_samples)]
                    control_single_block_samples = [control_single_block_sample + block_sample for control_single_block_sample, block_sample in zip(control_single_block_samples, single_block_samples)]
        else:
            for i, (image, mode, scale, controlnet) in enumerate(zip(controlnet_cond, controlnet_mode, conditioning_scale, self.nets)):
                block_samples, single_block_samples = controlnet(hidden_states=hidden_states, controlnet_cond=image, controlnet_mode=mode[:, None], conditioning_scale=scale,
                timestep=timestep, guidance=guidance, pooled_projections=pooled_projections, encoder_hidden_states=encoder_hidden_states, txt_ids=txt_ids, img_ids=img_ids,
                joint_attention_kwargs=joint_attention_kwargs, return_dict=return_dict)
                if i == 0:
                    control_block_samples = block_samples
                    control_single_block_samples = single_block_samples
                else:
                    if block_samples is not None and control_block_samples is not None:
                        control_block_samples = [control_block_sample + block_sample for control_block_sample, block_sample in zip(control_block_samples, block_samples)]
                    if single_block_samples is not None and control_single_block_samples is not None:
                        control_single_block_samples = [control_single_block_sample + block_sample for control_single_block_sample, block_sample in zip(control_single_block_samples, single_block_samples)]
        return (control_block_samples, control_single_block_samples)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
