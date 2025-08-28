'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Tuple, Union
import torch
from ....models import UNet2DModel
from ....schedulers import KarrasVeScheduler
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class KarrasVePipeline(DiffusionPipeline):
    unet: UNet2DModel
    scheduler: KarrasVeScheduler
    def __init__(self, unet: UNet2DModel, scheduler: KarrasVeScheduler):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler)
    @torch.no_grad()
    def __call__(self, batch_size: int=1, num_inference_steps: int=50, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, **kwargs) -> Union[Tuple, ImagePipelineOutput]:
        """Returns:"""
        img_size = self.unet.config.sample_size
        shape = (batch_size, 3, img_size, img_size)
        model = self.unet
        sample = randn_tensor(shape, generator=generator, device=self.device) * self.scheduler.init_noise_sigma
        self.scheduler.set_timesteps(num_inference_steps)
        for t in self.progress_bar(self.scheduler.timesteps):
            sigma = self.scheduler.schedule[t]
            sigma_prev = self.scheduler.schedule[t - 1] if t > 0 else 0
            sample_hat, sigma_hat = self.scheduler.add_noise_to_input(sample, sigma, generator=generator)
            model_output = sigma_hat / 2 * model((sample_hat + 1) / 2, sigma_hat / 2).sample
            step_output = self.scheduler.step(model_output, sigma_hat, sigma_prev, sample_hat)
            if sigma_prev != 0:
                model_output = sigma_prev / 2 * model((step_output.prev_sample + 1) / 2, sigma_prev / 2).sample
                step_output = self.scheduler.step_correct(model_output, sigma_hat, sigma_prev, sample_hat, step_output.prev_sample, step_output['derivative'])
            sample = step_output.prev_sample
        sample = (sample / 2 + 0.5).clamp(0, 1)
        image = sample.cpu().permute(0, 2, 3, 1).numpy()
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
