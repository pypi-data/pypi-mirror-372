'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Union
import PIL.Image
import torch
from sapiens_transformers import CLIPTokenizer
from ...models import AutoencoderKL, ControlNetModel, UNet2DConditionModel
from ...schedulers import PNDMScheduler
from ...utils import replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..blip_diffusion.blip_image_processing import BlipImageProcessor
from ..blip_diffusion.modeling_blip2 import Blip2QFormerModel
from ..blip_diffusion.modeling_ctx_clip import ContextCLIPTextModel
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> from sapiens_transformers.diffusers.pipelines import BlipDiffusionControlNetPipeline\n        >>> from sapiens_transformers.diffusers.utils import load_image\n        >>> from controlnet_aux import CannyDetector\n        >>> import torch\n\n        >>> blip_diffusion_pipe = BlipDiffusionControlNetPipeline.from_pretrained(\n        ...     "Salesforce/blipdiffusion-controlnet", torch_dtype=torch.float16\n        ... ).to("cuda")\n\n        >>> style_subject = "flower"\n        >>> tgt_subject = "teapot"\n        >>> text_prompt = "on a marble table"\n\n        >>> cldm_cond_image = load_image(\n        ...     "https://huggingface.co/datasets/ayushtues/blipdiffusion_images/resolve/main/kettle.jpg"\n        ... ).resize((512, 512))\n        >>> canny = CannyDetector()\n        >>> cldm_cond_image = canny(cldm_cond_image, 30, 70, output_type="pil")\n        >>> style_image = load_image(\n        ...     "https://huggingface.co/datasets/ayushtues/blipdiffusion_images/resolve/main/flower.jpg"\n        ... )\n        >>> guidance_scale = 7.5\n        >>> num_inference_steps = 50\n        >>> negative_prompt = "over-exposure, under-exposure, saturated, duplicate, out of frame, lowres, cropped, worst quality, low quality, jpeg artifacts, morbid, mutilated, out of frame, ugly, bad anatomy, bad proportions, deformed, blurry, duplicate"\n\n\n        >>> output = blip_diffusion_pipe(\n        ...     text_prompt,\n        ...     style_image,\n        ...     cldm_cond_image,\n        ...     style_subject,\n        ...     tgt_subject,\n        ...     guidance_scale=guidance_scale,\n        ...     num_inference_steps=num_inference_steps,\n        ...     neg_prompt=negative_prompt,\n        ...     height=512,\n        ...     width=512,\n        ... ).images\n        >>> output[0].save("image.png")\n        ```\n'
class BlipDiffusionControlNetPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'qformer->text_encoder->unet->vae'
    def __init__(self, tokenizer: CLIPTokenizer, text_encoder: ContextCLIPTextModel, vae: AutoencoderKL, unet: UNet2DConditionModel, scheduler: PNDMScheduler, qformer: Blip2QFormerModel,
    controlnet: ControlNetModel, image_processor: BlipImageProcessor, ctx_begin_pos: int=2, mean: List[float]=None, std: List[float]=None):
        super().__init__()
        self.register_modules(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, unet=unet, scheduler=scheduler, qformer=qformer, controlnet=controlnet, image_processor=image_processor)
        self.register_to_config(ctx_begin_pos=ctx_begin_pos, mean=mean, std=std)
    def get_query_embeddings(self, input_image, src_subject): return self.qformer(image_input=input_image, text_input=src_subject, return_dict=False)
    def _build_prompt(self, prompts, tgt_subjects, prompt_strength=1.0, prompt_reps=20):
        rv = []
        for prompt, tgt_subject in zip(prompts, tgt_subjects):
            prompt = f'a {tgt_subject} {prompt.strip()}'
            rv.append(', '.join([prompt] * int(prompt_strength * prompt_reps)))
        return rv
    def prepare_latents(self, batch_size, num_channels, height, width, dtype, device, generator, latents=None):
        shape = (batch_size, num_channels, height, width)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(shape, generator=generator, device=device, dtype=dtype)
        else: latents = latents.to(device=device, dtype=dtype)
        latents = latents * self.scheduler.init_noise_sigma
        return latents
    def encode_prompt(self, query_embeds, prompt, device=None):
        device = device or self._execution_device
        max_len = self.text_encoder.text_model.config.max_position_embeddings
        max_len -= self.qformer.config.num_query_tokens
        tokenized_prompt = self.tokenizer(prompt, padding='max_length', truncation=True, max_length=max_len, return_tensors='pt').to(device)
        batch_size = query_embeds.shape[0]
        ctx_begin_pos = [self.config.ctx_begin_pos] * batch_size
        text_embeddings = self.text_encoder(input_ids=tokenized_prompt.input_ids, ctx_embeddings=query_embeds, ctx_begin_pos=ctx_begin_pos)[0]
        return text_embeddings
    def prepare_control_image(self, image, width, height, batch_size, num_images_per_prompt, device, dtype, do_classifier_free_guidance=False):
        image = self.image_processor.preprocess(image, size={'width': width, 'height': height}, do_rescale=True, do_center_crop=False, do_normalize=False, return_tensors='pt')['pixel_values'].to(device)
        image_batch_size = image.shape[0]
        if image_batch_size == 1: repeat_by = batch_size
        else: repeat_by = num_images_per_prompt
        image = image.repeat_interleave(repeat_by, dim=0)
        image = image.to(device=device, dtype=dtype)
        if do_classifier_free_guidance: image = torch.cat([image] * 2)
        return image
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt: List[str], reference_image: PIL.Image.Image, condtioning_image: PIL.Image.Image, source_subject_category: List[str], target_subject_category: List[str],
    latents: Optional[torch.Tensor]=None, guidance_scale: float=7.5, height: int=512, width: int=512, num_inference_steps: int=50, generator: Optional[Union[torch.Generator,
    List[torch.Generator]]]=None, neg_prompt: Optional[str]='', prompt_strength: float=1.0, prompt_reps: int=20, output_type: Optional[str]='pil', return_dict: bool=True):
        """Examples:"""
        device = self._execution_device
        reference_image = self.image_processor.preprocess(reference_image, image_mean=self.config.mean, image_std=self.config.std, return_tensors='pt')['pixel_values']
        reference_image = reference_image.to(device)
        if isinstance(prompt, str): prompt = [prompt]
        if isinstance(source_subject_category, str): source_subject_category = [source_subject_category]
        if isinstance(target_subject_category, str): target_subject_category = [target_subject_category]
        batch_size = len(prompt)
        prompt = self._build_prompt(prompts=prompt, tgt_subjects=target_subject_category, prompt_strength=prompt_strength, prompt_reps=prompt_reps)
        query_embeds = self.get_query_embeddings(reference_image, source_subject_category)
        text_embeddings = self.encode_prompt(query_embeds, prompt, device)
        do_classifier_free_guidance = guidance_scale > 1.0
        if do_classifier_free_guidance:
            max_length = self.text_encoder.text_model.config.max_position_embeddings
            uncond_input = self.tokenizer([neg_prompt] * batch_size, padding='max_length', max_length=max_length, return_tensors='pt')
            uncond_embeddings = self.text_encoder(input_ids=uncond_input.input_ids.to(device), ctx_embeddings=None)[0]
            text_embeddings = torch.cat([uncond_embeddings, text_embeddings])
        scale_down_factor = 2 ** (len(self.unet.config.block_out_channels) - 1)
        latents = self.prepare_latents(batch_size=batch_size, num_channels=self.unet.config.in_channels, height=height // scale_down_factor,
        width=width // scale_down_factor, generator=generator, latents=latents, dtype=self.unet.dtype, device=device)
        extra_set_kwargs = {}
        self.scheduler.set_timesteps(num_inference_steps, **extra_set_kwargs)
        cond_image = self.prepare_control_image(image=condtioning_image, width=width, height=height, batch_size=batch_size, num_images_per_prompt=1, device=device, dtype=self.controlnet.dtype,
        do_classifier_free_guidance=do_classifier_free_guidance)
        for i, t in enumerate(self.progress_bar(self.scheduler.timesteps)):
            do_classifier_free_guidance = guidance_scale > 1.0
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            down_block_res_samples, mid_block_res_sample = self.controlnet(latent_model_input, t, encoder_hidden_states=text_embeddings, controlnet_cond=cond_image, return_dict=False)
            noise_pred = self.unet(latent_model_input, timestep=t, encoder_hidden_states=text_embeddings, down_block_additional_residuals=down_block_res_samples,
            mid_block_additional_residual=mid_block_res_sample)['sample']
            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
            latents = self.scheduler.step(noise_pred, t, latents)['prev_sample']
        image = self.vae.decode(latents / self.vae.config.scaling_factor, return_dict=False)[0]
        image = self.image_processor.postprocess(image, output_type=output_type)
        self.maybe_free_model_hooks()
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
