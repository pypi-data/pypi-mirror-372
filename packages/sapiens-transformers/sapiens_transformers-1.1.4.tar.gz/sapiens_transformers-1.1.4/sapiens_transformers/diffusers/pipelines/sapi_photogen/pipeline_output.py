'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import SapiensTechnologyOutput
from dataclasses import dataclass
from typing import List, Union
import numpy as np
import PIL.Image
import torch
@dataclass
class SAPIPhotoGenPipelineOutput(SapiensTechnologyOutput):
    """Args:"""
    images: Union[List[PIL.Image.Image], np.ndarray]
@dataclass
class SAPIPhotoGenPriorReduxPipelineOutput(SapiensTechnologyOutput):
    """Args:"""
    prompt_embeds: torch.Tensor
    pooled_prompt_embeds: torch.Tensor
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
