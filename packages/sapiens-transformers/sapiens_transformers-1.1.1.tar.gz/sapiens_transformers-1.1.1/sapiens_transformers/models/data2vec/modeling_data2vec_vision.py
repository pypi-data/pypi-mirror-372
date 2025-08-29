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
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ...activations import ACT2FN
from ...modeling_outputs import (BaseModelOutput, BaseModelOutputWithPooling, ImageClassifierOutput, SemanticSegmenterOutput)
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import find_pruneable_heads_and_indices, prune_linear_layer
from ...utils import (add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings, torch_int)
from .configuration_data2vec_vision import Data2VecVisionConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "Data2VecVisionConfig"
_CHECKPOINT_FOR_DOC = "facebook/data2vec-vision-base"
_EXPECTED_OUTPUT_SHAPE = [1, 197, 768]
_IMAGE_CLASS_CHECKPOINT = "facebook/data2vec-vision-base-ft1k"
_IMAGE_CLASS_EXPECTED_OUTPUT = "remote control, remote"
@dataclass
class Data2VecVisionModelOutputWithPooling(BaseModelOutputWithPooling):
    """Args:"""
    pass
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class Data2VecVisionDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class Data2VecVisionEmbeddings(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        if config.use_mask_token: self.mask_token = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        else: self.mask_token = None
        self.patch_embeddings = Data2VecVisionPatchEmbeddings(config)
        self.patch_size = config.patch_size
        self.image_size = (config.image_size if isinstance(config.image_size, collections.abc.Iterable) else (config.image_size, config.image_size))
        num_patches = self.patch_embeddings.num_patches
        if config.use_absolute_position_embeddings: self.position_embeddings = nn.Parameter(torch.zeros(1, num_patches + 1, config.hidden_size))
        else: self.position_embeddings = None
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def interpolate_pos_encoding(self, embeddings: torch.Tensor, height: int, width: int) -> torch.Tensor:
        num_patches = embeddings.shape[1] - 1
        num_positions = self.position_embeddings.shape[1] - 1
        if not torch.jit.is_tracing() and num_patches == num_positions and height == width: return self.position_embeddings
        class_pos_embed = self.position_embeddings[:, :1]
        patch_pos_embed = self.position_embeddings[:, 1:]
        dim = embeddings.shape[-1]
        new_height = height // self.patch_size
        new_width = width // self.patch_size
        sqrt_num_positions = torch_int(num_positions**0.5)
        patch_pos_embed = patch_pos_embed.reshape(1, sqrt_num_positions, sqrt_num_positions, dim)
        patch_pos_embed = patch_pos_embed.permute(0, 3, 1, 2)
        patch_pos_embed = nn.functional.interpolate(patch_pos_embed, size=(new_height, new_width), mode="bicubic", align_corners=False)
        patch_pos_embed = patch_pos_embed.permute(0, 2, 3, 1).view(1, -1, dim)
        return torch.cat((class_pos_embed, patch_pos_embed), dim=1)
    def forward(self, pixel_values: torch.Tensor, bool_masked_pos: Optional[torch.BoolTensor] = None, interpolate_pos_encoding: bool = False) -> torch.Tensor:
        _, _, height, width = pixel_values.shape
        embeddings, (patch_height, patch_width) = self.patch_embeddings(pixel_values, self.position_embeddings[:, 1:, :] if self.position_embeddings is not None else None)
        batch_size, seq_len, _ = embeddings.size()
        if bool_masked_pos is not None:
            mask_tokens = self.mask_token.expand(batch_size, seq_len, -1)
            w = bool_masked_pos.unsqueeze(-1).type_as(mask_tokens)
            embeddings = embeddings * (1 - w) + mask_tokens * w
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        if self.position_embeddings is not None:
            if interpolate_pos_encoding: cls_tokens = cls_tokens + self.interpolate_pos_encoding(embeddings, height, width)
            else: cls_tokens = cls_tokens + self.position_embeddings[:, :1, :]
        embeddings = torch.cat((cls_tokens, embeddings), dim=1)
        embeddings = self.dropout(embeddings)
        return embeddings, (patch_height, patch_width)
class Data2VecVisionPatchEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        patch_shape = (image_size[0] // patch_size[0], image_size[1] // patch_size[1])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.patch_shape = patch_shape
        self.projection = nn.Conv2d(num_channels, hidden_size, kernel_size=patch_size, stride=patch_size)
    def forward(self, pixel_values: torch.Tensor, position_embedding: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, num_channels, height, width = pixel_values.shape
        if num_channels != self.num_channels: raise ValueError("Make sure that the channel dimension of the pixel values match with the one set in the configuration.")
        embeddings = self.projection(pixel_values)
        patch_height, patch_width = embeddings.shape[2], embeddings.shape[3]
        if position_embedding is not None:
            position_embedding = position_embedding.view(1, self.patch_shape[0], self.patch_shape[1], -1).permute(0, 3, 1, 2)
            position_embedding = nn.functional.interpolate(position_embedding, size=(patch_height, patch_width), mode="bicubic")
            embeddings = embeddings + position_embedding
        embeddings = embeddings.flatten(2).transpose(1, 2)
        return embeddings, (patch_height, patch_width)
class Data2VecVisionSelfAttention(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, window_size: Optional[tuple] = None) -> None:
        super().__init__()
        self.config = config
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size {config.hidden_size,} is not a multiple of the number of attention heads {config.num_attention_heads}.")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size, bias=False)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)
        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)
        if window_size: self.relative_position_bias = Data2VecVisionRelativePositionBias(config, window_size=window_size)
        else: self.relative_position_bias = None
    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, relative_position_bias: Optional["Data2VecVisionRelativePositionBias"] = None,
    interpolate_pos_encoding: bool = False, resolution: Optional[Tuple[int]] = None) -> Union[Tuple[torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
        mixed_query_layer = self.query(hidden_states)
        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if self.relative_position_bias is not None:
            height, width = resolution
            window_size = (height // self.config.patch_size, width // self.config.patch_size)
            attention_scores = attention_scores + self.relative_position_bias(window_size, interpolate_pos_encoding, dim_size=hidden_states.shape[1])
        if relative_position_bias is not None: attention_scores = attention_scores + relative_position_bias
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        return outputs
class Data2VecVisionSelfOutput(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor, gamma=None) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class Data2VecVisionAttention(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, window_size: Optional[tuple] = None) -> None:
        super().__init__()
        self.attention = Data2VecVisionSelfAttention(config, window_size=window_size)
        self.output = Data2VecVisionSelfOutput(config)
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
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, relative_position_bias: Optional["Data2VecVisionRelativePositionBias"] = None,
    interpolate_pos_encoding: bool = False, resolution: Optional[Tuple[int]] = None) -> Union[Tuple[torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
        self_outputs = self.attention(hidden_states, head_mask, output_attentions, relative_position_bias, interpolate_pos_encoding, resolution)
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
class Data2VecVisionIntermediate(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class Data2VecVisionOutput(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class Data2VecVisionLayer(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, window_size: Optional[tuple] = None, drop_path_rate: float = 0.0) -> None:
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.attention = Data2VecVisionAttention(config, window_size=window_size)
        self.intermediate = Data2VecVisionIntermediate(config)
        self.output = Data2VecVisionOutput(config)
        self.layernorm_before = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.drop_path = Data2VecVisionDropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()
        self.layernorm_after = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        init_values = config.layer_scale_init_value
        if init_values > 0:
            self.lambda_1 = nn.Parameter(init_values * torch.ones((config.hidden_size)), requires_grad=True)
            self.lambda_2 = nn.Parameter(init_values * torch.ones((config.hidden_size)), requires_grad=True)
        else: self.lambda_1, self.lambda_2 = None, None
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, relative_position_bias: Optional["Data2VecVisionRelativePositionBias"] = None,
    interpolate_pos_encoding: bool = False, resolution: Optional[Tuple[int]] = None) -> Union[Tuple[torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
        self_attention_outputs = self.attention(self.layernorm_before(hidden_states), head_mask, output_attentions=output_attentions, relative_position_bias=relative_position_bias, interpolate_pos_encoding=interpolate_pos_encoding, resolution=resolution)
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        if self.lambda_1 is not None: attention_output = self.lambda_1 * attention_output
        hidden_states = self.drop_path(attention_output) + hidden_states
        layer_output = self.layernorm_after(hidden_states)
        layer_output = self.intermediate(layer_output)
        layer_output = self.output(layer_output)
        if self.lambda_2 is not None: layer_output = self.lambda_2 * layer_output
        layer_output = self.drop_path(layer_output) + hidden_states
        outputs = (layer_output,) + outputs
        return outputs
class Data2VecVisionRelativePositionBias(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, window_size: tuple) -> None:
        super().__init__()
        self.window_size = window_size
        self.num_relative_distance = (2 * window_size[0] - 1) * (2 * window_size[1] - 1) + 3
        self.relative_position_bias_table = nn.Parameter(torch.zeros(self.num_relative_distance, config.num_attention_heads))
        self.relative_position_indices = {}
    def generate_relative_position_index(self, window_size: Tuple[int, int]) -> torch.Tensor:
        num_relative_distance = (2 * window_size[0] - 1) * (2 * window_size[1] - 1) + 3
        window_area = window_size[0] * window_size[1]
        grid = torch.meshgrid(torch.arange(window_size[0]), torch.arange(window_size[1]), indexing="ij")
        coords = torch.stack(grid)
        coords_flatten = torch.flatten(coords, 1)
        relative_coords = coords_flatten[:, :, None] - coords_flatten[:, None, :]
        relative_coords = relative_coords.permute(1, 2, 0).contiguous()
        relative_coords[:, :, 0] += window_size[0] - 1
        relative_coords[:, :, 1] += window_size[1] - 1
        relative_coords[:, :, 0] *= 2 * window_size[1] - 1
        relative_position_index = torch.zeros(size=(window_area + 1,) * 2, dtype=relative_coords.dtype)
        relative_position_index[1:, 1:] = relative_coords.sum(-1)
        relative_position_index[0, 0:] = num_relative_distance - 3
        relative_position_index[0:, 0] = num_relative_distance - 2
        relative_position_index[0, 0] = num_relative_distance - 1
        return relative_position_index
    def forward(self, window_size, interpolate_pos_encoding: bool = False, dim_size=None) -> torch.Tensor:
        old_height = 2 * self.window_size[0] - 1
        old_width = 2 * self.window_size[1] - 1
        new_height = 2 * window_size[0] - 1
        new_width = 2 * window_size[1] - 1
        old_relative_position_bias_table = self.relative_position_bias_table
        old_num_relative_distance = self.num_relative_distance
        new_num_relative_distance = new_height * new_width + 3
        old_sub_table = old_relative_position_bias_table[: old_num_relative_distance - 3]
        old_sub_table = old_sub_table.reshape(1, old_width, old_height, -1).permute(0, 3, 1, 2)
        new_sub_table = nn.functional.interpolate(old_sub_table, size=(torch_int(new_height), torch_int(new_width)), mode="bilinear")
        new_sub_table = new_sub_table.permute(0, 2, 3, 1).reshape(new_num_relative_distance - 3, -1)
        new_relative_position_bias_table = torch.cat([new_sub_table, old_relative_position_bias_table[old_num_relative_distance - 3 :]])
        key = window_size
        if key not in self.relative_position_indices.keys(): self.relative_position_indices[key] = self.generate_relative_position_index(window_size)
        relative_position_bias = new_relative_position_bias_table[self.relative_position_indices[key].view(-1)]
        relative_position_bias = relative_position_bias.view(window_size[0] * window_size[1] + 1, window_size[0] * window_size[1] + 1, -1)
        relative_position_bias = relative_position_bias.permute(2, 0, 1).contiguous()
        if interpolate_pos_encoding: relative_position_bias = nn.functional.interpolate(relative_position_bias.unsqueeze(1), size=(dim_size, dim_size), mode="bilinear", align_corners=False).squeeze(1)
        return relative_position_bias.unsqueeze(0)
class Data2VecVisionEncoder(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, window_size: Optional[tuple] = None) -> None:
        super().__init__()
        self.config = config
        if config.use_shared_relative_position_bias: self.relative_position_bias = Data2VecVisionRelativePositionBias(config, window_size=window_size)
        else: self.relative_position_bias = None
        dpr = [x.item() for x in torch.linspace(0, config.drop_path_rate, config.num_hidden_layers)]
        self.layer = nn.ModuleList([Data2VecVisionLayer(config, window_size=window_size if config.use_relative_position_bias else None, drop_path_rate=dpr[i]) for i in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, output_hidden_states: bool = False,
    interpolate_pos_encoding: bool = False, resolution: Optional[Tuple[int]] = None, return_dict: bool = True) -> Union[tuple, BaseModelOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_head_mask = head_mask[i] if head_mask is not None else None
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states, layer_head_mask, output_attentions)
            else:
                height, width = resolution
                window_size = (height // self.config.patch_size, width // self.config.patch_size)
                relative_position_bias = (self.relative_position_bias(window_size, interpolate_pos_encoding=interpolate_pos_encoding, dim_size=hidden_states.shape[1]) if self.relative_position_bias is not None else None)
                layer_outputs = layer_module(hidden_states, layer_head_mask, output_attentions, relative_position_bias, interpolate_pos_encoding, resolution)
            hidden_states = layer_outputs[0]
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions)
class Data2VecVisionPreTrainedModel(PreTrainedModel):
    config_class = Data2VecVisionConfig
    base_model_prefix = "data2vec_vision"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = ["Data2VecVisionLayer"]
    _keys_to_ignore_on_load_unexpected = [r".*relative_position_index.*"]
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
DATA2VEC_VISION_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`Data2VecVisionConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
DATA2VEC_VISION_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`BeitImageProcessor.__call__`] for details.
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        interpolate_pos_encoding (`bool`, *optional*, defaults to `False`):
            Whether to interpolate the pre-trained position encodings.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare Data2VecVision Model transformer outputting raw hidden-states without any specific head on top.", DATA2VEC_VISION_START_DOCSTRING)
class Data2VecVisionModel(Data2VecVisionPreTrainedModel):
    def __init__(self, config: Data2VecVisionConfig, add_pooling_layer: bool = False) -> None:
        super().__init__(config)
        self.config = config
        self.embeddings = Data2VecVisionEmbeddings(config)
        self.encoder = Data2VecVisionEncoder(config, window_size=self.embeddings.patch_embeddings.patch_shape)
        self.layernorm = (nn.Identity() if config.use_mean_pooling else nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps))
        self.pooler = Data2VecVisionPooler(config) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.patch_embeddings
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(DATA2VEC_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, bool_masked_pos: Optional[torch.BoolTensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, interpolate_pos_encoding: bool = False, return_dict: Optional[bool] = None) -> Union[tuple, Data2VecVisionModelOutputWithPooling]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        embedding_output, _ = self.embeddings(pixel_values, bool_masked_pos=bool_masked_pos, interpolate_pos_encoding=interpolate_pos_encoding)
        resolution = pixel_values.shape[2:]
        encoder_outputs = self.encoder(embedding_output, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, resolution=resolution,
        return_dict=return_dict, interpolate_pos_encoding=interpolate_pos_encoding)
        sequence_output = encoder_outputs[0]
        sequence_output = self.layernorm(sequence_output)
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None
        if not return_dict:
            head_outputs = (sequence_output, pooled_output) if pooled_output is not None else (sequence_output,)
            return head_outputs + encoder_outputs[1:]
        return Data2VecVisionModelOutputWithPooling(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
class Data2VecVisionPooler(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.layernorm = (nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps) if config.use_mean_pooling else None)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if self.layernorm is not None:
            patch_tokens = hidden_states[:, 1:, :]
            pooled_output = self.layernorm(patch_tokens.mean(1))
        else: pooled_output = hidden_states[:, 0]
        return pooled_output
@add_start_docstrings("Data2VecVision Model transformer with an image classification head on top (a linear layer on top of the average of the final hidden states of the patch tokens) e.g. for ImageNet.", DATA2VEC_VISION_START_DOCSTRING)
class Data2VecVisionForImageClassification(Data2VecVisionPreTrainedModel):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__(config)
        self.num_labels = config.num_labels
        self.data2vec_vision = Data2VecVisionModel(config, add_pooling_layer=True)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels) if config.num_labels > 0 else nn.Identity()
        self.post_init()
    @add_start_docstrings_to_model_forward(DATA2VEC_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, interpolate_pos_encoding: bool = False, return_dict: Optional[bool] = None) -> Union[tuple, ImageClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.data2vec_vision(pixel_values, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, interpolate_pos_encoding=interpolate_pos_encoding, return_dict=return_dict)
        pooled_output = outputs.pooler_output if return_dict else outputs[1]
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return ImageClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
class Data2VecVisionConvModule(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: Union[int, Tuple[int, int]], padding: Union[int, Tuple[int, int], str] = 0,
    bias: bool = False, dilation: Union[int, Tuple[int, int]] = 1) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, padding=padding, bias=bias, dilation=dilation)
        self.bn = nn.BatchNorm2d(out_channels)
        self.activation = nn.ReLU()
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        output = self.conv(input)
        output = self.bn(output)
        output = self.activation(output)
        return output
class Data2VecVisionPyramidPoolingBlock(nn.Module):
    def __init__(self, pool_scale: int, in_channels: int, channels: int) -> None:
        super().__init__()
        self.layers = [nn.AdaptiveAvgPool2d(pool_scale), Data2VecVisionConvModule(in_channels, channels, kernel_size=1)]
        for i, layer in enumerate(self.layers): self.add_module(str(i), layer)
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class Data2VecVisionPyramidPoolingModule(nn.Module):
    def __init__(self, pool_scales: Tuple[int, ...], in_channels: int, channels: int, align_corners: bool) -> None:
        super().__init__()
        self.pool_scales = pool_scales
        self.align_corners = align_corners
        self.in_channels = in_channels
        self.channels = channels
        self.blocks = []
        for i, pool_scale in enumerate(pool_scales):
            block = Data2VecVisionPyramidPoolingBlock(pool_scale=pool_scale, in_channels=in_channels, channels=channels)
            self.blocks.append(block)
            self.add_module(str(i), block)
    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        ppm_outs = []
        for ppm in self.blocks:
            ppm_out = ppm(x)
            upsampled_ppm_out = nn.functional.interpolate(ppm_out, size=x.size()[2:], mode="bilinear", align_corners=self.align_corners)
            ppm_outs.append(upsampled_ppm_out)
        return ppm_outs
class Data2VecVisionUperHead(nn.Module):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__()
        self.pool_scales = config.pool_scales
        self.in_channels = [config.hidden_size] * 4
        self.channels = config.hidden_size
        self.align_corners = False
        self.classifier = nn.Conv2d(self.channels, config.num_labels, kernel_size=1)
        self.psp_modules = Data2VecVisionPyramidPoolingModule(self.pool_scales, self.in_channels[-1], self.channels, align_corners=self.align_corners)
        self.bottleneck = Data2VecVisionConvModule(self.in_channels[-1] + len(self.pool_scales) * self.channels, self.channels, kernel_size=3, padding=1)
        self.lateral_convs = nn.ModuleList()
        self.fpn_convs = nn.ModuleList()
        for in_channels in self.in_channels[:-1]:
            l_conv = Data2VecVisionConvModule(in_channels, self.channels, kernel_size=1)
            fpn_conv = Data2VecVisionConvModule(self.channels, self.channels, kernel_size=3, padding=1)
            self.lateral_convs.append(l_conv)
            self.fpn_convs.append(fpn_conv)
        self.fpn_bottleneck = Data2VecVisionConvModule(len(self.in_channels) * self.channels, self.channels, kernel_size=3, padding=1)
    def psp_forward(self, inputs):
        x = inputs[-1]
        psp_outs = [x]
        psp_outs.extend(self.psp_modules(x))
        psp_outs = torch.cat(psp_outs, dim=1)
        output = self.bottleneck(psp_outs)
        return output
    def forward(self, encoder_hidden_states: torch.Tensor) -> torch.Tensor:
        laterals = [lateral_conv(encoder_hidden_states[i]) for i, lateral_conv in enumerate(self.lateral_convs)]
        laterals.append(self.psp_forward(encoder_hidden_states))
        used_backbone_levels = len(laterals)
        for i in range(used_backbone_levels - 1, 0, -1):
            prev_shape = laterals[i - 1].shape[2:]
            laterals[i - 1] = laterals[i - 1] + nn.functional.interpolate(laterals[i], size=prev_shape, mode="bilinear", align_corners=self.align_corners)
        fpn_outs = [self.fpn_convs[i](laterals[i]) for i in range(used_backbone_levels - 1)]
        fpn_outs.append(laterals[-1])
        for i in range(used_backbone_levels - 1, 0, -1): fpn_outs[i] = nn.functional.interpolate(fpn_outs[i], size=fpn_outs[0].shape[2:], mode="bilinear", align_corners=self.align_corners)
        fpn_outs = torch.cat(fpn_outs, dim=1)
        output = self.fpn_bottleneck(fpn_outs)
        output = self.classifier(output)
        return output
class Data2VecVisionFCNHead(nn.Module):
    def __init__(self, config: Data2VecVisionConfig, in_index: int = 2, kernel_size: int = 3, dilation: Union[int, Tuple[int, int]] = 1) -> None:
        super().__init__()
        self.in_channels = config.hidden_size
        self.channels = config.auxiliary_channels
        self.num_convs = config.auxiliary_num_convs
        self.concat_input = config.auxiliary_concat_input
        self.in_index = in_index
        conv_padding = (kernel_size // 2) * dilation
        convs = []
        convs.append(Data2VecVisionConvModule(self.in_channels, self.channels, kernel_size=kernel_size, padding=conv_padding, dilation=dilation))
        for i in range(self.num_convs - 1): convs.append(Data2VecVisionConvModule(self.channels, self.channels, kernel_size=kernel_size, padding=conv_padding, dilation=dilation))
        if self.num_convs == 0: self.convs = nn.Identity()
        else: self.convs = nn.Sequential(*convs)
        if self.concat_input: self.conv_cat = Data2VecVisionConvModule(self.in_channels + self.channels, self.channels, kernel_size=kernel_size, padding=kernel_size // 2)
        self.classifier = nn.Conv2d(self.channels, config.num_labels, kernel_size=1)
    def forward(self, encoder_hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = encoder_hidden_states[self.in_index]
        output = self.convs(hidden_states)
        if self.concat_input: output = self.conv_cat(torch.cat([hidden_states, output], dim=1))
        output = self.classifier(output)
        return output
@add_start_docstrings("Data2VecVision Model transformer with a semantic segmentation head on top e.g. for ADE20k, CityScapes.", DATA2VEC_VISION_START_DOCSTRING)
class Data2VecVisionForSemanticSegmentation(Data2VecVisionPreTrainedModel):
    def __init__(self, config: Data2VecVisionConfig) -> None:
        super().__init__(config)
        self.num_labels = config.num_labels
        self.data2vec_vision = Data2VecVisionModel(config, add_pooling_layer=False)
        if len(self.config.out_indices) != 4: raise ValueError("Data2VecVisionForSemanticSegmentation requires config.out_indices to be a list of 4 integers, specifying which features to use from the backbone. One can use [3, 5, 7, 11] in case of a base-sized architecture.")
        self.fpn1 = nn.Sequential(nn.ConvTranspose2d(config.hidden_size, config.hidden_size, kernel_size=2, stride=2), nn.BatchNorm2d(config.hidden_size), nn.GELU(), nn.ConvTranspose2d(config.hidden_size, config.hidden_size, kernel_size=2, stride=2))
        self.fpn2 = nn.Sequential(nn.ConvTranspose2d(config.hidden_size, config.hidden_size, kernel_size=2, stride=2))
        self.fpn3 = nn.Identity()
        self.fpn4 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.decode_head = Data2VecVisionUperHead(config)
        self.auxiliary_head = Data2VecVisionFCNHead(config) if config.use_auxiliary_head else None
        self.post_init()
    def compute_loss(self, logits, auxiliary_logits, labels):
        upsampled_logits = nn.functional.interpolate(logits, size=labels.shape[-2:], mode="bilinear", align_corners=False)
        if auxiliary_logits is not None: upsampled_auxiliary_logits = nn.functional.interpolate(auxiliary_logits, size=labels.shape[-2:], mode="bilinear", align_corners=False)
        loss_fct = CrossEntropyLoss(ignore_index=self.config.semantic_loss_ignore_index)
        main_loss = loss_fct(upsampled_logits, labels)
        loss = main_loss
        if auxiliary_logits is not None:
            auxiliary_loss = loss_fct(upsampled_auxiliary_logits, labels)
            loss += self.config.auxiliary_loss_weight * auxiliary_loss
        return loss
    @add_start_docstrings_to_model_forward(DATA2VEC_VISION_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, interpolate_pos_encoding: bool = False, return_dict: Optional[bool] = None) -> Union[tuple, SemanticSegmenterOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        if labels is not None and self.config.num_labels == 1: raise ValueError("The number of labels should be greater than one")
        outputs = self.data2vec_vision(pixel_values, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=True, interpolate_pos_encoding=interpolate_pos_encoding, return_dict=return_dict)
        encoder_hidden_states = outputs.hidden_states if return_dict else outputs[1]
        features = [feature for idx, feature in enumerate(encoder_hidden_states) if idx + 1 in self.config.out_indices]
        batch_size = pixel_values.shape[0]
        patch_resolution = self.config.image_size // self.config.patch_size
        features = [x[:, 1:, :].permute(0, 2, 1).reshape(batch_size, -1, patch_resolution, patch_resolution) for x in features]
        ops = [self.fpn1, self.fpn2, self.fpn3, self.fpn4]
        for i in range(len(features)): features[i] = ops[i](features[i])
        logits = self.decode_head(features)
        auxiliary_logits = None
        if self.auxiliary_head is not None: auxiliary_logits = self.auxiliary_head(features)
        loss = None
        if labels is not None: loss = self.compute_loss(logits, auxiliary_logits, labels)
        if not return_dict:
            if output_hidden_states: output = (logits,) + outputs[1:]
            else: output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SemanticSegmenterOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states if output_hidden_states else None, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
