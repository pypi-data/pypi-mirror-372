'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from functools import partial
from typing import Dict, List, Optional, Union
import jax
import jax.numpy as jnp
import numpy as np
from flax.core.frozen_dict import FrozenDict
from flax.jax_utils import unreplicate
from flax.training.common_utils import shard
from PIL import Image
from sapiens_transformers import CLIPImageProcessor, CLIPTokenizer, FlaxCLIPTextModel
from ...models import FlaxAutoencoderKL, FlaxUNet2DConditionModel
from ...schedulers import FlaxDDIMScheduler, FlaxDPMSolverMultistepScheduler, FlaxLMSDiscreteScheduler, FlaxPNDMScheduler
from ...utils import PIL_INTERPOLATION, replace_example_docstring
from ..pipeline_flax_utils import FlaxDiffusionPipeline
from .pipeline_output import FlaxStableDiffusionPipelineOutput
from .safety_checker_flax import FlaxStableDiffusionSafetyChecker
DEBUG = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import jax\n        >>> import numpy as np\n        >>> import jax.numpy as jnp\n        >>> from flax.jax_utils import replicate\n        >>> from flax.training.common_utils import shard\n        >>> import requests\n        >>> from io import BytesIO\n        >>> from PIL import Image\n        >>> from sapiens_transformers.diffusers import FlaxStableDiffusionImg2ImgPipeline\n\n\n        >>> def create_key(seed=0):\n        ...     return jax.random.PRNGKey(seed)\n\n\n        >>> rng = create_key(0)\n\n        >>> url = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"\n        >>> response = requests.get(url)\n        >>> init_img = Image.open(BytesIO(response.content)).convert("RGB")\n        >>> init_img = init_img.resize((768, 512))\n\n        >>> prompts = "A fantasy landscape, trending on artstation"\n\n        >>> pipeline, params = FlaxStableDiffusionImg2ImgPipeline.from_pretrained(\n        ...     "CompVis/stable-diffusion-v1-4",\n        ...     revision="flax",\n        ...     dtype=jnp.bfloat16,\n        ... )\n\n        >>> num_samples = jax.device_count()\n        >>> rng = jax.random.split(rng, jax.device_count())\n        >>> prompt_ids, processed_image = pipeline.prepare_inputs(\n        ...     prompt=[prompts] * num_samples, image=[init_img] * num_samples\n        ... )\n        >>> p_params = replicate(params)\n        >>> prompt_ids = shard(prompt_ids)\n        >>> processed_image = shard(processed_image)\n\n        >>> output = pipeline(\n        ...     prompt_ids=prompt_ids,\n        ...     image=processed_image,\n        ...     params=p_params,\n        ...     prng_seed=rng,\n        ...     strength=0.75,\n        ...     num_inference_steps=50,\n        ...     jit=True,\n        ...     height=512,\n        ...     width=768,\n        ... ).images\n\n        >>> output_images = pipeline.numpy_to_pil(np.asarray(output.reshape((num_samples,) + output.shape[-3:])))\n        ```\n'
class FlaxStableDiffusionImg2ImgPipeline(FlaxDiffusionPipeline):
    """Args:"""
    def __init__(self, vae: FlaxAutoencoderKL, text_encoder: FlaxCLIPTextModel, tokenizer: CLIPTokenizer, unet: FlaxUNet2DConditionModel, scheduler: Union[FlaxDDIMScheduler, FlaxPNDMScheduler,
    FlaxLMSDiscreteScheduler, FlaxDPMSolverMultistepScheduler], safety_checker: FlaxStableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, dtype: jnp.dtype=jnp.float32):
        super().__init__()
        self.dtype = dtype
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
    def prepare_inputs(self, prompt: Union[str, List[str]], image: Union[Image.Image, List[Image.Image]]):
        if not isinstance(prompt, (str, list)): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if not isinstance(image, (Image.Image, list)): raise ValueError(f'image has to be of type `PIL.Image.Image` or list but is {type(image)}')
        if isinstance(image, Image.Image): image = [image]
        processed_images = jnp.concatenate([preprocess(img, jnp.float32) for img in image])
        text_input = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='np')
        return (text_input.input_ids, processed_images)
    def _get_has_nsfw_concepts(self, features, params):
        has_nsfw_concepts = self.safety_checker(features, params)
        return has_nsfw_concepts
    def _run_safety_checker(self, images, safety_model_params, jit=False):
        pil_images = [Image.fromarray(image) for image in images]
        features = self.feature_extractor(pil_images, return_tensors='np').pixel_values
        if jit:
            features = shard(features)
            has_nsfw_concepts = _p_get_has_nsfw_concepts(self, features, safety_model_params)
            has_nsfw_concepts = unshard(has_nsfw_concepts)
            safety_model_params = unreplicate(safety_model_params)
        else: has_nsfw_concepts = self._get_has_nsfw_concepts(features, safety_model_params)
        images_was_copied = False
        for idx, has_nsfw_concept in enumerate(has_nsfw_concepts):
            if has_nsfw_concept:
                if not images_was_copied:
                    images_was_copied = True
                    images = images.copy()
                images[idx] = np.zeros(images[idx].shape, dtype=np.uint8)
        return (images, has_nsfw_concepts)
    def get_timestep_start(self, num_inference_steps, strength):
        init_timestep = min(int(num_inference_steps * strength), num_inference_steps)
        t_start = max(num_inference_steps - init_timestep, 0)
        return t_start
    def _generate(self, prompt_ids: jnp.ndarray, image: jnp.ndarray, params: Union[Dict, FrozenDict], prng_seed: jax.Array, start_timestep: int, num_inference_steps: int, height: int,
    width: int, guidance_scale: float, noise: Optional[jnp.ndarray]=None, neg_prompt_ids: Optional[jnp.ndarray]=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        prompt_embeds = self.text_encoder(prompt_ids, params=params['text_encoder'])[0]
        batch_size = prompt_ids.shape[0]
        max_length = prompt_ids.shape[-1]
        if neg_prompt_ids is None: uncond_input = self.tokenizer([''] * batch_size, padding='max_length', max_length=max_length, return_tensors='np').input_ids
        else: uncond_input = neg_prompt_ids
        negative_prompt_embeds = self.text_encoder(uncond_input, params=params['text_encoder'])[0]
        context = jnp.concatenate([negative_prompt_embeds, prompt_embeds])
        latents_shape = (batch_size, self.unet.config.in_channels, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if noise is None: noise = jax.random.normal(prng_seed, shape=latents_shape, dtype=jnp.float32)
        elif noise.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {noise.shape}, expected {latents_shape}')
        init_latent_dist = self.vae.apply({'params': params['vae']}, image, method=self.vae.encode).latent_dist
        init_latents = init_latent_dist.sample(key=prng_seed).transpose((0, 3, 1, 2))
        init_latents = self.vae.config.scaling_factor * init_latents
        def loop_body(step, args):
            latents, scheduler_state = args
            latents_input = jnp.concatenate([latents] * 2)
            t = jnp.array(scheduler_state.timesteps, dtype=jnp.int32)[step]
            timestep = jnp.broadcast_to(t, latents_input.shape[0])
            latents_input = self.scheduler.scale_model_input(scheduler_state, latents_input, t)
            noise_pred = self.unet.apply({'params': params['unet']}, jnp.array(latents_input), jnp.array(timestep, dtype=jnp.int32), encoder_hidden_states=context).sample
            noise_pred_uncond, noise_prediction_text = jnp.split(noise_pred, 2, axis=0)
            noise_pred = noise_pred_uncond + guidance_scale * (noise_prediction_text - noise_pred_uncond)
            latents, scheduler_state = self.scheduler.step(scheduler_state, noise_pred, t, latents).to_tuple()
            return (latents, scheduler_state)
        scheduler_state = self.scheduler.set_timesteps(params['scheduler'], num_inference_steps=num_inference_steps, shape=latents_shape)
        latent_timestep = scheduler_state.timesteps[start_timestep:start_timestep + 1].repeat(batch_size)
        latents = self.scheduler.add_noise(params['scheduler'], init_latents, noise, latent_timestep)
        latents = latents * params['scheduler'].init_noise_sigma
        if DEBUG:
            for i in range(start_timestep, num_inference_steps): latents, scheduler_state = loop_body(i, (latents, scheduler_state))
        else: latents, _ = jax.lax.fori_loop(start_timestep, num_inference_steps, loop_body, (latents, scheduler_state))
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.apply({'params': params['vae']}, latents, method=self.vae.decode).sample
        image = (image / 2 + 0.5).clip(0, 1).transpose(0, 2, 3, 1)
        return image
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt_ids: jnp.ndarray, image: jnp.ndarray, params: Union[Dict, FrozenDict], prng_seed: jax.Array, strength: float=0.8, num_inference_steps: int=50,
    height: Optional[int]=None, width: Optional[int]=None, guidance_scale: Union[float, jnp.ndarray]=7.5, noise: jnp.ndarray=None,
    neg_prompt_ids: jnp.ndarray=None, return_dict: bool=True, jit: bool=False):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        if isinstance(guidance_scale, float):
            guidance_scale = jnp.array([guidance_scale] * prompt_ids.shape[0])
            if len(prompt_ids.shape) > 2: guidance_scale = guidance_scale[:, None]
        start_timestep = self.get_timestep_start(num_inference_steps, strength)
        if jit: images = _p_generate(self, prompt_ids, image, params, prng_seed, start_timestep, num_inference_steps, height, width, guidance_scale, noise, neg_prompt_ids)
        else: images = self._generate(prompt_ids, image, params, prng_seed, start_timestep, num_inference_steps, height, width, guidance_scale, noise, neg_prompt_ids)
        if self.safety_checker is not None:
            safety_params = params['safety_checker']
            images_uint8_casted = (images * 255).round().astype('uint8')
            num_devices, batch_size = images.shape[:2]
            images_uint8_casted = np.asarray(images_uint8_casted).reshape(num_devices * batch_size, height, width, 3)
            images_uint8_casted, has_nsfw_concept = self._run_safety_checker(images_uint8_casted, safety_params, jit)
            images = np.asarray(images)
            if any(has_nsfw_concept):
                for i, is_nsfw in enumerate(has_nsfw_concept):
                    if is_nsfw: images[i] = np.asarray(images_uint8_casted[i])
            images = images.reshape(num_devices, batch_size, height, width, 3)
        else:
            images = np.asarray(images)
            has_nsfw_concept = False
        if not return_dict: return (images, has_nsfw_concept)
        return FlaxStableDiffusionPipelineOutput(images=images, nsfw_content_detected=has_nsfw_concept)
@partial(jax.pmap, in_axes=(None, 0, 0, 0, 0, None, None, None, None, 0, 0, 0), static_broadcasted_argnums=(0, 5, 6, 7, 8))
def _p_generate(pipe, prompt_ids, image, params, prng_seed, start_timestep, num_inference_steps, height, width, guidance_scale, noise, neg_prompt_ids): return pipe._generate(prompt_ids,
image, params, prng_seed, start_timestep, num_inference_steps, height, width, guidance_scale, noise, neg_prompt_ids)
@partial(jax.pmap, static_broadcasted_argnums=(0,))
def _p_get_has_nsfw_concepts(pipe, features, params): return pipe._get_has_nsfw_concepts(features, params)
def unshard(x: jnp.ndarray):
    num_devices, batch_size = x.shape[:2]
    rest = x.shape[2:]
    return x.reshape(num_devices * batch_size, *rest)
def preprocess(image, dtype):
    w, h = image.size
    w, h = (x - x % 32 for x in (w, h))
    image = image.resize((w, h), resample=PIL_INTERPOLATION['lanczos'])
    image = jnp.array(image).astype(dtype) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    return 2.0 * image - 1.0
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
