'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Dict, List, Optional, Tuple, Union
import torch
from ...models import AutoencoderKL, DiTTransformer2DModel
from ...schedulers import KarrasDiffusionSchedulers
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class DiTPipeline(DiffusionPipeline):
    model_cpu_offload_seq = 'transformer->vae'
    def __init__(self, transformer: DiTTransformer2DModel, vae: AutoencoderKL, scheduler: KarrasDiffusionSchedulers, id2label: Optional[Dict[int, str]]=None):
        super().__init__()
        self.register_modules(transformer=transformer, vae=vae, scheduler=scheduler)
        self.labels = {}
        if id2label is not None:
            for key, value in id2label.items():
                for label in value.split(','): self.labels[label.lstrip().rstrip()] = int(key)
            self.labels = dict(sorted(self.labels.items()))
    def get_label_ids(self, label: Union[str, List[str]]) -> List[int]:
        """Returns:"""
        if not isinstance(label, list): label = list(label)
        for l in label:
            if l not in self.labels: raise ValueError(f'{l} does not exist. Please make sure to select one of the following labels: \n {self.labels}.')
        return [self.labels[l] for l in label]
    @torch.no_grad()
    def __call__(self, class_labels: List[int], guidance_scale: float=4.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, num_inference_steps: int=50,
    output_type: Optional[str]='pil', return_dict: bool=True) -> Union[ImagePipelineOutput, Tuple]:
        """Examples:"""
        batch_size = len(class_labels)
        latent_size = self.transformer.config.sample_size
        latent_channels = self.transformer.config.in_channels
        latents = randn_tensor(shape=(batch_size, latent_channels, latent_size, latent_size), generator=generator, device=self._execution_device, dtype=self.transformer.dtype)
        latent_model_input = torch.cat([latents] * 2) if guidance_scale > 1 else latents
        class_labels = torch.tensor(class_labels, device=self._execution_device).reshape(-1)
        class_null = torch.tensor([1000] * batch_size, device=self._execution_device)
        class_labels_input = torch.cat([class_labels, class_null], 0) if guidance_scale > 1 else class_labels
        self.scheduler.set_timesteps(num_inference_steps)
        for t in self.progress_bar(self.scheduler.timesteps):
            if guidance_scale > 1:
                half = latent_model_input[:len(latent_model_input) // 2]
                latent_model_input = torch.cat([half, half], dim=0)
            latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            timesteps = t
            if not torch.is_tensor(timesteps):
                is_mps = latent_model_input.device.type == 'mps'
                if isinstance(timesteps, float): dtype = torch.float32 if is_mps else torch.float64
                else: dtype = torch.int32 if is_mps else torch.int64
                timesteps = torch.tensor([timesteps], dtype=dtype, device=latent_model_input.device)
            elif len(timesteps.shape) == 0: timesteps = timesteps[None].to(latent_model_input.device)
            timesteps = timesteps.expand(latent_model_input.shape[0])
            noise_pred = self.transformer(latent_model_input, timestep=timesteps, class_labels=class_labels_input).sample
            if guidance_scale > 1:
                eps, rest = (noise_pred[:, :latent_channels], noise_pred[:, latent_channels:])
                cond_eps, uncond_eps = torch.split(eps, len(eps) // 2, dim=0)
                half_eps = uncond_eps + guidance_scale * (cond_eps - uncond_eps)
                eps = torch.cat([half_eps, half_eps], dim=0)
                noise_pred = torch.cat([eps, rest], dim=1)
            if self.transformer.config.out_channels // 2 == latent_channels: model_output, _ = torch.split(noise_pred, latent_channels, dim=1)
            else: model_output = noise_pred
            latent_model_input = self.scheduler.step(model_output, t, latent_model_input).prev_sample
        if guidance_scale > 1: latents, _ = latent_model_input.chunk(2, dim=0)
        else: latents = latent_model_input
        latents = 1 / self.vae.config.scaling_factor * latents
        samples = self.vae.decode(latents).sample
        samples = (samples / 2 + 0.5).clamp(0, 1)
        samples = samples.cpu().permute(0, 2, 3, 1).float().numpy()
        if output_type == 'pil': samples = self.numpy_to_pil(samples)
        self.maybe_free_model_hooks()
        if not return_dict: return (samples,)
        return ImagePipelineOutput(images=samples)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
