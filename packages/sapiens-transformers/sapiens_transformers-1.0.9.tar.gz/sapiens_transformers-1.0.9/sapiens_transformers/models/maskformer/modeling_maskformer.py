"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from numbers import Number
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch import Tensor, nn
from ...activations import ACT2FN
from ...modeling_attn_mask_utils import _prepare_4d_attention_mask
from ...modeling_outputs import BaseModelOutputWithCrossAttentions
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import is_torch_greater_or_equal_than_2_1
from ...utils import (ModelOutput, add_start_docstrings, add_start_docstrings_to_model_forward, is_sapiens_accelerator_available, is_scipy_available, logging, replace_return_docstrings, requires_backends)
from ...utils.backbone_utils import load_backbone
from ...utils.import_utils import is_torchdynamo_compiling
from ..detr import DetrConfig
from .configuration_maskformer import MaskFormerConfig
from .configuration_maskformer_swin import MaskFormerSwinConfig
if is_sapiens_accelerator_available():
    from sapiens_accelerator import PartialState
    from sapiens_accelerator.utils import reduce
if is_scipy_available(): from scipy.optimize import linear_sum_assignment
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "MaskFormerConfig"
_CHECKPOINT_FOR_DOC = "facebook/maskformer-swin-base-ade"
@dataclass
class DetrDecoderOutput(BaseModelOutputWithCrossAttentions):
    """Args:"""
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
@dataclass
class MaskFormerPixelLevelModuleOutput(ModelOutput):
    """Args:"""
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    decoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class MaskFormerPixelDecoderOutput(ModelOutput):
    """Args:"""
    last_hidden_state: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class MaskFormerModelOutput(ModelOutput):
    """Args:"""
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    pixel_decoder_last_hidden_state: Optional[torch.FloatTensor] = None
    transformer_decoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    pixel_decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    transformer_decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
@dataclass
class MaskFormerForInstanceSegmentationOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    class_queries_logits: torch.FloatTensor = None
    masks_queries_logits: torch.FloatTensor = None
    auxiliary_logits: torch.FloatTensor = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    pixel_decoder_last_hidden_state: Optional[torch.FloatTensor] = None
    transformer_decoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    pixel_decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    transformer_decoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None
def upsample_like(pixel_values: Tensor, like: Tensor, mode: str = "bilinear") -> Tensor:
    _, _, height, width = like.shape
    upsampled = nn.functional.interpolate(pixel_values, size=(height, width), mode=mode, align_corners=False)
    return upsampled
def dice_loss(inputs: Tensor, labels: Tensor, num_masks: int) -> Tensor:
    probs = inputs.sigmoid().flatten(1)
    numerator = 2 * (probs * labels).sum(-1)
    denominator = probs.sum(-1) + labels.sum(-1)
    loss = 1 - (numerator + 1) / (denominator + 1)
    loss = loss.sum() / num_masks
    return loss
def sigmoid_focal_loss(inputs: Tensor, labels: Tensor, num_masks: int, alpha: float = 0.25, gamma: float = 2) -> Tensor:
    criterion = nn.BCEWithLogitsLoss(reduction="none")
    probs = inputs.sigmoid()
    cross_entropy_loss = criterion(inputs, labels)
    p_t = probs * labels + (1 - probs) * (1 - labels)
    loss = cross_entropy_loss * ((1 - p_t) ** gamma)
    if alpha >= 0:
        alpha_t = alpha * labels + (1 - alpha) * (1 - labels)
        loss = alpha_t * loss
    loss = loss.mean(1).sum() / num_masks
    return loss
def pair_wise_dice_loss(inputs: Tensor, labels: Tensor) -> Tensor:
    inputs = inputs.sigmoid().flatten(1)
    numerator = 2 * torch.matmul(inputs, labels.T)
    denominator = inputs.sum(-1)[:, None] + labels.sum(-1)[None, :]
    loss = 1 - (numerator + 1) / (denominator + 1)
    return loss
def pair_wise_sigmoid_focal_loss(inputs: Tensor, labels: Tensor, alpha: float = 0.25, gamma: float = 2.0) -> Tensor:
    if alpha < 0: raise ValueError("alpha must be positive")
    height_and_width = inputs.shape[1]
    criterion = nn.BCEWithLogitsLoss(reduction="none")
    prob = inputs.sigmoid()
    cross_entropy_loss_pos = criterion(inputs, torch.ones_like(inputs))
    focal_pos = ((1 - prob) ** gamma) * cross_entropy_loss_pos
    focal_pos *= alpha
    cross_entropy_loss_neg = criterion(inputs, torch.zeros_like(inputs))
    focal_neg = (prob**gamma) * cross_entropy_loss_neg
    focal_neg *= 1 - alpha
    loss = torch.matmul(focal_pos, labels.T) + torch.matmul(focal_neg, (1 - labels).T)
    return loss / height_and_width
