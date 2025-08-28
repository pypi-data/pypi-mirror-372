'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from PIL import Image
from tqdm.auto import tqdm
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ...image_processor import PipelineImageInput
from ...models import AutoencoderKL, UNet2DConditionModel
from ...schedulers import DDIMScheduler, LCMScheduler
from ...utils import BaseOutput, replace_example_docstring
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline
from .marigold_image_processing import MarigoldImageProcessor
EXAMPLE_DOC_STRING = '\nExamples:\n```py\n>>> import sapiens_transformers.diffusers\n>>> import torch\n\n>>> pipe = diffusers.MarigoldNormalsPipeline.from_pretrained(\n...     "prs-eth/marigold-normals-lcm-v0-1", variant="fp16", torch_dtype=torch.float16\n... ).to("cuda")\n\n>>> image = diffusers.utils.load_image("https://marigoldmonodepth.github.io/images/einstein.jpg")\n>>> normals = pipe(image)\n\n>>> vis = pipe.image_processor.visualize_normals(normals.prediction)\n>>> vis[0].save("einstein_normals.png")\n```\n'
@dataclass
class MarigoldNormalsOutput(BaseOutput):
    """Args:"""
    prediction: Union[np.ndarray, torch.Tensor]
    uncertainty: Union[None, np.ndarray, torch.Tensor]
    latent: Union[None, torch.Tensor]
