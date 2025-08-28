'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Optional, Union
import torch
from torch import nn
from ...configuration_utils import ConfigMixin, register_to_config
from ...models.modeling_utils import ModelMixin
class StableUnCLIPImageNormalizer(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, embedding_dim: int=768):
        super().__init__()
        self.mean = nn.Parameter(torch.zeros(1, embedding_dim))
        self.std = nn.Parameter(torch.ones(1, embedding_dim))
    def to(self, torch_device: Optional[Union[str, torch.device]]=None, torch_dtype: Optional[torch.dtype]=None):
        self.mean = nn.Parameter(self.mean.to(torch_device).to(torch_dtype))
        self.std = nn.Parameter(self.std.to(torch_device).to(torch_dtype))
        return self
    def scale(self, embeds):
        embeds = (embeds - self.mean) * 1.0 / self.std
        return embeds
    def unscale(self, embeds):
        embeds = embeds * self.std + self.mean
        return embeds
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
