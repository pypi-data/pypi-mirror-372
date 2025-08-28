'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModelWithProjection, CLIPTokenizer, CLIPVisionModelWithProjection, XLMRobertaTokenizer
from ...models import PriorTransformer, UNet2DConditionModel, VQModel
from ...schedulers import DDIMScheduler, DDPMScheduler, UnCLIPScheduler
from ...utils import replace_example_docstring
from ..pipeline_utils import DiffusionPipeline
from .pipeline_kandinsky import KandinskyPipeline
from .pipeline_kandinsky_img2img import KandinskyImg2ImgPipeline
from .pipeline_kandinsky_inpaint import KandinskyInpaintPipeline
from .pipeline_kandinsky_prior import KandinskyPriorPipeline
from .text_encoder import MultilingualCLIP
TEXT2IMAGE_EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        from sapiens_transformers.diffusers import AutoPipelineForText2Image\n        import torch\n\n        pipe = AutoPipelineForText2Image.from_pretrained(\n            "kandinsky-community/kandinsky-2-1", torch_dtype=torch.float16\n        )\n        pipe.enable_model_cpu_offload()\n\n        prompt = "A lion in galaxies, spirals, nebulae, stars, smoke, iridescent, intricate detail, octane render, 8k"\n\n        image = pipe(prompt=prompt, num_inference_steps=25).images[0]\n        ```\n'
IMAGE2IMAGE_EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        from sapiens_transformers.diffusers import AutoPipelineForImage2Image\n        import torch\n        import requests\n        from io import BytesIO\n        from PIL import Image\n        import os\n\n        pipe = AutoPipelineForImage2Image.from_pretrained(\n            "kandinsky-community/kandinsky-2-1", torch_dtype=torch.float16\n        )\n        pipe.enable_model_cpu_offload()\n\n        prompt = "A fantasy landscape, Cinematic lighting"\n        negative_prompt = "low quality, bad quality"\n\n        url = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"\n\n        response = requests.get(url)\n        image = Image.open(BytesIO(response.content)).convert("RGB")\n        image.thumbnail((768, 768))\n\n        image = pipe(prompt=prompt, image=original_image, num_inference_steps=25).images[0]\n        ```\n'
INPAINT_EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        from sapiens_transformers.diffusers import AutoPipelineForInpainting\n        from sapiens_transformers.diffusers.utils import load_image\n        import torch\n        import numpy as np\n\n        pipe = AutoPipelineForInpainting.from_pretrained(\n            "kandinsky-community/kandinsky-2-1-inpaint", torch_dtype=torch.float16\n        )\n        pipe.enable_model_cpu_offload()\n\n        prompt = "A fantasy landscape, Cinematic lighting"\n        negative_prompt = "low quality, bad quality"\n\n        original_image = load_image(\n            "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main" "/kandinsky/cat.png"\n        )\n\n        mask = np.zeros((768, 768), dtype=np.float32)\n        # Let\'s mask out an area above the cat\'s head\n        mask[:250, 250:-250] = 1\n\n        image = pipe(prompt=prompt, image=original_image, mask_image=mask, num_inference_steps=25).images[0]\n        ```\n'
class KandinskyCombinedPipeline(DiffusionPipeline):
    """Args:"""
    _load_connected_pipes = True
    model_cpu_offload_seq = 'text_encoder->unet->movq->prior_prior->prior_image_encoder->prior_text_encoder'
    _exclude_from_cpu_offload = ['prior_prior']
    def __init__(self, text_encoder: MultilingualCLIP, tokenizer: XLMRobertaTokenizer, unet: UNet2DConditionModel, scheduler: Union[DDIMScheduler, DDPMScheduler], movq: VQModel,
    prior_prior: PriorTransformer, prior_image_encoder: CLIPVisionModelWithProjection, prior_text_encoder: CLIPTextModelWithProjection, prior_tokenizer: CLIPTokenizer,
    prior_scheduler: UnCLIPScheduler, prior_image_processor: CLIPImageProcessor):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq, prior_prior=prior_prior, prior_image_encoder=prior_image_encoder,
        prior_text_encoder=prior_text_encoder, prior_tokenizer=prior_tokenizer, prior_scheduler=prior_scheduler, prior_image_processor=prior_image_processor)
        self.prior_pipe = KandinskyPriorPipeline(prior=prior_prior, image_encoder=prior_image_encoder, text_encoder=prior_text_encoder, tokenizer=prior_tokenizer,
        scheduler=prior_scheduler, image_processor=prior_image_processor)
        self.decoder_pipe = KandinskyPipeline(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq)
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None): self.decoder_pipe.enable_xformers_memory_efficient_attention(attention_op)
    def enable_sequential_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        self.prior_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
        self.decoder_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
    def progress_bar(self, iterable=None, total=None):
        self.prior_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.enable_model_cpu_offload()
    def set_progress_bar_config(self, **kwargs):
        self.prior_pipe.set_progress_bar_config(**kwargs)
        self.decoder_pipe.set_progress_bar_config(**kwargs)
    @torch.no_grad()
    @replace_example_docstring(TEXT2IMAGE_EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], negative_prompt: Optional[Union[str, List[str]]]=None, num_inference_steps: int=100, guidance_scale: float=4.0, num_images_per_prompt: int=1,
    height: int=512, width: int=512, prior_guidance_scale: float=4.0, prior_num_inference_steps: int=25, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
        prior_outputs = self.prior_pipe(prompt=prompt, negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, num_inference_steps=prior_num_inference_steps,
        generator=generator, latents=latents, guidance_scale=prior_guidance_scale, output_type='pt', return_dict=False)
        image_embeds = prior_outputs[0]
        negative_image_embeds = prior_outputs[1]
        prompt = [prompt] if not isinstance(prompt, (list, tuple)) else prompt
        if len(prompt) < image_embeds.shape[0] and image_embeds.shape[0] % len(prompt) == 0: prompt = image_embeds.shape[0] // len(prompt) * prompt
        outputs = self.decoder_pipe(prompt=prompt, image_embeds=image_embeds, negative_image_embeds=negative_image_embeds, width=width, height=height, num_inference_steps=num_inference_steps,
        generator=generator, guidance_scale=guidance_scale, output_type=output_type, callback=callback, callback_steps=callback_steps, return_dict=return_dict)
        self.maybe_free_model_hooks()
        return outputs
