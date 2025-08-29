'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import importlib
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
import torch
from huggingface_hub.utils import validate_hf_hub_args
from ..utils import BaseOutput, PushToHubMixin
SCHEDULER_CONFIG_NAME = 'scheduler_config.json'
class KarrasDiffusionSchedulers(Enum):
    DDIMScheduler = 1
    DDPMScheduler = 2
    PNDMScheduler = 3
    LMSDiscreteScheduler = 4
    EulerDiscreteScheduler = 5
    HeunDiscreteScheduler = 6
    EulerAncestralDiscreteScheduler = 7
    DPMSolverMultistepScheduler = 8
    DPMSolverSinglestepScheduler = 9
    KDPM2DiscreteScheduler = 10
    KDPM2AncestralDiscreteScheduler = 11
    DEISMultistepScheduler = 12
    UniPCMultistepScheduler = 13
    DPMSolverSDEScheduler = 14
    EDMEulerScheduler = 15
AysSchedules = {'StableDiffusionTimesteps': [999, 850, 736, 645, 545, 455, 343, 233, 124, 24], 'StableDiffusionSigmas': [14.615, 6.475, 3.861, 2.697, 1.886, 1.396, 0.963, 0.652, 0.399,
0.152, 0.0], 'StableDiffusionXLTimesteps': [999, 845, 730, 587, 443, 310, 193, 116, 53, 13], 'StableDiffusionXLSigmas': [14.615, 6.315, 3.771, 2.181, 1.342, 0.862, 0.555, 0.38, 0.234,
0.113, 0.0], 'StableDiffusionVideoSigmas': [700.0, 54.5, 15.886, 7.977, 4.248, 1.789, 0.981, 0.403, 0.173, 0.034, 0.0]}
@dataclass
class SchedulerOutput(BaseOutput):
    """Args:"""
    prev_sample: torch.Tensor
class SchedulerMixin(PushToHubMixin):
    config_name = SCHEDULER_CONFIG_NAME
    _compatibles = []
    has_compatibles = True
    @classmethod
    @validate_hf_hub_args
    def from_pretrained(cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]]=None, subfolder: Optional[str]=None, return_unused_kwargs=False, **kwargs):
        config, kwargs, commit_hash = cls.load_config(pretrained_model_name_or_path=pretrained_model_name_or_path, subfolder=subfolder, return_unused_kwargs=True, return_commit_hash=True, **kwargs)
        return cls.from_config(config, return_unused_kwargs=return_unused_kwargs, **kwargs)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool=False, **kwargs):
        """Args:"""
        self.save_config(save_directory=save_directory, push_to_hub=push_to_hub, **kwargs)
    @property
    def compatibles(self):
        """Returns:"""
        return self._get_compatibles()
    @classmethod
    def _get_compatibles(cls):
        compatible_classes_str = list(set([cls.__name__] + cls._compatibles))
        diffusers_library = importlib.import_module(__name__.split('.')[0])
        compatible_classes = [getattr(diffusers_library, c) for c in compatible_classes_str if hasattr(diffusers_library, c)]
        return compatible_classes
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
