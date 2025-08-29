"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from sapiens_transformers.models.llava_next.modeling_llava_next import (LlavaNextCausalLMOutputWithPast, LlavaNextForConditionalGeneration, image_size_to_num_patches)
from ...configuration_utils import PretrainedConfig
from ...utils import (logging, replace_return_docstrings)
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class LlavaNextVideoConfig(PretrainedConfig):
    model_type = "llava_next_video"
    is_composition = True
    def __init__(self, vision_config=None, text_config=None, ignore_index=-100, image_token_index=32001, projector_hidden_act="gelu", vision_feature_select_strategy="default",
    vision_feature_layer=-2, image_grid_pinpoints=None, tie_word_embeddings=False, video_token_index=32000, spatial_pool_mode="average", spatial_pool_stride=2,
    image_seq_length=576, video_seq_length=288, **kwargs):
        self.video_token_index = video_token_index
        self.spatial_pool_mode = spatial_pool_mode
        self.spatial_pool_stride = spatial_pool_stride
        self.image_seq_length = image_seq_length
        self.video_seq_length = video_seq_length
        self.ignore_index = ignore_index
        self.image_token_index = image_token_index
        self.projector_hidden_act = projector_hidden_act
        if vision_feature_select_strategy not in ["default", "full"]: raise ValueError(f"vision_feature_select_strategy should be one of 'default', 'full'. Got: {vision_feature_select_strategy}")
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.vision_feature_layer = vision_feature_layer
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
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "llama"
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None: text_config = CONFIG_MAPPING["llama"]()
        self.text_config = text_config
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
@dataclass
class LlavaNextVideoCausalLMOutputWithPast(LlavaNextCausalLMOutputWithPast):
    video_hidden_states: Optional[torch.FloatTensor] = None
class LlavaNextVideoPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        mode = config.spatial_pool_mode
        stride = config.spatial_pool_stride
        out_channels = getattr(config, "spatial_pool_out_channels", config.vision_config.hidden_size)
        self.image_size = config.vision_config.image_size // config.vision_config.patch_size**2
        if mode == "average": self.pool = nn.AvgPool2d(kernel_size=stride, stride=stride)
        elif mode == "max": self.pool = nn.MaxPool2d(kernel_size=stride, stride=stride)
        elif mode == "conv": self.pool = nn.Conv2d(in_channels=config.vision_config.hidden_size, out_channels=out_channels, kernel_size=stride, stride=stride)
        else: raise ValueError(f"Unknown pooling mode: {mode}. Has to be one of [`average`, `max`, `conv`]")
    def forward(self, image_features):
        ori_width = int(math.sqrt(image_features.shape[1] * self.image_size // self.image_size))
        ori_height = int(ori_width * self.image_size // self.image_size)
        batch_size, _, dim = image_features.shape
        image_features_spatial = image_features.view(batch_size, ori_height, ori_height, dim).permute(0, 3, 1, 2)
        image_features_spatial_pool = self.pool(image_features_spatial)
        return image_features_spatial_pool.flatten(2).transpose(1, 2).contiguous()
class LlavaNextVideoForConditionalGeneration(LlavaNextForConditionalGeneration):
    def __init__(self, config: LlavaNextVideoConfig, **super_kwargs):
        super().__init__(config, **super_kwargs)
        self.vision_resampler = LlavaNextVideoPooler(config)
        self.post_init()
    def _get_image_features(self, pixel_values, image_sizes):
        image_num_patches = [image_size_to_num_patches(image_size=imsize, grid_pinpoints=self.config.image_grid_pinpoints, patch_size=self.config.vision_config.image_size) for imsize in image_sizes]
        if pixel_values.dim() == 5:
            _pixel_values_list = [pix_val[:num_patch] for pix_val, num_patch in zip(pixel_values, image_num_patches)]
            pixel_values = torch.cat(_pixel_values_list, dim=0)
        elif pixel_values.dim() != 4: raise ValueError(f"pixel_values of shape {pixel_values.shape}, expect to be of 4 or 5 dimensions")
        image_features = self.vision_tower(pixel_values, output_hidden_states=True)
        selected_image_feature = image_features.hidden_states[self.vision_feature_layer]
        if self.vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
        elif self.vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
        image_features = self.multi_modal_projector(selected_image_feature)
        image_features = torch.split(image_features, image_num_patches, dim=0)
        return image_features
    def _get_video_features(self, pixel_values):
        batch_size, frames, channels, height, width = pixel_values.shape
        pixel_values = pixel_values.reshape(batch_size * frames, channels, height, width)
        image_features = self.vision_tower(pixel_values, output_hidden_states=True)
        selected_image_feature = image_features.hidden_states[self.vision_feature_layer]
        if self.vision_feature_select_strategy == "default": selected_image_feature = selected_image_feature[:, 1:]
        elif self.vision_feature_select_strategy == "full": selected_image_feature = selected_image_feature
        image_features = self.vision_resampler(selected_image_feature)
        image_features = self.multi_modal_projector(image_features)
        image_features = torch.split(image_features, frames, dim=0)
        return image_features
    def forward(self, input_ids: torch.LongTensor = None, pixel_values: torch.FloatTensor = None, pixel_values_videos: torch.FloatTensor = None, image_sizes: Optional[torch.LongTensor] = None,
    attention_mask: Optional[torch.Tensor] = None, position_ids: Optional[torch.LongTensor] = None, past_key_values: Optional[List[torch.FloatTensor]] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, vision_feature_layer: Optional[int] = None, vision_feature_select_strategy: Optional[str] = None,
    labels: Optional[torch.LongTensor] = None, use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None, cache_position: Optional[torch.LongTensor] = None, num_logits_to_keep: int = 0) -> Union[Tuple, LlavaNextVideoCausalLMOutputWithPast]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        self.vision_feature_layer = (vision_feature_layer if vision_feature_layer is not None else self.config.vision_feature_layer)
        self.vision_feature_select_strategy = (vision_feature_select_strategy if vision_feature_select_strategy is not None else self.config.vision_feature_select_strategy)
        if (input_ids is None) ^ (inputs_embeds is not None): raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time, and must specify either one")
        if (pixel_values is not None or pixel_values_videos is not None) and inputs_embeds is not None: raise ValueError("You cannot specify both pixel_values and inputs_embeds at the same time, and must specify either one")
        legacy_processing = False
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
            img_token_not_enough = (input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length
            video_token_not_enough = (input_ids == self.config.video_token_index).sum(1).max() < self.config.video_seq_length
            inputs_not_expanded = (img_token_not_enough and pixel_values is not None) or (video_token_not_enough and pixel_values_videos is not None)
            pixels_present = input_ids.shape[-1] == 1 and (pixel_values is not None or pixel_values_videos is not None)
            legacy_processing = inputs_not_expanded or pixels_present
        image_features = feature_lens = None
        if pixel_values is not None and pixel_values.size(0) > 0:
            image_features = self._get_image_features(pixel_values, image_sizes)
            image_features, feature_lens = self.pack_image_features(image_features, image_sizes, self.vision_feature_select_strategy, image_newline=self.image_newline)
        video_features = video_feature_lens = None
        if pixel_values_videos is not None and pixel_values_videos.size(0) > 0:
            video_features = self._get_video_features(pixel_values_videos)
            video_features = [feature.flatten(0, 1) for feature in video_features]
            video_feature_lens = [feature.size(0) for feature in video_features]
            video_features = torch.cat(video_features, dim=0)
            video_feature_lens = torch.tensor(video_feature_lens, dtype=torch.long, device=video_features.device)
        if legacy_processing:
            logger.warning_once("Expanding inputs for image.video tokens in LLaVa-NeXT-Video should be done in processing. Please add `patch_size` and `vision_feature_select_strategy` to the model's processing config or set directly with `processor.patch_size = {{patch_size}}` and processor.vision_feature_select_strategy = {{vision_feature_select_strategy}}`. Using processors without these attributes in the config is deprecated and will throw an error in v1.0.")
            if input_ids.shape[1] != 1:
                iterator = ((image_features, feature_lens, self.config.image_token_index), (video_features, video_feature_lens, self.config.video_token_index),)
                for features, lens, special_token in iterator:
                    if features is not None: (inputs_embeds, attention_mask, position_ids, labels, input_ids) = self._merge_input_ids_with_image_features(features, lens, inputs_embeds, input_ids, attention_mask, position_ids, labels=labels, image_token_index=special_token)
                cache_position = torch.arange(attention_mask.shape[1], device=attention_mask.device)
            else:
                first_layer_past_key_value = past_key_values[0][0][:, :, :, 0]
                batch_index, non_attended_tokens = torch.where(first_layer_past_key_value.float().sum(-2) == 0)
                target_length = input_ids.shape[1]
                past_length = first_layer_past_key_value.shape[-1]
                extended_attention_mask = torch.ones((attention_mask.shape[0], past_length), dtype=attention_mask.dtype, device=attention_mask.device)
                valid_indices = non_attended_tokens < extended_attention_mask.size(-1)
                new_batch_index = batch_index[valid_indices]
                new_non_attended_tokens = non_attended_tokens[valid_indices]
                extended_attention_mask[new_batch_index, new_non_attended_tokens] = 0
                attention_mask = torch.cat((extended_attention_mask, attention_mask[:, -target_length:]), dim=1)
                position_ids = torch.sum(attention_mask, dim=1).unsqueeze(-1) - 1
                cache_position = torch.arange(attention_mask.shape[1], device=attention_mask.device)[-target_length:]
        else:
            if image_features is not None:
                special_image_mask = ((input_ids == self.config.image_token_index).unsqueeze(-1).expand_as(inputs_embeds))
                image_features = image_features.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter(special_image_mask, image_features)
            if video_features is not None:
                special_image_mask = ((input_ids == self.config.video_token_index).unsqueeze(-1).expand_as(inputs_embeds))
                video_features = video_features.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter(special_image_mask, video_features)
        outputs = self.language_model(attention_mask=attention_mask, position_ids=position_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, cache_position=cache_position, num_logits_to_keep=num_logits_to_keep)
        logits = outputs[0]
        loss = None
        if labels is not None:
            if attention_mask is not None:
                shift_attention_mask = attention_mask[..., 1:]
                shift_logits = logits[..., :-1, :][shift_attention_mask.to(logits.device) != 0].contiguous()
                shift_labels = labels[..., 1:][shift_attention_mask.to(labels.device) != 0].contiguous()
            else:
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1).to(shift_logits.device))
        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output
        return LlavaNextVideoCausalLMOutputWithPast(loss=loss, logits=logits, past_key_values=outputs.past_key_values, hidden_states=outputs.hidden_states,
        attentions=outputs.attentions, image_hidden_states=image_features if pixel_values is not None else None, video_hidden_states=video_features if pixel_values_videos is not None else None)
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, pixel_values=None, pixel_values_videos=None, image_sizes=None,
    attention_mask=None, cache_position=None, num_logits_to_keep=None, **kwargs):
        if input_ids is not None:
            img_token_not_enough = (input_ids == self.config.image_token_index).sum(1).max() < self.config.image_seq_length
            video_token_not_enough = (input_ids == self.config.video_token_index).sum(1).max() < self.config.video_seq_length
            legacy_processing = (img_token_not_enough and pixel_values is not None) or (video_token_not_enough and pixel_values_videos is not None)
        model_inputs = self.language_model.prepare_inputs_for_generation(input_ids, past_key_values=past_key_values, inputs_embeds=inputs_embeds, attention_mask=attention_mask,
        cache_position=cache_position, num_logits_to_keep=num_logits_to_keep, **kwargs)
        if legacy_processing or cache_position[0] == 0:
            model_inputs["pixel_values"] = pixel_values
            model_inputs["pixel_values_videos"] = pixel_values_videos
            model_inputs["image_sizes"] = image_sizes
        return model_inputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
