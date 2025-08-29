'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, Dict, List, Optional, Union
import PIL
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection
from ...models import StableCascadeUNet
from ...schedulers import DDPMWuerstchenScheduler
from ...utils import is_torch_version, replace_example_docstring
from ..pipeline_utils import DiffusionPipeline
from ..wuerstchen.modeling_paella_vq_model import PaellaVQModel
from .pipeline_stable_cascade import StableCascadeDecoderPipeline
from .pipeline_stable_cascade_prior import StableCascadePriorPipeline
TEXT2IMAGE_EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableCascadeCombinedPipeline\n\n        >>> pipe = StableCascadeCombinedPipeline.from_pretrained(\n        ...     "stabilityai/stable-cascade", variant="bf16", torch_dtype=torch.bfloat16\n        ... )\n        >>> pipe.enable_model_cpu_offload()\n        >>> prompt = "an image of a shiba inu, donning a spacesuit and helmet"\n        >>> images = pipe(prompt=prompt)\n        ```\n'
class StableCascadeCombinedPipeline(DiffusionPipeline):
    """Args:"""
    _load_connected_pipes = True
    _optional_components = ['prior_feature_extractor', 'prior_image_encoder']
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: CLIPTextModel, decoder: StableCascadeUNet, scheduler: DDPMWuerstchenScheduler, vqgan: PaellaVQModel, prior_prior: StableCascadeUNet,
    prior_text_encoder: CLIPTextModel, prior_tokenizer: CLIPTokenizer, prior_scheduler: DDPMWuerstchenScheduler, prior_feature_extractor: Optional[CLIPImageProcessor]=None,
    prior_image_encoder: Optional[CLIPVisionModelWithProjection]=None):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, decoder=decoder, scheduler=scheduler, vqgan=vqgan, prior_text_encoder=prior_text_encoder,
        prior_tokenizer=prior_tokenizer, prior_prior=prior_prior, prior_scheduler=prior_scheduler, prior_feature_extractor=prior_feature_extractor, prior_image_encoder=prior_image_encoder)
        self.prior_pipe = StableCascadePriorPipeline(prior=prior_prior, text_encoder=prior_text_encoder, tokenizer=prior_tokenizer, scheduler=prior_scheduler,
        image_encoder=prior_image_encoder, feature_extractor=prior_feature_extractor)
        self.decoder_pipe = StableCascadeDecoderPipeline(text_encoder=text_encoder, tokenizer=tokenizer, decoder=decoder, scheduler=scheduler, vqgan=vqgan)
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
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, images: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]]=None, height: int=512,
    width: int=512, prior_num_inference_steps: int=60, prior_guidance_scale: float=4.0, num_inference_steps: int=12, decoder_guidance_scale: float=0.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_embeds_pooled: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds_pooled: Optional[torch.Tensor]=None, num_images_per_prompt: int=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, prior_callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, prior_callback_on_step_end_tensor_inputs: List[str]=['latents'],
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents']):
        """Examples:"""
        dtype = self.decoder_pipe.decoder.dtype
        if is_torch_version('<', '2.2.0') and dtype == torch.bfloat16: raise ValueError('`StableCascadeCombinedPipeline` requires torch>=2.2.0 when using `torch.bfloat16` dtype.')
        prior_outputs = self.prior_pipe(prompt=prompt if prompt_embeds is None else None, images=images, height=height, width=width, num_inference_steps=prior_num_inference_steps,
        guidance_scale=prior_guidance_scale, negative_prompt=negative_prompt if negative_prompt_embeds is None else None, prompt_embeds=prompt_embeds, prompt_embeds_pooled=prompt_embeds_pooled,
        negative_prompt_embeds=negative_prompt_embeds, negative_prompt_embeds_pooled=negative_prompt_embeds_pooled, num_images_per_prompt=num_images_per_prompt, generator=generator,
        latents=latents, output_type='pt', return_dict=True, callback_on_step_end=prior_callback_on_step_end, callback_on_step_end_tensor_inputs=prior_callback_on_step_end_tensor_inputs)
        image_embeddings = prior_outputs.image_embeddings
        prompt_embeds = prior_outputs.get('prompt_embeds', None)
        prompt_embeds_pooled = prior_outputs.get('prompt_embeds_pooled', None)
        negative_prompt_embeds = prior_outputs.get('negative_prompt_embeds', None)
        negative_prompt_embeds_pooled = prior_outputs.get('negative_prompt_embeds_pooled', None)
        outputs = self.decoder_pipe(image_embeddings=image_embeddings, prompt=prompt if prompt_embeds is None else None, num_inference_steps=num_inference_steps,
        guidance_scale=decoder_guidance_scale, negative_prompt=negative_prompt if negative_prompt_embeds is None else None, prompt_embeds=prompt_embeds, prompt_embeds_pooled=prompt_embeds_pooled,
        negative_prompt_embeds=negative_prompt_embeds, negative_prompt_embeds_pooled=negative_prompt_embeds_pooled, generator=generator, output_type=output_type, return_dict=return_dict,
        callback_on_step_end=callback_on_step_end, callback_on_step_end_tensor_inputs=callback_on_step_end_tensor_inputs)
        return outputs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
