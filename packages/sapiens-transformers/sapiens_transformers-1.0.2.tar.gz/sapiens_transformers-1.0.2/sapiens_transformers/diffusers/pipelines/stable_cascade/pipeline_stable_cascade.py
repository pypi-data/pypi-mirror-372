'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import torch
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ...models import StableCascadeUNet
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import is_torch_version, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from ..wuerstchen.modeling_paella_vq_model import PaellaVQModel
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableCascadePriorPipeline, StableCascadeDecoderPipeline\n\n        >>> prior_pipe = StableCascadePriorPipeline.from_pretrained(\n        ...     "stabilityai/stable-cascade-prior", torch_dtype=torch.bfloat16\n        ... ).to("cuda")\n        >>> gen_pipe = StableCascadeDecoderPipeline.from_pretrain(\n        ...     "stabilityai/stable-cascade", torch_dtype=torch.float16\n        ... ).to("cuda")\n\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> prior_output = pipe(prompt)\n        >>> images = gen_pipe(prior_output.image_embeddings, prompt=prompt)\n        ```\n'
class StableCascadeDecoderPipeline(DiffusionPipeline):
    """Args:"""
    unet_name = 'decoder'
    text_encoder_name = 'text_encoder'
    model_cpu_offload_seq = 'text_encoder->decoder->vqgan'
    _callback_tensor_inputs = ['latents', 'prompt_embeds_pooled', 'negative_prompt_embeds', 'image_embeddings']
    def __init__(self, decoder: StableCascadeUNet, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModel, scheduler: DDPMWuerstchenScheduler, vqgan: PaellaVQModel, latent_dim_scale: float=10.67) -> None:
        super().__init__()
        self.register_modules(decoder=decoder, tokenizer=tokenizer, text_encoder=text_encoder, scheduler=scheduler, vqgan=vqgan)
        self.register_to_config(latent_dim_scale=latent_dim_scale)
    def prepare_latents(self, batch_size, image_embeddings, num_images_per_prompt, dtype, device, generator, latents, scheduler):
        _, channels, height, width = image_embeddings.shape
        latents_shape = (batch_size * num_images_per_prompt, 4, int(height * self.config.latent_dim_scale), int(width * self.config.latent_dim_scale))
        if latents is None: latents = randn_tensor(latents_shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latents_shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def encode_prompt(self, device, batch_size, num_images_per_prompt, do_classifier_free_guidance, prompt=None, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    prompt_embeds_pooled: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds_pooled: Optional[torch.Tensor]=None):
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            attention_mask = text_inputs.attention_mask
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
                removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
                attention_mask = attention_mask[:, :self.tokenizer.model_max_length]
            text_encoder_output = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask.to(device), output_hidden_states=True)
            prompt_embeds = text_encoder_output.hidden_states[-1]
            if prompt_embeds_pooled is None: prompt_embeds_pooled = text_encoder_output.text_embeds.unsqueeze(1)
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds_pooled = prompt_embeds_pooled.to(dtype=self.text_encoder.dtype, device=device)
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        prompt_embeds_pooled = prompt_embeds_pooled.repeat_interleave(num_images_per_prompt, dim=0)
        if negative_prompt_embeds is None and do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=uncond_input.attention_mask.to(device), output_hidden_states=True)
            negative_prompt_embeds = negative_prompt_embeds_text_encoder_output.hidden_states[-1]
            negative_prompt_embeds_pooled = negative_prompt_embeds_text_encoder_output.text_embeds.unsqueeze(1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            seq_len = negative_prompt_embeds_pooled.shape[1]
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds_pooled = negative_prompt_embeds_pooled.view(batch_size * num_images_per_prompt, seq_len, -1)
        return (prompt_embeds, prompt_embeds_pooled, negative_prompt_embeds, negative_prompt_embeds_pooled)
    def check_inputs(self, prompt, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, callback_on_step_end_tensor_inputs=None):
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    def get_timestep_ratio_conditioning(self, t, alphas_cumprod):
        s = torch.tensor([0.008])
        clamp_range = [0, 1]
        min_var = torch.cos(s / (1 + s) * torch.pi * 0.5) ** 2
        var = alphas_cumprod[t]
        var = var.clamp(*clamp_range)
        s, min_var = (s.to(var.device), min_var.to(var.device))
        ratio = ((var * min_var) ** 0.5).acos() / (torch.pi * 0.5) * (1 + s) - s
        return ratio
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image_embeddings: Union[torch.Tensor, List[torch.Tensor]], prompt: Union[str, List[str]]=None, num_inference_steps: int=10, guidance_scale: float=0.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_embeds_pooled: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds_pooled: Optional[torch.Tensor]=None, num_images_per_prompt: int=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        device = self._execution_device
        dtype = self.decoder.dtype
        self._guidance_scale = guidance_scale
        if is_torch_version('<', '2.2.0') and dtype == torch.bfloat16: raise ValueError('`StableCascadeDecoderPipeline` requires torch>=2.2.0 when using `torch.bfloat16` dtype.')
        self.check_inputs(prompt, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs)
        if isinstance(image_embeddings, list): image_embeddings = torch.cat(image_embeddings, dim=0)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        num_images_per_prompt = num_images_per_prompt * (image_embeddings.shape[0] // batch_size)
        if prompt_embeds is None and negative_prompt_embeds is None: _, prompt_embeds_pooled, _, negative_prompt_embeds_pooled = self.encode_prompt(prompt=prompt,
        device=device, batch_size=batch_size, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, prompt_embeds_pooled=prompt_embeds_pooled, negative_prompt_embeds=negative_prompt_embeds,
        negative_prompt_embeds_pooled=negative_prompt_embeds_pooled)
        prompt_embeds_pooled = torch.cat([prompt_embeds_pooled, negative_prompt_embeds_pooled]) if self.do_classifier_free_guidance else prompt_embeds_pooled
        effnet = torch.cat([image_embeddings, torch.zeros_like(image_embeddings)]) if self.do_classifier_free_guidance else image_embeddings
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        latents = self.prepare_latents(batch_size, image_embeddings, num_images_per_prompt, dtype, device, generator, latents, self.scheduler)
        if isinstance(self.scheduler, DDPMWuerstchenScheduler): timesteps = timesteps[:-1]
        elif hasattr(self.scheduler.config, 'clip_sample') and self.scheduler.config.clip_sample: self.scheduler.config.clip_sample = False
        if hasattr(self.scheduler, 'betas'):
            alphas = 1.0 - self.scheduler.betas
            alphas_cumprod = torch.cumprod(alphas, dim=0)
        else: alphas_cumprod = []
        self._num_timesteps = len(timesteps)
        for i, t in enumerate(self.progress_bar(timesteps)):
            if not isinstance(self.scheduler, DDPMWuerstchenScheduler):
                if len(alphas_cumprod) > 0:
                    timestep_ratio = self.get_timestep_ratio_conditioning(t.long().cpu(), alphas_cumprod)
                    timestep_ratio = timestep_ratio.expand(latents.size(0)).to(dtype).to(device)
                else: timestep_ratio = t.float().div(self.scheduler.timesteps[-1]).expand(latents.size(0)).to(dtype)
            else: timestep_ratio = t.expand(latents.size(0)).to(dtype)
            predicted_latents = self.decoder(sample=torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents,
            timestep_ratio=torch.cat([timestep_ratio] * 2) if self.do_classifier_free_guidance else timestep_ratio, clip_text_pooled=prompt_embeds_pooled, effnet=effnet, return_dict=False)[0]
            if self.do_classifier_free_guidance:
                predicted_latents_text, predicted_latents_uncond = predicted_latents.chunk(2)
                predicted_latents = torch.lerp(predicted_latents_uncond, predicted_latents_text, self.guidance_scale)
            if not isinstance(self.scheduler, DDPMWuerstchenScheduler): timestep_ratio = t
            latents = self.scheduler.step(model_output=predicted_latents, timestep=timestep_ratio, sample=latents, generator=generator).prev_sample
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
        if output_type not in ['pt', 'np', 'pil', 'latent']: raise ValueError(f'Only the output types `pt`, `np`, `pil` and `latent` are supported not output_type={output_type}')
        if not output_type == 'latent':
            latents = self.vqgan.config.scale_factor * latents
            images = self.vqgan.decode(latents).sample.clamp(0, 1)
            if output_type == 'np': images = images.permute(0, 2, 3, 1).cpu().float().numpy()
            elif output_type == 'pil':
                images = images.permute(0, 2, 3, 1).cpu().float().numpy()
                images = self.numpy_to_pil(images)
        else: images = latents
        self.maybe_free_model_hooks()
        if not return_dict: return images
        return ImagePipelineOutput(images)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
