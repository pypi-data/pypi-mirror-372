"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections.abc
import math
from typing import Dict, List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...modeling_outputs import BackboneOutput, BaseModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from ...utils.backbone_utils import BackboneMixin
from .configuration_vitdet import VitDetConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "VitDetConfig"
class VitDetEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        image_size, patch_size = config.pretrain_image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        if config.use_absolute_position_embeddings:
            num_positions = num_patches + 1
            self.position_embeddings = nn.Parameter(torch.zeros(1, num_positions, config.hidden_size))
        else: self.position_embeddings = None
        self.projection = nn.Conv2d(num_channels, hidden_size, kernel_size=patch_size, stride=patch_size)
    def get_absolute_positions(self, abs_pos_embeddings, has_cls_token, height, width):
        if has_cls_token: abs_pos_embeddings = abs_pos_embeddings[:, 1:]
        num_position = abs_pos_embeddings.shape[1]
        size = int(math.sqrt(num_position))
        if size * size != num_position: raise ValueError("Absolute position embeddings must be a square number.")
        if torch.jit.is_tracing() or (size != height or size != width):
            new_abs_pos_embeddings = nn.functional.interpolate(abs_pos_embeddings.reshape(1, size, size, -1).permute(0, 3, 1, 2), size=(height, width), mode="bicubic", align_corners=False)
            return new_abs_pos_embeddings.permute(0, 2, 3, 1)
        else: return abs_pos_embeddings.reshape(1, height, width, -1)
    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        num_channels = pixel_values.shape[1]
        if num_channels != self.num_channels: raise ValueError(f"Make sure that the channel dimension of the pixel values match with the one set in the configuration. Expected {self.num_channels} but got {num_channels}.")
        embeddings = self.projection(pixel_values)
        if self.position_embeddings is not None:
            embeddings = embeddings.permute(0, 2, 3, 1)
            embeddings = embeddings + self.get_absolute_positions(self.position_embeddings, True, embeddings.shape[1], embeddings.shape[2])
            embeddings = embeddings.permute(0, 3, 1, 2)
        return embeddings
@torch.jit.script_if_tracing
def get_rel_pos(q_size, k_size, rel_pos):
    max_rel_dist = int(2 * max(q_size, k_size) - 1)
    if rel_pos.shape[0] != max_rel_dist:
        rel_pos_resized = nn.functional.interpolate(rel_pos.reshape(1, rel_pos.shape[0], -1).permute(0, 2, 1), size=max_rel_dist, mode="linear")
        rel_pos_resized = rel_pos_resized.reshape(-1, max_rel_dist).permute(1, 0)
    else: rel_pos_resized = rel_pos
    q_coords = torch.arange(q_size)[:, None] * max(k_size / q_size, 1.0)
    k_coords = torch.arange(k_size)[None, :] * max(q_size / k_size, 1.0)
    relative_coords = (q_coords - k_coords) + (k_size - 1) * max(q_size / k_size, 1.0)
    return rel_pos_resized[relative_coords.long()]
def add_decomposed_relative_positions(attn, queries, rel_pos_h, rel_pos_w, q_size, k_size):
    queries_height, queries_width = q_size
    keys_height, keys_width = k_size
    relative_height = get_rel_pos(queries_height, keys_height, rel_pos_h)
    relative_width = get_rel_pos(queries_width, keys_width, rel_pos_w)
    batch_size, _, dim = queries.shape
    r_q = queries.reshape(batch_size, queries_height, queries_width, dim)
    relative_height = torch.einsum("bhwc,hkc->bhwk", r_q, relative_height)
    relative_weight = torch.einsum("bhwc,wkc->bhwk", r_q, relative_width)
    attn = (attn.view(batch_size, queries_height, queries_width, keys_height, keys_width) + relative_height[:, :, :, :, None] + relative_weight[:, :, :, None, :]).view(batch_size, queries_height * queries_width, keys_height * keys_width)
    return attn
class VitDetAttention(nn.Module):
    def __init__(self, config, input_size=None):
        super().__init__()
        dim = config.hidden_size
        num_heads = config.num_attention_heads
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim**-0.5
        self.qkv = nn.Linear(dim, dim * 3, bias=config.qkv_bias)
        self.proj = nn.Linear(dim, dim)
        self.use_relative_position_embeddings = config.use_relative_position_embeddings
        if self.use_relative_position_embeddings:
            self.rel_pos_h = nn.Parameter(torch.zeros(2 * input_size[0] - 1, head_dim))
            self.rel_pos_w = nn.Parameter(torch.zeros(2 * input_size[1] - 1, head_dim))
    def forward(self, hidden_state, output_attentions=False):
        batch_size, height, width, _ = hidden_state.shape
        qkv = self.qkv(hidden_state).reshape(batch_size, height * width, 3, self.num_heads, -1).permute(2, 0, 3, 1, 4)
        queries, keys, values = qkv.reshape(3, batch_size * self.num_heads, height * width, -1).unbind(0)
        attention_scores = (queries * self.scale) @ keys.transpose(-2, -1)
        if self.use_relative_position_embeddings: attention_scores = add_decomposed_relative_positions(attention_scores, queries, self.rel_pos_h, self.rel_pos_w, (height, width), (height, width))
        attention_probs = attention_scores.softmax(dim=-1)
        hidden_state = attention_probs @ values
        hidden_state = hidden_state.view(batch_size, self.num_heads, height, width, -1)
        hidden_state = hidden_state.permute(0, 2, 3, 1, 4)
        hidden_state = hidden_state.reshape(batch_size, height, width, -1)
        hidden_state = self.proj(hidden_state)
        if output_attentions:
            attention_probs = attention_probs.reshape(batch_size, self.num_heads, attention_probs.shape[-2], attention_probs.shape[-1])
            outputs = (hidden_state, attention_probs)
        else: outputs = (hidden_state,)
        return outputs
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class VitDetDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class VitDetLayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.normalized_shape = (normalized_shape,)
    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + self.eps)
        x = self.weight[:, None, None] * x + self.bias[:, None, None]
        return x
