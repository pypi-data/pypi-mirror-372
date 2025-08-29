'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...models.controlnets.controlnet import ControlNetModel, ControlNetOutput
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ...models.modeling_utils import ModelMixin
from torch import nn
import torch
import os
class MultiControlNetModel(ModelMixin):
    """Args:"""
    def __init__(self, controlnets: Union[List[ControlNetModel], Tuple[ControlNetModel]]):
        super().__init__()
        self.nets = nn.ModuleList(controlnets)
    def forward(self, sample: torch.Tensor, timestep: Union[torch.Tensor, float, int], encoder_hidden_states: torch.Tensor, controlnet_cond: List[torch.tensor], conditioning_scale: List[float], class_labels: Optional[torch.Tensor]=None, timestep_cond: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None, added_cond_kwargs: Optional[Dict[str, torch.Tensor]]=None, cross_attention_kwargs: Optional[Dict[str, Any]]=None, guess_mode: bool=False, return_dict: bool=True) -> Union[ControlNetOutput, Tuple]:
        for i, (image, scale, controlnet) in enumerate(zip(controlnet_cond, conditioning_scale, self.nets)):
            down_samples, mid_sample = controlnet(sample=sample, timestep=timestep, encoder_hidden_states=encoder_hidden_states, controlnet_cond=image, conditioning_scale=scale, class_labels=class_labels, timestep_cond=timestep_cond, attention_mask=attention_mask, added_cond_kwargs=added_cond_kwargs, cross_attention_kwargs=cross_attention_kwargs, guess_mode=guess_mode, return_dict=return_dict)
            if i == 0: down_block_res_samples, mid_block_res_sample = (down_samples, mid_sample)
            else:
                down_block_res_samples = [samples_prev + samples_curr for samples_prev, samples_curr in zip(down_block_res_samples, down_samples)]
                mid_block_res_sample += mid_sample
        return (down_block_res_samples, mid_block_res_sample)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], is_main_process: bool=True, save_function: Callable=None, safe_serialization: bool=True, variant: Optional[str]=None):
        for idx, controlnet in enumerate(self.nets):
            suffix = '' if idx == 0 else f'_{idx}'
            controlnet.save_pretrained(save_directory + suffix, is_main_process=is_main_process, save_function=save_function, safe_serialization=safe_serialization, variant=variant)
    @classmethod
    def from_pretrained(cls, pretrained_model_path: Optional[Union[str, os.PathLike]], **kwargs):
        idx = 0
        controlnets = []
        model_path_to_load = pretrained_model_path
        while os.path.isdir(model_path_to_load):
            controlnet = ControlNetModel.from_pretrained(model_path_to_load, **kwargs)
            controlnets.append(controlnet)
            idx += 1
            model_path_to_load = pretrained_model_path + f'_{idx}'
        if len(controlnets) == 0: raise ValueError(f"No ControlNets found under {os.path.dirname(pretrained_model_path)}. Expected at least {pretrained_model_path + '_0'}.")
        return cls(controlnets)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
