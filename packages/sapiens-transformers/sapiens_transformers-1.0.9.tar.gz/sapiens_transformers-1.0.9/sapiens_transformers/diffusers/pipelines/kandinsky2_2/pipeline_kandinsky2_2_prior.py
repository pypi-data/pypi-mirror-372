'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModelWithProjection, CLIPTokenizer, CLIPVisionModelWithProjection
from ...models import PriorTransformer
from ...schedulers import UnCLIPScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..kandinsky import KandinskyPriorPipelineOutput
from ..pipeline_utils import DiffusionPipeline
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import KandinskyV22Pipeline, KandinskyV22PriorPipeline\n        >>> import torch\n\n        >>> pipe_prior = KandinskyV22PriorPipeline.from_pretrained("kandinsky-community/kandinsky-2-2-prior")\n        >>> pipe_prior.to("cuda")\n        >>> prompt = "red cat, 4k photo"\n        >>> image_emb, negative_image_emb = pipe_prior(prompt).to_tuple()\n\n        >>> pipe = KandinskyV22Pipeline.from_pretrained("kandinsky-community/kandinsky-2-2-decoder")\n        >>> pipe.to("cuda")\n        >>> image = pipe(\n        ...     image_embeds=image_emb,\n        ...     negative_image_embeds=negative_image_emb,\n        ...     height=768,\n        ...     width=768,\n        ...     num_inference_steps=50,\n        ... ).images\n        >>> image[0].save("cat.png")\n        ```\n'
EXAMPLE_INTERPOLATE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import KandinskyV22PriorPipeline, KandinskyV22Pipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import PIL\n        >>> import torch\n        >>> from torchvision import transforms\n\n        >>> pipe_prior = KandinskyV22PriorPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-prior", torch_dtype=torch.float16\n        ... )\n        >>> pipe_prior.to("cuda")\n        >>> img1 = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/cat.png"\n        ... )\n        >>> img2 = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/starry_night.jpeg"\n        ... )\n        >>> images_texts = ["a cat", img1, img2]\n        >>> weights = [0.3, 0.3, 0.4]\n        >>> out = pipe_prior.interpolate(images_texts, weights)\n        >>> pipe = KandinskyV22Pipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-2-decoder", torch_dtype=torch.float16\n        ... )\n        >>> pipe.to("cuda")\n        >>> image = pipe(\n        ...     image_embeds=out.image_embeds,\n        ...     negative_image_embeds=out.negative_image_embeds,\n        ...     height=768,\n        ...     width=768,\n        ...     num_inference_steps=50,\n        ... ).images[0]\n        >>> image.save("starry_cat.png")\n        ```\n'
class KandinskyV22PriorPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->image_encoder->prior'
    _exclude_from_cpu_offload = ['prior']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'text_encoder_hidden_states', 'text_mask']
    def __init__(self, prior: PriorTransformer, image_encoder: CLIPVisionModelWithProjection, text_encoder: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer,
    scheduler: UnCLIPScheduler, image_processor: CLIPImageProcessor):
        super().__init__()
        self.register_modules(prior=prior, text_encoder=text_encoder, tokenizer=tokenizer, scheduler=scheduler, image_encoder=image_encoder, image_processor=image_processor)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_INTERPOLATE_DOC_STRING)
    def interpolate(self, images_and_prompts: List[Union[str, PIL.Image.Image, torch.Tensor]], weights: List[float], num_images_per_prompt: int=1, num_inference_steps: int=25,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, negative_prior_prompt: Optional[str]=None,
    negative_prompt: str='', guidance_scale: float=4.0, device=None):
        """Examples:"""
        device = device or self.device
        if len(images_and_prompts) != len(weights): raise ValueError(f'`images_and_prompts` contains {len(images_and_prompts)} items and `weights` contains {len(weights)} items - they should be lists of same length')
        image_embeddings = []
        for cond, weight in zip(images_and_prompts, weights):
            if isinstance(cond, str): image_emb = self(cond, num_inference_steps=num_inference_steps, num_images_per_prompt=num_images_per_prompt, generator=generator, latents=latents,
            negative_prompt=negative_prior_prompt, guidance_scale=guidance_scale).image_embeds.unsqueeze(0)
            elif isinstance(cond, (PIL.Image.Image, torch.Tensor)):
                if isinstance(cond, PIL.Image.Image): cond = self.image_processor(cond, return_tensors='pt').pixel_values[0].unsqueeze(0).to(dtype=self.image_encoder.dtype, device=device)
                image_emb = self.image_encoder(cond)['image_embeds'].repeat(num_images_per_prompt, 1).unsqueeze(0)
            else: raise ValueError(f'`images_and_prompts` can only contains elements to be of type `str`, `PIL.Image.Image` or `torch.Tensor`  but is {type(cond)}')
            image_embeddings.append(image_emb * weight)
        image_emb = torch.cat(image_embeddings).sum(dim=0)
        out_zero = self(negative_prompt, num_inference_steps=num_inference_steps, num_images_per_prompt=num_images_per_prompt, generator=generator, latents=latents,
        negative_prompt=negative_prior_prompt, guidance_scale=guidance_scale)
        zero_image_emb = out_zero.negative_image_embeds if negative_prompt == '' else out_zero.image_embeds
        return KandinskyPriorPipelineOutput(image_embeds=image_emb, negative_image_embeds=zero_image_emb)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def get_zero_embed(self, batch_size=1, device=None):
        device = device or self.device
        zero_img = torch.zeros(1, 3, self.image_encoder.config.image_size, self.image_encoder.config.image_size).to(device=device, dtype=self.image_encoder.dtype)
        zero_image_emb = self.image_encoder(zero_img)['image_embeds']
        zero_image_emb = zero_image_emb.repeat(batch_size, 1)
        return zero_image_emb
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None):
        batch_size = len(prompt) if isinstance(prompt, list) else 1
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        text_mask = text_inputs.attention_mask.bool().to(device)
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
            removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
        text_encoder_output = self.text_encoder(text_input_ids.to(device))
        prompt_embeds = text_encoder_output.text_embeds
        text_encoder_hidden_states = text_encoder_output.last_hidden_state
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        text_encoder_hidden_states = text_encoder_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
        text_mask = text_mask.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            uncond_text_mask = uncond_input.attention_mask.bool().to(device)
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device))
            negative_prompt_embeds = negative_prompt_embeds_text_encoder_output.text_embeds
            uncond_text_encoder_hidden_states = negative_prompt_embeds_text_encoder_output.last_hidden_state
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len)
            seq_len = uncond_text_encoder_hidden_states.shape[1]
            uncond_text_encoder_hidden_states = uncond_text_encoder_hidden_states.repeat(1, num_images_per_prompt, 1)
            uncond_text_encoder_hidden_states = uncond_text_encoder_hidden_states.view(batch_size * num_images_per_prompt, seq_len, -1)
            uncond_text_mask = uncond_text_mask.repeat_interleave(num_images_per_prompt, dim=0)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            text_encoder_hidden_states = torch.cat([uncond_text_encoder_hidden_states, text_encoder_hidden_states])
            text_mask = torch.cat([uncond_text_mask, text_mask])
        return (prompt_embeds, text_encoder_hidden_states, text_mask)
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: int=1, num_inference_steps: int=25,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, guidance_scale: float=4.0, output_type: Optional[str]='pt',
    return_dict: bool=True, callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if isinstance(prompt, str): prompt = [prompt]
        elif not isinstance(prompt, list): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if isinstance(negative_prompt, str): negative_prompt = [negative_prompt]
        elif not isinstance(negative_prompt, list) and negative_prompt is not None: raise ValueError(f'`negative_prompt` has to be of type `str` or `list` but is {type(negative_prompt)}')
        if negative_prompt is not None:
            prompt = prompt + negative_prompt
            negative_prompt = 2 * negative_prompt
        device = self._execution_device
        batch_size = len(prompt)
        batch_size = batch_size * num_images_per_prompt
        self._guidance_scale = guidance_scale
        prompt_embeds, text_encoder_hidden_states, text_mask = self._encode_prompt(prompt, device, num_images_per_prompt, self.do_classifier_free_guidance, negative_prompt)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        embedding_dim = self.prior.config.embedding_dim
        latents = self.prepare_latents((batch_size, embedding_dim), prompt_embeds.dtype, device, generator, latents, self.scheduler)
        self._num_timesteps = len(timesteps)
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
            predicted_image_embedding = self.prior(latent_model_input, timestep=t, proj_embedding=prompt_embeds,
            encoder_hidden_states=text_encoder_hidden_states, attention_mask=text_mask).predicted_image_embedding
            if self.do_classifier_free_guidance:
                predicted_image_embedding_uncond, predicted_image_embedding_text = predicted_image_embedding.chunk(2)
                predicted_image_embedding = predicted_image_embedding_uncond + self.guidance_scale * (predicted_image_embedding_text - predicted_image_embedding_uncond)
            if i + 1 == timesteps.shape[0]: prev_timestep = None
            else: prev_timestep = timesteps[i + 1]
            latents = self.scheduler.step(predicted_image_embedding, timestep=t, sample=latents, generator=generator, prev_timestep=prev_timestep).prev_sample
            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop('latents', latents)
                prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                text_encoder_hidden_states = callback_outputs.pop('text_encoder_hidden_states', text_encoder_hidden_states)
                text_mask = callback_outputs.pop('text_mask', text_mask)
        latents = self.prior.post_process_latents(latents)
        image_embeddings = latents
        if negative_prompt is None: zero_embeds = self.get_zero_embed(latents.shape[0], device=latents.device)
        else: image_embeddings, zero_embeds = image_embeddings.chunk(2)
        self.maybe_free_model_hooks()
        if output_type not in ['pt', 'np']: raise ValueError(f'Only the output types `pt` and `np` are supported not output_type={output_type}')
        if output_type == 'np':
            image_embeddings = image_embeddings.cpu().numpy()
            zero_embeds = zero_embeds.cpu().numpy()
        if not return_dict: return (image_embeddings, zero_embeds)
        return KandinskyPriorPipelineOutput(image_embeds=image_embeddings, negative_image_embeds=zero_embeds)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
