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
from sapiens_transformers import ClapFeatureExtractor, ClapModel, GPT2Model, RobertaTokenizer, RobertaTokenizerFast, SpeechT5HifiGan, T5EncoderModel, T5Tokenizer, T5TokenizerFast, VitsModel, VitsTokenizer
from ...models import AutoencoderKL
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import is_sapiens_accelerator_available, is_sapiens_accelerator_version, is_librosa_available, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import AudioPipelineOutput, DiffusionPipeline
from .modeling_audioldm2 import AudioLDM2ProjectionModel, AudioLDM2UNet2DConditionModel
if is_librosa_available(): import librosa
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import scipy\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AudioLDM2Pipeline\n\n        >>> repo_id = "cvssp/audioldm2"\n        >>> pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n\n        >>> # define the prompts\n        >>> prompt = "The sound of a hammer hitting a wooden surface."\n        >>> negative_prompt = "Low quality."\n\n        >>> # set the seed for generator\n        >>> generator = torch.Generator("cuda").manual_seed(0)\n\n        >>> # run the generation\n        >>> audio = pipe(\n        ...     prompt,\n        ...     negative_prompt=negative_prompt,\n        ...     num_inference_steps=200,\n        ...     audio_length_in_s=10.0,\n        ...     num_waveforms_per_prompt=3,\n        ...     generator=generator,\n        ... ).audios\n\n        >>> # save the best audio sample (index 0) as a .wav file\n        >>> scipy.io.wavfile.write("techno.wav", rate=16000, data=audio[0])\n        ```\n        ```\n        #Using AudioLDM2 for Text To Speech\n        >>> import scipy\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import AudioLDM2Pipeline\n\n        >>> repo_id = "anhnct/audioldm2_gigaspeech"\n        >>> pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)\n        >>> pipe = pipe.to("cuda")\n\n        >>> # define the prompts\n        >>> prompt = "A female reporter is speaking"\n        >>> transcript = "wish you have a good day"\n\n        >>> # set the seed for generator\n        >>> generator = torch.Generator("cuda").manual_seed(0)\n\n        >>> # run the generation\n        >>> audio = pipe(\n        ...     prompt,\n        ...     transcription=transcript,\n        ...     num_inference_steps=200,\n        ...     audio_length_in_s=10.0,\n        ...     num_waveforms_per_prompt=2,\n        ...     generator=generator,\n        ...     max_new_tokens=512,          #Must set max_new_tokens equa to 512 for TTS\n        ... ).audios\n\n        >>> # save the best audio sample (index 0) as a .wav file\n        >>> scipy.io.wavfile.write("tts.wav", rate=16000, data=audio[0])\n        ```\n'
def prepare_inputs_for_generation(inputs_embeds, attention_mask=None, past_key_values=None, **kwargs):
    if past_key_values is not None: inputs_embeds = inputs_embeds[:, -1:]
    return {'inputs_embeds': inputs_embeds, 'attention_mask': attention_mask, 'past_key_values': past_key_values, 'use_cache': kwargs.get('use_cache')}
