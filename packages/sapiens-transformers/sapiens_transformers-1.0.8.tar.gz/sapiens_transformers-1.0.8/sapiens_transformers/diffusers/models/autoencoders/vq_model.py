'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..autoencoders.vae import Decoder, DecoderOutput, Encoder, VectorQuantizer
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from typing import Optional, Tuple, Union
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
from ...utils import BaseOutput
import torch.nn as nn
import torch
@dataclass
class VQEncoderOutput(BaseOutput):
    """Args:"""
    latents: torch.Tensor
class VQModel(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, in_channels: int=3, out_channels: int=3, down_block_types: Tuple[str, ...]=('DownEncoderBlock2D',), up_block_types: Tuple[str, ...]=('UpDecoderBlock2D',),
    block_out_channels: Tuple[int, ...]=(64,), layers_per_block: int=1, act_fn: str='silu', latent_channels: int=3, sample_size: int=32, num_vq_embeddings: int=256, norm_num_groups: int=32,
    vq_embed_dim: Optional[int]=None, scaling_factor: float=0.18215, norm_type: str='group', mid_block_add_attention=True, lookup_from_codebook=False, force_upcast=False):
        super().__init__()
        self.encoder = Encoder(in_channels=in_channels, out_channels=latent_channels, down_block_types=down_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block,
        act_fn=act_fn, norm_num_groups=norm_num_groups, double_z=False, mid_block_add_attention=mid_block_add_attention)
        vq_embed_dim = vq_embed_dim if vq_embed_dim is not None else latent_channels
        self.quant_conv = nn.Conv2d(latent_channels, vq_embed_dim, 1)
        self.quantize = VectorQuantizer(num_vq_embeddings, vq_embed_dim, beta=0.25, remap=None, sane_index_shape=False)
        self.post_quant_conv = nn.Conv2d(vq_embed_dim, latent_channels, 1)
        self.decoder = Decoder(in_channels=latent_channels, out_channels=out_channels, up_block_types=up_block_types, block_out_channels=block_out_channels, layers_per_block=layers_per_block,
        act_fn=act_fn, norm_num_groups=norm_num_groups, norm_type=norm_type, mid_block_add_attention=mid_block_add_attention)
    @apply_forward_hook
    def encode(self, x: torch.Tensor, return_dict: bool=True) -> VQEncoderOutput:
        h = self.encoder(x)
        h = self.quant_conv(h)
        if not return_dict: return (h,)
        return VQEncoderOutput(latents=h)
    @apply_forward_hook
    def decode(self, h: torch.Tensor, force_not_quantize: bool=False, return_dict: bool=True, shape=None) -> Union[DecoderOutput, torch.Tensor]:
        if not force_not_quantize: quant, commit_loss, _ = self.quantize(h)
        elif self.config.lookup_from_codebook:
            quant = self.quantize.get_codebook_entry(h, shape)
            commit_loss = torch.zeros(h.shape[0]).to(h.device, dtype=h.dtype)
        else:
            quant = h
            commit_loss = torch.zeros(h.shape[0]).to(h.device, dtype=h.dtype)
        quant2 = self.post_quant_conv(quant)
        dec = self.decoder(quant2, quant if self.config.norm_type == 'spatial' else None)
        if not return_dict: return (dec, commit_loss)
        return DecoderOutput(sample=dec, commit_loss=commit_loss)
    def forward(self, sample: torch.Tensor, return_dict: bool=True) -> Union[DecoderOutput, Tuple[torch.Tensor, ...]]:
        """Returns:"""
        h = self.encode(sample).latents
        dec = self.decode(h)
        if not return_dict: return (dec.sample, dec.commit_loss)
        return dec
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
