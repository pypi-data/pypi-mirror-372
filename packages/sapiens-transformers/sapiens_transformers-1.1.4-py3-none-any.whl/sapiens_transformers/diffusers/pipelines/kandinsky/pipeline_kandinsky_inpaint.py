'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from copy import deepcopy
from typing import Callable, List, Optional, Union
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
from packaging import version
from PIL import Image
from sapiens_transformers import XLMRobertaTokenizer
from ... import __version__
from ...models import UNet2DConditionModel, VQModel
from ...schedulers import DDIMScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from .text_encoder import MultilingualCLIP
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import KandinskyInpaintPipeline, KandinskyPriorPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import torch\n        >>> import numpy as np\n\n        >>> pipe_prior = KandinskyPriorPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-1-prior", torch_dtype=torch.float16\n        ... )\n        >>> pipe_prior.to("cuda")\n\n        >>> prompt = "a hat"\n        >>> image_emb, zero_image_emb = pipe_prior(prompt, return_dict=False)\n\n        >>> pipe = KandinskyInpaintPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-1-inpaint", torch_dtype=torch.float16\n        ... )\n        >>> pipe.to("cuda")\n\n        >>> init_image = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/cat.png"\n        ... )\n\n        >>> mask = np.zeros((768, 768), dtype=np.float32)\n        >>> mask[:250, 250:-250] = 1\n\n        >>> out = pipe(\n        ...     prompt,\n        ...     image=init_image,\n        ...     mask_image=mask,\n        ...     image_embeds=image_emb,\n        ...     negative_image_embeds=zero_image_emb,\n        ...     height=768,\n        ...     width=768,\n        ...     num_inference_steps=50,\n        ... )\n\n        >>> image = out.images[0]\n        >>> image.save("cat_with_hat.png")\n        ```\n'
def get_new_h_w(h, w, scale_factor=8):
    new_h = h // scale_factor ** 2
    if h % scale_factor ** 2 != 0: new_h += 1
    new_w = w // scale_factor ** 2
    if w % scale_factor ** 2 != 0: new_w += 1
    return (new_h * scale_factor, new_w * scale_factor)
def prepare_mask(masks):
    prepared_masks = []
    for mask in masks:
        old_mask = deepcopy(mask)
        for i in range(mask.shape[1]):
            for j in range(mask.shape[2]):
                if old_mask[0][i][j] == 1: continue
                if i != 0: mask[:, i - 1, j] = 0
                if j != 0: mask[:, i, j - 1] = 0
                if i != 0 and j != 0: mask[:, i - 1, j - 1] = 0
                if i != mask.shape[1] - 1: mask[:, i + 1, j] = 0
                if j != mask.shape[2] - 1: mask[:, i, j + 1] = 0
                if i != mask.shape[1] - 1 and j != mask.shape[2] - 1: mask[:, i + 1, j + 1] = 0
        prepared_masks.append(mask)
    return torch.stack(prepared_masks, dim=0)
def prepare_mask_and_masked_image(image, mask, height, width):
    """Returns:"""
    if image is None: raise ValueError('`image` input cannot be undefined.')
    if mask is None: raise ValueError('`mask_image` input cannot be undefined.')
    if isinstance(image, torch.Tensor):
        if not isinstance(mask, torch.Tensor): raise TypeError(f'`image` is a torch.Tensor but `mask` (type: {type(mask)} is not')
        if image.ndim == 3:
            assert image.shape[0] == 3, 'Image outside a batch should be of shape (3, H, W)'
            image = image.unsqueeze(0)
        if mask.ndim == 2: mask = mask.unsqueeze(0).unsqueeze(0)
        if mask.ndim == 3:
            if mask.shape[0] == 1: mask = mask.unsqueeze(0)
            else: mask = mask.unsqueeze(1)
        assert image.ndim == 4 and mask.ndim == 4, 'Image and Mask must have 4 dimensions'
        assert image.shape[-2:] == mask.shape[-2:], 'Image and Mask must have the same spatial dimensions'
        assert image.shape[0] == mask.shape[0], 'Image and Mask must have the same batch size'
        if image.min() < -1 or image.max() > 1: raise ValueError('Image should be in [-1, 1] range')
        if mask.min() < 0 or mask.max() > 1: raise ValueError('Mask should be in [0, 1] range')
        mask[mask < 0.5] = 0
        mask[mask >= 0.5] = 1
        image = image.to(dtype=torch.float32)
    elif isinstance(mask, torch.Tensor): raise TypeError(f'`mask` is a torch.Tensor but `image` (type: {type(image)} is not')
    else:
        if isinstance(image, (PIL.Image.Image, np.ndarray)): image = [image]
        if isinstance(image, list) and isinstance(image[0], PIL.Image.Image):
            image = [i.resize((width, height), resample=Image.BICUBIC, reducing_gap=1) for i in image]
            image = [np.array(i.convert('RGB'))[None, :] for i in image]
            image = np.concatenate(image, axis=0)
        elif isinstance(image, list) and isinstance(image[0], np.ndarray): image = np.concatenate([i[None, :] for i in image], axis=0)
        image = image.transpose(0, 3, 1, 2)
        image = torch.from_numpy(image).to(dtype=torch.float32) / 127.5 - 1.0
        if isinstance(mask, (PIL.Image.Image, np.ndarray)): mask = [mask]
        if isinstance(mask, list) and isinstance(mask[0], PIL.Image.Image):
            mask = [i.resize((width, height), resample=PIL.Image.LANCZOS) for i in mask]
            mask = np.concatenate([np.array(m.convert('L'))[None, None, :] for m in mask], axis=0)
            mask = mask.astype(np.float32) / 255.0
        elif isinstance(mask, list) and isinstance(mask[0], np.ndarray): mask = np.concatenate([m[None, None, :] for m in mask], axis=0)
        mask[mask < 0.5] = 0
        mask[mask >= 0.5] = 1
        mask = torch.from_numpy(mask)
    mask = 1 - mask
    return (mask, image)
class KandinskyInpaintPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->movq'
    def __init__(self, text_encoder: MultilingualCLIP, movq: VQModel, tokenizer: XLMRobertaTokenizer, unet: UNet2DConditionModel, scheduler: DDIMScheduler):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, movq=movq, tokenizer=tokenizer, unet=unet, scheduler=scheduler)
        self.movq_scale_factor = 2 ** (len(self.movq.config.block_out_channels) - 1)
        self._warn_has_been_called = False
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None):
        batch_size = len(prompt) if isinstance(prompt, list) else 1
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=77, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
        text_input_ids = text_input_ids.to(device)
        text_mask = text_inputs.attention_mask.to(device)
        prompt_embeds, text_encoder_hidden_states = self.text_encoder(input_ids=text_input_ids, attention_mask=text_mask)
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
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=77, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            uncond_text_input_ids = uncond_input.input_ids.to(device)
            uncond_text_mask = uncond_input.attention_mask.to(device)
            negative_prompt_embeds, uncond_text_encoder_hidden_states = self.text_encoder(input_ids=uncond_text_input_ids, attention_mask=uncond_text_mask)
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
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], image: Union[torch.Tensor, PIL.Image.Image], mask_image: Union[torch.Tensor, PIL.Image.Image, np.ndarray], image_embeds: torch.Tensor,
    negative_image_embeds: torch.Tensor, negative_prompt: Optional[Union[str, List[str]]]=None, height: int=512, width: int=512, num_inference_steps: int=100, guidance_scale: float=4.0,
    num_images_per_prompt: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil',
    callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
        if not self._warn_has_been_called and version.parse(version.parse(__version__).base_version) < version.parse('0.23.0.dev0'): self._warn_has_been_called = True
        if isinstance(prompt, str): batch_size = 1
        elif isinstance(prompt, list): batch_size = len(prompt)
        else: raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        device = self._execution_device
        batch_size = batch_size * num_images_per_prompt
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, text_encoder_hidden_states, _ = self._encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt)
        if isinstance(image_embeds, list): image_embeds = torch.cat(image_embeds, dim=0)
        if isinstance(negative_image_embeds, list): negative_image_embeds = torch.cat(negative_image_embeds, dim=0)
        if do_classifier_free_guidance:
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            negative_image_embeds = negative_image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            image_embeds = torch.cat([negative_image_embeds, image_embeds], dim=0).to(dtype=prompt_embeds.dtype, device=device)
        mask_image, image = prepare_mask_and_masked_image(image, mask_image, height, width)
        image = image.to(dtype=prompt_embeds.dtype, device=device)
        image = self.movq.encode(image)['latents']
        mask_image = mask_image.to(dtype=prompt_embeds.dtype, device=device)
        image_shape = tuple(image.shape[-2:])
        mask_image = F.interpolate(mask_image, image_shape, mode='nearest')
        mask_image = prepare_mask(mask_image)
        masked_image = image * mask_image
        mask_image = mask_image.repeat_interleave(num_images_per_prompt, dim=0)
        masked_image = masked_image.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            mask_image = mask_image.repeat(2, 1, 1, 1)
            masked_image = masked_image.repeat(2, 1, 1, 1)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps_tensor = self.scheduler.timesteps
        num_channels_latents = self.movq.config.latent_channels
        sample_height, sample_width = get_new_h_w(height, width, self.movq_scale_factor)
        latents = self.prepare_latents((batch_size, num_channels_latents, sample_height, sample_width), text_encoder_hidden_states.dtype, device, generator, latents, self.scheduler)
        num_channels_mask = mask_image.shape[1]
        num_channels_masked_image = masked_image.shape[1]
        if num_channels_latents + num_channels_mask + num_channels_masked_image != self.unet.config.in_channels: raise ValueError(f'Incorrect configuration settings! The config of `pipeline.unet`: {self.unet.config} expects {self.unet.config.in_channels} but received `num_channels_latents`: {num_channels_latents} + `num_channels_mask`: {num_channels_mask} + `num_channels_masked_image`: {num_channels_masked_image} = {num_channels_latents + num_channels_masked_image + num_channels_mask}. Please verify the config of `pipeline.unet` or your `mask_image` or `image` input.')
        for i, t in enumerate(self.progress_bar(timesteps_tensor)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            latent_model_input = torch.cat([latent_model_input, masked_image, mask_image], dim=1)
            added_cond_kwargs = {'text_embeds': prompt_embeds, 'image_embeds': image_embeds}
            noise_pred = self.unet(sample=latent_model_input, timestep=t, encoder_hidden_states=text_encoder_hidden_states, added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
            if do_classifier_free_guidance:
                noise_pred, variance_pred = noise_pred.split(latents.shape[1], dim=1)
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                _, variance_pred_text = variance_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                noise_pred = torch.cat([noise_pred, variance_pred_text], dim=1)
            if not (hasattr(self.scheduler.config, 'variance_type') and self.scheduler.config.variance_type in ['learned', 'learned_range']): noise_pred, _ = noise_pred.split(latents.shape[1], dim=1)
            latents = self.scheduler.step(noise_pred, t, latents, generator=generator).prev_sample
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        image = self.movq.decode(latents, force_not_quantize=True)['sample']
        self.maybe_free_model_hooks()
        if output_type not in ['pt', 'np', 'pil']: raise ValueError(f'Only the output types `pt`, `pil` and `np` are supported not output_type={output_type}')
        if output_type in ['np', 'pil']:
            image = image * 0.5 + 0.5
            image = image.clamp(0, 1)
            image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
