"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import List, Optional
from tokenizers import ByteLevelBPETokenizer
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from .tokenization_blenderbot_small import BlenderbotSmallTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'merges_file': 'merges.txt', 'tokenizer_config_file': 'tokenizer_config.json'}
class BlenderbotSmallTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = BlenderbotSmallTokenizer
    def __init__(self, vocab_file=None, merges_file=None, unk_token="<|endoftext|>", bos_token="<|endoftext|>", eos_token="<|endoftext|>",
    add_prefix_space=False, trim_offsets=True, **kwargs):
        super().__init__(ByteLevelBPETokenizer(vocab=vocab_file, merges=merges_file, add_prefix_space=add_prefix_space, trim_offsets=trim_offsets), bos_token=bos_token,
        eos_token=eos_token, unk_token=unk_token, **kwargs)
        self.add_prefix_space = add_prefix_space
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        output = [self.bos_token_id] + token_ids_0 + [self.eos_token_id]
        if token_ids_1 is None: return output
        return output + [self.eos_token_id] + token_ids_1 + [self.eos_token_id]
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
