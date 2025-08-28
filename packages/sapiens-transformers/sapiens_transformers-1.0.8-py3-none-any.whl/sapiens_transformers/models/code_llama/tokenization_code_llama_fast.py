"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import os
from shutil import copyfile
from typing import List, Optional, Tuple
from tokenizers import normalizers, processors
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import is_sentencepiece_available, logging
from ...utils.versions import require_version
require_version("tokenizers>=0.13.3")
if is_sentencepiece_available(): from .tokenization_code_llama import CodeLlamaTokenizer
else: CodeLlamaTokenizer = None
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "tokenizer.model", "tokenizer_file": "tokenizer.json"}
SPIECE_UNDERLINE = "▁"
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your \
answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure\
 that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not \
correct. If you don't know the answer to a question, please don't share false information."""
class CodeLlamaTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = CodeLlamaTokenizer
    padding_side = "left"
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(self, vocab_file=None, tokenizer_file=None, clean_up_tokenization_spaces=False, unk_token="<unk>", bos_token="<s>", eos_token="</s>", prefix_token="▁<PRE>",
    middle_token="▁<MID>", suffix_token="▁<SUF>", eot_token="▁<EOT>", fill_token="<FILL_ME>", additional_special_tokens=None, add_bos_token=True, add_eos_token=False,
    use_default_system_prompt=False, **kwargs):
        additional_special_tokens = additional_special_tokens or []
        for token in [prefix_token, middle_token, suffix_token, eot_token]: additional_special_tokens += [token] if token is not None else []
        self.use_default_system_prompt = use_default_system_prompt
        super().__init__(vocab_file=vocab_file, tokenizer_file=tokenizer_file, clean_up_tokenization_spaces=clean_up_tokenization_spaces, additional_special_tokens=additional_special_tokens,
        unk_token=unk_token, bos_token=bos_token, eos_token=eos_token, add_bos_token=add_bos_token, add_eos_token=add_eos_token, prefix_token=prefix_token, middle_token=middle_token,
        suffix_token=suffix_token, eot_token=eot_token, fill_token=fill_token, use_default_system_prompt=use_default_system_prompt, **kwargs)
        self._add_bos_token = add_bos_token
        self._add_eos_token = add_eos_token
        self.update_post_processor()
        self.vocab_file = vocab_file
        self._prefix_token = prefix_token
        self._middle_token = middle_token
        self._suffix_token = suffix_token
        self._eot_token = eot_token
        self.fill_token = fill_token
    @property
    def can_save_slow_tokenizer(self) -> bool: return os.path.isfile(self.vocab_file) if self.vocab_file else False
    def update_post_processor(self):
        bos = self.bos_token
        bos_token_id = self.bos_token_id
        if bos is None and self.add_bos_token: raise ValueError("add_bos_token = True but bos_token = None")
        eos = self.eos_token
        eos_token_id = self.eos_token_id
        if eos is None and self.add_eos_token: raise ValueError("add_eos_token = True but eos_token = None")
        single = f"{(bos+':0 ') if self.add_bos_token else ''}$A:0{(' '+eos+':0') if self.add_eos_token else ''}"
        pair = f"{single}{(' '+bos+':1') if self.add_bos_token else ''} $B:1{(' '+eos+':1') if self.add_eos_token else ''}"
        special_tokens = []
        if self.add_bos_token: special_tokens.append((bos, bos_token_id))
        if self.add_eos_token: special_tokens.append((eos, eos_token_id))
        self._tokenizer.post_processor = processors.TemplateProcessing(single=single, pair=pair, special_tokens=special_tokens)
    @property
    def prefix_token(self): return self._prefix_token
    @property
    def prefix_id(self):
        if self._prefix_token is None: return None
        return self.convert_tokens_to_ids(self.prefix_token)
    @property
    def middle_token(self): return self._middle_token
    @property
    def middle_id(self):
        if self._middle_token is None: return None
        return self.convert_tokens_to_ids(self.middle_token)
    @property
    def suffix_token(self): return self._suffix_token
    @property
    def suffix_id(self):
        if self._suffix_token is None: return None
        return self.convert_tokens_to_ids(self.suffix_token)
    @property
    def eot_id(self):
        if self._eot_token is None: return None
        return self.convert_tokens_to_ids(self.eot_token)
    @property
    def eot_token(self): return self._eot_token
    @property
    def add_eos_token(self): return self._add_eos_token
    @property
    def add_bos_token(self): return self._add_bos_token
    @add_eos_token.setter
    def add_eos_token(self, value):
        self._add_eos_token = value
        self.update_post_processor()
    @add_bos_token.setter
    def add_bos_token(self, value):
        self._add_bos_token = value
        self.update_post_processor()
    def set_infilling_processor(self, reset, suffix_first=False, add_special_tokens=True):
        if reset:
            self._tokenizer.normalizer = normalizers.Sequence([normalizers.Prepend(prepend="▁"), normalizers.Replace(pattern=" ", content="▁")])
            self.update_post_processor()
            return
        self._tokenizer.normalizer = normalizers.Replace(pattern=" ", content="▁")
        pair = [self.bos_token] if self.add_bos_token and add_special_tokens else []
        special_tokens = [(self.bos_token, self.bos_token_id)] if self.add_bos_token and add_special_tokens else []
        if suffix_first:
            pair += [self.prefix_token, self.suffix_token, "$B", self.middle_token, "$A"]
            special_tokens += [(self.prefix_token, self.prefix_id), (self.suffix_token, self.suffix_id), (self.middle_token, self.middle_id)]
        else:
            pair += [self.prefix_token, "$A", self.suffix_token, "$B", self.middle_token]
            special_tokens += [(self.prefix_token, self.prefix_id), (self.suffix_token, self.suffix_id), (self.middle_token, self.middle_id)]
        if self.add_eos_token and add_special_tokens:
            pair += [self.eos_token]
            special_tokens += [(self.eos_token, self.eos_token_id)]
        self._tokenizer.post_processor = processors.TemplateProcessing(single="$A", pair=pair, special_tokens=special_tokens)
    def encode_plus(self, text, text_pair=None, suffix_first=False, add_special_tokens=True, **kwargs):
        text_pair = kwargs.pop("suffix", text_pair)
        if self.fill_token is not None and self.fill_token in text and text_pair is None: text, text_pair = text.split(self.fill_token)
        if text_pair is None or len(text_pair) < 1: return super().encode_plus(text, text_pair, add_special_tokens=add_special_tokens, **kwargs)
        if None in (self.prefix_id, self.middle_id, self.suffix_id): raise ValueError(f"Then input includes a `prefix` and a `suffix` used for the infilling task, the `prefix_id, middle_id, suffix_id` must all be initialized. Current values : {self.prefix_id, self.middle_id, self.suffix_id}")
        self.set_infilling_processor(False, suffix_first=suffix_first, add_special_tokens=add_special_tokens)
        tokens = super().encode_plus(" " + text, text_pair=text_pair, add_special_tokens=True, **kwargs)
        self.set_infilling_processor(True)
        return tokens
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not self.can_save_slow_tokenizer: raise ValueError("Your fast tokenizer does not have the necessary information to save the vocabulary for a slow tokenizer.")
        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file): copyfile(self.vocab_file, out_vocab_file)
        return (out_vocab_file,)
    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> List[int]:
        if token_ids_1 is None: return self.bos_token_id + token_ids_0 + self.eos_token_id
        return self.bos_token_id + token_ids_0 + token_ids_1 + self.eos_token_id
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
