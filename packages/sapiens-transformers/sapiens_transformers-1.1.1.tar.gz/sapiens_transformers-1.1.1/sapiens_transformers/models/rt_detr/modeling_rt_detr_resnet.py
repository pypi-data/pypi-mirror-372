"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from typing import Optional
from torch import Tensor, nn
from ...activations import ACT2FN
from ...modeling_outputs import (BackboneOutput, BaseModelOutputWithNoAttention)
from ...modeling_utils import PreTrainedModel
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from ...utils.backbone_utils import BackboneMixin
from .configuration_rt_detr_resnet import RTDetrResNetConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "RTDetrResNetConfig"
_CHECKPOINT_FOR_DOC = "microsoft/resnet-50"
_EXPECTED_OUTPUT_SHAPE = [1, 2048, 7, 7]
class RTDetrResNetConvLayer(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, stride: int = 1, activation: str = "relu"):
        super().__init__()
        self.convolution = nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=kernel_size // 2, bias=False)
        self.normalization = nn.BatchNorm2d(out_channels)
        self.activation = ACT2FN[activation] if activation is not None else nn.Identity()
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = self.convolution(input)
        hidden_state = self.normalization(hidden_state)
        hidden_state = self.activation(hidden_state)
        return hidden_state
class RTDetrResNetEmbeddings(nn.Module):
    def __init__(self, config: RTDetrResNetConfig):
        super().__init__()
        self.embedder = nn.Sequential(*[RTDetrResNetConvLayer(config.num_channels, config.embedding_size // 2, kernel_size=3, stride=2, activation=config.hidden_act),
        RTDetrResNetConvLayer(config.embedding_size // 2, config.embedding_size // 2, kernel_size=3, stride=1, activation=config.hidden_act),
        RTDetrResNetConvLayer(config.embedding_size // 2, config.embedding_size, kernel_size=3, stride=1, activation=config.hidden_act)])
        self.pooler = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.num_channels = config.num_channels
    def forward(self, pixel_values: Tensor) -> Tensor:
        num_channels = pixel_values.shape[1]
        if num_channels != self.num_channels: raise ValueError("Make sure that the channel dimension of the pixel values match with the one set in the configuration.")
        embedding = self.embedder(pixel_values)
        embedding = self.pooler(embedding)
        return embedding
class RTDetrResNetShortCut(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 2):
        super().__init__()
        self.convolution = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False)
        self.normalization = nn.BatchNorm2d(out_channels)
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = self.convolution(input)
        hidden_state = self.normalization(hidden_state)
        return hidden_state
class RTDetrResNetBasicLayer(nn.Module):
    def __init__(self, config: RTDetrResNetConfig, in_channels: int, out_channels: int, stride: int = 1, should_apply_shortcut: bool = False):
        super().__init__()
        if in_channels != out_channels: self.shortcut = (nn.Sequential(*[nn.AvgPool2d(2, 2, 0, ceil_mode=True), RTDetrResNetShortCut(in_channels, out_channels, stride=1)]) if should_apply_shortcut else nn.Identity())
        else: self.shortcut = (RTDetrResNetShortCut(in_channels, out_channels, stride=stride) if should_apply_shortcut else nn.Identity())
        self.layer = nn.Sequential(RTDetrResNetConvLayer(in_channels, out_channels, stride=stride), RTDetrResNetConvLayer(out_channels, out_channels, activation=None))
        self.activation = ACT2FN[config.hidden_act]
    def forward(self, hidden_state):
        residual = hidden_state
        hidden_state = self.layer(hidden_state)
        residual = self.shortcut(residual)
        hidden_state += residual
        hidden_state = self.activation(hidden_state)
        return hidden_state
class RTDetrResNetBottleNeckLayer(nn.Module):
    def __init__(self, config: RTDetrResNetConfig, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        reduction = 4
        should_apply_shortcut = in_channels != out_channels or stride != 1
        reduces_channels = out_channels // reduction
        if stride == 2: self.shortcut = nn.Sequential(*[nn.AvgPool2d(2, 2, 0, ceil_mode=True),
        RTDetrResNetShortCut(in_channels, out_channels, stride=1) if should_apply_shortcut else nn.Identity()])
        else: self.shortcut = (RTDetrResNetShortCut(in_channels, out_channels, stride=stride) if should_apply_shortcut else nn.Identity())
        self.layer = nn.Sequential(RTDetrResNetConvLayer(in_channels, reduces_channels, kernel_size=1, stride=stride if config.downsample_in_bottleneck else 1),
        RTDetrResNetConvLayer(reduces_channels, reduces_channels, stride=stride if not config.downsample_in_bottleneck else 1), RTDetrResNetConvLayer(reduces_channels, out_channels, kernel_size=1, activation=None))
        self.activation = ACT2FN[config.hidden_act]
    def forward(self, hidden_state):
        residual = hidden_state
        hidden_state = self.layer(hidden_state)
        residual = self.shortcut(residual)
        hidden_state += residual
        hidden_state = self.activation(hidden_state)
        return hidden_state
class RTDetrResNetStage(nn.Module):
    def __init__(self, config: RTDetrResNetConfig, in_channels: int, out_channels: int, stride: int = 2, depth: int = 2):
        super().__init__()
        layer = RTDetrResNetBottleNeckLayer if config.layer_type == "bottleneck" else RTDetrResNetBasicLayer
        if config.layer_type == "bottleneck": first_layer = layer(config, in_channels, out_channels, stride=stride)
        else: first_layer = layer(config, in_channels, out_channels, stride=stride, should_apply_shortcut=True)
        self.layers = nn.Sequential(first_layer, *[layer(config, out_channels, out_channels) for _ in range(depth - 1)])
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class RTDetrResNetEncoder(nn.Module):
    def __init__(self, config: RTDetrResNetConfig):
        super().__init__()
        self.stages = nn.ModuleList([])
        self.stages.append(RTDetrResNetStage(config, config.embedding_size, config.hidden_sizes[0], stride=2 if config.downsample_in_first_stage else 1, depth=config.depths[0]))
        in_out_channels = zip(config.hidden_sizes, config.hidden_sizes[1:])
        for (in_channels, out_channels), depth in zip(in_out_channels, config.depths[1:]): self.stages.append(RTDetrResNetStage(config, in_channels, out_channels, depth=depth))
    def forward(self, hidden_state: Tensor, output_hidden_states: bool = False, return_dict: bool = True) -> BaseModelOutputWithNoAttention:
        hidden_states = () if output_hidden_states else None
        for stage_module in self.stages:
            if output_hidden_states: hidden_states = hidden_states + (hidden_state,)
            hidden_state = stage_module(hidden_state)
        if output_hidden_states: hidden_states = hidden_states + (hidden_state,)
        if not return_dict: return tuple(v for v in [hidden_state, hidden_states] if v is not None)
        return BaseModelOutputWithNoAttention(last_hidden_state=hidden_state, hidden_states=hidden_states)
class RTDetrResNetPreTrainedModel(PreTrainedModel):
    config_class = RTDetrResNetConfig
    base_model_prefix = "resnet"
    main_input_name = "pixel_values"
    _no_split_modules = ["RTDetrResNetConvLayer", "RTDetrResNetShortCut"]
    def _init_weights(self, module):
        if isinstance(module, nn.Conv2d): nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
        elif isinstance(module, nn.Linear):
            nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5))
            if module.bias is not None:
                fan_in, _ = nn.init._calculate_fan_in_and_fan_out(module.weight)
                bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
                nn.init.uniform_(module.bias, -bound, bound)
        elif isinstance(module, (nn.BatchNorm2d, nn.GroupNorm)):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
RTDETR_RESNET_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`RTDetrResNetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
RTDETR_RESNET_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`RTDetrImageProcessor.__call__`] for details.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("ResNet backbone, to be used with frameworks like RTDETR.", RTDETR_RESNET_START_DOCSTRING)
class RTDetrResNetBackbone(RTDetrResNetPreTrainedModel, BackboneMixin):
    def __init__(self, config):
        super().__init__(config)
        super()._init_backbone(config)
        self.num_features = [config.embedding_size] + config.hidden_sizes
        self.embedder = RTDetrResNetEmbeddings(config)
        self.encoder = RTDetrResNetEncoder(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(RTDETR_RESNET_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Tensor, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> BackboneOutput:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        embedding_output = self.embedder(pixel_values)
        outputs = self.encoder(embedding_output, output_hidden_states=True, return_dict=True)
        hidden_states = outputs.hidden_states
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
