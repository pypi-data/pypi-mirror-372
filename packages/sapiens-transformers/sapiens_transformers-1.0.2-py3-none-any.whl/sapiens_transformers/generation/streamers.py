"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from queue import Queue
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING: from ..models.auto import AutoTokenizer
class BaseStreamer:
    def put(self, value): raise NotImplementedError()
    def end(self): raise NotImplementedError()
class TextStreamer(BaseStreamer):
    def __init__(self, tokenizer: "AutoTokenizer", skip_prompt: bool = False, **decode_kwargs):
        self.tokenizer = tokenizer
        self.skip_prompt = skip_prompt
        self.decode_kwargs = decode_kwargs
        self.token_cache = []
        self.print_len = 0
        self.next_tokens_are_prompt = True
    def put(self, value):
        if len(value.shape) > 1 and value.shape[0] > 1: raise ValueError("TextStreamer only supports batch size 1")
        elif len(value.shape) > 1: value = value[0]
        if self.skip_prompt and self.next_tokens_are_prompt:
            self.next_tokens_are_prompt = False
            return
        self.token_cache.extend(value.tolist())
        text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)
        if text.endswith("\n"):
            printable_text = text[self.print_len :]
            self.token_cache = []
            self.print_len = 0
        elif len(text) > 0 and self._is_chinese_char(ord(text[-1])):
            printable_text = text[self.print_len :]
            self.print_len += len(printable_text)
        else:
            printable_text = text[self.print_len : text.rfind(" ") + 1]
            self.print_len += len(printable_text)
        self.on_finalized_text(printable_text)
    def end(self):
        if len(self.token_cache) > 0:
            text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)
            printable_text = text[self.print_len :]
            self.token_cache = []
            self.print_len = 0
        else: printable_text = ""
        self.next_tokens_are_prompt = True
        self.on_finalized_text(printable_text, stream_end=True)
    def on_finalized_text(self, text: str, stream_end: bool = False): print(text, flush=True, end="" if not stream_end else None)
    def _is_chinese_char(self, cp):
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or (cp >= 0x3400 and cp <= 0x4DBF) or (cp >= 0x20000 and cp <= 0x2A6DF) or (cp >= 0x2A700 and cp <= 0x2B73F) or
        (cp >= 0x2B740 and cp <= 0x2B81F) or (cp >= 0x2B820 and cp <= 0x2CEAF) or (cp >= 0xF900 and cp <= 0xFAFF) or (cp >= 0x2F800 and cp <= 0x2FA1F)): return True
        return False
class TextIteratorStreamer(TextStreamer):
    def __init__(self, tokenizer: "AutoTokenizer", skip_prompt: bool = False, timeout: Optional[float] = None, **decode_kwargs):
        super().__init__(tokenizer, skip_prompt, **decode_kwargs)
        self.text_queue = Queue()
        self.stop_signal = None
        self.timeout = timeout
    def on_finalized_text(self, text: str, stream_end: bool = False):
        self.text_queue.put(text, timeout=self.timeout)
        if stream_end: self.text_queue.put(self.stop_signal, timeout=self.timeout)
    def __iter__(self): return self
    def __next__(self):
        value = self.text_queue.get(timeout=self.timeout)
        if value == self.stop_signal: raise StopIteration()
        else: return value
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
