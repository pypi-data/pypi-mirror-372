'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Union
import torch
from ...models import UNet2DModel
from ...schedulers import CMStochasticIterativeScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n\n        >>> from sapiens_transformers.diffusers import ConsistencyModelPipeline\n\n        >>> device = "cuda"\n        >>> # Load the cd_imagenet64_l2 checkpoint.\n        >>> model_id_or_path = "openai/diffusers-cd_imagenet64_l2"\n        >>> pipe = ConsistencyModelPipeline.from_pretrained(model_id_or_path, torch_dtype=torch.float16)\n        >>> pipe.to(device)\n\n        >>> # Onestep Sampling\n        >>> image = pipe(num_inference_steps=1).images[0]\n        >>> image.save("cd_imagenet64_l2_onestep_sample.png")\n\n        >>> # Onestep sampling, class-conditional image generation\n        >>> # ImageNet-64 class label 145 corresponds to king penguins\n        >>> image = pipe(num_inference_steps=1, class_labels=145).images[0]\n        >>> image.save("cd_imagenet64_l2_onestep_sample_penguin.png")\n\n        >>> # Multistep sampling, class-conditional image generation\n        >>> # Timesteps can be explicitly specified; the particular timesteps below are from the original GitHub repo:\n        >>> # https://github.com/openai/consistency_models/blob/main/scripts/launch.sh#L77\n        >>> image = pipe(num_inference_steps=None, timesteps=[22, 0], class_labels=145).images[0]\n        >>> image.save("cd_imagenet64_l2_multistep_sample_penguin.png")\n        ```\n'
class ConsistencyModelPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'unet'
    def __init__(self, unet: UNet2DModel, scheduler: CMStochasticIterativeScheduler) -> None:
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler)
        self.safety_checker = None
    def prepare_latents(self, batch_size, num_channels, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels, height, width)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device=device, dtype=dtype)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def postprocess_image(self, sample: torch.Tensor, output_type: str='pil'):
        if output_type not in ['pt', 'np', 'pil']: raise ValueError(f"output_type={output_type} is not supported. Make sure to choose one of ['pt', 'np', or 'pil']")
        sample = (sample / 2 + 0.5).clamp(0, 1)
        if output_type == 'pt': return sample
        sample = sample.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'np': return sample
        sample = self.numpy_to_pil(sample)
        return sample
    def prepare_class_labels(self, batch_size, device, class_labels=None):
        if self.unet.config.num_class_embeds is not None:
            if isinstance(class_labels, list): class_labels = torch.tensor(class_labels, dtype=torch.int)
            elif isinstance(class_labels, int):
                assert batch_size == 1, 'Batch size must be 1 if classes is an int'
                class_labels = torch.tensor([class_labels], dtype=torch.int)
            elif class_labels is None: class_labels = torch.randint(0, self.unet.config.num_class_embeds, size=(batch_size,))
            class_labels = class_labels.to(device)
        else: class_labels = None
        return class_labels
    def check_inputs(self, num_inference_steps, timesteps, latents, batch_size, img_size, callback_steps):
        if num_inference_steps is None and timesteps is None: raise ValueError('Exactly one of `num_inference_steps` or `timesteps` must be supplied.')
        if latents is not None:
            expected_shape = (batch_size, 3, img_size, img_size)
            if latents.shape != expected_shape: raise ValueError(f'The shape of latents is {latents.shape} but is expected to be {expected_shape}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, batch_size: int=1, class_labels: Optional[Union[torch.Tensor, List[int], int]]=None, num_inference_steps: int=1, timesteps: List[int]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Examples:"""
        img_size = self.unet.config.sample_size
        device = self._execution_device
        self.check_inputs(num_inference_steps, timesteps, latents, batch_size, img_size, callback_steps)
        sample = self.prepare_latents(batch_size=batch_size, num_channels=self.unet.config.in_channels, height=img_size, width=img_size, dtype=self.unet.dtype, device=device, generator=generator, latents=latents)
        class_labels = self.prepare_class_labels(batch_size, device, class_labels=class_labels)
        if timesteps is not None:
            self.scheduler.set_timesteps(timesteps=timesteps, device=device)
            timesteps = self.scheduler.timesteps
            num_inference_steps = len(timesteps)
        else:
            self.scheduler.set_timesteps(num_inference_steps)
            timesteps = self.scheduler.timesteps
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                scaled_sample = self.scheduler.scale_model_input(sample, t)
                model_output = self.unet(scaled_sample, t, class_labels=class_labels, return_dict=False)[0]
                sample = self.scheduler.step(model_output, t, sample, generator=generator)[0]
                progress_bar.update()
                if callback is not None and i % callback_steps == 0: callback(i, t, sample)
        image = self.postprocess_image(sample, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