class DetrAttention(nn.Module):
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
    def with_pos_embed(self, tensor: torch.Tensor, object_queries: Optional[Tensor]): return tensor if object_queries is None else tensor + object_queries
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, object_queries: Optional[torch.Tensor] = None, key_value_states: Optional[torch.Tensor] = None,
    spatial_position_embeddings: Optional[torch.Tensor] = None, output_attentions: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        is_cross_attention = key_value_states is not None
        batch_size, target_len, embed_dim = hidden_states.size()
        if object_queries is not None:
            hidden_states_original = hidden_states
            hidden_states = self.with_pos_embed(hidden_states, object_queries)
        if spatial_position_embeddings is not None:
            key_value_states_original = key_value_states
            key_value_states = self.with_pos_embed(key_value_states, spatial_position_embeddings)
        query_states = self.q_proj(hidden_states) * self.scaling
        if is_cross_attention:
            key_states = self._shape(self.k_proj(key_value_states), -1, batch_size)
            value_states = self._shape(self.v_proj(key_value_states_original), -1, batch_size)
        else:
            key_states = self._shape(self.k_proj(hidden_states), -1, batch_size)
            value_states = self._shape(self.v_proj(hidden_states_original), -1, batch_size)
        proj_shape = (batch_size * self.num_heads, -1, self.head_dim)
        query_states = self._shape(query_states, target_len, batch_size).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        source_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (batch_size * self.num_heads, target_len, source_len): raise ValueError(f"Attention weights should be of size {(batch_size * self.num_heads, target_len, source_len)}, but is {attn_weights.size()}")
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
class DetrDecoderLayer(nn.Module):
    def __init__(self, config: DetrConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = DetrAttention(embed_dim=self.embed_dim, num_heads=config.decoder_attention_heads, dropout=config.attention_dropout)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.encoder_attn = DetrAttention(self.embed_dim, config.decoder_attention_heads, dropout=config.attention_dropout)
        self.encoder_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.fc1 = nn.Linear(self.embed_dim, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None, object_queries: Optional[torch.Tensor] = None, query_position_embeddings: Optional[torch.Tensor] = None,
    encoder_hidden_states: Optional[torch.Tensor] = None, encoder_attention_mask: Optional[torch.Tensor] = None, output_attentions: Optional[bool] = False):
        residual = hidden_states
        hidden_states, self_attn_weights = self.self_attn(hidden_states=hidden_states, object_queries=query_position_embeddings, attention_mask=attention_mask, output_attentions=output_attentions)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        cross_attn_weights = None
        if encoder_hidden_states is not None:
            residual = hidden_states
            hidden_states, cross_attn_weights = self.encoder_attn(hidden_states=hidden_states, object_queries=query_position_embeddings, key_value_states=encoder_hidden_states,
            attention_mask=encoder_attention_mask, spatial_position_embeddings=object_queries, output_attentions=output_attentions)
            hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
            hidden_states = residual + hidden_states
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
class DetrDecoder(nn.Module):
    def __init__(self, config: DetrConfig):
        super().__init__()
        self.config = config
        self.dropout = config.dropout
        self.layerdrop = config.decoder_layerdrop
        self.layers = nn.ModuleList([DetrDecoderLayer(config) for _ in range(config.decoder_layers)])
        self.layernorm = nn.LayerNorm(config.d_model)
        self.gradient_checkpointing = False
    def forward(self, inputs_embeds=None, attention_mask=None, encoder_hidden_states=None, encoder_attention_mask=None, object_queries=None, query_position_embeddings=None,
    output_attentions=None, output_hidden_states=None, return_dict=None):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is not None:
            hidden_states = inputs_embeds
            input_shape = inputs_embeds.size()[:-1]
        if encoder_hidden_states is not None and encoder_attention_mask is not None: encoder_attention_mask = _prepare_4d_attention_mask(encoder_attention_mask, inputs_embeds.dtype, tgt_len=input_shape[-1])
        intermediate = () if self.config.auxiliary_loss else None
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states: all_hidden_states += (hidden_states,)
            if self.training:
                dropout_probability = torch.rand([])
                if dropout_probability < self.layerdrop: continue
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(decoder_layer.__call__, hidden_states, None, encoder_hidden_states, encoder_attention_mask, None, output_attentions)
            else:
                layer_outputs = decoder_layer(hidden_states, attention_mask=None, object_queries=object_queries, query_position_embeddings=query_position_embeddings,
                encoder_hidden_states=encoder_hidden_states, encoder_attention_mask=encoder_attention_mask, output_attentions=output_attentions)
            hidden_states = layer_outputs[0]
            if self.config.auxiliary_loss:
                hidden_states = self.layernorm(hidden_states)
                intermediate += (hidden_states,)
            if output_attentions:
                all_self_attns += (layer_outputs[1],)
                if encoder_hidden_states is not None: all_cross_attentions += (layer_outputs[2],)
        hidden_states = self.layernorm(hidden_states)
        if output_hidden_states: all_hidden_states += (hidden_states,)
        if self.config.auxiliary_loss: intermediate = torch.stack(intermediate)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states, all_self_attns, all_cross_attentions, intermediate] if v is not None)
        return DetrDecoderOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_self_attns, cross_attentions=all_cross_attentions, intermediate_hidden_states=intermediate)
