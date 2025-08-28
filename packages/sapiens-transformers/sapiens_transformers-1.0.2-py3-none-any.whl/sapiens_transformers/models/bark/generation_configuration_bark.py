"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from typing import Dict
from ...generation.configuration_utils import GenerationConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class BarkSemanticGenerationConfig(GenerationConfig):
    model_type = "semantic"
    def __init__(self, eos_token_id=10_000, renormalize_logits=True, max_new_tokens=768, output_scores=False, return_dict_in_generate=False, output_hidden_states=False,
    output_attentions=False, temperature=1.0, do_sample=False, text_encoding_offset=10_048, text_pad_token=129_595, semantic_infer_token=129_599, semantic_vocab_size=10_000,
    max_input_semantic_length=256, semantic_rate_hz=49.9, min_eos_p=None, **kwargs):
        super().__init__(temperature=temperature, do_sample=do_sample, eos_token_id=eos_token_id, renormalize_logits=renormalize_logits, max_new_tokens=max_new_tokens,
        output_scores=output_scores, return_dict_in_generate=return_dict_in_generate, output_hidden_states=output_hidden_states, output_attentions=output_attentions, **kwargs)
        self.text_encoding_offset = text_encoding_offset
        self.text_pad_token = text_pad_token
        self.semantic_pad_token = eos_token_id
        self.semantic_infer_token = semantic_infer_token
        self.semantic_vocab_size = semantic_vocab_size
        self.max_input_semantic_length = max_input_semantic_length
        self.semantic_rate_hz = semantic_rate_hz
        self.min_eos_p = min_eos_p
class BarkCoarseGenerationConfig(GenerationConfig):
    model_type = "coarse_acoustics"
    def __init__(self, renormalize_logits=True, output_scores=False, return_dict_in_generate=False, output_hidden_states=False, output_attentions=False, temperature=1.0,
    do_sample=False, coarse_semantic_pad_token=12_048, coarse_rate_hz=75, n_coarse_codebooks=2, coarse_infer_token=12_050, max_coarse_input_length=256, max_coarse_history: int = 630,
    sliding_window_len: int = 60, **kwargs):
        super().__init__(temperature=temperature, do_sample=do_sample, renormalize_logits=renormalize_logits, output_scores=output_scores, return_dict_in_generate=return_dict_in_generate,
        output_hidden_states=output_hidden_states, output_attentions=output_attentions, **kwargs)
        self.coarse_semantic_pad_token = coarse_semantic_pad_token
        self.coarse_rate_hz = coarse_rate_hz
        self.n_coarse_codebooks = n_coarse_codebooks
        self.coarse_infer_token = coarse_infer_token
        self.max_coarse_input_length = max_coarse_input_length
        self.max_coarse_history = max_coarse_history
        self.sliding_window_len = sliding_window_len
class BarkFineGenerationConfig(GenerationConfig):
    model_type = "fine_acoustics"
    def __init__(self, temperature=1.0, max_fine_history_length=512, max_fine_input_length=1024, n_fine_codebooks=8, **kwargs):
        super().__init__(temperature=temperature)
        self.max_fine_history_length = max_fine_history_length
        self.max_fine_input_length = max_fine_input_length
        self.n_fine_codebooks = n_fine_codebooks
    def validate(self, **kwargs): pass
class BarkGenerationConfig(GenerationConfig):
    model_type = "bark"
    is_composition = True
    def __init__(self, semantic_config: Dict = None, coarse_acoustics_config: Dict = None, fine_acoustics_config: Dict = None, sample_rate=24_000, codebook_size=1024, **kwargs):
        if semantic_config is None:
            semantic_config = {}
            logger.info("semantic_config is None. initializing the semantic model with default values.")
        if coarse_acoustics_config is None:
            coarse_acoustics_config = {}
            logger.info("coarse_acoustics_config is None. initializing the coarse model with default values.")
        if fine_acoustics_config is None:
            fine_acoustics_config = {}
            logger.info("fine_acoustics_config is None. initializing the fine model with default values.")
        self.semantic_config = BarkSemanticGenerationConfig(**semantic_config)
        self.coarse_acoustics_config = BarkCoarseGenerationConfig(**coarse_acoustics_config)
        self.fine_acoustics_config = BarkFineGenerationConfig(**fine_acoustics_config)
        self.sample_rate = sample_rate
        self.codebook_size = codebook_size
    @classmethod
    def from_sub_model_configs(cls, semantic_config: BarkSemanticGenerationConfig, coarse_acoustics_config: BarkCoarseGenerationConfig, fine_acoustics_config: BarkFineGenerationConfig, **kwargs): return cls(semantic_config=semantic_config.to_dict(), coarse_acoustics_config=coarse_acoustics_config.to_dict(), fine_acoustics_config=fine_acoustics_config.to_dict(), **kwargs)
    def to_dict(self):
        output = copy.deepcopy(self.__dict__)
        output["semantic_config"] = self.semantic_config.to_dict()
        output["coarse_acoustics_config"] = self.coarse_acoustics_config.to_dict()
        output["fine_acoustics_config"] = self.fine_acoustics_config.to_dict()
        output["model_type"] = self.__class__.model_type
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
