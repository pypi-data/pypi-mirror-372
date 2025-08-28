'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Union
import numpy as np
import PIL.Image
import torch
from PIL import Image
from sapiens_transformers import XLMRobertaTokenizer
from ...models import UNet2DConditionModel, VQModel
from ...schedulers import DDIMScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from .text_encoder import MultilingualCLIP
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import KandinskyImg2ImgPipeline, KandinskyPriorPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> import torch\n\n        >>> pipe_prior = KandinskyPriorPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-1-prior", torch_dtype=torch.float16\n        ... )\n        >>> pipe_prior.to("cuda")\n\n        >>> prompt = "A red cartoon frog, 4k"\n        >>> image_emb, zero_image_emb = pipe_prior(prompt, return_dict=False)\n\n        >>> pipe = KandinskyImg2ImgPipeline.from_pretrained(\n        ...     "kandinsky-community/kandinsky-2-1", torch_dtype=torch.float16\n        ... )\n        >>> pipe.to("cuda")\n\n        >>> init_image = load_image(\n        ...     "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main"\n        ...     "/kandinsky/frog.png"\n        ... )\n\n        >>> image = pipe(\n        ...     prompt,\n        ...     image=init_image,\n        ...     image_embeds=image_emb,\n        ...     negative_image_embeds=zero_image_emb,\n        ...     height=768,\n        ...     width=768,\n        ...     num_inference_steps=100,\n        ...     strength=0.2,\n        ... ).images\n\n        >>> image[0].save("red_frog.png")\n        ```\n'
def get_new_h_w(h, w, scale_factor=8):
    new_h = h // scale_factor ** 2
    if h % scale_factor ** 2 != 0: new_h += 1
    new_w = w // scale_factor ** 2
    if w % scale_factor ** 2 != 0: new_w += 1
    return (new_h * scale_factor, new_w * scale_factor)
def prepare_image(pil_image, w=512, h=512):
    pil_image = pil_image.resize((w, h), resample=Image.BICUBIC, reducing_gap=1)
    arr = np.array(pil_image.convert('RGB'))
    arr = arr.astype(np.float32) / 127.5 - 1
    arr = np.transpose(arr, [2, 0, 1])
    image = torch.from_numpy(arr).unsqueeze(0)
    return image
class KandinskyImg2ImgPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->movq'
    def __init__(self, text_encoder: MultilingualCLIP, movq: VQModel, tokenizer: XLMRobertaTokenizer, unet: UNet2DConditionModel, scheduler: DDIMScheduler):
        super().__init__()
        self.register_modules(text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, movq=movq)
        self.movq_scale_factor = 2 ** (len(self.movq.config.block_out_channels) - 1)
    def get_timesteps(self, num_inference_steps, strength, device):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        timesteps = self.scheduler.timesteps[t_start:]
        return (timesteps, num_inference_steps - t_start)
    def prepare_latents(self, latents, latent_timestep, shape, dtype, device, generator, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        shape = latents.shape
        noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        latents = self.add_noise(latents, noise, latent_timestep)
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
    def add_noise(self, original_samples: torch.Tensor, noise: torch.Tensor, timesteps: torch.IntTensor) -> torch.Tensor:
        betas = torch.linspace(0.0001, 0.02, 1000, dtype=torch.float32)
        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        alphas_cumprod = alphas_cumprod.to(device=original_samples.device, dtype=original_samples.dtype)
        timesteps = timesteps.to(original_samples.device)
        sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
        sqrt_alpha_prod = sqrt_alpha_prod.flatten()
        while len(sqrt_alpha_prod.shape) < len(original_samples.shape): sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
        sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
        while len(sqrt_one_minus_alpha_prod.shape) < len(original_samples.shape): sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)
        noisy_samples = sqrt_alpha_prod * original_samples + sqrt_one_minus_alpha_prod * noise
        return noisy_samples
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]], image: Union[torch.Tensor, PIL.Image.Image, List[torch.Tensor], List[PIL.Image.Image]], image_embeds: torch.Tensor,
    negative_image_embeds: torch.Tensor, negative_prompt: Optional[Union[str, List[str]]]=None, height: int=512, width: int=512, num_inference_steps: int=100,
    strength: float=0.3, guidance_scale: float=7.0, num_images_per_prompt: int=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    output_type: Optional[str]='pil', callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1, return_dict: bool=True):
        """Examples:"""
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
        if not isinstance(image, list): image = [image]
        if not all((isinstance(i, (PIL.Image.Image, torch.Tensor)) for i in image)): raise ValueError(f'Input is in incorrect format: {[type(i) for i in image]}. Currently, we only support  PIL image and pytorch tensor')
        image = torch.cat([prepare_image(i, width, height) for i in image], dim=0)
        image = image.to(dtype=prompt_embeds.dtype, device=device)
        latents = self.movq.encode(image)['latents']
        latents = latents.repeat_interleave(num_images_per_prompt, dim=0)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps_tensor, num_inference_steps = self.get_timesteps(num_inference_steps, strength, device)
        latent_timestep = int(self.scheduler.config.num_train_timesteps * strength) - 2
        latent_timestep = torch.tensor([latent_timestep] * batch_size, dtype=timesteps_tensor.dtype, device=device)
        num_channels_latents = self.unet.config.in_channels
        height, width = get_new_h_w(height, width, self.movq_scale_factor)
        latents = self.prepare_latents(latents, latent_timestep, (batch_size, num_channels_latents, height, width), text_encoder_hidden_states.dtype, device, generator, self.scheduler)
        for i, t in enumerate(self.progress_bar(timesteps_tensor)):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
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
