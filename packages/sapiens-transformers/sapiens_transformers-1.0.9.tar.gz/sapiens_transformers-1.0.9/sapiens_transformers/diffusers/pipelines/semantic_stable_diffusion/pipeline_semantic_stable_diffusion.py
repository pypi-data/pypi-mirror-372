'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from itertools import repeat
from typing import Callable, List, Optional, Union
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ...image_processor import VaeImageProcessor
from ...models import AutoencoderKL, UNet2DConditionModel
from ...pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import deprecate
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from .pipeline_output import SemanticStableDiffusionPipelineOutput
class SemanticStableDiffusionPipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers,
    safety_checker: StableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
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
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, callback_steps, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, callback_on_step_end_tensor_inputs=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    @torch.no_grad()
    def __call__(self, prompt: Union[str, List[str]], height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: int=1, eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None,
    callback_steps: int=1, editing_prompt: Optional[Union[str, List[str]]]=None, editing_prompt_embeddings: Optional[torch.Tensor]=None, reverse_editing_direction: Optional[Union[bool,
    List[bool]]]=False, edit_guidance_scale: Optional[Union[float, List[float]]]=5, edit_warmup_steps: Optional[Union[int, List[int]]]=10, edit_cooldown_steps: Optional[Union[int,
    List[int]]]=None, edit_threshold: Optional[Union[float, List[float]]]=0.9, edit_momentum_scale: Optional[float]=0.1, edit_mom_beta: Optional[float]=0.4,
    edit_weights: Optional[List[float]]=None, sem_guidance: Optional[List[torch.Tensor]]=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, callback_steps)
        batch_size = 1 if isinstance(prompt, str) else len(prompt)
        device = self._execution_device
        if editing_prompt:
            enable_edit_guidance = True
            if isinstance(editing_prompt, str): editing_prompt = [editing_prompt]
            enabled_editing_prompts = len(editing_prompt)
        elif editing_prompt_embeddings is not None:
            enable_edit_guidance = True
            enabled_editing_prompts = editing_prompt_embeddings.shape[0]
        else:
            enabled_editing_prompts = 0
            enable_edit_guidance = False
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        if text_input_ids.shape[-1] > self.tokenizer.model_max_length:
            removed_text = self.tokenizer.batch_decode(text_input_ids[:, self.tokenizer.model_max_length:])
            text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
        text_embeddings = self.text_encoder(text_input_ids.to(device))[0]
        bs_embed, seq_len, _ = text_embeddings.shape
        text_embeddings = text_embeddings.repeat(1, num_images_per_prompt, 1)
        text_embeddings = text_embeddings.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if enable_edit_guidance:
            if editing_prompt_embeddings is None:
                edit_concepts_input = self.tokenizer([x for item in editing_prompt for x in repeat(item, batch_size)],
                padding='max_length', max_length=self.tokenizer.model_max_length, return_tensors='pt')
                edit_concepts_input_ids = edit_concepts_input.input_ids
                if edit_concepts_input_ids.shape[-1] > self.tokenizer.model_max_length:
                    removed_text = self.tokenizer.batch_decode(edit_concepts_input_ids[:, self.tokenizer.model_max_length:])
                    edit_concepts_input_ids = edit_concepts_input_ids[:, :self.tokenizer.model_max_length]
                edit_concepts = self.text_encoder(edit_concepts_input_ids.to(device))[0]
            else: edit_concepts = editing_prompt_embeddings.to(device).repeat(batch_size, 1, 1)
            bs_embed_edit, seq_len_edit, _ = edit_concepts.shape
            edit_concepts = edit_concepts.repeat(1, num_images_per_prompt, 1)
            edit_concepts = edit_concepts.view(bs_embed_edit * num_images_per_prompt, seq_len_edit, -1)
        do_classifier_free_guidance = guidance_scale > 1.0
        if do_classifier_free_guidance:
            uncond_tokens: List[str]
            if negative_prompt is None: uncond_tokens = [''] * batch_size
            elif type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif isinstance(negative_prompt, str): uncond_tokens = [negative_prompt]
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = negative_prompt
            max_length = text_input_ids.shape[-1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            uncond_embeddings = self.text_encoder(uncond_input.input_ids.to(device))[0]
            seq_len = uncond_embeddings.shape[1]
            uncond_embeddings = uncond_embeddings.repeat(1, num_images_per_prompt, 1)
            uncond_embeddings = uncond_embeddings.view(batch_size * num_images_per_prompt, seq_len, -1)
            if enable_edit_guidance: text_embeddings = torch.cat([uncond_embeddings, text_embeddings, edit_concepts])
            else: text_embeddings = torch.cat([uncond_embeddings, text_embeddings])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, text_embeddings.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        edit_momentum = None
        self.uncond_estimates = None
        self.text_estimates = None
        self.edit_estimates = None
        self.sem_guidance = None
        for i, t in enumerate(self.progress_bar(timesteps)):
            latent_model_input = torch.cat([latents] * (2 + enabled_editing_prompts)) if do_classifier_free_guidance else latents
            latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample
            if do_classifier_free_guidance:
                noise_pred_out = noise_pred.chunk(2 + enabled_editing_prompts)
                noise_pred_uncond, noise_pred_text = (noise_pred_out[0], noise_pred_out[1])
                noise_pred_edit_concepts = noise_pred_out[2:]
                noise_guidance = guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.uncond_estimates is None: self.uncond_estimates = torch.zeros((num_inference_steps + 1, *noise_pred_uncond.shape))
                self.uncond_estimates[i] = noise_pred_uncond.detach().cpu()
                if self.text_estimates is None: self.text_estimates = torch.zeros((num_inference_steps + 1, *noise_pred_text.shape))
                self.text_estimates[i] = noise_pred_text.detach().cpu()
                if self.edit_estimates is None and enable_edit_guidance: self.edit_estimates = torch.zeros((num_inference_steps + 1,
                len(noise_pred_edit_concepts), *noise_pred_edit_concepts[0].shape))
                if self.sem_guidance is None: self.sem_guidance = torch.zeros((num_inference_steps + 1, *noise_pred_text.shape))
                if edit_momentum is None: edit_momentum = torch.zeros_like(noise_guidance)
                if enable_edit_guidance:
                    concept_weights = torch.zeros((len(noise_pred_edit_concepts), noise_guidance.shape[0]), device=device, dtype=noise_guidance.dtype)
                    noise_guidance_edit = torch.zeros((len(noise_pred_edit_concepts), *noise_guidance.shape), device=device, dtype=noise_guidance.dtype)
                    warmup_inds = []
                    for c, noise_pred_edit_concept in enumerate(noise_pred_edit_concepts):
                        self.edit_estimates[i, c] = noise_pred_edit_concept
                        if isinstance(edit_guidance_scale, list): edit_guidance_scale_c = edit_guidance_scale[c]
                        else: edit_guidance_scale_c = edit_guidance_scale
                        if isinstance(edit_threshold, list): edit_threshold_c = edit_threshold[c]
                        else: edit_threshold_c = edit_threshold
                        if isinstance(reverse_editing_direction, list): reverse_editing_direction_c = reverse_editing_direction[c]
                        else: reverse_editing_direction_c = reverse_editing_direction
                        if edit_weights: edit_weight_c = edit_weights[c]
                        else: edit_weight_c = 1.0
                        if isinstance(edit_warmup_steps, list): edit_warmup_steps_c = edit_warmup_steps[c]
                        else: edit_warmup_steps_c = edit_warmup_steps
                        if isinstance(edit_cooldown_steps, list): edit_cooldown_steps_c = edit_cooldown_steps[c]
                        elif edit_cooldown_steps is None: edit_cooldown_steps_c = i + 1
                        else: edit_cooldown_steps_c = edit_cooldown_steps
                        if i >= edit_warmup_steps_c: warmup_inds.append(c)
                        if i >= edit_cooldown_steps_c:
                            noise_guidance_edit[c, :, :, :, :] = torch.zeros_like(noise_pred_edit_concept)
                            continue
                        noise_guidance_edit_tmp = noise_pred_edit_concept - noise_pred_uncond
                        tmp_weights = (noise_guidance - noise_pred_edit_concept).sum(dim=(1, 2, 3))
                        tmp_weights = torch.full_like(tmp_weights, edit_weight_c)
                        if reverse_editing_direction_c: noise_guidance_edit_tmp = noise_guidance_edit_tmp * -1
                        concept_weights[c, :] = tmp_weights
                        noise_guidance_edit_tmp = noise_guidance_edit_tmp * edit_guidance_scale_c
                        if noise_guidance_edit_tmp.dtype == torch.float32: tmp = torch.quantile(torch.abs(noise_guidance_edit_tmp).flatten(start_dim=2), edit_threshold_c, dim=2, keepdim=False)
                        else: tmp = torch.quantile(torch.abs(noise_guidance_edit_tmp).flatten(start_dim=2).to(torch.float32), edit_threshold_c, dim=2, keepdim=False).to(noise_guidance_edit_tmp.dtype)
                        noise_guidance_edit_tmp = torch.where(torch.abs(noise_guidance_edit_tmp) >= tmp[:, :, None, None], noise_guidance_edit_tmp, torch.zeros_like(noise_guidance_edit_tmp))
                        noise_guidance_edit[c, :, :, :, :] = noise_guidance_edit_tmp
                    warmup_inds = torch.tensor(warmup_inds).to(device)
                    if len(noise_pred_edit_concepts) > warmup_inds.shape[0] > 0:
                        concept_weights = concept_weights.to('cpu')
                        noise_guidance_edit = noise_guidance_edit.to('cpu')
                        concept_weights_tmp = torch.index_select(concept_weights.to(device), 0, warmup_inds)
                        concept_weights_tmp = torch.where(concept_weights_tmp < 0, torch.zeros_like(concept_weights_tmp), concept_weights_tmp)
                        concept_weights_tmp = concept_weights_tmp / concept_weights_tmp.sum(dim=0)
                        noise_guidance_edit_tmp = torch.index_select(noise_guidance_edit.to(device), 0, warmup_inds)
                        noise_guidance_edit_tmp = torch.einsum('cb,cbijk->bijk', concept_weights_tmp, noise_guidance_edit_tmp)
                        noise_guidance = noise_guidance + noise_guidance_edit_tmp
                        self.sem_guidance[i] = noise_guidance_edit_tmp.detach().cpu()
                        del noise_guidance_edit_tmp
                        del concept_weights_tmp
                        concept_weights = concept_weights.to(device)
                        noise_guidance_edit = noise_guidance_edit.to(device)
                    concept_weights = torch.where(concept_weights < 0, torch.zeros_like(concept_weights), concept_weights)
                    concept_weights = torch.nan_to_num(concept_weights)
                    noise_guidance_edit = torch.einsum('cb,cbijk->bijk', concept_weights, noise_guidance_edit)
                    noise_guidance_edit = noise_guidance_edit.to(edit_momentum.device)
                    noise_guidance_edit = noise_guidance_edit + edit_momentum_scale * edit_momentum
                    edit_momentum = edit_mom_beta * edit_momentum + (1 - edit_mom_beta) * noise_guidance_edit
                    if warmup_inds.shape[0] == len(noise_pred_edit_concepts):
                        noise_guidance = noise_guidance + noise_guidance_edit
                        self.sem_guidance[i] = noise_guidance_edit.detach().cpu()
                if sem_guidance is not None:
                    edit_guidance = sem_guidance[i].to(device)
                    noise_guidance = noise_guidance + edit_guidance
                noise_pred = noise_pred_uncond + noise_guidance
            latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
            if callback is not None and i % callback_steps == 0:
                step_idx = i // getattr(self.scheduler, 'order', 1)
                callback(step_idx, t, latents)
        if not output_type == 'latent':
            image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
            image, has_nsfw_concept = self.run_safety_checker(image, device, text_embeddings.dtype)
        else:
            image = latents
            has_nsfw_concept = None
        if has_nsfw_concept is None: do_denormalize = [True] * image.shape[0]
        else: do_denormalize = [not has_nsfw for has_nsfw in has_nsfw_concept]
        image = self.image_processor.postprocess(image, output_type=output_type, do_denormalize=do_denormalize)
        if not return_dict: return (image, has_nsfw_concept)
        return SemanticStableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
