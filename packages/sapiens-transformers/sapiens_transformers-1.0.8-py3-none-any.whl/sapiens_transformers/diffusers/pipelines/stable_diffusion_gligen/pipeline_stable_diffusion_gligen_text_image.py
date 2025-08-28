'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPImageProcessor, CLIPProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection
from ...image_processor import VaeImageProcessor
from ...loaders import StableDiffusionLoraLoaderMixin, TextualInversionLoaderMixin
from ...models import AutoencoderKL, UNet2DConditionModel
from ...models.attention import GatedSelfAttentionDense
from ...models.lora import adjust_lora_scale_text_encoder
from ...schedulers import KarrasDiffusionSchedulers
from ...utils import USE_PEFT_BACKEND, replace_example_docstring, scale_lora_layers, unscale_lora_layers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, StableDiffusionMixin
from ..stable_diffusion import StableDiffusionPipelineOutput
from ..stable_diffusion.clip_image_project_model import CLIPImageProjection
from ..stable_diffusion.safety_checker import StableDiffusionSafetyChecker
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import torch\n        >>> from sapiens_transformers.diffusers import StableDiffusionGLIGENTextImagePipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n\n        >>> # Insert objects described by image at the region defined by bounding boxes\n        >>> pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(\n        ...     "anhnct/Gligen_Inpainting_Text_Image", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n\n        >>> input_image = load_image(\n        ...     "https://hf.co/datasets/huggingface/documentation-images/resolve/main/diffusers/gligen/livingroom_modern.png"\n        ... )\n        >>> prompt = "a backpack"\n        >>> boxes = [[0.2676, 0.4088, 0.4773, 0.7183]]\n        >>> phrases = None\n        >>> gligen_image = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/gligen/backpack.jpeg"\n        ... )\n\n        >>> images = pipe(\n        ...     prompt=prompt,\n        ...     gligen_phrases=phrases,\n        ...     gligen_inpaint_image=input_image,\n        ...     gligen_boxes=boxes,\n        ...     gligen_images=[gligen_image],\n        ...     gligen_scheduled_sampling_beta=1,\n        ...     output_type="pil",\n        ...     num_inference_steps=50,\n        ... ).images\n\n        >>> images[0].save("./gligen-inpainting-text-image-box.jpg")\n\n        >>> # Generate an image described by the prompt and\n        >>> # insert objects described by text and image at the region defined by bounding boxes\n        >>> pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(\n        ...     "anhnct/Gligen_Text_Image", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n\n        >>> prompt = "a flower sitting on the beach"\n        >>> boxes = [[0.0, 0.09, 0.53, 0.76]]\n        >>> phrases = ["flower"]\n        >>> gligen_image = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/gligen/pexels-pixabay-60597.jpg"\n        ... )\n\n        >>> images = pipe(\n        ...     prompt=prompt,\n        ...     gligen_phrases=phrases,\n        ...     gligen_images=[gligen_image],\n        ...     gligen_boxes=boxes,\n        ...     gligen_scheduled_sampling_beta=1,\n        ...     output_type="pil",\n        ...     num_inference_steps=50,\n        ... ).images\n\n        >>> images[0].save("./gligen-generation-text-image-box.jpg")\n\n        >>> # Generate an image described by the prompt and\n        >>> # transfer style described by image at the region defined by bounding boxes\n        >>> pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(\n        ...     "anhnct/Gligen_Text_Image", torch_dtype=torch.float16\n        ... )\n        >>> pipe = pipe.to("cuda")\n\n        >>> prompt = "a dragon flying on the sky"\n        >>> boxes = [[0.4, 0.2, 1.0, 0.8], [0.0, 1.0, 0.0, 1.0]]  # Set `[0.0, 1.0, 0.0, 1.0]` for the style\n\n        >>> gligen_image = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/landscape.png"\n        ... )\n\n        >>> gligen_placeholder = load_image(\n        ...     "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/landscape.png"\n        ... )\n\n        >>> images = pipe(\n        ...     prompt=prompt,\n        ...     gligen_phrases=[\n        ...         "dragon",\n        ...         "placeholder",\n        ...     ],  # Can use any text instead of `placeholder` token, because we will use mask here\n        ...     gligen_images=[\n        ...         gligen_placeholder,\n        ...         gligen_image,\n        ...     ],  # Can use any image in gligen_placeholder, because we will use mask here\n        ...     input_phrases_mask=[1, 0],  # Set 0 for the placeholder token\n        ...     input_images_mask=[0, 1],  # Set 0 for the placeholder image\n        ...     gligen_boxes=boxes,\n        ...     gligen_scheduled_sampling_beta=1,\n        ...     output_type="pil",\n        ...     num_inference_steps=50,\n        ... ).images\n\n        >>> images[0].save("./gligen-generation-text-image-box-style-transfer.jpg")\n        ```\n'
class StableDiffusionGLIGENTextImagePipeline(DiffusionPipeline, StableDiffusionMixin):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    _optional_components = ['safety_checker', 'feature_extractor']
    _exclude_from_cpu_offload = ['safety_checker']
    def __init__(self, vae: AutoencoderKL, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, processor: CLIPProcessor, image_encoder: CLIPVisionModelWithProjection,
    image_project: CLIPImageProjection, unet: UNet2DConditionModel, scheduler: KarrasDiffusionSchedulers, safety_checker: StableDiffusionSafetyChecker,
    feature_extractor: CLIPImageProcessor, requires_safety_checker: bool=True):
        super().__init__()
        if safety_checker is not None and feature_extractor is None: raise ValueError("Make sure to define a feature extractor when loading {self.__class__} if you want to use the safety checker. If you do not want to use the safety checker, you can pass `'safety_checker=None'` instead.")
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, image_encoder=image_encoder, processor=processor, image_project=image_project, unet=unet,
        scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.image_processor = VaeImageProcessor(vae_scale_factor=self.vae_scale_factor, do_convert_rgb=True)
        self.register_to_config(requires_safety_checker=requires_safety_checker)
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
    def prepare_extra_step_kwargs(self, generator, eta):
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta: extra_step_kwargs['eta'] = eta
        accepts_generator = 'generator' in set(inspect.signature(self.scheduler.step).parameters.keys())
        if accepts_generator: extra_step_kwargs['generator'] = generator
        return extra_step_kwargs
    def check_inputs(self, prompt, height, width, callback_steps, gligen_images, gligen_phrases, negative_prompt=None, prompt_embeds=None,
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
        if gligen_images is not None and gligen_phrases is not None:
            if len(gligen_images) != len(gligen_phrases): raise ValueError(f'`gligen_images` and `gligen_phrases` must have the same length when both are provided, but got: `gligen_images` with length {len(gligen_images)} != `gligen_phrases` with length {len(gligen_phrases)}.')
    def prepare_latents(self, batch_size, num_channels_latents, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels_latents, int(height) // self.vae_scale_factor, int(width) // self.vae_scale_factor)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def enable_fuser(self, enabled=True):
        for module in self.unet.modules():
            if type(module) is GatedSelfAttentionDense: module.enabled = enabled
    def draw_inpaint_mask_from_boxes(self, boxes, size):
        inpaint_mask = torch.ones(size[0], size[1])
        for box in boxes:
            x0, x1 = (box[0] * size[0], box[2] * size[0])
            y0, y1 = (box[1] * size[1], box[3] * size[1])
            inpaint_mask[int(y0):int(y1), int(x0):int(x1)] = 0
        return inpaint_mask
    def crop(self, im, new_width, new_height):
        width, height = im.size
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        return im.crop((left, top, right, bottom))
    def target_size_center_crop(self, im, new_hw):
        width, height = im.size
        if width != height: im = self.crop(im, min(height, width), min(height, width))
        return im.resize((new_hw, new_hw), PIL.Image.LANCZOS)
    def complete_mask(self, has_mask, max_objs, device):
        mask = torch.ones(1, max_objs).type(self.text_encoder.dtype).to(device)
        if has_mask is None: return mask
        if isinstance(has_mask, int): return mask * has_mask
        else:
            for idx, value in enumerate(has_mask): mask[0, idx] = value
            return mask
    def get_clip_feature(self, input, normalize_constant, device, is_image=False):
        if is_image:
            if input is None: return None
            inputs = self.processor(images=[input], return_tensors='pt').to(device)
            inputs['pixel_values'] = inputs['pixel_values'].to(self.image_encoder.dtype)
            outputs = self.image_encoder(**inputs)
            feature = outputs.image_embeds
            feature = self.image_project(feature).squeeze(0)
            feature = feature / feature.norm() * normalize_constant
            feature = feature.unsqueeze(0)
        else:
            if input is None: return None
            inputs = self.tokenizer(input, return_tensors='pt', padding=True).to(device)
            outputs = self.text_encoder(**inputs)
            feature = outputs.pooler_output
        return feature
    def get_cross_attention_kwargs_with_grounded(self, hidden_size, gligen_phrases, gligen_images, gligen_boxes, input_phrases_mask,
    input_images_mask, repeat_batch, normalize_constant, max_objs, device):
        phrases, images = (gligen_phrases, gligen_images)
        images = [None] * len(phrases) if images is None else images
        phrases = [None] * len(images) if phrases is None else phrases
        boxes = torch.zeros(max_objs, 4, device=device, dtype=self.text_encoder.dtype)
        masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        phrases_masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        image_masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        phrases_embeddings = torch.zeros(max_objs, hidden_size, device=device, dtype=self.text_encoder.dtype)
        image_embeddings = torch.zeros(max_objs, hidden_size, device=device, dtype=self.text_encoder.dtype)
        text_features = []
        image_features = []
        for phrase, image in zip(phrases, images):
            text_features.append(self.get_clip_feature(phrase, normalize_constant, device, is_image=False))
            image_features.append(self.get_clip_feature(image, normalize_constant, device, is_image=True))
        for idx, (box, text_feature, image_feature) in enumerate(zip(gligen_boxes, text_features, image_features)):
            boxes[idx] = torch.tensor(box)
            masks[idx] = 1
            if text_feature is not None:
                phrases_embeddings[idx] = text_feature
                phrases_masks[idx] = 1
            if image_feature is not None:
                image_embeddings[idx] = image_feature
                image_masks[idx] = 1
        input_phrases_mask = self.complete_mask(input_phrases_mask, max_objs, device)
        phrases_masks = phrases_masks.unsqueeze(0).repeat(repeat_batch, 1) * input_phrases_mask
        input_images_mask = self.complete_mask(input_images_mask, max_objs, device)
        image_masks = image_masks.unsqueeze(0).repeat(repeat_batch, 1) * input_images_mask
        boxes = boxes.unsqueeze(0).repeat(repeat_batch, 1, 1)
        masks = masks.unsqueeze(0).repeat(repeat_batch, 1)
        phrases_embeddings = phrases_embeddings.unsqueeze(0).repeat(repeat_batch, 1, 1)
        image_embeddings = image_embeddings.unsqueeze(0).repeat(repeat_batch, 1, 1)
        out = {'boxes': boxes, 'masks': masks, 'phrases_masks': phrases_masks, 'image_masks': image_masks, 'phrases_embeddings': phrases_embeddings, 'image_embeddings': image_embeddings}
        return out
    def get_cross_attention_kwargs_without_grounded(self, hidden_size, repeat_batch, max_objs, device):
        boxes = torch.zeros(max_objs, 4, device=device, dtype=self.text_encoder.dtype)
        masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        phrases_masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        image_masks = torch.zeros(max_objs, device=device, dtype=self.text_encoder.dtype)
        phrases_embeddings = torch.zeros(max_objs, hidden_size, device=device, dtype=self.text_encoder.dtype)
        image_embeddings = torch.zeros(max_objs, hidden_size, device=device, dtype=self.text_encoder.dtype)
        out = {'boxes': boxes.unsqueeze(0).repeat(repeat_batch, 1, 1), 'masks': masks.unsqueeze(0).repeat(repeat_batch, 1), 'phrases_masks': phrases_masks.unsqueeze(0).repeat(repeat_batch, 1), 'image_masks': image_masks.unsqueeze(0).repeat(repeat_batch, 1), 'phrases_embeddings': phrases_embeddings.unsqueeze(0).repeat(repeat_batch, 1, 1), 'image_embeddings': image_embeddings.unsqueeze(0).repeat(repeat_batch, 1, 1)}
        return out
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: Union[str, List[str]]=None, height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: int=50, guidance_scale: float=7.5,
    gligen_scheduled_sampling_beta: float=0.3, gligen_phrases: List[str]=None, gligen_images: List[PIL.Image.Image]=None, input_phrases_mask: Union[int, List[int]]=None,
    input_images_mask: Union[int, List[int]]=None, gligen_boxes: List[List[float]]=None, gligen_inpaint_image: Optional[PIL.Image.Image]=None,
    negative_prompt: Optional[Union[str, List[str]]]=None, num_images_per_prompt: Optional[int]=1, eta: float=0.0, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, prompt_embeds: Optional[torch.Tensor]=None, negative_prompt_embeds: Optional[torch.Tensor]=None,
    output_type: Optional[str]='pil', return_dict: bool=True, callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1,
    cross_attention_kwargs: Optional[Dict[str, Any]]=None, gligen_normalize_constant: float=28.7, clip_skip: int=None):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, callback_steps, gligen_images, gligen_phrases, negative_prompt, prompt_embeds, negative_prompt_embeds)
        if prompt is not None and isinstance(prompt, str): batch_size = 1
        elif prompt is not None and isinstance(prompt, list): batch_size = len(prompt)
        else: batch_size = prompt_embeds.shape[0]
        device = self._execution_device
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds, negative_prompt_embeds = self.encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt,
        prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds, clip_skip=clip_skip)
        if do_classifier_free_guidance: prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        self.scheduler.set_timesteps(num_inference_steps, device=device)
        timesteps = self.scheduler.timesteps
        num_channels_latents = self.unet.config.in_channels
        latents = self.prepare_latents(batch_size * num_images_per_prompt, num_channels_latents, height, width, prompt_embeds.dtype, device, generator, latents)
        max_objs = 30
        if len(gligen_boxes) > max_objs:
            gligen_phrases = gligen_phrases[:max_objs]
            gligen_boxes = gligen_boxes[:max_objs]
            gligen_images = gligen_images[:max_objs]
        repeat_batch = batch_size * num_images_per_prompt
        if do_classifier_free_guidance: repeat_batch = repeat_batch * 2
        if cross_attention_kwargs is None: cross_attention_kwargs = {}
        hidden_size = prompt_embeds.shape[2]
        cross_attention_kwargs['gligen'] = self.get_cross_attention_kwargs_with_grounded(hidden_size=hidden_size, gligen_phrases=gligen_phrases, gligen_images=gligen_images,
        gligen_boxes=gligen_boxes, input_phrases_mask=input_phrases_mask, input_images_mask=input_images_mask, repeat_batch=repeat_batch,
        normalize_constant=gligen_normalize_constant, max_objs=max_objs, device=device)
        cross_attention_kwargs_without_grounded = {}
        cross_attention_kwargs_without_grounded['gligen'] = self.get_cross_attention_kwargs_without_grounded(hidden_size=hidden_size, repeat_batch=repeat_batch, max_objs=max_objs, device=device)
        if gligen_inpaint_image is not None:
            if gligen_inpaint_image.size != (self.vae.sample_size, self.vae.sample_size): gligen_inpaint_image = self.target_size_center_crop(gligen_inpaint_image, self.vae.sample_size)
            gligen_inpaint_image = self.image_processor.preprocess(gligen_inpaint_image)
            gligen_inpaint_image = gligen_inpaint_image.to(dtype=self.vae.dtype, device=self.vae.device)
            gligen_inpaint_latent = self.vae.encode(gligen_inpaint_image).latent_dist.sample()
            gligen_inpaint_latent = self.vae.config.scaling_factor * gligen_inpaint_latent
            gligen_inpaint_mask = self.draw_inpaint_mask_from_boxes(gligen_boxes, gligen_inpaint_latent.shape[2:])
            gligen_inpaint_mask = gligen_inpaint_mask.to(dtype=gligen_inpaint_latent.dtype, device=gligen_inpaint_latent.device)
            gligen_inpaint_mask = gligen_inpaint_mask[None, None]
            gligen_inpaint_mask_addition = torch.cat((gligen_inpaint_latent * gligen_inpaint_mask, gligen_inpaint_mask), dim=1)
            gligen_inpaint_mask_addition = gligen_inpaint_mask_addition.expand(repeat_batch, -1, -1, -1).clone()
        int(gligen_scheduled_sampling_beta * len(timesteps))
        self.enable_fuser(True)
        extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)
        num_warmup_steps = len(timesteps) - num_inference_steps * self.scheduler.order
        with self.progress_bar(total=num_inference_steps) as progress_bar:
            for i, t in enumerate(timesteps):
                if latents.shape[1] != 4: latents = torch.randn_like(latents[:, :4])
                if gligen_inpaint_image is not None:
                    gligen_inpaint_latent_with_noise = self.scheduler.add_noise(gligen_inpaint_latent, torch.randn_like(gligen_inpaint_latent), torch.tensor([t])).expand(latents.shape[0], -1, -1, -1).clone()
                    latents = gligen_inpaint_latent_with_noise * gligen_inpaint_mask + latents * (1 - gligen_inpaint_mask)
                latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
                latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                if gligen_inpaint_image is not None: latent_model_input = torch.cat((latent_model_input, gligen_inpaint_mask_addition), dim=1)
                noise_pred_with_grounding = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs).sample
                noise_pred_without_grounding = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds, cross_attention_kwargs=cross_attention_kwargs_without_grounded).sample
                if do_classifier_free_guidance:
                    _, noise_pred_text = noise_pred_with_grounding.chunk(2)
                    noise_pred_uncond, _ = noise_pred_without_grounding.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                else: noise_pred = noise_pred_with_grounding
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
