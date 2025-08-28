'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import List, Optional, Tuple, Union
import numpy as np
import PIL.Image
import torch
import torch.utils.checkpoint
from ...models import UNet2DModel, VQModel
from ...schedulers import DDIMScheduler, DPMSolverMultistepScheduler, EulerAncestralDiscreteScheduler, EulerDiscreteScheduler, LMSDiscreteScheduler, PNDMScheduler
from ...utils import PIL_INTERPOLATION
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
def preprocess(image):
    w, h = image.size
    w, h = (x - x % 32 for x in (w, h))
    image = image.resize((w, h), resample=PIL_INTERPOLATION['lanczos'])
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return 2.0 * image - 1.0
class LDMSuperResolutionPipeline(DiffusionPipeline):
    def __init__(self, vqvae: VQModel, unet: UNet2DModel, scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler, EulerDiscreteScheduler,
    EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler]):
        super().__init__()
        self.register_modules(vqvae=vqvae, unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, image: Union[torch.Tensor, PIL.Image.Image]=None, batch_size: Optional[int]=1, num_inference_steps: Optional[int]=100, eta: Optional[float]=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, output_type: Optional[str]='pil', return_dict: bool=True) -> Union[Tuple, ImagePipelineOutput]:
        """Returns:"""
        if isinstance(image, PIL.Image.Image): batch_size = 1
        elif isinstance(image, torch.Tensor): batch_size = image.shape[0]
        else: raise ValueError(f'`image` has to be of type `PIL.Image.Image` or `torch.Tensor` but is {type(image)}')
        if isinstance(image, PIL.Image.Image): image = preprocess(image)
        height, width = image.shape[-2:]
        latents_shape = (batch_size, self.unet.config.in_channels // 2, height, width)
        latents_dtype = next(self.unet.parameters()).dtype
        latents = randn_tensor(latents_shape, generator=generator, device=self.device, dtype=latents_dtype)
        image = image.to(device=self.device, dtype=latents_dtype)
        self.scheduler.set_timesteps(num_inference_steps, device=self.device)
        timesteps_tensor = self.scheduler.timesteps
        latents = latents * self.scheduler.init_noise_sigma
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_kwargs = {}
        if accepts_eta: extra_kwargs['eta'] = eta
        for t in self.progress_bar(timesteps_tensor):
            latents_input = torch.cat([latents, image], dim=1)
            latents_input = self.scheduler.scale_model_input(latents_input, t)
            noise_pred = self.unet(latents_input, t).sample
            latents = self.scheduler.step(noise_pred, t, latents, **extra_kwargs).prev_sample
        image = self.vqvae.decode(latents).sample
        image = torch.clamp(image, -1.0, 1.0)
        image = image / 2 + 0.5
        image = image.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
