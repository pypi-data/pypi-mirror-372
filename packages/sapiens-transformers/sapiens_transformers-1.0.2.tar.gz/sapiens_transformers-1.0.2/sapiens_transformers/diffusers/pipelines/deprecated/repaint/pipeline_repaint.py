'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Tuple, Union
import numpy as np
import PIL.Image
import torch
from ....models import UNet2DModel
from ....schedulers import RePaintScheduler
from ....utils import PIL_INTERPOLATION, deprecate
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, ImagePipelineOutput
def _preprocess_image(image: Union[List, PIL.Image.Image, torch.Tensor]):
    deprecation_message = 'The preprocess method is deprecated and will be removed in diffusers 1.0.0. Please use VaeImageProcessor.preprocess(...) instead'
    deprecate('preprocess', '1.0.0', deprecation_message, standard_warn=False)
    if isinstance(image, torch.Tensor): return image
    elif isinstance(image, PIL.Image.Image): image = [image]
    if isinstance(image[0], PIL.Image.Image):
        w, h = image[0].size
        w, h = (x - x % 8 for x in (w, h))
        image = [np.array(i.resize((w, h), resample=PIL_INTERPOLATION['lanczos']))[None, :] for i in image]
        image = np.concatenate(image, axis=0)
        image = np.array(image).astype(np.float32) / 255.0
        image = image.transpose(0, 3, 1, 2)
        image = 2.0 * image - 1.0
        image = torch.from_numpy(image)
    elif isinstance(image[0], torch.Tensor): image = torch.cat(image, dim=0)
    return image
def _preprocess_mask(mask: Union[List, PIL.Image.Image, torch.Tensor]):
    if isinstance(mask, torch.Tensor): return mask
    elif isinstance(mask, PIL.Image.Image): mask = [mask]
    if isinstance(mask[0], PIL.Image.Image):
        w, h = mask[0].size
        w, h = (x - x % 32 for x in (w, h))
        mask = [np.array(m.convert('L').resize((w, h), resample=PIL_INTERPOLATION['nearest']))[None, :] for m in mask]
        mask = np.concatenate(mask, axis=0)
        mask = mask.astype(np.float32) / 255.0
        mask[mask < 0.5] = 0
        mask[mask >= 0.5] = 1
        mask = torch.from_numpy(mask)
    elif isinstance(mask[0], torch.Tensor): mask = torch.cat(mask, dim=0)
    return mask
class RePaintPipeline(DiffusionPipeline):
    unet: UNet2DModel
    scheduler: RePaintScheduler
    model_cpu_offload_seq = 'unet'
    def __init__(self, unet, scheduler):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, image: Union[torch.Tensor, PIL.Image.Image], mask_image: Union[torch.Tensor, PIL.Image.Image], num_inference_steps: int=250, eta: float=0.0, jump_length: int=10,
    jump_n_sample: int=10, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, output_type: Optional[str]='pil', return_dict: bool=True) -> Union[ImagePipelineOutput, Tuple]:
        """Returns:"""
        original_image = image
        original_image = _preprocess_image(original_image)
        original_image = original_image.to(device=self._execution_device, dtype=self.unet.dtype)
        mask_image = _preprocess_mask(mask_image)
        mask_image = mask_image.to(device=self._execution_device, dtype=self.unet.dtype)
        batch_size = original_image.shape[0]
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        image_shape = original_image.shape
        image = randn_tensor(image_shape, generator=generator, device=self._execution_device, dtype=self.unet.dtype)
        self.scheduler.set_timesteps(num_inference_steps, jump_length, jump_n_sample, self._execution_device)
        self.scheduler.eta = eta
        t_last = self.scheduler.timesteps[0] + 1
        generator = generator[0] if isinstance(generator, list) else generator
        for i, t in enumerate(self.progress_bar(self.scheduler.timesteps)):
            if t < t_last:
                model_output = self.unet(image, t).sample
                image = self.scheduler.step(model_output, t, image, original_image, mask_image, generator).prev_sample
            else: image = self.scheduler.undo_step(image, t_last, generator)
            t_last = t
        image = (image / 2 + 0.5).clamp(0, 1)
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
