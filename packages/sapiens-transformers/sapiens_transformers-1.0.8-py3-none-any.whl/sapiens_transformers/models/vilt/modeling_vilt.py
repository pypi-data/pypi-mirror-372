"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections.abc
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...modeling_outputs import (BaseModelOutput, BaseModelOutputWithPooling, MaskedLMOutput, ModelOutput, SequenceClassifierOutput, TokenClassifierOutput)
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import (find_pruneable_heads_and_indices, meshgrid, prune_linear_layer)
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_vilt import ViltConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "ViltConfig"
_CHECKPOINT_FOR_DOC = "dandelin/vilt-b32-mlm"
@dataclass
class ViltForImagesAndTextClassificationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    hidden_states: Optional[List[Tuple[torch.FloatTensor]]] = None
    attentions: Optional[List[Tuple[torch.FloatTensor]]] = None
class ViltEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.text_embeddings = TextEmbeddings(config)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.patch_embeddings = ViltPatchEmbeddings(config)
        num_patches = self.patch_embeddings.num_patches
        self.position_embeddings = nn.Parameter(torch.zeros(1, num_patches + 1, config.hidden_size))
        self.token_type_embeddings = nn.Embedding(config.modality_type_vocab_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.config = config
    def visual_embed(self, pixel_values, pixel_mask, max_image_length=200):
        _, _, ph, pw = self.patch_embeddings.projection.weight.shape
        x = self.patch_embeddings(pixel_values)
        x_mask = pixel_mask[:, None, :, :].float()
        x_mask = nn.functional.interpolate(x_mask, size=(x.shape[2], x.shape[3])).long()
        x_h = x_mask[:, 0].sum(dim=1)[:, 0]
        x_w = x_mask[:, 0].sum(dim=2)[:, 0]
        batch_size, num_channels, height, width = x.shape
        patch_dim = self.config.image_size // self.config.patch_size
        spatial_pos = self.position_embeddings[:, 1:, :].transpose(1, 2).view(1, num_channels, patch_dim, patch_dim)
        pos_embed = torch.cat([nn.functional.pad(nn.functional.interpolate(spatial_pos, size=(h, w), mode="bilinear", align_corners=True), (0, width - w, 0, height - h)) for h, w in zip(x_h, x_w)], dim=0)
        pos_embed = pos_embed.flatten(2).transpose(1, 2)
        x = x.flatten(2).transpose(1, 2)
        patch_index = torch.stack(meshgrid(torch.arange(x_mask.shape[-2]), torch.arange(x_mask.shape[-1]), indexing="ij"), dim=-1).to(device=x_mask.device)
        patch_index = patch_index[None, None, :, :, :]
        patch_index = patch_index.expand(x_mask.shape[0], x_mask.shape[1], -1, -1, -1)
        patch_index = patch_index.flatten(1, 3)
        x_mask = x_mask.flatten(1)
        if max_image_length < 0 or max_image_length is None or not isinstance(max_image_length, int):
            effective_resolution = x_h * x_w
            max_image_length = effective_resolution.max()
        else:
            effective_resolution = x_h * x_w
            max_image_length = min(effective_resolution.max(), max_image_length)
        valid_idx = x_mask.nonzero(as_tuple=False)
        non_valid_idx = (1 - x_mask).nonzero(as_tuple=False)
        unique_rows = valid_idx[:, 0].unique()
        valid_row_idx = [valid_idx[valid_idx[:, 0] == u] for u in unique_rows]
        non_valid_row_idx = [non_valid_idx[non_valid_idx[:, 0] == u] for u in unique_rows]
        valid_nums = [v.size(0) for v in valid_row_idx]
        non_valid_nums = [v.size(0) for v in non_valid_row_idx]
        pad_nums = [max_image_length - v for v in valid_nums]
        select = []
        for i, (v, nv, p) in enumerate(zip(valid_nums, non_valid_nums, pad_nums)):
            if p <= 0:
                valid_choice = torch.multinomial(torch.ones(v).float(), max_image_length)
                select.append(valid_row_idx[i][valid_choice])
            else:
                pad_choice = torch.multinomial(torch.ones(nv).float(), p, replacement=True)
                select.append(torch.cat([valid_row_idx[i], non_valid_row_idx[i][pad_choice]], dim=0))
        select = torch.cat(select, dim=0)
        x = x[select[:, 0], select[:, 1]].view(batch_size, -1, num_channels)
        x_mask = x_mask[select[:, 0], select[:, 1]].view(batch_size, -1)
        patch_index = patch_index[select[:, 0], select[:, 1]].view(batch_size, -1, 2)
        pos_embed = pos_embed[select[:, 0], select[:, 1]].view(batch_size, -1, num_channels)
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        pos_embed = torch.cat((self.position_embeddings[:, 0, :][:, None, :].expand(batch_size, -1, -1), pos_embed), dim=1)
        x = x + pos_embed
        x = self.dropout(x)
        x_mask = torch.cat([torch.ones(x_mask.shape[0], 1).to(x_mask), x_mask], dim=1)
        return x, x_mask, (patch_index, (height, width))
    def forward(self, input_ids, attention_mask, token_type_ids, pixel_values, pixel_mask, inputs_embeds, image_embeds, image_token_type_idx=1):
        text_embeds = self.text_embeddings(input_ids=input_ids, token_type_ids=token_type_ids, inputs_embeds=inputs_embeds)
        if image_embeds is None: image_embeds, image_masks, patch_index = self.visual_embed(pixel_values, pixel_mask, max_image_length=self.config.max_image_length)
        else: image_masks = pixel_mask.flatten(1)
        if image_token_type_idx is None: image_token_type_idx = 1
        text_embeds = text_embeds + self.token_type_embeddings(torch.zeros_like(attention_mask, dtype=torch.long, device=text_embeds.device))
        image_embeds = image_embeds + self.token_type_embeddings(torch.full_like(image_masks, image_token_type_idx, dtype=torch.long, device=text_embeds.device))
        embeddings = torch.cat([text_embeds, image_embeds], dim=1)
        masks = torch.cat([attention_mask, image_masks], dim=1)
        return embeddings, masks
class TextEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.position_embedding_type = getattr(config, "position_embedding_type", "absolute")
        self.register_buffer("position_ids", torch.arange(config.max_position_embeddings).expand((1, -1)), persistent=False)
        self.register_buffer("token_type_ids", torch.zeros(self.position_ids.size(), dtype=torch.long), persistent=False)
    def forward(self, input_ids=None, token_type_ids=None, position_ids=None, inputs_embeds=None):
        if input_ids is not None: input_shape = input_ids.size()
        else: input_shape = inputs_embeds.size()[:-1]
        seq_length = input_shape[1]
        if position_ids is None: position_ids = self.position_ids[:, :seq_length]
        if token_type_ids is None:
            if hasattr(self, "token_type_ids"):
                buffered_token_type_ids = self.token_type_ids[:, :seq_length]
                buffered_token_type_ids_expanded = buffered_token_type_ids.expand(input_shape[0], seq_length)
                token_type_ids = buffered_token_type_ids_expanded
            else: token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=self.position_ids.device)
        if inputs_embeds is None: inputs_embeds = self.word_embeddings(input_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        embeddings = inputs_embeds + token_type_embeddings
        if self.position_embedding_type == "absolute":
            position_embeddings = self.position_embeddings(position_ids)
            embeddings += position_embeddings
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
class ViltPatchEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.projection = nn.Conv2d(num_channels, hidden_size, kernel_size=patch_size, stride=patch_size)
    def forward(self, pixel_values):
        batch_size, num_channels, height, width = pixel_values.shape
        if num_channels != self.num_channels: raise ValueError("Make sure that the channel dimension of the pixel values match with the one set in the configuration.")
        target_dtype = self.projection.weight.dtype
        x = self.projection(pixel_values.to(dtype=target_dtype))
        return x
class ViltSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size {config.hidden_size,} is not a multiple of the number of attention heads {config.num_attention_heads}.")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
        self.key = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
        self.value = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)
    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions=False):
        mixed_query_layer = self.query(hidden_states)
        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = nn.Softmax(dim=-1)(attention_scores)
        attention_probs = self.dropout(attention_probs)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        return outputs
