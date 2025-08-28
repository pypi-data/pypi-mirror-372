"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections.abc
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import functional as F
from ...activations import ACT2FN
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings, torch_int)
from .configuration_seggpt import SegGptConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "SegGptConfig"
_CHECKPOINT_FOR_DOC = "BAAI/seggpt-vit-large"
_EXPECTED_OUTPUT_SHAPE = [3, 896, 448]
@dataclass
class SegGptEncoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    intermediate_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class SegGptImageSegmentationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    pred_masks: Optional[torch.FloatTensor] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
class SegGptPatchEmbeddings(nn.Module):
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
        if height != self.image_size[0] or width != self.image_size[1]: raise ValueError(f"Input image size ({height}*{width}) doesn't match model ({self.image_size[0]}*{self.image_size[1]}).")
        embeddings = self.projection(pixel_values).permute(0, 2, 3, 1)
        return embeddings
class SegGptEmbeddings(nn.Module):
    def __init__(self, config: SegGptConfig) -> None:
        super().__init__()
        self.mask_token = nn.Parameter(torch.zeros(1, 1, 1, config.hidden_size))
        self.segment_token_input = nn.Parameter(torch.zeros(1, 1, 1, config.hidden_size))
        self.segment_token_prompt = nn.Parameter(torch.zeros(1, 1, 1, config.hidden_size))
        self.type_token_semantic = nn.Parameter(torch.zeros(1, 1, 1, config.hidden_size))
        self.type_token_instance = nn.Parameter(torch.zeros(1, 1, 1, config.hidden_size))
        self.patch_embeddings = SegGptPatchEmbeddings(config)
        num_positions = (config.pretrain_image_size // config.patch_size) ** 2 + 1
        self.position_embeddings = nn.Parameter(torch.randn(1, num_positions, config.hidden_size))
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def interpolate_pos_encoding(self, height: int, width: int) -> torch.Tensor:
        patch_pos_embed = self.position_embeddings[:, 1:]
        num_patches = patch_pos_embed.shape[1]
        pretrain_patch_size = torch_int(num_patches**0.5)
        if torch.jit.is_tracing() or pretrain_patch_size != height or pretrain_patch_size != width:
            patch_pos_embed = F.interpolate(patch_pos_embed.reshape(1, pretrain_patch_size, pretrain_patch_size, -1).permute(0, 3, 1, 2), size=(height, width), mode="bicubic", align_corners=False)
            return patch_pos_embed.permute(0, 2, 3, 1)
        else: return patch_pos_embed.reshape(1, height, width, -1)
    def forward(self, pixel_values: torch.Tensor, prompt_pixel_values: torch.Tensor, bool_masked_pos: Optional[torch.BoolTensor] = None, embedding_type: Optional[str] = None) -> torch.Tensor:
        input_embeddings = self.patch_embeddings(pixel_values)
        prompt_embeddings = self.patch_embeddings(prompt_pixel_values)
        batch_size, patch_height, patch_width, _ = input_embeddings.shape
        mask_token = self.mask_token.expand(batch_size, patch_height, patch_width, -1)
        w = bool_masked_pos.unsqueeze(-1).type_as(mask_token).reshape(-1, patch_height, patch_width, 1)
        prompt_embeddings = prompt_embeddings * (1 - w) + mask_token * w
        embedding_type = embedding_type if embedding_type is not None else "instance"
        pos_embed = self.interpolate_pos_encoding(patch_height, patch_width)
        input_embeddings = input_embeddings + self.segment_token_input
        prompt_embeddings = prompt_embeddings + self.segment_token_prompt
        input_embeddings = input_embeddings + pos_embed
        prompt_embeddings = prompt_embeddings + pos_embed
        if embedding_type == "semantic": type_embedding = self.type_token_semantic
        elif embedding_type == "instance": type_embedding = self.type_token_instance
        else: raise ValueError(f"Embedding type should be either 'semantic' or 'instance', but got {embedding_type}")
        input_embeddings = input_embeddings + type_embedding
        prompt_embeddings = prompt_embeddings + type_embedding
        embeddings = torch.cat((input_embeddings, prompt_embeddings), dim=0)
        return embeddings
class SegGptAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        image_size, patch_size = config.image_size, config.patch_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        input_size = (image_size[0] // config.patch_size, image_size[1] // config.patch_size)
        head_dim = config.hidden_size // config.num_attention_heads
        self.num_attention_heads = config.num_attention_heads
        self.scale = head_dim**-0.5
        self.qkv = nn.Linear(config.hidden_size, config.hidden_size * 3, bias=config.qkv_bias)
        self.proj = nn.Linear(config.hidden_size, config.hidden_size)
        self.use_relative_position_embeddings = config.use_relative_position_embeddings
        if self.use_relative_position_embeddings:
            if input_size is None: raise ValueError("Input size must be provided if using relative positional encoding.")
            self.rel_pos_h = nn.Parameter(torch.zeros(2 * input_size[0] - 1, head_dim))
            self.rel_pos_w = nn.Parameter(torch.zeros(2 * input_size[1] - 1, head_dim))
    def get_rel_pos(self, q_size: int, k_size: int, rel_pos: torch.Tensor) -> torch.Tensor:
        max_rel_dist = int(2 * max(q_size, k_size) - 1)
        rel_pos_resized = F.interpolate(rel_pos.reshape(1, rel_pos.shape[0], -1).permute(0, 2, 1), size=max_rel_dist, mode="linear")
        rel_pos_resized = rel_pos_resized.reshape(-1, max_rel_dist).permute(1, 0)
        q_coords = torch.arange(q_size)[:, None] * max(k_size / q_size, 1.0)
        k_coords = torch.arange(k_size)[None, :] * max(q_size / k_size, 1.0)
        relative_coords = (q_coords - k_coords) + (k_size - 1) * max(q_size / k_size, 1.0)
        return rel_pos_resized[relative_coords.long()]
    def add_decomposed_rel_pos(self, attn: torch.Tensor, query: torch.Tensor, rel_pos_h: torch.Tensor, rel_pos_w: torch.Tensor, q_size: Tuple[int, int], k_size: Tuple[int, int]) -> torch.Tensor:
        query_height, query_width = q_size
        key_height, key_width = k_size
        relative_position_height = self.get_rel_pos(query_height, key_height, rel_pos_h)
        relative_position_width = self.get_rel_pos(query_width, key_width, rel_pos_w)
        batch_size, _, dim = query.shape
        reshaped_query = query.reshape(batch_size, query_height, query_width, dim)
        rel_h = torch.einsum("bhwc,hkc->bhwk", reshaped_query, relative_position_height)
        rel_w = torch.einsum("bhwc,wkc->bhwk", reshaped_query, relative_position_width)
        attn = attn.reshape(batch_size, query_height, query_width, key_height, key_width)
        attn = attn + rel_h[:, :, :, :, None] + rel_w[:, :, :, None, :]
        attn = attn.reshape(batch_size, query_height * query_width, key_height * key_width)
        return attn
    def forward(self, hidden_states: torch.Tensor, output_attentions=False) -> torch.Tensor:
        batch_size, height, width, _ = hidden_states.shape
        qkv = (self.qkv(hidden_states).reshape(batch_size, height * width, 3, self.num_attention_heads, -1).permute(2, 0, 3, 1, 4))
        query, key, value = qkv.reshape(3, batch_size * self.num_attention_heads, height * width, -1).unbind(0)
        attn_weights = (query * self.scale) @ key.transpose(-2, -1)
        if self.use_relative_position_embeddings: attn_weights = self.add_decomposed_rel_pos(attn_weights, query, self.rel_pos_h, self.rel_pos_w, (height, width), (height, width))
        attn_weights = torch.nn.functional.softmax(attn_weights, dtype=torch.float32, dim=-1).to(query.dtype)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(batch_size, self.num_attention_heads, height * width, -1)
            attn_weights = attn_weights_reshaped.view(batch_size * self.num_attention_heads, height * width, -1)
        else: attn_weights_reshaped = None
        attn_output = (attn_weights @ value).reshape(batch_size, self.num_attention_heads, height, width, -1)
        attn_output = attn_output.permute(0, 2, 3, 1, 4).reshape(batch_size, height, width, -1)
        attn_output = self.proj(attn_output)
        return (attn_output, attn_weights_reshaped)
class SegGptMlp(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.lin1 = nn.Linear(config.hidden_size, config.mlp_dim)
        self.lin2 = nn.Linear(config.mlp_dim, config.hidden_size)
        self.act = ACT2FN[config.hidden_act]
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.lin1(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.lin2(hidden_states)
        return hidden_states
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class SegGptDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class SegGptLayer(nn.Module):
    def __init__(self, config: SegGptConfig, drop_path_rate: float) -> None:
        super().__init__()
        self.attention = SegGptAttention(config)
        self.mlp = SegGptMlp(config)
        self.drop_path = SegGptDropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()
        self.layernorm_before = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.layernorm_after = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, ensemble_cond: int, feature_ensemble: bool = False, output_attentions: bool = False) -> Union[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor]]:
        self_attention_outputs = self.attention(self.layernorm_before(hidden_states), output_attentions=output_attentions)
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        if feature_ensemble and attention_output.shape[0] // 2 >= ensemble_cond:
            prompt, inputs = attention_output.split(attention_output.shape[1] // 2, dim=1)
            if ensemble_cond == 2:
                num_prompts = attention_output.shape[0] // 2
                inputs = inputs.reshape(2, num_prompts, -1)
                inputs = inputs.mean(dim=1, keepdim=True).expand_as(inputs)
                inputs = inputs.reshape(*prompt.shape)
            else: inputs = inputs.mean(dim=0, keepdim=True).expand_as(inputs)
            attention_output = torch.cat([prompt, inputs], dim=1)
        hidden_states = self.drop_path(attention_output) + hidden_states
        residual = hidden_states
        hidden_states = self.layernorm_after(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + self.drop_path(hidden_states)
        outputs = (hidden_states,) + outputs
        return outputs
class SegGptEncoder(nn.Module):
    def __init__(self, config: SegGptConfig) -> None:
        super().__init__()
        self.config = config
        dpr = [x.item() for x in torch.linspace(0, config.drop_path_rate, config.num_hidden_layers)]
        self.layers = nn.ModuleList([SegGptLayer(config, dpr[i]) for i in range(config.num_hidden_layers)])
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, feature_ensemble: bool = False, output_attentions: bool = False, output_hidden_states: bool = False, return_dict: bool = True) -> Union[tuple, SegGptEncoderOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        intermediate_hidden_states = []
        for i, layer_module in enumerate(self.layers):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            ensemble_cond = 2 if self.config.merge_index > i else 1
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states,
            ensemble_cond, feature_ensemble, output_attentions)
            else: layer_outputs = layer_module(hidden_states, ensemble_cond, feature_ensemble, output_attentions)
            hidden_states = layer_outputs[0]
            if i == self.config.merge_index: hidden_states = (hidden_states[: hidden_states.shape[0] // 2] + hidden_states[hidden_states.shape[0] // 2 :]) * 0.5
            if i in self.config.intermediate_hidden_state_indices: intermediate_hidden_states.append(self.layernorm(hidden_states))
            if output_attentions: all_self_attentions = all_self_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions, intermediate_hidden_states] if v is not None)
        return SegGptEncoderOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attentions, intermediate_hidden_states=intermediate_hidden_states)
class SegGptLayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-6, data_format="channels_last"):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.data_format = data_format
        if self.data_format not in ["channels_last", "channels_first"]: raise NotImplementedError(f"Unsupported data format: {self.data_format}")
        self.normalized_shape = (normalized_shape,)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.data_format == "channels_last": x = torch.nn.functional.layer_norm(x, self.normalized_shape, self.weight, self.bias, self.eps)
        elif self.data_format == "channels_first":
            input_dtype = x.dtype
            x = x.float()
            u = x.mean(1, keepdim=True)
            s = (x - u).pow(2).mean(1, keepdim=True)
            x = (x - u) / torch.sqrt(s + self.eps)
            x = x.to(dtype=input_dtype)
            x = self.weight[:, None, None] * x + self.bias[:, None, None]
        return x
class SegGptDecoderHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.conv = nn.Conv2d(config.decoder_hidden_size, config.decoder_hidden_size, kernel_size=3, padding=1)
        self.layernorm = SegGptLayerNorm(normalized_shape=config.decoder_hidden_size, eps=config.layer_norm_eps, data_format="channels_first")
        self.act_fct = ACT2FN[config.hidden_act]
        self.head = nn.Conv2d(config.decoder_hidden_size, 3, kernel_size=1, bias=True)
    def forward(self, hidden_states: torch.FloatTensor):
        hidden_states = self.conv(hidden_states)
        hidden_states = self.layernorm(hidden_states)
        hidden_states = self.act_fct(hidden_states)
        hidden_states = self.head(hidden_states)
        return hidden_states
class SegGptDecoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.decoder_embed = nn.Linear(config.hidden_size * len(config.intermediate_hidden_state_indices), config.patch_size**2 * config.decoder_hidden_size, bias=True)
        self.decoder_pred = SegGptDecoderHead(config)
        self.patch_size = config.patch_size
        self.decoder_hidden_size = config.decoder_hidden_size
        self.config = config
    def _reshape_hidden_states(self, hidden_states: torch.FloatTensor) -> torch.FloatTensor:
        batch_size, patch_height, patch_width, _ = hidden_states.shape
        hidden_states = hidden_states.reshape(batch_size, patch_height, patch_width, self.patch_size, self.patch_size, self.decoder_hidden_size)
        hidden_states = hidden_states.permute(0, 5, 1, 3, 2, 4)
        hidden_states = hidden_states.reshape(shape=(batch_size, -1, patch_height * self.patch_size, patch_width * self.patch_size))
        return hidden_states
    def forward(self, hidden_states: torch.FloatTensor):
        hidden_states = self.decoder_embed(hidden_states)
        hidden_states = self._reshape_hidden_states(hidden_states)
        hidden_states = self.decoder_pred(hidden_states)
        return hidden_states
class SegGptPreTrainedModel(PreTrainedModel):
    config_class = SegGptConfig
    base_model_prefix = "model"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = ["SegGptEmbeddings", "SegGptLayer"]
    def _init_weights(self, module: Union[nn.Linear, nn.Conv2d, nn.LayerNorm]) -> None:
        std = self.config.initializer_range
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data = nn.init.trunc_normal_(module.weight.data.to(torch.float32), mean=0.0, std=std).to(module.weight.dtype)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, SegGptAttention):
            module.rel_pos_h.data = nn.init.trunc_normal_(module.rel_pos_h.data.to(torch.float32), mean=0.0, std=std).to(module.rel_pos_h.dtype)
            module.rel_pos_w.data = nn.init.trunc_normal_(module.rel_pos_w.data.to(torch.float32), mean=0.0, std=std).to(module.rel_pos_w.dtype)
        elif isinstance(module, SegGptEmbeddings):
            module.position_embeddings.data = nn.init.trunc_normal_(module.position_embeddings.data.to(torch.float32), mean=0.0, std=std).to(module.position_embeddings.dtype)
            torch.nn.init.normal_(module.mask_token, std=std)
            torch.nn.init.normal_(module.segment_token_input, std=std)
            torch.nn.init.normal_(module.segment_token_prompt, std=std)
            torch.nn.init.normal_(module.type_token_semantic, std=std)
            torch.nn.init.normal_(module.type_token_instance, std=std)
