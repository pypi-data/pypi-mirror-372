'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .image_processor import VaeImageProcessor, is_valid_image, is_valid_image_imagelist
from typing import List, Optional, Union
import numpy as np
import torch
import PIL
class VideoProcessor(VaeImageProcessor):
    def preprocess_video(self, video, height: Optional[int]=None, width: Optional[int]=None) -> torch.Tensor:
        """Args:"""
        if isinstance(video, list) and isinstance(video[0], np.ndarray) and (video[0].ndim == 5): video = np.concatenate(video, axis=0)
        if isinstance(video, list) and isinstance(video[0], torch.Tensor) and (video[0].ndim == 5): video = torch.cat(video, axis=0)
        if isinstance(video, (np.ndarray, torch.Tensor)) and video.ndim == 5: video = list(video)
        elif isinstance(video, list) and is_valid_image(video[0]) or is_valid_image_imagelist(video): video = [video]
        elif isinstance(video, list) and is_valid_image_imagelist(video[0]): video = video
        else: raise ValueError('Input is in incorrect format. Currently, we only support numpy.ndarray, torch.Tensor, PIL.Image.Image')
        video = torch.stack([self.preprocess(img, height=height, width=width) for img in video], dim=0)
        video = video.permute(0, 2, 1, 3, 4)
        return video
    def postprocess_video(self, video: torch.Tensor, output_type: str='np') -> Union[np.ndarray, torch.Tensor, List[PIL.Image.Image]]:
        """Args:"""
        batch_size = video.shape[0]
        outputs = []
        for batch_idx in range(batch_size):
            batch_vid = video[batch_idx].permute(1, 0, 2, 3)
            batch_output = self.postprocess(batch_vid, output_type)
            outputs.append(batch_output)
        if output_type == 'np': outputs = np.stack(outputs)
        elif output_type == 'pt': outputs = torch.stack(outputs)
        elif not output_type == 'pil': raise ValueError(f"{output_type} does not exist. Please choose one of ['np', 'pt', 'pil']")
        return outputs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