class MaskFormerHungarianMatcher(nn.Module):
    def __init__(self, cost_class: float = 1.0, cost_mask: float = 1.0, cost_dice: float = 1.0):
        super().__init__()
        if cost_class == 0 and cost_mask == 0 and cost_dice == 0: raise ValueError("All costs cant be 0")
        self.cost_class = cost_class
        self.cost_mask = cost_mask
        self.cost_dice = cost_dice
    @torch.no_grad()
    def forward(self, masks_queries_logits, class_queries_logits, mask_labels, class_labels) -> List[Tuple[Tensor]]:
        indices: List[Tuple[np.array]] = []
        preds_masks = masks_queries_logits
        preds_probs = class_queries_logits
        for pred_probs, pred_mask, target_mask, labels in zip(preds_probs, preds_masks, mask_labels, class_labels):
            target_mask = nn.functional.interpolate(target_mask[:, None], size=pred_mask.shape[-2:], mode="nearest")
            pred_probs = pred_probs.softmax(-1)
            cost_class = -pred_probs[:, labels]
            pred_mask_flat = pred_mask.flatten(1)
            target_mask_flat = target_mask[:, 0].flatten(1)
            cost_mask = pair_wise_sigmoid_focal_loss(pred_mask_flat, target_mask_flat)
            cost_dice = pair_wise_dice_loss(pred_mask_flat, target_mask_flat)
            cost_matrix = self.cost_mask * cost_mask + self.cost_class * cost_class + self.cost_dice * cost_dice
            assigned_indices: Tuple[np.array] = linear_sum_assignment(cost_matrix.cpu())
            indices.append(assigned_indices)
        matched_indices = [(torch.as_tensor(i, dtype=torch.int64), torch.as_tensor(j, dtype=torch.int64)) for i, j in indices]
        return matched_indices
    def __repr__(self):
        head = "Matcher " + self.__class__.__name__
        body = [f"cost_class: {self.cost_class}", f"cost_mask: {self.cost_mask}", f"cost_dice: {self.cost_dice}"]
        _repr_indent = 4
        lines = [head] + [" " * _repr_indent + line for line in body]
        return "\n".join(lines)
