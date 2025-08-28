"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch.nn import CrossEntropyLoss
from sapiens_transformers.models.instructblip.configuration_instructblip import (InstructBlipQFormerConfig, InstructBlipVisionConfig)
from sapiens_transformers.models.instructblip.modeling_instructblip import (InstructBlipForConditionalGeneration, InstructBlipForConditionalGenerationModelOutput)
from ...configuration_utils import PretrainedConfig
from ...models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class InstructBlipVideoVisionConfig(InstructBlipVisionConfig): pass
class InstructBlipVideoQFormerConfig(InstructBlipQFormerConfig): pass
class InstructBlipVideoConfig(PretrainedConfig):
    model_type = "instructblipvideo"
    def __init__(self, vision_config=None, qformer_config=None, text_config=None, num_query_tokens=32, video_token_index=None, **kwargs):
        super().__init__(**kwargs)
        if vision_config is None:
            vision_config = {}
            logger.info("vision_config is None. initializing the InstructBlipVideoVisionConfig with default values.")
        if qformer_config is None:
            qformer_config = {}
            logger.info("qformer_config is None. Initializing the InstructBlipVideoQFormerConfig with default values.")
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the text config with default values (`OPTConfig`).")
        self.vision_config = InstructBlipVideoVisionConfig(**vision_config)
        self.qformer_config = InstructBlipVideoQFormerConfig(**qformer_config)
        text_model_type = text_config["model_type"] if "model_type" in text_config else "opt"
        self.text_config = CONFIG_MAPPING[text_model_type](**text_config)
        self.tie_word_embeddings = self.text_config.tie_word_embeddings
        self.is_encoder_decoder = self.text_config.is_encoder_decoder
        self.num_query_tokens = num_query_tokens
        self.video_token_index = video_token_index
        self.qformer_config.encoder_hidden_size = self.vision_config.hidden_size
        self.use_decoder_only_language_model = self.text_config.model_type in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
        self.initializer_factor = 1.0
        self.initializer_range = 0.02
    @classmethod
    def from_vision_qformer_text_configs(cls, vision_config: InstructBlipVideoVisionConfig, qformer_config: InstructBlipVideoQFormerConfig, text_config: PretrainedConfig, **kwargs): return cls(vision_config=vision_config.to_dict(), qformer_config=qformer_config.to_dict(), text_config=text_config.to_dict(), **kwargs)
