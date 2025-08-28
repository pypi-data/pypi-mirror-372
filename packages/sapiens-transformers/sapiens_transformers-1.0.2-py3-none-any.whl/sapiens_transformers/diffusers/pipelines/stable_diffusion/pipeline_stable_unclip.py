'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import torch
from sapiens_transformers import CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer
from sapiens_transformers.models.clip.modeling_clip import CLIPTextModelOutput
from ...image_processor import VaeImageProcessor
from ...loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, PriorTransformer, UNet2DConditionModel
from ...models.embeddings import get_timestep_embedding
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput, StableDiffusionMixin
from .stable_unclip_image_normalizer import StableUnCLIPImageNormalizer
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableUnCLIPPipeline\n\n        >>> pipe = StableUnCLIPPipeline.from_pretrained(\n        ...     "fusing/stable-unclip-2-1-l", torch_dtype=torch.float16\n        ... )  # TODO update model path\n        >>> pipe = pipe.to("cuda")\n\n        >>> prompt = "a photo of an astronaut riding a horse on mars"\n        >>> images = pipe(prompt).images\n        >>> images[0].save("astronaut_horse.png")\n        ```\n'
class StableUnCLIPPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, StableDiffusionLoraLoaderMixin):
    """Args:"""
    _exclude_from_cpu_offload = ['prior', 'image_normalizer']
    model_cpu_offload_seq = 'text_encoder->prior_text_encoder->unet->vae'
    prior_tokenizer: CLIPTokenizer
    prior_text_encoder: CLIPTextModelWithProjection
    prior: PriorTransformer
    prior_scheduler: KarrasDiffusionSchedulers
    image_normalizer: StableUnCLIPImageNormalizer
    image_noising_scheduler: KarrasDiffusionSchedulers
    tokenizer: CLIPTokenizer
    text_encoder: CLIPTextModel
    unet: UNet2DConditionModel
    scheduler: KarrasDiffusionSchedulers
    vae: AutoencoderKL
    def __init__(self, prior_tokenizer: CLIPTokenizer, prior_text_encoder: CLIPTextModelWithProjection, prior: PriorTransformer, prior_scheduler: KarrasDiffusionSchedulers,
    image_normalizer: StableUnCLIPImageNormalizer, image_noising_scheduler: KarrasDiffusionSchedulers, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModelWithProjection,
    unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers, vae: AutoencoderKL):
        super().__init__()
        self.register_modules(prior_tokenizer=prior_tokenizer, prior_text_encoder=prior_text_encoder, prior=prior, prior_scheduler=prior_scheduler, image_normalizer=image_normalizer,
        image_noising_scheduler=image_noising_scheduler, tokenizer=tokenizer, text_encoder=text_encoder, unet=unet, scheduler=scheduler, vae=vae)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def _encode_prior_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance,
    text_model_output: Optional[Union[CLIPTextModelOutput, Tuple]]=None, text_attention_mask: Optional[torch.Tensor]=None):
        if text_model_output is None:
            batch_size = len(prompt) if isinstance(prompt, list) else 1
            text_inputs = self.prior_tokenizer(prompt, padding='max_length', max_length=self.prior_tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            text_mask = text_inputs.attention_mask.bool().to(device)
            untruncated_ids = self.prior_tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
                removed_text = self.prior_tokenizer.batch_decode(untruncated_ids[:, self.prior_tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids[:, :self.prior_tokenizer.model_max_length]
            prior_text_encoder_output = self.prior_text_encoder(text_input_ids.to(device))
            prompt_embeds = prior_text_encoder_output.text_embeds
            text_enc_hid_states = prior_text_encoder_output.last_hidden_state
        else:
            batch_size = text_model_output[0].shape[0]
            prompt_embeds, text_enc_hid_states = (text_model_output[0], text_model_output[1])
            text_mask = text_attention_mask
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        text_enc_hid_states = text_enc_hid_states.repeat_interleave(num_images_per_prompt, dim=0)
        text_mask = text_mask.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            uncond_tokens = [''] * batch_size
            uncond_input = self.prior_tokenizer(uncond_tokens, padding='max_length', max_length=self.prior_tokenizer.model_max_length, truncation=True, return_tensors='pt')
            uncond_text_mask = uncond_input.attention_mask.bool().to(device)
            negative_prompt_embeds_prior_text_encoder_output = self.prior_text_encoder(uncond_input.input_ids.to(device))
            negative_prompt_embeds = negative_prompt_embeds_prior_text_encoder_output.text_embeds
            uncond_text_enc_hid_states = negative_prompt_embeds_prior_text_encoder_output.last_hidden_state
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len)
            seq_len = uncond_text_enc_hid_states.shape[1]
            uncond_text_enc_hid_states = uncond_text_enc_hid_states.repeat(1, num_images_per_prompt, 1)
            uncond_text_enc_hid_states = uncond_text_enc_hid_states.view(batch_size * num_images_per_prompt, seq_len, -1)
            uncond_text_mask = uncond_text_mask.repeat_interleave(num_images_per_prompt, dim=0)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            text_enc_hid_states = torch.cat([uncond_text_enc_hid_states, text_enc_hid_states])
            text_mask = torch.cat([uncond_text_mask, text_mask])
        return (prompt_embeds, text_enc_hid_states, text_mask)
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, **kwargs):
        deprecation_message = '`_encode_prompt()` is deprecated and it will be removed in a future version. Use `encode_prompt()` instead. Also, be aware that the output format changed from a concatenated tensor to a tuple.'
        deprecate('_encode_prompt()', '1.0.0', deprecation_message, standard_warn=False)
        prompt_embeds_tuple = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=lora_scale, **kwargs)
        prompt_embeds = torch.cat([prompt_embeds_tuple[1], prompt_embeds_tuple[0]])
        return prompt_embeds
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = text_inputs.attention_mask.to(device)
            else: attention_mask = None
            if clip_skip is None:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
                prompt_embeds = prompt_embeds[0]
            else:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask, output_hidden_states=True)
                prompt_embeds = prompt_embeds[-1][-(clip_skip + 1)]
                prompt_embeds = self.text_encoder.text_model.final_layer_norm(prompt_embeds)
        if self.text_encoder is not None: prompt_embeds_dtype = self.text_encoder.dtype
        elif self.unet is not None: prompt_embeds_dtype = self.unet.dtype
        else: prompt_embeds_dtype = prompt_embeds.dtype
        prompt_embeds = prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            if isinstance(self, TextualInversionLoaderMixin): uncond_tokens = self.maybe_convert_prompt(uncond_tokens, self.tokenizer)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = uncond_input.attention_mask.to(device)
            else: attention_mask = None
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (prompt_embeds, negative_prompt_embeds)
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def prepare_prior_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.prior_scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.prior_scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, callback_steps, noise_level, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Please make sure to define only one of the two.')
        if prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        if prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError('Provide either `negative_prompt` or `negative_prompt_embeds`. Cannot leave both `negative_prompt` and `negative_prompt_embeds` undefined.')
        if prompt is not None and negative_prompt is not None:
            if type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if noise_level < 0 or noise_level >= self.image_noising_scheduler.config.num_train_timesteps: raise ValueError(f'`noise_level` must be between 0 and {self.image_noising_scheduler.config.num_train_timesteps - 1}, inclusive.')
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def noise_image_embeddings(self, image_embeds: torch.Tensor, noise_level: int, noise: Optional[torch.Tensor]=None, generator: Optional[torch.Generator]=None):
        if noise is None: noise = randn_tensor(image_embeds.shape, generator=generator, device=image_embeds.device, dtype=image_embeds.dtype)
        noise_level = torch.tensor([noise_level] * image_embeds.shape[0], device=image_embeds.device)
        self.image_normalizer.to(image_embeds.device)
        image_embeds = self.image_normalizer.scale(image_embeds)
        image_embeds = self.image_noising_scheduler.add_noise(image_embeds, timesteps=noise_level, noise=noise)
        image_embeds = self.image_normalizer.unscale(image_embeds)
        noise_level = get_timestep_embedding(timesteps=noise_level, embedding_dim=image_embeds.shape[-1], flip_sin_to_cos=True, downscale_freq_shift=0)
        noise_level = noise_level.to(image_embeds.dtype)
        image_embeds = torch.cat((image_embeds, noise_level), 1)
        return image_embeds
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=20, guidance_scale: float=10.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[torch.Generator]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None,
    noise_level: int=0, prior_num_inference_steps: int=25, prior_guidance_scale: float=4.0, prior_latents: Optional[torch.Tensor]=None, clip_skip: Optional[int]=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt=prompt, height=height, width=width, callback_steps=callback_steps, noise_level=noise_level, negative_prompt=negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        batch_size = batch_size * num_images_per_prompt
        device = self._execution_device
        prior_do_classifier_free_guidance = prior_guidance_scale > 1.0
        prior_prompt_embeds, prior_text_encoder_hidden_states, prior_text_mask = self._encode_prior_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt,
        do_classifier_free_guidance=prior_do_classifier_free_guidance)
        self.prior_scheduler.set_timesteps(prior_num_inference_steps, device=device)
        prior_timesteps_tensor = self.prior_scheduler.timesteps
        embedding_dim = self.prior.config.embedding_dim
        prior_latents = self.prepare_latents((batch_size, embedding_dim), prior_prompt_embeds.dtype, device, generator, prior_latents, self.prior_scheduler)
        prior_extra_step_kwargs = self.prepare_prior_extra_step_kwargs(generator, eta)
        for i, t in enumerate(self.progress_bar(prior_timesteps_tensor)):
            latent_model_input = torch.cat([prior_latents] * 2) if prior_do_classifier_free_guidance else prior_latents
            latent_model_input = self.prior_scheduler.scale_model_input(latent_model_input, t)
            predicted_image_embedding = self.prior(latent_model_input, timestep=t, proj_embedding=prior_prompt_embeds, encoder_hidden_states=prior_text_encoder_hidden_states,
            attention_mask=prior_text_mask).predicted_image_embedding
            if prior_do_classifier_free_guidance:
                predicted_image_embedding_uncond, predicted_image_embedding_text = predicted_image_embedding.chunk(2)
                predicted_image_embedding = predicted_image_embedding_uncond + prior_guidance_scale * (predicted_image_embedding_text - predicted_image_embedding_uncond)
            prior_latents = self.prior_scheduler.step(predicted_image_embedding, timestep=t, sample=prior_latents, **prior_extra_step_kwargs, return_dict=False)[0]
            if callback is not None and i % callback_steps == 0: callback(i, t, prior_latents)
        prior_latents = self.prior.post_process_latents(prior_latents)
        image_embeds = prior_latents
        do_classifier_free_guidance = guidance_scale > 1.0
        text_encoder_lora_scale = cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        image_embeds = self.noise_image_embeddings(image_embeds=image_embeds, noise_level=noise_level, generator=generator)
        if do_classifier_free_guidance:
            negative_prompt_embeds = torch.zeros_like(image_embeds)
            image_embeds = torch.cat([negative_prompt_embeds, image_embeds])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        latents = self.prepare_latents(shape=shape, dtype=prompt_embeds.dtype, device=device, generator=generator, latents=latents, scheduler=self.scheduler)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, class_labels=image_embeds, cross_attention_kwargs=cross_attention_kwargs, return_dict=False)[0]
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
            latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
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