class MaskFormerLoss(nn.Module):
    def __init__(self, num_labels: int, matcher: MaskFormerHungarianMatcher, weight_dict: Dict[str, float], eos_coef: float):
        super().__init__()
        requires_backends(self, ["scipy"])
        self.num_labels = num_labels
        self.matcher = matcher
        self.weight_dict = weight_dict
        self.eos_coef = eos_coef
        empty_weight = torch.ones(self.num_labels + 1)
        empty_weight[-1] = self.eos_coef
        self.register_buffer("empty_weight", empty_weight)
    def _max_by_axis(self, the_list: List[List[int]]) -> List[int]:
        maxes = the_list[0]
        for sublist in the_list[1:]:
            for index, item in enumerate(sublist): maxes[index] = max(maxes[index], item)
        return maxes
    def _pad_images_to_max_in_batch(self, tensors: List[Tensor]) -> Tuple[Tensor, Tensor]:
        max_size = self._max_by_axis([list(tensor.shape) for tensor in tensors])
        batch_size = len(tensors)
        batch_shape = [batch_size] + max_size
        b, _, h, w = batch_shape
        dtype = tensors[0].dtype
        device = tensors[0].device
        padded_tensors = torch.zeros(batch_shape, dtype=dtype, device=device)
        padding_masks = torch.ones((b, h, w), dtype=torch.bool, device=device)
        for tensor, padded_tensor, padding_mask in zip(tensors, padded_tensors, padding_masks):
            padded_tensor[: tensor.shape[0], : tensor.shape[1], : tensor.shape[2]].copy_(tensor)
            padding_mask[: tensor.shape[1], : tensor.shape[2]] = False
        return padded_tensors, padding_masks
    def loss_labels(self, class_queries_logits: Tensor, class_labels: List[Tensor], indices: Tuple[np.array]) -> Dict[str, Tensor]:
        pred_logits = class_queries_logits
        batch_size, num_queries, _ = pred_logits.shape
        criterion = nn.CrossEntropyLoss(weight=self.empty_weight)
        idx = self._get_predictions_permutation_indices(indices)
        target_classes_o = torch.cat([target[j] for target, (_, j) in zip(class_labels, indices)])
        target_classes = torch.full((batch_size, num_queries), fill_value=self.num_labels, dtype=torch.int64, device=pred_logits.device)
        target_classes[idx] = target_classes_o
        pred_logits_transposed = pred_logits.transpose(1, 2)
        loss_ce = criterion(pred_logits_transposed, target_classes)
        losses = {"loss_cross_entropy": loss_ce}
        return losses
    def loss_masks(self, masks_queries_logits: Tensor, mask_labels: List[Tensor], indices: Tuple[np.array], num_masks: int) -> Dict[str, Tensor]:
        src_idx = self._get_predictions_permutation_indices(indices)
        tgt_idx = self._get_targets_permutation_indices(indices)
        pred_masks = masks_queries_logits[src_idx]
        target_masks, _ = self._pad_images_to_max_in_batch(mask_labels)
        target_masks = target_masks[tgt_idx]
        pred_masks = nn.functional.interpolate(pred_masks[:, None], size=target_masks.shape[-2:], mode="bilinear", align_corners=False)
        pred_masks = pred_masks[:, 0].flatten(1)
        target_masks = target_masks.flatten(1)
        losses = {"loss_mask": sigmoid_focal_loss(pred_masks, target_masks, num_masks), "loss_dice": dice_loss(pred_masks, target_masks, num_masks)}
        return losses
    def _get_predictions_permutation_indices(self, indices):
        batch_indices = torch.cat([torch.full_like(src, i) for i, (src, _) in enumerate(indices)])
        predictions_indices = torch.cat([src for (src, _) in indices])
        return batch_indices, predictions_indices
    def _get_targets_permutation_indices(self, indices):
        batch_indices = torch.cat([torch.full_like(tgt, i) for i, (_, tgt) in enumerate(indices)])
        target_indices = torch.cat([tgt for (_, tgt) in indices])
        return batch_indices, target_indices
    def forward(self, masks_queries_logits: Tensor, class_queries_logits: Tensor, mask_labels: List[Tensor], class_labels: List[Tensor], auxiliary_predictions: Optional[Dict[str, Tensor]] = None) -> Dict[str, Tensor]:
        indices = self.matcher(masks_queries_logits, class_queries_logits, mask_labels, class_labels)
        num_masks: Number = self.get_num_masks(class_labels, device=class_labels[0].device)
        losses: Dict[str, Tensor] = {**self.loss_masks(masks_queries_logits, mask_labels, indices, num_masks), **self.loss_labels(class_queries_logits, class_labels, indices)}
        if auxiliary_predictions is not None:
            for idx, aux_outputs in enumerate(auxiliary_predictions):
                masks_queries_logits = aux_outputs["masks_queries_logits"]
                class_queries_logits = aux_outputs["class_queries_logits"]
                loss_dict = self.forward(masks_queries_logits, class_queries_logits, mask_labels, class_labels)
                loss_dict = {f"{key}_{idx}": value for key, value in loss_dict.items()}
                losses.update(loss_dict)
        return losses
    def get_num_masks(self, class_labels: torch.Tensor, device: torch.device) -> torch.Tensor:
        num_masks = sum([len(classes) for classes in class_labels])
        num_masks = torch.as_tensor(num_masks, dtype=torch.float, device=device)
        world_size = 1
        if is_sapiens_accelerator_available():
            if PartialState._shared_state != {}:
                num_masks = reduce(num_masks)
                world_size = PartialState().num_processes
        num_masks = torch.clamp(num_masks / world_size, min=1)
        return num_masks
