'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import torch
from sapiens_transformers import CLIPTextModelWithProjection, CLIPTokenizer
from ...image_processor import VaeImageProcessor
from ...models import UVit2DModel, VQModel
from ...schedulers import AmusedScheduler
from ...utils import replace_example_docstring
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AmusedPipeline\n\n        >>> pipe = AmusedPipeline.from_pretrained("amused/amused-512", variant="fp16", torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n\n        >>> prompt = "a photo of an astronaut riding a horse on mars"\n        >>> image = pipe(prompt).images[0]\n        ```\n'
class AmusedPipeline(DiffusionPipeline):
    image_processor: VaeImageProcessor
    vqvae: VQModel
    tokenizer: CLIPTokenizer
    text_encoder: CLIPTextModelWithProjection
    transformer: UVit2DModel
    scheduler: AmusedScheduler
    model_cpu_offload_seq = 'text_encoder->transformer->vqvae'
    def __init__(self, vqvae: VQModel, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModelWithProjection, transformer: UVit2DModel, scheduler: AmusedScheduler):
        super().__init__()
        self.register_modules(vqvae=vqvae, tokenizer=tokenizer, text_encoder=text_encoder, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vqvae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_normalize=False)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[List[str], str]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=12, guidance_scale: float=10.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, generator: Optional[torch.Generator]=None, latents: Optional[torch.IntTensor]=None,
    prompt_embeds: Optional[torch.Tensor]=None, encoder_hidden_states: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    negative_encoder_hidden_states: Optional[torch.Tensor]=None, output_type='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None,
    callback_steps: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, micro_conditioning_aesthetic_score: int=6, micro_conditioning_crop_coord: Tuple[int, int]=(0, 0),
    temperature: Union[int, Tuple[int, int], List[int]]=(2, 0)):
        """Examples:"""
        if prompt_embeds is not None and encoder_hidden_states is None or (prompt_embeds is None and encoder_hidden_states is not None): raise ValueError('pass either both `prompt_embeds` and `encoder_hidden_states` or neither')
        if negative_prompt_embeds is not None and negative_encoder_hidden_states is None or (negative_prompt_embeds is None and negative_encoder_hidden_states is not None): raise ValueError('pass either both `negatve_prompt_embeds` and `negative_encoder_hidden_states` or neither')
        if prompt is None and prompt_embeds is None or (prompt is not None and prompt_embeds is not None): raise ValueError('pass only one of `prompt` or `prompt_embeds`')
        if isinstance(prompt, str): prompt = [prompt]
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        batch_size = batch_size * num_images_per_prompt
        if height is None: height = self.transformer.config.sample_size * self.vae_scale_factor
        if width is None: width = self.transformer.config.sample_size * self.vae_scale_factor
        if prompt_embeds is None:
            input_ids = self.tokenizer(prompt, return_tensors='pt', padding='max_length', truncation=True, max_length=self.tokenizer.model_max_length).input_ids.to(self._execution_device)
            outputs = self.text_encoder(input_ids, return_dict=True, output_hidden_states=True)
            prompt_embeds = outputs.text_embeds
            encoder_hidden_states = outputs.hidden_states[-2]
        prompt_embeds = prompt_embeds.repeat(num_images_per_prompt, 1)
        encoder_hidden_states = encoder_hidden_states.repeat(num_images_per_prompt, 1, 1)
        if guidance_scale > 1.0:
            if negative_prompt_embeds is None:
                if negative_prompt is None: negative_prompt = [''] * len(prompt)
                if isinstance(negative_prompt, str): negative_prompt = [negative_prompt]
                input_ids = self.tokenizer(negative_prompt, return_tensors='pt', padding='max_length', truncation=True, max_length=self.tokenizer.model_max_length).input_ids.to(self._execution_device)
                outputs = self.text_encoder(input_ids, return_dict=True, output_hidden_states=True)
                negative_prompt_embeds = outputs.text_embeds
                negative_encoder_hidden_states = outputs.hidden_states[-2]
            negative_prompt_embeds = negative_prompt_embeds.repeat(num_images_per_prompt, 1)
            negative_encoder_hidden_states = negative_encoder_hidden_states.repeat(num_images_per_prompt, 1, 1)
            prompt_embeds = torch.concat([negative_prompt_embeds, prompt_embeds])
            encoder_hidden_states = torch.concat([negative_encoder_hidden_states, encoder_hidden_states])
        micro_conds = torch.tensor([width, height, micro_conditioning_crop_coord[0], micro_conditioning_crop_coord[1], micro_conditioning_aesthetic_score], device=self._execution_device, dtype=encoder_hidden_states.dtype)
        micro_conds = micro_conds.unsqueeze(0)
        micro_conds = micro_conds.expand(2 * batch_size if guidance_scale > 1.0 else batch_size, -1)
        shape = (batch_size, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if latents is None: latents = torch.full(shape, self.scheduler.config.mask_token_id, dtype=torch.long, device=self._execution_device)
        self.scheduler.set_timesteps(num_inference_steps, temperature, self._execution_device)
        num_warmup_steps = len(self.scheduler.timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, timestep in enumerate(self.scheduler.timesteps):
                if guidance_scale > 1.0: model_input = torch.cat([latents] * 2)
                else: model_input = latents
                model_output = self.transformer(model_input, micro_conds=micro_conds, pooled_text_emb=prompt_embeds, encoder_hidden_states=encoder_hidden_states, cross_attention_kwargs=cross_attention_kwargs)
                if guidance_scale > 1.0:
                    uncond_logits, cond_logits = model_output.chunk(2)
                    model_output = uncond_logits + guidance_scale * (cond_logits - uncond_logits)
                latents = self.scheduler.step(model_output=model_output, timestep=timestep, sample=latents, generator=generator).prev_sample
                if i == len(self.scheduler.timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, timestep, latents)
        if output_type == 'latent': output = latents
        else:
            needs_upcasting = self.vqvae.dtype == torch.float16 and self.vqvae.config.force_upcast
            if needs_upcasting: self.vqvae.float()
            output = self.vqvae.decode(latents, force_not_quantize=True, shape=(batch_size, height // self.vae_scale_factor, width // self.vae_scale_factor, self.vqvae.config.latent_channels)).sample.clip(0, 1)
            output = self.image_processor.postprocess(output, output_type)
            if needs_upcasting: self.vqvae.half()
        self.maybe_free_model_hooks()
        if not return_dict: return (output,)
        return ImagePipelineOutput(output)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
