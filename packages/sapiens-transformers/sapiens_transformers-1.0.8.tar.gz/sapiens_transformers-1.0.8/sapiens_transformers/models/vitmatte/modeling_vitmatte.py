"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import torch
from torch import nn
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings)
from ...utils.backbone_utils import load_backbone
from .configuration_vitmatte import VitMatteConfig
_CONFIG_FOR_DOC = "VitMatteConfig"
@dataclass
class ImageMattingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    alphas: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
class VitMattePreTrainedModel(PreTrainedModel):
    config_class = VitMatteConfig
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = []
    def _init_weights(self, module):
        if isinstance(module, nn.Conv2d):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
class VitMatteBasicConv3x3(nn.Module):
    def __init__(self, config, in_channels, out_channels, stride=2, padding=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=3, stride=stride, padding=padding, bias=False)
        self.batch_norm = nn.BatchNorm2d(out_channels, eps=config.batch_norm_eps)
        self.relu = nn.ReLU()
    def forward(self, hidden_state):
        hidden_state = self.conv(hidden_state)
        hidden_state = self.batch_norm(hidden_state)
        hidden_state = self.relu(hidden_state)
        return hidden_state
class VitMatteConvStream(nn.Module):
    def __init__(self, config):
        super().__init__()
        in_channels = 4
        if config.backbone_config is not None: in_channels = config.backbone_config.num_channels
        out_channels = config.convstream_hidden_sizes
        self.convs = nn.ModuleList()
        self.conv_chans = [in_channels] + out_channels
        for i in range(len(self.conv_chans) - 1):
            in_chan_ = self.conv_chans[i]
            out_chan_ = self.conv_chans[i + 1]
            self.convs.append(VitMatteBasicConv3x3(config, in_chan_, out_chan_))
    def forward(self, pixel_values):
        out_dict = {"detailed_feature_map_0": pixel_values}
        embeddings = pixel_values
        for i in range(len(self.convs)):
            embeddings = self.convs[i](embeddings)
            name_ = "detailed_feature_map_" + str(i + 1)
            out_dict[name_] = embeddings
        return out_dict
class VitMatteFusionBlock(nn.Module):
    def __init__(self, config, in_channels, out_channels):
        super().__init__()
        self.conv = VitMatteBasicConv3x3(config, in_channels, out_channels, stride=1, padding=1)
    def forward(self, features, detailed_feature_map):
        upscaled_features = nn.functional.interpolate(features, scale_factor=2, mode="bilinear", align_corners=False)
        out = torch.cat([detailed_feature_map, upscaled_features], dim=1)
        out = self.conv(out)
        return out
class VitMatteHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        in_channels = config.fusion_hidden_sizes[-1]
        mid_channels = 16
        self.matting_convs = nn.Sequential(nn.Conv2d(in_channels, mid_channels, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(mid_channels), nn.ReLU(True),
        nn.Conv2d(mid_channels, 1, kernel_size=1, stride=1, padding=0))
    def forward(self, hidden_state):
        hidden_state = self.matting_convs(hidden_state)
        return hidden_state
class VitMatteDetailCaptureModule(nn.Module):
    def __init__(self, config):
        super().__init__()
        if len(config.fusion_hidden_sizes) != len(config.convstream_hidden_sizes) + 1: raise ValueError("The length of fusion_hidden_sizes should be equal to the length of convstream_hidden_sizes + 1.")
        self.config = config
        self.convstream = VitMatteConvStream(config)
        self.conv_chans = self.convstream.conv_chans
        self.fusion_blocks = nn.ModuleList()
        self.fusion_channels = [config.hidden_size] + config.fusion_hidden_sizes
        for i in range(len(self.fusion_channels) - 1): self.fusion_blocks.append(VitMatteFusionBlock(config=config, in_channels=self.fusion_channels[i] + self.conv_chans[-(i + 1)], out_channels=self.fusion_channels[i + 1]))
        self.matting_head = VitMatteHead(config)
    def forward(self, features, pixel_values):
        detail_features = self.convstream(pixel_values)
        for i in range(len(self.fusion_blocks)):
            detailed_feature_map_name = "detailed_feature_map_" + str(len(self.fusion_blocks) - i - 1)
            features = self.fusion_blocks[i](features, detail_features[detailed_feature_map_name])
        alphas = torch.sigmoid(self.matting_head(features))
        return alphas
VITMATTE_START_DOCSTRING = r"""
    Parameters:
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) sub-class. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
        config ([`UperNetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
VITMATTE_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`VitMatteImageProcessor.__call__`] for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers in case the backbone has them. See
            `attentions` under returned tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers of the backbone. See `hidden_states` under
            returned tensors for more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("ViTMatte framework leveraging any vision backbone e.g. for ADE20k, CityScapes.", VITMATTE_START_DOCSTRING)
class VitMatteForImageMatting(VitMattePreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.backbone = load_backbone(config)
        self.decoder = VitMatteDetailCaptureModule(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(VITMATTE_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, pixel_values: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, labels: Optional[torch.Tensor] = None, return_dict: Optional[bool] = None):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        loss = None
        if labels is not None: raise NotImplementedError("Training is not yet supported")
        outputs = self.backbone.forward_with_filtered_kwargs(pixel_values, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        features = outputs.feature_maps[-1]
        alphas = self.decoder(features, pixel_values)
        if not return_dict:
            output = (alphas,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return ImageMattingOutput(loss=loss, alphas=alphas, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