class MaskFormerFPNConvLayer(nn.Module):
    def __init__(self, in_features: int, out_features: int, kernel_size: int = 3, padding: int = 1):
        super().__init__()
        self.layers = [nn.Conv2d(in_features, out_features, kernel_size=kernel_size, padding=padding, bias=False), nn.GroupNorm(32, out_features), nn.ReLU(inplace=True)]
        for i, layer in enumerate(self.layers): self.add_module(str(i), layer)
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class MaskFormerFPNLayer(nn.Module):
    def __init__(self, in_features: int, lateral_features: int):
        super().__init__()
        self.proj = nn.Sequential(nn.Conv2d(lateral_features, in_features, kernel_size=1, padding=0, bias=False), nn.GroupNorm(32, in_features))
        self.block = MaskFormerFPNConvLayer(in_features, in_features)
    def forward(self, down: Tensor, left: Tensor) -> Tensor:
        left = self.proj(left)
        down = nn.functional.interpolate(down, size=left.shape[-2:], mode="nearest")
        down += left
        down = self.block(down)
        return down
class MaskFormerFPNModel(nn.Module):
    def __init__(self, in_features: int, lateral_widths: List[int], feature_size: int = 256):
        super().__init__()
        self.stem = MaskFormerFPNConvLayer(in_features, feature_size)
        self.layers = nn.Sequential(*[MaskFormerFPNLayer(feature_size, lateral_width) for lateral_width in lateral_widths[::-1]])
    def forward(self, features: List[Tensor]) -> List[Tensor]:
        fpn_features = []
        last_feature = features[-1]
        other_features = features[:-1]
        output = self.stem(last_feature)
        for layer, left in zip(self.layers, other_features[::-1]):
            output = layer(output, left)
            fpn_features.append(output)
        return fpn_features
class MaskFormerPixelDecoder(nn.Module):
    def __init__(self, *args, feature_size: int = 256, mask_feature_size: int = 256, **kwargs):
        super().__init__()
        self.fpn = MaskFormerFPNModel(*args, feature_size=feature_size, **kwargs)
        self.mask_projection = nn.Conv2d(feature_size, mask_feature_size, kernel_size=3, padding=1)
    def forward(self, features: List[Tensor], output_hidden_states: bool = False, return_dict: bool = True) -> MaskFormerPixelDecoderOutput:
        fpn_features = self.fpn(features)
        last_feature_projected = self.mask_projection(fpn_features[-1])
        if not return_dict: return (last_feature_projected, tuple(fpn_features)) if output_hidden_states else (last_feature_projected,)
        return MaskFormerPixelDecoderOutput(last_hidden_state=last_feature_projected, hidden_states=tuple(fpn_features) if output_hidden_states else ())
class MaskFormerSinePositionEmbedding(nn.Module):
    def __init__(self, num_pos_feats: int = 64, temperature: int = 10000, normalize: bool = False, scale: Optional[float] = None):
        super().__init__()
        if scale is not None and normalize is False: raise ValueError("normalize should be True if scale is passed")
        self.num_pos_feats = num_pos_feats
        self.temperature = temperature
        self.normalize = normalize
        self.scale = 2 * math.pi if scale is None else scale
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        if mask is None: mask = torch.zeros((x.size(0), x.size(2), x.size(3)), device=x.device, dtype=torch.bool)
        not_mask = (~mask).to(x.dtype)
        y_embed = not_mask.cumsum(1)
        x_embed = not_mask.cumsum(2)
        if self.normalize:
            eps = 1e-6
            y_embed = y_embed / (y_embed[:, -1:, :] + eps) * self.scale
            x_embed = x_embed / (x_embed[:, :, -1:] + eps) * self.scale
        dim_t = torch.arange(self.num_pos_feats, dtype=torch.int64, device=x.device).type_as(x)
        dim_t = self.temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / self.num_pos_feats)
        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos = torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)
        return pos
class PredictionBlock(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, activation: nn.Module) -> None:
        super().__init__()
        self.layers = [nn.Linear(in_dim, out_dim), activation]
        for i, layer in enumerate(self.layers): self.add_module(str(i), layer)
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class MaskformerMLPPredictionHead(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int = 3):
        super().__init__()
        in_dims = [input_dim] + [hidden_dim] * (num_layers - 1)
        out_dims = [hidden_dim] * (num_layers - 1) + [output_dim]
        self.layers = []
        for i, (in_dim, out_dim) in enumerate(zip(in_dims, out_dims)):
            activation = nn.ReLU() if i < num_layers - 1 else nn.Identity()
            layer = PredictionBlock(in_dim, out_dim, activation=activation)
            self.layers.append(layer)
            self.add_module(str(i), layer)
    def forward(self, input: Tensor) -> Tensor:
        hidden_state = input
        for layer in self.layers: hidden_state = layer(hidden_state)
        return hidden_state
