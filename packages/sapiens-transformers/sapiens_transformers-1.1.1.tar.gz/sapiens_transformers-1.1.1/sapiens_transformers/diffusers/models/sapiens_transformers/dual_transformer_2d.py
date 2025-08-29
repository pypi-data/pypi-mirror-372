'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ..modeling_outputs import Transformer2DModelOutput
from .transformer_2d import Transformer2DModel
from typing import Optional
from torch import nn
class DualTransformer2DModel(nn.Module):
    def __init__(self, num_attention_heads: int=16, attention_head_dim: int=88, in_channels: Optional[int]=None, num_layers: int=1, dropout: float=0.0, norm_num_groups: int=32, cross_attention_dim: Optional[int]=None, attention_bias: bool=False, sample_size: Optional[int]=None, num_vector_embeds: Optional[int]=None, activation_fn: str='geglu', num_embeds_ada_norm: Optional[int]=None):
        super().__init__()
        self.sapiens_transformers = nn.ModuleList([Transformer2DModel(num_attention_heads=num_attention_heads, attention_head_dim=attention_head_dim, in_channels=in_channels, num_layers=num_layers, dropout=dropout, norm_num_groups=norm_num_groups, cross_attention_dim=cross_attention_dim, attention_bias=attention_bias, sample_size=sample_size, num_vector_embeds=num_vector_embeds, activation_fn=activation_fn, num_embeds_ada_norm=num_embeds_ada_norm) for _ in range(2)])
        self.mix_ratio = 0.5
        self.condition_lengths = [77, 257]
        self.transformer_index_for_condition = [1, 0]
    def forward(self, hidden_states, encoder_hidden_states, timestep=None, attention_mask=None, cross_attention_kwargs=None, return_dict: bool=True):
        """Returns:"""
        input_states = hidden_states
        encoded_states = []
        tokens_start = 0
        for i in range(2):
            condition_state = encoder_hidden_states[:, tokens_start:tokens_start + self.condition_lengths[i]]
            transformer_index = self.transformer_index_for_condition[i]
            encoded_state = self.sapiens_transformers[transformer_index](input_states, encoder_hidden_states=condition_state, timestep=timestep, cross_attention_kwargs=cross_attention_kwargs, return_dict=False)[0]
            encoded_states.append(encoded_state - input_states)
            tokens_start += self.condition_lengths[i]
        output_states = encoded_states[0] * self.mix_ratio + encoded_states[1] * (1 - self.mix_ratio)
        output_states = output_states + input_states
        if not return_dict: return (output_states,)
        return Transformer2DModelOutput(sample=output_states)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
