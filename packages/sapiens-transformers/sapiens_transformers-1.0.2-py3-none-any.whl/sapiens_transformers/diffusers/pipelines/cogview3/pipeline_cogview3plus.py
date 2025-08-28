'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, Dict, List, Optional, Tuple, Union
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import VaeImageProcessor
from ...models import AutoencoderKL, CogView3PlusTransformer2DModel
from ...pipelines.pipeline_utils import DiffusionPipeline
from ...schedulers import CogVideoXDDIMScheduler, CogVideoXDPMScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from .pipeline_output import CogView3PipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```python\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import CogView3PlusPipeline\n\n        >>> pipe = CogView3PlusPipeline.from_pretrained("THUDM/CogView3-Plus-3B", torch_dtype=torch.bfloat16)\n        >>> pipe.to("cuda")\n\n        >>> prompt = "A photo of an astronaut riding a horse on mars"\n        >>> image = pipe(prompt).images[0]\n        >>> image.save("output.png")\n        ```\n'
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
class CogView3PlusPipeline(DiffusionPipeline):
    """Args:"""
    _optional_components = []
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, vae: AutoencoderKL, transformer: CogView3PlusTransformer2DModel, scheduler: Union[CogVideoXDDIMScheduler, CogVideoXDPMScheduler]):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def _get_t5_prompt_embeds(self, prompt: Union[str, List[str]]=None, num_images_per_prompt: int=1, max_sequence_length: int=226, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
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
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return prompt_embeds
    def encode_prompt(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, do_classifier_free_guidance: bool=True, num_images_per_prompt: int=1, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, max_sequence_length: int=224, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None):
        """Args:"""
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None: prompt_embeds = self._get_t5_prompt_embeds(prompt=prompt, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        if do_classifier_free_guidance and negative_prompt is None: negative_prompt_embeds = prompt_embeds.new_zeros(prompt_embeds.shape)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            negative_prompt_embeds = self._get_t5_prompt_embeds(prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, max_sequence_length=max_sequence_length, device=device, dtype=dtype)
        return (prompt_embeds, negative_prompt_embeds)
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, negative_prompt, callback_on_step_end_tensor_inputs, prompt_embeds=None, negative_prompt_embeds=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, negative_prompt: Optional[Union[str, List[str]]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, timesteps: Optional[List[int]]=None, guidance_scale: float=5.0, num_images_per_prompt: int=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.FloatTensor]=None, prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None, original_size: Optional[Tuple[int, int]]=None, crops_coords_top_left: Tuple[int, int]=(0, 0), output_type: str='pil', return_dict: bool=True, callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=224) -> Union[CogView3PipelineOutput, Tuple]:
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.transformer.config.sample_size * self.vae_scale_factor
        width = width or self.transformer.config.sample_size * self.vae_scale_factor
        original_size = original_size or (height, width)
        target_size = (height, width)
        self.check_inputs(prompt, height, width, negative_prompt, callback_on_step_end_tensor_inputs, prompt_embeds, negative_prompt_embeds)
        self._guidance_scale = guidance_scale
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, negative_prompt, self.do_classifier_free_guidance, num_images_per_prompt=num_images_per_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, max_sequence_length=max_sequence_length, device=device)
        if self.do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps)
        self._num_timesteps = len(timesteps)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        original_size = torch.tensor([original_size], dtype=prompt_embeds.dtype)
        target_size = torch.tensor([target_size], dtype=prompt_embeds.dtype)
        crops_coords_top_left = torch.tensor([crops_coords_top_left], dtype=prompt_embeds.dtype)
        if self.do_classifier_free_guidance:
            original_size = torch.cat([original_size, original_size])
            target_size = torch.cat([target_size, target_size])
            crops_coords_top_left = torch.cat([crops_coords_top_left, crops_coords_top_left])
        original_size = original_size.to(device).repeat(batch_size * num_images_per_prompt, 1)
        target_size = target_size.to(device).repeat(batch_size * num_images_per_prompt, 1)
        crops_coords_top_left = crops_coords_top_left.to(device).repeat(batch_size * num_images_per_prompt, 1)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            old_pred_original_sample = None
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                timestep = t.expand(latent_model_input.shape[0])
                noise_pred = self.transformer(hidden_states=latent_model_input, encoder_hidden_states=prompt_embeds, timestep=timestep, original_size=original_size, target_size=target_size, crop_coords=crops_coords_top_left, return_dict=False)[0]
                noise_pred = noise_pred.float()
                if self.do_classifier_free_guidance:
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
        if not output_type == 'latent': image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False, generator=generator)[0]
        else: image = latents
        image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return CogView3PipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
