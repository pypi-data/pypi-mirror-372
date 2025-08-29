"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import math
from dataclasses import dataclass
from typing import Any, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...modeling_attn_mask_utils import _create_4d_causal_attention_mask, _prepare_4d_attention_mask
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPooling
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_clipseg import CLIPSegConfig, CLIPSegTextConfig, CLIPSegVisionConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "CIDAS/clipseg-rd64-refined"
def contrastive_loss(logits: torch.Tensor) -> torch.Tensor: return nn.functional.cross_entropy(logits, torch.arange(len(logits), device=logits.device))
def clipseg_loss(similarity: torch.Tensor) -> torch.Tensor:
    caption_loss = contrastive_loss(similarity)
    image_loss = contrastive_loss(similarity.t())
    return (caption_loss + image_loss) / 2.0
@dataclass
class CLIPSegOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits_per_image: torch.FloatTensor = None
    logits_per_text: torch.FloatTensor = None
    text_embeds: torch.FloatTensor = None
    image_embeds: torch.FloatTensor = None
    text_model_output: BaseModelOutputWithPooling = None
    vision_model_output: BaseModelOutputWithPooling = None
    def to_tuple(self) -> Tuple[Any]: return tuple(self[k] if k not in ["text_model_output", "vision_model_output"] else getattr(self, k).to_tuple() for k in self.keys())
@dataclass
class CLIPSegDecoderOutput(ModelOutput):
    """Args:"""
    logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class CLIPSegImageSegmentationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    conditional_embeddings: torch.FloatTensor = None
    pooled_output: torch.FloatTensor = None
    vision_model_output: BaseModelOutputWithPooling = None
    decoder_output: CLIPSegDecoderOutput = None
    def to_tuple(self) -> Tuple[Any]: return tuple(self[k] if k not in ["vision_model_output", "decoder_output"] else getattr(self, k).to_tuple() for k in self.keys())
