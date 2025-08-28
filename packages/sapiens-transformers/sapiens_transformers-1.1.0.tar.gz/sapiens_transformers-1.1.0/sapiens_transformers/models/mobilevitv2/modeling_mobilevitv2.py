"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ...activations import ACT2FN
from ...modeling_outputs import (BaseModelOutputWithNoAttention, BaseModelOutputWithPoolingAndNoAttention, ImageClassifierOutputWithNoAttention, SemanticSegmenterOutput)
from ...modeling_utils import PreTrainedModel
from ...utils import (add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_mobilevitv2 import MobileViTV2Config
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "MobileViTV2Config"
_CHECKPOINT_FOR_DOC = "apple/mobilevitv2-1.0-imagenet1k-256"
_EXPECTED_OUTPUT_SHAPE = [1, 512, 8, 8]
_IMAGE_CLASS_CHECKPOINT = "apple/mobilevitv2-1.0-imagenet1k-256"
_IMAGE_CLASS_EXPECTED_OUTPUT = "tabby, tabby cat"
def make_divisible(value: int, divisor: int = 8, min_value: Optional[int] = None) -> int:
    if min_value is None: min_value = divisor
    new_value = max(min_value, int(value + divisor / 2) // divisor * divisor)
    if new_value < 0.9 * value: new_value += divisor
    return int(new_value)
def clip(value: float, min_val: float = float("-inf"), max_val: float = float("inf")) -> float: return max(min_val, min(max_val, value))
class MobileViTV2ConvLayer(nn.Module):
    def __init__(self, config: MobileViTV2Config, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1, groups: int = 1, bias: bool = False,
    dilation: int = 1, use_normalization: bool = True, use_activation: Union[bool, str] = True) -> None:
        super().__init__()
        padding = int((kernel_size - 1) / 2) * dilation
        if in_channels % groups != 0: raise ValueError(f"Input channels ({in_channels}) are not divisible by {groups} groups.")
        if out_channels % groups != 0: raise ValueError(f"Output channels ({out_channels}) are not divisible by {groups} groups.")
        self.convolution = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding,
        dilation=dilation, groups=groups, bias=bias, padding_mode="zeros")
        if use_normalization: self.normalization = nn.BatchNorm2d(num_features=out_channels, eps=1e-5, momentum=0.1, affine=True, track_running_stats=True)
        else: self.normalization = None
        if use_activation:
            if isinstance(use_activation, str): self.activation = ACT2FN[use_activation]
            elif isinstance(config.hidden_act, str): self.activation = ACT2FN[config.hidden_act]
            else: self.activation = config.hidden_act
        else: self.activation = None
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        features = self.convolution(features)
        if self.normalization is not None: features = self.normalization(features)
        if self.activation is not None: features = self.activation(features)
        return features
class MobileViTV2InvertedResidual(nn.Module):
    def __init__(self, config: MobileViTV2Config, in_channels: int, out_channels: int, stride: int, dilation: int = 1) -> None:
        super().__init__()
        expanded_channels = make_divisible(int(round(in_channels * config.expand_ratio)), 8)
        if stride not in [1, 2]: raise ValueError(f"Invalid stride {stride}.")
        self.use_residual = (stride == 1) and (in_channels == out_channels)
        self.expand_1x1 = MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=expanded_channels, kernel_size=1)
        self.conv_3x3 = MobileViTV2ConvLayer(config, in_channels=expanded_channels, out_channels=expanded_channels, kernel_size=3, stride=stride,
        groups=expanded_channels, dilation=dilation)
        self.reduce_1x1 = MobileViTV2ConvLayer(config, in_channels=expanded_channels, out_channels=out_channels, kernel_size=1, use_activation=False)
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        residual = features
        features = self.expand_1x1(features)
        features = self.conv_3x3(features)
        features = self.reduce_1x1(features)
        return residual + features if self.use_residual else features
class MobileViTV2MobileNetLayer(nn.Module):
    def __init__(self, config: MobileViTV2Config, in_channels: int, out_channels: int, stride: int = 1, num_stages: int = 1) -> None:
        super().__init__()
        self.layer = nn.ModuleList()
        for i in range(num_stages):
            layer = MobileViTV2InvertedResidual(config, in_channels=in_channels, out_channels=out_channels, stride=stride if i == 0 else 1)
            self.layer.append(layer)
            in_channels = out_channels
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        for layer_module in self.layer: features = layer_module(features)
        return features
