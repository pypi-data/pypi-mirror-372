'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import Attention, AttentionProcessor, FusedHunyuanAttnProcessor2_0, HunyuanAttnProcessor2_0
from ..embeddings import HunyuanCombinedTimestepTextSizeStyleEmbedding, PatchEmbed, PixArtAlphaTextProjection
from ...configuration_utils import ConfigMixin, register_to_config
from ..normalization import AdaLayerNormContinuous, FP32LayerNorm
from ..modeling_outputs import Transformer2DModelOutput
from ...utils.torch_utils import maybe_allow_in_graph
from typing import Dict, Optional, Union
from ..modeling_utils import ModelMixin
from ..attention import FeedForward
from torch import nn
import torch
class AdaLayerNormShift(nn.Module):
    def __init__(self, embedding_dim: int, elementwise_affine=True, eps=1e-06):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(embedding_dim, embedding_dim)
        self.norm = FP32LayerNorm(embedding_dim, elementwise_affine=elementwise_affine, eps=eps)
    def forward(self, x: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        shift = self.linear(self.silu(emb.to(torch.float32)).to(emb.dtype))
        x = self.norm(x) + shift.unsqueeze(dim=1)
        return x
@maybe_allow_in_graph
class HunyuanDiTBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, cross_attention_dim: int=1024, dropout=0.0, activation_fn: str='geglu', norm_elementwise_affine: bool=True, norm_eps: float=1e-06,
    final_dropout: bool=False, ff_inner_dim: Optional[int]=None, ff_bias: bool=True, skip: bool=False, qk_norm: bool=True):
        super().__init__()
        self.norm1 = AdaLayerNormShift(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, cross_attention_dim=None, dim_head=dim // num_attention_heads, heads=num_attention_heads,
        qk_norm='layer_norm' if qk_norm else None, eps=1e-06, bias=True, processor=HunyuanAttnProcessor2_0())
        self.norm2 = FP32LayerNorm(dim, norm_eps, norm_elementwise_affine)
        self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim, dim_head=dim // num_attention_heads, heads=num_attention_heads,
        qk_norm='layer_norm' if qk_norm else None, eps=1e-06, bias=True, processor=HunyuanAttnProcessor2_0())
        self.norm3 = FP32LayerNorm(dim, norm_eps, norm_elementwise_affine)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn=activation_fn, final_dropout=final_dropout, inner_dim=ff_inner_dim, bias=ff_bias)
        if skip:
            self.skip_norm = FP32LayerNorm(2 * dim, norm_eps, elementwise_affine=True)
            self.skip_linear = nn.Linear(2 * dim, dim)
        else: self.skip_linear = None
        self._chunk_size = None
        self._chunk_dim = 0
    def set_chunk_feed_forward(self, chunk_size: Optional[int], dim: int=0):
        self._chunk_size = chunk_size
        self._chunk_dim = dim
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: Optional[torch.Tensor]=None, temb: Optional[torch.Tensor]=None, image_rotary_emb=None, skip=None) -> torch.Tensor:
        if self.skip_linear is not None:
            cat = torch.cat([hidden_states, skip], dim=-1)
            cat = self.skip_norm(cat)
            hidden_states = self.skip_linear(cat)
        norm_hidden_states = self.norm1(hidden_states, temb)
        attn_output = self.attn1(norm_hidden_states, image_rotary_emb=image_rotary_emb)
        hidden_states = hidden_states + attn_output
        hidden_states = hidden_states + self.attn2(self.norm2(hidden_states), encoder_hidden_states=encoder_hidden_states, image_rotary_emb=image_rotary_emb)
        mlp_inputs = self.norm3(hidden_states)
        hidden_states = hidden_states + self.ff(mlp_inputs)
        return hidden_states
