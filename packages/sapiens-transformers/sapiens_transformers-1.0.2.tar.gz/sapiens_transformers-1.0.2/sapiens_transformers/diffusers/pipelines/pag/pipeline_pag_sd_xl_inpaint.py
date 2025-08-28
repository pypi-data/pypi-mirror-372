'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer, CLIPVisionModelWithProjection
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin, IPAdapterMixin, StableDiffusionXLLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, ImageProjection, UNet2DConditionModel
from ...models.attention_processor import AttnProcessor2_0, XFormersAttnProcessor
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, is_invisible_watermark_available, is_torch_xla_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from .pag_utils import PAGMixin
if is_invisible_watermark_available(): from ..stable_diffusion_xl.watermark import StableDiffusionXLWatermarker
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AutoPipelineForInpainting\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n        >>> pipe = AutoPipelineForInpainting.from_pretrained(\n        ...     "stabilityai/stable-diffusion-xl-base-1.0",\n        ...     torch_dtype=torch.float16,\n        ...     variant="fp16",\n        ...     enable_pag=True,\n        ... )\n        >>> pipe.to("cuda")\n\n        >>> img_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo.png"\n        >>> mask_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo_mask.png"\n\n        >>> init_image = load_image(img_url).convert("RGB")\n        >>> mask_image = load_image(mask_url).convert("RGB")\n\n        >>> prompt = "A majestic tiger sitting on a bench"\n        >>> image = pipe(\n        ...     prompt=prompt,\n        ...     image=init_image,\n        ...     mask_image=mask_image,\n        ...     num_inference_steps=50,\n        ...     strength=0.80,\n        ...     pag_scale=0.3,\n        ... ).images[0]\n        ```\n'
def rescale_noise_cfg(noise_cfg, noise_pred_text, guidance_rescale=0.0):
    """Returns:"""
    std_text = noise_pred_text.std(dim=list(range(1, noise_pred_text.ndim)), keepdim=True)
    std_cfg = noise_cfg.std(dim=list(range(1, noise_cfg.ndim)), keepdim=True)
    noise_pred_rescaled = noise_cfg * (std_text / std_cfg)
    noise_cfg = guidance_rescale * noise_pred_rescaled + (1 - guidance_rescale) * noise_cfg
    return noise_cfg
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None, timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, **kwargs):
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
class StableDiffusionXLPAGInpaintPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, StableDiffusionXLLoraLoaderMixin, FromSingleFileMixin, IPAdapterMixin, PAGMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->image_encoder->unet->vae'
    _optional_components = ['tokenizer', 'tokenizer_2', 'text_encoder', 'text_encoder_2', 'image_encoder', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'add_text_embeds', 'add_time_ids', 'negative_pooled_prompt_embeds', 'add_neg_time_ids', 'mask', 'masked_image_latents']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, text_encoder_2: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, tokenizer_2: CLIPTokenizer, unet: UNet2DConditionModel,
    scheduler: KarrasDiffusionSchedulers, image_encoder: CLIPVisionModelWithProjection=None, feature_extractor: CLIPImageProcessor=None, requires_aesthetics_score: bool=False,
    force_zeros_for_empty_prompt: bool=True, add_watermarker: Optional[bool]=None, pag_applied_layers: Union[str, List[str]]='mid'):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, tokenizer=tokenizer, tokenizer_2=tokenizer_2, unet=unet,
        image_encoder=image_encoder, feature_extractor=feature_extractor, scheduler=scheduler)
        self.register_to_config(force_zeros_for_empty_prompt=force_zeros_for_empty_prompt)
        self.register_to_config(requires_aesthetics_score=requires_aesthetics_score)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.mask_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_normalize=False, do_binarize=True, do_convert_grayscale=True)
        add_watermarker = add_watermarker if add_watermarker is not None else is_invisible_watermark_available()
        if add_watermarker: self.watermark = StableDiffusionXLWatermarker()
        else: self.watermark = None
        self.set_pag_applied_layers(pag_applied_layers)
    def encode_image(self, image, device, num_images_per_prompt, output_hidden_states=None):
        dtype = next(self.image_encoder.parameters()).dtype
        if not isinstance(image, torch.Tensor): image = self.feature_extractor(image, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=dtype)
        if output_hidden_states:
            image_enc_hidden_states = self.image_encoder(image, output_hidden_states=True).hidden_states[-2]
            image_enc_hidden_states = image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_enc_hidden_states = self.image_encoder(torch.zeros_like(image), output_hidden_states=True).hidden_states[-2]
            uncond_image_enc_hidden_states = uncond_image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            return (image_enc_hidden_states, uncond_image_enc_hidden_states)
        else:
            image_embeds = self.image_encoder(image).image_embeds
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_embeds = torch.zeros_like(image_embeds)
            return (image_embeds, uncond_image_embeds)
    def prepare_ip_adapter_image_embeds(self, ip_adapter_image, ip_adapter_image_embeds, device, num_images_per_prompt, do_classifier_free_guidance):
        image_embeds = []
        if do_classifier_free_guidance: negative_image_embeds = []
        if ip_adapter_image_embeds is None:
            if not isinstance(ip_adapter_image, list): ip_adapter_image = [ip_adapter_image]
            if len(ip_adapter_image) != len(self.unet.encoder_hid_proj.image_projection_layers): raise ValueError(f'`ip_adapter_image` must have same length as the number of IP Adapters. Got {len(ip_adapter_image)} images and {len(self.unet.encoder_hid_proj.image_projection_layers)} IP Adapters.')
            for single_ip_adapter_image, image_proj_layer in zip(ip_adapter_image, self.unet.encoder_hid_proj.image_projection_layers):
                output_hidden_state = not isinstance(image_proj_layer, ImageProjection)
                single_image_embeds, single_negative_image_embeds = self.encode_image(single_ip_adapter_image, device, 1, output_hidden_state)
                image_embeds.append(single_image_embeds[None, :])
                if do_classifier_free_guidance: negative_image_embeds.append(single_negative_image_embeds[None, :])
        else:
            for single_image_embeds in ip_adapter_image_embeds:
                if do_classifier_free_guidance:
                    single_negative_image_embeds, single_image_embeds = single_image_embeds.chunk(2)
                    negative_image_embeds.append(single_negative_image_embeds)
                image_embeds.append(single_image_embeds)
        ip_adapter_image_embeds = []
        for i, single_image_embeds in enumerate(image_embeds):
            single_image_embeds = torch.cat([single_image_embeds] * num_images_per_prompt, dim=0)
            if do_classifier_free_guidance:
                single_negative_image_embeds = torch.cat([negative_image_embeds[i]] * num_images_per_prompt, dim=0)
                single_image_embeds = torch.cat([single_negative_image_embeds, single_image_embeds], dim=0)
            single_image_embeds = single_image_embeds.to(device=device)
            ip_adapter_image_embeds.append(single_image_embeds)
        return ip_adapter_image_embeds
    def encode_prompt(self, prompt: str, prompt_2: Optional[str]=None, device: Optional[torch.device]=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True,
    negative_prompt: Optional[str]=None, negative_prompt_2: Optional[str]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, StableDiffusionXLLoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
                else: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder_2, lora_scale)
                else: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        tokenizers = [self.tokenizer, self.tokenizer_2] if self.tokenizer is not None else [self.tokenizer_2]
        text_encoders = [self.text_encoder, self.text_encoder_2] if self.text_encoder is not None else [self.text_encoder_2]
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            prompt_embeds_list = []
            prompts = [prompt, prompt_2]
            for prompt, tokenizer, text_encoder in zip(prompts, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, tokenizer)
                text_inputs = tokenizer(prompt, padding='max_length', max_length=tokenizer.model_max_length, truncation=True, return_tensors='pt')
                text_input_ids = text_inputs.input_ids
                untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
                if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, tokenizer.model_max_length - 1:-1])
                prompt_embeds = text_encoder(text_input_ids.to(device), output_hidden_states=True)
                pooled_prompt_embeds = prompt_embeds[0]
                if clip_skip is None: prompt_embeds = prompt_embeds.hidden_states[-2]
                else: prompt_embeds = prompt_embeds.hidden_states[-(clip_skip + 2)]
                prompt_embeds_list.append(prompt_embeds)
            prompt_embeds = torch.concat(prompt_embeds_list, dim=-1)
        zero_out_negative_prompt = negative_prompt is None and self.config.force_zeros_for_empty_prompt
        if do_classifier_free_guidance and negative_prompt_embeds is None and zero_out_negative_prompt:
            negative_prompt_embeds = torch.zeros_like(prompt_embeds)
            negative_pooled_prompt_embeds = torch.zeros_like(pooled_prompt_embeds)
        elif do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt_2 = negative_prompt_2 or negative_prompt
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            negative_prompt_2 = batch_size * [negative_prompt_2] if isinstance(negative_prompt_2, str) else negative_prompt_2
            uncond_tokens: List[str]
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = [negative_prompt, negative_prompt_2]
            negative_prompt_embeds_list = []
            for negative_prompt, tokenizer, text_encoder in zip(uncond_tokens, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): negative_prompt = self.maybe_convert_prompt(negative_prompt, tokenizer)
                max_length = prompt_embeds.shape[1]
                uncond_input = tokenizer(negative_prompt, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
                negative_prompt_embeds = text_encoder(uncond_input.input_ids.to(device), output_hidden_states=True)
                negative_pooled_prompt_embeds = negative_prompt_embeds[0]
                negative_prompt_embeds = negative_prompt_embeds.hidden_states[-2]
                negative_prompt_embeds_list.append(negative_prompt_embeds)
            negative_prompt_embeds = torch.concat(negative_prompt_embeds_list, dim=-1)
        if self.text_encoder_2 is not None: prompt_embeds = prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
        else: prompt_embeds = prompt_embeds.to(dtype=self.unet.dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            if self.text_encoder_2 is not None: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
            else: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.unet.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if do_classifier_free_guidance: negative_pooled_prompt_embeds = negative_pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, prompt_2, image, mask_image, height, width, strength, callback_steps, output_type, negative_prompt=None, negative_prompt_2=None, prompt_embeds=None,
    negative_prompt_embeds=None, ip_adapter_image=None, ip_adapter_image_embeds=None, callback_on_step_end_tensor_inputs=None, padding_mask_crop=None):
        if strength < 0 or strength > 1: raise ValueError(f'The value of strength should in [0.0, 1.0] but is {strength}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_2 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_2`: {negative_prompt_2} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if padding_mask_crop is not None:
            if not isinstance(image, PIL.Image.Image): raise ValueError(f'The image should be a PIL image when inpainting mask crop, but is of type {type(image)}.')
            if not isinstance(mask_image, PIL.Image.Image): raise ValueError(f'The mask image should be a PIL image when inpainting mask crop, but is of type {type(mask_image)}.')
            if output_type != 'pil': raise ValueError(f'The output type should be PIL when inpainting mask crop, but is {output_type}.')
        if ip_adapter_image is not None and ip_adapter_image_embeds is not None: raise ValueError('Provide either `ip_adapter_image` or `ip_adapter_image_embeds`. Cannot leave both `ip_adapter_image` and `ip_adapter_image_embeds` defined.')
        if ip_adapter_image_embeds is not None:
            if not isinstance(ip_adapter_image_embeds, list): raise ValueError(f'`ip_adapter_image_embeds` has to be of type `list` but is {type(ip_adapter_image_embeds)}')
            elif ip_adapter_image_embeds[0].ndim not in [3, 4]: raise ValueError(f'`ip_adapter_image_embeds` has to be a list of 3D or 4D tensors but is {ip_adapter_image_embeds[0].ndim}D')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None, image=None, timestep=None, is_strength_max=True,
    add_noise=True, return_noise=False, return_image_latents=False):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if (image is None or timestep is None) and (not is_strength_max): raise ValueError('Since strength < 1. initial latents are to be initialised as a combination of Image + Noise.However, either the image or the noise timestep has not been provided.')
        if image.shape[1] == 4:
            image_latents = image.to(device=device, dtype=dtype)
            image_latents = image_latents.repeat(batch_size // image_latents.shape[0], 1, 1, 1)
        elif return_image_latents or (latents is None and (not is_strength_max)):
            image = image.to(device=device, dtype=dtype)
            image_latents = self._encode_vae_image(image=image, generator=generator)
            image_latents = image_latents.repeat(batch_size // image_latents.shape[0], 1, 1, 1)
        if latents is None and add_noise:
            noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            latents = noise if is_strength_max else self.scheduler.add_noise(image_latents, noise, timestep)
            latents = latents * self.scheduler.init_noise_sigma if is_strength_max else latents
        elif add_noise:
            noise = latents.to(device)
            latents = noise * self.scheduler.init_noise_sigma
        else:
            noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            latents = image_latents.to(device)
        outputs = (latents,)
        if return_noise: outputs += (noise,)
        if return_image_latents: outputs += (image_latents,)
        return outputs
    def _encode_vae_image(self, image: torch.Tensor, generator: torch.Generator):
        dtype = image.dtype
        if self.vae.config.force_upcast:
            image = image.float()
            self.vae.to(dtype=torch.float32)
        if isinstance(generator, list):
            image_latents = [retrieve_latents(self.vae.encode(image[i:i + 1]), generator=generator[i]) for i in range(image.shape[0])]
            image_latents = torch.cat(image_latents, dim=0)
        else: image_latents = retrieve_latents(self.vae.encode(image), generator=generator)
        if self.vae.config.force_upcast: self.vae.to(dtype)
        image_latents = image_latents.to(dtype)
        image_latents = self.vae.config.scaling_factor * image_latents
        return image_latents
    def prepare_mask_latents(self, mask, masked_image, batch_size, height, width, dtype, device, generator, do_classifier_free_guidance):
        mask = torch.nn.functional.interpolate(mask, size=(height // self.vae_scale_factor, width // self.vae_scale_factor))
        mask = mask.to(device=device, dtype=dtype)
        if mask.shape[0] < batch_size:
            if not batch_size % mask.shape[0] == 0: raise ValueError(f"The passed mask and the required batch size don't match. Masks are supposed to be duplicated to a total batch size of {batch_size}, but {mask.shape[0]} masks were passed. Make sure the number of masks that you pass is divisible by the total requested batch size.")
            mask = mask.repeat(batch_size // mask.shape[0], 1, 1, 1)
        mask = torch.cat([mask] * 2) if do_classifier_free_guidance else mask
        if masked_image is not None and masked_image.shape[1] == 4: masked_image_latents = masked_image
        else: masked_image_latents = None
        if masked_image is not None:
            if masked_image_latents is None:
                masked_image = masked_image.to(device=device, dtype=dtype)
                masked_image_latents = self._encode_vae_image(masked_image, generator=generator)
            if masked_image_latents.shape[0] < batch_size:
                if not batch_size % masked_image_latents.shape[0] == 0: raise ValueError(f"The passed images and the required batch size don't match. Images are supposed to be duplicated to a total batch size of {batch_size}, but {masked_image_latents.shape[0]} images were passed. Make sure the number of images that you pass is divisible by the total requested batch size.")
                masked_image_latents = masked_image_latents.repeat(batch_size // masked_image_latents.shape[0], 1, 1, 1)
            masked_image_latents = torch.cat([masked_image_latents] * 2) if do_classifier_free_guidance else masked_image_latents
            masked_image_latents = masked_image_latents.to(device=device, dtype=dtype)
        return (mask, masked_image_latents)
    def get_timesteps(self, num_inference_steps, strength, device, denoising_start=None):
        if denoising_start is None:
            init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
            t_start = max(num_inference_steps - init_timestep, 0)
            timesteps = self.scheduler.timesteps[t_start * self.scheduler.order:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start * self.scheduler.order)
            return (timesteps, num_inference_steps - t_start)
        else:
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - denoising_start * self.scheduler.config.num_train_timesteps))
            num_inference_steps = (self.scheduler.timesteps < discrete_timestep_cutoff).sum().item()
            if self.scheduler.order == 2 and num_inference_steps % 2 == 0: num_inference_steps = num_inference_steps + 1
            t_start = len(self.scheduler.timesteps) - num_inference_steps
            timesteps = self.scheduler.timesteps[t_start:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start)
            return (timesteps, num_inference_steps)
    def _get_add_time_ids(self, original_size, crops_coords_top_left, target_size, aesthetic_score, negative_aesthetic_score, negative_original_size, negative_crops_coords_top_left,
    negative_target_size, dtype, text_encoder_projection_dim=None):
        if self.config.requires_aesthetics_score:
            add_time_ids = list(original_size + crops_coords_top_left + (aesthetic_score,))
            add_neg_time_ids = list(negative_original_size + negative_crops_coords_top_left + (negative_aesthetic_score,))
        else:
            add_time_ids = list(original_size + crops_coords_top_left + target_size)
            add_neg_time_ids = list(negative_original_size + crops_coords_top_left + negative_target_size)
        passed_add_embed_dim = self.unet.config.addition_time_embed_dim * len(add_time_ids) + text_encoder_projection_dim
        expected_add_embed_dim = self.unet.add_embedding.linear_1.in_features
        if expected_add_embed_dim > passed_add_embed_dim and expected_add_embed_dim - passed_add_embed_dim == self.unet.config.addition_time_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. Please make sure to enable `requires_aesthetics_score` with `pipe.register_to_config(requires_aesthetics_score=True)` to make sure `aesthetic_score` {aesthetic_score} and `negative_aesthetic_score` {negative_aesthetic_score} is correctly used by the model.')
        elif expected_add_embed_dim < passed_add_embed_dim and passed_add_embed_dim - expected_add_embed_dim == self.unet.config.addition_time_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. Please make sure to disable `requires_aesthetics_score` with `pipe.register_to_config(requires_aesthetics_score=False)` to make sure `target_size` {target_size} is correctly used by the model.')
        elif expected_add_embed_dim != passed_add_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. The model has an incorrect config. Please check `unet.config.time_embedding_type` and `text_encoder_2.config.projection_dim`.')
        add_time_ids = torch.tensor([add_time_ids], dtype=dtype)
        add_neg_time_ids = torch.tensor([add_neg_time_ids], dtype=dtype)
        return (add_time_ids, add_neg_time_ids)
    def upcast_vae(self):
        dtype = self.vae.dtype
        self.vae.to(dtype=torch.float32)
        use_torch_2_0_or_xformers = isinstance(self.vae.decoder.mid_block.attentions[0].processor, (AttnProcessor2_0, XFormersAttnProcessor))
        if use_torch_2_0_or_xformers:
            self.vae.post_quant_conv.to(dtype)
            self.vae.decoder.conv_in.to(dtype)
            self.vae.decoder.mid_block.to(dtype)
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
    def guidance_rescale(self): return self._guidance_rescale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1 and self.unet.config.time_cond_proj_dim is None
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @property
    def denoising_end(self): return self._denoising_end
    @property
    def denoising_start(self): return self._denoising_start
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, image: PipelineImageInput=None, mask_image: PipelineImageInput=None,
    masked_image_latents: torch.Tensor=None, height: Optional[int]=None, width: Optional[int]=None, padding_mask_crop: Optional[int]=None, strength: float=0.9999,
    num_inference_steps: int=50, timesteps: List[int]=None, sigmas: List[float]=None, denoising_start: Optional[float]=None, denoising_end: Optional[float]=None,
    guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str, List[str]]]=None,
    num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, ip_adapter_image: Optional[PipelineImageInput]=None,
    ip_adapter_image_embeds: Optional[List[torch.Tensor]]=None, output_type: Optional[str]='pil', return_dict: bool=True, cross_attention_kwargs: Optional[Dict[str, Any]]=None,
    guidance_rescale: float=0.0, original_size: Tuple[int, int]=None, crops_coords_top_left: Tuple[int, int]=(0, 0), target_size: Tuple[int, int]=None,
    negative_original_size: Optional[Tuple[int, int]]=None, negative_crops_coords_top_left: Tuple[int, int]=(0, 0), negative_target_size: Optional[Tuple[int,
    int]]=None, aesthetic_score: float=6.0, negative_aesthetic_score: float=2.5, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Union[Callable[[int,
    int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], pag_scale: float=3.0, pag_adaptive_scale: float=0.0):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, prompt_2, image, mask_image, height, width, strength, None, output_type, negative_prompt, negative_prompt_2, prompt_embeds,
        negative_prompt_embeds, ip_adapter_image, ip_adapter_image_embeds, callback_on_step_end_tensor_inputs, padding_mask_crop)
        self._guidance_scale = guidance_scale
        self._guidance_rescale = guidance_rescale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        self._denoising_end = denoising_end
        self._denoising_start = denoising_start
        self._interrupt = False
        self._pag_scale = pag_scale
        self._pag_adaptive_scale = pag_adaptive_scale
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        text_encoder_lora_scale = self.cross_attention_kwargs.get('scale', None) if self.cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, device=device,
        num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt,
        negative_prompt_2=negative_prompt_2, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds,
        negative_pooled_prompt_embeds=negative_pooled_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=self.clip_skip)
        def denoising_value_valid(dnv): return isinstance(dnv, float) and 0 < dnv < 1
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, strength, device, denoising_start=self.denoising_start if denoising_value_valid(self.denoising_start) else None)
        if num_inference_steps < 1: raise ValueError(f'After adjusting the num_inference_steps by strength parameter: {strength}, the number of pipelinesteps is {num_inference_steps} which is < 1 and not appropriate for this pipeline.')
        latent_timestep = timesteps[:1].repeat(batch_size * num_images_per_prompt)
        is_strength_max = strength == 1.0
        if padding_mask_crop is not None:
            crops_coords = self.mask_processor.get_crop_region(mask_image, width, height, pad=padding_mask_crop)
            resize_mode = 'fill'
        else:
            crops_coords = None
            resize_mode = 'default'
        original_image = image
        init_image = self.image_processor.preprocess(image, height=height, width=width, crops_coords=crops_coords, resize_mode=resize_mode)
        init_image = init_image.to(dtype=torch.float32)
        mask = self.mask_processor.preprocess(mask_image, height=height, width=width, resize_mode=resize_mode, crops_coords=crops_coords)
        if masked_image_latents is not None: masked_image = masked_image_latents
        elif init_image.shape[1] == 4: masked_image = None
        else: masked_image = init_image * (mask < 0.5)
        num_channels_latents = self.vae.config.latent_channels
        num_channels_unet = self.unet.config.in_channels
        return_image_latents = num_channels_unet == 4
        add_noise = True if self.denoising_start is None else False
        latents_outputs = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator,
        latents, image=init_image, timestep=latent_timestep, is_strength_max=is_strength_max, add_noise=add_noise, return_noise=True, return_image_latents=return_image_latents)
        if return_image_latents: latents, noise, image_latents = latents_outputs
        else: latents, noise = latents_outputs
        mask, masked_image_latents = self.prepare_mask_latents(mask, masked_image, batch_size * num_images_per_prompt, height,
        width, prompt_embeds.dtype, device, generator, self.do_classifier_free_guidance)
        if self.do_perturbed_attention_guidance:
            if self.do_classifier_free_guidance:
                mask, _ = mask.chunk(2)
                masked_image_latents, _ = masked_image_latents.chunk(2)
            mask = self._prepare_perturbed_attention_guidance(mask, mask, self.do_classifier_free_guidance)
            masked_image_latents = self._prepare_perturbed_attention_guidance(masked_image_latents, masked_image_latents, self.do_classifier_free_guidance)
        if num_channels_unet == 9:
            num_channels_mask = mask.shape[1]
            num_channels_masked_image = masked_image_latents.shape[1]
            if num_channels_latents + num_channels_mask + num_channels_masked_image != self.unet.config.in_channels: raise ValueError(f'Incorrect configuration settings! The config of `pipeline.unet`: {self.unet.config} expects {self.unet.config.in_channels} but received `num_channels_latents`: {num_channels_latents} + `num_channels_mask`: {num_channels_mask} + `num_channels_masked_image`: {num_channels_masked_image} = {num_channels_latents + num_channels_masked_image + num_channels_mask}. Please verify the config of `pipeline.unet` or your `mask_image` or `image` input.')
        elif num_channels_unet != 4: raise ValueError(f'The unet {self.unet.__class__} should have either 4 or 9 input channels, not {self.unet.config.in_channels}.')
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        height, width = latents.shape[-2:]
        height = height * self.vae_scale_factor
        width = width * self.vae_scale_factor
        original_size = original_size or (height, width)
        target_size = target_size or (height, width)
        if negative_original_size is None: negative_original_size = original_size
        if negative_target_size is None: negative_target_size = target_size
        add_text_embeds = pooled_prompt_embeds
        if self.text_encoder_2 is None: text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1])
        else: text_encoder_projection_dim = self.text_encoder_2.config.projection_dim
        add_time_ids, add_neg_time_ids = self._get_add_time_ids(original_size, crops_coords_top_left, target_size, aesthetic_score, negative_aesthetic_score,
        negative_original_size, negative_crops_coords_top_left, negative_target_size, dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        add_time_ids = add_time_ids.repeat(batch_size * num_images_per_prompt, 1)
        add_neg_time_ids = add_neg_time_ids.repeat(batch_size * num_images_per_prompt, 1)
        if self.do_perturbed_attention_guidance:
            prompt_embeds = self._prepare_perturbed_attention_guidance(prompt_embeds, negative_prompt_embeds, self.do_classifier_free_guidance)
            add_text_embeds = self._prepare_perturbed_attention_guidance(add_text_embeds, negative_pooled_prompt_embeds, self.do_classifier_free_guidance)
            add_time_ids = self._prepare_perturbed_attention_guidance(add_time_ids, add_neg_time_ids, self.do_classifier_free_guidance)
        elif self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
            add_time_ids = torch.cat([add_neg_time_ids, add_time_ids], dim=0)
        prompt_embeds = prompt_embeds.to(device)
        add_text_embeds = add_text_embeds.to(device)
        add_time_ids = add_time_ids.to(device)
        if ip_adapter_image is not None or ip_adapter_image_embeds is not None:
            ip_adapter_image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image, ip_adapter_image_embeds,
            device, batch_size * num_images_per_prompt, self.do_classifier_free_guidance)
            for i, image_embeds in enumerate(ip_adapter_image_embeds):
                negative_image_embeds = None
                if self.do_classifier_free_guidance: negative_image_embeds, image_embeds = image_embeds.chunk(2)
                if self.do_perturbed_attention_guidance: image_embeds = self._prepare_perturbed_attention_guidance(image_embeds, negative_image_embeds, self.do_classifier_free_guidance)
                elif self.do_classifier_free_guidance: image_embeds = torch.cat([negative_image_embeds, image_embeds], dim=0)
                image_embeds = image_embeds.to(device)
                ip_adapter_image_embeds[i] = image_embeds
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        if self.denoising_end is not None and self.denoising_start is not None and denoising_value_valid(self.denoising_end) and denoising_value_valid(self.denoising_start) and (self.denoising_start >= self.denoising_end): raise ValueError(f'`denoising_start`: {self.denoising_start} cannot be larger than or equal to `denoising_end`: ' + f' {self.denoising_end} when using type float.')
        elif self.denoising_end is not None and denoising_value_valid(self.denoising_end):
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - self.denoising_end * self.scheduler.config.num_train_timesteps))
            num_inference_steps = len(list(filter(lambda ts: ts >= discrete_timestep_cutoff, timesteps)))
            timesteps = timesteps[:num_inference_steps]
        timestep_cond = None
        if self.unet.config.time_cond_proj_dim is not None:
            guidance_scale_tensor = torch.tensor(self.guidance_scale - 1).repeat(batch_size * num_images_per_prompt)
            timestep_cond = self.get_guidance_scale_embedding(guidance_scale_tensor, embedding_dim=self.unet.config.time_cond_proj_dim).to(device=device, dtype=latents.dtype)
        if self.do_perturbed_attention_guidance:
            original_attn_proc = self.unet.attn_processors
            self._set_pag_attn_processor(pag_applied_layers=self.pag_applied_layers, do_classifier_free_guidance=self.do_classifier_free_guidance)
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * (prompt_embeds.shape[0] // latents.shape[0]))
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                if num_channels_unet == 9: latent_model_input = torch.cat([latent_model_input, mask, masked_image_latents], dim=1)
                added_cond_kwargs = {'text_embeds': add_text_embeds, 'time_ids': add_time_ids}
                if ip_adapter_image is not None or ip_adapter_image_embeds is not None: added_cond_kwargs['image_embeds'] = ip_adapter_image_embeds
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, timestep_cond=timestep_cond, cross_attention_kwargs=self.cross_attention_kwargs,
                added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
                if self.do_perturbed_attention_guidance: noise_pred, noise_pred_text = self._apply_perturbed_attention_guidance(noise_pred, self.do_classifier_free_guidance, self.guidance_scale, t, True)
                elif self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.do_classifier_free_guidance and self.guidance_rescale > 0.0: noise_pred = rescale_noise_cfg(noise_pred, noise_pred_text, guidance_rescale=self.guidance_rescale)
                latents_dtype = latents.dtype
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
                if num_channels_unet == 4:
                    init_latents_proper = image_latents
                    if self.do_perturbed_attention_guidance: init_mask, *_ = mask.chunk(3) if self.do_classifier_free_guidance else mask.chunk(2)
                    else: init_mask, *_ = mask.chunk(2) if self.do_classifier_free_guidance else mask
                    if i < len(timesteps) - 1:
                        noise_timestep = timesteps[i + 1]
                        init_latents_proper = self.scheduler.add_noise(init_latents_proper, noise, torch.tensor([noise_timestep]))
                    latents = (1 - init_mask) * init_latents_proper + init_mask * latents
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    add_text_embeds = callback_outputs.pop('add_text_embeds', add_text_embeds)
                    negative_pooled_prompt_embeds = callback_outputs.pop('negative_pooled_prompt_embeds', negative_pooled_prompt_embeds)
                    add_time_ids = callback_outputs.pop('add_time_ids', add_time_ids)
                    add_neg_time_ids = callback_outputs.pop('add_neg_time_ids', add_neg_time_ids)
                    mask = callback_outputs.pop('mask', mask)
                    masked_image_latents = callback_outputs.pop('masked_image_latents', masked_image_latents)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
        if not output_type == 'latent':
            needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
            if needs_upcasting:
                self.upcast_vae()
                latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
            elif latents.dtype != self.vae.dtype:
                if torch.backends.mps.is_available(): self.vae = self.vae.to(latents.dtype)
            has_latents_mean = hasattr(self.vae.config, 'latents_mean') and self.vae.config.latents_mean is not None
            has_latents_std = hasattr(self.vae.config, 'latents_std') and self.vae.config.latents_std is not None
            if has_latents_mean and has_latents_std:
                latents_mean = torch.tensor(self.vae.config.latents_mean).view(1, 4, 1, 1).to(latents.device, latents.dtype)
                latents_std = torch.tensor(self.vae.config.latents_std).view(1, 4, 1, 1).to(latents.device, latents.dtype)
                latents = latents * latents_std / self.vae.config.scaling_factor + latents_mean
            else: latents = latents / self.vae.config.scaling_factor
            image = self.vae.decode(latents, return_dict=False)[0]
            if needs_upcasting: self.vae.to(dtype=torch.float16)
        else: return StableDiffusionXLPipelineOutput(images=latents)
        if self.watermark is not None: image = self.watermark.apply_watermark(image)
        image = self.image_processor.postprocess(image, output_type=output_type)
        if padding_mask_crop is not None: image = [self.image_processor.apply_overlay(mask_image, original_image, i, crops_coords) for i in image]
        self.maybe_free_model_hooks()
        if self.do_perturbed_attention_guidance: self.unet.set_attn_processor(original_attn_proc)
        if not return_dict: return (image,)
        return StableDiffusionXLPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
