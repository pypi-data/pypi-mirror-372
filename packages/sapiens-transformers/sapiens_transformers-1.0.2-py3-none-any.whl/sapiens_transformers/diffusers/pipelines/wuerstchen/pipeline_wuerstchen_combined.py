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
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import deprecate, replace_example_docstring
from ..pipeline_utils import DiffusionPipeline
from .modeling_paella_vq_model import PaellaVQModel
from .modeling_wuerstchen_diffnext import WuerstchenDiffNeXt
from .modeling_wuerstchen_prior import WuerstchenPrior
from .pipeline_wuerstchen import WuerstchenDecoderPipeline
from .pipeline_wuerstchen_prior import WuerstchenPriorPipeline
TEXT2IMAGE_EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from diffusions import WuerstchenCombinedPipeline\n\n        >>> pipe = WuerstchenCombinedPipeline.from_pretrained("warp-ai/Wuerstchen", torch_dtype=torch.float16).to(\n        ...     "cuda"\n        ... )\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> images = pipe(prompt=prompt)\n        ```\n'
class WuerstchenCombinedPipeline(DiffusionPipeline):
    """Args:"""
    _load_connected_pipes = True
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModel, decoder: WuerstchenDiffNeXt, scheduler: DDPMWuerstchenScheduler, vqgan: PaellaVQModel, prior_tokenizer: CLIPTokenizer,
    prior_text_encoder: CLIPTextModel, prior_prior: WuerstchenPrior, prior_scheduler: DDPMWuerstchenScheduler):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, decoder=decoder, scheduler=scheduler, vqgan=vqgan, prior_prior=prior_prior, prior_text_encoder=prior_text_encoder,
        prior_tokenizer=prior_tokenizer, prior_scheduler=prior_scheduler)
        self.prior_pipe = WuerstchenPriorPipeline(prior=prior_prior, text_encoder=prior_text_encoder, tokenizer=prior_tokenizer, scheduler=prior_scheduler)
        self.decoder_pipe = WuerstchenDecoderPipeline(text_encoder=text_encoder, tokenizer=tokenizer, decoder=decoder, scheduler=scheduler, vqgan=vqgan)
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None): self.decoder_pipe.enable_xformers_memory_efficient_attention(attention_op)
    def enable_model_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        self.prior_pipe.enable_model_cpu_offload(gpu_id=gpu_id, device=device)
        self.decoder_pipe.enable_model_cpu_offload(gpu_id=gpu_id, device=device)
    def enable_sequential_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        self.prior_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
        self.decoder_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
    def progress_bar(self, iterable=None, total=None):
        self.prior_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.progress_bar(iterable=iterable, total=total)
    def set_progress_bar_config(self, **kwargs):
        self.prior_pipe.set_progress_bar_config(**kwargs)
        self.decoder_pipe.set_progress_bar_config(**kwargs)
    @torch.no_grad()
    @replace_example_docstring(TEXT2IMAGE_EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, height: int=512, width: int=512, prior_num_inference_steps: int=60, prior_timesteps: Optional[List[float]]=None,
    prior_guidance_scale: float=4.0, num_inference_steps: int=12, decoder_timesteps: Optional[List[float]]=None, decoder_guidance_scale: float=0.0, negative_prompt: Optional[Union[str,
    List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, num_images_per_prompt: int=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    prior_callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, prior_callback_on_step_end_tensor_inputs: List[str]=['latents'],
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        prior_kwargs = {}
        if kwargs.get('prior_callback', None) is not None:
            prior_kwargs['callback'] = kwargs.pop('prior_callback')
            deprecate('prior_callback', '1.0.0', 'Passing `prior_callback` as an input argument to `__call__` is deprecated, consider use `prior_callback_on_step_end`')
        if kwargs.get('prior_callback_steps', None) is not None:
            deprecate('prior_callback_steps', '1.0.0', 'Passing `prior_callback_steps` as an input argument to `__call__` is deprecated, consider use `prior_callback_on_step_end`')
            prior_kwargs['callback_steps'] = kwargs.pop('prior_callback_steps')
        prior_outputs = self.prior_pipe(prompt=prompt if prompt_embeds is None else None, height=height, width=width, num_inference_steps=prior_num_inference_steps,
        timesteps=prior_timesteps, guidance_scale=prior_guidance_scale, negative_prompt=negative_prompt if negative_prompt_embeds is None else None, prompt_embeds=prompt_embeds,
        negative_prompt_embeds=negative_prompt_embeds, num_images_per_prompt=num_images_per_prompt, generator=generator, latents=latents, output_type='pt', return_dict=False,
        callback_on_step_end=prior_callback_on_step_end, callback_on_step_end_tensor_inputs=prior_callback_on_step_end_tensor_inputs, **prior_kwargs)
        image_embeddings = prior_outputs[0]
        outputs = self.decoder_pipe(image_embeddings=image_embeddings, prompt=prompt if prompt is not None else '', num_inference_steps=num_inference_steps,
        timesteps=decoder_timesteps, guidance_scale=decoder_guidance_scale, negative_prompt=negative_prompt, generator=generator, output_type=output_type,
        return_dict=return_dict, callback_on_step_end=callback_on_step_end, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs, **kwargs)
        return outputs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