class KandinskyImg2ImgCombinedPipeline(DiffusionPipeline):
    """Args:"""
    _load_connected_pipes = True
    model_cpu_offload_seq = 'prior_text_encoder->prior_image_encoder->prior_prior->text_encoder->unet->movq'
    _exclude_from_cpu_offload = ['prior_prior']
    def __init__(self, text_encoder: MultilingualCLIP, tokenizer: XLMRobertaTokenizer, unet: UNet2DConditionModel, scheduler: Union[DDIMScheduler, DDPMScheduler], movq: VQModel,
    prior_prior: PriorTransformer, prior_image_encoder: CLIPVisionModelWithProjection, prior_text_encoder: CLIPTextModelWithProjection, prior_tokenizer: CLIPTokenizer,
    prior_scheduler: UnCLIPScheduler, prior_image_processor: CLIPImageProcessor):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq, prior_prior=prior_prior, prior_image_encoder=prior_image_encoder,
        prior_text_encoder=prior_text_encoder, prior_tokenizer=prior_tokenizer, prior_scheduler=prior_scheduler, prior_image_processor=prior_image_processor)
        self.prior_pipe = KandinskyPriorPipeline(prior=prior_prior, image_encoder=prior_image_encoder, text_encoder=prior_text_encoder,
        tokenizer=prior_tokenizer, scheduler=prior_scheduler, image_processor=prior_image_processor)
        self.decoder_pipe = KandinskyImg2ImgPipeline(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq)
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None): self.decoder_pipe.enable_xformers_memory_efficient_attention(attention_op)
    def enable_sequential_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        self.prior_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
        self.decoder_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
    def progress_bar(self, iterable=None, total=None):
        self.prior_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.enable_model_cpu_offload()
    def set_progress_bar_config(self, **kwargs):
        self.prior_pipe.set_progress_bar_config(**kwargs)
        self.decoder_pipe.set_progress_bar_config(**kwargs)
    @torch.no_grad()
    @replace_example_docstring(IMAGE2IMAGE_EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], image: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]], negative_prompt: Optional[Union[str,
    List[str]]]=None, num_inference_steps: int=100, guidance_scale: float=4.0, num_images_per_prompt: int=1, strength: float=0.3, height: int=512, width: int=512,
    prior_guidance_scale: float=4.0, prior_num_inference_steps: int=25, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
        prior_outputs = self.prior_pipe(prompt=prompt, negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, num_inference_steps=prior_num_inference_steps,
        generator=generator, latents=latents, guidance_scale=prior_guidance_scale, output_type='pt', return_dict=False)
        image_embeds = prior_outputs[0]
        negative_image_embeds = prior_outputs[1]
        prompt = [prompt] if not isinstance(prompt, (list, tuple)) else prompt
        image = [image] if isinstance(prompt, PIL.Image.Image) else image
        if len(prompt) < image_embeds.shape[0] and image_embeds.shape[0] % len(prompt) == 0: prompt = image_embeds.shape[0] // len(prompt) * prompt
        if isinstance(image, (list, tuple)) and len(image) < image_embeds.shape[0] and (image_embeds.shape[0] % len(image) == 0): image = image_embeds.shape[0] // len(image) * image
        outputs = self.decoder_pipe(prompt=prompt, image=image, image_embeds=image_embeds, negative_image_embeds=negative_image_embeds, strength=strength, width=width, height=height,
        num_inference_steps=num_inference_steps, generator=generator, guidance_scale=guidance_scale, output_type=output_type, callback=callback, callback_steps=callback_steps, return_dict=return_dict)
        self.maybe_free_model_hooks()
        return outputs
