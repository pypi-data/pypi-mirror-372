"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
import inspect
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.distributed as dist
from torch import nn
from torch.nn import functional as F
from ..cache_utils import (Cache, DynamicCache, EncoderDecoderCache, OffloadedCache, QuantizedCacheConfig)
from ..configuration_utils import PretrainedConfig
from ..integrations.deepspeed import is_deepspeed_zero3_enabled
from ..modeling_outputs import CausalLMOutputWithPast, Seq2SeqLMOutput
from ..pytorch_utils import isin_mps_friendly
from ..tokenization_utils import ExtensionsTrie
from ..utils import (ModelOutput, is_sapiens_accelerator_available, is_hqq_available, is_quanto_available, is_torchdynamo_compiling, logging)
from .beam_constraints import DisjunctiveConstraint, PhrasalConstraint
from .beam_search import BeamScorer, BeamSearchScorer, ConstrainedBeamSearchScorer
from .candidate_generator import (AssistedCandidateGenerator, CandidateGenerator, PromptLookupCandidateGenerator, _crop_past_key_values, _prepare_attention_mask, _prepare_token_type_ids)
from .configuration_utils import (NEED_SETUP_CACHE_CLASSES_MAPPING, QUANT_BACKEND_CLASSES_MAPPING, GenerationConfig, GenerationMode)
from .logits_process import (EncoderNoRepeatNGramLogitsProcessor, EncoderRepetitionPenaltyLogitsProcessor, EpsilonLogitsWarper, EtaLogitsWarper, ExponentialDecayLengthPenalty,
ForcedBOSTokenLogitsProcessor, ForcedEOSTokenLogitsProcessor, HammingDiversityLogitsProcessor, InfNanRemoveLogitsProcessor, LogitNormalization, LogitsProcessorList,
MinLengthLogitsProcessor, MinNewTokensLengthLogitsProcessor, MinPLogitsWarper, NoBadWordsLogitsProcessor, NoRepeatNGramLogitsProcessor, PrefixConstrainedLogitsProcessor,
RepetitionPenaltyLogitsProcessor, SequenceBiasLogitsProcessor, SuppressTokensAtBeginLogitsProcessor, SuppressTokensLogitsProcessor, TemperatureLogitsWarper, TopKLogitsWarper,
TopPLogitsWarper, TypicalLogitsWarper, UnbatchedClassifierFreeGuidanceLogitsProcessor, WatermarkLogitsProcessor)
from .stopping_criteria import (ConfidenceCriteria, EosTokenCriteria, MaxLengthCriteria, MaxTimeCriteria, StoppingCriteria, StoppingCriteriaList, StopStringCriteria)
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
    from ..tokenization_utils_base import PreTrainedTokenizerBase
    from .streamers import BaseStreamer
logger = logging.get_logger(__name__)
if is_sapiens_accelerator_available(): from sapiens_accelerator.hooks import AlignDevicesHook, add_hook_to_module
@dataclass
class GenerateDecoderOnlyOutput(ModelOutput):
    """Args:"""
    sequences: torch.LongTensor = None
    scores: Optional[Tuple[torch.FloatTensor]] = None
    logits: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None
