"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import pickle
from typing import Optional, Tuple
from ...tokenization_utils_base import BatchEncoding
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"tokenizer_file": "tokenizer.json"}
class BloomTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = None
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, unk_token="<unk>", bos_token="<s>", eos_token="</s>", pad_token="<pad>",
    add_prefix_space=False, clean_up_tokenization_spaces=False, **kwargs):
        super().__init__(vocab_file, merges_file, tokenizer_file=tokenizer_file, unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token,
        add_prefix_space=add_prefix_space, clean_up_tokenization_spaces=clean_up_tokenization_spaces, **kwargs)
        pre_tok_state = pickle.dumps(self.backend_tokenizer.pre_tokenizer)
        decoder_state = pickle.dumps(self.backend_tokenizer.decoder)
        if add_prefix_space:
            pre_tok_state = pre_tok_state.replace(b'"add_prefix_space":false', b'"add_prefix_space": true')
            decoder_state = decoder_state.replace(b'"add_prefix_space":false', b'"add_prefix_space": true')
        self.backend_tokenizer.pre_tokenizer = pickle.loads(pre_tok_state)
        self.backend_tokenizer.decoder = pickle.loads(decoder_state)
        self.add_prefix_space = add_prefix_space
    def _batch_encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        if not (self.add_prefix_space or not is_split_into_words): raise Exception(f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._batch_encode_plus(*args, **kwargs)
    def _encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        if not (self.add_prefix_space or not is_split_into_words): raise Exception(f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True to use it with pretokenized inputs.")
        return super()._encode_plus(*args, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        files = self._tokenizer.model.save(save_directory, name=filename_prefix)
        return tuple(files)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
