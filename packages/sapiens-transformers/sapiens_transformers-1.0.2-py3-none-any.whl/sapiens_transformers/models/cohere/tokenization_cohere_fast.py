"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import pickle
from typing import Dict, List, Literal, Union
from tokenizers import processors
from ...tokenization_utils_base import BatchEncoding
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from ...utils import logging
from ...utils.versions import require_version
require_version("tokenizers>=0.13.3")
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"tokenizer_file": "tokenizer.json"}
PRETRAINED_VOCAB_FILES_MAP = {"tokenizer_file": {'Cohere/Command-nightly': 'https://huggingface.co/Cohere/Command-nightly/blob/main/tokenizer.json'}}
DEFAULT_SYSTEM_PROMPT = "You are Command-R, a brilliant, sophisticated, AI-assistant trained to assist human users by providing thorough responses. You are trained by Cohere."
DEFAULT_RAG_PREAMBLE = """## Task and Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling."""
class CohereTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    padding_side = "left"
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = None
    def __init__(self, vocab_file=None, merges_file=None, tokenizer_file=None, clean_up_tokenization_spaces=False, unk_token="<UNK>", bos_token="<BOS_TOKEN>", eos_token="<|END_OF_TURN_TOKEN|>",
    add_bos_token=True, add_eos_token=False, use_default_system_prompt=False, add_prefix_space=False, **kwargs):
        super().__init__(vocab_file=vocab_file, merges_file=merges_file, tokenizer_file=tokenizer_file, clean_up_tokenization_spaces=clean_up_tokenization_spaces, unk_token=unk_token,
        bos_token=bos_token, eos_token=eos_token, add_bos_token=add_bos_token, add_eos_token=add_eos_token, use_default_system_prompt=use_default_system_prompt, add_prefix_space=add_prefix_space, **kwargs)
        self._add_bos_token = add_bos_token
        self._add_eos_token = add_eos_token
        self.update_post_processor()
        self.use_default_system_prompt = use_default_system_prompt
        self.vocab_file = vocab_file
        self.grounded_generation_template = kwargs.pop("grounded_generation_template", None)
        self.tool_use_template = kwargs.pop("tool_use_template", None)
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
    def apply_tool_use_template(self, conversation: Union[List[Dict[str, str]]], tools: List[Dict], **kwargs) -> Union[str, List[int]]: return self.apply_chat_template(conversation, chat_template="tool_use", tools=tools, **kwargs)
    def apply_grounded_generation_template(self, conversation: Union[List[Dict[str, str]]], documents: List[Dict], citation_mode: Literal["fast", "accurate"] = "accurate", **kwargs) -> Union[str, List[int]]: return self.apply_chat_template(conversation, chat_template="rag", documents=documents, citation_mode=citation_mode, **kwargs)
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        bos_token_id = [self.bos_token_id] if self.add_bos_token else []
        eos_token_id = [self.eos_token_id] if self.add_eos_token else []
        output = bos_token_id + token_ids_0 + eos_token_id
        if token_ids_1 is not None: output = output + bos_token_id + token_ids_1 + eos_token_id
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
