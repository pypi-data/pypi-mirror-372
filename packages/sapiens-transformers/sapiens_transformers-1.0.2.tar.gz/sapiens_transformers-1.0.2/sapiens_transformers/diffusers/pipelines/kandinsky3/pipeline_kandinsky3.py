'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer
from ...loaders import StableDiffusionLoraLoaderMixin
from ...models import Kandinsky3UNet, VQModel
from ...schedulers import DDPMScheduler
from ...utils import deprecate, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import AutoPipelineForText2Image\n        >>> import torch\n\n        >>> pipe = AutoPipelineForText2Image.from_pretrained(\n        ...     "kandinsky-community/kandinsky-3", variant="fp16", torch_dtype=torch.float16\n        ... )\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> prompt = "A photograph of the inside of a subway train. There are raccoons sitting on the seats. One of them is reading a newspaper. The window shows the city in the background."\n\n        >>> generator = torch.Generator(device="cpu").manual_seed(0)\n        >>> image = pipe(prompt, num_inference_steps=25, generator=generator).images[0]\n        ```\n\n'
def downscale_height_and_width(height, width, scale_factor=8):
    new_height = height // scale_factor ** 2
    if height % scale_factor ** 2 != 0: new_height += 1
    new_width = width // scale_factor ** 2
    if width % scale_factor ** 2 != 0: new_width += 1
    return (new_height * scale_factor, new_width * scale_factor)
class Kandinsky3Pipeline(DiffusionPipeline, StableDiffusionLoraLoaderMixin):
    model_cpu_offload_seq = 'text_encoder->unet->movq'
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'negative_attention_mask', 'attention_mask']
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, unet: Kandinsky3UNet, scheduler: DDPMScheduler, movq: VQModel):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, unet=unet, scheduler=scheduler, movq=movq)
    def process_embeds(self, embeddings, attention_mask, cut_context):
        if cut_context:
            embeddings[attention_mask == 0] = torch.zeros_like(embeddings[attention_mask == 0])
            max_seq_length = attention_mask.sum(-1).max() + 1
            embeddings = embeddings[:, :max_seq_length]
            attention_mask = attention_mask[:, :max_seq_length]
        return (embeddings, attention_mask)
    @torch.no_grad()
    def encode_prompt(self, prompt, do_classifier_free_guidance=True, num_images_per_prompt=1, device=None, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, _cut_context=False, attention_mask: Optional[torch.Tensor]=None, negative_attention_mask: Optional[torch.Tensor]=None):
        """Args:"""
        if prompt is not None and negative_prompt is not None:
            if type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
        if device is None: device = self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        max_length = 128
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids.to(device)
            attention_mask = text_inputs.attention_mask.to(device)
            prompt_embeds = self.text_encoder(text_input_ids, attention_mask=attention_mask)
            prompt_embeds = prompt_embeds[0]
            prompt_embeds, attention_mask = self.process_embeds(prompt_embeds, attention_mask, _cut_context)
            prompt_embeds = prompt_embeds * attention_mask.unsqueeze(2)
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        attention_mask = attention_mask.repeat(num_images_per_prompt, 1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            if negative_prompt is not None:
                uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=128, truncation=True, return_attention_mask=True, return_tensors='pt')
                text_input_ids = uncond_input.input_ids.to(device)
                negative_attention_mask = uncond_input.attention_mask.to(device)
                negative_prompt_embeds = self.text_encoder(text_input_ids, attention_mask=negative_attention_mask)
                negative_prompt_embeds = negative_prompt_embeds[0]
                negative_prompt_embeds = negative_prompt_embeds[:, :prompt_embeds.shape[1]]
                negative_attention_mask = negative_attention_mask[:, :prompt_embeds.shape[1]]
                negative_prompt_embeds = negative_prompt_embeds * negative_attention_mask.unsqueeze(2)
            else:
                negative_prompt_embeds = torch.zeros_like(prompt_embeds)
                negative_attention_mask = torch.zeros_like(attention_mask)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            if negative_prompt_embeds.shape != prompt_embeds.shape:
                negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
                negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
                negative_attention_mask = negative_attention_mask.repeat(num_images_per_prompt, 1)
        else:
            negative_prompt_embeds = None
            negative_attention_mask = None
        return (prompt_embeds, negative_prompt_embeds, attention_mask, negative_attention_mask)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def check_inputs(self, prompt, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, callback_on_step_end_tensor_inputs=None,
    attention_mask=None, negative_attention_mask=None):
        if callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if negative_prompt_embeds is not None and negative_attention_mask is None: raise ValueError('Please provide `negative_attention_mask` along with `negative_prompt_embeds`')
        if negative_prompt_embeds is not None and negative_attention_mask is not None:
            if negative_prompt_embeds.shape[:2] != negative_attention_mask.shape: raise ValueError(f'`negative_prompt_embeds` and `negative_attention_mask` must have the same batch_size and token length when passed directly, but got: `negative_prompt_embeds` {negative_prompt_embeds.shape[:2]} != `negative_attention_mask` {negative_attention_mask.shape}.')
        if prompt_embeds is not None and attention_mask is None: raise ValueError('Please provide `attention_mask` along with `prompt_embeds`')
        if prompt_embeds is not None and attention_mask is not None:
            if prompt_embeds.shape[:2] != attention_mask.shape: raise ValueError(f'`prompt_embeds` and `attention_mask` must have the same batch_size and token length when passed directly, but got: `prompt_embeds` {prompt_embeds.shape[:2]} != `attention_mask` {attention_mask.shape}.')
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, num_inference_steps: int=25, guidance_scale: float=3.0, negative_prompt: Optional[Union[str, List[str]]]=None,
    num_images_per_prompt: Optional[int]=1, height: Optional[int]=1024, width: Optional[int]=1024, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, attention_mask: Optional[torch.Tensor]=None,
    negative_attention_mask: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, latents=None, callback_on_step_end: Optional[Callable[[int,
    int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        callback = kwargs.pop('callback', None)
        callback_steps = kwargs.pop('callback_steps', None)
        if callback is not None: deprecate('callback', '1.0.0', 'Passing `callback` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_steps is not None: deprecate('callback_steps', '1.0.0', 'Passing `callback_steps` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        cut_context = True
        device = self._execution_device
        self.check_inputs(prompt, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds, callback_on_step_end_tensor_inputs, attention_mask, negative_attention_mask)
        self._guidance_scale = guidance_scale
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        prompt_embeds, negative_prompt_embeds, attention_mask, negative_attention_mask = self.encode_prompt(prompt, self.do_classifier_free_guidance,
        num_images_per_prompt=num_images_per_prompt, device=device, negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        _cut_context=cut_context, attention_mask=attention_mask, negative_attention_mask=negative_attention_mask)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            attention_mask = torch.cat([negative_attention_mask, attention_mask]).bool()
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        height, width = downscale_height_and_width(height, width, 8)
        latents = self.prepare_latents((batch_size * num_images_per_prompt, 4, height, width), prompt_embeds.dtype, device, generator, latents, self.scheduler)
        if hasattr(self, 'text_encoder_offload_hook') and self.text_encoder_offload_hook is not None: self.text_encoder_offload_hook.offload()
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, encoder_attention_mask=attention_mask, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = (guidance_scale + 1.0) * noise_pred_text - guidance_scale * noise_pred_uncond
                latents = self.scheduler.step(noise_pred, t, latents, generator=generator).prev_sample
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    attention_mask = callback_outputs.pop('attention_mask', attention_mask)
                    negative_attention_mask = callback_outputs.pop('negative_attention_mask', negative_attention_mask)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
            if output_type not in ['pt', 'np', 'pil', 'latent']: raise ValueError(f'Only the output types `pt`, `pil`, `np` and `latent` are supported not output_type={output_type}')
            if not output_type == 'latent':
                image = self.movq.decode(latents, force_not_quantize=True)['sample']
                if output_type in ['np', 'pil']:
                    image = image * 0.5 + 0.5
                    image = image.clamp(0, 1)
                    image = image.cpu().permute(0, 2, 3, 1).float().numpy()
                if output_type == 'pil': image = self.numpy_to_pil(image)
            else: image = latents
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
