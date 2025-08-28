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
from packaging import version
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ...configuration_utils import FrozenDict
from ...image_processor import VaeImageProcessor
from ...loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, UNet2DConditionModel
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import DDIMInverseScheduler, KarrasDiffusionSchedulers
from ...utils import PIL_INTERPOLATION, USE_PEFT_BACKEND, BaseOutput, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion import StableDiffusionPipelineOutput
from ..stable_diffusion.safety_checker import StableDiffusionSafetyChecker
@dataclass
class DiffEditInversionPipelineOutput(BaseOutput):
    """Args:"""
    latents: torch.Tensor
    images: Union[List[PIL.Image.Image], np.ndarray]
EXAMPLE_DOC_STRING = '\n\n        ```py\n        >>> import PIL\n        >>> import requests\n        >>> import torch\n        >>> from io import BytesIO\n\n        >>> from sapiens_transformers.diffusers import StableDiffusionDiffEditPipeline\n\n\n        >>> def download_image(url):\n        ...     response = requests.get(url)\n        ...     return PIL.Image.open(BytesIO(response.content)).convert("RGB")\n\n\n        >>> img_url = "https://github.com/Xiang-cd/DiffEdit-stable-diffusion/raw/main/assets/origin.png"\n\n        >>> init_image = download_image(img_url).resize((768, 768))\n\n        >>> pipeline = StableDiffusionDiffEditPipeline.from_pretrained(\n        ...     "stabilityai/stable-diffusion-2-1", torch_dtype=torch.float16\n        ... )\n\n        >>> pipeline.scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.inverse_scheduler = DDIMInverseScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.enable_model_cpu_offload()\n\n        >>> mask_prompt = "A bowl of fruits"\n        >>> prompt = "A bowl of pears"\n\n        >>> mask_image = pipeline.generate_mask(image=init_image, source_prompt=prompt, target_prompt=mask_prompt)\n        >>> image_latents = pipeline.invert(image=init_image, prompt=mask_prompt).latents\n        >>> image = pipeline(prompt=prompt, mask_image=mask_image, image_latents=image_latents).images[0]\n        ```\n'
EXAMPLE_INVERT_DOC_STRING = '\n        ```py\n        >>> import PIL\n        >>> import requests\n        >>> import torch\n        >>> from io import BytesIO\n\n        >>> from sapiens_transformers.diffusers import StableDiffusionDiffEditPipeline\n\n\n        >>> def download_image(url):\n        ...     response = requests.get(url)\n        ...     return PIL.Image.open(BytesIO(response.content)).convert("RGB")\n\n\n        >>> img_url = "https://github.com/Xiang-cd/DiffEdit-stable-diffusion/raw/main/assets/origin.png"\n\n        >>> init_image = download_image(img_url).resize((768, 768))\n\n        >>> pipeline = StableDiffusionDiffEditPipeline.from_pretrained(\n        ...     "stabilityai/stable-diffusion-2-1", torch_dtype=torch.float16\n        ... )\n\n        >>> pipeline.scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.inverse_scheduler = DDIMInverseScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.enable_model_cpu_offload()\n\n        >>> prompt = "A bowl of fruits"\n\n        >>> inverted_latents = pipeline.invert(image=init_image, prompt=prompt).latents\n        ```\n'
def auto_corr_loss(hidden_states, generator=None):
    reg_loss = 0.0
    for i in range(hidden_states.shape[0]):
        for j in range(hidden_states.shape[1]):
            noise = hidden_states[i:i + 1, j:j + 1, :, :]
            while True:
                roll_amount = torch.randint(noise.shape[2] // 2, (1,), generator=generator).item()
                reg_loss += (noise * torch.roll(noise, shifts=roll_amount, dims=2)).mean() ** 2
                reg_loss += (noise * torch.roll(noise, shifts=roll_amount, dims=3)).mean() ** 2
                if noise.shape[2] <= 8: break
                noise = torch.nn.functional.avg_pool2d(noise, kernel_size=2)
    return reg_loss
def kl_divergence(hidden_states): return hidden_states.var() + hidden_states.mean() ** 2 - 1 - torch.log(hidden_states.var() + 1e-07)
def preprocess(image):
    deprecation_message = 'The preprocess method is deprecated and will be removed in diffusers 1.0.0. Please use VaeImageProcessor.preprocess(...) instead'
    deprecate('preprocess', '1.0.0', deprecation_message, standard_warn=False)
    if isinstance(image, torch.Tensor): return image
    elif isinstance(image, PIL.Image.Image): image = [image]
    if isinstance(image[0], PIL.Image.Image):
        w, h = image[0].size
        w, h = (x - x % 8 for x in (w, h))
        image = [np.array(i.resize((w, h), resample=PIL_INTERPOLATION['lanczos']))[None, :] for i in image]
        image = np.concatenate(image, axis=0)
        image = np.array(image).astype(np.float32) / 255.0
        image = image.transpose(0, 3, 1, 2)
        image = 2.0 * image - 1.0
        image = torch.from_numpy(image)
    elif isinstance(image[0], torch.Tensor): image = torch.cat(image, dim=0)
    return image
def preprocess_mask(mask, batch_size: int=1):
    if not isinstance(mask, torch.Tensor):
        if isinstance(mask, (PIL.Image.Image, np.ndarray)): mask = [mask]
        if isinstance(mask, list):
            if isinstance(mask[0], PIL.Image.Image): mask = [np.array(m.convert('L')).astype(np.float32) / 255.0 for m in mask]
            if isinstance(mask[0], np.ndarray):
                mask = np.stack(mask, axis=0) if mask[0].ndim < 3 else np.concatenate(mask, axis=0)
                mask = torch.from_numpy(mask)
            elif isinstance(mask[0], torch.Tensor): mask = torch.stack(mask, dim=0) if mask[0].ndim < 3 else torch.cat(mask, dim=0)
    if mask.ndim == 2: mask = mask.unsqueeze(0).unsqueeze(0)
    if mask.ndim == 3:
        if mask.shape[0] == 1: mask = mask.unsqueeze(0)
        else: mask = mask.unsqueeze(1)
    if batch_size > 1:
        if mask.shape[0] == 1: mask = torch.cat([mask] * batch_size)
        elif mask.shape[0] > 1 and mask.shape[0] != batch_size: raise ValueError(f'`mask_image` with batch size {mask.shape[0]} cannot be broadcasted to batch size {batch_size} inferred by prompt inputs')
    if mask.shape[1] != 1: raise ValueError(f'`mask_image` must have 1 channel, but has {mask.shape[1]} channels')
    if mask.min() < 0 or mask.max() > 1: raise ValueError('`mask_image` should be in [0, 1] range')
    mask[mask < 0.5] = 0
    mask[mask >= 0.5] = 1
    return mask
class StableDiffusionDiffEditPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, StableDiffusionLoraLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor', 'inverse_scheduler']
    _exclude_from_cpu_offload = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers,
    safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, inverse_scheduler: DDIMInverseScheduler, requires_safety_checker: bool=True):
        super().__init__()
        if hasattr(scheduler.config, 'steps_offset') and scheduler.config.steps_offset != 1:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} is outdated. `steps_offset` should be set to 1 instead of {scheduler.config.steps_offset}. Please make sure to update the config accordingly as leaving `steps_offset` might led to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('steps_offset!=1', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['steps_offset'] = 1
            scheduler._internal_dict = FrozenDict(new_config)
        if hasattr(scheduler.config, 'skip_prk_steps') and scheduler.config.skip_prk_steps is False:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} has not set the configuration `skip_prk_steps`. `skip_prk_steps` should be set to True in the configuration file. Please make sure to update the config accordingly as not setting `skip_prk_steps` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('skip_prk_steps not set', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['skip_prk_steps'] = True
            scheduler._internal_dict = FrozenDict(new_config)
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        is_unet_version_less_0_9_0 = hasattr(unet.config, '_diffusers_version') and version.parse(version.parse(unet.config._diffusers_version).base_version) < version.parse('0.9.0.dev0')
        is_unet_sample_size_less_64 = hasattr(unet.config, 'sample_size') and unet.config.sample_size < 64
        if is_unet_version_less_0_9_0 and is_unet_sample_size_less_64:
            deprecation_message = "The configuration file of the unet has set the default `sample_size` to smaller than 64 which seems highly unlikely .If you're checkpoint is a fine-tuned version of any of the following: \n- CompVis/stable-diffusion-v1-4 \n- CompVis/stable-diffusion-v1-3 \n- CompVis/stable-diffusion-v1-2 \n- CompVis/stable-diffusion-v1-1 \n- runwayml/stable-diffusion-v1-5 \n- runwayml/stable-diffusion-inpainting \n you should change 'sample_size' to 64 in the configuration file. Please make sure to update the config accordingly as leaving `sample_size=32` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `unet/config.json` file"
            deprecate('sample_size<64', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(unet.config)
            new_config['sample_size'] = 64
            unet._internal_dict = FrozenDict(new_config)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker,
        feature_extractor=feature_extractor, inverse_scheduler=inverse_scheduler)
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
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def check_inputs(self, prompt, strength, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        if strength is None or (strength is not None and (strength < 0 or strength > 1)): raise ValueError(f'The value of `strength` should in [0.0, 1.0] but is, but is {strength} of type {type(strength)}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def check_source_inputs(self, source_prompt=None, source_negative_prompt=None, source_prompt_embeds=None, source_negative_prompt_embeds=None):
        if source_prompt is not None and source_prompt_embeds is not None: raise ValueError(f'Cannot forward both `source_prompt`: {source_prompt} and `source_prompt_embeds`: {source_prompt_embeds}.  Please make sure to only forward one of the two.')
        elif source_prompt is None and source_prompt_embeds is None: raise ValueError('Provide either `source_image` or `source_prompt_embeds`. Cannot leave all both of the arguments undefined.')
        elif source_prompt is not None and (not isinstance(source_prompt, str) and (not isinstance(source_prompt, list))): raise ValueError(f'`source_prompt` has to be of type `str` or `list` but is {type(source_prompt)}')
        if source_negative_prompt is not None and source_negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `source_negative_prompt`: {source_negative_prompt} and `source_negative_prompt_embeds`: {source_negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if source_prompt_embeds is not None and source_negative_prompt_embeds is not None:
            if source_prompt_embeds.shape != source_negative_prompt_embeds.shape: raise ValueError(f'`source_prompt_embeds` and `source_negative_prompt_embeds` must have the same shape when passed directly, but got: `source_prompt_embeds` {source_prompt_embeds.shape} != `source_negative_prompt_embeds` {source_negative_prompt_embeds.shape}.')
    def get_timesteps(self, num_inference_steps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        timesteps = self.scheduler.timesteps[t_start * self.scheduler.order:]
        return (timesteps, num_inference_steps - t_start)
    def get_inverse_timesteps(self, num_inference_steps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        if t_start == 0: return (self.inverse_scheduler.timesteps, num_inference_steps)
        timesteps = self.inverse_scheduler.timesteps[:-t_start]
        return (timesteps, num_inference_steps - t_start)
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def prepare_image_latents(self, image, batch_size, dtype, device, generator=None):
        if not isinstance(image, (torch.Tensor, PIL.Image.Image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image` or list but is {type(image)}')
        image = image.to(device=device, dtype=dtype)
        if image.shape[1] == 4: latents = image
        else:
            if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
            if isinstance(generator, list):
                latents = [self.vae.encode(image[i:i + 1]).latent_dist.sample(generator[i]) for i in range(batch_size)]
                latents = torch.cat(latents, dim=0)
            else: latents = self.vae.encode(image).latent_dist.sample(generator)
            latents = self.vae.config.scaling_factor * latents
        if batch_size != latents.shape[0]:
            if batch_size % latents.shape[0] == 0:
                deprecation_message = f'You have passed {batch_size} text prompts (`prompt`), but only {latents.shape[0]} initial images (`image`). Initial images are now duplicating to match the number of text prompts. Note that this behavior is deprecated and will be removed in a version 1.0.0. Please make sure to update your script to pass as many initial images as text prompts to suppress this warning.'
                deprecate('len(prompt) != len(image)', '1.0.0', deprecation_message, standard_warn=False)
                additional_latents_per_image = batch_size // latents.shape[0]
                latents = torch.cat([latents] * additional_latents_per_image, dim=0)
            else: raise ValueError(f'Cannot duplicate `image` of batch size {latents.shape[0]} to {batch_size} text prompts.')
        else: latents = torch.cat([latents], dim=0)
        return latents
    def get_epsilon(self, model_output: torch.Tensor, sample: torch.Tensor, timestep: int):
        pred_type = self.inverse_scheduler.config.prediction_type
        alpha_prod_t = self.inverse_scheduler.alphas_cumprod[timestep]
        beta_prod_t = 1 - alpha_prod_t
        if pred_type == 'epsilon': return model_output
        elif pred_type == 'sample': return (sample - alpha_prod_t ** 0.5 * model_output) / beta_prod_t ** 0.5
        elif pred_type == 'v_prediction': return alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
        else: raise ValueError(f'prediction_type given as {pred_type} must be one of `epsilon`, `sample`, or `v_prediction`')
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def generate_mask(self, image: Union[torch.Tensor, PIL.Image.Image]=None, target_prompt: Optional[Union[str, List[str]]]=None, target_negative_prompt: Optional[Union[str,
    List[str]]]=None, target_prompt_embeds: Optional[torch.Tensor]=None, target_negative_prompt_embeds: Optional[torch.Tensor]=None, source_prompt: Optional[Union[str,
    List[str]]]=None, source_negative_prompt: Optional[Union[str, List[str]]]=None, source_prompt_embeds: Optional[torch.Tensor]=None,
    source_negative_prompt_embeds: Optional[torch.Tensor]=None, num_maps_per_mask: Optional[int]=10, mask_encode_strength: Optional[float]=0.5,
    mask_thresholding_ratio: Optional[float]=3.0, num_inference_steps: int=50, guidance_scale: float=7.5, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, output_type: Optional[str]='np', cross_attention_kwargs: Optional[Dict[str, Any]]=None):
        """Examples:"""
        self.check_inputs(target_prompt, mask_encode_strength, 1, target_negative_prompt, target_prompt_embeds, target_negative_prompt_embeds)
        self.check_source_inputs(source_prompt, source_negative_prompt, source_prompt_embeds, source_negative_prompt_embeds)
        if num_maps_per_mask is None or (num_maps_per_mask is not None and (not isinstance(num_maps_per_mask, int) or num_maps_per_mask <= 0)): raise ValueError(f'`num_maps_per_mask` has to be a positive integer but is {num_maps_per_mask} of type {type(num_maps_per_mask)}.')
        if mask_thresholding_ratio is None or mask_thresholding_ratio <= 0: raise ValueError(f'`mask_thresholding_ratio` has to be positive but is {mask_thresholding_ratio} of type {type(mask_thresholding_ratio)}.')
        if target_prompt is not None and isinstance(target_prompt, str): batch_size = 1
        elif target_prompt is not None and isinstance(target_prompt, list): batch_size = len(target_prompt)
        else: batch_size = target_prompt_embeds.shape[0]
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        target_negative_prompt_embeds, target_prompt_embeds = self.encode_prompt(target_prompt, device, num_maps_per_mask, do_classifier_free_guidance, target_negative_prompt,
        prompt_embeds=target_prompt_embeds, negative_prompt_embeds=target_negative_prompt_embeds)
        if do_classifier_free_guidance: target_prompt_embeds = torch.cat([target_negative_prompt_embeds, target_prompt_embeds])
        source_negative_prompt_embeds, source_prompt_embeds = self.encode_prompt(source_prompt, device, num_maps_per_mask, do_classifier_free_guidance, source_negative_prompt,
        prompt_embeds=source_prompt_embeds, negative_prompt_embeds=source_negative_prompt_embeds)
        if do_classifier_free_guidance: source_prompt_embeds = torch.cat([source_negative_prompt_embeds, source_prompt_embeds])
        image = self.image_processor.preprocess(image).repeat_interleave(num_maps_per_mask, dim=0)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps, _ = self.get_timesteps(num_inference_steps, mask_encode_strength, device)
        encode_timestep = timesteps[0]
        image_latents = self.prepare_image_latents(image, batch_size * num_maps_per_mask, self.vae.dtype, device, generator)
        noise = randn_tensor(image_latents.shape, generator=generator, device=device, dtype=self.vae.dtype)
        image_latents = self.scheduler.add_noise(image_latents, noise, encode_timestep)
        latent_model_input = torch.cat([image_latents] * (4 if do_classifier_free_guidance else 2))
        latent_model_input = self.scheduler.scale_model_input(latent_model_input, encode_timestep)
        prompt_embeds = torch.cat([source_prompt_embeds, target_prompt_embeds])
        noise_pred = self.unet(latent_model_input, encode_timestep, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
        if do_classifier_free_guidance:
            noise_pred_neg_src, noise_pred_source, noise_pred_uncond, noise_pred_target = noise_pred.chunk(4)
            noise_pred_source = noise_pred_neg_src + guidance_scale * (noise_pred_source - noise_pred_neg_src)
            noise_pred_target = noise_pred_uncond + guidance_scale * (noise_pred_target - noise_pred_uncond)
        else: noise_pred_source, noise_pred_target = noise_pred.chunk(2)
        mask_guidance_map = torch.abs(noise_pred_target - noise_pred_source).reshape(batch_size, num_maps_per_mask, *noise_pred_target.shape[-3:]).mean([1, 2])
        clamp_magnitude = mask_guidance_map.mean() * mask_thresholding_ratio
        semantic_mask_image = mask_guidance_map.clamp(0, clamp_magnitude) / clamp_magnitude
        semantic_mask_image = torch.where(semantic_mask_image <= 0.5, 0, 1)
        mask_image = semantic_mask_image.cpu().numpy()
        if output_type == 'pil': mask_image = self.image_processor.numpy_to_pil(mask_image)
        self.maybe_free_model_hooks()
        return mask_image
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_INVERT_DOC_STRING)
    def invert(self, prompt: Optional[Union[str, List[str]]]=None, image: Union[torch.Tensor, PIL.Image.Image]=None, num_inference_steps: int=50, inpaint_strength: float=0.8,
    guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, decode_latents: bool=False, output_type: Optional[str]='pil',
    return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: Optional[int]=1, cross_attention_kwargs: Optional[Dict[str,
    Any]]=None, lambda_auto_corr: float=20.0, lambda_kl: float=20.0, num_reg_steps: int=0, num_auto_corr_rolls: int=5):
        """Examples:"""
        self.check_inputs(prompt, inpaint_strength, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if image is None: raise ValueError('`image` input cannot be undefined.')
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        image = self.image_processor.preprocess(image)
        num_images_per_prompt = 1
        latents = self.prepare_image_latents(image, batch_size * num_images_per_prompt, self.vae.dtype, device, generator)
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.inverse_scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps, num_inference_steps = self.get_inverse_timesteps(num_inference_steps, inpaint_strength, device)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.inverse_scheduler.order
        inverted_latents = []
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.inverse_scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if num_reg_steps > 0:
                    with torch.enable_grad():
                        for _ in range(num_reg_steps):
                            if lambda_auto_corr > 0:
                                for _ in range(num_auto_corr_rolls):
                                    var = torch.autograd.Variable(noise_pred.detach().clone(), requires_grad=True)
                                    var_epsilon = self.get_epsilon(var, latent_model_input.detach(), t)
                                    l_ac = auto_corr_loss(var_epsilon, generator=generator)
                                    l_ac.backward()
                                    grad = var.grad.detach() / num_auto_corr_rolls
                                    noise_pred = noise_pred - lambda_auto_corr * grad
                            if lambda_kl > 0:
                                var = torch.autograd.Variable(noise_pred.detach().clone(), requires_grad=True)
                                var_epsilon = self.get_epsilon(var, latent_model_input.detach(), t)
                                l_kld = kl_divergence(var_epsilon)
                                l_kld.backward()
                                grad = var.grad.detach()
                                noise_pred = noise_pred - lambda_kl * grad
                            noise_pred = noise_pred.detach()
                latents = self.inverse_scheduler.step(noise_pred, t, latents).prev_sample
                inverted_latents.append(latents.detach().clone())
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.inverse_scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        assert len(inverted_latents) == len(timesteps)
        latents = torch.stack(list(reversed(inverted_latents)), 1)
        image = None
        if decode_latents: image = self.decode_latents(latents.flatten(0, 1))
        if decode_latents and output_type == 'pil': image = self.image_processor.numpy_to_pil(image)
        self.maybe_free_model_hooks()
        if not return_dict: return (latents, image)
        return DiffEditInversionPipelineOutput(latents=latents, images=image)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, mask_image: Union[torch.Tensor, PIL.Image.Image]=None, image_latents: Union[torch.Tensor,
    PIL.Image.Image]=None, inpaint_strength: Optional[float]=0.8, num_inference_steps: int=50, guidance_scale: float=7.5, negative_prompt: Optional[Union[str,
    List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: int=None):
        """Examples:"""
        self.check_inputs(prompt, inpaint_strength, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if mask_image is None: raise ValueError('`mask_image` input cannot be undefined. Use `generate_mask()` to compute `mask_image` from text prompts.')
        if image_latents is None: raise ValueError('`image_latents` input cannot be undefined. Use `invert()` to compute `image_latents` from input images.')
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        text_encoder_lora_scale = cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        mask_image = preprocess_mask(mask_image, batch_size)
        latent_height, latent_width = mask_image.shape[-2:]
        mask_image = torch.cat([mask_image] * num_images_per_prompt)
        mask_image = mask_image.to(device=device, dtype=prompt_embeds.dtype)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, inpaint_strength, device)
        if isinstance(image_latents, list) and any((isinstance(l, torch.Tensor) and l.ndim == 5 for l in image_latents)): image_latents = torch.cat(image_latents).detach()
        elif isinstance(image_latents, torch.Tensor) and image_latents.ndim == 5: image_latents = image_latents.detach()
        else: image_latents = self.image_processor.preprocess(image_latents).detach()
        latent_shape = (self.vae.config.latent_channels, latent_height, latent_width)
        if image_latents.shape[-3:] != latent_shape: raise ValueError(f'Each latent image in `image_latents` must have shape {latent_shape}, but has shape {image_latents.shape[-3:]}')
        if image_latents.ndim == 4: image_latents = image_latents.reshape(batch_size, len(timesteps), *latent_shape)
        if image_latents.shape[:2] != (batch_size, len(timesteps)): raise ValueError(f'`image_latents` must have batch size {batch_size} with latent images from {len(timesteps)} timesteps, but has batch size {image_latents.shape[0]} with latent images from {image_latents.shape[1]} timesteps.')
        image_latents = image_latents.transpose(0, 1).repeat_interleave(num_images_per_prompt, dim=1)
        image_latents = image_latents.to(device=device, dtype=prompt_embeds.dtype)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        latents = image_latents[0].clone()
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                latents = latents * mask_image + image_latents[i] * (1 - mask_image)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, device, prompt_embeds.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        self.maybe_free_model_hooks()
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
