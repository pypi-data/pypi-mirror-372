'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
from sapiens_transformers import BlipForConditionalGeneration, BlipProcessor, CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ....image_processor import PipelineImageInput, VaeImageProcessor
from ....loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ....models import AutoencoderKL, UNet2DConditionModel
from ....models.attention_processor import Attention
from ....models.lora import adjust_lora_scale_text_encoder
from ....schedulers import DDIMScheduler, DDPMScheduler, EulerAncestralDiscreteScheduler, LMSDiscreteScheduler
from ....schedulers.scheduling_ddim_inverse import DDIMInverseScheduler
from ....utils import PIL_INTERPOLATION, USE_PEFT_BACKEND, BaseOutput, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ...stable_diffusion.pipeline_output import StableDiffusionPipelineOutput
from ...stable_diffusion.safety_checker import StableDiffusionSafetyChecker
@dataclass
class Pix2PixInversionPipelineOutput(BaseOutput, TextualInversionLoaderMixin):
    """Args:"""
    latents: torch.Tensor
    images: Union[List[PIL.Image.Image], np.ndarray]
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import requests\n        >>> import torch\n\n        >>> from sapiens_transformers.diffusers import DDIMScheduler, StableDiffusionPix2PixZeroPipeline\n\n\n        >>> def download(embedding_url, local_filepath):\n        ...     r = requests.get(embedding_url)\n        ...     with open(local_filepath, "wb") as f:\n        ...         f.write(r.content)\n\n\n        >>> model_ckpt = "CompVis/stable-diffusion-v1-4"\n        >>> pipeline = StableDiffusionPix2PixZeroPipeline.from_pretrained(model_ckpt, torch_dtype=torch.float16)\n        >>> pipeline.scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.to("cuda")\n\n        >>> prompt = "a high resolution painting of a cat in the style of van gough"\n        >>> source_emb_url = "https://hf.co/datasets/sayakpaul/sample-datasets/resolve/main/cat.pt"\n        >>> target_emb_url = "https://hf.co/datasets/sayakpaul/sample-datasets/resolve/main/dog.pt"\n\n        >>> for url in [source_emb_url, target_emb_url]:\n        ...     download(url, url.split("/")[-1])\n\n        >>> src_embeds = torch.load(source_emb_url.split("/")[-1])\n        >>> target_embeds = torch.load(target_emb_url.split("/")[-1])\n        >>> images = pipeline(\n        ...     prompt,\n        ...     source_embeds=src_embeds,\n        ...     target_embeds=target_embeds,\n        ...     num_inference_steps=50,\n        ...     cross_attention_guidance_amount=0.15,\n        ... ).images\n\n        >>> images[0].save("edited_image_dog.png")\n        ```\n'
EXAMPLE_INVERT_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers import BlipForConditionalGeneration, BlipProcessor\n        >>> from sapiens_transformers.diffusers import DDIMScheduler, DDIMInverseScheduler, StableDiffusionPix2PixZeroPipeline\n\n        >>> import requests\n        >>> from PIL import Image\n\n        >>> captioner_id = "Salesforce/blip-image-captioning-base"\n        >>> processor = BlipProcessor.from_pretrained(captioner_id)\n        >>> model = BlipForConditionalGeneration.from_pretrained(\n        ...     captioner_id, torch_dtype=torch.float16, low_cpu_mem_usage=True\n        ... )\n\n        >>> sd_model_ckpt = "CompVis/stable-diffusion-v1-4"\n        >>> pipeline = StableDiffusionPix2PixZeroPipeline.from_pretrained(\n        ...     sd_model_ckpt,\n        ...     caption_generator=model,\n        ...     caption_processor=processor,\n        ...     torch_dtype=torch.float16,\n        ...     safety_checker=None,\n        ... )\n\n        >>> pipeline.scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.inverse_scheduler = DDIMInverseScheduler.from_config(pipeline.scheduler.config)\n        >>> pipeline.enable_model_cpu_offload()\n\n        >>> img_url = "https://github.com/pix2pixzero/pix2pix-zero/raw/main/assets/test_images/cats/cat_6.png"\n\n        >>> raw_image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB").resize((512, 512))\n        >>> # generate caption\n        >>> caption = pipeline.generate_caption(raw_image)\n\n        >>> # "a photography of a cat with flowers and dai dai daie - daie - daie kasaii"\n        >>> inv_latents = pipeline.invert(caption, image=raw_image).latents\n        >>> # we need to generate source and target embeds\n\n        >>> source_prompts = ["a cat sitting on the street", "a cat playing in the field", "a face of a cat"]\n\n        >>> target_prompts = ["a dog sitting on the street", "a dog playing in the field", "a face of a dog"]\n\n        >>> source_embeds = pipeline.get_embeds(source_prompts)\n        >>> target_embeds = pipeline.get_embeds(target_prompts)\n        >>> # the latents can then be used to edit a real image\n        >>> # when using Stable Diffusion 2 or other models that use v-prediction\n        >>> # set `cross_attention_guidance_amount` to 0.01 or less to avoid input latent gradient explosion\n\n        >>> image = pipeline(\n        ...     caption,\n        ...     source_embeds=source_embeds,\n        ...     target_embeds=target_embeds,\n        ...     num_inference_steps=50,\n        ...     cross_attention_guidance_amount=0.15,\n        ...     generator=generator,\n        ...     latents=inv_latents,\n        ...     negative_prompt=caption,\n        ... ).images[0]\n        >>> image.save("edited_image.png")\n        ```\n'
def preprocess(image):
    deprecation_message = 'The preprocess method is deprecated and will be removed in diffusers 1.0.0. Please use VaeImageProcessor.preprocess(...) instead'
    deprecate('preprocess', '1.0.0', deprecation_message, standard_warn=False)
    if isinstance(image, torch.Tensor): return image
    elif isinstance(image, PIL.Image.Image): image = [image]
    if isinstance(image[0], PIL.Image.Image):
        w, h = image[0].size
        w, h = (x - x % 8 for x in (w, h))
        image = [np.array(i.resize((w, h), resample=PIL_INTERPOLATION['lanczos']))[None, :] for i in image]
        image = np.concatenate(image, axis=0)
        image = np.array(image).astype(np.float32) / 255.0
        image = image.transpose(0, 3, 1, 2)
        image = 2.0 * image - 1.0
        image = torch.from_numpy(image)
    elif isinstance(image[0], torch.Tensor): image = torch.cat(image, dim=0)
    return image