class VitDetResBottleneckBlock(nn.Module):
    def __init__(self, config, in_channels, out_channels, bottleneck_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, bottleneck_channels, 1, bias=False)
        self.norm1 = VitDetLayerNorm(bottleneck_channels)
        self.act1 = ACT2FN[config.hidden_act]
        self.conv2 = nn.Conv2d(bottleneck_channels, bottleneck_channels, 3, padding=1, bias=False)
        self.norm2 = VitDetLayerNorm(bottleneck_channels)
        self.act2 = ACT2FN[config.hidden_act]
        self.conv3 = nn.Conv2d(bottleneck_channels, out_channels, 1, bias=False)
        self.norm3 = VitDetLayerNorm(out_channels)
    def forward(self, x):
        out = x
        for layer in self.children(): out = layer(out)
        out = x + out
        return out
class VitDetMlp(nn.Module):
    def __init__(self, config, in_features: int, hidden_features: int) -> None:
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = ACT2FN[config.hidden_act]
        self.fc2 = nn.Linear(hidden_features, in_features)
        self.drop = nn.Dropout(config.dropout_prob)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x
def window_partition(hidden_state, window_size):
    batch_size, height, width, num_channels = hidden_state.shape
    pad_height = (window_size - height % window_size) % window_size
    pad_width = (window_size - width % window_size) % window_size
    hidden_state = nn.functional.pad(hidden_state, (0, 0, 0, pad_width, 0, pad_height))
    padded_height, padded_width = height + pad_height, width + pad_width
    hidden_state = hidden_state.view(batch_size, padded_height // window_size, window_size, padded_width // window_size, window_size, num_channels)
    windows = hidden_state.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, num_channels)
    return windows, (padded_height, padded_width)
def window_unpartition(windows, window_size, pad_height_width, height_width):
    padded_height, padded_width = pad_height_width
    height, width = height_width
    batch_size = windows.shape[0] // (padded_height * padded_width // window_size // window_size)
    hidden_state = windows.view(batch_size, padded_height // window_size, padded_width // window_size, window_size, window_size, -1)
    hidden_state = hidden_state.permute(0, 1, 3, 2, 4, 5).contiguous()
    hidden_state = hidden_state.view(batch_size, padded_height, padded_width, -1)
    hidden_state = hidden_state[:, :height, :width, :].contiguous()
    return hidden_state
class VitDetLayer(nn.Module):
    def __init__(self, config: VitDetConfig, drop_path_rate: float = 0, window_size: int = 0, use_residual_block: bool = False) -> None:
        super().__init__()
        dim = config.hidden_size
        input_size = (config.image_size // config.patch_size, config.image_size // config.patch_size)
        self.norm1 = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        self.attention = VitDetAttention(config, input_size=input_size if window_size == 0 else (window_size, window_size))
        self.drop_path = VitDetDropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()
        self.norm2 = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        self.mlp = VitDetMlp(config=config, in_features=dim, hidden_features=int(dim * config.mlp_ratio))
        self.window_size = window_size
        self.use_residual_block = use_residual_block
        if self.use_residual_block: self.residual = VitDetResBottleneckBlock(config=config, in_channels=dim, out_channels=dim, bottleneck_channels=dim // 2)
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False) -> Union[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor]]:
        hidden_states = hidden_states.permute(0, 2, 3, 1)
        shortcut = hidden_states
        hidden_states = self.norm1(hidden_states)
        if self.window_size > 0:
            height, width = hidden_states.shape[1], hidden_states.shape[2]
            hidden_states, pad_height_width = window_partition(hidden_states, self.window_size)
        self_attention_outputs = self.attention(hidden_states, output_attentions=output_attentions)
        hidden_states = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        if self.window_size > 0: hidden_states = window_unpartition(hidden_states, self.window_size, pad_height_width, (height, width))
        hidden_states = shortcut + self.drop_path(hidden_states)
        hidden_states = hidden_states + self.drop_path(self.mlp(self.norm2(hidden_states)))
        hidden_states = hidden_states.permute(0, 3, 1, 2)
        if self.use_residual_block: hidden_states = self.residual(hidden_states)
        outputs = (hidden_states,) + outputs
        return outputs
class VitDetEncoder(nn.Module):
    def __init__(self, config: VitDetConfig) -> None:
        super().__init__()
        self.config = config
        depth = config.num_hidden_layers
        drop_path_rate = [x.item() for x in torch.linspace(0, config.drop_path_rate, depth)]
        layers = []
        for i in range(depth): layers.append(VitDetLayer(config, drop_path_rate=drop_path_rate[i], window_size=config.window_size if i in config.window_block_indices else 0, use_residual_block=i in config.residual_block_indices))
        self.layer = nn.ModuleList(layers)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_attentions: bool = False, output_hidden_states: bool = False, return_dict: bool = True) -> Union[tuple, BaseModelOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            layer_head_mask = head_mask[i] if head_mask is not None else None
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states, layer_head_mask, output_attentions)
            else: layer_outputs = layer_module(hidden_states, layer_head_mask, output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions)
