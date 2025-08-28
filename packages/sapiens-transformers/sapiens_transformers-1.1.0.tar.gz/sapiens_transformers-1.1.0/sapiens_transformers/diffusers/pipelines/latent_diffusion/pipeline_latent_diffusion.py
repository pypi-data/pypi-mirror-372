'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import inspect
from typing import List, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.utils.checkpoint
from sapiens_transformers import PretrainedConfig, PreTrainedModel, PreTrainedTokenizer
from sapiens_transformers.activations import ACT2FN
from sapiens_transformers.modeling_outputs import BaseModelOutput
from ...models import AutoencoderKL, UNet2DConditionModel, UNet2DModel, VQModel
from ...schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
from ...utils.torch_utils import randn_tensor
from ..pipeline_utils import DiffusionPipeline, ImagePipelineOutput
class LDMTextToImagePipeline(DiffusionPipeline):
    model_cpu_offload_seq = 'bert->unet->vqvae'
    def __init__(self, vqvae: Union[VQModel, AutoencoderKL], bert: PreTrainedModel, tokenizer: PreTrainedTokenizer, unet: Union[UNet2DModel, UNet2DConditionModel],
    scheduler: Union[DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler]):
        super().__init__()
        self.register_modules(vqvae=vqvae, bert=bert, tokenizer=tokenizer, unet=unet, scheduler=scheduler)
        self.vae_scale_factor = 2 ** (len(self.vqvae.config.block_out_channels) - 1)
    @torch.no_grad()
    def __call__(self, prompt: Union[str, List[str]], height: Optional[int]=None, width: Optional[int]=None, num_inference_steps: Optional[int]=50, guidance_scale: Optional[float]=1.0,
    eta: Optional[float]=0.0, generator: Optional[Union[torch.Generator, List[torch.Generator]]]=None, latents: Optional[torch.Tensor]=None, output_type: Optional[str]='pil',
    return_dict: bool=True, **kwargs) -> Union[Tuple, ImagePipelineOutput]:
        """Returns:"""
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width = width or self.unet.config.sample_size * self.vae_scale_factor
        if isinstance(prompt, str): batch_size = 1
        elif isinstance(prompt, list): batch_size = len(prompt)
        else: raise ValueError(f'`prompt` has to be of type `str` or `list` but is {type(prompt)}')
        if height % 8 != 0 or width % 8 != 0: raise ValueError(f'`height` and `width` have to be divisible by 8 but are {height} and {width}.')
        if guidance_scale != 1.0:
            uncond_input = self.tokenizer([''] * batch_size, padding='max_length', max_length=77, truncation=True, return_tensors='pt')
            negative_prompt_embeds = self.bert(uncond_input.input_ids.to(self._execution_device))[0]
        text_input = self.tokenizer(prompt, padding='max_length', max_length=77, truncation=True, return_tensors='pt')
        prompt_embeds = self.bert(text_input.input_ids.to(self._execution_device))[0]
        latents_shape = (batch_size, self.unet.config.in_channels, height // 8, width // 8)
        if isinstance(generator, list) and len(generator) != batch_size: raise ValueError(f'You have passed a list of generators of length {len(generator)}, but requested an effective batch size of {batch_size}. Make sure the batch size matches the length of the generators.')
        if latents is None: latents = randn_tensor(latents_shape, generator=generator, device=self._execution_device, dtype=prompt_embeds.dtype)
        elif latents.shape != latents_shape: raise ValueError(f'Unexpected latents shape, got {latents.shape}, expected {latents_shape}')
        latents = latents.to(self._execution_device)
        self.scheduler.set_timesteps(num_inference_steps)
        accepts_eta = 'eta' in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_kwargs = {}
        if accepts_eta: extra_kwargs['eta'] = eta
        for t in self.progress_bar(self.scheduler.timesteps):
            if guidance_scale == 1.0:
                latents_input = latents
                context = prompt_embeds
            else:
                latents_input = torch.cat([latents] * 2)
                context = torch.cat([negative_prompt_embeds, prompt_embeds])
            noise_pred = self.unet(latents_input, t, encoder_hidden_states=context).sample
            if guidance_scale != 1.0:
                noise_pred_uncond, noise_prediction_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_prediction_text - noise_pred_uncond)
            latents = self.scheduler.step(noise_pred, t, latents, **extra_kwargs).prev_sample
        latents = 1 / self.vqvae.config.scaling_factor * latents
        image = self.vqvae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).numpy()
        if output_type == 'pil': image = self.numpy_to_pil(image)
        if not return_dict: return (image,)
        return ImagePipelineOutput(images=image)
