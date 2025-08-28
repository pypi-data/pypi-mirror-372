'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.attention_processor import Attention, AttentionProcessor, StableAudioAttnProcessor2_0
from ...models.sapiens_transformers.transformer_2d import Transformer2DModelOutput
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.torch_utils import maybe_allow_in_graph
from ...models.modeling_utils import ModelMixin
from ...utils import is_torch_version
from typing import Any, Dict, Optional, Union
from ...models.attention import FeedForward
import torch.utils.checkpoint
import torch.nn as nn
import numpy as np
import torch
class StableAudioGaussianFourierProjection(nn.Module):
    def __init__(self, embedding_size: int=256, scale: float=1.0, set_W_to_weight=True, log=True, flip_sin_to_cos=False):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(embedding_size) * scale, requires_grad=False)
        self.log = log
        self.flip_sin_to_cos = flip_sin_to_cos
        if set_W_to_weight:
            del self.weight
            self.W = nn.Parameter(torch.randn(embedding_size) * scale, requires_grad=False)
            self.weight = self.W
            del self.W
    def forward(self, x):
        if self.log: x = torch.log(x)
        x_proj = 2 * np.pi * x[:, None] @ self.weight[None, :]
        if self.flip_sin_to_cos: out = torch.cat([torch.cos(x_proj), torch.sin(x_proj)], dim=-1)
        else: out = torch.cat([torch.sin(x_proj), torch.cos(x_proj)], dim=-1)
        return out
@maybe_allow_in_graph
class StableAudioDiTBlock(nn.Module):
    def __init__(self, dim: int, num_attention_heads: int, num_key_value_attention_heads: int, attention_head_dim: int, dropout=0.0, cross_attention_dim: Optional[int]=None,
    upcast_attention: bool=False, norm_eps: float=1e-05, ff_inner_dim: Optional[int]=None):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=True, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=False,
        upcast_attention=upcast_attention, out_bias=False, processor=StableAudioAttnProcessor2_0())
        self.norm2 = nn.LayerNorm(dim, norm_eps, True)
        self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim, heads=num_attention_heads, dim_head=attention_head_dim, kv_heads=num_key_value_attention_heads,
        dropout=dropout, bias=False, upcast_attention=upcast_attention, out_bias=False, processor=StableAudioAttnProcessor2_0())
        self.norm3 = nn.LayerNorm(dim, norm_eps, True)
        self.ff = FeedForward(dim, dropout=dropout, activation_fn='swiglu', final_dropout=False, inner_dim=ff_inner_dim, bias=True)
        self._chunk_size = None
        self._chunk_dim = 0
    def set_chunk_feed_forward(self, chunk_size: Optional[int], dim: int=0):
        self._chunk_size = chunk_size
        self._chunk_dim = dim
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, encoder_attention_mask: Optional[torch.Tensor]=None,
    rotary_embedding: Optional[torch.FloatTensor]=None) -> torch.Tensor:
        norm_hidden_states = self.norm1(hidden_states)
        attn_output = self.attn1(norm_hidden_states, attention_mask=attention_mask, rotary_emb=rotary_embedding)
        hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm2(hidden_states)
        attn_output = self.attn2(norm_hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask)
        hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm3(hidden_states)
        ff_output = self.ff(norm_hidden_states)
        hidden_states = ff_output + hidden_states
        return hidden_states
class StableAudioDiTModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, sample_size: int=1024, in_channels: int=64, num_layers: int=24, attention_head_dim: int=64, num_attention_heads: int=24, num_key_value_attention_heads: int=12,
    out_channels: int=64, cross_attention_dim: int=768, time_proj_dim: int=256, global_states_input_dim: int=1536, cross_attention_input_dim: int=768):
        super().__init__()
        self.sample_size = sample_size
        self.out_channels = out_channels
        self.inner_dim = num_attention_heads * attention_head_dim
        self.time_proj = StableAudioGaussianFourierProjection(embedding_size=time_proj_dim // 2, flip_sin_to_cos=True, log=False, set_W_to_weight=False)
        self.timestep_proj = nn.Sequential(nn.Linear(time_proj_dim, self.inner_dim, bias=True), nn.SiLU(), nn.Linear(self.inner_dim, self.inner_dim, bias=True))
        self.global_proj = nn.Sequential(nn.Linear(global_states_input_dim, self.inner_dim, bias=False), nn.SiLU(), nn.Linear(self.inner_dim, self.inner_dim, bias=False))
        self.cross_attention_proj = nn.Sequential(nn.Linear(cross_attention_input_dim, cross_attention_dim, bias=False), nn.SiLU(), nn.Linear(cross_attention_dim, cross_attention_dim, bias=False))
        self.preprocess_conv = nn.Conv1d(in_channels, in_channels, 1, bias=False)
        self.proj_in = nn.Linear(in_channels, self.inner_dim, bias=False)
        self.transformer_blocks = nn.ModuleList([StableAudioDiTBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads, num_key_value_attention_heads=num_key_value_attention_heads,
        attention_head_dim=attention_head_dim, cross_attention_dim=cross_attention_dim) for i in range(num_layers)])
        self.proj_out = nn.Linear(self.inner_dim, self.out_channels, bias=False)
        self.postprocess_conv = nn.Conv1d(self.out_channels, self.out_channels, 1, bias=False)
        self.gradient_checkpointing = False
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
    def set_default_attn_processor(self): self.set_attn_processor(StableAudioAttnProcessor2_0())
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, hidden_states: torch.FloatTensor, timestep: torch.LongTensor=None, encoder_hidden_states: torch.FloatTensor=None, global_hidden_states: torch.FloatTensor=None,
    rotary_embedding: torch.FloatTensor=None, return_dict: bool=True, attention_mask: Optional[torch.LongTensor]=None,
    encoder_attention_mask: Optional[torch.LongTensor]=None) -> Union[torch.FloatTensor, Transformer2DModelOutput]:
        """Returns:"""
        cross_attention_hidden_states = self.cross_attention_proj(encoder_hidden_states)
        global_hidden_states = self.global_proj(global_hidden_states)
        time_hidden_states = self.timestep_proj(self.time_proj(timestep.to(self.dtype)))
        global_hidden_states = global_hidden_states + time_hidden_states.unsqueeze(1)
        hidden_states = self.preprocess_conv(hidden_states) + hidden_states
        hidden_states = hidden_states.transpose(1, 2)
        hidden_states = self.proj_in(hidden_states)
        hidden_states = torch.cat([global_hidden_states, hidden_states], dim=-2)
        if attention_mask is not None:
            prepend_mask = torch.ones((hidden_states.shape[0], 1), device=hidden_states.device, dtype=torch.bool)
            attention_mask = torch.cat([prepend_mask, attention_mask], dim=-1)
        for block in self.transformer_blocks:
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, attention_mask,
                cross_attention_hidden_states, encoder_attention_mask, rotary_embedding, **ckpt_kwargs)
            else: hidden_states = block(hidden_states=hidden_states, attention_mask=attention_mask, encoder_hidden_states=cross_attention_hidden_states,
            encoder_attention_mask=encoder_attention_mask, rotary_embedding=rotary_embedding)
        hidden_states = self.proj_out(hidden_states)
        hidden_states = hidden_states.transpose(1, 2)[:, :, 1:]
        hidden_states = self.postprocess_conv(hidden_states) + hidden_states
        if not return_dict: return (hidden_states,)
        return Transformer2DModelOutput(sample=hidden_states)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