class MobileViTV2LinearSelfAttention(nn.Module):
    def __init__(self, config: MobileViTV2Config, embed_dim: int) -> None:
        super().__init__()
        self.qkv_proj = MobileViTV2ConvLayer(config=config, in_channels=embed_dim, out_channels=1 + (2 * embed_dim), bias=True, kernel_size=1, use_normalization=False, use_activation=False)
        self.attn_dropout = nn.Dropout(p=config.attn_dropout)
        self.out_proj = MobileViTV2ConvLayer(config=config, in_channels=embed_dim, out_channels=embed_dim, bias=True, kernel_size=1, use_normalization=False, use_activation=False)
        self.embed_dim = embed_dim
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        qkv = self.qkv_proj(hidden_states)
        query, key, value = torch.split(qkv, split_size_or_sections=[1, self.embed_dim, self.embed_dim], dim=1)
        context_scores = torch.nn.functional.softmax(query, dim=-1)
        context_scores = self.attn_dropout(context_scores)
        context_vector = key * context_scores
        context_vector = torch.sum(context_vector, dim=-1, keepdim=True)
        out = torch.nn.functional.relu(value) * context_vector.expand_as(value)
        out = self.out_proj(out)
        return out
class MobileViTV2FFN(nn.Module):
    def __init__(self, config: MobileViTV2Config, embed_dim: int, ffn_latent_dim: int, ffn_dropout: float = 0.0) -> None:
        super().__init__()
        self.conv1 = MobileViTV2ConvLayer(config=config, in_channels=embed_dim, out_channels=ffn_latent_dim, kernel_size=1, stride=1, bias=True, use_normalization=False, use_activation=True)
        self.dropout1 = nn.Dropout(ffn_dropout)
        self.conv2 = MobileViTV2ConvLayer(config=config, in_channels=ffn_latent_dim, out_channels=embed_dim, kernel_size=1, stride=1, bias=True, use_normalization=False, use_activation=False)
        self.dropout2 = nn.Dropout(ffn_dropout)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.conv1(hidden_states)
        hidden_states = self.dropout1(hidden_states)
        hidden_states = self.conv2(hidden_states)
        hidden_states = self.dropout2(hidden_states)
        return hidden_states
class MobileViTV2TransformerLayer(nn.Module):
    def __init__(self, config: MobileViTV2Config, embed_dim: int, ffn_latent_dim: int, dropout: float = 0.0) -> None:
        super().__init__()
        self.layernorm_before = nn.GroupNorm(num_groups=1, num_channels=embed_dim, eps=config.layer_norm_eps)
        self.attention = MobileViTV2LinearSelfAttention(config, embed_dim)
        self.dropout1 = nn.Dropout(p=dropout)
        self.layernorm_after = nn.GroupNorm(num_groups=1, num_channels=embed_dim, eps=config.layer_norm_eps)
        self.ffn = MobileViTV2FFN(config, embed_dim, ffn_latent_dim, config.ffn_dropout)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        layernorm_1_out = self.layernorm_before(hidden_states)
        attention_output = self.attention(layernorm_1_out)
        hidden_states = attention_output + hidden_states
        layer_output = self.layernorm_after(hidden_states)
        layer_output = self.ffn(layer_output)
        layer_output = layer_output + hidden_states
        return layer_output
