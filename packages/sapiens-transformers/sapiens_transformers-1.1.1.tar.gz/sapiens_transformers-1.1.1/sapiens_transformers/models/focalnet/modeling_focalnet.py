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
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ...activations import ACT2FN
from ...modeling_outputs import BackboneOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from ...utils.backbone_utils import BackboneMixin
from .configuration_focalnet import FocalNetConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "FocalNetConfig"
_CHECKPOINT_FOR_DOC = "microsoft/focalnet-tiny"
_EXPECTED_OUTPUT_SHAPE = [1, 49, 768]
_IMAGE_CLASS_CHECKPOINT = "microsoft/focalnet-tiny"
_IMAGE_CLASS_EXPECTED_OUTPUT = "tabby, tabby cat"
@dataclass
class FocalNetEncoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    reshaped_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class FocalNetModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    reshaped_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class FocalNetMaskedImageModelingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    reconstruction: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    reshaped_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class FocalNetImageClassifierOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    reshaped_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
class FocalNetEmbeddings(nn.Module):
    def __init__(self, config, use_mask_token=False):
        super().__init__()
        self.patch_embeddings = FocalNetPatchEmbeddings(config=config, image_size=config.image_size, patch_size=config.patch_size, num_channels=config.num_channels,
        embed_dim=config.embed_dim, use_conv_embed=config.use_conv_embed, is_stem=True)
        self.patch_grid = self.patch_embeddings.grid_size
        self.mask_token = nn.Parameter(torch.zeros(1, 1, config.embed_dim)) if use_mask_token else None
        self.norm = nn.LayerNorm(config.embed_dim, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, pixel_values: Optional[torch.FloatTensor], bool_masked_pos: Optional[torch.BoolTensor] = None) -> Tuple[torch.Tensor]:
        embeddings, output_dimensions = self.patch_embeddings(pixel_values)
        embeddings = self.norm(embeddings)
        batch_size, seq_len, _ = embeddings.size()
        if bool_masked_pos is not None:
            mask_tokens = self.mask_token.expand(batch_size, seq_len, -1)
            mask = bool_masked_pos.unsqueeze(-1).type_as(mask_tokens)
            embeddings = embeddings * (1.0 - mask) + mask_tokens * mask
        embeddings = self.dropout(embeddings)
        return embeddings, output_dimensions
