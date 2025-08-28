'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from sapiens_transformers import BertModel, BertTokenizer, CLIPImageProcessor, MT5Tokenizer, T5EncoderModel
from ...pipelines.stable_diffusion import StableDiffusionPipelineOutput
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import VaeImageProcessor
from ...models import AutoencoderKL, HunyuanDiT2DModel
from ...models.attention_processor import PAGCFGHunyuanAttnProcessor2_0, PAGHunyuanAttnProcessor2_0
from ...models.embeddings import get_2d_rotary_pos_embed
from ...pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from ...schedulers import DDPMScheduler
from ...utils import is_torch_xla_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .pag_utils import PAGMixin
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```python\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AutoPipelineForText2Image\n\n        >>> pipe = AutoPipelineForText2Image.from_pretrained(\n        ...     "Tencent-Hunyuan/HunyuanDiT-v1.2-Diffusers",\n        ...     torch_dtype=torch.float16,\n        ...     enable_pag=True,\n        ...     pag_applied_layers=[14],\n        ... ).to("cuda")\n\n        >>> # prompt = "an astronaut riding a horse"\n        >>> prompt = "一个宇航员在骑马"\n        >>> image = pipe(prompt, guidance_scale=4, pag_scale=3).images[0]\n        ```\n'
STANDARD_RATIO = np.array([1.0, 4.0 / 3.0, 3.0 / 4.0, 16.0 / 9.0, 9.0 / 16.0])
STANDARD_SHAPE = [[(1024, 1024), (1280, 1280)], [(1024, 768), (1152, 864), (1280, 960)], [(768, 1024), (864, 1152), (960, 1280)], [(1280, 768)], [(768, 1280)]]
STANDARD_AREA = [np.array([w * h for w, h in shapes]) for shapes in STANDARD_SHAPE]
SUPPORTED_SHAPE = [(1024, 1024), (1280, 1280), (1024, 768), (1152, 864), (1280, 960), (768, 1024), (864, 1152), (960, 1280), (1280, 768), (768, 1280)]
def map_to_standard_shapes(target_width, target_height):
    target_ratio = target_width / target_height
    closest_ratio_idx = np.argmin(np.abs(STANDARD_RATIO - target_ratio))
    closest_area_idx = np.argmin(np.abs(STANDARD_AREA[closest_ratio_idx] - target_width * target_height))
    width, height = STANDARD_SHAPE[closest_ratio_idx][closest_area_idx]
    return (width, height)
def get_resize_crop_region_for_grid(src, tgt_size):
    th = tw = tgt_size
    h, w = src
    r = h / w
    if r > 1:
        resize_height = th
        resize_width = int(round(th / h * w))
    else:
        resize_width = tw
        resize_height = int(round(tw / w * h))
    crop_top = int(round((th - resize_height) / 2.0))
    crop_left = int(round((tw - resize_width) / 2.0))
    return ((crop_top, crop_left), (crop_top + resize_height, crop_left + resize_width))
def rescale_noise_cfg(noise_cfg, noise_pred_text, guidance_rescale=0.0):
    """Returns:"""
    std_text = noise_pred_text.std(dim=list(range(1, noise_pred_text.ndim)), keepdim=True)
    std_cfg = noise_cfg.std(dim=list(range(1, noise_cfg.ndim)), keepdim=True)
    noise_pred_rescaled = noise_cfg * (std_text / std_cfg)
    noise_cfg = guidance_rescale * noise_pred_rescaled + (1 - guidance_rescale) * noise_cfg
    return noise_cfg
