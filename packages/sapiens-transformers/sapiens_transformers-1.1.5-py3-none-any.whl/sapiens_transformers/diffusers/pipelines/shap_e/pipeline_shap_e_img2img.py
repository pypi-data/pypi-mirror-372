'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPVisionModel
from ...models import PriorTransformer
from ...schedulers import HeunDiscreteScheduler
from ...utils import BaseOutput, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .renderer import ShapERenderer
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from PIL import Image\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import DiffusionPipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_gif, load_image\n\n        >>> device = torch.device("cuda" if torch.cuda.is_available() else "cpu")\n\n        >>> repo = "openai/shap-e-img2img"\n        >>> pipe = DiffusionPipeline.from_pretrained(repo, torch_dtype=torch.float16)\n        >>> pipe = pipe.to(device)\n\n        >>> guidance_scale = 3.0\n        >>> image_url = "https://hf.co/datasets/diffusers/docs-images/resolve/main/shap-e/corgi.png"\n        >>> image = load_image(image_url).convert("RGB")\n\n        >>> images = pipe(\n        ...     image,\n        ...     guidance_scale=guidance_scale,\n        ...     num_inference_steps=64,\n        ...     frame_size=256,\n        ... ).images\n\n        >>> gif_path = export_to_gif(images[0], "corgi_3d.gif")\n        ```\n'
@dataclass
class ShapEPipelineOutput(BaseOutput):
    """Args:"""
    images: Union[PIL.Image.Image, np.ndarray]
class ShapEImg2ImgPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'image_encoder->prior'
    _exclude_from_cpu_offload = ['shap_e_renderer']
    def __init__(self, prior: PriorTransformer, image_encoder: CLIPVisionModel, image_processor: CLIPImageProcessor, scheduler: HeunDiscreteScheduler, shap_e_renderer: ShapERenderer):
        super().__init__()
        self.register_modules(prior=prior, image_encoder=image_encoder, image_processor=image_processor, scheduler=scheduler, shap_e_renderer=shap_e_renderer)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def _encode_image(self, image, device, num_images_per_prompt, do_classifier_free_guidance):
        if isinstance(image, List) and isinstance(image[0], torch.Tensor): image = torch.cat(image, axis=0) if image[0].ndim == 4 else torch.stack(image, axis=0)
        if not isinstance(image, torch.Tensor): image = self.image_processor(image, return_tensors='pt').pixel_values[0].unsqueeze(0)
        image = image.to(dtype=self.image_encoder.dtype, device=device)
        image_embeds = self.image_encoder(image)['last_hidden_state']
        image_embeds = image_embeds[:, 1:, :].contiguous()
        image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            negative_image_embeds = torch.zeros_like(image_embeds)
            image_embeds = torch.cat([negative_image_embeds, image_embeds])
        return image_embeds
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: Union[PIL.Image.Image, List[PIL.Image.Image]], num_images_per_prompt: int=1, num_inference_steps: int=25, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, guidance_scale: float=4.0, frame_size: int=64, output_type: Optional[str]='pil', return_dict: bool=True):
        """Examples:"""
        if isinstance(image, PIL.Image.Image): batch_size = 1
        elif isinstance(image, torch.Tensor): batch_size = image.shape[0]
        elif isinstance(image, list) and isinstance(image[0], (torch.Tensor, PIL.Image.Image)): batch_size = len(image)
        else: raise ValueError(f'`image` has to be of type `PIL.Image.Image`, `torch.Tensor`, `List[PIL.Image.Image]` or `List[torch.Tensor]` but is {type(image)}')
        device = self._execution_device
        batch_size = batch_size * num_images_per_prompt
        do_classifier_free_guidance = guidance_scale > 1.0
        image_embeds = self._encode_image(image, device, num_images_per_prompt, do_classifier_free_guidance)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_embeddings = self.prior.config.num_embeddings
        embedding_dim = self.prior.config.embedding_dim
        if latents is None: latents = self.prepare_latents((batch_size, num_embeddings * embedding_dim), image_embeds.dtype, device, generator, latents, self.scheduler)
        latents = latents.reshape(latents.shape[0], num_embeddings, embedding_dim)
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            scaled_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            noise_pred = self.prior(scaled_model_input, timestep=t, proj_embedding=image_embeds).predicted_image_embedding
            noise_pred, _ = noise_pred.split(scaled_model_input.shape[2], dim=2)
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred - noise_pred_uncond)
            latents = self.scheduler.step(noise_pred, timestep=t, sample=latents).prev_sample
        if output_type not in ['np', 'pil', 'latent', 'mesh']: raise ValueError(f'Only the output types `pil`, `np`, `latent` and `mesh` are supported not output_type={output_type}')
        self.maybe_free_model_hooks()
        if output_type == 'latent': return ShapEPipelineOutput(images=latents)
        images = []
        if output_type == 'mesh':
            for i, latent in enumerate(latents):
                mesh = self.shap_e_renderer.decode_to_mesh(latent[None, :], device)
                images.append(mesh)
        else:
            for i, latent in enumerate(latents):
                image = self.shap_e_renderer.decode_to_image(latent[None, :], device, size=frame_size)
                images.append(image)
            images = torch.stack(images)
            images = images.cpu().numpy()
            if output_type == 'pil': images = [self.numpy_to_pil(image) for image in images]
        if not return_dict: return (images,)
        return ShapEPipelineOutput(images=images)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
