"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
import os
from typing import Optional, Tuple
from ...tokenization_utils import PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json"}
class MgpstrTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES
    def __init__(self, vocab_file, unk_token="[GO]", bos_token="[GO]", eos_token="[s]", pad_token="[GO]", **kwargs):
        with open(vocab_file, encoding="utf-8") as vocab_handle: self.vocab = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.vocab.items()}
        super().__init__(unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, pad_token=pad_token, **kwargs)
    @property
    def vocab_size(self): return len(self.vocab)
    def get_vocab(self):
        vocab = dict(self.vocab).copy()
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text):
        char_tokens = []
        for s in text: char_tokens.extend(s)
        return char_tokens
    def _convert_token_to_id(self, token): return self.vocab.get(token, self.vocab.get(self.unk_token))
    def _convert_id_to_token(self, index): return self.decoder.get(index)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not os.path.isdir(save_directory):
            logger.error("Vocabulary path ({}) should be a directory".format(save_directory))
            return
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        with open(vocab_file, "w", encoding="utf-8") as f: f.write(json.dumps(self.vocab, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        return (vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
