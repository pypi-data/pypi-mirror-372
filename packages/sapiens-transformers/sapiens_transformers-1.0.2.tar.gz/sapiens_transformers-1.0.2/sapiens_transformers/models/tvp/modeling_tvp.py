"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple
import torch
import torch.utils.checkpoint
from torch import nn
from ...activations import ACT2FN
from ...file_utils import add_start_docstrings, add_start_docstrings_to_model_forward, replace_return_docstrings
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPooling, ModelOutput
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import prune_linear_layer
from ...utils import logging
from ...utils.backbone_utils import load_backbone
from .configuration_tvp import TvpConfig
logger = logging.get_logger(__name__)
@dataclass
class TvpVideoGroundingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
class TvpLoss(nn.Module):
    def __init__(self, losses):
        super().__init__()
        self.loss_map = {"iou": self.loss_iou, "distance": self.loss_distance, "duration": self.loss_duration}
        for loss in losses:
            if loss not in self.loss_map: raise ValueError(f"Loss {loss} not supported")
        self.losses = losses
    def loss_iou(self, start_time, end_time, candidates_start_time, candidates_end_time, duration):
        inter = torch.min(candidates_end_time, end_time) - torch.max(candidates_start_time, start_time)
        union = torch.max(candidates_end_time, end_time) - torch.min(candidates_start_time, start_time)
        iou = 1 - inter.clamp(min=0) / union
        return iou
    def loss_distance(self, start_time, end_time, candidates_start_time, candidates_end_time, duration):
        mid_candidates = torch.div(torch.add(candidates_start_time, candidates_end_time), 2.0)
        mid_groundtruth = torch.div(torch.add(start_time, end_time), 2.0)
        distance_diff = torch.div(torch.max(mid_candidates, mid_groundtruth) - torch.min(mid_candidates, mid_groundtruth), duration).clamp(min=0.2)
        return distance_diff
    def loss_duration(self, start_time, end_time, candidates_start_time, candidates_end_time, duration):
        duration_candidates = torch.sub(candidates_end_time, candidates_start_time)
        duration_groundtruth = torch.sub(end_time, start_time)
        duration_diff = torch.square(torch.div(torch.sub(duration_candidates, duration_groundtruth), duration))
        duration_diff = duration_diff.clamp(min=0.4)
        return duration_diff
    def forward(self, logits, labels):
        duration, start_time, end_time = labels
        candidates = torch.mul(logits, duration)
        candidates_start_time, candidates_end_time = candidates[:, 0].float(), candidates[:, 1].float()
        losses_dict = {}
        for loss in self.losses: losses_dict.update({loss: self.loss_map[loss](start_time, end_time, candidates_start_time, candidates_end_time, duration)})
        return losses_dict
class TvpVisionModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.backbone = load_backbone(config)
        if config.backbone_config is not None: in_channels = config.backbone_config.hidden_sizes[-1]
        elif hasattr(self.backbone, "config") and hasattr(self.backbone.config, "hidden_sizes"): in_channels = self.backbone.config.hidden_sizes[-1]
        elif hasattr(self.backbone, "config") and hasattr(self.backbone.config, "hidden_size"): in_channels = self.backbone.config.hidden_size
        else: raise ValueError("Backbone config not found")
        self.grid_encoder_conv = nn.Conv2d(in_channels, config.hidden_size, kernel_size=3, stride=1, padding=1, groups=1, bias=False)
    def forward(self, pixel_values):
        batch_size, num_frames, num_channels, height, width = pixel_values.shape
        pixel_values = pixel_values.view(batch_size * num_frames, num_channels, height, width)
        grid_feat_outputs = self.backbone(pixel_values)["feature_maps"][0]
        grid = self.grid_encoder_conv(grid_feat_outputs)
        grid = nn.functional.max_pool2d(grid, kernel_size=2, stride=2)
        grid = nn.functional.relu(grid, inplace=True)
        new_channel, new_height, new_width = grid.shape[-3:]
        grid = grid.view(batch_size, num_frames, new_channel, new_height, new_width)
        grid = grid.permute(0, 1, 3, 4, 2)
        return grid
