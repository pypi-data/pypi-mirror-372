'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection
from ...utils import USE_PEFT_BACKEND, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...loaders import IPAdapterMixin, StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, ImageProjection, UNet2DConditionModel, UNetMotionModel
from ...models.controlnets.controlnet_sparsectrl import SparseControlNetModel
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...utils.torch_utils import is_compiled_module, randn_tensor
from ...models.unets.unet_motion_model import MotionAdapter
from ...models.lora import adjust_lora_scale_text_encoder
from .pipeline_output import SAPIVideoGenPipelineOutput
from ...schedulers import KarrasDiffusionSchedulers
from ...video_processor import VideoProcessor
from ..free_init_utils import FreeInitMixin
import torch.nn.functional as F
import numpy as np
import inspect
import torch
import PIL
EXAMPLE_DOC_STRING = ''
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
class SAPIVideoGenSparseControlNetPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, IPAdapterMixin, StableDiffusionLoraLoaderMixin, FreeInitMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->image_encoder->unet->vae'
    _optional_components = ['feature_extractor', 'image_encoder', 'motion_adapter']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: Union[UNet2DConditionModel, UNetMotionModel], motion_adapter: MotionAdapter,
    controlnet: SparseControlNetModel, scheduler: KarrasDiffusionSchedulers, feature_extractor: CLIPImageProcessor=None, image_encoder: CLIPVisionModelWithProjection=None):
        super().__init__()
        if isinstance(unet, UNet2DConditionModel): unet = UNetMotionModel.from_unet2d(unet, motion_adapter)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, motion_adapter=motion_adapter, controlnet=controlnet, scheduler=scheduler,
        feature_extractor=feature_extractor, image_encoder=image_encoder)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.video_processor = VideoProcessor(do_resize=False, vae_scale_factor=self.vae_scale_factor)
        self.control_image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True, do_normalize=False)
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
    def decode_latents(self, latents):
        latents = 1 / self.vae.config.scaling_factor * latents
        batch_size, channels, num_frames, height, width = latents.shape
        latents = latents.permute(0, 2, 1, 3, 4).reshape(batch_size * num_frames, channels, height, width)
        image = self.vae.decode(latents).sample
        video = image[None, :].reshape((batch_size, num_frames, -1) + image.shape[2:]).permute(0, 2, 1, 3, 4)
        video = video.float()
        return video
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, ip_adapter_image=None, ip_adapter_image_embeds=None,
    callback_on_step_end_tensor_inputs=None, image=None, controlnet_conditioning_scale: float=1.0):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if ip_adapter_image is not None and ip_adapter_image_embeds is not None: raise ValueError('Provide either `ip_adapter_image` or `ip_adapter_image_embeds`. Cannot leave both `ip_adapter_image` and `ip_adapter_image_embeds` defined.')
        if ip_adapter_image_embeds is not None:
            if not isinstance(ip_adapter_image_embeds, list): raise ValueError(f'`ip_adapter_image_embeds` has to be of type `list` but is {type(ip_adapter_image_embeds)}')
            elif ip_adapter_image_embeds[0].ndim not in [3, 4]: raise ValueError(f'`ip_adapter_image_embeds` has to be a list of 3D or 4D tensors but is {ip_adapter_image_embeds[0].ndim}D')
        is_compiled = hasattr(F, 'scaled_dot_product_attention') and isinstance(self.controlnet, torch._dynamo.eval_frame.OptimizedModule)
        if isinstance(self.controlnet, SparseControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, SparseControlNetModel)):
            if isinstance(image, list):
                for image_ in image: self.check_image(image_, prompt, prompt_embeds)
            else: self.check_image(image, prompt, prompt_embeds)
        else: assert False
        if isinstance(self.controlnet, SparseControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, SparseControlNetModel)):
            if not isinstance(controlnet_conditioning_scale, float): raise TypeError('For single controlnet: `controlnet_conditioning_scale` must be type `float`.')
        else: assert False
    def check_image(self, image, prompt, prompt_embeds):
        image_is_pil = isinstance(image, PIL.Image.Image)
        image_is_tensor = isinstance(image, torch.Tensor)
        image_is_np = isinstance(image, np.ndarray)
        image_is_pil_list = isinstance(image, list) and isinstance(image[0], PIL.Image.Image)
        image_is_tensor_list = isinstance(image, list) and isinstance(image[0], torch.Tensor)
        image_is_np_list = isinstance(image, list) and isinstance(image[0], np.ndarray)
        if not image_is_pil and (not image_is_tensor) and (not image_is_np) and (not image_is_pil_list) and (not image_is_tensor_list) and (not image_is_np_list): raise TypeError(f'image must be passed and be one of PIL image, numpy array, torch tensor, list of PIL images, list of numpy arrays or list of torch tensors, but is {type(image)}')
        if image_is_pil: image_batch_size = 1
        else: image_batch_size = len(image)
        if prompt is not None and isinstance(prompt, str): prompt_batch_size = 1
        elif prompt is not None and isinstance(prompt, list): prompt_batch_size = len(prompt)
        elif prompt_embeds is not None: prompt_batch_size = prompt_embeds.shape[0]
        if image_batch_size != 1 and image_batch_size != prompt_batch_size: raise ValueError(f'If image batch size is not 1, image batch size must be same as prompt batch size. image batch size: {image_batch_size}, prompt batch size: {prompt_batch_size}')
    def prepare_latents(self, batch_size, num_channels_latents, num_frames, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, num_frames, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def prepare_image(self, image, width, height, device, dtype):
        image = self.control_image_processor.preprocess(image, height=height, width=width)
        controlnet_images = image.unsqueeze(0).to(device, dtype)
        batch_size, num_frames, channels, height, width = controlnet_images.shape
        assert controlnet_images.min() >= 0 and controlnet_images.max() <= 1
        if self.controlnet.use_simplified_condition_embedding:
            controlnet_images = controlnet_images.reshape(batch_size * num_frames, channels, height, width)
            controlnet_images = 2 * controlnet_images - 1
            conditioning_frames = retrieve_latents(self.vae.encode(controlnet_images)) * self.vae.config.scaling_factor
            conditioning_frames = conditioning_frames.reshape(batch_size, num_frames, 4, height // self.vae_scale_factor, width // self.vae_scale_factor)
        else: conditioning_frames = controlnet_images
        conditioning_frames = conditioning_frames.permute(0, 2, 1, 3, 4)
        return conditioning_frames
    def prepare_sparse_control_conditioning(self, conditioning_frames: torch.Tensor, num_frames: int, controlnet_frame_indices: int, device: torch.device,
    dtype: torch.dtype) -> Tuple[torch.Tensor, torch.Tensor]:
        assert conditioning_frames.shape[2] >= len(controlnet_frame_indices)
        batch_size, channels, _, height, width = conditioning_frames.shape
        controlnet_cond = torch.zeros((batch_size, channels, num_frames, height, width), dtype=dtype, device=device)
        controlnet_cond_mask = torch.zeros((batch_size, 1, num_frames, height, width), dtype=dtype, device=device)
        controlnet_cond[:, :, controlnet_frame_indices] = conditioning_frames[:, :, :len(controlnet_frame_indices)]
        controlnet_cond_mask[:, :, controlnet_frame_indices] = 1
        return (controlnet_cond, controlnet_cond_mask)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_frames: int=16, num_inference_steps: int=50,
    guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None, num_videos_per_prompt: int=1, eta: float=0.0, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[List[torch.Tensor]]=None, conditioning_frames: Optional[List[PipelineImageInput]]=None,
    output_type: str='pil', return_dict: bool=True, cross_attention_kwargs: Optional[Dict[str, Any]]=None, controlnet_conditioning_scale: Union[float, List[float]]=1.0,
    controlnet_frame_indices: List[int]=[0], guess_mode: bool=False, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        controlnet = self.controlnet._orig_mod if is_compiled_module(self.controlnet) else self.controlnet
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        num_videos_per_prompt = 1
        self.check_inputs(prompt=prompt, height=height, width=width, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        ip_adapter_image=ip_adapter_image, ip_adapter_image_embeds=ip_adapter_image_embeds, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs,
        image=conditioning_frames, controlnet_conditioning_scale=controlnet_conditioning_scale)
        self._guidance_scale = guidance_scale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        global_pool_conditions = controlnet.config.global_pool_conditions if isinstance(controlnet, SparseControlNetModel) else controlnet.nets[0].config.global_pool_conditions
        guess_mode = guess_mode or global_pool_conditions
        text_encoder_lora_scale = self.cross_attention_kwargs.get('scale', None) if self.cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_videos_per_prompt, self.do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=self.clip_skip)
        if self.do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        prompt_embeds = prompt_embeds.repeat_interleave(repeats=num_frames, dim=0)
        if ip_adapter_image is not None or ip_adapter_image_embeds is not None: image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image,
        ip_adapter_image_embeds, device, batch_size * num_videos_per_prompt, self.do_classifier_free_guidance)
        conditioning_frames = self.prepare_image(conditioning_frames, width, height, device, controlnet.dtype)
        controlnet_cond, controlnet_cond_mask = self.prepare_sparse_control_conditioning(conditioning_frames, num_frames, controlnet_frame_indices, device, controlnet.dtype)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_videos_per_prompt, num_channels_latents, num_frames, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        added_cond_kwargs = {'image_embeds': image_embeds} if ip_adapter_image is not None or ip_adapter_image_embeds is not None else None
        num_free_init_iters = self._free_init_num_iters if self.free_init_enabled else 1
        for free_init_iter in range(num_free_init_iters):
            if self.free_init_enabled: latents, timesteps = self._apply_free_init(latents, free_init_iter, num_inference_steps, device, latents.dtype, generator)
            self._num_timesteps = len(timesteps)
            num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
            with self.progress_bar(total=self._num_timesteps) as progress_bar:
                for i, t in enumerate(timesteps):
                    latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                    latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                    if guess_mode and self.do_classifier_free_guidance:
                        control_model_input = latents
                        control_model_input = self.scheduler.scale_model_input(control_model_input, t)
                        controlnet_prompt_embeds = prompt_embeds.chunk(2)[1]
                    else:
                        control_model_input = latent_model_input
                        controlnet_prompt_embeds = prompt_embeds
                    down_block_res_samples, mid_block_res_sample = self.controlnet(control_model_input, t, encoder_hidden_states=controlnet_prompt_embeds, controlnet_cond=controlnet_cond,
                    conditioning_mask=controlnet_cond_mask, conditioning_scale=controlnet_conditioning_scale, guess_mode=guess_mode, return_dict=False)
                    noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs, added_cond_kwargs=added_cond_kwargs,
                    down_block_additional_residuals=down_block_res_samples, mid_block_additional_residual=mid_block_res_sample).sample
                    if self.do_classifier_free_guidance:
                        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                        noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                    latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                    if callback_on_step_end is not None:
                        callback_kwargs = {}
                        for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                        callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                        latents = callback_outputs.pop('latents', latents)
                        prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                        negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if output_type == 'latent': video = latents
        else:
            video_tensor = self.decode_latents(latents)
            video = self.video_processor.postprocess_video(video=video_tensor, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return SAPIVideoGenPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
