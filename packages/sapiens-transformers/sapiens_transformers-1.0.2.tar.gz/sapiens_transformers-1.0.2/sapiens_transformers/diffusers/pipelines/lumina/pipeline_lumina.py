'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import html
import inspect
import math
import re
import urllib.parse as ul
from typing import List, Optional, Tuple, Union
import torch
from sapiens_transformers import AutoModel, AutoTokenizer
from ...image_processor import VaeImageProcessor
from ...models import AutoencoderKL
from ...models.embeddings import get_2d_rotary_pos_embed_lumina
from ...models.sapiens_transformers.lumina_nextdit2d import LuminaNextDiT2DModel
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import BACKENDS_MAPPING, is_bs4_available, is_ftfy_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
if is_bs4_available(): from bs4 import BeautifulSoup
if is_ftfy_available(): import ftfy
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import LuminaText2ImgPipeline\n\n        >>> pipe = LuminaText2ImgPipeline.from_pretrained(\n        ...     "Alpha-VLLM/Lumina-Next-SFT-diffusers", torch_dtype=torch.bfloat16\n        ... )\n        >>> # Enable memory optimizations.\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> prompt = "Upper body of a young woman in a Victorian-era outfit with brass goggles and leather straps. Background shows an industrial revolution cityscape with smoky skies and tall, metal structures"\n        >>> image = pipe(prompt).images[0]\n        ```\n'
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
class LuminaText2ImgPipeline(DiffusionPipeline):
    """Args:"""
    bad_punct_regex = re.compile('[' + '#®•©™&@·º½¾¿¡§~' + '\\)' + '\\(' + '\\]' + '\\[' + '\\}' + '\\{' + '\\|' + '\\' + '\\/' + '\\*' + ']{1,}')
    _optional_components = []
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    def __init__(self, transformer: LuminaNextDiT2DModel, scheduler: FlowMatchEulerDiscreteScheduler, vae: AutoencoderKL, text_encoder: AutoModel, tokenizer: AutoTokenizer):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.max_sequence_length = 256
        self.default_sample_size = self.transformer.config.sample_size if hasattr(self, 'transformer') and self.transformer is not None else 128
        self.default_image_size = self.default_sample_size * self.vae_scale_factor
    def _get_gemma_prompt_embeds(self, prompt: Union[str, List[str]], num_images_per_prompt: int=1, device: Optional[torch.device]=None, clean_caption: Optional[bool]=False, max_length: Optional[int]=None):
        device = device or self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        prompt = self._text_preprocessing(prompt, clean_caption=clean_caption)
        text_inputs = self.tokenizer(prompt, pad_to_multiple_of=8, max_length=self.max_sequence_length, truncation=True, padding=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids.to(device)
        untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids.to(device)
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.max_sequence_length - 1:-1])
        prompt_attention_mask = text_inputs.attention_mask.to(device)
        prompt_embeds = self.text_encoder(text_input_ids, attention_mask=prompt_attention_mask, output_hidden_states=True)
        prompt_embeds = prompt_embeds.hidden_states[-2]
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        elif self.transformer is not None: dtype = self.transformer.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(num_images_per_prompt, 1)
        prompt_attention_mask = prompt_attention_mask.view(batch_size * num_images_per_prompt, -1)
        return (prompt_embeds, prompt_attention_mask)
    def encode_prompt(self, prompt: Union[str, List[str]], do_classifier_free_guidance: bool=True, negative_prompt: Union[str, List[str]]=None, num_images_per_prompt: int=1,
    device: Optional[torch.device]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, clean_caption: bool=False, **kwargs):
        """Args:"""
        if device is None: device = self._execution_device
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None: prompt_embeds, prompt_attention_mask = self._get_gemma_prompt_embeds(prompt=prompt, num_images_per_prompt=num_images_per_prompt, device=device, clean_caption=clean_caption)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt if negative_prompt is not None else ''
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): negative_prompt = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            prompt_max_length = prompt_embeds.shape[1]
            negative_text_inputs = self.tokenizer(negative_prompt, padding='max_length', max_length=prompt_max_length, truncation=True, return_tensors='pt')
            negative_text_input_ids = negative_text_inputs.input_ids.to(device)
            negative_prompt_attention_mask = negative_text_inputs.attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(negative_text_input_ids, attention_mask=negative_prompt_attention_mask, output_hidden_states=True)
            negative_dtype = self.text_encoder.dtype
            negative_prompt_embeds = negative_prompt_embeds.hidden_states[-2]
            _, seq_len, _ = negative_prompt_embeds.shape
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=negative_dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.repeat(num_images_per_prompt, 1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.view(batch_size * num_images_per_prompt, -1)
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, negative_prompt, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
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
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, width: Optional[int]=None, height: Optional[int]=None, num_inference_steps: int=30, guidance_scale: float=4.0,
    negative_prompt: Union[str, List[str]]=None, sigmas: List[float]=None, num_images_per_prompt: Optional[int]=1, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    clean_caption: bool=True, max_sequence_length: int=256, scaling_watershed: Optional[float]=1.0, proportional_attn: Optional[bool]=True) -> Union[ImagePipelineOutput, Tuple]:
        """Examples:"""
        height = height or self.default_sample_size * self.vae_scale_factor
        width = width or self.default_sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask)
        cross_attention_kwargs = {}
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if proportional_attn: cross_attention_kwargs['base_sequence_length'] = (self.default_image_size // 16) ** 2
        scaling_factor = math.sqrt(width * height / self.default_image_size ** 2)
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask = self.encode_prompt(prompt, do_classifier_free_guidance,
        negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, device=device, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask, clean_caption=clean_caption, max_sequence_length=max_sequence_length)
        if do_classifier_free_guidance:
            prompt_embeds = torch.cat([prompt_embeds, negative_prompt_embeds], dim=0)
            prompt_attention_mask = torch.cat([prompt_attention_mask, negative_prompt_attention_mask], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, sigmas=sigmas)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, height, width, prompt_embeds.dtype, device, generator, latents)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                current_timestep = t
                if not torch.is_tensor(current_timestep):
                    is_mps = latent_model_input.device.type == 'mps'
                    if isinstance(current_timestep, float): dtype = torch.float32 if is_mps else torch.float64
                    else: dtype = torch.int32 if is_mps else torch.int64
                    current_timestep = torch.tensor([current_timestep], dtype=dtype, device=latent_model_input.device)
                elif len(current_timestep.shape) == 0: current_timestep = current_timestep[None].to(latent_model_input.device)
                current_timestep = current_timestep.expand(latent_model_input.shape[0])
                current_timestep = 1 - current_timestep / self.scheduler.config.num_train_timesteps
                if current_timestep[0] < scaling_watershed:
                    linear_factor = scaling_factor
                    ntk_factor = 1.0
                else:
                    linear_factor = 1.0
                    ntk_factor = scaling_factor
                image_rotary_emb = get_2d_rotary_pos_embed_lumina(self.transformer.head_dim, 384, 384, linear_factor=linear_factor, ntk_factor=ntk_factor)
                noise_pred = self.transformer(hidden_states=latent_model_input, timestep=current_timestep, encoder_hidden_states=prompt_embeds, encoder_mask=prompt_attention_mask,
                image_rotary_emb=image_rotary_emb, cross_attention_kwargs=cross_attention_kwargs, return_dict=False)[0]
                noise_pred = noise_pred.chunk(2, dim=1)[0]
                if do_classifier_free_guidance:
                    noise_pred_eps, noise_pred_rest = (noise_pred[:, :3], noise_pred[:, 3:])
                    noise_pred_cond_eps, noise_pred_uncond_eps = torch.split(noise_pred_eps, len(noise_pred_eps) // 2, dim=0)
                    noise_pred_half = noise_pred_uncond_eps + guidance_scale * (noise_pred_cond_eps - noise_pred_uncond_eps)
                    noise_pred_eps = torch.cat([noise_pred_half, noise_pred_half], dim=0)
                    noise_pred = torch.cat([noise_pred_eps, noise_pred_rest], dim=1)
                    noise_pred, _ = noise_pred.chunk(2, dim=0)
                latents_dtype = latents.dtype
                noise_pred = -noise_pred
                latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                if latents.dtype != latents_dtype:
                    if torch.backends.mps.is_available(): latents = latents.to(latents_dtype)
                progress_bar.update()
        if not output_type == 'latent':
            latents = latents / self.vae.config.scaling_factor
            image = self.vae.decode(latents, return_dict=False)[0]
            image = self.image_processor.postprocess(image, output_type=output_type)
        else: image = latents
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
