"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch.nn import Module, AvgPool2d, MaxPool2d, Conv2d, CrossEntropyLoss
from torch import (FloatTensor as t_FloatTensor, cat as t_cat, split as t_split, LongTensor as t_LongTensor, Tensor as t_Tensor, tensor as t_tensor, long as t_long,
arange as t_arange, where as t_where, ones as t_ones, sum as t_sum)
class SAPIVideoPooler(Module):
    def __init__(self, config):
        super().__init__()
        mode, stride, out_channels = config.spatial_pool_mode, config.spatial_pool_stride, getattr(config, "spatial_pool_out_channels", config.vision_config.hidden_size)
        self.image_size = config.vision_config.image_size // config.vision_config.patch_size**2
        if mode == "average": self.pool = AvgPool2d(kernel_size=stride, stride=stride)
        elif mode == "max": self.pool = MaxPool2d(kernel_size=stride, stride=stride)
        elif mode == "conv": self.pool = Conv2d(in_channels=config.vision_config.hidden_size, out_channels=out_channels, kernel_size=stride, stride=stride)
        else: raise ValueError(f"Unknown pooling mode: {mode}. Has to be one of [`average`, `max`, `conv`]")
    def forward(self, image_features):
        from math import sqrt
        ori_height = int(int(sqrt(image_features.shape[1] * self.image_size // self.image_size)) * self.image_size // self.image_size)
        batch_size, _, dim = image_features.shape
        return self.pool(image_features.view(batch_size, ori_height, ori_height, dim).permute(0, 3, 1, 2)).flatten(2).transpose(1, 2).contiguous()
from dataclasses import dataclass
from sapiens_transformers.models.sapi_image.modeling_sapi_image import (SAPIImageCausalLMOutputWithPast, SAPIImageForConditionalGeneration, image_size_to_num_patches)
from typing import Optional, List, Union, Tuple
@dataclass
class SAPIVideoCausalLMOutputWithPast(SAPIImageCausalLMOutputWithPast): video_hidden_states: Optional[torch.FloatTensor] = None
from ...configuration_utils import PretrainedConfig
from ..auto import CONFIG_MAPPING
class SAPIVideoConfig(PretrainedConfig):
    model_type = "sapi_video"
    is_composition = True
    def __init__(self, vision_config=None, text_config=None, ignore_index=-100, image_token_index=32001, projector_hidden_act="gelu", vision_feature_select_strategy="default",
    vision_feature_layer=-2, image_grid_pinpoints=None, tie_word_embeddings=False, video_token_index=32000, spatial_pool_mode="average", spatial_pool_stride=2,
    image_seq_length=576, video_seq_length=288, **kwargs):
        self.video_token_index, self.spatial_pool_mode, self.spatial_pool_stride = video_token_index, spatial_pool_mode, spatial_pool_stride
        self.image_seq_length, self.video_seq_length, self.ignore_index = image_seq_length, video_seq_length, ignore_index
        self.image_token_index,  self.projector_hidden_act = image_token_index, projector_hidden_act
        if vision_feature_select_strategy not in ["default", "full"]: raise ValueError(f"vision_feature_select_strategy should be one of 'default', 'full'. Got: {vision_feature_select_strategy}")
        self.vision_feature_select_strategy, self.vision_feature_layer = vision_feature_select_strategy, vision_feature_layer
        image_grid_pinpoints = (image_grid_pinpoints if image_grid_pinpoints is not None else [[336, 672], [672, 336], [672, 672], [1008, 336], [336, 1008]])
        self.image_grid_pinpoints = image_grid_pinpoints
        if isinstance(vision_config, dict):
            vision_config["model_type"] = (vision_config["model_type"] if "model_type" in vision_config else "clip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["clip_vision_model"](intermediate_size=4096, hidden_size=1024, patch_size=14, image_size=336, num_hidden_layers=24,
            num_attention_heads=16, vocab_size=32000, projection_dim=768)
        self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "entity"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["entity"]()
        self.text_config = text_config
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
class SAPIVideoForConditionalGeneration(SAPIImageForConditionalGeneration):
    def __init__(self, config: SAPIVideoConfig, **super_kwargs):
        super().__init__(config, **super_kwargs)
        self.vision_resampler = SAPIVideoPooler(config)
        self.post_init()
    def _get_image_features(self, pixel_values, image_sizes):
        image_num_patches = [image_size_to_num_patches(image_size=imsize, grid_pinpoints=self.config.image_grid_pinpoints, patch_size=self.config.vision_config.image_size) for imsize in image_sizes]
        if pixel_values.dim() == 5: pixel_values = torch.cat([pix_val[:num_patch] for pix_val, num_patch in zip(pixel_values, image_num_patches)], dim=0)
        elif pixel_values.dim() != 4: raise ValueError(f"pixel_values of shape {pixel_values.shape}, expect to be of 4 or 5 dimensions")
        image_features = self.vision_tower(pixel_values, output_hidden_states=True)
        selected_image_feature = image_features.hidden_states[self.vision_feature_layer]
        if self.vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
        elif self.vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
        return torch.split(self.multi_modal_projector(selected_image_feature), image_num_patches, dim=0)
    def _get_video_features(self, pixel_values):
        batch_size, frames, channels, height, width = pixel_values.shape
        image_features = self.vision_tower(pixel_values.reshape(batch_size * frames, channels, height, width), output_hidden_states=True)
        selected_image_feature = image_features.hidden_states[self.vision_feature_layer]
        if self.vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
        elif self.vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
        return torch.split(self.multi_modal_projector(self.vision_resampler(selected_image_feature)), frames, dim=0)
    def forward(self, input_ids: torch.LongTensor = None, pixel_values: torch.FloatTensor = None, pixel_values_videos: torch.FloatTensor = None, image_sizes: Optional[torch.LongTensor] = None,
    attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, vision_feature_layer: Optional[int] = None, vision_feature_select_strategy: Optional[str] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, SAPIVideoCausalLMOutputWithPast]:
        output_attentions, output_hidden_states = output_attentions if output_attentions is not None else self.config.output_attentions, (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict, legacy_processing = return_dict if return_dict is not None else self.config.use_return_dict, False
        self.vision_feature_layer = (vision_feature_layer if vision_feature_layer is not None else self.config.vision_feature_layer)
        self.vision_feature_select_strategy = (vision_feature_select_strategy if vision_feature_select_strategy is not None else self.config.vision_feature_select_strategy)
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if (pixel_values is not None or pixel_values_videos is not None) and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values and inputs_embeds at the same time, and must specify either one")
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
            inputs_not_expanded = (((input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length) and pixel_values is not None) or (((input_ids == self.config.video_token_index).sum(1).max() < self.config.video_seq_length) and pixel_values_videos is not None)
            legacy_processing = inputs_not_expanded or (input_ids.shape[-1] == 1 and (pixel_values is not None or pixel_values_videos is not None))
        image_features = feature_lens = None
        if pixel_values is not None and pixel_values.size(0) > 0:
            image_features = self._get_image_features(pixel_values, image_sizes)
            image_features, feature_lens = self.pack_image_features(image_features, image_sizes, self.vision_feature_select_strategy, image_newline=self.image_newline)
        video_features = video_feature_lens = None
        if pixel_values_videos is not None and pixel_values_videos.size(0) > 0:
            video_features = [feature.flatten(0, 1) for feature in self._get_video_features(pixel_values_videos)]
            video_feature_lens, video_features = [feature.size(0) for feature in video_features], torch.cat(video_features, dim=0)
            video_feature_lens = torch.tensor(video_feature_lens, dtype=torch.long, device=video_features.device)
        if legacy_processing:
            if input_ids.shape[1] != 1:
                iterator = ((image_features, feature_lens, self.config.image_token_index), (video_features, video_feature_lens, self.config.video_token_index),)
                for features, lens, special_token in iterator:
                    if features is not None: (inputs_embeds, attention_mask, position_ids, labels, input_ids) = self._merge_input_ids_with_image_features(features, lens, inputs_embeds, input_ids, attention_mask, position_ids, labels=labels, image_token_index=special_token)
                cache_position = torch.arange(attention_mask.shape[1], device=attention_mask.device)
            else:
                first_layer_past_key_value = past_key_values[0][0][:, :, :, 0]
                batch_index, non_attended_tokens = torch.where(first_layer_past_key_value.float().sum(-2) == 0)
                target_length, past_length = input_ids.shape[1], first_layer_past_key_value.shape[-1]
                extended_attention_mask = torch.ones((attention_mask.shape[0], past_length), dtype=attention_mask.dtype, device=attention_mask.device)
                valid_indices = non_attended_tokens < extended_attention_mask.size(-1)
                new_batch_index, new_non_attended_tokens = batch_index[valid_indices], non_attended_tokens[valid_indices]
                extended_attention_mask[new_batch_index, new_non_attended_tokens] = 0
                attention_mask = torch.cat((extended_attention_mask, attention_mask[:, -target_length:]), dim=1)
                position_ids, cache_position = torch.sum(attention_mask, dim=1).unsqueeze(-1) - 1, torch.arange(attention_mask.shape[1], device=attention_mask.device)[-target_length:]
        else:
            if image_features is not None:
                image_features = image_features.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter(((input_ids == self.config.image_token_index).unsqueeze(-1).expand_as(inputs_embeds)), image_features)
            if video_features is not None:
                video_features = video_features.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter(((input_ids == self.config.video_token_index).unsqueeze(-1).expand_as(inputs_embeds)), video_features)
        outputs = self.language_model(attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
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
        return SAPIVideoCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states,
        attentions=outputs.attentions, image_hidden_states=image_features if pixel_values is not None else None, video_hidden_states=video_features if pixel_values_videos is not None else None)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, pixel_values=None, pixel_values_videos=None, image_sizes=None,
    attention_mask=None, cache_position=None, num_logits_to_keep=None, **kwargs):
        if input_ids is not None:
            img_token_not_enough, video_token_not_enough = (input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length, (input_ids == self.config.video_token_index).sum(1).max() < self.config.video_seq_length
            legacy_processing = (img_token_not_enough and pixel_values is not None) or (video_token_not_enough and pixel_values_videos is not None)
        model_inputs = self.language_model.prepare_inputs_for_generation(input_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, attention_mask=attention_mask,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep, **kwargs)
        if legacy_processing or cache_position[0] == 0: model_inputs["pixel_values"], model_inputs["pixel_values_videos"], model_inputs["image_sizes"] = pixel_values, pixel_values_videos, image_sizes
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
