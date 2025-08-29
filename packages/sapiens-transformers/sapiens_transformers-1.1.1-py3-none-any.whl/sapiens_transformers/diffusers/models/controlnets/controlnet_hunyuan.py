'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..embeddings import HunyuanCombinedTimestepTextSizeStyleEmbedding, PatchEmbed, PixArtAlphaTextProjection
from ...configuration_utils import ConfigMixin, register_to_config
from ..sapiens_transformers.hunyuan_transformer_2d import HunyuanDiTBlock
from ..attention_processor import AttentionProcessor
from .controlnet import Tuple, zero_module
from ...utils import BaseOutput
from typing import Dict, Optional, Union
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
from torch import nn
import torch
@dataclass
class HunyuanControlNetOutput(BaseOutput): controlnet_block_samples: Tuple[torch.Tensor]
class HunyuanDiT2DControlNetModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, conditioning_channels: int=3, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, patch_size: Optional[int]=None,
    activation_fn: str='gelu-approximate', sample_size=32, hidden_size=1152, transformer_num_layers: int=40, mlp_ratio: float=4.0, cross_attention_dim: int=1024, cross_attention_dim_t5: int=2048,
    pooled_projection_dim: int=1024, text_len: int=77, text_len_t5: int=256, use_style_cond_and_image_meta_size: bool=True):
        super().__init__()
        self.num_heads = num_attention_heads
        self.inner_dim = num_attention_heads * attention_head_dim
        self.text_embedder = PixArtAlphaTextProjection(in_features=cross_attention_dim_t5, hidden_size=cross_attention_dim_t5 * 4, out_features=cross_attention_dim, act_fn='silu_fp32')
        self.text_embedding_padding = nn.Parameter(torch.randn(text_len + text_len_t5, cross_attention_dim, dtype=torch.float32))
        self.pos_embed = PatchEmbed(height=sample_size, width=sample_size, in_channels=in_channels, embed_dim=hidden_size, patch_size=patch_size, pos_embed_type=None)
        self.time_extra_emb = HunyuanCombinedTimestepTextSizeStyleEmbedding(hidden_size, pooled_projection_dim=pooled_projection_dim, seq_len=text_len_t5, cross_attention_dim=cross_attention_dim_t5,
        use_style_cond_and_image_meta_size=use_style_cond_and_image_meta_size)
        self.controlnet_blocks = nn.ModuleList([])
        self.blocks = nn.ModuleList([HunyuanDiTBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads, activation_fn=activation_fn, ff_inner_dim=int(self.inner_dim * mlp_ratio),
        cross_attention_dim=cross_attention_dim, qk_norm=True, skip=False) for layer in range(transformer_num_layers // 2 - 1)])
        self.input_block = zero_module(nn.Linear(hidden_size, hidden_size))
        for _ in range(len(self.blocks)):
            controlnet_block = nn.Linear(hidden_size, hidden_size)
            controlnet_block = zero_module(controlnet_block)
            self.controlnet_blocks.append(controlnet_block)
    @property
    def attn_processors(self) -> Dict[str, AttentionProcessor]:
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor(return_deprecated_lora=True)
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
    @classmethod
    def from_transformer(cls, transformer, conditioning_channels=3, transformer_num_layers=None, load_weights_from_transformer=True):
        config = transformer.config
        activation_fn = config.activation_fn
        attention_head_dim = config.attention_head_dim
        cross_attention_dim = config.cross_attention_dim
        cross_attention_dim_t5 = config.cross_attention_dim_t5
        hidden_size = config.hidden_size
        in_channels = config.in_channels
        mlp_ratio = config.mlp_ratio
        num_attention_heads = config.num_attention_heads
        patch_size = config.patch_size
        sample_size = config.sample_size
        text_len = config.text_len
        text_len_t5 = config.text_len_t5
        conditioning_channels = conditioning_channels
        transformer_num_layers = transformer_num_layers or config.transformer_num_layers
        controlnet = cls(conditioning_channels=conditioning_channels, transformer_num_layers=transformer_num_layers, activation_fn=activation_fn, attention_head_dim=attention_head_dim, cross_attention_dim=cross_attention_dim,
        cross_attention_dim_t5=cross_attention_dim_t5, hidden_size=hidden_size, in_channels=in_channels, mlp_ratio=mlp_ratio, num_attention_heads=num_attention_heads, patch_size=patch_size, sample_size=sample_size, text_len=text_len, text_len_t5=text_len_t5)
        if load_weights_from_transformer: key = controlnet.load_state_dict(transformer.state_dict(), strict=False)
        return controlnet
    def forward(self, hidden_states, timestep, controlnet_cond: torch.Tensor, conditioning_scale: float=1.0, encoder_hidden_states=None, text_embedding_mask=None, encoder_hidden_states_t5=None, text_embedding_mask_t5=None,
    image_meta_size=None, style=None, image_rotary_emb=None, return_dict=True):
        """Args:"""
        height, width = hidden_states.shape[-2:]
        hidden_states = self.pos_embed(hidden_states)
        hidden_states = hidden_states + self.input_block(self.pos_embed(controlnet_cond))
        temb = self.time_extra_emb(timestep, encoder_hidden_states_t5, image_meta_size, style, hidden_dtype=timestep.dtype)
        batch_size, sequence_length, _ = encoder_hidden_states_t5.shape
        encoder_hidden_states_t5 = self.text_embedder(encoder_hidden_states_t5.view(-1, encoder_hidden_states_t5.shape[-1]))
        encoder_hidden_states_t5 = encoder_hidden_states_t5.view(batch_size, sequence_length, -1)
        encoder_hidden_states = torch.cat([encoder_hidden_states, encoder_hidden_states_t5], dim=1)
        text_embedding_mask = torch.cat([text_embedding_mask, text_embedding_mask_t5], dim=-1)
        text_embedding_mask = text_embedding_mask.unsqueeze(2).bool()
        encoder_hidden_states = torch.where(text_embedding_mask, encoder_hidden_states, self.text_embedding_padding)
        block_res_samples = ()
        for layer, block in enumerate(self.blocks):
            hidden_states = block(hidden_states, temb=temb, encoder_hidden_states=encoder_hidden_states, image_rotary_emb=image_rotary_emb)
            block_res_samples = block_res_samples + (hidden_states,)
        controlnet_block_res_samples = ()
        for block_res_sample, controlnet_block in zip(block_res_samples, self.controlnet_blocks):
            block_res_sample = controlnet_block(block_res_sample)
            controlnet_block_res_samples = controlnet_block_res_samples + (block_res_sample,)
        controlnet_block_res_samples = [sample * conditioning_scale for sample in controlnet_block_res_samples]
        if not return_dict: return (controlnet_block_res_samples,)
        return HunyuanControlNetOutput(controlnet_block_samples=controlnet_block_res_samples)
class HunyuanDiT2DMultiControlNetModel(ModelMixin):
    """Args:"""
    def __init__(self, controlnets):
        super().__init__()
        self.nets = nn.ModuleList(controlnets)
    def forward(self, hidden_states, timestep, controlnet_cond: torch.Tensor, conditioning_scale: float=1.0, encoder_hidden_states=None, text_embedding_mask=None, encoder_hidden_states_t5=None, text_embedding_mask_t5=None,
    image_meta_size=None, style=None, image_rotary_emb=None, return_dict=True):
        """Args:"""
        for i, (image, scale, controlnet) in enumerate(zip(controlnet_cond, conditioning_scale, self.nets)):
            block_samples = controlnet(hidden_states=hidden_states, timestep=timestep, controlnet_cond=image, conditioning_scale=scale, encoder_hidden_states=encoder_hidden_states, text_embedding_mask=text_embedding_mask, encoder_hidden_states_t5=encoder_hidden_states_t5,
            text_embedding_mask_t5=text_embedding_mask_t5, image_meta_size=image_meta_size, style=style, image_rotary_emb=image_rotary_emb, return_dict=return_dict)
            if i == 0: control_block_samples = block_samples
            else:
                control_block_samples = [control_block_sample + block_sample for control_block_sample, block_sample in zip(control_block_samples[0], block_samples[0])]
                control_block_samples = (control_block_samples,)
        return control_block_samples
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
