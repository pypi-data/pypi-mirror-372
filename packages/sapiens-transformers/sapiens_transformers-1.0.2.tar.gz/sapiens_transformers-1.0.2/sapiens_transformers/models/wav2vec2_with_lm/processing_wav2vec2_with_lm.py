"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
import warnings
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from multiprocessing import Pool, get_context, get_start_method
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Union
import numpy as np
from ...processing_utils import ProcessorMixin
from ...utils import ModelOutput, logging, requires_backends
logger = logging.get_logger(__name__)
if TYPE_CHECKING:
    from pyctcdecode import BeamSearchDecoderCTC
    from ...feature_extraction_utils import FeatureExtractionMixin
    from ...tokenization_utils import PreTrainedTokenizerBase
ListOfDict = List[Dict[str, Union[int, str]]]
@dataclass
class Wav2Vec2DecoderWithLMOutput(ModelOutput):
    """Args:"""
    text: Union[List[List[str]], List[str], str]
    logit_score: Union[List[List[float]], List[float], float] = None
    lm_score: Union[List[List[float]], List[float], float] = None
    word_offsets: Union[List[List[ListOfDict]], List[ListOfDict], ListOfDict] = None
class Wav2Vec2ProcessorWithLM(ProcessorMixin):
    feature_extractor_class = "AutoFeatureExtractor"
    tokenizer_class = "Wav2Vec2CTCTokenizer"
    def __init__(self, feature_extractor: "FeatureExtractionMixin", tokenizer: "PreTrainedTokenizerBase", decoder: "BeamSearchDecoderCTC"):
        from pyctcdecode import BeamSearchDecoderCTC
        super().__init__(feature_extractor, tokenizer)
        if not isinstance(decoder, BeamSearchDecoderCTC): raise TypeError(f"`decoder` has to be of type {BeamSearchDecoderCTC.__class__}, but is {type(decoder)}")
        if feature_extractor.__class__.__name__ not in ["Wav2Vec2FeatureExtractor", "SeamlessM4TFeatureExtractor"]: raise ValueError(f"`feature_extractor` has to be of type `Wav2Vec2FeatureExtractor` or `SeamlessM4TFeatureExtractor`, but is {type(feature_extractor)}")
        missing_decoder_tokens = self.get_missing_alphabet_tokens(decoder, tokenizer)
        if len(missing_decoder_tokens) > 0: raise ValueError(f"The tokens {missing_decoder_tokens} are defined in the tokenizer's vocabulary, but not in the decoder's alphabet. Make sure to include {missing_decoder_tokens} in the decoder's alphabet.")
        self.decoder = decoder
        self.current_processor = self.feature_extractor
        self._in_target_context_manager = False
    def save_pretrained(self, save_directory):
        super().save_pretrained(save_directory)
        self.decoder.save_to_dir(save_directory)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        requires_backends(cls, "pyctcdecode")
        from pyctcdecode import BeamSearchDecoderCTC
        feature_extractor, tokenizer = super()._get_arguments_from_pretrained(pretrained_model_name_or_path, **kwargs)
        if os.path.isdir(pretrained_model_name_or_path) or os.path.isfile(pretrained_model_name_or_path):
            unigram_encoding = kwargs.get("unigram_encoding", "utf-8")
            decoder = BeamSearchDecoderCTC.load_from_dir(pretrained_model_name_or_path, unigram_encoding)
        else:
            kwargs.pop("_from_auto", None)
            kwargs.pop("trust_remote_code", None)
            language_model_filenames = os.path.join(BeamSearchDecoderCTC._LANGUAGE_MODEL_SERIALIZED_DIRECTORY, "*")
            alphabet_filename = BeamSearchDecoderCTC._ALPHABET_SERIALIZED_FILENAME
            allow_patterns = [language_model_filenames, alphabet_filename]
            decoder = BeamSearchDecoderCTC.load_from_hf_hub(pretrained_model_name_or_path, allow_patterns=allow_patterns, **kwargs)
        for attribute in ["alpha", "beta", "unk_score_offset", "score_boundary"]:
            value = kwargs.pop(attribute, None)
            if value is not None: cls._set_language_model_attribute(decoder, attribute, value)
        missing_decoder_tokens = cls.get_missing_alphabet_tokens(decoder, tokenizer)
        if len(missing_decoder_tokens) > 0: raise ValueError(f"The tokens {missing_decoder_tokens} are defined in the tokenizer's vocabulary, but not in the decoder's alphabet. Make sure to include {missing_decoder_tokens} in the decoder's alphabet.")
        return cls(feature_extractor=feature_extractor, tokenizer=tokenizer, decoder=decoder)
    @staticmethod
    def _set_language_model_attribute(decoder: "BeamSearchDecoderCTC", attribute: str, value: float): setattr(decoder.model_container[decoder._model_key], attribute, value)
    @property
    def language_model(self): return self.decoder.model_container[self.decoder._model_key]
    @staticmethod
    def get_missing_alphabet_tokens(decoder, tokenizer):
        from pyctcdecode.alphabet import BLANK_TOKEN_PTN, UNK_TOKEN, UNK_TOKEN_PTN
        tokenizer_vocab_list = list(tokenizer.get_vocab().keys())
        for i, token in enumerate(tokenizer_vocab_list):
            if BLANK_TOKEN_PTN.match(token): tokenizer_vocab_list[i] = ""
            if token == tokenizer.word_delimiter_token: tokenizer_vocab_list[i] = " "
            if UNK_TOKEN_PTN.match(token): tokenizer_vocab_list[i] = UNK_TOKEN
        missing_tokens = set(tokenizer_vocab_list) - set(decoder._alphabet.labels)
        return missing_tokens
    def __call__(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor(*args, **kwargs)
        if "raw_speech" in kwargs:
            warnings.warn("Using `raw_speech` as a keyword argument is deprecated. Use `audio` instead.")
            audio = kwargs.pop("raw_speech")
        else: audio = kwargs.pop("audio", None)
        sampling_rate = kwargs.pop("sampling_rate", None)
        text = kwargs.pop("text", None)
        if len(args) > 0:
            audio = args[0]
            args = args[1:]
        if audio is None and text is None: raise ValueError("You need to specify either an `audio` or `text` input to process.")
        if audio is not None: inputs = self.feature_extractor(audio, *args, sampling_rate=sampling_rate, **kwargs)
        if text is not None: encodings = self.tokenizer(text, **kwargs)
        if text is None: return inputs
        elif audio is None: return encodings
        else:
            inputs["labels"] = encodings["input_ids"]
            return inputs
    def pad(self, *args, **kwargs):
        if self._in_target_context_manager: return self.current_processor.pad(*args, **kwargs)
        input_features = kwargs.pop("input_features", None)
        labels = kwargs.pop("labels", None)
        if len(args) > 0:
            input_features = args[0]
            args = args[1:]
        if input_features is not None: input_features = self.feature_extractor.pad(input_features, *args, **kwargs)
        if labels is not None: labels = self.tokenizer.pad(labels, **kwargs)
        if labels is None: return input_features
        elif input_features is None: return labels
        else:
            input_features["labels"] = labels["input_ids"]
            return input_features
    def batch_decode(self, logits: np.ndarray, pool: Optional[Pool] = None, num_processes: Optional[int] = None, beam_width: Optional[int] = None, beam_prune_logp: Optional[float] = None,
    token_min_logp: Optional[float] = None, hotwords: Optional[Iterable[str]] = None, hotword_weight: Optional[float] = None, alpha: Optional[float] = None,
    beta: Optional[float] = None, unk_score_offset: Optional[float] = None, lm_score_boundary: Optional[bool] = None, output_word_offsets: bool = False, n_best: int = 1):
        from pyctcdecode.constants import (DEFAULT_BEAM_WIDTH, DEFAULT_HOTWORD_WEIGHT, DEFAULT_MIN_TOKEN_LOGP, DEFAULT_PRUNE_LOGP)
        beam_width = beam_width if beam_width is not None else DEFAULT_BEAM_WIDTH
        beam_prune_logp = beam_prune_logp if beam_prune_logp is not None else DEFAULT_PRUNE_LOGP
        token_min_logp = token_min_logp if token_min_logp is not None else DEFAULT_MIN_TOKEN_LOGP
        hotword_weight = hotword_weight if hotword_weight is not None else DEFAULT_HOTWORD_WEIGHT
        self.decoder.reset_params(alpha=alpha, beta=beta, unk_score_offset=unk_score_offset, lm_score_boundary=lm_score_boundary)
        logits_list = [array[(array != -100.0).all(axis=-1)] for array in logits]
        if pool is None:
            default_context = get_start_method()
            if default_context == "fork": cm = pool = get_context().Pool(num_processes)
            else:
                logger.warning("Parallel batch decoding is not currently supported in this platform. Falling back to sequential decoding.")
                cm = nullcontext()
        else:
            cm = nullcontext()
            if num_processes is not None: logger.warning("Parameter `num_process` was passed, but it will be ignored since `pool` was also specified.")
        with cm:
            decoded_beams = self.decoder.decode_beams_batch(pool=pool, logits_list=logits_list, beam_width=beam_width, beam_prune_logp=beam_prune_logp,
            token_min_logp=token_min_logp, hotwords=hotwords, hotword_weight=hotword_weight)
        batch_texts, logit_scores, lm_scores, word_offsets = [], [], [], []
        for d in decoded_beams:
            batch_texts.append([beam[0] for beam in d])
            logit_scores.append([beam[-2] for beam in d])
            lm_scores.append([beam[-1] for beam in d])
            word_offsets.append([[{"word": word, "start_offset": start_offset, "end_offset": end_offset} for word, (start_offset, end_offset) in beam[1]] for beam in d])
        word_offsets = word_offsets if output_word_offsets else None
        if n_best == 1: return Wav2Vec2DecoderWithLMOutput(text=[hyps[0] for hyps in batch_texts], logit_score=[hyps[0] for hyps in logit_scores], lm_score=[hyps[0] for hyps in lm_scores], word_offsets=[hyps[0] for hyps in word_offsets] if word_offsets is not None else None)
        else: return Wav2Vec2DecoderWithLMOutput(text=[hyps[:n_best] for hyps in batch_texts], logit_score=[hyps[:n_best] for hyps in logit_scores], lm_score=[hyps[:n_best] for hyps in lm_scores], word_offsets=[hyps[:n_best] for hyps in word_offsets] if word_offsets is not None else None)
    def decode(self, logits: np.ndarray, beam_width: Optional[int] = None, beam_prune_logp: Optional[float] = None, token_min_logp: Optional[float] = None, hotwords: Optional[Iterable[str]] = None,
    hotword_weight: Optional[float] = None, alpha: Optional[float] = None, beta: Optional[float] = None, unk_score_offset: Optional[float] = None, lm_score_boundary: Optional[bool] = None, output_word_offsets: bool = False, n_best: int = 1):
        from pyctcdecode.constants import (DEFAULT_BEAM_WIDTH, DEFAULT_HOTWORD_WEIGHT, DEFAULT_MIN_TOKEN_LOGP, DEFAULT_PRUNE_LOGP)
        beam_width = beam_width if beam_width is not None else DEFAULT_BEAM_WIDTH
        beam_prune_logp = beam_prune_logp if beam_prune_logp is not None else DEFAULT_PRUNE_LOGP
        token_min_logp = token_min_logp if token_min_logp is not None else DEFAULT_MIN_TOKEN_LOGP
        hotword_weight = hotword_weight if hotword_weight is not None else DEFAULT_HOTWORD_WEIGHT
        self.decoder.reset_params(alpha=alpha, beta=beta, unk_score_offset=unk_score_offset, lm_score_boundary=lm_score_boundary)
        decoded_beams = self.decoder.decode_beams(logits, beam_width=beam_width, beam_prune_logp=beam_prune_logp, token_min_logp=token_min_logp, hotwords=hotwords, hotword_weight=hotword_weight)
        word_offsets = None
        if output_word_offsets: word_offsets = [[{"word": word, "start_offset": start_offset, "end_offset": end_offset} for word, (start_offset, end_offset) in beam[2]] for beam in decoded_beams]
        logit_scores = [beam[-2] for beam in decoded_beams]
        lm_scores = [beam[-1] for beam in decoded_beams]
        hypotheses = [beam[0] for beam in decoded_beams]
        if n_best > len(decoded_beams): logger.info("N-best size is larger than the number of generated hypotheses, all hypotheses will be returned.")
        if n_best == 1: return Wav2Vec2DecoderWithLMOutput(text=hypotheses[0], logit_score=logit_scores[0], lm_score=lm_scores[0], word_offsets=word_offsets[0] if word_offsets is not None else None)
        else: return Wav2Vec2DecoderWithLMOutput(text=hypotheses[:n_best], logit_score=logit_scores[:n_best], lm_score=lm_scores[:n_best], word_offsets=word_offsets[:n_best] if word_offsets is not None else None)
    @contextmanager
    def as_target_processor(self):
        warnings.warn("`as_target_processor` is deprecated and will be removed in v1 of Sapiens Transformers. You can process your labels by using the argument `text` of the regular `__call__` method (either in the same call as your audio inputs, or in a separate call.")
        self._in_target_context_manager = True
        self.current_processor = self.tokenizer
        yield
        self.current_processor = self.feature_extractor
        self._in_target_context_manager = False
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
