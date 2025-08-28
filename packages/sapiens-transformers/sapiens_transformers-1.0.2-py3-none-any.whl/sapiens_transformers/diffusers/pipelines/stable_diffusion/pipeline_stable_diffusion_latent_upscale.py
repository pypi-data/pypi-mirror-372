'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Union
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin
from ...models import AutoencoderKL, UNet2DConditionModel
from ...schedulers import EulerDiscreteScheduler
from ...utils import deprecate
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput, StableDiffusionMixin
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
def preprocess(image):
    if isinstance(image, torch.Tensor): return image
    elif isinstance(image, PIL.Image.Image): image = [image]
    if isinstance(image[0], PIL.Image.Image):
        w, h = image[0].size
        w, h = (x - x % 64 for x in (w, h))
        image = [np.array(i.resize((w, h)))[None, :] for i in image]
        image = np.concatenate(image, axis=0)
        image = np.array(image).astype(np.float32) / 255.0
        image = image.transpose(0, 3, 1, 2)
        image = 2.0 * image - 1.0
        image = torch.from_numpy(image)
    elif isinstance(image[0], torch.Tensor): image = torch.cat(image, dim=0)
    return image
class StableDiffusionLatentUpscalePipeline(DiffusionPipeline, StableDiffusionMixin, FromSingleFileMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: EulerDiscreteScheduler):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, resample='bicubic')
    def _encode_prompt(self, prompt, device, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, **kwargs):
        deprecation_message = '`_encode_prompt()` is deprecated and it will be removed in a future version. Use `encode_prompt()` instead. Also, be aware that the output format changed from a concatenated tensor to a tuple.'
        deprecate('_encode_prompt()', '1.0.0', deprecation_message, standard_warn=False)
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, device=device,
        do_classifier_free_guidance=do_classifier_free_guidance, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds, **kwargs)
        prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embeds, pooled_prompt_embeds])
        return (prompt_embeds, pooled_prompt_embeds)
    def encode_prompt(self, prompt, device, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None):
        """Args:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None or pooled_prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_length=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            text_encoder_out = self.text_encoder(text_input_ids.to(device), output_hidden_states=True)
            prompt_embeds = text_encoder_out.hidden_states[-1]
            pooled_prompt_embeds = text_encoder_out.pooler_output
        if do_classifier_free_guidance:
            if negative_prompt_embeds is None or negative_pooled_prompt_embeds is None:
                uncond_tokens: List[str]
                if negative_prompt is None: uncond_tokens = [''] * batch_size
                elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
                elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
                elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
                else: uncond_tokens = negative_prompt
                max_length = text_input_ids.shape[-1]
                uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_length=True, return_tensors='pt')
                uncond_encoder_out = self.text_encoder(uncond_input.input_ids.to(device), output_hidden_states=True)
                negative_prompt_embeds = uncond_encoder_out.hidden_states[-1]
                negative_pooled_prompt_embeds = uncond_encoder_out.pooler_output
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def check_inputs(self, prompt, image, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None,
    pooled_prompt_embeds=None, negative_pooled_prompt_embeds=None):
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str)) and (not isinstance(prompt, list)): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        if not isinstance(image, torch.Tensor) and (not isinstance(image, np.ndarray)) and (not isinstance(image, PIL.Image.Image)) and (not isinstance(image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image` or `list` but is {type(image)}')
        if isinstance(image, (list, torch.Tensor)):
            if prompt is not None:
                if isinstance(prompt, str): batch_size = 1
                else: batch_size = len(prompt)
            else: batch_size = prompt_embeds.shape[0]
            if isinstance(image, list): image_batch_size = len(image)
            else: image_batch_size = image.shape[0] if image.ndim == 4 else 1
            if batch_size != image_batch_size: raise ValueError(f'`prompt` has batch size {batch_size} and `image` has batch size {image_batch_size}. Please make sure that passed `prompt` matches the batch size of `image`.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, height, width)
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    def __call__(self, prompt: Union[str, List[str]]=None, image: PipelineImageInput=None, num_inference_steps: int=75, guidance_scale: float=9.0, negative_prompt: Optional[Union[str,
    List[str]]]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Examples:"""
        self.check_inputs(prompt, image, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
        if prompt is not None: batch_size = 1 if isinstance(prompt, str) else len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        if guidance_scale == 0: prompt = [''] * batch_size
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt, device, do_classifier_free_guidance, negative_prompt,
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
        if do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embeds, pooled_prompt_embeds])
        image = self.image_processor.preprocess(image)
        image = image.to(dtype=prompt_embeds.dtype, device=device)
        if image.shape[1] == 3: image = retrieve_latents(self.vae.encode(image), generator=generator) * self.vae.config.scaling_factor
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        batch_multiplier = 2 if do_classifier_free_guidance else 1
        image = image[None, :] if image.ndim == 3 else image
        image = torch.cat([image] * batch_multiplier)
        noise_level = torch.tensor([0.0], dtype=torch.float32, device=device)
        noise_level = torch.cat([noise_level] * image.shape[0])
        inv_noise_level = (noise_level ** 2 + 1) ** (-0.5)
        image_cond = F.interpolate(image, scale_factor=2, mode='nearest') * inv_noise_level[:, None, None, None]
        image_cond = image_cond.to(prompt_embeds.dtype)
        noise_level_embed = torch.cat([torch.ones(pooled_prompt_embeds.shape[0], 64, dtype=pooled_prompt_embeds.dtype, device=device), torch.zeros(pooled_prompt_embeds.shape[0], 64,
        dtype=pooled_prompt_embeds.dtype, device=device)], dim=1)
        timestep_condition = torch.cat([noise_level_embed, pooled_prompt_embeds], dim=1)
        height, width = image.shape[2:]
        num_channels_latents = self.vae.config.latent_channels
        latents = self.prepare_latents(batch_size, num_channels_latents, height * 2, width * 2, prompt_embeds.dtype, device, generator, latents)
        num_channels_image = image.shape[1]
        if num_channels_latents + num_channels_image != self.unet.config.in_channels: raise ValueError(f'Incorrect configuration settings! The config of `pipeline.unet`: {self.unet.config} expects {self.unet.config.in_channels} but received `num_channels_latents`: {num_channels_latents} + `num_channels_image`: {num_channels_image}  = {num_channels_latents + num_channels_image}. Please verify the config of `pipeline.unet` or your `image` input.')
        num_warmup_steps = 0
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                sigma = self.scheduler.sigmas[i]
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                scaled_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                scaled_model_input = torch.cat([scaled_model_input, image_cond], dim=1)
                timestep = torch.log(sigma) * 0.25
                noise_pred = self.unet(scaled_model_input, timestep, encoder_hidden_states=prompt_embeds, timestep_cond=timestep_condition).sample
                noise_pred = noise_pred[:, :-1]
                inv_sigma = 1 / (sigma ** 2 + 1)
                noise_pred = inv_sigma * latent_model_input + self.scheduler.scale_model_input(sigma, t) * noise_pred
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if not output_type == 'latent': image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
        else: image = latents
        image = self.image_processor.postprocess(image, output_type=output_type)
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
