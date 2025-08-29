"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional, Tuple, Union
import torch
from torch import nn
from torch.nn import CrossEntropyLoss
from ...modeling_outputs import SemanticSegmenterOutput
from ...modeling_utils import PreTrainedModel
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings
from ...utils.backbone_utils import load_backbone
from .configuration_upernet import UperNetConfig
_CONFIG_FOR_DOC = "UperNetConfig"
class UperNetConvModule(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: Union[int, Tuple[int, int]], padding: Union[int, Tuple[int, int], str] = 0,
    bias: bool = False, dilation: Union[int, Tuple[int, int]] = 1) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, padding=padding, bias=bias, dilation=dilation)
        self.batch_norm = nn.BatchNorm2d(out_channels)
        self.activation = nn.ReLU()
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        output = self.conv(input)
        output = self.batch_norm(output)
        output = self.activation(output)
        return output
class UperNetPyramidPoolingBlock(nn.Module):
    def __init__(self, pool_scale: int, in_channels: int, channels: int) -> None:
        super().__init__()
        self.layers = [nn.AdaptiveAvgPool2d(pool_scale), UperNetConvModule(in_channels, channels, kernel_size=1)]
        for i, layer in enumerate(self.layers): self.add_module(str(i), layer)
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class UperNetPyramidPoolingModule(nn.Module):
    def __init__(self, pool_scales: Tuple[int, ...], in_channels: int, channels: int, align_corners: bool) -> None:
        super().__init__()
        self.pool_scales = pool_scales
        self.align_corners = align_corners
        self.in_channels = in_channels
        self.channels = channels
        self.blocks = []
        for i, pool_scale in enumerate(pool_scales):
            block = UperNetPyramidPoolingBlock(pool_scale=pool_scale, in_channels=in_channels, channels=channels)
            self.blocks.append(block)
            self.add_module(str(i), block)
    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        ppm_outs = []
        for ppm in self.blocks:
            ppm_out = ppm(x)
            upsampled_ppm_out = nn.functional.interpolate(ppm_out, size=x.size()[2:], mode="bilinear", align_corners=self.align_corners)
            ppm_outs.append(upsampled_ppm_out)
        return ppm_outs
