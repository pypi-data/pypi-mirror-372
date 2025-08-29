"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from copy import deepcopy
from enum import Enum
from typing import Dict, List, Optional
from huggingface_hub import InferenceClient
from ..pipelines.base import Pipeline
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool-call"
    TOOL_RESPONSE = "tool-response"
    @classmethod
    def roles(cls): return [r.value for r in cls]
def get_clean_message_list(message_list: List[Dict[str, str]], role_conversions: Dict[str, str] = {}):
    final_message_list = []
    message_list = deepcopy(message_list)
    for message in message_list:
        if not set(message.keys()) == {"role", "content"}: raise ValueError("Message should contain only 'role' and 'content' keys!")
        role = message["role"]
        if role not in MessageRole.roles(): raise ValueError(f"Incorrect role {role}, only {MessageRole.roles()} are supported for now.")
        if role in role_conversions: message["role"] = role_conversions[role]
        if len(final_message_list) > 0 and message["role"] == final_message_list[-1]["role"]: final_message_list[-1]["content"] += "\n=======\n" + message["content"]
        else: final_message_list.append(message)
    return final_message_list
llama_role_conversions = {MessageRole.TOOL_RESPONSE: MessageRole.USER}
class HfApiEngine:
    def __init__(self, model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"):
        self.model = model
        self.client = InferenceClient(self.model, timeout=120)
    def __call__(self, messages: List[Dict[str, str]], stop_sequences: List[str] = [], grammar: Optional[str] = None) -> str:
        messages = get_clean_message_list(messages, role_conversions=llama_role_conversions)
        if grammar is not None: response = self.client.chat_completion(messages, stop=stop_sequences, max_tokens=1500, response_format=grammar)
        else: response = self.client.chat_completion(messages, stop=stop_sequences, max_tokens=1500)
        response = response.choices[0].message.content
        for stop_seq in stop_sequences:
            if response[-len(stop_seq) :] == stop_seq: response = response[: -len(stop_seq)]
        return response
class TransformersEngine:
    def __init__(self, pipeline: Pipeline): self.pipeline = pipeline
    def __call__(self, messages: List[Dict[str, str]], stop_sequences: Optional[List[str]] = None, grammar: Optional[str] = None) -> str:
        messages = get_clean_message_list(messages, role_conversions=llama_role_conversions)
        output = self.pipeline(messages, stop_strings=stop_sequences, max_length=1500, tokenizer=self.pipeline.tokenizer)
        response = output[0]["generated_text"][-1]["content"]
        if stop_sequences is not None:
            for stop_seq in stop_sequences:
                if response[-len(stop_seq) :] == stop_seq: response = response[: -len(stop_seq)]
        return response
DEFAULT_JSONAGENT_REGEX_GRAMMAR = {"type": "regex", "value": 'Thought: .+?\\nAction:\\n\\{\\n\\s{4}"action":\\s"[^"\\n]+",\\n\\s{4}"action_input":\\s"[^"\\n]+"\\n\\}\\n<end_action>'}
DEFAULT_CODEAGENT_REGEX_GRAMMAR = {"type": "regex", "value": "Thought: .+?\\nCode:\\n```(?:py|python)?\\n(?:.|\\s)+?\\n```<end_action>"}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
