'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.attention_processor import Attention, AttentionProcessor, CogVideoXAttnProcessor2_0
from ..embeddings import CogView3CombinedTimestepSizeEmbeddings, CogView3PlusPatchEmbed
from ...configuration_utils import ConfigMixin, register_to_config
from ..normalization import CogView3PlusAdaLayerNormZeroTextImage
from ...models.normalization import AdaLayerNormContinuous
from ..modeling_outputs import Transformer2DModelOutput
from ...models.modeling_utils import ModelMixin
from ...utils import is_torch_version
from ...models.attention import FeedForward
from typing import Any, Dict, Union
import torch.nn as nn
import torch
class CogView3PlusTransformerBlock(nn.Module):
    """Args:"""
    def __init__(self, dim: int=2560, num_attention_heads: int=64, attention_head_dim: int=40, time_embed_dim: int=512):
        super().__init__()
        self.norm1 = CogView3PlusAdaLayerNormZeroTextImage(embedding_dim=time_embed_dim, dim=dim)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, out_dim=dim, bias=True,
        qk_norm='layer_norm', elementwise_affine=False, eps=1e-06, processor=CogVideoXAttnProcessor2_0())
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-05)
        self.norm2_context = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-05)
        self.ff = FeedForward(dim=dim, dim_out=dim, activation_fn='gelu-approximate')
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        text_seq_length = encoder_hidden_states.size(1)
        norm_hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp, norm_encoder_hidden_states, c_gate_msa, c_shift_mlp,
        c_scale_mlp, c_gate_mlp = self.norm1(hidden_states, encoder_hidden_states, emb)
        attn_hidden_states, attn_encoder_hidden_states = self.attn1(hidden_states=norm_hidden_states, encoder_hidden_states=norm_encoder_hidden_states)
        hidden_states = hidden_states + gate_msa.unsqueeze(1) * attn_hidden_states
        encoder_hidden_states = encoder_hidden_states + c_gate_msa.unsqueeze(1) * attn_encoder_hidden_states
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        norm_encoder_hidden_states = self.norm2_context(encoder_hidden_states)
        norm_encoder_hidden_states = norm_encoder_hidden_states * (1 + c_scale_mlp[:, None]) + c_shift_mlp[:, None]
        norm_hidden_states = torch.cat([norm_encoder_hidden_states, norm_hidden_states], dim=1)
        ff_output = self.ff(norm_hidden_states)
        hidden_states = hidden_states + gate_mlp.unsqueeze(1) * ff_output[:, text_seq_length:]
        encoder_hidden_states = encoder_hidden_states + c_gate_mlp.unsqueeze(1) * ff_output[:, :text_seq_length]
        if hidden_states.dtype == torch.float16: hidden_states = hidden_states.clip(-65504, 65504)
        if encoder_hidden_states.dtype == torch.float16: encoder_hidden_states = encoder_hidden_states.clip(-65504, 65504)
        return (hidden_states, encoder_hidden_states)
class CogView3PlusTransformer2DModel(ModelMixin, ConfigMixin):
    """Args:"""
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, patch_size: int=2, in_channels: int=16, num_layers: int=30, attention_head_dim: int=40, num_attention_heads: int=64, out_channels: int=16, text_embed_dim: int=4096,
    time_embed_dim: int=512, condition_dim: int=256, pos_embed_max_size: int=128, sample_size: int=128):
        super().__init__()
        self.out_channels = out_channels
        self.inner_dim = num_attention_heads * attention_head_dim
        self.pooled_projection_dim = 3 * 2 * condition_dim
        self.patch_embed = CogView3PlusPatchEmbed(in_channels=in_channels, hidden_size=self.inner_dim, patch_size=patch_size, text_hidden_size=text_embed_dim, pos_embed_max_size=pos_embed_max_size)
        self.time_condition_embed = CogView3CombinedTimestepSizeEmbeddings(embedding_dim=time_embed_dim, condition_dim=condition_dim, pooled_projection_dim=self.pooled_projection_dim, timesteps_dim=self.inner_dim)
        self.transformer_blocks = nn.ModuleList([CogView3PlusTransformerBlock(dim=self.inner_dim, num_attention_heads=num_attention_heads,
        attention_head_dim=attention_head_dim, time_embed_dim=time_embed_dim) for _ in range(num_layers)])
        self.norm_out = AdaLayerNormContinuous(embedding_dim=self.inner_dim, conditioning_embedding_dim=time_embed_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out = nn.Linear(self.inner_dim, patch_size * patch_size * self.out_channels, bias=True)
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
        if isinstance(processor, dict) and len(processor) != count: raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor, timestep: torch.LongTensor, original_size: torch.Tensor, target_size: torch.Tensor, crop_coords: torch.Tensor,
    return_dict: bool=True) -> Union[torch.Tensor, Transformer2DModelOutput]:
        """Returns:"""
        height, width = hidden_states.shape[-2:]
        text_seq_length = encoder_hidden_states.shape[1]
        hidden_states = self.patch_embed(hidden_states, encoder_hidden_states)
        emb = self.time_condition_embed(timestep, original_size, target_size, crop_coords, hidden_states.dtype)
        encoder_hidden_states = hidden_states[:, :text_seq_length]
        hidden_states = hidden_states[:, text_seq_length:]
        for index_block, block in enumerate(self.transformer_blocks):
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs)
                    return custom_forward
                ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
                hidden_states, encoder_hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, encoder_hidden_states, emb, **ckpt_kwargs)
            else: hidden_states, encoder_hidden_states = block(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, emb=emb)
        hidden_states = self.norm_out(hidden_states, emb)
        hidden_states = self.proj_out(hidden_states)
        patch_size = self.config.patch_size
        height = height // patch_size
        width = width // patch_size
        hidden_states = hidden_states.reshape(shape=(hidden_states.shape[0], height, width, self.out_channels, patch_size, patch_size))
        hidden_states = torch.einsum('nhwcpq->nchpwq', hidden_states)
        output = hidden_states.reshape(shape=(hidden_states.shape[0], self.out_channels, height * patch_size, width * patch_size))
        if not return_dict: return (output,)
        return Transformer2DModelOutput(sample=output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
