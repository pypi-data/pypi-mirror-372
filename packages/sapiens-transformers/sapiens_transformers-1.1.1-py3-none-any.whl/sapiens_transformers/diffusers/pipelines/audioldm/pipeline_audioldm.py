'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np
import torch
import torch.nn.functional as F
from sapiens_transformers import ClapTextModelWithProjection, RobertaTokenizer, RobertaTokenizerFast, SpeechT5HifiGan
from ...models import AutoencoderKL, UNet2DConditionModel
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import AudioPipelineOutput, DiffusionPipeline, StableDiffusionMixin
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers import AudioLDMPipeline\n        >>> import torch\n        >>> import scipy\n\n        >>> repo_id = "cvssp/audioldm-s-full-v2"\n        >>> pipe = AudioLDMPipeline.from_pretrained(repo_id, torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n\n        >>> prompt = "Techno music with a strong, upbeat tempo and high melodic riffs"\n        >>> audio = pipe(prompt, num_inference_steps=10, audio_length_in_s=5.0).audios[0]\n\n        >>> # save the audio sample as a .wav file\n        >>> scipy.io.wavfile.write("techno.wav", rate=16000, data=audio)\n        ```\n'
class AudioLDMPipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    def __init__(self, vae: AutoencoderKL, text_encoder: ClapTextModelWithProjection, tokenizer: Union[RobertaTokenizer, RobertaTokenizerFast],
    unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers, vocoder: SpeechT5HifiGan):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, vocoder=vocoder)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
    def _encode_prompt(self, prompt, device, num_waveforms_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None):
        """Args:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            attention_mask = text_inputs.attention_mask
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask.to(device))
            prompt_embeds = prompt_embeds.text_embeds
            prompt_embeds = F.normalize(prompt_embeds, dim=-1)
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
        bs_embed, seq_len = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_waveforms_per_prompt)
        prompt_embeds = prompt_embeds.view(bs_embed * num_waveforms_per_prompt, seq_len)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            uncond_input_ids = uncond_input.input_ids.to(device)
            attention_mask = uncond_input.attention_mask.to(device)
            negative_prompt_embeds = self.text_encoder(uncond_input_ids, attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds.text_embeds
            negative_prompt_embeds = F.normalize(negative_prompt_embeds, dim=-1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_waveforms_per_prompt)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_waveforms_per_prompt, seq_len)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        return prompt_embeds
    def decode_latents(self, latents):
        latents = 1 / self.vae.config.scaling_factor * latents
        mel_spectrogram = self.vae.decode(latents).sample
        return mel_spectrogram
    def mel_spectrogram_to_waveform(self, mel_spectrogram):
        if mel_spectrogram.dim() == 4: mel_spectrogram = mel_spectrogram.squeeze(1)
        waveform = self.vocoder(mel_spectrogram)
        waveform = waveform.cpu().float()
        return waveform
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, audio_length_in_s, vocoder_upsample_factor, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None):
        min_audio_length_in_s = vocoder_upsample_factor * self.vae_scale_factor
        if audio_length_in_s < min_audio_length_in_s: raise ValueError(f'`audio_length_in_s` has to be a positive value greater than or equal to {min_audio_length_in_s}, but is {audio_length_in_s}.')
        if self.vocoder.config.model_in_dim % self.vae_scale_factor != 0: raise ValueError(f"The number of frequency bins in the vocoder's log-mel spectrogram has to be divisible by the VAE scale factor, but got {self.vocoder.config.model_in_dim} bins and a scale factor of {self.vae_scale_factor}.")
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(self.vocoder.config.model_in_dim) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, audio_length_in_s: Optional[float]=None, num_inference_steps: int=10, guidance_scale: float=2.5, negative_prompt: Optional[Union[str,
    List[str]]]=None, num_waveforms_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None,
    prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None,
    callback_steps: Optional[int]=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, output_type: Optional[str]='np'):
        """Examples:"""
        vocoder_upsample_factor = np.prod(self.vocoder.config.upsample_rates) / self.vocoder.config.sampling_rate
        if audio_length_in_s is None: audio_length_in_s = self.unet.config.sample_size * self.vae_scale_factor * vocoder_upsample_factor
        height = int(audio_length_in_s / vocoder_upsample_factor)
        original_waveform_length = int(audio_length_in_s * self.vocoder.config.sampling_rate)
        if height % self.vae_scale_factor != 0: height = int(np.ceil(height / self.vae_scale_factor)) * self.vae_scale_factor
        self.check_inputs(prompt, audio_length_in_s, vocoder_upsample_factor, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds = self._encode_prompt(prompt, device, num_waveforms_per_prompt, do_classifier_free_guidance, negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds)
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_waveforms_per_prompt, num_channels_latents, height, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=None, class_labels=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        mel_spectrogram = self.decode_latents(latents)
        audio = self.mel_spectrogram_to_waveform(mel_spectrogram)
        audio = audio[:, :original_waveform_length]
        if output_type == 'np': audio = audio.numpy()
        if not return_dict: return (audio,)
        return AudioPipelineOutput(audios=audio)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