class HunyuanDiTPAGPipeline(DiffusionPipeline, PAGMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->transformer->vae'
    _optional_components = ['safety_checker', 'feature_extractor', 'text_encoder_2', 'tokenizer_2', 'text_encoder', 'tokenizer']
    _exclude_from_cpu_offload = ['safety_checker']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'prompt_embeds_2', 'negative_prompt_embeds_2']
    def __init__(self, vae: AutoencoderKL, text_encoder: BertModel, tokenizer: BertTokenizer, transformer: HunyuanDiT2DModel, scheduler: DDPMScheduler,
    safety_checker: Optional[StableDiffusionSafetyChecker]=None, feature_extractor: Optional[CLIPImageProcessor]=None, requires_safety_checker: bool=True,
    text_encoder_2: Optional[T5EncoderModel]=None, tokenizer_2: Optional[MT5Tokenizer]=None, pag_applied_layers: Union[str, List[str]]='blocks.1'):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, tokenizer_2=tokenizer_2, transformer=transformer, scheduler=scheduler,
        safety_checker=safety_checker, feature_extractor=feature_extractor, text_encoder_2=text_encoder_2)
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1) if hasattr(self, 'vae') and self.vae is not None else 8
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
        self.default_sample_size = self.transformer.config.sample_size if hasattr(self, 'transformer') and self.transformer is not None else 128
        self.set_pag_applied_layers(pag_applied_layers, pag_attn_processors=(PAGCFGHunyuanAttnProcessor2_0(), PAGHunyuanAttnProcessor2_0()))
    def encode_prompt(self, prompt: str, device: torch.device=None, dtype: torch.dtype=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True,
    negative_prompt: Optional[str]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    prompt_attention_mask: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None,
    max_sequence_length: Optional[int]=None, text_encoder_index: int=0):
        """Args:"""
        if dtype is None:
            if self.text_encoder_2 is not None: dtype = self.text_encoder_2.dtype
            elif self.transformer is not None: dtype = self.transformer.dtype
            else: dtype = None
        if device is None: device = self._execution_device
        tokenizers = [self.tokenizer, self.tokenizer_2]
        text_encoders = [self.text_encoder, self.text_encoder_2]
        tokenizer = tokenizers[text_encoder_index]
        text_encoder = text_encoders[text_encoder_index]
        if max_sequence_length is None:
            if text_encoder_index == 0: max_length = 77
            if text_encoder_index == 1: max_length = 256
        else: max_length = max_sequence_length
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            text_inputs = tokenizer(prompt, padding='max_length', max_length=max_length, truncation=True, return_attention_mask=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, tokenizer.model_max_length - 1:-1])
            prompt_attention_mask = text_inputs.attention_mask.to(device)
            prompt_embeds = text_encoder(text_input_ids.to(device), attention_mask=prompt_attention_mask)
            prompt_embeds = prompt_embeds[0]
            prompt_attention_mask = prompt_attention_mask.repeat(num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.to(dtype=dtype, device=device)
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
            max_length = prompt_embeds.shape[1]
            uncond_input = tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            negative_prompt_attention_mask = uncond_input.attention_mask.to(device)
            negative_prompt_embeds = text_encoder(uncond_input.input_ids.to(device), attention_mask=negative_prompt_attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
            negative_prompt_attention_mask = negative_prompt_attention_mask.repeat(num_images_per_prompt, 1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        return (prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask)
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
    def check_inputs(self, prompt, height, width, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, prompt_attention_mask=None,
    negative_prompt_attention_mask=None, prompt_embeds_2=None, negative_prompt_embeds_2=None, prompt_attention_mask_2=None,
    negative_prompt_attention_mask_2=None, callback_on_step_end_tensor_inputs=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is None and prompt_embeds_2 is None: raise ValueError('Provide either `prompt` or `prompt_embeds_2`. Cannot leave both `prompt` and `prompt_embeds_2` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if prompt_embeds is not None and prompt_attention_mask is None: raise ValueError('Must provide `prompt_attention_mask` when specifying `prompt_embeds`.')
        if prompt_embeds_2 is not None and prompt_attention_mask_2 is None: raise ValueError('Must provide `prompt_attention_mask_2` when specifying `prompt_embeds_2`.')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if negative_prompt_embeds is not None and negative_prompt_attention_mask is None: raise ValueError('Must provide `negative_prompt_attention_mask` when specifying `negative_prompt_embeds`.')
        if negative_prompt_embeds_2 is not None and negative_prompt_attention_mask_2 is None: raise ValueError('Must provide `negative_prompt_attention_mask_2` when specifying `negative_prompt_embeds_2`.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if prompt_embeds_2 is not None and negative_prompt_embeds_2 is not None:
            if prompt_embeds_2.shape != negative_prompt_embeds_2.shape: raise ValueError(f'`prompt_embeds_2` and `negative_prompt_embeds_2` must have the same shape when passed directly, but got: `prompt_embeds_2` {prompt_embeds_2.shape} != `negative_prompt_embeds_2` {negative_prompt_embeds_2.shape}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def guidance_rescale(self): return self._guidance_rescale
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: Optional[int]=50,
    guidance_scale: Optional[float]=5.0, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: Optional[float]=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    prompt_embeds_2: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds_2: Optional[torch.Tensor]=None,
    prompt_attention_mask: Optional[torch.Tensor]=None, prompt_attention_mask_2: Optional[torch.Tensor]=None, negative_prompt_attention_mask: Optional[torch.Tensor]=None,
    negative_prompt_attention_mask_2: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None,
    callback_on_step_end_tensor_inputs: List[str]=['latents'], guidance_rescale: float=0.0, original_size: Optional[Tuple[int,
    int]]=(1024, 1024), target_size: Optional[Tuple[int, int]]=None, crops_coords_top_left: Tuple[int, int]=(0, 0),
    use_resolution_binning: bool=True, pag_scale: float=3.0, pag_adaptive_scale: float=0.0):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        height = height or self.default_sample_size * self.vae_scale_factor
        width = width or self.default_sample_size * self.vae_scale_factor
        height = int(height // 16 * 16)
        width = int(width // 16 * 16)
        if use_resolution_binning and (height, width) not in SUPPORTED_SHAPE:
            width, height = map_to_standard_shapes(width, height)
            height = int(height)
            width = int(width)
        self.check_inputs(prompt, height, width, negative_prompt, prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask,
        prompt_embeds_2, negative_prompt_embeds_2, prompt_attention_mask_2, negative_prompt_attention_mask_2, callback_on_step_end_tensor_inputs)
        self._guidance_scale = guidance_scale
        self._guidance_rescale = guidance_rescale
        self._interrupt = False
        self._pag_scale = pag_scale
        self._pag_adaptive_scale = pag_adaptive_scale
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        prompt_embeds, negative_prompt_embeds, prompt_attention_mask, negative_prompt_attention_mask = self.encode_prompt(prompt=prompt, device=device,
        dtype=self.transformer.dtype, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, prompt_attention_mask=prompt_attention_mask,
        negative_prompt_attention_mask=negative_prompt_attention_mask, max_sequence_length=77, text_encoder_index=0)
        prompt_embeds_2, negative_prompt_embeds_2, prompt_attention_mask_2, negative_prompt_attention_mask_2 = self.encode_prompt(prompt=prompt,
        device=device, dtype=self.transformer.dtype, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds_2, negative_prompt_embeds=negative_prompt_embeds_2, prompt_attention_mask=prompt_attention_mask_2,
        negative_prompt_attention_mask=negative_prompt_attention_mask_2, max_sequence_length=256, text_encoder_index=1)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        grid_height = height // 8 // self.transformer.config.patch_size
        grid_width = width // 8 // self.transformer.config.patch_size
        base_size = 512 // 8 // self.transformer.config.patch_size
        grid_crops_coords = get_resize_crop_region_for_grid((grid_height, grid_width), base_size)
        image_rotary_emb = get_2d_rotary_pos_embed(self.transformer.inner_dim // self.transformer.num_heads, grid_crops_coords,
        (grid_height, grid_width), device=device, output_type='pt')
        style = torch.tensor([0], device=device)
        target_size = target_size or (height, width)
        add_time_ids = list(original_size + target_size + crops_coords_top_left)
        add_time_ids = torch.tensor([add_time_ids], dtype=prompt_embeds.dtype)
        if self.do_perturbed_attention_guidance:
            prompt_embeds = self._prepare_perturbed_attention_guidance(prompt_embeds, negative_prompt_embeds, self.do_classifier_free_guidance)
            prompt_attention_mask = self._prepare_perturbed_attention_guidance(prompt_attention_mask, negative_prompt_attention_mask, self.do_classifier_free_guidance)
            prompt_embeds_2 = self._prepare_perturbed_attention_guidance(prompt_embeds_2, negative_prompt_embeds_2, self.do_classifier_free_guidance)
            prompt_attention_mask_2 = self._prepare_perturbed_attention_guidance(prompt_attention_mask_2, negative_prompt_attention_mask_2, self.do_classifier_free_guidance)
            add_time_ids = torch.cat([add_time_ids] * 3, dim=0)
            style = torch.cat([style] * 3, dim=0)
        elif self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            prompt_attention_mask = torch.cat([negative_prompt_attention_mask, prompt_attention_mask])
            prompt_embeds_2 = torch.cat([negative_prompt_embeds_2, prompt_embeds_2])
            prompt_attention_mask_2 = torch.cat([negative_prompt_attention_mask_2, prompt_attention_mask_2])
            add_time_ids = torch.cat([add_time_ids] * 2, dim=0)
            style = torch.cat([style] * 2, dim=0)
        prompt_embeds = prompt_embeds.to(device=device)
        prompt_attention_mask = prompt_attention_mask.to(device=device)
        prompt_embeds_2 = prompt_embeds_2.to(device=device)
        prompt_attention_mask_2 = prompt_attention_mask_2.to(device=device)
        add_time_ids = add_time_ids.to(dtype=prompt_embeds.dtype, device=device).repeat(batch_size * num_images_per_prompt, 1)
        style = style.to(device=device).repeat(batch_size * num_images_per_prompt)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        self._num_timesteps = len(timesteps)
        if self.do_perturbed_attention_guidance:
            original_attn_proc = self.transformer.attn_processors
            self._set_pag_attn_processor(pag_applied_layers=self.pag_applied_layers, do_classifier_free_guidance=self.do_classifier_free_guidance)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * (prompt_embeds.shape[0] // latents.shape[0]))
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                t_expand = torch.tensor([t] * latent_model_input.shape[0], device=device).to(dtype=latent_model_input.dtype)
                noise_pred = self.transformer(latent_model_input, t_expand, encoder_hidden_states=prompt_embeds, text_embedding_mask=prompt_attention_mask,
                encoder_hidden_states_t5=prompt_embeds_2, text_embedding_mask_t5=prompt_attention_mask_2, image_meta_size=add_time_ids, style=style,
                image_rotary_emb=image_rotary_emb, return_dict=False)[0]
                noise_pred, _ = noise_pred.chunk(2, dim=1)
                if self.do_perturbed_attention_guidance: noise_pred, noise_pred_text = self._apply_perturbed_attention_guidance(noise_pred,
                self.do_classifier_free_guidance, self.guidance_scale, t, True)
                elif self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.do_classifier_free_guidance and guidance_rescale > 0.0: noise_pred = rescale_noise_cfg(noise_pred, noise_pred_text, guidance_rescale=guidance_rescale)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                    prompt_embeds_2 = callback_outputs.pop('prompt_embeds_2', prompt_embeds_2)
                    negative_prompt_embeds_2 = callback_outputs.pop('negative_prompt_embeds_2', negative_prompt_embeds_2)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
                if XLA_AVAILABLE: xm.mark_step()
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
        if self.do_perturbed_attention_guidance: self.transformer.set_attn_processor(original_attn_proc)
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
