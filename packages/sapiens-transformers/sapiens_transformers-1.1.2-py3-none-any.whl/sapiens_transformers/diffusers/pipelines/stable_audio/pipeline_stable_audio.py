'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Callable, List, Optional, Union
import torch
from sapiens_transformers import T5EncoderModel, T5Tokenizer, T5TokenizerFast
from ...models import AutoencoderOobleck, StableAudioDiTModel
from ...models.embeddings import get_1d_rotary_pos_embed
from ...schedulers import EDMDPMSolverMultistepScheduler
from ...utils import is_torch_xla_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import AudioPipelineOutput, DiffusionPipeline
from .modeling_stable_audio import StableAudioProjectionModel
if is_torch_xla_available():
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
else: XLA_AVAILABLE = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import scipy\n        >>> import torch\n        >>> import soundfile as sf\n        >>> from sapiens_transformers.diffusers import StableAudioPipeline\n\n        >>> repo_id = "stabilityai/stable-audio-open-1.0"\n        >>> pipe = StableAudioPipeline.from_pretrained(repo_id, torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n\n        >>> # define the prompts\n        >>> prompt = "The sound of a hammer hitting a wooden surface."\n        >>> negative_prompt = "Low quality."\n\n        >>> # set the seed for generator\n        >>> generator = torch.Generator("cuda").manual_seed(0)\n\n        >>> # run the generation\n        >>> audio = pipe(\n        ...     prompt,\n        ...     negative_prompt=negative_prompt,\n        ...     num_inference_steps=200,\n        ...     audio_end_in_s=10.0,\n        ...     num_waveforms_per_prompt=3,\n        ...     generator=generator,\n        ... ).audios\n\n        >>> output = audio[0].T.float().cpu().numpy()\n        >>> sf.write("hammer.wav", output, pipe.vae.sampling_rate)\n        ```\n'
class StableAudioPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->projection_model->transformer->vae'
    def __init__(self, vae: AutoencoderOobleck, text_encoder: T5EncoderModel, projection_model: StableAudioProjectionModel, tokenizer: Union[T5Tokenizer,
    T5TokenizerFast], transformer: StableAudioDiTModel, scheduler: EDMDPMSolverMultistepScheduler):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, projection_model=projection_model, tokenizer=tokenizer, transformer=transformer, scheduler=scheduler)
        self.rotary_embed_dim = self.transformer.config.attention_head_dim // 2
    def enable_vae_slicing(self): self.vae.enable_slicing()
    def disable_vae_slicing(self): self.vae.disable_slicing()
    def encode_prompt(self, prompt, device, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, attention_mask: Optional[torch.LongTensor]=None, negative_attention_mask: Optional[torch.LongTensor]=None):
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            attention_mask = text_inputs.attention_mask
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            text_input_ids = text_input_ids.to(device)
            attention_mask = attention_mask.to(device)
            self.text_encoder.eval()
            prompt_embeds = self.text_encoder(text_input_ids, attention_mask=attention_mask)
            prompt_embeds = prompt_embeds[0]
        if do_classifier_free_guidance and negative_prompt is not None:
            uncond_tokens: List[str]
            if type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            uncond_input_ids = uncond_input.input_ids.to(device)
            negative_attention_mask = uncond_input.attention_mask.to(device)
            self.text_encoder.eval()
            negative_prompt_embeds = self.text_encoder(uncond_input_ids, attention_mask=negative_attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
            if negative_attention_mask is not None: negative_prompt_embeds = torch.where(negative_attention_mask.to(torch.bool).unsqueeze(2), negative_prompt_embeds, 0.0)
        if do_classifier_free_guidance and negative_prompt_embeds is not None:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            if attention_mask is not None and negative_attention_mask is None: negative_attention_mask = torch.ones_like(attention_mask)
            elif attention_mask is None and negative_attention_mask is not None: attention_mask = torch.ones_like(negative_attention_mask)
            if attention_mask is not None: attention_mask = torch.cat([negative_attention_mask, attention_mask])
        prompt_embeds = self.projection_model(text_hidden_states=prompt_embeds).text_hidden_states
        if attention_mask is not None:
            prompt_embeds = prompt_embeds * attention_mask.unsqueeze(-1).to(prompt_embeds.dtype)
            prompt_embeds = prompt_embeds * attention_mask.unsqueeze(-1).to(prompt_embeds.dtype)
        return prompt_embeds
    def encode_duration(self, audio_start_in_s, audio_end_in_s, device, do_classifier_free_guidance, batch_size):
        audio_start_in_s = audio_start_in_s if isinstance(audio_start_in_s, list) else [audio_start_in_s]
        audio_end_in_s = audio_end_in_s if isinstance(audio_end_in_s, list) else [audio_end_in_s]
        if len(audio_start_in_s) == 1: audio_start_in_s = audio_start_in_s * batch_size
        if len(audio_end_in_s) == 1: audio_end_in_s = audio_end_in_s * batch_size
        audio_start_in_s = [float(x) for x in audio_start_in_s]
        audio_start_in_s = torch.tensor(audio_start_in_s).to(device)
        audio_end_in_s = [float(x) for x in audio_end_in_s]
        audio_end_in_s = torch.tensor(audio_end_in_s).to(device)
        projection_output = self.projection_model(start_seconds=audio_start_in_s, end_seconds=audio_end_in_s)
        seconds_start_hidden_states = projection_output.seconds_start_hidden_states
        seconds_end_hidden_states = projection_output.seconds_end_hidden_states
        if do_classifier_free_guidance:
            seconds_start_hidden_states = torch.cat([seconds_start_hidden_states, seconds_start_hidden_states], dim=0)
            seconds_end_hidden_states = torch.cat([seconds_end_hidden_states, seconds_end_hidden_states], dim=0)
        return (seconds_start_hidden_states, seconds_end_hidden_states)
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, audio_start_in_s, audio_end_in_s, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None,
    attention_mask=None, negative_attention_mask=None, initial_audio_waveforms=None, initial_audio_sampling_rate=None):
        if audio_end_in_s < audio_start_in_s: raise ValueError(f"`audio_end_in_s={audio_end_in_s}' must be higher than 'audio_start_in_s={audio_start_in_s}` but ")
        if audio_start_in_s < self.projection_model.config.min_value or audio_start_in_s > self.projection_model.config.max_value: raise ValueError(f'`audio_start_in_s` must be greater than or equal to {self.projection_model.config.min_value}, and lower than or equal to {self.projection_model.config.max_value} but is {audio_start_in_s}.')
        if audio_end_in_s < self.projection_model.config.min_value or audio_end_in_s > self.projection_model.config.max_value: raise ValueError(f'`audio_end_in_s` must be greater than or equal to {self.projection_model.config.min_value}, and lower than or equal to {self.projection_model.config.max_value} but is {audio_end_in_s}.')
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt`, or `prompt_embeds`. Cannot leave`prompt` undefined without specifying `prompt_embeds`.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if attention_mask is not None and attention_mask.shape != prompt_embeds.shape[:2]: raise ValueError(f'`attention_mask should have the same batch size and sequence length as `prompt_embeds`, but got:`attention_mask: {attention_mask.shape} != `prompt_embeds` {prompt_embeds.shape}')
        if initial_audio_sampling_rate is None and initial_audio_waveforms is not None: raise ValueError("`initial_audio_waveforms' is provided but the sampling rate is not. Make sure to pass `initial_audio_sampling_rate`.")
        if initial_audio_sampling_rate is not None and initial_audio_sampling_rate != self.vae.sampling_rate: raise ValueError(f"`initial_audio_sampling_rate` must be {self.vae.hop_length}' but is `{initial_audio_sampling_rate}`.Make sure to resample the `initial_audio_waveforms` and to correct the sampling rate. ")
    def prepare_latents(self, batch_size, num_channels_vae, sample_size, dtype, device, generator, latents=None, initial_audio_waveforms=None, num_waveforms_per_prompt=None, audio_channels=None):
        shape = (batch_size, num_channels_vae, sample_size)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        if initial_audio_waveforms is not None:
            if initial_audio_waveforms.ndim == 2: initial_audio_waveforms = initial_audio_waveforms.unsqueeze(1)
            elif initial_audio_waveforms.ndim != 3: raise ValueError(f'`initial_audio_waveforms` must be of shape `(batch_size, num_channels, audio_length)` or `(batch_size, audio_length)` but has `{initial_audio_waveforms.ndim}` dimensions')
            audio_vae_length = int(self.transformer.config.sample_size) * self.vae.hop_length
            audio_shape = (batch_size // num_waveforms_per_prompt, audio_channels, audio_vae_length)
            if initial_audio_waveforms.shape[1] == 1 and audio_channels == 2: initial_audio_waveforms = initial_audio_waveforms.repeat(1, 2, 1)
            elif initial_audio_waveforms.shape[1] == 2 and audio_channels == 1: initial_audio_waveforms = initial_audio_waveforms.mean(1, keepdim=True)
            if initial_audio_waveforms.shape[:2] != audio_shape[:2]: raise ValueError(f'`initial_audio_waveforms` must be of shape `(batch_size, num_channels, audio_length)` or `(batch_size, audio_length)` but is of shape `{initial_audio_waveforms.shape}`')
            audio_length = initial_audio_waveforms.shape[-1]
            audio = initial_audio_waveforms.new_zeros(audio_shape)
            audio[:, :, :min(audio_length, audio_vae_length)] = initial_audio_waveforms[:, :, :audio_vae_length]
            encoded_audio = self.vae.encode(audio).latent_dist.sample(generator)
            encoded_audio = encoded_audio.repeat((num_waveforms_per_prompt, 1, 1))
            latents = encoded_audio + latents
        return latents
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, audio_end_in_s: Optional[float]=None, audio_start_in_s: Optional[float]=0.0, num_inference_steps: int=100, guidance_scale: float=7.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_waveforms_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, initial_audio_waveforms: Optional[torch.Tensor]=None, initial_audio_sampling_rate: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, attention_mask: Optional[torch.LongTensor]=None, negative_attention_mask: Optional[torch.LongTensor]=None, return_dict: bool=True,
    callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: Optional[int]=1, output_type: Optional[str]='pt'):
        """Examples:"""
        downsample_ratio = self.vae.hop_length
        max_audio_length_in_s = self.transformer.config.sample_size * downsample_ratio / self.vae.config.sampling_rate
        if audio_end_in_s is None: audio_end_in_s = max_audio_length_in_s
        if audio_end_in_s - audio_start_in_s > max_audio_length_in_s: raise ValueError(f"The total audio length requested ({audio_end_in_s - audio_start_in_s}s) is longer than the model maximum possible length ({max_audio_length_in_s}). Make sure that 'audio_end_in_s-audio_start_in_s<={max_audio_length_in_s}'.")
        waveform_start = int(audio_start_in_s * self.vae.config.sampling_rate)
        waveform_end = int(audio_end_in_s * self.vae.config.sampling_rate)
        waveform_length = int(self.transformer.config.sample_size)
        self.check_inputs(prompt, audio_start_in_s, audio_end_in_s, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds, attention_mask,
        negative_attention_mask, initial_audio_waveforms, initial_audio_sampling_rate)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds = self.encode_prompt(prompt, device, do_classifier_free_guidance, negative_prompt, prompt_embeds, negative_prompt_embeds, attention_mask, negative_attention_mask)
        seconds_start_hidden_states, seconds_end_hidden_states = self.encode_duration(audio_start_in_s, audio_end_in_s, device,
        do_classifier_free_guidance and (negative_prompt is not None or negative_prompt_embeds is not None), batch_size)
        text_audio_duration_embeds = torch.cat([prompt_embeds, seconds_start_hidden_states, seconds_end_hidden_states], dim=1)
        audio_duration_embeds = torch.cat([seconds_start_hidden_states, seconds_end_hidden_states], dim=2)
        if do_classifier_free_guidance and negative_prompt_embeds is None and (negative_prompt is None):
            negative_text_audio_duration_embeds = torch.zeros_like(text_audio_duration_embeds, device=text_audio_duration_embeds.device)
            text_audio_duration_embeds = torch.cat([negative_text_audio_duration_embeds, text_audio_duration_embeds], dim=0)
            audio_duration_embeds = torch.cat([audio_duration_embeds, audio_duration_embeds], dim=0)
        bs_embed, seq_len, hidden_size = text_audio_duration_embeds.shape
        text_audio_duration_embeds = text_audio_duration_embeds.repeat(1, num_waveforms_per_prompt, 1)
        text_audio_duration_embeds = text_audio_duration_embeds.view(bs_embed * num_waveforms_per_prompt, seq_len, hidden_size)
        audio_duration_embeds = audio_duration_embeds.repeat(1, num_waveforms_per_prompt, 1)
        audio_duration_embeds = audio_duration_embeds.view(bs_embed * num_waveforms_per_prompt, -1, audio_duration_embeds.shape[-1])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_vae = self.transformer.config.in_channels
        latents = self.prepare_latents(batch_size * num_waveforms_per_prompt, num_channels_vae, waveform_length, text_audio_duration_embeds.dtype, device, generator,
        latents, initial_audio_waveforms, num_waveforms_per_prompt, audio_channels=self.vae.config.audio_channels)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        rotary_embedding = get_1d_rotary_pos_embed(self.rotary_embed_dim, latents.shape[2] + audio_duration_embeds.shape[1], use_real=True, repeat_interleave_real=False)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.transformer(latent_model_input, t.unsqueeze(0), encoder_hidden_states=text_audio_duration_embeds,
                global_hidden_states=audio_duration_embeds, rotary_embedding=rotary_embedding, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
                if XLA_AVAILABLE: xm.mark_step()
        if not output_type == 'latent': audio = self.vae.decode(latents).sample
        else: return AudioPipelineOutput(audios=latents)
        audio = audio[:, :, waveform_start:waveform_end]
        if output_type == 'np': audio = audio.cpu().float().numpy()
        self.maybe_free_model_hooks()
        if not return_dict: return (audio,)
        return AudioPipelineOutput(audios=audio)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
