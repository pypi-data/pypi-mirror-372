"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import json
from typing import List, Optional, Tuple
from tokenizers import normalizers
from ....tokenization_utils_base import BatchEncoding
from ....tokenization_utils_fast import PreTrainedTokenizerFast
from ....utils import PaddingStrategy, logging
from .tokenization_realm import RealmTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt", "tokenizer_file": "tokenizer.json"}
class RealmTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = RealmTokenizer
    def __init__(self, vocab_file=None, tokenizer_file=None, do_lower_case=True, unk_token="[UNK]", sep_token="[SEP]", pad_token="[PAD]", cls_token="[CLS]",
    mask_token="[MASK]", tokenize_chinese_chars=True, strip_accents=None, **kwargs):
        super().__init__(vocab_file, tokenizer_file=tokenizer_file, do_lower_case=do_lower_case, unk_token=unk_token, sep_token=sep_token, pad_token=pad_token,
        cls_token=cls_token, mask_token=mask_token, tokenize_chinese_chars=tokenize_chinese_chars, strip_accents=strip_accents, **kwargs)
        normalizer_state = json.loads(self.backend_tokenizer.normalizer.__getstate__())
        if (normalizer_state.get("lowercase", do_lower_case) != do_lower_case or normalizer_state.get("strip_accents", strip_accents) != strip_accents
        or normalizer_state.get("handle_chinese_chars", tokenize_chinese_chars) != tokenize_chinese_chars):
            normalizer_class = getattr(normalizers, normalizer_state.pop("type"))
            normalizer_state["lowercase"] = do_lower_case
            normalizer_state["strip_accents"] = strip_accents
            normalizer_state["handle_chinese_chars"] = tokenize_chinese_chars
            self.backend_tokenizer.normalizer = normalizer_class(**normalizer_state)
        self.do_lower_case = do_lower_case
    def batch_encode_candidates(self, text, **kwargs):
        kwargs["padding"] = PaddingStrategy.MAX_LENGTH
        batch_text = text
        batch_text_pair = kwargs.pop("text_pair", None)
        return_tensors = kwargs.pop("return_tensors", None)
        output_data = {'input_ids': [], 'attention_mask': [], 'token_type_ids': []}
        for idx, candidate_text in enumerate(batch_text):
            if batch_text_pair is not None: candidate_text_pair = batch_text_pair[idx]
            else: candidate_text_pair = None
            encoded_candidates = super().__call__(candidate_text, candidate_text_pair, return_tensors=None, **kwargs)
            encoded_input_ids = encoded_candidates.get("input_ids")
            encoded_attention_mask = encoded_candidates.get("attention_mask")
            encoded_token_type_ids = encoded_candidates.get("token_type_ids")
            if encoded_input_ids is not None: output_data["input_ids"].append(encoded_input_ids)
            if encoded_attention_mask is not None: output_data["attention_mask"].append(encoded_attention_mask)
            if encoded_token_type_ids is not None: output_data["token_type_ids"].append(encoded_token_type_ids)
        output_data = {key: item for key, item in output_data.items() if len(item) != 0}
        return BatchEncoding(output_data, tensor_type=return_tensors)
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        output = [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        if token_ids_1 is not None: output += token_ids_1 + [self.sep_token_id]
        return output
    def create_token_type_ids_from_sequences(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None: return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]
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
