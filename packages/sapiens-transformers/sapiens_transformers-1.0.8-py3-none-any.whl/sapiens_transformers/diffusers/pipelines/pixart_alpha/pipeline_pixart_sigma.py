'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import html
import inspect
import re
import urllib.parse as ul
from typing import Callable, List, Optional, Tuple, Union
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer
from ...image_processor import PixArtImageProcessor
from ...models import AutoencoderKL, PixArtTransformer2DModel
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import BACKENDS_MAPPING, deprecate, is_bs4_available, is_ftfy_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from .pipeline_pixart_alpha import ASPECT_RATIO_256_BIN, ASPECT_RATIO_512_BIN, ASPECT_RATIO_1024_BIN
if is_bs4_available(): from bs4 import BeautifulSoup
if is_ftfy_available(): import ftfy
ASPECT_RATIO_2048_BIN = {'0.25': [1024.0, 4096.0], '0.26': [1024.0, 3968.0], '0.27': [1024.0, 3840.0], '0.28': [1024.0, 3712.0], '0.32': [1152.0, 3584.0], '0.33': [1152.0, 3456.0],
'0.35': [1152.0, 3328.0], '0.4': [1280.0, 3200.0], '0.42': [1280.0, 3072.0], '0.48': [1408.0, 2944.0], '0.5': [1408.0, 2816.0], '0.52': [1408.0, 2688.0], '0.57': [1536.0, 2688.0],
'0.6': [1536.0, 2560.0], '0.68': [1664.0, 2432.0], '0.72': [1664.0, 2304.0], '0.78': [1792.0, 2304.0], '0.82': [1792.0, 2176.0], '0.88': [1920.0, 2176.0], '0.94': [1920.0, 2048.0],
'1.0': [2048.0, 2048.0], '1.07': [2048.0, 1920.0], '1.13': [2176.0, 1920.0], '1.21': [2176.0, 1792.0], '1.29': [2304.0, 1792.0], '1.38': [2304.0, 1664.0], '1.46': [2432.0, 1664.0],
'1.67': [2560.0, 1536.0], '1.75': [2688.0, 1536.0], '2.0': [2816.0, 1408.0], '2.09': [2944.0, 1408.0], '2.4': [3072.0, 1280.0], '2.5': [3200.0, 1280.0], '2.89': [3328.0, 1152.0],
'3.0': [3456.0, 1152.0], '3.11': [3584.0, 1152.0], '3.62': [3712.0, 1024.0], '3.75': [3840.0, 1024.0], '3.88': [3968.0, 1024.0], '4.0': [4096.0, 1024.0]}
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import PixArtSigmaPipeline\n\n        >>> # You can replace the checkpoint id with "PixArt-alpha/PixArt-Sigma-XL-2-512-MS" too.\n        >>> pipe = PixArtSigmaPipeline.from_pretrained(\n        ...     "PixArt-alpha/PixArt-Sigma-XL-2-1024-MS", torch_dtype=torch.float16\n        ... )\n        >>> # Enable memory optimizations.\n        >>> # pipe.enable_model_cpu_offload()\n\n        >>> prompt = "A small cactus with a happy face in the Sahara desert."\n        >>> image = pipe(prompt).images[0]\n        ```\n'
def retrieve_timesteps(scheduler, num_inference_steps: Optional[int]=None, device: Optional[Union[str, torch.device]]=None, timesteps: Optional[List[int]]=None, sigmas: Optional[List[float]]=None, **kwargs):
    """Returns:"""
    if timesteps is not None and sigmas is not None: raise ValueError('Only one of `timesteps` or `sigmas` can be passed. Please choose one to set custom values')
    if timesteps is not None:
        accepts_timesteps = 'timesteps' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accepts_timesteps: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom timestep schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(timesteps=timesteps, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    elif sigmas is not None:
        accept_sigmas = 'sigmas' in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accept_sigmas: raise ValueError(f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom sigmas schedules. Please check whether you are using the correct scheduler.")
        scheduler.set_timesteps(sigmas=sigmas, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    else:
        scheduler.set_timesteps(num_inference_steps, device=device, **kwargs)
        timesteps = scheduler.timesteps
    return (timesteps, num_inference_steps)
class PixArtSigmaPipeline(DiffusionPipeline):
    bad_punct_regex = re.compile('[' + '#®•©™&@·º½¾¿¡§~' + '\\)' + '\\(' + '\\]' + '\\[' + '\\}' + '\\{' + '\\|' + '\\' + '\\/' + '\\*' + ']{1,}')
    _optional_components = ['tokenizer', 'text_encoder']
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, vae: AutoencoderKL, transformer: PixArtTransformer2DModel, scheduler: KarrasDiffusionSchedulers):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = PixArtImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def encode_prompt(self, prompt: Union[str, List[str]], do_classifier_free_guidance: bool=True, negative_prompt: str='', num_images_per_prompt: int=1, device: Optional[torch.device]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None,
    clean_caption: bool=False, max_sequence_length: int=300, **kwargs):
        """Args:"""
        if 'mask_feature' in kwargs:
            deprecation_message = "The use of `mask_feature` is deprecated. It is no longer used in any computation and that doesn't affect the end results. It will be removed in a future version."
            deprecate('mask_feature', '1.0.0', deprecation_message, standard_warn=False)
        if device is None: device = self._execution_device
        max_length = max_sequence_length
        if prompt_embeds is None:
            prompt = self._text_preprocessing(prompt, clean_caption=clean_caption)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_length, truncation=True, add_special_tokens=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_length - 1:-1])
            prompt_attention_mask = text_inputs.attention_mask
            prompt_attention_mask = prompt_attention_mask.to(device)
            prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=prompt_attention_mask)
            prompt_embeds = prompt_embeds[0]
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        elif self.transformer is not None: dtype = self.transformer.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(1, num_images_per_prompt)
        prompt_attention_mask = prompt_attention_mask.view(bs_embed * num_images_per_prompt, -1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens = [negative_prompt] * bs_embed if isinstance(negative_prompt, str) else negative_prompt
            uncond_tokens = self._text_preprocessing(uncond_tokens, clean_caption=clean_caption)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            negative_prompt_attention_mask = uncond_input.attention_mask
            negative_prompt_attention_mask = negative_prompt_attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=negative_prompt_attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.repeat(1, num_images_per_prompt)
            negative_prompt_attention_mask = negative_prompt_attention_mask.view(bs_embed * num_images_per_prompt, -1)
        else:
            negative_prompt_embeds = None
            negative_prompt_attention_mask = None
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, negative_prompt, callback_steps, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and prompt_attention_mask is None: raise ValueError('Must provide `prompt_attention_mask` when specifying `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_prompt_attention_mask is None: raise ValueError('Must provide `negative_prompt_attention_mask` when specifying `negative_prompt_embeds`.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if prompt_attention_mask.shape != negative_prompt_attention_mask.shape: raise ValueError(f'`prompt_attention_mask` and `negative_prompt_attention_mask` must have the same shape when passed directly, but got: `prompt_attention_mask` {prompt_attention_mask.shape} != `negative_prompt_attention_mask` {negative_prompt_attention_mask.shape}.')
    def _text_preprocessing(self, text, clean_caption=False):
        if clean_caption and (not is_bs4_available()): clean_caption = False
        if clean_caption and (not is_ftfy_available()): clean_caption = False
        if not isinstance(text, (tuple, list)): text = [text]
        def process(text: str):
            if clean_caption:
                text = self._clean_caption(text)
                text = self._clean_caption(text)
            else: text = text.lower().strip()
            return text
        return [process(t) for t in text]
    def _clean_caption(self, caption):
        caption = str(caption)
        caption = ul.unquote_plus(caption)
        caption = caption.strip().lower()
        caption = re.sub('<person>', 'person', caption)
        caption = re.sub('\\b((?:https?:(?:\\/{1,3}|[a-zA-Z0-9%])|[a-zA-Z0-9.\\-]+[.](?:com|co|ru|net|org|edu|gov|it)[\\w/-]*\\b\\/?(?!@)))', '', caption)
        caption = re.sub('\\b((?:www:(?:\\/{1,3}|[a-zA-Z0-9%])|[a-zA-Z0-9.\\-]+[.](?:com|co|ru|net|org|edu|gov|it)[\\w/-]*\\b\\/?(?!@)))', '', caption)
        caption = BeautifulSoup(caption, features='html.parser').text
        caption = re.sub('@[\\w\\d]+\\b', '', caption)
        caption = re.sub('[\\u31c0-\\u31ef]+', '', caption)
        caption = re.sub('[\\u31f0-\\u31ff]+', '', caption)
        caption = re.sub('[\\u3200-\\u32ff]+', '', caption)
        caption = re.sub('[\\u3300-\\u33ff]+', '', caption)
        caption = re.sub('[\\u3400-\\u4dbf]+', '', caption)
        caption = re.sub('[\\u4dc0-\\u4dff]+', '', caption)
        caption = re.sub('[\\u4e00-\\u9fff]+', '', caption)
        caption = re.sub('[\\u002D\\u058A\\u05BE\\u1400\\u1806\\u2010-\\u2015\\u2E17\\u2E1A\\u2E3A\\u2E3B\\u2E40\\u301C\\u3030\\u30A0\\uFE31\\uFE32\\uFE58\\uFE63\\uFF0D]+', '-', caption)
        caption = re.sub('[`´«»“”¨]', '"', caption)
        caption = re.sub('[‘’]', "'", caption)
        caption = re.sub('&quot;?', '', caption)
        caption = re.sub('&amp', '', caption)
        caption = re.sub('\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}', ' ', caption)
        caption = re.sub('\\d:\\d\\d\\s+$', '', caption)
        caption = re.sub('\\\\n', ' ', caption)
        caption = re.sub('#\\d{1,3}\\b', '', caption)
        caption = re.sub('#\\d{5,}\\b', '', caption)
        caption = re.sub('\\b\\d{6,}\\b', '', caption)
        caption = re.sub('[\\S]+\\.(?:png|jpg|jpeg|bmp|webp|eps|pdf|apk|mp4)', '', caption)
        caption = re.sub('[\\"\\\']{2,}', '"', caption)
        caption = re.sub('[\\.]{2,}', ' ', caption)
        caption = re.sub(self.bad_punct_regex, ' ', caption)
        caption = re.sub('\\s+\\.\\s+', ' ', caption)
        regex2 = re.compile('(?:\\-|\\_)')
        if len(re.findall(regex2, caption)) > 3: caption = re.sub(regex2, ' ', caption)
        caption = ftfy.fix_text(caption)
        caption = html.unescape(html.unescape(caption))
        caption = re.sub('\\b[a-zA-Z]{1,3}\\d{3,15}\\b', '', caption)
        caption = re.sub('\\b[a-zA-Z]+\\d+[a-zA-Z]+\\b', '', caption)
        caption = re.sub('\\b\\d+[a-zA-Z]+\\d+\\b', '', caption)
        caption = re.sub('(worldwide\\s+)?(free\\s+)?shipping', '', caption)
        caption = re.sub('(free\\s)?download(\\sfree)?', '', caption)
        caption = re.sub('\\bclick\\b\\s(?:for|on)\\s\\w+', '', caption)
        caption = re.sub('\\b(?:png|jpg|jpeg|bmp|webp|eps|pdf|apk|mp4)(\\simage[s]?)?', '', caption)
        caption = re.sub('\\bpage\\s+\\d+\\b', '', caption)
        caption = re.sub('\\b\\d*[a-zA-Z]+\\d+[a-zA-Z]+\\d+[a-zA-Z\\d]*\\b', ' ', caption)
        caption = re.sub('\\b\\d+\\.?\\d*[xх×]\\d+\\.?\\d*\\b', '', caption)
        caption = re.sub('\\b\\s+\\:\\s+', ': ', caption)
        caption = re.sub('(\\D[,\\./])\\b', '\\1 ', caption)
        caption = re.sub('\\s+', ' ', caption)
        caption.strip()
        caption = re.sub('^[\\"\\\']([\\w\\W]+)[\\"\\\']$', '\\1', caption)
        caption = re.sub("^[\\'\\_,\\-\\:;]", '', caption)
        caption = re.sub("[\\'\\_,\\-\\:\\-\\+]$", '', caption)
        caption = re.sub('^\\.\\S+$', '', caption)
        return caption.strip()
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, negative_prompt: str='', num_inference_steps: int=20, timesteps: List[int]=None, sigmas: List[float]=None, guidance_scale: float=4.5,
    num_images_per_prompt: Optional[int]=1, height: Optional[int]=None, width: Optional[int]=None, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None,
    callback_steps: int=1, clean_caption: bool=True, use_resolution_binning: bool=True, max_sequence_length: int=300, **kwargs) -> Union[ImagePipelineOutput, Tuple]:
        """Examples:"""
        height = height or self.transformer.config.sample_size * self.vae_scale_factor
        width = width or self.transformer.config.sample_size * self.vae_scale_factor
        if use_resolution_binning:
            if self.transformer.config.sample_size == 256: aspect_ratio_bin = ASPECT_RATIO_2048_BIN
            elif self.transformer.config.sample_size == 128: aspect_ratio_bin = ASPECT_RATIO_1024_BIN
            elif self.transformer.config.sample_size == 64: aspect_ratio_bin = ASPECT_RATIO_512_BIN
            elif self.transformer.config.sample_size == 32: aspect_ratio_bin = ASPECT_RATIO_256_BIN
            else: raise ValueError('Invalid sample size')
            orig_height, orig_width = (height, width)
            height, width = self.image_processor.classify_height_width_bin(height, width, ratios=aspect_ratio_bin)
        self.check_inputs(prompt, height, width, negative_prompt, callback_steps, prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask = self.encode_prompt(prompt, do_classifier_free_guidance, negative_prompt=negative_prompt,
        num_images_per_prompt=num_images_per_prompt, device=device, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, prompt_attention_mask=prompt_attention_mask,
        negative_prompt_attention_mask=negative_prompt_attention_mask, clean_caption=clean_caption, max_sequence_length=max_sequence_length)
        if do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            prompt_attention_mask = torch.cat([negative_prompt_attention_mask, prompt_attention_mask], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        added_cond_kwargs = {'resolution': None, 'aspect_ratio': None}
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                current_timestep = t
                if not torch.is_tensor(current_timestep):
                    is_mps = latent_model_input.device.type == 'mps'
                    if isinstance(current_timestep, float): dtype = torch.float32 if is_mps else torch.float64
                    else: dtype = torch.int32 if is_mps else torch.int64
                    current_timestep = torch.tensor([current_timestep], dtype=dtype, device=latent_model_input.device)
                elif len(current_timestep.shape) == 0: current_timestep = current_timestep[None].to(latent_model_input.device)
                current_timestep = current_timestep.expand(latent_model_input.shape[0])
                noise_pred = self.transformer(latent_model_input, encoder_hidden_states=prompt_embeds, encoder_attention_mask=prompt_attention_mask, timestep=current_timestep,
                added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.transformer.config.out_channels // 2 == latent_channels: noise_pred = noise_pred.chunk(2, dim=1)[0]
                else: noise_pred = noise_pred
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            if use_resolution_binning: image = self.image_processor.resize_and_crop_tensor(image, orig_width, orig_height)
        else: image = latents
        if not output_type == 'latent': image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
