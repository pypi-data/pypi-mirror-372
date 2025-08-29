'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ...image_processor import VaeImageProcessor
from ...loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, MultiAdapter, T2IAdapter, UNet2DConditionModel
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import PIL_INTERPOLATION, USE_PEFT_BACKEND, BaseOutput, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion.safety_checker import StableDiffusionSafetyChecker
@dataclass
class StableDiffusionAdapterPipelineOutput(BaseOutput):
    """Args:"""
    images: Union[List[PIL.Image.Image], np.ndarray]
    nsfw_content_detected: Optional[List[bool]]
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from PIL import Image\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableDiffusionAdapterPipeline, T2IAdapter\n\n        >>> image = load_image(\n        ...     "https://huggingface.co/datasets/diffusers/docs-images/resolve/main/t2i-adapter/color_ref.png"\n        ... )\n\n        >>> color_palette = image.resize((8, 8))\n        >>> color_palette = color_palette.resize((512, 512), resample=Image.Resampling.NEAREST)\n\n        >>> adapter = T2IAdapter.from_pretrained("TencentARC/t2iadapter_color_sd14v1", torch_dtype=torch.float16)\n        >>> pipe = StableDiffusionAdapterPipeline.from_pretrained(\n        ...     "CompVis/stable-diffusion-v1-4",\n        ...     adapter=adapter,\n        ...     torch_dtype=torch.float16,\n        ... )\n\n        >>> pipe.to("cuda")\n\n        >>> out_image = pipe(\n        ...     "At night, glowing cubes in front of the beach",\n        ...     image=color_palette,\n        ... ).images[0]\n        ```\n'
def _preprocess_adapter_image(image, height, width):
    if isinstance(image, torch.Tensor): return image
    elif isinstance(image, PIL.Image.Image): image = [image]
    if isinstance(image[0], PIL.Image.Image):
        image = [np.array(i.resize((width, height), resample=PIL_INTERPOLATION['lanczos'])) for i in image]
        image = [i[None, ..., None] if i.ndim == 2 else i[None, ...] for i in image]
        image = np.concatenate(image, axis=0)
        image = np.array(image).astype(np.float32) / 255.0
        image = image.transpose(0, 3, 1, 2)
        image = torch.from_numpy(image)
    elif isinstance(image[0], torch.Tensor):
        if image[0].ndim == 3: image = torch.stack(image, dim=0)
        elif image[0].ndim == 4: image = torch.cat(image, dim=0)
        else: raise ValueError(f'Invalid image tensor! Expecting image tensor with 3 or 4 dimension, but recive: {image[0].ndim}')
    return image
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None,
timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, **kwargs):
    """Returns:"""
    if timesteps is not None and sigmas is not None: raise ValueError('Only one of `timesteps` or `sigmas` can be passed. Please choose one to set custom values')
    if timesteps is not None:
        accepts_timesteps = 'timesteps' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accepts_timesteps: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom timestep schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(timesteps=timesteps, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    elif sigmas is not None:
        accept_sigmas = 'sigmas' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accept_sigmas: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom sigmas schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(sigmas=sigmas, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    else:
        scheduler.set_timesteps(num_inference_steps, device=device, **kwargs)
        timesteps = scheduler.timesteps
    return (timesteps, num_inference_steps)
class StableDiffusionAdapterPipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->adapter->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, adapter: Union[T2IAdapter, MultiAdapter, List[T2IAdapter]],
    scheduler: KarrasDiffusionSchedulers, safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        if isinstance(adapter, (list, tuple)): adapter = MultiAdapter(adapter)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, adapter=adapter, scheduler=scheduler,
        safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
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
    def run_safety_checker(self, image, device, dtype):
        if self.safety_checker is None: has_nsfw_concept = None
        else:
            if torch.is_tensor(image): feature_extractor_input = self.image_processor.postprocess(image, output_type='pil')
            else: feature_extractor_input = self.image_processor.numpy_to_pil(image)
            safety_checker_input = self.feature_extractor(feature_extractor_input, return_tensors='pt').to(device)
            image, has_nsfw_concept = self.safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(dtype))
        return (image, has_nsfw_concept)
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, callback_steps, image, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if isinstance(self.adapter, MultiAdapter):
            if not isinstance(image, list): raise ValueError('MultiAdapter is enabled, but `image` is not a list. Please pass a list of images to `image`.')
            if len(image) != len(self.adapter.adapters): raise ValueError(f'MultiAdapter requires passing the same number of images as adapters. Given {len(image)} images and {len(self.adapter.adapters)} adapters.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def _default_height_width(self, height, width, image):
        while isinstance(image, list): image = image[0]
        if height is None:
            if isinstance(image, PIL.Image.Image): height = image.height
            elif isinstance(image, torch.Tensor): height = image.shape[-2]
            height = height // self.adapter.downscale_factor * self.adapter.downscale_factor
        if width is None:
            if isinstance(image, PIL.Image.Image): width = image.width
            elif isinstance(image, torch.Tensor): width = image.shape[-1]
            width = width // self.adapter.downscale_factor * self.adapter.downscale_factor
        return (height, width)
    def get_guidance_scale_embedding(self, w: torch.Tensor, embedding_dim: int=512, dtype: torch.dtype=torch.float32) -> torch.Tensor:
        """Returns:"""
        assert len(w.shape) == 1
        w = w * 1000.0
        half_dim = embedding_dim // 2
        emb = torch.log(torch.tensor(10000.0)) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, dtype=dtype) * -emb)
        emb = w.to(dtype)[:, None] * emb[None, :]
        emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=1)
        if embedding_dim % 2 == 1: emb = torch.nn.functional.pad(emb, (0, 1))
        assert emb.shape == (w.shape[0], embedding_dim)
        return emb
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1 and self.unet.config.time_cond_proj_dim is None
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, image: Union[torch.Tensor, PIL.Image.Image, List[PIL.Image.Image]]=None, height: Optional[int]=None, width: Optional[int]=None,
    num_inference_steps: int=50, timesteps: List[int]=None, sigmas: List[float]=None, guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None,
    num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, adapter_conditioning_scale: Union[float,
    List[float]]=1.0, clip_skip: Optional[int]=None):
        """Examples:"""
        height, width = self._default_height_width(height, width, image)
        device = self._execution_device
        self.check_inputs(prompt, height, width, callback_steps, image, negative_prompt, prompt_embeds, negative_prompt_embeds)
        self._guidance_scale = guidance_scale
        if isinstance(self.adapter, MultiAdapter):
            adapter_input = []
            for one_image in image:
                one_image = _preprocess_adapter_image(one_image, height, width)
                one_image = one_image.to(device=device, dtype=self.adapter.dtype)
                adapter_input.append(one_image)
        else:
            adapter_input = _preprocess_adapter_image(image, height, width)
            adapter_input = adapter_input.to(device=device, dtype=self.adapter.dtype)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, self.do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clip_skip=clip_skip)
        if self.do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        timestep_cond = None
        if self.unet.config.time_cond_proj_dim is not None:
            guidance_scale_tensor = torch.tensor(self.guidance_scale - 1).repeat(batch_size * num_images_per_prompt)
            timestep_cond = self.get_guidance_scale_embedding(guidance_scale_tensor, embedding_dim=self.unet.config.time_cond_proj_dim).to(device=device, dtype=latents.dtype)
        if isinstance(self.adapter, MultiAdapter):
            adapter_state = self.adapter(adapter_input, adapter_conditioning_scale)
            for k, v in enumerate(adapter_state): adapter_state[k] = v
        else:
            adapter_state = self.adapter(adapter_input)
            for k, v in enumerate(adapter_state): adapter_state[k] = v * adapter_conditioning_scale
        if num_images_per_prompt > 1:
            for k, v in enumerate(adapter_state): adapter_state[k] = v.repeat(num_images_per_prompt, 1, 1, 1)
        if self.do_classifier_free_guidance:
            for k, v in enumerate(adapter_state): adapter_state[k] = torch.cat([v] * 2, dim=0)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, timestep_cond=timestep_cond, cross_attention_kwargs=cross_attention_kwargs,
                down_intrablock_additional_residuals=[state.clone() for state in adapter_state], return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if output_type == 'latent':
            image = latents
            has_nsfw_concept = None
        elif output_type == 'pil':
            image = self.decode_latents(latents)
            image, has_nsfw_concept = self.run_safety_checker(image, device, prompt_embeds.dtype)
            image = self.numpy_to_pil(image)
        else:
            image = self.decode_latents(latents)
            image, has_nsfw_concept = self.run_safety_checker(image, device, prompt_embeds.dtype)
        self.maybe_free_model_hooks()
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionAdapterPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