class TvpVisualInputEmbedding(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.row_position_embeddings = nn.Embedding(config.max_grid_row_position_embeddings, config.hidden_size)
        self.col_position_embeddings = nn.Embedding(config.max_grid_col_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(1, config.hidden_size)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.max_grid_row_position_embeddings = config.max_grid_row_position_embeddings
        self.max_grid_col_position_embeddings = config.max_grid_col_position_embeddings
    def interpolate_pos_encoding(self, embedding: torch.Tensor, height: int, width: int) -> torch.Tensor:
        h0 = w0 = 1
        if height > self.max_grid_row_position_embeddings: h0 = height / self.max_grid_row_position_embeddings
        if width > self.max_grid_col_position_embeddings: w0 = width / self.max_grid_col_position_embeddings
        embedding = embedding.permute(0, 3, 1, 2)
        embedding = nn.functional.interpolate(embedding, scale_factor=(h0, w0), mode="bicubic", align_corners=False)
        embedding = embedding.permute(0, 2, 3, 1)
        return embedding
    def add_2d_positional_embeddings(self, grid, interpolate_pos_encoding: bool = False):
        batch_size, height, width, hidden_dim = grid.shape
        row_height = min(self.max_grid_row_position_embeddings, height)
        row_position_ids = torch.arange(row_height, dtype=torch.long, device=grid.device)
        row_position_embeddings = self.row_position_embeddings(row_position_ids)
        row_shape = (1,) * (len(grid.shape) - 3) + (row_height, 1, hidden_dim)
        row_position_embeddings = row_position_embeddings.view(*row_shape)
        row_width = min(self.max_grid_col_position_embeddings, width)
        col_position_ids = torch.arange(row_width, dtype=torch.long, device=grid.device)
        col_position_embeddings = self.col_position_embeddings(col_position_ids)
        col_shape = (batch_size, 1, row_width, hidden_dim)
        col_position_embeddings = col_position_embeddings.view(*col_shape)
        positional_embeddings = row_position_embeddings + col_position_embeddings
        if interpolate_pos_encoding and (height > self.max_grid_row_position_embeddings or width > self.max_grid_col_position_embeddings): grid = grid + self.interpolate_pos_encoding(positional_embeddings, height, width)
        else: grid = grid + positional_embeddings
        return grid
    def forward(self, grid, interpolate_pos_encoding: bool = False):
        batch_size, num_frames, height, width, num_channels = grid.shape
        grid = grid.mean(1)
        grid = self.add_2d_positional_embeddings(grid, interpolate_pos_encoding=interpolate_pos_encoding)
        visual_tokens = grid.view(batch_size, -1, num_channels)
        visual_tokens_shape = visual_tokens.shape[:-1]
        device = visual_tokens.device
        token_type_ids = torch.zeros(visual_tokens_shape, dtype=torch.long, device=device)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        embeddings = visual_tokens + token_type_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
class TvpTextInputEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, input_ids=None, token_type_ids=None, position_ids=None, inputs_embeds=None):
        if input_ids is not None: input_shape = input_ids.size()
        else: input_shape = inputs_embeds.size()[:-1]
        seq_length = input_shape[1]
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if position_ids is None:
            position_ids = torch.arange(seq_length, dtype=torch.long, device=device)
            position_ids = position_ids.unsqueeze(0).expand(input_shape)
        if token_type_ids is None: token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=device)
        if inputs_embeds is None: inputs_embeds = self.word_embeddings(input_ids)
        position_embeddings = self.position_embeddings(position_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        embeddings = inputs_embeds + position_embeddings + token_type_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
class TvpAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"): raise ValueError(f"The hidden size {config.hidden_size} is not a multiple of the number of attention heads {config.num_attention_heads}")
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)
        self.attn_dropout = nn.Dropout(config.attention_probs_dropout_prob)
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.pruned_heads = set()
    def prune_heads(self, heads):
        if len(heads) == 0: return
        mask = torch.ones(self.num_attention_heads, self.attention_head_size)
        heads = set(heads) - self.pruned_heads
        for head in heads:
            head = head - sum(1 if h < head else 0 for h in self.pruned_heads)
            mask[head] = 0
        mask = mask.view(-1).contiguous().eq(1)
        index = torch.arange(len(mask))[mask].long()
        self.query = prune_linear_layer(self.query, index)
        self.key = prune_linear_layer(self.key, index)
        self.value = prune_linear_layer(self.value, index)
        self.dense = prune_linear_layer(self.dense, index, dim=1)
        self.num_attention_heads = self.num_attention_heads - len(heads)
        self.all_head_size = self.attention_head_size * self.num_attention_heads
        self.pruned_heads = self.pruned_heads.union(heads)
    def _reshape(self, tensor: torch.Tensor, sequence_length: int, batch_size: int): return (tensor.view(batch_size, sequence_length, self.num_attention_heads, self.attention_head_size).transpose(1, 2).contiguous())
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions: Optional[bool] = None):
        batch_size, sequence_length = hidden_states.shape[:2]
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(hidden_states)
        mixed_value_layer = self.value(hidden_states)
        query_layer = self._reshape(mixed_query_layer, sequence_length, batch_size)
        key_layer = self._reshape(mixed_key_layer, sequence_length, batch_size)
        value_layer = self._reshape(mixed_value_layer, sequence_length, batch_size)
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None: attention_scores = attention_scores + attention_mask
        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.attn_dropout(attention_probs)
        if head_mask is not None: attention_probs = attention_probs * head_mask
        attn_output = torch.matmul(attention_probs, value_layer)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(batch_size, sequence_length, self.all_head_size)
        attn_output = self.dense(attn_output)
        attn_output = self.dropout(attn_output)
        attn_output = self.layer_norm(attn_output + hidden_states)
        outputs = (attn_output, attention_probs) if output_attentions else (attn_output,)
        return outputs
