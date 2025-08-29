'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np
import torch
from sapiens_transformers import T5EncoderModel, T5TokenizerFast
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...loaders import Mochi1LoraLoaderMixin
from ...models.autoencoders import AutoencoderKL
from ...models.sapiens_transformers import MochiTransformer3DModel
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import is_torch_xla_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ...video_processor import VideoProcessor
from ..pipeline_utils import DiffusionPipeline
from .pipeline_output import MochiPipelineOutput
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import MochiPipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_video\n\n        >>> pipe = MochiPipeline.from_pretrained("genmo/mochi-1-preview", torch_dtype=torch.bfloat16)\n        >>> pipe.enable_model_cpu_offload()\n        >>> pipe.enable_vae_tiling()\n        >>> prompt = "Close-up of a chameleon\'s eye, with its scaly skin changing color. Ultra high resolution 4k."\n        >>> frames = pipe(prompt, num_inference_steps=28, guidance_scale=3.5).frames[0]\n        >>> export_to_video(frames, "mochi.mp4")\n        ```\n'
def calculate_shift(image_seq_len, base_seq_len: int=256, max_seq_len: int=4096, base_shift: float=0.5, max_shift: float=1.16):
    m = (max_shift - base_shift) / (max_seq_len - base_seq_len)
    b = base_shift - m * base_seq_len
    mu = image_seq_len * m + b
    return mu
def linear_quadratic_schedule(num_steps, threshold_noise, linear_steps=None):
    if linear_steps is None: linear_steps = num_steps // 2
    linear_sigma_schedule = [i * threshold_noise / linear_steps for i in range(linear_steps)]
    threshold_noise_step_diff = linear_steps - threshold_noise * num_steps
    quadratic_steps = num_steps - linear_steps
    quadratic_coef = threshold_noise_step_diff / (linear_steps * quadratic_steps ** 2)
    linear_coef = threshold_noise / linear_steps - 2 * threshold_noise_step_diff / quadratic_steps ** 2
    const = quadratic_coef * linear_steps ** 2
    quadratic_sigma_schedule = [quadratic_coef * i ** 2 + linear_coef * i + const for i in range(linear_steps, num_steps)]
    sigma_schedule = linear_sigma_schedule + quadratic_sigma_schedule
    sigma_schedule = [1.0 - x for x in sigma_schedule]
    return sigma_schedule
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
class MochiPipeline(DiffusionPipeline, Mochi1LoraLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _optional_components = []
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, scheduler: FlowMatchEulerDiscreteScheduler, vae: AutoencoderKL, text_encoder: T5EncoderModel, tokenizer: T5TokenizerFast, transformer: MochiTransformer3DModel, force_zeros_for_empty_prompt: bool=False):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, transformer=transformer, scheduler=scheduler)
        self.vae_spatial_scale_factor = 8
        self.vae_temporal_scale_factor = 6
        self.patch_size = 2
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_spatial_scale_factor)
        self.tokenizer_max_length = self.tokenizer.model_max_length if hasattr(self, 'tokenizer') and self.tokenizer is not None else 256
        self.default_height = 480
        self.default_width = 848
        self.register_to_config(force_zeros_for_empty_prompt=force_zeros_for_empty_prompt)
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_videos_per_prompt: int=1, max_sequence_length: int=256, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        prompt_attention_mask = text_inputs.attention_mask
        prompt_attention_mask = prompt_attention_mask.bool().to(device)
        if self.config.force_zeros_for_empty_prompt and (prompt == '' or prompt[-1] == ''):
            text_input_ids = torch.zeros_like(text_input_ids, device=device)
            prompt_attention_mask = torch.zeros_like(prompt_attention_mask, dtype=torch.bool, device=device)
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_sequence_length - 1:-1])
        prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=prompt_attention_mask)[0]
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_videos_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_videos_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.view(batch_size, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(num_videos_per_prompt, 1)
        return (prompt_embeds, prompt_attention_mask)
    def encode_prompt(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, do_classifier_free_guidance: bool=True, num_videos_per_prompt: int=1,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, max_sequence_length: int=256, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        """Args:"""
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None: prompt_embeds, prompt_attention_mask = self._get_t5_prompt_embeds(prompt=prompt, num_videos_per_prompt=num_videos_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embeds, negative_prompt_attention_mask = self._get_t5_prompt_embeds(prompt=negative_prompt, num_videos_per_prompt=num_videos_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def check_inputs(self, prompt, height, width, callback_on_step_end_tensor_inputs=None, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt_embeds is not None and prompt_attention_mask is None: raise ValueError('Must provide `prompt_attention_mask` when specifying `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_prompt_attention_mask is None: raise ValueError('Must provide `negative_prompt_attention_mask` when specifying `negative_prompt_embeds`.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if prompt_attention_mask.shape != negative_prompt_attention_mask.shape: raise ValueError(f'`prompt_attention_mask` and `negative_prompt_attention_mask` must have the same shape when passed directly, but got: `prompt_attention_mask` {prompt_attention_mask.shape} != `negative_prompt_attention_mask` {negative_prompt_attention_mask.shape}.')
    def enable_vae_slicing(self): self.vae.enable_slicing()
    def disable_vae_slicing(self): self.vae.disable_slicing()
    def enable_vae_tiling(self): self.vae.enable_tiling()
    def disable_vae_tiling(self): self.vae.disable_tiling()
    def prepare_latents(self, batch_size, num_channels_latents, height, width, num_frames, dtype, device, generator, latents=None):
        height = height // self.vae_spatial_scale_factor
        width = width // self.vae_spatial_scale_factor
        num_frames = (num_frames - 1) // self.vae_temporal_scale_factor + 1
        shape = (batch_size, num_channels_latents, num_frames, height, width)
        if latents is not None: return latents.to(device=device, dtype=dtype)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=torch.float32)
        latents = latents.to(dtype)
        return latents
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
    def __call__(self, prompt: Union[str, List[str]]=None, negative_prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_frames: int=19,
    num_inference_steps: int=64, timesteps: List[int]=None, guidance_scale: float=4.5, num_videos_per_prompt: Optional[int]=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, attention_kwargs: Optional[Dict[str, Any]]=None,
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=256):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.default_height
        width = width or self.default_width
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
        do_classifier_free_guidance=self.do_classifier_free_guidance, num_videos_per_prompt=num_videos_per_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask, max_sequence_length=max_sequence_length, device=device)
        num_channels_latents = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_videos_per_prompt, num_channels_latents, height, width, num_frames, prompt_embeds.dtype, device, generator, latents)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            prompt_attention_mask = torch.cat([negative_prompt_attention_mask, prompt_attention_mask], dim=0)
        threshold_noise = 0.025
        sigmas = linear_quadratic_schedule(num_inference_steps, threshold_noise)
        sigmas = np.array(sigmas)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                timestep = t.expand(latent_model_input.shape[0]).to(latents.dtype)
                noise_pred = self.transformer(hidden_states=latent_model_input, encoder_hidden_states=prompt_embeds, timestep=timestep,
                encoder_attention_mask=prompt_attention_mask, attention_kwargs=attention_kwargs, return_dict=False)[0]
                noise_pred = noise_pred.to(torch.float32)
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents_dtype = latents.dtype
                latents = self.scheduler.step(noise_pred, t, latents.to(torch.float32), return_dict=False)[0]
                latents = latents.to(latents_dtype)
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
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
            has_latents_mean = hasattr(self.vae.config, 'latents_mean') and self.vae.config.latents_mean is not None
            has_latents_std = hasattr(self.vae.config, 'latents_std') and self.vae.config.latents_std is not None
            if has_latents_mean and has_latents_std:
                latents_mean = torch.tensor(self.vae.config.latents_mean).view(1, 12, 1, 1, 1).to(latents.device, latents.dtype)
                latents_std = torch.tensor(self.vae.config.latents_std).view(1, 12, 1, 1, 1).to(latents.device, latents.dtype)
                latents = latents * latents_std / self.vae.config.scaling_factor + latents_mean
            else: latents = latents / self.vae.config.scaling_factor
            video = self.vae.decode(latents, return_dict=False)[0]
            video = self.video_processor.postprocess_video(video, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return MochiPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
