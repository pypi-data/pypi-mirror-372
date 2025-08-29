'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Tuple, Union
import torch
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import AudioPipelineOutput, DiffusionPipeline
class DanceDiffusionPipeline(DiffusionPipeline):
    model_cpu_offload_seq = 'unet'
    def __init__(self, unet, scheduler):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, batch_size: int=1, num_inference_steps: int=100, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, audio_length_in_s: Optional[float]=None,
    return_dict: bool=True) -> Union[AudioPipelineOutput, Tuple]:
        """Returns:"""
        if audio_length_in_s is None: audio_length_in_s = self.unet.config.sample_size / self.unet.config.sample_rate
        sample_size = audio_length_in_s * self.unet.config.sample_rate
        down_scale_factor = 2 ** len(self.unet.up_blocks)
        if sample_size < 3 * down_scale_factor: raise ValueError(f"{audio_length_in_s} is too small. Make sure it's bigger or equal to {3 * down_scale_factor / self.unet.config.sample_rate}.")
        original_sample_size = int(sample_size)
        if sample_size % down_scale_factor != 0: sample_size = (audio_length_in_s * self.unet.config.sample_rate // down_scale_factor + 1) * down_scale_factor
        sample_size = int(sample_size)
        dtype = next(self.unet.parameters()).dtype
        shape = (batch_size, self.unet.config.in_channels, sample_size)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        audio = randn_tensor(shape, generator=generator, device=self._execution_device, dtype=dtype)
        self.scheduler.set_timesteps(num_inference_steps, device=audio.device)
        self.scheduler.timesteps = self.scheduler.timesteps.to(dtype)
        for t in self.progress_bar(self.scheduler.timesteps):
            model_output = self.unet(audio, t).sample
            audio = self.scheduler.step(model_output, t, audio).prev_sample
        audio = audio.clamp(-1, 1).float().cpu().numpy()
        audio = audio[:, :, :original_sample_size]
        if not return_dict: return (audio,)
        return AudioPipelineOutput(audios=audio)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
