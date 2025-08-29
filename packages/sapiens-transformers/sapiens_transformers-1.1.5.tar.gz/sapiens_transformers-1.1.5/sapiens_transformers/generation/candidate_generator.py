"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
import torch
from ..cache_utils import DynamicCache
from ..pytorch_utils import isin_mps_friendly
from .logits_process import LogitsProcessorList, MinLengthLogitsProcessor
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
    from .configuration_utils import GenerationConfig
class CandidateGenerator:
    def get_candidates(self, input_ids: torch.LongTensor) -> Tuple[torch.LongTensor, Optional[torch.FloatTensor]]: raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can call `get_candidates`.")
    def update_candidate_strategy(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, num_matches: int): raise NotImplementedError(f"{self.__class__} is an abstract class. Only classes inheriting this class can call `update_candidate_strategy`.")
class AssistedCandidateGenerator(CandidateGenerator):
    def __init__(self, input_ids: torch.LongTensor, assistant_model: "PreTrainedModel", generation_config: "GenerationConfig", model_kwargs: Dict, inputs_tensor: Optional[torch.Tensor] = None, logits_processor: "LogitsProcessorList" = None):
        device = assistant_model.device
        input_ids = input_ids.to(device)
        if inputs_tensor is not None: inputs_tensor = inputs_tensor.to(device)
        self.assistant_model = assistant_model
        self.num_assistant_tokens = assistant_model.generation_config.num_assistant_tokens
        self.assistant_confidence_threshold = assistant_model.generation_config.assistant_confidence_threshold
        self.assistant_model.generation_config.eos_token_id = generation_config.eos_token_id
        assistant_kwargs = {}
        for key, value in model_kwargs.items():
            if key not in ("encoder_outputs", "assistant_encoder_outputs", "past_key_values"): assistant_kwargs[key] = (value.detach().to(device) if isinstance(value, torch.Tensor) else copy.deepcopy(value))
        if "num_logits_to_keep" in assistant_kwargs.keys() and not assistant_model._supports_num_logits_to_keep(): del assistant_kwargs["num_logits_to_keep"]
        if "assistant_encoder_outputs" in model_kwargs: assistant_kwargs["encoder_outputs"] = model_kwargs["assistant_encoder_outputs"]
        elif assistant_model.config.is_encoder_decoder:
            inputs_tensor, model_input_name, assistant_kwargs = assistant_model._prepare_model_inputs(inputs_tensor, assistant_model.generation_config.bos_token_id, assistant_kwargs)
            assistant_kwargs = assistant_model._prepare_encoder_decoder_kwargs_for_generation(inputs_tensor, assistant_kwargs, model_input_name, assistant_model.generation_config)
        elif "encoder_outputs" in model_kwargs: assistant_kwargs["encoder_outputs"] = model_kwargs["encoder_outputs"]
        self.assistant_kwargs = assistant_kwargs
        if assistant_model.config.is_encoder_decoder: self.input_ids_key = "decoder_input_ids"
        elif "encoder_outputs" in assistant_kwargs:
            self.input_ids_key = "input_ids"
            self.assistant_kwargs["attention_mask"] = self.assistant_kwargs.get("decoder_attention_mask", torch.ones((input_ids.shape[0], 1), device=input_ids.device, dtype=torch.long))
        else: self.input_ids_key = "input_ids"
        self.logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        self.generation_config = copy.deepcopy(generation_config)
        self.generation_config.return_dict_in_generate = True
        self.generation_config.output_scores = True
        self.generation_config.assistant_confidence_threshold = self.assistant_confidence_threshold
        self.generation_config.is_assistant = True
        self.main_model_min_length = self.generation_config.min_length
        self.generation_config.min_length = 0
        self.generation_config.min_new_tokens = None
        for processor in self.logits_processor:
            if isinstance(processor, MinLengthLogitsProcessor): raise ValueError("Passing `MinLengthLogitsProcessor` when using `assisted_generation is disabled. Please pass in `min_length` into `.generate()` instead")
        self.generation_config.cache_implementation = None
    def get_candidates(self, input_ids: torch.LongTensor) -> Tuple[torch.LongTensor, Optional[torch.FloatTensor]]:
        input_ids = input_ids.to(self.assistant_model.device)
        new_cur_len = input_ids.shape[-1]
        max_new_tokens = min(int(self.num_assistant_tokens), self.generation_config.max_length - new_cur_len - 1)
        min_new_tokens = max(min(max_new_tokens, self.main_model_min_length - new_cur_len), 0)
        if max_new_tokens == 0: return input_ids, None
        has_past_key_values = self.assistant_kwargs.get("past_key_values", None) is not None
        if has_past_key_values:
            new_cache_size = new_cur_len - 1
            self.assistant_kwargs["past_key_values"] = _crop_past_key_values(self.assistant_model, self.assistant_kwargs["past_key_values"], new_cache_size - 1)
            self.assistant_kwargs = _prepare_attention_mask(self.assistant_kwargs, new_cur_len, self.assistant_model.config.is_encoder_decoder)
            self.assistant_kwargs = _prepare_token_type_ids(self.assistant_kwargs, new_cur_len)
        assistant_generation_kwargs = {self.input_ids_key: input_ids, "min_new_tokens": min_new_tokens, "max_new_tokens": max_new_tokens, "generation_config": self.generation_config, "logits_processor": self.logits_processor}
        assistant_output = self.assistant_model.generate(**assistant_generation_kwargs, **self.assistant_kwargs)
        self.assistant_kwargs["past_key_values"] = assistant_output.past_key_values
        candidate_logits = torch.stack(assistant_output.scores, dim=1)
        candidate_ids = assistant_output.sequences
        return candidate_ids, candidate_logits
    def update_candidate_strategy(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, num_matches: int):
        if self.assistant_model.generation_config.num_assistant_tokens_schedule in {'heuristic_transient', 'heuristic'}:
            if num_matches == int(self.num_assistant_tokens): self.num_assistant_tokens += 2.0
            else: self.num_assistant_tokens = max(1.0, self.num_assistant_tokens - 1.0)
