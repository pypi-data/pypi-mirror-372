"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
import os
import warnings
from dataclasses import dataclass
from functools import lru_cache, partial, wraps
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.autograd import Function
from torch.autograd.function import once_differentiable
from ...activations import ACT2CLS, ACT2FN
from ...image_transforms import center_to_corners_format, corners_to_center_format
from ...modeling_outputs import BaseModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, is_ninja_available, is_scipy_available, is_torch_cuda_available,
logging, replace_return_docstrings, requires_backends)
from ...utils.backbone_utils import load_backbone
from .configuration_rt_detr import RTDetrConfig
if is_scipy_available(): from scipy.optimize import linear_sum_assignment
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
_CONFIG_FOR_DOC = "RTDetrConfig"
_CHECKPOINT_FOR_DOC = "PekingU/rtdetr_r50vd"
@dataclass
class RTDetrDecoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_logits: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class RTDetrModelOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_logits: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    init_reference_points: torch.FloatTensor = None
    enc_topk_logits: Optional[torch.FloatTensor] = None
    enc_topk_bboxes: Optional[torch.FloatTensor] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
    denoising_meta_values: Optional[Dict] = None
@dataclass
class RTDetrObjectDetectionOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    loss_dict: Optional[Dict] = None
    logits: torch.FloatTensor = None
    pred_boxes: torch.FloatTensor = None
    auxiliary_outputs: Optional[List[Dict]] = None
    last_hidden_state: torch.FloatTensor = None
    intermediate_hidden_states: torch.FloatTensor = None
    intermediate_logits: torch.FloatTensor = None
    intermediate_reference_points: torch.FloatTensor = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    init_reference_points: Optional[Tuple[torch.FloatTensor]] = None
    enc_topk_logits: Optional[torch.FloatTensor] = None
    enc_topk_bboxes: Optional[torch.FloatTensor] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
    denoising_meta_values: Optional[Dict] = None
def _get_clones(partial_module, N): return nn.ModuleList([partial_module() for i in range(N)])
def inverse_sigmoid(x, eps=1e-5):
    x = x.clamp(min=0, max=1)
    x1 = x.clamp(min=eps)
    x2 = (1 - x).clamp(min=eps)
    return torch.log(x1 / x2)
class RTDetrFrozenBatchNorm2d(nn.Module):
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
            new_module = RTDetrFrozenBatchNorm2d(module.num_features)
            if not module.weight.device == torch.device("meta"):
                new_module.weight.data.copy_(module.weight)
                new_module.bias.data.copy_(module.bias)
                new_module.running_mean.data.copy_(module.running_mean)
                new_module.running_var.data.copy_(module.running_var)
            model._modules[name] = new_module
        if len(list(module.children())) > 0: replace_batch_norm(module)
def get_contrastive_denoising_training_group(targets, num_classes, num_queries, class_embed, num_denoising_queries=100, label_noise_ratio=0.5, box_noise_scale=1.0):
    if num_denoising_queries <= 0: return None, None, None, None
    num_ground_truths = [len(t["class_labels"]) for t in targets]
    device = targets[0]["class_labels"].device
    max_gt_num = max(num_ground_truths)
    if max_gt_num == 0: return None, None, None, None
    num_groups_denoising_queries = num_denoising_queries // max_gt_num
    num_groups_denoising_queries = 1 if num_groups_denoising_queries == 0 else num_groups_denoising_queries
    batch_size = len(num_ground_truths)
    input_query_class = torch.full([batch_size, max_gt_num], num_classes, dtype=torch.int32, device=device)
    input_query_bbox = torch.zeros([batch_size, max_gt_num, 4], device=device)
    pad_gt_mask = torch.zeros([batch_size, max_gt_num], dtype=torch.bool, device=device)
    for i in range(batch_size):
        num_gt = num_ground_truths[i]
        if num_gt > 0:
            input_query_class[i, :num_gt] = targets[i]["class_labels"]
            input_query_bbox[i, :num_gt] = targets[i]["boxes"]
            pad_gt_mask[i, :num_gt] = 1
    input_query_class = input_query_class.tile([1, 2 * num_groups_denoising_queries])
    input_query_bbox = input_query_bbox.tile([1, 2 * num_groups_denoising_queries, 1])
    pad_gt_mask = pad_gt_mask.tile([1, 2 * num_groups_denoising_queries])
    negative_gt_mask = torch.zeros([batch_size, max_gt_num * 2, 1], device=device)
    negative_gt_mask[:, max_gt_num:] = 1
    negative_gt_mask = negative_gt_mask.tile([1, num_groups_denoising_queries, 1])
    positive_gt_mask = 1 - negative_gt_mask
    positive_gt_mask = positive_gt_mask.squeeze(-1) * pad_gt_mask
    denoise_positive_idx = torch.nonzero(positive_gt_mask)[:, 1]
    denoise_positive_idx = torch.split(denoise_positive_idx, [n * num_groups_denoising_queries for n in num_ground_truths])
    num_denoising_queries = int(max_gt_num * 2 * num_groups_denoising_queries)
    if label_noise_ratio > 0:
        mask = torch.rand_like(input_query_class, dtype=torch.float) < (label_noise_ratio * 0.5)
        new_label = torch.randint_like(mask, 0, num_classes, dtype=input_query_class.dtype)
        input_query_class = torch.where(mask & pad_gt_mask, new_label, input_query_class)
    if box_noise_scale > 0:
        known_bbox = center_to_corners_format(input_query_bbox)
        diff = torch.tile(input_query_bbox[..., 2:] * 0.5, [1, 1, 2]) * box_noise_scale
        rand_sign = torch.randint_like(input_query_bbox, 0, 2) * 2.0 - 1.0
        rand_part = torch.rand_like(input_query_bbox)
        rand_part = (rand_part + 1.0) * negative_gt_mask + rand_part * (1 - negative_gt_mask)
        rand_part *= rand_sign
        known_bbox += rand_part * diff
        known_bbox.clip_(min=0.0, max=1.0)
        input_query_bbox = corners_to_center_format(known_bbox)
        input_query_bbox = inverse_sigmoid(input_query_bbox)
    input_query_class = class_embed(input_query_class)
    target_size = num_denoising_queries + num_queries
    attn_mask = torch.full([target_size, target_size], False, dtype=torch.bool, device=device)
    attn_mask[num_denoising_queries:, :num_denoising_queries] = True
    for i in range(num_groups_denoising_queries):
        idx_block_start = max_gt_num * 2 * i
        idx_block_end = max_gt_num * 2 * (i + 1)
        attn_mask[idx_block_start:idx_block_end, :idx_block_start] = True
        attn_mask[idx_block_start:idx_block_end, idx_block_end:num_denoising_queries] = True
    denoising_meta_values = {"dn_positive_idx": denoise_positive_idx, "dn_num_group": num_groups_denoising_queries, "dn_num_split": [num_denoising_queries, num_queries]}
    return input_query_class, input_query_bbox, attn_mask, denoising_meta_values
class RTDetrConvEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        backbone = load_backbone(config)
        if config.freeze_backbone_batch_norms:
            with torch.no_grad(): replace_batch_norm(backbone)
        self.model = backbone
        self.intermediate_channel_sizes = self.model.channels
    def forward(self, pixel_values: torch.Tensor, pixel_mask: torch.Tensor):
        features = self.model(pixel_values).feature_maps
        out = []
        for feature_map in features:
            mask = nn.functional.interpolate(pixel_mask[None].float(), size=feature_map.shape[-2:]).to(torch.bool)[0]
            out.append((feature_map, mask))
        return out
class RTDetrConvNormLayer(nn.Module):
    def __init__(self, config, in_channels, out_channels, kernel_size, stride, padding=None, activation=None):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding=(kernel_size - 1) // 2 if padding is None else padding, bias=False)
        self.norm = nn.BatchNorm2d(out_channels, config.batch_norm_eps)
        self.activation = nn.Identity() if activation is None else ACT2CLS[activation]()
    def forward(self, hidden_state):
        hidden_state = self.conv(hidden_state)
        hidden_state = self.norm(hidden_state)
        hidden_state = self.activation(hidden_state)
        return hidden_state
class RTDetrEncoderLayer(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        self.normalize_before = config.normalize_before
        self.self_attn = RTDetrMultiheadAttention(embed_dim=config.encoder_hidden_dim, num_heads=config.num_attention_heads, dropout=config.dropout)
        self.self_attn_layer_norm = nn.LayerNorm(config.encoder_hidden_dim, eps=config.layer_norm_eps)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.encoder_activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(config.encoder_hidden_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, config.encoder_hidden_dim)
        self.final_layer_norm = nn.LayerNorm(config.encoder_hidden_dim, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor, position_embeddings: torch.Tensor = None, output_attentions: bool = False, **kwargs):
        residual = hidden_states
        if self.normalize_before: hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states, attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=attention_mask, position_embeddings=position_embeddings, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if not self.normalize_before: hidden_states = self.self_attn_layer_norm(hidden_states)
        if self.normalize_before: hidden_states = self.final_layer_norm(hidden_states)
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if not self.normalize_before: hidden_states = self.final_layer_norm(hidden_states)
        if self.training:
            if torch.isinf(hidden_states).any() or torch.isnan(hidden_states).any():
                clamp_value = torch.finfo(hidden_states.dtype).max - 1000
                hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        outputs = (hidden_states,)
        if output_attentions: outputs += (attn_weights,)
        return outputs
class RTDetrRepVggBlock(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        activation = config.activation_function
        hidden_channels = int(config.encoder_hidden_dim * config.hidden_expansion)
        self.conv1 = RTDetrConvNormLayer(config, hidden_channels, hidden_channels, 3, 1, padding=1)
        self.conv2 = RTDetrConvNormLayer(config, hidden_channels, hidden_channels, 1, 1, padding=0)
        self.activation = nn.Identity() if activation is None else ACT2CLS[activation]()
    def forward(self, x):
        y = self.conv1(x) + self.conv2(x)
        return self.activation(y)
class RTDetrCSPRepLayer(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        in_channels = config.encoder_hidden_dim * 2
        out_channels = config.encoder_hidden_dim
        num_blocks = 3
        activation = config.activation_function
        hidden_channels = int(out_channels * config.hidden_expansion)
        self.conv1 = RTDetrConvNormLayer(config, in_channels, hidden_channels, 1, 1, activation=activation)
        self.conv2 = RTDetrConvNormLayer(config, in_channels, hidden_channels, 1, 1, activation=activation)
        self.bottlenecks = nn.Sequential(*[RTDetrRepVggBlock(config) for _ in range(num_blocks)])
        if hidden_channels != out_channels: self.conv3 = RTDetrConvNormLayer(config, hidden_channels, out_channels, 1, 1, activation=activation)
        else: self.conv3 = nn.Identity()
    def forward(self, hidden_state):
        device = hidden_state.device
        hidden_state_1 = self.conv1(hidden_state)
        hidden_state_1 = self.bottlenecks(hidden_state_1).to(device)
        hidden_state_2 = self.conv2(hidden_state).to(device)
        return self.conv3(hidden_state_1 + hidden_state_2)
def multi_scale_deformable_attention(value: Tensor, value_spatial_shapes: Tensor, sampling_locations: Tensor, attention_weights: Tensor) -> Tensor:
    batch_size, _, num_heads, hidden_dim = value.shape
    _, num_queries, num_heads, num_levels, num_points, _ = sampling_locations.shape
    value_list = value.split([height * width for height, width in value_spatial_shapes], dim=1)
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
class RTDetrMultiscaleDeformableAttention(nn.Module):
    def __init__(self, config: RTDetrConfig, num_heads: int, n_points: int):
        super().__init__()
        kernel_loaded = MultiScaleDeformableAttention is not None
        if is_torch_cuda_available() and is_ninja_available() and not kernel_loaded:
            try: load_cuda_kernels()
            except Exception as e: logger.warning(f"Could not load the custom kernel for multi-scale deformable attention: {e}")
        if config.d_model % num_heads != 0: raise ValueError(f"embed_dim (d_model) must be divisible by num_heads, but got {config.d_model} and {num_heads}")
        dim_per_head = config.d_model // num_heads
        if not ((dim_per_head & (dim_per_head - 1) == 0) and dim_per_head != 0): warnings.warn("You'd better set embed_dim (d_model) in RTDetrMultiscaleDeformableAttention to make the dimension of each attention head a power of 2 which is more efficient in the authors' CUDA implementation.")
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
    reference_points=None, spatial_shapes=None, spatial_shapes_list=None, level_start_index=None, output_attentions: bool = False):
        if position_embeddings is not None: hidden_states = self.with_pos_embed(hidden_states, position_embeddings)
        batch_size, num_queries, _ = hidden_states.shape
        batch_size, sequence_length, _ = encoder_hidden_states.shape
        total_elements = sum(shape[0] * shape[1] for shape in spatial_shapes_list)
        if total_elements != sequence_length: raise ValueError("Make sure to align the spatial shapes with the sequence length of the encoder hidden states")
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
        if self.disable_custom_kernels or MultiScaleDeformableAttention is None: output = multi_scale_deformable_attention(value, spatial_shapes_list, sampling_locations, attention_weights)
        else:
            try: output = MultiScaleDeformableAttentionFunction.apply(value, spatial_shapes, level_start_index, sampling_locations, attention_weights, self.im2col_step)
            except Exception: output = multi_scale_deformable_attention(value, spatial_shapes_list, sampling_locations, attention_weights)
        output = self.output_proj(output)
        return output, attention_weights
class RTDetrMultiheadAttention(nn.Module):
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
    def _reshape(self, tensor: torch.Tensor, seq_len: int, batch_size: int): return tensor.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def with_pos_embed(self, tensor: torch.Tensor, position_embeddings: Optional[Tensor]): return tensor if position_embeddings is None else tensor + position_embeddings
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, position_embeddings: Optional[torch.Tensor] = None,
    output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        batch_size, target_len, embed_dim = hidden_states.size()
        if position_embeddings is not None:
            hidden_states_original = hidden_states
            hidden_states = self.with_pos_embed(hidden_states, position_embeddings)
        query_states = self.q_proj(hidden_states) * self.scaling
        key_states = self._reshape(self.k_proj(hidden_states), -1, batch_size)
        value_states = self._reshape(self.v_proj(hidden_states_original), -1, batch_size)
        proj_shape = (batch_size * self.num_heads, -1, self.head_dim)
        query_states = self._reshape(query_states, target_len, batch_size).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        source_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (batch_size * self.num_heads, target_len, source_len): raise ValueError(f"Attention weights should be of size {(batch_size * self.num_heads, target_len, source_len)}, but is {attn_weights.size()}")
        if attention_mask is not None: attention_mask = attention_mask.expand(batch_size, 1, *attention_mask.size())
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
class RTDetrDecoderLayer(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        self.self_attn = RTDetrMultiheadAttention(embed_dim=config.d_model, num_heads=config.decoder_attention_heads, dropout=config.attention_dropout)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.decoder_activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.encoder_attn = RTDetrMultiscaleDeformableAttention(config, num_heads=config.decoder_attention_heads, n_points=config.decoder_n_points)
        self.encoder_attn_layer_norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.fc1 = nn.Linear(config.d_model, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, config.d_model)
        self.final_layer_norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, position_embeddings: Optional[torch.Tensor] = None, reference_points=None, spatial_shapes=None, spatial_shapes_list=None,
    level_start_index=None, encoder_hidden_states: Optional[torch.Tensor] = None, encoder_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False):
        residual = hidden_states
        hidden_states, self_attn_weights = self.self_attn(hidden_states=hidden_states, attention_mask=encoder_attention_mask, position_embeddings=position_embeddings, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        second_residual = hidden_states
        cross_attn_weights = None
        hidden_states, cross_attn_weights = self.encoder_attn(hidden_states=hidden_states, encoder_hidden_states=encoder_hidden_states, position_embeddings=position_embeddings,
        reference_points=reference_points, spatial_shapes=spatial_shapes, spatial_shapes_list=spatial_shapes_list, level_start_index=level_start_index, output_attentions=output_attentions)
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
class RTDetrPreTrainedModel(PreTrainedModel):
    config_class = RTDetrConfig
    base_model_prefix = "rt_detr"
    main_input_name = "pixel_values"
    _no_split_modules = [r"RTDetrConvEncoder", r"RTDetrEncoderLayer", r"RTDetrDecoderLayer"]
    def _init_weights(self, module):
        if isinstance(module, (RTDetrForObjectDetection, RTDetrDecoder)):
            if module.class_embed is not None:
                for layer in module.class_embed:
                    prior_prob = self.config.initializer_bias_prior_prob or 1 / (self.config.num_labels + 1)
                    bias = float(-math.log((1 - prior_prob) / prior_prob))
                    nn.init.xavier_uniform_(layer.weight)
                    nn.init.constant_(layer.bias, bias)
            if module.bbox_embed is not None:
                for layer in module.bbox_embed:
                    nn.init.constant_(layer.layers[-1].weight, 0)
                    nn.init.constant_(layer.layers[-1].bias, 0)
        if isinstance(module, RTDetrModel):
            prior_prob = self.config.initializer_bias_prior_prob or 1 / (self.config.num_labels + 1)
            bias = float(-math.log((1 - prior_prob) / prior_prob))
            nn.init.xavier_uniform_(module.enc_score_head.weight)
            nn.init.constant_(module.enc_score_head.bias, bias)
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        if hasattr(module, "weight_embedding") and self.config.learn_initial_query: nn.init.xavier_uniform_(module.weight_embedding.weight)
        if hasattr(module, "denoising_class_embed") and self.config.num_denoising > 0: nn.init.xavier_uniform_(module.denoising_class_embed.weight)
RTDETR_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`RTDetrConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
RTDETR_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Padding will be ignored by default should you provide it. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`RTDetrImageProcessor.__call__`] for details.
        pixel_mask (`torch.LongTensor` of shape `(batch_size, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            [What are attention masks?](../glossary#attention-mask)
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
        labels (`List[Dict]` of len `(batch_size,)`, *optional*):
            Labels for computing the bipartite matching loss. List of dicts, each dictionary containing at least the
            following 2 keys: 'class_labels' and 'boxes' (the class labels and bounding boxes of an image in the batch
            respectively). The class labels themselves should be a `torch.LongTensor` of len `(number of bounding boxes
            in the image,)` and the boxes a `torch.FloatTensor` of shape `(number of bounding boxes in the image, 4)`.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
class RTDetrEncoder(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        self.layers = nn.ModuleList([RTDetrEncoderLayer(config) for _ in range(config.encoder_layers)])
    def forward(self, src, src_mask=None, pos_embed=None, output_attentions: bool = False) -> torch.Tensor:
        hidden_states = src
        for layer in self.layers: hidden_states = layer(hidden_states, attention_mask=src_mask, position_embeddings=pos_embed, output_attentions=output_attentions)
        return hidden_states
class RTDetrHybridEncoder(nn.Module):
    def __init__(self, config: RTDetrConfig):
        super().__init__()
        self.config = config
        self.in_channels = config.encoder_in_channels
        self.feat_strides = config.feat_strides
        self.encoder_hidden_dim = config.encoder_hidden_dim
        self.encode_proj_layers = config.encode_proj_layers
        self.positional_encoding_temperature = config.positional_encoding_temperature
        self.eval_size = config.eval_size
        self.out_channels = [self.encoder_hidden_dim for _ in self.in_channels]
        self.out_strides = self.feat_strides
        activation_function = config.activation_function
        self.encoder = nn.ModuleList([RTDetrEncoder(config) for _ in range(len(self.encode_proj_layers))])
        self.lateral_convs = nn.ModuleList()
        self.fpn_blocks = nn.ModuleList()
        for _ in range(len(self.in_channels) - 1, 0, -1):
            self.lateral_convs.append(RTDetrConvNormLayer(config, self.encoder_hidden_dim, self.encoder_hidden_dim, 1, 1, activation=activation_function))
            self.fpn_blocks.append(RTDetrCSPRepLayer(config))
        self.downsample_convs = nn.ModuleList()
        self.pan_blocks = nn.ModuleList()
        for _ in range(len(self.in_channels) - 1):
            self.downsample_convs.append(RTDetrConvNormLayer(config, self.encoder_hidden_dim, self.encoder_hidden_dim, 3, 2, activation=activation_function))
            self.pan_blocks.append(RTDetrCSPRepLayer(config))
    @staticmethod
    def build_2d_sincos_position_embedding(width, height, embed_dim=256, temperature=10000.0, device="cpu", dtype=torch.float32):
        grid_w = torch.arange(int(width), dtype=dtype, device=device)
        grid_h = torch.arange(int(height), dtype=dtype, device=device)
        grid_w, grid_h = torch.meshgrid(grid_w, grid_h, indexing="ij")
        if embed_dim % 4 != 0: raise ValueError("Embed dimension must be divisible by 4 for 2D sin-cos position embedding")
        pos_dim = embed_dim // 4
        omega = torch.arange(pos_dim, dtype=dtype, device=device) / pos_dim
        omega = 1.0 / (temperature**omega)
        out_w = grid_w.flatten()[..., None] @ omega[None]
        out_h = grid_h.flatten()[..., None] @ omega[None]
        return torch.concat([out_w.sin(), out_w.cos(), out_h.sin(), out_h.cos()], dim=1)[None, :, :]
    def forward(self, inputs_embeds=None, attention_mask=None, position_embeddings=None, spatial_shapes=None, level_start_index=None, valid_ratios=None,
    output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states = inputs_embeds
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        if self.config.encoder_layers > 0:
            for i, enc_ind in enumerate(self.encode_proj_layers):
                if output_hidden_states: encoder_states = encoder_states + (hidden_states[enc_ind],)
                height, width = hidden_states[enc_ind].shape[2:]
                src_flatten = hidden_states[enc_ind].flatten(2).permute(0, 2, 1)
                if self.training or self.eval_size is None: pos_embed = self.build_2d_sincos_position_embedding(width, height, self.encoder_hidden_dim, self.positional_encoding_temperature,
                device=src_flatten.device, dtype=src_flatten.dtype)
                else: pos_embed = None
                layer_outputs = self.encoder[i](src_flatten, pos_embed=pos_embed, output_attentions=output_attentions)
                hidden_states[enc_ind] = (layer_outputs[0].permute(0, 2, 1).reshape(-1, self.encoder_hidden_dim, height, width).contiguous())
                if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
            if output_hidden_states: encoder_states = encoder_states + (hidden_states[enc_ind],)
        fpn_feature_maps = [hidden_states[-1]]
        for idx in range(len(self.in_channels) - 1, 0, -1):
            feat_high = fpn_feature_maps[0]
            feat_low = hidden_states[idx - 1]
            feat_high = self.lateral_convs[len(self.in_channels) - 1 - idx](feat_high)
            fpn_feature_maps[0] = feat_high
            upsample_feat = F.interpolate(feat_high, scale_factor=2.0, mode="nearest")
            fps_map = self.fpn_blocks[len(self.in_channels) - 1 - idx](torch.concat([upsample_feat, feat_low], dim=1))
            fpn_feature_maps.insert(0, fps_map)
        fpn_states = [fpn_feature_maps[0]]
        for idx in range(len(self.in_channels) - 1):
            feat_low = fpn_states[-1]
            feat_high = fpn_feature_maps[idx + 1]
            downsample_feat = self.downsample_convs[idx](feat_low)
            hidden_states = self.pan_blocks[idx](torch.concat([downsample_feat, feat_high.to(downsample_feat.device)], dim=1))
            fpn_states.append(hidden_states)
        if not return_dict: return tuple(v for v in [fpn_states, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(last_hidden_state=fpn_states, hidden_states=encoder_states, attentions=all_attentions)
class RTDetrDecoder(RTDetrPreTrainedModel):
    def __init__(self, config: RTDetrConfig):
        super().__init__(config)
        self.dropout = config.dropout
        self.layers = nn.ModuleList([RTDetrDecoderLayer(config) for _ in range(config.decoder_layers)])
        self.query_pos_head = RTDetrMLPPredictionHead(config, 4, 2 * config.d_model, config.d_model, num_layers=2)
        self.bbox_embed = None
        self.class_embed = None
        self.post_init()
    def forward(self, inputs_embeds=None, encoder_hidden_states=None, encoder_attention_mask=None, position_embeddings=None, reference_points=None, spatial_shapes=None,
    spatial_shapes_list=None, level_start_index=None, valid_ratios=None, output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is not None: hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        intermediate = ()
        intermediate_reference_points = ()
        intermediate_logits = ()
        reference_points = F.sigmoid(reference_points)
        for idx, decoder_layer in enumerate(self.layers):
            reference_points_input = reference_points.unsqueeze(2)
            position_embeddings = self.query_pos_head(reference_points)
            if output_hidden_states: all_hidden_states += (hidden_states,)
            layer_outputs = decoder_layer(hidden_states, position_embeddings=position_embeddings, encoder_hidden_states=encoder_hidden_states, reference_points=reference_points_input,
            spatial_shapes=spatial_shapes, spatial_shapes_list=spatial_shapes_list, level_start_index=level_start_index, encoder_attention_mask=encoder_attention_mask,
            output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if self.bbox_embed is not None:
                tmp = self.bbox_embed[idx](hidden_states)
                new_reference_points = F.sigmoid(tmp + inverse_sigmoid(reference_points))
                reference_points = new_reference_points.detach()
            intermediate += (hidden_states,)
            intermediate_reference_points += ((new_reference_points,) if self.bbox_embed is not None else (reference_points,))
            if self.class_embed is not None:
                logits = self.class_embed[idx](hidden_states)
                intermediate_logits += (logits,)
            if output_attentions:
                all_self_attns += (layer_outputs[1],)
                if encoder_hidden_states is not None: all_cross_attentions += (layer_outputs[2],)
        intermediate = torch.stack(intermediate, dim=1)
        intermediate_reference_points = torch.stack(intermediate_reference_points, dim=1)
        if self.class_embed is not None: intermediate_logits = torch.stack(intermediate_logits, dim=1)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, intermediate, intermediate_logits, intermediate_reference_points, all_hidden_states, all_self_attns, all_cross_attentions] if v is not None)
        return RTDetrDecoderOutput(last_hidden_state=hidden_states, intermediate_hidden_states=intermediate, intermediate_logits=intermediate_logits, intermediate_reference_points=intermediate_reference_points,
        hidden_states=all_hidden_states, attentions=all_self_attns, cross_attentions=all_cross_attentions)
def compile_compatible_lru_cache(*lru_args, **lru_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not torch.compiler.is_compiling():
                if not hasattr(self, f"_cached_{func.__name__}"): self.__setattr__(f"_cached_{func.__name__}", lru_cache(*lru_args, **lru_kwargs)(func.__get__(self)))
                return self.__getattribute__(f"_cached_{func.__name__}")(*args, **kwargs)
            else: return func(self, *args, **kwargs)
        return wrapper
    return decorator
@add_start_docstrings("RT-DETR Model (consisting of a backbone and encoder-decoder) outputting raw hidden states without any head on top.", RTDETR_START_DOCSTRING)
class RTDetrModel(RTDetrPreTrainedModel):
    def __init__(self, config: RTDetrConfig):
        super().__init__(config)
        self.backbone = RTDetrConvEncoder(config)
        intermediate_channel_sizes = self.backbone.intermediate_channel_sizes
        num_backbone_outs = len(intermediate_channel_sizes)
        encoder_input_proj_list = []
        for _ in range(num_backbone_outs):
            in_channels = intermediate_channel_sizes[_]
            encoder_input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.encoder_hidden_dim, kernel_size=1, bias=False), nn.BatchNorm2d(config.encoder_hidden_dim)))
        self.encoder_input_proj = nn.ModuleList(encoder_input_proj_list)
        self.encoder = RTDetrHybridEncoder(config)
        if config.num_denoising > 0: self.denoising_class_embed = nn.Embedding(config.num_labels + 1, config.d_model, padding_idx=config.num_labels)
        if config.learn_initial_query: self.weight_embedding = nn.Embedding(config.num_queries, config.d_model)
        self.enc_output = nn.Sequential(nn.Linear(config.d_model, config.d_model), nn.LayerNorm(config.d_model, eps=config.layer_norm_eps))
        self.enc_score_head = nn.Linear(config.d_model, config.num_labels)
        self.enc_bbox_head = RTDetrMLPPredictionHead(config, config.d_model, config.d_model, 4, num_layers=3)
        if config.anchor_image_size: self.anchors, self.valid_mask = self.generate_anchors(dtype=self.dtype)
        num_backbone_outs = len(config.decoder_in_channels)
        decoder_input_proj_list = []
        for _ in range(num_backbone_outs):
            in_channels = config.decoder_in_channels[_]
            decoder_input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=1, bias=False), nn.BatchNorm2d(config.d_model, config.batch_norm_eps)))
        for _ in range(config.num_feature_levels - num_backbone_outs):
            decoder_input_proj_list.append(nn.Sequential(nn.Conv2d(in_channels, config.d_model, kernel_size=3, stride=2, padding=1, bias=False), nn.BatchNorm2d(config.d_model, config.batch_norm_eps)))
            in_channels = config.d_model
        self.decoder_input_proj = nn.ModuleList(decoder_input_proj_list)
        self.decoder = RTDetrDecoder(config)
        self.post_init()
    def get_encoder(self): return self.encoder
    def get_decoder(self): return self.decoder
    def freeze_backbone(self):
        for param in self.backbone.parameters(): param.requires_grad_(False)
    def unfreeze_backbone(self):
        for param in self.backbone.parameters(): param.requires_grad_(True)
    @compile_compatible_lru_cache(maxsize=32)
    def generate_anchors(self, spatial_shapes=None, grid_size=0.05, device="cpu", dtype=torch.float32):
        if spatial_shapes is None: spatial_shapes = [[int(self.config.anchor_image_size[0] / s), int(self.config.anchor_image_size[1] / s)] for s in self.config.feat_strides]
        anchors = []
        for level, (height, width) in enumerate(spatial_shapes):
            grid_y, grid_x = torch.meshgrid(torch.arange(end=height, dtype=dtype, device=device), torch.arange(end=width, dtype=dtype, device=device), indexing="ij")
            grid_xy = torch.stack([grid_x, grid_y], -1)
            valid_wh = torch.tensor([width, height], device=device).to(dtype)
            grid_xy = (grid_xy.unsqueeze(0) + 0.5) / valid_wh
            wh = torch.ones_like(grid_xy) * grid_size * (2.0**level)
            anchors.append(torch.concat([grid_xy, wh], -1).reshape(-1, height * width, 4))
        eps = 1e-2
        anchors = torch.concat(anchors, 1)
        valid_mask = ((anchors > eps) * (anchors < 1 - eps)).all(-1, keepdim=True)
        anchors = torch.log(anchors / (1 - anchors))
        anchors = torch.where(valid_mask, anchors, torch.inf)
        return anchors, valid_mask
    @add_start_docstrings_to_model_forward(RTDETR_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, pixel_mask: Optional[torch.LongTensor] = None, encoder_outputs: Optional[torch.FloatTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[List[dict]] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], RTDetrModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, num_channels, height, width = pixel_values.shape
        device = pixel_values.device
        if pixel_mask is None: pixel_mask = torch.ones(((batch_size, height, width)), device=device)
        features = self.backbone(pixel_values, pixel_mask)
        proj_feats = [self.encoder_input_proj[level](source) for level, (source, mask) in enumerate(features)]
        if encoder_outputs is None: encoder_outputs = self.encoder(proj_feats, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        elif return_dict and not isinstance(encoder_outputs, BaseModelOutput): encoder_outputs = BaseModelOutput(last_hidden_state=encoder_outputs[0], hidden_states=encoder_outputs[1] if output_hidden_states else None,
        attentions=encoder_outputs[2] if len(encoder_outputs) > 2 else encoder_outputs[1] if output_attentions else None)
        sources = []
        for level, source in enumerate(encoder_outputs[0]): sources.append(self.decoder_input_proj[level](source))
        if self.config.num_feature_levels > len(sources):
            _len_sources = len(sources)
            sources.append(self.decoder_input_proj[_len_sources](encoder_outputs[0])[-1])
            for i in range(_len_sources + 1, self.config.num_feature_levels): sources.append(self.decoder_input_proj[i](encoder_outputs[0][-1]))
        source_flatten = []
        spatial_shapes_list = []
        for level, source in enumerate(sources):
            batch_size, num_channels, height, width = source.shape
            spatial_shape = (height, width)
            spatial_shapes_list.append(spatial_shape)
            source = source.flatten(2).transpose(1, 2)
            source_flatten.append(source)
        source_flatten = torch.cat(source_flatten, 1)
        spatial_shapes = torch.as_tensor(spatial_shapes_list, dtype=torch.long, device=source_flatten.device)
        level_start_index = torch.cat((spatial_shapes.new_zeros((1,)), spatial_shapes.prod(1).cumsum(0)[:-1]))
        if self.training and self.config.num_denoising > 0 and labels is not None: (denoising_class, denoising_bbox_unact, attention_mask, denoising_meta_values) = get_contrastive_denoising_training_group(targets=labels,
        num_classes=self.config.num_labels, num_queries=self.config.num_queries, class_embed=self.denoising_class_embed, num_denoising_queries=self.config.num_denoising,
        label_noise_ratio=self.config.label_noise_ratio, box_noise_scale=self.config.box_noise_scale)
        else: denoising_class, denoising_bbox_unact, attention_mask, denoising_meta_values = None, None, None, None
        batch_size = len(source_flatten)
        device = source_flatten.device
        dtype = source_flatten.dtype
        if self.training or self.config.anchor_image_size is None:
            spatial_shapes_tuple = tuple(spatial_shapes_list)
            anchors, valid_mask = self.generate_anchors(spatial_shapes_tuple, device=device, dtype=dtype)
        else: anchors, valid_mask = self.anchors, self.valid_mask
        anchors, valid_mask = anchors.to(device, dtype), valid_mask.to(device, dtype)
        memory = valid_mask.to(source_flatten.dtype) * source_flatten
        output_memory = self.enc_output(memory)
        enc_outputs_class = self.enc_score_head(output_memory)
        enc_outputs_coord_logits = self.enc_bbox_head(output_memory) + anchors
        _, topk_ind = torch.topk(enc_outputs_class.max(-1).values, self.config.num_queries, dim=1)
        reference_points_unact = enc_outputs_coord_logits.gather(dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, enc_outputs_coord_logits.shape[-1]))
        enc_topk_bboxes = F.sigmoid(reference_points_unact)
        if denoising_bbox_unact is not None: reference_points_unact = torch.concat([denoising_bbox_unact, reference_points_unact], 1)
        enc_topk_logits = enc_outputs_class.gather(dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, enc_outputs_class.shape[-1]))
        if self.config.learn_initial_query: target = self.weight_embedding.tile([batch_size, 1, 1])
        else:
            target = output_memory.gather(dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, output_memory.shape[-1]))
            target = target.detach()
        if denoising_class is not None: target = torch.concat([denoising_class, target], 1)
        init_reference_points = reference_points_unact.detach()
        decoder_outputs = self.decoder(inputs_embeds=target, encoder_hidden_states=source_flatten, encoder_attention_mask=attention_mask, reference_points=init_reference_points,
        spatial_shapes=spatial_shapes, spatial_shapes_list=spatial_shapes_list, level_start_index=level_start_index, output_attentions=output_attentions,
        output_hidden_states=output_hidden_states, return_dict=return_dict)
        if not return_dict:
            enc_outputs = tuple(value for value in [enc_topk_logits, enc_topk_bboxes, enc_outputs_class, enc_outputs_coord_logits] if value is not None)
            dn_outputs = tuple(value if value is not None else None for value in [denoising_meta_values])
            tuple_outputs = decoder_outputs + encoder_outputs + (init_reference_points,) + enc_outputs + dn_outputs
            return tuple_outputs
        return RTDetrModelOutput(last_hidden_state=decoder_outputs.last_hidden_state, intermediate_hidden_states=decoder_outputs.intermediate_hidden_states,
        intermediate_logits=decoder_outputs.intermediate_logits, intermediate_reference_points=decoder_outputs.intermediate_reference_points,
        decoder_hidden_states=decoder_outputs.hidden_states, decoder_attentions=decoder_outputs.attentions, cross_attentions=decoder_outputs.cross_attentions,
        encoder_last_hidden_state=encoder_outputs.last_hidden_state, encoder_hidden_states=encoder_outputs.hidden_states, encoder_attentions=encoder_outputs.attentions,
        init_reference_points=init_reference_points, enc_topk_logits=enc_topk_logits, enc_topk_bboxes=enc_topk_bboxes, enc_outputs_class=enc_outputs_class,
        enc_outputs_coord_logits=enc_outputs_coord_logits, denoising_meta_values=denoising_meta_values)
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
class RTDetrLoss(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.matcher = RTDetrHungarianMatcher(config)
        self.num_classes = config.num_labels
        self.weight_dict = {"loss_vfl": config.weight_loss_vfl, "loss_bbox": config.weight_loss_bbox, "loss_giou": config.weight_loss_giou}
        self.losses = ["vfl", "boxes"]
        self.eos_coef = config.eos_coefficient
        empty_weight = torch.ones(config.num_labels + 1)
        empty_weight[-1] = self.eos_coef
        self.register_buffer("empty_weight", empty_weight)
        self.alpha = config.focal_loss_alpha
        self.gamma = config.focal_loss_gamma
    def loss_labels_vfl(self, outputs, targets, indices, num_boxes, log=True):
        if "pred_boxes" not in outputs: raise KeyError("No predicted boxes found in outputs")
        if "logits" not in outputs: raise KeyError("No predicted logits found in outputs")
        idx = self._get_source_permutation_idx(indices)
        src_boxes = outputs["pred_boxes"][idx]
        target_boxes = torch.cat([_target["boxes"][i] for _target, (_, i) in zip(targets, indices)], dim=0)
        ious, _ = box_iou(center_to_corners_format(src_boxes), center_to_corners_format(target_boxes))
        ious = torch.diag(ious).detach()
        src_logits = outputs["logits"]
        target_classes_original = torch.cat([_target["class_labels"][i] for _target, (_, i) in zip(targets, indices)])
        target_classes = torch.full(src_logits.shape[:2], self.num_classes, dtype=torch.int64, device=src_logits.device)
        target_classes[idx] = target_classes_original
        target = F.one_hot(target_classes, num_classes=self.num_classes + 1)[..., :-1]
        target_score_original = torch.zeros_like(target_classes, dtype=src_logits.dtype)
        target_score_original[idx] = ious.to(target_score_original.dtype)
        target_score = target_score_original.unsqueeze(-1) * target
        pred_score = F.sigmoid(src_logits).detach()
        weight = self.alpha * pred_score.pow(self.gamma) * (1 - target) + target_score
        loss = F.binary_cross_entropy_with_logits(src_logits, target_score, weight=weight, reduction="none")
        loss = loss.mean(1).sum() * src_logits.shape[1] / num_boxes
        return {"loss_vfl": loss}
    def loss_labels(self, outputs, targets, indices, num_boxes, log=True):
        if "logits" not in outputs: raise KeyError("No logits were found in the outputs")
        src_logits = outputs["logits"]
        idx = self._get_source_permutation_idx(indices)
        target_classes_original = torch.cat([_target["class_labels"][i] for _target, (_, i) in zip(targets, indices)])
        target_classes = torch.full(src_logits.shape[:2], self.num_classes, dtype=torch.int64, device=src_logits.device)
        target_classes[idx] = target_classes_original
        loss_ce = F.cross_entropy(src_logits.transpose(1, 2), target_classes, self.class_weight)
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
        src_boxes = outputs["pred_boxes"][idx]
        target_boxes = torch.cat([t["boxes"][i] for t, (_, i) in zip(targets, indices)], dim=0)
        losses = {}
        loss_bbox = F.l1_loss(src_boxes, target_boxes, reduction="none")
        losses["loss_bbox"] = loss_bbox.sum() / num_boxes
        loss_giou = 1 - torch.diag(generalized_box_iou(center_to_corners_format(src_boxes), center_to_corners_format(target_boxes)))
        losses["loss_giou"] = loss_giou.sum() / num_boxes
        return losses
    def loss_masks(self, outputs, targets, indices, num_boxes):
        if "pred_masks" not in outputs: raise KeyError("No predicted masks found in outputs")
        source_idx = self._get_source_permutation_idx(indices)
        target_idx = self._get_target_permutation_idx(indices)
        source_masks = outputs["pred_masks"]
        source_masks = source_masks[source_idx]
        masks = [t["masks"] for t in targets]
        target_masks, valid = nested_tensor_from_tensor_list(masks).decompose()
        target_masks = target_masks.to(source_masks)
        target_masks = target_masks[target_idx]
        source_masks = nn.functional.interpolate(source_masks[:, None], size=target_masks.shape[-2:], mode="bilinear", align_corners=False)
        source_masks = source_masks[:, 0].flatten(1)
        target_masks = target_masks.flatten(1)
        target_masks = target_masks.view(source_masks.shape)
        losses = {"loss_mask": sigmoid_focal_loss(source_masks, target_masks, num_boxes), "loss_dice": dice_loss(source_masks, target_masks, num_boxes)}
        return losses
    def loss_labels_bce(self, outputs, targets, indices, num_boxes, log=True):
        src_logits = outputs["logits"]
        idx = self._get_source_permutation_idx(indices)
        target_classes_original = torch.cat([_target["class_labels"][i] for _target, (_, i) in zip(targets, indices)])
        target_classes = torch.full(src_logits.shape[:2], self.num_classes, dtype=torch.int64, device=src_logits.device)
        target_classes[idx] = target_classes_original
        target = F.one_hot(target_classes, num_classes=self.num_classes + 1)[..., :-1]
        loss = F.binary_cross_entropy_with_logits(src_logits, target * 1.0, reduction="none")
        loss = loss.mean(1).sum() * src_logits.shape[1] / num_boxes
        return {"loss_bce": loss}
    def _get_source_permutation_idx(self, indices):
        batch_idx = torch.cat([torch.full_like(source, i) for i, (source, _) in enumerate(indices)])
        source_idx = torch.cat([source for (source, _) in indices])
        return batch_idx, source_idx
    def _get_target_permutation_idx(self, indices):
        batch_idx = torch.cat([torch.full_like(target, i) for i, (_, target) in enumerate(indices)])
        target_idx = torch.cat([target for (_, target) in indices])
        return batch_idx, target_idx
    def loss_labels_focal(self, outputs, targets, indices, num_boxes, log=True):
        if "logits" not in outputs: raise KeyError("No logits found in outputs")
        src_logits = outputs["logits"]
        idx = self._get_source_permutation_idx(indices)
        target_classes_original = torch.cat([_target["class_labels"][i] for _target, (_, i) in zip(targets, indices)])
        target_classes = torch.full(src_logits.shape[:2], self.num_classes, dtype=torch.int64, device=src_logits.device)
        target_classes[idx] = target_classes_original
        target = F.one_hot(target_classes, num_classes=self.num_classes + 1)[..., :-1]
        loss = sigmoid_focal_loss(src_logits, target, self.alpha, self.gamma)
        loss = loss.mean(1).sum() * src_logits.shape[1] / num_boxes
        return {"loss_focal": loss}
    def get_loss(self, loss, outputs, targets, indices, num_boxes):
        loss_map = {"labels": self.loss_labels, "cardinality": self.loss_cardinality, "boxes": self.loss_boxes, "masks": self.loss_masks, "bce": self.loss_labels_bce, "focal": self.loss_labels_focal, "vfl": self.loss_labels_vfl}
        if loss not in loss_map: raise ValueError(f"Loss {loss} not supported")
        return loss_map[loss](outputs, targets, indices, num_boxes)
    @staticmethod
    def get_cdn_matched_indices(dn_meta, targets):
        dn_positive_idx, dn_num_group = dn_meta["dn_positive_idx"], dn_meta["dn_num_group"]
        num_gts = [len(t["class_labels"]) for t in targets]
        device = targets[0]["class_labels"].device
        dn_match_indices = []
        for i, num_gt in enumerate(num_gts):
            if num_gt > 0:
                gt_idx = torch.arange(num_gt, dtype=torch.int64, device=device)
                gt_idx = gt_idx.tile(dn_num_group)
                assert len(dn_positive_idx[i]) == len(gt_idx)
                dn_match_indices.append((dn_positive_idx[i], gt_idx))
            else: dn_match_indices.append((torch.zeros(0, dtype=torch.int64, device=device), torch.zeros(0, dtype=torch.int64, device=device)))
        return dn_match_indices
    def forward(self, outputs, targets):
        outputs_without_aux = {k: v for k, v in outputs.items() if "auxiliary_outputs" not in k}
        indices = self.matcher(outputs_without_aux, targets)
        num_boxes = sum(len(t["class_labels"]) for t in targets)
        num_boxes = torch.as_tensor([num_boxes], dtype=torch.float, device=next(iter(outputs.values())).device)
        num_boxes = torch.clamp(num_boxes, min=1).item()
        losses = {}
        for loss in self.losses:
            l_dict = self.get_loss(loss, outputs, targets, indices, num_boxes)
            l_dict = {k: l_dict[k] * self.weight_dict[k] for k in l_dict if k in self.weight_dict}
            losses.update(l_dict)
        if "auxiliary_outputs" in outputs:
            for i, auxiliary_outputs in enumerate(outputs["auxiliary_outputs"]):
                indices = self.matcher(auxiliary_outputs, targets)
                for loss in self.losses:
                    if loss == "masks": continue
                    l_dict = self.get_loss(loss, auxiliary_outputs, targets, indices, num_boxes)
                    l_dict = {k: l_dict[k] * self.weight_dict[k] for k in l_dict if k in self.weight_dict}
                    l_dict = {k + f"_aux_{i}": v for k, v in l_dict.items()}
                    losses.update(l_dict)
        if "dn_auxiliary_outputs" in outputs:
            if "denoising_meta_values" not in outputs: raise ValueError("The output must have the 'denoising_meta_values` key. Please, ensure that 'outputs' includes a 'denoising_meta_values' entry.")
            indices = self.get_cdn_matched_indices(outputs["denoising_meta_values"], targets)
            num_boxes = num_boxes * outputs["denoising_meta_values"]["dn_num_group"]
            for i, auxiliary_outputs in enumerate(outputs["dn_auxiliary_outputs"]):
                for loss in self.losses:
                    if loss == "masks": continue
                    kwargs = {}
                    l_dict = self.get_loss(loss, auxiliary_outputs, targets, indices, num_boxes, **kwargs)
                    l_dict = {k: l_dict[k] * self.weight_dict[k] for k in l_dict if k in self.weight_dict}
                    l_dict = {k + f"_dn_{i}": v for k, v in l_dict.items()}
                    losses.update(l_dict)
        return losses
class RTDetrMLPPredictionHead(nn.Module):
    def __init__(self, config, input_dim, d_model, output_dim, num_layers):
        super().__init__()
        self.num_layers = num_layers
        h = [d_model] * (num_layers - 1)
        self.layers = nn.ModuleList(nn.Linear(n, k) for n, k in zip([input_dim] + h, h + [output_dim]))
    def forward(self, x):
        for i, layer in enumerate(self.layers): x = nn.functional.relu(layer(x)) if i < self.num_layers - 1 else layer(x)
        return x
class RTDetrHungarianMatcher(nn.Module):
    def __init__(self, config):
        super().__init__()
        requires_backends(self, ["scipy"])
        self.class_cost = config.matcher_class_cost
        self.bbox_cost = config.matcher_bbox_cost
        self.giou_cost = config.matcher_giou_cost
        self.use_focal_loss = config.use_focal_loss
        self.alpha = config.matcher_alpha
        self.gamma = config.matcher_gamma
        if self.class_cost == self.bbox_cost == self.giou_cost == 0: raise ValueError("All costs of the Matcher can't be 0")
    @torch.no_grad()
    def forward(self, outputs, targets):
        batch_size, num_queries = outputs["logits"].shape[:2]
        out_bbox = outputs["pred_boxes"].flatten(0, 1)
        target_ids = torch.cat([v["class_labels"] for v in targets])
        target_bbox = torch.cat([v["boxes"] for v in targets])
        if self.use_focal_loss:
            out_prob = F.sigmoid(outputs["logits"].flatten(0, 1))
            out_prob = out_prob[:, target_ids]
            neg_cost_class = (1 - self.alpha) * (out_prob**self.gamma) * (-(1 - out_prob + 1e-8).log())
            pos_cost_class = self.alpha * ((1 - out_prob) ** self.gamma) * (-(out_prob + 1e-8).log())
            class_cost = pos_cost_class - neg_cost_class
        else:
            out_prob = outputs["logits"].flatten(0, 1).softmax(-1)
            class_cost = -out_prob[:, target_ids]
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
def _max_by_axis(the_list):
    maxes = the_list[0]
    for sublist in the_list[1:]:
        for index, item in enumerate(sublist): maxes[index] = max(maxes[index], item)
    return maxes
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
@add_start_docstrings("RT-DETR Model (consisting of a backbone and encoder-decoder) outputting bounding boxes and logits to be further decoded into scores and classes.", RTDETR_START_DOCSTRING)
class RTDetrForObjectDetection(RTDetrPreTrainedModel):
    _tied_weights_keys = ["bbox_embed", "class_embed"]
    _no_split_modules = None
    def __init__(self, config: RTDetrConfig):
        super().__init__(config)
        self.model = RTDetrModel(config)
        self.class_embed = partial(nn.Linear, config.d_model, config.num_labels)
        self.bbox_embed = partial(RTDetrMLPPredictionHead, config, config.d_model, config.d_model, 4, num_layers=3)
        num_pred = config.decoder_layers
        if config.with_box_refine:
            self.class_embed = _get_clones(self.class_embed, num_pred)
            self.bbox_embed = _get_clones(self.bbox_embed, num_pred)
        else:
            self.class_embed = nn.ModuleList([self.class_embed() for _ in range(num_pred)])
            self.bbox_embed = nn.ModuleList([self.bbox_embed() for _ in range(num_pred)])
        self.model.decoder.class_embed = self.class_embed
        self.model.decoder.bbox_embed = self.bbox_embed
        self.post_init()
    @torch.jit.unused
    def _set_aux_loss(self, outputs_class, outputs_coord): return [{"logits": a, "pred_boxes": b} for a, b in zip(outputs_class, outputs_coord)]
    @add_start_docstrings_to_model_forward(RTDETR_INPUTS_DOCSTRING)
    def forward(self, pixel_values: torch.FloatTensor, pixel_mask: Optional[torch.LongTensor] = None, encoder_outputs: Optional[torch.FloatTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, decoder_inputs_embeds: Optional[torch.FloatTensor] = None, labels: Optional[List[dict]] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], RTDetrObjectDetectionOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(pixel_values, pixel_mask=pixel_mask, encoder_outputs=encoder_outputs, inputs_embeds=inputs_embeds, decoder_inputs_embeds=decoder_inputs_embeds,
        labels=labels, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        denoising_meta_values = (outputs.denoising_meta_values if return_dict else outputs[-1] if self.training else None)
        outputs_class = outputs.intermediate_logits if return_dict else outputs[2]
        outputs_coord = outputs.intermediate_reference_points if return_dict else outputs[3]
        if self.training and denoising_meta_values is not None:
            dn_out_coord, outputs_coord = torch.split(outputs_coord, denoising_meta_values["dn_num_split"], dim=2)
            dn_out_class, outputs_class = torch.split(outputs_class, denoising_meta_values["dn_num_split"], dim=2)
        logits = outputs_class[:, -1]
        pred_boxes = outputs_coord[:, -1]
        loss, loss_dict, auxiliary_outputs = None, None, None
        if labels is not None:
            criterion = RTDetrLoss(self.config)
            criterion.to(self.device)
            outputs_loss = {}
            outputs_loss["logits"] = logits
            outputs_loss["pred_boxes"] = pred_boxes
            if self.config.auxiliary_loss:
                enc_topk_logits = outputs.enc_topk_logits if return_dict else outputs[-5]
                enc_topk_bboxes = outputs.enc_topk_bboxes if return_dict else outputs[-4]
                auxiliary_outputs = self._set_aux_loss(outputs_class[:, :-1].transpose(0, 1), outputs_coord[:, :-1].transpose(0, 1))
                outputs_loss["auxiliary_outputs"] = auxiliary_outputs
                outputs_loss["auxiliary_outputs"].extend(self._set_aux_loss([enc_topk_logits], [enc_topk_bboxes]))
                if self.training and denoising_meta_values is not None:
                    outputs_loss["dn_auxiliary_outputs"] = self._set_aux_loss(dn_out_class.transpose(0, 1), dn_out_coord.transpose(0, 1))
                    outputs_loss["denoising_meta_values"] = denoising_meta_values
            loss_dict = criterion(outputs_loss, labels)
            loss = sum(loss_dict.values())
        if not return_dict:
            if auxiliary_outputs is not None: output = (logits, pred_boxes) + (auxiliary_outputs,) + outputs
            else: output = (logits, pred_boxes) + outputs
            return ((loss, loss_dict) + output) if loss is not None else output
        return RTDetrObjectDetectionOutput(loss=loss, loss_dict=loss_dict, logits=logits, pred_boxes=pred_boxes, auxiliary_outputs=auxiliary_outputs, last_hidden_state=outputs.last_hidden_state,
        intermediate_hidden_states=outputs.intermediate_hidden_states, intermediate_logits=outputs.intermediate_logits, intermediate_reference_points=outputs.intermediate_reference_points,
        decoder_hidden_states=outputs.decoder_hidden_states, decoder_attentions=outputs.decoder_attentions, cross_attentions=outputs.cross_attentions, encoder_last_hidden_state=outputs.encoder_last_hidden_state,
        encoder_hidden_states=outputs.encoder_hidden_states, encoder_attentions=outputs.encoder_attentions, init_reference_points=outputs.init_reference_points, enc_topk_logits=outputs.enc_topk_logits,
        enc_topk_bboxes=outputs.enc_topk_bboxes, enc_outputs_class=outputs.enc_outputs_class, enc_outputs_coord_logits=outputs.enc_outputs_coord_logits, denoising_meta_values=outputs.denoising_meta_values)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
