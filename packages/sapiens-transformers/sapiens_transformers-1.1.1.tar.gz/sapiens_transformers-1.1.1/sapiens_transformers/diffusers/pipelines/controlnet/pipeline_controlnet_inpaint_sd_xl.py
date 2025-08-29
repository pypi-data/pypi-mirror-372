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
import PIL.Image
import torch
import torch.nn.functional as F
from sapiens_transformers import CLIPImageProcessor, CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer, CLIPVisionModelWithProjection
from ...callbacks import MultiPipelineCallbacks, PipelineCallback
from ...image_processor import PipelineImageInput, VaeImageProcessor
from ...loaders import FromSingleFileMixin, IPAdapterMixin, StableDiffusionXLLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, ControlNetModel, ImageProjection, MultiControlNetModel, UNet2DConditionModel
from ...models.attention_processor import AttnProcessor2_0, XFormersAttnProcessor
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, deprecate, is_invisible_watermark_available, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import is_compiled_module, randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
if is_invisible_watermark_available(): from ...pipelines.stable_diffusion_xl.watermark import StableDiffusionXLWatermarker
def retrieve_latents(encoder_output: torch.Tensor, generator: Optional[torch.Generator]=None, sample_mode: str='sample'):
    if hasattr(encoder_output, 'latent_dist') and sample_mode == 'sample': return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, 'latent_dist') and sample_mode == 'argmax': return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, 'latents'): return encoder_output.latents
    else: raise AttributeError('Could not access latents of provided encoder_output')
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> # !pip install transformers sapiens_accelerator\n        >>> from sapiens_transformers.diffusers import StableDiffusionXLControlNetInpaintPipeline, ControlNetModel, DDIMScheduler\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> from PIL import Image\n        >>> import numpy as np\n        >>> import torch\n\n        >>> init_image = load_image(\n        ...     "https://huggingface.co/datasets/diffusers/test-arrays/resolve/main/stable_diffusion_inpaint/boy.png"\n        ... )\n        >>> init_image = init_image.resize((1024, 1024))\n\n        >>> generator = torch.Generator(device="cpu").manual_seed(1)\n\n        >>> mask_image = load_image(\n        ...     "https://huggingface.co/datasets/diffusers/test-arrays/resolve/main/stable_diffusion_inpaint/boy_mask.png"\n        ... )\n        >>> mask_image = mask_image.resize((1024, 1024))\n\n\n        >>> def make_canny_condition(image):\n        ...     image = np.array(image)\n        ...     image = cv2.Canny(image, 100, 200)\n        ...     image = image[:, :, None]\n        ...     image = np.concatenate([image, image, image], axis=2)\n        ...     image = Image.fromarray(image)\n        ...     return image\n\n\n        >>> control_image = make_canny_condition(init_image)\n\n        >>> controlnet = ControlNetModel.from_pretrained(\n        ...     "sapiens_transformers.diffusers/controlnet-canny-sdxl-1.0", torch_dtype=torch.float16\n        ... )\n        >>> pipe = StableDiffusionXLControlNetInpaintPipeline.from_pretrained(\n        ...     "stabilityai/stable-diffusion-xl-base-1.0", controlnet=controlnet, torch_dtype=torch.float16\n        ... )\n\n        >>> pipe.enable_model_cpu_offload()\n\n        >>> # generate image\n        >>> image = pipe(\n        ...     "a handsome man with ray-ban sunglasses",\n        ...     num_inference_steps=20,\n        ...     generator=generator,\n        ...     eta=1.0,\n        ...     image=init_image,\n        ...     mask_image=mask_image,\n        ...     control_image=control_image,\n        ... ).images[0]\n        ```\n'
def rescale_noise_cfg(noise_cfg, noise_pred_text, guidance_rescale=0.0):
    """Returns:"""
    std_text = noise_pred_text.std(dim=list(range(1, noise_pred_text.ndim)), keepdim=True)
    std_cfg = noise_cfg.std(dim=list(range(1, noise_cfg.ndim)), keepdim=True)
    noise_pred_rescaled = noise_cfg * (std_text / std_cfg)
    noise_cfg = guidance_rescale * noise_pred_rescaled + (1 - guidance_rescale) * noise_cfg
    return noise_cfg
