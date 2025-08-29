"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...file_utils import (add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings)
from ...modeling_outputs import DepthEstimatorOutput
from ...modeling_utils import PreTrainedModel
from ...utils import logging
from ...utils.backbone_utils import load_backbone
from .configuration_depth_anything import DepthAnythingConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "DepthAnythingConfig"
DEPTH_ANYTHING_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`DepthAnythingConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
DEPTH_ANYTHING_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See [`DPTImageProcessor.__call__`]
            for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
class DepthAnythingReassembleLayer(nn.Module):
    def __init__(self, config, channels, factor):
        super().__init__()
        self.projection = nn.Conv2d(in_channels=config.reassemble_hidden_size, out_channels=channels, kernel_size=1)
        if factor > 1: self.resize = nn.ConvTranspose2d(channels, channels, kernel_size=factor, stride=factor, padding=0)
        elif factor == 1: self.resize = nn.Identity()
        elif factor < 1: self.resize = nn.Conv2d(channels, channels, kernel_size=3, stride=int(1 / factor), padding=1)
    def forward(self, hidden_state):
        hidden_state = self.projection(hidden_state)
        hidden_state = self.resize(hidden_state)
        return hidden_state
class DepthAnythingReassembleStage(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList()
        for channels, factor in zip(config.neck_hidden_sizes, config.reassemble_factors): self.layers.append(DepthAnythingReassembleLayer(config, channels=channels, factor=factor))
    def forward(self, hidden_states: List[torch.Tensor], patch_height=None, patch_width=None) -> List[torch.Tensor]:
        out = []
        for i, hidden_state in enumerate(hidden_states):
            hidden_state = hidden_state[:, 1:]
            batch_size, _, num_channels = hidden_state.shape
            hidden_state = hidden_state.reshape(batch_size, patch_height, patch_width, num_channels)
            hidden_state = hidden_state.permute(0, 3, 1, 2).contiguous()
            hidden_state = self.layers[i](hidden_state)
            out.append(hidden_state)
        return out
class DepthAnythingPreActResidualLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.activation1 = nn.ReLU()
        self.convolution1 = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=3, stride=1, padding=1, bias=True)
        self.activation2 = nn.ReLU()
        self.convolution2 = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=3, stride=1, padding=1, bias=True)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        residual = hidden_state
        hidden_state = self.activation1(hidden_state)
        hidden_state = self.convolution1(hidden_state)
        hidden_state = self.activation2(hidden_state)
        hidden_state = self.convolution2(hidden_state)
        return hidden_state + residual
class DepthAnythingFeatureFusionLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.projection = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=1, bias=True)
        self.residual_layer1 = DepthAnythingPreActResidualLayer(config)
        self.residual_layer2 = DepthAnythingPreActResidualLayer(config)
    def forward(self, hidden_state, residual=None, size=None):
        if residual is not None:
            if hidden_state.shape != residual.shape: residual = nn.functional.interpolate(residual, size=(hidden_state.shape[2], hidden_state.shape[3]), mode="bilinear", align_corners=False)
            hidden_state = hidden_state + self.residual_layer1(residual)
        hidden_state = self.residual_layer2(hidden_state)
        modifier = {"scale_factor": 2} if size is None else {"size": size}
        hidden_state = nn.functional.interpolate(hidden_state, **modifier, mode="bilinear", align_corners=True)
        hidden_state = self.projection(hidden_state)
        return hidden_state
class DepthAnythingFeatureFusionStage(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layers = nn.ModuleList()
        for _ in range(len(config.neck_hidden_sizes)): self.layers.append(DepthAnythingFeatureFusionLayer(config))
    def forward(self, hidden_states, size=None):
        hidden_states = hidden_states[::-1]
        fused_hidden_states = []
        size = hidden_states[1].shape[2:]
        fused_hidden_state = self.layers[0](hidden_states[0], size=size)
        fused_hidden_states.append(fused_hidden_state)
        for idx, (hidden_state, layer) in enumerate(zip(hidden_states[1:], self.layers[1:])):
            size = hidden_states[1:][idx + 1].shape[2:] if idx != (len(hidden_states[1:]) - 1) else None
            fused_hidden_state = layer(fused_hidden_state, hidden_state, size=size)
            fused_hidden_states.append(fused_hidden_state)
        return fused_hidden_states
class DepthAnythingPreTrainedModel(PreTrainedModel):
    config_class = DepthAnythingConfig
    base_model_prefix = "depth_anything"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
class DepthAnythingNeck(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.reassemble_stage = DepthAnythingReassembleStage(config)
        self.convs = nn.ModuleList()
        for channel in config.neck_hidden_sizes: self.convs.append(nn.Conv2d(channel, config.fusion_hidden_size, kernel_size=3, padding=1, bias=False))
        self.fusion_stage = DepthAnythingFeatureFusionStage(config)
    def forward(self, hidden_states: List[torch.Tensor], patch_height=None, patch_width=None) -> List[torch.Tensor]:
        if not isinstance(hidden_states, (tuple, list)): raise TypeError("hidden_states should be a tuple or list of tensors")
        if len(hidden_states) != len(self.config.neck_hidden_sizes): raise ValueError("The number of hidden states should be equal to the number of neck hidden sizes.")
        hidden_states = self.reassemble_stage(hidden_states, patch_height, patch_width)
        features = [self.convs[i](feature) for i, feature in enumerate(hidden_states)]
        output = self.fusion_stage(features)
        return output
class DepthAnythingDepthEstimationHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.head_in_index = config.head_in_index
        self.patch_size = config.patch_size
        features = config.fusion_hidden_size
        self.conv1 = nn.Conv2d(features, features // 2, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(features // 2, config.head_hidden_size, kernel_size=3, stride=1, padding=1)
        self.activation1 = nn.ReLU()
        self.conv3 = nn.Conv2d(config.head_hidden_size, 1, kernel_size=1, stride=1, padding=0)
        if config.depth_estimation_type == "relative": self.activation2 = nn.ReLU()
        elif config.depth_estimation_type == "metric": self.activation2 = nn.Sigmoid()
        else: raise ValueError(f"Unknown depth estimation type: {config.depth_estimation_type}")
        self.max_depth = config.max_depth
    def forward(self, hidden_states: List[torch.Tensor], patch_height, patch_width) -> torch.Tensor:
        hidden_states = hidden_states[self.head_in_index]
        predicted_depth = self.conv1(hidden_states)
        predicted_depth = nn.functional.interpolate(predicted_depth, (int(patch_height * self.patch_size), int(patch_width * self.patch_size)), mode="bilinear", align_corners=True)
        predicted_depth = self.conv2(predicted_depth)
        predicted_depth = self.activation1(predicted_depth)
        predicted_depth = self.conv3(predicted_depth)
        predicted_depth = self.activation2(predicted_depth) * self.max_depth
        predicted_depth = predicted_depth.squeeze(dim=1)
        return predicted_depth
@add_start_docstrings("Depth Anything Model with a depth estimation head on top (consisting of 3 convolutional layers) e.g. for KITTI, NYUv2.", DEPTH_ANYTHING_START_DOCSTRING)
class DepthAnythingForDepthEstimation(DepthAnythingPreTrainedModel):
    _no_split_modules = ["DPTViTEmbeddings"]
    def __init__(self, config):
        super().__init__(config)
        self.backbone = load_backbone(config)
        self.neck = DepthAnythingNeck(config)
        self.head = DepthAnythingDepthEstimationHead(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(DEPTH_ANYTHING_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, labels: Optional[torch.LongTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.Tensor], DepthEstimatorOutput]:
        loss = None
        if labels is not None: raise NotImplementedError("Training is not implemented yet")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        outputs = self.backbone.forward_with_filtered_kwargs(pixel_values, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        hidden_states = outputs.feature_maps
        _, _, height, width = pixel_values.shape
        patch_size = self.config.patch_size
        patch_height = height // patch_size
        patch_width = width // patch_size
        hidden_states = self.neck(hidden_states, patch_height, patch_width)
        predicted_depth = self.head(hidden_states, patch_height, patch_width)
        if not return_dict:
            if output_hidden_states: output = (predicted_depth,) + outputs[1:]
            else: output = (predicted_depth,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return DepthEstimatorOutput(loss=loss, predicted_depth=predicted_depth, hidden_states=outputs.hidden_states if output_hidden_states else None, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
