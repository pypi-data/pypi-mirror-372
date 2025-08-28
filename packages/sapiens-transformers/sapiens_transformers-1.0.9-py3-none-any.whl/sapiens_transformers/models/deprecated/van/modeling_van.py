"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from collections import OrderedDict
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ....activations import ACT2FN
from ....modeling_outputs import (BaseModelOutputWithNoAttention, BaseModelOutputWithPoolingAndNoAttention, ImageClassifierOutputWithNoAttention)
from ....modeling_utils import PreTrainedModel
from ....utils import add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging
from .configuration_van import VanConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "VanConfig"
_CHECKPOINT_FOR_DOC = "Visual-Attention-Network/van-base"
_EXPECTED_OUTPUT_SHAPE = [1, 512, 7, 7]
_IMAGE_CLASS_CHECKPOINT = "Visual-Attention-Network/van-base"
_IMAGE_CLASS_EXPECTED_OUTPUT = "tabby, tabby cat"
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class VanDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class VanOverlappingPatchEmbedder(nn.Module):
    def __init__(self, in_channels: int, hidden_size: int, patch_size: int = 7, stride: int = 4):
        super().__init__()
        self.convolution = nn.Conv2d(in_channels, hidden_size, kernel_size=patch_size, stride=stride, padding=patch_size // 2)
        self.normalization = nn.BatchNorm2d(hidden_size)
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        hidden_state = self.convolution(input)
        hidden_state = self.normalization(hidden_state)
        return hidden_state
class VanMlpLayer(nn.Module):
    def __init__(self, in_channels: int, hidden_size: int, out_channels: int, hidden_act: str = "gelu", dropout_rate: float = 0.5):
        super().__init__()
        self.in_dense = nn.Conv2d(in_channels, hidden_size, kernel_size=1)
        self.depth_wise = nn.Conv2d(hidden_size, hidden_size, kernel_size=3, padding=1, groups=hidden_size)
        self.activation = ACT2FN[hidden_act]
        self.dropout1 = nn.Dropout(dropout_rate)
        self.out_dense = nn.Conv2d(hidden_size, out_channels, kernel_size=1)
        self.dropout2 = nn.Dropout(dropout_rate)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state = self.in_dense(hidden_state)
        hidden_state = self.depth_wise(hidden_state)
        hidden_state = self.activation(hidden_state)
        hidden_state = self.dropout1(hidden_state)
        hidden_state = self.out_dense(hidden_state)
        hidden_state = self.dropout2(hidden_state)
        return hidden_state
class VanLargeKernelAttention(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.depth_wise = nn.Conv2d(hidden_size, hidden_size, kernel_size=5, padding=2, groups=hidden_size)
        self.depth_wise_dilated = nn.Conv2d(hidden_size, hidden_size, kernel_size=7, dilation=3, padding=9, groups=hidden_size)
        self.point_wise = nn.Conv2d(hidden_size, hidden_size, kernel_size=1)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state = self.depth_wise(hidden_state)
        hidden_state = self.depth_wise_dilated(hidden_state)
        hidden_state = self.point_wise(hidden_state)
        return hidden_state
class VanLargeKernelAttentionLayer(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.attention = VanLargeKernelAttention(hidden_size)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        attention = self.attention(hidden_state)
        attended = hidden_state * attention
        return attended
class VanSpatialAttentionLayer(nn.Module):
    def __init__(self, hidden_size: int, hidden_act: str = "gelu"):
        super().__init__()
        self.pre_projection = nn.Sequential(OrderedDict([("conv", nn.Conv2d(hidden_size, hidden_size, kernel_size=1)), ("act", ACT2FN[hidden_act])]))
        self.attention_layer = VanLargeKernelAttentionLayer(hidden_size)
        self.post_projection = nn.Conv2d(hidden_size, hidden_size, kernel_size=1)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        residual = hidden_state
        hidden_state = self.pre_projection(hidden_state)
        hidden_state = self.attention_layer(hidden_state)
        hidden_state = self.post_projection(hidden_state)
        hidden_state = hidden_state + residual
        return hidden_state
class VanLayerScaling(nn.Module):
    def __init__(self, hidden_size: int, initial_value: float = 1e-2):
        super().__init__()
        self.weight = nn.Parameter(initial_value * torch.ones((hidden_size)), requires_grad=True)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state = self.weight.unsqueeze(-1).unsqueeze(-1) * hidden_state
        return hidden_state
class VanLayer(nn.Module):
    def __init__(self, config: VanConfig, hidden_size: int, mlp_ratio: int = 4, drop_path_rate: float = 0.5):
        super().__init__()
        self.drop_path = VanDropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()
        self.pre_normomalization = nn.BatchNorm2d(hidden_size)
        self.attention = VanSpatialAttentionLayer(hidden_size, config.hidden_act)
        self.attention_scaling = VanLayerScaling(hidden_size, config.layer_scale_init_value)
        self.post_normalization = nn.BatchNorm2d(hidden_size)
        self.mlp = VanMlpLayer(hidden_size, hidden_size * mlp_ratio, hidden_size, config.hidden_act, config.dropout_rate)
        self.mlp_scaling = VanLayerScaling(hidden_size, config.layer_scale_init_value)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        residual = hidden_state
        hidden_state = self.pre_normomalization(hidden_state)
        hidden_state = self.attention(hidden_state)
        hidden_state = self.attention_scaling(hidden_state)
        hidden_state = self.drop_path(hidden_state)
        hidden_state = residual + hidden_state
        residual = hidden_state
        hidden_state = self.post_normalization(hidden_state)
        hidden_state = self.mlp(hidden_state)
        hidden_state = self.mlp_scaling(hidden_state)
        hidden_state = self.drop_path(hidden_state)
        hidden_state = residual + hidden_state
        return hidden_state
class VanStage(nn.Module):
    def __init__(self, config: VanConfig, in_channels: int, hidden_size: int, patch_size: int, stride: int, depth: int, mlp_ratio: int = 4, drop_path_rate: float = 0.0):
        super().__init__()
        self.embeddings = VanOverlappingPatchEmbedder(in_channels, hidden_size, patch_size, stride)
        self.layers = nn.Sequential(*[VanLayer(config, hidden_size, mlp_ratio=mlp_ratio, drop_path_rate=drop_path_rate) for _ in range(depth)])
        self.normalization = nn.LayerNorm(hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state = self.embeddings(hidden_state)
        hidden_state = self.layers(hidden_state)
        batch_size, hidden_size, height, width = hidden_state.shape
        hidden_state = hidden_state.flatten(2).transpose(1, 2)
        hidden_state = self.normalization(hidden_state)
        hidden_state = hidden_state.view(batch_size, height, width, hidden_size).permute(0, 3, 1, 2)
        return hidden_state
class VanEncoder(nn.Module):
    def __init__(self, config: VanConfig):
        super().__init__()
        self.stages = nn.ModuleList([])
        patch_sizes = config.patch_sizes
        strides = config.strides
        hidden_sizes = config.hidden_sizes
        depths = config.depths
        mlp_ratios = config.mlp_ratios
        drop_path_rates = [x.item() for x in torch.linspace(0, config.drop_path_rate, sum(config.depths))]
        for num_stage, (patch_size, stride, hidden_size, depth, mlp_expantion, drop_path_rate) in enumerate(zip(patch_sizes, strides, hidden_sizes, depths, mlp_ratios, drop_path_rates)):
            is_first_stage = num_stage == 0
            in_channels = hidden_sizes[num_stage - 1]
            if is_first_stage: in_channels = config.num_channels
            self.stages.append(VanStage(config, in_channels, hidden_size, patch_size=patch_size, stride=stride, depth=depth, mlp_ratio=mlp_expantion, drop_path_rate=drop_path_rate))
    def forward(self, hidden_state: torch.Tensor, output_hidden_states: Optional[bool] = False, return_dict: Optional[bool] = True) -> Union[Tuple, BaseModelOutputWithNoAttention]:
        all_hidden_states = () if output_hidden_states else None
        for _, stage_module in enumerate(self.stages):
            hidden_state = stage_module(hidden_state)
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_state,)
        if not return_dict: return tuple(v for v in [hidden_state, all_hidden_states] if v is not None)
        return BaseModelOutputWithNoAttention(last_hidden_state=hidden_state, hidden_states=all_hidden_states)
class VanPreTrainedModel(PreTrainedModel):
    config_class = VanConfig
    base_model_prefix = "van"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.trunc_normal_(module.weight, std=self.config.initializer_range)
            if isinstance(module, nn.Linear) and module.bias is not None: nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.LayerNorm):
            nn.init.constant_(module.bias, 0)
            nn.init.constant_(module.weight, 1.0)
        elif isinstance(module, nn.Conv2d):
            fan_out = module.kernel_size[0] * module.kernel_size[1] * module.out_channels
            fan_out //= module.groups
            module.weight.data.normal_(0, math.sqrt(2.0 / fan_out))
            if module.bias is not None: module.bias.data.zero_()
VAN_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`VanConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
VAN_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`ConvNextImageProcessor.__call__`] for details.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all stages. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare VAN model outputting raw features without any specific head on top. Note, VAN does not have an embedding layer.", VAN_START_DOCSTRING)
class VanModel(VanPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.encoder = VanEncoder(config)
        self.layernorm = nn.LayerNorm(config.hidden_sizes[-1], eps=config.layer_norm_eps)
        self.post_init()
    @add_start_docstrings_to_model_forward(VAN_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor], output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, BaseModelOutputWithPoolingAndNoAttention]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        encoder_outputs = self.encoder(pixel_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs[0]
        pooled_output = last_hidden_state.mean(dim=[-2, -1])
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPoolingAndNoAttention(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states)
@add_start_docstrings("VAN Model with an image classification head on top (a linear layer on top of the pooled features), e.g. for ImageNet.", VAN_START_DOCSTRING)
class VanForImageClassification(VanPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.van = VanModel(config)
        self.classifier = (nn.Linear(config.hidden_sizes[-1], config.num_labels) if config.num_labels > 0 else nn.Identity())
        self.post_init()
    @add_start_docstrings_to_model_forward(VAN_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, ImageClassifierOutputWithNoAttention]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.van(pixel_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs.pooler_output if return_dict else outputs[1]
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.config.num_labels == 1: self.config.problem_type = "regression"
                elif self.config.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.config.num_labels == 1: loss = loss_fct(logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.config.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return ImageClassifierOutputWithNoAttention(loss=loss, logits=logits, hidden_states=outputs.hidden_states)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