LDMBERT_PRETRAINED_MODEL_ARCHIVE_LIST = ['ldm-bert']
LDMBERT_PRETRAINED_CONFIG_ARCHIVE_MAP = {'ldm-bert': 'https://huggingface.co/valhalla/ldm-bert/blob/main/config.json'}
class LDMBertConfig(PretrainedConfig):
    model_type = 'ldmbert'
    keys_to_ignore_at_inference = ['past_key_values']
    attribute_map = {'num_attention_heads': 'encoder_attention_heads', 'hidden_size': 'd_model'}
    def __init__(self, vocab_size=30522, max_position_embeddings=77, encoder_layers=32, encoder_ffn_dim=5120, encoder_attention_heads=8, head_dim=64, encoder_layerdrop=0.0,
    activation_function='gelu', d_model=1280, dropout=0.1, attention_dropout=0.0, activation_dropout=0.0, init_std=0.02, classifier_dropout=0.0,
    scale_embedding=False, use_cache=True, pad_token_id=0, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.head_dim = head_dim
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.encoder_layerdrop = encoder_layerdrop
        self.classifier_dropout = classifier_dropout
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        super().__init__(pad_token_id=pad_token_id, **kwargs)
def _expand_mask(mask: torch.Tensor, dtype: torch.dtype, tgt_len: Optional[int]=None):
    bsz, src_len = mask.size()
    tgt_len = tgt_len if tgt_len is not None else src_len
    expanded_mask = mask[:, None, None, :].expand(bsz, 1, tgt_len, src_len).to(dtype)
    inverted_mask = 1.0 - expanded_mask
    return inverted_mask.masked_fill(inverted_mask.to(torch.bool), torch.finfo(dtype).min)
class LDMBertAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, head_dim: int, dropout: float=0.0, is_decoder: bool=False, bias: bool=False):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = head_dim
        self.inner_dim = head_dim * num_heads
        self.scaling = self.head_dim ** (-0.5)
        self.is_decoder = is_decoder
        self.k_proj = nn.Linear(embed_dim, self.inner_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, self.inner_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, self.inner_dim, bias=bias)
        self.out_proj = nn.Linear(self.inner_dim, embed_dim)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, key_value_states: Optional[torch.Tensor]=None, past_key_value: Optional[Tuple[torch.Tensor]]=None,
    attention_mask: Optional[torch.Tensor]=None, layer_head_mask: Optional[torch.Tensor]=None,
    output_attentions: bool=False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        bsz, tgt_len, _ = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scaling
        if is_cross_attention and past_key_value is not None:
            key_states = past_key_value[0]
            value_states = past_key_value[1]
        elif is_cross_attention:
            key_states = self._shape(self.k_proj(key_value_states), -1, bsz)
            value_states = self._shape(self.v_proj(key_value_states), -1, bsz)
        elif past_key_value is not None:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
            key_states = torch.cat([past_key_value[0], key_states], dim=2)
            value_states = torch.cat([past_key_value[1], value_states], dim=2)
        else:
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
        if self.is_decoder: past_key_value = (key_states, value_states)
        proj_shape = (bsz * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, tgt_len, bsz).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f'Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}')
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f'Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {attention_mask.size()}')
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if layer_head_mask is not None:
            if layer_head_mask.size() != (self.num_heads,): raise ValueError(f'Head mask for a single layer should be of size {(self.num_heads,)}, but is {layer_head_mask.size()}')
            attn_weights = layer_head_mask.view(1, -1, 1, 1) * attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights_reshaped.view(bsz * self.num_heads, tgt_len, src_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f'`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}')
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, self.inner_dim)
        attn_output = self.out_proj(attn_output)
        return (attn_output, attn_weights_reshaped, past_key_value)
