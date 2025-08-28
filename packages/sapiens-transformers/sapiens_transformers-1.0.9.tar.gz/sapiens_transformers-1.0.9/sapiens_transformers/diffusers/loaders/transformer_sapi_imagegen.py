'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..models.modeling_utils import _LOW_CPU_MEM_USAGE_DEFAULT, load_model_dict_into_meta
from ..models.attention_processor import SAPIIPAdapterJointAttnProcessor2_0
from ..models.embeddings import IPAdapterTimeImageProjection
from typing import Dict
class SAPITransformer2DLoadersMixin:
    def _load_ip_adapter_weights(self, state_dict: Dict, low_cpu_mem_usage: bool=_LOW_CPU_MEM_USAGE_DEFAULT) -> None:
        """Args:"""
        hidden_size = self.config.attention_head_dim * self.config.num_attention_heads
        ip_hidden_states_dim = self.config.attention_head_dim * self.config.num_attention_heads
        timesteps_emb_dim = state_dict['ip_adapter']['0.norm_ip.linear.weight'].shape[1]
        layer_state_dict = {idx: {} for idx in range(len(self.attn_processors))}
        for key, weights in state_dict['ip_adapter'].items():
            idx, name = key.split('.', maxsplit=1)
            layer_state_dict[int(idx)][name] = weights
        attn_procs = {}
        for idx, name in enumerate(self.attn_processors.keys()):
            attn_procs[name] = SAPIIPAdapterJointAttnProcessor2_0(hidden_size=hidden_size, ip_hidden_states_dim=ip_hidden_states_dim, head_dim=self.config.attention_head_dim, timesteps_emb_dim=timesteps_emb_dim).to(self.device, dtype=self.dtype)
            if not low_cpu_mem_usage: attn_procs[name].load_state_dict(layer_state_dict[idx], strict=True)
            else: load_model_dict_into_meta(attn_procs[name], layer_state_dict[idx], device=self.device, dtype=self.dtype)
        self.set_attn_processor(attn_procs)
        embed_dim = state_dict['image_proj']['proj_in.weight'].shape[1]
        output_dim = state_dict['image_proj']['proj_out.weight'].shape[0]
        hidden_dim = state_dict['image_proj']['proj_in.weight'].shape[0]
        heads = state_dict['image_proj']['layers.0.attn.to_q.weight'].shape[0] // 64
        num_queries = state_dict['image_proj']['latents'].shape[1]
        timestep_in_dim = state_dict['image_proj']['time_embedding.linear_1.weight'].shape[1]
        self.image_proj = IPAdapterTimeImageProjection(embed_dim=embed_dim, output_dim=output_dim, hidden_dim=hidden_dim, heads=heads, num_queries=num_queries, timestep_in_dim=timestep_in_dim).to(device=self.device, dtype=self.dtype)
        if not low_cpu_mem_usage: self.image_proj.load_state_dict(state_dict['image_proj'], strict=True)
        else: load_model_dict_into_meta(self.image_proj, state_dict['image_proj'], device=self.device, dtype=self.dtype)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
