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
from sapiens_transformers import CLIPTextModelWithProjection, CLIPTokenizer, T5EncoderModel, T5TokenizerFast
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin, SAPILoraLoaderMixin
from ...models.autoencoders import AutoencoderKL
from ...models.controlnets.controlnet_sapi_imagegen import SAPIControlNetModel, SAPIMultiControlNetModel
from ...models.sapiens_transformers import SAPITransformer2DModel
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import USE_PEFT_BACKEND, is_torch_xla_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from ..sapi_imagegen.pipeline_output import SAPIImageGenPipelineOutput
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers.utils import load_image, check_min_version\n        >>> from sapiens_transformers.diffusers.pipelines import SAPIImageGenControlNetInpaintingPipeline\n        >>> from sapiens_transformers.diffusers.models.controlnet_sapi_imagegen import SAPIControlNetModel\n\n        >>> controlnet = SAPIControlNetModel.from_pretrained(\n        ...     "sapiens/SAPI-Controlnet-Inpainting", use_safetensors=True, extra_conditioning_channels=1\n        ... )\n        >>> pipe = SAPIImageGenControlNetInpaintingPipeline.from_pretrained(\n        ...     "sapiens/sapi-imagegen-medium-diffusers",\n        ...     controlnet=controlnet,\n        ...     torch_dtype=torch.float16,\n        ... )\n        >>> pipe.text_encoder.to(torch.float16)\n        >>> pipe.controlnet.to(torch.float16)\n        >>> pipe.to("cuda")\n\n        >>> image = load_image(\n        ...     "https://huggingface.co/alimama-creative/SAPI-Controlnet-Inpainting/resolve/main/images/dog.png"\n        ... )\n        >>> mask = load_image(\n        ...     "https://huggingface.co/alimama-creative/SAPI-Controlnet-Inpainting/resolve/main/images/dog_mask.png"\n        ... )\n        >>> width = 1024\n        >>> height = 1024\n        >>> prompt = "A cat is sitting next to a puppy."\n        >>> generator = torch.Generator(device="cuda").manual_seed(24)\n        >>> res_image = pipe(\n        ...     negative_prompt="deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, mutated hands and fingers, disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, NSFW",\n        ...     prompt=prompt,\n        ...     height=height,\n        ...     width=width,\n        ...     control_image=image,\n        ...     control_mask=mask,\n        ...     num_inference_steps=28,\n        ...     generator=generator,\n        ...     controlnet_conditioning_scale=0.95,\n        ...     guidance_scale=7,\n        ... ).images[0]\n        >>> res_image.save(f"sapi_imagegen.png")\n        ```\n'
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
class SAPIImageGenControlNetInpaintingPipeline(DiffusionPipeline, SAPILoraLoaderMixin, FromSingleFileMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->text_encoder_3->transformer->vae'
    _optional_components = []
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'negative_pooled_prompt_embeds']
    def __init__(self, transformer: SAPITransformer2DModel, scheduler: FlowMatchEulerDiscreteScheduler, vae: AutoencoderKL, text_encoder: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, text_encoder_2: CLIPTextModelWithProjection, tokenizer_2: CLIPTokenizer, text_encoder_3: T5EncoderModel, tokenizer_3: T5TokenizerFast, controlnet: Union[SAPIControlNetModel, List[SAPIControlNetModel], Tuple[SAPIControlNetModel], SAPIMultiControlNetModel]):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, text_encoder_3=text_encoder_3, tokenizer=tokenizer, tokenizer_2=tokenizer_2, tokenizer_3=tokenizer_3, transformer=transformer, scheduler=scheduler, controlnet=controlnet)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_resize=True, do_convert_rgb=True, do_normalize=True)
        self.mask_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_resize=True, do_convert_grayscale=True, do_normalize=False, do_binarize=True)
        self.tokenizer_max_length = self.tokenizer.model_max_length if hasattr(self, 'tokenizer') and self.tokenizer is not None else 77
        self.default_sample_size = self.transformer.config.sample_size if hasattr(self, 'transformer') and self.transformer is not None else 128
        self.patch_size = self.transformer.config.patch_size if hasattr(self, 'transformer') and self.transformer is not None else 2
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_images_per_prompt: int=1, max_sequence_length: int=256, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        if self.text_encoder_3 is None: return torch.zeros((batch_size * num_images_per_prompt, self.tokenizer_max_length, self.transformer.config.joint_attention_dim), device=device, dtype=dtype)
        text_inputs = self.tokenizer_3(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer_3(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer_3.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = self.text_encoder_3(text_input_ids.to(device))[0]
        dtype = self.text_encoder_3.dtype
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return prompt_embeds
    def _get_clip_prompt_embeds(self, prompt: Union[str, List[str]], num_images_per_prompt: int=1, device: Optional[torch.device]=None, clip_skip: Optional[int]=None, clip_model_index: int=0):
        device = device or self._execution_device
        clip_tokenizers = [self.tokenizer, self.tokenizer_2]
        clip_text_encoders = [self.text_encoder, self.text_encoder_2]
        tokenizer = clip_tokenizers[clip_model_index]
        text_encoder = clip_text_encoders[clip_model_index]
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = tokenizer(prompt, padding='max_length', max_length=self.tokenizer_max_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, self.tokenizer_max_length - 1:-1])
        prompt_embeds = text_encoder(text_input_ids.to(device), output_hidden_states=True)
        pooled_prompt_embeds = prompt_embeds[0]
        if clip_skip is None: prompt_embeds = prompt_embeds.hidden_states[-2]
        else: prompt_embeds = prompt_embeds.hidden_states[-(clip_skip + 2)]
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt, 1)
        pooled_prompt_embeds = pooled_prompt_embeds.view(batch_size * num_images_per_prompt, -1)
        return (prompt_embeds, pooled_prompt_embeds)
    def encode_prompt(self, prompt: Union[str, List[str]], prompt_2: Union[str, List[str]], prompt_3: Union[str, List[str]], device: Optional[torch.device]=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True, negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str, List[str]]]=None, negative_prompt_3: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None, pooled_prompt_embeds: Optional[torch.FloatTensor]=None, negative_pooled_prompt_embeds: Optional[torch.FloatTensor]=None, clip_skip: Optional[int]=None, max_sequence_length: int=256, lora_scale: Optional[float]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, SAPILoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            prompt_3 = prompt_3 or prompt
            prompt_3 = [prompt_3] if isinstance(prompt_3, str) else prompt_3
            prompt_embed, pooled_prompt_embed = self._get_clip_prompt_embeds(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=clip_skip, clip_model_index=0)
            prompt_2_embed, pooled_prompt_2_embed = self._get_clip_prompt_embeds(prompt=prompt_2, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=clip_skip, clip_model_index=1)
            clip_prompt_embeds = torch.cat([prompt_embed, prompt_2_embed], dim=-1)
            t5_prompt_embed = self._get_t5_prompt_embeds(prompt=prompt_3, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device)
            clip_prompt_embeds = torch.nn.functional.pad(clip_prompt_embeds, (0, t5_prompt_embed.shape[-1] - clip_prompt_embeds.shape[-1]))
            prompt_embeds = torch.cat([clip_prompt_embeds, t5_prompt_embed], dim=-2)
            pooled_prompt_embeds = torch.cat([pooled_prompt_embed, pooled_prompt_2_embed], dim=-1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt_2 = negative_prompt_2 or negative_prompt
            negative_prompt_3 = negative_prompt_3 or negative_prompt
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            negative_prompt_2 = batch_size * [negative_prompt_2] if isinstance(negative_prompt_2, str) else negative_prompt_2
            negative_prompt_3 = batch_size * [negative_prompt_3] if isinstance(negative_prompt_3, str) else negative_prompt_3
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embed, negative_pooled_prompt_embed = self._get_clip_prompt_embeds(negative_prompt, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=None, clip_model_index=0)
            negative_prompt_2_embed, negative_pooled_prompt_2_embed = self._get_clip_prompt_embeds(negative_prompt_2, device=device, num_images_per_prompt=num_images_per_prompt, clip_skip=None, clip_model_index=1)
            negative_clip_prompt_embeds = torch.cat([negative_prompt_embed, negative_prompt_2_embed], dim=-1)
            t5_negative_prompt_embed = self._get_t5_prompt_embeds(prompt=negative_prompt_3, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device)
            negative_clip_prompt_embeds = torch.nn.functional.pad(negative_clip_prompt_embeds, (0, t5_negative_prompt_embed.shape[-1] - negative_clip_prompt_embeds.shape[-1]))
            negative_prompt_embeds = torch.cat([negative_clip_prompt_embeds, t5_negative_prompt_embed], dim=-2)
            negative_pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embed, negative_pooled_prompt_2_embed], dim=-1)
        if self.text_encoder is not None:
            if isinstance(self, SAPILoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, SAPILoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def check_inputs(self, prompt, prompt_2, prompt_3, height, width, negative_prompt=None, negative_prompt_2=None, negative_prompt_3=None, prompt_embeds=None, negative_prompt_embeds=None, pooled_prompt_embeds=None, negative_pooled_prompt_embeds=None, callback_on_step_end_tensor_inputs=None, max_sequence_length=None):
        if height % (self.vae_scale_factor * self.patch_size) != 0 or width % (self.vae_scale_factor * self.patch_size) != 0: raise ValueError(f'`height` and `width` have to be divisible by {self.vae_scale_factor * self.patch_size} but are {height} and {width}.You can use height {height - height % (self.vae_scale_factor * self.patch_size)} and width {width - width % (self.vae_scale_factor * self.patch_size)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_3 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_3`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        elif prompt_3 is not None and (not isinstance(prompt_3, str) and (not isinstance(prompt_3, list))): raise ValueError(f'`prompt_3` has to be of type `str` or `list` but is {type(prompt_3)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_2 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_2`: {negative_prompt_2} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_3 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_3`: {negative_prompt_3} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        if max_sequence_length is not None and max_sequence_length > 512: raise ValueError(f'`max_sequence_length` cannot be greater than 512 but is {max_sequence_length}')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        if latents is not None: return latents.to(device=device, dtype=dtype)
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        return latents
    def prepare_image_with_mask(self, image, mask, width, height, batch_size, num_images_per_prompt, device, dtype, do_classifier_free_guidance=False, guess_mode=False):
        if isinstance(image, torch.Tensor): pass
        else: image = self.image_processor.preprocess(image, height=height, width=width)
        image_batch_size = image.shape[0]
        if image_batch_size == 1: repeat_by = batch_size
        else: repeat_by = num_images_per_prompt
        image = image.repeat_interleave(repeat_by, dim=0)
        image = image.to(device=device, dtype=dtype)
        if isinstance(mask, torch.Tensor): pass
        else: mask = self.mask_processor.preprocess(mask, height=height, width=width)
        mask = mask.repeat_interleave(repeat_by, dim=0)
        mask = mask.to(device=device, dtype=dtype)
        masked_image = image.clone()
        masked_image[(mask > 0.5).repeat(1, 3, 1, 1)] = -1
        image_latents = self.vae.encode(masked_image).latent_dist.sample()
        image_latents = (image_latents - self.vae.config.shift_factor) * self.vae.config.scaling_factor
        image_latents = image_latents.to(dtype)
        mask = torch.nn.functional.interpolate(mask, size=(height // self.vae_scale_factor, width // self.vae_scale_factor))
        mask = 1 - mask
        control_image = torch.cat([image_latents, mask], dim=1)
        if do_classifier_free_guidance and (not guess_mode): control_image = torch.cat([control_image] * 2)
        return control_image
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def joint_attention_kwargs(self): return self._joint_attention_kwargs
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, prompt_3: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=28, sigmas: Optional[List[float]]=None, guidance_scale: float=7.0, control_guidance_start: Union[float, List[float]]=0.0, control_guidance_end: Union[float, List[float]]=1.0, control_image: PipelineImageInput=None, control_mask: PipelineImageInput=None, controlnet_conditioning_scale: Union[float, List[float]]=1.0, controlnet_pooled_projections: Optional[torch.FloatTensor]=None, negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str, List[str]]]=None, negative_prompt_3: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.FloatTensor]=None, prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None, pooled_prompt_embeds: Optional[torch.FloatTensor]=None, negative_pooled_prompt_embeds: Optional[torch.FloatTensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, joint_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=256):
        """Examples:"""
        height = height or self.default_sample_size * self.vae_scale_factor
        width = width or self.default_sample_size * self.vae_scale_factor
        if not isinstance(control_guidance_start, list) and isinstance(control_guidance_end, list): control_guidance_start = len(control_guidance_end) * [control_guidance_start]
        elif not isinstance(control_guidance_end, list) and isinstance(control_guidance_start, list): control_guidance_end = len(control_guidance_start) * [control_guidance_end]
        elif not isinstance(control_guidance_start, list) and (not isinstance(control_guidance_end, list)):
            mult = len(self.controlnet.nets) if isinstance(self.controlnet, SAPIMultiControlNetModel) else 1
            control_guidance_start, control_guidance_end = (mult * [control_guidance_start], mult * [control_guidance_end])
        self.check_inputs(prompt, prompt_2, prompt_3, height, width, negative_prompt=negative_prompt, negative_prompt_2=negative_prompt_2, negative_prompt_3=negative_prompt_3, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs, max_sequence_length=max_sequence_length)
        self._guidance_scale = guidance_scale
        self._clip_skip = clip_skip
        self._joint_attention_kwargs = joint_attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        dtype = self.transformer.dtype
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, prompt_3=prompt_3, negative_prompt=negative_prompt, negative_prompt_2=negative_prompt_2, negative_prompt_3=negative_prompt_3, do_classifier_free_guidance=self.do_classifier_free_guidance, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds, device=device, clip_skip=self.clip_skip, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            pooled_prompt_embeds = torch.cat([negative_pooled_prompt_embeds, pooled_prompt_embeds], dim=0)
        if isinstance(self.controlnet, SAPIControlNetModel):
            control_image = self.prepare_image_with_mask(image=control_image, mask=control_mask, width=width, height=height, batch_size=batch_size * num_images_per_prompt, num_images_per_prompt=num_images_per_prompt, device=device, dtype=dtype, do_classifier_free_guidance=self.do_classifier_free_guidance, guess_mode=False)
            latent_height, latent_width = control_image.shape[-2:]
            height = latent_height * self.vae_scale_factor
            width = latent_width * self.vae_scale_factor
        elif isinstance(self.controlnet, SAPIMultiControlNetModel): raise NotImplementedError('MultiControlNetModel is not supported for SAPIControlNetInpaintingPipeline.')
        else: assert False
        if controlnet_pooled_projections is None: controlnet_pooled_projections = torch.zeros_like(pooled_prompt_embeds)
        else: controlnet_pooled_projections = controlnet_pooled_projections or pooled_prompt_embeds
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, sigmas=sigmas)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        self._num_timesteps = len(timesteps)
        num_channels_latents = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        controlnet_keep = []
        for i in range(len(timesteps)):
            keeps = [1.0 - float(i / len(timesteps) < s or (i + 1) / len(timesteps) > e) for s, e in zip(control_guidance_start, control_guidance_end)]
            controlnet_keep.append(keeps[0] if isinstance(self.controlnet, SAPIControlNetModel) else keeps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                timestep = t.expand(latent_model_input.shape[0])
                if isinstance(controlnet_keep[i], list): cond_scale = [c * s for c, s in zip(controlnet_conditioning_scale, controlnet_keep[i])]
                else:
                    controlnet_cond_scale = controlnet_conditioning_scale
                    if isinstance(controlnet_cond_scale, list): controlnet_cond_scale = controlnet_cond_scale[0]
                    cond_scale = controlnet_cond_scale * controlnet_keep[i]
                control_block_samples = self.controlnet(hidden_states=latent_model_input, timestep=timestep, encoder_hidden_states=prompt_embeds, pooled_projections=controlnet_pooled_projections, joint_attention_kwargs=self.joint_attention_kwargs, controlnet_cond=control_image, conditioning_scale=cond_scale, return_dict=False)[0]
                noise_pred = self.transformer(hidden_states=latent_model_input, timestep=timestep, encoder_hidden_states=prompt_embeds, pooled_projections=pooled_prompt_embeds, block_controlnet_hidden_states=control_block_samples, joint_attention_kwargs=self.joint_attention_kwargs, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents_dtype = latents.dtype
                latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    negative_pooled_prompt_embeds = callback_outputs.pop('negative_pooled_prompt_embeds', negative_pooled_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
        if output_type == 'latent': image = latents
        else:
            latents = latents / self.vae.config.scaling_factor + self.vae.config.shift_factor
            latents = latents.to(dtype=self.vae.dtype)
            image = self.vae.decode(latents, return_dict=False)[0]
            image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return SAPIImageGenPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
