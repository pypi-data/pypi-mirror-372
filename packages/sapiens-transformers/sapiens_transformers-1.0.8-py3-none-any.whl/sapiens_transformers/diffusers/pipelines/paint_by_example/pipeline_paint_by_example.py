'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, List, Optional, Union
import numpy as np
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor
from ...image_processor import VaeImageProcessor
from ...models import AutoencoderKL, UNet2DConditionModel
from ...schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
from ...utils import deprecate
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion import StableDiffusionPipelineOutput
from ..stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from .image_encoder import PaintByExampleImageEncoder
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
def prepare_mask_and_masked_image(image, mask):
    """Returns:"""
    if isinstance(image, torch.Tensor):
        if not isinstance(mask, torch.Tensor): raise TypeError(f'`image` is a torch.Tensor but `mask` (type: {type(mask)} is not')
        if image.ndim == 3:
            assert image.shape[0] == 3, 'Image outside a batch should be of shape (3, H, W)'
            image = image.unsqueeze(0)
        if mask.ndim == 2: mask = mask.unsqueeze(0).unsqueeze(0)
        if mask.ndim == 3:
            if mask.shape[0] == image.shape[0]: mask = mask.unsqueeze(1)
            else: mask = mask.unsqueeze(0)
        assert image.ndim == 4 and mask.ndim == 4, 'Image and Mask must have 4 dimensions'
        assert image.shape[-2:] == mask.shape[-2:], 'Image and Mask must have the same spatial dimensions'
        assert image.shape[0] == mask.shape[0], 'Image and Mask must have the same batch size'
        assert mask.shape[1] == 1, 'Mask image must have a single channel'
        if image.min() < -1 or image.max() > 1: raise ValueError('Image should be in [-1, 1] range')
        if mask.min() < 0 or mask.max() > 1: raise ValueError('Mask should be in [0, 1] range')
        mask = 1 - mask
        mask[mask < 0.5] = 0
        mask[mask >= 0.5] = 1
        image = image.to(dtype=torch.float32)
    elif isinstance(mask, torch.Tensor): raise TypeError(f'`mask` is a torch.Tensor but `image` (type: {type(image)} is not')
    else:
        if isinstance(image, PIL.Image.Image): image = [image]
        image = np.concatenate([np.array(i.convert('RGB'))[None, :] for i in image], axis=0)
        image = image.transpose(0, 3, 1, 2)
        image = torch.from_numpy(image).to(dtype=torch.float32) / 127.5 - 1.0
        if isinstance(mask, PIL.Image.Image): mask = [mask]
        mask = np.concatenate([np.array(m.convert('L'))[None, None, :] for m in mask], axis=0)
        mask = mask.astype(np.float32) / 255.0
        mask = 1 - mask
        mask[mask < 0.5] = 0
        mask[mask >= 0.5] = 1
        mask = torch.from_numpy(mask)
    masked_image = image * mask
    return (mask, masked_image)
class PaintByExamplePipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'unet->vae'
    _exclude_from_cpu_offload = ['image_encoder']
    _optional_components = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, image_encoder: PaintByExampleImageEncoder, unet: UNet2DConditionModel, scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler],
    safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=False):
        super().__init__()
        self.register_modules(vae=vae, image_encoder=image_encoder, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
    def run_safety_checker(self, image, device, dtype):
        if self.safety_checker is None: has_nsfw_concept = None
        else:
            if torch.is_tensor(image): feature_extractor_input = self.image_processor.postprocess(image, output_type='pil')
            else: feature_extractor_input = self.image_processor.numpy_to_pil(image)
            safety_checker_input = self.feature_extractor(feature_extractor_input, return_tensors='pt').to(device)
            image, has_nsfw_concept = self.safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(dtype))
        return (image, has_nsfw_concept)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def check_inputs(self, image, height, width, callback_steps):
        if not isinstance(image, torch.Tensor) and (not isinstance(image, PIL.Image.Image)) and (not isinstance(image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor` or `PIL.Image.Image` or `List[PIL.Image.Image]` but is {type(image)}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def prepare_mask_latents(self, mask, masked_image, batch_size, height, width, dtype, device, generator, do_classifier_free_guidance):
        mask = torch.nn.functional.interpolate(mask, size=(height // self.vae_scale_factor, width // self.vae_scale_factor))
        mask = mask.to(device=device, dtype=dtype)
        masked_image = masked_image.to(device=device, dtype=dtype)
        if masked_image.shape[1] == 4: masked_image_latents = masked_image
        else: masked_image_latents = self._encode_vae_image(masked_image, generator=generator)
        if mask.shape[0] < batch_size:
            if not batch_size % mask.shape[0] == 0: raise ValueError(f"The passed mask and the required batch size don't match. Masks are supposed to be duplicated to a total batch size of {batch_size}, but {mask.shape[0]} masks were passed. Make sure the number of masks that you pass is divisible by the total requested batch size.")
            mask = mask.repeat(batch_size // mask.shape[0], 1, 1, 1)
        if masked_image_latents.shape[0] < batch_size:
            if not batch_size % masked_image_latents.shape[0] == 0: raise ValueError(f"The passed images and the required batch size don't match. Images are supposed to be duplicated to a total batch size of {batch_size}, but {masked_image_latents.shape[0]} images were passed. Make sure the number of images that you pass is divisible by the total requested batch size.")
            masked_image_latents = masked_image_latents.repeat(batch_size // masked_image_latents.shape[0], 1, 1, 1)
        mask = torch.cat([mask] * 2) if do_classifier_free_guidance else mask
        masked_image_latents = torch.cat([masked_image_latents] * 2) if do_classifier_free_guidance else masked_image_latents
        masked_image_latents = masked_image_latents.to(device=device, dtype=dtype)
        return (mask, masked_image_latents)
    def _encode_vae_image(self, image: torch.Tensor, generator: torch.Generator):
        if isinstance(generator, list):
            image_latents = [retrieve_latents(self.vae.encode(image[i:i + 1]), generator=generator[i]) for i in range(image.shape[0])]
            image_latents = torch.cat(image_latents, dim=0)
        else: image_latents = retrieve_latents(self.vae.encode(image), generator=generator)
        image_latents = self.vae.config.scaling_factor * image_latents
        return image_latents
    def _encode_image(self, image, device, num_images_per_prompt, do_classifier_free_guidance):
        dtype = next(self.image_encoder.parameters()).dtype
        if not isinstance(image, torch.Tensor): image = self.feature_extractor(images=image, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=dtype)
        image_embeddings, negative_prompt_embeds = self.image_encoder(image, return_uncond_vector=True)
        bs_embed, seq_len, _ = image_embeddings.shape
        image_embeddings = image_embeddings.repeat(1, num_images_per_prompt, 1)
        image_embeddings = image_embeddings.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance:
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, image_embeddings.shape[0], 1)
            negative_prompt_embeds = negative_prompt_embeds.view(bs_embed * num_images_per_prompt, 1, -1)
            image_embeddings = torch.cat([negative_prompt_embeds, image_embeddings])
        return image_embeddings
    @torch.no_grad()
    def __call__(self, example_image: Union[torch.Tensor, PIL.Image.Image], image: Union[torch.Tensor, PIL.Image.Image], mask_image: Union[torch.Tensor, PIL.Image.Image],
    height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=5.0, negative_prompt: Optional[Union[str, List[str]]]=None,
    num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1):
        """Returns:"""
        if isinstance(image, PIL.Image.Image): batch_size = 1
        elif isinstance(image, list): batch_size = len(image)
        else: batch_size = image.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        mask, masked_image = prepare_mask_and_masked_image(image, mask_image)
        height, width = masked_image.shape[-2:]
        self.check_inputs(example_image, height, width, callback_steps)
        image_embeddings = self._encode_image(example_image, device, num_images_per_prompt, do_classifier_free_guidance)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.vae.config.latent_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, image_embeddings.dtype, device, generator, latents)
        mask, masked_image_latents = self.prepare_mask_latents(mask, masked_image, batch_size * num_images_per_prompt, height,
        width, image_embeddings.dtype, device, generator, do_classifier_free_guidance)
        num_channels_mask = mask.shape[1]
        num_channels_masked_image = masked_image_latents.shape[1]
        if num_channels_latents + num_channels_mask + num_channels_masked_image != self.unet.config.in_channels: raise ValueError(f'Incorrect configuration settings! The config of `pipeline.unet`: {self.unet.config} expects {self.unet.config.in_channels} but received `num_channels_latents`: {num_channels_latents} + `num_channels_mask`: {num_channels_mask} + `num_channels_masked_image`: {num_channels_masked_image} = {num_channels_latents + num_channels_masked_image + num_channels_mask}. Please verify the config of `pipeline.unet` or your `mask_image` or `image` input.')
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                latent_model_input = torch.cat([latent_model_input, masked_image_latents, mask], dim=1)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=image_embeddings).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        self.maybe_free_model_hooks()
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, device, image_embeddings.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