class FocalNetPatchEmbeddings(nn.Module):
    def __init__(self, config, image_size, patch_size, num_channels, embed_dim, add_norm=False, use_conv_embed=False, is_stem=False):
        super().__init__()
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.grid_size = (image_size[0] // patch_size[0], image_size[1] // patch_size[1])
        if use_conv_embed:
            if is_stem:
                kernel_size = 7
                padding = 2
                stride = 4
            else:
                kernel_size = 3
                padding = 1
                stride = 2
            self.projection = nn.Conv2d(num_channels, embed_dim, kernel_size=kernel_size, stride=stride, padding=padding)
        else: self.projection = nn.Conv2d(num_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        if add_norm: self.norm = nn.LayerNorm(embed_dim, eps=config.layer_norm_eps)
        else: self.norm = None
    def maybe_pad(self, pixel_values, height, width):
        if width % self.patch_size[1] != 0:
            pad_values = (0, self.patch_size[1] - width % self.patch_size[1])
            pixel_values = nn.functional.pad(pixel_values, pad_values)
        if height % self.patch_size[0] != 0:
            pad_values = (0, 0, 0, self.patch_size[0] - height % self.patch_size[0])
            pixel_values = nn.functional.pad(pixel_values, pad_values)
        return pixel_values
    def forward(self, pixel_values: Optional[torch.FloatTensor]) -> Tuple[torch.Tensor, Tuple[int]]:
        _, num_channels, height, width = pixel_values.shape
        if num_channels != self.num_channels: raise ValueError("Make sure that the channel dimension of the pixel values match with the one set in the configuration.")
        pixel_values = self.maybe_pad(pixel_values, height, width)
        embeddings = self.projection(pixel_values)
        _, _, height, width = embeddings.shape
        output_dimensions = (height, width)
        embeddings = embeddings.flatten(2).transpose(1, 2)
        if self.norm is not None: embeddings = self.norm(embeddings)
        return embeddings, output_dimensions
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class FocalNetDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class FocalNetModulation(nn.Module):
    def __init__(self, config, index, dim, focal_factor=2, bias=True, projection_dropout=0.0):
        super().__init__()
        self.dim = dim
        self.focal_window = config.focal_windows[index]
        self.focal_level = config.focal_levels[index]
        self.focal_factor = focal_factor
        self.use_post_layernorm_in_modulation = config.use_post_layernorm_in_modulation
        self.normalize_modulator = config.normalize_modulator
        self.projection_in = nn.Linear(dim, 2 * dim + (self.focal_level + 1), bias=bias)
        self.projection_context = nn.Conv2d(dim, dim, kernel_size=1, stride=1, bias=bias)
        self.activation = nn.GELU()
        self.projection_out = nn.Linear(dim, dim)
        self.projection_dropout = nn.Dropout(projection_dropout)
        self.focal_layers = nn.ModuleList()
        self.kernel_sizes = []
        for k in range(self.focal_level):
            kernel_size = self.focal_factor * k + self.focal_window
            self.focal_layers.append(nn.Sequential(nn.Conv2d(dim, dim, kernel_size=kernel_size, stride=1, groups=dim, padding=kernel_size // 2, bias=False), nn.GELU()))
            self.kernel_sizes.append(kernel_size)
        if self.use_post_layernorm_in_modulation: self.layernorm = nn.LayerNorm(dim, eps=config.layer_norm_eps)
    def forward(self, hidden_state):
        num_channels = hidden_state.shape[-1]
        x = self.projection_in(hidden_state).permute(0, 3, 1, 2).contiguous()
        q, ctx, self.gates = torch.split(x, (num_channels, num_channels, self.focal_level + 1), 1)
        ctx_all = 0
        for level in range(self.focal_level):
            ctx = self.focal_layers[level](ctx)
            ctx_all = ctx_all + ctx * self.gates[:, level : level + 1]
        ctx_global = self.activation(ctx.mean(2, keepdim=True).mean(3, keepdim=True))
        ctx_all = ctx_all + ctx_global * self.gates[:, self.focal_level :]
        if self.normalize_modulator: ctx_all = ctx_all / (self.focal_level + 1)
        self.modulator = self.projection_context(ctx_all)
        x_out = q * self.modulator
        x_out = x_out.permute(0, 2, 3, 1).contiguous()
        if self.use_post_layernorm_in_modulation: x_out = self.layernorm(x_out)
        x_out = self.projection_out(x_out)
        x_out = self.projection_dropout(x_out)
        return x_out
class FocalNetMlp(nn.Module):
    def __init__(self, config, in_features, hidden_features=None, out_features=None, drop=0.0):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.activation = ACT2FN[config.hidden_act]
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(drop)
    def forward(self, hidden_state):
        hidden_state = self.fc1(hidden_state)
        hidden_state = self.activation(hidden_state)
        hidden_state = self.drop(hidden_state)
        hidden_state = self.fc2(hidden_state)
        hidden_state = self.drop(hidden_state)
        return hidden_state
class FocalNetLayer(nn.Module):
    def __init__(self, config, index, dim, input_resolution, drop_path=0.0):
        super().__init__()
        self.config = config
        self.dim = dim
        self.input_resolution = input_resolution
        self.drop = config.hidden_dropout_prob
        self.use_post_layernorm = config.use_post_layernorm
        self.norm1 = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        self.modulation = FocalNetModulation(config=config, index=index, dim=dim, projection_dropout=self.drop)
        self.drop_path = FocalNetDropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        self.norm2 = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        mlp_hidden_dim = int(dim * config.mlp_ratio)
        self.mlp = FocalNetMlp(config=config, in_features=dim, hidden_features=mlp_hidden_dim, drop=self.drop)
        self.gamma_1 = 1.0
        self.gamma_2 = 1.0
        if config.use_layerscale:
            self.gamma_1 = nn.Parameter(config.layerscale_value * torch.ones((dim)), requires_grad=True)
            self.gamma_2 = nn.Parameter(config.layerscale_value * torch.ones((dim)), requires_grad=True)
    def forward(self, hidden_state, input_dimensions):
        height, width = input_dimensions
        batch_size, _, num_channels = hidden_state.shape
        shortcut = hidden_state
        hidden_state = hidden_state if self.use_post_layernorm else self.norm1(hidden_state)
        hidden_state = hidden_state.view(batch_size, height, width, num_channels)
        hidden_state = self.modulation(hidden_state).view(batch_size, height * width, num_channels)
        hidden_state = hidden_state if not self.use_post_layernorm else self.norm1(hidden_state)
        hidden_state = shortcut + self.drop_path(self.gamma_1 * hidden_state)
        hidden_state = hidden_state + self.drop_path(self.gamma_2 * (self.norm2(self.mlp(hidden_state)) if self.use_post_layernorm else self.mlp(self.norm2(hidden_state))))
        return hidden_state
class FocalNetStage(nn.Module):
    def __init__(self, config, index, input_resolution):
        super().__init__()
        self.config = config
        self.num_stages = len(config.depths)
        embed_dim = [config.embed_dim * (2**i) for i in range(self.num_stages)]
        dim = embed_dim[index]
        out_dim = embed_dim[index + 1] if (index < self.num_stages - 1) else None
        downsample = FocalNetPatchEmbeddings if (index < self.num_stages - 1) else None
        dpr = [x.item() for x in torch.linspace(0, config.drop_path_rate, sum(config.depths))]
        drop_path = dpr[sum(config.depths[:index]) : sum(config.depths[: index + 1])]
        self.layers = nn.ModuleList([FocalNetLayer(config=config, index=index, dim=dim, input_resolution=input_resolution, drop_path=drop_path[i] if isinstance(drop_path, list) else drop_path) for i in range(config.depths[index])])
        if downsample is not None: self.downsample = downsample(config=config, image_size=input_resolution, patch_size=2, num_channels=dim, embed_dim=out_dim, add_norm=True, use_conv_embed=config.use_conv_embed, is_stem=False)
        else: self.downsample = None
        self.pointing = False
    def forward(self, hidden_states: torch.Tensor, input_dimensions: Tuple[int, int]) -> Tuple[torch.Tensor]:
        height, width = input_dimensions
        for layer_module in self.layers: hidden_states = layer_module(hidden_states, input_dimensions)
        hidden_states_before_downsampling = hidden_states
        if self.downsample is not None:
            height, width = input_dimensions
            hidden_states = hidden_states.transpose(1, 2).reshape(hidden_states_before_downsampling.shape[0], -1, height, width)
            hidden_states, output_dimensions = self.downsample(hidden_states)
        else: output_dimensions = (height, width, height, width)
        stage_outputs = (hidden_states, hidden_states_before_downsampling, output_dimensions)
        return stage_outputs
class FocalNetEncoder(nn.Module):
    def __init__(self, config, grid_size):
        super().__init__()
        self.num_stages = len(config.depths)
        self.config = config
        self.stages = nn.ModuleList([FocalNetStage(config=config, index=i_layer, input_resolution=(grid_size[0] // (2**i_layer), grid_size[1] // (2**i_layer))) for i_layer in range(self.num_stages)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states: torch.Tensor, input_dimensions: Tuple[int, int], output_hidden_states: Optional[bool] = False, output_hidden_states_before_downsampling: Optional[bool] = False, return_dict: Optional[bool] = True) -> Union[Tuple, FocalNetEncoderOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_reshaped_hidden_states = () if output_hidden_states else None
        if output_hidden_states:
            batch_size, _, hidden_size = hidden_states.shape
            reshaped_hidden_state = hidden_states.view(batch_size, *input_dimensions, hidden_size)
            reshaped_hidden_state = reshaped_hidden_state.permute(0, 3, 1, 2)
            all_hidden_states += (hidden_states,)
            all_reshaped_hidden_states += (reshaped_hidden_state,)
        for i, stage_module in enumerate(self.stages):
            if self.gradient_checkpointing and self.training: stage_outputs = self._gradient_checkpointing_func(stage_module.__call__, hidden_states, input_dimensions)
            else: stage_outputs = stage_module(hidden_states, input_dimensions)
            hidden_states = stage_outputs[0]
            hidden_states_before_downsampling = stage_outputs[1]
            output_dimensions = stage_outputs[2]
            input_dimensions = (output_dimensions[-2], output_dimensions[-1])
            if output_hidden_states and output_hidden_states_before_downsampling:
                batch_size, _, hidden_size = hidden_states_before_downsampling.shape
                reshaped_hidden_state = hidden_states_before_downsampling.view(batch_size, *(output_dimensions[0], output_dimensions[1]), hidden_size)
                reshaped_hidden_state = reshaped_hidden_state.permute(0, 3, 1, 2)
                all_hidden_states += (hidden_states_before_downsampling,)
                all_reshaped_hidden_states += (reshaped_hidden_state,)
            elif output_hidden_states and not output_hidden_states_before_downsampling:
                batch_size, _, hidden_size = hidden_states.shape
                reshaped_hidden_state = hidden_states.view(batch_size, *input_dimensions, hidden_size)
                reshaped_hidden_state = reshaped_hidden_state.permute(0, 3, 1, 2)
                all_hidden_states += (hidden_states,)
                all_reshaped_hidden_states += (reshaped_hidden_state,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states] if v is not None)
        return FocalNetEncoderOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, reshaped_hidden_states=all_reshaped_hidden_states)
class FocalNetPreTrainedModel(PreTrainedModel):
    config_class = FocalNetConfig
    base_model_prefix = "focalnet"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = ["FocalNetStage"]
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
FOCALNET_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) sub-class. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`FocalNetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
FOCALNET_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`AutoImageProcessor.__call__`] for details.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare FocalNet Model outputting raw hidden-states without any specific head on top.", FOCALNET_START_DOCSTRING)
class FocalNetModel(FocalNetPreTrainedModel):
    def __init__(self, config, add_pooling_layer=True, use_mask_token=False):
        super().__init__(config)
        self.config = config
        self.num_stages = len(config.depths)
        self.num_features = int(config.embed_dim * 2 ** (self.num_stages - 1))
        self.embeddings = FocalNetEmbeddings(config, use_mask_token=use_mask_token)
        self.encoder = FocalNetEncoder(config, self.embeddings.patch_grid)
        self.layernorm = nn.LayerNorm(self.num_features, eps=config.layer_norm_eps)
        self.pooler = nn.AdaptiveAvgPool1d(1) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.patch_embeddings
    @add_start_docstrings_to_model_forward(FOCALNET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, bool_masked_pos: Optional[torch.BoolTensor] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, FocalNetModelOutput]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        embedding_output, input_dimensions = self.embeddings(pixel_values, bool_masked_pos=bool_masked_pos)
        encoder_outputs = self.encoder(embedding_output, input_dimensions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = encoder_outputs[0]
        sequence_output = self.layernorm(sequence_output)
        pooled_output = None
        if self.pooler is not None:
            pooled_output = self.pooler(sequence_output.transpose(1, 2))
            pooled_output = torch.flatten(pooled_output, 1)
        if not return_dict:
            output = (sequence_output, pooled_output) + encoder_outputs[1:]
            return output
        return FocalNetModelOutput(last_hidden_state=sequence_output, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, reshaped_hidden_states=encoder_outputs.reshaped_hidden_states)
@add_start_docstrings("""FocalNet Model with a decoder on top for masked image modeling.
    This follows the same implementation as in [SimMIM](https://arxiv.org/abs/2111.09886).
    <Tip>
    Note that we provide a script to pre-train this model.
    </Tip>
    """, FOCALNET_START_DOCSTRING)
class FocalNetForMaskedImageModeling(FocalNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.focalnet = FocalNetModel(config, add_pooling_layer=False, use_mask_token=True)
        self.num_stages = len(config.depths)
        num_features = int(config.embed_dim * 2 ** (self.num_stages - 1))
        self.decoder = nn.Sequential(nn.Conv2d(in_channels=num_features, out_channels=config.encoder_stride**2 * config.num_channels, kernel_size=1), nn.PixelShuffle(config.encoder_stride))
        self.post_init()
    @add_start_docstrings_to_model_forward(FOCALNET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, bool_masked_pos: Optional[torch.BoolTensor] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, FocalNetMaskedImageModelingOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.focalnet(pixel_values, bool_masked_pos=bool_masked_pos, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        sequence_output = sequence_output.transpose(1, 2)
        batch_size, num_channels, sequence_length = sequence_output.shape
        height = width = math.floor(sequence_length**0.5)
        sequence_output = sequence_output.reshape(batch_size, num_channels, height, width)
        reconstructed_pixel_values = self.decoder(sequence_output)
        masked_im_loss = None
        if bool_masked_pos is not None:
            size = self.config.image_size // self.config.patch_size
            bool_masked_pos = bool_masked_pos.reshape(-1, size, size)
            mask = (bool_masked_pos.repeat_interleave(self.config.patch_size, 1).repeat_interleave(self.config.patch_size, 2).unsqueeze(1).contiguous())
            reconstruction_loss = nn.functional.l1_loss(pixel_values, reconstructed_pixel_values, reduction="none")
            masked_im_loss = (reconstruction_loss * mask).sum() / (mask.sum() + 1e-5) / self.config.num_channels
        if not return_dict:
            output = (reconstructed_pixel_values,) + outputs[2:]
            return ((masked_im_loss,) + output) if masked_im_loss is not None else output
        return FocalNetMaskedImageModelingOutput(loss=masked_im_loss, reconstruction=reconstructed_pixel_values, hidden_states=outputs.hidden_states, reshaped_hidden_states=outputs.reshaped_hidden_states)
@add_start_docstrings("FocalNet Model with an image classification head on top (a linear layer on top of the pooled output) e.g. for ImageNet.", FOCALNET_START_DOCSTRING)
class FocalNetForImageClassification(FocalNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.focalnet = FocalNetModel(config)
        self.classifier = (nn.Linear(self.focalnet.num_features, config.num_labels) if config.num_labels > 0 else nn.Identity())
        self.post_init()
    @add_start_docstrings_to_model_forward(FOCALNET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple, FocalNetImageClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.focalnet(pixel_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs[1]
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
        return FocalNetImageClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, reshaped_hidden_states=outputs.reshaped_hidden_states)
@add_start_docstrings("FocalNet backbone, to be used with frameworks like X-Decoder.", FOCALNET_START_DOCSTRING)
class FocalNetBackbone(FocalNetPreTrainedModel, BackboneMixin):
    def __init__(self, config: FocalNetConfig):
        super().__init__(config)
        super()._init_backbone(config)
        self.num_features = [config.embed_dim] + config.hidden_sizes
        self.focalnet = FocalNetModel(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(FOCALNET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.Tensor, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> BackboneOutput:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        outputs = self.focalnet(pixel_values, output_hidden_states=True, return_dict=True)
        hidden_states = outputs.reshaped_hidden_states
        feature_maps = ()
        for idx, stage in enumerate(self.stage_names):
            if stage in self.out_features: feature_maps += (hidden_states[idx],)
        if not return_dict:
            output = (feature_maps,)
            if output_hidden_states: output += (outputs.hidden_states,)
            return output
        return BackboneOutput(feature_maps=feature_maps, hidden_states=outputs.hidden_states if output_hidden_states else None, attentions=None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
