'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import Attention, AttentionProcessor, AttnProcessor2_0, SapiensImageGenLinearAttnProcessor2_0
from ...utils import USE_PEFT_BACKEND, is_torch_version, scale_lora_layers, unscale_lora_layers
from ...configuration_utils import ConfigMixin, register_to_config
from ..embeddings import PatchEmbed, PixArtAlphaTextProjection
from ..normalization import AdaLayerNormSingle, RMSNorm
from ..modeling_outputs import Transformer2DModelOutput
from typing import Any, Dict, Optional, Tuple, Union
from ...loaders import PeftAdapterMixin
from ..modeling_utils import ModelMixin
from torch import nn
import torch
class GLUMBConv(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, expand_ratio: float=4, norm_type: Optional[str]=None, residual_connection: bool=True) -> None:
        super().__init__()
        hidden_channels = int(expand_ratio * in_channels)
        self.norm_type = norm_type
        self.residual_connection = residual_connection
        self.nonlinearity = nn.SiLU()
        self.conv_inverted = nn.Conv2d(in_channels, hidden_channels * 2, 1, 1, 0)
        self.conv_depth = nn.Conv2d(hidden_channels * 2, hidden_channels * 2, 3, 1, 1, groups=hidden_channels * 2)
        self.conv_point = nn.Conv2d(hidden_channels, out_channels, 1, 1, 0, bias=False)
        self.norm = None
        if norm_type == 'rms_norm': self.norm = RMSNorm(out_channels, eps=1e-05, elementwise_affine=True, bias=True)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if self.residual_connection: residual = hidden_states
        hidden_states = self.conv_inverted(hidden_states)
        hidden_states = self.nonlinearity(hidden_states)
        hidden_states = self.conv_depth(hidden_states)
        hidden_states, gate = torch.chunk(hidden_states, 2, dim=1)
        hidden_states = hidden_states * self.nonlinearity(gate)
        hidden_states = self.conv_point(hidden_states)
        if self.norm_type == 'rms_norm': hidden_states = self.norm(hidden_states.movedim(1, -1)).movedim(-1, 1)
        if self.residual_connection: hidden_states = hidden_states + residual
        return hidden_states
class SapiensImageGenTransformerBlock(nn.Module):
    def __init__(self, dim: int=2240, num_attention_heads: int=70, attention_head_dim: int=32, dropout: float=0.0, num_cross_attention_heads: Optional[int]=20,
    cross_attention_head_dim: Optional[int]=112, cross_attention_dim: Optional[int]=2240, attention_bias: bool=True,
    norm_elementwise_affine: bool=False, norm_eps: float=1e-06, attention_out_bias: bool=True, mlp_ratio: float=2.5) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=False, eps=norm_eps)
        self.attn1 = Attention(query_dim=dim, heads=num_attention_heads, dim_head=attention_head_dim, dropout=dropout, bias=attention_bias, cross_attention_dim=None, processor=SapiensImageGenLinearAttnProcessor2_0())
        if cross_attention_dim is not None:
            self.norm2 = nn.LayerNorm(dim, elementwise_affine=norm_elementwise_affine, eps=norm_eps)
            self.attn2 = Attention(query_dim=dim, cross_attention_dim=cross_attention_dim, heads=num_cross_attention_heads,
            dim_head=cross_attention_head_dim, dropout=dropout, bias=True, out_bias=attention_out_bias, processor=AttnProcessor2_0())
        self.ff = GLUMBConv(dim, dim, mlp_ratio, norm_type=None, residual_connection=False)
        self.scale_shift_table = nn.Parameter(torch.randn(6, dim) / dim ** 0.5)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None,
    encoder_attention_mask: Optional[torch.Tensor]=None, timestep: Optional[torch.LongTensor]=None, height: int=None, width: int=None) -> torch.Tensor:
        batch_size = hidden_states.shape[0]
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = (self.scale_shift_table[None] + timestep.reshape(batch_size, 6, -1)).chunk(6, dim=1)
        norm_hidden_states = self.norm1(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_msa) + shift_msa
        norm_hidden_states = norm_hidden_states.to(hidden_states.dtype)
        attn_output = self.attn1(norm_hidden_states)
        hidden_states = hidden_states + gate_msa * attn_output
        if self.attn2 is not None:
            attn_output = self.attn2(hidden_states, encoder_hidden_states=encoder_hidden_states, attention_mask=encoder_attention_mask)
            hidden_states = attn_output + hidden_states
        norm_hidden_states = self.norm2(hidden_states)
        norm_hidden_states = norm_hidden_states * (1 + scale_mlp) + shift_mlp
        norm_hidden_states = norm_hidden_states.unflatten(1, (height, width)).permute(0, 3, 1, 2)
        ff_output = self.ff(norm_hidden_states)
        ff_output = ff_output.flatten(2, 3).permute(0, 2, 1)
        hidden_states = hidden_states + gate_mlp * ff_output
        return hidden_states