class MobileViTV2Transformer(nn.Module):
    def __init__(self, config: MobileViTV2Config, n_layers: int, d_model: int) -> None:
        super().__init__()
        ffn_multiplier = config.ffn_multiplier
        ffn_dims = [ffn_multiplier * d_model] * n_layers
        ffn_dims = [int((d // 16) * 16) for d in ffn_dims]
        self.layer = nn.ModuleList()
        for block_idx in range(n_layers):
            transformer_layer = MobileViTV2TransformerLayer(config, embed_dim=d_model, ffn_latent_dim=ffn_dims[block_idx])
            self.layer.append(transformer_layer)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        for layer_module in self.layer: hidden_states = layer_module(hidden_states)
        return hidden_states
class MobileViTV2Layer(nn.Module):
    def __init__(self, config: MobileViTV2Config, in_channels: int, out_channels: int, attn_unit_dim: int, n_attn_blocks: int = 2, dilation: int = 1, stride: int = 2) -> None:
        super().__init__()
        self.patch_width = config.patch_size
        self.patch_height = config.patch_size
        cnn_out_dim = attn_unit_dim
        if stride == 2:
            self.downsampling_layer = MobileViTV2InvertedResidual(config, in_channels=in_channels, out_channels=out_channels, stride=stride if dilation == 1 else 1,
            dilation=dilation // 2 if dilation > 1 else 1)
            in_channels = out_channels
        else: self.downsampling_layer = None
        self.conv_kxk = MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=in_channels, kernel_size=config.conv_kernel_size, groups=in_channels)
        self.conv_1x1 = MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=cnn_out_dim, kernel_size=1, use_normalization=False, use_activation=False)
        self.transformer = MobileViTV2Transformer(config, d_model=attn_unit_dim, n_layers=n_attn_blocks)
        self.layernorm = nn.GroupNorm(num_groups=1, num_channels=attn_unit_dim, eps=config.layer_norm_eps)
        self.conv_projection = MobileViTV2ConvLayer(config, in_channels=cnn_out_dim, out_channels=in_channels, kernel_size=1, use_normalization=True, use_activation=False)
    def unfolding(self, feature_map: torch.Tensor) -> Tuple[torch.Tensor, Tuple[int, int]]:
        batch_size, in_channels, img_height, img_width = feature_map.shape
        patches = nn.functional.unfold(feature_map, kernel_size=(self.patch_height, self.patch_width), stride=(self.patch_height, self.patch_width))
        patches = patches.reshape(batch_size, in_channels, self.patch_height * self.patch_width, -1)
        return patches, (img_height, img_width)
    def folding(self, patches: torch.Tensor, output_size: Tuple[int, int]) -> torch.Tensor:
        batch_size, in_dim, patch_size, n_patches = patches.shape
        patches = patches.reshape(batch_size, in_dim * patch_size, n_patches)
        feature_map = nn.functional.fold(patches, output_size=output_size, kernel_size=(self.patch_height, self.patch_width), stride=(self.patch_height, self.patch_width))
        return feature_map
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        if self.downsampling_layer: features = self.downsampling_layer(features)
        features = self.conv_kxk(features)
        features = self.conv_1x1(features)
        patches, output_size = self.unfolding(features)
        patches = self.transformer(patches)
        patches = self.layernorm(patches)
        features = self.folding(patches, output_size)
        features = self.conv_projection(features)
        return features
class MobileViTV2Encoder(nn.Module):
    def __init__(self, config: MobileViTV2Config) -> None:
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList()
        self.gradient_checkpointing = False
        dilate_layer_4 = dilate_layer_5 = False
        if config.output_stride == 8:
            dilate_layer_4 = True
            dilate_layer_5 = True
        elif config.output_stride == 16: dilate_layer_5 = True
        dilation = 1
        layer_0_dim = make_divisible(clip(value=32 * config.width_multiplier, min_val=16, max_val=64), divisor=8, min_value=16)
        layer_1_dim = make_divisible(64 * config.width_multiplier, divisor=16)
        layer_2_dim = make_divisible(128 * config.width_multiplier, divisor=8)
        layer_3_dim = make_divisible(256 * config.width_multiplier, divisor=8)
        layer_4_dim = make_divisible(384 * config.width_multiplier, divisor=8)
        layer_5_dim = make_divisible(512 * config.width_multiplier, divisor=8)
        layer_1 = MobileViTV2MobileNetLayer(config, in_channels=layer_0_dim, out_channels=layer_1_dim, stride=1, num_stages=1)
        self.layer.append(layer_1)
        layer_2 = MobileViTV2MobileNetLayer(config, in_channels=layer_1_dim, out_channels=layer_2_dim, stride=2, num_stages=2)
        self.layer.append(layer_2)
        layer_3 = MobileViTV2Layer(config, in_channels=layer_2_dim, out_channels=layer_3_dim, attn_unit_dim=make_divisible(config.base_attn_unit_dims[0] * config.width_multiplier, divisor=8),
        n_attn_blocks=config.n_attn_blocks[0])
        self.layer.append(layer_3)
        if dilate_layer_4: dilation *= 2
        layer_4 = MobileViTV2Layer(config, in_channels=layer_3_dim, out_channels=layer_4_dim, attn_unit_dim=make_divisible(config.base_attn_unit_dims[1] * config.width_multiplier, divisor=8),
        n_attn_blocks=config.n_attn_blocks[1], dilation=dilation)
        self.layer.append(layer_4)
        if dilate_layer_5: dilation *= 2
        layer_5 = MobileViTV2Layer(config, in_channels=layer_4_dim, out_channels=layer_5_dim, attn_unit_dim=make_divisible(config.base_attn_unit_dims[2] * config.width_multiplier, divisor=8),
        n_attn_blocks=config.n_attn_blocks[2], dilation=dilation)
        self.layer.append(layer_5)
    def forward(self, hidden_states: torch.Tensor, output_hidden_states: bool = False, return_dict: bool = True) -> Union[tuple, BaseModelOutputWithNoAttention]:
        all_hidden_states = () if output_hidden_states else None
        for i, layer_module in enumerate(self.layer):
            if self.gradient_checkpointing and self.training: hidden_states = self._gradient_checkpointing_func(layer_module.__call__, hidden_states)
            else: hidden_states = layer_module(hidden_states)
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states] if v is not None)
        return BaseModelOutputWithNoAttention(last_hidden_state=hidden_states, hidden_states=all_hidden_states)