class UperNetHead(nn.Module):
    def __init__(self, config, in_channels):
        super().__init__()
        self.config = config
        self.pool_scales = config.pool_scales
        self.in_channels = in_channels
        self.channels = config.hidden_size
        self.align_corners = False
        self.classifier = nn.Conv2d(self.channels, config.num_labels, kernel_size=1)
        self.psp_modules = UperNetPyramidPoolingModule(self.pool_scales, self.in_channels[-1], self.channels, align_corners=self.align_corners)
        self.bottleneck = UperNetConvModule(self.in_channels[-1] + len(self.pool_scales) * self.channels, self.channels, kernel_size=3, padding=1)
        self.lateral_convs = nn.ModuleList()
        self.fpn_convs = nn.ModuleList()
        for in_channels in self.in_channels[:-1]:
            l_conv = UperNetConvModule(in_channels, self.channels, kernel_size=1)
            fpn_conv = UperNetConvModule(self.channels, self.channels, kernel_size=3, padding=1)
            self.lateral_convs.append(l_conv)
            self.fpn_convs.append(fpn_conv)
        self.fpn_bottleneck = UperNetConvModule(len(self.in_channels) * self.channels, self.channels, kernel_size=3, padding=1)
    def init_weights(self): self.apply(self._init_weights)
    def _init_weights(self, module):
        if isinstance(module, nn.Conv2d):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
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
class UperNetFCNHead(nn.Module):
    def __init__(self, config, in_index: int = 2, kernel_size: int = 3, dilation: Union[int, Tuple[int, int]] = 1) -> None:
        super().__init__()
        self.config = config
        self.in_channels = config.auxiliary_in_channels
        self.channels = config.auxiliary_channels
        self.num_convs = config.auxiliary_num_convs
        self.concat_input = config.auxiliary_concat_input
        self.in_index = in_index
        conv_padding = (kernel_size // 2) * dilation
        convs = []
        convs.append(UperNetConvModule(self.in_channels, self.channels, kernel_size=kernel_size, padding=conv_padding, dilation=dilation))
        for i in range(self.num_convs - 1): convs.append(UperNetConvModule(self.channels, self.channels, kernel_size=kernel_size, padding=conv_padding, dilation=dilation))
        if self.num_convs == 0: self.convs = nn.Identity()
        else: self.convs = nn.Sequential(*convs)
        if self.concat_input: self.conv_cat = UperNetConvModule(self.in_channels + self.channels, self.channels, kernel_size=kernel_size, padding=kernel_size // 2)
        self.classifier = nn.Conv2d(self.channels, config.num_labels, kernel_size=1)
    def init_weights(self): self.apply(self._init_weights)
    def _init_weights(self, module):
        if isinstance(module, nn.Conv2d):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
    def forward(self, encoder_hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = encoder_hidden_states[self.in_index]
        output = self.convs(hidden_states)
        if self.concat_input: output = self.conv_cat(torch.cat([hidden_states, output], dim=1))
        output = self.classifier(output)
        return output
class UperNetPreTrainedModel(PreTrainedModel):
    config_class = UperNetConfig
    main_input_name = "pixel_values"
    _no_split_modules = []
    def _init_weights(self, module):
        if isinstance(module, UperNetPreTrainedModel):
            module.backbone.init_weights()
            module.decode_head.init_weights()
            if module.auxiliary_head is not None: module.auxiliary_head.init_weights()
    def init_weights(self):
        self.backbone.init_weights()
        self.decode_head.init_weights()
        if self.auxiliary_head is not None: self.auxiliary_head.init_weights()
UPERNET_START_DOCSTRING = r"""
    Parameters:
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) sub-class. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
        config ([`UperNetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
UPERNET_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`SegformerImageProcessor.__call__`] for details.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers in case the backbone has them. See
            `attentions` under returned tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers of the backbone. See `hidden_states` under
            returned tensors for more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("UperNet framework leveraging any vision backbone e.g. for ADE20k, CityScapes.", UPERNET_START_DOCSTRING)
class UperNetForSemanticSegmentation(UperNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.backbone = load_backbone(config)
        self.decode_head = UperNetHead(config, in_channels=self.backbone.channels)
        self.auxiliary_head = UperNetFCNHead(config) if config.use_auxiliary_head else None
        self.post_init()
    @add_start_docstrings_to_model_forward(UPERNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, pixel_values: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    labels: Optional[torch.Tensor] = None, return_dict: Optional[bool] = None) -> Union[tuple, SemanticSegmenterOutput]:
        if labels is not None and self.config.num_labels == 1: raise ValueError("The number of labels should be greater than one")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        outputs = self.backbone.forward_with_filtered_kwargs(pixel_values, output_hidden_states=output_hidden_states, output_attentions=output_attentions)
        features = outputs.feature_maps
        logits = self.decode_head(features)
        logits = nn.functional.interpolate(logits, size=pixel_values.shape[2:], mode="bilinear", align_corners=False)
        auxiliary_logits = None
        if self.auxiliary_head is not None:
            auxiliary_logits = self.auxiliary_head(features)
            auxiliary_logits = nn.functional.interpolate(auxiliary_logits, size=pixel_values.shape[2:], mode="bilinear", align_corners=False)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss(ignore_index=self.config.loss_ignore_index)
            loss = loss_fct(logits, labels)
            if auxiliary_logits is not None:
                auxiliary_loss = loss_fct(auxiliary_logits, labels)
                loss += self.config.auxiliary_loss_weight * auxiliary_loss
        if not return_dict:
            if output_hidden_states: output = (logits,) + outputs[1:]
            else: output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SemanticSegmenterOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