def prepare_unet(unet: UNet2DConditionModel):
    pix2pix_zero_attn_procs = {}
    for name in unet.attn_processors.keys():
        module_name = name.replace('.processor', '')
        module = unet.get_submodule(module_name)
        if 'attn2' in name:
            pix2pix_zero_attn_procs[name] = Pix2PixZeroAttnProcessor(is_pix2pix_zero=True)
            module.requires_grad_(True)
        else:
            pix2pix_zero_attn_procs[name] = Pix2PixZeroAttnProcessor(is_pix2pix_zero=False)
            module.requires_grad_(False)
    unet.set_attn_processor(pix2pix_zero_attn_procs)
    return unet
class Pix2PixZeroL2Loss:
    def __init__(self): self.loss = 0.0
    def compute_loss(self, predictions, targets): self.loss += ((predictions - targets) ** 2).sum((1, 2)).mean(0)
class Pix2PixZeroAttnProcessor:
    def __init__(self, is_pix2pix_zero=False):
        self.is_pix2pix_zero = is_pix2pix_zero
        if self.is_pix2pix_zero: self.reference_cross_attn_map = {}
    def __call__(self, attn: Attention, hidden_states, encoder_hidden_states=None, attention_mask=None, timestep=None, loss=None):
        batch_size, sequence_length, _ = hidden_states.shape
        attention_mask = attn.prepare_attention_mask(attention_mask, sequence_length, batch_size)
        query = attn.to_q(hidden_states)
        if encoder_hidden_states is None: encoder_hidden_states = hidden_states
        elif attn.norm_cross: encoder_hidden_states = attn.norm_encoder_hidden_states(encoder_hidden_states)
        key = attn.to_k(encoder_hidden_states)
        value = attn.to_v(encoder_hidden_states)
        query = attn.head_to_batch_dim(query)
        key = attn.head_to_batch_dim(key)
        value = attn.head_to_batch_dim(value)
        attention_probs = attn.get_attention_scores(query, key, attention_mask)
        if self.is_pix2pix_zero and timestep is not None:
            if loss is None: self.reference_cross_attn_map[timestep.item()] = attention_probs.detach().cpu()
            elif loss is not None:
                prev_attn_probs = self.reference_cross_attn_map.pop(timestep.item())
                loss.compute_loss(attention_probs, prev_attn_probs.to(attention_probs.device))
        hidden_states = torch.bmm(attention_probs, value)
        hidden_states = attn.batch_to_head_dim(hidden_states)
        hidden_states = attn.to_out[0](hidden_states)
        hidden_states = attn.to_out[1](hidden_states)
        return hidden_states
