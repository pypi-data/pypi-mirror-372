'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...configuration_utils import ConfigMixin, register_to_config
from ...models.modeling_utils import ModelMixin
from ...utils import SapiensTechnologyOutput
from dataclasses import dataclass
from typing import Optional
import torch.nn as nn
import torch
@dataclass
class ReduxImageEncoderOutput(SapiensTechnologyOutput):
    image_embeds: Optional[torch.Tensor] = None
class ReduxImageEncoder(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, redux_dim: int=1152, txt_in_features: int=4096) -> None:
        super().__init__()
        self.redux_up = nn.Linear(redux_dim, txt_in_features * 3)
        self.redux_down = nn.Linear(txt_in_features * 3, txt_in_features)
    def forward(self, x: torch.Tensor) -> ReduxImageEncoderOutput:
        projected_x = self.redux_down(nn.functional.silu(self.redux_up(x)))
        return ReduxImageEncoderOutput(image_embeds=projected_x)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
