'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, List, Optional, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModel
from ....models import AutoencoderKL, UNet2DConditionModel
from ....schedulers import KarrasDiffusionSchedulers
from ...pipeline_utils import DiffusionPipeline
from .pipeline_versatile_diffusion_dual_guided import VersatileDiffusionDualGuidedPipeline
from .pipeline_versatile_diffusion_image_variation import VersatileDiffusionImageVariationPipeline
from .pipeline_versatile_diffusion_text_to_image import VersatileDiffusionTextToImagePipeline
class VersatileDiffusionPipeline(DiffusionPipeline):
    """Args:"""
    tokenizer: CLIPTokenizer
    image_feature_extractor: CLIPImageProcessor
    text_encoder: CLIPTextModel
    image_encoder: CLIPVisionModel
    image_unet: UNet2DConditionModel
    text_unet: UNet2DConditionModel
    vae: AutoencoderKL
    scheduler: KarrasDiffusionSchedulers
    def __init__(self, tokenizer: CLIPTokenizer, image_feature_extractor: CLIPImageProcessor, text_encoder: CLIPTextModel, image_encoder: CLIPVisionModel, image_unet: UNet2DConditionModel,
    text_unet: UNet2DConditionModel, vae: AutoencoderKL, scheduler: KarrasDiffusionSchedulers):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, image_feature_extractor=image_feature_extractor, text_encoder=text_encoder, image_encoder=image_encoder,
        image_unet=image_unet, text_unet=text_unet, vae=vae, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
    @torch.no_grad()
    def image_variation(self, image: Union[torch.Tensor, PIL.Image.Image], height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Examples:"""
        expected_components = inspect.signature(VersatileDiffusionImageVariationPipeline.__init__).parameters.keys()
        components = {name: component for name, component in self.components.items() if name in expected_components}
        return VersatileDiffusionImageVariationPipeline(**components)(image=image, height=height, width=width, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale,
        negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, eta=eta, generator=generator, latents=latents, output_type=output_type,
        return_dict=return_dict, callback=callback, callback_steps=callback_steps)
    @torch.no_grad()
    def text_to_image(self, prompt: Union[str, List[str]], height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Examples:"""
        expected_components = inspect.signature(VersatileDiffusionTextToImagePipeline.__init__).parameters.keys()
        components = {name: component for name, component in self.components.items() if name in expected_components}
        temp_pipeline = VersatileDiffusionTextToImagePipeline(**components)
        output = temp_pipeline(prompt=prompt, height=height, width=width, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale, negative_prompt=negative_prompt,
        num_images_per_prompt=num_images_per_prompt, eta=eta, generator=generator, latents=latents, output_type=output_type, return_dict=return_dict, callback=callback, callback_steps=callback_steps)
        temp_pipeline._swap_unet_attention_blocks()
        return output
    @torch.no_grad()
    def dual_guided(self, prompt: Union[PIL.Image.Image, List[PIL.Image.Image]], image: Union[str, List[str]], text_to_image_strength: float=0.5, height: Optional[int]=None,
    width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Examples:"""
        expected_components = inspect.signature(VersatileDiffusionDualGuidedPipeline.__init__).parameters.keys()
        components = {name: component for name, component in self.components.items() if name in expected_components}
        temp_pipeline = VersatileDiffusionDualGuidedPipeline(**components)
        output = temp_pipeline(prompt=prompt, image=image, text_to_image_strength=text_to_image_strength, height=height, width=width, num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale, num_images_per_prompt=num_images_per_prompt, eta=eta, generator=generator, latents=latents, output_type=output_type,
        return_dict=return_dict, callback=callback, callback_steps=callback_steps)
        temp_pipeline._revert_dual_attention()
        return output
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
