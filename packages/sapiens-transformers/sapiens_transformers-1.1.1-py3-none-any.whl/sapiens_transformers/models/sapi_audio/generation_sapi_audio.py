"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...generation.logits_process import (LogitsProcessorList, SuppressTokensAtBeginLogitsProcessor, SuppressTokensLogitsProcessor, SAPIAudioNoSpeechDetection, SAPIAudioTimeStampLogitsProcessor)
from typing import Callable, Iterator, List, Optional, Tuple, Union
from ...generation.stopping_criteria import StoppingCriteriaList
from .tokenization_sapi_audio import TASK_IDS, TO_LANGUAGE_CODE
from ...generation import GenerationConfig, GenerationMixin
from sapiens_transformers.cache_utils import EncoderDecoderCache
import numpy as sapiens_technology_numbers
from ...modeling_outputs import BaseModelOutput
import torch.nn.functional as Functional
import torch as sapiens_technology_torch
import copy as sapiens_technology_copy
def _get_attr_from_logit_processors(logits_processor, logit_processor_class, attribute_name):
    if logits_processor is not None:
        logit_processor = next((cls for cls in logits_processor if isinstance(cls, logit_processor_class)), None)
        if logit_processor: return getattr(logit_processor, attribute_name, None)
    return None
def _pad_to_max_length(current_segments, pad_token_id, device, padding_side="right", padding="longest", bos_token_tensor=None, cut_off_length=None):
    max_total_length, sequences = 0, []
    if padding_side not in ["right", "left"]: raise ValueError(f"`padding_side` must be either 'right' or 'left', not {padding_side}")
    if padding not in ["longest", "max_length"]: raise ValueError(f"`padding` must be either 'longest' or 'max_length', not {padding}")
    elif padding == "max_length" and cut_off_length is None: raise ValueError("`cut_off_length` must be specified when `padding='max_length'`")
    for current_segment_list in current_segments:
        if current_segment_list is not None and len([d["tokens"] for d in current_segment_list]) > 0:
            sequence = sapiens_technology_torch.cat([d["tokens"] for d in current_segment_list], dim=-1)
            if cut_off_length is not None: sequence = sequence[-cut_off_length:]
            if bos_token_tensor is not None: sequence = sapiens_technology_torch.cat([bos_token_tensor, sequence])
            sequences.append(sequence)
            max_total_length = max(max_total_length, len(sequences[-1]))
        elif bos_token_tensor is not None: sequences.append(bos_token_tensor)
        else: sequences.append(sapiens_technology_torch.tensor([], device=device))
    max_total_length = cut_off_length + 1 if padding == "max_length" else max_total_length
    for i in range(len(current_segments)):
        pad_length = max_total_length - len(sequences[i])
        sequences[i] = Functional.pad(sequences[i], pad=(0, pad_length) if padding_side == "right" else (pad_length, 0), value=pad_token_id)
    return sapiens_technology_torch.stack(sequences, dim=0)
def _median_filter(inputs: sapiens_technology_torch.Tensor, filter_width: int) -> sapiens_technology_torch.Tensor:
    if filter_width <= 0 or filter_width % 2 != 1: raise ValueError("`filter_width` should be an odd number")
    pad_width = filter_width // 2
    if inputs.shape[-1] <= pad_width: return inputs
    return Functional.pad(inputs, (pad_width, pad_width, 0, 0), mode="reflect").unfold(-1, filter_width, 1).sort()[0][..., pad_width]
def _dynamic_time_warping(matrix: sapiens_technology_numbers.ndarray):
    output_length, input_length = matrix.shape
    cost = sapiens_technology_numbers.ones((output_length + 1, input_length + 1), dtype=sapiens_technology_numbers.float32) * sapiens_technology_numbers.inf
    trace, cost[0, 0] = -sapiens_technology_numbers.ones((output_length + 1, input_length + 1), dtype=sapiens_technology_numbers.float32), 0
    for j in range(1, input_length + 1):
        for i in range(1, output_length + 1):
            c0, c1, c2 = cost[i - 1, j - 1], cost[i - 1, j], cost[i, j - 1]
            if c0 < c1 and c0 < c2: c, t = c0, 0
            elif c1 < c0 and c1 < c2: c, t = c1, 1
            else: c, t = c2, 2
            cost[i, j], trace[i, j] = matrix[i - 1, j - 1] + c, t
    i, j = trace.shape[0] - 1, trace.shape[1] - 1
    trace[0, :], trace[:, 0], text_indices, time_indices = 2, 1, [], []
    while i > 0 or j > 0:
        text_indices.append(i - 1)
        time_indices.append(j - 1)
        if trace[i, j] == 0:
            i -= 1
            j -= 1
        elif trace[i, j] == 1: i -= 1
        elif trace[i, j] == 2: j -= 1
        else: raise RuntimeError(f"Internal error in dynamic time warping. Unexpected trace[{i}, {j}]. Please file a bug report.")
    return sapiens_technology_numbers.array(text_indices)[::-1], sapiens_technology_numbers.array(time_indices)[::-1]
