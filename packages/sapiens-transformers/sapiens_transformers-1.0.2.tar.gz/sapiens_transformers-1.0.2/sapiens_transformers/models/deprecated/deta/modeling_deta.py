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
from ....activations import ACT2FN
from ....file_utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, is_scipy_available, is_torch_cuda_available, is_vision_available, replace_return_docstrings)
from ....modeling_attn_mask_utils import _prepare_4d_attention_mask
from ....modeling_outputs import BaseModelOutput
from ....modeling_utils import PreTrainedModel
from ....pytorch_utils import meshgrid
from ....utils import is_sapiens_accelerator_available, is_ninja_available, is_torchvision_available, logging, requires_backends
from ....utils.backbone_utils import load_backbone
from .configuration_deta import DetaConfig
logger = logging.get_logger(__name__)
MultiScaleDeformableAttention = None
def load_cuda_kernels():
    from torch.utils.cpp_extension import load
    global MultiScaleDeformableAttention
    root = Path(__file__).resolve().parent.parent.parent / "kernels" / "deta"
    src_files = [root / filename for filename in ["vision.cpp", os.path.join("cpu", "ms_deform_attn_cpu.cpp"), os.path.join("cuda", "ms_deform_attn_cuda.cu")]]
    load("MultiScaleDeformableAttention", src_files, with_cuda=True, extra_include_paths=[str(root)], extra_cflags=["-DWITH_CUDA=1"], extra_cuda_cflags=["-DCUDA_HAS_FP16=1", "-D__CUDA_NO_HALF_OPERATORS__", "-D__CUDA_NO_HALF_CONVERSIONS__", "-D__CUDA_NO_HALF2_OPERATORS__"])
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
if is_sapiens_accelerator_available():
    from sapiens_accelerator import PartialState
    from sapiens_accelerator.utils import reduce
if is_vision_available(): from sapiens_transformers.image_transforms import center_to_corners_format
if is_torchvision_available(): from torchvision.ops.boxes import batched_nms
if is_scipy_available(): from scipy.optimize import linear_sum_assignment
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "DetaConfig"
_CHECKPOINT_FOR_DOC = "jozhang97/deta-swin-large-o365"
@dataclass
class DetaDecoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class DetaModelOutput(ModelOutput):
    """Args:"""
    init_reference_points: torch.FloatTensor = None
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
    output_proposals: Optional[torch.FloatTensor] = None
@dataclass
class DetaObjectDetectionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    loss_dict: Optional[Dict] = None
    logits: torch.FloatTensor = None
    pred_boxes: torch.FloatTensor = None
    auxiliary_outputs: Optional[List[Dict]] = None
    init_reference_points: Optional[torch.FloatTensor] = None
    last_hidden_state: Optional[torch.FloatTensor] = None
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_reference_points: Optional[torch.FloatTensor] = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    enc_outputs_class: Optional = None
    enc_outputs_coord_logits: Optional = None
    output_proposals: Optional[torch.FloatTensor] = None
def _get_clones(module, N): return nn.ModuleList([copy.deepcopy(module) for i in range(N)])
def inverse_sigmoid(x, eps=1e-5):
    x = x.clamp(min=0, max=1)
    x1 = x.clamp(min=eps)
    x2 = (1 - x).clamp(min=eps)
    return torch.log(x1 / x2)
class DetaFrozenBatchNorm2d(nn.Module):
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
            new_module = DetaFrozenBatchNorm2d(module.num_features)
            if not module.weight.device == torch.device("meta"):
                new_module.weight.data.copy_(module.weight)
                new_module.bias.data.copy_(module.bias)
                new_module.running_mean.data.copy_(module.running_mean)
                new_module.running_var.data.copy_(module.running_var)
            model._modules[name] = new_module
        if len(list(module.children())) > 0: replace_batch_norm(module)
class DetaBackboneWithPositionalEncodings(nn.Module):
    def __init__(self, config):
        super().__init__()
        backbone = load_backbone(config)
        with torch.no_grad(): replace_batch_norm(backbone)
        self.model = backbone
        self.intermediate_channel_sizes = self.model.channels
        if config.backbone_config.model_type == "resnet":
            for name, parameter in self.model.named_parameters():
                if "stages.1" not in name and "stages.2" not in name and "stages.3" not in name: parameter.requires_grad_(False)
        self.position_embedding = build_position_encoding(config)
    def forward(self, pixel_values: torch.Tensor, pixel_mask: torch.Tensor):
        features = self.model(pixel_values).feature_maps
        out = []
        pos = []
        for feature_map in features:
            mask = nn.functional.interpolate(pixel_mask[None].float(), size=feature_map.shape[-2:]).to(torch.bool)[0]
            position_embeddings = self.position_embedding(feature_map, mask).to(feature_map.dtype)
            out.append((feature_map, mask))
            pos.append(position_embeddings)
        return out, pos
class DetaSinePositionEmbedding(nn.Module):
    def __init__(self, embedding_dim=64, temperature=10000, normalize=False, scale=None):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.temperature = temperature
        self.normalize = normalize
        if scale is not None and normalize is False: raise ValueError("normalize should be True if scale is passed")
        if scale is None: scale = 2 * math.pi
        self.scale = scale
    def forward(self, pixel_values, pixel_mask):
        if pixel_mask is None: raise ValueError("No pixel mask provided")
        y_embed = pixel_mask.cumsum(1, dtype=torch.float32)
        x_embed = pixel_mask.cumsum(2, dtype=torch.float32)
        if self.normalize:
            eps = 1e-6
            y_embed = (y_embed - 0.5) / (y_embed[:, -1:, :] + eps) * self.scale
            x_embed = (x_embed - 0.5) / (x_embed[:, :, -1:] + eps) * self.scale
        dim_t = torch.arange(self.embedding_dim, dtype=torch.int64, device=pixel_values.device).float()
        dim_t = self.temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / self.embedding_dim)
        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos = torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)
        return pos
