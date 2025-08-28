"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import math
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.autograd import Function
from torch.autograd.function import once_differentiable
from ...activations import ACT2FN
from ...file_utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, is_scipy_available, is_timm_available, is_torch_cuda_available,
is_vision_available, replace_return_docstrings, requires_backends)
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import meshgrid
from ...utils import is_sapiens_accelerator_available, is_ninja_available, logging
from ...utils.backbone_utils import load_backbone
from ..auto import AutoModel
from .configuration_grounding_dino import GroundingDinoConfig
if is_vision_available(): from sapiens_transformers.image_transforms import center_to_corners_format
if is_sapiens_accelerator_available():
    from sapiens_accelerator import PartialState
    from sapiens_accelerator.utils import reduce
if is_scipy_available(): from scipy.optimize import linear_sum_assignment
if is_timm_available(): from timm import create_model
logger = logging.get_logger(__name__)
MultiScaleDeformableAttention = None
def load_cuda_kernels():
    from torch.utils.cpp_extension import load
    global MultiScaleDeformableAttention
    root = Path(__file__).resolve().parent.parent.parent / "kernels" / "deformable_detr"
    src_files = [root / filename for filename in ["vision.cpp", os.path.join("cpu", "ms_deform_attn_cpu.cpp"), os.path.join("cuda", "ms_deform_attn_cuda.cu")]]
    MultiScaleDeformableAttention = load("MultiScaleDeformableAttention", src_files, with_cuda=True, extra_include_paths=[str(root)], extra_cflags=["-DWITH_CUDA=1"],
    extra_cuda_cflags=["-DCUDA_HAS_FP16=1", "-D__CUDA_NO_HALF_OPERATORS__", "-D__CUDA_NO_HALF_CONVERSIONS__", "-D__CUDA_NO_HALF2_OPERATORS__"])
class MultiScaleDeformableAttentionFunction(Function):
    @staticmethod
    def forward(context, value, value_spatial_shapes, value_level_start_index, sampling_locations, attention_weights, im2col_step):
        context.im2col_step = im2col_step
        output = MultiScaleDeformableAttention.ms_deform_attn_forward(value, value_spatial_shapes, value_level_start_index, sampling_locations, attention_weights, context.im2col_step)
        context.save_for_backward(value, value_spatial_shapes, value_level_start_index, sampling_locations, attention_weights)
        return output
    @staticmethod
    @once_differentiable
    def backward(context, grad_output):
        (value, value_spatial_shapes, value_level_start_index, sampling_locations, attention_weights) = context.saved_tensors
        grad_value, grad_sampling_loc, grad_attn_weight = MultiScaleDeformableAttention.ms_deform_attn_backward(value, value_spatial_shapes, value_level_start_index,
        sampling_locations, attention_weights, grad_output, context.im2col_step)
        return grad_value, None, None, grad_sampling_loc, grad_attn_weight, None
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "GroundingDinoConfig"
_CHECKPOINT_FOR_DOC = "IDEA-Research/grounding-dino-tiny"
@dataclass
class GroundingDinoDecoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
@dataclass
class GroundingDinoEncoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state_vision: torch.FloatTensor = None
    last_hidden_state_text: torch.FloatTensor = None
    vision_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    text_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
@dataclass
class GroundingDinoModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    init_reference_points: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    encoder_last_hidden_state_vision: Optional[torch.FloatTensor] = None
    encoder_last_hidden_state_text: Optional[torch.FloatTensor] = None
    encoder_vision_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_text_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
@dataclass
class GroundingDinoObjectDetectionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    loss_dict: Optional[Dict] = None
    logits: torch.FloatTensor = None
    pred_boxes: torch.FloatTensor = None
    auxiliary_outputs: Optional[List[Dict]] = None
    last_hidden_state: Optional[torch.FloatTensor] = None
    init_reference_points: Optional[torch.FloatTensor] = None
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_reference_points: Optional[torch.FloatTensor] = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    encoder_last_hidden_state_vision: Optional[torch.FloatTensor] = None
    encoder_last_hidden_state_text: Optional[torch.FloatTensor] = None
    encoder_vision_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_text_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
class GroundingDinoFrozenBatchNorm2d(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.register_buffer("weight", torch.ones(n))
        self.register_buffer("bias", torch.zeros(n))
        self.register_buffer("running_mean", torch.zeros(n))
        self.register_buffer("running_var", torch.ones(n))
    def _load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
        num_batches_tracked_key = prefix + "num_batches_tracked"
        if num_batches_tracked_key in state_dict: del state_dict[num_batches_tracked_key]
        super()._load_from_state_dict(state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs)
    def forward(self, x):
        weight = self.weight.reshape(1, -1, 1, 1)
        bias = self.bias.reshape(1, -1, 1, 1)
        running_var = self.running_var.reshape(1, -1, 1, 1)
        running_mean = self.running_mean.reshape(1, -1, 1, 1)
        epsilon = 1e-5
        scale = weight * (running_var + epsilon).rsqrt()
        bias = bias - running_mean * scale
        return x * scale + bias
def replace_batch_norm(model):
    for name, module in model.named_children():
        if isinstance(module, nn.BatchNorm2d):
            new_module = GroundingDinoFrozenBatchNorm2d(module.num_features)
            if not module.weight.device == torch.device("meta"):
                new_module.weight.data.copy_(module.weight)
                new_module.bias.data.copy_(module.bias)
                new_module.running_mean.data.copy_(module.running_mean)
                new_module.running_var.data.copy_(module.running_var)
            model._modules[name] = new_module
        if len(list(module.children())) > 0: replace_batch_norm(module)
class GroundingDinoConvEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config.use_timm_backbone:
            requires_backends(self, ["timm"])
            backbone = create_model(config.backbone, pretrained=config.use_pretrained_backbone, features_only=True, **config.backbone_kwargs)
        else: backbone = load_backbone(config)
        with torch.no_grad(): replace_batch_norm(backbone)
        self.model = backbone
        self.intermediate_channel_sizes = (self.model.feature_info.channels() if config.use_timm_backbone else self.model.channels)
        backbone_model_type = None
        if config.backbone is not None: backbone_model_type = config.backbone
        elif config.backbone_config is not None: backbone_model_type = config.backbone_config.model_type
        else: raise ValueError("Either `backbone` or `backbone_config` should be provided in the config")
        if "resnet" in backbone_model_type:
            for name, parameter in self.model.named_parameters():
                if config.use_timm_backbone:
                    if "layer2" not in name and "layer3" not in name and "layer4" not in name: parameter.requires_grad_(False)
                else:
                    if "stage.1" not in name and "stage.2" not in name and "stage.3" not in name: parameter.requires_grad_(False)
    def forward(self, pixel_values: torch.Tensor, pixel_mask: torch.Tensor):
        features = self.model(pixel_values) if self.config.use_timm_backbone else self.model(pixel_values).feature_maps
        out = []
        for feature_map in features:
            mask = nn.functional.interpolate(pixel_mask[None].float(), size=feature_map.shape[-2:]).to(torch.bool)[0]
            out.append((feature_map, mask))
        return out
class GroundingDinoConvModel(nn.Module):
    def __init__(self, conv_encoder, position_embedding):
        super().__init__()
        self.conv_encoder = conv_encoder
        self.position_embedding = position_embedding
    def forward(self, pixel_values, pixel_mask):
        out = self.conv_encoder(pixel_values, pixel_mask)
        pos = []
        for feature_map, mask in out: pos.append(self.position_embedding(feature_map, mask).to(feature_map.dtype))
        return out, pos
class GroundingDinoSinePositionEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.embedding_dim = config.d_model // 2
        self.temperature = config.positional_embedding_temperature
        self.scale = 2 * math.pi
    def forward(self, pixel_values, pixel_mask):
        y_embed = pixel_mask.cumsum(1, dtype=torch.float32)
        x_embed = pixel_mask.cumsum(2, dtype=torch.float32)
        eps = 1e-6
        y_embed = y_embed / (y_embed[:, -1:, :] + eps) * self.scale
        x_embed = x_embed / (x_embed[:, :, -1:] + eps) * self.scale
        dim_t = torch.arange(self.embedding_dim, dtype=torch.float32, device=pixel_values.device)
        dim_t = self.temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / self.embedding_dim)
        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos = torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)
        return pos
class GroundingDinoLearnedPositionEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        embedding_dim = config.d_model // 2
        self.row_embeddings = nn.Embedding(50, embedding_dim)
        self.column_embeddings = nn.Embedding(50, embedding_dim)
    def forward(self, pixel_values, pixel_mask=None):
        height, width = pixel_values.shape[-2:]
        width_values = torch.arange(width, device=pixel_values.device)
        height_values = torch.arange(height, device=pixel_values.device)
        x_emb = self.column_embeddings(width_values)
        y_emb = self.row_embeddings(height_values)
        pos = torch.cat([x_emb.unsqueeze(0).repeat(height, 1, 1), y_emb.unsqueeze(1).repeat(1, width, 1)], dim=-1)
        pos = pos.permute(2, 0, 1)
        pos = pos.unsqueeze(0)
        pos = pos.repeat(pixel_values.shape[0], 1, 1, 1)
        return pos
def build_position_encoding(config):
    if config.position_embedding_type == "sine": position_embedding = GroundingDinoSinePositionEmbedding(config)
    elif config.position_embedding_type == "learned": position_embedding = GroundingDinoLearnedPositionEmbedding(config)
    else: raise ValueError(f"Not supported {config.position_embedding_type}")
    return position_embedding