class SapiensImageGenTransformer2DModel(ModelMixin, ConfigMixin, PeftAdapterMixin):
    """Args:"""
    _supports_gradient_checkpointing = True
    _no_split_modules = ['SapiensImageGenTransformerBlock', 'PatchEmbed']
    @register_to_config
    def __init__(self, in_channels: int=32, out_channels: Optional[int]=32, num_attention_heads: int=70, attention_head_dim: int=32, num_layers: int=20,
    num_cross_attention_heads: Optional[int]=20, cross_attention_head_dim: Optional[int]=112, cross_attention_dim: Optional[int]=2240, caption_channels: int=2304,
    mlp_ratio: float=2.5, dropout: float=0.0, attention_bias: bool=False, sample_size: int=32, patch_size: int=1, norm_elementwise_affine: bool=False,
    norm_eps: float=1e-06, interpolation_scale: Optional[int]=None) -> None:
        super().__init__()
        out_channels = out_channels or in_channels
        inner_dim = num_attention_heads * attention_head_dim
        interpolation_scale = interpolation_scale if interpolation_scale is not None else max(sample_size // 64, 1)
        self.patch_embed = PatchEmbed(height=sample_size, width=sample_size, patch_size=patch_size, in_channels=in_channels, embed_dim=inner_dim, interpolation_scale=interpolation_scale)
        self.time_embed = AdaLayerNormSingle(inner_dim)
        self.caption_projection = PixArtAlphaTextProjection(in_features=caption_channels, hidden_size=inner_dim)
        self.caption_norm = RMSNorm(inner_dim, eps=1e-05, elementwise_affine=True)
        self.transformer_blocks = nn.ModuleList([SapiensImageGenTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout,
        num_cross_attention_heads=num_cross_attention_heads, cross_attention_head_dim=cross_attention_head_dim, cross_attention_dim=cross_attention_dim,
        attention_bias=attention_bias, norm_elementwise_affine=norm_elementwise_affine, norm_eps=norm_eps, mlp_ratio=mlp_ratio) for _ in range(num_layers)])
        self.scale_shift_table = nn.Parameter(torch.randn(2, inner_dim) / inner_dim ** 0.5)
        self.norm_out = nn.LayerNorm(inner_dim, elementwise_affine=False, eps=1e-06)
        self.proj_out = nn.Linear(inner_dim, patch_size * patch_size * out_channels)
        self.gradient_checkpointing = False
    def _set_gradient_checkpointing(self, module, value=False):
        if hasattr(module, 'gradient_checkpointing'): module.gradient_checkpointing = value
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
    def forward(self, hidden_states: torch.Tensor, encoder_hidden_states: torch.Tensor, timestep: torch.LongTensor, encoder_attention_mask: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.Tensor]=None, attention_kwargs: Optional[Dict[str, Any]]=None, return_dict: bool=True) -> Union[Tuple[torch.Tensor, ...], Transformer2DModelOutput]:
        if attention_kwargs is not None:
            attention_kwargs = attention_kwargs.copy()
            lora_scale = attention_kwargs.pop('scale', 1.0)
        else: lora_scale = 1.0
        if USE_PEFT_BACKEND: scale_lora_layers(self, lora_scale)
        if attention_mask is not None and attention_mask.ndim == 2:
            attention_mask = (1 - attention_mask.to(hidden_states.dtype)) * -10000.0
            attention_mask = attention_mask.unsqueeze(1)
        if encoder_attention_mask is not None and encoder_attention_mask.ndim == 2:
            encoder_attention_mask = (1 - encoder_attention_mask.to(hidden_states.dtype)) * -10000.0
            encoder_attention_mask = encoder_attention_mask.unsqueeze(1)
        batch_size, num_channels, height, width = hidden_states.shape
        p = self.config.patch_size
        post_patch_height, post_patch_width = (height // p, width // p)
        hidden_states = self.patch_embed(hidden_states)
        timestep, embedded_timestep = self.time_embed(timestep, batch_size=batch_size, hidden_dtype=hidden_states.dtype)
        encoder_hidden_states = self.caption_projection(encoder_hidden_states)
        encoder_hidden_states = encoder_hidden_states.view(batch_size, -1, hidden_states.shape[-1])
        encoder_hidden_states = self.caption_norm(encoder_hidden_states)
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module, return_dict=None):
                def custom_forward(*inputs):
                    if return_dict is not None: return module(*inputs, return_dict=return_dict)
                    else: return module(*inputs)
                return custom_forward
            ckpt_kwargs: Dict[str, Any] = {'use_reentrant': False} if is_torch_version('>=', '1.11.0') else {}
            for block in self.transformer_blocks: hidden_states = torch.utils.checkpoint.checkpoint(create_custom_forward(block), hidden_states, attention_mask,
            encoder_hidden_states, encoder_attention_mask, timestep, post_patch_height, post_patch_width, **ckpt_kwargs)
        else:
            for block in self.transformer_blocks: hidden_states = block(hidden_states, attention_mask, encoder_hidden_states, encoder_attention_mask, timestep, post_patch_height, post_patch_width)
        shift, scale = (self.scale_shift_table[None] + embedded_timestep[:, None].to(self.scale_shift_table.device)).chunk(2, dim=1)
        hidden_states = self.norm_out(hidden_states)
        hidden_states = hidden_states * (1 + scale) + shift
        hidden_states = self.proj_out(hidden_states)
        hidden_states = hidden_states.reshape(batch_size, post_patch_height, post_patch_width, self.config.patch_size, self.config.patch_size, -1)
        hidden_states = hidden_states.permute(0, 5, 1, 3, 2, 4)
        output = hidden_states.reshape(batch_size, -1, post_patch_height * p, post_patch_width * p)
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
