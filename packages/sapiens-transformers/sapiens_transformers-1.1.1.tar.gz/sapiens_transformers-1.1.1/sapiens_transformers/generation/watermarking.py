"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional, Union
import numpy as np
from ..configuration_utils import PretrainedConfig
from ..utils import is_torch_available, logging
from .configuration_utils import WatermarkingConfig
if is_torch_available():
    import torch
    from .logits_process import WatermarkLogitsProcessor
logger = logging.get_logger(__name__)
@dataclass
class WatermarkDetectorOutput:
    num_tokens_scored: np.array = None
    num_green_tokens: np.array = None
    green_fraction: np.array = None
    z_score: np.array = None
    p_value: np.array = None
    prediction: Optional[np.array] = None
    confidence: Optional[np.array] = None
class WatermarkDetector:
    def __init__(self, model_config: PretrainedConfig, device: str, watermarking_config: Union[WatermarkingConfig, Dict], ignore_repeated_ngrams: bool = False, max_cache_size: int = 128):
        if isinstance(watermarking_config, WatermarkingConfig): watermarking_config = watermarking_config.to_dict()
        self.bos_token_id = (model_config.bos_token_id if not model_config.is_encoder_decoder else model_config.decoder_start_token_id)
        self.greenlist_ratio = watermarking_config["greenlist_ratio"]
        self.ignore_repeated_ngrams = ignore_repeated_ngrams
        self.processor = WatermarkLogitsProcessor(vocab_size=model_config.vocab_size, device=device, **watermarking_config)
        self._get_ngram_score_cached = lru_cache(maxsize=max_cache_size)(self._get_ngram_score)
    def _get_ngram_score(self, prefix: torch.LongTensor, target: int):
        greenlist_ids = self.processor._get_greenlist_ids(prefix)
        return target in greenlist_ids
    def _score_ngrams_in_passage(self, input_ids: torch.LongTensor):
        batch_size, seq_length = input_ids.shape
        selfhash = int(self.processor.seeding_scheme == "selfhash")
        n = self.processor.context_width + 1 - selfhash
        indices = torch.arange(n).unsqueeze(0) + torch.arange(seq_length - n + 1).unsqueeze(1)
        ngram_tensors = input_ids[:, indices]
        num_tokens_scored_batch = np.zeros(batch_size)
        green_token_count_batch = np.zeros(batch_size)
        for batch_idx in range(ngram_tensors.shape[0]):
            frequencies_table = collections.Counter(ngram_tensors[batch_idx])
            ngram_to_watermark_lookup = {}
            for ngram_example in frequencies_table.keys():
                prefix = ngram_example if selfhash else ngram_example[:-1]
                target = ngram_example[-1]
                ngram_to_watermark_lookup[ngram_example] = self._get_ngram_score_cached(prefix, target)
            if self.ignore_repeated_ngrams:
                num_tokens_scored_batch[batch_idx] = len(frequencies_table.keys())
                green_token_count_batch[batch_idx] = sum(ngram_to_watermark_lookup.values())
            else:
                num_tokens_scored_batch[batch_idx] = sum(frequencies_table.values())
                green_token_count_batch[batch_idx] = sum(freq * outcome for freq, outcome in zip(frequencies_table.values(), ngram_to_watermark_lookup.values()))
        return num_tokens_scored_batch, green_token_count_batch
    def _compute_z_score(self, green_token_count: np.array, total_num_tokens: np.array) -> np.array:
        expected_count = self.greenlist_ratio
        numer = green_token_count - expected_count * total_num_tokens
        denom = np.sqrt(total_num_tokens * expected_count * (1 - expected_count))
        z = numer / denom
        return z
    def _compute_pval(self, x, loc=0, scale=1):
        z = (x - loc) / scale
        return 1 - (0.5 * (1 + np.sign(z) * (1 - np.exp(-2 * z**2 / np.pi))))
    def __call__(self, input_ids: torch.LongTensor, z_threshold: float = 3.0, return_dict: bool = False) -> Union[WatermarkDetectorOutput, np.array]:
        if input_ids[0, 0] == self.bos_token_id: input_ids = input_ids[:, 1:]
        if input_ids.shape[-1] - self.processor.context_width < 1: raise ValueError(f"Must have at least `1` token to score after the first min_prefix_len={self.processor.context_width} tokens required by the seeding scheme.")
        num_tokens_scored, green_token_count = self._score_ngrams_in_passage(input_ids)
        z_score = self._compute_z_score(green_token_count, num_tokens_scored)
        prediction = z_score > z_threshold
        if return_dict:
            p_value = self._compute_pval(z_score)
            confidence = 1 - p_value
            return WatermarkDetectorOutput(num_tokens_scored=num_tokens_scored, num_green_tokens=green_token_count, green_fraction=green_token_count / num_tokens_scored, z_score=z_score, p_value=p_value, prediction=prediction, confidence=confidence)
        return prediction
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