class CLIPSegVisionEmbeddings(nn.Module):
    def __init__(self, config: CLIPSegVisionConfig):
        super().__init__()
        self.config = config
        self.embed_dim = config.hidden_size
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.class_embedding = nn.Parameter(torch.randn(self.embed_dim))
        self.patch_embedding = nn.Conv2d(in_channels=config.num_channels, out_channels=self.embed_dim, kernel_size=self.patch_size, stride=self.patch_size, bias=False)
        self.num_patches = (self.image_size // self.patch_size) ** 2
        self.num_positions = self.num_patches + 1
        self.position_embedding = nn.Embedding(self.num_positions, self.embed_dim)
        self.register_buffer("position_ids", torch.arange(self.num_positions).expand((1, -1)), persistent=False)
    def interpolate_position_embeddings(self, new_size):
        if len(new_size) != 2: raise ValueError("new_size should consist of 2 values")
        num_patches_one_direction = int(self.num_patches**0.5)
        a = self.position_embedding.weight[1:].T.view(1, self.config.hidden_size, num_patches_one_direction, num_patches_one_direction)
        b = (nn.functional.interpolate(a, new_size, mode="bicubic", align_corners=False).squeeze(0).view(self.config.hidden_size, new_size[0] * new_size[1]).T)
        result = torch.cat([self.position_embedding.weight[:1], b])
        return result
    def forward(self, pixel_values: torch.FloatTensor) -> torch.Tensor:
        batch_size = pixel_values.shape[0]
        patch_embeds = self.patch_embedding(pixel_values)
        patch_embeds = patch_embeds.flatten(2).transpose(1, 2)
        class_embeds = self.class_embedding.expand(batch_size, 1, -1)
        embeddings = torch.cat([class_embeds, patch_embeds], dim=1)
        if embeddings.shape[1] != self.num_positions:
            new_shape = int(math.sqrt(embeddings.shape[1] - 1))
            embeddings = embeddings + self.interpolate_position_embeddings((new_shape, new_shape))
            embeddings = embeddings.to(embeddings.dtype)
        else: embeddings = embeddings + self.position_embedding(self.position_ids)
        return embeddings
class CLIPSegTextEmbeddings(nn.Module):
    def __init__(self, config: CLIPSegTextConfig):
        super().__init__()
        embed_dim = config.hidden_size
        self.token_embedding = nn.Embedding(config.vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(config.max_position_embeddings, embed_dim)
        self.register_buffer("position_ids", torch.arange(config.max_position_embeddings).expand((1, -1)), persistent=False)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None) -> torch.Tensor:
        seq_length = input_ids.shape[-1] if input_ids is not None else inputs_embeds.shape[-2]
        if position_ids is None: position_ids = self.position_ids[:, :seq_length]
        if inputs_embeds is None: inputs_embeds = self.token_embedding(input_ids)
        position_embeddings = self.position_embedding(position_ids)
        embeddings = inputs_embeds + position_embeddings
        return embeddings
class CLIPSegAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        if self.head_dim * self.num_heads != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.scale = self.head_dim**-0.5
        self.dropout = config.attention_dropout
        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim)
    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int): return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, causal_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        bsz, tgt_len, embed_dim = hidden_states.size()
        query_states = self.q_proj(hidden_states) * self.scale
        key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
        value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
        proj_shape = (bsz * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, tgt_len, bsz).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        src_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (bsz * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(bsz * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        if causal_attention_mask is not None:
            if causal_attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {causal_attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + causal_attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, tgt_len, src_len): raise ValueError(f"Attention mask should be of size {(bsz, 1, tgt_len, src_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len) + attention_mask
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights_reshaped.view(bsz * self.num_heads, tgt_len, src_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (bsz * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(bsz, self.num_heads, tgt_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(bsz, self.num_heads, tgt_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, tgt_len, embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped
class CLIPSegMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.activation_fn = ACT2FN[config.hidden_act]
        self.fc1 = nn.Linear(config.hidden_size, config.intermediate_size)
        self.fc2 = nn.Linear(config.intermediate_size, config.hidden_size)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        return hidden_states
class CLIPSegEncoderLayer(nn.Module):
    def __init__(self, config: CLIPSegConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.self_attn = CLIPSegAttention(config)
        self.layer_norm1 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
        self.mlp = CLIPSegMLP(config)
        self.layer_norm2 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, causal_attention_mask: torch.Tensor, output_attentions: Optional[bool] = False) -> Tuple[torch.FloatTensor]:
        residual = hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, causal_attention_mask=causal_attention_mask, output_attentions=output_attentions)
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class CLIPSegPreTrainedModel(PreTrainedModel):
    config_class = CLIPSegConfig
    base_model_prefix = "clip"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        factor = self.config.initializer_factor
        if isinstance(module, CLIPSegTextEmbeddings):
            module.token_embedding.weight.data.normal_(mean=0.0, std=factor * 0.02)
            module.position_embedding.weight.data.normal_(mean=0.0, std=factor * 0.02)
        elif isinstance(module, CLIPSegVisionEmbeddings):
            factor = self.config.initializer_factor
            nn.init.normal_(module.class_embedding, mean=0.0, std=module.embed_dim**-0.5 * factor)
            nn.init.normal_(module.patch_embedding.weight, std=module.config.initializer_range * factor)
            nn.init.normal_(module.position_embedding.weight, std=module.config.initializer_range * factor)
        elif isinstance(module, CLIPSegAttention):
            factor = self.config.initializer_factor
            in_proj_std = (module.embed_dim**-0.5) * ((2 * module.config.num_hidden_layers) ** -0.5) * factor
            out_proj_std = (module.embed_dim**-0.5) * factor
            nn.init.normal_(module.q_proj.weight, std=in_proj_std)
            nn.init.normal_(module.k_proj.weight, std=in_proj_std)
            nn.init.normal_(module.v_proj.weight, std=in_proj_std)
            nn.init.normal_(module.out_proj.weight, std=out_proj_std)
        elif isinstance(module, CLIPSegMLP):
            factor = self.config.initializer_factor
            in_proj_std = (module.config.hidden_size**-0.5) * ((2 * module.config.num_hidden_layers) ** -0.5) * factor
            fc_std = (2 * module.config.hidden_size) ** -0.5 * factor
            nn.init.normal_(module.fc1.weight, std=fc_std)
            nn.init.normal_(module.fc2.weight, std=in_proj_std)
        elif isinstance(module, CLIPSegModel):
            nn.init.normal_(module.text_projection.weight, std=module.text_embed_dim**-0.5 * self.config.initializer_factor)
            nn.init.normal_(module.visual_projection.weight, std=module.vision_embed_dim**-0.5 * self.config.initializer_factor)
        if isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        if isinstance(module, nn.Linear) and module.bias is not None: module.bias.data.zero_()
CLIPSEG_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`CLIPSegConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
CLIPSEG_TEXT_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
CLIPSEG_VISION_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`CLIPImageProcessor.__call__`] for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
CLIPSEG_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`CLIPImageProcessor.__call__`] for details.
        return_loss (`bool`, *optional*):
            Whether or not to return the contrastive loss.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
class CLIPSegEncoder(nn.Module):
    def __init__(self, config: CLIPSegConfig):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([CLIPSegEncoderLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, inputs_embeds, attention_mask: Optional[torch.Tensor] = None, causal_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        hidden_states = inputs_embeds
        for idx, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(encoder_layer.__call__, hidden_states, attention_mask, causal_attention_mask, output_attentions)
            else: layer_outputs = encoder_layer(hidden_states, attention_mask, causal_attention_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class CLIPSegTextTransformer(nn.Module):
    def __init__(self, config: CLIPSegTextConfig):
        super().__init__()
        self.config = config
        embed_dim = config.hidden_size
        self.embeddings = CLIPSegTextEmbeddings(config)
        self.encoder = CLIPSegEncoder(config)
        self.final_layer_norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.eos_token_id = config.eos_token_id
    @add_start_docstrings_to_model_forward(CLIPSEG_TEXT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is None: raise ValueError("You have to specify input_ids")
        input_shape = input_ids.size()
        input_ids = input_ids.view(-1, input_shape[-1])
        hidden_states = self.embeddings(input_ids=input_ids, position_ids=position_ids)
        causal_attention_mask = _create_4d_causal_attention_mask(input_shape, hidden_states.dtype, device=hidden_states.device)
        if attention_mask is not None: attention_mask = _prepare_4d_attention_mask(attention_mask, hidden_states.dtype)
        encoder_outputs = self.encoder(inputs_embeds=hidden_states, attention_mask=attention_mask, causal_attention_mask=causal_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        last_hidden_state = self.final_layer_norm(last_hidden_state)
        if self.eos_token_id == 2: pooled_output = last_hidden_state[torch.arange(last_hidden_state.shape[0], device=last_hidden_state.device), input_ids.to(dtype=torch.int, device=last_hidden_state.device).argmax(dim=-1)]
        else: pooled_output = last_hidden_state[torch.arange(last_hidden_state.shape[0], device=last_hidden_state.device), (input_ids.to(dtype=torch.int, device=last_hidden_state.device) == self.eos_token_id) .int().argmax(dim=-1)]
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
class CLIPSegTextModel(CLIPSegPreTrainedModel):
    config_class = CLIPSegTextConfig
    _no_split_modules = ["CLIPSegTextEmbeddings", "CLIPSegEncoderLayer"]
    def __init__(self, config: CLIPSegTextConfig):
        super().__init__(config)
        self.text_model = CLIPSegTextTransformer(config)
        self.post_init()
    def get_input_embeddings(self) -> nn.Module: return self.text_model.embeddings.token_embedding
    def set_input_embeddings(self, value): self.text_model.embeddings.token_embedding = value
    @add_start_docstrings_to_model_forward(CLIPSEG_TEXT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]: return self.text_model(input_ids=input_ids, attention_mask=attention_mask,
    position_ids=position_ids, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
class CLIPSegVisionTransformer(nn.Module):
    def __init__(self, config: CLIPSegVisionConfig):
        super().__init__()
        self.config = config
        embed_dim = config.hidden_size
        self.embeddings = CLIPSegVisionEmbeddings(config)
        self.pre_layrnorm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        self.encoder = CLIPSegEncoder(config)
        self.post_layernorm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
    @add_start_docstrings_to_model_forward(CLIPSEG_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        hidden_states = self.embeddings(pixel_values)
        hidden_states = self.pre_layrnorm(hidden_states)
        encoder_outputs = self.encoder(inputs_embeds=hidden_states, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        pooled_output = last_hidden_state[:, 0, :]
        pooled_output = self.post_layernorm(pooled_output)
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
class CLIPSegVisionModel(CLIPSegPreTrainedModel):
    config_class = CLIPSegVisionConfig
    main_input_name = "pixel_values"
    def __init__(self, config: CLIPSegVisionConfig):
        super().__init__(config)
        self.vision_model = CLIPSegVisionTransformer(config)
        self.post_init()
    def get_input_embeddings(self) -> nn.Module: return self.vision_model.embeddings.patch_embedding
    @add_start_docstrings_to_model_forward(CLIPSEG_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPooling]: return self.vision_model(pixel_values=pixel_values,
    output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
@add_start_docstrings(CLIPSEG_START_DOCSTRING)
class CLIPSegModel(CLIPSegPreTrainedModel):
    config_class = CLIPSegConfig
    def __init__(self, config: CLIPSegConfig):
        super().__init__(config)
        if not isinstance(config.text_config, CLIPSegTextConfig): raise TypeError(f"config.text_config is expected to be of type CLIPSegTextConfig but is of type {type(config.text_config)}.")
        if not isinstance(config.vision_config, CLIPSegVisionConfig): raise TypeError(f"config.vision_config is expected to be of type CLIPSegVisionConfig but is of type {type(config.vision_config)}.")
        text_config = config.text_config
        vision_config = config.vision_config
        self.projection_dim = config.projection_dim
        self.text_embed_dim = text_config.hidden_size
        self.vision_embed_dim = vision_config.hidden_size
        self.text_model = CLIPSegTextTransformer(text_config)
        self.vision_model = CLIPSegVisionTransformer(vision_config)
        self.visual_projection = nn.Linear(self.vision_embed_dim, self.projection_dim, bias=False)
        self.text_projection = nn.Linear(self.text_embed_dim, self.projection_dim, bias=False)
        self.logit_scale = nn.Parameter(torch.tensor(self.config.logit_scale_init_value))
        self.post_init()
    @add_start_docstrings_to_model_forward(CLIPSEG_TEXT_INPUTS_DOCSTRING)
    def get_text_features(self, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> torch.FloatTensor:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        text_outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = text_outputs[1]
        text_features = self.text_projection(pooled_output)
        return text_features
    @add_start_docstrings_to_model_forward(CLIPSEG_VISION_INPUTS_DOCSTRING)
    def get_image_features(self, pixel_values: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> torch.FloatTensor:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = vision_outputs[1]
        image_features = self.visual_projection(pooled_output)
        return image_features
    @add_start_docstrings_to_model_forward(CLIPSEG_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None,
    return_loss: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, CLIPSegOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        text_outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        image_embeds = vision_outputs[1]
        image_embeds = self.visual_projection(image_embeds)
        text_embeds = text_outputs[1]
        text_embeds = self.text_projection(text_embeds)
        image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
        text_embeds = text_embeds / text_embeds.norm(p=2, dim=-1, keepdim=True)
        logit_scale = self.logit_scale.exp()
        logits_per_text = torch.matmul(text_embeds, image_embeds.t()) * logit_scale
        logits_per_image = logits_per_text.t()
        loss = None
        if return_loss: loss = clipseg_loss(logits_per_text)
        if not return_dict:
            output = (logits_per_image, logits_per_text, text_embeds, image_embeds, text_outputs, vision_outputs)
            return ((loss,) + output) if loss is not None else output
        return CLIPSegOutput(loss=loss, logits_per_image=logits_per_image, logits_per_text=logits_per_text, text_embeds=text_embeds, image_embeds=image_embeds, text_model_output=text_outputs, vision_model_output=vision_outputs)
class CLIPSegDecoderLayer(nn.Module):
    def __init__(self, config: CLIPSegConfig):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.self_attn = CLIPSegAttention(config)
        self.layer_norm1 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
        self.mlp = CLIPSegMLP(config)
        self.layer_norm2 = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, causal_attention_mask: torch.Tensor, output_attentions: Optional[bool] = False) -> Tuple[torch.FloatTensor]:
        residual = hidden_states
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, causal_attention_mask=causal_attention_mask, output_attentions=output_attentions)
        hidden_states = residual + hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        residual = hidden_states
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class CLIPSegDecoder(CLIPSegPreTrainedModel):
    def __init__(self, config: CLIPSegConfig):
        super().__init__(config)
        self.conditional_layer = config.conditional_layer
        self.film_mul = nn.Linear(config.projection_dim, config.reduce_dim)
        self.film_add = nn.Linear(config.projection_dim, config.reduce_dim)
        if config.use_complex_transposed_convolution:
            transposed_kernels = (config.vision_config.patch_size // 4, config.vision_config.patch_size // 4)
            self.transposed_convolution = nn.Sequential(nn.Conv2d(config.reduce_dim, config.reduce_dim, kernel_size=3, padding=1), nn.ReLU(), nn.ConvTranspose2d(config.reduce_dim, config.reduce_dim // 2, kernel_size=transposed_kernels[0], stride=transposed_kernels[0]),
            nn.ReLU(), nn.ConvTranspose2d(config.reduce_dim // 2, 1, kernel_size=transposed_kernels[1], stride=transposed_kernels[1]))
        else: self.transposed_convolution = nn.ConvTranspose2d(config.reduce_dim, 1, config.vision_config.patch_size, stride=config.vision_config.patch_size)
        depth = len(config.extract_layers)
        self.reduces = nn.ModuleList([nn.Linear(config.vision_config.hidden_size, config.reduce_dim) for _ in range(depth)])
        decoder_config = copy.deepcopy(config.vision_config)
        decoder_config.hidden_size = config.reduce_dim
        decoder_config.num_attention_heads = config.decoder_num_attention_heads
        decoder_config.intermediate_size = config.decoder_intermediate_size
        decoder_config.hidden_act = "relu"
        self.layers = nn.ModuleList([CLIPSegDecoderLayer(decoder_config) for _ in range(len(config.extract_layers))])
    def forward(self, hidden_states: Tuple[torch.Tensor], conditional_embeddings: torch.Tensor, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = True):
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        activations = hidden_states[::-1]
        output = None
        for i, (activation, layer, reduce) in enumerate(zip(activations, self.layers, self.reduces)):
            if output is not None: output = reduce(activation) + output
            else: output = reduce(activation)
            if i == self.conditional_layer:
                output = self.film_mul(conditional_embeddings) * output.permute(1, 0, 2) + self.film_add(conditional_embeddings)
                output = output.permute(1, 0, 2)
            layer_outputs = layer(output, attention_mask=None, causal_attention_mask=None, output_attentions=output_attentions)
            output = layer_outputs[0]
            if output_hidden_states: all_hidden_states += (output,)
            if output_attentions: all_attentions += (layer_outputs[1],)
        output = output[:, 1:, :].permute(0, 2, 1)
        size = int(math.sqrt(output.shape[2]))
        batch_size = conditional_embeddings.shape[0]
        output = output.view(batch_size, output.shape[1], size, size)
        logits = self.transposed_convolution(output).squeeze(1)
        if not return_dict: return tuple(v for v in [logits, all_hidden_states, all_attentions] if v is not None)
        return CLIPSegDecoderOutput(logits=logits, hidden_states=all_hidden_states, attentions=all_attentions)
@add_start_docstrings("CLIPSeg model with a Transformer-based decoder on top for zero-shot and one-shot image segmentation.", CLIPSEG_START_DOCSTRING)
class CLIPSegForImageSegmentation(CLIPSegPreTrainedModel):
    config_class = CLIPSegConfig
    def __init__(self, config: CLIPSegConfig):
        super().__init__(config)
        self.config = config
        self.clip = CLIPSegModel(config)
        self.extract_layers = config.extract_layers
        self.decoder = CLIPSegDecoder(config)
        self.post_init()
    def get_conditional_embeddings(self, batch_size: int = None, input_ids: Optional[torch.Tensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None,
    conditional_pixel_values: Optional[torch.Tensor] = None):
        if input_ids is not None:
            if len(input_ids) != batch_size: raise ValueError("Make sure to pass as many prompt texts as there are query images")
            with torch.no_grad(): conditional_embeddings = self.clip.get_text_features(input_ids, attention_mask=attention_mask, position_ids=position_ids)
        elif conditional_pixel_values is not None:
            if len(conditional_pixel_values) != batch_size: raise ValueError("Make sure to pass as many prompt images as there are query images")
            with torch.no_grad(): conditional_embeddings = self.clip.get_image_features(conditional_pixel_values)
        else: raise ValueError("Invalid conditional, should be either provided as `input_ids` or `conditional_pixel_values`")
        return conditional_embeddings
    @add_start_docstrings_to_model_forward(CLIPSEG_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.FloatTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, conditional_pixel_values: Optional[torch.FloatTensor] = None,
    conditional_embeddings: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, labels: Optional[torch.LongTensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, CLIPSegOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        with torch.no_grad():
            vision_outputs = self.clip.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=True, return_dict=return_dict)
            pooled_output = self.clip.visual_projection(vision_outputs[1])
            hidden_states = vision_outputs.hidden_states if return_dict else vision_outputs[2]
            activations = [hidden_states[i + 1] for i in self.extract_layers]
            if return_dict: vision_outputs = BaseModelOutputWithPooling(last_hidden_state=vision_outputs.last_hidden_state, pooler_output=vision_outputs.pooler_output, hidden_states=vision_outputs.hidden_states if output_hidden_states else None, attentions=vision_outputs.attentions)
            else: vision_outputs = (vision_outputs[:2] + vision_outputs[3:] if not output_hidden_states else vision_outputs)
        if conditional_embeddings is None: conditional_embeddings = self.get_conditional_embeddings(batch_size=pixel_values.shape[0], input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids, conditional_pixel_values=conditional_pixel_values)
        else:
            if conditional_embeddings.shape[0] != pixel_values.shape[0]: raise ValueError("Make sure to pass as many conditional embeddings as there are query images in the batch")
            if conditional_embeddings.shape[1] != self.config.projection_dim: raise ValueError("Make sure that the feature dimension of the conditional embeddings matches `config.projection_dim`.")
        decoder_outputs = self.decoder(activations, conditional_embeddings, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        logits = decoder_outputs.logits if return_dict else decoder_outputs[0]
        loss = None
        if labels is not None:
            labels = labels.to(logits.device)
            loss_fn = nn.BCEWithLogitsLoss()
            loss = loss_fn(logits, labels)
        if not return_dict:
            output = (logits, conditional_embeddings, pooled_output, vision_outputs, decoder_outputs)
            return ((loss,) + output) if loss is not None else output
        return CLIPSegImageSegmentationOutput(loss=loss, logits=logits, conditional_embeddings=conditional_embeddings, pooled_output=pooled_output, vision_model_output=vision_outputs, decoder_output=decoder_outputs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