class AudioLDM2Pipeline(DiffusionPipeline):
    """Args:"""
    def __init__(self, vae: AutoencoderKL, text_encoder: ClapModel, text_encoder_2: Union[T5EncoderModel, VitsModel], projection_model: AudioLDM2ProjectionModel, language_model: GPT2Model,
    tokenizer: Union[RobertaTokenizer, RobertaTokenizerFast], tokenizer_2: Union[T5Tokenizer, T5TokenizerFast, VitsTokenizer], feature_extractor: ClapFeatureExtractor, unet: AudioLDM2UNet2DConditionModel,
    scheduler: KarrasDiffusionSchedulers, vocoder: SpeechT5HifiGan):
        super().__init__()
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, projection_model=projection_model, language_model=language_model, tokenizer=tokenizer,
        tokenizer_2=tokenizer_2, feature_extractor=feature_extractor, unet=unet, scheduler=scheduler, vocoder=vocoder)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
    def enable_vae_slicing(self): self.vae.enable_slicing()
    def disable_vae_slicing(self): self.vae.disable_slicing()
    def enable_model_cpu_offload(self, gpu_id=0):
        if is_sapiens_accelerator_available() and is_sapiens_accelerator_version('>=', '0.17.0.dev0'): from sapiens_accelerator import cpu_offload_with_hook
        else: raise ImportError('`enable_model_cpu_offload` requires `sapiens_accelerator v0.17.0` or higher.')
        device = torch.device(f'cuda:{gpu_id}')
        if self.device.type != 'cpu':
            self.to('cpu', silence_dtype_warnings=True)
            torch.cuda.empty_cache()
        model_sequence = [self.text_encoder.text_model, self.text_encoder.text_projection, self.text_encoder_2, self.projection_model, self.language_model, self.unet, self.vae, self.vocoder, self.text_encoder]
        hook = None
        for cpu_offloaded_model in model_sequence: _, hook = cpu_offload_with_hook(cpu_offloaded_model, device, prev_module_hook=hook)
        self.final_offload_hook = hook
    def generate_language_model(self, inputs_embeds: torch.Tensor=None, max_new_tokens: int=8, **model_kwargs):
        max_new_tokens = max_new_tokens if max_new_tokens is not None else self.language_model.config.max_new_tokens
        model_kwargs = self.language_model._get_initial_cache_position(inputs_embeds, model_kwargs)
        for _ in range(max_new_tokens):
            model_inputs = prepare_inputs_for_generation(inputs_embeds, **model_kwargs)
            output = self.language_model(**model_inputs, return_dict=True)
            next_hidden_states = output.last_hidden_state
            inputs_embeds = torch.cat([inputs_embeds, next_hidden_states[:, -1:, :]], dim=1)
            model_kwargs = self.language_model._update_model_kwargs_for_generation(output, model_kwargs)
        return inputs_embeds[:, -max_new_tokens:, :]
    def encode_prompt(self, prompt, device, num_waveforms_per_prompt, do_classifier_free_guidance, transcription=None, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, generated_prompt_embeds: Optional[torch.Tensor]=None, negative_generated_prompt_embeds: Optional[torch.Tensor]=None,
    attention_mask: Optional[torch.LongTensor]=None, negative_attention_mask: Optional[torch.LongTensor]=None, max_new_tokens: Optional[int]=None):
        """Returns:"""
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        tokenizers = [self.tokenizer, self.tokenizer_2]
        is_vits_text_encoder = isinstance(self.text_encoder_2, VitsModel)
        if is_vits_text_encoder: text_encoders = [self.text_encoder, self.text_encoder_2.text_encoder]
        else: text_encoders = [self.text_encoder, self.text_encoder_2]
        if prompt_embeds is None:
            prompt_embeds_list = []
            attention_mask_list = []
            for tokenizer, text_encoder in zip(tokenizers, text_encoders):
                use_prompt = isinstance(tokenizer, (RobertaTokenizer, RobertaTokenizerFast, T5Tokenizer, T5TokenizerFast))
                text_inputs = tokenizer(prompt if use_prompt else transcription, padding='max_length' if isinstance(tokenizer, (RobertaTokenizer, RobertaTokenizerFast,
                VitsTokenizer)) else True, max_length=tokenizer.model_max_length, truncation=True, return_tensors='pt')
                text_input_ids = text_inputs.input_ids
                attention_mask = text_inputs.attention_mask
                untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
                if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids.to(device)
                attention_mask = attention_mask.to(device)
                if text_encoder.config.model_type == 'clap':
                    prompt_embeds = text_encoder.get_text_features(text_input_ids, attention_mask=attention_mask)
                    prompt_embeds = prompt_embeds[:, None, :]
                    attention_mask = attention_mask.new_ones((batch_size, 1))
                elif is_vits_text_encoder:
                    for text_input_id, text_attention_mask in zip(text_input_ids, attention_mask):
                        for idx, phoneme_id in enumerate(text_input_id):
                            if phoneme_id == 0:
                                text_input_id[idx] = 182
                                text_attention_mask[idx] = 1
                                break
                    prompt_embeds = text_encoder(text_input_ids, attention_mask=attention_mask, padding_mask=attention_mask.unsqueeze(-1))
                    prompt_embeds = prompt_embeds[0]
                else:
                    prompt_embeds = text_encoder(text_input_ids, attention_mask=attention_mask)
                    prompt_embeds = prompt_embeds[0]
                prompt_embeds_list.append(prompt_embeds)
                attention_mask_list.append(attention_mask)
            projection_output = self.projection_model(hidden_states=prompt_embeds_list[0], hidden_states_1=prompt_embeds_list[1], attention_mask=attention_mask_list[0], attention_mask_1=attention_mask_list[1])
            projected_prompt_embeds = projection_output.hidden_states
            projected_attention_mask = projection_output.attention_mask
            generated_prompt_embeds = self.generate_language_model(projected_prompt_embeds, attention_mask=projected_attention_mask, max_new_tokens=max_new_tokens)
        prompt_embeds = prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
        attention_mask = attention_mask.to(device=device) if attention_mask is not None else torch.ones(prompt_embeds.shape[:2], dtype=torch.long, device=device)
        generated_prompt_embeds = generated_prompt_embeds.to(dtype=self.language_model.dtype, device=device)
        bs_embed, seq_len, hidden_size = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_waveforms_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_waveforms_per_prompt, seq_len, hidden_size)
        attention_mask = attention_mask.repeat(1, num_waveforms_per_prompt)
        attention_mask = attention_mask.view(bs_embed * num_waveforms_per_prompt, seq_len)
        bs_embed, seq_len, hidden_size = generated_prompt_embeds.shape
        generated_prompt_embeds = generated_prompt_embeds.repeat(1, num_waveforms_per_prompt, 1)
        generated_prompt_embeds = generated_prompt_embeds.view(bs_embed * num_waveforms_per_prompt, seq_len, hidden_size)
        if do_classifier_free_guidance and negative_prompt_embeds is None:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            negative_prompt_embeds_list = []
            negative_attention_mask_list = []
            max_length = prompt_embeds.shape[1]
            for tokenizer, text_encoder in zip(tokenizers, text_encoders):
                uncond_input = tokenizer(uncond_tokens, padding='max_length', max_length=tokenizer.model_max_length if isinstance(tokenizer, (RobertaTokenizer,
                RobertaTokenizerFast, VitsTokenizer)) else max_length, truncation=True, return_tensors='pt')
                uncond_input_ids = uncond_input.input_ids.to(device)
                negative_attention_mask = uncond_input.attention_mask.to(device)
                if text_encoder.config.model_type == 'clap':
                    negative_prompt_embeds = text_encoder.get_text_features(uncond_input_ids, attention_mask=negative_attention_mask)
                    negative_prompt_embeds = negative_prompt_embeds[:, None, :]
                    negative_attention_mask = negative_attention_mask.new_ones((batch_size, 1))
                elif is_vits_text_encoder:
                    negative_prompt_embeds = torch.zeros(batch_size, tokenizer.model_max_length, text_encoder.config.hidden_size).to(dtype=self.text_encoder_2.dtype, device=device)
                    negative_attention_mask = torch.zeros(batch_size, tokenizer.model_max_length).to(dtype=self.text_encoder_2.dtype, device=device)
                else:
                    negative_prompt_embeds = text_encoder(uncond_input_ids, attention_mask=negative_attention_mask)
                    negative_prompt_embeds = negative_prompt_embeds[0]
                negative_prompt_embeds_list.append(negative_prompt_embeds)
                negative_attention_mask_list.append(negative_attention_mask)
            projection_output = self.projection_model(hidden_states=negative_prompt_embeds_list[0], hidden_states_1=negative_prompt_embeds_list[1],
            attention_mask=negative_attention_mask_list[0], attention_mask_1=negative_attention_mask_list[1])
            negative_projected_prompt_embeds = projection_output.hidden_states
            negative_projected_attention_mask = projection_output.attention_mask
            negative_generated_prompt_embeds = self.generate_language_model(negative_projected_prompt_embeds, attention_mask=negative_projected_attention_mask, max_new_tokens=max_new_tokens)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
            negative_attention_mask = negative_attention_mask.to(device=device) if negative_attention_mask is not None else torch.ones(negative_prompt_embeds.shape[:2], dtype=torch.long, device=device)
            negative_generated_prompt_embeds = negative_generated_prompt_embeds.to(dtype=self.language_model.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_waveforms_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_waveforms_per_prompt, seq_len, -1)
            negative_attention_mask = negative_attention_mask.repeat(1, num_waveforms_per_prompt)
            negative_attention_mask = negative_attention_mask.view(batch_size * num_waveforms_per_prompt, seq_len)
            seq_len = negative_generated_prompt_embeds.shape[1]
            negative_generated_prompt_embeds = negative_generated_prompt_embeds.repeat(1, num_waveforms_per_prompt, 1)
            negative_generated_prompt_embeds = negative_generated_prompt_embeds.view(batch_size * num_waveforms_per_prompt, seq_len, -1)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            attention_mask = torch.cat([negative_attention_mask, attention_mask])
            generated_prompt_embeds = torch.cat([negative_generated_prompt_embeds, generated_prompt_embeds])
        return (prompt_embeds, attention_mask, generated_prompt_embeds)
    def mel_spectrogram_to_waveform(self, mel_spectrogram):
        if mel_spectrogram.dim() == 4: mel_spectrogram = mel_spectrogram.squeeze(1)
        waveform = self.vocoder(mel_spectrogram)
        waveform = waveform.cpu().float()
        return waveform
    def score_waveforms(self, text, audio, num_waveforms_per_prompt, device, dtype):
        if not is_librosa_available(): return audio
        inputs = self.tokenizer(text, return_tensors='pt', padding=True)
        resampled_audio = librosa.resample(audio.numpy(), orig_sr=self.vocoder.config.sampling_rate, target_sr=self.feature_extractor.sampling_rate)
        inputs['input_features'] = self.feature_extractor(list(resampled_audio), return_tensors='pt', sampling_rate=self.feature_extractor.sampling_rate).input_features.type(dtype)
        inputs = inputs.to(device)
        logits_per_text = self.text_encoder(**inputs).logits_per_text
        indices = torch.argsort(logits_per_text, dim=1, descending=True)[:, :num_waveforms_per_prompt]
        audio = torch.index_select(audio, 0, indices.reshape(-1).cpu())
        return audio
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, audio_length_in_s, vocoder_upsample_factor, callback_steps, transcription=None, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, generated_prompt_embeds=None,
    negative_generated_prompt_embeds=None, attention_mask=None, negative_attention_mask=None):
        min_audio_length_in_s = vocoder_upsample_factor * self.vae_scale_factor
        if audio_length_in_s < min_audio_length_in_s: raise ValueError(f'`audio_length_in_s` has to be a positive value greater than or equal to {min_audio_length_in_s}, but is {audio_length_in_s}.')
        if self.vocoder.config.model_in_dim % self.vae_scale_factor != 0: raise ValueError(f"The number of frequency bins in the vocoder's log-mel spectrogram has to be divisible by the VAE scale factor, but got {self.vocoder.config.model_in_dim} bins and a scale factor of {self.vae_scale_factor}.")
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and (prompt_embeds is None or generated_prompt_embeds is None): raise ValueError('Provide either `prompt`, or `prompt_embeds` and `generated_prompt_embeds`. Cannot leave `prompt` undefined without specifying both `prompt_embeds` and `generated_prompt_embeds`.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_embeds is not None and negative_generated_prompt_embeds is None: raise ValueError('Cannot forward `negative_prompt_embeds` without `negative_generated_prompt_embeds`. Ensure thatboth arguments are specified')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
            if attention_mask is not None and attention_mask.shape != prompt_embeds.shape[:2]: raise ValueError(f'`attention_mask should have the same batch size and sequence length as `prompt_embeds`, but got:`attention_mask: {attention_mask.shape} != `prompt_embeds` {prompt_embeds.shape}')
        if transcription is None:
            if self.text_encoder_2.config.model_type == 'vits': raise ValueError('Cannot forward without transcription. Please make sure to have transcription')
        elif transcription is not None and (not isinstance(transcription, str) and (not isinstance(transcription, list))): raise ValueError(f'`transcription` has to be of type `str` or `list` but is {type(transcription)}')
        if generated_prompt_embeds is not None and negative_generated_prompt_embeds is not None:
            if generated_prompt_embeds.shape != negative_generated_prompt_embeds.shape: raise ValueError(f'`generated_prompt_embeds` and `negative_generated_prompt_embeds` must have the same shape when passed directly, but got: `generated_prompt_embeds` {generated_prompt_embeds.shape} != `negative_generated_prompt_embeds` {negative_generated_prompt_embeds.shape}.')
            if negative_attention_mask is not None and negative_attention_mask.shape != negative_prompt_embeds.shape[:2]: raise ValueError(f'`attention_mask should have the same batch size and sequence length as `prompt_embeds`, but got:`attention_mask: {negative_attention_mask.shape} != `prompt_embeds` {negative_prompt_embeds.shape}')
    def prepare_latents(self, batch_size, num_channels_latents, height, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(self.vocoder.config.model_in_dim) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, transcription: Union[str, List[str]]=None, audio_length_in_s: Optional[float]=None, num_inference_steps: int=200, guidance_scale: float=3.5,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_waveforms_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None, generated_prompt_embeds: Optional[torch.Tensor]=None,
    negative_generated_prompt_embeds: Optional[torch.Tensor]=None, attention_mask: Optional[torch.LongTensor]=None, negative_attention_mask: Optional[torch.LongTensor]=None, max_new_tokens: Optional[int]=None,
    return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: Optional[int]=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, output_type: Optional[str]='np'):
        """Examples:"""
        vocoder_upsample_factor = np.prod(self.vocoder.config.upsample_rates) / self.vocoder.config.sampling_rate
        if audio_length_in_s is None: audio_length_in_s = self.unet.config.sample_size * self.vae_scale_factor * vocoder_upsample_factor
        height = int(audio_length_in_s / vocoder_upsample_factor)
        original_waveform_length = int(audio_length_in_s * self.vocoder.config.sampling_rate)
        if height % self.vae_scale_factor != 0: height = int(np.ceil(height / self.vae_scale_factor)) * self.vae_scale_factor
        self.check_inputs(prompt, audio_length_in_s, vocoder_upsample_factor, callback_steps, transcription, negative_prompt, prompt_embeds, negative_prompt_embeds,
        generated_prompt_embeds, negative_generated_prompt_embeds, attention_mask, negative_attention_mask)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, attention_mask, generated_prompt_embeds = self.encode_prompt(prompt, device, num_waveforms_per_prompt, do_classifier_free_guidance, transcription, negative_prompt, prompt_embeds=prompt_embeds,
        negative_prompt_embeds=negative_prompt_embeds, generated_prompt_embeds=generated_prompt_embeds, negative_generated_prompt_embeds=negative_generated_prompt_embeds, attention_mask=attention_mask,
        negative_attention_mask=negative_attention_mask, max_new_tokens=max_new_tokens)
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
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=generated_prompt_embeds, encoder_hidden_states_1=prompt_embeds, encoder_attention_mask_1=attention_mask, return_dict=False)[0]
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        self.maybe_free_model_hooks()
        if not output_type == 'latent':
            latents = 1 / self.vae.config.scaling_factor * latents
            mel_spectrogram = self.vae.decode(latents).sample
        else: return AudioPipelineOutput(audios=latents)
        audio = self.mel_spectrogram_to_waveform(mel_spectrogram)
        audio = audio[:, :original_waveform_length]
        if num_waveforms_per_prompt > 1 and prompt is not None: audio = self.score_waveforms(text=prompt, audio=audio, num_waveforms_per_prompt=num_waveforms_per_prompt, device=device, dtype=prompt_embeds.dtype)
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