class HunyuanDiT2DModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, patch_size: Optional[int]=None, activation_fn: str='gelu-approximate',
    sample_size=32, hidden_size=1152, num_layers: int=28, mlp_ratio: float=4.0, learn_sigma: bool=True, cross_attention_dim: int=1024, norm_type: str='layer_norm', cross_attention_dim_t5: int=2048,
    pooled_projection_dim: int=1024, text_len: int=77, text_len_t5: int=256, use_style_cond_and_image_meta_size: bool=True):
        super().__init__()
        self.out_channels = in_channels * 2 if learn_sigma else in_channels
        self.num_heads = num_attention_heads
        self.inner_dim = num_attention_heads * attention_head_dim
        self.text_embedder = PixArtAlphaTextProjection(in_features=cross_attention_dim_t5, hidden_size=cross_attention_dim_t5 * 4, out_features=cross_attention_dim, act_fn='silu_fp32')
        self.text_embedding_padding = nn.Parameter(torch.randn(text_len + text_len_t5, cross_attention_dim, dtype=torch.float32))
        self.pos_embed = PatchEmbed(height=sample_size, width=sample_size, in_channels=in_channels, embed_dim=hidden_size, patch_size=patch_size, pos_embed_type=None)
        self.time_extra_emb = HunyuanCombinedTimestepTextSizeStyleEmbedding(hidden_size, pooled_projection_dim=pooled_projection_dim, seq_len=text_len_t5,
        cross_attention_dim=cross_attention_dim_t5, use_style_cond_and_image_meta_size=use_style_cond_and_image_meta_size)
        self.blocks = nn.ModuleList([HunyuanDiTBlock(dim=self.inner_dim, num_attention_heads=self.config.num_attention_heads, activation_fn=activation_fn, ff_inner_dim=int(self.inner_dim * mlp_ratio),
        cross_attention_dim=cross_attention_dim, qk_norm=True, skip=layer > num_layers // 2) for layer in range(num_layers)])
        self.norm_out = AdaLayerNormContinuous(self.inner_dim, self.inner_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * self.out_channels, bias=True)
    def fuse_qkv_projections(self):
        self.original_attn_processors = None
        for _, attn_processor in self.attn_processors.items():
            if 'Added' in str(attn_processor.__class__.__name__): raise ValueError('`fuse_qkv_projections()` is not supported for models having added KV projections.')
        self.original_attn_processors = self.attn_processors
        for module in self.modules():
            if isinstance(module, Attention): module.fuse_projections(fuse=True)
        self.set_attn_processor(FusedHunyuanAttnProcessor2_0())
    def unfuse_qkv_projections(self):
        if self.original_attn_processors is not None: self.set_attn_processor(self.original_attn_processors)
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
    def set_default_attn_processor(self): self.set_attn_processor(HunyuanAttnProcessor2_0())
    def forward(self, hidden_states, timestep, encoder_hidden_states=None, text_embedding_mask=None, encoder_hidden_states_t5=None, text_embedding_mask_t5=None, image_meta_size=None,
    style=None, image_rotary_emb=None, controlnet_block_samples=None, return_dict=True):
        """Args:"""
        height, width = hidden_states.shape[-2:]
        hidden_states = self.pos_embed(hidden_states)
        temb = self.time_extra_emb(timestep, encoder_hidden_states_t5, image_meta_size, style, hidden_dtype=timestep.dtype)
        batch_size, sequence_length, _ = encoder_hidden_states_t5.shape
        encoder_hidden_states_t5 = self.text_embedder(encoder_hidden_states_t5.view(-1, encoder_hidden_states_t5.shape[-1]))
        encoder_hidden_states_t5 = encoder_hidden_states_t5.view(batch_size, sequence_length, -1)
        encoder_hidden_states = torch.cat([encoder_hidden_states, encoder_hidden_states_t5], dim=1)
        text_embedding_mask = torch.cat([text_embedding_mask, text_embedding_mask_t5], dim=-1)
        text_embedding_mask = text_embedding_mask.unsqueeze(2).bool()
        encoder_hidden_states = torch.where(text_embedding_mask, encoder_hidden_states, self.text_embedding_padding)
        skips = []
        for layer, block in enumerate(self.blocks):
            if layer > self.config.num_layers // 2:
                if controlnet_block_samples is not None: skip = skips.pop() + controlnet_block_samples.pop()
                else: skip = skips.pop()
                hidden_states = block(hidden_states, temb=temb, encoder_hidden_states=encoder_hidden_states, image_rotary_emb=image_rotary_emb, skip=skip)
            else: hidden_states = block(hidden_states, temb=temb, encoder_hidden_states=encoder_hidden_states, image_rotary_emb=image_rotary_emb)
            if layer < self.config.num_layers // 2 - 1: skips.append(hidden_states)
        if controlnet_block_samples is not None and len(controlnet_block_samples) != 0: raise ValueError('The number of controls is not equal to the number of skip connections.')
        hidden_states = self.norm_out(hidden_states, temb.to(torch.float32))
        hidden_states = self.proj_out(hidden_states)
        patch_size = self.pos_embed.patch_size
        height = height // patch_size
        width = width // patch_size
        hidden_states = hidden_states.reshape(shape=(hidden_states.shape[0], height, width, patch_size, patch_size, self.out_channels))
        hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(hidden_states.shape[0], self.out_channels, height * patch_size, width * patch_size))
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
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
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