class PromptLookupCandidateGenerator(CandidateGenerator):
    def __init__(self, eos_token_id: torch.Tensor = None, num_output_tokens: int = 10, max_matching_ngram_size: int = None, max_length: int = 20):
        self.num_output_tokens = num_output_tokens
        self.max_matching_ngram_size = max_matching_ngram_size if max_matching_ngram_size else 2
        self.max_length = max_length
        self.eos_token_id = eos_token_id
        if self.max_matching_ngram_size <= 0 or self.num_output_tokens <= 0: raise ValueError("Invalid max_matching_ngram_size or num_output_tokens")
    def get_candidates(self, input_ids: torch.LongTensor) -> Tuple[torch.LongTensor, Optional[torch.FloatTensor]]:
        input_length = input_ids.size(1)
        if self.max_length == input_length + 1: return input_ids, None
        chosen_ids = None
        match_found = False
        for ngram_size in range(min(self.max_matching_ngram_size, input_length - 1), 0, -1):
            windows = input_ids.unfold(dimension=1, size=ngram_size, step=1)
            ngram_tensor = input_ids[0, -ngram_size:]
            matches = (windows == ngram_tensor).all(dim=2)
            match_indices = matches.nonzero(as_tuple=True)[1]
            for idx in match_indices:
                start_idx = idx + ngram_size
                end_idx = start_idx + self.num_output_tokens
                end_idx = min(end_idx, input_length, self.max_length)
                if start_idx < end_idx:
                    chosen_ids = input_ids[0, start_idx:end_idx]
                    match_found = True
                    mask = isin_mps_friendly(chosen_ids, self.eos_token_id)
                    match_indices_eos = torch.nonzero(mask)
                    if match_indices_eos.numel() > 0:
                        first_eos_index = match_indices_eos[0].item()
                        chosen_ids = chosen_ids[:first_eos_index]
                    break
            if match_found: break
        if chosen_ids is None or len(chosen_ids) == 0: return input_ids, None
        chosen_ids = chosen_ids.unsqueeze(0)
        candidate_input_ids = torch.cat((input_ids, chosen_ids), dim=1)
        return candidate_input_ids, None
    def update_candidate_strategy(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, num_matches: int): return
def _crop_past_key_values(model, past_key_values, max_length):
    new_past = []
    if model.config.is_encoder_decoder:
        for idx in range(len(past_key_values)): new_past.append((past_key_values[idx][0][:, :, :max_length, :], past_key_values[idx][1][:, :, :max_length, :], past_key_values[idx][2], past_key_values[idx][3]))
        past_key_values = tuple(new_past)
    elif "gptbigcode" in model.__class__.__name__.lower() or (model.config.architectures is not None and "gptbigcode" in model.config.architectures[0].lower()):
        if model.config.multi_query:
            for idx in range(len(past_key_values)): past_key_values[idx] = past_key_values[idx][:, :max_length, :]
        else:
            for idx in range(len(past_key_values)): past_key_values[idx] = past_key_values[idx][:, :, :max_length, :]
    elif isinstance(past_key_values, DynamicCache): past_key_values.crop(max_length)
    elif past_key_values is not None:
        for idx in range(len(past_key_values)):
            if past_key_values[idx] != ([], []): new_past.append((past_key_values[idx][0][:, :, :max_length, :], past_key_values[idx][1][:, :, :max_length, :]))
            else: new_past.append((past_key_values[idx][0], past_key_values[idx][1]))
        past_key_values = tuple(new_past)
    return past_key_values
def _prepare_attention_mask(model_kwargs: Dict[str, Any], new_length: int, is_encoder_decoder: bool) -> Dict[str, Any]:
    mask_key = "decoder_attention_mask" if is_encoder_decoder else "attention_mask"
    if mask_key not in model_kwargs: return model_kwargs
    mask = model_kwargs[mask_key]
    mask_length_diff = new_length - mask.shape[1]
    if mask_length_diff < 0: model_kwargs[mask_key] = mask[:, :mask_length_diff]
    elif mask_length_diff > 0: model_kwargs[mask_key] = torch.cat([mask, mask.new_ones((mask.shape[0], mask_length_diff))], dim=-1)
    return model_kwargs
def _prepare_token_type_ids(model_kwargs: Dict[str, Any], new_length: int) -> Dict[str, Any]:
    if "token_type_ids" not in model_kwargs or model_kwargs["token_type_ids"] is None: return model_kwargs
    token_type_ids = model_kwargs["token_type_ids"]
    final_token_type = token_type_ids[:, -1].unsqueeze(-1)
    type_length_diff = new_length - token_type_ids.shape[1]
    if type_length_diff < 0: token_type_ids = token_type_ids[:, :type_length_diff]
    elif type_length_diff > 0:
        token_type_copies = final_token_type.repeat(1, type_length_diff)
        model_kwargs["token_type_ids"] = torch.cat([model_kwargs["token_type_ids"], token_type_copies], dim=-1)
    return model_kwargs
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
