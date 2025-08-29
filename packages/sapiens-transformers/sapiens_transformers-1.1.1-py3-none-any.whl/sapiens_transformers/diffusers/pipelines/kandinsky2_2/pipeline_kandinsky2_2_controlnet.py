'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Union
import torch
from ...models import UNet2DConditionModel, VQModel
from ...schedulers import DDPMScheduler
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> import numpy as np\n\n        >>> from sapiens_transformers.diffusers import KandinskyV22PriorPipeline, KandinskyV22ControlnetPipeline\n        >>> from sapiens_transformers import pipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n\n        >>> def make_hint(image, depth_estimator):\n        ...     image = depth_estimator(image)["depth"]\n        ...     image = np.array(image)\n        ...     image = image[:, :, None]\n        ...     image = np.concatenate([image, image, image], axis=2)\n        ...     detected_map = torch.from_numpy(image).float() / 255.0\n        ...     hint = detected_map.permute(2, 0, 1)\n        ...     return hint\n\n\n        >>> depth_estimator = pipeline("depth-estimation")\n\n        >>> pipe_prior = KandinskyV22PriorPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-prior", torch_dtype=torch.float16\n        ... )\n        >>> pipe_prior = pipe_prior.to("cuda")\n\n        >>> pipe = KandinskyV22ControlnetPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-controlnet-depth", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n\n\n        >>> img = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/cat.png"\n        ... ).resize((768, 768))\n\n        >>> hint = make_hint(img, depth_estimator).unsqueeze(0).half().to("cuda")\n\n        >>> prompt = "A robot, 4k photo"\n        >>> negative_prior_prompt = "lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, username, watermark, signature"\n\n        >>> generator = torch.Generator(device="cuda").manual_seed(43)\n\n        >>> image_emb, zero_image_emb = pipe_prior(\n        ...     prompt=prompt, negative_prompt=negative_prior_prompt, generator=generator\n        ... ).to_tuple()\n\n        >>> images = pipe(\n        ...     image_embeds=image_emb,\n        ...     negative_image_embeds=zero_image_emb,\n        ...     hint=hint,\n        ...     num_inference_steps=50,\n        ...     generator=generator,\n        ...     height=768,\n        ...     width=768,\n        ... ).images\n\n        >>> images[0].save("robot_cat.png")\n        ```\n'
def downscale_height_and_width(height, width, scale_factor=8):
    new_height = height // scale_factor ** 2
    if height % scale_factor ** 2 != 0: new_height += 1
    new_width = width // scale_factor ** 2
    if width % scale_factor ** 2 != 0: new_width += 1
    return (new_height * scale_factor, new_width * scale_factor)
class KandinskyV22ControlnetPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'unet->movq'
    def __init__(self, unet: UNet2DConditionModel, scheduler: DDPMScheduler, movq: VQModel):
        super().__init__()
        self.register_modules(unet=unet, scheduler=scheduler, movq=movq)
        self.movq_scale_factor = 2 ** (len(self.movq.config.block_out_channels) - 1)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    def __call__(self, image_embeds: Union[torch.Tensor, List[torch.Tensor]], negative_image_embeds: Union[torch.Tensor, List[torch.Tensor]], hint: torch.Tensor, height: int=512, width: int=512,
    num_inference_steps: int=100, guidance_scale: float=4.0, num_images_per_prompt: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        if isinstance(image_embeds, list): image_embeds = torch.cat(image_embeds, dim=0)
        if isinstance(negative_image_embeds, list): negative_image_embeds = torch.cat(negative_image_embeds, dim=0)
        if isinstance(hint, list): hint = torch.cat(hint, dim=0)
        batch_size = image_embeds.shape[0] * num_images_per_prompt
        if do_classifier_free_guidance:
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            negative_image_embeds = negative_image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            hint = hint.repeat_interleave(num_images_per_prompt, dim=0)
            image_embeds = torch.cat([negative_image_embeds, image_embeds], dim=0).to(dtype=self.unet.dtype, device=device)
            hint = torch.cat([hint, hint], dim=0).to(dtype=self.unet.dtype, device=device)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps_tensor = self.scheduler.timesteps
        num_channels_latents = self.movq.config.latent_channels
        height, width = downscale_height_and_width(height, width, self.movq_scale_factor)
        latents = self.prepare_latents((batch_size, num_channels_latents, height, width), image_embeds.dtype, device, generator, latents, self.scheduler)
        for i, t in enumerate(self.progress_bar(timesteps_tensor)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            added_cond_kwargs = {'image_embeds': image_embeds, 'hint': hint}
            noise_pred = self.unet(sample=latent_model_input, timestep=t, encoder_hidden_states=None, added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
            if do_classifier_free_guidance:
                noise_pred, variance_pred = noise_pred.split(latents.shape[1], dim=1)
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                _, variance_pred_text = variance_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                noise_pred = torch.cat([noise_pred, variance_pred_text], dim=1)
            if not (hasattr(self.scheduler.config, 'variance_type') and self.scheduler.config.variance_type in ['learned', 'learned_range']): noise_pred, _ = noise_pred.split(latents.shape[1], dim=1)
            latents = self.scheduler.step(noise_pred, t, latents, generator=generator)[0]
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        image = self.movq.decode(latents, force_not_quantize=True)['sample']
        self.maybe_free_model_hooks()
        if output_type not in ['pt', 'np', 'pil']: raise ValueError(f'Only the output types `pt`, `pil` and `np` are supported not output_type={output_type}')
        if output_type in ['np', 'pil']:
            image = image * 0.5 + 0.5
            image = image.clamp(0, 1)
            image = image.cpu().permute(0, 2, 3, 1).float().numpy()
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
