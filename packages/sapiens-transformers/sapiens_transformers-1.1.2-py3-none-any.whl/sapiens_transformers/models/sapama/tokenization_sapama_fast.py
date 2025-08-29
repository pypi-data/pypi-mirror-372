"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...utils import is_sentencepiece_available
from ...utils.versions import require_version
require_version("tokenizers>=0.13.3")
from typing import Optional, Tuple
from os import path as _path
if is_sentencepiece_available(): from .tokenization_sapama import SapamaTokenizer
else: SapamaTokenizer = None
VOCAB_FILES_NAMES, B_INST, E_INST, B_SYS, E_SYS = {"vocab_file": "tokenizer.model", "tokenizer_file": "tokenizer.json"}, "[INST]", "[/INST]", "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "Your name is Sapama, you are an Artificial Intelligence model created by Sapiens Technology to be a helpful assistant."
from ...tokenization_utils_fast import PreTrainedTokenizerFast
class SapamaTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names, slow_tokenizer_class, padding_side, model_input_names = VOCAB_FILES_NAMES, SapamaTokenizer, "left", ["input_ids", "attention_mask"]
    def __init__(self, vocab_file=None, tokenizer_file=None, clean_up_tokenization_spaces=False, unk_token="<unk>", bos_token="<s>", eos_token="</s>", add_bos_token=True,
    add_eos_token=False, use_default_system_prompt=False, legacy=None, add_prefix_space=None, **kwargs):
        if legacy is None: legacy = True
        self.legacy = legacy
        if add_prefix_space is not None: kwargs["from_slow"] = True
        super().__init__(vocab_file=vocab_file, tokenizer_file=tokenizer_file, clean_up_tokenization_spaces=clean_up_tokenization_spaces, unk_token=unk_token,
        bos_token=bos_token, eos_token=eos_token, add_bos_token=add_bos_token, add_eos_token=add_eos_token, use_default_system_prompt=use_default_system_prompt,
        add_prefix_space=add_prefix_space, legacy=legacy, **kwargs)
        self._add_bos_token, self._add_eos_token = add_bos_token, add_eos_token
        self.update_post_processor()
        self.use_default_system_prompt, self.vocab_file = use_default_system_prompt, vocab_file
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        bos_token_id, eos_token_id = [self.bos_token_id] if self.add_bos_token else [], [self.eos_token_id] if self.add_eos_token else []
        output = bos_token_id + token_ids_0 + eos_token_id
        if token_ids_1 is not None: output = output + bos_token_id + token_ids_1 + eos_token_id
        return output
    def update_post_processor(self):
        bos, bos_token_id = self.bos_token, self.bos_token_id
        if bos is None and self.add_bos_token: raise ValueError("add_bos_token = True but bos_token = None")
        eos, eos_token_id, special_tokens = self.eos_token, self.eos_token_id, []
        if eos is None and self.add_eos_token: raise ValueError("add_eos_token = True but eos_token = None")
        single = f"{(bos+':0 ') if self.add_bos_token else ''}$A:0{(' '+eos+':0') if self.add_eos_token else ''}"
        pair = f"{single}{(' '+bos+':1') if self.add_bos_token else ''} $B:1{(' '+eos+':1') if self.add_eos_token else ''}"
        if self.add_bos_token: special_tokens.append((bos, bos_token_id))
        if self.add_eos_token: special_tokens.append((eos, eos_token_id))
        from tokenizers import processors
        self._tokenizer.post_processor = processors.TemplateProcessing(single=single, pair=pair, special_tokens=special_tokens)
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
    @property
    def can_save_slow_tokenizer(self) -> bool: return _path.isfile(self.vocab_file) if self.vocab_file else False
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not self.can_save_slow_tokenizer: raise ValueError("Your fast tokenizer does not have the necessary information to save the vocabulary for a slow tokenizer.")
        if not _path.isdir(save_directory): return
        out_vocab_file = _path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"])
        from shutil import copyfile
        if _path.abspath(self.vocab_file) != _path.abspath(out_vocab_file): copyfile(self.vocab_file, out_vocab_file)
        return (out_vocab_file,)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
