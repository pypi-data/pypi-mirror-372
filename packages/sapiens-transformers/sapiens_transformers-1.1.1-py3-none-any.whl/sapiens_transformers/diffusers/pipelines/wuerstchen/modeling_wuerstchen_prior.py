'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from typing import Dict, Union
import torch
import torch.nn as nn
from ...configuration_utils import ConfigMixin, register_to_config
from ...loaders import PeftAdapterMixin, UNet2DConditionLoadersMixin
from ...models.attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from ...models.modeling_utils import ModelMixin
from ...utils import is_torch_version
from .modeling_wuerstchen_common import AttnBlock, ResBlock, TimestepBlock, WuerstchenLayerNorm
class WuerstchenPrior(ModelMixin, ConfigMixin, UNet2DConditionLoadersMixin, PeftAdapterMixin):
    unet_name = 'prior'
    _supports_gradient_checkpointing = True
    @register_to_config
    def __init__(self, c_in=16, c=1280, c_cond=1024, c_r=64, depth=16, nhead=16, dropout=0.1):
        super().__init__()
        self.c_r = c_r
        self.projection = nn.Conv2d(c_in, c, kernel_size=1)
        self.cond_mapper = nn.Sequential(nn.Linear(c_cond, c), nn.LeakyReLU(0.2), nn.Linear(c, c))
        self.blocks = nn.ModuleList()
        for _ in range(depth):
            self.blocks.append(ResBlock(c, dropout=dropout))
            self.blocks.append(TimestepBlock(c, c_r))
            self.blocks.append(AttnBlock(c, c, nhead, self_attn=True, dropout=dropout))
        self.out = nn.Sequential(WuerstchenLayerNorm(c, elementwise_affine=False, eps=1e-06), nn.Conv2d(c, c_in * 2, kernel_size=1))
        self.gradient_checkpointing = False
        self.set_default_attn_processor()
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
    def _set_gradient_checkpointing(self, module, value=False): self.gradient_checkpointing = value
    def gen_r_embedding(self, r, max_positions=10000):
        r = r * max_positions
        half_dim = self.c_r // 2
        emb = math.log(max_positions) / (half_dim - 1)
        emb = torch.arange(half_dim, device=r.device).float().mul(-emb).exp()
        emb = r[:, None] * emb[None, :]
        emb = torch.cat([emb.sin(), emb.cos()], dim=1)
        if self.c_r % 2 == 1: emb = nn.functional.pad(emb, (0, 1), mode='constant')
        return emb.to(dtype=r.dtype)
    def forward(self, x, r, c):
        x_in = x
        x = self.projection(x)
        c_embed = self.cond_mapper(c)
        r_embed = self.gen_r_embedding(r)
        if torch.is_grad_enabled() and self.gradient_checkpointing:
            def create_custom_forward(module):
                def custom_forward(*inputs): return module(*inputs)
                return custom_forward
            if is_torch_version('>=', '1.11.0'):
                for block in self.blocks:
                    if isinstance(block, AttnBlock): x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x, c_embed, use_reentrant=False)
                    elif isinstance(block, TimestepBlock): x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x, r_embed, use_reentrant=False)
                    else: x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x, use_reentrant=False)
            else:
                for block in self.blocks:
                    if isinstance(block, AttnBlock): x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x, c_embed)
                    elif isinstance(block, TimestepBlock): x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x, r_embed)
                    else: x = torch.utils.checkpoint.checkpoint(create_custom_forward(block), x)
        else:
            for block in self.blocks:
                if isinstance(block, AttnBlock): x = block(x, c_embed)
                elif isinstance(block, TimestepBlock): x = block(x, r_embed)
                else: x = block(x)
        a, b = self.out(x).chunk(2, dim=1)
        return (x_in - a) / ((1 - b).abs() + 1e-05)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
