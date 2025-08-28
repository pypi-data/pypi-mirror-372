'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import PIL
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import PipelineImageInput
from ...loaders import CogVideoXLoraLoaderMixin
from ...models import AutoencoderKLCogVideoX, CogVideoXTransformer3DModel
from ...models.embeddings import get_3d_rotary_pos_embed
from ...pipelines.pipeline_utils import DiffusionPipeline
from ...schedulers import CogVideoXDDIMScheduler, CogVideoXDPMScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ...video_processor import VideoProcessor
from .pipeline_output import CogVideoXPipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import CogVideoXImageToVideoPipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_video, load_image\n\n        >>> pipe = CogVideoXImageToVideoPipeline.from_pretrained("THUDM/CogVideoX-5b-I2V", torch_dtype=torch.bfloat16)\n        >>> pipe.to("cuda")\n\n        >>> prompt = "An astronaut hatching from an egg, on the surface of the moon, the darkness and depth of space realised in the background. High quality, ultrarealistic detail and breath-taking movie-like camera shot."\n        >>> image = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/astronaut.jpg"\n        ... )\n        >>> video = pipe(image, prompt, use_dynamic_cfg=True)\n        >>> export_to_video(video.frames[0], "output.mp4", fps=8)\n        ```\n'
def get_resize_crop_region_for_grid(src, tgt_width, tgt_height):
    tw = tgt_width
    th = tgt_height
    h, w = src
    r = h / w
    if r > th / tw:
        resize_height = th
        resize_width = int(round(th / h * w))
    else:
        resize_width = tw
        resize_height = int(round(tw / w * h))
    crop_top = int(round((th - resize_height) / 2.0))
    crop_left = int(round((tw - resize_width) / 2.0))
    return ((crop_top, crop_left), (crop_top + resize_height, crop_left + resize_width))
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
class CogVideoXImageToVideoPipeline(DiffusionPipeline, CogVideoXLoraLoaderMixin):
    """Args:"""
    _optional_components = []
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, vae: AutoencoderKLCogVideoX, transformer: CogVideoXTransformer3DModel, scheduler: Union[CogVideoXDDIMScheduler, CogVideoXDPMScheduler]):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor_spatial = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.vae_scale_factor_temporal = self.vae.config.temporal_compression_ratio if hasattr(self, 'vae') and self.vae is not None else 4
        self.vae_scaling_factor_image = self.vae.config.scaling_factor if hasattr(self, 'vae') and self.vae is not None else 0.7
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_scale_factor_spatial)
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_videos_per_prompt: int=1, max_sequence_length: int=226, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_sequence_length - 1:-1])
        prompt_embeds = self.text_encoder(text_input_ids.to(device))[0]
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_videos_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_videos_per_prompt, seq_len, -1)
        return prompt_embeds
    def encode_prompt(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, do_classifier_free_guidance: bool=True, num_videos_per_prompt: int=1,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, max_sequence_length: int=226, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        """Args:"""
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None: prompt_embeds = self._get_t5_prompt_embeds(prompt=prompt, num_videos_per_prompt=num_videos_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embeds = self._get_t5_prompt_embeds(prompt=negative_prompt, num_videos_per_prompt=num_videos_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        return (prompt_embeds, negative_prompt_embeds)
    def prepare_latents(self, image: torch.Tensor, batch_size: int=1, num_channels_latents: int=16, num_frames: int=13, height: int=60, width: int=90, dtype: Optional[torch.dtype]=None,
    device: Optional[torch.device]=None, generator: Optional[torch.Generator]=None, latents: Optional[torch.Tensor]=None):
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        num_frames = (num_frames - 1) // self.vae_scale_factor_temporal + 1
        shape = (batch_size, num_frames, num_channels_latents, height // self.vae_scale_factor_spatial, width // self.vae_scale_factor_spatial)
        if self.transformer.config.patch_size_t is not None: shape = shape[:1] + (shape[1] + shape[1] % self.transformer.config.patch_size_t,) + shape[2:]
        image = image.unsqueeze(2)
        if isinstance(generator, list): image_latents = [retrieve_latents(self.vae.encode(image[i].unsqueeze(0)), generator[i]) for i in range(batch_size)]
        else: image_latents = [retrieve_latents(self.vae.encode(img.unsqueeze(0)), generator) for img in image]
        image_latents = torch.cat(image_latents, dim=0).to(dtype).permute(0, 2, 1, 3, 4)
        if not self.vae.config.invert_scale_latents: image_latents = self.vae_scaling_factor_image * image_latents
        else: image_latents = 1 / self.vae_scaling_factor_image * image_latents
        padding_shape = (batch_size, num_frames - 1, num_channels_latents, height // self.vae_scale_factor_spatial, width // self.vae_scale_factor_spatial)
        latent_padding = torch.zeros(padding_shape, device=device, dtype=dtype)
        image_latents = torch.cat([image_latents, latent_padding], dim=1)
        if self.transformer.config.patch_size_t is not None:
            first_frame = image_latents[:, :image_latents.size(1) % self.transformer.config.patch_size_t, ...]
            image_latents = torch.cat([first_frame, image_latents], dim=1)
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return (latents, image_latents)
    def decode_latents(self, latents: torch.Tensor) -> torch.Tensor:
        latents = latents.permute(0, 2, 1, 3, 4)
        latents = 1 / self.vae_scaling_factor_image * latents
        frames = self.vae.decode(latents).sample
        return frames
    def get_timesteps(self, num_inference_steps, timesteps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        timesteps = timesteps[t_start * self.scheduler.order:]
        return (timesteps, num_inference_steps - t_start)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, image, prompt, height, width, negative_prompt, callback_on_step_end_tensor_inputs, latents=None, prompt_embeds=None, negative_prompt_embeds=None):
        if not isinstance(image, torch.Tensor) and (not isinstance(image, PIL.Image.Image)) and (not isinstance(image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor` or `PIL.Image.Image` or `List[PIL.Image.Image]` but is {type(image)}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def fuse_qkv_projections(self) -> None:
        self.fusing_transformer = True
        self.transformer.fuse_qkv_projections()
    def unfuse_qkv_projections(self) -> None:
        self.transformer.unfuse_qkv_projections()
        self.fusing_transformer = False
    def _prepare_rotary_positional_embeddings(self, height: int, width: int, num_frames: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        grid_height = height // (self.vae_scale_factor_spatial * self.transformer.config.patch_size)
        grid_width = width // (self.vae_scale_factor_spatial * self.transformer.config.patch_size)
        p = self.transformer.config.patch_size
        p_t = self.transformer.config.patch_size_t
        base_size_width = self.transformer.config.sample_width // p
        base_size_height = self.transformer.config.sample_height // p
        if p_t is None:
            grid_crops_coords = get_resize_crop_region_for_grid((grid_height, grid_width), base_size_width, base_size_height)
            freqs_cos, freqs_sin = get_3d_rotary_pos_embed(embed_dim=self.transformer.config.attention_head_dim, crops_coords=grid_crops_coords,
            grid_size=(grid_height, grid_width), temporal_size=num_frames, device=device)
        else:
            base_num_frames = (num_frames + p_t - 1) // p_t
            freqs_cos, freqs_sin = get_3d_rotary_pos_embed(embed_dim=self.transformer.config.attention_head_dim, crops_coords=None, grid_size=(grid_height, grid_width), temporal_size=base_num_frames,
            grid_type='slice', max_size=(base_size_height, base_size_width), device=device)
        return (freqs_cos, freqs_sin)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def attention_kwargs(self): return self._attention_kwargs
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: PipelineImageInput, prompt: Optional[Union[str, List[str]]]=None, negative_prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None,
    num_frames: int=49, num_inference_steps: int=50, timesteps: Optional[List[int]]=None, guidance_scale: float=6, use_dynamic_cfg: bool=False, num_videos_per_prompt: int=1, eta: float=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.FloatTensor]=None, prompt_embeds: Optional[torch.FloatTensor]=None,
    negative_prompt_embeds: Optional[torch.FloatTensor]=None, output_type: str='pil', return_dict: bool=True, attention_kwargs: Optional[Dict[str, Any]]=None,
    callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'],
    max_sequence_length: int=226) -> Union[CogVideoXPipelineOutput, Tuple]:
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.transformer.config.sample_height * self.vae_scale_factor_spatial
        width = width or self.transformer.config.sample_width * self.vae_scale_factor_spatial
        num_frames = num_frames or self.transformer.config.sample_frames
        num_videos_per_prompt = 1
        self.check_inputs(image=image, prompt=prompt, height=height, width=width, negative_prompt=negative_prompt, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs,
        latents=latents, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        self._guidance_scale = guidance_scale
        self._attention_kwargs = attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt=prompt, negative_prompt=negative_prompt, do_classifier_free_guidance=do_classifier_free_guidance,
        num_videos_per_prompt=num_videos_per_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, max_sequence_length=max_sequence_length, device=device)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps)
        self._num_timesteps = len(timesteps)
        latent_frames = (num_frames - 1) // self.vae_scale_factor_temporal + 1
        patch_size_t = self.transformer.config.patch_size_t
        additional_frames = 0
        if patch_size_t is not None and latent_frames % patch_size_t != 0:
            additional_frames = patch_size_t - latent_frames % patch_size_t
            num_frames += additional_frames * self.vae_scale_factor_temporal
        image = self.video_processor.preprocess(image, height=height, width=width).to(device, dtype=prompt_embeds.dtype)
        latent_channels = self.transformer.config.in_channels // 2
        latents, image_latents = self.prepare_latents(image, batch_size * num_videos_per_prompt, latent_channels, num_frames, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        image_rotary_emb = self._prepare_rotary_positional_embeddings(height, width, latents.size(1), device) if self.transformer.config.use_rotary_positional_embeddings else None
        ofs_emb = None if self.transformer.config.ofs_embed_dim is None else latents.new_full((1,), fill_value=2.0)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            old_pred_original_sample = None
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                latent_image_input = torch.cat([image_latents] * 2) if do_classifier_free_guidance else image_latents
                latent_model_input = torch.cat([latent_model_input, latent_image_input], dim=2)
                timestep = t.expand(latent_model_input.shape[0])
                noise_pred = self.transformer(hidden_states=latent_model_input, encoder_hidden_states=prompt_embeds, timestep=timestep, ofs=ofs_emb,
                image_rotary_emb=image_rotary_emb, attention_kwargs=attention_kwargs, return_dict=False)[0]
                noise_pred = noise_pred.float()
                if use_dynamic_cfg: self._guidance_scale = 1 + guidance_scale * ((1 - math.cos(math.pi * ((num_inference_steps - t.item()) / num_inference_steps) ** 5.0)) / 2)
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                if not isinstance(self.scheduler, CogVideoXDPMScheduler): latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                else: latents, old_pred_original_sample = self.scheduler.step(noise_pred, old_pred_original_sample, t, timesteps[i - 1] if i > 0 else None, latents, **extra_step_kwargs, return_dict=False)
                latents = latents.to(prompt_embeds.dtype)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latent':
            latents = latents[:, additional_frames:]
            video = self.decode_latents(latents)
            video = self.video_processor.postprocess_video(video=video, output_type=output_type)
        else: video = latents
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return CogVideoXPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