def caffe2_msra_fill(module: nn.Module) -> None:
    nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
    if module.bias is not None: nn.init.constant_(module.bias, 0)
class VitDetPreTrainedModel(PreTrainedModel):
    config_class = VitDetConfig
    base_model_prefix = "vitdet"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = []
    def _init_weights(self, module: Union[nn.Linear, nn.Conv2d, nn.LayerNorm]) -> None:
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data = nn.init.trunc_normal_(module.weight.data.to(torch.float32), mean=0.0, std=self.config.initializer_range).to(module.weight.dtype)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, VitDetEmbeddings): module.position_embeddings.data = nn.init.trunc_normal_(module.position_embeddings.data.to(torch.float32),
        mean=0.0, std=self.config.initializer_range).to(module.position_embeddings.dtype)
        elif isinstance(module, VitDetAttention) and self.config.use_relative_position_embeddings:
            module.rel_pos_h.data = nn.init.trunc_normal_(module.rel_pos_h.data.to(torch.float32), mean=0.0, std=self.config.initializer_range)
            module.rel_pos_w.data = nn.init.trunc_normal_(module.rel_pos_w.data.to(torch.float32), mean=0.0, std=self.config.initializer_range)
        elif isinstance(module, VitDetResBottleneckBlock):
            for layer in [module.conv1, module.conv2, module.conv3]: caffe2_msra_fill(layer)
            for layer in [module.norm1, module.norm2]:
                layer.weight.data.fill_(1.0)
                layer.bias.data.zero_()
            module.norm3.weight.data.zero_()
            module.norm3.bias.data.zero_()
VITDET_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`VitDetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
VITDET_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See [`ViTImageProcessor.__call__`]
            for details.
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
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare VitDet Transformer model outputting raw hidden-states without any specific head on top.", VITDET_START_DOCSTRING)
class VitDetModel(VitDetPreTrainedModel):
    def __init__(self, config: VitDetConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = VitDetEmbeddings(config)
        self.encoder = VitDetEncoder(config)
        self.post_init()
    def get_input_embeddings(self) -> VitDetEmbeddings: return self.embeddings.projection
    def _prune_heads(self, heads_to_prune: Dict[int, List[int]]) -> None:
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(VITDET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, head_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        embedding_output = self.embeddings(pixel_values)
        encoder_outputs = self.encoder(embedding_output, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = encoder_outputs[0]
        if not return_dict: return (sequence_output,) + encoder_outputs[1:]
        return BaseModelOutput(last_hidden_state=sequence_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
@add_start_docstrings("ViTDet backbone, to be used with frameworks like Mask R-CNN.", VITDET_START_DOCSTRING)
class VitDetBackbone(VitDetPreTrainedModel, BackboneMixin):
    def __init__(self, config):
        super().__init__(config)
        super()._init_backbone(config)
        self.embeddings = VitDetEmbeddings(config)
        self.encoder = VitDetEncoder(config)
        self.num_features = [config.hidden_size for _ in range(config.num_hidden_layers + 1)]
        self.post_init()
    def get_input_embeddings(self) -> VitDetEmbeddings: return self.embeddings.projection
    @add_start_docstrings_to_model_forward(VITDET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None, return_dict: Optional[bool] = None) -> BackboneOutput:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        embedding_output = self.embeddings(pixel_values)
        outputs = self.encoder(embedding_output, output_hidden_states=True, output_attentions=output_attentions, return_dict=return_dict)
        hidden_states = outputs.hidden_states if return_dict else outputs[1]
        feature_maps = ()
        for stage, hidden_state in zip(self.stage_names, hidden_states):
            if stage in self.out_features: feature_maps += (hidden_state,)
        if not return_dict:
            if output_hidden_states: output = (feature_maps,) + outputs[1:]
            else: output = (feature_maps,) + outputs[2:]
            return output
        return BackboneOutput(feature_maps=feature_maps, hidden_states=outputs.hidden_states if output_hidden_states else None, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
