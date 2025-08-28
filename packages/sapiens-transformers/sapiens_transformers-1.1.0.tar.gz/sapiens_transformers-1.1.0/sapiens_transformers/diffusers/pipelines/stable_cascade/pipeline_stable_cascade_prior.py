'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from math import ceil
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import PIL
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModelWithProjection, CLIPTokenizer, CLIPVisionModelWithProjection
from ...models import StableCascadeUNet
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import BaseOutput, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
DEFAULT_STAGE_C_TIMESTEPS = list(np.linspace(1.0, 2 / 3, 20)) + list(np.linspace(2 / 3, 0.0, 11))[1:]
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableCascadePriorPipeline\n\n        >>> prior_pipe = StableCascadePriorPipeline.from_pretrained(\n        ...     "stabilityai/stable-cascade-prior", torch_dtype=torch.bfloat16\n        ... ).to("cuda")\n\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> prior_output = pipe(prompt)\n        ```\n'
@dataclass
class StableCascadePriorPipelineOutput(BaseOutput):
    """Args:"""
    image_embeddings: Union[torch.Tensor, np.ndarray]
    prompt_embeds: Union[torch.Tensor, np.ndarray]
    prompt_embeds_pooled: Union[torch.Tensor, np.ndarray]
    negative_prompt_embeds: Union[torch.Tensor, np.ndarray]
    negative_prompt_embeds_pooled: Union[torch.Tensor, np.ndarray]
class StableCascadePriorPipeline(DiffusionPipeline):
    """Args:"""
    unet_name = 'prior'
    text_encoder_name = 'text_encoder'
    model_cpu_offload_seq = 'image_encoder->text_encoder->prior'
    _optional_components = ['image_encoder', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'text_encoder_hidden_states', 'negative_prompt_embeds']
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModelWithProjection, prior: StableCascadeUNet, scheduler: DDPMWuerstchenScheduler, resolution_multiple: float=42.67,
    feature_extractor: Optional[CLIPImageProcessor]=None, image_encoder: Optional[CLIPVisionModelWithProjection]=None) -> None:
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, image_encoder=image_encoder, feature_extractor=feature_extractor, prior=prior, scheduler=scheduler)
        self.register_to_config(resolution_multiple=resolution_multiple)
    def prepare_latents(self, batch_size, height, width, num_images_per_prompt, dtype, device, generator, latents, scheduler):
        latent_shape = (num_images_per_prompt * batch_size, self.prior.config.in_channels, ceil(height / self.config.resolution_multiple), ceil(width / self.config.resolution_multiple))
        if latents is None: latents = randn_tensor(latent_shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != latent_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latent_shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def encode_prompt(self, device, batch_size, num_images_per_prompt, do_classifier_free_guidance, prompt=None, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    prompt_embeds_pooled: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds_pooled: Optional[torch.Tensor]=None):
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            attention_mask = text_inputs.attention_mask
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
                removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
                attention_mask = attention_mask[:, :self.tokenizer.model_max_length]
            text_encoder_output = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask.to(device), output_hidden_states=True)
            prompt_embeds = text_encoder_output.hidden_states[-1]
            if prompt_embeds_pooled is None: prompt_embeds_pooled = text_encoder_output.text_embeds.unsqueeze(1)
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds_pooled = prompt_embeds_pooled.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        prompt_embeds_pooled = prompt_embeds_pooled.repeat_interleave(num_images_per_prompt, dim=0)
        if negative_prompt_embeds is None and do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=uncond_input.attention_mask.to(device), output_hidden_states=True)
            negative_prompt_embeds = negative_prompt_embeds_text_encoder_output.hidden_states[-1]
            negative_prompt_embeds_pooled = negative_prompt_embeds_text_encoder_output.text_embeds.unsqueeze(1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            seq_len = negative_prompt_embeds_pooled.shape[1]
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.view(batch_size * num_images_per_prompt, seq_len, -1)
        return (prompt_embeds, prompt_embeds_pooled, negative_prompt_embeds, negative_prompt_embeds_pooled)
    def encode_image(self, images, device, dtype, batch_size, num_images_per_prompt):
        image_embeds = []
        for image in images:
            image = self.feature_extractor(image, return_tensors='pt').pixel_values
            image = image.to(device=device, dtype=dtype)
            image_embed = self.image_encoder(image).image_embeds.unsqueeze(1)
            image_embeds.append(image_embed)
        image_embeds = torch.cat(image_embeds, dim=1)
        image_embeds = image_embeds.repeat(batch_size * num_images_per_prompt, 1, 1)
        negative_image_embeds = torch.zeros_like(image_embeds)
        return (image_embeds, negative_image_embeds)
    def check_inputs(self, prompt, images=None, image_embeds=None, negative_prompt=None, prompt_embeds=None, prompt_embeds_pooled=None, negative_prompt_embeds=None,
    negative_prompt_embeds_pooled=None, callback_on_step_end_tensor_inputs=None):
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and prompt_embeds_pooled is None: raise ValueError('If `prompt_embeds` are provided, `prompt_embeds_pooled` must also be provided. Make sure to generate `prompt_embeds_pooled` from the same text encoder that was used to generate `prompt_embeds`')
        if negative_prompt_embeds is not None and negative_prompt_embeds_pooled is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_prompt_embeds_pooled` must also be provided. Make sure to generate `prompt_embeds_pooled` from the same text encoder that was used to generate `prompt_embeds`')
        if prompt_embeds_pooled is not None and negative_prompt_embeds_pooled is not None:
            if prompt_embeds_pooled.shape != negative_prompt_embeds_pooled.shape: raise ValueError(f'`prompt_embeds_pooled` and `negative_prompt_embeds_pooled` must have the same shape when passeddirectly, but got: `prompt_embeds_pooled` {prompt_embeds_pooled.shape} !=`negative_prompt_embeds_pooled` {negative_prompt_embeds_pooled.shape}.')
        if image_embeds is not None and images is not None: raise ValueError(f'Cannot forward both `images`: {images} and `image_embeds`: {image_embeds}. Please make sure to only forward one of the two.')
        if images:
            for i, image in enumerate(images):
                if not isinstance(image, torch.Tensor) and (not isinstance(image, PIL.Image.Image)): raise TypeError(f"'images' must contain images of type 'torch.Tensor' or 'PIL.Image.Image, but got{type(image)} for image number {i}.")
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    def get_timestep_ratio_conditioning(self, t, alphas_cumprod):
        s = torch.tensor([0.008])
        clamp_range = [0, 1]
        min_var = torch.cos(s / (1 + s) * torch.pi * 0.5) ** 2
        var = alphas_cumprod[t]
        var = var.clamp(*clamp_range)
        s, min_var = (s.to(var.device), min_var.to(var.device))
        ratio = ((var * min_var) ** 0.5).acos() / (torch.pi * 0.5) * (1 + s) - s
        return ratio
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, images: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]]=None,
    height: int=1024, width: int=1024, num_inference_steps: int=20, timesteps: List[float]=None, guidance_scale: float=4.0, negative_prompt: Optional[Union[str,
    List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_embeds_pooled: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds_pooled: Optional[torch.Tensor]=None, image_embeds: Optional[torch.Tensor]=None, num_images_per_prompt: Optional[int]=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pt',
    return_dict: bool=True, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        device = self._execution_device
        dtype = next(self.prior.parameters()).dtype
        self._guidance_scale = guidance_scale
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        self.check_inputs(prompt, images=images, image_embeds=image_embeds, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, prompt_embeds_pooled=prompt_embeds_pooled,
        negative_prompt_embeds=negative_prompt_embeds, negative_prompt_embeds_pooled=negative_prompt_embeds_pooled, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs)
        prompt_embeds, prompt_embeds_pooled, negative_prompt_embeds, negative_prompt_embeds_pooled = self.encode_prompt(prompt=prompt, device=device, batch_size=batch_size,
        num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds,
        prompt_embeds_pooled=prompt_embeds_pooled, negative_prompt_embeds=negative_prompt_embeds, negative_prompt_embeds_pooled=negative_prompt_embeds_pooled)
        if images is not None: image_embeds_pooled, uncond_image_embeds_pooled = self.encode_image(images=images, device=device, dtype=dtype,
        batch_size=batch_size, num_images_per_prompt=num_images_per_prompt)
        elif image_embeds is not None:
            image_embeds_pooled = image_embeds.repeat(batch_size * num_images_per_prompt, 1, 1)
            uncond_image_embeds_pooled = torch.zeros_like(image_embeds_pooled)
        else:
            image_embeds_pooled = torch.zeros(batch_size * num_images_per_prompt, 1, self.prior.config.clip_image_in_channels, device=device, dtype=dtype)
            uncond_image_embeds_pooled = torch.zeros(batch_size * num_images_per_prompt, 1, self.prior.config.clip_image_in_channels, device=device, dtype=dtype)
        if self.do_classifier_free_guidance: image_embeds = torch.cat([image_embeds_pooled, uncond_image_embeds_pooled], dim=0)
        else: image_embeds = image_embeds_pooled
        text_encoder_hidden_states = torch.cat([prompt_embeds, negative_prompt_embeds]) if negative_prompt_embeds is not None else prompt_embeds
        text_encoder_pooled = torch.cat([prompt_embeds_pooled, negative_prompt_embeds_pooled]) if negative_prompt_embeds is not None else prompt_embeds_pooled
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        latents = self.prepare_latents(batch_size, height, width, num_images_per_prompt, dtype, device, generator, latents, self.scheduler)
        if isinstance(self.scheduler, DDPMWuerstchenScheduler): timesteps = timesteps[:-1]
        elif hasattr(self.scheduler.config, 'clip_sample') and self.scheduler.config.clip_sample: self.scheduler.config.clip_sample = False
        if hasattr(self.scheduler, 'betas'):
            alphas = 1.0 - self.scheduler.betas
            alphas_cumprod = torch.cumprod(alphas, dim=0)
        else: alphas_cumprod = []
        self._num_timesteps = len(timesteps)
        for i, t in enumerate(self.progress_bar(timesteps)):
            if not isinstance(self.scheduler, DDPMWuerstchenScheduler):
                if len(alphas_cumprod) > 0:
                    timestep_ratio = self.get_timestep_ratio_conditioning(t.long().cpu(), alphas_cumprod)
                    timestep_ratio = timestep_ratio.expand(latents.size(0)).to(dtype).to(device)
                else: timestep_ratio = t.float().div(self.scheduler.timesteps[-1]).expand(latents.size(0)).to(dtype)
            else: timestep_ratio = t.expand(latents.size(0)).to(dtype)
            predicted_image_embedding = self.prior(sample=torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents,
            timestep_ratio=torch.cat([timestep_ratio] * 2) if self.do_classifier_free_guidance else timestep_ratio, clip_text_pooled=text_encoder_pooled,
            clip_text=text_encoder_hidden_states, clip_img=image_embeds, return_dict=False)[0]
            if self.do_classifier_free_guidance:
                predicted_image_embedding_text, predicted_image_embedding_uncond = predicted_image_embedding.chunk(2)
                predicted_image_embedding = torch.lerp(predicted_image_embedding_uncond, predicted_image_embedding_text, self.guidance_scale)
            if not isinstance(self.scheduler, DDPMWuerstchenScheduler): timestep_ratio = t
            latents = self.scheduler.step(model_output=predicted_image_embedding, timestep=timestep_ratio, sample=latents, generator=generator).prev_sample
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
        self.maybe_free_model_hooks()
        if output_type == 'np':
            latents = latents.cpu().float().numpy()
            prompt_embeds = prompt_embeds.cpu().float().numpy()
            negative_prompt_embeds = negative_prompt_embeds.cpu().float().numpy() if negative_prompt_embeds is not None else None
        if not return_dict: return (latents, prompt_embeds, prompt_embeds_pooled, negative_prompt_embeds, negative_prompt_embeds_pooled)
        return StableCascadePriorPipelineOutput(image_embeddings=latents, prompt_embeds=prompt_embeds, prompt_embeds_pooled=prompt_embeds_pooled, negative_prompt_embeds=negative_prompt_embeds,
        negative_prompt_embeds_pooled=negative_prompt_embeds_pooled)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
