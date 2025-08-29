'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import torch
from PIL import Image
from ...models import UNet2DConditionModel, VQModel
from ...schedulers import DDPMScheduler
from ...utils import deprecate
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import KandinskyV22Img2ImgPipeline, KandinskyV22PriorPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import torch\n\n        >>> pipe_prior = KandinskyV22PriorPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-prior", torch_dtype=torch.float16\n        ... )\n        >>> pipe_prior.to("cuda")\n\n        >>> prompt = "A red cartoon frog, 4k"\n        >>> image_emb, zero_image_emb = pipe_prior(prompt, return_dict=False)\n\n        >>> pipe = KandinskyV22Img2ImgPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-decoder", torch_dtype=torch.float16\n        ... )\n        >>> pipe.to("cuda")\n\n        >>> init_image = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/frog.png"\n        ... )\n\n        >>> image = pipe(\n        ...     image=init_image,\n        ...     image_embeds=image_emb,\n        ...     negative_image_embeds=zero_image_emb,\n        ...     height=768,\n        ...     width=768,\n        ...     num_inference_steps=100,\n        ...     strength=0.2,\n        ... ).images\n\n        >>> image[0].save("red_frog.png")\n        ```\n'
def downscale_height_and_width(height, width, scale_factor=8):
    new_height = height // scale_factor ** 2
    if height % scale_factor ** 2 != 0: new_height += 1
    new_width = width // scale_factor ** 2
    if width % scale_factor ** 2 != 0: new_width += 1
    return (new_height * scale_factor, new_width * scale_factor)
def prepare_image(pil_image, w=512, h=512):
    pil_image = pil_image.resize((w, h), resample=Image.BICUBIC, reducing_gap=1)
    arr = np.array(pil_image.convert('RGB'))
    arr = arr.astype(np.float32) / 127.5 - 1
    arr = np.transpose(arr, [2, 0, 1])
    image = torch.from_numpy(arr).unsqueeze(0)
    return image
class KandinskyV22Img2ImgPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'unet->movq'
    _callback_tensor_inputs = ['latents', 'image_embeds', 'negative_image_embeds']
    def __init__(self, unet: UNet2DConditionModel, scheduler: DDPMScheduler, movq: VQModel):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler, movq=movq)
        self.movq_scale_factor = 2 ** (len(self.movq.config.block_out_channels) - 1)
    def get_timesteps(self, num_inference_steps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        timesteps = self.scheduler.timesteps[t_start:]
        return (timesteps, num_inference_steps - t_start)
    def prepare_latents(self, image, timestep, batch_size, num_images_per_prompt, dtype, device, generator=None):
        if not isinstance(image, (torch.Tensor, PIL.Image.Image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image` or list but is {type(image)}')
        image = image.to(device=device, dtype=dtype)
        batch_size = batch_size * num_images_per_prompt
        if image.shape[1] == 4: init_latents = image
        else:
            if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
            elif isinstance(generator, list):
                init_latents = [self.movq.encode(image[i:i + 1]).latent_dist.sample(generator[i]) for i in range(batch_size)]
                init_latents = torch.cat(init_latents, dim=0)
            else: init_latents = self.movq.encode(image).latent_dist.sample(generator)
            init_latents = self.movq.config.scaling_factor * init_latents
        init_latents = torch.cat([init_latents], dim=0)
        shape = init_latents.shape
        noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        init_latents = self.scheduler.add_noise(init_latents, noise, timestep)
        latents = init_latents
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    def __call__(self, image_embeds: Union[torch.Tensor, List[torch.Tensor]], image: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]],
    negative_image_embeds: Union[torch.Tensor, List[torch.Tensor]], height: int=512, width: int=512, num_inference_steps: int=100, guidance_scale: float=4.0, strength: float=0.3,
    num_images_per_prompt: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        callback = kwargs.pop('callback', None)
        callback_steps = kwargs.pop('callback_steps', None)
        if callback is not None: deprecate('callback', '1.0.0', 'Passing `callback` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_steps is not None: deprecate('callback_steps', '1.0.0', 'Passing `callback_steps` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        device = self._execution_device
        self._guidance_scale = guidance_scale
        if isinstance(image_embeds, list): image_embeds = torch.cat(image_embeds, dim=0)
        batch_size = image_embeds.shape[0]
        if isinstance(negative_image_embeds, list): negative_image_embeds = torch.cat(negative_image_embeds, dim=0)
        if self.do_classifier_free_guidance:
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            negative_image_embeds = negative_image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            image_embeds = torch.cat([negative_image_embeds, image_embeds], dim=0).to(dtype=self.unet.dtype, device=device)
        if not isinstance(image, list): image = [image]
        if not all((isinstance(i, (PIL.Image.Image, torch.Tensor)) for i in image)): raise ValueError(f'Input is in incorrect format: {[type(i) for i in image]}. Currently, we only support  PIL image and pytorch tensor')
        image = torch.cat([prepare_image(i, width, height) for i in image], dim=0)
        image = image.to(dtype=image_embeds.dtype, device=device)
        latents = self.movq.encode(image)['latents']
        latents = latents.repeat_interleave(num_images_per_prompt, dim=0)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, strength, device)
        latent_timestep = timesteps[:1].repeat(batch_size * num_images_per_prompt)
        height, width = downscale_height_and_width(height, width, self.movq_scale_factor)
        latents = self.prepare_latents(latents, latent_timestep, batch_size, num_images_per_prompt, image_embeds.dtype, device, generator)
        self._num_timesteps = len(timesteps)
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
            added_cond_kwargs = {'image_embeds': image_embeds}
            noise_pred = self.unet(sample=latent_model_input, timestep=t, encoder_hidden_states=None, added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
            if self.do_classifier_free_guidance:
                noise_pred, variance_pred = noise_pred.split(latents.shape[1], dim=1)
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                _, variance_pred_text = variance_pred.chunk(2)
                noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                noise_pred = torch.cat([noise_pred, variance_pred_text], dim=1)
            if not (hasattr(self.scheduler.config, 'variance_type') and self.scheduler.config.variance_type in ['learned', 'learned_range']): noise_pred, _ = noise_pred.split(latents.shape[1], dim=1)
            latents = self.scheduler.step(noise_pred, t, latents, generator=generator)[0]
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                image_embeds = callback_outputs.pop('image_embeds', image_embeds)
                negative_image_embeds = callback_outputs.pop('negative_image_embeds', negative_image_embeds)
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        if output_type not in ['pt', 'np', 'pil', 'latent']: raise ValueError(f'Only the output types `pt`, `pil` ,`np` and `latent` are supported not output_type={output_type}')
        if not output_type == 'latent':
            image = self.movq.decode(latents, force_not_quantize=True)['sample']
            if output_type in ['np', 'pil']:
                image = image * 0.5 + 0.5
                image = image.clamp(0, 1)
                image = image.cpu().permute(0, 2, 3, 1).float().numpy()
            if output_type == 'pil': image = self.numpy_to_pil(image)
        else: image = latents
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