class TvpIntermediate(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class TvpOutputLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.layer_norm(hidden_states + input_tensor)
        return hidden_states
class TvpEncodeLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.attention = TvpAttention(config)
        self.intermediate = TvpIntermediate(config)
        self.output = TvpOutputLayer(config)
    def forward(self, hidden_states, attention_mask=None, head_mask=None, output_attentions: Optional[bool] = None):
        self_attention_outputs = self.attention(hidden_states, attention_mask, head_mask, output_attentions=output_attentions)
        attention_output = self_attention_outputs[0]
        outputs = self_attention_outputs[1:]
        intermediate_output = self.intermediate(attention_output)
        layer_output = self.output(intermediate_output, attention_output)
        outputs = (layer_output,) + outputs
        return outputs
class TvpEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([TvpEncodeLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states, attention_mask=None, head_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        all_hidden_states = ()
        all_attentions = ()
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states,
            attention_mask, (head_mask[i] if head_mask is not None else None), output_attentions)
            else: layer_outputs = layer_module(hidden_states, attention_mask, head_mask[i], output_attentions)
            hidden_states = layer_outputs[0]
            if output_attentions: all_attentions = all_attentions + (layer_outputs[1],)
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict:
            outputs = (hidden_states,)
            if output_hidden_states: outputs = outputs + (all_hidden_states,)
            if output_attentions: outputs = outputs + (all_attentions,)
            return outputs
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states if output_hidden_states else None, attentions=all_attentions if output_attentions else None)
class TvpPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output
class TvpPreTrainedModel(PreTrainedModel):
    config_class = TvpConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)): module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        if isinstance(module, nn.Linear) and module.bias is not None: module.bias.data.zero_()
        if isinstance(module, nn.Conv2d):
            nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            if module.bias is not None: nn.init.constant_(module.bias, 0)
