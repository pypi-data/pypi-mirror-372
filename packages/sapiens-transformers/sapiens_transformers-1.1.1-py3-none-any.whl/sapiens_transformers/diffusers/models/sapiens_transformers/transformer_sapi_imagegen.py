'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.attention_processor import Attention, AttentionProcessor, FusedJointAttnProcessor2_0, JointAttnProcessor2_0
from ...utils import USE_PEFT_BACKEND, is_torch_version, scale_lora_layers, unscale_lora_layers
from ...loaders import FromOriginalModelMixin, PeftAdapterMixin, SAPITransformer2DLoadersMixin
from ...models.normalization import AdaLayerNormContinuous, AdaLayerNormZero
from ..embeddings import CombinedTimestepTextProjEmbeddings, PatchEmbed
from ...models.attention import FeedForward, JointTransformerBlock
from ...configuration_utils import ConfigMixin, register_to_config
from typing import Any, Dict, List, Optional, Tuple, Union
from ..modeling_outputs import Transformer2DModelOutput
from ...utils.torch_utils import maybe_allow_in_graph
from ...models.modeling_utils import ModelMixin
import torch.nn.functional as F
import torch.nn as nn
import torch
@maybe_allow_in_graph
class SAPISingleTransformerBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, attention_head_dim: int):
        super().__init__()
        self.norm1 = AdaLayerNormZero(dim)
        if hasattr(F, 'scaled_dot_product_attention'): processor = JointAttnProcessor2_0()
        else: raise ValueError('The current PyTorch version does not support the `scaled_dot_product_attention` function.')
        self.attn = Attention(query_dim=dim, dim_head=attention_head_dim, heads=num_attention_heads, out_dim=dim, bias=True, processor=processor, eps=1e-06)
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-06)
        self.ff = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
    def forward(self, hidden_states: torch.Tensor, temb: torch.Tensor):
        norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.norm1(hidden_states, emb=temb)
        attn_output = self.attn(hidden_states=norm_hidden_states, encoder_hidden_states=None)
        attn_output = gate_msa.unsqueeze(1) * attn_output
        hidden_states = hidden_states + attn_output
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        ff_output = self.ff(norm_hidden_states)
        ff_output = gate_mlp.unsqueeze(1) * ff_output
        hidden_states = hidden_states + ff_output
        return hidden_states
class SAPITransformer2DModel(ModelMixin, ConfigMixin, PeftAdapterMixin, FromOriginalModelMixin, SAPITransformer2DLoadersMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: int=128, patch_size: int=2, in_channels: int=16, num_layers: int=18, attention_head_dim: int=64, num_attention_heads: int=18, joint_attention_dim: int=4096,
    caption_projection_dim: int=1152, pooled_projection_dim: int=2048, out_channels: int=16, pos_embed_max_size: int=96, dual_attention_layers: Tuple[int, ...]=(), qk_norm: Optional[str]=None):
        super().__init__()
        default_out_channels = in_channels
        self.out_channels = out_channels if out_channels is not None else default_out_channels
        self.inner_dim = self.config.num_attention_heads * self.config.attention_head_dim
        self.pos_embed = PatchEmbed(height=self.config.sample_size, width=self.config.sample_size, patch_size=self.config.patch_size,
        in_channels=self.config.in_channels, embed_dim=self.inner_dim, pos_embed_max_size=pos_embed_max_size)
        self.time_text_embed = CombinedTimestepTextProjEmbeddings(embedding_dim=self.inner_dim, pooled_projection_dim=self.config.pooled_projection_dim)
        self.context_embedder = nn.Linear(self.config.joint_attention_dim, self.config.caption_projection_dim)
        self.transformer_blocks = nn.ModuleList([JointTransformerBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads,
        attention_head_dim=self.config.attention_head_dim, context_pre_only=i == num_layers - 1, qk_norm=qk_norm, use_dual_attention=True if i in dual_attention_layers else False) for i in range(self.config.num_layers)])
        self.norm_out = AdaLayerNormContinuous(self.inner_dim, self.inner_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * self.out_channels, bias=True)
        self.gradient_checkpointing = False
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
    def forward(self, hidden_states: torch.FloatTensor, encoder_hidden_states: torch.FloatTensor=None, pooled_projections: torch.FloatTensor=None, timestep: torch.LongTensor=None,
    block_controlnet_hidden_states: List=None, joint_attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True, skip_layers: Optional[List[int]]=None) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        """Returns:"""
        if joint_attention_kwargs is not None:
            joint_attention_kwargs = joint_attention_kwargs.copy()
            lora_scale = joint_attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        height, width = hidden_states.shape[-2:]
        hidden_states = self.pos_embed(hidden_states)
        temb = self.time_text_embed(timestep, pooled_projections)
        encoder_hidden_states = self.context_embedder(encoder_hidden_states)
        if joint_attention_kwargs is not None and 'ip_adapter_image_embeds' in joint_attention_kwargs:
            ip_adapter_image_embeds = joint_attention_kwargs.pop('ip_adapter_image_embeds')
            ip_hidden_states, ip_temb = self.image_proj(ip_adapter_image_embeds, timestep)
            joint_attention_kwargs.update(ip_hidden_states=ip_hidden_states, temb=ip_temb)
        for index_block, block in enumerate(self.transformer_blocks):
            is_skip = True if skip_layers is not None and index_block in skip_layers else False
            if torch.is_grad_enabled() and self.gradient_checkpointing and (not is_skip):
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                encoder_hidden_states, hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, temb, joint_attention_kwargs, **ckpt_kwargs)
            elif not is_skip: encoder_hidden_states, hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, temb=temb, joint_attention_kwargs=joint_attention_kwargs)
            if block_controlnet_hidden_states is not None and block.context_pre_only is False:
                interval_control = len(self.transformer_blocks) / len(block_controlnet_hidden_states)
                hidden_states = hidden_states + block_controlnet_hidden_states[int(index_block / interval_control)]
        hidden_states = self.norm_out(hidden_states, temb)
        hidden_states = self.proj_out(hidden_states)
        patch_size = self.config.patch_size
        height = height // patch_size
        width = width // patch_size
        hidden_states = hidden_states.reshape(shape=(hidden_states.shape[0], height, width, patch_size, patch_size, self.out_channels))
        hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(hidden_states.shape[0], self.out_channels, height * patch_size, width * patch_size))
        if USE_PEFT_BACKEND: unscale_lora_layers(self, lora_scale)
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
