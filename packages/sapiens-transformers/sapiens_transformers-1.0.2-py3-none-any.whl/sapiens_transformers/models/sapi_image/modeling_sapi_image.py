"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch.nn import Module, Linear, Conv2d, Embedding, Parameter, CrossEntropyLoss
from .configuration_sapi_image import SAPIImageConfig
from torch import (Tensor as t_Tensor, FloatTensor as t_FloatTensor, randn as t_randn, no_grad as t_no_grad, any as t_any, sum as t_sum, tensor as t_tensor, where as t_where,
cumsum as t_cumsum, zeros as t_zeros, full as t_full, full_like as t_full_like, long as t_long, bool as t_bool, arange as t_arange, cat as t_cat, LongTensor as t_LongTensor,
split as t_split, ones as t_ones)
_CONFIG_FOR_DOC = "SAPIImageConfig"
class SAPIImageMultiModalProjector(Module):
    def __init__(self, config: SAPIImageConfig):
        super().__init__()
        from ...activations import ACT2FN
        self.linear_1, self.linear_2, self.act = Linear(config.vision_config.hidden_size, config.text_config.hidden_size, bias=True), Linear(config.text_config.hidden_size, config.text_config.hidden_size, bias=True), ACT2FN[config.projector_hidden_act]
    def forward(self, image_features): return self.linear_2(self.act(self.linear_1(image_features)))