class LDMBertEncoderLayer(nn.Module):
    def __init__(self, config: LDMBertConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = LDMBertAttention(embed_dim=self.embed_dim, num_heads=config.encoder_attention_heads, head_dim=config.head_dim, dropout=config.attention_dropout)
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(self.embed_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, layer_head_mask: torch.Tensor, output_attentions: Optional[bool]=False) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Args:"""
        residual = hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states, attn_weights, _ = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, layer_head_mask=layer_head_mask, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if hidden_states.dtype == torch.float16 and (torch.isinf(hidden_states).any() or torch.isnan(hidden_states).any()):
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class LDMBertPreTrainedModel(PreTrainedModel):
    config_class = LDMBertConfig
    base_model_prefix = 'model'
    _supports_gradient_checkpointing = True
    _keys_to_ignore_on_load_unexpected = ['encoder\\.version', 'decoder\\.version']
    def _init_weights(self, module):
        std = self.config.init_std
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, (LDMBertEncoder,)): module.gradient_checkpointing = value
    @property
    def dummy_inputs(self):
        pad_token = self.config.pad_token_id
        input_ids = torch.tensor([[0, 6, 10, 4, 2], [0, 8, 12, 2, pad_token]], device=self.device)
        dummy_inputs = {'attention_mask': input_ids.ne(pad_token), 'input_ids': input_ids}
        return dummy_inputs
class LDMBertEncoder(LDMBertPreTrainedModel):
    """Args:"""
    def __init__(self, config: LDMBertConfig):
        super().__init__(config)
        self.dropout = config.dropout
        embed_dim = config.d_model
        self.padding_idx = config.pad_token_id
        self.max_source_positions = config.max_position_embeddings
        self.embed_tokens = nn.Embedding(config.vocab_size, embed_dim)
        self.embed_positions = nn.Embedding(config.max_position_embeddings, embed_dim)
        self.layers = nn.ModuleList([LDMBertEncoderLayer(config) for _ in range(config.encoder_layers)])
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.gradient_checkpointing = False
        self.post_init()
    def get_input_embeddings(self): return self.embed_tokens
    def set_input_embeddings(self, value): self.embed_tokens = value
    def forward(self, input_ids: torch.LongTensor=None, attention_mask: Optional[torch.Tensor]=None, position_ids: Optional[torch.LongTensor]=None,
    head_mask: Optional[torch.Tensor]=None, inputs_embeds: Optional[torch.Tensor]=None, output_attentions: Optional[bool]=None,
    output_hidden_states: Optional[bool]=None, return_dict: Optional[bool]=None) -> Union[Tuple, BaseModelOutput]:
        """Args:"""
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError('You cannot specify both input_ids and inputs_embeds at the same time')
        elif input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
        elif inputs_embeds is not None: input_shape = inputs_embeds.size()[:-1]
        else: raise ValueError('You have to specify either input_ids or inputs_embeds')
        if inputs_embeds is None: inputs_embeds = self.embed_tokens(input_ids)
        seq_len = input_shape[1]
        if position_ids is None: position_ids = torch.arange(seq_len, dtype=torch.long, device=inputs_embeds.device).expand((1, -1))
        embed_pos = self.embed_positions(position_ids)
        hidden_states = inputs_embeds + embed_pos
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        if attention_mask is not None: attention_mask = _expand_mask(attention_mask, inputs_embeds.dtype)
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        if head_mask is not None:
            if head_mask.size()[0] != len(self.layers): raise ValueError(f'The head_mask should be specified for {len(self.layers)} layers, but it is for {head_mask.size()[0]}.')
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if torch.is_grad_enabled() and self.gradient_checkpointing:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs, output_attentions)
                    return custom_forward
                layer_outputs = torch.utils.checkpoint.checkpoint(create_custom_forward(encoder_layer), hidden_states, attention_mask, head_mask[idx] if head_mask is not None else None)
            else: layer_outputs = encoder_layer(hidden_states, attention_mask, layer_head_mask=head_mask[idx] if head_mask is not None else None, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        hidden_states = self.layer_norm(hidden_states)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple((v for v in [hidden_states, encoder_states, all_attentions] if v is not None))
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class LDMBertModel(LDMBertPreTrainedModel):
    _no_split_modules = []
    def __init__(self, config: LDMBertConfig):
        super().__init__(config)
        self.model = LDMBertEncoder(config)
        self.to_logits = nn.Linear(config.hidden_size, config.vocab_size)
    def forward(self, input_ids=None, attention_mask=None, position_ids=None, head_mask=None, inputs_embeds=None,
    output_attentions=None, output_hidden_states=None, return_dict=None):
        outputs = self.model(input_ids, attention_mask=attention_mask, position_ids=position_ids, head_mask=head_mask, inputs_embeds=inputs_embeds, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        return outputs
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
