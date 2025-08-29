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
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...models import AutoencoderKL, LatteTransformer3DModel
from ...pipelines.pipeline_utils import DiffusionPipeline
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import BACKENDS_MAPPING, BaseOutput, is_bs4_available, is_ftfy_available, replace_example_docstring
from ...utils.torch_utils import is_compiled_module, randn_tensor
from ...video_processor import VideoProcessor
if is_bs4_available(): from bs4 import BeautifulSoup
if is_ftfy_available(): import ftfy
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import LattePipeline\n        >>> from sapiens_transformers.diffusers.utils import export_to_gif\n\n        >>> # You can replace the checkpoint id with "maxin-cn/Latte-1" too.\n        >>> pipe = LattePipeline.from_pretrained("maxin-cn/Latte-1", torch_dtype=torch.float16)\n        >>> # Enable memory optimizations.\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> prompt = "A small cactus with a happy face in the Sahara desert."\n        >>> videos = pipe(prompt).frames[0]\n        >>> export_to_gif(videos, "latte.gif")\n        ```\n'
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
@dataclass
class LattePipelineOutput(BaseOutput):
    frames: torch.Tensor
class LattePipeline(DiffusionPipeline):
    """Args:"""
    bad_punct_regex = re.compile('[#®•©™&@·º½¾¿¡§~\\)\\(\\]\\[\\}\\{\\|\\\\/\\\\*]{1,}')
    _optional_components = ['tokenizer', 'text_encoder']
    model_cpu_offload_seq = 'text_encoder->transformer->vae'
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    def __init__(self, tokenizer: T5Tokenizer, text_encoder: T5EncoderModel, vae: AutoencoderKL, transformer: LatteTransformer3DModel, scheduler: KarrasDiffusionSchedulers):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, transformer=transformer, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_scale_factor)
    def mask_text_embeddings(self, emb, mask):
        if emb.shape[0] == 1:
            keep_index = mask.sum().item()
            return (emb[:, :, :keep_index, :], keep_index)
        else:
            masked_feature = emb * mask[:, None, :, None]
            return (masked_feature, emb.shape[2])
    def encode_prompt(self, prompt: Union[str, List[str]], do_classifier_free_guidance: bool=True, negative_prompt: str='', num_images_per_prompt: int=1, device: Optional[torch.device]=None,
    prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None, clean_caption: bool=False, mask_feature: bool=True, dtype=None):
        """Args:"""
        embeds_initially_provided = prompt_embeds is not None and negative_prompt_embeds is not None
        if device is None: device = self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        max_length = 120
        if prompt_embeds is None:
            prompt = self._text_preprocessing(prompt, clean_caption=clean_caption)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=max_length, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, max_length - 1:-1])
            attention_mask = text_inputs.attention_mask.to(device)
            prompt_embeds_attention_mask = attention_mask
            prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
            prompt_embeds = prompt_embeds[0]
        else: prompt_embeds_attention_mask = torch.ones_like(prompt_embeds)
        if self.text_encoder is not None: dtype = self.text_encoder.dtype
        elif self.transformer is not None: dtype = self.transformer.dtype
        else: dtype = None
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        prompt_embeds_attention_mask = prompt_embeds_attention_mask.view(bs_embed, -1)
        prompt_embeds_attention_mask = prompt_embeds_attention_mask.repeat(num_images_per_prompt, 1)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens = [negative_prompt] * batch_size if isinstance(negative_prompt, str) else negative_prompt
            uncond_tokens = self._text_preprocessing(uncond_tokens, clean_caption=clean_caption)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_attention_mask=True, add_special_tokens=True, return_tensors='pt')
            attention_mask = uncond_input.attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        else: negative_prompt_embeds = None
        if mask_feature and (not embeds_initially_provided):
            prompt_embeds = prompt_embeds.unsqueeze(1)
            masked_prompt_embeds, keep_indices = self.mask_text_embeddings(prompt_embeds, prompt_embeds_attention_mask)
            masked_prompt_embeds = masked_prompt_embeds.squeeze(1)
            masked_negative_prompt_embeds = negative_prompt_embeds[:, :keep_indices, :] if negative_prompt_embeds is not None else None
            return (masked_prompt_embeds, masked_negative_prompt_embeds)
        return (prompt_embeds, negative_prompt_embeds)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, negative_prompt, callback_on_step_end_tensor_inputs, prompt_embeds=None, negative_prompt_embeds=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
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
    def prepare_latents(self, batch_size, num_channels_latents, num_frames, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, num_frames, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, negative_prompt: str='', num_inference_steps: int=50, timesteps: Optional[List[int]]=None, guidance_scale: float=7.5, num_images_per_prompt: int=1,
    video_length: int=16, height: int=512, width: int=512, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.FloatTensor]=None,
    prompt_embeds: Optional[torch.FloatTensor]=None, negative_prompt_embeds: Optional[torch.FloatTensor]=None, output_type: str='pil', return_dict: bool=True, callback_on_step_end: Optional[Union[Callable[[int,
    int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], clean_caption: bool=True, mask_feature: bool=True,
    enable_temporal_attentions: bool=True, decode_chunk_size: Optional[int]=None) -> Union[LattePipelineOutput, Tuple]:
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        decode_chunk_size = decode_chunk_size if decode_chunk_size is not None else video_length
        height = height or self.transformer.config.sample_size * self.vae_scale_factor
        width = width or self.transformer.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, negative_prompt, callback_on_step_end_tensor_inputs, prompt_embeds, negative_prompt_embeds)
        self._guidance_scale = guidance_scale
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, do_classifier_free_guidance, negative_prompt=negative_prompt, num_images_per_prompt=num_images_per_prompt,
        device=device, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clean_caption=clean_caption, mask_feature=mask_feature)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps)
        self._num_timesteps = len(timesteps)
        latent_channels = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, latent_channels, video_length, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
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
                noise_pred = self.transformer(latent_model_input, encoder_hidden_states=prompt_embeds, timestep=current_timestep, enable_temporal_attentions=enable_temporal_attentions, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if not (hasattr(self.scheduler.config, 'variance_type') and self.scheduler.config.variance_type in ['learned', 'learned_range']): noise_pred = noise_pred.chunk(2, dim=1)[0]
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latents':
            video = self.decode_latents(latents, video_length, decode_chunk_size=14)
            video = self.video_processor.postprocess_video(video=video, output_type=output_type)
        else: video = latents
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return LattePipelineOutput(frames=video)
    def decode_latents(self, latents: torch.Tensor, video_length: int, decode_chunk_size: int=14):
        latents = latents.permute(0, 2, 1, 3, 4).flatten(0, 1)
        latents = 1 / self.vae.config.scaling_factor * latents
        forward_vae_fn = self.vae._orig_mod.forward if is_compiled_module(self.vae) else self.vae.forward
        accepts_num_frames = 'num_frames' in set(inspect.signature(forward_vae_fn).parameters.keys())
        frames = []
        for i in range(0, latents.shape[0], decode_chunk_size):
            num_frames_in = latents[i:i + decode_chunk_size].shape[0]
            decode_kwargs = {}
            if accepts_num_frames: decode_kwargs['num_frames'] = num_frames_in
            frame = self.vae.decode(latents[i:i + decode_chunk_size], **decode_kwargs).sample
            frames.append(frame)
        frames = torch.cat(frames, dim=0)
        frames = frames.reshape(-1, video_length, *frames.shape[1:]).permute(0, 2, 1, 3, 4)
        frames = frames.float()
        return frames
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
