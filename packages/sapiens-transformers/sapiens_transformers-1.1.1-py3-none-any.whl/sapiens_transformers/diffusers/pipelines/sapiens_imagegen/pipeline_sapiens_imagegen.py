'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils import BACKENDS_MAPPING, USE_PEFT_BACKEND, is_bs4_available, is_ftfy_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ..pixart_alpha.pipeline_pixart_alpha import ASPECT_RATIO_512_BIN, ASPECT_RATIO_1024_BIN
from ..pixart_alpha.pipeline_pixart_sigma import ASPECT_RATIO_2048_BIN
from ...models import AutoencoderDC, SapiensImageGenTransformer2DModel
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer
from .pipeline_output import SapiensImageGenPipelineOutput
from ...loaders import SapiensImageGenLoraLoaderMixin
from ...schedulers import DPMSolverMultistepScheduler
from ...image_processor import PixArtImageProcessor
from ..pipeline_utils import DiffusionPipeline
from ...utils.torch_utils import randn_tensor
import urllib.parse as ul
import inspect
import torch
import html
import re
if is_bs4_available(): from bs4 import BeautifulSoup
if is_ftfy_available(): import ftfy
EXAMPLE_DOC_STRING = ''
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
class SapiensImageGenPipeline(DiffusionPipeline, SapiensImageGenLoraLoaderMixin):
    bad_punct_regex = re.compile('[' + '#®•©™&@·º½¾¿¡§~' + '\\)' + '\\(' + '\\]' + '\\[' + '\\}' + '\\{' + '\\|' + '\\' + '\\/' + '\\*' + ']{1,}')
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, tokenizer: AutoTokenizer, text_encoder: AutoModelForCausalLM, vae: AutoencoderDC, transformer: SapiensImageGenTransformer2DModel, scheduler: DPMSolverMultistepScheduler):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.encoder_block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 32
        self.image_processor = PixArtImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def encode_prompt(self, prompt: Union[str, List[str]], do_classifier_free_guidance: bool=True, negative_prompt: str='', num_images_per_prompt: int=1, device: Optional[torch.device]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask: Optional[torch.Tensor]=None, clean_caption: bool=False, max_sequence_length: int=300,
    complex_human_instruction: Optional[List[str]]=None, lora_scale: Optional[float]=None):
        """Args:"""
        if device is None: device = self._execution_device
        if lora_scale is not None and isinstance(self, SapiensImageGenLoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None and USE_PEFT_BACKEND: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        self.tokenizer.padding_side = 'right'
        max_length = max_sequence_length
        select_index = [0] + list(range(-max_length + 1, 0))
        if prompt_embeds is None:
            prompt = self._text_preprocessing(prompt, clean_caption=clean_caption)
            if not complex_human_instruction: max_length_all = max_length
            else:
                chi_prompt = '\n'.join(complex_human_instruction)
                prompt = [chi_prompt + p for p in prompt]
                num_chi_prompt_tokens = len(self.tokenizer.encode(chi_prompt))
                max_length_all = num_chi_prompt_tokens + max_length - 2
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_length_all, truncation=True, add_special_tokens=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            prompt_attention_mask = text_inputs.attention_mask
            prompt_attention_mask = prompt_attention_mask.to(device)
            prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=prompt_attention_mask)
            prompt_embeds = prompt_embeds[0][:, select_index]
            prompt_attention_mask = prompt_attention_mask[:, select_index]
        if self.transformer is not None: dtype = self.transformer.dtype
        elif self.text_encoder is not None: dtype = self.text_encoder.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.view(bs_embed, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(num_images_per_prompt, 1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens = [negative_prompt] * batch_size if isinstance(negative_prompt, str) else negative_prompt
            uncond_tokens = self._text_preprocessing(uncond_tokens, clean_caption=clean_caption)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True,
            return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            negative_prompt_attention_mask = uncond_input.attention_mask
            negative_prompt_attention_mask = negative_prompt_attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=negative_prompt_attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.view(bs_embed, -1)
            negative_prompt_attention_mask = negative_prompt_attention_mask.repeat(num_images_per_prompt, 1)
        else:
            negative_prompt_embeds = None
            negative_prompt_attention_mask = None
        if self.text_encoder is not None:
            if isinstance(self, SapiensImageGenLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, callback_on_step_end_tensor_inputs=None, negative_prompt=None, prompt_embeds=None,
    negative_prompt_embeds=None, prompt_attention_mask=None, negative_prompt_attention_mask=None):
        if height % 32 != 0 or width % 32 != 0: raise ValueError(f'`height` and `width` have to be divisible by 32 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
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
        if latents is not None: return latents.to(device=device, dtype=dtype)
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def attention_kwargs(self): return self._attention_kwargs
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1.0
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, negative_prompt: str='', num_inference_steps: int=20, timesteps: List[int]=None,
    sigmas: List[float]=None, guidance_scale: float=4.5, num_images_per_prompt: Optional[int]=1, height: int=1024, width: int=1024, eta: float=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, clean_caption: bool=True, use_resolution_binning: bool=True, attention_kwargs: Optional[Dict[str, Any]]=None,
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], max_sequence_length: int=300,
    complex_human_instruction: List[str]=["Given a user prompt, generate an 'Enhanced prompt' that provides detailed visual descriptions suitable for image generation. Evaluate the level of detail in the user prompt:", '- If the prompt is simple, focus on adding specifics about colors, shapes, sizes, textures, and spatial relationships to create vivid and concrete scenes.', '- If the prompt is already detailed, refine and enhance the existing details slightly without overcomplicating.', 'Here are examples of how to transform or refine prompts:', '- User Prompt: A cat sleeping -> Enhanced: A small, fluffy white cat curled up in a round shape, sleeping peacefully on a warm sunny windowsill, surrounded by pots of blooming red flowers.', '- User Prompt: A busy city street -> Enhanced: A bustling city street scene at dusk, featuring glowing street lamps, a diverse crowd of people in colorful clothing, and a double-decker bus passing by towering glass skyscrapers.', 'Please generate only the enhanced description for the prompt below and avoid including any additional commentary or evaluations:', 'User Prompt: ']) -> Union[SapiensImageGenPipelineOutput, Tuple]:
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        if use_resolution_binning:
            if self.transformer.config.sample_size == 64: aspect_ratio_bin = ASPECT_RATIO_2048_BIN
            elif self.transformer.config.sample_size == 32: aspect_ratio_bin = ASPECT_RATIO_1024_BIN
            elif self.transformer.config.sample_size == 16: aspect_ratio_bin = ASPECT_RATIO_512_BIN
            else: raise ValueError('Invalid sample size')
            orig_height, orig_width = (height, width)
            height, width = self.image_processor.classify_height_width_bin(height, width, ratios=aspect_ratio_bin)
        self.check_inputs(prompt, height, width, callback_on_step_end_tensor_inputs, negative_prompt, prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask)
        self._guidance_scale = guidance_scale
        self._attention_kwargs = attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        lora_scale = self.attention_kwargs.get('scale', None) if self.attention_kwargs is not None else None
        prompt_embeds, prompt_attention_mask, negative_prompt_embeds, negative_prompt_attention_mask = self.encode_prompt(prompt, self.do_classifier_free_guidance,
        negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt, device=device, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        prompt_attention_mask=prompt_attention_mask, negative_prompt_attention_mask=negative_prompt_attention_mask, clean_caption=clean_caption,
        max_sequence_length=max_sequence_length, complex_human_instruction=complex_human_instruction, lora_scale=lora_scale)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            prompt_attention_mask = torch.cat([negative_prompt_attention_mask, prompt_attention_mask], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, height, width, torch.float32, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = latent_model_input.to(prompt_embeds.dtype)
                timestep = t.expand(latent_model_input.shape[0]).to(latents.dtype)
                noise_pred = self.transformer(latent_model_input, encoder_hidden_states=prompt_embeds, encoder_attention_mask=prompt_attention_mask,
                timestep=timestep, return_dict=False, attention_kwargs=self.attention_kwargs)[0]
                noise_pred = noise_pred.float()
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.transformer.config.out_channels // 2 == latent_channels: noise_pred = noise_pred.chunk(2, dim=1)[0]
                else: noise_pred = noise_pred
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if output_type == 'latent': image = latents
        else:
            latents = latents.to(self.vae.dtype)
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            if use_resolution_binning: image = self.image_processor.resize_and_crop_tensor(image, orig_width, orig_height)
        if not output_type == 'latent': image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return SapiensImageGenPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
