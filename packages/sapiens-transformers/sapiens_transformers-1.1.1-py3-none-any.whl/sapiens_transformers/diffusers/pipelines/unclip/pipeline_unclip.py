'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import List, Optional, Tuple, Union
import torch
from torch.nn import functional as F
from sapiens_transformers import CLIPTextModelWithProjection, CLIPTokenizer
from sapiens_transformers.models.clip.modeling_clip import CLIPTextModelOutput
from ...models import PriorTransformer, UNet2DConditionModel, UNet2DModel
from ...schedulers import UnCLIPScheduler
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
from .text_proj import UnCLIPTextProjModel
class UnCLIPPipeline(DiffusionPipeline):
    """Args:"""
    _exclude_from_cpu_offload = ['prior']
    prior: PriorTransformer
    decoder: UNet2DConditionModel
    text_proj: UnCLIPTextProjModel
    text_encoder: CLIPTextModelWithProjection
    tokenizer: CLIPTokenizer
    super_res_first: UNet2DModel
    super_res_last: UNet2DModel
    prior_scheduler: UnCLIPScheduler
    decoder_scheduler: UnCLIPScheduler
    super_res_scheduler: UnCLIPScheduler
    model_cpu_offload_seq = 'text_encoder->text_proj->decoder->super_res_first->super_res_last'
    def __init__(self, prior: PriorTransformer, decoder: UNet2DConditionModel, text_encoder: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, text_proj: UnCLIPTextProjModel,
    super_res_first: UNet2DModel, super_res_last: UNet2DModel, prior_scheduler: UnCLIPScheduler, decoder_scheduler: UnCLIPScheduler, super_res_scheduler: UnCLIPScheduler):
        super().__init__()
        self.register_modules(prior=prior, decoder=decoder, text_encoder=text_encoder, tokenizer=tokenizer, text_proj=text_proj, super_res_first=super_res_first, super_res_last=super_res_last,
        prior_scheduler=prior_scheduler, decoder_scheduler=decoder_scheduler, super_res_scheduler=super_res_scheduler)
    def prepare_latents(self, shape, dtype, device, generator, latents, scheduler):
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else:
            if latents.shape != shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {shape}')
            latents = latents.to(device)
        latents = latents * scheduler.init_noise_sigma
        return latents
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, text_model_output: Optional[Union[CLIPTextModelOutput,
    Tuple]]=None, text_attention_mask: Optional[torch.Tensor]=None):
        if text_model_output is None:
            batch_size = len(prompt) if isinstance(prompt, list) else 1
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            text_mask = text_inputs.attention_mask.bool().to(device)
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)):
                removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
                text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
            text_encoder_output = self.text_encoder(text_input_ids.to(device))
            prompt_embeds = text_encoder_output.text_embeds
            text_enc_hid_states = text_encoder_output.last_hidden_state
        else:
            batch_size = text_model_output[0].shape[0]
            prompt_embeds, text_enc_hid_states = (text_model_output[0], text_model_output[1])
            text_mask = text_attention_mask
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        text_enc_hid_states = text_enc_hid_states.repeat_interleave(num_images_per_prompt, dim=0)
        text_mask = text_mask.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            uncond_tokens = [''] * batch_size
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            uncond_text_mask = uncond_input.attention_mask.bool().to(device)
            negative_prompt_embeds_text_encoder_output = self.text_encoder(uncond_input.input_ids.to(device))
            negative_prompt_embeds = negative_prompt_embeds_text_encoder_output.text_embeds
            uncond_text_enc_hid_states = negative_prompt_embeds_text_encoder_output.last_hidden_state
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len)
            seq_len = uncond_text_enc_hid_states.shape[1]
            uncond_text_enc_hid_states = uncond_text_enc_hid_states.repeat(1, num_images_per_prompt, 1)
            uncond_text_enc_hid_states = uncond_text_enc_hid_states.view(batch_size * num_images_per_prompt, seq_len, -1)
            uncond_text_mask = uncond_text_mask.repeat_interleave(num_images_per_prompt, dim=0)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
            text_enc_hid_states = torch.cat([uncond_text_enc_hid_states, text_enc_hid_states])
            text_mask = torch.cat([uncond_text_mask, text_mask])
        return (prompt_embeds, text_enc_hid_states, text_mask)
    @torch.no_grad()
    def __call__(self, prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: int=1, prior_num_inference_steps: int=25, decoder_num_inference_steps: int=25,
    super_res_num_inference_steps: int=7, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, prior_latents: Optional[torch.Tensor]=None,
    decoder_latents: Optional[torch.Tensor]=None, super_res_latents: Optional[torch.Tensor]=None, text_model_output: Optional[Union[CLIPTextModelOutput, Tuple]]=None,
    text_attention_mask: Optional[torch.Tensor]=None, prior_guidance_scale: float=4.0, decoder_guidance_scale: float=8.0, output_type: Optional[str]='pil', return_dict: bool=True):
        """Returns:"""
        if prompt is not None:
            if isinstance(prompt, str): batch_size = 1
            elif isinstance(prompt, list): batch_size = len(prompt)
            else: raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        else: batch_size = text_model_output[0].shape[0]
        device = self._execution_device
        batch_size = batch_size * num_images_per_prompt
        do_classifier_free_guidance = prior_guidance_scale > 1.0 or decoder_guidance_scale > 1.0
        prompt_embeds, text_enc_hid_states, text_mask = self._encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, text_model_output, text_attention_mask)
        self.prior_scheduler.set_timesteps(prior_num_inference_steps, device=device)
        prior_timesteps_tensor = self.prior_scheduler.timesteps
        embedding_dim = self.prior.config.embedding_dim
        prior_latents = self.prepare_latents((batch_size, embedding_dim), prompt_embeds.dtype, device, generator, prior_latents, self.prior_scheduler)
        for i, t in enumerate(self.progress_bar(prior_timesteps_tensor)):
            latent_model_input = torch.cat([prior_latents] * 2) if do_classifier_free_guidance else prior_latents
            predicted_image_embedding = self.prior(latent_model_input, timestep=t, proj_embedding=prompt_embeds,
            encoder_hidden_states=text_enc_hid_states, attention_mask=text_mask).predicted_image_embedding
            if do_classifier_free_guidance:
                predicted_image_embedding_uncond, predicted_image_embedding_text = predicted_image_embedding.chunk(2)
                predicted_image_embedding = predicted_image_embedding_uncond + prior_guidance_scale * (predicted_image_embedding_text - predicted_image_embedding_uncond)
            if i + 1 == prior_timesteps_tensor.shape[0]: prev_timestep = None
            else: prev_timestep = prior_timesteps_tensor[i + 1]
            prior_latents = self.prior_scheduler.step(predicted_image_embedding, timestep=t, sample=prior_latents, generator=generator, prev_timestep=prev_timestep).prev_sample
        prior_latents = self.prior.post_process_latents(prior_latents)
        image_embeddings = prior_latents
        text_enc_hid_states, additive_clip_time_embeddings = self.text_proj(image_embeddings=image_embeddings, prompt_embeds=prompt_embeds,
        text_encoder_hidden_states=text_enc_hid_states, do_classifier_free_guidance=do_classifier_free_guidance)
        if device.type == 'mps':
            text_mask = text_mask.type(torch.int)
            decoder_text_mask = F.pad(text_mask, (self.text_proj.clip_extra_context_tokens, 0), value=1)
            decoder_text_mask = decoder_text_mask.type(torch.bool)
        else: decoder_text_mask = F.pad(text_mask, (self.text_proj.clip_extra_context_tokens, 0), value=True)
        self.decoder_scheduler.set_timesteps(decoder_num_inference_steps, device=device)
        decoder_timesteps_tensor = self.decoder_scheduler.timesteps
        num_channels_latents = self.decoder.config.in_channels
        height = self.decoder.config.sample_size
        width = self.decoder.config.sample_size
        decoder_latents = self.prepare_latents((batch_size, num_channels_latents, height, width), text_enc_hid_states.dtype, device, generator, decoder_latents, self.decoder_scheduler)
        for i, t in enumerate(self.progress_bar(decoder_timesteps_tensor)):
            latent_model_input = torch.cat([decoder_latents] * 2) if do_classifier_free_guidance else decoder_latents
            noise_pred = self.decoder(sample=latent_model_input, timestep=t, encoder_hidden_states=text_enc_hid_states,
            class_labels=additive_clip_time_embeddings, attention_mask=decoder_text_mask).sample
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred_uncond, _ = noise_pred_uncond.split(latent_model_input.shape[1], dim=1)
                noise_pred_text, predicted_variance = noise_pred_text.split(latent_model_input.shape[1], dim=1)
                noise_pred = noise_pred_uncond + decoder_guidance_scale * (noise_pred_text - noise_pred_uncond)
                noise_pred = torch.cat([noise_pred, predicted_variance], dim=1)
            if i + 1 == decoder_timesteps_tensor.shape[0]: prev_timestep = None
            else: prev_timestep = decoder_timesteps_tensor[i + 1]
            decoder_latents = self.decoder_scheduler.step(noise_pred, t, decoder_latents, prev_timestep=prev_timestep, generator=generator).prev_sample
        decoder_latents = decoder_latents.clamp(-1, 1)
        image_small = decoder_latents
        self.super_res_scheduler.set_timesteps(super_res_num_inference_steps, device=device)
        super_res_timesteps_tensor = self.super_res_scheduler.timesteps
        channels = self.super_res_first.config.in_channels // 2
        height = self.super_res_first.config.sample_size
        width = self.super_res_first.config.sample_size
        super_res_latents = self.prepare_latents((batch_size, channels, height, width), image_small.dtype, device, generator, super_res_latents, self.super_res_scheduler)
        if device.type == 'mps': image_upscaled = F.interpolate(image_small, size=[height, width])
        else:
            interpolate_antialias = {}
            if 'antialias' in inspect.signature(F.interpolate).parameters: interpolate_antialias['antialias'] = True
            image_upscaled = F.interpolate(image_small, size=[height, width], mode='bicubic', align_corners=False, **interpolate_antialias)
        for i, t in enumerate(self.progress_bar(super_res_timesteps_tensor)):
            if i == super_res_timesteps_tensor.shape[0] - 1: unet = self.super_res_last
            else: unet = self.super_res_first
            latent_model_input = torch.cat([super_res_latents, image_upscaled], dim=1)
            noise_pred = unet(sample=latent_model_input, timestep=t).sample
            if i + 1 == super_res_timesteps_tensor.shape[0]: prev_timestep = None
            else: prev_timestep = super_res_timesteps_tensor[i + 1]
            super_res_latents = self.super_res_scheduler.step(noise_pred, t, super_res_latents, prev_timestep=prev_timestep, generator=generator).prev_sample
        image = super_res_latents
        self.maybe_free_model_hooks()
        image = image * 0.5 + 0.5
        image = image.clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
