'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import copy
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer
from ....image_processor import VaeImageProcessor
from ....loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ....models import AutoencoderKL, UNet2DConditionModel
from ....models.lora import adjust_lora_scale_text_encoder
from ....schedulers import PNDMScheduler
from ....schedulers.scheduling_utils import SchedulerMixin
from ....utils import USE_PEFT_BACKEND, deprecate, scale_lora_layers, unscale_lora_layers
from ....utils.torch_utils import randn_tensor
from ...pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ...stable_diffusion.pipeline_output import StableDiffusionPipelineOutput
from ...stable_diffusion.safety_checker import StableDiffusionSafetyChecker
AUGS_CONST = ['A photo of ', 'An image of ', 'A picture of ']
class StableDiffusionModelEditingPipeline(DiffusionPipeline, StableDiffusionMixin, TextualInversionLoaderMixin, StableDiffusionLoraLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor']
    _exclude_from_cpu_offload = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, unet: UNet2DConditionModel, scheduler: SchedulerMixin, safety_checker: StableDiffusionSafetyChecker,
    feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True, with_to_k: bool=True, with_augs: list=AUGS_CONST):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
        self.with_to_k = with_to_k
        self.with_augs = with_augs
        ca_layers = []
        def append_ca(net_):
            if net_.__class__.__name__ == 'CrossAttention': ca_layers.append(net_)
            elif hasattr(net_, 'children'):
                for net__ in net_.children(): append_ca(net__)
        for net in self.unet.named_children():
            if 'down' in net[0]: append_ca(net[1])
            elif 'up' in net[0]: append_ca(net[1])
            elif 'mid' in net[0]: append_ca(net[1])
        self.ca_clip_layers = [l for l in ca_layers if l.to_v.in_features == 768]
        self.projection_matrices = [l.to_v for l in self.ca_clip_layers]
        self.og_matrices = [copy.deepcopy(l.to_v) for l in self.ca_clip_layers]
        if self.with_to_k:
            self.projection_matrices = self.projection_matrices + [l.to_k for l in self.ca_clip_layers]
            self.og_matrices = self.og_matrices + [copy.deepcopy(l.to_k) for l in self.ca_clip_layers]
    def _encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, **kwargs):
        deprecation_message = '`_encode_prompt()` is deprecated and it will be removed in a future version. Use `encode_prompt()` instead. Also, be aware that the output format changed from a concatenated tensor to a tuple.'
        deprecate('_encode_prompt()', '1.0.0', deprecation_message, standard_warn=False)
        prompt_embeds_tuple = self.encode_prompt(prompt=prompt, device=device, num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=do_classifier_free_guidance,
        negative_prompt=negative_prompt, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=lora_scale, **kwargs)
        prompt_embeds = torch.cat([prompt_embeds_tuple[1], prompt_embeds_tuple[0]])
        return prompt_embeds
    def encode_prompt(self, prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        if lora_scale is not None and isinstance(self, StableDiffusionLoraLoaderMixin):
            self._lora_scale = lora_scale
            if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
            else: scale_lora_layers(self.text_encoder, lora_scale)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        if prompt_embeds is None:
            if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, self.tokenizer)
            text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids
            untruncated_ids = self.tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
            if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = self.tokenizer.batch_decode(untruncated_ids[:, self.tokenizer.model_max_length - 1:-1])
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = text_inputs.attention_mask.to(device)
            else: attention_mask = None
            if clip_skip is None:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask)
                prompt_embeds = prompt_embeds[0]
            else:
                prompt_embeds = self.text_encoder(text_input_ids.to(device), attention_mask=attention_mask, output_hidden_states=True)
                prompt_embeds = prompt_embeds[-1][-(clip_skip + 1)]
                prompt_embeds = self.text_encoder.text_model.final_layer_norm(prompt_embeds)
        if self.text_encoder is not None: prompt_embeds_dtype = self.text_encoder.dtype
        elif self.unet is not None: prompt_embeds_dtype = self.unet.dtype
        else: prompt_embeds_dtype = prompt_embeds.dtype
        prompt_embeds = prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
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
            if isinstance(self, TextualInversionLoaderMixin): uncond_tokens = self.maybe_convert_prompt(uncond_tokens, self.tokenizer)
            max_length = prompt_embeds.shape[1]
            uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
            if hasattr(self.text_encoder.config, 'use_attention_mask') and self.text_encoder.config.use_attention_mask: attention_mask = uncond_input.attention_mask.to(device)
            else: attention_mask = None
            negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(device), attention_mask=attention_mask)
            negative_prompt_embeds = negative_prompt_embeds[0]
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.to(dtype=prompt_embeds_dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        return (prompt_embeds, negative_prompt_embeds)
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
    def check_inputs(self, prompt, height, width, callback_steps, negative_prompt=None, prompt_embeds=None,
    negative_prompt_embeds=None, callback_on_step_end_tensor_inputs=None):
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
    def edit_model(self, source_prompt: str, destination_prompt: str, lamb: float=0.1, restart_params: bool=True):
        """Args:"""
        if restart_params:
            num_ca_clip_layers = len(self.ca_clip_layers)
            for idx_, l in enumerate(self.ca_clip_layers):
                l.to_v = copy.deepcopy(self.og_matrices[idx_])
                self.projection_matrices[idx_] = l.to_v
                if self.with_to_k:
                    l.to_k = copy.deepcopy(self.og_matrices[num_ca_clip_layers + idx_])
                    self.projection_matrices[num_ca_clip_layers + idx_] = l.to_k
        old_texts = [source_prompt]
        new_texts = [destination_prompt]
        base = old_texts[0] if old_texts[0][0:1] != 'A' else 'a' + old_texts[0][1:]
        for aug in self.with_augs: old_texts.append(aug + base)
        base = new_texts[0] if new_texts[0][0:1] != 'A' else 'a' + new_texts[0][1:]
        for aug in self.with_augs: new_texts.append(aug + base)
        old_embs, new_embs = ([], [])
        for old_text, new_text in zip(old_texts, new_texts):
            text_input = self.tokenizer([old_text, new_text], padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_embeddings = self.text_encoder(text_input.input_ids.to(self.device))[0]
            old_emb, new_emb = text_embeddings
            old_embs.append(old_emb)
            new_embs.append(new_emb)
        idxs_replaces = []
        for old_text, new_text in zip(old_texts, new_texts):
            tokens_a = self.tokenizer(old_text).input_ids
            tokens_b = self.tokenizer(new_text).input_ids
            tokens_a = [self.tokenizer.encode('a ')[1] if self.tokenizer.decode(t) == 'an' else t for t in tokens_a]
            tokens_b = [self.tokenizer.encode('a ')[1] if self.tokenizer.decode(t) == 'an' else t for t in tokens_b]
            num_orig_tokens = len(tokens_a)
            idxs_replace = []
            j = 0
            for i in range(num_orig_tokens):
                curr_token = tokens_a[i]
                while tokens_b[j] != curr_token: j += 1
                idxs_replace.append(j)
                j += 1
            while j < 77:
                idxs_replace.append(j)
                j += 1
            while len(idxs_replace) < 77: idxs_replace.append(76)
            idxs_replaces.append(idxs_replace)
        contexts, valuess = ([], [])
        for old_emb, new_emb, idxs_replace in zip(old_embs, new_embs, idxs_replaces):
            context = old_emb.detach()
            values = []
            with torch.no_grad():
                for layer in self.projection_matrices: values.append(layer(new_emb[idxs_replace]).detach())
            contexts.append(context)
            valuess.append(values)
        for layer_num in range(len(self.projection_matrices)):
            mat1 = lamb * self.projection_matrices[layer_num].weight
            mat2 = lamb * torch.eye(self.projection_matrices[layer_num].weight.shape[1], device=self.projection_matrices[layer_num].weight.device)
            for context, values in zip(contexts, valuess):
                context_vector = context.reshape(context.shape[0], context.shape[1], 1)
                context_vector_T = context.reshape(context.shape[0], 1, context.shape[1])
                value_vector = values[layer_num].reshape(values[layer_num].shape[0], values[layer_num].shape[1], 1)
                for_mat1 = (value_vector @ context_vector_T).sum(dim=0)
                for_mat2 = (context_vector @ context_vector_T).sum(dim=0)
                mat1 += for_mat1
                mat2 += for_mat2
            self.projection_matrices[layer_num].weight = torch.nn.Parameter(mat1 @ torch.inverse(mat2))
    @torch.no_grad()
    def __call__(self, prompt: Union[str, List[str]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50,
    guidance_scale: float=7.5, negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int,
    int, torch.Tensor], None]]=None, callback_steps: int=1, cross_attention_kwargs: Optional[Dict[str, Any]]=None, clip_skip: Optional[int]=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, callback_steps, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        text_encoder_lora_scale = cross_attention_kwargs.get('scale', None) if cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, lora_scale=text_encoder_lora_scale, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                if do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
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
        if not return_dict: return (image, has_nsfw_concept)
        return StableDiffusionPipelineOutput(images=image, nsfw_content_detected=has_nsfw_concept)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
