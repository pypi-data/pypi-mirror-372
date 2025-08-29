'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..attention_processor import ADDED_KV_ATTENTION_PROCESSORS, CROSS_ATTENTION_PROCESSORS, AttentionProcessor, AttnAddedKVProcessor, AttnProcessor
from ...loaders import PeftAdapterMixin, UNet2DConditionLoadersMixin
from ...configuration_utils import ConfigMixin, register_to_config
from ..embeddings import TimestepEmbedding, Timesteps
from ..attention import BasicTransformerBlock
from typing import Dict, Optional, Union
from ..modeling_utils import ModelMixin
from dataclasses import dataclass
from ...utils import BaseOutput
import torch.nn.functional as F
from torch import nn
import torch
@dataclass
class PriorTransformerOutput(BaseOutput):
    """Args:"""
    predicted_image_embedding: torch.Tensor
class PriorTransformer(ModelMixin, ConfigMixin, UNet2DConditionLoadersMixin, PeftAdapterMixin):
    @register_to_config
    def __init__(self, num_attention_heads: int=32, attention_head_dim: int=64, num_layers: int=20, embedding_dim: int=768, num_embeddings=77, additional_embeddings=4,
    dropout: float=0.0, time_embed_act_fn: str='silu', norm_in_type: Optional[str]=None, embedding_proj_norm_type: Optional[str]=None, encoder_hid_proj_type: Optional[str]='linear',
    added_emb_type: Optional[str]='prd', time_embed_dim: Optional[int]=None, embedding_proj_dim: Optional[int]=None, clip_embed_dim: Optional[int]=None):
        super().__init__()
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        inner_dim = num_attention_heads * attention_head_dim
        self.additional_embeddings = additional_embeddings
        time_embed_dim = time_embed_dim or inner_dim
        embedding_proj_dim = embedding_proj_dim or embedding_dim
        clip_embed_dim = clip_embed_dim or embedding_dim
        self.time_proj = Timesteps(inner_dim, True, 0)
        self.time_embedding = TimestepEmbedding(inner_dim, time_embed_dim, out_dim=inner_dim, act_fn=time_embed_act_fn)
        self.proj_in = nn.Linear(embedding_dim, inner_dim)
        if embedding_proj_norm_type is None: self.embedding_proj_norm = None
        elif embedding_proj_norm_type == 'layer': self.embedding_proj_norm = nn.LayerNorm(embedding_proj_dim)
        else: raise ValueError(f'unsupported embedding_proj_norm_type: {embedding_proj_norm_type}')
        self.embedding_proj = nn.Linear(embedding_proj_dim, inner_dim)
        if encoder_hid_proj_type is None: self.encoder_hidden_states_proj = None
        elif encoder_hid_proj_type == 'linear': self.encoder_hidden_states_proj = nn.Linear(embedding_dim, inner_dim)
        else: raise ValueError(f'unsupported encoder_hid_proj_type: {encoder_hid_proj_type}')
        self.positional_embedding = nn.Parameter(torch.zeros(1, num_embeddings + additional_embeddings, inner_dim))
        if added_emb_type == 'prd': self.prd_embedding = nn.Parameter(torch.zeros(1, 1, inner_dim))
        elif added_emb_type is None: self.prd_embedding = None
        else: raise ValueError(f"`added_emb_type`: {added_emb_type} is not supported. Make sure to choose one of `'prd'` or `None`.")
        self.transformer_blocks = nn.ModuleList([BasicTransformerBlock(inner_dim, num_attention_heads, attention_head_dim, dropout=dropout, activation_fn='gelu', attention_bias=True) for d in range(num_layers)])
        if norm_in_type == 'layer': self.norm_in = nn.LayerNorm(inner_dim)
        elif norm_in_type is None: self.norm_in = None
        else: raise ValueError(f'Unsupported norm_in_type: {norm_in_type}.')
        self.norm_out = nn.LayerNorm(inner_dim)
        self.proj_to_clip_embeddings = nn.Linear(inner_dim, clip_embed_dim)
        causal_attention_mask = torch.full([num_embeddings + additional_embeddings, num_embeddings + additional_embeddings], -10000.0)
        causal_attention_mask.triu_(1)
        causal_attention_mask = causal_attention_mask[None, ...]
        self.register_buffer('causal_attention_mask', causal_attention_mask, persistent=False)
        self.clip_mean = nn.Parameter(torch.zeros(1, clip_embed_dim))
        self.clip_std = nn.Parameter(torch.zeros(1, clip_embed_dim))
    @property
    def attn_processors(self) -> Dict[str, AttentionProcessor]:
        """Returns:"""
        processors = {}
        def fn_recursive_add_processors(name: str, module: torch.nn.Module, processors: Dict[str, AttentionProcessor]):
            if hasattr(module, 'get_processor'): processors[f'{name}.processor'] = module.get_processor()
            for sub_name, child in module.named_children(): fn_recursive_add_processors(f'{name}.{sub_name}', child, processors)
            return processors
        for name, module in self.named_children(): fn_recursive_add_processors(name, module, processors)
        return processors
    def set_attn_processor(self, processor: Union[AttentionProcessor, Dict[str, AttentionProcessor]]):
        count = len(self.attn_processors.keys())
        if isinstance(processor, dict) and len(processor) != count: raise ValueError(f'A dict of processors was passed, but the number of processors {len(processor)} does not match the number of attention layers: {count}. Please make sure to pass {count} processor classes.')
        def fn_recursive_attn_processor(name: str, module: torch.nn.Module, processor):
            if hasattr(module, 'set_processor'):
                if not isinstance(processor, dict): module.set_processor(processor)
                else: module.set_processor(processor.pop(f'{name}.processor'))
            for sub_name, child in module.named_children(): fn_recursive_attn_processor(f'{name}.{sub_name}', child, processor)
        for name, module in self.named_children(): fn_recursive_attn_processor(name, module, processor)
    def set_default_attn_processor(self):
        if all((proc.__class__ in ADDED_KV_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnAddedKVProcessor()
        elif all((proc.__class__ in CROSS_ATTENTION_PROCESSORS for proc in self.attn_processors.values())): processor = AttnProcessor()
        else: raise ValueError(f'Cannot call `set_default_attn_processor` when attention processors are of type {next(iter(self.attn_processors.values()))}')
        self.set_attn_processor(processor)
    def forward(self, hidden_states, timestep: Union[torch.Tensor, float, int], proj_embedding: torch.Tensor,
    encoder_hidden_states: Optional[torch.Tensor]=None, attention_mask: Optional[torch.BoolTensor]=None, return_dict: bool=True):
        """Returns:"""
        batch_size = hidden_states.shape[0]
        timesteps = timestep
        if not torch.is_tensor(timesteps): timesteps = torch.tensor([timesteps], dtype=torch.long, device=hidden_states.device)
        elif torch.is_tensor(timesteps) and len(timesteps.shape) == 0: timesteps = timesteps[None].to(hidden_states.device)
        timesteps = timesteps * torch.ones(batch_size, dtype=timesteps.dtype, device=timesteps.device)
        timesteps_projected = self.time_proj(timesteps)
        timesteps_projected = timesteps_projected.to(dtype=self.dtype)
        time_embeddings = self.time_embedding(timesteps_projected)
        if self.embedding_proj_norm is not None: proj_embedding = self.embedding_proj_norm(proj_embedding)
        proj_embeddings = self.embedding_proj(proj_embedding)
        if self.encoder_hidden_states_proj is not None and encoder_hidden_states is not None: encoder_hidden_states = self.encoder_hidden_states_proj(encoder_hidden_states)
        elif self.encoder_hidden_states_proj is not None and encoder_hidden_states is None: raise ValueError('`encoder_hidden_states_proj` requires `encoder_hidden_states` to be set')
        hidden_states = self.proj_in(hidden_states)
        positional_embeddings = self.positional_embedding.to(hidden_states.dtype)
        additional_embeds = []
        additional_embeddings_len = 0
        if encoder_hidden_states is not None:
            additional_embeds.append(encoder_hidden_states)
            additional_embeddings_len += encoder_hidden_states.shape[1]
        if len(proj_embeddings.shape) == 2: proj_embeddings = proj_embeddings[:, None, :]
        if len(hidden_states.shape) == 2: hidden_states = hidden_states[:, None, :]
        additional_embeds = additional_embeds + [proj_embeddings, time_embeddings[:, None, :], hidden_states]
        if self.prd_embedding is not None:
            prd_embedding = self.prd_embedding.to(hidden_states.dtype).expand(batch_size, -1, -1)
            additional_embeds.append(prd_embedding)
        hidden_states = torch.cat(additional_embeds, dim=1)
        additional_embeddings_len = additional_embeddings_len + proj_embeddings.shape[1] + 1
        if positional_embeddings.shape[1] < hidden_states.shape[1]: positional_embeddings = F.pad(positional_embeddings, (0, 0, additional_embeddings_len, self.prd_embedding.shape[1] if self.prd_embedding is not None else 0), value=0.0)
        hidden_states = hidden_states + positional_embeddings
        if attention_mask is not None:
            attention_mask = (1 - attention_mask.to(hidden_states.dtype)) * -10000.0
            attention_mask = F.pad(attention_mask, (0, self.additional_embeddings), value=0.0)
            attention_mask = (attention_mask[:, None, :] + self.causal_attention_mask).to(hidden_states.dtype)
            attention_mask = attention_mask.repeat_interleave(self.config.num_attention_heads, dim=0)
        if self.norm_in is not None: hidden_states = self.norm_in(hidden_states)
        for block in self.transformer_blocks: hidden_states = block(hidden_states, attention_mask=attention_mask)
        hidden_states = self.norm_out(hidden_states)
        if self.prd_embedding is not None: hidden_states = hidden_states[:, -1]
        else: hidden_states = hidden_states[:, additional_embeddings_len:]
        predicted_image_embedding = self.proj_to_clip_embeddings(hidden_states)
        if not return_dict: return (predicted_image_embedding,)
        return PriorTransformerOutput(predicted_image_embedding=predicted_image_embedding)
    def post_process_latents(self, prior_latents):
        prior_latents = prior_latents * self.clip_std + self.clip_mean
        return prior_latents
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