SEGGPT_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`SegGptConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
SEGGPT_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See [`SegGptImageProcessor.__call__`]
            for details.
        prompt_pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Prompt pixel values. Prompt pixel values can be obtained using [`AutoImageProcessor`]. See
            [`SegGptImageProcessor.__call__`] for details.
        prompt_masks (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Prompt mask. Prompt mask can be obtained using [`AutoImageProcessor`]. See [`SegGptImageProcessor.__call__`] for
            details.
        bool_masked_pos (`torch.BoolTensor` of shape `(batch_size, num_patches)`, *optional*):
            Boolean masked positions. Indicates which patches are masked (1) and which aren't (0).
        feature_ensemble (`bool`, *optional*):
            Boolean indicating whether to use feature ensemble or not. If `True`, the model will use feature ensemble
            if we have at least two prompts. If `False`, the model will not use feature ensemble. This argument should
            be considered when doing few-shot inference on an input image i.e. more than one prompt for the same image.
        embedding_type (`str`, *optional*):
            Embedding type. Indicates whether the prompt is a semantic or instance embedding. Can be either
            instance or semantic.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare SegGpt Model transformer outputting raw hidden-states without any specific head on top.", SEGGPT_START_DOCSTRING)
class SegGptModel(SegGptPreTrainedModel):
    def __init__(self, config: SegGptConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = SegGptEmbeddings(config)
        self.encoder = SegGptEncoder(config)
        self.post_init()
    def get_input_embeddings(self) -> SegGptPatchEmbeddings: return self.embeddings.patch_embeddings
    def _prune_heads(self, heads_to_prune: Dict[int, List[int]]) -> None:
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(SEGGPT_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, prompt_pixel_values: torch.Tensor, prompt_masks: torch.Tensor, bool_masked_pos: Optional[torch.BoolTensor] = None,
    feature_ensemble: Optional[bool] = None, embedding_type: Optional[str] = None, labels: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, SegGptEncoderOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        feature_ensemble = feature_ensemble if feature_ensemble is not None else False
        expected_dtype = self.embeddings.patch_embeddings.projection.weight.dtype
        pixel_values = pixel_values.to(expected_dtype)
        prompt_pixel_values = prompt_pixel_values.to(expected_dtype)
        pixel_values = torch.cat((prompt_pixel_values, pixel_values), dim=2)
        prompt_pixel_values = (torch.cat((prompt_masks, prompt_masks), dim=2) if labels is None else torch.cat((prompt_masks, labels), dim=2))
        if bool_masked_pos is None and labels is not None: logger.warning_once("Labels were provided, but bool_masked_pos were not. It will be set to default value. If you're training the model, make sure to provide a bool_masked_pos.")
        if bool_masked_pos is None:
            num_patches = self.embeddings.patch_embeddings.num_patches
            bool_masked_pos = torch.zeros(num_patches, dtype=torch.bool).to(pixel_values.device)
            bool_masked_pos[num_patches // 2 :] = 1
            bool_masked_pos = bool_masked_pos.unsqueeze(0)
        embedding_output = self.embeddings(pixel_values, prompt_pixel_values, embedding_type=embedding_type, bool_masked_pos=bool_masked_pos)
        encoder_outputs = self.encoder(embedding_output, feature_ensemble=feature_ensemble, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        return encoder_outputs
def patchify(tensor: torch.Tensor, patch_size: int) -> torch.Tensor:
    batch_size, num_channels, height, width = tensor.shape
    patch_height = height // patch_size
    patch_width = width // patch_size
    tensor = tensor.reshape(shape=(batch_size, num_channels, patch_height, patch_size, patch_width, patch_size))
    tensor = tensor.permute(0, 2, 4, 3, 5, 1)
    tensor = tensor.reshape(shape=(batch_size, patch_height * patch_width, patch_size**2 * 3))
    return tensor
def unpatchify(tensor: torch.Tensor, patch_height: int, patch_width: int) -> torch.Tensor:
    batch_size = tensor.shape[0]
    patch_size = int((tensor.shape[-1] / 3) ** 0.5)
    if patch_height * patch_width != tensor.shape[1]: raise ValueError(f"Number of patches {tensor.shape[1]} does not match patch height ({patch_height}) and width ({patch_width}).")
    tensor = tensor.reshape(shape=(batch_size, patch_height, patch_width, patch_size, patch_size, 3))
    tensor = tensor.permute(0, 5, 1, 3, 2, 4)
    tensor = tensor.reshape(shape=(batch_size, 3, patch_height * patch_size, patch_width * patch_size))
    return tensor
class SegGptLoss(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.beta = config.beta
        self.patch_size = config.patch_size
    def forward(self, prompt_masks: torch.FloatTensor, pred_masks: torch.FloatTensor, labels: torch.FloatTensor, bool_masked_pos: torch.BoolTensor):
        ground_truth = torch.cat((prompt_masks, labels), dim=2)
        mask = bool_masked_pos[:, :, None].repeat(1, 1, self.patch_size**2 * 3)
        mask = unpatchify(mask, ground_truth.shape[2] // self.patch_size, ground_truth.shape[3] // self.patch_size)
        loss = F.smooth_l1_loss(pred_masks, ground_truth, reduction="none", beta=self.beta)
        loss = (loss * mask).sum() / mask.sum()
        return loss
@add_start_docstrings("SegGpt model with a decoder on top for one-shot image segmentation.", SEGGPT_START_DOCSTRING)
class SegGptForImageSegmentation(SegGptPreTrainedModel):
    def __init__(self, config: SegGptConfig):
        super().__init__(config)
        self.config = config
        self.model = SegGptModel(config)
        self.decoder = SegGptDecoder(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(SEGGPT_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, prompt_pixel_values: torch.Tensor, prompt_masks: torch.Tensor, bool_masked_pos: Optional[torch.BoolTensor] = None,
    feature_ensemble: Optional[bool] = None, embedding_type: Optional[str] = None, labels: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, SegGptImageSegmentationOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if bool_masked_pos is None:
            num_patches = self.model.embeddings.patch_embeddings.num_patches
            bool_masked_pos = torch.zeros(num_patches, dtype=torch.bool).to(pixel_values.device)
            bool_masked_pos[num_patches // 2 :] = 1
            bool_masked_pos = bool_masked_pos.unsqueeze(0)
        outputs = self.model(pixel_values=pixel_values, prompt_pixel_values=prompt_pixel_values, prompt_masks=prompt_masks, bool_masked_pos=bool_masked_pos,
        feature_ensemble=feature_ensemble, embedding_type=embedding_type, labels=labels, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        intermediate_hidden_states = outputs.intermediate_hidden_states if return_dict else outputs[-1]
        intermediate_hidden_states = torch.cat(intermediate_hidden_states, dim=-1)
        pred_masks = self.decoder(intermediate_hidden_states)
        loss = None
        if labels is not None:
            loss_fn = SegGptLoss(self.config)
            loss = loss_fn(prompt_masks, pred_masks, labels, bool_masked_pos)
        if not return_dict:
            output = (pred_masks,)
            if output_hidden_states: output = output + (outputs[1],)
            if output_attentions:
                idx = 2 if output_hidden_states else 1
                output = output + (outputs[idx],)
            if loss is not None: output = (loss,) + output
            return output
        return SegGptImageSegmentationOutput(loss=loss, pred_masks=pred_masks, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