class MobileViTV2PreTrainedModel(PreTrainedModel):
    config_class = MobileViTV2Config
    base_model_prefix = "mobilevitv2"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _no_split_modules = ["MobileViTV2Layer"]
    def _init_weights(self, module: Union[nn.Linear, nn.Conv2d, nn.LayerNorm]) -> None:
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
MOBILEVITV2_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`MobileViTV2Config`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MOBILEVITV2_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`MobileViTImageProcessor.__call__`] for details.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare MobileViTV2 model outputting raw hidden-states without any specific head on top.", MOBILEVITV2_START_DOCSTRING)
class MobileViTV2Model(MobileViTV2PreTrainedModel):
    def __init__(self, config: MobileViTV2Config, expand_output: bool = True):
        super().__init__(config)
        self.config = config
        self.expand_output = expand_output
        layer_0_dim = make_divisible(clip(value=32 * config.width_multiplier, min_val=16, max_val=64), divisor=8, min_value=16)
        self.conv_stem = MobileViTV2ConvLayer(config, in_channels=config.num_channels, out_channels=layer_0_dim, kernel_size=3, stride=2, use_normalization=True, use_activation=True)
        self.encoder = MobileViTV2Encoder(config)
        self.post_init()
    def _prune_heads(self, heads_to_prune):
        for layer_index, heads in heads_to_prune.items():
            mobilevitv2_layer = self.encoder.layer[layer_index]
            if isinstance(mobilevitv2_layer, MobileViTV2Layer):
                for transformer_layer in mobilevitv2_layer.transformer.layer: transformer_layer.attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(MOBILEVITV2_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[tuple, BaseModelOutputWithPoolingAndNoAttention]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        embedding_output = self.conv_stem(pixel_values)
        encoder_outputs = self.encoder(embedding_output, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if self.expand_output:
            last_hidden_state = encoder_outputs[0]
            pooled_output = torch.mean(last_hidden_state, dim=[-2, -1], keepdim=False)
        else:
            last_hidden_state = encoder_outputs[0]
            pooled_output = None
        if not return_dict:
            output = (last_hidden_state, pooled_output) if pooled_output is not None else (last_hidden_state,)
            return output + encoder_outputs[1:]
        return BaseModelOutputWithPoolingAndNoAttention(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states)
@add_start_docstrings("MobileViTV2 model with an image classification head on top (a linear layer on top of the pooled features), e.g. for ImageNet.", MOBILEVITV2_START_DOCSTRING)
class MobileViTV2ForImageClassification(MobileViTV2PreTrainedModel):
    def __init__(self, config: MobileViTV2Config) -> None:
        super().__init__(config)
        self.num_labels = config.num_labels
        self.mobilevitv2 = MobileViTV2Model(config)
        out_channels = make_divisible(512 * config.width_multiplier, divisor=8)
        self.classifier = (nn.Linear(in_features=out_channels, out_features=config.num_labels) if config.num_labels > 0 else nn.Identity())
        self.post_init()
    @add_start_docstrings_to_model_forward(MOBILEVITV2_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, labels: Optional[torch.Tensor] = None,
    return_dict: Optional[bool] = None) -> Union[tuple, ImageClassifierOutputWithNoAttention]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.mobilevitv2(pixel_values, output_hidden_states=output_hidden_states, return_dict=return_dict)
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
        return ImageClassifierOutputWithNoAttention(loss=loss, logits=logits, hidden_states=outputs.hidden_states)
class MobileViTV2ASPPPooling(nn.Module):
    def __init__(self, config: MobileViTV2Config, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.global_pool = nn.AdaptiveAvgPool2d(output_size=1)
        self.conv_1x1 = MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1, use_normalization=True, use_activation="relu")
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        spatial_size = features.shape[-2:]
        features = self.global_pool(features)
        features = self.conv_1x1(features)
        features = nn.functional.interpolate(features, size=spatial_size, mode="bilinear", align_corners=False)
        return features
class MobileViTV2ASPP(nn.Module):
    def __init__(self, config: MobileViTV2Config) -> None:
        super().__init__()
        encoder_out_channels = make_divisible(512 * config.width_multiplier, divisor=8)
        in_channels = encoder_out_channels
        out_channels = config.aspp_out_channels
        if len(config.atrous_rates) != 3: raise ValueError("Expected 3 values for atrous_rates")
        self.convs = nn.ModuleList()
        in_projection = MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=out_channels, kernel_size=1, use_activation="relu")
        self.convs.append(in_projection)
        self.convs.extend([MobileViTV2ConvLayer(config, in_channels=in_channels, out_channels=out_channels, kernel_size=3, dilation=rate, use_activation="relu")
        for rate in config.atrous_rates])
        pool_layer = MobileViTV2ASPPPooling(config, in_channels, out_channels)
        self.convs.append(pool_layer)
        self.project = MobileViTV2ConvLayer(config, in_channels=5 * out_channels, out_channels=out_channels, kernel_size=1, use_activation="relu")
        self.dropout = nn.Dropout(p=config.aspp_dropout_prob)
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        pyramid = []
        for conv in self.convs: pyramid.append(conv(features))
        pyramid = torch.cat(pyramid, dim=1)
        pooled_features = self.project(pyramid)
        pooled_features = self.dropout(pooled_features)
        return pooled_features
class MobileViTV2DeepLabV3(nn.Module):
    def __init__(self, config: MobileViTV2Config) -> None:
        super().__init__()
        self.aspp = MobileViTV2ASPP(config)
        self.dropout = nn.Dropout2d(config.classifier_dropout_prob)
        self.classifier = MobileViTV2ConvLayer(config, in_channels=config.aspp_out_channels, out_channels=config.num_labels, kernel_size=1, use_normalization=False,
        use_activation=False, bias=True)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        features = self.aspp(hidden_states[-1])
        features = self.dropout(features)
        features = self.classifier(features)
        return features
@add_start_docstrings("MobileViTV2 model with a semantic segmentation head on top, e.g. for Pascal VOC.", MOBILEVITV2_START_DOCSTRING)
class MobileViTV2ForSemanticSegmentation(MobileViTV2PreTrainedModel):
    def __init__(self, config: MobileViTV2Config) -> None:
        super().__init__(config)
        self.num_labels = config.num_labels
        self.mobilevitv2 = MobileViTV2Model(config, expand_output=False)
        self.segmentation_head = MobileViTV2DeepLabV3(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(MOBILEVITV2_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[tuple, SemanticSegmenterOutput]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if labels is not None and self.config.num_labels == 1: raise ValueError("The number of labels should be greater than one")
        outputs = self.mobilevitv2(pixel_values, output_hidden_states=True, return_dict=return_dict)
        encoder_hidden_states = outputs.hidden_states if return_dict else outputs[1]
        logits = self.segmentation_head(encoder_hidden_states)
        loss = None
        if labels is not None:
            upsampled_logits = nn.functional.interpolate(logits, size=labels.shape[-2:], mode="bilinear", align_corners=False)
            loss_fct = CrossEntropyLoss(ignore_index=self.config.semantic_loss_ignore_index)
            loss = loss_fct(upsampled_logits, labels)
        if not return_dict:
            if output_hidden_states: output = (logits,) + outputs[1:]
            else: output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SemanticSegmenterOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states if output_hidden_states else None, attentions=None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