@dataclass
class InstructBlipVideoForConditionalGenerationModelOutput(InstructBlipForConditionalGenerationModelOutput): pass
class InstructBlipVideoForConditionalGeneration(InstructBlipForConditionalGeneration):
    def forward(self, pixel_values: torch.FloatTensor, qformer_input_ids: torch.FloatTensor, qformer_attention_mask: Optional[torch.LongTensor] = None, input_ids: Optional[torch.FloatTensor] = None,
    attention_mask: Optional[torch.LongTensor] = None, decoder_input_ids: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.LongTensor] = None,
    output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, labels: Optional[torch.LongTensor] = None, return_dict: Optional[bool] = None,
    interpolate_pos_encoding: bool = False) -> Union[Tuple, InstructBlipVideoForConditionalGenerationModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, frames, channel, height, width = pixel_values.shape
        pixel_values = pixel_values.reshape(batch_size * frames, channel, height, width)
        vision_outputs = self.vision_model(pixel_values=pixel_values, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, interpolate_pos_encoding=interpolate_pos_encoding)
        image_embeds = vision_outputs[0]
        image_attention_mask = torch.ones(image_embeds.size()[:-1], dtype=torch.long, device=image_embeds.device)
        query_tokens = self.query_tokens.expand(image_embeds.shape[0], -1, -1)
        query_attention_mask = torch.ones(query_tokens.size()[:-1], dtype=torch.long, device=image_embeds.device)
        if qformer_attention_mask is None: qformer_attention_mask = torch.ones_like(qformer_input_ids)
        qformer_input_ids = qformer_input_ids.repeat_interleave(frames, dim=0)
        qformer_attention_mask = qformer_attention_mask.repeat_interleave(frames, dim=0)
        qformer_attention_mask = torch.cat([query_attention_mask, qformer_attention_mask], dim=1)
        query_outputs = self.qformer(input_ids=qformer_input_ids, attention_mask=qformer_attention_mask, query_embeds=query_tokens, encoder_hidden_states=image_embeds,
        encoder_attention_mask=image_attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
        query_output = query_outputs[0][:, : query_tokens.size(1), :]
        language_model_inputs = self.language_projection(query_output)
        language_model_inputs = language_model_inputs.reshape(batch_size, self.config.num_query_tokens * frames, -1)
        language_model_attention_mask = torch.ones(language_model_inputs.size()[:-1], dtype=torch.long, device=language_model_inputs.device)
        inputs_embeds = self.language_model.get_input_embeddings()(input_ids)
        if attention_mask is None: attention_mask = torch.ones_like(input_ids)
        if getattr(self.config, "video_token_index", None) is not None:
            special_image_mask = (input_ids == self.config.video_token_index).unsqueeze(-1).expand_as(inputs_embeds)
            inputs_embeds[special_image_mask] = language_model_inputs.flatten()
        else:
            logger.warning_once("Expanding inputs for video tokens in InstructBLIPVideo should be done in processing. Please follow instruction here (https://gist.github.com/zucchini-nlp/65f22892b054dc0d68228af56fbeaac2) to update your InstructBLIPVideo model. Using processors without these attributes in the config is deprecated and will throw an error in v1.0.")
            inputs_embeds = torch.cat([language_model_inputs, inputs_embeds.to(language_model_inputs.device)], dim=1)
            attention_mask = torch.cat([language_model_attention_mask, attention_mask.to(language_model_attention_mask.device)], dim=1)
        if self.config.use_decoder_only_language_model:
            outputs = self.language_model(inputs_embeds=inputs_embeds, attention_mask=attention_mask, output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict)
            logits = outputs.logits if return_dict else outputs[0]
            loss = None
            if labels is not None:
                labels = labels.to(logits.device)
                logits = logits[:, -labels.size(1) :, :]
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous().to(logits.device)
                loss_fct = CrossEntropyLoss(reduction="mean")
                loss = loss_fct(shift_logits.view(-1, self.config.text_config.vocab_size), shift_labels.view(-1))
        else:
            outputs = self.language_model(inputs_embeds=inputs_embeds, attention_mask=attention_mask, decoder_input_ids=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
            output_attentions=output_attentions, output_hidden_states=output_hidden_states, return_dict=return_dict, labels=labels)
            loss = outputs.loss if return_dict else outputs[0]
            logits = outputs.logits if return_dict else outputs[1]
        if not return_dict:
            output = (logits, vision_outputs, query_outputs, outputs)
            return ((loss,) + output) if loss is not None else output
        return InstructBlipVideoForConditionalGenerationModelOutput(loss=loss, logits=logits, vision_outputs=vision_outputs, qformer_outputs=query_outputs, language_model_outputs=outputs)
    @torch.no_grad()
    def generate(self, pixel_values: torch.FloatTensor, qformer_input_ids: Optional[torch.LongTensor] = None, qformer_attention_mask: Optional[torch.LongTensor] = None,
    input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.LongTensor] = None, interpolate_pos_encoding: bool = False, **generate_kwargs) -> torch.LongTensor:
        if hasattr(self, "hf_device_map"): self._preprocess_sapiens_accelerator()
        batch_size, frames, channel, height, width = pixel_values.shape
        pixel_values = pixel_values.reshape(batch_size * frames, channel, height, width)
        image_embeds = self.vision_model(pixel_values, return_dict=True, interpolate_pos_encoding=interpolate_pos_encoding).last_hidden_state
        image_attention_mask = torch.ones(image_embeds.size()[:-1], dtype=torch.long, device=image_embeds.device)
        query_tokens = self.query_tokens.expand(image_embeds.shape[0], -1, -1)
        query_attention_mask = torch.ones(query_tokens.size()[:-1], dtype=torch.long, device=image_embeds.device)
        if qformer_attention_mask is None: qformer_attention_mask = torch.ones_like(qformer_input_ids)
        qformer_input_ids = qformer_input_ids.repeat_interleave(frames, dim=0)
        qformer_attention_mask = qformer_attention_mask.repeat_interleave(frames, dim=0)
        qformer_attention_mask = torch.cat([query_attention_mask, qformer_attention_mask], dim=1)
        query_outputs = self.qformer(input_ids=qformer_input_ids, attention_mask=qformer_attention_mask, query_embeds=query_tokens, encoder_hidden_states=image_embeds,
        encoder_attention_mask=image_attention_mask, return_dict=True)
        query_output = query_outputs.last_hidden_state[:, : query_tokens.size(1), :]
        language_model_inputs = self.language_projection(query_output)
        language_model_inputs = language_model_inputs.reshape(batch_size, self.config.num_query_tokens * frames, -1)
        language_attention_mask = torch.ones(language_model_inputs.size()[:-1], dtype=torch.long, device=language_model_inputs.device)
        if input_ids is None: input_ids = (torch.LongTensor([[self.config.text_config.bos_token_id]]).repeat(batch_size, 1).to(image_embeds.device))
        if attention_mask is None: attention_mask = torch.ones_like(input_ids)
        inputs_embeds = self.get_input_embeddings()(input_ids)
        if getattr(self.config, "video_token_index", None) is not None:
            special_image_mask = (input_ids == self.config.video_token_index).unsqueeze(-1).expand_as(inputs_embeds)
            inputs_embeds[special_image_mask] = language_model_inputs.flatten()
        else:
            logger.warning_once("Expanding inputs for video tokens in InstructBLIPVideo should be done in processing. Please follow instruction here (https://gist.github.com/zucchini-nlp/65f22892b054dc0d68228af56fbeaac2) to update your InstructBLIPVideo model. Using processors without these attributes in the config is deprecated and will throw an error in v1.0.")
            inputs_embeds = torch.cat([language_model_inputs, inputs_embeds.to(language_model_inputs.device)], dim=1)
            attention_mask = torch.cat([language_attention_mask, attention_mask.to(language_attention_mask.device)], dim=1)
            if not self.language_model.config.is_encoder_decoder:
                generate_kwargs["max_length"] = (generate_kwargs.get("max_length", 20) + language_model_inputs.shape[1] - 1)
                generate_kwargs["min_length"] = generate_kwargs.get("min_length", 0) + language_model_inputs.shape[1]
        outputs = self.language_model.generate(inputs_embeds=inputs_embeds, attention_mask=attention_mask, **generate_kwargs)
        if not self.language_model.config.is_encoder_decoder:
            bos_token_id = (2 if self.config.text_config.architectures[0] == "LLaMAForCausalLM" else self.config.text_config.bos_token_id)
            bos_tokens = torch.LongTensor([[bos_token_id]]).repeat(batch_size, 1).to(image_embeds.device)
            if not isinstance(outputs, torch.Tensor): outputs.sequences = torch.cat([bos_tokens, outputs.sequences], dim=-1)
            else: outputs = torch.cat([bos_tokens, outputs], dim=-1)
        return outputs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