def multi_scale_deformable_attention(value: Tensor, value_spatial_shapes: Tensor, sampling_locations: Tensor, attention_weights: Tensor) -> Tensor:
    batch_size, _, num_heads, hidden_dim = value.shape
    _, num_queries, num_heads, num_levels, num_points, _ = sampling_locations.shape
    value_list = value.split([height.item() * width.item() for height, width in value_spatial_shapes], dim=1)
    sampling_grids = 2 * sampling_locations - 1
    sampling_value_list = []
    for level_id, (height, width) in enumerate(value_spatial_shapes):
        value_l_ = (value_list[level_id].flatten(2).transpose(1, 2).reshape(batch_size * num_heads, hidden_dim, height, width))
        sampling_grid_l_ = sampling_grids[:, :, :, level_id].transpose(1, 2).flatten(0, 1)
        sampling_value_l_ = nn.functional.grid_sample(value_l_, sampling_grid_l_, mode="bilinear", padding_mode="zeros", align_corners=False)
        sampling_value_list.append(sampling_value_l_)
    attention_weights = attention_weights.transpose(1, 2).reshape(batch_size * num_heads, 1, num_queries, num_levels * num_points)
    output = ((torch.stack(sampling_value_list, dim=-2).flatten(-2) * attention_weights).sum(-1).view(batch_size, num_heads * hidden_dim, num_queries))
    return output.transpose(1, 2).contiguous()