class StableDiffusionPix2PixZeroPipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor', 'caption_generator', 'caption_processor', 'inverse_scheduler']
    _exclude_from_cpu_offload = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: Union[DDPMScheduler, DDIMScheduler,
    EulerAncestralDiscreteScheduler, LMSDiscreteScheduler], feature_extractor: CLIPImageProcessor, safety_checker: StableDiffusionSafetyChecker, inverse_scheduler: DDIMInverseScheduler,
    caption_generator: BlipForConditionalGeneration, caption_processor: BlipProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker,
        feature_extractor=feature_extractor, caption_processor=caption_processor, caption_generator=caption_generator, inverse_scheduler=inverse_scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, **kwargs):
        deprecation_message = '`_encode_prompt()` is deprecated and it will be removed in a future version. Use `encode_prompt()` instead. Also, be aware that the output format changed from a concatenated tensor to a tuple.'
        deprecate('_encode_prompt()', '1.0.0', deprecation_message, standard_warn=False)
        prompt_embeds_tuple = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=lora_scale, **kwargs)
        prompt_embeds = torch.cat([prompt_embeds_tuple[1], prompt_embeds_tuple[0]])
        return prompt_embeds
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = text_inputs.attention_mask.to(device)
            else: attention_mask = None
            if clip_skip is None:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
                prompt_embeds = prompt_embeds[0]
            else:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask, output_hidden_states=True)
                prompt_embeds = prompt_embeds[-1][-(clip_skip + 1)]
                prompt_embeds = self.text_encoder.text_model.final_layer_norm(prompt_embeds)
        if self.text_encoder is not None: prompt_embeds_dtype = self.text_encoder.dtype
        elif self.unet is not None: prompt_embeds_dtype = self.unet.dtype
        else: prompt_embeds_dtype = prompt_embeds.dtype
        prompt_embeds = prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            if isinstance(self, TextualInversionLoaderMixin): uncond_tokens = self.maybe_convert_prompt(uncond_tokens, self.tokenizer)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = uncond_input.attention_mask.to(device)
            else: attention_mask = None
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (prompt_embeds, negative_prompt_embeds)
    def run_safety_checker(self, image, device, dtype):
        if self.safety_checker is None: has_nsfw_concept = None
        else:
            if torch.is_tensor(image): feature_extractor_input = self.image_processor.postprocess(image, output_type='pil')
            else: feature_extractor_input = self.image_processor.numpy_to_pil(image)
            safety_checker_input = self.feature_extractor(feature_extractor_input, return_tensors='pt').to(device)
            image, has_nsfw_concept = self.safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(dtype))
        return (image, has_nsfw_concept)
    def decode_latents(self, latents):
        deprecation_message = 'The decode_latents method is deprecated and will be removed in 1.0.0. Please use VaeImageProcessor.postprocess(...) instead'
        deprecate('decode_latents', '1.0.0', deprecation_message, standard_warn=False)
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.decode(latents, return_dict=False)[0]
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        return image
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, source_embeds, target_embeds, callback_steps, prompt_embeds=None):
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if source_embeds is None and target_embeds is None: raise ValueError('`source_embeds` and `target_embeds` cannot be undefined.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    def generate_caption(self, images):
        text = 'a photography of'
        prev_device = self.caption_generator.device
        device = self._execution_device
        inputs = self.caption_processor(images, text, return_tensors='pt').to(device=device, dtype=self.caption_generator.dtype)
        self.caption_generator.to(device)
        outputs = self.caption_generator.generate(**inputs, max_new_tokens=128)
        self.caption_generator.to(prev_device)
        caption = self.caption_processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return caption
    def construct_direction(self, embs_source: torch.Tensor, embs_target: torch.Tensor): return (embs_target.mean(0) - embs_source.mean(0)).unsqueeze(0)
    @torch.no_grad()
    def get_embeds(self, prompt: List[str], batch_size: int=16) -> torch.Tensor:
        num_prompts = len(prompt)
        embeds = []
        for i in range(0, num_prompts, batch_size):
            prompt_slice = prompt[i:i + batch_size]
            input_ids = self.tokenizer(prompt_slice, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt').input_ids
            input_ids = input_ids.to(self.text_encoder.device)
            embeds.append(self.text_encoder(input_ids)[0])
        return torch.cat(embeds, dim=0).mean(0)[None]
    def prepare_image_latents(self, image, batch_size, dtype, device, generator=None):
        if not isinstance(image, (torch.Tensor, PIL.Image.Image, list)): raise ValueError(f'`image` has to be of type `torch.Tensor`, `PIL.Image.Image` or list but is {type(image)}')
        image = image.to(device=device, dtype=dtype)
        if image.shape[1] == 4: latents = image
        else:
            if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
            if isinstance(generator, list):
                latents = [self.vae.encode(image[i:i + 1]).latent_dist.sample(generator[i]) for i in range(batch_size)]
                latents = torch.cat(latents, dim=0)
            else: latents = self.vae.encode(image).latent_dist.sample(generator)
            latents = self.vae.config.scaling_factor * latents
        if batch_size != latents.shape[0]:
            if batch_size % latents.shape[0] == 0:
                deprecation_message = f'You have passed {batch_size} text prompts (`prompt`), but only {latents.shape[0]} initial images (`image`). Initial images are now duplicating to match the number of text prompts. Note that this behavior is deprecated and will be removed in a version 1.0.0. Please make sure to update your script to pass as many initial images as text prompts to suppress this warning.'
                deprecate('len(prompt) != len(image)', '1.0.0', deprecation_message, standard_warn=False)
                additional_latents_per_image = batch_size // latents.shape[0]
                latents = torch.cat([latents] * additional_latents_per_image, dim=0)
            else: raise ValueError(f'Cannot duplicate `image` of batch size {latents.shape[0]} to {batch_size} text prompts.')
        else: latents = torch.cat([latents], dim=0)
        return latents
    def get_epsilon(self, model_output: torch.Tensor, sample: torch.Tensor, timestep: int):
        pred_type = self.inverse_scheduler.config.prediction_type
        alpha_prod_t = self.inverse_scheduler.alphas_cumprod[timestep]
        beta_prod_t = 1 - alpha_prod_t
        if pred_type == 'epsilon': return model_output
        elif pred_type == 'sample': return (sample - alpha_prod_t ** 0.5 * model_output) / beta_prod_t ** 0.5
        elif pred_type == 'v_prediction': return alpha_prod_t ** 0.5 * model_output + beta_prod_t ** 0.5 * sample
        else: raise ValueError(f'prediction_type given as {pred_type} must be one of `epsilon`, `sample`, or `v_prediction`')
    def auto_corr_loss(self, hidden_states, generator=None):
        reg_loss = 0.0
        for i in range(hidden_states.shape[0]):
            for j in range(hidden_states.shape[1]):
                noise = hidden_states[i:i + 1, j:j + 1, :, :]
                while True:
                    roll_amount = torch.randint(noise.shape[2] // 2, (1,), generator=generator).item()
                    reg_loss += (noise * torch.roll(noise, shifts=roll_amount, dims=2)).mean() ** 2
                    reg_loss += (noise * torch.roll(noise, shifts=roll_amount, dims=3)).mean() ** 2
                    if noise.shape[2] <= 8: break
                    noise = F.avg_pool2d(noise, kernel_size=2)
        return reg_loss
    def kl_divergence(self, hidden_states):
        mean = hidden_states.mean()
        var = hidden_states.var()
        return var + mean ** 2 - 1 - torch.log(var + 1e-07)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, source_embeds: torch.Tensor=None, target_embeds: torch.Tensor=None,
    height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5, negative_prompt: Optional[Union[str,
    List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    cross_attention_guidance_amount: float=0.1, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor],
    None]]=None, callback_steps: Optional[int]=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: Optional[int]=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, source_embeds, target_embeds, callback_steps, prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        latents_init = latents.clone()
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        self.unet = prepare_unet(self.unet)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs={'timestep': t}).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        edit_direction = self.construct_direction(source_embeds, target_embeds).to(prompt_embeds.device)
        prompt_embeds_edit = prompt_embeds.clone()
        prompt_embeds_edit[1:2] += edit_direction
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        latents = latents_init
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                x_in = latent_model_input.detach().clone()
                x_in.requires_grad = True
                opt = torch.optim.SGD([x_in], lr=cross_attention_guidance_amount)
                with torch.enable_grad():
                    loss = Pix2PixZeroL2Loss()
                    noise_pred = self.unet(x_in, t, encoder_hidden_states=prompt_embeds_edit.detach(), cross_attention_kwargs={'timestep': t, 'loss': loss}).sample
                    loss.loss.backward(retain_graph=False)
                    opt.step()
                noise_pred = self.unet(x_in.detach(), t, encoder_hidden_states=prompt_embeds_edit, cross_attention_kwargs={'timestep': None}).sample
                latents = x_in.detach().chunk(2)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, device, prompt_embeds.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        self.maybe_free_model_hooks()
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_INVERT_DOC_STRING)
    def invert(self, prompt: Optional[str]=None, image: PipelineImageInput=None, num_inference_steps: int=50, guidance_scale: float=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    cross_attention_guidance_amount: float=0.1, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None,
    callback_steps: Optional[int]=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, lambda_auto_corr: float=20.0,
    lambda_kl: float=20.0, num_reg_steps: int=5, num_auto_corr_rolls: int=5):
        """Examples:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        image = self.image_processor.preprocess(image)
        latents = self.prepare_image_latents(image, batch_size, self.vae.dtype, device, generator)
        num_images_per_prompt = 1
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, prompt_embeds=prompt_embeds)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.inverse_scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.inverse_scheduler.timesteps
        self.unet = prepare_unet(self.unet)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.inverse_scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.inverse_scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs={'timestep': t}).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                with torch.enable_grad():
                    for _ in range(num_reg_steps):
                        if lambda_auto_corr > 0:
                            for _ in range(num_auto_corr_rolls):
                                var = torch.autograd.Variable(noise_pred.detach().clone(), requires_grad=True)
                                var_epsilon = self.get_epsilon(var, latent_model_input.detach(), t)
                                l_ac = self.auto_corr_loss(var_epsilon, generator=generator)
                                l_ac.backward()
                                grad = var.grad.detach() / num_auto_corr_rolls
                                noise_pred = noise_pred - lambda_auto_corr * grad
                        if lambda_kl > 0:
                            var = torch.autograd.Variable(noise_pred.detach().clone(), requires_grad=True)
                            var_epsilon = self.get_epsilon(var, latent_model_input.detach(), t)
                            l_kld = self.kl_divergence(var_epsilon)
                            l_kld.backward()
                            grad = var.grad.detach()
                            noise_pred = noise_pred - lambda_kl * grad
                        noise_pred = noise_pred.detach()
                latents = self.inverse_scheduler.step(noise_pred, t, latents).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.inverse_scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        inverted_latents = latents.detach().clone()
        image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
        image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (inverted_latents, image)
        return Pix2PixInversionPipelineOutput(latents=inverted_latents, images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
