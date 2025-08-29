'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
import math
from itertools import repeat
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
from packaging import version
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ...configuration_utils import FrozenDict
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin, IPAdapterMixin, StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, UNet2DConditionModel
from ...models.attention_processor import Attention, AttnProcessor
from ...models.lora import adjust_lora_scale_text_encoder
from ...pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from ...schedulers import DDIMScheduler, DPMSolverMultistepScheduler
from ...utils import USE_PEFT_BACKEND, deprecate, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .pipeline_output import LEditsPPDiffusionPipelineOutput, LEditsPPInversionPipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import PIL\n        >>> import requests\n        >>> import torch\n        >>> from io import BytesIO\n\n        >>> from sapiens_transformers.diffusers import LEditsPPPipelineStableDiffusion\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n        >>> pipe = LEditsPPPipelineStableDiffusion.from_pretrained(\n        ...     "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n\n        >>> img_url = "https://www.aiml.informatik.tu-darmstadt.de/people/mbrack/cherry_blossom.png"\n        >>> image = load_image(img_url).convert("RGB")\n\n        >>> _ = pipe.invert(image=image, num_inversion_steps=50, skip=0.1)\n\n        >>> edited_image = pipe(\n        ...     editing_prompt=["cherry blossom"], edit_guidance_scale=10.0, edit_threshold=0.75\n        ... ).images[0]\n        ```\n'
class LeditsAttentionStore:
    @staticmethod
    def get_empty_store(): return {'down_cross': [], 'mid_cross': [], 'up_cross': [], 'down_self': [], 'mid_self': [], 'up_self': []}
    def __call__(self, attn, is_cross: bool, place_in_unet: str, editing_prompts, PnP=False):
        if attn.shape[1] <= self.max_size:
            bs = 1 + int(PnP) + editing_prompts
            skip = 2 if PnP else 1
            attn = torch.stack(attn.split(self.batch_size)).permute(1, 0, 2, 3)
            source_batch_size = int(attn.shape[1] // bs)
            self.forward(attn[:, skip * source_batch_size:], is_cross, place_in_unet)
    def forward(self, attn, is_cross: bool, place_in_unet: str):
        key = f"{place_in_unet}_{('cross' if is_cross else 'self')}"
        self.step_store[key].append(attn)
    def between_steps(self, store_step=True):
        if store_step:
            if self.average:
                if len(self.attention_store) == 0: self.attention_store = self.step_store
                else:
                    for key in self.attention_store:
                        for i in range(len(self.attention_store[key])): self.attention_store[key][i] += self.step_store[key][i]
            elif len(self.attention_store) == 0: self.attention_store = [self.step_store]
            else: self.attention_store.append(self.step_store)
            self.cur_step += 1
        self.step_store = self.get_empty_store()
    def get_attention(self, step: int):
        if self.average: attention = {key: [item / self.cur_step for item in self.attention_store[key]] for key in self.attention_store}
        else:
            assert step is not None
            attention = self.attention_store[step]
        return attention
    def aggregate_attention(self, attention_maps, prompts, res: Union[int, Tuple[int]], from_where: List[str], is_cross: bool, select: int):
        out = [[] for x in range(self.batch_size)]
        if isinstance(res, int):
            num_pixels = res ** 2
            resolution = (res, res)
        else:
            num_pixels = res[0] * res[1]
            resolution = res[:2]
        for location in from_where:
            for bs_item in attention_maps[f"{location}_{('cross' if is_cross else 'self')}"]:
                for batch, item in enumerate(bs_item):
                    if item.shape[1] == num_pixels:
                        cross_maps = item.reshape(len(prompts), -1, *resolution, item.shape[-1])[select]
                        out[batch].append(cross_maps)
        out = torch.stack([torch.cat(x, dim=0) for x in out])
        out = out.sum(1) / out.shape[1]
        return out
    def __init__(self, average: bool, batch_size=1, max_resolution=16, max_size: int=None):
        self.step_store = self.get_empty_store()
        self.attention_store = []
        self.cur_step = 0
        self.average = average
        self.batch_size = batch_size
        if max_size is None: self.max_size = max_resolution ** 2
        elif max_size is not None and max_resolution is None: self.max_size = max_size
        else: raise ValueError('Only allowed to set one of max_resolution or max_size')
class LeditsGaussianSmoothing:
    def __init__(self, device):
        kernel_size = [3, 3]
        sigma = [0.5, 0.5]
        kernel = 1
        meshgrids = torch.meshgrid([torch.arange(size, dtype=torch.float32) for size in kernel_size])
        for size, std, mgrid in zip(kernel_size, sigma, meshgrids):
            mean = (size - 1) / 2
            kernel *= 1 / (std * math.sqrt(2 * math.pi)) * torch.exp(-((mgrid - mean) / (2 * std)) ** 2)
        kernel = kernel / torch.sum(kernel)
        kernel = kernel.view(1, 1, *kernel.size())
        kernel = kernel.repeat(1, *[1] * (kernel.dim() - 1))
        self.weight = kernel.to(device)
    def __call__(self, input):
        """Returns:"""
        return F.conv2d(input, weight=self.weight.to(input.dtype))
class LEDITSCrossAttnProcessor:
    def __init__(self, attention_store, place_in_unet, pnp, editing_prompts):
        self.attnstore = attention_store
        self.place_in_unet = place_in_unet
        self.editing_prompts = editing_prompts
        self.pnp = pnp
    def __call__(self, attn: Attention, hidden_states, encoder_hidden_states, attention_mask=None, temb=None):
        batch_size, sequence_length, _ = hidden_states.shape if encoder_hidden_states is None else encoder_hidden_states.shape
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
        self.attnstore(attention_probs, is_cross=True, place_in_unet=self.place_in_unet, editing_prompts=self.editing_prompts, PnP=self.pnp)
        hidden_states = torch.bmm(attention_probs, value)
        hidden_states = attn.batch_to_head_dim(hidden_states)
        hidden_states = attn.to_out[0](hidden_states)
        hidden_states = attn.to_out[1](hidden_states)
        hidden_states = hidden_states / attn.rescale_output_factor
        return hidden_states
def rescale_noise_cfg(noise_cfg, noise_pred_text, guidance_rescale=0.0):
    """Returns:"""
    std_text = noise_pred_text.std(dim=list(range(1, noise_pred_text.ndim)), keepdim=True)
    std_cfg = noise_cfg.std(dim=list(range(1, noise_cfg.ndim)), keepdim=True)
    noise_pred_rescaled = noise_cfg * (std_text / std_cfg)
    noise_cfg = guidance_rescale * noise_pred_rescaled + (1 - guidance_rescale) * noise_cfg
    return noise_cfg
class LEditsPPPipelineStableDiffusion(DiffusionPipeline, TextualInversionLoaderMixin, StableDiffusionLoraLoaderMixin, IPAdapterMixin, FromSingleFileMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _exclude_from_cpu_offload = ['safety_checker']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds']
    _optional_components = ['safety_checker', 'feature_extractor', 'image_encoder']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: Union[DDIMScheduler, DPMSolverMultistepScheduler],
    safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if not isinstance(scheduler, DDIMScheduler) and (not isinstance(scheduler, DPMSolverMultistepScheduler)): scheduler = DPMSolverMultistepScheduler.from_config(scheduler.config, algorithm_type='sde-dpmsolver++', solver_order=2)
        if hasattr(scheduler.config, 'steps_offset') and scheduler.config.steps_offset != 1:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} is outdated. `steps_offset` should be set to 1 instead of {scheduler.config.steps_offset}. Please make sure to update the config accordingly as leaving `steps_offset` might led to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('steps_offset!=1', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['steps_offset'] = 1
            scheduler._internal_dict = FrozenDict(new_config)
        if hasattr(scheduler.config, 'clip_sample') and scheduler.config.clip_sample is True:
            deprecation_message = f'The configuration file of this scheduler: {scheduler} has not set the configuration `clip_sample`. `clip_sample` should be set to False in the configuration file. Please make sure to update the config accordingly as not setting `clip_sample` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `scheduler/scheduler_config.json` file'
            deprecate('clip_sample not set', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(scheduler.config)
            new_config['clip_sample'] = False
            scheduler._internal_dict = FrozenDict(new_config)
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        is_unet_version_less_0_9_0 = hasattr(unet.config, '_diffusers_version') and version.parse(version.parse(unet.config._diffusers_version).base_version) < version.parse('0.9.0.dev0')
        is_unet_sample_size_less_64 = hasattr(unet.config, 'sample_size') and unet.config.sample_size < 64
        if is_unet_version_less_0_9_0 and is_unet_sample_size_less_64:
            deprecation_message = "The configuration file of the unet has set the default `sample_size` to smaller than 64 which seems highly unlikely. If your checkpoint is a fine-tuned version of any of the following: \n- CompVis/stable-diffusion-v1-4 \n- CompVis/stable-diffusion-v1-3 \n- CompVis/stable-diffusion-v1-2 \n- CompVis/stable-diffusion-v1-1 \n- runwayml/stable-diffusion-v1-5 \n- runwayml/stable-diffusion-inpainting \n you should change 'sample_size' to 64 in the configuration file. Please make sure to update the config accordingly as leaving `sample_size=32` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `unet/config.json` file"
            deprecate('sample_size<64', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(unet.config)
            new_config['sample_size'] = 64
            unet._internal_dict = FrozenDict(new_config)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
        self.inversion_steps = None
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
    def prepare_extra_step_kwargs(self, eta, generator=None):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, negative_prompt=None, editing_prompt_embeddings=None, negative_prompt_embeds=None, callback_on_step_end_tensor_inputs=None):
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if editing_prompt_embeddings is not None and negative_prompt_embeds is not None:
            if editing_prompt_embeddings.shape != negative_prompt_embeds.shape: raise ValueError(f'`editing_prompt_embeddings` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `editing_prompt_embeddings` {editing_prompt_embeddings.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, latents):
        latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def prepare_unet(self, attention_store, PnP: bool=False):
        attn_procs = {}
        for name in self.unet.attn_processors.keys():
            if name.startswith('mid_block'): place_in_unet = 'mid'
            elif name.startswith('up_blocks'): place_in_unet = 'up'
            elif name.startswith('down_blocks'): place_in_unet = 'down'
            else: continue
            if 'attn2' in name and place_in_unet != 'mid': attn_procs[name] = LEDITSCrossAttnProcessor(attention_store=attention_store,
            place_in_unet=place_in_unet, pnp=PnP, editing_prompts=self.enabled_editing_prompts)
            else: attn_procs[name] = AttnProcessor()
        self.unet.set_attn_processor(attn_procs)
    def encode_prompt(self, device, num_images_per_prompt, enable_edit_guidance, negative_prompt=None, editing_prompt=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    editing_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        batch_size = self.batch_size
        num_edit_tokens = None
        if negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but exoected{batch_size} based on the input images. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            if isinstance(self, TextualInversionLoaderMixin): uncond_tokens = self.maybe_convert_prompt(uncond_tokens, self.tokenizer)
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = uncond_input.attention_mask.to(device)
            else: attention_mask = None
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if self.text_encoder is not None: prompt_embeds_dtype = self.text_encoder.dtype
        elif self.unet is not None: prompt_embeds_dtype = self.unet.dtype
        else: prompt_embeds_dtype = negative_prompt_embeds.dtype
        negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
        if enable_edit_guidance:
            if editing_prompt_embeds is None:
                if isinstance(editing_prompt, str): editing_prompt = [editing_prompt]
                max_length = negative_prompt_embeds.shape[1]
                text_inputs = self.tokenizer([x for item in editing_prompt for x in repeat(item, batch_size)], padding='max_length', max_length=max_length, truncation=True,
                return_tensors='pt', return_length=True)
                num_edit_tokens = text_inputs.length - 2
                text_input_ids = text_inputs.input_ids
                untruncated_ids = self.tokenizer([x for item in editing_prompt for x in repeat(item, batch_size)], padding='longest', return_tensors='pt').input_ids
                if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
                if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = text_inputs.attention_mask.to(device)
                else: attention_mask = None
                if clip_skip is None:
                    editing_prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
                    editing_prompt_embeds = editing_prompt_embeds[0]
                else:
                    editing_prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask, output_hidden_states=True)
                    editing_prompt_embeds = editing_prompt_embeds[-1][-(clip_skip + 1)]
                    editing_prompt_embeds = self.text_encoder.text_model.final_layer_norm(editing_prompt_embeds)
            editing_prompt_embeds = editing_prompt_embeds.to(dtype=negative_prompt_embeds.dtype, device=device)
            bs_embed_edit, seq_len, _ = editing_prompt_embeds.shape
            editing_prompt_embeds = editing_prompt_embeds.to(dtype=negative_prompt_embeds.dtype, device=device)
            editing_prompt_embeds = editing_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            editing_prompt_embeds = editing_prompt_embeds.view(bs_embed_edit * num_images_per_prompt, seq_len, -1)
        seq_len = negative_prompt_embeds.shape[1]
        negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
        negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
        negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        if isinstance(self, StableDiffusionLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (editing_prompt_embeds, negative_prompt_embeds, num_edit_tokens)
    @property
    def guidance_rescale(self): return self._guidance_rescale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, negative_prompt: Optional[Union[str, List[str]]]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, editing_prompt: Optional[Union[str, List[str]]]=None, editing_prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, reverse_editing_direction: Optional[Union[bool, List[bool]]]=False,
    edit_guidance_scale: Optional[Union[float, List[float]]]=5, edit_warmup_steps: Optional[Union[int, List[int]]]=0,
    edit_cooldown_steps: Optional[Union[int, List[int]]]=None, edit_threshold: Optional[Union[float, List[float]]]=0.9,
    user_mask: Optional[torch.Tensor]=None, sem_guidance: Optional[List[torch.Tensor]]=None, use_cross_attn_mask: bool=False,
    use_intersect_mask: bool=True, attn_store_steps: Optional[List[int]]=[], store_averaged_over_steps: bool=True,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, guidance_rescale: float=0.0, clip_skip: Optional[int]=None,
    callback_on_step_end: Optional[Callable[[int, int, Dict], None]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        if self.inversion_steps is None: raise ValueError('You need to invert an input image first before calling the pipeline. The `invert` method has to be called beforehand. Edits will always be performed for the last inverted image(s).')
        eta = self.eta
        num_images_per_prompt = 1
        latents = self.init_latents
        zs = self.zs
        self.scheduler.set_timesteps(len(self.scheduler.timesteps))
        if use_intersect_mask: use_cross_attn_mask = True
        if use_cross_attn_mask: self.smoothing = LeditsGaussianSmoothing(self.device)
        if user_mask is not None: user_mask = user_mask.to(self.device)
        org_prompt = ''
        self.check_inputs(negative_prompt, editing_prompt_embeds, negative_prompt_embeds, callback_on_step_end_tensor_inputs)
        self._guidance_rescale = guidance_rescale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        batch_size = self.batch_size
        if editing_prompt:
            enable_edit_guidance = True
            if isinstance(editing_prompt, str): editing_prompt = [editing_prompt]
            self.enabled_editing_prompts = len(editing_prompt)
        elif editing_prompt_embeds is not None:
            enable_edit_guidance = True
            self.enabled_editing_prompts = editing_prompt_embeds.shape[0]
        else:
            self.enabled_editing_prompts = 0
            enable_edit_guidance = False
        lora_scale = self.cross_attention_kwargs.get('scale', None) if self.cross_attention_kwargs is not None else None
        edit_concepts, uncond_embeddings, num_edit_tokens = self.encode_prompt(editing_prompt=editing_prompt, device=self.device,
        num_images_per_prompt=num_images_per_prompt, enable_edit_guidance=enable_edit_guidance, negative_prompt=negative_prompt,
        editing_prompt_embeds=editing_prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=lora_scale, clip_skip=self.clip_skip)
        if enable_edit_guidance:
            text_embeddings = torch.cat([uncond_embeddings, edit_concepts])
            self.text_cross_attention_maps = [editing_prompt] if isinstance(editing_prompt, str) else editing_prompt
        else: text_embeddings = torch.cat([uncond_embeddings])
        timesteps = self.inversion_steps
        t_to_idx = {int(v): k for k, v in enumerate(timesteps[-zs.shape[0]:])}
        if use_cross_attn_mask:
            self.attention_store = LeditsAttentionStore(average=store_averaged_over_steps, batch_size=batch_size,
            max_size=latents.shape[-2] / 4.0 * (latents.shape[-1] / 4.0), max_resolution=None)
            self.prepare_unet(self.attention_store, PnP=False)
            resolution = latents.shape[-2:]
            att_res = (int(resolution[0] / 4), int(resolution[1] / 4))
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, None, None, text_embeddings.dtype, self.device, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(eta)
        self.sem_guidance = None
        self.activation_mask = None
        num_warmup_steps = 0
        with self.progress_bar(total=len(timesteps)) as progress_bar:
            for i, t in enumerate(timesteps):
                if enable_edit_guidance: latent_model_input = torch.cat([latents] * (1 + self.enabled_editing_prompts))
                else: latent_model_input = latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                text_embed_input = text_embeddings
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embed_input).sample
                noise_pred_out = noise_pred.chunk(1 + self.enabled_editing_prompts)
                noise_pred_uncond = noise_pred_out[0]
                noise_pred_edit_concepts = noise_pred_out[1:]
                noise_guidance_edit = torch.zeros(noise_pred_uncond.shape, device=self.device, dtype=noise_pred_uncond.dtype)
                if sem_guidance is not None and len(sem_guidance) > i: noise_guidance_edit += sem_guidance[i].to(self.device)
                elif enable_edit_guidance:
                    if self.activation_mask is None: self.activation_mask = torch.zeros((len(timesteps), len(noise_pred_edit_concepts), *noise_pred_edit_concepts[0].shape))
                    if self.sem_guidance is None: self.sem_guidance = torch.zeros((len(timesteps), *noise_pred_uncond.shape))
                    for c, noise_pred_edit_concept in enumerate(noise_pred_edit_concepts):
                        if isinstance(edit_warmup_steps, list): edit_warmup_steps_c = edit_warmup_steps[c]
                        else: edit_warmup_steps_c = edit_warmup_steps
                        if i < edit_warmup_steps_c: continue
                        if isinstance(edit_guidance_scale, list): edit_guidance_scale_c = edit_guidance_scale[c]
                        else: edit_guidance_scale_c = edit_guidance_scale
                        if isinstance(edit_threshold, list): edit_threshold_c = edit_threshold[c]
                        else: edit_threshold_c = edit_threshold
                        if isinstance(reverse_editing_direction, list): reverse_editing_direction_c = reverse_editing_direction[c]
                        else: reverse_editing_direction_c = reverse_editing_direction
                        if isinstance(edit_cooldown_steps, list): edit_cooldown_steps_c = edit_cooldown_steps[c]
                        elif edit_cooldown_steps is None: edit_cooldown_steps_c = i + 1
                        else: edit_cooldown_steps_c = edit_cooldown_steps
                        if i >= edit_cooldown_steps_c: continue
                        noise_guidance_edit_tmp = noise_pred_edit_concept - noise_pred_uncond
                        if reverse_editing_direction_c: noise_guidance_edit_tmp = noise_guidance_edit_tmp * -1
                        noise_guidance_edit_tmp = noise_guidance_edit_tmp * edit_guidance_scale_c
                        if user_mask is not None: noise_guidance_edit_tmp = noise_guidance_edit_tmp * user_mask
                        if use_cross_attn_mask:
                            out = self.attention_store.aggregate_attention(attention_maps=self.attention_store.step_store, prompts=self.text_cross_attention_maps,
                            res=att_res, from_where=['up', 'down'], is_cross=True, select=self.text_cross_attention_maps.index(editing_prompt[c]))
                            attn_map = out[:, :, :, 1:1 + num_edit_tokens[c]]
                            if attn_map.shape[3] != num_edit_tokens[c]: raise ValueError(f'Incorrect shape of attention_map. Expected size {num_edit_tokens[c]}, but found {attn_map.shape[3]}!')
                            attn_map = torch.sum(attn_map, dim=3)
                            attn_map = F.pad(attn_map.unsqueeze(1), (1, 1, 1, 1), mode='reflect')
                            attn_map = self.smoothing(attn_map).squeeze(1)
                            if attn_map.dtype == torch.float32: tmp = torch.quantile(attn_map.flatten(start_dim=1), edit_threshold_c, dim=1)
                            else: tmp = torch.quantile(attn_map.flatten(start_dim=1).to(torch.float32), edit_threshold_c, dim=1).to(attn_map.dtype)
                            attn_mask = torch.where(attn_map >= tmp.unsqueeze(1).unsqueeze(1).repeat(1, *att_res), 1.0, 0.0)
                            attn_mask = F.interpolate(attn_mask.unsqueeze(1), noise_guidance_edit_tmp.shape[-2:]).repeat(1, 4, 1, 1)
                            self.activation_mask[i, c] = attn_mask.detach().cpu()
                            if not use_intersect_mask: noise_guidance_edit_tmp = noise_guidance_edit_tmp * attn_mask
                        if use_intersect_mask:
                            if t <= 800:
                                noise_guidance_edit_tmp_quantile = torch.abs(noise_guidance_edit_tmp)
                                noise_guidance_edit_tmp_quantile = torch.sum(noise_guidance_edit_tmp_quantile, dim=1, keepdim=True)
                                noise_guidance_edit_tmp_quantile = noise_guidance_edit_tmp_quantile.repeat(1, self.unet.config.in_channels, 1, 1)
                                if noise_guidance_edit_tmp_quantile.dtype == torch.float32: tmp = torch.quantile(noise_guidance_edit_tmp_quantile.flatten(start_dim=2), edit_threshold_c, dim=2, keepdim=False)
                                else: tmp = torch.quantile(noise_guidance_edit_tmp_quantile.flatten(start_dim=2).to(torch.float32), edit_threshold_c, dim=2, keepdim=False).to(noise_guidance_edit_tmp_quantile.dtype)
                                intersect_mask = torch.where(noise_guidance_edit_tmp_quantile >= tmp[:, :, None, None], torch.ones_like(noise_guidance_edit_tmp), torch.zeros_like(noise_guidance_edit_tmp)) * attn_mask
                                self.activation_mask[i, c] = intersect_mask.detach().cpu()
                                noise_guidance_edit_tmp = noise_guidance_edit_tmp * intersect_mask
                            else: noise_guidance_edit_tmp = noise_guidance_edit_tmp * attn_mask
                        elif not use_cross_attn_mask:
                            noise_guidance_edit_tmp_quantile = torch.abs(noise_guidance_edit_tmp)
                            noise_guidance_edit_tmp_quantile = torch.sum(noise_guidance_edit_tmp_quantile, dim=1, keepdim=True)
                            noise_guidance_edit_tmp_quantile = noise_guidance_edit_tmp_quantile.repeat(1, 4, 1, 1)
                            if noise_guidance_edit_tmp_quantile.dtype == torch.float32: tmp = torch.quantile(noise_guidance_edit_tmp_quantile.flatten(start_dim=2), edit_threshold_c, dim=2, keepdim=False)
                            else: tmp = torch.quantile(noise_guidance_edit_tmp_quantile.flatten(start_dim=2).to(torch.float32), edit_threshold_c, dim=2, keepdim=False).to(noise_guidance_edit_tmp_quantile.dtype)
                            self.activation_mask[i, c] = torch.where(noise_guidance_edit_tmp_quantile >= tmp[:, :, None, None], torch.ones_like(noise_guidance_edit_tmp), torch.zeros_like(noise_guidance_edit_tmp)).detach().cpu()
                            noise_guidance_edit_tmp = torch.where(noise_guidance_edit_tmp_quantile >= tmp[:, :, None, None], noise_guidance_edit_tmp, torch.zeros_like(noise_guidance_edit_tmp))
                        noise_guidance_edit += noise_guidance_edit_tmp
                    self.sem_guidance[i] = noise_guidance_edit.detach().cpu()
                noise_pred = noise_pred_uncond + noise_guidance_edit
                if enable_edit_guidance and self.guidance_rescale > 0.0: noise_pred = rescale_noise_cfg(noise_pred,
                noise_pred_edit_concepts.mean(dim=0, keepdim=False), guidance_rescale=self.guidance_rescale)
                idx = t_to_idx[int(t)]
                latents = self.scheduler.step(noise_pred, t, latents, variance_noise=zs[idx], **extra_step_kwargs).prev_sample
                if use_cross_attn_mask:
                    store_step = i in attn_store_steps
                    self.attention_store.between_steps(store_step)
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False, generator=generator)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, self.device, text_embeddings.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        self.maybe_free_model_hooks()
        if not return_dict: return (image, has_nsfw_concept)
        return LEditsPPDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
    @torch.no_grad()
    def invert(self, image: PipelineImageInput, source_prompt: str='', source_guidance_scale: float=3.5, num_inversion_steps: int=30, skip: float=0.15, generator: Optional[torch.Generator]=None,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: Optional[int]=None, height: Optional[int]=None, width: Optional[int]=None,
    resize_mode: Optional[str]='default', crops_coords: Optional[Tuple[int, int, int, int]]=None):
        """Returns:"""
        self.unet.set_attn_processor(AttnProcessor())
        self.eta = 1.0
        self.scheduler.config.timestep_spacing = 'leading'
        self.scheduler.set_timesteps(int(num_inversion_steps * (1 + skip)))
        self.inversion_steps = self.scheduler.timesteps[-num_inversion_steps:]
        timesteps = self.inversion_steps
        x0, resized = self.encode_image(image, dtype=self.text_encoder.dtype, height=height, width=width, resize_mode=resize_mode, crops_coords=crops_coords)
        self.batch_size = x0.shape[0]
        image_rec = self.vae.decode(x0 / self.vae.config.scaling_factor, return_dict=False, generator=generator)[0]
        image_rec = self.image_processor.postprocess(image_rec, output_type='pil')
        do_classifier_free_guidance = source_guidance_scale > 1.0
        lora_scale = cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        uncond_embedding, text_embeddings, _ = self.encode_prompt(num_images_per_prompt=1, device=self.device, negative_prompt=None, enable_edit_guidance=do_classifier_free_guidance,
        editing_prompt=source_prompt, lora_scale=lora_scale, clip_skip=clip_skip)
        variance_noise_shape = (num_inversion_steps, *x0.shape)
        t_to_idx = {int(v): k for k, v in enumerate(timesteps)}
        xts = torch.zeros(size=variance_noise_shape, device=self.device, dtype=uncond_embedding.dtype)
        for t in reversed(timesteps):
            idx = num_inversion_steps - t_to_idx[int(t)] - 1
            noise = randn_tensor(shape=x0.shape, generator=generator, device=self.device, dtype=x0.dtype)
            xts[idx] = self.scheduler.add_noise(x0, noise, torch.Tensor([t]))
        xts = torch.cat([x0.unsqueeze(0), xts], dim=0)
        self.scheduler.set_timesteps(len(self.scheduler.timesteps))
        zs = torch.zeros(size=variance_noise_shape, device=self.device, dtype=uncond_embedding.dtype)
        with self.progress_bar(total=len(timesteps)) as progress_bar:
            for t in timesteps:
                idx = num_inversion_steps - t_to_idx[int(t)] - 1
                xt = xts[idx + 1]
                noise_pred = self.unet(xt, timestep=t, encoder_hidden_states=uncond_embedding).sample
                if not source_prompt == '':
                    noise_pred_cond = self.unet(xt, timestep=t, encoder_hidden_states=text_embeddings).sample
                    noise_pred = noise_pred + source_guidance_scale * (noise_pred_cond - noise_pred)
                xtm1 = xts[idx]
                z, xtm1_corrected = compute_noise(self.scheduler, xtm1, xt, t, noise_pred, self.eta)
                zs[idx] = z
                xts[idx] = xtm1_corrected
                progress_bar.update()
        self.init_latents = xts[-1].expand(self.batch_size, -1, -1, -1)
        zs = zs.flip(0)
        self.zs = zs
        return LEditsPPInversionPipelineOutput(images=resized, vae_reconstruction_images=image_rec)
    @torch.no_grad()
    def encode_image(self, image, dtype=None, height=None, width=None, resize_mode='default', crops_coords=None):
        image = self.image_processor.preprocess(image=image, height=height, width=width, resize_mode=resize_mode, crops_coords=crops_coords)
        resized = self.image_processor.postprocess(image=image, output_type='pil')
        image = image.to(dtype)
        x0 = self.vae.encode(image.to(self.device)).latent_dist.mode()
        x0 = x0.to(dtype)
        x0 = self.vae.config.scaling_factor * x0
        return (x0, resized)
def compute_noise_ddim(scheduler, prev_latents, latents, timestep, noise_pred, eta):
    prev_timestep = timestep - scheduler.config.num_train_timesteps // scheduler.num_inference_steps
    alpha_prod_t = scheduler.alphas_cumprod[timestep]
    alpha_prod_t_prev = scheduler.alphas_cumprod[prev_timestep] if prev_timestep >= 0 else scheduler.final_alpha_cumprod
    beta_prod_t = 1 - alpha_prod_t
    pred_original_sample = (latents - beta_prod_t ** 0.5 * noise_pred) / alpha_prod_t ** 0.5
    if scheduler.config.clip_sample: pred_original_sample = torch.clamp(pred_original_sample, -1, 1)
    variance = scheduler._get_variance(timestep, prev_timestep)
    std_dev_t = eta * variance ** 0.5
    pred_sample_direction = (1 - alpha_prod_t_prev - std_dev_t ** 2) ** 0.5 * noise_pred
    mu_xt = alpha_prod_t_prev ** 0.5 * pred_original_sample + pred_sample_direction
    if variance > 0.0: noise = (prev_latents - mu_xt) / (variance ** 0.5 * eta)
    else: noise = torch.tensor([0.0]).to(latents.device)
    return (noise, mu_xt + eta * variance ** 0.5 * noise)
def compute_noise_sde_dpm_pp_2nd(scheduler, prev_latents, latents, timestep, noise_pred, eta):
    def first_order_update(model_output, sample):
        sigma_t, sigma_s = (scheduler.sigmas[scheduler.step_index + 1], scheduler.sigmas[scheduler.step_index])
        alpha_t, sigma_t = scheduler._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s, sigma_s = scheduler._sigma_to_alpha_sigma_t(sigma_s)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s = torch.log(alpha_s) - torch.log(sigma_s)
        h = lambda_t - lambda_s
        mu_xt = sigma_t / sigma_s * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * model_output
        mu_xt = scheduler.dpm_solver_first_order_update(model_output=model_output, sample=sample, noise=torch.zeros_like(sample))
        sigma = sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h))
        if sigma > 0.0: noise = (prev_latents - mu_xt) / sigma
        else: noise = torch.tensor([0.0]).to(sample.device)
        prev_sample = mu_xt + sigma * noise
        return (noise, prev_sample)
    def second_order_update(model_output_list, sample):
        sigma_t, sigma_s0, sigma_s1 = (scheduler.sigmas[scheduler.step_index + 1], scheduler.sigmas[scheduler.step_index], scheduler.sigmas[scheduler.step_index - 1])
        alpha_t, sigma_t = scheduler._sigma_to_alpha_sigma_t(sigma_t)
        alpha_s0, sigma_s0 = scheduler._sigma_to_alpha_sigma_t(sigma_s0)
        alpha_s1, sigma_s1 = scheduler._sigma_to_alpha_sigma_t(sigma_s1)
        lambda_t = torch.log(alpha_t) - torch.log(sigma_t)
        lambda_s0 = torch.log(alpha_s0) - torch.log(sigma_s0)
        lambda_s1 = torch.log(alpha_s1) - torch.log(sigma_s1)
        m0, m1 = (model_output_list[-1], model_output_list[-2])
        h, h_0 = (lambda_t - lambda_s0, lambda_s0 - lambda_s1)
        r0 = h_0 / h
        D0, D1 = (m0, 1.0 / r0 * (m0 - m1))
        mu_xt = sigma_t / sigma_s0 * torch.exp(-h) * sample + alpha_t * (1 - torch.exp(-2.0 * h)) * D0 + 0.5 * (alpha_t * (1 - torch.exp(-2.0 * h))) * D1
        sigma = sigma_t * torch.sqrt(1.0 - torch.exp(-2 * h))
        if sigma > 0.0: noise = (prev_latents - mu_xt) / sigma
        else: noise = torch.tensor([0.0]).to(sample.device)
        prev_sample = mu_xt + sigma * noise
        return (noise, prev_sample)
    if scheduler.step_index is None: scheduler._init_step_index(timestep)
    model_output = scheduler.convert_model_output(model_output=noise_pred, sample=latents)
    for i in range(scheduler.config.solver_order - 1): scheduler.model_outputs[i] = scheduler.model_outputs[i + 1]
    scheduler.model_outputs[-1] = model_output
    if scheduler.lower_order_nums < 1: noise, prev_sample = first_order_update(model_output, latents)
    else: noise, prev_sample = second_order_update(scheduler.model_outputs, latents)
    if scheduler.lower_order_nums < scheduler.config.solver_order: scheduler.lower_order_nums += 1
    scheduler._step_index += 1
    return (noise, prev_sample)
def compute_noise(scheduler, *args):
    if isinstance(scheduler, DDIMScheduler): return compute_noise_ddim(scheduler, *args)
    elif isinstance(scheduler, DPMSolverMultistepScheduler) and scheduler.config.algorithm_type == 'sde-dpmsolver++' and (scheduler.config.solver_order == 2): return compute_noise_sde_dpm_pp_2nd(scheduler, *args)
    else: raise NotImplementedError
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