class GroundingDinoMultiscaleDeformableAttention(nn.Module):
    def __init__(self, config: GroundingDinoConfig, num_heads: int, n_points: int):
        super().__init__()
        kernel_loaded = MultiScaleDeformableAttention is not None
        if is_torch_cuda_available() and is_ninja_available() and not kernel_loaded:
            try: load_cuda_kernels()
            except Exception as e: logger.warning(f"Could not load the custom kernel for multi-scale deformable attention: {e}")
        if config.d_model % num_heads != 0: raise ValueError(f"embed_dim (d_model) must be divisible by num_heads, but got {config.d_model} and {num_heads}")
        dim_per_head = config.d_model // num_heads
        if not ((dim_per_head & (dim_per_head - 1) == 0) and dim_per_head != 0): warnings.warn("You'd better set embed_dim (d_model) in GroundingDinoMultiscaleDeformableAttention to make the dimension of each attention head a power of 2 which is more efficient in the authors' CUDA implementation.")
        self.im2col_step = 64
        self.d_model = config.d_model
        self.n_levels = config.num_feature_levels
        self.n_heads = num_heads
        self.n_points = n_points
        self.sampling_offsets = nn.Linear(config.d_model, num_heads * self.n_levels * n_points * 2)
        self.attention_weights = nn.Linear(config.d_model, num_heads * self.n_levels * n_points)
        self.value_proj = nn.Linear(config.d_model, config.d_model)
        self.output_proj = nn.Linear(config.d_model, config.d_model)
        self.disable_custom_kernels = config.disable_custom_kernels
        self._reset_parameters()
    def _reset_parameters(self):
        nn.init.constant_(self.sampling_offsets.weight.data, 0.0)
        default_dtype = torch.get_default_dtype()
        thetas = torch.arange(self.n_heads, dtype=torch.int64).to(default_dtype) * (2.0 * math.pi / self.n_heads)
        grid_init = torch.stack([thetas.cos(), thetas.sin()], -1)
        grid_init = ((grid_init / grid_init.abs().max(-1, keepdim=True)[0]).view(self.n_heads, 1, 1, 2).repeat(1, self.n_levels, self.n_points, 1))
        for i in range(self.n_points): grid_init[:, :, i, :] *= i + 1
        with torch.no_grad(): self.sampling_offsets.bias = nn.Parameter(grid_init.view(-1))
        nn.init.constant_(self.attention_weights.weight.data, 0.0)
        nn.init.constant_(self.attention_weights.bias.data, 0.0)
        nn.init.xavier_uniform_(self.value_proj.weight.data)
        nn.init.constant_(self.value_proj.bias.data, 0.0)
        nn.init.xavier_uniform_(self.output_proj.weight.data)
        nn.init.constant_(self.output_proj.bias.data, 0.0)
    def with_pos_embed(self, tensor: torch.Tensor, position_embeddings: Optional[Tensor]): return tensor if position_embeddings is None else tensor + position_embeddings
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, encoder_hidden_states=None, encoder_attention_mask=None, position_embeddings: Optional[torch.Tensor] = None,
    reference_points=None, spatial_shapes=None, level_start_index=None, output_attentions: bool = False):
        if position_embeddings is not None: hidden_states = self.with_pos_embed(hidden_states, position_embeddings)
        batch_size, num_queries, _ = hidden_states.shape
        batch_size, sequence_length, _ = encoder_hidden_states.shape
        if (spatial_shapes[:, 0] * spatial_shapes[:, 1]).sum() != sequence_length: raise ValueError("Make sure to align the spatial shapes with the sequence length of the encoder hidden states")
        value = self.value_proj(encoder_hidden_states)
        if attention_mask is not None: value = value.masked_fill(~attention_mask[..., None], float(0))
        value = value.view(batch_size, sequence_length, self.n_heads, self.d_model // self.n_heads)
        sampling_offsets = self.sampling_offsets(hidden_states).view(batch_size, num_queries, self.n_heads, self.n_levels, self.n_points, 2)
        attention_weights = self.attention_weights(hidden_states).view(batch_size, num_queries, self.n_heads, self.n_levels * self.n_points)
        attention_weights = F.softmax(attention_weights, -1).view(batch_size, num_queries, self.n_heads, self.n_levels, self.n_points)
        num_coordinates = reference_points.shape[-1]
        if num_coordinates == 2:
            offset_normalizer = torch.stack([spatial_shapes[..., 1], spatial_shapes[..., 0]], -1)
            sampling_locations = (reference_points[:, :, None, :, None, :] + sampling_offsets / offset_normalizer[None, None, None, :, None, :])
        elif num_coordinates == 4: sampling_locations = (reference_points[:, :, None, :, None, :2] + sampling_offsets / self.n_points * reference_points[:, :, None, :, None, 2:] * 0.5)
        else: raise ValueError(f"Last dim of reference_points must be 2 or 4, but got {reference_points.shape[-1]}")
        if self.disable_custom_kernels: output = multi_scale_deformable_attention(value, spatial_shapes, sampling_locations, attention_weights)
        else:
            try: output = MultiScaleDeformableAttentionFunction.apply(value, spatial_shapes, level_start_index, sampling_locations, attention_weights, self.im2col_step)
            except Exception: output = multi_scale_deformable_attention(value, spatial_shapes, sampling_locations, attention_weights)
        output = self.output_proj(output)
        return output, attention_weights
class GroundingDinoTextEnhancerLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.self_attn = GroundingDinoMultiheadAttention(config, num_attention_heads=config.encoder_attention_heads // 2)
        self.fc1 = nn.Linear(config.d_model, config.encoder_ffn_dim // 2)
        self.fc2 = nn.Linear(config.encoder_ffn_dim // 2, config.d_model)
        self.layer_norm_before = nn.LayerNorm(config.d_model, config.layer_norm_eps)
        self.layer_norm_after = nn.LayerNorm(config.d_model, config.layer_norm_eps)
        self.activation = ACT2FN[config.activation_function]
        self.num_heads = config.encoder_attention_heads // 2
        self.dropout = config.text_enhancer_dropout
    def with_pos_embed(self, hidden_state: Tensor, position_embeddings: Optional[Tensor]): return hidden_state if position_embeddings is None else hidden_state + position_embeddings
    def forward(self, hidden_states: torch.FloatTensor, attention_masks: Optional[torch.BoolTensor] = None, position_embeddings: Optional[torch.FloatTensor] = None) -> Tuple[torch.FloatTensor, torch.FloatTensor]:
        if attention_masks.dim() == 3 and attention_masks.shape[0] == hidden_states.shape[0]:
            attention_masks = attention_masks[:, None, :, :]
            attention_masks = attention_masks.repeat(1, self.num_heads, 1, 1)
            dtype = hidden_states.dtype
            attention_masks = attention_masks.to(dtype=dtype)
            attention_masks = (1.0 - attention_masks) * torch.finfo(dtype).min
        queries = keys = self.with_pos_embed(hidden_states, position_embeddings)
        attention_output, attention_weights = self.self_attn(queries=queries, keys=keys, values=hidden_states, attention_mask=attention_masks, output_attentions=True)
        attention_output = nn.functional.dropout(attention_output, p=self.dropout, training=self.training)
        hidden_states = hidden_states + attention_output
        hidden_states = self.layer_norm_before(hidden_states)
        residual = hidden_states
        hidden_states = self.activation(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = hidden_states + residual
        hidden_states = self.layer_norm_after(hidden_states)
        return hidden_states, attention_weights
class GroundingDinoBiMultiHeadAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        vision_dim = text_dim = config.d_model
        embed_dim = config.encoder_ffn_dim // 2
        num_heads = config.encoder_attention_heads // 2
        dropout = config.fusion_dropout
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.vision_dim = vision_dim
        self.text_dim = text_dim
        if self.head_dim * self.num_heads != self.embed_dim: raise ValueError(f"`embed_dim` must be divisible by `num_heads` (got `embed_dim`: {self.embed_dim} and `num_heads`: {self.num_heads}).")
        self.scale = self.head_dim ** (-0.5)
        self.dropout = dropout
        self.vision_proj = nn.Linear(self.vision_dim, self.embed_dim)
        self.text_proj = nn.Linear(self.text_dim, self.embed_dim)
        self.values_vision_proj = nn.Linear(self.vision_dim, self.embed_dim)
        self.values_text_proj = nn.Linear(self.text_dim, self.embed_dim)
        self.out_vision_proj = nn.Linear(self.embed_dim, self.vision_dim)
        self.out_text_proj = nn.Linear(self.embed_dim, self.text_dim)
    def _reshape(self, tensor: torch.Tensor, seq_len: int, batch_size: int): return tensor.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def forward(self, vision_features: torch.FloatTensor, text_features: torch.FloatTensor, vision_attention_mask: Optional[torch.BoolTensor] = None,
    text_attention_mask: Optional[torch.BoolTensor] = None) -> Tuple[Tuple[torch.FloatTensor, torch.FloatTensor], Tuple[torch.FloatTensor, torch.FloatTensor]]:
        batch_size, tgt_len, _ = vision_features.size()
        vision_query_states = self.vision_proj(vision_features) * self.scale
        vision_query_states = self._reshape(vision_query_states, tgt_len, batch_size)
        text_key_states = self.text_proj(text_features)
        text_key_states = self._reshape(text_key_states, -1, batch_size)
        vision_value_states = self.values_vision_proj(vision_features)
        vision_value_states = self._reshape(vision_value_states, -1, batch_size)
        text_value_states = self.values_text_proj(text_features)
        text_value_states = self._reshape(text_value_states, -1, batch_size)
        proj_shape = (batch_size * self.num_heads, -1, self.head_dim)
        vision_query_states = vision_query_states.view(*proj_shape)
        text_key_states = text_key_states.view(*proj_shape)
        vision_value_states = vision_value_states.view(*proj_shape)
        text_value_states = text_value_states.view(*proj_shape)
        src_len = text_key_states.size(1)
        attn_weights = torch.bmm(vision_query_states, text_key_states.transpose(1, 2))
        if attn_weights.size() != (batch_size * self.num_heads, tgt_len, src_len): raise ValueError(f"Attention weights should be of size {(batch_size * self.num_heads, tgt_len, src_len)}, but is {attn_weights.size()}")
        attn_weights = attn_weights - attn_weights.max()
        attn_weights = torch.clamp(attn_weights, min=-50000, max=50000)
        attn_weights_transposed = attn_weights.transpose(1, 2)
        text_attn_weights = attn_weights_transposed - torch.max(attn_weights_transposed, dim=-1, keepdim=True)[0]
        text_attn_weights = torch.clamp(text_attn_weights, min=-50000, max=50000)
        if vision_attention_mask is not None:
            vision_attention_mask = (vision_attention_mask[:, None, None, :].repeat(1, self.num_heads, 1, 1).flatten(0, 1))
            text_attn_weights.masked_fill_(vision_attention_mask, float("-inf"))
        text_attn_weights = text_attn_weights.softmax(dim=-1)
        if text_attention_mask is not None:
            text_attention_mask = text_attention_mask[:, None, None, :].repeat(1, self.num_heads, 1, 1).flatten(0, 1)
            attn_weights.masked_fill_(text_attention_mask, float("-inf"))
        vision_attn_weights = attn_weights.softmax(dim=-1)
        vision_attn_probs = F.dropout(vision_attn_weights, p=self.dropout, training=self.training)
        text_attn_probs = F.dropout(text_attn_weights, p=self.dropout, training=self.training)
        vision_attn_output = torch.bmm(vision_attn_probs, text_value_states)
        text_attn_output = torch.bmm(text_attn_probs, vision_value_states)
        if vision_attn_output.size() != (batch_size * self.num_heads, tgt_len, self.head_dim): raise ValueError(f"`vision_attn_output` should be of size {(batch_size, self.num_heads, tgt_len, self.head_dim)}, but is {vision_attn_output.size()}")
        if text_attn_output.size() != (batch_size * self.num_heads, src_len, self.head_dim): raise ValueError(f"`text_attn_output` should be of size {(batch_size, self.num_heads, src_len, self.head_dim)}, but is {text_attn_output.size()}")
        vision_attn_output = vision_attn_output.view(batch_size, self.num_heads, tgt_len, self.head_dim)
        vision_attn_output = vision_attn_output.transpose(1, 2)
        vision_attn_output = vision_attn_output.reshape(batch_size, tgt_len, self.embed_dim)
        text_attn_output = text_attn_output.view(batch_size, self.num_heads, src_len, self.head_dim)
        text_attn_output = text_attn_output.transpose(1, 2)
        text_attn_output = text_attn_output.reshape(batch_size, src_len, self.embed_dim)
        vision_attn_output = self.out_vision_proj(vision_attn_output)
        text_attn_output = self.out_text_proj(text_attn_output)
        return (vision_attn_output, vision_attn_weights), (text_attn_output, text_attn_weights)
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training: return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class GroundingDinoDropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str: return "p={}".format(self.drop_prob)
class GroundingDinoFusionLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        drop_path = config.fusion_droppath
        self.layer_norm_vision = nn.LayerNorm(config.d_model, config.layer_norm_eps)
        self.layer_norm_text = nn.LayerNorm(config.d_model, config.layer_norm_eps)
        self.attn = GroundingDinoBiMultiHeadAttention(config)
        self.drop_path = GroundingDinoDropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        init_values = 1e-4
        self.vision_param = nn.Parameter(init_values * torch.ones((config.d_model)), requires_grad=True)
        self.text_param = nn.Parameter(init_values * torch.ones((config.d_model)), requires_grad=True)
    def forward(self, vision_features: torch.FloatTensor, text_features: torch.FloatTensor, attention_mask_vision: Optional[torch.BoolTensor] = None,
    attention_mask_text: Optional[torch.BoolTensor] = None) -> Tuple[Tuple[torch.FloatTensor, torch.FloatTensor], Tuple[torch.FloatTensor, torch.FloatTensor]]:
        vision_features = self.layer_norm_vision(vision_features)
        text_features = self.layer_norm_text(text_features)
        (delta_v, vision_attn), (delta_t, text_attn) = self.attn(vision_features, text_features, vision_attention_mask=attention_mask_vision, text_attention_mask=attention_mask_text)
        vision_features = vision_features + self.drop_path(self.vision_param * delta_v)
        text_features = text_features + self.drop_path(self.text_param * delta_t)
        return (vision_features, vision_attn), (text_features, text_attn)
class GroundingDinoDeformableLayer(nn.Module):
    def __init__(self, config: GroundingDinoConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = GroundingDinoMultiscaleDeformableAttention(config, num_heads=config.encoder_attention_heads, n_points=config.encoder_n_points)
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(self.embed_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, position_embeddings: torch.Tensor = None, reference_points=None, spatial_shapes=None,
    level_start_index=None, output_attentions: bool = False):
        residual = hidden_states
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, encoder_hidden_states=hidden_states, encoder_attention_mask=attention_mask,
        position_embeddings=position_embeddings, reference_points=reference_points, spatial_shapes=spatial_shapes, level_start_index=level_start_index, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        if self.training:
            if torch.isinf(hidden_states).any() or torch.isnan(hidden_states).any():
                clamp_value = torch.finfo(hidden_states.dtype).max - 1000
                hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        return hidden_states, attn_weights
def get_sine_pos_embed(pos_tensor: torch.Tensor, num_pos_feats: int = 128, temperature: int = 10000, exchange_xy: bool = True) -> Tensor:
    scale = 2 * math.pi
    dim_t = torch.arange(num_pos_feats, dtype=torch.float32, device=pos_tensor.device)
    dim_t = temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / num_pos_feats)
    def sine_func(x: torch.Tensor):
        sin_x = x * scale / dim_t
        sin_x = torch.stack((sin_x[..., 0::2].sin(), sin_x[..., 1::2].cos()), dim=3).flatten(2)
        return sin_x
    pos_tensor = pos_tensor.split([1] * pos_tensor.shape[-1], dim=-1)
    position_embeddings = [sine_func(x) for x in pos_tensor]
    if exchange_xy: position_embeddings[0], position_embeddings[1] = position_embeddings[1], position_embeddings[0]
    position_embeddings = torch.cat(position_embeddings, dim=-1)
    return position_embeddings
class GroundingDinoEncoderLayer(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.d_model = config.d_model
        self.text_enhancer_layer = GroundingDinoTextEnhancerLayer(config)
        self.fusion_layer = GroundingDinoFusionLayer(config)
        self.deformable_layer = GroundingDinoDeformableLayer(config)
    def get_text_position_embeddings(self, text_features: Tensor, text_position_embedding: Optional[torch.Tensor], text_position_ids: Optional[torch.Tensor]) -> Tensor:
        batch_size, seq_length, _ = text_features.shape
        if text_position_embedding is None and text_position_ids is None:
            text_position_embedding = torch.arange(seq_length, device=text_features.device)
            text_position_embedding = text_position_embedding.float()
            text_position_embedding = text_position_embedding.unsqueeze(0).unsqueeze(-1)
            text_position_embedding = text_position_embedding.repeat(batch_size, 1, 1)
            text_position_embedding = get_sine_pos_embed(text_position_embedding, num_pos_feats=self.d_model, exchange_xy=False)
        if text_position_ids is not None: text_position_embedding = get_sine_pos_embed(text_position_ids[..., None], num_pos_feats=self.d_model, exchange_xy=False)
        return text_position_embedding
    def forward(self, vision_features: Tensor, vision_position_embedding: Tensor, spatial_shapes: Tensor, level_start_index: Tensor, key_padding_mask: Tensor,
    reference_points: Tensor, text_features: Optional[Tensor] = None, text_attention_mask: Optional[Tensor] = None, text_position_embedding: Optional[Tensor] = None,
    text_self_attention_masks: Optional[Tensor] = None, text_position_ids: Optional[Tensor] = None):
        text_position_embedding = self.get_text_position_embeddings(text_features, text_position_embedding, text_position_ids)
        (vision_features, vision_fused_attn), (text_features, text_fused_attn) = self.fusion_layer(vision_features=vision_features, text_features=text_features,
        attention_mask_vision=key_padding_mask, attention_mask_text=text_attention_mask)
        (text_features, text_enhanced_attn) = self.text_enhancer_layer(hidden_states=text_features, attention_masks=~text_self_attention_masks, position_embeddings=(text_position_embedding if text_position_embedding is not None else None))
        (vision_features, vision_deformable_attn) = self.deformable_layer(hidden_states=vision_features, attention_mask=~key_padding_mask, position_embeddings=vision_position_embedding,
        reference_points=reference_points, spatial_shapes=spatial_shapes, level_start_index=level_start_index)
        return ((vision_features, text_features), (vision_fused_attn, text_fused_attn, text_enhanced_attn, vision_deformable_attn))
class GroundingDinoMultiheadAttention(nn.Module):
    def __init__(self, config, num_attention_heads=None):
        super().__init__()
        if config.hidden_size % num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size ({config.hidden_size}) is not a multiple of the number of attention heads ({num_attention_heads})")
        self.num_attention_heads = num_attention_heads
        self.attention_head_size = int(config.hidden_size / num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)
        self.out_proj = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.attention_dropout)
    def transpose_for_scores(self, x: torch.Tensor) -> torch.Tensor:
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(new_x_shape)
        return x.permute(0, 2, 1, 3)
    def forward(self, queries: torch.Tensor, keys: torch.Tensor, values: torch.Tensor, attention_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor]:
        query_layer = self.transpose_for_scores(self.query(queries))
        key_layer = self.transpose_for_scores(self.key(keys))
        value_layer = self.transpose_for_scores(self.value(values))
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(new_context_layer_shape)
        context_layer = self.out_proj(context_layer)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        return outputs
class GroundingDinoDecoderLayer(nn.Module):
    def __init__(self, config: GroundingDinoConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = GroundingDinoMultiheadAttention(config, num_attention_heads=config.decoder_attention_heads)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
        self.encoder_attn_text = GroundingDinoMultiheadAttention(config, num_attention_heads=config.decoder_attention_heads)
        self.encoder_attn_text_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
        self.encoder_attn = GroundingDinoMultiscaleDeformableAttention(config, num_heads=config.decoder_attention_heads, n_points=config.decoder_n_points)
        self.encoder_attn_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
        self.fc1 = nn.Linear(self.embed_dim, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim, config.layer_norm_eps)
    def with_pos_embed(self, tensor: torch.Tensor, position_embeddings: Optional[Tensor]): return tensor if position_embeddings is None else tensor + position_embeddings
    def forward(self, hidden_states: torch.Tensor, position_embeddings: Optional[torch.Tensor] = None, reference_points=None, spatial_shapes=None, level_start_index=None,
    vision_encoder_hidden_states: Optional[torch.Tensor] = None, vision_encoder_attention_mask: Optional[torch.Tensor] = None, text_encoder_hidden_states: Optional[torch.Tensor] = None,
    text_encoder_attention_mask: Optional[torch.Tensor] = None, self_attn_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False):
        residual = hidden_states
        queries = keys = self.with_pos_embed(hidden_states, position_embeddings)
        hidden_states, self_attn_weights = self.self_attn(queries=queries, keys=keys, values=hidden_states, attention_mask=self_attn_mask, output_attentions=True)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        second_residual = hidden_states
        queries = self.with_pos_embed(hidden_states, position_embeddings)
        hidden_states, text_cross_attn_weights = self.encoder_attn_text(queries=queries, keys=text_encoder_hidden_states, values=text_encoder_hidden_states, attention_mask=text_encoder_attention_mask, output_attentions=True)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = second_residual + hidden_states
        hidden_states = self.encoder_attn_text_layer_norm(hidden_states)
        third_residual = hidden_states
        cross_attn_weights = None
        hidden_states, cross_attn_weights = self.encoder_attn(hidden_states=hidden_states, attention_mask=vision_encoder_attention_mask, encoder_hidden_states=vision_encoder_hidden_states,
        encoder_attention_mask=vision_encoder_attention_mask, position_embeddings=position_embeddings, reference_points=reference_points, spatial_shapes=spatial_shapes,
        level_start_index=level_start_index, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = third_residual + hidden_states
        hidden_states = self.encoder_attn_layer_norm(hidden_states)
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights, text_cross_attn_weights, cross_attn_weights)
        return outputs
class GroundingDinoContrastiveEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.max_text_len = config.max_text_len
    def forward(self, vision_hidden_state: torch.FloatTensor, text_hidden_state: torch.FloatTensor, text_token_mask: torch.BoolTensor) -> torch.FloatTensor:
        output = vision_hidden_state @ text_hidden_state.transpose(-1, -2)
        output = output.masked_fill(~text_token_mask[:, None, :], float("-inf"))
        new_output = torch.full((*output.shape[:-1], self.max_text_len), float("-inf"), device=output.device)
        new_output[..., : output.shape[-1]] = output
        return new_output
class GroundingDinoPreTrainedModel(PreTrainedModel):
    config_class = GroundingDinoConfig
    base_model_prefix = "model"
    main_input_name = "pixel_values"
    def _init_weights(self, module):
        std = self.config.init_std
        if isinstance(module, GroundingDinoLearnedPositionEmbedding):
            nn.init.uniform_(module.row_embeddings.weight)
            nn.init.uniform_(module.column_embeddings.weight)
        elif isinstance(module, GroundingDinoMultiscaleDeformableAttention): module._reset_parameters()
        elif isinstance(module, GroundingDinoBiMultiHeadAttention):
            nn.init.xavier_uniform_(module.vision_proj.weight)
            module.vision_proj.bias.data.fill_(0)
            nn.init.xavier_uniform_(module.text_proj.weight)
            module.text_proj.bias.data.fill_(0)
            nn.init.xavier_uniform_(module.values_vision_proj.weight)
            module.values_vision_proj.bias.data.fill_(0)
            nn.init.xavier_uniform_(module.values_text_proj.weight)
            module.values_text_proj.bias.data.fill_(0)
            nn.init.xavier_uniform_(module.out_vision_proj.weight)
            module.out_vision_proj.bias.data.fill_(0)
            nn.init.xavier_uniform_(module.out_text_proj.weight)
            module.out_text_proj.bias.data.fill_(0)
        elif isinstance(module, (GroundingDinoEncoderLayer, GroundingDinoDecoderLayer)):
            for p in module.parameters():
                if p.dim() > 1: nn.init.normal_(p, mean=0.0, std=std)
        elif isinstance(module, (nn.Linear, nn.Conv2d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, GroundingDinoMLPPredictionHead):
            nn.init.constant_(module.layers[-1].weight.data, 0)
            nn.init.constant_(module.layers[-1].bias.data, 0)
        if hasattr(module, "reference_points") and not self.config.two_stage:
            nn.init.xavier_uniform_(module.reference_points.weight.data, gain=1.0)
            nn.init.constant_(module.reference_points.bias.data, 0.0)
        if hasattr(module, "level_embed"): nn.init.normal_(module.level_embed)
    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, GroundingDinoDecoder): module.gradient_checkpointing = value
GROUNDING_DINO_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`GroundingDinoConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
GROUNDING_DINO_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it.
            Pixel values can be obtained using [`AutoImageProcessor`]. See [`GroundingDinoImageProcessor.__call__`] for
            details.
        input_ids (`torch.LongTensor` of shape `(batch_size, text_sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`BertTokenizer.__call__`] for details.
        token_type_ids (`torch.LongTensor` of shape `(batch_size, text_sequence_length)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`: 0 corresponds to a `sentence A` token, 1 corresponds to a `sentence B` token
            [What are token type IDs?](../glossary#token-type-ids)
        attention_mask (`torch.LongTensor` of shape `(batch_size, text_sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are real (i.e. *not masked*),
            - 0 for tokens that are padding (i.e. *masked*).
            [What are attention masks?](../glossary#attention-mask)
        pixel_mask (`torch.LongTensor` of shape `(batch_size, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            [What are attention masks?](../glossary#attention-mask)
        encoder_outputs (`tuple(tuple(torch.FloatTensor)`, *optional*):
            Tuple consists of (`last_hidden_state_vision`, *optional*: `last_hidden_state_text`, *optional*:
            `vision_hidden_states`, *optional*: `text_hidden_states`, *optional*: `attentions`)
            `last_hidden_state_vision` of shape `(batch_size, sequence_length, hidden_size)`, *optional*) is a sequence
            of hidden-states at the output of the last layer of the encoder. Used in the cross-attention of the
            decoder.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
class GroundingDinoEncoder(GroundingDinoPreTrainedModel):
    def __init__(self, config: GroundingDinoConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layers = nn.ModuleList([GroundingDinoEncoderLayer(config) for _ in range(config.encoder_layers)])
        self.post_init()
    @staticmethod
    def get_reference_points(spatial_shapes, valid_ratios, device):
        reference_points_list = []
        for level, (height, width) in enumerate(spatial_shapes):
            ref_y, ref_x = meshgrid(torch.linspace(0.5, height - 0.5, height, dtype=torch.float32, device=device), torch.linspace(0.5, width - 0.5, width, dtype=torch.float32, device=device), indexing="ij")
            ref_y = ref_y.reshape(-1)[None] / (valid_ratios[:, None, level, 1] * height)
            ref_x = ref_x.reshape(-1)[None] / (valid_ratios[:, None, level, 0] * width)
            ref = torch.stack((ref_x, ref_y), -1)
            reference_points_list.append(ref)
        reference_points = torch.cat(reference_points_list, 1)
        reference_points = reference_points[:, :, None] * valid_ratios[:, None]
        return reference_points
    def forward(self, vision_features: Tensor, vision_attention_mask: Tensor, vision_position_embedding: Tensor, spatial_shapes: Tensor, level_start_index: Tensor,
    valid_ratios=None, text_features: Optional[Tensor] = None, text_attention_mask: Optional[Tensor] = None, text_position_embedding: Optional[Tensor] = None,
    text_self_attention_masks: Optional[Tensor] = None, text_position_ids: Optional[Tensor] = None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        reference_points = self.get_reference_points(spatial_shapes, valid_ratios, device=vision_features.device)
        encoder_vision_states = () if output_hidden_states else None
        encoder_text_states = () if output_hidden_states else None
        all_attns = () if output_attentions else None
        all_attn_fused_text = () if output_attentions else None
        all_attn_fused_vision = () if output_attentions else None
        all_attn_enhanced_text = () if output_attentions else None
        all_attn_deformable = () if output_attentions else None
        for i, encoder_layer in enumerate(self.layers):
            if output_hidden_states:
                encoder_vision_states += (vision_features,)
                encoder_text_states += (text_features,)
            (vision_features, text_features), attentions = encoder_layer(vision_features=vision_features, vision_position_embedding=vision_position_embedding,
            spatial_shapes=spatial_shapes, level_start_index=level_start_index, key_padding_mask=vision_attention_mask, reference_points=reference_points,
            text_features=text_features, text_attention_mask=text_attention_mask, text_position_embedding=text_position_embedding,
            text_self_attention_masks=text_self_attention_masks, text_position_ids=text_position_ids)
            if output_attentions:
                all_attn_fused_vision += (attentions[0],)
                all_attn_fused_text += (attentions[1],)
                all_attn_enhanced_text += (attentions[2],)
                all_attn_deformable += (attentions[3],)
        if output_hidden_states:
            encoder_vision_states += (vision_features,)
            encoder_text_states += (text_features,)
        if output_attentions: all_attns = (all_attn_fused_vision, all_attn_fused_text, all_attn_enhanced_text, all_attn_deformable)
        if not return_dict:
            enc_outputs = [vision_features, text_features, encoder_vision_states, encoder_text_states, all_attns]
            return tuple(v for v in enc_outputs if v is not None)
        return GroundingDinoEncoderOutput(last_hidden_state_vision=vision_features, last_hidden_state_text=text_features, vision_hidden_states=encoder_vision_states,
        text_hidden_states=encoder_text_states, attentions=all_attns)
class GroundingDinoDecoder(GroundingDinoPreTrainedModel):
    def __init__(self, config: GroundingDinoConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layer_norm = nn.LayerNorm(config.d_model, config.layer_norm_eps)
        self.layers = nn.ModuleList([GroundingDinoDecoderLayer(config) for _ in range(config.decoder_layers)])
        self.reference_points_head = GroundingDinoMLPPredictionHead(config.query_dim // 2 * config.d_model, config.d_model, config.d_model, 2)
        self.gradient_checkpointing = False
        self.bbox_embed = None
        self.class_embed = None
        self.query_scale = None
        self.post_init()
    def forward(self, inputs_embeds, vision_encoder_hidden_states, vision_encoder_attention_mask=None, text_encoder_hidden_states=None, text_encoder_attention_mask=None,
    reference_points=None, spatial_shapes=None, level_start_index=None, valid_ratios=None, self_attn_mask=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is not None: hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_attns = () if output_attentions else None
        all_cross_attns_vision = () if (output_attentions and vision_encoder_hidden_states is not None) else None
        all_cross_attns_text = () if (output_attentions and text_encoder_hidden_states is not None) else None
        intermediate = ()
        intermediate_reference_points = ()
        if text_encoder_attention_mask is not None:
            dtype = text_encoder_hidden_states.dtype
            text_encoder_attention_mask = text_encoder_attention_mask[:, None, None, :]
            text_encoder_attention_mask = text_encoder_attention_mask.repeat(1, self.config.decoder_attention_heads, self.config.num_queries, 1)
            text_encoder_attention_mask = text_encoder_attention_mask.to(dtype=dtype)
            text_encoder_attention_mask = text_encoder_attention_mask * torch.finfo(dtype).min
        for idx, decoder_layer in enumerate(self.layers):
            num_coordinates = reference_points.shape[-1]
            if num_coordinates == 4: reference_points_input = (reference_points[:, :, None] * torch.cat([valid_ratios, valid_ratios], -1)[:, None])
            elif num_coordinates == 2: reference_points_input = reference_points[:, :, None] * valid_ratios[:, None]
            else: raise ValueError("Last dim of reference_points must be 2 or 4, but got {reference_points.shape[-1]}")
            query_pos = get_sine_pos_embed(reference_points_input[:, :, 0, :], num_pos_feats=self.config.d_model // 2)
            query_pos = self.reference_points_head(query_pos)
            if output_hidden_states: all_hidden_states += (self.layer_norm(hidden_states),)
            if self.gradient_checkpointing and self.training:
                def create_custom_forward(module):
                    def custom_forward(*inputs): return module(*inputs, output_attentions)
                    return custom_forward
                layer_outputs = torch.utils.checkpoint.checkpoint(create_custom_forward(decoder_layer), hidden_states, query_pos, reference_points_input, spatial_shapes,
                level_start_index, vision_encoder_hidden_states, vision_encoder_attention_mask, text_encoder_hidden_states, text_encoder_attention_mask, self_attn_mask, None)
            else:
                layer_outputs = decoder_layer(hidden_states=hidden_states, position_embeddings=query_pos, reference_points=reference_points_input, spatial_shapes=spatial_shapes,
                level_start_index=level_start_index, vision_encoder_hidden_states=vision_encoder_hidden_states, vision_encoder_attention_mask=vision_encoder_attention_mask,
                text_encoder_hidden_states=text_encoder_hidden_states, text_encoder_attention_mask=text_encoder_attention_mask, self_attn_mask=self_attn_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if self.bbox_embed is not None:
                tmp = self.bbox_embed[idx](hidden_states)
                num_coordinates = reference_points.shape[-1]
                if num_coordinates == 4:
                    new_reference_points = tmp + torch.special.logit(reference_points, eps=1e-5)
                    new_reference_points = new_reference_points.sigmoid()
                elif num_coordinates == 2:
                    new_reference_points = tmp
                    new_reference_points[..., :2] = tmp[..., :2] + torch.special.logit(reference_points, eps=1e-5)
                    new_reference_points = new_reference_points.sigmoid()
                else: raise ValueError(f"Last dim of reference_points must be 2 or 4, but got {reference_points.shape[-1]}")
                reference_points = new_reference_points.detach()
            intermediate += (self.layer_norm(hidden_states),)
            intermediate_reference_points += (reference_points,)
            if output_attentions:
                all_self_attns += (layer_outputs[1],)
                if text_encoder_hidden_states is not None: all_cross_attns_text += (layer_outputs[2],)
                if vision_encoder_hidden_states is not None: all_cross_attns_vision += (layer_outputs[3],)
        intermediate = torch.stack(intermediate, dim=1)
        intermediate_reference_points = torch.stack(intermediate_reference_points, dim=1)
        hidden_states = self.layer_norm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        if output_attentions: all_attns += (all_self_attns, all_cross_attns_text, all_cross_attns_vision)
        if not return_dict: return tuple(v for v in [hidden_states, intermediate, intermediate_reference_points, all_hidden_states, all_attns] if v is not None)
        return GroundingDinoDecoderOutput(last_hidden_state=hidden_states, intermediate_hidden_states=intermediate, intermediate_reference_points=intermediate_reference_points,
        hidden_states=all_hidden_states, attentions=all_attns)
SPECIAL_TOKENS = [101, 102, 1012, 1029]
def generate_masks_with_special_tokens_and_transfer_map(input_ids: torch.LongTensor) -> Tuple[Tensor, Tensor]:
    batch_size, num_token = input_ids.shape
    special_tokens_mask = torch.zeros((batch_size, num_token), device=input_ids.device).bool()
    for special_token in SPECIAL_TOKENS: special_tokens_mask |= input_ids == special_token
    idxs = torch.nonzero(special_tokens_mask)
    attention_mask = torch.eye(num_token, device=input_ids.device).bool().unsqueeze(0).repeat(batch_size, 1, 1)
    position_ids = torch.zeros((batch_size, num_token), device=input_ids.device)
    previous_col = 0
    for i in range(idxs.shape[0]):
        row, col = idxs[i]
        if (col == 0) or (col == num_token - 1):
            attention_mask[row, col, col] = True
            position_ids[row, col] = 0
        else:
            attention_mask[row, previous_col + 1 : col + 1, previous_col + 1 : col + 1] = True
            position_ids[row, previous_col + 1 : col + 1] = torch.arange(0, col - previous_col, device=input_ids.device)
        previous_col = col
    return attention_mask, position_ids.to(torch.long)
@add_start_docstrings("The bare Grounding DINO Model (consisting of a backbone and encoder-decoder Transformer) outputting raw hidden-states without any specific head on top.", GROUNDING_DINO_START_DOCSTRING)
class GroundingDinoModel(GroundingDinoPreTrainedModel):
    def __init__(self, config: GroundingDinoConfig):
        super().__init__(config)
        backbone = GroundingDinoConvEncoder(config)
        position_embeddings = build_position_encoding(config)
        self.backbone = GroundingDinoConvModel(backbone, position_embeddings)
        if config.num_feature_levels > 1:
            num_backbone_outs = len(backbone.intermediate_channel_sizes)
            input_proj_list = []
            for i in range(num_backbone_outs):
                in_channels = backbone.intermediate_channel_sizes[i]
                input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=1), nn.GroupNorm(32, config.d_model)))
            for _ in range(config.num_feature_levels - num_backbone_outs):
                input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=3, stride=2, padding=1), nn.GroupNorm(32, config.d_model)))
                in_channels = config.d_model
            self.input_proj_vision = nn.ModuleList(input_proj_list)
        else: self.input_proj_vision = nn.ModuleList([nn.Sequential(nn.Conv2d(backbone.intermediate_channel_sizes[-1], config.d_model, kernel_size=1), nn.GroupNorm(32, config.d_model))])
        self.text_backbone = AutoModel.from_config(config.text_config, add_pooling_layer=False, attn_implementation=config._attn_implementation)
        self.text_projection = nn.Linear(config.text_config.hidden_size, config.d_model)
        if config.embedding_init_target or not config.two_stage: self.query_position_embeddings = nn.Embedding(config.num_queries, config.d_model)
        self.encoder = GroundingDinoEncoder(config)
        self.decoder = GroundingDinoDecoder(config)
        self.level_embed = nn.Parameter(torch.Tensor(config.num_feature_levels, config.d_model))
        if config.two_stage:
            self.enc_output = nn.Linear(config.d_model, config.d_model)
            self.enc_output_norm = nn.LayerNorm(config.d_model, config.layer_norm_eps)
            if (config.two_stage_bbox_embed_share and config.decoder_bbox_embed_share and self.decoder.bbox_embed is not None): self.encoder_output_bbox_embed = self.decoder.bbox_embed
            else: self.encoder_output_bbox_embed = GroundingDinoMLPPredictionHead(input_dim=config.d_model, hidden_dim=config.d_model, output_dim=4, num_layers=3)
            self.encoder_output_class_embed = GroundingDinoContrastiveEmbedding(config)
        else: self.reference_points = nn.Embedding(config.num_queries, 4)
        self.post_init()
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def freeze_backbone(self):
        for name, param in self.backbone.conv_encoder.model.named_parameters(): param.requires_grad_(False)
    def unfreeze_backbone(self):
        for name, param in self.backbone.conv_encoder.model.named_parameters(): param.requires_grad_(True)
    def get_valid_ratio(self, mask):
        _, height, width = mask.shape
        valid_height = torch.sum(mask[:, :, 0], 1)
        valid_width = torch.sum(mask[:, 0, :], 1)
        valid_ratio_heigth = valid_height.float() / height
        valid_ratio_width = valid_width.float() / width
        valid_ratio = torch.stack([valid_ratio_width, valid_ratio_heigth], -1)
        return valid_ratio
    def generate_encoder_output_proposals(self, enc_output, padding_mask, spatial_shapes):
        batch_size = enc_output.shape[0]
        proposals = []
        current_position = 0
        for level, (height, width) in enumerate(spatial_shapes):
            mask_flatten_ = padding_mask[:, current_position : (current_position + height * width)]
            mask_flatten_ = mask_flatten_.view(batch_size, height, width, 1)
            valid_height = torch.sum(~mask_flatten_[:, :, 0, 0], 1)
            valid_width = torch.sum(~mask_flatten_[:, 0, :, 0], 1)
            grid_y, grid_x = meshgrid(torch.linspace(0, height - 1, height, dtype=torch.float32, device=enc_output.device), torch.linspace(0, width - 1, width, dtype=torch.float32, device=enc_output.device), indexing="ij")
            grid = torch.cat([grid_x.unsqueeze(-1), grid_y.unsqueeze(-1)], -1)
            scale = torch.cat([valid_width.unsqueeze(-1), valid_height.unsqueeze(-1)], 1).view(batch_size, 1, 1, 2)
            grid = (grid.unsqueeze(0).expand(batch_size, -1, -1, -1) + 0.5) / scale
            width_heigth = torch.ones_like(grid) * 0.05 * (2.0**level)
            proposal = torch.cat((grid, width_heigth), -1).view(batch_size, -1, 4)
            proposals.append(proposal)
            current_position += height * width
        output_proposals = torch.cat(proposals, 1)
        output_proposals_valid = ((output_proposals > 0.01) & (output_proposals < 0.99)).all(-1, keepdim=True)
        output_proposals = torch.log(output_proposals / (1 - output_proposals))
        output_proposals = output_proposals.masked_fill(padding_mask.unsqueeze(-1), float("inf"))
        output_proposals = output_proposals.masked_fill(~output_proposals_valid, float("inf"))
        object_query = enc_output
        object_query = object_query.masked_fill(padding_mask.unsqueeze(-1), float(0))
        object_query = object_query.masked_fill(~output_proposals_valid, float(0))
        object_query = self.enc_output_norm(self.enc_output(object_query))
        return object_query, output_proposals
    @add_start_docstrings_to_model_forward(GROUNDING_DINO_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Tensor, input_ids: Tensor, token_type_ids: Optional[Tensor] = None, attention_mask: Optional[Tensor] = None, pixel_mask: Optional[Tensor] = None,
    encoder_outputs=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        text_self_attention_masks, position_ids = generate_masks_with_special_tokens_and_transfer_map(input_ids)
        if attention_mask is None: attention_mask = torch.ones_like(input_ids)
        if token_type_ids is None: token_type_ids = torch.zeros_like(input_ids)
        text_token_mask = attention_mask.bool()
        max_text_len = self.config.max_text_len
        if text_self_attention_masks.shape[1] > max_text_len:
            text_self_attention_masks = text_self_attention_masks[:, :max_text_len, :max_text_len]
            position_ids = position_ids[:, :max_text_len]
            input_ids = input_ids[:, :max_text_len]
            token_type_ids = token_type_ids[:, :max_text_len]
            text_token_mask = text_token_mask[:, :max_text_len]
        text_outputs = self.text_backbone(input_ids, text_self_attention_masks, token_type_ids, position_ids, return_dict=return_dict)
        text_features = text_outputs.last_hidden_state if return_dict else text_outputs[0]
        text_features = self.text_projection(text_features)
        batch_size, num_channels, height, width = pixel_values.shape
        device = pixel_values.device
        if pixel_mask is None: pixel_mask = torch.ones(((batch_size, height, width)), dtype=torch.long, device=device)
        vision_features, position_embeddings_list = self.backbone(pixel_values, pixel_mask)
        feature_maps = []
        masks = []
        for level, (source, mask) in enumerate(vision_features):
            feature_maps.append(self.input_proj_vision[level](source))
            masks.append(mask)
        if self.config.num_feature_levels > len(feature_maps):
            _len_sources = len(feature_maps)
            for level in range(_len_sources, self.config.num_feature_levels):
                if level == _len_sources: source = self.input_proj_vision[level](vision_features[-1][0])
                else: source = self.input_proj_vision[level](feature_maps[-1])
                mask = nn.functional.interpolate(pixel_mask[None].float(), size=source.shape[-2:]).to(torch.bool)[0]
                pos_l = self.backbone.position_embedding(source, mask).to(source.dtype)
                feature_maps.append(source)
                masks.append(mask)
                position_embeddings_list.append(pos_l)
        query_embeds = None
        if self.config.embedding_init_target or self.config.two_stage: query_embeds = self.query_position_embeddings.weight
        source_flatten = []
        mask_flatten = []
        lvl_pos_embed_flatten = []
        spatial_shapes = []
        for level, (source, mask, pos_embed) in enumerate(zip(feature_maps, masks, position_embeddings_list)):
            batch_size, num_channels, height, width = source.shape
            spatial_shape = (height, width)
            spatial_shapes.append(spatial_shape)
            source = source.flatten(2).transpose(1, 2)
            mask = mask.flatten(1)
            pos_embed = pos_embed.flatten(2).transpose(1, 2)
            lvl_pos_embed = pos_embed + self.level_embed[level].view(1, 1, -1)
            lvl_pos_embed_flatten.append(lvl_pos_embed)
            source_flatten.append(source)
            mask_flatten.append(mask)
        source_flatten = torch.cat(source_flatten, 1)
        mask_flatten = torch.cat(mask_flatten, 1)
        lvl_pos_embed_flatten = torch.cat(lvl_pos_embed_flatten, 1)
        spatial_shapes = torch.as_tensor(spatial_shapes, dtype=torch.long, device=source_flatten.device)
        level_start_index = torch.cat((spatial_shapes.new_zeros((1,)), spatial_shapes.prod(1).cumsum(0)[:-1]))
        valid_ratios = torch.stack([self.get_valid_ratio(m) for m in masks], 1)
        valid_ratios = valid_ratios.float()
        if encoder_outputs is None:
            encoder_outputs = self.encoder(vision_features=source_flatten, vision_attention_mask=~mask_flatten, vision_position_embedding=lvl_pos_embed_flatten,
            spatial_shapes=spatial_shapes, level_start_index=level_start_index, valid_ratios=valid_ratios, text_features=text_features, text_attention_mask=~text_token_mask,
            text_position_embedding=None, text_self_attention_masks=~text_self_attention_masks, text_position_ids=position_ids, output_attentions=output_attentions,
            output_hidden_states=output_hidden_states, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, GroundingDinoEncoderOutput):
            encoder_outputs = GroundingDinoEncoderOutput(last_hidden_state_vision=encoder_outputs[0], last_hidden_state_text=encoder_outputs[1], vision_hidden_states=encoder_outputs[2] if output_hidden_states else None,
            text_hidden_states=encoder_outputs[3] if output_hidden_states else None, attentions=encoder_outputs[-1] if output_attentions else None)
        enc_outputs_class = None
        enc_outputs_coord_logits = None
        if self.config.two_stage:
            object_query_embedding, output_proposals = self.generate_encoder_output_proposals(encoder_outputs[0], ~mask_flatten, spatial_shapes)
            enc_outputs_class = self.encoder_output_class_embed(object_query_embedding, encoder_outputs[1], text_token_mask)
            delta_bbox = self.encoder_output_bbox_embed(object_query_embedding)
            enc_outputs_coord_logits = delta_bbox + output_proposals
            topk = self.config.num_queries
            topk_logits = enc_outputs_class.max(-1)[0]
            topk_proposals = torch.topk(topk_logits, topk, dim=1)[1]
            topk_coords_logits = torch.gather(enc_outputs_coord_logits, 1, topk_proposals.unsqueeze(-1).repeat(1, 1, 4))
            topk_coords_logits = topk_coords_logits.detach()
            reference_points = topk_coords_logits.sigmoid()
            init_reference_points = reference_points
            if query_embeds is not None: target = query_embeds.unsqueeze(0).repeat(batch_size, 1, 1)
            else: target = torch.gather(object_query_embedding, 1, topk_proposals.unsqueeze(-1).repeat(1, 1, self.d_model)).detach()
        else:
            target = query_embeds.unsqueeze(0).repeat(batch_size, 1, 1)
            reference_points = self.reference_points.weight.unsqueeze(0).repeat(batch_size, 1, 1).sigmoid()
            init_reference_points = reference_points
        decoder_outputs = self.decoder(inputs_embeds=target, vision_encoder_hidden_states=encoder_outputs[0], vision_encoder_attention_mask=mask_flatten,
        text_encoder_hidden_states=encoder_outputs[1], text_encoder_attention_mask=~text_token_mask, reference_points=reference_points, spatial_shapes=spatial_shapes,
        level_start_index=level_start_index, valid_ratios=valid_ratios, self_attn_mask=None, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        if not return_dict:
            enc_outputs = tuple(value for value in [enc_outputs_class, enc_outputs_coord_logits] if value is not None)
            tuple_outputs = ((decoder_outputs[0], init_reference_points) + decoder_outputs[1:] + encoder_outputs + enc_outputs)
            return tuple_outputs
        return GroundingDinoModelOutput(last_hidden_state=decoder_outputs.last_hidden_state, init_reference_points=init_reference_points, intermediate_hidden_states=decoder_outputs.intermediate_hidden_states,
        intermediate_reference_points=decoder_outputs.intermediate_reference_points, decoder_hidden_states=decoder_outputs.hidden_states, decoder_attentions=decoder_outputs.attentions,
        encoder_last_hidden_state_vision=encoder_outputs.last_hidden_state_vision, encoder_last_hidden_state_text=encoder_outputs.last_hidden_state_text, encoder_vision_hidden_states=encoder_outputs.vision_hidden_states,
        encoder_text_hidden_states=encoder_outputs.text_hidden_states, encoder_attentions=encoder_outputs.attentions, enc_outputs_class=enc_outputs_class, enc_outputs_coord_logits=enc_outputs_coord_logits)
class GroundingDinoMLPPredictionHead(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
        super().__init__()
        self.num_layers = num_layers
        h = [hidden_dim] * (num_layers - 1)
        self.layers = nn.ModuleList(nn.Linear(n, k) for n, k in zip([input_dim] + h, h + [output_dim]))
    def forward(self, x):
        for i, layer in enumerate(self.layers): x = nn.functional.relu(layer(x)) if i < self.num_layers - 1 else layer(x)
        return x
def _upcast(t: Tensor) -> Tensor:
    if t.is_floating_point(): return t if t.dtype in (torch.float32, torch.float64) else t.float()
    else: return t if t.dtype in (torch.int32, torch.int64) else t.int()
def box_area(boxes: Tensor) -> Tensor:
    boxes = _upcast(boxes)
    return (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
def box_iou(boxes1, boxes2):
    area1 = box_area(boxes1)
    area2 = box_area(boxes2)
    left_top = torch.max(boxes1[:, None, :2], boxes2[:, :2])
    right_bottom = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])
    width_height = (right_bottom - left_top).clamp(min=0)
    inter = width_height[:, :, 0] * width_height[:, :, 1]
    union = area1[:, None] + area2 - inter
    iou = inter / union
    return iou, union
def generalized_box_iou(boxes1, boxes2):
    if not (boxes1[:, 2:] >= boxes1[:, :2]).all(): raise ValueError(f"boxes1 must be in [x0, y0, x1, y1] (corner) format, but got {boxes1}")
    if not (boxes2[:, 2:] >= boxes2[:, :2]).all(): raise ValueError(f"boxes2 must be in [x0, y0, x1, y1] (corner) format, but got {boxes2}")
    iou, union = box_iou(boxes1, boxes2)
    top_left = torch.min(boxes1[:, None, :2], boxes2[:, :2])
    bottom_right = torch.max(boxes1[:, None, 2:], boxes2[:, 2:])
    width_height = (bottom_right - top_left).clamp(min=0)
    area = width_height[:, :, 0] * width_height[:, :, 1]
    return iou - (area - union) / area
def _max_by_axis(the_list):
    maxes = the_list[0]
    for sublist in the_list[1:]:
        for index, item in enumerate(sublist): maxes[index] = max(maxes[index], item)
    return maxes
def dice_loss(inputs, targets, num_boxes):
    inputs = inputs.sigmoid()
    inputs = inputs.flatten(1)
    numerator = 2 * (inputs * targets).sum(1)
    denominator = inputs.sum(-1) + targets.sum(-1)
    loss = 1 - (numerator + 1) / (denominator + 1)
    return loss.sum() / num_boxes
def sigmoid_focal_loss(inputs, targets, num_boxes, alpha: float = 0.25, gamma: float = 2):
    prob = inputs.sigmoid()
    ce_loss = nn.functional.binary_cross_entropy_with_logits(inputs, targets, reduction="none")
    p_t = prob * targets + (1 - prob) * (1 - targets)
    loss = ce_loss * ((1 - p_t) ** gamma)
    if alpha >= 0:
        alpha_t = alpha * targets + (1 - alpha) * (1 - targets)
        loss = alpha_t * loss
    return loss.mean(1).sum() / num_boxes
class NestedTensor:
    def __init__(self, tensors, mask: Optional[Tensor]):
        self.tensors = tensors
        self.mask = mask
    def to(self, device):
        cast_tensor = self.tensors.to(device)
        mask = self.mask
        if mask is not None: cast_mask = mask.to(device)
        else: cast_mask = None
        return NestedTensor(cast_tensor, cast_mask)
    def decompose(self): return self.tensors, self.mask
    def __repr__(self): return str(self.tensors)
def nested_tensor_from_tensor_list(tensor_list: List[Tensor]):
    if tensor_list[0].ndim == 3:
        max_size = _max_by_axis([list(img.shape) for img in tensor_list])
        batch_shape = [len(tensor_list)] + max_size
        batch_size, num_channels, height, width = batch_shape
        dtype = tensor_list[0].dtype
        device = tensor_list[0].device
        tensor = torch.zeros(batch_shape, dtype=dtype, device=device)
        mask = torch.ones((batch_size, height, width), dtype=torch.bool, device=device)
        for img, pad_img, m in zip(tensor_list, tensor, mask):
            pad_img[: img.shape[0], : img.shape[1], : img.shape[2]].copy_(img)
            m[: img.shape[1], : img.shape[2]] = False
    else: raise ValueError("Only 3-dimensional tensors are supported")
    return NestedTensor(tensor, mask)
class GroundingDinoHungarianMatcher(nn.Module):
    def __init__(self, class_cost: float = 1, bbox_cost: float = 1, giou_cost: float = 1):
        super().__init__()
        requires_backends(self, ["scipy"])
        self.class_cost = class_cost
        self.bbox_cost = bbox_cost
        self.giou_cost = giou_cost
        if class_cost == 0 and bbox_cost == 0 and giou_cost == 0: raise ValueError("All costs of the Matcher can't be 0")
    @torch.no_grad()
    def forward(self, outputs, targets):
        batch_size, num_queries = outputs["logits"].shape[:2]
        out_prob = outputs["logits"].flatten(0, 1).sigmoid()
        out_bbox = outputs["pred_boxes"].flatten(0, 1)
        target_ids = torch.cat([v["class_labels"] for v in targets])
        target_bbox = torch.cat([v["boxes"] for v in targets])
        alpha = 0.25
        gamma = 2.0
        neg_cost_class = (1 - alpha) * (out_prob**gamma) * (-(1 - out_prob + 1e-8).log())
        pos_cost_class = alpha * ((1 - out_prob) ** gamma) * (-(out_prob + 1e-8).log())
        class_cost = pos_cost_class[:, target_ids] - neg_cost_class[:, target_ids]
        bbox_cost = torch.cdist(out_bbox, target_bbox, p=1)
        giou_cost = -generalized_box_iou(center_to_corners_format(out_bbox), center_to_corners_format(target_bbox))
        cost_matrix = self.bbox_cost * bbox_cost + self.class_cost * class_cost + self.giou_cost * giou_cost
        cost_matrix = cost_matrix.view(batch_size, num_queries, -1).cpu()
        sizes = [len(v["boxes"]) for v in targets]
        indices = [linear_sum_assignment(c[i]) for i, c in enumerate(cost_matrix.split(sizes, -1))]
        return [(torch.as_tensor(i, dtype=torch.int64), torch.as_tensor(j, dtype=torch.int64)) for i, j in indices]
class GroundingDinoLoss(nn.Module):
    def __init__(self, matcher, num_classes, focal_alpha, losses):
        super().__init__()
        self.matcher = matcher
        self.num_classes = num_classes
        self.focal_alpha = focal_alpha
        self.losses = losses
    def loss_labels(self, outputs, targets, indices, num_boxes):
        if "logits" not in outputs: raise KeyError("No logits were found in the outputs")
        source_logits = outputs["logits"]
        idx = self._get_source_permutation_idx(indices)
        target_classes_o = torch.cat([t["class_labels"][J] for t, (_, J) in zip(targets, indices)])
        target_classes = torch.full(source_logits.shape[:2], self.num_classes, dtype=torch.int64, device=source_logits.device)
        target_classes[idx] = target_classes_o
        target_classes_onehot = torch.zeros([source_logits.shape[0], source_logits.shape[1], source_logits.shape[2] + 1], dtype=source_logits.dtype,
        layout=source_logits.layout, device=source_logits.device)
        target_classes_onehot.scatter_(2, target_classes.unsqueeze(-1), 1)
        target_classes_onehot = target_classes_onehot[:, :, :-1]
        loss_ce = (sigmoid_focal_loss(source_logits, target_classes_onehot, num_boxes, alpha=self.focal_alpha, gamma=2) * source_logits.shape[1])
        losses = {"loss_ce": loss_ce}
        return losses
    @torch.no_grad()
    def loss_cardinality(self, outputs, targets, indices, num_boxes):
        logits = outputs["logits"]
        device = logits.device
        target_lengths = torch.as_tensor([len(v["class_labels"]) for v in targets], device=device)
        card_pred = (logits.argmax(-1) != logits.shape[-1] - 1).sum(1)
        card_err = nn.functional.l1_loss(card_pred.float(), target_lengths.float())
        losses = {"cardinality_error": card_err}
        return losses
    def loss_boxes(self, outputs, targets, indices, num_boxes):
        if "pred_boxes" not in outputs: raise KeyError("No predicted boxes found in outputs")
        idx = self._get_source_permutation_idx(indices)
        source_boxes = outputs["pred_boxes"][idx]
        target_boxes = torch.cat([t["boxes"][i] for t, (_, i) in zip(targets, indices)], dim=0)
        loss_bbox = nn.functional.l1_loss(source_boxes, target_boxes, reduction="none")
        losses = {}
        losses["loss_bbox"] = loss_bbox.sum() / num_boxes
        loss_giou = 1 - torch.diag(generalized_box_iou(center_to_corners_format(source_boxes), center_to_corners_format(target_boxes)))
        losses["loss_giou"] = loss_giou.sum() / num_boxes
        return losses
    def _get_source_permutation_idx(self, indices):
        batch_idx = torch.cat([torch.full_like(source, i) for i, (source, _) in enumerate(indices)])
        source_idx = torch.cat([source for (source, _) in indices])
        return batch_idx, source_idx
    def _get_target_permutation_idx(self, indices):
        batch_idx = torch.cat([torch.full_like(target, i) for i, (_, target) in enumerate(indices)])
        target_idx = torch.cat([target for (_, target) in indices])
        return batch_idx, target_idx
    def get_loss(self, loss, outputs, targets, indices, num_boxes):
        loss_map = {"labels": self.loss_labels, "cardinality": self.loss_cardinality, "boxes": self.loss_boxes}
        if loss not in loss_map: raise ValueError(f"Loss {loss} not supported")
        return loss_map[loss](outputs, targets, indices, num_boxes)
    def forward(self, outputs, targets):
        outputs_without_aux = {k: v for k, v in outputs.items() if k != "auxiliary_outputs" and k != "enc_outputs"}
        indices = self.matcher(outputs_without_aux, targets)
        num_boxes = sum(len(t["class_labels"]) for t in targets)
        num_boxes = torch.as_tensor([num_boxes], dtype=torch.float, device=next(iter(outputs.values())).device)
        world_size = 1
        if is_sapiens_accelerator_available():
            if PartialState._shared_state != {}:
                num_boxes = reduce(num_boxes)
                world_size = PartialState().num_processes
        num_boxes = torch.clamp(num_boxes / world_size, min=1).item()
        losses = {}
        for loss in self.losses: losses.update(self.get_loss(loss, outputs, targets, indices, num_boxes))
        if "auxiliary_outputs" in outputs:
            for i, auxiliary_outputs in enumerate(outputs["auxiliary_outputs"]):
                indices = self.matcher(auxiliary_outputs, targets)
                for loss in self.losses:
                    l_dict = self.get_loss(loss, auxiliary_outputs, targets, indices, num_boxes)
                    l_dict = {k + f"_{i}": v for k, v in l_dict.items()}
                    losses.update(l_dict)
        if "enc_outputs" in outputs:
            enc_outputs = outputs["enc_outputs"]
            bin_targets = copy.deepcopy(targets)
            for bt in bin_targets: bt["class_labels"] = torch.zeros_like(bt["class_labels"])
            indices = self.matcher(enc_outputs, bin_targets)
            for loss in self.losses:
                l_dict = self.get_loss(loss, enc_outputs, bin_targets, indices, num_boxes)
                l_dict = {k + "_enc": v for k, v in l_dict.items()}
                losses.update(l_dict)
        return losses
@add_start_docstrings("Grounding DINO Model (consisting of a backbone and encoder-decoder Transformer) with object detection heads on top, for tasks such as COCO detection.", GROUNDING_DINO_START_DOCSTRING)
class GroundingDinoForObjectDetection(GroundingDinoPreTrainedModel):
    _tied_weights_keys = [r"bbox_embed\.[1-9]\d*", r"model\.decoder\.bbox_embed\.[0-9]\d*"]
    def __init__(self, config: GroundingDinoConfig):
        super().__init__(config)
        self.model = GroundingDinoModel(config)
        _class_embed = GroundingDinoContrastiveEmbedding(config)
        if config.decoder_bbox_embed_share:
            _bbox_embed = GroundingDinoMLPPredictionHead(input_dim=config.d_model, hidden_dim=config.d_model, output_dim=4, num_layers=3)
            self.bbox_embed = nn.ModuleList([_bbox_embed for _ in range(config.decoder_layers)])
        else:
            for _ in range(config.decoder_layers):
                _bbox_embed = GroundingDinoMLPPredictionHead(input_dim=config.d_model, hidden_dim=config.d_model, output_dim=4, num_layers=3)
                self.bbox_embed = nn.ModuleList([_bbox_embed for _ in range(config.decoder_layers)])
        self.class_embed = nn.ModuleList([_class_embed for _ in range(config.decoder_layers)])
        self.model.decoder.bbox_embed = self.bbox_embed
        self.model.decoder.class_embed = self.class_embed
        self.post_init()
    @torch.jit.unused
    def _set_aux_loss(self, outputs_class, outputs_coord): return [{"logits": a, "pred_boxes": b} for a, b in zip(outputs_class[:-1], outputs_coord[:-1])]
    @add_start_docstrings_to_model_forward(GROUNDING_DINO_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, input_ids: torch.LongTensor, token_type_ids: torch.LongTensor = None, attention_mask: torch.LongTensor = None,
    pixel_mask: Optional[torch.BoolTensor] = None, encoder_outputs: Optional[Union[GroundingDinoEncoderOutput, Tuple]] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, labels: List[Dict[str, Union[torch.LongTensor, torch.FloatTensor]]] = None):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if attention_mask is None: attention_mask = torch.ones_like(input_ids)
        outputs = self.model(pixel_values=pixel_values, input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, pixel_mask=pixel_mask,
        encoder_outputs=encoder_outputs, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        idx = 5 + (1 if output_attentions else 0) + (1 if output_hidden_states else 0)
        enc_text_hidden_state = outputs.encoder_last_hidden_state_text if return_dict else outputs[idx]
        hidden_states = outputs.intermediate_hidden_states if return_dict else outputs[2]
        init_reference_points = outputs.init_reference_points if return_dict else outputs[1]
        inter_references_points = outputs.intermediate_reference_points if return_dict else outputs[3]
        outputs_classes = []
        outputs_coords = []
        num_levels = hidden_states.shape[1]
        for level in range(num_levels):
            if level == 0: reference = init_reference_points
            else: reference = inter_references_points[:, level - 1]
            reference = torch.special.logit(reference, eps=1e-5)
            outputs_class = self.class_embed[level](vision_hidden_state=hidden_states[:, level], text_hidden_state=enc_text_hidden_state, text_token_mask=attention_mask.bool())
            delta_bbox = self.bbox_embed[level](hidden_states[:, level])
            reference_coordinates = reference.shape[-1]
            if reference_coordinates == 4: outputs_coord_logits = delta_bbox + reference
            elif reference_coordinates == 2:
                delta_bbox[..., :2] += reference
                outputs_coord_logits = delta_bbox
            else: raise ValueError(f"reference.shape[-1] should be 4 or 2, but got {reference.shape[-1]}")
            outputs_coord = outputs_coord_logits.sigmoid()
            outputs_classes.append(outputs_class)
            outputs_coords.append(outputs_coord)
        outputs_class = torch.stack(outputs_classes)
        outputs_coord = torch.stack(outputs_coords)
        logits = outputs_class[-1]
        pred_boxes = outputs_coord[-1]
        loss, loss_dict, auxiliary_outputs = None, None, None
        if labels is not None:
            matcher = GroundingDinoHungarianMatcher(class_cost=self.config.class_cost, bbox_cost=self.config.bbox_cost, giou_cost=self.config.giou_cost)
            losses = ["labels", "boxes", "cardinality"]
            criterion = GroundingDinoLoss(matcher=matcher, num_classes=self.config.num_labels, focal_alpha=self.config.focal_alpha, losses=losses)
            criterion.to(self.device)
            outputs_loss = {}
            outputs_loss["logits"] = logits
            outputs_loss["pred_boxes"] = pred_boxes
            if self.config.auxiliary_loss:
                auxiliary_outputs = self._set_aux_loss(outputs_class, outputs_coord)
                outputs_loss["auxiliary_outputs"] = auxiliary_outputs
            if self.config.two_stage:
                enc_outputs_coord = outputs[-1].sigmoid()
                outputs_loss["enc_outputs"] = {"logits": outputs[-2], "pred_boxes": enc_outputs_coord}
            loss_dict = criterion(outputs_loss, labels)
            weight_dict = {"loss_ce": 1, "loss_bbox": self.config.bbox_loss_coefficient}
            weight_dict["loss_giou"] = self.config.giou_loss_coefficient
            if self.config.auxiliary_loss:
                aux_weight_dict = {}
                for i in range(self.config.decoder_layers - 1): aux_weight_dict.update({k + f"_{i}": v for k, v in weight_dict.items()})
                weight_dict.update(aux_weight_dict)
            loss = sum(loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict)
        if not return_dict:
            if auxiliary_outputs is not None: output = (logits, pred_boxes) + auxiliary_outputs + outputs
            else: output = (logits, pred_boxes) + outputs
            tuple_outputs = ((loss, loss_dict) + output) if loss is not None else output
            return tuple_outputs
        dict_outputs = GroundingDinoObjectDetectionOutput(loss=loss, loss_dict=loss_dict, logits=logits, pred_boxes=pred_boxes, last_hidden_state=outputs.last_hidden_state,
        auxiliary_outputs=auxiliary_outputs, decoder_hidden_states=outputs.decoder_hidden_states, decoder_attentions=outputs.decoder_attentions, encoder_last_hidden_state_vision=outputs.encoder_last_hidden_state_vision,
        encoder_last_hidden_state_text=outputs.encoder_last_hidden_state_text, encoder_vision_hidden_states=outputs.encoder_vision_hidden_states, encoder_text_hidden_states=outputs.encoder_text_hidden_states,
        encoder_attentions=outputs.encoder_attentions, intermediate_hidden_states=outputs.intermediate_hidden_states, intermediate_reference_points=outputs.intermediate_reference_points,
        init_reference_points=outputs.init_reference_points, enc_outputs_class=outputs.enc_outputs_class, enc_outputs_coord_logits=outputs.enc_outputs_coord_logits)
        return dict_outputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