class StableDiffusionXLControlNetInpaintPipeline(DiffusionPipeline, StableDiffusionMixin, StableDiffusionXLLoraLoaderMixin, FromSingleFileMixin, IPAdapterMixin, TextualInversionLoaderMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->text_encoder_2->unet->vae'
    _optional_components = ['tokenizer', 'tokenizer_2', 'text_encoder', 'text_encoder_2', 'image_encoder', 'feature_extractor']
    _callback_tensor_inputs = ['latents', 'prompt_embeds', 'negative_prompt_embeds', 'add_text_embeds', 'add_time_ids', 'negative_pooled_prompt_embeds', 'add_neg_time_ids', 'mask', 'masked_image_latents']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, text_encoder_2: CLIPTextModelWithProjection, tokenizer: CLIPTokenizer, tokenizer_2: CLIPTokenizer, unet: UNet2DConditionModel,
    controlnet: Union[ControlNetModel, List[ControlNetModel], Tuple[ControlNetModel], MultiControlNetModel], scheduler: KarrasDiffusionSchedulers, requires_aesthetics_score: bool=False,
    force_zeros_for_empty_prompt: bool=True, add_watermarker: Optional[bool]=None, feature_extractor: Optional[CLIPImageProcessor]=None, image_encoder: Optional[CLIPVisionModelWithProjection]=None):
        super().__init__()
        if isinstance(controlnet, (list, tuple)): controlnet = MultiControlNetModel(controlnet)
        self.register_modules(vae=vae, text_encoder=text_encoder, text_encoder_2=text_encoder_2, tokenizer=tokenizer, tokenizer_2=tokenizer_2, unet=unet, controlnet=controlnet,
        scheduler=scheduler, feature_extractor=feature_extractor, image_encoder=image_encoder)
        self.register_to_config(force_zeros_for_empty_prompt=force_zeros_for_empty_prompt)
        self.register_to_config(requires_aesthetics_score=requires_aesthetics_score)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor)
        self.mask_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_normalize=False, do_binarize=True, do_convert_grayscale=True)
        self.control_image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True, do_normalize=False)
        add_watermarker = add_watermarker if add_watermarker is not None else is_invisible_watermark_available()
        if add_watermarker: self.watermark = StableDiffusionXLWatermarker()
        else: self.watermark = None
    def encode_prompt(self, prompt: str, prompt_2: Optional[str]=None, device: Optional[torch.device]=None, num_images_per_prompt: int=1, do_classifier_free_guidance: bool=True,
    negative_prompt: Optional[str]=None, negative_prompt_2: Optional[str]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, lora_scale: Optional[float]=None, clip_skip: Optional[int]=None):
        """Args:"""
        device = device or self._execution_device
        if lora_scale is not None and isinstance(self, StableDiffusionXLLoraLoaderMixin):
            self._lora_scale = lora_scale
            if self.text_encoder is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder, lora_scale)
                else: scale_lora_layers(self.text_encoder, lora_scale)
            if self.text_encoder_2 is not None:
                if not USE_PEFT_BACKEND: adjust_lora_scale_text_encoder(self.text_encoder_2, lora_scale)
                else: scale_lora_layers(self.text_encoder_2, lora_scale)
        prompt = [prompt] if isinstance(prompt, str) else prompt
        if prompt is not None: batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        tokenizers = [self.tokenizer, self.tokenizer_2] if self.tokenizer is not None else [self.tokenizer_2]
        text_encoders = [self.text_encoder, self.text_encoder_2] if self.text_encoder is not None else [self.text_encoder_2]
        if prompt_embeds is None:
            prompt_2 = prompt_2 or prompt
            prompt_2 = [prompt_2] if isinstance(prompt_2, str) else prompt_2
            prompt_embeds_list = []
            prompts = [prompt, prompt_2]
            for prompt, tokenizer, text_encoder in zip(prompts, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): prompt = self.maybe_convert_prompt(prompt, tokenizer)
                text_inputs = tokenizer(prompt, padding='max_length', max_length=tokenizer.model_max_length, truncation=True, return_tensors='pt')
                text_input_ids = text_inputs.input_ids
                untruncated_ids = tokenizer(prompt, padding='longest', return_tensors='pt').input_ids
                if untruncated_ids.shape[-1] >= text_input_ids.shape[-1] and (not torch.equal(text_input_ids, untruncated_ids)): removed_text = tokenizer.batch_decode(untruncated_ids[:, tokenizer.model_max_length - 1:-1])
                prompt_embeds = text_encoder(text_input_ids.to(device), output_hidden_states=True)
                pooled_prompt_embeds = prompt_embeds[0]
                if clip_skip is None: prompt_embeds = prompt_embeds.hidden_states[-2]
                else: prompt_embeds = prompt_embeds.hidden_states[-(clip_skip + 2)]
                prompt_embeds_list.append(prompt_embeds)
            prompt_embeds = torch.concat(prompt_embeds_list, dim=-1)
        zero_out_negative_prompt = negative_prompt is None and self.config.force_zeros_for_empty_prompt
        if do_classifier_free_guidance and negative_prompt_embeds is None and zero_out_negative_prompt:
            negative_prompt_embeds = torch.zeros_like(prompt_embeds)
            negative_pooled_prompt_embeds = torch.zeros_like(pooled_prompt_embeds)
        elif do_classifier_free_guidance and negative_prompt_embeds is None:
            negative_prompt = negative_prompt or ''
            negative_prompt_2 = negative_prompt_2 or negative_prompt
            negative_prompt = batch_size * [negative_prompt] if isinstance(negative_prompt, str) else negative_prompt
            negative_prompt_2 = batch_size * [negative_prompt_2] if isinstance(negative_prompt_2, str) else negative_prompt_2
            uncond_tokens: List[str]
            if prompt is not None and type(prompt) is not type(negative_prompt): raise TypeError(f'`negative_prompt` should be the same type to `prompt`, but got {type(negative_prompt)} != {type(prompt)}.')
            elif batch_size != len(negative_prompt): raise ValueError(f'`negative_prompt`: {negative_prompt} has batch size {len(negative_prompt)}, but `prompt`: {prompt} has batch size {batch_size}. Please make sure that passed `negative_prompt` matches the batch size of `prompt`.')
            else: uncond_tokens = [negative_prompt, negative_prompt_2]
            negative_prompt_embeds_list = []
            for negative_prompt, tokenizer, text_encoder in zip(uncond_tokens, tokenizers, text_encoders):
                if isinstance(self, TextualInversionLoaderMixin): negative_prompt = self.maybe_convert_prompt(negative_prompt, tokenizer)
                max_length = prompt_embeds.shape[1]
                uncond_input = tokenizer(negative_prompt, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
                negative_prompt_embeds = text_encoder(uncond_input.input_ids.to(device), output_hidden_states=True)
                negative_pooled_prompt_embeds = negative_prompt_embeds[0]
                negative_prompt_embeds = negative_prompt_embeds.hidden_states[-2]
                negative_prompt_embeds_list.append(negative_prompt_embeds)
            negative_prompt_embeds = torch.concat(negative_prompt_embeds_list, dim=-1)
        if self.text_encoder_2 is not None: prompt_embeds = prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
        else: prompt_embeds = prompt_embeds.to(dtype=self.unet.dtype, device=device)
        bs_embed, seq_len, _ = prompt_embeds.shape
        prompt_embeds = prompt_embeds.repeat(1, num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(bs_embed * num_images_per_prompt, seq_len, -1)
        if do_classifier_free_guidance:
            seq_len = negative_prompt_embeds.shape[1]
            if self.text_encoder_2 is not None: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.text_encoder_2.dtype, device=device)
            else: negative_prompt_embeds = negative_prompt_embeds.to(dtype=self.unet.dtype, device=device)
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
        pooled_prompt_embeds = pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if do_classifier_free_guidance: negative_pooled_prompt_embeds = negative_pooled_prompt_embeds.repeat(1, num_images_per_prompt).view(bs_embed * num_images_per_prompt, -1)
        if self.text_encoder is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder, lora_scale)
        if self.text_encoder_2 is not None:
            if isinstance(self, StableDiffusionXLLoraLoaderMixin) and USE_PEFT_BACKEND: unscale_lora_layers(self.text_encoder_2, lora_scale)
        return (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds)
    def encode_image(self, image, device, num_images_per_prompt, output_hidden_states=None):
        dtype = next(self.image_encoder.parameters()).dtype
        if not isinstance(image, torch.Tensor): image = self.feature_extractor(image, return_tensors='pt').pixel_values
        image = image.to(device=device, dtype=dtype)
        if output_hidden_states:
            image_enc_hidden_states = self.image_encoder(image, output_hidden_states=True).hidden_states[-2]
            image_enc_hidden_states = image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_enc_hidden_states = self.image_encoder(torch.zeros_like(image), output_hidden_states=True).hidden_states[-2]
            uncond_image_enc_hidden_states = uncond_image_enc_hidden_states.repeat_interleave(num_images_per_prompt, dim=0)
            return (image_enc_hidden_states, uncond_image_enc_hidden_states)
        else:
            image_embeds = self.image_encoder(image).image_embeds
            image_embeds = image_embeds.repeat_interleave(num_images_per_prompt, dim=0)
            uncond_image_embeds = torch.zeros_like(image_embeds)
            return (image_embeds, uncond_image_embeds)
    def prepare_ip_adapter_image_embeds(self, ip_adapter_image, ip_adapter_image_embeds, device, num_images_per_prompt, do_classifier_free_guidance):
        image_embeds = []
        if do_classifier_free_guidance: negative_image_embeds = []
        if ip_adapter_image_embeds is None:
            if not isinstance(ip_adapter_image, list): ip_adapter_image = [ip_adapter_image]
            if len(ip_adapter_image) != len(self.unet.encoder_hid_proj.image_projection_layers): raise ValueError(f'`ip_adapter_image` must have same length as the number of IP Adapters. Got {len(ip_adapter_image)} images and {len(self.unet.encoder_hid_proj.image_projection_layers)} IP Adapters.')
            for single_ip_adapter_image, image_proj_layer in zip(ip_adapter_image, self.unet.encoder_hid_proj.image_projection_layers):
                output_hidden_state = not isinstance(image_proj_layer, ImageProjection)
                single_image_embeds, single_negative_image_embeds = self.encode_image(single_ip_adapter_image, device, 1, output_hidden_state)
                image_embeds.append(single_image_embeds[None, :])
                if do_classifier_free_guidance: negative_image_embeds.append(single_negative_image_embeds[None, :])
        else:
            for single_image_embeds in ip_adapter_image_embeds:
                if do_classifier_free_guidance:
                    single_negative_image_embeds, single_image_embeds = single_image_embeds.chunk(2)
                    negative_image_embeds.append(single_negative_image_embeds)
                image_embeds.append(single_image_embeds)
        ip_adapter_image_embeds = []
        for i, single_image_embeds in enumerate(image_embeds):
            single_image_embeds = torch.cat([single_image_embeds] * num_images_per_prompt, dim=0)
            if do_classifier_free_guidance:
                single_negative_image_embeds = torch.cat([negative_image_embeds[i]] * num_images_per_prompt, dim=0)
                single_image_embeds = torch.cat([single_negative_image_embeds, single_image_embeds], dim=0)
            single_image_embeds = single_image_embeds.to(device=device)
            ip_adapter_image_embeds.append(single_image_embeds)
        return ip_adapter_image_embeds
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_image(self, image, prompt, prompt_embeds):
        image_is_pil = isinstance(image, PIL.Image.Image)
        image_is_tensor = isinstance(image, torch.Tensor)
        image_is_np = isinstance(image, np.ndarray)
        image_is_pil_list = isinstance(image, list) and isinstance(image[0], PIL.Image.Image)
        image_is_tensor_list = isinstance(image, list) and isinstance(image[0], torch.Tensor)
        image_is_np_list = isinstance(image, list) and isinstance(image[0], np.ndarray)
        if not image_is_pil and (not image_is_tensor) and (not image_is_np) and (not image_is_pil_list) and (not image_is_tensor_list) and (not image_is_np_list): raise TypeError(f'image must be passed and be one of PIL image, numpy array, torch tensor, list of PIL images, list of numpy arrays or list of torch tensors, but is {type(image)}')
        if image_is_pil: image_batch_size = 1
        else: image_batch_size = len(image)
        if prompt is not None and isinstance(prompt, str): prompt_batch_size = 1
        elif prompt is not None and isinstance(prompt, list): prompt_batch_size = len(prompt)
        elif prompt_embeds is not None: prompt_batch_size = prompt_embeds.shape[0]
        if image_batch_size != 1 and image_batch_size != prompt_batch_size: raise ValueError(f'If image batch size is not 1, image batch size must be same as prompt batch size. image batch size: {image_batch_size}, prompt batch size: {prompt_batch_size}')
    def check_inputs(self, prompt, prompt_2, image, mask_image, strength, num_inference_steps, callback_steps, output_type, negative_prompt=None, negative_prompt_2=None, prompt_embeds=None,
    negative_prompt_embeds=None, ip_adapter_image=None, ip_adapter_image_embeds=None, pooled_prompt_embeds=None, negative_pooled_prompt_embeds=None, controlnet_conditioning_scale=1.0,
    control_guidance_start=0.0, control_guidance_end=1.0, callback_on_step_end_tensor_inputs=None, padding_mask_crop=None):
        if strength < 0 or strength > 1: raise ValueError(f'The value of strength should in [0.0, 1.0] but is {strength}')
        if num_inference_steps is None: raise ValueError('`num_inference_steps` cannot be None.')
        elif not isinstance(num_inference_steps, int) or num_inference_steps <= 0: raise ValueError(f'`num_inference_steps` has to be a positive integer but is {num_inference_steps} of type {type(num_inference_steps)}.')
        if callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        if callback_on_step_end_tensor_inputs is not None and (not all((k in self._callback_tensor_inputs for k in callback_on_step_end_tensor_inputs))): raise ValueError(f'`callback_on_step_end_tensor_inputs` has to be in {self._callback_tensor_inputs}, but found {[k for k in callback_on_step_end_tensor_inputs if k not in self._callback_tensor_inputs]}')
        if prompt is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt`: {prompt} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt_2 is not None and prompt_embeds is not None: raise ValueError(f'Cannot forward both `prompt_2`: {prompt_2} and `prompt_embeds`: {prompt_embeds}. Please make sure to only forward one of the two.')
        elif prompt is None and prompt_embeds is None: raise ValueError('Provide either `prompt` or `prompt_embeds`. Cannot leave both `prompt` and `prompt_embeds` undefined.')
        elif prompt is not None and (not isinstance(prompt, str) and (not isinstance(prompt, list))): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        elif prompt_2 is not None and (not isinstance(prompt_2, str) and (not isinstance(prompt_2, list))): raise ValueError(f'`prompt_2` has to be of type `str` or `list` but is {type(prompt_2)}')
        if negative_prompt is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt`: {negative_prompt} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        elif negative_prompt_2 is not None and negative_prompt_embeds is not None: raise ValueError(f'Cannot forward both `negative_prompt_2`: {negative_prompt_2} and `negative_prompt_embeds`: {negative_prompt_embeds}. Please make sure to only forward one of the two.')
        if prompt_embeds is not None and negative_prompt_embeds is not None:
            if prompt_embeds.shape != negative_prompt_embeds.shape: raise ValueError(f'`prompt_embeds` and `negative_prompt_embeds` must have the same shape when passed directly, but got: `prompt_embeds` {prompt_embeds.shape} != `negative_prompt_embeds` {negative_prompt_embeds.shape}.')
        if padding_mask_crop is not None:
            if not isinstance(image, PIL.Image.Image): raise ValueError(f'The image should be a PIL image when inpainting mask crop, but is of type {type(image)}.')
            if not isinstance(mask_image, PIL.Image.Image): raise ValueError(f'The mask image should be a PIL image when inpainting mask crop, but is of type {type(mask_image)}.')
            if output_type != 'pil': raise ValueError(f'The output type should be PIL when inpainting mask crop, but is {output_type}.')
        if prompt_embeds is not None and pooled_prompt_embeds is None: raise ValueError('If `prompt_embeds` are provided, `pooled_prompt_embeds` also have to be passed. Make sure to generate `pooled_prompt_embeds` from the same text encoder that was used to generate `prompt_embeds`.')
        if negative_prompt_embeds is not None and negative_pooled_prompt_embeds is None: raise ValueError('If `negative_prompt_embeds` are provided, `negative_pooled_prompt_embeds` also have to be passed. Make sure to generate `negative_pooled_prompt_embeds` from the same text encoder that was used to generate `negative_prompt_embeds`.')
        is_compiled = hasattr(F, 'scaled_dot_product_attention') and isinstance(self.controlnet, torch._dynamo.eval_frame.OptimizedModule)
        if isinstance(self.controlnet, ControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, ControlNetModel)): self.check_image(image, prompt, prompt_embeds)
        elif isinstance(self.controlnet, MultiControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, MultiControlNetModel)):
            if not isinstance(image, list): raise TypeError('For multiple controlnets: `image` must be type `list`')
            elif any((isinstance(i, list) for i in image)): raise ValueError('A single batch of multiple conditionings are supported at the moment.')
            elif len(image) != len(self.controlnet.nets): raise ValueError(f'For multiple controlnets: `image` must have the same length as the number of controlnets, but got {len(image)} images and {len(self.controlnet.nets)} ControlNets.')
            for image_ in image: self.check_image(image_, prompt, prompt_embeds)
        else: assert False
        if isinstance(self.controlnet, ControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, ControlNetModel)):
            if not isinstance(controlnet_conditioning_scale, float): raise TypeError('For single controlnet: `controlnet_conditioning_scale` must be type `float`.')
        elif isinstance(self.controlnet, MultiControlNetModel) or (is_compiled and isinstance(self.controlnet._orig_mod, MultiControlNetModel)):
            if isinstance(controlnet_conditioning_scale, list):
                if any((isinstance(i, list) for i in controlnet_conditioning_scale)): raise ValueError('A single batch of multiple conditionings are supported at the moment.')
            elif isinstance(controlnet_conditioning_scale, list) and len(controlnet_conditioning_scale) != len(self.controlnet.nets): raise ValueError('For multiple controlnets: When `controlnet_conditioning_scale` is specified as `list`, it must have the same length as the number of controlnets')
        else: assert False
        if not isinstance(control_guidance_start, (tuple, list)): control_guidance_start = [control_guidance_start]
        if not isinstance(control_guidance_end, (tuple, list)): control_guidance_end = [control_guidance_end]
        if len(control_guidance_start) != len(control_guidance_end): raise ValueError(f'`control_guidance_start` has {len(control_guidance_start)} elements, but `control_guidance_end` has {len(control_guidance_end)} elements. Make sure to provide the same number of elements to each list.')
        if isinstance(self.controlnet, MultiControlNetModel):
            if len(control_guidance_start) != len(self.controlnet.nets): raise ValueError(f'`control_guidance_start`: {control_guidance_start} has {len(control_guidance_start)} elements but there are {len(self.controlnet.nets)} controlnets available. Make sure to provide {len(self.controlnet.nets)}.')
        for start, end in zip(control_guidance_start, control_guidance_end):
            if start >= end: raise ValueError(f'control guidance start: {start} cannot be larger or equal to control guidance end: {end}.')
            if start < 0.0: raise ValueError(f"control guidance start: {start} can't be smaller than 0.")
            if end > 1.0: raise ValueError(f"control guidance end: {end} can't be larger than 1.0.")
        if ip_adapter_image is not None and ip_adapter_image_embeds is not None: raise ValueError('Provide either `ip_adapter_image` or `ip_adapter_image_embeds`. Cannot leave both `ip_adapter_image` and `ip_adapter_image_embeds` defined.')
        if ip_adapter_image_embeds is not None:
            if not isinstance(ip_adapter_image_embeds, list): raise ValueError(f'`ip_adapter_image_embeds` has to be of type `list` but is {type(ip_adapter_image_embeds)}')
            elif ip_adapter_image_embeds[0].ndim not in [3, 4]: raise ValueError(f'`ip_adapter_image_embeds` has to be a list of 3D or 4D tensors but is {ip_adapter_image_embeds[0].ndim}D')
    def prepare_control_image(self, image, width, height, batch_size, num_images_per_prompt, device, dtype, crops_coords, resize_mode, do_classifier_free_guidance=False, guess_mode=False):
        image = self.control_image_processor.preprocess(image, height=height, width=width, crops_coords=crops_coords, resize_mode=resize_mode).to(dtype=torch.float32)
        image_batch_size = image.shape[0]
        if image_batch_size == 1: repeat_by = batch_size
        else: repeat_by = num_images_per_prompt
        image = image.repeat_interleave(repeat_by, dim=0)
        image = image.to(device=device, dtype=dtype)
        if do_classifier_free_guidance and (not guess_mode): image = torch.cat([image] * 2)
        return image
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None, image=None, timestep=None, is_strength_max=True, add_noise=True,
    return_noise=False, return_image_latents=False):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if (image is None or timestep is None) and (not is_strength_max): raise ValueError('Since strength < 1. initial latents are to be initialised as a combination of Image + Noise.However, either the image or the noise timestep has not been provided.')
        if return_image_latents or (latents is None and (not is_strength_max)):
            image = image.to(device=device, dtype=dtype)
            if image.shape[1] == 4: image_latents = image
            else: image_latents = self._encode_vae_image(image=image, generator=generator)
            image_latents = image_latents.repeat(batch_size // image_latents.shape[0], 1, 1, 1)
        if latents is None and add_noise:
            noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            latents = noise if is_strength_max else self.scheduler.add_noise(image_latents, noise, timestep)
            latents = latents * self.scheduler.init_noise_sigma if is_strength_max else latents
        elif add_noise:
            noise = latents.to(device)
            latents = noise * self.scheduler.init_noise_sigma
        else:
            noise = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
            latents = image_latents.to(device)
        outputs = (latents,)
        if return_noise: outputs += (noise,)
        if return_image_latents: outputs += (image_latents,)
        return outputs
    def _encode_vae_image(self, image: torch.Tensor, generator: torch.Generator):
        dtype = image.dtype
        if self.vae.config.force_upcast:
            image = image.float()
            self.vae.to(dtype=torch.float32)
        if isinstance(generator, list):
            image_latents = [retrieve_latents(self.vae.encode(image[i:i + 1]), generator=generator[i]) for i in range(image.shape[0])]
            image_latents = torch.cat(image_latents, dim=0)
        else: image_latents = retrieve_latents(self.vae.encode(image), generator=generator)
        if self.vae.config.force_upcast: self.vae.to(dtype)
        image_latents = image_latents.to(dtype)
        image_latents = self.vae.config.scaling_factor * image_latents
        return image_latents
    def prepare_mask_latents(self, mask, masked_image, batch_size, height, width, dtype, device, generator, do_classifier_free_guidance):
        mask = torch.nn.functional.interpolate(mask, size=(height // self.vae_scale_factor, width // self.vae_scale_factor))
        mask = mask.to(device=device, dtype=dtype)
        if mask.shape[0] < batch_size:
            if not batch_size % mask.shape[0] == 0: raise ValueError(f"The passed mask and the required batch size don't match. Masks are supposed to be duplicated to a total batch size of {batch_size}, but {mask.shape[0]} masks were passed. Make sure the number of masks that you pass is divisible by the total requested batch size.")
            mask = mask.repeat(batch_size // mask.shape[0], 1, 1, 1)
        mask = torch.cat([mask] * 2) if do_classifier_free_guidance else mask
        masked_image_latents = None
        if masked_image is not None:
            masked_image = masked_image.to(device=device, dtype=dtype)
            masked_image_latents = self._encode_vae_image(masked_image, generator=generator)
            if masked_image_latents.shape[0] < batch_size:
                if not batch_size % masked_image_latents.shape[0] == 0: raise ValueError(f"The passed images and the required batch size don't match. Images are supposed to be duplicated to a total batch size of {batch_size}, but {masked_image_latents.shape[0]} images were passed. Make sure the number of images that you pass is divisible by the total requested batch size.")
                masked_image_latents = masked_image_latents.repeat(batch_size // masked_image_latents.shape[0], 1, 1, 1)
            masked_image_latents = torch.cat([masked_image_latents] * 2) if do_classifier_free_guidance else masked_image_latents
            masked_image_latents = masked_image_latents.to(device=device, dtype=dtype)
        return (mask, masked_image_latents)
    def get_timesteps(self, num_inference_steps, strength, device, denoising_start=None):
        if denoising_start is None:
            init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
            t_start = max(num_inference_steps - init_timestep, 0)
            timesteps = self.scheduler.timesteps[t_start * self.scheduler.order:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start * self.scheduler.order)
            return (timesteps, num_inference_steps - t_start)
        else:
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - denoising_start * self.scheduler.config.num_train_timesteps))
            num_inference_steps = (self.scheduler.timesteps < discrete_timestep_cutoff).sum().item()
            if self.scheduler.order == 2 and num_inference_steps % 2 == 0: num_inference_steps = num_inference_steps + 1
            t_start = len(self.scheduler.timesteps) - num_inference_steps
            timesteps = self.scheduler.timesteps[t_start:]
            if hasattr(self.scheduler, 'set_begin_index'): self.scheduler.set_begin_index(t_start)
            return (timesteps, num_inference_steps)
    def _get_add_time_ids(self, original_size, crops_coords_top_left, target_size, aesthetic_score, negative_aesthetic_score, dtype, text_encoder_projection_dim=None):
        if self.config.requires_aesthetics_score:
            add_time_ids = list(original_size + crops_coords_top_left + (aesthetic_score,))
            add_neg_time_ids = list(original_size + crops_coords_top_left + (negative_aesthetic_score,))
        else:
            add_time_ids = list(original_size + crops_coords_top_left + target_size)
            add_neg_time_ids = list(original_size + crops_coords_top_left + target_size)
        passed_add_embed_dim = self.unet.config.addition_time_embed_dim * len(add_time_ids) + text_encoder_projection_dim
        expected_add_embed_dim = self.unet.add_embedding.linear_1.in_features
        if expected_add_embed_dim > passed_add_embed_dim and expected_add_embed_dim - passed_add_embed_dim == self.unet.config.addition_time_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. Please make sure to enable `requires_aesthetics_score` with `pipe.register_to_config(requires_aesthetics_score=True)` to make sure `aesthetic_score` {aesthetic_score} and `negative_aesthetic_score` {negative_aesthetic_score} is correctly used by the model.')
        elif expected_add_embed_dim < passed_add_embed_dim and passed_add_embed_dim - expected_add_embed_dim == self.unet.config.addition_time_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. Please make sure to disable `requires_aesthetics_score` with `pipe.register_to_config(requires_aesthetics_score=False)` to make sure `target_size` {target_size} is correctly used by the model.')
        elif expected_add_embed_dim != passed_add_embed_dim: raise ValueError(f'Model expects an added time embedding vector of length {expected_add_embed_dim}, but a vector of {passed_add_embed_dim} was created. The model has an incorrect config. Please check `unet.config.time_embedding_type` and `text_encoder_2.config.projection_dim`.')
        add_time_ids = torch.tensor([add_time_ids], dtype=dtype)
        add_neg_time_ids = torch.tensor([add_neg_time_ids], dtype=dtype)
        return (add_time_ids, add_neg_time_ids)
    def upcast_vae(self):
        dtype = self.vae.dtype
        self.vae.to(dtype=torch.float32)
        use_torch_2_0_or_xformers = isinstance(self.vae.decoder.mid_block.attentions[0].processor, (AttnProcessor2_0, XFormersAttnProcessor))
        if use_torch_2_0_or_xformers:
            self.vae.post_quant_conv.to(dtype)
            self.vae.decoder.conv_in.to(dtype)
            self.vae.decoder.mid_block.to(dtype)
    @property
    def guidance_scale(self): return self._guidance_scale
    @property
    def clip_skip(self): return self._clip_skip
    @property
    def do_classifier_free_guidance(self): return self._guidance_scale > 1
    @property
    def cross_attention_kwargs(self): return self._cross_attention_kwargs
    @property
    def num_timesteps(self): return self._num_timesteps
    @property
    def interrupt(self): return self._interrupt
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, prompt_2: Optional[Union[str, List[str]]]=None, image: PipelineImageInput=None, mask_image: PipelineImageInput=None,
    control_image: Union[PipelineImageInput, List[PipelineImageInput]]=None, height: Optional[int]=None, width: Optional[int]=None, padding_mask_crop: Optional[int]=None,
    strength: float=0.9999, num_inference_steps: int=50, denoising_start: Optional[float]=None, denoising_end: Optional[float]=None, guidance_scale: float=5.0,
    negative_prompt: Optional[Union[str, List[str]]]=None, negative_prompt_2: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1,
    eta: float=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None,
    negative_prompt_embeds: Optional[torch.Tensor]=None, ip_adapter_image: Optional[PipelineImageInput]=None, ip_adapter_image_embeds: Optional[List[torch.Tensor]]=None,
    pooled_prompt_embeds: Optional[torch.Tensor]=None, negative_pooled_prompt_embeds: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, controlnet_conditioning_scale: Union[float, List[float]]=1.0, guess_mode: bool=False,
    control_guidance_start: Union[float, List[float]]=0.0, control_guidance_end: Union[float, List[float]]=1.0, guidance_rescale: float=0.0, original_size: Tuple[int, int]=None,
    crops_coords_top_left: Tuple[int, int]=(0, 0), target_size: Tuple[int, int]=None, aesthetic_score: float=6.0, negative_aesthetic_score: float=2.5, clip_skip: Optional[int]=None,
    callback_on_step_end: Optional[Union[Callable[[int, int, Dict], None], PipelineCallback, MultiPipelineCallbacks]]=None, callback_on_step_end_tensor_inputs: List[str]=['latents'], **kwargs):
        """Examples:"""
        callback = kwargs.pop('callback', None)
        callback_steps = kwargs.pop('callback_steps', None)
        if callback is not None: deprecate('callback', '1.0.0', 'Passing `callback` as an input argument to `__call__` is deprecated, consider using `callback_on_step_end`')
        if callback_steps is not None: deprecate('callback_steps', '1.0.0', 'Passing `callback_steps` as an input argument to `__call__` is deprecated, consider using `callback_on_step_end`')
        if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)): callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs
        controlnet = self.controlnet._orig_mod if is_compiled_module(self.controlnet) else self.controlnet
        if not isinstance(control_guidance_start, list) and isinstance(control_guidance_end, list): control_guidance_start = len(control_guidance_end) * [control_guidance_start]
        elif not isinstance(control_guidance_end, list) and isinstance(control_guidance_start, list): control_guidance_end = len(control_guidance_start) * [control_guidance_end]
        elif not isinstance(control_guidance_start, list) and (not isinstance(control_guidance_end, list)):
            mult = len(controlnet.nets) if isinstance(controlnet, MultiControlNetModel) else 1
            control_guidance_start, control_guidance_end = (mult * [control_guidance_start], mult * [control_guidance_end])
        if not isinstance(control_guidance_start, list) and isinstance(control_guidance_end, list): control_guidance_start = len(control_guidance_end) * [control_guidance_start]
        elif not isinstance(control_guidance_end, list) and isinstance(control_guidance_start, list): control_guidance_end = len(control_guidance_start) * [control_guidance_end]
        elif not isinstance(control_guidance_start, list) and (not isinstance(control_guidance_end, list)):
            mult = len(controlnet.nets) if isinstance(controlnet, MultiControlNetModel) else 1
            control_guidance_start, control_guidance_end = (mult * [control_guidance_start], mult * [control_guidance_end])
        self.check_inputs(prompt, prompt_2, control_image, mask_image, strength, num_inference_steps, callback_steps, output_type, negative_prompt, negative_prompt_2, prompt_embeds,
        negative_prompt_embeds, ip_adapter_image, ip_adapter_image_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds, controlnet_conditioning_scale, control_guidance_start,
        control_guidance_end, callback_on_step_end_tensor_inputs, padding_mask_crop)
        self._guidance_scale = guidance_scale
        self._clip_skip = clip_skip
        self._cross_attention_kwargs = cross_attention_kwargs
        self._interrupt = False
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        if isinstance(controlnet, MultiControlNetModel) and isinstance(controlnet_conditioning_scale, float): controlnet_conditioning_scale = [controlnet_conditioning_scale] * len(controlnet.nets)
        text_encoder_lora_scale = self.cross_attention_kwargs.get('scale', None) if self.cross_attention_kwargs is not None else None
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = self.encode_prompt(prompt=prompt, prompt_2=prompt_2, device=device,
        num_images_per_prompt=num_images_per_prompt, do_classifier_free_guidance=self.do_classifier_free_guidance, negative_prompt=negative_prompt, negative_prompt_2=negative_prompt_2,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
        lora_scale=text_encoder_lora_scale, clip_skip=self.clip_skip)
        if ip_adapter_image is not None or ip_adapter_image_embeds is not None: image_embeds = self.prepare_ip_adapter_image_embeds(ip_adapter_image,
        ip_adapter_image_embeds, device, batch_size * num_images_per_prompt, self.do_classifier_free_guidance)
        def denoising_value_valid(dnv): return isinstance(dnv, float) and 0 < dnv < 1
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps, num_inference_steps = self.get_timesteps(num_inference_steps, strength, device, denoising_start=denoising_start if denoising_value_valid(denoising_start) else None)
        if num_inference_steps < 1: raise ValueError(f'After adjusting the num_inference_steps by strength parameter: {strength}, the number of pipelinesteps is {num_inference_steps} which is < 1 and not appropriate for this pipeline.')
        latent_timestep = timesteps[:1].repeat(batch_size * num_images_per_prompt)
        is_strength_max = strength == 1.0
        self._num_timesteps = len(timesteps)
        if padding_mask_crop is not None:
            height, width = self.image_processor.get_default_height_width(image, height, width)
            crops_coords = self.mask_processor.get_crop_region(mask_image, width, height, pad=padding_mask_crop)
            resize_mode = 'fill'
        else:
            crops_coords = None
            resize_mode = 'default'
        original_image = image
        init_image = self.image_processor.preprocess(image, height=height, width=width, crops_coords=crops_coords, resize_mode=resize_mode)
        init_image = init_image.to(dtype=torch.float32)
        if isinstance(controlnet, ControlNetModel): control_image = self.prepare_control_image(image=control_image, width=width, height=height, batch_size=batch_size * num_images_per_prompt,
        num_images_per_prompt=num_images_per_prompt, device=device, dtype=controlnet.dtype, crops_coords=crops_coords, resize_mode=resize_mode, do_classifier_free_guidance=self.do_classifier_free_guidance, guess_mode=guess_mode)
        elif isinstance(controlnet, MultiControlNetModel):
            control_images = []
            for control_image_ in control_image:
                control_image_ = self.prepare_control_image(image=control_image_, width=width, height=height, batch_size=batch_size * num_images_per_prompt, num_images_per_prompt=num_images_per_prompt,
                device=device, dtype=controlnet.dtype, crops_coords=crops_coords, resize_mode=resize_mode, do_classifier_free_guidance=self.do_classifier_free_guidance, guess_mode=guess_mode)
                control_images.append(control_image_)
            control_image = control_images
        else: raise ValueError(f'{controlnet.__class__} is not supported.')
        mask = self.mask_processor.preprocess(mask_image, height=height, width=width, resize_mode=resize_mode, crops_coords=crops_coords)
        masked_image = init_image * (mask < 0.5)
        _, _, height, width = init_image.shape
        num_channels_latents = self.vae.config.latent_channels
        num_channels_unet = self.unet.config.in_channels
        return_image_latents = num_channels_unet == 4
        add_noise = True if denoising_start is None else False
        latents_outputs = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents, image=init_image, timestep=latent_timestep,
        is_strength_max=is_strength_max, add_noise=add_noise, return_noise=True, return_image_latents=return_image_latents)
        if return_image_latents: latents, noise, image_latents = latents_outputs
        else: latents, noise = latents_outputs
        mask, masked_image_latents = self.prepare_mask_latents(mask, masked_image, batch_size * num_images_per_prompt, height, width, prompt_embeds.dtype, device, generator, self.do_classifier_free_guidance)
        if num_channels_unet == 9:
            num_channels_mask = mask.shape[1]
            num_channels_masked_image = masked_image_latents.shape[1]
            if num_channels_latents + num_channels_mask + num_channels_masked_image != self.unet.config.in_channels: raise ValueError(f'Incorrect configuration settings! The config of `pipeline.unet`: {self.unet.config} expects {self.unet.config.in_channels} but received `num_channels_latents`: {num_channels_latents} + `num_channels_mask`: {num_channels_mask} + `num_channels_masked_image`: {num_channels_masked_image} = {num_channels_latents + num_channels_masked_image + num_channels_mask}. Please verify the config of `pipeline.unet` or your `mask_image` or `image` input.')
        elif num_channels_unet != 4: raise ValueError(f'The unet {self.unet.__class__} should have either 4 or 9 input channels, not {self.unet.config.in_channels}.')
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        controlnet_keep = []
        for i in range(len(timesteps)):
            keeps = [1.0 - float(i / len(timesteps) < s or (i + 1) / len(timesteps) > e) for s, e in zip(control_guidance_start, control_guidance_end)]
            controlnet_keep.append(keeps if isinstance(controlnet, MultiControlNetModel) else keeps[0])
        height, width = latents.shape[-2:]
        height = height * self.vae_scale_factor
        width = width * self.vae_scale_factor
        original_size = original_size or (height, width)
        target_size = target_size or (height, width)
        add_text_embeds = pooled_prompt_embeds
        if self.text_encoder_2 is None: text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1])
        else: text_encoder_projection_dim = self.text_encoder_2.config.projection_dim
        add_time_ids, add_neg_time_ids = self._get_add_time_ids(original_size, crops_coords_top_left, target_size, aesthetic_score, negative_aesthetic_score,
        dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim)
        add_time_ids = add_time_ids.repeat(batch_size * num_images_per_prompt, 1)
        if self.do_classifier_free_guidance:
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
            add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
            add_neg_time_ids = add_neg_time_ids.repeat(batch_size * num_images_per_prompt, 1)
            add_time_ids = torch.cat([add_neg_time_ids, add_time_ids], dim=0)
        prompt_embeds = prompt_embeds.to(device)
        add_text_embeds = add_text_embeds.to(device)
        add_time_ids = add_time_ids.to(device)
        num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
        if denoising_end is not None and denoising_start is not None and denoising_value_valid(denoising_end) and denoising_value_valid(denoising_start) and (denoising_start >= denoising_end): raise ValueError(f'`denoising_start`: {denoising_start} cannot be larger than or equal to `denoising_end`: ' + f' {denoising_end} when using type float.')
        elif denoising_end is not None and denoising_value_valid(denoising_end):
            discrete_timestep_cutoff = int(round(self.scheduler.config.num_train_timesteps - denoising_end * self.scheduler.config.num_train_timesteps))
            num_inference_steps = len(list(filter(lambda ts: ts >= discrete_timestep_cutoff, timesteps)))
            timesteps = timesteps[:num_inference_steps]
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if self.interrupt: continue
                latent_model_input = torch.cat([latents] * 2) if self.do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                added_cond_kwargs = {'text_embeds': add_text_embeds, 'time_ids': add_time_ids}
                if guess_mode and self.do_classifier_free_guidance:
                    control_model_input = latents
                    control_model_input = self.scheduler.scale_model_input(control_model_input, t)
                    controlnet_prompt_embeds = prompt_embeds.chunk(2)[1]
                    controlnet_added_cond_kwargs = {'text_embeds': add_text_embeds.chunk(2)[1], 'time_ids': add_time_ids.chunk(2)[1]}
                else:
                    control_model_input = latent_model_input
                    controlnet_prompt_embeds = prompt_embeds
                    controlnet_added_cond_kwargs = added_cond_kwargs
                if isinstance(controlnet_keep[i], list): cond_scale = [c * s for c, s in zip(controlnet_conditioning_scale, controlnet_keep[i])]
                else:
                    controlnet_cond_scale = controlnet_conditioning_scale
                    if isinstance(controlnet_cond_scale, list): controlnet_cond_scale = controlnet_cond_scale[0]
                    cond_scale = controlnet_cond_scale * controlnet_keep[i]
                down_block_res_samples, mid_block_res_sample = self.controlnet(control_model_input, t, encoder_hidden_states=controlnet_prompt_embeds, controlnet_cond=control_image, conditioning_scale=cond_scale,
                guess_mode=guess_mode, added_cond_kwargs=controlnet_added_cond_kwargs, return_dict=False)
                if guess_mode and self.do_classifier_free_guidance:
                    down_block_res_samples = [torch.cat([torch.zeros_like(d), d]) for d in down_block_res_samples]
                    mid_block_res_sample = torch.cat([torch.zeros_like(mid_block_res_sample), mid_block_res_sample])
                if ip_adapter_image is not None or ip_adapter_image_embeds is not None: added_cond_kwargs['image_embeds'] = image_embeds
                if num_channels_unet == 9: latent_model_input = torch.cat([latent_model_input, mask, masked_image_latents], dim=1)
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=self.cross_attention_kwargs, down_block_additional_residuals=down_block_res_samples,
                mid_block_additional_residual=mid_block_res_sample, added_cond_kwargs=added_cond_kwargs, return_dict=False)[0]
                if self.do_classifier_free_guidance:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                if self.do_classifier_free_guidance and guidance_rescale > 0.0: noise_pred = rescale_noise_cfg(noise_pred, noise_pred_text, guidance_rescale=guidance_rescale)
                latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
                if num_channels_unet == 4:
                    init_latents_proper = image_latents
                    if self.do_classifier_free_guidance: init_mask, _ = mask.chunk(2)
                    else: init_mask = mask
                    if i < len(timesteps) - 1:
                        noise_timestep = timesteps[i + 1]
                        init_latents_proper = self.scheduler.add_noise(init_latents_proper, noise, torch.tensor([noise_timestep]))
                    latents = (1 - init_mask) * init_latents_proper + init_mask * latents
                if callback_on_step_end is not None:
                    callback_kwargs = {}
                    for k in callback_on_step_end_tensor_inputs: callback_kwargs[k] = locals()[k]
                    callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                    latents = callback_outputs.pop('latents', latents)
                    prompt_embeds = callback_outputs.pop('prompt_embeds', prompt_embeds)
                    negative_prompt_embeds = callback_outputs.pop('negative_prompt_embeds', negative_prompt_embeds)
                if i == len(timesteps) - 1 or (i + 1 > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                    progress_bar.update()
                    if callback is not None and i % callback_steps == 0:
                        step_idx = i // getattr(self.scheduler, 'order', 1)
                        callback(step_idx, t, latents)
        if self.vae.dtype == torch.float16 and self.vae.config.force_upcast:
            self.upcast_vae()
            latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
        if hasattr(self, 'final_offload_hook') and self.final_offload_hook is not None:
            self.unet.to('cpu')
            self.controlnet.to('cpu')
            torch.cuda.empty_cache()
        if not output_type == 'latent': image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
        else: return StableDiffusionXLPipelineOutput(images=latents)
        if self.watermark is not None: image = self.watermark.apply_watermark(image)
        image = self.image_processor.postprocess(image, output_type=output_type)
        if padding_mask_crop is not None: image = [self.image_processor.apply_overlay(mask_image, original_image, i, crops_coords) for i in image]
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return StableDiffusionXLPipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