TVP_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass. Use it
    as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`TvpConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
TVP_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Indices can be obtained using [`AutoTokenizer`]. See
            [`PreTrainedTokenizer.encode`] and [`PreTrainedTokenizer.__call__`] for details. [What are input
            IDs?](../glossary#input-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_frames, num_channels, height, width)`):
            Pixel values. Pixel values can be obtained using [`TvpImageProcessor`]. See [`TvpImageProcessor.__call__`]
            for details.
        attention_mask (`torch.FloatTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        head_mask (`torch.FloatTensor` of shape `(num_heads,)` or `(num_layers, num_heads)`, *optional*):
            Mask to nullify selected heads of the self-attention modules. Mask values selected in `[0, 1]`:
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        interpolate_pos_encoding (`bool`, *optional*, defaults to `False`):
            Whether to interpolate the pre-trained image pad prompter encodings and positional encodings.
"""
class TvpFrameDownPadPrompter(nn.Module):
    def __init__(self, config):
        if config.visual_prompter_apply not in ("add", "replace", "remove"): raise ValueError("`visual_prompter_apply` must be in (add, replace, remove)")
        super().__init__()
        self.visual_prompt_size = config.visual_prompt_size
        self.frame_num = config.frame_num
        self.max_img_size = config.max_img_size
        self.visual_prompter_apply = config.visual_prompter_apply
        self.pad_down = nn.Parameter(torch.randn([1, config.frame_num, 3, config.visual_prompt_size, config.max_img_size]))
    def forward(self, pixel_values):
        if self.visual_prompter_apply != "add":
            visual_prompt_mask = torch.ones([self.max_img_size, self.max_img_size], dtype=pixel_values.dtype, device=pixel_values.device)
            visual_prompt_mask[self.max_img_size - self.visual_prompt_size : self.max_img_size, :] = 0.0
            pixel_values *= visual_prompt_mask
        if self.visual_prompter_apply != "remove":
            prompt = torch.zeros([pixel_values.shape[0], pixel_values.shape[1], 3, self.max_img_size, self.max_img_size], device=pixel_values.device)
            start_point = self.max_img_size - self.visual_prompt_size
            prompt[:, :, :, start_point : self.max_img_size, :] = self.pad_down
            pixel_values += prompt.to(pixel_values.dtype)
        return pixel_values
class TvpFramePadPrompter(nn.Module):
    def __init__(self, config):
        if config.visual_prompter_apply not in ("add", "replace", "remove"): raise ValueError("`visual_prompter_apply` must be in (add, replace, remove)")
        super().__init__()
        self.num_frames = config.num_frames
        self.max_img_size = config.max_img_size
        self.visual_prompter_apply = config.visual_prompter_apply
        self.base_size = config.max_img_size - config.visual_prompt_size * 2
        self.pad_up = nn.Parameter(torch.randn([1, config.num_frames, 3, config.visual_prompt_size, config.max_img_size]))
        self.pad_down = nn.Parameter(torch.randn([1, config.num_frames, 3, config.visual_prompt_size, config.max_img_size]))
        self.pad_left = nn.Parameter(torch.randn([1, config.num_frames, 3, config.max_img_size - config.visual_prompt_size * 2, config.visual_prompt_size]))
        self.pad_right = nn.Parameter(torch.randn([1, config.num_frames, 3, config.max_img_size - config.visual_prompt_size * 2, config.visual_prompt_size]))
    def interpolate_pad_encoding(self, prompt: torch.Tensor, height: int, width: int) -> torch.Tensor:
        h0, w0 = height / self.max_img_size, width / self.max_img_size
        batch, num_frames, channels, prompt_height, prompt_width = prompt.shape
        prompt = prompt.reshape(batch * num_frames, channels, prompt_height, prompt_width)
        prompt = nn.functional.interpolate(prompt, scale_factor=(h0, w0), mode="bicubic", align_corners=False)
        prompt = prompt.reshape(batch, num_frames, channels, height, width)
        return prompt
    def forward(self, pixel_values, interpolate_pad_encoding: bool = False):
        height, width = ((pixel_values.shape[-2], pixel_values.shape[-1]) if interpolate_pad_encoding else (self.max_img_size, self.max_img_size))
        if self.visual_prompter_apply not in ("add", "remove", "replace"): raise ValueError(f"Invalid visual_prompter_apply value {self.visual_prompter_apply}")
        if self.visual_prompter_apply in ("replace", "remove"):
            visual_prompt_mask = torch.ones([height, width], dtype=pixel_values.dtype, device=pixel_values.device)
            pixel_values *= visual_prompt_mask
        if self.visual_prompter_apply in ("replace", "add"):
            base = torch.zeros(1, self.num_frames, 3, self.base_size, self.base_size, device=pixel_values.device)
            prompt = torch.cat([self.pad_left, base, self.pad_right], dim=4)
            prompt = torch.cat([self.pad_up, prompt, self.pad_down], dim=3)
            prompt = torch.cat(pixel_values.size(0) * [prompt])
            if interpolate_pad_encoding: prompt = self.interpolate_pad_encoding(prompt, height, width)
            pixel_values = pixel_values + prompt.to(pixel_values.dtype)
        return pixel_values
TVP_PROMPTER_CLASSES_MAPPING = {"framedownpad": TvpFrameDownPadPrompter, "framepad": TvpFramePadPrompter}
@add_start_docstrings("The bare Tvp Model transformer outputting BaseModelOutputWithPooling object without any specific head on" " top.", TVP_START_DOCSTRING)
class TvpModel(TvpPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.vision_model = TvpVisionModel(config)
        self.embeddings = TvpTextInputEmbeddings(config)
        self.visual_embeddings = TvpVisualInputEmbedding(config)
        self.encoder = TvpEncoder(config)
        self.pooler = TvpPooler(config)
        self.text_prompt = nn.Parameter(torch.randn([1, 10, config.hidden_size]))
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        if config.visual_prompter_type not in TVP_PROMPTER_CLASSES_MAPPING: raise ValueError("`visual_prompter_type` must be in (framedownpad, framepad)")
        self.visual_prompter = TVP_PROMPTER_CLASSES_MAPPING[config.visual_prompter_type](config)
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.word_embeddings
    def set_input_embeddings(self, value): self.embeddings.word_embeddings = value
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items(): self.encoder.layer[layer].attention.prune_heads(heads)
    @add_start_docstrings_to_model_forward(TVP_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None,
    head_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None,
    interpolate_pos_encoding: bool = False):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        pixel_values = self.vision_model(self.visual_prompter(pixel_values, interpolate_pad_encoding=interpolate_pos_encoding))
        text_embedding_output = self.embeddings(input_ids=input_ids)
        visual_embedding_output = self.visual_embeddings(pixel_values, interpolate_pos_encoding=interpolate_pos_encoding)
        if attention_mask is not None:
            visual_attention_mask = attention_mask.new_ones(visual_embedding_output.shape[:2])
            pt_mask = torch.ones(attention_mask.shape[0], 10).to(device=attention_mask.device, dtype=attention_mask.dtype)
            attention_mask = torch.cat([pt_mask, attention_mask, visual_attention_mask], dim=-1)
            attention_mask = self.get_extended_attention_mask(attention_mask, input_ids.size()).to(input_ids.device)
        text_prompt = self.text_prompt.expand(text_embedding_output.shape[0], -1, -1)
        embedding_output = torch.cat([text_prompt, text_embedding_output, visual_embedding_output], dim=1)
        encoder_outputs = self.encoder(embedding_output, attention_mask=attention_mask, head_mask=self.get_head_mask(head_mask, self.config.num_hidden_layers),
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        last_hidden_state = encoder_outputs.last_hidden_state if return_dict else encoder_outputs[0]
        pooled_output = self.pooler(last_hidden_state)
        last_hidden_state = self.dropout(last_hidden_state)
        pooled_output = self.dropout(pooled_output)
        if not return_dict: return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=last_hidden_state, pooler_output=pooled_output, hidden_states=encoder_outputs.hidden_states, attentions=encoder_outputs.attentions)
class TvpVideoGroundingHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layer_0 = nn.Linear(config.hidden_size, config.hidden_size * 2)
        self.layer_1 = nn.Linear(config.hidden_size * 2, 2)
        self.activation_0 = nn.ReLU()
        self.activation_1 = nn.Sigmoid()
    def forward(self, pooler_output):
        logits = self.activation_0(self.layer_0(pooler_output))
        logits = self.activation_1(self.layer_1(logits))
        return logits
@add_start_docstrings("Tvp Model with a video grounding head on top computing IoU, distance, and duration loss.", TVP_START_DOCSTRING)
class TvpForVideoGrounding(TvpPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.model = TvpModel(config)
        self.video_grounding_head = TvpVideoGroundingHead(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(TVP_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, pixel_values: Optional[torch.FloatTensor] = None, attention_mask: Optional[torch.LongTensor] = None,
    labels: Tuple[torch.Tensor] = None, head_mask: Optional[torch.FloatTensor] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, interpolate_pos_encoding: bool = False):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        outputs = self.model(input_ids, pixel_values, attention_mask, head_mask=head_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states,
        return_dict=return_dict, interpolate_pos_encoding=interpolate_pos_encoding)
        pooler_output = outputs[1]
        logits = self.video_grounding_head(pooler_output)
        loss = None
        if labels is not None:
            criterion = TvpLoss(["iou", "distance", "duration"])
            criterion.to(self.device)
            loss_dict = criterion(logits, labels)
            loss = (loss_dict["iou"] + self.config.distance_loss_weight * loss_dict["distance"] + self.config.duration_loss_weight * loss_dict["duration"])
        if not return_dict:
            outputs = (logits,) + outputs[2:]
            if loss is not None: outputs = (loss,) + outputs
            return outputs
        return TvpVideoGroundingOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states, attentions=outputs.attentions)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