SAPI_IMAGE_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        pixel_values (`torch.FloatTensor` of shape `(batch_size, num_channels, image_size, image_size)):
            The tensors corresponding to the input images. Pixel values can be obtained using
            [`AutoImageProcessor`]. See [`SAPIImageImageProcessor.__call__`] for details. Uses [`SAPIImageImageProcessor`] for processing images.
        image_sizes (`torch.LongTensor` of shape `(batch_size, 2)`, *optional*):
            The sizes of the images in the batch, being (height, width) for each image.
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            If `past_key_values` is used, optionally only the last `decoder_input_ids` have to be input (see
            `past_key_values`).
            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.
            - 1 indicates the head is *not masked*,
            - 0 indicates the head is *masked*.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`. [What are position IDs?](../glossary#position-ids)
        past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
            Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
            `(batch_size, num_heads, sequence_length, embed_size_per_head)` and 2 additional tensors of shape
            `(batch_size, num_heads, encoder_sequence_length, embed_size_per_head)`.
            Contains pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used (see `past_key_values` input) to speed up sequential decoding.
            If `past_key_values` are used, the user can optionally input only the last `decoder_input_ids` (those that
            don't have their past key value states given to this model) of shape `(batch_size, 1)` instead of all
            `decoder_input_ids` of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        vision_feature_layer (`int`, *optional*, defaults to -2):
            The index of the layer to select the vision feature.
        vision_feature_select_strategy (`str`, *optional*, defaults to `"default"`):
            The feature selection strategy used to select the vision feature from the vision backbone.
            Can be one of `"default"` or `"full"`. If `"default"`, the CLS token is removed from the vision features.
            If `"full"`, the full vision features are used.
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        cache_position (`torch.LongTensor` of shape `(sequence_length)`, *optional*):
            Indices depicting the position of the input sequence tokens in the sequence. Contrarily to `position_ids`,
            this tensor is not affected by padding. It is used to update the cache in the correct position and to infer
            the complete sequence length.
"""
SAPI_IMAGE_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`SAPIImageConfig`] or [`SAPIImageVisionConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
from numpy import ndarray as n_ndarray
from ...image_processing_utils import select_best_resolution
def get_anyres_image_grid_shape(image_size, grid_pinpoints, patch_size):
    if not isinstance(grid_pinpoints, list): raise TypeError("grid_pinpoints should be a list of tuples or lists")
    if not isinstance(image_size, (list, tuple)):
        if not isinstance(image_size, (t_Tensor, n_ndarray)): raise TypeError(f"image_size invalid type: {type(image_size)} not valid, should be either list, tuple, np.ndarray or tensor")
        image_size = image_size.tolist()
    height, width = select_best_resolution(image_size, grid_pinpoints)
    return height // patch_size, width // patch_size
def unpad_image(tensor, original_size):
    if not isinstance(original_size, (list, tuple)):
        if not isinstance(original_size, (t_Tensor, n_ndarray)): raise TypeError(f"image_size invalid type: {type(original_size)} not valid, should be either list, tuple, np.ndarray or tensor")
        original_size = original_size.tolist()
    original_height, original_width = original_size
    current_height, current_width = tensor.shape[1:]
    original_aspect_ratio, current_aspect_ratio = original_width / original_height, current_width / current_height
    if original_aspect_ratio > current_aspect_ratio:
        padding = (current_height - int(original_height * (current_width / original_width))) // 2
        unpadded_tensor = tensor[:, padding : current_height - padding, :]
    else:
        padding = (current_width - int(original_width * (current_height / original_height))) // 2
        unpadded_tensor = tensor[:, :, padding : current_width - padding]
    return unpadded_tensor
def image_size_to_num_patches(image_size, grid_pinpoints, patch_size: int):
    if not isinstance(grid_pinpoints, list): raise TypeError("grid_pinpoints should be a list of tuples or lists")
    if not isinstance(image_size, (list, tuple)):
        if not isinstance(image_size, (t_Tensor, n_ndarray)): raise TypeError(f"image_size invalid type {type(image_size)} with value {image_size}")
        image_size = image_size.tolist()
    best_resolution, num_patches = select_best_resolution(image_size, grid_pinpoints), 0
    height, width = best_resolution
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size): num_patches += 1
    num_patches += 1
    return num_patches
from ...utils import (add_start_docstrings, add_start_docstrings_to_model_forward)
from ...modeling_utils import PreTrainedModel
@add_start_docstrings("The bare Entity Model outputting raw hidden-states without any specific head on top.", SAPI_IMAGE_START_DOCSTRING)
class SAPIImagePreTrainedModel(PreTrainedModel):
    config_class, base_model_prefix, supports_gradient_checkpointing = SAPIImageConfig, "model", True
    _no_split_modules, _skip_keys_device_placement, _supports_flash_attn_2, _supports_cache_class = ["SAPIImageVisionAttention"], "past_key_values", True, True
    def _init_weights(self, module):
        std = (self.config.initializer_range if hasattr(self.config, "initializer_range") else self.config.text_config.initializer_range)
        if hasattr(module, "class_embedding"): module.class_embedding.data.normal_(mean=0.0, std=std)
        if isinstance(module, (Linear, Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
    @property
    def _supports_sdpa(self): return self.language_model._supports_sdpa
from ...modeling_outputs import ModelOutput
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union
@dataclass
class SAPIImageCausalLMOutputWithPast(ModelOutput):
    """Args:"""
    loss: Optional[t_FloatTensor] = None
    logits: t_FloatTensor = None
    past_key_values: Optional[List[t_FloatTensor]] = None
    hidden_states: Optional[Tuple[t_FloatTensor]] = None
    attentions: Optional[Tuple[t_FloatTensor]] = None
    image_hidden_states: Optional[t_FloatTensor] = None
from ...generation import GenerationMixin
from ..auto import AutoModel, AutoModelForCausalLM
@add_start_docstrings("The SAPI-Image model which consists of a vision backbone and a language model.", SAPI_IMAGE_START_DOCSTRING)
class SAPIImageForConditionalGeneration(SAPIImagePreTrainedModel, GenerationMixin):
    def __init__(self, config: SAPIImageConfig):
        super().__init__(config)
        from math import sqrt
        self.vision_tower, self.multi_modal_projector = AutoModel.from_config(config.vision_config), SAPIImageMultiModalProjector(config)
        self.image_newline = Parameter(t_randn(config.text_config.hidden_size, dtype=self.dtype) * (1 / sqrt(config.text_config.hidden_size)))
        self.vocab_size, self.language_model = config.text_config.vocab_size, AutoModelForCausalLM.from_config(config.text_config, attn_implementation=config._attn_implementation)
        self.pad_token_id, self._padding_side = self.config.pad_token_id if self.config.pad_token_id is not None else -1, "left"
        self.post_init()
    @property
    def padding_side(self): return self._padding_side
    @padding_side.setter
    def padding_side(self, padding_side: str):
        if padding_side not in ["left", "right"]: raise ValueError(f"{padding_side} is not `left` or `right`.")
        self._padding_side = padding_side
    def get_input_embeddings(self): return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value): self.language_model.set_input_embeddings(value)
    def get_output_embeddings(self): return self.language_model.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): self.language_model.set_output_embeddings(new_embeddings)
    def set_decoder(self, decoder): self.language_model.set_decoder(decoder)
    def get_decoder(self): return self.language_model.get_decoder()
    def tie_weights(self): return self.language_model.tie_weights()
    def resize_token_embeddings(self, new_num_tokens: Optional[int] = None, pad_to_multiple_of=None) -> Embedding:
        model_embeds = self.language_model.resize_token_embeddings(new_num_tokens, pad_to_multiple_of)
        self.config.text_config.vocab_size, self.vocab_size = model_embeds.num_embeddings, model_embeds.num_embeddings
        return model_embeds
    def _merge_input_ids_with_image_features(self, image_features, feature_lens, inputs_embeds, input_ids, attention_mask, position_ids=None, labels=None, image_token_index=None, ignore_index=-100):
        image_token_index, ignore_index = image_token_index if image_token_index is not None else self.config.image_token_index, ignore_index if ignore_index is not None else self.config.ignore_index
        with t_no_grad():
            num_images = feature_lens.size(0)
            num_image_features, embed_dim = image_features.shape
            if feature_lens.sum() != num_image_features: raise ValueError(f"{feature_lens=} / {feature_lens.sum()} != {image_features.shape=}")
            batch_size, _left_padding, _right_padding, left_padding = input_ids.shape[0], t_any(attention_mask[:, 0] == 0), t_any(attention_mask[:, -1] == 0), self.padding_side == "left"
            if batch_size > 1:
                if _left_padding and _right_padding: raise ValueError(f"both side of attention_mask has zero, invalid. {attention_mask}")
                elif _right_padding and left_padding: left_padding = False
                elif _left_padding and not left_padding: left_padding = True
            special_image_token_mask = input_ids == image_token_index
            num_special_image_tokens = t_sum(special_image_token_mask, dim=-1)
            total_num_special_image_tokens = t_sum(special_image_token_mask)
            if total_num_special_image_tokens != num_images: raise ValueError(f"Number of image tokens in input_ids ({total_num_special_image_tokens}) different from num_images ({num_images}).")
            feature_lens = feature_lens.to(input_ids.device)
            max_embed_dim = ((attention_mask == 1).long().sum(-1) - num_special_image_tokens + t_tensor([x.sum() for x in feature_lens.split(num_special_image_tokens.tolist(), dim=0)], device=input_ids.device)).max()
            batch_indices, non_image_indices = t_where((input_ids != image_token_index) & (attention_mask == 1))
            special_image_token_mask = special_image_token_mask.long()
            special_image_token_mask[special_image_token_mask == 1] = feature_lens - 1
            new_token_positions = t_cumsum((special_image_token_mask + 1), -1) - 1
            if left_padding: new_token_positions += max_embed_dim - 1 - new_token_positions[:, -1:]
            text_to_overwrite = new_token_positions[batch_indices, non_image_indices]
        final_embedding, final_attention_mask = t_zeros(batch_size, max_embed_dim, embed_dim, dtype=inputs_embeds.dtype, device=inputs_embeds.device), t_zeros(batch_size, max_embed_dim, dtype=attention_mask.dtype, device=inputs_embeds.device)
        final_input_ids, target_device = t_full((batch_size, max_embed_dim), self.pad_token_id, dtype=input_ids.dtype, device=inputs_embeds.device), inputs_embeds.device
        batch_indices, non_image_indices, text_to_overwrite = (batch_indices.to(target_device), non_image_indices.to(target_device), text_to_overwrite.to(target_device))
        attention_mask, input_ids = attention_mask.to(target_device), input_ids.to(target_device)
        final_embedding[batch_indices, text_to_overwrite], final_attention_mask[batch_indices, text_to_overwrite] = inputs_embeds[batch_indices, non_image_indices], attention_mask[batch_indices, non_image_indices]
        final_input_ids[batch_indices, text_to_overwrite], final_labels = input_ids[batch_indices, non_image_indices], None
        if labels is not None:
            final_labels = t_full_like(final_attention_mask, ignore_index).to(t_long)
            final_labels[batch_indices, text_to_overwrite] = labels.to(target_device)[batch_indices, non_image_indices]
        with t_no_grad():
            image_to_overwrite = t_full((batch_size, max_embed_dim), True, dtype=t_bool, device=inputs_embeds.device)
            image_to_overwrite[batch_indices, text_to_overwrite] = False
            embed_indices, embed_seq_lens = t_arange(max_embed_dim).unsqueeze(0).to(target_device).expand(batch_size, max_embed_dim), embed_sequence_lengths[:, None].to(target_device)
            if left_padding: val = (max_embed_dim.to(target_device) - embed_indices) <= embed_seq_lens
            else: val = embed_indices < embed_seq_lens
            image_to_overwrite &= val
            if image_to_overwrite.sum() != num_image_features: raise ValueError(f"{image_to_overwrite.sum()=} != {num_image_features=} The input provided to the model are wrong. The number of image tokens is {t_sum(special_image_token_mask)} while the number of image given to the model is {num_images}. This prevents correct indexing and breaks batch generation.")
        final_embedding[image_to_overwrite] = image_features.contiguous().reshape(-1, embed_dim).to(target_device)
        final_attention_mask |= image_to_overwrite
        return final_embedding, final_attention_mask, (final_attention_mask.cumsum(-1) - 1).masked_fill_((final_attention_mask == 0), 1), final_labels, final_input_ids
    def pack_image_features(self, image_features, image_sizes, vision_feature_select_strategy, image_newline=None):
        new_image_features, feature_lens = [], []
        for image_idx, image_feature in enumerate(image_features):
            if image_feature.shape[0] > 1:
                base_image_feature = image_feature[0]
                image_feature = image_feature[1:]
                height = width = self.config.vision_config.image_size // self.config.vision_config.patch_size
                if vision_feature_select_strategy == "default": expected_num_patches = height * width
                elif vision_feature_select_strategy == "full": expected_num_patches = height * width + 1
                if expected_num_patches != base_image_feature.shape[0]: raise ValueError("The number of patches is not consistent with the image size.")
                num_patch_height, num_patch_width = get_anyres_image_grid_shape(image_sizes[image_idx], self.config.image_grid_pinpoints, self.config.vision_config.image_size)
                image_feature = unpad_image(image_feature.view(num_patch_height, num_patch_width, height, width, -1).permute(4, 0, 2, 1, 3).contiguous().flatten(1, 2).flatten(2, 3), image_sizes[image_idx])
                if image_newline is not None: image_feature = t_cat((image_feature, image_newline[:, None, None].expand(*image_feature.shape[:-1], 1).to(image_feature.dtype),), dim=-1)
                image_feature = t_cat((base_image_feature, image_feature.flatten(1, 2).transpose(0, 1)), dim=0)
            else:
                image_feature = image_feature[0]
                if image_newline is not None: image_feature = t_cat((image_feature, image_newline[None].to(image_feature)), dim=0)
            new_image_features.append(image_feature)
            feature_lens.append(image_feature.size(0))
        image_features = t_cat(new_image_features, dim=0)
        return image_features, t_tensor(feature_lens, dtype=t_long, device=image_features.device)
    @add_start_docstrings_to_model_forward(SAPI_IMAGE_INPUTS_DOCSTRING)
    def forward(self, input_ids: t_LongTensor = None, pixel_values: t_FloatTensor = None, image_sizes: Optional[t_LongTensor] = None, attention_mask: Optional[t_Tensor] = None,
    position_ids: Optional[t_LongTensor] = None, past_key_values: Optional[List[t_FloatTensor]] = None, inputs_embeds: Optional[t_FloatTensor] = None,
    vision_feature_layer: Optional[int] = None, vision_feature_select_strategy: Optional[str] = None, labels: Optional[t_LongTensor] = None, use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, cache_position: Optional[t_LongTensor] = None,
    num_logits_to_keep: int = 0) -> Union[Tuple, SAPIImageCausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict, vision_feature_layer = return_dict if return_dict is not None else self.config.use_return_dict, (vision_feature_layer if vision_feature_layer is not None else self.config.vision_feature_layer)
        vision_feature_select_strategy, legacy_processing = (vision_feature_select_strategy if vision_feature_select_strategy is not None else self.config.vision_feature_select_strategy), False
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if pixel_values is not None and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values and inputs_embeds at the same time, and must specify either one")
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
            legacy_processing = ((input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length) or (input_ids.shape[-1] == 1 and pixel_values is not None)
        if pixel_values is not None and pixel_values.size(0) > 0:
            image_num_patches = [image_size_to_num_patches(image_size=imsize, grid_pinpoints=self.config.image_grid_pinpoints, patch_size=self.config.vision_config.image_size) for imsize in image_sizes]
            if pixel_values.dim() == 5: pixel_values = t_cat([pix_val[:num_patch] for pix_val, num_patch in zip(pixel_values, image_num_patches)], dim=0)
            elif pixel_values.dim() != 4: raise ValueError(f"pixel_values of shape {pixel_values.shape}, expect to be of 4 or 5 dimensions")
            image_features = self.vision_tower(pixel_values, output_hidden_states=True)
            selected_image_feature = image_features.hidden_states[vision_feature_layer]
            if vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
            elif vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
            image_features = t_split(self.multi_modal_projector(selected_image_feature), image_num_patches, dim=0)
            image_features, feature_lens = self.pack_image_features(image_features, image_sizes, vision_feature_select_strategy=vision_feature_select_strategy, image_newline=self.image_newline)
            if legacy_processing:
                if input_ids.shape[1] != 1:
                    inputs_embeds = inputs_embeds.to(image_features.dtype)
                    inputs_embeds, attention_mask, position_ids, labels, _ = self._merge_input_ids_with_image_features(image_features, feature_lens, inputs_embeds,
                    input_ids, attention_mask, position_ids, labels=labels)
                    cache_position = t_arange(attention_mask.shape[1], device=attention_mask.device)
                else:
                    first_layer_past_key_value = past_key_values[0][0][:, :, :, 0]
                    batch_index, non_attended_tokens = t_where(first_layer_past_key_value.float().sum(-2) == 0)
                    target_length = input_ids.shape[1]
                    extended_attention_mask = t_ones((attention_mask.shape[0], first_layer_past_key_value.shape[-1]), dtype=attention_mask.dtype, device=attention_mask.device)
                    valid_indices = non_attended_tokens < extended_attention_mask.size(-1)
                    new_batch_index, new_non_attended_tokens = batch_index[valid_indices], non_attended_tokens[valid_indices]
                    extended_attention_mask[new_batch_index, new_non_attended_tokens] = 0
                    attention_mask = t_cat((extended_attention_mask, attention_mask[:, -target_length:]), dim=1)
                    position_ids = t_sum(attention_mask, dim=1).unsqueeze(-1) - 1
                    cache_position = t_arange(attention_mask.shape[1], device=attention_mask.device)[-target_length:]
            else: inputs_embeds = inputs_embeds.masked_scatter(((input_ids == self.config.image_token_index).unsqueeze(-1).expand_as(inputs_embeds)), image_features.to(inputs_embeds.device, inputs_embeds.dtype))
        outputs = self.language_model(attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds,
        use_cache=use_cache, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
        logits, loss = outputs[0], None
        if labels is not None:
            if attention_mask is not None:
                shift_attention_mask = attention_mask[..., 1:]
                shift_logits, shift_labels = logits[..., :-1, :][shift_attention_mask.to(logits.device) != 0].contiguous(), labels[..., 1:][shift_attention_mask.to(labels.device) != 0].contiguous()
            else: shift_logits, shift_labels = logits[..., :-1, :].contiguous(), labels[..., 1:].contiguous()
            loss = CrossEntropyLoss()(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return SAPIImageCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states, attentions=outputs.attentions, image_hidden_states=image_features if pixel_values is not None else None)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, pixel_values=None, image_sizes=None, attention_mask=None, cache_position=None, num_logits_to_keep=None, **kwargs):
        legacy_processing = (input_ids is not None and (input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length)
        model_inputs = self.language_model.prepare_inputs_for_generation(input_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, attention_mask=attention_mask,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep, **kwargs)
        if legacy_processing or cache_position[0] == 0: model_inputs["pixel_values"], model_inputs["image_sizes"] = pixel_values, image_sizes
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
