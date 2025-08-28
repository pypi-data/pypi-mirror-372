'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from math import ceil
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import torch
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ...loaders import StableDiffusionLoraLoaderMixin
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import BaseOutput, deprecate, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .modeling_wuerstchen_prior import WuerstchenPrior
DEFAULT_STAGE_C_TIMESTEPS = list(np.linspace(1.0, 2 / 3, 20)) + list(np.linspace(2 / 3, 0.0, 11))[1:]
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import WuerstchenPriorPipeline\n\n        >>> prior_pipe = WuerstchenPriorPipeline.from_pretrained(\n        ...     "warp-ai/wuerstchen-prior", torch_dtype=torch.float16\n        ... ).to("cuda")\n\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> prior_output = pipe(prompt)\n        ```\n'
@dataclass
class WuerstchenPriorPipelineOutput(BaseOutput):
    """Args:"""
    image_embeddings: Union[torch.Tensor, np.ndarray]
class WuerstchenPriorPipeline(DiffusionPipeline, StableDiffusionLoraLoaderMixin):
    """Args:"""
    unet_name = 'prior'
    text_encoder_name = 'text_encoder'
    model_cpu_offload_seq = 'text_encoder->prior'
    _callback_tensor_inputs = ['latents', 'text_encoder_hidden_states', 'negative_prompt_embeds']
    _lora_loadable_modules = ['prior', 'text_encoder']
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModel, prior: WuerstchenPrior, scheduler: DDPMWuerstchenScheduler, latent_mean: float=42.0,
    latent_std: float=1.0, resolution_multiple: float=42.67) -> None:
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, prior=prior, scheduler=scheduler)
        self.register_to_config(latent_mean=latent_mean, latent_std=latent_std, resolution_multiple=resolution_multiple)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def encode_prompt(self, device, num_images_per_prompt, do_classifier_free_guidance, prompt=None, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None):
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            attention_mask = text_inputs.attention_mask
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
                removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
                attention_mask = attention_mask[:, :self.tokenizer.model_max_length]
            text_encoder_output = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask.to(device))
            prompt_embeds = text_encoder_output.last_hidden_state
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        if negative_prompt_embeds is None and do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=uncond_input.attention_mask.to(device))
            negative_prompt_embeds = negative_prompt_embeds_text_encoder_output.last_hidden_state
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return (prompt_embeds, negative_prompt_embeds)
    def check_inputs(self, prompt, negative_prompt, num_inference_steps, do_classifier_free_guidance, prompt_embeds=None, negative_prompt_embeds=None):
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if not isinstance(num_inference_steps, int): raise TypeError(f"'num_inference_steps' must be of type 'int', but got {type(num_inference_steps)}                           In Case you want to provide explicit timesteps, please use the 'timesteps' argument.")
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, height: int=1024, width: int=1024, num_inference_steps: int=60, timesteps: List[float]=None, guidance_scale: float=8.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, num_images_per_prompt: Optional[int]=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pt', return_dict: bool=True,
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        callback = kwargs.pop('callback', None)
        callback_steps = kwargs.pop('callback_steps', None)
        if callback is not None: deprecate('callback', '1.0.0', 'Passing `callback` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_steps is not None: deprecate('callback_steps', '1.0.0', 'Passing `callback_steps` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        device = self._execution_device
        self._guidance_scale = guidance_scale
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt is not None and (not isinstance(prompt, list)):
            if isinstance(prompt, str): prompt = [prompt]
            else: raise TypeError(f"'prompt' must be of type 'list' or 'str', but got {type(prompt)}.")
        if self.do_classifier_free_guidance:
            if negative_prompt is not None and (not isinstance(negative_prompt, list)):
                if isinstance(negative_prompt, str): negative_prompt = [negative_prompt]
                else: raise TypeError(f"'negative_prompt' must be of type 'list' or 'str', but got {type(negative_prompt)}.")
        self.check_inputs(prompt, negative_prompt, num_inference_steps, self.do_classifier_free_guidance, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt,
        do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        text_encoder_hidden_states = torch.cat([prompt_embeds, negative_prompt_embeds]) if negative_prompt_embeds is not None else prompt_embeds
        dtype = text_encoder_hidden_states.dtype
        latent_height = ceil(height / self.config.resolution_multiple)
        latent_width = ceil(width / self.config.resolution_multiple)
        num_channels = self.prior.config.c_in
        effnet_features_shape = (num_images_per_prompt * batch_size, num_channels, latent_height, latent_width)
        if timesteps is not None:
            self.scheduler.set_timesteps(timesteps=timesteps, device=device)
            timesteps = self.scheduler.timesteps
            num_inference_steps = len(timesteps)
        else:
            self.scheduler.set_timesteps(num_inference_steps, device=device)
            timesteps = self.scheduler.timesteps
        latents = self.prepare_latents(effnet_features_shape, dtype, device, generator, latents, self.scheduler)
        self._num_timesteps = len(timesteps[:-1])
        for i, t in enumerate(self.progress_bar(timesteps[:-1])):
            ratio = t.expand(latents.size(0)).to(dtype)
            predicted_image_embedding = self.prior(torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents,
            r=torch.cat([ratio] * 2) if self.do_classifier_free_guidance else ratio, c=text_encoder_hidden_states)
            if self.do_classifier_free_guidance:
                predicted_image_embedding_text, predicted_image_embedding_uncond = predicted_image_embedding.chunk(2)
                predicted_image_embedding = torch.lerp(predicted_image_embedding_uncond, predicted_image_embedding_text, self.guidance_scale)
            latents = self.scheduler.step(model_output=predicted_image_embedding, timestep=ratio, sample=latents, generator=generator).prev_sample
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                text_encoder_hidden_states = callback_outputs.pop('text_encoder_hidden_states', text_encoder_hidden_states)
                negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        latents = latents * self.config.latent_mean - self.config.latent_std
        self.maybe_free_model_hooks()
        if output_type == 'np': latents = latents.cpu().float().numpy()
        if not return_dict: return (latents,)
        return WuerstchenPriorPipelineOutput(latents)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