class DetaLearnedPositionEmbedding(nn.Module):
    def __init__(self, embedding_dim=256):
        super().__init__()
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
    n_steps = config.d_model // 2
    if config.position_embedding_type == "sine": position_embedding = DetaSinePositionEmbedding(n_steps, normalize=True)
    elif config.position_embedding_type == "learned": position_embedding = DetaLearnedPositionEmbedding(n_steps)
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
class DetaMultiscaleDeformableAttention(nn.Module):
    def __init__(self, config: DetaConfig, num_heads: int, n_points: int):
        super().__init__()
        kernel_loaded = MultiScaleDeformableAttention is not None
        if is_torch_cuda_available() and is_ninja_available() and not kernel_loaded:
            try: load_cuda_kernels()
            except Exception as e: logger.warning(f"Could not load the custom kernel for multi-scale deformable attention: {e}")
        if config.d_model % num_heads != 0: raise ValueError(f"embed_dim (d_model) must be divisible by num_heads, but got {config.d_model} and {num_heads}")
        dim_per_head = config.d_model // num_heads
        if not ((dim_per_head & (dim_per_head - 1) == 0) and dim_per_head != 0): warnings.warn("You'd better set embed_dim (d_model) in DetaMultiscaleDeformableAttention to make the dimension of each attention head a power of 2 which is more efficient in the authors' CUDA implementation.")
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
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, encoder_hidden_states=None, encoder_attention_mask=None,
    position_embeddings: Optional[torch.Tensor] = None, reference_points=None, spatial_shapes=None, level_start_index=None, output_attentions: bool = False):
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
class DetaMultiheadAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0, bias: bool = True):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        if self.head_dim * num_heads != self.embed_dim: raise ValueError(f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`: {num_heads}).")
        self.scaling = self.head_dim**-0.5
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _shape(self, tensor: torch.Tensor, seq_len: int, batch_size: int): return tensor.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def with_pos_embed(self, tensor: torch.Tensor, position_embeddings: Optional[Tensor]): return tensor if position_embeddings is None else tensor + position_embeddings
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_embeddings: Optional[torch.Tensor] = None,
    output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        batch_size, target_len, embed_dim = hidden_states.size()
        if position_embeddings is not None:
            hidden_states_original = hidden_states
            hidden_states = self.with_pos_embed(hidden_states, position_embeddings)
        query_states = self.q_proj(hidden_states) * self.scaling
        key_states = self._shape(self.k_proj(hidden_states), -1, batch_size)
        value_states = self._shape(self.v_proj(hidden_states_original), -1, batch_size)
        proj_shape = (batch_size * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, target_len, batch_size).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        source_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (batch_size * self.num_heads, target_len, source_len): raise ValueError(f"Attention weights should be of size {(batch_size * self.num_heads, target_len, source_len)}, but is {attn_weights.size()}")
        if attention_mask is not None: attention_mask = _prepare_4d_attention_mask(attention_mask, hidden_states.dtype)
        if attention_mask is not None:
            if attention_mask.size() != (batch_size, 1, target_len, source_len): raise ValueError(f"Attention mask should be of size {(batch_size, 1, target_len, source_len)}, but is {attention_mask.size()}")
            attn_weights = attn_weights.view(batch_size, self.num_heads, target_len, source_len) + attention_mask
            attn_weights = attn_weights.view(batch_size * self.num_heads, target_len, source_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(batch_size, self.num_heads, target_len, source_len)
            attn_weights = attn_weights_reshaped.view(batch_size * self.num_heads, target_len, source_len)
        else: attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (batch_size * self.num_heads, target_len, self.head_dim): raise ValueError(f"`attn_output` should be of size {(batch_size, self.num_heads, target_len, self.head_dim)}, but is {attn_output.size()}")
        attn_output = attn_output.view(batch_size, self.num_heads, target_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(batch_size, target_len, embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped
class DetaEncoderLayer(nn.Module):
    def __init__(self, config: DetaConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = DetaMultiscaleDeformableAttention(config, num_heads=config.encoder_attention_heads, n_points=config.encoder_n_points)
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(self.embed_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, position_embeddings: torch.Tensor = None, reference_points=None, spatial_shapes=None, level_start_index=None, output_attentions: bool = False):
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
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class DetaDecoderLayer(nn.Module):
    def __init__(self, config: DetaConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = DetaMultiheadAttention(embed_dim=self.embed_dim, num_heads=config.decoder_attention_heads, dropout=config.attention_dropout)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.encoder_attn = DetaMultiscaleDeformableAttention(config, num_heads=config.decoder_attention_heads, n_points=config.decoder_n_points)
        self.encoder_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.fc1 = nn.Linear(self.embed_dim, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, position_embeddings: Optional[torch.Tensor] = None, reference_points=None, spatial_shapes=None, level_start_index=None,
    encoder_hidden_states: Optional[torch.Tensor] = None, encoder_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False):
        residual = hidden_states
        hidden_states, self_attn_weights = self.self_attn(hidden_states=hidden_states, position_embeddings=position_embeddings, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        second_residual = hidden_states
        cross_attn_weights = None
        hidden_states, cross_attn_weights = self.encoder_attn(hidden_states=hidden_states, attention_mask=encoder_attention_mask, encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask,
        position_embeddings=position_embeddings, reference_points=reference_points, spatial_shapes=spatial_shapes, level_start_index=level_start_index, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = second_residual + hidden_states
        hidden_states = self.encoder_attn_layer_norm(hidden_states)
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        outputs = (hidden_states,)
        if output_attentions: outputs += (self_attn_weights, cross_attn_weights)
        return outputs
class DetaPreTrainedModel(PreTrainedModel):
    config_class = DetaConfig
    base_model_prefix = "model"
    main_input_name = "pixel_values"
    _no_split_modules = [r"DetaBackboneWithPositionalEncodings", r"DetaEncoderLayer", r"DetaDecoderLayer"]
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        std = self.config.init_std
        if isinstance(module, DetaLearnedPositionEmbedding):
            nn.init.uniform_(module.row_embeddings.weight)
            nn.init.uniform_(module.column_embeddings.weight)
        elif isinstance(module, DetaMultiscaleDeformableAttention): module._reset_parameters()
        elif isinstance(module, (nn.Linear, nn.Conv2d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        if hasattr(module, "reference_points") and not self.config.two_stage:
            nn.init.xavier_uniform_(module.reference_points.weight.data, gain=1.0)
            nn.init.constant_(module.reference_points.bias.data, 0.0)
        if hasattr(module, "level_embed"): nn.init.normal_(module.level_embed)
DETA_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`DetaConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
DETA_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it.
            Pixel values can be obtained using [`AutoImageProcessor`]. See [`AutoImageProcessor.__call__`] for details.
        pixel_mask (`torch.LongTensor` of shape `(batch_size, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            [What are attention masks?](../glossary#attention-mask)
        decoder_attention_mask (`torch.FloatTensor` of shape `(batch_size, num_queries)`, *optional*):
            Not used by default. Can be used to mask object queries.
        encoder_outputs (`tuple(tuple(torch.FloatTensor)`, *optional*):
            Tuple consists of (`last_hidden_state`, *optional*: `hidden_states`, *optional*: `attentions`)
            `last_hidden_state` of shape `(batch_size, sequence_length, hidden_size)`, *optional*) is a sequence of
            hidden-states at the output of the last layer of the encoder. Used in the cross-attention of the decoder.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing the flattened feature map (output of the backbone + projection layer), you
            can choose to directly pass a flattened representation of an image.
        decoder_inputs_embeds (`torch.FloatTensor` of shape `(batch_size, num_queries, hidden_size)`, *optional*):
            Optionally, instead of initializing the queries with a tensor of zeros, you can choose to directly pass an
            embedded representation.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~file_utils.ModelOutput`] instead of a plain tuple.
"""
class DetaEncoder(DetaPreTrainedModel):
    def __init__(self, config: DetaConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layers = nn.ModuleList([DetaEncoderLayer(config) for _ in range(config.encoder_layers)])
        self.gradient_checkpointing = False
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
    def forward(self, inputs_embeds=None, attention_mask=None, position_embeddings=None, spatial_shapes=None, level_start_index=None, valid_ratios=None,
    output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states = inputs_embeds
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        reference_points = self.get_reference_points(spatial_shapes, valid_ratios, device=inputs_embeds.device)
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for i, encoder_layer in enumerate(self.layers):
            if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
            layer_outputs = encoder_layer(hidden_states, attention_mask, position_embeddings=position_embeddings, reference_points=reference_points, spatial_shapes=spatial_shapes,
            level_start_index=level_start_index, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: encoder_states = encoder_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=encoder_states, attentions=all_attentions)
class DetaDecoder(DetaPreTrainedModel):
    def __init__(self, config: DetaConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layers = nn.ModuleList([DetaDecoderLayer(config) for _ in range(config.decoder_layers)])
        self.gradient_checkpointing = False
        self.bbox_embed = None
        self.class_embed = None
        self.post_init()
    def forward(self, inputs_embeds=None, encoder_hidden_states=None, encoder_attention_mask=None, position_embeddings=None, reference_points=None, spatial_shapes=None,
    level_start_index=None, valid_ratios=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is not None: hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        intermediate = ()
        intermediate_reference_points = ()
        for idx, decoder_layer in enumerate(self.layers):
            if reference_points.shape[-1] == 4: reference_points_input = (reference_points[:, :, None] * torch.cat([valid_ratios, valid_ratios], -1)[:, None])
            else:
                if reference_points.shape[-1] != 2: raise ValueError("Reference points' last dimension must be of size 2")
                reference_points_input = reference_points[:, :, None] * valid_ratios[:, None]
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, position_embeddings, reference_points_input, spatial_shapes,
                level_start_index, encoder_hidden_states, encoder_attention_mask, output_attentions)
            else:
                layer_outputs = decoder_layer(hidden_states, position_embeddings=position_embeddings, encoder_hidden_states=encoder_hidden_states, reference_points=reference_points_input,
                spatial_shapes=spatial_shapes, level_start_index=level_start_index, encoder_attention_mask=encoder_attention_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if self.bbox_embed is not None:
                tmp = self.bbox_embed[idx](hidden_states)
                if reference_points.shape[-1] == 4:
                    new_reference_points = tmp + inverse_sigmoid(reference_points)
                    new_reference_points = new_reference_points.sigmoid()
                else:
                    if reference_points.shape[-1] != 2: raise ValueError(f"Reference points' last dimension must be of size 2, but is {reference_points.shape[-1]}")
                    new_reference_points = tmp
                    new_reference_points[..., :2] = tmp[..., :2] + inverse_sigmoid(reference_points)
                    new_reference_points = new_reference_points.sigmoid()
                reference_points = new_reference_points.detach()
            intermediate += (hidden_states,)
            intermediate_reference_points += (reference_points,)
            if output_attentions:
                all_self_attns += (layer_outputs[1],)
                if encoder_hidden_states is not None: all_cross_attentions += (layer_outputs[2],)
        intermediate = torch.stack(intermediate, dim=1)
        intermediate_reference_points = torch.stack(intermediate_reference_points, dim=1)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, intermediate, intermediate_reference_points, all_hidden_states, all_self_attns, all_cross_attentions] if v is not None)
        return DetaDecoderOutput(last_hidden_state=hidden_states, intermediate_hidden_states=intermediate, intermediate_reference_points=intermediate_reference_points,
        hidden_states=all_hidden_states, attentions=all_self_attns, cross_attentions=all_cross_attentions)
@add_start_docstrings("The bare DETA Model (consisting of a backbone and encoder-decoder Transformer) outputting raw hidden-states without any specific head on top.", DETA_START_DOCSTRING)
class DetaModel(DetaPreTrainedModel):
    def __init__(self, config: DetaConfig):
        super().__init__(config)
        if config.two_stage: requires_backends(self, ["torchvision"])
        self.backbone = DetaBackboneWithPositionalEncodings(config)
        intermediate_channel_sizes = self.backbone.intermediate_channel_sizes
        if config.num_feature_levels > 1:
            num_backbone_outs = len(intermediate_channel_sizes)
            input_proj_list = []
            for _ in range(num_backbone_outs):
                in_channels = intermediate_channel_sizes[_]
                input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=1), nn.GroupNorm(32, config.d_model)))
            for _ in range(config.num_feature_levels - num_backbone_outs):
                input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=3, stride=2, padding=1), nn.GroupNorm(32, config.d_model)))
                in_channels = config.d_model
            self.input_proj = nn.ModuleList(input_proj_list)
        else: self.input_proj = nn.ModuleList([nn.Sequential(nn.Conv2d(intermediate_channel_sizes[-1], config.d_model, kernel_size=1), nn.GroupNorm(32, config.d_model))])
        if not config.two_stage: self.query_position_embeddings = nn.Embedding(config.num_queries, config.d_model * 2)
        self.encoder = DetaEncoder(config)
        self.decoder = DetaDecoder(config)
        self.level_embed = nn.Parameter(torch.Tensor(config.num_feature_levels, config.d_model))
        if config.two_stage:
            self.enc_output = nn.Linear(config.d_model, config.d_model)
            self.enc_output_norm = nn.LayerNorm(config.d_model)
            self.pos_trans = nn.Linear(config.d_model * 2, config.d_model * 2)
            self.pos_trans_norm = nn.LayerNorm(config.d_model * 2)
            self.pix_trans = nn.Linear(config.d_model, config.d_model)
            self.pix_trans_norm = nn.LayerNorm(config.d_model)
        else: self.reference_points = nn.Linear(config.d_model, 2)
        self.assign_first_stage = config.assign_first_stage
        self.two_stage_num_proposals = config.two_stage_num_proposals
        self.post_init()
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def freeze_backbone(self):
        for name, param in self.backbone.model.named_parameters():
            param.requires_grad_(False)
    def unfreeze_backbone(self):
        for name, param in self.backbone.model.named_parameters():
            param.requires_grad_(True)
    def get_valid_ratio(self, mask, dtype=torch.float32):
        _, height, width = mask.shape
        valid_height = torch.sum(mask[:, :, 0], 1)
        valid_width = torch.sum(mask[:, 0, :], 1)
        valid_ratio_height = valid_height.to(dtype) / height
        valid_ratio_width = valid_width.to(dtype) / width
        valid_ratio = torch.stack([valid_ratio_width, valid_ratio_height], -1)
        return valid_ratio
    def get_proposal_pos_embed(self, proposals):
        num_pos_feats = self.config.d_model // 2
        temperature = 10000
        scale = 2 * math.pi
        dim_t = torch.arange(num_pos_feats, dtype=torch.int64, device=proposals.device).float()
        dim_t = temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / num_pos_feats)
        proposals = proposals.sigmoid() * scale
        pos = proposals[:, :, :, None] / dim_t
        pos = torch.stack((pos[:, :, :, 0::2].sin(), pos[:, :, :, 1::2].cos()), dim=4).flatten(2)
        return pos
    def gen_encoder_output_proposals(self, enc_output, padding_mask, spatial_shapes):
        batch_size = enc_output.shape[0]
        proposals = []
        _cur = 0
        level_ids = []
        for level, (height, width) in enumerate(spatial_shapes):
            mask_flatten_ = padding_mask[:, _cur : (_cur + height * width)].view(batch_size, height, width, 1)
            valid_height = torch.sum(~mask_flatten_[:, :, 0, 0], 1)
            valid_width = torch.sum(~mask_flatten_[:, 0, :, 0], 1)
            grid_y, grid_x = meshgrid(torch.linspace(0, height - 1, height, dtype=torch.float32, device=enc_output.device), torch.linspace(0, width - 1, width, dtype=torch.float32, device=enc_output.device), indexing="ij")
            grid = torch.cat([grid_x.unsqueeze(-1), grid_y.unsqueeze(-1)], -1)
            scale = torch.cat([valid_width.unsqueeze(-1), valid_height.unsqueeze(-1)], 1).view(batch_size, 1, 1, 2)
            grid = (grid.unsqueeze(0).expand(batch_size, -1, -1, -1) + 0.5) / scale
            width_heigth = torch.ones_like(grid) * 0.05 * (2.0**level)
            proposal = torch.cat((grid, width_heigth), -1).view(batch_size, -1, 4)
            proposals.append(proposal)
            _cur += height * width
            level_ids.append(grid.new_ones(height * width, dtype=torch.long) * level)
        output_proposals = torch.cat(proposals, 1)
        output_proposals_valid = ((output_proposals > 0.01) & (output_proposals < 0.99)).all(-1, keepdim=True)
        output_proposals = torch.log(output_proposals / (1 - output_proposals))
        output_proposals = output_proposals.masked_fill(padding_mask.unsqueeze(-1), float("inf"))
        output_proposals = output_proposals.masked_fill(~output_proposals_valid, float("inf"))
        object_query = enc_output
        object_query = object_query.masked_fill(padding_mask.unsqueeze(-1), float(0))
        object_query = object_query.masked_fill(~output_proposals_valid, float(0))
        object_query = self.enc_output_norm(self.enc_output(object_query))
        level_ids = torch.cat(level_ids)
        return object_query, output_proposals, level_ids
    @add_start_docstrings_to_model_forward(DETA_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, pixel_mask: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.FloatTensor] = None, encoder_outputs: Optional[torch.FloatTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], DetaModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, num_channels, height, width = pixel_values.shape
        device = pixel_values.device
        if pixel_mask is None: pixel_mask = torch.ones(((batch_size, height, width)), dtype=torch.long, device=device)
        features, position_embeddings_list = self.backbone(pixel_values, pixel_mask)
        sources = []
        masks = []
        for level, (source, mask) in enumerate(features):
            sources.append(self.input_proj[level](source))
            masks.append(mask)
            if mask is None: raise ValueError("No attention mask was provided")
        if self.config.num_feature_levels > len(sources):
            _len_sources = len(sources)
            for level in range(_len_sources, self.config.num_feature_levels):
                if level == _len_sources: source = self.input_proj[level](features[-1][0])
                else: source = self.input_proj[level](sources[-1])
                mask = nn.functional.interpolate(pixel_mask[None].float(), size=source.shape[-2:]).to(torch.bool)[0]
                pos_l = self.backbone.position_embedding(source, mask).to(source.dtype)
                sources.append(source)
                masks.append(mask)
                position_embeddings_list.append(pos_l)
        query_embeds = None
        if not self.config.two_stage: query_embeds = self.query_position_embeddings.weight
        spatial_shapes = [(source.shape[2:]) for source in sources]
        source_flatten = [source.flatten(2).transpose(1, 2) for source in sources]
        mask_flatten = [mask.flatten(1) for mask in masks]
        lvl_pos_embed_flatten = []
        for level, pos_embed in enumerate(position_embeddings_list):
            pos_embed = pos_embed.flatten(2).transpose(1, 2)
            lvl_pos_embed = pos_embed + self.level_embed[level].view(1, 1, -1)
            lvl_pos_embed_flatten.append(lvl_pos_embed)
        source_flatten = torch.cat(source_flatten, 1)
        mask_flatten = torch.cat(mask_flatten, 1)
        lvl_pos_embed_flatten = torch.cat(lvl_pos_embed_flatten, 1)
        spatial_shapes = torch.as_tensor(spatial_shapes, dtype=torch.long, device=source_flatten.device)
        level_start_index = torch.cat((spatial_shapes.new_zeros((1,)), spatial_shapes.prod(1).cumsum(0)[:-1]))
        valid_ratios = torch.stack([self.get_valid_ratio(m) for m in masks], 1)
        valid_ratios = valid_ratios.float()
        if encoder_outputs is None:
            encoder_outputs = self.encoder(inputs_embeds=source_flatten, attention_mask=mask_flatten, position_embeddings=lvl_pos_embed_flatten, spatial_shapes=spatial_shapes,
            level_start_index=level_start_index, valid_ratios=valid_ratios, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, BaseModelOutput): encoder_outputs = BaseModelOutput(last_hidden_state=encoder_outputs[0], hidden_states=encoder_outputs[1] if len(encoder_outputs) > 1 else None, attentions=encoder_outputs[2] if len(encoder_outputs) > 2 else None)
        batch_size, _, num_channels = encoder_outputs[0].shape
        enc_outputs_class = None
        enc_outputs_coord_logits = None
        output_proposals = None
        if self.config.two_stage:
            object_query_embedding, output_proposals, level_ids = self.gen_encoder_output_proposals(encoder_outputs[0], ~mask_flatten, spatial_shapes)
            enc_outputs_class = self.decoder.class_embed[-1](object_query_embedding)
            delta_bbox = self.decoder.bbox_embed[-1](object_query_embedding)
            enc_outputs_coord_logits = delta_bbox + output_proposals
            topk = self.two_stage_num_proposals
            proposal_logit = enc_outputs_class[..., 0]
            if self.assign_first_stage:
                proposal_boxes = center_to_corners_format(enc_outputs_coord_logits.sigmoid().float()).clamp(0, 1)
                topk_proposals = []
                for b in range(batch_size):
                    prop_boxes_b = proposal_boxes[b]
                    prop_logits_b = proposal_logit[b]
                    pre_nms_topk = 1000
                    pre_nms_inds = []
                    for lvl in range(len(spatial_shapes)):
                        lvl_mask = level_ids == lvl
                        pre_nms_inds.append(torch.topk(prop_logits_b.sigmoid() * lvl_mask, pre_nms_topk)[1])
                    pre_nms_inds = torch.cat(pre_nms_inds)
                    post_nms_inds = batched_nms(prop_boxes_b[pre_nms_inds], prop_logits_b[pre_nms_inds], level_ids[pre_nms_inds], 0.9)
                    keep_inds = pre_nms_inds[post_nms_inds]
                    if len(keep_inds) < self.two_stage_num_proposals:
                        print(f"[WARNING] nms proposals ({len(keep_inds)}) < {self.two_stage_num_proposals}, running naive topk")
                        keep_inds = torch.topk(proposal_logit[b], topk)[1]
                    q_per_l = topk // len(spatial_shapes)
                    is_level_ordered = (level_ids[keep_inds][None] == torch.arange(len(spatial_shapes), device=level_ids.device)[:, None])
                    keep_inds_mask = is_level_ordered & (is_level_ordered.cumsum(1) <= q_per_l)
                    keep_inds_mask = keep_inds_mask.any(0)
                    if keep_inds_mask.sum() < topk:
                        num_to_add = topk - keep_inds_mask.sum()
                        pad_inds = (~keep_inds_mask).nonzero()[:num_to_add]
                        keep_inds_mask[pad_inds] = True
                    keep_inds_topk = keep_inds[keep_inds_mask]
                    topk_proposals.append(keep_inds_topk)
                topk_proposals = torch.stack(topk_proposals)
            else: topk_proposals = torch.topk(enc_outputs_class[..., 0], topk, dim=1)[1]
            topk_coords_logits = torch.gather(enc_outputs_coord_logits, 1, topk_proposals.unsqueeze(-1).repeat(1, 1, 4))
            topk_coords_logits = topk_coords_logits.detach()
            reference_points = topk_coords_logits.sigmoid()
            init_reference_points = reference_points
            pos_trans_out = self.pos_trans_norm(self.pos_trans(self.get_proposal_pos_embed(topk_coords_logits)))
            query_embed, target = torch.split(pos_trans_out, num_channels, dim=2)
            topk_feats = torch.stack([object_query_embedding[b][topk_proposals[b]] for b in range(batch_size)]).detach()
            target = target + self.pix_trans_norm(self.pix_trans(topk_feats))
        else:
            query_embed, target = torch.split(query_embeds, num_channels, dim=1)
            query_embed = query_embed.unsqueeze(0).expand(batch_size, -1, -1)
            target = target.unsqueeze(0).expand(batch_size, -1, -1)
            reference_points = self.reference_points(query_embed).sigmoid()
            init_reference_points = reference_points
        decoder_outputs = self.decoder(inputs_embeds=target, position_embeddings=query_embed, encoder_hidden_states=encoder_outputs[0], encoder_attention_mask=mask_flatten,
        reference_points=reference_points, spatial_shapes=spatial_shapes, level_start_index=level_start_index, valid_ratios=valid_ratios, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        if not return_dict:
            enc_outputs = tuple(value for value in [enc_outputs_class, enc_outputs_coord_logits] if value is not None)
            tuple_outputs = (init_reference_points,) + decoder_outputs + encoder_outputs + enc_outputs
            return tuple_outputs
        return DetaModelOutput(init_reference_points=init_reference_points, last_hidden_state=decoder_outputs.last_hidden_state, intermediate_hidden_states=decoder_outputs.intermediate_hidden_states,
        intermediate_reference_points=decoder_outputs.intermediate_reference_points, decoder_hidden_states=decoder_outputs.hidden_states, decoder_attentions=decoder_outputs.attentions,
        cross_attentions=decoder_outputs.cross_attentions, encoder_last_hidden_state=encoder_outputs.last_hidden_state, encoder_hidden_states=encoder_outputs.hidden_states,
        encoder_attentions=encoder_outputs.attentions, enc_outputs_class=enc_outputs_class, enc_outputs_coord_logits=enc_outputs_coord_logits, output_proposals=output_proposals)
@add_start_docstrings("DETA Model (consisting of a backbone and encoder-decoder Transformer) with object detection heads on top, for tasks such as COCO detection.", DETA_START_DOCSTRING)
class DetaForObjectDetection(DetaPreTrainedModel):
    _tied_weights_keys = [r"bbox_embed\.\d+", r"class_embed\.\d+"]
    _no_split_modules = None
    def __init__(self, config: DetaConfig):
        super().__init__(config)
        self.model = DetaModel(config)
        self.class_embed = nn.Linear(config.d_model, config.num_labels)
        self.bbox_embed = DetaMLPPredictionHead(input_dim=config.d_model, hidden_dim=config.d_model, output_dim=4, num_layers=3)
        prior_prob = 0.01
        bias_value = -math.log((1 - prior_prob) / prior_prob)
        self.class_embed.bias.data = torch.ones(config.num_labels) * bias_value
        nn.init.constant_(self.bbox_embed.layers[-1].weight.data, 0)
        nn.init.constant_(self.bbox_embed.layers[-1].bias.data, 0)
        num_pred = (config.decoder_layers + 1) if config.two_stage else config.decoder_layers
        if config.with_box_refine:
            self.class_embed = _get_clones(self.class_embed, num_pred)
            self.bbox_embed = _get_clones(self.bbox_embed, num_pred)
            nn.init.constant_(self.bbox_embed[0].layers[-1].bias.data[2:], -2.0)
            self.model.decoder.bbox_embed = self.bbox_embed
        else:
            nn.init.constant_(self.bbox_embed.layers[-1].bias.data[2:], -2.0)
            self.class_embed = nn.ModuleList([self.class_embed for _ in range(num_pred)])
            self.bbox_embed = nn.ModuleList([self.bbox_embed for _ in range(num_pred)])
            self.model.decoder.bbox_embed = None
        if config.two_stage:
            self.model.decoder.class_embed = self.class_embed
            for box_embed in self.bbox_embed: nn.init.constant_(box_embed.layers[-1].bias.data[2:], 0.0)
        self.post_init()
    @torch.jit.unused
    def _set_aux_loss(self, outputs_class, outputs_coord):
        aux_loss = [{"logits": logits, "pred_boxes": pred_boxes} for logits, pred_boxes in zip(outputs_class.transpose(0, 1)[:-1], outputs_coord.transpose(0, 1)[:-1])]
        return aux_loss
    @add_start_docstrings_to_model_forward(DETA_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, pixel_mask: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.FloatTensor] = None, encoder_outputs: Optional[torch.FloatTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[List[dict]] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], DetaObjectDetectionOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(pixel_values, pixel_mask=pixel_mask, decoder_attention_mask=decoder_attention_mask, encoder_outputs=encoder_outputs, inputs_embeds=inputs_embeds,
        decoder_inputs_embeds=decoder_inputs_embeds, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        hidden_states = outputs.intermediate_hidden_states if return_dict else outputs[2]
        init_reference = outputs.init_reference_points if return_dict else outputs[0]
        inter_references = outputs.intermediate_reference_points if return_dict else outputs[3]
        outputs_classes = []
        outputs_coords = []
        for level in range(hidden_states.shape[1]):
            if level == 0: reference = init_reference
            else: reference = inter_references[:, level - 1]
            reference = inverse_sigmoid(reference)
            outputs_class = self.class_embed[level](hidden_states[:, level])
            delta_bbox = self.bbox_embed[level](hidden_states[:, level])
            if reference.shape[-1] == 4: outputs_coord_logits = delta_bbox + reference
            elif reference.shape[-1] == 2:
                delta_bbox[..., :2] += reference
                outputs_coord_logits = delta_bbox
            else: raise ValueError(f"reference.shape[-1] should be 4 or 2, but got {reference.shape[-1]}")
            outputs_coord = outputs_coord_logits.sigmoid()
            outputs_classes.append(outputs_class)
            outputs_coords.append(outputs_coord)
        outputs_class = torch.stack(outputs_classes, dim=1)
        outputs_coord = torch.stack(outputs_coords, dim=1)
        logits = outputs_class[:, -1]
        pred_boxes = outputs_coord[:, -1]
        loss, loss_dict, auxiliary_outputs = None, None, None
        if labels is not None:
            matcher = DetaHungarianMatcher(class_cost=self.config.class_cost, bbox_cost=self.config.bbox_cost, giou_cost=self.config.giou_cost)
            losses = ["labels", "boxes", "cardinality"]
            criterion = DetaLoss(matcher=matcher, num_classes=self.config.num_labels, focal_alpha=self.config.focal_alpha, losses=losses, num_queries=self.config.num_queries,
            assign_first_stage=self.config.assign_first_stage, assign_second_stage=self.config.assign_second_stage)
            criterion.to(logits.device)
            outputs_loss = {}
            outputs_loss["logits"] = logits
            outputs_loss["pred_boxes"] = pred_boxes
            outputs_loss["init_reference"] = init_reference
            if self.config.auxiliary_loss:
                auxiliary_outputs = self._set_aux_loss(outputs_class, outputs_coord)
                outputs_loss["auxiliary_outputs"] = auxiliary_outputs
            if self.config.two_stage:
                enc_outputs_coord = outputs.enc_outputs_coord_logits.sigmoid()
                outputs_loss["enc_outputs"] = {"logits": outputs.enc_outputs_class, "pred_boxes": enc_outputs_coord, "anchors": outputs.output_proposals.sigmoid()}
            loss_dict = criterion(outputs_loss, labels)
            weight_dict = {"loss_ce": 1, "loss_bbox": self.config.bbox_loss_coefficient}
            weight_dict["loss_giou"] = self.config.giou_loss_coefficient
            if self.config.auxiliary_loss:
                aux_weight_dict = {}
                for i in range(self.config.decoder_layers - 1): aux_weight_dict.update({k + f"_{i}": v for k, v in weight_dict.items()})
                aux_weight_dict.update({k + "_enc": v for k, v in weight_dict.items()})
                weight_dict.update(aux_weight_dict)
            loss = sum(loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict)
        if not return_dict:
            if auxiliary_outputs is not None: output = (logits, pred_boxes) + auxiliary_outputs + outputs
            else: output = (logits, pred_boxes) + outputs
            tuple_outputs = ((loss, loss_dict) + output) if loss is not None else output
            return tuple_outputs
        dict_outputs = DetaObjectDetectionOutput(loss=loss, loss_dict=loss_dict, logits=logits, pred_boxes=pred_boxes, auxiliary_outputs=auxiliary_outputs, last_hidden_state=outputs.last_hidden_state,
        decoder_hidden_states=outputs.decoder_hidden_states, decoder_attentions=outputs.decoder_attentions, cross_attentions=outputs.cross_attentions, encoder_last_hidden_state=outputs.encoder_last_hidden_state,
        encoder_hidden_states=outputs.encoder_hidden_states, encoder_attentions=outputs.encoder_attentions, intermediate_hidden_states=outputs.intermediate_hidden_states, intermediate_reference_points=outputs.intermediate_reference_points,
        init_reference_points=outputs.init_reference_points, enc_outputs_class=outputs.enc_outputs_class, enc_outputs_coord_logits=outputs.enc_outputs_coord_logits, output_proposals=outputs.output_proposals)
        return dict_outputs
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
class DetaLoss(nn.Module):
    def __init__(self, matcher, num_classes, focal_alpha, losses, num_queries, assign_first_stage=False, assign_second_stage=False):
        super().__init__()
        self.matcher = matcher
        self.num_classes = num_classes
        self.focal_alpha = focal_alpha
        self.losses = losses
        self.assign_first_stage = assign_first_stage
        self.assign_second_stage = assign_second_stage
        if self.assign_first_stage: self.stg1_assigner = DetaStage1Assigner()
        if self.assign_second_stage: self.stg2_assigner = DetaStage2Assigner(num_queries)
    def loss_labels(self, outputs, targets, indices, num_boxes):
        if "logits" not in outputs: raise KeyError("No logits were found in the outputs")
        source_logits = outputs["logits"]
        idx = self._get_source_permutation_idx(indices)
        target_classes_o = torch.cat([t["class_labels"][J] for t, (_, J) in zip(targets, indices)])
        target_classes = torch.full(source_logits.shape[:2], self.num_classes, dtype=torch.int64, device=source_logits.device)
        target_classes[idx] = target_classes_o
        target_classes_onehot = torch.zeros([source_logits.shape[0], source_logits.shape[1], source_logits.shape[2] + 1], dtype=source_logits.dtype, layout=source_logits.layout, device=source_logits.device)
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
        outputs_without_aux = {k: v for k, v in outputs.items() if k not in ("auxiliary_outputs", "enc_outputs")}
        if self.assign_second_stage: indices = self.stg2_assigner(outputs_without_aux, targets)
        else: indices = self.matcher(outputs_without_aux, targets)
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
                if not self.assign_second_stage: indices = self.matcher(auxiliary_outputs, targets)
                for loss in self.losses:
                    l_dict = self.get_loss(loss, auxiliary_outputs, targets, indices, num_boxes)
                    l_dict = {k + f"_{i}": v for k, v in l_dict.items()}
                    losses.update(l_dict)
        if "enc_outputs" in outputs:
            enc_outputs = outputs["enc_outputs"]
            bin_targets = copy.deepcopy(targets)
            for bt in bin_targets: bt["class_labels"] = torch.zeros_like(bt["class_labels"])
            if self.assign_first_stage: indices = self.stg1_assigner(enc_outputs, bin_targets)
            else: indices = self.matcher(enc_outputs, bin_targets)
            for loss in self.losses:
                l_dict = self.get_loss(loss, enc_outputs, bin_targets, indices, num_boxes)
                l_dict = {k + "_enc": v for k, v in l_dict.items()}
                losses.update(l_dict)
        return losses
class DetaMLPPredictionHead(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
        super().__init__()
        self.num_layers = num_layers
        h = [hidden_dim] * (num_layers - 1)
        self.layers = nn.ModuleList(nn.Linear(n, k) for n, k in zip([input_dim] + h, h + [output_dim]))
    def forward(self, x):
        for i, layer in enumerate(self.layers): x = nn.functional.relu(layer(x)) if i < self.num_layers - 1 else layer(x)
        return x
class DetaHungarianMatcher(nn.Module):
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
def nonzero_tuple(x):
    if torch.jit.is_scripting():
        if x.dim() == 0: return x.unsqueeze(0).nonzero().unbind(1)
        return x.nonzero().unbind(1)
    else: return x.nonzero(as_tuple=True)
class DetaMatcher:
    def __init__(self, thresholds: List[float], labels: List[int], allow_low_quality_matches: bool = False):
        thresholds = thresholds[:]
        if thresholds[0] < 0: raise ValueError("Thresholds should be positive")
        thresholds.insert(0, -float("inf"))
        thresholds.append(float("inf"))
        if not all(low <= high for (low, high) in zip(thresholds[:-1], thresholds[1:])): raise ValueError("Thresholds should be sorted.")
        if not all(l in [-1, 0, 1] for l in labels): raise ValueError("All labels should be either -1, 0 or 1")
        if len(labels) != len(thresholds) - 1: raise ValueError("Number of labels should be equal to number of thresholds - 1")
        self.thresholds = thresholds
        self.labels = labels
        self.allow_low_quality_matches = allow_low_quality_matches
    def __call__(self, match_quality_matrix):
        assert match_quality_matrix.dim() == 2
        if match_quality_matrix.numel() == 0:
            default_matches = match_quality_matrix.new_full((match_quality_matrix.size(1),), 0, dtype=torch.int64)
            default_match_labels = match_quality_matrix.new_full((match_quality_matrix.size(1),), self.labels[0], dtype=torch.int8)
            return default_matches, default_match_labels
        assert torch.all(match_quality_matrix >= 0)
        matched_vals, matches = match_quality_matrix.max(dim=0)
        match_labels = matches.new_full(matches.size(), 1, dtype=torch.int8)
        for l, low, high in zip(self.labels, self.thresholds[:-1], self.thresholds[1:]):
            low_high = (matched_vals >= low) & (matched_vals < high)
            match_labels[low_high] = l
        if self.allow_low_quality_matches: self.set_low_quality_matches_(match_labels, match_quality_matrix)
        return matches, match_labels
    def set_low_quality_matches_(self, match_labels, match_quality_matrix):
        highest_quality_foreach_gt, _ = match_quality_matrix.max(dim=1)
        _, pred_inds_with_highest_quality = nonzero_tuple(match_quality_matrix == highest_quality_foreach_gt[:, None])
        match_labels[pred_inds_with_highest_quality] = 1
def subsample_labels(labels: torch.Tensor, num_samples: int, positive_fraction: float, bg_label: int):
    positive = nonzero_tuple((labels != -1) & (labels != bg_label))[0]
    negative = nonzero_tuple(labels == bg_label)[0]
    num_pos = int(num_samples * positive_fraction)
    num_pos = min(positive.numel(), num_pos)
    num_neg = num_samples - num_pos
    num_neg = min(negative.numel(), num_neg)
    perm1 = torch.randperm(positive.numel(), device=positive.device)[:num_pos]
    perm2 = torch.randperm(negative.numel(), device=negative.device)[:num_neg]
    pos_idx = positive[perm1]
    neg_idx = negative[perm2]
    return pos_idx, neg_idx
def sample_topk_per_gt(pr_inds, gt_inds, iou, k):
    if len(gt_inds) == 0: return pr_inds, gt_inds
    gt_inds2, counts = gt_inds.unique(return_counts=True)
    scores, pr_inds2 = iou[gt_inds2].topk(k, dim=1)
    gt_inds2 = gt_inds2[:, None].repeat(1, k)
    pr_inds3 = torch.cat([pr[:c] for c, pr in zip(counts, pr_inds2)])
    gt_inds3 = torch.cat([gt[:c] for c, gt in zip(counts, gt_inds2)])
    return pr_inds3, gt_inds3
class DetaStage2Assigner(nn.Module):
    def __init__(self, num_queries, max_k=4):
        super().__init__()
        self.positive_fraction = 0.25
        self.bg_label = 400
        self.batch_size_per_image = num_queries
        self.proposal_matcher = DetaMatcher(thresholds=[0.6], labels=[0, 1], allow_low_quality_matches=True)
        self.k = max_k
    def _sample_proposals(self, matched_idxs: torch.Tensor, matched_labels: torch.Tensor, gt_classes: torch.Tensor):
        has_gt = gt_classes.numel() > 0
        if has_gt:
            gt_classes = gt_classes[matched_idxs]
            gt_classes[matched_labels == 0] = self.bg_label
            gt_classes[matched_labels == -1] = -1
        else: gt_classes = torch.zeros_like(matched_idxs) + self.bg_label
        sampled_fg_idxs, sampled_bg_idxs = subsample_labels(gt_classes, self.batch_size_per_image, self.positive_fraction, self.bg_label)
        sampled_idxs = torch.cat([sampled_fg_idxs, sampled_bg_idxs], dim=0)
        return sampled_idxs, gt_classes[sampled_idxs]
    def forward(self, outputs, targets, return_cost_matrix=False):
        bs = len(targets)
        indices = []
        ious = []
        for b in range(bs):
            iou, _ = box_iou(center_to_corners_format(targets[b]["boxes"]), center_to_corners_format(outputs["init_reference"][b].detach()))
            matched_idxs, matched_labels = self.proposal_matcher(iou)
            (sampled_idxs, sampled_gt_classes) = self._sample_proposals(matched_idxs, matched_labels, targets[b]["class_labels"])
            pos_pr_inds = sampled_idxs[sampled_gt_classes != self.bg_label]
            pos_gt_inds = matched_idxs[pos_pr_inds]
            pos_pr_inds, pos_gt_inds = self.postprocess_indices(pos_pr_inds, pos_gt_inds, iou)
            indices.append((pos_pr_inds, pos_gt_inds))
            ious.append(iou)
        if return_cost_matrix: return indices, ious
        return indices
    def postprocess_indices(self, pr_inds, gt_inds, iou): return sample_topk_per_gt(pr_inds, gt_inds, iou, self.k)
class DetaStage1Assigner(nn.Module):
    def __init__(self, t_low=0.3, t_high=0.7, max_k=4):
        super().__init__()
        self.positive_fraction = 0.5
        self.batch_size_per_image = 256
        self.k = max_k
        self.t_low = t_low
        self.t_high = t_high
        self.anchor_matcher = DetaMatcher(thresholds=[t_low, t_high], labels=[0, -1, 1], allow_low_quality_matches=True)
    def _subsample_labels(self, label):
        pos_idx, neg_idx = subsample_labels(label, self.batch_size_per_image, self.positive_fraction, 0)
        label.fill_(-1)
        label.scatter_(0, pos_idx, 1)
        label.scatter_(0, neg_idx, 0)
        return label
    def forward(self, outputs, targets):
        bs = len(targets)
        indices = []
        for b in range(bs):
            anchors = outputs["anchors"][b]
            if len(targets[b]["boxes"]) == 0:
                indices.append((torch.tensor([], dtype=torch.long, device=anchors.device), torch.tensor([], dtype=torch.long, device=anchors.device),))
                continue
            iou, _ = box_iou(center_to_corners_format(targets[b]["boxes"]), center_to_corners_format(anchors))
            matched_idxs, matched_labels = self.anchor_matcher(iou)
            matched_labels = self._subsample_labels(matched_labels)
            all_pr_inds = torch.arange(len(anchors), device=matched_labels.device)
            pos_pr_inds = all_pr_inds[matched_labels == 1]
            pos_gt_inds = matched_idxs[pos_pr_inds]
            pos_pr_inds, pos_gt_inds = self.postprocess_indices(pos_pr_inds, pos_gt_inds, iou)
            pos_pr_inds, pos_gt_inds = pos_pr_inds.to(anchors.device), pos_gt_inds.to(anchors.device)
            indices.append((pos_pr_inds, pos_gt_inds))
        return indices
    def postprocess_indices(self, pr_inds, gt_inds, iou): return sample_topk_per_gt(pr_inds, gt_inds, iou, self.k)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