class KandinskyInpaintCombinedPipeline(DiffusionPipeline):
    """Args:"""
    _load_connected_pipes = True
    model_cpu_offload_seq = 'prior_text_encoder->prior_image_encoder->prior_prior->text_encoder->unet->movq'
    _exclude_from_cpu_offload = ['prior_prior']
    def __init__(self, text_encoder: MultilingualCLIP, tokenizer: XLMRobertaTokenizer, unet: UNet2DConditionModel, scheduler: Union[DDIMScheduler, DDPMScheduler], movq: VQModel,
    prior_prior: PriorTransformer, prior_image_encoder: CLIPVisionModelWithProjection, prior_text_encoder: CLIPTextModelWithProjection, prior_tokenizer: CLIPTokenizer,
    prior_scheduler: UnCLIPScheduler, prior_image_processor: CLIPImageProcessor):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq, prior_prior=prior_prior, prior_image_encoder=prior_image_encoder,
        prior_text_encoder=prior_text_encoder, prior_tokenizer=prior_tokenizer, prior_scheduler=prior_scheduler, prior_image_processor=prior_image_processor)
        self.prior_pipe = KandinskyPriorPipeline(prior=prior_prior, image_encoder=prior_image_encoder, text_encoder=prior_text_encoder,
        tokenizer=prior_tokenizer, scheduler=prior_scheduler, image_processor=prior_image_processor)
        self.decoder_pipe = KandinskyInpaintPipeline(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq)
    def enable_xformers_memory_efficient_attention(self, attention_op: Optional[Callable]=None): self.decoder_pipe.enable_xformers_memory_efficient_attention(attention_op)
    def enable_sequential_cpu_offload(self, gpu_id: Optional[int]=None, device: Union[torch.device, str]='cuda'):
        self.prior_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
        self.decoder_pipe.enable_sequential_cpu_offload(gpu_id=gpu_id, device=device)
    def progress_bar(self, iterable=None, total=None):
        self.prior_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.progress_bar(iterable=iterable, total=total)
        self.decoder_pipe.enable_model_cpu_offload()
    def set_progress_bar_config(self, **kwargs):
        self.prior_pipe.set_progress_bar_config(**kwargs)
        self.decoder_pipe.set_progress_bar_config(**kwargs)
    @torch.no_grad()
    @replace_example_docstring(INPAINT_EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], image: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]], mask_image: Union[torch.Tensor, PIL.Image.Image,
    List[torch.Tensor], List[PIL.Image.Image]], negative_prompt: Optional[Union[str, List[str]]]=None, num_inference_steps: int=100, guidance_scale: float=4.0, num_images_per_prompt: int=1,
    height: int=512, width: int=512, prior_guidance_scale: float=4.0, prior_num_inference_steps: int=25, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
        prior_outputs = self.prior_pipe(prompt=prompt, negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, num_inference_steps=prior_num_inference_steps,
        generator=generator, latents=latents, guidance_scale=prior_guidance_scale, output_type='pt', return_dict=False)
        image_embeds = prior_outputs[0]
        negative_image_embeds = prior_outputs[1]
        prompt = [prompt] if not isinstance(prompt, (list, tuple)) else prompt
        image = [image] if isinstance(prompt, PIL.Image.Image) else image
        mask_image = [mask_image] if isinstance(mask_image, PIL.Image.Image) else mask_image
        if len(prompt) < image_embeds.shape[0] and image_embeds.shape[0] % len(prompt) == 0: prompt = image_embeds.shape[0] // len(prompt) * prompt
        if isinstance(image, (list, tuple)) and len(image) < image_embeds.shape[0] and (image_embeds.shape[0] % len(image) == 0): image = image_embeds.shape[0] // len(image) * image
        if isinstance(mask_image, (list, tuple)) and len(mask_image) < image_embeds.shape[0] and (image_embeds.shape[0] % len(mask_image) == 0): mask_image = image_embeds.shape[0] // len(mask_image) * mask_image
        outputs = self.decoder_pipe(prompt=prompt, image=image, mask_image=mask_image, image_embeds=image_embeds, negative_image_embeds=negative_image_embeds, width=width, height=height,
        num_inference_steps=num_inference_steps, generator=generator, guidance_scale=guidance_scale, output_type=output_type, callback=callback, callback_steps=callback_steps, return_dict=return_dict)
        self.maybe_free_model_hooks()
        return outputs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