@dataclass
class GenerateEncoderDecoderOutput(ModelOutput):
    """Args:"""
    sequences: torch.LongTensor = None
    scores: Optional[Tuple[torch.FloatTensor]] = None
    logits: Optional[Tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    cross_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    decoder_hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None
@dataclass
class GenerateBeamDecoderOnlyOutput(ModelOutput):
    """Args:"""
    sequences: torch.LongTensor = None
    sequences_scores: Optional[torch.FloatTensor] = None
    scores: Optional[Tuple[torch.FloatTensor]] = None
    logits: Optional[Tuple[torch.FloatTensor]] = None
    beam_indices: Optional[torch.LongTensor] = None
    attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None
@dataclass
class GenerateBeamEncoderDecoderOutput(ModelOutput):
    """Args:"""
    sequences: torch.LongTensor = None
    sequences_scores: Optional[torch.FloatTensor] = None
    scores: Optional[Tuple[torch.FloatTensor]] = None
    logits: Optional[Tuple[torch.FloatTensor]] = None
    beam_indices: Optional[torch.LongTensor] = None
    encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
    encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    cross_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    decoder_hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None
GreedySearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
ContrastiveSearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
SampleDecoderOnlyOutput = GenerateDecoderOnlyOutput
ContrastiveSearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
GreedySearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
SampleEncoderDecoderOutput = GenerateEncoderDecoderOutput
BeamSearchDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput
BeamSampleDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput
BeamSearchEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput
BeamSampleEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput
GreedySearchOutput = Union[GreedySearchEncoderDecoderOutput, GreedySearchDecoderOnlyOutput]
SampleOutput = Union[SampleEncoderDecoderOutput, SampleDecoderOnlyOutput]
BeamSearchOutput = Union[BeamSearchEncoderDecoderOutput, BeamSearchDecoderOnlyOutput]
BeamSampleOutput = Union[BeamSampleEncoderDecoderOutput, BeamSampleDecoderOnlyOutput]
ContrastiveSearchOutput = Union[ContrastiveSearchEncoderDecoderOutput, ContrastiveSearchDecoderOnlyOutput]
GenerateNonBeamOutput = Union[GenerateDecoderOnlyOutput, GenerateEncoderDecoderOutput]
GenerateBeamOutput = Union[GenerateBeamDecoderOnlyOutput, GenerateBeamEncoderDecoderOutput]
GenerateOutput = Union[GenerateNonBeamOutput, GenerateBeamOutput]
class GenerationMixin:
    def prepare_inputs_for_generation(self, *args, **kwargs): raise NotImplementedError("A model class needs to define a `prepare_inputs_for_generation` method in order to use `.generate()`.")
    def _prepare_model_inputs(self, inputs: Optional[torch.Tensor] = None, bos_token_id: Optional[torch.Tensor] = None, model_kwargs: Optional[Dict[str, torch.Tensor]] = None) -> Tuple[torch.Tensor, Optional[str], Dict[str, torch.Tensor]]:
        if (self.config.is_encoder_decoder and hasattr(self, "encoder") and self.encoder.main_input_name != self.main_input_name): input_name = self.encoder.main_input_name
        else: input_name = self.main_input_name
        model_kwargs = {k: v for k, v in model_kwargs.items() if v is not None or k != input_name}
        inputs_kwarg = model_kwargs.pop(input_name, None)
        if inputs_kwarg is not None and inputs is not None: raise ValueError(f"`inputs`: {inputs}` were passed alongside {input_name} which is not allowed. Make sure to either pass {inputs} or {input_name}=...")
        elif inputs_kwarg is not None: inputs = inputs_kwarg
        if input_name == "input_ids" and "inputs_embeds" in model_kwargs:
            if not self.config.is_encoder_decoder:
                has_inputs_embeds_forwarding = "inputs_embeds" in set(inspect.signature(self.prepare_inputs_for_generation).parameters.keys())
                if not has_inputs_embeds_forwarding: raise ValueError(f"You passed `inputs_embeds` to `.generate()`, but the model class {self.__class__.__name__} doesn't have its forwarding implemented.")
                model_kwargs["input_ids"] = self._maybe_initialize_input_ids_for_generation(inputs, bos_token_id, model_kwargs=model_kwargs)
            else:
                if inputs is not None: raise ValueError("You passed `inputs_embeds` and `input_ids` to `.generate()`. Please pick one.")
            inputs, input_name = model_kwargs["inputs_embeds"], "inputs_embeds"
        inputs = self._maybe_initialize_input_ids_for_generation(inputs, bos_token_id, model_kwargs)
        return inputs, input_name, model_kwargs
    def _maybe_initialize_input_ids_for_generation(self, inputs: Optional[torch.Tensor] = None, bos_token_id: Optional[torch.Tensor] = None, model_kwargs: Optional[Dict[str, torch.Tensor]] = None) -> torch.LongTensor:
        if inputs is not None: return inputs
        encoder_outputs = model_kwargs.get("encoder_outputs")
        if self.config.is_encoder_decoder and encoder_outputs is not None:
            shape = encoder_outputs.last_hidden_state.size()[:-1]
            return torch.ones(shape, dtype=torch.long, device=self.device) * -100
        batch_size = 1
        for value in model_kwargs.values():
            if isinstance(value, torch.Tensor):
                batch_size = value.shape[0]
                break
        if "inputs_embeds" in model_kwargs: return torch.ones((batch_size, 0), dtype=torch.long, device=self.device)
        if bos_token_id is None: raise ValueError("`bos_token_id` has to be defined when no `input_ids` are provided.")
        return torch.ones((batch_size, 1), dtype=torch.long, device=self.device) * bos_token_id
    def _prepare_attention_mask_for_generation(self, inputs: torch.Tensor, pad_token_id: Optional[torch.Tensor], eos_token_id: Optional[torch.Tensor]) -> torch.LongTensor:
        default_attention_mask = torch.ones(inputs.shape[:2], dtype=torch.long, device=inputs.device)
        if pad_token_id is None: return default_attention_mask
        is_input_ids = len(inputs.shape) == 2 and inputs.dtype in [torch.int, torch.long]
        if not is_input_ids: return default_attention_mask
        is_pad_token_in_inputs = (pad_token_id is not None) and (isin_mps_friendly(elements=inputs, test_elements=pad_token_id).any())
        is_pad_token_not_equal_to_eos_token_id = (eos_token_id is None) or ~(isin_mps_friendly(elements=eos_token_id, test_elements=pad_token_id).any())
        can_infer_attention_mask = is_pad_token_in_inputs * is_pad_token_not_equal_to_eos_token_id
        attention_mask_from_padding = inputs.ne(pad_token_id).long()
        attention_mask = (attention_mask_from_padding * can_infer_attention_mask + default_attention_mask * ~can_infer_attention_mask)
        return attention_mask
    def _prepare_encoder_decoder_kwargs_for_generation(self, inputs_tensor: torch.Tensor, model_kwargs, model_input_name: Optional[str], generation_config: GenerationConfig) -> Dict[str, Any]:
        """Args:"""
        encoder = self.get_encoder()
        if hasattr(self, "hf_device_map"):
            if hasattr(encoder, "_hf_hook"): encoder._hf_hook.io_same_device = True
            else: add_hook_to_module(encoder, AlignDevicesHook(io_same_device=True))
        irrelevant_prefix = ["decoder_", "cross_attn", "use_cache"]
        encoder_kwargs = {argument: value for argument, value in model_kwargs.items() if not any(argument.startswith(p) for p in irrelevant_prefix)}
        encoder_signature = set(inspect.signature(encoder.forward).parameters)
        encoder_accepts_wildcard = "kwargs" in encoder_signature or "model_kwargs" in encoder_signature
        if not encoder_accepts_wildcard: encoder_kwargs = {argument: value for argument, value in encoder_kwargs.items() if argument in encoder_signature}
        encoder_kwargs["output_attentions"] = generation_config.output_attentions
        encoder_kwargs["output_hidden_states"] = generation_config.output_hidden_states
        model_input_name = model_input_name if model_input_name is not None else self.main_input_name
        encoder_kwargs["return_dict"] = True
        encoder_kwargs[model_input_name] = inputs_tensor
        model_kwargs["encoder_outputs"]: ModelOutput = encoder(**encoder_kwargs)
        return model_kwargs
    def _prepare_decoder_input_ids_for_generation(self, batch_size: int, model_input_name: str, model_kwargs: Dict[str, torch.Tensor], decoder_start_token_id: torch.Tensor, device: torch.device = None) -> Tuple[torch.LongTensor, Dict[str, torch.Tensor]]:
        if model_kwargs is not None and "decoder_input_ids" in model_kwargs: decoder_input_ids = model_kwargs.pop("decoder_input_ids")
        elif "input_ids" in model_kwargs and model_input_name != "input_ids": decoder_input_ids = model_kwargs.pop("input_ids")
        else: decoder_input_ids = None
        if device is None: device = self.device
        if decoder_start_token_id.ndim == 1:
            if decoder_start_token_id.shape[0] != batch_size: raise ValueError(f"`decoder_start_token_id` expected to have length {batch_size} but got {decoder_start_token_id.shape[0]}")
            decoder_start_token_id = decoder_start_token_id.view(-1, 1)
        else: decoder_start_token_id = (torch.ones((batch_size, 1), dtype=torch.long, device=device) * decoder_start_token_id)
        if decoder_input_ids is None: decoder_input_ids = decoder_start_token_id
        elif "donut" in self.__class__.__name__.lower() or (self.config.model_type == "vision-encoder-decoder" and "donut" in self.config.encoder.model_type.lower()): pass
        elif self.config.model_type in ["whisper"]: pass
        elif (decoder_input_ids[:, 0] != decoder_start_token_id[:, 0]).all().item():
            decoder_input_ids = torch.cat([decoder_start_token_id, decoder_input_ids], dim=-1)
            if "decoder_attention_mask" in model_kwargs:
                decoder_attention_mask = model_kwargs["decoder_attention_mask"]
                decoder_attention_mask = torch.cat((torch.ones_like(decoder_attention_mask)[:, :1], decoder_attention_mask), dim=-1)
                model_kwargs["decoder_attention_mask"] = decoder_attention_mask
        return decoder_input_ids, model_kwargs
    @staticmethod
    def _expand_inputs_for_generation(expand_size: int = 1, is_encoder_decoder: bool = False, input_ids: Optional[torch.LongTensor] = None, **model_kwargs) -> Tuple[torch.LongTensor, Dict[str, Any]]:
        if expand_size == 1: return input_ids, model_kwargs
        def _expand_dict_for_generation(dict_to_expand):
            for key in dict_to_expand:
                if (key != "cache_position" and dict_to_expand[key] is not None and isinstance(dict_to_expand[key], torch.Tensor)): dict_to_expand[key] = dict_to_expand[key].repeat_interleave(expand_size, dim=0)
            return dict_to_expand
        if input_ids is not None: input_ids = input_ids.repeat_interleave(expand_size, dim=0)
        model_kwargs = _expand_dict_for_generation(model_kwargs)
        if is_encoder_decoder:
            if model_kwargs.get("encoder_outputs") is None: raise ValueError("If `is_encoder_decoder` is True, make sure that `encoder_outputs` is defined.")
            model_kwargs["encoder_outputs"] = _expand_dict_for_generation(model_kwargs["encoder_outputs"])
        return input_ids, model_kwargs
    def _extract_past_from_model_output(self, outputs: ModelOutput):
        """Args:"""
        past_key_values = None
        cache_name = "past_key_values"
        if "past_key_values" in outputs: past_key_values = outputs.past_key_values
        elif "mems" in outputs: past_key_values = outputs.mems
        elif "past_buckets_states" in outputs: past_key_values = outputs.past_buckets_states
        elif "cache_params" in outputs:
            past_key_values = outputs.cache_params
            cache_name = "cache_params"
        return cache_name, past_key_values
    def _update_model_kwargs_for_generation(self, outputs: ModelOutput, model_kwargs: Dict[str, Any], is_encoder_decoder: bool = False, num_new_tokens: int = 1) -> Dict[str, Any]:
        """Args:"""
        cache_name, cache = self._extract_past_from_model_output(outputs)
        model_kwargs[cache_name] = cache
        if getattr(outputs, "state", None) is not None: model_kwargs["state"] = outputs.state
        if "token_type_ids" in model_kwargs:
            token_type_ids = model_kwargs["token_type_ids"]
            model_kwargs["token_type_ids"] = torch.cat([token_type_ids, token_type_ids[:, -1].unsqueeze(-1)], dim=-1)
        if not is_encoder_decoder:
            if "attention_mask" in model_kwargs:
                attention_mask = model_kwargs["attention_mask"]
                model_kwargs["attention_mask"] = torch.cat([attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1)
        else:
            if "decoder_attention_mask" in model_kwargs:
                decoder_attention_mask = model_kwargs["decoder_attention_mask"]
                model_kwargs["decoder_attention_mask"] = torch.cat([decoder_attention_mask, decoder_attention_mask.new_ones((decoder_attention_mask.shape[0], 1))], dim=-1)
        if model_kwargs.get("use_cache", True): model_kwargs["cache_position"] = model_kwargs["cache_position"][-1:] + num_new_tokens
        else:
            past_positions = model_kwargs.pop("cache_position")
            new_positions = torch.arange(past_positions[-1] + 1, past_positions[-1] + num_new_tokens + 1, dtype=past_positions.dtype).to(past_positions.device)
            model_kwargs["cache_position"] = torch.cat((past_positions, new_positions))
        return model_kwargs
    def _reorder_cache(self, past_key_values, beam_idx): raise NotImplementedError(f"Make sure that a `_reorder_cache` function is correctly implemented in {self.__class__.__module__} to enable beam search for {self.__class__}")
    def _get_candidate_generator(self, generation_config: GenerationConfig, input_ids: torch.LongTensor, inputs_tensor: torch.Tensor, assistant_model: "PreTrainedModel", logits_processor: LogitsProcessorList, model_kwargs: Dict) -> CandidateGenerator:
        if generation_config.prompt_lookup_num_tokens is not None: candidate_generator = PromptLookupCandidateGenerator(eos_token_id=generation_config._eos_token_tensor, num_output_tokens=generation_config.prompt_lookup_num_tokens, max_matching_ngram_size=generation_config.max_matching_ngram_size, max_length=generation_config.max_length)
        else: candidate_generator = AssistedCandidateGenerator(input_ids=input_ids, assistant_model=assistant_model, generation_config=generation_config, model_kwargs=model_kwargs, inputs_tensor=inputs_tensor, logits_processor=logits_processor)
        return candidate_generator
    def _get_logits_processor(self, generation_config: GenerationConfig, input_ids_seq_length: int, encoder_input_ids: torch.LongTensor, prefix_allowed_tokens_fn: Callable[[int, torch.Tensor], List[int]], logits_processor: Optional[LogitsProcessorList], device: str = None,
    model_kwargs: Optional[Dict[str, Any]] = None, negative_prompt_ids: Optional[torch.Tensor] = None, negative_prompt_attention_mask: Optional[torch.Tensor] = None) -> LogitsProcessorList:
        processors = LogitsProcessorList()
        if generation_config.guidance_scale is not None and generation_config.guidance_scale != 1: processors.append(UnbatchedClassifierFreeGuidanceLogitsProcessor(generation_config.guidance_scale, self, unconditional_ids=negative_prompt_ids, unconditional_attention_mask=negative_prompt_attention_mask, use_cache=model_kwargs["use_cache"]))
        if generation_config.sequence_bias is not None: processors.append(SequenceBiasLogitsProcessor(sequence_bias=generation_config.sequence_bias))
        if generation_config.diversity_penalty is not None and generation_config.diversity_penalty > 0.0: processors.append(HammingDiversityLogitsProcessor(diversity_penalty=generation_config.diversity_penalty, num_beams=generation_config.num_beams, num_beam_groups=generation_config.num_beam_groups))
        if (generation_config.encoder_repetition_penalty is not None and generation_config.encoder_repetition_penalty != 1.0): processors.append(EncoderRepetitionPenaltyLogitsProcessor(penalty=generation_config.encoder_repetition_penalty, encoder_input_ids=encoder_input_ids))
        if generation_config.repetition_penalty is not None and generation_config.repetition_penalty != 1.0: processors.append(RepetitionPenaltyLogitsProcessor(penalty=generation_config.repetition_penalty))
        if generation_config.no_repeat_ngram_size is not None and generation_config.no_repeat_ngram_size > 0: processors.append(NoRepeatNGramLogitsProcessor(generation_config.no_repeat_ngram_size))
        if (generation_config.encoder_no_repeat_ngram_size is not None and generation_config.encoder_no_repeat_ngram_size > 0): processors.append(EncoderNoRepeatNGramLogitsProcessor(generation_config.encoder_no_repeat_ngram_size, encoder_input_ids))
        if generation_config.bad_words_ids is not None: processors.append(NoBadWordsLogitsProcessor(generation_config.bad_words_ids, generation_config._eos_token_tensor))
        if (generation_config.min_length is not None and generation_config._eos_token_tensor is not None and generation_config.min_length > 0): processors.append(MinLengthLogitsProcessor(generation_config.min_length, generation_config._eos_token_tensor, device=device))
        if (generation_config.min_new_tokens is not None and generation_config._eos_token_tensor is not None and generation_config.min_new_tokens > 0): processors.append(MinNewTokensLengthLogitsProcessor(input_ids_seq_length, generation_config.min_new_tokens, generation_config._eos_token_tensor, device=device))
        if prefix_allowed_tokens_fn is not None: processors.append(PrefixConstrainedLogitsProcessor(prefix_allowed_tokens_fn, generation_config.num_beams // generation_config.num_beam_groups))
        if generation_config.forced_bos_token_id is not None: processors.append(ForcedBOSTokenLogitsProcessor(generation_config.forced_bos_token_id))
        if generation_config.forced_eos_token_id is not None: processors.append(ForcedEOSTokenLogitsProcessor(generation_config.max_length, generation_config.forced_eos_token_id, device=device))
        if generation_config.remove_invalid_values is True: processors.append(InfNanRemoveLogitsProcessor())
        if generation_config.exponential_decay_length_penalty is not None: processors.append(ExponentialDecayLengthPenalty(generation_config.exponential_decay_length_penalty, generation_config._eos_token_tensor, input_ids_seq_length))
        if generation_config.suppress_tokens is not None: processors.append(SuppressTokensLogitsProcessor(generation_config.suppress_tokens, device=device))
        if generation_config.begin_suppress_tokens is not None:
            begin_index = input_ids_seq_length
            begin_index = (begin_index if (input_ids_seq_length > 1 or generation_config.forced_bos_token_id is None) else begin_index + 1)
            processors.append(SuppressTokensAtBeginLogitsProcessor(generation_config.begin_suppress_tokens, begin_index, device=device))
        if generation_config.forced_decoder_ids is not None: raise ValueError("You have explicitly specified `forced_decoder_ids`. Please remove the `forced_decoder_ids` argument in favour of `input_ids` or `decoder_input_ids` respectively.")
        if generation_config.watermarking_config is not None: processors.append(WatermarkLogitsProcessor(vocab_size=self.config.vocab_size, device=device, greenlist_ratio=generation_config.watermarking_config.greenlist_ratio, bias=generation_config.watermarking_config.bias,
        hashing_key=generation_config.watermarking_config.hashing_key, seeding_scheme=generation_config.watermarking_config.seeding_scheme, context_width=generation_config.watermarking_config.context_width))
        processors = self._merge_criteria_processor_list(processors, logits_processor)
        if generation_config.do_sample:
            if generation_config.num_beams > 1:
                if isinstance(generation_config._eos_token_tensor, list): min_tokens_to_keep = len(generation_config._eos_token_tensor) + 1
                elif isinstance(generation_config._eos_token_tensor, torch.Tensor): min_tokens_to_keep = generation_config._eos_token_tensor.shape[0] + 1
                else: min_tokens_to_keep = 2
            else: min_tokens_to_keep = 1
            if generation_config.temperature is not None and generation_config.temperature != 1.0: processors.append(TemperatureLogitsWarper(generation_config.temperature))
            if generation_config.top_k is not None and generation_config.top_k != 0: processors.append(TopKLogitsWarper(top_k=generation_config.top_k, min_tokens_to_keep=min_tokens_to_keep))
            if generation_config.top_p is not None and generation_config.top_p < 1.0: processors.append(TopPLogitsWarper(top_p=generation_config.top_p, min_tokens_to_keep=min_tokens_to_keep))
            if generation_config.min_p is not None: processors.append(MinPLogitsWarper(min_p=generation_config.min_p, min_tokens_to_keep=min_tokens_to_keep))
            if generation_config.typical_p is not None and generation_config.typical_p < 1.0: processors.append(TypicalLogitsWarper(mass=generation_config.typical_p, min_tokens_to_keep=min_tokens_to_keep))
            if generation_config.epsilon_cutoff is not None and 0.0 < generation_config.epsilon_cutoff < 1.0: processors.append(EpsilonLogitsWarper(epsilon=generation_config.epsilon_cutoff, min_tokens_to_keep=min_tokens_to_keep))
            if generation_config.eta_cutoff is not None and 0.0 < generation_config.eta_cutoff < 1.0: processors.append(EtaLogitsWarper(epsilon=generation_config.eta_cutoff, min_tokens_to_keep=min_tokens_to_keep, device=device))
        if generation_config.renormalize_logits is True: processors.append(LogitNormalization())
        return processors
    def _get_stopping_criteria(self, generation_config: GenerationConfig, stopping_criteria: Optional[StoppingCriteriaList], tokenizer: Optional["PreTrainedTokenizerBase"] = None, **kwargs) -> StoppingCriteriaList:
        criteria = StoppingCriteriaList()
        if generation_config.max_length is not None:
            max_position_embeddings = getattr(self.config, "max_position_embeddings", None)
            criteria.append(MaxLengthCriteria(max_length=generation_config.max_length, max_position_embeddings=max_position_embeddings))
        if generation_config.max_time is not None: criteria.append(MaxTimeCriteria(max_time=generation_config.max_time))
        if generation_config.stop_strings is not None:
            if tokenizer is None: raise ValueError("There are one or more stop strings, either in the arguments to `generate` or in the model's generation config, but we could not locate a tokenizer. When generating with stop strings, you must pass the model's tokenizer to the `tokenizer` argument of `generate`.")
            criteria.append(StopStringCriteria(stop_strings=generation_config.stop_strings, tokenizer=tokenizer))
        if generation_config._eos_token_tensor is not None: criteria.append(EosTokenCriteria(eos_token_id=generation_config._eos_token_tensor))
        if (generation_config.is_assistant and generation_config.assistant_confidence_threshold is not None and generation_config.assistant_confidence_threshold > 0): criteria.append(ConfidenceCriteria(assistant_confidence_threshold=generation_config.assistant_confidence_threshold))
        criteria = self._merge_criteria_processor_list(criteria, stopping_criteria)
        return criteria
    def _merge_criteria_processor_list(self, default_list: Union[LogitsProcessorList, StoppingCriteriaList], custom_list: Union[LogitsProcessorList, StoppingCriteriaList]) -> Union[LogitsProcessorList, StoppingCriteriaList]:
        if len(custom_list) == 0: return default_list
        for default in default_list:
            for custom in custom_list:
                if type(custom) is type(default):
                    object_type = "stopping criteria" if isinstance(custom, StoppingCriteria) else "logits processor"
                    raise ValueError(f"A custom {object_type} of type {type(custom)} with values {custom} has been passed to `.generate()`, but it has already been created with the values {default}. {default} has been created by passing the corresponding arguments to generate or by the model's config default values. If you just want to change the default values of {object_type} consider passing them as arguments to `.generate()` instead of using a custom {object_type}.")
        default_list.extend(custom_list)
        return default_list
    def compute_transition_scores(self, sequences: torch.Tensor, scores: Tuple[torch.Tensor], beam_indices: Optional[torch.Tensor] = None, normalize_logits: bool = False) -> torch.Tensor:
        if beam_indices is None:
            beam_indices = torch.arange(scores[0].shape[0]).view(-1, 1).to(sequences.device)
            beam_indices = beam_indices.expand(-1, len(scores))
        scores = torch.stack(scores).reshape(len(scores), -1).transpose(0, 1)
        if normalize_logits:
            scores = scores.reshape(-1, self.config.vocab_size, scores.shape[-1])
            scores = torch.nn.functional.log_softmax(scores, dim=1)
            scores = scores.reshape(-1, scores.shape[-1])
        beam_indices_mask = beam_indices < 0
        max_beam_length = (1 - beam_indices_mask.long()).sum(-1).max()
        beam_indices = beam_indices.clone()[:, :max_beam_length]
        beam_indices_mask = beam_indices_mask[:, :max_beam_length]
        beam_indices[beam_indices_mask] = 0
        beam_sequence_indices = beam_indices * self.config.vocab_size
        cut_idx = sequences.shape[-1] - max_beam_length
        indices = sequences[:, cut_idx:] + beam_sequence_indices
        transition_scores = scores.gather(0, indices)
        transition_scores[beam_indices_mask] = 0
        return transition_scores
    def _validate_model_class(self):
        if not is_torchdynamo_compiling() and not self.can_generate():
            terminations_with_generation_support = ["ForCausalLM", "ForConditionalGeneration", "ForSpeechSeq2Seq", "ForVision2Seq"]
            raise TypeError(f"The current model class ({self.__class__.__name__}) is not compatible with `.generate()`, as it doesn't have a language model head. Classes that support generation often end in one of these names: {terminations_with_generation_support}.")
    def _validate_assistant(self, assistant_model):
        if assistant_model is None: return
        if self.config.is_encoder_decoder and not assistant_model.config.is_encoder_decoder:
            attributes_to_check = ["encoder_attention_heads", "encoder_ffn_dim", "encoder_layers"]
            attributes_to_check = [attr for attr in dir(assistant_model.config) if attr in attributes_to_check]
            are_equal = all(getattr(self.config, attr) == getattr(assistant_model.config, attr) for attr in attributes_to_check)
            if not are_equal: raise ValueError("The main model and the assistant don't have compatible encoder-dependent input shapes. Ensure you load the assistant with the correct encoder-decoder class, e.g. `AutoModelForSpeechSeq2Seq` for Whisper.")
        if not self.config.get_text_config().vocab_size == assistant_model.config.get_text_config().vocab_size: raise ValueError("Make sure the main and assistant model use the same tokenizer")
    def _validate_model_kwargs(self, model_kwargs: Dict[str, Any]):
        if isinstance(model_kwargs.get("past_key_values", None), Cache) and not self._supports_cache_class: raise ValueError(f"{self.__class__.__name__} does not support an instance of `Cache` as `past_key_values`. Please check the model documentation for supported cache formats.")
        if self.config.is_encoder_decoder:
            for key in ["decoder_input_ids"]: model_kwargs.pop(key, None)
        unused_model_args = []
        model_args = set(inspect.signature(self.prepare_inputs_for_generation).parameters)
        if "kwargs" in model_args or "model_kwargs" in model_args: model_args |= set(inspect.signature(self.forward).parameters)
        if self.config.is_encoder_decoder:
            base_model = getattr(self, self.base_model_prefix, None)
            encoder = getattr(self, "encoder", None)
            if encoder is None and base_model is not None: encoder = getattr(base_model, "encoder", None)
            if encoder is not None:
                encoder_model_args = set(inspect.signature(encoder.forward).parameters)
                model_args |= encoder_model_args
            decoder = getattr(self, "decoder", None)
            if decoder is None and base_model is not None: decoder = getattr(base_model, "decoder", None)
            if decoder is not None:
                decoder_model_args = set(inspect.signature(decoder.forward).parameters)
                model_args |= {f"decoder_{x}" for x in decoder_model_args}
            if "assistant_encoder_outputs" in model_kwargs: model_args |= {"assistant_encoder_outputs"}
        for key, value in model_kwargs.items():
            if value is not None and key not in model_args: unused_model_args.append(key)
        if unused_model_args: raise ValueError(f"The following `model_kwargs` are not used by the model: {unused_model_args} (note: typos in the generate arguments will also show up in this list)")
    def _validate_generated_length(self, generation_config, input_ids_length, has_default_max_length):
        if is_torchdynamo_compiling(): return
        if has_default_max_length and generation_config.max_new_tokens is None and generation_config.max_length == 20: warnings.warn(f"Using the model-agnostic default `max_length` (={generation_config.max_length}) to control the generation length. We recommend setting `max_new_tokens` to control the maximum length of the generation.", UserWarning)
        if input_ids_length >= generation_config.max_length:
            input_ids_string = "decoder_input_ids" if self.config.is_encoder_decoder else "input_ids"
            raise ValueError(f"Input length of {input_ids_string} is {input_ids_length}, but `max_length` is set to {generation_config.max_length}. This can lead to unexpected behavior. You should consider increasing `max_length` or, better yet, setting `max_new_tokens`.")
        min_length_error_suffix = (" Generation will stop at the defined maximum length. You should decrease the minimum length and/or increase the maximum length.")
        if has_default_max_length: min_length_error_suffix += (f" Note that `max_length` is set to {generation_config.max_length}, its default value.")
        if generation_config.min_length is not None and generation_config.min_length > generation_config.max_length: warnings.warn(f"Unfeasible length constraints: `min_length` ({generation_config.min_length}) is larger than the maximum possible length ({generation_config.max_length})." + min_length_error_suffix, UserWarning)
        if generation_config.min_new_tokens is not None:
            min_length = generation_config.min_new_tokens + input_ids_length
            if min_length > generation_config.max_length: warnings.warn(f"Unfeasible length constraints: `min_new_tokens` ({generation_config.min_new_tokens}), when added to the prompt length ({input_ids_length}), is larger than the maximum possible length ({generation_config.max_length})." + min_length_error_suffix, UserWarning)
    def _prepare_generated_length(self, generation_config, has_default_max_length, has_default_min_length, model_input_name, input_ids_length, inputs_tensor):
        if generation_config.max_new_tokens is not None:
            if not has_default_max_length and generation_config.max_length is not None: logger.warning(f"Both `max_new_tokens` (={generation_config.max_new_tokens}) and `max_length`(={generation_config.max_length}) seem to have been set. `max_new_tokens` will take precedence. Please refer to the documentation for more information.")
            generation_config.max_length = generation_config.max_new_tokens + input_ids_length
        elif (model_input_name == "inputs_embeds" and input_ids_length != inputs_tensor.shape[1] and not self.config.is_encoder_decoder): generation_config.max_length -= inputs_tensor.shape[1]
        if generation_config.min_new_tokens is not None:
            if not has_default_min_length: logger.warning(f"Both `min_new_tokens` (={generation_config.min_new_tokens}) and `min_length`(={generation_config.min_length}) seem to have been set. `min_new_tokens` will take precedence. Please refer to the documentation for more information.")
            generation_config.min_length = generation_config.min_new_tokens + input_ids_length
        elif (model_input_name == "inputs_embeds" and input_ids_length != inputs_tensor.shape[1] and not self.config.is_encoder_decoder): generation_config.min_length = max(generation_config.min_length - inputs_tensor.shape[1], 0)
        return generation_config
    def _prepare_generation_config(self, generation_config: Optional[GenerationConfig], **kwargs: Dict) -> Tuple[GenerationConfig, Dict]:
        using_model_generation_config = False
        if generation_config is None:
            if (not is_torchdynamo_compiling() and self.generation_config._from_model_config and self.generation_config._original_object_hash == hash(self.generation_config) and len(self.config._get_non_default_generation_parameters()) > 0):
                new_generation_config = GenerationConfig.from_model_config(self.config)
                if new_generation_config != self.generation_config:
                    warnings.warn("You have modified the pretrained model configuration to control generation. This is a deprecated strategy to control generation and will be removed in v5.", UserWarning)
                    self.generation_config = new_generation_config
            generation_config = self.generation_config
            using_model_generation_config = True
        if not is_torchdynamo_compiling():
            generation_config = copy.deepcopy(generation_config)
            model_kwargs = generation_config.update(**kwargs)
            if not using_model_generation_config:
                if generation_config.bos_token_id is None: generation_config.bos_token_id = self.generation_config.bos_token_id
                if generation_config.eos_token_id is None: generation_config.eos_token_id = self.generation_config.eos_token_id
                if generation_config.pad_token_id is None: generation_config.pad_token_id = self.generation_config.pad_token_id
                if generation_config.decoder_start_token_id is None: generation_config.decoder_start_token_id = self.generation_config.decoder_start_token_id
        else: model_kwargs = kwargs
        return generation_config, model_kwargs
    def _get_initial_cache_position(self, input_ids, model_kwargs):
        if "inputs_embeds" in model_kwargs: cache_position = torch.ones_like(model_kwargs["inputs_embeds"][0, :, 0], dtype=torch.int64).cumsum(0) - 1
        else: cache_position = torch.ones_like(input_ids[0, :], dtype=torch.int64).cumsum(0) - 1
        past_length = 0
        if model_kwargs.get("past_key_values") is not None:
            cache = model_kwargs["past_key_values"]
            past_length = 0
            if not isinstance(cache, Cache): past_length = cache[0][0].shape[2]
            elif hasattr(cache, "get_seq_length") and cache.get_seq_length() is not None: past_length = cache.get_seq_length()
            if not is_torchdynamo_compiling(): cache_position = cache_position[past_length:]
        model_kwargs["cache_position"] = cache_position
        return model_kwargs
    def _get_cache(self, cache_implementation: str, batch_size: int, max_cache_len: int, device: torch.device, model_kwargs) -> Cache:
        cache_cls: Cache = NEED_SETUP_CACHE_CLASSES_MAPPING[cache_implementation]
        requires_cross_attention_cache = (self.config.is_encoder_decoder or model_kwargs.get("encoder_outputs") is not None)
        if hasattr(self, "_cache"): cache_to_check = self._cache.self_attention_cache if requires_cross_attention_cache else self._cache
        if cache_implementation == "sliding_window": max_cache_len = min(self.config.sliding_window, max_cache_len)
        need_new_cache = (not hasattr(self, "_cache") or (not isinstance(cache_to_check, cache_cls)) or cache_to_check.batch_size != batch_size)
        if cache_implementation != "mamba": need_new_cache = need_new_cache or cache_to_check.max_cache_len < max_cache_len
        if requires_cross_attention_cache and hasattr(self, "_cache"): need_new_cache = (need_new_cache or self._cache.cross_attention_cache.max_cache_len != model_kwargs["encoder_outputs"][0].shape[1])
        if need_new_cache:
            if hasattr(self.config, "_pre_quantization_dtype"): cache_dtype = self.config._pre_quantization_dtype
            else:
                if not is_torchdynamo_compiling(): cache_dtype = self.dtype
                else: cache_dtype = self.get_output_embeddings().weight.dtype
            def get_layer_device_map(execution_device_map: Optional[dict] = None):
                if execution_device_map is None or len(execution_device_map) <= 1: return None
                layer_device_map = {}
                for layer in execution_device_map:
                    for idx in range(self.config.num_hidden_layers):
                        if f".{idx}." in f"{layer}.":
                            layer_device_map[idx] = execution_device_map[layer]
                            break
                for idx in range(self.config.num_hidden_layers):
                    if idx not in layer_device_map: raise RuntimeError(f"layer {idx} has not been mapped to a device.")
                return layer_device_map
            execution_device_map = None
            if hasattr(self, "hf_device_map"):
                main_device = [d for d in self.hf_device_map.values() if d not in ["cpu", "disk"]][0]
                execution_device_map = {name: main_device if device in ["cpu", "disk"] else device for name, device in self.hf_device_map.items()}
            layer_device_map = get_layer_device_map(execution_device_map)
            cache_kwargs = {"config": self.config.get_text_config(), "max_batch_size": batch_size, "max_cache_len": max_cache_len, "device": device, "dtype": cache_dtype, "layer_device_map": layer_device_map}
            self._cache = cache_cls(**cache_kwargs)
            if requires_cross_attention_cache:
                encoder_kwargs = cache_kwargs.copy()
                encoder_kwargs["max_cache_len"] = model_kwargs["encoder_outputs"][0].shape[1]
                self._cache = EncoderDecoderCache(self._cache, cache_cls(**encoder_kwargs))
        else: self._cache.reset()
        return self._cache
    def _supports_default_dynamic_cache(self) -> bool: return self._supports_cache_class and "jamba" not in self.__class__.__name__.lower()
    def _prepare_cache_for_generation(self, generation_config: GenerationConfig, model_kwargs: Dict, assistant_model: "PreTrainedModel", batch_size: int, max_cache_length: int, device: torch.device) -> bool:
        cache_name = "past_key_values" if "mamba" not in self.__class__.__name__.lower() else "cache_params"
        requires_cross_attention_cache = (self.config.is_encoder_decoder or model_kwargs.get("encoder_outputs") is not None)
        user_defined_cache = model_kwargs.get(cache_name)
        if user_defined_cache is not None:
            if generation_config.cache_implementation is not None: raise ValueError(f"Passing both `cache_implementation` (used to initialize certain caches) and `{cache_name}` (a Cache object) is unsupported. Please use only one of the two.")
            if isinstance(user_defined_cache, tuple) and self._supports_default_dynamic_cache(): model_kwargs[cache_name] = (DynamicCache.from_legacy_cache(user_defined_cache) if not requires_cross_attention_cache else EncoderDecoderCache.from_legacy_cache(user_defined_cache))
            return
        if generation_config.use_cache is False: return
        if not self._supports_default_dynamic_cache():
            if generation_config.cache_implementation is not None: warnings.warn(f"This model does not support `Cache` instances, it only supports the legacy cache format (tuple of tuples). `cache_implementation` (set to {generation_config.cache_implementation}) will be ignored.", UserWarning)
            return
        if assistant_model is not None and generation_config.cache_implementation is not None:
            logger.warning_once(f"An assistant model is provided, using a dynamic cache instead of a cache of type='{generation_config.cache_implementation}'.")
            generation_config.cache_implementation = None
        if generation_config.cache_implementation is not None:
            if generation_config.cache_implementation in NEED_SETUP_CACHE_CLASSES_MAPPING:
                if generation_config.cache_implementation == "static" and not self._supports_static_cache: raise ValueError("This model does not support `cache_implementation='static'`.")
                model_kwargs[cache_name] = self._get_cache(cache_implementation=generation_config.cache_implementation, batch_size=max(generation_config.num_beams, generation_config.num_return_sequences) * batch_size, max_cache_len=max_cache_length, device=device, model_kwargs=model_kwargs)
            elif generation_config.cache_implementation == "quantized":
                if not self._supports_quantized_cache: raise ValueError("This model does not support the quantized cache. If you want your model to support quantized cache, please open an issue and tag @zucchini-nlp.")
                cache_config = (generation_config.cache_config if generation_config.cache_config is not None else QuantizedCacheConfig())
                cache_class = QUANT_BACKEND_CLASSES_MAPPING[cache_config.backend]
                if cache_config.backend == "quanto" and not is_quanto_available(): raise ImportError("You need to install `quanto` in order to use KV cache quantization with quanto backend. Please install it via  with `pip install quanto`")
                elif cache_config.backend == "HQQ" and not is_hqq_available(): raise ImportError("You need to install `HQQ` in order to use KV cache quantization with HQQ backend. Please install it via  with `pip install hqq`")
                model_kwargs[cache_name] = cache_class(cache_config)
            elif generation_config.cache_implementation == "offloaded": model_kwargs[cache_name] = OffloadedCache()
        else: model_kwargs[cache_name] = (DynamicCache() if not requires_cross_attention_cache else EncoderDecoderCache(DynamicCache(), DynamicCache()))
    def _supports_num_logits_to_keep(self) -> bool: return "num_logits_to_keep" in set(inspect.signature(self.forward).parameters.keys())
    def _prepare_special_tokens(self, generation_config: GenerationConfig, kwargs_has_attention_mask: Optional[bool] = None, device: Optional[Union[torch.device, str]] = None):
        def _tensor_or_none(token, device=None):
            if token is None: return token
            device = device if device is not None else self.device
            if isinstance(token, torch.Tensor): return token.to(device)
            return torch.tensor(token, device=device, dtype=torch.long)
        bos_token_tensor = _tensor_or_none(generation_config.bos_token_id, device=device)
        eos_token_tensor = _tensor_or_none(generation_config.eos_token_id, device=device)
        pad_token_tensor = _tensor_or_none(generation_config.pad_token_id, device=device)
        decoder_start_token_tensor = _tensor_or_none(generation_config.decoder_start_token_id, device=device)
        if self.config.is_encoder_decoder: decoder_start_token_tensor = (decoder_start_token_tensor if decoder_start_token_tensor is not None else bos_token_tensor)
        if eos_token_tensor is not None and eos_token_tensor.ndim == 0: eos_token_tensor = eos_token_tensor.unsqueeze(0)
        if pad_token_tensor is None and eos_token_tensor is not None:
            if not is_torchdynamo_compiling():
                if kwargs_has_attention_mask is not None and not kwargs_has_attention_mask: logger.warning("The attention mask and the pad token id were not set. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.")
            pad_token_tensor = eos_token_tensor[0]
        if self.config.is_encoder_decoder and decoder_start_token_tensor is None: raise ValueError("`decoder_start_token_id` or `bos_token_id` has to be defined for encoder-decoder generation.")
        if not is_torchdynamo_compiling():
            if (eos_token_tensor is not None and isin_mps_friendly(elements=eos_token_tensor, test_elements=pad_token_tensor).any()):
                if kwargs_has_attention_mask is not None and not kwargs_has_attention_mask: logger.warning_once("The attention mask is not set and cannot be inferred from input because pad token is same as eos token. As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.")
            if eos_token_tensor is not None and (torch.is_floating_point(eos_token_tensor) or (eos_token_tensor < 0).any()): logger.warning(f"`eos_token_id` should consist of positive integers, but is {eos_token_tensor}. Your generation will not stop until the maximum length is reached. Depending on other flags, it may even crash.")
        generation_config._bos_token_tensor = bos_token_tensor
        generation_config._eos_token_tensor = eos_token_tensor
        generation_config._pad_token_tensor = pad_token_tensor
        generation_config._decoder_start_token_tensor = decoder_start_token_tensor
    @torch.no_grad()
    def generate(self, inputs: Optional[torch.Tensor] = None, generation_config: Optional[GenerationConfig] = None, logits_processor: Optional[LogitsProcessorList] = None, stopping_criteria: Optional[StoppingCriteriaList] = None, prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], List[int]]] = None,
    synced_gpus: Optional[bool] = None, assistant_model: Optional["PreTrainedModel"] = None, streamer: Optional["BaseStreamer"] = None, negative_prompt_ids: Optional[torch.Tensor] = None, negative_prompt_attention_mask: Optional[torch.Tensor] = None, **kwargs) -> Union[GenerateOutput, torch.LongTensor]:
        self._validate_model_class()
        tokenizer = kwargs.pop("tokenizer", None)
        generation_config, model_kwargs = self._prepare_generation_config(generation_config, **kwargs)
        self._validate_model_kwargs(model_kwargs.copy())
        self._validate_assistant(assistant_model)
        if synced_gpus is None:
            if is_deepspeed_zero3_enabled() and dist.get_world_size() > 1: synced_gpus = True
            else: synced_gpus = False
        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
        accepts_attention_mask = "attention_mask" in set(inspect.signature(self.forward).parameters.keys())
        requires_attention_mask = "encoder_outputs" not in model_kwargs
        kwargs_has_attention_mask = model_kwargs.get("attention_mask", None) is not None
        inputs_tensor, model_input_name, model_kwargs = self._prepare_model_inputs(inputs, generation_config.bos_token_id, model_kwargs)
        batch_size = inputs_tensor.shape[0]
        device = inputs_tensor.device
        self._prepare_special_tokens(generation_config, kwargs_has_attention_mask, device=device)
        if not self.config.is_encoder_decoder and not is_torchdynamo_compiling():
            if (generation_config._pad_token_tensor is not None and batch_size > 1 and len(inputs_tensor.shape) == 2 and torch.sum(inputs_tensor[:, -1] == generation_config._pad_token_tensor) > 0): logger.warning("A decoder-only architecture is being used, but right-padding was detected! For correct generation results, please set `padding_side='left'` when initializing the tokenizer.")
        if not self.config.is_encoder_decoder and model_input_name == "inputs_embeds": model_kwargs["use_cache"] = True
        else: model_kwargs["use_cache"] = generation_config.use_cache
        if not kwargs_has_attention_mask and requires_attention_mask and accepts_attention_mask: model_kwargs["attention_mask"] = self._prepare_attention_mask_for_generation(inputs_tensor, generation_config._pad_token_tensor, generation_config._eos_token_tensor)
        elif kwargs_has_attention_mask:
            if model_input_name == "input_ids" and len(model_kwargs["attention_mask"].shape) > 2: raise ValueError("`attention_mask` passed to `generate` must be 2D.")
        if self.config.is_encoder_decoder and "encoder_outputs" not in model_kwargs: model_kwargs = self._prepare_encoder_decoder_kwargs_for_generation(inputs_tensor, model_kwargs, model_input_name, generation_config)
        if self.config.is_encoder_decoder: input_ids, model_kwargs = self._prepare_decoder_input_ids_for_generation(batch_size=batch_size, model_input_name=model_input_name,
        model_kwargs=model_kwargs, decoder_start_token_id=generation_config._decoder_start_token_tensor, device=inputs_tensor.device)
        else: input_ids = inputs_tensor if model_input_name == "input_ids" else model_kwargs.pop("input_ids")
        if generation_config.token_healing: input_ids = self.heal_tokens(input_ids, tokenizer)
        if streamer is not None: streamer.put(input_ids.cpu())
        input_ids_length = input_ids.shape[-1]
        has_default_max_length = kwargs.get("max_length") is None and generation_config.max_length is not None
        has_default_min_length = kwargs.get("min_length") is None and generation_config.min_length is not None
        generation_config = self._prepare_generated_length(generation_config=generation_config, has_default_max_length=has_default_max_length, has_default_min_length=has_default_min_length,
        model_input_name=model_input_name, inputs_tensor=inputs_tensor, input_ids_length=input_ids_length)
        if self._supports_num_logits_to_keep() and "num_logits_to_keep" not in model_kwargs: model_kwargs["num_logits_to_keep"] = 1
        self._validate_generated_length(generation_config, input_ids_length, has_default_max_length)
        cache_name = "past_key_values" if "mamba" not in self.__class__.__name__.lower() else "cache_params"
        user_defined_cache = model_kwargs.get(cache_name)
        max_cache_length = generation_config.max_length
        if (inputs_tensor.shape[1] != input_ids_length and model_input_name == "inputs_embeds" and not self.config.is_encoder_decoder): max_cache_length += inputs_tensor.shape[1]
        self._prepare_cache_for_generation(generation_config, model_kwargs, assistant_model, batch_size, max_cache_length, device)
        generation_mode = generation_config.get_generation_mode(assistant_model)
        if streamer is not None and (generation_config.num_beams > 1): raise ValueError("`streamer` cannot be used with beam search (yet!). Make sure that `num_beams` is set to 1.")
        if not is_torchdynamo_compiling() and self.device.type != input_ids.device.type: warnings.warn(f"You are calling .generate() with the `input_ids` being on a device type different than your model's device. `input_ids` is on {input_ids.device.type}, whereas the model is on {self.device.type}. You may experience unexpected behaviors or slower generation. Please make sure that you have put `input_ids` to the correct device by calling for example input_ids = input_ids.to('{self.device.type}') before running `.generate()`.", UserWarning)
        prepared_logits_processor = self._get_logits_processor(generation_config=generation_config, input_ids_seq_length=input_ids_length, encoder_input_ids=inputs_tensor, prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
        logits_processor=logits_processor, device=inputs_tensor.device, model_kwargs=model_kwargs, negative_prompt_ids=negative_prompt_ids, negative_prompt_attention_mask=negative_prompt_attention_mask)
        prepared_stopping_criteria = self._get_stopping_criteria(generation_config=generation_config, stopping_criteria=stopping_criteria, tokenizer=tokenizer, **kwargs)
        if generation_mode == GenerationMode.ASSISTED_GENERATION:
            if generation_config.num_return_sequences > 1: raise ValueError(f"num_return_sequences has to be 1 when doing assisted generate, but is {generation_config.num_return_sequences}.")
            if batch_size > 1: raise ValueError("assisted generate is only supported for batch_size = 1")
            if not model_kwargs["use_cache"]: raise ValueError("assisted generate requires `use_cache=True`")
            if generation_config.cache_implementation in ["static", "hybrid", "sliding_window"]: raise ValueError("assisted generate is not supported with Static cache classes`")
            if self._is_stateful: raise ValueError(f"assisted generation is not supported with stateful models, such as {self.__class__.__name__}")
            candidate_generator = self._get_candidate_generator(generation_config=generation_config, input_ids=input_ids, inputs_tensor=inputs_tensor, assistant_model=assistant_model, logits_processor=logits_processor, model_kwargs=model_kwargs)
            result = self._assisted_decoding(input_ids, candidate_generator=candidate_generator, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, streamer=streamer, **model_kwargs)
        elif generation_mode == GenerationMode.DOLA_GENERATION:
            if self._is_stateful: raise ValueError(f"dola decoding is not supported with stateful models, such as {self.__class__.__name__}")
            result = self._dola_decoding(input_ids, dola_layers=generation_config.dola_layers, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, streamer=streamer, **model_kwargs)
        elif generation_mode == GenerationMode.CONTRASTIVE_SEARCH:
            if not model_kwargs["use_cache"]: raise ValueError("Contrastive search requires `use_cache=True`")
            if self._is_stateful: raise ValueError(f"contrastive search is not supported with stateful models, such as {self.__class__.__name__}")
            result = self._contrastive_search(input_ids, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, streamer=streamer, **model_kwargs)
        elif generation_mode in (GenerationMode.SAMPLE, GenerationMode.GREEDY_SEARCH):
            input_ids, model_kwargs = self._expand_inputs_for_generation(input_ids=input_ids, expand_size=generation_config.num_return_sequences, is_encoder_decoder=self.config.is_encoder_decoder, **model_kwargs)
            result = self._sample(input_ids, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, streamer=streamer, **model_kwargs)
        elif generation_mode in (GenerationMode.BEAM_SAMPLE, GenerationMode.BEAM_SEARCH):
            beam_scorer = BeamSearchScorer(batch_size=batch_size, num_beams=generation_config.num_beams, device=inputs_tensor.device, length_penalty=generation_config.length_penalty, do_early_stopping=generation_config.early_stopping,
            num_beam_hyps_to_keep=generation_config.num_return_sequences, max_length=generation_config.max_length)
            input_ids, model_kwargs = self._expand_inputs_for_generation(input_ids=input_ids, expand_size=generation_config.num_beams, is_encoder_decoder=self.config.is_encoder_decoder, **model_kwargs)
            result = self._beam_search(input_ids, beam_scorer, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, **model_kwargs)
        elif generation_mode == GenerationMode.GROUP_BEAM_SEARCH:
            beam_scorer = BeamSearchScorer(batch_size=batch_size, num_beams=generation_config.num_beams, device=inputs_tensor.device, length_penalty=generation_config.length_penalty, do_early_stopping=generation_config.early_stopping,
            num_beam_hyps_to_keep=generation_config.num_return_sequences, num_beam_groups=generation_config.num_beam_groups, max_length=generation_config.max_length)
            input_ids, model_kwargs = self._expand_inputs_for_generation(input_ids=input_ids, expand_size=generation_config.num_beams, is_encoder_decoder=self.config.is_encoder_decoder, **model_kwargs)
            result = self._group_beam_search(input_ids, beam_scorer, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, **model_kwargs)
        elif generation_mode == GenerationMode.CONSTRAINED_BEAM_SEARCH:
            final_constraints = []
            if generation_config.constraints is not None: final_constraints = generation_config.constraints
            if generation_config.force_words_ids is not None:
                def typeerror(): raise ValueError(f"`force_words_ids` has to either be a `List[List[List[int]]]` or `List[List[int]]` of positive integers, but is {generation_config.force_words_ids}.")
                if (not isinstance(generation_config.force_words_ids, list) or len(generation_config.force_words_ids) == 0): typeerror()
                for word_ids in generation_config.force_words_ids:
                    if isinstance(word_ids[0], list):
                        if not isinstance(word_ids, list) or len(word_ids) == 0: typeerror()
                        if any(not isinstance(token_ids, list) for token_ids in word_ids): typeerror()
                        if any(any((not isinstance(token_id, int) or token_id < 0) for token_id in token_ids) for token_ids in word_ids): typeerror()
                        constraint = DisjunctiveConstraint(word_ids)
                    else:
                        if not isinstance(word_ids, list) or len(word_ids) == 0: typeerror()
                        if any((not isinstance(token_id, int) or token_id < 0) for token_id in word_ids): typeerror()
                        constraint = PhrasalConstraint(word_ids)
                    final_constraints.append(constraint)
            constrained_beam_scorer = ConstrainedBeamSearchScorer(constraints=final_constraints, batch_size=batch_size, num_beams=generation_config.num_beams, device=inputs_tensor.device, length_penalty=generation_config.length_penalty,
            do_early_stopping=generation_config.early_stopping, num_beam_hyps_to_keep=generation_config.num_return_sequences, max_length=generation_config.max_length)
            input_ids, model_kwargs = self._expand_inputs_for_generation(input_ids=input_ids, expand_size=generation_config.num_beams, is_encoder_decoder=self.config.is_encoder_decoder, **model_kwargs)
            result = self._constrained_beam_search(input_ids, constrained_beam_scorer=constrained_beam_scorer, logits_processor=prepared_logits_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config, synced_gpus=synced_gpus, **model_kwargs)
        if (generation_config.return_legacy_cache is not False and not is_torchdynamo_compiling() and hasattr(result, "past_key_values") and hasattr(result.past_key_values, "to_legacy_cache") and result.past_key_values.to_legacy_cache is not None):
            should_convert_cache = generation_config.return_legacy_cache
            is_user_defined_cache = user_defined_cache is not None
            is_default_cache_type = (type(result.past_key_values) == DynamicCache or (isinstance(result.past_key_values, EncoderDecoderCache) and type(result.past_key_values.self_attention_cache) == DynamicCache and type(result.past_key_values.cross_attention_cache) == DynamicCache))
            if not is_user_defined_cache and is_default_cache_type: should_convert_cache = True
            if should_convert_cache: result.past_key_values = result.past_key_values.to_legacy_cache()
        return result
    def _has_unfinished_sequences(self, this_peer_finished: bool, synced_gpus: bool, device: torch.device, cur_len: Optional[int] = None, max_length: Optional[int] = None) -> bool:
        if is_torchdynamo_compiling(): return cur_len < max_length
        else:
            if synced_gpus:
                this_peer_finished_flag = torch.tensor(0.0 if this_peer_finished else 1.0).to(device)
                dist.all_reduce(this_peer_finished_flag, op=dist.ReduceOp.SUM)
                if this_peer_finished_flag.item() == 0.0: return False
            elif this_peer_finished: return False
            return True
    def heal_tokens(self, input_ids: torch.LongTensor, tokenizer: Optional["PreTrainedTokenizerBase"] = None) -> torch.LongTensor:
        if tokenizer is None: raise ValueError(" When generating with token healing, you must pass the model's tokenizer to the `tokenizer` argument of `generate`.")
        bos_token_id, pad_token_id = tokenizer.bos_token_id, tokenizer.pad_token_id
        vocab_trie = ExtensionsTrie(tokenizer.get_vocab())
        generation_config = GenerationConfig(max_new_tokens=1, pad_token_id=pad_token_id)
        prompts = [p.strip() for p in tokenizer.batch_decode(input_ids, skip_special_tokens=True)]
        input_ids = tokenizer(prompts, return_tensors="pt", padding=True).input_ids.to(input_ids.device)
        input_ids = torch.where(input_ids == bos_token_id, pad_token_id, input_ids)
        tail_ids = input_ids[:, -1].tolist()
        space_tok = tokenizer.convert_ids_to_tokens(tokenizer.convert_tokens_to_ids(" "))[0]
        tail_toks = (tokenizer.decode(t).replace(" ", space_tok) for t in tail_ids)
        for batch_idx, (tail_id, tail_tok) in enumerate(zip(tail_ids, tail_toks)):
            batch_ids = input_ids[batch_idx]
            if torch.all(batch_ids == pad_token_id).item(): continue
            seq_bias = {(alt_tok,): 10.0 for alt_tok in vocab_trie.values(prefix=tail_tok)}
            if len(seq_bias) == 1: continue
            seq_bias[(tail_id,)] += 1.0
            generation_config.update(sequence_bias=seq_bias)
            trimmed_ids = batch_ids[:-1]
            if len(batch_ids[batch_ids != pad_token_id]) == 1: trimmed_ids[-1] = bos_token_id
            input_ids[batch_idx] = self.generate(trimmed_ids.unsqueeze(0), generation_config=generation_config)
        return input_ids
    def _dola_decoding(self, input_ids: torch.LongTensor, dola_layers: Union[str, List[int]], logits_processor: LogitsProcessorList,
    stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig, synced_gpus: bool, streamer: "BaseStreamer", **model_kwargs) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        if self.config.is_encoder_decoder: raise ValueError("DoLa decoding is only available for decoder-only models.")
        pad_token_id = generation_config._pad_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        has_eos_stopping_criteria = any(hasattr(criteria, "eos_token_id") for criteria in stopping_criteria)
        do_sample = generation_config.do_sample
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        this_peer_finished = False
        final_layer = self.config.get_text_config().num_hidden_layers
        if not self.config.tie_word_embeddings: start_layer = 0
        elif final_layer > 2: start_layer = 2
        elif final_layer == 2: start_layer = 1
        else: start_layer = 0
        if isinstance(dola_layers, str) and dola_layers == "low":
            if start_layer == final_layer // 2: candidate_premature_layers = [start_layer]
            else: candidate_premature_layers = (list(range(start_layer, final_layer // 2, 2)) if final_layer <= 40 else list(range(start_layer, 20, 2)))
        elif isinstance(dola_layers, str) and dola_layers == "high": candidate_premature_layers = (list(range(final_layer // 2, final_layer, 2)) if final_layer <= 40 else list(range(final_layer - 20, final_layer, 2)))
        elif isinstance(dola_layers, list): candidate_premature_layers = [i for i in dola_layers if i < final_layer]
        else: raise ValueError("dola_layers must be either 'low', 'high' or a list of integers.")
        lm_head = self.get_output_embeddings()
        if lm_head is None: raise ValueError("DoLa is not supported for models that don't have output embeddings.")
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            outputs = self(**model_inputs, return_dict=True, output_attentions=output_attentions, output_hidden_states=True)
            final_layer_next_token_logits = outputs.logits[:, -1, :].detach().clone().float()
            final_logits = outputs.logits[:, -1, :].float()
            candidate_premature_logits = {}
            for candidate_premature_layer in candidate_premature_layers: candidate_premature_logits[candidate_premature_layer] = lm_head(outputs.hidden_states[candidate_premature_layer][:, -1, :]).to(final_logits.device)
            if synced_gpus and this_peer_finished: continue
            next_token_logits = _dola_select_contrast(candidate_premature_layers, candidate_premature_logits, final_logits)
            next_token_scores = logits_processor(input_ids, next_token_logits)
            if return_dict_in_generate:
                if output_scores: scores += (next_token_scores,)
                if output_logits: raw_logits += (final_layer_next_token_logits,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
            else: next_tokens = torch.argmax(next_token_scores, dim=-1)
            if has_eos_stopping_criteria: next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            if streamer is not None: streamer.put(next_tokens.cpu())
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
        if streamer is not None: streamer.end()
        if return_dict_in_generate: return GenerateDecoderOnlyOutput(sequences=input_ids, scores=scores, logits=raw_logits, attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return input_ids
    @torch.no_grad()
    def _contrastive_search(self, input_ids: torch.LongTensor, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig,
    synced_gpus: bool, streamer: Optional["BaseStreamer"], **model_kwargs) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        has_eos_stopping_criteria = any(hasattr(criteria, "eos_token_id") for criteria in stopping_criteria)
        top_k = generation_config.top_k
        penalty_alpha = generation_config.penalty_alpha
        pad_token_id = generation_config._pad_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        sequential = generation_config.low_memory
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        scores = () if (return_dict_in_generate and output_scores) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        cosine_matrix_mask = torch.ones_like(input_ids, dtype=torch.long)
        if self.config.is_encoder_decoder:
            if "decoder_attention_mask" in model_kwargs and model_kwargs["decoder_attention_mask"] is not None: cosine_matrix_mask = model_kwargs["decoder_attention_mask"]
        else: cosine_matrix_mask = model_kwargs["attention_mask"]
        cosine_matrix_mask = cosine_matrix_mask.repeat_interleave(top_k, dim=0)
        this_peer_finished = False
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            if model_kwargs.get("past_key_values") is None or (isinstance(model_kwargs["past_key_values"], (Cache, EncoderDecoderCache)) and model_kwargs["past_key_values"].get_seq_length() == 0):
                model_kwargs["use_cache"] = True
                model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                outputs = self(**model_inputs, return_dict=True, output_hidden_states=True, output_attentions=output_attentions)
                if self.config.is_encoder_decoder: last_hidden_states = outputs.decoder_hidden_states[-1]
                else: last_hidden_states = outputs.hidden_states[-1]
                logit_for_next_step = outputs.logits[:, -1, :].clone().float()
                model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
                if not sequential: _, model_kwargs = self._expand_inputs_for_generation(expand_size=top_k, is_encoder_decoder=self.config.is_encoder_decoder, **model_kwargs)
                past_key_values = model_kwargs.get("past_key_values")
                if past_key_values is None: raise ValueError(f"{self.__class__.__name__} does not support caching and therefore **can't** be used for contrastive search.")
                elif (not isinstance(past_key_values[0], (tuple, torch.Tensor)) or past_key_values[0][0].shape[0] != batch_size): raise ValueError(f"{self.__class__.__name__} does not have a standard cache format and therefore **can't** be used for contrastive search without further modifications.")
            processed_logit_for_next_step = logits_processor(input_ids, logit_for_next_step)
            next_probs = nn.functional.softmax(processed_logit_for_next_step, dim=-1)
            top_k_probs, top_k_ids = torch.topk(next_probs, dim=-1, k=top_k)
            if return_dict_in_generate:
                if output_logits: raw_logits += (logit_for_next_step,)
                if output_scores: scores += (processed_logit_for_next_step,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            del outputs
            if not sequential:
                past = model_kwargs["past_key_values"]
                if isinstance(past, DynamicCache) or (isinstance(past, EncoderDecoderCache) and isinstance(past.self_attention_cache, DynamicCache)): past.batch_repeat_interleave(top_k)
                else:
                    new_key_values = []
                    for layer in past:
                        items = []
                        for item in layer: items.append(item.repeat_interleave(top_k, dim=0))
                        new_key_values.append(tuple(items))
                    past = tuple(new_key_values)
                model_kwargs["past_key_values"] = past
            if sequential:
                all_outputs = []
                for i in range(top_k):
                    next_model_inputs = self.prepare_inputs_for_generation(top_k_ids[:, i].view(-1, 1), **model_kwargs)
                    outputs = self(**next_model_inputs, return_dict=True, output_hidden_states=True, output_attentions=output_attentions)
                    if isinstance(outputs["past_key_values"], DynamicCache) or (isinstance(outputs["past_key_values"], EncoderDecoderCache) and isinstance(outputs["past_key_values"].self_attention_cache, DynamicCache)):
                        outputs["past_key_values"] = None
                        model_kwargs["past_key_values"].crop(-1)
                    all_outputs.append(outputs)
                outputs = stack_model_outputs(all_outputs, self.config.get_text_config())
            else:
                next_model_inputs = self.prepare_inputs_for_generation(top_k_ids.view(-1, 1), **model_kwargs)
                outputs = self(**next_model_inputs, return_dict=True, output_hidden_states=True, output_attentions=output_attentions)
            del next_model_inputs
            if self.config.is_encoder_decoder:
                next_hidden = outputs.decoder_hidden_states[-1]
                full_hidden_states = outputs.decoder_hidden_states
            else:
                next_hidden = outputs.hidden_states[-1]
                full_hidden_states = outputs.hidden_states
            logits = outputs.logits[:, -1, :].float()
            context_hidden = last_hidden_states.repeat_interleave(top_k, dim=0)
            selected_idx = _ranking_fast(context_hidden, next_hidden, top_k_probs, cosine_matrix_mask, penalty_alpha, top_k)
            cosine_matrix_mask = torch.cat([cosine_matrix_mask, cosine_matrix_mask.new_ones((cosine_matrix_mask.shape[0], 1))], dim=-1)
            selected_idx = selected_idx.to("cpu")
            augmented_idx = torch.tensor([x + i * top_k for i, x in enumerate(selected_idx)])
            next_tokens = top_k_ids[range(len(top_k_ids)), selected_idx]
            next_hidden = torch.stack(torch.split(next_hidden.squeeze(dim=1), top_k))
            next_hidden = next_hidden[range(batch_size), selected_idx, :]
            last_hidden_states = torch.cat([last_hidden_states, next_hidden.unsqueeze(1)], dim=1)
            next_decoder_hidden_states = ()
            for layer in full_hidden_states:
                layer = torch.stack(torch.split(layer, top_k))[range(batch_size), selected_idx, :]
                next_decoder_hidden_states += (layer,)
            if sequential:
                next_model_input = self.prepare_inputs_for_generation(top_k_ids[:, selected_idx].view(-1, 1), **model_kwargs)
                selected_outputs = self(**next_model_input, return_dict=True, output_hidden_states=False, output_attentions=False)
                next_past_key_values = selected_outputs["past_key_values"]
            else:
                _, next_past_key_values = self._extract_past_from_model_output(outputs)
                if isinstance(next_past_key_values, DynamicCache) or (isinstance(next_past_key_values, EncoderDecoderCache) and isinstance(next_past_key_values.self_attention_cache, DynamicCache)): next_past_key_values.batch_select_indices(augmented_idx)
                else:
                    new_key_values = []
                    for layer in next_past_key_values:
                        items = []
                        for item in layer: items.append(item[augmented_idx, ...])
                        new_key_values.append(tuple(items))
                    next_past_key_values = tuple(new_key_values)
            logit_for_next_step = torch.stack(torch.split(logits, top_k))[range(batch_size), selected_idx, :]
            if self.config.is_encoder_decoder:
                next_step_cross_attentions = ()
                next_step_decoder_attentions = ()
                if output_attentions:
                    for layer in outputs.cross_attentions:
                        layer = torch.stack(torch.split(layer, top_k, dim=0))[range(batch_size), selected_idx, ...]
                        next_step_cross_attentions += (layer,)
                    for layer in outputs.decoder_attentions:
                        layer = torch.stack(torch.split(layer, top_k, dim=0))[range(batch_size), selected_idx, ...]
                        next_step_decoder_attentions += (layer,)
                outputs = Seq2SeqLMOutput(past_key_values=next_past_key_values, decoder_hidden_states=next_decoder_hidden_states, decoder_attentions=next_step_decoder_attentions or None, cross_attentions=next_step_cross_attentions or None)
            else:
                next_step_attentions = ()
                if output_attentions:
                    for layer in outputs.attentions:
                        layer = torch.stack(torch.split(layer, top_k, dim=0))[range(batch_size), selected_idx, ...]
                        next_step_attentions += (layer,)
                outputs = CausalLMOutputWithPast(past_key_values=next_past_key_values, hidden_states=next_decoder_hidden_states, attentions=next_step_attentions or None)
            if synced_gpus and this_peer_finished: continue
            if has_eos_stopping_criteria: next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            if streamer is not None: streamer.put(next_tokens.cpu())
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
        if streamer is not None: streamer.end()
        if return_dict_in_generate:
            if model_kwargs.get("past_key_values") is not None:
                if isinstance(model_kwargs["past_key_values"], DynamicCache) or (isinstance(model_kwargs["past_key_values"], EncoderDecoderCache) and isinstance(model_kwargs["past_key_values"].self_attention_cache, DynamicCache)): model_kwargs["past_key_values"].crop(-1)
                else:
                    past_key_values = []
                    for layer in model_kwargs["past_key_values"]:
                        layer_past_key_values = []
                        for item in layer: layer_past_key_values.append(item[..., :-1, :])
                        past_key_values.append(tuple(layer_past_key_values))
                    model_kwargs["past_key_values"] = tuple(past_key_values)
            if self.config.is_encoder_decoder: return GenerateEncoderDecoderOutput(sequences=input_ids, scores=scores, logits=raw_logits, encoder_attentions=encoder_attentions,
            encoder_hidden_states=encoder_hidden_states, decoder_attentions=decoder_attentions, cross_attentions=cross_attentions, decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateDecoderOnlyOutput(sequences=input_ids, scores=scores, logits=raw_logits, attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return input_ids
    def _sample(self, input_ids: torch.LongTensor, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig, synced_gpus: bool, streamer: Optional["BaseStreamer"], **model_kwargs) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        pad_token_id = generation_config._pad_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        max_length = generation_config.max_length
        has_eos_stopping_criteria = any(hasattr(criteria, "eos_token_id") for criteria in stopping_criteria)
        do_sample = generation_config.do_sample
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        batch_size, cur_len = input_ids.shape
        this_peer_finished = False
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device, cur_len=cur_len, max_length=max_length):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
            outputs = self(**model_inputs, return_dict=True)
            if synced_gpus and this_peer_finished: continue
            next_token_logits = outputs.logits.clone()[:, -1, :].float()
            next_token_scores = logits_processor(input_ids, next_token_logits)
            if return_dict_in_generate:
                if output_scores: scores += (next_token_scores,)
                if output_logits: raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
            else: next_tokens = torch.argmax(next_token_scores, dim=-1)
            if has_eos_stopping_criteria: next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            if streamer is not None: streamer.put(next_tokens.cpu())
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
            cur_len += 1
            del outputs
        if streamer is not None: streamer.end()
        if return_dict_in_generate:
            if self.config.is_encoder_decoder: return GenerateEncoderDecoderOutput(sequences=input_ids, scores=scores, logits=raw_logits, encoder_attentions=encoder_attentions, encoder_hidden_states=encoder_hidden_states, decoder_attentions=decoder_attentions,
            cross_attentions=cross_attentions, decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateDecoderOnlyOutput(sequences=input_ids, scores=scores, logits=raw_logits, attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return input_ids
    def _temporary_reorder_cache(self, past_key_values, beam_idx):
        model_class = self.__class__.__name__.lower()
        if isinstance(past_key_values, (tuple, list)): past_key_values = self._reorder_cache(past_key_values, beam_idx)
        elif "gptbigcode" in model_class:
            if not isinstance(past_key_values, (DynamicCache, EncoderDecoderCache)): raise ValueError(f"Using an unsupported cache format with {model_class}. Currently, it only supports the legacy tuple format or `DynamicCache`")
            past_key_values = self._reorder_cache(past_key_values, beam_idx)
            past_key_values = DynamicCache.from_legacy_cache(past_key_values)
        else: past_key_values.reorder_cache(beam_idx)
        return past_key_values
    def _beam_search(self, input_ids: torch.LongTensor, beam_scorer: BeamScorer, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig, synced_gpus: bool, **model_kwargs) -> Union[GenerateBeamOutput, torch.LongTensor]:
        pad_token_id = generation_config._pad_token_tensor
        eos_token_id = generation_config._eos_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        sequential = generation_config.low_memory
        do_sample = generation_config.do_sample
        batch_size = len(beam_scorer._beam_hyps)
        num_beams = beam_scorer.num_beams
        batch_beam_size, cur_len = input_ids.shape
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        if num_beams * batch_size != batch_beam_size: raise ValueError(f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but is {batch_beam_size}.")
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        beam_indices = (tuple(() for _ in range(batch_beam_size)) if (return_dict_in_generate and output_scores) else None)
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        beam_scores = torch.zeros((batch_size, num_beams), dtype=torch.float, device=input_ids.device)
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        this_peer_finished = False
        decoder_prompt_len = input_ids.shape[-1]
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
            if sequential:
                if any(model_name in self.__class__.__name__.lower() for model_name in ["fsmt", "reformer", "ctrl", "gpt_bigcode", "transo_xl", "sapiens_code", "xlnet", "cpm", "jamba"]): raise RuntimeError(f"Currently generation for {self.__class__.__name__} is not supported for `low_memory beam_search`. Please open an issue on GitHub if you need this feature.")
                inputs_per_sub_batches = _split_model_inputs(model_inputs, split_size=batch_size, full_batch_size=batch_beam_size, config=self.config.get_text_config())
                outputs_per_sub_batch = [self(**inputs_per_sub_batch, return_dict=True) for inputs_per_sub_batch in inputs_per_sub_batches]
                outputs = stack_model_outputs(outputs_per_sub_batch, self.config.get_text_config())
            else: outputs = self(**model_inputs, return_dict=True)
            if synced_gpus and this_peer_finished:
                cur_len = cur_len + 1
                continue
            next_token_logits = outputs.logits[:, -1, :].clone().float()
            next_token_scores = nn.functional.log_softmax(next_token_logits, dim=-1)
            next_token_scores_processed = logits_processor(input_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(next_token_scores_processed)
            if return_dict_in_generate:
                if output_scores: scores += (next_token_scores_processed,)
                if output_logits: raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)
            n_eos_tokens = eos_token_id.shape[0] if eos_token_id is not None else 0
            n_tokens_to_keep = max(2, 1 + n_eos_tokens) * num_beams
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=n_tokens_to_keep)
                next_token_scores = torch.gather(next_token_scores, -1, next_tokens)
                next_token_scores, _indices = torch.sort(next_token_scores, descending=True, dim=1)
                next_tokens = torch.gather(next_tokens, -1, _indices)
            else: next_token_scores, next_tokens = torch.topk(next_token_scores, n_tokens_to_keep, dim=1, largest=True, sorted=True)
            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size
            beam_outputs = beam_scorer.process(input_ids, next_token_scores, next_tokens, next_indices, pad_token_id=pad_token_id, eos_token_id=eos_token_id, beam_indices=beam_indices, decoder_prompt_len=decoder_prompt_len)
            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]
            input_ids = torch.cat([input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            del outputs
            if model_kwargs.get("past_key_values", None) is not None: model_kwargs["past_key_values"] = self._temporary_reorder_cache(model_kwargs["past_key_values"], beam_idx)
            if return_dict_in_generate and output_scores: beam_indices = tuple((beam_indices[beam_idx[i]] + (beam_idx[i],) for i in range(len(beam_indices))))
            cur_len = cur_len + 1
            if beam_scorer.is_done or all(stopping_criteria(input_ids, scores)): this_peer_finished = True
        sequence_outputs = beam_scorer.finalize(input_ids, beam_scores, next_tokens, next_indices, pad_token_id=pad_token_id, eos_token_id=eos_token_id, max_length=stopping_criteria.max_length, beam_indices=beam_indices, decoder_prompt_len=decoder_prompt_len)
        if return_dict_in_generate:
            if not output_scores: sequence_outputs["sequence_scores"] = None
            if self.config.is_encoder_decoder: return GenerateBeamEncoderDecoderOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"], scores=scores, logits=raw_logits,
            beam_indices=sequence_outputs["beam_indices"], encoder_attentions=encoder_attentions, encoder_hidden_states=encoder_hidden_states, decoder_attentions=decoder_attentions, cross_attentions=cross_attentions,
            decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateBeamDecoderOnlyOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"], scores=scores, logits=raw_logits, beam_indices=sequence_outputs["beam_indices"],
            attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return sequence_outputs["sequences"]
    def _group_beam_search(self, input_ids: torch.LongTensor, beam_scorer: BeamScorer, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig, synced_gpus: bool, **model_kwargs):
        pad_token_id = generation_config._pad_token_tensor
        eos_token_id = generation_config._eos_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        num_beams = beam_scorer.num_beams
        num_beam_groups = beam_scorer.num_beam_groups
        num_sub_beams = num_beams // num_beam_groups
        batch_size = len(beam_scorer._beam_hyps) // num_beam_groups
        device = input_ids.device
        batch_beam_size, cur_len = input_ids.shape
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        if return_dict_in_generate and output_scores: beam_indices = [tuple(() for _ in range(num_sub_beams * batch_size)) for _ in range(num_beam_groups)]
        else: beam_indices = None
        if num_beams * batch_size != batch_beam_size: raise ValueError(f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but is {batch_beam_size}.")
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        beam_scores = torch.full((batch_size, num_beams), -1e9, dtype=torch.float, device=device)
        beam_scores[:, ::num_sub_beams] = 0
        beam_scores = beam_scores.view((batch_size * num_beams,))
        this_peer_finished = False
        decoder_prompt_len = input_ids.shape[-1]
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            current_tokens = torch.zeros(batch_size * num_beams, dtype=input_ids.dtype, device=device)
            reordering_indices = torch.zeros(batch_size * num_beams, dtype=torch.long, device=device)
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
            outputs = self(**model_inputs, return_dict=True)
            if synced_gpus and this_peer_finished:
                cur_len = cur_len + 1
                continue
            if output_scores: processed_score = torch.zeros_like(outputs.logits[:, -1, :])
            if output_logits: raw_logit_score = outputs.logits[:, -1, :].clone()
            for beam_group_idx in range(num_beam_groups):
                group_start_idx = beam_group_idx * num_sub_beams
                group_end_idx = min(group_start_idx + num_sub_beams, num_beams)
                group_size = group_end_idx - group_start_idx
                batch_group_indices = []
                for batch_idx in range(batch_size): batch_group_indices.extend([batch_idx * num_beams + idx for idx in range(group_start_idx, group_end_idx)])
                group_input_ids = input_ids[batch_group_indices]
                next_token_logits = outputs.logits[batch_group_indices, -1, :].float()
                next_token_scores = nn.functional.log_softmax(next_token_logits, dim=-1)
                vocab_size = next_token_scores.shape[-1]
                next_token_scores_processed = logits_processor(group_input_ids, next_token_scores, current_tokens=current_tokens, beam_group_idx=beam_group_idx)
                next_token_scores = next_token_scores_processed + beam_scores[batch_group_indices].unsqueeze(-1)
                next_token_scores = next_token_scores.expand_as(next_token_scores_processed)
                if output_scores: processed_score[batch_group_indices] = next_token_scores_processed
                next_token_scores = next_token_scores.view(batch_size, group_size * vocab_size)
                n_eos_tokens = eos_token_id.shape[0] if eos_token_id is not None else 0
                next_token_scores, next_tokens = torch.topk(next_token_scores, max(2, 1 + n_eos_tokens) * group_size, dim=1, largest=True, sorted=True)
                next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
                next_tokens = next_tokens % vocab_size
                process_beam_indices = sum(beam_indices, ()) if beam_indices is not None else None
                beam_outputs = beam_scorer.process(group_input_ids, next_token_scores, next_tokens, next_indices, pad_token_id=pad_token_id, eos_token_id=eos_token_id,
                beam_indices=process_beam_indices, group_index=beam_group_idx, decoder_prompt_len=decoder_prompt_len)
                beam_scores[batch_group_indices] = beam_outputs["next_beam_scores"]
                beam_next_tokens = beam_outputs["next_beam_tokens"]
                beam_idx = beam_outputs["next_beam_indices"]
                if return_dict_in_generate and output_scores: beam_indices[beam_group_idx] = tuple(beam_indices[beam_group_idx][beam_idx[i]] + (beam_idx[i],) for i in range(len(beam_indices[0])))
                input_ids[batch_group_indices] = group_input_ids[beam_idx]
                group_input_ids = torch.cat([group_input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1)
                current_tokens[batch_group_indices] = group_input_ids[:, -1]
                reordering_indices[batch_group_indices] = (num_beams * torch.div(beam_idx, group_size, rounding_mode="floor") + group_start_idx + (beam_idx % group_size))
            if return_dict_in_generate:
                if output_scores: scores += (processed_score,)
                if output_logits: raw_logits += (raw_logit_score,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            input_ids = torch.cat([input_ids, current_tokens.unsqueeze(-1)], dim=-1)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            del outputs
            if model_kwargs.get("past_key_values", None) is not None: model_kwargs["past_key_values"] = self._temporary_reorder_cache(model_kwargs["past_key_values"], reordering_indices)
            cur_len = cur_len + 1
            if beam_scorer.is_done or all(stopping_criteria(input_ids, scores)): this_peer_finished = True
        final_beam_indices = sum(beam_indices, ()) if beam_indices is not None else None
        sequence_outputs = beam_scorer.finalize(input_ids, beam_scores, next_tokens, next_indices, pad_token_id=pad_token_id, eos_token_id=eos_token_id, max_length=stopping_criteria.max_length, beam_indices=final_beam_indices, decoder_prompt_len=decoder_prompt_len)
        if return_dict_in_generate:
            if not output_scores: sequence_outputs["sequence_scores"] = None
            if self.config.is_encoder_decoder: return GenerateBeamEncoderDecoderOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"], scores=scores, logits=raw_logits, beam_indices=sequence_outputs["beam_indices"],
            encoder_attentions=encoder_attentions, encoder_hidden_states=encoder_hidden_states, decoder_attentions=decoder_attentions, cross_attentions=cross_attentions, decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateBeamDecoderOnlyOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"], scores=scores, logits=raw_logits, beam_indices=sequence_outputs["beam_indices"], attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return sequence_outputs["sequences"]
    def _constrained_beam_search(self, input_ids: torch.LongTensor, constrained_beam_scorer: ConstrainedBeamSearchScorer, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList, generation_config: GenerationConfig, synced_gpus: bool, **model_kwargs) -> Union[GenerateBeamOutput, torch.LongTensor]:
        pad_token_id = generation_config._pad_token_tensor
        eos_token_id = generation_config._eos_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        batch_size = len(constrained_beam_scorer._beam_hyps)
        num_beams = constrained_beam_scorer.num_beams
        batch_beam_size, cur_len = input_ids.shape
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        if num_beams * batch_size != batch_beam_size: raise ValueError(f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but is {batch_beam_size}.")
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        beam_indices = (tuple(() for _ in range(batch_beam_size)) if (return_dict_in_generate and output_scores) else None)
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        beam_scores = torch.zeros((batch_size, num_beams), dtype=torch.float, device=input_ids.device)
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        this_peer_finished = False
        decoder_prompt_len = input_ids.shape[-1]
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
            outputs = self(**model_inputs, return_dict=True)
            if synced_gpus and this_peer_finished:
                cur_len = cur_len + 1
                continue
            next_token_logits = outputs.logits[:, -1, :].clone().float()
            next_token_scores = nn.functional.log_softmax(next_token_logits, dim=-1)
            next_token_scores_processed = logits_processor(input_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(next_token_scores_processed)
            scores_for_all_vocab = next_token_scores.clone()
            if return_dict_in_generate:
                if output_scores: scores += (next_token_scores,)
                if output_logits: raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += ((outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,))
                    if self.config.is_encoder_decoder: cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states: decoder_hidden_states += ((outputs.decoder_hidden_states,) if self.config.is_encoder_decoder else (outputs.hidden_states,))
            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)
            n_eos_tokens = eos_token_id.shape[0] if eos_token_id is not None else 0
            next_token_scores, next_tokens = torch.topk(next_token_scores, max(2, 1 + n_eos_tokens) * num_beams, dim=1, largest=True, sorted=True)
            next_indices = (next_tokens / vocab_size).long()
            next_tokens = next_tokens % vocab_size
            beam_outputs = constrained_beam_scorer.process(input_ids, next_token_scores, next_tokens, next_indices, scores_for_all_vocab, pad_token_id=pad_token_id,
            eos_token_id=eos_token_id, beam_indices=beam_indices, decoder_prompt_len=decoder_prompt_len)
            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]
            input_ids = torch.cat([input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder)
            del outputs
            if model_kwargs.get("past_key_values", None) is not None: model_kwargs["past_key_values"] = self._temporary_reorder_cache(model_kwargs["past_key_values"], beam_idx)
            if return_dict_in_generate and output_scores: beam_indices = tuple((beam_indices[beam_idx[i]] + (beam_idx[i],) for i in range(len(beam_indices))))
            cur_len = cur_len + 1
            if constrained_beam_scorer.is_done or all(stopping_criteria(input_ids, scores)): this_peer_finished = True
        sequence_outputs = constrained_beam_scorer.finalize(input_ids, beam_scores, next_tokens, next_indices, pad_token_id=pad_token_id, eos_token_id=eos_token_id,
        max_length=stopping_criteria.max_length, beam_indices=beam_indices, decoder_prompt_len=decoder_prompt_len)
        if return_dict_in_generate:
            if not output_scores: sequence_outputs["sequence_scores"] = None
            if self.config.is_encoder_decoder: return GenerateBeamEncoderDecoderOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"],
            scores=scores, logits=raw_logits, beam_indices=sequence_outputs["beam_indices"], encoder_attentions=encoder_attentions, encoder_hidden_states=encoder_hidden_states,
            decoder_attentions=decoder_attentions, cross_attentions=cross_attentions, decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateBeamDecoderOnlyOutput(sequences=sequence_outputs["sequences"], sequences_scores=sequence_outputs["sequence_scores"], scores=scores, logits=raw_logits,
            beam_indices=sequence_outputs["beam_indices"], attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return sequence_outputs["sequences"]
    def _assisted_decoding(self, input_ids: torch.LongTensor, candidate_generator: CandidateGenerator, logits_processor: LogitsProcessorList, stopping_criteria: StoppingCriteriaList,
    generation_config: GenerationConfig, synced_gpus: bool, streamer: Optional["BaseStreamer"], **model_kwargs) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        do_sample = generation_config.do_sample
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None)
        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(input_ids, model_kwargs)
        start_from_empty_dynamic_cache = False
        past_key_values = model_kwargs.get("past_key_values", None)
        if isinstance(past_key_values, DynamicCache) or (isinstance(past_key_values, EncoderDecoderCache) and isinstance(past_key_values.self_attention_cache, DynamicCache)):
            if past_key_values.get_seq_length() == 0: start_from_empty_dynamic_cache = True
        this_peer_finished = False
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            cur_len = input_ids.shape[-1]
            candidate_input_ids, candidate_logits = candidate_generator.get_candidates(input_ids)
            candidate_input_ids = candidate_input_ids.to(self.device)
            if candidate_logits is not None: candidate_logits = candidate_logits.to(self.device)
            candidate_length = candidate_input_ids.shape[1] - input_ids.shape[1]
            is_done_candidate = stopping_criteria(candidate_input_ids, None)
            candidate_kwargs = copy.copy(model_kwargs)
            candidate_kwargs = _prepare_attention_mask(candidate_kwargs, candidate_input_ids.shape[1], self.config.is_encoder_decoder)
            candidate_kwargs = _prepare_token_type_ids(candidate_kwargs, candidate_input_ids.shape[1])
            if "cache_position" in candidate_kwargs: candidate_kwargs["cache_position"] = torch.cat((candidate_kwargs["cache_position"], torch.arange(cur_len, cur_len + candidate_length, device=input_ids.device, dtype=torch.long)), dim=0)
            model_inputs = self.prepare_inputs_for_generation(candidate_input_ids, **candidate_kwargs)
            if "num_logits_to_keep" in model_inputs: model_inputs["num_logits_to_keep"] = candidate_length + 1
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
            outputs = self(**model_inputs)
            new_logits = outputs.logits[:, -candidate_length - 1 :].float()
            next_token_logits = new_logits.clone()
            if len(logits_processor) > 0:
                for i in range(candidate_length + 1): new_logits[:, i, :] = logits_processor(candidate_input_ids[:, : cur_len + i], new_logits[:, i, :])
            if do_sample and candidate_logits is not None: valid_tokens, n_matches = _speculative_sampling(candidate_input_ids, candidate_logits, candidate_length, new_logits, is_done_candidate)
            else:
                if do_sample:
                    probs = new_logits.softmax(dim=-1)
                    selected_tokens = torch.multinomial(probs[0, :, :], num_samples=1).squeeze(1)[None, :]
                else: selected_tokens = new_logits.argmax(dim=-1)
                candidate_new_tokens = candidate_input_ids[:, cur_len:]
                n_matches = ((~(candidate_new_tokens == selected_tokens[:, :-1])).cumsum(dim=-1) < 1).sum()
                if is_done_candidate and n_matches == candidate_length: n_matches -= 1
                valid_tokens = selected_tokens[:, : n_matches + 1]
            input_ids = torch.cat((input_ids, valid_tokens), dim=-1)
            if streamer is not None: streamer.put(valid_tokens.cpu())
            new_cur_len = input_ids.shape[-1]
            new_cache_size = new_cur_len - 1
            outputs.past_key_values = _crop_past_key_values(self, outputs.past_key_values, new_cache_size)
            candidate_generator.update_candidate_strategy(input_ids, new_logits, n_matches)
            if synced_gpus and this_peer_finished: continue
            if return_dict_in_generate:
                if output_scores: scores += tuple(new_logits[:, i, :] for i in range(n_matches + 1))
                if output_logits: raw_logits += (next_token_logits,)
                if "past_key_values" not in model_kwargs or start_from_empty_dynamic_cache:
                    added_len = new_cur_len
                    start_from_empty_dynamic_cache = False
                else: added_len = n_matches + 1
                if output_attentions:
                    if self.config.is_encoder_decoder:
                        cross_attentions = _split_model_outputs(cross_attentions, outputs.cross_attentions, cur_len, added_len)
                        decoder_attentions = _split_model_outputs(decoder_attentions, outputs.decoder_attentions, cur_len, added_len, is_decoder_attention=True)
                    else: decoder_attentions = _split_model_outputs(decoder_attentions, outputs.attentions, cur_len, added_len, is_decoder_attention=True)
                if output_hidden_states:
                    if self.config.is_encoder_decoder: decoder_hidden_states = _split_model_outputs(decoder_hidden_states, outputs.decoder_hidden_states, cur_len, added_len)
                    else: decoder_hidden_states = _split_model_outputs(decoder_hidden_states, outputs.hidden_states, cur_len, added_len)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder, num_new_tokens=n_matches + 1)
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
        if streamer is not None: streamer.end()
        if (hasattr(candidate_generator, "assistant_model") and candidate_generator.assistant_model.generation_config.num_assistant_tokens_schedule == "heuristic"): candidate_generator.assistant_model.generation_config.num_assistant_tokens = (candidate_generator.num_assistant_tokens)
        if return_dict_in_generate:
            if self.config.is_encoder_decoder: return GenerateEncoderDecoderOutput(sequences=input_ids, scores=scores, logits=raw_logits, encoder_attentions=encoder_attentions, encoder_hidden_states=encoder_hidden_states,
            decoder_attentions=decoder_attentions, cross_attentions=cross_attentions, decoder_hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
            else: return GenerateDecoderOnlyOutput(sequences=input_ids, scores=scores, logits=raw_logits, attentions=decoder_attentions, hidden_states=decoder_hidden_states, past_key_values=model_kwargs.get("past_key_values"))
        else: return input_ids
def _speculative_sampling(candidate_input_ids, candidate_logits, candidate_length, new_logits, is_done_candidate):
    new_candidate_input_ids = candidate_input_ids[:, -candidate_length:]
    q = candidate_logits.softmax(dim=-1)
    q_i = q[:, torch.arange(candidate_length), new_candidate_input_ids].squeeze(0, 1)
    p = new_logits.softmax(dim=-1)
    p_i = p[:, torch.arange(candidate_length), new_candidate_input_ids].squeeze(0, 1)
    probability_ratio = p_i / q_i
    r_i = torch.rand_like(probability_ratio)
    is_accepted = r_i <= probability_ratio
    n_matches = ((~is_accepted).cumsum(dim=-1) < 1).sum()
    if is_done_candidate and n_matches == candidate_length:
        n_matches -= 1
        valid_tokens = new_candidate_input_ids[:, : n_matches + 1]
    else:
        gamma = candidate_logits.shape[1]
        p_n_plus_1 = p[:, n_matches, :]
        if n_matches < gamma:
            q_n_plus_1 = q[:, n_matches, :]
            p_prime = torch.clamp((p_n_plus_1 - q_n_plus_1), min=0)
            p_prime.div_(p_prime.sum())
        else: p_prime = p_n_plus_1
        t = torch.multinomial(p_prime, num_samples=1).squeeze(1)[None, :]
        if n_matches > 0: valid_tokens = torch.cat((new_candidate_input_ids[:, :n_matches], t), dim=-1)
        else: valid_tokens = t
    return valid_tokens, n_matches
def _split_model_outputs(outputs, new_outputs, cur_len, added_len, is_decoder_attention=False):
    if len(outputs) == 0:
        new_tuple = ()
        for layer in new_outputs:
            last_dim_size = cur_len if is_decoder_attention else layer.shape[-1]
            new_tuple += (layer[..., :cur_len, :last_dim_size],)
        outputs += (new_tuple,)
        cur_len += 1
        added_len -= cur_len
    for i in range(added_len):
        new_tuple = ()
        for layer in new_outputs:
            last_dim_size = cur_len + i if is_decoder_attention else layer.shape[-1]
            new_tuple += (layer[..., i : i + 1, :last_dim_size],)
        outputs += (new_tuple,)
    return outputs
def _ranking_fast(context_hidden: torch.FloatTensor, next_hidden: torch.FloatTensor, next_top_k_probs: torch.FloatTensor, cosine_matrix_mask: torch.LongTensor, alpha: float, beam_width: int) -> torch.FloatTensor:
    norm_context_hidden = context_hidden / context_hidden.norm(dim=2, keepdim=True)
    norm_next_hidden = next_hidden / next_hidden.norm(dim=2, keepdim=True)
    cosine_matrix = torch.matmul(norm_context_hidden, norm_next_hidden.transpose(1, 2)).squeeze(-1)
    cosine_matrix_mask = cosine_matrix_mask.to(dtype=cosine_matrix.dtype)
    cosine_matrix_mask = (1 - cosine_matrix_mask) * torch.finfo(cosine_matrix.dtype).min
    cosine_matrix = cosine_matrix + cosine_matrix_mask
    degeneration_penalty, _ = torch.max(cosine_matrix, dim=-1)
    next_top_k_probs = next_top_k_probs.view(-1)
    contrastive_score = (1.0 - alpha) * next_top_k_probs - alpha * degeneration_penalty
    contrastive_score = torch.stack(torch.split(contrastive_score, beam_width))
    _, selected_idx = contrastive_score.max(dim=-1)
    return selected_idx
def _split(data, full_batch_size: int, num_hidden_layers: int, split_size: int = None):
    if data is None: return [None] * (full_batch_size // split_size)
    if isinstance(data, torch.Tensor): return [data[i : i + split_size] for i in range(0, full_batch_size, split_size)]
    elif isinstance(data, DynamicCache) or (isinstance(data, EncoderDecoderCache) and isinstance(data.self_attention_cache, DynamicCache)): return data.batch_split(full_batch_size, split_size, num_hidden_layers)
    elif isinstance(data, tuple):
        if isinstance(data[0], tuple): return [tuple(tuple(tensor[i : i + split_size] for tensor in inner_tuple) for inner_tuple in data) for i in range(0, full_batch_size, split_size)]
        else: return [tuple(sub_tensor[i : i + split_size] for sub_tensor in data) for i in range(0, full_batch_size, split_size)]
    else: raise TypeError(f"Unexpected attribute type: {type(data)}")
def _split_model_inputs(model_input: Union[ModelOutput, Dict], split_size: int, full_batch_size: int, config: PretrainedConfig) -> List[Union[ModelOutput, Dict]]:
    """Args:"""
    if model_input is None: return [model_input] * (full_batch_size // split_size)
    model_output_cls = type(model_input)
    if (full_batch_size % split_size) != 0: raise ValueError("`full_batch_size` must be divisible by `split_size`")
    if split_size > full_batch_size: raise ValueError("`split_size` must be smaller or equal to `full_batch_size`")
    keys = (model_input.__dataclass_fields__.keys() if hasattr(model_input, "__dataclass_fields__") else model_input.keys())
    keys = [k for k in keys if k in model_input]
    bool_keys = [k for k in keys if isinstance(model_input[k], bool) or k == "cache_position"]
    keys_to_ignore = ["cache_position", "encoder_outputs", "num_logits_to_keep"]
    non_bool_keys = [k for k in keys if not isinstance(model_input[k], bool) and k not in keys_to_ignore]
    num_hidden_layers = config.get_text_config().num_hidden_layers
    data_split_list = [{k: _split(model_input[k], full_batch_size, num_hidden_layers, split_size)[i] for k in non_bool_keys} for i in range(full_batch_size // split_size)]
    bool_data = {k: model_input[k] for k in bool_keys}
    if "encoder_outputs" in model_input:
        encoder_outputs_split = _split_model_inputs(model_input["encoder_outputs"], split_size, full_batch_size, config.get_text_config())
        data_split_list = [{**data_split, "encoder_outputs": encoder_outputs_split[i]} for i, data_split in enumerate(data_split_list)]
    if "num_logits_to_keep" in model_input: data_split_list = [{**data_split, "num_logits_to_keep": model_input["num_logits_to_keep"]} for data_split in data_split_list]
    split_model_inputs: List[Union[ModelOutput, Dict]] = [model_output_cls(**data_split, **bool_data) for data_split in data_split_list]
    return split_model_inputs
def stack_model_outputs(model_outputs: List[ModelOutput], config: PretrainedConfig) -> ModelOutput:
    """Args:"""
    if not model_outputs: raise ValueError("Input list is empty.")
    model_output_cls = type(model_outputs[0])
    num_hidden_layers = config.get_text_config().num_hidden_layers
    if not all(isinstance(obj, model_output_cls) for obj in model_outputs): raise ValueError("All elements in the list should be of the same type.")
    def _concat(data):
        if any(data is None for data in data): return None
        if isinstance(data[0], torch.Tensor): return torch.cat(data, dim=0)
        elif isinstance(data[0], DynamicCache): return DynamicCache.from_batch_splits(data, num_hidden_layers=num_hidden_layers)
        elif isinstance(data[0], EncoderDecoderCache): return EncoderDecoderCache.from_batch_splits(data, num_hidden_layers=num_hidden_layers)
        elif isinstance(data[0], tuple):
            if isinstance(data[0][0], tuple): return tuple(tuple(torch.cat([attr[i][j] for attr in data], dim=0) for j in range(len(data[0][0]))) for i in range(len(data[0])))
            else: return tuple(torch.cat([attr[i] for attr in data], dim=0) for i in range(len(data[0])))
        elif isinstance(data[0], (int, float)): return torch.tensor(data)
        else: raise TypeError(f"Unexpected attribute type: {type(data[0])}")
    concatenated_data = {k: _concat([getattr(model_output, k) for model_output in model_outputs]) for k in model_output_cls.__dataclass_fields__.keys()}
    return model_output_cls(**concatenated_data)
def _relative_top_filter(scores: torch.FloatTensor, baseline_scores: torch.FloatTensor, relative_top: float = 0.1, filter_value: float = -float("Inf"), base_filter_value=-1e-3, min_tokens_to_keep: int = 1) -> torch.FloatTensor:
    scores_normalized = scores.log_softmax(dim=-1)
    baseline_scores_normalized = baseline_scores.log_softmax(dim=-1)
    sorted_logits, sorted_indices = torch.sort(scores_normalized, descending=True)
    min_thresh = sorted_logits[..., min_tokens_to_keep - 1]
    probs_max = torch.max(scores_normalized, dim=-1).values
    probs_thresh = probs_max + np.log(relative_top)
    probs_thresh = torch.min(min_thresh, probs_thresh)
    probs_thresh = probs_thresh.unsqueeze(-1)
    baseline_scores_normalized[scores_normalized < probs_thresh] = base_filter_value
    scores_normalized[scores_normalized < probs_thresh] = filter_value
    return scores_normalized, baseline_scores_normalized
def _dola_select_contrast(candidate_premature_layers: List[int], candidate_premature_logits: Dict[int, torch.FloatTensor], final_logits: torch.FloatTensor) -> torch.FloatTensor:
    if len(candidate_premature_layers) == 1:
        base_logits = candidate_premature_logits[candidate_premature_layers[0]]
        final_logits, base_logits = _relative_top_filter(final_logits, base_logits)
        logits = final_logits - base_logits
        return logits
    stacked_premature_layers = torch.stack([candidate_premature_logits[i] for i in candidate_premature_layers], dim=0)
    softmax_mature_layer = F.softmax(final_logits, dim=-1)
    softmax_premature_layers = F.softmax(stacked_premature_layers, dim=-1)
    avg_dist = 0.5 * (softmax_mature_layer[None, :, :] + softmax_premature_layers)
    log_softmax_mature_layer = F.log_softmax(final_logits, dim=-1)
    log_softmax_premature_layers = F.log_softmax(stacked_premature_layers, dim=-1)
    kl1 = F.kl_div(log_softmax_mature_layer[None, :, :], avg_dist, reduction="none").mean(-1)
    kl2 = F.kl_div(log_softmax_premature_layers, avg_dist, reduction="none").mean(-1)
    js_divs = 0.5 * (kl1 + kl2)
    js_divs = js_divs.mean(-1)
    premature_layer = candidate_premature_layers[int(js_divs.argmax().cpu().item())]
    base_logits = candidate_premature_logits[premature_layer]
    final_logits, base_logits = _relative_top_filter(final_logits, base_logits)
    logits = final_logits - base_logits
    return logits
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