class ViltSelfOutput(nn.Module):
    def __init__(self, config: ViltConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class ViltAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.attention = ViltSelfAttention(config)
        self.output = ViltSelfOutput(config)
        self.pruned_heads = set()
    def prune_heads(self, heads):
        if len(heads) == 0: return
        heads, index = find_pruneable_heads_and_indices(heads, self.attention.num_attention_heads, self.attention.attention_head_size, self.pruned_heads)
        self.attention.query = prune_linear_layer(self.attention.query, index)
        self.attention.key = prune_linear_layer(self.attention.key, index)
        self.attention.value = prune_linear_layer(self.attention.value, index)
        self.output.dense = prune_linear_layer(self.output.dense, index, dim=1)
        self.attention.num_attention_heads = self.attention.num_attention_heads - len(heads)
        self.attention.all_head_size = self.attention.attention_head_size * self.attention.num_attention_heads
        self.pruned_heads = self.pruned_heads.union(heads)
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions=False):
        self_outputs = self.attention(hidden_states, attention_mask, head_mask, output_attentions)
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
class ViltIntermediate(nn.Module):
    def __init__(self, config: ViltConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class ViltOutput(nn.Module):
    def __init__(self, config: ViltConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = hidden_states + input_tensor
        return hidden_states
class ViltLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.attention = ViltAttention(config)
        self.intermediate = ViltIntermediate(config)
        self.output = ViltOutput(config)
        self.layernorm_before = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.layernorm_after = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions=False):
        self_attention_outputs = self.attention(self.layernorm_before(hidden_states), attention_mask, head_mask, output_attentions=output_attentions)
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        hidden_states = attention_output + hidden_states.to(attention_output.device)
        layer_output = self.layernorm_after(hidden_states)
        layer_output = self.intermediate(layer_output)
        layer_output = self.output(layer_output, hidden_states)
        outputs = (layer_output,) + outputs
        return outputs
class ViltEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([ViltLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions=False, output_hidden_states=False, return_dict=True):
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_head_mask = head_mask[i] if head_mask is not None else None
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states,
            attention_mask, layer_head_mask, output_attentions)
            else: layer_outputs = layer_module(hidden_states, attention_mask, layer_head_mask, output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions)
class ViltPreTrainedModel(PreTrainedModel):
    config_class = ViltConfig
    base_model_prefix = "vilt"
    supports_gradient_checkpointing = True
    _no_split_modules = ["ViltEmbeddings", "ViltSelfAttention"]
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
VILT_START_DOCSTRING = r"""
    This model is a PyTorch `torch.nn.Module <https://pytorch.org/docs/stable/nn.html#torch.nn.Module>`_ subclass. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`ViltConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
VILT_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary. Indices can be obtained using [`AutoTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details. [What are input
            IDs?](../glossary#input-ids)
        attention_mask (`torch.FloatTensor` of shape `(0)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`torch.LongTensor` of shape `(0)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`ViltImageProcessor.__call__`] for details.
        pixel_mask (`torch.LongTensor` of shape `(batch_size, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            `What are attention masks? <../glossary.html#attention-mask>`__
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        inputs_embeds (`torch.FloatTensor` of shape `(0, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        image_embeds (`torch.FloatTensor` of shape `(batch_size, num_patches, hidden_size)`, *optional*):
            Optionally, instead of passing `pixel_values`, you can choose to directly pass an embedded representation.
            This is useful if you want more control over how to convert `pixel_values` into patch embeddings.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
VILT_IMAGES_AND_TEXT_CLASSIFICATION_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary. Indices can be obtained using [`AutoTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details. [What are input
            IDs?](../glossary#input-ids)
        attention_mask (`torch.FloatTensor` of shape `(0)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        token_type_ids (`torch.LongTensor` of shape `(0)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_images, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`ViltImageProcessor.__call__`] for details.
        pixel_mask (`torch.LongTensor` of shape `(batch_size, num_images, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            `What are attention masks? <../glossary.html#attention-mask>`__
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        inputs_embeds (`torch.FloatTensor` of shape `(0, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        image_embeds (`torch.FloatTensor` of shape `(batch_size, num_images, num_patches, hidden_size)`, *optional*):
            Optionally, instead of passing `pixel_values`, you can choose to directly pass an embedded representation.
            This is useful if you want more control over how to convert `pixel_values` into patch embeddings.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare ViLT Model transformer outputting raw hidden-states without any specific head on top.", VILT_START_DOCSTRING)
class ViltModel(ViltPreTrainedModel):
    def __init__(self, config, add_pooling_layer=True):
        super().__init__(config)
        self.config = config
        self.embeddings = ViltEmbeddings(config)
        self.encoder = ViltEncoder(config)
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.pooler = ViltPooler(config) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.text_embeddings.word_embeddings
    def set_input_embeddings(self, value): self.embeddings.text_embeddings.word_embeddings = value
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, image_token_type_idx: Optional[int] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[BaseModelOutputWithPooling, Tuple[torch.FloatTensor]]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            self.warn_if_padding_and_no_attention_mask(input_ids, attention_mask)
            input_shape = input_ids.size()
        elif inputs_embeds is not None: input_shape = inputs_embeds.size()[:-1]
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        text_batch_size, seq_length = input_shape
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if attention_mask is None: attention_mask = torch.ones(((text_batch_size, seq_length)), device=device)
        if pixel_values is not None and image_embeds is not None: raise ValueError("You cannot specify both pixel_values and image_embeds at the same time")
        elif pixel_values is None and image_embeds is None: raise ValueError("You have to specify either pixel_values or image_embeds")
        image_batch_size = pixel_values.shape[0] if pixel_values is not None else image_embeds.shape[0]
        if image_batch_size != text_batch_size: raise ValueError("The text inputs and image inputs need to have the same batch size")
        if pixel_mask is None: pixel_mask = torch.ones((image_batch_size, self.config.image_size, self.config.image_size), device=device)
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        embedding_output, attention_mask = self.embeddings(input_ids, attention_mask, token_type_ids, pixel_values, pixel_mask, inputs_embeds, image_embeds, image_token_type_idx=image_token_type_idx)
        extended_attention_mask: torch.Tensor = self.get_extended_attention_mask(attention_mask, input_shape)
        encoder_outputs = self.encoder(embedding_output, attention_mask=extended_attention_mask, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = encoder_outputs[0]
        sequence_output = self.layernorm(sequence_output)
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None
        if not return_dict: return (sequence_output, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
class ViltPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()
    def forward(self, hidden_states):
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output
@add_start_docstrings("ViLT Model with a language modeling head on top as done during pretraining.", VILT_START_DOCSTRING)
class ViltForMaskedLM(ViltPreTrainedModel):
    _tied_weights_keys = ["mlm_score.decoder.weight", "mlm_score.decoder.bias"]
    def __init__(self, config):
        super().__init__(config)
        self.vilt = ViltModel(config)
        self.mlm_score = ViltMLMHead(config)
        self.post_init()
    def get_output_embeddings(self): return self.mlm_score.decoder
    def set_output_embeddings(self, new_embeddings):
        self.mlm_score.decoder = new_embeddings
        self.mlm_score.bias = new_embeddings.bias
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[MaskedLMOutput, Tuple[torch.FloatTensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.vilt(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, pixel_values=pixel_values, pixel_mask=pixel_mask, head_mask=head_mask,
        inputs_embeds=inputs_embeds, image_embeds=image_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output, pooled_output = outputs[:2]
        text_seq_len = input_ids.shape[1] if input_ids is not None else inputs_embeds.shape[1]
        text_features, _ = (sequence_output[:, :text_seq_len], sequence_output[:, text_seq_len:])
        mlm_logits = self.mlm_score(text_features)
        masked_lm_loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            labels = labels.to(mlm_logits.device)
            masked_lm_loss = loss_fct(mlm_logits.view(-1, self.config.vocab_size), labels.view(-1))
        if not return_dict:
            output = (mlm_logits,) + outputs[2:]
            return ((masked_lm_loss,) + output) if masked_lm_loss is not None else output
        return MaskedLMOutput(loss=masked_lm_loss, logits=mlm_logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
class ViltPredictionHeadTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        if isinstance(config.hidden_act, str): self.transform_act_fn = ACT2FN[config.hidden_act]
        else: self.transform_act_fn = config.hidden_act
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        return hidden_states
class ViltMLMHead(nn.Module):
    def __init__(self, config, weight=None):
        super().__init__()
        self.config = config
        self.transform = ViltPredictionHeadTransform(config)
        self.decoder = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.bias = nn.Parameter(torch.zeros(config.vocab_size))
        if weight is not None: self.decoder.weight = weight
        self.decoder.bias = self.bias
    def _tie_weights(self): self.decoder.bias = self.bias
    def forward(self, x):
        x = self.transform(x)
        x = self.decoder(x)
        return x
@add_start_docstrings("Vilt Model transformer with a classifier head on top (a linear layer on top of the final hidden state of the [CLS] token) for visual question answering, e.g. for VQAv2.", VILT_START_DOCSTRING)
class ViltForQuestionAnswering(ViltPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.vilt = ViltModel(config)
        self.classifier = nn.Sequential(nn.Linear(config.hidden_size, config.hidden_size * 2), nn.LayerNorm(config.hidden_size * 2), nn.GELU(), nn.Linear(config.hidden_size * 2, config.num_labels))
        self.post_init()
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[SequenceClassifierOutput, Tuple[torch.FloatTensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.vilt(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, pixel_values=pixel_values, pixel_mask=pixel_mask, head_mask=head_mask,
        inputs_embeds=inputs_embeds, image_embeds=image_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooler_output = outputs.pooler_output if return_dict else outputs[1]
        logits = self.classifier(pooler_output)
        loss = None
        if labels is not None:
            labels = labels.to(logits.device)
            loss = nn.functional.binary_cross_entropy_with_logits(logits, labels) * labels.shape[1]
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Vilt Model transformer with a classifier head on top (a linear layer on top of the final hidden state of the [CLS] token) for image-to-text or text-to-image retrieval, e.g. MSCOCO and F30K.", VILT_START_DOCSTRING)
class ViltForImageAndTextRetrieval(ViltPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.vilt = ViltModel(config)
        self.rank_output = nn.Linear(config.hidden_size, 1)
        self.post_init()
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[SequenceClassifierOutput, Tuple[torch.FloatTensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        loss = None
        if labels is not None: raise NotImplementedError("Training is not yet supported.")
        outputs = self.vilt(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, pixel_values=pixel_values, pixel_mask=pixel_mask, head_mask=head_mask,
        inputs_embeds=inputs_embeds, image_embeds=image_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooler_output = outputs.pooler_output if return_dict else outputs[1]
        logits = self.rank_output(pooler_output)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
@add_start_docstrings("Vilt Model transformer with a classifier head on top for natural language visual reasoning, e.g. NLVR2.", VILT_IMAGES_AND_TEXT_CLASSIFICATION_INPUTS_DOCSTRING)
class ViltForImagesAndTextClassification(ViltPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.vilt = ViltModel(config)
        num_images = config.num_images
        self.classifier = nn.Sequential(nn.Linear(config.hidden_size * num_images, config.hidden_size * num_images), nn.LayerNorm(config.hidden_size * num_images), nn.GELU(),
        nn.Linear(config.hidden_size * num_images, config.num_labels))
        self.post_init()
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[ViltForImagesAndTextClassificationOutput, Tuple[torch.FloatTensor]]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is not None and pixel_values.ndim == 4: pixel_values = pixel_values.unsqueeze(1)
        if image_embeds is not None and image_embeds.ndim == 3: image_embeds = image_embeds.unsqueeze(1)
        num_images = pixel_values.shape[1] if pixel_values is not None else None
        if num_images is None: num_images = image_embeds.shape[1] if image_embeds is not None else None
        if num_images != self.config.num_images: raise ValueError("Make sure to match the number of images in the model with the number of images in the input.")
        pooler_outputs = []
        hidden_states = [] if output_hidden_states else None
        attentions = [] if output_attentions else None
        for i in range(num_images):
            outputs = self.vilt(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, pixel_values=pixel_values[:, i, :, :, :] if pixel_values is not None else None,
            pixel_mask=pixel_mask[:, i, :, :] if pixel_mask is not None else None, head_mask=head_mask, inputs_embeds=inputs_embeds, image_embeds=image_embeds[:, i, :, :] if image_embeds is not None else None,
            image_token_type_idx=i + 1, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
            pooler_output = outputs.pooler_output if return_dict else outputs[1]
            pooler_outputs.append(pooler_output)
            if output_hidden_states: hidden_states.append(outputs.hidden_states)
            if output_attentions: attentions.append(outputs.attentions)
        pooled_output = torch.cat(pooler_outputs, dim=-1)
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            labels = labels.to(logits.device)
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits, hidden_states, attentions)
            return ((loss,) + output) if loss is not None else output
        return ViltForImagesAndTextClassificationOutput(loss=loss, logits=logits, hidden_states=hidden_states, attentions=attentions)
@add_start_docstrings("ViLT Model with a token classification head on top (a linear layer on top of the final hidden-states of the text tokens) e.g. for Named-Entity-Recognition (NER) tasks.", VILT_START_DOCSTRING)
class ViltForTokenClassification(ViltPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.vilt = ViltModel(config, add_pooling_layer=False)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(VILT_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, token_type_ids: Optional[torch.LongTensor] = None,
    pixel_values: Optional[torch.FloatTensor] = None, pixel_mask: Optional[torch.LongTensor] = None, head_mask: Optional[torch.FloatTensor] = None, inputs_embeds: Optional[torch.FloatTensor] = None,
    image_embeds: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[TokenClassifierOutput, Tuple[torch.FloatTensor]]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.vilt(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, pixel_values=pixel_values, pixel_mask=pixel_mask, head_mask=head_mask,
        inputs_embeds=inputs_embeds, image_embeds=image_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        text_input_size = input_ids.shape[1] if input_ids is not None else inputs_embeds.shape[1]
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output[:, :text_input_size])
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            labels = labels.to(logits.device)
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
