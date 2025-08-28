'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPVisionModelWithProjection
from ...image_processor import PipelineImageInput
from ...models import AutoencoderKLTemporalDecoder, UNetSpatioTemporalConditionModel
from ...schedulers import EulerDiscreteScheduler
from ...utils import BaseOutput, replace_example_docstring
from ...utils.torch_utils import is_compiled_module, randn_tensor
from ...video_processor import VideoProcessor
from ..pipeline_utils import DiffusionPipeline
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import StableVideoDiffusionPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image, export_to_video\n\n        >>> pipe = StableVideoDiffusionPipeline.from_pretrained(\n        ...     "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"\n        ... )\n        >>> pipe.to("cuda")\n\n        >>> image = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/svd-docstring-example.jpeg"\n        ... )\n        >>> image = image.resize((1024, 576))\n\n        >>> frames = pipe(image, num_frames=25, decode_chunk_size=8).frames[0]\n        >>> export_to_video(frames, "generated.mp4", fps=7)\n        ```\n'
def _append_dims(x, target_dims):
    dims_to_append = target_dims - x.ndim
    if dims_to_append < 0: raise ValueError(f'input has {x.ndim} dims but target_dims is {target_dims}, which is less')
    return x[(...,) + (None,) * dims_to_append]
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None, timesteps: Optional[List[int]]=None,
sigmas: Optional[List[float]]=None, **kwargs):
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
@dataclass
class StableVideoDiffusionPipelineOutput(BaseOutput):
    """Args:"""
    frames: Union[List[List[PIL.Image.Image]], np.ndarray, torch.Tensor]
class StableVideoDiffusionPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'image_encoder->unet->vae'
    _callback_tensor_inputs = ['latents']
    def __init__(self, vae: AutoencoderKLTemporalDecoder, image_encoder: CLIPVisionModelWithProjection, unet: UNetSpatioTemporalConditionModel,
    scheduler: EulerDiscreteScheduler, feature_extractor: CLIPImageProcessor):
        super().__init__()
        self.register_modules(vae=vae, image_encoder=image_encoder, unet=unet, scheduler=scheduler, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.video_processor = VideoProcessor(do_resize=True, vae_scale_factor=self.vae_scale_factor)
    def _encode_image(self, image: PipelineImageInput, device: Union[str, torch.device], num_videos_per_prompt: int, do_classifier_free_guidance: bool) -> torch.Tensor:
        dtype = next(self.image_encoder.parameters()).dtype
        if not isinstance(image, torch.Tensor):
            image = self.video_processor.pil_to_numpy(image)
            image = self.video_processor.numpy_to_pt(image)
            image = image * 2.0 - 1.0
            image = _resize_with_antialiasing(image, (224, 224))
            image = (image + 1.0) / 2.0
        image = self.feature_extractor(images=image, do_normalize=True, do_center_crop=False, do_resize=False, do_rescale=False, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=dtype)
        image_embeddings = self.image_encoder(image).image_embeds
        image_embeddings = image_embeddings.unsqueeze(1)
        bs_embed, seq_len, _ = image_embeddings.shape
        image_embeddings = image_embeddings.repeat(1, num_videos_per_prompt, 1)
        image_embeddings = image_embeddings.view(bs_embed * num_videos_per_prompt, seq_len, -1)
        if do_classifier_free_guidance:
            negative_image_embeddings = torch.zeros_like(image_embeddings)
            image_embeddings = torch.cat([negative_image_embeddings, image_embeddings])
        return image_embeddings
    def _encode_vae_image(self, image: torch.Tensor, device: Union[str, torch.device], num_videos_per_prompt: int, do_classifier_free_guidance: bool):
        image = image.to(device=device)
        image_latents = self.vae.encode(image).latent_dist.mode()
        image_latents = image_latents.repeat(num_videos_per_prompt, 1, 1, 1)
        if do_classifier_free_guidance:
            negative_image_latents = torch.zeros_like(image_latents)
            image_latents = torch.cat([negative_image_latents, image_latents])
        return image_latents
    def _get_add_time_ids(self, fps: int, motion_bucket_id: int, noise_aug_strength: float, dtype: torch.dtype, batch_size: int,
    num_videos_per_prompt: int, do_classifier_free_guidance: bool):
        add_time_ids = [fps, motion_bucket_id, noise_aug_strength]
        passed_add_embed_dim = self.unet.config.addition_time_embed_dim * len(add_time_ids)
        expected_add_embed_dim = self.unet.add_embedding.linear_1.in_features
        if expected_add_embed_dim != passed_add_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. The model has an incorrect config. Please check `unet.config.time_embedding_type` and `text_encoder_2.config.projection_dim`.')
        add_time_ids = torch.tensor([add_time_ids], dtype=dtype)
        add_time_ids = add_time_ids.repeat(batch_size * num_videos_per_prompt, 1)
        if do_classifier_free_guidance: add_time_ids = torch.cat([add_time_ids, add_time_ids])
        return add_time_ids
    def decode_latents(self, latents: torch.Tensor, num_frames: int, decode_chunk_size: int=14):
        latents = latents.flatten(0, 1)
        latents = 1 / self.vae.config.scaling_factor * latents
        forward_vae_fn = self.vae._orig_mod.forward if is_compiled_module(self.vae) else self.vae.forward
        accepts_num_frames = 'num_frames' in set(inspect.signature(forward_vae_fn).parameters.keys())
        frames = []
        for i in range(0, latents.shape[0], decode_chunk_size):
            num_frames_in = latents[i:i + decode_chunk_size].shape[0]
            decode_kwargs = {}
            if accepts_num_frames: decode_kwargs['num_frames'] = num_frames_in
            frame = self.vae.decode(latents[i:i + decode_chunk_size], **decode_kwargs).sample
            frames.append(frame)
        frames = torch.cat(frames, dim=0)
        frames = frames.reshape(-1, num_frames, *frames.shape[1:]).permute(0, 2, 1, 3, 4)
        frames = frames.float()
        return frames
    def check_inputs(self, image, height, width):
        if not isinstance(image, torch.Tensor) and (not isinstance(image, PIL.Image.Image)) and (not isinstance(image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor` or `PIL.Image.Image` or `List[PIL.Image.Image]` but is {type(image)}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
    def prepare_latents(self, batch_size: int, num_frames: int, num_channels_latents: int, height: int, width: int, dtype: torch.dtype, device: Union[str,
    torch.device], generator: torch.Generator, latents: Optional[torch.Tensor]=None):
        shape = (batch_size, num_frames, num_channels_latents // 2, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self):
        if isinstance(self.guidance_scale, (int, float)): return self.guidance_scale > 1
        return self.guidance_scale.max() > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: Union[PIL.Image.Image, List[PIL.Image.Image], torch.Tensor], height: int=576, width: int=1024, num_frames: Optional[int]=None, num_inference_steps: int=25,
    sigmas: Optional[List[float]]=None, min_guidance_scale: float=1.0, max_guidance_scale: float=3.0, fps: int=7, motion_bucket_id: int=127, noise_aug_strength: float=0.02,
    decode_chunk_size: Optional[int]=None, num_videos_per_prompt: Optional[int]=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents'], return_dict: bool=True):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        num_frames = num_frames if num_frames is not None else self.unet.config.num_frames
        decode_chunk_size = decode_chunk_size if decode_chunk_size is not None else num_frames
        self.check_inputs(image, height, width)
        if isinstance(image, PIL.Image.Image): batch_size = 1
        elif isinstance(image, list): batch_size = len(image)
        else: batch_size = image.shape[0]
        device = self._execution_device
        self._guidance_scale = max_guidance_scale
        image_embeddings = self._encode_image(image, device, num_videos_per_prompt, self.do_classifier_free_guidance)
        fps = fps - 1
        image = self.video_processor.preprocess(image, height=height, width=width).to(device)
        noise = randn_tensor(image.shape, generator=generator, device=device, dtype=image.dtype)
        image = image + noise_aug_strength * noise
        needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
        if needs_upcasting: self.vae.to(dtype=torch.float32)
        image_latents = self._encode_vae_image(image, device=device, num_videos_per_prompt=num_videos_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance)
        image_latents = image_latents.to(image_embeddings.dtype)
        if needs_upcasting: self.vae.to(dtype=torch.float16)
        image_latents = image_latents.unsqueeze(1).repeat(1, num_frames, 1, 1, 1)
        added_time_ids = self._get_add_time_ids(fps, motion_bucket_id, noise_aug_strength, image_embeddings.dtype, batch_size, num_videos_per_prompt, self.do_classifier_free_guidance)
        added_time_ids = added_time_ids.to(device)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, None, sigmas)
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_videos_per_prompt, num_frames, num_channels_latents, height, width, image_embeddings.dtype, device, generator, latents)
        guidance_scale = torch.linspace(min_guidance_scale, max_guidance_scale, num_frames).unsqueeze(0)
        guidance_scale = guidance_scale.to(device, latents.dtype)
        guidance_scale = guidance_scale.repeat(batch_size * num_videos_per_prompt, 1)
        guidance_scale = _append_dims(guidance_scale, latents.ndim)
        self._guidance_scale = guidance_scale
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                latent_model_input = torch.cat([latent_model_input, image_latents], dim=2)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=image_embeddings, added_time_ids=added_time_ids, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_cond = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_cond - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents).prev_sample
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latent':
            if needs_upcasting: self.vae.to(dtype=torch.float16)
            frames = self.decode_latents(latents, num_frames, decode_chunk_size)
            frames = self.video_processor.postprocess_video(video=frames, output_type=output_type)
        else: frames = latents
        self.maybe_free_model_hooks()
        if not return_dict: return frames
        return StableVideoDiffusionPipelineOutput(frames=frames)
def _resize_with_antialiasing(input, size, interpolation='bicubic', align_corners=True):
    h, w = input.shape[-2:]
    factors = (h / size[0], w / size[1])
    sigmas = (max((factors[0] - 1.0) / 2.0, 0.001), max((factors[1] - 1.0) / 2.0, 0.001))
    ks = (int(max(2.0 * 2 * sigmas[0], 3)), int(max(2.0 * 2 * sigmas[1], 3)))
    if ks[0] % 2 == 0: ks = (ks[0] + 1, ks[1])
    if ks[1] % 2 == 0: ks = (ks[0], ks[1] + 1)
    input = _gaussian_blur2d(input, ks, sigmas)
    output = torch.nn.functional.interpolate(input, size=size, mode=interpolation, align_corners=align_corners)
    return output
def _compute_padding(kernel_size):
    if len(kernel_size) < 2: raise AssertionError(kernel_size)
    computed = [k - 1 for k in kernel_size]
    out_padding = 2 * len(kernel_size) * [0]
    for i in range(len(kernel_size)):
        computed_tmp = computed[-(i + 1)]
        pad_front = computed_tmp // 2
        pad_rear = computed_tmp - pad_front
        out_padding[2 * i + 0] = pad_front
        out_padding[2 * i + 1] = pad_rear
    return out_padding
def _filter2d(input, kernel):
    b, c, h, w = input.shape
    tmp_kernel = kernel[:, None, ...].to(device=input.device, dtype=input.dtype)
    tmp_kernel = tmp_kernel.expand(-1, c, -1, -1)
    height, width = tmp_kernel.shape[-2:]
    padding_shape: List[int] = _compute_padding([height, width])
    input = torch.nn.functional.pad(input, padding_shape, mode='reflect')
    tmp_kernel = tmp_kernel.reshape(-1, 1, height, width)
    input = input.view(-1, tmp_kernel.size(0), input.size(-2), input.size(-1))
    output = torch.nn.functional.conv2d(input, tmp_kernel, groups=tmp_kernel.size(0), padding=0, stride=1)
    out = output.view(b, c, h, w)
    return out
def _gaussian(window_size: int, sigma):
    if isinstance(sigma, float): sigma = torch.tensor([[sigma]])
    batch_size = sigma.shape[0]
    x = (torch.arange(window_size, device=sigma.device, dtype=sigma.dtype) - window_size // 2).expand(batch_size, -1)
    if window_size % 2 == 0: x = x + 0.5
    gauss = torch.exp(-x.pow(2.0) / (2 * sigma.pow(2.0)))
    return gauss / gauss.sum(-1, keepdim=True)
def _gaussian_blur2d(input, kernel_size, sigma):
    if isinstance(sigma, tuple): sigma = torch.tensor([sigma], dtype=input.dtype)
    else: sigma = sigma.to(dtype=input.dtype)
    ky, kx = (int(kernel_size[0]), int(kernel_size[1]))
    bs = sigma.shape[0]
    kernel_x = _gaussian(kx, sigma[:, 1].view(bs, 1))
    kernel_y = _gaussian(ky, sigma[:, 0].view(bs, 1))
    out_x = _filter2d(input, kernel_x[..., None, :])
    out = _filter2d(out_x, kernel_y[..., None])
    return out
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
