'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import torch
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import deprecate, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from .modeling_paella_vq_model import PaellaVQModel
from .modeling_wuerstchen_diffnext import WuerstchenDiffNeXt
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import WuerstchenPriorPipeline, WuerstchenDecoderPipeline\n\n        >>> prior_pipe = WuerstchenPriorPipeline.from_pretrained(\n        ...     "warp-ai/wuerstchen-prior", torch_dtype=torch.float16\n        ... ).to("cuda")\n        >>> gen_pipe = WuerstchenDecoderPipeline.from_pretrain("warp-ai/wuerstchen", torch_dtype=torch.float16).to(\n        ...     "cuda"\n        ... )\n\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> prior_output = pipe(prompt)\n        >>> images = gen_pipe(prior_output.image_embeddings, prompt=prompt)\n        ```\n'
class WuerstchenDecoderPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->decoder->vqgan'
    _callback_tensor_inputs = ['latents', 'text_encoder_hidden_states', 'negative_prompt_embeds', 'image_embeddings']
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModel, decoder: WuerstchenDiffNeXt, scheduler: DDPMWuerstchenScheduler,
    vqgan: PaellaVQModel, latent_dim_scale: float=10.67) -> None:
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, decoder=decoder, scheduler=scheduler, vqgan=vqgan)
        self.register_to_config(latent_dim_scale=latent_dim_scale)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None):
        batch_size = len(prompt) if isinstance(prompt, list) else 1
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        attention_mask = text_inputs.attention_mask
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
            removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
            attention_mask = attention_mask[:, :self.tokenizer.model_max_length]
        text_encoder_output = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask.to(device))
        text_encoder_hidden_states = text_encoder_output.last_hidden_state
        text_encoder_hidden_states = text_encoder_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
        uncond_text_encoder_hidden_states = None
        if do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=uncond_input.attention_mask.to(device))
            uncond_text_encoder_hidden_states = negative_prompt_embeds_text_encoder_output.last_hidden_state
            seq_len = uncond_text_encoder_hidden_states.shape[1]
            uncond_text_encoder_hidden_states = uncond_text_encoder_hidden_states.repeat(1, num_images_per_prompt, 1)
            uncond_text_encoder_hidden_states = uncond_text_encoder_hidden_states.view(batch_size * num_images_per_prompt, seq_len, -1)
        return (text_encoder_hidden_states, uncond_text_encoder_hidden_states)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image_embeddings: Union[torch.Tensor, List[torch.Tensor]], prompt: Union[str, List[str]]=None, num_inference_steps: int=12, timesteps: Optional[List[float]]=None,
    guidance_scale: float=0.0, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        callback = kwargs.pop('callback', None)
        callback_steps = kwargs.pop('callback_steps', None)
        if callback is not None: deprecate('callback', '1.0.0', 'Passing `callback` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_steps is not None: deprecate('callback_steps', '1.0.0', 'Passing `callback_steps` as an input argument to `__call__` is deprecated, consider use `callback_on_step_end`')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        device = self._execution_device
        dtype = self.decoder.dtype
        self._guidance_scale = guidance_scale
        if not isinstance(prompt, list):
            if isinstance(prompt, str): prompt = [prompt]
            else: raise TypeError(f"'prompt' must be of type 'list' or 'str', but got {type(prompt)}.")
        if self.do_classifier_free_guidance:
            if negative_prompt is not None and (not isinstance(negative_prompt, list)):
                if isinstance(negative_prompt, str): negative_prompt = [negative_prompt]
                else: raise TypeError(f"'negative_prompt' must be of type 'list' or 'str', but got {type(negative_prompt)}.")
        if isinstance(image_embeddings, list): image_embeddings = torch.cat(image_embeddings, dim=0)
        if isinstance(image_embeddings, np.ndarray): image_embeddings = torch.Tensor(image_embeddings, device=device).to(dtype=dtype)
        if not isinstance(image_embeddings, torch.Tensor): raise TypeError(f"'image_embeddings' must be of type 'torch.Tensor' or 'np.array', but got {type(image_embeddings)}.")
        if not isinstance(num_inference_steps, int): raise TypeError(f"'num_inference_steps' must be of type 'int', but got {type(num_inference_steps)}                           In Case you want to provide explicit timesteps, please use the 'timesteps' argument.")
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, image_embeddings.size(0) * num_images_per_prompt, self.do_classifier_free_guidance, negative_prompt)
        text_encoder_hidden_states = torch.cat([prompt_embeds, negative_prompt_embeds]) if negative_prompt_embeds is not None else prompt_embeds
        effnet = torch.cat([image_embeddings, torch.zeros_like(image_embeddings)]) if self.do_classifier_free_guidance else image_embeddings
        latent_height = int(image_embeddings.size(2) * self.config.latent_dim_scale)
        latent_width = int(image_embeddings.size(3) * self.config.latent_dim_scale)
        latent_features_shape = (image_embeddings.size(0) * num_images_per_prompt, 4, latent_height, latent_width)
        if timesteps is not None:
            self.scheduler.set_timesteps(timesteps=timesteps, device=device)
            timesteps = self.scheduler.timesteps
            num_inference_steps = len(timesteps)
        else:
            self.scheduler.set_timesteps(num_inference_steps, device=device)
            timesteps = self.scheduler.timesteps
        latents = self.prepare_latents(latent_features_shape, dtype, device, generator, latents, self.scheduler)
        self._num_timesteps = len(timesteps[:-1])
        for i, t in enumerate(self.progress_bar(timesteps[:-1])):
            ratio = t.expand(latents.size(0)).to(dtype)
            predicted_latents = self.decoder(torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents,
            r=torch.cat([ratio] * 2) if self.do_classifier_free_guidance else ratio, effnet=effnet, clip=text_encoder_hidden_states)
            if self.do_classifier_free_guidance:
                predicted_latents_text, predicted_latents_uncond = predicted_latents.chunk(2)
                predicted_latents = torch.lerp(predicted_latents_uncond, predicted_latents_text, self.guidance_scale)
            latents = self.scheduler.step(model_output=predicted_latents, timestep=ratio, sample=latents, generator=generator).prev_sample
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                image_embeddings = callback_outputs.pop('image_embeddings', image_embeddings)
                text_encoder_hidden_states = callback_outputs.pop('text_encoder_hidden_states', text_encoder_hidden_states)
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
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
