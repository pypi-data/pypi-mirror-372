'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import Optional
import numpy as np
import torch
from torch import nn
from sapiens_transformers import GPT2Config, GPT2LMHeadModel
from sapiens_transformers.modeling_utils import ModuleUtilsMixin
from ...configuration_utils import ConfigMixin, register_to_config
from ...models import ModelMixin
class UniDiffuserTextDecoder(ModelMixin, ConfigMixin, ModuleUtilsMixin):
    _keys_to_ignore_on_load_unexpected = ['h\\.\\d+\\.attn\\.bias', 'h\\.\\d+\\.attn\\.masked_bias']
    @register_to_config
    def __init__(self, prefix_length: int, prefix_inner_dim: int, prefix_hidden_dim: Optional[int]=None, vocab_size: int=50257, n_positions: int=1024, n_embd: int=768, n_layer: int=12,
    n_head: int=12, n_inner: Optional[int]=None, activation_function: str='gelu_new', resid_pdrop: float=0.1, embd_pdrop: float=0.1, attn_pdrop: float=0.1, layer_norm_epsilon: float=1e-05,
    initializer_range: float=0.02, scale_attn_weights: bool=True, use_cache: bool=True, scale_attn_by_inverse_layer_idx: bool=False, reorder_and_upcast_attn: bool=False):
        super().__init__()
        self.prefix_length = prefix_length
        if prefix_inner_dim != n_embd and prefix_hidden_dim is None: raise ValueError(f'`prefix_hidden_dim` cannot be `None` when `prefix_inner_dim`: {prefix_hidden_dim} and `n_embd`: {n_embd} are not equal.')
        self.prefix_inner_dim = prefix_inner_dim
        self.prefix_hidden_dim = prefix_hidden_dim
        self.encode_prefix = nn.Linear(self.prefix_inner_dim, self.prefix_hidden_dim) if self.prefix_hidden_dim is not None else nn.Identity()
        self.decode_prefix = nn.Linear(self.prefix_hidden_dim, n_embd) if self.prefix_hidden_dim is not None else nn.Identity()
        gpt_config = GPT2Config(vocab_size=vocab_size, n_positions=n_positions, n_embd=n_embd, n_layer=n_layer, n_head=n_head, n_inner=n_inner, activation_function=activation_function,
        resid_pdrop=resid_pdrop, embd_pdrop=embd_pdrop, attn_pdrop=attn_pdrop, layer_norm_epsilon=layer_norm_epsilon, initializer_range=initializer_range, scale_attn_weights=scale_attn_weights,
        use_cache=use_cache, scale_attn_by_inverse_layer_idx=scale_attn_by_inverse_layer_idx, reorder_and_upcast_attn=reorder_and_upcast_attn)
        self.transformer = GPT2LMHeadModel(gpt_config)
    def forward(self, input_ids: torch.Tensor, prefix_embeds: torch.Tensor, attention_mask: Optional[torch.Tensor]=None, labels: Optional[torch.Tensor]=None):
        """Args:"""
        embedding_text = self.transformer.transformer.wte(input_ids)
        hidden = self.encode_prefix(prefix_embeds)
        prefix_embeds = self.decode_prefix(hidden)
        embedding_cat = torch.cat((prefix_embeds, embedding_text), dim=1)
        if labels is not None:
            dummy_token = self.get_dummy_token(input_ids.shape[0], input_ids.device)
            labels = torch.cat((dummy_token, input_ids), dim=1)
        out = self.transformer(inputs_embeds=embedding_cat, labels=labels, attention_mask=attention_mask)
        if self.prefix_hidden_dim is not None: return (out, hidden)
        else: return out
    def get_dummy_token(self, batch_size: int, device: torch.device) -> torch.Tensor: return torch.zeros(batch_size, self.prefix_length, dtype=torch.int64, device=device)
    def encode(self, prefix): return self.encode_prefix(prefix)
    @torch.no_grad()
    def generate_captions(self, features, eos_token_id, device):
        """Returns:"""
        features = torch.split(features, 1, dim=0)
        generated_tokens = []
        generated_seq_lengths = []
        for feature in features:
            feature = self.decode_prefix(feature.to(device))
            output_tokens, seq_lengths = self.generate_beam(input_embeds=feature, device=device, eos_token_id=eos_token_id)
            generated_tokens.append(output_tokens[0])
            generated_seq_lengths.append(seq_lengths[0])
        generated_tokens = torch.stack(generated_tokens)
        generated_seq_lengths = torch.stack(generated_seq_lengths)
        return (generated_tokens, generated_seq_lengths)
    @torch.no_grad()
    def generate_beam(self, input_ids=None, input_embeds=None, device=None, beam_size: int=5, entry_length: int=67, temperature: float=1.0, eos_token_id: Optional[int]=None):
        """Returns:"""
        stop_token_index = eos_token_id
        tokens = None
        scores = None
        seq_lengths = torch.ones(beam_size, device=device, dtype=torch.int)
        is_stopped = torch.zeros(beam_size, device=device, dtype=torch.bool)
        if input_embeds is not None: generated = input_embeds
        else: generated = self.transformer.transformer.wte(input_ids)
        for i in range(entry_length):
            outputs = self.transformer(inputs_embeds=generated)
            logits = outputs.logits
            logits = logits[:, -1, :] / (temperature if temperature > 0 else 1.0)
            logits = logits.softmax(-1).log()
            if scores is None:
                scores, next_tokens = logits.topk(beam_size, -1)
                generated = generated.expand(beam_size, *generated.shape[1:])
                next_tokens, scores = (next_tokens.permute(1, 0), scores.squeeze(0))
                if tokens is None: tokens = next_tokens
                else:
                    tokens = tokens.expand(beam_size, *tokens.shape[1:])
                    tokens = torch.cat((tokens, next_tokens), dim=1)
            else:
                logits[is_stopped] = -float(np.inf)
                logits[is_stopped, 0] = 0
                scores_sum = scores[:, None] + logits
                seq_lengths[~is_stopped] += 1
                scores_sum_average = scores_sum / seq_lengths[:, None]
                scores_sum_average, next_tokens = scores_sum_average.view(-1).topk(beam_size, -1)
                next_tokens_source = next_tokens // scores_sum.shape[1]
                seq_lengths = seq_lengths[next_tokens_source]
                next_tokens = next_tokens % scores_sum.shape[1]
                next_tokens = next_tokens.unsqueeze(1)
                tokens = tokens[next_tokens_source]
                tokens = torch.cat((tokens, next_tokens), dim=1)
                generated = generated[next_tokens_source]
                scores = scores_sum_average * seq_lengths
                is_stopped = is_stopped[next_tokens_source]
            next_token_embed = self.transformer.transformer.wte(next_tokens.squeeze()).view(generated.shape[0], 1, -1)
            generated = torch.cat((generated, next_token_embed), dim=1)
            is_stopped = is_stopped + next_tokens.eq(stop_token_index).squeeze()
            if is_stopped.all(): break
        scores = scores / seq_lengths
        order = scores.argsort(descending=True)
        output_texts = [tokens[i] for i in order]
        output_texts = torch.stack(output_texts, dim=0)
        seq_lengths = torch.tensor([seq_lengths[i] for i in order], dtype=seq_lengths.dtype)
        return (output_texts, seq_lengths)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
