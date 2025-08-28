'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Callable, List, Optional, Tuple, Union
import torch
from sapiens_transformers import CLIPTextModel, CLIPTokenizer
from ....configuration_utils import ConfigMixin, register_to_config
from ....models import ModelMixin, Transformer2DModel, VQModel
from ....schedulers import VQDiffusionScheduler
from ...pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class LearnedClassifierFreeSamplingEmbeddings(ModelMixin, ConfigMixin):
    @register_to_config
    def __init__(self, learnable: bool, hidden_size: Optional[int]=None, length: Optional[int]=None):
        super().__init__()
        self.learnable = learnable
        if self.learnable:
            assert hidden_size is not None, 'learnable=True requires `hidden_size` to be set'
            assert length is not None, 'learnable=True requires `length` to be set'
            embeddings = torch.zeros(length, hidden_size)
        else: embeddings = None
        self.embeddings = torch.nn.Parameter(embeddings)
class VQDiffusionPipeline(DiffusionPipeline):
    """Args:"""
    vqvae: VQModel
    text_encoder: CLIPTextModel
    tokenizer: CLIPTokenizer
    transformer: Transformer2DModel
    learned_classifier_free_sampling_embeddings: LearnedClassifierFreeSamplingEmbeddings
    scheduler: VQDiffusionScheduler
    def __init__(self, vqvae: VQModel, text_encoder: CLIPTextModel, tokenizer: CLIPTokenizer, transformer: Transformer2DModel,
    scheduler: VQDiffusionScheduler, learned_classifier_free_sampling_embeddings: LearnedClassifierFreeSamplingEmbeddings):
        super().__init__()
        self.register_modules(vqvae=vqvae, transformer=transformer, text_encoder=text_encoder, tokenizer=tokenizer, scheduler=scheduler,
        learned_classifier_free_sampling_embeddings=learned_classifier_free_sampling_embeddings)
    def _encode_prompt(self, prompt, num_images_per_prompt, do_classifier_free_guidance):
        batch_size = len(prompt) if isinstance(prompt, list) else 1
        text_inputs = self.tokenizer(prompt, padding='max_length', max_length=self.tokenizer.model_max_length, return_tensors='pt')
        text_input_ids = text_inputs.input_ids
        if text_input_ids.shape[-1] > self.tokenizer.model_max_length:
            removed_text = self.tokenizer.batch_decode(text_input_ids[:, self.tokenizer.model_max_length:])
            text_input_ids = text_input_ids[:, :self.tokenizer.model_max_length]
        prompt_embeds = self.text_encoder(text_input_ids.to(self.device))[0]
        prompt_embeds = prompt_embeds / prompt_embeds.norm(dim=-1, keepdim=True)
        prompt_embeds = prompt_embeds.repeat_interleave(num_images_per_prompt, dim=0)
        if do_classifier_free_guidance:
            if self.learned_classifier_free_sampling_embeddings.learnable:
                negative_prompt_embeds = self.learned_classifier_free_sampling_embeddings.embeddings
                negative_prompt_embeds = negative_prompt_embeds.unsqueeze(0).repeat(batch_size, 1, 1)
            else:
                uncond_tokens = [''] * batch_size
                max_length = text_input_ids.shape[-1]
                uncond_input = self.tokenizer(uncond_tokens, padding='max_length', max_length=max_length, truncation=True, return_tensors='pt')
                negative_prompt_embeds = self.text_encoder(uncond_input.input_ids.to(self.device))[0]
                negative_prompt_embeds = negative_prompt_embeds / negative_prompt_embeds.norm(dim=-1, keepdim=True)
            seq_len = negative_prompt_embeds.shape[1]
            negative_prompt_embeds = negative_prompt_embeds.repeat(1, num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(batch_size * num_images_per_prompt, seq_len, -1)
            prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds])
        return prompt_embeds
    @torch.no_grad()
    def __call__(self, prompt: Union[str, List[str]], num_inference_steps: int=100, guidance_scale: float=5.0, truncation_rate: float=1.0, num_images_per_prompt: int=1,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil', return_dict: bool=True,
    callback: Optional[Callable[[int, int, torch.Tensor], None]]=None, callback_steps: int=1) -> Union[ImagePipelineOutput, Tuple]:
        """Returns:"""
        if isinstance(prompt, str): batch_size = 1
        elif isinstance(prompt, list): batch_size = len(prompt)
        else: raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        batch_size = batch_size * num_images_per_prompt
        do_classifier_free_guidance = guidance_scale > 1.0
        prompt_embeds = self._encode_prompt(prompt, num_images_per_prompt, do_classifier_free_guidance)
        if callback_steps is None or (callback_steps is not None and (not isinstance(callback_steps, int) or callback_steps <= 0)): raise ValueError(f'`callback_steps` has to be a positive integer but is {callback_steps} of type {type(callback_steps)}.')
        latents_shape = (batch_size, self.transformer.num_latent_pixels)
        if latents is None:
            mask_class = self.transformer.num_vector_embeds - 1
            latents = torch.full(latents_shape, mask_class).to(self.device)
        else:
            if latents.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latents_shape}')
            if (latents < 0).any() or (latents >= self.transformer.num_vector_embeds).any(): raise ValueError(f'Unexpected latents value(s). All latents be valid embedding indices i.e. in the range 0, {self.transformer.num_vector_embeds - 1} (inclusive).')
            latents = latents.to(self.device)
        self.scheduler.set_timesteps(num_inference_steps, device=self.device)
        timesteps_tensor = self.scheduler.timesteps.to(self.device)
        sample = latents
        for i, t in enumerate(self.progress_bar(timesteps_tensor)):
            latent_model_input = torch.cat([sample] * 2) if do_classifier_free_guidance else sample
            model_output = self.transformer(latent_model_input, encoder_hidden_states=prompt_embeds, timestep=t).sample
            if do_classifier_free_guidance:
                model_output_uncond, model_output_text = model_output.chunk(2)
                model_output = model_output_uncond + guidance_scale * (model_output_text - model_output_uncond)
                model_output -= torch.logsumexp(model_output, dim=1, keepdim=True)
            model_output = self.truncate(model_output, truncation_rate)
            model_output = model_output.clamp(-70)
            sample = self.scheduler.step(model_output, timestep=t, sample=sample, generator=generator).prev_sample
            if callback is not None and i % callback_steps == 0: callback(i, t, sample)
        embedding_channels = self.vqvae.config.vq_embed_dim
        embeddings_shape = (batch_size, self.transformer.height, self.transformer.width, embedding_channels)
        embeddings = self.vqvae.quantize.get_codebook_entry(sample, shape=embeddings_shape)
        image = self.vqvae.decode(embeddings, force_not_quantize=True).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
    def truncate(self, log_p_x_0: torch.Tensor, truncation_rate: float) -> torch.Tensor:
        sorted_log_p_x_0, indices = torch.sort(log_p_x_0, 1, descending=True)
        sorted_p_x_0 = torch.exp(sorted_log_p_x_0)
        keep_mask = sorted_p_x_0.cumsum(dim=1) < truncation_rate
        all_true = torch.full_like(keep_mask[:, 0:1, :], True)
        keep_mask = torch.cat((all_true, keep_mask), dim=1)
        keep_mask = keep_mask[:, :-1, :]
        keep_mask = keep_mask.gather(1, indices.argsort(1))
        rv = log_p_x_0.clone()
        rv[~keep_mask] = -torch.inf
        return rv
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
