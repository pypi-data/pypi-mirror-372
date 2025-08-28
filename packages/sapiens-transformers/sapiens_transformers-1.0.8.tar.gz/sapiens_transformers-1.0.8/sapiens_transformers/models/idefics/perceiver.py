"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Tuple
import torch
import torch.nn as nn
from .configuration_idefics import IdeficsConfig
class IdeficsPerceiverResampler(nn.Module):
    def __init__(self, config: IdeficsConfig, embed_dim: int, depth: int, n_heads: int, head_dim: int, n_latents: int) -> None:
        super().__init__()
        self.embed_dim, self.n_heads, self.head_dim, self.n_latents = embed_dim, n_heads, head_dim, n_latents
        self.qk_layer_norms = config.perceiver_config.qk_layer_norms_perceiver
        self.latents = nn.Parameter(torch.randn(self.n_latents, self.embed_dim), requires_grad=True)
        self.intermediate_dim = (self.embed_dim * 4 if not hasattr(config.vision_config, "embed_dim") else config.vision_config.embed_dim * 4)
        self.blocks = nn.ModuleList([nn.ModuleList([IdeficsPerceiverAttention(self.embed_dim, self.n_heads, self.head_dim, self.qk_layer_norms), IdeficsMLP(self.intermediate_dim, config)]) for _ in range(depth)])
        self.layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, context: torch.Tensor) -> torch.Tensor:
        latents = self.latents.repeat(context.shape[0], 1, 1)
        for attn, ff in self.blocks:
            latents = attn(context, latents) + latents
            latents = ff(latents) + latents
        return self.layer_norm(latents)
class IdeficsPerceiverAttention(nn.Module):
    def __init__(self, embed_dim: int, n_heads: int, head_dim: int, qk_layer_norms: bool) -> None:
        super().__init__()
        self.embed_dim, self.n_heads, self.head_dim = embed_dim, n_heads, head_dim
        self.qk_layer_norms = qk_layer_norms
        self.context_layer_norm = nn.LayerNorm(self.embed_dim)
        self.latents_layer_norm = nn.LayerNorm(self.embed_dim)
        if self.qk_layer_norms:
            self.q_layer_norm = nn.LayerNorm(self.head_dim)
            self.k_layer_norm = nn.LayerNorm(self.head_dim)
        self.qk_scale = self.head_dim**-0.5
        self.q_proj = nn.Linear(self.embed_dim, self.n_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.embed_dim, self.n_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.embed_dim, self.n_heads * self.head_dim, bias=False)
        self.output_proj = nn.Linear(self.n_heads * self.head_dim, embed_dim, bias=False)
    def forward(self, context: torch.Tensor, latents: torch.Tensor) -> torch.Tensor:
        context = self.context_layer_norm(context)
        latents = self.latents_layer_norm(latents)
        batch_size, seq_length, embed_dim = context.shape[:3]
        q = self.q_proj(latents)
        k = self.k_proj(torch.cat([context, latents], dim=-2))
        v = self.v_proj(torch.cat([context, latents], dim=-2))
        q, k, v = [x.reshape(batch_size, x.shape[1], self.n_heads, self.head_dim).transpose(1, 2) for x in (q, k, v)]
        if self.qk_layer_norms:
            q = self.q_layer_norm(q)
            k = self.k_layer_norm(k)
        scores = torch.einsum("... i d, ... j d -> ... i j", q * self.qk_scale, k)
        stabilized_scores = scores - (scores.amax(dim=-1, keepdim=True).detach())
        attn = stabilized_scores.softmax(dim=-1)
        resampled = torch.einsum("... i j, ... j d -> ... i d", attn, v)
        return self.output_proj(resampled.transpose(1, 2).flatten(-2))
class IdeficsMLP(nn.Module):
    def __init__(self, intermediate_size, config: IdeficsConfig):
        super().__init__()
        self.embed_dim = config.vision_config.embed_dim
        self.ln = nn.LayerNorm(self.embed_dim)
        self.fc = nn.Linear(self.embed_dim, intermediate_size, bias=False)
        self.act = nn.ReLU()
        self.c_proj = nn.Linear(intermediate_size, self.embed_dim, bias=False)
    def forward(self, hidden_states: Optional[Tuple[torch.FloatTensor]]) -> torch.FloatTensor:
        hidden_states = self.ln(hidden_states)
        hidden_states = self.fc(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.c_proj(hidden_states)
        return hidden_states
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
