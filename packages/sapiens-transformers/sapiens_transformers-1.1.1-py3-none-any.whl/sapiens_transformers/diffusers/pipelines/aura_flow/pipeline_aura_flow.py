'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import List, Optional, Tuple, Union
import torch
from sapiens_transformers import T5Tokenizer, UMT5EncoderModel
from ...image_processor import VaeImageProcessor
from ...models import AuraFlowTransformer2DModel, AutoencoderKL
from ...models.attention_processor import AttnProcessor2_0, FusedAttnProcessor2_0, XFormersAttnProcessor
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AuraFlowPipeline\n\n        >>> pipe = AuraFlowPipeline.from_pretrained("fal/AuraFlow", torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n        >>> prompt = "A cat holding a sign that says hello world"\n        >>> image = pipe(prompt).images[0]\n        >>> image.save("aura_flow.png")\n        ```\n'
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
class AuraFlowPipeline(DiffusionPipeline):
    """Args:"""
    _optional_components = []
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: UMT5EncoderModel, vae: AutoencoderKL, transformer: AuraFlowTransformer2DModel, scheduler: FlowMatchEulerDiscreteScheduler):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def check_inputs(self, prompt, height, width, negative_prompt, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and prompt_attention_mask is None: raise ValueError('Must provide `prompt_attention_mask` when specifying `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_prompt_attention_mask is None: raise ValueError('Must provide `negative_prompt_attention_mask` when specifying `negative_prompt_embeds`.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if prompt_attention_mask.shape != negative_prompt_attention_mask.shape: raise ValueError(f'`prompt_attention_mask` and `negative_prompt_attention_mask` must have the same shape when passed directly, but got: `prompt_attention_mask` {prompt_attention_mask.shape} != `negative_prompt_attention_mask` {negative_prompt_attention_mask.shape}.')
    def encode_prompt(self, prompt: Union[str, List[str]], negative_prompt: Union[str, List[str]]=None, do_classifier_free_guidance: bool=True, num_images_per_prompt: int=1,
    device: Optional[torch.device]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, max_sequence_length: int=256):
        """Args:"""
        if device is None: device = self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        max_length = max_sequence_length
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, truncation=True, max_length=max_length, padding='max_length', return_tensors='pt')
            text_input_ids = text_inputs['input_ids']
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_length - 1:-1])
            text_inputs = {k: v.to(device) for k, v in text_inputs.items()}
            prompt_embeds = self.text_encoder(**text_inputs)[0]
            prompt_attention_mask = text_inputs['attention_mask'].unsqueeze(-1).expand(prompt_embeds.shape)
            prompt_embeds = prompt_embeds * prompt_attention_mask
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        elif self.transformer is not None: dtype = self.transformer.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.reshape(bs_embed, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(num_images_per_prompt, 1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            uncond_tokens = [negative_prompt] * batch_size if isinstance(negative_prompt, str) else negative_prompt
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, truncation=True, max_length=max_length, padding='max_length', return_tensors='pt')
            uncond_input = {k: v.to(device) for k, v in uncond_input.items()}
            negative_prompt_embeds = self.text_encoder(**uncond_input)[0]
            negative_prompt_attention_mask = uncond_input['attention_mask'].unsqueeze(-1).expand(negative_prompt_embeds.shape)
            negative_prompt_embeds = negative_prompt_embeds * negative_prompt_attention_mask
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.reshape(bs_embed, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.repeat(num_images_per_prompt, 1)
        else:
            negative_prompt_embeds = None
            negative_prompt_attention_mask = None
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        if latents is not None: return latents.to(device=device, dtype=dtype)
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        return latents
    def upcast_vae(self):
        dtype = self.vae.dtype
        self.vae.to(dtype=torch.float32)
        use_torch_2_0_or_xformers = isinstance(self.vae.decoder.mid_block.attentions[0].processor, (AttnProcessor2_0, XFormersAttnProcessor, FusedAttnProcessor2_0))
        if use_torch_2_0_or_xformers:
            self.vae.post_quant_conv.to(dtype)
            self.vae.decoder.conv_in.to(dtype)
            self.vae.decoder.mid_block.to(dtype)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, negative_prompt: Union[str, List[str]]=None, num_inference_steps: int=50, sigmas: List[float]=None, guidance_scale: float=3.5,
    num_images_per_prompt: Optional[int]=1, height: Optional[int]=1024, width: Optional[int]=1024, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, max_sequence_length: int=256, output_type: Optional[str]='pil', return_dict: bool=True) -> Union[ImagePipelineOutput, Tuple]:
        """Examples:"""
        height = height or self.transformer.config.sample_size * self.vae_scale_factor
        width = width or self.transformer.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, negative_prompt, prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask = self.encode_prompt(prompt=prompt, negative_prompt=negative_prompt,
        do_classifier_free_guidance=do_classifier_free_guidance, num_images_per_prompt=num_images_per_prompt, device=device, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask, max_sequence_length=max_sequence_length)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, sigmas=sigmas)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, height, width, prompt_embeds.dtype, device, generator, latents)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                timestep = torch.tensor([t / 1000]).expand(latent_model_input.shape[0])
                timestep = timestep.to(latents.device, dtype=latents.dtype)
                noise_pred = self.transformer(latent_model_input, encoder_hidden_states=prompt_embeds, timestep=timestep, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if output_type == 'latent': image = latents
        else:
            needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
            if needs_upcasting:
                self.upcast_vae()
                latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
