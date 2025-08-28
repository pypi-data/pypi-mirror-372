'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from sapiens_transformers import CLIPTextModel, CLIPTokenizer, LlamaModel, LlamaTokenizerFast
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...loaders import HunyuanVideoLoraLoaderMixin
from ...models import AutoencoderKLHunyuanVideo, HunyuanVideoTransformer3DModel
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ...video_processor import VideoProcessor
from ..pipeline_utils import DiffusionPipeline
from .pipeline_output import HunyuanVideoPipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```python\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import HunyuanVideoPipeline, HunyuanVideoTransformer3DModel\n        >>> from sapiens_transformers.diffusers.utils import export_to_video\n\n        >>> model_id = "hunyuanvideo-community/HunyuanVideo"\n        >>> transformer = HunyuanVideoTransformer3DModel.from_pretrained(\n        ...     model_id, subfolder="transformer", torch_dtype=torch.bfloat16\n        ... )\n        >>> pipe = HunyuanVideoPipeline.from_pretrained(model_id, transformer=transformer, torch_dtype=torch.float16)\n        >>> pipe.vae.enable_tiling()\n        >>> pipe.to("cuda")\n\n        >>> output = pipe(\n        ...     prompt="A cat walks on the grass, realistic",\n        ...     height=320,\n        ...     width=512,\n        ...     num_frames=61,\n        ...     num_inference_steps=30,\n        ... ).frames[0]\n        >>> export_to_video(output, "output.mp4", fps=15)\n        ```\n'
DEFAULT_PROMPT_TEMPLATE = {'template': '<|start_header_id|>system<|end_header_id|>\n\nDescribe the video by detailing the following aspects: 1. The main content and theme of the video.2. The color, shape, size, texture, quantity, text, and spatial relationships of the objects.3. Actions, events, behaviors temporal relationships, physical movement changes of the objects.4. background environment, light, style and atmosphere.5. camera angles, movements, and transitions used in the video:<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{}<|eot_id|>', 'crop_start': 95}
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
class HunyuanVideoPipeline(DiffusionPipeline, HunyuanVideoLoraLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->transformer->vae'
    _callback_tensor_inputs = ['latents', 'prompt_embeds']
    def __init__(self, text_encoder: LlamaModel, tokenizer: LlamaTokenizerFast, transformer: HunyuanVideoTransformer3DModel, vae: AutoencoderKLHunyuanVideo,
    scheduler: FlowMatchEulerDiscreteScheduler, text_encoder_2: CLIPTextModel, tokenizer_2: CLIPTokenizer):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, transformer=transformer, scheduler=scheduler, text_encoder_2=text_encoder_2, tokenizer_2=tokenizer_2)
        self.vae_scale_factor_temporal = self.vae.temporal_compression_ratio if hasattr(self, 'vae') and self.vae is not None else 4
        self.vae_scale_factor_spatial = self.vae.spatial_compression_ratio if hasattr(self, 'vae') and self.vae is not None else 8
        self.video_processor = VideoProcessor(vae_scale_factor=self.vae_scale_factor_spatial)
    def _get_llama_prompt_embeds(self, prompt: Union[str, List[str]], prompt_template: Dict[str, Any], num_videos_per_prompt: int=1, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None,
    max_sequence_length: int=256, num_hidden_layers_to_skip: int=2) -> Tuple[torch.Tensor, torch.Tensor]:
        device = device or self._execution_device
        dtype = dtype or self.text_encoder.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        prompt = [prompt_template['template'].format(p) for p in prompt]
        crop_start = prompt_template.get('crop_start', None)
        if crop_start is None:
            prompt_template_input = self.tokenizer(prompt_template['template'], padding='max_length', return_tensors='pt', return_length=False, return_overflowing_tokens=False, return_attention_mask=False)
            crop_start = prompt_template_input['input_ids'].shape[-1]
            crop_start -= 2
        max_sequence_length += crop_start
        text_inputs = self.tokenizer(prompt, max_length=max_sequence_length, padding='max_length', truncation=True, return_tensors='pt', return_length=False, return_overflowing_tokens=False, return_attention_mask=True)
        text_input_ids = text_inputs.input_ids.to(device=device)
        prompt_attention_mask = text_inputs.attention_mask.to(device=device)
        prompt_embeds = self.text_encoder(input_ids=text_input_ids, attention_mask=prompt_attention_mask, output_hidden_states=True).hidden_states[-(num_hidden_layers_to_skip + 1)]
        prompt_embeds = prompt_embeds.to(dtype=dtype)
        if crop_start is not None and crop_start > 0:
            prompt_embeds = prompt_embeds[:, crop_start:]
            prompt_attention_mask = prompt_attention_mask[:, crop_start:]
        _, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_videos_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(batch_size * num_videos_per_prompt, seq_len, -1)
        prompt_attention_mask = prompt_attention_mask.repeat(1, num_videos_per_prompt)
        prompt_attention_mask = prompt_attention_mask.view(batch_size * num_videos_per_prompt, seq_len)
        return (prompt_embeds, prompt_attention_mask)
    def _get_clip_prompt_embeds(self, prompt: Union[str, List[str]], num_videos_per_prompt: int=1, device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None, max_sequence_length: int=77) -> torch.Tensor:
        device = device or self._execution_device
        dtype = dtype or self.text_encoder_2.dtype
        prompt = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompt)
        text_inputs = self.tokenizer_2(prompt, padding='max_length', max_length=max_sequence_length, truncation=True, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        untruncated_ids = self.tokenizer_2(prompt, padding='longest', return_tensors='pt').input_ids
        if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer_2.batch_decode(untruncated_ids[:, max_sequence_length - 1:-1])
        prompt_embeds = self.text_encoder_2(text_input_ids.to(device), output_hidden_states=False).pooler_output
        prompt_embeds = prompt_embeds.repeat(1, num_videos_per_prompt)
        prompt_embeds = prompt_embeds.view(batch_size * num_videos_per_prompt, -1)
        return prompt_embeds
    def encode_prompt(self, prompt: Union[str, List[str]], prompt_2: Union[str, List[str]]=None, prompt_template: Dict[str, Any]=DEFAULT_PROMPT_TEMPLATE, num_videos_per_prompt: int=1,
    prompt_embeds: Optional[torch.Tensor]=None, pooled_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    device: Optional[torch.device]=None, dtype: Optional[torch.dtype]=None, max_sequence_length: int=256):
        if prompt_embeds is None: prompt_embeds, prompt_attention_mask = self._get_llama_prompt_embeds(prompt, prompt_template,
        num_videos_per_prompt, device=device, dtype=dtype, max_sequence_length=max_sequence_length)
        if pooled_prompt_embeds is None:
            if prompt_2 is None and pooled_prompt_embeds is None: prompt_2 = prompt
            pooled_prompt_embeds = self._get_clip_prompt_embeds(prompt, num_videos_per_prompt, device=device, dtype=dtype, max_sequence_length=77)
        return (prompt_embeds, pooled_prompt_embeds, prompt_attention_mask)
    def check_inputs(self, prompt, prompt_2, height, width, prompt_embeds=None, callback_on_step_end_tensor_inputs=None, prompt_template=None):
        if height % 16 != 0 or width % 16 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        if prompt_template is not None:
            if not isinstance(prompt_template, dict): raise ValueError(f'`prompt_template` has to be of type `dict` but is {type(prompt_template)}')
            if 'template' not in prompt_template: raise ValueError(f'`prompt_template` has to contain a key `template` but only found {prompt_template.keys()}')
    def prepare_latents(self, batch_size: int, num_channels_latents: 32, height: int=720, width: int=1280, num_frames: int=129, dtype: Optional[torch.dtype]=None, device: Optional[torch.device]=None,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None) -> torch.Tensor:
        if latents is not None: return latents.to(device=device, dtype=dtype)
        shape = (batch_size, num_channels_latents, num_frames, int(height) // self.vae_scale_factor_spatial, int(width) // self.vae_scale_factor_spatial)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        return latents
    def enable_vae_slicing(self): self.vae.enable_slicing()
    def disable_vae_slicing(self): self.vae.disable_slicing()
    def enable_vae_tiling(self): self.vae.enable_tiling()
    def disable_vae_tiling(self): self.vae.disable_tiling()
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def attention_kwargs(self): return self._attention_kwargs
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Union[str, List[str]]=None, height: int=720, width: int=1280, num_frames: int=129, num_inference_steps: int=50,
    sigmas: List[float]=None, guidance_scale: float=6.0, num_videos_per_prompt: Optional[int]=1, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, pooled_prompt_embeds: Optional[torch.Tensor]=None, prompt_attention_mask: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, attention_kwargs: Optional[Dict[str, Any]]=None, callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None],
    PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], prompt_template: Dict[str, Any]=DEFAULT_PROMPT_TEMPLATE, max_sequence_length: int=256):
        """Examples:"""
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        self.check_inputs(prompt, prompt_2, height, width, prompt_embeds, callback_on_step_end_tensor_inputs, prompt_template)
        self._guidance_scale = guidance_scale
        self._attention_kwargs = attention_kwargs
        self._interrupt = False
        device = self._execution_device
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        prompt_embeds, pooled_prompt_embeds, prompt_attention_mask = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, prompt_template=prompt_template, num_videos_per_prompt=num_videos_per_prompt,
        prompt_embeds=prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, prompt_attention_mask=prompt_attention_mask, device=device, max_sequence_length=max_sequence_length)
        transformer_dtype = self.transformer.dtype
        prompt_embeds = prompt_embeds.to(transformer_dtype)
        prompt_attention_mask = prompt_attention_mask.to(transformer_dtype)
        if pooled_prompt_embeds is not None: pooled_prompt_embeds = pooled_prompt_embeds.to(transformer_dtype)
        sigmas = np.linspace(1.0, 0.0, num_inference_steps + 1)[:-1] if sigmas is None else sigmas
        timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, sigmas=sigmas)
        num_channels_latents = self.transformer.config.in_channels
        num_latent_frames = (num_frames - 1) // self.vae_scale_factor_temporal + 1
        latents = self.prepare_latents(batch_size * num_videos_per_prompt, num_channels_latents, height, width, num_latent_frames, torch.float32, device, generator, latents)
        guidance = torch.tensor([guidance_scale] * latents.shape[0], dtype=transformer_dtype, device=device) * 1000.0
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        self._num_timesteps = len(timesteps)
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = latents.to(transformer_dtype)
                timestep = t.expand(latents.shape[0]).to(latents.dtype)
                noise_pred = self.transformer(hidden_states=latent_model_input, timestep=timestep, encoder_hidden_states=prompt_embeds, encoder_attention_mask=prompt_attention_mask,
                pooled_projections=pooled_prompt_embeds, guidance=guidance, attention_kwargs=attention_kwargs, return_dict=False)[0]
                latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0): progress_bar.update()
        if not output_type == 'latent':
            latents = latents.to(self.vae.dtype) / self.vae.config.scaling_factor
            video = self.vae.decode(latents, return_dict=False)[0]
            video = self.video_processor.postprocess_video(video, output_type=output_type)
        else: video = latents
        self.maybe_free_model_hooks()
        if not return_dict: return (video,)
        return HunyuanVideoPipelineOutput(frames=video)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
