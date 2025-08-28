'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from .vae import DecoderOutput, DiagonalGaussianDistribution, Encoder
from ...configuration_utils import ConfigMixin, register_to_config
from ...utils.sapiens_accelerator_utils import apply_forward_hook
from ...schedulers import ConsistencyDecoderScheduler
from typing import Dict, Optional, Tuple, Union
from ...utils.torch_utils import randn_tensor
from ..modeling_utils import ModelMixin
from ..unets.unet_2d import UNet2DModel
from dataclasses import dataclass
import torch.nn.functional as F
from ...utils import BaseOutput
from torch import nn
import torch
@dataclass
class ConsistencyDecoderVAEOutput(BaseOutput):
    """Args:"""
    latent_dist: 'DiagonalGaussianDistribution'
class ConsistencyDecoderVAE(ModelMixin, ConfigMixin):
    """Examples:"""
    @register_to_config
    def __init__(self, scaling_factor: float=0.18215, latent_channels: int=4, sample_size: int=32, encoder_act_fn: str='silu', encoder_block_out_channels: Tuple[int, ...]=(128, 256, 512, 512),
    encoder_double_z: bool=True, encoder_down_block_types: Tuple[str, ...]=('DownEncoderBlock2D', 'DownEncoderBlock2D', 'DownEncoderBlock2D', 'DownEncoderBlock2D'), encoder_in_channels: int=3,
    encoder_layers_per_block: int=2, encoder_norm_num_groups: int=32, encoder_out_channels: int=4, decoder_add_attention: bool=False, decoder_block_out_channels: Tuple[int, ...]=(320, 640, 1024, 1024),
    decoder_down_block_types: Tuple[str, ...]=('ResnetDownsampleBlock2D', 'ResnetDownsampleBlock2D', 'ResnetDownsampleBlock2D', 'ResnetDownsampleBlock2D'), decoder_downsample_padding: int=1,
    decoder_in_channels: int=7, decoder_layers_per_block: int=3, decoder_norm_eps: float=1e-05, decoder_norm_num_groups: int=32, decoder_num_train_timesteps: int=1024, decoder_out_channels: int=6,
    decoder_resnet_time_scale_shift: str='scale_shift', decoder_time_embedding_type: str='learned',
    decoder_up_block_types: Tuple[str, ...]=('ResnetUpsampleBlock2D', 'ResnetUpsampleBlock2D', 'ResnetUpsampleBlock2D', 'ResnetUpsampleBlock2D')):
        super().__init__()
        self.encoder = Encoder(act_fn=encoder_act_fn, block_out_channels=encoder_block_out_channels, double_z=encoder_double_z, down_block_types=encoder_down_block_types, in_channels=encoder_in_channels,
        layers_per_block=encoder_layers_per_block, norm_num_groups=encoder_norm_num_groups, out_channels=encoder_out_channels)
        self.decoder_unet = UNet2DModel(add_attention=decoder_add_attention, block_out_channels=decoder_block_out_channels, down_block_types=decoder_down_block_types,
        downsample_padding=decoder_downsample_padding, in_channels=decoder_in_channels, layers_per_block=decoder_layers_per_block, norm_eps=decoder_norm_eps,
        norm_num_groups=decoder_norm_num_groups, num_train_timesteps=decoder_num_train_timesteps, out_channels=decoder_out_channels, resnet_time_scale_shift=decoder_resnet_time_scale_shift,
        time_embedding_type=decoder_time_embedding_type, up_block_types=decoder_up_block_types)
        self.decoder_scheduler = ConsistencyDecoderScheduler()
        self.register_to_config(block_out_channels=encoder_block_out_channels)
        self.register_to_config(force_upcast=False)
        self.register_buffer('means', torch.tensor([0.38862467, 0.02253063, 0.07381133, -0.0171294])[None, :, None, None], persistent=False)
        self.register_buffer('stds', torch.tensor([0.9654121, 1.0440036, 0.76147926, 0.77022034])[None, :, None, None], persistent=False)
        self.quant_conv = nn.Conv2d(2 * latent_channels, 2 * latent_channels, 1)
        self.use_slicing = False
        self.use_tiling = False
        self.tile_sample_min_size = self.config.sample_size
        sample_size = self.config.sample_size[0] if isinstance(self.config.sample_size, (list, tuple)) else self.config.sample_size
        self.tile_latent_min_size = int(sample_size / 2 ** (len(self.config.block_out_channels) - 1))
        self.tile_overlap_factor = 0.25
    def enable_tiling(self, use_tiling: bool=True): self.use_tiling = use_tiling
    def disable_tiling(self): self.enable_tiling(False)
    def enable_slicing(self): self.use_slicing = True
    def disable_slicing(self): self.use_slicing = False
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
    def set_default_attn_processor(self):
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    @apply_forward_hook
    def encode(self, x: torch.Tensor, return_dict: bool=True) -> Union[ConsistencyDecoderVAEOutput, Tuple[DiagonalGaussianDistribution]]:
        """Returns:"""
        if self.use_tiling and (x.shape[-1] > self.tile_sample_min_size or x.shape[-2] > self.tile_sample_min_size): return self.tiled_encode(x, return_dict=return_dict)
        if self.use_slicing and x.shape[0] > 1:
            encoded_slices = [self.encoder(x_slice) for x_slice in x.split(1)]
            h = torch.cat(encoded_slices)
        else: h = self.encoder(x)
        moments = self.quant_conv(h)
        posterior = DiagonalGaussianDistribution(moments)
        if not return_dict: return (posterior,)
        return ConsistencyDecoderVAEOutput(latent_dist=posterior)
    @apply_forward_hook
    def decode(self, z: torch.Tensor, generator: Optional[torch.Generator]=None, return_dict: bool=True, num_inference_steps: int=2) -> Union[DecoderOutput, Tuple[torch.Tensor]]:
        """Returns:"""
        z = (z * self.config.scaling_factor - self.means) / self.stds
        scale_factor = 2 ** (len(self.config.block_out_channels) - 1)
        z = F.interpolate(z, mode='nearest', scale_factor=scale_factor)
        batch_size, _, height, width = z.shape
        self.decoder_scheduler.set_timesteps(num_inference_steps, device=self.device)
        x_t = self.decoder_scheduler.init_noise_sigma * randn_tensor((batch_size, 3, height, width), generator=generator, dtype=z.dtype, device=z.device)
        for t in self.decoder_scheduler.timesteps:
            model_input = torch.concat([self.decoder_scheduler.scale_model_input(x_t, t), z], dim=1)
            model_output = self.decoder_unet(model_input, t).sample[:, :3, :, :]
            prev_sample = self.decoder_scheduler.step(model_output, t, x_t, generator).prev_sample
            x_t = prev_sample
        x_0 = x_t
        if not return_dict: return (x_0,)
        return DecoderOutput(sample=x_0)
    def blend_v(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[2], b.shape[2], blend_extent)
        for y in range(blend_extent): b[:, :, y, :] = a[:, :, -blend_extent + y, :] * (1 - y / blend_extent) + b[:, :, y, :] * (y / blend_extent)
        return b
    def blend_h(self, a: torch.Tensor, b: torch.Tensor, blend_extent: int) -> torch.Tensor:
        blend_extent = min(a.shape[3], b.shape[3], blend_extent)
        for x in range(blend_extent): b[:, :, :, x] = a[:, :, :, -blend_extent + x] * (1 - x / blend_extent) + b[:, :, :, x] * (x / blend_extent)
        return b
    def tiled_encode(self, x: torch.Tensor, return_dict: bool=True) -> Union[ConsistencyDecoderVAEOutput, Tuple]:
        """Returns:"""
        overlap_size = int(self.tile_sample_min_size * (1 - self.tile_overlap_factor))
        blend_extent = int(self.tile_latent_min_size * self.tile_overlap_factor)
        row_limit = self.tile_latent_min_size - blend_extent
        rows = []
        for i in range(0, x.shape[2], overlap_size):
            row = []
            for j in range(0, x.shape[3], overlap_size):
                tile = x[:, :, i:i + self.tile_sample_min_size, j:j + self.tile_sample_min_size]
                tile = self.encoder(tile)
                tile = self.quant_conv(tile)
                row.append(tile)
            rows.append(row)
        result_rows = []
        for i, row in enumerate(rows):
            result_row = []
            for j, tile in enumerate(row):
                if i > 0: tile = self.blend_v(rows[i - 1][j], tile, blend_extent)
                if j > 0: tile = self.blend_h(row[j - 1], tile, blend_extent)
                result_row.append(tile[:, :, :row_limit, :row_limit])
            result_rows.append(torch.cat(result_row, dim=3))
        moments = torch.cat(result_rows, dim=2)
        posterior = DiagonalGaussianDistribution(moments)
        if not return_dict: return (posterior,)
        return ConsistencyDecoderVAEOutput(latent_dist=posterior)
    def forward(self, sample: torch.Tensor, sample_posterior: bool=False, return_dict: bool=True, generator: Optional[torch.Generator]=None) -> Union[DecoderOutput, Tuple[torch.Tensor]]:
        """Returns:"""
        x = sample
        posterior = self.encode(x).latent_dist
        if sample_posterior: z = posterior.sample(generator=generator)
        else: z = posterior.mode()
        dec = self.decode(z, generator=generator).sample
        if not return_dict: return (dec,)
        return DecoderOutput(sample=dec)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
