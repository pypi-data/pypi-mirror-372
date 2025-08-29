'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...loaders import FromSingleFileMixin, SapiensVideoGenVideoLoraLoaderMixin
from ...models.sapiens_transformers import SapiensVideoGenVideoTransformer3DModel
from ...utils import is_torch_xla_available, replace_example_docstring
from ...models.autoencoders import AutoencoderKLSapiensVideoGenVideo
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from typing import Any, Callable, Dict, List, Optional, Union
from .pipeline_output import SapiensVideoGenPipelineOutput
from ...schedulers import FlowMatchEulerDiscreteScheduler
from sapiens_transformers import T5EncoderModel, T5TokenizerFast
from ...image_processor import PipelineImageInput
from ..pipeline_utils import DiffusionPipeline
from ...utils.torch_utils import randn_tensor
from ...video_processor import VideoProcessor
import numpy as np
import inspect
import torch
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = ''
def calculate_shift(image_seq_len, base_seq_len: int=256, max_seq_len: int=4096, base_shift: float=0.5, max_shift: float=1.16):
    m = (max_shift - base_shift) / (max_seq_len - base_seq_len)
    b = base_shift - m * base_seq_len
    mu = image_seq_len * m + b
    return mu
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
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
class SapiensVideoGenImageToVideoPipeline(DiffusionPipeline, FromSingleFileMixin, SapiensVideoGenVideoLoraLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _optional_components = []
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, scheduler: FlowMatchEulerDiscreteScheduler, vae: AutoencoderKLSapiensVideoGenVideo, text_encoder: T5EncoderModel, tokenizer: T5TokenizerFast, transformer: SapiensVideoGenVideoTransformer3DModel):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, transformer=transformer, scheduler=scheduler)
        self.vae_spatial_compression_ratio = self.vae.spatial_compression_ratio if hasattr(self, 'vae') else 32
        self.vae_temporal_compression_ratio = self.vae.temporal_compression_ratio if hasattr(self, 'vae') else 8
        self.transformer_spatial_patch_size = self.transformer.config.patch_size if hasattr(self, 'transformer') else 1
        self.transformer_temporal_patch_size = self.transformer.config.patch_size_t if hasattr(self, 'transformer') else 1
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_spatial_compression_ratio)
        self.tokenizer_max_length = self.tokenizer.model_max_length if hasattr(self, 'tokenizer') and self.tokenizer is not None else 128
        self.default_height = 512
        self.default_width = 704
        self.default_frames = 121
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_videos_per_prompt: int=1, max_sequence_length: int=128, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        prompt_attention_mask = text_inputs.attention_mask
        prompt_attention_mask = prompt_attention_mask.bool().to(device)
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_sequence_length - 1:-1])
        prompt_embeds = self.text_encoder(text_input_ids.to(device))[0]
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_videos_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_videos_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.view(batch_size, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(num_videos_per_prompt, 1)
        return (prompt_embeds, prompt_attention_mask)
    def encode_prompt(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, do_classifier_free_guidance: bool=True, num_videos_per_prompt: int=1,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, max_sequence_length: int=128, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        """Args:"""
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None: prompt_embeds, prompt_attention_mask = self._get_t5_prompt_embeds(prompt=prompt, num_videos_per_prompt=num_videos_per_prompt,
        max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embeds, negative_prompt_attention_mask = self._get_t5_prompt_embeds(prompt=negative_prompt, num_videos_per_prompt=num_videos_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def check_inputs(self, prompt, height, width, callback_on_step_end_tensor_inputs=None, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 32 != 0 or width % 32 != 0: raise ValueError(f'`height` and `width` have to be divisible by 32 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt_embeds is not None and prompt_attention_mask is None: raise ValueError('Must provide `prompt_attention_mask` when specifying `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_prompt_attention_mask is None: raise ValueError('Must provide `negative_prompt_attention_mask` when specifying `negative_prompt_embeds`.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if prompt_attention_mask.shape != negative_prompt_attention_mask.shape: raise ValueError(f'`prompt_attention_mask` and `negative_prompt_attention_mask` must have the same shape when passed directly, but got: `prompt_attention_mask` {prompt_attention_mask.shape} != `negative_prompt_attention_mask` {negative_prompt_attention_mask.shape}.')
    @staticmethod
    def _pack_latents(latents: torch.Tensor, patch_size: int=1, patch_size_t: int=1) -> torch.Tensor:
        batch_size, num_channels, num_frames, height, width = latents.shape
        post_patch_num_frames = num_frames // patch_size_t
        post_patch_height = height // patch_size
        post_patch_width = width // patch_size
        latents = latents.reshape(batch_size, -1, post_patch_num_frames, patch_size_t, post_patch_height, patch_size, post_patch_width, patch_size)
        latents = latents.permute(0, 2, 4, 6, 1, 3, 5, 7).flatten(4, 7).flatten(1, 3)
        return latents
    @staticmethod
    def _unpack_latents(latents: torch.Tensor, num_frames: int, height: int, width: int, patch_size: int=1, patch_size_t: int=1) -> torch.Tensor:
        batch_size = latents.size(0)
        latents = latents.reshape(batch_size, num_frames, height, width, -1, patch_size_t, patch_size, patch_size)
        latents = latents.permute(0, 4, 1, 5, 2, 6, 3, 7).flatten(6, 7).flatten(4, 5).flatten(2, 3)
        return latents
    @staticmethod
    def _normalize_latents(latents: torch.Tensor, latents_mean: torch.Tensor, latents_std: torch.Tensor, scaling_factor: float=1.0) -> torch.Tensor:
        latents_mean = latents_mean.view(1, -1, 1, 1, 1).to(latents.device, latents.dtype)
        latents_std = latents_std.view(1, -1, 1, 1, 1).to(latents.device, latents.dtype)
        latents = (latents - latents_mean) * scaling_factor / latents_std
        return latents
    @staticmethod
    def _denormalize_latents(latents: torch.Tensor, latents_mean: torch.Tensor, latents_std: torch.Tensor, scaling_factor: float=1.0) -> torch.Tensor:
        latents_mean = latents_mean.view(1, -1, 1, 1, 1).to(latents.device, latents.dtype)
        latents_std = latents_std.view(1, -1, 1, 1, 1).to(latents.device, latents.dtype)
        latents = latents * latents_std / scaling_factor + latents_mean
        return latents
    def prepare_latents(self, image: Optional[torch.Tensor]=None, batch_size: int=1, num_channels_latents: int=128, height: int=512, width: int=704, num_frames: int=161,
    dtype: Optional[torch.dtype]=None, device: Optional[torch.device]=None, generator: Optional[torch.Generator]=None, latents: Optional[torch.Tensor]=None) -> torch.Tensor:
        height = height // self.vae_spatial_compression_ratio
        width = width // self.vae_spatial_compression_ratio
        num_frames = (num_frames - 1) // self.vae_temporal_compression_ratio + 1 if latents is None else latents.size(2)
        shape = (batch_size, num_channels_latents, num_frames, height, width)
        mask_shape = (batch_size, 1, num_frames, height, width)
        if latents is not None:
            conditioning_mask = latents.new_zeros(shape)
            conditioning_mask[:, :, 0] = 1.0
            conditioning_mask = self._pack_latents(conditioning_mask, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
            return (latents.to(device=device, dtype=dtype), conditioning_mask)
        if isinstance(generator, list):
            if len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
            init_latents = [retrieve_latents(self.vae.encode(image[i].unsqueeze(0).unsqueeze(2)), generator[i]) for i in range(batch_size)]
        else: init_latents = [retrieve_latents(self.vae.encode(img.unsqueeze(0).unsqueeze(2)), generator) for img in image]
        init_latents = torch.cat(init_latents, dim=0).to(dtype)
        init_latents = self._normalize_latents(init_latents, self.vae.latents_mean, self.vae.latents_std)
        init_latents = init_latents.repeat(1, 1, num_frames, 1, 1)
        conditioning_mask = torch.zeros(mask_shape, device=device, dtype=dtype)
        conditioning_mask[:, :, 0] = 1.0
        noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        latents = init_latents * conditioning_mask + noise * (1 - conditioning_mask)
        conditioning_mask = self._pack_latents(conditioning_mask, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size).squeeze(-1)
        latents = self._pack_latents(latents, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
        return (latents, conditioning_mask)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1.0
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def attention_kwargs(self): return self._attention_kwargs
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: PipelineImageInput=None, prompt: Union[str, List[str]]=None, negative_prompt: Optional[Union[str, List[str]]]=None, height: int=512,
    width: int=704, num_frames: int=161, frame_rate: int=25, num_inference_steps: int=50, timesteps: List[int]=None, guidance_scale: float=3, num_videos_per_prompt: Optional[int]=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None,
    decode_timestep: Union[float, List[float]]=0.0, decode_noise_scale: Optional[Union[float, List[float]]]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    attention_kwargs: Optional[Dict[str, Any]]=None, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=128):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        self.check_inputs(prompt=prompt, height=height, width=width, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs, prompt_embeds=prompt_embeds,
        negative_prompt_embeds=negative_prompt_embeds, prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask)
        self._guidance_scale = guidance_scale
        self._attention_kwargs = attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask = self.encode_prompt(prompt=prompt, negative_prompt=negative_prompt,
        do_classifier_free_guidance=self.do_classifier_free_guidance, num_videos_per_prompt=num_videos_per_prompt, prompt_embeds=prompt_embeds,
        negative_prompt_embeds=negative_prompt_embeds, prompt_attention_mask=prompt_attention_mask,
        negative_prompt_attention_mask=negative_prompt_attention_mask, max_sequence_length=max_sequence_length, device=device)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            prompt_attention_mask = torch.cat([negative_prompt_attention_mask, prompt_attention_mask], dim=0)
        if latents is None:
            image = self.video_processor.preprocess(image, height=height, width=width)
            image = image.to(device=device, dtype=prompt_embeds.dtype)
        num_channels_latents = self.transformer.config.in_channels
        latents, conditioning_mask = self.prepare_latents(image, batch_size * num_videos_per_prompt, num_channels_latents, height,
        width, num_frames, torch.float32, device, generator, latents)
        if self.do_classifier_free_guidance: conditioning_mask = torch.cat([conditioning_mask, conditioning_mask])
        latent_num_frames = (num_frames - 1) // self.vae_temporal_compression_ratio + 1
        latent_height = height // self.vae_spatial_compression_ratio
        latent_width = width // self.vae_spatial_compression_ratio
        video_sequence_length = latent_num_frames * latent_height * latent_width
        sigmas = np.linspace(1.0, 1 / num_inference_steps, num_inference_steps)
        mu = calculate_shift(video_sequence_length, self.scheduler.config.base_image_seq_len, self.scheduler.config.max_image_seq_len, self.scheduler.config.base_shift, self.scheduler.config.max_shift)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas=sigmas, mu=mu)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        self._num_timesteps = len(timesteps)
        latent_frame_rate = frame_rate / self.vae_temporal_compression_ratio
        rope_interpolation_scale = (1 / latent_frame_rate, self.vae_spatial_compression_ratio, self.vae_spatial_compression_ratio)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = latent_model_input.to(prompt_embeds.dtype)
                timestep = t.expand(latent_model_input.shape[0])
                timestep = timestep.unsqueeze(-1) * (1 - conditioning_mask)
                noise_pred = self.transformer(hidden_states=latent_model_input, encoder_hidden_states=prompt_embeds, timestep=timestep, encoder_attention_mask=prompt_attention_mask,
                num_frames=latent_num_frames, height=latent_height, width=latent_width, rope_interpolation_scale=rope_interpolation_scale, attention_kwargs=attention_kwargs, return_dict=False)[0]
                noise_pred = noise_pred.float()
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                    timestep, _ = timestep.chunk(2)
                noise_pred = self._unpack_latents(noise_pred, latent_num_frames, latent_height, latent_width, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
                latents = self._unpack_latents(latents, latent_num_frames, latent_height, latent_width, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
                noise_pred = noise_pred[:, :, 1:]
                noise_latents = latents[:, :, 1:]
                pred_latents = self.scheduler.step(noise_pred, t, noise_latents, return_dict=False)[0]
                latents = torch.cat([latents[:, :, :1], pred_latents], dim=2)
                latents = self._pack_latents(latents, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
        if output_type == 'latent': video = latents
        else:
            latents = self._unpack_latents(latents, latent_num_frames, latent_height, latent_width, self.transformer_spatial_patch_size, self.transformer_temporal_patch_size)
            latents = self._denormalize_latents(latents, self.vae.latents_mean, self.vae.latents_std, self.vae.config.scaling_factor)
            latents = latents.to(prompt_embeds.dtype)
            if not self.vae.config.timestep_conditioning: timestep = None
            else:
                noise = torch.randn(latents.shape, generator=generator, device=device, dtype=latents.dtype)
                if not isinstance(decode_timestep, list): decode_timestep = [decode_timestep] * batch_size
                if decode_noise_scale is None: decode_noise_scale = decode_timestep
                elif not isinstance(decode_noise_scale, list): decode_noise_scale = [decode_noise_scale] * batch_size
                timestep = torch.tensor(decode_timestep, device=device, dtype=latents.dtype)
                decode_noise_scale = torch.tensor(decode_noise_scale, device=device, dtype=latents.dtype)[:, None, None, None, None]
                latents = (1 - decode_noise_scale) * latents + decode_noise_scale * noise
            video = self.vae.decode(latents, timestep, return_dict=False)[0]
            video = self.video_processor.postprocess_video(video, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return SapiensVideoGenPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