class MarigoldNormalsPipeline(DiffusionPipeline):
    """Args:"""
    model_cpu_offload_seq = 'text_encoder->unet->vae'
    supported_prediction_types = ('normals',)
    def __init__(self, unet: UNet2DConditionModel, vae: AutoencoderKL, scheduler: Union[DDIMScheduler, LCMScheduler], text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer,
    prediction_type: Optional[str]=None, use_full_z_range: Optional[bool]=True, default_denoising_steps: Optional[int]=None, default_processing_resolution: Optional[int]=None):
        super().__init__()
        self.register_modules(unet=unet, vae=vae, scheduler=scheduler, text_encoder=text_encoder, tokenizer=tokenizer)
        self.register_to_config(use_full_z_range=use_full_z_range, default_denoising_steps=default_denoising_steps, default_processing_resolution=default_processing_resolution)
        self.vae_scale_factor = 2 ** (len(self.vae.config.block_out_channels) - 1)
        self.use_full_z_range = use_full_z_range
        self.default_denoising_steps = default_denoising_steps
        self.default_processing_resolution = default_processing_resolution
        self.empty_text_embedding = None
        self.image_processor = MarigoldImageProcessor(vae_scale_factor=self.vae_scale_factor)
    def check_inputs(self, image: PipelineImageInput, num_inference_steps: int, ensemble_size: int, processing_resolution: int, resample_method_input: str, resample_method_output: str,
    batch_size: int, ensembling_kwargs: Optional[Dict[str, Any]], latents: Optional[torch.Tensor], generator: Optional[Union[torch.Generator,
    List[torch.Generator]]], output_type: str, output_uncertainty: bool) -> int:
        if num_inference_steps is None: raise ValueError('`num_inference_steps` is not specified and could not be resolved from the model config.')
        if num_inference_steps < 1: raise ValueError('`num_inference_steps` must be positive.')
        if ensemble_size < 1: raise ValueError('`ensemble_size` must be positive.')
        if ensemble_size == 1 and output_uncertainty: raise ValueError('Computing uncertainty by setting `output_uncertainty=True` also requires setting `ensemble_size` greater than 1.')
        if processing_resolution is None: raise ValueError('`processing_resolution` is not specified and could not be resolved from the model config.')
        if processing_resolution < 0: raise ValueError('`processing_resolution` must be non-negative: 0 for native resolution, or any positive value for downsampled processing.')
        if processing_resolution % self.vae_scale_factor != 0: raise ValueError(f'`processing_resolution` must be a multiple of {self.vae_scale_factor}.')
        if resample_method_input not in ('nearest', 'nearest-exact', 'bilinear', 'bicubic', 'area'): raise ValueError('`resample_method_input` takes string values compatible with PIL library: nearest, nearest-exact, bilinear, bicubic, area.')
        if resample_method_output not in ('nearest', 'nearest-exact', 'bilinear', 'bicubic', 'area'): raise ValueError('`resample_method_output` takes string values compatible with PIL library: nearest, nearest-exact, bilinear, bicubic, area.')
        if batch_size < 1: raise ValueError('`batch_size` must be positive.')
        if output_type not in ['pt', 'np']: raise ValueError('`output_type` must be one of `pt` or `np`.')
        if latents is not None and generator is not None: raise ValueError('`latents` and `generator` cannot be used together.')
        if ensembling_kwargs is not None:
            if not isinstance(ensembling_kwargs, dict): raise ValueError('`ensembling_kwargs` must be a dictionary.')
            if 'reduction' in ensembling_kwargs and ensembling_kwargs['reduction'] not in ('closest', 'mean'): raise ValueError("`ensembling_kwargs['reduction']` can be either `'closest'` or `'mean'`.")
        num_images = 0
        W, H = (None, None)
        if not isinstance(image, list): image = [image]
        for i, img in enumerate(image):
            if isinstance(img, np.ndarray) or torch.is_tensor(img):
                if img.ndim not in (2, 3, 4): raise ValueError(f'`image[{i}]` has unsupported dimensions or shape: {img.shape}.')
                H_i, W_i = img.shape[-2:]
                N_i = 1
                if img.ndim == 4: N_i = img.shape[0]
            elif isinstance(img, Image.Image):
                W_i, H_i = img.size
                N_i = 1
            else: raise ValueError(f'Unsupported `image[{i}]` type: {type(img)}.')
            if W is None: W, H = (W_i, H_i)
            elif (W, H) != (W_i, H_i): raise ValueError(f'Input `image[{i}]` has incompatible dimensions {(W_i, H_i)} with the previous images {(W, H)}')
            num_images += N_i
        if latents is not None:
            if not torch.is_tensor(latents): raise ValueError('`latents` must be a torch.Tensor.')
            if latents.dim() != 4: raise ValueError(f'`latents` has unsupported dimensions or shape: {latents.shape}.')
            if processing_resolution > 0:
                max_orig = max(H, W)
                new_H = H * processing_resolution // max_orig
                new_W = W * processing_resolution // max_orig
                if new_H == 0 or new_W == 0: raise ValueError(f'Extreme aspect ratio of the input image: [{W} x {H}]')
                W, H = (new_W, new_H)
            w = (W + self.vae_scale_factor - 1) // self.vae_scale_factor
            h = (H + self.vae_scale_factor - 1) // self.vae_scale_factor
            shape_expected = (num_images * ensemble_size, self.vae.config.latent_channels, h, w)
            if latents.shape != shape_expected: raise ValueError(f'`latents` has unexpected shape={latents.shape} expected={shape_expected}.')
        if generator is not None:
            if isinstance(generator, list):
                if len(generator) != num_images * ensemble_size: raise ValueError('The number of generators must match the total number of ensemble members for all input images.')
                if not all((g.device.type == generator[0].device.type for g in generator)): raise ValueError('`generator` device placement is not consistent in the list.')
            elif not isinstance(generator, torch.Generator): raise ValueError(f'Unsupported generator type: {type(generator)}.')
        return num_images
    def progress_bar(self, iterable=None, total=None, desc=None, leave=True):
        if not hasattr(self, '_progress_bar_config'): self._progress_bar_config = {}
        elif not isinstance(self._progress_bar_config, dict): raise ValueError(f'`self._progress_bar_config` should be of type `dict`, but is {type(self._progress_bar_config)}.')
        progress_bar_config = dict(**self._progress_bar_config)
        progress_bar_config['desc'] = progress_bar_config.get('desc', desc)
        progress_bar_config['leave'] = progress_bar_config.get('leave', leave)
        if iterable is not None: return tqdm(iterable, **progress_bar_config)
        elif total is not None: return tqdm(total=total, **progress_bar_config)
        else: raise ValueError('Either `total` or `iterable` has to be defined.')
    @torch.no_grad()
    @replace_example_docstring(EXAMPLE_DOC_STRING)
    def __call__(self, image: PipelineImageInput, num_inference_steps: Optional[int]=None, ensemble_size: int=1, processing_resolution: Optional[int]=None, match_input_resolution: bool=True,
    resample_method_input: str='bilinear', resample_method_output: str='bilinear', batch_size: int=1, ensembling_kwargs: Optional[Dict[str, Any]]=None,
    latents: Optional[Union[torch.Tensor, List[torch.Tensor]]]=None, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None,
    output_type: str='np', output_uncertainty: bool=False, output_latent: bool=False, return_dict: bool=True):
        """Examples:"""
        device = self._execution_device
        dtype = self.dtype
        if num_inference_steps is None: num_inference_steps = self.default_denoising_steps
        if processing_resolution is None: processing_resolution = self.default_processing_resolution
        num_images = self.check_inputs(image, num_inference_steps, ensemble_size, processing_resolution, resample_method_input, resample_method_output, batch_size,
        ensembling_kwargs, latents, generator, output_type, output_uncertainty)
        if self.empty_text_embedding is None:
            prompt = ''
            text_inputs = self.tokenizer(prompt, padding='do_not_pad', max_length=self.tokenizer.model_max_length, truncation=True, return_tensors='pt')
            text_input_ids = text_inputs.input_ids.to(device)
            self.empty_text_embedding = self.text_encoder(text_input_ids)[0]
        image, padding, original_resolution = self.image_processor.preprocess(image, processing_resolution, resample_method_input, device, dtype)
        image_latent, pred_latent = self.prepare_latents(image, latents, generator, ensemble_size, batch_size)
        del image
        batch_empty_text_embedding = self.empty_text_embedding.to(device=device, dtype=dtype).repeat(batch_size, 1, 1)
        pred_latents = []
        for i in self.progress_bar(range(0, num_images * ensemble_size, batch_size), leave=True, desc='Marigold predictions...'):
            batch_image_latent = image_latent[i:i + batch_size]
            batch_pred_latent = pred_latent[i:i + batch_size]
            effective_batch_size = batch_image_latent.shape[0]
            text = batch_empty_text_embedding[:effective_batch_size]
            self.scheduler.set_timesteps(num_inference_steps, device=device)
            for t in self.progress_bar(self.scheduler.timesteps, leave=False, desc='Diffusion steps...'):
                batch_latent = torch.cat([batch_image_latent, batch_pred_latent], dim=1)
                noise = self.unet(batch_latent, t, encoder_hidden_states=text, return_dict=False)[0]
                batch_pred_latent = self.scheduler.step(noise, t, batch_pred_latent, generator=generator).prev_sample
            pred_latents.append(batch_pred_latent)
        pred_latent = torch.cat(pred_latents, dim=0)
        del (pred_latents, image_latent, batch_empty_text_embedding, batch_image_latent, batch_pred_latent, text, batch_latent, noise)
        prediction = torch.cat([self.decode_prediction(pred_latent[i:i + batch_size]) for i in range(0, pred_latent.shape[0], batch_size)], dim=0)
        if not output_latent: pred_latent = None
        prediction = self.image_processor.unpad_image(prediction, padding)
        uncertainty = None
        if ensemble_size > 1:
            prediction = prediction.reshape(num_images, ensemble_size, *prediction.shape[1:])
            prediction = [self.ensemble_normals(prediction[i], output_uncertainty, **ensembling_kwargs or {}) for i in range(num_images)]
            prediction, uncertainty = zip(*prediction)
            prediction = torch.cat(prediction, dim=0)
            if output_uncertainty: uncertainty = torch.cat(uncertainty, dim=0)
            else: uncertainty = None
        if match_input_resolution:
            prediction = self.image_processor.resize_antialias(prediction, original_resolution, resample_method_output, is_aa=False)
            prediction = self.normalize_normals(prediction)
            if uncertainty is not None and output_uncertainty: uncertainty = self.image_processor.resize_antialias(uncertainty, original_resolution, resample_method_output, is_aa=False)
        if output_type == 'np':
            prediction = self.image_processor.pt_to_numpy(prediction)
            if uncertainty is not None and output_uncertainty: uncertainty = self.image_processor.pt_to_numpy(uncertainty)
        self.maybe_free_model_hooks()
        if not return_dict: return (prediction, uncertainty, pred_latent)
        return MarigoldNormalsOutput(prediction=prediction, uncertainty=uncertainty, latent=pred_latent)
    def prepare_latents(self, image: torch.Tensor, latents: Optional[torch.Tensor], generator: Optional[torch.Generator],
    ensemble_size: int, batch_size: int) -> Tuple[torch.Tensor, torch.Tensor]:
        def retrieve_latents(encoder_output):
            if hasattr(encoder_output, 'latent_dist'): return encoder_output.latent_dist.mode()
            elif hasattr(encoder_output, 'latents'): return encoder_output.latents
            else: raise AttributeError('Could not access latents of provided encoder_output')
        image_latent = torch.cat([retrieve_latents(self.vae.encode(image[i:i + batch_size])) for i in range(0, image.shape[0], batch_size)], dim=0)
        image_latent = image_latent * self.vae.config.scaling_factor
        image_latent = image_latent.repeat_interleave(ensemble_size, dim=0)
        pred_latent = latents
        if pred_latent is None: pred_latent = randn_tensor(image_latent.shape, generator=generator, device=image_latent.device, dtype=image_latent.dtype)
        return (image_latent, pred_latent)
    def decode_prediction(self, pred_latent: torch.Tensor) -> torch.Tensor:
        if pred_latent.dim() != 4 or pred_latent.shape[1] != self.vae.config.latent_channels: raise ValueError(f'Expecting 4D tensor of shape [B,{self.vae.config.latent_channels},H,W]; got {pred_latent.shape}.')
        prediction = self.vae.decode(pred_latent / self.vae.config.scaling_factor, return_dict=False)[0]
        prediction = torch.clip(prediction, -1.0, 1.0)
        if not self.use_full_z_range:
            prediction[:, 2, :, :] *= 0.5
            prediction[:, 2, :, :] += 0.5
        prediction = self.normalize_normals(prediction)
        return prediction
    @staticmethod
    def normalize_normals(normals: torch.Tensor, eps: float=1e-06) -> torch.Tensor:
        if normals.dim() != 4 or normals.shape[1] != 3: raise ValueError(f'Expecting 4D tensor of shape [B,3,H,W]; got {normals.shape}.')
        norm = torch.norm(normals, dim=1, keepdim=True)
        normals /= norm.clamp(min=eps)
        return normals
    @staticmethod
    def ensemble_normals(normals: torch.Tensor, output_uncertainty: bool, reduction: str='closest') -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Returns:"""
        if normals.dim() != 4 or normals.shape[1] != 3: raise ValueError(f'Expecting 4D tensor of shape [B,3,H,W]; got {normals.shape}.')
        if reduction not in ('closest', 'mean'): raise ValueError(f'Unrecognized reduction method: {reduction}.')
        mean_normals = normals.mean(dim=0, keepdim=True)
        mean_normals = MarigoldNormalsPipeline.normalize_normals(mean_normals)
        sim_cos = (mean_normals * normals).sum(dim=1, keepdim=True)
        sim_cos = sim_cos.clamp(-1, 1)
        uncertainty = None
        if output_uncertainty:
            uncertainty = sim_cos.arccos()
            uncertainty = uncertainty.mean(dim=0, keepdim=True) / np.pi
        if reduction == 'mean': return (mean_normals, uncertainty)
        closest_indices = sim_cos.argmax(dim=0, keepdim=True)
        closest_indices = closest_indices.repeat(1, 3, 1, 1)
        closest_normals = torch.gather(normals, 0, closest_indices)
        return (closest_normals, uncertainty)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
