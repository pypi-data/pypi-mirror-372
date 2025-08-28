'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from ..modeling_outputs import Transformer2DModelOutput
from ...utils import is_torch_version
from ..attention import BasicTransformerBlock
from ..modeling_utils import ModelMixin
from typing import Any, Dict, Optional
from ..embeddings import PatchEmbed
import torch.nn.functional as F
from torch import nn
import torch
class DiTTransformer2DModel(ModelMixin, ConfigMixin):
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=72, in_channels: int=4, out_channels: Optional[int]=None, num_layers: int=28, dropout: float=0.0,
    norm_num_groups: int=32, attention_bias: bool=True, sample_size: int=32, patch_size: int=2, activation_fn: str='gelu-approximate', num_embeds_ada_norm: Optional[int]=1000,
    upcast_attention: bool=False, norm_type: str='ada_norm_zero', norm_elementwise_affine: bool=False, norm_eps: float=1e-05):
        super().__init__()
        if norm_type != 'ada_norm_zero': raise NotImplementedError(f"Forward pass is not implemented when `patch_size` is not None and `norm_type` is '{norm_type}'.")
        elif norm_type == 'ada_norm_zero' and num_embeds_ada_norm is None: raise ValueError(f'When using a `patch_size` and this `norm_type` ({norm_type}), `num_embeds_ada_norm` cannot be None.')
        self.attention_head_dim = attention_head_dim
        self.inner_dim = self.config.num_attention_heads * self.config.attention_head_dim
        self.out_channels = in_channels if out_channels is None else out_channels
        self.gradient_checkpointing = False
        self.height = self.config.sample_size
        self.width = self.config.sample_size
        self.patch_size = self.config.patch_size
        self.pos_embed = PatchEmbed(height=self.config.sample_size, width=self.config.sample_size, patch_size=self.config.patch_size, in_channels=self.config.in_channels, embed_dim=self.inner_dim)
        self.transformer_blocks = nn.ModuleList([BasicTransformerBlock(self.inner_dim, self.config.num_attention_heads, self.config.attention_head_dim, dropout=self.config.dropout,
        activation_fn=self.config.activation_fn, num_embeds_ada_norm=self.config.num_embeds_ada_norm, attention_bias=self.config.attention_bias, upcast_attention=self.config.upcast_attention,
        norm_type=norm_type, norm_elementwise_affine=self.config.norm_elementwise_affine, norm_eps=self.config.norm_eps) for _ in range(self.config.num_layers)])
        self.norm_out = nn.LayerNorm(self.inner_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out_1 = nn.Linear(self.inner_dim, 2 * self.inner_dim)
        self.proj_out_2 = nn.Linear(self.inner_dim, self.config.patch_size * self.config.patch_size * self.out_channels)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, hidden_states: torch.Tensor, timestep: Optional[torch.LongTensor]=None, class_labels: Optional[torch.LongTensor]=None, cross_attention_kwargs: Dict[str, Any]=None, return_dict: bool=True):
        """Returns:"""
        height, width = (hidden_states.shape[-2] // self.patch_size, hidden_states.shape[-1] // self.patch_size)
        hidden_states = self.pos_embed(hidden_states)
        for block in self.transformer_blocks:
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module, return_dict=None):
                    def custom_forward(*inputs):
                        if return_dict is not None: return module(*inputs, return_dict=return_dict)
                        else: return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, None, None, None, timestep, cross_attention_kwargs, class_labels, **ckpt_kwargs)
            else: hidden_states = block(hidden_states, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, timestep=timestep, cross_attention_kwargs=cross_attention_kwargs, class_labels=class_labels)
        conditioning = self.transformer_blocks[0].norm1.emb(timestep, class_labels, hidden_dtype=hidden_states.dtype)
        shift, scale = self.proj_out_1(F.silu(conditioning)).chunk(2, dim=1)
        hidden_states = self.norm_out(hidden_states) * (1 + scale[:, None]) + shift[:, None]
        hidden_states = self.proj_out_2(hidden_states)
        height = width = int(hidden_states.shape[1] ** 0.5)
        hidden_states = hidden_states.reshape(shape=(-1, height, width, self.patch_size, self.patch_size, self.out_channels))
        hidden_states = torch.einsum('nhwpqc->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(-1, self.out_channels, height * self.patch_size, width * self.patch_size))
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