class SAPIAudioGenerationMixin(GenerationMixin):
    def _extract_token_timestamps(self, generate_outputs, alignment_heads, time_precision=0.02, num_frames=None):
        cross_attentions = []
        for i in range(self.config.decoder_layers): cross_attentions.append(sapiens_technology_torch.cat([x[i] for x in generate_outputs.cross_attentions], dim=2))
        weights, weight_length = sapiens_technology_torch.stack([cross_attentions[l][:, h] for l, h in alignment_heads]).permute([1, 0, 2, 3]), None
        if "beam_indices" in generate_outputs:
            weight_length = (generate_outputs.beam_indices != -1).sum(-1).max()
            weights = weights[:, :, :weight_length]
            beam_indices = generate_outputs.beam_indices[:, :weight_length]
            beam_indices = beam_indices.masked_fill(beam_indices == -1, 0)
            weights = sapiens_technology_torch.stack([sapiens_technology_torch.index_select(weights[:, :, i, :], dim=0, index=beam_indices[:, i]) for i in range(beam_indices.shape[1])], dim=2)
        timestamps = sapiens_technology_torch.zeros_like(generate_outputs.sequences, dtype=sapiens_technology_torch.float32)[:, : (weight_length or cross_attentions[0].shape[2]) + 1]
        batch_size = timestamps.shape[0]
        if num_frames is not None:
            if isinstance(num_frames, int): weights = weights[..., : num_frames // 2]
            elif isinstance(num_frames, (list, tuple, sapiens_technology_numbers.ndarray)) and len(sapiens_technology_numbers.unique(num_frames)) == 1: weights = weights[..., : num_frames[0] // 2]
            elif isinstance(num_frames, (sapiens_technology_torch.Tensor)) and len(sapiens_technology_torch.unique(num_frames)) == 1: weights = weights[..., : num_frames[0] // 2]
            else: num_frames = sapiens_technology_numbers.repeat(num_frames, batch_size if isinstance(num_frames, int) else batch_size // len(num_frames))
        if num_frames is None or isinstance(num_frames, int):
            std, mean = sapiens_technology_torch.std(weights, dim=-2, keepdim=True, unbiased=False), sapiens_technology_torch.mean(weights, dim=-2, keepdim=True)
            weights = _median_filter((weights - mean) / std, self.config.median_filter_width).mean(dim=1)
        for batch_idx in range(batch_size):
            if num_frames is not None and isinstance(num_frames, (tuple, list, sapiens_technology_numbers.ndarray, sapiens_technology_torch.Tensor)):
                matrix = weights[batch_idx, ..., : num_frames[batch_idx] // 2]
                std, mean = sapiens_technology_torch.std(matrix, dim=-2, keepdim=True, unbiased=False), sapiens_technology_torch.mean(matrix, dim=-2, keepdim=True)
                matrix = _median_filter((matrix - mean) / std, self.config.median_filter_width).mean(dim=0)
            else: matrix = weights[batch_idx]
            text_indices, time_indices = _dynamic_time_warping(-matrix.cpu().double().numpy())
            timestamps[batch_idx, 1:] = sapiens_technology_torch.tensor(time_indices[sapiens_technology_numbers.pad(sapiens_technology_numbers.diff(text_indices), (1, 0), constant_values=1).astype(bool)] * time_precision)
        return timestamps
    def generate(self, input_features: Optional[sapiens_technology_torch.Tensor] = None, generation_config: Optional[GenerationConfig] = None, logits_processor: Optional[LogitsProcessorList] = None,
    stopping_criteria: Optional[StoppingCriteriaList] = None, prefix_allowed_tokens_fn: Optional[Callable[[int, sapiens_technology_torch.Tensor], List[int]]] = None, synced_gpus: bool = False,
    return_timestamps: Optional[bool] = None, task: Optional[str] = None, language: Optional[Union[str, List[str]]] = None, is_multilingual: Optional[bool] = None,
    prompt_ids: Optional[sapiens_technology_torch.Tensor] = None, prompt_condition_type: Optional[str] = None, condition_on_prev_tokens: Optional[bool] = None, temperature: Optional[Union[float, Tuple[float, ...]]] = None,
    compression_ratio_threshold: Optional[float] = None, logprob_threshold: Optional[float] = None, no_speech_threshold: Optional[float] = None, num_segment_frames: Optional[int] = None,
    attention_mask: Optional[sapiens_technology_torch.Tensor] = None, time_precision: float = 0.02, return_token_timestamps: Optional[bool] = None, return_segments: bool = False,
    return_dict_in_generate: Optional[bool] = None, **kwargs):
        if "inputs" in kwargs: input_features = kwargs.pop("inputs")
        generation_config, kwargs = self._prepare_generation_config(generation_config, **kwargs)
        input_stride = self.model.encoder.conv1.stride[0] * self.model.encoder.conv2.stride[0]
        num_segment_frames = input_stride * self.config.max_source_positions
        batch_size, total_input_frames = self._retrieve_total_input_frames(input_features=input_features, input_stride=input_stride, kwargs=kwargs)
        is_shortform = total_input_frames <= num_segment_frames
        return_dict_in_generate = self._set_return_outputs(return_dict_in_generate=return_dict_in_generate, return_token_timestamps=return_token_timestamps,
        logprob_threshold=logprob_threshold, generation_config=generation_config)
        timestamp_begin = self._set_return_timestamps(return_timestamps=return_timestamps, is_shortform=is_shortform, generation_config=generation_config)
        self._set_language_and_task(language=language, task=task, is_multilingual=is_multilingual, generation_config=generation_config)
        self._set_num_frames(return_token_timestamps=return_token_timestamps, generation_config=generation_config, kwargs=kwargs)
        self._set_thresholds_and_condition(generation_config=generation_config, logprob_threshold=logprob_threshold, compression_ratio_threshold=compression_ratio_threshold,
        no_speech_threshold=no_speech_threshold, condition_on_prev_tokens=condition_on_prev_tokens)
        self._set_prompt_condition_type(generation_config=generation_config, prompt_condition_type=prompt_condition_type)
        init_tokens = self._retrieve_init_tokens(input_features, batch_size=batch_size, generation_config=generation_config, config=self.config, num_segment_frames=num_segment_frames, kwargs=kwargs)
        self._check_decoder_input_ids(kwargs=kwargs)
        device = kwargs["encoder_outputs"][0].device if "encoder_outputs" in kwargs else input_features.device
        logits_processor = self._retrieve_logit_processors(generation_config=generation_config, logits_processor=logits_processor, begin_index=init_tokens.shape[1],
        num_beams=kwargs.get("num_beams", 1), device=device)
        self._set_condition_on_prev_tokens(condition_on_prev_tokens=condition_on_prev_tokens, generation_config=generation_config)
        temperatures = [temperature] if not isinstance(temperature, (list, tuple)) else temperature
        temperature = temperatures[0]
        max_frames, seek = self._retrieve_max_frames_and_seek(batch_size=batch_size, attention_mask=attention_mask, total_input_frames=total_input_frames, is_shortform=is_shortform)
        num_return_sequences = generation_config.num_return_sequences
        (batch_idx_map, cur_bsz, input_features, seek, max_frames, init_tokens, do_condition_on_prev_tokens) = self._expand_variables_for_generation(input_features=input_features,
        seek=seek, max_frames=max_frames, init_tokens=init_tokens, batch_size=batch_size, condition_on_prev_tokens=condition_on_prev_tokens, generation_config=generation_config)
        current_segments = self._prepare_segments(prompt_ids=prompt_ids, batch_size=cur_bsz, generation_config=generation_config)
        while (seek < max_frames).any():
            input_features, cur_bsz, batch_idx_map = self._maybe_reduce_batch(input_features=input_features, seek=seek, max_frames=max_frames, cur_bsz=cur_bsz, batch_idx_map=batch_idx_map)
            time_offset, seek_num_frames = seek * time_precision / input_stride, (max_frames - seek).clamp(max=num_segment_frames)
            segment_input = self._get_input_segment(input_features=input_features, seek=seek, seek_num_frames=seek_num_frames, num_segment_frames=num_segment_frames,
            cur_bsz=cur_bsz, batch_idx_map=batch_idx_map)
            suppress_tokens = _get_attr_from_logit_processors(logits_processor, SuppressTokensLogitsProcessor, "suppress_tokens")
            decoder_input_ids, kwargs = self._prepare_decoder_input_ids(cur_bsz=cur_bsz, init_tokens=init_tokens, current_segments=current_segments, batch_idx_map=batch_idx_map,
            do_condition_on_prev_tokens=do_condition_on_prev_tokens, prompt_ids=prompt_ids, generation_config=generation_config, config=self.config, device=init_tokens.device,
            suppress_tokens=suppress_tokens, kwargs=kwargs)
            self._set_max_new_tokens_and_length(config=self.config, decoder_input_ids=decoder_input_ids, generation_config=generation_config)
            if logits_processor is not None:
                for proc in logits_processor:
                    if hasattr(proc, "set_begin_index"): proc.set_begin_index(decoder_input_ids.shape[-1])
            (seek_sequences, seek_outputs, should_skip, do_condition_on_prev_tokens, model_output_type) = self.generate_with_fallback(segment_input=segment_input,
            decoder_input_ids=decoder_input_ids, cur_bsz=cur_bsz, batch_idx_map=batch_idx_map, seek=seek, num_segment_frames=num_segment_frames, max_frames=max_frames,
            temperatures=temperatures, generation_config=generation_config, logits_processor=logits_processor, stopping_criteria=stopping_criteria, prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
            synced_gpus=synced_gpus, return_token_timestamps=return_token_timestamps, do_condition_on_prev_tokens=do_condition_on_prev_tokens, is_shortform=is_shortform,
            batch_size=batch_size, attention_mask=attention_mask, kwargs=kwargs)
            for i, seek_sequence in enumerate(seek_sequences):
                prev_i = batch_idx_map[i]
                if should_skip[i]:
                    seek[prev_i] += seek_num_frames[prev_i]
                    continue
                segments, segment_offset = self._retrieve_segment(seek_sequence=seek_sequence, seek_outputs=seek_outputs, time_offset=time_offset, timestamp_begin=timestamp_begin,
                seek_num_frames=seek_num_frames, time_precision=time_precision, input_stride=input_stride, prev_idx=prev_i, idx=i, return_token_timestamps=return_token_timestamps)
                current_segments[prev_i] += segments
                if is_shortform: seek[prev_i] += max_frames[i]
                else: seek[prev_i] += segment_offset
        final_segments = ([x[1:] for x in current_segments] if (prompt_ids is not None and generation_config.prompt_condition_type == "first-segment") else current_segments)
        sequences = _pad_to_max_length(final_segments, generation_config.pad_token_id, device=self.device, padding_side="right")
        if return_segments: return {"sequences": sequences, "segments": final_segments}
        if is_shortform:
            if generation_config.max_new_tokens is None and generation_config.max_length is None: sequences = sapiens_technology_torch.cat([sequences, sapiens_technology_torch.full((sequences.shape[0], 1), generation_config.eos_token_id)], dim=-1)
            if return_token_timestamps:
                outputs = {}
                outputs["sequences"] = sequences
                outputs["token_timestamps"] = sapiens_technology_torch.stack([d["token_timestamps"] for d in seek_outputs], dim=0)
            else: outputs = sequences
            if return_dict_in_generate and generation_config.return_dict_in_generate:
                dict_outputs = self._stack_split_outputs(seek_outputs, model_output_type, sequences.device, kwargs)
                if num_return_sequences > 1:
                    if hasattr(dict_outputs, "encoder_attentions") and dict_outputs.encoder_attentions is not None: dict_outputs.encoder_attentions = tuple(dict_outputs.encoder_attentions[i][::num_return_sequences] for i in range(len(dict_outputs.encoder_attentions)))
                    if (hasattr(dict_outputs, "encoder_hidden_states") and dict_outputs.encoder_hidden_states is not None): dict_outputs.encoder_hidden_states = tuple(dict_outputs.encoder_hidden_states[i][::num_return_sequences] for i in range(len(dict_outputs.encoder_hidden_states)))
                if return_token_timestamps: dict_outputs["token_timestamps"] = outputs["token_timestamps"]
                return dict_outputs
            return outputs
        return sequences
    def generate_with_fallback(self, segment_input, decoder_input_ids, cur_bsz, batch_idx_map, seek, num_segment_frames, max_frames, temperatures, generation_config,
    logits_processor, stopping_criteria, prefix_allowed_tokens_fn, synced_gpus, return_token_timestamps, do_condition_on_prev_tokens, is_shortform, batch_size, attention_mask, kwargs):
        kwargs, seek_sequence_list, seek_outputs_list = sapiens_technology_copy.copy(kwargs), [None for _ in range(cur_bsz)], [None for _ in range(cur_bsz)]
        needs_fallback, should_skip, fallback_index_map = [False for _ in range(cur_bsz)], [False for _ in range(cur_bsz)], list(range(cur_bsz))
        if generation_config.no_speech_threshold is not None: self._setup_no_speech_detection(logits_processor, segment_input, decoder_input_ids, kwargs)
        for fallback_idx, temperature in enumerate(temperatures):
            generation_config.do_sample = temperature is not None and temperature > 0.0
            generation_config.temperature = temperature if generation_config.do_sample else 1.0
            if generation_config.do_sample: generation_config.num_beams = 1
            generate_kwargs = sapiens_technology_copy.copy(kwargs)
            for key in ["do_sample", "temperature", "num_beams"]:
                if key in generate_kwargs: del generate_kwargs[key]
            cur_bsz = decoder_input_ids.shape[0]
            if generation_config.cache_implementation == "static" and cur_bsz < batch_size:
                segment_input = Functional.pad(segment_input, (0, 0, 0, 0, 0, batch_size - cur_bsz), value=0)
                decoder_input_ids = Functional.pad(decoder_input_ids, (0, 0, 0, batch_size - cur_bsz), value=generation_config.pad_token_id)
                if generate_kwargs.get("decoder_attention_mask") is not None: generate_kwargs["decoder_attention_mask"] = Functional.pad(generate_kwargs["decoder_attention_mask"], (0, 0, 0, batch_size - cur_bsz), value=True)
                if generate_kwargs.get("encoder_outputs") is not None: generate_kwargs["encoder_outputs"] = Functional.pad(generate_kwargs["encoder_outputs"], (0, 0, 0, 0, 0, batch_size - cur_bsz), value=0)
            seek_outputs = super().generate(segment_input, generation_config=generation_config, logits_processor=logits_processor, stopping_criteria=stopping_criteria,
            prefix_allowed_tokens_fn=prefix_allowed_tokens_fn, synced_gpus=synced_gpus, decoder_input_ids=decoder_input_ids, attention_mask=attention_mask, **generate_kwargs)
            model_output_type = type(seek_outputs)
            seek_sequences, seek_outputs = self._postprocess_outputs(seek_outputs=seek_outputs, decoder_input_ids=decoder_input_ids, return_token_timestamps=return_token_timestamps,
            generation_config=generation_config, is_shortform=is_shortform)
            if cur_bsz < batch_size: seek_sequences, seek_outputs = seek_sequences[:cur_bsz], seek_outputs[:cur_bsz]
            new_fallback_index_map, new_segment_input, new_decoder_input_ids, new_decoder_attention_mask = [], [], [], []
            for i, seek_sequence in enumerate(seek_sequences):
                prev_i = batch_idx_map[fallback_index_map[i]]
                is_not_final = (seek[prev_i] + num_segment_frames) < max_frames[prev_i]
                if is_not_final and seek_sequence[-1] == generation_config.eos_token_id:
                    seek_sequence = seek_sequence[:-1]
                    if return_token_timestamps and not is_shortform: seek_outputs[i]["token_timestamps"] = seek_outputs[i]["token_timestamps"][:-1]
                if seek_sequence[-1] == generation_config.pad_token_id:
                    num_paddings = (seek_sequence == generation_config.pad_token_id).sum()
                    seek_sequence = seek_sequence[:-num_paddings]
                    if return_token_timestamps and not is_shortform: seek_outputs[i]["token_timestamps"] = seek_outputs[i]["token_timestamps"][:-num_paddings]
                needs_fallback[i], should_skip[i] = self._need_fallback(seek_sequence, seek_outputs, i, logits_processor, generation_config, self.config.vocab_size, temperature)
                seek_sequence_list[fallback_index_map[i]], seek_outputs_list[fallback_index_map[i]] = seek_sequence, seek_outputs[i]
                do_condition_on_prev_tokens[fallback_index_map[i]] = (generation_config.condition_on_prev_tokens and (temperature is None or temperature < 0.5))
                if needs_fallback[i]:
                    new_fallback_index_map.append(fallback_index_map[i])
                    new_segment_input.append(segment_input[i])
                    new_decoder_input_ids.append(decoder_input_ids[i])
                    if "decoder_attention_mask" in kwargs: new_decoder_attention_mask.append(kwargs["decoder_attention_mask"][i])
            fallback_index_map = new_fallback_index_map
            if len(fallback_index_map) == 0 or fallback_idx == len(temperatures) - 1:
                seek_sequences, seek_outputs = seek_sequence_list, seek_outputs_list
                break
            decoder_input_ids, segment_input = sapiens_technology_torch.stack(new_decoder_input_ids), sapiens_technology_torch.stack(new_segment_input)
            if "decoder_attention_mask" in kwargs: kwargs["decoder_attention_mask"] = sapiens_technology_torch.stack(new_decoder_attention_mask)
        return seek_sequences, seek_outputs, should_skip, do_condition_on_prev_tokens, model_output_type
    @staticmethod
    def _prepare_segments(prompt_ids, batch_size, generation_config):
        if prompt_ids is not None and generation_config.prompt_condition_type == "first-segment":
            prev_sot_token_id = getattr(generation_config, "prev_sot_token_id", None)
            prompt_ids = prompt_ids[1:] if prompt_ids[0] == prev_sot_token_id else prompt_ids
            current_segments = [[{"tokens": prompt_ids}] for _ in range(batch_size)]
        else: current_segments = [[] for _ in range(batch_size)]
        return current_segments
    def _postprocess_outputs(self, seek_outputs, decoder_input_ids, return_token_timestamps, generation_config, is_shortform):
        start_idx = decoder_input_ids.shape[-1] if not is_shortform else sapiens_technology_torch.tensor(0)
        if isinstance(seek_outputs, sapiens_technology_torch.Tensor):
            seek_outputs = seek_outputs[:, start_idx:]
            return seek_outputs, seek_outputs
        if return_token_timestamps and hasattr(generation_config, "alignment_heads"):
            num_frames = getattr(generation_config, "num_frames", None)
            seek_outputs["token_timestamps"] = self._extract_token_timestamps(seek_outputs, generation_config.alignment_heads, num_frames=num_frames)
            seek_outputs["token_timestamps"] = seek_outputs["token_timestamps"][:, start_idx:]
        seek_outputs["sequences"] = seek_outputs["sequences"][:, start_idx:]
        def split_by_batch_index(values, key, batch_idx, is_shortform, beam_indices=None):
            if beam_indices is not None and key == "scores": return [v[beam_idx].cpu() for (v, beam_idx) in zip(values, beam_indices[batch_idx][: len(values)])]
            if key in ["scores", "encoder_attentions", "encoder_hidden_states", "logits"]: return [v[batch_idx].cpu() for v in values]
            if key in ["decoder_attentions", "decoder_hidden_states", "cross_attentions"]: return tuple(tuple(w[batch_idx][None].cpu() for w in v) for v in values)
            elif key == "past_key_values":
                if not is_shortform: return None
                elif isinstance(values, EncoderDecoderCache):
                    all_past_key_values = []
                    for layer_idx in range(self.config.decoder_layers):
                        layer_past_key_values = []
                        for cache_cls in [values.self_attention_cache, values.cross_attention_cache]:
                            for v in [cache_cls.key_cache, cache_cls.value_cache]: layer_past_key_values.append(v[layer_idx][batch_idx][None].cpu())
                        all_past_key_values.append(tuple(layer_past_key_values))
                    return tuple(all_past_key_values)
                else:
                    all_past_key_values = []
                    for v in range(len(values)):
                        layer_past_key_values = []
                        for w in values[v]: layer_past_key_values.append(w[batch_idx][None].cpu())
                        all_past_key_values.append(tuple(layer_past_key_values))
                    return tuple(all_past_key_values)
            return values[batch_idx].cpu()
        sequence_tokens = seek_outputs["sequences"]
        seek_outputs = [{k: split_by_batch_index(v, k, i, is_shortform, beam_indices=seek_outputs.get("beam_indices")) for k, v in seek_outputs.items()} for i in range(sequence_tokens.shape[0])]
        return sequence_tokens, seek_outputs
    def _stack_split_outputs(self, seek_outputs, model_output_type, device, kwargs):
        outputs = {}
        for key in seek_outputs[0].keys():
            if key in ["sequences", "beam_indices"]: outputs[key] = sapiens_technology_torch.stack([v[key] for v in seek_outputs], dim=0).to(device)
            elif key in ["scores", "encoder_attentions", "encoder_hidden_states", "logits"]: outputs[key] = tuple(sapiens_technology_torch.stack([v[key][i] for v in seek_outputs]).to(device) for i in range(len(seek_outputs[0][key])))
            elif key == "sequences_scores": outputs[key] = sapiens_technology_torch.stack([v[key] for v in seek_outputs], dim=0).to(device)
            elif key in ["decoder_attentions", "decoder_hidden_states", "cross_attentions"]: outputs[key] = tuple(tuple(sapiens_technology_torch.stack([v[key][i][j] for v in seek_outputs]).squeeze(1).to(device) for j in range(len(seek_outputs[0][key][0]))) for i in range(len(seek_outputs[0][key])))
            elif key == "past_key_values":
                past_key_value_type = kwargs.get("past_key_values")
                if seek_outputs[0][key] is not None:
                    outputs[key] = tuple(tuple(sapiens_technology_torch.stack([v[key][i][j] for v in seek_outputs]).squeeze(1).to(device) for j in range(len(seek_outputs[0][key][0]))) for i in range(len(seek_outputs[0][key])))
                    if past_key_value_type is not None and isinstance(past_key_value_type, EncoderDecoderCache): outputs[key] = past_key_value_type.from_legacy_cache(outputs[key])
                else: outputs[key] = None
        return model_output_type(**outputs)
    def _need_fallback(self, seek_sequence, seek_outputs, index, logits_processor, generation_config, vocab_size, temperature):
        needs_fallback, should_skip = False, False
        if generation_config.compression_ratio_threshold is not None:
            compression_ratio = self._retrieve_compression_ratio(seek_sequence, vocab_size)
            if compression_ratio > generation_config.compression_ratio_threshold: needs_fallback = True
        if generation_config.logprob_threshold is not None:
            if hasattr(seek_outputs[0], "sequences_scores"): logprobs = [s["sequences_scores"] for s in seek_outputs][index]
            else: logprobs = self._retrieve_avg_logprobs(seek_outputs[index]["scores"], seek_sequence, generation_config.eos_token_id, temperature)
            if logprobs < generation_config.logprob_threshold: needs_fallback = True
        if generation_config.no_speech_threshold is not None:
            no_speech_prob = _get_attr_from_logit_processors(logits_processor, SAPIAudioNoSpeechDetection, "no_speech_prob")
            if (logprobs < generation_config.logprob_threshold and no_speech_prob[index] > generation_config.no_speech_threshold): needs_fallback, should_skip = False, True
        return needs_fallback, should_skip
    def _expand_variables_for_generation(self, input_features, seek, max_frames, init_tokens, batch_size, condition_on_prev_tokens, generation_config):
        if generation_config.num_return_sequences is not None and generation_config.num_return_sequences > 1:
            batch_idx_map = list(range(batch_size * generation_config.num_return_sequences))
            cur_bsz, do_condition_on_prev_tokens = len(batch_idx_map), [condition_on_prev_tokens for _ in range(len(batch_idx_map))]
            input_features, seek = input_features.repeat_interleave(generation_config.num_return_sequences, dim=0), seek.repeat_interleave(generation_config.num_return_sequences, dim=0)
            max_frames, init_tokens = max_frames.repeat_interleave(generation_config.num_return_sequences, dim=0), init_tokens.repeat_interleave(generation_config.num_return_sequences, dim=0)
            generation_config.num_return_sequences = 1
        else:
            cur_bsz = batch_size
            batch_idx_map, do_condition_on_prev_tokens = list(range(cur_bsz)), [condition_on_prev_tokens for _ in range(cur_bsz)]
        return (batch_idx_map, cur_bsz, input_features, seek, max_frames, init_tokens, do_condition_on_prev_tokens)
    @staticmethod
    def _setup_no_speech_detection(logits_processor, segment_input, decoder_input_ids, kwargs):
        set_inputs = _get_attr_from_logit_processors(logits_processor, SAPIAudioNoSpeechDetection, "set_inputs")
        extra_kwargs = {k: v for k, v in kwargs.items() if sapiens_technology_torch.is_tensor(v)}
        set_inputs({"inputs": segment_input, "decoder_input_ids": decoder_input_ids, **extra_kwargs})
    @staticmethod
    def _retrieve_total_input_frames(input_features, input_stride, kwargs):
        if input_features is not None: return input_features.shape[0], input_features.shape[-1]
        if "encoder_outputs" in kwargs:
            encoder_outputs_shape = (kwargs["encoder_outputs"][0].shape if isinstance(kwargs["encoder_outputs"], BaseModelOutput) else kwargs["encoder_outputs"].shape)
            return encoder_outputs_shape[0], encoder_outputs_shape[1] * input_stride
        raise ValueError("Make sure to provide either `input_features` or `encoder_outputs` to `generate`.")
    @staticmethod
    def _maybe_warn_unused_inputs(condition_on_prev_tokens, temperature, compression_ratio_threshold, logprob_threshold, no_speech_threshold, total_input_frames):
        warning_prefix = (f"Audio input consists of only {total_input_frames}. Short-form transcription is activated."" {}, but will be ignored.")
        if isinstance(temperature, (list, tuple)): raise ValueError(f"Audio input consists of only {total_input_frames}. Short-form transcription is activated. temperature cannot be set to {temperature} which can only be used for temperature fallback for long-form generation. Make sure to set `temperature` to a float value or `None` for short-form generation.")
    @staticmethod
    def _set_return_outputs(return_dict_in_generate, return_token_timestamps, logprob_threshold, generation_config):
        if return_dict_in_generate is None: return_dict_in_generate = generation_config.return_dict_in_generate
        else: generation_config.return_dict_in_generate = return_dict_in_generate
        generation_config.return_token_timestamps = return_token_timestamps
        if return_token_timestamps: generation_config.return_dict_in_generate, generation_config.output_attentions, generation_config.output_scores = True, True, True
        if logprob_threshold is not None: generation_config.return_dict_in_generate, generation_config.output_scores = True, True
        return return_dict_in_generate
    def _set_return_timestamps(self, return_timestamps, is_shortform, generation_config):
        if return_timestamps is None and hasattr(generation_config, "return_timestamps"): return_timestamps = generation_config.return_timestamps
        if not is_shortform:
            if return_timestamps is False: raise ValueError("You have passed more than 3000 mel input features (> 30 seconds) which automatically enables long-form generation which requires the model to predict timestamp tokens. Please either pass `return_timestamps=True` or make sure to pass no more than 3000 mel input features.")
            return_timestamps = True
        if return_timestamps and not hasattr(generation_config, "no_timestamps_token_id"): raise ValueError("You are trying to return timestamps, but the generation config is not properly set. Make sure to initialize the generation config with the correct attributes that are needed such as `no_timestamps_token_id`.")
        generation_config.return_timestamps = return_timestamps
        if hasattr(generation_config, "no_timestamps_token_id"): timestamp_begin = generation_config.no_timestamps_token_id + 1
        else: timestamp_begin = self.config.vocab_size + 1
        return timestamp_begin
    @staticmethod
    def _set_language_and_task(language, task, is_multilingual, generation_config):
        if is_multilingual is not None:
            if not hasattr(generation_config, "is_multilingual"): raise ValueError("The generation config is outdated and is thus not compatible with the `is_multilingual` argument to `generate`.")
            generation_config.is_multilingual = is_multilingual
        if hasattr(generation_config, "is_multilingual") and not generation_config.is_multilingual:
            if task is not None or language is not None: raise ValueError("Cannot specify `task` or `language` for an English-only model. If the model is intended to be multilingual, pass `is_multilingual=True` to generate, or update the generation config.")
        if language is not None:
            if not hasattr(generation_config, "lang_to_id"): raise ValueError("The generation config is outdated and is thus not compatible with the `language` argument to `generate`.")
            generation_config.language = language
        if task is not None:
            if not hasattr(generation_config, "task_to_id"): raise ValueError("The generation config is outdated and is thus not compatible with the `task` argument to `generate`.")
            generation_config.task = task
    def _retrieve_init_tokens(self, input_features, batch_size, generation_config, config, num_segment_frames, kwargs):
        def replace_or_add(lst: List[int], num: int, itr: Iterator[int]):
            if any(i in lst for i in itr): lst = [num if i in itr else i for i in lst]
            else: lst.append(num)
            return lst
        def language_to_id(language: str) -> int:
            language = language.lower()
            if language in generation_config.lang_to_id.keys(): language_token = language
            elif language in TO_LANGUAGE_CODE.keys(): language_token = f"<|{TO_LANGUAGE_CODE[language]}|>"
            elif language in TO_LANGUAGE_CODE.values(): language_token = f"<|{language}|>"
            else:
                is_language_code = len(language) == 2
                raise ValueError(f"Unsupported language: {language}. Language should be one of: {list(TO_LANGUAGE_CODE.values()) if is_language_code else list(TO_LANGUAGE_CODE.keys())}.")
            if language_token not in generation_config.lang_to_id: raise ValueError(f"{language_token} is not supported by this specific model as it is not in the `generation_config.lang_to_id`. (You should just add it to the generation config)")
            return generation_config.lang_to_id[language_token]
        task, language, forced_decoder_ids = getattr(generation_config, "task", None), getattr(generation_config, "language", None), generation_config.forced_decoder_ids
        if hasattr(config, "forced_decoder_ids") and config.forced_decoder_ids is not None: forced_decoder_ids = config.forced_decoder_ids
        if (forced_decoder_ids is not None and task is not None) or (forced_decoder_ids is not None and language is not None): forced_decoder_ids = None
        init_tokens = [generation_config.decoder_start_token_id]
        if forced_decoder_ids is not None and forced_decoder_ids[0][0] == 1:
            i = 1
            while len(forced_decoder_ids) > 0 and forced_decoder_ids[0][0] == i:
                init_tokens += [forced_decoder_ids[0][1]]
                forced_decoder_ids = forced_decoder_ids[1:]
                i += 1
            if len(forced_decoder_ids) > 0: raise ValueError(f"You are using token ids in `forced_decoder_ids` that do not seem to correctly follow the prompt pattern of SAPIAudio. Make sure that {forced_decoder_ids} has an entry for all indices >= 1 and < {forced_decoder_ids[0][0]}.")
        generation_config.forced_decoder_ids, is_lang_id_undefined = None, len(init_tokens) <= 1 or (len(init_tokens) > 1 and init_tokens[1] is None)
        if isinstance(language, (list, tuple)):
            if any(l is None for l in language): raise TypeError("Expected `language` to be `None`, a single string (e.g. `'en'`), or a list of strings with length equal to the batch size (e.g. `('en', 'fr')` for a batch size of 2). Got a list containing `None`.")
            if len(language) != batch_size: raise ValueError(f"When passing a list of languages, the length of the list must match the batch size. Expected length of {batch_size}, but got {len(language)} languages.")
            languages = language
        elif language is None: languages = [None] * batch_size
        else: languages = [language]
        init_tokens, lang_ids = [sapiens_technology_copy.copy(init_tokens) for _ in languages], None
        if language is not None: lang_ids = [language_to_id(l) for l in languages]
        elif hasattr(generation_config, "lang_to_id") and is_lang_id_undefined: lang_ids = self.detect_language(input_features=input_features, encoder_outputs=kwargs.get("encoder_outputs", None), generation_config=generation_config, num_segment_frames=num_segment_frames).tolist()
        if lang_ids is not None:
            for i in range(len(init_tokens)):
                if len(init_tokens[i]) > 1: init_tokens[i][1] = lang_ids[i]
                else: init_tokens[i].append(lang_ids[i])
        del languages
        for i in range(len(init_tokens)):
            if task is not None:
                if task in TASK_IDS:
                    init_tokens[i].append(generation_config.task_to_id[generation_config.task])
                    task_id = generation_config.task_to_id[generation_config.task]
                    replace_or_add(init_tokens[i], task_id, generation_config.task_to_id.values())
                else: raise ValueError(f"The `{task}`task is not supported. The task should be one of `{TASK_IDS}`")
            elif language is not None and hasattr(generation_config, "task_to_id"):
                if not any(ti in init_tokens[i] for ti in generation_config.task_to_id.values()): init_tokens[i].append(generation_config.task_to_id["transcribe"])
            if (not generation_config.return_timestamps and hasattr(generation_config, "no_timestamps_token_id") and init_tokens[i][-1] != generation_config.no_timestamps_token_id): init_tokens[i].append(generation_config.no_timestamps_token_id)
            elif (generation_config.return_timestamps and init_tokens[i][-1] == generation_config.no_timestamps_token_id): init_tokens[i] = init_tokens[i][:-1]
            init_tokens[i] = [t for t in init_tokens[i] if t is not None]
        return sapiens_technology_torch.as_tensor(init_tokens, dtype=sapiens_technology_torch.long, device=self.device).expand(batch_size, -1)
    def detect_language(self, input_features: Optional[sapiens_technology_torch.FloatTensor] = None, encoder_outputs: Optional[Union[sapiens_technology_torch.FloatTensor, BaseModelOutput]] = None,
    generation_config: Optional[GenerationConfig] = None, num_segment_frames: int = 3000) -> sapiens_technology_torch.Tensor:
        if input_features is None and encoder_outputs is None: raise ValueError("You have to specify either `input_features` or `encoder_outputs`")
        elif input_features is not None and encoder_outputs is not None: raise ValueError("Make sure to specificy only one of `input_features` or `encoder_outputs` - not both!")
        elif input_features is not None:
            inputs = {"input_features": input_features[:, :, :num_segment_frames]}
            batch_size = input_features.shape[0]
        elif encoder_outputs is not None:
            inputs = {"encoder_outputs": encoder_outputs}
            batch_size = (encoder_outputs[0].shape[0] if isinstance(encoder_outputs, BaseModelOutput) else encoder_outputs[0])
        generation_config = generation_config or self.generation_config
        decoder_input_ids = (sapiens_technology_torch.ones((batch_size, 1), device=self.device, dtype=sapiens_technology_torch.long) * generation_config.decoder_start_token_id)
        with sapiens_technology_torch.no_grad(): logits = self(**inputs, decoder_input_ids=decoder_input_ids).logits[:, -1]
        non_lang_mask = sapiens_technology_torch.ones_like(logits[0], dtype=sapiens_technology_torch.bool)
        non_lang_mask[list(generation_config.lang_to_id.values())] = False
        logits[:, non_lang_mask] = -sapiens_technology_numbers.inf
        return logits.argmax(-1)
    @staticmethod
    def _check_decoder_input_ids(kwargs):
        decoder_input_ids, assistant_model = kwargs.get("decoder_input_ids", None), kwargs.get("assistant_model", None)
        if decoder_input_ids is not None and assistant_model is not None: raise ValueError("Passing `decoder_input_ids` is deprecated. Consider passing `prompt_ids` instead.")
    @staticmethod
    def _set_num_frames(return_token_timestamps, generation_config, kwargs):
        if return_token_timestamps:
            if not hasattr(generation_config, "alignment_heads"): raise ValueError("Model generation config has no `alignment_heads`, token-level timestamps not available. See https://gist.github.com/hollance/42e32852f24243b748ae6bc1f985b13a on how to add this property to the generation config.")
            generation_config.num_frames = kwargs.pop("num_frames", None)
    @staticmethod
    def _set_thresholds_and_condition(generation_config, logprob_threshold, compression_ratio_threshold, no_speech_threshold, condition_on_prev_tokens):
        generation_config.logprob_threshold = (logprob_threshold if logprob_threshold is not None else getattr(generation_config, "logprob_threshold", None))
        generation_config.compression_ratio_threshold = (compression_ratio_threshold if compression_ratio_threshold is not None else getattr(generation_config, "compression_ratio_threshold", None))
        generation_config.no_speech_threshold = (no_speech_threshold if no_speech_threshold is not None else getattr(generation_config, "no_speech_threshold", None))
        generation_config.condition_on_prev_tokens = (condition_on_prev_tokens if condition_on_prev_tokens is not None else getattr(generation_config, "condition_on_prev_tokens", None))
    @staticmethod
    def _set_prompt_condition_type(generation_config, prompt_condition_type):
        allowed_cond_types = ["first-segment", "all-segments"]
        prompt_condition_type = prompt_condition_type or allowed_cond_types[0]
        if prompt_condition_type not in allowed_cond_types: raise ValueError(f"`prompt_condition_type={prompt_condition_type} does not exist. Make sure to set `prompt_condition_type` to one of {', '.join(allowed_cond_types)}")
        if generation_config.condition_on_prev_tokens is not True and prompt_condition_type == "all-segments": raise ValueError("Make sure to set `condition_on_prev_tokens=True` when setting `prompt_condition_type='all-segments'`.")
        generation_config.prompt_condition_type = prompt_condition_type
    @staticmethod
    def _set_condition_on_prev_tokens(condition_on_prev_tokens, generation_config): generation_config.condition_on_prev_tokens = (condition_on_prev_tokens if condition_on_prev_tokens is not None else getattr(generation_config, "condition_on_prev_tokens", False))
    @staticmethod
    def _retrieve_max_frames_and_seek(batch_size, attention_mask, total_input_frames, is_shortform):
        if batch_size > 1 and not is_shortform and attention_mask is None: raise ValueError("When doing batched long-form audio transcription, make sure to pass an `attention_mask`. You can retrieve the `attention_mask` by doing `processor(audio, ..., return_attention_mask=True)` ")
        elif batch_size > 1 and not is_shortform: max_frames, seek = attention_mask.sum(-1).cpu().to(sapiens_technology_torch.long), sapiens_technology_torch.zeros((batch_size,), dtype=sapiens_technology_torch.long)
        else: max_frames, seek = sapiens_technology_torch.ones((batch_size,), dtype=sapiens_technology_torch.long) * total_input_frames, sapiens_technology_torch.zeros((batch_size,), dtype=sapiens_technology_torch.long)
        return max_frames, seek
    def _retrieve_logit_processors(self, generation_config, logits_processor, begin_index, num_beams, device):
        if generation_config.return_timestamps is True:
            timestamp_processor = SAPIAudioTimeStampLogitsProcessor(generation_config, begin_index=begin_index)
            logits_processor = ([timestamp_processor] if logits_processor is None else [timestamp_processor] + logits_processor)
        if generation_config.suppress_tokens is not None:
            suppress_tokens_processor = SuppressTokensLogitsProcessor(generation_config.suppress_tokens, device=device)
            logits_processor, generation_config.suppress_tokens = ([suppress_tokens_processor] if logits_processor is None else [suppress_tokens_processor] + logits_processor), None
        if generation_config.begin_suppress_tokens is not None:
            begin_suppress_processor = SuppressTokensAtBeginLogitsProcessor(generation_config.begin_suppress_tokens, begin_index=begin_index, device=device)
            logits_processor, generation_config.begin_suppress_tokens = ([begin_suppress_processor] if logits_processor is None else [begin_suppress_processor] + logits_processor), None
        if generation_config.no_speech_threshold is not None:
            no_speech_detector = SAPIAudioNoSpeechDetection(no_speech_token=generation_config.no_timestamps_token_id - 1, begin_index=begin_index, scores_is_logprobs=num_beams > 1)
            logits_processor = ([no_speech_detector] if logits_processor is None else [no_speech_detector] + logits_processor)
            no_speech_detector.set_model(self)
        return logits_processor
    @staticmethod
    def _maybe_reduce_batch(input_features, seek, max_frames, cur_bsz, batch_idx_map):
        prev_bsz, new_batch_idx_map = cur_bsz, []
        for i in range(prev_bsz):
            prev_i = batch_idx_map[i]
            if seek[prev_i] >= max_frames[prev_i]:
                cut_index = i + (cur_bsz - prev_bsz)
                cur_bsz -= 1
                input_features = sapiens_technology_torch.cat([input_features[:cut_index], input_features[cut_index + 1 :]], dim=0)
            else: new_batch_idx_map.append(prev_i)
        return input_features, cur_bsz, new_batch_idx_map
    @staticmethod
    def _get_input_segment(input_features, seek, seek_num_frames, num_segment_frames, cur_bsz, batch_idx_map):
        if input_features is None: return None
        segment_input = []
        for i in range(cur_bsz):
            prev_i = batch_idx_map[i]
            segment_input_slice = input_features[i : i + 1, :, seek[prev_i] : seek[prev_i] + seek_num_frames[prev_i]]
            if segment_input_slice.shape[-1] < num_segment_frames: segment_input_slice = Functional.pad(segment_input_slice, pad=(0, num_segment_frames - segment_input_slice.shape[-1]))
            segment_input.append(segment_input_slice)
        return sapiens_technology_torch.cat(segment_input, dim=0)
    @staticmethod
    def _prepare_decoder_input_ids(cur_bsz, init_tokens, current_segments, batch_idx_map, do_condition_on_prev_tokens, prompt_ids, generation_config, config, device, suppress_tokens, kwargs):
        if "decoder_input_ids" in kwargs:
            decoder_input_ids = kwargs.pop("decoder_input_ids")
            return decoder_input_ids, kwargs
        cut_off_length, decoder_input_ids, prev_start_of_text = config.max_target_positions // 2 - 1, init_tokens[batch_idx_map], getattr(generation_config, "prev_sot_token_id", None)
        if prev_start_of_text is None: prev_start_of_text = suppress_tokens[-2] if suppress_tokens is not None else None
        if any(do_condition_on_prev_tokens) and len(current_segments[0]) > 0:
            active_segments = [current_segments[i] if do_condition_on_prev_tokens[i] else None for i in batch_idx_map]
            if prompt_ids is not None and generation_config.prompt_condition_type == "all-segments": prev_ids = prompt_ids
            else: prev_ids = prev_start_of_text * sapiens_technology_torch.ones((cur_bsz, 1), device=device, dtype=sapiens_technology_torch.long)[0] if prev_start_of_text is not None else None
            padding = "max_length" if generation_config.cache_implementation == "static" else "longest"
            prev_tokens = _pad_to_max_length(active_segments, generation_config.pad_token_id, device=device, padding_side="left", padding=padding, bos_token_tensor=prev_ids, cut_off_length=cut_off_length)
            decoder_input_ids = sapiens_technology_torch.cat([prev_tokens, decoder_input_ids], dim=-1)
            kwargs["decoder_attention_mask"] = decoder_input_ids != generation_config.pad_token_id
        elif prompt_ids is not None:
            decoder_input_ids = sapiens_technology_torch.cat([prompt_ids[None].repeat(decoder_input_ids.shape[0], 1), decoder_input_ids], dim=-1)
            kwargs.pop("decoder_attention_mask", None)
        else: kwargs.pop("decoder_attention_mask", None)
        return decoder_input_ids, kwargs
    def _set_max_new_tokens_and_length(self, config, decoder_input_ids, generation_config):
        max_new_tokens = generation_config.max_new_tokens if generation_config.max_new_tokens is not None else 0
        if max_new_tokens + decoder_input_ids.shape[-1] > self.config.max_target_positions: raise ValueError(f"The length of `decoder_input_ids`, including special start tokens, prompt tokens, and previous tokens, is {decoder_input_ids.shape[-1]}, and `max_new_tokens` is {max_new_tokens}. Thus, the combined length of `decoder_input_ids` and `max_new_tokens` is: {max_new_tokens + decoder_input_ids.shape[-1]}. This exceeds the `max_target_positions` of the SAPIAudio model: {self.config.max_target_positions}. You should either reduce the length of your prompt, or reduce the value of `max_new_tokens`, so that their combined length is less than {self.config.max_target_positions}.")
        num_initial_tokens = min(config.max_target_positions // 2 - 1, decoder_input_ids.shape[-1] - 1)
        if generation_config.max_length is not None and generation_config.max_new_tokens is None: max_length = min(generation_config.max_length + num_initial_tokens, config.max_target_positions)
        elif (generation_config.max_new_tokens is not None and generation_config.max_new_tokens + decoder_input_ids.shape[-1] > config.max_target_positions): generation_config.max_new_tokens = config.max_target_positions - decoder_input_ids.shape[-1]
    @staticmethod
    def _retrieve_compression_ratio(tokens, vocab_size):
        from math import log2
        from zlib import compress
        token_bytes = b"".join([t.to_bytes(int(log2(vocab_size) / 8) + 1, "little") for t in tokens.tolist()])
        return len(token_bytes) / len(compress(token_bytes))
    @staticmethod
    def _retrieve_avg_logprobs(scores, tokens, eos_token_id, temperature):
        scores = sapiens_technology_torch.stack(scores).to(tokens.device)
        if scores.shape[0] > tokens.shape[0]: scores = scores[: tokens.shape[0]]
        else: tokens = tokens[-scores.shape[0] :]
        logprobs = Functional.log_softmax((scores * (temperature if temperature > 0.0 else 1)).float(), dim=-1).to(scores.dtype)
        return (sum((logprobs[i][tokens[i]] * (tokens[i] != eos_token_id)) for i in range(logprobs.shape[0]))) / (((tokens != eos_token_id).sum(-1) if eos_token_id is not None else tokens.shape[0]) + 1)
    @staticmethod
    def _retrieve_segment(seek_sequence, seek_outputs, time_offset, timestamp_begin, seek_num_frames, time_precision, input_stride, prev_idx, idx, return_token_timestamps):
        timestamp_tokens: sapiens_technology_torch.Tensor = seek_sequence.ge(timestamp_begin)
        single_timestamp_ending = timestamp_tokens[-2:].tolist() == [False, True]
        timestamp_segment_indices = sapiens_technology_torch.where(timestamp_tokens[:-1] & timestamp_tokens[1:])[0]
        timestamp_segment_indices.add_(1)
        token_timestamps = seek_outputs[idx]["token_timestamps"] if return_token_timestamps else []
        if len(timestamp_segment_indices) > 0:
            slices, segments, last_slice = timestamp_segment_indices.tolist(), [], 0
            if single_timestamp_ending: slices.append(len(seek_sequence))
            for current_slice in slices:
                sliced_tokens = seek_sequence[last_slice:current_slice]
                start_timestamp_pos, end_timestamp_pos = sliced_tokens[0].item() - timestamp_begin, sliced_tokens[-1].item() - timestamp_begin
                segments.append({"start": time_offset[prev_idx] + start_timestamp_pos * time_precision, "end": time_offset[prev_idx] + end_timestamp_pos * time_precision,
                "tokens": sliced_tokens, "result": seek_outputs[idx]})
                if return_token_timestamps: segments[-1]["token_timestamps"] = (token_timestamps[last_slice:current_slice] + time_offset[prev_idx])
                last_slice = current_slice
            if single_timestamp_ending: segment_offset = seek_num_frames[prev_idx]
            else: segment_offset = (seek_sequence[last_slice - 1].item() - timestamp_begin) * input_stride
        else:
            timestamps = seek_sequence[timestamp_tokens.nonzero().flatten()]
            last_timestamp_pos = seek_num_frames[prev_idx]
            if timestamps.numel() > 0 and timestamps[-1].item() != timestamp_begin: last_timestamp_pos = timestamps[-1].item() - timestamp_begin
            segments = [{"start": time_offset[prev_idx], "end": time_offset[prev_idx] + last_timestamp_pos * time_precision, "tokens": seek_sequence, "result": seek_outputs[idx]}]
            if return_token_timestamps: segments[-1]["token_timestamps"] = token_timestamps + time_offset[prev_idx]
            segment_offset = seek_num_frames[prev_idx]
        return segments, segment_offset
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
