'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import math
from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np
import PIL.Image
import torch
from sapiens_transformers import CLIPTextModelWithProjection, CLIPTokenizer
from ...models import PriorTransformer
from ...schedulers import HeunDiscreteScheduler
from ...utils import BaseOutput, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .renderer import ShapERenderer
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import DiffusionPipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_gif\n\n        >>> device = torch.device("cuda" if torch.cuda.is_available() else "cpu")\n\n        >>> repo = "openai/shap-e"\n        >>> pipe = DiffusionPipeline.from_pretrained(repo, torch_dtype=torch.float16)\n        >>> pipe = pipe.to(device)\n\n        >>> guidance_scale = 15.0\n        >>> prompt = "a shark"\n\n        >>> images = pipe(\n        ...     prompt,\n        ...     guidance_scale=guidance_scale,\n        ...     num_inference_steps=64,\n        ...     frame_size=256,\n        ... ).images\n\n        >>> gif_path = export_to_gif(images[0], "shark_3d.gif")\n        ```\n'
@dataclass
class ShapEPipelineOutput(BaseOutput):
    """Args:"""
    images: Union[List[List[PIL.Image.Image]], List[List[np.ndarray]]]
class ShapEPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->prior'
    _exclude_from_cpu_offload = ['shap_e_renderer']
    def __init__(self, prior: PriorTransformer, text_encoder: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, scheduler: HeunDiscreteScheduler, shap_e_renderer: ShapERenderer):
        super().__init__()
        self.register_modules(prior=prior, text_encoder=text_encoder, tokenizer=tokenizer, scheduler=scheduler, shap_e_renderer=shap_e_renderer)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance):
        len(prompt) if isinstance(prompt, list) else 1
        self.tokenizer.pad_token_id = 0
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
        text_encoder_output = self.text_encoder(text_input_ids.to(device))
        prompt_embeds = text_encoder_output.text_embeds
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        prompt_embeds = prompt_embeds / torch.linalg.norm(prompt_embeds, dim=-1, keepdim=True)
        if do_classifier_free_guidance:
            negative_prompt_embeds = torch.zeros_like(prompt_embeds)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        prompt_embeds = math.sqrt(prompt_embeds.shape[1]) * prompt_embeds
        return prompt_embeds
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: str, num_images_per_prompt: int=1, num_inference_steps: int=25, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, guidance_scale: float=4.0, frame_size: int=64, output_type: Optional[str]='pil', return_dict: bool=True):
        """Examples:"""
        if isinstance(prompt, str): batch_size = 1
        elif isinstance(prompt, list): batch_size = len(prompt)
        else: raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        device = self._execution_device
        batch_size = batch_size * num_images_per_prompt
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds = self._encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_embeddings = self.prior.config.num_embeddings
        embedding_dim = self.prior.config.embedding_dim
        latents = self.prepare_latents((batch_size, num_embeddings * embedding_dim), prompt_embeds.dtype, device, generator, latents, self.scheduler)
        latents = latents.reshape(latents.shape[0], num_embeddings, embedding_dim)
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            scaled_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            noise_pred = self.prior(scaled_model_input, timestep=t, proj_embedding=prompt_embeds).predicted_image_embedding
            noise_pred, _ = noise_pred.split(scaled_model_input.shape[2], dim=2)
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred - noise_pred_uncond)
            latents = self.scheduler.step(noise_pred, timestep=t, sample=latents).prev_sample
        self.maybe_free_model_hooks()
        if output_type not in ['np', 'pil', 'latent', 'mesh']: raise ValueError(f'Only the output types `pil`, `np`, `latent` and `mesh` are supported not output_type={output_type}')
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
