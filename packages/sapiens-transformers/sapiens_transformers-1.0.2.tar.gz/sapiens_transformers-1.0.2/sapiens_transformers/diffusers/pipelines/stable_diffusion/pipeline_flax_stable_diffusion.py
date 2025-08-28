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
from packaging import version
from PIL import Image
from sapiens_transformers import CLIPImageProcessor, CLIPTokenizer, FlaxCLIPTextModel
from ...models import FlaxAutoencoderKL, FlaxUNet2DConditionModel
from ...schedulers import FlaxDDIMScheduler, FlaxDPMSolverMultistepScheduler, FlaxLMSDiscreteScheduler, FlaxPNDMScheduler
from ...utils import deprecate, replace_example_docstring
from ..pipeline_flax_utils import FlaxDiffusionPipeline
from .pipeline_output import FlaxStableDiffusionPipelineOutput
from .safety_checker_flax import FlaxStableDiffusionSafetyChecker
DEBUG = False
EXAMPLE_DOC_STRING = '\n    Examples:\n        ```py\n        >>> import jax\n        >>> import numpy as np\n        >>> from flax.jax_utils import replicate\n        >>> from flax.training.common_utils import shard\n\n        >>> from sapiens_transformers.diffusers import FlaxStableDiffusionPipeline\n\n        >>> pipeline, params = FlaxStableDiffusionPipeline.from_pretrained(\n        ...     "runwayml/stable-diffusion-v1-5", variant="bf16", dtype=jax.numpy.bfloat16\n        ... )\n\n        >>> prompt = "a photo of an astronaut riding a horse on mars"\n\n        >>> prng_seed = jax.random.PRNGKey(0)\n        >>> num_inference_steps = 50\n\n        >>> num_samples = jax.device_count()\n        >>> prompt = num_samples * [prompt]\n        >>> prompt_ids = pipeline.prepare_inputs(prompt)\n        # shard inputs and rng\n\n        >>> params = replicate(params)\n        >>> prng_seed = jax.random.split(prng_seed, jax.device_count())\n        >>> prompt_ids = shard(prompt_ids)\n\n        >>> images = pipeline(prompt_ids, params, prng_seed, num_inference_steps, jit=True).images\n        >>> images = pipeline.numpy_to_pil(np.asarray(images.reshape((num_samples,) + images.shape[-3:])))\n        ```\n'
class FlaxStableDiffusionPipeline(FlaxDiffusionPipeline):
    """Args:"""
    def __init__(self, vae: FlaxAutoencoderKL, text_encoder: FlaxCLIPTextModel, tokenizer: CLIPTokenizer, unet: FlaxUNet2DConditionModel, scheduler: Union[FlaxDDIMScheduler, FlaxPNDMScheduler,
    FlaxLMSDiscreteScheduler, FlaxDPMSolverMultistepScheduler], safety_checker: FlaxStableDiffusionSafetyChecker, feature_extractor: CLIPImageProcessor, dtype: jnp.dtype=jnp.float32):
        super().__init__()
        self.dtype = dtype
        is_unet_version_less_0_9_0 = hasattr(unet.config, '_diffusers_version') and version.parse(version.parse(unet.config._diffusers_version).base_version) < version.parse('0.9.0.dev0')
        is_unet_sample_size_less_64 = hasattr(unet.config, 'sample_size') and unet.config.sample_size < 64
        if is_unet_version_less_0_9_0 and is_unet_sample_size_less_64:
            deprecation_message = "The configuration file of the unet has set the default `sample_size` to smaller than 64 which seems highly unlikely .If you're checkpoint is a fine-tuned version of any of the following: \n- CompVis/stable-diffusion-v1-4 \n- CompVis/stable-diffusion-v1-3 \n- CompVis/stable-diffusion-v1-2 \n- CompVis/stable-diffusion-v1-1 \n- runwayml/stable-diffusion-v1-5 \n- runwayml/stable-diffusion-inpainting \n you should change 'sample_size' to 64 in the configuration file. Please make sure to update the config accordingly as leaving `sample_size=32` in the config might lead to incorrect results in future versions. If you have downloaded this checkpoint from the Sapiens Hub, it would be very nice if you could open a Pull request for the `unet/config.json` file"
            deprecate('sample_size<64', '1.0.0', deprecation_message, standard_warn=False)
            new_config = dict(unet.config)
            new_config['sample_size'] = 64
            unet._internal_dict = FrozenDict(new_config)
        self.register_modules(vae=vae, text_encoder=text_encoder, tokenizer=tokenizer, unet=unet, scheduler=scheduler, safety_checker=safety_checker, feature_extractor=feature_extractor)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
    def prepare_inputs(self, prompt: Union[str, List[str]]):
        if not isinstance(prompt, (str, list)): raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        text_input = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='np')
        return text_input.input_ids
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
    def _generate(self, prompt_ids: jnp.array, params: Union[Dict, FrozenDict], prng_seed: jax.Array, num_inference_steps: int, height: int, width: int, guidance_scale: float,
    latents: Optional[jnp.ndarray]=None, neg_prompt_ids: Optional[jnp.ndarray]=None):
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        prompt_embeds = self.text_encoder(prompt_ids, params=params['text_encoder'])[0]
        batch_size = prompt_ids.shape[0]
        max_length = prompt_ids.shape[-1]
        if neg_prompt_ids is None: uncond_input = self.tokenizer([''] * batch_size, padding='max_length', max_length=max_length, return_tensors='np').input_ids
        else: uncond_input = neg_prompt_ids
        negative_prompt_embeds = self.text_encoder(uncond_input, params=params['text_encoder'])[0]
        context = jnp.concatenate([negative_prompt_embeds, prompt_embeds])
        guidance_scale = jnp.array([guidance_scale], dtype=jnp.float32)
        latents_shape = (batch_size, self.unet.config.in_channels, height // self.vae_scale_factor, width // self.vae_scale_factor)
        if latents is None: latents = jax.random.normal(prng_seed, shape=latents_shape, dtype=jnp.float32)
        elif latents.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latents_shape}')
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
        scheduler_state = self.scheduler.set_timesteps(params['scheduler'], num_inference_steps=num_inference_steps, shape=latents.shape)
        latents = latents * params['scheduler'].init_noise_sigma
        if DEBUG:
            for i in range(num_inference_steps): latents, scheduler_state = loop_body(i, (latents, scheduler_state))
        else: latents, _ = jax.lax.fori_loop(0, num_inference_steps, loop_body, (latents, scheduler_state))
        latents = 1 / self.vae.config.scaling_factor * latents
        image = self.vae.apply({'params': params['vae']}, latents, method=self.vae.decode).sample
        image = (image / 2 + 0.5).clip(0, 1).transpose(0, 2, 3, 1)
        return image
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, prompt_ids: jnp.array, params: Union[Dict, FrozenDict], prng_seed: jax.Array, num_inference_steps: int=50, height: Optional[int]=None,
    width: Optional[int]=None, guidance_scale: Union[float, jnp.ndarray]=7.5, latents: jnp.ndarray=None, neg_prompt_ids: jnp.ndarray=None, return_dict: bool=True, jit: bool=False):
        """Examples:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        if isinstance(guidance_scale, float):
            guidance_scale = jnp.array([guidance_scale] * prompt_ids.shape[0])
            if len(prompt_ids.shape) > 2: guidance_scale = guidance_scale[:, None]
        if jit: images = _p_generate(self, prompt_ids, params, prng_seed, num_inference_steps, height, width, guidance_scale, latents, neg_prompt_ids)
        else: images = self._generate(prompt_ids, params, prng_seed, num_inference_steps, height, width, guidance_scale, latents, neg_prompt_ids)
        if self.safety_checker is not None:
            safety_params = params['safety_checker']
            images_uint8_casted = (images * 255).round().astype('uint8')
            num_devices, batch_size = images.shape[:2]
            images_uint8_casted = np.asarray(images_uint8_casted).reshape(num_devices * batch_size, height, width, 3)
            images_uint8_casted, has_nsfw_concept = self._run_safety_checker(images_uint8_casted, safety_params, jit)
            images = np.asarray(images).copy()
            if any(has_nsfw_concept):
                for i, is_nsfw in enumerate(has_nsfw_concept):
                    if is_nsfw: images[i, 0] = np.asarray(images_uint8_casted[i])
            images = images.reshape(num_devices, batch_size, height, width, 3)
        else:
            images = np.asarray(images)
            has_nsfw_concept = False
        if not return_dict: return (images, has_nsfw_concept)
        return FlaxStableDiffusionPipelineOutput(images=images, nsfw_content_detected=has_nsfw_concept)
@partial(jax.pmap, in_axes=(None, 0, 0, 0, None, None, None, 0, 0, 0), static_broadcasted_argnums=(0, 4, 5, 6))
def _p_generate(pipe, prompt_ids, params, prng_seed, num_inference_steps, height, width, guidance_scale, latents, neg_prompt_ids): return pipe._generate(prompt_ids,
params, prng_seed, num_inference_steps, height, width, guidance_scale, latents, neg_prompt_ids)
@partial(jax.pmap, static_broadcasted_argnums=(0,))
def _p_get_has_nsfw_concepts(pipe, features, params): return pipe._get_has_nsfw_concepts(features, params)
def unshard(x: jnp.ndarray):
    num_devices, batch_size = x.shape[:2]
    rest = x.shape[2:]
    return x.reshape(num_devices * batch_size, *rest)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