class MaskFormerPixelLevelModule(nn.Module):
    def __init__(self, config: MaskFormerConfig):
        super().__init__()
        if getattr(config, "backbone_config") is not None and config.backbone_config.model_type == "swin":
            backbone_config = config.backbone_config
            backbone_config = MaskFormerSwinConfig.from_dict(backbone_config.to_dict())
            backbone_config.out_features = ["stage1", "stage2", "stage3", "stage4"]
            config.backbone_config = backbone_config
        self.encoder = load_backbone(config)
        feature_channels = self.encoder.channels
        self.decoder = MaskFormerPixelDecoder(in_features=feature_channels[-1], feature_size=config.fpn_feature_size, mask_feature_size=config.mask_feature_size,
        lateral_widths=feature_channels[:-1])
    def forward(self, pixel_values: Tensor, output_hidden_states: bool = False, return_dict: bool = True) -> MaskFormerPixelLevelModuleOutput:
        features = self.encoder(pixel_values).feature_maps
        decoder_output = self.decoder(features, output_hidden_states, return_dict=return_dict)
        if not return_dict:
            last_hidden_state = decoder_output[0]
            outputs = (features[-1], last_hidden_state)
            if output_hidden_states:
                hidden_states = decoder_output[1]
                outputs = outputs + (tuple(features),) + (hidden_states,)
            return outputs
        return MaskFormerPixelLevelModuleOutput(encoder_last_hidden_state=features[-1], decoder_last_hidden_state=decoder_output.last_hidden_state, encoder_hidden_states=tuple(features) if output_hidden_states else (),
        decoder_hidden_states=decoder_output.hidden_states if output_hidden_states else ())
