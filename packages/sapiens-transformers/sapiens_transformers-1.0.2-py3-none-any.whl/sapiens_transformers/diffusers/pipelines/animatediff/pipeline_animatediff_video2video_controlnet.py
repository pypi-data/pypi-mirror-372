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
import torch.nn.functional as F
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection
from ...image_processor import PipelineImageInput
from ...loaders import IPAdapterMixin, StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, ControlNetModel, ImageProjection, MultiControlNetModel, UNet2DConditionModel, UNetMotionModel
from ...models.lora import adjust_lora_scale_text_encoder
from ...models.unets.unet_motion_model import MotionAdapter
from ...schedulers import DDIMScheduler, DPMSolverMultistepScheduler, EulerAncestralDiscreteScheduler, EulerDiscreteScheduler, LMSDiscreteScheduler, PNDMScheduler
from ...utils import USE_PEFT_BACKEND, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import is_compiled_module, randn_tensor
from ...video_processor import VideoProcessor
from ..free_init_utils import FreeInitMixin
from ..free_noise_utils import AnimateDiffFreeNoiseMixin
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from .pipeline_output import AnimateDiffPipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from PIL import Image\n        >>> from tqdm.auto import tqdm\n\n        >>> from sapiens_transformers.diffusers import AnimateDiffVideoToVideoControlNetPipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_gif, load_video\n        >>> from sapiens_transformers.diffusers import AutoencoderKL, ControlNetModel, MotionAdapter, LCMScheduler\n\n        >>> controlnet = ControlNetModel.from_pretrained(\n        ...     "lllyasviel/sd-controlnet-openpose", torch_dtype=torch.float16\n        ... )\n        >>> motion_adapter = MotionAdapter.from_pretrained("wangfuyun/AnimateLCM")\n        >>> vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float16)\n\n        >>> pipe = AnimateDiffVideoToVideoControlNetPipeline.from_pretrained(\n        ...     "SG161222/Realistic_Vision_V5.1_noVAE",\n        ...     motion_adapter=motion_adapter,\n        ...     controlnet=controlnet,\n        ...     vae=vae,\n        ... ).to(device="cuda", dtype=torch.float16)\n\n        >>> pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear")\n        >>> pipe.load_lora_weights(\n        ...     "wangfuyun/AnimateLCM", weight_name="AnimateLCM_sd15_t2v_lora.safetensors", adapter_name="lcm-lora"\n        ... )\n        >>> pipe.set_adapters(["lcm-lora"], [0.8])\n\n        >>> video = load_video(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/dance.gif"\n        ... )\n        >>> video = [frame.convert("RGB") for frame in video]\n\n        >>> from controlnet_aux.processor import OpenposeDetector\n\n        >>> open_pose = OpenposeDetector.from_pretrained("lllyasviel/Annotators").to("cuda")\n        >>> for frame in tqdm(video):\n        ...     conditioning_frames.append(open_pose(frame))\n\n        >>> prompt = "astronaut in space, dancing"\n        >>> negative_prompt = "bad quality, worst quality, jpeg artifacts, ugly"\n\n        >>> strength = 0.8\n        >>> with torch.inference_mode():\n        ...     video = pipe(\n        ...         video=video,\n        ...         prompt=prompt,\n        ...         negative_prompt=negative_prompt,\n        ...         num_inference_steps=10,\n        ...         guidance_scale=2.0,\n        ...         controlnet_conditioning_scale=0.75,\n        ...         conditioning_frames=conditioning_frames,\n        ...         strength=strength,\n        ...         generator=torch.Generator().manual_seed(42),\n        ...     ).frames[0]\n\n        >>> video = [frame.resize(conditioning_frames[0].size) for frame in video]\n        >>> export_to_gif(video, f"animatediff_vid2vid_controlnet.gif", fps=8)\n        ```\n'
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
class AnimateDiffVideoToVideoControlNetPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, IPAdapterMixin, StableDiffusionLoraLoaderMixin, FreeInitMixin, AnimateDiffFreeNoiseMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->image_encoder->unet->vae'
    _optional_components = ['feature_extractor', 'image_encoder', 'motion_adapter']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, motion_adapter: MotionAdapter, controlnet: Union[ControlNetModel,
    List[ControlNetModel], Tuple[ControlNetModel], MultiControlNetModel], scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler, EulerDiscreteScheduler, EulerAncestralDiscreteScheduler,
    DPMSolverMultistepScheduler], feature_extractor: CLIPImageProcessor=None, image_encoder: CLIPVisionModelWithProjection=None):
        super().__init__()
        if isinstance(unet, UNet2DConditionModel): unet = UNetMotionModel.from_unet2d(unet, motion_adapter)
        if isinstance(controlnet, (list, tuple)): controlnet = MultiControlNetModel(controlnet)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, motion_adapter=motion_adapter, controlnet=controlnet,
        scheduler=scheduler, feature_extractor=feature_extractor, image_encoder=image_encoder)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_scale_factor)
        self.control_video_processor = VideoProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True, do_normalize=False)
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, (str, dict)): batch_size = 1
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
    def encode_video(self, video, generator, decode_chunk_size: int=16) -> torch.Tensor:
        latents = []
        for i in range(0, len(video), decode_chunk_size):
            batch_video = video[i:i + decode_chunk_size]
            batch_video = retrieve_latents(self.vae.encode(batch_video), generator=generator)
            latents.append(batch_video)
        return torch.cat(latents)
    def decode_latents(self, latents, decode_chunk_size: int=16):
        latents = 1 / self.vae.config.scaling_factor * latents
        batch_size, channels, num_frames, height, width = latents.shape
        latents = latents.permute(0, 2, 1, 3, 4).reshape(batch_size * num_frames, channels, height, width)
        video = []
        for i in range(0, latents.shape[0], decode_chunk_size):
            batch_latents = latents[i:i + decode_chunk_size]
            batch_latents = self.vae.decode(batch_latents).sample
            video.append(batch_latents)
        video = torch.cat(video)
        video = video[None, :].reshape((batch_size, num_frames, -1) + video.shape[2:]).permute(0, 2, 1, 3, 4)
        video = video.float()
        return video
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, strength, height, width, video=None, conditioning_frames=None, latents=None, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None,
    ip_adapter_image=None, ip_adapter_image_embeds=None, callback_on_step_end_tensor_inputs=None, controlnet_conditioning_scale=1.0, control_guidance_start=0.0, control_guidance_end=1.0):
        if strength < 0 or strength > 1: raise ValueError(f'The value of strength should in [0.0, 1.0] but is {strength}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, (str, list, dict))): raise ValueError(f'`prompt` has to be of type `str`, `list` or `dict` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if video is not None and latents is not None: raise ValueError('Only one of `video` or `latents` should be provided')
        if ip_adapter_image is not None and ip_adapter_image_embeds is not None: raise ValueError('Provide either `ip_adapter_image` or `ip_adapter_image_embeds`. Cannot leave both `ip_adapter_image` and `ip_adapter_image_embeds` defined.')
        if ip_adapter_image_embeds is not None:
            if not isinstance(ip_adapter_image_embeds, list): raise ValueError(f'`ip_adapter_image_embeds` has to be of type `list` but is {type(ip_adapter_image_embeds)}')
            elif ip_adapter_image_embeds[0].ndim not in [3, 4]: raise ValueError(f'`ip_adapter_image_embeds` has to be a list of 3D or 4D tensors but is {ip_adapter_image_embeds[0].ndim}D')
        is_compiled = hasattr(F, 'scaled_dot_product_attention') and isinstance(self.controlnet, torch._dynamo.eval_frame.OptimizedModule)
        num_frames = len(video) if latents is None else latents.shape[2]
        if isinstance(self.controlnet, ControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, ControlNetModel)):
            if not isinstance(conditioning_frames, list): raise TypeError(f'For single controlnet, `image` must be of type `list` but got {type(conditioning_frames)}')
            if len(conditioning_frames) != num_frames: raise ValueError(f'Excepted image to have length {num_frames} but got len(conditioning_frames)={len(conditioning_frames)!r}')
        elif isinstance(self.controlnet, MultiControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, MultiControlNetModel)):
            if not isinstance(conditioning_frames, list) or not isinstance(conditioning_frames[0], list): raise TypeError(f'For multiple controlnets: `image` must be type list of lists but got type(conditioning_frames)={type(conditioning_frames)!r}')
            if len(conditioning_frames[0]) != num_frames: raise ValueError(f'Expected length of image sublist as {num_frames} but got len(conditioning_frames)={len(conditioning_frames)!r}')
            if any((len(img) != len(conditioning_frames[0]) for img in conditioning_frames)): raise ValueError('All conditioning frame batches for multicontrolnet must be same size')
        else: assert False
        if isinstance(self.controlnet, ControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, ControlNetModel)):
            if not isinstance(controlnet_conditioning_scale, float): raise TypeError('For single controlnet: `controlnet_conditioning_scale` must be type `float`.')
        elif isinstance(self.controlnet, MultiControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, MultiControlNetModel)):
            if isinstance(controlnet_conditioning_scale, list):
                if any((isinstance(i, list) for i in controlnet_conditioning_scale)): raise ValueError('A single batch of multiple conditionings are supported at the moment.')
            elif isinstance(controlnet_conditioning_scale, list) and len(controlnet_conditioning_scale) != len(self.controlnet.nets): raise ValueError('For multiple controlnets: When `controlnet_conditioning_scale` is specified as `list`, it must have the same length as the number of controlnets')
        else: assert False
        if not isinstance(control_guidance_start, (tuple, list)): control_guidance_start = [control_guidance_start]
        if not isinstance(control_guidance_end, (tuple, list)): control_guidance_end = [control_guidance_end]
        if len(control_guidance_start) != len(control_guidance_end): raise ValueError(f'`control_guidance_start` has {len(control_guidance_start)} elements, but `control_guidance_end` has {len(control_guidance_end)} elements. Make sure to provide the same number of elements to each list.')
        if isinstance(self.controlnet, MultiControlNetModel):
            if len(control_guidance_start) != len(self.controlnet.nets): raise ValueError(f'`control_guidance_start`: {control_guidance_start} has {len(control_guidance_start)} elements but there are {len(self.controlnet.nets)} controlnets available. Make sure to provide {len(self.controlnet.nets)}.')
        for start, end in zip(control_guidance_start, control_guidance_end):
            if start >= end: raise ValueError(f'control guidance start: {start} cannot be larger or equal to control guidance end: {end}.')
            if start < 0.0: raise ValueError(f"control guidance start: {start} can't be smaller than 0.")
            if end > 1.0: raise ValueError(f"control guidance end: {end} can't be larger than 1.0.")
    def get_timesteps(self, num_inference_steps, timesteps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        timesteps = timesteps[t_start * self.scheduler.order:]
        return (timesteps, num_inference_steps - t_start)
    def prepare_latents(self, video: Optional[torch.Tensor]=None, height: int=64, width: int=64, num_channels_latents: int=4, batch_size: int=1, timestep: Optional[int]=None, dtype: Optional[torch.dtype]=None,
    device: Optional[torch.device]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, decode_chunk_size: int=16, add_noise: bool=False) -> torch.Tensor:
        num_frames = video.shape[1] if latents is None else latents.shape[2]
        shape = (batch_size, num_channels_latents, num_frames, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None:
            if self.vae.config.force_upcast:
                video = video.float()
                self.vae.to(dtype=torch.float32)
            if isinstance(generator, list): init_latents = [self.encode_video(video[i], generator[i], decode_chunk_size).unsqueeze(0) for i in range(batch_size)]
            else: init_latents = [self.encode_video(vid, generator, decode_chunk_size).unsqueeze(0) for vid in video]
            init_latents = torch.cat(init_latents, dim=0)
            if self.vae.config.force_upcast: self.vae.to(dtype)
            init_latents = init_latents.to(dtype)
            init_latents = self.vae.config.scaling_factor * init_latents
            if batch_size > init_latents.shape[0] and batch_size % init_latents.shape[0] == 0:
                error_message = f'You have passed {batch_size} text prompts (`prompt`), but only {init_latents.shape[0]} initial images (`image`). Please make sure to update your script to pass as many initial images as text prompts'
                raise ValueError(error_message)
            elif batch_size > init_latents.shape[0] and batch_size % init_latents.shape[0] != 0: raise ValueError(f'Cannot duplicate `image` of batch size {init_latents.shape[0]} to {batch_size} text prompts.')
            else: init_latents = torch.cat([init_latents], dim=0)
            noise = randn_tensor(init_latents.shape, generator=generator, device=device, dtype=dtype)
            latents = self.scheduler.add_noise(init_latents, noise, timestep).permute(0, 2, 1, 3, 4)
        else:
            if shape != latents.shape: raise ValueError(f'`latents` expected to have shape={shape!r}, but found latents.shape={latents.shape!r}')
            latents = latents.to(device, dtype=dtype)
            if add_noise:
                noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
                latents = self.scheduler.add_noise(latents, noise, timestep)
        return latents
    def prepare_conditioning_frames(self, video, width, height, batch_size, num_videos_per_prompt, device, dtype, do_classifier_free_guidance=False, guess_mode=False):
        video = self.control_video_processor.preprocess_video(video, height=height, width=width).to(dtype=torch.float32)
        video = video.permute(0, 2, 1, 3, 4).flatten(0, 1)
        video_batch_size = video.shape[0]
        if video_batch_size == 1: repeat_by = batch_size
        else: repeat_by = num_videos_per_prompt
        video = video.repeat_interleave(repeat_by, dim=0)
        video = video.to(device=device, dtype=dtype)
        if do_classifier_free_guidance and (not guess_mode): video = torch.cat([video] * 2)
        return video
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
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    def __call__(self, video: List[List[PipelineImageInput]]=None, prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50,
    enforce_inference_steps: bool=False, timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, guidance_scale: float=7.5, strength: float=0.8, negative_prompt: Optional[Union[str, List[str]]]=None,
    num_videos_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[List[torch.Tensor]]=None,
    conditioning_frames: Optional[List[PipelineImageInput]]=None, output_type: Optional[str]='pil', return_dict: bool=True, cross_attention_kwargs: Optional[Dict[str, Any]]=None,
    controlnet_conditioning_scale: Union[float, List[float]]=1.0, guess_mode: bool=False, control_guidance_start: Union[float, List[float]]=0.0, control_guidance_end: Union[float,
    List[float]]=1.0, clip_skip: Optional[int]=None, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], decode_chunk_size: int=16):
        """Examples:"""
        controlnet = self.controlnet._orig_mod if is_compiled_module(self.controlnet) else self.controlnet
        if not isinstance(control_guidance_start, list) and isinstance(control_guidance_end, list): control_guidance_start = len(control_guidance_end) * [control_guidance_start]
        elif not isinstance(control_guidance_end, list) and isinstance(control_guidance_start, list): control_guidance_end = len(control_guidance_start) * [control_guidance_end]
        elif not isinstance(control_guidance_start, list) and (not isinstance(control_guidance_end, list)):
            mult = len(controlnet.nets) if isinstance(controlnet, MultiControlNetModel) else 1
            control_guidance_start, control_guidance_end = (mult * [control_guidance_start], mult * [control_guidance_end])
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        num_videos_per_prompt = 1
        self.check_inputs(prompt=prompt, strength=strength, height=height, width=width, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, video=video,
        conditioning_frames=conditioning_frames, latents=latents, ip_adapter_image=ip_adapter_image, ip_adapter_image_embeds=ip_adapter_image_embeds, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs,
        controlnet_conditioning_scale=controlnet_conditioning_scale, control_guidance_start=control_guidance_start, control_guidance_end=control_guidance_end)
        self._guidance_scale = guidance_scale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, (str, dict)): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        dtype = self.dtype
        if not enforce_inference_steps:
            timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
            timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, timesteps, strength, device)
            latent_timestep = timesteps[:1].repeat(batch_size * num_videos_per_prompt)
        else:
            denoising_inference_steps = int(num_inference_steps / strength)
            timesteps, denoising_inference_steps = retrieve_timesteps(self.scheduler, denoising_inference_steps, device, timesteps, sigmas)
            timesteps = timesteps[-num_inference_steps:]
            latent_timestep = timesteps[:1].repeat(batch_size * num_videos_per_prompt)
        if latents is None:
            video = self.video_processor.preprocess_video(video, height=height, width=width)
            video = video.permute(0, 2, 1, 3, 4)
            video = video.to(device=device, dtype=dtype)
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(video=video, height=height, width=width, num_channels_latents=num_channels_latents, batch_size=batch_size * num_videos_per_prompt, timestep=latent_timestep, dtype=dtype,
        device=device, generator=generator, latents=latents, decode_chunk_size=decode_chunk_size, add_noise=enforce_inference_steps)
        text_encoder_lora_scale = self.cross_attention_kwargs.get('scale', None) if self.cross_attention_kwargs is not None else None
        num_frames = latents.shape[2]
        if self.free_noise_enabled: prompt_embeds, negative_prompt_embeds = self._encode_prompt_free_noise(prompt=prompt, num_frames=num_frames, device=device, num_videos_per_prompt=num_videos_per_prompt,
        do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        lora_scale=text_encoder_lora_scale, clip_skip=self.clip_skip)
        else:
            prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_videos_per_prompt, self.do_classifier_free_guidance, negative_prompt, prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=self.clip_skip)
            if self.do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            prompt_embeds = prompt_embeds.repeat_interleave(repeats=num_frames, dim=0)
        if ip_adapter_image is not None or ip_adapter_image_embeds is not None: image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image, ip_adapter_image_embeds,
        device, batch_size * num_videos_per_prompt, self.do_classifier_free_guidance)
        if isinstance(controlnet, MultiControlNetModel) and isinstance(controlnet_conditioning_scale, float): controlnet_conditioning_scale = [controlnet_conditioning_scale] * len(controlnet.nets)
        global_pool_conditions = controlnet.config.global_pool_conditions if isinstance(controlnet, ControlNetModel) else controlnet.nets[0].config.global_pool_conditions
        guess_mode = guess_mode or global_pool_conditions
        controlnet_keep = []
        for i in range(len(timesteps)):
            keeps = [1.0 - float(i / len(timesteps) < s or (i + 1) / len(timesteps) > e) for s, e in zip(control_guidance_start, control_guidance_end)]
            controlnet_keep.append(keeps[0] if isinstance(controlnet, ControlNetModel) else keeps)
        if isinstance(controlnet, ControlNetModel): conditioning_frames = self.prepare_conditioning_frames(video=conditioning_frames, width=width, height=height,
        batch_size=batch_size * num_videos_per_prompt * num_frames, num_videos_per_prompt=num_videos_per_prompt, device=device, dtype=controlnet.dtype,
        do_classifier_free_guidance=self.do_classifier_free_guidance, guess_mode=guess_mode)
        elif isinstance(controlnet, MultiControlNetModel):
            cond_prepared_videos = []
            for frame_ in conditioning_frames:
                prepared_video = self.prepare_conditioning_frames(video=frame_, width=width, height=height, batch_size=batch_size * num_videos_per_prompt * num_frames, num_videos_per_prompt=num_videos_per_prompt,
                device=device, dtype=controlnet.dtype, do_classifier_free_guidance=self.do_classifier_free_guidance, guess_mode=guess_mode)
                cond_prepared_videos.append(prepared_video)
            conditioning_frames = cond_prepared_videos
        else: assert False
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        added_cond_kwargs = {'image_embeds': image_embeds} if ip_adapter_image is not None or ip_adapter_image_embeds is not None else None
        num_free_init_iters = self._free_init_num_iters if self.free_init_enabled else 1
        for free_init_iter in range(num_free_init_iters):
            if self.free_init_enabled:
                latents, timesteps = self._apply_free_init(latents, free_init_iter, num_inference_steps, device, latents.dtype, generator)
                num_inference_steps = len(timesteps)
                timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, timesteps, strength, device)
            self._num_timesteps = len(timesteps)
            num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
            with self.progress_bar(total=self._num_timesteps) as progress_bar:
                for i, t in enumerate(timesteps):
                    if self.interrupt: continue
                    latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                    latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                    if guess_mode and self.do_classifier_free_guidance:
                        control_model_input = latents
                        control_model_input = self.scheduler.scale_model_input(control_model_input, t)
                        controlnet_prompt_embeds = prompt_embeds.chunk(2)[1]
                    else:
                        control_model_input = latent_model_input
                        controlnet_prompt_embeds = prompt_embeds
                    if isinstance(controlnet_keep[i], list): cond_scale = [c * s for c, s in zip(controlnet_conditioning_scale, controlnet_keep[i])]
                    else:
                        controlnet_cond_scale = controlnet_conditioning_scale
                        if isinstance(controlnet_cond_scale, list): controlnet_cond_scale = controlnet_cond_scale[0]
                        cond_scale = controlnet_cond_scale * controlnet_keep[i]
                    control_model_input = torch.transpose(control_model_input, 1, 2)
                    control_model_input = control_model_input.reshape((-1, control_model_input.shape[2], control_model_input.shape[3], control_model_input.shape[4]))
                    down_block_res_samples, mid_block_res_sample = self.controlnet(control_model_input, t, encoder_hidden_states=controlnet_prompt_embeds, controlnet_cond=conditioning_frames,
                    conditioning_scale=cond_scale, guess_mode=guess_mode, return_dict=False)
                    noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=self.cross_attention_kwargs, added_cond_kwargs=added_cond_kwargs,
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
            video_tensor = self.decode_latents(latents, decode_chunk_size)
            video = self.video_processor.postprocess_video(video=video_tensor, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return AnimateDiffPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