class MaskFormerTransformerModule(nn.Module):
    def __init__(self, in_features: int, config: MaskFormerConfig):
        super().__init__()
        hidden_size = config.decoder_config.hidden_size
        should_project = in_features != hidden_size
        self.position_embedder = MaskFormerSinePositionEmbedding(num_pos_feats=hidden_size // 2, normalize=True)
        self.queries_embedder = nn.Embedding(config.decoder_config.num_queries, hidden_size)
        self.input_projection = nn.Conv2d(in_features, hidden_size, kernel_size=1) if should_project else None
        self.decoder = DetrDecoder(config=config.decoder_config)
    def forward(self, image_features: Tensor, output_hidden_states: bool = False, output_attentions: bool = False, return_dict: Optional[bool] = None) -> DetrDecoderOutput:
        if self.input_projection is not None: image_features = self.input_projection(image_features)
        object_queries = self.position_embedder(image_features)
        batch_size = image_features.shape[0]
        queries_embeddings = self.queries_embedder.weight.unsqueeze(0).repeat(batch_size, 1, 1)
        inputs_embeds = torch.zeros_like(queries_embeddings, requires_grad=True)
        batch_size, num_channels, height, width = image_features.shape
        image_features = image_features.view(batch_size, num_channels, height * width).permute(0, 2, 1)
        object_queries = object_queries.view(batch_size, num_channels, height * width).permute(0, 2, 1)
        decoder_output: DetrDecoderOutput = self.decoder(inputs_embeds=inputs_embeds, attention_mask=None, encoder_hidden_states=image_features, encoder_attention_mask=None,
        object_queries=object_queries, query_position_embeddings=queries_embeddings, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        return decoder_output
MASKFORMER_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) sub-class. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`MaskFormerConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
MASKFORMER_INPUTS_DOCSTRING = r"""
    Args:
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`AutoImageProcessor`]. See
            [`MaskFormerImageProcessor.__call__`] for details.
        pixel_mask (`torch.LongTensor` of shape `(batch_size, height, width)`, *optional*):
            Mask to avoid performing attention on padding pixel values. Mask values selected in `[0, 1]`:
            - 1 for pixels that are real (i.e. *not masked*),
            - 0 for pixels that are padding (i.e. *masked*).
            [What are attention masks?](../glossary#attention-mask)
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of Detr's decoder attention layers.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~MaskFormerModelOutput`] instead of a plain tuple.
"""
class MaskFormerPreTrainedModel(PreTrainedModel):
    config_class = MaskFormerConfig
    base_model_prefix = "model"
    main_input_name = "pixel_values"
    def _init_weights(self, module: nn.Module):
        xavier_std = self.config.init_xavier_std
        std = self.config.init_std
        if isinstance(module, MaskFormerTransformerModule):
            if module.input_projection is not None:
                nn.init.xavier_uniform_(module.input_projection.weight, gain=xavier_std)
                nn.init.constant_(module.input_projection.bias, 0)
        elif isinstance(module, MaskFormerFPNModel): nn.init.xavier_uniform_(module.stem.get_submodule("0").weight, gain=xavier_std)
        elif isinstance(module, MaskFormerFPNLayer): nn.init.xavier_uniform_(module.proj[0].weight, gain=xavier_std)
        elif isinstance(module, MaskFormerFPNConvLayer): nn.init.xavier_uniform_(module.get_submodule("0").weight, gain=xavier_std)
        elif isinstance(module, MaskformerMLPPredictionHead):
            for submodule in module.modules():
                if isinstance(submodule, nn.Linear):
                    nn.init.xavier_uniform_(submodule.weight, gain=xavier_std)
                    nn.init.constant_(submodule.bias, 0)
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
@add_start_docstrings("The bare MaskFormer Model outputting raw hidden-states without any specific head on top.", MASKFORMER_START_DOCSTRING)
class MaskFormerModel(MaskFormerPreTrainedModel):
    def __init__(self, config: MaskFormerConfig):
        super().__init__(config)
        self.pixel_level_module = MaskFormerPixelLevelModule(config)
        self.transformer_module = MaskFormerTransformerModule(in_features=self.pixel_level_module.encoder.channels[-1], config=config)
        self.post_init()
    @add_start_docstrings_to_model_forward(MASKFORMER_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Tensor, pixel_mask: Optional[Tensor] = None, output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None,
    return_dict: Optional[bool] = None) -> MaskFormerModelOutput:
        if pixel_values is None: raise ValueError("You have to specify pixel_values")
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, _, height, width = pixel_values.shape
        if pixel_mask is None: pixel_mask = torch.ones((batch_size, height, width), device=pixel_values.device)
        pixel_level_module_output = self.pixel_level_module(pixel_values, output_hidden_states, return_dict=return_dict)
        image_features = pixel_level_module_output[0]
        pixel_embeddings = pixel_level_module_output[1]
        transformer_module_output = self.transformer_module(image_features, output_hidden_states, output_attentions)
        queries = transformer_module_output.last_hidden_state
        encoder_hidden_states = None
        pixel_decoder_hidden_states = None
        transformer_decoder_hidden_states = None
        hidden_states = None
        if output_hidden_states:
            encoder_hidden_states = pixel_level_module_output[2]
            pixel_decoder_hidden_states = pixel_level_module_output[3]
            transformer_decoder_hidden_states = transformer_module_output[1]
            hidden_states = encoder_hidden_states + pixel_decoder_hidden_states + transformer_decoder_hidden_states
        output = MaskFormerModelOutput(encoder_last_hidden_state=image_features, pixel_decoder_last_hidden_state=pixel_embeddings, transformer_decoder_last_hidden_state=queries,
        encoder_hidden_states=encoder_hidden_states, pixel_decoder_hidden_states=pixel_decoder_hidden_states, transformer_decoder_hidden_states=transformer_decoder_hidden_states,
        hidden_states=hidden_states, attentions=transformer_module_output.attentions)
        if not return_dict: output = tuple(v for v in output.values())
        return output
class MaskFormerForInstanceSegmentation(MaskFormerPreTrainedModel):
    def __init__(self, config: MaskFormerConfig):
        super().__init__(config)
        self.model = MaskFormerModel(config)
        hidden_size = config.decoder_config.hidden_size
        self.class_predictor = nn.Linear(hidden_size, config.num_labels + 1)
        self.mask_embedder = MaskformerMLPPredictionHead(hidden_size, hidden_size, config.mask_feature_size)
        self.matcher = MaskFormerHungarianMatcher(cost_class=1.0, cost_dice=config.dice_weight, cost_mask=config.mask_weight)
        self.weight_dict: Dict[str, float] = {"loss_cross_entropy": config.cross_entropy_weight, "loss_mask": config.mask_weight, "loss_dice": config.dice_weight}
        self.criterion = MaskFormerLoss(config.num_labels, matcher=self.matcher, weight_dict=self.weight_dict, eos_coef=config.no_object_weight)
        self.post_init()
    def get_loss_dict(self, masks_queries_logits: Tensor, class_queries_logits: Tensor, mask_labels: Tensor, class_labels: Tensor, auxiliary_logits: Dict[str, Tensor]) -> Dict[str, Tensor]:
        loss_dict: Dict[str, Tensor] = self.criterion(masks_queries_logits, class_queries_logits, mask_labels, class_labels, auxiliary_logits)
        for key, weight in self.weight_dict.items():
            for loss_key, loss in loss_dict.items():
                if key in loss_key: loss *= weight
        return loss_dict
    def get_loss(self, loss_dict: Dict[str, Tensor]) -> Tensor: return sum(loss_dict.values())
    def get_logits(self, outputs: MaskFormerModelOutput) -> Tuple[Tensor, Tensor, Dict[str, Tensor]]:
        pixel_embeddings = outputs.pixel_decoder_last_hidden_state
        auxiliary_logits: List[str, Tensor] = []
        is_tracing = torch.jit.is_tracing() or isinstance(outputs, torch.fx.Proxy) or is_torchdynamo_compiling()
        if self.config.use_auxiliary_loss:
            stacked_transformer_decoder_outputs = torch.stack(outputs.transformer_decoder_hidden_states)
            classes = self.class_predictor(stacked_transformer_decoder_outputs)
            class_queries_logits = classes[-1]
            mask_embeddings = self.mask_embedder(stacked_transformer_decoder_outputs)
            if is_tracing and not is_torch_greater_or_equal_than_2_1:
                num_embeddings, batch_size, num_queries, num_channels = mask_embeddings.shape
                _, _, height, width = pixel_embeddings.shape
                binaries_masks = torch.zeros((num_embeddings, batch_size, num_queries, height, width), device=mask_embeddings.device)
                for c in range(num_channels): binaries_masks += mask_embeddings[..., c][..., None, None] * pixel_embeddings[None, :, None, c]
            else: binaries_masks = torch.einsum("lbqc, bchw -> lbqhw", mask_embeddings, pixel_embeddings)
            masks_queries_logits = binaries_masks[-1]
            for aux_binary_masks, aux_classes in zip(binaries_masks[:-1], classes[:-1]): auxiliary_logits.append({"masks_queries_logits": aux_binary_masks, "class_queries_logits": aux_classes})
        else:
            transformer_decoder_hidden_states = outputs.transformer_decoder_last_hidden_state
            classes = self.class_predictor(transformer_decoder_hidden_states)
            class_queries_logits = classes
            mask_embeddings = self.mask_embedder(transformer_decoder_hidden_states)
            if is_tracing and not is_torch_greater_or_equal_than_2_1:
                batch_size, num_queries, num_channels = mask_embeddings.shape
                _, _, height, width = pixel_embeddings.shape
                masks_queries_logits = torch.zeros((batch_size, num_queries, height, width), device=mask_embeddings.device)
                for c in range(num_channels): masks_queries_logits += mask_embeddings[..., c][..., None, None] * pixel_embeddings[:, None, c]
            else: masks_queries_logits = torch.einsum("bqc, bchw -> bqhw", mask_embeddings, pixel_embeddings)
        return class_queries_logits, masks_queries_logits, auxiliary_logits
    @add_start_docstrings_to_model_forward(MASKFORMER_INPUTS_DOCSTRING)
    def forward(self, pixel_values: Tensor, mask_labels: Optional[List[Tensor]] = None, class_labels: Optional[List[Tensor]] = None, pixel_mask: Optional[Tensor] = None,
    output_auxiliary_logits: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_attentions: Optional[bool] = None, return_dict: Optional[bool] = None) -> MaskFormerForInstanceSegmentationOutput:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        raw_outputs = self.model(pixel_values, pixel_mask, output_hidden_states=output_hidden_states or self.config.use_auxiliary_loss, return_dict=return_dict, output_attentions=output_attentions)
        outputs = MaskFormerModelOutput(encoder_last_hidden_state=raw_outputs[0], pixel_decoder_last_hidden_state=raw_outputs[1], transformer_decoder_last_hidden_state=raw_outputs[2],
        encoder_hidden_states=raw_outputs[3] if output_hidden_states else None, pixel_decoder_hidden_states=raw_outputs[4] if output_hidden_states else None,
        transformer_decoder_hidden_states=raw_outputs[5] if output_hidden_states else None, hidden_states=raw_outputs[6] if output_hidden_states else None,
        attentions=raw_outputs[-1] if output_attentions else None)
        loss, loss_dict, auxiliary_logits = None, None, None
        class_queries_logits, masks_queries_logits, auxiliary_logits = self.get_logits(outputs)
        if mask_labels is not None and class_labels is not None:
            loss_dict: Dict[str, Tensor] = self.get_loss_dict(masks_queries_logits, class_queries_logits, mask_labels, class_labels, auxiliary_logits)
            loss = self.get_loss(loss_dict)
        output_auxiliary_logits = (self.config.output_auxiliary_logits if output_auxiliary_logits is None else output_auxiliary_logits)
        if not output_auxiliary_logits: auxiliary_logits = None
        if not return_dict:
            output = tuple(v for v in (loss, class_queries_logits, masks_queries_logits, auxiliary_logits, *outputs.values()) if v is not None)
            return output
        return MaskFormerForInstanceSegmentationOutput(loss=loss, **outputs, class_queries_logits=class_queries_logits, masks_queries_logits=masks_queries_logits, auxiliary_logits=auxiliary_logits)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
